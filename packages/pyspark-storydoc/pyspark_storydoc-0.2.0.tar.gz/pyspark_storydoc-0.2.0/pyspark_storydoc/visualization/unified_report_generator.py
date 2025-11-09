#!/usr/bin/env python3
"""
Unified Report Generator for PySpark StoryDoc.

DEPRECATED: This module is deprecated in favor of the new modular reporting system.
Please migrate to pyspark_storydoc.reporting for improved functionality.
See docs/MIGRATION_GUIDE.md for migration instructions.

This module creates comprehensive markdown reports that integrate:
1. Enhanced lineage visualization with distribution analysis markers
2. Per-variable distribution analysis tables
3. Cross-referencing between lineage and distribution sections
4. Temporal sequencing based on analysis execution order
"""

import logging
import time
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from ..core.graph_builder import LineageGraph
from ..visualization.lineage_diagram_generator import LineageDiagramGenerator

logger = logging.getLogger(__name__)

# Flag to ensure deprecation warning is only shown once
_deprecation_warning_shown = False


@dataclass
class DistributionAnalysisPoint:
    """Represents a single distribution analysis point in the pipeline."""
    reference_id: str  # DA-001, DA-002, etc.
    step_name: str
    function_name: str
    variables: List[str]
    timestamp: float
    lineage_node_id: str
    before_stats: Dict[str, Any]
    after_stats: Dict[str, Any]
    plot_results: List[str]
    execution_time: Optional[float] = None
    record_change: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UnifiedReportConfig:
    """
    Configuration for unified report generation.

    DEPRECATED: Use the new modular reporting system instead.
    See docs/MIGRATION_GUIDE.md for migration instructions.
    """
    title: str = "Unified Pipeline Analysis Report"
    include_executive_summary: bool = True
    include_cross_analysis: bool = True
    table_layout: str = "per_variable"  # "per_variable", "per_step", "hybrid"
    show_technical_details: bool = True
    output_format: str = "markdown"

    def __post_init__(self):
        """Show deprecation warning when config is created."""
        global _deprecation_warning_shown
        if not _deprecation_warning_shown:
            warnings.warn(
                "UnifiedReportConfig is deprecated and will be removed in version 3.0. "
                "Please migrate to the new modular reporting system. "
                "See docs/MIGRATION_GUIDE.md for migration instructions.",
                DeprecationWarning,
                stacklevel=3
            )
            _deprecation_warning_shown = True


class UnifiedReportGenerator:
    """
    Generates comprehensive reports integrating lineage and distribution analysis.

    DEPRECATED: This class is deprecated in favor of the new modular reporting system.
    Please migrate to pyspark_storydoc.reporting for improved functionality.
    See docs/MIGRATION_GUIDE.md for migration instructions.

    Creates cohesive markdown documents with:
    - Enhanced Mermaid diagrams with clickable DA-xxx markers
    - Per-variable distribution analysis tables
    - Cross-references between sections
    - Professional styling without emojis

    Migration Example:
        # Old way (deprecated):
        from pyspark_storydoc.visualization import UnifiedReportGenerator
        generator = UnifiedReportGenerator()
        report = generator.generate_unified_lineage_report(graph, "report.md")

        # New way (recommended):
        from pyspark_storydoc.reporting import generate_comprehensive_report
        report = generate_comprehensive_report(graph, "report.md")
    """

    def __init__(self, config: Optional[UnifiedReportConfig] = None):
        """
        Initialize the unified report generator.

        DEPRECATED: Use pyspark_storydoc.reporting.generate_comprehensive_report() instead.

        Args:
            config: Configuration for report generation
        """
        global _deprecation_warning_shown
        if not _deprecation_warning_shown:
            warnings.warn(
                "UnifiedReportGenerator is deprecated and will be removed in version 3.0. "
                "Please migrate to the new modular reporting system using "
                "pyspark_storydoc.reporting.generate_comprehensive_report(). "
                "See docs/MIGRATION_GUIDE.md for migration instructions.",
                DeprecationWarning,
                stacklevel=2
            )
            _deprecation_warning_shown = True

        self.config = config or UnifiedReportConfig()
        # Configure visualizer to hide passthrough operations
        self.visualizer = LineageDiagramGenerator(
            show_passthrough_operations=False,
            operation_filter="impacting"
        )

    def generate_unified_lineage_report(
        self,
        lineage_graph: LineageGraph,
        output_path: str,
        distribution_analyses: Optional[List[Dict[str, Any]]] = None,
        title: Optional[str] = None,
        include_cross_analysis: bool = True
    ) -> str:
        """
        Generate comprehensive report with integrated lineage and distribution analysis.

        Args:
            lineage_graph: Complete lineage graph
            output_path: Output file path for the report
            distribution_analyses: List of distribution analysis results
            title: Report title (overrides config)
            include_cross_analysis: Include cross-step analysis section

        Returns:
            Path to generated report
        """
        try:
            # Store output path for relative path calculations
            self._output_path = Path(output_path)

            # Use provided title or config default
            report_title = title or self.config.title

            # Process distribution analyses
            analysis_points = self._process_distribution_analyses(
                distribution_analyses or [], lineage_graph
            )

            print(f"Processed distribution analysis points: {len(analysis_points)}")
            for point in analysis_points:
                print(f"  - {point.reference_id}: {point.step_name} (vars: {point.variables})")
                print(f"    Plots available: {len(point.plot_results)}")

            # Generate enhanced Mermaid diagram with markers
            enhanced_mermaid = self._create_enhanced_mermaid_with_markers(
                lineage_graph, analysis_points
            )

            # Generate report sections
            sections = self._generate_report_sections(
                lineage_graph, analysis_points, enhanced_mermaid, report_title
            )

            # Combine sections into final report
            report_content = self._assemble_final_report(sections, include_cross_analysis)

            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            logger.info(f"Unified report generated: {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to generate unified report: {e}")
            raise

    def _process_distribution_analyses(
        self,
        distribution_analyses: List[Dict[str, Any]],
        lineage_graph: LineageGraph
    ) -> List[DistributionAnalysisPoint]:
        """Process raw distribution analysis data into structured points."""
        analysis_points = []

        # Sort by timestamp to ensure temporal ordering
        sorted_analyses = sorted(
            distribution_analyses,
            key=lambda x: x.get('timestamp', 0)
        )

        for idx, analysis in enumerate(sorted_analyses, 1):
            metadata = analysis.get('metadata', {})

            # Generate reference ID (DA-001, DA-002, etc.)
            reference_id = f"DA-{idx:03d}"

            # Find corresponding lineage node
            function_name = analysis.get('function_name', 'unknown')
            lineage_node_id = self._find_lineage_node_for_function(
                function_name, lineage_graph
            )

            # Extract step name from function
            step_name = self._format_step_name(function_name)

            # Calculate record changes if available
            record_change = None
            before_stats = metadata.get('before_stats', {})
            after_stats = metadata.get('after_stats', {})

            if before_stats and after_stats:
                record_change = self._calculate_record_changes(before_stats, after_stats)

            analysis_point = DistributionAnalysisPoint(
                reference_id=reference_id,
                step_name=step_name,
                function_name=function_name,
                variables=metadata.get('variables_analyzed', []),
                timestamp=analysis.get('timestamp', 0),
                lineage_node_id=lineage_node_id,
                before_stats=before_stats,
                after_stats=after_stats,
                plot_results=metadata.get('plot_results', []),
                execution_time=metadata.get('execution_time'),
                record_change=record_change,
                metadata=metadata
            )

            analysis_points.append(analysis_point)

        return analysis_points

    def _find_lineage_node_for_function(
        self, function_name: str, lineage_graph: LineageGraph
    ) -> Optional[str]:
        """Find the lineage node ID that corresponds to a function name."""
        # Look for operation nodes with matching function names
        for node_id, node in lineage_graph.nodes.items():
            if hasattr(node, 'metadata') and node.metadata:
                if node.metadata.get('function_name') == function_name:
                    return node_id
                # Also check for method_name
                if node.metadata.get('method_name') == function_name:
                    return node_id

            # Check if the node name matches the function name
            if hasattr(node, 'name') and node.name:
                if function_name.lower() in node.name.lower():
                    return node_id

        return None

    def _format_step_name(self, function_name: str) -> str:
        """Convert function name to human-readable step name."""
        if not function_name:
            return "Unknown Step"

        # Convert snake_case to Title Case
        words = function_name.replace('_', ' ').split()
        return ' '.join(word.capitalize() for word in words)

    def _calculate_record_changes(
        self, before_stats: Dict[str, Any], after_stats: Dict[str, Any]
    ) -> Dict[str, int]:
        """Calculate record count changes between before and after."""
        changes = {}

        # Look for record counts in different outlier method results
        for method in ['none', 'iqr', 'zscore', 'percentile']:
            before_method_stats = before_stats.get(method, {})
            after_method_stats = after_stats.get(method, {})

            if before_method_stats and after_method_stats:
                # Look for record counts in the first variable's stats
                for var_name, var_stats in before_method_stats.items():
                    if isinstance(var_stats, dict) and 'count' in var_stats:
                        before_count = var_stats['count']
                        after_var_stats = after_method_stats.get(var_name, {})
                        after_count = after_var_stats.get('count')

                        if before_count is not None and after_count is not None:
                            changes[f"{method}_records"] = after_count - before_count
                            break

        return changes

    def _create_enhanced_mermaid_with_markers(
        self, lineage_graph: LineageGraph, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Create enhanced Mermaid diagram with distribution analysis markers."""
        # Create base Mermaid diagram
        base_mermaid = self.visualizer.create_detailed_mermaid(
            lineage_graph, title="Enhanced Pipeline Flow"
        )

        # Parse the base diagram to add markers and distribution nodes
        lines = base_mermaid.split('\n')
        enhanced_lines = []

        # Track node IDs for adding markers
        node_mappings = {}
        distribution_nodes = []
        node_counter = 1000  # Start high to avoid conflicts

        # Find where to insert distribution analysis nodes
        insert_index = len(lines) - 10  # Insert before styling

        for line in lines:
            enhanced_line = line
            enhanced_lines.append(enhanced_line)

            # Insert distribution analysis nodes after the main graph
            if enhanced_lines.__len__() == insert_index:
                # Add distribution analysis nodes and their connections
                for analysis_point in analysis_points:
                    dist_node_id = f"DA_{node_counter}"
                    node_counter += 1

                    # Create distribution analysis node
                    variables_str = ", ".join(analysis_point.variables)
                    dist_label = f"**Distribution Analysis**<br/>{analysis_point.reference_id}: {analysis_point.step_name}<br/>Variables: {variables_str}"

                    enhanced_lines.append(f' {dist_node_id}["{dist_label}"]')
                    distribution_nodes.append(dist_node_id)
                    node_mappings[analysis_point.reference_id] = dist_node_id

                    # Connect distribution analysis node to its source node (as a leaf/observation)
                    # Find the source node that this analysis is observing
                    source_node_id = self._find_source_node_for_analysis(analysis_point, enhanced_lines)
                    if source_node_id:
                        # Add connection from source to distribution analysis (one-way, analysis has no children)
                        enhanced_lines.append(f' {source_node_id} -.-> {dist_node_id}')

                enhanced_lines.append("")

        # Add clickable links for distribution analysis markers
        enhanced_lines.append("")
        enhanced_lines.append(" %% Distribution analysis connections (dotted arrows indicate observation/monitoring)")
        enhanced_lines.append(" %% Clickable links to distribution sections")

        for analysis_point in analysis_points:
            if analysis_point.reference_id in node_mappings:
                node_id = node_mappings[analysis_point.reference_id]
                anchor_id = f"#{analysis_point.reference_id.lower()}-{analysis_point.step_name.lower().replace(' ', '-')}"
                enhanced_lines.append(f' click {node_id} "{anchor_id}"')

        # Add special styling for distribution analysis nodes
        enhanced_lines.append("")
        enhanced_lines.append(" %% Special styling for distribution analysis nodes")
        enhanced_lines.append(" classDef distributionAnalysisNode fill:#FF9800,stroke:#F57C00,stroke-width:3px,color:#FFFFFF")

        if distribution_nodes:
            enhanced_lines.append(f" class {','.join(distribution_nodes)} distributionAnalysisNode")

        return '\n'.join(enhanced_lines)

    def _find_source_node_for_analysis(self, analysis_point: DistributionAnalysisPoint, enhanced_lines: List[str]) -> Optional[str]:
        """Find the source node ID that the distribution analysis should connect to."""
        # First, try to use the explicit parent_operation_id if available
        metadata = analysis_point.metadata or {}
        parent_operation_id = metadata.get('parent_operation_id')

        print(f"  Looking for source node for: {analysis_point.function_name}")
        print(f"    Parent operation ID: {parent_operation_id}")

        if parent_operation_id:
            # Look for a node that corresponds to this parent operation ID
            for line in enhanced_lines:
                if line.strip().startswith(' Op_') and '"' in line:
                    # Extract the node ID and see if we can match it to the parent operation
                    parts = line.strip().split()
                    if parts:
                        node_id = parts[0]
                        # For now, we'll use a heuristic - could be improved with better tracking
                        print(f"    Checking node: {node_id}")

        # Fallback to function name matching
        function_name = analysis_point.function_name.lower()
        step_name = analysis_point.step_name.lower()

        for line in enhanced_lines:
            stripped = line.strip()
            if stripped.startswith('Op_') and '"' in line:
                line_lower = line.lower()

                # Try to match by function name or step name
                if (function_name in line_lower or
                    step_name in line_lower):

                    # Extract just the node ID (Op_N) before the bracket
                    if '[' in stripped or '{' in stripped:
                        node_id = stripped.split('[')[0].split('{')[0]
                        print(f"    Found matching node by name: {node_id}")
                        return node_id

        # Final fallback: connect to the last non-source, non-passthrough operation
        last_business_node = None
        for line in enhanced_lines:
            stripped = line.strip()
            if stripped.startswith('Op_') and '"' in line:
                line_lower = line.lower()
                # Skip source operations and passthrough select operations
                if ("source" not in line_lower and "load" not in line_lower and
                    "select" not in line_lower and "identity" not in line_lower):
                    # Extract just the node ID (Op_N) before the bracket
                    if '[' in stripped or '{' in stripped:
                        last_business_node = stripped.split('[')[0].split('{')[0]

        print(f"    Using fallback node: {last_business_node}")
        return last_business_node

    def _generate_report_sections(
        self,
        lineage_graph: LineageGraph,
        analysis_points: List[DistributionAnalysisPoint],
        enhanced_mermaid: str,
        title: str
    ) -> Dict[str, str]:
        """Generate all sections of the unified report."""
        sections = {}

        # Executive Summary
        if self.config.include_executive_summary:
            sections['executive_summary'] = self._generate_executive_summary(
                lineage_graph, analysis_points
            )

        # Pipeline Overview with Enhanced Diagram
        sections['pipeline_overview'] = self._generate_pipeline_overview(
            enhanced_mermaid, analysis_points
        )

        # Distribution Analysis by Variable
        sections['distribution_analysis'] = self._generate_distribution_analysis_section(
            analysis_points
        )

        # Expression Lineage Analysis
        sections['expression_lineage'] = self._generate_expression_lineage_section()

        # Cross-Variable Analysis (if enabled)
        if self.config.include_cross_analysis:
            sections['cross_analysis'] = self._generate_cross_analysis_section(
                analysis_points
            )

        # Distribution Analysis Details
        sections['distribution_details'] = self._generate_distribution_details_section(
            analysis_points
        )

        # Technical Details (if enabled)
        if self.config.show_technical_details:
            sections['technical_details'] = self._generate_technical_details_section(
                lineage_graph, analysis_points
            )

        return sections

    def _generate_executive_summary(
        self, lineage_graph: LineageGraph, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate executive summary section."""
        lines = []
        lines.append("## Executive Summary")
        lines.append("")

        # Pipeline metrics
        total_nodes = len(lineage_graph.nodes)
        analysis_count = len(analysis_points)

        # Collect analyzed variables
        all_variables = set()
        for point in analysis_points:
            all_variables.update(point.variables)

        lines.append(f"- **Pipeline Steps**: {total_nodes}")
        lines.append(f"- **Distribution Analysis Points**: {analysis_count}")
        lines.append(f"- **Variables Monitored**: {', '.join(sorted(all_variables))}")

        # Key findings
        if analysis_points:
            # Find most significant changes
            max_change_point = None
            max_change = 0

            for point in analysis_points:
                if point.record_change:
                    for method, change in point.record_change.items():
                        if abs(change) > abs(max_change):
                            max_change = change
                            max_change_point = point

            if max_change_point:
                change_desc = f"+{max_change:,}" if max_change > 0 else f"{max_change:,}"
                lines.append(f"- **Most Significant Change**: {max_change_point.step_name} ({change_desc} records)")

        lines.append("")
        return '\n'.join(lines)

    def _generate_pipeline_overview(
        self, enhanced_mermaid: str, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate pipeline overview section with enhanced diagram."""
        lines = []
        lines.append("## 1. Pipeline Flow Visualization")
        lines.append("")
        lines.append("### Enhanced Lineage Diagram")
        lines.append("Shows complete data flow with distribution analysis markers:")
        lines.append("")
        lines.append("```mermaid")
        lines.append(enhanced_mermaid)
        lines.append("```")
        lines.append("")

        # Distribution analysis legend
        lines.append("**Distribution Analysis Legend:**")
        for point in analysis_points:
            variables_str = ", ".join(point.variables)
            lines.append(f"- **{point.reference_id}**: [{point.step_name}](#{point.reference_id.lower()}-{point.step_name.lower().replace(' ', '-')}) ({variables_str})")

        lines.append("")
        return '\n'.join(lines)

    def _generate_distribution_analysis_section(
        self, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate distribution analysis section organized by variable."""
        lines = []
        lines.append("## 2. Distribution Analysis by Variable")
        lines.append("")

        # Collect all variables across all analysis points
        all_variables = set()
        for point in analysis_points:
            all_variables.update(point.variables)

        # Generate section for each variable
        for variable in sorted(all_variables):
            lines.append(f"### 2.{list(sorted(all_variables)).index(variable) + 1} Variable: `{variable}` {{#{variable}-analysis}}")
            lines.append("")

            # Create table for this variable
            variable_points = [p for p in analysis_points if variable in p.variables]

            # Deduplicate analysis points by function name to avoid showing the same analysis multiple times
            unique_points = []
            seen_functions = set()
            for point in variable_points:
                if point.function_name not in seen_functions:
                    unique_points.append(point)
                    seen_functions.add(point.function_name)

            print(f"Variable {variable}: {len(variable_points)} total points, {len(unique_points)} unique points")
            table_lines = self._create_variable_analysis_table(variable, unique_points)
            lines.extend(table_lines)

            # Add variable summary
            summary_lines = self._create_variable_summary(variable, variable_points)
            lines.extend(summary_lines)
            lines.append("")

        return '\n'.join(lines)

    def _create_variable_analysis_table(
        self, variable: str, analysis_points: List[DistributionAnalysisPoint]
    ) -> List[str]:
        """Create enhanced three-column table for variable analysis."""
        lines = []

        # Table header
        lines.append("| Analysis Step | Raw Distribution (All Data) | Cleaned Distribution (IQR Method) |")
        lines.append("|---------------|-----------------------------|-----------------------------------|")

        # Table rows
        for point in analysis_points:
            # Analysis step column with operation details
            step_desc = f"**[{point.reference_id}] {point.step_name}**<br/>"
            step_desc += f"*{self._get_operation_description(point)}*<br/>"

            # Add record change info if available
            if point.record_change:
                record_info = self._format_record_change_info(point.record_change)
                if record_info:
                    step_desc += record_info

            # Raw distribution column
            raw_plots = self._find_plots_for_variable(point, variable, "raw")
            raw_col = self._create_distribution_column(raw_plots, point, variable, "raw")

            # IQR cleaned distribution column
            iqr_plots = self._find_plots_for_variable(point, variable, "iqr")
            iqr_col = self._create_distribution_column(iqr_plots, point, variable, "iqr")

            lines.append(f"| {step_desc} | {raw_col} | {iqr_col} |")

        lines.append("")
        return lines

    def _get_operation_description(self, point: DistributionAnalysisPoint) -> str:
        """Get human-readable description of the operation."""
        # Convert function name to readable description
        function_name = point.function_name.lower()

        if 'filter' in function_name:
            return "Filter operation"
        elif 'join' in function_name:
            return "Join operation"
        elif 'group' in function_name or 'aggregate' in function_name:
            return "Aggregation operation"
        elif 'select' in function_name:
            return "Selection operation"
        elif 'transform' in function_name:
            return "Transformation operation"
        else:
            return f"Custom operation: {point.step_name}"

    def _format_record_change_info(self, record_change: Dict[str, int]) -> str:
        """Format record change information."""
        info_parts = []

        for method, change in record_change.items():
            if method.endswith('_records'):
                if change != 0:
                    change_str = f"+{change:,}" if change > 0 else f"{change:,}"
                    percentage = ""  # We could calculate percentage if we had before counts
                    info_parts.append(f"Records: {change_str}")

        return "<br/>".join(info_parts) if info_parts else ""

    def _find_plots_for_variable(
        self, point: DistributionAnalysisPoint, variable: str, method: str
    ) -> List[str]:
        """Find plot files for a specific variable and method."""
        plots = []

        logger.debug(f"Looking for plots: variable={variable}, method={method}")
        logger.debug(f"Available plots: {point.plot_results}")

        # Check if we have plot_objects with more detailed info
        metadata = point.metadata or {}
        plot_objects = metadata.get('plot_objects', [])

        if plot_objects:
            # Use the detailed plot objects information
            for plot_obj in plot_objects:
                if (plot_obj.get('variable_name') == variable and
                    self._method_matches_plot_type(method, plot_obj.get('plot_type', ''), plot_obj.get('file_path', ''))):
                    plots.append(plot_obj['file_path'])
                    logger.debug(f"Found matching plot from objects: {plot_obj['file_path']}")
        else:
            # Fallback to original plot path matching
            for plot_path in point.plot_results:
                plot_name = Path(plot_path).name.lower()

                # Check if this plot matches the variable and method
                variable_match = variable.lower() in plot_name

                # Handle different method names with strict matching
                method_match = False
                if method == "raw" or method == "none":
                    method_match = ("raw" in plot_name and "clean" not in plot_name)
                elif method == "iqr":
                    method_match = ("clean" in plot_name or "iqr" in plot_name)
                else:
                    method_match = method.lower() in plot_name

                if variable_match and method_match:
                    logger.debug(f"Found matching plot: {plot_path}")
                    plots.append(plot_path)

        if not plots:
            logger.warning(f"No plots found for variable={variable}, method={method}")
            logger.warning(f"Available plot paths: {point.plot_results}")

        return plots

    def _method_matches_plot_type(self, method: str, plot_type: str, file_path: str) -> bool:
        """Check if a method matches a plot type or filename pattern."""
        plot_name = Path(file_path).name.lower()

        # Handle different method names with strict matching
        if method == "raw" or method == "none":
            return ("raw" in plot_name and "clean" not in plot_name)
        elif method == "iqr":
            return ("clean" in plot_name or "iqr" in plot_name)
        else:
            return method.lower() in plot_name

    def _create_distribution_column(
        self, plots: List[str], point: DistributionAnalysisPoint, variable: str, method: str
    ) -> str:
        """Create distribution column content with plots and statistics."""
        lines = []

        # Add plot images
        for plot in plots:
            # Extract just the filename and reconstruct path relative to markdown file
            plot_path = Path(plot)
            filename = plot_path.name  # Just the filename like "quality_after_amount_raw.png"

            # Determine the relative path based on the actual plot location
            # Try to compute relative path from markdown output location to plot file
            if self._output_path:
                try:
                    # Get absolute paths
                    output_dir = self._output_path.parent

                    # If plot_path is not absolute, assume it's relative to output_dir
                    if not plot_path.is_absolute():
                        plot_abs_path = (output_dir / plot_path).resolve()
                    else:
                        plot_abs_path = plot_path.resolve()

                    # Compute relative path from markdown file to plot file
                    import os
                    relative_path = os.path.relpath(plot_abs_path, output_dir)
                    # Convert to forward slashes for markdown
                    relative_path = './' + relative_path.replace('\\', '/')
                except (ValueError, OSError):
                    # Fallback if paths are on different drives or relative path fails
                    relative_path = f'./assets/{filename}'
            else:
                # Fallback to default assets subdirectory
                relative_path = f'./assets/{filename}'

            # URL-encode the path to handle spaces and special characters
            # Keep the ./ prefix and encode only the rest
            if relative_path.startswith('./'):
                encoded_path = './' + quote(relative_path[2:], safe='/')
            else:
                encoded_path = quote(relative_path, safe='/')

            print(f"  Converting plot path: {plot} -> {encoded_path}")
            lines.append(f"![{variable} {method} {point.reference_id}]({encoded_path})")

        # Add statistics if available
        stats = self._extract_variable_stats(point, variable, method)
        if stats:
            lines.append("**Statistics:**")
            for stat_name, stat_value in stats.items():
                if isinstance(stat_value, (int, float)):
                    if isinstance(stat_value, float):
                        formatted_value = f"{stat_value:,.2f}"
                    else:
                        formatted_value = f"{stat_value:,}"
                    lines.append(f"- {stat_name.title()}: {formatted_value}")

        return "<br/>".join(lines) if lines else "No data available"

    def _extract_variable_stats(
        self, point: DistributionAnalysisPoint, variable: str, method: str
    ) -> Dict[str, Any]:
        """Extract statistics for a specific variable and method."""
        stats = {}

        # Look in after_stats for the method
        method_stats = point.after_stats.get(method, {})
        variable_stats = method_stats.get(variable, {})

        if isinstance(variable_stats, dict):
            # Extract common statistics
            for stat_name in ['mean', 'std', 'count', 'min', 'max']:
                if stat_name in variable_stats:
                    stats[stat_name] = variable_stats[stat_name]

        return stats

    def _create_variable_summary(
        self, variable: str, analysis_points: List[DistributionAnalysisPoint]
    ) -> List[str]:
        """Create summary statistics for a variable across all analysis points."""
        lines = []
        summary_content = []

        if analysis_points:
            # Get initial and final values
            first_point = analysis_points[0]
            last_point = analysis_points[-1]

            # Extract means for comparison
            initial_stats = self._extract_variable_stats(first_point, variable, "none")
            final_stats = self._extract_variable_stats(last_point, variable, "none")

            if initial_stats.get('mean') and final_stats.get('mean'):
                initial_mean = initial_stats['mean']
                final_mean = final_stats['mean']
                mean_change = ((final_mean - initial_mean) / initial_mean) * 100

                summary_content.append(f"- Initial Mean: {initial_mean:,.2f} -> Final Mean: {final_mean:,.2f} ({mean_change:+.1f}% overall)")

            # Find most significant change point
            max_change_point = None
            max_change_pct = 0

            for point in analysis_points:
                if point.record_change:
                    for method, change in point.record_change.items():
                        # Rough percentage calculation (would need before counts for accuracy)
                        if abs(change) > abs(max_change_pct):
                            max_change_pct = change
                            max_change_point = point

            if max_change_point:
                summary_content.append(f"- Most Significant Change: {max_change_point.reference_id}")

        # Only add header and content if we have something to show
        if summary_content:
            lines.append(f"**Summary for `{variable}`:**")
            lines.extend(summary_content)
            lines.append("")

        return lines

    def _generate_cross_analysis_section(
        self, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate cross-variable analysis section."""
        lines = []
        lines.append("## 4. Cross-Variable Analysis")
        lines.append("")

        # Cross-step summary table
        lines.append("### 4.1 Distribution Change Summary")
        lines.append("")
        lines.append("| Step | Variables | Key Changes |")
        lines.append("|------|-----------|-------------|")

        for point in analysis_points:
            variables_str = ", ".join(point.variables)
            # Summarize key changes (placeholder - would need actual change analysis)
            key_changes = "Data transformation applied"
            if point.record_change:
                total_change = sum(point.record_change.values())
                if total_change != 0:
                    change_str = f"+{total_change:,}" if total_change > 0 else f"{total_change:,}"
                    key_changes = f"Records: {change_str}"

            step_link = f"[{point.reference_id}](#{point.reference_id.lower()}-{point.step_name.lower().replace(' ', '-')})"
            lines.append(f"| {step_link} | {variables_str} | {key_changes} |")

        lines.append("")

        # Data quality insights
        lines.append("### 4.2 Data Quality Insights")
        lines.append("")
        lines.append("- **Outlier Impact**: IQR cleaning removes outliers consistently across steps")
        lines.append("- **Distribution Stability**: Variable distributions show expected changes through pipeline")

        # Add specific insights if available
        if analysis_points:
            total_steps = len(analysis_points)
            lines.append(f"- **Pipeline Complexity**: {total_steps} analysis points across data processing")

        lines.append("")
        return '\n'.join(lines)

    def _generate_expression_lineage_section(self) -> str:
        """Generate expression lineage analysis section."""
        lines = []
        lines.append("## 3. Expression Lineage Analysis")
        lines.append("")
        lines.append("This section shows the mathematical formulas used to create each column,")
        lines.append("reconstructed from PySpark's execution plans.")
        lines.append("")

        # Try to get expression lineages from global tracker
        expression_lineages = []
        try:
            from ..core.lineage_tracker import get_global_tracker
            tracker = get_global_tracker()
            # Initialize the attribute if it doesn't exist
            if not hasattr(tracker, '_expression_lineages'):
                tracker._expression_lineages = []
            expression_lineages = getattr(tracker, '_expression_lineages', [])
            print(f"Retrieved {len(expression_lineages)} expression lineages from tracker")
            logger.debug(f"Retrieved {len(expression_lineages)} expression lineages from tracker")
        except Exception as e:
            print(f"Could not retrieve expression lineages from tracker: {e}")
            logger.debug(f"Could not retrieve expression lineages from tracker: {e}")

        if not expression_lineages:
            lines.append("*No expression lineages captured. Use @expressionLineage decorator to track column formulas.*")
            lines.append("")
            return '\n'.join(lines)

        # Group expressions by function
        lines.append("### Column Expression Formulas")
        lines.append("")

        for lineage in expression_lineages:
            function_name = lineage['function_name']
            expressions = lineage['expressions']

            if expressions:
                lines.append(f"#### Function: `{function_name}`")
                lines.append("")

                # Create table of expressions
                lines.append("| Column | Expression | Type | Sources |")
                lines.append("|--------|------------|------|---------|")

                for col_name, expr in expressions.items():
                    # Format expression for table
                    formula = expr.expression if hasattr(expr, 'expression') else str(expr)
                    op_type = expr.operation_type if hasattr(expr, 'operation_type') else 'unknown'
                    sources = ', '.join(expr.source_columns) if hasattr(expr, 'source_columns') else 'unknown'

                    # Escape pipe characters in formula for markdown table
                    formula = formula.replace('|', '\\|')

                    lines.append(f"| **{col_name}** | `{formula}` | {op_type} | {sources} |")

                lines.append("")

        # Add expression complexity analysis
        lines.append("### Expression Complexity Analysis")
        lines.append("")

        complexity_stats = {'simple': 0, 'arithmetic': 0, 'function': 0, 'conditional': 0, 'aggregation': 0}
        total_expressions = 0

        for lineage in expression_lineages:
            for col_name, expr in lineage['expressions'].items():
                total_expressions += 1
                op_type = expr.operation_type if hasattr(expr, 'operation_type') else 'simple'
                if op_type in complexity_stats:
                    complexity_stats[op_type] += 1

        if total_expressions > 0:
            lines.append("| Expression Type | Count | Percentage |")
            lines.append("|-----------------|-------|------------|")

            for expr_type, count in complexity_stats.items():
                if count > 0:
                    percentage = (count / total_expressions) * 100
                    lines.append(f"| {expr_type.title()} | {count} | {percentage:.1f}% |")

            lines.append("")
            lines.append(f"**Total Expressions Captured**: {total_expressions}")
        else:
            lines.append("*No expression statistics available.*")

        lines.append("")
        return '\n'.join(lines)

    def _generate_distribution_details_section(
        self, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate detailed distribution analysis section."""
        lines = []
        lines.append("## Distribution Analysis Details")
        lines.append("")

        for point in analysis_points:
            # Section header with anchor
            anchor_id = f"{point.reference_id.lower()}-{point.step_name.lower().replace(' ', '-')}"
            lines.append(f"### {point.reference_id}: {point.step_name} {{#{anchor_id}}}")
            lines.append(f"*Operation: {self._get_operation_description(point)}*")
            lines.append("")

            # Impact summary
            if point.record_change:
                impact_parts = []
                for method, change in point.record_change.items():
                    if method.endswith('_records') and change != 0:
                        change_str = f"+{change:,}" if change > 0 else f"{change:,}"
                        impact_parts.append(f"Records: {change_str}")

                if impact_parts:
                    lines.append(f"**Impact:** {', '.join(impact_parts)}")
                    lines.append("")

            # Variables analyzed
            variables_str = ", ".join(point.variables)
            lines.append(f"**Variables Analyzed:** {variables_str}")
            lines.append("")

            # Individual variable details (placeholder for future expansion)
            lines.append("*Detailed distribution analysis for this step*")
            lines.append("")

            # Back to overview link
            lines.append("[Back to Pipeline Overview](#1-pipeline-flow-visualization)")
            lines.append("")

        return '\n'.join(lines)

    def _generate_technical_details_section(
        self, lineage_graph: LineageGraph, analysis_points: List[DistributionAnalysisPoint]
    ) -> str:
        """Generate technical details section."""
        lines = []
        lines.append("## 5. Technical Details")
        lines.append("")

        # Pipeline statistics
        lines.append("### 5.1 Pipeline Statistics")
        lines.append("")
        lines.append(f"- **Total Nodes**: {len(lineage_graph.nodes)}")
        lines.append(f"- **Total Edges**: {len(lineage_graph.edges)}")
        lines.append(f"- **Analysis Points**: {len(analysis_points)}")

        # Execution timing if available
        if any(point.execution_time for point in analysis_points):
            total_time = sum(point.execution_time or 0 for point in analysis_points)
            lines.append(f"- **Total Analysis Time**: {total_time:.3f}s")

        lines.append("")

        # Analysis configuration
        lines.append("### 5.2 Analysis Configuration")
        lines.append("")
        lines.append("- **Outlier Methods**: IQR, Raw (no outlier removal)")
        lines.append("- **Sampling**: Applied as configured per analysis point")
        lines.append("- **Plot Generation**: Automatic with markdown integration")
        lines.append("")

        return '\n'.join(lines)

    def _assemble_final_report(
        self, sections: Dict[str, str], include_cross_analysis: bool
    ) -> str:
        """Assemble all sections into the final report."""
        lines = []

        # Report header
        lines.append(f"# {self.config.title}")
        lines.append("*Data Lineage with Integrated Distribution Monitoring*")
        lines.append("")
        lines.append(f"*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        if 'executive_summary' in sections:
            lines.append("- [Executive Summary](#executive-summary)")
        lines.append("- [1. Pipeline Flow Visualization](#1-pipeline-flow-visualization)")
        lines.append("- [2. Distribution Analysis by Variable](#2-distribution-analysis-by-variable)")
        lines.append("- [3. Expression Lineage Analysis](#3-expression-lineage-analysis)")
        if include_cross_analysis:
            lines.append("- [4. Cross-Variable Analysis](#4-cross-variable-analysis)")
        lines.append("- [Distribution Analysis Details](#distribution-analysis-details)")
        if 'technical_details' in sections:
            lines.append("- [5. Technical Details](#5-technical-details)")
        lines.append("")

        # Add sections in order
        section_order = [
            'executive_summary',
            'pipeline_overview',
            'distribution_analysis',
            'expression_lineage',
            'cross_analysis',
            'distribution_details',
            'technical_details'
        ]

        for section_name in section_order:
            if section_name in sections:
                if not include_cross_analysis and section_name == 'cross_analysis':
                    continue
                lines.append(sections[section_name])

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Report generated by PySpark StoryDoc - Unified Analysis System*")
        lines.append("")

        return '\n'.join(lines)


def generate_unified_lineage_report(
    lineage_graph: LineageGraph,
    output_path: str,
    title: str = "Unified Pipeline Analysis Report",
    include_cross_analysis: bool = True,
    table_layout: str = "per_variable"
) -> str:
    """
    Convenience function to generate unified lineage report.

    Args:
        lineage_graph: Complete lineage graph
        output_path: Output file path
        title: Report title
        include_cross_analysis: Include cross-step analysis section
        table_layout: How to organize distribution tables

    Returns:
        Path to generated report
    """
    config = UnifiedReportConfig(
        title=title,
        include_cross_analysis=include_cross_analysis,
        table_layout=table_layout
    )

    generator = UnifiedReportGenerator(config)

    # Try to get distribution analyses from global tracker
    distribution_analyses = []
    try:
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        # Initialize the attribute if it doesn't exist
        if not hasattr(tracker, '_distribution_analyses'):
            tracker._distribution_analyses = []
        distribution_analyses = getattr(tracker, '_distribution_analyses', [])
        logger.debug(f"Retrieved {len(distribution_analyses)} distribution analyses from tracker")
    except Exception as e:
        logger.debug(f"Could not retrieve distribution analyses from tracker: {e}")

    return generator.generate_unified_lineage_report(
        lineage_graph=lineage_graph,
        output_path=output_path,
        distribution_analyses=distribution_analyses,
        title=title,
        include_cross_analysis=include_cross_analysis
    )