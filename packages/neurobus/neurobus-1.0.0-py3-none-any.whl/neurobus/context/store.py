"""
Context storage for hierarchical context management.

Provides thread-safe, TTL-based context storage with scope-aware access.
"""

import time
from collections import defaultdict
from threading import RLock
from typing import Any

from neurobus.types.context import ContextData, ContextScope


class ContextEntry:
    """
    A single context entry with TTL support.

    Attributes:
        key: Context key
        value: Context value
        scope: Context scope (GLOBAL, SESSION, USER, EVENT)
        created_at: Creation timestamp
        expires_at: Expiration timestamp (0 = no expiry)
    """

    def __init__(
        self,
        key: str,
        value: Any,
        scope: ContextScope,
        ttl: float = 0.0,
    ) -> None:
        """
        Initialize context entry.

        Args:
            key: Context key
            value: Context value
            scope: Context scope
            ttl: Time-to-live in seconds (0 = no expiry)
        """
        self.key = key
        self.value = value
        self.scope = scope
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl if ttl > 0 else 0.0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at == 0:
            return False
        return time.time() > self.expires_at

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ContextEntry(key={self.key!r}, scope={self.scope.value}, "
            f"expired={self.is_expired()})"
        )


class ContextStore:
    """
    Thread-safe hierarchical context storage.

    Stores context at different scopes (GLOBAL, SESSION, USER, EVENT) with
    automatic TTL-based expiration and inheritance support.

    Features:
    - Hierarchical scopes (global → session → user → event)
    - TTL-based automatic expiration
    - Thread-safe operations
    - Efficient lookups with scope resolution
    - Statistics tracking

    Example:
        >>> store = ContextStore()
        >>> store.set("user_id", "alice", scope=ContextScope.SESSION, ttl=3600)
        >>> value = store.get("user_id", scope=ContextScope.SESSION)
    """

    def __init__(self, enable_auto_cleanup: bool = True) -> None:
        """
        Initialize context store.

        Args:
            enable_auto_cleanup: Whether to auto-clean expired entries on access
        """
        self.enable_auto_cleanup = enable_auto_cleanup

        # Storage: scope -> identifier -> key -> entry
        # For GLOBAL: identifier is always ""
        # For SESSION: identifier is session_id
        # For USER: identifier is user_id
        # For EVENT: identifier is event_id
        self._storage: dict[ContextScope, dict[str, dict[str, ContextEntry]]] = {
            ContextScope.GLOBAL: defaultdict(dict),
            ContextScope.SESSION: defaultdict(dict),
            ContextScope.USER: defaultdict(dict),
            ContextScope.EVENT: defaultdict(dict),
        }

        # Thread safety
        self._lock = RLock()

        # Statistics
        self._stats = {
            "sets": 0,
            "gets": 0,
            "hits": 0,
            "misses": 0,
            "expirations": 0,
            "cleanups": 0,
        }

    def set(
        self,
        key: str,
        value: Any,
        scope: ContextScope = ContextScope.GLOBAL,
        identifier: str = "",
        ttl: float = 0.0,
    ) -> None:
        """
        Set a context value.

        Args:
            key: Context key
            value: Context value
            scope: Context scope
            identifier: Scope identifier (session_id, user_id, event_id)
            ttl: Time-to-live in seconds (0 = no expiry)
        """
        with self._lock:
            entry = ContextEntry(key, value, scope, ttl)

            if scope == ContextScope.GLOBAL:
                identifier = ""  # Global uses empty identifier

            self._storage[scope][identifier][key] = entry
            self._stats["sets"] += 1

    def get(
        self,
        key: str,
        scope: ContextScope = ContextScope.GLOBAL,
        identifier: str = "",
        default: Any = None,
    ) -> Any:
        """
        Get a context value.

        Args:
            key: Context key
            scope: Context scope
            identifier: Scope identifier
            default: Default value if not found

        Returns:
            Context value or default
        """
        with self._lock:
            self._stats["gets"] += 1

            if scope == ContextScope.GLOBAL:
                identifier = ""

            # Check if scope and identifier exist
            if identifier not in self._storage[scope]:
                self._stats["misses"] += 1
                return default

            scope_storage = self._storage[scope][identifier]

            # Check if key exists
            if key not in scope_storage:
                self._stats["misses"] += 1
                return default

            entry = scope_storage[key]

            # Check expiration
            if entry.is_expired():
                del scope_storage[key]
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                return default

            self._stats["hits"] += 1
            return entry.value

    def get_hierarchical(
        self,
        key: str,
        scope: ContextScope,
        identifier: str = "",
        session_id: str = "",
        user_id: str = "",
        default: Any = None,
    ) -> Any:
        """
        Get context value with hierarchical fallback.

        Looks for key in order: scope → user → session → global

        Args:
            key: Context key
            scope: Starting scope
            identifier: Scope identifier
            session_id: Session ID (for fallback)
            user_id: User ID (for fallback)
            default: Default value

        Returns:
            Context value or default
        """
        # Try requested scope first
        value = self.get(key, scope, identifier)
        if value is not None:
            return value

        # Fallback hierarchy
        if scope == ContextScope.EVENT:
            # Try user scope
            if user_id:
                value = self.get(key, ContextScope.USER, user_id)
                if value is not None:
                    return value

            # Try session scope
            if session_id:
                value = self.get(key, ContextScope.SESSION, session_id)
                if value is not None:
                    return value

        elif scope == ContextScope.USER:
            # Try session scope
            if session_id:
                value = self.get(key, ContextScope.SESSION, session_id)
                if value is not None:
                    return value

        elif scope == ContextScope.SESSION:
            pass  # Skip to global

        # Try global scope
        value = self.get(key, ContextScope.GLOBAL)
        if value is not None:
            return value

        return default

    def delete(
        self,
        key: str,
        scope: ContextScope = ContextScope.GLOBAL,
        identifier: str = "",
    ) -> bool:
        """
        Delete a context value.

        Args:
            key: Context key
            scope: Context scope
            identifier: Scope identifier

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if scope == ContextScope.GLOBAL:
                identifier = ""

            if identifier not in self._storage[scope]:
                return False

            scope_storage = self._storage[scope][identifier]

            if key in scope_storage:
                del scope_storage[key]
                return True

            return False

    def clear_scope(
        self,
        scope: ContextScope,
        identifier: str = "",
    ) -> int:
        """
        Clear all context in a scope.

        Args:
            scope: Context scope
            identifier: Scope identifier (if not global)

        Returns:
            Number of entries cleared
        """
        with self._lock:
            if scope == ContextScope.GLOBAL:
                identifier = ""

            if identifier not in self._storage[scope]:
                return 0

            count = len(self._storage[scope][identifier])
            del self._storage[scope][identifier]
            return count

    def cleanup_expired(self) -> int:
        """
        Clean up all expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            count = 0

            for scope in ContextScope:
                for identifier in list(self._storage[scope].keys()):
                    scope_storage = self._storage[scope][identifier]

                    for key in list(scope_storage.keys()):
                        entry = scope_storage[key]
                        if entry.is_expired():
                            del scope_storage[key]
                            count += 1

                    # Remove empty scope storage
                    if not scope_storage:
                        del self._storage[scope][identifier]

            self._stats["cleanups"] += 1
            self._stats["expirations"] += count
            return count

    def get_all(
        self,
        scope: ContextScope,
        identifier: str = "",
    ) -> ContextData:
        """
        Get all context in a scope.

        Args:
            scope: Context scope
            identifier: Scope identifier

        Returns:
            Dictionary of all context in scope
        """
        with self._lock:
            if scope == ContextScope.GLOBAL:
                identifier = ""

            if identifier not in self._storage[scope]:
                return {}

            scope_storage = self._storage[scope][identifier]

            # Filter out expired entries
            result: ContextData = {}
            for key, entry in list(scope_storage.items()):
                if entry.is_expired():
                    del scope_storage[key]
                    self._stats["expirations"] += 1
                else:
                    result[key] = entry.value

            return result

    def get_stats(self) -> dict[str, Any]:
        """
        Get store statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_entries = sum(
                len(identifiers)
                for scope_storage in self._storage.values()
                for identifiers in scope_storage.values()
            )

            hit_rate = self._stats["hits"] / max(self._stats["gets"], 1)

            return {
                "total_entries": total_entries,
                "sets": self._stats["sets"],
                "gets": self._stats["gets"],
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": hit_rate,
                "expirations": self._stats["expirations"],
                "cleanups": self._stats["cleanups"],
                "scopes": {scope.value: len(self._storage[scope]) for scope in ContextScope},
            }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            self._stats = {
                "sets": 0,
                "gets": 0,
                "hits": 0,
                "misses": 0,
                "expirations": 0,
                "cleanups": 0,
            }

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"ContextStore("
            f"entries={stats['total_entries']}, "
            f"hit_rate={stats['hit_rate']:.1%})"
        )
