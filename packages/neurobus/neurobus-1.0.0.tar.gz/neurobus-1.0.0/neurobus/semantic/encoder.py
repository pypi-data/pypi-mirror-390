"""
Text encoding with sentence transformers.

Provides embedding generation for semantic similarity matching.
"""

import logging
from typing import Any

import numpy as np

from neurobus.exceptions.semantic import EncodingError, ModelNotLoadedError
from neurobus.semantic.cache import EmbeddingCache

logger = logging.getLogger(__name__)


class SemanticEncoder:
    """
    Semantic text encoder using sentence transformers.

    Features:
    - Lazy model loading
    - Embedding caching
    - Batch encoding
    - GPU support
    - Multiple model support

    Attributes:
        model_name: Name of the sentence transformer model
        device: Device to run on ('cpu', 'cuda', 'mps')
        cache: Embedding cache instance

    Example:
        >>> encoder = SemanticEncoder(model_name="all-MiniLM-L6-v2")
        >>> embedding = encoder.encode("hello world")
        >>> similarity = encoder.similarity(embedding1, embedding2)
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str | None = None,
        cache_size: int = 10000,
        cache_ttl: float = 3600.0,
    ) -> None:
        """
        Initialize semantic encoder.

        Args:
            model_name: Sentence transformer model name
            device: Device to use (None = auto-detect)
            cache_size: Maximum cache entries
            cache_ttl: Cache TTL in seconds
        """
        self.model_name = model_name
        self.device = device

        # Lazy loading
        self._model: Any = None
        self._model_loaded = False

        # Embedding cache
        self.cache = EmbeddingCache(max_size=cache_size, ttl=cache_ttl)

        logger.info(f"SemanticEncoder initialized with model={model_name}, device={device}")

    def _load_model(self) -> None:
        """Load the sentence transformer model."""
        if self._model_loaded:
            return

        try:
            # Import here to make it optional
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name, device=self.device)
            self._model_loaded = True

            logger.info(
                f"Model loaded successfully: {self.model_name} "
                f"(dimensions: {self.embedding_dim})"
            )

        except ImportError as e:
            raise ModelNotLoadedError(
                self.model_name,
                "sentence-transformers not installed. "
                "Install with: pip install neurobus[semantic]",
            ) from e
        except Exception as e:
            raise ModelNotLoadedError(
                self.model_name,
                f"Failed to load model: {e}",
            ) from e

    @property
    def embedding_dim(self) -> int:
        """Get embedding dimensions."""
        if not self._model_loaded:
            raise ModelNotLoadedError(self.model_name, "Model not loaded yet")
        return self._model.get_sentence_embedding_dimension()

    def encode(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Encode text to embedding vector.

        Args:
            text: Text to encode
            use_cache: Whether to use cache

        Returns:
            Numpy array embedding

        Raises:
            EncodingError: If encoding fails
            ModelNotLoadedError: If model not loaded
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(text)
            if cached is not None:
                return cached

        # Ensure model is loaded
        if not self._model_loaded:
            self._load_model()

        try:
            # Encode text
            embedding = self._model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False,
            )

            # Normalize to unit vector
            embedding = embedding / np.linalg.norm(embedding)

            # Cache result
            if use_cache:
                self.cache.set(text, embedding)

            return embedding

        except Exception as e:
            raise EncodingError(
                text=text,
                model=self.model_name,
                original_error=e,
            ) from e

    def encode_batch(
        self,
        texts: list[str],
        use_cache: bool = True,
        batch_size: int = 32,
    ) -> list[np.ndarray]:
        """
        Encode multiple texts in batch.

        Args:
            texts: List of texts to encode
            use_cache: Whether to use cache
            batch_size: Batch size for encoding

        Returns:
            List of embeddings
        """
        if not texts:
            return []

        embeddings: list[np.ndarray] = []
        texts_to_encode: list[str] = []
        cache_indices: list[int] = []

        # Check cache for each text
        for i, text in enumerate(texts):
            if use_cache:
                cached = self.cache.get(text)
                if cached is not None:
                    embeddings.append(cached)
                    continue

            texts_to_encode.append(text)
            cache_indices.append(i)

        # Encode uncached texts
        if texts_to_encode:
            if not self._model_loaded:
                self._load_model()

            try:
                batch_embeddings = self._model.encode(
                    texts_to_encode,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                    batch_size=batch_size,
                )

                # Normalize and cache
                for text, embedding in zip(texts_to_encode, batch_embeddings):
                    normalized = embedding / np.linalg.norm(embedding)

                    if use_cache:
                        self.cache.set(text, normalized)

                    embeddings.append(normalized)

            except Exception as e:
                raise EncodingError(
                    text=f"batch of {len(texts_to_encode)} texts",
                    model=self.model_name,
                    original_error=e,
                ) from e

        return embeddings

    def similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1)
        """
        # Cosine similarity (embeddings are already normalized)
        similarity = float(np.dot(embedding1, embedding2))

        # Clamp to [0, 1] range
        return max(0.0, min(1.0, similarity))

    def similarity_batch(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: list[np.ndarray],
    ) -> list[float]:
        """
        Compute similarities between query and multiple candidates.

        Args:
            query_embedding: Query embedding
            candidate_embeddings: List of candidate embeddings

        Returns:
            List of similarity scores
        """
        if not candidate_embeddings:
            return []

        # Stack into matrix for efficient computation
        candidates_matrix = np.vstack(candidate_embeddings)

        # Batch dot product
        similarities = np.dot(candidates_matrix, query_embedding)

        # Clamp to [0, 1]
        similarities = np.clip(similarities, 0.0, 1.0)

        return similarities.tolist()

    def get_stats(self) -> dict[str, Any]:
        """
        Get encoder statistics.

        Returns:
            Dictionary with encoder stats
        """
        return {
            "model_name": self.model_name,
            "model_loaded": self._model_loaded,
            "embedding_dim": self.embedding_dim if self._model_loaded else None,
            "device": self.device,
            "cache": self.cache.get_stats(),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"SemanticEncoder("
            f"model={self.model_name}, "
            f"loaded={self._model_loaded}, "
            f"cache_size={len(self.cache)})"
        )
