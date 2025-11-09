"""
PySpark StoryDoc

Transform technical PySpark operations into stakeholder-friendly business documentation.

This package provides automatic lineage tracking and visualization for PySpark DataFrames,
making it easy to explain data transformations to non-technical stakeholders.

Quick Start:
    >>> from pyspark_storydoc import businessConcept, LineageDataFrame
    >>>
    >>> @businessConcept('Customer Analysis')
    >>> def analyze_customers(df):
    ...     return df.filter(col('status') == 'active')
    >>>
    >>> tracked_df = LineageDataFrame(spark_df, business_label="Customer Data")
    >>> result = analyze_customers(tracked_df)

For advanced features, use explicit imports:
    >>> from pyspark_storydoc.visualization import MermaidGenerator
    >>> from pyspark_storydoc.utils import export_lineage_to_json
"""

from .analysis.expression_lineage_decorator import expressionLineage
from .core.context_managers import business_context

# Core API - Essential functionality for 90% of users
from .core.decorators import businessConcept, track_lineage
from .core.graph_builder import LineageGraph
from .core.hierarchy_context import (
    businessConceptHierarchy,
    get_concept_hierarchy,
    get_concept_path,
    get_hierarchy_depth,
    is_in_hierarchy,
)
from .core.lineage_dataframe import LineageDataFrame, wrap_dataframe
from .core.lineage_tracker import get_enhanced_tracker as get_global_tracker
from .version import __author__, __description__, __email__, __version__

__all__ = [
    # Version information
    '__version__',
    '__author__',
    '__email__',
    '__description__',

    # Core functionality
    'businessConcept',
    'track_lineage',
    'businessConceptHierarchy',
    'get_concept_hierarchy',
    'get_concept_path',
    'get_hierarchy_depth',
    'is_in_hierarchy',
    'LineageDataFrame',
    'wrap_dataframe',
    'business_context',
    'get_global_tracker',
    'LineageGraph',
    'expressionLineage',
]

# Package-level configuration
import logging

# Set up package logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Module-level constants
DEFAULT_MATERIALIZE = True
DEFAULT_TRACK_COLUMNS = ['id', 'customer_id', 'user_id', 'account_id']

# Advanced features available via explicit imports:
#
# Context Managers:
#   from pyspark_storydoc.core.context_managers import (
#       performance_context, debug_context, audit_context, temporary_context
#   )
#
# Visualization:
#   from pyspark_storydoc.visualization import (
#       MermaidGenerator, MermaidTheme, MermaidStyle,
#       GraphvizGenerator, GraphvizLayout, GraphvizFormat, GraphvizStyle,
#       BusinessLineageVisualizer, ExportFormat, VisualizationConfig
#   )
#
# Utilities:
#   from pyspark_storydoc.utils import (
#       export_lineage_to_json,
#       export_business_concepts_summary,
#       generate_lineage_report
#   )
#
# Exceptions:
#   from pyspark_storydoc.utils.exceptions import (
#       PySparkStoryDocError,
#       LineageTrackingError,
#       InferenceError,
#       VisualizationError
#   )
