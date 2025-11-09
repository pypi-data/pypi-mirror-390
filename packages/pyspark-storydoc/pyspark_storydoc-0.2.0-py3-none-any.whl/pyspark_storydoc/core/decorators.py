"""Enhanced decorators with immutable lineage tracking, fork support, and automatic hierarchy."""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from pyspark.storagelevel import StorageLevel

from ..utils.dataframe_utils import (
    extract_dataframes,
    extract_dataframes_with_keys,
    is_dataframe,
)
from ..utils.exceptions import LineageTrackingError, ValidationError
from ..utils.validation import (
    validate_business_concept_name,
    validate_description,
    validate_function_for_decoration,
    validate_materialize_setting,
    validate_track_columns,
)
from .execution_context import ExecutionContext, get_context_manager
from .fork_detector import ForkStatus, get_fork_detector
from .graph_builder import BusinessConceptNode, MetricsData

# Import hierarchy support functions
from .hierarchy_context import (
    _build_concept_path,
    _get_parent_concept,
    _pop_concept_from_hierarchy,
    _push_concept_to_hierarchy,
)
from .lineage_dataframe import LineageDataFrame
from .lineage_id import LineageID
from .lineage_tracker import get_global_tracker

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


def businessConcept(
    name: str,
    description: Optional[str] = None,
    materialize: bool = True,
    materialize_line_level_functions: bool = True,
    track_columns: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    auto_cache: bool = False,
    cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
    cache_threshold: int = 2,
    hierarchical: bool = True,
    governance: Optional[Union[Dict[str, Any], Any]] = None,
) -> Callable[[F], F]:
    """
    Enhanced business concept decorator with automatic hierarchy support.

    This decorator creates an execution context for each function call, enabling
    proper fork detection and handling when the same DataFrame is used by multiple
    operations. It uses immutable LineageIDs to track relationships correctly.

    By default (hierarchical=True), this decorator automatically detects and tracks
    parent-child relationships when concepts are nested, creating a hierarchical
    business concept structure.

    Args:
        name: Business-friendly name for this operation
        description: Detailed explanation for stakeholders
        materialize: Whether to compute row counts and metrics. When True, automatically
            caches input and output DataFrames to prevent redundant computation during
            metrics capture. Without caching, each count() triggers a full recomputation.
        materialize_line_level_functions: Whether to materialize metrics for individual
            operations within this concept
        track_columns: Specific columns to monitor for distinct counts
        metadata: Additional context information
        auto_cache: (DEPRECATED - caching is now automatic with materialize=True)
            Enable automatic caching after repeated materializations
        cache_storage_level: Storage level for automatic caching (default: MEMORY_AND_DISK)
        cache_threshold: (DEPRECATED - not used with automatic caching)
            Number of materializations before auto-caching kicks in
        hierarchical: Enable automatic hierarchy tracking (default: True)
            When True, nested @businessConcept decorators automatically form parent-child
            relationships with full path tracking (e.g., "Parent > Child > Grandchild").
            When False, concepts remain independent (legacy flat behavior).
        governance: Optional governance metadata for this operation. Can be:
            - A dict created by create_governance_dict() or create_quick_governance()
            - A GovernanceMetadata object
            - None (no governance tracking)
            Governance metadata includes business justification, risks, customer impact,
            PII handling, and compliance requirements.

    Returns:
        Decorated function that tracks business lineage with fork support

    Raises:
        ValidationError: If parameters are invalid
        LineageTrackingError: If tracking fails during execution

    Examples:
        # Automatic hierarchy (default):
        @businessConcept("Data Pipeline")
        def pipeline(df):
            @businessConcept("Stage 1")  # Auto-detected as child
            def stage1(df):
                return df.filter(...)

            @businessConcept("Stage 2")  # Auto-detected as child
            def stage2(df):
                return df.withColumn(...)

            return stage2(stage1(df))

        # Independent concepts (legacy flat mode):
        @businessConcept("Independent Task", hierarchical=False)
        def task(df):
            return df.filter(...)

        # With governance metadata:
        from pyspark_storydoc.governance import create_quick_governance

        @businessConcept(
            "Calculate Premium",
            description="Calculate insurance premium based on risk factors",
            governance=create_quick_governance(
                why="Required for automated underwriting",
                risks=["Potential algorithmic bias"],
                mitigations=["Quarterly fairness audits"],
                impacts_customers=True,
                impacting_columns=["premium"]
            )
        )
        def calculate_premium(df):
            return df.withColumn("premium", ...)
    """
    # Validate decorator parameters
    validate_business_concept_name(name)
    validate_description(description)
    validate_materialize_setting(materialize)
    if track_columns is not None:
        validate_track_columns(track_columns)

    def decorator(func: F) -> F:
        # Validate the function can be decorated
        validate_function_for_decoration(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if tracking is enabled
            tracker = get_global_tracker()
            if not tracker or not tracker.should_track():
                # Zero-overhead mode - just execute the function
                return func(*args, **kwargs)

            # Determine execution mode based on hierarchical parameter
            if hierarchical:
                # Hierarchical mode: check for parent and track relationships
                return _execute_with_hierarchy(
                    func, args, kwargs, name, description,
                    materialize, materialize_line_level_functions,
                    track_columns, metadata, auto_cache,
                    cache_storage_level, cache_threshold, governance
                )
            else:
                # Legacy flat mode: independent concepts
                context_manager = get_context_manager()

                with context_manager.context(
                    function_name=name,
                    materialization_enabled=materialize
                ) as context:
                    try:
                        return _execute_business_concept(
                            func, args, kwargs, context, name, description,
                            materialize, materialize_line_level_functions,
                            track_columns, metadata, auto_cache,
                            cache_storage_level, cache_threshold, governance
                        )
                    except Exception as e:
                        logger.error(f"Error in business concept '{name}': {e}")
                        if isinstance(e, LineageTrackingError):
                            raise
                        # For other errors, still execute the function but log the tracking failure
                        logger.warning(f"Executing '{name}' without lineage tracking due to error: {e}")
                        return func(*args, **kwargs)

        # Add metadata to the wrapper for introspection
        wrapper._business_concept_meta = {
            'name': name,
            'description': description,
            'materialize': materialize,
            'materialize_line_level_functions': materialize_line_level_functions,
            'track_columns': track_columns or [],
            'metadata': metadata or {},
            'hierarchical': hierarchical,
            'governance': governance,
            'original_function': func,
        }

        # Mark as business concept
        wrapper._is_business_concept = True

        return wrapper

    return decorator


def _execute_with_hierarchy(
    func: Callable,
    args: tuple,
    kwargs: dict,
    name: str,
    description: Optional[str],
    materialize: bool,
    materialize_line_level_functions: bool,
    track_columns: Optional[List[str]],
    metadata: Optional[Dict[str, Any]],
    auto_cache: bool,
    cache_storage_level: StorageLevel,
    cache_threshold: int,
    governance: Optional[Union[Dict[str, Any], Any]] = None
) -> Any:
    """
    Execute business concept with automatic hierarchy detection and tracking.

    This function checks for parent concepts on the hierarchy stack and automatically
    creates parent-child relationships, tracking the full concept path.
    """
    # Get parent concept from hierarchy stack
    parent_concept = _get_parent_concept()
    parent_name = parent_concept['name'] if parent_concept else None
    parent_context_id = parent_concept['context_id'] if parent_concept else None

    # Build concept path
    concept_path = _build_concept_path()
    full_path = f"{concept_path} > {name}" if concept_path else name

    # Create execution context
    context_manager = get_context_manager()

    with context_manager.context(
        function_name=name,
        materialization_enabled=materialize
    ) as context:
        # Create concept info for hierarchy
        concept_info = {
            'name': name,
            'description': description,
            'context_id': context.context_id,
            'parent_concept_name': parent_name,
            'parent_context_id': parent_context_id,
            'concept_path': full_path,
            'materialize': materialize,
            'track_columns': track_columns or [],
            'metadata': metadata or {},
        }

        # Push to hierarchy stack
        _push_concept_to_hierarchy(concept_info)

        try:
            # Add hierarchy metadata to the metadata dict
            hierarchy_metadata = {
                **(metadata or {}),
                'hierarchy': {
                    'parent_concept_name': parent_name,
                    'parent_context_id': parent_context_id,
                    'concept_path': full_path,
                    'depth': len(_get_parent_concept() or []) if parent_concept else 0,
                    'is_root': parent_name is None,
                }
            }

            # Execute with existing business concept logic but with hierarchy metadata
            result = _execute_business_concept(
                func, args, kwargs, context, name, description,
                materialize, materialize_line_level_functions,
                track_columns, hierarchy_metadata, auto_cache,
                cache_storage_level, cache_threshold, governance
            )

            logger.info(f"Completed hierarchical concept '{full_path}'")
            return result

        except Exception as e:
            logger.error(f"Error in hierarchical business concept '{full_path}': {e}")
            if isinstance(e, LineageTrackingError):
                raise
            # For other errors, still execute the function but log the tracking failure
            logger.warning(f"Executing '{name}' without lineage tracking due to error: {e}")
            return func(*args, **kwargs)

        finally:
            # Always pop from hierarchy stack
            _pop_concept_from_hierarchy()


def _execute_business_concept(
    func: Callable,
    args: tuple,
    kwargs: dict,
    context: ExecutionContext,
    name: str,
    description: Optional[str],
    materialize: bool,
    materialize_line_level_functions: bool,
    track_columns: Optional[List[str]],
    metadata: Optional[Dict[str, Any]],
    auto_cache: bool,
    cache_storage_level: StorageLevel,
    cache_threshold: int,
    governance: Optional[Union[Dict[str, Any], Any]] = None
) -> Any:
    """Execute business concept with full lineage tracking and fork detection."""

    # Extract input DataFrames and their lineage information
    input_dataframes = extract_dataframes_with_keys(args, kwargs)
    input_lineage_info = {}
    fork_detector = get_fork_detector()

    # Process input DataFrames and detect forks
    for key, df in input_dataframes.items():
        if isinstance(df, LineageDataFrame):
            lineage_id = df.lineage_id
            context.add_input_lineage(key, lineage_id)
            input_lineage_info[key] = lineage_id

            # Register consumption and detect forks
            fork_status = fork_detector.register_consumer(
                lineage_id.id,
                context.context_id,
                name
            )

            if fork_status == ForkStatus.FORK_DETECTED:
                logger.info(f"Fork detected in '{name}': LineageID {lineage_id.id} consumed by multiple operations")

    # Create business concept node
    concept_node = BusinessConceptNode(
        node_id=context.context_id,
        name=name,
        description=description,
        function_name=func.__name__,
        materialize=materialize,
        track_columns=track_columns or [],
        metadata=metadata or {},
        governance_metadata=governance,
    )

    # CRITICAL FIX: Register business concept BEFORE function execution
    # so that DataFrame operations can find it and associate themselves with it
    tracker = get_global_tracker()
    if tracker:
        tracker.register_business_concept(concept_node)
        logger.debug(f"Pre-registered business concept '{name}' with context {context.context_id}")

    # Capture input metrics if materialization is enabled
    # CRITICAL: Cache input DataFrames before metrics capture to avoid redundant computation
    cached_inputs = {}
    if materialize and input_dataframes:
        # Cache each input DataFrame before capturing metrics to prevent re-execution
        for key, df in input_dataframes.items():
            if isinstance(df, LineageDataFrame) and not df.is_cached:
                logger.debug(f"Auto-caching input DataFrame '{key}' before materialization")
                cached_inputs[key] = df.cache(storage_level=cache_storage_level)
            else:
                cached_inputs[key] = df

        concept_node.input_metrics = _capture_input_metrics(
            cached_inputs, track_columns, materialize
        )

    # Auto-wrap DataFrame arguments if needed
    wrapped_args, wrapped_kwargs, restore_settings = _auto_wrap_dataframes(
        args, kwargs, track_columns, materialize, materialize_line_level_functions,
        auto_cache, cache_storage_level, cache_threshold, context
    )

    try:
        # Execute the actual business function
        execution_start = time.time()
        result = func(*wrapped_args, **wrapped_kwargs)
        execution_time = time.time() - execution_start
    finally:
        # Always restore original settings, even if execution fails
        restore_settings()

    concept_node.execution_time = execution_time

    # Process result and capture output metrics
    if is_dataframe(result):
        if isinstance(result, LineageDataFrame):
            context.add_output_lineage(result.lineage_id)

            # Register the result production
            fork_detector.register_producer(result.lineage_id.id, context.context_id)

            # Capture output metrics if enabled
            # CRITICAL: Cache result before metrics capture to avoid redundant computation
            if materialize:
                # Cache the result DataFrame before capturing metrics
                if not result.is_cached:
                    logger.debug(f"Auto-caching output DataFrame before materialization")
                    result = result.cache(storage_level=cache_storage_level)

                output_metrics = _capture_output_metrics(result, track_columns)
                concept_node.output_metrics = output_metrics

    # Update enhanced graph with timing, metrics, and business concept details
    # Do this AFTER capturing both input and output metrics
    if tracker:
        tracker.update_node_metrics(
            node_id=context.context_id,
            timing=execution_time,
            operation_name=name,
            operation_description=description,
            input_metrics=concept_node.input_metrics if hasattr(concept_node, 'input_metrics') else None,
            metrics=concept_node.output_metrics if hasattr(concept_node, 'output_metrics') else None
        )

    # CRITICAL FIX: Handle merge operations (union/join)
    # If this business concept has multiple inputs and produces a single output,
    # replace individual technical operations with a single merge operation
    is_merge_op = len(input_dataframes) > 1 and is_dataframe(result)
    if is_merge_op:
        # Ensure the result DataFrame is registered first (if not already registered)
        # IMPORTANT: Check if already registered to avoid overwriting metadata
        if isinstance(result, LineageDataFrame) and tracker:
            enhanced_graph = tracker.get_lineage_graph()
            if result.lineage_id.id not in enhanced_graph.lineage_nodes:
                tracker.register_lineage_id(result.lineage_id)
                logger.debug(f"Registered lineage ID for merge result: {result.lineage_id.id}")
            else:
                logger.debug(f"Lineage ID already registered, skipping: {result.lineage_id.id}")

        _handle_merge_operation(concept_node, input_dataframes, result, context, tracker)

    # Store execution metadata
    concept_node.metadata.update({
        'function_signature': _get_function_signature(func, args, kwargs),
        'execution_time': execution_time,
        'context_id': context.context_id,
        'input_lineage_ids': [lid.id for lid in input_lineage_info.values()],
        'fork_points_detected': [
            lid.id for lid in input_lineage_info.values()
            if fork_detector.is_fork_point(lid.id)
        ]
    })

    # Business concept was already registered before execution
    # Update final execution metrics
    if tracker:
        # Update the already-registered concept node with final execution data
        enhanced_graph = tracker.get_lineage_graph()
        if context.context_id in enhanced_graph.nodes:
            registered_concept = enhanced_graph.nodes[context.context_id]
            registered_concept.execution_time = execution_time
            registered_concept.metadata.update(concept_node.metadata)

    logger.info(f"Executed business concept '{name}' in {execution_time:.3f}s")

    return result


def _capture_input_metrics(input_dataframes: Dict[str, Any],
                          track_columns: Optional[List[str]],
                          materialize: bool) -> Optional[MetricsData]:
    """Capture metrics from input DataFrames."""
    if not materialize or not input_dataframes:
        return None

    tracker = get_global_tracker()
    if not tracker or not tracker.should_materialize():
        return None

    # Use the first DataFrame for metrics
    first_df = next(iter(input_dataframes.values()))
    if isinstance(first_df, LineageDataFrame):
        # Force metrics capture even if the DataFrame itself has materialize=False
        # because the business concept has materialize=True
        from ..utils.dataframe_utils import safe_count, safe_distinct_count
        from .graph_builder import MetricsData

        try:
            row_count = safe_count(first_df._df)
            distinct_counts = {}

            # Use track_columns from business concept
            for col_name in (track_columns or []):
                if col_name in first_df._df.columns:
                    try:
                        distinct_counts[col_name] = safe_distinct_count(first_df._df, col_name)
                    except Exception:
                        pass

            return MetricsData(
                row_count=row_count,
                column_count=len(first_df._df.columns),
                distinct_counts=distinct_counts,
                estimated=False
            )
        except Exception as e:
            logger.warning(f"Failed to capture input metrics: {e}")
            return None
    else:
        # Handle regular DataFrames
        return tracker.capture_metrics([first_df], track_columns)


def _capture_output_metrics(result_df: LineageDataFrame,
                           track_columns: Optional[List[str]]) -> Optional[MetricsData]:
    """Capture metrics from output DataFrame."""
    # Force metrics capture even if the DataFrame itself has materialize=False
    import logging

    from ..utils.dataframe_utils import safe_count, safe_distinct_count
    from .graph_builder import MetricsData
    logger = logging.getLogger(__name__)

    try:
        row_count = safe_count(result_df._df)
        distinct_counts = {}

        # Use track_columns from business concept
        for col_name in (track_columns or []):
            if col_name in result_df._df.columns:
                try:
                    distinct_counts[col_name] = safe_distinct_count(result_df._df, col_name)
                except Exception:
                    pass

        return MetricsData(
            row_count=row_count,
            column_count=len(result_df._df.columns),
            distinct_counts=distinct_counts,
            estimated=False
        )
    except Exception as e:
        logger.warning(f"Failed to capture output metrics: {e}")
        return None


def _auto_wrap_dataframes(
    args: tuple,
    kwargs: dict,
    track_columns: Optional[List[str]] = None,
    materialize: bool = True,
    materialize_line_level_functions: bool = True,
    auto_cache: bool = False,
    cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
    cache_threshold: int = 2,
    context: ExecutionContext = None
) -> tuple:
    """
    Automatically wrap DataFrame arguments with immutable lineage tracking.

    This function ensures that all DataFrame inputs are properly wrapped
    as LineageDataFrames to enable fork detection and immutable
    lineage tracking.

    Returns:
        Tuple of (wrapped_args, wrapped_kwargs, restore_function)
        The restore_function should be called after execution to restore original settings.
    """
    # Check track_row_count_level from tracker to determine operation-level materialization
    tracker = get_global_tracker()
    should_materialize_operations = materialize_line_level_functions

    if tracker and hasattr(tracker, 'track_row_count_level'):
        # If track_row_count_level is "business_concept", don't materialize operations
        # If track_row_count_level is "operation", materialize operations
        if tracker.track_row_count_level == "business_concept":
            should_materialize_operations = False
        elif tracker.track_row_count_level == "operation":
            should_materialize_operations = True
        # If not set or other value, use materialize_line_level_functions parameter

    # Track original settings for restoration
    original_settings = []

    # Wrap positional arguments
    wrapped_args = []
    for i, arg in enumerate(args):
        if isinstance(arg, LineageDataFrame):
            # Save original settings
            original_settings.append({
                'dataframe': arg,
                'materialize': arg._materialize,
                'track_columns': arg._track_columns.copy() if arg._track_columns else []
            })
            # Override settings on existing LineageDataFrame with tracker settings
            arg._materialize = should_materialize_operations
            arg._track_columns = track_columns or []
            wrapped_args.append(arg)
        elif is_dataframe(arg):
            # Create wrapper for regular DataFrame
            wrapped_arg = LineageDataFrame(
                dataframe=arg,
                business_label=f"Auto-wrapped DataFrame (arg_{i})",
                materialize=should_materialize_operations,
                track_columns=track_columns
            )
            wrapped_args.append(wrapped_arg)
        else:
            wrapped_args.append(arg)

    # Wrap keyword arguments
    wrapped_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, LineageDataFrame):
            # Save original settings
            original_settings.append({
                'dataframe': value,
                'materialize': value._materialize,
                'track_columns': value._track_columns.copy() if value._track_columns else []
            })
            # Override settings on existing LineageDataFrame with tracker settings
            value._materialize = should_materialize_operations
            value._track_columns = track_columns or []
            wrapped_kwargs[key] = value
        elif is_dataframe(value):
            # Create wrapper for regular DataFrame
            wrapped_value = LineageDataFrame(
                dataframe=value,
                business_label=f"Auto-wrapped DataFrame ({key})",
                materialize=should_materialize_operations,
                track_columns=track_columns
            )
            wrapped_kwargs[key] = wrapped_value
        else:
            wrapped_kwargs[key] = value

    # Create restore function to reset settings after execution
    def restore_original_settings():
        """Restore original DataFrame settings after business concept execution."""
        for settings in original_settings:
            df = settings['dataframe']
            df._materialize = settings['materialize']
            df._track_columns = settings['track_columns']

    return tuple(wrapped_args), wrapped_kwargs, restore_original_settings


def _get_function_signature(func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
    """Get function signature information for debugging."""
    try:
        import inspect
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        return {
            'function_name': func.__name__,
            'module': func.__module__ if hasattr(func, '__module__') else None,
            'parameters': {
                name: (
                    f"<LineageDataFrame: {value.lineage_id.id}>"
                    if isinstance(value, LineageDataFrame)
                    else f"<DataFrame with {len(value.columns)} columns>"
                    if is_dataframe(value)
                    else str(value)[:100]  # Truncate long values
                )
                for name, value in bound_args.arguments.items()
            },
            'parameter_count': len(bound_args.arguments),
        }

    except Exception as e:
        logger.warning(f"Could not extract function signature for {func}: {e}")
        return {
            'function_name': getattr(func, '__name__', str(func)),
            'error': str(e),
            'arg_count': len(args),
            'kwarg_count': len(kwargs),
        }


def track_lineage(
    materialize: bool = True,
    track_columns: Optional[List[str]] = None,
    auto_wrap: bool = False,
    graph_name: Optional[str] = None,
) -> Callable[[F], F]:
    """
    Enhanced lineage tracking decorator with immutable lineage support.

    This decorator sets up the tracking context for an entire pipeline,
    establishing defaults for materialization and column tracking while
    supporting the new immutable lineage architecture.

    Args:
        materialize: Whether to compute row counts by default
        track_columns: Default columns to track for distinct counts
        auto_wrap: Automatically wrap DataFrames for inline tracking
        graph_name: Name for the lineage graph

    Returns:
        Decorated function with enhanced lineage tracking enabled
    """
    # Validate parameters
    validate_materialize_setting(materialize)
    if track_columns is not None:
        validate_track_columns(track_columns)

    def decorator(func: F) -> F:
        validate_function_for_decoration(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracker = get_global_tracker()
            if not tracker or not tracker.should_track():
                # Zero-overhead mode
                return func(*args, **kwargs)

            # Use pipeline name as graph name if not specified
            pipeline_name = graph_name or func.__name__

            context_manager = get_context_manager()

            # Check if already inside a business concept or other context
            existing_context = context_manager.get_current_context()

            # If already in a context (e.g., @businessConcept), don't create a new one
            if existing_context:
                logger.debug(f"@track_lineage skipping context creation - already in context {existing_context.context_id}")
                try:
                    logger.info(f"Starting lineage-tracked operation: {pipeline_name}")

                    execution_start = time.time()
                    result = func(*args, **kwargs)
                    execution_time = time.time() - execution_start

                    logger.info(f"Completed operation '{pipeline_name}' in {execution_time:.3f}s")

                    # Auto-wrap result if requested and it's a DataFrame
                    if auto_wrap and is_dataframe(result) and not isinstance(result, LineageDataFrame):
                        result = LineageDataFrame(
                            dataframe=result,
                            business_label=f"{pipeline_name} Output",
                            materialize=materialize,
                            track_columns=track_columns
                        )

                    return result

                except Exception as e:
                    logger.error(f"Error in lineage-tracked operation '{pipeline_name}': {e}")
                    raise

            # No existing context, create a new one
            with context_manager.context(
                function_name=pipeline_name,
                materialization_enabled=materialize
            ) as context:
                try:
                    logger.info(f"Starting lineage-tracked pipeline: {pipeline_name}")

                    execution_start = time.time()
                    result = func(*args, **kwargs)
                    execution_time = time.time() - execution_start

                    logger.info(f"Completed pipeline '{pipeline_name}' in {execution_time:.3f}s")

                    # Auto-wrap result if requested and it's a DataFrame
                    if auto_wrap and is_dataframe(result) and not isinstance(result, LineageDataFrame):
                        result = LineageDataFrame(
                            dataframe=result,
                            business_label=f"{pipeline_name} Output",
                            materialize=materialize,
                            track_columns=track_columns
                        )

                    return result

                except Exception as e:
                    logger.error(f"Error in lineage-tracked pipeline '{pipeline_name}': {e}")
                    raise

        # Add metadata
        wrapper._lineage_pipeline_meta = {
            'materialize': materialize,
            'track_columns': track_columns or [],
            'auto_wrap': auto_wrap,
            'graph_name': graph_name,
            'original_function': func,
        }

        wrapper._is_lineage_pipeline = True

        return wrapper

    return decorator


def _handle_merge_operation(concept_node: BusinessConceptNode,
                          input_dataframes: Dict[str, Any],
                          result: Any,
                          context: ExecutionContext,
                          tracker) -> None:
    """
    Handle merge operations (union/join) by replacing individual technical operations
    with a single merge operation node.
    """
    from .graph_builder import OperationNode, OperationType

    # Keep existing technical operations but add the merge operation as the primary one
    original_operations = concept_node.technical_operations.copy()

    # Determine merge operation type based on function name or input count
    merge_type = OperationType.UNION
    if "join" in concept_node.name.lower():
        merge_type = OperationType.JOIN
    elif "union" in concept_node.name.lower():
        merge_type = OperationType.UNION
    elif len(input_dataframes) == 2:
        merge_type = OperationType.UNION  # Default for 2 inputs
    else:
        merge_type = OperationType.CUSTOM  # For complex merge operations

    # Create a single merge operation node
    if isinstance(result, LineageDataFrame):
        merge_operation = OperationNode(
            node_id=result.lineage_id.operation_id,
            operation_type=merge_type,
            business_context=f"Merge: {concept_node.name}"
        )

        # Set operation name based on type
        if merge_type == OperationType.UNION:
            merge_operation.name = f"Union: {len(input_dataframes)} inputs"
        elif merge_type == OperationType.JOIN:
            merge_operation.name = f"Join: {len(input_dataframes)} inputs"
        else:
            merge_operation.name = f"Merge: {len(input_dataframes)} inputs"

        # Set up metadata including input lineage IDs
        input_lineage_ids = []
        for key, df in input_dataframes.items():
            if isinstance(df, LineageDataFrame):
                input_lineage_ids.append(df.lineage_id.id)

        merge_operation.metadata = {
            'operation_type': merge_type.value,
            'input_count': len(input_dataframes),
            'input_lineage_ids': input_lineage_ids,
            'merge_type': 'multi_input_merge',
            'original_operations_count': len(original_operations)
        }

        # Capture metrics if available
        if concept_node.input_metrics:
            merge_operation.before_metrics = concept_node.input_metrics
        if concept_node.output_metrics:
            merge_operation.after_metrics = concept_node.output_metrics

        # Add execution time from the concept
        merge_operation.execution_time = concept_node.execution_time

        # Add the merge operation alongside the existing operations
        concept_node.add_technical_operation(merge_operation)

        # CRITICAL FIX: The union operation naturally creates the correct parent relationships
        # We just need to ensure it's properly tracked and the merge operation reflects this
        if tracker and isinstance(result, LineageDataFrame):
            logger.info(f"Registering merge operation alongside existing operations")

            # The union operation already has the correct parent relationships
            # Just ensure the merge operation metadata reflects the actual lineage
            enhanced_graph = tracker.get_lineage_graph()
            if enhanced_graph:
                existing_parents = enhanced_graph.get_parents(result.lineage_id.id)
                logger.info(f"Result {result.lineage_id.id} has {len(existing_parents)} existing parents from union operation")

                # Update merge operation metadata to show the actual parents
                if existing_parents:
                    merge_operation.metadata['parent_lineage_ids'] = existing_parents

        logger.info(f"Created merge operation for '{concept_node.name}': {merge_operation.name}")
        logger.debug(f"Replaced {len(original_operations)} individual operations with 1 merge operation")


# Compatibility functions for existing code
def get_business_concept_info(func: Callable) -> Optional[Dict[str, Any]]:
    """Extract business concept metadata from a decorated function."""
    if hasattr(func, '_business_concept_meta'):
        return func._business_concept_meta.copy()
    return None


def is_business_concept(func: Callable) -> bool:
    """Check if a function is decorated as a business concept."""
    return hasattr(func, '_is_business_concept') and func._is_business_concept


def is_lineage_pipeline(func: Callable) -> bool:
    """Check if a function is decorated as a lineage pipeline."""
    return hasattr(func, '_is_lineage_pipeline') and func._is_lineage_pipeline