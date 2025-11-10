"""
Event dispatcher for parallel async event handling.

The dispatcher executes handler callbacks asynchronously with error
isolation to prevent handler failures from crashing the bus.
"""

import asyncio
import logging
from typing import Any

from neurobus.core.event import Event
from neurobus.core.subscription import Subscription
from neurobus.exceptions.core import HandlerError
from neurobus.utils.helpers import get_function_name
from neurobus.utils.timing import with_timeout

logger = logging.getLogger(__name__)


class EventDispatcher:
    """
    Dispatches events to subscribed handlers in parallel.

    Features:
    - Parallel async execution of handlers
    - Error isolation (handler failures don't crash bus)
    - Per-handler timeout support
    - Concurrency limiting
    - Comprehensive error logging

    Attributes:
        enable_parallel: Whether to execute handlers in parallel
        enable_error_isolation: Whether to isolate handler errors
        handler_timeout: Default timeout for handlers
        max_concurrent: Maximum concurrent handler executions

    Example:
        >>> dispatcher = EventDispatcher(
        ...     enable_parallel=True,
        ...     handler_timeout=10.0,
        ...     max_concurrent=100
        ... )
        >>> await dispatcher.dispatch(event, subscriptions)
    """

    def __init__(
        self,
        enable_parallel: bool = True,
        enable_error_isolation: bool = True,
        handler_timeout: float = 10.0,
        max_concurrent: int = 100,
    ) -> None:
        """
        Initialize dispatcher.

        Args:
            enable_parallel: Execute handlers in parallel
            enable_error_isolation: Isolate handler errors
            handler_timeout: Timeout for individual handlers
            max_concurrent: Maximum concurrent handlers
        """
        self.enable_parallel = enable_parallel
        self.enable_error_isolation = enable_error_isolation
        self.handler_timeout = handler_timeout
        self.max_concurrent = max_concurrent

        # Semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Statistics
        self._total_dispatched = 0
        self._total_succeeded = 0
        self._total_failed = 0
        self._total_timeout = 0

    async def dispatch(
        self,
        event: Event,
        subscriptions: list[Subscription],
    ) -> None:
        """
        Dispatch event to all subscriptions.

        Executes handlers in parallel (if enabled) with error isolation.
        Each handler gets its own timeout and failures are logged but
        don't prevent other handlers from executing.

        Args:
            event: Event to dispatch
            subscriptions: List of subscriptions to notify

        Raises:
            DispatchError: Only if error_isolation is disabled and handler fails
        """
        if not subscriptions:
            return

        self._total_dispatched += 1

        if self.enable_parallel:
            # Execute all handlers in parallel
            await self._dispatch_parallel(event, subscriptions)
        else:
            # Execute handlers sequentially
            await self._dispatch_sequential(event, subscriptions)

    async def _dispatch_parallel(
        self,
        event: Event,
        subscriptions: list[Subscription],
    ) -> None:
        """
        Dispatch to handlers in parallel.

        Args:
            event: Event to dispatch
            subscriptions: Subscriptions to notify
        """
        tasks = [self._execute_handler(event, subscription) for subscription in subscriptions]

        # Execute all handlers concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log any failures
        for subscription, result in zip(subscriptions, results):
            if isinstance(result, Exception):
                self._log_handler_error(event, subscription, result)

    async def _dispatch_sequential(
        self,
        event: Event,
        subscriptions: list[Subscription],
    ) -> None:
        """
        Dispatch to handlers sequentially.

        Args:
            event: Event to dispatch
            subscriptions: Subscriptions to notify
        """
        for subscription in subscriptions:
            try:
                await self._execute_handler(event, subscription)
            except Exception as e:
                self._log_handler_error(event, subscription, e)

                if not self.enable_error_isolation:
                    raise

    async def _execute_handler(
        self,
        event: Event,
        subscription: Subscription,
    ) -> None:
        """
        Execute a single handler with timeout and error handling.

        Args:
            event: Event to handle
            subscription: Subscription with handler

        Raises:
            Exception: If error_isolation is disabled and handler fails
        """
        async with self._semaphore:
            try:
                # Execute with timeout
                await with_timeout(
                    subscription.handle_event(event),
                    timeout=self.handler_timeout,
                    error_context={
                        "event_id": str(event.id),
                        "subscription_id": str(subscription.id),
                    },
                )

                self._total_succeeded += 1

            except TimeoutError:
                self._total_timeout += 1
                handler_name = get_function_name(subscription.handler)

                error = HandlerError(
                    handler_name=handler_name,
                    event_id=str(event.id),
                    original_error=TimeoutError(f"Handler timed out after {self.handler_timeout}s"),
                )

                logger.error(
                    "Handler timeout",
                    extra={
                        "event_id": str(event.id),
                        "event_topic": event.topic,
                        "subscription_id": str(subscription.id),
                        "handler": handler_name,
                        "timeout": self.handler_timeout,
                    },
                )

                if not self.enable_error_isolation:
                    raise error

            except Exception as e:
                self._total_failed += 1
                handler_name = get_function_name(subscription.handler)

                error = HandlerError(
                    handler_name=handler_name,
                    event_id=str(event.id),
                    original_error=e,
                )

                logger.error(
                    "Handler failed",
                    extra={
                        "event_id": str(event.id),
                        "event_topic": event.topic,
                        "subscription_id": str(subscription.id),
                        "handler": handler_name,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                    exc_info=True,
                )

                if not self.enable_error_isolation:
                    raise error from e

    def _log_handler_error(
        self,
        event: Event,
        subscription: Subscription,
        error: Exception,
    ) -> None:
        """
        Log handler error.

        Args:
            event: Event that was being handled
            subscription: Subscription that failed
            error: The error that occurred
        """
        handler_name = get_function_name(subscription.handler)

        logger.error(
            "Handler error during dispatch",
            extra={
                "event_id": str(event.id),
                "event_topic": event.topic,
                "subscription_id": str(subscription.id),
                "handler": handler_name,
                "error": str(error),
                "error_type": type(error).__name__,
            },
        )

    def get_stats(self) -> dict[str, Any]:
        """
        Get dispatcher statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            "total_dispatched": self._total_dispatched,
            "total_succeeded": self._total_succeeded,
            "total_failed": self._total_failed,
            "total_timeout": self._total_timeout,
            "success_rate": (self._total_succeeded / max(self._total_dispatched, 1)),
            "config": {
                "parallel": self.enable_parallel,
                "error_isolation": self.enable_error_isolation,
                "handler_timeout": self.handler_timeout,
                "max_concurrent": self.max_concurrent,
            },
        }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self._total_dispatched = 0
        self._total_succeeded = 0
        self._total_failed = 0
        self._total_timeout = 0

    def __repr__(self) -> str:
        """String representation for debugging."""
        stats = self.get_stats()
        return (
            f"EventDispatcher("
            f"dispatched={stats['total_dispatched']}, "
            f"succeeded={stats['total_succeeded']}, "
            f"failed={stats['total_failed']}, "
            f"parallel={self.enable_parallel})"
        )
