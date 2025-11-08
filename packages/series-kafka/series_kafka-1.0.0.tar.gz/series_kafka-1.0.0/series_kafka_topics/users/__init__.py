"""Users topic plugin."""

from series_kafka.contracts.base import TopicContract
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.topic import Topic
from series_kafka_topics.users.schemas import (
    UserCreatedPayload,
    UserDeletedPayload,
    UserUpdatedPayload,
)


class UsersTopic(Topic):
    """Users topic for user lifecycle events."""

    @property
    def name(self) -> str:
        return "users"

    @property
    def schema_registry(self) -> dict[str, type[BasePayload]]:
        return {
            "user.created": UserCreatedPayload,
            "user.updated": UserUpdatedPayload,
            "user.deleted": UserDeletedPayload,
        }

    def get_partition_key(
        self,
        message: BaseMessage[BasePayload],
        event_type: str,
    ) -> str | None:
        """Partition by user_id to maintain per-user ordering."""
        if hasattr(message.payload, "user_id"):
            return message.payload.user_id  # type: ignore[attr-defined, return-value]
        return None

    def validate_message(self, message: BaseMessage[BasePayload]) -> bool:
        """Validate user message business rules."""
        payload = message.payload

        # Validate user_id format
        if hasattr(payload, "user_id"):
            user_id = payload.user_id  # type: ignore[attr-defined]
            if not user_id.startswith("usr_"):
                return False

        return True

    def get_contract(self) -> TopicContract:
        """Get users topic contract."""
        return TopicContract(
            name=self.name,
            version="1.0.0",
            event_types={
                "user.created": {
                    "type": "object",
                    "description": "User account created",
                },
                "user.updated": {
                    "type": "object",
                    "description": "User account updated",
                },
                "user.deleted": {
                    "type": "object",
                    "description": "User account deleted",
                },
            },
        )


__all__ = [
    "UsersTopic",
    "UserCreatedPayload",
    "UserUpdatedPayload",
    "UserDeletedPayload",
]
