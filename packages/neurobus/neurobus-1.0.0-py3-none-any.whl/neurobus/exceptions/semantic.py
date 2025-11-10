"""Exceptions for semantic layer."""

from neurobus.exceptions.core import NeuroBusError


class SemanticError(NeuroBusError):
    """Base exception for semantic layer errors."""

    pass


class EncodingError(SemanticError):
    """Raised when embedding encoding fails."""

    def __init__(self, text: str, reason: str) -> None:
        """
        Initialize with text and reason.

        Args:
            text: Text that failed to encode
            reason: Why encoding failed
        """
        super().__init__(
            f"Failed to encode text: {reason}", {"text_preview": text[:100], "reason": reason}
        )


class ModelNotLoadedError(SemanticError):
    """Raised when attempting to use unloaded model."""

    def __init__(self, model_name: str) -> None:
        """
        Initialize with model name.

        Args:
            model_name: Name of the model
        """
        super().__init__(f"Model not loaded: {model_name}", {"model": model_name})


class CacheError(SemanticError):
    """Raised when cache operations fail."""

    pass


class SimilarityComputationError(SemanticError):
    """Raised when similarity computation fails."""

    def __init__(self, reason: str) -> None:
        """
        Initialize with reason.

        Args:
            reason: Why computation failed
        """
        super().__init__(f"Similarity computation failed: {reason}", {"reason": reason})
