"""Utility functions and helpers."""

from neurobus.utils.helpers import (
    deep_merge,
    ensure_async,
    flatten_dict,
    gather_with_concurrency,
    get_function_name,
    is_async_callable,
    safe_repr,
    unflatten_dict,
)
from neurobus.utils.patterns import extract_variables, wildcard_match
from neurobus.utils.serialization import deserialize, event_to_bytes, serialize
from neurobus.utils.timing import AsyncTimer, Timer, measure_async_time, measure_time
from neurobus.utils.validation import (
    validate_dict,
    validate_pattern,
    validate_threshold,
    validate_timeout,
    validate_topic,
)

__all__ = [
    # Validation
    "validate_topic",
    "validate_pattern",
    "validate_threshold",
    "validate_timeout",
    "validate_dict",
    # Serialization
    "serialize",
    "deserialize",
    "event_to_bytes",
    # Timing
    "Timer",
    "AsyncTimer",
    "measure_time",
    "measure_async_time",
    # Patterns
    "wildcard_match",
    "extract_variables",
    # Helpers
    "get_function_name",
    "is_async_callable",
    "ensure_async",
    "deep_merge",
    "safe_repr",
    "flatten_dict",
    "unflatten_dict",
    "gather_with_concurrency",
]
