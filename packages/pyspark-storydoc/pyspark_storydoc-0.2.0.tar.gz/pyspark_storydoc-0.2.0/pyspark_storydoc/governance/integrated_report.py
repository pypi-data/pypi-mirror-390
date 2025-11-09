"""
Integrated Governance Report Generator

Combines lineage diagrams with governance catalogs to create comprehensive,
stakeholder-ready documentation that tells the complete story:
- Technical lineage (what happens)
- Business justification (why it happens)
- Risk management (what could go wrong)
- Customer impact (who is affected)
- Compliance trail (who approved it)
"""

from pathlib import Path
from typing import Optional, Union

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.graph_builder import LineageGraph
from ..reporting import generate_business_diagram
from .comprehensive_catalog import ComprehensiveGovernanceCatalog


class IntegratedGovernanceReport:
    """
    Generate integrated governance reports combining:
    1. Executive Summary
    2. Lineage Diagram (visual data flow)
    3. Governance Catalog (detailed documentation)
    4. Cross-references between diagram and catalog
    """

    def __init__(self):
        """Initialize integrated report generator."""
        self.catalog_generator = ComprehensiveGovernanceCatalog()

    def generate_report(
        self,
        lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
        output_path: str,
        title: Optional[str] = None,
        include_diagram: bool = True,
        diagram_detail_level: str = "complete"
    ) -> str:
        """
        Generate integrated governance report.

        Args:
            lineage_graph: The lineage graph to document
            output_path: Path to save the report (markdown file)
            title: Optional custom title
            include_diagram: Whether to include lineage diagram
            diagram_detail_level: Detail level for diagram (complete, medium, high_level)

        Returns:
            Path to generated report
        """
        # Ensure output path ends with .md
        if not output_path.endswith('.md'):
            output_path = output_path + '.md'

        output_file = Path(output_path)
        output_dir = output_file.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate diagram if requested
        diagram_path = None
        if include_diagram:
            diagram_filename = output_file.stem + '_diagram.md'
            diagram_path = output_dir / diagram_filename
            generate_business_diagram(
                lineage_graph,
                str(diagram_path),
                detail_level=diagram_detail_level
            )

        # Build integrated report
        lines = []

        # Title and introduction
        lines.extend(self._generate_header(title or lineage_graph.name))
        lines.append("")

        # Executive Summary
        lines.extend(self._generate_executive_summary(lineage_graph))
        lines.append("")

        # Lineage Diagram section
        if include_diagram and diagram_path:
            lines.extend(self._generate_diagram_section(diagram_path))
            lines.append("")

        # Governance Legend
        lines.extend(self._generate_governance_legend())
        lines.append("")

        # Governance Catalog (embedded)
        lines.extend(self._generate_embedded_catalog(lineage_graph))
        lines.append("")

        # Footer
        lines.extend(self._generate_footer())
        lines.append("")

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_header(self, pipeline_name: str) -> list[str]:
        """Generate report header."""
        from datetime import datetime

        lines = []
        lines.append("---")
        lines.append("title: Governance Report")
        lines.append(f"pipeline: {pipeline_name}")
        lines.append(f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("type: governance-report")
        lines.append("---")
        lines.append("")
        lines.append(f"# [REPORT] Governance Report: {pipeline_name}")
        lines.append("")
        lines.append("> **Purpose:** Comprehensive governance documentation for data engineering, ")
        lines.append("> business stakeholders, and audit teams.")
        lines.append("")
        lines.append("---")

        return lines

    def _generate_executive_summary(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> list[str]:
        """Generate executive summary."""
        lines = []
        lines.append("## [TARGET] Executive Summary")
        lines.append("")

        # Extract governance entries
        entries = self.catalog_generator._extract_governance_data(lineage_graph)

        if not entries:
            lines.append("[WARN] **No governance metadata found in this pipeline.**")
            lines.append("")
            lines.append("Add governance metadata using the `@businessConcept` decorator with the `governance` parameter.")
            return lines

        total_ops = len(entries)
        with_justification = sum(1 for e in entries if e.business_justification)
        with_risks = sum(1 for e in entries if e.risks)
        direct_impact = sum(1 for e in entries if 'direct' in e.customer_impact_level.lower())
        pii_processing = sum(1 for e in entries if e.processes_pii)

        # Collect all risks
        all_risks = []
        for entry in entries:
            all_risks.extend(entry.risks)

        critical_risks = sum(1 for r in all_risks if self.catalog_generator._get_attr(r, 'severity', '').lower() == 'critical')
        high_risks = sum(1 for r in all_risks if self.catalog_generator._get_attr(r, 'severity', '').lower() == 'high')

        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| **Total Operations** | {total_ops} |")
        lines.append(f"| **Documented Justifications** | {with_justification}/{total_ops} ({with_justification/total_ops*100:.0f}%) |")
        lines.append(f"| **Risk Assessments** | {with_risks}/{total_ops} ({with_risks/total_ops*100:.0f}%) |")
        lines.append(f"| **Customer-Impacting Operations** | {direct_impact} |")
        lines.append(f"| **PII Processing Operations** | {pii_processing} |")
        lines.append(f"| **Critical Risks** | {critical_risks} |")
        lines.append(f"| **High Risks** | {high_risks} |")
        lines.append("")

        # Quick status indicators
        lines.append("### [CHART] Status Indicators")
        lines.append("")

        status_items = []

        if with_justification == total_ops:
            status_items.append("[OK] All operations have business justifications")
        elif with_justification > 0:
            status_items.append(f"[WARN] {total_ops - with_justification} operations missing business justifications")
        else:
            status_items.append(f"[FAIL] No business justifications documented")

        if critical_risks > 0:
            status_items.append(f"[RED] {critical_risks} CRITICAL risks require immediate attention")
        if high_risks > 0:
            status_items.append(f"[ORANGE] {high_risks} HIGH risks identified")

        if direct_impact > 0:
            status_items.append(f"[USERS] {direct_impact} operations directly impact customers")

        if pii_processing > 0:
            status_items.append(f"[LOCKED] {pii_processing} operations process PII")

        for item in status_items:
            lines.append(f"- {item}")

        lines.append("")

        return lines

    def _generate_diagram_section(self, diagram_path: Path) -> list[str]:
        """Generate diagram section with embedded diagram."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## [CHART] Data Lineage Diagram")
        lines.append("")
        lines.append("Visual representation of data flow through the pipeline. Operations are color-coded by type and governance status.")
        lines.append("")

        # Read and embed the diagram
        try:
            with open(diagram_path, 'r', encoding='utf-8') as f:
                diagram_content = f.read()

            # Extract just the mermaid diagram (skip the header)
            lines_in_file = diagram_content.split('\n')
            in_mermaid = False
            mermaid_lines = []

            for line in lines_in_file:
                if line.strip().startswith('```mermaid'):
                    in_mermaid = True
                    mermaid_lines.append(line)
                elif line.strip().startswith('```') and in_mermaid:
                    mermaid_lines.append(line)
                    break
                elif in_mermaid:
                    mermaid_lines.append(line)

            if mermaid_lines:
                lines.extend(mermaid_lines)
                lines.append("")
            else:
                lines.append(f"[Diagram generated at: {diagram_path}]")
                lines.append("")

        except Exception as e:
            lines.append(f"[WARN] Could not embed diagram: {e}")
            lines.append("")

        return lines

    def _generate_governance_legend(self) -> list[str]:
        """Generate legend explaining governance indicators."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## 🔑 Governance Legend")
        lines.append("")
        lines.append("### Risk Severity Levels")
        lines.append("")
        lines.append("| Symbol | Severity | Description |")
        lines.append("|--------|----------|-------------|")
        lines.append("| [RED] | **CRITICAL** | Business-threatening, requires immediate action |")
        lines.append("| [ORANGE] | **HIGH** | Significant impact, needs mitigation |")
        lines.append("| [YELLOW] | **MEDIUM** | Moderate impact, requires attention |")
        lines.append("| [GREEN] | **LOW** | Minimal impact, manageable |")
        lines.append("")
        lines.append("### Customer Impact Levels")
        lines.append("")
        lines.append("| Symbol | Level | Description |")
        lines.append("|--------|-------|-------------|")
        lines.append("| [RED] | **DIRECT** | Directly affects customer experience, pricing, or access |")
        lines.append("| [YELLOW] | **INDIRECT** | Influences but doesn't directly determine customer outcomes |")
        lines.append("| [GREEN] | **NONE** | Internal analytics, no customer-facing impact |")
        lines.append("")
        lines.append("### Data Classification")
        lines.append("")
        lines.append("| Symbol | Classification | Description |")
        lines.append("|--------|---------------|-------------|")
        lines.append("| [LOCKED] | **RESTRICTED** | Highest sensitivity (SSN, financial accounts, health records) |")
        lines.append("| 🔐 | **CONFIDENTIAL** | Customer PII (email, phone, address) |")
        lines.append("| [FOLDER] | **INTERNAL** | Business data, non-PII |")
        lines.append("| 🌐 | **PUBLIC** | Safe for external sharing |")
        lines.append("")

        return lines

    def _generate_embedded_catalog(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> list[str]:
        """Generate embedded governance catalog."""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## [BOOKS] Governance Catalog")
        lines.append("")
        lines.append("Detailed governance documentation for each operation.")
        lines.append("")

        # Get governance entries
        entries = self.catalog_generator._extract_governance_data(lineage_graph)

        if not entries:
            lines.append("[WARN] No governance data available.")
            return lines

        # Generate catalog sections
        lines.extend(self._generate_justifications_section(entries))
        lines.append("")
        lines.extend(self._generate_risks_section(entries))
        lines.append("")
        lines.extend(self._generate_customer_impact_section(entries))
        lines.append("")
        lines.extend(self._generate_pii_section(entries))
        lines.append("")
        lines.extend(self._generate_approvals_section(entries))
        lines.append("")

        return lines

    def _generate_justifications_section(self, entries) -> list[str]:
        """Generate business justifications section."""
        lines = []
        lines.append("### [IDEA] Business Justifications")
        lines.append("")

        justified_ops = [e for e in entries if e.business_justification]

        if not justified_ops:
            lines.append("_No business justifications documented._")
            return lines

        for i, entry in enumerate(justified_ops, 1):
            lines.append(f"#### {i}. {entry.operation_name}")
            lines.append("")
            lines.append(f"**WHY:** {entry.business_justification}")
            lines.append("")

            if entry.regulatory_requirement:
                lines.append(f"**REGULATORY:** {entry.regulatory_requirement}")
                lines.append("")

        return lines

    def _generate_risks_section(self, entries) -> list[str]:
        """Generate risks section."""
        lines = []
        lines.append("### [WARN] Risk Registry")
        lines.append("")

        # Collect all risks
        all_risks = []
        for entry in entries:
            for risk in entry.risks:
                all_risks.append({
                    'operation': entry.operation_name,
                    'risk': risk,
                    'mitigations': entry.mitigations,
                    'owner': entry.risk_owner
                })

        if not all_risks:
            lines.append("_No risks documented._")
            return lines

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_risks.sort(key=lambda x: severity_order.get(
            self.catalog_generator._get_attr(x['risk'], 'severity', '').lower(), 4
        ))

        for i, item in enumerate(all_risks, 1):
            risk = item['risk']
            severity = self.catalog_generator._get_attr(risk, 'severity', 'unknown').upper()
            risk_id = self.catalog_generator._get_attr(risk, 'risk_id', f'R{i:03d}')
            description = self.catalog_generator._get_attr(risk, 'description', 'No description')
            category = self.catalog_generator._get_attr(risk, 'category', 'general')

            emoji = "[RED]" if severity == "CRITICAL" else "[ORANGE]" if severity == "HIGH" else "[YELLOW]" if severity == "MEDIUM" else "[GREEN]"

            lines.append(f"#### {emoji} [{risk_id}] {description}")
            lines.append("")
            lines.append(f"- **Operation:** {item['operation']}")
            lines.append(f"- **Severity:** {severity}")
            lines.append(f"- **Category:** {category}")

            # Find mitigation
            mitigation = self.catalog_generator._find_mitigation(item['mitigations'], risk_id)
            if mitigation:
                mitigation_text = self.catalog_generator._get_attr(mitigation, 'mitigation', 'No mitigation')
                status = self.catalog_generator._get_attr(mitigation, 'status', 'unknown')
                effectiveness = self.catalog_generator._get_attr(mitigation, 'effectiveness', 'unknown')

                lines.append(f"- **Mitigation:** {mitigation_text}")
                lines.append(f"- **Status:** {status} | **Effectiveness:** {effectiveness}")
            else:
                lines.append(f"- **Mitigation:** [WARN] NO MITIGATION DOCUMENTED")

            if item['owner']:
                lines.append(f"- **Owner:** {item['owner']}")

            lines.append("")

        return lines

    def _generate_customer_impact_section(self, entries) -> list[str]:
        """Generate customer impact section."""
        lines = []
        lines.append("### [USERS] Customer Impact")
        lines.append("")

        direct_impact = [e for e in entries if 'direct' in e.customer_impact_level.lower()]
        indirect_impact = [e for e in entries if 'indirect' in e.customer_impact_level.lower()]

        if not direct_impact and not indirect_impact:
            lines.append("_No customer-impacting operations identified._")
            return lines

        if direct_impact:
            lines.append("#### [RED] DIRECT Customer Impact")
            lines.append("")

            for entry in direct_impact:
                lines.append(f"**{entry.operation_name}**")
                if entry.impact_description:
                    lines.append(f"- {entry.impact_description}")
                if entry.impacting_columns:
                    lines.append(f"- Impacting Columns: `{', '.join(entry.impacting_columns)}`")
                lines.append("")

        if indirect_impact:
            lines.append("#### [YELLOW] INDIRECT Customer Impact")
            lines.append("")

            for entry in indirect_impact:
                lines.append(f"**{entry.operation_name}**")
                if entry.impact_description:
                    lines.append(f"- {entry.impact_description}")
                lines.append("")

        return lines

    def _generate_pii_section(self, entries) -> list[str]:
        """Generate PII section."""
        lines = []
        lines.append("### [LOCKED] PII & Data Classification")
        lines.append("")

        pii_ops = [e for e in entries if e.processes_pii]

        if not pii_ops:
            lines.append("_No PII processing operations identified._")
            return lines

        for entry in pii_ops:
            classification = entry.data_classification.upper() if entry.data_classification else 'UNCLASSIFIED'
            emoji = "[LOCKED]" if classification == "RESTRICTED" else "🔐" if classification == "CONFIDENTIAL" else "[FOLDER]" if classification == "INTERNAL" else "🌐" if classification == "PUBLIC" else "[WARN]"

            lines.append(f"**{emoji} {entry.operation_name}** ({classification})")
            if entry.pii_columns:
                lines.append(f"- PII Columns: `{', '.join(entry.pii_columns)}`")
            lines.append("")

        return lines

    def _generate_approvals_section(self, entries) -> list[str]:
        """Generate approvals section."""
        lines = []
        lines.append("### [OK] Approval Trail")
        lines.append("")

        approved = [e for e in entries if e.approval_status and 'approved' in e.approval_status.lower()]

        if not approved:
            lines.append("_No approvals recorded._")
            return lines

        for entry in approved:
            lines.append(f"**{entry.operation_name}**")
            if entry.approved_by:
                lines.append(f"- Approved By: {entry.approved_by}")
            if entry.approval_date:
                lines.append(f"- Date: {entry.approval_date}")
            lines.append("")

        return lines

    def _generate_footer(self) -> list[str]:
        """Generate report footer."""
        from datetime import datetime

        lines = []
        lines.append("---")
        lines.append("")
        lines.append("## [FILE] Report Information")
        lines.append("")
        lines.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("- **Tool:** PySpark StoryDoc Governance Framework")
        lines.append("- **Purpose:** Audit, Compliance, and Stakeholder Communication")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("_For questions or to report governance issues, consult your governance team._")

        return lines


# Convenience function
def generate_integrated_governance_report(
    lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
    output_path: str,
    title: Optional[str] = None,
    include_diagram: bool = True
) -> str:
    """
    Generate integrated governance report combining diagram and catalog.

    Args:
        lineage_graph: The lineage graph to document
        output_path: Path to save the report (markdown file)
        title: Optional custom title
        include_diagram: Whether to include lineage diagram

    Returns:
        Path to generated report
    """
    report_gen = IntegratedGovernanceReport()
    return report_gen.generate_report(
        lineage_graph,
        output_path,
        title=title,
        include_diagram=include_diagram
    )
