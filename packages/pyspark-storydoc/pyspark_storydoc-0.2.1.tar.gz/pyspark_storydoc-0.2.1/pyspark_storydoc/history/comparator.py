"""
Lineage comparator for detecting differences between snapshots.

This module provides the LineageComparator class which:
- Compares two lineage snapshots and identifies differences
- Detects added/removed/changed operations
- Compares governance metadata for common operations
- Compares expression logic with similarity scoring
- Generates structured diff objects with detailed change information

The comparison algorithm uses normalization to handle non-semantic differences
(whitespace, formatting) and provides similarity scoring for expressions.
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import (
    ChangeType,
    ExpressionDiff,
    GovernanceDiff,
    GraphDiff,
    LineageDiff,
    OperationDiff,
)

logger = logging.getLogger(__name__)


class LineageComparator:
    """
    Compares two lineage snapshots to identify differences.

    This class provides comprehensive comparison capabilities:
    - Graph structure comparison (operations and edges)
    - Operation-level comparison (expressions, metrics)
    - Governance metadata comparison
    - Expression similarity scoring

    Example:
        >>> comparator = LineageComparator()
        >>> diff = comparator.compare_snapshots(snapshot_a, snapshot_b)
        >>> print(f"Operations changed: {len(diff.operation_diffs)}")
        >>> print(f"Has governance drift: {diff.has_governance_drift}")
    """

    def __init__(
        self,
        similarity_threshold: float = 0.95,
        ignore_whitespace: bool = True,
        ignore_comments: bool = True,
    ):
        """
        Initialize the lineage comparator.

        Args:
            similarity_threshold: Threshold for "equivalent" expressions (default: 0.95)
            ignore_whitespace: Ignore whitespace differences (default: True)
            ignore_comments: Ignore comment differences (default: True)
        """
        self.similarity_threshold = similarity_threshold
        self.ignore_whitespace = ignore_whitespace
        self.ignore_comments = ignore_comments

        logger.debug(
            f"Initialized LineageComparator with similarity_threshold={similarity_threshold}"
        )

    def compare_snapshots(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> LineageDiff:
        """
        Compare two complete snapshots and return detailed differences.

        This is the main entry point for snapshot comparison. It orchestrates
        all sub-comparisons (graph, operations, governance, expressions).

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            LineageDiff object containing complete comparison results

        Example:
            >>> diff = comparator.compare_snapshots(snapshot_a, snapshot_b)
            >>> if diff.has_differences():
            ...     print("Snapshots differ!")
            ...     print(diff.get_summary())
        """
        logger.info(
            f"Comparing snapshots: {snapshot_a['snapshot_id']} vs {snapshot_b['snapshot_id']}"
        )

        # Extract lineage graphs
        graph_a = self._parse_lineage_graph(snapshot_a.get("lineage_graph", "{}"))
        graph_b = self._parse_lineage_graph(snapshot_b.get("lineage_graph", "{}"))

        # Compare graph structure
        graph_diff = self.compare_graphs(graph_a, graph_b)

        # Compare operations
        operation_diffs = self._compare_all_operations(
            snapshot_a, snapshot_b, graph_diff
        )

        # Compare governance metadata
        governance_diffs = self._compare_all_governance(
            snapshot_a, snapshot_b, graph_diff
        )

        # Compare expressions
        expression_diffs = self._compare_all_expressions(
            snapshot_a, snapshot_b, graph_diff
        )

        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(
            graph_diff, operation_diffs, governance_diffs, expression_diffs
        )

        # Create LineageDiff result
        lineage_diff = LineageDiff(
            snapshot_id_a=snapshot_a["snapshot_id"],
            snapshot_id_b=snapshot_b["snapshot_id"],
            snapshot_a_metadata=self._extract_snapshot_metadata(snapshot_a),
            snapshot_b_metadata=self._extract_snapshot_metadata(snapshot_b),
            compared_at=datetime.now(),
            graph_diff=graph_diff,
            operation_diffs=operation_diffs,
            governance_diffs=governance_diffs,
            expression_diffs=expression_diffs,
            summary_stats=summary_stats,
        )

        logger.info(f"Comparison complete: {lineage_diff.get_summary()}")

        return lineage_diff

    def compare_graphs(
        self,
        graph_a: Dict[str, Any],
        graph_b: Dict[str, Any],
    ) -> GraphDiff:
        """
        Compare graph structures and identify differences.

        This method compares:
        - Operations (nodes in the graph)
        - Edges (dependencies between operations)
        - Business concepts

        Args:
            graph_a: First lineage graph
            graph_b: Second lineage graph

        Returns:
            GraphDiff object with structural differences

        Example:
            >>> graph_diff = comparator.compare_graphs(graph_a, graph_b)
            >>> print(f"Added: {len(graph_diff.operations_added)}")
            >>> print(f"Removed: {len(graph_diff.operations_removed)}")
        """
        # Extract operation IDs (normalized)
        ops_a = {
            self._normalize_operation_id(op)
            for op in graph_a.get("nodes", [])
        }
        ops_b = {
            self._normalize_operation_id(op)
            for op in graph_b.get("nodes", [])
        }

        # Calculate set differences
        operations_added = list(ops_b - ops_a)
        operations_removed = list(ops_a - ops_b)
        operations_common = list(ops_a & ops_b)

        # Determine which common operations were modified
        operations_modified = []
        operations_unchanged = []

        for op_id in operations_common:
            op_a = self._find_operation(graph_a, op_id)
            op_b = self._find_operation(graph_b, op_id)

            if self._operations_differ(op_a, op_b):
                operations_modified.append(op_id)
            else:
                operations_unchanged.append(op_id)

        # Compare edges
        edges_a = {
            self._normalize_edge(edge)
            for edge in graph_a.get("edges", [])
        }
        edges_b = {
            self._normalize_edge(edge)
            for edge in graph_b.get("edges", [])
        }

        edges_added = list(edges_b - edges_a)
        edges_removed = list(edges_a - edges_b)

        # Compare business concepts
        concepts_a = self._extract_business_concepts(graph_a)
        concepts_b = self._extract_business_concepts(graph_b)

        business_concepts_added = list(concepts_b - concepts_a)
        business_concepts_removed = list(concepts_a - concepts_b)

        graph_diff = GraphDiff(
            operations_added=operations_added,
            operations_removed=operations_removed,
            operations_modified=operations_modified,
            operations_unchanged=operations_unchanged,
            edges_added=edges_added,
            edges_removed=edges_removed,
            business_concepts_added=business_concepts_added,
            business_concepts_removed=business_concepts_removed,
        )

        logger.debug(f"Graph diff: {graph_diff.get_summary()}")

        return graph_diff

    def compare_operations(
        self,
        op_a: Dict[str, Any],
        op_b: Dict[str, Any],
    ) -> OperationDiff:
        """
        Compare two operations and identify differences.

        Args:
            op_a: First operation record
            op_b: Second operation record

        Returns:
            OperationDiff object with operation-level differences

        Example:
            >>> op_diff = comparator.compare_operations(op_a, op_b)
            >>> if op_diff.has_significant_change():
            ...     print("Significant change detected!")
        """
        operation_id = op_a.get("operation_id") or op_b.get("operation_id")

        # Determine change type
        if op_a is None:
            change_type = ChangeType.ADDED
        elif op_b is None:
            change_type = ChangeType.REMOVED
        elif self._operations_differ(op_a, op_b):
            change_type = ChangeType.MODIFIED
        else:
            change_type = ChangeType.UNCHANGED

        # Extract expressions
        expr_a = op_a.get("expression_json") if op_a else None
        expr_b = op_b.get("expression_json") if op_b else None

        # Calculate expression similarity
        expression_similarity = 1.0
        if expr_a and expr_b:
            expression_similarity = self.calculate_similarity(expr_a, expr_b)
        elif expr_a != expr_b:
            expression_similarity = 0.0

        # Create OperationDiff
        operation_diff = OperationDiff(
            operation_id=operation_id,
            change_type=change_type,
            business_concept=op_a.get("business_concept") if op_a else op_b.get("business_concept"),
            operation_type=op_a.get("operation_type") if op_a else op_b.get("operation_type"),
            description_before=op_a.get("description") if op_a else None,
            description_after=op_b.get("description") if op_b else None,
            expression_before=expr_a,
            expression_after=expr_b,
            expression_similarity=expression_similarity,
            metrics_before=self._extract_operation_metrics(op_a) if op_a else {},
            metrics_after=self._extract_operation_metrics(op_b) if op_b else {},
        )

        return operation_diff

    def calculate_similarity(
        self,
        expr_a: str,
        expr_b: str,
    ) -> float:
        """
        Calculate similarity between two expressions.

        This method uses:
        1. Text normalization (whitespace, comments)
        2. Token-based comparison
        3. Levenshtein-like sequence matching

        Args:
            expr_a: First expression (JSON string)
            expr_b: Second expression (JSON string)

        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)

        Example:
            >>> score = comparator.calculate_similarity(expr1, expr2)
            >>> if score > 0.95:
            ...     print("Expressions are equivalent")
        """
        # Normalize expressions
        norm_a = self._normalize_expression(expr_a)
        norm_b = self._normalize_expression(expr_b)

        # Exact match after normalization
        if norm_a == norm_b:
            return 1.0

        # Calculate sequence similarity
        similarity = SequenceMatcher(None, norm_a, norm_b).ratio()

        return similarity

    def _parse_lineage_graph(self, graph_json: str) -> Dict[str, Any]:
        """Parse lineage graph JSON string."""
        try:
            if isinstance(graph_json, dict):
                return graph_json
            return json.loads(graph_json)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Failed to parse lineage graph, returning empty graph")
            return {"nodes": [], "edges": [], "metadata": {}}

    def _normalize_operation_id(self, operation: Dict[str, Any]) -> str:
        """
        Normalize operation ID to handle non-semantic differences.

        We create a canonical ID based on:
        - Operation type
        - Business concept
        - Description (normalized)

        This allows us to match operations even if their IDs changed.
        """
        op_type = operation.get("type", "")
        business_concept = operation.get("business_concept", "")
        description = operation.get("description", "")

        # Normalize description
        norm_desc = re.sub(r'\s+', ' ', description.strip().lower())

        # Create canonical ID
        canonical = f"{op_type}:{business_concept}:{norm_desc}"

        # Return hash to keep IDs manageable
        return hashlib.md5(canonical.encode()).hexdigest()[:16]

    def _normalize_edge(self, edge: Dict[str, Any]) -> Tuple[str, str]:
        """Normalize edge for comparison."""
        source = edge.get("source", "")
        target = edge.get("target", "")
        return (source, target)

    def _normalize_expression(self, expression: str) -> str:
        """
        Normalize expression for comparison.

        Removes:
        - Extra whitespace (if ignore_whitespace=True)
        - Comments (if ignore_comments=True)
        - Formatting differences
        """
        norm = expression

        if self.ignore_whitespace:
            # Normalize whitespace
            norm = re.sub(r'\s+', ' ', norm)
            norm = norm.strip()

        if self.ignore_comments:
            # Remove single-line comments
            norm = re.sub(r'//.*?$', '', norm, flags=re.MULTILINE)
            # Remove multi-line comments
            norm = re.sub(r'/\*.*?\*/', '', norm, flags=re.DOTALL)

        return norm

    def _find_operation(
        self,
        graph: Dict[str, Any],
        operation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Find operation in graph by normalized ID."""
        for node in graph.get("nodes", []):
            if self._normalize_operation_id(node) == operation_id:
                return node
        return None

    def _operations_differ(
        self,
        op_a: Dict[str, Any],
        op_b: Dict[str, Any],
    ) -> bool:
        """Check if two operations have meaningful differences."""
        # Compare descriptions
        desc_a = op_a.get("description", "")
        desc_b = op_b.get("description", "")

        if desc_a != desc_b:
            return True

        # Compare expressions
        expr_a = op_a.get("expression_json")
        expr_b = op_b.get("expression_json")

        if expr_a and expr_b:
            similarity = self.calculate_similarity(expr_a, expr_b)
            if similarity < self.similarity_threshold:
                return True

        return False

    def _extract_business_concepts(self, graph: Dict[str, Any]) -> Set[str]:
        """Extract unique business concepts from graph."""
        concepts = set()
        for node in graph.get("nodes", []):
            concept = node.get("business_concept")
            if concept:
                concepts.add(concept)
        return concepts

    def _extract_snapshot_metadata(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metadata from snapshot."""
        return {
            "pipeline_name": snapshot.get("pipeline_name"),
            "environment": snapshot.get("environment"),
            "captured_at": snapshot.get("captured_at"),
            "version": snapshot.get("version"),
            "user": snapshot.get("user"),
            "summary_stats": snapshot.get("summary_stats", {}),
        }

    def _extract_operation_metrics(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from operation record."""
        return {
            "row_count_before": operation.get("row_count_before"),
            "row_count_after": operation.get("row_count_after"),
            "row_count_change_pct": operation.get("row_count_change_pct"),
            "execution_time_seconds": operation.get("execution_time_seconds"),
        }

    def _compare_all_operations(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        graph_diff: GraphDiff,
    ) -> List[OperationDiff]:
        """Compare all operations between snapshots."""
        operation_diffs = []

        # Get operation records
        ops_a = {op["operation_id"]: op for op in snapshot_a.get("operations", [])}
        ops_b = {op["operation_id"]: op for op in snapshot_b.get("operations", [])}

        # Compare added operations
        for op_id in graph_diff.operations_added:
            # Find the actual operation (need to map normalized ID back)
            op_b = self._find_operation_by_normalized_id(snapshot_b, op_id)
            if op_b:
                diff = self.compare_operations(None, op_b)
                operation_diffs.append(diff)

        # Compare removed operations
        for op_id in graph_diff.operations_removed:
            op_a = self._find_operation_by_normalized_id(snapshot_a, op_id)
            if op_a:
                diff = self.compare_operations(op_a, None)
                operation_diffs.append(diff)

        # Compare modified operations
        for op_id in graph_diff.operations_modified:
            op_a = self._find_operation_by_normalized_id(snapshot_a, op_id)
            op_b = self._find_operation_by_normalized_id(snapshot_b, op_id)
            if op_a and op_b:
                diff = self.compare_operations(op_a, op_b)
                operation_diffs.append(diff)

        return operation_diffs

    def _find_operation_by_normalized_id(
        self,
        snapshot: Dict[str, Any],
        normalized_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Find operation record by normalized ID."""
        graph = self._parse_lineage_graph(snapshot.get("lineage_graph", "{}"))
        node = self._find_operation(graph, normalized_id)

        if node:
            # Find corresponding operation record
            for op in snapshot.get("operations", []):
                if op.get("operation_id") == node.get("id"):
                    return op

        return None

    def _compare_all_governance(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        graph_diff: GraphDiff,
    ) -> List[GovernanceDiff]:
        """Compare all governance metadata between snapshots."""
        governance_diffs = []

        # Get governance records
        gov_a = {g["operation_id"]: g for g in snapshot_a.get("governance", [])}
        gov_b = {g["operation_id"]: g for g in snapshot_b.get("governance", [])}

        # Compare governance for common and modified operations
        common_ops = set(graph_diff.operations_modified + graph_diff.operations_unchanged)

        for op_id in common_ops:
            # Find governance records
            gov_record_a = gov_a.get(op_id)
            gov_record_b = gov_b.get(op_id)

            if gov_record_a and gov_record_b:
                diff = self._compare_governance_records(op_id, gov_record_a, gov_record_b)
                if diff.has_changes():
                    governance_diffs.append(diff)

        return governance_diffs

    def _compare_governance_records(
        self,
        operation_id: str,
        gov_a: Dict[str, Any],
        gov_b: Dict[str, Any],
    ) -> GovernanceDiff:
        """Compare two governance records."""
        changed_fields = []

        # Compare key fields
        if gov_a.get("business_justification") != gov_b.get("business_justification"):
            changed_fields.append("business_justification")

        if gov_a.get("pii_processing") != gov_b.get("pii_processing"):
            changed_fields.append("pii_processing")

        if gov_a.get("data_classification") != gov_b.get("data_classification"):
            changed_fields.append("data_classification")

        if gov_a.get("approval_status") != gov_b.get("approval_status"):
            changed_fields.append("approval_status")

        # Compare risk assessments (as JSON strings)
        risks_a = json.dumps(gov_a.get("risks", []), sort_keys=True)
        risks_b = json.dumps(gov_b.get("risks", []), sort_keys=True)
        if risks_a != risks_b:
            changed_fields.append("risks")

        return GovernanceDiff(
            operation_id=operation_id,
            business_justification_changed="business_justification" in changed_fields,
            pii_processing_changed="pii_processing" in changed_fields,
            risk_assessment_changed="risks" in changed_fields,
            approval_status_changed="approval_status" in changed_fields,
            data_classification_changed="data_classification" in changed_fields,
            fields_before=gov_a,
            fields_after=gov_b,
            changed_fields=changed_fields,
        )

    def _compare_all_expressions(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        graph_diff: GraphDiff,
    ) -> List[ExpressionDiff]:
        """Compare all expressions between snapshots."""
        expression_diffs = []

        # Get operation records
        ops_a = {op["operation_id"]: op for op in snapshot_a.get("operations", [])}
        ops_b = {op["operation_id"]: op for op in snapshot_b.get("operations", [])}

        # Compare expressions for modified operations
        for op_id in graph_diff.operations_modified:
            op_a = self._find_operation_by_normalized_id(snapshot_a, op_id)
            op_b = self._find_operation_by_normalized_id(snapshot_b, op_id)

            if op_a and op_b:
                expr_a = op_a.get("expression_json")
                expr_b = op_b.get("expression_json")

                if expr_a and expr_b and expr_a != expr_b:
                    similarity = self.calculate_similarity(expr_a, expr_b)

                    expression_diff = ExpressionDiff(
                        operation_id=op_id,
                        expression_before=expr_a,
                        expression_after=expr_b,
                        similarity_score=similarity,
                    )

                    expression_diffs.append(expression_diff)

        return expression_diffs

    def _calculate_summary_stats(
        self,
        graph_diff: GraphDiff,
        operation_diffs: List[OperationDiff],
        governance_diffs: List[GovernanceDiff],
        expression_diffs: List[ExpressionDiff],
    ) -> Dict[str, Any]:
        """Calculate summary statistics for comparison."""
        return {
            "total_operations_a": (
                len(graph_diff.operations_removed)
                + len(graph_diff.operations_modified)
                + len(graph_diff.operations_unchanged)
            ),
            "total_operations_b": (
                len(graph_diff.operations_added)
                + len(graph_diff.operations_modified)
                + len(graph_diff.operations_unchanged)
            ),
            "operations_added": len(graph_diff.operations_added),
            "operations_removed": len(graph_diff.operations_removed),
            "operations_modified": len(graph_diff.operations_modified),
            "operations_unchanged": len(graph_diff.operations_unchanged),
            "governance_changes": len(governance_diffs),
            "expression_changes": len(expression_diffs),
            "significant_changes": len([
                d for d in operation_diffs if d.has_significant_change()
            ]),
        }
