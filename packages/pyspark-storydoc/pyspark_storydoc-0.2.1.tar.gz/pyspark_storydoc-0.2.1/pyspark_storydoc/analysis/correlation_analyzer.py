"""
Correlation Analyzer for PySpark StoryDoc.

This module provides correlation analysis capabilities:
- Captures correlation matrices at key pipeline points
- Detects multicollinearity warnings
- Stores results for report generation
- Integration with PySpark DataFrames and lineage tracking
"""

import functools
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TypeVar

import pandas as pd
from pyspark.sql import DataFrame

from ..core.lineage_tracker import get_global_tracker
from ..utils.dataframe_utils import is_dataframe

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class CorrelationStats:
    """Container for correlation analysis results."""
    checkpoint_name: str
    function_name: str
    timestamp: float
    columns: List[str]
    correlation_matrix: pd.DataFrame
    high_correlations: List[Dict[str, Any]]
    multicollinearity_warnings: List[str]
    row_count: int
    result_dataframe_lineage_ref: Optional[str] = None
    parent_operation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'checkpoint_name': self.checkpoint_name,
            'function_name': self.function_name,
            'timestamp': self.timestamp,
            'columns': self.columns,
            'correlation_matrix': self.correlation_matrix.to_dict(),
            'high_correlations': self.high_correlations,
            'multicollinearity_warnings': self.multicollinearity_warnings,
            'row_count': self.row_count,
            'result_dataframe_lineage_ref': self.result_dataframe_lineage_ref,
            'parent_operation_id': self.parent_operation_id,
            'metadata': self.metadata
        }


class CorrelationAnalyzer:
    """
    Core engine for correlation analysis.

    Computes correlation matrices and detects multicollinearity.
    """

    def __init__(self, correlation_threshold: float = 0.7):
        """
        Initialize the correlation analyzer.

        Args:
            correlation_threshold: Threshold for flagging high correlations (default 0.7)
        """
        self.correlation_threshold = correlation_threshold
        self.analyses = []

    def analyze_correlations(
        self,
        df: DataFrame,
        checkpoint_name: str,
        function_name: str = "unknown",
        columns: Optional[List[str]] = None,
        result_dataframe_lineage_ref: Optional[str] = None
    ) -> Optional[CorrelationStats]:
        """
        Compute correlation matrix for specified columns.

        Args:
            df: Spark DataFrame to analyze
            checkpoint_name: Name for this analysis checkpoint
            function_name: Name of the function being analyzed
            columns: Specific columns to analyze (None = all numeric columns)
            result_dataframe_lineage_ref: Lineage ID of the DataFrame

        Returns:
            CorrelationStats object containing the analysis results
        """
        try:
            row_count = df.count()

            # Select numeric columns if not specified
            if columns is None:
                from pyspark.sql.types import NumericType
                columns = [f.name for f in df.schema.fields
                          if isinstance(f.dataType, NumericType)]

            if len(columns) < 2:
                logger.warning(f"Need at least 2 numeric columns for correlation analysis, got {len(columns)}")
                return None

            # Compute correlation matrix using PySpark
            # Convert to pandas for easier manipulation
            pandas_df = df.select(*columns).toPandas()
            corr_matrix = pandas_df.corr()

            # Find high correlations
            high_correlations = []
            multicollinearity_warnings = []

            for i, col1 in enumerate(columns):
                for j, col2 in enumerate(columns):
                    if i >= j:  # Skip diagonal and duplicates
                        continue

                    corr_value = corr_matrix.loc[col1, col2]

                    if abs(corr_value) >= self.correlation_threshold:
                        high_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': corr_value
                        })

                        warning = (f"High correlation between '{col1}' and '{col2}': "
                                 f"{corr_value:.3f}")
                        multicollinearity_warnings.append(warning)

            # Create stats object
            stats = CorrelationStats(
                checkpoint_name=checkpoint_name,
                function_name=function_name,
                timestamp=time.time(),
                columns=columns,
                correlation_matrix=corr_matrix,
                high_correlations=high_correlations,
                multicollinearity_warnings=multicollinearity_warnings,
                row_count=row_count,
                result_dataframe_lineage_ref=result_dataframe_lineage_ref,
                parent_operation_id=None
            )

            self.analyses.append(stats)
            logger.info(f"Computed correlation matrix at '{checkpoint_name}': "
                       f"{len(columns)} columns, {len(high_correlations)} high correlations")

            return stats

        except Exception as e:
            logger.error(f"Failed to compute correlations at '{checkpoint_name}': {e}")
            raise


def correlationAnalyzer(
    checkpoint_name: str,
    columns: Optional[List[str]] = None,
    correlation_threshold: float = 0.7,
    store_in_tracker: bool = True
) -> Callable[[F], F]:
    """
    Decorator to automatically compute correlation matrix at a pipeline point.

    Args:
        checkpoint_name: Descriptive name for this analysis checkpoint
        columns: Specific columns to analyze (None = all numeric columns)
        correlation_threshold: Threshold for flagging high correlations
        store_in_tracker: Whether to store analysis in global tracker

    Returns:
        Decorated function with correlation analysis

    Example:
        >>> @correlationAnalyzer(
        ...     checkpoint_name="After Feature Engineering",
        ...     columns=["age", "income", "credit_score", "loan_amount"]
        ... )
        ... def engineer_features(df):
        ...     return df.withColumn("credit_score", calculate_score(...))
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Analyze correlations if result is a DataFrame
            if is_dataframe(result):
                try:
                    analyzer = CorrelationAnalyzer(correlation_threshold=correlation_threshold)

                    # Capture lineage ID
                    result_lineage_ref = None
                    if hasattr(result, '_lineage_id'):
                        result_lineage_ref = result._lineage_id.id
                    elif hasattr(result, 'lineage_id'):
                        result_lineage_ref = result.lineage_id

                    # Analyze correlations
                    stats = analyzer.analyze_correlations(
                        df=result,
                        checkpoint_name=checkpoint_name,
                        function_name=func.__name__,
                        columns=columns,
                        result_dataframe_lineage_ref=result_lineage_ref
                    )

                    # Store in global tracker if requested
                    if store_in_tracker and stats:
                        try:
                            tracker = get_global_tracker()

                            if not hasattr(tracker, '_correlation_analyses'):
                                tracker._correlation_analyses = []

                            analysis_data = {
                                'checkpoint_name': checkpoint_name,
                                'function_name': func.__name__,
                                'stats': stats,
                                'execution_time': execution_time,
                                'timestamp': time.time()
                            }

                            tracker._correlation_analyses.append(analysis_data)
                            logger.info(f"Stored correlation analysis '{checkpoint_name}': "
                                       f"{len(tracker._correlation_analyses)} total analyses")

                        except Exception as e:
                            logger.error(f"Could not store correlation analysis in tracker: {e}")

                except Exception as e:
                    logger.error(f"Failed to analyze correlations: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                logger.warning(f"Function {func.__name__} did not return a DataFrame, "
                             f"skipping correlation analysis")

            return result

        return wrapper
    return decorator


class CorrelationAnalyzerContext:
    """Context manager for inline correlation analysis."""

    def __init__(
        self,
        checkpoint_name: str,
        columns: Optional[List[str]] = None,
        correlation_threshold: float = 0.7,
        store_in_tracker: bool = True
    ):
        self.checkpoint_name = checkpoint_name
        self.columns = columns
        self.correlation_threshold = correlation_threshold
        self.store_in_tracker = store_in_tracker
        self.analyzer = CorrelationAnalyzer(correlation_threshold=correlation_threshold)
        self.stats = None

    def __enter__(self):
        """Initialize the analysis context."""
        logger.info(f"Started correlation analyzer context: {self.checkpoint_name}")
        return self

    def capture(self, df: DataFrame, function_name: str = "context_capture"):
        """Capture correlation analysis for a DataFrame."""
        if not is_dataframe(df):
            logger.warning(f"Expected DataFrame for analysis, got {type(df)}")
            return

        try:
            # Capture lineage ID
            result_lineage_ref = None
            if hasattr(df, '_lineage_id'):
                result_lineage_ref = df._lineage_id.id
            elif hasattr(df, 'lineage_id'):
                result_lineage_ref = df.lineage_id

            # Analyze correlations
            self.stats = self.analyzer.analyze_correlations(
                df=df,
                checkpoint_name=self.checkpoint_name,
                function_name=function_name,
                columns=self.columns,
                result_dataframe_lineage_ref=result_lineage_ref
            )

            # Store in global tracker if requested
            if self.store_in_tracker and self.stats:
                try:
                    tracker = get_global_tracker()

                    if not hasattr(tracker, '_correlation_analyses'):
                        tracker._correlation_analyses = []

                    analysis_data = {
                        'checkpoint_name': self.checkpoint_name,
                        'function_name': function_name,
                        'stats': self.stats,
                        'timestamp': time.time()
                    }

                    tracker._correlation_analyses.append(analysis_data)
                    logger.info(f"Stored correlation analysis '{self.checkpoint_name}'")

                except Exception as e:
                    logger.error(f"Could not store correlation analysis in tracker: {e}")

        except Exception as e:
            logger.error(f"Failed to analyze correlations: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete the analysis context."""
        logger.info(f"Completed correlation analyzer context: {self.checkpoint_name}")


def correlation_analyzer_context(
    checkpoint_name: str,
    columns: Optional[List[str]] = None,
    correlation_threshold: float = 0.7,
    store_in_tracker: bool = True
) -> CorrelationAnalyzerContext:
    """
    Context manager for inline correlation analysis.

    Args:
        checkpoint_name: Descriptive name for this analysis checkpoint
        columns: Specific columns to analyze (None = all numeric columns)
        correlation_threshold: Threshold for flagging high correlations
        store_in_tracker: Whether to store analysis in global tracker

    Returns:
        Context manager for correlation analysis

    Example:
        >>> with correlation_analyzer_context(
        ...     checkpoint_name="After Join",
        ...     columns=["age", "income", "loan_amount"]
        ... ) as analyzer:
        ...     joined_df = customers.join(loans, "customer_id")
        ...     analyzer.capture(joined_df, function_name="join_loans")
    """
    return CorrelationAnalyzerContext(
        checkpoint_name=checkpoint_name,
        columns=columns,
        correlation_threshold=correlation_threshold,
        store_in_tracker=store_in_tracker
    )
