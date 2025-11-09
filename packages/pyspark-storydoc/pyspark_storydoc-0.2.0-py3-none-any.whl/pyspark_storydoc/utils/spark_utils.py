"""
Spark session utilities for proper resource management and cleanup.

This module provides utilities for managing Spark sessions, particularly
focused on proper cleanup to avoid Windows-specific file locking issues
during shutdown.
"""

import gc
import logging
import time
from typing import Optional

from pyspark.sql import SparkSession

logger = logging.getLogger(__name__)


def cleanup_spark_session(
    spark: Optional[SparkSession] = None,
    clear_cache: bool = True,
    reset_tracker: bool = True,
    delay_ms: int = 1000,
    verbose: bool = False
) -> None:
    """
    Perform proper cleanup before stopping a Spark session.

    This function addresses Windows-specific file locking issues by:
    1. Clearing the Spark catalog cache
    2. Resetting the lineage tracker (optional)
    3. Forcing garbage collection to release file handles
    4. Stopping the Spark session gracefully
    5. Adding a brief delay to allow file handles to be released

    Important - Known Spark on Windows Issue:
        Even with proper cleanup, you may see this error during JVM shutdown:

            ERROR ShutdownHookManager: Exception while deleting Spark temp dir
            java.nio.file.NoSuchFileException: C:\\Users\\...\\Temp\\spark-...

        This is a HARMLESS cosmetic error that occurs AFTER your Python code
        completes successfully. It is caused by:

        - Race conditions between JVM shutdown hooks running concurrently
        - Windows file handle delays (slower than Unix systems)
        - Spark's internal cleanup threads competing to delete the same files

        The error does NOT affect functionality - all outputs are generated
        successfully before this error occurs. This is a known Spark issue
        (SPARK-12216, SPARK-29912) and can be safely ignored.

        See KNOWN_ISSUES.md for more details.

    Args:
        spark: SparkSession to clean up. If None, uses the active session.
        clear_cache: Whether to clear the Spark catalog cache (default: True)
        reset_tracker: Whether to reset the lineage tracker (default: True)
        delay_ms: Delay in milliseconds after stopping Spark (default: 1000)
                  Helps prevent Windows file locking issues. Increase to 2000ms
                  if you still see temp directory deletion errors frequently.
        verbose: Print cleanup status messages to console (default: False)

    Example:
        >>> from pyspark.sql import SparkSession
        >>> from pyspark_storydoc.utils import cleanup_spark_session
        >>>
        >>> spark = SparkSession.builder.appName("MyApp").getOrCreate()
        >>> # ... do work ...
        >>> cleanup_spark_session(spark, verbose=True)

    Note:
        The delay after spark.stop() is specifically for Windows systems
        where file locks can persist longer than on Unix systems. This
        helps reduce (but may not eliminate) temp directory deletion errors.
    """
    # Get the active session if not provided
    if spark is None:
        spark = SparkSession.getActiveSession()

    if spark is None:
        logger.warning("No active Spark session found for cleanup")
        return

    try:
        if verbose:
            print("\nCleaning up Spark session...")

        # Clear Spark's catalog cache to release DataFrame references
        if clear_cache:
            try:
                spark.catalog.clearCache()
                logger.debug("Cleared Spark catalog cache")
            except Exception as e:
                logger.warning(f"Failed to clear Spark catalog cache: {e}")

        # Reset the lineage tracker to clear internal caches
        if reset_tracker:
            try:
                from pyspark_storydoc.core.lineage_tracker import reset_tracker
                reset_tracker()
                logger.debug("Reset lineage tracker")
            except ImportError:
                logger.debug("Lineage tracker not available, skipping reset")
            except Exception as e:
                logger.warning(f"Failed to reset lineage tracker: {e}")

        # Force garbage collection to release file handles
        # This is especially important on Windows where file locks persist
        gc.collect()
        logger.debug("Forced garbage collection")

        # Stop the Spark session
        spark.stop()
        logger.debug("Stopped Spark session")

        # Brief delay to allow cleanup, especially important on Windows
        if delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
            logger.debug(f"Applied {delay_ms}ms cleanup delay")

        if verbose:
            print("Spark cleanup complete.")
            print("\nNote: If you see 'ERROR ShutdownHookManager' during JVM shutdown,")
            print("this is a known Spark-on-Windows issue and does not affect results.")
            print("See KNOWN_ISSUES.md for details.")

    except Exception as e:
        logger.error(f"Error during Spark session cleanup: {e}")
        raise


def get_or_create_spark_session(
    app_name: str,
    master: str = "local[*]",
    config: Optional[dict] = None,
    enable_arrow: bool = True,
    adaptive_execution: bool = True,
    optimize_for: str = "development"
) -> SparkSession:
    """
    Get or create a Spark session with optimized multi-core configuration.

    This function creates a Spark session optimized for local multi-core execution,
    ensuring all available CPU cores are utilized for maximum performance.

    Configuration Optimization Levels:
    - "development": Optimized for small datasets and fast feedback (default)
    - "production": Optimized for large datasets and throughput
    - "testing": Minimal resources for unit tests

    Args:
        app_name: Name for the Spark application
        master: Spark master URL (default: "local[*]" uses all available cores)
        config: Additional Spark configuration options to override defaults
        enable_arrow: Enable Apache Arrow for optimized pandas conversion (default: True)
        adaptive_execution: Enable Adaptive Query Execution (AQE) for dynamic optimization (default: True)
        optimize_for: Optimization profile - "development", "production", or "testing" (default: "development")

    Returns:
        SparkSession instance configured for optimal multi-core performance

    Examples:
        >>> # Default configuration - uses all cores
        >>> spark = get_or_create_spark_session("MyApp")

        >>> # Custom configuration for specific workload
        >>> spark = get_or_create_spark_session(
        ...     "MyApp",
        ...     optimize_for="production",
        ...     config={"spark.sql.shuffle.partitions": "200"}
        ... )

        >>> # Testing configuration with minimal resources
        >>> spark = get_or_create_spark_session(
        ...     "TestApp",
        ...     optimize_for="testing",
        ...     master="local[2]"
        ... )

    Notes:
        - Default master "local[*]" uses all available CPU cores
        - Use "local[N]" to limit to N cores (e.g., "local[4]" for 4 cores)
        - Adaptive execution automatically optimizes shuffle partitions and join strategies
        - Arrow optimization significantly speeds up DataFrame/pandas conversions
    """
    builder = SparkSession.builder.appName(app_name).master(master)

    # Apply optimization profile defaults
    profile_config = _get_optimization_profile(optimize_for)
    for key, value in profile_config.items():
        builder = builder.config(key, str(value))

    # Enable Adaptive Query Execution for dynamic optimization
    if adaptive_execution:
        builder = builder \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.sql.adaptive.localShuffleReader.enabled", "true")

    # Enable Apache Arrow for optimized pandas conversion
    if enable_arrow:
        builder = builder \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.sql.execution.arrow.pyspark.fallback.enabled", "true")

    # Apply user-provided configuration overrides
    if config:
        for key, value in config.items():
            builder = builder.config(key, str(value))

    return builder.getOrCreate()


def _get_optimization_profile(profile: str) -> dict:
    """
    Get Spark configuration profile for different optimization levels.

    Args:
        profile: One of "development", "production", or "testing"

    Returns:
        Dictionary of Spark configuration settings
    """
    import multiprocessing

    # Detect number of CPU cores
    num_cores = multiprocessing.cpu_count()

    profiles = {
        "testing": {
            # Minimal resources for fast unit tests
            "spark.sql.shuffle.partitions": "2",
            "spark.default.parallelism": "2",
            "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
            "spark.driver.memory": "1g",
            "spark.executor.memory": "1g",
            "spark.memory.fraction": "0.6",
        },
        "development": {
            # Balanced for local development with small to medium datasets
            "spark.sql.shuffle.partitions": min(num_cores * 2, 16),
            "spark.default.parallelism": num_cores * 2,
            "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
            "spark.driver.memory": "2g",
            "spark.executor.memory": "2g",
            "spark.memory.fraction": "0.6",
            "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
        },
        "production": {
            # Optimized for large datasets and high throughput
            "spark.sql.shuffle.partitions": "200",
            "spark.default.parallelism": num_cores * 3,
            "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
            "spark.driver.memory": "4g",
            "spark.executor.memory": "4g",
            "spark.memory.fraction": "0.8",
            "spark.memory.storageFraction": "0.5",
            "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
        }
    }

    return profiles.get(profile, profiles["development"])


def get_recommended_partitions(
    data_size_mb: float,
    partition_size_mb: float = 128.0,
    min_partitions: int = 2,
    max_partitions: int = 1000
) -> int:
    """
    Calculate recommended number of partitions based on data size.

    This function helps determine the optimal partition count to balance
    parallelism with per-partition overhead.

    Rules of Thumb:
    - Target partition size: 100-200 MB (default: 128 MB)
    - Minimum partitions: 2-4 (even for small data)
    - Maximum partitions: Limited to avoid excessive overhead
    - Adjust based on operation type (joins need more partitions)

    Args:
        data_size_mb: Estimated data size in megabytes
        partition_size_mb: Target size per partition in MB (default: 128 MB)
        min_partitions: Minimum number of partitions (default: 2)
        max_partitions: Maximum number of partitions (default: 1000)

    Returns:
        Recommended number of partitions

    Examples:
        >>> # Small dataset: 500 MB
        >>> get_recommended_partitions(500)
        4

        >>> # Medium dataset: 10 GB
        >>> get_recommended_partitions(10 * 1024)
        80

        >>> # Large dataset: 100 GB
        >>> get_recommended_partitions(100 * 1024)
        800

        >>> # Custom partition size for joins
        >>> get_recommended_partitions(50 * 1024, partition_size_mb=64)
        800
    """
    import math

    # Calculate ideal partitions based on data size
    ideal_partitions = math.ceil(data_size_mb / partition_size_mb)

    # Apply min/max constraints
    recommended = max(min_partitions, min(ideal_partitions, max_partitions))

    return recommended


def configure_spark_for_workload(
    spark: SparkSession,
    workload_type: str,
    data_size_mb: Optional[float] = None
) -> None:
    """
    Dynamically configure an existing Spark session for specific workload types.

    This function adjusts Spark configuration at runtime based on the workload
    characteristics, optimizing for different operation patterns.

    Workload Types:
    - "join_heavy": Optimized for multiple joins with moderate skew handling
    - "aggregation": Optimized for groupBy and aggregation operations
    - "etl": Balanced for extract-transform-load pipelines
    - "iterative": Optimized for iterative algorithms (caching, reuse)
    - "streaming": Optimized for structured streaming (not implemented yet)

    Args:
        spark: Active SparkSession to configure
        workload_type: Type of workload - one of the types listed above
        data_size_mb: Optional data size hint for partition tuning

    Examples:
        >>> spark = get_or_create_spark_session("MyApp")
        >>> configure_spark_for_workload(spark, "join_heavy", data_size_mb=50000)

        >>> # For aggregation-heavy workloads
        >>> configure_spark_for_workload(spark, "aggregation", data_size_mb=10000)

    Raises:
        ValueError: If workload_type is not recognized
    """
    workload_configs = {
        "join_heavy": {
            "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
            "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "268435456",  # 256MB
        },
        "aggregation": {
            "spark.sql.shuffle.partitions": "200" if not data_size_mb else str(get_recommended_partitions(data_size_mb)),
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.minPartitionSize": "1048576",  # 1MB
        },
        "etl": {
            "spark.sql.shuffle.partitions": "200",
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.files.maxPartitionBytes": "134217728",  # 128MB
            "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
        },
        "iterative": {
            "spark.memory.fraction": "0.8",
            "spark.memory.storageFraction": "0.5",
            "spark.cleaner.periodicGC.interval": "30min",
        }
    }

    if workload_type not in workload_configs:
        raise ValueError(
            f"Unknown workload_type: {workload_type}. "
            f"Must be one of: {', '.join(workload_configs.keys())}"
        )

    configs = workload_configs[workload_type]
    for key, value in configs.items():
        spark.conf.set(key, value)

    logger.info(f"Configured Spark session for '{workload_type}' workload")


def print_spark_config_summary(spark: SparkSession) -> None:
    """
    Print a summary of key Spark configuration settings.

    This helper function displays the most important Spark settings
    for performance tuning and debugging.

    Args:
        spark: SparkSession to inspect

    Example:
        >>> spark = get_or_create_spark_session("MyApp")
        >>> print_spark_config_summary(spark)
        ================================================================================
        Spark Configuration Summary
        ================================================================================
        Master:                    local[*]
        App Name:                  MyApp
        Shuffle Partitions:        16
        Default Parallelism:       16
        ...
    """
    conf = spark.sparkContext.getConf()

    print("=" * 80)
    print("Spark Configuration Summary")
    print("=" * 80)

    key_configs = [
        ("Master", "spark.master"),
        ("App Name", "spark.app.name"),
        ("Shuffle Partitions", "spark.sql.shuffle.partitions"),
        ("Default Parallelism", "spark.default.parallelism"),
        ("Driver Memory", "spark.driver.memory"),
        ("Executor Memory", "spark.executor.memory"),
        ("Memory Fraction", "spark.memory.fraction"),
        ("Adaptive Execution", "spark.sql.adaptive.enabled"),
        ("Arrow Enabled", "spark.sql.execution.arrow.pyspark.enabled"),
        ("Broadcast Threshold", "spark.sql.autoBroadcastJoinThreshold"),
    ]

    for label, key in key_configs:
        value = conf.get(key, "Not set")
        print(f"{label:30s} {value}")

    print("=" * 80)
    print(f"Active Cores: {spark.sparkContext.defaultParallelism}")
    print("=" * 80)
