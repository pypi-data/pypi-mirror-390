"""Logger initialization utilities for configuring logging system."""

import logging
from typing import Any

from .config import LogConfig
from .handlers import get_handlers_data

__all__ = (
    "log_initializer",
    "celery_logger_handler",
)


def log_initializer(config: LogConfig) -> None:
    """Initialize the root and Celery loggers based on the provided
    configuration.

    This function sets up the logging system by creating and attaching handlers
    to the root logger. If celery_mode is enabled in the configuration, it
    also configures the 'celery' logger with the same handlers and level.

    Args:
        config: The LogConfig object containing the logging configuration.
    """
    celery_mode = config.get("celery_mode", True)

    handlers, log_level = get_handlers_data(config=config)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    celery_logger = logging.getLogger("celery")

    if celery_mode:
        celery_logger.setLevel(log_level)

    for handle in handlers:
        root_logger.addHandler(handle)
        if celery_mode:
            celery_logger.addHandler(handle)


def celery_logger_handler(
    config: LogConfig,
    logger: Any,
    propagate: bool,
) -> None:
    """Configure a Celery logger with handlers from the provided configuration.

    This function is intended to be used within a Celery application to set up
    logging for its workers. It only applies the configuration if celery_mode
    is enabled in the config. The logger parameter should be a Celery logger
    instance obtained from the Celery signals.

    Args:
        config: The LogConfig object containing the logging configuration.
        logger: The Celery logger instance to configure (typically from signals).
        propagate: Whether the logger should propagate messages to its parent.
    """
    celery_mode = config.get("celery_mode", True)
    if celery_mode:
        handlers, log_level = get_handlers_data(config=config)
        logger.logLevel = log_level
        logger.propagate = propagate
        for handle in handlers:
            logger.addHandler(handle)
