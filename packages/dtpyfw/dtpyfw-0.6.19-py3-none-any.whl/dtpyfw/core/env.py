"""Utility helpers for interacting with environment variables."""

import os
from functools import lru_cache
from typing import Any, List, Set

from ..log import footprint

__all__ = ("Env",)


class Env:
    """Lightweight wrapper around ``os.environ`` with allow-list support.

    Description:
        Provides controlled access to environment variables with an allow-list
        mechanism. Only variables explicitly registered can be loaded from files
        or accessed via the get method.
    """

    _allowed_variables: Set[str] = set()

    @staticmethod
    def load_file(
        file_path: str, override: bool = False, fail_on_missing: bool = False
    ) -> None:
        """Load key/value pairs from a ``.env`` style file.

        Description:
            Reads environment variables from a file and loads them into os.environ.
            Only variables that have been registered via register() are loaded.
            Lines without '=' are ignored.

        Args:
            file_path: Path to the file containing environment variables.
            override: When True, existing environment variables will be overwritten.
            fail_on_missing: If True, raises FileNotFoundError when the file is missing.

        Returns:
            None

        Raises:
            FileNotFoundError: If fail_on_missing is True and the file doesn't exist.
        """
        controller = f"{__name__}.Env.load_file"
        if not os.path.exists(file_path):
            if fail_on_missing:
                raise FileNotFoundError(f"The file {file_path} does not exist.")

            return

        with open(file_path, "r") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    key = key.strip().upper()
                    value = value.strip()
                    if key in Env._allowed_variables:
                        if override or key not in os.environ:
                            os.environ[key] = value
                    else:
                        footprint.leave(
                            log_type="warning",
                            message=f"Skipping unallowed environment variable {key}.",
                            controller=controller,
                            subject="Unallowed Environment Variable",
                        )

    @staticmethod
    def register(variables: List[str] | Set[str]) -> None:
        """Register environment variable names that are allowed to be loaded.

        Description:
            Adds variable names to the internal allow-list. Only registered
            variables can be loaded from files via load_file(). Variable names
            are automatically converted to uppercase.

        Args:
            variables: A list or set of environment variable names to register.

        Returns:
            None
        """
        Env._allowed_variables.update([item.upper() for item in variables])

    @staticmethod
    @lru_cache(maxsize=128)
    def get(key: str, default: Any = None) -> Any:
        """Retrieve a variable from ``os.environ`` with optional default.

        Description:
            Gets an environment variable value. The key is automatically
            converted to uppercase. Returns the default if the variable
            is not set. Results are cached for performance.

        Args:
            key: The environment variable name to retrieve.
            default: Value to return if the variable is not set. Defaults to None.

        Returns:
            The value of the environment variable, or the default value if not found.
        """
        return os.getenv(key.upper()) or default
