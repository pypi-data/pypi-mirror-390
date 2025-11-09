"""Main business inference engine that coordinates pattern matching and operation analysis."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from ..utils.exceptions import InferenceError
from .column_patterns import ColumnPatternMatcher, PatternMatch
from .operation_analyzer import OperationAnalyzer, OperationContext

logger = logging.getLogger(__name__)


@dataclass
class BusinessContext:
    """Represents the inferred business context for an operation."""
    primary_domain: str
    description: str
    confidence: float
    operation_type: str
    involved_columns: List[str]
    pattern_matches: Dict[str, PatternMatch]
    metadata: Dict[str, Any]


class BusinessInferenceEngine:
    """
    Main engine for inferring business context from PySpark operations.

    This engine combines column pattern matching with operation analysis
    to provide intelligent business context inference for data transformations.
    """

    def __init__(self):
        """Initialize the inference engine with pattern matcher and operation analyzer."""
        self.pattern_matcher = ColumnPatternMatcher()
        self.operation_analyzer = OperationAnalyzer()

        # Cache for performance
        self._column_match_cache: Dict[str, PatternMatch] = {}
        self._context_cache: Dict[str, BusinessContext] = {}

        logger.debug("Initialized BusinessInferenceEngine")

    def infer_filter_context(self, columns: List[str], condition: str) -> str:
        """
        Infer business context for filter operations.

        Args:
            columns: Column names involved in the filter
            condition: Filter condition string

        Returns:
            Business-friendly description of the filter operation
        """
        try:
            # Get pattern matches for involved columns
            pattern_matches = self._get_column_matches(columns)

            if not pattern_matches:
                return self._fallback_filter_description(columns, condition)

            # Get the primary domain
            primary_domain = self.pattern_matcher.get_primary_domain(columns)
            if not primary_domain:
                primary_domain = list(pattern_matches.values())[0].pattern.domain

            # Analyze the operation context
            operation_context = self.operation_analyzer.analyze_filter_operation(
                columns, condition, pattern_matches
            )

            # Generate business description
            if operation_context.template:
                description = operation_context.template.format(
                    domain=primary_domain,
                    **operation_context.template_params
                )
            else:
                description = f"{primary_domain} Filtering"

            logger.debug(f"Inferred filter context: {description}")
            return description

        except Exception as e:
            logger.warning(f"Failed to infer filter context: {e}")
            return self._fallback_filter_description(columns, condition)

    def infer_join_context(self, columns: List[str], join_type: str) -> str:
        """
        Infer business context for join operations.

        Args:
            columns: Column names involved in the join
            join_type: Type of join (inner, left, right, etc.)

        Returns:
            Business-friendly description of the join operation
        """
        try:
            # Get pattern matches for join columns
            pattern_matches = self._get_column_matches(columns)

            if not pattern_matches:
                return self._fallback_join_description(columns, join_type)

            # Analyze the join operation
            operation_context = self.operation_analyzer.analyze_join_operation(
                columns, join_type, pattern_matches
            )

            # Generate business description
            if operation_context.template:
                description = operation_context.template.format(
                    join_type=join_type.title(),
                    **operation_context.template_params
                )
            else:
                primary_domain = self.pattern_matcher.get_primary_domain(columns)
                description = f"{primary_domain or 'Data'} {join_type.title()} Join"

            logger.debug(f"Inferred join context: {description}")
            return description

        except Exception as e:
            logger.warning(f"Failed to infer join context: {e}")
            return self._fallback_join_description(columns, join_type)

    def infer_aggregation_context(self, group_columns: List[str], agg_columns: List[str]) -> str:
        """
        Infer business context for aggregation operations.

        Args:
            group_columns: Columns used for grouping
            agg_columns: Columns being aggregated

        Returns:
            Business-friendly description of the aggregation operation
        """
        try:
            all_columns = group_columns + agg_columns
            pattern_matches = self._get_column_matches(all_columns)

            if not pattern_matches:
                return self._fallback_aggregation_description(group_columns, agg_columns)

            # Analyze the aggregation operation
            operation_context = self.operation_analyzer.analyze_aggregation_operation(
                group_columns, agg_columns, pattern_matches
            )

            # Generate business description
            if operation_context.template:
                description = operation_context.template.format(
                    **operation_context.template_params
                )
            else:
                primary_domain = self.pattern_matcher.get_primary_domain(all_columns)
                description = f"{primary_domain or 'Data'} Analysis"

            logger.debug(f"Inferred aggregation context: {description}")
            return description

        except Exception as e:
            logger.warning(f"Failed to infer aggregation context: {e}")
            return self._fallback_aggregation_description(group_columns, agg_columns)

    def infer_general_context(self, operation_type: str, columns: List[str]) -> str:
        """
        Infer business context for general operations.

        Args:
            operation_type: Type of operation
            columns: Columns involved in the operation

        Returns:
            Business-friendly description of the operation
        """
        try:
            pattern_matches = self._get_column_matches(columns)
            primary_domain = self.pattern_matcher.get_primary_domain(columns)

            if primary_domain:
                return f"{primary_domain} {operation_type.title()}"
            elif pattern_matches:
                # Use the domain from the highest confidence match
                best_match = max(pattern_matches.values(), key=lambda m: m.confidence)
                return f"{best_match.pattern.domain} {operation_type.title()}"
            else:
                return f"{operation_type.title()} Operation"

        except Exception as e:
            logger.warning(f"Failed to infer general context: {e}")
            return f"{operation_type.title()} Operation"

    def infer_comprehensive_context(
        self,
        operation_type: str,
        columns: List[str],
        condition: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> BusinessContext:
        """
        Perform comprehensive business context inference.

        Args:
            operation_type: Type of operation
            columns: Columns involved in the operation
            condition: Optional condition string
            additional_metadata: Additional context metadata

        Returns:
            Complete BusinessContext object with detailed analysis
        """
        try:
            # Get pattern matches
            pattern_matches = self._get_column_matches(columns)
            primary_domain = self.pattern_matcher.get_primary_domain(columns)

            # Determine confidence
            if pattern_matches:
                avg_confidence = sum(m.confidence for m in pattern_matches.values()) / len(pattern_matches)
                confidence = min(avg_confidence, 0.95)  # Cap at 95%
            else:
                confidence = 0.2  # Low confidence for no matches

            # Generate description based on operation type
            if operation_type == 'filter':
                description = self.infer_filter_context(columns, condition or "")
            elif operation_type == 'join':
                description = self.infer_join_context(columns, "inner")
            elif operation_type in ['groupBy', 'agg']:
                description = self.infer_aggregation_context(columns[:1], columns[1:])
            else:
                description = self.infer_general_context(operation_type, columns)

            # Build metadata
            metadata = {
                'operation_type': operation_type,
                'column_count': len(columns),
                'has_condition': condition is not None,
                'pattern_match_count': len(pattern_matches),
                'inference_method': 'pattern_matching' if pattern_matches else 'fallback'
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            return BusinessContext(
                primary_domain=primary_domain or "General Data",
                description=description,
                confidence=confidence,
                operation_type=operation_type,
                involved_columns=columns,
                pattern_matches=pattern_matches,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Comprehensive context inference failed: {e}")
            # Return minimal context
            return BusinessContext(
                primary_domain="Unknown",
                description=f"{operation_type.title()} Operation",
                confidence=0.1,
                operation_type=operation_type,
                involved_columns=columns,
                pattern_matches={},
                metadata={'error': str(e)}
            )

    def add_custom_pattern(self, pattern) -> None:
        """
        Add a custom column pattern to the matcher.

        Args:
            pattern: ColumnPattern to add
        """
        self.pattern_matcher.add_custom_pattern(pattern)
        # Clear cache since patterns have changed
        self._column_match_cache.clear()
        self._context_cache.clear()
        logger.debug("Added custom pattern and cleared caches")

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about pattern matching performance."""
        pattern_stats = self.pattern_matcher.get_statistics()

        return {
            'pattern_matcher': pattern_stats,
            'cache_stats': {
                'column_match_cache_size': len(self._column_match_cache),
                'context_cache_size': len(self._context_cache),
            },
            'engine_info': {
                'analyzer_loaded': self.operation_analyzer is not None,
                'pattern_matcher_loaded': self.pattern_matcher is not None,
            }
        }

    def clear_caches(self) -> None:
        """Clear all inference caches."""
        self._column_match_cache.clear()
        self._context_cache.clear()
        logger.debug("Cleared inference caches")

    def _get_column_matches(self, columns: List[str]) -> Dict[str, PatternMatch]:
        """Get pattern matches for columns, using cache when possible."""
        matches = {}

        for column in columns:
            if column in self._column_match_cache:
                matches[column] = self._column_match_cache[column]
            else:
                match = self.pattern_matcher.match_column(column)
                if match:
                    self._column_match_cache[column] = match
                    matches[column] = match

        return matches

    def _fallback_filter_description(self, columns: List[str], condition: str) -> str:
        """Generate fallback description for filter operations."""
        if len(columns) == 1:
            return f"{columns[0].replace('_', ' ').title()} Filtering"
        else:
            return f"Multi-Column Filtering ({len(columns)} columns)"

    def _fallback_join_description(self, columns: List[str], join_type: str) -> str:
        """Generate fallback description for join operations."""
        if len(columns) == 1:
            return f"{join_type.title()} Join on {columns[0].replace('_', ' ').title()}"
        else:
            return f"{join_type.title()} Join ({len(columns)} columns)"

    def _fallback_aggregation_description(self, group_columns: List[str], agg_columns: List[str]) -> str:
        """Generate fallback description for aggregation operations."""
        if group_columns:
            group_desc = f"by {group_columns[0].replace('_', ' ').title()}"
            if len(group_columns) > 1:
                group_desc += f" (+{len(group_columns)-1} others)"
        else:
            group_desc = "Overall"

        return f"Data Analysis {group_desc}"