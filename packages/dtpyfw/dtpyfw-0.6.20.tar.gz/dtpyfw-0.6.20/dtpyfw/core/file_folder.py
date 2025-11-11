"""Small file and directory utilities.

This module provides simple helper functions for common file system
operations such as creating directories and removing files.
"""

import os

__all__ = (
    "make_directory",
    "folder_path_of_file",
    "remove_file",
)


def make_directory(path: str) -> None:
    """Create a directory if it does not already exist.

    Description:
        Creates the directory specified by path, including any necessary
        parent directories. If the directory already exists, no action
        is taken.

    Args:
        path: The directory path to create.

    Returns:
        None
    """
    if not os.path.exists(path):
        os.makedirs(path)


def folder_path_of_file(path: str) -> str:
    """Return the directory portion of a file path.

    Description:
        Extracts and returns the directory component from a file path,
        resolving it to an absolute path.

    Args:
        path: The file path to extract the directory from.

    Returns:
        The absolute directory path containing the file.
    """
    return os.path.dirname(os.path.realpath(path))


def remove_file(path: str) -> None:
    """Delete a file if it exists.

    Description:
        Removes the file at the specified path. If the file does not
        exist, no action is taken and no error is raised.

    Args:
        path: The file path to remove.

    Returns:
        None
    """
    if os.path.exists(path):
        os.remove(path)
