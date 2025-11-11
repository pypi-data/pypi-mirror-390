"""
Alert generation and formatting system.

This module provides:
- Alert formatting for different outputs (Markdown, JSON, plain text)
- Alert deduplication logic
- Alert aggregation and grouping
- Alert threshold configuration

The alert system supports multiple output formats and provides
deduplication to avoid alert fatigue.
"""

import hashlib
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .models import AlertSeverity, AlertType, DriftAlert

logger = logging.getLogger(__name__)


class AlertFormatter:
    """
    Formats drift alerts for different output types.

    Supports:
    - Markdown (for reports)
    - JSON (for programmatic access)
    - Plain text (for logs/emails)
    - HTML (for dashboards)

    Example:
        >>> formatter = AlertFormatter()
        >>> markdown = formatter.format_markdown(alerts)
        >>> json_str = formatter.format_json(alerts)
        >>> text = formatter.format_plain_text(alerts)
    """

    def format_markdown(
        self,
        alerts: List[DriftAlert],
        include_metadata: bool = True,
    ) -> str:
        """
        Format alerts as markdown.

        Args:
            alerts: List of drift alerts
            include_metadata: Include detailed metadata (default: True)

        Returns:
            Markdown formatted alert list

        Example:
            >>> markdown = formatter.format_markdown(alerts)
            >>> with open("alerts.md", "w") as f:
            ...     f.write(markdown)
        """
        if not alerts:
            return "No alerts to display.\n"

        # Sort by severity
        sorted_alerts = sorted(
            alerts,
            key=lambda a: a.severity.priority,
            reverse=True
        )

        lines = [
            "# Drift Alerts",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Alerts:** {len(alerts)}",
            "",
        ]

        # Summary by severity
        by_severity = self._group_by_severity(alerts)
        lines.append("## Summary by Severity")
        lines.append("")

        for severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR, AlertSeverity.WARNING, AlertSeverity.INFO]:
            count = len(by_severity[severity])
            if count > 0:
                lines.append(f"- **{severity}:** {count}")

        lines.append("")

        # Detailed alerts
        lines.append("## Detailed Alerts")
        lines.append("")

        for alert in sorted_alerts:
            lines.extend(self._format_alert_markdown(alert, include_metadata))
            lines.append("")

        return "\n".join(lines)

    def format_json(
        self,
        alerts: List[DriftAlert],
        pretty: bool = True,
    ) -> str:
        """
        Format alerts as JSON.

        Args:
            alerts: List of drift alerts
            pretty: Pretty print JSON (default: True)

        Returns:
            JSON formatted alert list

        Example:
            >>> json_str = formatter.format_json(alerts)
            >>> alerts_data = json.loads(json_str)
        """
        alerts_data = [alert.to_dict() for alert in alerts]

        if pretty:
            return json.dumps(alerts_data, indent=2, default=str)
        else:
            return json.dumps(alerts_data, default=str)

    def format_plain_text(
        self,
        alerts: List[DriftAlert],
        max_width: int = 80,
    ) -> str:
        """
        Format alerts as plain text.

        Args:
            alerts: List of drift alerts
            max_width: Maximum line width (default: 80)

        Returns:
            Plain text formatted alert list

        Example:
            >>> text = formatter.format_plain_text(alerts)
            >>> print(text)
        """
        if not alerts:
            return "No alerts to display.\n"

        # Sort by severity
        sorted_alerts = sorted(
            alerts,
            key=lambda a: a.severity.priority,
            reverse=True
        )

        lines = [
            "=" * max_width,
            "DRIFT ALERTS",
            "=" * max_width,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Alerts: {len(alerts)}",
            "",
        ]

        for i, alert in enumerate(sorted_alerts, 1):
            lines.extend(self._format_alert_plain_text(alert, i, max_width))
            lines.append("")

        lines.append("=" * max_width)

        return "\n".join(lines)

    def format_html(
        self,
        alerts: List[DriftAlert],
    ) -> str:
        """
        Format alerts as HTML.

        Args:
            alerts: List of drift alerts

        Returns:
            HTML formatted alert list

        Example:
            >>> html = formatter.format_html(alerts)
            >>> with open("alerts.html", "w") as f:
            ...     f.write(html)
        """
        if not alerts:
            return "<p>No alerts to display.</p>"

        # Sort by severity
        sorted_alerts = sorted(
            alerts,
            key=lambda a: a.severity.priority,
            reverse=True
        )

        html_parts = [
            '<div class="drift-alerts">',
            '<h2>Drift Alerts</h2>',
            f'<p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
            f'<p><strong>Total Alerts:</strong> {len(alerts)}</p>',
        ]

        # Summary by severity
        by_severity = self._group_by_severity(alerts)
        html_parts.append('<h3>Summary by Severity</h3>')
        html_parts.append('<ul>')

        for severity in [AlertSeverity.CRITICAL, AlertSeverity.ERROR, AlertSeverity.WARNING, AlertSeverity.INFO]:
            count = len(by_severity[severity])
            if count > 0:
                html_parts.append(
                    f'<li class="severity-{severity.value.lower()}"><strong>{severity}:</strong> {count}</li>'
                )

        html_parts.append('</ul>')

        # Detailed alerts
        html_parts.append('<h3>Detailed Alerts</h3>')

        for alert in sorted_alerts:
            html_parts.extend(self._format_alert_html(alert))

        html_parts.append('</div>')

        return '\n'.join(html_parts)

    def _format_alert_markdown(
        self,
        alert: DriftAlert,
        include_metadata: bool = True,
    ) -> List[str]:
        """Format single alert as markdown."""
        lines = [
            f"### {self._get_severity_emoji(alert.severity)} {alert.title}",
            "",
            f"**Severity:** {alert.severity}  ",
            f"**Type:** {alert.alert_type}  ",
            f"**Pipeline:** {alert.pipeline_name}  ",
            f"**Environment:** {alert.environment}  ",
        ]

        if alert.operation_id:
            lines.append(f"**Operation:** {alert.operation_id}  ")

        lines.extend([
            "",
            f"**Message:** {alert.message}",
            "",
            f"**Recommendation:** {alert.recommendation}",
            "",
        ])

        if include_metadata and alert.metadata:
            lines.append("<details>")
            lines.append("<summary>Metadata</summary>")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(alert.metadata, indent=2, default=str))
            lines.append("```")
            lines.append("</details>")
            lines.append("")

        lines.append("---")

        return lines

    def _format_alert_plain_text(
        self,
        alert: DriftAlert,
        index: int,
        max_width: int,
    ) -> List[str]:
        """Format single alert as plain text."""
        lines = [
            "-" * max_width,
            f"ALERT #{index}: {alert.title}",
            "-" * max_width,
            f"Severity: {alert.severity}",
            f"Type: {alert.alert_type}",
            f"Pipeline: {alert.pipeline_name}",
            f"Environment: {alert.environment}",
        ]

        if alert.operation_id:
            lines.append(f"Operation: {alert.operation_id}")

        lines.extend([
            "",
            "MESSAGE:",
            self._wrap_text(alert.message, max_width),
            "",
            "RECOMMENDATION:",
            self._wrap_text(alert.recommendation, max_width),
        ])

        return lines

    def _format_alert_html(self, alert: DriftAlert) -> List[str]:
        """Format single alert as HTML."""
        severity_class = f"alert-{alert.severity.value.lower()}"

        html_parts = [
            f'<div class="alert {severity_class}">',
            f'<h4>{self._get_severity_emoji(alert.severity)} {alert.title}</h4>',
            '<dl>',
            f'<dt>Severity</dt><dd>{alert.severity}</dd>',
            f'<dt>Type</dt><dd>{alert.alert_type}</dd>',
            f'<dt>Pipeline</dt><dd>{alert.pipeline_name}</dd>',
            f'<dt>Environment</dt><dd>{alert.environment}</dd>',
        ]

        if alert.operation_id:
            html_parts.extend([
                '<dt>Operation</dt>',
                f'<dd>{alert.operation_id}</dd>',
            ])

        html_parts.extend([
            '</dl>',
            '<p><strong>Message:</strong></p>',
            f'<p>{alert.message}</p>',
            '<p><strong>Recommendation:</strong></p>',
            f'<p>{alert.recommendation}</p>',
            '</div>',
        ])

        return html_parts

    def _group_by_severity(self, alerts: List[DriftAlert]) -> Dict[AlertSeverity, List[DriftAlert]]:
        """Group alerts by severity level."""
        grouped = defaultdict(list)
        for alert in alerts:
            grouped[alert.severity].append(alert)
        return dict(grouped)

    def _get_severity_emoji(self, severity: AlertSeverity) -> str:
        """Get emoji for severity level."""
        return {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.ERROR: "❌",
            AlertSeverity.CRITICAL: "🚨",
        }.get(severity, "")

    def _wrap_text(self, text: str, max_width: int) -> str:
        """Wrap text to maximum width."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)

            if current_length + word_length + len(current_line) <= max_width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)


class AlertDeduplicator:
    """
    Deduplicates alerts to avoid alert fatigue.

    Tracks alert fingerprints and prevents duplicate alerts within
    a configurable time window.

    Example:
        >>> deduplicator = AlertDeduplicator(time_window_hours=24)
        >>> unique_alerts = deduplicator.deduplicate(alerts)
        >>> print(f"Filtered {len(alerts) - len(unique_alerts)} duplicates")
    """

    def __init__(
        self,
        time_window_hours: int = 24,
        storage: Optional[Dict[str, datetime]] = None,
    ):
        """
        Initialize alert deduplicator.

        Args:
            time_window_hours: Time window for deduplication (default: 24)
            storage: Optional storage for alert fingerprints
        """
        self.time_window_hours = time_window_hours
        self.storage = storage or {}

        logger.debug(f"Initialized AlertDeduplicator with time_window_hours={time_window_hours}")

    def deduplicate(
        self,
        alerts: List[DriftAlert],
    ) -> List[DriftAlert]:
        """
        Remove duplicate alerts based on fingerprint and time window.

        Args:
            alerts: List of drift alerts

        Returns:
            List of unique alerts (duplicates filtered out)

        Example:
            >>> unique_alerts = deduplicator.deduplicate(all_alerts)
        """
        unique_alerts = []
        current_time = datetime.now()

        for alert in alerts:
            fingerprint = alert.fingerprint

            # Check if we've seen this alert recently
            if fingerprint in self.storage:
                last_seen = self.storage[fingerprint]
                time_diff = current_time - last_seen

                if time_diff.total_seconds() < self.time_window_hours * 3600:
                    logger.debug(
                        f"Skipping duplicate alert: {alert.title} "
                        f"(last seen {time_diff.total_seconds() / 3600:.1f}h ago)"
                    )
                    continue

            # New or expired alert - keep it
            unique_alerts.append(alert)
            self.storage[fingerprint] = current_time

        logger.info(
            f"Deduplicated {len(alerts)} alerts -> {len(unique_alerts)} unique"
        )

        return unique_alerts

    def clear_expired(self):
        """Remove expired fingerprints from storage."""
        current_time = datetime.now()
        expired_keys = []

        for fingerprint, last_seen in self.storage.items():
            time_diff = current_time - last_seen

            if time_diff.total_seconds() >= self.time_window_hours * 3600:
                expired_keys.append(fingerprint)

        for key in expired_keys:
            del self.storage[key]

        logger.debug(f"Cleared {len(expired_keys)} expired fingerprints")

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about deduplication storage."""
        return {
            "total_fingerprints": len(self.storage),
            "time_window_hours": self.time_window_hours,
        }


class AlertAggregator:
    """
    Aggregates alerts for summary reporting.

    Provides grouping and statistical analysis of alerts:
    - Group by pipeline
    - Group by severity
    - Group by type
    - Calculate trends

    Example:
        >>> aggregator = AlertAggregator()
        >>> summary = aggregator.aggregate(alerts)
        >>> print(f"Most common alert type: {summary['by_type'][0]}")
    """

    def aggregate(
        self,
        alerts: List[DriftAlert],
    ) -> Dict[str, Any]:
        """
        Aggregate alerts and generate summary statistics.

        Args:
            alerts: List of drift alerts

        Returns:
            Dictionary with aggregated statistics

        Example:
            >>> summary = aggregator.aggregate(alerts)
            >>> print(f"Total: {summary['total']}")
            >>> print(f"By severity: {summary['by_severity']}")
        """
        if not alerts:
            return {
                "total": 0,
                "by_severity": {},
                "by_type": {},
                "by_pipeline": {},
                "by_environment": {},
            }

        # Group by various dimensions
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        by_pipeline = defaultdict(int)
        by_environment = defaultdict(int)

        for alert in alerts:
            by_severity[str(alert.severity)] += 1
            by_type[str(alert.alert_type)] += 1
            by_pipeline[alert.pipeline_name] += 1
            by_environment[alert.environment] += 1

        return {
            "total": len(alerts),
            "by_severity": dict(by_severity),
            "by_type": dict(by_type),
            "by_pipeline": dict(by_pipeline),
            "by_environment": dict(by_environment),
            "most_common_type": max(by_type.items(), key=lambda x: x[1])[0] if by_type else None,
            "most_affected_pipeline": max(by_pipeline.items(), key=lambda x: x[1])[0] if by_pipeline else None,
        }

    def group_by_pipeline(
        self,
        alerts: List[DriftAlert],
    ) -> Dict[str, List[DriftAlert]]:
        """Group alerts by pipeline name."""
        grouped = defaultdict(list)
        for alert in alerts:
            grouped[alert.pipeline_name].append(alert)
        return dict(grouped)

    def group_by_severity(
        self,
        alerts: List[DriftAlert],
    ) -> Dict[AlertSeverity, List[DriftAlert]]:
        """Group alerts by severity."""
        grouped = defaultdict(list)
        for alert in alerts:
            grouped[alert.severity].append(alert)
        return dict(grouped)

    def group_by_type(
        self,
        alerts: List[DriftAlert],
    ) -> Dict[AlertType, List[DriftAlert]]:
        """Group alerts by type."""
        grouped = defaultdict(list)
        for alert in alerts:
            grouped[alert.alert_type].append(alert)
        return dict(grouped)

    def get_critical_alerts(
        self,
        alerts: List[DriftAlert],
    ) -> List[DriftAlert]:
        """Get only critical severity alerts."""
        return [a for a in alerts if a.severity == AlertSeverity.CRITICAL]

    def get_high_priority_alerts(
        self,
        alerts: List[DriftAlert],
    ) -> List[DriftAlert]:
        """Get critical and error severity alerts."""
        return [
            a for a in alerts
            if a.severity in (AlertSeverity.CRITICAL, AlertSeverity.ERROR)
        ]
