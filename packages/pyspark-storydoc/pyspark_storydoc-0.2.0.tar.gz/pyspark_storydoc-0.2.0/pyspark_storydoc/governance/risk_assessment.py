"""Risk assessment engine for automatic risk detection."""

import re
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..core.graph_builder import BusinessConceptNode, OperationNode, OperationType


class RiskCategory(Enum):
    """Risk categories."""
    FAIRNESS = "fairness"
    FINANCIAL = "financial"
    DATA_SECURITY = "data_security"
    DATA_QUALITY = "data_quality"
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"


class RiskSeverity(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DetectedRisk:
    """A risk detected by the assessment engine."""
    risk_id: str
    severity: RiskSeverity
    category: RiskCategory
    description: str
    detection_method: str
    confidence: float
    recommended_mitigation: str
    evidence: Optional[str] = None

    def to_inferred_risk_dict(self) -> dict:
        """Convert to InferredRisk dictionary format."""
        return {
            "risk_id": self.risk_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "description": self.description,
            "detection_method": self.detection_method,
            "confidence": self.confidence,
            "recommended_mitigation": self.recommended_mitigation,
        }


class RiskAssessmentEngine:
    """
    Automatically detect operational and compliance risks in business concepts.

    This engine uses pattern matching and heuristics to identify potential risks
    without requiring external AI APIs.
    """

    # Protected attributes that might indicate discrimination risk
    PROTECTED_ATTRIBUTES = {
        "age", "gender", "sex", "race", "ethnicity", "nationality",
        "religion", "disability", "sexual_orientation", "marital_status",
        "pregnancy", "veteran_status", "colour", "color"
    }

    # Geographic proxies that might correlate with protected classes
    GEO_PROXIES = {
        "postcode", "zip_code", "zip", "address", "neighborhood",
        "neighbourhood", "district", "area_code", "region"
    }

    # PII indicators
    PII_INDICATORS = {
        "ssn", "social_security", "national_insurance", "ni_number",
        "passport", "driver_license", "driving_licence", "credit_card",
        "bank_account", "sort_code", "routing_number", "email",
        "phone", "telephone", "mobile", "address", "date_of_birth",
        "dob", "birthdate", "tax_id", "taxpayer_id"
    }

    # Financial calculation indicators
    FINANCIAL_INDICATORS = {
        "price", "premium", "cost", "fee", "charge", "payment",
        "amount", "total", "subtotal", "tax", "discount", "refund",
        "balance", "credit", "debit", "interest", "rate", "apr"
    }

    def __init__(self):
        """Initialize the risk assessment engine."""
        self.risk_counter = 0

    def analyze_concept(self, concept_node: BusinessConceptNode) -> List[DetectedRisk]:
        """
        Analyze a business concept for potential risks.

        Args:
            concept_node: The business concept node to analyze

        Returns:
            List of detected risks
        """
        risks = []

        # Check for filtering on sensitive attributes
        sensitive_filter_risk = self._check_sensitive_filtering(concept_node)
        if sensitive_filter_risk:
            risks.append(sensitive_filter_risk)

        # Check for financial calculations
        financial_risk = self._check_financial_operations(concept_node)
        if financial_risk:
            risks.append(financial_risk)

        # Check for PII processing
        pii_risk = self._check_pii_processing(concept_node)
        if pii_risk:
            risks.append(pii_risk)

        # Check for high data reduction
        data_reduction_risk = self._check_data_reduction(concept_node)
        if data_reduction_risk:
            risks.append(data_reduction_risk)

        # Check for join operations (data quality risk)
        join_risk = self._check_join_operations(concept_node)
        if join_risk:
            risks.append(join_risk)

        # Check for aggregation without proper grouping
        aggregation_risk = self._check_aggregation_operations(concept_node)
        if aggregation_risk:
            risks.append(aggregation_risk)

        return risks

    def _generate_risk_id(self) -> str:
        """Generate a unique risk ID."""
        self.risk_counter += 1
        return f"R{self.risk_counter:03d}"

    def _check_sensitive_filtering(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check if operation filters on sensitive attributes."""
        # Check operation name
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        # Check if name/description mentions protected attributes
        mentioned_attributes = []
        for attr in self.PROTECTED_ATTRIBUTES:
            if attr in name_lower or attr in description_lower:
                mentioned_attributes.append(attr)

        # Check if name/description mentions geographic proxies
        mentioned_proxies = []
        for proxy in self.GEO_PROXIES:
            if proxy in name_lower or proxy in description_lower:
                mentioned_proxies.append(proxy)

        # Check tracked columns
        tracked_sensitive = []
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for attr in self.PROTECTED_ATTRIBUTES:
                if attr in col_lower:
                    tracked_sensitive.append(col)
                    break

        # Check for filter operations in technical operations
        has_filter_op = any(
            op.operation_type == OperationType.FILTER
            for op in concept_node.technical_operations
        )

        # Determine if this is a risk
        if (mentioned_attributes or mentioned_proxies or tracked_sensitive) and has_filter_op:
            attributes_str = ", ".join(mentioned_attributes + mentioned_proxies + tracked_sensitive)
            return DetectedRisk(
                risk_id=self._generate_risk_id(),
                severity=RiskSeverity.HIGH,
                category=RiskCategory.FAIRNESS,
                description=f"Operation filters on potential protected/sensitive attributes: {attributes_str}. This may lead to discriminatory outcomes.",
                detection_method="pattern_analysis",
                confidence=0.75,
                recommended_mitigation="Document business justification, perform disparate impact analysis, conduct regular bias audits",
                evidence=f"Protected attributes detected: {attributes_str}"
            )

        return None

    def _check_financial_operations(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check if operation involves financial calculations."""
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        # Check for financial keywords
        financial_keywords_found = []
        for keyword in self.FINANCIAL_INDICATORS:
            if keyword in name_lower or keyword in description_lower:
                financial_keywords_found.append(keyword)

        # Check tracked columns for financial indicators
        financial_columns = []
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for keyword in self.FINANCIAL_INDICATORS:
                if keyword in col_lower:
                    financial_columns.append(col)
                    break

        # Check for calculation operations
        has_calculation = any(
            op.operation_type in [OperationType.WITH_COLUMN, OperationType.TRANSFORM, OperationType.SELECT]
            for op in concept_node.technical_operations
        )

        if (financial_keywords_found or financial_columns) and has_calculation:
            return DetectedRisk(
                risk_id=self._generate_risk_id(),
                severity=RiskSeverity.HIGH,
                category=RiskCategory.FINANCIAL,
                description="Financial calculation detected. Errors could have direct monetary impact on customers or business.",
                detection_method="keyword_analysis",
                confidence=0.85,
                recommended_mitigation="Implement comprehensive unit tests, validation rules, human review for outliers, and audit trails",
                evidence=f"Financial indicators: {', '.join(financial_keywords_found + financial_columns)}"
            )

        return None

    def _check_pii_processing(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check if operation processes PII without proper safeguards."""
        # Check if governance metadata already declares PII processing
        if hasattr(concept_node, 'governance_metadata') and concept_node.governance_metadata:
            if concept_node.governance_metadata.processes_pii:
                # Already documented, check for proper classification
                if not concept_node.governance_metadata.data_classification:
                    return DetectedRisk(
                        risk_id=self._generate_risk_id(),
                        severity=RiskSeverity.CRITICAL,
                        category=RiskCategory.DATA_SECURITY,
                        description="PII processing declared but data classification not specified",
                        detection_method="metadata_analysis",
                        confidence=1.0,
                        recommended_mitigation="Specify data classification level (confidential/restricted) and implement appropriate access controls",
                    )
                return None  # PII properly documented

        # Check for PII indicators in names and columns
        name_lower = concept_node.name.lower()
        description_lower = (concept_node.description or "").lower()

        pii_indicators_found = []
        for indicator in self.PII_INDICATORS:
            if indicator in name_lower or indicator in description_lower:
                pii_indicators_found.append(indicator)

        # Check tracked columns
        pii_columns = []
        for col in concept_node.track_columns:
            col_lower = col.lower()
            for indicator in self.PII_INDICATORS:
                if indicator in col_lower:
                    pii_columns.append(col)
                    break

        if pii_indicators_found or pii_columns:
            return DetectedRisk(
                risk_id=self._generate_risk_id(),
                severity=RiskSeverity.CRITICAL,
                category=RiskCategory.DATA_SECURITY,
                description=f"Potential PII processing detected: {', '.join(pii_indicators_found + pii_columns)}. PII must be properly classified and protected.",
                detection_method="pii_pattern_matching",
                confidence=0.70,
                recommended_mitigation="Declare PII processing in governance metadata, specify data classification, implement encryption and access controls",
                evidence=f"PII indicators: {', '.join(pii_indicators_found + pii_columns)}"
            )

        return None

    def _check_data_reduction(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check for high data reduction that might indicate data loss."""
        if not (concept_node.input_metrics and concept_node.output_metrics):
            return None

        input_count = concept_node.input_metrics.row_count
        output_count = concept_node.output_metrics.row_count

        if input_count == 0:
            return None

        reduction_percentage = ((input_count - output_count) / input_count) * 100

        # Flag if reduction is > 50%
        if reduction_percentage > 50:
            return DetectedRisk(
                risk_id=self._generate_risk_id(),
                severity=RiskSeverity.MEDIUM,
                category=RiskCategory.DATA_QUALITY,
                description=f"High data reduction detected: {reduction_percentage:.1f}% of records removed ({input_count:,} -> {output_count:,}). Verify filters are correct.",
                detection_method="metrics_analysis",
                confidence=0.80,
                recommended_mitigation="Review filter logic, implement data quality checks, add monitoring for unexpected data loss",
                evidence=f"Input: {input_count:,} rows, Output: {output_count:,} rows, Reduction: {reduction_percentage:.1f}%"
            )

        return None

    def _check_join_operations(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check for join operations that might cause data quality issues."""
        join_ops = [
            op for op in concept_node.technical_operations
            if op.operation_type == OperationType.JOIN
        ]

        if not join_ops:
            return None

        # Check if metrics show unexpected row count changes
        if concept_node.input_metrics and concept_node.output_metrics:
            input_count = concept_node.input_metrics.row_count
            output_count = concept_node.output_metrics.row_count

            # If output significantly differs from input, flag it
            if output_count > input_count * 1.5:  # 50% increase
                return DetectedRisk(
                    risk_id=self._generate_risk_id(),
                    severity=RiskSeverity.MEDIUM,
                    category=RiskCategory.DATA_QUALITY,
                    description=f"Join operation caused unexpected data multiplication: {input_count:,} -> {output_count:,} rows. Check for duplicate keys or incorrect join conditions.",
                    detection_method="metrics_analysis",
                    confidence=0.85,
                    recommended_mitigation="Verify join keys are unique, check for many-to-many relationships, add data quality validation",
                    evidence=f"Input: {input_count:,} rows, Output: {output_count:,} rows"
                )
            elif output_count < input_count * 0.5:  # 50% reduction
                return DetectedRisk(
                    risk_id=self._generate_risk_id(),
                    severity=RiskSeverity.MEDIUM,
                    category=RiskCategory.DATA_QUALITY,
                    description=f"Join operation caused significant data loss: {input_count:,} -> {output_count:,} rows. Verify join type (inner/left/right) is correct.",
                    detection_method="metrics_analysis",
                    confidence=0.85,
                    recommended_mitigation="Review join type and join keys, check for missing data in join columns, add monitoring",
                    evidence=f"Input: {input_count:,} rows, Output: {output_count:,} rows"
                )

        return None

    def _check_aggregation_operations(self, concept_node: BusinessConceptNode) -> Optional[DetectedRisk]:
        """Check for aggregation operations that might lose important details."""
        agg_ops = [
            op for op in concept_node.technical_operations
            if op.operation_type in [OperationType.GROUP_BY, OperationType.AGGREGATE]
        ]

        if not agg_ops:
            return None

        # Check if there's significant data reduction (which is expected for aggregation)
        if concept_node.input_metrics and concept_node.output_metrics:
            input_count = concept_node.input_metrics.row_count
            output_count = concept_node.output_metrics.row_count

            reduction_percentage = ((input_count - output_count) / input_count) * 100

            # Aggregation should reduce data significantly; if not, might be wrong
            if reduction_percentage < 10 and input_count > 100:
                return DetectedRisk(
                    risk_id=self._generate_risk_id(),
                    severity=RiskSeverity.LOW,
                    category=RiskCategory.DATA_QUALITY,
                    description=f"Aggregation operation with minimal data reduction ({reduction_percentage:.1f}%). Verify grouping columns are correct.",
                    detection_method="metrics_analysis",
                    confidence=0.60,
                    recommended_mitigation="Review GROUP BY columns, verify aggregation logic is as intended",
                    evidence=f"Input: {input_count:,} rows, Output: {output_count:,} rows, Reduction: {reduction_percentage:.1f}%"
                )

        return None

    def assess_pipeline_risks(self, concept_nodes: List[BusinessConceptNode]) -> Dict[str, List[DetectedRisk]]:
        """
        Assess risks across an entire pipeline.

        Args:
            concept_nodes: List of business concept nodes in the pipeline

        Returns:
            Dictionary mapping concept IDs to detected risks
        """
        pipeline_risks = {}

        for concept in concept_nodes:
            risks = self.analyze_concept(concept)
            if risks:
                pipeline_risks[concept.node_id] = risks

        return pipeline_risks

    def generate_risk_summary(self, risks: List[DetectedRisk]) -> Dict[str, any]:
        """
        Generate a summary of detected risks.

        Args:
            risks: List of detected risks

        Returns:
            Summary dictionary with counts and severity breakdown
        """
        summary = {
            "total_risks": len(risks),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            "by_category": {},
            "highest_severity": None,
            "average_confidence": 0.0,
        }

        if not risks:
            return summary

        # Count by severity
        for risk in risks:
            summary["by_severity"][risk.severity.value] += 1

        # Count by category
        for risk in risks:
            category = risk.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

        # Determine highest severity
        if summary["by_severity"]["critical"] > 0:
            summary["highest_severity"] = "critical"
        elif summary["by_severity"]["high"] > 0:
            summary["highest_severity"] = "high"
        elif summary["by_severity"]["medium"] > 0:
            summary["highest_severity"] = "medium"
        else:
            summary["highest_severity"] = "low"

        # Calculate average confidence
        summary["average_confidence"] = sum(risk.confidence for risk in risks) / len(risks)

        return summary
