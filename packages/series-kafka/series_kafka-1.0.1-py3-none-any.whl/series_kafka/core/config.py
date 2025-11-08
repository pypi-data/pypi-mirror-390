"""Configuration models for Kafka producer and consumer."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from series_kafka.exceptions import ConfigurationError


class ProducerConfig(BaseModel):
    """
    Configuration for Kafka producer.

    Provides type-safe configuration with validation for:
    - Kafka connection (bootstrap servers, SASL auth)
    - Service identity
    - Idempotency settings
    - Observability (metrics, tracing)
    - Schema registry (optional)
    """

    # Kafka connection
    bootstrap_servers: str = Field(
        ...,
        description="Kafka bootstrap servers (comma-separated)",
        min_length=1,
        max_length=500,
    )

    sasl_username: str | None = Field(
        default=None,
        description="SASL username for authentication",
        max_length=200,
    )

    sasl_password: str | None = Field(
        default=None,
        description="SASL password for authentication",
        max_length=200,
    )

    sasl_mechanism: str = Field(
        default="PLAIN",
        description="SASL mechanism (PLAIN, SCRAM-SHA-256, SCRAM-SHA-512)",
    )

    security_protocol: str = Field(
        default="SASL_SSL",
        description="Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)",
    )

    # Service identity
    service_name: str = Field(
        ...,
        description="Name of the service using this producer",
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9_-]+$",
    )

    # Idempotency (default: enabled)
    enable_idempotence: bool = Field(
        default=True,
        description="Enable idempotent producer for exactly-once delivery",
    )

    # Observability (default: disabled)
    enable_metrics: bool = Field(
        default=False,
        description="Enable OpenTelemetry metrics",
    )

    enable_tracing: bool = Field(
        default=False,
        description="Enable OpenTelemetry distributed tracing",
    )

    # Schema registry (optional)
    schema_registry_url: str | None = Field(
        default=None,
        description="Schema registry URL (optional)",
        max_length=500,
    )

    # Producer performance tuning
    acks: str | int = Field(
        default="all",
        description="Number of acknowledgments required (-1, 0, 1, 'all')",
    )

    compression_type: str = Field(
        default="gzip",
        description="Compression type (none, gzip, snappy, lz4, zstd)",
    )

    max_in_flight_requests_per_connection: int = Field(
        default=5,
        description="Max requests in flight per connection",
        ge=1,
        le=100,
    )

    request_timeout_ms: int = Field(
        default=30000,
        description="Request timeout in milliseconds",
        ge=1000,
        le=300000,
    )

    retries: int = Field(
        default=10,
        description="Number of retries for transient errors",
        ge=0,
        le=100,
    )

    # Batching
    batch_size: int = Field(
        default=16384,
        description="Batch size in bytes",
        ge=1024,
        le=1048576,
    )

    linger_ms: int = Field(
        default=10,
        description="Linger time before sending batch (milliseconds)",
        ge=0,
        le=10000,
    )

    # Buffer
    buffer_memory: int = Field(
        default=33554432,  # 32MB
        description="Total memory buffer for producer (bytes)",
        ge=1048576,  # 1MB minimum
        le=1073741824,  # 1GB maximum
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }

    @field_validator("sasl_mechanism")
    @classmethod
    def validate_sasl_mechanism(cls, value: str) -> str:
        """Validate SASL mechanism."""
        valid_mechanisms = {"PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512"}
        if value not in valid_mechanisms:
            msg = f"Invalid SASL mechanism: {value}. Must be one of {valid_mechanisms}"
            raise ConfigurationError(msg)
        return value

    @field_validator("security_protocol")
    @classmethod
    def validate_security_protocol(cls, value: str) -> str:
        """Validate security protocol."""
        valid_protocols = {"PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"}
        if value not in valid_protocols:
            msg = f"Invalid security protocol: {value}. Must be one of {valid_protocols}"
            raise ConfigurationError(msg)
        return value

    @field_validator("compression_type")
    @classmethod
    def validate_compression_type(cls, value: str) -> str:
        """Validate compression type."""
        valid_types = {"none", "gzip", "snappy", "lz4", "zstd"}
        if value not in valid_types:
            msg = f"Invalid compression type: {value}. Must be one of {valid_types}"
            raise ConfigurationError(msg)
        return value

    @field_validator("acks")
    @classmethod
    def validate_acks(cls, value: str | int) -> str | int:
        """Validate acks setting."""
        if isinstance(value, str):
            if value not in {"all", "-1", "0", "1"}:
                msg = f"Invalid acks value: {value}. Must be 'all', -1, 0, or 1"
                raise ConfigurationError(msg)
        elif isinstance(value, int):
            if value not in {-1, 0, 1}:
                msg = f"Invalid acks value: {value}. Must be -1, 0, or 1"
                raise ConfigurationError(msg)
        return value

    @property
    def kafka_config(self) -> dict[str, Any]:
        """
        Generate aiokafka producer configuration.

        Returns:
            Dictionary of aiokafka-compatible configuration
        """
        config: dict[str, Any] = {
            "bootstrap_servers": self.bootstrap_servers,
            "enable_idempotence": self.enable_idempotence,
            "acks": self.acks,
            "compression_type": self.compression_type,
            "request_timeout_ms": self.request_timeout_ms,
            "linger_ms": self.linger_ms,
            "max_batch_size": self.batch_size,  # aiokafka uses max_batch_size
            "retry_backoff_ms": (self.retries * 100),  # Convert retries to backoff
        }

        # Add SASL authentication if provided
        if self.sasl_username and self.sasl_password:
            config.update(
                {
                    "security_protocol": self.security_protocol,
                    "sasl_mechanism": self.sasl_mechanism,
                    "sasl_plain_username": self.sasl_username,
                    "sasl_plain_password": self.sasl_password,
                }
            )

        return config


class ConsumerConfig(BaseModel):
    """
    Configuration for Kafka consumer.

    Provides type-safe configuration with validation for:
    - Kafka connection
    - Consumer group settings
    - DLQ settings
    - Retry configuration
    - Event filtering
    - Subset field extraction
    - Graceful shutdown
    """

    # Kafka connection
    bootstrap_servers: str = Field(
        ...,
        description="Kafka bootstrap servers (comma-separated)",
        min_length=1,
        max_length=500,
    )

    sasl_username: str | None = Field(
        default=None,
        description="SASL username for authentication",
        max_length=200,
    )

    sasl_password: str | None = Field(
        default=None,
        description="SASL password for authentication",
        max_length=200,
    )

    sasl_mechanism: str = Field(
        default="PLAIN",
        description="SASL mechanism (PLAIN, SCRAM-SHA-256, SCRAM-SHA-512)",
    )

    security_protocol: str = Field(
        default="SASL_SSL",
        description="Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)",
    )

    # Consumer group
    group_id: str = Field(
        ...,
        description="Consumer group ID",
        min_length=1,
        max_length=200,
    )

    # Service identity
    service_name: str = Field(
        ...,
        description="Name of the service using this consumer",
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9_-]+$",
    )

    # DLQ settings (default: enabled)
    enable_dlq: bool = Field(
        default=True,
        description="Enable dead letter queue for failed messages",
    )

    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts before sending to DLQ",
        ge=0,
        le=10,
    )

    retry_backoff_ms: int = Field(
        default=1000,
        description="Base backoff time for retries in milliseconds",
        ge=100,
        le=60000,
    )

    # Event filtering (optional)
    event_type_filter: set[str] | None = Field(
        default=None,
        description="Filter to specific event types (e.g., {'user.created', 'user.updated'})",
    )

    # Subset field extraction (optional)
    subset_fields: list[str] | None = Field(
        default=None,
        description="Extract only specific fields (dot notation, e.g., ['payload.user_id'])",
    )

    # Observability (default: disabled)
    enable_metrics: bool = Field(
        default=False,
        description="Enable OpenTelemetry metrics",
    )

    enable_tracing: bool = Field(
        default=False,
        description="Enable OpenTelemetry distributed tracing",
    )

    # Consumer settings
    auto_offset_reset: str = Field(
        default="earliest",
        description="Offset reset strategy (earliest, latest)",
    )

    enable_auto_commit: bool = Field(
        default=False,
        description="Enable auto commit (False = manual commit)",
    )

    max_poll_records: int = Field(
        default=500,
        description="Maximum records per poll",
        ge=1,
        le=10000,
    )

    session_timeout_ms: int = Field(
        default=30000,
        description="Session timeout in milliseconds",
        ge=6000,
        le=300000,
    )

    heartbeat_interval_ms: int = Field(
        default=3000,
        description="Heartbeat interval in milliseconds",
        ge=1000,
        le=30000,
    )

    # Graceful shutdown
    shutdown_timeout_seconds: int = Field(
        default=30,
        description="Timeout for graceful shutdown in seconds",
        ge=5,
        le=300,
    )

    model_config = {
        "validate_assignment": True,
        "extra": "forbid",
    }

    @field_validator("sasl_mechanism")
    @classmethod
    def validate_sasl_mechanism(cls, value: str) -> str:
        """Validate SASL mechanism."""
        valid_mechanisms = {"PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512"}
        if value not in valid_mechanisms:
            msg = f"Invalid SASL mechanism: {value}. Must be one of {valid_mechanisms}"
            raise ConfigurationError(msg)
        return value

    @field_validator("security_protocol")
    @classmethod
    def validate_security_protocol(cls, value: str) -> str:
        """Validate security protocol."""
        valid_protocols = {"PLAINTEXT", "SSL", "SASL_PLAINTEXT", "SASL_SSL"}
        if value not in valid_protocols:
            msg = f"Invalid security protocol: {value}. Must be one of {valid_protocols}"
            raise ConfigurationError(msg)
        return value

    @field_validator("auto_offset_reset")
    @classmethod
    def validate_auto_offset_reset(cls, value: str) -> str:
        """Validate auto offset reset strategy."""
        valid_strategies = {"earliest", "latest"}
        if value not in valid_strategies:
            msg = f"Invalid auto_offset_reset: {value}. Must be one of {valid_strategies}"
            raise ConfigurationError(msg)
        return value

    @field_validator("heartbeat_interval_ms", "session_timeout_ms")
    @classmethod
    def validate_heartbeat_session_relationship(cls, value: int, info: Any) -> int:
        """Validate heartbeat interval is less than session timeout."""
        # This validator runs for both fields, so we need to check if both are available
        if info.field_name == "heartbeat_interval_ms" and "session_timeout_ms" in info.data:
            if value >= info.data["session_timeout_ms"]:
                msg = "heartbeat_interval_ms must be less than session_timeout_ms"
                raise ConfigurationError(msg)
        return value

    @property
    def kafka_config(self) -> dict[str, Any]:
        """
        Generate aiokafka consumer configuration.

        Returns:
            Dictionary of aiokafka-compatible configuration
        """
        config: dict[str, Any] = {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": self.group_id,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "max_poll_records": self.max_poll_records,
            "session_timeout_ms": self.session_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
        }

        # Add SASL authentication if provided
        if self.sasl_username and self.sasl_password:
            config.update(
                {
                    "security_protocol": self.security_protocol,
                    "sasl_mechanism": self.sasl_mechanism,
                    "sasl_plain_username": self.sasl_username,
                    "sasl_plain_password": self.sasl_password,
                }
            )

        return config
