"""Business Flow Diagram - Visual Mermaid diagrams with configurable detail levels."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..visualization.lineage_diagram_generator import LineageDiagramGenerator
from .auxiliary_node_providers import (
    DescribeProfileProvider,
    DistributionAnalysisProvider,
)
from .auxiliary_nodes import AuxiliaryNodeManager
from .base_report import BaseReport, ReportConfig

logger = logging.getLogger(__name__)


@dataclass
class BusinessFlowDiagramConfig(ReportConfig):
    """Configuration for Business Flow Diagram generation."""
    detail_level: str = "impacting"  # "minimal", "impacting", "complete"
    show_metrics: bool = True
    show_execution_times: bool = True
    show_tracked_variables: bool = True
    show_distribution_markers: bool = True
    color_scheme: str = "operation_type"  # "operation_type", "impact_level", "execution_time"
    group_by_context: bool = True
    orientation: str = "TD"  # "TD", "LR", "RL", "BT"


class BusinessFlowDiagram(BaseReport):
    """
    Generates visual Mermaid diagrams showing business concepts and data flow.

    This report creates flowchart diagrams with three detail levels:
    - Minimal: Business concepts only
    - Impacting: Concepts + operations that change record count
    - Complete: All operations including passthrough
    """

    def __init__(self, config: Optional[BusinessFlowDiagramConfig] = None, **kwargs):
        """
        Initialize the Business Flow Diagram generator.

        Args:
            config: Configuration object
            **kwargs: Configuration parameters (alternative to config object)
        """
        if config is None and kwargs:
            config = BusinessFlowDiagramConfig(**kwargs)
        elif config is None:
            config = BusinessFlowDiagramConfig()

        super().__init__(config)
        self.config: BusinessFlowDiagramConfig = config

        # Initialize diagram generator based on detail level
        self._init_diagram_generator()

        # Initialize auxiliary node manager with providers
        self.auxiliary_node_manager = AuxiliaryNodeManager()
        self.auxiliary_node_manager.register_provider(DistributionAnalysisProvider())
        self.auxiliary_node_manager.register_provider(DescribeProfileProvider())

    def _validate_config(self) -> bool:
        """Validate configuration parameters."""
        valid_detail_levels = ["minimal", "impacting", "complete"]
        if self.config.detail_level not in valid_detail_levels:
            raise ValueError(
                f"Invalid detail_level: {self.config.detail_level}. "
                f"Must be one of {valid_detail_levels}"
            )

        valid_orientations = ["TD", "LR", "RL", "BT"]
        if self.config.orientation not in valid_orientations:
            raise ValueError(
                f"Invalid orientation: {self.config.orientation}. "
                f"Must be one of {valid_orientations}"
            )

        return True

    def _init_diagram_generator(self):
        """Initialize the underlying diagram generator with appropriate settings."""
        # Map detail level to operation filter
        operation_filter_map = {
            "minimal": "none",  # Will be handled specially
            "impacting": "impacting",
            "complete": "all"
        }

        operation_filter = operation_filter_map.get(
            self.config.detail_level,
            "impacting"
        )

        self.diagram_generator = LineageDiagramGenerator(
            show_column_metrics=self.config.show_metrics,
            show_execution_times=self.config.show_execution_times,
            operation_filter=operation_filter,
            group_raw_operations=self.config.group_by_context,
            show_passthrough_operations=(self.config.detail_level == "complete")
        )

    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the Business Flow Diagram report.

        Args:
            lineage_graph: EnhancedLineageGraph to visualize
            output_path: Path to write the markdown file

        Returns:
            Path to the generated report
        """
        logger.info(f"Generating Business Flow Diagram (detail_level={self.config.detail_level})")

        # Generate diagram based on detail level
        if self.config.detail_level == "minimal":
            diagram = self._generate_minimal_diagram(lineage_graph)
        else:
            # Use existing diagram generator for impacting and complete
            diagram = self.diagram_generator.create_detailed_mermaid(
                lineage_graph,
                title=f"Business Flow Diagram ({self.config.detail_level.title()})"
            )

        # Add auxiliary nodes (distribution analysis, describe profiles, etc.) if enabled
        if self.config.show_distribution_markers:
            from ..core.lineage_tracker import get_enhanced_tracker
            tracker = get_enhanced_tracker()
            lineage_to_mermaid = getattr(self.diagram_generator, '_lineage_to_mermaid', {})
            diagram = self.auxiliary_node_manager.add_auxiliary_nodes_to_diagram(
                diagram, tracker, lineage_to_mermaid
            )

        # Wrap in markdown with metadata
        content = self._generate_markdown(diagram, lineage_graph)

        # Write to file
        return self._write_report(content, output_path)

    def _generate_minimal_diagram(self, lineage_graph) -> str:
        """
        Generate minimal diagram showing only business concepts.

        Args:
            lineage_graph: EnhancedLineageGraph

        Returns:
            Mermaid diagram string
        """
        lines = []

        # Mermaid header with configuration
        lines.append("%%{init: {'theme':'base', 'themeVariables': {'fontSize': '12px', 'clusterBkg': '#F5F5F5', 'clusterBorder': '#666'}, 'flowchart': {'nodeSpacing': 150, 'rankSpacing': 100, 'curve': 'basis', 'padding': 25, 'htmlLabels': true}}}%%")
        lines.append(f"flowchart {self.config.orientation}")

        # Extract business concepts
        concepts = []
        for node_id, node in lineage_graph.nodes.items():
            if hasattr(node, 'metadata') and node.metadata:
                if node.metadata.get('operation_type') == 'business_concept':
                    concepts.append({
                        'node_id': node_id,
                        'name': node.metadata.get('operation_name', 'Unknown'),
                        'description': node.metadata.get('description', ''),
                        'execution_time': node.metadata.get('execution_time', 0),
                        'timestamp': node.timestamp
                    })

        # Sort by timestamp to maintain execution order
        concepts.sort(key=lambda c: c['timestamp'])

        # Create concept nodes
        for i, concept in enumerate(concepts, 1):
            node_label = f"BC{i}"
            name = concept['name']

            # Build node content
            content_parts = [f"**{name}**"]

            if self.config.show_execution_times and concept['execution_time'] > 0:
                content_parts.append(f"{self._format_duration(concept['execution_time'])}")

            node_content = "<br/>".join(content_parts)
            lines.append(f"    {node_label}[\"{node_content}\"]")

        # Create edges based on execution order
        for i in range(len(concepts) - 1):
            lines.append(f"    BC{i+1} --> BC{i+2}")

        # Add styling
        lines.append("")
        lines.append("    classDef conceptStyle fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px,color:#FFFFFF")
        for i in range(len(concepts)):
            lines.append(f"    class BC{i+1} conceptStyle")

        return '\n'.join(lines)

    def _generate_markdown(self, diagram: str, lineage_graph) -> str:
        """
        Generate complete markdown document with diagram.

        Args:
            diagram: Mermaid diagram string
            lineage_graph: EnhancedLineageGraph

        Returns:
            Complete markdown content
        """
        lines = []

        # Title and metadata
        lines.append(f"# Business Flow Diagram\n")
        lines.append(f"*Visual representation of data flow and business logic*\n")
        lines.append(f"**Detail Level:** {self.config.detail_level.title()}\n")
        lines.append("---\n")

        # Description based on detail level
        detail_descriptions = {
            "minimal": "This diagram shows only business concepts, providing a high-level overview of the pipeline.",
            "impacting": "This diagram shows business concepts and operations that impact record counts or tracked columns.",
            "complete": "This diagram shows all operations including passthrough operations, providing complete detail."
        }

        lines.append(f"\n{detail_descriptions[self.config.detail_level]}\n")

        # Statistics
        lines.append("\n## Diagram Statistics\n")
        lines.append(f"- Total Nodes: {len(lineage_graph.nodes)}")
        lines.append(f"- Total Edges: {len(lineage_graph.edges)}")
        lines.append(f"- Detail Level: {self.config.detail_level}")
        lines.append("")

        # The diagram
        lines.append("\n## Flow Diagram\n")
        lines.append("```mermaid")
        lines.append(diagram)
        lines.append("```\n")

        return '\n'.join(lines)

    def _generate_legend(self) -> List[str]:
        """Generate legend for the diagram using centralized style definitions."""
        from ..visualization.diagram_styles import get_legend_items

        lines = ["\n## Legend\n"]

        lines.append("**Node Types:**")
        # Get standardized legend items
        legend_items = get_legend_items()
        for emoji, name, description in legend_items:
            lines.append(f"- {emoji} **{name}**: {description}")

        if self.config.show_distribution_markers:
            lines.append("\n**Analysis Markers:**")
            lines.append("- DA-XXX: Distribution analysis points (dotted connections)")
            lines.append("- DP-XXX: Describe profile checkpoints (dotted connections)")

        lines.append("")
        return lines
