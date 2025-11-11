from typing import Any

from kafka import KafkaProducer  # type: ignore[import-not-found]

from ..core.exception import exception_to_dict
from .connection import KafkaInstance
from ..log import footprint


class Producer:
    """High-level wrapper for Kafka message production.

    This class simplifies sending messages to Kafka topics by providing
    a clean interface with built-in error handling and logging. Messages
    are automatically JSON-encoded before transmission.
    """

    def __init__(self, kafka_instance: KafkaInstance) -> None:
        """Initialize the producer from a Kafka instance.

        Creates the underlying KafkaProducer with JSON serialization
        configured for message values.

        Args:
            kafka_instance: KafkaInstance to create the producer from.
        """
        self._producer: KafkaProducer = kafka_instance.get_producer()

    def send(
        self, topic: str, value: Any, key: str | bytes | None = None, timeout: int = 10
    ) -> None:
        """Send a message to a Kafka topic.

        Publishes a message to the specified topic and waits for broker
        acknowledgment. The message value is automatically JSON-encoded,
        and the operation is logged for monitoring purposes.

        Args:
            topic: Target topic name for the message. Must be a non-empty string.
            value: Message payload to send. Will be JSON-serialized automatically.
            key: Optional message key for partitioning and compaction.
                Can be a string (UTF-8 encoded) or bytes. Defaults to None.
            timeout: Maximum time in seconds to wait for broker acknowledgment.
                    Defaults to 10 seconds.

        Raises:
            ValueError: If topic is not a non-empty string.
            Exception: If message sending fails or times out after logging
                      the error details.

        Example:
            >>> producer = Producer(kafka_instance)
            >>> producer.send('my-topic', {'data': 'value'}, key='msg-1')
        """
        controller = f"{__name__}.Producer.send"
        if not isinstance(topic, str) or not topic:
            raise ValueError("`topic` must be a non-empty string")

        encoded_key: bytes | None
        if isinstance(key, str):
            encoded_key = key.encode("utf-8")
        else:
            encoded_key = key

        try:
            future = self._producer.send(topic, key=encoded_key, value=value)
            future.get(timeout=timeout)
            footprint.leave(
                log_type="info",
                message=f"Message {key!r} has been sent to {topic}",
                controller=controller,
                subject="Message sent",
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                message=f"Failed to send message to topic {topic}",
                controller=controller,
                subject="Producer Error",
                payload={
                    "error": exception_to_dict(e),
                },
            )
            raise
