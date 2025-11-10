"""Exceptions for temporal layer."""

from neurobus.exceptions.core import NeuroBusError


class TemporalError(NeuroBusError):
    """Base exception for temporal layer errors."""

    pass


class StoreError(TemporalError):
    """Raised when storage operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        """
        Initialize with operation and reason.

        Args:
            operation: Storage operation that failed
            reason: Why it failed
        """
        super().__init__(
            f"Storage {operation} failed: {reason}", {"operation": operation, "reason": reason}
        )


class QueryError(TemporalError):
    """Raised when temporal queries fail."""

    def __init__(self, reason: str) -> None:
        """
        Initialize with reason.

        Args:
            reason: Why query failed
        """
        super().__init__(f"Query failed: {reason}", {"reason": reason})


class ReplayError(TemporalError):
    """Raised when event replay fails."""

    def __init__(self, reason: str) -> None:
        """
        Initialize with reason.

        Args:
            reason: Why replay failed
        """
        super().__init__(f"Replay failed: {reason}", {"reason": reason})


class WALError(TemporalError):
    """Raised when write-ahead log operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        """
        Initialize with operation and reason.

        Args:
            operation: WAL operation that failed
            reason: Why it failed
        """
        super().__init__(
            f"WAL {operation} failed: {reason}", {"operation": operation, "reason": reason}
        )
