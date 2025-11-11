from typing import Any, Callable

from kafka import KafkaConsumer  # type: ignore[import-not-found]

from ..core.exception import exception_to_dict
from ..log import footprint
from .connection import KafkaInstance

# Type alias for message handler functions
MessageHandler = Callable[..., None]


class Consumer:
    """High-level Kafka consumer with topic-specific message handlers.

    This class simplifies message consumption by allowing registration
    of handler functions for different topics. It manages polling,
    message dispatching, and optional manual offset committing, with
    integrated error handling and logging.
    """

    def __init__(
        self, kafka_instance: KafkaInstance, topics: list[str], **consumer_kwargs: Any
    ) -> None:
        """Initialize the consumer with topics and configuration.

        Creates a KafkaConsumer instance subscribed to the specified topics
        and initializes the handler registry.

        Args:
            kafka_instance: KafkaInstance to create the consumer from.
            topics: List of topic names to subscribe to.
            **consumer_kwargs: Additional keyword arguments passed to the
                             underlying KafkaConsumer constructor.
        """
        # Create and subscribe consumer
        self._consumer: KafkaConsumer = kafka_instance.get_consumer(
            topics, **consumer_kwargs
        )
        self._handlers: dict[str, list[MessageHandler]] = {}

    def register_handler(self, topic: str, handler: MessageHandler) -> "Consumer":
        """Register a handler function for a specific topic.

        Associates a callback function with a topic. When messages are
        received from this topic, the handler will be invoked with message
        details. Multiple handlers can be registered for the same topic.

        Args:
            topic: Topic name to handle messages from.
            handler: Callback function that accepts keyword arguments:
                    - topic (str): The topic name
                    - partition (int): The partition number
                    - offset (int): The message offset
                    - key (bytes | None): The message key
                    - value (Any): The deserialized message value

        Returns:
            Self reference for method chaining.

        Example:
            >>> def my_handler(topic, partition, offset, key, value):
            ...     print(f"Received: {value} from {topic}")
            >>> consumer.register_handler('my-topic', my_handler)
        """
        self._handlers.setdefault(topic, []).append(handler)
        return self

    def commit(self) -> None:
        """Commit the current consumer offsets to Kafka.

        Manually commits the current read positions for all assigned partitions.
        This method should be called after successfully processing messages
        when enable_auto_commit is disabled to ensure message processing
        progress is persisted.

        Raises:
            Exception: Propagates any exception from the commit operation
                      after logging the error.

        Example:
            >>> consumer.consume(timeout_ms=5000)
            >>> # Process messages...
            >>> consumer.commit()
        """
        controller = f"{__name__}.Consumer.commit"
        try:
            self._consumer.commit()
        except Exception as e:
            footprint.leave(
                log_type="error",
                message="Error during commit()",
                controller=controller,
                subject="Commit Error",
                payload={
                    "error": exception_to_dict(e),
                },
            )
            raise

    def consume(self, timeout_ms: int = 1000) -> None:
        """Poll for new messages and dispatch them to registered handlers.

        Fetches new messages from subscribed topics and invokes all registered
        handlers for each message's topic. If enable_auto_commit is False,
        offsets are automatically committed after processing all polled messages.
        Handler exceptions are caught and logged but do not stop processing
        of other messages.

        Args:
            timeout_ms: Maximum time to block waiting for messages, in
                       milliseconds. Defaults to 1000ms (1 second).

        Example:
            >>> while True:
            ...     consumer.consume(timeout_ms=5000)
        """
        controller = f"{__name__}.Consumer.consume"
        try:
            records = self._consumer.poll(timeout_ms=timeout_ms)
            for tp_records in records.values():
                for msg in tp_records:
                    for handler in self._handlers.get(msg.topic, []):
                        try:
                            handler(
                                topic=msg.topic,
                                partition=msg.partition,
                                offset=msg.offset,
                                key=msg.key,
                                value=msg.value,
                            )
                        except Exception as e:
                            footprint.leave(
                                log_type="error",
                                message=f"Handler {handler.__name__} failed for topic {msg.topic}",
                                controller=controller,
                                subject="Handler failed",
                                payload={
                                    "error": exception_to_dict(e),
                                },
                            )

            # Commit manually if needed
            if not self._consumer.config.get("enable_auto_commit", True):
                self._consumer.commit()
        except Exception as e:
            footprint.leave(
                log_type="error",
                message="Error during consume()",
                controller=controller,
                subject="Consumer Error",
                payload={
                    "error": exception_to_dict(e),
                },
            )
