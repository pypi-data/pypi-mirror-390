"""
Embedding cache for semantic routing.

Provides efficient caching of text embeddings with TTL support and LRU eviction.
"""

import time
from collections import OrderedDict
from threading import RLock
from typing import Any

import numpy as np


class EmbeddingCache:
    """
    Thread-safe LRU cache for text embeddings.

    Features:
    - LRU eviction policy
    - TTL-based expiration
    - Thread-safe operations
    - Memory-efficient storage
    - Hit/miss statistics

    Attributes:
        max_size: Maximum number of cached embeddings
        ttl: Time-to-live in seconds (0 = no expiration)

    Example:
        >>> cache = EmbeddingCache(max_size=1000, ttl=3600)
        >>> cache.set("hello world", embedding)
        >>> embedding = cache.get("hello world")
    """

    def __init__(self, max_size: int = 10000, ttl: float = 3600.0) -> None:
        """
        Initialize embedding cache.

        Args:
            max_size: Maximum cache entries (0 = unlimited)
            ttl: Time-to-live in seconds (0 = no expiration)
        """
        self.max_size = max_size
        self.ttl = ttl

        # OrderedDict for LRU behavior
        self._cache: OrderedDict[str, tuple[np.ndarray, float]] = OrderedDict()
        self._lock = RLock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, text: str) -> np.ndarray | None:
        """
        Get embedding from cache.

        Args:
            text: Text to look up

        Returns:
            Cached embedding or None if not found/expired
        """
        with self._lock:
            if text not in self._cache:
                self._misses += 1
                return None

            embedding, timestamp = self._cache[text]

            # Check TTL
            if self.ttl > 0 and (time.time() - timestamp) > self.ttl:
                del self._cache[text]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(text)
            self._hits += 1

            return embedding

    def set(self, text: str, embedding: np.ndarray) -> None:
        """
        Store embedding in cache.

        Args:
            text: Text key
            embedding: Numpy array embedding
        """
        with self._lock:
            # Remove if already exists (to update timestamp)
            if text in self._cache:
                del self._cache[text]

            # Add new entry
            self._cache[text] = (embedding, time.time())

            # Evict oldest if over capacity
            if self.max_size > 0 and len(self._cache) > self.max_size:
                self._cache.popitem(last=False)  # Remove oldest (FIFO)
                self._evictions += 1

    def clear(self) -> None:
        """Clear all cached embeddings."""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
            }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._evictions = 0

    def __len__(self) -> int:
        """Get cache size."""
        return self.size()

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_stats()
        return (
            f"EmbeddingCache("
            f"size={stats['size']}/{stats['max_size']}, "
            f"hit_rate={stats['hit_rate']:.2%})"
        )
