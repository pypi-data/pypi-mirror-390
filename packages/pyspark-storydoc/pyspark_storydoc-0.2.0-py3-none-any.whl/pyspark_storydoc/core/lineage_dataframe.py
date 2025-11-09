"""Enhanced DataFrame wrapper with immutable lineage tracking and fork support."""

import logging
import time
from functools import wraps
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from pyspark.sql import DataFrame
from pyspark.sql.types import StructType
from pyspark.storagelevel import StorageLevel

from ..utils.dataframe_utils import extract_column_names, safe_count
from ..utils.exceptions import LineageTrackingError, ValidationError
from ..utils.validation import validate_business_concept_name
from .execution_context import get_current_context, get_current_context_id
from .fork_detector import ForkStatus, get_fork_detector
from .graph_builder import MetricsData, OperationNode, OperationType
from .lineage_id import LineageID
from .lineage_tracker import get_global_tracker

if TYPE_CHECKING:
    from pyspark.sql import Column
    from pyspark.sql.functions import UserDefinedFunction

logger = logging.getLogger(__name__)


def _get_variable_name(obj, default="unknown"):
    """
    Try to get the variable name of an object from the calling context.

    This is best-effort and may not always work, but it's useful for
    creating human-readable labels for untracked DataFrames.

    Args:
        obj: The object to find the variable name for
        default: Default name if variable name cannot be determined

    Returns:
        Variable name as string, or default if not found
    """
    try:
        import inspect

        # Get the calling frame (2 levels up: helper -> join/union -> caller)
        frame = inspect.currentframe().f_back.f_back

        # Search local variables for the object
        for name, value in frame.f_locals.items():
            if value is obj:
                return name

        # If not found, return default
        return default
    except Exception:
        return default


class LineageDataFrame:
    """
    DataFrame wrapper with immutable lineage tracking and fork support.

    This class provides comprehensive lineage tracking with immutable lineage IDs
    and each transformation creates a new lineage point. This enables proper
    fork detection and handling when the same DataFrame is consumed by multiple
    operations.

    Features:
    - Uses immutable LineageID for robust tracking
    - Integrates with ExecutionContext for proper fork detection
    - Preserves PySpark lazy evaluation completely
    - Zero overhead when materialization is disabled
    - Compatible with all PySpark DataFrame operations
    """

    def __init__(self,
                 dataframe: DataFrame,
                 lineage_id: Optional[LineageID] = None,
                 business_label: Optional[str] = None,
                 materialize: bool = False,
                 track_columns: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 parent_lineages: Optional[List[LineageID]] = None):
        """
        Initialize LineageDataFrame wrapper.

        Args:
            dataframe: PySpark DataFrame to wrap
            lineage_id: Immutable LineageID for this DataFrame state
            business_label: Optional business-friendly label
            materialize: Whether to compute row counts and metrics
            track_columns: Specific columns to track for distinct counts
            metadata: Additional metadata
            parent_lineages: Parent LineageIDs when wrapping result of operations on LineageDataFrames
        """
        if not isinstance(dataframe, DataFrame):
            raise ValidationError("dataframe must be a PySpark DataFrame")

        self._df = dataframe
        self._materialize = materialize
        self._track_columns = track_columns or []
        self._metadata = metadata or {}
        self._business_label = business_label

        # Validate business label
        if business_label:
            validate_business_concept_name(business_label)

        # Create or use provided LineageID
        if lineage_id is None:
            context_id = get_current_context_id()

            # Check if this is wrapping a result from LineageDataFrame operations
            if parent_lineages:
                # Create as a transformation with parent lineages
                operation_type = metadata.get('operation_type', 'custom') if metadata else 'custom'
                parent_ids = [p.id for p in parent_lineages]

                self._lineage_id = LineageID.create_from_parents(
                    parents=parent_lineages,
                    operation_type=operation_type,
                    context_id=context_id
                )

                # Register as operation, not source
                self._register_as_operation(
                    operation_type=operation_type,
                    parent_lineages=parent_lineages
                )

                logger.info(
                    f"Created LineageDataFrame from operation '{operation_type}' "
                    f"with {len(parent_lineages)} parent(s): {parent_ids}"
                )
            else:
                # Attempt to auto-detect parent lineages from DataFrame metadata
                detected_parents = self._detect_parent_lineages(dataframe)

                if detected_parents:
                    # Found parent lineages - create as transformation
                    operation_type = metadata.get('operation_type', 'custom') if metadata else 'custom'
                    parent_ids = [p.id for p in detected_parents]

                    self._lineage_id = LineageID.create_from_parents(
                        parents=detected_parents,
                        operation_type=operation_type,
                        context_id=context_id
                    )

                    self._register_as_operation(
                        operation_type=operation_type,
                        parent_lineages=detected_parents
                    )

                    logger.warning(
                        f"Auto-detected parent lineages for LineageDataFrame. "
                        f"Consider using df.join() method instead of creating new LineageDataFrame. "
                        f"Parents: {parent_ids}"
                    )
                else:
                    # No parents detected - create as source
                    self._lineage_id = LineageID.create_source(
                        source_name=business_label or "dataframe",
                        context_id=context_id
                    )
                    self._register_as_source()

                    logger.debug(f"Created LineageDataFrame as source: {self._lineage_id.id}")
        else:
            # Validate that lineage_id is actually a LineageID object
            if not isinstance(lineage_id, LineageID):
                raise ValidationError(
                    f"lineage_id must be a LineageID object, got {type(lineage_id).__name__}. "
                    f"Did you mean to use business_label parameter instead?"
                )
            self._lineage_id = lineage_id

        logger.debug(f"Created LineageDataFrame with LineageID: {self._lineage_id.id}")

    @property
    def dataframe(self) -> DataFrame:
        """Get the underlying PySpark DataFrame."""
        return self._df

    @property
    def lineage_id(self) -> LineageID:
        """Get the immutable LineageID for this DataFrame."""
        return self._lineage_id

    @property
    def business_label(self) -> Optional[str]:
        """Get the business label for this DataFrame."""
        return self._business_label

    @property
    def is_cached(self) -> bool:
        """Check if the underlying DataFrame is cached."""
        return self._df.is_cached

    # DataFrame Properties (delegate to underlying DataFrame)
    @property
    def columns(self) -> List[str]:
        """Get column names."""
        return self._df.columns

    @property
    def dtypes(self) -> List[tuple]:
        """Get column data types."""
        return self._df.dtypes

    @property
    def schema(self) -> StructType:
        """Get DataFrame schema."""
        return self._df.schema

    @property
    def rdd(self):
        """Get underlying RDD."""
        return self._df.rdd

    def _register_as_source(self) -> None:
        """Register this DataFrame as a source in the lineage tracking system."""
        tracker = get_global_tracker()
        if not tracker or not tracker.should_track():
            return

        try:
            # Register with fork detector
            fork_detector = get_fork_detector()
            context_id = get_current_context_id()
            if context_id:
                fork_detector.register_producer(self._lineage_id.id, context_id)

            # Create and register source operation node
            source_node = OperationNode(
                node_id=self._lineage_id.operation_id,
                operation_type=OperationType.SOURCE,
                business_context=self._business_label or "Data Source"
            )
            source_node.name = f"Load {self._business_label or 'Dataset'}"
            source_node.metadata = {
                'operation_name': f"Load Source Data",
                'lineage_id': self._lineage_id.id,
                'business_label': self._business_label,
                'track_columns': self._track_columns.copy(),
                'materialized': self._materialize,
                'datasource_type': 'immutable_dataframe_wrapper'
            }

            # Capture metrics if materialization is enabled
            if self._materialize and tracker.should_materialize():
                source_node.output_metrics = self._capture_metrics()

            # Register the source LineageID with the enhanced tracker
            tracker.register_lineage_id(self._lineage_id)

            # Register with tracker
            tracker.add_operation(source_node, parent_node_id=None)

            logger.debug(f"Registered source operation: {source_node.node_id}")

        except Exception as e:
            logger.warning(f"Failed to register source: {e}")

    def _register_as_operation(self, operation_type: str, parent_lineages: List[LineageID]) -> None:
        """Register this DataFrame as an operation with parent lineages."""
        tracker = get_global_tracker()
        if not tracker or not tracker.should_track():
            return

        try:
            # Register with fork detector
            fork_detector = get_fork_detector()
            context_id = get_current_context_id()
            if context_id:
                fork_detector.register_producer(self._lineage_id.id, context_id)

            # Register consumption of parent lineages
            for parent in parent_lineages:
                if context_id:
                    fork_detector.register_consumer(parent.id, context_id)

            # Create and register operation node
            op_type = OperationType(operation_type) if operation_type in [t.value for t in OperationType] else OperationType.CUSTOM
            operation_node = OperationNode(
                node_id=self._lineage_id.operation_id,
                operation_type=op_type,
                business_context=self._business_label or f"{operation_type} operation"
            )
            operation_node.name = self._business_label or f"{operation_type.title()} Operation"
            operation_node.metadata = {
                'lineage_id': self._lineage_id.id,
                'parent_lineage_ids': [p.id for p in parent_lineages],
                'business_label': self._business_label,
                'track_columns': self._track_columns.copy(),
                'materialized': self._materialize,
                'operation_type': operation_type,
                'created_from_constructor': True
            }

            # Capture metrics if materialization is enabled
            if self._materialize and tracker.should_materialize():
                operation_node.output_metrics = self._capture_metrics()

            # Register the LineageID with the enhanced tracker
            tracker.register_lineage_id(self._lineage_id)

            # Register with tracker (use first parent as primary parent for tree structure)
            primary_parent_id = parent_lineages[0].operation_id if parent_lineages else None
            tracker.add_operation(operation_node, parent_node_id=primary_parent_id)

            # Add edges for all parent relationships
            for parent in parent_lineages:
                tracker.add_edge(parent.id, self._lineage_id.id, context_id=context_id)

            logger.debug(f"Registered operation: {operation_node.node_id} with {len(parent_lineages)} parent(s)")

        except Exception as e:
            logger.warning(f"Failed to register operation: {e}")

    def _detect_parent_lineages(self, dataframe: DataFrame) -> List[LineageID]:
        """
        Attempt to detect parent LineageIDs from DataFrame metadata or execution plan.

        This method checks:
        1. Custom metadata attached to DataFrame columns
        2. DataFrame execution plan for references to LineageDataFrame operations

        Returns:
            List of detected parent LineageIDs, or empty list if none found
        """
        detected_parents = []

        try:
            # Method 1: Check for lineage metadata in DataFrame schema metadata
            # (This would require storing lineage info in column metadata during operations)
            if hasattr(dataframe, '_jdf'):
                # Try to extract lineage from Spark's internal metadata
                # Note: This is a placeholder - actual implementation would depend on
                # how we choose to embed lineage metadata in Spark DataFrames
                pass

            # Method 2: Parse execution plan for LineageDataFrame references
            # This is more complex and might not be reliable, so we skip for now

            # For now, return empty list - explicit parent_lineages parameter is preferred
            return detected_parents

        except Exception as e:
            logger.debug(f"Failed to detect parent lineages: {e}")
            return []

    def _capture_metrics(self) -> Optional[MetricsData]:
        """Capture metrics for this DataFrame if materialization is enabled."""
        if not self._materialize:
            return None

        try:
            row_count = safe_count(self._df)
            distinct_counts = {}

            for col_name in self._track_columns:
                if col_name in self._df.columns:
                    try:
                        from ..utils.dataframe_utils import safe_distinct_count
                        distinct_counts[col_name] = safe_distinct_count(self._df, col_name)
                    except Exception:
                        pass

            return MetricsData(
                row_count=row_count,
                column_count=len(self._df.columns),
                distinct_counts=distinct_counts,
                estimated=False
            )

        except Exception as e:
            logger.warning(f"Failed to capture metrics: {e}")
            return None

    def _create_result_dataframe(self,
                                result_df: DataFrame,
                                operation_type: str,
                                operation_name: str = None,
                                extra_metadata: Optional[Dict[str, Any]] = None) -> 'LineageDataFrame':
        """
        Create a new LineageDataFrame for an operation result.

        This method creates a new DataFrame wrapper with a new LineageID that
        references this DataFrame as its parent. This preserves immutability
        and enables proper fork tracking.
        """
        context_id = get_current_context_id()

        # Create new LineageID for the result
        result_lineage_id = LineageID.create_from_parent(
            parent=self._lineage_id,
            operation_type=operation_type,
            context_id=context_id
        )

        # Register fork consumption with enhanced tracker (which syncs to enhanced graph)
        tracker = get_global_tracker()
        if context_id and tracker:
            # CRITICAL FIX: Register the new result LineageID as a node in the enhanced graph
            # Pass the current context so operation nodes get context_id set
            current_context = get_current_context()
            tracker.register_lineage_id(result_lineage_id, current_context)
            logger.debug(f"Registered new LineageID as node: {result_lineage_id.id}")

            # Register this DataFrame as being consumed
            fork_status = tracker.register_fork_consumption(
                self._lineage_id.id,
                context_id,
                operation_type
            )

            if fork_status == ForkStatus.FORK_DETECTED:
                logger.info(f"Fork detected: {self._lineage_id.id} consumed by multiple operations")

            # Register the new result as being produced
            fork_detector = get_fork_detector()
            fork_detector.register_producer(result_lineage_id.id, context_id)

        # Create result wrapper
        result_wrapper = LineageDataFrame(
            dataframe=result_df,
            lineage_id=result_lineage_id,
            business_label=operation_name or f"Result of {operation_type}",
            materialize=self._materialize,
            track_columns=self._track_columns,
            metadata=self._metadata.copy()
        )

        # Register operation with tracker, passing extra metadata
        self._register_operation(result_lineage_id, operation_type, operation_name, result_wrapper, extra_metadata)

        return result_wrapper

    def _register_operation(self,
                           result_lineage_id: LineageID,
                           operation_type: str,
                           operation_name: str = None,
                           result_wrapper: 'LineageDataFrame' = None,
                           extra_metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register an operation with the lineage tracker."""
        tracker = get_global_tracker()
        if not tracker or not tracker.should_track():
            return

        # No longer suppressing operations in merge mode - let them all be tracked

        try:
            operation_node = OperationNode(
                node_id=result_lineage_id.operation_id,
                operation_type=getattr(OperationType, operation_type.upper(), OperationType.TRANSFORM),
                business_context=operation_name or f"{operation_type.title()} Operation"
            )
            operation_node.name = operation_name or f"{operation_type.title()} Operation"
            operation_node.metadata = {
                'lineage_id': result_lineage_id.id,
                'parent_lineage_id': self._lineage_id.id,
                'operation_type': operation_type,
                'materialized': self._materialize
            }

            # Merge in extra metadata (like filter_condition)
            if extra_metadata:
                operation_node.metadata.update(extra_metadata)

            # Capture metrics if enabled
            if self._materialize and tracker.should_materialize():
                operation_node.before_metrics = self._capture_metrics()

                # Capture after_metrics from result if available
                if result_wrapper:
                    operation_node.after_metrics = result_wrapper._capture_metrics()

            # Extract operation-specific details (fallback if not in extra_metadata)
            if operation_type == "filter" and operation_name and 'filter_condition' not in operation_node.metadata:
                # Extract filter condition from operation name as fallback
                if "Filter:" in operation_name:
                    condition = operation_name.split("Filter:")[1].strip()
                    operation_node.metadata['filter_condition'] = condition

            # Add execution time (simple timing for now)
            import time
            operation_node.execution_time = 0.001  # Placeholder - could be enhanced with actual timing

            # CRITICAL FIX: Associate operation with current business concept context
            current_context = get_current_context()
            if current_context:
                # Get the BusinessConceptNode for this context from the enhanced graph
                enhanced_graph = tracker.get_lineage_graph()
                if current_context.context_id in enhanced_graph.nodes:
                    business_concept_node = enhanced_graph.nodes[current_context.context_id]
                    if hasattr(business_concept_node, 'add_technical_operation'):
                        business_concept_node.add_technical_operation(operation_node)
                        logger.debug(f"Added operation {operation_node.node_id} to business concept {business_concept_node.name}")

            # Register the LineageID with the enhanced tracker
            # Pass the current context so operation nodes get context_id set
            tracker.register_lineage_id(result_lineage_id, current_context)

            # Register with parent
            tracker.add_operation(operation_node, parent_node_id=self._lineage_id.operation_id)

            logger.debug(f"Registered operation: {operation_node.node_id} -> {result_lineage_id.id}")

        except Exception as e:
            logger.warning(f"Failed to register operation: {e}")

    # Core DataFrame Operations with Immutable Lineage Tracking

    def filter(self, condition) -> 'LineageDataFrame':
        """Filter rows with immutable lineage tracking."""
        result_df = self._df.filter(condition)
        # Capture full condition for metadata, short version for business label
        full_condition_str = str(condition)
        condition_str = full_condition_str[:50].replace('<', '').replace('>', '').replace('"', "'")

        # Pass full condition in metadata
        result = self._create_result_dataframe(
            result_df,
            "filter",
            f"Filter: {condition_str}",
            extra_metadata={'filter_condition': full_condition_str}
        )
        return result

    def where(self, condition) -> 'LineageDataFrame':
        """Alias for filter with immutable lineage tracking."""
        return self.filter(condition)

    def select(self, *cols) -> 'LineageDataFrame':
        """Select columns with immutable lineage tracking."""
        input_column_count = len(self._df.columns)
        result_df = self._df.select(*cols)
        output_column_count = len(result_df.columns)
        col_names = [str(col) for col in cols]
        return self._create_result_dataframe(
            result_df,
            "select",
            f"Column Selection",
            extra_metadata={
                'operation_name': 'Column Selection',
                'selected_columns': col_names,
                'input_column_count': input_column_count,
                'output_column_count': output_column_count
            }
        )

    def withColumn(self, colName: str, col) -> 'LineageDataFrame':
        """Add or replace column with immutable lineage tracking."""
        result_df = self._df.withColumn(colName, col)
        col_expr = str(col)

        # Remove redundant Column<> wrapper if present
        if col_expr.startswith("Column<") and col_expr.endswith(">"):
            col_expr = col_expr[8:-1]  # Remove "Column<" and ">"
        # Remove outer quotes if present (either single or double)
        if (col_expr.startswith("'") and col_expr.endswith("'")) or \
           (col_expr.startswith('"') and col_expr.endswith('"')):
            col_expr = col_expr[1:-1]
        # Remove any remaining trailing quote that wasn't matched
        if col_expr.endswith("'") or col_expr.endswith('"'):
            col_expr = col_expr[:-1]

        # Check if column exists to determine if this is creation or modification
        is_new_column = colName not in self._df.columns

        # Build metadata with reassignment tracking
        metadata = {
            'columns_added': [colName] if is_new_column else [],
            'columns_modified': [] if is_new_column else [colName],
            'transformation': f"{colName} = {col_expr}",
            'transformation_type': 'creation' if is_new_column else 'modification'
        }

        # If this is a modification (reassignment), track additional context
        if not is_new_column:
            metadata['is_reassignment'] = True
            metadata['reassigned_column'] = colName
            metadata['previous_lineage_id'] = self._lineage_id.id

            # Try to find which transformation last touched this column in this lineage chain
            tracker = get_global_tracker()
            if tracker:
                # Trace back through the lineage chain to find previous transformation
                current_lineage_id = self._lineage_id.id
                visited = set()

                def find_previous_transformation(lid):
                    """Recursively search for the last transformation that created/modified this column."""
                    if lid in visited:
                        return None
                    visited.add(lid)

                    # Check if this lineage has the column transformation
                    if lid in tracker.enhanced_graph.lineage_nodes:
                        node = tracker.enhanced_graph.lineage_nodes[lid]
                        if hasattr(node, 'metadata') and node.metadata:
                            cols_added = node.metadata.get('columns_added', [])
                            cols_modified = node.metadata.get('columns_modified', [])
                            transformation = node.metadata.get('transformation', '')

                            # Check if this transformation involves our column
                            if (colName in cols_added or colName in cols_modified) and transformation:
                                return {
                                    'node_id': node.node_id,
                                    'transformation': transformation
                                }

                    # Search through parent lineages
                    lineage_obj = tracker.lineage_id_tracker.get_lineage(lid)
                    if lineage_obj:
                        for parent_id in lineage_obj.parent_ids:
                            result = find_previous_transformation(parent_id)
                            if result:
                                return result

                    return None

                # Start search from current lineage
                result = find_previous_transformation(current_lineage_id)
                if result:
                    metadata['previous_transformation_id'] = result['node_id']
                    metadata['previous_transformation'] = result['transformation']

        return self._create_result_dataframe(
            result_df,
            "transform",
            f"Add column: {colName}",
            extra_metadata=metadata
        )

    def drop(self, *cols) -> 'LineageDataFrame':
        """Drop columns with immutable lineage tracking."""
        input_column_count = len(self._df.columns)
        result_df = self._df.drop(*cols)
        output_column_count = len(result_df.columns)
        col_names = [str(col) for col in cols]
        return self._create_result_dataframe(
            result_df,
            "select",
            f"Drop: {', '.join(col_names)}",
            extra_metadata={
                'operation_name': 'Column Selection',
                'dropped_columns': col_names,
                'input_column_count': input_column_count,
                'output_column_count': output_column_count
            }
        )

    def groupBy(self, *cols) -> 'LineageGroupedData':
        """
        Group by columns - returns LineageGroupedData for tracked aggregation.

        This method wraps PySpark's native groupBy to preserve lineage tracking
        through aggregation operations. The returned LineageGroupedData intercepts
        all aggregation methods (agg, count, sum, etc.) to create lineage nodes
        and edges.

        Args:
            *cols: Column names or Column objects to group by

        Returns:
            LineageGroupedData wrapper that tracks all aggregation operations

        Example:
            result = ldf.groupBy("region", "product").agg(
                sum("revenue").alias("total_revenue"),
                avg("quantity").alias("avg_quantity")
            )
        """
        from .lineage_grouped_data import LineageGroupedData
        from .lineage_tracker import get_global_tracker

        # Execute native groupBy
        native_grouped = self._df.groupBy(*cols)

        # Convert columns to strings for metadata
        group_cols = []
        for col in cols:
            if isinstance(col, str):
                group_cols.append(col)
            else:
                # Column object - try to extract name
                group_cols.append(str(col))

        # Wrap in LineageGroupedData with lineage context
        return LineageGroupedData(
            grouped_data=native_grouped,
            parent_lineage_df=self,
            group_cols=group_cols,
            tracker=get_global_tracker(),
            context_id=self.lineage_id.context_id
        )

    def join(self,
             other: Union[DataFrame, 'LineageDataFrame'],
             on: Union[str, List[str]] = None,
             how: str = "inner") -> 'LineageDataFrame':
        """
        Join with another DataFrame with multi-parent lineage tracking.

        When joining with an untracked DataFrame (regular PySpark DataFrame),
        a synthetic lineage node is automatically created to track it as a parent.
        The synthetic node will appear as "Untracked DataFrame: {variable_name}"
        in lineage reports.

        Args:
            other: DataFrame or LineageDataFrame to join with
            on: Column name(s) to join on
            how: Join type (inner, outer, left, right, etc.)

        Returns:
            New LineageDataFrame representing the join result

        Example:
            >>> tracked_df = LineageDataFrame(...)
            >>> regular_df = spark.createDataFrame(...)  # Untracked
            >>> result = tracked_df.join(regular_df, "id")  # Both parents tracked
        """
        # Extract DataFrame and LineageID from other
        if isinstance(other, LineageDataFrame):
            other_df = other.dataframe
            other_lineage_id = other.lineage_id
        else:
            # Handle untracked DataFrame - create synthetic lineage node
            other_df = other

            # Try to get variable name
            var_name = _get_variable_name(other) or "unknown"

            # Create synthetic lineage ID for untracked DataFrame
            other_lineage_id = LineageID.create_source(
                source_name=f"untracked_{var_name}"
            )

            # Register as a source node in tracker
            tracker = get_global_tracker()
            if tracker and tracker.should_track():
                # Register the LineageID
                tracker.register_lineage_id(other_lineage_id)

                # Create a source operation node for the untracked DataFrame
                source_node = OperationNode(
                    node_id=other_lineage_id.operation_id,
                    operation_type=OperationType.SOURCE,
                    business_context=f"Untracked DataFrame: {var_name}"
                )
                source_node.name = f"Untracked DataFrame: {var_name}"
                source_node.metadata = {
                    'lineage_id': other_lineage_id.id,
                    'is_synthetic': True,
                    'reason': 'Untracked DataFrame joined with tracked DataFrame',
                    'variable_name': var_name,
                    'datasource_type': 'untracked_dataframe'
                }

                # Register the source operation
                tracker.add_operation(source_node, parent_node_id=None)

                logger.info(
                    f"Created synthetic source node for untracked DataFrame: {var_name} "
                    f"(lineage_id: {other_lineage_id.id})"
                )

        # Capture input metrics before join
        input_column_count = len(self._df.columns)
        other_column_count = len(other_df.columns)

        # Perform the join
        result_df = self._df.join(other_df, on, how)

        # Capture output metrics after join
        output_column_count = len(result_df.columns)

        # Create multi-parent LineageID
        context_id = get_current_context_id()
        result_lineage_id = LineageID.create_from_parents(
            parents=[self._lineage_id, other_lineage_id],
            operation_type="join",
            context_id=context_id
        )

        # Register consumers with enhanced tracker (which syncs to enhanced graph)
        tracker = get_global_tracker()
        fork_detector = get_fork_detector()

        if tracker and tracker.should_track():
            # Register fork consumption
            if context_id:
                tracker.register_fork_consumption(self._lineage_id.id, context_id, "join")
                tracker.register_fork_consumption(other_lineage_id.id, context_id, "join")

                # Register with fork detector
                fork_detector.register_producer(result_lineage_id.id, context_id)
                fork_detector.register_consumer(self._lineage_id.id, context_id)
                fork_detector.register_consumer(other_lineage_id.id, context_id)

            # Create and register join operation node
            join_node = OperationNode(
                node_id=result_lineage_id.operation_id,
                operation_type=OperationType.JOIN,
                business_context=f"Join: {how}"
            )
            join_node.name = f"Join ({how})"
            join_node.metadata = {
                'lineage_id': result_lineage_id.id,
                'parent_lineage_ids': [self._lineage_id.id, other_lineage_id.id],
                'operation_type': 'join',
                'join_type': how,
                'join_keys': str(on) if on is not None else 'unknown',
                'input_column_count': input_column_count,
                'other_column_count': other_column_count,
                'output_column_count': output_column_count
            }

            # Register the join LineageID
            tracker.register_lineage_id(result_lineage_id)

            # Update the lineage node's metadata with join details
            if result_lineage_id.id in tracker.enhanced_graph.lineage_nodes:
                lineage_node = tracker.enhanced_graph.lineage_nodes[result_lineage_id.id]
                lineage_node.metadata['join_type'] = how
                lineage_node.metadata['join_keys'] = str(on) if on is not None else 'unknown'
                lineage_node.metadata['input_column_count'] = input_column_count
                lineage_node.metadata['other_column_count'] = other_column_count
                lineage_node.metadata['output_column_count'] = output_column_count

            # CRITICAL: Create result wrapper FIRST so we can capture after_metrics before calling add_operation
            result_wrapper = LineageDataFrame(
                dataframe=result_df,
                lineage_id=result_lineage_id,
                business_label=f"Join: {how}",
                materialize=self._materialize,
                track_columns=self._track_columns
            )

            # Capture metrics if materialization is enabled
            # MUST be done BEFORE calling add_operation so metrics are available for copying
            if self._materialize and tracker.should_materialize():
                # Capture before metrics from input dataframe
                join_node.before_metrics = self._capture_metrics()
                # Capture after metrics from result
                join_node.after_metrics = result_wrapper._capture_metrics()

                # Update the join_node metadata with the metrics
                if 'metrics' not in join_node.metadata:
                    join_node.metadata['metrics'] = {}
                if join_node.before_metrics:
                    join_node.metadata['metrics']['input_record_count'] = join_node.before_metrics.row_count
                if join_node.after_metrics:
                    join_node.metadata['metrics']['output_record_count'] = join_node.after_metrics.row_count
                    join_node.metadata['metrics']['row_count'] = join_node.after_metrics.row_count

            # Register operation with primary parent (first DataFrame)
            logger.debug(f"About to call add_operation for join_node {join_node.node_id}")
            logger.debug(f"join_node.metadata = {join_node.metadata}")
            logger.debug(f"parent_node_id = {self._lineage_id.operation_id}")
            tracker.add_operation(join_node, parent_node_id=self._lineage_id.operation_id)

            # Add additional parent edge for second DataFrame in join
            # The first parent edge is added automatically by add_operation
            if hasattr(tracker, 'add_lineage_edge'):
                tracker.add_lineage_edge(other_lineage_id.id, result_lineage_id.id, context_id=context_id)

            # CRITICAL: Update the enhanced graph node metadata for JSON export
            # The add_operation call above adds the node, but we need to ensure metadata is copied
            enhanced_graph = tracker.get_lineage_graph()
            logger.debug(f"Join node ID: {join_node.node_id}, checking in enhanced_graph.nodes...")
            logger.debug(f"Enhanced graph nodes keys: {list(enhanced_graph.nodes.keys())}")

            if join_node.node_id in enhanced_graph.nodes:
                graph_node = enhanced_graph.nodes[join_node.node_id]
                logger.debug(f"Found graph node, current metadata: {graph_node.metadata}")
                # Ensure all join metadata is in the graph node
                for key in ['join_type', 'join_keys', 'input_column_count', 'other_column_count', 'output_column_count']:
                    if key in join_node.metadata:
                        graph_node.metadata[key] = join_node.metadata[key]
                logger.debug(f"Updated join metadata in enhanced graph for {join_node.node_id}, new metadata: {graph_node.metadata}")
            else:
                logger.warning(f"Join node {join_node.node_id} NOT found in enhanced_graph.nodes!")

            logger.debug(f"Registered join operation: {join_node.node_id}")

        return result_wrapper

    def union(self, other: Union[DataFrame, 'LineageDataFrame']) -> 'LineageDataFrame':
        """
        Union with another DataFrame with multi-parent lineage tracking.

        When unioning with an untracked DataFrame (regular PySpark DataFrame),
        a synthetic lineage node is automatically created to track it as a parent.
        The synthetic node will appear as "Untracked DataFrame: {variable_name}"
        in lineage reports.

        Args:
            other: DataFrame or LineageDataFrame to union with

        Returns:
            New LineageDataFrame representing the union result

        Example:
            >>> tracked_df = LineageDataFrame(...)
            >>> regular_df = spark.createDataFrame(...)  # Untracked
            >>> result = tracked_df.union(regular_df)  # Both parents tracked
        """
        # Extract DataFrame and LineageID from other
        if isinstance(other, LineageDataFrame):
            other_df = other.dataframe
            other_lineage_id = other.lineage_id
        else:
            # Handle untracked DataFrame - create synthetic lineage node
            other_df = other

            # Try to get variable name
            var_name = _get_variable_name(other) or "unknown"

            # Create synthetic lineage ID for untracked DataFrame
            other_lineage_id = LineageID.create_source(
                source_name=f"untracked_{var_name}"
            )

            # Register as a source node in tracker
            tracker = get_global_tracker()
            if tracker and tracker.should_track():
                # Register the LineageID
                tracker.register_lineage_id(other_lineage_id)

                # Create a source operation node for the untracked DataFrame
                source_node = OperationNode(
                    node_id=other_lineage_id.operation_id,
                    operation_type=OperationType.SOURCE,
                    business_context=f"Untracked DataFrame: {var_name}"
                )
                source_node.name = f"Untracked DataFrame: {var_name}"
                source_node.metadata = {
                    'lineage_id': other_lineage_id.id,
                    'is_synthetic': True,
                    'reason': 'Untracked DataFrame unioned with tracked DataFrame',
                    'variable_name': var_name,
                    'datasource_type': 'untracked_dataframe'
                }

                # Register the source operation
                tracker.add_operation(source_node, parent_node_id=None)

                logger.info(
                    f"Created synthetic source node for untracked DataFrame: {var_name} "
                    f"(lineage_id: {other_lineage_id.id})"
                )

        result_df = self._df.union(other_df)

        context_id = get_current_context_id()
        result_lineage_id = LineageID.create_from_parents(
            parents=[self._lineage_id, other_lineage_id],
            operation_type="union",
            context_id=context_id
        )

        # Register consumers with enhanced tracker (which syncs to enhanced graph)
        tracker = get_global_tracker()
        fork_detector = get_fork_detector()

        if tracker and tracker.should_track():
            # Register fork consumption
            if context_id:
                tracker.register_fork_consumption(self._lineage_id.id, context_id, "union")
                tracker.register_fork_consumption(other_lineage_id.id, context_id, "union")

                # Register with fork detector
                fork_detector.register_producer(result_lineage_id.id, context_id)
                fork_detector.register_consumer(self._lineage_id.id, context_id)
                fork_detector.register_consumer(other_lineage_id.id, context_id)

            # Create and register union operation node
            union_node = OperationNode(
                node_id=result_lineage_id.operation_id,
                operation_type=OperationType.UNION,
                business_context="Union"
            )
            union_node.name = "Union"
            union_node.metadata = {
                'lineage_id': result_lineage_id.id,
                'parent_lineage_ids': [self._lineage_id.id, other_lineage_id.id],
                'operation_type': 'union'
            }

            # Capture metrics if materialization is enabled
            if self._materialize and tracker.should_materialize():
                # Capture before metrics from first input dataframe
                union_node.before_metrics = self._capture_metrics()

            # Register the union LineageID
            tracker.register_lineage_id(result_lineage_id)

            # Register operation with primary parent (first DataFrame)
            tracker.add_operation(union_node, parent_node_id=self._lineage_id.operation_id)

            # Add additional parent edge for second DataFrame in union
            # The first parent edge is added automatically by add_operation
            if hasattr(tracker, 'add_lineage_edge'):
                tracker.add_lineage_edge(other_lineage_id.id, result_lineage_id.id, context_id=context_id)

            logger.debug(f"Registered union operation: {union_node.node_id}")

        # Create result wrapper
        result_wrapper = LineageDataFrame(
            dataframe=result_df,
            lineage_id=result_lineage_id,
            business_label="Union",
            materialize=self._materialize,
            track_columns=self._track_columns
        )

        # Capture after metrics if materialization was enabled
        if tracker and tracker.should_track() and self._materialize and tracker.should_materialize():
            union_node.after_metrics = result_wrapper._capture_metrics()

        return result_wrapper

    def cache(self, storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK) -> 'LineageDataFrame':
        """Cache DataFrame and mark as potential fork point."""
        cached_df = self._df.cache()

        # Mark as cached in fork detector
        fork_detector = get_fork_detector()
        fork_detector.mark_as_cached(self._lineage_id.id)

        # Return new wrapper with cached DataFrame
        return LineageDataFrame(
            dataframe=cached_df,
            lineage_id=self._lineage_id,  # Same lineage ID - just cached
            business_label=self._business_label,
            materialize=self._materialize,
            track_columns=self._track_columns,
            metadata=self._metadata
        )

    def persist(self, storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK) -> 'LineageDataFrame':
        """Persist DataFrame and mark as potential fork point."""
        persisted_df = self._df.persist(storage_level)

        # Mark as cached in fork detector
        fork_detector = get_fork_detector()
        fork_detector.mark_as_cached(self._lineage_id.id)

        return LineageDataFrame(
            dataframe=persisted_df,
            lineage_id=self._lineage_id,
            business_label=self._business_label,
            materialize=self._materialize,
            track_columns=self._track_columns,
            metadata=self._metadata
        )

    # Special methods for DataFrame API compatibility
    def __getitem__(self, item):
        """
        Support subscript notation for column access: df["column"] or df[column_list].

        This is a critical PySpark DataFrame API method that must be explicitly implemented
        because Python's __getattr__ doesn't intercept special methods like __getitem__.

        Args:
            item: Column name (str), list of column names, or Column object

        Returns:
            Column object or LineageDataFrame with selected columns
        """
        result = self._df.__getitem__(item)

        # If result is a DataFrame (column selection), wrap it with lineage tracking
        if isinstance(result, DataFrame):
            return self._create_result_dataframe(
                result,
                "select",
                "Column Selection"
            )

        # Otherwise it's a Column object, return as-is
        return result

    # Delegation to underlying DataFrame for all other operations
    def __getattr__(self, name):
        """
        Delegate to underlying DataFrame for operations not explicitly handled.

        This ensures compatibility with all DataFrame methods while preserving
        the option to add specific lineage tracking for any operation.
        """
        attr = getattr(self._df, name)

        if callable(attr):
            @wraps(attr)
            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)

                # If result is a DataFrame, wrap it
                if isinstance(result, DataFrame):
                    return self._create_result_dataframe(
                        result,
                        "transform",
                        f"{name.title()} Operation"
                    )

                return result

            return wrapper
        else:
            return attr

    def show(self, n: int = 20, truncate: Union[bool, int] = True, vertical: bool = False) -> None:
        """Show DataFrame contents."""
        return self._df.show(n, truncate, vertical)

    def count(self) -> int:
        """Count rows in DataFrame."""
        return self._df.count()

    def collect(self) -> List:
        """Collect DataFrame to driver."""
        return self._df.collect()

    def generate_governance_audit_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./"
    ) -> str:
        """
        Generate a governance audit report for all operations with governance metadata.

        This method automatically extracts operations from the lineage graph,
        filters for those with governance metadata, and generates a comprehensive
        audit report. This provides a simple API for governance reporting without
        requiring manual graph traversal.

        Args:
            pipeline_name: Name of the pipeline (defaults to current script filename or "pipeline")
            output_path: Directory or file path where to save the report (default: "./")

        Returns:
            Path to the generated audit report file

        Example:
            >>> # Simple usage with defaults
            >>> result_df.generate_governance_audit_report()

            >>> # With custom pipeline name and output location
            >>> result_df.generate_governance_audit_report(
            ...     pipeline_name="customer_risk_scoring",
            ...     output_path="./reports/governance/"
            ... )

        Note:
            - Only operations with EnhancedGovernanceMetadata will be included
            - The report follows the standard governance audit template
            - Auto-detects pipeline name from __main__.__file__ if not provided
        """
        import os
        from pathlib import Path

        from ..governance.audit_report import GovernanceAuditReportGenerator
        from ..governance.enhanced_metadata import EnhancedGovernanceMetadata

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            try:
                import __main__
                if hasattr(__main__, '__file__') and __main__.__file__:
                    # Extract filename without extension
                    pipeline_name = Path(__main__.__file__).stem
                else:
                    pipeline_name = "pipeline"
            except:
                pipeline_name = "pipeline"

        # Get the lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        if not tracker:
            raise LineageTrackingError(
                "No lineage tracker found. Ensure tracking is enabled."
            )

        graph = tracker.get_lineage_graph()

        # Extract operations with governance metadata from the graph
        operations_with_governance = []

        for node in graph.nodes.values():
            gov = None

            # Check if it's a BusinessConceptNode with governance_metadata attribute
            if hasattr(node, 'governance_metadata') and node.governance_metadata:
                gov = node.governance_metadata

            # Also check in metadata dict
            elif hasattr(node, 'metadata') and 'governance_metadata' in node.metadata:
                gov = node.metadata['governance_metadata']

            if gov and isinstance(gov, EnhancedGovernanceMetadata):
                operations_with_governance.append({
                    'operation_name': node.name if hasattr(node, 'name') else str(node),
                    'governance_metadata': gov,
                })

        # Handle case where no governance metadata found
        if not operations_with_governance:
            logger.warning(
                "No operations with governance metadata found in lineage graph. "
                "Report will be empty. Use @businessConcept decorator with governance parameter."
            )

        # Determine output file path
        output_path_obj = Path(output_path)

        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            # It's a directory, create filename
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_governance_audit_report.md"
        else:
            # It's a file path, ensure directory exists
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate the audit report
        generator = GovernanceAuditReportGenerator()
        generated_path = generator.generate_audit_report(
            pipeline_name=pipeline_name,
            operations=operations_with_governance,
            output_path=str(report_file)
        )

        logger.info(f"Governance audit report generated: {generated_path}")

        return generated_path

    def generate_data_engineer_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> Dict[str, str]:
        """
        Generate comprehensive data engineer reports for debugging and validation.

        This method automatically extracts the lineage graph and generates technical
        reports including lineage diagrams, terminal summaries, column lineage, and
        data quality metrics. This provides a simple API for engineer-focused reporting.

        Args:
            pipeline_name: Name of the pipeline (defaults to current script filename or "Data Pipeline")
            output_path: Directory where to save the reports (default: "./")
            **kwargs: Additional configuration options for DataEngineerReportConfig:
                - data_loss_threshold: Threshold for data loss alerts (default: 0.10)
                - duplicate_threshold: Threshold for duplicate alerts (default: 0.05)
                - null_threshold: Threshold for null value alerts (default: 0.05)
                - track_columns: List of columns to track in detail
                - include_lineage_diagram: Include lineage diagram (default: True)
                - include_terminal_summary: Include terminal summary (default: True)
                - include_column_lineage: Include column lineage (default: True)

        Returns:
            Dictionary mapping report type to file path with keys:
                - 'lineage_diagram': Path to main lineage diagram
                - 'terminal_summary': Path to terminal summary
                - 'column_lineage': Path to column lineage report
                - 'json_lineage': Path to JSON lineage data

        Example:
            >>> # Simple usage with defaults
            >>> report_paths = result_df.generate_data_engineer_report()

            >>> # With custom configuration
            >>> report_paths = result_df.generate_data_engineer_report(
            ...     pipeline_name="customer_enrichment",
            ...     output_path="./reports/",
            ...     data_loss_threshold=0.05,
            ...     track_columns=["customer_id", "email"]
            ... )
            >>> print(f"Main report: {report_paths['lineage_diagram']}")

        Note:
            - Includes row count tracking and data quality metrics
            - Detects data loss, duplicates, and high null percentages
            - Generates multiple output files for different use cases
        """
        from pathlib import Path
        from typing import Dict

        from ..reporting.data_engineer_report import generate_engineer_reports

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            try:
                import __main__
                if hasattr(__main__, '__file__') and __main__.__file__:
                    # Extract filename without extension
                    pipeline_name = Path(__main__.__file__).stem
                else:
                    pipeline_name = "Data Pipeline"
            except:
                pipeline_name = "Data Pipeline"

        # Get the lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        if not tracker:
            raise LineageTrackingError(
                "No lineage tracker found. Ensure tracking is enabled."
            )

        graph = tracker.get_lineage_graph()

        # Ensure output_path is a directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate the reports using the existing convenience function
        report_paths = generate_engineer_reports(
            lineage_graph=graph,
            output_dir=str(output_dir),
            pipeline_name=pipeline_name,
            **kwargs
        )

        logger.info(f"Data engineer reports generated: {len(report_paths)} files")

        return report_paths

    def _auto_detect_pipeline_name(self) -> str:
        """
        Auto-detect pipeline name from __main__.__file__ or use default.

        Returns:
            Detected pipeline name or 'pipeline' as fallback
        """
        try:
            import __main__
            if hasattr(__main__, '__file__') and __main__.__file__:
                from pathlib import Path
                return Path(__main__.__file__).stem
        except:
            pass
        return "pipeline"

    # ========================================================================
    # CRITICAL PRIORITY: Governance and Core Reporting Outputs
    # ========================================================================

    def generate_governance_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        include_technical_details: bool = False,
        **kwargs
    ) -> str:
        """
        Generate comprehensive governance report for the pipeline.

        This method abstracts away the complexity of extracting governance data
        from the lineage graph, following the Output Abstraction Pattern (DP-001).

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            include_technical_details: Include technical implementation details.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_governance_report()
            >>> print(f"Report generated: {report_path}")
        """
        from pathlib import Path

        from ..governance.reporting import GovernanceReportGenerator

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_governance_report.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = GovernanceReportGenerator()
        report_path = generator.generate_pipeline_report(
            lineage_graph=lineage_graph,
            output_path=str(report_file),
            include_technical_details=include_technical_details,
            **kwargs
        )

        logger.info(f"Governance report generated: {report_path}")
        return report_path

    def generate_comprehensive_tracking_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate comprehensive tracking report combining multiple views.

        This method generates a comprehensive report with business catalog,
        flow diagrams, and optional statistical sections.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for ComprehensivePipelineReportConfig.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_comprehensive_tracking_report()
        """
        from pathlib import Path

        from ..reporting.comprehensive_report import ComprehensivePipelineReport

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_comprehensive_report.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = ComprehensivePipelineReport(**kwargs)
        report_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Comprehensive tracking report generated: {report_path}")
        return report_path

    # ========================================================================
    # HIGH PRIORITY: Business Stakeholder Outputs
    # ========================================================================

    def generate_business_catalog(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate business concept catalog with textual documentation.

        This method abstracts away the complexity of extracting business concepts
        from the lineage graph, following the Output Abstraction Pattern (DP-001).

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for BusinessConceptCatalogConfig:
                - sort_by: "execution_order", "name", or "execution_time"
                - include_metrics: Include row counts and metrics
                - show_quality_metrics: Show data quality information

        Returns:
            Path to generated catalog file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> catalog_path = result_df.generate_business_catalog()
            >>> print(f"Catalog generated: {catalog_path}")
        """
        from pathlib import Path

        from ..reporting.business_concept_catalog import BusinessConceptCatalog

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_business_catalog.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate catalog
        generator = BusinessConceptCatalog(**kwargs)
        catalog_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Business catalog generated: {catalog_path}")
        return catalog_path

    def generate_business_flow_diagram(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate business flow diagram with Mermaid visualization.

        This method creates a visual flowchart showing business concepts and
        data flow with configurable detail levels.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for BusinessFlowDiagramConfig:
                - detail_level: "minimal", "impacting", or "complete"
                - show_metrics: Show row counts and metrics
                - group_by_context: Group operations by business context

        Returns:
            Path to generated diagram file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> diagram_path = result_df.generate_business_flow_diagram(
            ...     detail_level="impacting"
            ... )
        """
        from pathlib import Path

        from ..reporting.business_flow_diagram import BusinessFlowDiagram

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_business_flow.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate diagram
        generator = BusinessFlowDiagram(**kwargs)
        diagram_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Business flow diagram generated: {diagram_path}")
        return diagram_path

    def generate_concept_relationship_diagram(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate concept relationship diagram showing dependencies.

        This method creates a visual diagram showing relationships between
        business concepts with data flow and dependencies.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated diagram file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> diagram_path = result_df.generate_concept_relationship_diagram()
        """
        from pathlib import Path

        from ..reporting.concept_relationship_diagram import ConceptRelationshipDiagram

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_concept_relationships.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate diagram
        generator = ConceptRelationshipDiagram(**kwargs)
        diagram_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Concept relationship diagram generated: {diagram_path}")
        return diagram_path

    # ========================================================================
    # HIGH PRIORITY: Data Scientist Outputs
    # ========================================================================

    def generate_feature_catalog(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate comprehensive feature catalog for data scientists.

        This method creates a detailed feature catalog with lineage, statistics,
        correlations, and business context.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for FeatureCatalogConfig:
                - features: List of features to include (None = all)
                - target_variable: Target variable name for correlations
                - feature_importance: Dict of feature importance scores
                - include_correlations: Include correlation matrix

        Returns:
            Path to generated catalog file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> catalog_path = result_df.generate_feature_catalog(
            ...     target_variable="churn",
            ...     features=["age", "tenure", "monthly_charges"]
            ... )
        """
        from pathlib import Path

        from ..data_scientist.feature_catalog import generate_feature_catalog

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Set pipeline_name in kwargs if not already present
        if 'pipeline_name' not in kwargs:
            kwargs['pipeline_name'] = pipeline_name

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_feature_catalog.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Get the lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Generate catalog using the standalone function
        catalog_path = generate_feature_catalog(
            lineage_graph=lineage_graph,
            df=self._df,  # Pass the underlying Spark DataFrame
            output_path=str(report_file),
            **kwargs
        )

        logger.info(f"Feature catalog generated: {catalog_path}")
        return catalog_path

    def generate_statistical_profile(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate statistical profile report for datasets.

        This method creates detailed statistical profiling with checkpoint-based
        snapshots, correlations, and data quality metrics.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated profile report.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> profile_path = result_df.generate_statistical_profile()
        """
        from pathlib import Path

        from ..data_scientist.statistical_report_generator import (
            StatisticalReportGenerator,
        )

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker to get profiler data
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()

        # Get profiler if available
        profiler = getattr(tracker, 'profiler', None)
        if profiler is None:
            logger.warning(
                "No statistical profiler found. Use @statisticalProfiler decorator "
                "to enable statistical profiling."
            )
            # Create empty profiler
            from ..data_scientist.statistical_profiler import StatisticalProfiler
            profiler = StatisticalProfiler()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_statistical_profile.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = StatisticalReportGenerator(profiler=profiler)
        report_path = generator.generate_report(
            output_path=str(report_file),
            pipeline_name=pipeline_name,
            **kwargs
        )

        logger.info(f"Statistical profile generated: {report_path}")
        return report_path

    def generate_reproducibility_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate reproducibility report for experiments.

        This method creates comprehensive documentation for reproducing experiments
        including environment, dependencies, data sources, and parameters.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for ReproducibilityConfig:
                - experiment_id: Unique experiment identifier
                - purpose: Purpose of the experiment
                - data_sources: List of data source paths
                - random_seed: Random seed used

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_reproducibility_report(
            ...     experiment_id="exp_001",
            ...     purpose="Customer churn prediction"
            ... )
        """
        from pathlib import Path

        from ..data_scientist.reproducibility_report import (
            ReproducibilityReportGenerator,
        )

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_reproducibility.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = ReproducibilityReportGenerator(**kwargs)
        report_path = generator.generate_report(
            lineage_graph=lineage_graph,
            output_path=str(report_file),
            pipeline_name=pipeline_name
        )

        logger.info(f"Reproducibility report generated: {report_path}")
        return report_path

    # ========================================================================
    # HIGH PRIORITY: Governance Outputs
    # ========================================================================

    def generate_governance_catalog(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate governance catalog in plain text format.

        This method creates a text catalog of all governance metadata for
        quick scanning and review.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated catalog file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> catalog_path = result_df.generate_governance_catalog()
        """
        from pathlib import Path

        from ..governance.catalog import generate_governance_catalog

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_governance_catalog.txt"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate catalog
        catalog_path = generate_governance_catalog(
            lineage_graph=lineage_graph,
            output_path=str(report_file),
            pipeline_name=pipeline_name,
            **kwargs
        )

        logger.info(f"Governance catalog generated: {catalog_path}")
        return catalog_path

    def generate_comprehensive_governance_catalog(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate comprehensive governance catalog with detailed metadata.

        This method creates a detailed governance catalog with risk analysis,
        customer impact, bias detection, and validation results.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated catalog file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> catalog_path = result_df.generate_comprehensive_governance_catalog()
        """
        from pathlib import Path

        from ..governance.comprehensive_catalog import (
            generate_comprehensive_governance_catalog,
        )

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_comprehensive_governance_catalog.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate catalog
        catalog_path = generate_comprehensive_governance_catalog(
            lineage_graph=lineage_graph,
            output_path=str(report_file),
            pipeline_name=pipeline_name,
            **kwargs
        )

        logger.info(f"Comprehensive governance catalog generated: {catalog_path}")
        return catalog_path

    def generate_integrated_governance_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate integrated governance report with lineage and governance overlay.

        This method creates a combined report with business flow diagram and
        governance markers/annotations.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_integrated_governance_report()
        """
        from pathlib import Path

        from ..governance.integrated_report import generate_integrated_governance_report

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_integrated_governance_report.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        report_path = generate_integrated_governance_report(
            lineage_graph=lineage_graph,
            output_path=str(report_file),
            pipeline_name=pipeline_name,
            **kwargs
        )

        logger.info(f"Integrated governance report generated: {report_path}")
        return report_path

    # ========================================================================
    # MEDIUM PRIORITY: Analytical and Utility Outputs
    # ========================================================================

    def generate_distribution_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate distribution analysis report for column values.

        This method creates statistical analysis of value distributions with
        frequency counts and histograms.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for DistributionReportConfig.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_distribution_report()
        """
        from pathlib import Path

        from ..reporting.distribution_report import DistributionReport

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_distribution_analysis.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = DistributionReport(**kwargs)
        report_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Distribution report generated: {report_path}")
        return report_path

    def generate_describe_profiler_report(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate describe profiler report with PySpark statistics.

        This method creates statistical profiling using PySpark's describe()
        with checkpoint tracking.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_describe_profiler_report()
        """
        from pathlib import Path

        from ..reporting.describe_report import DescribeProfilerReport

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_describe_profiles.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = DescribeProfilerReport(**kwargs)
        report_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Describe profiler report generated: {report_path}")
        return report_path

    def export_lineage_json(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Export lineage graph as JSON for programmatic access.

        This method exports the complete lineage graph structure in JSON format
        for external tools and analysis.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options for GraphJsonExportConfig.

        Returns:
            Path to generated JSON file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> json_path = result_df.export_lineage_json()
        """
        from pathlib import Path

        from ..reporting.graph_json_export import GraphJsonExporter

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_lineage.json"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate JSON export
        exporter = GraphJsonExporter(**kwargs)
        json_path = exporter.export(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Lineage JSON exported: {json_path}")
        return json_path

    def generate_expression_documentation(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate expression documentation report (when expression lineage available).

        This method documents derived column expressions and their lineage.
        Note: Requires @expressionLineage decorator for full functionality.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated report file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> report_path = result_df.generate_expression_documentation()
        """
        from pathlib import Path

        from ..reporting.expression_documentation import ExpressionDocumentationReport

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_expression_documentation.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate report
        generator = ExpressionDocumentationReport(**kwargs)
        report_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Expression documentation generated: {report_path}")
        return report_path

    def generate_expression_impact_diagram(
        self,
        pipeline_name: Optional[str] = None,
        output_path: str = "./",
        **kwargs
    ) -> str:
        """
        Generate expression impact diagram (when expression lineage available).

        This method creates a visual diagram showing expression dependencies
        and column lineage. Note: Requires @expressionLineage decorator.

        Args:
            pipeline_name: Name of the pipeline. Defaults to script filename.
            output_path: Directory or file path for output. Defaults to current directory.
            **kwargs: Additional configuration options.

        Returns:
            Path to generated diagram file.

        Example:
            >>> result_df = pipeline.transform(source_df)
            >>> diagram_path = result_df.generate_expression_impact_diagram()
        """
        from pathlib import Path

        from ..reporting.expression_impact_diagram import ExpressionImpactDiagram

        # Auto-detect pipeline name if not provided
        if pipeline_name is None:
            pipeline_name = self._auto_detect_pipeline_name()

        # Access lineage tracker and graph
        from ..core.lineage_tracker import get_global_tracker
        tracker = get_global_tracker()
        lineage_graph = tracker.get_lineage_graph()

        # Determine output file path
        output_path_obj = Path(output_path)
        if output_path_obj.is_dir() or str(output_path).endswith(('/', '\\')):
            output_path_obj.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj / f"{pipeline_name}_expression_impact.md"
        else:
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            report_file = output_path_obj

        # Generate diagram
        generator = ExpressionImpactDiagram(**kwargs)
        diagram_path = generator.generate(
            lineage_graph=lineage_graph,
            output_path=str(report_file)
        )

        logger.info(f"Expression impact diagram generated: {diagram_path}")
        return diagram_path

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"LineageDataFrame(lineage_id={self._lineage_id.id}, label={self._business_label})"


def wrap_dataframe(
    df: DataFrame,
    business_label: Optional[str] = None,
    auto_infer: bool = True,
    materialize: bool = True,
    track_columns: Optional[List[str]] = None,
    auto_cache: bool = False,
    cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
    cache_threshold: int = 2,
) -> LineageDataFrame:
    """
    Convenience function to wrap a PySpark DataFrame for lineage tracking.

    Args:
        df: PySpark DataFrame to wrap
        business_label: Optional business-friendly label
        auto_infer: Enable automatic business context inference
        materialize: Whether to compute row counts
        track_columns: Specific columns to track for distinct counts
        auto_cache: Enable automatic caching based on materialization count
        cache_storage_level: Storage level for caching
        cache_threshold: Number of materializations before auto-caching

    Returns:
        LineageDataFrame wrapper

    Example:
        >>> from pyspark_storydoc import wrap_dataframe
        >>> tracked_df = wrap_dataframe(df, "Customer Data")
        >>> high_value = tracked_df.filter(col('ltv') > 10000)  # Automatically tracked
    """
    # Create LineageDataFrame
    # The LineageDataFrame constructor will handle SOURCE operation creation
    lineage_df = LineageDataFrame(
        dataframe=df,
        business_label=business_label,
        materialize=materialize,
        track_columns=track_columns
    )

    return lineage_df