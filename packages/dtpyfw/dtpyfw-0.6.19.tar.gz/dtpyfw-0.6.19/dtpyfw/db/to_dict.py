"""Utility for converting SQLAlchemy model instances to dictionaries.

Provides simple conversion from ORM models to dictionary
representations.
"""

from typing import Any

from sqlalchemy import inspect


def to_dict(obj: Any) -> dict[str, Any]:
    """Convert a SQLAlchemy model instance to a dictionary of column values.

    Extracts all mapped column attributes from a SQLAlchemy model instance
    and returns them as a dictionary.

    Args:
        obj: A SQLAlchemy model instance to convert.

    Returns:
        Dictionary mapping column names to their values from the instance.
    """
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
