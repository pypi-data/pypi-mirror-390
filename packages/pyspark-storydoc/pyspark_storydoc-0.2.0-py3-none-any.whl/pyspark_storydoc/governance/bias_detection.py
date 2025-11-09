"""Bias detection engine for identifying potential fairness concerns."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..core.graph_builder import BusinessConceptNode, OperationType


class BiasCategory(Enum):
    """Categories of bias concerns."""
    DIRECT_DISCRIMINATION = "direct_discrimination"
    PROXY_DISCRIMINATION = "proxy_discrimination"
    DISPARATE_IMPACT = "disparate_impact"
    MISSING_DATA_BIAS = "missing_data_bias"
    REPRESENTATION_BIAS = "representation_bias"


@dataclass
class BiasIssue:
    """A potential bias issue detected in an operation."""
    severity: str  # critical, high, medium, low
    category: BiasCategory
    description: str
    affected_attributes: List[str]
    recommendation: str
    requires_legal_review: bool = False
    requires_fairness_testing: bool = False
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "category": self.category.value,
            "description": self.description,
            "affected_attributes": self.affected_attributes,
            "recommendation": self.recommendation,
            "requires_legal_review": self.requires_legal_review,
            "requires_fairness_testing": self.requires_fairness_testing,
            "confidence": self.confidence,
        }


@dataclass
class BiasAnalysisResult:
    """Complete bias analysis results for an operation."""
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # critical, high, medium, low, none
    issues: List[BiasIssue] = field(default_factory=list)
    recommended_fairness_metrics: List[str] = field(default_factory=list)
    requires_human_review: bool = False
    requires_legal_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "issues": [issue.to_dict() for issue in self.issues],
            "recommended_fairness_metrics": self.recommended_fairness_metrics,
            "requires_human_review": self.requires_human_review,
            "requires_legal_review": self.requires_legal_review,
        }


class BiasDetectionEngine:
    """
    Detect potential bias in data operations.

    This engine analyzes business concepts for potential discriminatory
    practices using pattern matching and heuristics.
    """

    # Protected attributes (vary by jurisdiction)
    PROTECTED_ATTRIBUTES = {
        "age", "gender", "sex", "race", "ethnicity", "nationality",
        "religion", "disability", "disabled", "sexual_orientation",
        "marital_status", "pregnancy", "pregnant", "veteran_status",
        "veteran", "colour", "color", "caste", "tribal_status"
    }

    # Geographic proxies that may correlate with protected classes
    GEO_PROXIES = {
        "postcode", "zip_code", "zip", "postal_code", "address",
        "neighborhood", "neighbourhood", "district", "area_code",
        "region", "county", "borough", "ward", "census_tract"
    }

    # Names that might indicate ethnicity/origin
    NAME_PROXIES = {
        "first_name", "last_name", "surname", "family_name",
        "given_name", "middle_name", "full_name", "maiden_name"
    }

    # Decision-making indicators
    DECISION_INDICATORS = {
        "approval", "approved", "decline", "declined", "reject",
        "rejected", "decision", "eligibility", "eligible", "qualified",
        "acceptance", "accepted", "status", "outcome"
    }

    def __init__(self):
        """Initialize the bias detection engine."""
        pass

    def analyze_for_bias(
        self,
        concept_node: BusinessConceptNode
    ) -> BiasAnalysisResult:
        """
        Analyze a business concept for potential bias.

        Args:
            concept_node: The business concept to analyze

        Returns:
            Complete bias analysis results
        """
        issues = []

        # 1. Check for direct filtering on protected attributes
        direct_discrimination = self._check_direct_discrimination(concept_node)
        if direct_discrimination:
            issues.append(direct_discrimination)

        # 2. Check for proxy discrimination
        proxy_discrimination = self._check_proxy_discrimination(concept_node)
        if proxy_discrimination:
            issues.append(proxy_discrimination)

        # 3. Check for decision-making operations requiring fairness testing
        disparate_impact = self._check_disparate_impact_risk(concept_node)
        if disparate_impact:
            issues.append(disparate_impact)

        # 4. Check governance metadata for declared sensitive attributes
        metadata_bias = self._check_declared_sensitive_attributes(concept_node)
        if metadata_bias:
            issues.append(metadata_bias)

        # Calculate overall bias risk score
        bias_risk_score = self._calculate_bias_risk_score(issues)

        # Classify risk level
        risk_level = self._classify_risk_level(bias_risk_score)

        # Recommend fairness metrics
        fairness_metrics = self._recommend_fairness_metrics(issues)

        # Determine if reviews are required
        requires_legal = any(issue.requires_legal_review for issue in issues)
        requires_human = bias_risk_score > 0.6 or requires_legal

        return BiasAnalysisResult(
            risk_score=bias_risk_score,
            risk_level=risk_level,
            issues=issues,
            recommended_fairness_metrics=fairness_metrics,
            requires_human_review=requires_human,
            requires_legal_review=requires_legal
        )

    def _check_direct_discrimination(self, concept_node: BusinessConceptNode) -> Optional[BiasIssue]:
        """Check for direct filtering on protected attributes."""
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        # Check for protected attributes in names/descriptions
        protected_found = []
        for attr in self.PROTECTED_ATTRIBUTES:
            if attr in name_lower or attr in description_lower:
                protected_found.append(attr)

        # Check tracked columns
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for attr in self.PROTECTED_ATTRIBUTES:
                if attr in col_lower:
                    if col not in protected_found:
                        protected_found.append(col)

        # Check if this is a filtering operation
        has_filter = any(
            op.operation_type == OperationType.FILTER
            for op in concept_node.technical_operations
        )

        if protected_found and has_filter:
            return BiasIssue(
                severity="critical",
                category=BiasCategory.DIRECT_DISCRIMINATION,
                description=f"Operation filters directly on protected attribute(s): {', '.join(protected_found)}. This may constitute direct discrimination.",
                affected_attributes=protected_found,
                recommendation="Provide legal justification for filtering on protected attributes or remove the filter. Consult legal/compliance team.",
                requires_legal_review=True,
                requires_fairness_testing=True,
                confidence=0.85
            )

        return None

    def _check_proxy_discrimination(self, concept_node: BusinessConceptNode) -> Optional[BiasIssue]:
        """Check for use of proxy features that correlate with protected attributes."""
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        # Check for geographic proxies
        geo_proxies_found = []
        for proxy in self.GEO_PROXIES:
            if proxy in name_lower or proxy in description_lower:
                geo_proxies_found.append(proxy)

        # Check tracked columns for geo proxies
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for proxy in self.GEO_PROXIES:
                if proxy in col_lower:
                    if col not in geo_proxies_found:
                        geo_proxies_found.append(col)

        # Check for name proxies
        name_proxies_found = []
        for proxy in self.NAME_PROXIES:
            if proxy in name_lower or proxy in description_lower:
                name_proxies_found.append(proxy)

        for col in concept_node.track_columns:
            col_lower = col.lower()
            for proxy in self.NAME_PROXIES:
                if proxy in col_lower:
                    if col not in name_proxies_found:
                        name_proxies_found.append(col)

        all_proxies = geo_proxies_found + name_proxies_found

        if all_proxies:
            # Check if this is used in decision-making
            is_decision_making = self._is_decision_making_operation(concept_node)

            if is_decision_making:
                return BiasIssue(
                    severity="high",
                    category=BiasCategory.PROXY_DISCRIMINATION,
                    description=f"Operation uses proxy features that may correlate with protected attributes: {', '.join(all_proxies)}. This could lead to indirect discrimination.",
                    affected_attributes=all_proxies,
                    recommendation="Perform disparate impact analysis to verify these features don't produce discriminatory outcomes. Consider feature engineering or removing highly correlated proxies.",
                    requires_legal_review=True,
                    requires_fairness_testing=True,
                    confidence=0.70
                )

        return None

    def _check_disparate_impact_risk(self, concept_node: BusinessConceptNode) -> Optional[BiasIssue]:
        """Check if operation is decision-making and requires fairness testing."""
        is_decision = self._is_decision_making_operation(concept_node)

        if is_decision:
            # Infer which protected attributes might be relevant
            relevant_attributes = self._infer_relevant_protected_attributes(concept_node)

            return BiasIssue(
                severity="high",
                category=BiasCategory.DISPARATE_IMPACT,
                description="Decision-making operation detected. Requires fairness testing to ensure no disparate impact on protected groups.",
                affected_attributes=relevant_attributes,
                recommendation=(
                    "Implement disparate impact analysis using the 80% rule (4/5ths rule). "
                    "Test outcomes across protected groups. Conduct regular bias audits."
                ),
                requires_fairness_testing=True,
                confidence=0.80
            )

        return None

    def _check_declared_sensitive_attributes(self, concept_node: BusinessConceptNode) -> Optional[BiasIssue]:
        """Check if governance metadata declares sensitive attributes."""
        if not hasattr(concept_node, 'governance_metadata') or not concept_node.governance_metadata:
            return None

        sensitive_attrs = concept_node.governance_metadata.sensitive_attributes
        if not sensitive_attrs:
            return None

        # If sensitive attributes are declared, recommend fairness testing
        return BiasIssue(
            severity="medium",
            category=BiasCategory.DISPARATE_IMPACT,
            description=f"Operation declared as processing sensitive attributes: {', '.join(sensitive_attrs)}. Fairness analysis required.",
            affected_attributes=sensitive_attrs,
            recommendation=(
                "Perform fairness testing across all declared sensitive attributes. "
                "Implement monitoring for discriminatory outcomes. Document justification for using these attributes."
            ),
            requires_fairness_testing=True,
            confidence=1.0  # High confidence since explicitly declared
        )

    def _is_decision_making_operation(self, concept_node: BusinessConceptNode) -> bool:
        """Check if operation appears to be decision-making."""
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        # Check for decision indicators
        for indicator in self.DECISION_INDICATORS:
            if indicator in name_lower or indicator in description_lower:
                return True

        # Check tracked columns for decision indicators
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for indicator in self.DECISION_INDICATORS:
                if indicator in col_lower:
                    return True

        # Check if governance metadata indicates customer impact
        if hasattr(concept_node, 'governance_metadata') and concept_node.governance_metadata:
            if concept_node.governance_metadata.customer_impact_level:
                level = concept_node.governance_metadata.customer_impact_level.value
                if level == "direct":
                    return True

        return False

    def _infer_relevant_protected_attributes(self, concept_node: BusinessConceptNode) -> List[str]:
        """Infer which protected attributes might be relevant for this operation."""
        # Check governance metadata first
        if hasattr(concept_node, 'governance_metadata') and concept_node.governance_metadata:
            if concept_node.governance_metadata.sensitive_attributes:
                return concept_node.governance_metadata.sensitive_attributes

        # Otherwise, return common attributes for decision-making
        return ["age", "gender", "race", "ethnicity", "postcode"]

    def _calculate_bias_risk_score(self, issues: List[BiasIssue]) -> float:
        """Calculate overall bias risk score (0.0 to 1.0)."""
        if not issues:
            return 0.0

        # Weight by severity
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }

        total_score = 0.0
        for issue in issues:
            weight = severity_weights.get(issue.severity, 0.5)
            total_score += weight * issue.confidence

        # Normalize by number of issues (max 1.0)
        return min(total_score / len(issues), 1.0)

    def _classify_risk_level(self, risk_score: float) -> str:
        """Classify risk level based on score."""
        if risk_score >= 0.8:
            return "critical"
        elif risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        elif risk_score > 0.0:
            return "low"
        else:
            return "none"

    def _recommend_fairness_metrics(self, issues: List[BiasIssue]) -> List[str]:
        """Recommend fairness metrics based on detected issues."""
        if not issues:
            return []

        # Standard fairness metrics for any bias concern
        metrics = [
            "demographic_parity",  # Equal selection rates across groups
            "equal_opportunity",  # Equal true positive rates
            "equalized_odds",  # Equal TPR and FPR across groups
            "disparate_impact_ratio",  # 80% rule compliance
        ]

        # Add specialized metrics based on issue categories
        for issue in issues:
            if issue.category == BiasCategory.DIRECT_DISCRIMINATION:
                if "predictive_parity" not in metrics:
                    metrics.append("predictive_parity")  # Equal precision across groups

            if issue.category == BiasCategory.PROXY_DISCRIMINATION:
                if "calibration" not in metrics:
                    metrics.append("calibration")  # Accurate probability estimates

        return metrics

    def generate_fairness_testing_checklist(self, analysis: BiasAnalysisResult) -> List[str]:
        """Generate a fairness testing checklist based on analysis."""
        checklist = []

        if analysis.risk_level in ["critical", "high"]:
            checklist.append("[RED] CRITICAL: Conduct comprehensive fairness audit before production")
            checklist.append("Perform disparate impact analysis (80% rule) across all protected groups")
            checklist.append("Document statistical evidence of fairness")

        if analysis.requires_legal_review:
            checklist.append("Obtain legal review and approval for use of sensitive attributes")
            checklist.append("Document business necessity and less discriminatory alternatives")

        for issue in analysis.issues:
            if issue.category == BiasCategory.DIRECT_DISCRIMINATION:
                checklist.append(f"Justify filtering on {', '.join(issue.affected_attributes)} with legal/business rationale")

            if issue.category == BiasCategory.PROXY_DISCRIMINATION:
                checklist.append(f"Test correlation between {', '.join(issue.affected_attributes)} and protected attributes")

        # Add metrics testing
        if analysis.recommended_fairness_metrics:
            checklist.append(f"Calculate fairness metrics: {', '.join(analysis.recommended_fairness_metrics)}")

        # General recommendations
        checklist.append("Implement monitoring for ongoing fairness (not just one-time testing)")
        checklist.append("Establish bias audit schedule (recommended: quarterly)")
        checklist.append("Create appeals process for adverse decisions")

        return checklist
