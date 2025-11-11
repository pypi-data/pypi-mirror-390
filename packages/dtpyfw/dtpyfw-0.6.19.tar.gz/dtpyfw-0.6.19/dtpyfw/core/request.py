"""HTTP request utilities with error handling and logging."""

from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests

from .exception import RequestException, exception_to_dict
from .jsonable_encoder import jsonable_encoder
from ..log import footprint

__all__ = ("request",)


def request(
    method: str,
    path: str,
    host: Optional[str] = None,
    auth_key: Optional[str] = None,
    auth_value: Optional[str] = None,
    auth_type: Optional[str] = None,
    disable_caching: bool = True,
    full_return: bool = False,
    json_return: bool = True,
    internal_service: bool = True,
    add_dt_user_agent: bool = True,
    push_logs: bool = True,
    **kwargs: Any,
) -> Union[requests.Response, Any, str, None]:
    """Send an HTTP request with standardized headers, authentication, and
    error handling.

    Description:
        Makes HTTP requests with configurable authentication, caching headers,
        and response handling. Supports internal service response format with
        'success' and 'data' fields. Automatically logs errors to footprint.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.).
        path: Endpoint path relative to host.
        host: Base URL of the service. Returns None if not provided.
        auth_key: Key for authentication header or parameter.
        auth_value: Value for authentication.
        auth_type: Where to place auth - 'headers' or 'params'.
        disable_caching: If True, sets no-cache headers.
        full_return: If True, returns the raw Response object.
        json_return: If True, attempts to parse JSON response.
        internal_service: If True, expects response format with 'success' and 'data'.
        add_dt_user_agent: If True, includes DealerTower user-agent header.
        push_logs: If True, sends errors to footprint logging system.
        **kwargs: Additional arguments passed directly to requests.request().

    Returns:
        Depending on flags: Response object, parsed JSON data, text, or None.

    Raises:
        RequestException: On network errors, JSON parsing failures, or service errors.
    """
    controller = f"{__name__}.request"
    if not host:
        return None

    url = urljoin(host.rstrip("/") + "/", path.lstrip("/"))
    headers: Dict[str, Any] = {}
    params: Dict[str, Any] = {}

    # Merge user-provided headers & params
    if "headers" in kwargs:
        headers.update(jsonable_encoder(kwargs.pop("headers", {}) or {}))
    if "params" in kwargs:
        params.update(kwargs.pop("params", {}) or {})

    # Authentication
    if auth_key and auth_value and auth_type in ("headers", "params"):
        target = headers if auth_type == "headers" else params
        target[auth_key] = auth_value

    # Disable caching headers
    if disable_caching:
        headers.update(
            {
                "Cache-Control": "private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )

    # Add default user-agent
    if add_dt_user_agent:
        headers.setdefault("User-Agent", "DealerTower-Service/1.0")

    # Prepare footprint context
    error_context: Dict[str, Any] = {
        "subject": "Error sending request",
        "controller": controller,
        "payload": {
            "method": method,
            "url": url,
            "disable_caching": disable_caching,
            "json_return": json_return,
            "internal_service": internal_service,
        },
    }

    try:
        resp = requests.request(method, url, headers=headers, params=params, **kwargs)
        status = resp.status_code
    except Exception as exc:
        if push_logs:
            error_context["payload"]["error"] = exception_to_dict(exc)
            footprint.leave(**error_context, log_type="error", message="Request failed")
        raise RequestException(
            status_code=500,
            controller="dtpyfw.core.request",
            message="Request sending error",
        )

    if full_return:
        return resp

    if not json_return:
        return resp.text

    # Parse JSON
    try:
        body = resp.json()
    except Exception as exc:
        if push_logs:
            error_context["payload"].update(
                {
                    "error": exception_to_dict(exc),
                    "headers": dict(resp.headers),
                    "text": resp.text,
                }
            )
            footprint.leave(
                **error_context, log_type="error", message="Invalid JSON response"
            )
        raise RequestException(
            status_code=500,
            controller="dtpyfw.core.request",
            message="Response parsing error",
        )

    # Handle internal service wrapper
    if internal_service:
        success = isinstance(body, dict) and body.get("success", False)
        if success:
            return body.get("data")
        else:
            if push_logs:
                error_context["payload"].update(
                    {
                        "status_code": status,
                        "response": body,
                    }
                )
                footprint.leave(
                    **error_context,
                    log_type="error",
                    message="Service reported failure",
                )
            raise RequestException(
                status_code=status,
                message=str(body.get("message", "")),
                controller="dtpyfw.core.request",
            )

    return body
