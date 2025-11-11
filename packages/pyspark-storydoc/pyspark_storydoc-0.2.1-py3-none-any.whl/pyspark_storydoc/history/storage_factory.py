"""
Storage backend factory for lineage history tracking.

This module provides automatic detection and instantiation of storage
backends (Delta Lake or Parquet) based on availability and user preference.

The factory supports three modes:
1. "auto" (default): Use Delta Lake if available, fallback to Parquet
2. "delta": Force Delta Lake (raises error if not available)
3. "parquet": Force Parquet (useful for testing or compatibility)

Example:
    >>> from pyspark_storydoc.history import create_storage
    >>>
    >>> # Automatic detection (recommended)
    >>> storage = create_storage(
    ...     spark=spark,
    ...     base_path="./lineage_history",
    ...     storage_backend="auto"
    ... )
    >>>
    >>> # Force specific backend
    >>> storage = create_storage(
    ...     spark=spark,
    ...     base_path="./lineage_history",
    ...     storage_backend="parquet"
    ... )
"""

import logging
from typing import Union

from pyspark.sql import SparkSession

from .parquet_storage import ParquetStorage
from .storage import DeltaLakeStorage

logger = logging.getLogger(__name__)


def detect_delta_lake_available() -> bool:
    """
    Detect if Delta Lake is available in the current environment.

    This function checks if the delta-spark package is installed and
    can be imported successfully. It does not check if Delta Lake is
    configured in the SparkSession.

    Returns:
        True if Delta Lake package is available, False otherwise

    Example:
        >>> if detect_delta_lake_available():
        ...     print("Delta Lake is available")
        ... else:
        ...     print("Delta Lake is not installed")

    Note:
        This only checks package availability. Actual Delta Lake
        functionality may still fail if Spark is not properly configured.
    """
    try:
        # Try importing Delta Lake configuration function
        from delta import configure_spark_with_delta_pip
        logger.debug("Delta Lake package detected (delta-spark is installed)")
        return True
    except ImportError:
        logger.debug("Delta Lake package not found (delta-spark not installed)")
        return False


def create_storage(
    spark: SparkSession,
    base_path: str,
    storage_backend: str = "auto",
    **kwargs
) -> Union[DeltaLakeStorage, ParquetStorage]:
    """
    Create appropriate storage backend based on availability and preference.

    This factory function automatically selects the best available storage
    backend or forces a specific backend based on user preference.

    Backend Selection Logic:
        - "auto" (default): Use Delta Lake if available, fallback to Parquet
        - "delta": Force Delta Lake, raise error if not available
        - "parquet": Force Parquet, always available

    Args:
        spark: Active SparkSession
        base_path: Base directory for storage
        storage_backend: Backend selection mode ("auto", "delta", or "parquet")
        **kwargs: Additional arguments passed to storage backend:
            - enable_compression: Enable compression (default: True)
            - retention_days: Retention period in days (default: 90)

    Returns:
        Storage instance (DeltaLakeStorage or ParquetStorage)

    Raises:
        ValueError: If storage_backend is unknown or requested backend
                   is not available

    Examples:
        >>> # Automatic detection (recommended for most use cases)
        >>> storage = create_storage(
        ...     spark=spark,
        ...     base_path="./lineage_history"
        ... )
        >>>
        >>> # Force Delta Lake (production deployments)
        >>> try:
        ...     storage = create_storage(
        ...         spark=spark,
        ...         base_path="./lineage_history",
        ...         storage_backend="delta"
        ...     )
        ... except ValueError as e:
        ...     print(f"Delta Lake not available: {e}")
        >>>
        >>> # Force Parquet (testing or compatibility)
        >>> storage = create_storage(
        ...     spark=spark,
        ...     base_path="./lineage_history",
        ...     storage_backend="parquet"
        ... )

    Note:
        When using "auto" mode with Delta Lake unavailable, a warning
        will be logged recommending delta-spark installation.
    """
    # Normalize backend name (case-insensitive)
    storage_backend = storage_backend.lower().strip()

    if storage_backend == "auto":
        # Automatic backend selection
        if detect_delta_lake_available():
            logger.info(
                "Using Delta Lake storage backend (auto-detected). "
                "This provides ACID guarantees and time travel capabilities."
            )
            return DeltaLakeStorage(spark, base_path, **kwargs)
        else:
            logger.warning(
                "Delta Lake not available. Using Parquet fallback backend. "
                "For production workloads with ACID guarantees, "
                "install delta-spark: pip install delta-spark"
            )
            logger.info(
                "Parquet backend limitations: No ACID transactions, "
                "no time travel, manual cleanup required. "
                "See documentation for details."
            )
            return ParquetStorage(spark, base_path, **kwargs)

    elif storage_backend == "delta":
        # Force Delta Lake
        if not detect_delta_lake_available():
            raise ValueError(
                "Delta Lake backend requested but delta-spark is not installed. "
                "Install with: pip install delta-spark\n"
                "Or use storage_backend='auto' to fallback to Parquet."
            )

        logger.info(
            "Using Delta Lake storage backend (explicitly requested). "
            "This provides ACID guarantees and time travel capabilities."
        )
        return DeltaLakeStorage(spark, base_path, **kwargs)

    elif storage_backend == "parquet":
        # Force Parquet
        logger.info(
            "Using Parquet storage backend (explicitly requested). "
            "Note: No ACID transactions, no time travel, manual cleanup required."
        )
        logger.warning(
            "Parquet backend is NOT recommended for production workloads "
            "with concurrent writers. Consider Delta Lake for production."
        )
        return ParquetStorage(spark, base_path, **kwargs)

    else:
        raise ValueError(
            f"Unknown storage backend: '{storage_backend}'. "
            f"Must be one of: 'auto', 'delta', 'parquet'"
        )


def get_backend_info(storage_backend: str = "auto") -> dict:
    """
    Get information about a storage backend.

    This utility function provides metadata about storage backends
    without instantiating them.

    Args:
        storage_backend: Backend to query ("auto", "delta", or "parquet")

    Returns:
        Dictionary containing:
            - backend: Resolved backend name
            - available: Whether backend is available
            - class_name: Storage class name
            - features: List of supported features
            - limitations: List of known limitations

    Example:
        >>> info = get_backend_info("auto")
        >>> print(f"Backend: {info['backend']}")
        >>> print(f"Available: {info['available']}")
        >>> print(f"Features: {', '.join(info['features'])}")
    """
    storage_backend = storage_backend.lower().strip()

    if storage_backend == "auto":
        # Resolve to actual backend
        if detect_delta_lake_available():
            storage_backend = "delta"
        else:
            storage_backend = "parquet"

    if storage_backend == "delta":
        features = [
            "ACID transactions",
            "Time travel",
            "Automatic VACUUM",
            "OPTIMIZE command",
            "Schema evolution",
            "Concurrent writes",
        ]
        limitations = [
            "Requires delta-spark package",
            "Additional dependencies",
        ]
        return {
            "backend": "delta",
            "name": "Delta Lake",
            "available": detect_delta_lake_available(),
            "class_name": "DeltaLakeStorage",
            "features": features,
            "pros": features,  # Alias for backwards compatibility
            "limitations": limitations,
            "cons": limitations,  # Alias for backwards compatibility
            "recommended_for": "Production workloads, concurrent writes, compliance",
        }
    elif storage_backend == "parquet":
        features = [
            "No extra dependencies",
            "Simple file format",
            "Partition pruning",
            "Compression support",
        ]
        limitations = [
            "No ACID transactions",
            "No time travel",
            "Manual cleanup required",
            "Risk of duplicates on concurrent writes",
            "Less efficient for updates",
        ]
        return {
            "backend": "parquet",
            "name": "Parquet",
            "available": True,  # Always available
            "class_name": "ParquetStorage",
            "features": features,
            "pros": features,  # Alias for backwards compatibility
            "limitations": limitations,
            "cons": limitations,  # Alias for backwards compatibility
            "recommended_for": "Development, testing, single-writer scenarios",
        }
    else:
        raise ValueError(
            f"Unknown storage backend: '{storage_backend}'. "
            f"Must be one of: 'auto', 'delta', 'parquet'"
        )


def print_backend_comparison():
    """
    Print a comparison table of storage backends.

    This utility function displays a formatted comparison of Delta Lake
    and Parquet backends to help users choose the right backend.

    Example:
        >>> from pyspark_storydoc.history import print_backend_comparison
        >>> print_backend_comparison()
    """
    delta_info = get_backend_info("delta")
    parquet_info = get_backend_info("parquet")

    print("\n" + "="*80)
    print("STORAGE BACKEND COMPARISON")
    print("="*80)

    print(f"\nDelta Lake (Available: {delta_info['available']})")
    print("-" * 40)
    print("Features:")
    for feature in delta_info['features']:
        print(f"  [+] {feature}")
    print("\nLimitations:")
    for limitation in delta_info['limitations']:
        print(f"  [!] {limitation}")
    print(f"\nRecommended for: {delta_info['recommended_for']}")

    print(f"\n{'='*80}")

    print(f"\nParquet (Available: {parquet_info['available']})")
    print("-" * 40)
    print("Features:")
    for feature in parquet_info['features']:
        print(f"  [+] {feature}")
    print("\nLimitations:")
    for limitation in parquet_info['limitations']:
        print(f"  [!] {limitation}")
    print(f"\nRecommended for: {parquet_info['recommended_for']}")

    print(f"\n{'='*80}")
    print("\nRecommendation:")
    if delta_info['available']:
        print("  > Use Delta Lake (storage_backend='delta') for production workloads")
        print("  > Use Parquet (storage_backend='parquet') only for testing/dev")
    else:
        print("  > Delta Lake not available - using Parquet fallback")
        print("  > Install delta-spark for production features: pip install delta-spark")
    print("="*80 + "\n")
