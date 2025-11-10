"""Input validation utilities."""

import re
from typing import Any

from neurobus.exceptions.core import ValidationError


def validate_topic(topic: str) -> None:
    """
    Validate event topic format.

    Topics must:
    - Be non-empty strings
    - Contain only alphanumeric, dots, hyphens, underscores
    - Not start or end with dots
    - Have reasonable length (<256 chars)

    Args:
        topic: Topic string to validate

    Raises:
        ValidationError: If topic is invalid
    """
    if not topic:
        raise ValidationError("topic", "Topic cannot be empty")

    if not isinstance(topic, str):
        raise ValidationError("topic", f"Topic must be string, got {type(topic).__name__}")

    if len(topic) > 255:
        raise ValidationError("topic", f"Topic too long ({len(topic)} > 255 chars)")

    if topic.startswith(".") or topic.endswith("."):
        raise ValidationError("topic", "Topic cannot start or end with '.'")

    # Allow alphanumeric, dots, hyphens, underscores, forward slashes
    if not re.match(r"^[a-zA-Z0-9._/-]+$", topic):
        raise ValidationError(
            "topic",
            "Topic must contain only alphanumeric characters, dots, hyphens, underscores, or slashes",
        )


def validate_pattern(pattern: str) -> None:
    """
    Validate subscription pattern format.

    Patterns follow same rules as topics but may include wildcards.

    Args:
        pattern: Pattern string to validate

    Raises:
        ValidationError: If pattern is invalid
    """
    if not pattern:
        raise ValidationError("pattern", "Pattern cannot be empty")

    if not isinstance(pattern, str):
        raise ValidationError("pattern", f"Pattern must be string, got {type(pattern).__name__}")

    if len(pattern) > 255:
        raise ValidationError("pattern", f"Pattern too long ({len(pattern)} > 255 chars)")

    # Allow wildcards (* and #) in addition to topic characters
    if not re.match(r"^[a-zA-Z0-9._/*#-]+$", pattern):
        raise ValidationError(
            "pattern",
            "Pattern must contain only alphanumeric, dots, wildcards (*, #), hyphens, or underscores",
        )


def validate_threshold(threshold: float) -> None:
    """
    Validate similarity threshold.

    Args:
        threshold: Threshold value (0.0-1.0)

    Raises:
        ValidationError: If threshold is invalid
    """
    if not isinstance(threshold, (int, float)):
        raise ValidationError(
            "threshold", f"Threshold must be numeric, got {type(threshold).__name__}"
        )

    if not 0.0 <= threshold <= 1.0:
        raise ValidationError(
            "threshold", f"Threshold must be between 0.0 and 1.0, got {threshold}"
        )


def validate_dict(data: Any, name: str = "data") -> None:
    """
    Validate that data is a dictionary.

    Args:
        data: Data to validate
        name: Name of the field for error messages

    Raises:
        ValidationError: If data is not a dict
    """
    if not isinstance(data, dict):
        raise ValidationError(name, f"Must be a dictionary, got {type(data).__name__}")


def validate_timeout(timeout: float, name: str = "timeout") -> None:
    """
    Validate timeout value.

    Args:
        timeout: Timeout in seconds
        name: Name of the field for error messages

    Raises:
        ValidationError: If timeout is invalid
    """
    if not isinstance(timeout, (int, float)):
        raise ValidationError(name, f"Must be numeric, got {type(timeout).__name__}")

    if timeout <= 0:
        raise ValidationError(name, f"Must be positive, got {timeout}")


def validate_priority(priority: int) -> None:
    """
    Validate subscription priority.

    Args:
        priority: Priority value

    Raises:
        ValidationError: If priority is invalid
    """
    if not isinstance(priority, int):
        raise ValidationError(
            "priority", f"Priority must be integer, got {type(priority).__name__}"
        )


def is_valid_json_serializable(data: Any) -> bool:
    """
    Check if data is JSON serializable.

    Args:
        data: Data to check

    Returns:
        True if JSON serializable, False otherwise
    """
    import json

    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False
