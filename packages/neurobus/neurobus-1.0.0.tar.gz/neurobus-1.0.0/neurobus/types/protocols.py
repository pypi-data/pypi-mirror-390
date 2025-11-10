"""
Protocol definitions for NeuroBUS components.

Protocols define interfaces for dependency injection and extensibility.
"""

from typing import Any, Protocol, runtime_checkable

from neurobus.core.event import Event
from neurobus.core.subscription import Subscription


@runtime_checkable
class EventDispatcherProtocol(Protocol):
    """Protocol for event dispatchers."""

    async def dispatch(
        self,
        event: Event,
        subscriptions: list[Subscription],
    ) -> None:
        """
        Dispatch an event to multiple subscriptions.

        Args:
            event: Event to dispatch
            subscriptions: List of subscriptions to notify
        """
        ...


@runtime_checkable
class SubscriptionRegistryProtocol(Protocol):
    """Protocol for subscription registries."""

    def add(self, subscription: Subscription) -> None:
        """
        Add a subscription to the registry.

        Args:
            subscription: Subscription to add
        """
        ...

    def remove(self, subscription_id: Any) -> bool:
        """
        Remove a subscription from the registry.

        Args:
            subscription_id: ID of subscription to remove

        Returns:
            True if removed, False if not found
        """
        ...

    def find_matches(self, event: Event) -> list[Subscription]:
        """
        Find all subscriptions matching an event.

        Args:
            event: Event to match

        Returns:
            List of matching subscriptions
        """
        ...

    def get_all(self) -> list[Subscription]:
        """
        Get all registered subscriptions.

        Returns:
            List of all subscriptions
        """
        ...


@runtime_checkable
class SemanticRouterProtocol(Protocol):
    """Protocol for semantic routers."""

    def encode(self, text: str) -> list[float]:
        """
        Encode text to embedding vector.

        Args:
            text: Text to encode

        Returns:
            Embedding vector
        """
        ...

    def compute_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """
        Compute similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0.0-1.0)
        """
        ...

    def find_semantic_matches(
        self,
        topic: str,
        patterns: list[str],
        threshold: float = 0.75,
    ) -> list[tuple[str, float]]:
        """
        Find semantically similar patterns.

        Args:
            topic: Topic to match
            patterns: List of patterns to match against
            threshold: Minimum similarity threshold

        Returns:
            List of (pattern, similarity) tuples
        """
        ...


@runtime_checkable
class ContextEngineProtocol(Protocol):
    """Protocol for context engines."""

    def set(self, key: str, value: Any, scope: str = "global") -> None:
        """
        Set a context variable.

        Args:
            key: Variable key (dot notation supported)
            value: Variable value
            scope: Scope (global, session, user)
        """
        ...

    def get(self, key: str, scope: str = "global") -> Any:
        """
        Get a context variable.

        Args:
            key: Variable key
            scope: Scope to search

        Returns:
            Variable value or None
        """
        ...

    def merge_context(self, event: Event) -> dict[str, Any]:
        """
        Merge all context for an event.

        Args:
            event: Event to merge context for

        Returns:
            Merged context dictionary
        """
        ...


@runtime_checkable
class TemporalStoreProtocol(Protocol):
    """Protocol for temporal event stores."""

    async def store(self, event: Event) -> None:
        """
        Store an event in the temporal log.

        Args:
            event: Event to store
        """
        ...

    async def query(
        self,
        from_time: Any | None = None,
        to_time: Any | None = None,
        topic: str | None = None,
    ) -> list[Event]:
        """
        Query events from the temporal store.

        Args:
            from_time: Start time
            to_time: End time
            topic: Optional topic filter

        Returns:
            List of matching events
        """
        ...

    async def replay(
        self,
        from_time: Any,
        to_time: Any,
        speed: float = 1.0,
    ) -> None:
        """
        Replay events in time range.

        Args:
            from_time: Start time
            to_time: End time
            speed: Playback speed multiplier
        """
        ...


@runtime_checkable
class MemoryAdapterProtocol(Protocol):
    """Protocol for vector memory adapters."""

    async def store_event(self, event: Event, embedding: list[float]) -> None:
        """
        Store event in vector memory.

        Args:
            event: Event to store
            embedding: Event embedding vector
        """
        ...

    async def search_similar(
        self,
        query: str,
        k: int = 5,
    ) -> list[tuple[Event, float]]:
        """
        Search for similar events.

        Args:
            query: Query string
            k: Number of results

        Returns:
            List of (event, similarity) tuples
        """
        ...


@runtime_checkable
class LLMProviderProtocol(Protocol):
    """Protocol for LLM providers."""

    async def invoke(self, prompt: str, context: dict[str, Any]) -> str:
        """
        Invoke LLM with prompt and context.

        Args:
            prompt: Prompt template
            context: Context variables

        Returns:
            LLM response text
        """
        ...

    def validate_api_key(self) -> bool:
        """
        Validate API key is present and valid.

        Returns:
            True if valid
        """
        ...
