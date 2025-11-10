"""
Memory engine for long-term event memory management.

Provides high-level API for memory storage, retrieval, and semantic search.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from neurobus.core.event import Event
from neurobus.memory.store import MemoryEntry, MemoryStore

logger = logging.getLogger(__name__)


class MemoryEngine:
    """
    High-level memory management engine.

    Manages long-term memory storage with semantic search capabilities,
    importance tracking, and memory consolidation.

    Features:
    - Automatic memory creation from events
    - Semantic memory search (with encoder)
    - Topic-based retrieval
    - Time-based queries
    - Importance-based ranking
    - Memory consolidation and decay
    - Statistics tracking

    Example:
        >>> engine = MemoryEngine()
        >>> await engine.initialize()
        >>>
        >>> # Store event as memory
        >>> await engine.remember_event(event)
        >>>
        >>> # Search memories
        >>> memories = await engine.search("user authentication")
        >>>
        >>> # Get recent memories
        >>> recent = engine.get_recent(limit=10)
    """

    def __init__(
        self,
        store: MemoryStore | None = None,
        max_memories: int = 10000,
        enable_semantic: bool = False,
        auto_consolidate: bool = True,
        consolidate_interval: int = 3600,  # 1 hour
    ) -> None:
        """
        Initialize memory engine.

        Args:
            store: Optional custom memory store
            max_memories: Maximum memories to store
            enable_semantic: Enable semantic search
            auto_consolidate: Auto-consolidate memories
            consolidate_interval: Consolidation interval (seconds)
        """
        self.store = store or MemoryStore(max_memories=max_memories)
        self.enable_semantic = enable_semantic
        self.auto_consolidate = auto_consolidate
        self.consolidate_interval = consolidate_interval

        # Semantic encoder (lazy-loaded)
        self._encoder: Any = None

        # Consolidation task
        self._consolidation_task: asyncio.Task | None = None

        logger.info(
            f"MemoryEngine initialized "
            f"(semantic={enable_semantic}, auto_consolidate={auto_consolidate})"
        )

    async def initialize(self) -> None:
        """Initialize engine and encoder."""
        if self.enable_semantic:
            await self._init_encoder()

        # Start auto-consolidation if enabled
        if self.auto_consolidate:
            self._consolidation_task = asyncio.create_task(self._consolidation_loop())

        logger.info("MemoryEngine ready")

    async def _init_encoder(self) -> None:
        """Initialize semantic encoder."""
        try:
            from neurobus.semantic.encoder import SemanticEncoder

            self._encoder = SemanticEncoder()
            logger.info("Semantic encoder loaded for memory search")

        except ImportError:
            logger.warning(
                "Semantic encoder not available. " "Install with: pip install neurobus[semantic]"
            )
            self.enable_semantic = False

    async def remember_event(
        self,
        event: Event,
        importance: float = 0.5,
    ) -> MemoryEntry:
        """
        Create memory from event.

        Args:
            event: Event to remember
            importance: Initial importance score

        Returns:
            Created memory entry
        """
        # Convert event to memory content
        content = self._event_to_content(event)

        # Generate embedding if semantic enabled
        embedding = None
        if self.enable_semantic and self._encoder:
            embedding = self._encoder.encode(content).tolist()

        # Create memory entry
        entry = MemoryEntry(
            event_id=event.id,
            topic=event.topic,
            content=content,
            embedding=embedding,
            metadata={
                "event_timestamp": event.timestamp.isoformat(),
                "event_data": event.data,
            },
            importance=importance,
        )

        # Store memory
        self.store.add(entry)

        logger.debug(f"Remembered event: {event.id} as memory {entry.id}")

        return entry

    def _event_to_content(self, event: Event) -> str:
        """
        Convert event to memory content string.

        Args:
            event: Event to convert

        Returns:
            Content string
        """
        # Create text representation
        parts = [f"Topic: {event.topic}"]

        # Add data as JSON
        if event.data:
            data_str = json.dumps(event.data, default=str)
            parts.append(f"Data: {data_str}")

        # Add context if available
        if event.context:
            context_str = json.dumps(event.context, default=str)
            parts.append(f"Context: {context_str}")

        return " | ".join(parts)

    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
    ) -> list[MemoryEntry]:
        """
        Semantic search for memories.

        Args:
            query: Search query
            limit: Maximum results
            threshold: Similarity threshold (0-1)

        Returns:
            List of matching memory entries
        """
        if not self.enable_semantic or not self._encoder:
            logger.warning("Semantic search not enabled, falling back to topic search")
            return self.store.search_by_topic(f"*{query}*", limit=limit)

        # Generate query embedding
        query_embedding = self._encoder.encode(query)

        # Find similar memories
        results: list[tuple[MemoryEntry, float]] = []

        for entry in self.store._memories.values():
            if entry.embedding is None:
                continue

            # Compute similarity
            similarity = self._encoder.similarity(query_embedding, entry.embedding)

            if similarity >= threshold:
                results.append((entry, similarity))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        # Record access
        for entry, _ in results[:limit]:
            entry.access()

        return [entry for entry, _ in results[:limit]]

    def search_by_topic(
        self,
        topic: str,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search memories by topic.

        Args:
            topic: Topic pattern
            limit: Maximum results

        Returns:
            List of memory entries
        """
        return self.store.search_by_topic(topic, limit=limit)

    def search_by_time(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search memories by time range.

        Args:
            start_time: Start time
            end_time: End time
            limit: Maximum results

        Returns:
            List of memory entries
        """
        return self.store.search_by_time(start_time, end_time, limit=limit)

    def get_recent(self, limit: int = 10) -> list[MemoryEntry]:
        """
        Get recent memories.

        Args:
            limit: Maximum memories

        Returns:
            List of recent memory entries
        """
        return self.store.get_recent(limit=limit)

    def get_important(self, limit: int = 10) -> list[MemoryEntry]:
        """
        Get most important memories.

        Args:
            limit: Maximum memories

        Returns:
            List of important memory entries
        """
        return self.store.get_most_important(limit=limit)

    def consolidate(self) -> None:
        """
        Consolidate memories.

        Applies importance decay and prunes low-importance memories.
        """
        self.store.consolidate()
        logger.info("Memory consolidation completed")

    async def _consolidation_loop(self) -> None:
        """Background task for periodic memory consolidation."""
        logger.info(f"Memory consolidation loop started (interval={self.consolidate_interval}s)")

        while True:
            try:
                await asyncio.sleep(self.consolidate_interval)
                self.consolidate()

            except asyncio.CancelledError:
                logger.info("Memory consolidation loop stopped")
                break
            except Exception as e:
                logger.error(f"Error in consolidation loop: {e}", exc_info=True)

    def get_stats(self) -> dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dictionary with statistics
        """
        store_stats = self.store.get_stats()

        return {
            "store": store_stats,
            "semantic_enabled": self.enable_semantic,
            "auto_consolidate": self.auto_consolidate,
            "consolidate_interval": self.consolidate_interval,
            "encoder_loaded": self._encoder is not None,
        }

    async def close(self) -> None:
        """Close engine and stop background tasks."""
        if self._consolidation_task:
            self._consolidation_task.cancel()
            try:
                await self._consolidation_task
            except asyncio.CancelledError:
                pass

        logger.info("MemoryEngine closed")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MemoryEngine(" f"memories={self.store.count()}, " f"semantic={self.enable_semantic})"
        )
