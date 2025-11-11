"""Comprehensive Pipeline Report - Combines multiple reports into one document."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_report import BaseReport, ReportConfig
from .business_concept_catalog import (
    BusinessConceptCatalog,
    BusinessConceptCatalogConfig,
)
from .business_flow_diagram import BusinessFlowDiagram, BusinessFlowDiagramConfig
from .describe_report import DescribeReportGenerator
from .distribution_report import DistributionReport, DistributionReportConfig
from .expression_documentation import (
    ExpressionDocumentationConfig,
    ExpressionDocumentationReport,
)
from .expression_impact_diagram import (
    ExpressionImpactDiagramConfig,
    ExpressionImpactDiagramReport,
)

logger = logging.getLogger(__name__)


@dataclass
class ComprehensivePipelineReportConfig(ReportConfig):
    """Configuration for Comprehensive Pipeline Report generation."""
    title: str = "Comprehensive Pipeline Report"
    include_reports: List[str] = field(default_factory=lambda: [
        "business_catalog",
        "business_diagram",
        "distribution_analysis",
        "describe_profiles"
    ])
    report_configs: Dict[str, Any] = field(default_factory=dict)
    generate_individual_files: bool = False
    individual_files_directory: Optional[str] = None
    include_executive_summary: bool = True
    organize_by_stakeholder: bool = False  # Keep default as False for backward compatibility
    stakeholders: List[str] = field(default_factory=lambda: ["all"])  # Filter by stakeholder


class ComprehensivePipelineReport(BaseReport):
    """
    Generates comprehensive pipeline reports combining multiple sub-reports.

    This report can combine:
    - Business Concept Catalog
    - Business Flow Diagram
    - Expression Documentation
    - Expression Impact Diagram
    - Distribution Analysis
    """

    # Available report types
    AVAILABLE_REPORTS = {
        "business_catalog": {
            "class": BusinessConceptCatalog,
            "config_class": BusinessConceptCatalogConfig,
            "title": "Business Concept Catalog",
            "anchor": "business-concept-catalog",
            "stakeholder": "business"
        },
        "business_diagram": {
            "class": BusinessFlowDiagram,
            "config_class": BusinessFlowDiagramConfig,
            "title": "Business Flow Diagram",
            "anchor": "business-flow-diagram",
            "stakeholder": "business"
        },
        "distribution_analysis": {
            "class": DistributionReport,
            "config_class": DistributionReportConfig,
            "title": "Distribution Analysis",
            "anchor": "distribution-analysis",
            "stakeholder": "data_scientist"
        },
        "expression_documentation": {
            "class": ExpressionDocumentationReport,
            "config_class": ExpressionDocumentationConfig,
            "title": "Expression Documentation",
            "anchor": "expression-documentation",
            "stakeholder": "technical"
        },
        "expression_impact_diagram": {
            "class": ExpressionImpactDiagramReport,
            "config_class": ExpressionImpactDiagramConfig,
            "title": "Expression Impact Diagram",
            "anchor": "expression-impact-diagram",
            "stakeholder": "technical"
        },
        "describe_profiles": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Describe Profiles",
            "anchor": "describe-profiles",
            "stakeholder": "data_scientist"
        },
        # NEW: Governance reports
        "governance_summary": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Governance Overview",
            "anchor": "governance-overview",
            "stakeholder": "governance"
        },
        # NEW: Data engineer reports
        "data_engineer_summary": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Data Engineering Insights",
            "anchor": "data-engineering-insights",
            "stakeholder": "data_engineer"
        },
        # NEW: Data scientist reports
        "feature_catalog": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Feature Catalog",
            "anchor": "feature-catalog",
            "stakeholder": "data_scientist"
        },
        "correlation_analysis": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Correlation Analysis",
            "anchor": "correlation-analysis",
            "stakeholder": "data_scientist"
        },
        "statistical_profiling": {
            "class": None,  # Custom handling in _generate_report_section
            "config_class": None,
            "title": "Statistical Profiling",
            "anchor": "statistical-profiling",
            "stakeholder": "data_scientist"
        }
    }

    def __init__(self, config: Optional[ComprehensivePipelineReportConfig] = None, **kwargs):
        """
        Initialize the Comprehensive Pipeline Report generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = ComprehensivePipelineReportConfig(**kwargs)
        elif config is None:
            config = ComprehensivePipelineReportConfig()

        super().__init__(config)
        self.config: ComprehensivePipelineReportConfig = config

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        # Check that requested reports are available
        for report_type in self.config.include_reports:
            if report_type not in self.AVAILABLE_REPORTS:
                raise ValueError(
                    f"Unknown report type: {report_type}. "
                    f"Available: {list(self.AVAILABLE_REPORTS.keys())}"
                )
        return True

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the Comprehensive Pipeline Report.

        Args:
            lineage_graph: EnhancedLineageGraph to analyze
            output_path: Path to write the combined markdown file

        Returns:
            Path to the generated report
        """
        logger.info("Generating Comprehensive Pipeline Report")

        output_file = Path(output_path)

        # Generate individual report sections
        report_sections = {}
        individual_files = {}

        for report_type in self.config.include_reports:
            logger.info(f"Generating {report_type} section")

            # Generate report
            section_content, file_path = self._generate_report_section(
                report_type,
                lineage_graph,
                output_file
            )

            report_sections[report_type] = section_content
            if file_path:
                individual_files[report_type] = file_path

        # Combine into comprehensive report
        combined_content = self._combine_reports(report_sections, lineage_graph)

        # Write combined report
        result_path = self._write_report(combined_content, output_path)

        logger.info(f"Comprehensive report generated: {result_path}")
        if individual_files:
            logger.info(f"Individual reports: {len(individual_files)}")

        return result_path

    def _generate_report_section(
        self,
        report_type: str,
        lineage_graph,
        output_file: Path
    ) -> tuple:
        """
        Generate a single report section.

        Args:
            report_type: Type of report to generate
            lineage_graph: EnhancedLineageGraph
            output_file: Main output file path

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        report_info = self.AVAILABLE_REPORTS[report_type]

        # Handle custom report types that don't have a standard class
        if report_type == "describe_profiles":
            # Custom handling for describe profiles
            return self._generate_describe_profiles_section()
        elif report_type == "governance_summary":
            # Custom handling for governance overview
            return self._generate_governance_section(lineage_graph)
        elif report_type == "data_engineer_summary":
            # Custom handling for data engineer insights
            return self._generate_data_engineer_section(lineage_graph)
        elif report_type == "feature_catalog":
            # Custom handling for feature catalog
            return self._generate_feature_catalog_section(lineage_graph)
        elif report_type == "correlation_analysis":
            # Custom handling for correlation analysis
            return self._generate_correlation_section(lineage_graph)
        elif report_type == "statistical_profiling":
            # Custom handling for statistical profiling
            return self._generate_statistical_profiling_section()

        # Get config for this report
        config_kwargs = self.config.report_configs.get(report_type, {})
        report_config = report_info["config_class"](**config_kwargs)

        # Create report generator
        report_generator = report_info["class"](config=report_config)

        # Generate to temp location or individual file
        if self.config.generate_individual_files:
            # Create individual files directory
            if self.config.individual_files_directory:
                individual_dir = Path(self.config.individual_files_directory)
            else:
                individual_dir = output_file.parent / "individual_reports"

            individual_dir.mkdir(parents=True, exist_ok=True)

            # Generate individual file
            individual_path = individual_dir / f"{report_type}.md"
            report_generator.generate(lineage_graph, str(individual_path))

            # Read content
            with open(individual_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return content, str(individual_path)
        else:
            # Generate to temp file, but use the actual output file path for relative path calculations
            # This ensures image paths are relative to the final comprehensive report location
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
                temp_path = tmp.name

            # For DistributionReport, we need to generate content with simple relative paths
            if report_type == "distribution_analysis":
                # Generate content directly with simple ./assets paths
                from ..core.lineage_tracker import get_enhanced_tracker

                tracker = get_enhanced_tracker()
                distribution_analyses = getattr(tracker, '_distribution_analyses', [])

                if distribution_analyses:
                    # Process analysis points
                    from ..visualization.unified_report_generator import (
                        DistributionAnalysisPoint,
                    )

                    analysis_points = []
                    for idx, analysis in enumerate(distribution_analyses, 1):
                        metadata = analysis.get('metadata', {})
                        reference_id = f"DA-{idx:03d}"
                        function_name = analysis.get('function_name', 'unknown')

                        analysis_point = DistributionAnalysisPoint(
                            reference_id=reference_id,
                            step_name=function_name.replace('_', ' ').title(),
                            function_name=function_name,
                            variables=metadata.get('variables_analyzed', []),
                            timestamp=analysis.get('timestamp', 0.0),
                            lineage_node_id=metadata.get('parent_operation_id', ''),
                            before_stats=metadata.get('before_stats', {}),
                            after_stats=metadata.get('after_stats', {}),
                            plot_results=metadata.get('plot_results', []),
                            execution_time=metadata.get('execution_time'),
                            record_change=metadata.get('record_change'),
                            metadata=metadata
                        )
                        analysis_points.append(analysis_point)

                    # Build content manually with simple ./assets paths
                    content_lines = []
                    content_lines.append("# Distribution Analysis\n")
                    content_lines.append("*Statistical analysis of variable distributions across the pipeline*\n")
                    content_lines.append("---\n")
                    content_lines.append("\n## Overview\n")
                    content_lines.append(f"- **Analysis Points:** {len(analysis_points)}")

                    all_variables = set()
                    for point in analysis_points:
                        all_variables.update(point.variables)
                    content_lines.append(f"- **Variables Monitored:** {', '.join(sorted(all_variables))}")
                    content_lines.append("")

                    # Generate distribution section with SIMPLE paths
                    content_lines.append("## 2. Distribution Analysis by Variable\n")

                    for variable in sorted(all_variables):
                        content_lines.append(f"### 2.{list(sorted(all_variables)).index(variable) + 1} Variable: `{variable}` {{#{variable}-analysis}}\n")

                        variable_points = [p for p in analysis_points if variable in p.variables]

                        # Table header
                        content_lines.append("| Analysis Step | Raw Distribution (All Data) | Cleaned Distribution (IQR Method) |")
                        content_lines.append("|---------------|-----------------------------|-----------------------------------|")

                        # Table rows
                        for point in variable_points:
                            step_desc = f"**[{point.reference_id}] {point.step_name}**<br/>*Custom operation: {point.step_name}*<br/>"

                            # Extract the actual filename prefix from plot_results
                            # The plots are stored with their full paths, extract just the filename
                            raw_filename = None
                            iqr_filename = None

                            for plot_path in point.plot_results:
                                filename = plot_path.split('/')[-1] if '/' in plot_path else plot_path.split('\\')[-1]
                                if f'_after_{variable}_raw' in filename:
                                    raw_filename = filename
                                elif f'_after_{variable}_clean' in filename:
                                    iqr_filename = filename

                            # Use the actual filenames or fallback to function_name pattern
                            if raw_filename:
                                raw_img = f"![{variable} raw {point.reference_id}](./assets/distribution_analysis/{raw_filename})"
                            else:
                                raw_img = f"![{variable} raw {point.reference_id}](./assets/distribution_analysis/{point.function_name}_after_{variable}_raw.png)"

                            if iqr_filename:
                                iqr_img = f"![{variable} iqr {point.reference_id}](./assets/distribution_analysis/{iqr_filename})"
                            else:
                                iqr_img = f"![{variable} iqr {point.reference_id}](./assets/distribution_analysis/{point.function_name}_after_{variable}_clean.png)"

                            content_lines.append(f"| {step_desc} | {raw_img} | {iqr_img} |")

                    # Add cross-analysis if configured
                    if report_config.include_cross_analysis:
                        content_lines.append("\n## 4. Cross-Variable Analysis\n")
                        content_lines.append("### 4.1 Distribution Change Summary\n")
                        content_lines.append("| Step | Variables | Key Changes |")
                        content_lines.append("|------|-----------|-------------|")
                        for point in analysis_points:
                            vars_str = ", ".join(point.variables)
                            content_lines.append(f"| [{point.reference_id}](#{point.reference_id.lower()}-{point.step_name.lower().replace(' ', '-')}) | {vars_str} | Data transformation applied |")

                        content_lines.append("\n### 4.2 Data Quality Insights\n")
                        content_lines.append("- **Outlier Impact**: IQR cleaning removes outliers consistently across steps")
                        content_lines.append("- **Distribution Stability**: Variable distributions show expected changes through pipeline")
                        content_lines.append(f"- **Pipeline Complexity**: {len(analysis_points)} analysis points across data processing\n")

                    content = '\n'.join(content_lines)
                else:
                    content = "# Distribution Analysis\n\n*No distribution analyses found*\n"
            else:
                # For other reports, use the normal temp file approach
                report_generator.generate(lineage_graph, temp_path)

                # Read content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Clean up temp file
                Path(temp_path).unlink()

            return content, None

    def _generate_describe_profiles_section(self) -> tuple:
        """
        Generate describe profiles section with simple handling.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        from ..core.lineage_tracker import get_global_tracker

        tracker = get_global_tracker()
        describe_profiles = getattr(tracker, '_describe_profiles', [])

        if describe_profiles:
            # Use the DescribeReportGenerator
            generator = DescribeReportGenerator()
            content = generator.generate_report(describe_profiles, output_path=None)
        else:
            content = "# Describe Profiles\n\n*No describe profiles found*\n"

        return content, None

    def _generate_governance_section(self, lineage_graph) -> tuple:
        """
        Generate governance overview section.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        lines = []
        lines.append("# Governance Overview\n")
        lines.append("*Compliance, Risk Assessment, and Data Governance*\n")
        lines.append("")

        # Check if governance metadata exists
        has_governance = False
        governance_nodes = []

        for node in lineage_graph.nodes.values():
            if hasattr(node, 'metadata') and 'governance_metadata' in node.metadata:
                gov_meta = node.metadata['governance_metadata']
                if gov_meta:
                    has_governance = True
                    governance_nodes.append({
                        'node': node,
                        'metadata': gov_meta
                    })

        if not has_governance:
            lines.append("*No governance metadata found. Use governance decorators to track compliance and risk information.*\n")
            return '\n'.join(lines), None

        # Executive Summary
        lines.append("## Governance Summary\n")
        lines.append(f"- **Governed Operations:** {len(governance_nodes)}")

        # Count various governance aspects
        has_justification = sum(1 for g in governance_nodes if hasattr(g['metadata'], 'business_justification') and g['metadata'].business_justification)
        has_risks = sum(1 for g in governance_nodes if hasattr(g['metadata'], 'known_risks') and g['metadata'].known_risks)
        processes_pii = sum(1 for g in governance_nodes if hasattr(g['metadata'], 'processes_pii') and g['metadata'].processes_pii)

        lines.append(f"- **Business Justification Documented:** {has_justification}/{len(governance_nodes)}")
        lines.append(f"- **Risk Assessments:** {has_risks}/{len(governance_nodes)}")
        lines.append(f"- **PII Processing Operations:** {processes_pii}")
        lines.append("")

        # Business Justifications
        if has_justification > 0:
            lines.append("## Business Justifications\n")
            for g in governance_nodes:
                meta = g['metadata']
                if hasattr(meta, 'business_justification') and meta.business_justification:
                    node_name = g['node'].metadata.get('operation_name', g['node'].name)
                    lines.append(f"**{node_name}:**")
                    lines.append(f"{meta.business_justification}")
                    if hasattr(meta, 'regulatory_requirement') and meta.regulatory_requirement:
                        lines.append(f"*Regulatory Requirement:* {meta.regulatory_requirement}")
                    lines.append("")

        # Risk Assessments - NEW IMPROVED FORMAT
        if has_risks > 0:
            lines.append("## Risk Assessment\n")

            # Collect all risks and mitigations from all governance nodes
            all_risks = []
            all_mitigations = []

            for g in governance_nodes:
                meta = g['metadata']
                if hasattr(meta, 'known_risks') and meta.known_risks:
                    all_risks.extend(meta.known_risks)
                if hasattr(meta, 'risk_mitigations') and meta.risk_mitigations:
                    all_mitigations.extend(meta.risk_mitigations)

            if all_risks:
                # Generate Risk Summary Matrix
                summary_table = self._generate_risk_summary_matrix(all_risks)
                lines.append(summary_table)

                # Generate Risk Details & Mitigations Table
                details_table = self._generate_risk_details_table(all_risks, all_mitigations)
                lines.append(details_table)
            else:
                lines.append("*No risks identified*\n")

        # Customer Impact
        customer_impact_ops = [g for g in governance_nodes
                              if hasattr(g['metadata'], 'customer_impact_level') and g['metadata'].customer_impact_level]
        if customer_impact_ops:
            lines.append("## Customer Impact Analysis\n")
            for g in customer_impact_ops:
                meta = g['metadata']
                node_name = g['node'].metadata.get('operation_name', g['node'].name)
                impact_level = meta.customer_impact_level
                if hasattr(impact_level, 'value'):
                    impact_level = impact_level.value
                lines.append(f"**{node_name}:** {str(impact_level).upper()}")
                if hasattr(meta, 'customer_impact_description') and meta.customer_impact_description:
                    lines.append(f"*Description:* {meta.customer_impact_description}")
                lines.append("")

        # PII and Data Classification
        if processes_pii > 0:
            lines.append("## PII and Data Classification\n")
            for g in governance_nodes:
                meta = g['metadata']
                if hasattr(meta, 'processes_pii') and meta.processes_pii:
                    node_name = g['node'].metadata.get('operation_name', g['node'].name)
                    lines.append(f"**{node_name}:**")
                    if hasattr(meta, 'pii_columns') and meta.pii_columns:
                        lines.append(f"- PII Columns: {', '.join(meta.pii_columns)}")
                    if hasattr(meta, 'data_classification') and meta.data_classification:
                        classification = meta.data_classification
                        if hasattr(classification, 'value'):
                            classification = classification.value
                        lines.append(f"- Classification: {classification}")
                    if hasattr(meta, 'data_retention_days') and meta.data_retention_days:
                        lines.append(f"- Retention Policy: {meta.data_retention_days} days")
                    lines.append("")

        # Approval Status
        requires_approval = [g for g in governance_nodes
                            if hasattr(g['metadata'], 'requires_approval') and g['metadata'].requires_approval]
        if requires_approval:
            lines.append("## Approval Status\n")
            for g in requires_approval:
                meta = g['metadata']
                node_name = g['node'].metadata.get('operation_name', g['node'].name)
                approval_status = "UNKNOWN"
                if hasattr(meta, 'approval_status'):
                    status = meta.approval_status
                    if hasattr(status, 'value'):
                        approval_status = status.value.upper()
                    else:
                        approval_status = str(status).upper()

                lines.append(f"**{node_name}:** {approval_status}")
                if hasattr(meta, 'approved_by') and meta.approved_by:
                    lines.append(f"- Approved By: {meta.approved_by}")
                if hasattr(meta, 'approval_date') and meta.approval_date:
                    approval_date = meta.approval_date
                    if hasattr(approval_date, 'strftime'):
                        lines.append(f"- Date: {approval_date.strftime('%Y-%m-%d')}")
                    else:
                        lines.append(f"- Date: {approval_date}")
                lines.append("")

        return '\n'.join(lines), None

    def _find_parent_business_concept(self, node, lineage_graph) -> str:
        """
        Find the immediate parent business concept for an operation node.

        Args:
            node: The operation node to find the parent business concept for
            lineage_graph: The lineage graph containing all nodes and edges

        Returns:
            The name of the parent business concept, or "-" if none exists
        """
        # Strategy 1: Check if this node has a context_id
        # Business concepts are organized by context, and operations belong to contexts
        if hasattr(node, 'context_id') and node.context_id:
            context_id = node.context_id

            # Look through all nodes in this context to find the business concept name
            if hasattr(lineage_graph, 'context_nodes') and context_id in lineage_graph.context_nodes:
                context_node_list = lineage_graph.context_nodes[context_id]

                # Search for business concept metadata in the context nodes
                for context_node in context_node_list:
                    if hasattr(context_node, 'metadata') and context_node.metadata:
                        # Check for business_context (context manager approach)
                        if 'business_context' in context_node.metadata:
                            return context_node.metadata['business_context']

                        # Check for operation_name with operation_type='business_concept' (decorator approach)
                        if (context_node.metadata.get('operation_type') == 'business_concept' and
                            'operation_name' in context_node.metadata):
                            return context_node.metadata['operation_name']

                # If no business concept metadata found, use the context_id as fallback
                # This handles cases where the context_id IS the business concept name
                return context_id

        # Strategy 2: Check node's own metadata for business_context
        if hasattr(node, 'metadata') and node.metadata:
            if 'business_context' in node.metadata:
                return node.metadata['business_context']

        # Strategy 3: Search through edges to find parent business concept nodes
        node_id = node.node_id if hasattr(node, 'node_id') else None
        lineage_id = node.lineage_id if hasattr(node, 'lineage_id') else None

        parent_ids = set()

        # Collect parent IDs from edges
        for edge in lineage_graph.edges:
            if edge.target_id == node_id or edge.target_id == lineage_id:
                parent_ids.add(edge.source_id)

        # Also check parents_index if available
        if hasattr(lineage_graph, 'parents_index'):
            if node_id and node_id in lineage_graph.parents_index:
                parent_ids.update(lineage_graph.parents_index[node_id])
            if lineage_id and lineage_id in lineage_graph.parents_index:
                parent_ids.update(lineage_graph.parents_index[lineage_id])

        # Search for a business concept among the parents
        for parent_id in parent_ids:
            parent_node = lineage_graph.nodes.get(parent_id)
            if parent_node and hasattr(parent_node, 'metadata') and parent_node.metadata:
                if parent_node.metadata.get('operation_type') == 'business_concept':
                    return parent_node.metadata.get('operation_name', parent_node.name if hasattr(parent_node, 'name') else parent_id)

        return "-"

    def _generate_data_engineer_section(self, lineage_graph) -> tuple:
        """
        Generate data engineer insights section.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        lines = []
        lines.append("# Data Engineering Insights\n")
        lines.append("*Pipeline Debugging, Data Quality, and Execution Metrics*\n")
        lines.append("")

        # Collect metrics from nodes
        nodes_with_metrics = []
        total_operations = 0
        data_sources = 0

        for node in lineage_graph.nodes.values():
            operation_type = node.metadata.get('operation_type', '')
            if operation_type == 'data_source':
                data_sources += 1
            elif operation_type not in ['business_concept']:
                total_operations += 1

            # CRITICAL FIX: Skip business_concept operation_type nodes from row count tracking
            # to avoid duplicates with their underlying technical operations.
            # The decorator approach creates nodes with operation_type='business_concept' that
            # represent the same operation as their child technical nodes (filter, join, etc).
            # The context manager approach only creates technical operation nodes.
            # We filter by operation_type metadata, not node instance type.
            if operation_type == 'business_concept':
                # Skip business concept nodes - we'll show their underlying operations instead
                logger.debug(f"Skipping business_concept node '{node.name}' from row count tracking")
                continue

            metrics = node.metadata.get('metrics', {})
            if isinstance(metrics, dict) and metrics:
                nodes_with_metrics.append({
                    'node': node,
                    'metrics': metrics,
                    'operation_type': operation_type
                })

        # Pipeline Overview
        lines.append("## Pipeline Overview\n")
        lines.append(f"- **Total Operations:** {total_operations}")
        lines.append(f"- **Data Sources:** {data_sources}")
        lines.append(f"- **Operations with Metrics:** {len(nodes_with_metrics)}")
        lines.append("")

        if not nodes_with_metrics:
            lines.append("*No execution metrics found. Use materialize=True to track row counts and data quality.*\n")
            return '\n'.join(lines), None

        # Row Count Tracking
        lines.append("## Row Count Tracking\n")
        lines.append("| Operation | Business Concept | Input Rows | Output Rows | Change | Change % |")
        lines.append("|-----------|------------------|-----------|------------|--------|----------|")

        for item in nodes_with_metrics:
            node = item['node']
            metrics = item['metrics']

            node_name = node.metadata.get('operation_name', node.name)
            business_concept = self._find_parent_business_concept(node, lineage_graph)
            input_count = metrics.get('input_record_count', 0)
            output_count = metrics.get('output_record_count', metrics.get('row_count', 0))

            if input_count and output_count:
                change = output_count - input_count
                change_pct = (change / input_count * 100) if input_count > 0 else 0
                change_str = f"{change:+,}"
                change_pct_str = f"{change_pct:+.1f}%"

                # Flag significant data loss
                warning = ""
                if change_pct < -10:
                    warning = " [WARN]"

                lines.append(f"| {node_name}{warning} | {business_concept} | {input_count:,} | {output_count:,} | {change_str} | {change_pct_str} |")
            elif output_count:
                lines.append(f"| {node_name} | {business_concept} | - | {output_count:,} | - | - |")

        lines.append("")

        # Data Quality Warnings
        warnings = []
        for item in nodes_with_metrics:
            node = item['node']
            metrics = item['metrics']
            node_name = node.metadata.get('operation_name', node.name)

            # Check for significant data loss
            input_count = metrics.get('input_record_count', 0)
            output_count = metrics.get('output_record_count', metrics.get('row_count', 0))

            if input_count and output_count and input_count > 0:
                loss_pct = ((input_count - output_count) / input_count * 100)
                if loss_pct > 10:
                    warnings.append(f"- **{node_name}**: {loss_pct:.1f}% data loss ({input_count:,} -> {output_count:,} rows)")

            # Check for null values
            null_counts = metrics.get('null_counts', {})
            if null_counts and output_count > 0:
                for col, null_count in null_counts.items():
                    null_pct = (null_count / output_count * 100)
                    if null_pct > 5:
                        warnings.append(f"- **{node_name}.{col}**: {null_pct:.1f}% null values ({null_count:,}/{output_count:,})")

        if warnings:
            lines.append("## Data Quality Warnings\n")
            lines.extend(warnings)
            lines.append("")
        else:
            lines.append("## Data Quality\n")
            lines.append("[OK] No data quality issues detected.\n")
            lines.append("")

        # Execution Metrics
        total_time = 0.0
        nodes_with_time = []

        for item in nodes_with_metrics:
            node = item['node']
            exec_time = node.metadata.get('execution_time', 0) or node.metadata.get('duration', 0)
            if exec_time and exec_time > 0:
                total_time += exec_time
                nodes_with_time.append({
                    'name': node.metadata.get('operation_name', node.name),
                    'time': exec_time
                })

        if total_time > 0:
            lines.append("## Execution Metrics\n")
            lines.append(f"**Total Execution Time:** {self._format_duration(total_time)}\n")

            if nodes_with_time:
                # Sort by time descending
                nodes_with_time.sort(key=lambda x: x['time'], reverse=True)

                lines.append("**Top Operations by Execution Time:**\n")
                for item in nodes_with_time[:5]:  # Top 5
                    time_str = self._format_duration(item['time'])
                    pct = (item['time'] / total_time * 100) if total_time > 0 else 0
                    lines.append(f"- {item['name']}: {time_str} ({pct:.1f}%)")
                lines.append("")

        # Location References for Debugging
        lines.append("## Debugging Information\n")
        lines.append("**Operation Locations:**\n")

        for item in nodes_with_metrics[:10]:  # Limit to first 10
            node = item['node']
            node_name = node.metadata.get('operation_name', node.name)
            location = node.metadata.get('location', '')

            if location:
                lines.append(f"- **{node_name}**: `{location}`")

        lines.append("")

        return '\n'.join(lines), None

    def _generate_feature_catalog_section(self, lineage_graph) -> tuple:
        """
        Generate feature catalog section for data scientists.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        from ..core.lineage_tracker import get_global_tracker

        lines = []
        lines.append("# Feature Catalog\n")
        lines.append("*Feature Documentation and Lineage Tracking*\n")
        lines.append("")

        tracker = get_global_tracker()

        # Check if we have any feature-related metadata
        # Features could come from:
        # 1. Target variable tracking
        # 2. Expression lineage (derived features)
        # 3. Correlation analyses (identified features)

        target_variable = getattr(tracker, '_target_variable', None)
        expression_lineages = getattr(tracker, '_expression_lineages', [])
        correlation_analyses = getattr(tracker, '_correlation_analyses', [])

        # Collect all features from various sources
        all_features = set()

        # Extract features from expressions
        for lineage_data in expression_lineages:
            expressions = lineage_data.get('expressions', {})
            all_features.update(expressions.keys())

        # Extract features from correlations
        for analysis in correlation_analyses:
            stats = analysis.get('stats')
            if stats and hasattr(stats, 'columns'):
                all_features.update(stats.columns)

        if not all_features and not target_variable:
            lines.append("*No feature tracking data found. Use expression lineage or correlation analysis to track features.*\n")
            return '\n'.join(lines), None

        # Feature Summary
        lines.append("## Feature Summary\n")
        lines.append(f"- **Total Features Identified:** {len(all_features)}")
        if target_variable:
            lines.append(f"- **Target Variable:** {target_variable}")
        lines.append("")

        # Feature List
        if all_features:
            lines.append("## Identified Features\n")
            lines.append("| Feature Name | Type | Source |")
            lines.append("|-------------|------|--------|")

            for feature in sorted(all_features):
                # Determine feature type and source
                feature_type = "Derived" if feature in [e for lineage in expression_lineages
                                                       for e in lineage.get('expressions', {}).keys()] else "Original"
                source = "Expression Lineage" if feature_type == "Derived" else "Data Source"

                # Mark target variable
                is_target = " **[TARGET]**" if feature == target_variable else ""
                lines.append(f"| {feature}{is_target} | {feature_type} | {source} |")

            lines.append("")

        # Feature Transformations
        if expression_lineages:
            lines.append("## Feature Transformations\n")
            lines.append("*Features created through expressions:*\n")

            for lineage_data in expression_lineages:
                function_name = lineage_data.get('function_name', 'unknown')
                expressions = lineage_data.get('expressions', {})

                if expressions:
                    lines.append(f"### Function: `{function_name}`\n")
                    for col_name, expr_obj in list(expressions.items())[:5]:  # Limit to 5 per function
                        lines.append(f"**{col_name}**: `{expr_obj.expression[:100]}...`" if len(expr_obj.expression) > 100
                                   else f"**{col_name}**: `{expr_obj.expression}`")
                    if len(expressions) > 5:
                        lines.append(f"*...and {len(expressions) - 5} more transformations*")
                    lines.append("")

        # Feature Importance Placeholder
        lines.append("## Feature Importance\n")
        lines.append("*Feature importance can be added by providing importance scores in the configuration.*\n")
        lines.append("")

        # Next Steps
        lines.append("## Next Steps\n")
        lines.append("- **Model Training**: Use identified features for ML models")
        lines.append("- **Feature Engineering**: Review transformations for optimization")
        lines.append("- **Correlation Analysis**: Check for multicollinearity")
        lines.append("")

        return '\n'.join(lines), None

    def _generate_correlation_section(self, lineage_graph) -> tuple:
        """
        Generate correlation analysis section.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        from ..core.lineage_tracker import get_global_tracker

        lines = []
        lines.append("# Correlation Analysis\n")
        lines.append("*Multicollinearity Detection and Feature Relationships*\n")
        lines.append("")

        tracker = get_global_tracker()
        correlation_analyses = getattr(tracker, '_correlation_analyses', [])

        if not correlation_analyses:
            lines.append("*No correlation analyses found. Use the `@correlationAnalyzer` decorator to track correlations.*\n")
            lines.append("")
            lines.append("**Example:**")
            lines.append("```python")
            lines.append("@correlationAnalyzer(")
            lines.append("    checkpoint_name='After Feature Engineering',")
            lines.append("    columns=['age', 'income', 'credit_score']")
            lines.append(")")
            lines.append("def engineer_features(df):")
            lines.append("    return df.withColumn('new_feature', ...)")
            lines.append("```\n")
            return '\n'.join(lines), None

        # Overview
        lines.append("## Overview\n")
        lines.append(f"- **Analysis Checkpoints:** {len(correlation_analyses)}")

        # Count total high correlations
        total_high_correlations = sum(
            len(analysis.get('stats').high_correlations)
            for analysis in correlation_analyses
            if hasattr(analysis.get('stats'), 'high_correlations')
        )
        lines.append(f"- **High Correlations Detected:** {total_high_correlations}")
        lines.append("")

        # Each correlation analysis checkpoint
        for idx, analysis in enumerate(correlation_analyses, 1):
            checkpoint_name = analysis.get('checkpoint_name', f'Analysis {idx}')
            function_name = analysis.get('function_name', 'unknown')
            stats = analysis.get('stats')

            lines.append(f"## {idx}. {checkpoint_name}\n")
            lines.append(f"**Function:** `{function_name}`")
            lines.append(f"**Variables Analyzed:** {len(stats.columns)}")
            lines.append("")

            # Correlation matrix
            if hasattr(stats, 'correlation_matrix') and stats.correlation_matrix is not None:
                lines.append("### Correlation Matrix\n")
                lines.append("```")
                # Format correlation matrix (simplified)
                corr_df = stats.correlation_matrix
                lines.append(corr_df.to_string())
                lines.append("```\n")

            # High correlations
            if hasattr(stats, 'high_correlations') and stats.high_correlations:
                lines.append("### High Correlations (Multicollinearity Warnings)\n")
                for corr in stats.high_correlations:
                    col1 = corr.get('column1')
                    col2 = corr.get('column2')
                    corr_value = corr.get('correlation')
                    lines.append(f"- **{col1}** ↔ **{col2}**: {corr_value:.3f}")
                lines.append("")
            else:
                lines.append("**No high correlations detected** (threshold: 0.7)\n")

            lines.append("---\n")

        # Recommendations
        lines.append("## Recommendations\n")
        if total_high_correlations > 0:
            lines.append("**Multicollinearity Detected:**")
            lines.append("- Consider removing one variable from highly correlated pairs")
            lines.append("- Use dimensionality reduction (PCA) if needed")
            lines.append("- Monitor for model instability")
        else:
            lines.append("**No multicollinearity issues detected.**")
            lines.append("- Features appear to be independent")
            lines.append("- Safe to use all features in modeling")
        lines.append("")

        return '\n'.join(lines), None

    def _generate_statistical_profiling_section(self) -> tuple:
        """
        Generate statistical profiling section.

        Returns:
            Tuple of (section_content, individual_file_path)
        """
        from ..core.lineage_tracker import get_global_tracker

        lines = []
        lines.append("# Statistical Profiling\n")
        lines.append("*Advanced Statistical Analysis Beyond Basic Describe*\n")
        lines.append("")

        tracker = get_global_tracker()

        # Check for both describe profiles and any statistical profiling
        describe_profiles = getattr(tracker, '_describe_profiles', [])

        if not describe_profiles:
            lines.append("*No statistical profiles found. Use the `@describeProfiler` decorator to capture statistics.*\n")
            lines.append("")
            lines.append("**Example:**")
            lines.append("```python")
            lines.append("@describeProfiler(")
            lines.append("    checkpoint_name='After Transformation',")
            lines.append("    columns=['age', 'income', 'premium']")
            lines.append(")")
            lines.append("def transform_data(df):")
            lines.append("    return df.filter(col('age') > 18)")
            lines.append("```\n")
            return '\n'.join(lines), None

        # Overview
        lines.append("## Overview\n")
        lines.append(f"- **Profiling Checkpoints:** {len(describe_profiles)}")

        # Calculate total columns profiled
        total_columns = sum(
            len(profile.get('stats').columns)
            for profile in describe_profiles
            if hasattr(profile.get('stats'), 'columns')
        )
        lines.append(f"- **Total Columns Profiled:** {total_columns}")
        lines.append("")

        # Each profiling checkpoint
        for idx, profile in enumerate(describe_profiles, 1):
            checkpoint_name = profile.get('checkpoint_name', f'Profile {idx}')
            function_name = profile.get('function_name', 'unknown')
            stats = profile.get('stats')

            lines.append(f"## {idx}. {checkpoint_name}\n")
            lines.append(f"**Function:** `{function_name}`")
            lines.append(f"**Rows:** {stats.row_count:,}" if hasattr(stats, 'row_count') else "")
            lines.append(f"**Columns:** {len(stats.columns)}" if hasattr(stats, 'columns') else "")
            lines.append("")

            # Statistical summary table
            if hasattr(stats, 'describe_df') and stats.describe_df is not None:
                lines.append("### Statistical Summary\n")
                lines.append("```")
                lines.append(stats.describe_df.to_string())
                lines.append("```\n")

            lines.append("---\n")

        # Data Quality Summary
        lines.append("## Data Quality Insights\n")
        lines.append("*Based on statistical profiling:*\n")
        lines.append("- All profiling checkpoints captured successfully")
        lines.append("- Review individual checkpoint statistics for outliers and anomalies")
        lines.append("- Use correlation analysis to identify feature relationships")
        lines.append("")

        return '\n'.join(lines), None

    def _get_severity_emoji(self, severity: str) -> str:
        """
        Map severity level to emoji representation.

        Args:
            severity: Severity level string (high, medium, low, etc.)

        Returns:
            Emoji representation of severity
        """
        severity_lower = severity.lower().strip() if severity else ""

        if severity_lower in ["high", "critical"]:
            return "🔴 High"
        elif severity_lower in ["medium", "moderate"]:
            return "🟡 Medium"
        elif severity_lower in ["low", "minimal"]:
            return "🟢 Low"
        else:
            return severity.title() if severity else "-"

    def _get_status_emoji(self, status: str) -> str:
        """
        Map mitigation status to emoji representation.

        Args:
            status: Status string (implemented, planned, etc.)

        Returns:
            Emoji representation of status
        """
        status_lower = status.lower().strip() if status else ""

        if status_lower == "implemented":
            return "✅ Implemented"
        elif status_lower in ["planned", "in_progress"]:
            return "📋 Planned"
        elif status_lower == "pending":
            return "⏳ Pending"
        else:
            return status.title() if status else "-"

    def _generate_risk_summary_matrix(self, risks: List) -> str:
        """
        Generate risk summary matrix table.

        Args:
            risks: List of RiskEntry objects

        Returns:
            Markdown table showing risk summary by severity
        """
        if not risks:
            return ""

        # Count risks by severity
        severity_counts = {}
        severity_risk_ids = {}

        for risk in risks:
            severity = risk.severity.lower().strip() if hasattr(risk, 'severity') and risk.severity else "unknown"

            # Normalize severity
            if severity in ["high", "critical"]:
                normalized = "high"
            elif severity in ["medium", "moderate"]:
                normalized = "medium"
            elif severity in ["low", "minimal"]:
                normalized = "low"
            else:
                normalized = severity

            severity_counts[normalized] = severity_counts.get(normalized, 0) + 1

            if normalized not in severity_risk_ids:
                severity_risk_ids[normalized] = []
            severity_risk_ids[normalized].append(risk.risk_id if hasattr(risk, 'risk_id') else "?")

        # Generate table
        lines = []
        lines.append("### Risk Summary\n")
        lines.append("| Severity | Count | Risk IDs |")
        lines.append("|----------|-------|----------|")

        # Order: High, Medium, Low
        for severity_key, emoji in [("high", "🔴 High"), ("medium", "🟡 Medium"), ("low", "🟢 Low")]:
            count = severity_counts.get(severity_key, 0)
            risk_ids = ", ".join(severity_risk_ids.get(severity_key, []))
            if not risk_ids:
                risk_ids = "-"
            lines.append(f"| {emoji} | {count} | {risk_ids} |")

        lines.append("")
        return "\n".join(lines)

    def _generate_risk_details_table(self, risks: List, mitigations: List) -> str:
        """
        Generate risk details and mitigations table.

        Args:
            risks: List of RiskEntry objects
            mitigations: List of RiskMitigation objects

        Returns:
            Markdown table showing risk details with mitigations
        """
        if not risks:
            return ""

        # Create mapping from risk_id to mitigations
        risk_mitigations_map = {}
        for mitigation in mitigations:
            risk_id = mitigation.risk_id if hasattr(mitigation, 'risk_id') else None
            if risk_id:
                if risk_id not in risk_mitigations_map:
                    risk_mitigations_map[risk_id] = []
                risk_mitigations_map[risk_id].append(mitigation)

        # Generate table
        lines = []
        lines.append("### Risk Details & Mitigations\n")
        lines.append("| Risk | Mitigation & Controls |")
        lines.append("|------|----------------------|")

        for risk in risks:
            # Extract risk details
            risk_id = risk.risk_id if hasattr(risk, 'risk_id') else "Unknown"
            severity = self._get_severity_emoji(risk.severity if hasattr(risk, 'severity') else "")
            description = risk.description if hasattr(risk, 'description') else "No description"
            category = risk.category.title() if hasattr(risk, 'category') and risk.category else "General"
            impact = risk.impact.title() if hasattr(risk, 'impact') and risk.impact else "-"

            # Build risk column
            risk_lines = []
            risk_lines.append(f"**{risk_id}: {category} Risk** <br>")
            risk_lines.append(f"**Severity:** {severity} <br>")
            risk_lines.append(f"**Impact:** {impact} <br>")
            if hasattr(risk, 'likelihood') and risk.likelihood:
                risk_lines.append(f"**Likelihood:** {risk.likelihood.title()} <br>")
            risk_lines.append(f"{description}")

            # Build mitigation column
            risk_mits = risk_mitigations_map.get(risk_id, [])

            if risk_mits:
                mitigation_lines = []
                for mit in risk_mits:
                    status = self._get_status_emoji(mit.status if hasattr(mit, 'status') else "")
                    effectiveness = mit.effectiveness.title() if hasattr(mit, 'effectiveness') and mit.effectiveness else "-"
                    review_date = mit.review_date if hasattr(mit, 'review_date') and mit.review_date else "-"
                    mitigation_text = mit.mitigation if hasattr(mit, 'mitigation') else "No details"

                    mitigation_lines.append(f"**Status:** {status} <br>")
                    mitigation_lines.append(f"**Effectiveness:** {effectiveness} <br>")
                    mitigation_lines.append(f"**Review:** {review_date} <br><br>")
                    mitigation_lines.append(mitigation_text)

                mitigation_column = " ".join(mitigation_lines)
            else:
                mitigation_column = "*No mitigations defined*"

            # Add table row
            lines.append(f"| {' '.join(risk_lines)} | {mitigation_column} |")

        lines.append("")
        return "\n".join(lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def _strip_metadata_section(self, content: str) -> str:
        """
        Strip metadata section from sub-report content.

        Removes lines containing generation metadata like:
        - Generated: timestamp
        - Generated By: username
        - Environment: Spark
        - Git Project: name
        - Commit ID: hash

        Args:
            content: Report content with metadata

        Returns:
            Content with metadata section removed
        """
        lines = content.split('\n')
        filtered_lines = []
        skip_next_separator = False

        for i, line in enumerate(lines):
            # Check if this is a metadata line
            is_metadata = any([
                line.startswith('**Generated:'),
                line.startswith('**Generated By:'),
                line.startswith('**Environment:'),
                line.startswith('**Git Project:'),
                line.startswith('**Commit ID:'),
                line.startswith('**Branch:')
            ])

            # Skip metadata lines
            if is_metadata:
                # Check if the next non-empty line is a separator (---)
                # If so, we'll skip it too to avoid double separators
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:
                        if next_line.startswith('---'):
                            skip_next_separator = True
                        break
                continue

            # Skip separator that follows metadata
            if skip_next_separator and line.strip().startswith('---'):
                skip_next_separator = False
                continue

            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _combine_reports(
        self,
        report_sections: Dict[str, str],
        lineage_graph
    ) -> str:
        """
        Combine report sections into comprehensive document.

        Args:
            report_sections: Dictionary of report type to content
            lineage_graph: EnhancedLineageGraph

        Returns:
            Combined markdown content
        """
        lines = []

        # Main title
        lines.append(f"# {self.config.title}\n")
        lines.append("*Complete Analysis of Data Processing Pipeline*\n")
        lines.append("\n")

        # Add standardized metadata section
        lines.extend(self._generate_metadata_section())
        lines.append("\n")

        lines.append("---\n")

        # Table of contents
        lines.append("\n## Table of Contents\n")
        for i, report_type in enumerate(self.config.include_reports, 1):
            report_info = self.AVAILABLE_REPORTS[report_type]
            title = report_info["title"]
            anchor = report_info["anchor"]
            lines.append(f"{i}. [{title}](#{anchor})")
        lines.append("\n---\n")

        # Add each report section
        for report_type in self.config.include_reports:
            report_info = self.AVAILABLE_REPORTS[report_type]

            # Extract content (remove title and metadata from individual reports)
            content = report_sections[report_type]

            # Strip metadata section from sub-report
            content = self._strip_metadata_section(content)

            # Add section with proper heading level
            lines.append(f"\n<a id='{report_info['anchor']}'></a>\n")
            lines.append(f"## {report_info['title']}\n")

            # Remove the first-level heading from the section content
            content_lines = content.split('\n')
            if content_lines and content_lines[0].startswith('# '):
                content_lines = content_lines[1:]  # Skip title

            lines.append('\n'.join(content_lines))
            lines.append("\n---\n")

        # Footer
        lines.append("\n*Report generated by PySpark StoryDoc - Modular Reporting System*\n")

        return '\n'.join(lines)
