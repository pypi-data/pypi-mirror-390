"""Enhanced governance metadata structures for audit readiness."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ControlStatus(Enum):
    """Status of a control."""
    IMPLEMENTED = "implemented"
    PLANNED = "planned"
    NOT_IMPLEMENTED = "not_implemented"


class ControlEffectiveness(Enum):
    """Effectiveness of a control."""
    EFFECTIVE = "effective"
    PARTIALLY_EFFECTIVE = "partially_effective"
    NOT_EFFECTIVE = "not_effective"
    NOT_TESTED = "not_tested"


class RegulatoryFramework(Enum):
    """Common regulatory frameworks."""
    GDPR = "GDPR"
    CCPA = "CCPA"
    FCRA = "FCRA"
    ECOA = "ECOA"
    SOC2 = "SOC2"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    ISO_27001 = "ISO_27001"
    CUSTOM = "CUSTOM"


@dataclass
class ControlEntry:
    """
    A single control for risk mitigation.

    Controls are specific measures implemented to mitigate risks.
    """
    control_id: str
    """Unique identifier for the control (e.g., CTRL-001)"""

    description: str
    """What this control does"""

    risk_id: str
    """Which risk this control mitigates"""

    status: ControlStatus = ControlStatus.IMPLEMENTED
    """Implementation status"""

    effectiveness: ControlEffectiveness = ControlEffectiveness.NOT_TESTED
    """How effective is this control"""

    owner: Optional[str] = None
    """Who is responsible for this control"""

    last_test_date: Optional[datetime] = None
    """When was this control last tested"""

    next_test_date: Optional[datetime] = None
    """When should this control be tested next"""

    test_result: Optional[str] = None
    """Result of last control test"""

    evidence_location: Optional[str] = None
    """Where evidence of control effectiveness is stored"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "control_id": self.control_id,
            "description": self.description,
            "risk_id": self.risk_id,
            "status": self.status.value,
            "effectiveness": self.effectiveness.value,
            "owner": self.owner,
            "last_test_date": self.last_test_date.isoformat() if self.last_test_date else None,
            "next_test_date": self.next_test_date.isoformat() if self.next_test_date else None,
            "test_result": self.test_result,
            "evidence_location": self.evidence_location,
        }


@dataclass
class ApprovalEntry:
    """
    A single approval in the approval trail.

    Captures who approved what and when for audit trail.
    """
    approval_type: str
    """Type of approval (business, technical, compliance, legal)"""

    approved_by: str
    """Who approved (name or email)"""

    approval_date: datetime
    """When approval was granted"""

    approval_id: Optional[str] = None
    """Reference ID for approval (ticket number, email ID, etc.)"""

    comments: Optional[str] = None
    """Any comments or conditions on approval"""

    evidence_location: Optional[str] = None
    """Where approval evidence is stored"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "approval_type": self.approval_type,
            "approved_by": self.approved_by,
            "approval_date": self.approval_date.isoformat(),
            "approval_id": self.approval_id,
            "comments": self.comments,
            "evidence_location": self.evidence_location,
        }


@dataclass
class RegulatoryRequirement:
    """
    A specific regulatory requirement that applies to this operation.

    Maps operation to specific articles/sections of regulations.
    """
    framework: RegulatoryFramework
    """Which regulatory framework (GDPR, CCPA, etc.)"""

    requirement_id: str
    """Specific requirement (e.g., "Article 5", "15 U.S.C. § 1681b")"""

    requirement_description: str
    """What the requirement says"""

    compliance_status: str
    """compliant, non_compliant, in_progress, not_applicable"""

    evidence_location: Optional[str] = None
    """Where compliance evidence is stored"""

    last_review_date: Optional[datetime] = None
    """When compliance was last reviewed"""

    next_review_date: Optional[datetime] = None
    """When compliance should be reviewed next"""

    notes: Optional[str] = None
    """Additional notes on compliance"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "framework": self.framework.value,
            "requirement_id": self.requirement_id,
            "requirement_description": self.requirement_description,
            "compliance_status": self.compliance_status,
            "evidence_location": self.evidence_location,
            "last_review_date": self.last_review_date.isoformat() if self.last_review_date else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
            "notes": self.notes,
        }


@dataclass
class StakeholderEntry:
    """
    A stakeholder involved in this operation.

    Captures who is responsible for different aspects.
    """
    role: str
    """Role (business_owner, technical_owner, data_steward, compliance_owner, etc.)"""

    name_or_email: str
    """Name or email of stakeholder"""

    responsibilities: Optional[str] = None
    """What they're responsible for"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "name_or_email": self.name_or_email,
            "responsibilities": self.responsibilities,
        }


@dataclass
class ChangeLogEntry:
    """
    A change to this operation.

    Captures what changed, why, and when for audit trail.
    """
    change_date: datetime
    """When the change was made"""

    changed_by: str
    """Who made the change"""

    change_description: str
    """What was changed"""

    change_reason: str
    """Why the change was made"""

    version_from: Optional[str] = None
    """Previous version"""

    version_to: Optional[str] = None
    """New version"""

    approval_required: bool = False
    """Did this change require approval"""

    approval_id: Optional[str] = None
    """Reference to approval"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "change_date": self.change_date.isoformat(),
            "changed_by": self.changed_by,
            "change_description": self.change_description,
            "change_reason": self.change_reason,
            "version_from": self.version_from,
            "version_to": self.version_to,
            "approval_required": self.approval_required,
            "approval_id": self.approval_id,
        }


@dataclass
class EnhancedGovernanceMetadata:
    """
    Enhanced governance metadata for comprehensive audit readiness.

    This extends the basic governance metadata with audit trail,
    control tracking, and regulatory compliance mapping.
    """

    # BASIC JUSTIFICATION (required)
    business_justification: str
    """Why this operation exists - what business value it provides"""

    operation_name: str
    """Name of the operation"""

    operation_id: Optional[str] = None
    """Unique identifier for this operation"""

    # STAKEHOLDERS
    stakeholders: List[StakeholderEntry] = field(default_factory=list)
    """Who is responsible for different aspects"""

    # RISK MANAGEMENT (enhanced)
    known_risks: List[Dict[str, Any]] = field(default_factory=list)
    """List of identified risks"""

    controls: List[ControlEntry] = field(default_factory=list)
    """Controls implemented to mitigate risks"""

    residual_risk_level: Optional[str] = None
    """Overall residual risk after controls (low, medium, high, critical)"""

    residual_risk_accepted_by: Optional[str] = None
    """Who accepted the residual risk"""

    residual_risk_acceptance_date: Optional[datetime] = None
    """When residual risk was accepted"""

    # APPROVAL TRAIL
    approvals: List[ApprovalEntry] = field(default_factory=list)
    """Complete approval trail"""

    # REGULATORY COMPLIANCE
    regulatory_requirements: List[RegulatoryRequirement] = field(default_factory=list)
    """Specific regulatory requirements that apply"""

    # CHANGE HISTORY
    change_history: List[ChangeLogEntry] = field(default_factory=list)
    """History of changes to this operation"""

    current_version: Optional[str] = None
    """Current version of the operation"""

    # PII AND DATA CLASSIFICATION
    processes_pii: bool = False
    """Does this process PII"""

    pii_columns: List[str] = field(default_factory=list)
    """Which columns contain PII"""

    data_classification: Optional[str] = None
    """public, internal, confidential, restricted"""

    # ACCESS CONTROL (documentation only)
    required_access_roles: List[str] = field(default_factory=list)
    """Which roles need access to this operation's data"""

    access_approval_required: bool = False
    """Does access require approval"""

    access_approval_id: Optional[str] = None
    """Reference to access approval"""

    # EVIDENCE PACKAGE
    evidence_base_path: Optional[str] = None
    """Base path where all evidence is stored"""

    evidence_files: List[str] = field(default_factory=list)
    """List of evidence files"""

    # METADATA
    created_date: Optional[datetime] = None
    """When this operation was created"""

    last_modified_date: Optional[datetime] = None
    """When governance metadata was last modified"""

    last_review_date: Optional[datetime] = None
    """When governance was last reviewed"""

    next_review_date: Optional[datetime] = None
    """When governance should be reviewed next"""

    audit_ready: bool = False
    """Is this operation audit-ready"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "business_justification": self.business_justification,
            "operation_name": self.operation_name,
            "operation_id": self.operation_id,
            "stakeholders": [s.to_dict() for s in self.stakeholders],
            "known_risks": self.known_risks,
            "controls": [c.to_dict() for c in self.controls],
            "residual_risk_level": self.residual_risk_level,
            "residual_risk_accepted_by": self.residual_risk_accepted_by,
            "residual_risk_acceptance_date": self.residual_risk_acceptance_date.isoformat() if self.residual_risk_acceptance_date else None,
            "approvals": [a.to_dict() for a in self.approvals],
            "regulatory_requirements": [r.to_dict() for r in self.regulatory_requirements],
            "change_history": [c.to_dict() for c in self.change_history],
            "current_version": self.current_version,
            "processes_pii": self.processes_pii,
            "pii_columns": self.pii_columns,
            "data_classification": self.data_classification,
            "required_access_roles": self.required_access_roles,
            "access_approval_required": self.access_approval_required,
            "access_approval_id": self.access_approval_id,
            "evidence_base_path": self.evidence_base_path,
            "evidence_files": self.evidence_files,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "last_modified_date": self.last_modified_date.isoformat() if self.last_modified_date else None,
            "last_review_date": self.last_review_date.isoformat() if self.last_review_date else None,
            "next_review_date": self.next_review_date.isoformat() if self.next_review_date else None,
            "audit_ready": self.audit_ready,
        }

    def get_audit_readiness_score(self) -> float:
        """
        Calculate audit readiness score (0.0 to 1.0).

        Checks for completeness of governance documentation.
        """
        score = 0.0
        checks = 0

        # Required: Business justification
        checks += 1
        if self.business_justification:
            score += 1

        # Required: Stakeholders identified
        checks += 1
        if self.stakeholders:
            score += 1

        # Required: Risks documented
        checks += 1
        if self.known_risks:
            score += 1

        # Required: Controls for risks
        checks += 1
        if self.known_risks and self.controls:
            score += 1
        elif not self.known_risks:  # No risks = no controls needed
            score += 1

        # Required: Approvals documented
        checks += 1
        if self.approvals:
            score += 1

        # Required: Regulatory requirements mapped
        checks += 1
        if self.regulatory_requirements:
            score += 1

        # Required: PII classification if processes PII
        checks += 1
        if self.processes_pii:
            if self.pii_columns and self.data_classification:
                score += 1
        else:
            score += 1

        # Optional but helpful: Evidence locations
        checks += 1
        if self.evidence_base_path or self.evidence_files:
            score += 1

        # Optional but helpful: Change history
        checks += 1
        if self.change_history:
            score += 1

        # Optional but helpful: Control testing
        checks += 1
        if self.controls:
            tested_controls = [c for c in self.controls if c.effectiveness != ControlEffectiveness.NOT_TESTED]
            if tested_controls:
                score += 1
        else:
            score += 0.5  # Partial credit if no controls needed

        return score / checks if checks > 0 else 0.0

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get a summary of compliance status."""
        total_reqs = len(self.regulatory_requirements)
        compliant = len([r for r in self.regulatory_requirements if r.compliance_status == "compliant"])
        non_compliant = len([r for r in self.regulatory_requirements if r.compliance_status == "non_compliant"])
        in_progress = len([r for r in self.regulatory_requirements if r.compliance_status == "in_progress"])

        return {
            "total_requirements": total_reqs,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "in_progress": in_progress,
            "compliance_rate": compliant / total_reqs if total_reqs > 0 else 0.0,
        }

    def get_control_effectiveness_summary(self) -> Dict[str, Any]:
        """Get a summary of control effectiveness."""
        total_controls = len(self.controls)
        effective = len([c for c in self.controls if c.effectiveness == ControlEffectiveness.EFFECTIVE])
        not_tested = len([c for c in self.controls if c.effectiveness == ControlEffectiveness.NOT_TESTED])

        return {
            "total_controls": total_controls,
            "effective": effective,
            "not_tested": not_tested,
            "effectiveness_rate": effective / total_controls if total_controls > 0 else 0.0,
        }
