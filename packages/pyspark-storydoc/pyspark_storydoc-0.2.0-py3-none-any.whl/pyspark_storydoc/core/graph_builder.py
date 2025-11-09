"""Graph structure for representing business lineage."""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from ..utils.dataframe_utils import calculate_impact_metrics, format_row_count
from ..utils.exceptions import LineageTrackingError, ValidationError
from ..utils.validation import validate_business_concept_name, validate_description

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the lineage graph."""
    SOURCE = "source"
    BUSINESS_CONCEPT = "business_concept"
    OPERATION = "operation"
    CONTEXT_GROUP = "context_group"
    SINK = "sink"


class OperationType(Enum):
    """Types of operations that can be tracked."""
    SOURCE = "source"
    FILTER = "filter"
    JOIN = "join"
    GROUP_BY = "groupby"
    AGGREGATE = "aggregate"
    SELECT = "select"
    TRANSFORM = "transform"
    WITH_COLUMN = "withColumn"
    DROP = "drop"
    UNION = "union"
    DISTINCT = "distinct"
    ORDER_BY = "orderBy"
    SORT = "sort"
    LIMIT = "limit"
    SAMPLE = "sample"
    DESCRIBE_PROFILE = "describe_profile"
    CUSTOM = "custom"
    COMPRESSED = "compressed"


@dataclass
class MetricsData:
    """Container for metrics associated with a DataFrame operation."""
    row_count: int
    distinct_counts: Dict[str, int] = field(default_factory=dict)
    column_count: int = 0
    schema_info: Optional[Dict[str, Any]] = None
    computation_time: Optional[float] = None
    estimated: bool = False

    def __post_init__(self) -> None:
        """Validate metrics data after initialization."""
        if self.row_count < 0:
            raise ValidationError("Row count cannot be negative")


@dataclass
class LineageEdge:
    """Represents a connection between nodes in the lineage graph."""
    source_id: str
    target_id: str
    edge_type: str = "data_flow"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate edge data after initialization."""
        if not self.source_id or not self.target_id:
            raise ValidationError("Source and target IDs cannot be empty")


class BaseLineageNode:
    """Base class for all lineage nodes."""

    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: NodeType,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base lineage node.

        Args:
            node_id: Unique identifier for the node
            name: Display name for the node
            node_type: Type of the node
            description: Optional description
            metadata: Optional metadata dictionary
        """
        validate_business_concept_name(name)
        validate_description(description)

        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.description = description
        self.metadata = metadata or {}
        self.created_at = time.time()

        # Lineage connections
        self.parents: Set[str] = set()
        self.children: Set[str] = set()

    def add_parent(self, parent_id: str) -> None:
        """Add a parent node."""
        self.parents.add(parent_id)

    def add_child(self, child_id: str) -> None:
        """Add a child node."""
        self.children.add(child_id)

    def get_display_name(self, max_length: int = 50) -> str:
        """Get a display-friendly version of the name."""
        from ..utils.validation import sanitize_for_visualization
        return sanitize_for_visualization(self.name, max_length)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type.value,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "parents": list(self.parents),
            "children": list(self.children),
        }


class BusinessConceptNode(BaseLineageNode):
    """Represents a business concept in the lineage graph."""

    def __init__(
        self,
        node_id: str,
        name: str,
        description: Optional[str] = None,
        function_name: Optional[str] = None,
        materialize: bool = True,
        track_columns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        governance_metadata: Optional[Any] = None,  # GovernanceMetadata or dict
    ):
        """
        Initialize business concept node.

        Args:
            node_id: Unique identifier
            name: Business-friendly name
            description: Detailed description
            function_name: Name of the Python function (if applicable)
            materialize: Whether to compute metrics
            track_columns: Columns to track for distinct counts
            metadata: Additional metadata
            governance_metadata: Governance and compliance metadata
        """
        super().__init__(node_id, name, NodeType.BUSINESS_CONCEPT, description, metadata)

        self.function_name = function_name
        self.materialize = materialize
        self.track_columns = track_columns or []

        # Metrics
        self.input_metrics: Optional[MetricsData] = None
        self.output_metrics: Optional[MetricsData] = None
        self.execution_time: Optional[float] = None

        # Sub-operations within this concept
        self.technical_operations: List['OperationNode'] = []

        # Execution tracking
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Governance metadata
        self.governance_metadata: Optional[Any] = None  # Will be GovernanceMetadata type
        if governance_metadata is not None:
            self._set_governance_metadata(governance_metadata)

    def _set_governance_metadata(self, gov_data: Any):
        """Set governance metadata from dict or GovernanceMetadata object."""
        if gov_data is None:
            self.governance_metadata = None
            return

        # Import here to avoid circular dependency
        try:
            from ..governance.enhanced_metadata import EnhancedGovernanceMetadata
            from ..governance.metadata import GovernanceMetadata

            # Check for enhanced governance metadata first (it's the newer type)
            if isinstance(gov_data, EnhancedGovernanceMetadata):
                self.governance_metadata = gov_data
            elif isinstance(gov_data, GovernanceMetadata):
                self.governance_metadata = gov_data
            elif isinstance(gov_data, dict):
                # Try enhanced first, fallback to basic
                try:
                    self.governance_metadata = EnhancedGovernanceMetadata(**gov_data)
                except (TypeError, KeyError):
                    self.governance_metadata = GovernanceMetadata.from_dict(gov_data)
            else:
                logger.warning(f"Invalid governance_metadata type: {type(gov_data)}")
                self.governance_metadata = None
        except ImportError:
            # Governance module not available
            logger.debug("Governance module not available")
            self.governance_metadata = None

    def start_execution(self) -> None:
        """Mark the start of execution for this concept."""
        self.start_time = time.time()

    def end_execution(self) -> None:
        """Mark the end of execution for this concept."""
        self.end_time = time.time()
        if self.start_time:
            self.execution_time = self.end_time - self.start_time

    def add_technical_operation(self, operation: 'OperationNode') -> None:
        """Add a technical operation that occurred within this business concept."""
        self.technical_operations.append(operation)

    def calculate_impact(self) -> Optional[Dict[str, Any]]:
        """Calculate business impact metrics."""
        if not (self.input_metrics and self.output_metrics):
            return None

        return calculate_impact_metrics(
            self.input_metrics.row_count,
            self.output_metrics.row_count
        )

    def get_business_summary(self) -> str:
        """Generate business-friendly summary of this concept's impact."""
        impact = self.calculate_impact()
        if not impact:
            return f"Business Concept: {self.name}"

        return f"{self.name}: {impact['impact_description']}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "function_name": self.function_name,
            "materialize": self.materialize,
            "track_columns": self.track_columns,
            "input_metrics": self.input_metrics.__dict__ if self.input_metrics else None,
            "output_metrics": self.output_metrics.__dict__ if self.output_metrics else None,
            "execution_time": self.execution_time,
            "technical_operations": [op.to_dict() for op in self.technical_operations],
            "impact": self.calculate_impact(),
            "governance_metadata": self.governance_metadata.to_dict() if self.governance_metadata else None,
        })
        return base_dict


class OperationNode(BaseLineageNode):
    """Represents a technical operation in the lineage graph."""

    def __init__(
        self,
        node_id: str,
        operation_type: OperationType,
        business_context: str,
        technical_details: Optional[str] = None,
        before_metrics: Optional[MetricsData] = None,
        after_metrics: Optional[MetricsData] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize operation node.

        Args:
            node_id: Unique identifier
            operation_type: Type of operation
            business_context: Business-friendly description
            technical_details: Technical implementation details
            before_metrics: Metrics before the operation
            after_metrics: Metrics after the operation
            metadata: Additional metadata
        """
        super().__init__(node_id, business_context, NodeType.OPERATION, metadata=metadata)

        self.operation_type = operation_type
        self.technical_details = technical_details
        self.before_metrics = before_metrics
        self.after_metrics = after_metrics

    def calculate_impact(self) -> Optional[Dict[str, Any]]:
        """Calculate impact of this operation."""
        if not (self.before_metrics and self.after_metrics):
            return None

        return calculate_impact_metrics(
            self.before_metrics.row_count,
            self.after_metrics.row_count
        )

    def get_operation_summary(self) -> str:
        """Get a summary of the operation's impact."""
        impact = self.calculate_impact()
        if not impact:
            return f"{self.operation_type.value.title()}: {self.name}"

        return f"{self.name}: {impact['impact_description']}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "operation_type": self.operation_type.value,
            "technical_details": self.technical_details,
            "before_metrics": self.before_metrics.__dict__ if self.before_metrics else None,
            "after_metrics": self.after_metrics.__dict__ if self.after_metrics else None,
            "impact": self.calculate_impact(),
        })
        return base_dict


class ContextGroupNode(BaseLineageNode):
    """Represents a group of operations with shared business context."""

    def __init__(
        self,
        node_id: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize context group node.

        Args:
            node_id: Unique identifier
            name: Business-friendly name for the group
            description: Detailed description
            metadata: Additional metadata
        """
        super().__init__(node_id, name, NodeType.CONTEXT_GROUP, description, metadata)

        self.operations: List[OperationNode] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def add_operation(self, operation: OperationNode) -> None:
        """Add an operation to this context group."""
        self.operations.append(operation)
        operation.add_parent(self.node_id)
        self.add_child(operation.node_id)

    def start_context(self) -> None:
        """Mark the start of this context."""
        self.start_time = time.time()

    def end_context(self) -> None:
        """Mark the end of this context."""
        self.end_time = time.time()

    def get_aggregate_impact(self) -> Optional[Dict[str, Any]]:
        """Calculate aggregate impact of all operations in this context."""
        if not self.operations:
            return None

        first_op = self.operations[0]
        last_op = self.operations[-1]

        if not (first_op.before_metrics and last_op.after_metrics):
            return None

        return calculate_impact_metrics(
            first_op.before_metrics.row_count,
            last_op.after_metrics.row_count
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            "operations": [op.to_dict() for op in self.operations],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "aggregate_impact": self.get_aggregate_impact(),
        })
        return base_dict


class LineageGraph:
    """Manages the complete business lineage graph."""

    def __init__(self, name: Optional[str] = None):
        """
        Initialize lineage graph.

        Args:
            name: Optional name for the graph
        """
        self.name = name or "Business Lineage"
        self.nodes: Dict[str, BaseLineageNode] = {}
        self.edges: List[LineageEdge] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = time.time()

    def add_node(self, node: BaseLineageNode) -> None:
        """
        Add a node to the graph.

        Args:
            node: Node to add

        Raises:
            LineageTrackingError: If node ID already exists
        """
        if node.node_id in self.nodes:
            raise LineageTrackingError(f"Node with ID '{node.node_id}' already exists")

        self.nodes[node.node_id] = node
        logger.debug(f"Added node: {node.node_id} ({node.name})")

    def add_edge(self, edge: LineageEdge) -> None:
        """
        Add an edge to the graph.

        Args:
            edge: Edge to add

        Raises:
            LineageTrackingError: If source or target nodes don't exist
        """
        if edge.source_id not in self.nodes:
            raise LineageTrackingError(f"Source node '{edge.source_id}' not found")
        if edge.target_id not in self.nodes:
            raise LineageTrackingError(f"Target node '{edge.target_id}' not found")

        self.edges.append(edge)

        # Update node connections
        self.nodes[edge.source_id].add_child(edge.target_id)
        self.nodes[edge.target_id].add_parent(edge.source_id)

        logger.debug(f"Added edge: {edge.source_id} -> {edge.target_id}")

    def get_node(self, node_id: str) -> Optional[BaseLineageNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_business_concepts(self) -> List[BusinessConceptNode]:
        """Get all business concept nodes."""
        return [
            node for node in self.nodes.values()
            if isinstance(node, BusinessConceptNode)
        ]

    def get_operations(self) -> List[OperationNode]:
        """Get all operation nodes."""
        return [
            node for node in self.nodes.values()
            if isinstance(node, OperationNode)
        ]

    def get_root_nodes(self) -> List[BaseLineageNode]:
        """Get nodes with no parents (data sources)."""
        return [node for node in self.nodes.values() if not node.parents]

    def get_leaf_nodes(self) -> List[BaseLineageNode]:
        """Get nodes with no children (outputs)."""
        return [node for node in self.nodes.values() if not node.children]

    def validate_graph(self) -> List[str]:
        """
        Validate the graph structure and return any issues found.

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check for orphaned nodes
        referenced_nodes = set()
        for edge in self.edges:
            referenced_nodes.add(edge.source_id)
            referenced_nodes.add(edge.target_id)

        orphaned = set(self.nodes.keys()) - referenced_nodes
        if len(orphaned) > 1:  # One orphan is okay (root node)
            issues.append(f"Multiple orphaned nodes found: {orphaned}")

        # Check for cycles (simplified check)
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            for child_id in self.nodes[node_id].children:
                if has_cycle(child_id):
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    issues.append("Cycle detected in graph")
                    break

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "name": self.name,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "edges": [edge.__dict__ for edge in self.edges],
            "validation_issues": self.validate_graph(),
            "statistics": {
                "total_nodes": len(self.nodes),
                "business_concepts": len(self.get_business_concepts()),
                "operations": len(self.get_operations()),
                "edges": len(self.edges),
            }
        }

    def set_lineage_graph_from_dict(self, graph_dict: Dict[str, Any]) -> None:
        """
        Reconstruct the lineage graph from a dictionary representation.

        Args:
            graph_dict: Dictionary representation of the lineage graph
        """
        # Clear existing graph
        self.nodes = {}
        self.edges = []

        # Set basic properties
        self.name = graph_dict.get("name", "Business Lineage")
        self.created_at = graph_dict.get("created_at", time.time())
        self.metadata = graph_dict.get("metadata", {})

        # Recreate nodes
        nodes_data = graph_dict.get("nodes", {})
        for node_id, node_data in nodes_data.items():
            node = self._create_node_from_dict(node_data)
            if node:
                self.nodes[node_id] = node

        # Recreate edges
        edges_data = graph_dict.get("edges", [])
        for edge_data in edges_data:
            edge = LineageEdge(
                source_id=edge_data["source_id"],
                target_id=edge_data["target_id"],
                edge_type=edge_data.get("edge_type", "data_flow"),
                metadata=edge_data.get("metadata", {})
            )
            self.edges.append(edge)

        logger.debug(f"Reconstructed lineage graph with {len(self.nodes)} nodes and {len(self.edges)} edges")

    def _create_node_from_dict(self, node_data: Dict[str, Any]) -> Optional[BaseLineageNode]:
        """Create a node from dictionary data."""
        node_type = node_data.get("node_type")

        if node_type == "business_concept":
            return self._create_business_concept_from_dict(node_data)
        elif node_type == "operation":
            return self._create_operation_from_dict(node_data)
        elif node_type == "context_group":
            return self._create_context_group_from_dict(node_data)
        else:
            logger.warning(f"Unknown node type: {node_type}")
            return None

    def _create_business_concept_from_dict(self, node_data: Dict[str, Any]) -> BusinessConceptNode:
        """Create a BusinessConceptNode from dictionary data."""
        from ..utils.validation import sanitize_for_visualization

        # Sanitize the name to avoid validation issues
        original_name = node_data["name"]
        sanitized_name = sanitize_for_visualization(original_name, max_length=200)

        # Create the business concept node
        metadata = node_data.get("metadata", {}).copy()
        # Store the original name in metadata if it was sanitized
        if original_name != sanitized_name:
            metadata["original_name"] = original_name

        node = BusinessConceptNode(
            node_id=node_data["node_id"],
            name=sanitized_name,
            description=node_data.get("description"),
            function_name=node_data.get("function_name"),
            materialize=node_data.get("materialize", True),
            track_columns=node_data.get("track_columns", []),
            metadata=metadata
        )

        # Set additional properties
        node.created_at = node_data.get("created_at", time.time())
        node.parents = node_data.get("parents", [])
        node.children = node_data.get("children", [])
        node.execution_time = node_data.get("execution_time")

        # Recreate metrics
        if node_data.get("input_metrics"):
            node.input_metrics = self._create_metrics_from_dict(node_data["input_metrics"])
        if node_data.get("output_metrics"):
            node.output_metrics = self._create_metrics_from_dict(node_data["output_metrics"])

        # Recreate technical operations
        tech_ops_data = node_data.get("technical_operations", [])
        for op_data in tech_ops_data:
            op_node = self._create_operation_from_dict(op_data)
            if op_node:
                node.technical_operations.append(op_node)

        return node

    def _create_operation_from_dict(self, node_data: Dict[str, Any]) -> OperationNode:
        """Create an OperationNode from dictionary data."""
        from ..utils.validation import sanitize_for_visualization

        # Convert operation type string back to enum
        try:
            operation_type = OperationType(node_data["operation_type"])
        except ValueError:
            operation_type = OperationType.CUSTOM

        # Sanitize the business_context to avoid validation issues
        original_name = node_data["name"]
        sanitized_name = sanitize_for_visualization(original_name, max_length=200)

        # Store original name in metadata if it was sanitized
        metadata = node_data.get("metadata", {}).copy()
        if original_name != sanitized_name:
            metadata["original_name"] = original_name

        # Create the operation node
        node = OperationNode(
            node_id=node_data["node_id"],
            operation_type=operation_type,
            business_context=sanitized_name,
            technical_details=node_data.get("technical_details"),
            metadata=metadata
        )

        # Set additional properties
        node.created_at = node_data.get("created_at", time.time())
        node.parents = node_data.get("parents", [])
        node.children = node_data.get("children", [])

        # Recreate metrics
        if node_data.get("before_metrics"):
            node.before_metrics = self._create_metrics_from_dict(node_data["before_metrics"])
        if node_data.get("after_metrics"):
            node.after_metrics = self._create_metrics_from_dict(node_data["after_metrics"])

        return node

    def _create_context_group_from_dict(self, node_data: Dict[str, Any]) -> ContextGroupNode:
        """Create a ContextGroupNode from dictionary data."""
        from ..utils.validation import sanitize_for_visualization

        # Sanitize the name to avoid validation issues
        original_name = node_data["name"]
        sanitized_name = sanitize_for_visualization(original_name, max_length=200)

        # Store original name in metadata if it was sanitized
        metadata = node_data.get("metadata", {}).copy()
        if original_name != sanitized_name:
            metadata["original_name"] = original_name

        node = ContextGroupNode(
            node_id=node_data["node_id"],
            name=sanitized_name,
            description=node_data.get("description"),
            metadata=metadata
        )

        # Set additional properties
        node.created_at = node_data.get("created_at", time.time())
        node.parents = node_data.get("parents", [])
        node.children = node_data.get("children", [])
        node.start_time = node_data.get("start_time")
        node.end_time = node_data.get("end_time")

        # Recreate operations
        ops_data = node_data.get("operations", [])
        for op_data in ops_data:
            op_node = self._create_operation_from_dict(op_data)
            if op_node:
                node.operations.append(op_node)

        return node

    def _create_metrics_from_dict(self, metrics_data: Dict[str, Any]) -> MetricsData:
        """Create MetricsData from dictionary data."""
        return MetricsData(
            row_count=metrics_data["row_count"],
            distinct_counts=metrics_data.get("distinct_counts", {}),
            column_count=metrics_data.get("column_count", 0),
            schema_info=metrics_data.get("schema_info"),
            computation_time=metrics_data.get("computation_time"),
            estimated=metrics_data.get("estimated", False)
        )