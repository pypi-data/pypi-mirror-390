"""Exception hierarchy for Series Kafka SDK."""

from typing import Any


class KafkaSDKError(Exception):
    """
    Base exception for all Kafka SDK errors.

    All exceptions in the SDK inherit from this base class,
    allowing consumers to catch all SDK-related errors.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class RetryableError(KafkaSDKError):
    """
    Indicates a transient error that should be retried.

    Raised when an operation fails due to temporary conditions
    (network issues, broker unavailability, rate limiting, etc.).
    Consumer will retry with exponential backoff before sending to DLQ.

    Examples:
        - Kafka broker temporarily unavailable
        - Network timeout
        - Rate limit exceeded
        - Temporary service unavailability
    """

    def __init__(
        self,
        message: str,
        retry_after_seconds: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize retryable error.

        Args:
            message: Human-readable error message
            retry_after_seconds: Suggested retry delay (optional)
            details: Additional error context
        """
        super().__init__(message, details)
        self.retry_after_seconds = retry_after_seconds


class ValidationError(KafkaSDKError):
    """
    Indicates a schema or data validation error.

    Raised when a message fails validation against its schema.
    These errors are NOT retried and go directly to DLQ,
    as retrying will not fix invalid data.

    Examples:
        - Required field missing
        - Invalid data type
        - Pattern validation failure
        - Field constraint violation
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        invalid_value: Any = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Human-readable error message
            field_name: Name of the field that failed validation
            invalid_value: The invalid value that was provided
            details: Additional error context
        """
        super().__init__(message, details)
        self.field_name = field_name
        self.invalid_value = invalid_value


class FatalError(KafkaSDKError):
    """
    Indicates an unrecoverable error.

    Raised when an operation encounters a permanent failure
    that cannot be recovered through retries. Messages causing
    this error go directly to DLQ without retry attempts.

    Examples:
        - Configuration error
        - Authentication failure
        - Authorization denial
        - Resource not found (topic doesn't exist)
        - Unrecoverable application logic error
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize fatal error.

        Args:
            message: Human-readable error message
            error_code: Optional error code for categorization
            details: Additional error context
        """
        super().__init__(message, details)
        self.error_code = error_code


class ProducerError(KafkaSDKError):
    """
    Producer-specific error.

    Raised when producer operations fail.
    """


class ConsumerError(KafkaSDKError):
    """
    Consumer-specific error.

    Raised when consumer operations fail.
    """


class SchemaValidationError(ValidationError):
    """
    Schema validation error.

    Raised when a payload fails Pydantic schema validation.
    """

    def __init__(
        self,
        message: str,
        schema_name: str | None = None,
        validation_errors: list[dict[str, Any]] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize schema validation error.

        Args:
            message: Human-readable error message
            schema_name: Name of the schema that failed validation
            validation_errors: List of Pydantic validation errors
            details: Additional error context
        """
        super().__init__(message, details=details)
        self.schema_name = schema_name
        self.validation_errors = validation_errors or []


class DLQError(KafkaSDKError):
    """
    Dead Letter Queue error.

    Raised when DLQ operations fail.
    """


class SerializationError(KafkaSDKError):
    """
    Serialization/deserialization error.

    Raised when message serialization or deserialization fails.
    """


class TopicError(KafkaSDKError):
    """
    Topic-specific error.

    Raised when topic operations fail.
    """


class ConfigurationError(FatalError):
    """
    Configuration error.

    Raised when SDK configuration is invalid.
    """
