"""
ASCII chart visualization for trend analysis reports.

This module provides utilities for generating ASCII-based visualizations
suitable for markdown reports, including line charts, bar charts, and sparklines.

Example:
    >>> from pyspark_storydoc.history.trend_visualizer import TrendVisualizer
    >>>
    >>> visualizer = TrendVisualizer()
    >>> data_points = [10, 15, 13, 18, 22, 25, 23]
    >>> chart = visualizer.generate_ascii_chart(data_points, width=60, height=15)
    >>> print(chart)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .models import TrendAnalysis, MetricPoint

logger = logging.getLogger(__name__)


class TrendVisualizer:
    """
    Generate ASCII-based visualizations for trend analysis.

    This class provides methods to create text-based charts and graphs
    that can be embedded in markdown reports.
    """

    def __init__(self):
        """Initialize trend visualizer."""
        pass

    def generate_ascii_chart(
        self,
        data_points: List[float],
        width: int = 80,
        height: int = 20,
        title: Optional[str] = None,
        y_label: Optional[str] = None,
        show_values: bool = False,
    ) -> str:
        """
        Generate ASCII line chart from data points.

        Args:
            data_points: List of numeric values to plot
            width: Chart width in characters (default: 80)
            height: Chart height in characters (default: 20)
            title: Optional chart title
            y_label: Optional Y-axis label
            show_values: Show min/max values on Y-axis (default: False)

        Returns:
            ASCII art line chart as string

        Example:
            >>> values = [10, 12, 15, 13, 18, 22, 20]
            >>> chart = visualizer.generate_ascii_chart(values, width=60, height=10)
            >>> print(chart)
        """
        try:
            if not data_points:
                return "No data to visualize"

            if len(data_points) == 1:
                return f"Single data point: {data_points[0]:.2f}"

            # Normalize data to fit in height
            values = np.array(data_points)
            min_val = np.min(values)
            max_val = np.max(values)

            if min_val == max_val:
                # All values are the same
                mid_line = height // 2
                lines = []

                if title:
                    lines.append(title)
                    lines.append("")

                for i in range(height):
                    if i == mid_line:
                        line = "+" + "-" * width
                    else:
                        line = "|" + " " * width
                    lines.append(line)

                lines.append("+" + "-" * width)
                if show_values:
                    lines.append(f"Value: {min_val:.2f}")

                return "\n".join(lines)

            # Scale values to chart height
            scaled = ((values - min_val) / (max_val - min_val) * (height - 1)).astype(int)
            scaled = height - 1 - scaled  # Flip for top-to-bottom

            # Create chart grid
            grid = [[' ' for _ in range(width)] for _ in range(height)]

            # Plot points
            points_per_column = len(data_points) / width
            for col in range(width):
                # Get data point index for this column
                idx = int(col * points_per_column)
                if idx >= len(scaled):
                    idx = len(scaled) - 1

                row = scaled[idx]
                grid[row][col] = '*'

                # Connect with previous point (simple line drawing)
                if col > 0:
                    prev_idx = int((col - 1) * points_per_column)
                    if prev_idx >= len(scaled):
                        prev_idx = len(scaled) - 1
                    prev_row = scaled[prev_idx]

                    # Draw vertical line between points
                    start_row = min(row, prev_row)
                    end_row = max(row, prev_row)
                    for r in range(start_row, end_row + 1):
                        if grid[r][col] == ' ':
                            grid[r][col] = '|' if r != row else '*'

            # Build output
            lines = []

            if title:
                lines.append(title)
                lines.append("")

            # Y-axis labels
            if show_values and y_label:
                label_space = len(f"{max_val:.2f}") + 2
            elif show_values:
                label_space = len(f"{max_val:.2f}") + 1
            else:
                label_space = 1

            # Add chart rows
            for i, row in enumerate(grid):
                if show_values:
                    # Calculate Y value for this row
                    y_val = max_val - (i / (height - 1)) * (max_val - min_val)
                    if i == 0:
                        label = f"{y_val:.2f}".rjust(label_space - 1)
                    elif i == height - 1:
                        label = f"{y_val:.2f}".rjust(label_space - 1)
                    elif i == height // 2:
                        label = f"{y_val:.2f}".rjust(label_space - 1)
                    else:
                        label = " " * (label_space - 1)
                else:
                    label = ""

                lines.append(label + "|" + "".join(row))

            # X-axis
            lines.append(" " * label_space + "+" + "-" * width)

            # Summary statistics
            if show_values:
                lines.append("")
                lines.append(f"Min: {min_val:.2f}  Max: {max_val:.2f}  Mean: {np.mean(values):.2f}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to generate ASCII chart: {str(e)}", exc_info=True)
            return f"Error generating chart: {str(e)}"

    def generate_sparkline(
        self,
        data_points: List[float],
        width: int = 40,
    ) -> str:
        """
        Generate compact sparkline visualization.

        Args:
            data_points: List of numeric values
            width: Width in characters (default: 40)

        Returns:
            Sparkline string using block characters

        Example:
            >>> values = [1, 2, 3, 2, 4, 3, 5]
            >>> sparkline = visualizer.generate_sparkline(values)
            >>> print(f"Trend: {sparkline}")
        """
        try:
            if not data_points:
                return ""

            # Unicode block characters for sparklines
            blocks = " ▁▂▃▄▅▆▇█"

            values = np.array(data_points)
            min_val = np.min(values)
            max_val = np.max(values)

            if min_val == max_val:
                return blocks[4] * min(width, len(data_points))

            # Normalize to 0-8 range
            scaled = ((values - min_val) / (max_val - min_val) * 8).astype(int)
            scaled = np.clip(scaled, 0, 8)

            # Sample if too many points
            if len(scaled) > width:
                indices = np.linspace(0, len(scaled) - 1, width, dtype=int)
                scaled = scaled[indices]

            # Build sparkline
            sparkline = "".join([blocks[val] for val in scaled])

            return sparkline

        except Exception as e:
            logger.error(f"Failed to generate sparkline: {str(e)}", exc_info=True)
            return ""

    def generate_trend_table(
        self,
        trend_data: List[Tuple[str, TrendAnalysis]],
    ) -> str:
        """
        Generate markdown table with trend statistics.

        Args:
            trend_data: List of (metric_name, TrendAnalysis) tuples

        Returns:
            Markdown formatted table

        Example:
            >>> table = visualizer.generate_trend_table([(
            ...     "complexity_score",
            ...     trend_analysis
            ... )])
            >>> print(table)
        """
        try:
            if not trend_data:
                return "No trend data available"

            # Build table header
            lines = [
                "| Metric | Trend | Growth | Mean | StdDev | Anomalies |",
                "|--------|-------|--------|------|--------|-----------|",
            ]

            # Add rows
            for metric_name, trend in trend_data:
                # Trend direction indicator
                if trend.trend_direction == "increasing":
                    trend_icon = "↗ Increasing"
                elif trend.trend_direction == "decreasing":
                    trend_icon = "↘ Decreasing"
                else:
                    trend_icon = "→ Stable"

                # Growth rate with sign
                growth = trend.growth_rate_percent
                if growth > 0:
                    growth_str = f"+{growth:.1f}%"
                else:
                    growth_str = f"{growth:.1f}%"

                # Anomaly count
                anomaly_count = len(trend.anomalies)
                if anomaly_count > 0:
                    anomaly_str = f"⚠ {anomaly_count}"
                else:
                    anomaly_str = "✓ 0"

                row = (
                    f"| {metric_name} "
                    f"| {trend_icon} "
                    f"| {growth_str} "
                    f"| {trend.mean:.2f} "
                    f"| {trend.std_dev:.2f} "
                    f"| {anomaly_str} |"
                )
                lines.append(row)

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to generate trend table: {str(e)}", exc_info=True)
            return f"Error generating table: {str(e)}"

    def generate_summary_stats(
        self,
        trend_data: TrendAnalysis,
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for trend data.

        Args:
            trend_data: TrendAnalysis object

        Returns:
            Dictionary with summary statistics

        Example:
            >>> stats = visualizer.generate_summary_stats(trend_analysis)
            >>> print(f"Mean: {stats['mean']:.2f}")
            >>> print(f"Median: {stats['median']:.2f}")
        """
        try:
            values = np.array([dp.value for dp in trend_data.data_points])

            return {
                "count": len(values),
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std_dev": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "q25": float(np.percentile(values, 25)),
                "q75": float(np.percentile(values, 75)),
                "range": float(np.max(values) - np.min(values)),
            }

        except Exception as e:
            logger.error(f"Failed to generate summary stats: {str(e)}", exc_info=True)
            return {}

    def format_trend_report(
        self,
        trend_analysis: TrendAnalysis,
        include_chart: bool = True,
        include_anomalies: bool = True,
    ) -> str:
        """
        Format complete trend report as markdown.

        Args:
            trend_analysis: TrendAnalysis object
            include_chart: Include ASCII chart (default: True)
            include_anomalies: Include anomaly details (default: True)

        Returns:
            Markdown formatted report

        Example:
            >>> report = visualizer.format_trend_report(trend_analysis)
            >>> with open("trend_report.md", "w") as f:
            ...     f.write(report)
        """
        try:
            lines = []

            # Header
            lines.append(f"## Trend Analysis: {trend_analysis.metric_name}")
            lines.append("")
            lines.append(f"**Pipeline:** {trend_analysis.pipeline_name}")
            lines.append(f"**Time Window:** {trend_analysis.time_window_days} days")
            lines.append(f"**Data Points:** {len(trend_analysis.data_points)}")
            lines.append("")

            # Summary statistics
            lines.append("### Summary Statistics")
            lines.append("")
            lines.append(f"- **Trend Direction:** {trend_analysis.trend_direction.title()}")

            growth = trend_analysis.growth_rate_percent
            if growth > 0:
                lines.append(f"- **Growth Rate:** +{growth:.1f}%")
            else:
                lines.append(f"- **Growth Rate:** {growth:.1f}%")

            lines.append(f"- **Mean:** {trend_analysis.mean:.2f}")
            lines.append(f"- **Std Dev:** {trend_analysis.std_dev:.2f}")
            lines.append(f"- **Min:** {trend_analysis.min_value:.2f}")
            lines.append(f"- **Max:** {trend_analysis.max_value:.2f}")
            lines.append(f"- **Confidence:** {trend_analysis.confidence:.1%}")
            lines.append(f"- **R²:** {trend_analysis.r_squared:.3f}")
            lines.append("")

            # ASCII chart
            if include_chart and len(trend_analysis.data_points) >= 2:
                lines.append("### Trend Visualization")
                lines.append("")
                lines.append("```")

                values = [dp.value for dp in trend_analysis.data_points]
                chart = self.generate_ascii_chart(
                    values,
                    width=70,
                    height=15,
                    title=f"{trend_analysis.metric_name} over time",
                    show_values=True,
                )
                lines.append(chart)
                lines.append("```")
                lines.append("")

            # Anomalies
            if include_anomalies and trend_analysis.anomalies:
                lines.append("### Anomalies Detected")
                lines.append("")
                lines.append(f"Found {len(trend_analysis.anomalies)} anomalies:")
                lines.append("")

                # Create anomaly table
                lines.append("| Timestamp | Value | Expected | Deviation | Severity |")
                lines.append("|-----------|-------|----------|-----------|----------|")

                for anomaly in trend_analysis.anomalies:
                    timestamp_str = anomaly.timestamp.strftime("%Y-%m-%d %H:%M")
                    severity_icon = {
                        "INFO": "ℹ️",
                        "WARNING": "⚠️",
                        "ERROR": "❌",
                        "CRITICAL": "🚨",
                    }.get(str(anomaly.severity), "")

                    row = (
                        f"| {timestamp_str} "
                        f"| {anomaly.value:.2f} "
                        f"| {anomaly.expected_value:.2f} "
                        f"| {anomaly.deviation_std_devs:.1f}σ "
                        f"| {severity_icon} {anomaly.severity} |"
                    )
                    lines.append(row)

                lines.append("")

            # Sparkline
            values = [dp.value for dp in trend_analysis.data_points]
            sparkline = self.generate_sparkline(values, width=50)
            if sparkline:
                lines.append("### Quick View")
                lines.append("")
                lines.append(f"```")
                lines.append(sparkline)
                lines.append("```")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to format trend report: {str(e)}", exc_info=True)
            return f"Error formatting report: {str(e)}"

    def generate_bar_chart(
        self,
        labels: List[str],
        values: List[float],
        width: int = 50,
        title: Optional[str] = None,
    ) -> str:
        """
        Generate ASCII horizontal bar chart.

        Args:
            labels: List of bar labels
            values: List of values for each bar
            width: Maximum bar width (default: 50)
            title: Optional chart title

        Returns:
            ASCII bar chart as string

        Example:
            >>> labels = ["Pipeline A", "Pipeline B", "Pipeline C"]
            >>> values = [45, 30, 60]
            >>> chart = visualizer.generate_bar_chart(labels, values)
            >>> print(chart)
        """
        try:
            if not labels or not values or len(labels) != len(values):
                return "Invalid data for bar chart"

            # Find max value for scaling
            max_value = max(values)
            if max_value == 0:
                max_value = 1

            # Find max label length for alignment
            max_label_len = max(len(label) for label in labels)

            lines = []

            if title:
                lines.append(title)
                lines.append("")

            # Generate bars
            for label, value in zip(labels, values):
                bar_length = int((value / max_value) * width)
                bar = "█" * bar_length
                padded_label = label.ljust(max_label_len)
                lines.append(f"{padded_label} | {bar} {value:.1f}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to generate bar chart: {str(e)}", exc_info=True)
            return f"Error generating bar chart: {str(e)}"

    def generate_comparison_chart(
        self,
        baseline_points: List[float],
        current_points: List[float],
        width: int = 80,
        height: int = 20,
    ) -> str:
        """
        Generate ASCII chart comparing two trend lines.

        Args:
            baseline_points: Baseline data points
            current_points: Current data points
            width: Chart width (default: 80)
            height: Chart height (default: 20)

        Returns:
            ASCII comparison chart

        Example:
            >>> baseline = [10, 12, 13, 15, 14]
            >>> current = [10, 13, 16, 18, 20]
            >>> chart = visualizer.generate_comparison_chart(baseline, current)
            >>> print(chart)
        """
        try:
            if not baseline_points or not current_points:
                return "Insufficient data for comparison"

            # Combine for scaling
            all_values = baseline_points + current_points
            min_val = min(all_values)
            max_val = max(all_values)

            if min_val == max_val:
                return "All values are identical"

            # Create grid
            grid = [[' ' for _ in range(width)] for _ in range(height)]

            # Plot baseline (using 'o')
            self._plot_line(grid, baseline_points, height, width, min_val, max_val, 'o')

            # Plot current (using '*')
            self._plot_line(grid, current_points, height, width, min_val, max_val, '*')

            # Build output
            lines = ["Comparison: Baseline (o) vs Current (*)"]
            lines.append("")

            for row in grid:
                lines.append("|" + "".join(row))

            lines.append("+" + "-" * width)
            lines.append("")
            lines.append("Legend: o = baseline, * = current")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to generate comparison chart: {str(e)}", exc_info=True)
            return f"Error generating comparison chart: {str(e)}"

    def _plot_line(
        self,
        grid: List[List[str]],
        data_points: List[float],
        height: int,
        width: int,
        min_val: float,
        max_val: float,
        marker: str,
    ):
        """Helper to plot a line on the grid."""
        values = np.array(data_points)
        scaled = ((values - min_val) / (max_val - min_val) * (height - 1)).astype(int)
        scaled = height - 1 - scaled

        points_per_column = len(data_points) / width
        for col in range(width):
            idx = int(col * points_per_column)
            if idx >= len(scaled):
                idx = len(scaled) - 1

            row = scaled[idx]
            if 0 <= row < height and 0 <= col < width:
                grid[row][col] = marker
