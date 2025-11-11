"""Request timing middleware for measuring response times."""

import time
from typing import Callable

from fastapi import Request, Response

__all__ = ("Timer",)


class Timer:
    """Middleware for tracking request processing time.

    Description:
        Measures the time taken to process each request and adds the duration
        in milliseconds to the response headers as 'X-Process-Time'.
    """

    def __init__(self):
        """Initialize the timer middleware.

        Description:
            Creates a new Timer middleware instance.

        Args:
            None

        Returns:
            None
        """

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Measure processing time and add it to response headers.

        Description:
            Starlette middleware dispatch method that records the start time,
            processes the request, then calculates and adds the elapsed time
            in milliseconds to the response headers.

        Args:
            request: The incoming FastAPI request.
            call_next: The next middleware or route handler in the chain.

        Returns:
            Response: The response with added X-Process-Time header.
        """
        start_time = time.time()
        response = await call_next(request)
        response.headers["X-Process-Time"] = str(
            round((time.time() - start_time) * 1000)
        )
        return response
