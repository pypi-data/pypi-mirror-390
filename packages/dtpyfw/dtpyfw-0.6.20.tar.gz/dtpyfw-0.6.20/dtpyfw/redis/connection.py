"""Redis connection management module.

This module provides the RedisInstance class for managing both
synchronous and asynchronous Redis connections with connection pooling,
URL construction, and context managers for safe resource handling.
"""

import urllib.parse
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

import redis
from redis.asyncio import Redis as AsyncRedis
from redis.asyncio.connection import ConnectionPool as AsyncConnectionPool
from redis.connection import ConnectionPool

from .config import RedisConfig

__all__ = ("RedisInstance",)


class RedisInstance:
    """Manage synchronous and asynchronous Redis connection pools.

    Provides unified access to Redis clients with connection pooling for both
    synchronous and asynchronous operations. Handles connection URL construction
    from configuration parameters and lazy initialization of connection pools.

    Attributes:
        config: RedisConfig object containing connection parameters.
        redis_url: Constructed Redis connection URL string.

    Example:
        >>> config = RedisConfig() \\
        ...     .set_redis_host("localhost") \\
        ...     .set_redis_port(6379) \\
        ...     .set_redis_db("0")
        >>> redis_instance = RedisInstance(config)
        >>> 
        >>> # Synchronous usage
        >>> with redis_instance.get_redis() as client:
        ...     client.set("key", "value")
        ...     value = client.get("key")
        >>> 
        >>> # Asynchronous usage
        >>> async with redis_instance.get_async_redis() as client:
        ...     await client.set("key", "value")
        ...     value = await client.get("key")
    """

    def __init__(self, redis_config: RedisConfig) -> None:
        """Initialize Redis instance from configuration.

        Args:
            redis_config: RedisConfig object containing connection parameters
                such as host, port, database, authentication, etc.
        """
        self.config: RedisConfig = redis_config
        self.redis_url: str = self._set_redis_url()
        self._sync_pool: Optional[ConnectionPool] = None
        self._async_pool: Optional[AsyncConnectionPool] = None

    def _set_redis_url(self) -> str:
        """Construct the Redis connection URL from configuration.

        Builds a connection URL from individual configuration parameters if
        a full URL is not provided. Handles authentication, SSL, and URL encoding
        of credentials to ensure special characters are properly escaped.

        Returns:
            str: A complete Redis connection URL in the format:
                redis[s]://[username:password@]host:port/database

        Note:
            - Uses rediss:// protocol if SSL is enabled, redis:// otherwise
            - URL-encodes username and password to handle special characters
            - Supports username-only, password-only, or both for authentication
        """
        redis_url: Optional[str] = self.config.get("redis_url")
        if redis_url:
            return redis_url

        redis_ssl: bool = self.config.get("redis_ssl", False)
        redis_host: str = self.config.get("redis_host")
        redis_port: int = self.config.get("redis_port")
        redis_db: str = self.config.get("redis_db")
        redis_username: str = self.config.get("redis_username", "")
        redis_password: str = self.config.get("redis_password", "")

        username: str = urllib.parse.quote(redis_username) if redis_username else ""
        password: str = urllib.parse.quote(redis_password) if redis_password else ""

        auth_part: str = (
            f"{username}:{password}@"
            if username and password
            else f"{password}@" if password else f"{username}@" if username else ""
        )
        protocol: str = "rediss" if redis_ssl else "redis"

        return f"{protocol}://{auth_part}{redis_host}:{redis_port}/{redis_db}"

    def get_redis_url(self) -> str:
        """Get the Redis connection URL.

        Returns:
            str: The constructed or configured Redis connection URL.
        """
        return self.redis_url

    def _get_sync_pool(self) -> ConnectionPool:
        """Get or create a synchronous connection pool.

        Creates a connection pool on first access and reuses it for subsequent calls.
        Uses max_connections and socket_timeout from configuration if specified.

        Returns:
            ConnectionPool: A synchronous Redis connection pool instance.

        Note:
            Defaults to 10 max connections and 5 second timeout if not configured.
        """
        if self._sync_pool is None:
            self._sync_pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.get("redis_max_connections", 10),
                socket_timeout=self.config.get("redis_socket_timeout", 5),
            )
        return self._sync_pool

    def _get_async_pool(self) -> AsyncConnectionPool:
        """Get or create an asynchronous connection pool.

        Creates a connection pool on first access and reuses it for subsequent calls.
        Uses max_connections and socket_timeout from configuration if specified.

        Returns:
            AsyncConnectionPool: An asynchronous Redis connection pool instance.

        Note:
            Defaults to 10 max connections and 5 second timeout if not configured.
        """
        if self._async_pool is None:
            self._async_pool = AsyncConnectionPool.from_url(
                self.redis_url,
                max_connections=self.config.get("redis_max_connections", 10),
                socket_timeout=self.config.get("redis_socket_timeout", 5),
            )
        return self._async_pool

    def get_redis_client(self) -> redis.Redis:
        """Create a synchronous Redis client using the connection pool.

        Returns:
            redis.Redis: A synchronous Redis client instance configured with
                the connection pool for efficient connection reuse.

        Example:
            >>> redis_instance = RedisInstance(config)
            >>> client = redis_instance.get_redis_client()
            >>> client.set("key", "value")
            >>> client.close()
        """
        return redis.Redis(connection_pool=self._get_sync_pool())

    async def get_async_redis_client(self) -> AsyncRedis:
        """Create an asynchronous Redis client using the connection pool.

        Returns:
            AsyncRedis: An asynchronous Redis client instance configured with
                the connection pool for efficient connection reuse.

        Example:
            >>> redis_instance = RedisInstance(config)
            >>> client = await redis_instance.get_async_redis_client()
            >>> await client.set("key", "value")
            >>> await client.close()
        """
        return AsyncRedis(connection_pool=self._get_async_pool())

    async def reset_async_pool(self) -> None:
        """Reset and disconnect the asynchronous connection pool.

        Disconnects all connections in the async pool and clears the pool reference.
        The pool will be recreated on next access. Useful for cleanup or
        reconfiguration scenarios.

        Example:
            >>> await redis_instance.reset_async_pool()
        """
        if self._async_pool:
            await self._async_pool.disconnect()
        self._async_pool = None

    def reset_sync_pool(self) -> None:
        """Reset and disconnect the synchronous connection pool.

        Disconnects all connections in the sync pool and clears the pool reference.
        The pool will be recreated on next access. Useful for cleanup or
        reconfiguration scenarios.

        Example:
            >>> redis_instance.reset_sync_pool()
        """
        if self._sync_pool:
            self._sync_pool.disconnect()
        self._sync_pool = None

    @contextmanager
    def get_redis(self) -> Generator[redis.Redis, None, None]:
        """Create a context manager for a synchronous Redis client.

        Provides a Redis client within a context manager that properly handles
        cleanup, though the actual connection is managed by the pool.

        Yields:
            redis.Redis: A synchronous Redis client instance.

        Example:
            >>> with redis_instance.get_redis() as client:
            ...     client.set("key", "value")
            ...     value = client.get("key")
            ...     print(value)
        """
        client: redis.Redis = self.get_redis_client()
        try:
            yield client
        finally:
            pass

    @asynccontextmanager
    async def get_async_redis(self) -> AsyncGenerator[AsyncRedis, None]:
        """Create a context manager for an asynchronous Redis client.

        Provides an async Redis client within a context manager that properly
        handles cleanup, though the actual connection is managed by the pool.

        Yields:
            AsyncRedis: An asynchronous Redis client instance.

        Example:
            >>> async with redis_instance.get_async_redis() as client:
            ...     await client.set("key", "value")
            ...     value = await client.get("key")
            ...     print(value)
        """
        client: AsyncRedis = await self.get_async_redis_client()
        try:
            yield client
        finally:
            pass
