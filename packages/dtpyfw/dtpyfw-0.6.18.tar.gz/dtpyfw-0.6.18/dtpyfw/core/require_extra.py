"""Utility to assert optional dependencies are installed."""

from importlib.util import find_spec

__all__ = ("require_extra",)


def require_extra(extra_name: str, *modules: str) -> None:
    """Raise RuntimeError if any of the specified modules cannot be imported.

    Description:
        Validates that optional dependencies are installed. Used to enforce
        that extras specified in pyproject.toml are available before using
        features that depend on them.

    Args:
        extra_name: Name of the extra group (e.g., 'bucket', 'redis').
        *modules: Module names to check for availability.

    Returns:
        None

    Raises:
        RuntimeError: If any module cannot be imported, with installation instructions.
    """
    for mod in modules:
        if find_spec(mod) is None:
            raise RuntimeError(
                f"Missing optional dependency `{mod}`. "
                f"Install with `pip install dtpyfw[{extra_name}]`."
            )
