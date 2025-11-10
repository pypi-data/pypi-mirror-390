"""
Memory adapter interface for vector database integration.

Provides protocol for different vector store implementations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Protocol
from uuid import UUID

from neurobus.core.event import Event

logger = logging.getLogger(__name__)


class VectorSearchResult:
    """Result from vector similarity search."""

    def __init__(
        self,
        event_id: UUID,
        score: float,
        payload: dict[str, Any],
    ):
        """
        Initialize search result.

        Args:
            event_id: Event identifier
            score: Similarity score (0-1)
            payload: Event payload/metadata
        """
        self.event_id = event_id
        self.score = score
        self.payload = payload

    def __repr__(self) -> str:
        """String representation."""
        return f"VectorSearchResult(id={self.event_id}, score={self.score:.3f})"


class MemoryAdapter(Protocol):
    """
    Protocol for vector memory adapters.

    Implementations must provide:
    - store_event: Store event with vector embedding
    - search_similar: Search for similar events
    - get_event: Retrieve specific event
    - delete_event: Remove event
    - clear: Clear all events
    - get_stats: Get adapter statistics
    """

    async def initialize(self) -> None:
        """Initialize the adapter and connect to backend."""
        ...

    async def store_event(
        self,
        event: Event,
        embedding: list[float],
    ) -> None:
        """
        Store event with its vector embedding.

        Args:
            event: Event to store
            embedding: Vector embedding
        """
        ...

    async def search_similar(
        self,
        embedding: list[float],
        k: int = 5,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar events.

        Args:
            embedding: Query vector
            k: Number of results
            filter_dict: Optional filters

        Returns:
            List of search results
        """
        ...

    async def get_event(self, event_id: UUID) -> dict[str, Any] | None:
        """
        Get specific event by ID.

        Args:
            event_id: Event identifier

        Returns:
            Event data or None
        """
        ...

    async def delete_event(self, event_id: UUID) -> bool:
        """
        Delete event.

        Args:
            event_id: Event identifier

        Returns:
            True if deleted
        """
        ...

    async def clear(self) -> None:
        """Clear all stored events."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get adapter statistics."""
        ...

    async def close(self) -> None:
        """Close adapter and cleanup resources."""
        ...


class BaseMemoryAdapter(ABC):
    """
    Base class for memory adapters.

    Provides common functionality for concrete implementations.
    """

    def __init__(self, collection_name: str = "neurobus_events"):
        """
        Initialize base adapter.

        Args:
            collection_name: Name of vector collection
        """
        self.collection_name = collection_name
        self._stats = {
            "events_stored": 0,
            "searches_performed": 0,
            "events_retrieved": 0,
        }

        logger.info(f"{self.__class__.__name__} initialized " f"(collection={collection_name})")

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the adapter."""
        pass

    @abstractmethod
    async def store_event(
        self,
        event: Event,
        embedding: list[float],
    ) -> None:
        """Store event with embedding."""
        pass

    @abstractmethod
    async def search_similar(
        self,
        embedding: list[float],
        k: int = 5,
        filter_dict: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search for similar events."""
        pass

    @abstractmethod
    async def get_event(self, event_id: UUID) -> dict[str, Any] | None:
        """Get event by ID."""
        pass

    @abstractmethod
    async def delete_event(self, event_id: UUID) -> bool:
        """Delete event."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all events."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get adapter statistics."""
        return {
            "adapter": self.__class__.__name__,
            "collection": self.collection_name,
            **self._stats,
        }

    async def close(self) -> None:
        """Close adapter."""
        logger.info(f"{self.__class__.__name__} closed")
