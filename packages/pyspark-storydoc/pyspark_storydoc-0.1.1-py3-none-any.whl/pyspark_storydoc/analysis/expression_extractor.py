#!/usr/bin/env python3
"""
Expression Extractor for PySpark StoryDoc.

This module extracts human-readable expressions from PySpark execution plans
to reconstruct the formulas used to create columns.
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

try:
    from pyspark.sql import DataFrame
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    logger.warning("PySpark not available. Expression extraction will be limited.")
    # Create dummy DataFrame class for type hints
    class DataFrame:
        pass


@dataclass
class ColumnExpression:
    """Represents a reconstructed column expression."""
    column_name: str
    expression: str
    source_columns: List[str]
    operation_type: str  # 'arithmetic', 'conditional', 'aggregation', 'function'
    complexity_level: int  # 1=simple, 2=multi-level, 3=complex aggregation
    raw_plan_expression: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'column_name': self.column_name,
            'expression': self.expression,
            'source_columns': self.source_columns,
            'operation_type': self.operation_type,
            'complexity_level': self.complexity_level,
            'raw_plan_expression': self.raw_plan_expression
        }


class ExecutionPlanExpressionExtractor:
    """
    Extracts column expressions from PySpark execution plans.

    This class analyzes the optimized logical plan to reconstruct
    human-readable formulas showing how columns were created.
    """

    def __init__(self):
        """Initialize the expression extractor."""
        # Regex patterns for parsing execution plans
        self.column_assignment_pattern = re.compile(r'(.+?)\s+AS\s+(\w+)#\d+', re.IGNORECASE)
        self.project_pattern = re.compile(r'Project\s*\[(.*?)\]', re.DOTALL)
        # Aggregate has two bracket groups: [grouping_cols], [output_cols]
        # We need the second group which contains the aggregation expressions
        self.aggregate_pattern = re.compile(r'Aggregate\s*\[.*?\],\s*\[(.*?)\]', re.DOTALL)

        # Patterns for cleaning expressions
        self.cast_pattern = re.compile(r'cast\(([^,]+?)(?:\s+as\s+\w+)?\)', re.IGNORECASE)
        self.column_id_pattern = re.compile(r'(\w+)#\d+')
        self.literal_cast_pattern = re.compile(r'cast\((\d+(?:\.\d+)?)\s+as\s+\w+\)', re.IGNORECASE)

        # Operation type classifiers
        self.arithmetic_ops = {'+', '-', '*', '/', '%'}
        self.comparison_ops = {'>', '<', '>=', '<=', '=', '!=', '<>'}
        self.logical_ops = {'AND', 'OR', 'NOT'}
        self.aggregation_funcs = {'SUM', 'AVG', 'COUNT', 'MAX', 'MIN', 'STDDEV', 'VAR'}

    def extract_column_expressions(self, df: DataFrame, target_columns: Optional[List[str]] = None) -> Dict[str, ColumnExpression]:
        """
        Extract expressions for specified columns from DataFrame execution plan.

        Args:
            df: PySpark DataFrame to analyze
            target_columns: List of column names to extract expressions for (None = all)

        Returns:
            Dictionary mapping column names to their ColumnExpression objects
        """
        if not PYSPARK_AVAILABLE:
            logger.error("PySpark is not available")
            return {}

        try:
            # Get optimized logical plan - this has the best expression substitution
            plan_string = df._jdf.queryExecution().optimizedPlan().toString()
            logger.debug(f"Optimized plan extracted: {len(plan_string)} characters")

            # Parse expressions from the plan
            expressions = self._parse_expressions_from_plan(plan_string)

            # Filter to target columns if specified
            if target_columns:
                expressions = {col: expr for col, expr in expressions.items()
                             if col in target_columns}

            # Convert to ColumnExpression objects
            column_expressions = {}
            for col_name, raw_expr in expressions.items():
                try:
                    column_expr = self._create_column_expression(col_name, raw_expr)
                    column_expressions[col_name] = column_expr
                except Exception as e:
                    logger.warning(f"Failed to process expression for {col_name}: {e}")
                    continue

            return column_expressions

        except Exception as e:
            logger.error(f"Failed to extract expressions: {e}")
            return {}

    def _parse_expressions_from_plan(self, plan_string: str) -> Dict[str, str]:
        """Parse column expressions from execution plan string."""
        expressions = {}

        # Split plan into lines for processing
        lines = plan_string.split('\n')

        for line in lines:
            # Look for Project lines that contain column assignments
            if 'Project [' in line:
                project_expressions = self._extract_project_expressions(line)
                expressions.update(project_expressions)

            # Look for Aggregate lines
            elif 'Aggregate [' in line:
                agg_expressions = self._extract_aggregate_expressions(line)
                expressions.update(agg_expressions)

        return expressions

    def _extract_project_expressions(self, project_line: str) -> Dict[str, str]:
        """Extract expressions from a Project line."""
        expressions = {}

        # Find the content between Project [ and ]
        match = self.project_pattern.search(project_line)
        if not match:
            return expressions

        project_content = match.group(1)

        # Split on commas, but be careful with nested parentheses
        expr_parts = self._split_expressions(project_content)

        for expr_part in expr_parts:
            expr_part = expr_part.strip()

            # Look for assignment pattern: expression AS column_name#id
            assignment_match = self.column_assignment_pattern.search(expr_part)
            if assignment_match:
                raw_expr = assignment_match.group(1).strip()
                col_name = assignment_match.group(2)
                expressions[col_name] = raw_expr

        return expressions

    def _extract_aggregate_expressions(self, aggregate_line: str) -> Dict[str, str]:
        """Extract expressions from an Aggregate line."""
        expressions = {}

        # Find the content between Aggregate [ and ]
        match = self.aggregate_pattern.search(aggregate_line)
        if not match:
            return expressions

        agg_content = match.group(1)

        # Split aggregate functions
        expr_parts = self._split_expressions(agg_content)

        for expr_part in expr_parts:
            expr_part = expr_part.strip()

            # Look for assignment pattern in aggregations
            assignment_match = self.column_assignment_pattern.search(expr_part)
            if assignment_match:
                raw_expr = assignment_match.group(1).strip()
                col_name = assignment_match.group(2)
                expressions[col_name] = raw_expr

        return expressions

    def _split_expressions(self, content: str) -> List[str]:
        """Split expression content on commas, respecting nested parentheses."""
        expressions = []
        current_expr = ""
        paren_depth = 0

        for char in content:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                # This comma is at the top level, so it's a separator
                if current_expr.strip():
                    expressions.append(current_expr.strip())
                current_expr = ""
                continue

            current_expr += char

        # Add the last expression
        if current_expr.strip():
            expressions.append(current_expr.strip())

        return expressions

    def _create_column_expression(self, col_name: str, raw_expr: str) -> ColumnExpression:
        """Create a ColumnExpression object from raw plan expression."""
        # Clean the expression
        cleaned_expr = self._clean_expression(raw_expr)

        # Extract source columns
        source_columns = self._extract_source_columns(raw_expr)

        # Determine operation type
        operation_type = self._classify_operation_type(raw_expr)

        # Determine complexity level
        complexity_level = self._calculate_complexity_level(raw_expr, source_columns)

        return ColumnExpression(
            column_name=col_name,
            expression=cleaned_expr,
            source_columns=source_columns,
            operation_type=operation_type,
            complexity_level=complexity_level,
            raw_plan_expression=raw_expr
        )

    def _clean_expression(self, raw_expr: str) -> str:
        """Clean raw expression to make it human-readable."""
        expr = raw_expr

        # Remove cast functions but keep the content
        expr = self.literal_cast_pattern.sub(r'\1', expr)  # cast(100 as double) -> 100
        expr = self.cast_pattern.sub(r'\1', expr)  # cast(quantity#1 as double) -> quantity#1

        # Remove column IDs (keep just column names)
        expr = self.column_id_pattern.sub(r'\1', expr)  # quantity#1 -> quantity

        # Clean up extra whitespace
        expr = ' '.join(expr.split())

        # Format for readability
        expr = self._format_expression(expr)

        return expr

    def _format_expression(self, expr: str) -> str:
        """Format expression for better readability."""
        # Add spaces around operators
        for op in self.arithmetic_ops:
            expr = re.sub(f'\\s*\\{op}\\s*', f' {op} ', expr)

        for op in self.comparison_ops:
            if op in ['>=', '<=', '!=', '<>']:
                expr = expr.replace(op, f' {op} ')
            else:
                expr = re.sub(f'\\s*\\{op}\\s*', f' {op} ', expr)

        # Clean up multiple spaces
        expr = ' '.join(expr.split())

        return expr

    def _extract_source_columns(self, raw_expr: str) -> List[str]:
        """Extract source column names from raw expression."""
        # Find all column references (word#number pattern)
        column_matches = self.column_id_pattern.findall(raw_expr)

        # Remove duplicates and return sorted list
        return sorted(list(set(column_matches)))

    def _classify_operation_type(self, raw_expr: str) -> str:
        """Classify the type of operation based on expression content."""
        expr_upper = raw_expr.upper()

        # Check for aggregation functions
        for agg_func in self.aggregation_funcs:
            if agg_func + '(' in expr_upper:
                return 'aggregation'

        # Check for conditional logic
        if 'CASE WHEN' in expr_upper or 'IF(' in expr_upper:
            return 'conditional'

        # Check for function calls
        if re.search(r'\w+\s*\(', raw_expr):
            return 'function'

        # Check for arithmetic operations
        if any(op in raw_expr for op in self.arithmetic_ops):
            return 'arithmetic'

        # Default case
        return 'simple'

    def _calculate_complexity_level(self, raw_expr: str, source_columns: List[str]) -> int:
        """Calculate complexity level of the expression."""
        # Count nesting levels (parentheses depth)
        max_depth = 0
        current_depth = 0
        for char in raw_expr:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1

        # Base complexity on various factors
        complexity = 1

        # Add complexity for nesting
        if max_depth > 2:
            complexity += 1

        # Add complexity for multiple source columns
        if len(source_columns) > 3:
            complexity += 1

        # Add complexity for aggregations
        if 'aggregation' == self._classify_operation_type(raw_expr):
            complexity += 1

        # Add complexity for conditional logic
        if 'CASE WHEN' in raw_expr.upper():
            complexity += 1

        return min(complexity, 3)  # Cap at 3

    def generate_expression_summary(self, expressions: Dict[str, ColumnExpression]) -> str:
        """Generate a human-readable summary of all expressions."""
        lines = []
        lines.append("Expression Summary")
        lines.append("=" * 50)

        for col_name, expr in expressions.items():
            lines.append(f"\n{col_name} = {expr.expression}")
            lines.append(f"  Type: {expr.operation_type}")
            lines.append(f"  Sources: {', '.join(expr.source_columns)}")
            lines.append(f"  Complexity: {expr.complexity_level}/3")

        return '\n'.join(lines)


# Convenience function for easy usage
def extract_column_expressions(df: DataFrame, target_columns: Optional[List[str]] = None) -> Dict[str, ColumnExpression]:
    """
    Convenience function to extract column expressions from a DataFrame.

    Args:
        df: PySpark DataFrame to analyze
        target_columns: List of column names to extract expressions for (None = all)

    Returns:
        Dictionary mapping column names to their ColumnExpression objects
    """
    extractor = ExecutionPlanExpressionExtractor()
    return extractor.extract_column_expressions(df, target_columns)