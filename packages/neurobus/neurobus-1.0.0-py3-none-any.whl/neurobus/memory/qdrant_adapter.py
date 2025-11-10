"""
Qdrant vector database adapter for NeuroBUS.

Provides integration with Qdrant for vector similarity search.
"""

import logging
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.memory.adapter import BaseMemoryAdapter, VectorSearchResult

logger = logging.getLogger(__name__)


class QdrantAdapter(BaseMemoryAdapter):
    """
    Qdrant vector database adapter.

    Stores events as vectors in Qdrant for semantic search.

    Example:
        >>> adapter = QdrantAdapter(
        ...     url="http://localhost:6333",
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
        url: str = "http://localhost:6333",
        api_key: str | None = None,
        collection_name: str = "neurobus_events",
        vector_size: int = 384,
        distance: str = "Cosine",
    ):
        """
        Initialize Qdrant adapter.

        Args:
            url: Qdrant server URL
            api_key: Optional API key for authentication
            collection_name: Collection name
            vector_size: Vector dimension size
            distance: Distance metric (Cosine, Euclid, Dot)
        """
        super().__init__(collection_name)

        self.url = url
        self.api_key = api_key
        self.vector_size = vector_size
        self.distance = distance

        self._client: Any = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Qdrant client and create collection."""
        if self._initialized:
            return

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            # Create client
            self._client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
            )

            # Map distance metric
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT,
            }

            # Create collection if it doesn't exist
            collections = self._client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                self._client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=distance_map.get(self.distance, Distance.COSINE),
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")

            self._initialized = True
            logger.info(f"Qdrant adapter initialized (url={self.url})")

        except ImportError:
            raise ImportError(
                "qdrant-client not installed. " "Install with: pip install qdrant-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}", exc_info=True)
            raise

    async def store_event(
        self,
        event: Event,
        embedding: list[float],
    ) -> None:
        """Store event with embedding in Qdrant."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        from qdrant_client.models import PointStruct

        # Create point
        point = PointStruct(
            id=str(event.id),
            vector=embedding,
            payload={
                "event_id": str(event.id),
                "topic": event.topic,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data,
                "context": event.context or {},
                "metadata": event.metadata or {},
                "parent_id": str(event.parent_id) if event.parent_id else None,
            },
        )

        # Upsert to Qdrant
        self._client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

        self._stats["events_stored"] += 1
        logger.debug(f"Stored event {event.id} in Qdrant")

    async def search_similar(
        self,
        embedding: list[float],
        k: int = 5,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar events in Qdrant."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        from qdrant_client.models import Filter as QdrantFilter

        # Build filter if provided
        qdrant_filter = None
        if filter_dict:
            # Convert filter_dict to Qdrant filter format
            # This is a simplified version - can be expanded
            qdrant_filter = QdrantFilter()

        # Search
        search_result = self._client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            limit=k,
            query_filter=qdrant_filter,
        )

        self._stats["searches_performed"] += 1

        # Convert to VectorSearchResult
        results = []
        for hit in search_result:
            results.append(
                VectorSearchResult(
                    event_id=UUID(hit.id),
                    score=hit.score,
                    payload=hit.payload,
                )
            )

        logger.debug(f"Found {len(results)} similar events")
        return results

    async def get_event(self, event_id: UUID) -> dict[str, Any] | None:
        """Get event by ID from Qdrant."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        try:
            result = self._client.retrieve(
                collection_name=self.collection_name,
                ids=[str(event_id)],
            )

            if result:
                self._stats["events_retrieved"] += 1
                return result[0].payload

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve event {event_id}: {e}")
            return None

    async def delete_event(self, event_id: UUID) -> bool:
        """Delete event from Qdrant."""
        if not self._initialized:
            raise RuntimeError("Adapter not initialized")

        try:
            self._client.delete(
                collection_name=self.collection_name,
                points_selector=[str(event_id)],
            )
            return True

        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            return False

    async def clear(self) -> None:
        """Clear all events from collection."""
        if not self._initialized:
            return

        try:
            self._client.delete_collection(self.collection_name)

            # Recreate collection
            await self.initialize()

            self._stats["events_stored"] = 0
            logger.info(f"Cleared Qdrant collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")

    async def close(self) -> None:
        """Close Qdrant client."""
        if self._client:
            self._client.close()
            self._initialized = False

        await super().close()
