"""API-based log handler for sending logs to remote endpoints."""

import json
import logging
from time import sleep
from typing import Any

import requests

from . import footprint

__all__ = ("LoggerHandler",)


class Logger:
    """A client for sending log records to a remote API endpoint.

    This class handles the HTTP POST request to the logging API, including
    authentication and JSON serialization. It also implements a retry
    mechanism with backoff for transient network errors.

    Args:
        logging_api_url: The URL of the remote logging API endpoint.
        logging_api_key: The API key for authenticating with the logging API.
    """

    def __init__(self, logging_api_url: str, logging_api_key: str) -> None:
        """Initialize the Logger client with API endpoint and authentication.

        Args:
            logging_api_url: The URL of the remote logging API endpoint.
            logging_api_key: The API key for authenticating with the logging API.
        """
        self.api_url = logging_api_url
        self.api_key = logging_api_key

        self.headers = {
            "Authorization": f"{self.api_key}",
            "Content-Type": "application/json",
        }

    def log(self, details: dict[str, Any]) -> bool | None:
        """Send a log entry to the remote API.

        Attempts to send a log entry to the configured remote API endpoint
        with retry logic for handling transient network failures. Retries up
        to 5 times with a 3-second backoff between attempts.

        Args:
            details: A dictionary containing the log data to be sent to the API.

        Returns:
            True if the log was successfully sent, None otherwise.
        """
        controller = f"{__name__}.Logger.log"
        max_retries = 5
        backoff_seconds = 3
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    url=self.api_url,
                    data=json.dumps(details, default=str),
                    headers=self.headers,
                )
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    sleep(backoff_seconds)
                else:
                    footprint.leave(
                        log_type="warning",
                        controller=controller,
                        subject="Log Sending Error",
                        message=f"Failed to send log to API: {e}",
                        payload={
                            "data": details,
                        },
                    )
        return None


class LoggerHandler(logging.Handler):
    """A logging handler that sends log records to a remote API.

    This handler integrates with Python's logging framework to forward log
    records to a remote API endpoint. It can be configured to filter logs,
    sending only those marked as "footprints" when in footprint-only mode.

    Args:
        logging_api_url: The URL of the remote logging API endpoint.
        logging_api_key: The API key for authenticating with the logging API.
        only_footprint_mode: If True, only send logs marked as footprints.

    Attributes:
        only_footprint_mode: Whether to filter non-footprint logs.
        logger: The Logger instance used to send logs to the API.
    """

    def __init__(
        self,
        logging_api_url: str,
        logging_api_key: str,
        only_footprint_mode: bool,
    ) -> None:
        """Initialize the LoggerHandler with API configuration.

        Args:
            logging_api_url: The URL of the remote logging API endpoint.
            logging_api_key: The API key for authenticating with the logging API.
            only_footprint_mode: If True, only send logs marked as footprints.
        """
        super().__init__()
        self.only_footprint_mode = only_footprint_mode
        self.logger = Logger(
            logging_api_url=logging_api_url,
            logging_api_key=logging_api_key,
        )

    def emit(self, record: logging.LogRecord) -> None:
        """Process a log record and send it to the remote API.

        This method extracts details from the log record, formats them, and
        uses the Logger client to send the log to the remote API. When
        `only_footprint_mode` is enabled, it filters out non-footprint logs.

        Args:
            record: The log record to be emitted to the remote API.
        """
        details = record.__dict__.get("details") or {}

        if self.only_footprint_mode and not details.get("footprint"):
            return None

        details["log_type"] = details.get("log_type") or record.levelname.lower()
        details["subject"] = details.get("subject") or "Unnamed"
        details["controller"] = details.get("controller") or record.funcName
        details["message"] = details.get("message") or self.format(record)
        self.logger.log(details=details)
