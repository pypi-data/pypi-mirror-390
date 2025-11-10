"""
Cluster manager for distributed NeuroBUS.

Coordinates multiple event bus nodes for horizontal scaling.
"""

import asyncio
import logging
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.distributed.redis_backend import RedisBackend
from neurobus.utils.serialization import deserialize, serialize

logger = logging.getLogger(__name__)


class ClusterManager:
    """
    Manages distributed NeuroBUS cluster.

    Coordinates multiple nodes, handles event broadcasting,
    distributed subscriptions, and cluster health monitoring.

    Features:
    - Multi-node event broadcasting
    - Distributed subscription management
    - Node discovery and health checking
    - Leader election
    - Event deduplication
    - Cluster-wide statistics

    Example:
        >>> cluster = ClusterManager(redis_url="redis://localhost:6379")
        >>> await cluster.start()
        >>>
        >>> # Broadcast event to all nodes
        >>> await cluster.broadcast_event(event)
        >>>
        >>> # Get cluster status
        >>> nodes = await cluster.get_active_nodes()
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        node_id: str | None = None,
        enable_deduplication: bool = True,
        dedup_window: int = 60,
    ) -> None:
        """
        Initialize cluster manager.

        Args:
            redis_url: Redis connection URL
            node_id: Optional node identifier
            enable_deduplication: Enable event deduplication
            dedup_window: Deduplication window in seconds
        """
        self.redis_url = redis_url
        self.enable_deduplication = enable_deduplication
        self.dedup_window = dedup_window

        # Redis backend
        self.backend = RedisBackend(
            redis_url=redis_url,
            node_id=node_id,
        )

        # Event handlers
        self._event_handlers: list[Any] = []

        # Deduplication cache
        self._seen_events: set[str] = set()
        self._dedup_task: asyncio.Task | None = None

        # State
        self._running = False

        logger.info(f"ClusterManager initialized (node_id={self.backend.node_id})")

    @property
    def node_id(self) -> str:
        """Get this node's ID."""
        return self.backend.node_id

    @property
    def is_running(self) -> bool:
        """Check if cluster manager is running."""
        return self._running

    async def start(self) -> None:
        """Start cluster manager."""
        if self._running:
            return

        # Connect to Redis
        await self.backend.connect()

        # Subscribe to all events
        await self.backend.subscribe_pattern("*", self._handle_cluster_event)

        # Start deduplication cleanup if enabled
        if self.enable_deduplication:
            self._dedup_task = asyncio.create_task(self._dedup_cleanup_loop())

        self._running = True
        logger.info("ClusterManager started")

    async def stop(self) -> None:
        """Stop cluster manager."""
        if not self._running:
            return

        # Stop deduplication task
        if self._dedup_task:
            self._dedup_task.cancel()
            try:
                await self._dedup_task
            except asyncio.CancelledError:
                pass

        # Disconnect from Redis
        await self.backend.disconnect()

        self._running = False
        logger.info("ClusterManager stopped")

    async def broadcast_event(self, event: Event) -> int:
        """
        Broadcast event to all cluster nodes.

        Args:
            event: Event to broadcast

        Returns:
            Number of nodes that received the event
        """
        if not self._running:
            raise RuntimeError("Cluster manager not running")

        # Check for duplicate
        if self.enable_deduplication:
            event_key = f"{event.id}"
            if event_key in self._seen_events:
                logger.debug(f"Skipping duplicate event: {event.id}")
                return 0

            self._seen_events.add(event_key)

        # Serialize event
        event_data = {
            "id": str(event.id),
            "topic": event.topic,
            "data": serialize(event.data).hex(),
            "timestamp": event.timestamp.isoformat(),
            "context": serialize(event.context).hex() if event.context else None,
            "metadata": serialize(event.metadata).hex() if event.metadata else None,
            "parent_id": str(event.parent_id) if event.parent_id else None,
        }

        # Broadcast via Redis
        receivers = await self.backend.publish_event(event.topic, event_data)

        logger.debug(f"Broadcast event {event.id} to {receivers} nodes")

        return receivers

    def register_event_handler(self, handler: Any) -> None:
        """
        Register handler for cluster events.

        Args:
            handler: Async function to handle received events
        """
        self._event_handlers.append(handler)
        logger.debug(f"Registered event handler: {handler.__name__}")

    def unregister_event_handler(self, handler: Any) -> None:
        """
        Unregister event handler.

        Args:
            handler: Handler to remove
        """
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)
            logger.debug(f"Unregistered event handler: {handler.__name__}")

    async def _handle_cluster_event(self, message: dict[str, Any]) -> None:
        """Handle event received from cluster."""
        try:
            # Deserialize event
            event_data = message.get("data", {})

            event = Event(
                id=UUID(event_data["id"]),
                topic=event_data["topic"],
                data=deserialize(bytes.fromhex(event_data["data"])),
                timestamp=event_data.get("timestamp"),
                context=(
                    deserialize(bytes.fromhex(event_data["context"]))
                    if event_data.get("context")
                    else {}
                ),
                metadata=(
                    deserialize(bytes.fromhex(event_data["metadata"]))
                    if event_data.get("metadata")
                    else {}
                ),
                parent_id=UUID(event_data["parent_id"]) if event_data.get("parent_id") else None,
            )

            # Check for duplicate
            if self.enable_deduplication:
                event_key = f"{event.id}"
                if event_key in self._seen_events:
                    return

                self._seen_events.add(event_key)

            # Call handlers
            for handler in self._event_handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Event handler error: {e}", exc_info=True)

        except Exception as e:
            logger.error(f"Failed to handle cluster event: {e}", exc_info=True)

    async def get_active_nodes(self) -> list[dict[str, Any]]:
        """
        Get list of active cluster nodes.

        Returns:
            List of node information
        """
        if not self._running:
            return []

        return await self.backend.get_cluster_nodes()

    async def is_leader(self) -> bool:
        """
        Check if this node is the cluster leader.

        Returns:
            True if this node is the leader
        """
        if not self._running:
            return False

        return await self.backend.is_leader()

    async def acquire_lock(self, resource: str, timeout: int = 10) -> bool:
        """
        Acquire distributed lock.

        Args:
            resource: Resource identifier
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired
        """
        if not self._running:
            return False

        return await self.backend.acquire_lock(resource, timeout)

    async def release_lock(self, resource: str) -> bool:
        """
        Release distributed lock.

        Args:
            resource: Resource identifier

        Returns:
            True if lock released
        """
        if not self._running:
            return False

        return await self.backend.release_lock(resource)

    async def _dedup_cleanup_loop(self) -> None:
        """Background task to clean up deduplication cache."""
        logger.info("Deduplication cleanup loop started")

        while True:
            try:
                await asyncio.sleep(self.dedup_window)

                # Clear old entries
                self._seen_events.clear()
                logger.debug("Deduplication cache cleared")

            except asyncio.CancelledError:
                logger.info("Deduplication cleanup loop stopped")
                break
            except Exception as e:
                logger.error(f"Deduplication cleanup error: {e}", exc_info=True)

    def get_stats(self) -> dict[str, Any]:
        """
        Get cluster statistics.

        Returns:
            Dictionary with cluster statistics
        """
        backend_stats = self.backend.get_stats()

        return {
            "node_id": self.node_id,
            "running": self._running,
            "redis_url": self.redis_url,
            "enable_deduplication": self.enable_deduplication,
            "seen_events": len(self._seen_events),
            "event_handlers": len(self._event_handlers),
            "backend": backend_stats,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"ClusterManager(" f"node_id={self.node_id}, " f"running={self._running})"
