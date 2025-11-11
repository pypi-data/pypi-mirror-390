"""Redis health check utilities.

This module provides functions to verify Redis connectivity and server
availability by performing ping operations and returning diagnostic
information.
"""

from typing import Optional, Tuple

from .connection import RedisInstance

__all__ = ("is_redis_connected",)


def is_redis_connected(redis: RedisInstance) -> Tuple[bool, Optional[Exception]]:
    """Check if Redis connection is functional by sending a ping command.

    Attempts to ping the Redis server to verify connectivity and server availability.
    Returns both a boolean status and any exception encountered during the check,
    making it useful for health check endpoints and diagnostics.

    Args:
        redis: RedisInstance to test connectivity for. The instance should be
            properly configured with valid connection parameters.

    Returns:
        Tuple[bool, Optional[Exception]]: A tuple containing:
            - bool: True if ping successful and Redis is reachable, False otherwise.
            - Optional[Exception]: The exception object if connection failed (for
              debugging/logging), None if successful.

    Example:
        >>> config = RedisConfig().set_redis_host("localhost").set_redis_port(6379)
        >>> redis = RedisInstance(config)
        >>> is_connected, error = is_redis_connected(redis)
        >>> if is_connected:
        ...     print("Redis is healthy")
        ... else:
        ...     print(f"Redis connection failed: {error}")

    Note:
        This function uses a synchronous Redis client from the connection pool.
        For asynchronous health checks, consider implementing an async variant.
    """
    try:
        ping_result = redis.get_redis_client().ping()
        return bool(ping_result), None
    except Exception as e:
        return False, e
