"""Messages topic plugin."""

from series_kafka.contracts.base import TopicContract
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.topic import Topic
from series_kafka_topics.messages.schemas import (
    AgentResponsePayload,
    LinqPayload,
    SendBluePayload,
)


class MessagesTopic(Topic):
    """Messages topic for communication events."""

    @property
    def name(self) -> str:
        return "messages"

    @property
    def schema_registry(self) -> dict[str, type[BasePayload]]:
        return {
            "message.sendblue": SendBluePayload,
            "message.linq": LinqPayload,
            "message.agent_response": AgentResponsePayload,
        }

    def get_partition_key(
        self,
        message: BaseMessage[BasePayload],
        event_type: str,
    ) -> str | None:
        """Partition by conversation to maintain message ordering."""
        payload = message.payload

        if event_type == "message.sendblue":
            # Partition by sorted phone numbers for consistent routing
            if hasattr(payload, "from_number") and hasattr(payload, "to_number"):
                from_num = payload.from_number  # type: ignore[attr-defined]
                to_num = payload.to_number  # type: ignore[attr-defined]
                numbers = sorted([from_num, to_num])
                return f"{numbers[0]}:{numbers[1]}"

        elif event_type == "message.linq":
            if hasattr(payload, "conversation_id"):
                return payload.conversation_id  # type: ignore[attr-defined, return-value]

        elif event_type == "message.agent_response":
            if hasattr(payload, "user_id"):
                return payload.user_id  # type: ignore[attr-defined, return-value]

        return None

    def validate_message(self, message: BaseMessage[BasePayload]) -> bool:
        """Validate message-specific business rules."""
        payload = message.payload

        # Validate user_id format if present
        if hasattr(payload, "user_id"):
            user_id = payload.user_id  # type: ignore[attr-defined]
            if not user_id.startswith("usr_"):
                return False

        return True

    def get_contract(self) -> TopicContract:
        """Get messages topic contract."""
        return TopicContract(
            name=self.name,
            version="1.0.0",
            event_types={
                "message.sendblue": {
                    "type": "object",
                    "description": "SendBlue SMS message event",
                },
                "message.linq": {
                    "type": "object",
                    "description": "Linq messaging event",
                },
                "message.agent_response": {
                    "type": "object",
                    "description": "AI agent response event",
                },
            },
        )


__all__ = ["MessagesTopic", "SendBluePayload", "LinqPayload", "AgentResponsePayload"]
