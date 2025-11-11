"""Small URL manipulation helpers."""

from typing import Any, Dict
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

__all__ = ("add_query_param",)


def add_query_param(url: str, params: Dict[str, Any]) -> str:
    """Add or update query parameters in a URL.

    This function takes a URL and a dictionary of parameters, then adds the
    parameters to the URL's query string. If a parameter already exists,
    its value is updated.

    Args:
        url: The original URL.
        params: A dictionary of query parameters to add or update.

    Returns:
        The new URL with the updated query parameters.
    """

    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)
    query_params.update(params)
    new_query = urlencode(query_params, doseq=True)
    new_url = urlunparse(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            new_query,
            url_parts.fragment,
        )
    )
    return new_url
