"""
Delta Lake table schemas for lineage history tracking.

This module defines the schema for the 4 Delta Lake tables used to store
lineage history:
1. lineage_snapshots: Core lineage graph versioning
2. lineage_operations: Individual operation tracking
3. governance_versions: Governance metadata history
4. lineage_metrics: Performance/quality metrics

These schemas follow Delta Lake best practices:
- Partitioned for query efficiency
- Structured types for complex data
- Extensible metadata maps
- Support for time travel queries
"""

from typing import Any, Dict

from pyspark.sql.types import (
    ArrayType,
    BooleanType,
    DoubleType,
    IntegerType,
    LongType,
    MapType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


class HistoryTableSchemas:
    """
    Schema definitions for Delta Lake history tables.

    These schemas are designed to support:
    - Efficient time-range queries
    - Cross-environment comparisons
    - Governance drift detection
    - Trend analysis
    - Compliance auditing
    """

    @staticmethod
    def lineage_snapshots_schema() -> StructType:
        """
        Primary table storing complete lineage graph snapshots.

        Partition Strategy:
            - pipeline_name: Enable per-pipeline queries
            - environment: Enable cross-environment comparison
            - date(captured_at): Enable time-range pruning

        Storage Estimate:
            - Typical snapshot: 2-5 MB compressed (JSON with Zstandard)
            - 100 pipelines × 1 run/day × 90 days = 27 GB total

        Returns:
            StructType schema for lineage_snapshots table
        """
        return StructType([
            # Primary key
            StructField("snapshot_id", StringType(), False),

            # Pipeline identification
            StructField("pipeline_name", StringType(), False),
            StructField("environment", StringType(), False),

            # Temporal metadata
            StructField("captured_at", TimestampType(), False),

            # Execution metadata
            StructField("spark_app_id", StringType(), True),
            StructField("user", StringType(), True),
            StructField("version", StringType(), True),

            # Lineage graph (JSON serialized)
            StructField("lineage_graph", StringType(), False),

            # Summary statistics (for quick filtering)
            StructField("summary_stats", StructType([
                StructField("operation_count", IntegerType(), True),
                StructField("business_concept_count", IntegerType(), True),
                StructField("governance_operation_count", IntegerType(), True),
                StructField("total_row_count", LongType(), True),
                StructField("execution_time_seconds", DoubleType(), True),
            ]), True),

            # Extensible metadata
            StructField("metadata", MapType(StringType(), StringType()), True),
        ])

    @staticmethod
    def lineage_operations_schema() -> StructType:
        """
        Denormalized operation-level details for efficient querying.

        Use Cases:
            - Find high data loss operations: WHERE row_count_change_pct < -50
            - Track specific operation: WHERE operation_id = X ORDER BY captured_at
            - Performance regression: WHERE execution_time_seconds > threshold

        Partition Strategy:
            - snapshot_id: Enable efficient joins with snapshots table

        Returns:
            StructType schema for lineage_operations table
        """
        return StructType([
            # Foreign key
            StructField("snapshot_id", StringType(), False),

            # Operation identification
            StructField("operation_id", StringType(), False),
            StructField("operation_type", StringType(), False),
            StructField("business_concept", StringType(), True),
            StructField("description", StringType(), True),

            # Expression details (for withColumn, filter operations)
            StructField("expression_json", StringType(), True),

            # Row count metrics
            StructField("row_count_before", LongType(), True),
            StructField("row_count_after", LongType(), True),
            StructField("row_count_change_pct", DoubleType(), True),

            # Performance metrics
            StructField("execution_time_seconds", DoubleType(), True),

            # Column tracking
            StructField("columns_in", ArrayType(StringType()), True),
            StructField("columns_out", ArrayType(StringType()), True),

            # Extensible metadata
            StructField("metadata", MapType(StringType(), StringType()), True),
        ])

    @staticmethod
    def governance_versions_schema() -> StructType:
        """
        Governance metadata tracking for compliance auditing.

        Use Cases:
            - PII processing audit: WHERE pii_processing = true
            - Approval tracking: WHERE approval_status = 'pending'
            - Risk trend analysis: WHERE risks contains HIGH severity

        Compliance Coverage:
            - GDPR Article 30: Records of processing activities
            - CCPA Section 1798.100: Consumer data collection notice
            - HIPAA Security Rule: Audit controls

        Returns:
            StructType schema for governance_versions table
        """
        return StructType([
            # Foreign key
            StructField("snapshot_id", StringType(), False),
            StructField("operation_id", StringType(), False),

            # Business context
            StructField("business_justification", StringType(), True),
            StructField("customer_impact_level", StringType(), True),
            StructField("impacting_columns", ArrayType(StringType()), True),

            # PII tracking
            StructField("pii_processing", BooleanType(), True),
            StructField("pii_columns", ArrayType(StringType()), True),
            StructField("data_classification", StringType(), True),

            # Risk assessment
            StructField("risks", ArrayType(StructType([
                StructField("risk_id", StringType(), True),
                StructField("category", StringType(), True),
                StructField("description", StringType(), True),
                StructField("severity", StringType(), True),
                StructField("likelihood", StringType(), True),
                StructField("mitigation_status", StringType(), True),
            ])), True),

            # Approval workflow
            StructField("approval_status", StringType(), True),
            StructField("approved_by", StringType(), True),
            StructField("approval_date", TimestampType(), True),
            StructField("approval_reference", StringType(), True),

            # Bias and fairness
            StructField("bias_risk_score", DoubleType(), True),
            StructField("fairness_metrics", ArrayType(StringType()), True),

            # Extensible metadata
            StructField("metadata", MapType(StringType(), StringType()), True),
        ])

    @staticmethod
    def lineage_metrics_schema() -> StructType:
        """
        Performance and data quality metrics for trend analysis.

        Use Cases:
            - Complexity growth: WHERE metric_name = 'complexity_score'
            - Performance regression: WHERE metric_name = 'execution_time'
            - Data volume trends: WHERE metric_name = 'row_count'

        Partition Strategy:
            - snapshot_id: Enable efficient joins
            - metric_name: Enable metric-specific queries

        Returns:
            StructType schema for lineage_metrics table
        """
        return StructType([
            # Foreign key
            StructField("snapshot_id", StringType(), False),

            # Metric identification
            StructField("metric_name", StringType(), False),
            StructField("metric_value", DoubleType(), False),
            StructField("metric_unit", StringType(), True),

            # Scope
            StructField("scope", StringType(), False),  # pipeline/business_concept/operation
            StructField("scope_id", StringType(), False),

            # Extensible metadata
            StructField("metadata", MapType(StringType(), StringType()), True),
        ])

    @staticmethod
    def get_partition_columns(table_name: str) -> list:
        """
        Get partition columns for a specific table.

        Args:
            table_name: Name of the table (snapshots/operations/governance/metrics)

        Returns:
            List of column names to use for partitioning

        Raises:
            ValueError: If table_name is not recognized
        """
        partitions = {
            "lineage_snapshots": ["pipeline_name", "environment"],
            "lineage_operations": ["snapshot_id"],
            "governance_versions": ["snapshot_id"],
            "lineage_metrics": ["snapshot_id", "metric_name"],
        }

        if table_name not in partitions:
            raise ValueError(
                f"Unknown table name: {table_name}. "
                f"Must be one of: {list(partitions.keys())}"
            )

        return partitions[table_name]

    @staticmethod
    def get_schema(table_name: str) -> StructType:
        """
        Get schema for a specific table.

        Args:
            table_name: Name of the table (snapshots/operations/governance/metrics)

        Returns:
            StructType schema for the table

        Raises:
            ValueError: If table_name is not recognized
        """
        schemas = {
            "lineage_snapshots": HistoryTableSchemas.lineage_snapshots_schema,
            "lineage_operations": HistoryTableSchemas.lineage_operations_schema,
            "governance_versions": HistoryTableSchemas.governance_versions_schema,
            "lineage_metrics": HistoryTableSchemas.lineage_metrics_schema,
        }

        if table_name not in schemas:
            raise ValueError(
                f"Unknown table name: {table_name}. "
                f"Must be one of: {list(schemas.keys())}"
            )

        return schemas[table_name]()

    @staticmethod
    def validate_record(table_name: str, record: Dict[str, Any]) -> None:
        """
        Validate that a record conforms to the table schema.

        Args:
            table_name: Name of the table
            record: Dictionary representing a single record

        Raises:
            ValueError: If record is missing required fields or has invalid types
        """
        schema = HistoryTableSchemas.get_schema(table_name)

        # Check required fields
        required_fields = [f.name for f in schema.fields if not f.nullable]
        missing_fields = set(required_fields) - set(record.keys())

        if missing_fields:
            raise ValueError(
                f"Record for table '{table_name}' is missing required fields: "
                f"{missing_fields}"
            )
