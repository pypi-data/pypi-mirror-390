"""
Statistical Report Generator

Generates markdown reports from statistical profiles with:
- ASCII histograms
- Distribution visualizations
- Correlation matrices
- Data quality summaries
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .statistical_profiler import FeatureStats, StatisticalProfile

logger = logging.getLogger(__name__)


class StatisticalReportGenerator:
    """Generate markdown reports from statistical profiles."""

    def generate_report(
        self,
        profile: StatisticalProfile,
        output_path: str
    ) -> str:
        """
        Generate a statistical profile report.

        Args:
            profile: StatisticalProfile to document
            output_path: Path to write the report

        Returns:
            Path to generated report
        """
        logger.info(f"Generating statistical report: {profile.checkpoint_name}")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = self._generate_content(profile)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Statistical report generated: {output_file}")
        return str(output_file)

    def _generate_content(self, profile: StatisticalProfile) -> str:
        """Generate the full report content."""
        sections = []

        # Header
        sections.append(self._generate_header(profile))

        # Numeric Features
        if profile.numeric_features:
            sections.append(self._generate_numeric_section(profile.numeric_features, profile.row_count))

        # Categorical Features
        if profile.categorical_features:
            sections.append(self._generate_categorical_section(profile.categorical_features))

        # Missing Value Summary
        sections.append(self._generate_missing_summary(
            profile.numeric_features + profile.categorical_features
        ))

        # Outlier Summary
        if profile.numeric_features:
            sections.append(self._generate_outlier_summary(profile.numeric_features))

        # Correlation Matrix
        if profile.correlation_matrix:
            sections.append(self._generate_correlation_section(profile.correlation_matrix))

        # Data Quality Score
        sections.append(self._generate_quality_section(profile))

        # Footer
        sections.append(self._generate_footer(profile))

        return '\n\n'.join(sections)

    def _generate_header(self, profile: StatisticalProfile) -> str:
        """Generate report header."""
        timestamp = datetime.fromtimestamp(profile.timestamp).strftime('%Y-%m-%d %H:%M:%S')

        return f"""# Statistical Profile: {profile.checkpoint_name}

**Checkpoint**: "{profile.checkpoint_name}"
**Timestamp**: {timestamp}
**Dataset**: {profile.function_name}
**Rows**: {profile.row_count:,}
**Columns Profiled**: {profile.column_count}

---"""

    def _generate_numeric_section(
        self,
        features: List[FeatureStats],
        row_count: int
    ) -> str:
        """Generate numeric features section."""
        lines = ["## Numeric Features Profile\n"]

        for feature in features:
            lines.append(self._format_numeric_feature(feature, row_count))
            lines.append("\n---\n")

        return '\n'.join(lines)

    def _format_numeric_feature(self, feature: FeatureStats, row_count: int) -> str:
        """Format a single numeric feature."""
        lines = [f"### {feature.feature_name}\n", "```"]

        # Descriptive Statistics
        lines.append("Descriptive Statistics:")
        lines.append(f"  count: {feature.count:,}")
        if feature.mean is not None:
            lines.append(f"  mean: {feature.mean:.2f}")
        if feature.std is not None:
            lines.append(f"  std: {feature.std:.2f}")
        if feature.min_val is not None:
            lines.append(f"  min: {feature.min_val}")
        if feature.percentile_25 is not None:
            lines.append(f"  25%: {feature.percentile_25:.2f}")
        if feature.percentile_50 is not None:
            lines.append(f"  50%: {feature.percentile_50:.2f}")
        if feature.percentile_75 is not None:
            lines.append(f"  75%: {feature.percentile_75:.2f}")
        if feature.max_val is not None:
            lines.append(f"  max: {feature.max_val}")

        # Distribution
        if feature.distribution:
            lines.append("")
            lines.append("Distribution:")
            lines.append(f"  Skewness: {feature.distribution.skewness:.2f}")
            lines.append(f"  Kurtosis: {feature.distribution.kurtosis:.2f}")
            lines.append(f"  Shape: {feature.distribution.shape_description}")

        # Missing Values
        if feature.missing:
            lines.append("")
            lines.append("Missing Values:")
            lines.append(f"  count: {feature.missing.null_count:,}")
            lines.append(f"  percentage: {feature.missing.null_percentage:.2f}%")
            if feature.missing.zero_count is not None:
                lines.append(f"  Zero count: {feature.missing.zero_count:,} ({feature.missing.zero_percentage:.1f}%)")
            lines.append(f"  Interpretation: {feature.missing.interpretation}")

        # Outliers
        if feature.outliers:
            lines.append("")
            lines.append("Outliers (IQR method):")
            lines.append(f"  Lower bound: {feature.outliers.lower_bound:.2f}")
            lines.append(f"  Upper bound: {feature.outliers.upper_bound:.2f}")
            if feature.outliers.lower_count > 0:
                lines.append(f"  Outliers below: {feature.outliers.lower_count} ({feature.outliers.lower_percentage:.2f}%)")
            if feature.outliers.upper_count > 0:
                lines.append(f"  Outliers above: {feature.outliers.upper_count} ({feature.outliers.upper_percentage:.2f}%)")
            if feature.outliers.lower_count == 0 and feature.outliers.upper_count == 0:
                lines.append("  No outliers detected")

        # Unique values
        if feature.unique_count is not None:
            lines.append("")
            lines.append(f"Unique Values: {feature.unique_count:,} ({feature.unique_percentage:.1f}%)")

        # Histogram
        if feature.histogram_bins and feature.histogram_counts:
            lines.append("")
            lines.append("Histogram:")
            lines.append(self._generate_ascii_histogram(
                feature.histogram_bins,
                feature.histogram_counts,
                row_count
            ))

        lines.append("```")
        return '\n'.join(lines)

    def _generate_ascii_histogram(
        self,
        bins: List[tuple],
        counts: List[int],
        total_count: int,
        max_width: int = 40
    ) -> str:
        """Generate ASCII histogram."""
        if not bins or not counts:
            return "  No histogram data available"

        lines = []
        max_count = max(counts) if counts else 1

        for i, (bin_range, count) in enumerate(zip(bins, counts)):
            bin_start, bin_end = bin_range
            percentage = (count / total_count * 100) if total_count > 0 else 0

            # Create bar
            bar_width = int((count / max_count) * max_width) if max_count > 0 else 0
            bar = '█' * bar_width

            # Format bin label
            if i == 0:
                label = f"  [{bin_start:.1f}-{bin_end:.1f})"
            elif i == len(bins) - 1:
                label = f"  [{bin_start:.1f}+)"
            else:
                label = f"  [{bin_start:.1f}-{bin_end:.1f})"

            # Format line
            lines.append(f"{label:15} {bar} {count:,} ({percentage:.1f}%)")

        return '\n'.join(lines)

    def _generate_categorical_section(self, features: List[FeatureStats]) -> str:
        """Generate categorical features section."""
        lines = ["## Categorical Features Profile\n"]

        for feature in features:
            lines.append(self._format_categorical_feature(feature))
            lines.append("\n---\n")

        return '\n'.join(lines)

    def _format_categorical_feature(self, feature: FeatureStats) -> str:
        """Format a single categorical feature."""
        lines = [f"### {feature.feature_name}\n", "```"]

        # Value counts
        if feature.value_counts:
            lines.append("Value Counts:")
            for value, count in feature.value_counts.items():
                percentage = (count / feature.count * 100) if feature.count > 0 else 0
                lines.append(f"  {value}: {count:,} ({percentage:.1f}%)")

        # Basic stats
        lines.append("")
        lines.append(f"Unique Categories: {feature.unique_count}")

        if feature.missing:
            lines.append(f"Missing Values: {feature.missing.null_count:,} ({feature.missing.null_percentage:.2f}%)")

        if feature.mode is not None:
            mode_count = feature.value_counts.get(str(feature.mode), 0)
            mode_pct = (mode_count / feature.count * 100) if feature.count > 0 else 0
            lines.append(f"Mode: {feature.mode} ({mode_pct:.1f}%)")

        if feature.entropy is not None:
            lines.append(f"Entropy: {feature.entropy:.2f} (diversity measure)")

        # ASCII bar chart for value distribution
        if feature.value_counts:
            lines.append("")
            lines.append("Distribution:")
            lines.append(self._generate_categorical_bars(feature.value_counts, feature.count))

        lines.append("```")
        return '\n'.join(lines)

    def _generate_categorical_bars(
        self,
        value_counts: dict,
        total_count: int,
        max_width: int = 30
    ) -> str:
        """Generate ASCII bar chart for categorical values."""
        if not value_counts:
            return "  No data available"

        lines = []
        max_count = max(value_counts.values()) if value_counts else 1

        for value, count in value_counts.items():
            bar_width = int((count / max_count) * max_width) if max_count > 0 else 0
            bar = '█' * bar_width
            lines.append(f"  {str(value):15} {bar} {count:,}")

        return '\n'.join(lines)

    def _generate_missing_summary(self, features: List[FeatureStats]) -> str:
        """Generate missing value summary table."""
        lines = ["## Missing Value Summary\n"]

        # Create table
        lines.append("| Feature | Count | Percentage | Notes |")
        lines.append("|---------|-------|------------|-------|")

        features_with_missing = [f for f in features if f.missing and f.missing.null_count > 0]

        if not features_with_missing:
            lines.append("| All features | 0 | 0% | Complete data |")
        else:
            for feature in features_with_missing:
                lines.append(
                    f"| {feature.feature_name} | {feature.missing.null_count:,} | "
                    f"{feature.missing.null_percentage:.2f}% | {feature.missing.interpretation} |"
                )

        # Calculate total
        total_cells = sum(f.count + (f.missing.null_count if f.missing else 0) for f in features)
        total_missing = sum(f.missing.null_count if f.missing else 0 for f in features)
        total_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0

        lines.append("")
        lines.append(f"**Total Missing Values**: {total_missing:,} ({total_pct:.2f}% of all feature values)")

        return '\n'.join(lines)

    def _generate_outlier_summary(self, features: List[FeatureStats]) -> str:
        """Generate outlier summary table."""
        lines = ["## Outlier Summary\n"]

        # Create table
        lines.append("| Feature | Outlier Count | Percentage | Action |")
        lines.append("|---------|--------------|------------|--------|")

        features_with_outliers = []
        for feature in features:
            if feature.outliers:
                total_outliers = feature.outliers.lower_count + feature.outliers.upper_count
                if total_outliers > 0:
                    features_with_outliers.append((feature, total_outliers))

        if not features_with_outliers:
            lines.append("| All features | 0 | 0% | No outliers detected |")
        else:
            for feature, total_outliers in features_with_outliers:
                total_pct = feature.outliers.lower_percentage + feature.outliers.upper_percentage
                action = "Review" if total_pct > 5 else "Keep"
                lines.append(
                    f"| {feature.feature_name} | {total_outliers:,} | "
                    f"{total_pct:.2f}% | {action} |"
                )

        return '\n'.join(lines)

    def _generate_correlation_section(self, corr_matrix) -> str:
        """Generate correlation matrix section."""
        lines = ["## Feature Correlations\n"]

        # Show correlation matrix (formatted)
        lines.append("### Correlation Matrix\n")
        lines.append("```")

        # Format the correlation matrix nicely
        features = corr_matrix.features
        header = "                    " + "  ".join(f"{f[:8]:>8}" for f in features)
        lines.append(header)

        for i, feat1 in enumerate(features):
            row_values = []
            for j, feat2 in enumerate(features):
                corr_val = corr_matrix.matrix.loc[feat1, feat2]
                if not pd.isna(corr_val):
                    row_values.append(f"{corr_val:>8.2f}")
                else:
                    row_values.append(f"{'N/A':>8}")

            row = f"{feat1[:20]:20}" + "  ".join(row_values)
            lines.append(row)

        lines.append("")
        lines.append("Legend:")
        lines.append("  Strong correlation: |r| > 0.7")
        lines.append("  Moderate correlation: 0.4 < |r| < 0.7")
        lines.append("  Weak correlation: 0.2 < |r| < 0.4")
        lines.append("```")

        # Strong correlations
        if corr_matrix.strong_correlations:
            lines.append("\n### Key Insights\n")
            lines.append("**Strong Correlations**:")
            for i, (feat1, feat2, corr_val) in enumerate(corr_matrix.strong_correlations[:5], 1):
                sign = "positive" if corr_val > 0 else "negative"
                lines.append(f"  {i}. {feat1} <-> {feat2}: {corr_val:+.2f} ({sign})")

        # Multicollinearity warnings
        if corr_matrix.multicollinearity_warnings:
            lines.append("\n**[WARN] Multicollinearity Warnings**:")
            for warning in corr_matrix.multicollinearity_warnings:
                lines.append(f"  - {warning}")
            lines.append("\n**Recommendation**: Monitor VIF or consider dimensionality reduction")

        return '\n'.join(lines)

    def _generate_quality_section(self, profile: StatisticalProfile) -> str:
        """Generate data quality section."""
        lines = ["## Data Quality Score\n", "```"]

        # Calculate grade
        score = profile.data_quality_score
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        lines.append(f"Overall Data Quality: {score:.0f}/100 ({grade})")
        lines.append("")
        lines.append("Breakdown:")
        lines.append(f"  Completeness: {profile.overall_completeness:.1f}%")
        lines.append(f"  Data Quality Score: {score:.0f}/100")

        if profile.quality_issues:
            lines.append("")
            lines.append("Issues:")
            for issue in profile.quality_issues:
                lines.append(f"  [WARN] {issue}")
        else:
            lines.append("")
            lines.append("  [OK] No major data quality issues detected")

        lines.append("```")
        return '\n'.join(lines)

    def _generate_footer(self, profile: StatisticalProfile) -> str:
        """Generate report footer."""
        timestamp = datetime.fromtimestamp(profile.timestamp).strftime('%Y-%m-%d')
        return f"---\n\n*Checkpoint: \"{profile.checkpoint_name}\" | Generated by PySpark StoryDoc | {timestamp}*"


# Import pandas for correlation matrix formatting
import pandas as pd
