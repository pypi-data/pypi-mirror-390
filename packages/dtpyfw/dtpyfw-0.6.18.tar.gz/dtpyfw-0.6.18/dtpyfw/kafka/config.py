from typing import Any


class KafkaConfig:
    """Builder for Kafka connection settings.

    A configuration builder that supports both full URL-based
    configuration and individual parameter-based configuration for Kafka
    clients. Provides a fluent interface for setting connection
    parameters.
    """

    def __init__(self) -> None:
        """Initialize an empty Kafka configuration.

        Creates a new KafkaConfig instance with an empty configuration
        dictionary that can be populated using setter methods.
        """
        self._config: dict[str, Any] = {}

    def set_kafka_url(self, url: str) -> "KafkaConfig":
        """Set the full Kafka connection URL.

        Provide a complete Kafka URL with authentication and multiple brokers.
        This method simplifies configuration when all connection details can
        be expressed in a single URL string.

        Args:
            url: Complete Kafka URL in format
                 'kafka://user:pass@host1:9092,host2:9092'

        Returns:
            Self reference for method chaining.
        """
        self._config["kafka_url"] = url
        return self

    def set_bootstrap_servers(self, servers: list[str]) -> "KafkaConfig":
        """Set the list of Kafka bootstrap servers.

        Configure the initial Kafka broker addresses used to discover
        the full cluster membership.

        Args:
            servers: List of broker addresses in 'host:port' format.

        Returns:
            Self reference for method chaining.
        """
        self._config["bootstrap_servers"] = servers
        return self

    def set_security_protocol(self, protocol: str) -> "KafkaConfig":
        """Set the security protocol for broker communication.

        Defines the protocol used to communicate with brokers, determining
        encryption and authentication requirements.

        Args:
            protocol: Protocol name such as 'PLAINTEXT', 'SSL', 'SASL_PLAINTEXT',
                     or 'SASL_SSL'.

        Returns:
            Self reference for method chaining.
        """
        self._config["security_protocol"] = protocol
        return self

    def set_sasl_mechanism(self, mechanism: str) -> "KafkaConfig":
        """Set the SASL authentication mechanism.

        Specifies which SASL mechanism to use for authentication when
        using SASL-based security protocols.

        Args:
            mechanism: SASL mechanism name such as 'PLAIN', 'SCRAM-SHA-256',
                      'SCRAM-SHA-512', or 'GSSAPI'.

        Returns:
            Self reference for method chaining.
        """
        self._config["sasl_mechanism"] = mechanism
        return self

    def set_sasl_plain_username(self, username: str) -> "KafkaConfig":
        """Set the username for PLAIN SASL authentication.

        Configures the username credential used with SASL/PLAIN
        authentication mechanism.

        Args:
            username: Authentication username for SASL/PLAIN.

        Returns:
            Self reference for method chaining.
        """
        self._config["sasl_plain_username"] = username
        return self

    def set_sasl_plain_password(self, password: str) -> "KafkaConfig":
        """Set the password for PLAIN SASL authentication.

        Configures the password credential used with SASL/PLAIN
        authentication mechanism.

        Args:
            password: Authentication password for SASL/PLAIN.

        Returns:
            Self reference for method chaining.
        """
        self._config["sasl_plain_password"] = password
        return self

    def set_client_id(self, client_id: str) -> "KafkaConfig":
        """Set the client identifier for Kafka connections.

        Assigns a logical identifier for the client application, which
        appears in broker logs and metrics.

        Args:
            client_id: Unique identifier for this Kafka client application.

        Returns:
            Self reference for method chaining.
        """
        self._config["client_id"] = client_id
        return self

    def set_group_id(self, group_id: str) -> "KafkaConfig":
        """Set the consumer group identifier.

        Assigns the consumer group ID for coordinating consumption across
        multiple consumer instances. Required for consumer applications.

        Args:
            group_id: Unique identifier for the consumer group.

        Returns:
            Self reference for method chaining.
        """
        self._config["group_id"] = group_id
        return self

    def set_auto_offset_reset(self, offset: str) -> "KafkaConfig":
        """Set the auto offset reset policy.

        Defines what to do when there is no initial offset in Kafka or if
        the current offset no longer exists on the server.

        Args:
            offset: Reset policy - 'earliest' to reset to the beginning,
                   'latest' to reset to the end, or 'none' to throw exception.

        Returns:
            Self reference for method chaining.
        """
        self._config["auto_offset_reset"] = offset
        return self

    def set_enable_auto_commit(self, flag: bool) -> "KafkaConfig":
        """Enable or disable automatic offset committing.

        Controls whether consumed message offsets are automatically
        committed to Kafka or must be manually committed.

        Args:
            flag: True to enable auto-commit, False to require manual commits.

        Returns:
            Self reference for method chaining.
        """
        self._config["enable_auto_commit"] = flag
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Access a stored configuration parameter, returning a default
        value if the key is not present.

        Args:
            key: The configuration parameter name to retrieve.
            default: Value to return if key is not found. Defaults to None.

        Returns:
            The configuration value associated with the key, or the default
            value if the key does not exist.
        """
        return self._config.get(key, default)
