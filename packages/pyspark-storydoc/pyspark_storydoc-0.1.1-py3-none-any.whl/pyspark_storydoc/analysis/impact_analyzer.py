#!/usr/bin/env python3
"""
Impact Analyzer for PySpark StoryDoc.

This module analyzes downstream impact of column changes, helping users
understand the ripple effects of modifications to data transformations.
"""

import logging
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Analyze downstream impact of column changes.

    This class provides tools to understand how changes to a column
    propagate through the data pipeline, identifying all affected
    downstream columns and critical dependency paths.
    """

    def __init__(self):
        """Initialize the impact analyzer."""
        self._dependency_graph = {}
        self._reverse_dependency_graph = {}
        self._column_metadata = {}

    def build_dependency_graph(
        self,
        expressions: List[Dict[str, Any]]
    ) -> None:
        """
        Build dependency graph from expression metadata.

        Args:
            expressions: List of expression dictionaries containing:
                - column_name: Name of the column
                - source_columns: List of source column names
                - operation_type: Type of operation
                - complexity_level: Complexity score
        """
        self._dependency_graph = {}
        self._reverse_dependency_graph = defaultdict(set)
        self._column_metadata = {}

        for expr in expressions:
            col_name = expr.get('column_name')
            source_cols = expr.get('source_columns', [])

            # Store metadata
            self._column_metadata[col_name] = {
                'operation_type': expr.get('operation_type', 'unknown'),
                'complexity_level': expr.get('complexity_level', 1),
                'expression': expr.get('expression', '')
            }

            # Build forward dependency graph (column -> depends on)
            self._dependency_graph[col_name] = source_cols

            # Build reverse dependency graph (column -> used by)
            for source in source_cols:
                self._reverse_dependency_graph[source].add(col_name)

    def analyze_column_impact(
        self,
        column_name: str
    ) -> Dict[str, Any]:
        """
        Analyze impact of changes to a column.

        Args:
            column_name: Name of the column to analyze

        Returns:
            Dictionary containing:
                - direct_dependencies: Columns that directly use this column
                - transitive_dependencies: All downstream columns (recursive)
                - critical_path: Longest dependency chain
                - total_impact: Total number of columns affected
                - risk_assessment: Description of impact
                - impact_tree: Hierarchical tree structure
        """
        if not self._dependency_graph:
            logger.warning("Dependency graph not built. Call build_dependency_graph first.")
            return self._empty_impact_result()

        # Get direct dependencies (columns that use this column)
        direct_deps = list(self._reverse_dependency_graph.get(column_name, set()))

        # Get all transitive dependencies
        transitive_deps = self._get_all_downstream_columns(column_name)

        # Find critical path (longest chain)
        critical_path = self._find_critical_path(column_name)

        # Calculate total impact
        total_impact = len(transitive_deps)

        # Assess risk
        risk_assessment = self._assess_impact_risk(
            column_name,
            len(direct_deps),
            total_impact,
            critical_path
        )

        # Build impact tree
        impact_tree = self.build_impact_tree(column_name)

        return {
            'column_name': column_name,
            'direct_dependencies': direct_deps,
            'transitive_dependencies': transitive_deps,
            'critical_path': critical_path,
            'total_impact': total_impact,
            'risk_assessment': risk_assessment,
            'impact_tree': impact_tree
        }

    def build_impact_tree(
        self,
        column_name: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Build hierarchical tree of impacts.

        Args:
            column_name: Root column name
            max_depth: Maximum tree depth to prevent infinite recursion

        Returns:
            Tree structure:
            {
                'column': str,
                'children': [tree, tree, ...],
                'metadata': dict
            }
        """
        if max_depth <= 0:
            return {
                'column': column_name,
                'children': [],
                'metadata': self._column_metadata.get(column_name, {}),
                'truncated': True
            }

        # Get direct children (columns that depend on this one)
        children_names = self._reverse_dependency_graph.get(column_name, set())

        children = []
        for child_name in sorted(children_names):
            child_tree = self.build_impact_tree(child_name, max_depth - 1)
            children.append(child_tree)

        return {
            'column': column_name,
            'children': children,
            'metadata': self._column_metadata.get(column_name, {}),
            'truncated': False
        }

    def find_critical_paths(self) -> List[Dict[str, Any]]:
        """
        Identify critical paths in the lineage graph.

        Critical paths are long dependency chains that represent
        high coupling and potential fragility.

        Returns:
            List of critical paths, each containing:
                - path: List of column names in order
                - length: Number of hops
                - complexity_sum: Sum of complexity scores
                - risk: Risk level (LOW/MEDIUM/HIGH)
        """
        if not self._dependency_graph:
            logger.warning("Dependency graph not built.")
            return []

        critical_paths = []

        # Find all leaf columns (columns with no downstream dependencies)
        leaf_columns = []
        for col_name in self._dependency_graph.keys():
            if not self._reverse_dependency_graph.get(col_name):
                leaf_columns.append(col_name)

        # For each leaf, find the longest path to a source
        for leaf in leaf_columns:
            path = self._find_longest_path_to_source(leaf)
            if len(path) > 1:  # Only include paths with dependencies
                complexity_sum = sum(
                    self._column_metadata.get(col, {}).get('complexity_level', 1)
                    for col in path
                )

                risk = self._assess_path_risk(len(path), complexity_sum)

                critical_paths.append({
                    'path': path,
                    'length': len(path),
                    'complexity_sum': complexity_sum,
                    'risk': risk
                })

        # Sort by length (longest first)
        critical_paths.sort(key=lambda x: x['length'], reverse=True)

        return critical_paths

    def format_impact_tree_text(
        self,
        tree: Dict[str, Any],
        indent: int = 0,
        is_last: bool = True,
        prefix: str = ""
    ) -> str:
        """
        Format impact tree as text with tree-style characters.

        Args:
            tree: Impact tree structure
            indent: Current indentation level
            is_last: Whether this is the last child
            prefix: Current line prefix

        Returns:
            Formatted tree string
        """
        lines = []

        # Current node
        connector = "└── " if is_last else "├── "
        if indent == 0:
            connector = ""

        # Add metadata annotation
        metadata = tree.get('metadata', {})
        complexity = metadata.get('complexity_level', 0)
        op_type = metadata.get('operation_type', 'unknown')

        annotation = f" (complexity: {complexity}, type: {op_type})"

        lines.append(f"{prefix}{connector}{tree['column']}{annotation}")

        # Children
        children = tree.get('children', [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)

            if indent == 0:
                child_prefix = ""
            else:
                child_prefix = prefix + ("    " if is_last else "│   ")

            child_text = self.format_impact_tree_text(
                child,
                indent + 1,
                is_last_child,
                child_prefix
            )
            lines.append(child_text)

        return "\n".join(lines)

    def _get_all_downstream_columns(self, column_name: str) -> List[str]:
        """
        Get all columns that transitively depend on the given column.

        Uses BFS to find all reachable columns in the reverse dependency graph.
        """
        visited = set()
        queue = deque([column_name])
        all_downstream = []

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)

            # Get direct dependents
            dependents = self._reverse_dependency_graph.get(current, set())

            for dependent in dependents:
                if dependent not in visited:
                    queue.append(dependent)
                    all_downstream.append(dependent)

        return all_downstream

    def _find_critical_path(self, column_name: str) -> List[str]:
        """
        Find the longest dependency chain starting from this column.

        Returns list of column names representing the critical path.
        """
        def dfs_longest_path(col: str, visited: Set[str]) -> List[str]:
            """DFS to find longest path."""
            if col in visited:
                return []

            visited.add(col)

            # Get all downstream columns
            children = self._reverse_dependency_graph.get(col, set())

            if not children:
                return [col]

            # Find longest path among children
            longest = []
            for child in children:
                child_path = dfs_longest_path(child, visited.copy())
                if len(child_path) > len(longest):
                    longest = child_path

            return [col] + longest

        return dfs_longest_path(column_name, set())

    def _find_longest_path_to_source(self, column_name: str) -> List[str]:
        """
        Find the longest path from this column back to source columns.

        Returns list of column names in reverse order (leaf to root).
        """
        def dfs_to_source(col: str, visited: Set[str]) -> List[str]:
            """DFS to find longest path to source."""
            if col in visited:
                return []

            visited.add(col)

            # Get dependencies (columns this one depends on)
            dependencies = self._dependency_graph.get(col, [])

            if not dependencies:
                # This is a source column
                return [col]

            # Find longest path among dependencies
            longest = []
            for dep in dependencies:
                dep_path = dfs_to_source(dep, visited.copy())
                if len(dep_path) > len(longest):
                    longest = dep_path

            return [col] + longest

        path = dfs_to_source(column_name, set())
        return path  # Return as-is (leaf to root order)

    def _assess_impact_risk(
        self,
        column_name: str,
        direct_count: int,
        total_count: int,
        critical_path: List[str]
    ) -> str:
        """
        Assess risk level of changes to a column.

        Returns: "LOW", "MEDIUM", or "HIGH"
        """
        # Get column metadata
        metadata = self._column_metadata.get(column_name, {})
        complexity = metadata.get('complexity_level', 1)

        # Factors that increase risk:
        # 1. High direct dependency count
        # 2. High total impact
        # 3. Long critical path
        # 4. High complexity

        risk_score = 0

        # Direct dependencies (0-3 points)
        if direct_count >= 5:
            risk_score += 3
        elif direct_count >= 3:
            risk_score += 2
        elif direct_count >= 1:
            risk_score += 1

        # Total impact (0-3 points)
        if total_count >= 10:
            risk_score += 3
        elif total_count >= 5:
            risk_score += 2
        elif total_count >= 1:
            risk_score += 1

        # Critical path length (0-2 points)
        if len(critical_path) >= 5:
            risk_score += 2
        elif len(critical_path) >= 3:
            risk_score += 1

        # Complexity (0-2 points)
        if complexity >= 8:
            risk_score += 2
        elif complexity >= 5:
            risk_score += 1

        # Map score to risk level
        if risk_score >= 7:
            return "HIGH"
        elif risk_score >= 4:
            return "MEDIUM"
        else:
            return "LOW"

    def _assess_path_risk(self, path_length: int, complexity_sum: int) -> str:
        """
        Assess risk of a dependency path.

        Returns: "LOW", "MEDIUM", or "HIGH"
        """
        # Risk based on path length and total complexity
        risk_score = 0

        # Path length contribution
        if path_length >= 7:
            risk_score += 3
        elif path_length >= 5:
            risk_score += 2
        elif path_length >= 3:
            risk_score += 1

        # Complexity contribution
        avg_complexity = complexity_sum / path_length if path_length > 0 else 0
        if avg_complexity >= 7:
            risk_score += 3
        elif avg_complexity >= 5:
            risk_score += 2
        elif avg_complexity >= 3:
            risk_score += 1

        # Map to risk level
        if risk_score >= 5:
            return "HIGH"
        elif risk_score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _empty_impact_result(self) -> Dict[str, Any]:
        """Return empty impact result structure."""
        return {
            'column_name': '',
            'direct_dependencies': [],
            'transitive_dependencies': [],
            'critical_path': [],
            'total_impact': 0,
            'risk_assessment': 'UNKNOWN',
            'impact_tree': {}
        }

    def get_impact_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about the dependency graph.

        Returns:
            Dictionary with summary metrics:
                - total_columns: Total number of columns
                - source_columns: Columns with no dependencies
                - derived_columns: Columns with dependencies
                - leaf_columns: Columns with no downstream dependencies
                - max_chain_length: Longest dependency chain
                - avg_dependencies: Average number of dependencies per column
        """
        if not self._dependency_graph:
            return {
                'total_columns': 0,
                'source_columns': 0,
                'derived_columns': 0,
                'leaf_columns': 0,
                'max_chain_length': 0,
                'avg_dependencies': 0.0
            }

        total_columns = len(self._dependency_graph)

        # Source columns (no dependencies)
        source_columns = sum(
            1 for deps in self._dependency_graph.values()
            if not deps
        )

        # Derived columns (have dependencies)
        derived_columns = total_columns - source_columns

        # Leaf columns (no downstream dependencies)
        leaf_columns = sum(
            1 for col in self._dependency_graph.keys()
            if not self._reverse_dependency_graph.get(col)
        )

        # Find max chain length
        critical_paths = self.find_critical_paths()
        max_chain_length = max(
            (path['length'] for path in critical_paths),
            default=0
        )

        # Average dependencies per column
        total_deps = sum(
            len(deps) for deps in self._dependency_graph.values()
        )
        avg_dependencies = total_deps / total_columns if total_columns > 0 else 0.0

        return {
            'total_columns': total_columns,
            'source_columns': source_columns,
            'derived_columns': derived_columns,
            'leaf_columns': leaf_columns,
            'max_chain_length': max_chain_length,
            'avg_dependencies': round(avg_dependencies, 2)
        }
