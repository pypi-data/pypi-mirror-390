"""Utility helpers for safe attribute/function access."""

from typing import Any, Callable

__all__ = (
    "safe_access",
    "convert_to_int_or_float",
)


def safe_access(func: Callable, default_value: Any = None) -> Any:
    """Execute a function and return a default value if it raises an error.

    Description:
        Provides safe execution of a callable, catching all exceptions
        and returning a default value instead of propagating errors.
        Useful for optional operations or fallback scenarios.

    Args:
        func: A callable to execute with no arguments.
        default_value: Value to return if func raises any exception. Defaults to None.

    Returns:
        The result of func() if successful, otherwise default_value.
    """
    try:
        return func()
    except Exception:
        return default_value


def convert_to_int_or_float(string_num: str) -> int | float | None:
    """Convert a string to int or float if possible, otherwise None.

    Description:
        Attempts to parse a string as a number. Returns an int if the
        value is a whole number, float if it has a decimal component,
        or None if parsing fails.

    Args:
        string_num: The string representation of a number to convert.

    Returns:
        An int if the number is whole, a float if it has decimals, or None if invalid.
    """
    try:
        float_num = float(string_num)
        if float_num.is_integer():
            return int(float_num)
        else:
            return float_num
    except ValueError:
        return None
