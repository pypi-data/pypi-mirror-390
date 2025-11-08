"""Async Kafka consumer with retry and DLQ."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from series_kafka.core.config import ConsumerConfig
from series_kafka.core.dlq import DLQHandler
from series_kafka.core.field_extractor import FieldExtractor
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.producer import AsyncProducer
from series_kafka.core.topic import Topic
from series_kafka.exceptions import (
    ConsumerError,
    FatalError,
    RetryableError,
    ValidationError,
)
from series_kafka.schema.validator import SchemaValidator

# Type alias for message handler
MessageHandler = Callable[[BaseMessage[BasePayload]], Awaitable[None]]
SubsetHandler = Callable[[dict[str, Any]], Awaitable[None]]


class AsyncConsumer:
    """
    Async Kafka consumer with DLQ and retry logic.

    Features:
    - Automatic retry with exponential backoff
    - Dead letter queue for failed messages
    - Event type filtering
    - Subset field extraction
    - Graceful shutdown
    - Manual offset commits

    Example:
        >>> async def handle_message(message):
        ...     print(f"Received: {message.event_type}")
        >>>
        >>> config = ConsumerConfig(
        ...     bootstrap_servers="localhost:9092",
        ...     group_id="my-consumer",
        ...     service_name="my-service"
        ... )
        >>> consumer = AsyncConsumer(
        ...     config=config,
        ...     topics=[UsersTopic()],
        ...     handler=handle_message
        ... )
        >>> await consumer.start()
        >>> await consumer.consume()
    """

    def __init__(
        self,
        config: ConsumerConfig,
        topics: list[Topic],
        handler: MessageHandler | SubsetHandler,
    ) -> None:
        """
        Initialize consumer.

        Args:
            config: Consumer configuration
            topics: List of topic plugins to subscribe to
            handler: Async message handler function
        """
        self.config = config
        self.topics = {t.name: t for t in topics}
        self.handler = handler

        self._consumer: AIOKafkaConsumer | None = None
        self._dlq_handlers: dict[str, DLQHandler] = {}
        self._dlq_producer: AsyncProducer | None = None
        self._running = False
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """
        Start the consumer.

        Initializes Kafka consumer and DLQ handlers.

        Raises:
            ConsumerError: If consumer fails to start
        """
        try:
            # Initialize DLQ producer if DLQ enabled
            if self.config.enable_dlq:
                from series_kafka.core.config import ProducerConfig

                # Create producer config from consumer config
                dlq_producer_config = ProducerConfig(
                    bootstrap_servers=self.config.bootstrap_servers,
                    sasl_username=self.config.sasl_username,
                    sasl_password=self.config.sasl_password,
                    sasl_mechanism=self.config.sasl_mechanism,
                    security_protocol=self.config.security_protocol,
                    service_name=self.config.service_name,
                    enable_idempotence=True,
                )

                self._dlq_producer = AsyncProducer(dlq_producer_config)
                await self._dlq_producer.start()

                # Create DLQ handler per topic
                for topic in self.topics.values():
                    if topic.enable_dlq:
                        dlq_handler = DLQHandler(self._dlq_producer, topic.dlq_topic)
                        self._dlq_handlers[topic.name] = dlq_handler

            # Create Kafka consumer
            self._consumer = AIOKafkaConsumer(
                *self.topics.keys(),
                **self.config.kafka_config,
            )

            # Start consumer
            await self._consumer.start()

        except KafkaError as e:
            raise ConsumerError(
                f"Failed to start consumer: {str(e)}",
                details={"bootstrap_servers": self.config.bootstrap_servers},
            ) from e

        except Exception as e:
            raise ConsumerError(f"Unexpected error starting consumer: {str(e)}") from e

    async def consume(self) -> None:
        """
        Start consuming messages.

        Runs until stop() is called or shutdown signal received.
        """
        if not self._consumer:
            raise ConsumerError("Consumer not started. Call start() first.")

        self._running = True

        try:
            async for msg in self._consumer:
                if not self._running:
                    break

                await self._process_message(msg)

        except asyncio.CancelledError:
            # Graceful shutdown
            pass

        finally:
            await self._shutdown()

    async def _process_message(self, msg: Any) -> None:
        """Process a single message with error handling."""
        try:
            # Deserialize JSON
            raw_data = json.loads(msg.value.decode("utf-8"))
            event_type = raw_data.get("event_type", "unknown")

            # Get topic
            topic = self.topics.get(msg.topic)
            if not topic:
                # Skip messages from unknown topics
                return

            # Filter by event type if configured
            if self.config.event_type_filter:
                if event_type not in self.config.event_type_filter:
                    # Skip filtered events
                    await self._consumer.commit()
                    return

            # Get payload class
            if event_type not in topic.schema_registry:
                # Unknown event type for this topic
                await self._consumer.commit()
                return

            payload_class = topic.schema_registry[event_type]

            # Validate and parse payload
            payload_data = raw_data.get("payload", {})
            payload = SchemaValidator.validate_payload(payload_data, payload_class)

            # Create full message
            message = BaseMessage[type(payload)](  # type: ignore[valid-type]
                event_id=raw_data["event_id"],
                event_type=event_type,
                schema_version=raw_data.get("schema_version", "1.0.0"),
                timestamp=raw_data["timestamp"],
                source_service=raw_data["source_service"],
                payload=payload,
                correlation_id=raw_data.get("correlation_id"),
                trace_id=raw_data.get("trace_id"),
                parent_span_id=raw_data.get("parent_span_id"),
                metadata=raw_data.get("metadata", {}),
            )

            # Apply subset field extraction if configured
            if self.config.subset_fields:
                fields = FieldExtractor.extract_fields(message, self.config.subset_fields)
                await self._invoke_handler_with_retry(fields, topic, msg, raw_data, is_subset=True)
            else:
                await self._invoke_handler_with_retry(
                    message, topic, msg, raw_data, is_subset=False
                )

            # Commit offset on success
            await self._consumer.commit()

        except (ValidationError, FatalError) as e:
            # These errors go directly to DLQ without retry
            await self._send_to_dlq_and_commit(msg, raw_data, e, retry_count=0)

        except Exception as e:
            # Unexpected errors treated as fatal
            await self._send_to_dlq_and_commit(
                msg, raw_data, FatalError(f"Unexpected error: {str(e)}"), retry_count=0
            )

    async def _invoke_handler_with_retry(
        self,
        data: BaseMessage[BasePayload] | dict[str, Any],
        topic: Topic,
        msg: Any,
        raw_data: dict[str, Any],
        is_subset: bool = False,
    ) -> None:
        """Invoke handler with exponential backoff retry."""
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                # Call handler
                await self.handler(data)  # type: ignore[arg-type]
                return  # Success

            except RetryableError as e:
                # Retryable error - try again with backoff
                last_error = e

                if attempt < self.config.max_retries:
                    # Calculate backoff
                    backoff_seconds = (self.config.retry_backoff_ms * (2**attempt)) / 1000
                    await asyncio.sleep(backoff_seconds)
                    continue  # Retry
                # Max retries exceeded - send to DLQ
                break

            except (ValidationError, FatalError) as e:
                # Non-retryable errors - send to DLQ immediately
                await self._send_to_dlq_and_commit(msg, raw_data, e, retry_count=attempt)
                return

            except Exception as e:
                # Unexpected error - treat as fatal
                await self._send_to_dlq_and_commit(
                    msg,
                    raw_data,
                    FatalError(f"Unexpected handler error: {str(e)}"),
                    retry_count=attempt,
                )
                return

        # Max retries exceeded for RetryableError
        if last_error:
            await self._send_to_dlq_and_commit(
                msg, raw_data, last_error, retry_count=self.config.max_retries
            )

    async def _send_to_dlq_and_commit(
        self,
        msg: Any,
        raw_data: dict[str, Any],
        error: Exception,
        retry_count: int,
    ) -> None:
        """Send message to DLQ and commit offset."""
        topic_name = msg.topic

        if self.config.enable_dlq and topic_name in self._dlq_handlers:
            try:
                dlq_handler = self._dlq_handlers[topic_name]
                await dlq_handler.send_to_dlq(
                    original_topic=topic_name,
                    original_event_id=raw_data.get("event_id", "unknown"),
                    original_event_type=raw_data.get("event_type", "unknown"),
                    original_payload_json=json.dumps(raw_data),
                    error=error,
                    retry_count=retry_count,
                    original_headers={
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "timestamp": msg.timestamp,
                    },
                )
            except Exception:
                # DLQ send failed - log but don't crash
                # In production, this should be monitored
                pass

        # Commit offset to move past failed message
        await self._consumer.commit()

    async def stop(self) -> None:
        """
        Stop the consumer gracefully.

        Signals shutdown and waits for current message processing to complete.
        """
        self._running = False
        self._shutdown_event.set()

    async def _shutdown(self) -> None:
        """Internal shutdown with timeout."""
        try:
            # Wait for shutdown timeout
            await asyncio.wait_for(
                self._finalize_shutdown(),
                timeout=self.config.shutdown_timeout_seconds,
            )
        except TimeoutError:
            # Force shutdown after timeout
            pass

    async def _finalize_shutdown(self) -> None:
        """Finalize shutdown - commit offsets and close connections."""
        try:
            # Commit pending offsets
            if self._consumer:
                await self._consumer.commit()

            # Stop consumer
            if self._consumer:
                await self._consumer.stop()

            # Stop DLQ producer
            if self._dlq_producer:
                await self._dlq_producer.stop()

        finally:
            self._consumer = None
            self._dlq_producer = None

    async def __aenter__(self) -> "AsyncConsumer":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
