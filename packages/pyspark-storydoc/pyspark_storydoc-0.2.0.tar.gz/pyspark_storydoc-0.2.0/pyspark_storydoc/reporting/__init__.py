"""
Modular reporting system for PySpark StoryDoc.

This module provides a flexible, composable reporting system that allows
users to generate individual reports or combine them into comprehensive
pipeline documentation.

Report Types:
    - BusinessConceptCatalog: Textual documentation of business concepts
    - BusinessFlowDiagram: Visual Mermaid diagrams with configurable detail (supports hierarchy)
    - DistributionReport: Statistical analysis wrapper
    - ExpressionDocumentationReport: Column expression documentation (placeholder)
    - ExpressionImpactDiagramReport: Visual expression dependencies (placeholder)
    - ComprehensivePipelineReport: Combined multi-report output
    - HierarchicalDiagram: DEPRECATED - use BusinessFlowDiagram with group_by_context=True

Example Usage:
    >>> from pyspark_storydoc.reporting import (
    ...     BusinessConceptCatalog,
    ...     generate_comprehensive_report
    ... )
    >>>
    >>> # Generate individual report
    >>> catalog = BusinessConceptCatalog(include_metrics=True)
    >>> catalog.generate(lineage_graph, "reports/catalog.md")
    >>>
    >>> # Generate comprehensive report
    >>> generate_comprehensive_report(
    ...     lineage_graph,
    ...     output_path="reports/complete.md",
    ...     include_reports=["business_catalog", "business_diagram"]
    ... )
"""

from typing import Any, Dict, List

from .base_report import BaseReport, ReportConfig
from .business_concept_catalog import (
    BusinessConceptCatalog,
    BusinessConceptCatalogConfig,
)
from .business_flow_diagram import BusinessFlowDiagram, BusinessFlowDiagramConfig
from .comprehensive_report import (
    ComprehensivePipelineReport,
    ComprehensivePipelineReportConfig,
)
from .concept_relationship_diagram import (
    ConceptRelationshipConfig,
    ConceptRelationshipDiagram,
    generate_concept_relationship_diagram,
)
from .data_engineer_report import (
    DataEngineerReport,
    DataEngineerReportConfig,
    generate_engineer_reports,
)
from .diagram_detail_level import COMPLETE, IMPACTING, MINIMAL, DiagramDetailLevel
from .distribution_report import DistributionReport, DistributionReportConfig
from .enhanced_expression_formatter import (
    EnhancedExpressionFormatter,
    FormattedExpression,
)
from .expression_documentation import (
    ExpressionDocumentationConfig,
    ExpressionDocumentationReport,
)
from .expression_impact_diagram import (
    ExpressionImpactDiagramConfig,
    ExpressionImpactDiagramReport,
)
from .graph_json_export import (
    GraphJsonExport,
    GraphJsonExportConfig,
    generate_graph_json,
)
from .hierarchical_diagram import (
    HierarchicalDiagram,  # DEPRECATED: Use BusinessFlowDiagram instead
)
from .hierarchical_diagram import (
    HierarchicalDiagramConfig,  # DEPRECATED: Use BusinessFlowDiagramConfig instead
)
from .hierarchical_diagram import (
    generate_hierarchical_diagram,  # DEPRECATED: Use generate_business_diagram() instead
)
from .report_all import quickReport, reportAll

# Convenience functions


def generate_business_catalog(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Business Concept Catalog report.

    Args:
        lineage_graph: EnhancedLineageGraph to document
        output_path: Path to write the report
        **kwargs: Configuration options for BusinessConceptCatalogConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_business_catalog(
        ...     graph,
        ...     "reports/catalog.md",
        ...     include_metrics=True,
        ...     sort_by="name"
        ... )
    """
    catalog = BusinessConceptCatalog(**kwargs)
    return catalog.generate(lineage_graph, output_path)


def generate_business_diagram(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Business Flow Diagram report.

    Args:
        lineage_graph: EnhancedLineageGraph to visualize
        output_path: Path to write the report
        **kwargs: Configuration options for BusinessFlowDiagramConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_business_diagram(
        ...     graph,
        ...     "reports/diagram.md",
        ...     detail_level="impacting",
        ...     show_metrics=True
        ... )
    """
    diagram = BusinessFlowDiagram(**kwargs)
    return diagram.generate(lineage_graph, output_path)


def generate_distribution_report(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Distribution Analysis Report.

    Args:
        lineage_graph: EnhancedLineageGraph with distribution data
        output_path: Path to write the report
        **kwargs: Configuration options for DistributionReportConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_distribution_report(
        ...     graph,
        ...     "reports/distribution.md",
        ...     include_cross_analysis=True
        ... )
    """
    report = DistributionReport(**kwargs)
    return report.generate(lineage_graph, output_path)


def generate_expression_documentation(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Expression Documentation Report.

    NOTE: This is a placeholder for future expression lineage integration.
    Will generate full report when @expressionLineage decorator data is available.

    Args:
        lineage_graph: EnhancedLineageGraph with expression data
        output_path: Path to write the report
        **kwargs: Configuration options for ExpressionDocumentationConfig
            color_theme: "dark" or "light" (for future HTML export)
            enable_color_coding: Enable color-coded expansions (for future HTML export)
            include_formulas: Include reconstructed formulas
            include_expanded_expressions: Show fully expanded expressions
            sort_by: Sort expressions by "name", "complexity", or "creation_order"
            ... (see ExpressionDocumentationConfig for all options)

    Returns:
        Path to generated report

    Example:
        >>> generate_expression_documentation(
        ...     graph,
        ...     "reports/expressions.md",
        ...     include_formulas=True,
        ...     sort_by="complexity",
        ...     color_theme="dark"
        ... )
    """
    report = ExpressionDocumentationReport(**kwargs)
    return report.generate(lineage_graph, output_path)


def generate_expression_impact_diagram(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Expression Impact Diagram.

    NOTE: This is a placeholder for future expression lineage integration.
    Will generate full diagram when @expressionLineage decorator data is available.

    Args:
        lineage_graph: EnhancedLineageGraph with expression data
        output_path: Path to write the report
        **kwargs: Configuration options for ExpressionImpactDiagramConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_expression_impact_diagram(
        ...     graph,
        ...     "reports/expression_flow.md",
        ...     view_mode="variable_flow",
        ...     show_annotations=True
        ... )
    """
    report = ExpressionImpactDiagramReport(**kwargs)
    return report.generate(lineage_graph, output_path)


def generate_comprehensive_report(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Comprehensive Pipeline Report combining multiple sub-reports.

    Args:
        lineage_graph: EnhancedLineageGraph to analyze
        output_path: Path to write the combined report
        **kwargs: Configuration options for ComprehensivePipelineReportConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_comprehensive_report(
        ...     graph,
        ...     "reports/complete.md",
        ...     title="My Pipeline Analysis",
        ...     include_reports=["business_catalog", "business_diagram"],
        ...     generate_individual_files=True
        ... )
    """
    report = ComprehensivePipelineReport(**kwargs)
    return report.generate(lineage_graph, output_path)


def generate_data_engineer_report(lineage_graph, output_path: str, **kwargs) -> str:
    """
    Generate Data Engineer Report with debugging support.

    Args:
        lineage_graph: EnhancedLineageGraph to analyze
        output_path: Path to write the report
        **kwargs: Configuration options for DataEngineerReportConfig

    Returns:
        Path to generated report

    Example:
        >>> generate_data_engineer_report(
        ...     graph,
        ...     "reports/pipeline_lineage.md",
        ...     pipeline_name="Customer Enrichment",
        ...     track_columns=["customer_id", "email"]
        ... )
    """
    report = DataEngineerReport(**kwargs)
    return report.generate(lineage_graph, output_path)


def generate_expression_lineage_report(
    lineage_graph,
    output_dir: str,
    include_html: bool = True,
    include_impact_tree: bool = True,
    **kwargs
) -> Dict[str, str]:
    """
    Generate comprehensive expression lineage report.

    This function generates an enhanced expression lineage report with
    complexity analysis, impact assessment, and optional interactive HTML.

    Args:
        lineage_graph: EnhancedLineageGraph with expression metadata
        output_dir: Directory to write report files
        include_html: Generate interactive HTML explorer (default: True)
        include_impact_tree: Generate impact tree markdown (default: True)
        **kwargs: Additional configuration options

    Returns:
        Dictionary mapping report names to file paths:
            - expression_documentation: Enhanced expression docs (markdown)
            - expression_impact_diagram: Expression dependency diagram (markdown)
            - impact_tree: Impact tree visualization (markdown, if enabled)
            - html_explorer: Interactive HTML explorer (if enabled)

    Example:
        >>> reports = generate_expression_lineage_report(
        ...     graph,
        ...     "outputs/expressions",
        ...     include_html=True
        ... )
        >>> print(f"Documentation: {reports['expression_documentation']}")
        >>> print(f"HTML Explorer: {reports.get('html_explorer', 'Not generated')}")
    """
    from pathlib import Path

    from ..analysis import ImpactAnalyzer
    from ..visualization.interactive_expression_explorer import (
        InteractiveExpressionExplorer,
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {}

    # Generate enhanced expression documentation
    expr_doc_path = output_path / "expression_documentation.md"
    results['expression_documentation'] = generate_expression_documentation(
        lineage_graph,
        str(expr_doc_path),
        **kwargs
    )

    # Generate expression impact diagram
    impact_diagram_path = output_path / "expression_impact_diagram.md"
    results['expression_impact_diagram'] = generate_expression_impact_diagram(
        lineage_graph,
        str(impact_diagram_path),
        **kwargs
    )

    # Get expressions from tracker for enhanced features
    from ..core.lineage_tracker import get_enhanced_tracker
    tracker = get_enhanced_tracker()

    if hasattr(tracker, '_expression_lineages') and tracker._expression_lineages:
        expressions = []
        for expr_data in tracker._expression_lineages:
            captured_expressions = expr_data.get('expressions', {})
            function_name = expr_data.get('function_name', 'unknown')
            metadata = expr_data.get('metadata', {})

            for col_name, expr_obj in captured_expressions.items():
                expressions.append({
                    'column_name': col_name,
                    'expression': expr_obj.expression if hasattr(expr_obj, 'expression') else str(expr_obj),
                    'source_columns': expr_obj.source_columns if hasattr(expr_obj, 'source_columns') else [],
                    'operation_type': expr_obj.operation_type if hasattr(expr_obj, 'operation_type') else 'transform',
                    'complexity_level': expr_obj.complexity_level if hasattr(expr_obj, 'complexity_level') else 1,
                    'created_in': function_name,
                    'business_concept': metadata.get('business_concept', function_name)
                })

        # Build impact analyzer
        impact_analyzer = ImpactAnalyzer()
        impact_analyzer.build_dependency_graph(expressions)

        # Generate impact tree if requested
        if include_impact_tree:
            impact_tree_path = output_path / "expression_impact_tree.md"
            impact_tree_content = _generate_impact_tree_markdown(
                expressions,
                impact_analyzer
            )
            impact_tree_path.write_text(impact_tree_content, encoding='utf-8')
            results['impact_tree'] = str(impact_tree_path)

        # Generate interactive HTML if requested
        if include_html:
            html_path = output_path / "expression_explorer.html"
            explorer = InteractiveExpressionExplorer()
            html_file = explorer.generate_html(
                expressions,
                impact_analyzer,
                str(html_path),
                title="Expression Lineage Explorer"
            )
            results['html_explorer'] = html_file

    return results


def _generate_impact_tree_markdown(
    expressions: List[Dict[str, Any]],
    impact_analyzer
) -> str:
    """
    Generate markdown document with impact trees for all expressions.

    Args:
        expressions: List of expression metadata
        impact_analyzer: ImpactAnalyzer instance

    Returns:
        Markdown content
    """
    lines = []

    lines.append("# Expression Impact Trees")
    lines.append("")
    lines.append("*Hierarchical view of downstream dependencies*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Get summary statistics
    summary = impact_analyzer.get_impact_summary()

    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- **Total Columns:** {summary['total_columns']}")
    lines.append(f"- **Source Columns:** {summary['source_columns']}")
    lines.append(f"- **Derived Columns:** {summary['derived_columns']}")
    lines.append(f"- **Leaf Columns:** {summary['leaf_columns']}")
    lines.append(f"- **Max Chain Length:** {summary['max_chain_length']}")
    lines.append(f"- **Avg Dependencies:** {summary['avg_dependencies']}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Find critical paths
    critical_paths = impact_analyzer.find_critical_paths()

    if critical_paths:
        lines.append("## Critical Paths")
        lines.append("")
        lines.append("*Longest dependency chains that may represent fragility*")
        lines.append("")

        for i, path_info in enumerate(critical_paths[:5], 1):  # Top 5
            path = path_info['path']
            length = path_info['length']
            complexity_sum = path_info['complexity_sum']
            risk = path_info['risk']

            lines.append(f"### Path {i}: {' → '.join(path)}")
            lines.append("")
            lines.append(f"- **Length:** {length} hops")
            lines.append(f"- **Total Complexity:** {complexity_sum}")
            lines.append(f"- **Risk Level:** {risk}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Generate impact trees for key columns
    lines.append("## Individual Impact Trees")
    lines.append("")

    # Show trees for derived columns only
    derived_expressions = [
        expr for expr in expressions
        if expr.get('source_columns')
    ]

    for expr in derived_expressions[:10]:  # Limit to first 10 to avoid huge files
        col_name = expr['column_name']
        impact = impact_analyzer.analyze_column_impact(col_name)

        lines.append(f"### `{col_name}`")
        lines.append("")
        lines.append(f"**Impact:** {impact['total_impact']} downstream columns")
        lines.append("")
        lines.append("```")
        tree_text = impact_analyzer.format_impact_tree_text(impact['impact_tree'])
        lines.append(tree_text)
        lines.append("```")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated by PySpark StoryDoc - Expression Impact Tree Report*")
    lines.append("")

    return "\n".join(lines)


__all__ = [
    # Base classes
    'BaseReport',
    'ReportConfig',

    # Report implementations
    'BusinessConceptCatalog',
    'BusinessConceptCatalogConfig',
    'BusinessFlowDiagram',
    'BusinessFlowDiagramConfig',
    'HierarchicalDiagram',
    'HierarchicalDiagramConfig',
    'ConceptRelationshipDiagram',
    'ConceptRelationshipConfig',
    'GraphJsonExport',
    'GraphJsonExportConfig',
    'DistributionReport',
    'DistributionReportConfig',
    'ExpressionDocumentationReport',
    'ExpressionDocumentationConfig',
    'ExpressionImpactDiagramReport',
    'ExpressionImpactDiagramConfig',
    'EnhancedExpressionFormatter',
    'FormattedExpression',
    'ComprehensivePipelineReport',
    'ComprehensivePipelineReportConfig',
    'DataEngineerReport',
    'DataEngineerReportConfig',

    # Detail level constants
    'DiagramDetailLevel',
    'MINIMAL',
    'IMPACTING',
    'COMPLETE',

    # Convenience functions
    'generate_business_catalog',
    'generate_business_diagram',
    'generate_hierarchical_diagram',
    'generate_concept_relationship_diagram',
    'generate_graph_json',
    'generate_distribution_report',
    'generate_expression_documentation',
    'generate_expression_impact_diagram',
    'generate_comprehensive_report',
    'generate_data_engineer_report',
    'generate_engineer_reports',
    'generate_expression_lineage_report',
    'reportAll',
    'quickReport',
]

__version__ = '2.0.0'
