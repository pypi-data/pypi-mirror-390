"""Retry utilities for functions with exponential backoff."""

import asyncio
import inspect
import time
from functools import wraps
from typing import Any, Awaitable, Callable, Tuple, Type, TypeVar

from .exception import exception_to_dict
from .jsonable_encoder import jsonable_encoder
from ..log import footprint

__all__ = (
    "retry_async",
    "retry",
    "retry_wrapper",
)

T = TypeVar("T")


async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args: Any,
    sleep_time: int | float = 2,
    max_attempts: int = 3,
    backoff: int | float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_tries: bool = False,
    **kwargs: Any,
) -> T:
    """Retry an async function with exponential backoff.

    Description:
        Executes an async callable with automatic retry logic. On failure,
        waits with exponentially increasing delay before retrying. Logs
        final failures to footprint.

    Args:
        func: The async callable to execute.
        *args: Positional arguments to pass to func.
        sleep_time: Initial delay in seconds between retries.
        max_attempts: Maximum number of attempts before giving up.
        backoff: Multiplier for increasing delay after each retry.
        exceptions: Tuple of exception types to catch and retry.
        log_tries: If True, logs warnings for each retry attempt.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        The result from the successful function execution.

    Raises:
        Exception: The caught exception if all retry attempts fail.
    """
    controller = f"{__name__}.retry_async"
    delay = sleep_time
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            error_dict = exception_to_dict(e)
            error_dict["kwargs"] = jsonable_encoder(kwargs)
            error_dict["args"] = jsonable_encoder(args)
            if attempt == max_attempts:
                footprint.leave(
                    log_type="error",
                    message=f"We could not finish the current job in the function {func.__name__}.",
                    controller=controller,
                    subject=f"Error at {func.__name__}",
                    payload=error_dict,
                )
                raise e
            elif log_tries:
                footprint.leave(
                    log_type="warning",
                    message=f"An error happened while we retry to run {func.__name__} at the {attempt} attempt{'s' if attempt > 1 else ''}.",
                    controller=controller,
                    subject=f"Warning at retrying {func.__name__}",
                    payload=error_dict,
                )
            await asyncio.sleep(delay)
            delay *= backoff
    # This should never be reached, but satisfies type checker
    raise RuntimeError("Retry logic failed unexpectedly")


def retry(
    func: Callable[..., T],
    *args: Any,
    sleep_time: int | float = 2,
    max_attempts: int = 3,
    backoff: int | float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_tries: bool = False,
    **kwargs: Any,
) -> T:
    """Retry a synchronous callable with exponential backoff.

    Description:
        Executes a callable with automatic retry logic. Delegates to
        retry_async if the function is a coroutine. On failure, waits
        with exponentially increasing delay before retrying.

    Args:
        func: The callable to execute.
        *args: Positional arguments to pass to func.
        sleep_time: Initial delay in seconds between retries.
        max_attempts: Maximum number of attempts before giving up.
        backoff: Multiplier for increasing delay after each retry.
        exceptions: Tuple of exception types to catch and retry.
        log_tries: If True, logs warnings for each retry attempt.
        **kwargs: Keyword arguments to pass to func.

    Returns:
        The result from the successful function execution.

    Raises:
        Exception: The caught exception if all retry attempts fail.
    """
    controller = f"{__name__}.retry"
    if inspect.iscoroutinefunction(func):
        return retry_async(  # type: ignore
            func,
            *args,
            sleep_time=sleep_time,
            max_attempts=max_attempts,
            backoff=backoff,
            exceptions=exceptions,
            log_tries=log_tries,
            **kwargs,
        )

    delay = sleep_time
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            error_dict = exception_to_dict(e)
            error_dict["kwargs"] = jsonable_encoder(kwargs)
            error_dict["args"] = jsonable_encoder(args)
            if attempt == max_attempts:
                footprint.leave(
                    log_type="error",
                    message=f"We could not finish the current job in the function {func.__name__}.",
                    controller=controller,
                    subject=f"Error at {func.__name__}",
                    payload=error_dict,
                )
                raise e
            elif log_tries:
                footprint.leave(
                    log_type="warning",
                    message=f"An error happened while we retry to run {func.__name__} at the {attempt} attempt{'s' if attempt > 1 else ''}.",
                    controller=controller,
                    subject=f"Warning at retrying {func.__name__}",
                    payload=error_dict,
                )
            time.sleep(delay)
            delay *= backoff
    # This should never be reached, but satisfies type checker
    raise RuntimeError("Retry logic failed unexpectedly")


def retry_wrapper(
    max_attempts: int = 3,
    sleep_time: int | float = 2,
    backoff: int | float = 2,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_tries: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying functions with exponential backoff.

    Description:
        Returns a decorator that wraps sync or async functions with retry
        logic. Automatically detects if the decorated function is async
        and applies the appropriate retry mechanism.

    Args:
        max_attempts: Maximum number of attempts before giving up.
        sleep_time: Initial delay in seconds between retries.
        backoff: Multiplier for increasing delay after each retry.
        exceptions: Tuple of exception types to catch and retry.
        log_tries: If True, logs warnings for each retry attempt.

    Returns:
        A decorator function that wraps callables with retry logic.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_async(
                func,  # type: ignore
                *args,
                max_attempts=max_attempts,
                sleep_time=sleep_time,
                backoff=backoff,
                exceptions=exceptions,
                log_tries=log_tries,
                **kwargs,
            )

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            return retry(
                func,
                *args,
                max_attempts=max_attempts,
                sleep_time=sleep_time,
                backoff=backoff,
                exceptions=exceptions,
                log_tries=log_tries,
                **kwargs,
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper

    return decorator
