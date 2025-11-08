"""Base contracts for topic data schemas."""

from typing import Any


class TopicContract:
    """
    Data contract for a Kafka topic.

    Defines:
    - Event types supported
    - JSON Schema definitions per event type
    - Schema versioning
    """

    def __init__(
        self,
        name: str,
        version: str,
        event_types: dict[str, dict[str, Any]],
    ) -> None:
        """
        Initialize topic contract.

        Args:
            name: Topic name
            version: Contract version (semantic versioning)
            event_types: Map of event_type -> JSON Schema definition
        """
        self.name = name
        self.version = version
        self.event_types = event_types

    def validate_event_type(self, event_type: str) -> bool:
        """
        Check if event type is supported.

        Args:
            event_type: Event type to validate

        Returns:
            True if event type is supported
        """
        return event_type in self.event_types

    def get_schema(self, event_type: str) -> dict[str, Any]:
        """
        Get JSON Schema for an event type.

        Args:
            event_type: Event type

        Returns:
            JSON Schema definition

        Raises:
            KeyError: If event type not found
        """
        return self.event_types[event_type]

    def list_event_types(self) -> list[str]:
        """
        List all supported event types.

        Returns:
            List of event type names
        """
        return list(self.event_types.keys())
