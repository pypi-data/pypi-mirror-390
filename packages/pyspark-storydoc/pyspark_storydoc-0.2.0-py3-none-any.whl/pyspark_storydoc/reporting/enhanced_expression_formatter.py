#!/usr/bin/env python3
"""
Enhanced Expression Formatter for PySpark StoryDoc.

This module provides advanced formatting capabilities for expression lineage
documentation, including SQL-style formatting, complexity analysis, and
contextual information extraction.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FormattedExpression:
    """Represents a fully formatted expression with metadata."""
    formatted: str  # Human-readable formatted expression
    raw: str  # Original expression
    dependencies: List[Dict[str, Any]]  # Source columns with context
    complexity_score: int  # 1-10 score
    risk_level: str  # LOW/MEDIUM/HIGH
    operation_type: str  # aggregation/join/conditional/arithmetic/etc.
    context: Dict[str, Any]  # Additional context (join info, grouping, etc.)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'formatted': self.formatted,
            'raw': self.raw,
            'dependencies': self.dependencies,
            'complexity_score': self.complexity_score,
            'risk_level': self.risk_level,
            'operation_type': self.operation_type,
            'context': self.context
        }


class EnhancedExpressionFormatter:
    """
    Enhanced formatter for expression lineage documentation.

    Improvements over current implementation:
    - SQL-style formatting for readability
    - Complexity scoring
    - Source attribution for joins
    - Aggregation context
    - Impact analysis
    """

    def __init__(self):
        """Initialize the enhanced expression formatter."""
        # Patterns for expression parsing
        self.case_when_pattern = re.compile(
            r'CASE\s+WHEN\s+.*?\s+END',
            re.IGNORECASE | re.DOTALL
        )
        self.function_pattern = re.compile(r'(\w+)\s*\(')
        self.operator_pattern = re.compile(r'[+\-*/%<>=!&|]')

        # Aggregation function keywords
        self.aggregation_functions = {
            'sum', 'avg', 'count', 'max', 'min', 'stddev',
            'variance', 'collect_list', 'collect_set', 'first', 'last'
        }

        # Join indicator keywords (from metadata)
        self.join_indicators = {'join', 'left', 'right', 'inner', 'outer', 'cross'}

    def format_expression(
        self,
        expression: str,
        column_name: str,
        metadata: Dict[str, Any]
    ) -> FormattedExpression:
        """
        Format expression with enhanced context.

        Args:
            expression: Raw expression string
            column_name: Name of the column
            metadata: Additional metadata from lineage graph

        Returns:
            FormattedExpression object with all formatting and metadata
        """
        # Format the expression for readability
        formatted = self.format_sql_style(expression)

        # Extract dependencies
        dependencies = self.extract_dependencies(expression, metadata)

        # Calculate complexity
        complexity_metrics = self.calculate_complexity(expression)

        # Determine operation type
        operation_type = self._classify_operation(expression, metadata)

        # Extract context
        context = self._extract_context(expression, metadata, operation_type)

        # Determine risk level based on complexity
        risk_level = self._assess_risk_level(complexity_metrics, operation_type)

        return FormattedExpression(
            formatted=formatted,
            raw=expression,
            dependencies=dependencies,
            complexity_score=complexity_metrics['score'],
            risk_level=risk_level,
            operation_type=operation_type,
            context=context
        )

    def calculate_complexity(self, expression: str) -> Dict[str, Any]:
        """
        Calculate expression complexity metrics.

        Args:
            expression: Expression string to analyze

        Returns:
            Dictionary with complexity metrics:
                - nesting_depth: Maximum parenthesis depth
                - operation_count: Number of operations
                - conditional_branches: Number of CASE WHEN branches
                - function_calls: Number of function invocations
                - dependency_count: Estimated number of source columns
                - score: Overall complexity score (1-10)
        """
        # Calculate nesting depth
        nesting_depth = self._calculate_nesting_depth(expression)

        # Count operations
        operation_count = len(self.operator_pattern.findall(expression))

        # Count conditional branches
        conditional_branches = self._count_case_when_branches(expression)

        # Count function calls
        function_calls = len(self.function_pattern.findall(expression))

        # Estimate dependency count (rough estimate from column references)
        dependency_count = len(set(re.findall(r'\b[a-zA-Z_]\w*\b', expression)))

        # Calculate overall score (1-10)
        score = self._calculate_complexity_score(
            nesting_depth,
            operation_count,
            conditional_branches,
            function_calls,
            dependency_count
        )

        return {
            'nesting_depth': nesting_depth,
            'operation_count': operation_count,
            'conditional_branches': conditional_branches,
            'function_calls': function_calls,
            'dependency_count': dependency_count,
            'score': score
        }

    def format_sql_style(self, expression: str) -> str:
        """
        Format CASE WHEN and complex expressions in SQL style.

        Args:
            expression: Raw expression string

        Returns:
            Formatted expression with proper indentation and line breaks

        Example:
            Input:  "CASE WHEN (x = 1) THEN a WHEN (x = 2) THEN b ELSE c END"
            Output:
            ```
            CASE
                WHEN (x = 1) THEN a
                WHEN (x = 2) THEN b
                ELSE c
            END
            ```
        """
        formatted = expression

        # Format CASE WHEN statements
        if 'CASE' in formatted.upper():
            formatted = self._format_case_when(formatted)

        # Format long expressions with multiple operations
        if len(formatted) > 80 and '+' in formatted or '*' in formatted:
            formatted = self._format_arithmetic_expression(formatted)

        return formatted

    def extract_dependencies(
        self,
        expression: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract all source column dependencies with context.

        Args:
            expression: Expression string
            metadata: Metadata containing lineage information

        Returns:
            List of dependency dictionaries with:
                - column: Column name
                - source_table: Source table name (for joined columns) or None
                - operation: How it was created
                - is_aggregated: Whether it's an aggregated column
        """
        dependencies = []

        # Extract column names from expression
        column_references = self._extract_column_names(expression)

        # Get source information from metadata
        source_columns = metadata.get('source_columns', [])
        join_sources = metadata.get('join_sources', {})
        aggregation_context = metadata.get('aggregation_context', {})

        for col in column_references:
            dep_info = {
                'column': col,
                'source_table': join_sources.get(col),
                'operation': self._get_column_operation(col, metadata),
                'is_aggregated': col in aggregation_context.get('aggregated_columns', [])
            }
            dependencies.append(dep_info)

        return dependencies

    def _calculate_nesting_depth(self, expression: str) -> int:
        """Calculate maximum nesting depth from parentheses."""
        max_depth = 0
        current_depth = 0

        for char in expression:
            if char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ')':
                current_depth -= 1

        return max_depth

    def _count_case_when_branches(self, expression: str) -> int:
        """Count the number of WHEN clauses in CASE statements."""
        when_count = len(re.findall(r'\bWHEN\b', expression, re.IGNORECASE))
        return when_count

    def _calculate_complexity_score(
        self,
        nesting_depth: int,
        operation_count: int,
        conditional_branches: int,
        function_calls: int,
        dependency_count: int
    ) -> int:
        """
        Calculate overall complexity score (1-10).

        Scoring logic:
        - Each nesting level: +1 point
        - Every 3 operations: +1 point
        - Each conditional branch: +1 point
        - Every 2 function calls: +1 point
        - Every 5 dependencies: +1 point
        """
        score = 1  # Base score

        # Nesting depth contribution
        score += min(nesting_depth, 3)

        # Operations contribution
        score += min(operation_count // 3, 2)

        # Conditional branches contribution
        score += min(conditional_branches, 2)

        # Function calls contribution
        score += min(function_calls // 2, 2)

        # Dependencies contribution
        score += min(dependency_count // 5, 1)

        # Cap at 10
        return min(score, 10)

    def _assess_risk_level(
        self,
        complexity_metrics: Dict[str, Any],
        operation_type: str
    ) -> str:
        """
        Assess risk level based on complexity and operation type.

        Returns: "LOW", "MEDIUM", or "HIGH"
        """
        score = complexity_metrics['score']

        # Base risk on complexity score
        if score <= 3:
            base_risk = "LOW"
        elif score <= 6:
            base_risk = "MEDIUM"
        else:
            base_risk = "HIGH"

        # Elevate risk for certain operation types
        if operation_type in ['aggregation', 'join'] and base_risk == "LOW":
            return "MEDIUM"

        if complexity_metrics['conditional_branches'] > 5:
            return "HIGH"

        return base_risk

    def _format_case_when(self, expression: str) -> str:
        """Format CASE WHEN statements with proper indentation."""
        # Add line breaks before WHEN, ELSE, and END
        formatted = re.sub(
            r'\s+WHEN\s+',
            '\n    WHEN ',
            expression,
            flags=re.IGNORECASE
        )
        formatted = re.sub(
            r'\s+ELSE\s+',
            '\n    ELSE ',
            formatted,
            flags=re.IGNORECASE
        )
        formatted = re.sub(
            r'\s+END\b',
            '\nEND',
            formatted,
            flags=re.IGNORECASE
        )

        # Ensure CASE is on its own line
        formatted = re.sub(
            r'CASE\s+WHEN',
            'CASE\n    WHEN',
            formatted,
            flags=re.IGNORECASE
        )

        return formatted

    def _format_arithmetic_expression(self, expression: str) -> str:
        """Format long arithmetic expressions for readability."""
        # For very long expressions, consider breaking at operators
        # This is a simple implementation - can be enhanced
        if len(expression) > 120:
            # Break at major operators while preserving order
            formatted = expression.replace(' + ', '\n    + ')
            formatted = formatted.replace(' - ', '\n    - ')
            return formatted

        return expression

    def _extract_column_names(self, expression: str) -> List[str]:
        """Extract column names from expression."""
        # Remove function names and keywords
        cleaned = expression

        # Remove common SQL keywords
        keywords = {
            'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AND', 'OR', 'NOT',
            'IS', 'NULL', 'AS', 'CAST', 'TRUE', 'FALSE'
        }

        # Find all word tokens
        words = re.findall(r'\b[a-zA-Z_]\w*\b', cleaned)

        # Filter out keywords and function names
        columns = []
        for word in words:
            if word.upper() not in keywords and not self._is_function_name(word, expression):
                columns.append(word)

        # Remove duplicates while preserving order
        seen = set()
        unique_columns = []
        for col in columns:
            if col not in seen:
                seen.add(col)
                unique_columns.append(col)

        return unique_columns

    def _is_function_name(self, word: str, expression: str) -> bool:
        """Check if a word is likely a function name."""
        # Look for pattern: word followed by opening parenthesis
        pattern = rf'\b{re.escape(word)}\s*\('
        return bool(re.search(pattern, expression))

    def _classify_operation(self, expression: str, metadata: Dict[str, Any]) -> str:
        """
        Classify the operation type.

        Returns: aggregation, join, conditional, arithmetic, string, cast, or simple
        """
        expr_lower = expression.lower()

        # Check metadata first
        if metadata.get('operation_type'):
            return metadata['operation_type']

        # Check for aggregation functions
        for agg_func in self.aggregation_functions:
            if f'{agg_func}(' in expr_lower:
                return 'aggregation'

        # Check for join indicators in metadata
        if metadata.get('join_sources'):
            return 'join'

        # Check for conditional logic
        if 'case when' in expr_lower or 'if(' in expr_lower:
            return 'conditional'

        # Check for arithmetic
        if any(op in expression for op in ['+', '-', '*', '/', '%']):
            return 'arithmetic'

        # Check for string operations
        if 'concat' in expr_lower or '||' in expression:
            return 'string'

        # Check for type casting
        if 'cast(' in expr_lower:
            return 'cast'

        return 'simple'

    def _extract_context(
        self,
        expression: str,
        metadata: Dict[str, Any],
        operation_type: str
    ) -> Dict[str, Any]:
        """
        Extract additional context based on operation type.

        Returns context dictionary with operation-specific information.
        """
        context = {}

        if operation_type == 'aggregation':
            context.update(self._extract_aggregation_context(metadata))

        if operation_type == 'join':
            context.update(self._extract_join_context(metadata))

        if operation_type == 'conditional':
            context.update(self._extract_conditional_context(expression))

        return context

    def _extract_aggregation_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract aggregation-specific context."""
        agg_context = metadata.get('aggregation_context', {})

        return {
            'grouped_by': agg_context.get('group_by_columns', []),
            'aggregation_function': agg_context.get('agg_function', 'unknown'),
            'source_columns': agg_context.get('source_columns', []),
            'data_reduction': agg_context.get('data_reduction', 'unknown')
        }

    def _extract_join_context(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract join-specific context."""
        return {
            'join_sources': metadata.get('join_sources', {}),
            'join_type': metadata.get('join_type', 'unknown'),
            'join_keys': metadata.get('join_keys', [])
        }

    def _extract_conditional_context(self, expression: str) -> Dict[str, Any]:
        """Extract conditional logic context."""
        branches = self._count_case_when_branches(expression)

        return {
            'branch_count': branches,
            'has_else': 'ELSE' in expression.upper(),
            'complexity': 'high' if branches > 3 else 'medium' if branches > 1 else 'low'
        }

    def _get_column_operation(self, column: str, metadata: Dict[str, Any]) -> str:
        """Get how a column was created based on metadata."""
        # Check if it's a source column
        if column in metadata.get('source_columns', []):
            return 'source'

        # Check if it's from a join
        if column in metadata.get('join_sources', {}):
            return 'joined'

        # Check if it's derived
        if column in metadata.get('derived_columns', []):
            return 'derived'

        return 'unknown'
