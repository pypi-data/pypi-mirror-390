"""Helpers for bridging async and sync code."""

import asyncio
from typing import Any, Awaitable

__all__ = ("async_to_sync",)


def async_to_sync(awaitable: Awaitable) -> Any:
    """Execute an awaitable in a new event loop and return its result.

    Description:
        Runs an async coroutine or awaitable object in a synchronous context
        by using the current event loop to execute it to completion.

    Args:
        awaitable: An awaitable object (coroutine, task, or future) to execute.

    Returns:
        The result returned by the awaitable after it completes execution.
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(awaitable)
