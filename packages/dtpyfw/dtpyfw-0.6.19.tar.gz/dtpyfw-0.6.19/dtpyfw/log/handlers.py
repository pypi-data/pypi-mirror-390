"""Log handler configuration and setup utilities."""

import logging
from logging.handlers import RotatingFileHandler

from .api_handler import LoggerHandler
from .config import LogConfig
from .formatter import CustomFormatter

__all__ = ("get_handlers_data",)


def get_handlers_data(config: LogConfig) -> tuple[list[logging.Handler], int]:
    """Configure and return a list of log handlers based on the provided
    config.

    This function sets up handlers for API logging, console output, and file
    rotation, depending on the settings in the LogConfig object. Each handler
    is configured with the appropriate formatter and log level.

    Args:
        config: The LogConfig object containing the logging configuration.

    Returns:
        A tuple containing:
            - A list of configured logging handlers (may be empty if no handlers enabled).
            - The resolved log level as a logging module constant (e.g., logging.INFO).
    """
    formatter = CustomFormatter()

    logging_api_url = config.get("api_url")
    logging_api_key = config.get("api_key")
    only_footprint_mode = config.get("only_footprint_mode", True)

    log_print = config.get("log_print", default=False)
    log_store = config.get("log_store", default=False)
    log_level = getattr(logging, config.get("log_level", default="INFO"))

    handlers: list[logging.Handler] = []

    if logging_api_url and logging_api_key:
        api_handler = LoggerHandler(
            logging_api_url=logging_api_url,
            logging_api_key=logging_api_key,
            only_footprint_mode=only_footprint_mode,
        )
        api_handler.setLevel(log_level)
        api_handler.setFormatter(formatter)
        handlers.append(api_handler)

    if log_print:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    if log_store:
        log_file_name = config.get("log_file_name", default="app.log")
        log_file_backup_count = config.get("log_file_backup_count", default=1) or 1
        log_file_max_size = config.get("log_file_max_size", default=(10 * 1024 * 1024))
        rotating_handler = RotatingFileHandler(
            log_file_name, maxBytes=log_file_max_size, backupCount=log_file_backup_count
        )
        rotating_handler.setLevel(log_level)
        rotating_handler.setFormatter(formatter)
        handlers.append(rotating_handler)

    return handlers, log_level
