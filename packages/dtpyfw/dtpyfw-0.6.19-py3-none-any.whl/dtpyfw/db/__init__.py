"""Database utilities for SQLAlchemy-based applications.

This module provides comprehensive database management tools including:
- Configuration builders for database connections
- Engine and session orchestration for sync/async operations
- Health check utilities
- Base model classes with common ORM functionality
- Advanced search and filtering capabilities
- Data manipulation utilities
"""

from ..core.require_extra import require_extra

__all__ = (
    "config",
    "search_context",
    "database",
    "health",
    "model",
    "search",
    "utils",
)

require_extra("database", "sqlalchemy")
