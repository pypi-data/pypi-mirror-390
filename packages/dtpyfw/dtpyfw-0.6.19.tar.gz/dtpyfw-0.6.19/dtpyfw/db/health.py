"""Database health check utilities.

Provides functions to verify database connectivity and operational
status.
"""

from typing import Tuple

from sqlalchemy import text

from .database import DatabaseInstance

__all__ = ("is_database_connected",)


def is_database_connected(db: DatabaseInstance) -> Tuple[bool, Exception | None]:
    """Check if both read and write database connections are working.

    Executes a simple SELECT 1 query on both read and write database engines
    to verify connectivity and operational status.

    Args:
        db: DatabaseInstance to check for connectivity.

    Returns:
        A tuple containing:
            - bool: True if both connections are working, False otherwise.
            - Exception | None: The exception if connection failed, None if successful.
    """
    try:
        with db.engine_write.connect() as connection:
            connection.execute(text("SELECT 1"))

        with db.engine_read.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True, None

    except Exception as e:
        return False, e
