#!/usr/bin/env python3
"""
Distribution Visualization Module for PySpark StoryDoc.

This module provides high-quality distribution plotting capabilities using matplotlib and seaborn,
optimized for embedding in markdown reports and documentation.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

from ..analysis.distribution_analyzer import (
    DistributionAnalyzer,
    DistributionComparison,
    DistributionStats,
    OutlierMethod,
)

logger = logging.getLogger(__name__)

# Set matplotlib backend and style
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="husl")


@dataclass
class PlotConfig:
    """Configuration for distribution plots."""
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    font_size: int = 12
    title_size: int = 14
    bins: Union[int, str] = "auto"
    color_palette: str = "husl"
    save_format: str = "png"
    bbox_inches: str = "tight"
    transparent: bool = False


@dataclass
class PlotResult:
    """Result of a plot generation operation."""
    file_path: str
    variable_name: str
    plot_type: str
    statistics: Optional[DistributionStats] = None
    comparison: Optional[DistributionComparison] = None


class DistributionVisualizer:
    """
    High-quality distribution visualization using matplotlib and seaborn.

    This class generates publication-ready histograms and distribution plots
    that are optimized for embedding in markdown reports.
    """

    def __init__(self,
                 output_directory: str = "distribution_plots",
                 config: Optional[PlotConfig] = None):
        """
        Initialize the distribution visualizer.

        Args:
            output_directory: Directory to save generated plots. Can be absolute or relative path.
                            If relative, it will be resolved relative to the current working directory.
                            For proper integration with markdown reports, use absolute paths or paths
                            relative to where your markdown file will be saved.
            config: Plot configuration settings
        """
        # Convert to Path and resolve to absolute path
        # This ensures consistent behavior regardless of where the code is executed
        self.output_directory = Path(output_directory).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"DistributionVisualizer initialized with output directory: {self.output_directory}")

        self.config = config or PlotConfig()
        self.analyzer = DistributionAnalyzer()

        # Configure matplotlib and seaborn
        plt.rcParams.update({
            'font.size': self.config.font_size,
            'axes.titlesize': self.config.title_size,
            'axes.labelsize': self.config.font_size,
            'xtick.labelsize': self.config.font_size - 1,
            'ytick.labelsize': self.config.font_size - 1,
            'legend.fontsize': self.config.font_size - 1,
            'figure.titlesize': self.config.title_size + 2
        })

    def create_distribution_plot(self,
                               df: DataFrame,
                               variable: str,
                               title: Optional[str] = None,
                               sample_size: Optional[int] = 10000,
                               include_outlier_removal: bool = True,
                               outlier_method: OutlierMethod = OutlierMethod.IQR,
                               filename_prefix: Optional[str] = None) -> List[PlotResult]:
        """
        Create comprehensive distribution plots for a variable.

        Args:
            df: Spark DataFrame containing the data
            variable: Name of the variable to plot
            title: Custom title for the plot
            sample_size: Sample size for plotting performance
            include_outlier_removal: Whether to create outlier-removed version
            outlier_method: Method for outlier removal
            filename_prefix: Prefix for output filenames

        Returns:
            List of PlotResult objects for generated plots
        """
        results = []

        # Generate base filename
        if filename_prefix:
            base_filename = f"{filename_prefix}_{variable}"
        else:
            base_filename = variable

        # Create raw distribution plot
        try:
            raw_stats = self.analyzer.analyze_distribution(
                df, variable, sample_size=sample_size, outlier_method=OutlierMethod.NONE
            )

            raw_plot = self._create_single_distribution_plot(
                df, variable, raw_stats,
                title=title or f"{variable.title()} Distribution (Raw)",
                filename=f"{base_filename}_raw",
                outlier_method=OutlierMethod.NONE,
                sample_size=sample_size
            )
            results.append(raw_plot)

        except Exception as e:
            logger.error(f"Failed to create raw distribution plot for {variable}: {e}")

        # Create outlier-removed distribution plot if requested
        if include_outlier_removal:
            try:
                clean_stats = self.analyzer.analyze_distribution(
                    df, variable, sample_size=sample_size, outlier_method=outlier_method
                )

                clean_plot = self._create_single_distribution_plot(
                    df, variable, clean_stats,
                    title=title or f"{variable.title()} Distribution (Outliers Removed - {outlier_method.value.upper()})",
                    filename=f"{base_filename}_{outlier_method.value}",
                    outlier_method=outlier_method,
                    sample_size=sample_size
                )
                results.append(clean_plot)

            except Exception as e:
                logger.error(f"Failed to create clean distribution plot for {variable}: {e}")

        return results

    def create_comparison_plot(self,
                             before_df: DataFrame,
                             after_df: DataFrame,
                             variable: str,
                             operation_name: str = "Operation",
                             sample_size: Optional[int] = 10000,
                             outlier_method: OutlierMethod = OutlierMethod.IQR,
                             filename_prefix: Optional[str] = None) -> PlotResult:
        """
        Create before/after comparison plot for a variable.

        Args:
            before_df: DataFrame before the operation
            after_df: DataFrame after the operation
            variable: Variable to compare
            operation_name: Name of the operation for labeling
            sample_size: Sample size for plotting
            outlier_method: Method for outlier removal
            filename_prefix: Prefix for output filename

        Returns:
            PlotResult object for the generated comparison plot
        """
        # Analyze both distributions
        before_stats = self.analyzer.analyze_distribution(
            before_df, variable, sample_size=sample_size, outlier_method=outlier_method
        )
        after_stats = self.analyzer.analyze_distribution(
            after_df, variable, sample_size=sample_size, outlier_method=outlier_method
        )

        # Compare distributions
        comparison = self.analyzer.compare_distributions(before_stats, after_stats)

        # Generate filename
        if filename_prefix:
            filename = f"{filename_prefix}_{variable}_comparison"
        else:
            filename = f"{variable}_comparison"

        # Create the comparison plot
        return self._create_comparison_plot_impl(
            before_df, after_df, variable, comparison, operation_name,
            filename, sample_size, outlier_method
        )

    def create_multiple_variable_plots(self,
                                     df: DataFrame,
                                     variables: List[str],
                                     title_prefix: str = "",
                                     sample_size: Optional[int] = 10000,
                                     include_outlier_removal: bool = True,
                                     outlier_method: OutlierMethod = OutlierMethod.IQR,
                                     filename_prefix: Optional[str] = None) -> Dict[str, List[PlotResult]]:
        """
        Create distribution plots for multiple variables.

        Args:
            df: Spark DataFrame containing the data
            variables: List of variables to plot
            title_prefix: Prefix for plot titles
            sample_size: Sample size for plotting
            include_outlier_removal: Whether to include outlier-removed versions
            outlier_method: Method for outlier removal
            filename_prefix: Prefix for output filenames

        Returns:
            Dictionary mapping variable names to their plot results
        """
        results = {}

        for variable in variables:
            try:
                var_title = f"{title_prefix} {variable.title()}" if title_prefix else None
                var_filename = f"{filename_prefix}_{variable}" if filename_prefix else variable

                plots = self.create_distribution_plot(
                    df, variable,
                    title=var_title,
                    sample_size=sample_size,
                    include_outlier_removal=include_outlier_removal,
                    outlier_method=outlier_method,
                    filename_prefix=var_filename
                )
                results[variable] = plots

            except Exception as e:
                logger.error(f"Failed to create plots for variable {variable}: {e}")
                results[variable] = []

        return results

    def _create_single_distribution_plot(self,
                                       df: DataFrame,
                                       variable: str,
                                       stats: DistributionStats,
                                       title: str,
                                       filename: str,
                                       outlier_method: OutlierMethod,
                                       sample_size: Optional[int]) -> PlotResult:
        """Create a single distribution plot."""
        # Collect sample data for plotting
        sample_df = self.analyzer._apply_sampling(df, sample_size)

        if outlier_method != OutlierMethod.NONE:
            sample_df, _ = self.analyzer._remove_outliers(sample_df, variable, outlier_method)

        # Convert to pandas for plotting
        pandas_df = sample_df.select(variable).toPandas()
        data = pandas_df[variable].dropna()

        # Create the plot
        fig, ax = plt.subplots(figsize=self.config.figure_size)

        # Create histogram with density curve
        sns.histplot(data, bins=self.config.bins, kde=True, stat="density", ax=ax)

        # Add vertical lines for key statistics
        ax.axvline(stats.mean, color='red', linestyle='--', alpha=0.7, label=f'Mean: {stats.mean:.2f}')
        ax.axvline(stats.median, color='green', linestyle='--', alpha=0.7, label=f'Median: {stats.median:.2f}')

        # Set title and labels
        ax.set_title(title, fontsize=self.config.title_size, fontweight='bold')
        ax.set_xlabel(variable.replace('_', ' ').title(), fontsize=self.config.font_size)
        ax.set_ylabel('Density', fontsize=self.config.font_size)

        # Add statistics text box
        stats_text = (
            f"Count: {stats.non_null_count:,}\n"
            f"Mean: {stats.mean:.2f}\n"
            f"Std: {stats.std_dev:.2f}\n"
            f"Min: {stats.min_value:.2f}\n"
            f"Max: {stats.max_value:.2f}"
        )

        if stats.outlier_count and stats.outlier_count > 0:
            stats_text += f"\nOutliers removed: {stats.outlier_count:,}"

        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=self.config.font_size-1,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Add legend
        ax.legend()

        # Save the plot
        output_path = self.output_directory / f"{filename}.{self.config.save_format}"
        plt.tight_layout()
        plt.savefig(
            output_path,
            dpi=self.config.dpi,
            bbox_inches=self.config.bbox_inches,
            transparent=self.config.transparent
        )
        plt.close()

        logger.info(f"Distribution plot saved: {output_path}")

        return PlotResult(
            file_path=str(output_path),
            variable_name=variable,
            plot_type="distribution",
            statistics=stats
        )

    def _create_comparison_plot_impl(self,
                                   before_df: DataFrame,
                                   after_df: DataFrame,
                                   variable: str,
                                   comparison: DistributionComparison,
                                   operation_name: str,
                                   filename: str,
                                   sample_size: Optional[int],
                                   outlier_method: OutlierMethod) -> PlotResult:
        """Create a before/after comparison plot."""
        # Sample and clean data
        before_sample = self.analyzer._apply_sampling(before_df, sample_size)
        after_sample = self.analyzer._apply_sampling(after_df, sample_size)

        if outlier_method != OutlierMethod.NONE:
            before_sample, _ = self.analyzer._remove_outliers(before_sample, variable, outlier_method)
            after_sample, _ = self.analyzer._remove_outliers(after_sample, variable, outlier_method)

        # Convert to pandas
        before_data = before_sample.select(variable).toPandas()[variable].dropna()
        after_data = after_sample.select(variable).toPandas()[variable].dropna()

        # Create comparison plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(self.config.figure_size[0], self.config.figure_size[1]//1.5))

        # Before plot
        sns.histplot(before_data, bins=self.config.bins, kde=True, stat="density", ax=ax1, color='blue', alpha=0.7)
        ax1.axvline(comparison.before_stats.mean, color='red', linestyle='--', alpha=0.7,
                   label=f'Mean: {comparison.before_stats.mean:.2f}')
        ax1.set_title(f'Before {operation_name}', fontweight='bold')
        ax1.set_xlabel(variable.replace('_', ' ').title())
        ax1.set_ylabel('Density')
        ax1.legend()

        # After plot
        sns.histplot(after_data, bins=self.config.bins, kde=True, stat="density", ax=ax2, color='green', alpha=0.7)
        ax2.axvline(comparison.after_stats.mean, color='red', linestyle='--', alpha=0.7,
                   label=f'Mean: {comparison.after_stats.mean:.2f}')
        ax2.set_title(f'After {operation_name}', fontweight='bold')
        ax2.set_xlabel(variable.replace('_', ' ').title())
        ax2.set_ylabel('Density')
        ax2.legend()

        # Add overall title with change summary
        fig.suptitle(
            f'{variable.title()} Distribution Comparison\n'
            f'Count: {comparison.before_stats.non_null_count:,} -> {comparison.after_stats.non_null_count:,} '
            f'({comparison.count_change_pct:+.1f}%)',
            fontsize=self.config.title_size, fontweight='bold'
        )

        # Save the plot
        output_path = self.output_directory / f"{filename}.{self.config.save_format}"
        plt.tight_layout()
        plt.savefig(
            output_path,
            dpi=self.config.dpi,
            bbox_inches=self.config.bbox_inches,
            transparent=self.config.transparent
        )
        plt.close()

        logger.info(f"Comparison plot saved: {output_path}")

        return PlotResult(
            file_path=str(output_path),
            variable_name=variable,
            plot_type="comparison",
            comparison=comparison
        )

    def generate_summary_statistics_table(self,
                                         stats_dict: Dict[str, DistributionStats],
                                         filename: str = "distribution_summary") -> str:
        """
        Generate a summary table of distribution statistics.

        Args:
            stats_dict: Dictionary of variable names to their statistics
            filename: Output filename (without extension)

        Returns:
            Path to the generated CSV file
        """
        # Convert to pandas DataFrame
        summary_data = []
        for var_name, stats in stats_dict.items():
            summary_data.append({
                'Variable': var_name,
                'Count': stats.non_null_count,
                'Mean': round(stats.mean, 3),
                'Median': round(stats.median, 3),
                'Std Dev': round(stats.std_dev, 3),
                'Min': round(stats.min_value, 3),
                'Max': round(stats.max_value, 3),
                'Q25': round(stats.q25, 3),
                'Q75': round(stats.q75, 3),
                'Null Count': stats.null_count,
                'Outliers Removed': stats.outlier_count or 0
            })

        summary_df = pd.DataFrame(summary_data)

        # Save as CSV
        output_path = self.output_directory / f"{filename}.csv"
        summary_df.to_csv(output_path, index=False)

        logger.info(f"Summary statistics saved: {output_path}")
        return str(output_path)