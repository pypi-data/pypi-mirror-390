"""Base classes for all report types."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Base configuration for all reports."""
    output_directory: Optional[str] = None
    asset_directory: Optional[str] = None
    filename_prefix: str = ""


class BaseReport(ABC):
    """
    Abstract base class for all report types.

    This class defines the interface that all report implementations must follow,
    ensuring consistency across the reporting system.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        """
        Initialize the report generator.

        Args:
            config: Report configuration settings
        """
        self.config = config or ReportConfig()
        self._validate_config()

    @abstractmethod
    def generate(self, lineage_graph, output_path: str) -> str:
        """
        Generate the report and write to file.

        Args:
            lineage_graph: Lineage graph to analyze (LineageGraph or EnhancedLineageGraph)
            output_path: Path where the report should be written

        Returns:
            Path to the generated report file

        Raises:
            ValueError: If lineage_graph is invalid
            IOError: If unable to write to output_path
        """
        pass

    def _validate_config(self) -> bool:
        """
        Validate configuration parameters.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Default implementation - subclasses can override
        return True

    def get_assets_directory(self, output_path: str) -> Path:
        """
        Get the assets directory for this report.

        Args:
            output_path: The main report output path

        Returns:
            Path to the assets directory
        """
        if self.config.asset_directory:
            return Path(self.config.asset_directory)

        # Default: assets directory next to the report file
        report_dir = Path(output_path).parent
        return report_dir / "assets"

    def _ensure_output_directory(self, output_path: str) -> None:
        """
        Ensure the output directory exists.

        Args:
            output_path: Path to the output file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_file.parent}")

    def _write_report(self, content: str, output_path: str) -> str:
        """
        Write report content to file.

        Args:
            content: Markdown content to write
            output_path: Path to write the file

        Returns:
            Path to the written file
        """
        self._ensure_output_directory(output_path)

        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Report written to: {output_file}")
        return str(output_file)

    def _get_user_context(self) -> dict:
        """
        Get user context from Spark/Databricks environment.

        Returns:
            Dictionary with user information:
                - username: User running the script
                - environment: 'Databricks' or 'Spark' or 'Unknown'
        """
        context = {
            'username': 'Unknown',
            'environment': 'Unknown'
        }

        try:
            # Try to get Databricks context first
            try:
                # Check if running in Databricks
                from pyspark.dbutils import DBUtils
                from pyspark.sql import SparkSession

                spark = SparkSession.builder.getOrCreate()
                dbutils = DBUtils(spark)

                # Get current user from Databricks
                username = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get()
                context['username'] = username
                context['environment'] = 'Databricks'
                return context
            except:
                pass

            # Try to get from Spark configuration
            try:
                from pyspark.sql import SparkSession
                spark = SparkSession.builder.getOrCreate()

                # Try spark.sparkContext.sparkUser()
                if hasattr(spark.sparkContext, 'sparkUser'):
                    username = spark.sparkContext.sparkUser()
                    if username:
                        context['username'] = username
                        context['environment'] = 'Spark'
                        return context

                # Try from spark conf
                username = spark.conf.get("spark.user", None)
                if username:
                    context['username'] = username
                    context['environment'] = 'Spark'
                    return context
            except:
                pass

            # Try to get OS user as fallback
            try:
                import getpass
                context['username'] = getpass.getuser()
                context['environment'] = 'Local'
            except:
                pass

        except Exception as e:
            logger.debug(f"Could not determine user context: {e}")

        return context

    def _get_git_context(self) -> dict:
        """
        Get git repository context if available.

        Returns:
            Dictionary with git information:
                - project_name: Git repository name
                - commit_id: Current commit SHA hash
                - has_git: True if git is available and we're in a repo
        """
        context = {
            'project_name': None,
            'commit_id': None,
            'has_git': False
        }

        try:
            import os
            import subprocess

            # Check if git is installed and we're in a git repository
            try:
                # Get the root directory of the git repository
                result = subprocess.run(
                    ['git', 'rev-parse', '--show-toplevel'],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=os.getcwd()
                )
                repo_root = result.stdout.strip()

                # Get the repository name from the root directory
                context['project_name'] = os.path.basename(repo_root)

                # Get the current commit ID
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=os.getcwd()
                )
                context['commit_id'] = result.stdout.strip()

                context['has_git'] = True

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Git not installed or not in a git repository
                pass

        except Exception as e:
            logger.debug(f"Could not determine git context: {e}")

        return context

    def _generate_metadata_section(self) -> list:
        """
        Generate standardized metadata section for all reports.

        Returns:
            List of markdown lines containing generation metadata
        """
        lines = []

        # Get contexts
        user_context = self._get_user_context()
        git_context = self._get_git_context()

        # Generation timestamp
        import time
        lines.append("**Generated:** {}".format(self._format_timestamp(time.time())))

        # User information
        lines.append(f"**Generated By:** {user_context['username']}")

        # Environment
        if user_context['environment'] != 'Unknown':
            lines.append(f"**Environment:** {user_context['environment']}")

        # Git information
        if git_context['has_git']:
            if git_context['project_name']:
                lines.append(f"**Git Project:** {git_context['project_name']}")
            if git_context['commit_id']:
                lines.append(f"**Commit ID:** {git_context['commit_id'][:8]}")  # Short hash

        return lines

    def _format_timestamp(self, timestamp: float) -> str:
        """
        Format a timestamp for display.

        Args:
            timestamp: Unix timestamp

        Returns:
            Formatted timestamp string
        """
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _format_duration(self, seconds: float) -> str:
        """
        Format a duration for display.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration (e.g., "2.5s", "1m 30s")
        """
        if seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            mins = int(seconds // 60)
            secs = seconds % 60
            return f"{mins}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            return f"{hours}h {mins}m"

    def _format_number(self, number: int) -> str:
        """
        Format a number with thousands separators.

        Args:
            number: Number to format

        Returns:
            Formatted number (e.g., "1,234,567")
        """
        return f"{number:,}"

    def _format_percentage(self, value: float, decimals: int = 1) -> str:
        """
        Format a percentage value.

        Args:
            value: Percentage value (0-100)
            decimals: Number of decimal places

        Returns:
            Formatted percentage (e.g., "15.5%")
        """
        return f"{value:.{decimals}f}%"

    def _truncate_text(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
