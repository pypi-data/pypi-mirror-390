"""
Trend analysis for lineage metrics over time.

This module provides statistical analysis of metric trends including:
- Linear regression for trend direction
- Moving averages (simple and exponential)
- Anomaly detection using Z-score method
- Growth rate calculations
- Future value predictions

Example:
    >>> from pyspark_storydoc.history import LineageHistory, TrendAnalyzer
    >>>
    >>> history = LineageHistory(table_path="./lineage_history")
    >>> analyzer = TrendAnalyzer(history)
    >>>
    >>> # Analyze complexity trend
    >>> trend = analyzer.analyze_metric_trend(
    ...     pipeline_name="credit_scoring",
    ...     metric_name="complexity_score",
    ...     time_window_days=90
    ... )
    >>>
    >>> print(f"Trend: {trend.trend_direction}")
    >>> print(f"Growth: {trend.growth_rate_percent:.1f}%")
    >>> print(f"Anomalies detected: {len(trend.anomalies)}")
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

from .models import Anomaly, AlertSeverity, MetricPoint, TrendAnalysis

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Analyze metrics over time to identify trends, anomalies, and patterns.

    This class provides statistical analysis capabilities for lineage metrics
    including trend detection, anomaly identification, and growth rate calculation.
    """

    def __init__(self, history):
        """
        Initialize trend analyzer.

        Args:
            history: LineageHistory instance for querying snapshots
        """
        self.history = history

    def analyze_metric_trend(
        self,
        pipeline_name: str,
        metric_name: str,
        time_window_days: int = 90,
        detect_anomalies: bool = True,
        anomaly_threshold_std_devs: float = 2.0,
    ) -> TrendAnalysis:
        """
        Analyze trend for a specific metric over time.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric to analyze
            time_window_days: Number of days to analyze (default: 90)
            detect_anomalies: Whether to detect anomalies (default: True)
            anomaly_threshold_std_devs: Z-score threshold for anomalies (default: 2.0)

        Returns:
            TrendAnalysis object with complete analysis results

        Example:
            >>> trend = analyzer.analyze_metric_trend(
            ...     pipeline_name="customer_etl",
            ...     metric_name="execution_time",
            ...     time_window_days=30
            ... )
            >>> if trend.trend_direction == "increasing":
            ...     print(f"Performance degrading: {trend.growth_rate_percent:.1f}%")
        """
        try:
            logger.info(
                f"Analyzing trend for {pipeline_name}.{metric_name} "
                f"over {time_window_days} days"
            )

            # Get metric history
            data_points = self.get_metric_history(
                pipeline_name=pipeline_name,
                metric_name=metric_name,
                time_window_days=time_window_days,
            )

            if len(data_points) < 2:
                logger.warning(
                    f"Insufficient data points for trend analysis: {len(data_points)}"
                )
                return self._create_empty_trend_analysis(
                    metric_name, pipeline_name, time_window_days, data_points
                )

            # Calculate statistics
            values = np.array([dp.value for dp in data_points])
            mean = float(np.mean(values))
            std_dev = float(np.std(values))
            min_value = float(np.min(values))
            max_value = float(np.max(values))

            # Calculate trend using linear regression
            trend_direction, slope, r_squared, confidence = self._calculate_trend(values)

            # Calculate growth rate
            growth_rate_percent = self._calculate_growth_rate(values)

            # Detect anomalies if requested
            anomalies = []
            if detect_anomalies and len(data_points) >= 5:
                anomalies = self.detect_anomalies(
                    pipeline_name=pipeline_name,
                    metric_name=metric_name,
                    data_points=data_points,
                    threshold_std_devs=anomaly_threshold_std_devs,
                )

            # Create trend analysis result
            trend_analysis = TrendAnalysis(
                metric_name=metric_name,
                pipeline_name=pipeline_name,
                time_window_days=time_window_days,
                data_points=data_points,
                trend_direction=trend_direction,
                growth_rate_percent=growth_rate_percent,
                mean=mean,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                anomalies=anomalies,
                confidence=confidence,
                slope=slope,
                r_squared=r_squared,
            )

            logger.info(
                f"Trend analysis complete: {trend_direction} trend "
                f"({growth_rate_percent:.1f}% growth, {len(anomalies)} anomalies)"
            )

            return trend_analysis

        except Exception as e:
            logger.error(
                f"Failed to analyze metric trend: {str(e)}",
                exc_info=True
            )
            raise

    def get_metric_history(
        self,
        pipeline_name: str,
        metric_name: str,
        time_window_days: int,
        environment: Optional[str] = None,
    ) -> List[MetricPoint]:
        """
        Retrieve metric history from lineage snapshots.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            time_window_days: Number of days to retrieve
            environment: Optional environment filter

        Returns:
            List of MetricPoint objects ordered by timestamp

        Example:
            >>> points = analyzer.get_metric_history(
            ...     pipeline_name="customer_etl",
            ...     metric_name="row_count",
            ...     time_window_days=7
            ... )
            >>> for point in points:
            ...     print(f"{point.timestamp}: {point.value}")
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_window_days)
            start_date_str = start_date.strftime("%Y-%m-%d")

            # Get snapshots in time window
            snapshots = self.history.list_snapshots(
                pipeline_name=pipeline_name,
                environment=environment,
                start_date=start_date_str,
                include_details=True,
            )

            logger.debug(
                f"Retrieved {len(snapshots)} snapshots for metric history"
            )

            # Extract metric values
            data_points = []
            for snapshot in snapshots:
                # Look for metric in snapshot metrics
                metrics = snapshot.get("metrics", [])
                for metric in metrics:
                    if metric.get("metric_name") == metric_name:
                        # Parse timestamp
                        timestamp_str = snapshot.get("captured_at")
                        if isinstance(timestamp_str, str):
                            timestamp = datetime.fromisoformat(timestamp_str)
                        else:
                            timestamp = timestamp_str

                        data_point = MetricPoint(
                            timestamp=timestamp,
                            value=float(metric.get("metric_value", 0)),
                            snapshot_id=snapshot["snapshot_id"],
                            metadata=metric.get("metadata", {}),
                        )
                        data_points.append(data_point)
                        break

            # Sort by timestamp
            data_points.sort(key=lambda dp: dp.timestamp)

            logger.debug(f"Extracted {len(data_points)} metric data points")

            return data_points

        except Exception as e:
            logger.error(
                f"Failed to get metric history: {str(e)}",
                exc_info=True
            )
            raise

    def detect_anomalies(
        self,
        pipeline_name: str,
        metric_name: str,
        data_points: Optional[List[MetricPoint]] = None,
        threshold_std_devs: float = 2.0,
        time_window_days: int = 90,
    ) -> List[Anomaly]:
        """
        Detect statistical anomalies in metric data using Z-score method.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            data_points: Optional pre-loaded data points (if None, will fetch)
            threshold_std_devs: Z-score threshold (default: 2.0)
            time_window_days: Time window for fetching data (if data_points is None)

        Returns:
            List of Anomaly objects for values exceeding threshold

        Example:
            >>> anomalies = analyzer.detect_anomalies(
            ...     pipeline_name="customer_etl",
            ...     metric_name="execution_time",
            ...     threshold_std_devs=2.5
            ... )
            >>> for anomaly in anomalies:
            ...     print(f"Anomaly at {anomaly.timestamp}: {anomaly.deviation_std_devs:.1f}σ")
        """
        try:
            # Fetch data if not provided
            if data_points is None:
                data_points = self.get_metric_history(
                    pipeline_name=pipeline_name,
                    metric_name=metric_name,
                    time_window_days=time_window_days,
                )

            if len(data_points) < 5:
                logger.warning(
                    f"Insufficient data for anomaly detection: {len(data_points)} points"
                )
                return []

            # Calculate statistics
            values = np.array([dp.value for dp in data_points])
            mean = np.mean(values)
            std_dev = np.std(values)

            if std_dev == 0:
                logger.warning("Zero standard deviation - cannot detect anomalies")
                return []

            # Calculate Z-scores
            z_scores = (values - mean) / std_dev

            # Identify anomalies
            anomalies = []
            for i, (dp, z_score) in enumerate(zip(data_points, z_scores)):
                abs_z_score = abs(z_score)
                if abs_z_score >= threshold_std_devs:
                    # Calculate expected value (using moving average of neighbors)
                    expected_value = self._calculate_expected_value(values, i)

                    # Determine severity based on z-score magnitude
                    if abs_z_score >= 3.0:
                        severity = AlertSeverity.CRITICAL
                    elif abs_z_score >= 2.5:
                        severity = AlertSeverity.ERROR
                    elif abs_z_score >= 2.0:
                        severity = AlertSeverity.WARNING
                    else:
                        severity = AlertSeverity.INFO

                    anomaly = Anomaly(
                        timestamp=dp.timestamp,
                        value=dp.value,
                        expected_value=expected_value,
                        deviation_std_devs=float(z_score),
                        severity=severity,
                        metric_name=metric_name,
                        snapshot_id=dp.snapshot_id,
                    )
                    anomalies.append(anomaly)

            logger.info(
                f"Detected {len(anomalies)} anomalies in {metric_name} "
                f"(threshold: {threshold_std_devs}σ)"
            )

            return anomalies

        except Exception as e:
            logger.error(
                f"Failed to detect anomalies: {str(e)}",
                exc_info=True
            )
            raise

    def calculate_growth_rate(
        self,
        pipeline_name: str,
        metric_name: str,
        time_window_days: int = 90,
    ) -> float:
        """
        Calculate growth rate for a metric over time window.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            time_window_days: Time window in days (default: 90)

        Returns:
            Growth rate as percentage (e.g., 25.5 for 25.5% growth)

        Example:
            >>> growth = analyzer.calculate_growth_rate(
            ...     pipeline_name="customer_etl",
            ...     metric_name="complexity_score",
            ...     time_window_days=30
            ... )
            >>> print(f"Complexity grew by {growth:.1f}% in 30 days")
        """
        try:
            data_points = self.get_metric_history(
                pipeline_name=pipeline_name,
                metric_name=metric_name,
                time_window_days=time_window_days,
            )

            if len(data_points) < 2:
                return 0.0

            values = np.array([dp.value for dp in data_points])
            return self._calculate_growth_rate(values)

        except Exception as e:
            logger.error(
                f"Failed to calculate growth rate: {str(e)}",
                exc_info=True
            )
            raise

    def predict_future_value(
        self,
        pipeline_name: str,
        metric_name: str,
        days_ahead: int,
        time_window_days: int = 90,
    ) -> float:
        """
        Predict future metric value using linear regression.

        Args:
            pipeline_name: Name of the pipeline
            metric_name: Name of the metric
            days_ahead: Number of days to predict ahead
            time_window_days: Historical time window for trend calculation

        Returns:
            Predicted metric value

        Example:
            >>> predicted = analyzer.predict_future_value(
            ...     pipeline_name="customer_etl",
            ...     metric_name="execution_time",
            ...     days_ahead=30
            ... )
            >>> print(f"Predicted execution time in 30 days: {predicted:.2f}s")
        """
        try:
            data_points = self.get_metric_history(
                pipeline_name=pipeline_name,
                metric_name=metric_name,
                time_window_days=time_window_days,
            )

            if len(data_points) < 2:
                logger.warning("Insufficient data for prediction")
                return 0.0

            values = np.array([dp.value for dp in data_points])
            x = np.arange(len(values))

            # Linear regression
            coefficients = np.polyfit(x, values, 1)
            slope = coefficients[0]
            intercept = coefficients[1]

            # Predict future value
            future_x = len(values) + (days_ahead * len(values) / time_window_days)
            predicted_value = slope * future_x + intercept

            logger.info(
                f"Predicted {metric_name} value in {days_ahead} days: {predicted_value:.2f}"
            )

            return float(predicted_value)

        except Exception as e:
            logger.error(
                f"Failed to predict future value: {str(e)}",
                exc_info=True
            )
            raise

    def calculate_moving_average(
        self,
        values: np.ndarray,
        window_size: int = 7,
        method: str = "simple",
    ) -> np.ndarray:
        """
        Calculate moving average for metric values.

        Args:
            values: Array of metric values
            window_size: Size of moving window (default: 7)
            method: "simple" for SMA or "exponential" for EMA (default: "simple")

        Returns:
            Array of moving average values

        Example:
            >>> values = np.array([10, 12, 11, 13, 15, 14, 16])
            >>> ma = analyzer.calculate_moving_average(values, window_size=3)
            >>> print(ma)
        """
        try:
            if method == "simple":
                # Simple Moving Average (SMA)
                return self._simple_moving_average(values, window_size)
            elif method == "exponential":
                # Exponential Moving Average (EMA)
                return self._exponential_moving_average(values, window_size)
            else:
                raise ValueError(f"Unknown moving average method: {method}")

        except Exception as e:
            logger.error(
                f"Failed to calculate moving average: {str(e)}",
                exc_info=True
            )
            raise

    def _calculate_trend(
        self,
        values: np.ndarray
    ) -> tuple[str, float, float, float]:
        """
        Calculate trend direction using linear regression.

        Returns:
            Tuple of (trend_direction, slope, r_squared, confidence)
        """
        if len(values) < 2:
            return "stable", 0.0, 0.0, 0.0

        x = np.arange(len(values))

        # Linear regression
        coefficients = np.polyfit(x, values, 1)
        slope = coefficients[0]
        intercept = coefficients[1]

        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)

        if ss_tot == 0:
            r_squared = 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)

        # Determine trend direction
        mean_value = np.mean(values)
        if mean_value == 0:
            relative_slope = 0
        else:
            relative_slope = slope / mean_value

        # Confidence based on R-squared and relative slope
        confidence = r_squared * min(abs(relative_slope) * 10, 1.0)

        # Classify trend
        if confidence < 0.3:
            trend_direction = "stable"
        elif slope > 0:
            trend_direction = "increasing"
        else:
            trend_direction = "decreasing"

        return trend_direction, float(slope), float(r_squared), float(confidence)

    def _calculate_growth_rate(self, values: np.ndarray) -> float:
        """Calculate percentage growth rate from first to last value."""
        if len(values) < 2:
            return 0.0

        first_value = values[0]
        last_value = values[-1]

        if first_value == 0:
            return 0.0

        growth_rate = ((last_value - first_value) / first_value) * 100
        return float(growth_rate)

    def _calculate_expected_value(self, values: np.ndarray, index: int) -> float:
        """Calculate expected value using moving average of neighbors."""
        window_size = 5
        start = max(0, index - window_size // 2)
        end = min(len(values), index + window_size // 2 + 1)

        # Exclude the current value
        window_values = np.concatenate([
            values[start:index],
            values[index+1:end]
        ])

        if len(window_values) == 0:
            return float(np.mean(values))

        return float(np.mean(window_values))

    def _simple_moving_average(self, values: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate simple moving average."""
        if len(values) < window_size:
            return np.full(len(values), np.mean(values))

        ma = np.convolve(values, np.ones(window_size) / window_size, mode='same')

        # Fix edge effects
        for i in range(window_size // 2):
            ma[i] = np.mean(values[:i+window_size//2+1])
            ma[-(i+1)] = np.mean(values[-(i+window_size//2+1):])

        return ma

    def _exponential_moving_average(
        self,
        values: np.ndarray,
        window_size: int
    ) -> np.ndarray:
        """Calculate exponential moving average."""
        alpha = 2.0 / (window_size + 1)
        ema = np.zeros(len(values))
        ema[0] = values[0]

        for i in range(1, len(values)):
            ema[i] = alpha * values[i] + (1 - alpha) * ema[i-1]

        return ema

    def _create_empty_trend_analysis(
        self,
        metric_name: str,
        pipeline_name: str,
        time_window_days: int,
        data_points: List[MetricPoint],
    ) -> TrendAnalysis:
        """Create empty trend analysis for insufficient data."""
        values = np.array([dp.value for dp in data_points]) if data_points else np.array([])

        return TrendAnalysis(
            metric_name=metric_name,
            pipeline_name=pipeline_name,
            time_window_days=time_window_days,
            data_points=data_points,
            trend_direction="stable",
            growth_rate_percent=0.0,
            mean=float(np.mean(values)) if len(values) > 0 else 0.0,
            std_dev=0.0,
            min_value=float(np.min(values)) if len(values) > 0 else 0.0,
            max_value=float(np.max(values)) if len(values) > 0 else 0.0,
            anomalies=[],
            confidence=0.0,
            slope=0.0,
            r_squared=0.0,
        )
