"""Mermaid diagram generator for business-friendly lineage visualization."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..core.graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
    ContextGroupNode,
    LineageGraph,
    OperationNode,
    OperationType,
)
from ..utils.exceptions import VisualizationError
from .diagram_styles import (
    generate_mermaid_style_classes,
    get_mermaid_shape_template,
    get_node_class_name,
    get_node_style,
)

logger = logging.getLogger(__name__)


class MermaidTheme(Enum):
    """Available Mermaid themes for different presentation contexts."""
    DEFAULT = "default"
    BUSINESS = "base"
    TECHNICAL = "forest"
    PRESENTATION = "neutral"
    DARK = "dark"


@dataclass
class MermaidStyle:
    """Style configuration for Mermaid diagram elements."""
    business_concept_color: str = "#e1f5fe"
    business_concept_border: str = "#01579b"
    operation_color: str = "#f3e5f5"
    operation_border: str = "#4a148c"
    context_group_color: str = "#e8f5e8"
    context_group_border: str = "#1b5e20"
    data_flow_color: str = "#2196f3"
    containment_color: str = "#9c27b0"


class MermaidGenerator:
    """
    Generates Mermaid diagrams from business lineage graphs.

    Mermaid is a diagramming and charting tool that renders markdown-inspired
    text definitions to create and modify diagrams dynamically. It's ideal for
    business presentations and documentation.
    """

    def __init__(
        self,
        theme: MermaidTheme = MermaidTheme.BUSINESS,
        style: Optional[MermaidStyle] = None,
        include_technical_details: bool = False,
        max_label_length: int = 30,
    ):
        """
        Initialize the Mermaid generator.

        Args:
            theme: Mermaid theme to use
            style: Custom style configuration
            include_technical_details: Whether to include technical operation details
            max_label_length: Maximum length for node labels
        """
        self.theme = theme
        self.style = style or MermaidStyle()
        self.include_technical_details = include_technical_details
        self.max_label_length = max_label_length

        # Node ID mapping for valid Mermaid identifiers
        self._node_id_map: Dict[str, str] = {}
        self._next_id = 1

        logger.debug(f"Initialized MermaidGenerator with theme: {theme.value}")

    def generate_flowchart(
        self,
        lineage_graph: LineageGraph,
        direction: str = "TD",
        title: Optional[str] = None,
        group_by_context: bool = True,
    ) -> str:
        """
        Generate a Mermaid flowchart from a lineage graph.

        Args:
            lineage_graph: Lineage graph to visualize
            direction: Flow direction (TD=top-down, LR=left-right, BT=bottom-top, RL=right-left)
            title: Optional title for the diagram
            group_by_context: Whether to group nodes by business context

        Returns:
            Mermaid flowchart diagram as string

        Example:
            >>> generator = MermaidGenerator()
            >>> diagram = generator.generate_flowchart(graph, title="Customer Analysis Pipeline")
        """
        try:
            self._reset_id_mapping()

            # Start building the diagram
            lines = []

            # Add title if provided
            if title:
                lines.append(f"---")
                lines.append(f"title: {title}")
                lines.append(f"---")

            # Start flowchart definition
            lines.append(f"flowchart {direction}")

            # Generate nodes and edges
            if group_by_context:
                lines.extend(self._generate_grouped_nodes(lineage_graph))
            else:
                lines.extend(self._generate_flat_nodes(lineage_graph))

            lines.extend(self._generate_edges(lineage_graph))

            # Add styling
            lines.extend(self._generate_styles())

            # Join all lines
            diagram = "\n    ".join([""] + lines)

            logger.debug(f"Generated Mermaid flowchart with {len(lineage_graph.nodes)} nodes")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to generate Mermaid flowchart: {e}")

    def generate_timeline(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        show_execution_times: bool = True,
    ) -> str:
        """
        Generate a Mermaid timeline diagram showing business concept execution order.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title for the timeline
            show_execution_times: Whether to include execution times

        Returns:
            Mermaid timeline diagram as string
        """
        try:
            lines = []

            # Add title
            if title:
                lines.append(f"---")
                lines.append(f"title: {title}")
                lines.append(f"---")

            lines.append("timeline")

            # Get business concepts sorted by execution order
            business_concepts = [
                node for node in lineage_graph.nodes.values()
                if isinstance(node, BusinessConceptNode) and hasattr(node, 'start_time')
            ]
            business_concepts.sort(key=lambda x: getattr(x, 'start_time', 0))

            # Group by time periods (you could enhance this to group by actual time periods)
            for i, concept in enumerate(business_concepts):
                section_title = f"Step {i + 1}"
                lines.append(f"    section {section_title}")

                # Create timeline entry
                label = self._truncate_label(concept.name)
                if show_execution_times and hasattr(concept, 'execution_time'):
                    exec_time = getattr(concept, 'execution_time', 0)
                    label += f" ({exec_time:.2f}s)"

                lines.append(f"        {label}")

                # Add description if available
                if concept.description and len(concept.description) < 100:
                    lines.append(f"            : {concept.description}")

            diagram = "\n".join(lines)
            logger.debug(f"Generated Mermaid timeline with {len(business_concepts)} concepts")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to generate Mermaid timeline: {e}")

    def generate_journey_map(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        actor: str = "Data Analyst",
    ) -> str:
        """
        Generate a Mermaid user journey map for the data processing workflow.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title for the journey map
            actor: Name of the actor performing the journey

        Returns:
            Mermaid user journey diagram as string
        """
        try:
            lines = []

            # Add title
            if title:
                lines.append(f"---")
                lines.append(f"title: {title}")
                lines.append(f"---")

            lines.append("journey")
            lines.append(f"    title {actor} Data Processing Journey")

            # Get business concepts in execution order
            business_concepts = [
                node for node in lineage_graph.nodes.values()
                if isinstance(node, BusinessConceptNode)
            ]

            # Create journey sections
            for i, concept in enumerate(business_concepts):
                section_title = f"Phase {i + 1}: {self._truncate_label(concept.name, 20)}"
                lines.append(f"    section {section_title}")

                # Add journey steps
                if hasattr(concept, 'technical_operations') and concept.technical_operations:
                    for op in concept.technical_operations[:3]:  # Limit to 3 operations
                        op_name = self._truncate_label(op.name, 25)
                        satisfaction = self._calculate_satisfaction_score(op)
                        lines.append(f"        {op_name}: {satisfaction}: {actor}")
                else:
                    # Single step for the concept
                    satisfaction = self._calculate_satisfaction_score(concept)
                    lines.append(f"        Execute: {satisfaction}: {actor}")

            diagram = "\n".join(lines)
            logger.debug(f"Generated Mermaid journey map with {len(business_concepts)} concepts")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to generate Mermaid journey map: {e}")

    def generate_quadrant_chart(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        x_axis: str = "Complexity",
        y_axis: str = "Business Impact",
    ) -> str:
        """
        Generate a Mermaid quadrant chart showing business concepts by impact and complexity.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title for the chart
            x_axis: Label for x-axis
            y_axis: Label for y-axis

        Returns:
            Mermaid quadrant chart as string
        """
        try:
            lines = []

            # Add title
            if title:
                lines.append(f"---")
                lines.append(f"title: {title}")
                lines.append(f"---")

            lines.append("quadrantChart")
            lines.append(f"    title {title or 'Business Concept Analysis'}")
            lines.append(f"    x-axis Low {x_axis} --> High {x_axis}")
            lines.append(f"    y-axis Low {y_axis} --> High {y_axis}")
            lines.append("    quadrant-1 High Impact, Low Complexity")
            lines.append("    quadrant-2 High Impact, High Complexity")
            lines.append("    quadrant-3 Low Impact, Low Complexity")
            lines.append("    quadrant-4 Low Impact, High Complexity")

            # Add business concepts as points
            business_concepts = [
                node for node in lineage_graph.nodes.values()
                if isinstance(node, BusinessConceptNode)
            ]

            for concept in business_concepts:
                # Calculate complexity and impact scores
                complexity = self._calculate_complexity_score(concept)
                impact = self._calculate_impact_score(concept)

                label = self._truncate_label(concept.name, 20)
                lines.append(f"    {label}: [{complexity:.2f}, {impact:.2f}]")

            diagram = "\n".join(lines)
            logger.debug(f"Generated quadrant chart with {len(business_concepts)} concepts")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to generate Mermaid quadrant chart: {e}")

    def _reset_id_mapping(self) -> None:
        """Reset the node ID mapping for a new diagram."""
        self._node_id_map.clear()
        self._next_id = 1

    def _get_node_id(self, node_id: str) -> str:
        """Get or create a Mermaid-compatible node ID."""
        if node_id not in self._node_id_map:
            self._node_id_map[node_id] = f"node{self._next_id}"
            self._next_id += 1
        return self._node_id_map[node_id]

    def _generate_grouped_nodes(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate nodes grouped by business context."""
        lines = []

        # Group nodes by context
        context_groups = {}
        ungrouped_nodes = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, ContextGroupNode):
                context_groups[node.node_id] = {
                    'node': node,
                    'children': []
                }

        # Find child nodes for each context
        for edge in lineage_graph.edges:
            if edge.edge_type == "contains" and edge.source_id in context_groups:
                target_node = lineage_graph.nodes.get(edge.target_id)
                if target_node:
                    context_groups[edge.source_id]['children'].append(target_node)

        # Add ungrouped nodes
        grouped_node_ids = set()
        for group_info in context_groups.values():
            grouped_node_ids.update(child.node_id for child in group_info['children'])

        for node in lineage_graph.nodes.values():
            if node.node_id not in grouped_node_ids and not isinstance(node, ContextGroupNode):
                ungrouped_nodes.append(node)

        # Generate subgraphs for contexts
        for group_id, group_info in context_groups.items():
            group_node = group_info['node']
            children = group_info['children']

            if children:  # Only create subgraph if there are children
                subgraph_id = self._get_node_id(group_id)
                group_label = self._truncate_label(group_node.name)

                lines.append(f"subgraph {subgraph_id} [\"{group_label}\"]")

                # Add child nodes
                for child in children:
                    child_id = self._get_node_id(child.node_id)
                    child_label = self._truncate_label(child.name)
                    child_shape = self._get_node_shape(child)

                    lines.append(f"    {child_id}{child_shape}\"{child_label}\"{child_shape.replace('[', ']').replace('(', ')')}")

                lines.append("end")

        # Add ungrouped nodes
        for node in ungrouped_nodes:
            node_id = self._get_node_id(node.node_id)
            node_label = self._truncate_label(node.name)
            node_shape = self._get_node_shape(node)

            lines.append(f"{node_id}{node_shape}\"{node_label}\"{node_shape.replace('[', ']').replace('(', ')')}")

        return lines

    def _generate_flat_nodes(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate nodes without grouping."""
        lines = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, ContextGroupNode):
                continue  # Skip context groups in flat mode

            node_id = self._get_node_id(node.node_id)
            node_label = self._truncate_label(node.name)
            node_shape = self._get_node_shape(node)

            lines.append(f"{node_id}{node_shape}\"{node_label}\"{node_shape.replace('[', ']').replace('(', ')')}")

        return lines

    def _generate_edges(self, lineage_graph: LineageGraph) -> List[str]:
        """Generate edge definitions."""
        lines = []

        for edge in lineage_graph.edges:
            source_id = self._get_node_id(edge.source_id)
            target_id = self._get_node_id(edge.target_id)

            # Skip edges to/from context groups in flat mode
            source_node = lineage_graph.nodes.get(edge.source_id)
            target_node = lineage_graph.nodes.get(edge.target_id)

            if not self.include_technical_details:
                if isinstance(source_node, ContextGroupNode) or isinstance(target_node, ContextGroupNode):
                    continue

            # Choose edge style based on type
            if edge.edge_type == "data_flow":
                edge_style = "-->"
                edge_label = ""
            elif edge.edge_type == "contains":
                continue  # Handled by subgraphs
            else:
                edge_style = "-.->'"
                edge_label = ""

            # Add edge with optional label
            if edge_label:
                lines.append(f"{source_id} {edge_style}|{edge_label}| {target_id}")
            else:
                lines.append(f"{source_id} {edge_style} {target_id}")

        return lines

    def _generate_styles(self) -> List[str]:
        """Generate CSS-like style definitions."""
        lines = []

        # Apply theme
        if self.theme != MermaidTheme.DEFAULT:
            lines.append(f"%%{{init: {{'theme':'{self.theme.value}'}}}}%%")

        # Add custom styles for node types
        business_concept_style = f"fill:{self.style.business_concept_color},stroke:{self.style.business_concept_border}"
        operation_style = f"fill:{self.style.operation_color},stroke:{self.style.operation_border}"
        context_style = f"fill:{self.style.context_group_color},stroke:{self.style.context_group_border}"

        # Apply styles (this is a simplified approach - in practice you'd need to track node types)
        lines.append(f"classDef businessConcept {business_concept_style}")
        lines.append(f"classDef operation {operation_style}")
        lines.append(f"classDef contextGroup {context_style}")

        return lines

    def _get_node_shape(self, node: BaseLineageNode) -> str:
        """Get appropriate Mermaid shape for a node type using centralized styles."""
        if isinstance(node, BusinessConceptNode):
            return get_mermaid_shape_template('business_concept')
        elif isinstance(node, OperationNode):
            op_type = node.metadata.get('operation_type', 'operation')
            return get_mermaid_shape_template(op_type)
        elif isinstance(node, ContextGroupNode):
            return get_mermaid_shape_template('default')
        else:
            return get_mermaid_shape_template('default')

    def _truncate_label(self, label: str, max_length: Optional[int] = None) -> str:
        """Truncate labels to fit in diagram."""
        max_len = max_length or self.max_label_length
        if len(label) <= max_len:
            return label
        return label[:max_len - 3] + "..."

    def _calculate_satisfaction_score(self, node: BaseLineageNode) -> int:
        """Calculate satisfaction score for journey map (1-5)."""
        # Simple heuristic based on execution time and success
        if hasattr(node, 'execution_time'):
            exec_time = getattr(node, 'execution_time', 0)
            if exec_time < 1.0:
                return 5  # Very satisfied
            elif exec_time < 5.0:
                return 4  # Satisfied
            elif exec_time < 10.0:
                return 3  # Neutral
            elif exec_time < 30.0:
                return 2  # Dissatisfied
            else:
                return 1  # Very dissatisfied
        return 3  # Default neutral

    def _calculate_complexity_score(self, concept: BusinessConceptNode) -> float:
        """Calculate complexity score (0.0-1.0) based on operations and metadata."""
        base_complexity = 0.3

        # Add complexity based on number of operations
        if hasattr(concept, 'technical_operations'):
            op_count = len(getattr(concept, 'technical_operations', []))
            base_complexity += min(op_count * 0.1, 0.5)

        # Add complexity based on execution time
        if hasattr(concept, 'execution_time'):
            exec_time = getattr(concept, 'execution_time', 0)
            base_complexity += min(exec_time * 0.01, 0.2)

        return min(base_complexity, 1.0)

    def _calculate_impact_score(self, concept: BusinessConceptNode) -> float:
        """Calculate business impact score (0.0-1.0)."""
        # Use concept's calculate_impact method if available
        if hasattr(concept, 'calculate_impact'):
            return min(concept.calculate_impact() / 100.0, 1.0)

        # Fallback: use priority and metadata
        base_impact = 0.5

        # Higher impact if it's in the business domain patterns
        if concept.metadata.get('inferred_context'):
            confidence = concept.metadata.get('confidence', 0.5)
            base_impact += confidence * 0.3

        return min(base_impact, 1.0)