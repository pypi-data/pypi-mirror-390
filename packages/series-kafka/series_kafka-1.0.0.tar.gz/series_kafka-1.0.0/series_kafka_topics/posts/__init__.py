"""Posts topic plugin."""

from series_kafka.contracts.base import TopicContract
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.topic import Topic
from series_kafka_topics.posts.schemas import (
    PostCreatedPayload,
    PostDeletedPayload,
    PostUpdatedPayload,
)


class PostsTopic(Topic):
    """Posts topic for content lifecycle events."""

    @property
    def name(self) -> str:
        return "posts"

    @property
    def schema_registry(self) -> dict[str, type[BasePayload]]:
        return {
            "post.created": PostCreatedPayload,
            "post.updated": PostUpdatedPayload,
            "post.deleted": PostDeletedPayload,
        }

    def get_partition_key(
        self,
        message: BaseMessage[BasePayload],
        event_type: str,
    ) -> str | None:
        """Partition by post_id to maintain per-post ordering."""
        if hasattr(message.payload, "post_id"):
            return message.payload.post_id  # type: ignore[attr-defined, return-value]
        return None

    def validate_message(self, message: BaseMessage[BasePayload]) -> bool:
        """Validate post message business rules."""
        payload = message.payload

        # Validate post_id and user_id format
        if hasattr(payload, "post_id"):
            post_id = payload.post_id  # type: ignore[attr-defined]
            if not post_id.startswith("post_"):
                return False

        if hasattr(payload, "user_id"):
            user_id = payload.user_id  # type: ignore[attr-defined]
            if not user_id.startswith("usr_"):
                return False

        return True

    def get_contract(self) -> TopicContract:
        """Get posts topic contract."""
        return TopicContract(
            name=self.name,
            version="1.0.0",
            event_types={
                "post.created": {
                    "type": "object",
                    "description": "Post content created",
                },
                "post.updated": {
                    "type": "object",
                    "description": "Post content updated",
                },
                "post.deleted": {
                    "type": "object",
                    "description": "Post content deleted",
                },
            },
        )


__all__ = [
    "PostsTopic",
    "PostCreatedPayload",
    "PostUpdatedPayload",
    "PostDeletedPayload",
]
