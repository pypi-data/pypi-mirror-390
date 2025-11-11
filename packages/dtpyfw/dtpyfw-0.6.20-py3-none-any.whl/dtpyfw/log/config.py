"""Logging configuration management."""

from typing import Any, Self

__all__ = ("LogConfig",)


class LogConfig:
    """A builder for configuring the logging system.

    This class provides a fluent interface for setting logging configuration
    options such as API endpoints, log levels, file storage, and Celery mode.
    All setter methods return self to enable method chaining.

    Attributes:
        _config_data: Internal dictionary storing configuration key-value pairs.

    Example:
        >>> config = LogConfig()
        >>> config.set_api_url("https://api.example.com/logs") \\
        ...       .set_log_level("DEBUG") \\
        ...       .set_log_print("true")
    """

    def __init__(self) -> None:
        """Initialize the LogConfig with an empty configuration dictionary."""
        self._config_data: dict[str, Any] = {}

    def set_api_url(self, api_url: str) -> Self:
        """Set the URL for the remote logging API.

        Args:
            api_url: The URL endpoint for the remote logging API.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["api_url"] = api_url
        return self

    def set_api_key(self, api_key: str) -> Self:
        """Set the API key for the remote logging API.

        Args:
            api_key: The authentication key for the remote logging API.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["api_key"] = api_key
        return self

    def set_log_print(self, log_print: str) -> Self:
        """Set whether to print logs to the console.

        Args:
            log_print: A string value indicating if console logging is enabled.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_print"] = log_print
        return self

    def set_log_store(self, log_store: str) -> Self:
        """Set whether to store logs (e.g., in a file or via API).

        Args:
            log_store: A string value indicating if log storage is enabled.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_store"] = log_store
        return self

    def set_log_level(self, log_level: str) -> Self:
        """Set the minimum logging level (e.g., 'INFO', 'DEBUG').

        Args:
            log_level: The logging level as a string (converted to uppercase).

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_level"] = log_level.upper()
        return self

    def set_log_file_name(self, log_file_name: str) -> Self:
        """Set the name of the log file.

        Args:
            log_file_name: The filename for storing log output.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_file_name"] = log_file_name
        return self

    def set_log_file_backup_count(self, log_file_backup_count: int) -> Self:
        """Set the number of backup log files to keep.

        Args:
            log_file_backup_count: The number of rotated log files to retain.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_file_backup_count"] = int(log_file_backup_count)
        return self

    def set_log_file_max_size(self, log_file_max_size: int) -> Self:
        """Set the maximum size of a log file in bytes.

        Args:
            log_file_max_size: The maximum log file size in bytes before rotation.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["log_file_max_size"] = int(log_file_max_size)
        return self

    def set_only_footprint_mode(self, only_footprint_mode: bool) -> Self:
        """Set whether to only log messages marked as 'footprints'.

        This is typically used with the API handler to filter logs, ensuring
        only logs explicitly marked as footprints are sent to the remote API.

        Args:
            only_footprint_mode: If True, only footprint logs are sent to API.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["only_footprint_mode"] = bool(only_footprint_mode)
        return self

    def set_celery_mode(self, celery_mode: bool) -> Self:
        """Configure logging for a Celery worker context.

        This adapts the logging setup for Celery's process model, enabling
        specialized handling for Celery workers and tasks.

        Args:
            celery_mode: If True, configure logging for Celery workers.

        Returns:
            The LogConfig instance for method chaining.
        """
        self._config_data["celery_mode"] = bool(celery_mode)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            The configuration value associated with the key, or the default.
        """
        return self._config_data.get(key, default)
