"""Custom exceptions and helpers for serializing them."""

import sys
import traceback
from typing import Any, Dict

__all__ = (
    "RequestException",
    "exception_to_dict",
)


class RequestException(Exception):
    """Exception raised when a handled HTTP request fails.

    Description:
        Custom exception for HTTP request failures, containing status code,
        controller context, and optional message. Can be configured to skip
        footprint logging.

    Args:
        status_code: HTTP status code of the failed request. Defaults to 500.
        controller: Name of the controller/module where the exception occurred.
        message: Human-readable description of the error.
        skip_footprint: If True, prevents automatic logging to footprint system.

    Attributes:
        status_code (int): The HTTP status code.
        controller (str | None): The controller identifier.
        message (str): The error message.
        skip_footprint (bool): Whether to skip footprint logging.
    """

    def __init__(
        self,
        status_code: int = 500,
        controller: str | None = None,
        message: str = "",
        skip_footprint: bool = True,
    ) -> None:
        self.status_code = status_code
        self.controller = controller
        self.message = message
        self.skip_footprint = skip_footprint
        super().__init__(self.controller)


def exception_to_dict(exc: Exception) -> Dict[str, Any]:
    """Return a serializable dictionary representing an exception.

    Description:
        Converts an exception object into a dictionary containing type,
        message, traceback details, and optional arguments for logging
        or API responses.

    Args:
        exc: The exception object to serialize.

    Returns:
        A dictionary with keys 'type', 'message', 'traceback', and optionally 'args'.
    """
    exc_type, exc_obj, tb = sys.exc_info()

    exc_dict: Dict[str, Any] = {
        "type": str(exc_type.__name__) if exc_type else "Unknown",
        "message": str(exc),
    }

    tb_info = traceback.extract_tb(tb)
    detailed_tb: list[Dict[str, Any]] = []
    for frame in tb_info:
        tb_details: Dict[str, Any] = {
            "filename": frame.filename,
            "line": frame.lineno,
            "function": frame.name,
            "text": frame.line,
        }
        detailed_tb.append(tb_details)

    exc_dict["traceback"] = detailed_tb

    if hasattr(exc, "args"):
        exc_dict["args"] = exc.args

    return exc_dict
