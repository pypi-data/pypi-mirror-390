"""
Context engine for hierarchical context management.

Provides high-level API for managing and querying contextual state.
"""

import logging
from collections.abc import Callable
from typing import Any

from neurobus.context.store import ContextStore
from neurobus.core.event import Event
from neurobus.types.context import ContextData, ContextScope
from neurobus.utils.helpers import deep_merge

logger = logging.getLogger(__name__)


class ContextEngine:
    """
    High-level context management engine.

    Manages hierarchical context across different scopes with automatic
    inheritance, merging, and expiration.

    Features:
    - Hierarchical context (global → session → user → event)
    - Context inheritance with scope resolution
    - Deep merging of context dictionaries
    - TTL-based automatic expiration
    - Context snapshots for events
    - Query and filtering support

    Example:
        >>> engine = ContextEngine()
        >>> engine.set_global("app_version", "1.0.0")
        >>> engine.set_session("session_123", "user_id", "alice", ttl=3600)
        >>> context = engine.get_merged_context("session_123")
    """

    def __init__(
        self,
        store: ContextStore | None = None,
        default_ttl: dict[ContextScope, float] | None = None,
    ) -> None:
        """
        Initialize context engine.

        Args:
            store: Optional custom context store
            default_ttl: Default TTL per scope (seconds)
        """
        self.store = store or ContextStore()

        self.default_ttl = default_ttl or {
            ContextScope.GLOBAL: 0.0,  # Never expires
            ContextScope.SESSION: 3600.0,  # 1 hour
            ContextScope.USER: 7200.0,  # 2 hours
            ContextScope.EVENT: 300.0,  # 5 minutes
        }

        logger.info("ContextEngine initialized")

    # Global context

    def set_global(self, key: str, value: Any, ttl: float | None = None) -> None:
        """
        Set global context value.

        Args:
            key: Context key
            value: Context value
            ttl: Optional TTL (uses default if None)
        """
        ttl = ttl if ttl is not None else self.default_ttl[ContextScope.GLOBAL]
        self.store.set(key, value, ContextScope.GLOBAL, ttl=ttl)

    def get_global(self, key: str, default: Any = None) -> Any:
        """Get global context value."""
        return self.store.get(key, ContextScope.GLOBAL, default=default)

    def get_all_global(self) -> ContextData:
        """Get all global context."""
        return self.store.get_all(ContextScope.GLOBAL)

    # Session context

    def set_session(
        self,
        session_id: str,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """
        Set session context value.

        Args:
            session_id: Session identifier
            key: Context key
            value: Context value
            ttl: Optional TTL
        """
        ttl = ttl if ttl is not None else self.default_ttl[ContextScope.SESSION]
        self.store.set(key, value, ContextScope.SESSION, session_id, ttl=ttl)

    def get_session(
        self,
        session_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get session context value."""
        return self.store.get(key, ContextScope.SESSION, session_id, default)

    def get_all_session(self, session_id: str) -> ContextData:
        """Get all session context."""
        return self.store.get_all(ContextScope.SESSION, session_id)

    def clear_session(self, session_id: str) -> int:
        """Clear all session context."""
        return self.store.clear_scope(ContextScope.SESSION, session_id)

    # User context

    def set_user(
        self,
        user_id: str,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """
        Set user context value.

        Args:
            user_id: User identifier
            key: Context key
            value: Context value
            ttl: Optional TTL
        """
        ttl = ttl if ttl is not None else self.default_ttl[ContextScope.USER]
        self.store.set(key, value, ContextScope.USER, user_id, ttl=ttl)

    def get_user(
        self,
        user_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get user context value."""
        return self.store.get(key, ContextScope.USER, user_id, default)

    def get_all_user(self, user_id: str) -> ContextData:
        """Get all user context."""
        return self.store.get_all(ContextScope.USER, user_id)

    def clear_user(self, user_id: str) -> int:
        """Clear all user context."""
        return self.store.clear_scope(ContextScope.USER, user_id)

    # Event context

    def set_event(
        self,
        event_id: str,
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        """
        Set event-specific context.

        Args:
            event_id: Event identifier
            key: Context key
            value: Context value
            ttl: Optional TTL
        """
        ttl = ttl if ttl is not None else self.default_ttl[ContextScope.EVENT]
        self.store.set(key, value, ContextScope.EVENT, event_id, ttl=ttl)

    def get_event(
        self,
        event_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """Get event context value."""
        return self.store.get(key, ContextScope.EVENT, event_id, default)

    def get_all_event(self, event_id: str) -> ContextData:
        """Get all event context."""
        return self.store.get_all(ContextScope.EVENT, event_id)

    def clear_event(self, event_id: str) -> int:
        """Clear event context."""
        return self.store.clear_scope(ContextScope.EVENT, event_id)

    # Hierarchical context

    def get_merged_context(
        self,
        session_id: str = "",
        user_id: str = "",
        event_id: str = "",
    ) -> ContextData:
        """
        Get merged context from all scopes.

        Merges context in order: global → session → user → event
        Later scopes override earlier ones.

        Args:
            session_id: Optional session ID
            user_id: Optional user ID
            event_id: Optional event ID

        Returns:
            Merged context dictionary
        """
        # Start with global
        context = self.get_all_global().copy()

        # Merge session
        if session_id:
            session_ctx = self.get_all_session(session_id)
            context = deep_merge(context, session_ctx)

        # Merge user
        if user_id:
            user_ctx = self.get_all_user(user_id)
            context = deep_merge(context, user_ctx)

        # Merge event
        if event_id:
            event_ctx = self.get_all_event(event_id)
            context = deep_merge(context, event_ctx)

        return context

    def enrich_event(self, event: Event) -> Event:
        """
        Enrich event with hierarchical context.

        Merges context from global → session → user → event scopes
        and updates the event's context.

        Args:
            event: Event to enrich

        Returns:
            Event with enriched context
        """
        # Extract identifiers from event context
        session_id = event.context.get("session_id", "")
        user_id = event.context.get("user_id", "")
        event_id = str(event.id)

        # Get merged context
        merged = self.get_merged_context(session_id, user_id, event_id)

        # Merge with event's existing context (event context takes precedence)
        enriched_context = deep_merge(merged, event.context)

        # Return event with enriched context
        return event.with_context(**enriched_context)

    def query_context(
        self,
        scope: ContextScope,
        identifier: str = "",
        filter_func: Callable[[str, Any], bool] | None = None,
    ) -> ContextData:
        """
        Query context with optional filtering.

        Args:
            scope: Context scope
            identifier: Scope identifier
            filter_func: Optional filter function (key, value) -> bool

        Returns:
            Filtered context dictionary
        """
        all_context = self.store.get_all(scope, identifier)

        if filter_func is None:
            return all_context

        return {key: value for key, value in all_context.items() if filter_func(key, value)}

    def cleanup_expired(self) -> int:
        """
        Clean up expired context entries.

        Returns:
            Number of entries removed
        """
        count = self.store.cleanup_expired()
        logger.debug(f"Cleaned up {count} expired context entries")
        return count

    def get_stats(self) -> dict[str, Any]:
        """
        Get context engine statistics.

        Returns:
            Dictionary with statistics
        """
        store_stats = self.store.get_stats()

        return {
            "store": store_stats,
            "default_ttl": {scope.value: ttl for scope, ttl in self.default_ttl.items()},
        }

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"ContextEngine("
            f"entries={stats['store']['total_entries']}, "
            f"hit_rate={stats['store']['hit_rate']:.1%})"
        )
