"""Validation exception handler middleware for FastAPI."""

import json

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response

from ..routes.response import return_response
from ...log import footprint

__all__ = ("validation_exception_handler",)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> Response:
    """Handle validation errors and format them into readable responses.

    Description:
        FastAPI exception handler that processes request validation errors,
        extracts the first error with location and message details, logs it,
        and returns a standardized 422 error response.

    Args:
        request: The incoming FastAPI request that failed validation.
        exc: The validation error exception containing error details.

    Returns:
        Response: Formatted JSON error response with status code 422.
    """
    error_message = ""
    for error in exc.errors():
        location = " -> ".join(map(str, error["loc"]))
        try:
            input_data = f", input: {json.dumps(error['input'], default=str)}"
        except Exception:
            input_data = ""

        error_message = (
            f"Error [location: '{location}'; message: '{error['msg']}'{input_data}]."
        )
        break

    footprint.leave(
        log_type="debug",
        controller="validation_exception_handler",
        subject="validation_exception",
        message=error_message,
        payload={
            "url": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
            "errors": exc.errors(),
        },
    )

    return return_response(
        data=error_message,
        status_code=422,
        response_class=JSONResponse,
    )
