"""Response helper functions for FastAPI routes."""

from typing import Any, Dict, Optional, Type

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

__all__ = (
    "return_response",
    "return_json_response",
)


def return_response(
    data: Any,
    status_code: int,
    response_class: Type[Response],
    return_json_directly: bool = False,
    headers: Optional[Dict[int, Dict[Any, Any]]] = None,
    no_cache: bool = True,
) -> Response:
    """Build a FastAPI response with standard success/error wrapping.

    Description:
        Creates a standardized response object with optional success/error wrapping,
        cache control headers, and custom headers based on status code.

    Args:
        data: The response payload (can be Pydantic model, dict, list, or primitive).
        status_code: HTTP status code for the response.
        response_class: The Response class to use (e.g., JSONResponse, HTMLResponse).
        return_json_directly: If True, skips success/error wrapping and returns data as-is.
        headers: Optional dict mapping status codes to header dictionaries.
        no_cache: If True, adds cache-control headers to prevent caching.

    Returns:
        Response: Configured response object ready to be returned from an endpoint.
    """
    if headers is None:
        headers = {}

    final_headers = headers.get(status_code) or {}

    if no_cache:
        final_headers.update(
            {
                "Cache-Control": "private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

    if response_class != JSONResponse:
        return_json_directly = True

    if isinstance(data, BaseModel):
        final_data = data.model_dump(by_alias=True)
    else:
        final_data = data

    if return_json_directly:
        content = data
    else:
        if status_code < 300:
            content = {"success": True, "data": jsonable_encoder(final_data)}
        else:
            content = {"success": False, "message": data}

    return response_class(
        status_code=status_code, content=content, headers=final_headers
    )


def return_json_response(
    data: Any,
    status_code: int,
    return_json_directly: bool = False,
    headers: Optional[Dict[int, Dict[Any, Any]]] = None,
    no_cache: bool = True,
) -> Response:
    """Convenience wrapper for return_response using JSONResponse.

    Description:
        Simplified version of return_response that always returns JSON responses,
        reducing boilerplate in route handlers.

    Args:
        data: The response payload (can be Pydantic model, dict, list, or primitive).
        status_code: HTTP status code for the response.
        return_json_directly: If True, skips success/error wrapping and returns data as-is.
        headers: Optional dict mapping status codes to header dictionaries.
        no_cache: If True, adds cache-control headers to prevent caching.

    Returns:
        Response: JSON response object ready to be returned from an endpoint.
    """
    return return_response(
        data=data,
        status_code=status_code,
        return_json_directly=return_json_directly,
        headers=headers,
        no_cache=no_cache,
        response_class=JSONResponse,
    )
