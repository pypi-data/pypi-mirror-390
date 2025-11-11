"""
Lineage Diagram Generator - Creates comprehensive data lineage visualizations.

This module generates detailed Mermaid diagrams that show:
1. Each operation as its own node with input/output counts
2. Tracked column distinct counts at each operation
3. Proper handling of joins between lineages
4. Record count changes on connection arrows
5. Business concept groupings
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.fork_detector import ForkPoint, get_fork_detector
from ..core.graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
    LineageEdge,
    LineageGraph,
    MetricsData,
    OperationNode,
    OperationType,
)
from ..utils.exceptions import VisualizationError
from .diagram_styles import (
    NODE_STYLES,
    generate_mermaid_style_classes,
    get_mermaid_shape_template,
    get_node_class_name,
    get_node_style,
)

logger = logging.getLogger(__name__)


@dataclass
class OperationMetrics:
    """Detailed metrics for a single operation."""
    operation_id: str
    operation_name: str
    operation_type: OperationType

    # Record counts
    input_record_count: Optional[int] = None
    output_record_count: Optional[int] = None

    # Tracked column metrics - distinct counts per column
    input_column_metrics: Dict[str, int] = field(default_factory=dict)
    output_column_metrics: Dict[str, int] = field(default_factory=dict)

    # Operation specifics
    filter_condition: Optional[str] = None
    join_type: Optional[str] = None
    join_keys: List[str] = field(default_factory=list)
    group_by_columns: List[str] = field(default_factory=list)
    aggregations: List[str] = field(default_factory=list)
    business_label: Optional[str] = None
    input_column_count: Optional[int] = None
    output_column_count: Optional[int] = None

    # Performance
    execution_time: Optional[float] = None

    # For joins - track both inputs
    left_input_count: Optional[int] = None
    right_input_count: Optional[int] = None
    left_unique_keys: Optional[int] = None
    right_unique_keys: Optional[int] = None
    matched_keys: Optional[int] = None

    # Metadata for filtering decisions
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def record_change(self) -> Optional[int]:
        """Calculate record count change."""
        if self.input_record_count is not None and self.output_record_count is not None:
            return self.output_record_count - self.input_record_count
        return None

    @property
    def record_change_pct(self) -> Optional[float]:
        """Calculate percentage change."""
        if self.input_record_count and self.output_record_count is not None:
            return ((self.output_record_count - self.input_record_count) / self.input_record_count) * 100
        return None


@dataclass
class BusinessConceptGroup:
    """Represents a business concept with its operations."""
    concept_id: str
    concept_name: str
    concept_description: str
    tracked_columns: List[str]
    operations: List[OperationMetrics]

    # Track lineage connections
    input_operations: List[str] = field(default_factory=list) # Operations feeding into this group
    output_operations: List[str] = field(default_factory=list) # Operations this group feeds into


@dataclass
class LineageFlow:
    """Represents a complete lineage flow with multiple concepts."""
    name: str
    business_concepts: List[BusinessConceptGroup]
    source_operations: List[str] # Entry points
    sink_operations: List[str] # Exit points
    join_points: List[Dict[str, Any]] # Join operations connecting lineages


@dataclass
class CompressionSequence:
    """Represents a sequence of consecutive non-impacting operations to be compressed."""
    sequence_id: str
    operations: List[str]  # List of operation IDs in the sequence
    operation_types: List[str]  # List of operation type names for reference
    source_node: Optional[str] = None  # Impacting node before sequence (or None if starts from source)
    target_node: Optional[str] = None  # Impacting node after sequence (or None if terminal)
    concept_id: Optional[str] = None  # Business concept this sequence belongs to


class LineageDiagramGenerator:
    """
    Generates comprehensive lineage diagrams with full metrics.

    This diagram generator creates:
    - Each operation as a separate node
    - Full input/output metrics including tracked column counts
    - Proper join handling between lineages
    - Business concept groupings
    """

    def __init__(
        self,
        show_column_metrics: bool = True,
        show_percentages: bool = True,
        show_execution_times: bool = False,
        abbreviate_conditions: bool = True,
        max_condition_length: int = 50,
        operation_filter: str = "all",
        group_raw_operations: bool = True,
        show_passthrough_operations: bool = False
    ):
        """
        Initialize the detailed flow visualizer.

        Args:
            show_column_metrics: Whether to show tracked column distinct counts
            show_percentages: Whether to show percentage changes
            show_execution_times: Whether to show execution times
            abbreviate_conditions: Whether to abbreviate long filter conditions
            max_condition_length: Maximum length for filter conditions
            operation_filter: Filter for operations to include:
                - "all": Show all operations
                - "impacting": Show only operations that impact tracked columns
                - List[OperationType]: Show only specific operation types
            group_raw_operations: Whether to group raw operations under "Data Operations"
                - True: Raw operations grouped under default BusinessConceptGroup
                - False: Raw operations rendered as standalone nodes
            show_passthrough_operations: Whether to include passthrough operations as nodes
                - True: Show all operations including delegated passthrough methods
                - False: Hide passthrough operations from visualization (default)
        """
        self.show_column_metrics = show_column_metrics
        self.show_percentages = show_percentages
        self.show_execution_times = show_execution_times
        self.abbreviate_conditions = abbreviate_conditions
        self.max_condition_length = max_condition_length
        self.operation_filter = operation_filter
        self.group_raw_operations = group_raw_operations
        self.show_passthrough_operations = show_passthrough_operations

        # Track node relationships for join detection
        self._operation_inputs: Dict[str, List[str]] = defaultdict(list)
        self._operation_outputs: Dict[str, List[str]] = defaultdict(list)

    def analyze_lineage_flow(self, lineage_graph: LineageGraph) -> LineageFlow:
        """
        Analyze the lineage graph to extract detailed operation flows.

        Args:
            lineage_graph: The lineage graph to analyze

        Returns:
            LineageFlow with detailed operation metrics
        """
        # Extract business concepts and their operations
        business_concepts = self._extract_business_concepts(lineage_graph)

        # Deduplicate source operations before processing
        business_concepts = self._deduplicate_source_operations(business_concepts, lineage_graph)

        # Extract detailed metrics for each operation
        for concept in business_concepts:
            concept.operations = self._extract_operation_metrics(
                concept, lineage_graph
            )

        # Identify join points between lineages
        join_points = self._identify_join_points(lineage_graph)

        # Identify source and sink operations
        source_ops, sink_ops = self._identify_flow_endpoints(lineage_graph)

        return LineageFlow(
            name="Data Processing Pipeline",
            business_concepts=business_concepts,
            source_operations=source_ops,
            sink_operations=sink_ops,
            join_points=join_points
        )

    def _calculate_longest_path(self, lineage_graph) -> int:
        """
        Calculate the longest path in the lineage graph using DFS.

        Args:
            lineage_graph: EnhancedLineageGraph or LineageGraph

        Returns:
            Length of the longest path (number of nodes)
        """
        # Build adjacency list
        adjacency = defaultdict(list)
        nodes = set()

        if isinstance(lineage_graph, EnhancedLineageGraph):
            for edge in lineage_graph.edges:
                adjacency[edge.source_id].append(edge.target_id)
                nodes.add(edge.source_id)
                nodes.add(edge.target_id)
        else:
            for edge in lineage_graph.edges:
                adjacency[edge.source_id].append(edge.target_id)
                nodes.add(edge.source_id)
                nodes.add(edge.target_id)

        # Find all source nodes (nodes with no incoming edges)
        has_incoming = set()
        for targets in adjacency.values():
            has_incoming.update(targets)
        sources = nodes - has_incoming

        if not sources:
            # If no sources found (cycle or disconnected), use all nodes
            sources = nodes

        # DFS to find longest path from each source
        def dfs(node, visited):
            max_depth = 1
            visited.add(node)
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    max_depth = max(max_depth, 1 + dfs(neighbor, visited.copy()))
            return max_depth

        longest = 0
        for source in sources:
            path_length = dfs(source, set())
            longest = max(longest, path_length)

        return longest

    def create_detailed_mermaid(
        self,
        lineage_graph,  # Accept both LineageGraph and EnhancedLineageGraph
        title: str = "Detailed Operation Flow"
    ) -> str:
        """
        Create a detailed Mermaid diagram showing all operations with metrics.

        Args:
            lineage_graph: The lineage graph to visualize (LineageGraph or EnhancedLineageGraph)
            title: Title for the diagram

        Returns:
            Mermaid diagram as string
        """
        try:
            # Handle enhanced graph directly without conversion
            if isinstance(lineage_graph, EnhancedLineageGraph):
                return self._create_enhanced_mermaid_diagram(lineage_graph, title)

            flow = self.analyze_lineage_flow(lineage_graph)

            # Sanitize title for Mermaid compatibility
            sanitized_title = self._sanitize_title(title)

            lines = []
            # Add Mermaid configuration for proper width and spacing
            lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '12px', 'primaryColor': '#FAFAFA', 'primaryBorderColor': '#999', 'background': '#FAFAFA', 'mainBkg': '#FAFAFA', 'secondaryColor': '#F5F5F5', 'tertiaryColor': '#FFFFFF', 'clusterBkg': '#F5F5F5', 'clusterBorder': '#999', 'edgeLabelBackground': '#FAFAFA'}, 'flowchart': {'nodeSpacing': 150, 'rankSpacing': 100, 'curve': 'basis', 'padding': 25, 'htmlLabels': true, 'diagramPadding': 20}}}%%")

            # Determine direction based on longest path
            longest_path = self._calculate_longest_path(lineage_graph)
            direction = "LR" if longest_path < 10 else "TD"
            lines.append(f"flowchart {direction}")

            # Wrap entire diagram in a container subgraph for unified background
            lines.append(' subgraph Container[" "]')

            # Track generated node IDs
            node_ids = {}
            node_counter = 1

            # Process each business concept group
            for concept_idx, concept in enumerate(flow.business_concepts):
                # Check if this is a standalone operations group
                is_standalone = getattr(concept, '_is_standalone', False)

                if concept.operations:
                    if is_standalone or concept.concept_name == "":
                        # Render operations as standalone nodes (no subgraph)
                        for op_idx, operation in enumerate(concept.operations):
                            node_id = f"Op_{node_counter}"
                            node_ids[operation.operation_id] = node_id
                            node_counter += 1

                            # Build detailed node label with proper escaping
                            node_label = self._build_detailed_node_label(operation)

                            # Choose node shape based on operation type
                            shape_def = self._get_node_shape(operation)

                            # Add standalone node (extra indent for container subgraph)
                            lines.append(f'     {node_id}{shape_def}')
                            lines.append("") # Add spacing after each node
                    else:
                        # Create subgraph for business concept
                        subgraph_id = f"BC{concept_idx + 1}"

                        # Use only the concept name for subgraph title
                        subgraph_title = concept.concept_name
                        lines.append(f'  subgraph {subgraph_id}["{subgraph_title}"]')

                        # Add each operation as a node within subgraph
                        for op_idx, operation in enumerate(concept.operations):
                            node_id = f"Op_{node_counter}"
                            node_ids[operation.operation_id] = node_id
                            node_counter += 1

                            # Build detailed node label with proper escaping
                            node_label = self._build_detailed_node_label(operation)

                            # Choose node shape based on operation type
                            shape_def = self._get_node_shape(operation)

                            # Add node with subgraph indentation (extra indent for container)
                            lines.append(f'     {node_id}{shape_def}')
                            lines.append("") # Add spacing after each node

                        lines.append("  end")
                        lines.append("") # Add spacing between subgraphs

            # Close container subgraph
            lines.append(" end")
            lines.append("")

            # Add connections between operations
            lines.extend(self._generate_connections(flow, node_ids, lineage_graph))

            # Add node class assignments for styling
            lines.extend(self._generate_node_classes(flow, node_ids))

            # Add styling
            lines.extend(self._generate_styles())

            return "\n".join(lines)

        except Exception as e:
            raise VisualizationError(f"Failed to create detailed Mermaid diagram: {e}")


    def _sanitize_title(self, title: str) -> str:
        """Sanitize title for Mermaid compatibility by removing invalid characters."""
        if not title:
            return title

        # Replace characters that cause issues in Mermaid titles
        sanitized = title.replace(":", " -").replace(";", ",").replace('"', "'")

        # Remove any other potentially problematic characters
        sanitized = re.sub(r'[^\w\s\-\(\)\[\],.\']+', '', sanitized)

        return sanitized

    def _create_enhanced_mermaid_diagram(self, enhanced_graph: EnhancedLineageGraph, title: str) -> str:
        """
        Create a Mermaid diagram directly from the enhanced lineage graph.
        This follows the natural lineage flow where business concept nodes are the main nodes.

        Args:
            enhanced_graph: The enhanced lineage graph to visualize
            title: Title for the diagram

        Returns:
            Mermaid diagram as string
        """
        lines = []
        # Add Mermaid configuration
        lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '12px', 'primaryColor': '#FAFAFA', 'primaryBorderColor': '#999', 'background': '#FAFAFA', 'mainBkg': '#FAFAFA', 'secondaryColor': '#F5F5F5', 'tertiaryColor': '#FFFFFF', 'clusterBkg': '#F5F5F5', 'clusterBorder': '#999', 'edgeLabelBackground': '#FAFAFA'}, 'flowchart': {'nodeSpacing': 150, 'rankSpacing': 100, 'curve': 'basis', 'padding': 25, 'htmlLabels': true, 'diagramPadding': 20}}}%%")

        # Determine direction based on longest path
        longest_path = self._calculate_longest_path(enhanced_graph)
        direction = "LR" if longest_path < 10 else "TD"
        lines.append(f"flowchart {direction}")

        # Wrap entire diagram in a container subgraph for unified background
        lines.append(' subgraph Container[" "]')

        # Categorize nodes: separate business concepts from operations
        business_concept_nodes = {}  # context_id -> concept node (for containers/subgraphs)
        operation_nodes = {}  # node_id -> operation node
        source_nodes = []

        # First pass: categorize all nodes
        for node_id, node in enhanced_graph.nodes.items():
            op_type = node.metadata.get('operation_type')

            if op_type == 'business_concept':
                # Business concept nodes are containers, not operations
                business_concept_nodes[node_id] = node
            elif op_type == 'source':
                source_nodes.append(node)
            else:
                # All other nodes are operations
                operation_nodes[node_id] = node

        # Build hierarchy: map context_id to operations
        concept_to_operations = {}
        for node_id, node in operation_nodes.items():
            context_id = node.context_id or node.metadata.get('context_id')
            if context_id:
                if context_id not in concept_to_operations:
                    concept_to_operations[context_id] = []
                concept_to_operations[context_id].append(node)

        # Build parent-child hierarchy for business concepts
        concept_hierarchy = {}  # context_id -> {'node': node, 'children': [child_context_ids], 'parent': parent_context_id}
        for node_id, concept_node in business_concept_nodes.items():
            # Use the actual context_id from the concept node, not the node_id
            context_id = concept_node.context_id or concept_node.metadata.get('context_id') or node_id
            hierarchy_info = concept_node.metadata.get('hierarchy', {})
            parent_id = hierarchy_info.get('parent_context_id')

            concept_hierarchy[context_id] = {
                'node': concept_node,
                'children': [],
                'parent': parent_id,
                'depth': hierarchy_info.get('depth', 0)
            }

        # Populate children lists
        for context_id, info in concept_hierarchy.items():
            if info['parent'] and info['parent'] in concept_hierarchy:
                concept_hierarchy[info['parent']]['children'].append(context_id)

        # Find root concepts (no parent or parent not in hierarchy)
        root_concepts = [
            ctx_id for ctx_id, info in concept_hierarchy.items()
            if not info['parent'] or info['parent'] not in concept_hierarchy
        ]

        node_counter = 1
        node_ids = {}
        lineage_to_mermaid = {}
        concept_counter = 1

        # Create source nodes subgraph first
        if source_nodes:
            lines.append(f'  subgraph BC{concept_counter}["Data Sources"]')
            for node in source_nodes:
                mermaid_id = f"Op_{node_counter}"
                node_ids[node.node_id] = mermaid_id
                if node.lineage_id:
                    lineage_to_mermaid[node.lineage_id] = mermaid_id
                node_counter += 1

                node_shape = self._get_node_shape(node)
                lines.append(f'  {mermaid_id}{node_shape}')

            lines.append("  end")
            lines.append("")
            concept_counter += 1

        # Helper function to render concept and its children recursively
        def render_concept_subgraph(context_id, depth=0):
            nonlocal concept_counter, node_counter

            if context_id not in concept_hierarchy:
                return

            concept_info = concept_hierarchy[context_id]
            concept_node = concept_info['node']

            # Get concept details
            concept_name = concept_node.metadata.get('operation_name', 'Business Operations')

            # Use only the concept name for subgraph label, with risk indicator if applicable
            subgraph_label = self._format_subgraph_label_with_risk(concept_name, concept_node)

            # Add extra space for container subgraph
            indent = ' ' * (depth + 2)
            lines.append(f'{indent}subgraph BC{concept_counter}["{subgraph_label}"]')
            concept_counter += 1

            # For COMPLETE and IMPACTING detail levels, show individual operations
            # For MINIMAL, just show the business concept node
            if self.operation_filter != "none":
                # Show child concepts first (nested subgraphs)
                for child_id in concept_info['children']:
                    render_concept_subgraph(child_id, depth + 1)

                # Show operations within this concept
                operations = concept_to_operations.get(context_id, [])

                # Apply compression if using impacting filter
                if self.operation_filter == "impacting" and operations:
                    filtered_ops, compression_seqs = self._find_compression_sequences(
                        operations, concept_node, context_id
                    )
                    operations = filtered_ops
                    # Store compression sequences for later use in edge generation
                    if not hasattr(self, '_compression_sequences'):
                        self._compression_sequences = {}
                    self._compression_sequences.update(compression_seqs)

                for op_node in operations:
                    # For non-compressed nodes, check if operation should be included
                    is_compressed = op_node.metadata.get('is_compressed', False)
                    if not is_compressed:
                        op_metrics = self._build_operation_metrics_from_node(op_node)
                        if not self._should_include_operation(op_metrics, concept_node):
                            continue

                    mermaid_id = f"Op_{node_counter}"
                    node_ids[op_node.node_id] = mermaid_id
                    if op_node.lineage_id:
                        lineage_to_mermaid[op_node.lineage_id] = mermaid_id
                    node_counter += 1

                    node_shape = self._get_node_shape(op_node)
                    lines.append(f'{indent} {mermaid_id}{node_shape}')
            else:
                # MINIMAL: Just show the business concept node as a single representative
                mermaid_id = f"Op_{node_counter}"
                node_ids[context_id] = mermaid_id
                if concept_node.lineage_id:
                    lineage_to_mermaid[concept_node.lineage_id] = mermaid_id
                node_counter += 1

                node_shape = self._get_node_shape(concept_node)
                lines.append(f'{indent} {mermaid_id}{node_shape}')

            lines.append(f'{indent}end')
            lines.append("")

        # Render all root concepts (and their children recursively)
        for root_id in root_concepts:
            render_concept_subgraph(root_id)

        # Handle any orphaned operations (not in any business concept)
        orphaned_operations = []
        for node_id, node in operation_nodes.items():
            context_id = node.context_id or node.metadata.get('context_id')
            # Check if this context_id belongs to a business concept
            # Operation is orphaned if it has no context OR if its context is not a business concept
            if not context_id or context_id not in concept_hierarchy:
                # Check if already added to node_ids
                if node_id not in node_ids:
                    orphaned_operations.append(node)

        # DEBUG: Log orphaned operations
        logger.info(f"Found {len(orphaned_operations)} orphaned operations")
        for node in orphaned_operations:
            logger.info(f"  Orphaned: {node.node_id}, type={node.metadata.get('operation_type')}, context_id={node.context_id}")

        # Export full graph structure to JSON for debugging
        import json
        debug_data = {
            'total_nodes': len(enhanced_graph.nodes),
            'total_edges': len(enhanced_graph.edges),
            'operation_nodes_count': len(operation_nodes),
            'business_concept_nodes_count': len(business_concept_nodes),
            'source_nodes_count': len(source_nodes),
            'orphaned_operations_count': len(orphaned_operations),
            'orphaned_operations': [
                {
                    'node_id': node.node_id,
                    'operation_type': node.metadata.get('operation_type'),
                    'context_id': node.context_id,
                    'lineage_id': str(getattr(node, 'lineage_id', 'N/A'))
                }
                for node in orphaned_operations
            ],
            'all_nodes': [
                {
                    'node_id': node_id,
                    'operation_type': node.metadata.get('operation_type'),
                    'operation_name': node.metadata.get('operation_name'),
                    'context_id': getattr(node, 'context_id', None),
                    'lineage_id': str(getattr(node, 'lineage_id', 'N/A'))
                }
                for node_id, node in enhanced_graph.nodes.items()
            ],
            'edges': [
                {
                    'source_id': edge.source_id,
                    'target_id': edge.target_id,
                    'edge_type': edge.edge_type
                }
                for edge in enhanced_graph.edges
            ]
        }

        # Write to JSON file
        import os

        from ..utils.path_utils import get_project_root
        debug_file = os.path.join(get_project_root(), 'outputs', 'lineage_debug_output.json')
        os.makedirs(os.path.dirname(debug_file), exist_ok=True)
        with open(debug_file, 'w') as f:
            json.dump(debug_data, f, indent=2)
        logger.info(f"DEBUG: Exported graph structure to {debug_file}")

        # Add diagnostic comment to diagram
        if orphaned_operations:
            lines.append(f"%% DEBUG: Found {len(orphaned_operations)} orphaned operations")
            for node in orphaned_operations[:5]:  # Show first 5
                lines.append(f"%%   - {node.node_id}: {node.metadata.get('operation_type')}")
            lines.append("")

        # Render orphaned operations at root level (without subgraph)
        if orphaned_operations:
            for node in orphaned_operations:
                mermaid_id = f"Op_{node_counter}"
                node_ids[node.node_id] = mermaid_id
                if node.lineage_id:
                    lineage_to_mermaid[node.lineage_id] = mermaid_id
                node_counter += 1

                node_shape = self._get_node_shape(node)
                lines.append(f'  {mermaid_id}{node_shape}')

            lines.append("")

        # Close container subgraph
        lines.append(" end")
        lines.append("")

        # Add edges
        lines.append("")

        # Build a mapping from compressed operations to their compressed node
        op_to_compressed = {}  # Maps operation_id -> compressed_node_id
        lineage_to_compressed = {}  # Maps lineage_id -> compressed_node_id
        if hasattr(self, '_compression_sequences'):
            for seq_id, seq in self._compression_sequences.items():
                # Map each compressed operation to its compressed node
                for op_id in seq.operations:
                    op_to_compressed[op_id] = seq_id
                    # Also map the lineage_id to compressed node (edges use lineage_id)
                    if op_id in enhanced_graph.nodes:
                        op_node = enhanced_graph.nodes[op_id]
                        if hasattr(op_node, 'lineage_id') and op_node.lineage_id:
                            lineage_to_compressed[op_node.lineage_id] = seq_id

        # For COMPLETE/IMPACTING showing individual operations, use operation-level edges
        # For MINIMAL showing business concepts, use concept-level edges
        if self.operation_filter != "none":
            # Show operation-level edges from the graph
            edges_added = set()  # Track added edges to avoid duplicates
            for edge in enhanced_graph.edges:
                # Check if source or target was compressed, and redirect to compressed node
                source_id = edge.source_id
                target_id = edge.target_id

                # If source is compressed, redirect to its compressed node
                # Edges use lineage_id format, so check lineage_to_compressed first
                if source_id in lineage_to_compressed:
                    source_id = lineage_to_compressed[source_id]
                elif source_id in op_to_compressed:
                    source_id = op_to_compressed[source_id]

                # If target is compressed, redirect to its compressed node
                if target_id in lineage_to_compressed:
                    target_id = lineage_to_compressed[target_id]
                elif target_id in op_to_compressed:
                    target_id = op_to_compressed[target_id]

                # Now look up the Mermaid IDs
                source_mermaid_id = lineage_to_mermaid.get(source_id) or node_ids.get(source_id)
                target_mermaid_id = lineage_to_mermaid.get(target_id) or node_ids.get(target_id)

                # Skip if either endpoint is not found
                if not source_mermaid_id or not target_mermaid_id:
                    continue

                # Skip if this is a self-loop (can happen after compression redirection)
                if source_mermaid_id == target_mermaid_id:
                    continue

                # Skip if we've already added this edge
                edge_str = f"{source_mermaid_id}_{target_mermaid_id}"
                if edge_str in edges_added:
                    continue
                edges_added.add(edge_str)

                # Add the edge
                is_fork = edge.metadata.get('is_fork', False) if edge.metadata else False
                if is_fork:
                    lines.append(f" {source_mermaid_id} ==> {target_mermaid_id}")
                else:
                    lines.append(f" {source_mermaid_id} --> {target_mermaid_id}")
        else:
            # MINIMAL: Use business concept level edges
            business_concept_edges = self._derive_business_concept_edges(enhanced_graph, business_concept_nodes)

            for edge_info in business_concept_edges:
                source_mermaid_id = node_ids.get(edge_info['source'])
                target_mermaid_id = node_ids.get(edge_info['target'])

                if source_mermaid_id and target_mermaid_id:
                    if edge_info['is_fork']:
                        lines.append(f" {source_mermaid_id} ==> {target_mermaid_id}")
                    else:
                        lines.append(f" {source_mermaid_id} --> {target_mermaid_id}")

        # Add node class assignments
        lines.append("")
        for node_id, node in enhanced_graph.nodes.items():
            mermaid_id = node_ids.get(node_id) or lineage_to_mermaid.get(node.lineage_id if hasattr(node, 'lineage_id') else None)
            if mermaid_id:
                node_class = self._get_node_class(node)
                lines.append(f" class {mermaid_id} {node_class}")

        # Add class assignments for compressed nodes
        if hasattr(self, '_compression_sequences'):
            for seq_id in self._compression_sequences.keys():
                mermaid_id = node_ids.get(seq_id)
                if mermaid_id:
                    lines.append(f" class {mermaid_id} compressedOp")

        # Add CSS class definitions from centralized styles
        lines.append("")
        lines.append(generate_mermaid_style_classes())

        # Store lineage_to_mermaid mapping for external access (e.g., connecting analyzer nodes)
        self._lineage_to_mermaid = lineage_to_mermaid

        return "\n".join(lines)

    def _derive_business_concept_edges(self, enhanced_graph: EnhancedLineageGraph, business_concepts: dict) -> list:
        """
        Derive business concept level edges from operational edges.
        This creates the high-level flow between business concepts.
        """
        # Create mapping from lineage_id to context_id (business concept)
        # Edges use lineage_id format (lid_*), so we need to map lineage_id -> context_id
        lineage_to_context = {}

        # Map source nodes by their lineage_id
        for node_id, node in enhanced_graph.nodes.items():
            if node.metadata.get('operation_type') == 'source':
                lineage_to_context[node.lineage_id] = node_id  # Source nodes map to their node_id

        # Map operation nodes by their lineage_id to their business concept context_id
        for node_id, node in enhanced_graph.nodes.items():
            # Try to get context_id from node attribute, fallback to metadata
            context_id = node.context_id or node.metadata.get('context_id')
            if context_id and context_id in business_concepts:
                lineage_to_context[node.lineage_id] = context_id

        # WORKAROUND: If operation nodes don't have context_id set, try to infer from
        # business concept input_lineage_ids (which track what lineages fed into each concept)
        for ctx_id, bc_data in business_concepts.items():
            bc_node = bc_data['node']
            input_lids = bc_node.metadata.get('input_lineage_ids', [])
            for lid in input_lids:
                # Map this input lineage to the business concept
                if lid not in lineage_to_context:  # Don't override existing mappings
                    lineage_to_context[lid] = ctx_id

        # Map business concept nodes by their lineage_id to their node_id (context_id)
        # NOTE: Business concept nodes may not have lineage_ids since they're organizational,
        # not actual data transformations. Only map if lineage_id exists.
        for context_id in business_concepts.keys():
            concept_node = business_concepts[context_id]['node']
            if concept_node.lineage_id:
                lineage_to_context[concept_node.lineage_id] = context_id

        # Track unique business concept connections
        concept_connections = set()

        # Analyze all operational edges to find business concept connections
        for edge in enhanced_graph.edges:
            source_context = lineage_to_context.get(edge.source_id)
            target_context = lineage_to_context.get(edge.target_id)

            if source_context and target_context and source_context != target_context:
                # This edge crosses business concept boundaries
                connection_key = (source_context, target_context)
                if connection_key not in concept_connections:
                    concept_connections.add(connection_key)

        # Convert connection set to edge list with fork detection
        business_concept_edges = []
        for source_context, target_context in concept_connections:
            # Determine if this is a fork edge by checking if the source is a fork point
            is_fork = False
            for edge in enhanced_graph.edges:
                if (lineage_to_context.get(edge.source_id) == source_context and
                    lineage_to_context.get(edge.target_id) == target_context and
                    edge.source_id in enhanced_graph.fork_points):
                    is_fork = True
                    break

            business_concept_edges.append({
                'source': source_context,
                'target': target_context,
                'is_fork': is_fork
            })

        return business_concept_edges

    def _create_detailed_operation_label(self, node) -> str:
        """Create detailed operation label matching the expected format."""
        operation_type = node.metadata.get('operation_type', 'operation')

        # Handle compressed nodes specially
        if operation_type == 'compressed':
            operation_name = node.metadata.get('operation_name', 'Operations')
            return operation_name  # Simple label showing just the count

        # Get operation details
        operation_name = self._get_operation_display_name(node, operation_type)
        operation_description = self._get_operation_description(node, operation_type)

        # Build the multi-line label with horizontal separators
        lines = []

        # Line 1: Operation name (bold)
        lines.append(f"**{operation_name}**")

        # Horizontal separator after operation name
        lines.append("<hr/>")

        # Get metrics and timing upfront (outside conditional)
        metrics_lines = self._get_metrics_lines(node)
        timing_line = self._get_timing_line(node)

        # Line 3: Operation description (underlined)
        if operation_description:
            lines.append(f"<u>{operation_description}</u>")

            # Add horizontal separator after description if we have metrics or timing
            if metrics_lines or timing_line:
                lines.append("<hr/>")

        # Add metrics if available
        if metrics_lines:
            lines.extend(metrics_lines)

        # Add timing if available
        if timing_line:
            lines.append(timing_line)

        return "<br/>".join(lines)

    def _get_operation_display_name(self, node, operation_type: str) -> str:
        """Get display name for the operation."""
        # Default operation names based on type
        type_names = {
            'source': 'Load Source Data',
            'filter': 'Filtering',
            'transform': 'Transform Operation',
            'join': 'Join Operation',
            'union': 'Union Operation',
            'group': 'Group By',
            'groupby': 'Group By',
            'aggregate': 'Aggregate Operation',
            'select': 'Column Selection',
            'sort': 'Sort Operation'
        }

        # Try to get specific name from metadata or use default
        specific_name = node.metadata.get('operation_name')
        if specific_name:
            return specific_name

        # For SOURCE operations, extract business label from node_id pattern
        if operation_type == 'source':
            node_id = node.node_id
            if node_id and node_id.startswith("source_"):
                business_label = node_id.replace("source_", "", 1)
                return business_label

        # Check if this is a reassignment (variable modification)
        if operation_type == 'transform' and node.metadata.get('is_reassignment'):
            return 'Variable Reassignment'

        return type_names.get(operation_type, f"{operation_type.title()} Operation")

    def _get_operation_description(self, node, operation_type: str) -> str:
        """Get operation description for the label."""
        # Check for explicit description in metadata
        if 'description' in node.metadata:
            return node.metadata['description']

        # Check for transformation details (columns added/modified)
        if operation_type == 'transform':
            # Prioritize showing columns added/modified over raw transformation code

            # First try to extract column name from transformation metadata
            transformation = node.metadata.get('transformation', '')
            transformation_type = node.metadata.get('transformation_type', '')

            # Extract column name from transformation (e.g., "base_rate = ..." -> "base_rate")
            column_name = None
            if transformation and '=' in transformation:
                column_name = transformation.split('=')[0].strip()

            # Check transformation_type first
            if transformation_type == 'creation' and column_name:
                return f"Created: {column_name}"
            elif transformation_type == 'modification' and column_name:
                return f"Modified: {column_name}"

            # Check for columns added
            if 'columns_added' in node.metadata:
                cols = node.metadata['columns_added']
                if isinstance(cols, list) and cols:
                    col_str = ", ".join(cols[:3])
                    if len(cols) > 3:
                        col_str += f" +{len(cols) - 3} more"
                    return f"Created: {col_str}"
                elif cols:
                    return f"Created: {cols}"

            # Check for columns modified
            if 'columns_modified' in node.metadata:
                cols = node.metadata['columns_modified']
                if isinstance(cols, list) and cols:
                    col_str = ", ".join(cols[:3])
                    if len(cols) > 3:
                        col_str += f" +{len(cols) - 3} more"
                    return f"Modified: {col_str}"
                elif cols:
                    return f"Modified: {cols}"

            # Fall back to showing transformation expression only if no column info
            if transformation:
                # If this is a reassignment, show what's being replaced
                if node.metadata.get('is_reassignment') and node.metadata.get('previous_transformation'):
                    prev_trans = node.metadata['previous_transformation']
                    # Truncate if needed
                    if len(prev_trans) > 40:
                        prev_trans = prev_trans[:37] + "..."
                    if len(transformation) > 40:
                        transformation = transformation[:37] + "..."
                    return f"{transformation}<br/>↻ Replaces: {prev_trans}"

                # Truncate long transformations
                if len(transformation) > 80:
                    transformation = transformation[:77] + "..."
                return transformation

        # Check for filter conditions
        if operation_type == 'filter' and 'filter_condition' in node.metadata:
            condition = node.metadata['filter_condition']
            # Remove Column<'...'> encapsulation for cleaner display
            condition = condition.replace("Column<'", "").replace("'>", "")
            condition = condition.replace("Column<b'", "").replace("'>", "")
            return f"Filter: {condition}"

        # Check for join information
        if operation_type == 'join':
            parts = []

            # Add join type
            if 'join_type' in node.metadata:
                parts.append(f"{node.metadata['join_type'].upper()} join")
            else:
                parts.append("Join")

            # Add join keys
            if 'join_keys' in node.metadata:
                keys = node.metadata['join_keys']
                if isinstance(keys, list):
                    key_str = ", ".join(keys[:3])  # Show first 3 keys
                    if len(keys) > 3:
                        key_str += "..."
                else:
                    key_str = str(keys)
                parts.append(f"on {key_str}")

            # Add column count changes (input columns -> output columns)
            if 'input_column_count' in node.metadata and 'output_column_count' in node.metadata:
                input_cols = node.metadata['input_column_count']
                output_cols = node.metadata['output_column_count']
                col_change = output_cols - input_cols
                col_change_str = f" ({col_change:+})" if col_change != 0 else ""
                parts.append(f"<br/>Columns: {input_cols} -> {output_cols}{col_change_str}")

            return "<br/>".join(parts) if len(parts) > 1 else (" ".join(parts) if parts else "Join operation")

        # Check for group by columns
        if operation_type in ['group', 'groupby'] and 'group_columns' in node.metadata:
            lines = []

            # Group by columns
            cols = node.metadata['group_columns']
            if isinstance(cols, list):
                col_str = ", ".join(cols[:3])
                if len(cols) > 3:
                    col_str += "..."
            else:
                col_str = str(cols)
            lines.append(f"Group by: {col_str}")

            # Add aggregation operations if available
            agg_functions = node.metadata.get('aggregation_functions', [])
            if agg_functions:
                # Clean and format aggregation functions
                agg_list = []
                for agg_info in agg_functions:
                    func_name = agg_info.get('function', '')
                    col_name = agg_info.get('column', '')
                    alias = agg_info.get('alias', '')

                    # Clean up function names (remove "Column<'" prefix if present)
                    if func_name:
                        func_name = func_name.replace("Column<'", "").replace("'", "").strip()
                    if col_name:
                        col_name = col_name.replace("Column<'", "").replace("'", "").strip()

                    if func_name and col_name:
                        if alias:
                            agg_list.append(f"{func_name}({col_name}) as {alias}")
                        else:
                            agg_list.append(f"{func_name}({col_name})")

                if agg_list:
                    # Show up to 3 aggregations
                    if len(agg_list) <= 3:
                        agg_str = ', '.join(agg_list)
                        lines.append(f"Aggregations: {agg_str}")
                    else:
                        agg_str = ', '.join(agg_list[:3])
                        remaining = len(agg_list) - 3
                        lines.append(f"Aggregations: {agg_str} (+{remaining} more)")

            return "<br/>".join(lines)

        # Check for select/drop operations
        if operation_type == 'select':
            # Show column count changes if available
            input_cols = node.metadata.get('input_column_count')
            output_cols = node.metadata.get('output_column_count')

            if input_cols is not None and output_cols is not None:
                return f"Columns: {input_cols} -> {output_cols}"
            elif output_cols is not None:
                return f"Columns: {output_cols}"

            # Fall back to showing dropped/selected columns if no counts
            if 'columns_dropped' in node.metadata:
                cols = node.metadata['columns_dropped']
                if isinstance(cols, list) and cols:
                    col_str = ", ".join(cols[:3])
                    if len(cols) > 3:
                        col_str += f" +{len(cols) - 3} more"
                    return f"Drop: {col_str}"
            if 'columns_selected' in node.metadata:
                cols = node.metadata['columns_selected']
                if isinstance(cols, list) and cols:
                    col_str = ", ".join(cols[:3])
                    if len(cols) > 3:
                        col_str += f" +{len(cols) - 3} more"
                    return f"Select: {col_str}"

        # Default descriptions
        type_descriptions = {
            'source': 'Loading data from source',
            'filter': 'Applying filter conditions',
            'transform': 'Data transformation',
            'union': 'Combining datasets',
        }

        return type_descriptions.get(operation_type, "")

    def _get_metrics_lines(self, node) -> List[str]:
        """Get metrics lines for the operation label."""
        lines = []

        operation_type = node.metadata.get('operation_type', 'unknown')

        # Try to get metrics from metadata.metrics first
        metrics = node.metadata.get('metrics', {})

        # Also check for before_metrics and after_metrics (used by enhanced graph)
        before_metrics = node.metadata.get('before_metrics', {})
        after_metrics = node.metadata.get('after_metrics', {})

        # Record counts with changes
        input_count = None
        output_count = None

        # Try metadata.metrics first
        if metrics:
            input_count = metrics.get('input_record_count')
            output_count = metrics.get('output_record_count', metrics.get('row_count'))

        # Fall back to before/after metrics
        if input_count is None and before_metrics:
            if isinstance(before_metrics, dict):
                input_count = before_metrics.get('row_count')
            else:
                input_count = getattr(before_metrics, 'row_count', None)

        if output_count is None and after_metrics:
            if isinstance(after_metrics, dict):
                output_count = after_metrics.get('row_count')
            else:
                output_count = getattr(after_metrics, 'row_count', None)

        # Display record counts based on operation type
        if operation_type == 'source':
            # Source nodes only show the initial row count
            if output_count is not None:
                lines.append(f"Records: {output_count:,}")
        else:
            # All other nodes show input -> output with change if available
            if input_count is not None and output_count is not None:
                change = output_count - input_count
                change_str = f" ({change:+,})" if change != 0 else ""
                lines.append(f"Records: {input_count:,} -> {output_count:,}{change_str}")
            elif output_count is not None:
                lines.append(f"Records: {output_count:,}")

        # Column distinct counts - only show for operations that impact record counts
        # Filter: reduces records based on conditions
        # Union: combines datasets (affects distinct counts)
        # Join: combines datasets based on keys
        # Transform operations do NOT impact record counts, so we don't show distinct counts
        show_distinct_counts = operation_type in ['filter', 'union', 'join']

        if show_distinct_counts:
            # Get from before/after metrics
            before_distinct = {}
            after_distinct = {}

            if before_metrics:
                if isinstance(before_metrics, dict):
                    before_distinct = before_metrics.get('distinct_counts', {})
                else:
                    before_distinct = getattr(before_metrics, 'distinct_counts', {})

            if after_metrics:
                if isinstance(after_metrics, dict):
                    after_distinct = after_metrics.get('distinct_counts', {})
                else:
                    after_distinct = getattr(after_metrics, 'distinct_counts', {})

            # Combine before and after distinct counts
            all_tracked_cols = set(before_distinct.keys()) | set(after_distinct.keys())
            if all_tracked_cols:
                for col_name in sorted(all_tracked_cols)[:3]:  # Limit to 3 columns
                    before_count = before_distinct.get(col_name)
                    after_count = after_distinct.get(col_name)

                    if before_count is not None and after_count is not None:
                        change = after_count - before_count
                        change_str = f" ({change:+})" if change != 0 else ""
                        lines.append(f"{col_name}: {before_count} -> {after_count}{change_str} distinct")
                    elif after_count is not None:
                        lines.append(f"{col_name}: {after_count} distinct")
                    elif before_count is not None:
                        lines.append(f"{col_name}: {before_count} distinct")
            elif metrics:
                # Fall back to metadata.metrics.distinct_counts if before/after not available
                distinct_counts = metrics.get('distinct_counts', {})
                if distinct_counts:
                    for col_name, count in list(distinct_counts.items())[:3]:  # Show first 3 columns
                        if isinstance(count, dict):
                            input_distinct = count.get('input', count.get('input_distinct', 0))
                            output_distinct = count.get('output', count.get('output_distinct', count.get('distinct', 0)))
                            if input_distinct and output_distinct:
                                change = output_distinct - input_distinct
                                change_str = f" ({change:+})" if change != 0 else ""
                                lines.append(f"{col_name}: {input_distinct} -> {output_distinct}{change_str} distinct")
                            elif output_distinct:
                                lines.append(f"{col_name}: {output_distinct} distinct")
                        else:
                            lines.append(f"{col_name}: {count} distinct")

        return lines

    def _get_timing_line(self, node) -> str:
        """Get timing information for the operation."""
        # Check for timing in metadata
        duration = node.metadata.get('duration') or node.metadata.get('computation_time')

        if duration:
            if duration < 1:
                return f" {duration:.3f}s"
            else:
                return f" {duration:.2f}s"

        return ""

    def _get_node_shape(self, node) -> str:
        """Get Mermaid node shape based on operation type using centralized styles."""
        operation_type = node.metadata.get('operation_type', 'default')

        # Create the full node definition with label
        label = self._create_detailed_operation_label(node)

        # Properly escape the label for Mermaid
        escaped_label = self._escape_mermaid_label(label)

        # Get shape template from centralized styles
        template = get_mermaid_shape_template(operation_type)

        # Replace {content} placeholder with escaped label
        return template.replace('{content}', escaped_label)

    def _escape_mermaid_label(self, label: str) -> str:
        """Properly escape a label for Mermaid diagram compatibility."""
        # Replace problematic characters for Mermaid
        escaped = label.replace('"', "'")  # Replace double quotes with single quotes
        escaped = escaped.replace('\\', '/')  # Replace backslashes
        escaped = escaped.replace('\n', '<br/>')  # Replace newlines with HTML breaks

        # Handle HTML-like tags properly - keep them as is for Mermaid HTML rendering
        # Mermaid supports HTML in labels when properly formatted

        return escaped

    def _get_node_class(self, node) -> str:
        """
        Get CSS class for node based on operation type and governance metadata.

        Priority order for governance styling:
        1. Direct customer impact (highest priority)
        2. Critical/high risk level
        3. Indirect customer impact
        4. Approved with governance
        5. Default operation type styling
        """
        operation_type = node.metadata.get('operation_type', 'default')
        base_class = get_node_class_name(operation_type)

        # Check for governance metadata on this node
        governance_metadata = node.metadata.get('governance_metadata')

        # If no governance metadata on this node, check if it's part of a business concept
        # by looking for the business_context metadata (which contains parent concept info)
        if not governance_metadata:
            business_context = node.metadata.get('business_context')
            if business_context and isinstance(business_context, dict):
                # Check if the business context has governance metadata
                governance_metadata = business_context.get('governance_metadata')

        if not governance_metadata:
            return base_class

        # Priority 1: Direct customer impact (red border, highest priority)
        impact_level = getattr(governance_metadata, 'customer_impact_level', None)
        if impact_level == 'direct':
            return 'governance_direct_impactOp'

        # Priority 2: Critical or high risk level (orange/red border)
        known_risks = getattr(governance_metadata, 'known_risks', [])
        if known_risks:
            max_severity = 'low'
            for risk in known_risks:
                severity = getattr(risk, 'severity', 'low')
                if severity == 'critical':
                    max_severity = 'critical'
                    break  # Critical is highest, no need to continue
                elif severity == 'high' and max_severity != 'critical':
                    max_severity = 'high'
                elif severity == 'medium' and max_severity not in ['critical', 'high']:
                    max_severity = 'medium'

            if max_severity == 'critical':
                return 'governance_risk_criticalOp'
            elif max_severity == 'high':
                return 'governance_risk_highOp'
            elif max_severity == 'medium' and impact_level != 'indirect':
                # Only show medium risk if not already showing indirect impact
                return 'governance_risk_mediumOp'

        # Priority 3: Indirect customer impact (yellow border)
        if impact_level == 'indirect':
            return 'governance_indirect_impactOp'

        # Priority 4: Approved with governance (green border)
        approval_status = getattr(governance_metadata, 'approval_status', None)
        if approval_status == 'approved':
            return 'governance_approvedOp'

        # Default: Use operation type styling
        return base_class

    def _format_subgraph_label_with_risk(self, label: str, node) -> str:
        """
        Format subgraph label with risk indicator based on governance metadata
        and metrics (row counts) if available.

        Args:
            label: Original subgraph label
            node: Node containing governance metadata and output_metrics

        Returns:
            Formatted label with risk indicator emoji and metrics
        """
        # Start with the base label
        formatted_label = label

        # Don't add metrics to subgraph labels - they should be at the node level
        # Check for governance metadata
        governance_metadata = node.metadata.get('governance_metadata')

        if not governance_metadata:
            return formatted_label

        # Determine risk level (same logic as _get_node_class)
        impact_level = getattr(governance_metadata, 'customer_impact_level', None)
        known_risks = getattr(governance_metadata, 'known_risks', [])
        approval_status = getattr(governance_metadata, 'approval_status', None)

        # Priority 1: Direct customer impact (highest priority)
        if impact_level == 'direct':
            return f"[RED] {formatted_label}"

        # Priority 2: Critical or high risk level
        if known_risks:
            max_severity = 'low'
            for risk in known_risks:
                severity = getattr(risk, 'severity', 'low')
                if severity == 'critical':
                    max_severity = 'critical'
                    break
                elif severity == 'high' and max_severity != 'critical':
                    max_severity = 'high'
                elif severity == 'medium' and max_severity not in ['critical', 'high']:
                    max_severity = 'medium'

            if max_severity == 'critical':
                return f"[RED] {formatted_label}"
            elif max_severity == 'high':
                return f"[ORANGE] {formatted_label}"
            elif max_severity == 'medium':
                return f"[YELLOW] {formatted_label}"

        # Priority 3: Indirect customer impact
        if impact_level == 'indirect':
            return f"[YELLOW] {formatted_label}"

        # Priority 4: Approved with governance
        if approval_status == 'approved':
            return f"[GREEN] {formatted_label}"

        # Default: Return formatted label with metrics
        return formatted_label

    def _extract_business_concepts(self, lineage_graph: LineageGraph) -> List[BusinessConceptGroup]:
        """Extract business concepts and group their operations."""
        concepts = []

        # Find all business concept nodes and sort them by creation time
        business_concept_nodes = []
        all_operation_nodes = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, BusinessConceptNode):
                business_concept_nodes.append(node)
            elif isinstance(node, OperationNode):
                all_operation_nodes.append(node)

        # Sort by created_at timestamp to ensure proper execution order
        business_concept_nodes.sort(key=lambda x: getattr(x, 'created_at', 0))

        # Track which operations are already part of business concepts
        operations_in_concepts = set()

        for node in business_concept_nodes:
            # Get operations stored directly in the business concept node
            concept_operation_ids = []

            # Operations are stored as technical_operations within the BusinessConceptNode
            if hasattr(node, 'technical_operations') and node.technical_operations:
                concept_operation_ids = [op.node_id for op in node.technical_operations]
            # Track these operations as belonging to this concept
            operations_in_concepts.update(concept_operation_ids)

            # Extract tracked columns from the business concept node
            tracked_columns = node.track_columns if hasattr(node, 'track_columns') else []

            concepts.append(BusinessConceptGroup(
                concept_id=node.node_id,
                concept_name=node.name,
                concept_description=node.description or "",
                tracked_columns=tracked_columns,
                operations=concept_operation_ids # Store operation IDs for now
            ))

        # Collect raw operations that are NOT part of any business concept
        raw_operation_nodes = [
            op for op in all_operation_nodes
            if op.node_id not in operations_in_concepts
        ]

        # Handle raw operations based on group_raw_operations setting
        if raw_operation_nodes:
            # Sort raw operations by creation time
            raw_operation_nodes.sort(key=lambda x: getattr(x, 'created_at', 0))

            if self.group_raw_operations:
                # Group raw operations by connected components (new smart behavior)
                operation_groups = self._group_operations_by_connectivity(raw_operation_nodes, lineage_graph)

                for group_idx, operation_group in enumerate(operation_groups):
                    if len(operation_groups) == 1:
                        # Single group - use traditional name
                        group_name = "Ungrouped Operations" if concepts else "Data Operations"
                    else:
                        # Multiple groups - distinguish them
                        group_name = f"Operations Group {group_idx + 1}"

                    group_concept = BusinessConceptGroup(
                        concept_id=f"raw_group_{group_idx}",
                        concept_name=group_name,
                        concept_description=f"Connected operations group {group_idx + 1}",
                        tracked_columns=[],
                        operations=[] # Will be populated later
                    )
                    group_concept._raw_operations = operation_group
                    concepts.append(group_concept)
            else:
                # Render raw operations as standalone nodes (new behavior)
                standalone_operations = BusinessConceptGroup(
                    concept_id="_standalone_operations",
                    concept_name="", # Empty name means no subgraph
                    concept_description="Standalone operations",
                    tracked_columns=[],
                    operations=[]
                )
                standalone_operations._raw_operations = raw_operation_nodes
                standalone_operations._is_standalone = True
                concepts.append(standalone_operations)

        return concepts

    def _deduplicate_source_operations(self, business_concepts: List[BusinessConceptGroup], lineage_graph: LineageGraph) -> List[BusinessConceptGroup]:
        """
        Remove duplicate source operations that represent the same underlying data.

        This addresses the issue where both auto-wrapping and explicit DataFrame creation
        create separate SOURCE operations for the same data.
        """
        # Collect all source operations across all concepts
        all_source_ops = []
        source_to_concept = {}

        for concept in business_concepts:
            if hasattr(concept, '_raw_operations'):
                for op in concept._raw_operations:
                    if op.operation_type == OperationType.SOURCE:
                        all_source_ops.append(op)
                        source_to_concept[op.node_id] = concept

        # Group source operations by similarity (same record count and similar names)
        source_groups = []
        processed_sources = set()

        for source_op in all_source_ops:
            if source_op.node_id in processed_sources:
                continue

            # Find similar source operations
            similar_sources = [source_op]
            processed_sources.add(source_op.node_id)

            for other_source in all_source_ops:
                if (other_source.node_id not in processed_sources and
                    self._are_duplicate_sources(source_op, other_source)):
                    similar_sources.append(other_source)
                    processed_sources.add(other_source.node_id)

            # Keep the best representative from each group
            if len(similar_sources) > 1:
                best_source = self._select_best_source_representative(similar_sources)
                source_groups.append([best_source])

                # Remove duplicates from their concepts
                for source in similar_sources:
                    if source != best_source:
                        concept = source_to_concept[source.node_id]
                        if hasattr(concept, '_raw_operations'):
                            concept._raw_operations = [op for op in concept._raw_operations if op.node_id != source.node_id]
            else:
                source_groups.append(similar_sources)

        return business_concepts

    def _are_duplicate_sources(self, source1: OperationNode, source2: OperationNode) -> bool:
        """Check if two source operations represent the same underlying data."""
        # Check if they have the same output record count
        source1_count = source1.after_metrics.row_count if source1.after_metrics else None
        source2_count = source2.after_metrics.row_count if source2.after_metrics else None

        if (source1_count is not None and
            source2_count is not None and
            source1_count == source2_count):

            # Check if names suggest they're the same data (both contain "arg_" or similar patterns)
            name1 = source1.name.lower() if source1.name else ""
            name2 = source2.name.lower() if source2.name else ""

            # If both are auto-wrapped or both reference similar argument positions
            if (("auto-wrapped" in name1 and "auto-wrapped" in name2) or
                ("arg_" in name1 and "arg_" in name2)):
                return True

        return False

    def _select_best_source_representative(self, sources: List[OperationNode]) -> OperationNode:
        """Select the best representative from a group of duplicate sources."""
        # Prefer sources that are NOT auto-wrapped (more descriptive)
        non_auto_wrapped = [s for s in sources if "auto-wrapped" not in s.name.lower()]
        if non_auto_wrapped:
            return non_auto_wrapped[0]

        # Otherwise, just pick the first one
        return sources[0]

    def _group_operations_by_connectivity(self, raw_operations: List[OperationNode], lineage_graph: LineageGraph) -> List[List[OperationNode]]:
        """
        Group raw operations by their connectivity (connected components).

        Operations that are sequentially linked (connected by edges) will be grouped together.
        Unconnected operations will be in separate groups.

        Args:
            raw_operations: List of raw operation nodes to group
            lineage_graph: The lineage graph containing edges

        Returns:
            List of operation groups, where each group contains connected operations
        """
        if not raw_operations:
            return []

        # Build adjacency map for raw operations only
        raw_op_ids = {op.node_id for op in raw_operations}
        adjacency = {op.node_id: set() for op in raw_operations}

        # Add edges between raw operations
        for edge in lineage_graph.edges:
            if edge.source_id in raw_op_ids and edge.target_id in raw_op_ids:
                adjacency[edge.source_id].add(edge.target_id)
                adjacency[edge.target_id].add(edge.source_id) # Treat as undirected for grouping

        # Find connected components using DFS
        visited = set()
        groups = []

        def dfs(node_id: str, current_group: List[str]):
            """Depth-first search to find connected component."""
            if node_id in visited:
                return
            visited.add(node_id)
            current_group.append(node_id)

            for neighbor_id in adjacency[node_id]:
                dfs(neighbor_id, current_group)

        # Find all connected components
        for op in raw_operations:
            if op.node_id not in visited:
                current_group = []
                dfs(op.node_id, current_group)
                if current_group:
                    groups.append(current_group)

        # Convert node IDs back to operation nodes and sort by creation time
        operation_groups = []
        op_map = {op.node_id: op for op in raw_operations}

        for group_ids in groups:
            group_operations = [op_map[op_id] for op_id in group_ids]
            # Sort each group by creation time to maintain execution order
            group_operations.sort(key=lambda x: getattr(x, 'created_at', 0))
            operation_groups.append(group_operations)

        # Sort groups by the earliest operation in each group
        operation_groups.sort(key=lambda group: getattr(group[0], 'created_at', 0) if group else 0)

        return operation_groups

    def _extract_operation_metrics(
        self,
        concept: BusinessConceptGroup,
        lineage_graph: LineageGraph
    ) -> List[OperationMetrics]:
        """Extract detailed metrics for each operation."""
        operations = []

        # Check if this is a default concept with raw operations
        if hasattr(concept, '_raw_operations'):
            # Process raw operations directly
            for op_node in concept._raw_operations:
                metrics = self._build_operation_metrics(op_node)
                if self._should_include_operation(metrics, concept):
                    operations.append(metrics)
            return operations

        # Get the business concept node
        concept_node = lineage_graph.nodes.get(concept.concept_id)
        if isinstance(concept_node, BusinessConceptNode):
            # Get operations directly from the technical_operations list
            if hasattr(concept_node, 'technical_operations') and concept_node.technical_operations:
                # Sort operations by creation time to ensure proper execution order
                sorted_operations = sorted(
                    concept_node.technical_operations,
                    key=lambda x: getattr(x, 'created_at', 0)
                )
                for op_node in sorted_operations:
                    metrics = self._build_operation_metrics(op_node)

                    # Apply operation filtering
                    if not self._should_include_operation(metrics, concept_node):
                        continue

                    operations.append(metrics)

        # Operations are already sorted by creation time, no need to re-sort

        return operations

    def _should_include_operation(self, operation: OperationMetrics, concept_node) -> bool:
        """Determine if an operation should be included based on the filter settings."""

        # Check if this is a passthrough operation (delegated method)
        is_passthrough = getattr(operation, 'metadata', {}).get('delegated', False)

        # Also check for passthrough-like operations by name patterns
        passthrough_patterns = ['customer identity select', 'identity select', 'passthrough']
        is_passthrough_by_name = any(pattern in operation.operation_name.lower() for pattern in passthrough_patterns)

        # Filter out passthrough operations if show_passthrough_operations is False
        if (is_passthrough or is_passthrough_by_name) and not self.show_passthrough_operations:
            logger.debug(f"Excluding passthrough operation: {operation.operation_name}")
            return False

        # Handle different filter types
        if self.operation_filter == "all":
            return True
        elif self.operation_filter == "impacting":
            return self._operation_impacts_tracked_columns(operation, concept_node)
        elif isinstance(self.operation_filter, list):
            # Filter by specific operation types
            return operation.operation_type in self.operation_filter
        else:
            # Default to showing all operations for unknown filter types
            return True

    def _operation_impacts_tracked_columns(self, operation: OperationMetrics, concept_node) -> bool:
        """Check if an operation impacts tracked columns (record count or distinct counts)."""
        # Check metadata for impacts_tracked_columns flag (from new standardized tracking)
        if operation.metadata:
            impacts_flag = operation.metadata.get('impacts_tracked_columns')
            if impacts_flag is not None:
                return impacts_flag

        # Fallback to old logic: Always include source, joins, filters, and groupBy as they typically impact data
        if operation.operation_type in [OperationType.SOURCE, OperationType.JOIN, OperationType.FILTER, OperationType.GROUP_BY]:
            return True

        # Check if record count changed
        if (operation.input_record_count is not None and
            operation.output_record_count is not None and
            operation.input_record_count != operation.output_record_count):
            return True

        # Check if any tracked column distinct counts changed
        tracked_columns = getattr(concept_node, 'track_columns', [])
        if tracked_columns:
            for col in tracked_columns:
                input_count = operation.input_column_metrics.get(col)
                output_count = operation.output_column_metrics.get(col)

                if input_count != output_count:
                    return True

        # If no impact detected, exclude this operation
        return False

    def _find_compression_sequences(
        self,
        operations: List[Any],
        concept_node: Any,
        context_id: str
    ) -> Tuple[List[Any], Dict[str, CompressionSequence]]:
        """
        Find sequences of consecutive non-impacting operations and create compression metadata.

        Args:
            operations: List of operation nodes to analyze
            concept_node: The business concept node these operations belong to
            context_id: The context ID for the business concept

        Returns:
            Tuple of (filtered_operations_list, compression_sequences_dict)
            - filtered_operations_list: List of operations to show (impacting + compressed nodes)
            - compression_sequences_dict: Dict mapping compressed node ID to CompressionSequence
        """
        if not operations:
            return [], {}

        # Build list of (operation, is_impacting) tuples
        operation_impacts = []
        for op_node in operations:
            op_metrics = self._build_operation_metrics_from_node(op_node)
            is_impacting = self._operation_impacts_tracked_columns(op_metrics, concept_node)
            operation_impacts.append((op_node, is_impacting))

        # Find sequences of consecutive non-impacting operations
        sequences = {}
        filtered_operations = []
        current_sequence = []
        sequence_counter = 0
        last_visible_node_id = None  # Track the last node added to filtered_operations

        for i, (op_node, is_impacting) in enumerate(operation_impacts):
            if is_impacting:
                # If we have accumulated non-impacting operations, create a compressed node
                if current_sequence:
                    sequence_id = f"compressed_{context_id}_{sequence_counter}"
                    sequence_counter += 1

                    # Source is the last visible node we added (could be impacting op or another compressed node)
                    source_node = last_visible_node_id
                    target_node = op_node.node_id

                    # Create compression sequence metadata
                    sequence = CompressionSequence(
                        sequence_id=sequence_id,
                        operations=[op.node_id for op, _ in current_sequence],
                        operation_types=[op.metadata.get('operation_type', 'custom') for op, _ in current_sequence],
                        source_node=source_node,
                        target_node=target_node,
                        concept_id=context_id
                    )
                    sequences[sequence_id] = sequence

                    # Extract the business concept name to include in the label
                    concept_name = concept_node.metadata.get('operation_name', '') if concept_node else ''

                    # Create a concept-aware label
                    if concept_name:
                        operation_label = f'{concept_name}: {len(current_sequence)} operation{"s" if len(current_sequence) != 1 else ""}'
                    else:
                        operation_label = f'{len(current_sequence)} operation{"s" if len(current_sequence) != 1 else ""}'

                    # Create a synthetic compressed node representation
                    # We'll add this to filtered_operations as a marker
                    compressed_marker = type('obj', (object,), {
                        'node_id': sequence_id,
                        'metadata': {
                            'operation_type': 'compressed',
                            'operation_name': operation_label,
                            'operation_count': len(current_sequence),
                            'compressed_operations': sequence.operations,
                            'is_compressed': True,
                            'concept_name': concept_name
                        },
                        'lineage_id': None,
                        'context_id': context_id
                    })()
                    filtered_operations.append(compressed_marker)
                    last_visible_node_id = sequence_id  # Update last visible node

                    # Reset sequence
                    current_sequence = []

                # Add the impacting operation
                filtered_operations.append(op_node)
                last_visible_node_id = op_node.node_id  # Update last visible node
            else:
                # Accumulate non-impacting operations
                current_sequence.append((op_node, is_impacting))

        # Handle trailing non-impacting operations
        if current_sequence:
            sequence_id = f"compressed_{context_id}_{sequence_counter}"

            # Source is the last visible node we added
            source_node = last_visible_node_id

            sequence = CompressionSequence(
                sequence_id=sequence_id,
                operations=[op.node_id for op, _ in current_sequence],
                operation_types=[op.metadata.get('operation_type', 'custom') for op, _ in current_sequence],
                source_node=source_node,
                target_node=None,  # Terminal sequence
                concept_id=context_id
            )
            sequences[sequence_id] = sequence

            # Extract the business concept name to include in the label
            concept_name = concept_node.metadata.get('operation_name', '') if concept_node else ''

            # Create a concept-aware label
            if concept_name:
                operation_label = f'{concept_name}: {len(current_sequence)} operation{"s" if len(current_sequence) != 1 else ""}'
            else:
                operation_label = f'{len(current_sequence)} operation{"s" if len(current_sequence) != 1 else ""}'

            # Create compressed marker
            compressed_marker = type('obj', (object,), {
                'node_id': sequence_id,
                'metadata': {
                    'operation_type': 'compressed',
                    'operation_name': operation_label,
                    'operation_count': len(current_sequence),
                    'compressed_operations': sequence.operations,
                    'is_compressed': True,
                    'concept_name': concept_name
                },
                'lineage_id': None,
                'context_id': context_id
            })()
            filtered_operations.append(compressed_marker)

        return filtered_operations, sequences

    def _build_operation_metrics_from_node(self, node) -> OperationMetrics:
        """
        Build OperationMetrics from an EnhancedLineageGraph node.

        Args:
            node: Node from EnhancedLineageGraph

        Returns:
            OperationMetrics object
        """
        operation_name = node.metadata.get('operation_name', node.node_id)
        operation_type_str = node.metadata.get('operation_type', 'custom')

        # Convert string to OperationType enum
        try:
            operation_type = OperationType(operation_type_str)
        except (ValueError, KeyError):
            operation_type = OperationType.CUSTOM

        metrics = OperationMetrics(
            operation_id=node.node_id,
            operation_name=operation_name,
            operation_type=operation_type
        )

        # Store metadata for filtering logic
        metrics.metadata = node.metadata

        # Extract business label from source node_id pattern for SOURCE operations
        if operation_type == OperationType.SOURCE:
            # Source nodes have business label embedded in node_id as "source_{label}"
            if node.node_id.startswith("source_"):
                business_label = node.node_id.replace("source_", "", 1)
                metrics.business_label = business_label
                # Update operation name to use the business label
                metrics.operation_name = business_label

        # Extract column counts for SELECT operations
        if operation_type == OperationType.SELECT:
            input_cols = node.metadata.get('input_column_count')
            output_cols = node.metadata.get('output_column_count')
            if input_cols is not None:
                metrics.input_column_count = input_cols
            if output_cols is not None:
                metrics.output_column_count = output_cols

        # Extract group_by columns if available
        if operation_type == OperationType.GROUP_BY:
            group_columns = node.metadata.get('group_columns', [])
            metrics.group_by_columns = group_columns

            # Extract aggregation functions
            agg_functions = node.metadata.get('aggregation_functions', [])
            if agg_functions:
                # Convert aggregation function metadata to readable strings
                agg_list = []
                for agg_info in agg_functions:
                    func_name = agg_info.get('function', '')
                    col_name = agg_info.get('column', '')
                    alias = agg_info.get('alias', '')

                    # Clean up function names (remove "Column<'" prefix if present)
                    if func_name:
                        func_name = func_name.replace("Column<'", "").replace("'", "").strip()
                    if col_name:
                        col_name = col_name.replace("Column<'", "").replace("'", "").strip()

                    if func_name and col_name:
                        if alias:
                            agg_list.append(f"{func_name}({col_name}) as {alias}")
                        else:
                            agg_list.append(f"{func_name}({col_name})")

                metrics.aggregations = agg_list

        # Extract metrics if available
        node_metrics = node.metadata.get('metrics', {})
        if node_metrics:
            metrics.input_record_count = node_metrics.get('input_record_count')
            metrics.output_record_count = node_metrics.get('output_record_count')

            # Extract distinct counts
            distinct_counts = node_metrics.get('distinct_counts', {})
            if distinct_counts:
                input_distinct = {}
                output_distinct = {}
                for col, counts in distinct_counts.items():
                    if isinstance(counts, dict):
                        input_distinct[col] = counts.get('input')
                        output_distinct[col] = counts.get('output')
                    else:
                        # Assume it's output count
                        output_distinct[col] = counts

                metrics.input_column_metrics = input_distinct
                metrics.output_column_metrics = output_distinct

        return metrics

    def _build_operation_metrics(self, op_data) -> OperationMetrics:
        """Build detailed metrics for a single operation."""
        # Handle both OperationNode objects and dictionaries
        if isinstance(op_data, dict):
            # Extract from dictionary representation
            operation_id = op_data.get('node_id')
            operation_name = op_data.get('name')
            operation_type_str = op_data.get('operation_type')

            # Convert string back to OperationType enum
            try:
                operation_type = OperationType(operation_type_str)
            except ValueError:
                operation_type = OperationType.CUSTOM

            metadata = op_data.get('metadata', {})
            before_metrics = op_data.get('before_metrics')
            after_metrics = op_data.get('after_metrics')
            execution_time = op_data.get('execution_time')

        else:
            # Handle OperationNode objects
            operation_id = op_data.node_id
            operation_name = op_data.name
            operation_type = op_data.operation_type
            metadata = op_data.metadata or {}
            before_metrics = getattr(op_data, 'before_metrics', None)
            after_metrics = getattr(op_data, 'after_metrics', None)
            execution_time = getattr(op_data, 'execution_time', None)

        metrics = OperationMetrics(
            operation_id=operation_id,
            operation_name=operation_name,
            operation_type=operation_type
        )

        # Store metadata for access by filtering logic
        metrics.metadata = metadata

        # Extract business label from source node_id pattern for SOURCE operations
        if operation_type == OperationType.SOURCE:
            # Source nodes have business label embedded in node_id as "source_{label}"
            if operation_id and operation_id.startswith("source_"):
                business_label = operation_id.replace("source_", "", 1)
                metrics.business_label = business_label
                # Update operation name to use the business label
                metrics.operation_name = business_label

        # Extract column counts for SELECT operations
        if operation_type == OperationType.SELECT:
            input_cols = metadata.get('input_column_count')
            output_cols = metadata.get('output_column_count')
            if input_cols is not None:
                metrics.input_column_count = input_cols
            if output_cols is not None:
                metrics.output_column_count = output_cols

        # Extract record counts from before/after metrics
        if before_metrics:
            if isinstance(before_metrics, dict):
                metrics.input_record_count = before_metrics.get('row_count')
                metrics.input_column_metrics = before_metrics.get('distinct_counts', {})
            else:
                metrics.input_record_count = getattr(before_metrics, 'row_count', None)
                metrics.input_column_metrics = getattr(before_metrics, 'distinct_counts', {})

        if after_metrics:
            if isinstance(after_metrics, dict):
                metrics.output_record_count = after_metrics.get('row_count')
                metrics.output_column_metrics = after_metrics.get('distinct_counts', {})
            else:
                metrics.output_record_count = getattr(after_metrics, 'row_count', None)
                metrics.output_column_metrics = getattr(after_metrics, 'distinct_counts', {})

        # Extract operation-specific details from metadata
        if metadata:
            metrics.filter_condition = metadata.get('filter_condition')
            metrics.join_type = metadata.get('join_type')
            metrics.join_keys = metadata.get('join_keys', [])
            metrics.group_by_columns = metadata.get('group_columns', [])

            # Extract and clean aggregation functions for groupby operations
            if operation_type == OperationType.GROUP_BY:
                agg_functions = metadata.get('aggregation_functions', [])
                if agg_functions:
                    # Convert aggregation function metadata to readable strings
                    agg_list = []
                    for agg_info in agg_functions:
                        func_name = agg_info.get('function', '')
                        col_name = agg_info.get('column', '')
                        alias = agg_info.get('alias', '')

                        # Clean up function names (remove "Column<'" prefix if present)
                        if func_name:
                            func_name = func_name.replace("Column<'", "").replace("'", "").strip()
                        if col_name:
                            col_name = col_name.replace("Column<'", "").replace("'", "").strip()

                        if func_name and col_name:
                            if alias:
                                agg_list.append(f"{func_name}({col_name}) as {alias}")
                            else:
                                agg_list.append(f"{func_name}({col_name})")

                    metrics.aggregations = agg_list
                else:
                    metrics.aggregations = []
            else:
                metrics.aggregations = metadata.get('aggregations', [])

        # For joins, extract additional metrics
        if operation_type == OperationType.JOIN:
            metrics.left_input_count = metadata.get('left_count')
            metrics.right_input_count = metadata.get('right_count')
            metrics.left_unique_keys = metadata.get('left_unique_keys')
            metrics.right_unique_keys = metadata.get('right_unique_keys')
            metrics.matched_keys = metadata.get('matched_keys')

        # Extract execution time
        metrics.execution_time = execution_time

        return metrics

    def _identify_join_points(self, lineage_graph: LineageGraph) -> List[Dict[str, Any]]:
        """Identify join operations that connect different lineages."""
        join_points = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, OperationNode) and node.operation_type == OperationType.JOIN:
                # Find input edges to this join
                input_edges = [
                    edge for edge in lineage_graph.edges
                    if edge.target_id == node.node_id
                ]

                if len(input_edges) >= 2:
                    join_points.append({
                        'operation_id': node.node_id,
                        'left_input': input_edges[0].source_id if input_edges else None,
                        'right_input': input_edges[1].source_id if len(input_edges) > 1 else None,
                        'join_type': node.metadata.get('join_type', 'inner'),
                        'join_keys': node.metadata.get('join_keys', [])
                    })

        return join_points

    def _identify_flow_endpoints(
        self,
        lineage_graph: LineageGraph
    ) -> Tuple[List[str], List[str]]:
        """Identify source and sink operations in the flow."""
        # Operations with no inputs are sources
        sources = []
        # Operations with no outputs are sinks
        sinks = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, OperationNode):
                # Check for inputs
                has_input = any(
                    edge.target_id == node.node_id
                    for edge in lineage_graph.edges
                )

                # Check for outputs
                has_output = any(
                    edge.source_id == node.node_id
                    for edge in lineage_graph.edges
                )

                if not has_input:
                    sources.append(node.node_id)
                if not has_output:
                    sinks.append(node.node_id)

        return sources, sinks

    def _build_operation_node_label(self, operation: OperationMetrics) -> str:
        """Build a multi-line label for an operation node."""
        label_parts = []

        # Operation name
        label_parts.append(operation.operation_name)

        # Add operation-specific details
        if operation.operation_type == OperationType.FILTER and operation.filter_condition:
            condition = self._format_condition(operation.filter_condition)
            label_parts.append(f"Filter: {condition}")

        elif operation.operation_type == OperationType.JOIN:
            join_type = operation.join_type or "inner"
            label_parts.append(f"{join_type.upper()} Join")
            if operation.join_keys:
                label_parts.append(f"Keys: {', '.join(operation.join_keys)}")

        elif operation.operation_type == OperationType.GROUP_BY:
            # Check for group columns in metadata
            group_columns = getattr(operation, 'group_by_columns', None) or operation.metadata.get('group_columns', [])
            if group_columns:
                # Show actual column names instead of just count
                if len(group_columns) <= 3:
                    # Show all columns if 3 or fewer
                    col_names = ', '.join(group_columns)
                    label_parts.append(f"Group by: {col_names}")
                else:
                    # Show first 2 columns + count if more than 3
                    col_names = ', '.join(group_columns[:2])
                    remaining = len(group_columns) - 2
                    label_parts.append(f"Group by: {col_names} (+{remaining} more)")

            # Check for aggregations in metadata
            aggregations = getattr(operation, 'aggregations', None) or operation.metadata.get('aggregation_expressions', [])
            if aggregations:
                # Clean up aggregation display names
                clean_aggs = []
                for agg in aggregations[:2]: # Limit to 2 for brevity
                    # Extract function name from expressions like "sum(amount)"
                    agg_str = str(agg)
                    if '(' in agg_str and ')' in agg_str:
                        # Extract just the function part: "sum(amount)" -> "sum(amount)"
                        clean_aggs.append(agg_str.split('(')[0] + '(...)')
                    else:
                        clean_aggs.append(agg_str)
                label_parts.append(f"Aggs: {', '.join(clean_aggs)}")

        # Add record count summary
        if operation.operation_type == OperationType.SOURCE:
            # For source operations, only show the initial count
            if operation.output_record_count is not None:
                label_parts.append(f"Initial: {operation.output_record_count:,} records")
        elif operation.input_record_count is not None and operation.output_record_count is not None:
            change = operation.record_change or 0
            if change != 0:
                change_str = f"+{change:,}" if change > 0 else f"{change:,}"
                label_parts.append(f"{operation.input_record_count:,} {operation.output_record_count:,} ({change_str})")
            else:
                label_parts.append(f"{operation.output_record_count:,} records")

        # Add tracked column metrics if enabled and available
        if self.show_column_metrics and (operation.input_column_metrics or operation.output_column_metrics):
            # Get all tracked columns from both input and output
            all_columns = set(operation.input_column_metrics.keys()) | set(operation.output_column_metrics.keys())

            # Limit to top tracked columns to avoid overwhelming the label
            tracked_columns = sorted(all_columns)[:3] # Show max 3 columns

            for col_name in tracked_columns:
                input_count = operation.input_column_metrics.get(col_name)
                output_count = operation.output_column_metrics.get(col_name)

                if input_count is not None and output_count is not None:
                    # Show column distinct count change
                    col_change = output_count - input_count
                    if col_change != 0:
                        col_change_str = f"+{col_change:,}" if col_change > 0 else f"{col_change:,}"
                        label_parts.append(f"{col_name}: {input_count:,} {output_count:,} ({col_change_str})")
                    else:
                        label_parts.append(f"{col_name}: {output_count:,} distinct")
                elif output_count is not None:
                    # New column appeared
                    label_parts.append(f"{col_name}: {output_count:,} distinct (new)")
                elif input_count is not None:
                    # Column was removed
                    label_parts.append(f"{col_name}: {input_count:,} removed")

        # Add execution time if available and requested
        if self.show_execution_times and operation.execution_time is not None:
            label_parts.append(f" {operation.execution_time:.3f}s")

        return "<br/>".join(label_parts)

    def _build_simple_node_label(self, operation: OperationMetrics) -> str:
        """Build a simple, single-line label for an operation node."""
        parts = []

        # Operation name (shortened)
        op_name = operation.operation_name
        if len(op_name) > 30:
            op_name = op_name[:27] + "..."
        parts.append(op_name)

        # Add key details based on operation type
        if operation.operation_type == OperationType.FILTER and operation.filter_condition:
            condition = self._format_condition(operation.filter_condition)
            if len(condition) > 20:
                condition = condition[:17] + "..."
            parts.append(f"({condition})")

        elif operation.operation_type == OperationType.JOIN:
            join_type = operation.join_type or "inner"
            parts.append(f"({join_type.upper()})")

        # Add record count if available
        if operation.input_record_count is not None and operation.output_record_count is not None:
            change = operation.record_change or 0
            if change != 0:
                change_str = f"+{change}" if change > 0 else str(change)
                parts.append(f"{operation.input_record_count}{operation.output_record_count} ({change_str})")
            else:
                parts.append(f"{operation.output_record_count} records")

        return " ".join(parts)

    def _build_detailed_node_label(self, operation: OperationMetrics) -> str:
        """Build a detailed label with column metrics for Mermaid diagram."""
        label_parts = []

        # Operation name in bold - use business_label for source operations
        if operation.operation_type == OperationType.SOURCE:
            # Use the business_label attribute we extracted from node_id
            if operation.business_label:
                label_parts.append(f"**{operation.business_label}**")
            else:
                label_parts.append(f"**{operation.operation_name}**")
        else:
            label_parts.append(f"**{operation.operation_name}**")

        # Add horizontal line after title
        label_parts.append("" * 25)

        # Add operation-specific details
        if operation.operation_type == OperationType.SOURCE:
            # For source operations, show loading message
            label_parts.append(f"<u>Loading data from source</u>")

        elif operation.operation_type == OperationType.FILTER and operation.filter_condition:
            condition = self._format_condition(operation.filter_condition)
            # Underline the filter condition
            label_parts.append(f"<u>Filter: {condition}</u>")

        elif operation.operation_type == OperationType.JOIN:
            join_type = operation.join_type or "inner"
            label_parts.append(f"<u>{join_type.upper()} Join</u>")
            if operation.join_keys:
                keys_str = ", ".join(operation.join_keys[:2]) # Limit to 2 keys
                if len(operation.join_keys) > 2:
                    keys_str += "..."
                label_parts.append(f"Keys: {keys_str}")

        elif operation.operation_type == OperationType.GROUP_BY:
            # Check for group columns in metadata or operation attributes
            group_columns = getattr(operation, 'group_by_columns', None) or operation.metadata.get('group_columns', [])
            if group_columns:
                # Show actual column names instead of just count
                if len(group_columns) <= 3:
                    col_names = ', '.join(group_columns)
                    label_parts.append(f"<u>Group by: {col_names}</u>")
                else:
                    # Show first 2 columns + count if more than 3
                    col_names = ', '.join(group_columns[:2])
                    remaining = len(group_columns) - 2
                    label_parts.append(f"<u>Group by: {col_names} (+{remaining} more)</u>")
            else:
                label_parts.append(f"<u>Group by operation</u>")

            # Show aggregation operations if available
            aggregations = getattr(operation, 'aggregations', None) or operation.metadata.get('aggregations', [])
            if aggregations:
                if len(aggregations) <= 3:
                    agg_str = ', '.join(aggregations)
                    label_parts.append(f"Aggregations: {agg_str}")
                else:
                    # Show first 3 aggregations + count
                    agg_str = ', '.join(aggregations[:3])
                    remaining = len(aggregations) - 3
                    label_parts.append(f"Aggregations: {agg_str} (+{remaining} more)")

        elif operation.operation_type == OperationType.SELECT:
            # Show column count changes for select operations
            input_cols = getattr(operation, 'input_column_count', None) or operation.metadata.get('input_column_count')
            output_cols = getattr(operation, 'output_column_count', None) or operation.metadata.get('output_column_count')

            if input_cols is not None and output_cols is not None:
                label_parts.append(f"<u>Columns: {input_cols} -> {output_cols}</u>")
            elif output_cols is not None:
                label_parts.append(f"<u>Columns: {output_cols}</u>")

        elif operation.operation_type == OperationType.TRANSFORM:
            # Show actual method name for transform operations
            method_name = operation.metadata.get('method_name', 'transform')
            if method_name and method_name != 'transform':
                label_parts[0] = f"**{method_name.title()} Operation**"

        # Add horizontal separator before metrics
        label_parts.append("" * 25)

        # Add record count summary
        if operation.operation_type == OperationType.SOURCE:
            # For source operations, only show the initial count (no input output)
            if operation.output_record_count is not None:
                label_parts.append(f"Initial Records: {operation.output_record_count:,}")
        elif operation.input_record_count is not None and operation.output_record_count is not None:
            change = operation.record_change or 0
            if change != 0:
                change_str = f"+{change:,}" if change > 0 else f"{change:,}"
                label_parts.append(f"Records: {operation.input_record_count:,} {operation.output_record_count:,} ({change_str})")
            else:
                label_parts.append(f"Records: {operation.output_record_count:,}")

        # Add tracked column metrics (limit to top 3 for readability)
        if self.show_column_metrics and (operation.input_column_metrics or operation.output_column_metrics):
            all_columns = set(operation.input_column_metrics.keys()) | set(operation.output_column_metrics.keys())
            tracked_columns = sorted(all_columns)[:3] # Limit to 3 columns

            for col_name in tracked_columns:
                input_count = operation.input_column_metrics.get(col_name)
                output_count = operation.output_column_metrics.get(col_name)

                if input_count is not None and output_count is not None:
                    # Show column distinct count change
                    col_change = output_count - input_count
                    if col_change != 0:
                        col_change_str = f"+{col_change:,}" if col_change > 0 else f"{col_change:,}"
                        label_parts.append(f"{col_name}: {input_count:,} {output_count:,} ({col_change_str})")
                    else:
                        label_parts.append(f"{col_name}: {output_count:,} distinct")
                elif output_count is not None:
                    # New column appeared
                    label_parts.append(f"{col_name}: {output_count:,} (new)")
                elif input_count is not None:
                    # Column was removed
                    label_parts.append(f"{col_name}: {input_count:,} removed")

        # Add execution time if requested
        if self.show_execution_times and operation.execution_time is not None:
            label_parts.append(f" {operation.execution_time:.3f}s")

        # Join with HTML line breaks for Mermaid
        return "<br/>".join(label_parts)

    def _format_condition(self, condition: str) -> str:
        """Format a filter condition for display."""
        if not condition:
            return "unknown"

        # Clean up PySpark artifacts
        condition = condition.replace("Column<'", "").replace("'>", "")
        condition = condition.replace("Column<b'", "").replace("'>", "")

        # Abbreviate if needed
        if self.abbreviate_conditions and len(condition) > self.max_condition_length:
            condition = condition[:self.max_condition_length - 3] + "..."

        return condition

    def _generate_connections(
        self,
        flow: LineageFlow,
        node_ids: Dict[str, str],
        lineage_graph: LineageGraph
    ) -> List[str]:
        """Generate connections between operation nodes, bridging over hidden passthrough operations."""
        lines = [""] # Start with empty line for spacing

        # Track which connections we've already added to avoid duplicates
        added_connections = set()

        # Use the actual edges from the lineage graph
        for edge in lineage_graph.edges:
            source_node_id = node_ids.get(edge.source_id)
            target_node_id = node_ids.get(edge.target_id)

            # If both nodes are visible, add direct connection
            if source_node_id and target_node_id:
                connection = (source_node_id, target_node_id)
                if connection not in added_connections:
                    # Get operation types to choose appropriate arrow style
                    source_op = self._find_operation_by_id(flow, edge.source_id)
                    target_op = self._find_operation_by_id(flow, edge.target_id)

                    # Use different arrow styles based on operation types
                    if target_op and target_op.operation_type == OperationType.JOIN:
                        # Use thick arrows for join inputs to show parallel branches merging
                        lines.append(f' {source_node_id} ==> {target_node_id}')
                    else:
                        # Use regular arrows for normal data flow
                        lines.append(f' {source_node_id} --> {target_node_id}')

                    added_connections.add(connection)

            # If source is visible but target is hidden (passthrough), find the next visible operation
            elif source_node_id and not target_node_id:
                next_visible_id = self._find_next_visible_operation(edge.target_id, lineage_graph, node_ids)
                if next_visible_id:
                    connection = (source_node_id, next_visible_id)
                    if connection not in added_connections:
                        # Bridge connection - use regular arrow
                        lines.append(f' {source_node_id} --> {next_visible_id}')
                        added_connections.add(connection)

        return lines

    def _find_next_visible_operation(
        self,
        start_op_id: str,
        lineage_graph: LineageGraph,
        node_ids: Dict[str, str]
    ) -> Optional[str]:
        """
        Find the next visible operation by traversing the lineage graph from a hidden operation.

        This handles the case where passthrough operations are hidden and we need to bridge
        connections to the next visible operation in the chain.
        """
        visited = set()
        queue = [start_op_id]

        while queue:
            current_id = queue.pop(0)

            if current_id in visited:
                continue

            visited.add(current_id)

            # If this operation is visible (in node_ids), return it
            if current_id in node_ids:
                return node_ids[current_id]

            # Otherwise, find all operations that this operation connects to
            for edge in lineage_graph.edges:
                if edge.source_id == current_id and edge.target_id not in visited:
                    queue.append(edge.target_id)

        return None

    def _find_operation_by_id(self, flow: LineageFlow, op_id: str) -> Optional[OperationMetrics]:
        """Find an operation by its ID in the flow."""
        for concept in flow.business_concepts:
            for operation in concept.operations:
                if operation.operation_id == op_id:
                    return operation
        return None


    def _generate_node_classes(self, flow: LineageFlow, node_ids: Dict[str, str]) -> List[str]:
        """Generate CSS class assignments for operation nodes."""
        lines = [""] # Add empty line before class assignments

        # Only add class assignments if we have nodes
        if node_ids:
            for concept in flow.business_concepts:
                for operation in concept.operations:
                    node_id = node_ids.get(operation.operation_id)
                    if node_id:
                        if operation.operation_type == OperationType.SOURCE:
                            lines.append(f" class {node_id} sourceOp")
                        elif operation.operation_type == OperationType.FILTER:
                            lines.append(f" class {node_id} filterOp")
                        elif operation.operation_type == OperationType.JOIN:
                            lines.append(f" class {node_id} joinOp")
                        elif operation.operation_type == OperationType.GROUP_BY:
                            lines.append(f" class {node_id} groupOp")
                        else:
                            lines.append(f" class {node_id} defaultOp")

        return lines

    def _generate_styles(self) -> List[str]:
        """Generate Mermaid styles for the diagram using centralized styles."""
        return ["", generate_mermaid_style_classes()]

    def create_detailed_summary(self, lineage_graph: LineageGraph) -> str:
        """
        Create a detailed text summary of the operation flow.

        Args:
            lineage_graph: The lineage graph to analyze

        Returns:
            Formatted text summary
        """
        flow = self.analyze_lineage_flow(lineage_graph)

        lines = []
        lines.append("DETAILED OPERATION FLOW SUMMARY")
        lines.append("=" * 80)

        for concept in flow.business_concepts:
            lines.append(f"\n {concept.concept_name}")
            if concept.concept_description:
                lines.append(f" {concept.concept_description}")
            if concept.tracked_columns:
                lines.append(f" Tracked Columns: {', '.join(concept.tracked_columns)}")

            lines.append(f"\n Operations ({len(concept.operations)}):")

            for i, operation in enumerate(concept.operations, 1):
                lines.append(f"\n {i}. {operation.operation_name}")

                # Operation details
                if operation.filter_condition:
                    lines.append(f" Filter: {self._format_condition(operation.filter_condition)}")
                elif operation.join_type:
                    lines.append(f" Join Type: {operation.join_type}")
                    if operation.join_keys:
                        lines.append(f" Join Keys: {', '.join(operation.join_keys)}")
                elif operation.group_by_columns:
                    lines.append(f" Group By: {', '.join(operation.group_by_columns)}")

                # Record counts
                if operation.input_record_count is not None:
                    lines.append(f" Input: {operation.input_record_count:,} records")
                if operation.output_record_count is not None:
                    lines.append(f" Output: {operation.output_record_count:,} records")

                if operation.record_change is not None:
                    change = operation.record_change
                    change_str = f"+{change:,}" if change >= 0 else f"{change:,}"
                    if self.show_percentages and operation.record_change_pct is not None:
                        pct = operation.record_change_pct
                        pct_str = f"+{pct:.1f}%" if pct >= 0 else f"{pct:.1f}%"
                        lines.append(f" Impact: {change_str} ({pct_str})")
                    else:
                        lines.append(f" Impact: {change_str}")

                # Column metrics
                if self.show_column_metrics and (operation.input_column_metrics or operation.output_column_metrics):
                    lines.append(f" Column Metrics:")

                    # Get all tracked columns
                    all_columns = set(operation.input_column_metrics.keys()) | set(operation.output_column_metrics.keys())

                    for col_name in sorted(all_columns):
                        input_count = operation.input_column_metrics.get(col_name)
                        output_count = operation.output_column_metrics.get(col_name)

                        if input_count is not None and output_count is not None:
                            # Show input output change
                            col_change = output_count - input_count
                            if col_change != 0:
                                col_change_str = f"+{col_change:,}" if col_change > 0 else f"{col_change:,}"
                                lines.append(f" - {col_name}: {input_count:,} {output_count:,} ({col_change_str} distinct)")
                            else:
                                lines.append(f" - {col_name}: {output_count:,} distinct (unchanged)")
                        elif output_count is not None:
                            # New column
                            lines.append(f" - {col_name}: {output_count:,} distinct (new column)")
                        elif input_count is not None:
                            # Column removed
                            lines.append(f" - {col_name}: {input_count:,} removed")

                # Execution time
                if self.show_execution_times and operation.execution_time is not None:
                    lines.append(f" Time: {operation.execution_time:.3f}s")

        # Join points summary
        if flow.join_points:
            lines.append(f"\n Join Points ({len(flow.join_points)}):")
            for jp in flow.join_points:
                lines.append(f" - {jp['join_type']} join on {', '.join(jp['join_keys'])}")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)


class ForkAwareLineageDiagramGenerator:
    """
    Enhanced lineage diagram generator with fork-aware visualization.

    This class provides advanced visualization capabilities for lineage graphs
    that include fork patterns, merge points, and diamond patterns.
    """

    def __init__(self,
                 show_fork_indicators: bool = True,
                 show_merge_indicators: bool = True,
                 show_parallel_paths: bool = True,
                 highlight_diamond_patterns: bool = True):
        """
        Initialize fork-aware diagram generator.

        Args:
            show_fork_indicators: Show special styling for fork points
            show_merge_indicators: Show special styling for merge points
            show_parallel_paths: Highlight parallel execution paths
            highlight_diamond_patterns: Highlight fork-merge diamond patterns
        """
        self.show_fork_indicators = show_fork_indicators
        self.show_merge_indicators = show_merge_indicators
        self.show_parallel_paths = show_parallel_paths
        self.highlight_diamond_patterns = highlight_diamond_patterns

    def generate_fork_aware_diagram(self, enhanced_graph: EnhancedLineageGraph) -> str:
        """
        Generate a Mermaid diagram with fork-aware visualization.

        Args:
            enhanced_graph: Enhanced lineage graph with fork information

        Returns:
            Mermaid diagram string with fork visualization
        """
        lines = ["graph TD"]

        # Generate nodes with fork/merge styling
        self._add_nodes_with_styling(lines, enhanced_graph)

        # Generate edges with fork indicators
        self._add_edges_with_fork_indicators(lines, enhanced_graph)

        # Add styling classes
        self._add_styling_classes(lines)

        # Add legend if any special patterns are present
        if self._has_special_patterns(enhanced_graph):
            self._add_pattern_legend(lines, enhanced_graph)

        return "\n".join(lines)

    def _add_nodes_with_styling(self, lines: List[str], enhanced_graph: EnhancedLineageGraph) -> None:
        """Add nodes with appropriate styling for forks and merges."""
        for node_id, node in enhanced_graph.nodes.items():
            lineage_id = node.lineage_id
            display_name = self._format_node_name(node, enhanced_graph)

            # Determine node styling based on fork/merge status
            if lineage_id and enhanced_graph.is_fork_point(lineage_id):
                fork_degree = enhanced_graph.get_fork_degree(lineage_id)
                lines.append(f"    {node_id}[{display_name}<br/>Fork: {fork_degree} paths]:::fork")

            elif lineage_id and enhanced_graph.is_merge_point(lineage_id):
                parent_count = len(enhanced_graph.get_parents(lineage_id))
                lines.append(f"    {node_id}[{display_name}<br/>Merge: {parent_count} inputs]:::merge")

            else:
                lines.append(f"    {node_id}[{display_name}]")

    def _add_edges_with_fork_indicators(self, lines: List[str], enhanced_graph: EnhancedLineageGraph) -> None:
        """Add edges with special indicators for fork relationships."""
        for edge in enhanced_graph.edges:
            source_id = edge.source_id
            target_id = edge.target_id

            # Check if this is a fork edge
            if edge.is_fork_edge and self.show_fork_indicators:
                fork_degree = edge.fork_degree
                if fork_degree > 2:
                    # High-degree fork - use dashed line
                    lines.append(f"    {source_id} -.->|fork {fork_degree}| {target_id}")
                else:
                    # Simple fork - use thick line
                    lines.append(f"    {source_id} ==>|fork| {target_id}")
            else:
                # Regular edge
                lines.append(f"    {source_id} --> {target_id}")

    def _add_styling_classes(self, lines: List[str]) -> None:
        """Add CSS styling classes for fork/merge visualization."""
        if self.show_fork_indicators:
            lines.extend([
                "    classDef fork fill:#ffcccc,stroke:#cc0000,stroke-width:3px,color:#000",
                "    classDef merge fill:#ccffcc,stroke:#00cc00,stroke-width:3px,color:#000"
            ])

        if self.show_parallel_paths:
            lines.extend([
                "    classDef parallel fill:#ffffcc,stroke:#cccc00,stroke-width:2px,color:#000"
            ])

        if self.highlight_diamond_patterns:
            lines.extend([
                "    classDef diamond fill:#ccccff,stroke:#0000cc,stroke-width:2px,color:#000"
            ])

    def _add_pattern_legend(self, lines: List[str], enhanced_graph: EnhancedLineageGraph) -> None:
        """Add a legend explaining the fork patterns."""
        statistics = enhanced_graph.get_statistics()

        legend_lines = [
            "",
            "    subgraph Legend[\" Pattern Legend \"]",
            f"        L1[Fork Point<br/>{statistics['fork_points']} detected]:::fork",
            f"        L2[Merge Point<br/>{statistics['merge_points']} detected]:::merge"
        ]

        if statistics['diamond_patterns']:
            legend_lines.append(f"        L3[Diamond Pattern<br/>{len(statistics['diamond_patterns'])} detected]:::diamond")

        legend_lines.append("    end")
        lines.extend(legend_lines)

    def _format_node_name(self, node, enhanced_graph: EnhancedLineageGraph) -> str:
        """Format node name with context information."""
        name = node.name or node.node_id

        # Add context information
        if node.metadata.get('operation_type'):
            op_type = node.metadata['operation_type']
            name = f"{op_type.title()}<br/>{name}"

        return name

    def _has_special_patterns(self, enhanced_graph: EnhancedLineageGraph) -> bool:
        """Check if the graph has any special patterns worth highlighting."""
        statistics = enhanced_graph.get_statistics()
        return (statistics['fork_points'] > 0 or
                statistics['merge_points'] > 0 or
                len(statistics['diamond_patterns']) > 0)

    def generate_fork_summary_report(self, enhanced_graph: EnhancedLineageGraph) -> str:
        """
        Generate a summary report of fork patterns in the lineage.

        Args:
            enhanced_graph: Enhanced lineage graph with fork information

        Returns:
            Formatted report string
        """
        lines = ["# Fork Pattern Analysis Report", ""]

        statistics = enhanced_graph.get_statistics()

        # Overall statistics
        lines.extend([
            "## Overall Statistics",
            f"- Total nodes: {statistics['total_nodes']}",
            f"- Total edges: {statistics['total_edges']}",
            f"- Fork points: {statistics['fork_points']}",
            f"- Merge points: {statistics['merge_points']}",
            f"- Maximum fork degree: {statistics['max_fork_degree']}",
            f"- Average fork degree: {statistics['avg_fork_degree']:.2f}",
            ""
        ])

        # Fork points detail
        if statistics['fork_points'] > 0:
            lines.extend(["## Fork Points Detail", ""])
            for fork_point in enhanced_graph.get_fork_points():
                lines.extend([
                    f"### Fork Point: {fork_point.lineage_id}",
                    f"- Fork degree: {fork_point.get_fork_degree()}",
                    f"- Consumer contexts: {', '.join(fork_point.consumer_contexts)}",
                    f"- Is cached: {fork_point.is_cached}",
                    ""
                ])

        # Diamond patterns
        diamond_patterns = statistics.get('diamond_patterns', [])
        if diamond_patterns:
            lines.extend(["## Diamond Patterns", ""])
            for i, pattern in enumerate(diamond_patterns, 1):
                lines.extend([
                    f"### Diamond Pattern {i}",
                    f"- Fork point: {pattern['fork_point']}",
                    f"- Merge point: {pattern['merge_point']}",
                    f"- Parallel paths: {pattern['path_count']}",
                    f"- Path details: {', '.join(pattern['parallel_paths'])}",
                    ""
                ])

        # Recommendations
        lines.extend([
            "## Recommendations",
            ""
        ])

        if statistics['fork_points'] > 0:
            lines.extend([
                "### Fork Optimization",
                "- Consider caching DataFrames at fork points to improve performance",
                "- Monitor memory usage for high-degree fork points",
                "- Validate that fork patterns match business logic expectations",
                ""
            ])

        if len(diamond_patterns) > 0:
            lines.extend([
                "### Diamond Pattern Optimization",
                "- Review if parallel processing is intentional",
                "- Consider consolidating paths if business logic allows",
                "- Ensure proper resource allocation for parallel execution",
                ""
            ])

        return "\n".join(lines)