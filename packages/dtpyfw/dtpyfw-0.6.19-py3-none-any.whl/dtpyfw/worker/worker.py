"""Lightweight builder for configuring and creating a Celery application."""

from __future__ import annotations

import ssl
from typing import Any, Optional

from celery import Celery

from ..redis.connection import RedisInstance
from .task import Task

__all__ = ("Worker",)


class Worker:
    """Fluent builder for configuring and creating Celery applications.

    Description:
        Provides a builder pattern interface for constructing a Celery application
        with comprehensive configuration options. Manages broker and backend settings,
        task routing, serialization, timezone configuration, and integration with
        Redis as the message broker and result backend. Supports SSL/TLS connections,
        RedBeat scheduling, and celery-once task locking.

    Attributes:
        _celery (dict[str, Any]): Core Celery application configuration parameters.
        _celery_conf (dict[str, Any]): Additional Celery configuration settings.
        _discovered_task (list[str]): List of task module paths for autodiscovery.
    """

    _celery: dict[str, Any] = {
        "name": "dt_celery_app",
        "task_serializer": "json",
        "result_serializer": "json",
        "timezone": "America/Los_Angeles",
        "task_track_started": True,
        "result_persistent": True,
        "worker_prefetch_multiplier": 1,
        "broker": None,
        "backend": None,
    }
    _celery_conf: dict[str, Any] = {
        "broker_transport_options": {
            "global_keyprefix": "celery-broker:",
            "socket_keepalive": True,
        },
        "result_backend_transport_options": {
            "global_keyprefix": "celery-backend:",
            "socket_keepalive": True,
        },
        "enable_utc": False,
        "broker_connection_retry": True,
        "broker_connection_max_retries": None,
        "broker_connection_retry_on_startup": True,
        "result_expires": 3600,
        "task_routes": {},
        "beat_schedule": {},
        "beat_max_loop_interval": 30,
        "redbeat_redis_url": None,
        "beat_scheduler": "redbeat.RedBeatScheduler",
        "redbeat_key_prefix": "celery-beat:",
        "redbeat_lock_key": "celery-beat::lock",
        "ONCE": {
            "backend": "celery_once.backends.Redis",
            "settings": {"default_timeout": 60 * 60},
        },
    }
    _discovered_task: list[str] = []

    def set_task(self, task: Task) -> "Worker":
        """Attach Task registry containing routes, schedules, and modules.

        Description:
            Configures the worker with task routing, periodic schedules, and
            autodiscovery modules from a Task instance. This method extracts
            task routes for queue routing, beat schedules for periodic execution,
            and task module paths for Celery's autodiscovery mechanism.

        Args:
            task (Task): A Task instance containing registered task routes,
                periodic schedules, and module paths.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["task_routes"] = task.get_tasks_routes()
        self._celery_conf["beat_schedule"] = task.get_periodic_tasks()
        self._discovered_task = task.get_tasks()
        return self

    def set_redis(
        self,
        redis_instance: RedisInstance,
        retry_on_timeout: bool = True,
        socket_keepalive: bool = True,
    ) -> "Worker":
        """Configure Redis as broker and backend with connection settings.

        Description:
            Configures Redis as both the message broker and result backend for
            Celery. Extracts the Redis URL from the provided RedisInstance and
            applies connection parameters including max connections, timeouts,
            retry behavior, and keepalive settings. Automatically enables SSL/TLS
            configuration when a rediss:// URL is detected.

        Args:
            redis_instance (RedisInstance): The Redis connection instance containing
                configuration and URL for broker and backend.
            retry_on_timeout (bool): Whether to retry Redis operations that timeout.
                Defaults to True.
            socket_keepalive (bool): Whether to enable TCP keepalive on Redis sockets
                to detect dead connections. Defaults to True.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        redis_url = redis_instance.get_redis_url()
        self._celery["broker"] = redis_url
        self._celery["backend"] = redis_url
        self._celery_conf["redbeat_redis_url"] = redis_url
        self._celery_conf["ONCE"]["settings"]["url"] = redis_url

        redis_max_connections = redis_instance.config.get("redis_max_connections", 10)
        redis_socket_connect_timeout = redis_instance.config.get(
            "redis_socket_timeout", 10
        )
        self._celery_conf["broker_transport_options"][
            "redis_max_connections"
        ] = redis_max_connections
        self._celery_conf["broker_transport_options"][
            "redis_socket_connect_timeout"
        ] = redis_socket_connect_timeout
        self._celery_conf["broker_transport_options"][
            "redis_retry_on_timeout"
        ] = retry_on_timeout
        self._celery_conf["broker_transport_options"][
            "redis_socket_keepalive"
        ] = socket_keepalive

        self._celery_conf["result_backend_transport_options"][
            "redis_max_connections"
        ] = redis_max_connections
        self._celery_conf["result_backend_transport_options"][
            "redis_socket_connect_timeout"
        ] = redis_socket_connect_timeout
        self._celery_conf["result_backend_transport_options"][
            "redis_retry_on_timeout"
        ] = retry_on_timeout
        self._celery_conf["result_backend_transport_options"][
            "redis_socket_keepalive"
        ] = socket_keepalive

        if redis_url.startswith("rediss"):
            self._celery["broker_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}
            self._celery["redis_backend_use_ssl"] = {"ssl_cert_reqs": ssl.CERT_NONE}

        return self

    def set_name(self, name: str) -> "Worker":
        """Set the main application name for the Celery instance.

        Description:
            Configures the Celery application's main name identifier, which is
            used in logs, monitoring tools, and process identification.

        Args:
            name (str): The application name for the Celery instance.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["main"] = name
        return self

    def set_timezone(self, timezone: str) -> "Worker":
        """Set the timezone for Celery task scheduling and execution.

        Description:
            Configures the timezone used by Celery for task scheduling, particularly
            for periodic tasks with crontab schedules. This affects when scheduled
            tasks execute.

        Args:
            timezone (str): The timezone identifier (e.g., "UTC", "America/New_York").

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["timezone"] = timezone
        return self

    def set_task_serializer(self, task_serializer: str) -> "Worker":
        """Set the serialization format for task messages.

        Description:
            Configures how task messages are serialized when sent to the broker.
            Common formats include "json", "pickle", "yaml", or "msgpack".

        Args:
            task_serializer (str): The serializer name to use for task messages.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["task_serializer"] = task_serializer
        return self

    def set_result_serializer(self, result_serializer: str) -> "Worker":
        """Set the serialization format for task results.

        Description:
            Configures how task results are serialized when stored in the result
            backend. Common formats include "json", "pickle", "yaml", or "msgpack".

        Args:
            result_serializer (str): The serializer name to use for task results.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["result_serializer"] = result_serializer
        return self

    def set_track_started(self, value: bool) -> "Worker":
        """Enable or disable tracking of task started state.

        Description:
            Configures whether Celery tracks when a task transitions to the
            "started" state. Enabling this provides more detailed task lifecycle
            information but adds overhead to task execution.

        Args:
            value (bool): True to enable task started tracking, False to disable.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["task_track_started"] = value
        return self

    def set_result_persistent(self, value: bool) -> "Worker":
        """Enable or disable persistent storage of task results.

        Description:
            Configures whether task results are persisted in the result backend.
            When enabled, results are stored and can be retrieved later. When
            disabled, results are not saved to the backend.

        Args:
            value (bool): True to persist results, False to disable persistence.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["result_persistent"] = value
        return self

    def set_worker_prefetch_multiplier(self, number: int) -> "Worker":
        """Set the number of tasks each worker prefetches from the broker.

        Description:
            Configures how many tasks a worker will prefetch and reserve from
            the broker. A value of 1 means the worker only prefetches one task
            at a time. Higher values increase throughput but may cause uneven
            task distribution across workers.

        Args:
            number (int): The prefetch multiplier value (typically 1-4).

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery["worker_prefetch_multiplier"] = number
        return self

    def set_broker_prefix(self, prefix: str) -> "Worker":
        """Set the Redis key prefix for broker transport options.

        Description:
            Configures the global key prefix used by the broker transport for
            storing messages in Redis. This allows multiple Celery applications
            to share a Redis instance without key collisions.

        Args:
            prefix (str): The key prefix string (will be suffixed with ":").

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["broker_transport_options"]["global_keyprefix"] = f"{prefix}:"
        return self

    def set_backend_prefix(self, prefix: str) -> "Worker":
        """Set the Redis key prefix for result backend transport options.

        Description:
            Configures the global key prefix used by the result backend for
            storing task results in Redis. This allows multiple Celery applications
            to share a Redis instance without key collisions.

        Args:
            prefix (str): The key prefix string (will be suffixed with ":").

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["result_backend_transport_options"][
            "global_keyprefix"
        ] = f"{prefix}:"
        return self

    def set_redbeat_key_prefix(self, prefix: str) -> "Worker":
        """Set the Redis key prefix for RedBeat schedule storage.

        Description:
            Configures the key prefix used by RedBeat for storing periodic task
            schedules in Redis. This allows multiple Celery applications to share
            a Redis instance without schedule key collisions.

        Args:
            prefix (str): The key prefix string (will be suffixed with ":").

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["redbeat_key_prefix"] = f"{prefix}:"
        return self

    def set_redbeat_lock_key(self, redbeat_lock_key: str) -> "Worker":
        """Set the Redis key name for the RedBeat scheduler lock.

        Description:
            Configures the lock key used by RedBeat to ensure only one beat
            scheduler runs at a time across multiple worker instances. This
            prevents duplicate execution of periodic tasks.

        Args:
            redbeat_lock_key (str): The Redis key name for the RedBeat lock.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["redbeat_lock_key"] = redbeat_lock_key
        return self

    def set_enable_utc(self, value: bool) -> "Worker":
        """Enable or disable UTC mode for all Celery timestamps.

        Description:
            Configures whether Celery uses UTC for all internal timestamps and
            scheduling. When enabled, all times are stored and processed as UTC.
            When disabled, the configured timezone is used instead.

        Args:
            value (bool): True to enable UTC mode, False to use configured timezone.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["enable_utc"] = value
        return self

    def set_broker_connection_max_retries(self, value: Optional[int]) -> "Worker":
        """Set the maximum number of broker connection retry attempts.

        Description:
            Configures how many times Celery will attempt to reconnect to the
            broker when a connection is lost. Set to None for unlimited retries.

        Args:
            value (Optional[int]): Maximum retry attempts, or None for unlimited.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["broker_connection_max_retries"] = value
        return self

    def set_broker_connection_retry_on_startup(self, value: bool) -> "Worker":
        """Enable or disable broker connection retry during worker startup.

        Description:
            Configures whether the worker will retry connecting to the broker
            during the startup process if the initial connection fails. When
            enabled, the worker will keep attempting to connect rather than
            failing immediately.

        Args:
            value (bool): True to retry connections on startup, False to fail fast.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["broker_connection_retry_on_startup"] = value
        return self

    def set_result_expires(self, result_expires: int) -> "Worker":
        """Set the expiration time for task results in seconds.

        Description:
            Configures how long task results are retained in the result backend
            before being automatically deleted. This helps manage storage and
            prevents the backend from growing indefinitely.

        Args:
            result_expires (int): The result expiration time in seconds.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["result_expires"] = result_expires
        return self

    def set_once_default_timeout(self, default_timeout: int) -> "Worker":
        """Set the default lock timeout for celery-once task deduplication.

        Description:
            Configures the default timeout in seconds for celery-once locks,
            which prevent duplicate execution of tasks. When a task is running,
            subsequent invocations are blocked until the lock expires or is
            released.

        Args:
            default_timeout (int): The lock timeout in seconds.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["ONCE"]["settings"]["default_timeout"] = default_timeout
        return self

    def set_once_blocking(self, blocking: bool) -> "Worker":
        """Enable or disable blocking behavior for celery-once locks.

        Description:
            Configures whether tasks should block and wait when a celery-once
            lock is already held by another task execution. When enabled, tasks
            will wait for the lock to be released. When disabled, tasks will
            fail immediately if the lock is held.

        Args:
            blocking (bool): True to enable blocking wait, False to fail immediately.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["ONCE"]["settings"]["blocking"] = blocking
        return self

    def set_once_blocking_timeout(self, blocking_timeout: int) -> "Worker":
        """Set the blocking timeout for celery-once lock acquisition.

        Description:
            Configures how long in seconds a task will wait to acquire a
            celery-once lock when blocking is enabled. If the lock cannot be
            acquired within this timeout, the task will fail.

        Args:
            blocking_timeout (int): The blocking timeout in seconds.

        Returns:
            Worker: The current Worker instance for method chaining.
        """
        self._celery_conf["ONCE"]["settings"]["blocking_timeout"] = blocking_timeout
        return self

    def create(self) -> Celery:
        """Create and return a fully configured Celery application instance.

        Description:
            Instantiates a Celery application with all configured settings,
            including broker, backend, serializers, task routing, periodic
            schedules, and autodiscovery of task modules. This method should
            be called after all configuration methods to produce the final
            Celery app ready for use.

        Returns:
            Celery: A fully configured Celery application instance.
        """
        celery_app = Celery(**self._celery)
        celery_app.conf.update(self._celery_conf)
        celery_app.autodiscover_tasks(self._discovered_task)
        return celery_app
