"""Governance reporting and documentation generation."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.graph_builder import BusinessConceptNode, LineageGraph
from .bias_detection import BiasAnalysisResult, BiasDetectionEngine
from .customer_impact import CustomerImpactAnalysis, CustomerImpactDetector
from .metadata import ApprovalStatus, CustomerImpactLevel, GovernanceMetadata
from .risk_assessment import DetectedRisk, RiskAssessmentEngine
from .validation import GovernanceValidator, ValidationResult


class GovernanceReportGenerator:
    """
    Generate governance reports for pipelines and business concepts.

    Supports both LineageGraph and EnhancedLineageGraph.
    """

    def __init__(self):
        """Initialize report generator."""
        self.risk_engine = RiskAssessmentEngine()
        self.impact_detector = CustomerImpactDetector()
        self.bias_engine = BiasDetectionEngine()
        self.validator = GovernanceValidator()

    def _extract_business_concepts(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[Any]:
        """
        Extract business concepts from either LineageGraph or EnhancedLineageGraph.

        Args:
            lineage_graph: Either a LineageGraph or EnhancedLineageGraph

        Returns:
            List of business concept nodes
        """
        if isinstance(lineage_graph, LineageGraph):
            # Use the built-in method for LineageGraph
            return lineage_graph.get_business_concepts()
        elif isinstance(lineage_graph, EnhancedLineageGraph):
            # Extract from EnhancedLineageGraph nodes
            # Business concepts are nodes with 'business_context' in metadata
            concepts = []
            for node in lineage_graph.nodes.values():
                if 'business_context' in node.metadata:
                    # Create a pseudo-concept object that has the attributes we need
                    concept = type('BusinessConcept', (), {})()
                    concept.name = node.metadata.get('operation_name', node.name)
                    concept.node_id = node.node_id
                    concept.metadata = node.metadata
                    concept.governance_metadata = node.metadata.get('governance_metadata')
                    concepts.append(concept)
            return concepts
        else:
            # Fallback: empty list
            return []

    def generate_pipeline_report(
        self,
        lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
        output_path: str,
        include_technical_details: bool = False
    ) -> str:
        """
        Generate comprehensive governance report for entire pipeline.

        Args:
            lineage_graph: The lineage graph
            output_path: Path to save the report
            include_technical_details: Include technical implementation details

        Returns:
            Path to generated report
        """
        report_lines = []

        # Header
        report_lines.append("# Governance Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Pipeline:** {lineage_graph.name}")
        report_lines.append("")

        # Executive Summary
        report_lines.extend(self._generate_executive_summary(lineage_graph))
        report_lines.append("")

        # Business Justification
        report_lines.extend(self._generate_justification_section(lineage_graph))
        report_lines.append("")

        # Risk Assessment
        report_lines.extend(self._generate_risk_section(lineage_graph))
        report_lines.append("")

        # Customer Impact Analysis
        report_lines.extend(self._generate_impact_section(lineage_graph))
        report_lines.append("")

        # Bias Analysis
        report_lines.extend(self._generate_bias_section(lineage_graph))
        report_lines.append("")

        # Data Classification
        report_lines.extend(self._generate_classification_section(lineage_graph))
        report_lines.append("")

        # Compliance Checklist
        report_lines.extend(self._generate_compliance_checklist(lineage_graph))
        report_lines.append("")

        # Approval Trail
        report_lines.extend(self._generate_approval_section(lineage_graph))
        report_lines.append("")

        # Audit Recommendations
        report_lines.extend(self._generate_audit_recommendations(lineage_graph))
        report_lines.append("")

        # Technical Details (optional)
        if include_technical_details:
            report_lines.extend(self._generate_technical_details(lineage_graph))
            report_lines.append("")

        # Write report
        report_content = "\n".join(report_lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return output_path

    def _generate_executive_summary(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate executive summary section."""
        lines = ["## Executive Summary"]
        lines.append("")

        # Get business concepts
        concepts = self._extract_business_concepts(lineage_graph)
        total_concepts = len(concepts)

        # Count concepts with governance
        governed_concepts = sum(
            1 for c in concepts
            if hasattr(c, 'governance_metadata') and c.governance_metadata
        )

        # Detect overall risks
        all_risks = []
        for concept in concepts:
            risks = self.risk_engine.analyze_concept(concept)
            all_risks.extend(risks)

        risk_summary = self.risk_engine.generate_risk_summary(all_risks)

        # Detect customer impact
        impact_analysis = self.impact_detector.detect_impact(lineage_graph)

        lines.append(f"- **Total Operations:** {total_concepts}")
        lines.append(f"- **Governed Operations:** {governed_concepts} ({governed_concepts/total_concepts*100:.0f}%)")
        lines.append(f"- **Customer-Impacting Operations:** {len(impact_analysis.impacting_concepts)}")
        lines.append(f"- **Identified Risks:** {risk_summary['total_risks']} (Critical: {risk_summary['by_severity']['critical']}, High: {risk_summary['by_severity']['high']})")
        lines.append(f"- **Pipeline Impact Level:** {impact_analysis.impact_level.upper()}")

        return lines

    def _generate_justification_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate business justification section."""
        lines = ["## Business Justification"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        # Look for pipeline-level justification
        pipeline_justification = None
        for concept in concepts:
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                if concept.governance_metadata.business_justification:
                    pipeline_justification = concept.governance_metadata.business_justification
                    break

        if pipeline_justification:
            lines.append(f"**Pipeline Purpose:** {pipeline_justification}")
            lines.append("")

        # List operation justifications
        lines.append("### Operation Justifications")
        lines.append("")

        justified = 0
        for concept in concepts:
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                if concept.governance_metadata.business_justification:
                    justified += 1
                    lines.append(f"**{concept.name}:**")
                    lines.append(f"{concept.governance_metadata.business_justification}")
                    if concept.governance_metadata.regulatory_requirement:
                        lines.append(f"*Regulatory Requirement:* {concept.governance_metadata.regulatory_requirement}")
                    lines.append("")

        if justified == 0:
            lines.append("[!] No business justifications documented.")
            lines.append("")

        return lines

    def _generate_risk_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate risk assessment section."""
        lines = ["## Risk Assessment"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        # Collect all risks (both declared and inferred)
        all_risks = {}  # concept_id -> risks

        for concept in concepts:
            concept_risks = []

            # Get declared risks
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                if concept.governance_metadata.known_risks:
                    concept_risks.extend([
                        {
                            "source": "declared",
                            "risk": risk
                        }
                        for risk in concept.governance_metadata.known_risks
                    ])

            # Get inferred risks
            detected_risks = self.risk_engine.analyze_concept(concept)
            concept_risks.extend([
                {
                    "source": "detected",
                    "risk": risk
                }
                for risk in detected_risks
            ])

            if concept_risks:
                all_risks[concept.node_id] = {
                    "concept_name": concept.name,
                    "risks": concept_risks
                }

        if not all_risks:
            lines.append("[OK] No risks identified.")
            lines.append("")
            return lines

        # Group by severity
        critical_risks = []
        high_risks = []
        medium_risks = []

        for concept_id, data in all_risks.items():
            for risk_info in data["risks"]:
                risk = risk_info["risk"]
                severity = risk.severity if hasattr(risk, 'severity') else risk.get('severity', 'medium')
                entry = {
                    "concept": data["concept_name"],
                    "risk": risk,
                    "source": risk_info["source"]
                }

                if severity in ["critical", "CRITICAL"]:
                    critical_risks.append(entry)
                elif severity in ["high", "HIGH"]:
                    high_risks.append(entry)
                else:
                    medium_risks.append(entry)

        # Report critical risks
        if critical_risks:
            lines.append("### [RED] CRITICAL Risks")
            lines.append("")
            for entry in critical_risks:
                risk = entry["risk"]
                if hasattr(risk, 'description'):
                    lines.append(f"**{entry['concept']}:** {risk.description}")
                    if hasattr(risk, 'recommended_mitigation'):
                        lines.append(f"*Mitigation:* {risk.recommended_mitigation}")
                else:
                    lines.append(f"**{entry['concept']}:** {risk.description}")
                lines.append("")

        # Report high risks
        if high_risks:
            lines.append("### [!] HIGH Risks")
            lines.append("")
            for entry in high_risks:
                risk = entry["risk"]
                if hasattr(risk, 'description'):
                    lines.append(f"**{entry['concept']}:** {risk.description}")
                else:
                    lines.append(f"**{entry['concept']}:** {risk.description}")
                lines.append("")

        return lines

    def _generate_impact_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate customer impact section."""
        lines = ["## Customer Impact Analysis"]
        lines.append("")

        impact_analysis = self.impact_detector.detect_impact(lineage_graph)

        lines.append(f"**Overall Impact Level:** {impact_analysis.impact_level.upper()}")
        lines.append(f"**Confidence:** {impact_analysis.confidence:.0%}")
        lines.append("")

        if impact_analysis.impacting_columns:
            lines.append("### Impacting Columns")
            lines.append("")
            for col in impact_analysis.impacting_columns:
                lines.append(f"- **{col.column_name}** ({col.impact_type.value})")
                lines.append(f"  - Operation: {col.node_name}")
                lines.append(f"  - Confidence: {col.confidence:.0%}")
            lines.append("")

        if impact_analysis.recommendations:
            lines.append("### Recommendations")
            lines.append("")
            for rec in impact_analysis.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return lines

    def _generate_bias_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate bias analysis section."""
        lines = ["## Bias & Fairness Analysis"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        # Analyze each concept
        bias_concerns = []
        for concept in concepts:
            analysis = self.bias_engine.analyze_for_bias(concept)
            if analysis.issues:
                bias_concerns.append({
                    "concept": concept.name,
                    "analysis": analysis
                })

        if not bias_concerns:
            lines.append("[OK] No bias concerns detected.")
            lines.append("")
            return lines

        # Report concerns
        for concern in bias_concerns:
            lines.append(f"### {concern['concept']}")
            lines.append("")
            analysis = concern["analysis"]
            lines.append(f"**Risk Level:** {analysis.risk_level.upper()}")
            lines.append(f"**Risk Score:** {analysis.risk_score:.2f}")
            lines.append("")

            for issue in analysis.issues:
                lines.append(f"**{issue.category.value}** ({issue.severity})")
                lines.append(f"{issue.description}")
                lines.append(f"*Recommendation:* {issue.recommendation}")
                lines.append("")

        return lines

    def _generate_classification_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate data classification section."""
        lines = ["## Data Classification"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        # Check for PII processing
        pii_concepts = []
        for concept in concepts:
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                if concept.governance_metadata.processes_pii:
                    pii_concepts.append(concept)

        if pii_concepts:
            lines.append("### PII Processing")
            lines.append("")
            for concept in pii_concepts:
                lines.append(f"**{concept.name}:**")
                if concept.governance_metadata.pii_columns:
                    lines.append(f"- PII Columns: {', '.join(concept.governance_metadata.pii_columns)}")
                if concept.governance_metadata.data_classification:
                    lines.append(f"- Classification: {concept.governance_metadata.data_classification.value}")
                if concept.governance_metadata.data_retention_days:
                    lines.append(f"- Retention: {concept.governance_metadata.data_retention_days} days")
                lines.append("")

        return lines

    def _generate_compliance_checklist(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate compliance checklist."""
        lines = ["## Compliance Checklist"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        # Check various compliance requirements
        checks = {
            "Business justification documented": 0,
            "Risks have mitigations": 0,
            "Customer impact disclosed": 0,
            "PII handling documented": 0,
            "Approvals obtained": 0,
            "Review schedule established": 0,
        }

        for concept in concepts:
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                gov = concept.governance_metadata

                if gov.business_justification:
                    checks["Business justification documented"] += 1

                if gov.known_risks and gov.risk_mitigations:
                    checks["Risks have mitigations"] += 1

                if gov.customer_impact_level:
                    checks["Customer impact disclosed"] += 1

                if gov.processes_pii and gov.pii_columns and gov.data_classification:
                    checks["PII handling documented"] += 1

                if gov.requires_approval and gov.approval_status == ApprovalStatus.APPROVED:
                    checks["Approvals obtained"] += 1

                if gov.next_review_date:
                    checks["Review schedule established"] += 1

        # Report checklist
        for check, count in checks.items():
            status = "[OK]" if count == len(concepts) else "[!]" if count > 0 else "[X]"
            lines.append(f"{status} {check}: {count}/{len(concepts)}")

        lines.append("")
        return lines

    def _generate_approval_section(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate approval trail section."""
        lines = ["## Approval Trail"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        approved = []
        for concept in concepts:
            if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                if concept.governance_metadata.approval_status == ApprovalStatus.APPROVED:
                    approved.append(concept)

        if not approved:
            lines.append("[INFO] No approvals recorded.")
            lines.append("")
            return lines

        for concept in approved:
            gov = concept.governance_metadata
            lines.append(f"**{concept.name}:**")
            if gov.approved_by:
                lines.append(f"- Approved By: {gov.approved_by}")
            if gov.approval_date:
                lines.append(f"- Date: {gov.approval_date.strftime('%Y-%m-%d')}")
            if gov.approval_reference:
                lines.append(f"- Reference: {gov.approval_reference}")
            lines.append("")

        return lines

    def _generate_audit_recommendations(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate audit recommendations."""
        lines = ["## Audit Recommendations"]
        lines.append("")

        # Run validation on all concepts
        concepts = self._extract_business_concepts(lineage_graph)
        validation_issues = []

        for concept in concepts:
            result = self.validator.validate_concept_node(concept)
            if not result.is_valid:
                validation_issues.append({
                    "concept": concept.name,
                    "result": result
                })

        if not validation_issues:
            lines.append("[OK] All governance requirements met.")
            lines.append("")
            return lines

        lines.append("### Issues Requiring Attention")
        lines.append("")

        for issue_data in validation_issues:
            lines.append(f"**{issue_data['concept']}:**")
            result = issue_data['result']
            for issue in result.issues:
                lines.append(f"- [{issue.severity.value.upper()}] {issue.message}")
            lines.append("")

        return lines

    def _generate_technical_details(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[str]:
        """Generate technical implementation details."""
        lines = ["## Technical Details"]
        lines.append("")

        concepts = self._extract_business_concepts(lineage_graph)

        for concept in concepts:
            lines.append(f"### {concept.name}")
            lines.append("")

            # Operation types
            if concept.technical_operations:
                op_types = [op.operation_type.value for op in concept.technical_operations]
                lines.append(f"**Operations:** {', '.join(op_types)}")

            # Metrics
            if concept.input_metrics and concept.output_metrics:
                lines.append(f"**Input Records:** {concept.input_metrics.row_count:,}")
                lines.append(f"**Output Records:** {concept.output_metrics.row_count:,}")

            lines.append("")

        return lines
