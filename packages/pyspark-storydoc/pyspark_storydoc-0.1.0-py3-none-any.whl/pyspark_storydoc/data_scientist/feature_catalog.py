"""
Feature Catalog Generator for Data Scientists

Generates comprehensive feature documentation with:
- Feature lineage (source -> transformations -> result)
- Statistical profiles
- Business context
- Data quality information
- Target variable relationships
- Feature importance (if provided)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.lineage_tracker import get_global_tracker
from ..visualization.diagram_styles import (
    generate_mermaid_style_classes,
    get_mermaid_shape_template,
    get_node_class_name,
)
from .statistical_profiler import FeatureStats, StatisticalProfile, StatisticalProfiler

logger = logging.getLogger(__name__)


@dataclass
class FeatureCatalogConfig:
    """Configuration for feature catalog generation."""

    # What to include
    include_lineage: bool = True
    include_statistics: bool = True
    include_distributions: bool = True
    include_correlations: bool = True
    include_business_context: bool = True
    include_data_quality: bool = True

    # Feature selection
    features: Optional[List[str]] = None  # None = all features

    # Feature importance (optional)
    feature_importance: Optional[Dict[str, float]] = None

    # Target variable (optional)
    target_variable: Optional[str] = None

    # Pipeline metadata
    pipeline_name: str = "Feature Pipeline"
    experiment_id: Optional[str] = None
    dataset_name: str = "Dataset"
    row_count: Optional[int] = None

    # Formatting
    max_features_in_summary: int = 20
    max_value_counts: int = 10
    histogram_bins: int = 20


@dataclass
class FeatureInfo:
    """Complete information about a single feature."""
    name: str
    data_type: str
    source: str
    business_context: str

    # Statistics
    stats: Optional[FeatureStats] = None

    # Lineage
    lineage_path: List[str] = field(default_factory=list)
    transformation_steps: List[str] = field(default_factory=list)

    # Importance
    importance: Optional[float] = None
    importance_rank: Optional[int] = None

    # Target relationship (if target variable is specified)
    correlation_with_target: Optional[float] = None

    # Code location
    code_location: Optional[str] = None


class FeatureCatalog:
    """
    Generate comprehensive feature catalogs for data scientists.

    Combines lineage tracking, statistical profiling, and business context
    into a single comprehensive feature documentation.
    """

    def __init__(self, config: Optional[FeatureCatalogConfig] = None):
        """
        Initialize the feature catalog generator.

        Args:
            config: Configuration for catalog generation
        """
        self.config = config or FeatureCatalogConfig()

    def generate(
        self,
        lineage_graph: EnhancedLineageGraph,
        df,  # DataFrame to profile
        output_path: str,
        **kwargs
    ) -> str:
        """
        Generate a feature catalog report.

        Args:
            lineage_graph: Enhanced lineage graph with feature transformations
            df: DataFrame to profile statistically
            output_path: Path to write the report
            **kwargs: Additional config overrides

        Returns:
            Path to generated report
        """
        logger.info(f"Generating feature catalog: {self.config.pipeline_name}")

        # Update config with kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Get row count if not provided
        if self.config.row_count is None and df is not None:
            try:
                self.config.row_count = df.count()
            except:
                self.config.row_count = None

        # Profile the dataset statistically
        statistical_profile = None
        if self.config.include_statistics and df is not None:
            profiler = StatisticalProfiler()
            statistical_profile = profiler.profile_dataset(
                df=df,
                checkpoint_name="Feature Catalog",
                function_name=self.config.dataset_name,
                columns=self.config.features,
                include_correlations=self.config.include_correlations,
                histogram_bins=self.config.histogram_bins
            )

        # Extract feature information from lineage
        features = self._extract_features(lineage_graph, statistical_profile)

        # Sort features by importance if available
        if self.config.feature_importance:
            features = self._rank_features_by_importance(features)

        # Generate the report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Store output path for evolution report generation
        self.output_path = output_path

        content = self._generate_content(features, statistical_profile, lineage_graph)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Feature catalog generated: {output_file}")
        return str(output_file)

    def _extract_features(
        self,
        lineage_graph: EnhancedLineageGraph,
        statistical_profile: Optional[StatisticalProfile]
    ) -> List[FeatureInfo]:
        """Extract feature information from lineage graph and statistics."""
        features = []

        # Get features to document
        if self.config.features:
            feature_names = self.config.features
        elif statistical_profile:
            feature_names = [f.feature_name for f in statistical_profile.numeric_features + statistical_profile.categorical_features]
        else:
            # Try to extract from lineage graph - fallback to empty
            feature_names = []

        # Create FeatureInfo for each feature
        for feature_name in feature_names:
            feature_info = self._create_feature_info(
                feature_name,
                lineage_graph,
                statistical_profile
            )
            if feature_info:
                features.append(feature_info)

        return features

    def _create_feature_info(
        self,
        feature_name: str,
        lineage_graph: EnhancedLineageGraph,
        statistical_profile: Optional[StatisticalProfile]
    ) -> Optional[FeatureInfo]:
        """Create FeatureInfo for a single feature."""

        # Get statistics
        stats = None
        if statistical_profile:
            for feature_stats in statistical_profile.numeric_features + statistical_profile.categorical_features:
                if feature_stats.feature_name == feature_name:
                    stats = feature_stats
                    break

        # Get business context from lineage
        business_context = self._extract_business_context(feature_name, lineage_graph)

        # Get lineage path
        lineage_path, transformation_steps = self._extract_lineage_path(feature_name, lineage_graph)

        # Determine source
        source = lineage_path[0] if lineage_path else "Unknown"

        # Get data type
        data_type = stats.data_type if stats else "unknown"

        # Create feature info
        feature_info = FeatureInfo(
            name=feature_name,
            data_type=data_type,
            source=source,
            business_context=business_context,
            stats=stats,
            lineage_path=lineage_path,
            transformation_steps=transformation_steps,
            importance=self.config.feature_importance.get(feature_name) if self.config.feature_importance else None
        )

        return feature_info

    def _extract_business_context(
        self,
        feature_name: str,
        lineage_graph: EnhancedLineageGraph
    ) -> str:
        """Extract business context from lineage graph."""
        # Look for business concepts related to this feature
        for node_id, node in lineage_graph.nodes.items():
            if node.node_type == 'concept':
                # Check if this concept is related to the feature
                description = node.metadata.get('description', '')
                if feature_name.lower() in description.lower():
                    return description

        return f"Feature: {feature_name}"

    def _extract_lineage_path(
        self,
        feature_name: str,
        lineage_graph: EnhancedLineageGraph
    ) -> Tuple[List[str], List[str]]:
        """Extract lineage path for a feature."""
        # This is a simplified version - in practice would traverse the graph
        # to find the actual lineage path for this specific column

        lineage_path = []
        transformation_steps = []

        # For now, provide a placeholder
        lineage_path.append("source_data")
        transformation_steps.append(f"Derived {feature_name}")

        return lineage_path, transformation_steps

    def _rank_features_by_importance(self, features: List[FeatureInfo]) -> List[FeatureInfo]:
        """Rank features by importance scores."""
        # Sort by importance (descending)
        sorted_features = sorted(
            features,
            key=lambda f: f.importance if f.importance is not None else -1,
            reverse=True
        )

        # Assign ranks
        for i, feature in enumerate(sorted_features, 1):
            if feature.importance is not None:
                feature.importance_rank = i

        return sorted_features

    def _generate_content(
        self,
        features: List[FeatureInfo],
        statistical_profile: Optional[StatisticalProfile],
        lineage_graph: EnhancedLineageGraph
    ) -> str:
        """Generate the complete feature catalog content."""
        sections = []

        # Header
        sections.append(self._generate_header(features))

        # Feature Summary Table
        sections.append(self._generate_feature_summary_table(features))

        # Feature Importance (if available)
        if self.config.feature_importance:
            sections.append(self._generate_feature_importance_section(features))

        # Individual Feature Profiles
        sections.append(self._generate_feature_profiles(features))

        # Feature Correlations (if available)
        if statistical_profile and statistical_profile.correlation_matrix:
            sections.append(self._generate_correlation_section(statistical_profile))

        # Check for analyzers and add lineage diagram + evolution report
        tracker = get_global_tracker()
        has_checkpoints = (
            (hasattr(tracker, '_distribution_analyses') and tracker._distribution_analyses) or
            (hasattr(tracker, '_describe_profiles') and tracker._describe_profiles) or
            (hasattr(tracker, '_correlation_analyses') and tracker._correlation_analyses)
        )

        if has_checkpoints:
            # Add lineage diagram with analyzers in collapsible section
            sections.append(self._generate_lineage_diagram_with_analyzers_section(lineage_graph, tracker))

        # Pipeline Diagram (if available and no analyzers)
        elif self.config.include_lineage:
            sections.append(self._generate_pipeline_diagram_section())

        # Data Quality Summary
        if statistical_profile:
            sections.append(self._generate_data_quality_section(statistical_profile))

        # Reproducibility Information
        sections.append(self._generate_reproducibility_section())

        # Next Steps
        sections.append(self._generate_next_steps_section())

        # Footer
        sections.append(self._generate_footer(features))

        return '\n\n'.join(sections)

    def _generate_lineage_diagram_with_analyzers_section(
        self,
        lineage_graph: EnhancedLineageGraph,
        tracker
    ) -> str:
        """Generate lineage diagram with analyzers section."""
        lines = ["---\n"]
        lines.append("## Pipeline Lineage with Analysis Checkpoints\n")
        lines.append("*This diagram shows where analyzers were placed in the data pipeline*\n")
        lines.append("")

        # Add collapsible section for lineage diagram
        lines.append("<details>")
        lines.append("<summary><strong>Click to expand lineage diagram</strong></summary>")
        lines.append("")
        lines.append("```mermaid")

        # Generate lineage diagram with analyzer nodes
        diagram_content = self.generate_lineage_with_analyzers(lineage_graph, tracker)
        lines.append(diagram_content)

        lines.append("```")
        lines.append("")
        lines.append("**Legend**:")
        lines.append("- **Diamond nodes**: Data sources")
        lines.append("- **Hexagon nodes (blue)**: Filters and transformations")
        lines.append("- **Hexagon nodes (yellow)**: Analysis checkpoints")
        lines.append("- **Solid arrows**: Data flow")
        lines.append("- **Dotted arrows**: Analysis performed on data")
        lines.append("")
        lines.append("</details>")
        lines.append("")

        # Add link to evolution report and generate it
        lines.append("---\n")
        lines.append("## Feature Evolution Tracking\n")
        lines.append("*Detailed analysis of how features change through the pipeline*\n")

        # Generate evolution report
        output_dir = Path(self.output_path).parent if hasattr(self, 'output_path') else Path(".")
        evolution_path = output_dir / "feature_catalog_evolution.md"
        self.generate_feature_evolution_report(tracker, str(evolution_path))

        lines.append(f"**Evolution Report**: `feature_catalog_evolution.md`\n")

        return '\n'.join(lines)

    def _generate_header(self, features: List[FeatureInfo]) -> str:
        """Generate catalog header."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return f"""# Feature Catalog: {self.config.pipeline_name}

**Generated**: {timestamp}
**Pipeline**: {self.config.pipeline_name}
**Total Features**: {len(features)}
**Training Dataset**: {self.config.dataset_name}{f' ({self.config.row_count:,} rows)' if self.config.row_count else ''}

---"""

    def _generate_feature_summary_table(self, features: List[FeatureInfo]) -> str:
        """Generate feature summary table."""
        lines = ["## Feature Summary\n"]

        # Table header
        lines.append("| Feature | Type | Source | Nulls | Business Context |")
        lines.append("|---------|------|--------|-------|------------------|")

        # Table rows
        for feature in features[:self.config.max_features_in_summary]:
            null_pct = ""
            if feature.stats and feature.stats.missing:
                null_pct = f"{feature.stats.missing.null_percentage:.1f}%"

            # Truncate business context
            context = feature.business_context[:50] + "..." if len(feature.business_context) > 50 else feature.business_context

            # Add target indicator
            is_target = " **[TARGET]**" if feature.name == self.config.target_variable else ""

            lines.append(
                f"| {feature.name}{is_target} | {feature.data_type} | {feature.source} | "
                f"{null_pct} | {context} |"
            )

        if len(features) > self.config.max_features_in_summary:
            lines.append(f"\n*Showing {self.config.max_features_in_summary} of {len(features)} features*")

        return '\n'.join(lines)

    def _generate_feature_importance_section(self, features: List[FeatureInfo]) -> str:
        """Generate feature importance section."""
        lines = ["---\n", "**Feature Importance** (from model):\n"]

        features_with_importance = [f for f in features if f.importance is not None]
        features_with_importance.sort(key=lambda f: f.importance, reverse=True)

        for i, feature in enumerate(features_with_importance[:10], 1):
            lines.append(f"{i}. {feature.name} ({feature.importance:.2f})")

        return '\n'.join(lines)

    def _generate_feature_profiles(self, features: List[FeatureInfo]) -> str:
        """Generate detailed profiles for each feature."""
        lines = ["---\n", "## Feature Profiles\n"]

        for feature in features:
            lines.append(self._format_feature_profile(feature))
            lines.append("\n---\n")

        return '\n'.join(lines)

    def _format_feature_profile(self, feature: FeatureInfo) -> str:
        """Format a single feature profile."""
        lines = [f"### Feature: {feature.name}\n"]

        # Business context
        if self.config.include_business_context:
            lines.append(f"**Business Context**: \"{feature.business_context}\"\n")

        # Basic info
        lines.append(f"**Type**: {feature.data_type.capitalize()}")
        lines.append(f"**Role**: {'Target' if feature.name == self.config.target_variable else 'Predictor'}")

        if feature.importance is not None:
            importance_desc = "most important" if feature.importance_rank == 1 else f"rank {feature.importance_rank}"
            lines.append(f"**Importance**: {feature.importance:.2f} ({importance_desc})")

        # Lineage
        if self.config.include_lineage and feature.transformation_steps:
            lines.append("\n#### Source Lineage\n")
            lines.append("```")
            for step in feature.transformation_steps:
                lines.append(step)
            lines.append("```")

        # Statistical Profile
        if self.config.include_statistics and feature.stats:
            lines.append("\n#### Statistical Profile\n")
            lines.append(self._format_feature_statistics(feature.stats))

        # Distribution Visualization
        if self.config.include_distributions and feature.stats:
            if feature.stats.histogram_bins and feature.stats.histogram_counts:
                lines.append("\n#### Distribution Visualization\n")
                lines.append(self._format_distribution(feature.stats))

        # Missing Values
        if feature.stats and feature.stats.missing:
            lines.append("\n#### Missing Values\n")
            lines.append(self._format_missing_values(feature.stats.missing))

        # Data Quality
        if self.config.include_data_quality and feature.stats:
            lines.append("\n#### Data Quality Issues\n")
            lines.append(self._format_data_quality_issues(feature.stats))

        return '\n'.join(lines)

    def _format_feature_statistics(self, stats: FeatureStats) -> str:
        """Format statistical summary for a feature."""
        lines = ["```"]

        if stats.data_type == 'numeric':
            lines.append(f"Count: {stats.count:,}")
            if stats.mean is not None:
                lines.append(f"Mean: {stats.mean:.2f}")
            if stats.std is not None:
                lines.append(f"Std: {stats.std:.2f}")
            if stats.min_val is not None:
                lines.append(f"Min: {stats.min_val}")
            if stats.percentile_25 is not None:
                lines.append(f"25%: {stats.percentile_25:.2f}")
            if stats.percentile_50 is not None:
                lines.append(f"50%: {stats.percentile_50:.2f}")
            if stats.percentile_75 is not None:
                lines.append(f"75%: {stats.percentile_75:.2f}")
            if stats.max_val is not None:
                lines.append(f"Max: {stats.max_val}")

            if stats.distribution:
                lines.append(f"\nSkewness: {stats.distribution.skewness:.2f}")
                lines.append(f"Kurtosis: {stats.distribution.kurtosis:.2f}")
                lines.append(f"Shape: {stats.distribution.shape_description}")
        else:
            # Categorical
            lines.append(f"Unique Values: {stats.unique_count}")
            if stats.mode:
                lines.append(f"Mode: {stats.mode}")

        lines.append("```")
        return '\n'.join(lines)

    def _format_distribution(self, stats: FeatureStats) -> str:
        """Format distribution visualization."""
        from .statistical_report_generator import StatisticalReportGenerator

        generator = StatisticalReportGenerator()

        lines = ["```"]
        if stats.data_type == 'numeric':
            lines.append("Frequency Distribution:\n")
            lines.append(generator._generate_ascii_histogram(
                stats.histogram_bins,
                stats.histogram_counts,
                stats.count
            ))
        elif stats.value_counts:
            lines.append("Value Distribution:\n")
            lines.append(generator._generate_categorical_bars(
                stats.value_counts,
                stats.count
            ))

        lines.append("```")
        return '\n'.join(lines)

    def _format_missing_values(self, missing_info) -> str:
        """Format missing value information."""
        lines = ["```"]
        lines.append(f"NULL count: {missing_info.null_count:,} ({missing_info.null_percentage:.2f}%)")

        if missing_info.zero_count is not None and missing_info.zero_count > 0:
            lines.append(f"Zero count: {missing_info.zero_count:,} ({missing_info.zero_percentage:.1f}%)")

        lines.append(f"\nInterpretation: {missing_info.interpretation}")
        lines.append("```")
        return '\n'.join(lines)

    def _format_data_quality_issues(self, stats: FeatureStats) -> str:
        """Format data quality issues."""
        lines = ["```"]

        issues = []
        checks = []

        # Check missing values
        if stats.missing:
            if stats.missing.null_percentage == 0:
                checks.append("[OK] No NULL values")
            else:
                issues.append(f"[WARN] {stats.missing.null_percentage:.1f}% missing values")

        # Check outliers
        if stats.outliers:
            total_outliers = stats.outliers.lower_count + stats.outliers.upper_count
            if total_outliers == 0:
                checks.append("[OK] No outliers detected")
            else:
                total_pct = stats.outliers.lower_percentage + stats.outliers.upper_percentage
                if total_pct > 5:
                    issues.append(f"[WARN] {total_outliers:,} outliers ({total_pct:.2f}%)")
                else:
                    checks.append(f"[OK] {total_outliers:,} outliers ({total_pct:.2f}%) - acceptable")

        # Add checks and issues
        for check in checks:
            lines.append(check)
        for issue in issues:
            lines.append(issue)

        if not checks and not issues:
            lines.append("[OK] No quality issues detected")

        lines.append("```")
        return '\n'.join(lines)

    def _generate_correlation_section(self, statistical_profile: StatisticalProfile) -> str:
        """Generate correlation matrix section."""
        from .statistical_report_generator import StatisticalReportGenerator

        generator = StatisticalReportGenerator()
        return generator._generate_correlation_section(statistical_profile.correlation_matrix)

    def generate_lineage_with_analyzers(
        self,
        lineage_graph: EnhancedLineageGraph,
        tracker
    ) -> str:
        """
        Generate lineage diagram with analyzer nodes showing where analysis was performed.

        This creates a Mermaid diagram with:
        - Pipeline operations (sources, filters, joins, etc.)
        - Analyzer nodes (distribution, describe, correlation)
        - Connections showing which operation fed each analyzer

        Analyzers are rendered as separate nodes connected via dotted lines.
        """
        lines = []

        # Mermaid configuration
        lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '12px'}, 'flowchart': {'nodeSpacing': 150, 'rankSpacing': 100}}}%%")
        lines.append("graph TB")
        lines.append("")

        # Track node mappings
        node_ids = {}
        analyzer_nodes = []
        connection_id = 0

        # Step 1: Generate pipeline operation nodes
        for node in lineage_graph.nodes.values():
            operation_type = node.metadata.get('operation_type', '')
            operation_name = node.metadata.get('operation_name', 'unknown')

            # Get operation-specific shape
            shape_template = get_mermaid_shape_template(operation_type)
            content = operation_name
            node_label = shape_template.replace('{content}', content)

            # Generate unique node ID
            safe_id = f"Op_{connection_id}"
            node_ids[node.node_id] = safe_id

            # Store lineage_id mapping for analyzer linkage
            if hasattr(node, 'lineage_id') and node.lineage_id:
                node_ids[node.lineage_id] = safe_id

            connection_id += 1

            lines.append(f"    {safe_id}{node_label}")

        lines.append("")

        # Step 2: Generate analyzer nodes

        # Distribution analyzers
        if hasattr(tracker, '_distribution_analyses') and tracker._distribution_analyses:
            for analysis in tracker._distribution_analyses:
                checkpoint_name = analysis['checkpoint_name']
                variables = analysis.get('metadata', {}).get('variables', [])
                lineage_ref = analysis.get('result_dataframe_lineage_ref')

                # Create analyzer node (hexagon shape, yellow color)
                analyzer_id = f"Analyzer_{connection_id}"
                connection_id += 1

                # Hexagon shape for analyzers ({{content}} in Mermaid)
                var_list = ", ".join(variables[:3])
                if len(variables) > 3:
                    var_list += f" (+{len(variables)-3} more)"
                # Build hexagon label: {{checkpoint<br/>Distribution: vars}}
                content = f"{checkpoint_name}<br/>Distribution: {var_list}"
                analyzer_label = "{{" + content + "}}"
                lines.append(f"    {analyzer_id}{analyzer_label}")

                # Store analyzer info for connections
                analyzer_nodes.append({
                    'id': analyzer_id,
                    'type': 'distribution',
                    'lineage_ref': lineage_ref,
                    'checkpoint': checkpoint_name
                })

        # Describe profilers
        if hasattr(tracker, '_describe_profiles') and tracker._describe_profiles:
            for profile in tracker._describe_profiles:
                checkpoint_name = profile['checkpoint_name']
                stats = profile['stats']
                columns = stats.columns if hasattr(stats, 'columns') else []
                lineage_ref = stats.result_dataframe_lineage_ref if hasattr(stats, 'result_dataframe_lineage_ref') else None

                analyzer_id = f"Analyzer_{connection_id}"
                connection_id += 1

                col_list = ", ".join(columns[:3])
                if len(columns) > 3:
                    col_list += f" (+{len(columns)-3} more)"
                content = f"{checkpoint_name}<br/>Describe: {col_list}"
                analyzer_label = "{{" + content + "}}"
                lines.append(f"    {analyzer_id}{analyzer_label}")

                analyzer_nodes.append({
                    'id': analyzer_id,
                    'type': 'describe',
                    'lineage_ref': lineage_ref,
                    'checkpoint': checkpoint_name
                })

        # Correlation analyzers
        if hasattr(tracker, '_correlation_analyses') and tracker._correlation_analyses:
            for analysis in tracker._correlation_analyses:
                checkpoint_name = analysis['checkpoint_name']
                stats = analysis['stats']
                columns = stats.columns if hasattr(stats, 'columns') else []
                lineage_ref = stats.result_dataframe_lineage_ref if hasattr(stats, 'result_dataframe_lineage_ref') else None

                analyzer_id = f"Analyzer_{connection_id}"
                connection_id += 1

                content = f"{checkpoint_name}<br/>Correlation: {len(columns)} vars"
                analyzer_label = "{{" + content + "}}"
                lines.append(f"    {analyzer_id}{analyzer_label}")

                analyzer_nodes.append({
                    'id': analyzer_id,
                    'type': 'correlation',
                    'lineage_ref': lineage_ref,
                    'checkpoint': checkpoint_name
                })

        lines.append("")

        # Step 3: Generate pipeline connections (normal arrows)
        for edge in lineage_graph.edges:
            source_id = node_ids.get(edge.source_id)
            target_id = node_ids.get(edge.target_id)

            if source_id and target_id:
                # Check for fork edges
                is_fork = getattr(edge, 'is_fork_edge', False)
                if is_fork:
                    lines.append(f"    {source_id} ==> {target_id}")
                else:
                    lines.append(f"    {source_id} --> {target_id}")

        lines.append("")

        # Step 4: Connect analyzers to their source operations (dotted arrows)
        for analyzer in analyzer_nodes:
            lineage_ref = analyzer['lineage_ref']
            analyzer_id = analyzer['id']

            # Find the operation node that produced this lineage
            source_node_id = node_ids.get(lineage_ref) if lineage_ref else None

            if source_node_id:
                # Use dotted arrow to show analysis connection (not data flow)
                lines.append(f"    {source_node_id} -.->|analyzes| {analyzer_id}")
            else:
                # Fallback: connect to last operation node
                logger.warning(f"Could not find source operation for analyzer: {analyzer['checkpoint']}")

        lines.append("")

        # Step 5: Apply styling

        # Style pipeline operations
        for node in lineage_graph.nodes.values():
            if node.node_id in node_ids:
                mermaid_id = node_ids[node.node_id]
                operation_type = node.metadata.get('operation_type', 'default')
                class_name = get_node_class_name(operation_type)
                lines.append(f"    class {mermaid_id} {class_name}")

        lines.append("")

        # Style analyzer nodes (custom yellow style)
        for analyzer in analyzer_nodes:
            lines.append(f"    class {analyzer['id']} analyzerOp")

        lines.append("")

        # Generate style classes
        lines.append(generate_mermaid_style_classes())

        # Add analyzer-specific style (hexagon, yellow)
        lines.append(" classDef analyzerOp fill:#FFF9C4,stroke:#F57F17,stroke-width:2px,color:#000000")

        lines.append("")

        return '\n'.join(lines)

    def generate_feature_evolution_report(
        self,
        tracker,
        output_path: str
    ) -> str:
        """
        Generate a report showing how features evolve through pipeline checkpoints.

        This method extracts checkpoint data from:
        - tracker._distribution_analyses (distribution changes)
        - tracker._describe_profiles (statistical changes)
        - tracker._correlation_analyses (correlation changes)

        And generates a report showing:
        - How distributions shift at each checkpoint
        - How correlations change through transformations
        - How summary statistics evolve
        """
        lines = []

        lines.append("# Feature Evolution Report\n")
        lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("---\n")

        # Check if checkpoint data exists
        has_distribution = hasattr(tracker, '_distribution_analyses') and tracker._distribution_analyses
        has_describe = hasattr(tracker, '_describe_profiles') and tracker._describe_profiles
        has_correlation = hasattr(tracker, '_correlation_analyses') and tracker._correlation_analyses

        if not (has_distribution or has_describe or has_correlation):
            lines.append("*No checkpoint analyzers detected in pipeline.*\n")
            lines.append("\nTo use feature evolution tracking, add checkpoint analyzers:\n")
            lines.append("```python")
            lines.append("@distributionAnalysis(variables=['age', 'income'])")
            lines.append("def transform_data(df):")
            lines.append("    return df.filter(col('age') > 18)")
            lines.append("")
            lines.append("@describeProfiler(checkpoint_name='After Transform', columns=['age'])")
            lines.append("def add_features(df):")
            lines.append("    return df.withColumn('age_group', ...)")
            lines.append("")
            lines.append("@correlationAnalyzer(checkpoint_name='After Join')")
            lines.append("def join_data(df1, df2):")
            lines.append("    return df1.join(df2, 'customer_id')")
            lines.append("```\n")

            # Write empty report
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return str(output_file)

        # Section 1: Pipeline Checkpoint Overview
        lines.append("## Pipeline Checkpoints\n")

        all_checkpoints = []

        if has_distribution:
            for analysis in tracker._distribution_analyses:
                all_checkpoints.append({
                    'type': 'Distribution',
                    'name': analysis['checkpoint_name'],
                    'function': analysis['function_name'],
                    'timestamp': analysis['timestamp']
                })

        if has_describe:
            for profile in tracker._describe_profiles:
                all_checkpoints.append({
                    'type': 'Describe',
                    'name': profile['checkpoint_name'],
                    'function': profile['function_name'],
                    'timestamp': profile['timestamp']
                })

        if has_correlation:
            for analysis in tracker._correlation_analyses:
                all_checkpoints.append({
                    'type': 'Correlation',
                    'name': analysis['checkpoint_name'],
                    'function': analysis['function_name'],
                    'timestamp': analysis['timestamp']
                })

        # Sort by timestamp
        all_checkpoints.sort(key=lambda x: x['timestamp'])

        lines.append("| Step | Checkpoint | Type | Function |")
        lines.append("|------|-----------|------|----------|")
        for i, checkpoint in enumerate(all_checkpoints, 1):
            lines.append(f"| {i} | {checkpoint['name']} | {checkpoint['type']} | `{checkpoint['function']}()` |")

        lines.append("\n---\n")

        # Section 2: Correlation Evolution
        if has_correlation:
            lines.append("## Correlation Evolution\n")

            for analysis in tracker._correlation_analyses:
                checkpoint_name = analysis['checkpoint_name']
                stats = analysis['stats']

                lines.append(f"### Checkpoint: {checkpoint_name}\n")

                # Show correlation matrix
                lines.append("**Correlation Matrix**:\n")
                corr_df = stats.correlation_matrix

                # Convert to markdown table (simplified)
                lines.append("```")
                lines.append(corr_df.to_string())
                lines.append("```\n")

                # Show multicollinearity warnings
                if stats.multicollinearity_warnings:
                    lines.append("**Multicollinearity Warnings**:")
                    for warning in stats.multicollinearity_warnings:
                        lines.append(f"- {warning}")
                    lines.append("")
                else:
                    lines.append("No high correlations detected.\n")

                lines.append("---\n")

        # Write report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        logger.info(f"Generated feature evolution report: {output_file}")
        return str(output_file)

    def _generate_pipeline_diagram_section(self) -> str:
        """Generate placeholder for pipeline diagram."""
        return """---

## Feature Engineering Pipeline

*(Pipeline diagram would be generated here showing data sources -> transformations -> features)*

See the comprehensive lineage report for detailed pipeline visualization."""

    def _generate_data_quality_section(self, statistical_profile: StatisticalProfile) -> str:
        """Generate data quality summary."""
        from .statistical_report_generator import StatisticalReportGenerator

        generator = StatisticalReportGenerator()
        return generator._generate_quality_section(statistical_profile)

    def _generate_reproducibility_section(self) -> str:
        """Generate reproducibility information."""
        row_info = f"{self.config.row_count:,}" if self.config.row_count else "unknown"
        return f"""---

## Reproducibility Information

### Experiment Metadata

```
Experiment ID: {self.config.experiment_id or 'not_specified'}
Pipeline: {self.config.pipeline_name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Features Documented: {len(self.config.features) if self.config.features else 'all'}
```

### Data Sources

```
Dataset: {self.config.dataset_name}
Rows: {row_info}
```"""

    def _generate_next_steps_section(self) -> str:
        """Generate next steps section."""
        return """---

## Next Steps for Data Scientist

### Model Training

```python
# Load featured dataset
featured_df = spark.read.parquet("outputs/featured_dataset.parquet")

# All features documented in this catalog
# Feature importance rankings provided above
# Correlations and multicollinearity analyzed

# Ready for model training!
```

### Recommendations

1. **Feature Selection**
   - Review feature importance rankings
   - Consider removing highly correlated features

2. **Missing Value Handling**
   - Validate imputation strategies
   - Consider separate handling for different missing patterns

3. **Monitoring**
   - Track feature drift in production
   - Alert if distributions change significantly
   - Re-engineer features if source data changes

4. **Documentation**
   - Share this catalog with engineering team
   - Document feature transformations in model code
   - Link to this catalog in model documentation"""

    def _generate_footer(self, features: List[FeatureInfo]) -> str:
        """Generate report footer."""
        row_info = f" | Rows: {self.config.row_count:,}" if self.config.row_count else ""
        return f"\n---\n\n*Generated by PySpark StoryDoc | Feature count: {len(features)}{row_info}*"


def generate_feature_catalog(
    lineage_graph: EnhancedLineageGraph,
    df,
    output_path: str,
    **kwargs
) -> str:
    """
    Convenience function to generate a feature catalog.

    Args:
        lineage_graph: Enhanced lineage graph
        df: DataFrame to profile
        output_path: Where to save the catalog
        **kwargs: Configuration options (see FeatureCatalogConfig)

    Returns:
        Path to generated catalog
    """
    config = FeatureCatalogConfig(**kwargs)
    catalog = FeatureCatalog(config)
    return catalog.generate(lineage_graph, df, output_path)
