"""Context managers for business lineage tracking."""

import logging
import weakref
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

from pyspark.storagelevel import StorageLevel

from ..utils.dataframe_utils import generate_lineage_id
from ..utils.exceptions import LineageTrackingError
from ..utils.validation import validate_business_concept_name, validate_description
from .graph_builder import ContextGroupNode
from .lineage_tracker import get_enhanced_tracker as get_tracker

logger = logging.getLogger(__name__)


class BusinessConceptContext:
    """Enhanced context manager that auto-tracks LineageDataFrame operations."""

    def __init__(self, name: str, description: Optional[str] = None,
                 track_columns: Optional[List[str]] = None,
                 materialize: bool = True, metadata: Optional[Dict[str, Any]] = None,
                 auto_cache: bool = False, cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
                 cache_threshold: int = 2):
        self.name = name
        self.description = description
        self.track_columns = track_columns or []
        self.materialize = materialize
        self.metadata = metadata or {}
        self.auto_cache = auto_cache
        self.cache_storage_level = cache_storage_level
        self.cache_threshold = cache_threshold

        # Track operations within this context
        self.tracked_operations: List[weakref.ref] = []
        self.final_result = None
        self.context_node = None

    def __enter__(self):
        """Enter the business concept context."""
        # Validate inputs
        validate_business_concept_name(self.name)
        validate_description(self.description)

        # Generate unique ID for this context
        context_id = generate_lineage_id()

        # Create business concept node (not context group node)
        from .graph_builder import BusinessConceptNode
        self.context_node = BusinessConceptNode(
            node_id=context_id,
            name=self.name,
            description=self.description,
            track_columns=self.track_columns,
            materialize=self.materialize,
            metadata=self.metadata.copy(),
        )

        # Add business concept specific metadata
        self.context_node.metadata.update({
            'auto_cache': self.auto_cache,
            'cache_storage_level': str(self.cache_storage_level),
            'cache_threshold': self.cache_threshold,
            'context_type': 'business_concept'
        })

        # Get the global tracker and start concept context
        self.tracker = get_tracker()
        self.tracker_context = self.tracker.concept_context(self.context_node)
        self.concept_node = self.tracker_context.__enter__()

        logger.info(f"Started business concept context: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the business concept context."""
        try:
            # Auto-detect the final result if not explicitly set
            if self.final_result is None:
                self._auto_detect_final_result()

            # Apply business concept settings to final result if it exists
            if self.final_result is not None:
                self._apply_business_concept_settings()

            logger.info(f"Completed business concept context: {self.name}")
        finally:
            # Always exit the tracker context
            self.tracker_context.__exit__(exc_type, exc_val, exc_tb)

    def set_result(self, dataframe):
        """Explicitly set the result DataFrame (backward compatibility)."""
        from .lineage_dataframe import LineageDataFrame

        if isinstance(dataframe, LineageDataFrame):
            self.final_result = dataframe
        else:
            # Wrap if needed
            self.final_result = LineageDataFrame(
                dataframe,
                business_label=self.name,
                track_columns=self.track_columns,
                materialize=self.materialize,
                auto_cache=self.auto_cache,
                cache_storage_level=self.cache_storage_level,
                cache_threshold=self.cache_threshold,
            )

    def _auto_detect_final_result(self):
        """Auto-detect the final result by monitoring operations within this context."""
        from .lineage_dataframe import LineageDataFrame

        # Get operations that were added to this business concept
        if self.context_node and hasattr(self.context_node, 'technical_operations'):
            operations = self.context_node.technical_operations

            if operations:
                # Find the most recent operation that produces a result
                # This will be our final result
                latest_operation = max(operations, key=lambda op: getattr(op, 'created_at', 0))

                # Create a LineageDataFrame representing the result of this context
                # For auto-detection, we'll create a conceptual final result
                logger.debug(f"Auto-detected final operation: {latest_operation.business_context}")

                # The final result will be captured by the tracker context
                # No need to explicitly set self.final_result as the tracker handles it

    def _apply_business_concept_settings(self):
        """Apply business concept settings to the final result."""
        if self.final_result is None:
            return

        # Update the DataFrame's business label and settings
        if hasattr(self.final_result, '_business_label'):
            self.final_result._business_label = self.name

        # Apply caching settings if specified
        if self.auto_cache and hasattr(self.final_result, 'enable_auto_cache'):
            self.final_result.enable_auto_cache(
                cache_threshold=self.cache_threshold,
                storage_level=self.cache_storage_level
            )


@contextmanager
def business_concept(name: str, description: Optional[str] = None,
                    track_columns: Optional[List[str]] = None,
                    materialize: bool = True, metadata: Optional[Dict[str, Any]] = None,
                    auto_cache: bool = False,
                    cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
                    cache_threshold: int = 2) -> Generator[BusinessConceptContext, None, None]:
    """
    Enhanced context manager for business concepts with auto-detection of results.

    This context manager automatically tracks LineageDataFrame operations within its scope
    and applies business concept settings without requiring explicit set_result() calls.

    Args:
        name: Business name for this concept
        description: Detailed explanation for stakeholders
        track_columns: Specific columns to track for distinct counts
        materialize: Whether to compute row counts and metrics
        metadata: Additional context information
        auto_cache: Enable automatic caching based on materialization count
        cache_storage_level: Storage level for caching
        cache_threshold: Number of materializations before auto-caching

    Yields:
        BusinessConceptContext object that can optionally receive explicit results

    Example:
        >>> # Auto-detection (no set_result needed)
        >>> with business_concept("Customer Filtering", track_columns=["customer_id"]):
        ...     active_customers = customers_df.filter(col("status") == "active")
        ...     # Result is automatically detected and tracked

        >>> # Explicit result setting (backward compatibility)
        >>> with business_concept("Payment Analysis") as ctx:
        ...     aggregated = payments_df.groupBy("customer_id").agg(sum("amount"))
        ...     ctx.set_result(aggregated)  # Optional explicit setting
    """
    context = BusinessConceptContext(
        name=name,
        description=description,
        track_columns=track_columns,
        materialize=materialize,
        metadata=metadata,
        auto_cache=auto_cache,
        cache_storage_level=cache_storage_level,
        cache_threshold=cache_threshold
    )

    with context:
        yield context


@contextmanager
def business_context(
    name: str,
    description: Optional[str] = None,
    materialize: Optional[bool] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator[ContextGroupNode, None, None]:
    """
    Context manager to group inline operations under a business concept.

    This allows you to group multiple PySpark operations (filters, joins, etc.)
    under a single business concept without wrapping them in a function.

    Args:
        name: Business name for this group of operations
        description: Detailed explanation for stakeholders
        materialize: Override materialization setting for this context
        metadata: Additional context information

    Yields:
        ContextGroupNode representing this business context

    Raises:
        ValidationError: If parameters are invalid
        LineageTrackingError: If context management fails

    Example:
        >>> with business_context("Premium Customer Identification"):
        ...     high_value = df.filter(col('customer_lifetime_value') > 10000)
        ...     premium_tier = high_value.filter(col('account_tier') == 'premium')
        ...     active_premium = premium_tier.filter(col('account_status') == 'active')

        >>> with business_context("Geographic Segmentation",
        ...                      description="Filter customers by region for targeted campaigns"):
        ...     na_customers = df.filter(col('region') == 'North America')
        ...     with_demographics = na_customers.join(demographics, 'customer_id')
    """
    # Validate inputs
    validate_business_concept_name(name)
    validate_description(description)

    if materialize is not None and not isinstance(materialize, bool):
        raise LineageTrackingError(
            "materialize parameter must be a boolean",
            operation_type="context_manager"
        )

    # Generate unique ID for this context
    context_id = generate_lineage_id()

    # Create context group node
    context_node = ContextGroupNode(
        node_id=context_id,
        name=name,
        description=description,
        metadata=metadata or {},
    )

    # Set materialization override if provided
    if materialize is not None:
        context_node.metadata['materialize_override'] = materialize

    # Get the global tracker
    tracker = get_tracker()

    try:
        # Use the tracker's context group manager
        with tracker.context_group(context_node) as group_node:
            logger.info(f"Started business context: {name}")
            yield group_node
            logger.info(f"Completed business context: {name}")

    except Exception as e:
        logger.error(f"Error in business context '{name}': {e}")
        # Re-raise as LineageTrackingError if it's not already one
        if not isinstance(e, LineageTrackingError):
            raise LineageTrackingError(
                f"Failed to manage business context '{name}': {e}",
                operation_type="context_manager"
            )
        raise


@contextmanager
def performance_context(
    materialize: bool = False,
    name: Optional[str] = None,
) -> Generator[ContextGroupNode, None, None]:
    """
    Context manager optimized for performance with large datasets.

    This context disables materialization by default to handle
    very large datasets efficiently.

    Args:
        materialize: Whether to materialize (disabled by default for performance)
        name: Optional name for the context

    Yields:
        ContextGroupNode representing this performance context

    Example:
        >>> with performance_context(name="Large Dataset Processing"):
        ...     # Operations on very large datasets without materialization
        ...     filtered = large_df.filter(col('status') == 'active')
        ...     aggregated = filtered.groupBy('region').count()
    """
    context_name = name or "Performance Context"

    metadata = {
        'context_type': 'performance',
        'materialize_override': materialize,
        'performance_optimized': True,
    }

    with business_context(
        name=context_name,
        description="Performance-optimized context with disabled materialization",
        materialize=materialize,
        metadata=metadata,
    ) as context_node:
        yield context_node


@contextmanager
def debug_context(
    name: str,
    verbose: bool = True,
    capture_intermediate: bool = True,
) -> Generator[ContextGroupNode, None, None]:
    """
    Context manager for debugging business operations.

    This context provides enhanced logging and captures intermediate
    results for debugging purposes.

    Args:
        name: Name for the debug context
        verbose: Enable verbose logging
        capture_intermediate: Capture intermediate DataFrame info

    Yields:
        ContextGroupNode representing this debug context

    Example:
        >>> with debug_context("Customer Filtering Debug"):
        ...     # All operations will be logged in detail
        ...     active = df.filter(col('status') == 'active')
        ...     high_value = active.filter(col('ltv') > 10000)
    """
    # Set up enhanced logging for this context
    if verbose:
        debug_logger = logging.getLogger(__name__)
        original_level = debug_logger.level
        debug_logger.setLevel(logging.DEBUG)
    else:
        debug_logger = None
        original_level = None

    metadata = {
        'context_type': 'debug',
        'verbose': verbose,
        'capture_intermediate': capture_intermediate,
        'debug_enabled': True,
    }

    try:
        with business_context(
            name=f"DEBUG: {name}",
            description=f"Debug context for {name}",
            materialize=True,  # Always materialize in debug mode
            metadata=metadata,
        ) as context_node:
            if verbose:
                logger.info(f"Started debug context: {name}")

            yield context_node

            if verbose:
                logger.info(f"Completed debug context: {name}")

    finally:
        # Restore original logging level
        if debug_logger and original_level is not None:
            debug_logger.setLevel(original_level)


@contextmanager
def audit_context(
    name: str,
    auditor: Optional[str] = None,
    compliance_tags: Optional[list] = None,
) -> Generator[ContextGroupNode, None, None]:
    """
    Context manager for audit and compliance tracking.

    This context captures detailed information required for
    audit trails and compliance reporting.

    Args:
        name: Name for the audit context
        auditor: Name of person performing the audit
        compliance_tags: Tags for compliance categorization

    Yields:
        ContextGroupNode representing this audit context

    Example:
        >>> with audit_context("GDPR Customer Data Processing",
        ...                   auditor="John Doe",
        ...                   compliance_tags=["GDPR", "PII"]):
        ...     # All operations tracked for compliance
        ...     filtered_data = df.filter(col('consent') == True)
        ...     anonymized = filtered_data.drop('personal_email')
    """
    import getpass
    import time

    # Get current user if auditor not specified
    if auditor is None:
        try:
            auditor = getpass.getuser()
        except Exception:
            auditor = "Unknown"

    metadata = {
        'context_type': 'audit',
        'auditor': auditor,
        'compliance_tags': compliance_tags or [],
        'audit_timestamp': time.time(),
        'audit_enabled': True,
        'requires_approval': True,
    }

    with business_context(
        name=f"AUDIT: {name}",
        description=f"Audit context for {name} (Auditor: {auditor})",
        materialize=True,  # Always materialize for audit trail
        metadata=metadata,
    ) as context_node:
        logger.info(f"Started audit context: {name} (Auditor: {auditor})")
        yield context_node
        logger.info(f"Completed audit context: {name}")


@contextmanager
def temporary_context(
    materialize: bool = False,
    name: Optional[str] = None,
) -> Generator[ContextGroupNode, None, None]:
    """
    Context manager for temporary operations that shouldn't be tracked permanently.

    This is useful for exploratory data analysis or temporary transformations
    that don't represent permanent business logic.

    Args:
        materialize: Whether to materialize (disabled by default)
        name: Optional name for the context

    Yields:
        ContextGroupNode representing this temporary context

    Example:
        >>> with temporary_context(name="Exploratory Analysis"):
        ...     # Temporary exploration that won't clutter main lineage
        ...     sample_data = df.sample(0.1)
        ...     quick_stats = sample_data.describe()
    """
    context_name = name or "Temporary Operations"

    metadata = {
        'context_type': 'temporary',
        'temporary': True,
        'exclude_from_reports': True,
        'materialize_override': materialize,
    }

    with business_context(
        name=f"TEMP: {context_name}",
        description="Temporary context for exploratory operations",
        materialize=materialize,
        metadata=metadata,
    ) as context_node:
        yield context_node


def get_current_business_context() -> Optional[str]:
    """
    Get the name of the current business context.

    Returns:
        Name of current context or None if no context is active
    """
    tracker = get_tracker()
    current_context = tracker.get_current_context()

    if current_context:
        return current_context.name
    return None


def is_in_business_context() -> bool:
    """
    Check if we're currently inside a business context.

    Returns:
        True if inside a business context, False otherwise
    """
    return get_current_business_context() is not None


def get_context_metadata() -> Optional[Dict[str, Any]]:
    """
    Get metadata for the current business context.

    Returns:
        Context metadata or None if no context is active
    """
    tracker = get_tracker()
    current_context = tracker.get_current_context()

    if current_context:
        return current_context.metadata.copy()
    return None