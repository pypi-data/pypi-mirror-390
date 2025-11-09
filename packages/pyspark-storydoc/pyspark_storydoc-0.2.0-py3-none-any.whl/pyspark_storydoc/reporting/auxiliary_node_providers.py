"""
Concrete implementations of auxiliary node providers.

This module contains specific providers for different types of auxiliary nodes:
- DistributionAnalysisProvider: Adds distribution analysis nodes
- DescribeProfileProvider: Adds describe profiler nodes
"""

import logging
from typing import Dict, List

from .auxiliary_nodes import AuxiliaryNodeDefinition, AuxiliaryNodeProvider

logger = logging.getLogger(__name__)


class DistributionAnalysisProvider(AuxiliaryNodeProvider):
    """
    Provider for distribution analysis auxiliary nodes.

    Reads distribution analyses from the tracker and creates nodes showing
    which variables were analyzed at each step.
    """

    def get_node_type(self) -> str:
        return "distribution_analysis"

    def get_node_id_prefix(self) -> str:
        return "DA"

    def get_starting_node_counter(self) -> int:
        return 1000

    def get_nodes(self, tracker, lineage_to_mermaid: Dict[str, str]) -> List[AuxiliaryNodeDefinition]:
        """Generate distribution analysis nodes from tracker data."""
        nodes = []

        # Check if tracker has distribution analyses
        if not hasattr(tracker, '_distribution_analyses') or not tracker._distribution_analyses:
            return nodes

        node_counter = self.get_starting_node_counter()

        # Get enhanced graph for resolving parent operations
        enhanced_graph = tracker.get_lineage_graph()

        for idx, analysis in enumerate(tracker._distribution_analyses, 1):
            metadata = analysis.get('metadata', {})
            function_name = analysis.get('function_name', 'unknown')
            variables_analyzed = metadata.get('variables_analyzed', [])
            checkpoint_name = metadata.get('checkpoint_name', function_name)

            if not variables_analyzed:
                continue

            # Create node label
            step_name = checkpoint_name.replace('_', ' ').title() if checkpoint_name else function_name.replace('_', ' ').title()
            variables_str = ", ".join(variables_analyzed)
            label = f"[DA-{idx:03d}]<br/>{step_name}<br/>Analyzing: {variables_str}"

            # Resolve parent operation at diagram generation time
            # This allows us to find the actual operation that created the analyzed DataFrame
            parent_operation_id = self._resolve_parent_operation(
                analysis.get('result_dataframe_lineage_ref'),
                enhanced_graph,
                checkpoint_name,
                tracker
            )

            # Create node definition
            node = AuxiliaryNodeDefinition(
                node_id=f"{self.get_node_id_prefix()}_{node_counter}",
                label=label,
                parent_operation_id=parent_operation_id,
                node_type=self.get_node_type(),
                shape="rectangle",  # Distribution uses rectangles
                metadata={
                    'reference_id': f"DA-{idx:03d}",
                    'function_name': function_name,
                    'variables': variables_analyzed,
                    'timestamp': analysis.get('timestamp', 0.0)
                }
            )

            nodes.append(node)
            node_counter += 1
            logger.debug(f"Created distribution analysis node: {node.node_id}")

        return nodes

    def _resolve_parent_operation(
        self,
        lineage_ref: str,
        enhanced_graph,
        checkpoint_name: str,
        tracker=None
    ) -> str:
        """
        Find the actual last operation that produces the given lineage.

        This method makes distribution checkpoints attach to the correct operation
        by resolving the parent operation at diagram generation time.

        Args:
            lineage_ref: The lineage ID string captured at checkpoint time
            enhanced_graph: The complete lineage graph
            checkpoint_name: Name of the checkpoint (for logging)
            tracker: Global tracker instance

        Returns:
            The operation ID to use as parent for the distribution analysis node
        """
        if not lineage_ref:
            logger.warning(f"No lineage reference for distribution checkpoint '{checkpoint_name}'")
            return None

        # Check if tracker has a lineage registry
        if tracker:
            if hasattr(tracker, 'lineage_id_tracker'):
                id_tracker = tracker.lineage_id_tracker

                # Check for registry
                if hasattr(id_tracker, 'lineage_registry'):
                    registry = id_tracker.lineage_registry
                elif hasattr(id_tracker, 'registry'):
                    registry = id_tracker.registry
                elif hasattr(id_tracker, '_registry'):
                    registry = id_tracker._registry
                else:
                    registry = None
            elif hasattr(tracker, '_lineage_registry'):
                registry = tracker._lineage_registry
            else:
                registry = None

            if registry and lineage_ref in registry:
                # Look for child lineages (edges where this lineage is the source)
                child_lineages = [
                    edge.target_id for edge in enhanced_graph.edges
                    if edge.source_id == lineage_ref
                ]

                if child_lineages:
                    # Use the last child (most recent operation)
                    child_lineage_id = child_lineages[-1]
                    logger.debug(f"Resolved distribution checkpoint '{checkpoint_name}' to child lineage: {child_lineage_id}")
                    return child_lineage_id

        # Fallback: return the original lineage_ref
        return lineage_ref


class DescribeProfileProvider(AuxiliaryNodeProvider):
    """
    Provider for describe profiler auxiliary nodes.

    Reads describe profiles from the tracker and creates nodes showing
    which columns were profiled at each checkpoint.
    """

    def get_node_type(self) -> str:
        return "describe_profile"

    def get_node_id_prefix(self) -> str:
        return "DP"

    def get_starting_node_counter(self) -> int:
        return 2000

    def get_nodes(self, tracker, lineage_to_mermaid: Dict[str, str]) -> List[AuxiliaryNodeDefinition]:
        """Generate describe profile nodes from tracker data."""
        nodes = []

        # Check if tracker has describe profiles
        if not hasattr(tracker, '_describe_profiles') or not tracker._describe_profiles:
            return nodes

        node_counter = self.get_starting_node_counter()

        # Get enhanced graph for resolving parent operations
        enhanced_graph = tracker.get_lineage_graph()

        for idx, profile in enumerate(tracker._describe_profiles, 1):
            checkpoint_name = profile.get('checkpoint_name', 'Unknown')
            stats = profile.get('stats')

            if not stats:
                continue

            # Create node label with column information
            columns_str = ", ".join(stats.columns[:3])  # Show first 3 columns
            if len(stats.columns) > 3:
                columns_str += f", ... (+{len(stats.columns) - 3} more)"

            label = f"[DP-{idx:03d}]<br/>{checkpoint_name}<br/>Profiled: {columns_str}"

            # Resolve parent operation at diagram generation time
            # This allows decorator order independence - we find the actual last operation
            # that produces the profiled DataFrame's lineage, regardless of when
            # @describeProfiler was applied relative to @track_lineage
            parent_operation_id = self._resolve_parent_operation(
                stats.result_dataframe_lineage_ref,
                enhanced_graph,
                checkpoint_name,
                tracker
            )


            # Create node definition
            node = AuxiliaryNodeDefinition(
                node_id=f"{self.get_node_id_prefix()}_{node_counter}",
                label=label,
                parent_operation_id=parent_operation_id,
                node_type=self.get_node_type(),
                shape="hexagon",  # Describe profiles use hexagons
                metadata={
                    'reference_id': f"DP-{idx:03d}",
                    'checkpoint_name': checkpoint_name,
                    'columns': stats.columns,
                    'row_count': stats.row_count,
                    'column_count': stats.column_count,
                    'timestamp': profile.get('timestamp', 0.0)
                }
            )

            nodes.append(node)
            node_counter += 1
            logger.debug(f"Created describe profile node: {node.node_id}")

        return nodes

    def _resolve_parent_operation(
        self,
        lineage_ref: str,
        enhanced_graph,
        checkpoint_name: str,
        tracker=None
    ) -> str:
        """
        Find the actual last operation that produces the given lineage.

        This method makes the describeProfiler decorator order-independent by
        resolving the parent operation at diagram generation time rather than
        at decorator execution time.

        Strategy:
        1. Find all operations that have this lineage ID in their metadata
        2. For each candidate, check if it has children (e.g., materialize operations)
        3. If children exist, use the last child as the parent
        4. Otherwise, use the operation itself

        Args:
            lineage_ref: The lineage ID string captured at profiling time
            enhanced_graph: The complete lineage graph
            checkpoint_name: Name of the checkpoint (for logging)

        Returns:
            The operation ID to use as parent for the describe profile node
        """
        if not lineage_ref:
            logger.warning(f"No lineage reference for profile '{checkpoint_name}'")
            return None

        # lineage_ref is the lineage ID (like "lid_xxx") captured at decorator time
        # Strategy: Check tracker's lineage registry to find related lineages

        # Check if tracker has a lineage registry or id tracker
        if tracker:
            # Try lineage_id_tracker
            if hasattr(tracker, 'lineage_id_tracker'):
                id_tracker = tracker.lineage_id_tracker

                # Check for registry or similar
                if hasattr(id_tracker, 'lineage_registry'):
                    registry = id_tracker.lineage_registry
                elif hasattr(id_tracker, 'registry'):
                    registry = id_tracker.registry
                elif hasattr(id_tracker, '_registry'):
                    registry = id_tracker._registry
                else:
                    registry = None
            elif hasattr(tracker, '_lineage_registry'):
                registry = tracker._lineage_registry
            else:
                registry = None

            if registry and lineage_ref in registry:
                # Check if this lineage has children in the graph
                # IMPORTANT: Enhanced graph edges use lineage IDs, not operation IDs!

                # Look for child lineages (edges where this lineage is the source)
                child_lineages = [
                    edge.target_id for edge in enhanced_graph.edges
                    if edge.source_id == lineage_ref
                ]

                if child_lineages:
                    # Found child lineages! Use the last one (most recent operation)
                    child_lineage_id = child_lineages[-1]
                    logger.debug(f"Resolved profile '{checkpoint_name}' to child lineage: {child_lineage_id}")
                    return child_lineage_id

        # Fallback: return the original lineage_ref
        return lineage_ref
