"""Utilities for splitting lists into smaller chunks.

This module provides functions to divide lists into manageable chunks
for batch processing or pagination purposes.
"""

from typing import Any, Generator, List

__all__ = (
    "chunk_list",
    "chunk_list_generator",
)


def chunk_list(lst: List[Any], chunk_size: int) -> List[Any]:
    """Split a list into chunks of a specified size.

    Description:
        Divides a list into smaller sublists, each with a maximum size
        specified by chunk_size. The last chunk may be smaller if the list
        length is not evenly divisible by chunk_size.

    Args:
        lst: The list to split into chunks.
        chunk_size: The maximum number of elements in each chunk.

    Returns:
        A list of chunks, where each chunk is itself a list.
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def chunk_list_generator(
    lst: List[Any], chunk_size: int
) -> Generator[List[Any], None, None]:
    """Generate chunks of a specified size from a list.

    Description:
        Yields successive chunks from the input list without creating all
        chunks in memory at once. Useful for processing large lists with
        limited memory.

    Args:
        lst: The list to split into chunks.
        chunk_size: The maximum number of elements in each chunk.

    Yields:
        Lists containing up to chunk_size elements from the original list.
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]
