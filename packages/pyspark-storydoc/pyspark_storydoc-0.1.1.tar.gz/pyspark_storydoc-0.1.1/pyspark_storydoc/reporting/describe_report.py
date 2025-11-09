#!/usr/bin/env python3
"""
Describe Profile Report Generator for PySpark StoryDoc.

This module generates comprehensive reports from describe() profiling data,
displaying descriptive statistics tables at each profiling checkpoint.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DescribeReportPoint:
    """Represents a single describe profiling checkpoint in the report."""
    reference_id: str
    checkpoint_name: str
    function_name: str
    columns: List[str]
    describe_table: List[Dict[str, Any]]  # Pandas DataFrame as dict
    row_count: int
    column_count: int
    timestamp: float
    parent_operation_id: Optional[str] = None
    metadata: Dict[str, Any] = None


class DescribeReportGenerator:
    """
    Generator for describe profiling reports.

    Creates markdown reports showing descriptive statistics tables
    at each profiling checkpoint in the data pipeline.
    """

    def __init__(self):
        """Initialize the describe report generator."""
        pass

    def generate_report(self,
                       profiles: List[Dict[str, Any]],
                       output_path: Optional[Path] = None) -> str:
        """
        Generate a markdown report from describe profiles.

        Args:
            profiles: List of profile data dictionaries from tracker
            output_path: Optional path to save the report

        Returns:
            Markdown content as string
        """
        if not profiles:
            logger.warning("No describe profiles found, generating empty report")
            return self._generate_empty_report()

        # Convert profiles to report points
        report_points = []
        for idx, profile in enumerate(profiles, 1):
            stats = profile.get('stats')
            if not stats:
                continue

            point = DescribeReportPoint(
                reference_id=f"DP-{idx:03d}",
                checkpoint_name=profile.get('checkpoint_name', 'Unknown'),
                function_name=profile.get('function_name', 'unknown'),
                columns=stats.columns,
                describe_table=stats.describe_df.to_dict('records'),
                row_count=stats.row_count,
                column_count=stats.column_count,
                timestamp=profile.get('timestamp', 0.0),
                parent_operation_id=stats.parent_operation_id,
                metadata=stats.metadata
            )
            report_points.append(point)

        # Generate markdown content
        content = self._build_report_content(report_points)

        # Save to file if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Describe report saved to: {output_path}")

        return content

    def _generate_empty_report(self) -> str:
        """Generate an empty report when no profiles are available."""
        lines = []
        lines.append("# Describe Profile Report\n")
        lines.append("*Descriptive statistics at pipeline checkpoints*\n")
        lines.append("---\n\n")
        lines.append("No describe profiles were captured during this pipeline execution.\n")
        lines.append("\nTo capture profiles, use the `@describeProfiler` decorator or `describe_profiler_context` context manager.\n")
        return "\n".join(lines)

    def _build_report_content(self, report_points: List[DescribeReportPoint]) -> str:
        """Build the complete markdown report content."""
        lines = []

        # Title and header
        lines.append("# Describe Profile Report\n")
        lines.append("*Descriptive statistics at pipeline checkpoints*\n")
        lines.append("---\n\n")

        # Overview section
        lines.append("## Overview\n")
        lines.append(f"- **Profiling Checkpoints:** {len(report_points)}")

        # Collect all unique columns
        all_columns = set()
        for point in report_points:
            all_columns.update(point.columns)
        lines.append(f"- **Columns Profiled:** {', '.join(sorted(all_columns))}")
        lines.append("\n")

        # Checkpoint index
        lines.append("## Checkpoint Index\n")
        lines.append("| Reference | Checkpoint | Function | Columns | Rows |")
        lines.append("|-----------|------------|----------|---------|------|")
        for point in report_points:
            lines.append(
                f"| [{point.reference_id}](#{point.reference_id.lower()}) | "
                f"{point.checkpoint_name} | "
                f"`{point.function_name}` | "
                f"{point.column_count} | "
                f"{point.row_count:,} |"
            )
        lines.append("\n")

        # Detail section for each checkpoint
        lines.append("## Profiling Checkpoints\n")
        for point in report_points:
            lines.append(f"### {point.reference_id}: {point.checkpoint_name} {{#{point.reference_id.lower()}}}\n")
            lines.append(f"**Function:** `{point.function_name}`  ")
            lines.append(f"**Dataset Size:** {point.row_count:,} rows × {point.column_count} columns\n")

            # Convert describe table to markdown
            if point.describe_table:
                lines.append(self._describe_table_to_markdown(point.describe_table, point.columns))

            lines.append("\n---\n")

        return "\n".join(lines)

    def _describe_table_to_markdown(self,
                                   describe_table: List[Dict[str, Any]],
                                   columns: List[str]) -> str:
        """Convert a describe table to markdown format."""
        lines = []

        # Build header
        header = "| Statistic | " + " | ".join(columns) + " |"
        separator = "|-----------|" + "|".join(["---------:" for _ in columns]) + "|"

        lines.append(header)
        lines.append(separator)

        # Build rows
        for row in describe_table:
            summary_stat = row.get('summary', '')
            values = []
            for col in columns:
                value = row.get(col, '')
                # Format numbers nicely
                # Try to convert to float first to handle numpy types and strings
                try:
                    if value is None or value == '' or value == 'None':
                        values.append(str(value))
                    elif summary_stat in ['count']:
                        # Count should be integer
                        values.append(f"{int(float(value)):,}")
                    else:
                        # All other numeric stats: format to 3 decimal places
                        float_val = float(value)
                        values.append(f"{float_val:.3f}")
                except (ValueError, TypeError):
                    # Not a number, use as-is
                    values.append(str(value))

            row_str = f"| **{summary_stat}** | " + " | ".join(values) + " |"
            lines.append(row_str)

        return "\n".join(lines) + "\n"
