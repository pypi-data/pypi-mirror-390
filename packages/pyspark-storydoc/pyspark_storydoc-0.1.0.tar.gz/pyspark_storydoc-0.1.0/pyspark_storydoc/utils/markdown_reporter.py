#!/usr/bin/env python3
"""
Markdown report generation utilities for PySpark StoryDoc.
Provides functions to create comprehensive markdown reports with lineage visualization.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.graph_builder import BusinessConceptNode, LineageGraph, OperationNode


def generate_lineage_report(
    lineage_graph: LineageGraph,
    mermaid_diagram: str,
    output_path: str,
    title: str = "PySpark Data Lineage Report",
    description: str = "",
    scenario_details: Optional[Dict[str, Any]] = None,
    include_technical_details: bool = True
) -> str:
    """
Generate a comprehensive markdown report with lineage visualization.

    Args:
        lineage_graph: The lineage graph to analyze
        mermaid_diagram: Generated Mermaid diagram content
        output_path: Path where to save the markdown report
        title: Report title
        description: Report description
        scenario_details: Additional scenario information
        include_technical_details: Whether to include technical node details

    Returns:
        Path to the generated markdown file
    """

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Analyze the lineage graph
    analysis = _analyze_lineage_graph(lineage_graph)

    # Generate the markdown content
    content = []

    # Header
    content.append(f"# {title}")
    content.append("")
    content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")

    if description:
        content.append("## Overview")
        content.append("")
        content.append(description)
        content.append("")

    # Scenario details if provided
    if scenario_details:
        content.append("## Scenario Details")
        content.append("")
        for key, value in scenario_details.items():
            content.append(f"- **{key}**: {value}")
        content.append("")

    # Analysis summary
    content.append("## Lineage Analysis")
    content.append("")
    content.append(f"- **Total Nodes**: {analysis['total_nodes']}")
    content.append(f"- **Total Edges**: {analysis['total_edges']}")
    content.append(f"- **Business Concepts**: {analysis['business_concepts']}")
    content.append(f"- **Raw Operations**: {analysis['raw_operations']}")
    content.append(f"- **Join Operations**: {analysis['join_operations']}")
    content.append("")

    # Business concepts breakdown
    if analysis['business_concept_details']:
        content.append("### Business Concepts")
        content.append("")
        for concept in analysis['business_concept_details']:
            content.append(f"**{concept['name']}**")
            content.append(f"- Operations: {concept['operation_count']}")
            if concept['description']:
                content.append(f"- Description: {concept['description']}")
            if concept['track_columns']:
                content.append(f"- Tracked Columns: {', '.join(concept['track_columns'])}")
            content.append("")

    # Data flow summary
    if analysis['data_flow']:
        content.append("### Data Flow Summary")
        content.append("")
        for flow_step in analysis['data_flow']:
            content.append(f"- {flow_step}")
        content.append("")

    # Visualization
    content.append("## Data Lineage Visualization")
    content.append("")
    content.append("The following diagram shows the complete data lineage with:")
    content.append("- **Business Concepts** grouped in subgraphs")
    content.append("- **Operations** showing record counts and transformations")
    content.append("- **Connections** showing data flow between operations")
    content.append("- **Join Points** where multiple data streams converge")
    content.append("")
    content.append("```mermaid")
    content.append(mermaid_diagram)
    content.append("```")
    content.append("")

    # Technical details
    if include_technical_details:
        content.append("## Technical Details")
        content.append("")

        # Operation types breakdown
        if analysis['operation_types']:
            content.append("### Operation Types")
            content.append("")
            for op_type, count in analysis['operation_types'].items():
                content.append(f"- **{op_type}**: {count} operations")
            content.append("")

        # Join details
        if analysis['join_details']:
            content.append("### Join Operations")
            content.append("")
            for i, join_info in enumerate(analysis['join_details'], 1):
                content.append(f"**Join {i}: {join_info['name']}**")
                content.append(f"- Type: {join_info.get('join_type', 'unknown')}")
                content.append(f"- Keys: {join_info.get('join_keys', 'unknown')}")
                if join_info.get('before_count') and join_info.get('after_count'):
                    content.append(f"- Record Impact: {join_info['before_count']} {join_info['after_count']}")
                content.append("")

    # Usage instructions
    content.append("## How to Use This Report")
    content.append("")
    content.append("1. **View the Mermaid Diagram**: Copy the diagram code to GitHub, GitLab, or a Mermaid viewer")
    content.append("2. **Analyze Business Logic**: Review the business concepts and their operations")
    content.append("3. **Track Data Flow**: Follow the connections to understand data transformations")
    content.append("4. **Identify Bottlenecks**: Look for operations with significant record count changes")
    content.append("5. **Validate Joins**: Ensure join operations produce expected results")
    content.append("")

    # Footer
    content.append("---")
    content.append("")
    content.append(f"*Generated by PySpark StoryDoc - Making Data Lineage Business-Friendly*")

    # Write the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

    return str(output_file)


def _analyze_lineage_graph(lineage_graph: LineageGraph) -> Dict[str, Any]:
    """Analyze a lineage graph to extract summary information."""

    analysis = {
        'total_nodes': len(lineage_graph.nodes),
        'total_edges': len(lineage_graph.edges),
        'business_concepts': 0,
        'raw_operations': 0,
        'join_operations': 0,
        'business_concept_details': [],
        'operation_types': {},
        'join_details': [],
        'data_flow': []
    }

    # Analyze nodes
    for node in lineage_graph.nodes.values():
        if isinstance(node, BusinessConceptNode):
            analysis['business_concepts'] += 1
            analysis['business_concept_details'].append({
                'name': node.name,
                'description': node.description,
                'operation_count': len(node.technical_operations),
                'track_columns': getattr(node, 'track_columns', [])
            })

        elif isinstance(node, OperationNode):
            analysis['raw_operations'] += 1

            # Count operation types
            op_type = node.operation_type.value
            analysis['operation_types'][op_type] = analysis['operation_types'].get(op_type, 0) + 1

            # Collect join details
            if node.operation_type.value.lower() == 'join':
                analysis['join_operations'] += 1
                join_info = {
                    'name': node.name,
                    'join_type': node.metadata.get('join_type', 'unknown') if node.metadata else 'unknown',
                    'join_keys': node.metadata.get('join_keys', 'unknown') if node.metadata else 'unknown',
                }

                if hasattr(node, 'before_metrics') and node.before_metrics:
                    join_info['before_count'] = node.before_metrics.row_count
                if hasattr(node, 'after_metrics') and node.after_metrics:
                    join_info['after_count'] = node.after_metrics.row_count

                analysis['join_details'].append(join_info)

    # Generate data flow summary
    source_nodes = [node for node in lineage_graph.nodes.values()
                    if isinstance(node, OperationNode) and node.operation_type.value.lower() == 'source']

    if source_nodes:
        analysis['data_flow'].append(f"**Data Sources**: {len(source_nodes)} source operations")

    if analysis['join_operations'] > 0:
        analysis['data_flow'].append(f"**Join Points**: {analysis['join_operations']} join operations merge data streams")

    if analysis['business_concepts'] > 0:
        analysis['data_flow'].append(f"**Business Logic**: {analysis['business_concepts']} business concepts organize operations")

    return analysis