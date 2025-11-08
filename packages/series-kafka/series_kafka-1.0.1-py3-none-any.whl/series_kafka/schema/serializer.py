"""Message serialization and deserialization."""

import json
from typing import Any

from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.exceptions import SerializationError


class MessageSerializer:
    """
    Serializes and deserializes Kafka messages.

    Handles conversion between:
    - BaseMessage[Payload] ↔ JSON string
    - BaseMessage[Payload] ↔ bytes
    """

    @staticmethod
    def serialize(message: BaseMessage[BasePayload]) -> bytes:
        """
        Serialize message to bytes.

        Args:
            message: Message to serialize

        Returns:
            UTF-8 encoded JSON bytes

        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Use Pydantic's JSON serialization
            json_str = message.model_dump_json()
            return json_str.encode("utf-8")

        except Exception as e:
            raise SerializationError(f"Failed to serialize message: {str(e)}") from e

    @staticmethod
    def deserialize(
        data: bytes,
        payload_class: type[BasePayload],
    ) -> BaseMessage[BasePayload]:
        """
        Deserialize bytes to message.

        Args:
            data: UTF-8 encoded JSON bytes
            payload_class: Payload class for validation

        Returns:
            Deserialized message

        Raises:
            SerializationError: If deserialization fails
        """
        try:
            # Decode bytes to JSON string
            json_str = data.decode("utf-8")

            # Parse JSON to dict
            raw_data = json.loads(json_str)

            # Deserialize using Pydantic
            # First parse the payload
            payload_data = raw_data.get("payload")
            if not payload_data:
                raise SerializationError("Missing payload in message")

            payload = payload_class(**payload_data)

            # Then create the message
            return BaseMessage[payload_class](  # type: ignore[valid-type]
                event_id=raw_data["event_id"],
                event_type=raw_data["event_type"],
                schema_version=raw_data.get("schema_version", "1.0.0"),
                timestamp=raw_data["timestamp"],
                source_service=raw_data["source_service"],
                payload=payload,
                correlation_id=raw_data.get("correlation_id"),
                trace_id=raw_data.get("trace_id"),
                parent_span_id=raw_data.get("parent_span_id"),
                metadata=raw_data.get("metadata", {}),
            )

        except json.JSONDecodeError as e:
            raise SerializationError(f"Invalid JSON: {str(e)}") from e

        except UnicodeDecodeError as e:
            raise SerializationError(f"Invalid UTF-8 encoding: {str(e)}") from e

        except KeyError as e:
            raise SerializationError(f"Missing required field in message: {str(e)}") from e

        except Exception as e:
            raise SerializationError(f"Failed to deserialize message: {str(e)}") from e

    @staticmethod
    def serialize_to_dict(message: BaseMessage[BasePayload]) -> dict[str, Any]:
        """
        Serialize message to dictionary.

        Args:
            message: Message to serialize

        Returns:
            Dictionary representation

        Raises:
            SerializationError: If serialization fails
        """
        try:
            return message.model_dump()

        except Exception as e:
            raise SerializationError(f"Failed to serialize message to dict: {str(e)}") from e

    @staticmethod
    def deserialize_from_dict(
        data: dict[str, Any],
        payload_class: type[BasePayload],
    ) -> BaseMessage[BasePayload]:
        """
        Deserialize dictionary to message.

        Args:
            data: Dictionary representation
            payload_class: Payload class for validation

        Returns:
            Deserialized message

        Raises:
            SerializationError: If deserialization fails
        """
        try:
            # Parse payload
            payload_data = data.get("payload")
            if not payload_data:
                raise SerializationError("Missing payload in message data")

            payload = payload_class(**payload_data)

            # Create message
            return BaseMessage[payload_class](  # type: ignore[valid-type]
                event_id=data["event_id"],
                event_type=data["event_type"],
                schema_version=data.get("schema_version", "1.0.0"),
                timestamp=data["timestamp"],
                source_service=data["source_service"],
                payload=payload,
                correlation_id=data.get("correlation_id"),
                trace_id=data.get("trace_id"),
                parent_span_id=data.get("parent_span_id"),
                metadata=data.get("metadata", {}),
            )

        except KeyError as e:
            raise SerializationError(f"Missing required field: {str(e)}") from e

        except Exception as e:
            raise SerializationError(f"Failed to deserialize from dict: {str(e)}") from e
