#!/usr/bin/env python3
"""
JSON export utilities for lineage graphs.
Provides functions to export lineage graphs to JSON format for debugging and analysis.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ..core.graph_builder import BusinessConceptNode, LineageGraph, OperationNode

logger = logging.getLogger(__name__)


def export_lineage_to_json(
    lineage_graph: LineageGraph,
    output_path: str,
    include_metadata: bool = True,
    pretty_print: bool = True,
    include_timestamp: bool = True
) -> str:
    """
    Export a lineage graph to JSON format.

    Args:
        lineage_graph: The lineage graph to export
        output_path: Path where to save the JSON file
        include_metadata: Whether to include detailed metadata
        pretty_print: Whether to format JSON with indentation
        include_timestamp: Whether to add export timestamp

    Returns:
        Path to the exported JSON file

    Raises:
        Exception: If export fails
    """
    try:
        # Convert lineage graph to dictionary
        # EnhancedLineageGraph uses export_to_dict(), while LineageGraph may use to_dict()
        if hasattr(lineage_graph, 'export_to_dict'):
            lineage_dict = lineage_graph.export_to_dict()
        elif hasattr(lineage_graph, 'to_dict'):
            lineage_dict = lineage_graph.to_dict()
        else:
            raise AttributeError(f"Lineage graph type {type(lineage_graph).__name__} has no to_dict() or export_to_dict() method")

        # Add export metadata if requested
        if include_timestamp:
            export_info = {
                "export_timestamp": datetime.now().isoformat(),
                "total_nodes": len(lineage_graph.nodes),
                "total_edges": len(lineage_graph.edges),
                "node_types": _count_node_types(lineage_graph),
                "export_config": {
                    "include_metadata": include_metadata,
                    "pretty_print": pretty_print
                }
            }
            lineage_dict["export_info"] = export_info

        # Filter metadata if requested
        if not include_metadata:
            lineage_dict = _filter_metadata(lineage_dict)

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty_print:
                json.dump(lineage_dict, f, indent=2, default=str)
            else:
                json.dump(lineage_dict, f, default=str)

        logger.info(f"Exported lineage graph to: {output_file}")
        return str(output_file)

    except Exception as e:
        logger.error(f"Failed to export lineage to JSON: {e}")
        raise


def export_business_concepts_summary(
    lineage_graph: LineageGraph,
    output_path: str
) -> str:
    """
    Export a summary of business concepts and their operations to JSON.

    Args:
        lineage_graph: The lineage graph to analyze
        output_path: Path where to save the summary JSON

    Returns:
        Path to the exported summary file
    """
    try:
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_nodes": len(lineage_graph.nodes),
            "business_concepts": [],
            "raw_operations": [],
            "summary_stats": {
                "business_concept_count": 0,
                "operations_in_concepts": 0,
                "raw_operations_count": 0
            }
        }

        # Analyze business concepts
        for node_id, node in lineage_graph.nodes.items():
            if isinstance(node, BusinessConceptNode):
                concept_info = {
                    "node_id": node_id,
                    "name": node.name,
                    "description": node.description,
                    "track_columns": getattr(node, 'track_columns', []),
                    "technical_operations": [],
                    "operation_count": len(node.technical_operations)
                }

                # Add technical operations
                for op in node.technical_operations:
                    op_info = {
                        "node_id": op.node_id,
                        "operation_type": op.operation_type.value,
                        "name": op.name,
                        "execution_time": getattr(op, 'execution_time', None),
                        "has_before_metrics": op.before_metrics is not None,
                        "has_after_metrics": op.after_metrics is not None,
                        "metadata_keys": list(op.metadata.keys()) if op.metadata else []
                    }
                    concept_info["technical_operations"].append(op_info)

                summary["business_concepts"].append(concept_info)
                summary["summary_stats"]["business_concept_count"] += 1
                summary["summary_stats"]["operations_in_concepts"] += len(node.technical_operations)

            elif isinstance(node, OperationNode):
                # This is a raw operation (not in a business concept)
                op_info = {
                    "node_id": node_id,
                    "operation_type": node.operation_type.value,
                    "name": node.name,
                    "business_context": node.business_context if hasattr(node, 'business_context') else None,
                    "execution_time": getattr(node, 'execution_time', None),
                    "has_before_metrics": node.before_metrics is not None,
                    "has_after_metrics": node.after_metrics is not None,
                    "metadata_keys": list(node.metadata.keys()) if node.metadata else []
                }
                summary["raw_operations"].append(op_info)
                summary["summary_stats"]["raw_operations_count"] += 1

        # Write summary file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Exported business concepts summary to: {output_file}")
        return str(output_file)

    except Exception as e:
        logger.error(f"Failed to export business concepts summary: {e}")
        raise


def _count_node_types(lineage_graph: LineageGraph) -> Dict[str, int]:
    """Count nodes by type."""
    counts = {}
    for node in lineage_graph.nodes.values():
        node_type = type(node).__name__
        counts[node_type] = counts.get(node_type, 0) + 1
    return counts


def _filter_metadata(lineage_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Remove detailed metadata to create a cleaner export."""
    # This is a simple implementation - could be made more sophisticated
    filtered = lineage_dict.copy()

    # Remove heavy metadata from nodes
    if "nodes" in filtered:
        for node_id, node_data in filtered["nodes"].items():
            if "metadata" in node_data:
                # Keep only essential metadata
                essential_keys = ["operation_type", "materialize", "track_columns"]
                filtered_metadata = {
                    k: v for k, v in node_data["metadata"].items()
                    if k in essential_keys
                }
                node_data["metadata"] = filtered_metadata

    return filtered