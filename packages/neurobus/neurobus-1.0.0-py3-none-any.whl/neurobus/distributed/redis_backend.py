"""
Redis backend for distributed event bus.

Provides Redis-based event broadcasting, distributed subscriptions,
and cluster coordination.
"""

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class RedisBackend:
    """
    Redis-based backend for distributed event bus.

    Provides pub/sub messaging, distributed state, and cluster coordination
    using Redis as the backend.

    Features:
    - Event broadcasting across nodes
    - Distributed subscriptions
    - Node registration and discovery
    - Health checking with heartbeats
    - Leader election support
    - Event deduplication

    Example:
        >>> backend = RedisBackend("redis://localhost:6379")
        >>> await backend.connect()
        >>>
        >>> # Publish event to cluster
        >>> await backend.publish_event("user.login", event_data)
        >>>
        >>> # Subscribe to events
        >>> await backend.subscribe_pattern("user.*", handler)
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        node_id: str | None = None,
        channel_prefix: str = "neurobus",
        heartbeat_interval: int = 5,
        node_timeout: int = 15,
    ) -> None:
        """
        Initialize Redis backend.

        Args:
            redis_url: Redis connection URL
            node_id: Unique node identifier (auto-generated if None)
            channel_prefix: Prefix for Redis channels
            heartbeat_interval: Heartbeat interval in seconds
            node_timeout: Node timeout in seconds
        """
        self.redis_url = redis_url
        self.node_id = node_id or str(uuid4())
        self.channel_prefix = channel_prefix
        self.heartbeat_interval = heartbeat_interval
        self.node_timeout = node_timeout

        # Redis clients
        self._redis: Any = None
        self._pubsub: Any = None

        # Connection state
        self._connected = False
        self._subscriptions: dict[str, Callable] = {}

        # Background tasks
        self._heartbeat_task: asyncio.Task | None = None
        self._subscriber_task: asyncio.Task | None = None

        # Statistics
        self._stats = {
            "events_published": 0,
            "events_received": 0,
            "heartbeats_sent": 0,
            "nodes_discovered": 0,
        }

        logger.info(f"RedisBackend initialized (node_id={self.node_id}, " f"url={redis_url})")

    async def connect(self) -> None:
        """Connect to Redis."""
        if self._connected:
            return

        try:
            import redis.asyncio as aioredis

            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )

            self._pubsub = self._redis.pubsub()

            # Register this node
            await self._register_node()

            # Start background tasks
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._subscriber_task = asyncio.create_task(self._subscription_loop())

            self._connected = True
            logger.info(f"Connected to Redis at {self.redis_url}")

        except ImportError:
            raise ImportError("redis package not installed. " "Install with: pip install redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if not self._connected:
            return

        # Stop background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass

        # Unregister node
        await self._unregister_node()

        # Close connections
        if self._pubsub:
            await self._pubsub.close()

        if self._redis:
            await self._redis.close()

        self._connected = False
        logger.info("Disconnected from Redis")

    async def publish_event(
        self,
        topic: str,
        event_data: dict[str, Any],
    ) -> int:
        """
        Publish event to distributed cluster.

        Args:
            topic: Event topic
            event_data: Event data dictionary

        Returns:
            Number of subscribers that received the event
        """
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        # Create message
        message = {
            "node_id": self.node_id,
            "topic": topic,
            "data": event_data,
        }

        # Publish to Redis channel
        channel = f"{self.channel_prefix}:events:{topic}"

        try:
            receivers = await self._redis.publish(channel, json.dumps(message))

            self._stats["events_published"] += 1

            return receivers

        except Exception as e:
            logger.error(f"Failed to publish event: {e}", exc_info=True)
            raise

    async def subscribe_pattern(
        self,
        pattern: str,
        handler: Callable[[dict[str, Any]], Any],
    ) -> None:
        """
        Subscribe to event pattern.

        Args:
            pattern: Topic pattern (supports * wildcard)
            handler: Callback function for received events
        """
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        # Convert pattern to Redis pattern
        redis_pattern = f"{self.channel_prefix}:events:{pattern}"

        # Store subscription
        self._subscriptions[redis_pattern] = handler

        # Subscribe in Redis
        await self._pubsub.psubscribe(redis_pattern)

        logger.info(f"Subscribed to pattern: {pattern}")

    async def unsubscribe_pattern(self, pattern: str) -> None:
        """
        Unsubscribe from pattern.

        Args:
            pattern: Topic pattern to unsubscribe from
        """
        if not self._connected:
            return

        redis_pattern = f"{self.channel_prefix}:events:{pattern}"

        if redis_pattern in self._subscriptions:
            del self._subscriptions[redis_pattern]
            await self._pubsub.punsubscribe(redis_pattern)
            logger.info(f"Unsubscribed from pattern: {pattern}")

    async def get_cluster_nodes(self) -> list[dict[str, Any]]:
        """
        Get list of active cluster nodes.

        Returns:
            List of node information dictionaries
        """
        if not self._connected:
            raise RuntimeError("Not connected to Redis")

        nodes = []
        pattern = f"{self.channel_prefix}:node:*"

        try:
            keys = await self._redis.keys(pattern)

            for key in keys:
                node_data = await self._redis.get(key)
                if node_data:
                    nodes.append(json.loads(node_data))

            self._stats["nodes_discovered"] = len(nodes)
            return nodes

        except Exception as e:
            logger.error(f"Failed to get cluster nodes: {e}", exc_info=True)
            return []

    async def is_leader(self) -> bool:
        """
        Check if this node is the cluster leader.

        Uses Redis SET NX for simple leader election.

        Returns:
            True if this node is the leader
        """
        if not self._connected:
            return False

        leader_key = f"{self.channel_prefix}:leader"

        try:
            # Try to acquire leadership
            acquired = await self._redis.set(
                leader_key,
                self.node_id,
                nx=True,
                ex=self.node_timeout,
            )

            if acquired:
                return True

            # Check if we're the current leader
            current_leader = await self._redis.get(leader_key)
            return current_leader == self.node_id

        except Exception as e:
            logger.error(f"Leader election error: {e}", exc_info=True)
            return False

    async def acquire_lock(
        self,
        resource: str,
        timeout: int = 10,
    ) -> bool:
        """
        Acquire distributed lock.

        Args:
            resource: Resource identifier
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired
        """
        if not self._connected:
            return False

        lock_key = f"{self.channel_prefix}:lock:{resource}"

        try:
            acquired = await self._redis.set(
                lock_key,
                self.node_id,
                nx=True,
                ex=timeout,
            )

            return bool(acquired)

        except Exception as e:
            logger.error(f"Lock acquisition error: {e}", exc_info=True)
            return False

    async def release_lock(self, resource: str) -> bool:
        """
        Release distributed lock.

        Args:
            resource: Resource identifier

        Returns:
            True if lock released
        """
        if not self._connected:
            return False

        lock_key = f"{self.channel_prefix}:lock:{resource}"

        try:
            # Only release if we own the lock
            current = await self._redis.get(lock_key)
            if current == self.node_id:
                await self._redis.delete(lock_key)
                return True
            return False

        except Exception as e:
            logger.error(f"Lock release error: {e}", exc_info=True)
            return False

    async def _register_node(self) -> None:
        """Register this node in the cluster."""
        node_key = f"{self.channel_prefix}:node:{self.node_id}"

        node_info = {
            "node_id": self.node_id,
            "registered_at": asyncio.get_event_loop().time(),
            "redis_url": self.redis_url,
        }

        await self._redis.set(
            node_key,
            json.dumps(node_info),
            ex=self.node_timeout,
        )

        logger.info(f"Node registered: {self.node_id}")

    async def _unregister_node(self) -> None:
        """Unregister this node from the cluster."""
        node_key = f"{self.channel_prefix}:node:{self.node_id}"

        try:
            await self._redis.delete(node_key)
            logger.info(f"Node unregistered: {self.node_id}")
        except Exception as e:
            logger.error(f"Failed to unregister node: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task for sending heartbeats."""
        logger.info("Heartbeat loop started")

        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                # Refresh node registration
                await self._register_node()
                self._stats["heartbeats_sent"] += 1

            except asyncio.CancelledError:
                logger.info("Heartbeat loop stopped")
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", exc_info=True)

    async def _subscription_loop(self) -> None:
        """Background task for handling subscriptions."""
        logger.info("Subscription loop started")

        try:
            async for message in self._pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        # Parse message
                        pattern = message["pattern"]
                        data = json.loads(message["data"])

                        # Skip messages from self
                        if data.get("node_id") == self.node_id:
                            continue

                        # Call handler
                        handler = self._subscriptions.get(pattern)
                        if handler:
                            if asyncio.iscoroutinefunction(handler):
                                await handler(data)
                            else:
                                handler(data)

                            self._stats["events_received"] += 1

                    except Exception as e:
                        logger.error(f"Subscription handler error: {e}", exc_info=True)

        except asyncio.CancelledError:
            logger.info("Subscription loop stopped")
        except Exception as e:
            logger.error(f"Subscription loop error: {e}", exc_info=True)

    def get_stats(self) -> dict[str, Any]:
        """
        Get backend statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "node_id": self.node_id,
            "connected": self._connected,
            "redis_url": self.redis_url,
            "events_published": self._stats["events_published"],
            "events_received": self._stats["events_received"],
            "heartbeats_sent": self._stats["heartbeats_sent"],
            "nodes_discovered": self._stats["nodes_discovered"],
            "active_subscriptions": len(self._subscriptions),
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"RedisBackend(" f"node_id={self.node_id}, " f"connected={self._connected})"
