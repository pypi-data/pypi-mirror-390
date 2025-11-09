"""Main visualization interface for business lineage diagrams."""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.graph_builder import LineageGraph
from ..utils.exceptions import ValidationError, VisualizationError
from .graphviz_generator import (
    GraphvizFormat,
    GraphvizGenerator,
    GraphvizLayout,
    GraphvizStyle,
)
from .mermaid_generator import MermaidGenerator, MermaidStyle, MermaidTheme

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats for diagrams."""
    # Mermaid formats
    MERMAID = "mermaid"

    # Graphviz formats
    DOT = "dot"
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"

    # Text formats
    HTML = "html"
    MARKDOWN = "md"


@dataclass
class VisualizationConfig:
    """Configuration for visualization generation."""
    # Common settings
    title: Optional[str] = None
    include_metrics: bool = True
    include_execution_times: bool = True
    max_label_length: int = 30

    # Mermaid settings
    mermaid_theme: MermaidTheme = MermaidTheme.BUSINESS
    mermaid_direction: str = "TD"
    group_by_context: bool = True

    # Graphviz settings
    graphviz_layout: GraphvizLayout = GraphvizLayout.DOT
    graphviz_rankdir: str = "TB"
    cluster_by_context: bool = True
    show_technical_details: bool = True

    # Export settings
    output_directory: Optional[str] = None
    filename_prefix: str = "lineage"
    embed_styles: bool = True


class BusinessLineageVisualizer:
    """
    Main interface for generating business lineage visualizations.

    This class provides a unified interface to both Mermaid and Graphviz
    generators, with convenient methods for creating different types of
    diagrams and exporting them in various formats.
    """

    def __init__(
        self,
        config: Optional[VisualizationConfig] = None,
        mermaid_style: Optional[MermaidStyle] = None,
        graphviz_style: Optional[GraphvizStyle] = None,
    ):
        """
        Initialize the visualizer.

        Args:
            config: Visualization configuration
            mermaid_style: Custom Mermaid style settings
            graphviz_style: Custom Graphviz style settings
        """
        self.config = config or VisualizationConfig()

        # Initialize generators
        self.mermaid_generator = MermaidGenerator(
            theme=self.config.mermaid_theme,
            style=mermaid_style,
            include_technical_details=self.config.show_technical_details,
            max_label_length=self.config.max_label_length,
        )

        self.graphviz_generator = GraphvizGenerator(
            layout=self.config.graphviz_layout,
            style=graphviz_style,
            include_metrics=self.config.include_metrics,
            include_execution_times=self.config.include_execution_times,
            show_technical_details=self.config.show_technical_details,
        )

        # Track generated diagrams for batch export
        self._generated_diagrams: Dict[str, Dict[str, Any]] = {}

        logger.debug("Initialized BusinessLineageVisualizer")

    def create_business_flow(
        self,
        lineage_graph: LineageGraph,
        format: ExportFormat = ExportFormat.MERMAID,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a business flow diagram focusing on high-level business concepts.

        Args:
            lineage_graph: Lineage graph to visualize
            format: Output format for the diagram
            title: Optional title override
            **kwargs: Additional format-specific options

        Returns:
            Diagram content as string

        Example:
            >>> visualizer = BusinessLineageVisualizer()
            >>> flow = visualizer.create_business_flow(graph, ExportFormat.MERMAID)
        """
        try:
            diagram_title = title or self.config.title or "Business Data Flow"

            if format == ExportFormat.MERMAID:
                diagram = self.mermaid_generator.generate_flowchart(
                    lineage_graph,
                    direction=kwargs.get('direction', self.config.mermaid_direction),
                    title=diagram_title,
                    group_by_context=kwargs.get('group_by_context', self.config.group_by_context),
                )
            elif format in [ExportFormat.DOT, ExportFormat.SVG, ExportFormat.PNG, ExportFormat.PDF]:
                diagram = self.graphviz_generator.generate_business_flow(
                    lineage_graph,
                    title=diagram_title,
                    simplify=kwargs.get('simplify', True),
                )
            else:
                raise VisualizationError(f"Unsupported format for business flow: {format}")

            # Store for potential batch export
            self._generated_diagrams["business_flow"] = {
                'content': diagram,
                'format': format,
                'title': diagram_title,
                'type': 'business_flow'
            }

            logger.info(f"Created business flow diagram in {format.value} format")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create business flow: {e}")

    def create_technical_lineage(
        self,
        lineage_graph: LineageGraph,
        format: ExportFormat = ExportFormat.DOT,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a detailed technical lineage diagram.

        Args:
            lineage_graph: Lineage graph to visualize
            format: Output format for the diagram
            title: Optional title override
            **kwargs: Additional format-specific options

        Returns:
            Diagram content as string
        """
        try:
            diagram_title = title or self.config.title or "Technical Data Lineage"

            if format == ExportFormat.MERMAID:
                diagram = self.mermaid_generator.generate_flowchart(
                    lineage_graph,
                    direction=kwargs.get('direction', self.config.mermaid_direction),
                    title=diagram_title,
                    group_by_context=False,  # Flat structure for technical view
                )
            elif format in [ExportFormat.DOT, ExportFormat.SVG, ExportFormat.PNG, ExportFormat.PDF]:
                diagram = self.graphviz_generator.generate_lineage_graph(
                    lineage_graph,
                    title=diagram_title,
                    cluster_by_context=kwargs.get('cluster_by_context', self.config.cluster_by_context),
                    rankdir=kwargs.get('rankdir', self.config.graphviz_rankdir),
                )
            else:
                raise VisualizationError(f"Unsupported format for technical lineage: {format}")

            # Store for potential batch export
            self._generated_diagrams["technical_lineage"] = {
                'content': diagram,
                'format': format,
                'title': diagram_title,
                'type': 'technical_lineage'
            }

            logger.info(f"Created technical lineage diagram in {format.value} format")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create technical lineage: {e}")

    def create_timeline(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        show_execution_times: bool = True,
    ) -> str:
        """
        Create a timeline diagram showing execution order.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title override
            show_execution_times: Whether to include execution times

        Returns:
            Mermaid timeline diagram as string
        """
        try:
            diagram_title = title or self.config.title or "Execution Timeline"

            diagram = self.mermaid_generator.generate_timeline(
                lineage_graph,
                title=diagram_title,
                show_execution_times=show_execution_times,
            )

            # Store for potential batch export
            self._generated_diagrams["timeline"] = {
                'content': diagram,
                'format': ExportFormat.MERMAID,
                'title': diagram_title,
                'type': 'timeline'
            }

            logger.info("Created timeline diagram")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create timeline: {e}")

    def create_journey_map(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        actor: str = "Data Analyst",
    ) -> str:
        """
        Create a user journey map for the data processing workflow.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title override
            actor: Name of the actor performing the journey

        Returns:
            Mermaid journey map diagram as string
        """
        try:
            diagram_title = title or self.config.title or "Data Processing Journey"

            diagram = self.mermaid_generator.generate_journey_map(
                lineage_graph,
                title=diagram_title,
                actor=actor,
            )

            # Store for potential batch export
            self._generated_diagrams["journey_map"] = {
                'content': diagram,
                'format': ExportFormat.MERMAID,
                'title': diagram_title,
                'type': 'journey_map'
            }

            logger.info("Created journey map diagram")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create journey map: {e}")

    def create_impact_analysis(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        x_axis: str = "Complexity",
        y_axis: str = "Business Impact",
    ) -> str:
        """
        Create a quadrant chart for impact analysis.

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title override
            x_axis: Label for x-axis
            y_axis: Label for y-axis

        Returns:
            Mermaid quadrant chart diagram as string
        """
        try:
            diagram_title = title or self.config.title or "Business Impact Analysis"

            diagram = self.mermaid_generator.generate_quadrant_chart(
                lineage_graph,
                title=diagram_title,
                x_axis=x_axis,
                y_axis=y_axis,
            )

            # Store for potential batch export
            self._generated_diagrams["impact_analysis"] = {
                'content': diagram,
                'format': ExportFormat.MERMAID,
                'title': diagram_title,
                'type': 'impact_analysis'
            }

            logger.info("Created impact analysis diagram")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create impact analysis: {e}")

    def create_operation_detail(
        self,
        lineage_graph: LineageGraph,
        business_concept_id: str,
        title: Optional[str] = None,
    ) -> str:
        """
        Create a detailed view of operations within a business concept.

        Args:
            lineage_graph: Lineage graph to visualize
            business_concept_id: ID of the business concept to detail
            title: Optional title override

        Returns:
            Graphviz DOT diagram as string
        """
        try:
            diagram = self.graphviz_generator.generate_operation_detail(
                lineage_graph,
                business_concept_id,
                title=title,
            )

            # Store for potential batch export
            self._generated_diagrams[f"operation_detail_{business_concept_id}"] = {
                'content': diagram,
                'format': ExportFormat.DOT,
                'title': title or f"Operation Detail: {business_concept_id}",
                'type': 'operation_detail'
            }

            logger.info(f"Created operation detail for concept: {business_concept_id}")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create operation detail: {e}")

    def create_business_impact_flow(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        show_execution_times: bool = True,
        show_percentages: bool = True,
    ) -> str:
        """
        Create a top-down business impact flow showing count changes and filter logic.

        This visualization groups operations by business concept and shows:
        - Count changes between operations
        - Filter conditions and logic
        - Business impact flow

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title override
            show_execution_times: Whether to include execution times
            show_percentages: Whether to show percentage changes

        Returns:
            Mermaid flow diagram as string
        """
        try:
            from .impact_visualizer import BusinessImpactVisualizer

            diagram_title = title or self.config.title or "Business Impact Flow"

            impact_visualizer = BusinessImpactVisualizer(
                show_execution_times=show_execution_times,
                show_percentages=show_percentages
            )

            diagram = impact_visualizer.create_impact_mermaid(
                lineage_graph,
                title=diagram_title
            )

            # Store for potential batch export
            self._generated_diagrams["business_impact_flow"] = {
                'content': diagram,
                'format': ExportFormat.MERMAID,
                'title': diagram_title,
                'type': 'business_impact_flow'
            }

            logger.info("Created business impact flow diagram")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create business impact flow: {e}")

    def create_impact_summary(
        self,
        lineage_graph: LineageGraph,
        show_execution_times: bool = True,
        show_percentages: bool = True,
    ) -> str:
        """
        Create a text summary of business impacts.

        Args:
            lineage_graph: Lineage graph to analyze
            show_execution_times: Whether to include execution times
            show_percentages: Whether to show percentage changes

        Returns:
            Formatted text summary
        """
        try:
            from .impact_visualizer import BusinessImpactVisualizer

            impact_visualizer = BusinessImpactVisualizer(
                show_execution_times=show_execution_times,
                show_percentages=show_percentages
            )

            summary = impact_visualizer.create_impact_summary_table(lineage_graph)

            logger.info("Created business impact summary")
            return summary

        except Exception as e:
            raise VisualizationError(f"Failed to create impact summary: {e}")

    def create_detailed_operation_flow(
        self,
        lineage_graph: LineageGraph,
        title: Optional[str] = None,
        show_column_metrics: bool = True,
        show_percentages: bool = True,
        show_execution_times: bool = True,
    ) -> str:
        """
        Create a detailed operation flow showing each operation with full metrics.

        This visualization shows:
        - Each operation as its own node
        - Input/output record counts and tracked column distinct counts
        - Filter conditions and join details
        - Connections showing record count changes
        - Business concept groupings

        Args:
            lineage_graph: Lineage graph to visualize
            title: Optional title override
            show_column_metrics: Whether to show tracked column distinct counts
            show_percentages: Whether to show percentage changes
            show_execution_times: Whether to show execution times

        Returns:
            Mermaid flow diagram as string
        """
        try:
            from .lineage_diagram_generator import LineageDiagramGenerator

            diagram_title = title or self.config.title or "Detailed Operation Flow"

            detailed_visualizer = LineageDiagramGenerator(
                show_column_metrics=show_column_metrics,
                show_percentages=show_percentages,
                show_execution_times=show_execution_times
            )

            diagram = detailed_visualizer.create_detailed_mermaid(
                lineage_graph,
                title=diagram_title
            )

            # Store for potential batch export
            self._generated_diagrams["detailed_operation_flow"] = {
                'content': diagram,
                'format': ExportFormat.MERMAID,
                'title': diagram_title,
                'type': 'detailed_operation_flow'
            }

            logger.info("Created detailed operation flow diagram")
            return diagram

        except Exception as e:
            raise VisualizationError(f"Failed to create detailed operation flow: {e}")

    def create_detailed_flow_summary(
        self,
        lineage_graph: LineageGraph,
        show_column_metrics: bool = True,
        show_execution_times: bool = True,
    ) -> str:
        """
        Create a detailed text summary of the operation flow.

        Args:
            lineage_graph: Lineage graph to analyze
            show_column_metrics: Whether to include column metrics
            show_execution_times: Whether to include execution times

        Returns:
            Formatted text summary
        """
        try:
            from .lineage_diagram_generator import LineageDiagramGenerator

            detailed_visualizer = LineageDiagramGenerator(
                show_column_metrics=show_column_metrics,
                show_execution_times=show_execution_times
            )

            summary = detailed_visualizer.create_detailed_summary(lineage_graph)

            logger.info("Created detailed flow summary")
            return summary

        except Exception as e:
            raise VisualizationError(f"Failed to create detailed flow summary: {e}")

    def export_diagram(
        self,
        diagram_content: str,
        format: ExportFormat,
        filename: str,
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Export a diagram to a file.

        Args:
            diagram_content: The diagram content to export
            format: Export format
            filename: Output filename (without extension)
            output_dir: Output directory (uses config default if not provided)

        Returns:
            Path to the exported file

        Example:
            >>> visualizer = BusinessLineageVisualizer()
            >>> flow = visualizer.create_business_flow(graph)
            >>> path = visualizer.export_diagram(flow, ExportFormat.MERMAID, "business_flow")
        """
        try:
            # Determine output directory
            if output_dir is None:
                output_dir = self.config.output_directory or "."

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Determine file extension
            file_extension = self._get_file_extension(format)
            output_file = output_path / f"{filename}.{file_extension}"

            # Handle different export formats
            if format in [ExportFormat.MERMAID, ExportFormat.DOT]:
                # Text formats - save directly
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(diagram_content)

            elif format == ExportFormat.HTML:
                # Wrap in HTML for Mermaid diagrams
                if self._is_mermaid_diagram(diagram_content):
                    html_content = self._create_mermaid_html(diagram_content)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    raise VisualizationError("HTML export only supported for Mermaid diagrams")

            elif format == ExportFormat.MARKDOWN:
                # Wrap in Markdown code blocks
                md_content = self._create_markdown_content(diagram_content, format)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)

            elif format in [ExportFormat.SVG, ExportFormat.PNG, ExportFormat.PDF]:
                # These require external tools (Graphviz, Mermaid CLI)
                raise VisualizationError(
                    f"Export format {format.value} requires external tools. "
                    "Please install Graphviz or Mermaid CLI for binary exports."
                )

            else:
                raise VisualizationError(f"Unsupported export format: {format}")

            logger.info(f"Exported diagram to: {output_file}")
            return str(output_file)

        except Exception as e:
            raise VisualizationError(f"Failed to export diagram: {e}")

    def export_all_diagrams(
        self,
        output_dir: Optional[str] = None,
        formats: Optional[List[ExportFormat]] = None,
    ) -> Dict[str, List[str]]:
        """
        Export all generated diagrams to files.

        Args:
            output_dir: Output directory (uses config default if not provided)
            formats: List of formats to export (exports original formats if not provided)

        Returns:
            Dictionary mapping diagram types to lists of exported file paths
        """
        try:
            if not self._generated_diagrams:
                logger.warning("No diagrams have been generated yet")
                return {}

            exported_files = {}
            export_formats = formats or []

            for diagram_key, diagram_info in self._generated_diagrams.items():
                diagram_files = []
                original_format = diagram_info['format']

                # Export in original format
                if not formats or original_format in formats:
                    filename = f"{self.config.filename_prefix}_{diagram_key}"
                    file_path = self.export_diagram(
                        diagram_info['content'],
                        original_format,
                        filename,
                        output_dir
                    )
                    diagram_files.append(file_path)

                # Export in additional formats if requested
                for export_format in export_formats:
                    if export_format != original_format:
                        try:
                            filename = f"{self.config.filename_prefix}_{diagram_key}"
                            file_path = self.export_diagram(
                                diagram_info['content'],
                                export_format,
                                filename,
                                output_dir
                            )
                            diagram_files.append(file_path)
                        except VisualizationError as e:
                            logger.warning(f"Could not export {diagram_key} as {export_format.value}: {e}")

                exported_files[diagram_key] = diagram_files

            logger.info(f"Exported {len(self._generated_diagrams)} diagrams")
            return exported_files

        except Exception as e:
            raise VisualizationError(f"Failed to export all diagrams: {e}")

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of all generated diagrams."""
        return {
            'total_diagrams': len(self._generated_diagrams),
            'diagrams': {
                key: {
                    'type': info['type'],
                    'format': info['format'].value,
                    'title': info['title'],
                    'content_length': len(info['content'])
                }
                for key, info in self._generated_diagrams.items()
            },
            'config': {
                'mermaid_theme': self.config.mermaid_theme.value,
                'graphviz_layout': self.config.graphviz_layout.value,
                'include_metrics': self.config.include_metrics,
                'include_execution_times': self.config.include_execution_times,
            }
        }

    def clear_generated_diagrams(self) -> None:
        """Clear all generated diagrams from memory."""
        self._generated_diagrams.clear()
        logger.debug("Cleared all generated diagrams")

    def _get_file_extension(self, format: ExportFormat) -> str:
        """Get appropriate file extension for a format."""
        extensions = {
            ExportFormat.MERMAID: "mmd",
            ExportFormat.DOT: "dot",
            ExportFormat.SVG: "svg",
            ExportFormat.PNG: "png",
            ExportFormat.PDF: "pdf",
            ExportFormat.HTML: "html",
            ExportFormat.MARKDOWN: "md",
        }
        return extensions.get(format, "txt")

    def _is_mermaid_diagram(self, content: str) -> bool:
        """Check if content is a Mermaid diagram."""
        content = content.strip()

        # Check for Mermaid diagram types
        mermaid_keywords = [
            'flowchart', 'timeline', 'journey', 'quadrantChart',
            'graph', 'sequenceDiagram', 'classDiagram', 'stateDiagram',
            'erDiagram', 'gitgraph', 'pie', 'gantt'
        ]

        # Check if content contains any Mermaid keywords
        for keyword in mermaid_keywords:
            if keyword in content:
                return True

        return False

    def _create_mermaid_html(self, mermaid_content: str) -> str:
        """Create HTML wrapper for Mermaid diagrams."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Lineage Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{startOnLoad: true}});
    </script>
</head>
<body>
    <div class="mermaid">
{mermaid_content}
    </div>
</body>
</html>"""

    def _create_markdown_content(self, diagram_content: str, format: ExportFormat) -> str:
        """Create Markdown wrapper for diagrams."""
        if format == ExportFormat.MERMAID:
            return f"""# Business Lineage Diagram

```mermaid
{diagram_content}
```
"""
        elif format == ExportFormat.DOT:
            return f"""# Business Lineage Diagram

```dot
{diagram_content}
```
"""
        else:
            return f"""# Business Lineage Diagram

```
{diagram_content}
```
"""