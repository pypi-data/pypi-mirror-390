from dataclasses import dataclass
from enum import Enum
from typing import Any

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader, APIKeyQuery

from ...core.exception import RequestException

__all__ = (
    "AuthType",
    "Auth",
    "auth_data_class_to_dependency",
)


class AuthType(Enum):
    """Authentication transport mechanisms supported by the framework.

    Description:
        Defines how authentication credentials can be transmitted in API requests,
        either via HTTP headers or query parameters.
    """

    HEADER = "header"
    QUERY = "query"


@dataclass
class Auth:
    """Configuration for API route authentication requirements.

    Description:
        Specifies the authentication mechanism, credential location, and expected
        value for validating API requests.
    """

    auth_type: AuthType
    header_key: str | None = None
    real_value: str | None = None


class HeaderAuthChecker:
    """FastAPI dependency that validates authentication via request headers.

    Description:
        Validates that incoming requests contain the correct authentication
        header with the expected value.
    """

    def __init__(self, key: str, real_value: str):
        """Initialize the header authentication checker.

        Description:
            Sets up the authentication checker with the header name and expected value.

        Args:
            key: The name of the HTTP header containing the authentication token.
            real_value: The expected value of the authentication header.

        Returns:
            None
        """
        self.key = key
        self.real_value = real_value

    def __call__(self, request: Request) -> None:
        """Validate that the request contains the correct authentication
        header.

        Description:
            Checks the request headers for the authentication token and validates
            it against the expected value.

        Args:
            request: The incoming FastAPI request.

        Returns:
            None

        Raises:
            RequestException: 403 Forbidden if the header is missing or incorrect.
        """
        controller = f"{__name__}.HeaderAuthChecker.__call__"
        auth_token = request.headers.get(self.key)
        if auth_token is None or auth_token != self.real_value:
            raise RequestException(
                controller=controller,
                message="Wrong credential.",
                status_code=403,
            )


class QueryAuthChecker:
    """FastAPI dependency that validates authentication via query parameters.

    Description:
        Validates that incoming requests contain the correct authentication
        query parameter with the expected value.
    """

    def __init__(self, key: str, real_value: str):
        """Initialize the query parameter authentication checker.

        Description:
            Sets up the authentication checker with the parameter name and expected value.

        Args:
            key: The name of the query parameter containing the authentication token.
            real_value: The expected value of the authentication parameter.

        Returns:
            None
        """
        self.key = key
        self.real_value = real_value

    def __call__(self, request: Request) -> None:
        """Validate that the request contains the correct authentication query
        param.

        Description:
            Checks the request query parameters for the authentication token and
            validates it against the expected value.

        Args:
            request: The incoming FastAPI request.

        Returns:
            None

        Raises:
            RequestException: 403 Forbidden if the parameter is missing or incorrect.
        """
        controller = f"{__name__}.QueryAuthChecker.__call__"
        auth_token = request.query_params.get(self.key)
        if auth_token is None or auth_token != self.real_value:
            raise RequestException(
                controller=controller,
                message="Wrong credential.",
                status_code=403,
            )


def auth_data_class_to_dependency(authentication: Auth) -> list[Any]:
    """Convert an Auth configuration into a list of FastAPI dependencies.

    Behavior
    - For AuthType.HEADER: returns two dependencies:
        1. `Depends(HeaderAuthChecker(...))` — runtime checker that validates the incoming header value.
        2. `Depends(APIKeyHeader(name=...))` — exposes the header in OpenAPI/Swagger (so the docs show the required header).
    - For AuthType.QUERY: returns two dependencies:
        1. `Depends(QueryAuthChecker(...))` — runtime checker that validates the incoming query parameter.
        2. `Depends(APIKeyQuery(name=...))` — exposes the query param in OpenAPI/Swagger.
    - For any other/unsupported auth_type, returns an empty list.

    Parameters
    ----------
    authentication : Auth
        An `Auth` configuration object containing at least:
         - `auth_type` (AuthType) — which transport to use (HEADER or QUERY),
         - `header_key` (str) — the header / query parameter name,
         - `real_value` (str) — the expected secret value used by the checker.

    Returns
    -------
    list[Any]
        A list of FastAPI dependency objects suitable for inclusion in an endpoint signature.
        The pair (checker + APIKey dependency) is intentionally provided so the checker enforces
        runtime validation while the APIKey* dependency registers the parameter in OpenAPI.

    Raises
    ------
    ValueError
        If header_key or real_value is None when auth_type is HEADER or QUERY.
        This ensures authentication misconfiguration (e.g., missing environment variables)
        fails at application startup rather than silently disabling route protection.
    """
    if authentication.auth_type == AuthType.HEADER:
        # Validate that required fields are not None to prevent silent failures
        if authentication.header_key is None or authentication.real_value is None:
            missing = []
            if authentication.header_key is None:
                missing.append("header_key")
            if authentication.real_value is None:
                missing.append("real_value")
            raise ValueError(
                f"Authentication misconfiguration: {', '.join(missing)} cannot be None "
                f"for AuthType.HEADER. This usually indicates a missing environment variable "
                f"or incorrect Auth object initialization. Routes with incomplete authentication "
                f"would be left unprotected."
            )

        header_checker = HeaderAuthChecker(
            key=authentication.header_key, real_value=authentication.real_value
        )
        return [
            Depends(header_checker),
            Depends(
                APIKeyHeader(
                    name=authentication.header_key,
                    description=f"API key header '{authentication.header_key}' required for access.",
                )
            ),
        ]
    elif authentication.auth_type == AuthType.QUERY:
        # Validate that required fields are not None to prevent silent failures
        if authentication.header_key is None or authentication.real_value is None:
            missing = []
            if authentication.header_key is None:
                missing.append("header_key")
            if authentication.real_value is None:
                missing.append("real_value")
            raise ValueError(
                f"Authentication misconfiguration: {', '.join(missing)} cannot be None "
                f"for AuthType.QUERY. This usually indicates a missing environment variable "
                f"or incorrect Auth object initialization. Routes with incomplete authentication "
                f"would be left unprotected."
            )

        query_checker = QueryAuthChecker(
            key=authentication.header_key, real_value=authentication.real_value
        )
        return [
            Depends(query_checker),
            Depends(
                APIKeyQuery(
                    name=authentication.header_key,
                    description=f"API key query parameter '{authentication.header_key}' required for access.",
                )
            ),
        ]

    return []
