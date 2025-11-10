"""
Similarity computation utilities for semantic matching.

Provides various distance/similarity metrics for vector embeddings.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score (0-1, higher is more similar)

    Example:
        >>> v1 = np.array([1, 2, 3])
        >>> v2 = np.array([2, 3, 4])
        >>> cosine_similarity(v1, v2)
        0.9925...
    """
    # Normalize vectors
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Compute dot product
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)

    # Clamp to [0, 1] range
    return float(np.clip(similarity, 0.0, 1.0))


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute Euclidean distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Distance (lower is more similar)
    """
    return float(np.linalg.norm(vec1 - vec2))


def manhattan_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute Manhattan (L1) distance between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Distance (lower is more similar)
    """
    return float(np.sum(np.abs(vec1 - vec2)))


def dot_product_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute dot product similarity.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score
    """
    return float(np.dot(vec1, vec2))


def batch_cosine_similarity(
    query: np.ndarray,
    vectors: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between query and batch of vectors.

    Optimized for computing similarity against many vectors at once.

    Args:
        query: Query vector (1D)
        vectors: Matrix of vectors (2D, each row is a vector)

    Returns:
        Array of similarity scores
    """
    # Normalize query
    query_norm = query / np.linalg.norm(query)

    # Normalize vectors
    vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    # Compute all similarities at once
    similarities = np.dot(vectors_norm, query_norm)

    # Clamp to [0, 1]
    return np.clip(similarities, 0.0, 1.0)


def find_top_k_similar(
    query: np.ndarray,
    vectors: np.ndarray,
    k: int = 5,
    metric: str = "cosine",
) -> tuple[np.ndarray, np.ndarray]:
    """
    Find top-k most similar vectors.

    Args:
        query: Query vector
        vectors: Matrix of candidate vectors
        k: Number of results to return
        metric: Similarity metric ("cosine", "euclidean", "manhattan", "dot")

    Returns:
        Tuple of (indices, scores) for top-k matches
    """
    if metric == "cosine":
        scores = batch_cosine_similarity(query, vectors)
        # For cosine, higher is better
        top_k_idx = np.argsort(scores)[-k:][::-1]
        top_k_scores = scores[top_k_idx]

    elif metric == "euclidean":
        # Compute distances
        distances = np.linalg.norm(vectors - query, axis=1)
        # For distance, lower is better
        top_k_idx = np.argsort(distances)[:k]
        top_k_scores = distances[top_k_idx]

    elif metric == "manhattan":
        # Compute L1 distances
        distances = np.sum(np.abs(vectors - query), axis=1)
        top_k_idx = np.argsort(distances)[:k]
        top_k_scores = distances[top_k_idx]

    elif metric == "dot":
        # Compute dot products
        scores = np.dot(vectors, query)
        top_k_idx = np.argsort(scores)[-k:][::-1]
        top_k_scores = scores[top_k_idx]

    else:
        raise ValueError(f"Unknown metric: {metric}")

    return top_k_idx, top_k_scores
