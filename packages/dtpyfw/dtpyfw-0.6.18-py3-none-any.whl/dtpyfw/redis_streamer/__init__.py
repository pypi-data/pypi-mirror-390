"""Redis Streams messaging infrastructure for microservices.

Description:
    This package provides both synchronous and asynchronous Redis Streams
    consumers with built-in support for:
    - Decoupled fan-out across microservices using consumer groups
    - At-most-once message processing per group via ZSET-based deduplication
    - Adaptive sleep patterns to reduce network load during idle periods
    - Connection pooling for efficient resource utilization
    - Automatic reconnection and error handling
    - Background maintenance tasks for cleanup and housekeeping

Modules:
    message: Message dataclass for Redis Streams payloads
    asynchronize: AsyncRedisStreamer for async/await patterns
    synchronize: RedisStreamer for synchronous/threaded patterns
    common: Shared utilities and base class for streamers
"""

from ..core.require_extra import require_extra

__all__ = (
    "message",
    "asynchronize",
    "synchronize",
)


require_extra("redis", "redis")
