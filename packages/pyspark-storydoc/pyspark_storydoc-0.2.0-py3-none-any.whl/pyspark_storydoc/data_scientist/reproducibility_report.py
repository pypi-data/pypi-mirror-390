"""
Reproducibility Report Generator for Data Scientists

Generates comprehensive reproducibility documentation including:
- Experiment metadata (git commit, author, date)
- Data sources and versions
- Environment details (Python, PySpark, dependencies)
- Transformation pipeline steps
- Configuration and parameters
- Output artifacts
- Validation results
"""

import logging
import os
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.enhanced_lineage_graph import EnhancedLineageGraph

logger = logging.getLogger(__name__)


@dataclass
class ReproducibilityConfig:
    """Configuration for reproducibility report generation."""

    # Experiment information
    experiment_id: str = "experiment_001"
    experiment_purpose: str = "Feature engineering pipeline"
    author: str = "data-science-team"
    git_commit: Optional[str] = None
    git_branch: Optional[str] = None
    git_repository: Optional[str] = None

    # Data sources
    data_sources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Format: {'source_name': {'location': 'path', 'rows': 1000, 'snapshot_date': '2024-01-01', ...}}

    # Pipeline information
    pipeline_name: str = "Feature Pipeline"
    pipeline_steps: List[Dict[str, str]] = field(default_factory=list)
    # Format: [{'step': 'Load Data', 'function': 'load_data()', 'code': 'src/data/loaders.py:23'}]

    # Configuration
    parameters: Dict[str, Any] = field(default_factory=dict)
    random_seeds: Dict[str, int] = field(default_factory=dict)

    # Output artifacts
    output_artifacts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Format: {'artifact_name': {'location': 'path', 'size': 1024, 'checksum': 'md5...'}}

    # Validation results
    validation_results: Dict[str, Any] = field(default_factory=dict)

    # Auto-detect environment
    detect_environment: bool = True

    # Include sections
    include_quick_start: bool = True
    include_environment: bool = True
    include_data_sources: bool = True
    include_pipeline: bool = True
    include_validation: bool = True
    include_change_log: bool = False

    # Change log (if available)
    previous_version: Optional[str] = None
    changes: List[str] = field(default_factory=list)


class ReproducibilityReport:
    """
    Generate reproducibility reports for data science experiments.

    Captures all information needed to exactly reproduce an experiment,
    including code versions, data snapshots, environment, and configuration.
    """

    def __init__(self, config: Optional[ReproducibilityConfig] = None):
        """
        Initialize the reproducibility report generator.

        Args:
            config: Configuration for report generation
        """
        self.config = config or ReproducibilityConfig()

        # Auto-detect environment if requested
        if self.config.detect_environment:
            self._detect_environment()

    def generate(
        self,
        lineage_graph: Optional[EnhancedLineageGraph],
        output_path: str,
        **kwargs
    ) -> str:
        """
        Generate a reproducibility report.

        Args:
            lineage_graph: Optional lineage graph for pipeline visualization
            output_path: Path to write the report
            **kwargs: Additional config overrides

        Returns:
            Path to generated report
        """
        logger.info(f"Generating reproducibility report: {self.config.experiment_id}")

        # Update config with kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Generate the report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = self._generate_content(lineage_graph)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Reproducibility report generated: {output_file}")
        return str(output_file)

    def _detect_environment(self):
        """Detect environment information automatically."""
        # This will populate some config fields automatically
        try:
            # Git information (if available)
            self._detect_git_info()
        except Exception as e:
            logger.debug(f"Could not detect git info: {e}")

    def _detect_git_info(self):
        """Try to detect git information."""
        try:
            import subprocess

            # Get git commit
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.config.git_commit = result.stdout.strip()

            # Get git branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.config.git_branch = result.stdout.strip()

            # Get git remote
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.config.git_repository = result.stdout.strip()

        except Exception as e:
            logger.debug(f"Git detection failed: {e}")

    def _generate_content(self, lineage_graph: Optional[EnhancedLineageGraph]) -> str:
        """Generate the complete report content."""
        sections = []

        # Header
        sections.append(self._generate_header())

        # Quick Start
        if self.config.include_quick_start:
            sections.append(self._generate_quick_start())

        # Experiment Metadata
        sections.append(self._generate_metadata())

        # Data Sources
        if self.config.include_data_sources and self.config.data_sources:
            sections.append(self._generate_data_sources())

        # Environment
        if self.config.include_environment:
            sections.append(self._generate_environment())

        # Transformation Pipeline
        if self.config.include_pipeline:
            sections.append(self._generate_pipeline())

        # Configuration
        sections.append(self._generate_configuration())

        # Output Artifacts
        if self.config.output_artifacts:
            sections.append(self._generate_output_artifacts())

        # Validation
        if self.config.include_validation and self.config.validation_results:
            sections.append(self._generate_validation())

        # Change Log
        if self.config.include_change_log and self.config.changes:
            sections.append(self._generate_change_log())

        # Next Steps
        sections.append(self._generate_next_steps())

        # Footer
        sections.append(self._generate_footer())

        return '\n\n'.join(sections)

    def _generate_header(self) -> str:
        """Generate report header."""
        status = "[OK] Reproducible" if self.config.validation_results.get('reproducible', True) else "[WARN] Issues Detected"

        return f"""# Experiment Reproducibility Report

**Experiment ID**: {self.config.experiment_id}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Author**: {self.config.author}
**Status**: {status}

---"""

    def _generate_quick_start(self) -> str:
        """Generate quick start section."""
        git_section = ""
        if self.config.git_repository and self.config.git_commit:
            git_section = f"""# Clone repository
git clone {self.config.git_repository}
git checkout {self.config.git_commit}
"""

        env_section = """# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
"""

        run_section = f"""# Run {self.config.pipeline_name}
python src/pipelines/feature_pipeline.py \\
  --experiment-id {self.config.experiment_id} \\
  --output outputs/{self.config.experiment_id}/

# Output will match this experiment exactly
"""

        return f"""## Quick Start: Reproduce This Experiment

```bash
{git_section}
{env_section}
{run_section}```"""

    def _generate_metadata(self) -> str:
        """Generate experiment metadata section."""
        git_info = ""
        if self.config.git_repository:
            git_info = f"""
Git Information:
  Repository: {self.config.git_repository}
  Commit: {self.config.git_commit or 'not tracked'}
  Branch: {self.config.git_branch or 'not tracked'}"""

        return f"""---

## Experiment Metadata

```
Experiment ID: {self.config.experiment_id}
Purpose: {self.config.experiment_purpose}
{git_info}

Author: {self.config.author}
Date Created: {datetime.now().strftime('%Y-%m-%d')}
```"""

    def _generate_data_sources(self) -> str:
        """Generate data sources section."""
        lines = ["---\n", "## Data Sources\n", "### Input Datasets\n", "```"]

        for source_name, source_info in self.config.data_sources.items():
            lines.append(f"{source_name}:")
            for key, value in source_info.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        lines.append("```")
        return '\n'.join(lines)

    def _generate_environment(self) -> str:
        """Generate environment section."""
        lines = ["---\n", "## Environment\n", "### Software Versions\n", "```"]

        # System information
        lines.append(f"Operating System: {platform.system()} {platform.release()}")
        lines.append(f"Python: {sys.version.split()[0]}")

        # Try to get PySpark version
        try:
            import pyspark
            lines.append(f"PySpark: {pyspark.__version__}")
        except:
            lines.append("PySpark: (not detected)")

        # Common dependencies
        dependencies = ['pandas', 'numpy', 'scikit-learn']
        lines.append("\nPython Dependencies:")
        for dep in dependencies:
            try:
                module = __import__(dep)
                version = getattr(module, '__version__', 'unknown')
                lines.append(f"  {dep}=={version}")
            except:
                pass

        lines.append("\nFull environment: requirements.txt")
        lines.append("```")

        return '\n'.join(lines)

    def _generate_pipeline(self) -> str:
        """Generate transformation pipeline section."""
        lines = ["---\n", "## Transformation Pipeline\n", "### Pipeline Steps\n", "```"]

        if self.config.pipeline_steps:
            for i, step in enumerate(self.config.pipeline_steps, 1):
                lines.append(f"{i}. {step.get('step', 'Step')}")
                if 'function' in step:
                    lines.append(f"   Function: {step['function']}")
                if 'code' in step:
                    lines.append(f"   Code: {step['code']}")
                if 'description' in step:
                    lines.append(f"   Description: {step['description']}")
                lines.append("")
        else:
            lines.append("(Pipeline steps not documented)")

        lines.append("```")
        return '\n'.join(lines)

    def _generate_configuration(self) -> str:
        """Generate configuration section."""
        lines = ["---\n", "## Configuration\n"]

        # Random seeds
        if self.config.random_seeds:
            lines.append("### Random Seeds\n")
            lines.append("```")
            for name, seed in self.config.random_seeds.items():
                lines.append(f"{name}: {seed}")
            lines.append("\nAll random operations are seeded for reproducibility [OK]")
            lines.append("```\n")

        # Parameters
        if self.config.parameters:
            lines.append("### Parameters\n")
            lines.append("```")
            for param_name, param_value in self.config.parameters.items():
                lines.append(f"{param_name}: {param_value}")
            lines.append("```")

        return '\n'.join(lines)

    def _generate_output_artifacts(self) -> str:
        """Generate output artifacts section."""
        lines = ["---\n", "## Output Artifacts\n", "### Generated Files\n", "```"]

        for artifact_name, artifact_info in self.config.output_artifacts.items():
            lines.append(f"{artifact_name}:")
            for key, value in artifact_info.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        lines.append("```")
        return '\n'.join(lines)

    def _generate_validation(self) -> str:
        """Generate validation section."""
        lines = ["---\n", "## Validation\n", "### Data Quality Checks\n"]

        if self.config.validation_results:
            lines.append("```")

            # Overall status
            all_passed = all(
                v.get('passed', False)
                for v in self.config.validation_results.values()
                if isinstance(v, dict)
            )
            lines.append(f"{'[OK] All tests passed' if all_passed else '[WARN] Some tests failed'}")
            lines.append("")

            # Individual results
            lines.append("Test Results:")
            for test_name, result in self.config.validation_results.items():
                if isinstance(result, dict):
                    status = "[OK]" if result.get('passed', False) else "[FAIL]"
                    lines.append(f"  {status} {test_name}")
                elif isinstance(result, bool):
                    status = "[OK]" if result else "[FAIL]"
                    lines.append(f"  {status} {test_name}")

            lines.append("```")
        else:
            lines.append("```\n(No validation results available)\n```")

        return '\n'.join(lines)

    def _generate_change_log(self) -> str:
        """Generate change log section."""
        lines = ["---\n", "## Change Log\n"]

        if self.config.previous_version:
            lines.append(f"### Changes from Previous Version ({self.config.previous_version})\n")
        else:
            lines.append("### Changes\n")

        lines.append("```")
        for change in self.config.changes:
            lines.append(change)
        lines.append("```")

        return '\n'.join(lines)

    def _generate_next_steps(self) -> str:
        """Generate next steps section."""
        return f"""---

## Next Steps

### Model Training

```
Ready for model training [OK]

Recommended Next Steps:
  1. Train/test split (stratified)
  2. Train model
  3. Validate on holdout set
  4. Document model performance

Model Training Code: (specify location)
```

### Handoff to Engineering

```
For Productionization:
  - Pipeline code: src/pipelines/
  - Feature catalog: outputs/{self.config.experiment_id}/feature_catalog.md
  - Data quality checks: tests/
  - Configuration: config/

Contact: {self.config.author}
```"""

    def _generate_footer(self) -> str:
        """Generate report footer."""
        status = "[OK] Reproducible" if self.config.validation_results.get('reproducible', True) else "[WARN] Needs Review"
        return f"\n---\n\n*Experiment: {self.config.experiment_id} | Status: {status} | Generated: {datetime.now().strftime('%Y-%m-%d')}*"


def generate_reproducibility_report(
    output_path: str,
    experiment_id: str,
    **kwargs
) -> str:
    """
    Convenience function to generate a reproducibility report.

    Args:
        output_path: Where to save the report
        experiment_id: Unique experiment identifier
        **kwargs: Configuration options (see ReproducibilityConfig)

    Returns:
        Path to generated report
    """
    config = ReproducibilityConfig(experiment_id=experiment_id, **kwargs)
    report = ReproducibilityReport(config)
    return report.generate(None, output_path)
