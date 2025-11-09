"""Business Concept Catalog - Textual documentation of business concepts."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.expression_utils import expand_expression
from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class BusinessConceptCatalogConfig(ReportConfig):
    """Configuration for Business Concept Catalog generation."""
    include_metrics: bool = True
    include_execution_times: bool = False  # Show in overview only, not per-concept
    include_operations: bool = True
    include_filter_conditions: bool = True  # Always show the business logic
    max_condition_length: int = 200  # Increased to show more of the logic
    sort_by: str = "execution_order"  # "execution_order", "name", "execution_time"
    show_quality_metrics: bool = True
    show_data_flow_summary: bool = True
    show_expanded_expressions: bool = False  # Show fully expanded expressions for reassignments
    expression_expansion_max_depth: int = 10  # Max recursion depth for expression expansion


class BusinessConceptCatalog(BaseReport):
    """
    Generates textual documentation of all business concepts in a pipeline.

    This report provides a comprehensive catalog of business concepts,
    their operations, metrics, and data flow characteristics.
    """

    def __init__(self, config: Optional[BusinessConceptCatalogConfig] = None, **kwargs):
        """
        Initialize the Business Concept Catalog generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = BusinessConceptCatalogConfig(**kwargs)
        elif config is None:
            config = BusinessConceptCatalogConfig()

        super().__init__(config)
        self.config: BusinessConceptCatalogConfig = config

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        valid_sort_options = ["execution_order", "name", "execution_time"]
        if self.config.sort_by not in valid_sort_options:
            raise ValueError(
                f"Invalid sort_by value: {self.config.sort_by}. "
                f"Must be one of {valid_sort_options}"
            )
        return True

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the Business Concept Catalog report.

        Args:
            lineage_graph: EnhancedLineageGraph to document
            output_path: Path to write the markdown file

        Returns:
            Path to the generated report
        """
        logger.info("Generating Business Concept Catalog")

        # Extract business concepts from graph
        concepts = self._extract_business_concepts(lineage_graph)

        # Sort concepts according to configuration
        concepts = self._sort_concepts(concepts)

        # Generate markdown content
        content = self._generate_markdown(concepts, lineage_graph)

        # Write to file
        return self._write_report(content, output_path)

    def _extract_business_concepts(self, lineage_graph) -> List[Dict[str, Any]]:
        """
        Extract business concepts from the lineage graph.

        Args:
            lineage_graph: EnhancedLineageGraph

        Returns:
            List of business concept dictionaries
        """
        concepts = []

        # Extract business concepts from context_nodes
        # Each context_id represents a business concept
        if hasattr(lineage_graph, 'context_nodes') and lineage_graph.context_nodes:
            for context_id, context_node_list in lineage_graph.context_nodes.items():
                if not context_node_list:
                    continue

                # Get concept information from the first node in the context
                first_node = context_node_list[0]

                # Try to get business concept metadata from node metadata
                concept_name = context_id
                description = ''
                execution_time = 0
                timestamp = first_node.timestamp if hasattr(first_node, 'timestamp') else 0
                hierarchy = {}

                # Check if any node has business_context or business_concept metadata
                for node in context_node_list:
                    if hasattr(node, 'metadata') and node.metadata:
                        # Get concept name from business_context
                        if 'business_context' in node.metadata:
                            concept_name = node.metadata['business_context']
                        elif 'operation_name' in node.metadata and node.metadata.get('operation_type') == 'business_concept':
                            concept_name = node.metadata['operation_name']

                        # Get description
                        if 'description' in node.metadata:
                            description = node.metadata['description']

                        # Get execution time
                        if 'execution_time' in node.metadata:
                            execution_time = max(execution_time, node.metadata.get('execution_time', 0))

                        # Get hierarchy information
                        if 'hierarchy' in node.metadata:
                            hierarchy = node.metadata['hierarchy']

                        # Once we have good metadata, we can break
                        if concept_name != context_id and description:
                            break

                concept_info = {
                    'node_id': context_id,
                    'name': concept_name,
                    'description': description,
                    'context_id': context_id,
                    'execution_time': execution_time,
                    'timestamp': timestamp,
                    'metadata': first_node.metadata if hasattr(first_node, 'metadata') else {},
                    'operations': [],
                    # Hierarchy fields
                    'hierarchy': hierarchy,
                    'parent_context_id': hierarchy.get('parent_context_id'),
                    'parent_name': hierarchy.get('parent_concept_name'),
                    'concept_path': hierarchy.get('concept_path', ''),
                    'depth': hierarchy.get('depth', 0),
                    # CRITICAL FIX: If no hierarchy metadata exists, treat as root (independent concept)
                    # This ensures hierarchical=False concepts are treated as roots, not children
                    'is_root': hierarchy.get('is_root', True) if hierarchy else True
                }
                concepts.append(concept_info)

        logger.debug(f"Extracted {len(concepts)} business concepts from context_nodes")
        return concepts

    def _get_operations_for_concept(
        self, concept: Dict[str, Any], lineage_graph
    ) -> List[Dict[str, Any]]:
        """
        Get all operations belonging to a business concept.

        Args:
            concept: Business concept dictionary
            lineage_graph: EnhancedLineageGraph

        Returns:
            List of operation dictionaries
        """
        operations = []
        context_id = concept['context_id']

        for node_id, node in lineage_graph.nodes.items():
            # Skip if not a lineage node
            if not hasattr(node, 'context_id'):
                continue

            # Skip if not in this concept's context
            if node.context_id != context_id:
                continue

            # Skip business concept nodes themselves
            if hasattr(node, 'metadata') and node.metadata:
                if node.metadata.get('operation_type') == 'business_concept':
                    continue

            # Extract operation info
            op_info = self._extract_operation_info(node, node_id, lineage_graph)
            if op_info:
                operations.append(op_info)

        return operations

    def _extract_operation_info(
        self, node, node_id: str, lineage_graph
    ) -> Optional[Dict[str, Any]]:
        """
        Extract information about a single operation.

        Args:
            node: Node object
            node_id: Node identifier
            lineage_graph: EnhancedLineageGraph

        Returns:
            Operation info dictionary or None
        """
        if not hasattr(node, 'metadata') or not node.metadata:
            return None

        metadata = node.metadata
        operation_type = metadata.get('operation_type', 'unknown')

        # Get parent information for record counts
        parent_ids = metadata.get('parent_ids', [])

        op_info = {
            'node_id': node_id,
            'name': node.name,
            'operation_type': operation_type,
            'timestamp': node.timestamp,
            'parent_ids': parent_ids,
            'is_source': metadata.get('is_source', False),
            'metadata': metadata
        }

        return op_info

    def _sort_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort concepts according to configuration, respecting hierarchy.

        Concepts are sorted hierarchically:
        1. Root concepts first (by specified sort method)
        2. Child concepts immediately after their parent (by specified sort method)

        Args:
            concepts: List of concept dictionaries

        Returns:
            Sorted list of concepts in hierarchical order
        """
        # Separate root and child concepts
        root_concepts = [c for c in concepts if c.get('is_root', False)]
        child_concepts = [c for c in concepts if not c.get('is_root', False)]

        # Sort each group according to config
        def get_sort_key(c):
            if self.config.sort_by == "name":
                return c['name'].lower()
            elif self.config.sort_by == "execution_time":
                return -c['execution_time']  # Negative for reverse
            else:  # execution_order (default)
                return c['timestamp']

        root_concepts.sort(key=get_sort_key)

        # Build hierarchical order: parent followed by children
        hierarchical_order = []

        def add_concept_and_children(parent_id=None, parent_path=''):
            """Recursively add concepts in hierarchical order."""
            # Find children of this parent
            if parent_id is None:
                # Add root concepts
                for concept in root_concepts:
                    hierarchical_order.append(concept)
                    # Recursively add its children
                    add_concept_and_children(
                        concept['context_id'],
                        concept.get('concept_path', concept['name'])
                    )
            else:
                # Find and sort children of this parent
                children = [
                    c for c in child_concepts
                    if c.get('parent_context_id') == parent_id
                ]
                children.sort(key=get_sort_key)

                for child in children:
                    hierarchical_order.append(child)
                    # Recursively add its children
                    add_concept_and_children(
                        child['context_id'],
                        child.get('concept_path', child['name'])
                    )

        # Start with root concepts
        add_concept_and_children()

        return hierarchical_order

    def _generate_markdown(
        self, concepts: List[Dict[str, Any]], lineage_graph
    ) -> str:
        """
        Generate markdown content for the catalog.

        Args:
            concepts: List of business concept dictionaries
            lineage_graph: EnhancedLineageGraph

        Returns:
            Markdown content
        """
        lines = []

        # Title and metadata
        lines.append("# Business Concept Catalog\n")
        lines.append("*Comprehensive documentation of business logic and data transformations*\n")
        lines.append("\n")

        # Add standardized metadata section
        lines.extend(self._generate_metadata_section())
        lines.append("\n")

        lines.append("---\n")

        # Overview section
        lines.extend(self._generate_overview(concepts, lineage_graph))

        # Concept index
        if len(concepts) > 1:
            lines.append("\n## Concept Index\n")
            for i, concept in enumerate(concepts, 1):
                concept_anchor = concept['name'].lower().replace(' ', '-').replace('_', '-')
                lines.append(f"{i}. [{concept['name']}](#{concept_anchor})")
            lines.append("\n---\n")

        # Individual concept sections
        lines.append("\n## Business Concepts\n")
        for concept in concepts:
            lines.extend(self._generate_concept_section(concept, lineage_graph))

        return '\n'.join(lines)

    def _generate_overview(
        self, concepts: List[Dict[str, Any]], lineage_graph
    ) -> List[str]:
        """Generate the overview section."""
        lines = ["\n## Overview\n"]

        # Basic statistics
        total_execution_time = sum(c['execution_time'] for c in concepts)

        lines.append(f"- **Total Concepts:** {len(concepts)}")
        lines.append(f"- **Total Nodes:** {len(lineage_graph.nodes)}")
        lines.append(f"- **Total Edges:** {len(lineage_graph.edges)}")

        if self.config.include_execution_times and total_execution_time > 0:
            lines.append(f"- **Total Execution Time:** {self._format_duration(total_execution_time)}")

        lines.append("")
        return lines

    def _generate_concept_section(
        self, concept: Dict[str, Any], lineage_graph
    ) -> List[str]:
        """Generate documentation for a single business concept."""
        lines = []

        # Determine header level based on hierarchy depth
        # Root concepts: ### (h3)
        # Child concepts: #### (h4)
        # Grandchild+: ##### (h5)
        depth = concept.get('depth', 0)
        header_level = min(3 + depth, 5)  # Cap at h5
        header_prefix = '#' * header_level

        # Concept header
        concept_name = concept['name']
        lines.append(f"\n{header_prefix} {concept_name}\n")

        # Hierarchy information
        parent_name = concept.get('parent_name')
        concept_path = concept.get('concept_path', '')

        if parent_name:
            lines.append(f"**Parent Concept:** {parent_name}\n")
        if concept_path:
            lines.append(f"**Path:** {concept_path}\n")

        # Description
        if concept['description']:
            lines.append(f"**Description:** {concept['description']}\n")

        # Get operations for this concept
        operations = self._get_operations_for_concept(concept, lineage_graph)

        # Tracked variables (if available) - show as context
        tracked_vars = concept['metadata'].get('tracked_columns', [])
        if tracked_vars:
            lines.append("**Tracked Variables:**")
            lines.append(f"- {', '.join(tracked_vars)}")
            lines.append("")

        # Operations list - wrapped in collapsible section
        if self.config.include_operations and operations:
            lines.append("<details>")
            lines.append(f"<summary><b>Operations</b> ({len(operations)} operations)</summary>")
            lines.append("")
            for i, op in enumerate(operations, 1):
                lines.extend(self._format_operation(op, i, lineage_graph))
            lines.append("</details>")
            lines.append("")

        # Data flow summary
        if self.config.show_data_flow_summary and operations:
            lines.extend(self._generate_data_flow_summary(operations))

        lines.append("\n---\n")
        return lines

    def _format_operation(
        self, op: Dict[str, Any], index: int, lineage_graph
    ) -> List[str]:
        """Format a single operation for display."""
        lines = []

        op_type = op['operation_type'].replace('_', ' ').title()
        op_name = op['name']

        lines.append(f"{index}. **{op_name}** ({op_type})")

        # Operation details with indentation
        details = []

        # Show the actual business logic based on operation type
        if op['is_source']:
            details.append("   - Type: Data Source")
            # Show source info if available
            source_info = op['metadata'].get('source', '') or op['metadata'].get('business_label', '')
            if source_info:
                details.append(f"   - Source: {source_info}")

        elif op['operation_type'] == 'filter':
            # Show filter condition (the actual business logic)
            condition = op['metadata'].get('filter_condition', '') or op['metadata'].get('condition', '')
            if condition and self.config.include_filter_conditions:
                # Clean up the condition for readability
                truncated = self._truncate_text(condition, self.config.max_condition_length)
                details.append(f"   - **Filter Logic:** `{truncated}`")
            else:
                details.append(f"   - Type: {op_type}")

        elif op['operation_type'] == 'transform':
            # Show transformation details with type and code formatting
            transform_info = op['metadata'].get('transformation', '')
            transform_type = op['metadata'].get('transformation_type', '')
            is_reassignment = op['metadata'].get('is_reassignment', False)
            previous_transformation = op['metadata'].get('previous_transformation', '')

            if transform_info:
                # Determine transformation type label
                if transform_type == 'creation':
                    type_label = "Variable Creation"
                elif transform_type == 'modification':
                    type_label = "Variable Modification"
                else:
                    # Infer from columns_added/columns_modified if type not specified
                    columns_added = op['metadata'].get('columns_added', [])
                    columns_modified = op['metadata'].get('columns_modified', [])
                    if columns_added:
                        type_label = "Variable Creation"
                    elif columns_modified:
                        type_label = "Variable Modification"
                    else:
                        type_label = "Transformation"

                # Use code formatting for the transformation expression
                details.append(f"   - **{type_label}:** `{transform_info}`")

                # If this is a reassignment, show the previous transformation
                if is_reassignment and previous_transformation:
                    details.append(f"   - **Replaces:** `{previous_transformation}`")
                    details.append(f"   - **Note:** This modifies a column from a previous transformation")

                    # If expression expansion is enabled, show the fully expanded form
                    if self.config.show_expanded_expressions:
                        # Extract column name and expression from transformation
                        parts = transform_info.split('=', 1)
                        if len(parts) == 2:
                            col_name = parts[0].strip()
                            current_expr = parts[1].strip()

                            try:
                                # Expand the CURRENT expression by replacing all column references
                                from ..utils.expression_utils import (
                                    _extract_column_references,
                                )
                                refs = _extract_column_references(current_expr)
                                expanded_expr = current_expr

                                # For each referenced column, find its expansion (excluding current node)
                                import re
                                for ref_col in refs:
                                    ref_expansion = expand_expression(
                                        ref_col,
                                        lineage_graph,
                                        max_depth=self.config.expression_expansion_max_depth,
                                        current_node_id=op['node_id']
                                    )
                                    if ref_expansion and ref_expansion != ref_col:
                                        # Replace reference with expansion
                                        pattern = r'\b' + re.escape(ref_col) + r'\b'
                                        expanded_expr = re.sub(pattern, f'({ref_expansion})', expanded_expr)

                                if expanded_expr and expanded_expr != current_expr:
                                    details.append(f"   - **Expanded Formula:** `{col_name} = {expanded_expr}`")
                            except Exception as e:
                                logger.warning(f"Could not expand expression for {col_name}: {e}")
            else:
                # Fallback if no transformation info
                columns_info = op['metadata'].get('columns_added', [])
                if isinstance(columns_info, list) and columns_info:
                    details.append(f"   - **Columns Added:** {', '.join(columns_info)}")
                else:
                    details.append(f"   - Type: {op_type}")

        elif op['operation_type'] == 'join':
            join_type = op['metadata'].get('join_type', 'unknown')
            join_columns = op['metadata'].get('join_columns', [])
            if join_columns:
                details.append(f"   - **Join Type:** {join_type.upper()}")
                details.append(f"   - **Join Keys:** {', '.join(join_columns)}")
            else:
                details.append(f"   - Type: {op_type} ({join_type})")

        elif op['operation_type'] == 'aggregate':
            group_cols = op['metadata'].get('group_by_columns', [])
            agg_exprs = op['metadata'].get('aggregations', [])
            if group_cols or agg_exprs:
                if group_cols:
                    details.append(f"   - **Group By:** {', '.join(group_cols)}")
                if agg_exprs:
                    details.append(f"   - **Aggregations:** {', '.join(agg_exprs)}")
            else:
                details.append(f"   - Type: {op_type}")

        elif op['operation_type'] == 'select':
            selected_cols = op['metadata'].get('selected_columns', [])
            if selected_cols:
                details.append(f"   - **Selected Columns:** {', '.join(selected_cols)}")
            else:
                details.append(f"   - Type: {op_type}")

        else:
            # Generic operation - show type
            details.append(f"   - Type: {op_type}")

        lines.extend(details)
        lines.append("")

        return lines

    def _generate_data_flow_summary(self, operations: List[Dict[str, Any]]) -> List[str]:
        """Generate a summary of data flow through the concept."""
        lines = ["\n**Data Flow:**"]

        # Simple flow representation
        flow_items = []
        for op in operations:
            op_name = op['name']
            flow_items.append(f"-> {op_name}")

        if flow_items:
            lines.append(' '.join(flow_items))

        lines.append("")
        return lines
