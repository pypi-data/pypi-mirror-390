"""HTTP exception handler middleware for FastAPI."""

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..routes.response import return_response
from ...log import footprint

__all__ = ("http_exception_handler",)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    """Handle HTTP exceptions and log them appropriately.

    Description:
        FastAPI exception handler that processes HTTP errors, logs them with
        detailed context, and returns a standardized error response.

    Args:
        request: The incoming FastAPI request that triggered the exception.
        exc: The HTTP exception instance containing status code and error details.

    Returns:
        Response: Formatted JSON error response with appropriate status code.
    """
    status_code = exc.status_code
    detail = request.url.path if status_code == 404 else exc.detail

    footprint.leave(
        log_type="debug",
        controller="http_exception_handler",
        subject="http_exception",
        message=str(detail),
        payload={
            "status_code": status_code,
            "url": request.url.path,
            "method": request.method,
            "headers": dict(request.headers),
        },
    )

    return return_response(
        data=str(detail),
        status_code=status_code,
        response_class=JSONResponse,
    )
