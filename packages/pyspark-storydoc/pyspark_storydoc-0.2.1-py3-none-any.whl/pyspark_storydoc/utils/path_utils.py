"""
Path utilities for consistent output directory handling across examples and tests.

This module provides utilities to ensure all examples and tests write their outputs
to the standardized outputs/ directory in the project root, regardless of where
the script is executed from.
"""
import os
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """
    Find the project root directory by looking for marker files.

    Searches upward from the current file location for common project markers:
    - setup.py
    - pyproject.toml
    - .git directory
    - pyspark_storydoc package directory

    Returns:
        Path to the project root directory

    Raises:
        RuntimeError: If project root cannot be determined
    """
    # Start from this file's location
    current = Path(__file__).resolve().parent

    # Search upward for project markers
    markers = ['setup.py', 'pyproject.toml', '.git', 'pyspark_storydoc']

    for _ in range(10):  # Limit search depth to prevent infinite loops
        for marker in markers:
            marker_path = current / marker
            if marker_path.exists():
                return current

        # Move up one directory
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    raise RuntimeError(
        "Could not determine project root. Ensure the script is run from within "
        "the PySpark Business Explainer project directory."
    )


def get_output_path(relative_path: str, category: str = "examples") -> str:
    """
    Get an absolute output path in the standardized outputs/ directory.

    This ensures all examples and tests write to:
    - outputs/examples/... for examples
    - outputs/tests/... for tests

    Args:
        relative_path: Relative path within the category (e.g., "reporting/video_streaming")
        category: Either "examples" or "tests" (default: "examples")

    Returns:
        Absolute path string to the output directory

    Example:
        >>> get_output_path("reporting/video_streaming")
        '/path/to/project/outputs/examples/reporting/video_streaming'

        >>> get_output_path("unit/test_lineage", category="tests")
        '/path/to/project/outputs/tests/unit/test_lineage'
    """
    if category not in ("examples", "tests"):
        raise ValueError(f"Category must be 'examples' or 'tests', got: {category}")

    project_root = get_project_root()
    output_dir = project_root / "outputs" / category / relative_path

    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    return str(output_dir)


def get_asset_path(relative_path: str, asset_type: str = "diagrams", category: str = "examples") -> str:
    """
    Get an absolute path for assets (diagrams, charts, etc.) in the outputs directory.

    Assets are organized as:
    - outputs/examples/.../assets/{asset_type}/
    - outputs/tests/.../assets/{asset_type}/

    Args:
        relative_path: Relative path within the category (e.g., "reporting/video_streaming")
        asset_type: Type of asset (e.g., "diagrams", "charts", "distribution_analysis")
        category: Either "examples" or "tests" (default: "examples")

    Returns:
        Absolute path string to the asset directory

    Example:
        >>> get_asset_path("reporting/video_streaming", "distribution_analysis")
        '/path/to/project/outputs/examples/reporting/video_streaming/assets/distribution_analysis'
    """
    base_output = get_output_path(relative_path, category)
    asset_dir = Path(base_output) / "assets" / asset_type

    # Create directory if it doesn't exist
    asset_dir.mkdir(parents=True, exist_ok=True)

    return str(asset_dir)


def get_example_output_path(example_name: str) -> str:
    """
    Convenience function for examples.

    Args:
        example_name: Name/path of the example (e.g., "reporting/video_streaming")

    Returns:
        Absolute path to outputs/examples/{example_name}
    """
    return get_output_path(example_name, category="examples")


def get_test_output_path(test_name: str) -> str:
    """
    Convenience function for tests.

    Args:
        test_name: Name/path of the test (e.g., "unit/test_lineage")

    Returns:
        Absolute path to outputs/tests/{test_name}
    """
    return get_output_path(test_name, category="tests")
