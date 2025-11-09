"""
Hierarchical Business Diagram - Visual representation of nested business concepts.

DEPRECATED: This module is deprecated as of version X.X.X and will be removed in a future release.
Use BusinessFlowDiagram instead, which now supports hierarchical grouping via group_by_context=True.

BusinessFlowDiagram provides the same hierarchical visualization while also showing:
- Complete data flow and lineage
- Operation details (columns created, transformations)
- Distribution analysis markers
- Describe profile checkpoints

For migration:
    Old: generate_hierarchical_diagram(graph, path)
    New: generate_business_diagram(graph, path, group_by_context=True)
"""

import logging
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..visualization.diagram_styles import (
    generate_mermaid_style_classes,
    get_mermaid_shape_template,
    get_node_class_name,
    get_node_style,
)
from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class HierarchicalDiagramConfig(ReportConfig):
    """
    Configuration for Hierarchical Business Diagram generation.

    DEPRECATED: Use BusinessFlowDiagramConfig instead.
    """
    show_metrics: bool = True
    show_execution_times: bool = True
    show_descriptions: bool = True
    orientation: str = "TD"  # "TD", "LR", "RL", "BT"
    max_depth: Optional[int] = None  # None = unlimited
    collapse_non_hierarchical: bool = False  # Whether to hide non-hierarchical nodes


class HierarchicalDiagram(BaseReport):
    """
    Generates Mermaid diagrams showing hierarchical business concept relationships.

    DEPRECATED: This class is deprecated. Use BusinessFlowDiagram instead.

    BusinessFlowDiagram now supports hierarchical grouping via group_by_context=True,
    providing the same hierarchical structure while also showing complete data flow
    and operation details.

    This diagram visualizes the parent-child relationships between business concepts
    created using businessConceptHierarchy. Nodes are arranged to show the hierarchy
    structure, with parent concepts containing their children.
    """

    def __init__(self, config: Optional[HierarchicalDiagramConfig] = None, **kwargs):
        """
        Initialize the Hierarchical Diagram generator.

        DEPRECATED: Use BusinessFlowDiagram instead.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        warnings.warn(
            "HierarchicalDiagram is deprecated and will be removed in a future release. "
            "Use BusinessFlowDiagram with group_by_context=True instead, which provides "
            "the same hierarchical visualization with additional data flow information.",
            DeprecationWarning,
            stacklevel=2
        )

        if config is None and kwargs:
            config = HierarchicalDiagramConfig(**kwargs)
        elif config is None:
            config = HierarchicalDiagramConfig()

        super().__init__(config)
        self.config: HierarchicalDiagramConfig = config

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        valid_orientations = ["TD", "LR", "RL", "BT"]
        if self.config.orientation not in valid_orientations:
            raise ValueError(
                f"Invalid orientation: {self.config.orientation}. "
                f"Must be one of {valid_orientations}"
            )

        return True

    def generate(self, lineage_graph: EnhancedLineageGraph, output_path: str) -> str:
        """
        Generate the hierarchical diagram and write to file.

        Args:
            lineage_graph: Enhanced lineage graph with hierarchy metadata
            output_path: Path where the diagram should be written

        Returns:
            Path to the generated diagram file
        """
        # Extract hierarchy information from graph
        hierarchy_tree = self._build_hierarchy_tree(lineage_graph)

        # Generate Mermaid diagram
        mermaid_diagram = self._generate_mermaid(hierarchy_tree, lineage_graph)

        # Generate statistics
        stats = self._generate_statistics(hierarchy_tree, lineage_graph)

        # Create markdown content
        content = self._build_markdown_content(mermaid_diagram, stats)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Generated hierarchical diagram: {output_path}")
        return str(output_path)

    def _build_hierarchy_tree(self, graph: EnhancedLineageGraph) -> Dict:
        """
        Build a tree structure from the hierarchy metadata in the graph.

        Extracts:
        1. Business concept nodes (with hierarchy metadata) to form the hierarchy structure
        2. All operation nodes to display within their parent concepts

        Returns:
            Dictionary representing the hierarchy tree with root nodes at top level
        """
        # Extract business concept nodes (nodes with hierarchy metadata)
        business_concepts = {}
        root_concept_ids = []

        # Extract all operation nodes (nodes with context_id pointing to a concept)
        operation_nodes = {}

        for node_id, node in graph.nodes.items():
            # Check if this is a business concept node (has hierarchy metadata)
            if 'hierarchy' in node.metadata:
                hierarchy = node.metadata['hierarchy']
                concept_info = {
                    'node_id': node_id,
                    'name': node.metadata.get('operation_name', node_id),
                    'description': node.metadata.get('operation_description', ''),
                    'parent_id': hierarchy.get('parent_context_id'),
                    'parent_name': hierarchy.get('parent_concept_name'),
                    'path': hierarchy.get('concept_path', ''),
                    'depth': hierarchy.get('depth', 0),
                    'is_root': hierarchy.get('is_root', False),
                    'child_concepts': [],  # Child business concepts
                    'operations': [],  # Operations belonging to this concept
                    'execution_time': node.metadata.get('timing', 0),
                    'metrics': node.metadata.get('metrics'),
                    'tracked_variables': node.metadata.get('tracked_variables', []),
                    'node': node,
                }
                business_concepts[node_id] = concept_info

                if concept_info['is_root']:
                    root_concept_ids.append(node_id)

            # Check if this is an operation node (has context_id)
            elif hasattr(node, 'context_id') and node.context_id:
                operation_nodes[node_id] = node

        # Build parent-child relationships for business concepts
        for node_id, concept_info in business_concepts.items():
            parent_id = concept_info['parent_id']
            if parent_id and parent_id in business_concepts:
                business_concepts[parent_id]['child_concepts'].append(node_id)

        # Associate operations with their parent business concepts
        for node_id, op_node in operation_nodes.items():
            context_id = op_node.context_id
            if context_id and context_id in business_concepts:
                business_concepts[context_id]['operations'].append(op_node)

        # Build tree structure
        tree = {
            'roots': root_concept_ids,
            'concepts': business_concepts,
            'operations': operation_nodes,
            'total_hierarchical_nodes': len(business_concepts),
            'total_root_concepts': len(root_concept_ids),
        }

        return tree

    def _generate_mermaid(self, hierarchy_tree: Dict, graph: EnhancedLineageGraph) -> str:
        """
        Generate Mermaid flowchart syntax for the hierarchy.

        Uses nested subgraphs to show:
        1. Hierarchical business concepts (parents contain children)
        2. All operations within each business concept
        """
        lines = []

        # Mermaid header with configuration
        lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '12px', 'clusterBkg': '#F5F5F5', 'clusterBorder': '#666'}, 'flowchart': {'nodeSpacing': 150, 'rankSpacing': 100, 'curve': 'basis', 'padding': 25, 'htmlLabels': true}}}%%")
        lines.append(f"flowchart {self.config.orientation}")

        concepts = hierarchy_tree['concepts']

        # Track node IDs for edge creation
        node_id_map = {}  # Maps node_id (graph) -> mermaid_id
        lineage_to_mermaid = {}  # Maps lineage_id -> mermaid_id
        node_counter = 1

        # Render hierarchy recursively
        for root_id in hierarchy_tree['roots']:
            self._render_concept_hierarchy(
                root_id, concepts, graph, lines, node_id_map,
                lineage_to_mermaid, node_counter, depth=0
            )
            node_counter += len(concepts[root_id]['operations'])
            # Count all descendants
            for child_id in self._get_all_descendants(root_id, concepts):
                node_counter += len(concepts[child_id]['operations'])

        # Add edges
        lines.append("")
        self._add_operation_edges(graph, node_id_map, lineage_to_mermaid, lines)

        # Add styling
        lines.append("")
        self._add_styling(lines, node_id_map, concepts, graph)

        return '\n'.join(lines)

    def _render_concept_hierarchy(
        self,
        concept_id: str,
        concepts: Dict,
        graph: EnhancedLineageGraph,
        lines: List[str],
        node_id_map: Dict[str, str],
        lineage_to_mermaid: Dict[str, str],
        node_counter: int,
        depth: int = 0
    ):
        """
        Recursively render a business concept and its:
        1. Operations (within this concept)
        2. Child concepts (nested subgraphs)

        Uses nested subgraphs for hierarchical containment.
        """
        if self.config.max_depth is not None and depth > self.config.max_depth:
            return

        concept_info = concepts[concept_id]
        concept_mermaid_id = self._get_concept_mermaid_id(concept_id)
        indent = " " * (depth * 2)

        # Get concept details
        concept_name = concept_info['name']
        tracked_vars = concept_info.get('tracked_variables', [])

        # Build subgraph label
        if tracked_vars:
            subgraph_label = f"{concept_name}\\nTracking: {', '.join(tracked_vars[:3])}"
            if len(tracked_vars) > 3:
                subgraph_label += f", +{len(tracked_vars) - 3} more"
        else:
            subgraph_label = concept_name

        # Start subgraph for this concept
        lines.append(f"{indent}subgraph {concept_mermaid_id}[\"{subgraph_label}\"]")

        # Render operations within this concept
        for op_node in concept_info['operations']:
            mermaid_id = f"Op_{node_counter}"
            node_id_map[op_node.node_id] = mermaid_id
            lineage_to_mermaid[op_node.lineage_id] = mermaid_id
            node_counter += 1

            node_shape = self._get_operation_node_shape(op_node)
            lines.append(f"{indent}  {mermaid_id}{node_shape}")

        # Recursively render child concepts (nested subgraphs)
        for child_id in concept_info['child_concepts']:
            lines.append("")  # Blank line before nested subgraph
            self._render_concept_hierarchy(
                child_id, concepts, graph, lines, node_id_map,
                lineage_to_mermaid, node_counter, depth + 1
            )
            # Update counter after rendering child
            for child_op in concepts[child_id]['operations']:
                node_counter += 1

        lines.append(f"{indent}end")
        lines.append("")  # Blank line after subgraph

    def _get_node_mermaid_id(self, node_id: str) -> str:
        """Generate a valid Mermaid ID from a node ID."""
        # Replace any characters that might cause issues in Mermaid
        safe_id = node_id.replace('-', '_').replace('.', '_')
        return f"HC_{safe_id}"

    def _get_concept_mermaid_id(self, concept_id: str) -> str:
        """Generate a valid Mermaid ID for a business concept."""
        safe_id = concept_id.replace('-', '_').replace('.', '_')
        return f"BC_{safe_id}"

    def _get_all_descendants(self, concept_id: str, concepts: Dict) -> List[str]:
        """Get all descendant concept IDs recursively."""
        descendants = []
        concept = concepts.get(concept_id)
        if concept:
            for child_id in concept['child_concepts']:
                descendants.append(child_id)
                descendants.extend(self._get_all_descendants(child_id, concepts))
        return descendants

    def _get_operation_node_shape(self, op_node) -> str:
        """
        Generate the Mermaid node shape and content for an operation node using centralized styles.

        Returns Mermaid syntax like: [\"content\"] or {{\"content\"}} based on node type
        """
        # Get operation details
        op_name = op_node.metadata.get('operation_name', 'Operation')
        op_desc = op_node.metadata.get('description', '')
        op_type = op_node.metadata.get('operation_type', 'operation')
        execution_time = op_node.metadata.get('execution_time', 0)

        # Build content parts
        parts = [f"**{op_name}**"]

        if op_desc:
            parts.append(f"<br/><u>{op_desc}</u>")

        # Add metrics if available
        if hasattr(op_node, 'metrics') and op_node.metrics:
            metrics = op_node.metrics
            if hasattr(metrics, 'row_count') and metrics.row_count is not None:
                parts.append(f"<br/>[CHART] {metrics.row_count:,} rows")

        # Add execution time if available
        if self.config.show_execution_times and execution_time > 0:
            parts.append(f"<br/> {execution_time:.3f}s")

        content = ''.join(parts)

        # Get shape template from centralized styles
        template = get_mermaid_shape_template(op_type)
        return template.replace('{content}', content)

    def _add_operation_edges(
        self,
        graph: EnhancedLineageGraph,
        node_id_map: Dict[str, str],
        lineage_to_mermaid: Dict[str, str],
        lines: List[str]
    ):
        """
        Add edges showing data flow between operation nodes.

        Args:
            graph: Enhanced Lineage Graph with edges
            node_id_map: Mapping from node_id to mermaid_id
            lineage_to_mermaid: Mapping from lineage_id to mermaid_id
            lines: List to append edge lines to
        """
        added_edges = set()

        for edge in graph.edges:
            # Try both node_id and lineage_id mappings
            source_mermaid_id = lineage_to_mermaid.get(edge.source_id) or node_id_map.get(edge.source_id)
            target_mermaid_id = lineage_to_mermaid.get(edge.target_id) or node_id_map.get(edge.target_id)

            if source_mermaid_id and target_mermaid_id:
                edge_key = (source_mermaid_id, target_mermaid_id)

                if edge_key not in added_edges:
                    # Determine edge style based on metadata
                    is_fork = edge.metadata.get('is_fork', False) if edge.metadata else False

                    if is_fork:
                        lines.append(f" {source_mermaid_id} ==> {target_mermaid_id}")
                    else:
                        lines.append(f" {source_mermaid_id} --> {target_mermaid_id}")

                    added_edges.add(edge_key)

    def _add_styling(
        self,
        lines: List[str],
        node_id_map: Dict[str, str],
        concepts: Dict,
        graph: EnhancedLineageGraph
    ):
        """Add Mermaid styling for nodes based on operation type using centralized styles."""
        # Define styles from centralized configuration
        lines.append("")
        lines.append(generate_mermaid_style_classes())

        # Apply styles to nodes based on operation type
        lines.append("")
        for node_id, mermaid_id in node_id_map.items():
            # Find the node in the graph
            node = graph.nodes.get(node_id)
            if node:
                op_type = node.metadata.get('operation_type', 'operation')
                class_name = get_node_class_name(op_type)
                lines.append(f" class {mermaid_id} {class_name}")

    def _format_node_content(self, node_info: Dict) -> str:
        """
        Format the content displayed in a node.

        Returns Mermaid-formatted string with name, description, metrics, etc.
        """
        parts = []

        # Name (always show)
        parts.append(f"**{node_info['name']}**")

        # Description (if enabled and available)
        if self.config.show_descriptions and node_info['description']:
            parts.append(f"<br/><i>{node_info['description']}</i>")

        # Execution time (if enabled and available)
        if self.config.show_execution_times and node_info['execution_time']:
            exec_time = node_info['execution_time']
            if exec_time >= 1:
                parts.append(f"<br/>[TIMER] {exec_time:.2f}s")
            else:
                parts.append(f"<br/>[TIMER] {exec_time*1000:.0f}ms")

        # Metrics (if enabled and available)
        if self.config.show_metrics and node_info['metrics']:
            metrics = node_info['metrics']
            if hasattr(metrics, 'row_count') and metrics.row_count is not None:
                parts.append(f"<br/>[CHART] {metrics.row_count:,} rows")

            # Add distinct counts for tracked variables if available
            if hasattr(metrics, 'distinct_counts') and metrics.distinct_counts:
                for var_name, count in metrics.distinct_counts.items():
                    if count is not None:
                        parts.append(f"<br/>🔢 {var_name}: {count:,} distinct")

        # Tracked variables (if available and different from metrics)
        if node_info.get('tracked_variables'):
            tracked_vars = node_info['tracked_variables']
            if isinstance(tracked_vars, list) and tracked_vars:
                vars_str = ', '.join(tracked_vars[:3])  # Limit to first 3
                if len(tracked_vars) > 3:
                    vars_str += f", +{len(tracked_vars) - 3} more"
                parts.append(f"<br/>[REPORT] Tracking: {vars_str}")

        # Depth indicator
        if node_info['depth'] > 0:
            parts.append(f"<br/>📍 Level {node_info['depth']}")

        content = ''.join(parts)
        return f'"{content}"'

    def _generate_statistics(self, hierarchy_tree: Dict, graph: EnhancedLineageGraph) -> Dict:
        """Generate statistics about the hierarchy."""
        concepts = hierarchy_tree['concepts']

        # Calculate depth statistics
        depths = [concept['depth'] for concept in concepts.values()]
        max_depth = max(depths) if depths else 0
        avg_depth = sum(depths) / len(depths) if depths else 0

        # Count concepts at each depth
        depth_distribution = {}
        for depth in depths:
            depth_distribution[depth] = depth_distribution.get(depth, 0) + 1

        # Calculate children statistics
        child_counts = [len(concept['child_concepts']) for concept in concepts.values()]
        max_children = max(child_counts) if child_counts else 0
        avg_children = sum(child_counts) / len(child_counts) if child_counts else 0

        # Count total operations
        total_operations = sum(len(concept['operations']) for concept in concepts.values())

        # Count non-hierarchical nodes (operations not assigned to concepts)
        non_hierarchical_count = len(hierarchy_tree['operations']) - total_operations

        stats = {
            'total_hierarchical_nodes': hierarchy_tree['total_hierarchical_nodes'],
            'total_root_concepts': hierarchy_tree['total_root_concepts'],
            'max_depth': max_depth,
            'avg_depth': avg_depth,
            'depth_distribution': depth_distribution,
            'max_children_per_node': max_children,
            'avg_children_per_node': avg_children,
            'total_graph_nodes': len(graph.nodes),
            'total_operations': total_operations,
            'non_hierarchical_count': non_hierarchical_count,
        }

        return stats

    def _build_markdown_content(self, mermaid_diagram: str, stats: Dict) -> str:
        """Build the complete markdown document."""
        lines = []

        # Title
        lines.append("# Hierarchical Business Concept Diagram")
        lines.append("")
        lines.append("*Visual representation of nested business concept relationships*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Introduction
        lines.append("## Overview")
        lines.append("")
        lines.append("This diagram shows the complete lineage with operations grouped by hierarchical business concepts.")
        lines.append("Parent concepts are shown as containers with their child concepts and operations nested inside.")
        lines.append("")

        # Legend
        lines.append("### Legend")
        lines.append("")
        lines.append("**Node Types:**")
        # Get standardized legend items
        from ..visualization.diagram_styles import get_legend_items
        legend_items = get_legend_items()
        for emoji, name, description in legend_items:
            lines.append(f"- {emoji} **{name}**: {description}")
        lines.append("")
        lines.append("**Hierarchy:**")
        lines.append("- Subgraphs show business concept containment")
        lines.append("- Operations are grouped within their parent concepts")
        if self.config.show_execution_times:
            lines.append("- [TIMER] **Execution Time** - Time taken to execute each operation")
        if self.config.show_metrics:
            lines.append("- [CHART] **Row Count** - Number of rows after each operation")
        lines.append("")

        # Statistics
        lines.append("## Hierarchy Statistics")
        lines.append("")
        lines.append(f"- **Total Business Concepts:** {stats['total_hierarchical_nodes']}")
        lines.append(f"- **Root Concepts:** {stats['total_root_concepts']}")
        lines.append(f"- **Total Operations:** {stats['total_operations']}")
        lines.append(f"- **Total Nodes in Diagram:** {stats['total_operations']}")
        lines.append(f"- **Maximum Depth:** {stats['max_depth']} levels")
        lines.append(f"- **Average Depth:** {stats['avg_depth']:.1f} levels")
        lines.append(f"- **Maximum Children per Concept:** {stats['max_children_per_node']}")
        lines.append(f"- **Average Children per Concept:** {stats['avg_children_per_node']:.1f}")

        if stats['depth_distribution']:
            lines.append("")
            lines.append("### Concepts by Depth Level")
            lines.append("")
            for depth in sorted(stats['depth_distribution'].keys()):
                count = stats['depth_distribution'][depth]
                level_name = "Root" if depth == 0 else f"Level {depth}"
                lines.append(f"- **{level_name}:** {count} concept(s)")

        if stats.get('non_hierarchical_count', 0) > 0:
            lines.append("")
            lines.append(f"*Note: {stats['non_hierarchical_count']} operation nodes not assigned to any business concept are not shown.*")

        lines.append("")

        # Diagram
        lines.append("## Hierarchy Diagram")
        lines.append("")
        lines.append("```mermaid")
        lines.append(mermaid_diagram)
        lines.append("```")
        lines.append("")

        return '\n'.join(lines)


def generate_hierarchical_diagram(
    graph: EnhancedLineageGraph,
    output_path: str,
    show_metrics: bool = True,
    show_execution_times: bool = True,
    show_descriptions: bool = True,
    orientation: str = "TD",
    max_depth: Optional[int] = None,
) -> str:
    """
    Convenience function to generate a hierarchical business concept diagram.

    DEPRECATED: Use generate_business_diagram() instead with group_by_context=True.

    BusinessFlowDiagram provides the same hierarchical visualization while also
    showing complete data flow, operation details, and lineage connections.

    Args:
        graph: Enhanced lineage graph with hierarchy metadata
        output_path: Path where the diagram should be written
        show_metrics: Whether to show metrics (row counts, etc.)
        show_execution_times: Whether to show execution times
        show_descriptions: Whether to show concept descriptions
        orientation: Diagram orientation ("TD", "LR", "RL", "BT")
        max_depth: Maximum depth to display (None = unlimited)

    Returns:
        Path to the generated diagram file

    Example (Deprecated):
        >>> from pyspark_storydoc.reporting import generate_hierarchical_diagram
        >>> generate_hierarchical_diagram(graph, "hierarchy.md")

    Example (Recommended):
        >>> from pyspark_storydoc.reporting import generate_business_diagram
        >>> generate_business_diagram(graph, "flow.md", group_by_context=True)
    """
    warnings.warn(
        "generate_hierarchical_diagram() is deprecated and will be removed in a future release. "
        "Use generate_business_diagram() with group_by_context=True instead, which provides "
        "the same hierarchical visualization with additional data flow information.",
        DeprecationWarning,
        stacklevel=2
    )

    config = HierarchicalDiagramConfig(
        show_metrics=show_metrics,
        show_execution_times=show_execution_times,
        show_descriptions=show_descriptions,
        orientation=orientation,
        max_depth=max_depth,
    )

    diagram = HierarchicalDiagram(config)
    return diagram.generate(graph, output_path)
