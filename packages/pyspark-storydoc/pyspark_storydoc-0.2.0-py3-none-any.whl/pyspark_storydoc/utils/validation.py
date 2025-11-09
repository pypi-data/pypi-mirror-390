"""Input validation utilities."""

import re
from typing import Any, List, Optional, Union

from .exceptions import ValidationError


def validate_column_names(column_names: List[str],
                         available_columns: Optional[List[str]] = None) -> None:
    """
    Validate column names.

    Args:
        column_names: List of column names to validate
        available_columns: Optional list of available columns for validation

    Raises:
        ValidationError: If column names are invalid
    """
    if column_names is None:
        raise ValidationError(
            "Column names cannot be None",
            parameter_name="column_names",
            parameter_value=column_names,
            expected_type=list
        )

    if not isinstance(column_names, list):
        raise ValidationError(
            "Column names must be provided as a list",
            parameter_name="column_names",
            parameter_value=column_names,
            expected_type=list
        )

    # Empty list is valid - some operations may not track specific columns

    for col_name in column_names:
        if not isinstance(col_name, str):
            raise ValidationError(
                f"Column name must be a string, got {type(col_name).__name__}",
                parameter_name="column_name",
                parameter_value=col_name,
                expected_type=str
            )

        if not col_name.strip():
            raise ValidationError(
                "Column name cannot be empty or whitespace only",
                parameter_name="column_name",
                parameter_value=col_name
            )

    # Validate against available columns if provided
    if available_columns is not None:
        invalid_columns = set(column_names) - set(available_columns)
        if invalid_columns:
            raise ValidationError(
                f"Column(s) not found in DataFrame: {', '.join(invalid_columns)}",
                parameter_name="column_names",
                parameter_value=list(invalid_columns)
            )


def validate_business_concept_name(name: str) -> None:
    """
    Validate business concept name.

    Args:
        name: Business concept name to validate

    Raises:
        ValidationError: If name is invalid
    """
    if name is None:
        raise ValidationError(
            "Business concept name cannot be None",
            parameter_name="name",
            parameter_value=name,
            expected_type=str
        )

    if not isinstance(name, str):
        raise ValidationError(
            "Business concept name must be a string",
            parameter_name="name",
            parameter_value=name,
            expected_type=str
        )

    if not name.strip():
        raise ValidationError(
            "Business concept name cannot be empty or whitespace only",
            parameter_name="name",
            parameter_value=name
        )

    # Check minimum length (at least 2 characters)
    if len(name.strip()) < 2:
        raise ValidationError(
            "Business concept name must be at least 2 characters long",
            parameter_name="name",
            parameter_value=name
        )

    # Check for reasonable length
    if len(name.strip()) > 200:
        raise ValidationError(
            "Business concept name is too long (maximum 200 characters)",
            parameter_name="name",
            parameter_value=name
        )

    # Ensure it doesn't contain invalid characters for visualization
    invalid_chars = ['<', '>', '{', '}', '[', ']', '|', '\\', '"']
    for char in invalid_chars:
        if char in name:
            raise ValidationError(
                f"Business concept name contains invalid character: '{char}'",
                parameter_name="name",
                parameter_value=name
            )


def validate_description(description: Optional[str]) -> None:
    """
    Validate business concept description.

    Args:
        description: Description to validate

    Raises:
        ValidationError: If description is invalid
    """
    if description is None:
        return

    if not isinstance(description, str):
        raise ValidationError(
            "Description must be a string",
            parameter_name="description",
            parameter_value=description,
            expected_type=str
        )

    # Check for empty or whitespace-only strings
    if not description.strip():
        raise ValidationError(
            "Description cannot be empty or whitespace only",
            parameter_name="description",
            parameter_value=description
        )

    # Check minimum length (at least 2 characters)
    if len(description.strip()) < 2:
        raise ValidationError(
            "Description must be at least 2 characters long",
            parameter_name="description",
            parameter_value=description
        )

    # Check for reasonable length
    if len(description) > 1000:
        raise ValidationError(
            "Description is too long (maximum 1000 characters)",
            parameter_name="description",
            parameter_value=description
        )


def validate_track_columns(track_columns: Optional[List[str]]) -> None:
    """
    Validate track_columns parameter.

    Args:
        track_columns: List of columns to track

    Raises:
        ValidationError: If track_columns is invalid
    """
    if track_columns is None:
        return

    if not isinstance(track_columns, list):
        raise ValidationError(
            "track_columns must be a list",
            parameter_name="track_columns",
            parameter_value=track_columns,
            expected_type=list
        )

    validate_column_names(track_columns)


def validate_materialize_setting(materialize: Any) -> None:
    """
    Validate materialize parameter.

    Args:
        materialize: Materialize setting to validate

    Raises:
        ValidationError: If materialize setting is invalid
    """
    if not isinstance(materialize, bool):
        raise ValidationError(
            "materialize must be a boolean",
            parameter_name="materialize",
            parameter_value=materialize,
            expected_type=bool
        )


def validate_metadata(metadata: Optional[dict]) -> None:
    """
    Validate metadata parameter.

    Args:
        metadata: Metadata dictionary to validate

    Raises:
        ValidationError: If metadata is invalid
    """
    if metadata is None:
        return

    if not isinstance(metadata, dict):
        raise ValidationError(
            "metadata must be a dictionary",
            parameter_name="metadata",
            parameter_value=metadata,
            expected_type=dict
        )

    # Validate that all keys are strings
    for key in metadata.keys():
        if not isinstance(key, str):
            raise ValidationError(
                f"metadata keys must be strings, got {type(key).__name__}",
                parameter_name="metadata_key",
                parameter_value=key,
                expected_type=str
            )


def validate_function_for_decoration(func: Any) -> None:
    """
    Validate that a function can be decorated with business concept.

    Args:
        func: Function to validate

    Raises:
        ValidationError: If function cannot be decorated
    """
    if not callable(func):
        raise ValidationError(
            "Object is not callable and cannot be decorated",
            parameter_name="func",
            parameter_value=func
        )

    # Check if function has reasonable signature
    import inspect
    try:
        signature = inspect.signature(func)
        # Ensure function has at least one parameter (likely a DataFrame)
        if len(signature.parameters) == 0:
            raise ValidationError(
                "Function must have at least one parameter",
                parameter_name="func",
                parameter_value=func.__name__ if hasattr(func, '__name__') else str(func)
            )
    except (ValueError, TypeError) as e:
        # Some built-in functions don't have inspectable signatures
        # We'll allow them but log a warning
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not inspect function signature for {func}: {e}")


def is_valid_identifier(name: str) -> bool:
    """
    Check if a string is a valid Python identifier.

    Args:
        name: String to check

    Returns:
        True if the string is a valid identifier, False otherwise
    """
    return name.isidentifier()


def sanitize_for_visualization(text: str, max_length: int = 50) -> str:
    """
    Sanitize text for use in visualization outputs.

    Args:
        text: Text to sanitize
        max_length: Maximum length for the text

    Returns:
        Sanitized text suitable for visualization
    """
    if not isinstance(text, str):
        text = str(text)

    # Remove or replace problematic characters
    sanitized = text.replace('<', '&lt;').replace('>', '&gt;')
    sanitized = sanitized.replace('{', '').replace('}', '')
    sanitized = sanitized.replace('[', '(').replace(']', ')')
    sanitized = sanitized.replace('|', ' ')
    sanitized = sanitized.replace('"', "'")

    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."

    return sanitized