"""Users topic payload schemas."""

from datetime import datetime

from pydantic import EmailStr, Field

from series_kafka.core.message import BasePayload


class UserCreatedPayload(BasePayload):
    """User created event payload."""

    user_id: str = Field(..., pattern=r"^usr_")
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=100)
    created_at: datetime


class UserUpdatedPayload(BasePayload):
    """User updated event payload."""

    user_id: str = Field(..., pattern=r"^usr_")
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=1, max_length=100)
    updated_at: datetime


class UserDeletedPayload(BasePayload):
    """User deleted event payload."""

    user_id: str = Field(..., pattern=r"^usr_")
    deleted_at: datetime
    deletion_reason: str | None = None
