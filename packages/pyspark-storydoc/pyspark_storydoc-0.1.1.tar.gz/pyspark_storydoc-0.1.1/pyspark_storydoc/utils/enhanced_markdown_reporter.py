#!/usr/bin/env python3
"""
Enhanced Markdown report generation utilities for PySpark StoryDoc.

This module extends the standard markdown reporter to include distribution analysis,
providing comprehensive reports that combine lineage visualization with distribution
monitoring throughout data processing pipelines.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..analysis.distribution_analyzer import DistributionComparison, DistributionStats
from ..core.graph_builder import BusinessConceptNode, LineageGraph, OperationNode
from ..core.lineage_tracker import get_global_tracker


def generate_enhanced_lineage_report(
    lineage_graph: LineageGraph,
    mermaid_diagram: str,
    output_path: str,
    title: str = "PySpark Data Lineage Report with Distribution Analysis",
    description: str = "",
    scenario_details: Optional[Dict[str, Any]] = None,
    include_technical_details: bool = True,
    include_distribution_analysis: bool = True,
    distribution_layout: str = "inline"  # "inline", "side_by_side", "appendix"
) -> str:
    """
    Generate a comprehensive markdown report with lineage visualization and distribution analysis.

    Args:
        lineage_graph: The lineage graph to analyze
        mermaid_diagram: Generated Mermaid diagram content
        output_path: Path where to save the markdown report
        title: Report title
        description: Report description
        scenario_details: Additional scenario information
        include_technical_details: Whether to include technical node details
        include_distribution_analysis: Whether to include distribution analysis
        distribution_layout: How to layout distribution plots ("inline", "side_by_side", "appendix")

    Returns:
        Path to the generated markdown file
    """
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Analyze the lineage graph
    analysis = _analyze_lineage_graph(lineage_graph)

    # Get distribution analysis data if available
    distribution_data = _extract_distribution_data() if include_distribution_analysis else None

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
    content.append("## Pipeline Analysis Summary")
    content.append("")
    content.append(f"- **Total Operations**: {analysis['total_nodes']}")
    content.append(f"- **Business Concepts**: {analysis['business_concepts']}")
    content.append(f"- **Raw Operations**: {analysis['raw_operations']}")
    content.append(f"- **Join Operations**: {analysis['join_operations']}")

    # Add distribution summary if available
    if distribution_data:
        content.append(f"- **Distribution Checkpoints**: {len(distribution_data.get('checkpoints', []))}")
        content.append(f"- **Variables Analyzed**: {len(distribution_data.get('all_variables', []))}")

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

    # Data lineage visualization
    content.append("## Data Lineage Visualization")
    content.append("")
    content.append("The following diagram shows the complete data lineage:")
    content.append("")
    content.append("```mermaid")
    content.append(mermaid_diagram)
    content.append("```")
    content.append("")

    # Distribution analysis section
    if include_distribution_analysis and distribution_data:
        if distribution_layout == "inline":
            content.extend(_generate_inline_distribution_section(distribution_data, output_file))
        elif distribution_layout == "side_by_side":
            content.extend(_generate_side_by_side_distribution_section(distribution_data, output_file))
        elif distribution_layout == "appendix":
            content.extend(_generate_appendix_distribution_section(distribution_data, output_file))

    # Technical details
    if include_technical_details:
        content.extend(_generate_technical_details_section(analysis))

    # Usage instructions
    content.append("## How to Use This Report")
    content.append("")
    content.append("1. **View the Mermaid Diagram**: Copy the diagram code to GitHub, GitLab, or a Mermaid viewer")
    content.append("2. **Analyze Business Logic**: Review the business concepts and their operations")
    content.append("3. **Track Data Flow**: Follow the connections to understand data transformations")
    if distribution_data:
        content.append("4. **Review Distribution Changes**: Examine histograms to identify data quality issues")
        content.append("5. **Identify Outliers**: Compare raw vs cleaned distributions")
        content.append("6. **Monitor Data Drift**: Look for unexpected distribution shifts")
    content.append("")

    # Footer
    content.append("---")
    content.append("")
    content.append("*Generated by PySpark StoryDoc - Making Data Lineage Business-Friendly with Distribution Monitoring*")

    # Write the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

    return str(output_file)


def _extract_distribution_data() -> Optional[Dict[str, Any]]:
    """Extract distribution analysis data from the global tracker."""
    try:
        tracker = get_global_tracker()
        distribution_analyses = getattr(tracker, '_distribution_analyses', [])

        if not distribution_analyses:
            return None

        # Organize distribution data
        checkpoints = []
        all_variables = set()
        comparison_plots = []

        for analysis in distribution_analyses:
            metadata = analysis.get('metadata', {})
            function_name = analysis.get('function_name', 'Unknown')

            # Extract plot results
            plot_paths = metadata.get('plot_results', [])
            variables = metadata.get('variables_analyzed', [])
            all_variables.update(variables)

            checkpoints.append({
                'name': function_name,
                'variables': variables,
                'plots': plot_paths,
                'timestamp': analysis.get('timestamp'),
                'before_stats': metadata.get('before_stats', {}),
                'after_stats': metadata.get('after_stats', {})
            })

        return {
            'checkpoints': checkpoints,
            'all_variables': list(all_variables),
            'total_plots': sum(len(cp['plots']) for cp in checkpoints)
        }

    except Exception as e:
        return None


def _generate_inline_distribution_section(distribution_data: Dict[str, Any], markdown_file: Path) -> List[str]:
    """Generate inline distribution analysis section.

    Args:
        distribution_data: Distribution analysis data to include in the report
        markdown_file: Path to the markdown file being generated (used to compute relative image paths)

    Returns:
        List of markdown content lines
    """
    content = []

    content.append("## Distribution Analysis")
    content.append("")
    content.append("This section shows how variable distributions change throughout the pipeline, ")
    content.append("helping identify data quality issues and unexpected transformations.")
    content.append("")

    # Summary statistics
    content.append("### Distribution Monitoring Summary")
    content.append("")
    content.append(f"- **Variables Analyzed**: {', '.join(distribution_data['all_variables'])}")
    content.append(f"- **Analysis Points**: {len(distribution_data['checkpoints'])}")
    content.append(f"- **Total Plots Generated**: {distribution_data['total_plots']}")
    content.append("")

    # Process each checkpoint
    for i, checkpoint in enumerate(distribution_data['checkpoints'], 1):
        content.append(f"### {i}. {checkpoint['name'].replace('_', ' ').title()}")
        content.append("")

        if checkpoint['variables']:
            content.append(f"**Variables Analyzed**: {', '.join(checkpoint['variables'])}")
            content.append("")

        # Add plots
        for plot_path in checkpoint['plots']:
            plot_name = Path(plot_path).stem
            # Convert absolute path to relative path from the markdown file location
            # This ensures images are found regardless of where the markdown is opened
            plot_abs_path = Path(plot_path).resolve()
            markdown_dir = markdown_file.parent.resolve()
            relative_path = os.path.relpath(plot_abs_path, markdown_dir)
            content.append(f"![{plot_name}]({relative_path})")
            content.append("")

        # Add statistics if available
        if checkpoint.get('before_stats') and checkpoint.get('after_stats'):
            content.append("**Distribution Changes**:")
            content.append("")
            for variable in checkpoint['variables']:
                # Add summary of changes for each variable
                content.append(f"- **{variable}**: Distribution analysis completed")
            content.append("")

    return content


def _generate_side_by_side_distribution_section(distribution_data: Dict[str, Any], markdown_file: Path) -> List[str]:
    """Generate side-by-side distribution analysis section.

    Args:
        distribution_data: Distribution analysis data to include in the report
        markdown_file: Path to the markdown file being generated (used to compute relative image paths)

    Returns:
        List of markdown content lines
    """
    content = []

    content.append("## Distribution Analysis")
    content.append("")
    content.append("### Summary")
    content.append("")
    content.append(f"Variables: {', '.join(distribution_data['all_variables'])} | ")
    content.append(f"Checkpoints: {len(distribution_data['checkpoints'])} | ")
    content.append(f"Plots: {distribution_data['total_plots']}")
    content.append("")

    # Create table format for side-by-side comparison
    content.append("### Distribution Changes by Checkpoint")
    content.append("")

    markdown_dir = markdown_file.parent.resolve()

    for checkpoint in distribution_data['checkpoints']:
        content.append(f"#### {checkpoint['name'].replace('_', ' ').title()}")
        content.append("")

        if len(checkpoint['plots']) >= 2:
            # Try to pair before/after plots
            content.append("| Before | After |")
            content.append("|--------|-------|")

            plots = checkpoint['plots']
            for i in range(0, len(plots), 2):
                if i < len(plots):
                    left_abs = Path(plots[i]).resolve()
                    left_plot = os.path.relpath(left_abs, markdown_dir)
                else:
                    left_plot = ""

                if i + 1 < len(plots):
                    right_abs = Path(plots[i + 1]).resolve()
                    right_plot = os.path.relpath(right_abs, markdown_dir)
                else:
                    right_plot = ""

                left_img = f"![{Path(left_plot).stem}]({left_plot})" if left_plot else ""
                right_img = f"![{Path(right_plot).stem}]({right_plot})" if right_plot else ""

                content.append(f"| {left_img} | {right_img} |")

            content.append("")
        else:
            # Single plots
            for plot_path in checkpoint['plots']:
                plot_abs = Path(plot_path).resolve()
                relative_path = os.path.relpath(plot_abs, markdown_dir)
                content.append(f"![{Path(plot_path).stem}]({relative_path})")
                content.append("")

    return content


def _generate_appendix_distribution_section(distribution_data: Dict[str, Any], markdown_file: Path) -> List[str]:
    """Generate appendix distribution analysis section.

    Args:
        distribution_data: Distribution analysis data to include in the report
        markdown_file: Path to the markdown file being generated (used to compute relative image paths)

    Returns:
        List of markdown content lines
    """
    content = []

    # Just add a reference here, full details in appendix
    content.append("## Distribution Analysis")
    content.append("")
    content.append(f"Distribution analysis was performed on {len(distribution_data['all_variables'])} variables ")
    content.append(f"across {len(distribution_data['checkpoints'])} pipeline checkpoints. ")
    content.append("See [Appendix: Distribution Analysis](#appendix-distribution-analysis) for detailed plots and statistics.")
    content.append("")

    # Later in the document, add the full appendix
    content.extend([
        "",
        "---",
        "",
        "## Appendix: Distribution Analysis",
        "",
        "This appendix contains detailed distribution analysis including histograms, ",
        "outlier analysis, and before/after comparisons.",
        ""
    ])

    markdown_dir = markdown_file.parent.resolve()

    # Add all plots organized by checkpoint
    for checkpoint in distribution_data['checkpoints']:
        content.append(f"### {checkpoint['name'].replace('_', ' ').title()}")
        content.append("")

        for plot_path in checkpoint['plots']:
            plot_abs = Path(plot_path).resolve()
            relative_path = os.path.relpath(plot_abs, markdown_dir)
            plot_name = Path(plot_path).stem.replace('_', ' ').title()
            content.append(f"#### {plot_name}")
            content.append(f"![{plot_name}]({relative_path})")
            content.append("")

    return content


def _generate_technical_details_section(analysis: Dict[str, Any]) -> List[str]:
    """Generate technical details section."""
    content = []

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

    return content


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

    return analysis