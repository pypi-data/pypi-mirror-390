"""Type definitions for events."""

from typing import Any, TypeAlias

# Type aliases for common event data structures
EventData: TypeAlias = dict[str, Any]
EventContext: TypeAlias = dict[str, Any]
EventMetadata: TypeAlias = dict[str, Any]


# Common metadata keys
class MetadataKeys:
    """Standard metadata keys used across NeuroBUS."""

    PRIORITY = "priority"
    CORRELATION_ID = "correlation_id"
    CAUSATION_ID = "causation_id"
    TAGS = "tags"
    SOURCE = "source"
    DESTINATION = "destination"
    TTL = "ttl"
    RETRY_COUNT = "retry_count"


# Common context keys
class ContextKeys:
    """Standard context keys used across NeuroBUS."""

    USER_ID = "user_id"
    SESSION_ID = "session_id"
    REQUEST_ID = "request_id"
    ENVIRONMENT = "environment"
    LOCATION = "location"
    DEVICE = "device"
    TIMESTAMP = "timestamp"
