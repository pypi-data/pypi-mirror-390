#!/usr/bin/env python3
"""
Describe Profiler for PySpark StoryDoc.

This module provides DataFrame profiling capabilities using PySpark's describe() method:
- Captures comprehensive descriptive statistics at key pipeline points
- Stores describe() output tables for report generation
- Integration with PySpark DataFrames and lineage tracking
"""

import functools
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

import pandas as pd
from pyspark.sql import DataFrame

from ..core.lineage_tracker import get_global_tracker
from ..utils.dataframe_utils import extract_dataframes, is_dataframe

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class DescribeStats:
    """Container for describe() statistics."""
    checkpoint_name: str
    function_name: str
    timestamp: float
    columns: List[str]
    describe_df: pd.DataFrame
    row_count: int
    column_count: int
    result_dataframe_lineage_ref: Optional[str] = None
    parent_operation_id: Optional[str] = None  # Resolved at diagram generation time
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'checkpoint_name': self.checkpoint_name,
            'function_name': self.function_name,
            'timestamp': self.timestamp,
            'columns': self.columns,
            'describe_table': self.describe_df.to_dict('records'),
            'row_count': self.row_count,
            'column_count': self.column_count,
            'result_dataframe_lineage_ref': self.result_dataframe_lineage_ref,
            'parent_operation_id': self.parent_operation_id,
            'metadata': self.metadata
        }


class DescribeProfiler:
    """
    Core engine for DataFrame profiling using describe().

    This class captures comprehensive descriptive statistics at specified
    points in the data pipeline for inclusion in reports.
    """

    def __init__(self):
        """Initialize the describe profiler."""
        self.profiles = []

    def capture_profile(self,
                       df: DataFrame,
                       checkpoint_name: str,
                       function_name: str = "unknown",
                       columns: Optional[List[str]] = None,
                       result_dataframe_lineage_ref: Optional[str] = None) -> DescribeStats:
        """
        Capture describe() statistics for a DataFrame.

        Args:
            df: Spark DataFrame to profile
            checkpoint_name: Name for this profiling checkpoint
            function_name: Name of the function being profiled
            columns: Specific columns to include (None = all numeric columns)
            result_dataframe_lineage_ref: Lineage ID of the DataFrame being profiled

        Returns:
            DescribeStats object containing the captured statistics
        """
        try:
            # Get row and column counts
            row_count = df.count()

            # Run describe on specified columns or all columns
            if columns:
                describe_df = df.select(*columns).describe()
            else:
                describe_df = df.describe()

            # Convert to pandas for easier manipulation
            describe_pandas = describe_df.toPandas()

            # Get the columns that were described
            described_columns = list(describe_pandas.columns)
            if 'summary' in described_columns:
                described_columns.remove('summary')

            # Create stats object
            stats = DescribeStats(
                checkpoint_name=checkpoint_name,
                function_name=function_name,
                timestamp=time.time(),
                columns=described_columns,
                describe_df=describe_pandas,
                row_count=row_count,
                column_count=len(described_columns),
                result_dataframe_lineage_ref=result_dataframe_lineage_ref,
                parent_operation_id=None  # Will be resolved at diagram generation time
            )

            self.profiles.append(stats)
            logger.info(f"Captured describe profile '{checkpoint_name}': {len(described_columns)} columns, {row_count} rows")

            return stats

        except Exception as e:
            logger.error(f"Failed to capture describe profile '{checkpoint_name}': {e}")
            raise


def describeProfiler(
    checkpoint_name: str,
    columns: Optional[List[str]] = 'ALL',
    store_in_tracker: bool = True
) -> Callable[[F], F]:
    """
    Decorator to automatically capture describe() statistics at a pipeline point.

    This decorator will:
    1. Execute the decorated function
    2. Capture describe() statistics on the output DataFrame
    3. Store results for inclusion in reports
    4. Create a profiling node in the lineage diagram

    Args:
        checkpoint_name: Descriptive name for this profiling checkpoint
        columns: Specific columns to profile ('ALL' = all columns, None = all numeric columns, or list of column names)
        store_in_tracker: Whether to store profile in global tracker

    Returns:
        Decorated function with describe profiling

    Examples:
        >>> @describeProfiler(
        ...     checkpoint_name="After Premium Calculation",
        ...     columns=["base_rate", "comprehensive_premium", "discount"]
        ... )
        ... def calculate_premiums(df):
        ...     return df.withColumn("premium", col("base_rate") * col("factor"))

        >>> @describeProfiler(checkpoint_name="Final Output")  # Profiles all columns
        ... def final_transformations(df):
        ...     return df.select("customer_id", "premium", "quote_type")
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Capture describe profile if result is a DataFrame
            if is_dataframe(result):
                try:
                    profiler = DescribeProfiler()

                    # Capture the lineage ID of the result DataFrame
                    # This is the lineage identifier that gets mapped to mermaid nodes
                    # The actual parent operation will be resolved at diagram generation time
                    # by finding operations with this lineage and their children (e.g., materialize)
                    result_lineage_ref = None
                    if hasattr(result, '_lineage_id'):
                        # Use the full lineage ID - this is what's in lineage_to_mermaid mapping
                        result_lineage_ref = result._lineage_id.id
                    elif hasattr(result, 'lineage_id'):
                        result_lineage_ref = result.lineage_id

                    # Handle 'ALL' columns case
                    profile_columns = None if columns == 'ALL' else columns

                    # Capture the profile
                    stats = profiler.capture_profile(
                        df=result,
                        checkpoint_name=checkpoint_name,
                        function_name=func.__name__,
                        columns=profile_columns,
                        result_dataframe_lineage_ref=result_lineage_ref
                    )

                    # Store in global tracker if requested
                    if store_in_tracker:
                        try:
                            tracker = get_global_tracker()

                            # Initialize the attribute if it doesn't exist
                            if not hasattr(tracker, '_describe_profiles'):
                                tracker._describe_profiles = []

                            profile_data = {
                                'checkpoint_name': checkpoint_name,
                                'function_name': func.__name__,
                                'stats': stats,
                                'execution_time': execution_time,
                                'timestamp': time.time()
                            }

                            tracker._describe_profiles.append(profile_data)
                            logger.info(f"Stored describe profile '{checkpoint_name}': {len(tracker._describe_profiles)} total profiles")

                        except Exception as e:
                            logger.error(f"Could not store describe profile in global tracker: {e}")
                            import traceback
                            traceback.print_exc()

                except Exception as e:
                    logger.error(f"Failed to capture describe profile: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                logger.warning(f"Function {func.__name__} did not return a DataFrame, skipping describe profiling")

            return result

        return wrapper
    return decorator


class DescribeProfilerContext:
    """
    Context manager for inline describe profiling.

    Captures describe() statistics for a DataFrame within the context block.
    """

    def __init__(self,
                 checkpoint_name: str,
                 columns: Optional[List[str]] = None,
                 store_in_tracker: bool = True):
        self.checkpoint_name = checkpoint_name
        self.columns = columns
        self.store_in_tracker = store_in_tracker
        self.profiler = DescribeProfiler()
        self.stats = None

    def __enter__(self):
        """Initialize the profiling context."""
        logger.info(f"Started describe profiler context: {self.checkpoint_name}")
        return self

    def capture(self, df: DataFrame, function_name: str = "context_capture"):
        """Capture describe profile for a DataFrame."""
        if not is_dataframe(df):
            logger.warning(f"Expected DataFrame for profiling, got {type(df)}")
            return

        try:
            # Capture the lineage ID of the DataFrame
            # This is the lineage identifier that gets mapped to mermaid nodes
            # The actual parent operation will be resolved at diagram generation time
            # by finding operations with this lineage and their children (e.g., materialize)
            result_lineage_ref = None
            if hasattr(df, '_lineage_id'):
                # Use the full lineage ID - this is what's in lineage_to_mermaid mapping
                result_lineage_ref = df._lineage_id.id
            elif hasattr(df, 'lineage_id'):
                result_lineage_ref = df.lineage_id

            # Capture the profile
            self.stats = self.profiler.capture_profile(
                df=df,
                checkpoint_name=self.checkpoint_name,
                function_name=function_name,
                columns=self.columns,
                result_dataframe_lineage_ref=result_lineage_ref
            )

            # Store in global tracker if requested
            if self.store_in_tracker:
                try:
                    tracker = get_global_tracker()

                    # Initialize the attribute if it doesn't exist
                    if not hasattr(tracker, '_describe_profiles'):
                        tracker._describe_profiles = []

                    profile_data = {
                        'checkpoint_name': self.checkpoint_name,
                        'function_name': function_name,
                        'stats': self.stats,
                        'timestamp': time.time()
                    }

                    tracker._describe_profiles.append(profile_data)
                    logger.info(f"Stored describe profile '{self.checkpoint_name}': {len(tracker._describe_profiles)} total profiles")

                except Exception as e:
                    logger.error(f"Could not store describe profile in global tracker: {e}")

        except Exception as e:
            logger.error(f"Failed to capture describe profile: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete the profiling context."""
        logger.info(f"Completed describe profiler context: {self.checkpoint_name}")


def describe_profiler_context(
    checkpoint_name: str,
    columns: Optional[List[str]] = 'ALL',
    store_in_tracker: bool = True
) -> DescribeProfilerContext:
    """
    Context manager for inline describe profiling.

    This provides the same profiling as the @describeProfiler decorator but
    allows for inline usage without decorating a function.

    Args:
        checkpoint_name: Descriptive name for this profiling checkpoint
        columns: Specific columns to profile ('ALL' = all columns, None = all numeric columns, or list of column names)
        store_in_tracker: Whether to store profile in global tracker

    Returns:
        Context manager for describe profiling

    Example:
        >>> with describe_profiler_context("After Filtering") as profiler:
        ...     filtered_df = customers.filter(col("age") > 25)
        ...     profiler.capture(filtered_df)

        >>> # With specific columns
        >>> with describe_profiler_context(
        ...     checkpoint_name="Premium Statistics",
        ...     columns=["base_rate", "premium", "discount"]
        ... ) as profiler:
        ...     result = calculate_premiums(df)
        ...     profiler.capture(result, function_name="calculate_premiums")
    """
    # Handle 'ALL' columns case
    profile_columns = None if columns == 'ALL' else columns

    return DescribeProfilerContext(
        checkpoint_name=checkpoint_name,
        columns=profile_columns,
        store_in_tracker=store_in_tracker
    )
