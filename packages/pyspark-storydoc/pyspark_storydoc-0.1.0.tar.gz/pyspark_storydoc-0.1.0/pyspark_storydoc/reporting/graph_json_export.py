"""
Graph JSON Export - Export lineage graph structure to JSON format.

This module provides functionality to export the complete lineage graph
structure to JSON format for debugging, analysis, or integration with
external tools.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class GraphJsonExportConfig(ReportConfig):
    """Configuration for Graph JSON Export."""
    include_metadata: bool = True
    include_hierarchy: bool = True
    include_metrics: bool = False
    pretty_print: bool = True
    indent: int = 2


class GraphJsonExport(BaseReport):
    """
    Export lineage graph structure to JSON format.

    This exporter creates a JSON representation of the complete lineage graph
    including nodes, edges, business concepts, and metadata. Useful for:
    - Debugging lineage tracking issues
    - Analyzing graph structure programmatically
    - Integrating with external analysis tools
    - Archiving lineage information
    """

    def __init__(self, config: Optional[GraphJsonExportConfig] = None, **kwargs):
        """
        Initialize the Graph JSON Export generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = GraphJsonExportConfig(**kwargs)
        elif config is None:
            config = GraphJsonExportConfig()

        super().__init__(config)
        self.config: GraphJsonExportConfig = config

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        if self.config.indent < 0:
            raise ValueError("indent must be non-negative")
        return True

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate JSON export of the lineage graph.

        Args:
            lineage_graph: EnhancedLineageGraph to export
            output_path: Path to output JSON file

        Returns:
            Path to generated JSON file
        """
        logger.info(f"Generating JSON export of lineage graph to {output_path}")

        # Build JSON structure
        graph_data = self._build_graph_structure(lineage_graph)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            if self.config.pretty_print:
                json.dump(graph_data, f, indent=self.config.indent, ensure_ascii=False)
            else:
                json.dump(graph_data, f, ensure_ascii=False)

        logger.info(f"JSON export completed: {output_path}")
        return str(output_file)

    def _build_graph_structure(self, lineage_graph) -> Dict[str, Any]:
        """
        Build the complete graph structure as a dictionary.

        Args:
            lineage_graph: EnhancedLineageGraph to export

        Returns:
            Dictionary representation of the graph
        """
        # Summary statistics
        source_nodes = [n for n in lineage_graph.nodes.values()
                       if n.metadata.get('operation_type') == 'source']
        business_concept_nodes = [n for n in lineage_graph.nodes.values()
                                 if n.metadata.get('operation_type') == 'business_concept']
        operation_nodes = [n for n in lineage_graph.nodes.values()
                          if n.metadata.get('operation_type') not in ['source', 'business_concept']]

        graph_data = {
            'summary': {
                'total_nodes': len(lineage_graph.nodes),
                'total_edges': len(lineage_graph.edges),
                'source_nodes': len(source_nodes),
                'business_concept_nodes': len(business_concept_nodes),
                'operation_nodes': len(operation_nodes),
            },
            'nodes': self._export_nodes(lineage_graph),
            'edges': self._export_edges(lineage_graph),
        }

        # Add business concept hierarchy if requested
        if self.config.include_hierarchy and hasattr(lineage_graph, 'context_nodes'):
            graph_data['business_concepts'] = self._export_business_concepts(lineage_graph)

        return graph_data

    def _export_nodes(self, lineage_graph) -> list:
        """
        Export all nodes with their metadata.

        Args:
            lineage_graph: EnhancedLineageGraph to export

        Returns:
            List of node dictionaries
        """
        nodes = []

        for node_id, node in lineage_graph.nodes.items():
            node_data = {
                'node_id': node_id,
                'operation_type': node.metadata.get('operation_type', 'unknown'),
            }

            # Add basic attributes
            if hasattr(node, 'lineage_id'):
                node_data['lineage_id'] = str(node.lineage_id)

            if hasattr(node, 'context_id'):
                node_data['context_id'] = node.context_id

            # Add metadata if requested
            if self.config.include_metadata:
                # Filter out None values and add selected metadata
                metadata = {}
                for key in ['operation_name', 'business_label', 'source_name',
                           'table_name', 'file_path', 'join_type', 'join_keys',
                           'group_columns', 'aggregation_functions', 'filter_condition',
                           'created_columns', 'modified_columns', 'dropped_columns',
                           'selected_columns', 'input_column_count', 'output_column_count']:
                    value = node.metadata.get(key)
                    if value is not None:
                        metadata[key] = value

                if metadata:
                    node_data['metadata'] = metadata

                # Add hierarchy info if available
                if 'hierarchy' in node.metadata and self.config.include_hierarchy:
                    node_data['hierarchy'] = node.metadata['hierarchy']

            # Add metrics if requested
            if self.config.include_metrics:
                metrics = {}
                for key in ['row_count', 'execution_time']:
                    value = node.metadata.get(key)
                    if value is not None:
                        metrics[key] = value

                if metrics:
                    node_data['metrics'] = metrics

            nodes.append(node_data)

        return nodes

    def _export_edges(self, lineage_graph) -> list:
        """
        Export all edges.

        Args:
            lineage_graph: EnhancedLineageGraph to export

        Returns:
            List of edge dictionaries
        """
        edges = []

        for edge in lineage_graph.edges:
            edge_data = {
                'source_id': edge.source_id,
                'target_id': edge.target_id,
                'edge_type': edge.edge_type,
            }

            # Add edge metadata if available and requested
            if self.config.include_metadata and hasattr(edge, 'metadata') and edge.metadata:
                edge_data['metadata'] = edge.metadata

            edges.append(edge_data)

        return edges

    def _export_business_concepts(self, lineage_graph) -> list:
        """
        Export business concept hierarchy.

        Args:
            lineage_graph: EnhancedLineageGraph to export

        Returns:
            List of business concept dictionaries
        """
        concepts = []

        if not hasattr(lineage_graph, 'context_nodes'):
            return concepts

        for context_id, nodes in lineage_graph.context_nodes.items():
            # Find the business concept node
            concept_node = None
            for node in lineage_graph.nodes.values():
                if (node.metadata.get('operation_type') == 'business_concept' and
                    getattr(node, 'context_id', None) == context_id):
                    concept_node = node
                    break

            if not concept_node:
                continue

            concept_data = {
                'context_id': context_id,
                'name': concept_node.metadata.get('operation_name', 'Unknown'),
                'description': concept_node.metadata.get('description'),
                'operation_count': len(nodes),
                'operations': [node.node_id for node in nodes if hasattr(node, 'node_id')],
            }

            # Add hierarchy information
            if 'hierarchy' in concept_node.metadata:
                hierarchy = concept_node.metadata['hierarchy']
                concept_data['hierarchy'] = {
                    'depth': hierarchy.get('depth', 0),
                    'is_root': hierarchy.get('is_root', False),
                    'parent_context_id': hierarchy.get('parent_context_id'),
                    'concept_path': hierarchy.get('concept_path'),
                }

            concepts.append(concept_data)

        return concepts


def generate_graph_json(lineage_graph, output_path: str,
                       include_metadata: bool = True,
                       include_hierarchy: bool = True,
                       include_metrics: bool = False,
                       pretty_print: bool = True,
                       indent: int = 2) -> str:
    """
    Generate JSON export of lineage graph (convenience function).

    Args:
        lineage_graph: EnhancedLineageGraph to export
        output_path: Path to output JSON file
        include_metadata: Include detailed metadata for nodes and edges
        include_hierarchy: Include business concept hierarchy information
        include_metrics: Include metrics (row counts, execution times)
        pretty_print: Format JSON with indentation
        indent: Number of spaces for indentation (if pretty_print=True)

    Returns:
        Path to generated JSON file

    Example:
        >>> from pyspark_storydoc.reporting import generate_graph_json
        >>> from pyspark_storydoc.core.lineage_tracker import get_global_tracker
        >>>
        >>> tracker = get_global_tracker()
        >>> graph = tracker.get_lineage_graph()
        >>> generate_graph_json(graph, "lineage_graph.json")
    """
    config = GraphJsonExportConfig(
        include_metadata=include_metadata,
        include_hierarchy=include_hierarchy,
        include_metrics=include_metrics,
        pretty_print=pretty_print,
        indent=indent
    )

    exporter = GraphJsonExport(config)
    return exporter.generate(lineage_graph, output_path)
