"""Type definitions for subscriptions."""

from typing import TypeAlias

# Subscription filter expression type
FilterExpression: TypeAlias = str


# Subscription priority levels
class Priority:
    """Standard priority levels for subscriptions."""

    HIGHEST = 100
    HIGH = 50
    NORMAL = 0
    LOW = -50
    LOWEST = -100
