#!/usr/bin/env python3
"""
Distribution Analysis Engine for PySpark StoryDoc.

This module provides comprehensive distribution analysis capabilities including:
- Statistical analysis of variable distributions
- Outlier detection using multiple methods
- Distribution comparison and drift detection
- Integration with PySpark DataFrames
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count
from pyspark.sql.functions import max as spark_max
from pyspark.sql.functions import mean
from pyspark.sql.functions import min as spark_min
from pyspark.sql.functions import percentile_approx, stddev
from pyspark.sql.types import NumericType

from ..utils.dataframe_utils import safe_count, safe_distinct_count

logger = logging.getLogger(__name__)


class OutlierMethod(Enum):
    """Supported outlier detection methods."""
    NONE = "none"
    IQR = "iqr"
    Z_SCORE = "z_score"
    PERCENTILE = "percentile"


@dataclass
class DistributionStats:
    """Statistical summary of a variable distribution."""
    variable_name: str
    total_count: int
    non_null_count: int
    null_count: int
    mean: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    q25: float
    q75: float
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    outlier_count: Optional[int] = None
    outlier_method: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'variable_name': self.variable_name,
            'total_count': self.total_count,
            'non_null_count': self.non_null_count,
            'null_count': self.null_count,
            'mean': self.mean,
            'median': self.median,
            'std_dev': self.std_dev,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'q25': self.q25,
            'q75': self.q75,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'outlier_count': self.outlier_count,
            'outlier_method': self.outlier_method
        }


@dataclass
class DistributionComparison:
    """Comparison results between two distributions."""
    variable_name: str
    before_stats: DistributionStats
    after_stats: DistributionStats
    mean_change: float
    median_change: float
    std_change: float
    count_change: int
    count_change_pct: float
    distribution_shift_score: float
    is_significant_change: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'variable_name': self.variable_name,
            'before_stats': self.before_stats.to_dict(),
            'after_stats': self.after_stats.to_dict(),
            'mean_change': self.mean_change,
            'median_change': self.median_change,
            'std_change': self.std_change,
            'count_change': self.count_change,
            'count_change_pct': self.count_change_pct,
            'distribution_shift_score': self.distribution_shift_score,
            'is_significant_change': self.is_significant_change
        }


class DistributionAnalyzer:
    """
    Core engine for distribution analysis and comparison.

    This class provides methods to:
    - Analyze distributions of numeric variables in Spark DataFrames
    - Detect and remove outliers using various methods
    - Compare distributions before and after transformations
    - Generate statistical summaries and detect distribution drift
    """

    def __init__(self,
                 default_sample_size: Optional[int] = 10000,
                 outlier_z_threshold: float = 3.0,
                 outlier_percentile_threshold: Tuple[float, float] = (1.0, 99.0),
                 significance_threshold: float = 0.1):
        """
        Initialize the distribution analyzer.

        Args:
            default_sample_size: Default sample size for analysis (None = no sampling)
            outlier_z_threshold: Z-score threshold for outlier detection
            outlier_percentile_threshold: Percentile thresholds for outlier detection
            significance_threshold: Threshold for determining significant distribution changes
        """
        self.default_sample_size = default_sample_size
        self.outlier_z_threshold = outlier_z_threshold
        self.outlier_percentile_threshold = outlier_percentile_threshold
        self.significance_threshold = significance_threshold

    def analyze_distribution(self,
                           df: DataFrame,
                           variable: str,
                           sample_size: Optional[int] = None,
                           outlier_method: OutlierMethod = OutlierMethod.NONE) -> DistributionStats:
        """
        Analyze the distribution of a single variable.

        Args:
            df: Spark DataFrame to analyze
            variable: Name of the variable to analyze
            sample_size: Sample size for analysis (None uses default)
            outlier_method: Method for outlier detection

        Returns:
            DistributionStats object with comprehensive statistics

        Raises:
            ValueError: If variable doesn't exist or isn't numeric
        """
        # CRITICAL FIX: Extract raw DataFrame early to prevent lineage pollution
        raw_df = self._extract_raw_dataframe(df)

        # Validate inputs
        if variable not in raw_df.columns:
            raise ValueError(f"Variable '{variable}' not found in DataFrame columns: {raw_df.columns}")

        # Check if variable is numeric
        var_type = dict(raw_df.dtypes)[variable]
        if not self._is_numeric_type(var_type):
            raise ValueError(f"Variable '{variable}' is not numeric (type: {var_type})")

        # Apply sampling if specified (now uses raw_df internally)
        sample_df = self._apply_sampling(raw_df, sample_size or self.default_sample_size)

        # Remove outliers if specified
        if outlier_method != OutlierMethod.NONE:
            clean_df, outlier_count = self._remove_outliers(sample_df, variable, outlier_method)
        else:
            clean_df = sample_df
            outlier_count = 0

        # Calculate comprehensive statistics
        stats = self._calculate_statistics(clean_df, variable)

        # Add outlier information
        stats.outlier_count = outlier_count
        stats.outlier_method = outlier_method.value

        return stats

    def compare_distributions(self,
                            before_stats: DistributionStats,
                            after_stats: DistributionStats) -> DistributionComparison:
        """
        Compare two distribution statistics to detect changes.

        Args:
            before_stats: Statistics from the original distribution
            after_stats: Statistics from the transformed distribution

        Returns:
            DistributionComparison object with change metrics
        """
        if before_stats.variable_name != after_stats.variable_name:
            raise ValueError("Cannot compare distributions of different variables")

        # Calculate changes
        mean_change = ((after_stats.mean - before_stats.mean) / before_stats.mean * 100
                      if before_stats.mean != 0 else 0)
        median_change = ((after_stats.median - before_stats.median) / before_stats.median * 100
                        if before_stats.median != 0 else 0)
        std_change = ((after_stats.std_dev - before_stats.std_dev) / before_stats.std_dev * 100
                     if before_stats.std_dev != 0 else 0)

        count_change = after_stats.non_null_count - before_stats.non_null_count
        count_change_pct = (count_change / before_stats.non_null_count * 100
                           if before_stats.non_null_count != 0 else 0)

        # Calculate distribution shift score (simplified metric)
        distribution_shift_score = abs(mean_change) + abs(median_change) + abs(std_change) / 2

        # Determine if change is significant
        is_significant = (abs(mean_change) > self.significance_threshold * 100 or
                         abs(median_change) > self.significance_threshold * 100 or
                         abs(count_change_pct) > self.significance_threshold * 100)

        return DistributionComparison(
            variable_name=before_stats.variable_name,
            before_stats=before_stats,
            after_stats=after_stats,
            mean_change=mean_change,
            median_change=median_change,
            std_change=std_change,
            count_change=count_change,
            count_change_pct=count_change_pct,
            distribution_shift_score=distribution_shift_score,
            is_significant_change=is_significant
        )

    def analyze_multiple_variables(self,
                                 df: DataFrame,
                                 variables: List[str],
                                 sample_size: Optional[int] = None,
                                 outlier_method: OutlierMethod = OutlierMethod.NONE) -> Dict[str, DistributionStats]:
        """
        Analyze distributions of multiple variables efficiently.

        Args:
            df: Spark DataFrame to analyze
            variables: List of variable names to analyze
            sample_size: Sample size for analysis
            outlier_method: Method for outlier detection

        Returns:
            Dictionary mapping variable names to their DistributionStats
        """
        results = {}

        # CRITICAL FIX: Extract raw DataFrame early to prevent lineage pollution
        raw_df = self._extract_raw_dataframe(df)

        # Validate all variables first
        for var in variables:
            if var not in raw_df.columns:
                raise ValueError(f"Variable '{var}' not found in DataFrame")

            var_type = dict(raw_df.dtypes)[var]
            if not self._is_numeric_type(var_type):
                logger.warning(f"Skipping non-numeric variable '{var}' (type: {var_type})")
                continue

        # Filter to numeric variables only
        numeric_variables = [var for var in variables
                           if self._is_numeric_type(dict(raw_df.dtypes)[var])]

        if not numeric_variables:
            logger.warning("No numeric variables found for analysis")
            return results

        # Apply sampling once for all variables (now uses raw_df internally)
        sample_df = self._apply_sampling(raw_df, sample_size or self.default_sample_size)

        # Analyze each variable
        for var in numeric_variables:
            try:
                results[var] = self.analyze_distribution(
                    sample_df, var, sample_size=None, outlier_method=outlier_method
                )
            except Exception as e:
                logger.error(f"Failed to analyze variable '{var}': {e}")
                continue

        return results

    def _is_numeric_type(self, spark_type: str) -> bool:
        """Check if a Spark data type is numeric."""
        numeric_types = [
            'int', 'integer', 'bigint', 'long', 'float', 'double',
            'decimal', 'numeric', 'real', 'smallint', 'tinyint'
        ]
        return any(num_type in spark_type.lower() for num_type in numeric_types)

    def _extract_raw_dataframe(self, df: DataFrame) -> DataFrame:
        """
        Extract raw PySpark DataFrame from potential LineageDataFrame.

        This prevents distribution analysis operations from polluting the lineage
        graph with measurement-only operations.
        """
        if hasattr(df, '_df'):
            logger.debug("Extracted raw DataFrame from LineageDataFrame for distribution analysis")
            return df._df
        else:
            return df

    def _apply_sampling(self, df: DataFrame, sample_size: Optional[int]) -> DataFrame:
        """Apply random sampling to DataFrame if sample_size is specified."""
        if sample_size is None:
            return df

        # CRITICAL FIX: Extract raw DataFrame to prevent lineage pollution
        raw_df = self._extract_raw_dataframe(df)

        total_count = raw_df.count()
        if total_count <= sample_size:
            return raw_df

        # Calculate sampling fraction
        fraction = sample_size / total_count
        return raw_df.sample(withReplacement=False, fraction=fraction, seed=42)

    def _remove_outliers(self,
                        df: DataFrame,
                        variable: str,
                        method: OutlierMethod) -> Tuple[DataFrame, int]:
        """Remove outliers using the specified method."""
        # CRITICAL FIX: Extract raw DataFrame to prevent lineage pollution
        raw_df = self._extract_raw_dataframe(df)

        original_count = raw_df.count()

        if method == OutlierMethod.IQR:
            # Calculate IQR bounds
            percentiles = raw_df.select(
                percentile_approx(col(variable), 0.25).alias("q25"),
                percentile_approx(col(variable), 0.75).alias("q75")
            ).collect()[0]

            q25, q75 = percentiles['q25'], percentiles['q75']
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr

            clean_df = raw_df.filter(
                (col(variable) >= lower_bound) &
                (col(variable) <= upper_bound)
            )

        elif method == OutlierMethod.Z_SCORE:
            # Calculate Z-score bounds
            stats = raw_df.select(
                mean(col(variable)).alias("mean"),
                stddev(col(variable)).alias("stddev")
            ).collect()[0]

            var_mean, var_std = stats['mean'], stats['stddev']
            lower_bound = var_mean - self.outlier_z_threshold * var_std
            upper_bound = var_mean + self.outlier_z_threshold * var_std

            clean_df = raw_df.filter(
                (col(variable) >= lower_bound) &
                (col(variable) <= upper_bound)
            )

        elif method == OutlierMethod.PERCENTILE:
            # Calculate percentile bounds
            lower_pct, upper_pct = self.outlier_percentile_threshold
            percentiles = raw_df.select(
                percentile_approx(col(variable), lower_pct/100).alias("lower"),
                percentile_approx(col(variable), upper_pct/100).alias("upper")
            ).collect()[0]

            lower_bound, upper_bound = percentiles['lower'], percentiles['upper']

            clean_df = raw_df.filter(
                (col(variable) >= lower_bound) &
                (col(variable) <= upper_bound)
            )

        else:
            return raw_df, 0

        clean_count = clean_df.count()
        outlier_count = original_count - clean_count

        return clean_df, outlier_count

    def _calculate_statistics(self, df: DataFrame, variable: str) -> DistributionStats:
        """Calculate comprehensive statistics for a variable."""
        # CRITICAL FIX: Extract raw DataFrame to prevent lineage pollution
        raw_df = self._extract_raw_dataframe(df)

        # Basic aggregations
        stats_row = raw_df.select(
            count(col(variable)).alias("non_null_count"),
            count("*").alias("total_count"),
            mean(col(variable)).alias("mean"),
            stddev(col(variable)).alias("stddev"),
            spark_min(col(variable)).alias("min_value"),
            spark_max(col(variable)).alias("max_value"),
            percentile_approx(col(variable), 0.25).alias("q25"),
            percentile_approx(col(variable), 0.5).alias("median"),
            percentile_approx(col(variable), 0.75).alias("q75")
        ).collect()[0]

        # Convert to DistributionStats
        total_count = stats_row['total_count']
        non_null_count = stats_row['non_null_count']
        null_count = total_count - non_null_count

        return DistributionStats(
            variable_name=variable,
            total_count=total_count,
            non_null_count=non_null_count,
            null_count=null_count,
            mean=float(stats_row['mean']) if stats_row['mean'] is not None else 0.0,
            median=float(stats_row['median']) if stats_row['median'] is not None else 0.0,
            std_dev=float(stats_row['stddev']) if stats_row['stddev'] is not None else 0.0,
            min_value=float(stats_row['min_value']) if stats_row['min_value'] is not None else 0.0,
            max_value=float(stats_row['max_value']) if stats_row['max_value'] is not None else 0.0,
            q25=float(stats_row['q25']) if stats_row['q25'] is not None else 0.0,
            q75=float(stats_row['q75']) if stats_row['q75'] is not None else 0.0
        )