#!/usr/bin/env python3
"""
Report All - Automatic comprehensive report generation.

This module provides a convenience function that automatically generates all
applicable reports based on what tracking features were used in the pipeline.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def reportAll(
    output_dir: str = "outputs",
    output_filename: str = "comprehensive_report.md",
    include_reports: Optional[List[str]] = None,
    auto_detect: bool = True,
    generate_individual_files: bool = True,
    **report_configs
) -> Dict[str, str]:
    """
    Automatically generate all applicable reports based on captured tracking data.

    This function inspects the global tracker to determine what tracking features
    were used (describe profiles, distribution analysis, expression lineage, etc.)
    and automatically generates all applicable reports.

    Args:
        output_dir: Directory to write reports (default: "outputs")
        output_filename: Name of the comprehensive report file (default: "comprehensive_report.md")
        include_reports: Specific reports to include (None = auto-detect all available)
        auto_detect: Whether to auto-detect which reports are applicable (default: True)
        generate_individual_files: Whether to generate individual report files in addition
                                   to the comprehensive report (default: True)
        **report_configs: Additional configuration for specific report types
                         (e.g., business_catalog={'include_metadata': True})

    Returns:
        Dictionary mapping report types to their output file paths

    Examples:
        Basic usage (auto-detect and generate all applicable reports):
        >>> reportAll(output_dir="outputs/car_insurance")

        Generate specific reports only:
        >>> reportAll(
        ...     output_dir="outputs",
        ...     include_reports=["business_diagram", "distribution_analysis"],
        ...     auto_detect=False
        ... )

        Customize specific report configurations:
        >>> reportAll(
        ...     output_dir="outputs",
        ...     business_diagram={'detail_level': 'detailed'},
        ...     distribution_analysis={'include_cross_analysis': True}
        ... )
    """
    from ..core.lineage_tracker import get_enhanced_tracker, get_global_tracker
    from .comprehensive_report import (
        ComprehensivePipelineReport,
        ComprehensivePipelineReportConfig,
    )

    logger.info("Starting reportAll() - Automatic comprehensive report generation")

    # Get the global tracker
    try:
        tracker = get_global_tracker()
        enhanced_tracker = get_enhanced_tracker()
    except Exception as e:
        logger.error(f"Could not access global tracker: {e}")
        return {}

    # Auto-detect which reports are applicable
    if auto_detect:
        available_reports = _detect_available_reports(tracker)
        logger.info(f"Auto-detected {len(available_reports)} applicable report types: {available_reports}")
    else:
        available_reports = include_reports or []

    if not available_reports:
        logger.warning("No reports to generate (no tracking data found or no reports specified)")
        return {}

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Prepare comprehensive report configuration
    config = ComprehensivePipelineReportConfig(
        title="Comprehensive Pipeline Report",
        include_reports=available_reports,
        report_configs=report_configs,
        generate_individual_files=generate_individual_files,
        individual_files_directory=str(output_path / "individual_reports") if generate_individual_files else None
    )

    # Generate comprehensive report
    report_generator = ComprehensivePipelineReport(config=config)

    try:
        # Get the enhanced lineage graph
        lineage_graph = tracker.get_lineage_graph()

        # Generate comprehensive report
        comprehensive_path = str(output_path / output_filename)
        report_generator.generate(lineage_graph, comprehensive_path)

        result = {
            "comprehensive_report": comprehensive_path
        }

        logger.info(f"Comprehensive report generated: {comprehensive_path}")

        # If individual files were generated, add them to results
        if generate_individual_files:
            individual_dir = output_path / "individual_reports"
            if individual_dir.exists():
                for report_type in available_reports:
                    individual_path = individual_dir / f"{report_type}.md"
                    if individual_path.exists():
                        result[report_type] = str(individual_path)

        # Generate distribution plots if distribution analysis is included
        if "distribution_analysis" in available_reports:
            _generate_distribution_plots(tracker, output_path)

        # Generate expression lineage documentation if available
        if "expression_documentation" in available_reports:
            _generate_expression_documentation(tracker, output_path)

        logger.info(f"Successfully generated {len(result)} report files")
        return result

    except Exception as e:
        logger.error(f"Failed to generate reports: {e}")
        import traceback
        traceback.print_exc()
        return {}


def _detect_available_reports(tracker) -> List[str]:
    """
    Detect which report types are applicable based on captured tracking data.

    Args:
        tracker: Global LineageTracker instance

    Returns:
        List of applicable report type identifiers
    """
    available = []

    # Check for business catalog (always available if we have lineage data)
    if hasattr(tracker, 'enhanced_graph') and tracker.enhanced_graph:
        if len(tracker.enhanced_graph.nodes) > 0:
            available.append("business_catalog")
            logger.info(f"Found {len(tracker.enhanced_graph.nodes)} nodes for business catalog")

    # Check for business flow diagram (always available if we have lineage data)
    if hasattr(tracker, 'enhanced_graph') and tracker.enhanced_graph:
        if len(tracker.enhanced_graph.nodes) > 0:
            available.append("business_diagram")
            logger.info(f"Found {len(tracker.enhanced_graph.nodes)} nodes for business diagram")

    # NEW: Check for governance metadata
    if hasattr(tracker, 'enhanced_graph') and tracker.enhanced_graph:
        has_governance = any(
            'governance_metadata' in node.metadata and node.metadata['governance_metadata']
            for node in tracker.enhanced_graph.nodes.values()
            if hasattr(node, 'metadata')
        )
        if has_governance:
            available.append("governance_summary")
            logger.info("Governance metadata detected - adding governance report")

    # NEW: Check for execution metrics (data engineer features)
    if hasattr(tracker, 'enhanced_graph') and tracker.enhanced_graph:
        has_metrics = any(
            'metrics' in node.metadata and node.metadata['metrics']
            for node in tracker.enhanced_graph.nodes.values()
            if hasattr(node, 'metadata')
        )
        if has_metrics:
            available.append("data_engineer_summary")
            logger.info("Execution metrics detected - adding data engineer report")

    # Check for describe profiles
    describe_profiles = getattr(tracker, '_describe_profiles', [])
    if describe_profiles:
        available.append("describe_profiles")
        logger.info(f"Found {len(describe_profiles)} describe profile checkpoints")

    # Check for distribution analysis
    distribution_analyses = getattr(tracker, '_distribution_analyses', [])
    if distribution_analyses:
        available.append("distribution_analysis")
        logger.info(f"Found {len(distribution_analyses)} distribution analysis checkpoints")

    # Check for expression lineage
    expression_lineages = getattr(tracker, '_expression_lineages', [])
    if expression_lineages:
        available.append("expression_documentation")
        logger.info(f"Found {len(expression_lineages)} expression lineage captures")

    # Expression impact diagram (if we have expression lineages)
    if expression_lineages:
        available.append("expression_impact_diagram")

    # NEW: Check for correlation analyses (Data Scientist feature)
    correlation_analyses = getattr(tracker, '_correlation_analyses', [])
    if correlation_analyses:
        available.append("correlation_analysis")
        logger.info(f"Found {len(correlation_analyses)} correlation analysis checkpoints")

    # NEW: Check for feature tracking (Data Scientist feature)
    # Features can be detected from:
    # 1. Target variable tracking
    # 2. Expression lineages (derived features)
    # 3. Correlation analyses (identified features)
    target_variable = getattr(tracker, '_target_variable', None)
    has_feature_data = bool(target_variable or expression_lineages or correlation_analyses)
    if has_feature_data:
        available.append("feature_catalog")
        logger.info("Feature tracking data detected - adding feature catalog")

    # NEW: Check for statistical profiling (Data Scientist feature)
    # Note: This is different from describe_profiles which is basic describe()
    # We already have describe_profiles detection above, but we add statistical_profiling
    # when describe profiles exist to provide advanced statistical analysis
    if describe_profiles:
        available.append("statistical_profiling")
        logger.info("Statistical profiling data available from describe profiles")

    return available


def _generate_distribution_plots(tracker, output_path: Path):
    """
    Generate distribution plots and save them to the assets directory.

    Args:
        tracker: Global LineageTracker instance
        output_path: Base output directory
    """
    distribution_analyses = getattr(tracker, '_distribution_analyses', [])

    if not distribution_analyses:
        return

    logger.info(f"Generating distribution plots for {len(distribution_analyses)} analysis points")

    # Create assets directory
    assets_dir = output_path / "assets" / "distribution_analysis"
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Import visualization tools
    from ..analysis.distribution_analyzer import OutlierMethod
    from ..visualization.distribution_visualizer import (
        DistributionVisualizer,
        PlotConfig,
    )

    visualizer = DistributionVisualizer(
        output_directory=str(assets_dir),
        config=PlotConfig()
    )

    # Generate plots for each analysis point
    for idx, analysis in enumerate(distribution_analyses, 1):
        metadata = analysis.get('metadata', {})
        function_name = analysis.get('function_name', f'analysis_{idx}')

        # Get the DataFrame from the analysis
        df = analysis.get('dataframe')
        if df is None:
            logger.warning(f"No DataFrame found for analysis point {idx} ({function_name})")
            continue

        # Get variables that were analyzed
        variables = metadata.get('variables_analyzed', [])

        logger.info(f"  Generating plots for {function_name}: {variables}")

        # Generate plots for each variable
        for variable in variables:
            try:
                # Generate both raw and cleaned (IQR) plots
                visualizer.create_distribution_plot(
                    df,
                    variable,
                    title=f"{variable.title()} Distribution - {function_name.replace('_', ' ').title()}",
                    sample_size=metadata.get('sample_size', 10000),
                    include_outlier_removal=True,
                    outlier_method=OutlierMethod.NONE,
                    filename_prefix=f"{function_name}_after"
                )

                logger.info(f"    [OK] Generated plots for {variable}")

            except Exception as e:
                logger.warning(f"Failed to generate plot for {variable} in {function_name}: {e}")

    logger.info(f"Distribution plots saved to: {assets_dir}")


def _generate_expression_documentation(tracker, output_path: Path):
    """
    Generate expression lineage documentation.

    Args:
        tracker: Global LineageTracker instance
        output_path: Base output directory
    """
    expression_lineages = getattr(tracker, '_expression_lineages', [])

    if not expression_lineages:
        return

    logger.info(f"Generating expression documentation for {len(expression_lineages)} functions")

    # Create documentation directory
    docs_dir = output_path / "expression_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Generate markdown documentation for each function
    for lineage_data in expression_lineages:
        function_name = lineage_data.get('function_name', 'unknown')
        expressions = lineage_data.get('expressions', {})
        metadata = lineage_data.get('metadata', {})

        if not expressions:
            continue

        # Create documentation file
        doc_path = docs_dir / f"{function_name}_expressions.md"

        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f"# Expression Lineage: {function_name}\n\n")
            f.write(f"**Captured:** {datetime.fromtimestamp(lineage_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Column Expressions\n\n")

            for col_name, expr in expressions.items():
                f.write(f"### `{col_name}`\n\n")
                f.write(f"```\n{expr.expression}\n```\n\n")

                if hasattr(expr, 'operation_type') and expr.operation_type:
                    f.write(f"**Operation Type:** {expr.operation_type}\n\n")

                if hasattr(expr, 'dependencies') and expr.dependencies:
                    f.write(f"**Dependencies:** {', '.join(expr.dependencies)}\n\n")

        logger.info(f"  [OK] Generated expression docs: {doc_path}")

    logger.info(f"Expression documentation saved to: {docs_dir}")


def quickReport(output_dir: str = "outputs", **kwargs) -> Dict[str, str]:
    """
    Quick report generation with minimal configuration.

    Equivalent to reportAll() with auto_detect=True and generate_individual_files=True.

    Args:
        output_dir: Directory to write reports
        **kwargs: Additional arguments passed to reportAll()

    Returns:
        Dictionary mapping report types to their output file paths

    Example:
        >>> quickReport("outputs/my_pipeline")
    """
    return reportAll(
        output_dir=output_dir,
        auto_detect=True,
        generate_individual_files=True,
        **kwargs
    )
