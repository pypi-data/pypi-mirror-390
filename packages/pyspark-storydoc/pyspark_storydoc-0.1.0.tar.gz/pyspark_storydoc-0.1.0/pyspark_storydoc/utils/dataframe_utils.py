"""Utility functions for DataFrame operations."""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from .exceptions import ValidationError

logger = logging.getLogger(__name__)

try:
    from pyspark.sql import DataFrame
    PYSPARK_AVAILABLE = True
except ImportError:
    PYSPARK_AVAILABLE = False
    logger.warning("PySpark not available. Some functionality will be limited.")

    # Create a dummy DataFrame class for type hints when PySpark is not available
    class DataFrame:  # type: ignore
        pass


def is_dataframe(obj: Any) -> bool:
    """
    Check if an object is a PySpark DataFrame or LineageDataFrame.

    Args:
        obj: Object to check

    Returns:
        True if the object is a DataFrame, False otherwise
    """
    if not PYSPARK_AVAILABLE:
        return False

    # Import here to avoid circular imports
    try:
        from ..core.lineage_dataframe import LineageDataFrame
        return isinstance(obj, (DataFrame, LineageDataFrame))
    except ImportError:
        return isinstance(obj, DataFrame)


def extract_dataframes(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> List[DataFrame]:
    """
    Extract DataFrame objects from function arguments.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        List of DataFrame objects found in the arguments
    """
    dataframes = []

    # Check positional arguments
    for arg in args:
        if is_dataframe(arg):
            # If it's a LineageDataFrame, extract the underlying DataFrame
            if hasattr(arg, '_df'):
                dataframes.append(arg._df)
            else:
                dataframes.append(arg)

    # Check keyword arguments
    for value in kwargs.values():
        if is_dataframe(value):
            # If it's a LineageDataFrame, extract the underlying DataFrame
            if hasattr(value, '_df'):
                dataframes.append(value._df)
            else:
                dataframes.append(value)

    return dataframes


def extract_dataframes_with_keys(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract DataFrame objects from function arguments with position/name keys.

    Args:
        args: Positional arguments
        kwargs: Keyword arguments

    Returns:
        Dictionary mapping argument keys to DataFrame objects
    """
    dataframes = {}

    # Check positional arguments
    for i, arg in enumerate(args):
        if is_dataframe(arg):
            dataframes[f"arg_{i}"] = arg

    # Check keyword arguments
    for key, value in kwargs.items():
        if is_dataframe(value):
            dataframes[key] = value

    return dataframes


def generate_lineage_id() -> str:
    """
    Generate a unique identifier for lineage tracking.

    Returns:
        Unique string identifier
    """
    return str(uuid.uuid4())[:8]


def get_dataframe_info(df: DataFrame) -> Dict[str, Any]:
    """
    Extract basic information about a DataFrame without triggering computation.

    Args:
        df: PySpark DataFrame

    Returns:
        Dictionary with DataFrame information
    """
    try:
        return {
            "columns": df.columns,
            "dtypes": df.dtypes,
            "schema_json": df.schema.json(),
            "is_cached": df.is_cached,
            "storage_level": str(df.storageLevel) if hasattr(df, 'storageLevel') else None,
        }
    except Exception as e:
        logger.warning(f"Failed to extract DataFrame info: {e}")
        return {
            "columns": [],
            "dtypes": [],
            "schema_json": None,
            "is_cached": False,
            "storage_level": None,
            "error": str(e)
        }


def safe_count(df: DataFrame, timeout_seconds: Optional[int] = None) -> int:
    """
    Safely count DataFrame rows.

    Args:
        df: PySpark DataFrame
        timeout_seconds: Maximum time to wait for count operation (unused for now)

    Returns:
        Row count

    Raises:
        MaterializationError: If count operation fails
    """
    from .exceptions import MaterializationError

    # CRITICAL FIX: Ensure we're working with raw PySpark DataFrame
    # If this is a LineageDataFrame, extract the underlying DataFrame to avoid
    # triggering additional lineage tracking during metrics capture
    if hasattr(df, '_df'):
        raw_df = df._df
        logger.debug(f"Extracted raw DataFrame from LineageDataFrame for metrics capture")
    else:
        raw_df = df

    try:
        count = raw_df.count()
        logger.debug(f"Row count: {count}")
        return count

    except Exception as e:
        raise MaterializationError(f"Failed to count DataFrame rows: {e}")


def safe_distinct_count(df: DataFrame, column_name: str) -> int:
    """
    Safely count distinct values in a column.

    Args:
        df: PySpark DataFrame
        column_name: Name of the column to count distinct values

    Returns:
        Distinct count

    Raises:
        ValidationError: If column_name is invalid
        MaterializationError: If distinct count operation fails
    """
    from .exceptions import MaterializationError, ValidationError

    # CRITICAL FIX: Ensure we're working with raw PySpark DataFrame
    # If this is a LineageDataFrame, extract the underlying DataFrame to avoid
    # triggering additional lineage tracking during metrics capture
    if hasattr(df, '_df'):
        raw_df = df._df
        logger.debug(f"Extracted raw DataFrame from LineageDataFrame for metrics capture")
    else:
        raw_df = df

    if column_name not in raw_df.columns:
        raise ValidationError(
            f"Column '{column_name}' not found in DataFrame",
            parameter_name="column_name",
            parameter_value=column_name
        )

    try:
        distinct_count = raw_df.select(column_name).distinct().count()
        logger.debug(f"Distinct count for '{column_name}': {distinct_count}")
        return distinct_count

    except Exception as e:
        raise MaterializationError(
            f"Failed to count distinct values in column '{column_name}': {e}"
        )


def extract_column_references(condition_str: str) -> List[str]:
    """
    Extract column names from a condition string.

    This is a basic implementation that looks for common PySpark column patterns.
    A more sophisticated version might parse the actual expression tree.

    Args:
        condition_str: String representation of a PySpark condition

    Returns:
        List of column names found in the condition
    """
    import re

    # Pattern to match PySpark column references
    # Matches: Column<'column_name'>, col('column_name'), df['column_name']
    patterns = [
        r"Column<b?'([^']+)'>",  # Column<'name'> or Column<b'name'>
        r"col\(['\"]([^'\"]+)['\"]\)",  # col('name') or col("name")
        r"\['([^']+)'\]",  # df['name']
        r'[""]([^"]+)[""]',  # df["name"]
    ]

    columns = set()
    for pattern in patterns:
        matches = re.findall(pattern, condition_str)
        columns.update(matches)

    return list(columns)


def extract_column_names(condition_or_expr) -> List[str]:
    """
    Extract column names from various types of PySpark expressions.

    Args:
        condition_or_expr: Can be a string, PySpark Column, or other expression

    Returns:
        List of column names found in the expression
    """
    import re

    # Convert to string representation
    if hasattr(condition_or_expr, '__str__'):
        condition_str = str(condition_or_expr)
    else:
        condition_str = str(condition_or_expr)

    # Use the existing extract_column_references function
    return extract_column_references(condition_str)


def format_row_count(count: int, precision: int = 1) -> str:
    """
    Format row count in a human-readable way.

    Args:
        count: Row count to format
        precision: Number of decimal places for large numbers

    Returns:
        Formatted string (e.g., "1.2M", "150K", "2,500")
    """
    if count >= 1_000_000:
        return f"{count / 1_000_000:.{precision}f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.{precision}f}K"
    else:
        return f"{count:,}"



def calculate_impact_metrics(before_count: int,
                           after_count: int) -> Dict[str, Any]:
    """
    Calculate impact metrics for a transformation.

    Args:
        before_count: Row count before transformation
        after_count: Row count after transformation

    Returns:
        Dictionary with impact metrics
    """
    if before_count == 0:
        return {
            'operation_type': 'creation',
            'absolute_change': after_count,
            'percentage_change': None,
            'magnitude': after_count,
            'impact_description': f"Created {format_row_count(after_count)} records"
        }

    change = after_count - before_count
    percentage_change = (change / before_count) * 100

    if change > 0:
        operation_type = 'growth'
        impact_description = f"Added {format_row_count(abs(change))} records ({abs(percentage_change):.1f}% increase)"
    elif change < 0:
        operation_type = 'reduction'
        impact_description = f"Removed {format_row_count(abs(change))} records ({abs(percentage_change):.1f}% reduction)"
    else:
        operation_type = 'neutral'
        impact_description = "No change in record count"

    return {
        'operation_type': operation_type,
        'absolute_change': change,
        'percentage_change': percentage_change,
        'before_count': before_count,
        'after_count': after_count,
        'before_formatted': format_row_count(before_count),
        'after_formatted': format_row_count(after_count),
        'impact_description': impact_description
    }