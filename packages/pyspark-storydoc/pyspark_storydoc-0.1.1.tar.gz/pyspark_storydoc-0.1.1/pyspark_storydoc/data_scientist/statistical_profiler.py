"""
Statistical Profiler for Data Scientists

Provides comprehensive statistical profiling beyond basic describe():
- Distribution analysis (skewness, kurtosis)
- Missing value analysis
- Outlier detection
- Correlation matrices
- ASCII histograms
- Data quality scoring
"""

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)


@dataclass
class DistributionStats:
    """Statistical distribution properties"""
    skewness: float
    kurtosis: float
    shape_description: str


@dataclass
class OutlierInfo:
    """Outlier detection information"""
    lower_bound: float
    upper_bound: float
    lower_count: int
    upper_count: int
    lower_percentage: float
    upper_percentage: float


@dataclass
class MissingValueInfo:
    """Missing value analysis"""
    null_count: int
    null_percentage: float
    zero_count: Optional[int] = None
    zero_percentage: Optional[float] = None
    interpretation: str = ""


@dataclass
class FeatureStats:
    """Comprehensive statistics for a single feature"""
    feature_name: str
    data_type: str

    # Basic statistics
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    percentile_25: Optional[float] = None
    percentile_50: Optional[float] = None
    percentile_75: Optional[float] = None

    # Distribution
    distribution: Optional[DistributionStats] = None

    # Missing values
    missing: Optional[MissingValueInfo] = None

    # Outliers
    outliers: Optional[OutlierInfo] = None

    # Unique values
    unique_count: Optional[int] = None
    unique_percentage: Optional[float] = None

    # Categorical specific
    value_counts: Optional[Dict[str, int]] = None
    mode: Optional[Any] = None
    entropy: Optional[float] = None

    # Histogram data for ASCII visualization
    histogram_bins: Optional[List[Tuple[float, float]]] = None
    histogram_counts: Optional[List[int]] = None


@dataclass
class CorrelationMatrix:
    """Correlation matrix with insights"""
    features: List[str]
    matrix: pd.DataFrame
    strong_correlations: List[Tuple[str, str, float]]
    multicollinearity_warnings: List[str]


@dataclass
class StatisticalProfile:
    """Complete statistical profile for a dataset checkpoint"""
    checkpoint_name: str
    timestamp: float
    row_count: int
    column_count: int

    # Feature statistics
    numeric_features: List[FeatureStats]
    categorical_features: List[FeatureStats]

    # Correlations
    correlation_matrix: Optional[CorrelationMatrix] = None

    # Data quality
    overall_completeness: float = 0.0
    data_quality_score: float = 0.0
    quality_issues: List[str] = field(default_factory=list)

    # Metadata
    function_name: str = "unknown"
    result_dataframe_lineage_ref: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StatisticalProfiler:
    """
    Comprehensive statistical profiler for data scientist outputs.

    Goes beyond basic describe() to provide:
    - Distribution analysis
    - Outlier detection
    - Correlation matrices
    - Data quality scoring
    - ASCII histograms
    """

    def __init__(self):
        """Initialize the profiler."""
        self.profiles = []

    def profile_dataset(
        self,
        df: DataFrame,
        checkpoint_name: str,
        function_name: str = "unknown",
        columns: Optional[List[str]] = None,
        result_dataframe_lineage_ref: Optional[str] = None,
        include_correlations: bool = True,
        histogram_bins: int = 20
    ) -> StatisticalProfile:
        """
        Create comprehensive statistical profile for a dataset.

        Args:
            df: Spark DataFrame to profile
            checkpoint_name: Name for this checkpoint
            function_name: Name of the function
            columns: Specific columns to profile (None = all)
            result_dataframe_lineage_ref: Lineage ID
            include_correlations: Whether to compute correlations
            histogram_bins: Number of bins for histograms

        Returns:
            StatisticalProfile with comprehensive statistics
        """
        logger.info(f"Starting statistical profiling: {checkpoint_name}")
        start_time = time.time()

        # Get row count
        row_count = df.count()

        # Select columns to profile
        if columns:
            df_subset = df.select(*columns)
        else:
            df_subset = df

        # Separate numeric and categorical columns
        numeric_cols = []
        categorical_cols = []

        for field in df_subset.schema.fields:
            if field.dataType.typeName() in ['integer', 'long', 'float', 'double', 'decimal']:
                numeric_cols.append(field.name)
            elif field.dataType.typeName() in ['string', 'boolean']:
                categorical_cols.append(field.name)

        # Profile numeric features
        numeric_features = []
        for col_name in numeric_cols:
            feature_stats = self._profile_numeric_feature(
                df_subset, col_name, row_count, histogram_bins
            )
            numeric_features.append(feature_stats)

        # Profile categorical features
        categorical_features = []
        for col_name in categorical_cols:
            feature_stats = self._profile_categorical_feature(
                df_subset, col_name, row_count
            )
            categorical_features.append(feature_stats)

        # Compute correlations for numeric features
        correlation_matrix = None
        if include_correlations and len(numeric_cols) > 1:
            correlation_matrix = self._compute_correlations(df_subset, numeric_cols)

        # Calculate data quality metrics
        overall_completeness, quality_score, quality_issues = self._assess_data_quality(
            numeric_features + categorical_features, row_count
        )

        # Create profile
        profile = StatisticalProfile(
            checkpoint_name=checkpoint_name,
            timestamp=start_time,
            row_count=row_count,
            column_count=len(numeric_cols) + len(categorical_cols),
            numeric_features=numeric_features,
            categorical_features=categorical_features,
            correlation_matrix=correlation_matrix,
            overall_completeness=overall_completeness,
            data_quality_score=quality_score,
            quality_issues=quality_issues,
            function_name=function_name,
            result_dataframe_lineage_ref=result_dataframe_lineage_ref
        )

        self.profiles.append(profile)
        elapsed = time.time() - start_time
        logger.info(f"Statistical profiling completed: {checkpoint_name} ({elapsed:.2f}s)")

        return profile

    def _profile_numeric_feature(
        self,
        df: DataFrame,
        col_name: str,
        row_count: int,
        histogram_bins: int
    ) -> FeatureStats:
        """Profile a numeric feature."""

        # Basic statistics
        stats = df.select(
            F.count(col_name).alias('count'),
            F.mean(col_name).alias('mean'),
            F.stddev(col_name).alias('std'),
            F.min(col_name).alias('min'),
            F.max(col_name).alias('max'),
            F.expr(f"percentile_approx({col_name}, 0.25)").alias('p25'),
            F.expr(f"percentile_approx({col_name}, 0.50)").alias('p50'),
            F.expr(f"percentile_approx({col_name}, 0.75)").alias('p75'),
            F.skewness(col_name).alias('skewness'),
            F.kurtosis(col_name).alias('kurtosis'),
            F.countDistinct(col_name).alias('unique_count')
        ).first()

        # Missing values
        null_count = row_count - stats['count']
        null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0

        # Count zeros (often important for numeric features)
        zero_count = df.filter(F.col(col_name) == 0).count()
        zero_percentage = (zero_count / row_count) * 100 if row_count > 0 else 0

        missing = MissingValueInfo(
            null_count=null_count,
            null_percentage=null_percentage,
            zero_count=zero_count,
            zero_percentage=zero_percentage,
            interpretation=self._interpret_missing_values(null_percentage, zero_percentage)
        )

        # Distribution analysis
        skewness = stats['skewness'] if stats['skewness'] is not None else 0
        kurtosis = stats['kurtosis'] if stats['kurtosis'] is not None else 0

        distribution = DistributionStats(
            skewness=skewness,
            kurtosis=kurtosis,
            shape_description=self._describe_distribution_shape(skewness, kurtosis)
        )

        # Outlier detection using IQR method
        outliers = None
        if stats['p25'] is not None and stats['p75'] is not None:
            outliers = self._detect_outliers_iqr(df, col_name, stats['p25'], stats['p75'])

        # Histogram for visualization
        histogram_bins_data, histogram_counts = self._compute_histogram(
            df, col_name, histogram_bins, stats['min'], stats['max']
        )

        return FeatureStats(
            feature_name=col_name,
            data_type='numeric',
            count=stats['count'],
            mean=float(stats['mean']) if stats['mean'] is not None else None,
            std=float(stats['std']) if stats['std'] is not None else None,
            min_val=stats['min'],
            max_val=stats['max'],
            percentile_25=float(stats['p25']) if stats['p25'] is not None else None,
            percentile_50=float(stats['p50']) if stats['p50'] is not None else None,
            percentile_75=float(stats['p75']) if stats['p75'] is not None else None,
            distribution=distribution,
            missing=missing,
            outliers=outliers,
            unique_count=stats['unique_count'],
            unique_percentage=(stats['unique_count'] / row_count * 100) if row_count > 0 else 0,
            histogram_bins=histogram_bins_data,
            histogram_counts=histogram_counts
        )

    def _profile_categorical_feature(
        self,
        df: DataFrame,
        col_name: str,
        row_count: int
    ) -> FeatureStats:
        """Profile a categorical feature."""

        # Basic counts
        count = df.select(F.count(col_name)).first()[0]
        null_count = row_count - count
        null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0

        missing = MissingValueInfo(
            null_count=null_count,
            null_percentage=null_percentage,
            interpretation=f"{'No missing values' if null_count == 0 else f'{null_percentage:.1f}% missing'}"
        )

        # Value counts (top 10)
        value_counts_df = df.groupBy(col_name).count() \
            .orderBy(F.desc('count')) \
            .limit(10) \
            .collect()

        value_counts = {str(row[col_name]): row['count'] for row in value_counts_df if row[col_name] is not None}

        # Mode (most frequent value)
        mode = value_counts_df[0][col_name] if value_counts_df else None

        # Unique count
        unique_count = df.select(F.countDistinct(col_name)).first()[0]

        # Calculate entropy (measure of diversity)
        entropy = self._calculate_entropy(value_counts_df, count)

        return FeatureStats(
            feature_name=col_name,
            data_type='categorical',
            count=count,
            missing=missing,
            unique_count=unique_count,
            unique_percentage=(unique_count / row_count * 100) if row_count > 0 else 0,
            value_counts=value_counts,
            mode=mode,
            entropy=entropy
        )

    def _detect_outliers_iqr(
        self,
        df: DataFrame,
        col_name: str,
        q25: float,
        q75: float
    ) -> OutlierInfo:
        """Detect outliers using IQR method."""
        iqr = q75 - q25
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr

        # Count outliers
        lower_outliers = df.filter(F.col(col_name) < lower_bound).count()
        upper_outliers = df.filter(F.col(col_name) > upper_bound).count()
        total_count = df.count()

        return OutlierInfo(
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            lower_count=lower_outliers,
            upper_count=upper_outliers,
            lower_percentage=(lower_outliers / total_count * 100) if total_count > 0 else 0,
            upper_percentage=(upper_outliers / total_count * 100) if total_count > 0 else 0
        )

    def _compute_histogram(
        self,
        df: DataFrame,
        col_name: str,
        num_bins: int,
        min_val: Any,
        max_val: Any
    ) -> Tuple[List[Tuple[float, float]], List[int]]:
        """Compute histogram bins and counts."""
        if min_val is None or max_val is None or min_val == max_val:
            return [], []

        # Create bins
        bin_width = (float(max_val) - float(min_val)) / num_bins
        bins = []
        counts = []

        for i in range(num_bins):
            bin_start = float(min_val) + i * bin_width
            bin_end = bin_start + bin_width
            bins.append((bin_start, bin_end))

            # Count values in bin
            if i == num_bins - 1:
                # Include upper bound for last bin
                count = df.filter(
                    (F.col(col_name) >= bin_start) & (F.col(col_name) <= bin_end)
                ).count()
            else:
                count = df.filter(
                    (F.col(col_name) >= bin_start) & (F.col(col_name) < bin_end)
                ).count()
            counts.append(count)

        return bins, counts

    def _compute_correlations(
        self,
        df: DataFrame,
        numeric_cols: List[str]
    ) -> CorrelationMatrix:
        """Compute correlation matrix and identify strong correlations."""

        # Compute correlation matrix using pandas for convenience
        pandas_df = df.select(*numeric_cols).toPandas()
        corr_matrix = pandas_df.corr()

        # Find strong correlations
        strong_correlations = []
        multicollinearity_warnings = []

        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:  # Only upper triangle
                    corr_value = corr_matrix.loc[col1, col2]
                    if not np.isnan(corr_value):
                        abs_corr = abs(corr_value)
                        if abs_corr > 0.7:  # Strong correlation
                            strong_correlations.append((col1, col2, corr_value))
                            if abs_corr > 0.8:  # Multicollinearity warning
                                multicollinearity_warnings.append(
                                    f"{col1} and {col2} are highly correlated ({corr_value:.2f})"
                                )

        # Sort by absolute correlation value
        strong_correlations.sort(key=lambda x: abs(x[2]), reverse=True)

        return CorrelationMatrix(
            features=numeric_cols,
            matrix=corr_matrix,
            strong_correlations=strong_correlations,
            multicollinearity_warnings=multicollinearity_warnings
        )

    def _assess_data_quality(
        self,
        features: List[FeatureStats],
        row_count: int
    ) -> Tuple[float, float, List[str]]:
        """Assess overall data quality."""

        if not features:
            return 100.0, 100.0, []

        # Calculate completeness
        total_values = len(features) * row_count
        missing_values = sum(
            f.missing.null_count if f.missing else 0
            for f in features
        )
        completeness = ((total_values - missing_values) / total_values * 100) if total_values > 0 else 100

        # Quality scoring
        quality_score = 100.0
        issues = []

        # Penalize for missing values
        for feature in features:
            if feature.missing:
                if feature.missing.null_percentage > 10:
                    quality_score -= 5
                    issues.append(f"{feature.feature_name}: {feature.missing.null_percentage:.1f}% missing values")
                elif feature.missing.null_percentage > 5:
                    quality_score -= 2

        # Check for outliers
        for feature in features:
            if feature.outliers:
                total_outliers_pct = feature.outliers.lower_percentage + feature.outliers.upper_percentage
                if total_outliers_pct > 5:
                    issues.append(f"{feature.feature_name}: {total_outliers_pct:.1f}% outliers")

        # Ensure score doesn't go below 0
        quality_score = max(0, quality_score)

        return completeness, quality_score, issues

    def _describe_distribution_shape(self, skewness: float, kurtosis: float) -> str:
        """Describe the shape of a distribution."""
        skew_desc = ""
        if abs(skewness) < 0.5:
            skew_desc = "roughly symmetric"
        elif skewness > 0.5:
            skew_desc = "right-skewed" if skewness < 1 else "strongly right-skewed"
        else:
            skew_desc = "left-skewed" if skewness > -1 else "strongly left-skewed"

        kurt_desc = ""
        if abs(kurtosis) < 0.5:
            kurt_desc = "normal tails"
        elif kurtosis > 0.5:
            kurt_desc = "heavy tails" if kurtosis < 3 else "very heavy tails"
        else:
            kurt_desc = "light tails"

        return f"{skew_desc}, {kurt_desc}"

    def _interpret_missing_values(
        self,
        null_percentage: float,
        zero_percentage: float
    ) -> str:
        """Interpret missing value patterns."""
        parts = []

        if null_percentage == 0:
            parts.append("No missing data")
        elif null_percentage < 1:
            parts.append(f"{null_percentage:.2f}% missing")
        else:
            parts.append(f"{null_percentage:.1f}% missing")

        if zero_percentage > 5:
            parts.append(f"{zero_percentage:.1f}% zeros")

        return " - ".join(parts) if parts else "Complete data"

    def _calculate_entropy(self, value_counts: List, total_count: int) -> float:
        """Calculate Shannon entropy for categorical distribution."""
        if not value_counts or total_count == 0:
            return 0.0

        entropy = 0.0
        for row in value_counts:
            if row[1] > 0:  # count > 0
                probability = row[1] / total_count
                entropy -= probability * math.log2(probability)

        return entropy


def generate_statistical_checkpoint(
    df: DataFrame,
    checkpoint_name: str,
    output_path: str,
    function_name: str = "unknown",
    columns: Optional[List[str]] = None,
    include_correlations: bool = True
) -> str:
    """
    Generate a statistical profile checkpoint report.

    Args:
        df: DataFrame to profile
        checkpoint_name: Name for this checkpoint
        output_path: Where to save the report
        function_name: Function name
        columns: Columns to profile
        include_correlations: Include correlation analysis

    Returns:
        Path to generated report
    """
    from .statistical_report_generator import StatisticalReportGenerator

    profiler = StatisticalProfiler()
    profile = profiler.profile_dataset(
        df=df,
        checkpoint_name=checkpoint_name,
        function_name=function_name,
        columns=columns,
        include_correlations=include_correlations
    )

    generator = StatisticalReportGenerator()
    return generator.generate_report(profile, output_path)
