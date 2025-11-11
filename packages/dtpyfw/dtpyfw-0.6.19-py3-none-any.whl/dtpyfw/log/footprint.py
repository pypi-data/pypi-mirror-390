"""Footprint logging utility for creating structured log entries."""

import logging
from typing import Any
from uuid import UUID

__all__ = ("leave",)


def leave(
    log_type: str = "info",
    controller: str = "not_specified",
    retention_days: int = 90,
    subject: str = "not_specified",
    message: str = "no_message",
    dealer_id: UUID | None = None,
    user_id: UUID | None = None,
    payload: Any | None = None,
    footprint: bool = True,
) -> None:
    """Create a structured log entry with detailed metadata.

    This function simplifies the creation of detailed, structured logs by
    packaging various pieces of information into a single log record. It
    is designed to be used with handlers that can process these structured
    details, such as the LoggerHandler.

    Args:
        log_type: The severity of the log (e.g., 'info', 'error', 'warning').
        controller: The component or function where the log originates.
        retention_days: The desired retention period for the log in days.
        subject: A brief summary of the log entry.
        message: The main log message content.
        dealer_id: The UUID of the associated dealer, if applicable.
        user_id: The UUID of the associated user, if applicable.
        payload: Additional data to include with the log (any JSON-serializable type).
        footprint: A flag to mark this log as a 'footprint' for filtering.
    """
    logger = logging.getLogger()
    kwargs: dict[str, Any] = {
        "footprint": footprint,
        "retention_days": retention_days,
        "log_type": log_type,
        "controller": controller,
        "subject": subject,
        "message": message,
        "dealer_id": dealer_id,
        "user_id": user_id,
        "payload": payload,
    }

    data: dict[str, Any] = {
        "msg": message,
        "extra": {
            "details": kwargs,
        },
    }

    error_mapper = {
        "critical": logger.critical,
        "error": logger.error,
        "warning": logger.warning,
        "debug": logger.debug,
    }.get(log_type.lower(), logger.info)

    error_mapper(**data)
