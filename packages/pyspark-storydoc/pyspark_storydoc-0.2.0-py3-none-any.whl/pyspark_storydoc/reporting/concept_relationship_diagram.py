"""
Concept Relationship Diagram - Shows only business concepts and their relationships.

This diagram provides a high-level view of how business concepts relate to each other,
without showing the detailed operations. Hierarchical concepts are nested as subgraphs.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..visualization.diagram_styles import generate_mermaid_style_classes
from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class ConceptRelationshipConfig(ReportConfig):
    """Configuration for Concept Relationship Diagram generation."""
    show_metrics: bool = True
    show_execution_times: bool = False
    orientation: str = "TD"  # "TD", "LR", "RL", "BT"
    max_depth: Optional[int] = None  # None = unlimited


class ConceptRelationshipDiagram(BaseReport):
    """
    Generates Mermaid diagrams showing business concept relationships.

    This diagram shows:
    1. Only business concepts (no operation nodes)
    2. Relationships between concepts based on data flow
    3. Nested subgraphs for hierarchical concepts
    """

    def __init__(self, config: Optional[ConceptRelationshipConfig] = None, **kwargs):
        """
        Initialize the Concept Relationship Diagram generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = ConceptRelationshipConfig(**kwargs)
        elif config is None:
            config = ConceptRelationshipConfig()

        super().__init__(config)
        self.config: ConceptRelationshipConfig = config

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
        Generate the concept relationship diagram and write to file.

        Args:
            lineage_graph: Enhanced lineage graph with hierarchy metadata
            output_path: Path where the diagram should be written

        Returns:
            Path to the generated diagram file
        """
        # Extract business concepts, sources, and their relationships
        concepts, relationships, sources = self._extract_concepts_and_relationships(lineage_graph)

        if not concepts:
            logger.warning("No business concepts found in lineage graph")
            # Still generate a basic report
            concepts = {}
            relationships = []
            sources = {}

        # Build hierarchy structure
        hierarchy = self._build_hierarchy_structure(concepts)

        # Generate Mermaid diagram
        mermaid_diagram = self._generate_mermaid(concepts, relationships, hierarchy, sources)

        # Generate statistics
        stats = self._generate_statistics(concepts, relationships, hierarchy, sources)

        # Create markdown content
        content = self._build_markdown_content(mermaid_diagram, stats, concepts, relationships, sources)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Generated concept relationship diagram: {output_path}")
        return str(output_path)

    def _extract_concepts_and_relationships(
        self, graph: EnhancedLineageGraph
    ) -> Tuple[Dict, List[Tuple[str, str]], Dict]:
        """
        Extract business concepts, source nodes, and determine relationships.

        A relationship exists between two concepts if:
        - There is a data flow from operations in one concept to operations in another

        Returns:
            Tuple of (concepts dict, relationships list, sources dict)
            - concepts: {concept_id: concept_info}
            - relationships: [(source_id, target_id), ...]
            - sources: {source_id: source_info}
        """
        concepts = {}
        concept_operations = {}  # Maps concept_id -> list of operation node_ids
        sources = {}  # Maps source_id -> source_info

        # Extract business concepts from context_nodes
        for context_id, nodes in graph.context_nodes.items():
            for node in nodes:
                if hasattr(node, 'metadata'):
                    # Check if this is a business concept node
                    business_context = node.metadata.get('business_context')
                    if business_context:
                        # Extract concept information
                        hierarchy = node.metadata.get('hierarchy', {})

                        concept_info = {
                            'concept_id': context_id,
                            'name': business_context,
                            'description': node.metadata.get('description', ''),
                            'parent_id': hierarchy.get('parent_context_id'),
                            'parent_name': hierarchy.get('parent_concept_name'),
                            'path': hierarchy.get('concept_path', ''),
                            'depth': hierarchy.get('depth', 0),
                            'is_root': hierarchy.get('is_root', True),
                            'hierarchical': bool(hierarchy),
                            'execution_time': node.metadata.get('execution_time', 0),
                            'operations': [],
                            'node': node,
                        }

                        # Add metrics if available
                        if hasattr(node, 'output_metrics'):
                            concept_info['output_metrics'] = node.output_metrics

                        concepts[context_id] = concept_info
                        concept_operations[context_id] = []
                        break  # Only need one node per concept

        # Map operations to their concepts and extract source nodes
        for node_id, node in graph.nodes.items():
            # Check if this is a source node
            if hasattr(node, 'metadata'):
                op_type = node.metadata.get('operation_type', '')
                if op_type == 'source':
                    # Extract source information
                    # Try multiple metadata fields for source name
                    source_name = (
                        node.metadata.get('source_name') or
                        node.metadata.get('business_label') or
                        node.metadata.get('operation_name') or
                        'Unknown Source'
                    )

                    # If still unknown, try to extract from node_id (format: source_<label>)
                    if source_name == 'Unknown Source' and node_id.startswith('source_'):
                        # Extract label from node_id
                        source_name = node_id[7:]  # Remove 'source_' prefix

                    table_name = node.metadata.get('table_name')
                    file_path = node.metadata.get('file_path')

                    # Determine display name
                    if table_name:
                        display_name = table_name
                    elif file_path:
                        # Extract filename from path
                        from pathlib import Path
                        display_name = Path(file_path).name
                    else:
                        display_name = source_name

                    sources[node_id] = {
                        'node_id': node_id,
                        'name': display_name,
                        'source_name': source_name,
                        'table_name': table_name,
                        'file_path': file_path,
                        'node': node
                    }

            # Map to concepts
            if hasattr(node, 'context_id') and node.context_id:
                context_id = node.context_id
                if context_id in concept_operations:
                    concept_operations[context_id].append(node_id)
                    if context_id in concepts:
                        concepts[context_id]['operations'].append(node)

        # Determine relationships between concepts based on data flow
        relationships = set()

        # Helper function to check if one concept is parent/ancestor of another
        def is_parent_child(concept_id_a, concept_id_b, concepts):
            """
            Check if concept_a is an ancestor of concept_b or vice versa.

            Returns False for sibling relationships (same parent, same level).
            This allows edges between siblings to be shown in the diagram.
            """
            # Check if A is parent of B
            concept_b = concepts.get(concept_id_b, {})
            current_parent = concept_b.get('parent_id')
            while current_parent:
                if current_parent == concept_id_a:
                    return True
                current_parent = concepts.get(current_parent, {}).get('parent_id')

            # Check if B is parent of A
            concept_a = concepts.get(concept_id_a, {})
            current_parent = concept_a.get('parent_id')
            while current_parent:
                if current_parent == concept_id_b:
                    return True
                current_parent = concepts.get(current_parent, {}).get('parent_id')

            return False

        for edge in graph.edges:
            # Try to find source and target nodes using both node_id and lineage_id
            source_node = graph.nodes.get(edge.source_id)
            target_node = graph.nodes.get(edge.target_id)

            # If not found by node_id, try lineage_id
            if not source_node:
                for node_id, node in graph.nodes.items():
                    if hasattr(node, 'lineage_id') and node.lineage_id == edge.source_id:
                        source_node = node
                        break

            if not target_node:
                for node_id, node in graph.nodes.items():
                    if hasattr(node, 'lineage_id') and node.lineage_id == edge.target_id:
                        target_node = node
                        break

            if source_node and target_node:
                source_concept_id = getattr(source_node, 'context_id', None)
                target_concept_id = getattr(target_node, 'context_id', None)

                # Check if source is a source node
                source_is_source = edge.source_id in sources

                if source_is_source:
                    # Source node to concept relationship
                    if target_concept_id and target_concept_id in concepts:
                        relationships.add((edge.source_id, target_concept_id))
                else:
                    # Create relationship if:
                    # 1. Both concepts exist
                    # 2. Concepts are different
                    # 3. They are NOT in a parent-child relationship (we show that via nesting)
                    if (source_concept_id and target_concept_id and
                        source_concept_id != target_concept_id and
                        source_concept_id in concepts and
                        target_concept_id in concepts and
                        not is_parent_child(source_concept_id, target_concept_id, concepts)):

                        relationships.add((source_concept_id, target_concept_id))

        return concepts, list(relationships), sources

    def _build_hierarchy_structure(self, concepts: Dict) -> Dict:
        """
        Build hierarchical structure from concepts.

        Returns:
            {
                'roots': [list of root concept IDs],
                'parent_to_children': {parent_id: [child_ids]},
                'has_hierarchy': bool
            }
        """
        roots = []
        parent_to_children = {}
        has_hierarchy = False

        for concept_id, concept in concepts.items():
            # Check if this is a root concept
            if concept.get('is_root', True) and not concept.get('parent_id'):
                roots.append(concept_id)

            # Build parent-child mapping
            parent_id = concept.get('parent_id')
            if parent_id:
                has_hierarchy = True
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(concept_id)

        # If no explicit roots found, treat all concepts without parents as roots
        if not roots:
            roots = [cid for cid, c in concepts.items() if not c.get('parent_id')]

        return {
            'roots': roots,
            'parent_to_children': parent_to_children,
            'has_hierarchy': has_hierarchy
        }

    def _generate_mermaid(
        self, concepts: Dict, relationships: List[Tuple[str, str]], hierarchy: Dict, sources: Dict
    ) -> str:
        """
        Generate Mermaid flowchart syntax for concept relationships.

        Uses nested subgraphs for hierarchical concepts.
        Includes source nodes at the beginning.
        """
        lines = []

        # Mermaid header
        lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '14px', 'clusterBkg': '#F9F9F9', 'clusterBorder': '#666'}, 'flowchart': {'nodeSpacing': 100, 'rankSpacing': 150, 'curve': 'basis', 'padding': 20, 'htmlLabels': true}}}%%")
        lines.append(f"flowchart {self.config.orientation}")
        lines.append("")

        # Track mermaid IDs for each node (concepts and sources)
        concept_to_mermaid = {}
        source_to_mermaid = {}

        # Render source nodes first
        if sources:
            lines.append("%% Source Data")
            for source_id, source in sources.items():
                mermaid_id = self._safe_id(source_id)
                source_to_mermaid[source_id] = mermaid_id
                source_name = source['name']
                lines.append(f"  {mermaid_id}[(\"{source_name}\")]")
            lines.append("")

        # Render concepts hierarchically if hierarchy exists
        if hierarchy['has_hierarchy']:
            for root_id in hierarchy['roots']:
                self._render_concept_node_hierarchy(
                    root_id, concepts, hierarchy, lines, concept_to_mermaid, depth=0
                )
        else:
            # Flat structure - render all concepts at root level
            for concept_id, concept in concepts.items():
                mermaid_id = self._safe_id(concept_id)
                concept_to_mermaid[concept_id] = mermaid_id
                node_content = self._format_concept_node(concept)
                lines.append(f"  {mermaid_id}{node_content}")

        # Add relationships (edges between sources and concepts, and between concepts)
        lines.append("")
        lines.append("%% Relationships")
        for source_id, target_id in relationships:
            # Check if source is a source node or concept
            source_mermaid = source_to_mermaid.get(source_id) or concept_to_mermaid.get(source_id)
            target_mermaid = concept_to_mermaid.get(target_id)

            if source_mermaid and target_mermaid:
                lines.append(f"  {source_mermaid} --> {target_mermaid}")

        # Add styling
        lines.append("")
        self._add_styling(lines, concepts, concept_to_mermaid, source_to_mermaid)

        return '\n'.join(lines)

    def _render_concept_node_hierarchy(
        self,
        concept_id: str,
        concepts: Dict,
        hierarchy: Dict,
        lines: List[str],
        concept_to_mermaid: Dict,
        depth: int = 0
    ):
        """
        Recursively render a concept and its children as nested subgraphs.

        Args:
            concept_id: ID of the concept to render
            concepts: Dictionary of all concepts
            hierarchy: Hierarchy structure
            lines: List to append Mermaid syntax to
            concept_to_mermaid: Mapping from concept_id to mermaid_id
            depth: Current nesting depth
        """
        if self.config.max_depth is not None and depth > self.config.max_depth:
            return

        if concept_id not in concepts:
            return

        concept = concepts[concept_id]
        indent = "  " * depth

        # Check if this concept has children
        children = hierarchy['parent_to_children'].get(concept_id, [])

        if children:
            # This concept has children - render as subgraph
            subgraph_id = f"cluster_{self._safe_id(concept_id)}"
            subgraph_label = concept['name']

            lines.append(f"{indent}subgraph {subgraph_id}[\"{subgraph_label}\"]")

            # Create a node for this concept within its own subgraph
            mermaid_id = self._safe_id(concept_id)
            concept_to_mermaid[concept_id] = mermaid_id
            node_content = self._format_concept_node(concept)
            lines.append(f"{indent}  {mermaid_id}{node_content}")

            # Recursively render children
            for child_id in children:
                lines.append("")
                self._render_concept_node_hierarchy(
                    child_id, concepts, hierarchy, lines, concept_to_mermaid, depth + 1
                )

            lines.append(f"{indent}end")
            lines.append("")
        else:
            # Leaf concept - render as simple node
            mermaid_id = self._safe_id(concept_id)
            concept_to_mermaid[concept_id] = mermaid_id
            node_content = self._format_concept_node(concept)
            lines.append(f"{indent}  {mermaid_id}{node_content}")

    def _format_concept_node(self, concept: Dict) -> str:
        """
        Format a concept node for Mermaid diagram.

        Returns Mermaid node syntax like: ["content"]
        """
        parts = []

        # Concept name (bold)
        parts.append(f"**{concept['name']}**")

        # Description (if available and short)
        if concept.get('description'):
            desc = concept['description']
            if len(desc) <= 50:
                parts.append(f"<br/><i>{desc}</i>")

        # Metrics (if enabled and available)
        if self.config.show_metrics:
            output_metrics = concept.get('output_metrics')
            if output_metrics and hasattr(output_metrics, 'row_count'):
                if output_metrics.row_count is not None:
                    parts.append(f"<br/>[CHART] {output_metrics.row_count:,} rows")

            # Show distinct counts for tracked columns
            if output_metrics and hasattr(output_metrics, 'distinct_counts'):
                distinct_counts = output_metrics.distinct_counts
                if distinct_counts:
                    for col_name, count in list(distinct_counts.items())[:2]:  # Max 2 columns
                        if count is not None:
                            parts.append(f"<br/>🔢 {col_name}: {count:,}")

        # Execution time (if enabled)
        if self.config.show_execution_times and concept.get('execution_time', 0) > 0:
            exec_time = concept['execution_time']
            if exec_time >= 1:
                parts.append(f"<br/>[TIMER] {exec_time:.2f}s")
            else:
                parts.append(f"<br/>[TIMER] {exec_time*1000:.0f}ms")

        content = ''.join(parts)
        return f'["{content}"]'

    def _safe_id(self, concept_id: str) -> str:
        """Generate a safe Mermaid ID from concept ID."""
        safe = concept_id.replace('-', '_').replace('.', '_').replace(':', '_').replace(' ', '_')
        return f"C_{safe}"

    def _add_styling(self, lines: List[str], concepts: Dict, concept_to_mermaid: Dict, source_to_mermaid: Dict):
        """Add Mermaid styling for concept and source nodes."""
        lines.append("%% Styling")

        # Define node styles
        lines.append("classDef conceptStyle fill:#E3F2FD,stroke:#1976D2,stroke-width:2px,color:#000")
        lines.append("classDef rootConceptStyle fill:#C5E1A5,stroke:#558B2F,stroke-width:3px,color:#000")
        lines.append("classDef hierarchicalStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000")
        lines.append("classDef sourceStyle fill:#B3E5FC,stroke:#01579B,stroke-width:2px,color:#000")

        # Apply styles to concepts
        lines.append("")
        for concept_id, mermaid_id in concept_to_mermaid.items():
            concept = concepts.get(concept_id)
            if concept:
                if concept.get('is_root', False):
                    lines.append(f"class {mermaid_id} rootConceptStyle")
                elif concept.get('hierarchical', False):
                    lines.append(f"class {mermaid_id} hierarchicalStyle")
                else:
                    lines.append(f"class {mermaid_id} conceptStyle")

        # Apply styles to sources
        for source_id, mermaid_id in source_to_mermaid.items():
            lines.append(f"class {mermaid_id} sourceStyle")

    def _generate_statistics(
        self, concepts: Dict, relationships: List[Tuple[str, str]], hierarchy: Dict, sources: Dict
    ) -> Dict:
        """Generate statistics about concepts, sources, and relationships."""

        # Count concepts by type
        total_concepts = len(concepts)
        root_concepts = len(hierarchy['roots'])
        hierarchical_concepts = sum(1 for c in concepts.values() if c.get('hierarchical', False))
        flat_concepts = total_concepts - hierarchical_concepts

        # Count sources
        total_sources = len(sources)

        # Calculate depth statistics
        depths = [c.get('depth', 0) for c in concepts.values()]
        max_depth = max(depths) if depths else 0

        # Calculate relationship statistics
        total_relationships = len(relationships)

        # Find most connected concepts
        incoming = {}
        outgoing = {}
        for source, target in relationships:
            outgoing[source] = outgoing.get(source, 0) + 1
            incoming[target] = incoming.get(target, 0) + 1

        most_outgoing = max(outgoing.values()) if outgoing else 0
        most_incoming = max(incoming.values()) if incoming else 0

        return {
            'total_concepts': total_concepts,
            'root_concepts': root_concepts,
            'hierarchical_concepts': hierarchical_concepts,
            'flat_concepts': flat_concepts,
            'max_depth': max_depth,
            'total_sources': total_sources,
            'total_relationships': total_relationships,
            'most_outgoing_connections': most_outgoing,
            'most_incoming_connections': most_incoming,
            'has_hierarchy': hierarchy['has_hierarchy'],
        }

    def _build_markdown_content(
        self, mermaid_diagram: str, stats: Dict, concepts: Dict, relationships: List, sources: Dict
    ) -> str:
        """Build the complete markdown document."""
        lines = []

        # Title
        lines.append("# Business Concept Relationship Diagram")
        lines.append("")
        lines.append("*High-level view of business concept relationships*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Introduction
        lines.append("## Overview")
        lines.append("")
        lines.append("This diagram shows business concepts, their data sources, and how they relate through data flow.")
        lines.append("Hierarchical concepts are shown as nested containers. Individual operations are not displayed.")
        lines.append("")

        # Legend
        lines.append("### Legend")
        lines.append("")
        lines.append("**Node Types:**")
        lines.append("- [BLUE] **Source** - Data source (table or file)")
        lines.append("- [GREEN] **Root Concept** - Top-level business concept (green)")
        lines.append("- [YELLOW] **Hierarchical Concept** - Nested concept within a parent (yellow)")
        lines.append("- 🔷 **Flat Concept** - Independent concept without hierarchy (blue)")
        lines.append("")
        lines.append("**Relationships:**")
        lines.append("- `A --> B` - Data flows from A to B")
        lines.append("")

        # Statistics
        lines.append("## Statistics")
        lines.append("")
        lines.append(f"- **Data Sources:** {stats['total_sources']}")
        lines.append(f"- **Total Business Concepts:** {stats['total_concepts']}")
        lines.append(f"- **Root Concepts:** {stats['root_concepts']}")

        if stats['has_hierarchy']:
            lines.append(f"- **Hierarchical Concepts:** {stats['hierarchical_concepts']}")
            lines.append(f"- **Flat Concepts:** {stats['flat_concepts']}")
            lines.append(f"- **Maximum Nesting Depth:** {stats['max_depth']} levels")

        lines.append(f"- **Total Relationships:** {stats['total_relationships']}")

        if stats['total_relationships'] > 0:
            lines.append(f"- **Most Outgoing Connections:** {stats['most_outgoing_connections']}")
            lines.append(f"- **Most Incoming Connections:** {stats['most_incoming_connections']}")

        lines.append("")

        # Concept list
        if concepts:
            lines.append("## Concepts in Diagram")
            lines.append("")
            for concept_id, concept in sorted(concepts.items(), key=lambda x: (x[1].get('depth', 0), x[1]['name'])):
                depth_indicator = "  " * concept.get('depth', 0)
                lines.append(f"{depth_indicator}- **{concept['name']}**")
                if concept.get('description'):
                    lines.append(f"{depth_indicator}  _{concept['description']}_")
            lines.append("")

        # Diagram
        lines.append("## Concept Relationship Diagram")
        lines.append("")
        lines.append("```mermaid")
        lines.append(mermaid_diagram)
        lines.append("```")
        lines.append("")

        return '\n'.join(lines)


def generate_concept_relationship_diagram(
    graph: EnhancedLineageGraph,
    output_path: str,
    show_metrics: bool = True,
    show_execution_times: bool = False,
    orientation: str = "TD",
    max_depth: Optional[int] = None,
) -> str:
    """
    Convenience function to generate a concept relationship diagram.

    This diagram shows only business concepts and their relationships,
    without displaying individual operation nodes. Hierarchical concepts
    are displayed as nested subgraphs.

    Args:
        graph: Enhanced lineage graph with business concepts
        output_path: Path where the diagram should be written
        show_metrics: Whether to show metrics (row counts, etc.)
        show_execution_times: Whether to show execution times
        orientation: Diagram orientation ("TD", "LR", "RL", "BT")
        max_depth: Maximum depth to display (None = unlimited)

    Returns:
        Path to the generated diagram file

    Example:
        >>> from pyspark_storydoc.reporting import generate_concept_relationship_diagram
        >>> from pyspark_storydoc.core.lineage_tracker import get_global_tracker
        >>>
        >>> tracker = get_global_tracker()
        >>> graph = tracker.get_lineage_graph()
        >>> generate_concept_relationship_diagram(
        ...     graph,
        ...     "concept_relationships.md",
        ...     show_metrics=True
        ... )
    """
    config = ConceptRelationshipConfig(
        show_metrics=show_metrics,
        show_execution_times=show_execution_times,
        orientation=orientation,
        max_depth=max_depth,
    )

    diagram = ConceptRelationshipDiagram(config)
    return diagram.generate(graph, output_path)
