"""Builder functions for governance metadata to make it easy for developers."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .enhanced_metadata import (
    ApprovalEntry,
    ChangeLogEntry,
    ControlEffectiveness,
    ControlEntry,
    ControlStatus,
    EnhancedGovernanceMetadata,
    RegulatoryFramework,
    RegulatoryRequirement,
    StakeholderEntry,
)


class GovernanceBuilder:
    """
    Fluent builder for governance metadata.

    Makes it easy to construct comprehensive governance metadata.

    Example:
        >>> gov = (GovernanceBuilder("Calculate Risk Score")
        ...     .business_justification("Assess credit risk for loan decisions")
        ...     .add_stakeholder("business_owner", "risk-team@company.com")
        ...     .add_risk("RISK-001", "high", "Incorrect scores lead to bad loans")
        ...     .add_control("CTRL-001", "RISK-001", "Actuarial validation of formula")
        ...     .add_approval("business", "sarah@company.com", "2024-01-14")
        ...     .add_gdpr_requirement("Article 22", "Automated decision-making", "compliant")
        ...     .build())
    """

    def __init__(self, operation_name: str):
        """Initialize builder with operation name."""
        self._data = {
            "operation_name": operation_name,
            "stakeholders": [],
            "known_risks": [],
            "controls": [],
            "approvals": [],
            "regulatory_requirements": [],
            "change_history": [],
            "pii_columns": [],
            "required_access_roles": [],
            "evidence_files": [],
        }

    def business_justification(self, justification: str) -> 'GovernanceBuilder':
        """Set business justification (required)."""
        self._data["business_justification"] = justification
        return self

    def operation_id(self, op_id: str) -> 'GovernanceBuilder':
        """Set operation ID."""
        self._data["operation_id"] = op_id
        return self

    def add_stakeholder(
        self,
        role: str,
        name_or_email: str,
        responsibilities: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """
        Add a stakeholder.

        Common roles: business_owner, technical_owner, data_steward,
                     compliance_owner, security_contact, risk_owner
        """
        self._data["stakeholders"].append(
            StakeholderEntry(
                role=role,
                name_or_email=name_or_email,
                responsibilities=responsibilities
            )
        )
        return self

    def add_risk(
        self,
        risk_id: str,
        severity: str,
        description: str,
        likelihood: Optional[str] = None,
        impact: Optional[str] = None,
        category: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """
        Add a known risk.

        Severity: critical, high, medium, low
        Likelihood: high, medium, low
        """
        self._data["known_risks"].append({
            "risk_id": risk_id,
            "severity": severity,
            "description": description,
            "likelihood": likelihood,
            "impact": impact,
            "category": category,
        })
        return self

    def add_control(
        self,
        control_id: str,
        risk_id: str,
        description: str,
        status: ControlStatus = ControlStatus.IMPLEMENTED,
        effectiveness: ControlEffectiveness = ControlEffectiveness.NOT_TESTED,
        owner: Optional[str] = None,
        evidence_location: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Add a control for risk mitigation."""
        self._data["controls"].append(
            ControlEntry(
                control_id=control_id,
                risk_id=risk_id,
                description=description,
                status=status,
                effectiveness=effectiveness,
                owner=owner,
                evidence_location=evidence_location,
            )
        )
        return self

    def test_control(
        self,
        control_id: str,
        test_date: datetime,
        effectiveness: ControlEffectiveness,
        test_result: str,
        next_test_date: Optional[datetime] = None
    ) -> 'GovernanceBuilder':
        """Record control testing results."""
        for control in self._data["controls"]:
            if control.control_id == control_id:
                control.last_test_date = test_date
                control.effectiveness = effectiveness
                control.test_result = test_result
                control.next_test_date = next_test_date
                break
        return self

    def residual_risk(
        self,
        level: str,
        accepted_by: str,
        acceptance_date: datetime
    ) -> 'GovernanceBuilder':
        """Set residual risk acceptance."""
        self._data["residual_risk_level"] = level
        self._data["residual_risk_accepted_by"] = accepted_by
        self._data["residual_risk_acceptance_date"] = acceptance_date
        return self

    def add_approval(
        self,
        approval_type: str,
        approved_by: str,
        approval_date: str,  # ISO format or datetime
        approval_id: Optional[str] = None,
        comments: Optional[str] = None,
        evidence_location: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """
        Add an approval to the trail.

        Common types: business, technical, compliance, legal, security, risk_committee
        """
        if isinstance(approval_date, str):
            approval_date = datetime.fromisoformat(approval_date)

        self._data["approvals"].append(
            ApprovalEntry(
                approval_type=approval_type,
                approved_by=approved_by,
                approval_date=approval_date,
                approval_id=approval_id,
                comments=comments,
                evidence_location=evidence_location,
            )
        )
        return self

    def add_regulatory_requirement(
        self,
        framework: RegulatoryFramework,
        requirement_id: str,
        requirement_description: str,
        compliance_status: str = "compliant",
        evidence_location: Optional[str] = None,
        last_review_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Add a regulatory requirement."""
        self._data["regulatory_requirements"].append(
            RegulatoryRequirement(
                framework=framework,
                requirement_id=requirement_id,
                requirement_description=requirement_description,
                compliance_status=compliance_status,
                evidence_location=evidence_location,
                last_review_date=last_review_date,
                notes=notes,
            )
        )
        return self

    def add_gdpr_requirement(
        self,
        article: str,
        description: str,
        compliance_status: str = "compliant",
        evidence_location: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Shortcut for adding GDPR requirement."""
        return self.add_regulatory_requirement(
            RegulatoryFramework.GDPR,
            article,
            description,
            compliance_status,
            evidence_location
        )

    def add_ccpa_requirement(
        self,
        section: str,
        description: str,
        compliance_status: str = "compliant",
        evidence_location: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Shortcut for adding CCPA requirement."""
        return self.add_regulatory_requirement(
            RegulatoryFramework.CCPA,
            section,
            description,
            compliance_status,
            evidence_location
        )

    def add_change(
        self,
        change_date: datetime,
        changed_by: str,
        description: str,
        reason: str,
        version_from: Optional[str] = None,
        version_to: Optional[str] = None,
        approval_id: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Add a change log entry."""
        self._data["change_history"].append(
            ChangeLogEntry(
                change_date=change_date,
                changed_by=changed_by,
                change_description=description,
                change_reason=reason,
                version_from=version_from,
                version_to=version_to,
                approval_required=approval_id is not None,
                approval_id=approval_id,
            )
        )
        return self

    def current_version(self, version: str) -> 'GovernanceBuilder':
        """Set current version."""
        self._data["current_version"] = version
        return self

    def pii(
        self,
        processes_pii: bool,
        pii_columns: Optional[List[str]] = None,
        data_classification: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Set PII information."""
        self._data["processes_pii"] = processes_pii
        if pii_columns:
            self._data["pii_columns"] = pii_columns
        if data_classification:
            self._data["data_classification"] = data_classification
        return self

    def access_control(
        self,
        required_roles: List[str],
        approval_required: bool = False,
        approval_id: Optional[str] = None
    ) -> 'GovernanceBuilder':
        """Set access control requirements."""
        self._data["required_access_roles"] = required_roles
        self._data["access_approval_required"] = approval_required
        self._data["access_approval_id"] = approval_id
        return self

    def evidence(
        self,
        base_path: str,
        files: Optional[List[str]] = None
    ) -> 'GovernanceBuilder':
        """Set evidence package location."""
        self._data["evidence_base_path"] = base_path
        if files:
            self._data["evidence_files"] = files
        return self

    def dates(
        self,
        created: Optional[datetime] = None,
        last_modified: Optional[datetime] = None,
        last_review: Optional[datetime] = None,
        next_review: Optional[datetime] = None
    ) -> 'GovernanceBuilder':
        """Set important dates."""
        if created:
            self._data["created_date"] = created
        if last_modified:
            self._data["last_modified_date"] = last_modified
        if last_review:
            self._data["last_review_date"] = last_review
        if next_review:
            self._data["next_review_date"] = next_review
        return self

    def audit_ready(self, ready: bool = True) -> 'GovernanceBuilder':
        """Mark as audit ready."""
        self._data["audit_ready"] = ready
        return self

    def build(self) -> EnhancedGovernanceMetadata:
        """Build the governance metadata."""
        return EnhancedGovernanceMetadata(**self._data)


def create_minimal_governance(
    operation_name: str,
    business_justification: str,
    business_owner: str
) -> EnhancedGovernanceMetadata:
    """
    Create minimal governance metadata (for low-risk operations).

    This is the absolute minimum for audit readiness.
    """
    return (GovernanceBuilder(operation_name)
        .business_justification(business_justification)
        .add_stakeholder("business_owner", business_owner)
        .dates(created=datetime.now())
        .build())


def create_standard_governance(
    operation_name: str,
    business_justification: str,
    business_owner: str,
    technical_owner: str,
    risks: List[Dict[str, str]],
    approvals: List[Dict[str, Any]]
) -> EnhancedGovernanceMetadata:
    """
    Create standard governance metadata (for medium-risk operations).

    Args:
        operation_name: Name of the operation
        business_justification: Why this operation exists
        business_owner: Business owner email
        technical_owner: Technical owner email
        risks: List of dicts with keys: risk_id, severity, description
        approvals: List of dicts with keys: approval_type, approved_by, approval_date

    Returns:
        Governance metadata with risks, controls, and approvals
    """
    builder = (GovernanceBuilder(operation_name)
        .business_justification(business_justification)
        .add_stakeholder("business_owner", business_owner)
        .add_stakeholder("technical_owner", technical_owner)
        .dates(created=datetime.now()))

    # Add risks and basic controls
    for risk in risks:
        builder.add_risk(
            risk["risk_id"],
            risk["severity"],
            risk["description"],
            likelihood=risk.get("likelihood"),
            impact=risk.get("impact")
        )
        # Add a default control for each risk
        builder.add_control(
            f"CTRL-{risk['risk_id'].split('-')[1]}",
            risk["risk_id"],
            f"Mitigation for {risk['risk_id']}",
            owner=technical_owner
        )

    # Add approvals
    for approval in approvals:
        builder.add_approval(
            approval["approval_type"],
            approval["approved_by"],
            approval["approval_date"],
            approval_id=approval.get("approval_id"),
            comments=approval.get("comments")
        )

    return builder.build()


def create_comprehensive_governance(
    operation_name: str,
    business_justification: str,
    stakeholders: Dict[str, str],
    risks: List[Dict[str, Any]],
    controls: List[Dict[str, Any]],
    approvals: List[Dict[str, Any]],
    regulatory_requirements: List[Dict[str, Any]],
    pii_info: Optional[Dict[str, Any]] = None
) -> EnhancedGovernanceMetadata:
    """
    Create comprehensive governance metadata (for high-risk/critical operations).

    This includes all governance elements for full audit readiness.

    Args:
        operation_name: Name of the operation
        business_justification: Why this operation exists
        stakeholders: Dict mapping role to email (business_owner, technical_owner, etc.)
        risks: List of risk dicts
        controls: List of control dicts
        approvals: List of approval dicts
        regulatory_requirements: List of regulatory requirement dicts
        pii_info: Optional PII information dict

    Returns:
        Comprehensive governance metadata
    """
    builder = (GovernanceBuilder(operation_name)
        .business_justification(business_justification)
        .dates(created=datetime.now()))

    # Add stakeholders
    for role, email in stakeholders.items():
        builder.add_stakeholder(role, email)

    # Add risks
    for risk in risks:
        builder.add_risk(
            risk["risk_id"],
            risk["severity"],
            risk["description"],
            likelihood=risk.get("likelihood"),
            impact=risk.get("impact"),
            category=risk.get("category")
        )

    # Add controls
    for control in controls:
        builder.add_control(
            control["control_id"],
            control["risk_id"],
            control["description"],
            status=control.get("status", ControlStatus.IMPLEMENTED),
            effectiveness=control.get("effectiveness", ControlEffectiveness.NOT_TESTED),
            owner=control.get("owner"),
            evidence_location=control.get("evidence_location")
        )

    # Add approvals
    for approval in approvals:
        builder.add_approval(
            approval["approval_type"],
            approval["approved_by"],
            approval["approval_date"],
            approval_id=approval.get("approval_id"),
            comments=approval.get("comments"),
            evidence_location=approval.get("evidence_location")
        )

    # Add regulatory requirements
    for req in regulatory_requirements:
        framework = req.get("framework")
        if isinstance(framework, str):
            framework = RegulatoryFramework[framework.upper()]

        builder.add_regulatory_requirement(
            framework,
            req["requirement_id"],
            req["requirement_description"],
            compliance_status=req.get("compliance_status", "compliant"),
            evidence_location=req.get("evidence_location"),
            notes=req.get("notes")
        )

    # Add PII info if provided
    if pii_info:
        builder.pii(
            pii_info.get("processes_pii", False),
            pii_info.get("pii_columns"),
            pii_info.get("data_classification")
        )

    return builder.build()
