"""Generic helper utilities."""

import asyncio
import inspect
from collections.abc import Callable, Coroutine
from typing import Any


def get_function_name(func: Callable[..., Any]) -> str:
    """
    Get the name of a function or method.

    Args:
        func: Function or method

    Returns:
        Function name
    """
    if hasattr(func, "__name__"):
        return func.__name__
    elif hasattr(func, "__class__"):
        return func.__class__.__name__
    else:
        return str(func)


def is_async_callable(obj: Any) -> bool:
    """
    Check if object is an async callable.

    Args:
        obj: Object to check

    Returns:
        True if async callable
    """
    return asyncio.iscoroutinefunction(obj) or (
        callable(obj) and asyncio.iscoroutinefunction(obj.__call__)
    )


async def ensure_async(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Call function whether it's sync or async.

    Args:
        func: Function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    if is_async_callable(func):
        return await func(*args, **kwargs)
    else:
        # Run sync function in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Merged dictionary
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def safe_repr(obj: Any, max_length: int = 100) -> str:
    """
    Get a safe string representation of an object.

    Truncates long representations and handles exceptions.

    Args:
        obj: Object to represent
        max_length: Maximum string length

    Returns:
        String representation
    """
    try:
        repr_str = repr(obj)
        if len(repr_str) > max_length:
            return repr_str[:max_length] + "..."
        return repr_str
    except Exception:
        return f"<{type(obj).__name__} (repr failed)>"


def get_caller_info(depth: int = 2) -> dict[str, Any]:
    """
    Get information about the calling function.

    Args:
        depth: Stack depth (2 = immediate caller)

    Returns:
        Dictionary with caller info (filename, function, line)
    """
    frame = inspect.currentframe()

    try:
        for _ in range(depth):
            if frame is None:
                break
            frame = frame.f_back

        if frame is None:
            return {}

        info = inspect.getframeinfo(frame)
        return {
            "filename": info.filename,
            "function": info.function,
            "lineno": info.lineno,
        }
    finally:
        del frame  # Avoid reference cycles


async def gather_with_concurrency(
    n: int,
    *tasks: Coroutine[Any, Any, Any],
) -> list[Any]:
    """
    Gather coroutines with concurrency limit.

    Args:
        n: Maximum concurrent tasks
        *tasks: Coroutines to execute

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(n)

    async def bounded_task(coro: Coroutine[Any, Any, Any]) -> Any:
        async with semaphore:
            return await coro

    return await asyncio.gather(*[bounded_task(task) for task in tasks])


def chunk_list(lst: list[Any], chunk_size: int) -> list[list[Any]]:
    """
    Split list into chunks.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(
    d: dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Flattened dictionary

    Example:
        >>> flatten_dict({"a": {"b": {"c": 1}}})
        {"a.b.c": 1}
    """
    items: list[tuple[str, Any]] = []

    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(d: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """
    Unflatten dictionary with dot notation keys.

    Args:
        d: Flattened dictionary
        sep: Separator used in keys

    Returns:
        Nested dictionary

    Example:
        >>> unflatten_dict({"a.b.c": 1})
        {"a": {"b": {"c": 1}}}
    """
    result: dict[str, Any] = {}

    for key, value in d.items():
        parts = key.split(sep)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result
