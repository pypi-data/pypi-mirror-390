"""Wrapper around :func:`json.dumps` that forces serialization of unknown
types.

This module provides utilities to ensure data can be safely JSON-encoded
by converting it through a JSON round-trip with string fallbacks.
"""

import json
from typing import Any

__all__ = ("jsonable_encoder",)


def jsonable_encoder(data: Any) -> Any:
    """Return data encoded to JSON and back to ensure primitives only.

    Description:
        Converts the input data to JSON format and then parses it back,
        ensuring all values are JSON-compatible primitives. Non-serializable
        types are converted to strings.

    Args:
        data: The data to encode, can be any type.

    Returns:
        The data with all values converted to JSON-compatible primitives.
    """
    return json.loads(json.dumps(data, default=str))
