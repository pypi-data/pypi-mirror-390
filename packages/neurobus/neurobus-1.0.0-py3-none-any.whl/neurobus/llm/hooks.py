"""
LLM hook registry for pattern-based triggers.

Automatically invokes LLM reasoning when events match patterns.
"""

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from neurobus.core.event import Event
from neurobus.llm.connector import LLMConnector

logger = logging.getLogger(__name__)


class LLMHook:
    """
    Configuration for an LLM hook.

    Defines when and how to invoke LLM reasoning.
    """

    def __init__(
        self,
        pattern: str,
        prompt_template: str,
        model: str | None = None,
        callback: Callable[[Event, str], Any] | None = None,
        enabled: bool = True,
    ):
        """
        Initialize LLM hook.

        Args:
            pattern: Event topic pattern to match
            prompt_template: Prompt template with {variables}
            model: Optional specific model to use
            callback: Optional callback for LLM response
            enabled: Whether hook is active
        """
        self.pattern = pattern
        self.prompt_template = prompt_template
        self.model = model
        self.callback = callback
        self.enabled = enabled
        self.invocations = 0

    def matches(self, topic: str) -> bool:
        """
        Check if event topic matches pattern.

        Args:
            topic: Event topic

        Returns:
            True if matches
        """
        # Simple wildcard matching
        if "*" in self.pattern:
            import re

            regex_pattern = self.pattern.replace("*", ".*")
            return bool(re.match(f"^{regex_pattern}$", topic))

        return self.pattern == topic

    def format_prompt(self, event: Event) -> str:
        """
        Format prompt template with event data.

        Args:
            event: Event to extract data from

        Returns:
            Formatted prompt
        """
        variables = {
            "topic": event.topic,
            "timestamp": event.timestamp.isoformat(),
            "data": event.data,
            "context": event.context or {},
            "metadata": event.metadata or {},
        }

        # Also include flattened data fields
        if isinstance(event.data, dict):
            variables.update(event.data)

        try:
            return self.prompt_template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in prompt template: {e}")
            return self.prompt_template


class HookRegistry:
    """
    Registry for LLM hooks.

    Manages pattern-based LLM triggers and executes them when
    events match.

    Example:
        >>> registry = HookRegistry(connector)
        >>>
        >>> # Register hook
        >>> @registry.hook("task_failure")
        >>> async def analyze_failure(event, reasoning):
        ...     print(f"Analysis: {reasoning}")
        >>>
        >>> # Process event
        >>> await registry.process_event(event)
    """

    def __init__(
        self,
        connector: LLMConnector,
        max_concurrent: int = 5,
    ):
        """
        Initialize hook registry.

        Args:
            connector: LLM connector for reasoning
            max_concurrent: Max concurrent hook executions
        """
        self.connector = connector
        self.max_concurrent = max_concurrent

        self._hooks: list[LLMHook] = []
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Statistics
        self._stats = {
            "hooks_registered": 0,
            "hooks_triggered": 0,
            "llm_invocations": 0,
            "errors": 0,
        }

        logger.info("HookRegistry initialized")

    def register_hook(
        self,
        pattern: str,
        prompt_template: str,
        model: str | None = None,
        callback: Callable[[Event, str], Any] | None = None,
    ) -> LLMHook:
        """
        Register an LLM hook.

        Args:
            pattern: Event pattern to match
            prompt_template: Prompt template
            model: Optional model override
            callback: Optional callback function

        Returns:
            LLM hook instance
        """
        hook = LLMHook(
            pattern=pattern,
            prompt_template=prompt_template,
            model=model,
            callback=callback,
        )

        self._hooks.append(hook)
        self._stats["hooks_registered"] += 1

        logger.info(f"Registered LLM hook for pattern: {pattern}")

        return hook

    def hook(
        self,
        pattern: str,
        prompt_template: str | None = None,
        model: str | None = None,
    ):
        """
        Decorator for registering hook with callback.

        Args:
            pattern: Event pattern to match
            prompt_template: Prompt template
            model: Optional model override

        Example:
            >>> @registry.hook("error.*")
            >>> async def analyze_error(event, reasoning):
            ...     print(reasoning)
        """

        def decorator(func):
            template = prompt_template or "Analyze this event: {topic}\nData: {data}"

            self.register_hook(
                pattern=pattern,
                prompt_template=template,
                model=model,
                callback=func,
            )

            return func

        return decorator

    async def process_event(self, event: Event) -> None:
        """
        Process event through all matching hooks.

        Args:
            event: Event to process
        """
        # Find matching hooks
        matching_hooks = [
            hook for hook in self._hooks if hook.enabled and hook.matches(event.topic)
        ]

        if not matching_hooks:
            return

        # Execute hooks concurrently (with semaphore limit)
        tasks = [self._execute_hook(hook, event) for hook in matching_hooks]

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_hook(self, hook: LLMHook, event: Event) -> None:
        """
        Execute single hook.

        Args:
            hook: Hook to execute
            event: Event that triggered hook
        """
        async with self._semaphore:
            try:
                # Format prompt
                prompt = hook.format_prompt(event)

                # Invoke LLM
                response = await self.connector.generate(prompt)

                # Update statistics
                hook.invocations += 1
                self._stats["hooks_triggered"] += 1
                self._stats["llm_invocations"] += 1

                # Call callback if provided
                if hook.callback:
                    if asyncio.iscoroutinefunction(hook.callback):
                        await hook.callback(event, response.content)
                    else:
                        hook.callback(event, response.content)

                logger.debug(f"Hook executed for {event.topic} " f"(pattern={hook.pattern})")

            except Exception as e:
                self._stats["errors"] += 1
                logger.error(f"Hook execution error: {e}", exc_info=True)

    def get_hooks(self, pattern: str | None = None) -> list[LLMHook]:
        """
        Get registered hooks.

        Args:
            pattern: Optional pattern filter

        Returns:
            List of hooks
        """
        if pattern:
            return [h for h in self._hooks if h.pattern == pattern]
        return self._hooks.copy()

    def enable_hook(self, pattern: str) -> int:
        """
        Enable hooks matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of hooks enabled
        """
        count = 0
        for hook in self._hooks:
            if hook.pattern == pattern:
                hook.enabled = True
                count += 1

        logger.info(f"Enabled {count} hooks for pattern: {pattern}")
        return count

    def disable_hook(self, pattern: str) -> int:
        """
        Disable hooks matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of hooks disabled
        """
        count = 0
        for hook in self._hooks:
            if hook.pattern == pattern:
                hook.enabled = False
                count += 1

        logger.info(f"Disabled {count} hooks for pattern: {pattern}")
        return count

    def remove_hook(self, pattern: str) -> int:
        """
        Remove hooks matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            Number of hooks removed
        """
        original_count = len(self._hooks)
        self._hooks = [h for h in self._hooks if h.pattern != pattern]
        removed = original_count - len(self._hooks)

        logger.info(f"Removed {removed} hooks for pattern: {pattern}")
        return removed

    def get_stats(self) -> dict[str, Any]:
        """
        Get hook registry statistics.

        Returns:
            Statistics dictionary
        """
        return {
            **self._stats,
            "active_hooks": len([h for h in self._hooks if h.enabled]),
            "total_hooks": len(self._hooks),
            "hook_details": [
                {
                    "pattern": h.pattern,
                    "enabled": h.enabled,
                    "invocations": h.invocations,
                }
                for h in self._hooks
            ],
        }

    def clear(self) -> None:
        """Clear all hooks."""
        self._hooks.clear()
        logger.info("Hook registry cleared")
