#!/usr/bin/env python3
"""
Expression Documentation Report for PySpark StoryDoc.

NOTE: This is a placeholder implementation for future expression lineage integration.
Once expression lineage tracking is fully integrated into EnhancedLineageGraph,
this report will automatically extract and document column expressions.

Current Status:
- Framework and structure are complete
- Will activate when expression metadata is available in the graph
- Designed to work with @expressionLineage decorator outputs
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class ExpressionDocumentationConfig(ReportConfig):
    """
    Configuration for expression documentation report.

    Attributes:
        include_formulas: Include reconstructed formulas
        include_dependencies: Show column dependency chains
        include_sql_equivalent: Generate SQL equivalent when possible
        include_statistics: Show column statistics if available
        sort_by: Sort expressions by "name", "complexity", or "creation_order"
        max_formula_length: Maximum characters for inline formulas
        show_source_columns: Show source columns for each expression
        categorize_by_type: Group by operation type (arithmetic, conditional, etc.)
        include_summary_table: Include a summary table at the top
        include_expanded_expressions: Show fully expanded expressions with substitutions
        max_expansion_depth: Maximum recursion depth for expression expansion
        color_theme: Color theme for expression highlighting - "dark" or "light"
        enable_color_coding: Enable color-coded expression expansion (for future HTML export)
    """
    include_formulas: bool = True
    include_dependencies: bool = True
    include_sql_equivalent: bool = True
    include_statistics: bool = True
    sort_by: str = "creation_order"  # "name", "complexity", "creation_order"
    max_formula_length: int = 200
    show_source_columns: bool = True
    categorize_by_type: bool = True
    include_summary_table: bool = True
    include_expanded_expressions: bool = True
    max_expansion_depth: int = 10
    color_theme: str = "dark"  # "dark" or "light"
    enable_color_coding: bool = False  # For future HTML export functionality
    include_diagram: bool = True  # Include visual expression impact diagram
    diagram_view_mode: str = "variable_flow"  # "variable_flow" or "expression_centric"


class ExpressionDocumentationReport(BaseReport):
    """
    Generates documentation for column expressions and formulas.

    This report extracts expression metadata from the lineage graph and creates
    a comprehensive catalog of how columns are derived, including:
    - Human-readable formulas
    - Dependency chains showing source columns
    - SQL equivalents for documentation
    - Complexity analysis and classification
    - Derivation context (which operation/concept created the column)

    Example Output:
        # Expression Documentation

        ## customer_lifetime_value

        **Formula:**
        ```
        (total_purchases * avg_order_value) * retention_factor
        ```

        **Dependencies:**
        - total_purchases (from "Aggregate Purchases")
        - avg_order_value (from "Calculate Metrics")
        - retention_factor (constant: 0.85)

        **SQL Equivalent:**
        ```sql
        (total_purchases * avg_order_value) * 0.85 AS customer_lifetime_value
        ```
    """

    def __init__(self, config: Optional[ExpressionDocumentationConfig] = None, **kwargs):
        """
        Initialize the expression documentation report.

        Args:
            config: Report configuration
            **kwargs: Alternative way to pass config options
        """
        if config is None and kwargs:
            config = ExpressionDocumentationConfig(**kwargs)
        super().__init__(config or ExpressionDocumentationConfig())

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate expression documentation report.

        Args:
            lineage_graph: EnhancedLineageGraph with expression metadata
            output_path: Output file path

        Returns:
            Path to generated report
        """
        logger.info("Generating expression documentation report...")

        # Extract expression data from graph
        expressions = self._extract_expressions(lineage_graph)

        # Check if expressions are available
        if not expressions:
            logger.warning(
                "No expression lineage data found in graph. "
                "Expression documentation requires using @expressionLineage decorator. "
                "Generating placeholder report."
            )
            content = self._generate_placeholder_report()
        else:
            # Generate full report with expression data
            content = self._generate_expression_catalog(expressions, lineage_graph)

        # Write report
        return self._write_report(content, output_path)

    def _extract_expressions(self, lineage_graph) -> List[Dict[str, Any]]:
        """
        Extract expression metadata from tracker._expression_lineages.

        Args:
            lineage_graph: EnhancedLineageGraph

        Returns:
            List of expression metadata dictionaries
        """
        expressions = []

        # Get tracker instance
        from ..core.lineage_tracker import get_enhanced_tracker
        tracker = get_enhanced_tracker()

        # Check if tracker has expression lineages
        if not hasattr(tracker, '_expression_lineages'):
            return expressions

        # Extract expressions from tracker
        for expr_data in tracker._expression_lineages:
            # expr_data structure: {'function_name': str, 'expressions': dict, 'metadata': dict, 'timestamp': float}
            function_name = expr_data.get('function_name', 'unknown')
            captured_expressions = expr_data.get('expressions', {})
            metadata = expr_data.get('metadata', {})

            # Get business concept from metadata
            business_concept = metadata.get('business_concept', function_name)

            # Extract each column expression
            for col_name, expr_obj in captured_expressions.items():
                # expr_obj is a ColumnExpression object (dataclass)
                # Access attributes directly instead of using .get()
                expressions.append({
                    'column_name': col_name,
                    'expression': expr_obj.expression if hasattr(expr_obj, 'expression') else str(expr_obj),
                    'source_columns': expr_obj.source_columns if hasattr(expr_obj, 'source_columns') else [],
                    'operation_type': expr_obj.operation_type if hasattr(expr_obj, 'operation_type') else 'transform',
                    'complexity_level': expr_obj.complexity_level if hasattr(expr_obj, 'complexity_level') else 1,
                    'sql_equivalent': self._generate_sql_equivalent(col_name, expr_obj.expression if hasattr(expr_obj, 'expression') else ''),
                    'created_in': function_name,
                    'business_concept': business_concept
                })

        # Build expression map for expansion
        self._expression_map = {expr['column_name']: expr['expression'] for expr in expressions}

        # Add expanded expressions if configured
        if self.config.include_expanded_expressions:
            for expr in expressions:
                expr['expanded_expression'] = self._expand_expression(
                    expr['expression'],
                    depth=0
                )

        return expressions

    def _get_variable_color(self, var_name: str) -> tuple:
        """
        Generate a consistent color for a variable using HSL color space.
        Returns theme-appropriate colors based on config.

        NOTE: This color system is designed for future HTML export functionality.
        For markdown output, colors are currently disabled but the infrastructure
        remains in place for when HTML export is implemented.

        Args:
            var_name: Variable name to generate color for

        Returns:
            Tuple of (background_color, text_color, border_color) based on theme
        """
        # Use hash to get deterministic hue (0-359 degrees)
        hash_val = hash(var_name) % 360

        # Get theme from config
        theme = self.config.color_theme

        if theme == "light":
            # Light theme: pastel background (high lightness), dark text
            bg_color = f"hsl({hash_val}, 70%, 85%)"
            text_color = f"hsl({hash_val}, 80%, 20%)"
            border_color = f"hsl({hash_val}, 60%, 60%)"
        else:  # dark theme
            # Dark theme: muted background (low lightness), bright text
            bg_color = f"hsl({hash_val}, 40%, 25%)"
            text_color = f"hsl({hash_val}, 70%, 85%)"
            border_color = f"hsl({hash_val}, 50%, 50%)"

        return (bg_color, text_color, border_color)

    def _wrap_with_color(self, text: str, var_name: str) -> str:
        """
        Wrap text with colored HTML span for highlighting.

        NOTE: Color-coding is currently disabled for markdown output but kept
        for future HTML export functionality. When enable_color_coding=True,
        this will add visual highlighting to expression expansions.

        Args:
            text: Text to wrap
            var_name: Variable name (determines color)

        Returns:
            Plain text (current) or HTML span with inline CSS (future HTML export)
        """
        # TODO: Enable color-coding when HTML export is implemented
        if not self.config.enable_color_coding:
            # For markdown, just return plain text
            return text

        # Future HTML export: Apply theme-specific colors
        bg_color, text_color, border_color = self._get_variable_color(var_name)

        return (
            f'<span style="background-color: {bg_color}; '
            f'color: {text_color}; '
            f'border: 1px solid {border_color}; '
            f'padding: 2px 4px; '
            f'border-radius: 3px;" '
            f'title="{var_name}">{text}</span>'
        )

    def _expand_expression(self, expression: str, depth: int = 0, visited: set = None, color_code: bool = True) -> str:
        """
        Recursively expand an expression by substituting referenced columns with their definitions.
        Optionally adds color-coding to highlight which parts come from which variables.

        Args:
            expression: The expression to expand
            depth: Current recursion depth
            visited: Set of column names already visited (to prevent infinite loops)
            color_code: Whether to add color-coding (HTML spans) to expansions

        Returns:
            Fully expanded expression string with optional color-coding
        """
        if visited is None:
            visited = set()

        # Stop if max depth reached
        if depth >= self.config.max_expansion_depth:
            return expression

        # Try to find column references in the expression
        import re

        # Pattern to match column references (word boundaries to avoid partial matches)
        # Matches column names that appear as complete tokens
        expanded = expression

        for col_name, col_expr in self._expression_map.items():
            # Skip if we've already visited this column (circular reference)
            if col_name in visited:
                continue

            # Create pattern to match this column name as a whole word
            # Match column name but not as part of another word
            pattern = r'\b' + re.escape(col_name) + r'\b'

            # Check if this column appears in the expression
            if re.search(pattern, expanded):
                # Mark as visited
                new_visited = visited.copy()
                new_visited.add(col_name)

                # Recursively expand the column's expression (without color-coding in nested calls)
                substitution = self._expand_expression(col_expr, depth + 1, new_visited, color_code=False)

                # Wrap substitution in parentheses to preserve order of operations
                substitution_wrapped = f"({substitution})"

                # Add color-coding if enabled and this is the top-level expansion
                if color_code and depth == 0:
                    substitution_wrapped = self._wrap_with_color(substitution_wrapped, col_name)

                # Replace all occurrences
                expanded = re.sub(pattern, substitution_wrapped, expanded)

        return expanded

    def _format_sql_pseudocode(self, code: str) -> str:
        """
        Format SQL/pseudocode for improved readability.

        Applies simple formatting rules:
        - Indents WHEN/THEN/ELSE clauses in CASE statements
        - Adds line breaks for better readability
        - Preserves expression logic while improving presentation

        Args:
            code: SQL or pseudocode expression

        Returns:
            Formatted code string
        """
        if not code or 'CASE' not in code.upper():
            return code

        # Simple CASE statement formatting
        formatted = code

        # Add line breaks and indentation for CASE statements
        import re

        # Pattern to match CASE...END blocks
        case_pattern = r'(CASE\s+WHEN\s+.*?\s+END)'

        def format_case(match):
            case_expr = match.group(0)

            # Add line breaks before WHEN, ELSE, and END
            case_expr = re.sub(r'\s+WHEN\s+', '\n  WHEN ', case_expr, flags=re.IGNORECASE)
            case_expr = re.sub(r'\s+THEN\s+', ' THEN ', case_expr, flags=re.IGNORECASE)
            case_expr = re.sub(r'\s+ELSE\s+', '\n  ELSE ', case_expr, flags=re.IGNORECASE)
            case_expr = re.sub(r'\s+END', '\n  END', case_expr, flags=re.IGNORECASE)

            return case_expr

        formatted = re.sub(case_pattern, format_case, formatted, flags=re.IGNORECASE | re.DOTALL)

        return formatted

    # NOTE: Theme controls and interactive features removed for markdown output.
    # The following methods are preserved for future HTML export functionality:
    #
    # def _generate_theme_controls(self) -> List[str]:
    #     """Generate HTML/CSS/JS for theme switching (future HTML export)"""
    #     # TODO: Implement when HTML export is added
    #     pass
    #
    # def _generate_control_panel(self) -> List[str]:
    #     """Generate control panel for theme/highlighting (future HTML export)"""
    #     # TODO: Implement when HTML export is added
    #     pass

    def _generate_expression_catalog(
        self,
        expressions: List[Dict[str, Any]],
        lineage_graph
    ) -> str:
        """
        Generate full expression catalog with all expressions.

        Args:
            expressions: List of expression metadata
            lineage_graph: EnhancedLineageGraph

        Returns:
            Markdown content
        """
        config = self.config
        lines = []

        # Header
        lines.append("# Expression Documentation")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Total Expressions:** {len(expressions)}")

        # Group by type if configured
        if config.categorize_by_type:
            type_counts = {}
            for expr in expressions:
                op_type = expr.get('operation_type', 'unknown')
                type_counts[op_type] = type_counts.get(op_type, 0) + 1

            lines.append("- **By Type:**")
            for op_type, count in sorted(type_counts.items()):
                lines.append(f"  - {op_type.title()}: {count}")

        lines.append("")

        # Purpose (collapsible)
        lines.append("<details>")
        lines.append("<summary><b>Purpose</b></summary>")
        lines.append("")
        lines.append("This report provides a comprehensive catalog of all column expressions and their derivations ")
        lines.append("within your data pipeline. It helps you:")
        lines.append("")
        lines.append("- **Understand Complex Logic**: See exactly how derived columns are calculated from source data")
        lines.append("- **Track Dependencies**: Identify which source columns feed into each calculation")
        lines.append("- **Debug Data Issues**: Trace back from final outputs to understand transformation logic")
        lines.append("- **Document Business Rules**: Maintain clear records of calculation formulas and conditional logic")
        lines.append("- **Onboard Team Members**: Provide newcomers with clear documentation of data transformations")
        lines.append("")
        lines.append("</details>")
        lines.append("")

        # Add standardized metadata section
        lines.extend(self._generate_metadata_section())

        lines.append("")
        lines.append("---")
        lines.append("")

        # Sort expressions
        sorted_expressions = self._sort_expressions(expressions)

        # Expression Summary
        if config.include_summary_table:
            lines.append("## Expression Summary")
            lines.append("")
            lines.extend(self._generate_summary_table(sorted_expressions))
            lines.append("")

        # Expression Impact Diagram (after summary)
        if config.include_diagram and sorted_expressions:
            lines.append("## Expression Impact Diagram")
            lines.append("")
            lines.append("*Visual representation of expression dependencies and data flow*")
            lines.append("")
            lines.extend(self._generate_impact_diagram(sorted_expressions, config))
            lines.append("")

        lines.append("---")
        lines.append("")

        # Document each expression
        lines.append("## Expression Catalog")
        lines.append("")

        for expr in sorted_expressions:
            lines.extend(self._format_expression_section(expr))

        lines.append("---")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc - Expression Documentation Report*")
        lines.append("")

        return "\n".join(lines)

    def _generate_placeholder_report(self) -> str:
        """
        Generate placeholder report when no expression data is available.

        Returns:
            Markdown content
        """
        lines = []

        lines.append("# Expression Documentation")
        lines.append("")
        lines.append("*Catalog of column expressions and derivations*")
        lines.append("")
        lines.append(f"**Generated:** {self._format_timestamp(time.time())}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Status: Expression Lineage Not Available")
        lines.append("")
        lines.append("No expression lineage data was found in the pipeline.")
        lines.append("")
        lines.append("### How to Enable Expression Tracking")
        lines.append("")
        lines.append("Use the `@expressionLineage` decorator to track column expressions:")
        lines.append("")
        lines.append("```python")
        lines.append("from pyspark_storydoc import expressionLineage, track_lineage")
        lines.append("")
        lines.append("@expressionLineage(['profit_margin', 'total_revenue'])")
        lines.append("@track_lineage(materialize=True)")
        lines.append("def calculate_metrics(df):")
        lines.append("    df = df.withColumn('revenue', col('price') * col('quantity'))")
        lines.append("    df = df.withColumn('profit', col('revenue') - col('cost'))")
        lines.append("    df = df.withColumn('profit_margin', ")
        lines.append("                        (col('profit') / col('revenue')) * 100)")
        lines.append("    return df")
        lines.append("```")
        lines.append("")
        lines.append("### Benefits of Expression Tracking")
        lines.append("")
        lines.append("- **Documentation**: Automatically document complex formulas")
        lines.append("- **Understanding**: See how derived columns are calculated")
        lines.append("- **Dependencies**: Track which source columns feed into calculations")
        lines.append("- **SQL Generation**: Get SQL equivalents for documentation")
        lines.append("- **Complexity Analysis**: Identify complex calculations that may need optimization")
        lines.append("")
        lines.append("### Future Enhancement")
        lines.append("")
        lines.append("This report will automatically populate when expression lineage tracking ")
        lines.append("is integrated into the main EnhancedLineageGraph structure.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc - Expression Documentation Report*")
        lines.append("")

        return "\n".join(lines)

    def _generate_summary_table(self, expressions: List[Dict[str, Any]]) -> List[str]:
        """
        Generate a simple summary table of expressions (Column, Type, Sources only).

        Args:
            expressions: List of expression metadata

        Returns:
            List of markdown table lines
        """
        lines = []

        # Simple table header
        lines.append("| Column | Type | Sources |")
        lines.append("|--------|------|---------|")

        # Table rows - just metadata, no code
        for expr in expressions:
            col_name = expr.get('column_name', 'unknown')
            op_type = expr.get('operation_type', 'unknown')
            sources = expr.get('source_columns', [])

            # Format sources
            sources_str = ", ".join(f"`{s}`" for s in sources) if sources else "-"

            # Add table row
            lines.append(f"| **{col_name}** | {op_type.title()} | {sources_str} |")

        return lines

    def _sort_expressions(self, expressions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort expressions according to configuration."""
        sort_by = self.config.sort_by

        if sort_by == "name":
            return sorted(expressions, key=lambda x: x.get('column_name', ''))
        elif sort_by == "complexity":
            return sorted(
                expressions,
                key=lambda x: x.get('complexity_level', 0),
                reverse=True
            )
        else:  # creation_order (default)
            return expressions

    def _classify_expression_type(self, expression: str) -> str:
        """
        Classify the type of expression based on its content.

        Args:
            expression: Expression string

        Returns:
            Classification string
        """
        expr_lower = expression.lower()

        if 'case when' in expr_lower or 'when(' in expr_lower:
            return 'conditional'
        elif any(op in expression for op in ['+', '-', '*', '/', '%']):
            return 'arithmetic'
        elif 'concat' in expr_lower or '||' in expression:
            return 'string'
        elif any(func in expr_lower for func in ['sum(', 'avg(', 'count(', 'max(', 'min(']):
            return 'aggregation'
        elif 'cast' in expr_lower or 'as ' in expr_lower:
            return 'type_conversion'
        else:
            return 'transform'

    def _generate_sql_equivalent(self, column_name: str, expression: str) -> str:
        """
        Generate SQL equivalent for an expression.

        Args:
            column_name: Name of the column
            expression: PySpark expression string

        Returns:
            SQL equivalent string
        """
        # Basic conversion of PySpark expressions to SQL
        sql_expr = expression

        # Replace PySpark-specific syntax with SQL equivalents
        replacements = {
            'Column<\'': '',
            '\'>': '',
            'Column<"': '',
            '">': ''
        }

        for old, new in replacements.items():
            sql_expr = sql_expr.replace(old, new)

        return f"{sql_expr} AS {column_name}"

    def _format_expression_section(self, expr: Dict[str, Any]) -> List[str]:
        """
        Format a single expression section.

        Args:
            expr: Expression metadata dictionary

        Returns:
            List of markdown lines
        """
        config = self.config
        lines = []

        col_name = expr.get('column_name', 'unknown')
        lines.append(f"### {col_name}")
        lines.append("")

        # Operation type (removed complexity - it's self-evident from the formula)
        op_type = expr.get('operation_type', 'unknown')
        lines.append(f"**Type:** {op_type.title()}")
        lines.append("")

        # Formula - show full, non-truncated code
        if config.include_formulas and expr.get('expression'):
            formula = expr['expression']
            # Apply formatting to improve readability
            formatted_formula = self._format_sql_pseudocode(formula)

            lines.append("**Formula:**")
            lines.append("```sql")
            lines.append(formatted_formula)
            lines.append("```")
            lines.append("")

        # Expanded Formula - show full, non-truncated code
        if config.include_expanded_expressions and expr.get('expanded_expression'):
            expanded = expr['expanded_expression']
            # Only show if different from original
            if expanded != expr.get('expression'):
                lines.append("**Expanded Formula:**")
                lines.append("")

                # Apply formatting to improve readability
                formatted_expanded = self._format_sql_pseudocode(expanded)

                lines.append("```sql")
                lines.append(formatted_expanded)
                lines.append("```")

                lines.append("")
                lines.append("*This formula shows all intermediate expressions expanded to their base columns.*")
                lines.append("")

        # Dependencies
        if config.include_dependencies and expr.get('source_columns'):
            lines.append("**Dependencies:**")
            for src_col in expr['source_columns']:
                lines.append(f"- `{src_col}`")
            lines.append("")

        # Context
        if expr.get('created_in') or expr.get('business_concept'):
            lines.append("**Context:**")
            if expr.get('business_concept'):
                lines.append(f"- Business Concept: {expr['business_concept']}")
            if expr.get('created_in'):
                lines.append(f"- Created in: {expr['created_in']}")
            lines.append("")

        lines.append("---")
        lines.append("")

        return lines

    def _generate_impact_diagram(
        self,
        expressions: List[Dict[str, Any]],
        config: ExpressionDocumentationConfig
    ) -> List[str]:
        """
        Generate expression impact diagram showing dependencies.

        Args:
            expressions: List of expression metadata
            config: Configuration

        Returns:
            List of markdown lines containing the mermaid diagram
        """
        lines = []

        # Build dependency graph and track column modifications
        dependencies = set()
        all_nodes = set()
        column_modifications = {}  # Track if a column modifies itself

        for expr in expressions:
            target = expr['column_name']
            all_nodes.add(target)

            # Check if this column appears in its own source columns (modification)
            sources = expr.get('source_columns', [])
            if target in sources:
                column_modifications[target] = True

            for source in sources:
                all_nodes.add(source)
                # Only add edge if source is different from target
                if source != target:
                    dependencies.add((source, target))

        # Generate Mermaid flowchart
        lines.append("```mermaid")
        lines.append("flowchart TD")

        # Add nodes with just variable names (no formulas)
        for expr in expressions:
            target = expr['column_name']
            lines.append(f"    {target}[\"{target}\"]")

        # Classify nodes based on whether they appear as output of any expression
        # A column is "derived" if it appears as column_name in ANY expression
        # A column is "source" only if it NEVER appears as column_name (only in source_columns)
        all_derived_cols = {e['column_name'] for e in expressions}
        source_cols = all_nodes - all_derived_cols

        # Further classify derived columns by whether they come from aggregations
        aggregation_cols = {e['column_name'] for e in expressions if e.get('operation_type') == 'aggregation'}
        non_aggregation_derived_cols = all_derived_cols - aggregation_cols

        # Add source nodes (those that are dependencies but not expressions)
        for source in source_cols:
            lines.append(f"    {source}[\"{source}\"]")

        # Add edges
        for source, target in dependencies:
            lines.append(f"    {source} --> {target}")

        # Add self-referring edges for modified columns
        for col in column_modifications:
            lines.append(f"    {col} --> {col}")

        # Style with accessible dark-theme colors
        lines.append("")
        lines.append("    classDef source fill:#134e4a,stroke:#14B8A6,stroke-width:2px,color:#fff")
        lines.append("    classDef derived fill:#7c2d12,stroke:#F97316,stroke-width:2px,color:#fff")
        lines.append("    classDef aggregation fill:#4c1d95,stroke:#A78BFA,stroke-width:2px,color:#fff")

        # Apply classification
        if source_cols:
            lines.append(f"    class {','.join(sorted(source_cols))} source")
        if non_aggregation_derived_cols:
            lines.append(f"    class {','.join(sorted(non_aggregation_derived_cols))} derived")
        if aggregation_cols:
            lines.append(f"    class {','.join(sorted(aggregation_cols))} aggregation")

        lines.append("```")

        return lines
