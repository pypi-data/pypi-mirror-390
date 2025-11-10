"""Core exceptions for NeuroBUS."""


class NeuroBusError(Exception):
    """Base exception for all NeuroBUS errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """
        Initialize exception with message and optional details.

        Args:
            message: Error message
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class BusNotStartedError(NeuroBusError):
    """Raised when operations are attempted on a non-started bus."""

    def __init__(self) -> None:
        """Initialize with standard message."""
        super().__init__(
            "Bus has not been started. Call await bus.start() first.",
            {"suggestion": "Use async context manager: async with bus: ..."},
        )


class BusAlreadyStartedError(NeuroBusError):
    """Raised when attempting to start an already started bus."""

    def __init__(self) -> None:
        """Initialize with standard message."""
        super().__init__(
            "Bus is already started.", {"suggestion": "Check bus.is_running before calling start()"}
        )


class BusShutdownError(NeuroBusError):
    """Raised when operations are attempted during shutdown."""

    def __init__(self) -> None:
        """Initialize with standard message."""
        super().__init__(
            "Bus is shutting down. No new operations allowed.",
        )


class SubscriptionError(NeuroBusError):
    """Base exception for subscription-related errors."""

    pass


class InvalidSubscriptionError(SubscriptionError):
    """Raised when a subscription is invalid."""

    def __init__(self, reason: str) -> None:
        """
        Initialize with reason.

        Args:
            reason: Why the subscription is invalid
        """
        super().__init__(
            f"Invalid subscription: {reason}",
        )


class SubscriptionNotFoundError(SubscriptionError):
    """Raised when a subscription cannot be found."""

    def __init__(self, subscription_id: str) -> None:
        """
        Initialize with subscription ID.

        Args:
            subscription_id: ID of the missing subscription
        """
        super().__init__(
            f"Subscription not found: {subscription_id}", {"subscription_id": subscription_id}
        )


class DuplicateSubscriptionError(SubscriptionError):
    """Raised when attempting to add a duplicate subscription."""

    def __init__(self, subscription_id: str) -> None:
        """
        Initialize with subscription ID.

        Args:
            subscription_id: ID of the duplicate subscription
        """
        super().__init__(
            f"Subscription already exists: {subscription_id}", {"subscription_id": subscription_id}
        )


class DispatchError(NeuroBusError):
    """Base exception for event dispatch errors."""

    pass


class DispatchTimeoutError(DispatchError):
    """Raised when event dispatch times out."""

    def __init__(self, timeout: float, event_id: str) -> None:
        """
        Initialize with timeout and event ID.

        Args:
            timeout: Timeout duration in seconds
            event_id: ID of the event that timed out
        """
        super().__init__(
            f"Event dispatch timed out after {timeout}s", {"timeout": timeout, "event_id": event_id}
        )


class HandlerError(NeuroBusError):
    """Wrapper for errors that occur in event handlers."""

    def __init__(
        self,
        handler_name: str,
        event_id: str,
        original_error: Exception,
    ) -> None:
        """
        Initialize with handler info and original error.

        Args:
            handler_name: Name of the handler that failed
            event_id: ID of the event being handled
            original_error: The original exception
        """
        super().__init__(
            f"Handler '{handler_name}' failed: {original_error}",
            {
                "handler": handler_name,
                "event_id": event_id,
                "error_type": type(original_error).__name__,
            },
        )
        self.original_error = original_error


class RegistryError(NeuroBusError):
    """Base exception for registry errors."""

    pass


class RegistryFullError(RegistryError):
    """Raised when registry reaches maximum capacity."""

    def __init__(self, max_size: int) -> None:
        """
        Initialize with maximum size.

        Args:
            max_size: Maximum registry capacity
        """
        super().__init__(f"Registry is full (max: {max_size})", {"max_size": max_size})


class ValidationError(NeuroBusError):
    """Raised when data validation fails."""

    def __init__(self, field: str, reason: str) -> None:
        """
        Initialize with field and reason.

        Args:
            field: Field that failed validation
            reason: Why validation failed
        """
        super().__init__(
            f"Validation failed for '{field}': {reason}", {"field": field, "reason": reason}
        )


class ConfigurationError(NeuroBusError):
    """Raised when configuration is invalid."""

    def __init__(self, key: str, reason: str) -> None:
        """
        Initialize with config key and reason.

        Args:
            key: Configuration key that is invalid
            reason: Why configuration is invalid
        """
        super().__init__(
            f"Invalid configuration for '{key}': {reason}", {"key": key, "reason": reason}
        )
