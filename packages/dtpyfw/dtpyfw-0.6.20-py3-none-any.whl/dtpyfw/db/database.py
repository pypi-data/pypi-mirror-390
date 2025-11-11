"""Database engine/session orchestration utilities.

Centralizes sync/async SQLAlchemy engine creation, session management,
and health checks for both read and write connections.
"""

from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncGenerator, Generator, Optional

from sqlalchemy import NullPool, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session as SessionType
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from ..core.exception import exception_to_dict
from .config import DatabaseConfig
from ..log import footprint

__all__ = ("DatabaseInstance",)


class DatabaseInstance:
    """Manage SQLAlchemy engines and sessions for read/write usage.

    This class orchestrates database connections providing both synchronous
    and asynchronous engines, session factories, and context managers for
    read and write operations. It supports connection pooling, SSL configuration,
    and separate read replicas.

    Args:
        config: Resolved database configuration holding credentials and connection
            options for read and write connections.
    """

    base: type[DeclarativeBase]

    def __init__(self, config: DatabaseConfig, base_name: Optional[str] = None) -> None:
        """Initialize DatabaseInstance with configuration settings.

        Args:
            config: DatabaseConfig instance containing all connection parameters.
        """
        self.db_backend = (config.get("db_backend") or "postgresql").lower()
        self.db_driver_sync = config.get("db_driver_sync")
        self.db_driver_async = config.get("db_driver_async")
        self.connect_args = config.get("connect_args", {})
        self.db_user = config.get("db_user")
        self.db_password = config.get("db_password")
        self.db_host_write = config.get("db_host")
        self.db_host_read = config.get("db_host_read") or self.db_host_write
        self.db_port = config.get("db_port")
        self.db_name = config.get("db_name")
        self.db_ssl = config.get("db_ssl", False)
        self.db_pool_size = config.get("db_pool_size", None)
        self.db_max_overflow = config.get("db_max_overflow", 0)

        self.active_connections = 0

        # Build connection URLs for sync and async for both write and read.
        db_url = config.get("db_url")

        if db_url:
            self.database_path_write = db_url
            self.async_database_path_write = self._build_async_url(db_url)
        else:
            self.database_path_write = self._build_database_url(
                async_mode=False, host=self.db_host_write
            )
            self.async_database_path_write = self._build_database_url(
                async_mode=True, host=self.db_host_write
            )

        db_url_read = config.get("db_url_read") or db_url
        if db_url_read:
            self.database_path_read = db_url_read
            self.async_database_path_read = self._build_async_url(db_url_read)
        else:
            self.database_path_read = self._build_database_url(
                async_mode=False, host=self.db_host_read
            )
            self.async_database_path_read = self._build_database_url(
                async_mode=True, host=self.db_host_read
            )

        # Database settings
        db_settings = self._initialize_db_settings()

        # Create synchronous engines for write and read.
        self.engine_write = create_engine(self.database_path_write, **db_settings)
        self.engine_read = create_engine(self.database_path_read, **db_settings)

        self.write_session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine_write,
            expire_on_commit=True,
        )
        self.read_session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine_read,
            expire_on_commit=True,
        )

        # Create asynchronous engines for write and read.
        self.async_engine_write = create_async_engine(
            self.async_database_path_write, **db_settings
        )
        self.async_engine_read = create_async_engine(
            self.async_database_path_read, **db_settings
        )
        self.async_write_session = async_sessionmaker(
            bind=self.async_engine_write,
            class_=AsyncSession,
            expire_on_commit=True,
            autocommit=False,
            autoflush=False,
        )
        self.async_read_session = async_sessionmaker(
            bind=self.async_engine_read,
            class_=AsyncSession,
            expire_on_commit=True,
            autocommit=False,
            autoflush=False,
        )

        # Create a unique declarative base for this database instance
        if base_name is None:
            db_name = config.get("db_name", "default")
            base_name = f"DatabaseBase_{db_name}"
        
        # Create a new DatabaseBase class with isolated metadata
        self.base = type(base_name, (DeclarativeBase,), {
            "__module__": __name__,
            "__doc__": f"Isolated DatabaseBase for {base_name}"
        })

    def _build_async_url(self, db_url: str) -> str:
        """Convert a standard database URL to its asynchronous equivalent.

        This method adapts the URL scheme for async drivers, particularly for
        PostgreSQL, by replacing driver names and adjusting SSL parameters.

        Args:
            db_url: The synchronous database URL.

        Returns:
            The asynchronous database URL.
        """
        if self.db_driver_sync:
            if self.db_driver_async:
                db_url = db_url.replace(
                    f"{self.db_backend}+{self.db_driver_sync}://",
                    f"{self.db_backend}+{self.db_driver_async}://",
                    1,
                )
            else:
                db_url = db_url.replace(
                    f"{self.db_backend}+{self.db_driver_sync}://",
                    f"{self.db_backend}://",
                    1,
                )
        else:
            if self.db_driver_async:
                db_url = db_url.replace(
                    f"{self.db_backend}://",
                    f"{self.db_backend}+{self.db_driver_async}://",
                    1,
                )

        if "postgresql" in db_url:
            return db_url.replace("sslmode=require", "ssl=require", 1)
        else:
            return db_url

    def _build_database_url(
        self, async_mode: bool = False, host: Optional[str] = None
    ) -> str:
        """Construct a database URL from configuration components.

        Builds a properly formatted database connection URL from individual
        configuration parameters, supporting both sync and async drivers
        with optional SSL settings.

        Args:
            async_mode: If True, build an async URL; otherwise, a sync URL.
            host: The database host. Defaults to the write host if None.

        Returns:
            The fully constructed database connection URL string.
        """
        if host is None:
            host = self.db_host_write

        scheme = self.db_backend

        if async_mode and self.db_driver_async:
            scheme += f"+{self.db_driver_async}"
        else:
            if self.db_driver_sync:
                scheme += f"+{self.db_driver_sync}"

        url = f"{scheme}://{self.db_user}:{self.db_password}@{host}:{self.db_port}/{self.db_name}"

        if self.db_ssl:
            if self.db_backend == "postgresql":
                url += "?ssl=require" if async_mode else "?sslmode=require"
            elif self.db_backend == "mysql":
                url += "?ssl-mode=REQUIRED"

        return url

    def _initialize_db_settings(self) -> dict:
        """Build engine keyword arguments based on pooling configuration.

        Constructs SQLAlchemy engine settings including connection pooling,
        SSL configuration, and connection arguments based on the database
        backend and configuration.

        Returns:
            Dictionary of SQLAlchemy engine keyword arguments.
        """
        settings: dict[str, Any] = {
            "pool_pre_ping": True,
            "echo": False,
            "connect_args": self.connect_args or {},
        }

        if self.db_pool_size:
            settings.update(
                {
                    "pool_size": self.db_pool_size,
                    "pool_recycle": 300,
                    "pool_use_lifo": True,
                    "max_overflow": self.db_max_overflow,
                }
            )
        else:
            settings["poolclass"] = NullPool

        # SSL
        if self.db_ssl and self.db_backend == "mysql":
            settings["connect_args"] = {**settings.get("connect_args", {}), "ssl": {}}

        return settings

    def session_local(self) -> SessionType:
        """Create a new synchronous write session.

        Returns:
            A new SQLAlchemy Session instance configured for write operations.
        """
        return self.write_session()

    def session_local_read(self) -> SessionType:
        """Create a new synchronous read session.

        Returns:
            A new SQLAlchemy Session instance configured for read-only operations.
        """
        return self.read_session()

    def get_db(self, force: Optional[str] = None) -> Generator[SessionType, None, None]:
        """Yield a synchronous database session.

        This generator provides a session and ensures it is properly closed
        after use. It will roll back the session if an exception occurs during
        the session lifecycle.

        Args:
            force: If "read", yields a read-only session; otherwise, a write session.

        Yields:
            A SQLAlchemy Session object for database operations.

        Raises:
            Exception: Re-raises any exception that occurs during session usage
                after rolling back the transaction.
        """
        controller = f"{__name__}.get_db"
        if force == "read":
            db = self.session_local_read()
        else:
            db = self.session_local()

        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            try:
                db.close()
            except Exception as e:
                footprint.leave(
                    log_type="warning",
                    message="We could not close the database because of an error.",
                    controller=controller,
                    subject="Closing Database Connection Error",
                    payload=exception_to_dict(e),
                )

    @contextmanager
    def get_db_cm(
        self, force: Optional[str] = None
    ) -> Generator[SessionType, None, None]:
        """Provide a synchronous database session as a context manager.

        Manages the session lifecycle automatically with proper cleanup
        and rollback on exceptions.

        Args:
            force: If "read", provides a read-only session; otherwise, a write session.

        Yields:
            A SQLAlchemy Session object for database operations.

        Raises:
            Exception: Re-raises any exception after rolling back the transaction.
        """
        controller = f"{__name__}.get_db_cm"
        if force == "read":
            db = self.session_local_read()
        else:
            db = self.session_local()

        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            try:
                db.close()
            except Exception as e:
                footprint.leave(
                    log_type="warning",
                    message="We could not close the database because of an error.",
                    controller=controller,
                    subject="Closing Database Connection Error",
                    payload=exception_to_dict(e),
                )

    def get_db_read(self) -> Generator[SessionType, None, None]:
        """Yield a synchronous read-only database session.

        Convenience method that delegates to get_db with force="read".

        Yields:
            A SQLAlchemy Session configured for read-only operations.
        """
        yield from self.get_db(force="read")

    def get_db_write(self) -> Generator[SessionType, None, None]:
        """Yield a synchronous write-enabled database session.

        Convenience method that delegates to get_db with force="write".

        Yields:
            A SQLAlchemy Session configured for write operations.
        """
        yield from self.get_db(force="write")

    @contextmanager
    def get_db_cm_read(self) -> Generator[SessionType, None, None]:
        """Provide a synchronous read-only session via a context manager.

        Yields:
            A SQLAlchemy Session configured for read-only operations.
        """
        with self.get_db_cm(force="read") as db:
            yield db

    @contextmanager
    def get_db_cm_write(self) -> Generator[SessionType, None, None]:
        """Provide a synchronous write-enabled session via a context manager.

        Yields:
            A SQLAlchemy Session configured for write operations.
        """
        with self.get_db_cm(force="write") as db:
            yield db

    def create_tables(self) -> None:
        """Create all tables defined on the declarative base.

        This method uses the write engine to create tables in the database
        based on all models that inherit from the declarative base. This
        operation is idempotent - existing tables will not be modified.

        Returns:
            None
        """
        self.base.metadata.create_all(self.engine_write)

    def close_all_connections(self) -> None:
        """Dispose of all engine connection pools.

        Closes all database connections and cleans up connection pool resources
        for both read and write engines.

        Returns:
            None
        """
        self.engine_write.dispose()
        self.engine_read.dispose()

    def check_database_health(self) -> bool:
        """Ping both write and read databases; return True if healthy.

        Executes a simple SELECT 1 query on both write and read database
        connections to verify they are operational.

        Returns:
            True if both databases respond successfully, False otherwise.
        """
        controller = f"{__name__}.check_database_health"
        try:
            with self.engine_write.connect() as connection:
                connection.execute(text("SELECT 1"))

            with self.engine_read.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception as e:
            footprint.leave(
                log_type="error",
                message="We have issue on database health.",
                controller=controller,
                subject="Database Health Issue",
                payload=exception_to_dict(e),
            )
            return False

    def async_session_local(self) -> AsyncSession:
        """Create a new asynchronous write session.

        Returns:
            A new AsyncSession instance configured for write operations.
        """
        return self.async_write_session()

    def async_session_local_read(self) -> AsyncSession:
        """Create a new asynchronous read session.

        Returns:
            A new AsyncSession instance configured for read-only operations.
        """
        return self.async_read_session()

    async def async_get_db(
        self, force: Optional[str] = None
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async generator yielding a session with safe cleanup on errors.

        Provides an asynchronous database session with automatic rollback
        on exceptions and guaranteed cleanup.

        Args:
            force: If "read", yields a read-only session; otherwise, a write session.

        Yields:
            An AsyncSession object for database operations.

        Raises:
            Exception: Re-raises any exception after rolling back the transaction.
        """
        controller = f"{__name__}.async_get_db"
        if force == "read":
            db = self.async_session_local_read()
        else:
            db = self.async_session_local()

        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            try:
                await db.close()
            except Exception as e:
                footprint.leave(
                    log_type="warning",
                    message="We could not close the database because of an error.",
                    controller=controller,
                    subject="Closing Database Connection Error",
                    payload=exception_to_dict(e),
                )

    @asynccontextmanager
    async def async_get_db_cm(
        self, force: Optional[str] = None
    ) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager yielding an async session.

        Provides an asynchronous database session as a context manager with
        automatic cleanup and rollback on exceptions.

        Args:
            force: If "read", provides a read-only session; otherwise, a write session.

        Yields:
            An AsyncSession object for database operations.

        Raises:
            Exception: Re-raises any exception after rolling back the transaction.
        """
        if force == "read":
            db = self.async_session_local_read()
        else:
            db = self.async_session_local()

        try:
            yield db
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()

    async def async_get_db_read(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield async read sessions from async_get_db.

        Convenience method for obtaining read-only asynchronous sessions.

        Yields:
            An AsyncSession configured for read-only operations.
        """
        async for db in self.async_get_db(force="read"):
            yield db

    async def async_get_db_write(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield async write sessions from async_get_db.

        Convenience method for obtaining write-enabled asynchronous sessions.

        Yields:
            An AsyncSession configured for write operations.
        """
        async for db in self.async_get_db(force="write"):
            yield db

    @asynccontextmanager
    async def async_get_db_cm_read(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for a read session.

        Yields:
            An AsyncSession configured for read-only operations.
        """
        async with self.async_get_db_cm(force="read") as db:
            yield db

    @asynccontextmanager
    async def async_get_db_cm_write(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for a write session.

        Yields:
            An AsyncSession configured for write operations.
        """
        async with self.async_get_db_cm(force="write") as db:
            yield db
