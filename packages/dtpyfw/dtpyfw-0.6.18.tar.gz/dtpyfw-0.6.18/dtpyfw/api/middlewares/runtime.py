"""Runtime error handling middleware for FastAPI applications."""

from typing import Any, Callable, Dict

from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from ..routes.response import return_response
from ...core.exception import RequestException, exception_to_dict
from ...log import footprint

__all__ = ("Runtime",)


class Runtime:
    """Middleware for catching and handling runtime exceptions in FastAPI apps.

    Description:
        Intercepts all exceptions during request processing, logs them with
        detailed context, and returns standardized error responses to clients.
    """

    def __init__(self, hide_error_messages: bool = True) -> None:
        """Initialize the runtime error handler.

        Description:
            Configures whether detailed error messages should be exposed to
            clients or hidden for security purposes.

        Args:
            hide_error_messages: If True, returns generic error messages to clients.

        Returns:
            None
        """
        self.hide_error_messages = hide_error_messages

    @staticmethod
    async def get_request_body(request: Request) -> Dict[str, Any]:
        """Extract and serialize the request body if it's not too large.

        Description:
            Safely extracts the request body for logging, skipping bodies larger
            than 1MB to avoid memory issues.

        Args:
            request: The incoming FastAPI request.

        Returns:
            Dict[str, Any]: Dictionary containing content metadata and body JSON.
        """
        content_length = request.headers.get("content-length")
        content_type = request.headers.get("content-type")
        try:
            if content_length and int(content_length) > (1 * 1024 * 1024):
                return {}
            body = await request.body()
            return {
                "content_length": content_length,
                "content_type": content_type,
                "json": jsonable_encoder(body.decode("utf-8")),
            }
        except Exception:
            return {
                "content_length": content_length,
                "content_type": content_type,
            }

    @staticmethod
    async def create_payload(request: Request, exception: Exception) -> Dict[str, Any]:
        """Build a detailed payload for logging exceptions.

        Description:
            Constructs a comprehensive payload containing request details (path,
            method, headers, body) and exception information for logging.

        Args:
            request: The incoming FastAPI request that triggered the exception.
            exception: The exception instance that was raised.

        Returns:
            Dict[str, Any]: JSON-serializable payload for logging.
        """
        body = await Runtime.get_request_body(request)
        return jsonable_encoder(
            {
                "path": request.url.path,
                "method": request.method,
                "query_parameters": request.query_params,
                "path_parameters": request.path_params,
                "headers": request.headers,
                "body": body,
                **exception_to_dict(exception),
            }
        )

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process requests and handle any exceptions that occur.

        Description:
            Starlette middleware dispatch method that wraps the request processing
            chain, catching RequestException and general Exception instances, logging
            them, and returning appropriate error responses.

        Args:
            request: The incoming FastAPI request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: Either the successful response from call_next or an error response.
        """
        controller = f"{__name__}.Runtime.__call__"
        try:
            response = await call_next(request)
        except RequestException as e:
            payload = await self.create_payload(request, e)
            if not e.skip_footprint:
                footprint.leave(
                    log_type="warning",
                    message=e.message,
                    controller=e.controller or controller,
                    subject="Request Error",
                    payload=payload,
                )

            return return_response(
                data=str(e.message),
                status_code=e.status_code,
                response_class=JSONResponse,
            )
        except Exception as e:
            payload = await self.create_payload(request, e)
            try:
                message = str(e)
            except Exception:
                message = "Unrecognized Error has happened."

            footprint.leave(
                log_type="error",
                message=message,
                controller=controller,
                subject="Unrecognized Error",
                payload=payload,
            )

            return return_response(
                data=(
                    "An unexpected issue has occurred; our team has been notified and is working diligently to resolve it promptly."
                    if self.hide_error_messages
                    else message
                ),
                status_code=500,
                response_class=JSONResponse,
            )
        else:
            return response
