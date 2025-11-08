"""Dead Letter Queue handler."""

import traceback
from datetime import UTC, datetime
from typing import Any

from series_kafka.core.message import BasePayload
from series_kafka.core.producer import AsyncProducer
from series_kafka.exceptions import DLQError


class DLQPayload(BasePayload):
    """Payload for dead letter queue messages."""

    original_topic: str
    original_event_id: str
    original_event_type: str
    retry_count: int
    error_message: str
    error_type: str
    error_stacktrace: str
    failed_at: datetime
    original_headers: dict[str, Any]
    original_payload_json: str


class DLQHandler:
    """
    Handles dead letter queue operations.

    Sends failed messages to DLQ with complete metadata for debugging:
    - Original message data
    - Error information
    - Retry count
    - Stack trace
    - Timestamps
    """

    def __init__(self, producer: AsyncProducer, dlq_topic: str) -> None:
        """
        Initialize DLQ handler.

        Args:
            producer: AsyncProducer instance for sending to DLQ
            dlq_topic: DLQ topic name
        """
        self.producer = producer
        self.dlq_topic = dlq_topic

    async def send_to_dlq(
        self,
        original_topic: str,
        original_event_id: str,
        original_event_type: str,
        original_payload_json: str,
        error: Exception,
        retry_count: int = 0,
        original_headers: dict[str, Any] | None = None,
    ) -> None:
        """
        Send failed message to DLQ.

        Args:
            original_topic: Topic where message failed
            original_event_id: Original message event_id
            original_event_type: Original message event_type
            original_payload_json: Original message as JSON string
            error: Exception that caused failure
            retry_count: Number of retry attempts made
            original_headers: Original message headers/metadata

        Raises:
            DLQError: If sending to DLQ fails (non-fatal, logged)
        """
        try:
            # Create DLQ payload with full context
            dlq_payload = DLQPayload(
                original_topic=original_topic,
                original_event_id=original_event_id,
                original_event_type=original_event_type,
                retry_count=retry_count,
                error_message=str(error),
                error_type=type(error).__name__,
                error_stacktrace=traceback.format_exc(),
                failed_at=datetime.now(UTC),
                original_headers=original_headers or {},
                original_payload_json=original_payload_json,
            )

            # Note: We can't use normal produce() since we don't have a Topic plugin for DLQ
            # DLQ messages go directly without validation
            from series_kafka.core.message import BaseMessage
            from series_kafka.schema.serializer import MessageSerializer

            # Create DLQ message
            dlq_message = BaseMessage[DLQPayload](
                event_type="dlq.message",
                source_service=self.producer.config.service_name,
                payload=dlq_payload,
                metadata={
                    "original_topic": original_topic,
                    "original_event_id": original_event_id,
                    "retry_count": retry_count,
                },
            )

            # Serialize and send directly
            message_bytes = MessageSerializer.serialize(dlq_message)

            if self.producer._producer:
                future = await self.producer._producer.send(
                    self.dlq_topic,
                    value=message_bytes,
                    key=original_event_id.encode("utf-8"),
                )
                await future

        except Exception as e:
            # DLQ send failure - log but don't crash
            # In production, this should be logged to external monitoring
            raise DLQError(
                f"Failed to send message to DLQ: {str(e)}",
                details={
                    "dlq_topic": self.dlq_topic,
                    "original_topic": original_topic,
                    "original_event_id": original_event_id,
                },
            ) from e
