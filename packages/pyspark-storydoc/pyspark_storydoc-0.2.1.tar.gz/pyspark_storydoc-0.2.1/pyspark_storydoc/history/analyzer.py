"""
High-level analyzer combining trend analysis and alerting.

This module provides the HistoryAnalyzer class that integrates all Phase 3
trend analysis and alerting capabilities.

Example:
    >>> from pyspark_storydoc.history import HistoryAnalyzer, LineageHistory
    >>>
    >>> history = LineageHistory(table_path="./lineage_history")
    >>> analyzer = HistoryAnalyzer(history)
    >>>
    >>> # Analyze trends
    >>> report = analyzer.analyze_trends(
    ...     pipeline_name="credit_scoring",
    ...     lookback_days=90
    ... )
    >>>
    >>> # Evaluate alert rules
    >>> alerts = analyzer.evaluate_alert_rules("alert_rules.yaml")
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .alert_rules import AlertRulesEngine
from .models import DriftAlert, TrendReport
from .notifiers import NotifierFactory
from .trend_analyzer import TrendAnalyzer
from .trend_visualizer import TrendVisualizer

logger = logging.getLogger(__name__)


class HistoryAnalyzer:
    """
    High-level analyzer for trend analysis and alerting.

    This class provides convenient methods for analyzing pipeline trends,
    evaluating alert rules, and sending notifications.
    """

    def __init__(
        self,
        history,
        default_metrics: Optional[List[str]] = None,
    ):
        """
        Initialize history analyzer.

        Args:
            history: LineageHistory instance
            default_metrics: Default metrics to analyze (default: common metrics)
        """
        self.history = history
        self.trend_analyzer = TrendAnalyzer(history)
        self.visualizer = TrendVisualizer()

        # Default metrics to analyze
        self.default_metrics = default_metrics or [
            "complexity_score",
            "row_count",
            "execution_time",
        ]

    def analyze_trends(
        self,
        pipeline_name: str,
        lookback_days: int = 90,
        metrics: Optional[List[str]] = None,
        environment: Optional[str] = None,
        detect_anomalies: bool = True,
    ) -> TrendReport:
        """
        Analyze trends for a pipeline across multiple metrics.

        Args:
            pipeline_name: Name of the pipeline
            lookback_days: Number of days to analyze (default: 90)
            metrics: List of metrics to analyze (default: self.default_metrics)
            environment: Optional environment filter
            detect_anomalies: Detect anomalies in metrics (default: True)

        Returns:
            TrendReport with complete analysis

        Example:
            >>> report = analyzer.analyze_trends(
            ...     pipeline_name="customer_etl",
            ...     lookback_days=30
            ... )
            >>> print(f"Analyzed {len(report.metric_analyses)} metrics")
            >>> if report.has_critical_issues():
            ...     print("CRITICAL issues found!")
        """
        try:
            logger.info(
                f"Analyzing trends for '{pipeline_name}' over {lookback_days} days"
            )

            metrics_to_analyze = metrics or self.default_metrics

            # Analyze each metric
            metric_analyses = []
            for metric_name in metrics_to_analyze:
                try:
                    analysis = self.trend_analyzer.analyze_metric_trend(
                        pipeline_name=pipeline_name,
                        metric_name=metric_name,
                        time_window_days=lookback_days,
                        detect_anomalies=detect_anomalies,
                    )
                    metric_analyses.append(analysis)
                except Exception as e:
                    logger.warning(
                        f"Failed to analyze metric '{metric_name}': {str(e)}"
                    )

            # Generate visualizations
            visualizations = {}
            for analysis in metric_analyses:
                if len(analysis.data_points) >= 2:
                    values = [dp.value for dp in analysis.data_points]
                    chart = self.visualizer.generate_ascii_chart(
                        values,
                        width=70,
                        height=15,
                        title=f"{analysis.metric_name} Trend",
                        show_values=True,
                    )
                    visualizations[analysis.metric_name] = chart

            # Calculate summary statistics
            summary_stats = self._calculate_summary_stats(metric_analyses)

            # Generate recommendations
            recommendations = self._generate_recommendations(metric_analyses)

            # Create trend report
            report = TrendReport(
                pipeline_name=pipeline_name,
                generated_at=datetime.now(),
                lookback_days=lookback_days,
                metric_analyses=metric_analyses,
                alerts_triggered=[],  # Populated by evaluate_alert_rules
                summary_stats=summary_stats,
                visualizations=visualizations,
                recommendations=recommendations,
            )

            logger.info(
                f"Trend analysis complete: {len(metric_analyses)} metrics analyzed, "
                f"{len(recommendations)} recommendations"
            )

            return report

        except Exception as e:
            logger.error(f"Failed to analyze trends: {str(e)}", exc_info=True)
            raise

    def evaluate_alert_rules(
        self,
        rules_config: Union[str, Path, List],
        pipeline_name: Optional[str] = None,
        lookback_days: int = 90,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate alert rules against pipeline trends.

        Args:
            rules_config: Path to YAML rules file or list of rule objects
            pipeline_name: Optional pipeline filter
            lookback_days: Time window for trend analysis (default: 90)
            environment: Optional environment filter

        Returns:
            Dictionary with alerts and evaluation summary

        Example:
            >>> results = analyzer.evaluate_alert_rules(
            ...     rules_config="alert_rules.yaml",
            ...     pipeline_name="customer_etl"
            ... )
            >>> print(f"Generated {len(results['alerts'])} alerts")
        """
        try:
            # Create rules engine
            engine = AlertRulesEngine()

            # Load rules
            if isinstance(rules_config, (str, Path)):
                engine.load_rules_from_yaml(rules_config)
            elif isinstance(rules_config, list):
                for rule in rules_config:
                    engine.add_rule(rule)
            else:
                raise ValueError("rules_config must be path or list of rules")

            # Get pipelines to analyze
            if pipeline_name:
                pipelines = [pipeline_name]
            else:
                # Get all pipelines from history
                stats = self.history.get_summary_statistics()
                pipelines = stats.get("pipelines", [])

            # Analyze trends for each pipeline
            all_alerts = []
            all_trend_analyses = []

            for pipeline in pipelines:
                try:
                    # Get trend analyses
                    for metric_name in self.default_metrics:
                        trend_analysis = self.trend_analyzer.analyze_metric_trend(
                            pipeline_name=pipeline,
                            metric_name=metric_name,
                            time_window_days=lookback_days,
                        )
                        all_trend_analyses.append(trend_analysis)

                except Exception as e:
                    logger.warning(
                        f"Failed to analyze pipeline '{pipeline}': {str(e)}"
                    )

            # Evaluate rules
            context = {"environment": environment} if environment else {}
            alerts = engine.evaluate_all(all_trend_analyses, context=context)
            all_alerts.extend(alerts)

            # Group alerts by severity
            alerts_by_severity = {
                "CRITICAL": [],
                "ERROR": [],
                "WARNING": [],
                "INFO": [],
            }

            for alert in all_alerts:
                severity_str = str(alert.severity)
                if severity_str in alerts_by_severity:
                    alerts_by_severity[severity_str].append(alert)

            result = {
                "total_alerts": len(all_alerts),
                "alerts": all_alerts,
                "alerts_by_severity": alerts_by_severity,
                "rules_evaluated": len(engine.rules),
                "pipelines_analyzed": len(pipelines),
                "metrics_analyzed": len(all_trend_analyses),
            }

            logger.info(
                f"Alert evaluation complete: {len(all_alerts)} alerts generated "
                f"from {len(engine.rules)} rules"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to evaluate alert rules: {str(e)}", exc_info=True)
            raise

    def generate_trend_dashboard(
        self,
        pipeline_names: List[str],
        lookback_days: int = 90,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Generate multi-pipeline trend dashboard.

        Args:
            pipeline_names: List of pipeline names
            lookback_days: Time window (default: 90 days)
            output_path: Optional path to save markdown report

        Returns:
            Markdown formatted dashboard

        Example:
            >>> dashboard = analyzer.generate_trend_dashboard(
            ...     pipeline_names=["pipeline_a", "pipeline_b"],
            ...     output_path="dashboard.md"
            ... )
        """
        try:
            lines = []

            # Header
            lines.append("# Pipeline Trends Dashboard")
            lines.append("")
            lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Time Window:** {lookback_days} days")
            lines.append(f"**Pipelines:** {len(pipeline_names)}")
            lines.append("")

            # Analyze each pipeline
            for pipeline_name in pipeline_names:
                try:
                    report = self.analyze_trends(
                        pipeline_name=pipeline_name,
                        lookback_days=lookback_days,
                    )

                    lines.append(f"## {pipeline_name}")
                    lines.append("")

                    # Summary
                    if report.has_critical_issues():
                        lines.append("**Status:** CRITICAL ISSUES DETECTED")
                    else:
                        lines.append("**Status:** OK")

                    lines.append("")

                    # Metrics table
                    trend_data = [
                        (analysis.metric_name, analysis)
                        for analysis in report.metric_analyses
                    ]
                    table = self.visualizer.generate_trend_table(trend_data)
                    lines.append(table)
                    lines.append("")

                    # Recommendations
                    if report.recommendations:
                        lines.append("### Recommendations")
                        lines.append("")
                        for rec in report.recommendations:
                            lines.append(f"- {rec}")
                        lines.append("")

                    lines.append("---")
                    lines.append("")

                except Exception as e:
                    logger.warning(
                        f"Failed to analyze pipeline '{pipeline_name}': {str(e)}"
                    )
                    lines.append(f"## {pipeline_name}")
                    lines.append("")
                    lines.append(f"**Error:** Failed to analyze pipeline")
                    lines.append("")

            dashboard = "\n".join(lines)

            # Save to file if requested
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(dashboard)
                logger.info(f"Dashboard saved to {output_path}")

            return dashboard

        except Exception as e:
            logger.error(f"Failed to generate dashboard: {str(e)}", exc_info=True)
            raise

    def send_notifications(
        self,
        alerts: List[DriftAlert],
        notifier_configs: Dict[str, Dict[str, Any]],
        dry_run: bool = False,
    ) -> Dict[str, int]:
        """
        Send alert notifications to configured destinations.

        Args:
            alerts: List of alerts to send
            notifier_configs: Dictionary mapping notifier names to configurations
            dry_run: If True, log instead of sending (default: False)

        Returns:
            Dictionary with send statistics

        Example:
            >>> results = analyzer.send_notifications(
            ...     alerts=alerts,
            ...     notifier_configs={
            ...         "slack": {"webhook_url": "https://..."},
            ...         "console": {}
            ...     },
            ...     dry_run=False
            ... )
        """
        try:
            stats = {"total_alerts": len(alerts), "sent": 0, "failed": 0}

            for alert in alerts:
                # Determine which notifiers to use
                notifier_names = alert.metadata.get("rule_name", {})

                for notifier_name in alert.metadata.get("notifiers", []):
                    if notifier_name not in notifier_configs:
                        logger.warning(
                            f"Notifier '{notifier_name}' not configured, skipping"
                        )
                        continue

                    try:
                        # Create notifier
                        config = notifier_configs[notifier_name].copy()
                        config["dry_run"] = dry_run

                        notifier = NotifierFactory.create_notifier(
                            notifier_name,
                            config
                        )

                        # Send alert
                        if notifier.send_alert(alert):
                            stats["sent"] += 1
                        else:
                            stats["failed"] += 1

                    except Exception as e:
                        logger.error(
                            f"Failed to send via {notifier_name}: {str(e)}"
                        )
                        stats["failed"] += 1

            logger.info(
                f"Notifications complete: {stats['sent']} sent, {stats['failed']} failed"
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to send notifications: {str(e)}", exc_info=True)
            raise

    def _calculate_summary_stats(self, metric_analyses: List) -> Dict[str, Any]:
        """Calculate summary statistics across all metrics."""
        total_anomalies = sum(
            len(analysis.anomalies) for analysis in metric_analyses
        )

        increasing_trends = sum(
            1 for analysis in metric_analyses
            if analysis.trend_direction == "increasing"
        )

        decreasing_trends = sum(
            1 for analysis in metric_analyses
            if analysis.trend_direction == "decreasing"
        )

        return {
            "total_metrics": len(metric_analyses),
            "total_anomalies": total_anomalies,
            "increasing_trends": increasing_trends,
            "decreasing_trends": decreasing_trends,
            "stable_trends": len(metric_analyses) - increasing_trends - decreasing_trends,
        }

    def _generate_recommendations(self, metric_analyses: List) -> List[str]:
        """Generate actionable recommendations based on trend analysis."""
        recommendations = []

        # Check for complexity growth
        for analysis in metric_analyses:
            if analysis.metric_name == "complexity_score":
                if analysis.trend_direction == "increasing" and analysis.growth_rate_percent > 30:
                    recommendations.append(
                        f"Complexity growing rapidly ({analysis.growth_rate_percent:.1f}%). "
                        "Consider refactoring to improve maintainability."
                    )

        # Check for performance regression
        for analysis in metric_analyses:
            if analysis.metric_name == "execution_time":
                if analysis.trend_direction == "increasing" and analysis.growth_rate_percent > 50:
                    recommendations.append(
                        f"Execution time increased {analysis.growth_rate_percent:.1f}%. "
                        "Profile pipeline for performance bottlenecks."
                    )

        # Check for anomalies
        critical_anomalies = sum(
            len(analysis.get_critical_anomalies())
            for analysis in metric_analyses
        )

        if critical_anomalies > 0:
            recommendations.append(
                f"Found {critical_anomalies} critical anomalies. "
                "Review data quality and pipeline stability."
            )

        if not recommendations:
            recommendations.append("No significant issues detected. Pipeline is healthy.")

        return recommendations
