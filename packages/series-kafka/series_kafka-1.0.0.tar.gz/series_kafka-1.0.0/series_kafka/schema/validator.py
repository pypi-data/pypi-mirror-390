"""Schema validation using Pydantic."""

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from series_kafka.core.message import BasePayload
from series_kafka.exceptions import SchemaValidationError


class SchemaValidator:
    """
    Validates payloads against Pydantic schemas.

    Uses Pydantic's built-in validation to ensure payloads
    conform to their schema definitions.
    """

    @staticmethod
    def validate_payload(
        payload_data: dict[str, Any],
        payload_class: type[BasePayload],
    ) -> BasePayload:
        """
        Validate payload data against a schema.

        Args:
            payload_data: Raw payload data (dict)
            payload_class: Pydantic payload class to validate against

        Returns:
            Validated payload instance

        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            # Pydantic validation
            return payload_class(**payload_data)

        except PydanticValidationError as e:
            # Convert Pydantic errors to our exception type
            errors = e.errors()
            error_messages = [f"{err['loc']}: {err['msg']}" for err in errors]

            raise SchemaValidationError(
                message=f"Payload validation failed: {'; '.join(error_messages)}",
                schema_name=payload_class.__name__,
                validation_errors=errors,
            ) from e

        except Exception as e:
            # Catch any other validation errors
            raise SchemaValidationError(
                message=f"Payload validation failed: {str(e)}",
                schema_name=payload_class.__name__,
            ) from e

    @staticmethod
    def validate_payload_instance(
        payload: BasePayload,
        payload_class: type[BasePayload],
    ) -> bool:
        """
        Validate that payload is instance of expected class.

        Args:
            payload: Payload instance
            payload_class: Expected payload class

        Returns:
            True if valid

        Raises:
            SchemaValidationError: If not instance of expected class
        """
        if not isinstance(payload, payload_class):
            raise SchemaValidationError(
                message=f"Expected payload of type {payload_class.__name__}, "
                f"got {type(payload).__name__}",
                schema_name=payload_class.__name__,
            )

        return True
