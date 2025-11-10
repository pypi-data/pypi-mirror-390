"""Semantic routing layer for meaning-based event matching."""

from neurobus.semantic.cache import EmbeddingCache
from neurobus.semantic.encoder import SemanticEncoder
from neurobus.semantic.router import SemanticRouter

__all__ = [
    "EmbeddingCache",
    "SemanticEncoder",
    "SemanticRouter",
]
