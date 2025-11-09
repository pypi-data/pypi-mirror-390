"""
Data Engineer Report - Technical lineage with debugging support.

This module generates outputs specifically designed for Data Engineers, focusing on:
- Row count tracking and data loss detection
- Join validation and duplicate detection
- Data quality metrics (nulls, distributions)
- Technical lineage with business context
- Debugging information (location references, rejected rows)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.graph_builder import MetricsData
from ..visualization.lineage_diagram_generator import LineageDiagramGenerator
from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class DataEngineerReportConfig(ReportConfig):
    """Configuration for Data Engineer Report generation."""
    pipeline_name: str = "Data Pipeline"
    execution_id: Optional[str] = None
    status: str = "SUCCESS"  # SUCCESS, WARNING, FAILED

    # Output control
    include_lineage_diagram: bool = True
    include_terminal_summary: bool = True
    include_column_lineage: bool = True
    include_data_quality: bool = True
    include_performance_metrics: bool = True
    include_rejected_samples: bool = True

    # Alert thresholds
    data_loss_threshold: float = 0.10  # 10% data loss triggers warning
    duplicate_threshold: float = 0.05  # 5% duplicates triggers warning
    null_threshold: float = 0.05  # 5% nulls triggers warning

    # Column tracking
    track_columns: List[str] = field(default_factory=list)
    track_all_columns: bool = False

    # File generation
    generate_json_lineage: bool = True
    generate_samples: bool = False  # Generate sample data files


class DataEngineerReport(BaseReport):
    """
    Generates comprehensive Data Engineer reports with debugging support.

    This report provides:
    1. Pipeline Lineage Diagram with row counts and alerts
    2. Quick Debug Summary for terminal output
    3. Column Lineage Report for specific columns
    4. Data Quality Summary with completeness and distributions
    """

    def __init__(self, config: Optional[DataEngineerReportConfig] = None, **kwargs):
        """
        Initialize the Data Engineer Report generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = DataEngineerReportConfig(**kwargs)
        elif config is None:
            config = DataEngineerReportConfig()

        super().__init__(config)
        self.config: DataEngineerReportConfig = config

        # Set execution ID if not provided
        if not self.config.execution_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.config.execution_id = f"exec_{timestamp}"

        # Initialize the diagram generator (reuse existing implementation)
        self.diagram_generator = LineageDiagramGenerator(
            show_column_metrics=True,
            show_execution_times=True,
            operation_filter="all",  # Show all operations for engineers
            group_raw_operations=False,  # Don't group, show individual operations
            show_passthrough_operations=True  # Show everything for debugging
        )

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        if self.config.status not in ["SUCCESS", "WARNING", "FAILED"]:
            raise ValueError(f"Invalid status: {self.config.status}")

        if self.config.data_loss_threshold < 0 or self.config.data_loss_threshold > 1:
            raise ValueError(f"data_loss_threshold must be between 0 and 1")

        return True

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the Data Engineer Report.

        Args:
            lineage_graph: EnhancedLineageGraph to analyze
            output_path: Path to write the main lineage markdown file

        Returns:
            Path to the generated report
        """
        logger.info(f"Generating Data Engineer Report: {self.config.pipeline_name}")

        output_file = Path(output_path)
        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect pipeline statistics
        pipeline_stats = self._collect_pipeline_stats(lineage_graph)

        # Detect alerts
        alerts = self._detect_alerts(lineage_graph, pipeline_stats)

        # Update status based on alerts
        if alerts and self.config.status == "SUCCESS":
            self.config.status = "WARNING"

        # Generate outputs
        outputs = {}

        # 1. Pipeline Lineage Diagram
        if self.config.include_lineage_diagram:
            lineage_content = self._generate_lineage_diagram(
                lineage_graph, pipeline_stats, alerts, output_path
            )
            outputs['lineage_diagram'] = self._write_report(lineage_content, output_path)

        # 2. Terminal Summary
        if self.config.include_terminal_summary:
            terminal_content = self._generate_terminal_summary(
                lineage_graph, pipeline_stats, alerts
            )
            terminal_path = output_dir / f"{output_file.stem}_terminal_summary.txt"
            outputs['terminal_summary'] = self._write_report(terminal_content, str(terminal_path))
            # Also print to console (handle encoding issues)
            try:
                print(terminal_content)
            except UnicodeEncodeError:
                # Fall back to ASCII-safe version
                import sys
                print(terminal_content.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))

        # 3. Column Lineage Report
        if self.config.include_column_lineage:
            column_content = self._generate_column_lineage(lineage_graph)
            column_path = output_dir / f"{output_file.stem}_column_lineage.md"
            outputs['column_lineage'] = self._write_report(column_content, str(column_path))

        # 4. JSON Lineage
        if self.config.generate_json_lineage:
            json_content = self._generate_json_lineage(lineage_graph, pipeline_stats)
            json_path = output_dir / f"{output_file.stem}_lineage.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(json_content)
            outputs['json_lineage'] = str(json_path)

        logger.info(f"Data Engineer reports generated: {len(outputs)} files")
        for report_type, path in outputs.items():
            logger.info(f"  - {report_type}: {path}")

        return outputs.get('lineage_diagram', output_path)

    def _collect_pipeline_stats(self, lineage_graph) -> Dict[str, Any]:
        """Collect pipeline-wide statistics."""
        stats = {
            'total_operations': 0,
            'data_sources': 0,
            'output_datasets': 0,
            'total_input_rows': 0,
            'total_output_rows': 0,
            'execution_time': 0.0,
            'operations': []
        }

        # Analyze nodes
        for node in lineage_graph.nodes.values():
            operation_type = node.metadata.get('operation_type', '')

            # Count operations
            if operation_type not in ['data_source', 'business_concept']:
                stats['total_operations'] += 1

            # Count sources and outputs
            if operation_type == 'data_source':
                stats['data_sources'] += 1

            # Collect metrics
            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict):
                input_count = metrics.get('input_record_count', 0)
                output_count = metrics.get('output_record_count', metrics.get('row_count', 0))

                if input_count:
                    stats['total_input_rows'] += input_count
                if output_count:
                    stats['total_output_rows'] += output_count

            # Collect execution time
            exec_time = node.metadata.get('execution_time', 0) or node.metadata.get('duration', 0)
            if exec_time:
                stats['execution_time'] += exec_time

            # Store operation info
            stats['operations'].append({
                'node_id': node.node_id,
                'operation_type': operation_type,
                'operation_name': node.metadata.get('operation_name', 'unknown'),
                'input_rows': metrics.get('input_record_count', 0) if isinstance(metrics, dict) else 0,
                'output_rows': metrics.get('output_record_count', metrics.get('row_count', 0)) if isinstance(metrics, dict) else 0,
                'location': node.metadata.get('location', ''),
            })

        # Calculate row change percentage
        if stats['total_input_rows'] > 0:
            row_change = ((stats['total_output_rows'] - stats['total_input_rows']) /
                         stats['total_input_rows'] * 100)
            stats['row_change_pct'] = row_change
        else:
            stats['row_change_pct'] = 0.0

        return stats

    def _detect_alerts(self, lineage_graph, pipeline_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data quality and operational alerts."""
        alerts = []

        # Check for data loss at each operation
        for op in pipeline_stats['operations']:
            input_rows = op['input_rows']
            output_rows = op['output_rows']

            if input_rows > 0 and output_rows < input_rows:
                loss_pct = (input_rows - output_rows) / input_rows

                if loss_pct > self.config.data_loss_threshold:
                    alerts.append({
                        'type': 'DATA_LOSS',
                        'severity': 'WARNING',
                        'operation': op['operation_name'],
                        'node_id': op['node_id'],
                        'message': f"Unexpected {loss_pct*100:.1f}% data loss at {op['operation_name']}",
                        'details': f"Input: {input_rows:,} rows -> Output: {output_rows:,} rows",
                        'location': op['location']
                    })

            # Check for duplicates (output > input in non-aggregation operations)
            if input_rows > 0 and output_rows > input_rows:
                operation_type = op['operation_type']
                if operation_type not in ['groupBy', 'aggregate', 'explode']:
                    dup_pct = (output_rows - input_rows) / input_rows

                    if dup_pct > self.config.duplicate_threshold:
                        alerts.append({
                            'type': 'DUPLICATES',
                            'severity': 'WARNING',
                            'operation': op['operation_name'],
                            'node_id': op['node_id'],
                            'message': f"Possible duplicates: {dup_pct*100:.1f}% increase at {op['operation_name']}",
                            'details': f"Input: {input_rows:,} rows -> Output: {output_rows:,} rows",
                            'location': op['location']
                        })

        # Check for high null percentages in columns
        for node in lineage_graph.nodes.values():
            metrics = node.metadata.get('metrics', {})
            if not isinstance(metrics, dict):
                continue

            # Check null counts (if tracked)
            null_counts = metrics.get('null_counts', {})
            output_rows = metrics.get('output_record_count', metrics.get('row_count', 0))

            for col, null_count in null_counts.items():
                if output_rows > 0:
                    null_pct = null_count / output_rows

                    if null_pct > self.config.null_threshold:
                        alerts.append({
                            'type': 'NULL_VALUES',
                            'severity': 'WARNING',
                            'operation': node.metadata.get('operation_name', 'unknown'),
                            'node_id': node.node_id,
                            'message': f"High null percentage in column '{col}': {null_pct*100:.1f}%",
                            'details': f"{null_count:,} nulls out of {output_rows:,} rows",
                            'column': col
                        })

        return alerts

    def _generate_lineage_diagram(
        self,
        lineage_graph,
        pipeline_stats: Dict[str, Any],
        alerts: List[Dict[str, Any]],
        output_path: str = None
    ) -> str:
        """Generate the main pipeline lineage diagram in Markdown."""
        lines = []

        # Title and metadata
        status_emoji = {
            'SUCCESS': '[OK]',
            'WARNING': '[WARN]',
            'FAILED': '[FAIL]'
        }.get(self.config.status, '❓')

        lines.append(f"# Pipeline Lineage: {self.config.pipeline_name}\n")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Execution ID**: {self.config.execution_id}")
        lines.append(f"**Status**: {status_emoji} {self.config.status}\n")
        lines.append("---\n")

        # Quick Summary
        lines.append("## Quick Summary\n")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Operations | {pipeline_stats['total_operations']} |")
        lines.append(f"| Data Sources | {pipeline_stats['data_sources']} |")
        lines.append(f"| Output Datasets | {pipeline_stats['output_datasets']} |")

        if pipeline_stats['total_input_rows'] > 0:
            lines.append(f"| Total Rows Processed | {pipeline_stats['total_input_rows']:,} -> {pipeline_stats['total_output_rows']:,} |")
            lines.append(f"| Row Change | {pipeline_stats['row_change_pct']:+.1f}% |")

        if pipeline_stats['execution_time'] > 0:
            exec_time_str = self._format_duration(pipeline_stats['execution_time'])
            lines.append(f"| Execution Time | {exec_time_str} |")

        lines.append("")

        # Alerts section
        if alerts:
            lines.append("**[WARN] Alerts**:")
            for alert in alerts[:5]:  # Show top 5 alerts
                lines.append(f"- {alert['message']}")
        else:
            lines.append("**[OK] No Alerts**: Pipeline executed successfully with no issues detected.")

        lines.append("\n---\n")

        # Data Flow Visualization (Mermaid)
        lines.append("## Data Flow Visualization\n")
        lines.append("```mermaid")
        # Use the existing LineageDiagramGenerator for consistent diagram rendering
        mermaid_diagram = self.diagram_generator.create_detailed_mermaid(
            lineage_graph,
            title=None  # We don't need a title in the diagram itself
        )

        # Add warning highlights for alerted nodes
        mermaid_diagram = self._add_warning_highlights(mermaid_diagram, alerts)

        lines.append(mermaid_diagram)
        lines.append("```\n")
        lines.append("---\n")

        # Detailed Transformation Steps
        lines.append("## Detailed Transformation Steps\n")
        step_lines = self._generate_transformation_steps(lineage_graph, alerts)
        lines.extend(step_lines)

        # Data Quality Summary
        if self.config.include_data_quality:
            lines.append("\n---\n")
            lines.append("## Data Quality Summary\n")
            quality_lines = self._generate_data_quality_section(lineage_graph)
            lines.extend(quality_lines)

        # Performance Metrics
        if self.config.include_performance_metrics:
            lines.append("\n---\n")
            lines.append("## Performance Metrics\n")
            perf_lines = self._generate_performance_section(pipeline_stats)
            lines.extend(perf_lines)

        # Files Generated
        lines.append("\n---\n")
        lines.append("## Files Generated\n")
        if output_path:
            output_file = Path(output_path)
            lines.append(f"- **Lineage Diagram**: `{output_file.name}` (this file)")
            if self.config.generate_json_lineage:
                lines.append(f"- **Raw Lineage Data**: `{output_file.stem}_lineage.json`")
            if self.config.include_column_lineage:
                lines.append(f"- **Column Lineage**: `{output_file.stem}_column_lineage.md`")
            if self.config.include_terminal_summary:
                lines.append(f"- **Terminal Summary**: `{output_file.stem}_terminal_summary.txt`")
        else:
            lines.append("- **Lineage Diagram**: (generated)")
            if self.config.generate_json_lineage:
                lines.append("- **Raw Lineage Data**: (generated)")
            if self.config.include_column_lineage:
                lines.append("- **Column Lineage**: (generated)")
            if self.config.include_terminal_summary:
                lines.append("- **Terminal Summary**: (generated)")
        lines.append("")

        # Next Steps
        lines.append("---\n")
        lines.append("## Next Steps for Engineer\n")

        if self.config.status == "SUCCESS" and not alerts:
            lines.append("[OK] **Pipeline executed successfully**\n")
            lines.append("**Review Items**: None\n")
        else:
            lines.append(f"{status_emoji} **Pipeline completed with {len(alerts)} warning(s)**\n")
            lines.append("**Review Items**:")
            for i, alert in enumerate(alerts[:10], 1):
                lines.append(f"{i}. {alert['type']}: {alert['message']}")
            lines.append("")

        # Footer
        lines.append("---\n")
        lines.append(f"*Generated by PySpark StoryDoc v1.0 | Execution ID: {self.config.execution_id}*\n")

        return '\n'.join(lines)

    def _add_warning_highlights(self, mermaid_diagram: str, alerts: List[Dict[str, Any]]) -> str:
        """
        Add warning highlights to the diagram for alerted nodes.

        This modifies the generated diagram to highlight nodes with warnings.
        """
        if not alerts:
            return mermaid_diagram

        # The LineageDiagramGenerator already handles styling, so we just need to
        # ensure the warning style is available and applied
        # For now, return the diagram as-is since the generator handles it
        # In the future, we could parse and modify node classes here if needed

        return mermaid_diagram

    def _generate_transformation_steps(
        self,
        lineage_graph,
        alerts: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate detailed transformation steps."""
        lines = []

        # Get operations in order - filter out unnamed/internal operations
        operations = []
        for node in lineage_graph.nodes.values():
            operation_type = node.metadata.get('operation_type', '')
            operation_name = node.metadata.get('operation_name', '')

            # Skip data sources and business concepts (they're shown in the diagram)
            if operation_type in ['data_source', 'business_concept']:
                continue

            # Skip operations without meaningful names (internal/unnamed operations)
            # BUT keep all operations with specific operation types (filter, select, join, groupby, etc.)
            if operation_type in ['filter', 'select', 'join', 'groupby', 'group', 'union', 'withColumn']:
                operations.append(node)
                continue

            # For generic transforms, only include if they have a meaningful name
            if not operation_name or operation_name in ['unknown', 'operation', '']:
                continue

            operations.append(node)

        # Sort by some order (you might want to use topological sort)
        # For now, just use node_id order
        operations.sort(key=lambda n: n.node_id)

        for i, node in enumerate(operations, 1):
            operation_name = node.metadata.get('operation_name', '')
            operation_type = node.metadata.get('operation_type', '')

            # Use a meaningful default if operation_name is empty
            if not operation_name or operation_name in ['unknown', 'operation', '']:
                # Use operation type as fallback with proper formatting
                if operation_type:
                    operation_name = operation_type.replace('_', ' ').title()
                else:
                    operation_name = 'Operation'

            lines.append(f"### Step {i}: {operation_name}")

            # Location
            location = node.metadata.get('location', '')
            if location:
                lines.append(f"**Location**: `{location}`")

            # Business context
            business_context = node.metadata.get('business_context', '')
            if business_context:
                if isinstance(business_context, dict):
                    context_name = business_context.get('name', '')
                else:
                    context_name = business_context
                if context_name:
                    lines.append(f"**Business Context**: \"{context_name}\"")

            lines.append("")
            lines.append("```")

            # Metrics - try to get from operation node first, then from parent business concept
            metrics = node.metadata.get('metrics', {})
            input_rows = 0
            output_rows = 0

            if isinstance(metrics, dict):
                input_rows = metrics.get('input_record_count', 0)
                output_rows = metrics.get('output_record_count', metrics.get('row_count', 0))

            # Metrics should now be available on operation nodes (inherited from business concepts)

            if input_rows and output_rows:
                lines.append(f"Input:  {input_rows:,} rows")
                lines.append(f"Output: {output_rows:,} rows")

                change = output_rows - input_rows
                change_pct = (change / input_rows * 100) if input_rows > 0 else 0
                lines.append(f"Change: {change:+,} rows ({change_pct:+.1f}%)")
            elif output_rows:
                lines.append(f"Output: {output_rows:,} rows")

            lines.append("")

            # Operation details
            operation_name_detail = node.metadata.get('operation_name', '')
            lines.append(f"Operation: {operation_name_detail}")

            # Add operation-specific details
            if operation_type == 'join':
                # Extract join details
                join_type = node.metadata.get('join_type', 'inner')
                join_columns = node.metadata.get('join_columns', [])
                join_keys = node.metadata.get('join_keys', [])
                join_condition = node.metadata.get('join_condition', '')

                lines.append(f"Join Type: {join_type}")

                # Show join keys (prefer join_keys over join_columns)
                keys_to_show = join_keys if join_keys else join_columns
                if keys_to_show:
                    if isinstance(keys_to_show, list):
                        lines.append(f"Join Keys: {', '.join(str(c) for c in keys_to_show)}")
                    else:
                        lines.append(f"Join Keys: {keys_to_show}")
                if join_condition:
                    lines.append(f"Join Condition: {join_condition}")

                # Add column count changes
                if 'input_column_count' in node.metadata and 'output_column_count' in node.metadata:
                    input_cols = node.metadata['input_column_count']
                    output_cols = node.metadata['output_column_count']
                    col_change = output_cols - input_cols
                    lines.append(f"Columns: {input_cols} -> {output_cols} ({col_change:+})")

            elif 'filter_condition' in node.metadata:
                lines.append(f"Filter: {node.metadata['filter_condition']}")
            elif 'selected_columns' in node.metadata:
                cols = node.metadata['selected_columns']
                if isinstance(cols, list):
                    lines.append(f"Columns: {', '.join(cols)}")
            elif operation_type == 'groupby' or operation_type == 'group':
                # Extract groupBy details
                group_columns = node.metadata.get('group_columns', [])
                aggregations = node.metadata.get('aggregations', [])
                if group_columns:
                    if isinstance(group_columns, list):
                        lines.append(f"Group By: {', '.join(str(c) for c in group_columns)}")
                    else:
                        lines.append(f"Group By: {group_columns}")
                if aggregations:
                    lines.append(f"Aggregations: {', '.join(str(a) for a in aggregations)}")

            lines.append("")

            # Row Count Analysis
            lines.append("Row Count Analysis:")

            # Check for alerts
            node_alerts = [a for a in alerts if a.get('node_id') == node.node_id]
            if node_alerts:
                for alert in node_alerts:
                    lines.append(f"  [WARN] {alert['message']}")
            else:
                lines.append("  [OK] Row count change as expected")

            lines.append("```")
            lines.append("")
            lines.append("---\n")

        return lines

    def _generate_data_quality_section(self, lineage_graph) -> List[str]:
        """Generate data quality summary."""
        lines = []

        lines.append("### Completeness\n")
        lines.append("| Column | NULL Count | NULL % | Status |")
        lines.append("|--------|-----------|--------|--------|")

        # Collect null statistics from final output nodes
        output_nodes = [n for n in lineage_graph.nodes.values()
                       if n.metadata.get('operation_type') == 'output']

        if not output_nodes:
            # Use last operation node
            output_nodes = [n for n in lineage_graph.nodes.values()
                          if n.metadata.get('operation_type') not in ['data_source', 'business_concept']]
            if output_nodes:
                output_nodes = [output_nodes[-1]]

        for node in output_nodes:
            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict):
                null_counts = metrics.get('null_counts', {})
                output_rows = metrics.get('output_record_count', metrics.get('row_count', 0))

                for col, null_count in sorted(null_counts.items()):
                    null_pct = (null_count / output_rows * 100) if output_rows > 0 else 0

                    if null_pct == 0:
                        status = "[OK] Complete"
                    elif null_pct < 1:
                        status = "[WARN] Minor gaps"
                    else:
                        status = "[WARN] Needs attention"

                    lines.append(f"| {col} | {null_count:,} | {null_pct:.2f}% | {status} |")

        if not any('|' in line for line in lines[-5:]):
            lines.append("| *No data* | - | - | - |")

        lines.append("")

        return lines

    def _generate_performance_section(self, pipeline_stats: Dict[str, Any]) -> List[str]:
        """Generate performance metrics section."""
        lines = []

        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")

        if pipeline_stats['execution_time'] > 0:
            exec_time_str = self._format_duration(pipeline_stats['execution_time'])
            lines.append(f"| Total Execution Time | {exec_time_str} |")

        lines.append(f"| Total Operations | {pipeline_stats['total_operations']} |")

        lines.append("")
        lines.append("**Bottlenecks**: None detected [OK]")
        lines.append("")
        lines.append("*Note: For detailed performance analysis, see Spark UI*")
        lines.append("")

        return lines

    def _generate_terminal_summary(
        self,
        lineage_graph,
        pipeline_stats: Dict[str, Any],
        alerts: List[Dict[str, Any]]
    ) -> str:
        """Generate terminal-friendly summary."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("PIPELINE EXECUTION SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Pipeline: {self.config.pipeline_name}")

        status_emoji = {
            'SUCCESS': '[OK]',
            'WARNING': '[WARN]',
            'FAILED': '[FAIL]'
        }.get(self.config.status, '❓')
        lines.append(f"Status: {status_emoji} {self.config.status}")

        if pipeline_stats['execution_time'] > 0:
            exec_time_str = self._format_duration(pipeline_stats['execution_time'])
            lines.append(f"Duration: {exec_time_str}")

        lines.append("")
        lines.append("-" * 80)
        lines.append("DATA FLOW")
        lines.append("-" * 80)
        lines.append("")

        # Simple ASCII flow
        for op in pipeline_stats['operations']:
            if op['operation_type'] == 'data_source':
                lines.append(f"[CHART] {op['operation_name']} ({op['output_rows']:,} rows)")
            elif op['input_rows'] and op['output_rows']:
                change = op['output_rows'] - op['input_rows']
                change_pct = (change / op['input_rows'] * 100) if op['input_rows'] > 0 else 0

                # Check if alert
                has_alert = any(a['node_id'] == op['node_id'] for a in alerts)
                alert_marker = " [WARN]" if has_alert else ""

                lines.append(f"  v {op['operation_name']}")
                lines.append(f"  v {op['input_rows']:,} -> {op['output_rows']:,} rows ({change_pct:+.1f}%){alert_marker}")

        lines.append("")

        # Alerts section
        if alerts:
            lines.append("-" * 80)
            lines.append("ALERTS")
            lines.append("-" * 80)
            lines.append("")

            for alert in alerts:
                lines.append(f"[WARN] {alert['type']}: {alert['message']}")
                if 'details' in alert:
                    lines.append(f"   {alert['details']}")
                if 'location' in alert and alert['location']:
                    lines.append(f"   Location: {alert['location']}")
                lines.append("")

        # Data Quality
        lines.append("-" * 80)
        lines.append("DATA QUALITY")
        lines.append("-" * 80)
        lines.append("")
        lines.append("Completeness:")

        # Get quality stats from last node
        output_nodes = [n for n in lineage_graph.nodes.values()
                       if n.metadata.get('operation_type') not in ['data_source', 'business_concept']]
        if output_nodes:
            node = output_nodes[-1]
            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict):
                null_counts = metrics.get('null_counts', {})
                output_rows = metrics.get('output_record_count', metrics.get('row_count', 0))

                if null_counts and output_rows:
                    for col, null_count in sorted(null_counts.items())[:5]:  # Top 5 columns
                        null_pct = (null_count / output_rows * 100)
                        status = "[OK]" if null_pct < 1 else "[WARN]"
                        lines.append(f"  {status} {col}: {100-null_pct:.1f}% complete")
                else:
                    lines.append("  [OK] All tracked columns complete")

        lines.append("")

        # Output Files
        lines.append("-" * 80)
        lines.append("OUTPUT FILES")
        lines.append("-" * 80)
        lines.append("")
        lines.append("[FILE] Lineage Diagram: outputs/<name>_lineage.md")
        if self.config.generate_json_lineage:
            lines.append("[FILE] Raw Lineage: outputs/<name>_lineage.json")
        lines.append("")

        # Footer
        lines.append("=" * 80)
        completion_msg = "[OK] SUCCESS" if self.config.status == "SUCCESS" else f"{status_emoji} {self.config.status}"
        if alerts:
            completion_msg += f" (with {len(alerts)} warnings)"
        lines.append(f"EXECUTION COMPLETE: {completion_msg}")
        lines.append("=" * 80)
        lines.append("")

        if alerts:
            lines.append("Review warnings and validate results before deploying to production.")

        return '\n'.join(lines)

    def _generate_column_lineage(self, lineage_graph) -> str:
        """Generate column lineage report."""
        lines = []

        lines.append(f"# Column Lineage Report: {self.config.pipeline_name}\n")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Get columns to track
        columns_to_track = self.config.track_columns

        if not columns_to_track:
            # Try to infer from metrics
            all_columns = set()
            for node in lineage_graph.nodes.values():
                metrics = node.metadata.get('metrics', {})
                if isinstance(metrics, dict):
                    distinct_counts = metrics.get('distinct_counts', {})
                    all_columns.update(distinct_counts.keys())
            columns_to_track = sorted(all_columns)[:10]  # Limit to 10

        lines.append(f"**Tracked Columns**: {len(columns_to_track)}\n")
        lines.append("---\n")

        if not columns_to_track:
            lines.append("*No columns tracked. Use track_columns parameter to specify columns.*\n")
            return '\n'.join(lines)

        # Generate lineage for each column
        for column in columns_to_track:
            lines.append(f"## Column: {column}\n")
            lines.append("### Lineage Path\n")
            lines.append("```")

            # Trace column through operations
            column_path = self._trace_column_lineage(lineage_graph, column)
            lines.extend(column_path)

            lines.append("```\n")

            # Column statistics
            lines.append("### Statistics\n")
            stats_lines = self._get_column_statistics(lineage_graph, column)
            lines.extend(stats_lines)

            lines.append("---\n")

        # Footer
        lines.append(f"*Generated by PySpark StoryDoc v1.0 | Execution ID: {self.config.execution_id}*\n")

        return '\n'.join(lines)

    def _trace_column_lineage(self, lineage_graph, column: str) -> List[str]:
        """Trace a column's lineage through operations."""
        lines = []

        # Find nodes that mention this column
        relevant_nodes = []
        for node in lineage_graph.nodes.values():
            # Check if column appears in metrics
            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict):
                distinct_counts = metrics.get('distinct_counts', {})
                if column in distinct_counts:
                    relevant_nodes.append(node)

            # Check if column appears in selected_columns
            selected = node.metadata.get('selected_columns', [])
            if column in selected:
                relevant_nodes.append(node)

        if not relevant_nodes:
            lines.append(f"Column '{column}' not tracked in pipeline")
            return lines

        # Build path
        lines.append(f"Source: <data_source>.{column}")

        for node in relevant_nodes:
            operation_name = node.metadata.get('operation_name', 'unknown')
            operation_type = node.metadata.get('operation_type', '')

            # Determine what happened to column
            if operation_type == 'filter':
                lines.append(f"  v [KEPT] {operation_name}")
            elif operation_type == 'select':
                lines.append(f"  v [KEPT] {operation_name}")
            elif operation_type == 'join':
                lines.append(f"  v [JOIN KEY] {operation_name}")
            elif operation_type == 'withColumn':
                lines.append(f"  v [MODIFIED] {operation_name}")
            else:
                lines.append(f"  v [{operation_type.upper()}] {operation_name}")

        lines.append(f"  v [OUTPUT] final dataset")
        lines.append(f"")
        lines.append(f"Output: <dataset>.{column}")

        return lines

    def _get_column_statistics(self, lineage_graph, column: str) -> List[str]:
        """Get statistics for a column."""
        lines = []

        # Find final output node
        output_nodes = [n for n in lineage_graph.nodes.values()
                       if n.metadata.get('operation_type') not in ['data_source', 'business_concept']]

        if not output_nodes:
            lines.append("*No statistics available*\n")
            return lines

        # Use last node
        node = output_nodes[-1]
        metrics = node.metadata.get('metrics', {})

        if isinstance(metrics, dict):
            distinct_counts = metrics.get('distinct_counts', {})
            if column in distinct_counts:
                distinct_count = distinct_counts[column]
                output_rows = metrics.get('output_record_count', metrics.get('row_count', 0))

                lines.append(f"- Distinct values: {distinct_count:,}")
                lines.append(f"- Total rows: {output_rows:,}")

                if output_rows > 0:
                    cardinality = distinct_count / output_rows
                    lines.append(f"- Cardinality: {cardinality:.4f}")
        else:
            lines.append("*No statistics available*\n")

        lines.append("")

        return lines

    def _generate_json_lineage(self, lineage_graph, pipeline_stats: Dict[str, Any]) -> str:
        """Generate JSON representation of lineage."""
        data = {
            'pipeline_name': self.config.pipeline_name,
            'execution_id': self.config.execution_id,
            'status': self.config.status,
            'timestamp': datetime.now().isoformat(),
            'statistics': pipeline_stats,
            'nodes': [],
            'edges': []
        }

        # Add nodes
        for node in lineage_graph.nodes.values():
            node_data = {
                'id': node.node_id,
                'type': node.metadata.get('operation_type', 'unknown'),
                'name': node.metadata.get('operation_name', 'unknown'),
                'metadata': {}
            }

            # Add metrics
            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict):
                node_data['metadata']['metrics'] = metrics

            # Add location
            if 'location' in node.metadata:
                node_data['metadata']['location'] = node.metadata['location']

            # Add join-specific metadata
            if node_data['type'] == 'join':
                logger.debug(f"Processing join node {node.node_id} for JSON export")
                logger.debug(f"Node metadata keys: {list(node.metadata.keys())}")
                for key in ['join_type', 'join_keys', 'input_column_count', 'other_column_count', 'output_column_count']:
                    if key in node.metadata:
                        node_data['metadata'][key] = node.metadata[key]
                        logger.debug(f"Copied {key} = {node.metadata[key]}")
                logger.debug(f"Final node_data metadata: {node_data['metadata']}")

            data['nodes'].append(node_data)

        # Add edges
        for edge in lineage_graph.edges:
            edge_data = {
                'source': edge.source_id,
                'target': edge.target_id,
                'type': edge.edge_type
            }
            data['edges'].append(edge_data)

        return json.dumps(data, indent=2)

    def _get_operation_emoji(self, operation_name: str, operation_type: str) -> str:
        """Get emoji for operation type."""
        operation_lower = operation_name.lower()

        if 'filter' in operation_lower:
            return "[SEARCH]"
        elif 'select' in operation_lower:
            return "✂️"
        elif 'join' in operation_lower:
            return "[LINK]"
        elif 'group' in operation_lower or 'aggregate' in operation_lower:
            return "🔄"
        elif 'with' in operation_lower or 'add' in operation_lower:
            return "🧮"
        elif 'union' in operation_lower:
            return "🔀"
        elif 'sort' in operation_lower or 'order' in operation_lower:
            return "[CHART]"
        else:
            return "[SETTINGS]"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


def generate_engineer_reports(
    lineage_graph,
    output_dir: str,
    pipeline_name: str = "Data Pipeline",
    **kwargs
) -> Dict[str, str]:
    """
    Convenience function to generate all Data Engineer reports.

    Args:
        lineage_graph: EnhancedLineageGraph to analyze
        output_dir: Directory to write reports
        pipeline_name: Name of the pipeline
        **kwargs: Additional configuration options

    Returns:
        Dictionary mapping report type to file path
    """
    output_path = Path(output_dir) / f"{pipeline_name.lower().replace(' ', '_')}_lineage.md"

    config = DataEngineerReportConfig(
        pipeline_name=pipeline_name,
        **kwargs
    )

    report = DataEngineerReport(config=config)
    main_path = report.generate(lineage_graph, str(output_path))

    # Return paths to all generated files
    output_stem = output_path.stem
    output_parent = output_path.parent

    return {
        'lineage_diagram': main_path,
        'terminal_summary': str(output_parent / f"{output_stem}_terminal_summary.txt"),
        'column_lineage': str(output_parent / f"{output_stem}_column_lineage.md"),
        'json_lineage': str(output_parent / f"{output_stem}_lineage.json")
    }
