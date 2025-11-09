"""Custom exceptions for PySpark StoryDoc."""

from typing import Any, Optional


class PySparkStoryDocError(Exception):
    """Base exception for all PySpark StoryDoc errors."""

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional additional details about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class LineageTrackingError(PySparkStoryDocError):
    """Exception raised during lineage tracking operations."""

    def __init__(
        self,
        message: str,
        operation_type: Optional[str] = None,
        dataframe_info: Optional[dict] = None,
    ) -> None:
        """
        Initialize lineage tracking error.

        Args:
            message: Error message
            operation_type: Type of operation that failed (filter, join, etc.)
            dataframe_info: Information about the DataFrame that caused the error
        """
        details = {}
        if operation_type:
            details["operation_type"] = operation_type
        if dataframe_info:
            details["dataframe_info"] = dataframe_info

        super().__init__(message, details)
        self.operation_type = operation_type
        self.dataframe_info = dataframe_info


class InferenceError(PySparkStoryDocError):
    """Exception raised during business context inference."""

    def __init__(
        self,
        message: str,
        column_names: Optional[list] = None,
        operation_details: Optional[dict] = None,
    ) -> None:
        """
        Initialize inference error.

        Args:
            message: Error message
            column_names: Column names involved in the failed inference
            operation_details: Details about the operation being analyzed
        """
        details = {}
        if column_names:
            details["column_names"] = column_names
        if operation_details:
            details["operation_details"] = operation_details

        super().__init__(message, details)
        self.column_names = column_names
        self.operation_details = operation_details


class VisualizationError(PySparkStoryDocError):
    """Exception raised during visualization generation."""

    def __init__(
        self,
        message: str,
        renderer_type: Optional[str] = None,
        graph_info: Optional[dict] = None,
    ) -> None:
        """
        Initialize visualization error.

        Args:
            message: Error message
            renderer_type: Type of renderer that failed (mermaid, graphviz)
            graph_info: Information about the graph being rendered
        """
        details = {}
        if renderer_type:
            details["renderer_type"] = renderer_type
        if graph_info:
            details["graph_info"] = graph_info

        super().__init__(message, details)
        self.renderer_type = renderer_type
        self.graph_info = graph_info


class ConfigurationError(PySparkStoryDocError):
    """Exception raised for configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
    ) -> None:
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_value: Invalid configuration value
        """
        details = {}
        if config_key:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = config_value

        super().__init__(message, details)
        self.config_key = config_key
        self.config_value = config_value


class MaterializationError(LineageTrackingError):
    """Exception raised when DataFrame materialization fails."""

    def __init__(
        self,
        message: str,
        estimated_size: Optional[int] = None,
    ) -> None:
        """
        Initialize materialization error.

        Args:
            message: Error message
            estimated_size: Estimated DataFrame size
        """
        details = {}
        if estimated_size is not None:
            details["estimated_size"] = estimated_size

        super().__init__(message, "materialization", details)
        self.estimated_size = estimated_size


class ValidationError(PySparkStoryDocError):
    """Exception raised for input validation errors."""

    def __init__(
        self,
        message: str,
        parameter_name: Optional[str] = None,
        parameter_value: Optional[Any] = None,
        expected_type: Optional[type] = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            parameter_name: Name of the invalid parameter
            parameter_value: Invalid parameter value
            expected_type: Expected type for the parameter
        """
        details = {}
        if parameter_name:
            details["parameter_name"] = parameter_name
        if parameter_value is not None:
            details["parameter_value"] = parameter_value
        if expected_type:
            details["expected_type"] = expected_type.__name__

        super().__init__(message, details)
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        self.expected_type = expected_type