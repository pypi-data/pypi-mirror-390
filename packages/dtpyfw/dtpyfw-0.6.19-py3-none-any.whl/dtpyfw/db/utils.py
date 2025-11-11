"""Database utility functions for bulk operations.

Provides upsert (insert or update) functionality for PostgreSQL
databases with both synchronous and asynchronous support.
"""

from typing import Any, Dict, List, Type

from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

__all__ = (
    "upsert_data",
    "upsert_data_async",
)


def _prepare_upsert(
    list_of_data: List[Dict[str, Any]],
    model: Type[DeclarativeBase],
):
    """Prepare the INSERT ... ON CONFLICT DO UPDATE statement for PostgreSQL.

    Builds a PostgreSQL-specific upsert statement that inserts new rows or
    updates existing rows based on primary key conflicts.

    Args:
        list_of_data: A list of dictionaries with data to be inserted/updated.
        model: The SQLAlchemy model class (mapped to a table).

    Returns:
        A tuple (do_upsert, statement_or_None) where:
            - do_upsert (bool): Indicates if there's a valid statement to execute.
            - statement_or_None: The compiled statement or None if no valid upsert is needed.
    """

    # If there's no data, we can't do anything.
    if not list_of_data:
        return False, None

    # Build the base INSERT statement from the data
    stmt = insert(model.__table__).values(list_of_data) # type: ignore

    # We only want to update columns that exist in the data and are not primary keys
    data_keys = list_of_data[0].keys()
    update_dict = {
        col.name: col
        for col in stmt.excluded
        if not col.primary_key and col.name in data_keys
    }

    # If there's nothing to update, we can't do an upsert
    if not update_dict:
        return False, None

    # Get the primary keys to use in the ON CONFLICT clause
    primary_keys = [key.name for key in inspect(model.__table__).primary_key] # type: ignore

    # Build the ON CONFLICT DO UPDATE statement
    stmt = stmt.on_conflict_do_update(index_elements=primary_keys, set_=update_dict)

    return True, stmt


def upsert_data(
    list_of_data: List[Dict[str, Any]],
    model: Type[DeclarativeBase],
    db: Session,
    only_update=False,
    only_insert=False,
) -> bool:
    """Insert or update records in bulk using PostgreSQL upsert semantics.

    Performs bulk insert/update operations with support for PostgreSQL's
    ON CONFLICT DO UPDATE functionality. Can be configured for insert-only
    or update-only operations.

    Args:
        list_of_data: List of dictionaries containing the data to upsert.
        model: The SQLAlchemy model class representing the target table.
        db: SQLAlchemy Session for database operations.
        only_update: If True, only perform updates on existing records.
        only_insert: If True, only insert new records without updates.

    Returns:
        True if the operation succeeded, False if there was no data to process.

    Raises:
        SQLAlchemyError: If database operation fails.
        IntegrityError: If constraint violations occur.
    """
    if not list_of_data:
        return False

    try:
        if only_update:
            db.bulk_update_mappings(model, list_of_data) # type: ignore
            db.commit()
            return True

        elif only_insert:
            db.bulk_insert_mappings(model, list_of_data) # type: ignore
            db.commit()
            return True

        do_upsert, stmt = _prepare_upsert(list_of_data, model)
        if not do_upsert or stmt is None:
            return False

        db.execute(stmt)
        db.commit()
        return True

    except (SQLAlchemyError, IntegrityError):
        db.rollback()
        raise


async def upsert_data_async(
    list_of_data: List[Dict[str, Any]],
    model: Type[DeclarativeBase],
    db: AsyncSession,
    only_update: bool = False,
    only_insert: bool = False,
) -> bool:
    """Asynchronously insert or update records in bulk using PostgreSQL upsert.

    Performs async bulk insert/update operations with support for PostgreSQL's
    ON CONFLICT DO UPDATE functionality. Can be configured for insert-only
    or update-only operations.

    Args:
        list_of_data: List of dictionaries containing the data to upsert.
        model: The SQLAlchemy model class representing the target table.
        db: AsyncSession for asynchronous database operations.
        only_update: If True, only perform updates on existing records.
        only_insert: If True, only insert new records without updates.

    Returns:
        True if the operation succeeded, False if there was no data to process.

    Raises:
        SQLAlchemyError: If database operation fails.
        IntegrityError: If constraint violations occur.
    """
    if not list_of_data:
        return False

    if only_update:
        await db.run_sync(lambda s: s.bulk_update_mappings(model, list_of_data)) # type: ignore
        await db.commit()
        return True

    elif only_insert:
        await db.run_sync(lambda s: s.bulk_insert_mappings(model, list_of_data)) # type: ignore
        await db.commit()
        return True

    do_upsert, stmt = _prepare_upsert(list_of_data, model)
    if not do_upsert or stmt is None:
        return False

    await db.execute(stmt)
    await db.commit()
    return True
