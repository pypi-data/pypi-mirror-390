"""
Subscription registry for managing event subscriptions.

The registry maintains a thread-safe collection of subscriptions
and provides efficient lookup by topic pattern.
"""

import threading
from collections import defaultdict
from typing import Any
from uuid import UUID

from neurobus.core.event import Event
from neurobus.core.subscription import Subscription
from neurobus.exceptions.core import (
    DuplicateSubscriptionError,
    RegistryFullError,
    SubscriptionNotFoundError,
)
from neurobus.utils.patterns import is_wildcard_pattern, wildcard_match


class SubscriptionRegistry:
    """
    Thread-safe registry for event subscriptions.

    Provides efficient O(1) lookup for exact matches and O(n) for
    wildcard patterns. Subscriptions are organized by topic for fast
    matching.

    Attributes:
        max_size: Maximum number of subscriptions allowed

    Example:
        >>> registry = SubscriptionRegistry(max_size=1000)
        >>> registry.add(subscription)
        >>> matches = registry.find_matches(event)
    """

    def __init__(self, max_size: int = 10000) -> None:
        """
        Initialize registry.

        Args:
            max_size: Maximum subscriptions allowed (0 = unlimited)
        """
        self.max_size = max_size

        # Exact topic matches: topic -> list of subscriptions
        self._exact_matches: dict[str, list[Subscription]] = defaultdict(list)

        # Wildcard patterns: pattern -> list of subscriptions
        self._wildcard_patterns: dict[str, list[Subscription]] = defaultdict(list)

        # All subscriptions by ID for fast lookup
        self._by_id: dict[UUID, Subscription] = {}

        # Thread safety
        self._lock = threading.RLock()

    def add(self, subscription: Subscription) -> None:
        """
        Add a subscription to the registry.

        Args:
            subscription: Subscription to add

        Raises:
            DuplicateSubscriptionError: If subscription ID already exists
            RegistryFullError: If registry is at maximum capacity
        """
        with self._lock:
            # Check if already exists
            if subscription.id in self._by_id:
                raise DuplicateSubscriptionError(str(subscription.id))

            # Check capacity
            if self.max_size > 0 and len(self._by_id) >= self.max_size:
                raise RegistryFullError(self.max_size)

            # Add to appropriate index
            if is_wildcard_pattern(subscription.pattern):
                self._wildcard_patterns[subscription.pattern].append(subscription)
            else:
                self._exact_matches[subscription.pattern].append(subscription)

            # Add to ID index
            self._by_id[subscription.id] = subscription

    def remove(self, subscription_id: UUID | str) -> bool:
        """
        Remove a subscription from the registry.

        Args:
            subscription_id: ID of subscription to remove

        Returns:
            True if removed, False if not found
        """
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)

        with self._lock:
            subscription = self._by_id.get(subscription_id)
            if subscription is None:
                return False

            # Remove from appropriate index
            if is_wildcard_pattern(subscription.pattern):
                pattern_subs = self._wildcard_patterns[subscription.pattern]
                pattern_subs.remove(subscription)
                if not pattern_subs:
                    del self._wildcard_patterns[subscription.pattern]
            else:
                exact_subs = self._exact_matches[subscription.pattern]
                exact_subs.remove(subscription)
                if not exact_subs:
                    del self._exact_matches[subscription.pattern]

            # Remove from ID index
            del self._by_id[subscription_id]

            return True

    def get(self, subscription_id: UUID | str) -> Subscription:
        """
        Get a subscription by ID.

        Args:
            subscription_id: Subscription ID

        Returns:
            Subscription instance

        Raises:
            SubscriptionNotFoundError: If subscription not found
        """
        if isinstance(subscription_id, str):
            subscription_id = UUID(subscription_id)

        with self._lock:
            subscription = self._by_id.get(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(str(subscription_id))
            return subscription

    def find_matches(self, event: Event) -> list[Subscription]:
        """
        Find all subscriptions matching an event.

        Performs exact topic matching and wildcard pattern matching.
        Returns subscriptions sorted by priority (descending).

        Args:
            event: Event to match

        Returns:
            List of matching subscriptions, sorted by priority
        """
        with self._lock:
            matches: list[Subscription] = []

            # Find exact matches (O(1))
            if event.topic in self._exact_matches:
                exact_subs = self._exact_matches[event.topic]
                # Filter by context if subscription has filters
                matches.extend([sub for sub in exact_subs if sub.should_handle(event)])

            # Find wildcard matches (O(n) where n = number of patterns)
            for pattern, pattern_subs in self._wildcard_patterns.items():
                if wildcard_match(pattern, event.topic):
                    # Filter by context if subscription has filters
                    matches.extend([sub for sub in pattern_subs if sub.should_handle(event)])

            # Sort by priority (higher priority first)
            matches.sort(key=lambda sub: sub.priority, reverse=True)

            return matches

    def find_by_pattern(self, pattern: str) -> list[Subscription]:
        """
        Find all subscriptions for a specific pattern.

        Args:
            pattern: Topic pattern

        Returns:
            List of subscriptions for that pattern
        """
        with self._lock:
            if is_wildcard_pattern(pattern):
                return list(self._wildcard_patterns.get(pattern, []))
            else:
                return list(self._exact_matches.get(pattern, []))

    def get_all(self) -> list[Subscription]:
        """
        Get all registered subscriptions.

        Returns:
            List of all subscriptions
        """
        with self._lock:
            return list(self._by_id.values())

    def count(self) -> int:
        """
        Get the number of registered subscriptions.

        Returns:
            Subscription count
        """
        with self._lock:
            return len(self._by_id)

    def clear(self) -> None:
        """Clear all subscriptions from the registry."""
        with self._lock:
            self._exact_matches.clear()
            self._wildcard_patterns.clear()
            self._by_id.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary of statistics
        """
        with self._lock:
            return {
                "total_subscriptions": len(self._by_id),
                "exact_patterns": len(self._exact_matches),
                "wildcard_patterns": len(self._wildcard_patterns),
                "capacity": self.max_size,
                "utilization": (len(self._by_id) / self.max_size if self.max_size > 0 else 0.0),
            }

    def __len__(self) -> int:
        """Get the number of subscriptions."""
        return self.count()

    def __contains__(self, subscription_id: UUID | str) -> bool:
        """Check if subscription exists in registry."""
        if isinstance(subscription_id, str):
            try:
                subscription_id = UUID(subscription_id)
            except ValueError:
                return False

        with self._lock:
            return subscription_id in self._by_id

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_stats()
        return (
            f"SubscriptionRegistry("
            f"total={stats['total_subscriptions']}, "
            f"exact={stats['exact_patterns']}, "
            f"wildcard={stats['wildcard_patterns']})"
        )
