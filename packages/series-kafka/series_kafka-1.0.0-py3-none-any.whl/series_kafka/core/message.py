"""Core message models for Series Kafka SDK."""

from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class BasePayload(BaseModel):
    """
    Base class for all event payloads.

    Provides strict validation with:
    - Type checking enforced
    - Extra fields forbidden
    - Assignment validation
    - Whitespace stripping for strings
    """

    model_config = {
        "validate_assignment": True,  # Validate on attribute assignment
        "extra": "forbid",  # Reject unknown fields
        "str_strip_whitespace": True,  # Strip whitespace from strings
        "frozen": False,  # Allow updates (unless payload sets frozen=True)
        "use_enum_values": True,  # Use enum values instead of enum instances
    }


TPayload = TypeVar("TPayload", bound=BasePayload)


class BaseMessage[TPayload: BasePayload](BaseModel):
    """
    Universal message envelope for all Kafka events.

    Provides:
    - Automatic event_id generation (UUID4)
    - Timestamp generation (UTC)
    - Immutability (frozen=True)
    - Type-safe payload (generic)
    - Distributed tracing support
    - Schema versioning

    Example:
        >>> from datetime import datetime
        >>> payload = UserCreatedPayload(
        ...     user_id="usr_123",
        ...     email="user@example.com",
        ...     username="johndoe",
        ...     created_at=datetime.now(timezone.utc)
        ... )
        >>> message = BaseMessage[UserCreatedPayload](
        ...     event_type="user.created",
        ...     source_service="stargate",
        ...     payload=payload
        ... )
        >>> print(message.event_id)  # Auto-generated UUID
        >>> print(message.model_dump_json())  # JSON serialization
    """

    # Event identity (auto-generated, immutable)
    event_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique event identifier (UUID4)",
        frozen=True,
    )

    # Event type (dot-separated format: service.action)
    event_type: str = Field(
        ...,
        description="Event type in format: service.action (e.g., user.created)",
        pattern=r"^[a-z_]+\.[a-z_]+$",
        frozen=True,
        min_length=3,
        max_length=100,
    )

    # Schema versioning (semantic versioning)
    schema_version: str = Field(
        default="1.0.0",
        description="Schema version (semantic versioning)",
        pattern=r"^\d+\.\d+\.\d+$",
        max_length=20,
    )

    # Metadata (auto-generated timestamp)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp (UTC)",
    )

    source_service: str = Field(
        ...,
        description="Name of the service that produced this event",
        min_length=1,
        max_length=100,
    )

    # Payload (type-safe generic)
    payload: TPayload = Field(..., description="Event payload (type-safe)")

    # Distributed tracing fields (optional)
    correlation_id: str | None = Field(
        default=None,
        description="Request correlation ID for tracking across services",
        max_length=200,
    )

    trace_id: str | None = Field(
        default=None,
        description="OpenTelemetry trace ID",
        max_length=200,
    )

    parent_span_id: str | None = Field(
        default=None,
        description="OpenTelemetry parent span ID",
        max_length=200,
    )

    # Additional metadata (arbitrary key-value pairs)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for this event",
    )

    model_config = {
        "frozen": True,  # Message is immutable after creation
        "arbitrary_types_allowed": True,  # Allow custom types
        "validate_assignment": True,  # Validate on attribute assignment
        "extra": "forbid",  # Reject unknown fields
    }

    @field_validator("event_type")
    @classmethod
    def validate_event_type_format(cls, value: str) -> str:
        """
        Validate event type format.

        Must be lowercase with underscore separators, format: service.action
        """
        if not value:
            msg = "event_type cannot be empty"
            raise ValueError(msg)

        parts = value.split(".")
        if len(parts) != 2:
            msg = f"event_type must be in format 'service.action', got: {value}"
            raise ValueError(msg)

        service, action = parts
        if not service or not action:
            msg = f"event_type parts cannot be empty: {value}"
            raise ValueError(msg)

        return value

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        """Validate semantic versioning format."""
        parts = value.split(".")
        if len(parts) != 3:
            msg = f"schema_version must be semantic version (X.Y.Z), got: {value}"
            raise ValueError(msg)

        for part in parts:
            if not part.isdigit():
                msg = f"schema_version must contain only digits, got: {value}"
                raise ValueError(msg)

        return value

    @field_validator("timestamp")
    @classmethod
    def ensure_utc_timezone(cls, value: datetime) -> datetime:
        """Ensure timestamp is timezone-aware and in UTC."""
        if value.tzinfo is None:
            # Assume UTC if no timezone provided
            return value.replace(tzinfo=UTC)
        # Convert to UTC if different timezone
        return value.astimezone(UTC)

    def model_dump_json(self, **kwargs: Any) -> str:
        """
        Serialize message to JSON string.

        Automatically handles datetime serialization to ISO format.
        """
        # Set defaults for JSON serialization
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", False)

        return super().model_dump_json(**kwargs)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """
        Convert message to dictionary.

        Useful for inspection and debugging.
        """
        kwargs.setdefault("by_alias", True)
        kwargs.setdefault("exclude_none", False)

        return super().model_dump(**kwargs)
