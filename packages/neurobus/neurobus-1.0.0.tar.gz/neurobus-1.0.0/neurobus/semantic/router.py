"""
Semantic routing for events.

Routes events based on semantic similarity rather than just pattern matching.
"""

import logging
from typing import Any

import numpy as np

from neurobus.core.event import Event
from neurobus.core.subscription import Subscription
from neurobus.semantic.encoder import SemanticEncoder

logger = logging.getLogger(__name__)


class SemanticRouter:
    """
    Semantic event router using sentence similarity.

    Routes events to subscriptions based on semantic meaning rather than
    just topic patterns. Supports hybrid routing combining both pattern
    and semantic matching.

    Features:
    - Semantic similarity matching
    - Configurable similarity threshold
    - Embedding caching for performance
    - Hybrid pattern + semantic routing
    - Statistics and introspection

    Attributes:
        encoder: Semantic encoder instance
        default_threshold: Default similarity threshold (0-1)

    Example:
        >>> router = SemanticRouter()
        >>> matches = router.find_semantic_matches(
        ...     event,
        ...     subscriptions,
        ...     threshold=0.8
        ... )
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        cache_size: int = 10000,
        cache_ttl: float = 3600.0,
        default_threshold: float = 0.75,
    ) -> None:
        """
        Initialize semantic router.

        Args:
            model_name: Sentence transformer model
            device: Device to use (None = auto-detect)
            cache_size: Embedding cache size
            cache_ttl: Cache TTL in seconds
            default_threshold: Default similarity threshold
        """
        self.encoder = SemanticEncoder(
            model_name=model_name,
            device=device,
            cache_size=cache_size,
            cache_ttl=cache_ttl,
        )

        self.default_threshold = default_threshold

        # Statistics
        self._total_queries = 0
        self._total_matches = 0

        logger.info(
            f"SemanticRouter initialized with model={model_name}, " f"threshold={default_threshold}"
        )

    def find_semantic_matches(
        self,
        event: Event,
        subscriptions: list[Subscription],
        threshold: float | None = None,
    ) -> list[tuple[Subscription, float]]:
        """
        Find subscriptions matching event by semantic similarity.

        Args:
            event: Event to match
            subscriptions: Candidate subscriptions
            threshold: Similarity threshold (uses default if None)

        Returns:
            List of (subscription, similarity_score) tuples sorted by score
        """
        if not subscriptions:
            return []

        threshold = threshold if threshold is not None else self.default_threshold
        self._total_queries += 1

        # Filter to only semantic subscriptions
        semantic_subs = [sub for sub in subscriptions if sub.semantic]
        if not semantic_subs:
            return []

        # Encode event topic
        event_embedding = self.encoder.encode(event.topic)

        # Encode subscription patterns (with caching)
        patterns = [sub.pattern for sub in semantic_subs]
        pattern_embeddings = self.encoder.encode_batch(patterns)

        # Compute similarities
        similarities = self.encoder.similarity_batch(
            event_embedding,
            pattern_embeddings,
        )

        # Filter and sort by similarity
        matches: list[tuple[Subscription, float]] = []

        for sub, similarity in zip(semantic_subs, similarities):
            # Check threshold (use subscription threshold if specified)
            sub_threshold = sub.threshold if sub.threshold is not None else threshold

            if similarity >= sub_threshold:
                # Additional context filtering if specified
                if sub.should_handle(event):
                    matches.append((sub, similarity))
                    self._total_matches += 1

        # Sort by similarity (descending) then priority (descending)
        matches.sort(key=lambda x: (x[1], x[0].priority), reverse=True)

        return matches

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0-1)
        """
        emb1 = self.encoder.encode(text1)
        emb2 = self.encoder.encode(text2)

        return self.encoder.similarity(emb1, emb2)

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text.

        Args:
            text: Text to encode

        Returns:
            Embedding vector
        """
        return self.encoder.encode(text)

    def get_stats(self) -> dict[str, Any]:
        """
        Get router statistics.

        Returns:
            Dictionary with statistics
        """
        encoder_stats = self.encoder.get_stats()

        return {
            "total_queries": self._total_queries,
            "total_matches": self._total_matches,
            "avg_matches_per_query": (self._total_matches / max(self._total_queries, 1)),
            "default_threshold": self.default_threshold,
            "encoder": encoder_stats,
        }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._total_queries = 0
        self._total_matches = 0
        self.encoder.cache.reset_stats()

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_stats()
        return (
            f"SemanticRouter("
            f"model={self.encoder.model_name}, "
            f"queries={stats['total_queries']}, "
            f"threshold={self.default_threshold})"
        )
