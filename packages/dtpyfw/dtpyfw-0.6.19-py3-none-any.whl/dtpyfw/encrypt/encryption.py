"""JWT token encryption and decryption utilities.

This module provides functions for creating and validating JWT (JSON Web Tokens)
using configurable encryption algorithms and secret keys. It supports custom
claims, expiration handling, and subject validation.

Common encryption algorithms include:
    - HS256: HMAC using SHA-256
    - HS384: HMAC using SHA-384
    - HS512: HMAC using SHA-512
    - RS256: RSA signature with SHA-256
    - RS384: RSA signature with SHA-384
    - RS512: RSA signature with SHA-512
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import jwt

from ..core.jsonable_encoder import jsonable_encoder

__all__ = (
    "jwt_encrypt",
    "jwt_decrypt",
)


def jwt_encrypt(
    tokens_secret_key: str,
    encryption_algorithm: str,
    subject: str,
    claims: Dict[str, Any],
    expiration_timedelta: Optional[timedelta] = None,
) -> str:
    """Create a JWT token with the given subject, claims, and expiration.

    Encodes a JSON Web Token containing the specified subject and additional
    claims using the provided secret key and encryption algorithm. Optionally
    sets an expiration time for the token.

    Args:
        tokens_secret_key: The secret key used for signing the JWT token.
            Must be kept secure and match the key used for decryption.
        encryption_algorithm: The cryptographic algorithm to use for signing
            (e.g., 'HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512').
        subject: The subject identifier to embed in the token. This represents
            the principal (user, service, etc.) the token is issued for.
        claims: Dictionary of additional claims to include in the token payload.
            These can be standard JWT claims (iss, aud, etc.) or custom claims.
        expiration_timedelta: Optional duration after which the token expires.
            If None, the token has no expiration time set.

    Returns:
        str: The encoded JWT token as a compact, URL-safe string consisting
            of three base64-encoded parts separated by dots (header.payload.signature).

    Example:
        >>> from datetime import timedelta
        >>> token = jwt_encrypt(
        ...     tokens_secret_key="my-secret-key",
        ...     encryption_algorithm="HS256",
        ...     subject="user123",
        ...     claims={"role": "admin", "email": "user@example.com"},
        ...     expiration_timedelta=timedelta(hours=1)
        ... )
    """
    data: Dict[str, Any] = {
        "subject": subject,
    }
    if expiration_timedelta:
        data["exp"] = (datetime.now() + expiration_timedelta).timestamp()

    data.update(claims)
    return jwt.encode(
        claims=jsonable_encoder(data),
        key=tokens_secret_key,
        algorithm=encryption_algorithm,
    )


def jwt_decrypt(
    tokens_secret_key: str,
    encryption_algorithm: str,
    token: str,
    subject: str,
    check_exp: bool = True,
) -> Dict[str, Any]:
    """Decrypt and validate a JWT token.

    Decodes a JSON Web Token and validates its signature, expiration time
    (if enabled), and subject claim. Ensures the token was issued for the
    expected subject and has not expired.

    Args:
        tokens_secret_key: The secret key used for verifying the token signature.
            Must match the key used during token creation.
        encryption_algorithm: The cryptographic algorithm used to sign the token
            (e.g., 'HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512').
            Must match the algorithm used during token creation.
        token: The JWT token string to decrypt and validate. Should be in the
            format header.payload.signature.
        subject: The expected subject identifier that must match the token's
            subject claim. Used for additional validation.
        check_exp: Whether to validate the token's expiration time. When True,
            requires the 'exp' claim and validates it hasn't passed. Defaults to True.

    Returns:
        Dict[str, Any]: The decoded token payload containing all claims as a dictionary.
            Always includes the 'subject' claim and may include 'exp', custom claims,
            and any other data embedded during token creation.

    Raises:
        Exception: If the token's subject claim does not match the expected subject value.
            The exception message will be "wrong_token_subject".
        JWTError: If the token signature is invalid, the token is malformed,
            or decoding fails for any other reason.
        ExpiredSignatureError: If check_exp is True and the token has expired
            (current time is past the 'exp' claim).

    Example:
        >>> try:
        ...     payload = jwt_decrypt(
        ...         tokens_secret_key="my-secret-key",
        ...         encryption_algorithm="HS256",
        ...         token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        ...         subject="user123",
        ...         check_exp=True
        ...     )
        ...     print(payload)
        ... except ExpiredSignatureError:
        ...     print("Token has expired")
        ... except Exception as e:
        ...     print(f"Token validation failed: {e}")
    """
    options: Dict[str, bool] = {}
    if check_exp:
        options["require_exp"] = True
        options["verify_exp"] = True
    else:
        options["require_exp"] = False
        options["verify_exp"] = False

    decoded_token: Dict[str, Any] = jwt.decode(
        token=token,
        key=tokens_secret_key,
        algorithms=encryption_algorithm,
        options=options if options else None,
    )

    if decoded_token.get("subject") != subject:
        raise Exception("wrong_token_subject")

    return decoded_token
