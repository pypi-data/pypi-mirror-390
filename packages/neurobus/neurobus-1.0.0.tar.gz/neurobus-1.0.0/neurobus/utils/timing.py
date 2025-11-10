"""Timing utilities for performance measurement."""

import asyncio
import time
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any

from neurobus.exceptions.core import DispatchTimeoutError


class Timer:
    """Context manager for timing code execution."""

    def __init__(self) -> None:
        """Initialize timer."""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop timing."""
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000.0


class AsyncTimer:
    """Async context manager for timing async code."""

    def __init__(self) -> None:
        """Initialize timer."""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.elapsed: float = 0.0

    async def __aenter__(self) -> "AsyncTimer":
        """Start timing."""
        self.start_time = time.perf_counter()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Stop timing."""
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed * 1000.0


@contextmanager
def measure_time() -> Iterator[Timer]:
    """
    Context manager to measure execution time.

    Yields:
        Timer instance

    Example:
        >>> with measure_time() as timer:
        ...     # do work
        ...     pass
        >>> print(f"Took {timer.elapsed_ms:.2f}ms")
    """
    timer = Timer()
    with timer:
        yield timer


@asynccontextmanager
async def measure_async_time() -> AsyncIterator[AsyncTimer]:
    """
    Async context manager to measure execution time.

    Yields:
        AsyncTimer instance

    Example:
        >>> async with measure_async_time() as timer:
        ...     await asyncio.sleep(0.1)
        >>> print(f"Took {timer.elapsed_ms:.2f}ms")
    """
    timer = AsyncTimer()
    async with timer:
        yield timer


async def with_timeout(
    coro: Any,
    timeout: float,
    error_context: dict[str, Any] | None = None,
) -> Any:
    """
    Execute coroutine with timeout.

    Args:
        coro: Coroutine to execute
        timeout: Timeout in seconds
        error_context: Optional context for error messages

    Returns:
        Coroutine result

    Raises:
        DispatchTimeoutError: If timeout is exceeded
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except TimeoutError:
        context = error_context or {}
        event_id = context.get("event_id", "unknown")
        raise DispatchTimeoutError(timeout, event_id)


def get_timestamp_ms() -> int:
    """
    Get current timestamp in milliseconds.

    Returns:
        Timestamp in milliseconds since epoch
    """
    return int(time.time() * 1000)


def get_timestamp_us() -> int:
    """
    Get current timestamp in microseconds.

    Returns:
        Timestamp in microseconds since epoch
    """
    return int(time.time() * 1_000_000)


async def rate_limit(calls_per_second: float) -> None:
    """
    Rate limit async operations.

    Args:
        calls_per_second: Maximum calls per second

    Example:
        >>> for i in range(100):
        ...     await rate_limit(10)  # Max 10 calls/sec
        ...     await do_work()
    """
    await asyncio.sleep(1.0 / calls_per_second)


class RateLimiter:
    """Token bucket rate limiter for async operations."""

    def __init__(self, rate: float, capacity: float | None = None) -> None:
        """
        Initialize rate limiter.

        Args:
            rate: Tokens per second
            capacity: Bucket capacity (default: same as rate)
        """
        self.rate = rate
        self.capacity = capacity or rate
        self.tokens = self.capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0) -> None:
        """
        Acquire tokens from the bucket.

        Waits if insufficient tokens available.

        Args:
            tokens: Number of tokens to acquire
        """
        async with self._lock:
            while self.tokens < tokens:
                # Refill tokens based on elapsed time
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens < tokens:
                    # Wait for more tokens
                    wait_time = (tokens - self.tokens) / self.rate
                    await asyncio.sleep(wait_time)

            self.tokens -= tokens
