"""Operation analysis for business context inference."""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..utils.exceptions import InferenceError

logger = logging.getLogger(__name__)


class OperationCategory(Enum):
    """Categories of operations for business context."""
    FILTERING = "filtering"
    SELECTION = "selection"
    TRANSFORMATION = "transformation"
    AGGREGATION = "aggregation"
    ENRICHMENT = "enrichment"
    QUALITY = "quality"
    OPTIMIZATION = "optimization"


@dataclass
class OperationContext:
    """Context information about a data operation."""
    operation_type: str
    category: OperationCategory
    business_intent: str
    confidence: float
    details: Dict[str, Any]


class OperationAnalyzer:
    """Analyzes operations to determine business context."""

    def __init__(self):
        """Initialize the operation analyzer."""
        self.filter_patterns = self._load_filter_patterns()
        self.join_patterns = self._load_join_patterns()
        self.aggregation_patterns = self._load_aggregation_patterns()

    def _load_filter_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for analyzing filter operations."""
        return {
            # Value-based filters
            'high_value': {
                'patterns': [r'>\s*\d+', r'>=\s*\d+'],
                'keywords': ['value', 'amount', 'price', 'revenue', 'income'],
                'template': 'High-Value {domain}',
                'confidence_boost': 0.3,
                'category': OperationCategory.FILTERING
            },
            'low_value': {
                'patterns': [r'<\s*\d+', r'<=\s*\d+'],
                'keywords': ['value', 'amount', 'price', 'cost'],
                'template': 'Low-Value {domain}',
                'confidence_boost': 0.2,
                'category': OperationCategory.FILTERING
            },
            'value_range': {
                'patterns': [r'between\s+\d+\s+and\s+\d+', r'>\s*\d+.*<\s*\d+'],
                'keywords': ['value', 'amount', 'range'],
                'template': 'Value Range {domain}',
                'confidence_boost': 0.25,
                'category': OperationCategory.FILTERING
            },

            # Status-based filters
            'active_status': {
                'patterns': [r"==\s*['\"]active['\"]", r"=\s*['\"]active['\"]"],
                'keywords': ['status', 'state', 'active'],
                'template': 'Active {domain}',
                'confidence_boost': 0.4,
                'category': OperationCategory.FILTERING
            },
            'inactive_status': {
                'patterns': [r"==\s*['\"]inactive['\"]", r"!=\s*['\"]active['\"]"],
                'keywords': ['status', 'state', 'inactive'],
                'template': 'Inactive {domain}',
                'confidence_boost': 0.3,
                'category': OperationCategory.FILTERING
            },

            # Time-based filters
            'recent_time': {
                'patterns': [r'>\s*[\'\"]?\d{4}-\d{2}-\d{2}', r'after.*\d{4}'],
                'keywords': ['date', 'time', 'created', 'updated'],
                'template': 'Recent {domain}',
                'confidence_boost': 0.3,
                'category': OperationCategory.FILTERING
            },
            'historical_time': {
                'patterns': [r'<\s*[\'\"]?\d{4}-\d{2}-\d{2}', r'before.*\d{4}'],
                'keywords': ['date', 'time', 'historical'],
                'template': 'Historical {domain}',
                'confidence_boost': 0.25,
                'category': OperationCategory.FILTERING
            },

            # Quality filters
            'not_null': {
                'patterns': [r'isNotNull\(\)', r'is not null'],
                'keywords': ['null', 'missing', 'quality'],
                'template': 'Data Quality {domain}',
                'confidence_boost': 0.35,
                'category': OperationCategory.QUALITY
            },
            'null_check': {
                'patterns': [r'isNull\(\)', r'is null'],
                'keywords': ['null', 'missing'],
                'template': 'Missing Data {domain}',
                'confidence_boost': 0.3,
                'category': OperationCategory.QUALITY
            },

            # Category filters
            'category_match': {
                'patterns': [r"==\s*['\"][^'\"]+['\"]", r"=\s*['\"][^'\"]+['\"]"],
                'keywords': ['category', 'type', 'class', 'segment'],
                'template': 'Category {domain}',
                'confidence_boost': 0.2,
                'category': OperationCategory.FILTERING
            },
            'in_list': {
                'patterns': [r'\.isin\(', r' in \[', r' in \('],
                'keywords': ['list', 'options', 'choices'],
                'template': 'Multi-Category {domain}',
                'confidence_boost': 0.25,
                'category': OperationCategory.FILTERING
            },

            # Pattern matching
            'pattern_match': {
                'patterns': [r'like\s*[\'"]', r'contains\s*[\'"]', r'startsWith\s*[\'"]'],
                'keywords': ['pattern', 'search', 'match'],
                'template': 'Pattern Matching {domain}',
                'confidence_boost': 0.2,
                'category': OperationCategory.FILTERING
            },
        }

    def _load_join_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for analyzing join operations."""
        return {
            'inner_join': {
                'join_types': ['inner'],
                'template': '{domain} Enrichment',
                'description': 'Enrich data with matching records only',
                'confidence_boost': 0.3,
                'category': OperationCategory.ENRICHMENT
            },
            'left_join': {
                'join_types': ['left', 'left_outer'],
                'template': '{domain} Enhancement',
                'description': 'Enhance data with additional information',
                'confidence_boost': 0.25,
                'category': OperationCategory.ENRICHMENT
            },
            'broadcast_join': {
                'hints': ['broadcast', 'broadcastjoin'],
                'template': 'Optimized {domain} Lookup',
                'description': 'Performance-optimized data lookup',
                'confidence_boost': 0.2,
                'category': OperationCategory.OPTIMIZATION
            },
            'dimension_join': {
                'keywords': ['dimension', 'lookup', 'reference'],
                'template': '{domain} Dimension Lookup',
                'description': 'Reference data enrichment',
                'confidence_boost': 0.3,
                'category': OperationCategory.ENRICHMENT
            },
        }

    def _load_aggregation_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for analyzing aggregation operations."""
        return {
            'count_aggregation': {
                'functions': ['count', 'countDistinct'],
                'template': '{domain} Counting',
                'description': 'Count records or unique values',
                'confidence_boost': 0.3,
                'category': OperationCategory.AGGREGATION
            },
            'sum_aggregation': {
                'functions': ['sum'],
                'keywords': ['amount', 'value', 'revenue', 'total'],
                'template': '{domain} Summation',
                'description': 'Calculate totals',
                'confidence_boost': 0.3,
                'category': OperationCategory.AGGREGATION
            },
            'avg_aggregation': {
                'functions': ['avg', 'mean'],
                'template': '{domain} Averaging',
                'description': 'Calculate averages',
                'confidence_boost': 0.25,
                'category': OperationCategory.AGGREGATION
            },
            'window_aggregation': {
                'functions': ['row_number', 'rank', 'dense_rank', 'lag', 'lead'],
                'template': '{domain} Window Analysis',
                'description': 'Advanced analytical calculations',
                'confidence_boost': 0.35,
                'category': OperationCategory.AGGREGATION
            },
        }

    def analyze_filter_operation(
        self,
        condition: str,
        columns_involved: List[str],
        primary_domain: Optional[str] = None
    ) -> OperationContext:
        """
        Analyze a filter operation to determine business context.

        Args:
            condition: Filter condition string
            columns_involved: Columns referenced in the filter
            primary_domain: Primary business domain of the columns

        Returns:
            OperationContext with business meaning
        """
        if not condition:
            return OperationContext(
                operation_type='filter',
                category=OperationCategory.FILTERING,
                business_intent='Data Filtering',
                confidence=0.1,
                details={'condition': condition}
            )

        best_match = None
        best_confidence = 0.0

        condition_lower = condition.lower()

        # Try to match against known filter patterns
        for pattern_name, pattern_info in self.filter_patterns.items():
            confidence = 0.0

            # Check regex patterns
            for regex_pattern in pattern_info.get('patterns', []):
                if re.search(regex_pattern, condition, re.IGNORECASE):
                    confidence += 0.4

            # Check keywords in column names
            for keyword in pattern_info.get('keywords', []):
                for column in columns_involved:
                    if keyword in column.lower():
                        confidence += 0.3

            # Apply confidence boost
            confidence += pattern_info.get('confidence_boost', 0.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = (pattern_name, pattern_info)

        if best_match:
            pattern_name, pattern_info = best_match
            domain = primary_domain or 'Data'

            business_intent = pattern_info['template'].format(domain=domain)
            category = pattern_info['category']
        else:
            # Fallback analysis
            business_intent, category = self._analyze_condition_fallback(condition, primary_domain)

        return OperationContext(
            operation_type='filter',
            category=category,
            business_intent=business_intent,
            confidence=min(best_confidence, 1.0),
            details={
                'condition': condition,
                'columns_involved': columns_involved,
                'pattern_matched': best_match[0] if best_match else None,
                'primary_domain': primary_domain
            }
        )

    def analyze_join_operation(
        self,
        join_keys: Union[str, List[str]],
        join_type: str = 'inner',
        primary_domain: Optional[str] = None,
        hints: Optional[List[str]] = None
    ) -> OperationContext:
        """
        Analyze a join operation to determine business context.

        Args:
            join_keys: Column(s) being joined on
            join_type: Type of join (inner, left, etc.)
            primary_domain: Primary business domain
            hints: Any optimization hints

        Returns:
            OperationContext with business meaning
        """
        if isinstance(join_keys, str):
            join_keys = [join_keys]

        best_match = None
        best_confidence = 0.0

        # Analyze join patterns
        for pattern_name, pattern_info in self.join_patterns.items():
            confidence = 0.0

            # Check join type match
            if join_type.lower() in pattern_info.get('join_types', []):
                confidence += 0.4

            # Check hints
            if hints:
                for hint in hints:
                    if hint.lower() in pattern_info.get('hints', []):
                        confidence += 0.3

            # Check keywords in join keys
            for keyword in pattern_info.get('keywords', []):
                for key in join_keys:
                    if keyword in key.lower():
                        confidence += 0.2

            confidence += pattern_info.get('confidence_boost', 0.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = (pattern_name, pattern_info)

        if best_match:
            pattern_name, pattern_info = best_match
            domain = primary_domain or 'Data'
            business_intent = pattern_info['template'].format(domain=domain)
            category = pattern_info['category']
        else:
            # Fallback
            domain = primary_domain or 'Data'
            business_intent = f"{domain} Enrichment"
            category = OperationCategory.ENRICHMENT

        return OperationContext(
            operation_type='join',
            category=category,
            business_intent=business_intent,
            confidence=min(best_confidence, 1.0),
            details={
                'join_keys': join_keys,
                'join_type': join_type,
                'hints': hints or [],
                'pattern_matched': best_match[0] if best_match else None,
                'primary_domain': primary_domain
            }
        )

    def analyze_aggregation_operation(
        self,
        agg_functions: List[str],
        group_by_columns: List[str],
        primary_domain: Optional[str] = None
    ) -> OperationContext:
        """
        Analyze an aggregation operation to determine business context.

        Args:
            agg_functions: Aggregation functions being used
            group_by_columns: Columns being grouped by
            primary_domain: Primary business domain

        Returns:
            OperationContext with business meaning
        """
        best_match = None
        best_confidence = 0.0

        # Analyze aggregation patterns
        for pattern_name, pattern_info in self.aggregation_patterns.items():
            confidence = 0.0

            # Check function match
            for func in agg_functions:
                if func.lower() in [f.lower() for f in pattern_info.get('functions', [])]:
                    confidence += 0.4

            # Check keywords in group by columns
            for keyword in pattern_info.get('keywords', []):
                for column in group_by_columns:
                    if keyword in column.lower():
                        confidence += 0.2

            confidence += pattern_info.get('confidence_boost', 0.0)

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = (pattern_name, pattern_info)

        if best_match:
            pattern_name, pattern_info = best_match
            domain = primary_domain or 'Data'
            business_intent = pattern_info['template'].format(domain=domain)
            category = pattern_info['category']
        else:
            # Fallback
            domain = primary_domain or 'Data'
            business_intent = f"{domain} Aggregation"
            category = OperationCategory.AGGREGATION

        return OperationContext(
            operation_type='aggregation',
            category=category,
            business_intent=business_intent,
            confidence=min(best_confidence, 1.0),
            details={
                'agg_functions': agg_functions,
                'group_by_columns': group_by_columns,
                'pattern_matched': best_match[0] if best_match else None,
                'primary_domain': primary_domain
            }
        )

    def _analyze_condition_fallback(
        self,
        condition: str,
        primary_domain: Optional[str]
    ) -> Tuple[str, OperationCategory]:
        """
        Fallback analysis when no specific pattern matches.

        Args:
            condition: Filter condition
            primary_domain: Primary domain

        Returns:
            Tuple of (business_intent, category)
        """
        condition_lower = condition.lower()
        domain = primary_domain or 'Data'

        # Simple heuristics
        if any(op in condition_lower for op in ['>', '>=', '<', '<=']):
            if any(word in condition_lower for word in ['value', 'amount', 'price']):
                return f"Value-Based {domain} Selection", OperationCategory.FILTERING
            elif any(word in condition_lower for word in ['date', 'time']):
                return f"Time-Based {domain} Selection", OperationCategory.FILTERING
            else:
                return f"Threshold {domain} Selection", OperationCategory.FILTERING

        elif any(op in condition_lower for op in ['==', '=', '!=']):
            return f"{domain} Category Selection", OperationCategory.FILTERING

        elif 'null' in condition_lower:
            return f"{domain} Quality Check", OperationCategory.QUALITY

        else:
            return f"{domain} Filtering", OperationCategory.FILTERING

    def determine_threshold_type(self, condition: str) -> str:
        """
        Determine if a condition represents high/low threshold, etc.

        Args:
            condition: Filter condition string

        Returns:
            Threshold type description
        """
        condition_lower = condition.lower()

        if re.search(r'>\s*\d+', condition):
            # Look for high value indicators
            if any(word in condition_lower for word in ['value', 'amount', 'revenue', 'price']):
                return 'High-Value Selection'
            else:
                return 'Above Threshold'
        elif re.search(r'<\s*\d+', condition):
            return 'Below Threshold'
        elif '==' in condition and any(word in condition_lower for word in ['active', 'enabled', 'true']):
            return 'Active Selection'
        elif '!=' in condition and any(word in condition_lower for word in ['inactive', 'disabled', 'false']):
            return 'Exclusion Filter'
        else:
            return 'Criteria Filtering'

    def extract_operation_metadata(self, operation_context: OperationContext) -> Dict[str, Any]:
        """
        Extract additional metadata from operation context.

        Args:
            operation_context: Operation context to analyze

        Returns:
            Dictionary with additional metadata
        """
        metadata = {
            'category': operation_context.category.value,
            'confidence_level': self._get_confidence_level(operation_context.confidence),
            'business_impact': self._assess_business_impact(operation_context),
            'complexity': self._assess_complexity(operation_context),
        }

        return metadata

    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level."""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        elif confidence >= 0.2:
            return 'low'
        else:
            return 'very_low'

    def _assess_business_impact(self, context: OperationContext) -> str:
        """Assess the business impact of an operation."""
        if context.category in [OperationCategory.FILTERING, OperationCategory.QUALITY]:
            return 'data_reduction'
        elif context.category == OperationCategory.ENRICHMENT:
            return 'data_enhancement'
        elif context.category == OperationCategory.AGGREGATION:
            return 'data_summarization'
        else:
            return 'data_transformation'

    def _assess_complexity(self, context: OperationContext) -> str:
        """Assess the complexity of an operation."""
        if context.operation_type in ['filter', 'select']:
            return 'simple'
        elif context.operation_type in ['join', 'groupby']:
            return 'medium'
        else:
            return 'complex'