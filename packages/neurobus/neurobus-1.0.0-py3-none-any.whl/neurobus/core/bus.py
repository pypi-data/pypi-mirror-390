"""
Main NeuroBUS event bus implementation.

The NeuroBus class is the primary interface for event-driven communication
in cognitive AI systems.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any
from uuid import UUID

from neurobus.config.schema import NeuroBusConfig
from neurobus.core.dispatcher import EventDispatcher
from neurobus.core.event import Event
from neurobus.core.lifecycle import LifecycleManager
from neurobus.core.registry import SubscriptionRegistry
from neurobus.core.subscription import EventHandler, Subscription
from neurobus.exceptions.core import BusNotStartedError
from neurobus.utils.validation import validate_topic

logger = logging.getLogger(__name__)


class NeuroBus:
    """
    Universal Neuro-Semantic Event Bus.

    NeuroBUS provides a high-performance, context-aware event bus for
    cognitive AI systems. It supports exact topic matching, wildcard
    patterns, and (in Phase 2+) semantic similarity matching.

    Features:
    - Async pub/sub with exact topic matching
    - Wildcard pattern subscriptions (*, #)
    - Semantic similarity matching (Phase 2)
    - Hybrid routing (pattern + semantic)
    - Parallel handler execution with error isolation
    - Decorator-based subscription API
    - Lifecycle management (start/stop)
    - Thread-safe registry

    Example:
        >>> bus = NeuroBus()
        >>>
        >>> @bus.subscribe("user.login")
        >>> async def handle_login(event: Event):
        ...     print(f"User logged in: {event.data}")
        >>>
        >>> async with bus:
        ...     await bus.publish(Event(
        ...         topic="user.login",
        ...         data={"username": "alice"}
        ...     ))
    """

    def __init__(self, config: NeuroBusConfig | None = None) -> None:
        """
        Initialize NeuroBUS.

        Args:
            config: Optional configuration (uses defaults if not provided)
        """
        from neurobus.config.defaults import get_default_config

        self.config = config or get_default_config()

        # Core components
        self._registry = SubscriptionRegistry(max_size=self.config.core.max_subscriptions)
        self._dispatcher = EventDispatcher(
            enable_parallel=self.config.core.enable_parallel_dispatch,
            enable_error_isolation=self.config.core.enable_error_isolation,
            handler_timeout=self.config.core.handler_timeout,
            max_concurrent=self.config.core.max_concurrent_handlers,
        )
        self._lifecycle = LifecycleManager()

        # Semantic router (lazy-loaded)
        self._semantic_router: Any = None

        # Context engine (optional)
        self._context_engine: Any = None
        if self.config.context.enabled:
            self._init_context_engine()

        # Temporal engine (optional)
        self._temporal_engine: Any = None
        if self.config.temporal.enabled:
            self._init_temporal_engine()

        # Memory engine (optional)
        self._memory_engine: Any = None
        if self.config.memory.enabled:
            self._init_memory_engine()

        # Reasoning engine (optional)
        self._reasoning_engine: Any = None
        if self.config.llm.enabled:
            self._init_reasoning_engine()

        # Cluster manager (optional)
        self._cluster_manager: Any = None
        if self.config.distributed.enabled:
            self._init_cluster_manager()

        logger.info("NeuroBUS instance created", extra={"config": self.config.to_dict()})

    @property
    def is_running(self) -> bool:
        """Check if bus is running."""
        return self._lifecycle.is_running

    @property
    def state(self) -> str:
        """Get current bus state."""
        return self._lifecycle.state.value

    async def start(self) -> None:
        """
        Start the event bus.

        Must be called before publishing or subscribing to events.
        Alternatively, use the async context manager.

        Example:
            >>> await bus.start()
            >>> # ... use bus ...
            >>> await bus.stop()

            Or:

            >>> async with bus:
            ...     # bus is automatically started and stopped
            ...     await bus.publish(event)
        """
        await self._lifecycle.start()

        # Initialize temporal engine if enabled
        if self._temporal_engine is not None:
            await self._temporal_engine.initialize()

        # Initialize memory engine if enabled
        if self._memory_engine is not None:
            await self._memory_engine.initialize()

        # Initialize reasoning engine if enabled
        if self._reasoning_engine is not None:
            await self._reasoning_engine.initialize()

        # Start cluster manager if enabled
        if self._cluster_manager is not None:
            await self._cluster_manager.start()

        logger.info("NeuroBUS ready for events")

    async def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the event bus gracefully.

        Args:
            timeout: Maximum time to wait for shutdown
        """
        # Stop cluster manager if enabled
        if self._cluster_manager is not None:
            await self._cluster_manager.stop()

        await self._lifecycle.stop(timeout)
        logger.info("NeuroBUS stopped")

    async def publish(self, event: Event) -> None:
        """
        Publish an event to the bus.

        The event will be dispatched to all matching subscriptions.
        Handlers are executed asynchronously with error isolation.

        Args:
            event: Event to publish

        Raises:
            BusNotStartedError: If bus is not running
            ValidationError: If event is invalid

        Example:
            >>> await bus.publish(Event(
            ...     topic="user.login",
            ...     data={"username": "alice", "timestamp": "2024-01-01"}
            ... ))
        """
        if not self.is_running:
            raise BusNotStartedError()

        # Validate event topic
        validate_topic(event.topic)

        # Enrich event with hierarchical context if enabled
        if self._context_engine is not None:
            event = self._context_engine.enrich_event(event)

        # Persist event if temporal engine enabled
        if self._temporal_engine is not None:
            await self._temporal_engine.store_event(event)

        # Remember event in memory if enabled
        if self._memory_engine is not None:
            await self._memory_engine.remember_event(event)

        # Broadcast to cluster if enabled
        if self._cluster_manager is not None:
            await self._cluster_manager.broadcast_event(event)

        logger.debug(
            "Publishing event",
            extra={
                "event_id": str(event.id),
                "topic": event.topic,
            },
        )

        # Find matching subscriptions (pattern-based)
        pattern_matches = self._registry.find_matches(event)

        # Add semantic matches if enabled
        semantic_matches: list[tuple[Subscription, float]] = []
        if self.config.semantic.enabled and self._semantic_router is not None:
            try:
                semantic_matches = self._semantic_router.find_semantic_matches(
                    event,
                    self._registry.get_all(),
                    threshold=self.config.semantic.similarity_threshold,
                )
            except Exception as e:
                logger.warning(f"Semantic matching failed: {e}", exc_info=True)

        # Combine matches (pattern + semantic)
        # Remove duplicates and sort by priority/similarity
        all_subscriptions = self._merge_matches(pattern_matches, semantic_matches)

        if not all_subscriptions:
            logger.debug(
                "No subscribers for event",
                extra={
                    "event_id": str(event.id),
                    "topic": event.topic,
                },
            )
            return

        logger.debug(
            f"Dispatching to {len(all_subscriptions)} subscription(s)",
            extra={
                "event_id": str(event.id),
                "topic": event.topic,
                "subscription_count": len(all_subscriptions),
                "pattern_matches": len(pattern_matches),
                "semantic_matches": len(semantic_matches),
            },
        )

        # Dispatch to handlers
        await self._dispatcher.dispatch(event, all_subscriptions)

    def subscribe(
        self,
        pattern: str,
        handler: EventHandler | None = None,
        priority: int = 0,
        filter: Callable[[Event], bool] | None = None,
        semantic: bool = False,
        threshold: float | None = None,
    ) -> Callable[[EventHandler], EventHandler] | Subscription:
        """
        Subscribe to events matching a pattern.

        Can be used as a decorator or called directly.

        Args:
            pattern: Topic pattern (supports wildcards: *, #) or semantic description
            handler: Optional handler function (for direct call)
            priority: Handler execution priority (higher = earlier)
            filter: Optional filter function to gate events
            semantic: Enable semantic similarity matching
            threshold: Similarity threshold for semantic matching (0-1)

        Returns:
            Decorator function if handler is None, otherwise Subscription

        Examples:
            As decorator:
            >>> @bus.subscribe("user.*")
            >>> async def handle_user_events(event: Event):
            ...     print(f"User event: {event.topic}")

            Semantic subscription:
            >>> @bus.subscribe("user authentication", semantic=True, threshold=0.8)
            >>> async def handle_auth(event: Event):
            ...     # Matches events semantically similar to "user authentication"
            ...     pass

            With priority:
            >>> @bus.subscribe("critical.*", priority=100)
            >>> async def handle_critical(event: Event):
            ...     # Executes before lower priority handlers
            ...     pass

            With filter:
            >>> @bus.subscribe("message", filter=lambda e: e.data.get("urgent"))
            >>> async def handle_urgent(event: Event):
            ...     # Only receives urgent messages
            ...     pass
        """
        if handler is not None:
            # Direct call
            subscription = Subscription(
                pattern=pattern,
                handler=handler,
                priority=priority,
                filter_func=filter,
                semantic=semantic,
                threshold=threshold,
            )
            self._registry.add(subscription)

            logger.info(
                "Handler subscribed",
                extra={
                    "pattern": pattern,
                    "subscription_id": str(subscription.id),
                    "priority": priority,
                },
            )

            return subscription

        # Decorator
        def decorator(func: EventHandler) -> EventHandler:
            subscription = Subscription(
                pattern=pattern,
                handler=func,
                priority=priority,
                filter_func=filter,
                semantic=semantic,
                threshold=threshold,
            )
            self._registry.add(subscription)

            logger.info(
                "Handler subscribed (decorator)",
                extra={
                    "pattern": pattern,
                    "subscription_id": str(subscription.id),
                    "handler": func.__name__,
                    "priority": priority,
                    "semantic": semantic,
                },
            )

            return func

        return decorator

    def unsubscribe(self, subscription: Subscription | UUID | str) -> bool:
        """
        Unsubscribe a handler from events.

        Args:
            subscription: Subscription instance or ID

        Returns:
            True if unsubscribed, False if not found

        Example:
            >>> subscription = bus.subscribe("test", handler=my_handler)
            >>> bus.unsubscribe(subscription)
            True
        """
        if isinstance(subscription, Subscription):
            subscription_id = subscription.id
        else:
            subscription_id = subscription if isinstance(subscription, UUID) else UUID(subscription)

        removed = self._registry.remove(subscription_id)

        if removed:
            logger.info(
                "Handler unsubscribed",
                extra={"subscription_id": str(subscription_id)},
            )
        else:
            logger.warning(
                "Subscription not found",
                extra={"subscription_id": str(subscription_id)},
            )

        return removed

    def get_subscriptions(self, pattern: str | None = None) -> list[Subscription]:
        """
        Get all subscriptions, optionally filtered by pattern.

        Args:
            pattern: Optional pattern to filter by

        Returns:
            List of subscriptions

        Example:
            >>> all_subs = bus.get_subscriptions()
            >>> user_subs = bus.get_subscriptions("user.*")
        """
        if pattern:
            return self._registry.find_by_pattern(pattern)
        return self._registry.get_all()

    def clear_subscriptions(self) -> None:
        """
        Remove all subscriptions from the bus.

        Warning: This will remove ALL handlers.
        """
        self._registry.clear()
        logger.warning("All subscriptions cleared")

    def enable_semantic(
        self,
        model_name: str | None = None,
        device: str | None = None,
    ) -> None:
        """
        Enable semantic routing.

        Args:
            model_name: Optional model name (uses config default if None)
            device: Optional device ('cpu', 'cuda', 'mps')
        """
        if self._semantic_router is not None:
            logger.warning("Semantic router already enabled")
            return

        try:
            from neurobus.semantic.router import SemanticRouter

            self._semantic_router = SemanticRouter(
                model_name=model_name or self.config.semantic.model_name,
                device=device,
                cache_size=self.config.semantic.cache_size,
                cache_ttl=self.config.semantic.cache_ttl,
                default_threshold=self.config.semantic.similarity_threshold,
            )

            logger.info("Semantic routing enabled")

        except ImportError:
            logger.error(
                "Failed to enable semantic routing. "
                "Install with: pip install neurobus[semantic]",
                exc_info=True,
            )
            raise

    def _init_context_engine(self) -> None:
        """Initialize context engine."""
        from neurobus.context.engine import ContextEngine

        self._context_engine = ContextEngine()

        logger.info("Context engine initialized")

    def _init_temporal_engine(self) -> None:
        """Initialize temporal engine."""
        from neurobus.temporal.engine import TemporalEngine

        self._temporal_engine = TemporalEngine(
            db_path=str(self.config.temporal.store_path / "events.db"),
        )

        logger.info("Temporal engine initialized")

    def _init_memory_engine(self) -> None:
        """Initialize memory engine."""
        from neurobus.memory.engine import MemoryEngine

        self._memory_engine = MemoryEngine()
        logger.info("Memory engine initialized")

    def _init_reasoning_engine(self) -> None:
        """Initialize reasoning engine."""
        from neurobus.llm.connector import create_connector
        from neurobus.llm.reasoning import ReasoningEngine

        # Create LLM connector with defaults
        connector = create_connector(
            provider=self.config.llm.provider if hasattr(self.config.llm, "provider") else "mock",
            model=self.config.llm.model if hasattr(self.config.llm, "model") else None,
        )

        # Create reasoning engine
        self._reasoning_engine = ReasoningEngine(connector)

        logger.info("Reasoning engine initialized")

    def _init_cluster_manager(self) -> None:
        """Initialize cluster manager."""
        from neurobus.distributed.cluster import ClusterManager

        self._cluster_manager = ClusterManager(
            redis_url=self.config.distributed.redis_url,
            node_id=self.config.distributed.node_id,
            enable_deduplication=self.config.distributed.enable_deduplication,
        )

        # Register handler to process cluster events
        self._cluster_manager.register_event_handler(self._handle_distributed_event)

        logger.info("Cluster manager initialized")

    async def _handle_distributed_event(self, event: "Event") -> None:
        """Handle event received from cluster."""
        # Process event through local dispatcher
        subscriptions = self._registry.find_matches(event)
        await self._dispatcher.dispatch(event, subscriptions)

    @property
    def context(self) -> Any:
        """
        Get context engine.

        Returns:
            Context engine instance

        Example:
            >>> bus.context.set_global("app_version", "1.0.0")
            >>> bus.context.set_session("session_123", "user_id", "alice")
            >>> context = bus.context.get_merged_context("session_123")
        """
        if self._context_engine is None:
            raise RuntimeError(
                "Context engine not enabled. " "Enable in config: context.enabled=True"
            )
        return self._context_engine

    @property
    def temporal(self) -> Any:
        """
        Get temporal engine.

        Returns:
            Temporal engine instance

        Example:
            >>> # Query past events
            >>> past_events = await bus.temporal.query_past(hours=24)
            >>>
            >>> # Replay events
            >>> await bus.temporal.replay(
            ...     start_time=yesterday,
            ...     handler=lambda e: print(e.topic)
            ... )
        """
        if self._temporal_engine is None:
            raise RuntimeError(
                "Temporal engine not enabled. " "Enable in config: temporal.enabled=True"
            )
        return self._temporal_engine

    @property
    def memory(self) -> Any:
        """
        Get memory engine.

        Returns:
            Memory engine instance

        Example:
            >>> # Store event as memory
            >>> await bus.memory.remember_event(event)
            >>>
            >>> # Search memories
            >>> memories = await bus.memory.search("user authentication")
            >>>
            >>> # Get recent memories
            >>> recent = bus.memory.get_recent(limit=10)
        """
        if self._memory_engine is None:
            raise RuntimeError(
                "Memory engine not enabled. " "Enable in config: memory.enabled=True"
            )
        return self._memory_engine

    @property
    def reasoning(self) -> Any:
        """
        Get reasoning engine.

        Returns:
            Reasoning engine instance

        Example:
            >>> # Analyze event
            >>> analysis = await bus.reasoning.analyze_event(event)
            >>>
            >>> # Extract insights
            >>> insights = await bus.reasoning.extract_insights([event1, event2])
            >>>
            >>> # Make decision
            >>> decision = await bus.reasoning.make_decision(
            ...     event, options=["approve", "reject", "defer"]
            ... )
        """
        if self._reasoning_engine is None:
            raise RuntimeError(
                "Reasoning engine not enabled. " "Enable in config: llm.enabled=True"
            )
        return self._reasoning_engine

    @property
    def cluster(self) -> Any:
        """
        Get cluster manager.

        Returns:
            Cluster manager instance

        Example:
            >>> # Check if this node is leader
            >>> is_leader = await bus.cluster.is_leader()
            >>>
            >>> # Get active nodes
            >>> nodes = await bus.cluster.get_active_nodes()
            >>>
            >>> # Acquire distributed lock
            >>> locked = await bus.cluster.acquire_lock("resource_name")
        """
        if self._cluster_manager is None:
            raise RuntimeError(
                "Cluster manager not enabled. " "Enable in config: distributed.enabled=True"
            )
        return self._cluster_manager

    def _merge_matches(
        self,
        pattern_matches: list[Subscription],
        semantic_matches: list[tuple[Subscription, float]],
    ) -> list[Subscription]:
        """
        Merge pattern and semantic matches, removing duplicates.

        Args:
            pattern_matches: Subscriptions from pattern matching
            semantic_matches: Subscriptions from semantic matching with scores

        Returns:
            Combined list of unique subscriptions, sorted by priority
        """
        # Use set to track unique subscription IDs
        seen: set[UUID] = set()
        merged: list[Subscription] = []

        # Add pattern matches first (they're already priority-sorted)
        for sub in pattern_matches:
            if sub.id not in seen:
                merged.append(sub)
                seen.add(sub.id)

        # Add semantic matches (sorted by similarity then priority)
        for sub, _similarity in semantic_matches:
            if sub.id not in seen:
                merged.append(sub)
                seen.add(sub.id)

        # Final sort by priority (descending)
        merged.sort(key=lambda sub: sub.priority, reverse=True)

        return merged

    def get_stats(self) -> dict[str, Any]:
        """
        Get bus statistics.

        Returns:
            Dictionary with bus statistics

        Example:
            >>> stats = bus.get_stats()
            >>> print(f"Total subscriptions: {stats['registry']['total_subscriptions']}")
        """
        stats: dict[str, Any] = {
            "state": self.state,
            "is_running": self.is_running,
            "registry": self._registry.get_stats(),
            "dispatcher": self._dispatcher.get_stats(),
            "lifecycle": self._lifecycle.get_info(),
        }

        # Add semantic stats if enabled
        if self._semantic_router is not None:
            stats["semantic"] = self._semantic_router.get_stats()

        # Add context stats if enabled
        if self._context_engine is not None:
            stats["context"] = self._context_engine.get_stats()

        # Add temporal stats if enabled
        if self._temporal_engine is not None:
            stats["temporal"] = asyncio.create_task(self._temporal_engine.get_stats())

        # Add memory stats if enabled
        if self._memory_engine is not None:
            stats["memory"] = self._memory_engine.get_stats()

        # Add reasoning stats if enabled
        if self._reasoning_engine is not None:
            stats["reasoning"] = self._reasoning_engine.get_stats()

        # Add cluster stats if enabled
        if self._cluster_manager is not None:
            stats["cluster"] = self._cluster_manager.get_stats()

        return stats

    async def __aenter__(self) -> "NeuroBus":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"NeuroBus(" f"state={self.state}, " f"subscriptions={self._registry.count()})"
