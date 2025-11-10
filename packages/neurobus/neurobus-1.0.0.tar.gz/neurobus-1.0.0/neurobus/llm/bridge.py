"""
LLM bridge orchestrator for NeuroBUS.

Coordinates LLM hooks, providers, and reasoning operations.
"""

import logging
from typing import Any

from neurobus.core.event import Event
from neurobus.llm.connector import LLMConnector, create_connector
from neurobus.llm.hooks import HookRegistry
from neurobus.llm.reasoning import ReasoningEngine

logger = logging.getLogger(__name__)


class LLMBridge:
    """
    LLM bridge orchestrator.

    Provides high-level API for LLM integration:
    - Hook-based automatic reasoning
    - On-demand event analysis
    - Provider management
    - Reasoning coordination

    Example:
        >>> bridge = LLMBridge(provider="openai", api_key="sk-...")
        >>> await bridge.initialize()
        >>>
        >>> # Register hook
        >>> @bridge.hook("error.*")
        >>> async def analyze_error(event, reasoning):
        ...     print(f"Error analysis: {reasoning}")
        >>>
        >>> # Process event
        >>> await bridge.process_event(error_event)
        >>>
        >>> # Or analyze directly
        >>> analysis = await bridge.analyze_event(event)
    """

    def __init__(
        self,
        provider: str = "mock",
        api_key: str | None = None,
        model: str | None = None,
        **connector_kwargs: Any,
    ):
        """
        Initialize LLM bridge.

        Args:
            provider: LLM provider (openai, anthropic, ollama, mock)
            api_key: API key for provider
            model: Model identifier
            **connector_kwargs: Additional connector parameters
        """
        self.provider = provider
        self.api_key = api_key
        self.model = model
        self.connector_kwargs = connector_kwargs

        # Components
        self.connector: LLMConnector | None = None
        self.hook_registry: HookRegistry | None = None
        self.reasoning_engine: ReasoningEngine | None = None

        self._initialized = False

        logger.info(f"LLMBridge created (provider={provider})")

    async def initialize(self) -> None:
        """Initialize bridge components."""
        if self._initialized:
            return

        # Create connector
        self.connector = create_connector(
            provider=self.provider,
            api_key=self.api_key,
            model=self.model,
            **self.connector_kwargs,
        )

        # Create hook registry
        self.hook_registry = HookRegistry(self.connector)

        # Create reasoning engine
        self.reasoning_engine = ReasoningEngine(self.connector)
        await self.reasoning_engine.initialize()

        self._initialized = True
        logger.info("LLMBridge initialized")

    def hook(self, pattern: str, prompt_template: str | None = None):
        """
        Decorator for registering LLM hook.

        Args:
            pattern: Event pattern to match
            prompt_template: Optional prompt template

        Example:
            >>> @bridge.hook("task_failure")
            >>> async def analyze(event, reasoning):
            ...     print(reasoning)
        """
        if not self.hook_registry:
            raise RuntimeError("Bridge not initialized")

        return self.hook_registry.hook(pattern, prompt_template)

    async def process_event(self, event: Event) -> None:
        """
        Process event through hook registry.

        Args:
            event: Event to process
        """
        if not self._initialized:
            raise RuntimeError("Bridge not initialized")

        await self.hook_registry.process_event(event)

    async def analyze_event(
        self,
        event: Event,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze event using reasoning engine.

        Args:
            event: Event to analyze
            context: Optional additional context

        Returns:
            Analysis results
        """
        if not self._initialized:
            raise RuntimeError("Bridge not initialized")

        return await self.reasoning_engine.analyze_event(event, context)

    async def extract_insights(
        self,
        events: list[Event],
        time_window: str | None = None,
    ) -> dict[str, Any]:
        """
        Extract insights from multiple events.

        Args:
            events: Events to analyze
            time_window: Optional time window description

        Returns:
            Insights dictionary
        """
        if not self._initialized:
            raise RuntimeError("Bridge not initialized")

        return await self.reasoning_engine.extract_insights(events, time_window)

    async def make_decision(
        self,
        event: Event,
        options: list[str],
        criteria: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make decision about event.

        Args:
            event: Event to decide on
            options: Available options
            criteria: Decision criteria

        Returns:
            Decision dictionary
        """
        if not self._initialized:
            raise RuntimeError("Bridge not initialized")

        return await self.reasoning_engine.make_decision(event, options, criteria)

    def get_stats(self) -> dict[str, Any]:
        """
        Get bridge statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "initialized": self._initialized,
            "provider": self.provider,
        }

        if self.hook_registry:
            stats["hooks"] = self.hook_registry.get_stats()

        if self.reasoning_engine:
            stats["reasoning"] = self.reasoning_engine.get_stats()

        if self.connector:
            stats["connector"] = self.connector.get_stats()

        return stats

    async def close(self) -> None:
        """Close bridge and cleanup resources."""
        if self.reasoning_engine:
            await self.reasoning_engine.close()

        self._initialized = False
        logger.info("LLMBridge closed")
