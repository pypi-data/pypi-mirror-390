"""Configuration builder for :mod:`dtpyfw.db` utilities."""

from typing import Any

__all__ = ("DatabaseConfig",)


class DatabaseConfig:
    """Simple builder for SQLAlchemy connection settings.

    This class provides a fluent interface for configuring database
    connections, supporting both synchronous and asynchronous drivers,
    connection pooling, and separate read/write database configurations.
    """

    def __init__(self) -> None:
        """Initialize DatabaseConfig with default settings."""
        self._config_data: dict[str, Any] = {
            "db_backend": "postgresql",
            "db_driver_async": "asyncpg",
            "connect_args": None,
        }

    def set_db_backend(self, db_backend: str) -> "DatabaseConfig":
        """Set the database backend.

        Args:
            db_backend: Database backend type (e.g., 'postgresql', 'mysql').

        Returns:
            Self for method chaining.
        """
        self._config_data["db_backend"] = db_backend
        return self

    def set_db_driver_sync(self, db_driver_sync: str) -> "DatabaseConfig":
        """Set the synchronous database driver.

        Args:
            db_driver_sync: Synchronous driver name (e.g., 'psycopg2').

        Returns:
            Self for method chaining.
        """
        self._config_data["db_driver_sync"] = db_driver_sync
        return self

    def set_db_driver_async(self, db_driver_async: str) -> "DatabaseConfig":
        """Set the asynchronous database driver.

        Args:
            db_driver_async: Asynchronous driver name (e.g., 'asyncpg').

        Returns:
            Self for method chaining.
        """
        self._config_data["db_driver_async"] = db_driver_async
        return self

    def set_connect_args(self, connect_args: dict) -> "DatabaseConfig":
        """Set extra connection arguments for the database driver.

        Args:
            connect_args: Dictionary of driver-specific connection arguments.

        Returns:
            Self for method chaining.
        """
        self._config_data["connect_args"] = connect_args
        return self

    def set_db_url(self, db_url: str) -> "DatabaseConfig":
        """Set full database URL for both read and write operations.

        Args:
            db_url: Complete database connection URL string.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_url"] = db_url
        return self

    def set_db_url_read(self, db_url_read: str) -> "DatabaseConfig":
        """Set a read-only database URL.

        If not provided, the write URL will be used for read operations.

        Args:
            db_url_read: Database URL for read-only operations.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_url_read"] = db_url_read
        return self

    def set_db_user(self, db_user: str) -> "DatabaseConfig":
        """Set the database username.

        Args:
            db_user: Database username for authentication.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_user"] = db_user
        return self

    def set_db_password(self, db_password: str) -> "DatabaseConfig":
        """Set the database password.

        Args:
            db_password: Database password for authentication.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_password"] = db_password
        return self

    def set_db_host(self, db_host: str) -> "DatabaseConfig":
        """Set the database host for write operations.

        Args:
            db_host: Hostname or IP address of the database server.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_host"] = db_host
        return self

    def set_db_host_read(self, db_host_read: str) -> "DatabaseConfig":
        """Set the database host for read-only operations.

        Args:
            db_host_read: Hostname or IP address for read replicas.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_host_read"] = db_host_read
        return self

    def set_db_port(self, db_port: int) -> "DatabaseConfig":
        """Set the database port.

        Args:
            db_port: Port number for database connections.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_port"] = db_port
        return self

    def set_db_name(self, db_name: str) -> "DatabaseConfig":
        """Set the database name.

        Args:
            db_name: Name of the database to connect to.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_name"] = db_name
        return self

    def set_db_ssl(self, db_ssl: bool) -> "DatabaseConfig":
        """Enable or disable SSL for the database connection.

        Args:
            db_ssl: True to enable SSL/TLS, False to disable.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_ssl"] = db_ssl
        return self

    def set_db_pool_size(self, db_pool_size: int) -> "DatabaseConfig":
        """Set the database connection pool size.

        Args:
            db_pool_size: Maximum number of connections in the pool.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_pool_size"] = db_pool_size
        return self

    def set_db_max_overflow(self, db_max_overflow: int) -> "DatabaseConfig":
        """Set the database connection pool overflow limit.

        Args:
            db_max_overflow: Maximum number of connections beyond pool_size.

        Returns:
            Self for method chaining.
        """
        self._config_data["db_max_overflow"] = db_max_overflow
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value, or the default if not found.
        """
        return self._config_data.get(key, default)
