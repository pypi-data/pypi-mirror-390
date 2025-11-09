"""Business Concept Hierarchy - Support for nested business concepts with both decorator and context manager patterns."""

import contextvars
import functools
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, TypeVar

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
from .lineage_dataframe import LineageDataFrame
from .lineage_id import LineageID
from .lineage_tracker import get_enhanced_tracker

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])

# Context variable to track the current hierarchy of business concepts
# This is thread-safe and async-safe (Python 3.7+)
_concept_hierarchy_stack: contextvars.ContextVar[List[Dict[str, Any]]] = contextvars.ContextVar(
    '_concept_hierarchy_stack',
    default=[]
)


def _get_current_hierarchy() -> List[Dict[str, Any]]:
    """Get the current hierarchy stack."""
    stack = _concept_hierarchy_stack.get()
    # Return a copy to prevent external mutation
    return list(stack)


def _push_concept_to_hierarchy(concept_info: Dict[str, Any]) -> None:
    """Push a concept onto the hierarchy stack."""
    current_stack = list(_concept_hierarchy_stack.get())
    current_stack.append(concept_info)
    _concept_hierarchy_stack.set(current_stack)
    logger.debug(f"Pushed concept '{concept_info['name']}' to hierarchy (depth={len(current_stack)})")


def _pop_concept_from_hierarchy() -> Optional[Dict[str, Any]]:
    """Pop a concept from the hierarchy stack."""
    current_stack = list(_concept_hierarchy_stack.get())
    if not current_stack:
        logger.warning("Attempted to pop from empty hierarchy stack")
        return None

    concept_info = current_stack.pop()
    _concept_hierarchy_stack.set(current_stack)
    logger.debug(f"Popped concept '{concept_info['name']}' from hierarchy (depth={len(current_stack)})")
    return concept_info


def _get_parent_concept() -> Optional[Dict[str, Any]]:
    """Get the current parent concept (top of stack)."""
    stack = _concept_hierarchy_stack.get()
    return stack[-1] if stack else None


def _build_concept_path() -> str:
    """Build a path string representing the current concept hierarchy."""
    stack = _concept_hierarchy_stack.get()
    if not stack:
        return ""
    return " > ".join(c['name'] for c in stack)


@contextmanager
def businessConceptHierarchy(
    name: str,
    description: Optional[str] = None,
    materialize: bool = True,
    materialize_line_level_functions: bool = True,
    track_columns: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    auto_cache: bool = False,
    cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
    cache_threshold: int = 2,
):
    """
    Context manager for hierarchical business concepts.

    .. deprecated:: 2.1.0
        Use @businessConcept decorator with hierarchical=True (default) instead.
        The @businessConcept decorator now supports automatic hierarchy detection,
        making this context manager unnecessary in most cases.

        Old code (still works):
            with businessConceptHierarchy("Data Preparation"):
                df = prepare_data(df)

        New recommended approach:
            @businessConcept("Data Preparation")
            def prepare_data(df):
                return df.filter(...)

    This context manager enables nested business concepts, allowing you to define
    conceptual hierarchies using the 'with' statement. It tracks parent-child
    relationships and stores them in the lineage graph metadata.

    Usage as context manager:
        with businessConceptHierarchy(name="Data Preparation", description="Prepare data"):
            # Child concepts can be nested inside
            with businessConceptHierarchy(name="Load Data", description="Load source data"):
                df = load_data()

            with businessConceptHierarchy(name="Clean Data", description="Clean and validate"):
                df = clean_data(df)

    Can also be used as a decorator (though nesting is less intuitive):
        @businessConceptHierarchy(name="Transform", description="Transform data")
        def transform_pipeline():
            @businessConceptHierarchy(name="Step 1", description="First step")
            def step1():
                ...

            @businessConceptHierarchy(name="Step 2", description="Second step")
            def step2():
                ...

            step1()
            step2()

    Args:
        name: Business-friendly name for this concept
        description: Detailed explanation for stakeholders
        materialize: Whether to compute row counts (impacts performance)
        materialize_line_level_functions: Whether to materialize metrics for operations
        track_columns: Specific columns to monitor for distinct counts
        metadata: Additional context information
        auto_cache: Enable automatic caching after repeated materializations
        cache_storage_level: Storage level for automatic caching
        cache_threshold: Number of materializations before auto-caching kicks in

    Yields:
        ExecutionContext for this business concept

    Raises:
        ValidationError: If parameters are invalid
        LineageTrackingError: If tracking fails during execution
    """
    # Log soft deprecation warning
    import warnings
    warnings.warn(
        "businessConceptHierarchy context manager is soft-deprecated. "
        "Use @businessConcept decorator with hierarchical=True (default) instead. "
        "See documentation for migration examples.",
        DeprecationWarning,
        stacklevel=2
    )
    # Validate parameters
    validate_business_concept_name(name)
    validate_description(description)
    validate_materialize_setting(materialize)
    if track_columns is not None:
        validate_track_columns(track_columns)

    # Check if tracking is enabled
    tracker = get_enhanced_tracker()
    if not tracker or not tracker.should_track():
        # Zero-overhead mode - just yield without tracking
        yield None
        return

    # Get parent concept info
    parent_concept = _get_parent_concept()
    parent_name = parent_concept['name'] if parent_concept else None
    parent_context_id = parent_concept['context_id'] if parent_concept else None

    # Build the full concept path
    concept_path = _build_concept_path()
    full_path = f"{concept_path} > {name}" if concept_path else name

    # Create execution context
    context_manager = get_context_manager()

    with context_manager.context(
        function_name=name,
        materialization_enabled=materialize
    ) as context:
        # Create concept info for the hierarchy
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

        # Push this concept onto the hierarchy stack
        _push_concept_to_hierarchy(concept_info)

        try:
            # Create business concept node with hierarchy metadata
            concept_node = BusinessConceptNode(
                node_id=context.context_id,
                name=name,
                description=description,
                function_name=name,  # No actual function for context manager
                materialize=materialize,
                track_columns=track_columns or [],
                metadata={
                    **(metadata or {}),
                    'tracked_variables': track_columns or [],
                    'hierarchy': {
                        'parent_concept_name': parent_name,
                        'parent_context_id': parent_context_id,
                        'concept_path': full_path,
                        'depth': len(_get_current_hierarchy()),
                        'is_root': parent_name is None,
                    }
                },
            )

            # Register business concept BEFORE execution
            if tracker:
                tracker.register_business_concept(concept_node)
                logger.info(f"Registered hierarchical concept '{full_path}' with context {context.context_id}")

            execution_start = time.time()

            # Yield the context to the user's code block
            yield context

            execution_time = time.time() - execution_start
            concept_node.execution_time = execution_time

            # Update enhanced graph with timing and hierarchy info
            if tracker:
                tracker.update_node_metrics(
                    node_id=context.context_id,
                    timing=execution_time,
                    operation_name=name,
                    operation_description=description,
                )

                # Update the registered concept node with final execution data
                enhanced_graph = tracker.get_lineage_graph()
                if context.context_id in enhanced_graph.nodes:
                    registered_concept = enhanced_graph.nodes[context.context_id]
                    registered_concept.execution_time = execution_time
                    registered_concept.metadata.update(concept_node.metadata)

            logger.info(f"Completed hierarchical concept '{full_path}' in {execution_time:.3f}s")

        except Exception as e:
            logger.error(f"Error in hierarchical business concept '{full_path}': {e}")
            raise

        finally:
            # Always pop from hierarchy stack
            _pop_concept_from_hierarchy()


# Store the original context manager function
_original_context_manager = businessConceptHierarchy


# Allow businessConceptHierarchy to be used as a decorator as well
class _BusinessConceptHierarchyDecorator:
    """Helper class to make businessConceptHierarchy work as both context manager and decorator."""

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        materialize: bool = True,
        materialize_line_level_functions: bool = True,
        track_columns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_cache: bool = False,
        cache_storage_level: StorageLevel = StorageLevel.MEMORY_AND_DISK,
        cache_threshold: int = 2,
    ):
        self.name = name
        self.description = description
        self.materialize = materialize
        self.materialize_line_level_functions = materialize_line_level_functions
        self.track_columns = track_columns
        self.metadata = metadata
        self.auto_cache = auto_cache
        self.cache_storage_level = cache_storage_level
        self.cache_threshold = cache_threshold

    def __call__(self, func: F) -> F:
        """Use as a decorator."""
        validate_function_for_decoration(func)

        # Capture params for closure
        params = {
            'name': self.name,
            'description': self.description,
            'materialize': self.materialize,
            'materialize_line_level_functions': self.materialize_line_level_functions,
            'track_columns': self.track_columns,
            'metadata': self.metadata,
            'auto_cache': self.auto_cache,
            'cache_storage_level': self.cache_storage_level,
            'cache_threshold': self.cache_threshold,
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use the original context manager function stored above
            with _original_context_manager(**params):
                return func(*args, **kwargs)

        # Add metadata to the wrapper for introspection
        wrapper._business_concept_hierarchy_meta = {
            'name': self.name,
            'description': self.description,
            'materialize': self.materialize,
            'materialize_line_level_functions': self.materialize_line_level_functions,
            'track_columns': self.track_columns or [],
            'metadata': self.metadata or {},
            'original_function': func,
        }

        wrapper._is_business_concept_hierarchy = True

        return wrapper

    def __enter__(self):
        """Use as a context manager - delegate to the actual context manager."""
        # Use the original context manager function stored above
        self._cm = _original_context_manager(
            name=self.name,
            description=self.description,
            materialize=self.materialize,
            materialize_line_level_functions=self.materialize_line_level_functions,
            track_columns=self.track_columns,
            metadata=self.metadata,
            auto_cache=self.auto_cache,
            cache_storage_level=self.cache_storage_level,
            cache_threshold=self.cache_threshold,
        )
        return self._cm.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        return self._cm.__exit__(exc_type, exc_val, exc_tb)


# Replace the function with the dual-purpose class
# This allows businessConceptHierarchy to work as both decorator and context manager
businessConceptHierarchy = _BusinessConceptHierarchyDecorator


# Utility functions for hierarchy introspection
def get_concept_hierarchy() -> List[str]:
    """
    Get the current concept hierarchy as a list of names.

    Returns:
        List of concept names from root to current (e.g., ["Data Prep", "Load", "Validate"])
    """
    stack = _concept_hierarchy_stack.get()
    return [c['name'] for c in stack]


def get_concept_path() -> str:
    """
    Get the current concept path as a string.

    Returns:
        String representation of the path (e.g., "Data Prep > Load > Validate")
    """
    return _build_concept_path()


def get_hierarchy_depth() -> int:
    """
    Get the current hierarchy depth.

    Returns:
        Depth of nesting (0 = no hierarchy, 1 = one level, etc.)
    """
    return len(_concept_hierarchy_stack.get())


def is_in_hierarchy() -> bool:
    """
    Check if currently inside a business concept hierarchy.

    Returns:
        True if inside a businessConceptHierarchy context
    """
    return len(_concept_hierarchy_stack.get()) > 0


# Compatibility functions
def is_business_concept_hierarchy(func: Callable) -> bool:
    """Check if a function is decorated as a hierarchical business concept."""
    return hasattr(func, '_is_business_concept_hierarchy') and func._is_business_concept_hierarchy


def get_business_concept_hierarchy_info(func: Callable) -> Optional[Dict[str, Any]]:
    """Extract business concept hierarchy metadata from a decorated function."""
    if hasattr(func, '_business_concept_hierarchy_meta'):
        return func._business_concept_hierarchy_meta.copy()
    return None
