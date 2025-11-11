"""
Comparison reporter for generating markdown reports.

This module provides the ComparisonReporter class which generates:
- Side-by-side snapshot comparison reports
- Governance drift reports
- Change summaries with impact assessment
- Actionable recommendations

Reports are formatted in markdown for readability and can include
charts, tables, and structured sections.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .alerts import AlertFormatter
from .models import (
    AlertSeverity,
    ChangeType,
    ComparisonReport,
    DriftAlert,
    LineageDiff,
)

logger = logging.getLogger(__name__)


class ComparisonReporter:
    """
    Generates markdown reports for lineage comparisons.

    This class creates comprehensive reports that include:
    - Executive summary
    - Structural changes (operations added/removed/modified)
    - Governance drift analysis
    - Expression changes with similarity scores
    - Drift alerts
    - Actionable recommendations

    Example:
        >>> reporter = ComparisonReporter()
        >>> report = reporter.generate_comparison_report(lineage_diff, drift_alerts)
        >>> with open("comparison_report.md", "w") as f:
        ...     f.write(report.report_markdown)
    """

    def __init__(self):
        """Initialize comparison reporter."""
        self.alert_formatter = AlertFormatter()
        logger.debug("Initialized ComparisonReporter")

    def generate_comparison_report(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: Optional[List[DriftAlert]] = None,
        title: Optional[str] = None,
    ) -> ComparisonReport:
        """
        Generate a complete comparison report.

        Args:
            lineage_diff: LineageDiff object from comparison
            drift_alerts: Optional list of drift alerts
            title: Optional custom report title

        Returns:
            ComparisonReport object with markdown and JSON exports

        Example:
            >>> report = reporter.generate_comparison_report(diff, alerts)
            >>> print(report.summary)
            >>> print(report.report_markdown)
        """
        logger.info("Generating comparison report")

        drift_alerts = drift_alerts or []

        # Generate report components
        report_markdown = self._generate_markdown_report(
            lineage_diff, drift_alerts, title
        )

        report_json = self._generate_json_report(lineage_diff, drift_alerts)

        summary = self._generate_summary(lineage_diff, drift_alerts)

        recommendations = self._generate_recommendations(lineage_diff, drift_alerts)

        # Create ComparisonReport
        report = ComparisonReport(
            report_id=str(uuid.uuid4()),
            title=title or "Lineage Comparison Report",
            generated_at=datetime.now(),
            lineage_diff=lineage_diff,
            drift_alerts=drift_alerts,
            report_markdown=report_markdown,
            report_json=report_json,
            summary=summary,
            recommendations=recommendations,
        )

        logger.info(f"Generated comparison report: {report.report_id}")

        return report

    def generate_drift_report(
        self,
        drift_alerts: List[DriftAlert],
        title: Optional[str] = None,
    ) -> str:
        """
        Generate a drift-focused markdown report.

        Args:
            drift_alerts: List of drift alerts
            title: Optional custom report title

        Returns:
            Markdown formatted drift report

        Example:
            >>> report_md = reporter.generate_drift_report(alerts)
            >>> with open("drift_report.md", "w") as f:
            ...     f.write(report_md)
        """
        return self.alert_formatter.format_markdown(drift_alerts)

    def generate_summary_report(
        self,
        lineage_diff: LineageDiff,
        max_details: int = 10,
    ) -> str:
        """
        Generate a concise summary report.

        Args:
            lineage_diff: LineageDiff object from comparison
            max_details: Maximum number of detailed changes to show

        Returns:
            Markdown formatted summary report

        Example:
            >>> summary = reporter.generate_summary_report(diff)
            >>> print(summary)
        """
        lines = [
            "# Lineage Comparison Summary",
            "",
            f"**Compared:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Snapshots",
            "",
            f"**Baseline:** {lineage_diff.snapshot_id_a}  ",
            f"- Pipeline: {lineage_diff.snapshot_a_metadata.get('pipeline_name')}  ",
            f"- Environment: {lineage_diff.snapshot_a_metadata.get('environment')}  ",
            f"- Captured: {lineage_diff.snapshot_a_metadata.get('captured_at')}  ",
            "",
            f"**Comparison:** {lineage_diff.snapshot_id_b}  ",
            f"- Pipeline: {lineage_diff.snapshot_b_metadata.get('pipeline_name')}  ",
            f"- Environment: {lineage_diff.snapshot_b_metadata.get('environment')}  ",
            f"- Captured: {lineage_diff.snapshot_b_metadata.get('captured_at')}  ",
            "",
            "## Changes Summary",
            "",
            f"- **Operations Added:** {len(lineage_diff.graph_diff.operations_added)}",
            f"- **Operations Removed:** {len(lineage_diff.graph_diff.operations_removed)}",
            f"- **Operations Modified:** {len(lineage_diff.graph_diff.operations_modified)}",
            f"- **Governance Changes:** {len(lineage_diff.governance_diffs)}",
            f"- **Expression Changes:** {len(lineage_diff.expression_diffs)}",
            "",
        ]

        # Add drift flags
        if lineage_diff.has_governance_drift:
            lines.append("⚠️ **Governance Drift Detected**")
        if lineage_diff.has_lineage_drift:
            lines.append("ℹ️ **Lineage Drift Detected**")

        if lineage_diff.has_governance_drift or lineage_diff.has_lineage_drift:
            lines.append("")

        return "\n".join(lines)

    def _generate_markdown_report(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: List[DriftAlert],
        title: Optional[str],
    ) -> str:
        """Generate complete markdown report."""
        title = title or "Lineage Comparison Report"

        lines = [
            f"# {title}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Report ID:** {lineage_diff.snapshot_id_a} → {lineage_diff.snapshot_id_b}",
            "",
        ]

        # Executive summary
        lines.extend(self._generate_executive_summary_section(lineage_diff, drift_alerts))

        # Snapshot comparison
        lines.extend(self._generate_snapshot_comparison_section(lineage_diff))

        # Structural changes
        lines.extend(self._generate_structural_changes_section(lineage_diff))

        # Governance changes
        if lineage_diff.governance_diffs:
            lines.extend(self._generate_governance_changes_section(lineage_diff))

        # Expression changes
        if lineage_diff.expression_diffs:
            lines.extend(self._generate_expression_changes_section(lineage_diff))

        # Drift alerts
        if drift_alerts:
            lines.extend(self._generate_alerts_section(drift_alerts))

        # Recommendations
        recommendations = self._generate_recommendations(lineage_diff, drift_alerts)
        if recommendations:
            lines.extend(self._generate_recommendations_section(recommendations))

        return "\n".join(lines)

    def _generate_executive_summary_section(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: List[DriftAlert],
    ) -> List[str]:
        """Generate executive summary section."""
        lines = [
            "## Executive Summary",
            "",
        ]

        # Overall assessment
        if not lineage_diff.has_differences():
            lines.append("✅ **No significant differences detected between snapshots.**")
            lines.append("")
            return lines

        # Changes summary
        stats = lineage_diff.summary_stats
        lines.extend([
            f"**Total Operations (Baseline):** {stats.get('total_operations_a', 0)}  ",
            f"**Total Operations (Comparison):** {stats.get('total_operations_b', 0)}  ",
            f"**Operations Added:** {stats.get('operations_added', 0)}  ",
            f"**Operations Removed:** {stats.get('operations_removed', 0)}  ",
            f"**Operations Modified:** {stats.get('operations_modified', 0)}  ",
            f"**Significant Changes:** {stats.get('significant_changes', 0)}  ",
            "",
        ])

        # Drift status
        if lineage_diff.has_governance_drift:
            lines.append("⚠️ **Governance Drift:** Lineage changed without governance updates")
        if lineage_diff.has_lineage_drift:
            lines.append("ℹ️ **Lineage Drift:** Governance changed without lineage updates")

        if lineage_diff.has_governance_drift or lineage_diff.has_lineage_drift:
            lines.append("")

        # Alert summary
        if drift_alerts:
            critical = len([a for a in drift_alerts if a.severity == AlertSeverity.CRITICAL])
            errors = len([a for a in drift_alerts if a.severity == AlertSeverity.ERROR])
            warnings = len([a for a in drift_alerts if a.severity == AlertSeverity.WARNING])

            lines.append(f"**Alerts Generated:** {len(drift_alerts)} total")
            if critical > 0:
                lines.append(f"- 🚨 Critical: {critical}")
            if errors > 0:
                lines.append(f"- ❌ Errors: {errors}")
            if warnings > 0:
                lines.append(f"- ⚠️ Warnings: {warnings}")
            lines.append("")

        return lines

    def _generate_snapshot_comparison_section(
        self,
        lineage_diff: LineageDiff,
    ) -> List[str]:
        """Generate snapshot comparison section."""
        lines = [
            "## Snapshot Comparison",
            "",
            "### Baseline Snapshot",
            "",
            f"- **Snapshot ID:** `{lineage_diff.snapshot_id_a}`",
            f"- **Pipeline:** {lineage_diff.snapshot_a_metadata.get('pipeline_name')}",
            f"- **Environment:** {lineage_diff.snapshot_a_metadata.get('environment')}",
            f"- **Captured:** {lineage_diff.snapshot_a_metadata.get('captured_at')}",
            f"- **Version:** {lineage_diff.snapshot_a_metadata.get('version', 'N/A')}",
            f"- **User:** {lineage_diff.snapshot_a_metadata.get('user', 'N/A')}",
            "",
            "### Comparison Snapshot",
            "",
            f"- **Snapshot ID:** `{lineage_diff.snapshot_id_b}`",
            f"- **Pipeline:** {lineage_diff.snapshot_b_metadata.get('pipeline_name')}",
            f"- **Environment:** {lineage_diff.snapshot_b_metadata.get('environment')}",
            f"- **Captured:** {lineage_diff.snapshot_b_metadata.get('captured_at')}",
            f"- **Version:** {lineage_diff.snapshot_b_metadata.get('version', 'N/A')}",
            f"- **User:** {lineage_diff.snapshot_b_metadata.get('user', 'N/A')}",
            "",
        ]

        return lines

    def _generate_structural_changes_section(
        self,
        lineage_diff: LineageDiff,
    ) -> List[str]:
        """Generate structural changes section."""
        graph_diff = lineage_diff.graph_diff

        lines = [
            "## Structural Changes",
            "",
        ]

        # Operations added
        if graph_diff.operations_added:
            lines.append(f"### Operations Added ({len(graph_diff.operations_added)})")
            lines.append("")
            for op_id in graph_diff.operations_added[:20]:  # Limit to first 20
                lines.append(f"- `{op_id}`")
            if len(graph_diff.operations_added) > 20:
                lines.append(f"- ... and {len(graph_diff.operations_added) - 20} more")
            lines.append("")

        # Operations removed
        if graph_diff.operations_removed:
            lines.append(f"### Operations Removed ({len(graph_diff.operations_removed)})")
            lines.append("")
            for op_id in graph_diff.operations_removed[:20]:
                lines.append(f"- `{op_id}`")
            if len(graph_diff.operations_removed) > 20:
                lines.append(f"- ... and {len(graph_diff.operations_removed) - 20} more")
            lines.append("")

        # Operations modified
        if graph_diff.operations_modified:
            lines.append(f"### Operations Modified ({len(graph_diff.operations_modified)})")
            lines.append("")

            # Show details for modified operations
            modified_details = [
                diff for diff in lineage_diff.operation_diffs
                if diff.change_type == ChangeType.MODIFIED
            ]

            for op_diff in modified_details[:20]:
                lines.append(f"#### `{op_diff.operation_id}`")
                lines.append("")
                if op_diff.business_concept:
                    lines.append(f"**Business Concept:** {op_diff.business_concept}  ")
                if op_diff.expression_similarity < 0.95:
                    lines.append(
                        f"**Expression Similarity:** {op_diff.expression_similarity:.1%}  "
                    )
                if op_diff.governance_changed:
                    lines.append("**Governance:** Changed  ")
                lines.append("")

            if len(modified_details) > 20:
                lines.append(f"... and {len(modified_details) - 20} more")
                lines.append("")

        # Business concepts
        if graph_diff.business_concepts_added or graph_diff.business_concepts_removed:
            lines.append("### Business Concepts Changes")
            lines.append("")

            if graph_diff.business_concepts_added:
                lines.append("**Added:**")
                for concept in graph_diff.business_concepts_added:
                    lines.append(f"- {concept}")
                lines.append("")

            if graph_diff.business_concepts_removed:
                lines.append("**Removed:**")
                for concept in graph_diff.business_concepts_removed:
                    lines.append(f"- {concept}")
                lines.append("")

        return lines

    def _generate_governance_changes_section(
        self,
        lineage_diff: LineageDiff,
    ) -> List[str]:
        """Generate governance changes section."""
        lines = [
            "## Governance Changes",
            "",
            f"**Total Governance Changes:** {len(lineage_diff.governance_diffs)}",
            "",
        ]

        for gov_diff in lineage_diff.governance_diffs[:20]:
            lines.append(f"### Operation: `{gov_diff.operation_id}`")
            lines.append("")
            lines.append(f"**Changed Fields:** {', '.join(gov_diff.changed_fields)}")
            lines.append("")

            # Show specific changes
            if gov_diff.business_justification_changed:
                lines.append("**Business Justification:**")
                lines.append(f"- Before: {gov_diff.fields_before.get('business_justification', 'N/A')}")
                lines.append(f"- After: {gov_diff.fields_after.get('business_justification', 'N/A')}")
                lines.append("")

            if gov_diff.pii_processing_changed:
                lines.append("**PII Processing:**")
                lines.append(f"- Before: {gov_diff.fields_before.get('pii_processing', False)}")
                lines.append(f"- After: {gov_diff.fields_after.get('pii_processing', False)}")
                lines.append("")

        if len(lineage_diff.governance_diffs) > 20:
            lines.append(f"... and {len(lineage_diff.governance_diffs) - 20} more")
            lines.append("")

        return lines

    def _generate_expression_changes_section(
        self,
        lineage_diff: LineageDiff,
    ) -> List[str]:
        """Generate expression changes section."""
        lines = [
            "## Expression Changes",
            "",
            f"**Total Expression Changes:** {len(lineage_diff.expression_diffs)}",
            "",
        ]

        # Sort by similarity (most different first)
        sorted_diffs = sorted(
            lineage_diff.expression_diffs,
            key=lambda d: d.similarity_score
        )

        for expr_diff in sorted_diffs[:10]:
            lines.append(f"### Operation: `{expr_diff.operation_id}`")
            lines.append("")
            lines.append(f"**Similarity Score:** {expr_diff.similarity_score:.1%}")
            lines.append(f"**Change Assessment:** {expr_diff.get_summary()}")
            lines.append("")

            lines.append("<details>")
            lines.append("<summary>Expression Details</summary>")
            lines.append("")
            lines.append("**Before:**")
            lines.append("```json")
            lines.append(expr_diff.expression_before)
            lines.append("```")
            lines.append("")
            lines.append("**After:**")
            lines.append("```json")
            lines.append(expr_diff.expression_after)
            lines.append("```")
            lines.append("</details>")
            lines.append("")

        if len(lineage_diff.expression_diffs) > 10:
            lines.append(f"... and {len(lineage_diff.expression_diffs) - 10} more")
            lines.append("")

        return lines

    def _generate_alerts_section(
        self,
        drift_alerts: List[DriftAlert],
    ) -> List[str]:
        """Generate alerts section."""
        lines = [
            "## Drift Alerts",
            "",
            f"**Total Alerts:** {len(drift_alerts)}",
            "",
        ]

        # Use alert formatter for consistent formatting
        alert_markdown = self.alert_formatter.format_markdown(drift_alerts, include_metadata=False)

        # Extract just the detailed alerts section
        alert_lines = alert_markdown.split("\n")
        in_details = False
        for line in alert_lines:
            if line.startswith("## Detailed Alerts"):
                in_details = True
                continue
            if in_details:
                lines.append(line)

        return lines

    def _generate_recommendations_section(
        self,
        recommendations: List[str],
    ) -> List[str]:
        """Generate recommendations section."""
        lines = [
            "## Recommendations",
            "",
        ]

        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")

        lines.append("")

        return lines

    def _generate_json_report(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: List[DriftAlert],
    ) -> str:
        """Generate JSON export of comparison data."""
        data = {
            "snapshot_a": {
                "snapshot_id": lineage_diff.snapshot_id_a,
                "metadata": lineage_diff.snapshot_a_metadata,
            },
            "snapshot_b": {
                "snapshot_id": lineage_diff.snapshot_id_b,
                "metadata": lineage_diff.snapshot_b_metadata,
            },
            "compared_at": lineage_diff.compared_at.isoformat(),
            "graph_diff": {
                "operations_added": lineage_diff.graph_diff.operations_added,
                "operations_removed": lineage_diff.graph_diff.operations_removed,
                "operations_modified": lineage_diff.graph_diff.operations_modified,
                "business_concepts_added": lineage_diff.graph_diff.business_concepts_added,
                "business_concepts_removed": lineage_diff.graph_diff.business_concepts_removed,
            },
            "operation_diffs": [
                {
                    "operation_id": diff.operation_id,
                    "change_type": str(diff.change_type),
                    "expression_similarity": diff.expression_similarity,
                    "governance_changed": diff.governance_changed,
                }
                for diff in lineage_diff.operation_diffs
            ],
            "governance_diffs": [
                {
                    "operation_id": diff.operation_id,
                    "changed_fields": diff.changed_fields,
                }
                for diff in lineage_diff.governance_diffs
            ],
            "drift_alerts": [alert.to_dict() for alert in drift_alerts],
            "summary_stats": lineage_diff.summary_stats,
        }

        return json.dumps(data, indent=2, default=str)

    def _generate_summary(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: List[DriftAlert],
    ) -> str:
        """Generate executive summary text."""
        if not lineage_diff.has_differences():
            return "No significant differences detected between snapshots."

        parts = []

        # Structural changes
        added = len(lineage_diff.graph_diff.operations_added)
        removed = len(lineage_diff.graph_diff.operations_removed)
        modified = len(lineage_diff.graph_diff.operations_modified)

        if added > 0:
            parts.append(f"{added} operations added")
        if removed > 0:
            parts.append(f"{removed} operations removed")
        if modified > 0:
            parts.append(f"{modified} operations modified")

        # Drift
        if lineage_diff.has_governance_drift:
            parts.append("governance drift detected")
        if lineage_diff.has_lineage_drift:
            parts.append("lineage drift detected")

        # Alerts
        if drift_alerts:
            critical = len([a for a in drift_alerts if a.severity == AlertSeverity.CRITICAL])
            if critical > 0:
                parts.append(f"{critical} critical alerts")

        return "; ".join(parts) + "."

    def _generate_recommendations(
        self,
        lineage_diff: LineageDiff,
        drift_alerts: List[DriftAlert],
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Governance drift
        if lineage_diff.has_governance_drift:
            recommendations.append(
                "Update governance metadata for operations with lineage changes to maintain compliance."
            )

        # Lineage drift
        if lineage_diff.has_lineage_drift:
            recommendations.append(
                "Review governance documentation updates to ensure they accurately reflect current implementation."
            )

        # Critical alerts
        critical_alerts = [a for a in drift_alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            recommendations.append(
                f"Address {len(critical_alerts)} critical alerts immediately before proceeding."
            )

        # Large changes
        stats = lineage_diff.summary_stats
        if stats.get("operations_added", 0) > 10:
            recommendations.append(
                "Large number of operations added - ensure comprehensive testing and documentation."
            )

        # Default recommendation
        if not recommendations:
            recommendations.append(
                "Review all changes and ensure stakeholders are informed before deployment."
            )

        return recommendations
