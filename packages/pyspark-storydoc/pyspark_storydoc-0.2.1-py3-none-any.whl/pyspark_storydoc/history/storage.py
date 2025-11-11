"""
Delta Lake storage layer for lineage history.

This module provides persistent storage using Delta Lake tables with:
- ACID transaction support
- Time travel capabilities
- Efficient partitioning
- Automatic schema validation
- Error handling and retry logic
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pyspark.sql import DataFrame, SparkSession

from .schema import HistoryTableSchemas

logger = logging.getLogger(__name__)


class DeltaLakeStorage:
    """
    Delta Lake storage manager for lineage history tables.

    This class handles:
    - Table initialization (create if not exist)
    - Writing snapshots with ACID guarantees
    - Reading snapshots with time-travel support
    - Schema validation and evolution
    - Partition management
    - Storage optimization (VACUUM, OPTIMIZE)

    Example:
        >>> storage = DeltaLakeStorage(
        ...     spark=spark,
        ...     base_path="./lineage_history"
        ... )
        >>> storage.initialize_tables()
        >>> storage.write_snapshot(snapshot_data)
    """

    def __init__(
        self,
        spark: SparkSession,
        base_path: str,
        enable_compression: bool = True,
        retention_days: int = 90,
    ):
        """
        Initialize Delta Lake storage manager.

        Args:
            spark: Active SparkSession
            base_path: Base directory for Delta Lake tables
            enable_compression: Enable Zstandard compression for JSON columns
            retention_days: Number of days to retain history (for VACUUM)

        Raises:
            ValueError: If base_path is empty or invalid
        """
        if not base_path or not base_path.strip():
            raise ValueError("base_path must be a non-empty string")

        self.spark = spark
        self.base_path = Path(base_path)
        self.enable_compression = enable_compression
        self.retention_days = retention_days

        # Table names and paths
        self.tables = {
            "lineage_snapshots": self.base_path / "lineage_snapshots",
            "lineage_operations": self.base_path / "lineage_operations",
            "governance_versions": self.base_path / "governance_versions",
            "lineage_metrics": self.base_path / "lineage_metrics",
        }

        # Configure Delta Lake settings
        if enable_compression:
            self.spark.conf.set(
                "spark.databricks.delta.properties.defaults.compression",
                "zstd"
            )

        logger.info(
            f"Initialized DeltaLakeStorage at {base_path} "
            f"(compression={enable_compression}, retention={retention_days} days)"
        )

    def initialize_tables(self) -> None:
        """
        Initialize all Delta Lake tables if they don't exist.

        Creates tables with appropriate schemas and partitioning:
        - lineage_snapshots: Partitioned by pipeline_name, environment
        - lineage_operations: Partitioned by snapshot_id
        - governance_versions: Partitioned by snapshot_id
        - lineage_metrics: Partitioned by snapshot_id, metric_name

        This method is idempotent - safe to call multiple times.
        """
        for table_name, table_path in self.tables.items():
            if not self._table_exists(str(table_path)):
                logger.info(f"Creating Delta Lake table: {table_name}")
                self._create_table(table_name, str(table_path))
            else:
                logger.debug(f"Delta Lake table already exists: {table_name}")

    def _table_exists(self, table_path: str) -> bool:
        """
        Check if Delta Lake table exists at the given path.

        Args:
            table_path: Path to the Delta Lake table

        Returns:
            True if table exists, False otherwise
        """
        try:
            self.spark.read.format("delta").load(table_path)
            return True
        except Exception:
            return False

    def _create_table(self, table_name: str, table_path: str) -> None:
        """
        Create a new Delta Lake table with appropriate schema and partitioning.

        Args:
            table_name: Name of the table (e.g., 'lineage_snapshots')
            table_path: File system path for the table

        Raises:
            Exception: If table creation fails
        """
        schema = HistoryTableSchemas.get_schema(table_name)
        partition_columns = HistoryTableSchemas.get_partition_columns(table_name)

        # Create empty DataFrame with schema
        empty_df = self.spark.createDataFrame([], schema)

        # Write to Delta Lake with partitioning
        writer = empty_df.write.format("delta").mode("ignore")

        if partition_columns:
            writer = writer.partitionBy(*partition_columns)

        writer.save(table_path)

        logger.info(
            f"Created Delta Lake table '{table_name}' at {table_path} "
            f"with partitions: {partition_columns}"
        )

    def write_snapshot(
        self,
        snapshot_data: Dict[str, Any],
        operations_data: List[Dict[str, Any]],
        governance_data: List[Dict[str, Any]],
        metrics_data: List[Dict[str, Any]],
    ) -> str:
        """
        Write a complete lineage snapshot to Delta Lake tables.

        This method performs atomic writes to all four tables:
        1. lineage_snapshots: Core snapshot metadata and graph
        2. lineage_operations: Denormalized operation details
        3. governance_versions: Governance metadata
        4. lineage_metrics: Performance and quality metrics

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
            logger.info(f"Writing snapshot {snapshot_id} to Delta Lake")
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

            logger.info(f"Successfully wrote snapshot {snapshot_id} to Delta Lake")
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
        Write records to a specific Delta Lake table.

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

        # Write to Delta Lake
        table_path = str(self.tables[table_name])
        df.write.format("delta").mode(mode).save(table_path)

    def read_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a specific snapshot by ID.

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            Snapshot record as dictionary, or None if not found
        """
        try:
            df = (
                self.spark.read.format("delta")
                .load(str(self.tables["lineage_snapshots"]))
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

        Args:
            pipeline_name: Filter by pipeline name
            environment: Filter by environment (dev/staging/prod)
            start_date: Filter by start date (ISO format: YYYY-MM-DD)
            end_date: Filter by end date (ISO format: YYYY-MM-DD)
            limit: Maximum number of snapshots to return

        Returns:
            List of snapshot records as dictionaries
        """
        try:
            df = self.spark.read.format("delta").load(
                str(self.tables["lineage_snapshots"])
            )

            # Apply filters
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

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of operation records as dictionaries
        """
        try:
            df = (
                self.spark.read.format("delta")
                .load(str(self.tables["lineage_operations"]))
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

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of governance records as dictionaries
        """
        try:
            df = (
                self.spark.read.format("delta")
                .load(str(self.tables["governance_versions"]))
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

        Args:
            snapshot_id: Unique identifier for the snapshot

        Returns:
            List of metric records as dictionaries
        """
        try:
            df = (
                self.spark.read.format("delta")
                .load(str(self.tables["lineage_metrics"]))
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
        Remove old files from Delta Lake tables to save storage.

        Args:
            retention_hours: Hours of retention (default: self.retention_days * 24)
        """
        if retention_hours is None:
            retention_hours = self.retention_days * 24

        logger.info(f"Running VACUUM with {retention_hours} hours retention")

        for table_name, table_path in self.tables.items():
            try:
                self.spark.sql(
                    f"VACUUM delta.`{table_path}` RETAIN {retention_hours} HOURS"
                )
                logger.info(f"Vacuumed table: {table_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to vacuum {table_name}: {str(e)}"
                )

    def optimize_tables(self) -> None:
        """
        Optimize Delta Lake tables for query performance.

        Runs OPTIMIZE command to compact small files and improve read performance.
        """
        logger.info("Running OPTIMIZE on Delta Lake tables")

        for table_name, table_path in self.tables.items():
            try:
                self.spark.sql(f"OPTIMIZE delta.`{table_path}`")
                logger.info(f"Optimized table: {table_name}")
            except Exception as e:
                logger.warning(
                    f"Failed to optimize {table_name}: {str(e)}"
                )
