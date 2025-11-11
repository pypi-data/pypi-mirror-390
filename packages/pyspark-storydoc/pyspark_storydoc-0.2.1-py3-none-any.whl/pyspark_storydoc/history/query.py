"""
Query interface for lineage history.

This module provides a high-level API for querying historical lineage
snapshots from Delta Lake tables.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from pyspark.sql import SparkSession

from .storage_factory import create_storage

logger = logging.getLogger(__name__)


class LineageHistory:
    """
    Query interface for lineage history.

    This class provides convenient methods for retrieving and analyzing
    historical lineage snapshots stored in Delta Lake tables.

    Example:
        >>> history = LineageHistory(table_path="./lineage_history")
        >>>
        >>> # Get latest snapshot
        >>> snapshot = history.get_latest_snapshot(
        ...     pipeline_name="customer_analysis",
        ...     environment="production"
        ... )
        >>>
        >>> # List all snapshots
        >>> snapshots = history.list_snapshots(
        ...     pipeline_name="customer_analysis",
        ...     start_date="2024-01-01"
        ... )
        >>>
        >>> # Get specific snapshot
        >>> snapshot = history.get_snapshot(snapshot_id="abc123")
    """

    def __init__(
        self,
        table_path: str,
        spark: Optional[SparkSession] = None,
        storage_backend: str = "auto",
    ):
        """
        Initialize lineage history query interface.

        Args:
            table_path: Path to storage tables (Delta Lake or Parquet)
            spark: SparkSession (default: active session)
            storage_backend: Storage backend to use:
                - "auto" (default): Use Delta Lake if available, fallback to Parquet
                - "delta": Force Delta Lake (raises error if not available)
                - "parquet": Force Parquet (useful for testing or compatibility)

        Raises:
            RuntimeError: If no active SparkSession is available
            ValueError: If requested storage backend is not available
        """
        # Get SparkSession
        if spark is None:
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.getActiveSession()
                if spark is None:
                    raise RuntimeError("No active SparkSession found")
            except Exception as e:
                logger.error(f"Failed to get SparkSession: {str(e)}")
                raise

        self.spark = spark
        self.table_path = table_path
        self.storage_backend = storage_backend

        # Initialize storage (auto-detect or force specific backend)
        self.storage = create_storage(
            spark=spark,
            base_path=table_path,
            storage_backend=storage_backend,
        )

        logger.debug(
            f"Initialized LineageHistory with table_path: {table_path}, "
            f"backend: {storage_backend}"
        )

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific snapshot by ID.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            Snapshot record with all details, or None if not found

        Example:
            >>> snapshot = history.get_snapshot("abc123")
            >>> print(snapshot["pipeline_name"])
            >>> print(snapshot["captured_at"])
        """
        try:
            snapshot_data = self.storage.read_snapshot(snapshot_id)
            if snapshot_data is None:
                return None

            # Enrich with related data
            operations = self.storage.read_operations(snapshot_id)
            governance = self.storage.read_governance(snapshot_id)
            metrics = self.storage.read_metrics(snapshot_id)

            return {
                **snapshot_data,
                "operations": operations,
                "governance": governance,
                "metrics": metrics,
            }

        except Exception as e:
            logger.error(
                f"Failed to get snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def list_snapshots(
        self,
        pipeline_name: Optional[str] = None,
        environment: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        include_details: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        List snapshots with optional filters.

        Args:
            pipeline_name: Filter by pipeline name
            environment: Filter by environment (dev/staging/prod)
            start_date: Filter by start date (ISO format: YYYY-MM-DD)
            end_date: Filter by end date (ISO format: YYYY-MM-DD)
            limit: Maximum number of snapshots to return
            include_details: Include operations, governance, and metrics

        Returns:
            List of snapshot records (ordered by captured_at descending)

        Example:
            >>> # Get all production snapshots from last 30 days
            >>> snapshots = history.list_snapshots(
            ...     environment="production",
            ...     start_date="2024-10-01"
            ... )
            >>> print(f"Found {len(snapshots)} snapshots")
        """
        try:
            snapshots = self.storage.read_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )

            if include_details:
                # Enrich with related data
                for snapshot in snapshots:
                    snapshot_id = snapshot["snapshot_id"]
                    snapshot["operations"] = self.storage.read_operations(snapshot_id)
                    snapshot["governance"] = self.storage.read_governance(snapshot_id)
                    snapshot["metrics"] = self.storage.read_metrics(snapshot_id)

            return snapshots

        except Exception as e:
            logger.error(f"Failed to list snapshots: {str(e)}", exc_info=True)
            raise

    def get_latest_snapshot(
        self,
        pipeline_name: str,
        environment: str = "development",
        include_details: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the most recent snapshot for a pipeline in a specific environment.

        Args:
            pipeline_name: Name of the pipeline
            environment: Environment tag (dev/staging/prod)
            include_details: Include operations, governance, and metrics

        Returns:
            Most recent snapshot record, or None if not found

        Example:
            >>> snapshot = history.get_latest_snapshot(
            ...     pipeline_name="customer_analysis",
            ...     environment="production"
            ... )
            >>> if snapshot:
            ...     print(f"Latest snapshot: {snapshot['captured_at']}")
        """
        try:
            snapshots = self.list_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
                limit=1,
                include_details=include_details,
            )

            if snapshots:
                return snapshots[0]

            logger.info(
                f"No snapshots found for pipeline '{pipeline_name}' "
                f"in environment '{environment}'"
            )
            return None

        except Exception as e:
            logger.error(
                f"Failed to get latest snapshot for '{pipeline_name}': {str(e)}",
                exc_info=True
            )
            raise

    def get_pipeline_history(
        self,
        pipeline_name: str,
        environment: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get complete history for a specific pipeline.

        Args:
            pipeline_name: Name of the pipeline
            environment: Optional environment filter
            start_date: Optional start date (ISO format: YYYY-MM-DD)
            end_date: Optional end date (ISO format: YYYY-MM-DD)

        Returns:
            List of snapshots ordered by captured_at (newest first)

        Example:
            >>> history_records = history.get_pipeline_history(
            ...     pipeline_name="customer_analysis",
            ...     environment="production"
            ... )
            >>> print(f"Pipeline has {len(history_records)} historical snapshots")
        """
        return self.list_snapshots(
            pipeline_name=pipeline_name,
            environment=environment,
            start_date=start_date,
            end_date=end_date,
            include_details=False,
        )

    def get_lineage_graph(self, snapshot_id: str) -> Dict[str, Any]:
        """
        Get the lineage graph for a specific snapshot.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            Lineage graph as dictionary (deserialized JSON)

        Example:
            >>> graph = history.get_lineage_graph("abc123")
            >>> print(f"Graph has {len(graph['nodes'])} nodes")
            >>> print(f"Graph has {len(graph['edges'])} edges")
        """
        try:
            snapshot = self.storage.read_snapshot(snapshot_id)
            if snapshot is None:
                raise ValueError(f"Snapshot {snapshot_id} not found")

            graph_json = snapshot.get("lineage_graph")
            if not graph_json:
                return {"nodes": [], "edges": [], "metadata": {}}

            return json.loads(graph_json)

        except Exception as e:
            logger.error(
                f"Failed to get lineage graph for snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def get_summary_statistics(
        self,
        pipeline_name: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for lineage history.

        Args:
            pipeline_name: Optional pipeline filter
            environment: Optional environment filter

        Returns:
            Dictionary containing:
                - total_snapshots: Total number of snapshots
                - pipelines: List of unique pipeline names
                - environments: List of unique environments
                - date_range: Earliest and latest snapshot dates

        Example:
            >>> stats = history.get_summary_statistics()
            >>> print(f"Total snapshots: {stats['total_snapshots']}")
            >>> print(f"Pipelines: {stats['pipelines']}")
        """
        try:
            snapshots = self.list_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
            )

            if not snapshots:
                return {
                    "total_snapshots": 0,
                    "pipelines": [],
                    "environments": [],
                    "date_range": None,
                }

            # Extract statistics
            pipelines = set()
            environments = set()
            dates = []

            for snapshot in snapshots:
                pipelines.add(snapshot["pipeline_name"])
                environments.add(snapshot["environment"])
                dates.append(snapshot["captured_at"])

            return {
                "total_snapshots": len(snapshots),
                "pipelines": sorted(list(pipelines)),
                "environments": sorted(list(environments)),
                "date_range": {
                    "earliest": min(dates) if dates else None,
                    "latest": max(dates) if dates else None,
                },
            }

        except Exception as e:
            logger.error(
                f"Failed to get summary statistics: {str(e)}",
                exc_info=True
            )
            raise

    def compare_snapshots(
        self,
        snapshot_id_a: str,
        snapshot_id_b: str,
    ) -> Dict[str, Any]:
        """
        Compare two snapshots and identify differences.

        This is a basic comparison method retained for backward compatibility.
        For advanced comparison, use compare_snapshots_detailed().

        Args:
            snapshot_id_a: First snapshot ID (baseline)
            snapshot_id_b: Second snapshot ID (comparison)

        Returns:
            Dictionary containing:
                - snapshot_a: First snapshot metadata
                - snapshot_b: Second snapshot metadata
                - operation_count_diff: Difference in operation count
                - governance_count_diff: Difference in governance records

        Example:
            >>> diff = history.compare_snapshots("abc123", "def456")
            >>> print(f"Operation count changed by: {diff['operation_count_diff']}")
        """
        try:
            snapshot_a = self.get_snapshot(snapshot_id_a)
            snapshot_b = self.get_snapshot(snapshot_id_b)

            if snapshot_a is None:
                raise ValueError(f"Snapshot {snapshot_id_a} not found")
            if snapshot_b is None:
                raise ValueError(f"Snapshot {snapshot_id_b} not found")

            # Calculate basic differences
            # Convert Spark Row to dict if needed
            stats_a = snapshot_a.get("summary_stats", {})
            if hasattr(stats_a, "asDict"):
                stats_a = stats_a.asDict()
            stats_b = snapshot_b.get("summary_stats", {})
            if hasattr(stats_b, "asDict"):
                stats_b = stats_b.asDict()

            return {
                "snapshot_a": {
                    "snapshot_id": snapshot_id_a,
                    "pipeline_name": snapshot_a["pipeline_name"],
                    "environment": snapshot_a["environment"],
                    "version": snapshot_a.get("version", "unknown"),
                    "captured_at": snapshot_a["captured_at"],
                    "operation_count": stats_a.get("operation_count", 0),
                    "governance_count": stats_a.get("governance_operation_count", 0),
                },
                "snapshot_b": {
                    "snapshot_id": snapshot_id_b,
                    "pipeline_name": snapshot_b["pipeline_name"],
                    "environment": snapshot_b["environment"],
                    "version": snapshot_b.get("version", "unknown"),
                    "captured_at": snapshot_b["captured_at"],
                    "operation_count": stats_b.get("operation_count", 0),
                    "governance_count": stats_b.get("governance_operation_count", 0),
                },
                "operation_count_diff": (
                    stats_b.get("operation_count", 0) - stats_a.get("operation_count", 0)
                ),
                "governance_count_diff": (
                    stats_b.get("governance_operation_count", 0)
                    - stats_a.get("governance_operation_count", 0)
                ),
            }

        except Exception as e:
            logger.error(
                f"Failed to compare snapshots: {str(e)}",
                exc_info=True
            )
            raise

    def compare_snapshots_detailed(
        self,
        snapshot_id_a: str,
        snapshot_id_b: str,
        detect_drift: bool = True,
    ):
        """
        Perform detailed comparison between two snapshots.

        This is the advanced comparison method introduced in Phase 2.
        It provides comprehensive comparison with drift detection.

        Args:
            snapshot_id_a: First snapshot ID (baseline)
            snapshot_id_b: Second snapshot ID (comparison)
            detect_drift: Whether to run drift detection (default: True)

        Returns:
            LineageDiff object with complete comparison results

        Example:
            >>> from pyspark_storydoc.history.models import LineageDiff
            >>> diff = history.compare_snapshots_detailed("abc123", "def456")
            >>> print(f"Operations changed: {len(diff.get_changed_operations())}")
            >>> print(f"Has governance drift: {diff.has_governance_drift}")
        """
        from .comparator import LineageComparator
        from .drift_detector import DriftDetector

        try:
            # Get snapshots with full details
            snapshot_a = self.get_snapshot(snapshot_id_a)
            snapshot_b = self.get_snapshot(snapshot_id_b)

            if snapshot_a is None:
                raise ValueError(f"Snapshot {snapshot_id_a} not found")
            if snapshot_b is None:
                raise ValueError(f"Snapshot {snapshot_id_b} not found")

            # Perform comparison
            comparator = LineageComparator()
            lineage_diff = comparator.compare_snapshots(snapshot_a, snapshot_b)

            # Detect drift if requested
            if detect_drift:
                detector = DriftDetector()
                alerts = detector.detect_all_drift(snapshot_a, snapshot_b)

                # Flag drift in lineage_diff
                for alert in alerts:
                    if str(alert.alert_type) == "governance_drift":
                        lineage_diff.has_governance_drift = True
                    elif str(alert.alert_type) == "lineage_drift":
                        lineage_diff.has_lineage_drift = True

            return lineage_diff

        except Exception as e:
            logger.error(
                f"Failed to perform detailed comparison: {str(e)}",
                exc_info=True
            )
            raise

    def compare_environments(
        self,
        pipeline_name: str,
        env_a: str,
        env_b: str,
        detect_drift: bool = True,
    ):
        """
        Compare latest snapshots across two environments.

        This is useful for validating deployments (e.g., staging vs production).

        Args:
            pipeline_name: Name of the pipeline
            env_a: First environment (e.g., 'staging')
            env_b: Second environment (e.g., 'production')
            detect_drift: Whether to run drift detection (default: True)

        Returns:
            LineageDiff object with comparison results, or None if snapshots not found

        Example:
            >>> diff = history.compare_environments(
            ...     pipeline_name="credit_scoring",
            ...     env_a="staging",
            ...     env_b="production"
            ... )
            >>> if diff and diff.has_differences():
            ...     print("WARNING: Staging differs from production!")
        """
        try:
            # Get latest snapshots for each environment
            snapshot_a = self.get_latest_snapshot(
                pipeline_name=pipeline_name,
                environment=env_a,
                include_details=True,
            )

            snapshot_b = self.get_latest_snapshot(
                pipeline_name=pipeline_name,
                environment=env_b,
                include_details=True,
            )

            if snapshot_a is None:
                logger.warning(
                    f"No snapshot found for pipeline '{pipeline_name}' "
                    f"in environment '{env_a}'"
                )
                return None

            if snapshot_b is None:
                logger.warning(
                    f"No snapshot found for pipeline '{pipeline_name}' "
                    f"in environment '{env_b}'"
                )
                return None

            # Compare using detailed comparison
            return self.compare_snapshots_detailed(
                snapshot_id_a=snapshot_a["snapshot_id"],
                snapshot_id_b=snapshot_b["snapshot_id"],
                detect_drift=detect_drift,
            )

        except Exception as e:
            logger.error(
                f"Failed to compare environments: {str(e)}",
                exc_info=True
            )
            raise

    def detect_drift(
        self,
        pipeline_name: str,
        time_window_days: int = 30,
        environment: Optional[str] = None,
    ) -> List:
        """
        Detect drift for a pipeline over a time window.

        This method compares the latest snapshot with a snapshot from
        time_window_days ago to identify drift patterns.

        Args:
            pipeline_name: Name of the pipeline
            time_window_days: Number of days to look back (default: 30)
            environment: Optional environment filter

        Returns:
            List of DriftAlert objects

        Example:
            >>> alerts = history.detect_drift(
            ...     pipeline_name="credit_scoring",
            ...     time_window_days=30
            ... )
            >>> for alert in alerts:
            ...     if alert.severity in ["ERROR", "CRITICAL"]:
            ...         print(f"{alert.severity}: {alert.message}")
        """
        from datetime import datetime, timedelta
        from .drift_detector import DriftDetector

        try:
            # Get latest snapshot
            latest_snapshot = self.get_latest_snapshot(
                pipeline_name=pipeline_name,
                environment=environment,
                include_details=True,
            )

            if latest_snapshot is None:
                logger.warning(f"No snapshots found for pipeline '{pipeline_name}'")
                return []

            # Get snapshot from time_window_days ago
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")

            historical_snapshots = self.list_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
                end_date=cutoff_date_str,
                limit=1,
                include_details=True,
            )

            if not historical_snapshots:
                logger.info(
                    f"No historical snapshot found for '{pipeline_name}' "
                    f"from {time_window_days} days ago"
                )
                return []

            baseline_snapshot = historical_snapshots[0]

            # Detect drift
            detector = DriftDetector()
            alerts = detector.detect_all_drift(baseline_snapshot, latest_snapshot)

            logger.info(
                f"Drift detection complete: {len(alerts)} alerts generated "
                f"for '{pipeline_name}' over {time_window_days} days"
            )

            return alerts

        except Exception as e:
            logger.error(
                f"Failed to detect drift: {str(e)}",
                exc_info=True
            )
            raise

    def get_latest_comparison(
        self,
        pipeline_name: str,
        environment: str = "development",
    ):
        """
        Get the latest comparison report for a pipeline.

        This method compares the two most recent snapshots for a pipeline.

        Args:
            pipeline_name: Name of the pipeline
            environment: Environment to query (default: 'development')

        Returns:
            ComparisonReport object, or None if insufficient snapshots

        Example:
            >>> report = history.get_latest_comparison(
            ...     pipeline_name="credit_scoring",
            ...     environment="production"
            ... )
            >>> if report:
            ...     print(report.summary)
            ...     with open("report.md", "w") as f:
            ...         f.write(report.report_markdown)
        """
        from .comparison_reporter import ComparisonReporter
        from .drift_detector import DriftDetector

        try:
            # Get two most recent snapshots
            snapshots = self.list_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
                limit=2,
                include_details=True,
            )

            if len(snapshots) < 2:
                logger.warning(
                    f"Insufficient snapshots for comparison (found {len(snapshots)}, need 2)"
                )
                return None

            snapshot_b = snapshots[0]  # Most recent
            snapshot_a = snapshots[1]  # Second most recent

            # Perform detailed comparison
            lineage_diff = self.compare_snapshots_detailed(
                snapshot_id_a=snapshot_a["snapshot_id"],
                snapshot_id_b=snapshot_b["snapshot_id"],
                detect_drift=True,
            )

            # Detect drift for alerts
            detector = DriftDetector()
            drift_alerts = detector.detect_all_drift(snapshot_a, snapshot_b)

            # Generate report
            reporter = ComparisonReporter()
            report = reporter.generate_comparison_report(
                lineage_diff=lineage_diff,
                drift_alerts=drift_alerts,
                title=f"Latest Comparison: {pipeline_name} ({environment})",
            )

            return report

        except Exception as e:
            logger.error(
                f"Failed to get latest comparison: {str(e)}",
                exc_info=True
            )
            raise

    # Phase 3: Trend Analysis & Alerting Methods

    def get_metric_history(
        self,
        pipeline_name: str,
        metric_name: str,
        time_window_days: int,
        environment: Optional[str] = None,
    ):
        """
        Get metric history for trend analysis.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            time_window_days: Number of days to retrieve
            environment: Optional environment filter

        Returns:
            List of MetricPoint objects

        Example:
            >>> points = history.get_metric_history(
            ...     pipeline_name="customer_etl",
            ...     metric_name="row_count",
            ...     time_window_days=30
            ... )
        """
        from .trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer(self)
        return analyzer.get_metric_history(
            pipeline_name=pipeline_name,
            metric_name=metric_name,
            time_window_days=time_window_days,
            environment=environment,
        )

    def analyze_trend(
        self,
        pipeline_name: str,
        metric_name: str,
        time_window_days: int = 90,
        detect_anomalies: bool = True,
    ):
        """
        Analyze metric trend over time.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            time_window_days: Number of days to analyze (default: 90)
            detect_anomalies: Detect anomalies (default: True)

        Returns:
            TrendAnalysis object

        Example:
            >>> trend = history.analyze_trend(
            ...     pipeline_name="customer_etl",
            ...     metric_name="complexity_score",
            ...     time_window_days=30
            ... )
            >>> print(f"Trend: {trend.trend_direction}")
            >>> print(f"Growth: {trend.growth_rate_percent:.1f}%")
        """
        from .trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer(self)
        return analyzer.analyze_metric_trend(
            pipeline_name=pipeline_name,
            metric_name=metric_name,
            time_window_days=time_window_days,
            detect_anomalies=detect_anomalies,
        )

    def detect_anomalies(
        self,
        pipeline_name: str,
        metric_name: str,
        threshold_std_devs: float = 2.0,
        time_window_days: int = 90,
    ):
        """
        Detect statistical anomalies in metric data.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            threshold_std_devs: Z-score threshold (default: 2.0)
            time_window_days: Time window (default: 90 days)

        Returns:
            List of Anomaly objects

        Example:
            >>> anomalies = history.detect_anomalies(
            ...     pipeline_name="customer_etl",
            ...     metric_name="execution_time",
            ...     threshold_std_devs=2.5
            ... )
            >>> print(f"Found {len(anomalies)} anomalies")
        """
        from .trend_analyzer import TrendAnalyzer

        analyzer = TrendAnalyzer(self)
        return analyzer.detect_anomalies(
            pipeline_name=pipeline_name,
            metric_name=metric_name,
            threshold_std_devs=threshold_std_devs,
            time_window_days=time_window_days,
        )

    def evaluate_rules(
        self,
        rules_config_path: str,
        pipeline_name: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        """
        Evaluate alert rules from configuration file.

        Args:
            rules_config_path: Path to alert rules YAML file
            pipeline_name: Optional pipeline filter
            environment: Optional environment filter

        Returns:
            Dictionary with alert evaluation results

        Example:
            >>> results = history.evaluate_rules(
            ...     rules_config_path="alert_rules.yaml",
            ...     pipeline_name="customer_etl"
            ... )
            >>> print(f"Generated {results['total_alerts']} alerts")
        """
        from .analyzer import HistoryAnalyzer

        analyzer = HistoryAnalyzer(self)
        return analyzer.evaluate_alert_rules(
            rules_config=rules_config_path,
            pipeline_name=pipeline_name,
            environment=environment,
        )
