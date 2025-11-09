#!/usr/bin/env python3
"""
Comprehensive Tracking Decorator/Context Manager.

This module provides a unified interface for applying multiple tracking decorators
at once, simplifying common tracking scenarios.

Example:
    >>> @comprehensiveTracking(
    ...     track_expressions=["revenue", "profit"],
    ...     profile_columns=["revenue", "profit", "customers"],
    ...     analyze_distributions=["revenue"],
    ...     materialize=True
    ... )
    ... def calculate_metrics(df):
    ...     return df.withColumn("profit", col("revenue") - col("cost"))
"""

import functools
import logging
from typing import Any, Callable, List, Optional, Union

from ..core.decorators import track_lineage
from .describe_profiler import describeProfiler
from .distribution_decorator import distributionCheckpoint
from .expression_lineage_decorator import expressionLineage

logger = logging.getLogger(__name__)


def comprehensiveTracking(
    # Lineage tracking parameters
    materialize: bool = True,
    track_columns: Optional[List[str]] = None,

    # Expression lineage parameters
    track_expressions: Optional[Union[List[str], bool]] = None,

    # Describe profiler parameters
    profile_checkpoint: Optional[str] = None,
    profile_columns: Union[List[str], str] = 'ALL',

    # Distribution analyzer parameters
    analyze_distributions: Optional[List[str]] = None,
    distribution_step: Optional[str] = None,

    # Common parameters
    enable_all: bool = False
) -> Callable:
    """
    Comprehensive tracking decorator combining lineage, expression, profiling, and distribution analysis.

    This decorator simplifies applying multiple tracking features by providing a single interface.
    It intelligently applies the appropriate decorators based on the parameters provided.

    Args:
        materialize: Whether to materialize the result (cache + count)
        track_columns: Columns to track through lineage

        track_expressions: Columns to track expression lineage for.
                          Set to True to track all expressions, False/None to disable.

        profile_checkpoint: Name for describe profiler checkpoint.
                           If provided, enables describe profiling.
        profile_columns: Columns to profile ('ALL', None for numeric only, or list of column names)

        analyze_distributions: Variables to analyze distributions for.
                              If provided, enables distribution analysis.
        distribution_step: Step name for distribution analysis (defaults to checkpoint name)

        enable_all: If True, enables all tracking features with sensible defaults.

    Returns:
        Decorated function with all requested tracking features

    Examples:
        Basic usage with all features:
        >>> @comprehensiveTracking(
        ...     profile_checkpoint="After Calculation",
        ...     track_expressions=["revenue", "profit"],
        ...     analyze_distributions=["revenue", "profit"]
        ... )
        ... def calculate_metrics(df):
        ...     return df.withColumn("profit", col("revenue") - col("cost"))

        Enable everything with defaults:
        >>> @comprehensiveTracking(enable_all=True, profile_checkpoint="Checkpoint")
        ... def process_data(df):
        ...     return df.filter(col("amount") > 100)

        Just expression tracking and profiling:
        >>> @comprehensiveTracking(
        ...     track_expressions=True,  # Track all expressions
        ...     profile_checkpoint="Final Output"
        ... )
        ... def final_step(df):
        ...     return df
    """

    def decorator(func: Callable) -> Callable:
        # Start with the original function
        wrapped = func

        # Apply decorators from innermost to outermost (reverse order of execution)

        # 1. Track lineage (innermost - executes first)
        wrapped = track_lineage(
            materialize=materialize,
            track_columns=track_columns
        )(wrapped)

        # 2. Expression lineage (if requested)
        if track_expressions or enable_all:
            if track_expressions is True or enable_all:
                # Auto-detect: track all columns created in function
                # This will be handled by expressionLineage with target_columns=None
                wrapped = expressionLineage(target_columns=None)(wrapped)
            elif isinstance(track_expressions, list):
                wrapped = expressionLineage(target_columns=track_expressions)(wrapped)

        # 3. Describe profiler (if checkpoint provided)
        if profile_checkpoint or enable_all:
            checkpoint_name = profile_checkpoint or func.__name__
            wrapped = describeProfiler(
                checkpoint_name=checkpoint_name,
                columns=profile_columns
            )(wrapped)

        # 4. Distribution analyzer (if distributions requested)
        # Note: Distribution analyzer is typically used as context manager inline,
        # but we can add metadata to indicate it should be used
        if analyze_distributions or enable_all:
            # Store metadata for user to apply distribution analyzer manually
            # (since it needs to be applied to intermediate DataFrames)
            if not hasattr(wrapped, '_tracking_metadata'):
                wrapped._tracking_metadata = {}
            wrapped._tracking_metadata['distribution_variables'] = (
                analyze_distributions if analyze_distributions
                else track_columns if track_columns
                else []
            )
            wrapped._tracking_metadata['distribution_step'] = (
                distribution_step or profile_checkpoint or func.__name__
            )

        return wrapped

    return decorator


class ComprehensiveTrackingContext:
    """
    Context manager for inline comprehensive tracking.

    Provides the same features as the decorator but for inline usage.

    Example:
        >>> with comprehensiveTrackingContext(
        ...     profile_checkpoint="Midpoint Check",
        ...     analyze_distributions=["amount"]
        ... ) as tracker:
        ...     result = df.filter(col("amount") > 100)
        ...     tracker.profile(result)
        ...     tracker.analyze_distribution(result)
    """

    def __init__(
        self,
        profile_checkpoint: Optional[str] = None,
        profile_columns: Union[List[str], str] = 'ALL',
        analyze_distributions: Optional[List[str]] = None,
        distribution_step: Optional[str] = None
    ):
        """
        Initialize comprehensive tracking context.

        Args:
            profile_checkpoint: Name for describe profiler checkpoint
            profile_columns: Columns to profile
            analyze_distributions: Variables to analyze distributions for
            distribution_step: Step name for distribution analysis
        """
        self.profile_checkpoint = profile_checkpoint
        self.profile_columns = profile_columns
        self.analyze_distributions = analyze_distributions
        self.distribution_step = distribution_step or profile_checkpoint or "inline_tracking"

        self._describe_profiler = None
        self._distribution_analyzer = None

    def __enter__(self):
        """Enter the tracking context."""
        logger.info(f"Starting comprehensive tracking context: {self.profile_checkpoint or 'inline'}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the tracking context."""
        logger.info(f"Completed comprehensive tracking context: {self.profile_checkpoint or 'inline'}")

    def profile(self, df, function_name: str = "context_capture"):
        """
        Capture describe profile for a DataFrame.

        Args:
            df: DataFrame to profile
            function_name: Name of the function context
        """
        if self.profile_checkpoint:
            from .describe_profiler import DescribeProfilerContext

            context = DescribeProfilerContext(
                checkpoint_name=self.profile_checkpoint,
                columns=None if self.profile_columns == 'ALL' else self.profile_columns,
                store_in_tracker=True
            )

            with context:
                context.capture(df, function_name=function_name)

    def analyze_distribution(self, df, function_name: str = "context_capture"):
        """
        Analyze distributions for a DataFrame.

        Args:
            df: DataFrame to analyze
            function_name: Name of the function context
        """
        if self.analyze_distributions:
            with distributionCheckpoint(
                checkpoint_name=self.distribution_step or function_name,
                variables=self.analyze_distributions
            ) as context:
                context.capture(df, label=function_name)

    def track_all(self, df, function_name: str = "context_capture"):
        """
        Apply all enabled tracking to a DataFrame.

        Args:
            df: DataFrame to track
            function_name: Name of the function context
        """
        if self.profile_checkpoint:
            self.profile(df, function_name)
        if self.analyze_distributions:
            self.analyze_distribution(df, function_name)


def comprehensiveTrackingContext(
    profile_checkpoint: Optional[str] = None,
    profile_columns: Union[List[str], str] = 'ALL',
    analyze_distributions: Optional[List[str]] = None,
    distribution_step: Optional[str] = None
) -> ComprehensiveTrackingContext:
    """
    Create a comprehensive tracking context manager.

    This provides inline tracking capabilities without needing decorators.

    Args:
        profile_checkpoint: Name for describe profiler checkpoint
        profile_columns: Columns to profile
        analyze_distributions: Variables to analyze distributions for
        distribution_step: Step name for distribution analysis

    Returns:
        Context manager for comprehensive tracking

    Example:
        >>> with comprehensiveTrackingContext(
        ...     profile_checkpoint="After Filtering",
        ...     analyze_distributions=["amount", "quantity"]
        ... ) as tracker:
        ...     filtered = df.filter(col("amount") > 100)
        ...     tracker.track_all(filtered, function_name="filter_data")
    """
    return ComprehensiveTrackingContext(
        profile_checkpoint=profile_checkpoint,
        profile_columns=profile_columns,
        analyze_distributions=analyze_distributions,
        distribution_step=distribution_step
    )


# Convenience function for quick tracking
def quickTrack(
    checkpoint_name: str,
    track_expressions: bool = True,
    profile: bool = True,
    distributions: Optional[List[str]] = None
) -> Callable:
    """
    Quick tracking decorator with sensible defaults.

    Simplest interface for common tracking scenarios.

    Args:
        checkpoint_name: Name for this checkpoint (used for profiling and distributions)
        track_expressions: Whether to track all expression lineage
        profile: Whether to enable describe profiling
        distributions: List of variables to analyze distributions (None = disable)

    Returns:
        Decorated function with tracking enabled

    Example:
        >>> @quickTrack("Calculate Revenue", distributions=["revenue", "cost"])
        ... def calculate_revenue(df):
        ...     return df.withColumn("revenue", col("price") * col("quantity"))
    """
    return comprehensiveTracking(
        materialize=True,
        track_expressions=track_expressions,
        profile_checkpoint=checkpoint_name if profile else None,
        profile_columns='ALL',
        analyze_distributions=distributions
    )
