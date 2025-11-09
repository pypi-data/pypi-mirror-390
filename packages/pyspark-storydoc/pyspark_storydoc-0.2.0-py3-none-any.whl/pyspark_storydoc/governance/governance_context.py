"""Governance context manager for pipeline-level governance metadata."""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from .metadata import (
    ApprovalStatus,
    CustomerImpactLevel,
    DataClassification,
    GovernanceMetadata,
    RiskEntry,
    RiskMitigation,
)


class GovernanceContext:
    """
    Context manager for pipeline-level governance metadata.

    Allows setting common governance metadata at the pipeline level,
    which can be inherited by individual business concepts.

    Example:
        with GovernanceContext(
            pipeline_name="Insurance Underwriting",
            business_justification="Automated underwriting for efficiency",
            risk_owner="underwriting-team@company.com"
        ) as gov:
            @businessConcept(
                "Filter Applications",
                governance=gov.inherit({"customer_impact_level": "none"})
            )
            def filter_apps(df):
                return df.filter(...)
    """

    def __init__(
        self,
        pipeline_name: str,
        business_justification: Optional[str] = None,
        regulatory_requirement: Optional[str] = None,
        risk_owner: Optional[str] = None,
        data_classification: Optional[str] = None,
        processes_pii: bool = False,
        requires_approval: bool = False,
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize governance context.

        Args:
            pipeline_name: Name of the pipeline
            business_justification: Pipeline-level business justification
            regulatory_requirement: Regulatory requirements
            risk_owner: Team/person responsible for risk management
            data_classification: Data classification level
            processes_pii: Whether pipeline processes PII
            requires_approval: Whether approval is required
            approval_status: Approval status
            approved_by: Who approved
            **kwargs: Additional governance parameters
        """
        self.pipeline_name = pipeline_name
        self.pipeline_metadata = {
            "business_justification": business_justification,
            "regulatory_requirement": regulatory_requirement,
            "risk_owner": risk_owner,
            "data_classification": data_classification,
            "processes_pii": processes_pii,
            "requires_approval": requires_approval,
            "approval_status": approval_status,
            "approved_by": approved_by,
        }
        self.pipeline_metadata.update(kwargs)

        # Track operation-specific metadata
        self.operation_metadata: Dict[str, Dict[str, Any]] = {}

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        return False

    def inherit(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create governance metadata by inheriting pipeline-level defaults
        and applying operation-specific overrides.

        Args:
            overrides: Operation-specific governance metadata

        Returns:
            Complete governance metadata dictionary

        Example:
            gov.inherit({
                "customer_impact_level": "direct",
                "impacting_columns": ["premium"],
                "known_risks": [{"risk_id": "R001", ...}]
            })
        """
        # Start with pipeline defaults
        metadata = self.pipeline_metadata.copy()

        # Apply overrides
        if overrides:
            metadata.update(overrides)

        return metadata

    def register_operation(self, operation_name: str, governance: Dict[str, Any]):
        """
        Register operation-specific governance metadata.

        Args:
            operation_name: Name of the operation
            governance: Governance metadata for this operation
        """
        self.operation_metadata[operation_name] = governance

    def get_operation_metadata(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        Get governance metadata for a specific operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Governance metadata or None if not found
        """
        return self.operation_metadata.get(operation_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pipeline_name": self.pipeline_name,
            "pipeline_metadata": self.pipeline_metadata,
            "operation_metadata": self.operation_metadata,
        }


# Helper functions for creating governance metadata dictionaries
def create_governance_dict(
    business_justification: Optional[str] = None,
    regulatory_requirement: Optional[str] = None,
    known_risks: Optional[List[Dict[str, Any]]] = None,
    risk_mitigations: Optional[List[Dict[str, Any]]] = None,
    risk_owner: Optional[str] = None,
    customer_impact_level: Optional[str] = None,
    impacting_columns: Optional[List[str]] = None,
    impact_description: Optional[str] = None,
    processes_pii: bool = False,
    pii_columns: Optional[List[str]] = None,
    data_classification: Optional[str] = None,
    sensitive_attributes: Optional[List[str]] = None,
    requires_approval: bool = False,
    approval_status: Optional[str] = None,
    approved_by: Optional[str] = None,
    approval_date: Optional[str] = None,
    approval_reference: Optional[str] = None,
    data_retention_days: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Helper function to create a governance metadata dictionary.

    This is a convenience function for creating governance dicts without
    directly instantiating GovernanceMetadata objects.

    Args:
        business_justification: Why this operation exists
        regulatory_requirement: Regulatory requirements
        known_risks: List of risk dictionaries
        risk_mitigations: List of mitigation dictionaries
        risk_owner: Risk owner
        customer_impact_level: Impact level (direct/indirect/none)
        impacting_columns: Columns that impact customers
        impact_description: How customers are impacted
        processes_pii: Whether PII is processed
        pii_columns: PII column names
        data_classification: Data classification
        sensitive_attributes: Sensitive attributes for bias analysis
        requires_approval: Whether approval needed
        approval_status: Approval status
        approved_by: Who approved
        approval_date: Approval date (ISO format)
        approval_reference: Reference to approval ticket
        data_retention_days: Data retention period
        **kwargs: Additional parameters

    Returns:
        Governance metadata dictionary

    Example:
        governance = create_governance_dict(
            business_justification="Calculate premiums",
            customer_impact_level="direct",
            impacting_columns=["premium"],
            processes_pii=True,
            pii_columns=["customer_id"]
        )
    """
    gov_dict = {
        "business_justification": business_justification,
        "regulatory_requirement": regulatory_requirement,
        "risk_owner": risk_owner,
        "customer_impact_level": customer_impact_level,
        "impacting_columns": impacting_columns or [],
        "impact_description": impact_description,
        "processes_pii": processes_pii,
        "pii_columns": pii_columns or [],
        "data_classification": data_classification,
        "sensitive_attributes": sensitive_attributes or [],
        "requires_approval": requires_approval,
        "approval_status": approval_status,
        "approved_by": approved_by,
        "approval_reference": approval_reference,
        "data_retention_days": data_retention_days,
    }

    # Add risks
    if known_risks:
        gov_dict["known_risks"] = known_risks

    # Add mitigations
    if risk_mitigations:
        gov_dict["risk_mitigations"] = risk_mitigations

    # Add approval date
    if approval_date:
        gov_dict["approval_date"] = approval_date

    # Add any additional parameters
    gov_dict.update(kwargs)

    # Remove None values
    gov_dict = {k: v for k, v in gov_dict.items() if v is not None}

    return gov_dict


# Simplified governance helpers
def create_quick_governance(
    why: str,
    risks: Optional[List[str]] = None,
    mitigations: Optional[List[str]] = None,
    impacts_customers: bool = False,
    impacting_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create simplified governance metadata for developers who want minimal overhead.

    Args:
        why: Business justification (required)
        risks: List of risk descriptions
        mitigations: List of mitigation descriptions
        impacts_customers: Boolean flag for customer impact
        impacting_columns: Columns that impact customers

    Returns:
        Governance metadata dictionary

    Example:
        @businessConcept(
            "Filter High-Risk",
            governance_quick=create_quick_governance(
                why="Regulatory requirement for manual review",
                risks=["Potential bias", "False positives"],
                mitigations=["Quarterly audits", "30-day SLA"],
                impacts_customers=True,
                impacting_columns=["approval_status"]
            )
        )
    """
    gov_dict = {
        "business_justification": why,
        "customer_impact_level": "direct" if impacts_customers else "none",
    }

    if impacting_columns:
        gov_dict["impacting_columns"] = impacting_columns

    # Convert simple risk/mitigation lists to structured format
    if risks:
        gov_dict["known_risks"] = [
            {
                "risk_id": f"QR{i+1:02d}",
                "severity": "medium",
                "description": risk,
                "category": "general"
            }
            for i, risk in enumerate(risks)
        ]

    if mitigations:
        # Map mitigations to risks
        gov_dict["risk_mitigations"] = [
            {
                "risk_id": f"QR{i+1:02d}",
                "mitigation": mitigation,
                "status": "implemented"
            }
            for i, mitigation in enumerate(mitigations[:len(risks) if risks else len(mitigations)])
        ]

    return gov_dict
