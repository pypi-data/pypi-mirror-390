"""
Core Event model for NeuroBUS.

Events are the fundamental unit of communication in NeuroBUS, carrying
both data and semantic meaning.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class Event:
    """
    Represents a single event in the NeuroBUS system.

    Events carry data, metadata, and context through the event bus.
    They are immutable after creation to ensure consistency.

    Attributes:
        id: Unique identifier for the event
        topic: Topic/channel name (e.g., "user.login", "system.error")
        data: Event payload (arbitrary JSON-serializable data)
        timestamp: When the event was created
        context: Contextual information (user, session, environment)
        metadata: Additional metadata (tags, priority, correlation_id, etc.)
        parent_id: Optional parent event ID for causality tracking

    Example:
        >>> event = Event(
        ...     topic="user.login",
        ...     data={"username": "alice", "success": True},
        ...     context={"session_id": "abc123"}
        ... )
    """

    topic: str
    data: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: UUID | None = None

    def __post_init__(self) -> None:
        """Validate event after initialization."""
        if not self.topic:
            raise ValueError("Event topic cannot be empty")

        if not isinstance(self.topic, str):
            raise TypeError(f"Event topic must be str, got {type(self.topic)}")

    def with_context(self, **context: Any) -> "Event":
        """
        Create a new event with merged context.

        Args:
            **context: Additional context to merge

        Returns:
            New Event instance with merged context

        Example:
            >>> new_event = event.with_context(user_id="123", mood="happy")
        """
        from copy import deepcopy

        new_context = deepcopy(self.context)
        new_context.update(context)

        return Event(
            id=self.id,
            topic=self.topic,
            data=self.data,
            timestamp=self.timestamp,
            context=new_context,
            metadata=self.metadata,
            parent_id=self.parent_id,
        )

    def child_event(self, topic: str, data: dict[str, Any] | None = None) -> "Event":
        """
        Create a child event for causality tracking.

        Args:
            topic: Topic for the child event
            data: Data for the child event

        Returns:
            New Event with parent_id set to this event's id

        Example:
            >>> response = request_event.child_event("response", {"status": 200})
        """
        return Event(
            topic=topic,
            data=data or {},
            context=self.context.copy(),
            metadata=self.metadata.copy(),
            parent_id=self.id,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dictionary representation of the event
        """
        return {
            "id": str(self.id),
            "topic": self.topic,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
            "metadata": self.metadata,
            "parent_id": str(self.parent_id) if self.parent_id else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """
        Create event from dictionary.

        Args:
            data: Dictionary representation of event

        Returns:
            Event instance

        Raises:
            ValueError: If required fields are missing
        """
        return cls(
            id=UUID(data["id"]) if "id" in data else uuid4(),
            topic=data["topic"],
            data=data.get("data", {}),
            timestamp=(
                datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
            ),
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
            parent_id=UUID(data["parent_id"]) if data.get("parent_id") else None,
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Event(id={self.id!s:.8}, topic={self.topic!r}, "
            f"timestamp={self.timestamp.isoformat()})"
        )
