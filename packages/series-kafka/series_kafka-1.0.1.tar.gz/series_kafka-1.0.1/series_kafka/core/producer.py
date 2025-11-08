"""Async Kafka producer with idempotency."""

import time
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from series_kafka.core.config import ProducerConfig
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.topic import Topic
from series_kafka.exceptions import ProducerError, ValidationError
from series_kafka.schema.serializer import MessageSerializer
from series_kafka.schema.validator import SchemaValidator


class AsyncProducer:
    """
    Async Kafka producer with idempotent delivery.

    Features:
    - Exactly-once delivery (idempotent producer)
    - Schema validation before sending
    - Automatic partition key extraction
    - OpenTelemetry observability (optional)
    - Connection pooling and reuse

    Example:
        >>> config = ProducerConfig(
        ...     bootstrap_servers="localhost:9092",
        ...     service_name="my-service"
        ... )
        >>> producer = AsyncProducer(config)
        >>> await producer.start()
        >>> event_id = await producer.produce(
        ...     topic=UsersTopic(),
        ...     payload=UserCreatedPayload(...),
        ...     event_type="user.created"
        ... )
        >>> await producer.stop()
    """

    def __init__(self, config: ProducerConfig) -> None:
        """
        Initialize producer.

        Args:
            config: Producer configuration
        """
        self.config = config
        self._producer: AIOKafkaProducer | None = None
        self._started = False

        # Observability (optional)
        self._tracer = None
        self._meter = None
        self._messages_produced_counter = None
        self._produce_latency_histogram = None

        if config.enable_tracing or config.enable_metrics:
            self._setup_observability()

    def _setup_observability(self) -> None:
        """Setup OpenTelemetry tracing and metrics."""
        if self.config.enable_tracing:
            try:
                from opentelemetry import trace

                self._tracer = trace.get_tracer(__name__)
            except ImportError:
                pass

        if self.config.enable_metrics:
            try:
                from opentelemetry import metrics

                meter = metrics.get_meter(__name__)
                self._messages_produced_counter = meter.create_counter(
                    name="kafka.producer.messages.produced",
                    description="Total messages produced",
                    unit="1",
                )
                self._produce_latency_histogram = meter.create_histogram(
                    name="kafka.producer.produce.latency",
                    description="Production latency in milliseconds",
                    unit="ms",
                )
            except ImportError:
                pass

    async def start(self) -> None:
        """
        Start the producer.

        Initializes aiokafka producer with idempotent configuration.

        Raises:
            ProducerError: If producer fails to start
        """
        if self._started:
            return

        try:
            # Create aiokafka producer
            self._producer = AIOKafkaProducer(**self.config.kafka_config)

            # Start producer
            await self._producer.start()
            self._started = True

        except KafkaError as e:
            raise ProducerError(
                f"Failed to start producer: {str(e)}",
                details={"bootstrap_servers": self.config.bootstrap_servers},
            ) from e

        except Exception as e:
            raise ProducerError(f"Unexpected error starting producer: {str(e)}") from e

    async def produce(
        self,
        topic: Topic,
        payload: BasePayload,
        event_type: str,
        key: str | None = None,
        **metadata: Any,
    ) -> str:
        """
        Produce a message to Kafka.

        Args:
            topic: Topic plugin
            payload: Event payload
            event_type: Event type (must be in topic's schema registry)
            key: Partition key (optional, will use topic's get_partition_key if None)
            **metadata: Additional message metadata

        Returns:
            event_id: Unique event identifier

        Raises:
            ProducerError: If producer not started or production fails
            ValidationError: If schema validation fails
        """
        if not self._started or not self._producer:
            raise ProducerError("Producer not started. Call start() first.")

        start_time = time.time()

        try:
            # Start tracing span if enabled
            span_context = None
            if self._tracer:
                span_context = self._tracer.start_as_current_span("kafka.produce")
                span = span_context.__enter__()
                span.set_attribute("messaging.destination", topic.name)
                span.set_attribute("messaging.kafka.event_type", event_type)

            try:
                # 1. Validate event type is supported
                if not topic.supports_event_type(event_type):
                    raise ValidationError(
                        f"Event type '{event_type}' not supported by topic '{topic.name}'",
                        details={"supported_types": topic.get_event_types()},
                    )

                # 2. Validate payload against schema
                payload_class = topic.get_payload_class(event_type)
                SchemaValidator.validate_payload_instance(payload, payload_class)

                # 3. Create message envelope
                message = BaseMessage[type(payload)](  # type: ignore[valid-type]
                    event_type=event_type,
                    source_service=self.config.service_name,
                    payload=payload,
                    **metadata,
                )

                # 4. Topic-specific validation
                if not topic.validate_message(message):
                    raise ValidationError(
                        f"Topic validation failed for {topic.name}",
                        details={"event_type": event_type},
                    )

                # 5. Get partition key
                partition_key = key or topic.get_partition_key(message, event_type)

                # 6. Serialize message
                message_bytes = MessageSerializer.serialize(message)

                # 7. Produce to Kafka (idempotent)
                partition_key_bytes = partition_key.encode("utf-8") if partition_key else None

                future = await self._producer.send(
                    topic.name,
                    value=message_bytes,
                    key=partition_key_bytes,
                )

                # 8. Wait for acknowledgment
                await future

                # 9. Record metrics
                if self._messages_produced_counter:
                    self._messages_produced_counter.add(1, {"topic": topic.name})

                if self._produce_latency_histogram:
                    latency_ms = (time.time() - start_time) * 1000
                    self._produce_latency_histogram.record(latency_ms, {"topic": topic.name})

                return message.event_id

            finally:
                # End tracing span
                if span_context:
                    span_context.__exit__(None, None, None)

        except ValidationError:
            # Re-raise validation errors
            raise

        except KafkaError as e:
            raise ProducerError(
                f"Failed to produce message: {str(e)}",
                details={"topic": topic.name, "event_type": event_type},
            ) from e

        except Exception as e:
            raise ProducerError(
                f"Unexpected error producing message: {str(e)}",
                details={"topic": topic.name, "event_type": event_type},
            ) from e

    async def stop(self) -> None:
        """
        Stop the producer gracefully.

        Flushes pending messages and closes connection.
        """
        if not self._started:
            return

        try:
            if self._producer:
                # Flush pending messages
                await self._producer.flush()

                # Stop producer
                await self._producer.stop()

        finally:
            self._started = False
            self._producer = None

    async def __aenter__(self) -> "AsyncProducer":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
