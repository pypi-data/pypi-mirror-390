"""Posts topic payload schemas."""

from datetime import datetime

from pydantic import Field

from series_kafka.core.message import BasePayload


class PostCreatedPayload(BasePayload):
    """Post created event payload."""

    post_id: str = Field(..., pattern=r"^post_")
    user_id: str = Field(..., pattern=r"^usr_")
    content: str = Field(..., min_length=1, max_length=50000)
    created_at: datetime


class PostUpdatedPayload(BasePayload):
    """Post updated event payload."""

    post_id: str = Field(..., pattern=r"^post_")
    user_id: str = Field(..., pattern=r"^usr_")
    content: str | None = Field(None, min_length=1, max_length=50000)
    updated_at: datetime


class PostDeletedPayload(BasePayload):
    """Post deleted event payload."""

    post_id: str = Field(..., pattern=r"^post_")
    user_id: str = Field(..., pattern=r"^usr_")
    deleted_at: datetime
