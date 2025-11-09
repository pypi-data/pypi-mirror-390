"""Enhanced lineage graph with fork-aware tracking and immutable lineage support."""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .execution_context import ExecutionContext
from .fork_detector import ForkPoint
from .graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
    LineageEdge,
    OperationNode,
)
from .lineage_id import LineageID

logger = logging.getLogger(__name__)


@dataclass
class EnhancedLineageEdge:
    """Enhanced edge with fork-aware metadata."""
    source_id: str
    target_id: str
    edge_type: str
    context_id: Optional[str] = None
    is_fork_edge: bool = False
    fork_degree: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'edge_type': self.edge_type,
            'context_id': self.context_id,
            'is_fork_edge': self.is_fork_edge,
            'fork_degree': self.fork_degree,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


@dataclass
class LineageNode:
    """Enhanced node with lineage and context information."""
    node_id: str
    lineage_id: Optional[str] = None
    context_id: Optional[str] = None
    node_type: str = "unknown"
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'node_id': self.node_id,
            'lineage_id': self.lineage_id,
            'context_id': self.context_id,
            'node_type': self.node_type,
            'name': self.name,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }


class EnhancedLineageGraph:
    """
    Enhanced lineage graph with fork-aware tracking and immutable lineage support.

    This class maintains the complete lineage graph with support for:
    - Fork detection and visualization
    - Multiple parent/child relationships
    - Context-aware edge tracking
    - Immutable lineage ID relationships
    - Performance-optimized querying
    """

    def __init__(self, name: Optional[str] = None):
        self.name = name or "enhanced_lineage_graph"

        # Core graph data structures
        self.nodes = {}  # node_id -> LineageNode
        self.edges = []  # List of EnhancedLineageEdge
        self.lineage_nodes = {}  # lineage_id -> LineageNode
        self.context_nodes = {}  # context_id -> List[LineageNode]

        # Fork tracking
        self.fork_points = {}  # lineage_id -> ForkPoint
        self.fork_edges = []  # List of edges that represent forks
        self.merge_points = {}  # lineage_id -> List[parent_lineage_ids]

        # Performance indexes
        self.children_index = defaultdict(list)  # source_id -> List[target_id]
        self.parents_index = defaultdict(list)  # target_id -> List[source_id]
        self.lineage_hierarchy = defaultdict(list)  # lineage_id -> List[child_lineage_ids]

        # Statistics
        self.creation_time = time.time()
        self.last_updated = time.time()

    def add_lineage_node(self, lineage_id: LineageID, context: ExecutionContext = None) -> LineageNode:
        """Add a lineage node to the graph."""
        node = LineageNode(
            node_id=lineage_id.operation_id,
            lineage_id=lineage_id.id,
            context_id=context.context_id if context else lineage_id.context_id,
            node_type="lineage",
            name=f"{lineage_id.operation_type}_{lineage_id.id[:8]}",
            metadata={
                'operation_type': lineage_id.operation_type,
                'parent_ids': lineage_id.parent_ids,
                'is_source': lineage_id.is_source(),
                'is_merge_point': lineage_id.is_merge_point()
            }
        )

        self.nodes[node.node_id] = node
        self.lineage_nodes[lineage_id.id] = node

        if context:
            if context.context_id not in self.context_nodes:
                self.context_nodes[context.context_id] = []
            self.context_nodes[context.context_id].append(node)

        self._update_timestamp()
        logger.debug(f"Added lineage node: {lineage_id.id}")

        return node

    def add_lineage_relationship(self,
                                parent_lineage_id: str,
                                child_lineage_id: str,
                                context_id: str = None,
                                is_fork: bool = False) -> EnhancedLineageEdge:
        """Add a lineage relationship edge."""
        # Check if edge already exists to prevent duplicates
        for existing_edge in self.edges:
            if (existing_edge.source_id == parent_lineage_id and
                existing_edge.target_id == child_lineage_id):
                return existing_edge

        edge = EnhancedLineageEdge(
            source_id=parent_lineage_id,
            target_id=child_lineage_id,
            edge_type="lineage",
            context_id=context_id,
            is_fork_edge=is_fork,
            metadata={'relationship_type': 'parent_child'}
        )

        self.edges.append(edge)

        # Update indexes
        self.children_index[parent_lineage_id].append(child_lineage_id)
        self.parents_index[child_lineage_id].append(parent_lineage_id)
        self.lineage_hierarchy[parent_lineage_id].append(child_lineage_id)

        if is_fork:
            self.fork_edges.append(edge)

        self._update_timestamp()
        logger.debug(f"Added lineage relationship: {parent_lineage_id} -> {child_lineage_id}")

        return edge

    def add_fork_point(self, fork_point: ForkPoint) -> None:
        """Add a fork point to the graph."""
        self.fork_points[fork_point.lineage_id] = fork_point

        # Mark all edges from this fork point as fork edges
        for edge in self.edges:
            if edge.source_id == fork_point.lineage_id:
                edge.is_fork_edge = True
                edge.fork_degree = fork_point.get_fork_degree()

        self._update_timestamp()
        logger.debug(f"Added fork point: {fork_point.lineage_id} with degree {fork_point.get_fork_degree()}")

    def add_merge_point(self, lineage_id: str, parent_lineage_ids: List[str]) -> None:
        """Add a merge point (multiple parents) to the graph."""
        self.merge_points[lineage_id] = parent_lineage_ids

        # Update node metadata
        if lineage_id in self.lineage_nodes:
            node = self.lineage_nodes[lineage_id]
            node.metadata['is_merge_point'] = True
            node.metadata['parent_lineage_ids'] = parent_lineage_ids

        self._update_timestamp()
        logger.debug(f"Added merge point: {lineage_id} with parents {parent_lineage_ids}")

    def get_fork_points(self) -> List[ForkPoint]:
        """Get all fork points in the graph."""
        return list(self.fork_points.values())

    def get_merge_points(self) -> Dict[str, List[str]]:
        """Get all merge points in the graph."""
        return self.merge_points.copy()

    def get_children(self, lineage_id: str) -> List[str]:
        """Get all children of a lineage ID."""
        return self.children_index.get(lineage_id, [])

    def get_parents(self, lineage_id: str) -> List[str]:
        """Get all parents of a lineage ID."""
        return self.parents_index.get(lineage_id, [])

    def is_fork_point(self, lineage_id: str) -> bool:
        """Check if a lineage ID is a fork point."""
        return lineage_id in self.fork_points

    def is_merge_point(self, lineage_id: str) -> bool:
        """Check if a lineage ID is a merge point."""
        return lineage_id in self.merge_points

    def get_fork_degree(self, lineage_id: str) -> int:
        """Get the fork degree (number of children) for a lineage ID."""
        if lineage_id in self.fork_points:
            return self.fork_points[lineage_id].get_fork_degree()
        return len(self.get_children(lineage_id))

    def trace_lineage_path(self, start_lineage_id: str, end_lineage_id: str) -> List[str]:
        """Trace the path between two lineage IDs."""
        def dfs(current: str, target: str, path: List[str], visited: Set[str]) -> Optional[List[str]]:
            if current == target:
                return path + [current]

            if current in visited:
                return None

            visited.add(current)

            for child in self.get_children(current):
                result = dfs(child, target, path + [current], visited)
                if result:
                    return result

            return None

        return dfs(start_lineage_id, end_lineage_id, [], set()) or []

    def get_lineage_subgraph(self, lineage_ids: List[str]) -> 'EnhancedLineageGraph':
        """Create a subgraph containing only the specified lineage IDs."""
        subgraph = EnhancedLineageGraph(f"{self.name}_subgraph")

        # Add nodes
        for lineage_id in lineage_ids:
            if lineage_id in self.lineage_nodes:
                node = self.lineage_nodes[lineage_id]
                subgraph.nodes[node.node_id] = node
                subgraph.lineage_nodes[lineage_id] = node

        # Add edges
        for edge in self.edges:
            if edge.source_id in lineage_ids and edge.target_id in lineage_ids:
                subgraph.edges.append(edge)
                subgraph.children_index[edge.source_id].append(edge.target_id)
                subgraph.parents_index[edge.target_id].append(edge.source_id)

        # Add fork points
        for lineage_id in lineage_ids:
            if lineage_id in self.fork_points:
                subgraph.fork_points[lineage_id] = self.fork_points[lineage_id]

        return subgraph

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the lineage graph."""
        fork_points = self.get_fork_points()
        merge_points = self.get_merge_points()

        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'lineage_nodes': len(self.lineage_nodes),
            'context_nodes': len(self.context_nodes),
            'fork_points': len(fork_points),
            'merge_points': len(merge_points),
            'fork_edges': len(self.fork_edges),
            'max_fork_degree': max([fp.get_fork_degree() for fp in fork_points], default=0),
            'avg_fork_degree': (sum([fp.get_fork_degree() for fp in fork_points]) / len(fork_points)
                               if fork_points else 0),
            'diamond_patterns': self._detect_diamond_patterns(),
            'creation_time': self.creation_time,
            'last_updated': self.last_updated
        }

    def _detect_diamond_patterns(self) -> List[Dict[str, Any]]:
        """Detect diamond patterns (fork followed by merge)."""
        patterns = []

        for fork_id, fork_point in self.fork_points.items():
            # Get all downstream lineage IDs from fork consumers
            downstream_lineages = set()
            for context_id in fork_point.consumer_contexts:
                if context_id in self.context_nodes:
                    for node in self.context_nodes[context_id]:
                        downstream_lineages.add(node.lineage_id)

            # Check if any downstream lineage is a merge point
            for lineage_id in downstream_lineages:
                if lineage_id in self.merge_points:
                    parents = self.merge_points[lineage_id]
                    # Check if multiple parents come from the fork
                    fork_descendants = set()
                    for parent_id in parents:
                        if self._is_descendant_of(parent_id, fork_id):
                            fork_descendants.add(parent_id)

                    if len(fork_descendants) > 1:
                        patterns.append({
                            'fork_point': fork_id,
                            'merge_point': lineage_id,
                            'parallel_paths': list(fork_descendants),
                            'path_count': len(fork_descendants)
                        })

        return patterns

    def _is_descendant_of(self, descendant_id: str, ancestor_id: str) -> bool:
        """Check if one lineage ID is a descendant of another."""
        def dfs(current: str, target: str, visited: Set[str]) -> bool:
            if current == target:
                return True

            if current in visited:
                return False

            visited.add(current)

            for parent in self.get_parents(current):
                if dfs(parent, target, visited):
                    return True

            return False

        return dfs(descendant_id, ancestor_id, set())

    def export_to_dict(self) -> Dict[str, Any]:
        """Export the entire graph to a dictionary for serialization."""
        return {
            'name': self.name,
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': [edge.to_dict() for edge in self.edges],
            'fork_points': {lid: fp.to_dict() for lid, fp in self.fork_points.items()},
            'merge_points': self.merge_points,
            'statistics': self.get_statistics(),
            'creation_time': self.creation_time,
            'last_updated': self.last_updated
        }

    def generate_mermaid_diagram(self, include_fork_styling: bool = True) -> str:
        """Generate a Mermaid diagram with fork-aware styling."""
        lines = ["graph TD"]

        # Add nodes with special styling for fork and merge points
        for node_id, node in self.nodes.items():
            lineage_id = node.lineage_id
            display_name = node.name or node_id

            if include_fork_styling:
                if lineage_id and self.is_fork_point(lineage_id):
                    # Fork point styling
                    lines.append(f"    {node_id}[{display_name}]:::fork")
                elif lineage_id and self.is_merge_point(lineage_id):
                    # Merge point styling
                    lines.append(f"    {node_id}[{display_name}]:::merge")
                else:
                    lines.append(f"    {node_id}[{display_name}]")
            else:
                lines.append(f"    {node_id}[{display_name}]")

        # Add edges
        for edge in self.edges:
            if edge.is_fork_edge and include_fork_styling:
                lines.append(f"    {edge.source_id} -.->|fork| {edge.target_id}")
            else:
                lines.append(f"    {edge.source_id} --> {edge.target_id}")

        # Add styling classes
        if include_fork_styling:
            lines.extend([
                "    classDef fork fill:#ff9999,stroke:#333,stroke-width:2px",
                "    classDef merge fill:#99ff99,stroke:#333,stroke-width:2px"
            ])

        return "\n".join(lines)

    def _update_timestamp(self) -> None:
        """Update the last updated timestamp."""
        self.last_updated = time.time()

    def clear(self) -> None:
        """Clear all graph data."""
        self.nodes.clear()
        self.edges.clear()
        self.lineage_nodes.clear()
        self.context_nodes.clear()
        self.fork_points.clear()
        self.fork_edges.clear()
        self.merge_points.clear()
        self.children_index.clear()
        self.parents_index.clear()
        self.lineage_hierarchy.clear()
        self._update_timestamp()