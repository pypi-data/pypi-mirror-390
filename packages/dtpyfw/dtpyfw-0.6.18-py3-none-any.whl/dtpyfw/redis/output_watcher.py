"""Output watcher utilities for monitoring function outputs via Redis.

This module provides functionality to monitor function outputs by comparing
their hashes with previously stored values in Redis. Useful for detecting
changes in function outputs and triggering webhook events.
"""

import asyncio
from typing import Any, Callable, Tuple

from ..core.hashing import hash_data
from ..core.jsonable_encoder import jsonable_encoder
from .connection import RedisInstance

__all__ = ("watch_output", "awatch_output")


def watch_output(
    redis_instance: RedisInstance,
    func: Callable[..., Any],
    key: str,
    *args: Any,
    **kwargs: Any,
) -> Tuple[bool, Any]:
    """Monitor function output and compare with stored hash in Redis.

    Description:
        Executes a function, encodes its output as JSON, creates a hash of the
        encoded output, and compares it with a previously stored hash in Redis.
        Returns whether the output has changed and the actual output.

    Args:
        redis_instance: RedisInstance for Redis connection management.
        func: The callable function to execute and monitor.
        key: Redis key to store/retrieve the hash for comparison.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        A tuple containing:
            - bool: True if output hash matches stored hash, False if different
            - Any: The actual output of the function

    Example:
        >>> from dtpyfw.redis import RedisConfig, RedisInstance
        >>> config = RedisConfig().set_redis_host("localhost")
        >>> redis_instance = RedisInstance(config)
        >>> 
        >>> def get_user_count():
        ...     return {"count": 42, "timestamp": "2023-11-10"}
        >>> 
        >>> is_same, output = watch_output(
        ...     redis_instance, get_user_count, "user_count_hash"
        ... )
        >>> print(f"Output changed: {not is_same}")
        >>> print(f"Current output: {output}")

    Note:
        This function uses synchronous Redis operations. The output is
        JSON-encoded using jsonable_encoder before hashing to ensure
        consistent serialization of complex data types.
    """
    # Execute the function with provided arguments
    output = func(*args, **kwargs)
    
    # Encode output as JSON-compatible data
    encoded_output = jsonable_encoder(output)
    
    # Create hash of the encoded output
    current_hash = hash_data(encoded_output)
    
    # Get stored hash from Redis
    with redis_instance.get_redis() as redis_client:
        stored_hash = redis_client.get(key)
        
        # Convert bytes to string if hash exists
        if stored_hash is not None:
            stored_hash = stored_hash.decode("utf-8")
        
        # Compare hashes
        is_same = stored_hash == current_hash
        
        # Store current hash for future comparisons
        redis_client.set(key, current_hash)
    
    return is_same, output


async def awatch_output(
    redis_instance: RedisInstance,
    func: Callable[..., Any],
    key: str,
    *args: Any,
    **kwargs: Any,
) -> Tuple[bool, Any]:
    """Asynchronous version of watch_output for monitoring function outputs.

    Description:
        Asynchronously executes a function, encodes its output as JSON, creates
        a hash of the encoded output, and compares it with a previously stored
        hash in Redis. Returns whether the output has changed and the actual output.

    Args:
        redis_instance: RedisInstance for Redis connection management.
        func: The callable function to execute and monitor.
        key: Redis key to store/retrieve the hash for comparison.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        A tuple containing:
            - bool: True if output hash matches stored hash, False if different
            - Any: The actual output of the function

    Example:
        >>> import asyncio
        >>> from dtpyfw.redis import RedisConfig, RedisInstance
        >>> 
        >>> config = RedisConfig().set_redis_host("localhost")
        >>> redis_instance = RedisInstance(config)
        >>> 
        >>> async def get_async_data():
        ...     return {"status": "active", "data": [1, 2, 3]}
        >>> 
        >>> async def monitor_data():
        ...     is_same, output = await awatch_output(
        ...         redis_instance, get_async_data, "async_data_hash"
        ...     )
        ...     return is_same, output
        >>> 
        >>> # Run the async function
        >>> asyncio.run(monitor_data())

    Note:
        This function supports both synchronous and asynchronous callable
        functions. If func is a coroutine function, it will be awaited.
        Uses asynchronous Redis operations for better performance in
        async environments.
    """
    
    # Execute the function with provided arguments
    if asyncio.iscoroutinefunction(func):
        output = await func(*args, **kwargs)
    else:
        output = func(*args, **kwargs)
    
    # Encode output as JSON-compatible data
    encoded_output = jsonable_encoder(output)
    
    # Create hash of the encoded output
    current_hash = hash_data(encoded_output)
    
    # Get stored hash from Redis asynchronously
    async with redis_instance.get_async_redis() as redis_client:
        stored_hash = await redis_client.get(key)
        
        # Convert bytes to string if hash exists
        if stored_hash is not None:
            stored_hash = stored_hash.decode("utf-8")
        
        # Compare hashes
        is_same = stored_hash == current_hash
        
        # Store current hash for future comparisons
        await redis_client.set(key, current_hash)
    
    return is_same, output
