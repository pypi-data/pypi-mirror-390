"""Type definitions for context management."""

from enum import Enum
from typing import Any, TypeAlias


# Context scope type
class ContextScope(str, Enum):
    """Context scope levels."""

    GLOBAL = "global"
    SESSION = "session"
    USER = "user"
    EVENT = "event"


# Context data type
ContextData: TypeAlias = dict[str, Any]


# Filter result type
FilterResult: TypeAlias = bool
