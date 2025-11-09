"""Governance Audit Report Generator matching the template requirements."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .enhanced_metadata import (
    ControlEffectiveness,
    EnhancedGovernanceMetadata,
    RegulatoryFramework,
)


class GovernanceAuditReportGenerator:
    """
    Generates governance audit reports matching the auditor output template.

    This generates comprehensive audit reports with complete evidence trails,
    control effectiveness testing, and regulatory compliance mapping.
    """

    def __init__(self):
        """Initialize the report generator."""
        self.report_id_counter = 1

    def generate_audit_report(
        self,
        pipeline_name: str,
        operations: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """
        Generate a complete governance audit report.

        Args:
            pipeline_name: Name of the pipeline being audited
            operations: List of operations with governance metadata
            output_path: Where to save the report

        Returns:
            Path to the generated report
        """
        report_date = datetime.now()
        report_id = f"GOV-AUDIT-{report_date.strftime('%Y-%m')}-{str(self.report_id_counter).zfill(3)}"
        self.report_id_counter += 1

        # Calculate overall status
        overall_status = self._calculate_overall_status(operations)

        # Build report content
        content = []
        content.append(f"# Governance Audit Report: {pipeline_name}")
        content.append("")
        content.append(f"**Report Date**: {report_date.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append(f"**Pipeline**: {pipeline_name}")
        content.append(f"**Report ID**: {report_id}")
        content.append(f"**Auditor**: compliance-team@company.com")
        content.append(f"**Status**: {overall_status}")
        content.append("")
        content.append("---")
        content.append("")

        # Executive Summary
        content.extend(self._generate_executive_summary(pipeline_name, operations))

        # Business Justification Summary
        content.extend(self._generate_business_justification_summary(operations))

        # Risk Assessment Summary
        content.extend(self._generate_risk_assessment_summary(operations))

        # Regulatory Compliance Mapping
        content.extend(self._generate_regulatory_compliance_mapping(operations))

        # PII Data Classification
        content.extend(self._generate_pii_classification(operations))

        # Audit Trail
        content.extend(self._generate_audit_trail(operations))

        # Control Effectiveness Summary
        content.extend(self._generate_control_effectiveness_summary(operations))

        # Recommendations
        content.extend(self._generate_recommendations(operations))

        # Audit Readiness Assessment
        content.extend(self._generate_audit_readiness_assessment(operations))

        # Attestation
        content.extend(self._generate_attestation(report_id, report_date))

        # Write report
        report_content = "\n".join(content)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return output_path

    def _calculate_overall_status(self, operations: List[Dict[str, Any]]) -> str:
        """Calculate overall compliance status."""
        all_compliant = True

        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                return "[WARN] INCOMPLETE"

            # Check if has required elements
            if not gov.business_justification:
                all_compliant = False

            if gov.known_risks and not gov.controls:
                all_compliant = False

            # Check regulatory compliance
            for req in gov.regulatory_requirements:
                if req.compliance_status != "compliant":
                    all_compliant = False

        return "[OK] COMPLIANT" if all_compliant else "[WARN] PARTIAL COMPLIANCE"

    def _generate_executive_summary(
        self,
        pipeline_name: str,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate executive summary section."""
        content = []
        content.append("## Executive Summary")
        content.append("")

        # Count operations with governance
        total_ops = len(operations)
        ops_with_governance = len([op for op in operations if op.get('governance_metadata')])

        # Count risks and controls
        total_risks = sum(len(op.get('governance_metadata', EnhancedGovernanceMetadata(
            business_justification="", operation_name="")).known_risks) for op in operations)
        total_controls = sum(len(op.get('governance_metadata', EnhancedGovernanceMetadata(
            business_justification="", operation_name="")).controls) for op in operations)

        content.append(f"**Overall Compliance Status**: {self._calculate_overall_status(operations)}")
        content.append("")
        content.append("**Summary**:")
        content.append(f"This pipeline contains {total_ops} business operations. ")
        content.append(f"{ops_with_governance} operations have governance metadata documented.")
        content.append("")
        content.append("**Key Findings**:")
        content.append(f"- {'[OK]' if ops_with_governance == total_ops else '[WARN]'} {ops_with_governance}/{total_ops} operations have governance metadata")
        content.append(f"- {'[OK]' if total_risks > 0 else '[WARN]'} {total_risks} risks identified and documented")
        content.append(f"- {'[OK]' if total_controls > 0 else '[WARN]'} {total_controls} controls implemented")
        content.append("")
        content.append("---")
        content.append("")

        return content

    def _generate_business_justification_summary(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate business justification summary section."""
        content = []
        content.append("## Business Justification Summary")
        content.append("")

        for i, op in enumerate(operations, 1):
            gov = op.get('governance_metadata')
            if not gov:
                continue

            op_name = gov.operation_name
            content.append(f"### Operation {i}: {op_name}")
            content.append("")

            # Business Justification
            content.append("**Business Justification**:")
            content.append("```")
            content.append(gov.business_justification or "Not documented")
            content.append("```")
            content.append("")

            # Stakeholders
            if gov.stakeholders:
                content.append("**Stakeholders**:")
                for stakeholder in gov.stakeholders:
                    role = stakeholder.role.replace("_", " ").title()
                    content.append(f"- {role}: {stakeholder.name_or_email}")
                content.append("")

            # Approvals
            if gov.approvals:
                content.append("**Approvals**:")
                for approval in gov.approvals:
                    approval_type = approval.approval_type.replace("_", " ").title()
                    date_str = approval.approval_date.strftime("%Y-%m-%d %H:%M:%S UTC")
                    content.append(f"- **{approval_type}**:")
                    content.append(f"  - Approved By: {approval.approved_by}")
                    content.append(f"  - Date: {date_str}")
                    if approval.approval_id:
                        content.append(f"  - Approval ID: {approval.approval_id}")
                    if approval.evidence_location:
                        content.append(f"  - Evidence: `{approval.evidence_location}`")
                content.append("")

            content.append("---")
            content.append("")

        return content

    def _generate_risk_assessment_summary(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate risk assessment summary section."""
        content = []
        content.append("## Risk Assessment Summary")
        content.append("")

        # Count risks by severity
        risk_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                continue

            for risk in gov.known_risks:
                severity = risk.get("severity", "").lower()
                if severity in risk_counts:
                    risk_counts[severity] += 1

        total_risks = sum(risk_counts.values())

        content.append(f"**Total Risks Identified**: {total_risks}")
        if total_risks > 0:
            content.append(f"- Critical: {risk_counts['critical']}")
            content.append(f"- High: {risk_counts['high']}")
            content.append(f"- Medium: {risk_counts['medium']}")
            content.append(f"- Low: {risk_counts['low']}")
        content.append("")

        # Detail each high/critical risk
        content.append("### High-Risk Operations:")
        content.append("")

        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                continue

            high_risks = [r for r in gov.known_risks
                         if r.get("severity", "").lower() in ["critical", "high"]]

            if not high_risks:
                continue

            content.append(f"#### Operation: {gov.operation_name}")
            content.append("")

            for risk in high_risks:
                risk_id = risk.get("risk_id", "UNKNOWN")
                severity = risk.get("severity", "").upper()
                description = risk.get("description", "No description")

                content.append(f"**Risk ID**: {risk_id}")
                content.append(f"**Severity**: {severity}")
                content.append("")
                content.append("**Risk Description**:")
                content.append("```")
                content.append(description)
                content.append("```")
                content.append("")

                # Find associated controls
                associated_controls = [c for c in gov.controls if c.risk_id == risk_id]

                if associated_controls:
                    content.append("**Mitigation Strategies**:")
                    content.append("")
                    for i, control in enumerate(associated_controls, 1):
                        content.append(f"{i}. **{control.control_id}**: {control.description}")
                        content.append(f"   - Status: {control.status.value}")
                        content.append(f"   - Effectiveness: {control.effectiveness.value}")
                        if control.owner:
                            content.append(f"   - Owner: {control.owner}")
                        if control.evidence_location:
                            content.append(f"   - Evidence: `{control.evidence_location}`")
                        content.append("")

                # Residual risk
                if gov.residual_risk_level:
                    content.append(f"**Residual Risk**: {gov.residual_risk_level.upper()}")
                    if gov.residual_risk_accepted_by:
                        content.append(f"**Accepted By**: {gov.residual_risk_accepted_by}")
                        if gov.residual_risk_acceptance_date:
                            date_str = gov.residual_risk_acceptance_date.strftime("%Y-%m-%d")
                            content.append(f"**Acceptance Date**: {date_str}")
                    content.append("")

                content.append("---")
                content.append("")

        return content

    def _generate_regulatory_compliance_mapping(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate regulatory compliance mapping section."""
        content = []
        content.append("## Regulatory Compliance Mapping")
        content.append("")

        # Group requirements by framework
        frameworks = {}

        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                continue

            for req in gov.regulatory_requirements:
                framework_name = req.framework.value
                if framework_name not in frameworks:
                    frameworks[framework_name] = []
                frameworks[framework_name].append((op, req))

        if not frameworks:
            content.append("*No regulatory requirements documented*")
            content.append("")
            content.append("---")
            content.append("")
            return content

        # Generate section for each framework
        for framework_name in sorted(frameworks.keys()):
            content.append(f"### {framework_name} Compliance")
            content.append("")

            requirements = frameworks[framework_name]

            # Count compliance status
            total_reqs = len(requirements)
            compliant = len([r for _, r in requirements if r.compliance_status == "compliant"])
            non_compliant = len([r for _, r in requirements if r.compliance_status == "non_compliant"])

            content.append(f"**Total Requirements**: {total_reqs}")
            content.append(f"**Compliant**: {compliant} [OK]")
            if non_compliant > 0:
                content.append(f"**Non-Compliant**: {non_compliant} [FAIL]")
            content.append("")

            # List each requirement
            for op, req in requirements:
                gov = op.get('governance_metadata')
                status_icon = "[OK]" if req.compliance_status == "compliant" else "[FAIL]"

                content.append(f"#### {req.requirement_id}: {status_icon}")
                content.append("")
                content.append(f"**Operation**: {gov.operation_name}")
                content.append(f"**Requirement**: {req.requirement_description}")
                content.append(f"**Compliance Status**: {req.compliance_status.upper()}")
                content.append("")

                if req.evidence_location:
                    content.append(f"**Evidence**: `{req.evidence_location}`")
                    content.append("")

                if req.last_review_date:
                    date_str = req.last_review_date.strftime("%Y-%m-%d")
                    content.append(f"**Last Review**: {date_str}")
                    content.append("")

                if req.notes:
                    content.append(f"**Notes**: {req.notes}")
                    content.append("")

                content.append("---")
                content.append("")

            # Overall framework status
            compliance_rate = compliant / total_reqs if total_reqs > 0 else 0.0
            overall_status = "[OK] COMPLIANT" if compliance_rate == 1.0 else "[WARN] PARTIAL COMPLIANCE"

            content.append(f"**{framework_name} Overall Status**: {overall_status}")
            content.append("")

        return content

    def _generate_pii_classification(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate PII data classification section."""
        content = []
        content.append("## PII Data Classification")
        content.append("")

        pii_operations = [op for op in operations
                         if op.get('governance_metadata') and
                         op.get('governance_metadata').processes_pii]

        if not pii_operations:
            content.append("*No PII processing detected*")
            content.append("")
            content.append("---")
            content.append("")
            return content

        content.append(f"**Operations Processing PII**: {len(pii_operations)}")
        content.append("")

        for op in pii_operations:
            gov = op.get('governance_metadata')

            content.append(f"### Operation: {gov.operation_name}")
            content.append("")

            content.append(f"**Data Classification**: {gov.data_classification or 'Not specified'}")
            content.append("")

            content.append("**PII Columns**:")
            for col in gov.pii_columns:
                content.append(f"- `{col}`")
            content.append("")

            # Access control requirements
            if gov.required_access_roles:
                content.append("**Required Access Roles**:")
                for role in gov.required_access_roles:
                    content.append(f"- {role}")
                content.append("")

            if gov.access_approval_required:
                content.append("**Access Approval Required**: [OK] YES")
                if gov.access_approval_id:
                    content.append(f"**Approval ID**: {gov.access_approval_id}")
                content.append("")

            content.append("---")
            content.append("")

        return content

    def _generate_audit_trail(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate audit trail section."""
        content = []
        content.append("## Audit Trail")
        content.append("")

        for op in operations:
            gov = op.get('governance_metadata')
            if not gov or not gov.change_history:
                continue

            content.append(f"### Operation: {gov.operation_name}")
            content.append("")

            content.append("**Change History**:")
            content.append("")

            for change in sorted(gov.change_history, key=lambda c: c.change_date, reverse=True):
                date_str = change.change_date.strftime("%Y-%m-%d %H:%M:%S")
                content.append(f"#### {date_str}")
                content.append("")
                content.append(f"**Changed By**: {change.changed_by}")
                content.append(f"**Description**: {change.change_description}")
                content.append(f"**Reason**: {change.change_reason}")
                content.append("")

                if change.version_from and change.version_to:
                    content.append(f"**Version**: {change.version_from} -> {change.version_to}")
                    content.append("")

                if change.approval_required and change.approval_id:
                    content.append(f"**Approval Required**: [OK] YES (ID: {change.approval_id})")
                    content.append("")

                content.append("---")
                content.append("")

        return content

    def _generate_control_effectiveness_summary(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate control effectiveness summary section."""
        content = []
        content.append("## Control Effectiveness Summary")
        content.append("")

        # Count all controls
        all_controls = []
        for op in operations:
            gov = op.get('governance_metadata')
            if gov:
                all_controls.extend(gov.controls)

        if not all_controls:
            content.append("*No controls documented*")
            content.append("")
            content.append("---")
            content.append("")
            return content

        total_controls = len(all_controls)
        effective = len([c for c in all_controls if c.effectiveness == ControlEffectiveness.EFFECTIVE])
        partially_effective = len([c for c in all_controls if c.effectiveness == ControlEffectiveness.PARTIALLY_EFFECTIVE])
        not_tested = len([c for c in all_controls if c.effectiveness == ControlEffectiveness.NOT_TESTED])

        content.append(f"**Total Controls**: {total_controls}")
        content.append(f"**Effective**: {effective} [OK]")
        content.append(f"**Partially Effective**: {partially_effective} [WARN]")
        content.append(f"**Not Tested**: {not_tested} [WARN]")
        content.append("")

        effectiveness_rate = effective / total_controls if total_controls > 0 else 0.0
        content.append(f"**Control Effectiveness Rate**: {effectiveness_rate:.1%}")
        content.append("")

        # List all controls
        content.append("### Control Details")
        content.append("")

        content.append("| Control ID | Description | Risk ID | Status | Effectiveness | Last Test |")
        content.append("|------------|-------------|---------|--------|---------------|-----------|")

        for control in sorted(all_controls, key=lambda c: c.control_id):
            last_test = control.last_test_date.strftime("%Y-%m-%d") if control.last_test_date else "Never"
            status_icon = "[OK]" if control.effectiveness == ControlEffectiveness.EFFECTIVE else "[WARN]"

            content.append(f"| {control.control_id} | {control.description[:40]} | {control.risk_id} | "
                          f"{control.status.value} | {control.effectiveness.value} {status_icon} | {last_test} |")

        content.append("")
        content.append("---")
        content.append("")

        return content

    def _generate_recommendations(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations section."""
        content = []
        content.append("## Recommendations")
        content.append("")

        recommendations = []

        # Check for missing governance metadata
        ops_without_governance = [op for op in operations if not op.get('governance_metadata')]
        if ops_without_governance:
            recommendations.append({
                "priority": "HIGH",
                "title": "Add Governance Metadata to All Operations",
                "description": f"{len(ops_without_governance)} operations missing governance metadata",
                "action": "Document business justification, risks, and approvals for all operations"
            })

        # Check for untested controls
        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                continue

            untested_controls = [c for c in gov.controls if c.effectiveness == ControlEffectiveness.NOT_TESTED]
            if untested_controls:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": f"Test Controls in '{gov.operation_name}'",
                    "description": f"{len(untested_controls)} controls have not been tested",
                    "action": f"Conduct control effectiveness testing for {', '.join(c.control_id for c in untested_controls)}"
                })

        # Check for missing approvals
        for op in operations:
            gov = op.get('governance_metadata')
            if not gov:
                continue

            if gov.known_risks and not gov.approvals:
                recommendations.append({
                    "priority": "HIGH",
                    "title": f"Obtain Approvals for '{gov.operation_name}'",
                    "description": "Operation has risks but no documented approvals",
                    "action": "Obtain business, technical, and compliance approvals"
                })

        if not recommendations:
            content.append("*No recommendations - governance is comprehensive*")
            content.append("")
        else:
            for i, rec in enumerate(recommendations, 1):
                content.append(f"### Recommendation {i}: {rec['title']}")
                content.append("")
                content.append(f"**Priority**: {rec['priority']}")
                content.append(f"**Description**: {rec['description']}")
                content.append(f"**Action**: {rec['action']}")
                content.append("")
                content.append("---")
                content.append("")

        return content

    def _generate_audit_readiness_assessment(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate audit readiness assessment section."""
        content = []
        content.append("## Audit Readiness Assessment")
        content.append("")

        total_ops = len(operations)
        ops_with_governance = len([op for op in operations if op.get('governance_metadata')])

        # Calculate average audit readiness score
        scores = []
        for op in operations:
            gov = op.get('governance_metadata')
            if gov:
                scores.append(gov.get_audit_readiness_score())

        avg_score = sum(scores) / len(scores) if scores else 0.0

        if avg_score >= 0.8:
            overall_status = "[OK] AUDIT READY"
        elif avg_score >= 0.6:
            overall_status = "[WARN] MOSTLY READY (Minor Gaps)"
        else:
            overall_status = "[FAIL] NOT READY (Significant Gaps)"

        content.append(f"**Overall Status**: {overall_status}")
        content.append(f"**Average Readiness Score**: {avg_score:.1%}")
        content.append("")

        content.append("### Readiness Checklist")
        content.append("")

        checks = {
            "Business justification documented": ops_with_governance == total_ops,
            "Risk assessments completed": all(op.get('governance_metadata') and op.get('governance_metadata').known_risks for op in operations if op.get('governance_metadata')),
            "Controls implemented": all(op.get('governance_metadata') and op.get('governance_metadata').controls for op in operations if op.get('governance_metadata') and op.get('governance_metadata').known_risks),
            "Approvals documented": all(op.get('governance_metadata') and op.get('governance_metadata').approvals for op in operations if op.get('governance_metadata')),
            "Regulatory compliance mapped": any(op.get('governance_metadata') and op.get('governance_metadata').regulatory_requirements for op in operations if op.get('governance_metadata')),
        }

        for check_name, passed in checks.items():
            icon = "[OK]" if passed else "[FAIL]"
            content.append(f"{icon} {check_name}")

        content.append("")
        content.append("---")
        content.append("")

        return content

    def _generate_attestation(
        self,
        report_id: str,
        report_date: datetime
    ) -> List[str]:
        """Generate attestation section."""
        content = []
        content.append("## Attestation")
        content.append("")

        content.append("**Report Prepared By**: compliance-team@company.com")
        content.append(f"**Date**: {report_date.strftime('%Y-%m-%d')}")
        content.append(f"**Report ID**: {report_id}")
        content.append("")

        content.append("**Attestation**:")
        content.append("This governance audit report accurately reflects the compliance posture ")
        content.append("as of the report date. All evidence cited in this report is available for ")
        content.append("review and has been verified for accuracy and completeness.")
        content.append("")
        content.append("---")
        content.append("")

        content.append("*Generated by PySpark StoryDoc Governance Framework v1.0*")

        return content
