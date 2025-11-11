"""Validation utilities for common data types and formats."""

import re
from typing import Union
from urllib.parse import urlparse
from uuid import UUID

__all__ = (
    "is_email",
    "is_vin",
    "is_year",
    "is_uuid",
    "is_valid_http_url",
)


def is_email(email: str) -> bool:
    """Check if a string is a valid email address.

    Description:
        Validates email format using a regular expression pattern that checks
        for basic email structure with username, @ symbol, domain, and TLD.

    Args:
        email: The string to validate.

    Returns:
        True if the string is a valid email address, False otherwise.
    """
    return (
        True
        if re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email)
        else False
    )


def is_vin(vin: str) -> bool:
    """Validate a Vehicle Identification Number (VIN).

    Description:
        Checks if a string matches the standard 17-character VIN format
        using alphanumeric characters excluding I, O, and Q to avoid
        confusion with numbers.

    Args:
        vin: The VIN string to validate.

    Returns:
        True if the VIN is valid (17 characters, alphanumeric excluding I/O/Q), False otherwise.
    """
    vin_pattern = "[A-HJ-NPR-Z0-9]{17}"
    return bool(re.match(vin_pattern, vin))


def is_year(s: str) -> bool:
    """Check if a string represents a valid four-digit year.

    Description:
        Validates that the string is exactly 4 digits and represents a
        positive year value (greater than 0).

    Args:
        s: The string to check.

    Returns:
        True if the string is a valid year (4 digits, positive integer), False otherwise.
    """
    if len(s) != 4:
        return False
    try:
        year = int(s)
        if year < 1:
            return False
    except ValueError:
        return False
    return True


def is_uuid(uuid_to_test: Union[str, UUID], version: int = 4) -> bool:
    """Validate if a string is a valid UUID of a specified version.

    Description:
        Checks if the input is a UUID object or a valid UUID string
        matching the specified version (default: version 4).

    Args:
        uuid_to_test: The string or UUID object to test.
        version: The UUID version to validate against (1-5). Defaults to 4.

    Returns:
        True if the input is a valid UUID of the specified version, False otherwise.
    """
    if isinstance(uuid_to_test, UUID):
        return True

    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except (ValueError, AttributeError):
        return False
    return str(uuid_obj) == uuid_to_test


def is_valid_http_url(url: str) -> bool:
    """Check if a string is a valid HTTP or HTTPS URL.

    Description:
        Validates that a URL has a valid structure with http/https scheme
        and a non-empty network location (domain).

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is valid (http/https with domain), False otherwise.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False
