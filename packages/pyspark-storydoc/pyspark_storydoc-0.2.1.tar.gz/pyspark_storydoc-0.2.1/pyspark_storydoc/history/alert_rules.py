"""
Alert rules engine for configurable alerting.

This module provides rule classes and an engine for evaluating alert conditions
based on trend analysis results.

Example:
    >>> from pyspark_storydoc.history.alert_rules import AlertRulesEngine, ThresholdRule
    >>> from pyspark_storydoc.history.models import AlertSeverity
    >>>
    >>> # Define rules
    >>> rules = [
    ...     ThresholdRule(
    ...         name="High Complexity",
    ...         metric_name="complexity_score",
    ...         threshold=10.0,
    ...         operator="greater_than",
    ...         severity=AlertSeverity.WARNING,
    ...         notifiers=["slack", "email"]
    ...     )
    ... ]
    >>>
    >>> # Evaluate rules
    >>> engine = AlertRulesEngine(rules)
    >>> alerts = engine.evaluate(trend_analysis)
"""

import logging
import yaml
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import AlertRule, AlertSeverity, DriftAlert, TrendAnalysis

logger = logging.getLogger(__name__)


class BaseAlertRule(ABC):
    """
    Base class for alert rules.

    All rule types must implement the evaluate() method.
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        severity: AlertSeverity,
        notifiers: List[str],
        enabled: bool = True,
        cooldown_minutes: int = 60,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize base alert rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            severity: Alert severity
            notifiers: List of notifier names
            enabled: Whether rule is active
            cooldown_minutes: Cooldown period between alerts
            metadata: Additional metadata
        """
        self.name = name
        self.metric_name = metric_name
        self.severity = severity
        self.notifiers = notifiers
        self.enabled = enabled
        self.cooldown_minutes = cooldown_minutes
        self.metadata = metadata or {}

    @abstractmethod
    def evaluate(
        self,
        trend_analysis: TrendAnalysis,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[DriftAlert]:
        """
        Evaluate rule against trend analysis.

        Args:
            trend_analysis: TrendAnalysis object
            context: Additional context

        Returns:
            DriftAlert if rule triggered, None otherwise
        """
        pass

    def _create_alert(
        self,
        pipeline_name: str,
        environment: str,
        title: str,
        message: str,
        recommendation: str,
        alert_type: str = "trend_alert",
        operation_id: Optional[str] = None,
        snapshot_id: Optional[str] = None,
    ) -> DriftAlert:
        """Create DriftAlert object."""
        from .models import AlertType
        import hashlib

        alert_id = hashlib.sha256(
            f"{self.name}_{pipeline_name}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Map alert_type string to AlertType enum
        alert_type_enum = AlertType.COMPLEXITY_GROWTH  # Default
        if alert_type == "performance_regression":
            alert_type_enum = AlertType.PERFORMANCE_REGRESSION
        elif alert_type == "anomaly":
            alert_type_enum = AlertType.DATA_QUALITY_ISSUE
        elif alert_type == "governance_drift":
            alert_type_enum = AlertType.GOVERNANCE_DRIFT

        return DriftAlert(
            alert_id=alert_id,
            alert_type=alert_type_enum,
            severity=self.severity,
            pipeline_name=pipeline_name,
            environment=environment,
            operation_id=operation_id,
            title=title,
            message=message,
            recommendation=recommendation,
            detected_at=datetime.now(),
            snapshot_id_a=snapshot_id,
            snapshot_id_b=None,
            metadata={
                "rule_name": self.name,
                "metric_name": self.metric_name,
                **self.metadata
            },
        )


class ThresholdRule(BaseAlertRule):
    """
    Alert when metric exceeds or falls below threshold.

    Example:
        >>> rule = ThresholdRule(
        ...     name="Complexity Limit",
        ...     metric_name="complexity_score",
        ...     threshold=10.0,
        ...     operator="greater_than",
        ...     severity=AlertSeverity.WARNING,
        ...     notifiers=["slack"]
        ... )
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        operator: str,
        severity: AlertSeverity,
        notifiers: List[str],
        **kwargs
    ):
        """
        Initialize threshold rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            threshold: Threshold value
            operator: Comparison operator (greater_than/less_than/equals)
            severity: Alert severity
            notifiers: List of notifier names
            **kwargs: Additional base class parameters
        """
        super().__init__(name, metric_name, severity, notifiers, **kwargs)
        self.threshold = threshold
        self.operator = operator

    def evaluate(
        self,
        trend_analysis: TrendAnalysis,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[DriftAlert]:
        """Evaluate threshold rule."""
        if not self.enabled:
            return None

        if trend_analysis.metric_name != self.metric_name:
            return None

        # Check latest value against threshold
        if not trend_analysis.data_points:
            return None

        latest_value = trend_analysis.data_points[-1].value

        triggered = False
        if self.operator == "greater_than":
            triggered = latest_value > self.threshold
        elif self.operator == "less_than":
            triggered = latest_value < self.threshold
        elif self.operator == "equals":
            triggered = abs(latest_value - self.threshold) < 0.0001
        elif self.operator == "greater_equal":
            triggered = latest_value >= self.threshold
        elif self.operator == "less_equal":
            triggered = latest_value <= self.threshold

        if not triggered:
            return None

        # Create alert
        title = f"{self.name}: Threshold Exceeded"
        message = (
            f"Metric '{self.metric_name}' value {latest_value:.2f} {self.operator.replace('_', ' ')} "
            f"threshold {self.threshold:.2f}"
        )
        recommendation = (
            f"Investigate why {self.metric_name} is {self.operator.replace('_', ' ')} {self.threshold:.2f}. "
            f"Review recent pipeline changes."
        )

        environment = context.get("environment", "unknown") if context else "unknown"

        return self._create_alert(
            pipeline_name=trend_analysis.pipeline_name,
            environment=environment,
            title=title,
            message=message,
            recommendation=recommendation,
            alert_type="threshold_exceeded",
            snapshot_id=trend_analysis.data_points[-1].snapshot_id,
        )


class TrendRule(BaseAlertRule):
    """
    Alert based on trend direction and growth rate.

    Example:
        >>> rule = TrendRule(
        ...     name="Complexity Growth",
        ...     metric_name="complexity_score",
        ...     trend_direction="increasing",
        ...     growth_rate_threshold=30.0,
        ...     severity=AlertSeverity.WARNING,
        ...     notifiers=["slack"]
        ... )
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        trend_direction: str,
        growth_rate_threshold: float,
        severity: AlertSeverity,
        notifiers: List[str],
        **kwargs
    ):
        """
        Initialize trend rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            trend_direction: Expected trend direction (increasing/decreasing)
            growth_rate_threshold: Growth rate threshold percentage
            severity: Alert severity
            notifiers: List of notifier names
            **kwargs: Additional base class parameters
        """
        super().__init__(name, metric_name, severity, notifiers, **kwargs)
        self.trend_direction = trend_direction
        self.growth_rate_threshold = growth_rate_threshold

    def evaluate(
        self,
        trend_analysis: TrendAnalysis,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[DriftAlert]:
        """Evaluate trend rule."""
        if not self.enabled:
            return None

        if trend_analysis.metric_name != self.metric_name:
            return None

        # Check trend direction
        if trend_analysis.trend_direction != self.trend_direction:
            return None

        # Check growth rate
        abs_growth = abs(trend_analysis.growth_rate_percent)
        if abs_growth < self.growth_rate_threshold:
            return None

        # Create alert
        title = f"{self.name}: Trend Alert"
        message = (
            f"Metric '{self.metric_name}' showing {trend_analysis.trend_direction} trend "
            f"with {trend_analysis.growth_rate_percent:.1f}% growth "
            f"(threshold: {self.growth_rate_threshold:.1f}%)"
        )
        recommendation = (
            f"Review {self.metric_name} trend over {trend_analysis.time_window_days} days. "
            f"Consider refactoring or optimization if trend continues."
        )

        environment = context.get("environment", "unknown") if context else "unknown"

        return self._create_alert(
            pipeline_name=trend_analysis.pipeline_name,
            environment=environment,
            title=title,
            message=message,
            recommendation=recommendation,
            alert_type="trend_detected",
        )


class AnomalyRule(BaseAlertRule):
    """
    Alert when statistical anomalies are detected.

    Example:
        >>> rule = AnomalyRule(
        ...     name="Performance Anomaly",
        ...     metric_name="execution_time",
        ...     min_severity=AlertSeverity.WARNING,
        ...     severity=AlertSeverity.ERROR,
        ...     notifiers=["slack"]
        ... )
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        severity: AlertSeverity,
        notifiers: List[str],
        min_severity: AlertSeverity = AlertSeverity.WARNING,
        **kwargs
    ):
        """
        Initialize anomaly rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            severity: Alert severity
            notifiers: List of notifier names
            min_severity: Minimum anomaly severity to trigger (default: WARNING)
            **kwargs: Additional base class parameters
        """
        super().__init__(name, metric_name, severity, notifiers, **kwargs)
        self.min_severity = min_severity

    def evaluate(
        self,
        trend_analysis: TrendAnalysis,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[DriftAlert]:
        """Evaluate anomaly rule."""
        if not self.enabled:
            return None

        if trend_analysis.metric_name != self.metric_name:
            return None

        # Filter anomalies by minimum severity
        significant_anomalies = [
            a for a in trend_analysis.anomalies
            if a.severity.priority >= self.min_severity.priority
        ]

        if not significant_anomalies:
            return None

        # Create alert for most recent severe anomaly
        latest_anomaly = significant_anomalies[-1]

        title = f"{self.name}: Anomaly Detected"
        message = (
            f"Statistical anomaly in '{self.metric_name}' detected. "
            f"Value {latest_anomaly.value:.2f} deviates {abs(latest_anomaly.deviation_std_devs):.1f} "
            f"standard deviations from expected {latest_anomaly.expected_value:.2f}. "
            f"Total anomalies in period: {len(significant_anomalies)}"
        )
        recommendation = (
            f"Investigate data quality issues or pipeline changes around "
            f"{latest_anomaly.timestamp.strftime('%Y-%m-%d %H:%M')}. "
            f"Check for upstream data source changes."
        )

        environment = context.get("environment", "unknown") if context else "unknown"

        return self._create_alert(
            pipeline_name=trend_analysis.pipeline_name,
            environment=environment,
            title=title,
            message=message,
            recommendation=recommendation,
            alert_type="anomaly",
            snapshot_id=latest_anomaly.snapshot_id,
        )


class CompositeRule(BaseAlertRule):
    """
    Combine multiple rules with AND/OR logic.

    Example:
        >>> rule = CompositeRule(
        ...     name="Critical Complexity",
        ...     metric_name="complexity_score",
        ...     severity=AlertSeverity.CRITICAL,
        ...     notifiers=["slack", "jira"],
        ...     rules=[threshold_rule, trend_rule],
        ...     logic="and"
        ... )
    """

    def __init__(
        self,
        name: str,
        metric_name: str,
        severity: AlertSeverity,
        notifiers: List[str],
        rules: List[BaseAlertRule],
        logic: str = "and",
        **kwargs
    ):
        """
        Initialize composite rule.

        Args:
            name: Rule name
            metric_name: Metric to monitor
            severity: Alert severity
            notifiers: List of notifier names
            rules: List of sub-rules to evaluate
            logic: Combination logic ("and" or "or", default: "and")
            **kwargs: Additional base class parameters
        """
        super().__init__(name, metric_name, severity, notifiers, **kwargs)
        self.rules = rules
        self.logic = logic.lower()

    def evaluate(
        self,
        trend_analysis: TrendAnalysis,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[DriftAlert]:
        """Evaluate composite rule."""
        if not self.enabled:
            return None

        if trend_analysis.metric_name != self.metric_name:
            return None

        # Evaluate all sub-rules
        results = [
            rule.evaluate(trend_analysis, context)
            for rule in self.rules
        ]

        # Apply logic
        triggered = False
        if self.logic == "and":
            triggered = all(result is not None for result in results)
        elif self.logic == "or":
            triggered = any(result is not None for result in results)

        if not triggered:
            return None

        # Combine messages from triggered rules
        triggered_rules = [r for r in results if r is not None]
        combined_message = "; ".join([r.message for r in triggered_rules])

        title = f"{self.name}: Composite Rule Triggered"
        message = f"Multiple conditions met ({self.logic.upper()}): {combined_message}"
        recommendation = "Review all flagged conditions and take appropriate action."

        environment = context.get("environment", "unknown") if context else "unknown"

        return self._create_alert(
            pipeline_name=trend_analysis.pipeline_name,
            environment=environment,
            title=title,
            message=message,
            recommendation=recommendation,
            alert_type="composite",
        )


class AlertRulesEngine:
    """
    Engine for evaluating alert rules against trend analysis.

    Example:
        >>> engine = AlertRulesEngine(rules=[rule1, rule2, rule3])
        >>> alerts = engine.evaluate_all(trend_analyses, context={"environment": "prod"})
    """

    def __init__(
        self,
        rules: Optional[List[BaseAlertRule]] = None,
    ):
        """
        Initialize alert rules engine.

        Args:
            rules: List of alert rules
        """
        self.rules = rules or []

    def add_rule(self, rule: BaseAlertRule):
        """Add a rule to the engine."""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove a rule by name."""
        self.rules = [r for r in self.rules if r.name != rule_name]

    def evaluate_all(
        self,
        trend_analyses: List[TrendAnalysis],
        context: Optional[Dict[str, Any]] = None
    ) -> List[DriftAlert]:
        """
        Evaluate all rules against all trend analyses.

        Args:
            trend_analyses: List of TrendAnalysis objects
            context: Optional context dictionary

        Returns:
            List of triggered alerts
        """
        alerts = []

        for trend_analysis in trend_analyses:
            for rule in self.rules:
                if not rule.enabled:
                    continue

                try:
                    alert = rule.evaluate(trend_analysis, context)
                    if alert:
                        alerts.append(alert)
                        logger.info(
                            f"Rule '{rule.name}' triggered for {trend_analysis.metric_name}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error evaluating rule '{rule.name}': {str(e)}",
                        exc_info=True
                    )

        logger.info(f"Evaluated {len(self.rules)} rules, generated {len(alerts)} alerts")
        return alerts

    def load_rules_from_yaml(self, yaml_path: Union[str, Path]):
        """
        Load alert rules from YAML configuration file.

        Args:
            yaml_path: Path to YAML configuration file

        Example YAML format:
            alert_rules:
              - name: "Complexity Growth Alert"
                metric: "complexity_score"
                rule_type: "threshold"
                threshold: 10
                operator: "greater_than"
                severity: "warning"
                notifiers: ["slack", "email"]
        """
        try:
            yaml_path = Path(yaml_path)
            if not yaml_path.exists():
                raise FileNotFoundError(f"Rules file not found: {yaml_path}")

            with open(yaml_path, "r") as f:
                config = yaml.safe_load(f)

            alert_rules_config = config.get("alert_rules", [])

            for rule_config in alert_rules_config:
                rule = self._create_rule_from_config(rule_config)
                if rule:
                    self.add_rule(rule)

            logger.info(f"Loaded {len(alert_rules_config)} rules from {yaml_path}")

        except Exception as e:
            logger.error(f"Failed to load rules from YAML: {str(e)}", exc_info=True)
            raise

    def _create_rule_from_config(self, config: Dict[str, Any]) -> Optional[BaseAlertRule]:
        """Create rule instance from configuration dictionary."""
        try:
            rule_type = config.get("rule_type", "threshold")
            name = config["name"]
            metric_name = config["metric"]
            severity = AlertSeverity[config["severity"].upper()]
            notifiers = config.get("notifiers", [])
            enabled = config.get("enabled", True)

            if rule_type == "threshold":
                return ThresholdRule(
                    name=name,
                    metric_name=metric_name,
                    threshold=config["threshold"],
                    operator=config["operator"],
                    severity=severity,
                    notifiers=notifiers,
                    enabled=enabled,
                )
            elif rule_type == "trend":
                return TrendRule(
                    name=name,
                    metric_name=metric_name,
                    trend_direction=config["trend_direction"],
                    growth_rate_threshold=config["growth_rate_threshold"],
                    severity=severity,
                    notifiers=notifiers,
                    enabled=enabled,
                )
            elif rule_type == "anomaly":
                min_severity_str = config.get("min_severity", "WARNING")
                min_severity = AlertSeverity[min_severity_str.upper()]
                return AnomalyRule(
                    name=name,
                    metric_name=metric_name,
                    severity=severity,
                    notifiers=notifiers,
                    min_severity=min_severity,
                    enabled=enabled,
                )
            else:
                logger.warning(f"Unknown rule type: {rule_type}")
                return None

        except Exception as e:
            logger.error(f"Failed to create rule from config: {str(e)}", exc_info=True)
            return None
