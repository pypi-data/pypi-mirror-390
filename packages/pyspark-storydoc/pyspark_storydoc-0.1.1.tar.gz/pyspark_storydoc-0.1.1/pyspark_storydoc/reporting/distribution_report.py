"""Distribution Report - Wrapper for existing distribution analysis system."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class DistributionReportConfig(ReportConfig):
    """Configuration for Distribution Report generation."""
    include_cross_analysis: bool = True
    table_layout: str = "per_variable"  # "per_variable" or "per_step"
    outlier_methods: List[str] = None

    def __post_init__(self):
        if self.outlier_methods is None:
            self.outlier_methods = ["none", "iqr"]


class DistributionReport(BaseReport):
    """
    Generates distribution analysis reports.

    This is a wrapper around the existing unified report generator's
    distribution analysis functionality, making it available as a
    standalone modular report.
    """

    def __init__(self, config: Optional[DistributionReportConfig] = None, **kwargs):
        """
        Initialize the Distribution Report generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = DistributionReportConfig(**kwargs)
        elif config is None:
            config = DistributionReportConfig()

        super().__init__(config)
        self.config: DistributionReportConfig = config

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the Distribution Analysis Report.

        Args:
            lineage_graph: EnhancedLineageGraph with distribution analysis data
            output_path: Path to write the markdown file

        Returns:
            Path to the generated report
        """
        logger.info("Generating Distribution Analysis Report")

        # Get distribution analyses from global tracker
        distribution_analyses = self._get_distribution_analyses()

        if not distribution_analyses:
            logger.warning("No distribution analyses found")
            content = self._generate_empty_report()
        else:
            content = self._generate_distribution_report(
                distribution_analyses,
                lineage_graph,
                output_path
            )

        # Write to file
        return self._write_report(content, output_path)

    def _get_distribution_analyses(self) -> List[Dict[str, Any]]:
        """Retrieve distribution analyses from global tracker."""
        try:
            from ..core.lineage_tracker import get_enhanced_tracker
            tracker = get_enhanced_tracker()

            if not hasattr(tracker, '_distribution_analyses'):
                return []

            return getattr(tracker, '_distribution_analyses', [])
        except Exception as e:
            logger.error(f"Failed to retrieve distribution analyses: {e}")
            return []

    def _generate_distribution_report(
        self,
        distribution_analyses: List[Dict[str, Any]],
        lineage_graph,
        output_path: str
    ) -> str:
        """Generate distribution analysis report using existing system."""
        try:
            # Import unified report generator
            from pathlib import Path

            from ..visualization.unified_report_generator import UnifiedReportGenerator

            # Create generator
            generator = UnifiedReportGenerator()

            # Set output path so relative path calculation works correctly
            generator._output_path = Path(output_path)

            # Process distribution analyses
            analysis_points = generator._process_distribution_analyses(
                distribution_analyses,
                lineage_graph
            )

            # Generate distribution analysis section
            content_lines = []

            # Title
            content_lines.append("# Distribution Analysis Report\n")
            content_lines.append("*Statistical analysis of variable distributions across the pipeline*\n")
            content_lines.append("---\n")

            # Overview
            content_lines.append("\n## Overview\n")
            content_lines.append(f"- **Analysis Points:** {len(analysis_points)}")

            # Get unique variables
            all_variables = set()
            for point in analysis_points:
                all_variables.update(point.variables)

            content_lines.append(f"- **Variables Monitored:** {', '.join(sorted(all_variables))}")
            content_lines.append("")

            # Generate distribution analysis by variable
            distribution_section = generator._generate_distribution_analysis_section(
                analysis_points
            )
            content_lines.append(distribution_section)

            # Cross-analysis if enabled
            if self.config.include_cross_analysis:
                cross_section = generator._generate_cross_analysis_section(analysis_points)
                content_lines.append(cross_section)

            return '\n'.join(content_lines)

        except Exception as e:
            logger.error(f"Failed to generate distribution report: {e}")
            return self._generate_error_report(str(e))

    def _generate_empty_report(self) -> str:
        """Generate report when no distribution analyses are available."""
        lines = []
        lines.append("# Distribution Analysis Report\n")
        lines.append("*Statistical analysis of variable distributions*\n")
        lines.append("---\n")
        lines.append("\n## No Distribution Analyses Found\n")
        lines.append("No distribution analyses were tracked during pipeline execution.\n")
        lines.append("To enable distribution analysis, use the `@distributionAnalysis` decorator:\n")
        lines.append("```python")
        lines.append("@distributionAnalysis(")
        lines.append("    variables=['column1', 'column2'],")
        lines.append("    outlier_methods=['none', 'iqr']")
        lines.append(")")
        lines.append("def transform_data(df):")
        lines.append("    return df.filter(...)")
        lines.append("```\n")
        return '\n'.join(lines)

    def _generate_error_report(self, error: str) -> str:
        """Generate error report."""
        lines = []
        lines.append("# Distribution Analysis Report\n")
        lines.append("---\n")
        lines.append("\n## Error Generating Report\n")
        lines.append(f"An error occurred while generating the distribution analysis report:\n")
        lines.append(f"```\n{error}\n```\n")
        return '\n'.join(lines)
