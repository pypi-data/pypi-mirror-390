from contextlib import contextmanager
from typing import Any, Generator

from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import-not-found]

from ..core.exception import exception_to_dict
from .config import KafkaConfig
from ..log import footprint


class KafkaInstance:
    """Manages Kafka producer and consumer instances.

    This class simplifies the creation of Kafka clients by using a
    configuration object that can be initialized from either a single
    URL or individual connection parameters. It provides factory methods
    for creating producers and consumers with proper configuration and
    error handling.
    """

    def __init__(self, config: KafkaConfig) -> None:
        """Initialize the Kafka instance manager.

        Constructs the instance manager and builds the base configuration
        dictionary from the provided KafkaConfig object.

        Args:
            config: KafkaConfig instance containing connection settings.
        """
        self._config = config
        self._base: dict = self._build_base_config()

    def _build_base_config(self) -> dict[str, Any]:
        """Build the base configuration dictionary for Kafka clients.

        Constructs a configuration dictionary by extracting settings from
        the KafkaConfig object. Supports both URL-based configuration
        (via kafka_url) and individual parameter configuration
        (via bootstrap_servers and related settings).

        Returns:
            Dictionary with common Kafka connection settings suitable for
            passing to KafkaProducer or KafkaConsumer constructors.

        Raises:
            ValueError: If neither kafka_url nor bootstrap_servers is
                       provided in the configuration.
        """
        # If a full URL is provided, use it directly
        kafka_url = self._config.get("kafka_url")
        if kafka_url:
            return {"bootstrap_servers": [kafka_url]}

        # Otherwise build from individual params
        servers = self._config.get("bootstrap_servers")
        if not servers:
            raise ValueError("Either kafka_url or bootstrap_servers must be configured")
        base = {"bootstrap_servers": servers}

        for key in (
            "security_protocol",
            "sasl_mechanism",
            "sasl_plain_username",
            "sasl_plain_password",
            "client_id",
        ):
            value = self._config.get(key)
            if value:
                base[key] = value

        return base

    def get_producer(self, **kwargs: Any) -> KafkaProducer:
        """Create and return a KafkaProducer instance.

        Constructs a Kafka producer with the base configuration and
        automatically configures JSON serialization for message values.
        Logs any errors encountered during producer creation.

        Args:
            **kwargs: Additional keyword arguments to pass to the
                     KafkaProducer constructor, allowing override of
                     default settings.

        Returns:
            Configured KafkaProducer instance ready to send messages.

        Raises:
            Exception: Propagates any exception from KafkaProducer
                      initialization after logging the error.
        """
        controller = f"{__name__}.KafkaInstance.get_producer"
        try:
            return KafkaProducer(
                **self._base,
                value_serializer=lambda v: __import__("json").dumps(v).encode(),
                **kwargs,
            )
        except Exception as e:
            footprint.leave(
                log_type="error",
                message="Error creating KafkaProducer",
                controller=controller,
                subject="Kafka Producer",
                payload={
                    "error": exception_to_dict(e),
                },
            )
            raise

    def get_consumer(self, topics: list[str], **kwargs: Any) -> KafkaConsumer:
        """Create and return a KafkaConsumer subscribed to topics.

        Constructs a Kafka consumer with the base configuration plus
        consumer-specific settings (group_id, auto_offset_reset, etc.),
        and subscribes it to the specified topics. Logs any errors
        encountered during consumer creation.

        Args:
            topics: List of topic names to subscribe to.
            **kwargs: Additional keyword arguments to pass to the
                     KafkaConsumer constructor, allowing override of
                     default settings.

        Returns:
            Configured and subscribed KafkaConsumer instance ready to
            receive messages.

        Raises:
            Exception: Propagates any exception from KafkaConsumer
                      initialization or subscription after logging the error.
        """
        controller = f"{__name__}.KafkaInstance.get_consumer"
        try:
            consumer_config = {
                **self._base,
                "group_id": self._config.get("group_id"),
                "auto_offset_reset": self._config.get("auto_offset_reset", "latest"),
                "enable_auto_commit": self._config.get("enable_auto_commit", True),
                **kwargs,
            }
            consumer = KafkaConsumer(**consumer_config)
            consumer.subscribe(topics)
            return consumer
        except Exception as e:
            footprint.leave(
                log_type="error",
                message="Error creating KafkaConsumer",
                controller=controller,
                subject="Kafka Consumer",
                payload={
                    "error": exception_to_dict(e),
                },
            )
            raise

    @contextmanager
    def producer_context(self, **kwargs: Any) -> Generator[KafkaProducer, None, None]:
        """Provide a KafkaProducer as a context manager.

        Creates a Kafka producer that is automatically flushed and closed
        when the context exits, ensuring reliable message delivery and
        proper resource cleanup.

        Args:
            **kwargs: Additional arguments to pass to get_producer.

        Yields:
            KafkaProducer: Configured producer instance.

        Example:
            >>> with kafka_instance.producer_context() as producer:
            ...     producer.send('my-topic', value={'key': 'value'})
        """
        prod = self.get_producer(**kwargs)
        try:
            yield prod
        finally:
            prod.flush()
            prod.close()

    @contextmanager
    def consumer_context(
        self, topics: list[str], **kwargs: Any
    ) -> Generator[KafkaConsumer, None, None]:
        """Provide a KafkaConsumer as a context manager.

        Creates a Kafka consumer that is automatically closed when the
        context exits, ensuring proper resource cleanup and connection
        termination.

        Args:
            topics: List of topic names to subscribe to.
            **kwargs: Additional arguments to pass to get_consumer.

        Yields:
            KafkaConsumer: Configured and subscribed consumer instance.

        Example:
            >>> with kafka_instance.consumer_context(['my-topic']) as consumer:
            ...     for message in consumer:
            ...         print(message.value)
        """
        consumer = self.get_consumer(topics, **kwargs)
        try:
            yield consumer
        finally:
            consumer.close()
