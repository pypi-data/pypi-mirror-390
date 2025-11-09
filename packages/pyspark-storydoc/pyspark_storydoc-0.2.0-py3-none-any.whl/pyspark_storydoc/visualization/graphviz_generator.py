"""Graphviz generator for detailed technical lineage visualization."""

import html
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
    ContextGroupNode,
    LineageGraph,
    OperationNode,
    OperationType,
)
from ..utils.exceptions import VisualizationError

logger = logging.getLogger(__name__)


class GraphvizLayout(Enum):
    """Available Graphviz layout engines."""
    DOT = "dot"      # Hierarchical layouts
    NEATO = "neato"  # Spring model layouts
    FDP = "fdp"      # Force-directed layouts
    SFDP = "sfdp"    # Scalable force-directed layouts
    CIRCO = "circo"  # Circular layouts
    TWOPI = "twopi"  # Radial layouts


class GraphvizFormat(Enum):
    """Output formats supported by Graphviz."""
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    DOT = "dot"
    JSON = "json"


@dataclass
class GraphvizStyle:
    """Style configuration for Graphviz diagram elements."""
    # Node styles
    business_concept_color: str = "#E3F2FD"
    business_concept_border_color: str = "#1976D2"
    operation_color: str = "#FCE4EC"
    operation_border_color: str = "#C2185B"
    context_group_color: str = "#E8F5E8"
    context_group_border_color: str = "#388E3C"

    # Edge styles
    data_flow_color: str = "#2196F3"
    containment_color: str = "#9C27B0"
    dependency_color: str = "#FF9800"

    # Font settings
    node_font_name: str = "Arial"
    node_font_size: int = 10
    edge_font_name: str = "Arial"
    edge_font_size: int = 8

    # Shape settings
    business_concept_shape: str = "box"
    operation_shape: str = "ellipse"
    context_group_shape: str = "folder"


class GraphvizGenerator:
    """
    Generates Graphviz DOT diagrams from business lineage graphs.

    Graphviz provides precise control over graph layout and is ideal for
    complex technical documentation and detailed lineage visualization.
    """

    def __init__(
        self,
        layout: GraphvizLayout = GraphvizLayout.DOT,
        style: Optional[GraphvizStyle] = None,
        include_metrics: bool = True,
        include_execution_times: bool = True,
        show_technical_details: bool = True,
    ):
        """
        Initialize the Graphviz generator.

        Args:
            layout: Graphviz layout engine to use
            style: Custom style configuration
            include_metrics: Whether to include DataFrame metrics in nodes
            include_execution_times: Whether to show execution times
            show_technical_details: Whether to include technical operation details
        """
        self.layout = layout
        self.style = style or GraphvizStyle()
        self.include_metrics = include_metrics
        self.include_execution_times = include_execution_times
        self.show_technical_details = show_technical_details

        # Node ID sanitization
        self._node_id_map: Dict[str, str] = {}
        self._next_id = 1

        logger.debug(f"Initialized GraphvizGenerator with layout: {layout.value}")

    def generate_lineage_graph(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        cluster_by_context: bool = True,
        rankdir: str = "TB",
    ) -> str:
        """
        Generate a comprehensive lineage graph in DOT format.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title for the diagram
            cluster_by_context: Whether to cluster nodes by business context
            rankdir: Direction of graph layout (TB, BT, LR, RL)

        Returns:
            Graphviz DOT diagram as string

        Example:
            >>> generator = GraphvizGenerator()
            >>> dot_graph = generator.generate_lineage_graph(graph, title="Data Pipeline Lineage")
        """
        try:
            self._reset_id_mapping()

            lines = []

            # Start digraph
            graph_name = self._sanitize_id(title or "lineage_graph")
            lines.append(f'digraph "{graph_name}" {{')

            # Graph attributes
            lines.append(f'    rankdir="{rankdir}";')
            lines.append(f'    layout="{self.layout.value}";')
            lines.append('    node [fontname="Arial", fontsize=10];')
            lines.append('    edge [fontname="Arial", fontsize=8];')

            # Add title label if provided
            if title:
                escaped_title = html.escape(title)
                lines.append(f'    labelloc="t";')
                lines.append(f'    label="{escaped_title}";')

            # Generate content
            if cluster_by_context:
                lines.extend(self._generate_clustered_nodes(lineage_graph))
            else:
                lines.extend(self._generate_flat_nodes(lineage_graph))

            # Generate edges
            lines.extend(self._generate_edges(lineage_graph))

            # Close digraph
            lines.append('}')

            dot_content = '\n'.join(lines)
            logger.debug(f"Generated Graphviz DOT graph with {len(lineage_graph.nodes)} nodes")
            return dot_content

        except Exception as e:
            raise VisualizationError(f"Failed to generate Graphviz lineage graph: {e}")

    def generate_business_flow(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        simplify: bool = True,
    ) -> str:
        """
        Generate a simplified business flow diagram focusing on business concepts.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title for the diagram
            simplify: Whether to hide technical operations

        Returns:
            Graphviz DOT diagram as string
        """
        try:
            self._reset_id_mapping()

            lines = []

            # Start digraph
            graph_name = self._sanitize_id(title or "business_flow")
            lines.append(f'digraph "{graph_name}" {{')

            # Graph attributes for business flow
            lines.append('    rankdir="LR";')  # Left to right for flow
            lines.append('    node [fontname="Arial", fontsize=12, style="filled"];')
            lines.append('    edge [fontname="Arial", fontsize=10];')

            # Add title
            if title:
                escaped_title = html.escape(title)
                lines.append(f'    labelloc="t";')
                lines.append(f'    label="{escaped_title}";')

            # Generate business concept nodes only
            business_concepts = [
                node for node in lineage_graph.nodes.values()
                if isinstance(node, BusinessConceptNode)
            ]

            for concept in business_concepts:
                node_id = self._get_sanitized_id(concept.node_id)
                node_label = self._create_business_concept_label(concept)

                lines.append(f'    {node_id} [')
                lines.append(f'        label="{node_label}",')
                lines.append(f'        shape="{self.style.business_concept_shape}",')
                lines.append(f'        fillcolor="{self.style.business_concept_color}",')
                lines.append(f'        color="{self.style.business_concept_border_color}"')
                lines.append('    ];')

            # Generate simplified edges (business concept to business concept)
            self._generate_business_concept_edges(lineage_graph, lines)

            lines.append('}')

            dot_content = '\n'.join(lines)
            logger.debug(f"Generated business flow with {len(business_concepts)} concepts")
            return dot_content

        except Exception as e:
            raise VisualizationError(f"Failed to generate business flow: {e}")

    def generate_operation_detail(
        self,
        lineage_graph: LineageGraph,
        business_concept_id: str,
        title: Optional[str] = None,
    ) -> str:
        """
        Generate a detailed view of operations within a specific business concept.

        Args:
            lineage_graph: Lineage graph to visualize
            business_concept_id: ID of the business concept to detail
            title: Optional title for the diagram

        Returns:
            Graphviz DOT diagram as string
        """
        try:
            concept_node = lineage_graph.nodes.get(business_concept_id)
            if not isinstance(concept_node, BusinessConceptNode):
                raise VisualizationError(f"Node {business_concept_id} is not a business concept")

            self._reset_id_mapping()

            lines = []

            # Start digraph
            graph_name = self._sanitize_id(f"operations_{concept_node.name}")
            lines.append(f'digraph "{graph_name}" {{')

            # Graph attributes
            lines.append('    rankdir="TB";')
            lines.append('    node [fontname="Arial", fontsize=10, style="filled"];')
            lines.append('    edge [fontname="Arial", fontsize=8];')

            # Add title
            concept_title = title or f"Operations in: {concept_node.name}"
            escaped_title = html.escape(concept_title)
            lines.append(f'    labelloc="t";')
            lines.append(f'    label="{escaped_title}";')

            # Add the main business concept node
            concept_id = self._get_sanitized_id(concept_node.node_id)
            concept_label = self._create_business_concept_label(concept_node)

            lines.append(f'    {concept_id} [')
            lines.append(f'        label="{concept_label}",')
            lines.append(f'        shape="box",')
            lines.append(f'        fillcolor="{self.style.business_concept_color}",')
            lines.append(f'        color="{self.style.business_concept_border_color}",')
            lines.append('        style="filled,bold"')
            lines.append('    ];')

            # Add technical operations
            if hasattr(concept_node, 'technical_operations'):
                operations = getattr(concept_node, 'technical_operations', [])
                for i, operation in enumerate(operations):
                    op_id = self._get_sanitized_id(f"{concept_node.node_id}_op_{i}")
                    op_label = self._create_operation_label(operation)

                    lines.append(f'    {op_id} [')
                    lines.append(f'        label="{op_label}",')
                    lines.append(f'        shape="{self.style.operation_shape}",')
                    lines.append(f'        fillcolor="{self.style.operation_color}",')
                    lines.append(f'        color="{self.style.operation_border_color}"')
                    lines.append('    ];')

                    # Connect concept to operation
                    lines.append(f'    {concept_id} -> {op_id} [')
                    lines.append(f'        color="{self.style.dependency_color}",')
                    lines.append('        style="dashed"')
                    lines.append('    ];')

            lines.append('}')

            dot_content = '\n'.join(lines)
            logger.debug(f"Generated operation detail for concept: {concept_node.name}")
            return dot_content

        except Exception as e:
            raise VisualizationError(f"Failed to generate operation detail: {e}")

    def _reset_id_mapping(self) -> None:
        """Reset the node ID mapping for a new diagram."""
        self._node_id_map.clear()
        self._next_id = 1

    def _get_sanitized_id(self, node_id: str) -> str:
        """Get or create a sanitized Graphviz-compatible node ID."""
        if node_id not in self._node_id_map:
            # Create a valid Graphviz identifier
            sanitized = self._sanitize_id(f"node_{self._next_id}")
            self._node_id_map[node_id] = sanitized
            self._next_id += 1
        return self._node_id_map[node_id]

    def _sanitize_id(self, text: str) -> str:
        """Sanitize text to create valid Graphviz identifiers."""
        # Replace invalid characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        # Ensure it starts with a letter or underscore
        if not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = '_' + sanitized
        return sanitized

    def _generate_clustered_nodes(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate nodes clustered by business context."""
        lines = []

        # Group nodes by context
        context_groups = {}
        ungrouped_nodes = []

        # Find context groups
        for node in lineage_graph.nodes.values():
            if isinstance(node, ContextGroupNode):
                context_groups[node.node_id] = {
                    'node': node,
                    'children': []
                }

        # Find child nodes for each context
        for edge in lineage_graph.edges.values():
            if edge.edge_type == "contains" and edge.source_id in context_groups:
                target_node = lineage_graph.nodes.get(edge.target_id)
                if target_node:
                    context_groups[edge.source_id]['children'].append(target_node)

        # Find ungrouped nodes
        grouped_node_ids = set()
        for group_info in context_groups.values():
            grouped_node_ids.update(child.node_id for child in group_info['children'])

        for node in lineage_graph.nodes.values():
            if node.node_id not in grouped_node_ids and not isinstance(node, ContextGroupNode):
                ungrouped_nodes.append(node)

        # Generate clusters
        cluster_id = 0
        for group_id, group_info in context_groups.items():
            group_node = group_info['node']
            children = group_info['children']

            if children:  # Only create cluster if there are children
                cluster_name = f"cluster_{cluster_id}"
                escaped_label = html.escape(group_node.name)

                lines.append(f'    subgraph "{cluster_name}" {{')
                lines.append(f'        label="{escaped_label}";')
                lines.append(f'        style="filled";')
                lines.append(f'        fillcolor="{self.style.context_group_color}";')
                lines.append(f'        color="{self.style.context_group_border_color}";')

                # Add child nodes
                for child in children:
                    lines.extend(self._generate_single_node(child))

                lines.append('    }')
                cluster_id += 1

        # Add ungrouped nodes
        for node in ungrouped_nodes:
            lines.extend(self._generate_single_node(node))

        return lines

    def _generate_flat_nodes(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate nodes without clustering."""
        lines = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, ContextGroupNode):
                continue  # Skip context groups in flat mode
            lines.extend(self._generate_single_node(node))

        return lines

    def _generate_single_node(self, node: BaseLineageNode) -> List[str]:
        """Generate DOT definition for a single node."""
        lines = []
        node_id = self._get_sanitized_id(node.node_id)

        if isinstance(node, BusinessConceptNode):
            label = self._create_business_concept_label(node)
            shape = self.style.business_concept_shape
            fillcolor = self.style.business_concept_color
            color = self.style.business_concept_border_color

        elif isinstance(node, OperationNode):
            label = self._create_operation_label(node)
            shape = self.style.operation_shape
            fillcolor = self.style.operation_color
            color = self.style.operation_border_color

        else:
            label = html.escape(node.name)
            shape = "box"
            fillcolor = "#FFFFFF"
            color = "#000000"

        lines.append(f'        {node_id} [')
        lines.append(f'            label="{label}",')
        lines.append(f'            shape="{shape}",')
        lines.append(f'            fillcolor="{fillcolor}",')
        lines.append(f'            color="{color}",')
        lines.append('            style="filled"')
        lines.append('        ];')

        return lines

    def _generate_edges(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate edge definitions."""
        lines = []

        for edge in lineage_graph.edges.values():
            source_id = self._get_sanitized_id(edge.source_id)
            target_id = self._get_sanitized_id(edge.target_id)

            # Skip edges involving context groups if not showing technical details
            if not self.show_technical_details:
                source_node = lineage_graph.nodes.get(edge.source_id)
                target_node = lineage_graph.nodes.get(edge.target_id)
                if isinstance(source_node, ContextGroupNode) or isinstance(target_node, ContextGroupNode):
                    continue

            # Determine edge style based on type
            if edge.edge_type == "data_flow":
                color = self.style.data_flow_color
                style = "solid"
                label = ""
            elif edge.edge_type == "contains":
                continue  # Handled by clustering
            elif edge.edge_type == "dependency":
                color = self.style.dependency_color
                style = "dashed"
                label = "depends on"
            else:
                color = "#000000"
                style = "solid"
                label = ""

            lines.append(f'    {source_id} -> {target_id} [')
            lines.append(f'        color="{color}",')
            lines.append(f'        style="{style}"')

            if label:
                escaped_label = html.escape(label)
                lines.append(f',        label="{escaped_label}"')

            lines.append('    ];')

        return lines

    def _generate_business_concept_edges(self, lineage_graph: LineageGraph, lines: List[str]) -> None:
        """Generate simplified edges between business concepts."""
        business_concepts = [
            node for node in lineage_graph.nodes.values()
            if isinstance(node, BusinessConceptNode)
        ]

        # Create edges based on execution order or dependencies
        concept_ids = [concept.node_id for concept in business_concepts]
        for i in range(len(concept_ids) - 1):
            current_id = self._get_sanitized_id(concept_ids[i])
            next_id = self._get_sanitized_id(concept_ids[i + 1])

            lines.append(f'    {current_id} -> {next_id} [')
            lines.append(f'        color="{self.style.data_flow_color}",')
            lines.append('        style="bold"')
            lines.append('    ];')

    def _create_business_concept_label(self, concept: BusinessConceptNode) -> str:
        """Create a formatted label for a business concept node."""
        parts = [html.escape(concept.name)]

        # Add description if available and short
        if concept.description and len(concept.description) < 100:
            parts.append(html.escape(concept.description))

        # Add execution time if available and requested
        if self.include_execution_times and hasattr(concept, 'execution_time'):
            exec_time = getattr(concept, 'execution_time', 0)
            parts.append(f"Time: {exec_time:.3f}s")

        # Add metrics if available and requested
        if self.include_metrics and hasattr(concept, 'output_metrics'):
            metrics = getattr(concept, 'output_metrics')
            if metrics and hasattr(metrics, 'row_count'):
                parts.append(f"{metrics.row_count:,} rows")

        return "\\n".join(parts)

    def _create_operation_label(self, operation: OperationNode) -> str:
        """Create a formatted label for an operation node."""
        parts = [html.escape(operation.name)]

        # Add operation type
        parts.append(f"Type: {operation.operation_type.value}")

        # Add involved columns if available
        if operation.involved_columns:
            columns_text = ", ".join(operation.involved_columns[:3])
            if len(operation.involved_columns) > 3:
                columns_text += "..."
            parts.append(f"Columns: {html.escape(columns_text)}")

        # Add execution time if available
        if self.include_execution_times and hasattr(operation, 'execution_time'):
            exec_time = getattr(operation, 'execution_time', 0)
            parts.append(f"Time: {exec_time:.3f}s")

        return "\\n".join(parts)