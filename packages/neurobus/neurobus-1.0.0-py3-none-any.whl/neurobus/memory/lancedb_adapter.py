"""
LanceDB vector database adapter for NeuroBUS.

Provides integration with LanceDB for vector similarity search.
"""

import logging
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.memory.adapter import BaseMemoryAdapter, VectorSearchResult

logger = logging.getLogger(__name__)


class LanceDBAdapter(BaseMemoryAdapter):
    """
    LanceDB vector database adapter.

    Stores events as vectors in LanceDB for semantic search.

    Example:
        >>> adapter = LanceDBAdapter(
        ...     uri="./data/lancedb",
        ...     vector_size=384
        ... )
        >>> await adapter.initialize()
        >>>
        >>> # Store event with embedding
        >>> await adapter.store_event(event, embedding)
        >>>
        >>> # Search similar events
        >>> results = await adapter.search_similar(query_embedding, k=5)
    """

    def __init__(
        self,
        uri: str = "./data/lancedb",
        collection_name: str = "neurobus_events",
        vector_size: int = 384,
    ):
        """
        Initialize LanceDB adapter.

        Args:
            uri: LanceDB database URI/path
            collection_name: Table name
            vector_size: Vector dimension size
        """
        super().__init__(collection_name)

        self.uri = uri
        self.vector_size = vector_size

        self._db: Any = None
        self._table: Any = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize LanceDB client and create table."""
        if self._initialized:
            return

        try:
            import lancedb
            import pyarrow as pa

            # Connect to database
            self._db = await lancedb.connect_async(self.uri)

            # Define schema
            schema = pa.schema(
                [
                    pa.field("event_id", pa.string()),
                    pa.field("topic", pa.string()),
                    pa.field("timestamp", pa.string()),
                    pa.field("data", pa.string()),  # JSON string
                    pa.field("context", pa.string()),  # JSON string
                    pa.field("metadata", pa.string()),  # JSON string
                    pa.field("parent_id", pa.string()),
                    pa.field("vector", pa.list_(pa.float32(), self.vector_size)),
                ]
            )

            # Create or open table
            table_names = await self._db.table_names()

            if self.collection_name not in table_names:
                self._table = await self._db.create_table(
                    self.collection_name,
                    schema=schema,
                )
                logger.info(f"Created LanceDB table: {self.collection_name}")
            else:
                self._table = await self._db.open_table(self.collection_name)
                logger.info(f"Using existing LanceDB table: {self.collection_name}")

            self._initialized = True
            logger.info(f"LanceDB adapter initialized (uri={self.uri})")

        except ImportError:
            raise ImportError("lancedb not installed. " "Install with: pip install lancedb pyarrow")
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}", exc_info=True)
            raise

    async def store_event(
        self,
        event: Event,
        embedding: list[float],
    ) -> None:
        """Store event with embedding in LanceDB."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        import json

        # Create record
        record = {
            "event_id": str(event.id),
            "topic": event.topic,
            "timestamp": event.timestamp.isoformat(),
            "data": json.dumps(event.data),
            "context": json.dumps(event.context or {}),
            "metadata": json.dumps(event.metadata or {}),
            "parent_id": str(event.parent_id) if event.parent_id else "",
            "vector": embedding,
        }

        # Add to table
        await self._table.add([record])

        self._stats["events_stored"] += 1
        logger.debug(f"Stored event {event.id} in LanceDB")

    async def search_similar(
        self,
        embedding: list[float],
        k: int = 5,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar events in LanceDB."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        # Search using vector similarity
        query = self._table.search(embedding).limit(k)

        # Apply filters if provided
        if filter_dict:
            for key, value in filter_dict.items():
                query = query.where(f"{key} == '{value}'")

        # Execute search
        results_df = await query.to_pandas()

        self._stats["searches_performed"] += 1

        # Convert to VectorSearchResult
        results = []
        for _, row in results_df.iterrows():
            import json

            results.append(
                VectorSearchResult(
                    event_id=UUID(row["event_id"]),
                    score=float(row.get("_distance", 0.0)),  # LanceDB returns distance
                    payload={
                        "event_id": row["event_id"],
                        "topic": row["topic"],
                        "timestamp": row["timestamp"],
                        "data": json.loads(row["data"]),
                        "context": json.loads(row["context"]),
                        "metadata": json.loads(row["metadata"]),
                        "parent_id": row["parent_id"] if row["parent_id"] else None,
                    },
                )
            )

        logger.debug(f"Found {len(results)} similar events")
        return results

    async def get_event(self, event_id: UUID) -> dict[str, Any] | None:
        """Get event by ID from LanceDB."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        try:
            import json

            # Query by event_id
            result_df = (
                await self._table.search()
                .where(f"event_id == '{str(event_id)}'")
                .limit(1)
                .to_pandas()
            )

            if len(result_df) == 0:
                return None

            row = result_df.iloc[0]

            self._stats["events_retrieved"] += 1

            return {
                "event_id": row["event_id"],
                "topic": row["topic"],
                "timestamp": row["timestamp"],
                "data": json.loads(row["data"]),
                "context": json.loads(row["context"]),
                "metadata": json.loads(row["metadata"]),
                "parent_id": row["parent_id"] if row["parent_id"] else None,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve event {event_id}: {e}")
            return None

    async def delete_event(self, event_id: UUID) -> bool:
        """Delete event from LanceDB."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        try:
            # LanceDB uses delete with predicate
            await self._table.delete(f"event_id == '{str(event_id)}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            return False

    async def clear(self) -> None:
        """Clear all events from table."""
        if not self._initialized:
            return

        try:
            # Drop and recreate table
            await self._db.drop_table(self.collection_name)
            await self.initialize()

            self._stats["events_stored"] = 0
            logger.info(f"Cleared LanceDB table: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to clear table: {e}")

    async def close(self) -> None:
        """Close LanceDB connection."""
        self._initialized = False
        await super().close()
