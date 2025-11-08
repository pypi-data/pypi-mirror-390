"""Topic plugin abstract base class."""

from abc import ABC, abstractmethod

from series_kafka.contracts.base import TopicContract
from series_kafka.core.message import BaseMessage, BasePayload


class Topic(ABC):
    """
    Abstract base class for topic plugins.

    Each topic plugin must implement:
    - name: Kafka topic name
    - schema_registry: Map event types to payload classes
    - get_partition_key: Extract partition key from message
    - validate_message: Topic-specific validation
    - get_contract: Return data contract

    Example:
        >>> class UsersTopic(Topic):
        ...     @property
        ...     def name(self) -> str:
        ...         return "users"
        ...
        ...     @property
        ...     def schema_registry(self) -> dict[str, Type[BasePayload]]:
        ...         return {
        ...             "user.created": UserCreatedPayload,
        ...             "user.updated": UserUpdatedPayload,
        ...         }
        ...
        ...     def get_partition_key(self, message, event_type) -> str | None:
        ...         return message.payload.user_id
        ...
        ...     def validate_message(self, message) -> bool:
        ...         return message.payload.user_id.startswith("usr_")
        ...
        ...     def get_contract(self) -> TopicContract:
        ...         return UsersContract()
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Topic name in Kafka.

        Returns:
            Kafka topic name
        """

    @property
    @abstractmethod
    def schema_registry(self) -> dict[str, type[BasePayload]]:
        """
        Map event types to payload classes.

        Returns:
            Dictionary mapping event_type -> PayloadClass

        Example:
            {
                "user.created": UserCreatedPayload,
                "user.updated": UserUpdatedPayload,
                "user.deleted": UserDeletedPayload,
            }
        """

    @abstractmethod
    def get_partition_key(
        self,
        message: BaseMessage[BasePayload],
        event_type: str,
    ) -> str | None:
        """
        Extract partition key from message.

        Determines which partition the message should be sent to.
        Messages with the same partition key go to the same partition,
        maintaining order.

        Args:
            message: The message to partition
            event_type: Event type of the message

        Returns:
            Partition key string, or None for random partitioning

        Example:
            def get_partition_key(self, message, event_type):
                # Partition by user_id to maintain per-user ordering
                return message.payload.user_id
        """

    @abstractmethod
    def validate_message(self, message: BaseMessage[BasePayload]) -> bool:
        """
        Topic-specific message validation.

        Perform any custom validation logic beyond schema validation.

        Args:
            message: Message to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails

        Example:
            def validate_message(self, message):
                # Ensure user_id has correct prefix
                if not message.payload.user_id.startswith("usr_"):
                    raise ValidationError("user_id must start with 'usr_'")
                return True
        """

    @abstractmethod
    def get_contract(self) -> TopicContract:
        """
        Get topic data contract.

        Returns:
            TopicContract with schema definitions

        Example:
            def get_contract(self):
                return TopicContract(
                    name=self.name,
                    version="1.0.0",
                    event_types={
                        "user.created": {...schema...},
                        "user.updated": {...schema...},
                    }
                )
        """

    # Default implementations (can be overridden)

    @property
    def dlq_topic(self) -> str:
        """
        Dead letter queue topic name.

        Returns:
            DLQ topic name (default: {topic_name}.dlq)
        """
        return f"{self.name}.dlq"

    @property
    def enable_dlq(self) -> bool:
        """
        Whether DLQ is enabled for this topic.

        Returns:
            True if DLQ should be enabled (default: True)
        """
        return True

    def get_event_types(self) -> list[str]:
        """
        List all event types supported by this topic.

        Returns:
            List of event type names
        """
        return list(self.schema_registry.keys())

    def supports_event_type(self, event_type: str) -> bool:
        """
        Check if topic supports an event type.

        Args:
            event_type: Event type to check

        Returns:
            True if supported
        """
        return event_type in self.schema_registry

    def get_payload_class(self, event_type: str) -> type[BasePayload]:
        """
        Get payload class for an event type.

        Args:
            event_type: Event type

        Returns:
            Payload class

        Raises:
            KeyError: If event type not supported
        """
        return self.schema_registry[event_type]
