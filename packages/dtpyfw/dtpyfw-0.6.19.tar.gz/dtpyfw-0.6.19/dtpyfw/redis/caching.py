"""Redis caching utilities for function memoization and data caching.

This module provides decorators and functions for caching function results and data
in Redis with support for both synchronous and asynchronous operations. Features include:
    - Automatic cache key generation from function arguments
    - Configurable expiration times
    - Conditional caching based on argument values
    - Compression using zlib for efficient storage
    - Error handling with logging integration
"""

import asyncio
import hashlib
import inspect
import json
import zlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set

from redis import Redis

from ..core.exception import exception_to_dict
from ..core.jsonable_encoder import jsonable_encoder
from ..log import footprint
from .connection import RedisInstance

__all__ = (
    "cache_data",
    "cache_function",
    "cache_wrapper",
)


def cache_data(
    response: Dict[str, Any],
    cache_key: str,
    redis_instance: Redis,
    expire: Optional[int] = None,
) -> Dict[str, Any]:
    """Cache a dictionary in Redis with optional compression and expiration.

    Compresses the response dictionary using zlib and stores it in Redis
    under the specified key. Handles serialization via jsonable_encoder
    to ensure compatibility with non-JSON-native types.

    Args:
        response: The dictionary data to cache.
        cache_key: The Redis key under which to store the data.
        redis_instance: An active Redis client instance for cache operations.
        expire: Optional expiration time in seconds. If None, the key persists indefinitely.

    Returns:
        Dict[str, Any]: The original response dictionary, unchanged.

    Example:
        >>> redis_client = Redis()
        >>> data = {"user_id": 123, "name": "John"}
        >>> cached_data = cache_data(data, "user:123", redis_client, expire=3600)
    """
    controller = f"{__name__}.cache_data"
    try:
        compressed_main_value = zlib.compress(
            json.dumps(jsonable_encoder(response)).encode("utf-8")
        )
        redis_instance.delete(cache_key)
        if expire:
            redis_instance.setex(
                name=cache_key, value=compressed_main_value, time=expire
            )
        else:
            redis_instance.set(name=cache_key, value=compressed_main_value)

    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="We faced an error while we want to cache data.",
            controller=controller,
            subject="Error on caching data",
            payload={
                "expire": expire,
                "cache_key": cache_key,
                "error": exception_to_dict(exception),
            },
        )

    return response


def _cache_key_generator(
    namespace: str,
    args: tuple,
    kwargs: Dict[str, Any],
    skip_cache_keys: Set[str],
) -> str:
    """Generate a unique cache key from function namespace and arguments.

    Creates a deterministic cache key by hashing function arguments,
    excluding specified keyword arguments that should not affect caching.
    Uses SHA-256 hashing to ensure consistent key generation.

    Args:
        namespace: A prefix string to namespace the cache key.
        args: Positional arguments passed to the cached function.
        kwargs: Keyword arguments passed to the cached function.
        skip_cache_keys: Set of keyword argument names to exclude from key generation.

    Returns:
        A unique string suitable for use as a Redis cache key.
    """
    kwargs_key = {k: v for k, v in kwargs.items() if k not in skip_cache_keys}
    cache_key = ""
    if namespace:
        cache_key += f"{namespace}:"
    if args:
        args_hash = hashlib.sha256(
            json.dumps(args, default=str).encode("utf-8")
        ).hexdigest()
        cache_key += f"{args_hash}:"
    if kwargs_key:
        kwargs_hash = hashlib.sha256(
            json.dumps(kwargs_key, default=str).encode("utf-8")
        ).hexdigest()
        cache_key += f"{kwargs_hash}:"

    return cache_key.rstrip(":")


def _should_cache(
    cache_only_for: List[Dict[str, Any]] | None, kwargs: Dict[str, Any]
) -> bool:
    """Determine whether a function call should be cached based on conditions.

    Evaluates caching conditions against function keyword arguments.
    If no conditions are specified, caching is always enabled.

    Args:
        cache_only_for: List of condition dictionaries specifying when to cache.
            Each dict should contain 'kwarg', 'operator', and 'value' keys.
            If None, caching is always enabled.
        kwargs: Keyword arguments from the function call to evaluate.

    Returns:
        True if the function result should be cached, False otherwise.
    """
    if cache_only_for is None:
        return True
    for cond in cache_only_for:
        col = cond.get("kwarg")
        condition_value = cond.get("value")
        if (
            cond.get("operator") == "in" 
            and col is not None 
            and condition_value is not None
            and kwargs.get(col) in condition_value
        ):
            return True
    return False


def _decode_cached_value(cache_compressed: bytes, controller: str) -> Optional[Any]:
    """Decompress and deserialize a cached value from Redis.

    Decompresses zlib-compressed data and deserializes it from JSON.
    Logs errors if decompression or deserialization fails.

    Args:
        cache_compressed: The compressed bytes retrieved from Redis.
        controller: The name of the calling function for error logging.

    Returns:
        Optional[Any]: The deserialized Python object, or None if an error occurs.
    """
    try:
        return json.loads(zlib.decompress(cache_compressed).decode("utf-8"))
    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="Error during decompressing or loading cached data.",
            controller=controller,
            subject="Error on reading cache",
            payload={"error": exception_to_dict(exception)},
        )
        return None


def _encode_result(result: Any) -> bytes:
    """Encode and compress a result value for Redis storage.

    Serializes the result using jsonable_encoder and compresses it with zlib.

    Args:
        result: The value to encode and compress.

    Returns:
        Compressed bytes suitable for Redis storage.
    """
    return zlib.compress(json.dumps(jsonable_encoder(result)).encode("utf-8"))


def _redis_get_sync(redis_client: Redis, key: str, controller: str) -> Optional[bytes]:
    """Retrieve a value from Redis synchronously with error handling.

    Attempts to fetch a value from Redis and logs any errors encountered.

    Args:
        redis_client: The Redis client instance.
        key: The Redis key to retrieve.
        controller: The name of the calling function for error logging.

    Returns:
        Optional[bytes]: The cached bytes value if found, or None if an error occurs.
    """
    try:
        result = redis_client.get(key)
        return result if isinstance(result, (bytes, type(None))) else None
    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="Error while trying to retrieve data from cache.",
            controller=controller,
            subject="Error on get cached data",
            payload={"redis_key": key, "error": exception_to_dict(exception)},
        )
        return None


async def _redis_get_async(
    redis_client: Redis, key: str, controller: str
) -> Optional[bytes]:
    """Retrieve a value from Redis asynchronously with error handling.

    Offloads Redis get operation to a thread to avoid blocking the async event loop.
    Logs any errors encountered during retrieval.

    Args:
        redis_client: The Redis client instance.
        key: The Redis key to retrieve.
        controller: The name of the calling function for error logging.

    Returns:
        Optional[bytes]: The cached bytes value if found, or None if an error occurs.
    """
    try:
        result = await asyncio.to_thread(redis_client.get, key)
        return result if isinstance(result, (bytes, type(None))) else None
    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="Error while trying to retrieve data from cache.",
            controller=controller,
            subject="Error on get cached data",
            payload={"redis_key": key, "error": exception_to_dict(exception)},
        )
        return None


def _redis_write_sync(
    redis_client: Redis,
    key: str,
    value: bytes,
    expire: Optional[int],
    controller: str,
) -> None:
    """Write a value to Redis synchronously with error handling.

    Deletes any existing value at the key before writing the new value.
    Supports optional expiration time.

    Args:
        redis_client: The Redis client instance.
        key: The Redis key to write to.
        value: The compressed bytes to store.
        expire: Optional expiration time in seconds. If None, key persists indefinitely.
        controller: The name of the calling function for error logging.
    """
    try:
        redis_client.delete(key)
        if expire:
            redis_client.setex(name=key, time=expire, value=value)
        else:
            redis_client.set(name=key, value=value)
    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="Error occurred while caching the result.",
            controller=controller,
            subject="Error on writing cache",
            payload={"redis_key": key, "error": exception_to_dict(exception)},
        )


async def _redis_write_async(
    redis_client: Redis,
    key: str,
    value: bytes,
    expire: Optional[int],
    controller: str,
) -> None:
    """Write a value to Redis asynchronously with error handling.

    Offloads Redis operations to a thread to avoid blocking the async event loop.
    Deletes any existing value at the key before writing the new value.

    Args:
        redis_client: The Redis client instance.
        key: The Redis key to write to.
        value: The compressed bytes to store.
        expire: Optional expiration time in seconds. If None, key persists indefinitely.
        controller: The name of the calling function for error logging.
    """
    try:
        await asyncio.to_thread(redis_client.delete, key)
        if expire:
            # redis-py setex signature: setex(name, time, value)
            await asyncio.to_thread(redis_client.setex, key, expire, value)
        else:
            await asyncio.to_thread(redis_client.set, key, value)
    except Exception as exception:
        footprint.leave(
            log_type="error",
            message="Error occurred while caching the result.",
            controller=controller,
            subject="Error on writing cache",
            payload={"redis_key": key, "error": exception_to_dict(exception)},
        )


def cache_function(
    func: Callable[..., Any],
    redis: RedisInstance,
    namespace: str,
    expire: Optional[int] = None,
    cache_only_for: Optional[List[Dict[str, Any]]] = None,
    skip_cache_keys: Optional[Set[str]] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Execute a synchronous function with Redis caching support.

    Checks Redis for a cached result before executing the function.
    If no cache exists, executes the function and stores the result.
    Uses synchronous Redis I/O operations.

    Args:
        func: The synchronous function to execute and cache.
        redis: RedisInstance providing Redis connectivity.
        namespace: Cache key namespace prefix.
        expire: Optional cache expiration time in seconds.
        cache_only_for: Optional conditions determining when to cache.
            Each condition dict should have 'kwarg', 'operator', and 'value' keys.
        skip_cache_keys: Optional set of kwarg names to exclude from cache key.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The function's return value, either from cache or fresh execution.

    Example:
        >>> def expensive_operation(x, y):
        ...     return x * y
        >>> result = cache_function(
        ...     func=expensive_operation,
        ...     redis=redis_instance,
        ...     namespace="math:multiply",
        ...     expire=3600,
        ...     args=(5, 10)
        ... )
    """
    controller = f"{__name__}.cache_function"
    if skip_cache_keys is None:
        skip_cache_keys = set()

    if not _should_cache(cache_only_for, kwargs):
        return func(*args, **kwargs)

    cache_key = _cache_key_generator(namespace, args, kwargs, skip_cache_keys)

    with redis.get_redis_client() as redis_instance:
        cache_compressed = _redis_get_sync(redis_instance, cache_key, controller)
        if cache_compressed:
            cached = _decode_cached_value(cache_compressed, controller)
            if cached is not None:
                return cached

        # Miss → compute
        result = func(*args, **kwargs)

        # Write
        _redis_write_sync(
            redis_instance,
            cache_key,
            _encode_result(result),
            expire,
            controller,
        )
        return result


async def acache_function(
    func: Callable[..., Any],
    redis: RedisInstance,
    namespace: str,
    expire: Optional[int] = None,
    cache_only_for: Optional[List[Dict[str, Any]]] = None,
    skip_cache_keys: Optional[Set[str]] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Execute a function asynchronously with Redis caching support.

    Checks Redis for a cached result before executing the function.
    If no cache exists, executes the function and stores the result.
    Redis operations are offloaded to threads to avoid blocking async event loop.
    Supports both sync and async functions.

    Args:
        func: The function (sync or async) to execute and cache.
        redis: RedisInstance providing Redis connectivity.
        namespace: Cache key namespace prefix.
        expire: Optional cache expiration time in seconds.
        cache_only_for: Optional conditions determining when to cache.
            Each condition dict should have 'kwarg', 'operator', and 'value' keys.
        skip_cache_keys: Optional set of kwarg names to exclude from cache key.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The function's return value, either from cache or fresh execution.

    Example:
        >>> async def async_operation(user_id):
        ...     return await fetch_user_data(user_id)
        >>> result = await acache_function(
        ...     func=async_operation,
        ...     redis=redis_instance,
        ...     namespace="user:data",
        ...     expire=1800,
        ...     user_id=123
        ... )
    """
    controller = f"{__name__}.acache_function"
    if skip_cache_keys is None:
        skip_cache_keys = set()

    if not _should_cache(cache_only_for, kwargs):
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    cache_key = _cache_key_generator(namespace, args, kwargs, skip_cache_keys)

    with redis.get_redis_client() as redis_instance:
        cache_compressed = await _redis_get_async(redis_instance, cache_key, controller)
        if cache_compressed:
            cached = _decode_cached_value(cache_compressed, controller)
            if cached is not None:
                return cached

        # Miss → compute
        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            result = func(*args, **kwargs)

        # Write
        await _redis_write_async(
            redis_instance,
            cache_key,
            _encode_result(result),
            expire,
            controller,
        )
        return result


def cache_wrapper(
    redis: RedisInstance,
    namespace: str,
    expire: Optional[int] = None,
    cache_only_for: Optional[List[Dict[str, Any]]] = None,
    skip_cache_keys: Optional[Set[str]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Create a decorator that adds Redis caching to a function.

    Returns a decorator that automatically selects synchronous or asynchronous
    caching based on whether the decorated function is a coroutine.
    The decorator checks Redis before executing the function and caches results.

    Args:
        redis: RedisInstance providing Redis connectivity.
        namespace: Cache key namespace prefix for all cached calls.
        expire: Optional cache expiration time in seconds.
        cache_only_for: Optional conditions determining when to cache results.
            Each condition dict should have 'kwarg', 'operator', and 'value' keys.
        skip_cache_keys: Optional set of kwarg names to exclude from cache key generation.

    Returns:
        Callable: A decorator function that wraps the target function with caching logic.

    Example:
        >>> @cache_wrapper(
        ...     redis=redis_instance,
        ...     namespace="user_data",
        ...     expire=3600,
        ...     skip_cache_keys={"request_id"}
        ... )
        ... def get_user(user_id: int, request_id: str = None):
        ...     return fetch_user_from_db(user_id)

        >>> # For async functions:
        >>> @cache_wrapper(redis=redis_instance, namespace="api:data", expire=1800)
        ... async def fetch_api_data(endpoint: str):
        ...     return await call_external_api(endpoint)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Inner decorator that wraps the function with caching logic.

        Args:
            func: The function to wrap with caching.

        Returns:
            Callable: The wrapped function with caching support.
        """
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def awrapper(*args, **kwargs):
                return await acache_function(
                    func=func,
                    redis=redis,
                    namespace=namespace,
                    expire=expire,
                    cache_only_for=cache_only_for,
                    skip_cache_keys=skip_cache_keys,
                    *args,
                    **kwargs,
                )

            return awrapper
        else:

            @wraps(func)
            def swrapper(*args, **kwargs):
                return cache_function(
                    func=func,
                    redis=redis,
                    namespace=namespace,
                    expire=expire,
                    cache_only_for=cache_only_for,
                    skip_cache_keys=skip_cache_keys,
                    *args,
                    **kwargs,
                )

            return swrapper

    return decorator
