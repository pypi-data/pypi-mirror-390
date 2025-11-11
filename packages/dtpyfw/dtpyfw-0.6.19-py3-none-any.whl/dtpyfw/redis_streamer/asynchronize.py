import asyncio
import json
import time
from typing import Any, Dict, Optional, Self

from redis.asyncio import Redis as AsyncRedis

from ..core.exception import exception_to_dict
from ..core.retry import retry_wrapper
from ..log import footprint
from ..redis.connection import RedisInstance
from .common import REDIS_EXCEPTIONS, CommonMethods
from .message import Message


class AsyncRedisStreamer(CommonMethods):
    """
    Asynchronous Redis Streams consumer with:
      - Decoupled fan-out across microservices (one group per service).
      - Bounded at-most-once (per group) via a ZSET de-dup window.
      - Lower network load using adaptive sleeping.
      - Connection pooling for efficient connection reuse.
    """

    def __init__(
        self,
        redis_instance: RedisInstance,
        consumer_name: str,
        dedup_window_ms: int = 7 * 24 * 60 * 60 * 1000,
    ):
        """Initialize asynchronous Redis Streams consumer.

        Description:
            Sets up an async consumer with connection pooling and background
            maintenance tasks for deduplication and cleanup operations.

        Args:
            redis_instance (RedisInstance): The Redis connection manager.
            consumer_name (str): The logical name of the consumer service.
            dedup_window_ms (int, optional): Time window in milliseconds for
                deduplication tracking. Defaults to 7 days (604800000 ms).
        """
        super().__init__(redis_instance, consumer_name, dedup_window_ms)

        self._redis_client: Optional[AsyncRedis] = None
        self._maintenance_task: Optional[asyncio.Task] = None
        self._cleanup_channels_task: Optional[asyncio.Task] = None

    async def _reconnect(self) -> None:
        """Attempt to reconnect to Redis with exponential backoff retries.

        Description:
            Handles Redis connection failures by closing the existing client,
            resetting the connection pool, and attempting to reconnect up to
            3 times with exponential backoff delays between attempts. This
            method ensures resilience in the face of transient network issues
            or Redis server restarts.

        Raises:
            ConnectionError: If reconnection fails after 3 attempts.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._reconnect"

        for attempt in range(3):
            try:
                footprint.leave(
                    log_type="debug",
                    subject="Attempting to reconnect to Redis",
                    message=f"Attempt {attempt + 1} of 3",
                    controller=controller,
                )
                if self._redis_client is not None:
                    await self._redis_client.close()
                self._redis_client = None
                await self._redis_instance.reset_async_pool()
                client = await self._get_client()
                if await client.ping():
                    footprint.leave(
                        log_type="debug",
                        subject="Successfully reconnected to Redis",
                        controller=controller,
                        message=f"Successfully reconnected to Redis (attempt {attempt + 1} of 3)",
                    )
                    return
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="warning",
                    subject="Redis reconnection attempt failed",
                    message=f"Attempt {attempt + 1} failed.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )
                await asyncio.sleep(2**attempt)  # Exponential backoff

        footprint.leave(
            log_type="error",
            subject="Failed to reconnect to Redis after 3 attempts",
            controller=controller,
            message="Failed to reconnect to Redis",
        )
        raise ConnectionError("Failed to reconnect to Redis after 3 attempts")

    async def _get_client(self) -> AsyncRedis:
        """Lazily initialize and return the async Redis client.

        Description:
            Retrieves the async Redis client, initializing it on first access.
            Subsequent calls return the existing client instance.

        Returns:
            AsyncRedis: The async Redis client instance.
        """
        if self._redis_client is None:
            self._redis_client = await self._redis_instance.get_async_redis_client()
        return self._redis_client

    @retry_wrapper()
    async def _consumer_group_exists(
        self, channel_name: str, consumer_group: str
    ) -> bool:
        """Check if a consumer group exists for a channel.

        Description:
            Queries Redis to determine if the specified consumer group has
            been created for the given stream channel.

        Args:
            channel_name (str): The Redis stream channel name.
            consumer_group (str): The consumer group identifier.

        Returns:
            bool: True if the consumer group exists, False otherwise.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.
        """
        controller = f"{__name__}.AsyncRedisStreamer._consumer_group_exists"
        try:
            client = await self._get_client()
            groups = await client.xinfo_groups(channel_name)
            return any(
                group["name"].decode("utf-8") == consumer_group for group in groups
            )
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Checking consumer group existence",
                message=f"Error checking existence of consumer group {consumer_group} on channel {channel_name}.",
                payload=exception_to_dict(e),
            )
            await self._reconnect()
            raise e
        except Exception:
            return False

    @retry_wrapper()
    async def send_message(self, channel: str, message: Message) -> None:
        """Send a message to a Redis stream channel asynchronously.

        Description:
            Publishes a message to the specified channel using Redis XADD.
            The message is JSON-encoded before transmission. This method
            supports async/await patterns for non-blocking I/O operations.

        Args:
            channel (str): The Redis stream channel name where the message
                will be published.
            message (Message): The message object to send containing the
                event name and payload data.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer.send_message"
        try:
            footprint.leave(
                log_type="debug",
                subject="Sending single message asynchronously",
                controller=controller,
                message=f"Sending message to channel '{channel}' asynchronously.",
                payload={"channel": channel, "message_name": message.name},
            )
            client = await self._get_client()
            fields = message.get_json_encoded()
            await client.xadd(channel, fields)  # type: ignore[arg-type]
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Message sent",
                message=f"Message sent to channel '{channel}'.",
                payload={"channel": channel, "message_name": message.name},
            )
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Error sending message",
                message=f"Error sending message to channel {channel}.",
                payload=exception_to_dict(e),
            )
            await self._reconnect()
            raise e

    @retry_wrapper()
    async def subscribe(
        self, channel_name: str, start_from_latest: bool = True
    ) -> "Self":
        """Subscribe to a Redis stream channel asynchronously.

        Description:
            Creates a consumer group for the channel if it doesn't exist and
            registers the subscription for later message consumption. The
            consumer group enables decoupled fan-out across microservices,
            allowing multiple services to independently process all messages
            from the stream.

        Args:
            channel_name (str): The Redis stream channel name to subscribe to.
            start_from_latest (bool, optional): If True, start consuming from
                new messages only ($). If False, consume from beginning (0-0).
                Defaults to True.

        Returns:
            AsyncRedisStreamer: Returns self for method chaining.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.
        """
        controller = f"{__name__}.AsyncRedisStreamer.subscribe"
        listener_name = self.listener_name
        group = self._group_name(channel_name, listener_name)

        if not await self._consumer_group_exists(channel_name, group):
            try:
                start_id = "$" if start_from_latest else "0-0"
                client = await self._get_client()
                await client.xgroup_create(channel_name, group, start_id, mkstream=True)
                footprint.leave(
                    log_type="debug",
                    subject="Subscription created",
                    message=f"Listener {listener_name} has been subscribed to {channel_name}.",
                    controller=controller,
                    payload={
                        "channel": channel_name,
                        "group": group,
                        "listener": listener_name,
                        "start_from_latest": start_from_latest,
                    },
                )
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="debug",
                    controller=controller,
                    subject="Checking consumer group existence",
                    message=f"Error creating consumer group {group} for channel {channel_name}.",
                    payload=exception_to_dict(e),
                )
                await self._reconnect()
                raise e
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Error creating consumer group",
                    message=f"Error creating consumer group {group} for channel {channel_name}.",
                    controller=controller,
                    payload=exception_to_dict(e),
                )

        self._subscriptions.append((channel_name, listener_name, group))
        return self

    @retry_wrapper()
    async def _reserve_once(
        self, processed_key: str, message_id: str, now_ms: int
    ) -> bool:
        """Attempt to reserve a message ID for processing using ZSET.

        Description:
            Uses Redis ZADD with NX flag to atomically reserve a message ID
            for processing. This ensures at-most-once delivery within the
            consumer group by preventing duplicate processing.

        Args:
            processed_key (str): The Redis ZSET key for tracking processed messages.
            message_id (str): The Redis stream message ID to reserve.
            now_ms (int): Current timestamp in milliseconds for the ZSET score.

        Returns:
            bool: True if the message was successfully reserved, False if already processed.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.
        """
        controller = f"{__name__}.AsyncRedisStreamer._reserve_once"
        try:
            client = await self._get_client()
            added = await client.zadd(processed_key, {message_id: now_ms}, nx=True)
            result = added == 1
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Message reservation",
                message="Message reservation attempt completed.",
                payload={
                    "result": result,
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            return result
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Error reserving message",
                message=f"Error reserving message {message_id} on key {processed_key}.",
                payload=exception_to_dict(e),
            )
            await self._reconnect()
            raise e
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Dedup error",
                controller=f"{__name__}.AsyncRedisStreamer._reserve_once",
                message="ZADD NX failed; skipping message to avoid duplicate processing.",
                payload={
                    "error": exception_to_dict(e),
                    "message_id": message_id,
                    "key": processed_key,
                },
            )
            return False

    @retry_wrapper()
    async def _ack_message(self, channel: str, group: str, message_id: str) -> None:
        """Acknowledge a message as processed in Redis stream.

        Description:
            Sends an XACK command to Redis to mark the message as successfully
            processed by the consumer group. This prevents the message from
            being redelivered to other consumers in the group and maintains
            proper message tracking for the consumer group.

        Args:
            channel (str): The Redis stream channel name containing the message.
            group (str): The consumer group identifier that processed the message.
            message_id (str): The Redis stream message ID to acknowledge.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._ack_message"
        try:
            client = await self._get_client()
            await client.xack(channel, group, message_id)
            footprint.leave(
                log_type="debug",
                controller=controller,
                subject="Ack message",
                message="Message acknowledged successfully.",
                payload={
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                subject="Error acknowledging message",
                controller=controller,
                message=f"Ack error for message {message_id} on channel {channel}, group {group}.",
                payload=exception_to_dict(e),
            )
            await self._reconnect()
            raise e
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Ack error",
                controller=controller,
                message="XACK failed.",
                payload={
                    "error": exception_to_dict(e),
                    "channel": channel,
                    "group": group,
                    "message_id": message_id,
                },
            )

    @retry_wrapper()
    async def _consume_one(
        self,
        channel: str,
        consumer_group: str,
        listener_name: str,
        block_time: float,
        count: int = 32,
    ) -> None:
        """Consume and process a batch of messages from a Redis stream.

        Description:
            Reads a batch of messages from the stream using XREADGROUP,
            deduplicates them using ZSET-based tracking, decodes their payloads,
            invokes registered handlers, and acknowledges successful processing.
            Handles errors by logging to dead letter and re-subscribing if needed.
            Supports both async and sync handler functions.

        Args:
            channel (str): The Redis stream channel name to consume from.
            consumer_group (str): The consumer group identifier for this consumer.
            listener_name (str): The logical consumer service name for routing.
            block_time (float): Maximum seconds to block waiting for messages.
            count (int, optional): Maximum messages to read per batch. Defaults to 32.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._consume_one"

        try:
            client = await self._get_client()
            msgs = await client.xreadgroup(
                groupname=consumer_group,
                consumername=self.consumer_instance_name,
                streams={channel: ">"},
                block=int(block_time * 1000),
                count=count,
            )
            if not msgs:
                return

            _, batch = msgs[0]
            processed_key = self._processed_zset_key(channel, consumer_group)
            now_ms = self._server_now_ms()

            for message_id, fields in batch:
                reserved = await self._reserve_once(processed_key, message_id, now_ms)
                if not reserved:
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                try:
                    raw_name = fields.get(b"name")
                    raw_body = fields.get(b"body")
                    if raw_name is None or raw_body is None:
                        raise ValueError("Missing name or body")
                    name = raw_name.decode("utf-8")
                    body = json.loads(raw_body.decode("utf-8"))
                except Exception as e:
                    self._dead_letter(
                        channel,
                        "decode/schema",
                        message_id,
                        {"listener": listener_name, "error": str(e)},
                    )
                    await self._ack_message(channel, consumer_group, message_id)
                    continue

                for handler in self._handlers.get((channel, listener_name), []):
                    try:
                        footprint.leave(
                            log_type="debug",
                            subject="Invoking handler",
                            controller=controller,
                            message=f"Invoking message {name} handler.",
                            payload={
                                "listener": listener_name,
                                "name": name,
                                "body": body,
                            },
                        )

                        import inspect

                        if inspect.iscoroutinefunction(handler):
                            await handler(name=name, payload=body)
                        else:
                            handler(name=name, payload=body)

                        footprint.leave(
                            log_type="debug",
                            subject="Handler invoked",
                            controller=controller,
                            message=f"Handler for message {name} invoked successfully.",
                            payload={
                                "listener": listener_name,
                                "name": name,
                            },
                        )
                    except Exception as e:
                        self._dead_letter(
                            channel,
                            "handler",
                            message_id,
                            {
                                "listener": listener_name,
                                "handler": handler.__name__,
                                "error": str(e),
                                "name": name,
                            },
                        )
                        break

                await self._ack_message(channel, consumer_group, message_id)

        except REDIS_EXCEPTIONS as e:
            await self._reconnect()
            raise e
        except Exception as e:
            if "NOGROUP" in str(e):
                try:
                    footprint.leave(
                        log_type="warning",
                        subject=f"Need to resubscribe to channel {channel}",
                        message=f"Trying to resubscribe to {channel}.",
                        controller=controller,
                        payload={
                            "listener_name": listener_name,
                            "channel": channel,
                            "consumer_group": consumer_group,
                            "error": exception_to_dict(e),
                        },
                    )
                    await self.subscribe(channel_name=channel)
                except REDIS_EXCEPTIONS as e_resub:
                    footprint.leave(
                        log_type="debug",
                        message=f"Error resubscribing to channel {channel}",
                        controller=controller,
                        subject="Resubscribing Error",
                        payload={
                            "error": exception_to_dict(e_resub),
                            "group": consumer_group,
                            "listener": listener_name,
                        },
                    )
                    await self._reconnect()
                except Exception as e_resub:
                    footprint.leave(
                        log_type="error",
                        message=f"Error resubscribing to channel {channel}",
                        controller=controller,
                        subject="Resubscribing Error",
                        payload={
                            "error": exception_to_dict(e_resub),
                            "group": consumer_group,
                            "listener": listener_name,
                        },
                    )
            else:
                footprint.leave(
                    log_type="error",
                    message=f"Error consuming messages from channel {channel}",
                    controller=controller,
                    subject="Consuming Messages Error",
                    payload={
                        "error": exception_to_dict(e),
                        "group": consumer_group,
                        "listener": listener_name,
                    },
                )

    async def _consume_loop(
        self,
        channel: str,
        listener: str,
        group: str,
        block_time: float,
        count: int,
        rest_time: float,
    ) -> None:
        """Dedicated async loop for consuming messages from a channel.

        Description:
            Continuously polls the channel for new messages, processes them,
            and implements adaptive sleep with exponential backoff during
            idle periods to reduce network load. Handles reconnections on errors.
            Runs indefinitely until the task is cancelled or the application exits.

        Args:
            channel (str): The Redis stream channel name to monitor.
            listener (str): The logical consumer service name for this consumer.
            group (str): The consumer group identifier for coordination.
            block_time (float): Maximum seconds to block waiting for messages.
            count (int): Maximum messages to read per batch.
            rest_time (float): Base sleep duration in seconds between consume cycles.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._consume_loop"

        footprint.leave(
            log_type="info",
            message=f"Launching {channel} async consumer task",
            controller=controller,
            subject="Async Redis consumer",
            payload={
                "channel": channel,
                "listener": listener,
                "group": group,
            },
        )

        idle_backoff = rest_time

        while True:
            try:
                before = time.time()
                await self._consume_one(channel, group, listener, block_time, count)
                elapsed = time.time() - before

                if elapsed < block_time:
                    idle_backoff = min(idle_backoff * 2, 2.0)
                else:
                    idle_backoff = rest_time

                await asyncio.sleep(idle_backoff)

            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="debug",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                await self._reconnect()
                await asyncio.sleep(5)
            except Exception as e:
                footprint.leave(
                    log_type="warning",
                    subject="Consumer loop error",
                    controller=controller,
                    message=f"Error in consumer loop for channel {channel}. Restarting loop.",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )
                await asyncio.sleep(5)

    async def persist_consume(
        self,
        rest_time: float = 0.1,
        block_time: float = 5.0,
        count: int = 32,
        cleanup_interval: float = 300.0,
    ) -> None:
        """Continuously consume messages from all subscribed channels
        asynchronously.

        Description:
            Launches consumer tasks for each subscribed channel, starts
            background maintenance tasks for deduplication cleanup and
            channel retention, and monitors task health. Automatically
            restarts crashed tasks to ensure continuous operation. This
            is the main entry point for starting message consumption.

        Args:
            rest_time (float, optional): Base sleep duration in seconds between
                consume cycles during idle periods. Defaults to 0.1.
            block_time (float, optional): Maximum seconds to block waiting for
                messages in each XREADGROUP call. Defaults to 5.0.
            count (int, optional): Maximum messages to read per batch from
                each channel. Defaults to 32.
            cleanup_interval (float, optional): Seconds between channel cleanup
                runs for retention management. Defaults to 300.0 (5 minutes).

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer.persist_consume"

        if self._maintenance_task is None or self._maintenance_task.done():
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())

        if self._channel_retention and (
            self._cleanup_channels_task is None or self._cleanup_channels_task.done()
        ):
            self._cleanup_channels_task = asyncio.create_task(
                self._cleanup_channels_loop(cleanup_interval)
            )

        tasks = {}
        for channel, listener, group in self._subscriptions:
            task_args = (channel, listener, group, block_time, count, rest_time)
            task = asyncio.create_task(self._consume_loop(*task_args))
            tasks[(channel, listener, group)] = (task, task_args)

        while True:
            for key, (task, args) in list(tasks.items()):
                if task.done():
                    try:
                        await task
                    except Exception as e:
                        footprint.leave(
                            log_type="warning",
                            subject="Consumer task died",
                            controller=controller,
                            message=f"Consumer task for channel {key[0]} died. Restarting.",
                            payload={
                                "channel": key[0],
                                "listener": key[1],
                                "error": exception_to_dict(e),
                            },
                        )
                    else:
                        footprint.leave(
                            log_type="warning",
                            subject="Consumer task finished unexpectedly",
                            controller=controller,
                            message=f"Consumer task for channel {key[0]} finished. Restarting.",
                            payload={"channel": key[0], "listener": key[1]},
                        )

                    new_task = asyncio.create_task(self._consume_loop(*args))
                    tasks[key] = (new_task, args)

            await asyncio.sleep(60)

    @retry_wrapper()
    async def maintain_ledgers(self) -> None:
        """Clean up expired deduplication ZSET entries asynchronously.

        Description:
            Removes message IDs from the deduplication ZSETs that have
            exceeded the configured deduplication window. This prevents
            unbounded memory growth while maintaining at-most-once guarantees
            within the window. Runs periodically as part of the maintenance loop.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer.maintain_ledgers"
        now_ms = self._server_now_ms()
        cutoff = now_ms - self._dedup_window_ms

        client = await self._get_client()

        for channel_name, _, consumer_group in self._subscriptions:
            try:
                key = self._processed_zset_key(channel_name, consumer_group)
                removed = await client.zremrangebyscore(
                    key, min="-inf", max=f"({cutoff}"
                )
            except REDIS_EXCEPTIONS as e:
                await self._reconnect()
                raise e

            if removed:
                footprint.leave(
                    log_type="info",
                    message=f"Purged {removed} dedup entries",
                    controller=controller,
                    subject="Dedup ledger maintenance",
                    payload={"key": key, "removed": removed},
                )

    async def _maintenance_loop(self) -> None:
        """Background async task for periodic deduplication maintenance.

        Description:
            Runs continuously, sleeping for the configured interval and
            then triggering ledger cleanup to remove expired deduplication
            entries. Handles errors gracefully with reconnection attempts.
            This task runs in the background for the lifetime of the consumer.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._maintenance_loop"

        while True:
            try:
                await self.maintain_ledgers()
                self._last_ledger_cleanup = self._server_now_ms()
            except REDIS_EXCEPTIONS as e:
                footprint.leave(
                    log_type="debug",
                    subject="Maintenance loop error",
                    controller=controller,
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                await self._reconnect()
                await asyncio.sleep(60)
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Maintenance loop error",
                    controller=controller,
                    message="Error in maintenance loop",
                    payload={"error": exception_to_dict(e)},
                )
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(self._ledger_cleanup_interval / 1000)

    @retry_wrapper()
    async def cleanup_channels(self) -> None:
        """Clean up old messages from channels based on retention period.

        Description:
            For each registered channel with a retention configuration,
            removes messages older than the retention window using XTRIM.
            This helps manage memory usage for high-throughput channels by
            preventing unbounded growth of stream data.

        Raises:
            Exception: Re-raises Redis exceptions after reconnection attempt.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer.cleanup_channels"
        now_ms = self._server_now_ms()

        client = await self._get_client()
        for channel, retention in self._channel_retention.items():
            if retention is None:
                continue

            try:
                cutoff = now_ms - retention
                
                # Trim old messages from the stream based on retention
                # MINID removes all messages with ID lower than the cutoff
                trimmed_count = await client.xtrim(
                    channel, minid=cutoff, approximate=True
                )

                if trimmed_count:
                    footprint.leave(
                        log_type="info",
                        message=f"Trimmed {trimmed_count} old messages from channel {channel}",
                        controller=controller,
                        subject="Async channel cleanup",
                        payload={"channel": channel, "trimmed_count": trimmed_count},
                    )
                else:
                    footprint.leave(
                        log_type="debug",
                        message=f"No old messages to trim for channel {channel}",
                        controller=controller,
                        subject="Channel cleanup",
                        payload={"channel": channel},
                    )

            except REDIS_EXCEPTIONS as e:
                await self._reconnect()
                raise e
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async channel cleanup error",
                    controller=controller,
                    message=f"Error cleaning up channel {channel}",
                    payload={"error": exception_to_dict(e), "channel": channel},
                )

    async def _cleanup_channels_loop(self, cleanup_interval: float = 300.0) -> None:
        """Background async task for periodic channel cleanup.

        Description:
            Runs continuously, sleeping for the cleanup interval and then
            triggering channel cleanup to remove old deduplication entries
            based on retention policies. This task manages long-term memory
            usage for high-volume channels.

        Args:
            cleanup_interval (float, optional): Seconds between cleanup runs.
                Defaults to 300.0 (5 minutes).

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer._cleanup_channels_loop"

        footprint.leave(
            log_type="info",
            message="Launching channel cleanup thread",
            controller=controller,
            subject="Channel cleanup thread started",
        )
        while True:
            try:
                await self.cleanup_channels()
            except Exception as e:
                footprint.leave(
                    log_type="error",
                    subject="Async cleanup channels loop error",
                    controller=controller,
                    message="Error in async cleanup channels loop",
                    payload={"error": exception_to_dict(e)},
                )
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(cleanup_interval)

    async def cleanup(self) -> None:
        """Clean up async resources and stop all background tasks.

        Description:
            Stops all consumer tasks, maintenance tasks, and cleanup tasks,
            and closes the Redis client connection. Should be called before
            terminating the application or when using as a context manager.
            Ensures graceful shutdown of all async operations.

        Raises:
            Exception: Logs but doesn't raise exceptions during cleanup.

        Returns:
            None
        """
        try:
            await self.stop_consuming()

            footprint.leave(
                log_type="debug",
                subject="Cleanup completed",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="AsyncRedisStreamer cleanup completed",
            )
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                subject="Cleanup error",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="Error during cleanup",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Cleanup error",
                controller=f"{__name__}.AsyncRedisStreamer.cleanup",
                message="Error during cleanup",
                payload={"error": exception_to_dict(e)},
            )

    async def stop_consuming(self) -> None:
        """Stop all consuming tasks and clean up async resources.

        Description:
            Cancels and awaits completion of maintenance and cleanup tasks,
            then closes the Redis client connection. Used internally by
            cleanup() and can be called directly for graceful shutdown.
            Ensures all background tasks are properly terminated.

        Raises:
            Exception: Logs but doesn't raise exceptions during shutdown.

        Returns:
            None
        """
        controller = f"{__name__}.AsyncRedisStreamer.stop_consuming"

        footprint.leave(
            log_type="info",
            subject="Stopping consumer",
            controller=controller,
            message="Stopping all consumer tasks",
        )

        try:
            if self._maintenance_task:
                self._maintenance_task.cancel()
                await self._maintenance_task
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                subject="Error stopping maintenance task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping maintenance task",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping maintenance task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping maintenance task",
                payload={"error": exception_to_dict(e)},
            )

        try:
            if self._cleanup_channels_task:
                self._cleanup_channels_task.cancel()
                await self._cleanup_channels_task
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                subject="Error stopping cleanup channels task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping cleanup channels task",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error stopping cleanup channels task",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error stopping cleanup channels task",
                payload={"error": exception_to_dict(e)},
            )

        try:
            if self._redis_client:
                await self._redis_client.close()
                self._redis_client = None
        except REDIS_EXCEPTIONS as e:
            footprint.leave(
                log_type="debug",
                subject="Error closing Redis client",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error closing Redis client",
                payload={"error": exception_to_dict(e)},
            )
            await self._reconnect()
        except Exception as e:
            footprint.leave(
                log_type="error",
                subject="Error closing Redis client",
                controller=f"{__name__}.AsyncRedisStreamer.stop_consuming",
                message="Error closing Redis client",
                payload={"error": exception_to_dict(e)},
            )

    async def get_stats(self) -> Dict[str, Any]:
        """Get current statistics and state information about the streamer.

        Description:
            Returns a dictionary containing consumer identification,
            subscription count, channel list, configuration parameters,
            and maintenance task status. Useful for monitoring and debugging.

        Returns:
            Dict[str, Any]: Statistics including listener_name, consumer_instance,
                subscriptions count, channels list, dedup_window_ms,
                last_ledger_cleanup timestamp, and maintenance_running status.
        """
        stats = {
            "listener_name": self.listener_name,
            "consumer_instance": self.consumer_instance_name,
            "subscriptions": len(self._subscriptions),
            "channels": [sub[0] for sub in self._subscriptions],
            "dedup_window_ms": self._dedup_window_ms,
            "last_ledger_cleanup": self._last_ledger_cleanup,
        }

        if self._maintenance_task:
            stats["maintenance_running"] = not self._maintenance_task.done()

        return stats

    async def __aenter__(self) -> "Self":
        """Async context manager entry point.

        Description:
            Allows using AsyncRedisStreamer with async with statement
            for automatic resource management and cleanup. Enables the
            pattern: async with AsyncRedisStreamer(...) as streamer:

        Returns:
            AsyncRedisStreamer: Returns self for use in the async context.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        """Async context manager exit point with automatic cleanup.

        Description:
            Ensures cleanup() is called when exiting the async context,
            providing automatic resource cleanup and task cancellation.
            This guarantees proper cleanup even if exceptions occur.
            Returns False to allow exceptions to propagate normally.

        Args:
            exc_type: The exception type if an exception was raised, or None.
            exc_val: The exception value if an exception was raised, or None.
            exc_tb: The exception traceback if an exception was raised, or None.

        Returns:
            Optional[bool]: False to propagate exceptions, not suppress them.
        """
        await self.cleanup()
        return False
