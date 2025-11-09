#!/usr/bin/env python3
"""
Expression Impact Diagram for PySpark StoryDoc.

NOTE: This is a placeholder implementation for future expression lineage integration.
Once expression lineage tracking is fully integrated into EnhancedLineageGraph,
this report will automatically generate visual diagrams showing expression dependencies.

Current Status:
- Framework and structure are complete
- Will activate when expression metadata is available in the graph
- Designed to work with @expressionLineage decorator outputs
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class ExpressionImpactDiagramConfig(ReportConfig):
    """
    Configuration for expression impact diagram.

    Attributes:
        view_mode: Diagram view mode
            - "expression_centric": Focus on specific expression and its dependencies
            - "variable_flow": Show how variables flow through transformations
            - "dependency_tree": Hierarchical tree of all dependencies
        target_expression: Specific expression to highlight (for expression_centric mode)
        show_annotations: Show formula annotations on edges
        highlight_modifications: Highlight where variables are modified
        max_depth: Maximum dependency depth to show (for dependency_tree mode)
        orientation: Diagram orientation ("TD", "LR", "BT", "RL")
        include_legend: Include diagram legend
    """
    view_mode: str = "variable_flow"  # "expression_centric", "variable_flow", "dependency_tree"
    target_expression: Optional[str] = None
    show_annotations: bool = True
    highlight_modifications: bool = True
    max_depth: int = 5
    orientation: str = "TD"
    include_legend: bool = True


class ExpressionImpactDiagramReport(BaseReport):
    """
    Generates visual diagrams showing expression lineage and dependencies.

    This report creates Mermaid diagrams that visualize how expressions are built
    from source columns and intermediate calculations.

    View Modes:
        1. Expression-Centric: Focuses on a specific expression showing all its dependencies
        2. Variable Flow: Shows how variables flow and transform through the pipeline
        3. Dependency Tree: Hierarchical view of all expression dependencies

    Example Output (Variable Flow):
        ```mermaid
        flowchart TD
            price[price] --> revenue
            quantity[quantity] --> revenue
            revenue[revenue = price * quantity] --> profit
            cost[cost] --> profit
            profit[profit = revenue - cost] --> margin
            revenue --> margin
            margin[profit_margin = (profit / revenue) * 100]
        ```
    """

    def __init__(self, config: Optional[ExpressionImpactDiagramConfig] = None, **kwargs):
        """
        Initialize the expression impact diagram report.

        Args:
            config: Report configuration
            **kwargs: Alternative way to pass config options
        """
        if config is None and kwargs:
            config = ExpressionImpactDiagramConfig(**kwargs)
        super().__init__(config or ExpressionImpactDiagramConfig())

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate expression impact diagram report.

        Args:
            lineage_graph: EnhancedLineageGraph with expression metadata
            output_path: Output file path

        Returns:
            Path to generated report
        """
        logger.info(f"Generating expression impact diagram ({self.config.view_mode} mode)...")

        # Extract expression data
        expressions = self._extract_expressions(lineage_graph)

        # Check if expressions are available
        if not expressions:
            logger.warning(
                "No expression lineage data found in graph. "
                "Generating placeholder report."
            )
            content = self._generate_placeholder_report()
        else:
            # Generate diagram based on view mode
            content = self._generate_impact_diagram(expressions, lineage_graph)

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

            # Extract each column expression
            for col_name, expr_obj in captured_expressions.items():
                # expr_obj is a ColumnExpression object (dataclass)
                expressions.append({
                    'column_name': col_name,
                    'expression': expr_obj.expression if hasattr(expr_obj, 'expression') else str(expr_obj),
                    'source_columns': expr_obj.source_columns if hasattr(expr_obj, 'source_columns') else [],
                    'operation_type': expr_obj.operation_type if hasattr(expr_obj, 'operation_type') else metadata.get('operation_type', 'transform'),
                    'created_in': function_name
                })

        return expressions

    def _generate_impact_diagram(
        self,
        expressions: List[Dict[str, Any]],
        lineage_graph
    ) -> str:
        """
        Generate expression impact diagram.

        Args:
            expressions: List of expression metadata
            lineage_graph: EnhancedLineageGraph

        Returns:
            Markdown content
        """
        config = self.config
        lines = []

        # Header
        lines.append("# Expression Impact Diagram")
        lines.append("")
        lines.append("*Visual representation of expression dependencies and data flow*")
        lines.append("")
        lines.append(f"**View Mode:** {config.view_mode.replace('_', ' ').title()}")

        # Add standardized metadata section
        lines.extend(self._generate_metadata_section())

        lines.append("")
        lines.append("---")
        lines.append("")

        # Description based on view mode (moved from Diagram Description section)
        lines.append(self._get_view_mode_description(config.view_mode))
        lines.append("")

        # Generate diagram based on view mode
        if config.view_mode == "expression_centric":
            mermaid_diagram = self._generate_expression_centric_diagram(expressions, config)
        elif config.view_mode == "dependency_tree":
            mermaid_diagram = self._generate_dependency_tree_diagram(expressions, config)
        else:  # variable_flow
            mermaid_diagram = self._generate_variable_flow_diagram(expressions, config)

        lines.append("```mermaid")
        lines.append(mermaid_diagram)
        lines.append("```")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc - Expression Impact Diagram*")
        lines.append("")

        return "\n".join(lines)

    def _generate_placeholder_report(self) -> str:
        """Generate placeholder report when no expression data is available."""
        lines = []

        lines.append("# Expression Impact Diagram")
        lines.append("")
        lines.append("*Visual representation of expression dependencies and data flow*")
        lines.append("")

        # Add standardized metadata section
        lines.extend(self._generate_metadata_section())

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Status: Expression Lineage Not Available")
        lines.append("")
        lines.append("No expression lineage data was found in the pipeline.")
        lines.append("")
        lines.append("### How to Enable Expression Tracking")
        lines.append("")
        lines.append("Use the `@expressionLineage` decorator to track expressions:")
        lines.append("")
        lines.append("```python")
        lines.append("from pyspark_storydoc import expressionLineage, track_lineage")
        lines.append("")
        lines.append("@expressionLineage(['revenue', 'profit', 'profit_margin'])")
        lines.append("@track_lineage(materialize=True)")
        lines.append("def calculate_metrics(df):")
        lines.append("    df = df.withColumn('revenue', col('price') * col('quantity'))")
        lines.append("    df = df.withColumn('profit', col('revenue') - col('cost'))")
        lines.append("    df = df.withColumn('profit_margin',")
        lines.append("                        (col('profit') / col('revenue')) * 100)")
        lines.append("    return df")
        lines.append("```")
        lines.append("")
        lines.append("### Example Diagram Output")
        lines.append("")
        lines.append("Once expression tracking is enabled, you'll see diagrams like:")
        lines.append("")
        lines.append("```mermaid")
        lines.append("flowchart TD")
        lines.append("    price[price] --> revenue")
        lines.append("    quantity[quantity] --> revenue")
        lines.append("    revenue[revenue = price * quantity] --> profit")
        lines.append("    cost[cost] --> profit")
        lines.append("    profit[profit = revenue - cost] --> margin")
        lines.append("    revenue --> margin")
        lines.append("    margin[profit_margin = profit / revenue * 100]")
        lines.append("```")
        lines.append("")
        lines.append("### Future Enhancement")
        lines.append("")
        lines.append("This report will automatically populate when expression lineage tracking ")
        lines.append("is integrated into the main EnhancedLineageGraph structure.")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by PySpark StoryDoc - Expression Impact Diagram*")
        lines.append("")

        return "\n".join(lines)

    def _get_view_mode_description(self, view_mode: str) -> str:
        """Get description for view mode."""
        descriptions = {
            "expression_centric": (
                "This diagram focuses on a specific expression and shows all its dependencies, "
                "highlighting how the expression is built from source columns and intermediate calculations."
            ),
            "variable_flow": (
                "This diagram shows how variables flow through transformations, illustrating the "
                "step-by-step creation of derived columns from source data."
            ),
            "dependency_tree": (
                "This diagram presents a hierarchical view of expression dependencies, showing the "
                "complete dependency tree for all tracked expressions."
            )
        }
        return descriptions.get(view_mode, "Custom view mode.")

    def _count_unique_columns(self, expressions: List[Dict[str, Any]]) -> int:
        """Count unique columns across all expressions."""
        columns = set()
        for expr in expressions:
            columns.add(expr.get('column_name'))
            columns.update(expr.get('source_columns', []))
        return len(columns)

    def _generate_variable_flow_diagram(
        self,
        expressions: List[Dict[str, Any]],
        config: ExpressionImpactDiagramConfig
    ) -> str:
        """Generate variable flow diagram."""
        lines = []

        # Mermaid header
        lines.append(f"flowchart {config.orientation}")

        # Track all columns and modifications
        all_columns = set()
        dependencies = []
        column_modifications = {}  # Track if a column modifies itself

        # Build dependency graph
        for expr in expressions:
            target = expr['column_name']
            sources = expr.get('source_columns', [])

            all_columns.add(target)
            all_columns.update(sources)

            # Check if this column appears in its own source columns (modification)
            if target in sources:
                column_modifications[target] = True

            # Create edges from sources to target (excluding self-references for now)
            for source in sources:
                if source != target:
                    dependencies.append((source, target))

            # Create node with just variable name
            lines.append(f"    {target}[\"{target}\"]")

        # Classify nodes based on whether they appear as output of any expression
        # A column is "derived" if it appears as column_name in ANY expression
        # A column is "source" only if it NEVER appears as column_name (only in source_columns)
        all_derived_cols = {e['column_name'] for e in expressions}
        source_cols = all_columns - all_derived_cols

        # Further classify derived columns by whether they come from aggregations
        aggregation_cols = {e['column_name'] for e in expressions if e.get('operation_type') == 'aggregation'}
        non_aggregation_derived_cols = all_derived_cols - aggregation_cols

        # Add source nodes (those that are dependencies but never created by expressions)
        for source in source_cols:
            lines.append(f"    {source}[\"{source}\"]")

        # Add edges
        for source, target in dependencies:
            lines.append(f"    {source} --> {target}")

        # Add self-referring edges for modified columns
        for col in column_modifications:
            lines.append(f"    {col} --> {col}")

        # Style nodes with accessible dark-theme colors
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

        return "\n".join(lines)

    def _generate_expression_centric_diagram(
        self,
        expressions: List[Dict[str, Any]],
        config: ExpressionImpactDiagramConfig
    ) -> str:
        """Generate expression-centric diagram focusing on target expression."""
        lines = []
        lines.append(f"flowchart {config.orientation}")

        target_expr = config.target_expression
        if not target_expr and expressions:
            # Use first expression if no target specified
            target_expr = expressions[0]['column_name']

        # Find the target expression
        target_data = next(
            (e for e in expressions if e['column_name'] == target_expr),
            None
        )

        if not target_data:
            lines.append(f"    note[\"Target expression '{target_expr}' not found\"]")
            return "\n".join(lines)

        # Build dependency tree for target
        visited = set()
        self._add_expression_dependencies(
            target_data, expressions, lines, visited, 0, config
        )

        # Highlight target with bright lime color for dark theme
        lines.append("")
        lines.append("    classDef target fill:#3f6212,stroke:#84CC16,stroke-width:3px,color:#fff")
        lines.append(f"    class {target_expr} target")

        return "\n".join(lines)

    def _generate_dependency_tree_diagram(
        self,
        expressions: List[Dict[str, Any]],
        config: ExpressionImpactDiagramConfig
    ) -> str:
        """Generate hierarchical dependency tree."""
        lines = []
        lines.append(f"flowchart {config.orientation}")

        # Build full dependency tree
        # Group by depth level
        depth_map = self._calculate_expression_depths(expressions)

        # Add nodes and edges
        visited = set()
        for expr in expressions:
            if expr['column_name'] not in visited:
                self._add_tree_node(expr, expressions, lines, visited, depth_map, config)

        return "\n".join(lines)

    def _add_expression_dependencies(
        self,
        expr: Dict[str, Any],
        all_expressions: List[Dict[str, Any]],
        lines: List[str],
        visited: set,
        depth: int,
        config: ExpressionImpactDiagramConfig
    ):
        """Recursively add expression dependencies."""
        if depth > config.max_depth:
            return

        col_name = expr['column_name']
        if col_name in visited:
            return

        visited.add(col_name)

        # Add node
        if config.show_annotations:
            formula = expr.get('expression', '')[:50]
            lines.append(f"    {col_name}[\"{col_name} = {formula}\"]")

        # Add dependencies
        for source in expr.get('source_columns', []):
            lines.append(f"    {source} --> {col_name}")

            # Recurse if source is also an expression
            source_expr = next(
                (e for e in all_expressions if e['column_name'] == source),
                None
            )
            if source_expr:
                self._add_expression_dependencies(
                    source_expr, all_expressions, lines, visited, depth + 1, config
                )

    def _add_tree_node(
        self,
        expr: Dict[str, Any],
        all_expressions: List[Dict[str, Any]],
        lines: List[str],
        visited: set,
        depth_map: Dict[str, int],
        config: ExpressionImpactDiagramConfig
    ):
        """Add node to dependency tree."""
        col_name = expr['column_name']
        visited.add(col_name)

        # Add edges to sources
        for source in expr.get('source_columns', []):
            lines.append(f"    {source} --> {col_name}")

    def _calculate_expression_depths(
        self,
        expressions: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate depth of each expression in dependency tree."""
        depth_map = {}

        def calc_depth(col_name: str, visited: set) -> int:
            if col_name in depth_map:
                return depth_map[col_name]

            if col_name in visited:
                return 0  # Circular dependency

            visited.add(col_name)

            # Find expression
            expr = next((e for e in expressions if e['column_name'] == col_name), None)
            if not expr:
                return 0  # Source column

            # Depth is 1 + max depth of dependencies
            sources = expr.get('source_columns', [])
            if not sources:
                depth = 0
            else:
                depth = 1 + max(calc_depth(src, visited.copy()) for src in sources)

            depth_map[col_name] = depth
            return depth

        # Calculate depths
        for expr in expressions:
            calc_depth(expr['column_name'], set())

        return depth_map

    def _generate_legend(self) -> List[str]:
        """Generate diagram legend."""
        lines = []
        lines.append("## Legend")
        lines.append("")
        lines.append("**Node Colors:**")
        lines.append("- **Teal (cyan)**: Source columns from raw data")
        lines.append("- **Orange (coral)**: Derived columns with calculated expressions")
        lines.append("- **Lime (bright green)**: Target expression (expression_centric mode)")
        lines.append("")
        lines.append("**Arrows:**")
        lines.append("- Show data flow from source to derived column")
        lines.append("- Annotated with formulas when enabled")
        lines.append("")
        lines.append("*Colors are optimized for accessibility and dark theme compatibility*")
        lines.append("")

        return lines
