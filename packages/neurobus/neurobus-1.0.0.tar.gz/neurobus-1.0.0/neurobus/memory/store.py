"""
Memory store for long-term event memory.

Provides vector database integration for semantic memory storage and retrieval.
"""

import logging
import time
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class MemoryEntry:
    """
    A single memory entry.

    Attributes:
        id: Memory entry ID
        event_id: Original event ID
        topic: Event topic
        content: Memory content (text representation)
        embedding: Vector embedding
        timestamp: When memory was created
        metadata: Additional metadata
        access_count: Number of times accessed
        last_access: Last access timestamp
        importance: Importance score (0-1)
    """

    def __init__(
        self,
        event_id: UUID,
        topic: str,
        content: str,
        embedding: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
        importance: float = 0.5,
    ) -> None:
        """
        Initialize memory entry.

        Args:
            event_id: Original event ID
            topic: Event topic
            content: Memory content
            embedding: Optional vector embedding
            metadata: Optional metadata
            importance: Importance score (0-1)
        """
        self.id = uuid4()
        self.event_id = event_id
        self.topic = topic
        self.content = content
        self.embedding = embedding
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
        self.access_count = 0
        self.last_access = time.time()
        self.importance = importance

    def access(self) -> None:
        """Record an access to this memory."""
        self.access_count += 1
        self.last_access = time.time()

    def decay_importance(self, decay_rate: float = 0.1) -> None:
        """
        Decay importance over time.

        Args:
            decay_rate: Decay rate (0-1)
        """
        self.importance = max(0.0, self.importance - decay_rate)

    def boost_importance(self, boost: float = 0.1) -> None:
        """
        Boost importance (e.g., after access).

        Args:
            boost: Boost amount (0-1)
        """
        self.importance = min(1.0, self.importance + boost)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "event_id": str(self.event_id),
            "topic": self.topic,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_access": self.last_access,
            "importance": self.importance,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MemoryEntry(id={self.id}, topic={self.topic!r}, " f"importance={self.importance:.2f})"
        )


class MemoryStore:
    """
    In-memory storage for event memories.

    Provides basic memory storage with importance tracking and decay.
    Can be extended with vector database backends for semantic search.

    Features:
    - Memory storage and retrieval
    - Importance scoring
    - Access tracking
    - Memory decay
    - Topic-based filtering
    - Time-based queries

    Example:
        >>> store = MemoryStore(max_memories=1000)
        >>> entry = MemoryEntry(event.id, event.topic, "User logged in")
        >>> store.add(entry)
        >>> memories = store.search_by_topic("user.*")
    """

    def __init__(
        self,
        max_memories: int = 10000,
        decay_enabled: bool = True,
        decay_rate: float = 0.01,
    ) -> None:
        """
        Initialize memory store.

        Args:
            max_memories: Maximum memories to store
            decay_enabled: Whether to enable importance decay
            decay_rate: Decay rate for importance
        """
        self.max_memories = max_memories
        self.decay_enabled = decay_enabled
        self.decay_rate = decay_rate

        # Storage: memory_id -> MemoryEntry
        self._memories: dict[UUID, MemoryEntry] = {}

        # Index: topic -> set of memory_ids
        self._topic_index: dict[str, set[UUID]] = {}

        # Statistics
        self._stats = {
            "memories_added": 0,
            "memories_accessed": 0,
            "memories_pruned": 0,
            "searches": 0,
        }

        logger.info(f"MemoryStore initialized (max_memories={max_memories})")

    def add(self, entry: MemoryEntry) -> None:
        """
        Add a memory entry.

        Args:
            entry: Memory entry to add
        """
        # Check capacity
        if len(self._memories) >= self.max_memories:
            self._prune_least_important()

        # Store memory
        self._memories[entry.id] = entry

        # Index by topic
        if entry.topic not in self._topic_index:
            self._topic_index[entry.topic] = set()
        self._topic_index[entry.topic].add(entry.id)

        self._stats["memories_added"] += 1

        logger.debug(f"Added memory: {entry.id} (topic={entry.topic})")

    def get(self, memory_id: UUID) -> MemoryEntry | None:
        """
        Get a memory by ID.

        Args:
            memory_id: Memory ID

        Returns:
            Memory entry or None
        """
        entry = self._memories.get(memory_id)

        if entry:
            entry.access()
            self._stats["memories_accessed"] += 1

        return entry

    def search_by_topic(
        self,
        topic_pattern: str,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search memories by topic pattern.

        Args:
            topic_pattern: Topic pattern (supports * wildcard)
            limit: Maximum memories to return

        Returns:
            List of memory entries, sorted by importance
        """
        self._stats["searches"] += 1

        # Simple pattern matching (replace * with any chars)
        import fnmatch

        matching_memories: list[MemoryEntry] = []

        for topic, memory_ids in self._topic_index.items():
            if fnmatch.fnmatch(topic, topic_pattern):
                for memory_id in memory_ids:
                    entry = self._memories.get(memory_id)
                    if entry:
                        matching_memories.append(entry)

        # Sort by importance (descending)
        matching_memories.sort(key=lambda e: e.importance, reverse=True)

        # Record access
        for entry in matching_memories[:limit]:
            entry.access()
            self._stats["memories_accessed"] += 1

        return matching_memories[:limit]

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
            limit: Maximum memories

        Returns:
            List of memory entries
        """
        self._stats["searches"] += 1

        matching: list[MemoryEntry] = []

        for entry in self._memories.values():
            if start_time and entry.timestamp < start_time:
                continue
            if end_time and entry.timestamp > end_time:
                continue
            matching.append(entry)

        # Sort by timestamp (descending)
        matching.sort(key=lambda e: e.timestamp, reverse=True)

        return matching[:limit]

    def get_recent(self, limit: int = 10) -> list[MemoryEntry]:
        """
        Get most recent memories.

        Args:
            limit: Maximum memories

        Returns:
            List of recent memory entries
        """
        all_memories = list(self._memories.values())
        all_memories.sort(key=lambda e: e.timestamp, reverse=True)
        return all_memories[:limit]

    def get_most_important(self, limit: int = 10) -> list[MemoryEntry]:
        """
        Get most important memories.

        Args:
            limit: Maximum memories

        Returns:
            List of important memory entries
        """
        all_memories = list(self._memories.values())
        all_memories.sort(key=lambda e: e.importance, reverse=True)
        return all_memories[:limit]

    def _prune_least_important(self, count: int = 1) -> int:
        """
        Prune least important memories.

        Args:
            count: Number of memories to prune

        Returns:
            Number of memories pruned
        """
        if not self._memories:
            return 0

        # Sort by importance (ascending)
        sorted_memories = sorted(self._memories.values(), key=lambda e: e.importance)

        pruned = 0
        for entry in sorted_memories[:count]:
            # Remove from storage
            del self._memories[entry.id]

            # Remove from index
            if entry.topic in self._topic_index:
                self._topic_index[entry.topic].discard(entry.id)
                if not self._topic_index[entry.topic]:
                    del self._topic_index[entry.topic]

            pruned += 1
            self._stats["memories_pruned"] += 1

        logger.debug(f"Pruned {pruned} memories")
        return pruned

    def decay_all(self) -> None:
        """Apply importance decay to all memories."""
        if not self.decay_enabled:
            return

        for entry in self._memories.values():
            entry.decay_importance(self.decay_rate)

    def consolidate(self) -> None:
        """
        Consolidate memories.

        Applies decay and prunes low-importance memories.
        """
        # Apply decay
        self.decay_all()

        # Prune very low importance memories
        to_prune = [entry for entry in self._memories.values() if entry.importance < 0.1]

        for entry in to_prune:
            del self._memories[entry.id]
            if entry.topic in self._topic_index:
                self._topic_index[entry.topic].discard(entry.id)
            self._stats["memories_pruned"] += 1

        logger.info(f"Consolidated: pruned {len(to_prune)} low-importance memories")

    def count(self) -> int:
        """Get total memory count."""
        return len(self._memories)

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._topic_index.clear()
        logger.info("All memories cleared")

    def get_stats(self) -> dict[str, Any]:
        """
        Get store statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_memories": len(self._memories),
            "max_memories": self.max_memories,
            "unique_topics": len(self._topic_index),
            "memories_added": self._stats["memories_added"],
            "memories_accessed": self._stats["memories_accessed"],
            "memories_pruned": self._stats["memories_pruned"],
            "searches": self._stats["searches"],
            "decay_enabled": self.decay_enabled,
            "decay_rate": self.decay_rate,
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"MemoryStore(memories={len(self._memories)}, topics={len(self._topic_index)})"
