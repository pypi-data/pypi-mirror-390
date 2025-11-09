"""Fork detection for identifying multi-consumer DataFrame patterns."""

import logging
from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .execution_context import ExecutionContext
from .lineage_id import LineageID

logger = logging.getLogger(__name__)


class ForkStatus(Enum):
    """Status of fork detection for a lineage point."""
    NORMAL = "normal"  # Single consumer
    FORK_DETECTED = "fork_detected"  # Multiple consumers detected
    POTENTIAL_FORK = "potential_fork"  # Cached/materialized, could fork


class ForkPoint:
    """
    Represents a point in the lineage where a fork occurs.

    A fork point is where a single DataFrame is consumed by multiple
    operations, creating parallel execution paths.
    """

    def __init__(self, lineage_id: str, parent_context: str = None):
        self.lineage_id = lineage_id
        self.parent_context = parent_context  # Context that created this DataFrame
        self.consumer_contexts = set()  # Contexts that consume this DataFrame
        self.consumer_operations = []  # Operations that consume this DataFrame
        self.is_cached = False  # Whether this DataFrame was cached
        self.fork_timestamp = None

    def add_consumer(self, context_id: str, operation: str = None) -> ForkStatus:
        """Add a consumer and return fork status."""
        self.consumer_contexts.add(context_id)
        if operation:
            self.consumer_operations.append((context_id, operation))

        if len(self.consumer_contexts) > 1:
            return ForkStatus.FORK_DETECTED
        elif self.is_cached:
            return ForkStatus.POTENTIAL_FORK
        else:
            return ForkStatus.NORMAL

    def get_fork_degree(self) -> int:
        """Get the number of consumers (fork degree)."""
        return len(self.consumer_contexts)

    def is_fork(self) -> bool:
        """Check if this is an active fork point."""
        return len(self.consumer_contexts) > 1

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'lineage_id': self.lineage_id,
            'parent_context': self.parent_context,
            'consumer_contexts': list(self.consumer_contexts),
            'consumer_operations': self.consumer_operations,
            'is_cached': self.is_cached,
            'fork_degree': self.get_fork_degree()
        }


class ForkDetector:
    """
    Detects and tracks fork patterns in DataFrame lineage.

    This class monitors DataFrame consumption patterns to identify when
    a single DataFrame is used by multiple operations (fork pattern).
    It maintains metadata-only tracking without touching the actual DataFrames,
    preserving PySpark's lazy evaluation.
    """

    def __init__(self):
        self.fork_points = {}  # lineage_id -> ForkPoint
        self.context_lineage_map = defaultdict(set)  # context_id -> Set[lineage_ids consumed]
        self.lineage_producer_map = {}  # lineage_id -> context_id that produced it
        self.cache_points = set()  # Set of lineage_ids that are cached
        self.fork_detection_enabled = True

    def register_producer(self, lineage_id: str, context_id: str) -> None:
        """Register which context produced a LineageID."""
        self.lineage_producer_map[lineage_id] = context_id
        logger.debug(f"Registered producer: {context_id} -> {lineage_id}")

    def register_consumer(self, lineage_id: str, context_id: str,
                         operation: str = None) -> ForkStatus:
        """
        Register a consumer for a LineageID and detect forks.

        Args:
            lineage_id: The LineageID being consumed
            context_id: The execution context consuming it
            operation: Optional operation name for tracking

        Returns:
            ForkStatus indicating whether a fork was detected
        """
        if not self.fork_detection_enabled:
            return ForkStatus.NORMAL

        # Get or create fork point
        if lineage_id not in self.fork_points:
            parent_context = self.lineage_producer_map.get(lineage_id)
            fork_point = ForkPoint(lineage_id, parent_context)
            # Check if this was marked as cached before the fork point was created
            if lineage_id in self.cache_points:
                fork_point.is_cached = True
            self.fork_points[lineage_id] = fork_point
        else:
            fork_point = self.fork_points[lineage_id]

        # Add consumer and check fork status
        status = fork_point.add_consumer(context_id, operation)

        # Track context's lineage consumption
        self.context_lineage_map[context_id].add(lineage_id)

        if status == ForkStatus.FORK_DETECTED:
            logger.info(f"Fork detected at {lineage_id}: consumed by {fork_point.consumer_contexts}")

        return status

    def mark_as_cached(self, lineage_id: str) -> None:
        """Mark a LineageID as cached (potential fork point)."""
        self.cache_points.add(lineage_id)
        if lineage_id in self.fork_points:
            self.fork_points[lineage_id].is_cached = True
        logger.debug(f"Marked {lineage_id} as cached (potential fork point)")

    def is_fork_point(self, lineage_id: str) -> bool:
        """Check if a LineageID is a fork point."""
        if lineage_id in self.fork_points:
            return self.fork_points[lineage_id].is_fork()
        return False

    def is_potential_fork(self, lineage_id: str) -> bool:
        """Check if a LineageID is a potential fork point (cached)."""
        return lineage_id in self.cache_points

    def get_fork_point(self, lineage_id: str) -> Optional[ForkPoint]:
        """Get fork point information for a LineageID."""
        return self.fork_points.get(lineage_id)

    def get_all_fork_points(self) -> List[ForkPoint]:
        """Get all detected fork points."""
        return [fp for fp in self.fork_points.values() if fp.is_fork()]

    def get_fork_statistics(self) -> dict:
        """Get statistics about detected forks."""
        all_forks = self.get_all_fork_points()
        return {
            'total_fork_points': len(all_forks),
            'max_fork_degree': max([fp.get_fork_degree() for fp in all_forks], default=0),
            'avg_fork_degree': (sum([fp.get_fork_degree() for fp in all_forks]) / len(all_forks)
                               if all_forks else 0),
            'cached_fork_points': len([fp for fp in all_forks if fp.is_cached]),
            'fork_points': [fp.to_dict() for fp in all_forks]
        }

    def get_context_lineage_consumption(self, context_id: str) -> Set[str]:
        """Get all LineageIDs consumed by a context."""
        return self.context_lineage_map.get(context_id, set())

    def detect_diamond_pattern(self) -> List[Tuple[str, List[str], str]]:
        """
        Detect diamond patterns (fork followed by merge).

        Returns:
            List of (fork_point, parallel_paths, merge_point) tuples
        """
        diamond_patterns = []

        for fork_id, fork_point in self.fork_points.items():
            if not fork_point.is_fork():
                continue

            # Look for merge points where the forked paths converge
            consumer_lineages = defaultdict(set)
            for context_id in fork_point.consumer_contexts:
                consumed = self.context_lineage_map.get(context_id, set())
                for lineage_id in consumed:
                    consumer_lineages[lineage_id].add(context_id)

            # Find lineage points that have multiple of our fork's consumers as inputs
            for merge_id, contexts in consumer_lineages.items():
                if len(contexts) > 1 and contexts.issubset(fork_point.consumer_contexts):
                    diamond_patterns.append((fork_id, list(contexts), merge_id))

        return diamond_patterns

    def analyze_fork_impact(self, lineage_id: str) -> dict:
        """
        Analyze the impact of a fork point.

        Returns information about downstream operations affected by the fork.
        """
        if not self.is_fork_point(lineage_id):
            return {'is_fork': False}

        fork_point = self.fork_points[lineage_id]
        downstream_operations = defaultdict(list)

        # Trace downstream operations for each consumer
        for context_id in fork_point.consumer_contexts:
            # This would need integration with the lineage graph to trace downstream
            downstream_operations[context_id] = []  # Placeholder

        return {
            'is_fork': True,
            'fork_degree': fork_point.get_fork_degree(),
            'consumer_contexts': list(fork_point.consumer_contexts),
            'is_cached': fork_point.is_cached,
            'downstream_impact': downstream_operations
        }

    def clear(self) -> None:
        """Clear all fork detection data."""
        self.fork_points.clear()
        self.context_lineage_map.clear()
        self.lineage_producer_map.clear()
        self.cache_points.clear()

    def enable(self) -> None:
        """Enable fork detection."""
        self.fork_detection_enabled = True

    def disable(self) -> None:
        """Disable fork detection for performance."""
        self.fork_detection_enabled = False


# Global fork detector instance
_global_fork_detector = ForkDetector()


def get_fork_detector() -> ForkDetector:
    """Get the global fork detector instance."""
    return _global_fork_detector


def detect_fork(lineage_id: str, context_id: str, operation: str = None) -> ForkStatus:
    """Convenience function to detect forks."""
    return _global_fork_detector.register_consumer(lineage_id, context_id, operation)