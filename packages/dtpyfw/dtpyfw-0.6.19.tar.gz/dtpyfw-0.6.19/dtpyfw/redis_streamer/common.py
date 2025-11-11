import os
import re
import socket
import time
import uuid
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Dict, List, Optional, Self, Tuple

from redis.exceptions import ConnectionError, TimeoutError

from ..log import footprint
from ..redis.connection import RedisInstance

DEFAULT_EXCEPTIONS = (ConnectionError, TimeoutError, Exception)
REDIS_EXCEPTIONS = (ConnectionError, TimeoutError)


class CommonMethods:
    """Base class providing shared utilities for Redis Streams consumers.

    Description:
        Provides common methods and state management used by both synchronous
        and asynchronous Redis Streams consumer implementations. Handles
        consumer naming, subscription tracking, handler registration, and
        shared maintenance operations.
    """

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: int = 7 * 24 * 60 * 60 * 1000,
    ):
        """Initialize common consumer state and configuration.

        Description:
            Sets up the consumer instance with a unique name, initializes
            subscription and handler tracking, and configures the deduplication
            window for at-most-once message processing.

        Args:
            redis_instance (RedisInstance): The Redis connection manager.
            consumer_name (str): The logical name of the consumer service.
            dedup_window_ms (int, optional): Time window in milliseconds for
                deduplication tracking. Defaults to 7 days (604800000 ms).
        """
        self.listener_name: str = self._sanitize(consumer_name, maxlen=128)
        self.consumer_instance_name: str = self._gen_consumer_name()

        self._redis_instance = redis_instance

        self._subscriptions: List[Tuple[str, str, str]] = []
        self._handlers: DefaultDict[Tuple[str, str], List[Callable]] = defaultdict(list)

        # Default dedup window: 1 day
        self._dedup_window_ms: int = dedup_window_ms

        # Maintenance control
        self._last_ledger_cleanup = 0
        self._ledger_cleanup_interval = 300_000  # 5 minutes (ms)
        self._channel_retention: Dict[str, Optional[int]] = {}

    def _gen_consumer_name(self) -> str:
        """Generate unique consumer instance name.

        Description:
            Delegates to the static consumer name generator to create a unique
            identifier for this consumer instance.

        Returns:
            str: Unique consumer instance identifier.
        """
        return self._consumer_name_generator(self.listener_name)

    @staticmethod
    def _sanitize(s: str, maxlen: int) -> str:
        """Sanitize and truncate a string for use in Redis keys.

        Description:
            Removes or replaces invalid characters and ensures the string
            does not exceed a specified maximum length. Only alphanumeric
            characters and ._:- are preserved.

        Args:
            s (str): The string to sanitize.
            maxlen (int): Maximum allowed length for the result.

        Returns:
            str: Sanitized and truncated string.
        """
        s = re.sub(r"[^a-zA-Z0-9._:-]+", "-", s or "")
        return s[:maxlen]

    @staticmethod
    def _server_now_ms() -> int:
        """Get current server time in milliseconds since epoch.

        Description:
            Provides a consistent timestamp for deduplication and cleanup
            operations across the Redis Streams consumer.

        Returns:
            int: Current time in milliseconds.
        """
        return int(time.time() * 1000)

    @staticmethod
    def _group_name(channel: str, listener_name: str) -> str:
        """Generate consumer group name for a channel and listener.

        Description:
            Constructs the Redis consumer group identifier used for
            decoupled fan-out across microservices.

        Args:
            channel (str): The Redis stream channel name.
            listener_name (str): The logical consumer service name.

        Returns:
            str: Consumer group identifier.
        """
        return f"{channel}:{listener_name}:cg"

    @staticmethod
    def _processed_zset_key(channel: str, group: str) -> str:
        """Generate ZSET key for deduplication tracking.

        Description:
            Creates the Redis ZSET key used to track processed message IDs
            for at-most-once delivery guarantees within a consumer group.

        Args:
            channel (str): The Redis stream channel name.
            group (str): The consumer group identifier.

        Returns:
            str: ZSET key for processed messages.
        """
        return f"stream:{channel}:group:{group}:processed"

    @classmethod
    def _consumer_name_generator(cls, listener_name: str) -> str:
        """Generate a globally unique consumer instance identifier.

        Description:
            Creates a unique consumer name by combining the listener name,
            hostname (or pod name in Kubernetes), process ID, and a random
            suffix. This ensures each consumer instance is uniquely
            identifiable in the Redis consumer group.

        Args:
            listener_name (str): The logical consumer service name.

        Returns:
            str: Unique consumer instance identifier.
        """
        host = os.getenv("POD_NAME") or os.getenv("HOSTNAME") or socket.gethostname()
        pid = os.getpid()
        rnd = uuid.uuid4().hex[:8]
        name = ".".join([listener_name, cls._sanitize(host, maxlen=64), str(pid), rnd])
        return cls._sanitize(name, maxlen=200)

    @staticmethod
    def _dead_letter(
        channel: str, reason: str, message_id: str, extra: Dict[str, Any]
    ) -> None:
        """Log a failed message to the dead letter log.

        Description:
            Records information about messages that failed processing due to
            decode errors, schema validation failures, or handler exceptions.
            Uses the footprint logging system to create an audit trail for
            troubleshooting and monitoring purposes.

        Args:
            channel (str): The Redis stream channel name where the failure occurred.
            reason (str): The failure reason category. Common values include
                'decode/schema' for serialization errors and 'handler' for
                processing exceptions.
            message_id (str): The Redis stream message ID that failed.
            extra (Dict[str, Any]): Additional context information about the failure,
                such as error messages, handler names, or listener names.

        Returns:
            None
        """
        payload: Dict[str, Any] = {
            "reason": reason,
            "channel": channel,
            "message_id": message_id,
        }
        if extra:
            payload.update(extra)
        footprint.leave(
            log_type="error",
            subject="Message failed",
            controller=f"{__name__}.AsyncRedisStreamer._dead_letter",
            message=f"Message failure on channel '{channel}' (reason={reason})",
            payload=payload,
        )

    def register_channel(
        self,
        channel_name: str,
        retention_ms: int = 24 * 60 * 60 * 1000,
    ) -> "Self":
        """Register channel metadata with optional retention configuration.

        Description:
            Registers a channel for cleanup operations with a specified
            retention period. Messages older than the retention window
            will be eligible for removal during periodic cleanup tasks.
            This helps manage memory usage for high-throughput channels
            by preventing unbounded growth of deduplication tracking data.

        Args:
            channel_name (str): The Redis stream channel name to register.
            retention_ms (int, optional): Retention period in milliseconds
                for deduplication tracking. Messages older than this will
                be cleaned up. Defaults to 24 hours (86400000 ms).

        Returns:
            CommonMethods: Returns self for method chaining.
        """
        controller = f"{__name__}.AsyncRedisStreamer.register_channel"

        footprint.leave(
            log_type="debug",
            subject="Channel registered",
            message=f"Channel {channel_name} registered.",
            controller=controller,
            payload={
                "channel_name": channel_name,
                "retention_ms": retention_ms,
            },
        )
        self._channel_retention[channel_name] = retention_ms
        return self

    def register_handler(
        self,
        channel_name: str,
        handler_func: Callable,
        listener_name: Optional[str] = None,
    ) -> "Self":
        """Register a handler function for a specific channel.

        Description:
            Associates a callable handler with a channel and listener pair.
            When messages are consumed from the channel, registered handlers
            are invoked with the message name and payload. Multiple handlers
            can be registered for the same channel. The handler can be either
            a synchronous or asynchronous function.

        Args:
            channel_name (str): The Redis stream channel name to monitor.
            handler_func (Callable): The handler function to invoke for messages.
                Must accept 'name' and 'payload' keyword arguments. Can be
                either a regular function or an async coroutine function.
            listener_name (Optional[str], optional): The listener name to associate
                with this handler. If not provided, uses the instance's listener_name.

        Returns:
            CommonMethods: Returns self for method chaining.
        """
        listener = listener_name or self.listener_name
        self._handlers[(channel_name, listener)].append(handler_func)
        footprint.leave(
            log_type="debug",
            subject="Handler registered",
            controller=f"{__name__}.AsyncRedisStreamer.register_handler",
            message=f"Handler '{handler_func.__name__}' registered for channel '{channel_name}'.",
            payload={
                "channel_name": channel_name,
                "handler_name": handler_func.__name__,
                "listener_name": listener,
            },
        )
        return self
