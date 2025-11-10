"""
Temporal engine for event replay and time-travel.

Provides high-level API for event persistence, replay, and time-travel queries.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.temporal.store import EventStore

logger = logging.getLogger(__name__)


class TemporalEngine:
    """
    High-level temporal engine for event persistence and replay.

    Provides time-travel capabilities, event replay, and audit trail
    functionality for the event bus.

    Features:
    - Automatic event persistence
    - Event replay with filtering
    - Time-travel queries
    - Snapshot creation and restoration
    - Audit trail queries
    - Statistics tracking

    Example:
        >>> engine = TemporalEngine()
        >>> await engine.initialize()
        >>>
        >>> # Store events automatically
        >>> await engine.store_event(event)
        >>>
        >>> # Query historical events
        >>> past_events = await engine.query_past(hours=24)
        >>>
        >>> # Replay events
        >>> await engine.replay(
        ...     start_time=yesterday,
        ...     handler=lambda e: print(e.topic)
        ... )
    """

    def __init__(
        self,
        store: EventStore | None = None,
        db_path: str = "neurobus_events.db",
        max_events: int = 1000000,
        auto_persist: bool = True,
    ) -> None:
        """
        Initialize temporal engine.

        Args:
            store: Optional custom event store
            db_path: Database path (if store not provided)
            max_events: Maximum events to store
            auto_persist: Whether to automatically persist events
        """
        self.store = store or EventStore(db_path=db_path, max_events=max_events)
        self.auto_persist = auto_persist

        # Snapshots: snapshot_name -> list of events
        self._snapshots: dict[str, list[Event]] = {}

        logger.info(f"TemporalEngine initialized (auto_persist={auto_persist})")

    async def initialize(self) -> None:
        """Initialize engine and storage."""
        await self.store.initialize()
        logger.info("TemporalEngine ready")

    async def store_event(self, event: Event) -> None:
        """
        Store an event.

        Args:
            event: Event to store
        """
        if not self.auto_persist:
            return

        await self.store.store_event(event)

    async def get_event(self, event_id: UUID | str) -> Event | None:
        """
        Retrieve an event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event or None if not found
        """
        return await self.store.get_event(event_id)

    async def query_by_topic(
        self,
        topic: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Event]:
        """
        Query events by topic.

        Args:
            topic: Topic pattern (supports * wildcard)
            limit: Maximum events to return
            offset: Offset for pagination

        Returns:
            List of events
        """
        return await self.store.query_by_topic(
            topic,
            limit=limit,
            offset=offset,
        )

    async def query_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        topic: str = "*",
        limit: int = 100,
    ) -> list[Event]:
        """
        Query events in a time range.

        Args:
            start_time: Start time
            end_time: End time
            topic: Optional topic filter
            limit: Maximum events

        Returns:
            List of events
        """
        return await self.store.query_by_topic(
            topic,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    async def query_past(
        self,
        hours: int = 0,
        days: int = 0,
        topic: str = "*",
        limit: int = 100,
    ) -> list[Event]:
        """
        Query events from the past N hours/days.

        Args:
            hours: Hours in the past
            days: Days in the past
            topic: Topic filter
            limit: Maximum events

        Returns:
            List of events
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours, days=days)

        return await self.query_time_range(
            start_time,
            end_time,
            topic=topic,
            limit=limit,
        )

    async def query_at_time(
        self,
        point_in_time: datetime,
        topic: str = "*",
        limit: int = 100,
    ) -> list[Event]:
        """
        Time-travel query: get events up to a specific point in time.

        Args:
            point_in_time: Point in time to query
            topic: Topic filter
            limit: Maximum events

        Returns:
            List of events up to that point
        """
        return await self.store.query_by_topic(
            topic,
            end_time=point_in_time,
            limit=limit,
        )

    async def replay(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        topic: str = "*",
        handler: Callable[[Event], Any] | None = None,
        delay_ms: int = 0,
    ) -> list[Event]:
        """
        Replay events from history.

        Args:
            start_time: Optional start time
            end_time: Optional end time
            topic: Topic filter
            handler: Optional handler to call for each event
            delay_ms: Delay between events in milliseconds

        Returns:
            List of replayed events
        """
        events = await self.store.replay_events(
            start_time=start_time,
            end_time=end_time,
            topic_pattern=topic,
        )

        logger.info(f"Replaying {len(events)} events")

        if handler:
            for event in events:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)

                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)

        return events

    async def create_snapshot(
        self,
        name: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        topic: str = "*",
    ) -> int:
        """
        Create a named snapshot of events.

        Args:
            name: Snapshot name
            start_time: Optional start time
            end_time: Optional end time
            topic: Topic filter

        Returns:
            Number of events in snapshot
        """
        events = await self.store.replay_events(
            start_time=start_time,
            end_time=end_time,
            topic_pattern=topic,
        )

        self._snapshots[name] = events
        logger.info(f"Created snapshot '{name}' with {len(events)} events")

        return len(events)

    def get_snapshot(self, name: str) -> list[Event]:
        """
        Get events from a named snapshot.

        Args:
            name: Snapshot name

        Returns:
            List of events in snapshot
        """
        return self._snapshots.get(name, [])

    def list_snapshots(self) -> list[str]:
        """Get list of snapshot names."""
        return list(self._snapshots.keys())

    def delete_snapshot(self, name: str) -> bool:
        """
        Delete a snapshot.

        Args:
            name: Snapshot name

        Returns:
            True if deleted, False if not found
        """
        if name in self._snapshots:
            del self._snapshots[name]
            logger.info(f"Deleted snapshot '{name}'")
            return True
        return False

    async def count_events(
        self,
        topic: str = "*",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> int:
        """
        Count events matching criteria.

        Args:
            topic: Topic filter
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            Event count
        """
        return await self.store.count_events(
            topic_pattern=topic,
            start_time=start_time,
            end_time=end_time,
        )

    async def get_stats(self) -> dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dictionary with statistics
        """
        store_stats = await self.store.get_stats()

        return {
            "store": store_stats,
            "auto_persist": self.auto_persist,
            "snapshots": len(self._snapshots),
            "snapshot_names": list(self._snapshots.keys()),
        }

    async def close(self) -> None:
        """Close engine and storage."""
        await self.store.close()
        logger.info("TemporalEngine closed")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TemporalEngine("
            f"auto_persist={self.auto_persist}, "
            f"snapshots={len(self._snapshots)})"
        )
