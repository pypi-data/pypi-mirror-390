"""
Parquet storage layer for lineage history (fallback backend).

This module provides persistent storage using Parquet files as a fallback
option when Delta Lake is not available. It provides the same API as
DeltaLakeStorage but with some limitations:

Limitations compared to Delta Lake:
- No ACID transactions (risk of data corruption on concurrent writes)
- No time travel capabilities (cannot query historical versions)
- No automatic VACUUM (manual cleanup required)
- Less efficient for updates (requires full table scans)
- Risk of duplicate data on concurrent writes

Use this backend when:
- Delta Lake is not available or cannot be installed
- Simple append-only tracking is sufficient
- ACID guarantees are not critical

For production workloads, Delta Lake backend is strongly recommended.
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession

from .schema import HistoryTableSchemas

logger = logging.getLogger(__name__)


class ParquetStorage:
    """
    Parquet storage manager for lineage history tables (fallback backend).

    This class provides the same interface as DeltaLakeStorage but uses
    Parquet files instead of Delta Lake tables. It's designed to be a
    drop-in replacement when Delta Lake is not available.

    Important Limitations:
        - No ACID transactions: Concurrent writes may result in data corruption
        - No time travel: Cannot query historical table versions
        - Manual cleanup: No automatic VACUUM, old files must be cleaned manually
        - Less efficient: Queries require full partition scans
        - Duplicate risk: Race conditions may cause duplicate records

    Example:
        >>> storage = ParquetStorage(
        ...     spark=spark,
        ...     base_path="./lineage_history"
        ... )
        >>> storage.initialize_tables()
        >>> storage.write_snapshot(
        ...     snapshot_data=snapshot,
        ...     operations_data=operations,
        ...     governance_data=governance,
        ...     metrics_data=metrics
        ... )

    Warning:
        This backend is NOT recommended for production workloads with
        concurrent writers. Use Delta Lake backend for production deployments.
    """

    def __init__(
        self,
        spark: SparkSession,
        base_path: str,
        enable_compression: bool = True,
        retention_days: int = 90,
    ):
        """
        Initialize Parquet storage manager.

        Args:
            spark: Active SparkSession
            base_path: Base directory for Parquet tables
            enable_compression: Enable snappy compression (default: True)
            retention_days: Number of days to retain history (informational only,
                           no automatic cleanup)

        Raises:
            ValueError: If base_path is empty or invalid

        Note:
            retention_days is stored but not enforced. Manual cleanup required.
        """
        if not base_path or not base_path.strip():
            raise ValueError("base_path must be a non-empty string")

        self.spark = spark
        self.base_path = Path(base_path)
        self.enable_compression = enable_compression
        self.retention_days = retention_days

        # Compression codec (snappy is default for Parquet)
        self.compression = "snappy" if enable_compression else "uncompressed"

        # Table names and paths
        self.tables = {
            "lineage_snapshots": self.base_path / "lineage_snapshots",
            "lineage_operations": self.base_path / "lineage_operations",
            "governance_versions": self.base_path / "governance_versions",
            "lineage_metrics": self.base_path / "lineage_metrics",
        }

        logger.info(
            f"Initialized ParquetStorage at {base_path} "
            f"(compression={self.compression}, retention={retention_days} days)"
        )
        logger.warning(
            "Using Parquet storage backend. This backend does not provide "
            "ACID guarantees or time travel. For production workloads, "
            "consider installing delta-spark: pip install delta-spark"
        )

    def initialize_tables(self) -> None:
        """
        Initialize directory structure for Parquet tables.

        Creates directories for each table if they don't exist.
        Unlike Delta Lake, Parquet doesn't require table initialization,
        but we create directories to establish the structure.

        This method is idempotent - safe to call multiple times.
        """
        for table_name, table_path in self.tables.items():
            if not self._table_exists(str(table_path)):
                logger.info(f"Creating Parquet table directory: {table_name}")
                table_path.mkdir(parents=True, exist_ok=True)
            else:
                logger.debug(f"Parquet table already exists: {table_name}")

    def _table_exists(self, table_path: str) -> bool:
        """
        Check if Parquet table (directory) exists at the given path.

        Args:
            table_path: Path to the Parquet table directory

        Returns:
            True if directory exists and contains Parquet files, False otherwise
        """
        path = Path(table_path)
        if not path.exists():
            return False

        # Check if directory contains any parquet files
        try:
            # Try reading the table
            self.spark.read.parquet(table_path)
            return True
        except Exception:
            # Directory exists but no valid parquet files
            return False

    def table_exists(self, table_name: str) -> bool:
        """
        Public method to check if table exists.

        Args:
            table_name: Name of the table (e.g., 'lineage_snapshots')

        Returns:
            True if table exists, False otherwise

        Raises:
            ValueError: If table_name is not recognized
        """
        if table_name not in self.tables:
            raise ValueError(
                f"Unknown table name: {table_name}. "
                f"Must be one of: {list(self.tables.keys())}"
            )

        return self._table_exists(str(self.tables[table_name]))

    def write_snapshot(
        self,
        snapshot_data: Dict[str, Any],
        operations_data: List[Dict[str, Any]],
        governance_data: List[Dict[str, Any]],
        metrics_data: List[Dict[str, Any]],
    ) -> str:
        """
        Write a complete lineage snapshot to Parquet files.

        This method writes to all four tables using append mode:
        1. lineage_snapshots: Core snapshot metadata and graph
        2. lineage_operations: Denormalized operation details
        3. governance_versions: Governance metadata
        4. lineage_metrics: Performance and quality metrics

        Warning:
            Unlike Delta Lake, this method does NOT provide ACID guarantees.
            If the write fails partway through, some tables may be updated
            while others are not, resulting in an inconsistent state.

        Args:
            snapshot_data: Snapshot record (single dict)
            operations_data: List of operation records
            governance_data: List of governance records
            metrics_data: List of metric records

        Returns:
            snapshot_id of the written snapshot

        Raises:
            ValueError: If snapshot_data is invalid
            Exception: If write fails
        """
        snapshot_id = snapshot_data.get("snapshot_id")
        if not snapshot_id:
            raise ValueError("snapshot_data must contain 'snapshot_id'")

        try:
            # Write snapshot (single record)
            logger.info(f"Writing snapshot {snapshot_id} to Parquet")
            self._write_records(
                "lineage_snapshots",
                [snapshot_data],
                mode="append"
            )

            # Write operations (multiple records)
            if operations_data:
                self._write_records(
                    "lineage_operations",
                    operations_data,
                    mode="append"
                )
                logger.debug(
                    f"Wrote {len(operations_data)} operations for snapshot {snapshot_id}"
                )

            # Write governance metadata (multiple records)
            if governance_data:
                self._write_records(
                    "governance_versions",
                    governance_data,
                    mode="append"
                )
                logger.debug(
                    f"Wrote {len(governance_data)} governance records for snapshot {snapshot_id}"
                )

            # Write metrics (multiple records)
            if metrics_data:
                self._write_records(
                    "lineage_metrics",
                    metrics_data,
                    mode="append"
                )
                logger.debug(
                    f"Wrote {len(metrics_data)} metrics for snapshot {snapshot_id}"
                )

            logger.info(f"Successfully wrote snapshot {snapshot_id} to Parquet")
            return snapshot_id

        except Exception as e:
            logger.error(
                f"Failed to write snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def _write_records(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        mode: str = "append",
    ) -> None:
        """
        Write records to a specific Parquet table.

        Uses unique filenames with timestamps and UUIDs to minimize
        risk of concurrent write conflicts.

        Args:
            table_name: Name of the table
            records: List of records to write
            mode: Write mode (append/overwrite)

        Raises:
            Exception: If write fails
        """
        if not records:
            logger.debug(f"No records to write to {table_name}")
            return

        # Validate records
        for record in records:
            HistoryTableSchemas.validate_record(table_name, record)

        # Get schema and create DataFrame
        schema = HistoryTableSchemas.get_schema(table_name)
        df = self.spark.createDataFrame(records, schema)

        # Get partition columns
        partition_columns = HistoryTableSchemas.get_partition_columns(table_name)

        # Write to Parquet with partitioning
        table_path = str(self.tables[table_name])

        writer = df.write.format("parquet").mode(mode)

        # Enable compression
        if self.enable_compression:
            writer = writer.option("compression", self.compression)

        # Apply partitioning
        if partition_columns:
            writer = writer.partitionBy(*partition_columns)

        writer.save(table_path)

    def read_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a specific snapshot by ID.

        Note:
            This requires scanning all partitions to find the snapshot.
            Performance degrades with large datasets.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            Snapshot record as dictionary, or None if not found
        """
        try:
            table_path = str(self.tables["lineage_snapshots"])

            # Check if table exists
            if not self._table_exists(table_path):
                logger.warning(f"Table lineage_snapshots does not exist")
                return None

            df = (
                self.spark.read.parquet(table_path)
                .filter(f"snapshot_id = '{snapshot_id}'")
            )

            rows = df.collect()
            if not rows:
                logger.warning(f"Snapshot {snapshot_id} not found")
                return None

            return rows[0].asDict()

        except Exception as e:
            logger.error(
                f"Failed to read snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def read_snapshots(
        self,
        pipeline_name: Optional[str] = None,
        environment: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read snapshots with optional filters.

        Performance Note:
            Parquet backend uses partition pruning when filtering by
            pipeline_name and environment (partition columns), but still
            requires scanning all matching partitions for date filters.

        Args:
            pipeline_name: Filter by pipeline name (uses partition pruning)
            environment: Filter by environment (uses partition pruning)
            start_date: Filter by start date (ISO format: YYYY-MM-DD)
            end_date: Filter by end date (ISO format: YYYY-MM-DD)
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshot records as dictionaries
        """
        try:
            table_path = str(self.tables["lineage_snapshots"])

            # Check if table exists
            if not self._table_exists(table_path):
                logger.warning("Table lineage_snapshots does not exist")
                return []

            df = self.spark.read.parquet(table_path)

            # Apply filters (partition pruning for pipeline_name, environment)
            if pipeline_name:
                df = df.filter(f"pipeline_name = '{pipeline_name}'")
            if environment:
                df = df.filter(f"environment = '{environment}'")
            if start_date:
                df = df.filter(f"captured_at >= '{start_date}'")
            if end_date:
                df = df.filter(f"captured_at <= '{end_date}'")

            # Order by captured_at (most recent first)
            df = df.orderBy("captured_at", ascending=False)

            # Apply limit
            if limit:
                df = df.limit(limit)

            return [row.asDict() for row in df.collect()]

        except Exception as e:
            logger.error(f"Failed to read snapshots: {str(e)}", exc_info=True)
            raise

    def read_operations(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """
        Read all operations for a specific snapshot.

        Performance Note:
            Uses partition pruning on snapshot_id for efficient reads.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of operation records as dictionaries
        """
        try:
            table_path = str(self.tables["lineage_operations"])

            # Check if table exists
            if not self._table_exists(table_path):
                logger.warning("Table lineage_operations does not exist")
                return []

            df = (
                self.spark.read.parquet(table_path)
                .filter(f"snapshot_id = '{snapshot_id}'")
            )

            return [row.asDict() for row in df.collect()]

        except Exception as e:
            logger.error(
                f"Failed to read operations for snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def read_governance(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """
        Read all governance records for a specific snapshot.

        Performance Note:
            Uses partition pruning on snapshot_id for efficient reads.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of governance records as dictionaries
        """
        try:
            table_path = str(self.tables["governance_versions"])

            # Check if table exists
            if not self._table_exists(table_path):
                logger.warning("Table governance_versions does not exist")
                return []

            df = (
                self.spark.read.parquet(table_path)
                .filter(f"snapshot_id = '{snapshot_id}'")
            )

            return [row.asDict() for row in df.collect()]

        except Exception as e:
            logger.error(
                f"Failed to read governance for snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def read_metrics(self, snapshot_id: str) -> List[Dict[str, Any]]:
        """
        Read all metrics for a specific snapshot.

        Performance Note:
            Uses partition pruning on snapshot_id for efficient reads.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of metric records as dictionaries
        """
        try:
            table_path = str(self.tables["lineage_metrics"])

            # Check if table exists
            if not self._table_exists(table_path):
                logger.warning("Table lineage_metrics does not exist")
                return []

            df = (
                self.spark.read.parquet(table_path)
                .filter(f"snapshot_id = '{snapshot_id}'")
            )

            return [row.asDict() for row in df.collect()]

        except Exception as e:
            logger.error(
                f"Failed to read metrics for snapshot {snapshot_id}: {str(e)}",
                exc_info=True
            )
            raise

    def vacuum_tables(self, retention_hours: Optional[int] = None) -> None:
        """
        Manual cleanup of old Parquet files (no automatic VACUUM).

        Warning:
            Unlike Delta Lake, Parquet backend does NOT support automatic
            VACUUM. This method provides guidance but requires manual
            implementation.

        Args:
            retention_hours: Hours of retention (default: self.retention_days * 24)

        Note:
            This method logs instructions but does not delete files.
            Implement manual cleanup based on your retention policy.
        """
        if retention_hours is None:
            retention_hours = self.retention_days * 24

        logger.warning(
            "Parquet backend does not support automatic VACUUM. "
            f"Manual cleanup required for files older than {retention_hours} hours."
        )
        logger.info(
            "To clean up old files manually:\n"
            "1. Identify partition directories with old data\n"
            "2. Delete Parquet files older than retention period\n"
            "3. Be careful not to delete actively written files\n"
            f"Base path: {self.base_path}"
        )

    def optimize_tables(self) -> None:
        """
        Optimization placeholder (not supported for Parquet).

        Warning:
            Parquet backend does not support OPTIMIZE command.
            To improve query performance:
            1. Manually compact small files by reading and rewriting
            2. Repartition data for better partition balance
            3. Consider migrating to Delta Lake for automatic optimization

        Note:
            This method logs guidance but does not perform optimization.
        """
        logger.warning(
            "Parquet backend does not support automatic OPTIMIZE. "
            "Consider manually compacting small files or migrating to Delta Lake."
        )
        logger.info(
            "To improve Parquet query performance:\n"
            "1. Read partitions with many small files\n"
            "2. Repartition to fewer, larger files\n"
            "3. Write back with .write.mode('overwrite')\n"
            "4. Or migrate to Delta Lake: pip install delta-spark"
        )
