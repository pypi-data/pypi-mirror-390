"""Immutable lineage identifier for DataFrame transformations."""

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Set


@dataclass(frozen=True)
class LineageID:
    """
    Immutable identifier for a specific DataFrame state in the lineage graph.

    This class represents a unique point in the data transformation pipeline.
    Once created, a LineageID never changes - each transformation creates a new LineageID.
    This immutability is crucial for correctly tracking fork patterns where the same
    DataFrame is used by multiple consumers.

    Attributes:
        id: Unique identifier for this lineage point
        operation_id: Identifier of the operation that created this state
        parent_ids: List of parent LineageID identifiers (can be multiple for joins/unions)
        context_id: Execution context identifier that created this lineage point
        timestamp: Creation timestamp for ordering operations
        operation_type: Type of operation (filter, join, transform, etc.)
    """

    id: str = field(default_factory=lambda: f"lid_{uuid.uuid4().hex[:12]}")
    operation_id: str = field(default_factory=lambda: f"op_{uuid.uuid4().hex[:8]}")
    parent_ids: List[str] = field(default_factory=list)
    context_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    operation_type: str = "unknown"

    def __post_init__(self):
        """Validate LineageID after creation."""
        # Ensure parent_ids is a list (frozen dataclass prevents modification)
        if not isinstance(self.parent_ids, list):
            object.__setattr__(self, 'parent_ids', list(self.parent_ids))

    def is_source(self) -> bool:
        """Check if this is a source lineage point (no parents)."""
        return len(self.parent_ids) == 0

    def is_merge_point(self) -> bool:
        """Check if this is a merge point (multiple parents - join/union)."""
        return len(self.parent_ids) > 1

    def has_parent(self, parent_id: str) -> bool:
        """Check if this lineage point has a specific parent."""
        return parent_id in self.parent_ids

    def __repr__(self) -> str:
        """String representation for debugging."""
        parent_str = f"parents={len(self.parent_ids)}" if self.parent_ids else "source"
        return f"LineageID({self.id}, op={self.operation_type}, {parent_str})"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'operation_id': self.operation_id,
            'parent_ids': self.parent_ids,
            'context_id': self.context_id,
            'timestamp': self.timestamp,
            'operation_type': self.operation_type
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LineageID':
        """Create LineageID from dictionary."""
        return cls(
            id=data.get('id'),
            operation_id=data.get('operation_id'),
            parent_ids=data.get('parent_ids', []),
            context_id=data.get('context_id'),
            timestamp=data.get('timestamp', time.time()),
            operation_type=data.get('operation_type', 'unknown')
        )

    @classmethod
    def create_source(cls, source_name: str = None, context_id: str = None) -> 'LineageID':
        """Create a source LineageID (no parents)."""
        return cls(
            operation_id=f"source_{source_name or uuid.uuid4().hex[:8]}",
            parent_ids=[],
            context_id=context_id,
            operation_type="source"
        )

    @classmethod
    def create_from_parent(cls, parent: 'LineageID', operation_type: str,
                           context_id: str = None) -> 'LineageID':
        """Create a new LineageID from a single parent."""
        return cls(
            parent_ids=[parent.id],
            context_id=context_id,
            operation_type=operation_type
        )

    @classmethod
    def create_from_parents(cls, parents: List['LineageID'], operation_type: str,
                           context_id: str = None) -> 'LineageID':
        """Create a new LineageID from multiple parents (for joins/unions)."""
        parent_ids = [p.id for p in parents]
        return cls(
            parent_ids=parent_ids,
            context_id=context_id,
            operation_type=operation_type
        )


class LineageIDTracker:
    """
    Tracks LineageID relationships and consumer information.

    This class maintains the registry of all LineageIDs and tracks
    which execution contexts consume each LineageID, enabling fork detection.
    """

    def __init__(self):
        self.lineage_registry = {}  # id -> LineageID
        self.consumers = {}  # lineage_id -> Set[context_id]
        self.fork_points = set()  # Set of lineage_ids that have been forked

    def register(self, lineage_id: LineageID) -> None:
        """Register a new LineageID."""
        self.lineage_registry[lineage_id.id] = lineage_id
        if lineage_id.id not in self.consumers:
            self.consumers[lineage_id.id] = set()

    def add_consumer(self, lineage_id: str, context_id: str) -> bool:
        """
        Add a consumer for a LineageID.

        Returns:
            True if this creates a fork (multiple consumers), False otherwise
        """
        if lineage_id not in self.consumers:
            self.consumers[lineage_id] = set()

        self.consumers[lineage_id].add(context_id)

        # Check if this creates a fork
        if len(self.consumers[lineage_id]) > 1:
            self.fork_points.add(lineage_id)
            return True
        return False

    def is_fork_point(self, lineage_id: str) -> bool:
        """Check if a LineageID is a fork point."""
        return lineage_id in self.fork_points

    def get_consumers(self, lineage_id: str) -> Set[str]:
        """Get all consumers of a LineageID."""
        return self.consumers.get(lineage_id, set())

    def get_lineage(self, lineage_id: str) -> Optional[LineageID]:
        """Get a LineageID by its identifier."""
        return self.lineage_registry.get(lineage_id)

    def get_all_fork_points(self) -> List[LineageID]:
        """Get all LineageIDs that are fork points."""
        return [self.lineage_registry[lid] for lid in self.fork_points
                if lid in self.lineage_registry]

    def clear(self) -> None:
        """Clear all tracked lineage information."""
        self.lineage_registry.clear()
        self.consumers.clear()
        self.fork_points.clear()