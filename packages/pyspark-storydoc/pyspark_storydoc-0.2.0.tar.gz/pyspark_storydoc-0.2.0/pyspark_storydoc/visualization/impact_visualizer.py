"""
Business Impact Visualizer - Shows data flow impact with counts and filter logic.

This module creates specialized visualizations that show:
1. Top-down lineage grouped by Business Concept
2. Count changes between operations
3. Filter logic and operation details
4. Business impact flow
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
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


@dataclass
class OperationImpact:
    """Represents the impact of an operation on data."""
    operation_name: str
    operation_type: OperationType
    input_count: Optional[int] = None
    output_count: Optional[int] = None
    filter_condition: Optional[str] = None
    columns_involved: List[str] = None
    execution_time: Optional[float] = None
    business_context: Optional[str] = None

    @property
    def count_change(self) -> Optional[int]:
        """Calculate the change in record count."""
        if self.input_count is not None and self.output_count is not None:
            return self.output_count - self.input_count
        return None

    @property
    def count_change_percentage(self) -> Optional[float]:
        """Calculate the percentage change in record count."""
        if self.input_count is not None and self.output_count is not None and self.input_count > 0:
            return ((self.output_count - self.input_count) / self.input_count) * 100
        return None


@dataclass
class BusinessConceptFlow:
    """Represents a complete business concept flow with operations."""
    concept_name: str
    concept_description: str
    operations: List[OperationImpact]
    initial_count: Optional[int] = None
    final_count: Optional[int] = None

    @property
    def total_impact(self) -> Optional[int]:
        """Calculate total impact of all operations."""
        if self.initial_count is not None and self.final_count is not None:
            return self.final_count - self.initial_count
        return None


class BusinessImpactVisualizer:
    """
    Creates business-focused visualizations showing data flow impact.

    Specializes in showing:
    - Business concept groupings
    - Count changes through operations
    - Filter logic and conditions
    - Business impact summary
    """

    def __init__(self, show_execution_times: bool = True, show_percentages: bool = True):
        """
        Initialize the impact visualizer.

        Args:
            show_execution_times: Whether to include execution times
            show_percentages: Whether to show percentage changes
        """
        self.show_execution_times = show_execution_times
        self.show_percentages = show_percentages

    def analyze_business_flows(self, lineage_graph: LineageGraph) -> List[BusinessConceptFlow]:
        """
        Analyze the lineage graph to extract business concept flows.

        Args:
            lineage_graph: The lineage graph to analyze

        Returns:
            List of business concept flows with operation impacts
        """
        business_flows = []

        # Group nodes by business concepts
        business_concepts = [
            node for node in lineage_graph.nodes.values()
            if isinstance(node, BusinessConceptNode)
        ]

        for concept in business_concepts:
            # Find operations associated with this concept
            operations = self._find_concept_operations(concept, lineage_graph)

            # Extract operation impacts
            operation_impacts = []
            for op_node in operations:
                impact = self._extract_operation_impact(op_node)
                operation_impacts.append(impact)

            # Create business concept flow
            flow = BusinessConceptFlow(
                concept_name=concept.name,
                concept_description=concept.description or "",
                operations=operation_impacts,
                initial_count=self._get_initial_count(concept, operations),
                final_count=self._get_final_count(concept, operations)
            )

            business_flows.append(flow)

        return business_flows

    def create_impact_mermaid(
        self,
        lineage_graph: LineageGraph,
        title: str = "Business Impact Flow"
    ) -> str:
        """
        Create a Mermaid diagram showing business impact flow.

        Args:
            lineage_graph: The lineage graph to visualize
            title: Title for the diagram

        Returns:
            Mermaid diagram as string
        """
        try:
            flows = self.analyze_business_flows(lineage_graph)

            lines = []

            # Add title
            lines.append(f"---")
            lines.append(f"title: {title}")
            lines.append(f"---")
            lines.append("flowchart TD")

            node_counter = 1

            for flow in flows:
                # Create subgraph for each business concept
                subgraph_id = f"BC{node_counter}"
                lines.append(f"    subgraph {subgraph_id} [\"{flow.concept_name}\"]")

                # Add initial data node
                if flow.initial_count is not None:
                    initial_node = f"I{node_counter}"
                    lines.append(f"        {initial_node}[\" Initial Data<br/>{flow.initial_count:,} records\"]")
                    prev_node = initial_node
                else:
                    prev_node = None

                # Add operation nodes with impact
                for i, op in enumerate(flow.operations):
                    op_node = f"O{node_counter}_{i}"

                    # Create operation label with count change
                    label_parts = [f" {op.operation_name}"]

                    if op.filter_condition:
                        # Clean up filter condition for display
                        condition = self._clean_filter_condition(op.filter_condition)
                        label_parts.append(f"Filter: {condition}")

                    if op.output_count is not None:
                        label_parts.append(f"Result: {op.output_count:,} records")

                        if op.count_change is not None:
                            change_sign = "+" if op.count_change >= 0 else ""
                            label_parts.append(f"Change: {change_sign}{op.count_change:,}")

                            if self.show_percentages and op.count_change_percentage is not None:
                                label_parts.append(f"({change_sign}{op.count_change_percentage:.1f}%)")

                    if self.show_execution_times and op.execution_time is not None:
                        label_parts.append(f" {op.execution_time:.2f}s")

                    label = "<br/>".join(label_parts)

                    # Choose shape based on operation type
                    if op.operation_type == OperationType.FILTER:
                        shape = "{" # Diamond for decisions
                        end_shape = "}"
                    elif op.operation_type == OperationType.JOIN:
                        shape = "(" # Rounded for joins
                        end_shape = ")"
                    else:
                        shape = "[" # Rectangle for other ops
                        end_shape = "]"

                    lines.append(f"        {op_node}{shape}\"{label}\"{end_shape}")

                    # Connect to previous node
                    if prev_node:
                        lines.append(f"        {prev_node} --> {op_node}")

                    prev_node = op_node

                lines.append("    end")
                node_counter += 1

            # Add styling from centralized configuration
            lines.append("")
            # Add indented version of the style classes
            style_lines = generate_mermaid_style_classes().split('\n')
            for style_line in style_lines:
                lines.append(f"   {style_line}")  # Add indent for impact visualizer

            return "\n".join(lines)

        except Exception as e:
            raise VisualizationError(f"Failed to create impact Mermaid diagram: {e}")

    def create_impact_summary_table(self, lineage_graph: LineageGraph) -> str:
        """
        Create a text summary table of business impacts.

        Args:
            lineage_graph: The lineage graph to analyze

        Returns:
            Formatted text table
        """
        flows = self.analyze_business_flows(lineage_graph)

        lines = []
        lines.append("BUSINESS IMPACT SUMMARY")
        lines.append("=" * 80)

        for flow in flows:
            lines.append(f"\n {flow.concept_name}")
            lines.append("-" * len(flow.concept_name))

            if flow.concept_description:
                lines.append(f"   Description: {flow.concept_description}")

            if flow.initial_count is not None and flow.final_count is not None:
                lines.append(f"   Initial Records: {flow.initial_count:,}")
                lines.append(f"   Final Records:   {flow.final_count:,}")

                if flow.total_impact is not None:
                    change_sign = "+" if flow.total_impact >= 0 else ""
                    lines.append(f"   Total Impact:    {change_sign}{flow.total_impact:,}")

            lines.append("\n   Operations:")
            for i, op in enumerate(flow.operations, 1):
                lines.append(f"     {i}. {op.operation_name}")

                if op.filter_condition:
                    condition = self._clean_filter_condition(op.filter_condition)
                    lines.append(f"        Filter: {condition}")

                if op.output_count is not None:
                    lines.append(f"        Result: {op.output_count:,} records")

                    if op.count_change is not None:
                        change_sign = "+" if op.count_change >= 0 else ""
                        change_text = f"{change_sign}{op.count_change:,}"

                        if self.show_percentages and op.count_change_percentage is not None:
                            change_text += f" ({change_sign}{op.count_change_percentage:.1f}%)"

                        lines.append(f"        Impact: {change_text}")

                if self.show_execution_times and op.execution_time is not None:
                    lines.append(f"        Time:   {op.execution_time:.3f}s")

        return "\n".join(lines)

    def _find_concept_operations(
        self,
        concept: BusinessConceptNode,
        lineage_graph: LineageGraph
    ) -> List[OperationNode]:
        """Find all operations associated with a business concept."""
        operations = []

        # Find operations that are children of this concept
        for edge in lineage_graph.edges:
            if (edge.source_id == concept.node_id and
                edge.target_id in lineage_graph.nodes and
                isinstance(lineage_graph.nodes[edge.target_id], OperationNode)):
                operations.append(lineage_graph.nodes[edge.target_id])

        # Sort by creation time or node_id for consistent ordering
        operations.sort(key=lambda x: getattr(x, 'created_at', 0))

        return operations

    def _extract_operation_impact(self, operation: OperationNode) -> OperationImpact:
        """Extract impact information from an operation node."""
        # Get counts from metrics
        input_count = None
        output_count = None

        if hasattr(operation, 'input_metrics') and operation.input_metrics:
            input_count = getattr(operation.input_metrics, 'row_count', None)

        if hasattr(operation, 'output_metrics') and operation.output_metrics:
            output_count = getattr(operation.output_metrics, 'row_count', None)

        # Extract filter condition from metadata
        filter_condition = None
        if operation.operation_type == OperationType.FILTER:
            filter_condition = operation.metadata.get('filter_condition')
            if not filter_condition and operation.involved_columns:
                # Try to reconstruct from involved columns
                filter_condition = f"Filter on: {', '.join(operation.involved_columns)}"

        return OperationImpact(
            operation_name=operation.name,
            operation_type=operation.operation_type,
            input_count=input_count,
            output_count=output_count,
            filter_condition=filter_condition,
            columns_involved=operation.involved_columns or [],
            execution_time=getattr(operation, 'execution_time', None),
            business_context=operation.metadata.get('business_context')
        )

    def _get_initial_count(
        self,
        concept: BusinessConceptNode,
        operations: List[OperationNode]
    ) -> Optional[int]:
        """Get the initial record count for a business concept."""
        if operations and hasattr(operations[0], 'input_metrics') and operations[0].input_metrics:
            return getattr(operations[0].input_metrics, 'row_count', None)
        return None

    def _get_final_count(
        self,
        concept: BusinessConceptNode,
        operations: List[OperationNode]
    ) -> Optional[int]:
        """Get the final record count for a business concept."""
        if operations and hasattr(operations[-1], 'output_metrics') and operations[-1].output_metrics:
            return getattr(operations[-1].output_metrics, 'row_count', None)
        return None

    def _clean_filter_condition(self, condition: str) -> str:
        """Clean up filter condition for display."""
        if not condition:
            return "Unknown condition"

        # Remove common PySpark artifacts
        condition = condition.replace("Column<b'", "").replace("'>", "")
        condition = condition.replace("(col(", "").replace("))", ")")

        # Limit length for display
        if len(condition) > 50:
            condition = condition[:47] + "..."

        return condition