"""Series Kafka SDK - Type-safe async event streaming for Python microservices."""

__version__ = "1.0.0"
__author__ = "Series Engineering"

# Core components
from series_kafka.core.consumer import AsyncConsumer, ConsumerConfig
from series_kafka.core.message import BaseMessage, BasePayload
from series_kafka.core.producer import AsyncProducer, ProducerConfig
from series_kafka.core.topic import Topic

# Exceptions
from series_kafka.exceptions import (
    FatalError,
    KafkaSDKError,
    RetryableError,
    ValidationError,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    # Core components
    "AsyncProducer",
    "AsyncConsumer",
    "BaseMessage",
    "BasePayload",
    "Topic",
    # Configuration
    "ProducerConfig",
    "ConsumerConfig",
    # Exceptions
    "KafkaSDKError",
    "RetryableError",
    "ValidationError",
    "FatalError",
]
