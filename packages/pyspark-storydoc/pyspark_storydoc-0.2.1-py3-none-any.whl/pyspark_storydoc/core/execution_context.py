"""Execution context for tracking unique execution paths through the lineage graph."""

import logging
import threading
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from .lineage_id import LineageID

logger = logging.getLogger(__name__)


class ExecutionContext:
    """
    Represents a unique execution path through the lineage graph.

    Each function call gets its own context to track its specific execution path,
    input lineage IDs, and output lineage IDs. This enables proper fork detection
    and handling when the same DataFrame is used by multiple operations.

    Attributes:
        context_id: Unique identifier for this execution context
        parent_context: Optional parent context for nested operations
        input_lineage_ids: Maps input parameter names/positions to LineageIDs
        output_lineage_id: The LineageID produced by this execution
        function_name: Name of the function being executed
        metadata: Additional context information
        materialization_enabled: Whether to capture metrics for this context
        track_columns: Columns to track for distinct counts
    """

    def __init__(self,
                 context_id: str = None,
                 parent_context: Optional['ExecutionContext'] = None,
                 function_name: str = None,
                 materialization_enabled: bool = False,
                 track_columns: Optional[List[str]] = None):
        """Initialize an execution context."""
        self.context_id = context_id or f"ctx_{uuid.uuid4().hex[:12]}"
        self.parent_context = parent_context
        self.function_name = function_name
        self.input_lineage_ids = {}  # Maps input positions/names to LineageIDs
        self.output_lineage_ids = []  # Can have multiple outputs
        self.metadata = {}
        self.materialization_enabled = materialization_enabled
        self.track_columns = track_columns or []
        self.start_time = None
        self.end_time = None
        self.is_active = False

    def add_input_lineage(self, param_key: str, lineage_id: LineageID) -> None:
        """Add an input LineageID for a parameter."""
        self.input_lineage_ids[param_key] = lineage_id

    def add_output_lineage(self, lineage_id: LineageID) -> None:
        """Add an output LineageID."""
        self.output_lineage_ids.append(lineage_id)

    def get_input_lineage(self, param_key: str) -> Optional[LineageID]:
        """Get the input LineageID for a parameter."""
        return self.input_lineage_ids.get(param_key)

    def get_all_input_lineage_ids(self) -> List[str]:
        """Get all input LineageID identifiers."""
        return [lid.id for lid in self.input_lineage_ids.values()]

    def has_multiple_inputs(self) -> bool:
        """Check if this context has multiple inputs (potential merge point)."""
        return len(self.input_lineage_ids) > 1

    def is_nested(self) -> bool:
        """Check if this context is nested within another."""
        return self.parent_context is not None

    def get_root_context(self) -> 'ExecutionContext':
        """Get the root context in the hierarchy."""
        if self.parent_context is None:
            return self
        return self.parent_context.get_root_context()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'context_id': self.context_id,
            'parent_context_id': self.parent_context.context_id if self.parent_context else None,
            'function_name': self.function_name,
            'input_lineage_ids': {k: v.to_dict() for k, v in self.input_lineage_ids.items()},
            'output_lineage_ids': [lid.to_dict() for lid in self.output_lineage_ids],
            'metadata': self.metadata,
            'materialization_enabled': self.materialization_enabled,
            'track_columns': self.track_columns,
            'is_active': self.is_active
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        inputs = len(self.input_lineage_ids)
        outputs = len(self.output_lineage_ids)
        return f"ExecutionContext({self.context_id}, func={self.function_name}, inputs={inputs}, outputs={outputs})"


class ExecutionContextManager:
    """
    Manages execution contexts with thread-local storage support.

    This class provides thread-safe context management for tracking execution
    paths through the lineage graph. It maintains a stack of contexts to handle
    nested operations correctly.
    """

    def __init__(self):
        self._local = threading.local()
        self._contexts = {}  # context_id -> ExecutionContext
        self._active_contexts = {}  # thread_id -> List[ExecutionContext]

    def create_context(self,
                      function_name: str = None,
                      materialization_enabled: bool = False,
                      track_columns: Optional[List[str]] = None,
                      parent_context: Optional[ExecutionContext] = None) -> ExecutionContext:
        """Create a new execution context."""
        if parent_context is None:
            parent_context = self.get_current_context()

        context = ExecutionContext(
            parent_context=parent_context,
            function_name=function_name,
            materialization_enabled=materialization_enabled,
            track_columns=track_columns
        )

        self._contexts[context.context_id] = context
        logger.debug(f"Created execution context: {context.context_id} for function: {function_name}")

        return context

    def get_current_context(self) -> Optional[ExecutionContext]:
        """Get the current active context for this thread."""
        if not hasattr(self._local, 'context_stack'):
            return None

        stack = self._local.context_stack
        return stack[-1] if stack else None

    def get_context_stack(self) -> List[ExecutionContext]:
        """Get the full context stack for this thread."""
        if not hasattr(self._local, 'context_stack'):
            self._local.context_stack = []
        return self._local.context_stack

    def push_context(self, context: ExecutionContext) -> None:
        """Push a context onto the thread's context stack."""
        if not hasattr(self._local, 'context_stack'):
            self._local.context_stack = []

        self._local.context_stack.append(context)
        context.is_active = True
        logger.debug(f"Pushed context {context.context_id} onto stack (depth={len(self._local.context_stack)})")

    def pop_context(self) -> Optional[ExecutionContext]:
        """Pop a context from the thread's context stack."""
        if not hasattr(self._local, 'context_stack') or not self._local.context_stack:
            logger.warning("Attempted to pop context from empty stack")
            return None

        context = self._local.context_stack.pop()
        context.is_active = False
        logger.debug(f"Popped context {context.context_id} from stack (depth={len(self._local.context_stack)})")
        return context

    @contextmanager
    def context(self,
                function_name: str = None,
                materialization_enabled: bool = False,
                track_columns: Optional[List[str]] = None):
        """
        Context manager for execution contexts.

        Usage:
            with context_manager.context(function_name="my_transform"):
                # Your code here
                pass
        """
        context = self.create_context(
            function_name=function_name,
            materialization_enabled=materialization_enabled,
            track_columns=track_columns
        )

        self.push_context(context)
        try:
            yield context
        finally:
            self.pop_context()

    def get_context(self, context_id: str) -> Optional[ExecutionContext]:
        """Get a context by its ID."""
        return self._contexts.get(context_id)

    def get_all_contexts(self) -> Dict[str, ExecutionContext]:
        """Get all registered contexts."""
        return self._contexts.copy()

    def clear_thread_contexts(self) -> None:
        """Clear the context stack for the current thread."""
        if hasattr(self._local, 'context_stack'):
            self._local.context_stack.clear()

    def clear_all(self) -> None:
        """Clear all contexts."""
        self._contexts.clear()
        self.clear_thread_contexts()


# Global context manager instance
_global_context_manager = ExecutionContextManager()


def get_context_manager() -> ExecutionContextManager:
    """Get the global execution context manager."""
    return _global_context_manager


def get_current_context() -> Optional[ExecutionContext]:
    """Get the current active execution context."""
    return _global_context_manager.get_current_context()


def get_current_context_id() -> Optional[str]:
    """Get the ID of the current active execution context."""
    context = get_current_context()
    return context.context_id if context else None


@contextmanager
def execution_context(function_name: str = None,
                     materialization_enabled: bool = False):
    """
    Convenience context manager for execution contexts.

    Usage:
        with execution_context(function_name="my_transform"):
            # Your code here
            pass
    """
    with _global_context_manager.context(
        function_name=function_name,
        materialization_enabled=materialization_enabled
    ) as ctx:
        yield ctx