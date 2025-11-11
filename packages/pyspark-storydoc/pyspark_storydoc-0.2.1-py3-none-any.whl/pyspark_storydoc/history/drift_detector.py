"""
Drift detector for identifying governance and lineage drift.

This module provides the DriftDetector class which:
- Detects when lineage changes without governance updates (governance review needed)
- Detects when governance changes without lineage updates (documentation audit)
- Applies configurable drift detection rules
- Generates drift alerts with actionable recommendations

The drift detector uses the LineageComparator to identify changes, then applies
business rules to determine if drift has occurred.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .comparator import LineageComparator
from .models import (
    AlertSeverity,
    AlertType,
    ChangeType,
    DriftAlert,
    DriftDetectionConfig,
    LineageDiff,
)

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects drift between lineage and governance metadata.

    This class identifies situations where:
    1. Lineage changed but governance didn't (governance drift)
    2. Governance changed but lineage didn't (documentation audit)
    3. Complexity grew significantly (refactoring candidate)
    4. Performance regressed (optimization needed)
    5. Missing governance metadata (compliance gap)

    Example:
        >>> detector = DriftDetector()
        >>> alerts = detector.detect_governance_drift(snapshot_a, snapshot_b)
        >>> for alert in alerts:
        ...     if alert.severity == AlertSeverity.CRITICAL:
        ...         print(f"CRITICAL: {alert.message}")
    """

    def __init__(
        self,
        config: Optional[DriftDetectionConfig] = None,
        comparator: Optional[LineageComparator] = None,
    ):
        """
        Initialize drift detector.

        Args:
            config: Drift detection configuration (default: default config)
            comparator: LineageComparator instance (default: new instance)
        """
        self.config = config or DriftDetectionConfig()
        self.comparator = comparator or LineageComparator(
            similarity_threshold=self.config.expression_similarity_threshold,
            ignore_whitespace=self.config.ignore_whitespace,
            ignore_comments=self.config.ignore_comments,
        )

        logger.debug("Initialized DriftDetector")

    def detect_governance_drift(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect governance drift between two snapshots.

        Governance drift occurs when:
        - Lineage changed but governance metadata did not update
        - This indicates governance documentation is out of sync with reality

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            List of DriftAlert objects for governance drift issues

        Example:
            >>> alerts = detector.detect_governance_drift(old_snap, new_snap)
            >>> critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
            >>> print(f"Found {len(critical_alerts)} critical governance drift issues")
        """
        logger.info("Detecting governance drift")

        alerts = []

        # Compare snapshots
        diff = self.comparator.compare_snapshots(snapshot_a, snapshot_b)

        # Check each modified operation for governance drift
        for op_diff in diff.operation_diffs:
            if op_diff.change_type != ChangeType.MODIFIED:
                continue

            # Lineage changed?
            lineage_changed = op_diff.expression_similarity < self.config.expression_similarity_threshold

            # Governance changed?
            governance_changed = op_diff.governance_changed

            # Governance drift: lineage changed but governance didn't
            if lineage_changed and not governance_changed:
                alert = self._create_governance_drift_alert(
                    snapshot_a, snapshot_b, op_diff
                )
                alerts.append(alert)

        logger.info(f"Detected {len(alerts)} governance drift alerts")

        return alerts

    def detect_lineage_drift(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect lineage drift between two snapshots.

        Lineage drift occurs when:
        - Governance metadata changed but lineage did not update
        - This indicates documentation updates without code changes (documentation audit needed)

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            List of DriftAlert objects for lineage drift issues

        Example:
            >>> alerts = detector.detect_lineage_drift(old_snap, new_snap)
            >>> for alert in alerts:
            ...     print(f"{alert.severity}: {alert.title}")
        """
        logger.info("Detecting lineage drift")

        alerts = []

        # Compare snapshots
        diff = self.comparator.compare_snapshots(snapshot_a, snapshot_b)

        # Check governance diffs for lineage drift
        for gov_diff in diff.governance_diffs:
            # Find corresponding operation diff
            op_diff = next(
                (od for od in diff.operation_diffs if od.operation_id == gov_diff.operation_id),
                None
            )

            if not op_diff:
                continue

            # Lineage changed?
            lineage_changed = op_diff.expression_similarity < self.config.expression_similarity_threshold

            # Governance changed?
            governance_changed = gov_diff.has_changes()

            # Lineage drift: governance changed but lineage didn't
            if governance_changed and not lineage_changed:
                alert = self._create_lineage_drift_alert(
                    snapshot_a, snapshot_b, op_diff, gov_diff
                )
                alerts.append(alert)

        logger.info(f"Detected {len(alerts)} lineage drift alerts")

        return alerts

    def detect_complexity_growth(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect significant complexity growth between snapshots.

        Complexity growth indicates:
        - Pipeline becoming more complex over time
        - Potential technical debt accumulation
        - Refactoring candidate

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            List of DriftAlert objects for complexity growth

        Example:
            >>> alerts = detector.detect_complexity_growth(old_snap, new_snap)
            >>> for alert in alerts:
            ...     print(f"Complexity grew: {alert.message}")
        """
        logger.info("Detecting complexity growth")

        alerts = []

        # Get operation counts
        stats_a = snapshot_a.get("summary_stats", {})
        stats_b = snapshot_b.get("summary_stats", {})

        op_count_a = stats_a.get("operation_count", 0)
        op_count_b = stats_b.get("operation_count", 0)

        if op_count_a == 0:
            return alerts

        # Calculate growth rate
        growth_rate = (op_count_b - op_count_a) / op_count_a

        # Check threshold
        if growth_rate > self.config.complexity_growth_threshold:
            alert = self._create_complexity_growth_alert(
                snapshot_a, snapshot_b, growth_rate
            )
            alerts.append(alert)

        logger.info(f"Detected {len(alerts)} complexity growth alerts")

        return alerts

    def detect_performance_regression(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect performance regression between snapshots.

        Performance regression indicates:
        - Pipeline taking longer to execute
        - Potential optimization needed
        - Resource usage increase

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            List of DriftAlert objects for performance regression

        Example:
            >>> alerts = detector.detect_performance_regression(old_snap, new_snap)
            >>> for alert in alerts:
            ...     print(f"Performance regressed: {alert.message}")
        """
        logger.info("Detecting performance regression")

        alerts = []

        # Get execution times
        stats_a = snapshot_a.get("summary_stats", {})
        stats_b = snapshot_b.get("summary_stats", {})

        exec_time_a = stats_a.get("execution_time_seconds", 0)
        exec_time_b = stats_b.get("execution_time_seconds", 0)

        if exec_time_a == 0:
            return alerts

        # Calculate slowdown
        slowdown = (exec_time_b - exec_time_a) / exec_time_a

        # Check threshold
        if slowdown > self.config.performance_regression_threshold:
            alert = self._create_performance_regression_alert(
                snapshot_a, snapshot_b, slowdown
            )
            alerts.append(alert)

        logger.info(f"Detected {len(alerts)} performance regression alerts")

        return alerts

    def detect_missing_governance(
        self,
        snapshot: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect operations missing governance metadata.

        Missing governance indicates:
        - Compliance gap
        - Operations without business justification
        - Potential audit findings

        Args:
            snapshot: Snapshot to check for missing governance

        Returns:
            List of DriftAlert objects for missing governance

        Example:
            >>> alerts = detector.detect_missing_governance(snapshot)
            >>> print(f"Found {len(alerts)} operations missing governance")
        """
        logger.info("Detecting missing governance")

        alerts = []

        if not self.config.alert_on_missing_governance:
            return alerts

        # Get operations and governance records
        operations = snapshot.get("operations", [])
        governance = {g["operation_id"]: g for g in snapshot.get("governance", [])}

        # Check each operation
        for op in operations:
            op_id = op.get("operation_id")

            # Skip if governance exists
            if op_id in governance:
                continue

            # Create alert for missing governance
            alert = self._create_missing_governance_alert(snapshot, op)
            alerts.append(alert)

        logger.info(f"Detected {len(alerts)} missing governance alerts")

        return alerts

    def detect_all_drift(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
    ) -> List[DriftAlert]:
        """
        Detect all types of drift between two snapshots.

        This is a convenience method that runs all drift detection algorithms
        and returns a combined list of alerts.

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)

        Returns:
            List of all DriftAlert objects

        Example:
            >>> alerts = detector.detect_all_drift(old_snap, new_snap)
            >>> critical = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
            >>> print(f"Total alerts: {len(alerts)}, Critical: {len(critical)}")
        """
        logger.info("Detecting all drift types")

        all_alerts = []

        # Governance drift
        all_alerts.extend(self.detect_governance_drift(snapshot_a, snapshot_b))

        # Lineage drift
        all_alerts.extend(self.detect_lineage_drift(snapshot_a, snapshot_b))

        # Complexity growth
        all_alerts.extend(self.detect_complexity_growth(snapshot_a, snapshot_b))

        # Performance regression
        all_alerts.extend(self.detect_performance_regression(snapshot_a, snapshot_b))

        # Missing governance (only in snapshot B)
        all_alerts.extend(self.detect_missing_governance(snapshot_b))

        logger.info(f"Detected {len(all_alerts)} total drift alerts")

        return all_alerts

    def generate_drift_report(
        self,
        alerts: List[DriftAlert],
    ) -> str:
        """
        Generate a markdown report from drift alerts.

        Args:
            alerts: List of drift alerts

        Returns:
            Markdown formatted drift report

        Example:
            >>> alerts = detector.detect_all_drift(old_snap, new_snap)
            >>> report = detector.generate_drift_report(alerts)
            >>> print(report)
        """
        if not alerts:
            return "# Drift Detection Report\n\nNo drift detected.\n"

        # Sort alerts by severity
        sorted_alerts = sorted(
            alerts,
            key=lambda a: a.severity.priority,
            reverse=True
        )

        # Group by severity
        by_severity = {
            AlertSeverity.CRITICAL: [],
            AlertSeverity.ERROR: [],
            AlertSeverity.WARNING: [],
            AlertSeverity.INFO: [],
        }

        for alert in sorted_alerts:
            by_severity[alert.severity].append(alert)

        # Generate report
        lines = [
            "# Drift Detection Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Alerts:** {len(alerts)}",
            "",
            "## Summary",
            "",
        ]

        # Summary table
        for severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR, AlertSeverity.WARNING, AlertSeverity.INFO]:
            count = len(by_severity[severity])
            if count > 0:
                lines.append(f"- **{severity}:** {count}")

        lines.append("")

        # Detail sections by severity
        for severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR, AlertSeverity.WARNING, AlertSeverity.INFO]:
            alerts_for_severity = by_severity[severity]

            if not alerts_for_severity:
                continue

            lines.append(f"## {severity} Alerts")
            lines.append("")

            for alert in alerts_for_severity:
                lines.append(f"### {alert.title}")
                lines.append("")
                lines.append(f"**Type:** {alert.alert_type}")
                lines.append(f"**Pipeline:** {alert.pipeline_name}")
                lines.append(f"**Environment:** {alert.environment}")
                if alert.operation_id:
                    lines.append(f"**Operation:** {alert.operation_id}")
                lines.append("")
                lines.append(f"**Message:** {alert.message}")
                lines.append("")
                lines.append(f"**Recommendation:** {alert.recommendation}")
                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _create_governance_drift_alert(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        op_diff: Any,
    ) -> DriftAlert:
        """Create alert for governance drift."""
        return DriftAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.GOVERNANCE_DRIFT,
            severity=AlertSeverity.ERROR,
            pipeline_name=snapshot_b.get("pipeline_name", "unknown"),
            environment=snapshot_b.get("environment", "unknown"),
            operation_id=op_diff.operation_id,
            title="Governance Drift Detected",
            message=(
                f"Operation '{op_diff.operation_id}' has changed "
                f"(similarity: {op_diff.expression_similarity:.1%}) "
                f"but governance metadata was not updated. "
                f"This indicates governance documentation may be out of sync."
            ),
            recommendation=(
                "Review and update governance metadata for this operation. "
                "Ensure business justification, risk assessments, and approval "
                "status reflect the current implementation."
            ),
            detected_at=datetime.now(),
            snapshot_id_a=snapshot_a.get("snapshot_id"),
            snapshot_id_b=snapshot_b.get("snapshot_id"),
            metadata={
                "expression_similarity": op_diff.expression_similarity,
                "operation_type": op_diff.operation_type,
                "business_concept": op_diff.business_concept,
            },
        )

    def _create_lineage_drift_alert(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        op_diff: Any,
        gov_diff: Any,
    ) -> DriftAlert:
        """Create alert for lineage drift."""
        return DriftAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.LINEAGE_DRIFT,
            severity=AlertSeverity.WARNING,
            pipeline_name=snapshot_b.get("pipeline_name", "unknown"),
            environment=snapshot_b.get("environment", "unknown"),
            operation_id=op_diff.operation_id,
            title="Lineage Drift Detected",
            message=(
                f"Operation '{op_diff.operation_id}' governance metadata changed "
                f"({', '.join(gov_diff.changed_fields)}) "
                f"but lineage implementation did not change. "
                f"This may indicate documentation updates without code changes."
            ),
            recommendation=(
                "Verify that governance metadata changes are intentional. "
                "If documentation was updated to clarify existing behavior, this is expected. "
                "If documentation describes new behavior, ensure code is updated to match."
            ),
            detected_at=datetime.now(),
            snapshot_id_a=snapshot_a.get("snapshot_id"),
            snapshot_id_b=snapshot_b.get("snapshot_id"),
            metadata={
                "changed_fields": gov_diff.changed_fields,
                "operation_type": op_diff.operation_type,
                "business_concept": op_diff.business_concept,
            },
        )

    def _create_complexity_growth_alert(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        growth_rate: float,
    ) -> DriftAlert:
        """Create alert for complexity growth."""
        severity = AlertSeverity.WARNING
        if growth_rate > 0.5:
            severity = AlertSeverity.ERROR

        return DriftAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.COMPLEXITY_GROWTH,
            severity=severity,
            pipeline_name=snapshot_b.get("pipeline_name", "unknown"),
            environment=snapshot_b.get("environment", "unknown"),
            title="Complexity Growth Detected",
            message=(
                f"Pipeline complexity increased by {growth_rate:.1%}. "
                f"Operation count: {snapshot_a.get('summary_stats', {}).get('operation_count', 0)} "
                f"→ {snapshot_b.get('summary_stats', {}).get('operation_count', 0)}. "
                f"This may indicate technical debt accumulation."
            ),
            recommendation=(
                "Review pipeline for refactoring opportunities. "
                "Consider breaking down complex operations, "
                "extracting reusable components, or simplifying logic."
            ),
            detected_at=datetime.now(),
            snapshot_id_a=snapshot_a.get("snapshot_id"),
            snapshot_id_b=snapshot_b.get("snapshot_id"),
            metadata={
                "growth_rate": growth_rate,
                "operation_count_before": snapshot_a.get("summary_stats", {}).get("operation_count", 0),
                "operation_count_after": snapshot_b.get("summary_stats", {}).get("operation_count", 0),
            },
        )

    def _create_performance_regression_alert(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        slowdown: float,
    ) -> DriftAlert:
        """Create alert for performance regression."""
        severity = AlertSeverity.WARNING
        if slowdown > 1.0:
            severity = AlertSeverity.ERROR

        return DriftAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.PERFORMANCE_REGRESSION,
            severity=severity,
            pipeline_name=snapshot_b.get("pipeline_name", "unknown"),
            environment=snapshot_b.get("environment", "unknown"),
            title="Performance Regression Detected",
            message=(
                f"Pipeline execution time increased by {slowdown:.1%}. "
                f"Execution time: {snapshot_a.get('summary_stats', {}).get('execution_time_seconds', 0):.1f}s "
                f"→ {snapshot_b.get('summary_stats', {}).get('execution_time_seconds', 0):.1f}s. "
                f"This indicates performance degradation."
            ),
            recommendation=(
                "Profile pipeline to identify performance bottlenecks. "
                "Check for inefficient operations, missing optimizations, "
                "or increased data volume."
            ),
            detected_at=datetime.now(),
            snapshot_id_a=snapshot_a.get("snapshot_id"),
            snapshot_id_b=snapshot_b.get("snapshot_id"),
            metadata={
                "slowdown": slowdown,
                "execution_time_before": snapshot_a.get("summary_stats", {}).get("execution_time_seconds", 0),
                "execution_time_after": snapshot_b.get("summary_stats", {}).get("execution_time_seconds", 0),
            },
        )

    def _create_missing_governance_alert(
        self,
        snapshot: Dict[str, Any],
        operation: Dict[str, Any],
    ) -> DriftAlert:
        """Create alert for missing governance."""
        return DriftAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.MISSING_GOVERNANCE,
            severity=AlertSeverity.ERROR,
            pipeline_name=snapshot.get("pipeline_name", "unknown"),
            environment=snapshot.get("environment", "unknown"),
            operation_id=operation.get("operation_id"),
            title="Missing Governance Metadata",
            message=(
                f"Operation '{operation.get('operation_id')}' "
                f"({operation.get('operation_type')}) "
                f"does not have governance metadata. "
                f"This represents a compliance gap."
            ),
            recommendation=(
                "Add governance metadata for this operation using the governanceMeta decorator. "
                "At minimum, provide: business_justification, customer_impact_level, "
                "and data_classification."
            ),
            detected_at=datetime.now(),
            snapshot_id_b=snapshot.get("snapshot_id"),
            metadata={
                "operation_type": operation.get("operation_type"),
                "business_concept": operation.get("business_concept"),
                "description": operation.get("description"),
            },
        )
