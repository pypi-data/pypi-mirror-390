#!/usr/bin/env python3
"""
Expression Lineage Decorator for PySpark StoryDoc.

This module provides decorators for automatically capturing column expressions
and integrating them with the existing lineage tracking system.
"""

import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from ..core.lineage_tracker import get_global_tracker
from ..utils.dataframe_utils import is_dataframe
from .expression_extractor import ColumnExpression, ExecutionPlanExpressionExtractor

logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


def expressionLineage(
    target_columns: Optional[Union[str, List[str]]] = None,
    include_all_columns: bool = False,
    capture_intermediate: bool = True,
    store_raw_plans: bool = False
) -> Callable[[F], F]:
    """
    Decorator to automatically capture column expressions from execution plans.

    This decorator analyzes the PySpark execution plan to reconstruct human-readable
    formulas showing exactly how columns were created, including multi-level
    expression substitution.

    Args:
        target_columns: Specific column(s) to track expressions for (str or List[str])
        include_all_columns: Whether to capture expressions for all output columns
        capture_intermediate: Whether to capture intermediate expressions during processing
        store_raw_plans: Whether to store raw execution plans for debugging

    Returns:
        Decorated function with expression lineage tracking

    Examples:
        >>> @expressionLineage("profit_margin")
        ... def calculate_profit_margin(df):
        ...     df = df.withColumn("revenue", col("price") * col("quantity"))
        ...     df = df.withColumn("profit", col("revenue") - col("cost"))
        ...     df = df.withColumn("profit_margin", col("profit") / col("revenue") * 100)
        ...     return df
        ...
        ... # Result: profit_margin = ((price * quantity) - cost) / (price * quantity) * 100

        >>> @expressionLineage(["total_revenue", "avg_margin"])
        ... def sales_summary(df):
        ...     return df.groupBy("product").agg(
        ...         sum("revenue").alias("total_revenue"),
        ...         avg("profit_margin").alias("avg_margin")
        ...     )

        >>> @expressionLineage(include_all_columns=True)
        ... def complex_transformations(df):
        ...     # Captures expressions for all output columns
        ...     return df.withColumn("complex_calc",
        ...                         when(col("status") == "premium", col("base_value") * 1.2)
        ...                         .otherwise(col("base_value")))
    """
    # Normalize target_columns to list
    if isinstance(target_columns, str):
        target_columns = [target_columns]

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize expression extractor
            extractor = ExecutionPlanExpressionExtractor()

            # Track expressions metadata for lineage
            expression_metadata = {
                "expression_lineage": True,
                "target_columns": target_columns,
                "include_all_columns": include_all_columns,
                "capture_intermediate": capture_intermediate,
                "analysis_timestamp": time.time(),
                "function_name": func.__name__
            }

            captured_expressions = {}
            intermediate_expressions = []
            result = None  # Initialize to avoid UnboundLocalError

            try:
                # Execute the original function
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Capture expressions from the result DataFrame
                if is_dataframe(result):
                    logger.info(f"Capturing expressions for {func.__name__}")

                    # Determine which columns to analyze
                    columns_to_analyze = target_columns
                    if include_all_columns:
                        columns_to_analyze = result.columns
                    elif target_columns:
                        # Filter to columns that actually exist in the result
                        columns_to_analyze = [col for col in target_columns if col in result.columns]

                    if columns_to_analyze:
                        # Extract expressions
                        expressions = extractor.extract_column_expressions(
                            result, columns_to_analyze
                        )
                        captured_expressions.update(expressions)

                        # Log captured expressions
                        for col_name, expr in expressions.items():
                            logger.info(f"Captured expression: {col_name} = {expr.expression}")

                    # Capture intermediate expressions if requested
                    if capture_intermediate and hasattr(result, '_jdf'):
                        try:
                            intermediate_expressions = _capture_intermediate_expressions(
                                result, extractor, store_raw_plans
                            )
                        except Exception as e:
                            logger.warning(f"Failed to capture intermediate expressions: {e}")

                    # Store metadata for report generation
                    expression_metadata.update({
                        "execution_time": execution_time,
                        "captured_expressions": {name: expr.to_dict() for name, expr in captured_expressions.items()},
                        "intermediate_expressions": intermediate_expressions,
                        "total_expressions_captured": len(captured_expressions)
                    })

                    # Add to global tracker if available
                    try:
                        tracker = get_global_tracker()
                        # Initialize the attribute if it doesn't exist
                        if not hasattr(tracker, '_expression_lineages'):
                            tracker._expression_lineages = []

                        lineage_data = {
                            'function_name': func.__name__,
                            'expressions': captured_expressions,
                            'metadata': expression_metadata,
                            'timestamp': time.time()
                        }

                        tracker._expression_lineages.append(lineage_data)
                        logger.info(f"Stored {len(captured_expressions)} expressions for {func.__name__}: {len(tracker._expression_lineages)} total lineages")

                    except Exception as e:
                        logger.error(f"Could not store expressions in global tracker: {e}")
                        import traceback
                        traceback.print_exc()

                else:
                    logger.warning(f"Function {func.__name__} did not return a DataFrame, skipping expression analysis")

            except Exception as e:
                logger.error(f"Failed to capture expressions for {func.__name__}: {e}")
                # If result is None, the exception occurred during function execution
                # Re-raise it so the caller knows the function failed
                if result is None:
                    raise
                # Otherwise, the exception occurred during expression capture
                # We can still return the result
                import traceback
                traceback.print_exc()

            return result

        return wrapper
    return decorator


def _capture_intermediate_expressions(df, extractor, store_raw_plans=False):
    """Capture intermediate expressions from execution plan analysis."""
    intermediate_data = []

    try:
        # Get the full execution plan string
        plan_string = df._jdf.queryExecution().optimizedPlan().toString()

        if store_raw_plans:
            intermediate_data.append({
                'type': 'raw_plan',
                'content': plan_string,
                'timestamp': time.time()
            })

        # Extract all available expressions from the plan
        all_expressions = extractor._parse_expressions_from_plan(plan_string)

        # Create summary of intermediate expressions
        intermediate_summary = {
            'type': 'intermediate_summary',
            'total_expressions': len(all_expressions),
            'expression_types': {},
            'timestamp': time.time()
        }

        # Classify expression types
        for col_name, raw_expr in all_expressions.items():
            op_type = extractor._classify_operation_type(raw_expr)
            if op_type not in intermediate_summary['expression_types']:
                intermediate_summary['expression_types'][op_type] = 0
            intermediate_summary['expression_types'][op_type] += 1

        intermediate_data.append(intermediate_summary)

    except Exception as e:
        logger.warning(f"Failed to capture intermediate expressions: {e}")

    return intermediate_data


def get_expression_summary(func_name: Optional[str] = None) -> str:
    """
    Get a summary of captured expressions from the global tracker.

    Args:
        func_name: Optional function name to filter results

    Returns:
        Formatted string summary of expressions
    """
    try:
        tracker = get_global_tracker()
        expression_lineages = getattr(tracker, '_expression_lineages', [])

        if not expression_lineages:
            return "No expression lineages captured yet."

        # Filter by function name if provided
        if func_name:
            expression_lineages = [el for el in expression_lineages if el['function_name'] == func_name]

        lines = []
        lines.append("Expression Lineage Summary")
        lines.append("=" * 50)

        for lineage in expression_lineages:
            lines.append(f"\nFunction: {lineage['function_name']}")
            lines.append(f"Captured: {len(lineage['expressions'])} expressions")

            for col_name, expr in lineage['expressions'].items():
                lines.append(f"  {col_name} = {expr.expression}")

        return '\n'.join(lines)

    except Exception as e:
        logger.error(f"Failed to get expression summary: {e}")
        return f"Error retrieving expression summary: {e}"


def clear_expression_lineages():
    """Clear all captured expression lineages from the global tracker."""
    try:
        tracker = get_global_tracker()
        tracker._expression_lineages = []
        logger.info("Cleared all expression lineages")
    except Exception as e:
        logger.warning(f"Could not clear expression lineages: {e}")


# Convenience function for manual expression extraction
def analyze_column_expressions(df, columns: Optional[List[str]] = None) -> Dict[str, ColumnExpression]:
    """
    Manually analyze column expressions for a DataFrame.

    Args:
        df: PySpark DataFrame to analyze
        columns: Optional list of specific columns to analyze

    Returns:
        Dictionary of column expressions
    """
    extractor = ExecutionPlanExpressionExtractor()
    return extractor.extract_column_expressions(df, columns)