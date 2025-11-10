"""
Filter engine for context-based subscription filtering.

Evaluates filters (lambda or DSL) against event context.
"""

import logging
from collections.abc import Callable
from typing import Any

from neurobus.context.dsl import parse_filter
from neurobus.core.event import Event

logger = logging.getLogger(__name__)


class FilterEngine:
    """
    Engine for evaluating subscription filters.

    Supports both lambda filters and DSL string filters.

    Example:
        >>> engine = FilterEngine()
        >>>
        >>> # Lambda filter
        >>> lambda_filter = lambda e: e.context.get("priority", 0) > 5
        >>> engine.evaluate(event, lambda_filter)
        >>>
        >>> # DSL filter
        >>> dsl_filter = "priority > 5 AND user.role == 'admin'"
        >>> engine.evaluate(event, dsl_filter)
    """

    def __init__(self):
        """Initialize filter engine."""
        self._compiled_filters: dict[str, Callable] = {}

    def evaluate(
        self,
        event: Event,
        filter_spec: Callable[[Event], bool] | str | None,
    ) -> bool:
        """
        Evaluate filter against event.

        Args:
            event: Event to evaluate
            filter_spec: Filter specification (lambda, DSL string, or None)

        Returns:
            True if event passes filter, False otherwise

        Example:
            >>> engine = FilterEngine()
            >>> event = Event(topic="test", data={}, context={"priority": 10})
            >>> engine.evaluate(event, lambda e: e.context["priority"] > 5)
            True
        """
        if filter_spec is None:
            # No filter means pass everything
            return True

        try:
            if callable(filter_spec):
                # Lambda filter
                return bool(filter_spec(event))

            elif isinstance(filter_spec, str):
                # DSL filter - compile and cache
                if filter_spec not in self._compiled_filters:
                    self._compiled_filters[filter_spec] = parse_filter(filter_spec)

                filter_func = self._compiled_filters[filter_spec]
                return bool(filter_func(event.context))

            else:
                logger.warning(f"Unknown filter type: {type(filter_spec)}")
                return True

        except Exception as e:
            logger.error(f"Filter evaluation error: {e}", exc_info=True)
            # On error, allow event through (fail open)
            return True

    def compile_filter(self, filter_spec: str) -> Callable:
        """
        Compile DSL filter expression.

        Args:
            filter_spec: DSL filter string

        Returns:
            Compiled filter function

        Example:
            >>> engine = FilterEngine()
            >>> func = engine.compile_filter("priority >= 5")
            >>> func({"priority": 10})
            True
        """
        if filter_spec not in self._compiled_filters:
            self._compiled_filters[filter_spec] = parse_filter(filter_spec)

        return self._compiled_filters[filter_spec]

    def clear_cache(self) -> None:
        """Clear compiled filter cache."""
        self._compiled_filters.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get filter cache statistics."""
        return {
            "cached_filters": len(self._compiled_filters),
            "filter_expressions": list(self._compiled_filters.keys()),
        }
