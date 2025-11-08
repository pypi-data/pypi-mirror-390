"""Field extraction from messages using dot notation."""

from typing import Any

from series_kafka.core.message import BaseMessage, BasePayload


class FieldExtractor:
    """
    Extracts specific fields from messages using dot notation.

    Supports nested field access with dot notation paths:
    - "event_id" → message.event_id
    - "payload.user_id" → message.payload.user_id
    - "payload.data.score" → message.payload.data.score

    Example:
        >>> extractor = FieldExtractor()
        >>> fields = extractor.extract_fields(
        ...     message,
        ...     ["event_id", "payload.user_id", "payload.username"]
        ... )
        >>> print(fields)
        {"event_id": "evt_123", "user_id": "usr_456", "username": "john"}
    """

    @staticmethod
    def extract_fields(
        message: BaseMessage[BasePayload],
        field_paths: list[str],
    ) -> dict[str, Any]:
        """
        Extract specific fields from a message.

        Args:
            message: Source message
            field_paths: List of dot-notation paths to extract

        Returns:
            Dictionary with extracted values
            Keys are the leaf field names (rightmost part of path)
            Values are the extracted field values
            Missing fields are omitted from result

        Example:
            Input: ["payload.user_id", "event_id"]
            Output: {"user_id": "usr_123", "event_id": "evt_456"}
        """
        result: dict[str, Any] = {}

        for path in field_paths:
            try:
                value = FieldExtractor._get_nested_value(message, path)

                # Use leaf name as key
                leaf_name = path.split(".")[-1]

                # Store value
                result[leaf_name] = value

            except (AttributeError, KeyError, IndexError):
                # Field not found - skip it (don't add to result)
                continue

        return result

    @staticmethod
    def _get_nested_value(obj: Any, path: str) -> Any:
        """
        Get nested value using dot notation path.

        Args:
            obj: Root object
            path: Dot-notation path (e.g., "payload.user_id")

        Returns:
            Value at the path

        Raises:
            AttributeError: If path not found
            KeyError: If dict key not found
        """
        parts = path.split(".")
        current = obj

        for part in parts:
            # Try attribute access first (for Pydantic models)
            if hasattr(current, part):
                current = getattr(current, part)
            # Try dict access
            elif isinstance(current, dict):
                current = current[part]
            else:
                # Cannot access - raise error
                raise AttributeError(f"Cannot access '{part}' in path '{path}'")

        return current

    @staticmethod
    def extract_fields_with_full_paths(
        message: BaseMessage[BasePayload],
        field_paths: list[str],
    ) -> dict[str, Any]:
        """
        Extract fields preserving full path as keys.

        Alternative extraction method that uses full paths as keys
        instead of just leaf names. Useful when paths have conflicting
        leaf names.

        Args:
            message: Source message
            field_paths: List of dot-notation paths

        Returns:
            Dictionary with full paths as keys

        Example:
            Input: ["payload.user.id", "payload.profile.id"]
            Output: {
                "payload.user.id": 123,
                "payload.profile.id": 456
            }
        """
        result: dict[str, Any] = {}

        for path in field_paths:
            try:
                value = FieldExtractor._get_nested_value(message, path)
                result[path] = value
            except (AttributeError, KeyError, IndexError):
                # Field not found - skip it
                continue

        return result

    @staticmethod
    def has_field(message: BaseMessage[BasePayload], path: str) -> bool:
        """
        Check if a field path exists in the message.

        Args:
            message: Message to check
            path: Dot-notation path

        Returns:
            True if path exists
        """
        try:
            FieldExtractor._get_nested_value(message, path)
            return True
        except (AttributeError, KeyError, IndexError):
            return False
