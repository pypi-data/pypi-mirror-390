"""
Governance alert reporter for generating actionable governance drift reports.

This module provides the GovernanceAlertReporter class which:
- Detects when lineage changes without governance updates
- Generates actionable markdown reports with specific recommendations
- Identifies operations that need governance review
- Provides governance gap analysis across pipeline versions

The reporter uses DriftDetector for detection and adds specialized
reporting capabilities focused on governance compliance.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .drift_detector import DriftDetector
from .models import AlertSeverity, AlertType, DriftAlert, DriftDetectionConfig

logger = logging.getLogger(__name__)


class GovernanceAlertReporter:
    """
    Generates governance drift alert reports.

    This class specializes in detecting and reporting governance drift issues,
    specifically focusing on situations where lineage changes but governance
    metadata is not updated accordingly.

    Example:
        >>> reporter = GovernanceAlertReporter()
        >>> report_path = reporter.generate_governance_alert_report(
        ...     snapshot_a=old_snapshot,
        ...     snapshot_b=new_snapshot,
        ...     output_dir="./reports"
        ... )
        >>> print(f"Report saved to: {report_path}")
    """

    def __init__(
        self,
        config: Optional[DriftDetectionConfig] = None,
        detector: Optional[DriftDetector] = None,
    ):
        """
        Initialize governance alert reporter.

        Args:
            config: Drift detection configuration (default: default config)
            detector: DriftDetector instance (default: new instance)
        """
        self.config = config or DriftDetectionConfig()
        self.detector = detector or DriftDetector(config=self.config)

        logger.debug("Initialized GovernanceAlertReporter")

    def generate_governance_alert_report(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        output_dir: str,
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate governance alert report between two snapshots.

        This generates a detailed markdown report focusing on governance drift,
        identifying operations where lineage changed but governance did not.

        Args:
            snapshot_a: First snapshot (baseline)
            snapshot_b: Second snapshot (comparison)
            output_dir: Directory to save report
            filename: Optional custom filename (default: auto-generated)

        Returns:
            Path to generated report file

        Example:
            >>> report_path = reporter.generate_governance_alert_report(
            ...     snapshot_a=old_snapshot,
            ...     snapshot_b=new_snapshot,
            ...     output_dir="./reports"
            ... )
        """
        logger.info("Generating governance alert report")

        # Detect governance drift
        governance_alerts = self.detector.detect_governance_drift(snapshot_a, snapshot_b)

        # Also detect missing governance in new snapshot
        missing_governance_alerts = self.detector.detect_missing_governance(snapshot_b)

        # Combine alerts
        all_alerts = governance_alerts + missing_governance_alerts

        # Generate report content
        report_content = self._generate_report_content(
            snapshot_a, snapshot_b, all_alerts
        )

        # Save report
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            version_a = snapshot_a.get("version", "unknown")
            version_b = snapshot_b.get("version", "unknown")
            filename = f"governance_alert_{version_a}_to_{version_b}.md"

        report_path = output_path / filename
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"Governance alert report saved to: {report_path}")

        return str(report_path)

    def generate_multi_version_governance_report(
        self,
        snapshots: List[Dict[str, Any]],
        output_dir: str,
        filename: str = "governance_trend_analysis.md",
    ) -> str:
        """
        Generate governance trend analysis across multiple snapshots.

        This analyzes governance drift patterns across multiple pipeline versions,
        identifying trends and recurring issues.

        Args:
            snapshots: List of snapshots in chronological order
            output_dir: Directory to save report
            filename: Report filename (default: governance_trend_analysis.md)

        Returns:
            Path to generated report file

        Example:
            >>> snapshots = [snapshot_v1, snapshot_v2, snapshot_v3]
            >>> report_path = reporter.generate_multi_version_governance_report(
            ...     snapshots=snapshots,
            ...     output_dir="./reports"
            ... )
        """
        logger.info(f"Generating multi-version governance report for {len(snapshots)} snapshots")

        if len(snapshots) < 2:
            logger.warning("Need at least 2 snapshots for trend analysis")
            return ""

        # Analyze each consecutive pair
        all_drift_data = []
        for i in range(len(snapshots) - 1):
            snapshot_a = snapshots[i]
            snapshot_b = snapshots[i + 1]

            governance_alerts = self.detector.detect_governance_drift(snapshot_a, snapshot_b)
            missing_alerts = self.detector.detect_missing_governance(snapshot_b)

            all_drift_data.append({
                "version_from": snapshot_a.get("version", "unknown"),
                "version_to": snapshot_b.get("version", "unknown"),
                "timestamp": snapshot_b.get("captured_at"),
                "governance_drift_count": len(governance_alerts),
                "missing_governance_count": len(missing_alerts),
                "alerts": governance_alerts + missing_alerts,
            })

        # Generate trend report content
        report_content = self._generate_trend_report_content(snapshots, all_drift_data)

        # Save report
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        report_path = output_path / filename
        report_path.write_text(report_content, encoding="utf-8")

        logger.info(f"Governance trend report saved to: {report_path}")

        return str(report_path)

    def _generate_report_content(
        self,
        snapshot_a: Dict[str, Any],
        snapshot_b: Dict[str, Any],
        alerts: List[DriftAlert],
    ) -> str:
        """Generate markdown content for governance alert report."""
        lines = [
            "# Governance Alert Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            "",
            "This report identifies governance drift issues where pipeline lineage has changed",
            "but governance metadata has not been updated accordingly. Each alert requires",
            "review to ensure governance documentation remains synchronized with implementation.",
            "",
            "## Snapshot Comparison",
            "",
            "### Baseline Snapshot",
            "",
            f"- **Snapshot ID:** `{snapshot_a.get('snapshot_id', 'unknown')}`",
            f"- **Pipeline:** {snapshot_a.get('pipeline_name', 'unknown')}",
            f"- **Environment:** {snapshot_a.get('environment', 'unknown')}",
            f"- **Version:** {snapshot_a.get('version', 'unknown')}",
            f"- **Captured:** {snapshot_a.get('captured_at', 'unknown')}",
            "",
            "### Current Snapshot",
            "",
            f"- **Snapshot ID:** `{snapshot_b.get('snapshot_id', 'unknown')}`",
            f"- **Pipeline:** {snapshot_b.get('pipeline_name', 'unknown')}",
            f"- **Environment:** {snapshot_b.get('environment', 'unknown')}",
            f"- **Version:** {snapshot_b.get('version', 'unknown')}",
            f"- **Captured:** {snapshot_b.get('captured_at', 'unknown')}",
            "",
        ]

        # Summary
        governance_drift_alerts = [a for a in alerts if a.alert_type == AlertType.GOVERNANCE_DRIFT]
        missing_governance_alerts = [a for a in alerts if a.alert_type == AlertType.MISSING_GOVERNANCE]

        lines.extend([
            "## Alert Summary",
            "",
            f"- **Total Alerts:** {len(alerts)}",
            f"- **Governance Drift (lineage changed, governance unchanged):** {len(governance_drift_alerts)}",
            f"- **Missing Governance (operations without governance metadata):** {len(missing_governance_alerts)}",
            "",
        ])

        if not alerts:
            lines.extend([
                "## Status",
                "",
                "[OK] No governance drift detected. All lineage changes have corresponding governance updates.",
                "",
            ])
            return "\n".join(lines)

        # Group by severity
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        error_alerts = [a for a in alerts if a.severity == AlertSeverity.ERROR]
        warning_alerts = [a for a in alerts if a.severity == AlertSeverity.WARNING]

        if critical_alerts:
            lines.extend([
                f"## CRITICAL Alerts ({len(critical_alerts)})",
                "",
                "[!] These alerts require immediate attention.",
                "",
            ])
            for alert in critical_alerts:
                lines.extend(self._format_alert(alert))

        if error_alerts:
            lines.extend([
                f"## ERROR Alerts ({len(error_alerts)})",
                "",
                "[!] These alerts should be addressed soon.",
                "",
            ])
            for alert in error_alerts:
                lines.extend(self._format_alert(alert))

        if warning_alerts:
            lines.extend([
                f"## WARNING Alerts ({len(warning_alerts)})",
                "",
                "[!] These alerts should be reviewed.",
                "",
            ])
            for alert in warning_alerts:
                lines.extend(self._format_alert(alert))

        # Actionable recommendations
        lines.extend([
            "## Recommended Actions",
            "",
            "To resolve governance drift alerts:",
            "",
            "1. **Review Each Operation:** Examine the implementation changes for each flagged operation",
            "2. **Update Governance Metadata:** Use the `@governanceMeta` decorator to update:",
            "   - `business_justification`: Explain why the change was made",
            "   - `customer_impact_level`: Assess impact on customers (low, medium, high, critical)",
            "   - `data_classification`: Update if data sensitivity changed",
            "   - `requires_approval`: Mark if change requires additional review",
            "3. **Capture New Snapshot:** After updating governance, create a new snapshot to verify compliance",
            "4. **Review Missing Governance:** Add governance metadata to any operations without it",
            "",
            "## Example Governance Update",
            "",
            "```python",
            "@governanceMeta(",
            "    business_justification='Updated filtering logic to exclude inactive customers',",
            "    customer_impact_level='medium',",
            "    data_classification='internal',",
            "    requires_approval=False",
            ")",
            "@storyDoc(",
            "    business_concept='Active Customer Filter',",
            "    description='Filter to identify active customers'",
            ")",
            "def filter_active_customers(df):",
            "    return df.filter(F.col('status') == 'active')",
            "```",
            "",
        ])

        return "\n".join(lines)

    def _format_alert(self, alert: DriftAlert) -> List[str]:
        """Format a single alert as markdown lines."""
        lines = [
            f"### {alert.title}",
            "",
            f"**Operation:** `{alert.operation_id}`",
            f"**Type:** {alert.alert_type.value}",
            "",
            f"**Issue:** {alert.message}",
            "",
            f"**Action Required:** {alert.recommendation}",
            "",
        ]

        # Add metadata if available
        if alert.metadata:
            if "expression_similarity" in alert.metadata:
                similarity = alert.metadata["expression_similarity"]
                lines.append(f"**Expression Similarity:** {similarity:.1%} (lower = more changed)")
                lines.append("")

            if "business_concept" in alert.metadata and alert.metadata["business_concept"]:
                lines.append(f"**Business Concept:** {alert.metadata['business_concept']}")
                lines.append("")

        lines.append("---")
        lines.append("")

        return lines

    def _generate_trend_report_content(
        self,
        snapshots: List[Dict[str, Any]],
        drift_data: List[Dict[str, Any]],
    ) -> str:
        """Generate markdown content for governance trend analysis."""
        lines = [
            "# Governance Drift Trend Analysis",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Snapshots Analyzed:** {len(snapshots)}",
            "",
            "## Overview",
            "",
            "This report analyzes governance drift patterns across multiple pipeline versions,",
            "identifying trends and recurring governance compliance issues.",
            "",
            "## Trend Summary",
            "",
        ]

        # Calculate overall trends
        total_governance_drift = sum(d["governance_drift_count"] for d in drift_data)
        total_missing_governance = sum(d["missing_governance_count"] for d in drift_data)

        lines.extend([
            f"- **Total Version Transitions:** {len(drift_data)}",
            f"- **Total Governance Drift Alerts:** {total_governance_drift}",
            f"- **Total Missing Governance Alerts:** {total_missing_governance}",
            "",
        ])

        # Version-by-version breakdown
        lines.extend([
            "## Version-by-Version Analysis",
            "",
        ])

        for i, data in enumerate(drift_data, 1):
            total_alerts = data["governance_drift_count"] + data["missing_governance_count"]

            status_icon = "[OK]" if total_alerts == 0 else "[!]"

            lines.extend([
                f"### {i}. {data['version_from']} → {data['version_to']}",
                "",
                f"**Status:** {status_icon}",
                f"**Timestamp:** {data['timestamp']}",
                f"**Governance Drift:** {data['governance_drift_count']}",
                f"**Missing Governance:** {data['missing_governance_count']}",
                "",
            ])

            if data["alerts"]:
                lines.append("**Alerts:**")
                lines.append("")
                for alert in data["alerts"]:
                    lines.append(f"- {alert.severity.value}: {alert.operation_id} - {alert.message}")
                lines.append("")

        # Recommendations
        lines.extend([
            "## Trend-Based Recommendations",
            "",
        ])

        if total_governance_drift == 0 and total_missing_governance == 0:
            lines.extend([
                "[OK] Excellent governance compliance! No drift detected across all versions.",
                "",
                "Continue current practices:",
                "- Update governance metadata whenever implementation changes",
                "- Add governance metadata to all new operations",
                "- Regular snapshot capture for ongoing monitoring",
                "",
            ])
        else:
            # Calculate average drift per version
            avg_drift = total_governance_drift / len(drift_data) if drift_data else 0

            if avg_drift > 2:
                lines.extend([
                    "[!] HIGH governance drift rate detected.",
                    "",
                    "**Recommended Actions:**",
                    "1. Establish governance update policy in change management process",
                    "2. Add governance review step to code review checklist",
                    "3. Train team on importance of governance metadata",
                    "4. Consider automated governance validation in CI/CD pipeline",
                    "",
                ])
            else:
                lines.extend([
                    "[!] Moderate governance drift detected.",
                    "",
                    "**Recommended Actions:**",
                    "1. Review flagged operations and update governance metadata",
                    "2. Add governance metadata to operations that are missing it",
                    "3. Include governance update reminders in pull request templates",
                    "",
                ])

        return "\n".join(lines)
