"""Governance validation framework."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core.graph_builder import BusinessConceptNode
from .metadata import ApprovalStatus, CustomerImpactLevel, GovernanceMetadata


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"  # Must be fixed
    WARNING = "warning"  # Should be addressed
    INFO = "info"  # Informational


@dataclass
class ValidationIssue:
    """A governance validation issue."""
    severity: ValidationSeverity
    field: str
    message: str
    recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity.value,
            "field": self.field,
            "message": self.message,
            "recommendation": self.recommendation,
        }


@dataclass
class ValidationResult:
    """Result of governance validation."""
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    warnings_count: int = 0
    errors_count: int = 0
    completeness_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "issues": [issue.to_dict() for issue in self.issues],
            "warnings_count": self.warnings_count,
            "errors_count": self.errors_count,
            "completeness_score": self.completeness_score,
        }


class GovernanceValidator:
    """
    Validator for governance metadata completeness and consistency.
    """

    def __init__(self, strict_mode: bool = False):
        """
        Initialize governance validator.

        Args:
            strict_mode: If True, treat warnings as errors
        """
        self.strict_mode = strict_mode

    def validate(self, governance_metadata: GovernanceMetadata) -> ValidationResult:
        """
        Validate governance metadata.

        Args:
            governance_metadata: The governance metadata to validate

        Returns:
            ValidationResult with any issues found
        """
        issues = []

        # Check business justification
        if not governance_metadata.business_justification:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field="business_justification",
                message="Business justification is required",
                recommendation="Provide a clear explanation of why this operation is necessary"
            ))

        # Check risks and mitigations
        if governance_metadata.known_risks:
            if not governance_metadata.risk_mitigations:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="risk_mitigations",
                    message="Known risks identified but no mitigations provided",
                    recommendation="Document mitigation strategies for each identified risk"
                ))
            else:
                # Check that all risks have mitigations
                risk_ids = {risk.risk_id for risk in governance_metadata.known_risks}
                mitigation_risk_ids = {mit.risk_id for mit in governance_metadata.risk_mitigations}

                unmitigated = risk_ids - mitigation_risk_ids
                if unmitigated:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        field="risk_mitigations",
                        message=f"Risks without mitigations: {', '.join(unmitigated)}",
                        recommendation="Provide mitigation strategies for all identified risks"
                    ))

        # Check PII handling
        if governance_metadata.processes_pii:
            if not governance_metadata.pii_columns:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="pii_columns",
                    message="PII processing declared but no PII columns specified",
                    recommendation="List all columns containing PII"
                ))

            if not governance_metadata.data_classification:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="data_classification",
                    message="PII processing requires data classification",
                    recommendation="Specify data classification (confidential/restricted)"
                ))

        # Check customer impact
        if governance_metadata.customer_impact_level:
            if governance_metadata.customer_impact_level in [CustomerImpactLevel.DIRECT, CustomerImpactLevel.INDIRECT]:
                if not governance_metadata.impacting_columns:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        field="impacting_columns",
                        message="Customer impact declared but no impacting columns specified",
                        recommendation="List columns that directly impact customers"
                    ))

                if not governance_metadata.impact_description:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        field="impact_description",
                        message="Customer impact declared but no description provided",
                        recommendation="Describe how this operation impacts customers"
                    ))

        # Check approval requirements
        if governance_metadata.requires_approval:
            if not governance_metadata.approval_status:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="approval_status",
                    message="Approval required but status not specified",
                    recommendation="Set approval status (pending/approved/rejected/exempt)"
                ))
            elif governance_metadata.approval_status == ApprovalStatus.PENDING:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="approval_status",
                    message="Approval is pending - not ready for production",
                    recommendation="Obtain necessary approvals before deployment"
                ))
            elif governance_metadata.approval_status == ApprovalStatus.APPROVED:
                if not governance_metadata.approved_by:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        field="approved_by",
                        message="Approval granted but approver not recorded",
                        recommendation="Record who approved this operation"
                    ))

        # Check sensitive attributes
        if governance_metadata.sensitive_attributes:
            if not governance_metadata.bias_analysis_results:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="bias_analysis_results",
                    message="Sensitive attributes declared but no bias analysis performed",
                    recommendation="Conduct bias analysis and document results"
                ))

        # Check risk ownership
        if governance_metadata.known_risks or governance_metadata.inferred_risks:
            if not governance_metadata.risk_owner:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="risk_owner",
                    message="Risks identified but no risk owner assigned",
                    recommendation="Assign a team or individual responsible for risk management"
                ))

        # Check review dates
        if governance_metadata.customer_impact_level == CustomerImpactLevel.DIRECT:
            if not governance_metadata.last_reviewed_date:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field="last_reviewed_date",
                    message="High-impact operation should have regular governance reviews",
                    recommendation="Establish review schedule (recommend quarterly for high-impact operations)"
                ))

        # Calculate counts
        errors = sum(1 for issue in issues if issue.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)

        # Determine validity
        is_valid = errors == 0 if not self.strict_mode else (errors == 0 and warnings == 0)

        # Calculate completeness
        completeness = governance_metadata.get_completeness_score()

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            warnings_count=warnings,
            errors_count=errors,
            completeness_score=completeness
        )

    def validate_concept_node(self, concept_node: BusinessConceptNode) -> ValidationResult:
        """
        Validate a business concept node's governance metadata.

        Args:
            concept_node: The business concept node to validate

        Returns:
            ValidationResult
        """
        if not hasattr(concept_node, 'governance_metadata') or not concept_node.governance_metadata:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field="governance_metadata",
                    message="No governance metadata found",
                    recommendation="Add governance metadata to this business concept"
                )],
                warnings_count=0,
                errors_count=1,
                completeness_score=0.0
            )

        return self.validate(concept_node.governance_metadata)

    def generate_validation_report(self, validation_result: ValidationResult) -> str:
        """
        Generate a human-readable validation report.

        Args:
            validation_result: The validation result

        Returns:
            Formatted validation report
        """
        lines = []
        lines.append("# Governance Validation Report")
        lines.append("")

        # Status
        status = "[OK] VALID" if validation_result.is_valid else "[FAIL] INVALID"
        lines.append(f"**Status:** {status}")
        lines.append(f"**Completeness Score:** {validation_result.completeness_score:.1%}")
        lines.append(f"**Errors:** {validation_result.errors_count}")
        lines.append(f"**Warnings:** {validation_result.warnings_count}")
        lines.append("")

        # Issues
        if validation_result.issues:
            lines.append("## Issues")
            lines.append("")

            errors = [i for i in validation_result.issues if i.severity == ValidationSeverity.ERROR]
            warnings = [i for i in validation_result.issues if i.severity == ValidationSeverity.WARNING]
            infos = [i for i in validation_result.issues if i.severity == ValidationSeverity.INFO]

            if errors:
                lines.append("### Errors (Must Fix)")
                lines.append("")
                for issue in errors:
                    lines.append(f"- **{issue.field}:** {issue.message}")
                    if issue.recommendation:
                        lines.append(f"  - *Recommendation:* {issue.recommendation}")
                lines.append("")

            if warnings:
                lines.append("### Warnings (Should Address)")
                lines.append("")
                for issue in warnings:
                    lines.append(f"- **{issue.field}:** {issue.message}")
                    if issue.recommendation:
                        lines.append(f"  - *Recommendation:* {issue.recommendation}")
                lines.append("")

            if infos:
                lines.append("### Informational")
                lines.append("")
                for issue in infos:
                    lines.append(f"- **{issue.field}:** {issue.message}")
                lines.append("")
        else:
            lines.append("## [OK] No Issues Found")
            lines.append("")
            lines.append("Governance metadata is complete and valid.")

        return "\n".join(lines)
