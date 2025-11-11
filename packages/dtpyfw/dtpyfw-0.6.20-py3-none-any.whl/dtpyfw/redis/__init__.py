"""Redis utilities package for DealerTower framework.

This package provides Redis connection management, caching utilities,
configuration builders, and health check functions for working with
Redis in both synchronous and asynchronous contexts.
"""

from ..core.require_extra import require_extra

__all__ = (
    "caching",
    "config",
    "connection",
    "health",
    "output_watcher",
)


require_extra("redis", "redis")
