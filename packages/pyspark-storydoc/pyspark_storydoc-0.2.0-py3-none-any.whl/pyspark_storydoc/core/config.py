"""Configuration management for PySpark StoryDoc with zero-overhead mode support."""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class TrackingMode(Enum):
    """Tracking mode configuration."""
    FULL = "full"  # Full tracking with all features
    LIGHTWEIGHT = "lightweight"  # Basic tracking, minimal overhead
    ZERO_OVERHEAD = "zero_overhead"  # No tracking, production mode
    DEBUG = "debug"  # Full tracking with extensive logging


class RowCountTrackingLevel(Enum):
    """Row count tracking granularity."""
    BUSINESS_CONCEPT = "business_concept"  # Track at first and last operation only (more performant)
    OPERATION = "operation"  # Track at every operation (more detailed but expensive)


@dataclass
class TrackingConfig:
    """Configuration for lineage tracking behavior."""

    # Core tracking settings
    mode: TrackingMode = TrackingMode.FULL
    materialize_by_default: bool = True
    auto_infer_context: bool = True
    track_row_count_level: RowCountTrackingLevel = RowCountTrackingLevel.BUSINESS_CONCEPT

    # Fork detection settings
    enable_fork_detection: bool = True
    fork_caching_threshold: int = 2  # Cache after N consumers

    # Performance settings
    max_tracked_columns: int = 10
    materialization_timeout: float = 30.0  # seconds
    enable_async_metrics: bool = False

    # Column tracking
    default_track_columns: List[str] = field(default_factory=list)
    track_columns_by_pattern: List[str] = field(default_factory=list)  # regex patterns

    # Visualization settings
    enable_visualization: bool = True
    include_fork_styling: bool = True
    include_merge_styling: bool = True
    diagram_max_nodes: int = 100

    # Debugging and logging
    log_level: str = "INFO"
    debug_mode: bool = False
    capture_function_signatures: bool = True

    # Storage and export
    enable_json_export: bool = True
    enable_markdown_export: bool = True
    export_directory: Optional[str] = None

    @classmethod
    def zero_overhead(cls) -> 'TrackingConfig':
        """Create a zero-overhead configuration for production."""
        return cls(
            mode=TrackingMode.ZERO_OVERHEAD,
            materialize_by_default=False,
            auto_infer_context=False,
            enable_fork_detection=False,
            enable_visualization=False,
            enable_async_metrics=False,
            debug_mode=False,
            capture_function_signatures=False,
            enable_json_export=False,
            enable_markdown_export=False
        )

    @classmethod
    def lightweight(cls) -> 'TrackingConfig':
        """Create a lightweight configuration for development."""
        return cls(
            mode=TrackingMode.LIGHTWEIGHT,
            materialize_by_default=False,
            auto_infer_context=True,
            enable_fork_detection=True,
            max_tracked_columns=5,
            enable_async_metrics=True,
            debug_mode=False
        )

    @classmethod
    def debug(cls) -> 'TrackingConfig':
        """Create a debug configuration with extensive tracking."""
        return cls(
            mode=TrackingMode.DEBUG,
            materialize_by_default=True,
            auto_infer_context=True,
            enable_fork_detection=True,
            debug_mode=True,
            log_level="DEBUG",
            capture_function_signatures=True,
            enable_json_export=True,
            enable_markdown_export=True
        )

    @classmethod
    def from_environment(cls) -> 'TrackingConfig':
        """Create configuration from environment variables."""
        config = cls()

        # Parse environment variables
        if mode_str := os.getenv('PYSPARK_STORYDOC_MODE'):
            try:
                config.mode = TrackingMode(mode_str.lower())
            except ValueError:
                logger.warning(f"Invalid tracking mode: {mode_str}, using default")

        config.materialize_by_default = _parse_bool_env('PYSPARK_STORYDOC_MATERIALIZE', config.materialize_by_default)
        config.enable_fork_detection = _parse_bool_env('PYSPARK_STORYDOC_FORK_DETECTION', config.enable_fork_detection)
        config.debug_mode = _parse_bool_env('PYSPARK_STORYDOC_DEBUG', config.debug_mode)

        if columns_str := os.getenv('PYSPARK_STORYDOC_TRACK_COLUMNS'):
            config.default_track_columns = [col.strip() for col in columns_str.split(',')]

        if export_dir := os.getenv('PYSPARK_STORYDOC_EXPORT_DIR'):
            config.export_directory = export_dir

        if timeout_str := os.getenv('PYSPARK_STORYDOC_TIMEOUT'):
            try:
                config.materialization_timeout = float(timeout_str)
            except ValueError:
                logger.warning(f"Invalid timeout value: {timeout_str}, using default")

        return config

    def apply_mode_defaults(self) -> None:
        """Apply default settings based on the selected mode."""
        if self.mode == TrackingMode.ZERO_OVERHEAD:
            self.materialize_by_default = False
            self.enable_fork_detection = False
            self.enable_visualization = False
            self.debug_mode = False

        elif self.mode == TrackingMode.LIGHTWEIGHT:
            self.materialize_by_default = False
            self.max_tracked_columns = 5
            self.enable_async_metrics = True

        elif self.mode == TrackingMode.DEBUG:
            self.materialize_by_default = True
            self.debug_mode = True
            self.log_level = "DEBUG"
            self.capture_function_signatures = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'mode': self.mode.value,
            'materialize_by_default': self.materialize_by_default,
            'auto_infer_context': self.auto_infer_context,
            'track_row_count_level': self.track_row_count_level.value,
            'enable_fork_detection': self.enable_fork_detection,
            'fork_caching_threshold': self.fork_caching_threshold,
            'max_tracked_columns': self.max_tracked_columns,
            'materialization_timeout': self.materialization_timeout,
            'enable_async_metrics': self.enable_async_metrics,
            'default_track_columns': self.default_track_columns,
            'track_columns_by_pattern': self.track_columns_by_pattern,
            'enable_visualization': self.enable_visualization,
            'include_fork_styling': self.include_fork_styling,
            'include_merge_styling': self.include_merge_styling,
            'diagram_max_nodes': self.diagram_max_nodes,
            'log_level': self.log_level,
            'debug_mode': self.debug_mode,
            'capture_function_signatures': self.capture_function_signatures,
            'enable_json_export': self.enable_json_export,
            'enable_markdown_export': self.enable_markdown_export,
            'export_directory': self.export_directory
        }


def _parse_bool_env(env_var: str, default: bool) -> bool:
    """Parse boolean environment variable."""
    value = os.getenv(env_var, '').lower()
    if value in ('true', '1', 'yes', 'on'):
        return True
    elif value in ('false', '0', 'no', 'off'):
        return False
    else:
        return default


class GlobalConfig:
    """Global configuration manager for PySpark StoryDoc."""

    def __init__(self):
        self._config = TrackingConfig()
        self._initialized = False

    def initialize(self, config: Optional[TrackingConfig] = None) -> None:
        """Initialize global configuration."""
        if config is None:
            # Try to load from environment first
            config = TrackingConfig.from_environment()

        self._config = config
        self._config.apply_mode_defaults()
        self._initialized = True

        # Configure logging
        self._configure_logging()

        logger.info(f"Initialized PySpark StoryDoc with mode: {config.mode.value}")

    def get_config(self) -> TrackingConfig:
        """Get the current configuration."""
        if not self._initialized:
            self.initialize()
        return self._config

    def set_config(self, config: TrackingConfig) -> None:
        """Set a new configuration."""
        self._config = config
        config.apply_mode_defaults()
        self._configure_logging()
        logger.info(f"Updated configuration to mode: {config.mode.value}")

    def update_config(self, **kwargs) -> None:
        """Update specific configuration parameters."""
        if not self._initialized:
            self.initialize()

        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
            else:
                logger.warning(f"Unknown configuration parameter: {key}")

        self._config.apply_mode_defaults()
        self._configure_logging()

    def enable_zero_overhead_mode(self) -> None:
        """Enable zero-overhead mode."""
        self.set_config(TrackingConfig.zero_overhead())

    def enable_lightweight_mode(self) -> None:
        """Enable lightweight mode."""
        self.set_config(TrackingConfig.lightweight())

    def enable_debug_mode(self) -> None:
        """Enable debug mode."""
        self.set_config(TrackingConfig.debug())

    def is_tracking_enabled(self) -> bool:
        """Check if tracking is enabled."""
        config = self.get_config()
        return config.mode != TrackingMode.ZERO_OVERHEAD

    def should_materialize(self) -> bool:
        """Check if materialization should occur by default."""
        config = self.get_config()
        return self.is_tracking_enabled() and config.materialize_by_default

    def should_detect_forks(self) -> bool:
        """Check if fork detection should be enabled."""
        config = self.get_config()
        return self.is_tracking_enabled() and config.enable_fork_detection

    def _configure_logging(self) -> None:
        """Configure logging based on configuration."""
        if self._config.debug_mode:
            level = logging.DEBUG
        else:
            level = getattr(logging, self._config.log_level.upper(), logging.INFO)

        # Configure the pyspark_storydoc logger
        storydoc_logger = logging.getLogger('pyspark_storydoc')
        storydoc_logger.setLevel(level)

        # Add handler if none exists
        if not storydoc_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            storydoc_logger.addHandler(handler)


# Global configuration instance
_global_config = GlobalConfig()


def get_config() -> TrackingConfig:
    """Get the global configuration."""
    return _global_config.get_config()


def set_config(config: TrackingConfig) -> None:
    """Set the global configuration."""
    _global_config.set_config(config)


def update_config(**kwargs) -> None:
    """Update specific configuration parameters."""
    _global_config.update_config(**kwargs)


def enable_zero_overhead_mode() -> None:
    """Enable zero-overhead mode globally."""
    _global_config.enable_zero_overhead_mode()


def enable_lightweight_mode() -> None:
    """Enable lightweight mode globally."""
    _global_config.enable_lightweight_mode()


def enable_debug_mode() -> None:
    """Enable debug mode globally."""
    _global_config.enable_debug_mode()


def is_tracking_enabled() -> bool:
    """Check if tracking is enabled globally."""
    return _global_config.is_tracking_enabled()


def should_materialize() -> bool:
    """Check if materialization should occur by default."""
    return _global_config.should_materialize()


def should_detect_forks() -> bool:
    """Check if fork detection should be enabled."""
    return _global_config.should_detect_forks()


# Configuration shortcuts for common use cases
def configure_for_production():
    """Configure for production use with zero overhead."""
    enable_zero_overhead_mode()
    logger.info("Configured PySpark StoryDoc for production (zero overhead)")


def configure_for_development():
    """Configure for development use with lightweight tracking."""
    enable_lightweight_mode()
    logger.info("Configured PySpark StoryDoc for development (lightweight)")


def configure_for_debugging():
    """Configure for debugging with full tracking and logging."""
    enable_debug_mode()
    logger.info("Configured PySpark StoryDoc for debugging (full tracking)")


# Environment-based auto-configuration
def auto_configure():
    """Automatically configure based on environment."""
    # Check for common production indicators
    if (os.getenv('ENVIRONMENT') == 'production' or
        os.getenv('ENV') == 'prod' or
        os.getenv('STAGE') == 'production'):
        configure_for_production()
        return

    # Check for debug indicators
    if (os.getenv('DEBUG') == 'true' or
        os.getenv('PYSPARK_STORYDOC_DEBUG') == 'true'):
        configure_for_debugging()
        return

    # Default to development
    configure_for_development()