"""
Subscription model for event handlers in NeuroBUS.

Subscriptions define how handlers receive and filter events.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from neurobus.core.event import Event

# Type alias for event handlers
EventHandler = Callable[[Event], Awaitable[None]]


@dataclass
class Subscription:
    """
    Represents a subscription to events on the bus.

    Subscriptions can match events by exact topic, semantic similarity,
    or context filters.

    Attributes:
        id: Unique subscription identifier
        pattern: Topic pattern to match (exact or semantic)
        handler: Async function to call when event matches
        semantic: Whether to use semantic matching (default: False)
        threshold: Similarity threshold for semantic matching (0.0-1.0)
        filter_func: Optional callable to filter events by context
        filter_expr: Optional filter DSL expression string
        priority: Handler execution priority (higher = earlier)
        metadata: Additional subscription metadata

    Example:
        >>> async def handle_login(event: Event):
        ...     print(f"User logged in: {event.data['username']}")
        >>>
        >>> sub = Subscription(
        ...     pattern="user.login",
        ...     handler=handle_login,
        ...     semantic=False
        ... )
    """

    pattern: str
    handler: EventHandler
    id: UUID = field(default_factory=uuid4)
    semantic: bool = False
    threshold: float = 0.75
    filter_func: Callable[[Event], bool] | None = None
    filter_expr: str | None = None
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate subscription after initialization."""
        if not self.pattern:
            raise ValueError("Subscription pattern cannot be empty")

        if not callable(self.handler):
            raise TypeError("Subscription handler must be callable")

        # Validate threshold only if provided (None is allowed for non-semantic subscriptions)
        if self.threshold is not None:
            if not 0.0 <= self.threshold <= 1.0:
                raise ValueError(f"Threshold must be between 0.0 and 1.0, got {self.threshold}")

            if self.semantic and self.threshold < 0.5:
                raise ValueError("Semantic threshold should typically be >= 0.5")

    def matches_exact(self, topic: str) -> bool:
        """
        Check if topic matches pattern exactly.

        Args:
            topic: Topic to match against

        Returns:
            True if topic matches pattern exactly
        """
        return self.pattern == topic

    def should_handle(self, event: Event) -> bool:
        """
        Determine if this subscription should handle the event.

        Applies filter function if present.

        Args:
            event: Event to check

        Returns:
            True if subscription should handle event
        """
        if self.filter_func is not None:
            try:
                return self.filter_func(event)
            except Exception:
                # If filter fails, don't handle the event
                return False
        return True

    async def handle_event(self, event: Event) -> None:
        """
        Invoke the handler for this subscription.

        Args:
            event: Event to handle

        Raises:
            Any exception raised by the handler
        """
        await self.handler(event)

    def __repr__(self) -> str:
        """String representation for debugging."""
        semantic_str = f", semantic={self.semantic}" if self.semantic else ""
        filter_str = ", filtered" if self.filter_func or self.filter_expr else ""
        return (
            f"Subscription(id={str(self.id)[:8]}, pattern={self.pattern!r}"
            f"{semantic_str}{filter_str}, priority={self.priority})"
        )

    def __hash__(self) -> int:
        """Hash based on subscription ID."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Equality based on subscription ID."""
        if not isinstance(other, Subscription):
            return NotImplemented
        return self.id == other.id
