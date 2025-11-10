"""
Causality graph for tracking event relationships.

Maintains parent-child relationships and enables causality analysis.
"""

import logging
from collections import defaultdict
from typing import Any
from uuid import UUID

from neurobus.core.event import Event

logger = logging.getLogger(__name__)


class CausalityGraph:
    """
    Graph structure for tracking event causality relationships.

    Maintains parent-child relationships between events and enables
    querying of causal chains.

    Features:
    - Parent-child relationship tracking
    - Ancestor/descendant queries
    - Causal chain reconstruction
    - Root cause analysis
    - Statistics tracking

    Example:
        >>> graph = CausalityGraph()
        >>>
        >>> # Add event with parent
        >>> graph.add_event(child_event)
        >>>
        >>> # Query relationships
        >>> ancestors = graph.get_ancestors(event_id)
        >>> descendants = graph.get_descendants(event_id)
        >>> chain = graph.get_causal_chain(event_id)
    """

    def __init__(self):
        """Initialize causality graph."""
        # Event ID -> parent ID
        self._parents: dict[UUID, UUID | None] = {}

        # Event ID -> list of child IDs
        self._children: dict[UUID, list[UUID]] = defaultdict(list)

        # Event ID -> event metadata
        self._events: dict[UUID, dict[str, Any]] = {}

        # Statistics
        self._stats = {
            "events_tracked": 0,
            "causal_chains": 0,
            "root_events": 0,
        }

        logger.info("CausalityGraph initialized")

    def add_event(self, event: Event) -> None:
        """
        Add event to causality graph.

        Args:
            event: Event to add
        """
        event_id = event.id
        parent_id = event.parent_id

        # Store event metadata
        self._events[event_id] = {
            "topic": event.topic,
            "timestamp": event.timestamp,
            "parent_id": parent_id,
        }

        # Store parent relationship
        self._parents[event_id] = parent_id

        # Update children list
        if parent_id:
            self._children[parent_id].append(event_id)
        else:
            self._stats["root_events"] += 1

        self._stats["events_tracked"] += 1

        logger.debug(f"Added event {event_id} to causality graph (parent={parent_id})")

    def get_parent(self, event_id: UUID) -> UUID | None:
        """
        Get parent event ID.

        Args:
            event_id: Event ID

        Returns:
            Parent event ID or None if no parent
        """
        return self._parents.get(event_id)

    def get_children(self, event_id: UUID) -> list[UUID]:
        """
        Get list of child event IDs.

        Args:
            event_id: Event ID

        Returns:
            List of child event IDs
        """
        return self._children.get(event_id, [])

    def get_ancestors(self, event_id: UUID) -> list[UUID]:
        """
        Get all ancestor event IDs (parents, grandparents, etc.).

        Args:
            event_id: Event ID

        Returns:
            List of ancestor event IDs in order (immediate parent first)
        """
        ancestors = []
        current = event_id

        while True:
            parent = self._parents.get(current)
            if parent is None:
                break

            ancestors.append(parent)
            current = parent

        return ancestors

    def get_descendants(self, event_id: UUID) -> list[UUID]:
        """
        Get all descendant event IDs (children, grandchildren, etc.).

        Args:
            event_id: Event ID

        Returns:
            List of descendant event IDs (breadth-first order)
        """
        descendants = []
        queue = [event_id]

        while queue:
            current = queue.pop(0)
            children = self._children.get(current, [])

            for child in children:
                descendants.append(child)
                queue.append(child)

        return descendants

    def get_root(self, event_id: UUID) -> UUID:
        """
        Get root event ID (topmost ancestor).

        Args:
            event_id: Event ID

        Returns:
            Root event ID
        """
        current = event_id

        while True:
            parent = self._parents.get(current)
            if parent is None:
                return current
            current = parent

    def get_causal_chain(self, event_id: UUID) -> list[UUID]:
        """
        Get complete causal chain from root to this event.

        Args:
            event_id: Event ID

        Returns:
            List of event IDs from root to this event
        """
        ancestors = self.get_ancestors(event_id)
        ancestors.reverse()  # Root first
        ancestors.append(event_id)

        return ancestors

    def get_chain_metadata(self, event_id: UUID) -> list[dict[str, Any]]:
        """
        Get metadata for entire causal chain.

        Args:
            event_id: Event ID

        Returns:
            List of event metadata dictionaries
        """
        chain = self.get_causal_chain(event_id)

        return [self._events.get(eid, {}) for eid in chain]

    def is_ancestor(self, potential_ancestor: UUID, event_id: UUID) -> bool:
        """
        Check if one event is an ancestor of another.

        Args:
            potential_ancestor: Potential ancestor event ID
            event_id: Event ID to check

        Returns:
            True if potential_ancestor is an ancestor of event_id
        """
        ancestors = self.get_ancestors(event_id)
        return potential_ancestor in ancestors

    def is_descendant(self, potential_descendant: UUID, event_id: UUID) -> bool:
        """
        Check if one event is a descendant of another.

        Args:
            potential_descendant: Potential descendant event ID
            event_id: Event ID to check

        Returns:
            True if potential_descendant is a descendant of event_id
        """
        descendants = self.get_descendants(event_id)
        return potential_descendant in descendants

    def get_depth(self, event_id: UUID) -> int:
        """
        Get depth of event in causal tree (distance from root).

        Args:
            event_id: Event ID

        Returns:
            Depth (0 for root events)
        """
        return len(self.get_ancestors(event_id))

    def get_subtree_size(self, event_id: UUID) -> int:
        """
        Get size of subtree rooted at event.

        Args:
            event_id: Event ID

        Returns:
            Number of descendants
        """
        return len(self.get_descendants(event_id))

    def find_common_ancestor(self, event_id1: UUID, event_id2: UUID) -> UUID | None:
        """
        Find lowest common ancestor of two events.

        Args:
            event_id1: First event ID
            event_id2: Second event ID

        Returns:
            Common ancestor event ID or None
        """
        ancestors1 = set(self.get_ancestors(event_id1))
        ancestors2 = self.get_ancestors(event_id2)

        for ancestor in ancestors2:
            if ancestor in ancestors1:
                return ancestor

        return None

    def get_stats(self) -> dict[str, Any]:
        """
        Get causality graph statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "events_tracked": self._stats["events_tracked"],
            "root_events": self._stats["root_events"],
            "causal_chains": len([e for e, p in self._parents.items() if p is None]),
            "max_depth": max((self.get_depth(e) for e in self._events), default=0),
            "total_relationships": len(self._parents),
        }

    def clear(self) -> None:
        """Clear all causality data."""
        self._parents.clear()
        self._children.clear()
        self._events.clear()
        self._stats = {
            "events_tracked": 0,
            "causal_chains": 0,
            "root_events": 0,
        }
        logger.info("Causality graph cleared")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CausalityGraph("
            f"events={self._stats['events_tracked']}, "
            f"roots={self._stats['root_events']})"
        )
