"""Redis configuration builder module.

This module provides a fluent builder interface for constructing Redis
connection configurations with support for URLs, authentication, SSL,
and connection pooling.
"""

from typing import Any, Dict

__all__ = ("RedisConfig",)


class RedisConfig:
    """Builder for constructing Redis connection configuration.

    Provides a fluent interface for setting Redis connection parameters
    including URL, host, port, database, authentication, SSL, and pooling options.
    All setter methods return self for method chaining.

    Example:
        >>> config = RedisConfig() \\
        ...     .set_redis_host("localhost") \\
        ...     .set_redis_port(6379) \\
        ...     .set_redis_db("0") \\
        ...     .set_redis_password("secret") \\
        ...     .set_redis_max_connections(20)
    """

    def __init__(self) -> None:
        """Initialize an empty Redis configuration.

        Creates a new configuration builder with no preset values.
        """
        self._config_data: Dict[str, Any] = {}

    def set_redis_url(self, redis_url: str) -> "RedisConfig":
        """Set the full Redis connection URL.

        Allows specifying a complete connection string instead of individual
        components. Takes precedence over individual host/port/db settings.

        Args:
            redis_url: Full Redis connection URL (e.g., redis://localhost:6379/0
                or rediss://user:pass@host:6379/0 for SSL with auth).

        Returns:
            RedisConfig: Self for method chaining.

        Example:
            >>> config = RedisConfig().set_redis_url("redis://localhost:6379/0")
        """
        self._config_data["redis_url"] = redis_url
        return self

    def set_redis_host(self, host: str) -> "RedisConfig":
        """Set the Redis server hostname or IP address.

        Args:
            host: The hostname or IP address of the Redis server
                (e.g., "localhost", "127.0.0.1", "redis.example.com").

        Returns:
            RedisConfig: Self for method chaining.
        """
        self._config_data["redis_host"] = host
        return self

    def set_redis_port(self, port: int) -> "RedisConfig":
        """Set the Redis server port number.

        Args:
            port: The port number on which Redis is listening (default is 6379).

        Returns:
            RedisConfig: Self for method chaining.
        """
        self._config_data["redis_port"] = port
        return self

    def set_redis_db(self, database: str) -> "RedisConfig":
        """Set the Redis database number to use.

        Args:
            database: The database number as a string (typically 0-15 for default Redis).

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            Redis database numbers are 0-indexed. Most configurations use database 0.
        """
        self._config_data["redis_db"] = database
        return self

    def set_redis_password(self, password: str) -> "RedisConfig":
        """Set the Redis authentication password.

        Args:
            password: The password for Redis authentication. Will be URL-encoded
                automatically when constructing connection URLs.

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            Use this for simple password authentication (Redis < 6) or with
            set_redis_username() for ACL authentication (Redis 6+).
        """
        self._config_data["redis_password"] = password
        return self

    def set_redis_username(self, username: str) -> "RedisConfig":
        """Set the Redis authentication username.

        Used for Redis ACL authentication in Redis 6+.

        Args:
            username: The username for Redis ACL authentication.

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            This requires Redis 6.0 or higher. For older versions, only use
            set_redis_password() without username.
        """
        self._config_data["redis_username"] = username
        return self

    def set_redis_ssl(self, ssl: bool) -> "RedisConfig":
        """Enable or disable SSL/TLS for Redis connections.

        Args:
            ssl: True to use SSL/TLS (rediss:// protocol), False for plain
                connection (redis:// protocol).

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            When enabled, the connection URL will use rediss:// instead of redis://.
        """
        self._config_data["redis_ssl"] = ssl
        return self

    def set_redis_max_connections(self, redis_max_connections: int) -> "RedisConfig":
        """Set the maximum number of connections in the pool.

        Args:
            redis_max_connections: Maximum number of concurrent connections allowed
                in the connection pool. Higher values allow more concurrent operations
                but consume more resources.

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            Default is typically 10. Adjust based on your application's concurrency needs.
        """
        self._config_data["redis_max_connections"] = redis_max_connections
        return self

    def set_redis_socket_timeout(self, redis_socket_timeout: int) -> "RedisConfig":
        """Set the socket timeout in seconds for Redis operations.

        Args:
            redis_socket_timeout: Timeout in seconds for socket operations.
                Operations exceeding this time will raise a timeout error.

        Returns:
            RedisConfig: Self for method chaining.

        Note:
            Default is typically 5 seconds. Lower values fail faster but may
            cause issues with slow networks or heavy server load.
        """
        self._config_data["redis_socket_timeout"] = redis_socket_timeout
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration parameter name to retrieve (e.g., "redis_host",
                "redis_port", "redis_max_connections").
            default: The default value to return if the key is not found.

        Returns:
            Any: The configuration value if it exists, otherwise the default value.

        Example:
            >>> config = RedisConfig().set_redis_host("localhost")
            >>> host = config.get("redis_host")  # Returns "localhost"
            >>> timeout = config.get("redis_timeout", 30)  # Returns 30 (default)
        """
        return self._config_data.get(key, default)
