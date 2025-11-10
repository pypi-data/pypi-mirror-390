"""
Event store for temporal event persistence.

Provides durable storage and retrieval of events with time-travel capabilities.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.exceptions.temporal import QueryError, StoreError
from neurobus.utils.serialization import deserialize, serialize

logger = logging.getLogger(__name__)


class EventStore:
    """
    SQLite-based event store with time-travel support.

    Stores all events durably to disk, enabling event replay, time-travel
    queries, and audit trails.

    Features:
    - Durable SQLite storage
    - Indexed queries by topic, time, ID
    - Time-travel queries (events at point in time)
    - Event replay functionality
    - Retention policies
    - Statistics tracking

    Example:
        >>> store = EventStore("events.db")
        >>> await store.initialize()
        >>> await store.store_event(event)
        >>> events = await store.query_by_topic("user.*", limit=10)
    """

    def __init__(
        self,
        db_path: str | Path = "neurobus_events.db",
        max_events: int = 1000000,
    ) -> None:
        """
        Initialize event store.

        Args:
            db_path: Path to SQLite database
            max_events: Maximum events to store (for retention)
        """
        self.db_path = Path(db_path)
        self.max_events = max_events
        self._conn: sqlite3.Connection | None = None
        self._initialized = False

        # Statistics
        self._stats = {
            "events_stored": 0,
            "events_queried": 0,
            "events_replayed": 0,
        }

        logger.info(f"EventStore created with db_path={self.db_path}")

    async def initialize(self) -> None:
        """Initialize database and create tables."""
        if self._initialized:
            return

        try:
            # Create database directory if needed
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Connect to database
            self._conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )

            # Enable WAL mode for better concurrency
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")

            # Create events table
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL,
                    data BLOB NOT NULL,
                    timestamp REAL NOT NULL,
                    context BLOB,
                    metadata BLOB,
                    parent_id TEXT,
                    created_at REAL NOT NULL
                )
            """
            )

            # Create indexes
            self._conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_topic
                ON events(topic)
            """
            )

            self._conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON events(timestamp)
            """
            )

            self._conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON events(created_at)
            """
            )

            self._conn.commit()
            self._initialized = True

            logger.info("EventStore initialized successfully")

        except Exception as e:
            raise StoreError(
                f"Failed to initialize event store: {e}",
                original_error=e,
            ) from e

    async def store_event(self, event: Event) -> None:
        """
        Store an event.

        Args:
            event: Event to store

        Raises:
            StoreError: If storage fails
        """
        if not self._initialized:
            await self.initialize()

        try:
            # Serialize data
            data_bytes = serialize(event.data)
            context_bytes = serialize(event.context) if event.context else None
            metadata_bytes = serialize(event.metadata) if event.metadata else None

            # Convert timestamp to Unix timestamp
            timestamp = event.timestamp.timestamp()
            created_at = datetime.now().timestamp()

            # Insert event
            self._conn.execute(
                """
                INSERT INTO events
                (id, topic, data, timestamp, context, metadata, parent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.id),
                    event.topic,
                    data_bytes,
                    timestamp,
                    context_bytes,
                    metadata_bytes,
                    str(event.parent_id) if event.parent_id else None,
                    created_at,
                ),
            )

            self._conn.commit()
            self._stats["events_stored"] += 1

            # Check retention policy
            await self._enforce_retention()

        except Exception as e:
            self._conn.rollback()
            raise StoreError(
                f"Failed to store event {event.id}: {e}",
                original_error=e,
            ) from e

    async def get_event(self, event_id: UUID | str) -> Event | None:
        """
        Get an event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event or None if not found
        """
        if not self._initialized:
            await self.initialize()

        try:
            event_id_str = str(event_id)

            cursor = self._conn.execute(
                """
                SELECT id, topic, data, timestamp, context, metadata, parent_id
                FROM events
                WHERE id = ?
                """,
                (event_id_str,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_event(row)

        except Exception as e:
            raise QueryError(
                f"Failed to get event {event_id}: {e}",
                original_error=e,
            ) from e

    async def query_by_topic(
        self,
        topic_pattern: str,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Event]:
        """
        Query events by topic pattern.

        Args:
            topic_pattern: Topic pattern (supports % wildcard for SQLite LIKE)
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum events to return
            offset: Offset for pagination

        Returns:
            List of events
        """
        if not self._initialized:
            await self.initialize()

        try:
            query = """
                SELECT id, topic, data, timestamp, context, metadata, parent_id
                FROM events
                WHERE topic LIKE ?
            """
            params: list[Any] = [topic_pattern.replace("*", "%")]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.timestamp())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.timestamp())

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = self._conn.execute(query, params)
            rows = cursor.fetchall()

            self._stats["events_queried"] += len(rows)

            return [self._row_to_event(row) for row in rows]

        except Exception as e:
            raise QueryError(
                f"Failed to query events: {e}",
                original_error=e,
            ) from e

    async def query_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
    ) -> list[Event]:
        """
        Query events in a time range.

        Args:
            start_time: Start time
            end_time: End time
            limit: Maximum events to return

        Returns:
            List of events
        """
        return await self.query_by_topic(
            "%",  # Match all topics
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    async def replay_events(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        topic_pattern: str = "%",
    ) -> list[Event]:
        """
        Replay events for time-travel or replay scenarios.

        Args:
            start_time: Optional start time
            end_time: Optional end time
            topic_pattern: Topic pattern filter

        Returns:
            List of events in chronological order
        """
        if not self._initialized:
            await self.initialize()

        try:
            query = """
                SELECT id, topic, data, timestamp, context, metadata, parent_id
                FROM events
                WHERE topic LIKE ?
            """
            params: list[Any] = [topic_pattern.replace("*", "%")]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.timestamp())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.timestamp())

            query += " ORDER BY timestamp ASC"  # Chronological order for replay

            cursor = self._conn.execute(query, params)
            rows = cursor.fetchall()

            self._stats["events_replayed"] += len(rows)

            return [self._row_to_event(row) for row in rows]

        except Exception as e:
            raise QueryError(
                f"Failed to replay events: {e}",
                original_error=e,
            ) from e

    async def count_events(
        self,
        topic_pattern: str = "%",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> int:
        """
        Count events matching criteria.

        Args:
            topic_pattern: Topic pattern
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            Event count
        """
        if not self._initialized:
            await self.initialize()

        try:
            query = "SELECT COUNT(*) FROM events WHERE topic LIKE ?"
            params: list[Any] = [topic_pattern.replace("*", "%")]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.timestamp())

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.timestamp())

            cursor = self._conn.execute(query, params)
            count = cursor.fetchone()[0]

            return count

        except Exception as e:
            raise QueryError(
                f"Failed to count events: {e}",
                original_error=e,
            ) from e

    async def _enforce_retention(self) -> None:
        """Enforce retention policy by removing oldest events."""
        if self.max_events <= 0:
            return  # No retention limit

        try:
            # Count total events
            cursor = self._conn.execute("SELECT COUNT(*) FROM events")
            total = cursor.fetchone()[0]

            if total > self.max_events:
                # Delete oldest events beyond limit
                excess = total - self.max_events

                self._conn.execute(
                    """
                    DELETE FROM events
                    WHERE id IN (
                        SELECT id FROM events
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                    """,
                    (excess,),
                )

                self._conn.commit()
                logger.info(f"Removed {excess} events due to retention policy")

        except Exception as e:
            logger.error(f"Failed to enforce retention: {e}", exc_info=True)

    def _row_to_event(self, row: tuple) -> Event:
        """Convert database row to Event."""
        event_id, topic, data_bytes, timestamp, context_bytes, metadata_bytes, parent_id = row

        # Deserialize
        data = deserialize(data_bytes)
        context = deserialize(context_bytes) if context_bytes else {}
        metadata = deserialize(metadata_bytes) if metadata_bytes else {}

        return Event(
            id=UUID(event_id),
            topic=topic,
            data=data,
            timestamp=datetime.fromtimestamp(timestamp),
            context=context,
            metadata=metadata,
            parent_id=UUID(parent_id) if parent_id else None,
        )

    async def get_stats(self) -> dict[str, Any]:
        """
        Get store statistics.

        Returns:
            Dictionary with statistics
        """
        if not self._initialized:
            await self.initialize()

        # Get database size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        # Get total events
        cursor = self._conn.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        return {
            "db_path": str(self.db_path),
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / 1024 / 1024, 2),
            "total_events": total_events,
            "max_events": self.max_events,
            "events_stored": self._stats["events_stored"],
            "events_queried": self._stats["events_queried"],
            "events_replayed": self._stats["events_replayed"],
        }

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False
            logger.info("EventStore closed")

    def __repr__(self) -> str:
        """String representation."""
        return f"EventStore(db_path={self.db_path}, initialized={self._initialized})"
