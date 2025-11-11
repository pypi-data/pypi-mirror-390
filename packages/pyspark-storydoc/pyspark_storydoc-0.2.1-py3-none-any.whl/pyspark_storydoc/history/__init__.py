"""
Lineage and Governance Change Tracking Over Time.

This module provides temporal tracking capabilities for PySpark StoryDoc,
enabling organizations to:
- Track how data pipelines evolve over time
- Detect governance drift (lineage changes without governance updates)
- Monitor data quality trends
- Compare lineage across environments (dev/staging/prod)
- Maintain compliance audit trails

Key Components:
    - enable_history_tracking: Context manager for automatic history capture
    - LineageHistory: Query interface for historical snapshots
    - SnapshotManager: Core snapshot capture and serialization
    - DeltaLakeStorage: Persistent storage using Delta Lake tables

Example:
    >>> from pyspark_storydoc import businessConcept
    >>> from pyspark_storydoc.history import enable_history_tracking, LineageHistory
    >>>
    >>> # Capture lineage history
    >>> with enable_history_tracking(
    ...     table_path="./lineage_history",
    ...     environment="development",
    ...     pipeline_name="customer_analysis"
    ... ):
    ...     @businessConcept("Filter Active Customers")
    ...     def filter_active(df):
    ...         return df.filter(col("status") == "active")
    ...
    ...     result = filter_active(customers_df)
    >>>
    >>> # Query history
    >>> history = LineageHistory(table_path="./lineage_history")
    >>> snapshots = history.list_snapshots(pipeline_name="customer_analysis")
    >>> print(f"Found {len(snapshots)} historical snapshots")
"""

from .alert_rules import (
    AlertRulesEngine,
    AnomalyRule,
    BaseAlertRule,
    CompositeRule,
    ThresholdRule,
    TrendRule,
)
from .alerts import AlertAggregator, AlertDeduplicator, AlertFormatter
from .analyzer import HistoryAnalyzer
from .comparator import LineageComparator
from .comparison_reporter import ComparisonReporter
from .context_manager import enable_history_tracking
from .drift_detector import DriftDetector
from .governance_alert_reporter import GovernanceAlertReporter
from .models import (
    AlertRule,
    AlertSeverity,
    AlertType,
    Anomaly,
    ChangeType,
    ComparisonReport,
    DriftAlert,
    DriftDetectionConfig,
    ExpressionDiff,
    GovernanceDiff,
    GraphDiff,
    LineageDiff,
    MetricPoint,
    OperationDiff,
    TrendAnalysis,
    TrendReport,
)
from .notifiers import (
    ConsoleNotifier,
    EmailNotifier,
    JiraNotifier,
    Notifier,
    NotifierFactory,
    SlackNotifier,
    WebhookNotifier,
)
from .parquet_storage import ParquetStorage
from .query import LineageHistory
from .snapshot_manager import SnapshotManager
from .storage import DeltaLakeStorage
from .storage_factory import (
    create_storage,
    detect_delta_lake_available,
    get_backend_info,
    print_backend_comparison,
)
from .trend_analyzer import TrendAnalyzer
from .trend_visualizer import TrendVisualizer

__all__ = [
    # Phase 1: History Tracking
    'enable_history_tracking',
    'LineageHistory',
    'SnapshotManager',
    'DeltaLakeStorage',
    'ParquetStorage',
    'create_storage',
    'detect_delta_lake_available',
    'get_backend_info',
    'print_backend_comparison',
    # Phase 2: Comparison and Drift Detection
    'LineageComparator',
    'DriftDetector',
    'GovernanceAlertReporter',
    'ComparisonReporter',
    'AlertFormatter',
    'AlertDeduplicator',
    'AlertAggregator',
    # Phase 3: Trend Analysis & Alerting
    'TrendAnalyzer',
    'TrendVisualizer',
    'HistoryAnalyzer',
    'AlertRulesEngine',
    'BaseAlertRule',
    'ThresholdRule',
    'TrendRule',
    'AnomalyRule',
    'CompositeRule',
    'Notifier',
    'ConsoleNotifier',
    'SlackNotifier',
    'EmailNotifier',
    'JiraNotifier',
    'WebhookNotifier',
    'NotifierFactory',
    # Data Models
    'LineageDiff',
    'GraphDiff',
    'OperationDiff',
    'GovernanceDiff',
    'ExpressionDiff',
    'DriftAlert',
    'ComparisonReport',
    'DriftDetectionConfig',
    'AlertSeverity',
    'AlertType',
    'ChangeType',
    # Phase 3 Models
    'MetricPoint',
    'TrendAnalysis',
    'Anomaly',
    'AlertRule',
    'TrendReport',
]
