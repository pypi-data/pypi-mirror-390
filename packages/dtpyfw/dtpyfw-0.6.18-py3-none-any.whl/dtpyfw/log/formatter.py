"""Custom log formatter for structured logging output."""

import logging

__all__ = ("CustomFormatter",)


class CustomFormatter(logging.Formatter):
    """A custom log formatter that adapts to structured 'details'.

    This formatter checks if a log record has a 'details' attribute. If
    it does, it formats the log message to include the entire 'details'
    dictionary. Otherwise, it falls back to the standard message format.
    """

    def __init__(self) -> None:
        """Initialize the CustomFormatter with a default date format."""
        super().__init__(None, "%Y-%m-%d %H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        """Format the specified log record as text.

        Dynamically adjusts the format string based on whether the record
        contains a structured 'details' attribute or not. This allows
        structured logs to display their full details dictionary while
        standard logs use the basic message format.

        Args:
            record: The log record to format.

        Returns:
            The formatted log string with timestamp, level, and message or details.
        """
        if hasattr(record, "details"):
            self._style._fmt = "%(asctime)s - %(levelname)s - %(details)s"
        else:
            self._style._fmt = "%(asctime)s - %(levelname)s - %(message)s"
        return super().format(record)
