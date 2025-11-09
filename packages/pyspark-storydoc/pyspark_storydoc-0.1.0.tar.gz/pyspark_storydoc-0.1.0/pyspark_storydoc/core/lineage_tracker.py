"""Unified lineage tracker with immutable lineage support, fork and merge handling."""

import logging
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Union

from ..utils.dataframe_utils import extract_dataframes, safe_count, safe_distinct_count
from ..utils.exceptions import ConfigurationError, LineageTrackingError
from ..utils.validation import (
    validate_materialize_setting,
    validate_track_columns,
)
from .enhanced_lineage_graph import EnhancedLineageGraph
from .execution_context import (
    ExecutionContext,
    ExecutionContextManager,
    get_context_manager,
)
from .fork_detector import ForkDetector, ForkStatus, get_fork_detector
from .graph_builder import (
    BaseLineageNode,
    BusinessConceptNode,
    ContextGroupNode,
    LineageEdge,
    MetricsData,
    OperationNode,
)
from .lineage_id import LineageID, LineageIDTracker

logger = logging.getLogger(__name__)


class LineageTracker:
    """
    Unified lineage tracker with immutable lineage support, fork and merge handling.

    This tracker provides comprehensive lineage tracking with:
    - Immutable LineageID tracking
    - Fork pattern detection and handling
    - Merge pattern detection and handling
    - Multiple parent relationships (joins/unions)
    - Context-aware execution tracking
    - Zero-overhead mode for production
    - Business concept grouping and visualization
    """

    def __init__(
        self,
        auto_infer_context: bool = True,
        materialize_by_default: bool = True,
        default_track_columns: Optional[List[str]] = None,
        graph_name: Optional[str] = None,
        enable_fork_detection: bool = True,
        zero_overhead_mode: bool = False,
        track_row_count_level: str = "business_concept",
    ):
        """
        Initialize the enhanced lineage tracker.

        Args:
            auto_infer_context: Enable automatic business context inference
            materialize_by_default: Whether to materialize by default
            default_track_columns: Default columns to track
            graph_name: Name for the lineage graph
            enable_fork_detection: Enable fork pattern detection
            zero_overhead_mode: Disable all tracking for production use
            track_row_count_level: Row count tracking granularity - "business_concept" or "operation"
        """
        # Validate inputs
        validate_materialize_setting(materialize_by_default)
        if default_track_columns is not None:
            validate_track_columns(default_track_columns)

        # Validate track_row_count_level
        if track_row_count_level not in ["business_concept", "operation"]:
            raise ValueError(f"Invalid track_row_count_level: {track_row_count_level}. Must be 'business_concept' or 'operation'")

        self.auto_infer_context = auto_infer_context
        self.materialize_by_default = materialize_by_default
        self.default_track_columns = default_track_columns or []
        self.enable_fork_detection = enable_fork_detection
        self.zero_overhead_mode = zero_overhead_mode
        self.track_row_count_level = track_row_count_level

        # Enhanced tracking components
        self.enhanced_graph = EnhancedLineageGraph(graph_name)
        self.lineage_id_tracker = LineageIDTracker()
        self.context_manager = get_context_manager()
        self.fork_detector = get_fork_detector() if enable_fork_detection else None


        # Thread-local storage for concurrent execution
        self._local = threading.local()

        # Pipeline tracking
        self._pipeline_name: Optional[str] = None
        self._pipeline_active = False

        # Merge operation tracking
        self._merge_modes: Dict[str, bool] = {}  # context_id -> merge_mode

        # Inference engine (will be set by dependency injection)
        self._inference_engine = None

        # Performance tracking
        self._tracking_enabled = not zero_overhead_mode

        logger.debug(f"Initialized EnhancedLineageTracker with graph: {graph_name}")

    @property
    def inference_engine(self):
        """Get the inference engine, initializing if needed."""
        if self._inference_engine is None:
            from ..inference.engine import BusinessInferenceEngine
            self._inference_engine = BusinessInferenceEngine()
        return self._inference_engine

    @inference_engine.setter
    def inference_engine(self, engine):
        """Set the inference engine."""
        self._inference_engine = engine

    def should_track(self) -> bool:
        """Check if tracking should be performed."""
        return self._tracking_enabled and not self.zero_overhead_mode

    def should_materialize(self) -> bool:
        """Check if materialization should be performed."""
        return self.should_track() and self.materialize_by_default

    def register_lineage_id(self, lineage_id: LineageID, context: ExecutionContext = None) -> None:
        """Register a new LineageID with the tracking system."""
        if not self.should_track():
            return

        # Register with LineageID tracker
        self.lineage_id_tracker.register(lineage_id)

        # Add to enhanced graph
        node = self.enhanced_graph.add_lineage_node(lineage_id, context)

        # Register parent relationships
        for parent_id in lineage_id.parent_ids:
            self.enhanced_graph.add_lineage_relationship(
                parent_lineage_id=parent_id,
                child_lineage_id=lineage_id.id,
                context_id=context.context_id if context else lineage_id.context_id
            )

        # Handle multiple parents (merge points)
        if len(lineage_id.parent_ids) > 1:
            self.enhanced_graph.add_merge_point(lineage_id.id, lineage_id.parent_ids)

        logger.debug(f"Registered LineageID: {lineage_id.id}")

    def register_fork_consumption(self, lineage_id: str, context_id: str, operation: str = None) -> ForkStatus:
        """Register that a LineageID is being consumed and detect forks."""
        if not self.should_track() or not self.fork_detector:
            return ForkStatus.NORMAL

        # Register with fork detector
        fork_status = self.fork_detector.register_consumer(lineage_id, context_id, operation)

        # If fork detected, update enhanced graph
        if fork_status == ForkStatus.FORK_DETECTED:
            fork_point = self.fork_detector.get_fork_point(lineage_id)
            if fork_point:
                self.enhanced_graph.add_fork_point(fork_point)

        return fork_status

    def register_business_concept(self, concept_node: BusinessConceptNode) -> None:
        """Register a business concept with the lineage graph."""
        if not self.should_track():
            return

        try:
            # Get current context for this business concept
            context_manager = get_context_manager()
            current_context = context_manager.get_current_context()

            # Create enhanced node with context
            enhanced_node = self.enhanced_graph.add_lineage_node(
                lineage_id=LineageID(
                    id=concept_node.node_id,
                    operation_id=concept_node.node_id,
                    operation_type="business_concept"
                ),
                context=current_context
            )

            # CRITICAL: Add business concept metadata to the node for catalog extraction
            # The catalog looks for 'business_context' or 'operation_name' + 'operation_type'
            enhanced_node.metadata['business_context'] = concept_node.name
            enhanced_node.metadata['operation_name'] = concept_node.name
            enhanced_node.metadata['description'] = concept_node.description or ''
            enhanced_node.metadata['execution_time'] = concept_node.execution_time or 0
            enhanced_node.metadata['track_columns'] = concept_node.track_columns

            # Add governance metadata if present
            if hasattr(concept_node, 'governance_metadata') and concept_node.governance_metadata:
                enhanced_node.metadata['governance_metadata'] = concept_node.governance_metadata

            # Merge any additional metadata from the concept_node
            if concept_node.metadata:
                for key, value in concept_node.metadata.items():
                    if key not in enhanced_node.metadata:
                        enhanced_node.metadata[key] = value

            # Also ensure the business concept node is in context_nodes for catalog extraction
            if concept_node.node_id not in self.enhanced_graph.context_nodes:
                self.enhanced_graph.context_nodes[concept_node.node_id] = []

            # Add the node to its own context for business catalog extraction
            if enhanced_node not in self.enhanced_graph.context_nodes[concept_node.node_id]:
                self.enhanced_graph.context_nodes[concept_node.node_id].append(enhanced_node)

            logger.debug(f"Registered business concept: {concept_node.name} in context {concept_node.node_id}")

        except Exception as e:
            raise LineageTrackingError(
                f"Failed to register business concept '{concept_node.name}': {e}",
                operation_type="register_concept"
            )

    def update_node_metrics(self, node_id: str, timing: Optional[float] = None,
                           metrics: Optional[MetricsData] = None,
                           input_metrics: Optional[MetricsData] = None,
                           operation_description: Optional[str] = None,
                           operation_name: Optional[str] = None) -> None:
        """Update a node with timing and metrics information."""
        if not self.should_track():
            return

        try:
            # Find the node in the enhanced graph
            node = None
            for node_candidate in self.enhanced_graph.nodes.values():
                if node_candidate.node_id == node_id or node_candidate.lineage_id == node_id:
                    node = node_candidate
                    break

            if not node:
                logger.warning(f"Node {node_id} not found for metrics update")
                return

            # Update timing information
            if timing is not None:
                node.metadata['duration'] = timing
                node.metadata['computation_time'] = timing
                node.metadata['execution_time'] = timing

            # Initialize metrics dict if needed
            if 'metrics' not in node.metadata:
                node.metadata['metrics'] = {}

            # Update input metrics information
            if input_metrics:
                node.metadata['metrics']['input_record_count'] = input_metrics.row_count
                if input_metrics.distinct_counts:
                    if 'distinct_counts' not in node.metadata['metrics']:
                        node.metadata['metrics']['distinct_counts'] = {}
                    for col, count in input_metrics.distinct_counts.items():
                        node.metadata['metrics']['distinct_counts'][col] = {'input': count}

            # Update output metrics information (from 'metrics' parameter)
            if metrics:
                node.metadata['metrics']['output_record_count'] = metrics.row_count
                node.metadata['metrics']['row_count'] = metrics.row_count  # Backward compat
                node.metadata['metrics']['column_count'] = metrics.column_count
                node.metadata['metrics']['estimated'] = metrics.estimated

                if metrics.distinct_counts:
                    if 'distinct_counts' not in node.metadata['metrics']:
                        node.metadata['metrics']['distinct_counts'] = {}
                    for col, count in metrics.distinct_counts.items():
                        if col not in node.metadata['metrics']['distinct_counts']:
                            node.metadata['metrics']['distinct_counts'][col] = {}
                        node.metadata['metrics']['distinct_counts'][col]['output'] = count

                if metrics.computation_time:
                    node.metadata['metrics']['computation_time'] = metrics.computation_time

                # CRITICAL: If this is a business concept node, propagate metrics to child operation nodes
                if node.metadata.get('operation_type') == 'business_concept':
                    # Find all operation nodes that are children of this business concept
                    # by looking for nodes in context_nodes
                    if node_id in self.enhanced_graph.context_nodes:
                        for child_node in self.enhanced_graph.context_nodes[node_id]:
                            # Only propagate to operation nodes, not to other business concepts
                            if (child_node.metadata.get('operation_type') not in ['business_concept', 'source'] and
                                child_node.node_id != node_id):
                                if 'metrics' not in child_node.metadata:
                                    child_node.metadata['metrics'] = {}
                                # Use input_metrics for input, metrics for output
                                child_node.metadata['metrics']['input_record_count'] = input_metrics.row_count if input_metrics else node.metadata['metrics'].get('input_record_count', 0)
                                child_node.metadata['metrics']['output_record_count'] = metrics.row_count
                                child_node.metadata['metrics']['row_count'] = metrics.row_count

            # Update operation description
            if operation_description:
                node.metadata['description'] = operation_description

            # Update operation name
            if operation_name:
                node.metadata['operation_name'] = operation_name

            logger.debug(f"Updated metrics for node {node_id}")

        except Exception as e:
            logger.warning(f"Failed to update node metrics for {node_id}: {e}")

    def add_operation(self, operation_node: OperationNode, parent_node_id: Optional[str] = None) -> None:
        """Add an operation to the current context (legacy compatibility)."""
        if not self.should_track():
            return

        # Delegate to multi-parent method for consistency
        parent_ids = [parent_node_id] if parent_node_id else []
        self.add_operation_with_parents(operation_node, parent_ids)

    def add_operation_with_parents(self, operation_node: OperationNode, parent_node_ids: List[str]) -> None:
        """Add an operation with multiple parents (for joins/unions)."""
        if not self.should_track():
            return

        try:
            # Extract LineageID information from operation metadata if available
            lineage_id = operation_node.metadata.get('lineage_id')
            parent_lineage_id = operation_node.metadata.get('parent_lineage_id')
            parent_lineage_ids = operation_node.metadata.get('parent_lineage_ids', [])

            logger.debug(f"add_operation_with_parents: operation={operation_node.name}, lineage_id={lineage_id}")
            logger.debug(f"  parent_lineage_id={parent_lineage_id}, parent_lineage_ids={parent_lineage_ids}")
            logger.debug(f"  lineage_nodes keys: {list(self.enhanced_graph.lineage_nodes.keys())[:10]}")  # Show first 10

            # Support both single-parent (parent_lineage_id) and multi-parent (parent_lineage_ids) operations
            if lineage_id and (parent_lineage_id or parent_lineage_ids):
                # Add lineage relationship to enhanced graph
                self.enhanced_graph.add_lineage_relationship(
                    parent_lineage_id=parent_lineage_id,
                    child_lineage_id=lineage_id,
                    context_id=None  # Context is managed at business concept level
                )

                # Update the lineage node's metadata with operation-specific details
                if lineage_id in self.enhanced_graph.lineage_nodes:
                    logger.debug(f"Found lineage node {lineage_id} in lineage_nodes, copying metadata from operation_node")
                    logger.debug(f"operation_node.metadata keys: {list(operation_node.metadata.keys())}")
                    node = self.enhanced_graph.lineage_nodes[lineage_id]
                    logger.debug(f"Lineage node details: node_id={node.node_id}, lineage_id={node.lineage_id}")
                    logger.debug(f"Is this node also in enhanced_graph.nodes? {node.node_id in self.enhanced_graph.nodes}")
                    if node.node_id in self.enhanced_graph.nodes:
                        logger.debug(f"Same object? {self.enhanced_graph.nodes[node.node_id] is node}")
                    # Merge operation metadata (filter_condition, selected_columns, etc.)
                    for key, value in operation_node.metadata.items():
                        if key not in ['lineage_id', 'parent_lineage_id']:  # Skip these keys
                            node.metadata[key] = value
                            logger.debug(f"Copied {key} = {value}")

                    # CRITICAL: Transfer metrics from OperationNode to lineage node metadata
                    if hasattr(operation_node, 'before_metrics') and operation_node.before_metrics:
                        if 'metrics' not in node.metadata:
                            node.metadata['metrics'] = {}
                        # Store before metrics as input counts
                        before = operation_node.before_metrics
                        if isinstance(before, dict):
                            node.metadata['metrics']['input_record_count'] = before.get('row_count')
                            # Store input distinct counts
                            if 'distinct_counts' in before:
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in before['distinct_counts'].items():
                                    node.metadata['metrics']['distinct_counts'][col] = {'input': count}
                        elif hasattr(before, 'row_count'):
                            node.metadata['metrics']['input_record_count'] = before.row_count
                            if hasattr(before, 'distinct_counts'):
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in before.distinct_counts.items():
                                    node.metadata['metrics']['distinct_counts'][col] = {'input': count}

                    if hasattr(operation_node, 'after_metrics') and operation_node.after_metrics:
                        if 'metrics' not in node.metadata:
                            node.metadata['metrics'] = {}
                        # Store after metrics as output counts
                        after = operation_node.after_metrics
                        if isinstance(after, dict):
                            node.metadata['metrics']['output_record_count'] = after.get('row_count')
                            node.metadata['metrics']['row_count'] = after.get('row_count')  # Backward compat
                            # Store output distinct counts
                            if 'distinct_counts' in after:
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in after['distinct_counts'].items():
                                    if col not in node.metadata['metrics']['distinct_counts']:
                                        node.metadata['metrics']['distinct_counts'][col] = {}
                                    node.metadata['metrics']['distinct_counts'][col]['output'] = count
                        elif hasattr(after, 'row_count'):
                            node.metadata['metrics']['output_record_count'] = after.row_count
                            node.metadata['metrics']['row_count'] = after.row_count  # Backward compat
                            if hasattr(after, 'distinct_counts'):
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in after.distinct_counts.items():
                                    if col not in node.metadata['metrics']['distinct_counts']:
                                        node.metadata['metrics']['distinct_counts'][col] = {}
                                    node.metadata['metrics']['distinct_counts'][col]['output'] = count

                    # Inherit governance metadata from parent business concept if available
                    current_context = self.context_manager.get_current_context()
                    if current_context and current_context.context_id:
                        # Look for the business concept node for this context
                        for potential_concept in self.enhanced_graph.nodes.values():
                            if (potential_concept.node_id == current_context.context_id and
                                potential_concept.metadata.get('operation_type') == 'business_concept'):
                                # Found the parent business concept - copy governance metadata
                                governance_metadata = potential_concept.metadata.get('governance_metadata')
                                if governance_metadata:
                                    # Store in business_context dict for easy access
                                    if 'business_context' not in node.metadata:
                                        node.metadata['business_context'] = {}
                                    if not isinstance(node.metadata['business_context'], dict):
                                        node.metadata['business_context'] = {'name': node.metadata['business_context']}
                                    node.metadata['business_context']['governance_metadata'] = governance_metadata
                                    logger.debug(f"Inherited governance metadata from concept {current_context.context_id} to operation {lineage_id}")
                                break

                    logger.debug(f"Final node metadata keys after copy: {list(node.metadata.keys())}")
                else:
                    logger.warning(f"Lineage ID {lineage_id} NOT found in lineage_nodes!")

                    # Transfer metrics from OperationNode to lineage node metadata
                    if hasattr(operation_node, 'before_metrics') and operation_node.before_metrics:
                        if 'metrics' not in node.metadata:
                            node.metadata['metrics'] = {}
                        # Store before metrics as input counts
                        before = operation_node.before_metrics
                        if isinstance(before, dict):
                            node.metadata['metrics']['input_record_count'] = before.get('row_count')
                            # Store input distinct counts
                            if 'distinct_counts' in before:
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in before['distinct_counts'].items():
                                    node.metadata['metrics']['distinct_counts'][col] = {'input': count}
                        elif hasattr(before, 'row_count'):
                            node.metadata['metrics']['input_record_count'] = before.row_count
                            if hasattr(before, 'distinct_counts'):
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in before.distinct_counts.items():
                                    node.metadata['metrics']['distinct_counts'][col] = {'input': count}

                    if hasattr(operation_node, 'after_metrics') and operation_node.after_metrics:
                        if 'metrics' not in node.metadata:
                            node.metadata['metrics'] = {}
                        # Store after metrics as output counts
                        after = operation_node.after_metrics
                        if isinstance(after, dict):
                            node.metadata['metrics']['output_record_count'] = after.get('row_count')
                            # Store output distinct counts
                            if 'distinct_counts' in after:
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in after['distinct_counts'].items():
                                    if col not in node.metadata['metrics']['distinct_counts']:
                                        node.metadata['metrics']['distinct_counts'][col] = {}
                                    node.metadata['metrics']['distinct_counts'][col]['output'] = count
                        elif hasattr(after, 'row_count'):
                            node.metadata['metrics']['output_record_count'] = after.row_count
                            if hasattr(after, 'distinct_counts'):
                                if 'distinct_counts' not in node.metadata['metrics']:
                                    node.metadata['metrics']['distinct_counts'] = {}
                                for col, count in after.distinct_counts.items():
                                    if col not in node.metadata['metrics']['distinct_counts']:
                                        node.metadata['metrics']['distinct_counts'][col] = {}
                                    node.metadata['metrics']['distinct_counts'][col]['output'] = count

            logger.debug(f"Added operation: {operation_node.name} with {len(parent_node_ids)} parents")

        except Exception as e:
            raise LineageTrackingError(
                f"Failed to add operation '{operation_node.name}': {e}",
                operation_type=operation_node.operation_type.value
            )

    def capture_metrics(
        self,
        dataframes: List,
        track_columns: Optional[List[str]] = None,
    ) -> Optional[MetricsData]:
        """Capture metrics from DataFrames."""
        if not self.should_materialize() or not dataframes:
            return None

        # Use defaults if not specified
        if track_columns is None:
            track_columns = self.default_track_columns

        try:
            df = dataframes[0]  # Primary DataFrame

            # Get row count
            row_count = safe_count(df)

            # Get distinct counts for tracked columns
            distinct_counts = {}
            for col_name in track_columns:
                if col_name in df.columns:
                    distinct_counts[col_name] = safe_distinct_count(df, col_name)

            return MetricsData(
                row_count=row_count,
                distinct_counts=distinct_counts,
                column_count=len(df.columns),
                estimated=False,
            )

        except Exception as e:
            logger.warning(f"Failed to capture metrics: {e}")
            return None


    def get_lineage_graph(self) -> EnhancedLineageGraph:
        """
        Get the enhanced lineage graph containing all tracked operations.

        Returns:
            EnhancedLineageGraph: The complete lineage graph with all tracked operations,
                                 business concepts, and metadata.

        Example:
            >>> tracker = get_global_tracker()
            >>> graph = tracker.get_lineage_graph()
            >>> print(f"Tracked {len(graph.nodes)} operations")
        """
        return self.enhanced_graph

    def get_enhanced_graph(self) -> EnhancedLineageGraph:
        """
        Get the enhanced lineage graph containing all tracked operations.

        .. deprecated:: 1.0.0
            Use :meth:`get_lineage_graph` instead. This method will be removed in version 2.0.0.

        Returns:
            EnhancedLineageGraph: The complete lineage graph.
        """
        import warnings
        warnings.warn(
            "get_enhanced_graph() is deprecated and will be removed in version 2.0.0. "
            "Use get_lineage_graph() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.get_lineage_graph()

    def set_merge_mode(self, enabled: bool, context_id: str) -> None:
        """
        Enable or disable merge mode for a specific context.

        When merge mode is enabled, individual DataFrame operations within
        that context are suppressed from being tracked individually.
        """
        if enabled:
            self._merge_modes[context_id] = True
            logger.debug(f"Enabled merge mode for context {context_id}")
        else:
            self._merge_modes.pop(context_id, None)
            logger.debug(f"Disabled merge mode for context {context_id}")

    def is_merge_mode(self, context_id: str) -> bool:
        """Check if merge mode is enabled for a specific context."""
        return self._merge_modes.get(context_id, False)

    def get_fork_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fork statistics."""
        if not self.fork_detector:
            return {'fork_detection_enabled': False}

        stats = self.fork_detector.get_fork_statistics()
        stats['fork_detection_enabled'] = True
        stats['enhanced_graph_stats'] = self.enhanced_graph.get_statistics()
        return stats

    @contextmanager
    def concept_context(self, concept_node: BusinessConceptNode):
        """Context manager for business concept execution."""
        if not self.should_track():
            # No-op context manager for zero overhead mode
            yield concept_node
            return

        # Use enhanced context management
        with self.context_manager.context(
            function_name=concept_node.name,
            materialization_enabled=concept_node.materialize
        ) as context:
            try:
                concept_node.start_execution()
                logger.debug(f"Started business concept: {concept_node.name}")

                yield concept_node

            finally:
                concept_node.end_execution()
                self.register_business_concept(concept_node)
                logger.debug(f"Completed business concept: {concept_node.name}")

    @contextmanager
    def context_group(self, context_node: ContextGroupNode):
        """Context manager for context group execution (inline operations).

        This is used by the business_context() function for grouping
        inline operations without creating a full business concept.

        Args:
            context_node: ContextGroupNode representing the context

        Yields:
            ContextGroupNode: The context node for this group
        """
        if not self.should_track():
            # No-op context manager for zero overhead mode
            yield context_node
            return

        # Determine materialization setting
        materialize = context_node.metadata.get('materialize_override', self.materialize_by_default)

        # Use enhanced context management
        with self.context_manager.context(
            function_name=context_node.name,
            materialization_enabled=materialize
        ) as context:
            try:
                # Add context group node to enhanced graph similar to business concept
                # Create a lineage node for this context group
                enhanced_node = self.enhanced_graph.add_lineage_node(
                    lineage_id=LineageID(
                        id=context_node.node_id,
                        operation_id=context_node.node_id,
                        operation_type="context_group"
                    ),
                    context=context
                )

                # Add context group metadata
                enhanced_node.metadata['business_context'] = context_node.name
                enhanced_node.metadata['operation_name'] = context_node.name
                enhanced_node.metadata['description'] = context_node.description or ''
                enhanced_node.metadata['operation_type'] = 'context_group'

                # Merge any additional metadata from the context_node
                if context_node.metadata:
                    for key, value in context_node.metadata.items():
                        if key not in enhanced_node.metadata:
                            enhanced_node.metadata[key] = value

                # Ensure context_nodes entry exists for this context
                if context_node.node_id not in self.enhanced_graph.context_nodes:
                    self.enhanced_graph.context_nodes[context_node.node_id] = []

                # Add the node to its own context for catalog extraction
                if enhanced_node not in self.enhanced_graph.context_nodes[context_node.node_id]:
                    self.enhanced_graph.context_nodes[context_node.node_id].append(enhanced_node)

                logger.debug(f"Started context group: {context_node.name}")

                yield context_node

            finally:
                logger.debug(f"Completed context group: {context_node.name}")

    @contextmanager
    def pipeline_context(
        self,
        pipeline_name: str,
        materialize: Optional[bool] = None,
        track_columns: Optional[List[str]] = None,
    ):
        """Context manager for pipeline execution."""
        if not self.should_track():
            # No-op context manager for zero overhead mode
            yield self
            return

        # Validate inputs
        if materialize is not None:
            validate_materialize_setting(materialize)
        if track_columns is not None:
            validate_track_columns(track_columns)

        previous_pipeline = self._pipeline_name
        previous_active = self._pipeline_active

        try:
            self._pipeline_name = pipeline_name
            self._pipeline_active = True

            # Set pipeline-level defaults
            if materialize is not None:
                old_default = self.materialize_by_default
                self.materialize_by_default = materialize

            if track_columns is not None:
                old_columns = self.default_track_columns
                self.default_track_columns = track_columns

            with self.context_manager.context(
                function_name=pipeline_name,
                materialization_enabled=materialize if materialize is not None else self.materialize_by_default
            ):
                logger.info(f"Started pipeline: {pipeline_name}")
                yield self

        finally:
            # Restore previous settings
            if materialize is not None:
                self.materialize_by_default = old_default

            if track_columns is not None:
                self.default_track_columns = old_columns

            self._pipeline_name = previous_pipeline
            self._pipeline_active = previous_active

            logger.info(f"Completed pipeline: {pipeline_name}")

    def enable_zero_overhead_mode(self) -> None:
        """Enable zero-overhead mode for production."""
        self.zero_overhead_mode = True
        self._tracking_enabled = False
        if self.fork_detector:
            self.fork_detector.disable()
        logger.info("Enabled zero-overhead mode")

    def disable_zero_overhead_mode(self) -> None:
        """Disable zero-overhead mode for development."""
        self.zero_overhead_mode = False
        self._tracking_enabled = True
        if self.fork_detector:
            self.fork_detector.enable()
        logger.info("Disabled zero-overhead mode")

    def reset(self) -> None:
        """Reset the tracker state."""
        if not self.should_track():
            return

        self.enhanced_graph.clear()
        self.lineage_id_tracker.clear()
        self.context_manager.clear_all()
        if self.fork_detector:
            self.fork_detector.clear()

        self._pipeline_name = None
        self._pipeline_active = False

        logger.debug("Reset enhanced lineage tracker")

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tracking statistics."""
        base_stats = {
            "tracking_enabled": self._tracking_enabled,
            "zero_overhead_mode": self.zero_overhead_mode,
            "fork_detection_enabled": self.enable_fork_detection,
            "pipeline_active": self._pipeline_active,
            "pipeline_name": self._pipeline_name,
            "auto_infer_enabled": self.auto_infer_context,
            "default_materialize": self.materialize_by_default,
        }

        if self.should_track():
            enhanced_stats = self.enhanced_graph.get_statistics()
            fork_stats = self.get_fork_statistics()
            base_stats.update({
                "enhanced_graph": enhanced_stats,
                "fork_detection": fork_stats
            })

        return base_stats


# Global tracker instance
_global_tracker: Optional[LineageTracker] = None
_tracker_lock = threading.Lock()


def get_tracker() -> LineageTracker:
    """Get the global lineage tracker instance."""
    global _global_tracker

    if _global_tracker is None:
        with _tracker_lock:
            if _global_tracker is None:
                _global_tracker = LineageTracker()
                logger.debug("Created global lineage tracker")

    return _global_tracker


def set_tracker(tracker: LineageTracker) -> None:
    """Set the global lineage tracker instance."""
    global _global_tracker

    with _tracker_lock:
        _global_tracker = tracker
        logger.debug("Set new global lineage tracker")


def reset_tracker() -> None:
    """Reset the global lineage tracker."""
    global _global_tracker

    with _tracker_lock:
        if _global_tracker is not None:
            _global_tracker.reset()
            logger.debug("Reset global lineage tracker")


def enable_zero_overhead_mode() -> None:
    """Enable zero-overhead mode globally."""
    tracker = get_tracker()
    tracker.enable_zero_overhead_mode()


def disable_zero_overhead_mode() -> None:
    """Disable zero-overhead mode globally."""
    tracker = get_tracker()
    tracker.disable_zero_overhead_mode()


def is_tracking_enabled() -> bool:
    """Check if tracking is currently enabled."""
    tracker = get_tracker()
    return tracker.should_track()


# Backward compatibility - single naming convention
def get_enhanced_tracker() -> LineageTracker:
    """
    Get the global lineage tracker instance.

    DEPRECATED: Use get_global_tracker() instead for consistency with public API.
    This alias is maintained for backward compatibility but will be removed in v3.0.
    """
    import warnings
    warnings.warn(
        "get_enhanced_tracker() is deprecated, use get_global_tracker() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return get_tracker()


# Primary public API function
def get_global_tracker() -> LineageTracker:
    """Get the global lineage tracker instance."""
    return get_tracker()