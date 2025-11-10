"""Exceptions for memory layer."""

from neurobus.exceptions.core import NeuroBusError


class MemoryError(NeuroBusError):
    """Base exception for memory layer errors."""

    pass


class AdapterError(MemoryError):
    """Raised when memory adapter operations fail."""

    def __init__(self, adapter: str, operation: str, reason: str) -> None:
        """
        Initialize with adapter, operation, and reason.

        Args:
            adapter: Name of the adapter
            operation: Operation that failed
            reason: Why it failed
        """
        super().__init__(
            f"Adapter '{adapter}' {operation} failed: {reason}",
            {"adapter": adapter, "operation": operation, "reason": reason},
        )


class ConnectionError(MemoryError):
    """Raised when connection to memory store fails."""

    def __init__(self, store: str, reason: str) -> None:
        """
        Initialize with store and reason.

        Args:
            store: Name of the store (e.g., "Qdrant", "LanceDB")
            reason: Why connection failed
        """
        super().__init__(
            f"Failed to connect to {store}: {reason}", {"store": store, "reason": reason}
        )


class SearchError(MemoryError):
    """Raised when memory search fails."""

    def __init__(self, query: str, reason: str) -> None:
        """
        Initialize with query and reason.

        Args:
            query: Search query
            reason: Why search failed
        """
        super().__init__(
            f"Search failed: {reason}", {"query_preview": query[:100], "reason": reason}
        )


class PersistenceError(MemoryError):
    """Raised when memory persistence operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        """
        Initialize with operation and reason.

        Args:
            operation: Persistence operation
            reason: Why it failed
        """
        super().__init__(
            f"Persistence {operation} failed: {reason}", {"operation": operation, "reason": reason}
        )
