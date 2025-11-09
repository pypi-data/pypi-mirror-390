#!/usr/bin/env python3
"""
LineageGroupedData - Wrapper for PySpark GroupedData with lineage tracking.

This module provides a wrapper around PySpark's GroupedData object to maintain
lineage tracking through groupBy and aggregation operations.

Problem Solved:
--------------
When users call df.groupBy().agg(), PySpark returns a native GroupedData object
that doesn't preserve lineage metadata. This causes missing edges in the lineage
graph between the input DataFrame and the aggregated result.

Solution:
---------
LineageGroupedData wraps the native GroupedData and intercepts all aggregation
methods (agg, count, sum, avg, min, max, pivot) to:
1. Execute the native PySpark aggregation
2. Create a lineage node for the groupBy operation
3. Create an edge from the parent DataFrame to the result
4. Capture metadata (group columns, aggregation functions)
5. Return a LineageDataFrame with proper lineage tracking

Architecture:
------------
    LineageDataFrame
        └─> groupBy(*cols)
                └─> LineageGroupedData (this class)
                        ├─> agg(*exprs) → LineageDataFrame
                        ├─> count() → LineageDataFrame
                        ├─> sum(colName) → LineageDataFrame
                        ├─> avg(colName) → LineageDataFrame
                        ├─> min(colName) → LineageDataFrame
                        ├─> max(colName) → LineageDataFrame
                        └─> pivot(col, values) → LineageGroupedData

Example Usage:
-------------
    from pyspark_storydoc import LineageDataFrame
    from pyspark.sql.functions import sum, avg

    # Create lineage-tracked DataFrame
    ldf = LineageDataFrame(spark_df, business_label="Sales Data")

    # GroupBy with lineage tracking
    result = ldf.groupBy("region", "product").agg(
        sum("revenue").alias("total_revenue"),
        avg("quantity").alias("avg_quantity")
    )

    # Result is LineageDataFrame with edge from ldf to result
    # Metadata captured: group_columns=['region', 'product'],
    #                   aggregations=[{function: 'sum', column: 'revenue', ...}, ...]
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pyspark.sql.column import Column
from pyspark.sql.group import GroupedData

if TYPE_CHECKING:
    from .lineage_dataframe import LineageDataFrame
    from .lineage_tracker import LineageTracker


class LineageGroupedData:
    """
    Wrapper around PySpark GroupedData that preserves lineage tracking.

    This class intercepts aggregation operations to create lineage nodes and edges,
    ensuring that groupBy operations don't break the lineage chain.

    Attributes:
        _grouped_data: Native PySpark GroupedData object
        _parent_lineage_df: Source LineageDataFrame that was grouped
        _group_cols: List of column names used for grouping
        _tracker: Global LineageTracker instance
        _context_id: Business context ID (if within @businessConcept)
        _pivot_col: Pivot column name (if pivot was called)
        _pivot_values: Pivot values (if pivot was called)
    """

    def __init__(
        self,
        grouped_data: GroupedData,
        parent_lineage_df: 'LineageDataFrame',
        group_cols: List[str],
        tracker: 'LineageTracker',
        context_id: Optional[str] = None
    ):
        """
        Initialize LineageGroupedData wrapper.

        Args:
            grouped_data: Native PySpark GroupedData object
            parent_lineage_df: Source LineageDataFrame that was grouped
            group_cols: List of column names used for grouping
            tracker: Global LineageTracker instance
            context_id: Optional business context ID
        """
        self._grouped_data = grouped_data
        self._parent_lineage_df = parent_lineage_df
        self._group_cols = group_cols
        self._tracker = tracker
        self._context_id = context_id
        self._pivot_col = None
        self._pivot_values = None

    def agg(self, *exprs) -> 'LineageDataFrame':
        """
        Execute aggregation and create lineage node.

        This is the core method that:
        1. Executes the native PySpark aggregation
        2. Creates a lineage node for the groupBy operation
        3. Creates an edge from parent to result
        4. Captures metadata about grouping and aggregations
        5. Returns a LineageDataFrame with proper lineage tracking

        Args:
            *exprs: Aggregation expressions (Column objects or dict)

        Returns:
            LineageDataFrame wrapping the aggregated result

        Example:
            grouped_ldf.agg(
                sum("amount").alias("total"),
                avg("quantity").alias("avg_qty")
            )
        """
        # Execute native aggregation
        result_df = self._grouped_data.agg(*exprs)

        # Parse aggregation expressions to extract metadata
        agg_metadata = self._parse_aggregation_expressions(exprs)

        # Build operation metadata
        operation_metadata = {
            'operation_name': 'Group By',
            'group_columns': self._group_cols,
            'aggregation_functions': agg_metadata,
        }

        # Add pivot metadata if applicable
        if self._pivot_col:
            operation_metadata['pivot_column'] = self._pivot_col
            operation_metadata['pivot_values'] = self._pivot_values

        # Use parent's _create_result_dataframe to properly create lineage node
        result_ldf = self._parent_lineage_df._create_result_dataframe(
            result_df,
            operation_type="groupby",
            operation_name=f"Group By",
            extra_metadata=operation_metadata
        )

        return result_ldf

    def count(self) -> 'LineageDataFrame':
        """
        Count rows in each group with lineage tracking.

        Shortcut for agg(count("*").alias("count")).

        Returns:
            LineageDataFrame with count column
        """
        from pyspark.sql.functions import count as spark_count

        return self.agg(spark_count("*").alias("count"))

    def sum(self, colName: str) -> 'LineageDataFrame':
        """
        Sum values in each group with lineage tracking.

        Args:
            colName: Column name to sum

        Returns:
            LineageDataFrame with sum aggregation
        """
        from pyspark.sql.functions import sum as spark_sum

        return self.agg(spark_sum(colName))

    def avg(self, colName: str) -> 'LineageDataFrame':
        """
        Average values in each group with lineage tracking.

        Args:
            colName: Column name to average

        Returns:
            LineageDataFrame with average aggregation
        """
        from pyspark.sql.functions import avg as spark_avg

        return self.agg(spark_avg(colName))

    def mean(self, colName: str) -> 'LineageDataFrame':
        """
        Mean values in each group with lineage tracking.

        Alias for avg().

        Args:
            colName: Column name to average

        Returns:
            LineageDataFrame with mean aggregation
        """
        return self.avg(colName)

    def min(self, colName: str) -> 'LineageDataFrame':
        """
        Minimum value in each group with lineage tracking.

        Args:
            colName: Column name to find minimum

        Returns:
            LineageDataFrame with min aggregation
        """
        from pyspark.sql.functions import min as spark_min

        return self.agg(spark_min(colName))

    def max(self, colName: str) -> 'LineageDataFrame':
        """
        Maximum value in each group with lineage tracking.

        Args:
            colName: Column name to find maximum

        Returns:
            LineageDataFrame with max aggregation
        """
        from pyspark.sql.functions import max as spark_max

        return self.agg(spark_max(colName))

    def pivot(self, pivot_col: str, values: Optional[List[Any]] = None) -> 'LineageGroupedData':
        """
        Pivot on a column with lineage tracking.

        Returns a new LineageGroupedData for subsequent aggregation.

        Args:
            pivot_col: Column name to pivot on
            values: Optional list of values to pivot (for optimization)

        Returns:
            New LineageGroupedData with pivot configuration

        Example:
            ldf.groupBy("year").pivot("product", ["A", "B", "C"]).sum("revenue")
        """
        # Execute native pivot
        if values is not None:
            pivoted_grouped = self._grouped_data.pivot(pivot_col, values)
        else:
            pivoted_grouped = self._grouped_data.pivot(pivot_col)

        # Create new LineageGroupedData with pivot metadata
        pivoted_lineage_grouped = LineageGroupedData(
            grouped_data=pivoted_grouped,
            parent_lineage_df=self._parent_lineage_df,
            group_cols=self._group_cols,
            tracker=self._tracker,
            context_id=self._context_id
        )

        # Store pivot metadata
        pivoted_lineage_grouped._pivot_col = pivot_col
        pivoted_lineage_grouped._pivot_values = values

        return pivoted_lineage_grouped

    def _parse_aggregation_expressions(self, exprs) -> List[Dict[str, Any]]:
        """
        Parse aggregation expressions to extract metadata.

        Attempts to extract function name, column name, and alias from
        aggregation expressions for better lineage documentation.

        Args:
            exprs: Tuple of aggregation expressions (Column objects or dict)

        Returns:
            List of dicts with metadata: [{function, column, alias}, ...]

        Example:
            Input: (sum("amount").alias("total"), avg("price"))
            Output: [
                {'function': 'sum', 'column': 'amount', 'alias': 'total'},
                {'function': 'avg', 'column': 'price', 'alias': None}
            ]
        """
        agg_list = []

        for expr in exprs:
            agg_info = {}

            if isinstance(expr, dict):
                # Dictionary-style aggregation: {"amount": "sum", "price": "avg"}
                for col_name, func_name in expr.items():
                    agg_list.append({
                        'function': str(func_name),
                        'column': str(col_name),
                        'alias': None
                    })
            elif isinstance(expr, Column):
                # Column object - try to extract function and column name
                try:
                    # Get string representation of column
                    expr_str = str(expr)

                    # Try to extract function name (e.g., "sum(amount)")
                    # This is a simple heuristic - may not work for complex expressions
                    if '(' in expr_str and ')' in expr_str:
                        # Extract function name
                        func_start = expr_str.find('(')
                        func_name = expr_str[:func_start].strip()

                        # Extract column name (between parentheses)
                        col_part = expr_str[func_start+1:expr_str.rfind(')')].strip()

                        # Remove quotes if present
                        if col_part.startswith("'") or col_part.startswith('"'):
                            col_part = col_part[1:-1]

                        agg_info['function'] = func_name
                        agg_info['column'] = col_part
                    else:
                        # Fallback for non-function expressions
                        agg_info['function'] = 'unknown'
                        agg_info['column'] = expr_str

                    # Try to extract alias if present
                    # This is a heuristic - Column objects don't expose alias directly
                    agg_info['alias'] = None

                except Exception:
                    # If parsing fails, use generic metadata
                    agg_info['function'] = 'unknown'
                    agg_info['column'] = 'unknown'
                    agg_info['alias'] = None

                agg_list.append(agg_info)
            else:
                # Unknown expression type
                agg_list.append({
                    'function': 'unknown',
                    'column': str(expr),
                    'alias': None
                })

        return agg_list

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"LineageGroupedData("
            f"group_cols={self._group_cols}, "
            f"parent={self._parent_lineage_df.lineage_id.to_string()}, "
            f"pivot={self._pivot_col})"
        )
