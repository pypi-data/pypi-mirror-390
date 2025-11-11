"""
Snapshot manager for capturing lineage history.

This module handles:
- Capturing current lineage graph from tracker
- Extracting governance metadata
- Calculating metrics (row counts, distinct counts, etc.)
- Serializing lineage graph to JSON
- Generating snapshot IDs and timestamps
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


class SnapshotManager:
    """
    Manager for capturing and serializing lineage snapshots.

    This class extracts lineage information from the global tracker
    and prepares it for storage in Delta Lake tables.

    Example:
        >>> from pyspark_storydoc import get_global_tracker
        >>> manager = SnapshotManager(
        ...     spark=spark,
        ...     pipeline_name="customer_analysis",
        ...     environment="development"
        ... )
        >>> snapshot_data = manager.capture_snapshot()
    """

    def __init__(
        self,
        spark: SparkSession,
        pipeline_name: Optional[str] = None,
        environment: str = "development",
        version: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize snapshot manager.

        Args:
            spark: Active SparkSession
            pipeline_name: Name of the pipeline (default: auto-generated)
            environment: Environment tag (dev/staging/prod/testing)
            version: Code version (Git SHA, tag, etc.)
            metadata: Additional metadata to attach to snapshot
        """
        self.spark = spark
        self.pipeline_name = pipeline_name or f"pipeline_{uuid.uuid4().hex[:8]}"
        self.environment = environment
        self.version = version
        self.metadata = metadata or {}

        # Execution metadata
        self.spark_app_id = spark.sparkContext.applicationId
        self.user = spark.sparkContext.sparkUser()

        logger.debug(
            f"Initialized SnapshotManager for pipeline '{self.pipeline_name}' "
            f"in environment '{self.environment}'"
        )

    def capture_snapshot(self) -> Dict[str, Any]:
        """
        Capture a complete lineage snapshot from the global tracker.

        This method:
        1. Retrieves the current lineage graph from the tracker
        2. Extracts operations, governance, and metrics
        3. Serializes the graph to JSON
        4. Generates a unique snapshot ID
        5. Returns structured data ready for storage

        Returns:
            Dictionary containing:
                - snapshot_data: Core snapshot record
                - operations_data: List of operation records
                - governance_data: List of governance records
                - metrics_data: List of metric records

        Raises:
            Exception: If tracker is not available or snapshot capture fails
        """
        from pyspark_storydoc import get_global_tracker

        try:
            # Get tracker and lineage graph
            tracker = get_global_tracker()
            lineage_graph = tracker.get_lineage_graph()

            if lineage_graph is None:
                logger.warning("No lineage graph available - returning empty snapshot")
                return self._create_empty_snapshot()

            # Generate snapshot ID
            snapshot_id = self._generate_snapshot_id()
            captured_at = datetime.utcnow()

            # Extract data from lineage graph
            graph_json = self._serialize_graph(lineage_graph)
            operations = self._extract_operations(lineage_graph, snapshot_id)
            governance = self._extract_governance(lineage_graph, snapshot_id)
            metrics = self._extract_metrics(lineage_graph, snapshot_id)

            # Calculate summary statistics
            summary_stats = self._calculate_summary_stats(lineage_graph)

            # Build snapshot record
            snapshot_data = {
                "snapshot_id": snapshot_id,
                "pipeline_name": self.pipeline_name,
                "environment": self.environment,
                "captured_at": captured_at,
                "spark_app_id": self.spark_app_id,
                "user": self.user,
                "version": self.version,
                "lineage_graph": graph_json,
                "summary_stats": summary_stats,
                "metadata": self.metadata,
            }

            logger.info(
                f"Captured snapshot {snapshot_id} for pipeline '{self.pipeline_name}' "
                f"({len(operations)} operations, {len(governance)} governance records, "
                f"{len(metrics)} metrics)"
            )

            return {
                "snapshot_data": snapshot_data,
                "operations_data": operations,
                "governance_data": governance,
                "metrics_data": metrics,
            }

        except Exception as e:
            logger.error(f"Failed to capture snapshot: {str(e)}", exc_info=True)
            raise

    def _generate_snapshot_id(self) -> str:
        """
        Generate a unique snapshot ID.

        Returns:
            UUID-based snapshot ID
        """
        return str(uuid.uuid4())

    def _serialize_graph(self, lineage_graph: Any) -> str:
        """
        Serialize lineage graph to JSON.

        Args:
            lineage_graph: LineageGraph object from tracker

        Returns:
            JSON string representation of the graph
        """
        try:
            # Convert graph to dictionary
            graph_dict = {
                "nodes": [],
                "edges": [],
                "metadata": {},
            }

            # Extract nodes
            for node in lineage_graph.nodes:
                node_dict = {
                    "id": getattr(node, "id", str(node)),
                    "type": getattr(node, "node_type", type(node).__name__),
                    "label": getattr(node, "label", ""),
                    "description": getattr(node, "description", ""),
                    "metadata": getattr(node, "metadata", {}),
                }
                graph_dict["nodes"].append(node_dict)

            # Extract edges
            for edge in lineage_graph.edges:
                edge_dict = {
                    "source": getattr(edge, "source", ""),
                    "target": getattr(edge, "target", ""),
                    "edge_type": getattr(edge, "edge_type", ""),
                    "metadata": getattr(edge, "metadata", {}),
                }
                graph_dict["edges"].append(edge_dict)

            # Add graph-level metadata
            graph_dict["metadata"] = {
                "graph_name": getattr(lineage_graph, "name", ""),
                "node_count": len(graph_dict["nodes"]),
                "edge_count": len(graph_dict["edges"]),
            }

            return json.dumps(graph_dict, default=str)

        except Exception as e:
            logger.error(f"Failed to serialize graph: {str(e)}", exc_info=True)
            return json.dumps({"error": str(e), "nodes": [], "edges": []})

    def _extract_operations(
        self, lineage_graph: Any, snapshot_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract operation details from lineage graph.

        Args:
            lineage_graph: LineageGraph object
            snapshot_id: Snapshot ID to associate with operations

        Returns:
            List of operation records
        """
        operations = []

        for node in lineage_graph.nodes:
            # Skip non-operation nodes
            node_type = getattr(node, "node_type", type(node).__name__)
            if node_type in ["BusinessConceptNode", "ContextGroupNode"]:
                continue

            operation = {
                "snapshot_id": snapshot_id,
                "operation_id": getattr(node, "id", str(node)),
                "operation_type": node_type,
                "business_concept": getattr(node, "business_concept", None),
                "description": getattr(node, "description", ""),
                "expression_json": self._extract_expression(node),
                "row_count_before": getattr(node, "row_count_before", None),
                "row_count_after": getattr(node, "row_count_after", None),
                "row_count_change_pct": self._calculate_row_count_change(node),
                "execution_time_seconds": getattr(node, "execution_time", None),
                "columns_in": getattr(node, "input_columns", []),
                "columns_out": getattr(node, "output_columns", []),
                "metadata": getattr(node, "metadata", {}),
            }

            operations.append(operation)

        return operations

    def _extract_governance(
        self, lineage_graph: Any, snapshot_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract governance metadata from lineage graph.

        Args:
            lineage_graph: LineageGraph object
            snapshot_id: Snapshot ID to associate with governance records

        Returns:
            List of governance records
        """
        governance_records = []

        for node in lineage_graph.nodes:
            # Check if node has governance metadata
            governance_meta = getattr(node, "governance_metadata", None)
            if not governance_meta:
                continue

            governance = {
                "snapshot_id": snapshot_id,
                "operation_id": getattr(node, "id", str(node)),
                "business_justification": getattr(
                    governance_meta, "business_justification", None
                ),
                "customer_impact_level": getattr(
                    governance_meta, "customer_impact_level", None
                ),
                "impacting_columns": getattr(
                    governance_meta, "impacting_columns", []
                ),
                "pii_processing": getattr(governance_meta, "pii_processing", False),
                "pii_columns": getattr(governance_meta, "pii_columns", []),
                "data_classification": getattr(
                    governance_meta, "data_classification", None
                ),
                "risks": self._extract_risks(governance_meta),
                "approval_status": getattr(governance_meta, "approval_status", None),
                "approved_by": getattr(governance_meta, "approved_by", None),
                "approval_date": getattr(governance_meta, "approval_date", None),
                "approval_reference": getattr(
                    governance_meta, "approval_reference", None
                ),
                "bias_risk_score": getattr(governance_meta, "bias_risk_score", None),
                "fairness_metrics": getattr(governance_meta, "fairness_metrics", []),
                "metadata": getattr(governance_meta, "metadata", {}),
            }

            governance_records.append(governance)

        return governance_records

    def _extract_metrics(
        self, lineage_graph: Any, snapshot_id: str
    ) -> List[Dict[str, Any]]:
        """
        Extract metrics from lineage graph.

        Args:
            lineage_graph: LineageGraph object
            snapshot_id: Snapshot ID to associate with metrics

        Returns:
            List of metric records
        """
        metrics = []

        # Pipeline-level metrics
        metrics.append({
            "snapshot_id": snapshot_id,
            "metric_name": "operation_count",
            "metric_value": float(len(lineage_graph.nodes)),
            "metric_unit": "count",
            "scope": "pipeline",
            "scope_id": self.pipeline_name,
            "metadata": {},
        })

        # Node-level metrics
        for node in lineage_graph.nodes:
            node_id = getattr(node, "id", str(node))

            # Row count metric
            row_count = getattr(node, "row_count_after", None)
            if row_count is not None:
                metrics.append({
                    "snapshot_id": snapshot_id,
                    "metric_name": "row_count",
                    "metric_value": float(row_count),
                    "metric_unit": "count",
                    "scope": "operation",
                    "scope_id": node_id,
                    "metadata": {},
                })

            # Execution time metric
            execution_time = getattr(node, "execution_time", None)
            if execution_time is not None:
                metrics.append({
                    "snapshot_id": snapshot_id,
                    "metric_name": "execution_time",
                    "metric_value": float(execution_time),
                    "metric_unit": "seconds",
                    "scope": "operation",
                    "scope_id": node_id,
                    "metadata": {},
                })

        return metrics

    def _extract_expression(self, node: Any) -> Optional[str]:
        """
        Extract expression JSON from a node.

        Args:
            node: Operation node

        Returns:
            JSON string of expression, or None
        """
        expression = getattr(node, "expression", None)
        if expression:
            try:
                return json.dumps(expression, default=str)
            except Exception:
                return str(expression)
        return None

    def _extract_risks(self, governance_meta: Any) -> List[Dict[str, Any]]:
        """
        Extract risk assessments from governance metadata.

        Args:
            governance_meta: Governance metadata object

        Returns:
            List of risk dictionaries
        """
        risks = getattr(governance_meta, "risks", [])
        if not risks:
            return []

        risk_dicts = []
        for risk in risks:
            risk_dict = {
                "risk_id": getattr(risk, "risk_id", None),
                "category": getattr(risk, "category", None),
                "description": getattr(risk, "description", None),
                "severity": getattr(risk, "severity", None),
                "likelihood": getattr(risk, "likelihood", None),
                "mitigation_status": getattr(risk, "mitigation_status", None),
            }
            risk_dicts.append(risk_dict)

        return risk_dicts

    def _calculate_row_count_change(self, node: Any) -> Optional[float]:
        """
        Calculate row count change percentage.

        Args:
            node: Operation node

        Returns:
            Percentage change, or None if not calculable
        """
        before = getattr(node, "row_count_before", None)
        after = getattr(node, "row_count_after", None)

        if before is not None and after is not None and before > 0:
            return ((after - before) / before) * 100.0

        return None

    def _calculate_summary_stats(self, lineage_graph: Any) -> Dict[str, Any]:
        """
        Calculate summary statistics for the lineage graph.

        Args:
            lineage_graph: LineageGraph object

        Returns:
            Dictionary of summary statistics
        """
        stats = {
            "operation_count": 0,
            "business_concept_count": 0,
            "governance_operation_count": 0,
            "total_row_count": None,
            "execution_time_seconds": None,
        }

        total_rows = 0
        total_time = 0.0
        has_rows = False
        has_time = False

        for node in lineage_graph.nodes:
            node_type = getattr(node, "node_type", type(node).__name__)

            if node_type == "BusinessConceptNode":
                stats["business_concept_count"] += 1
            else:
                stats["operation_count"] += 1

            # Check for governance metadata
            if getattr(node, "governance_metadata", None):
                stats["governance_operation_count"] += 1

            # Aggregate row counts
            row_count = getattr(node, "row_count_after", None)
            if row_count is not None:
                total_rows += row_count
                has_rows = True

            # Aggregate execution time
            exec_time = getattr(node, "execution_time", None)
            if exec_time is not None:
                total_time += exec_time
                has_time = True

        if has_rows:
            stats["total_row_count"] = total_rows
        if has_time:
            stats["execution_time_seconds"] = total_time

        return stats

    def _create_empty_snapshot(self) -> Dict[str, Any]:
        """
        Create an empty snapshot when no lineage is available.

        Returns:
            Empty snapshot structure
        """
        snapshot_id = self._generate_snapshot_id()
        captured_at = datetime.utcnow()

        snapshot_data = {
            "snapshot_id": snapshot_id,
            "pipeline_name": self.pipeline_name,
            "environment": self.environment,
            "captured_at": captured_at,
            "spark_app_id": self.spark_app_id,
            "user": self.user,
            "version": self.version,
            "lineage_graph": json.dumps({"nodes": [], "edges": [], "metadata": {}}),
            "summary_stats": {
                "operation_count": 0,
                "business_concept_count": 0,
                "governance_operation_count": 0,
                "total_row_count": None,
                "execution_time_seconds": None,
            },
            "metadata": self.metadata,
        }

        return {
            "snapshot_data": snapshot_data,
            "operations_data": [],
            "governance_data": [],
            "metrics_data": [],
        }
