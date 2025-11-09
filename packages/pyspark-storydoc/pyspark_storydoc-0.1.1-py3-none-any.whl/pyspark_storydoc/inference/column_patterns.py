"""Column pattern matching for business context inference."""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Pattern, Tuple

from ..utils.exceptions import InferenceError

logger = logging.getLogger(__name__)


@dataclass
class ColumnPattern:
    """Represents a pattern for matching column names to business domains."""
    pattern: Pattern[str]
    domain: str
    filter_template: str
    join_template: str
    groupby_template: str
    priority: int = 50  # Higher number = higher priority
    examples: List[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []


@dataclass
class PatternMatch:
    """Represents a successful pattern match."""
    pattern: ColumnPattern
    column_name: str
    confidence: float
    matched_groups: List[str]


class ColumnPatternMatcher:
    """Matches column names to business domain patterns."""

    def __init__(self):
        """Initialize with default patterns."""
        self.patterns: List[ColumnPattern] = []
        self._load_default_patterns()

    def _load_default_patterns(self) -> None:
        """Load default column patterns for common business domains."""

        # Customer-related patterns (high priority)
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*customer.*lifetime.*value.*', re.IGNORECASE),
                domain='Customer Value',
                filter_template='Customer Value {threshold_type}',
                join_template='Customer Value Enrichment',
                groupby_template='Customer Value Analysis',
                priority=90,
                examples=['customer_lifetime_value', 'cust_ltv', 'customer_clv']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*customer.*id.*|.*cust.*id.*', re.IGNORECASE),
                domain='Customer Identity',
                filter_template='Customer Selection',
                join_template='Customer Data Enrichment',
                groupby_template='Customer Grouping',
                priority=85,
                examples=['customer_id', 'cust_id', 'customer_key']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*customer.*acquisition.*date.*', re.IGNORECASE),
                domain='Customer Lifecycle',
                filter_template='Customer Acquisition Filtering',
                join_template='Customer Lifecycle Analysis',
                groupby_template='Customer Cohort Analysis',
                priority=80,
                examples=['customer_acquisition_date', 'cust_acquired_date']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*customer.*segment.*|.*customer.*tier.*', re.IGNORECASE),
                domain='Customer Segmentation',
                filter_template='Customer Segment Selection',
                join_template='Customer Segment Enrichment',
                groupby_template='Customer Segment Analysis',
                priority=75,
                examples=['customer_segment', 'customer_tier', 'cust_category']
            ),
        ])

        # Account-related patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*account.*status.*', re.IGNORECASE),
                domain='Account Management',
                filter_template='Account Status {status_type}',
                join_template='Account Status Validation',
                groupby_template='Account Status Distribution',
                priority=80,
                examples=['account_status', 'acct_status', 'account_state']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*account.*id.*|.*acct.*id.*', re.IGNORECASE),
                domain='Account Identity',
                filter_template='Account Selection',
                join_template='Account Data Enrichment',
                groupby_template='Account Grouping',
                priority=75,
                examples=['account_id', 'acct_id', 'account_number']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*account.*tier.*|.*account.*level.*', re.IGNORECASE),
                domain='Account Hierarchy',
                filter_template='Account Tier Selection',
                join_template='Account Tier Analysis',
                groupby_template='Account Tier Distribution',
                priority=70,
                examples=['account_tier', 'account_level', 'acct_class']
            ),
        ])

        # Transaction and financial patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*transaction.*amount.*|.*order.*value.*|.*purchase.*amount.*', re.IGNORECASE),
                domain='Transaction Value',
                filter_template='Transaction Value {threshold_type}',
                join_template='Transaction Value Analysis',
                groupby_template='Transaction Value Aggregation',
                priority=85,
                examples=['transaction_amount', 'order_value', 'purchase_amount']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*transaction.*date.*|.*order.*date.*|.*purchase.*date.*', re.IGNORECASE),
                domain='Transaction Timing',
                filter_template='Transaction Period Selection',
                join_template='Transaction Temporal Enrichment',
                groupby_template='Transaction Time Analysis',
                priority=80,
                examples=['transaction_date', 'order_date', 'purchase_timestamp']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*transaction.*id.*|.*order.*id.*|.*invoice.*id.*', re.IGNORECASE),
                domain='Transaction Identity',
                filter_template='Transaction Selection',
                join_template='Transaction Data Enrichment',
                groupby_template='Transaction Grouping',
                priority=75,
                examples=['transaction_id', 'order_id', 'invoice_number']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*revenue.*|.*sales.*amount.*', re.IGNORECASE),
                domain='Revenue Analysis',
                filter_template='Revenue {threshold_type}',
                join_template='Revenue Data Enhancement',
                groupby_template='Revenue Aggregation',
                priority=80,
                examples=['revenue', 'total_revenue', 'sales_amount']
            ),
        ])

        # Geographic patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*postal.*code.*|.*zip.*code.*', re.IGNORECASE),
                domain='Geographic Location',
                filter_template='Geographic Area Selection',
                join_template='Geographic Enrichment',
                groupby_template='Geographic Distribution',
                priority=75,
                examples=['postal_code', 'zip_code', 'postcode']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*region.*|.*territory.*', re.IGNORECASE),
                domain='Regional Segmentation',
                filter_template='Regional Selection',
                join_template='Regional Data Enhancement',
                groupby_template='Regional Analysis',
                priority=70,
                examples=['region', 'sales_territory', 'market_region']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*country.*|.*nation.*', re.IGNORECASE),
                domain='Country Analysis',
                filter_template='Country Selection',
                join_template='Country Data Enhancement',
                groupby_template='Country Distribution',
                priority=65,
                examples=['country', 'country_code', 'nation']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*state.*|.*province.*', re.IGNORECASE),
                domain='State/Province Analysis',
                filter_template='State/Province Selection',
                join_template='State/Province Enhancement',
                groupby_template='State/Province Distribution',
                priority=60,
                examples=['state', 'province', 'state_code']
            ),
        ])

        # Product patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*product.*id.*|.*item.*id.*|.*sku.*', re.IGNORECASE),
                domain='Product Identity',
                filter_template='Product Selection',
                join_template='Product Data Enrichment',
                groupby_template='Product Analysis',
                priority=75,
                examples=['product_id', 'item_id', 'sku', 'product_code']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*product.*category.*|.*product.*type.*', re.IGNORECASE),
                domain='Product Classification',
                filter_template='Product Category Selection',
                join_template='Product Category Enhancement',
                groupby_template='Product Category Analysis',
                priority=70,
                examples=['product_category', 'product_type', 'item_category']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*brand.*|.*manufacturer.*', re.IGNORECASE),
                domain='Brand Analysis',
                filter_template='Brand Selection',
                join_template='Brand Data Enhancement',
                groupby_template='Brand Performance Analysis',
                priority=65,
                examples=['brand', 'brand_name', 'manufacturer']
            ),
        ])

        # User and engagement patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*user.*id.*|.*member.*id.*', re.IGNORECASE),
                domain='User Identity',
                filter_template='User Selection',
                join_template='User Data Enrichment',
                groupby_template='User Analysis',
                priority=75,
                examples=['user_id', 'member_id', 'subscriber_id']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*engagement.*score.*|.*activity.*score.*', re.IGNORECASE),
                domain='User Engagement',
                filter_template='Engagement Level Selection',
                join_template='Engagement Analysis',
                groupby_template='Engagement Scoring',
                priority=70,
                examples=['engagement_score', 'activity_score', 'interaction_rating']
            ),
        ])

        # Time-based patterns
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*created.*date.*|.*created.*at.*', re.IGNORECASE),
                domain='Record Creation',
                filter_template='Creation Date Selection',
                join_template='Creation Timeline Enhancement',
                groupby_template='Creation Time Analysis',
                priority=60,
                examples=['created_date', 'created_at', 'creation_timestamp']
            ),
            ColumnPattern(
                pattern=re.compile(r'.*updated.*date.*|.*modified.*date.*', re.IGNORECASE),
                domain='Record Updates',
                filter_template='Update Date Selection',
                join_template='Update Timeline Enhancement',
                groupby_template='Update Pattern Analysis',
                priority=55,
                examples=['updated_date', 'modified_date', 'last_updated']
            ),
        ])

        # Generic ID patterns (lowest priority)
        self.patterns.extend([
            ColumnPattern(
                pattern=re.compile(r'.*_id$|^id$', re.IGNORECASE),
                domain='Entity Identity',
                filter_template='Entity Selection',
                join_template='Entity Data Enrichment',
                groupby_template='Entity Grouping',
                priority=30,
                examples=['id', 'record_id', 'entity_id']
            ),
        ])

    def match_column(self, column_name: str) -> Optional[PatternMatch]:
        """
        Find the best pattern match for a column name.

        Args:
            column_name: Column name to match

        Returns:
            PatternMatch object or None if no match found
        """
        if not column_name or not isinstance(column_name, str):
            return None

        best_match = None
        best_confidence = 0.0

        for pattern in self.patterns:
            match = pattern.pattern.search(column_name)
            if match:
                # Calculate confidence based on match quality and pattern priority
                confidence = self._calculate_confidence(column_name, pattern, match)

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = PatternMatch(
                        pattern=pattern,
                        column_name=column_name,
                        confidence=confidence,
                        matched_groups=list(match.groups()) if match.groups() else []
                    )

        return best_match

    def match_columns(self, column_names: List[str]) -> Dict[str, PatternMatch]:
        """
        Match multiple column names to patterns.

        Args:
            column_names: List of column names to match

        Returns:
            Dictionary mapping column names to their best matches
        """
        matches = {}
        for column_name in column_names:
            match = self.match_column(column_name)
            if match:
                matches[column_name] = match

        return matches

    def get_primary_domain(self, column_names: List[str]) -> Optional[str]:
        """
        Identify the primary business domain from a list of columns.

        Args:
            column_names: List of column names to analyze

        Returns:
            Primary domain name or None if no clear primary domain
        """
        matches = self.match_columns(column_names)

        if not matches:
            return None

        # Weight domains by confidence and priority
        domain_scores = {}
        for match in matches.values():
            domain = match.pattern.domain
            score = match.confidence * (match.pattern.priority / 100.0)

            if domain in domain_scores:
                domain_scores[domain] += score
            else:
                domain_scores[domain] = score

        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)

        return None

    def _calculate_confidence(self, column_name: str, pattern: ColumnPattern, match: re.Match) -> float:
        """
        Calculate confidence score for a pattern match.

        Args:
            column_name: Original column name
            pattern: Matched pattern
            match: Regex match object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.5

        # Boost confidence for exact matches in examples
        if column_name.lower() in [ex.lower() for ex in pattern.examples]:
            base_confidence = 0.95

        # Boost confidence based on pattern priority
        priority_boost = pattern.priority / 100.0 * 0.3

        # Boost confidence for full word matches vs partial matches
        if match.group(0) == column_name:
            word_match_boost = 0.2
        else:
            word_match_boost = 0.1

        # Penalize very generic patterns on generic column names
        if pattern.priority < 40 and len(column_name) < 5:
            generic_penalty = -0.2
        else:
            generic_penalty = 0.0

        total_confidence = base_confidence + priority_boost + word_match_boost + generic_penalty

        # Clamp to valid range
        return max(0.0, min(1.0, total_confidence))

    def add_custom_pattern(self, pattern: ColumnPattern) -> None:
        """
        Add a custom pattern to the matcher.

        Args:
            pattern: Custom pattern to add
        """
        self.patterns.append(pattern)
        # Sort patterns by priority (highest first)
        self.patterns.sort(key=lambda p: p.priority, reverse=True)

    def get_pattern_suggestions(self, column_name: str, top_n: int = 3) -> List[PatternMatch]:
        """
        Get multiple pattern suggestions for a column name.

        Args:
            column_name: Column name to analyze
            top_n: Number of suggestions to return

        Returns:
            List of pattern matches sorted by confidence
        """
        suggestions = []

        for pattern in self.patterns:
            match = pattern.pattern.search(column_name)
            if match:
                confidence = self._calculate_confidence(column_name, pattern, match)
                suggestions.append(PatternMatch(
                    pattern=pattern,
                    column_name=column_name,
                    confidence=confidence,
                    matched_groups=list(match.groups()) if match.groups() else []
                ))

        # Sort by confidence and return top N
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:top_n]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded patterns."""
        domain_counts = {}
        priority_distribution = {}

        for pattern in self.patterns:
            # Count domains
            domain = pattern.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

            # Count priority levels
            priority_range = f"{pattern.priority//10*10}-{pattern.priority//10*10+9}"
            priority_distribution[priority_range] = priority_distribution.get(priority_range, 0) + 1

        return {
            'total_patterns': len(self.patterns),
            'domains': list(domain_counts.keys()),
            'domain_counts': domain_counts,
            'priority_distribution': priority_distribution,
            'highest_priority': max(p.priority for p in self.patterns) if self.patterns else 0,
            'lowest_priority': min(p.priority for p in self.patterns) if self.patterns else 0,
        }