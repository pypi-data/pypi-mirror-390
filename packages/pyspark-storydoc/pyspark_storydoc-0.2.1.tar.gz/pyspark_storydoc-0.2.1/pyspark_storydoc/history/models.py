"""
Data models for lineage comparison and drift detection.

This module defines dataclass models used throughout Phase 2:
- LineageDiff: Complete comparison between two snapshots
- GraphDiff: Graph structure differences
- OperationDiff: Single operation changes
- GovernanceDiff: Governance metadata changes
- ExpressionDiff: Expression logic changes
- DriftAlert: Drift detection alert
- ComparisonReport: Formatted comparison report

All models use Python 3.10+ features (dataclasses, match/case support).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AlertSeverity(Enum):
    """Alert severity levels for drift detection."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value

    @property
    def priority(self) -> int:
        """Priority level for sorting (higher = more severe)."""
        return {
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }[self.value]


class AlertType(Enum):
    """Types of alerts that can be generated."""
    GOVERNANCE_DRIFT = "governance_drift"
    LINEAGE_DRIFT = "lineage_drift"
    COMPLEXITY_GROWTH = "complexity_growth"
    SCHEMA_CHANGE = "schema_change"
    PERFORMANCE_REGRESSION = "performance_regression"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    MISSING_GOVERNANCE = "missing_governance"
    APPROVAL_EXPIRED = "approval_expired"

    def __str__(self) -> str:
        return self.value


class ChangeType(Enum):
    """Types of changes detected in comparison."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"

    def __str__(self) -> str:
        return self.value


@dataclass
class OperationDiff:
    """
    Differences for a single operation between snapshots.

    Attributes:
        operation_id: Unique identifier for the operation
        change_type: Type of change (added/removed/modified/unchanged)
        business_concept: Business concept this operation belongs to
        operation_type: Type of operation (filter/join/aggregate/etc.)
        description_before: Description in snapshot A
        description_after: Description in snapshot B
        expression_before: Expression in snapshot A
        expression_after: Expression in snapshot B
        expression_similarity: Similarity score (0.0 to 1.0)
        governance_changed: Whether governance metadata changed
        metrics_before: Metrics from snapshot A
        metrics_after: Metrics from snapshot B
        metadata: Additional comparison metadata
    """
    operation_id: str
    change_type: ChangeType
    business_concept: Optional[str] = None
    operation_type: Optional[str] = None
    description_before: Optional[str] = None
    description_after: Optional[str] = None
    expression_before: Optional[str] = None
    expression_after: Optional[str] = None
    expression_similarity: float = 1.0
    governance_changed: bool = False
    metrics_before: Dict[str, Any] = field(default_factory=dict)
    metrics_after: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_significant_change(self, threshold: float = 0.95) -> bool:
        """
        Check if the operation has a significant change.

        Args:
            threshold: Similarity threshold (below = significant change)

        Returns:
            True if change is significant
        """
        if self.change_type in (ChangeType.ADDED, ChangeType.REMOVED):
            return True

        if self.expression_similarity < threshold:
            return True

        if self.governance_changed:
            return True

        return False

    def get_summary(self) -> str:
        """Get a one-line summary of the change."""
        if self.change_type == ChangeType.ADDED:
            return f"Added: {self.operation_id}"
        elif self.change_type == ChangeType.REMOVED:
            return f"Removed: {self.operation_id}"
        elif self.change_type == ChangeType.MODIFIED:
            changes = []
            if self.expression_similarity < 0.95:
                changes.append(f"expression ({self.expression_similarity:.1%} similar)")
            if self.governance_changed:
                changes.append("governance")
            return f"Modified: {self.operation_id} ({', '.join(changes)})"
        else:
            return f"Unchanged: {self.operation_id}"


@dataclass
class GovernanceDiff:
    """
    Governance metadata differences.

    Attributes:
        operation_id: Operation this governance diff applies to
        business_justification_changed: Whether business justification changed
        pii_processing_changed: Whether PII processing status changed
        risk_assessment_changed: Whether risk assessment changed
        approval_status_changed: Whether approval status changed
        data_classification_changed: Whether data classification changed
        fields_before: Complete governance fields from snapshot A
        fields_after: Complete governance fields from snapshot B
        changed_fields: List of field names that changed
    """
    operation_id: str
    business_justification_changed: bool = False
    pii_processing_changed: bool = False
    risk_assessment_changed: bool = False
    approval_status_changed: bool = False
    data_classification_changed: bool = False
    fields_before: Dict[str, Any] = field(default_factory=dict)
    fields_after: Dict[str, Any] = field(default_factory=dict)
    changed_fields: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        """Check if any governance fields changed."""
        return len(self.changed_fields) > 0

    def get_summary(self) -> str:
        """Get a one-line summary of governance changes."""
        if not self.has_changes():
            return "No governance changes"

        return f"Changed fields: {', '.join(self.changed_fields)}"


@dataclass
class ExpressionDiff:
    """
    Expression logic differences.

    Attributes:
        operation_id: Operation this expression diff applies to
        expression_before: Expression from snapshot A
        expression_after: Expression from snapshot B
        similarity_score: Similarity score (0.0 to 1.0)
        structural_similarity: Structural/AST similarity (0.0 to 1.0)
        tokens_added: Tokens present in B but not A
        tokens_removed: Tokens present in A but not B
        tokens_common: Tokens present in both
    """
    operation_id: str
    expression_before: str
    expression_after: str
    similarity_score: float
    structural_similarity: float = 0.0
    tokens_added: List[str] = field(default_factory=list)
    tokens_removed: List[str] = field(default_factory=list)
    tokens_common: List[str] = field(default_factory=list)

    def is_significant_change(self, threshold: float = 0.95) -> bool:
        """Check if the expression change is significant."""
        return self.similarity_score < threshold

    def get_summary(self) -> str:
        """Get a one-line summary of expression changes."""
        if self.similarity_score >= 0.95:
            return "Minor changes"
        elif self.similarity_score >= 0.8:
            return "Moderate changes"
        else:
            return "Major rewrite"


@dataclass
class GraphDiff:
    """
    Graph structure differences between two snapshots.

    Attributes:
        operations_added: List of operation IDs added in snapshot B
        operations_removed: List of operation IDs removed from snapshot A
        operations_modified: List of operation IDs present in both but changed
        operations_unchanged: List of operation IDs present in both and unchanged
        edges_added: List of edges (source -> target) added in snapshot B
        edges_removed: List of edges removed from snapshot A
        business_concepts_added: List of business concepts added in snapshot B
        business_concepts_removed: List of business concepts removed from snapshot A
    """
    operations_added: List[str] = field(default_factory=list)
    operations_removed: List[str] = field(default_factory=list)
    operations_modified: List[str] = field(default_factory=list)
    operations_unchanged: List[str] = field(default_factory=list)
    edges_added: List[tuple[str, str]] = field(default_factory=list)
    edges_removed: List[tuple[str, str]] = field(default_factory=list)
    business_concepts_added: List[str] = field(default_factory=list)
    business_concepts_removed: List[str] = field(default_factory=list)

    def has_structural_changes(self) -> bool:
        """Check if there are any structural changes to the graph."""
        return (
            len(self.operations_added) > 0
            or len(self.operations_removed) > 0
            or len(self.operations_modified) > 0
            or len(self.edges_added) > 0
            or len(self.edges_removed) > 0
        )

    def get_summary(self) -> str:
        """Get a one-line summary of graph changes."""
        parts = []
        if self.operations_added:
            parts.append(f"+{len(self.operations_added)} ops")
        if self.operations_removed:
            parts.append(f"-{len(self.operations_removed)} ops")
        if self.operations_modified:
            parts.append(f"~{len(self.operations_modified)} ops")

        if not parts:
            return "No structural changes"

        return ", ".join(parts)


@dataclass
class LineageDiff:
    """
    Complete comparison result between two lineage snapshots.

    Attributes:
        snapshot_id_a: ID of first snapshot (baseline)
        snapshot_id_b: ID of second snapshot (comparison)
        snapshot_a_metadata: Metadata for snapshot A
        snapshot_b_metadata: Metadata for snapshot B
        compared_at: When comparison was performed
        graph_diff: Graph structure differences
        operation_diffs: List of operation-level differences
        governance_diffs: List of governance metadata differences
        expression_diffs: List of expression logic differences
        has_governance_drift: Whether governance drift was detected
        has_lineage_drift: Whether lineage drift was detected
        summary_stats: Summary statistics for the comparison
        metadata: Additional comparison metadata
    """
    snapshot_id_a: str
    snapshot_id_b: str
    snapshot_a_metadata: Dict[str, Any]
    snapshot_b_metadata: Dict[str, Any]
    compared_at: datetime
    graph_diff: GraphDiff
    operation_diffs: List[OperationDiff] = field(default_factory=list)
    governance_diffs: List[GovernanceDiff] = field(default_factory=list)
    expression_diffs: List[ExpressionDiff] = field(default_factory=list)
    has_governance_drift: bool = False
    has_lineage_drift: bool = False
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_differences(self) -> bool:
        """Check if there are any differences between snapshots."""
        return (
            self.graph_diff.has_structural_changes()
            or len([d for d in self.operation_diffs if d.has_significant_change()]) > 0
            or len([d for d in self.governance_diffs if d.has_changes()]) > 0
        )

    def get_changed_operations(self) -> List[OperationDiff]:
        """Get list of operations with significant changes."""
        return [
            diff for diff in self.operation_diffs
            if diff.has_significant_change()
        ]

    def get_summary(self) -> str:
        """Get a one-line summary of all differences."""
        if not self.has_differences():
            return "No differences detected"

        parts = []
        parts.append(self.graph_diff.get_summary())

        if self.has_governance_drift:
            parts.append("governance drift detected")

        if self.has_lineage_drift:
            parts.append("lineage drift detected")

        return "; ".join(parts)


@dataclass
class DriftAlert:
    """
    Alert generated by drift detection.

    Attributes:
        alert_id: Unique identifier for this alert
        alert_type: Type of alert (governance_drift/lineage_drift/etc.)
        severity: Alert severity level
        pipeline_name: Pipeline this alert applies to
        environment: Environment this alert applies to
        operation_id: Operation this alert relates to (if applicable)
        title: Short alert title
        message: Detailed alert message
        recommendation: Actionable recommendation
        detected_at: When the alert was generated
        snapshot_id_a: First snapshot involved in detection
        snapshot_id_b: Second snapshot involved in detection
        metadata: Additional alert metadata
        fingerprint: Hash for deduplication
    """
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    pipeline_name: str
    environment: str
    title: str
    message: str
    recommendation: str
    detected_at: datetime
    operation_id: Optional[str] = None
    snapshot_id_a: Optional[str] = None
    snapshot_id_b: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    fingerprint: Optional[str] = None

    def __post_init__(self):
        """Generate fingerprint after initialization if not provided."""
        if self.fingerprint is None:
            self.fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> str:
        """Generate a fingerprint for deduplication."""
        import hashlib

        # Create fingerprint from key attributes
        key_parts = [
            str(self.alert_type),
            self.pipeline_name,
            self.environment,
            self.operation_id or "",
            self.title,
        ]

        fingerprint_str = "|".join(key_parts)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for serialization."""
        return {
            "alert_id": self.alert_id,
            "alert_type": str(self.alert_type),
            "severity": str(self.severity),
            "pipeline_name": self.pipeline_name,
            "environment": self.environment,
            "operation_id": self.operation_id,
            "title": self.title,
            "message": self.message,
            "recommendation": self.recommendation,
            "detected_at": self.detected_at.isoformat(),
            "snapshot_id_a": self.snapshot_id_a,
            "snapshot_id_b": self.snapshot_id_b,
            "metadata": self.metadata,
            "fingerprint": self.fingerprint,
        }


@dataclass
class ComparisonReport:
    """
    Formatted comparison report.

    Attributes:
        report_id: Unique identifier for this report
        title: Report title
        generated_at: When report was generated
        lineage_diff: The comparison result
        drift_alerts: List of drift alerts generated
        report_markdown: Formatted markdown report
        report_json: JSON export of comparison data
        summary: Executive summary
        recommendations: List of actionable recommendations
        metadata: Additional report metadata
    """
    report_id: str
    title: str
    generated_at: datetime
    lineage_diff: LineageDiff
    drift_alerts: List[DriftAlert] = field(default_factory=list)
    report_markdown: str = ""
    report_json: str = ""
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_critical_alerts(self) -> bool:
        """Check if report has any critical alerts."""
        return any(
            alert.severity == AlertSeverity.CRITICAL
            for alert in self.drift_alerts
        )

    def has_error_alerts(self) -> bool:
        """Check if report has any error or critical alerts."""
        return any(
            alert.severity in (AlertSeverity.ERROR, AlertSeverity.CRITICAL)
            for alert in self.drift_alerts
        )

    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[DriftAlert]:
        """Get all alerts of a specific severity level."""
        return [
            alert for alert in self.drift_alerts
            if alert.severity == severity
        ]

    def get_sorted_alerts(self) -> List[DriftAlert]:
        """Get alerts sorted by severity (critical first)."""
        return sorted(
            self.drift_alerts,
            key=lambda a: a.severity.priority,
            reverse=True
        )


@dataclass
class DriftDetectionConfig:
    """
    Configuration for drift detection.

    Attributes:
        expression_similarity_threshold: Threshold for expression changes (default: 0.95)
        ignore_whitespace: Ignore whitespace in expression comparison (default: True)
        ignore_comments: Ignore comments in expression comparison (default: True)
        governance_fields_to_check: List of governance fields to monitor
        alert_on_missing_governance: Alert when governance is missing (default: True)
        alert_on_approval_expiry: Alert when approvals expire (default: True)
        approval_expiry_days: Days until approval expires (default: 365)
        complexity_growth_threshold: Percentage growth to trigger alert (default: 0.3)
        performance_regression_threshold: Percentage slowdown to trigger alert (default: 0.5)
        time_window_days: Days to look back for drift detection (default: 30)
    """
    expression_similarity_threshold: float = 0.95
    ignore_whitespace: bool = True
    ignore_comments: bool = True
    governance_fields_to_check: List[str] = field(default_factory=lambda: [
        "business_justification",
        "pii_processing",
        "data_classification",
        "approval_status",
        "risks",
    ])
    alert_on_missing_governance: bool = True
    alert_on_approval_expiry: bool = True
    approval_expiry_days: int = 365
    complexity_growth_threshold: float = 0.3
    performance_regression_threshold: float = 0.5
    time_window_days: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "expression_similarity_threshold": self.expression_similarity_threshold,
            "ignore_whitespace": self.ignore_whitespace,
            "ignore_comments": self.ignore_comments,
            "governance_fields_to_check": self.governance_fields_to_check,
            "alert_on_missing_governance": self.alert_on_missing_governance,
            "alert_on_approval_expiry": self.alert_on_approval_expiry,
            "approval_expiry_days": self.approval_expiry_days,
            "complexity_growth_threshold": self.complexity_growth_threshold,
            "performance_regression_threshold": self.performance_regression_threshold,
            "time_window_days": self.time_window_days,
        }


# Phase 3: Trend Analysis & Alerting Models


@dataclass
class MetricPoint:
    """
    Single metric value at a point in time.

    Attributes:
        timestamp: When the metric was captured
        value: Numeric metric value
        snapshot_id: Snapshot this metric belongs to
        metadata: Additional metric metadata
    """
    timestamp: datetime
    value: float
    snapshot_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "snapshot_id": self.snapshot_id,
            "metadata": self.metadata,
        }


@dataclass
class Anomaly:
    """
    Statistical anomaly detected in metric data.

    Attributes:
        timestamp: When the anomaly occurred
        value: Actual metric value
        expected_value: Expected value based on trend
        deviation_std_devs: Number of standard deviations from mean
        severity: Alert severity based on deviation magnitude
        metric_name: Name of the metric
        snapshot_id: Snapshot where anomaly was detected
    """
    timestamp: datetime
    value: float
    expected_value: float
    deviation_std_devs: float
    severity: AlertSeverity
    metric_name: str
    snapshot_id: str

    def __post_init__(self):
        """Calculate severity based on deviation if not set."""
        if self.severity is None:
            # Auto-assign severity based on deviation
            abs_dev = abs(self.deviation_std_devs)
            if abs_dev >= 3.0:
                self.severity = AlertSeverity.CRITICAL
            elif abs_dev >= 2.5:
                self.severity = AlertSeverity.ERROR
            elif abs_dev >= 2.0:
                self.severity = AlertSeverity.WARNING
            else:
                self.severity = AlertSeverity.INFO

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "expected_value": self.expected_value,
            "deviation_std_devs": self.deviation_std_devs,
            "severity": str(self.severity),
            "metric_name": self.metric_name,
            "snapshot_id": self.snapshot_id,
        }


@dataclass
class TrendAnalysis:
    """
    Trend analysis result for a metric over time.

    Attributes:
        metric_name: Name of the metric being analyzed
        pipeline_name: Pipeline this analysis applies to
        time_window_days: Number of days analyzed
        data_points: List of metric values over time
        trend_direction: Overall trend direction (increasing/decreasing/stable)
        growth_rate_percent: Percentage growth rate over period
        mean: Average value over period
        std_dev: Standard deviation
        min_value: Minimum value observed
        max_value: Maximum value observed
        anomalies: List of detected anomalies
        confidence: Confidence score for trend direction (0.0-1.0)
        slope: Linear regression slope
        r_squared: R-squared value for trend fit
    """
    metric_name: str
    pipeline_name: str
    time_window_days: int
    data_points: List[MetricPoint]
    trend_direction: str
    growth_rate_percent: float
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    anomalies: List[Anomaly] = field(default_factory=list)
    confidence: float = 0.0
    slope: float = 0.0
    r_squared: float = 0.0

    def has_anomalies(self) -> bool:
        """Check if any anomalies were detected."""
        return len(self.anomalies) > 0

    def get_critical_anomalies(self) -> List[Anomaly]:
        """Get list of critical anomalies."""
        return [
            a for a in self.anomalies
            if a.severity == AlertSeverity.CRITICAL
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "pipeline_name": self.pipeline_name,
            "time_window_days": self.time_window_days,
            "data_points": [dp.to_dict() for dp in self.data_points],
            "trend_direction": self.trend_direction,
            "growth_rate_percent": self.growth_rate_percent,
            "mean": self.mean,
            "std_dev": self.std_dev,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "anomalies": [a.to_dict() for a in self.anomalies],
            "confidence": self.confidence,
            "slope": self.slope,
            "r_squared": self.r_squared,
        }


@dataclass
class AlertRule:
    """
    Configuration for an alert rule.

    Attributes:
        name: Human-readable rule name
        metric_name: Metric to monitor
        rule_type: Type of rule (threshold/trend/anomaly/composite)
        threshold: Threshold value (for threshold rules)
        operator: Comparison operator (greater_than/less_than/equals)
        trend_direction: Expected trend direction (for trend rules)
        growth_rate_threshold: Growth rate threshold (for trend rules)
        severity: Alert severity to generate
        notifiers: List of notifier names to trigger
        enabled: Whether rule is active
        cooldown_minutes: Minimum time between alerts (deduplication)
        metadata: Additional rule configuration
    """
    name: str
    metric_name: str
    rule_type: str
    severity: AlertSeverity
    notifiers: List[str]
    threshold: Optional[float] = None
    operator: Optional[str] = None
    trend_direction: Optional[str] = None
    growth_rate_threshold: Optional[float] = None
    enabled: bool = True
    cooldown_minutes: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)

    def matches_condition(self, value: Any, context: Dict[str, Any]) -> bool:
        """
        Check if rule condition is met.

        Args:
            value: Current metric value or trend analysis
            context: Additional context for evaluation

        Returns:
            True if rule condition is met
        """
        if not self.enabled:
            return False

        if self.rule_type == "threshold":
            return self._check_threshold(value)
        elif self.rule_type == "trend":
            return self._check_trend(value, context)
        elif self.rule_type == "anomaly":
            return self._check_anomaly(context)

        return False

    def _check_threshold(self, value: float) -> bool:
        """Check threshold rule condition."""
        if self.threshold is None or self.operator is None:
            return False

        if self.operator == "greater_than":
            return value > self.threshold
        elif self.operator == "less_than":
            return value < self.threshold
        elif self.operator == "equals":
            return abs(value - self.threshold) < 0.0001
        elif self.operator == "greater_equal":
            return value >= self.threshold
        elif self.operator == "less_equal":
            return value <= self.threshold

        return False

    def _check_trend(self, trend_analysis: Any, context: Dict[str, Any]) -> bool:
        """Check trend rule condition."""
        if not hasattr(trend_analysis, 'trend_direction'):
            return False

        if self.trend_direction and trend_analysis.trend_direction != self.trend_direction:
            return False

        if self.growth_rate_threshold is not None:
            if abs(trend_analysis.growth_rate_percent) < self.growth_rate_threshold:
                return False

        return True

    def _check_anomaly(self, context: Dict[str, Any]) -> bool:
        """Check anomaly rule condition."""
        anomalies = context.get('anomalies', [])
        return len(anomalies) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "metric_name": self.metric_name,
            "rule_type": self.rule_type,
            "threshold": self.threshold,
            "operator": self.operator,
            "trend_direction": self.trend_direction,
            "growth_rate_threshold": self.growth_rate_threshold,
            "severity": str(self.severity),
            "notifiers": self.notifiers,
            "enabled": self.enabled,
            "cooldown_minutes": self.cooldown_minutes,
            "metadata": self.metadata,
        }


@dataclass
class TrendReport:
    """
    Comprehensive trend analysis report for a pipeline.

    Attributes:
        pipeline_name: Pipeline this report covers
        generated_at: When report was generated
        lookback_days: Number of days analyzed
        metric_analyses: List of metric trend analyses
        alerts_triggered: List of alerts generated
        summary_stats: Summary statistics across all metrics
        visualizations: Dictionary of ASCII charts by metric name
        recommendations: List of actionable recommendations
    """
    pipeline_name: str
    generated_at: datetime
    lookback_days: int
    metric_analyses: List[TrendAnalysis]
    alerts_triggered: List[DriftAlert] = field(default_factory=list)
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    visualizations: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def has_critical_issues(self) -> bool:
        """Check if report contains critical alerts or anomalies."""
        # Check for critical alerts
        critical_alerts = [
            a for a in self.alerts_triggered
            if a.severity == AlertSeverity.CRITICAL
        ]
        if critical_alerts:
            return True

        # Check for critical anomalies
        for analysis in self.metric_analyses:
            if analysis.get_critical_anomalies():
                return True

        return False

    def get_metrics_with_issues(self) -> List[str]:
        """Get list of metrics with alerts or anomalies."""
        metrics = set()

        for alert in self.alerts_triggered:
            if alert.metadata.get('metric_name'):
                metrics.add(alert.metadata['metric_name'])

        for analysis in self.metric_analyses:
            if analysis.has_anomalies():
                metrics.add(analysis.metric_name)

        return sorted(list(metrics))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pipeline_name": self.pipeline_name,
            "generated_at": self.generated_at.isoformat(),
            "lookback_days": self.lookback_days,
            "metric_analyses": [ma.to_dict() for ma in self.metric_analyses],
            "alerts_triggered": [a.to_dict() for a in self.alerts_triggered],
            "summary_stats": self.summary_stats,
            "visualizations": self.visualizations,
            "recommendations": self.recommendations,
        }
