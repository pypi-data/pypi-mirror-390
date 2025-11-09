#!/usr/bin/env python3
"""
Distribution Analysis Decorator for PySpark StoryDoc.

This module provides decorators for automatically capturing and analyzing
distribution data at key points in data processing pipelines.
"""

import functools
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from ..analysis.distribution_analyzer import DistributionAnalyzer, OutlierMethod
from ..core.lineage_tracker import get_global_tracker
from ..utils.dataframe_utils import extract_dataframes, is_dataframe

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


def distributionAnalysis(
    variables: List[str],
    sample_size: Optional[int] = 10000,
    outlier_methods: List[Union[str, OutlierMethod]] = ["none", "iqr"],
    output_directory: str = "assets",
    include_before_after: bool = True,
    include_summary_stats: bool = True,
    plot_config: Optional[Dict[str, Any]] = None,
    filename_prefix: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorator to automatically capture and analyze variable distributions.

    This decorator will:
    1. Capture distributions before the operation (if include_before_after=True)
    2. Execute the decorated function
    3. Capture distributions after the operation
    4. Generate comparison plots and statistics
    5. Store results for inclusion in reports

    Args:
        variables: List of variable names to analyze
        sample_size: Sample size for analysis (None = no sampling)
        outlier_methods: List of outlier removal methods to apply
        output_directory: Directory to save plots and analysis. Can be absolute or relative path.
                         For integration with markdown reports, use an absolute path or a path
                         relative to where your markdown report will be saved.
                         Example: If your markdown is at "outputs/report.md", use "outputs/assets"
                         Default: "assets" (relative to current working directory)
        include_before_after: Whether to create before/after comparison plots
        include_summary_stats: Whether to generate summary statistics
        plot_config: Custom plot configuration
        filename_prefix: Prefix for generated filenames

    Returns:
        Decorated function with distribution analysis

    Examples:
        >>> # Basic usage with default output directory
        >>> @distributionAnalysis(
        ...     variables=["salary", "age"],
        ...     outlier_methods=["none", "iqr"],
        ...     include_before_after=True
        ... )
        ... def filter_high_salary(df):
        ...     return df.filter(col("salary") > 50000)

        >>> # With explicit output directory for proper markdown integration
        >>> output_dir = Path("outputs/examples/my_analysis")
        >>> @distributionAnalysis(
        ...     variables=["customer_lifetime_value"],
        ...     output_directory=str(output_dir / "assets"),
        ...     sample_size=5000,
        ...     filename_prefix="premium_analysis"
        ... )
        ... def premium_customer_segmentation(df):
        ...     return df.filter(col("tier") == "premium")
    """
    # Validate parameters
    if not variables:
        raise ValueError("At least one variable must be specified for analysis")

    # Convert string outlier methods to enums
    processed_outlier_methods = []
    for method in outlier_methods:
        if isinstance(method, str):
            try:
                processed_outlier_methods.append(OutlierMethod(method.lower()))
            except ValueError:
                logger.warning(f"Unknown outlier method '{method}', skipping")
        else:
            processed_outlier_methods.append(method)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize analyzers with lazy imports to avoid circular dependencies
            analyzer = DistributionAnalyzer(default_sample_size=sample_size)

            # Lazy import to avoid circular dependency
            from ..visualization.distribution_visualizer import (
                DistributionVisualizer,
                PlotConfig,
            )
            visualizer = DistributionVisualizer(
                output_directory=output_directory,
                config=PlotConfig(**plot_config) if plot_config else PlotConfig()
            )

            # Extract input DataFrames
            input_dataframes = extract_dataframes(args, kwargs)

            if not input_dataframes:
                logger.warning(f"No DataFrames found in arguments for {func.__name__}")
                return func(*args, **kwargs)

            # Generate filename prefix if not provided
            operation_prefix = filename_prefix or func.__name__

            # Store distribution metadata for lineage
            distribution_metadata = {
                "distribution_analysis": True,
                "analyzed_variables": variables,
                "sample_size": sample_size,
                "outlier_methods": [m.value for m in processed_outlier_methods],
                "analysis_timestamp": time.time()
            }

            before_stats = {}
            plot_results = []

            # Capture before distributions if requested
            if include_before_after and input_dataframes:
                try:
                    # Use the first DataFrame for analysis
                    input_df = list(input_dataframes.values())[0]

                    logger.info(f"Capturing before distributions for {func.__name__}")

                    # Analyze distributions for each outlier method
                    for outlier_method in processed_outlier_methods:
                        before_stats[outlier_method.value] = analyzer.analyze_multiple_variables(
                            input_df, variables, sample_size=sample_size, outlier_method=outlier_method
                        )

                    # Generate before plots
                    for variable in variables:
                        try:
                            print(f"    Creating BEFORE plots for variable: {variable}")
                            plots = visualizer.create_distribution_plot(
                                input_df, variable,
                                title=f"{variable.title()} Distribution - Before {func.__name__.title()}",
                                sample_size=sample_size,
                                include_outlier_removal=len(processed_outlier_methods) > 1,
                                outlier_method=processed_outlier_methods[0] if processed_outlier_methods else OutlierMethod.NONE,
                                filename_prefix=f"{operation_prefix}_before"
                            )
                            plot_results.extend(plots)
                            for plot in plots:
                                print(f"      Plot saved: {plot.file_path}")
                        except Exception as e:
                            logger.error(f"Failed to create before plot for {variable}: {e}")

                except Exception as e:
                    logger.error(f"Failed to capture before distributions: {e}")

            # Execute the original function
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # Capture after distributions
            try:
                if is_dataframe(result):
                    output_df = result

                    logger.info(f"Capturing after distributions for {func.__name__}")

                    # Analyze distributions for each outlier method
                    after_stats = {}
                    for outlier_method in processed_outlier_methods:
                        after_stats[outlier_method.value] = analyzer.analyze_multiple_variables(
                            output_df, variables, sample_size=sample_size, outlier_method=outlier_method
                        )

                    # Generate after plots
                    for variable in variables:
                        try:
                            print(f"    Creating AFTER plots for variable: {variable}")
                            plots = visualizer.create_distribution_plot(
                                output_df, variable,
                                title=f"{variable.title()} Distribution - After {func.__name__.title()}",
                                sample_size=sample_size,
                                include_outlier_removal=len(processed_outlier_methods) > 1,
                                outlier_method=processed_outlier_methods[0] if processed_outlier_methods else OutlierMethod.NONE,
                                filename_prefix=f"{operation_prefix}_after"
                            )
                            plot_results.extend(plots)
                            for plot in plots:
                                print(f"      Plot saved: {plot.file_path}")
                        except Exception as e:
                            logger.error(f"Failed to create after plot for {variable}: {e}")

                    # Generate comparison plots if we have before data
                    if include_before_after and before_stats and input_dataframes:
                        input_df = list(input_dataframes.values())[0]

                        for variable in variables:
                            try:
                                for outlier_method in processed_outlier_methods:
                                    comparison_plot = visualizer.create_comparison_plot(
                                        input_df, output_df, variable,
                                        operation_name=func.__name__.replace('_', ' ').title(),
                                        sample_size=sample_size,
                                        outlier_method=outlier_method,
                                        filename_prefix=f"{operation_prefix}_{outlier_method.value}"
                                    )
                                    plot_results.append(comparison_plot)
                            except Exception as e:
                                logger.error(f"Failed to create comparison plot for {variable}: {e}")

                    # Generate summary statistics if requested
                    if include_summary_stats and after_stats:
                        try:
                            for method_name, stats_dict in after_stats.items():
                                summary_file = visualizer.generate_summary_statistics_table(
                                    stats_dict,
                                    filename=f"{operation_prefix}_summary_{method_name}"
                                )
                                logger.info(f"Summary statistics saved: {summary_file}")
                        except Exception as e:
                            logger.error(f"Failed to generate summary statistics: {e}")

                    # Capture parent operation ID for visualization linking
                    parent_operation_id = None
                    if hasattr(output_df, '_lineage_id'):
                        parent_operation_id = output_df._lineage_id
                    elif hasattr(output_df, 'lineage_id'):
                        parent_operation_id = output_df.lineage_id

                    # Store metadata in global context for report generation
                    distribution_metadata.update({
                        "execution_time": execution_time,
                        "plot_results": [plot.file_path for plot in plot_results],
                        "plot_objects": [{"file_path": plot.file_path, "variable_name": plot.variable_name,
                                        "plot_type": plot.plot_type, "statistics": plot.statistics.__dict__ if plot.statistics else None}
                                       for plot in plot_results],
                        "before_stats": before_stats,
                        "after_stats": after_stats,
                        "variables_analyzed": variables,
                        "parent_operation_id": parent_operation_id
                    })

                    # Add to global tracker if available
                    try:
                        tracker = get_global_tracker()
                        # Initialize the attribute if it doesn't exist
                        if not hasattr(tracker, '_distribution_analyses'):
                            tracker._distribution_analyses = []

                        analysis_data = {
                            'function_name': func.__name__,
                            'metadata': distribution_metadata,
                            'timestamp': time.time()
                        }

                        tracker._distribution_analyses.append(analysis_data)
                        print(f"    Stored distribution analysis for {func.__name__}: {len(tracker._distribution_analyses)} total analyses")
                        logger.info(f"Stored distribution analysis for {func.__name__}: {len(tracker._distribution_analyses)} total analyses")

                    except Exception as e:
                        logger.error(f"Could not store distribution analysis in global tracker: {e}")
                        import traceback
                        traceback.print_exc()

                else:
                    logger.warning(f"Function {func.__name__} did not return a DataFrame, skipping after analysis")

            except Exception as e:
                logger.error(f"Failed to capture after distributions: {e}")

            return result

        return wrapper
    return decorator


def distributionCheckpoint(
    checkpoint_name: str,
    variables: List[str],
    sample_size: Optional[int] = 10000,
    outlier_methods: List[Union[str, OutlierMethod]] = ["none", "iqr"],
    output_directory: str = "assets"
):
    """
    Context manager for capturing distribution checkpoints during processing.

    This allows for capturing distributions at specific points within a function
    without requiring decoration of the entire function.

    Args:
        checkpoint_name: Name for this checkpoint
        variables: Variables to analyze
        sample_size: Sample size for analysis
        outlier_methods: Outlier removal methods
        output_directory: Directory to save plots and analysis. Can be absolute or relative path.
                         For integration with markdown reports, use an absolute path or a path
                         relative to where your markdown report will be saved.
                         Example: If your markdown is at "outputs/report.md", use "outputs/assets"
                         Default: "assets" (relative to current working directory)

    Examples:
        >>> # Basic usage with default output directory
        >>> def complex_processing(df):
        ...     with distributionCheckpoint("After Filtering", ["salary", "age"]):
        ...         filtered_df = df.filter(col("status") == "active")
        ...         # checkpoint.capture() is called automatically on context exit
        ...     return filtered_df

        >>> # With explicit output directory for proper markdown integration
        >>> output_dir = Path("outputs/examples/my_analysis")
        >>> def complex_processing(df):
        ...     with distributionCheckpoint(
        ...         "After Filtering",
        ...         ["salary", "age"],
        ...         output_directory=str(output_dir / "assets")
        ...     ) as checkpoint:
        ...         filtered_df = df.filter(col("status") == "active")
        ...         checkpoint.capture(filtered_df, "Active_Employees")
        ...     return filtered_df
    """
    class DistributionCheckpointContext:
        def __init__(self):
            self.analyzer = DistributionAnalyzer(default_sample_size=sample_size)
            # Lazy import to avoid circular dependency
            from ..visualization.distribution_visualizer import DistributionVisualizer
            self.visualizer = DistributionVisualizer(output_directory=output_directory)
            self.checkpoints = []
            self.captured_lineage_ref = None  # Track the lineage ID of captured DataFrame

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # Process any captured checkpoints
            logger.info(f"Distribution checkpoint '{checkpoint_name}' completed with {len(self.checkpoints)} captures")

            # Store metadata in global tracker for report generation
            if self.checkpoints:
                try:
                    import time

                    from ..core.lineage_tracker import get_global_tracker

                    tracker = get_global_tracker()

                    # Initialize the attribute if it doesn't exist
                    if not hasattr(tracker, '_distribution_analyses'):
                        tracker._distribution_analyses = []

                    # Create metadata for this checkpoint
                    analysis_data = {
                        'function_name': f'checkpoint_{checkpoint_name}',
                        'result_dataframe_lineage_ref': self.captured_lineage_ref,  # Link to the operation
                        'metadata': {
                            'checkpoint_name': checkpoint_name,
                            'variables_analyzed': variables,
                            'sample_size': sample_size,
                            'outlier_methods': [m.value if isinstance(m, OutlierMethod) else m for m in outlier_methods],
                            'plot_results': [plot.file_path for plot in self.checkpoints],
                            'plot_objects': [{
                                'file_path': plot.file_path,
                                'variable_name': plot.variable_name,
                                'plot_type': plot.plot_type,
                                'statistics': plot.statistics.__dict__ if plot.statistics else None
                            } for plot in self.checkpoints]
                        },
                        'timestamp': time.time()
                    }

                    tracker._distribution_analyses.append(analysis_data)
                    logger.info(f"Stored distribution checkpoint analysis: {len(tracker._distribution_analyses)} total analyses")

                except Exception as e:
                    logger.error(f"Could not store distribution checkpoint in global tracker: {e}")
                    import traceback
                    traceback.print_exc()

        def capture(self, df, label: str = ""):
            """Capture distribution at this point."""
            if not is_dataframe(df):
                logger.warning(f"Expected DataFrame for checkpoint capture, got {type(df)}")
                return

            try:
                # Capture the lineage ID of the DataFrame being analyzed
                # This allows the distribution analysis to be linked to the operation that created this DataFrame
                if hasattr(df, '_lineage_id'):
                    self.captured_lineage_ref = df._lineage_id.id
                    logger.debug(f"Captured lineage ID from _lineage_id: {self.captured_lineage_ref}")
                elif hasattr(df, 'lineage_id'):
                    self.captured_lineage_ref = df.lineage_id
                    logger.debug(f"Captured lineage ID from lineage_id: {self.captured_lineage_ref}")
                else:
                    # Try to get lineage from the current execution context
                    try:
                        from ..core.execution_context import get_current_context
                        context = get_current_context()
                        if context:
                            # Use the context_id - the output lineage will be resolved when the function returns
                            # Store the context_id so we can resolve it later
                            self.captured_lineage_ref = context.context_id
                            logger.debug(f"Captured context ID for later resolution: {self.captured_lineage_ref}")
                        else:
                            logger.warning(f"DataFrame has no lineage_id attribute and no context available, distribution node will not be attached")
                    except Exception as e:
                        logger.warning(f"Could not get lineage from execution context: {e}")

                checkpoint_label = f"{checkpoint_name}_{label}" if label else checkpoint_name

                # Process each outlier method
                for outlier_method in outlier_methods:
                    if isinstance(outlier_method, str):
                        outlier_method = OutlierMethod(outlier_method.lower())

                    # Generate plots for this checkpoint
                    for variable in variables:
                        plots = self.visualizer.create_distribution_plot(
                            df, variable,
                            title=f"{variable.title()} - {checkpoint_label}",
                            sample_size=sample_size,
                            include_outlier_removal=False,  # Single method per capture
                            outlier_method=outlier_method,
                            filename_prefix=f"checkpoint_{checkpoint_label}_{outlier_method.value}"
                        )
                        self.checkpoints.extend(plots)

                logger.info(f"Captured distributions for {len(variables)} variables at checkpoint '{checkpoint_label}'")

            except Exception as e:
                logger.error(f"Failed to capture checkpoint '{checkpoint_label}': {e}")

    return DistributionCheckpointContext()


class DistributionAnalysisContext:
    """
    Context manager for inline distribution analysis.

    Captures before/after distributions for transformations within the context block.
    """

    def __init__(self, variables: List[str], sample_size: Optional[int],
                 outlier_methods: List[OutlierMethod], output_directory: str,
                 include_before_after: bool, include_summary_stats: bool,
                 plot_config: Optional[Dict[str, Any]], filename_prefix: Optional[str]):
        self.variables = variables
        self.sample_size = sample_size
        self.outlier_methods = outlier_methods
        self.output_directory = output_directory
        self.include_before_after = include_before_after
        self.include_summary_stats = include_summary_stats
        self.plot_config = plot_config
        self.filename_prefix = filename_prefix or "distribution_analysis"

        self.analyzer = None
        self.visualizer = None
        self.input_df = None
        self.output_df = None
        self.before_stats = {}
        self.plot_results = []

    def __enter__(self):
        """Initialize the distribution analysis context."""
        self.analyzer = DistributionAnalyzer(default_sample_size=self.sample_size)

        # Lazy import to avoid circular dependency
        from ..visualization.distribution_visualizer import (
            DistributionVisualizer,
            PlotConfig,
        )
        self.visualizer = DistributionVisualizer(
            output_directory=self.output_directory,
            config=PlotConfig(**self.plot_config) if self.plot_config else PlotConfig()
        )

        logger.info(f"Started distribution analysis context for variables: {self.variables}")
        return self

    def set_input(self, df):
        """Set the input DataFrame for before analysis."""
        if not is_dataframe(df):
            logger.warning(f"Expected DataFrame for input, got {type(df)}")
            return

        self.input_df = df

        # Capture before distributions if requested
        if self.include_before_after:
            try:
                logger.info("Capturing before distributions")

                # Analyze distributions for each outlier method
                for outlier_method in self.outlier_methods:
                    self.before_stats[outlier_method.value] = self.analyzer.analyze_multiple_variables(
                        df, self.variables, sample_size=self.sample_size, outlier_method=outlier_method
                    )

                # Generate before plots
                for variable in self.variables:
                    try:
                        print(f"    Creating BEFORE plots for variable: {variable}")
                        plots = self.visualizer.create_distribution_plot(
                            df, variable,
                            title=f"{variable.title()} Distribution - Before Analysis",
                            sample_size=self.sample_size,
                            include_outlier_removal=len(self.outlier_methods) > 1,
                            outlier_method=self.outlier_methods[0] if self.outlier_methods else OutlierMethod.NONE,
                            filename_prefix=f"{self.filename_prefix}_before"
                        )
                        self.plot_results.extend(plots)
                        for plot in plots:
                            print(f"      Plot saved: {plot.file_path}")
                    except Exception as e:
                        logger.error(f"Failed to create before plot for {variable}: {e}")

            except Exception as e:
                logger.error(f"Failed to capture before distributions: {e}")

    def set_output(self, df):
        """Set the output DataFrame for after analysis."""
        if not is_dataframe(df):
            logger.warning(f"Expected DataFrame for output, got {type(df)}")
            return

        self.output_df = df

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Generate after distributions and comparison plots."""
        if self.output_df is None:
            logger.warning("No output DataFrame was set, skipping after analysis")
            return

        try:
            logger.info("Capturing after distributions")

            # Analyze distributions for each outlier method
            after_stats = {}
            for outlier_method in self.outlier_methods:
                after_stats[outlier_method.value] = self.analyzer.analyze_multiple_variables(
                    self.output_df, self.variables, sample_size=self.sample_size, outlier_method=outlier_method
                )

            # Generate after plots
            for variable in self.variables:
                try:
                    print(f"    Creating AFTER plots for variable: {variable}")
                    plots = self.visualizer.create_distribution_plot(
                        self.output_df, variable,
                        title=f"{variable.title()} Distribution - After Analysis",
                        sample_size=self.sample_size,
                        include_outlier_removal=len(self.outlier_methods) > 1,
                        outlier_method=self.outlier_methods[0] if self.outlier_methods else OutlierMethod.NONE,
                        filename_prefix=f"{self.filename_prefix}_after"
                    )
                    self.plot_results.extend(plots)
                    for plot in plots:
                        print(f"      Plot saved: {plot.file_path}")
                except Exception as e:
                    logger.error(f"Failed to create after plot for {variable}: {e}")

            # Generate comparison plots if we have before data
            if self.include_before_after and self.before_stats and self.input_df is not None:
                for variable in self.variables:
                    try:
                        for outlier_method in self.outlier_methods:
                            comparison_plot = self.visualizer.create_comparison_plot(
                                self.input_df, self.output_df, variable,
                                operation_name="Analysis",
                                sample_size=self.sample_size,
                                outlier_method=outlier_method,
                                filename_prefix=f"{self.filename_prefix}_{outlier_method.value}"
                            )
                            self.plot_results.append(comparison_plot)
                    except Exception as e:
                        logger.error(f"Failed to create comparison plot for {variable}: {e}")

            # Generate summary statistics if requested
            if self.include_summary_stats and after_stats:
                try:
                    for method_name, stats_dict in after_stats.items():
                        summary_file = self.visualizer.generate_summary_statistics_table(
                            stats_dict,
                            filename=f"{self.filename_prefix}_summary_{method_name}"
                        )
                        logger.info(f"Summary statistics saved: {summary_file}")
                except Exception as e:
                    logger.error(f"Failed to generate summary statistics: {e}")

            # Store metadata in global context for report generation
            distribution_metadata = {
                "distribution_analysis": True,
                "analyzed_variables": self.variables,
                "sample_size": self.sample_size,
                "outlier_methods": [m.value for m in self.outlier_methods],
                "analysis_timestamp": time.time(),
                "plot_results": [plot.file_path for plot in self.plot_results],
                "plot_objects": [{"file_path": plot.file_path, "variable_name": plot.variable_name,
                                "plot_type": plot.plot_type, "statistics": plot.statistics.__dict__ if plot.statistics else None}
                               for plot in self.plot_results],
                "before_stats": self.before_stats,
                "after_stats": after_stats,
                "variables_analyzed": self.variables,
            }

            # Add to global tracker if available
            try:
                tracker = get_global_tracker()

                # Initialize the attribute if it doesn't exist
                if not hasattr(tracker, '_distribution_analyses'):
                    tracker._distribution_analyses = []

                analysis_data = {
                    'function_name': 'context_manager_analysis',
                    'metadata': distribution_metadata,
                    'timestamp': time.time()
                }

                tracker._distribution_analyses.append(analysis_data)
                logger.info(f"Stored distribution analysis: {len(tracker._distribution_analyses)} total analyses")

            except Exception as e:
                logger.error(f"Could not store distribution analysis in global tracker: {e}")
                import traceback
                traceback.print_exc()

            logger.info("Distribution analysis context completed")

        except Exception as e:
            logger.error(f"Failed to complete distribution analysis: {e}")
            import traceback
            traceback.print_exc()


def distribution_analysis_context(
    variables: List[str],
    sample_size: Optional[int] = 10000,
    outlier_methods: List[Union[str, OutlierMethod]] = ["none", "iqr"],
    output_directory: str = "assets",
    include_before_after: bool = True,
    include_summary_stats: bool = True,
    plot_config: Optional[Dict[str, Any]] = None,
    filename_prefix: Optional[str] = None
) -> DistributionAnalysisContext:
    """
    Context manager for inline distribution analysis.

    This provides the same analysis as the @distributionAnalysis decorator but
    allows for inline usage without decorating a function.

    Args:
        variables: List of variable names to analyze
        sample_size: Sample size for analysis (None = no sampling)
        outlier_methods: List of outlier removal methods to apply
        output_directory: Directory to save plots and analysis. Can be absolute or relative path.
                         For integration with markdown reports, use an absolute path or a path
                         relative to where your markdown report will be saved.
                         Example: If your markdown is at "outputs/report.md", use "outputs/assets"
                         Default: "assets" (relative to current working directory)
        include_before_after: Whether to create before/after comparison plots
        include_summary_stats: Whether to generate summary statistics
        plot_config: Custom plot configuration
        filename_prefix: Prefix for generated filenames

    Returns:
        Context manager for distribution analysis

    Examples:
        >>> # Basic usage with default output directory
        >>> with distribution_analysis_context(
        ...     variables=["salary"],
        ...     outlier_methods=["iqr"]
        ... ) as ctx:
        ...     ctx.set_input(employees)
        ...     filtered = employees.filter(col("department") != "Executive")
        ...     ctx.set_output(filtered)

        >>> # With explicit output directory for proper markdown integration
        >>> output_dir = Path("outputs/examples/my_analysis")
        >>> with distribution_analysis_context(
        ...     variables=["salary"],
        ...     outlier_methods=["iqr"],
        ...     output_directory=str(output_dir / "assets")
        ... ) as ctx:
        ...     ctx.set_input(employees)
        ...     filtered = employees.filter(col("department") != "Executive")
        ...     ctx.set_output(filtered)
    """
    # Validate parameters
    if not variables:
        raise ValueError("At least one variable must be specified for analysis")

    # Convert string outlier methods to enums
    processed_outlier_methods = []
    for method in outlier_methods:
        if isinstance(method, str):
            try:
                processed_outlier_methods.append(OutlierMethod(method.lower()))
            except ValueError:
                logger.warning(f"Unknown outlier method '{method}', skipping")
        else:
            processed_outlier_methods.append(method)

    return DistributionAnalysisContext(
        variables=variables,
        sample_size=sample_size,
        outlier_methods=processed_outlier_methods,
        output_directory=output_directory,
        include_before_after=include_before_after,
        include_summary_stats=include_summary_stats,
        plot_config=plot_config,
        filename_prefix=filename_prefix
    )