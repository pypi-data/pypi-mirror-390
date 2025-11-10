"""
Lifecycle management for NeuroBUS.

Handles startup, shutdown, and state transitions.
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class BusState(str, Enum):
    """Bus lifecycle states."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class LifecycleManager:
    """
    Manages bus lifecycle and state transitions.

    Features:
    - State machine for bus lifecycle
    - Startup/shutdown hooks
    - Graceful shutdown with timeout
    - Error state handling

    Example:
        >>> manager = LifecycleManager()
        >>> await manager.start()
        >>> # ... use bus ...
        >>> await manager.stop()
    """

    def __init__(self) -> None:
        """Initialize lifecycle manager."""
        self._state = BusState.CREATED
        self._startup_hooks: list[Callable[[], Coroutine[Any, Any, None]]] = []
        self._shutdown_hooks: list[Callable[[], Coroutine[Any, Any, None]]] = []
        self._lock = asyncio.Lock()

    @property
    def state(self) -> BusState:
        """Get current bus state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if bus is running."""
        return self._state == BusState.RUNNING

    @property
    def is_stopped(self) -> bool:
        """Check if bus is stopped."""
        return self._state in (BusState.STOPPED, BusState.ERROR)

    def add_startup_hook(
        self,
        hook: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Add a startup hook.

        Hooks are called in order during bus start.

        Args:
            hook: Async function to call on startup
        """
        self._startup_hooks.append(hook)

    def add_shutdown_hook(
        self,
        hook: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Add a shutdown hook.

        Hooks are called in reverse order during bus stop.

        Args:
            hook: Async function to call on shutdown
        """
        self._shutdown_hooks.append(hook)

    async def start(self) -> None:
        """
        Start the bus.

        Transitions from CREATED to RUNNING state and executes
        all startup hooks.

        Raises:
            RuntimeError: If bus is not in CREATED state
        """
        async with self._lock:
            if self._state != BusState.CREATED:
                raise RuntimeError(
                    f"Cannot start bus from state: {self._state}. " f"Expected: {BusState.CREATED}"
                )

            logger.info("Starting NeuroBUS...")
            self._state = BusState.STARTING

            try:
                # Execute startup hooks
                for hook in self._startup_hooks:
                    try:
                        await hook()
                    except Exception as e:
                        logger.error(
                            f"Startup hook failed: {hook.__name__}",
                            exc_info=True,
                        )
                        self._state = BusState.ERROR
                        raise RuntimeError(f"Startup failed: {e}") from e

                self._state = BusState.RUNNING
                logger.info("NeuroBUS started successfully")

            except Exception:
                self._state = BusState.ERROR
                logger.error("Failed to start NeuroBUS", exc_info=True)
                raise

    async def stop(self, timeout: float = 10.0) -> None:
        """
        Stop the bus gracefully.

        Transitions to STOPPED state and executes all shutdown hooks
        in reverse order.

        Args:
            timeout: Maximum time to wait for shutdown

        Raises:
            RuntimeError: If bus is not in RUNNING state
        """
        async with self._lock:
            if self._state != BusState.RUNNING:
                logger.warning(f"Stop called but bus is not running (state: {self._state})")
                return

            logger.info("Stopping NeuroBUS...")
            self._state = BusState.STOPPING

            try:
                # Execute shutdown hooks in reverse order
                for hook in reversed(self._shutdown_hooks):
                    try:
                        await asyncio.wait_for(hook(), timeout=timeout)
                    except TimeoutError:
                        logger.warning(f"Shutdown hook timed out: {hook.__name__}")
                    except Exception:
                        logger.error(
                            f"Shutdown hook failed: {hook.__name__}",
                            exc_info=True,
                        )

                self._state = BusState.STOPPED
                logger.info("NeuroBUS stopped successfully")

            except Exception:
                self._state = BusState.ERROR
                logger.error("Error during shutdown", exc_info=True)
                raise

    async def restart(self, timeout: float = 10.0) -> None:
        """
        Restart the bus.

        Args:
            timeout: Maximum time to wait for shutdown
        """
        await self.stop(timeout)

        # Reset to CREATED state
        async with self._lock:
            self._state = BusState.CREATED

        await self.start()

    def check_running(self) -> None:
        """
        Check if bus is running.

        Raises:
            RuntimeError: If bus is not running
        """
        if not self.is_running:
            raise RuntimeError(
                f"Bus is not running (state: {self._state}). " f"Call await bus.start() first."
            )

    def get_info(self) -> dict[str, Any]:
        """
        Get lifecycle info.

        Returns:
            Dictionary with lifecycle information
        """
        return {
            "state": self._state.value,
            "is_running": self.is_running,
            "is_stopped": self.is_stopped,
            "startup_hooks": len(self._startup_hooks),
            "shutdown_hooks": len(self._shutdown_hooks),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"LifecycleManager(state={self._state.value})"
