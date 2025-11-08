"""Message topic payload schemas."""

from pydantic import EmailStr, Field

from series_kafka.core.message import BasePayload


class SendBluePayload(BasePayload):
    """SendBlue webhook message payload."""

    account_email: EmailStr
    content: str = Field(..., min_length=1, max_length=10000)
    from_number: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    to_number: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    message_handle: str
    status: str
    date_sent: str
    date_updated: str
    is_outbound: bool

    # Optional fields
    media_url: str | None = None
    error_code: str | None = None


class LinqPayload(BasePayload):
    """Linq message payload."""

    conversation_id: str
    user_id: str = Field(..., pattern=r"^usr_")
    content: str = Field(..., min_length=1, max_length=10000)
    from_number: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    to_number: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    timestamp: str


class AgentResponsePayload(BasePayload):
    """AI agent response payload."""

    user_id: str = Field(..., pattern=r"^usr_")
    conversation_id: str
    response_text: str = Field(..., min_length=1)
    intent: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float = Field(..., ge=0.0)
    model_version: str = "v1.0"
