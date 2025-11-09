"""Governance metadata structures for business concepts."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CustomerImpactLevel(Enum):
    """Level of customer impact."""
    DIRECT = "direct"  # Directly determines customer treatment
    INDIRECT = "indirect"  # Influences but doesn't directly determine
    NONE = "none"  # No customer impact


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ApprovalStatus(Enum):
    """Approval status for operations."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXEMPT = "exempt"


@dataclass
class RiskEntry:
    """A single risk entry."""
    risk_id: str
    severity: str  # critical, high, medium, low
    description: str
    likelihood: Optional[str] = None  # high, medium, low
    category: Optional[str] = None  # fairness, financial, data_security, etc.
    impact: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "severity": self.severity,
            "description": self.description,
            "likelihood": self.likelihood,
            "category": self.category,
            "impact": self.impact,
        }


@dataclass
class RiskMitigation:
    """Mitigation for a risk."""
    risk_id: str
    mitigation: str
    status: str  # implemented, planned, not_implemented
    evidence: Optional[str] = None
    owner: Optional[str] = None
    effectiveness: Optional[str] = None  # high, medium, low, unknown
    review_date: Optional[str] = None  # Date when mitigation should be reviewed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "mitigation": self.mitigation,
            "status": self.status,
            "evidence": self.evidence,
            "owner": self.owner,
            "effectiveness": self.effectiveness,
            "review_date": self.review_date,
        }


@dataclass
class InferredRisk:
    """Risk automatically detected by inference engine."""
    risk_id: str
    severity: str
    category: str
    description: str
    detection_method: str
    confidence: float
    recommended_mitigation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "risk_id": self.risk_id,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "detection_method": self.detection_method,
            "confidence": self.confidence,
            "recommended_mitigation": self.recommended_mitigation,
        }


@dataclass
class GovernanceMetadata:
    """
    Governance and compliance metadata for business concepts.

    This class captures all governance-related information required for
    audit, compliance, and risk management in enterprise data processing.
    """

    # JUSTIFICATION
    business_justification: Optional[str] = None
    """Why is this operation being performed? What business value does it provide?"""

    regulatory_requirement: Optional[str] = None
    """Which regulation or policy requires this operation?"""

    # RISK MANAGEMENT
    known_risks: List[RiskEntry] = field(default_factory=list)
    """List of identified risks with severity, description, likelihood"""

    risk_mitigations: List[RiskMitigation] = field(default_factory=list)
    """Mitigations implemented for each risk"""

    risk_assessment_date: Optional[datetime] = None
    """When was the last risk assessment performed?"""

    risk_owner: Optional[str] = None
    """Who is responsible for managing risks? (team, email, or role)"""

    # CUSTOMER IMPACT
    customer_impact_level: Optional[CustomerImpactLevel] = None
    """Level of customer impact: 'direct', 'indirect', 'none'"""

    impacting_columns: List[str] = field(default_factory=list)
    """Columns that will be used to directly impact customers"""

    impact_description: Optional[str] = None
    """How does this operation impact customers?"""

    # DATA CLASSIFICATION
    processes_pii: bool = False
    """Does this operation process Personally Identifiable Information?"""

    pii_columns: List[str] = field(default_factory=list)
    """Which columns contain PII?"""

    data_classification: Optional[DataClassification] = None
    """Data classification level"""

    sensitive_attributes: List[str] = field(default_factory=list)
    """Protected attributes for bias analysis (age, gender, race, etc.)"""

    # COMPLIANCE & AUDIT
    requires_approval: bool = False
    """Does this operation require approval before production?"""

    approval_status: Optional[ApprovalStatus] = None
    """Current approval status"""

    approved_by: Optional[str] = None
    """Who approved this operation?"""

    approval_date: Optional[datetime] = None
    """When was approval granted?"""

    approval_reference: Optional[str] = None
    """Reference to approval ticket/document"""

    data_retention_days: Optional[int] = None
    """How long should outputs be retained?"""

    # INFERENCE FLAGS (set by AI engines)
    inferred_risks: List[InferredRisk] = field(default_factory=list)
    """Risks automatically detected by inference engine"""

    inferred_customer_impact: Optional[str] = None
    """AI-inferred customer impact level"""

    bias_analysis_results: Optional[Dict[str, Any]] = None
    """Results from bias detection analysis"""

    # METADATA
    governance_version: str = "1.0"
    """Version of governance framework used"""

    last_reviewed_date: Optional[datetime] = None
    """When was governance metadata last reviewed?"""

    next_review_date: Optional[datetime] = None
    """When should governance metadata be reviewed next?"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "business_justification": self.business_justification,
            "regulatory_requirement": self.regulatory_requirement,
            "known_risks": [risk.to_dict() for risk in self.known_risks],
            "risk_mitigations": [mit.to_dict() for mit in self.risk_mitigations],
            "risk_assessment_date": self.risk_assessment_date.isoformat() if self.risk_assessment_date else None,
            "risk_owner": self.risk_owner,
            "customer_impact_level": self.customer_impact_level.value if self.customer_impact_level else None,
            "impacting_columns": self.impacting_columns,
            "impact_description": self.impact_description,
            "processes_pii": self.processes_pii,
            "pii_columns": self.pii_columns,
            "data_classification": self.data_classification.value if self.data_classification else None,
            "sensitive_attributes": self.sensitive_attributes,
            "requires_approval": self.requires_approval,
            "approval_status": self.approval_status.value if self.approval_status else None,
            "approved_by": self.approved_by,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "approval_reference": self.approval_reference,
            "data_retention_days": self.data_retention_days,
            "inferred_risks": [risk.to_dict() for risk in self.inferred_risks],
            "inferred_customer_impact": self.inferred_customer_impact,
            "bias_analysis_results": self.bias_analysis_results,
            "governance_version": self.governance_version,
            "last_reviewed_date": self.last_reviewed_date.isoformat() if self.last_reviewed_date else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GovernanceMetadata':
        """Create from dictionary representation."""
        # Parse risks
        known_risks = []
        for risk_data in data.get("known_risks", []):
            known_risks.append(RiskEntry(**risk_data))

        # Parse mitigations
        risk_mitigations = []
        for mit_data in data.get("risk_mitigations", []):
            risk_mitigations.append(RiskMitigation(**mit_data))

        # Parse inferred risks
        inferred_risks = []
        for inferred_data in data.get("inferred_risks", []):
            inferred_risks.append(InferredRisk(**inferred_data))

        # Parse enums
        customer_impact_level = None
        if data.get("customer_impact_level"):
            customer_impact_level = CustomerImpactLevel(data["customer_impact_level"])

        data_classification = None
        if data.get("data_classification"):
            data_classification = DataClassification(data["data_classification"])

        approval_status = None
        if data.get("approval_status"):
            approval_status = ApprovalStatus(data["approval_status"])

        # Parse dates
        risk_assessment_date = None
        if data.get("risk_assessment_date"):
            risk_assessment_date = datetime.fromisoformat(data["risk_assessment_date"])

        approval_date = None
        if data.get("approval_date"):
            approval_date = datetime.fromisoformat(data["approval_date"])

        last_reviewed_date = None
        if data.get("last_reviewed_date"):
            last_reviewed_date = datetime.fromisoformat(data["last_reviewed_date"])

        next_review_date = None
        if data.get("next_review_date"):
            next_review_date = datetime.fromisoformat(data["next_review_date"])

        return cls(
            business_justification=data.get("business_justification"),
            regulatory_requirement=data.get("regulatory_requirement"),
            known_risks=known_risks,
            risk_mitigations=risk_mitigations,
            risk_assessment_date=risk_assessment_date,
            risk_owner=data.get("risk_owner"),
            customer_impact_level=customer_impact_level,
            impacting_columns=data.get("impacting_columns", []),
            impact_description=data.get("impact_description"),
            processes_pii=data.get("processes_pii", False),
            pii_columns=data.get("pii_columns", []),
            data_classification=data_classification,
            sensitive_attributes=data.get("sensitive_attributes", []),
            requires_approval=data.get("requires_approval", False),
            approval_status=approval_status,
            approved_by=data.get("approved_by"),
            approval_date=approval_date,
            approval_reference=data.get("approval_reference"),
            data_retention_days=data.get("data_retention_days"),
            inferred_risks=inferred_risks,
            inferred_customer_impact=data.get("inferred_customer_impact"),
            bias_analysis_results=data.get("bias_analysis_results"),
            governance_version=data.get("governance_version", "1.0"),
            last_reviewed_date=last_reviewed_date,
            next_review_date=next_review_date,
        )

    def is_complete(self) -> bool:
        """Check if governance metadata is reasonably complete."""
        # Must have business justification
        if not self.business_justification:
            return False

        # If has risks, must have mitigations
        if self.known_risks and not self.risk_mitigations:
            return False

        # If requires approval, must have approval info
        if self.requires_approval:
            if not self.approval_status or self.approval_status == ApprovalStatus.PENDING:
                return False

        # If processes PII, must have classification
        if self.processes_pii and not self.data_classification:
            return False

        return True

    def get_completeness_score(self) -> float:
        """Get a completeness score from 0.0 to 1.0."""
        score = 0.0
        total_checks = 10

        if self.business_justification:
            score += 1
        if self.risk_owner:
            score += 1
        if self.customer_impact_level:
            score += 1
        if self.known_risks or self.inferred_risks:
            score += 1
        if self.risk_mitigations:
            score += 1
        if self.data_classification:
            score += 1
        if self.requires_approval and self.approval_status:
            score += 1
        if self.risk_assessment_date:
            score += 1
        if self.processes_pii and self.pii_columns:
            score += 1
        if self.impacting_columns or self.customer_impact_level == CustomerImpactLevel.NONE:
            score += 1

        return score / total_checks
