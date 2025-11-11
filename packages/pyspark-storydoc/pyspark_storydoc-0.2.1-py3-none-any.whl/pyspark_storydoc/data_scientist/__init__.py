"""
Data Scientist Module for PySpark StoryDoc

Provides specialized outputs for data scientists focusing on:
- Feature lineage and understanding
- Data exploration and profiling
- Reproducibility documentation
- Statistical analysis support
"""

from .feature_catalog import (
    FeatureCatalog,
    FeatureCatalogConfig,
    generate_feature_catalog,
)
from .reproducibility_report import (
    ReproducibilityConfig,
    ReproducibilityReport,
    generate_reproducibility_report,
)
from .statistical_profiler import (
    StatisticalProfile,
    StatisticalProfiler,
    generate_statistical_checkpoint,
)

__all__ = [
    # Feature Catalog
    'FeatureCatalog',
    'FeatureCatalogConfig',
    'generate_feature_catalog',

    # Statistical Profiling
    'StatisticalProfiler',
    'StatisticalProfile',
    'generate_statistical_checkpoint',

    # Reproducibility
    'ReproducibilityReport',
    'ReproducibilityConfig',
    'generate_reproducibility_report',
]
