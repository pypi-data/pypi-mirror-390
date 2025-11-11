"""
Comprehensive Governance Catalog Generator

Generates detailed, well-organized governance catalogs with:
- Executive dashboard with metrics
- Business justifications catalog
- Risk registry with all risks and mitigations
- Customer impact registry
- PII and data classification registry
- Approval trail
- Recommendations and next steps
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.graph_builder import LineageGraph
from .metadata import (
    ApprovalStatus,
    CustomerImpactLevel,
    DataClassification,
    GovernanceMetadata,
)


@dataclass
class GovernanceCatalogEntry:
    """Single entry in governance catalog."""
    operation_name: str
    node_id: str
    business_justification: Optional[str] = None
    regulatory_requirement: Optional[str] = None
    risks: List[Dict[str, Any]] = None
    mitigations: List[Dict[str, Any]] = None
    customer_impact_level: Optional[str] = None
    impacting_columns: List[str] = None
    impact_description: Optional[str] = None
    processes_pii: bool = False
    pii_columns: List[str] = None
    data_classification: Optional[str] = None
    risk_owner: Optional[str] = None
    approval_status: Optional[str] = None
    approved_by: Optional[str] = None
    approval_date: Optional[str] = None

    def __post_init__(self):
        if self.risks is None:
            self.risks = []
        if self.mitigations is None:
            self.mitigations = []
        if self.impacting_columns is None:
            self.impacting_columns = []
        if self.pii_columns is None:
            self.pii_columns = []


class ComprehensiveGovernanceCatalog:
    """
    Generate comprehensive governance catalogs with multiple views:
    - Executive Dashboard
    - Business Justifications Catalog
    - Risk Registry
    - Customer Impact Registry
    - PII & Data Classification Registry
    - Approval Trail
    """

    def __init__(self):
        """Initialize catalog generator."""
        pass

    def _extract_governance_data(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[GovernanceCatalogEntry]:
        """
        Extract all governance data from lineage graph.

        Args:
            lineage_graph: The lineage graph to process

        Returns:
            List of governance catalog entries
        """
        entries = []

        if isinstance(lineage_graph, EnhancedLineageGraph):
            # Extract from EnhancedLineageGraph
            # Business concepts are nodes with 'business_context' in metadata
            for node in lineage_graph.nodes.values():
                if 'business_context' in node.metadata:
                    gov_meta = node.metadata.get('governance_metadata')
                    if gov_meta:
                        entry = self._create_entry_from_governance(
                            operation_name=node.metadata.get('operation_name', node.name),
                            node_id=node.node_id,
                            governance=gov_meta
                        )
                        entries.append(entry)

        elif isinstance(lineage_graph, LineageGraph):
            # Extract from LineageGraph
            for concept in lineage_graph.get_business_concepts():
                if hasattr(concept, 'governance_metadata') and concept.governance_metadata:
                    entry = self._create_entry_from_governance(
                        operation_name=concept.name,
                        node_id=concept.node_id,
                        governance=concept.governance_metadata
                    )
                    entries.append(entry)

        return entries

    def _create_entry_from_governance(
        self,
        operation_name: str,
        node_id: str,
        governance: GovernanceMetadata
    ) -> GovernanceCatalogEntry:
        """Create catalog entry from governance metadata."""
        return GovernanceCatalogEntry(
            operation_name=operation_name,
            node_id=node_id,
            business_justification=getattr(governance, 'business_justification', None),
            regulatory_requirement=getattr(governance, 'regulatory_requirement', None),
            risks=getattr(governance, 'known_risks', []) or [],
            mitigations=getattr(governance, 'risk_mitigations', []) or [],
            customer_impact_level=str(getattr(governance, 'customer_impact_level', '')),
            impacting_columns=getattr(governance, 'impacting_columns', []) or [],
            impact_description=getattr(governance, 'impact_description', None),
            processes_pii=getattr(governance, 'processes_pii', False),
            pii_columns=getattr(governance, 'pii_columns', []) or [],
            data_classification=str(getattr(governance, 'data_classification', '')),
            risk_owner=getattr(governance, 'risk_owner', None),
            approval_status=str(getattr(governance, 'approval_status', '')),
            approved_by=getattr(governance, 'approved_by', None),
            approval_date=self._format_date(getattr(governance, 'approval_date', None))
        )

    def _format_date(self, date_value: Any) -> Optional[str]:
        """Format date value to string."""
        if date_value is None:
            return None
        if isinstance(date_value, str):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        return str(date_value)

    def generate_catalog(
        self,
        lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
        output_path: str,
        title: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive governance catalog.

        Args:
            lineage_graph: The lineage graph to document
            output_path: Path to save the catalog
            title: Optional custom title

        Returns:
            Path to generated catalog
        """
        entries = self._extract_governance_data(lineage_graph)

        lines = []

        # Header
        lines.extend(self._generate_header(title or lineage_graph.name))
        lines.append("")

        if not entries:
            lines.append("═" * 100)
            lines.append("[WARN]  NO GOVERNANCE DATA FOUND")
            lines.append("═" * 100)
            lines.append("")
            lines.append("This pipeline does not contain governance metadata.")
            lines.append("Add governance metadata using @businessConcept decorator with governance parameter.")
            lines.append("")
        else:
            # Executive Dashboard
            lines.extend(self._generate_executive_dashboard(entries))
            lines.append("")

            # Business Justifications Catalog
            lines.extend(self._generate_justifications_catalog(entries))
            lines.append("")

            # Risk Registry
            lines.extend(self._generate_risk_registry(entries))
            lines.append("")

            # Customer Impact Registry
            lines.extend(self._generate_customer_impact_registry(entries))
            lines.append("")

            # PII & Data Classification Registry
            lines.extend(self._generate_pii_registry(entries))
            lines.append("")

            # Approval Trail
            lines.extend(self._generate_approval_trail(entries))
            lines.append("")

            # Recommendations
            lines.extend(self._generate_recommendations(entries))
            lines.append("")

        # Footer
        lines.extend(self._generate_footer())

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_header(self, pipeline_name: str) -> List[str]:
        """Generate catalog header."""
        lines = []
        lines.append("═" * 100)
        lines.append("                        GOVERNANCE CATALOG")
        lines.append("═" * 100)
        lines.append("")
        lines.append(f"Pipeline: {pipeline_name}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Purpose: Comprehensive governance documentation for audit, compliance, and stakeholder review")
        lines.append("")
        return lines

    def _generate_executive_dashboard(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate executive dashboard with key metrics."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 1: EXECUTIVE DASHBOARD")
        lines.append("═" * 100)
        lines.append("")

        total_ops = len(entries)

        # Coverage metrics
        with_justification = sum(1 for e in entries if e.business_justification)
        with_risks = sum(1 for e in entries if e.risks)
        with_mitigations = sum(1 for e in entries if e.mitigations)

        # Customer impact
        direct_impact = sum(1 for e in entries if 'direct' in e.customer_impact_level.lower())
        indirect_impact = sum(1 for e in entries if 'indirect' in e.customer_impact_level.lower())
        no_impact = sum(1 for e in entries if 'none' in e.customer_impact_level.lower() or not e.customer_impact_level)

        # Risk summary
        risk_counts = defaultdict(int)
        all_risks = []
        for entry in entries:
            for risk in entry.risks:
                severity = self._get_attr(risk, 'severity', 'unknown').lower()
                risk_counts[severity] += 1
                all_risks.append(risk)

        # Approval status
        approved = sum(1 for e in entries if 'approved' in e.approval_status.lower())
        pending = sum(1 for e in entries if 'pending' in e.approval_status.lower())

        # PII processing
        pii_processing = sum(1 for e in entries if e.processes_pii)

        # Dashboard
        lines.append("┌─────────────────────────────────────────────────────────────────────────────────────────────────┐")
        lines.append("│                                  GOVERNANCE OVERVIEW                                            │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────────────────────────┤")
        lines.append(f"│  Total Governed Operations:  {total_ops:3d}                                                             │")
        lines.append("│                                                                                                 │")
        lines.append("│  DOCUMENTATION COVERAGE:                                                                        │")
        lines.append(f"│    - Business Justification:    {with_justification:3d}/{total_ops:3d}  ({self._pct(with_justification, total_ops):3.0f}%)                                                    │")
        lines.append(f"│    - Risk Assessment:           {with_risks:3d}/{total_ops:3d}  ({self._pct(with_risks, total_ops):3.0f}%)                                                    │")
        lines.append(f"│    - Risk Mitigations:          {with_mitigations:3d}/{total_ops:3d}  ({self._pct(with_mitigations, total_ops):3.0f}%)                                                    │")
        lines.append("│                                                                                                 │")
        lines.append("│  CUSTOMER IMPACT:                                                                               │")
        lines.append(f"│    - DIRECT Impact:             {direct_impact:3d}  operations                                                      │")
        lines.append(f"│    - INDIRECT Impact:           {indirect_impact:3d}  operations                                                      │")
        lines.append(f"│    - NO Impact:                 {no_impact:3d}  operations                                                      │")
        lines.append("│                                                                                                 │")
        lines.append("│  RISK SUMMARY:                                                                                  │")
        lines.append(f"│    - CRITICAL Risks:            {risk_counts['critical']:3d}                                                            │")
        lines.append(f"│    - HIGH Risks:                {risk_counts['high']:3d}                                                            │")
        lines.append(f"│    - MEDIUM Risks:              {risk_counts['medium']:3d}                                                            │")
        lines.append(f"│    - LOW Risks:                 {risk_counts['low']:3d}                                                            │")
        lines.append(f"│    - Total Risks:               {len(all_risks):3d}                                                            │")
        lines.append("│                                                                                                 │")
        lines.append("│  APPROVAL STATUS:                                                                               │")
        lines.append(f"│    - Approved:                  {approved:3d}/{total_ops:3d}                                                            │")
        lines.append(f"│    - Pending Approval:          {pending:3d}/{total_ops:3d}                                                            │")
        lines.append("│                                                                                                 │")
        lines.append("│  DATA CLASSIFICATION:                                                                           │")
        lines.append(f"│    - Processing PII:            {pii_processing:3d}  operations                                                      │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────────────────────────┘")

        return lines

    def _generate_justifications_catalog(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate business justifications catalog."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 2: BUSINESS JUSTIFICATIONS CATALOG")
        lines.append("═" * 100)
        lines.append("")
        lines.append("This section documents WHY each operation exists and what business value it provides.")
        lines.append("")

        justified_ops = [e for e in entries if e.business_justification]

        if not justified_ops:
            lines.append("[!] No business justifications documented.")
            lines.append("")
            return lines

        for i, entry in enumerate(justified_ops, 1):
            lines.append(f"[{i}] {entry.operation_name}")
            lines.append("─" * 100)
            lines.append("")
            lines.append(f"BUSINESS JUSTIFICATION:")
            lines.append(f"  {self._wrap_text(entry.business_justification, 96, '  ')}")
            lines.append("")

            if entry.regulatory_requirement:
                lines.append(f"REGULATORY REQUIREMENT:")
                lines.append(f"  {self._wrap_text(entry.regulatory_requirement, 96, '  ')}")
                lines.append("")

            if entry.risk_owner:
                lines.append(f"OWNER: {entry.risk_owner}")
                lines.append("")

            lines.append("")

        return lines

    def _generate_risk_registry(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate comprehensive risk registry."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 3: RISK REGISTRY")
        lines.append("═" * 100)
        lines.append("")
        lines.append("Comprehensive catalog of all identified risks, their severity, and mitigation strategies.")
        lines.append("")

        # Collect all risks across operations
        risk_data = []
        for entry in entries:
            for risk in entry.risks:
                risk_data.append({
                    'operation': entry.operation_name,
                    'risk': risk,
                    'entry': entry
                })

        if not risk_data:
            lines.append("[OK] No risks documented (or all operations are low-risk).")
            lines.append("")
            return lines

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        risk_data.sort(key=lambda x: severity_order.get(
            self._get_attr(x['risk'], 'severity', 'unknown').lower(), 4
        ))

        current_severity = None
        risk_num = 1

        for item in risk_data:
            risk = item['risk']
            operation = item['operation']
            entry = item['entry']

            severity = self._get_attr(risk, 'severity', 'unknown').upper()
            risk_id = self._get_attr(risk, 'risk_id', f'R{risk_num:03d}')
            category = self._get_attr(risk, 'category', 'general')
            description = self._get_attr(risk, 'description', 'No description provided')
            likelihood = self._get_attr(risk, 'likelihood', None)
            impact = self._get_attr(risk, 'impact', None)

            # Section header for each severity level
            if severity != current_severity:
                if current_severity is not None:
                    lines.append("")
                lines.append(f"{'[RED] CRITICAL' if severity == 'CRITICAL' else '[ORANGE] HIGH' if severity == 'HIGH' else '[YELLOW] MEDIUM' if severity == 'MEDIUM' else '[GREEN] LOW' if severity == 'LOW' else '[WHITE] UNKNOWN'} RISKS")
                lines.append("─" * 100)
                lines.append("")
                current_severity = severity

            lines.append(f"[{risk_id}] {description}")
            lines.append(f"  Operation:   {operation}")
            lines.append(f"  Category:    {category}")
            lines.append(f"  Severity:    {severity}")
            if likelihood:
                lines.append(f"  Likelihood:  {likelihood}")
            if impact:
                lines.append(f"  Impact:      {impact}")

            # Find mitigation for this risk
            mitigation = self._find_mitigation(entry.mitigations, risk_id)
            if mitigation:
                mitigation_text = self._get_attr(mitigation, 'mitigation', 'No mitigation specified')
                status = self._get_attr(mitigation, 'status', 'unknown')
                effectiveness = self._get_attr(mitigation, 'effectiveness', 'unknown')

                lines.append(f"  Mitigation:  {self._wrap_text(mitigation_text, 88, '               ')}")
                lines.append(f"  Status:      {status}  |  Effectiveness: {effectiveness}")
            else:
                lines.append(f"  Mitigation:  [WARN]  NO MITIGATION DOCUMENTED")

            if entry.risk_owner:
                lines.append(f"  Owner:       {entry.risk_owner}")

            lines.append("")
            risk_num += 1

        return lines

    def _generate_customer_impact_registry(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate customer impact registry."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 4: CUSTOMER IMPACT REGISTRY")
        lines.append("═" * 100)
        lines.append("")
        lines.append("Operations that directly or indirectly affect customers.")
        lines.append("")

        # Separate by impact level
        direct_impact = [e for e in entries if 'direct' in e.customer_impact_level.lower()]
        indirect_impact = [e for e in entries if 'indirect' in e.customer_impact_level.lower()]

        if not direct_impact and not indirect_impact:
            lines.append("[OK] No customer-impacting operations identified.")
            lines.append("")
            return lines

        # Direct impact operations
        if direct_impact:
            lines.append("[RED] DIRECT CUSTOMER IMPACT")
            lines.append("─" * 100)
            lines.append("")
            lines.append("These operations directly affect customer experience, pricing, access, or service levels.")
            lines.append("")

            for i, entry in enumerate(direct_impact, 1):
                lines.append(f"[{i}] {entry.operation_name}")
                lines.append("")

                if entry.impact_description:
                    lines.append(f"  HOW IT IMPACTS CUSTOMERS:")
                    lines.append(f"    {self._wrap_text(entry.impact_description, 92, '    ')}")
                    lines.append("")

                if entry.impacting_columns:
                    lines.append(f"  IMPACTING COLUMNS: {', '.join(entry.impacting_columns)}")
                    lines.append("")

                if entry.approval_status and 'approved' in entry.approval_status.lower():
                    lines.append(f"  [OK] APPROVED by {entry.approved_by or 'governance team'}")
                elif entry.approval_status and 'pending' in entry.approval_status.lower():
                    lines.append(f"  [WARN]  PENDING APPROVAL - NOT APPROVED FOR PRODUCTION")

                lines.append("")

            lines.append("")

        # Indirect impact operations
        if indirect_impact:
            lines.append("[YELLOW] INDIRECT CUSTOMER IMPACT")
            lines.append("─" * 100)
            lines.append("")
            lines.append("These operations influence customer outcomes but don't directly determine them.")
            lines.append("")

            for i, entry in enumerate(indirect_impact, 1):
                lines.append(f"[{i}] {entry.operation_name}")
                lines.append("")

                if entry.impact_description:
                    lines.append(f"  HOW IT INFLUENCES CUSTOMERS:")
                    lines.append(f"    {self._wrap_text(entry.impact_description, 92, '    ')}")
                    lines.append("")

                if entry.impacting_columns:
                    lines.append(f"  RELATED COLUMNS: {', '.join(entry.impacting_columns)}")

                lines.append("")

            lines.append("")

        return lines

    def _generate_pii_registry(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate PII and data classification registry."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 5: PII & DATA CLASSIFICATION REGISTRY")
        lines.append("═" * 100)
        lines.append("")
        lines.append("Operations processing personally identifiable information (PII) and sensitive data.")
        lines.append("")

        pii_ops = [e for e in entries if e.processes_pii]

        if not pii_ops:
            lines.append("[OK] No PII processing operations identified.")
            lines.append("")
            return lines

        # Group by classification level
        classified = defaultdict(list)
        for entry in pii_ops:
            classification = entry.data_classification.upper() if entry.data_classification else 'UNCLASSIFIED'
            classified[classification].append(entry)

        for classification in ['RESTRICTED', 'CONFIDENTIAL', 'INTERNAL', 'PUBLIC', 'UNCLASSIFIED']:
            ops = classified.get(classification, [])
            if not ops:
                continue

            lines.append(f"{'[LOCKED] RESTRICTED' if classification == 'RESTRICTED' else '🔐 CONFIDENTIAL' if classification == 'CONFIDENTIAL' else '[FOLDER] INTERNAL' if classification == 'INTERNAL' else '🌐 PUBLIC' if classification == 'PUBLIC' else '[WARN]  UNCLASSIFIED'} DATA")
            lines.append("─" * 100)
            lines.append("")

            for entry in ops:
                lines.append(f"Operation: {entry.operation_name}")
                lines.append(f"  PII Columns: {', '.join(entry.pii_columns) if entry.pii_columns else 'Not specified'}")

                if entry.business_justification:
                    lines.append(f"  Purpose: {entry.business_justification[:80]}...")

                lines.append("")

            lines.append("")

        return lines

    def _generate_approval_trail(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate approval trail."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 6: APPROVAL TRAIL")
        lines.append("═" * 100)
        lines.append("")
        lines.append("Record of governance approvals for audit purposes.")
        lines.append("")

        approved_ops = [e for e in entries if e.approval_status and 'approved' in e.approval_status.lower()]
        pending_ops = [e for e in entries if e.approval_status and 'pending' in e.approval_status.lower()]

        if not approved_ops and not pending_ops:
            lines.append("[INFO] No approval requirements documented.")
            lines.append("")
            return lines

        if approved_ops:
            lines.append("[OK] APPROVED OPERATIONS")
            lines.append("─" * 100)
            lines.append("")

            for entry in approved_ops:
                lines.append(f"- {entry.operation_name}")
                if entry.approved_by:
                    lines.append(f"    Approved By: {entry.approved_by}")
                if entry.approval_date:
                    lines.append(f"    Date: {entry.approval_date}")
                lines.append("")

            lines.append("")

        if pending_ops:
            lines.append("[WARN]  PENDING APPROVAL (NOT APPROVED FOR PRODUCTION)")
            lines.append("─" * 100)
            lines.append("")

            for entry in pending_ops:
                lines.append(f"- {entry.operation_name}")
                lines.append("")

            lines.append("")

        return lines

    def _generate_recommendations(self, entries: List[GovernanceCatalogEntry]) -> List[str]:
        """Generate recommendations for improving governance."""
        lines = []
        lines.append("═" * 100)
        lines.append("SECTION 7: RECOMMENDATIONS & ACTION ITEMS")
        lines.append("═" * 100)
        lines.append("")

        recommendations = []

        # Check for missing justifications
        missing_justification = [e for e in entries if not e.business_justification]
        if missing_justification:
            recommendations.append(
                f"[NOTE] Document business justifications for {len(missing_justification)} operations: " +
                ", ".join([e.operation_name for e in missing_justification[:3]]) +
                ("..." if len(missing_justification) > 3 else "")
            )

        # Check for risks without mitigations
        risks_without_mitigations = []
        for entry in entries:
            if entry.risks:
                risk_ids = {self._get_attr(r, 'risk_id', '') for r in entry.risks}
                mitigation_ids = {self._get_attr(m, 'risk_id', '') for m in entry.mitigations}
                unmitigated = risk_ids - mitigation_ids
                if unmitigated:
                    risks_without_mitigations.append(entry.operation_name)

        if risks_without_mitigations:
            recommendations.append(
                f"[WARN]  Document mitigations for unmitigated risks in: " +
                ", ".join(risks_without_mitigations[:3]) +
                ("..." if len(risks_without_mitigations) > 3 else "")
            )

        # Check for customer-impacting ops without approvals
        unapproved_impact = [
            e for e in entries
            if 'direct' in e.customer_impact_level.lower()
            and (not e.approval_status or 'pending' in e.approval_status.lower())
        ]
        if unapproved_impact:
            recommendations.append(
                f"[RED] Obtain approvals for {len(unapproved_impact)} customer-impacting operations: " +
                ", ".join([e.operation_name for e in unapproved_impact[:3]]) +
                ("..." if len(unapproved_impact) > 3 else "")
            )

        # Check for PII ops without classification
        pii_unclassified = [e for e in entries if e.processes_pii and not e.data_classification]
        if pii_unclassified:
            recommendations.append(
                f"[LOCKED] Classify {len(pii_unclassified)} PII-processing operations: " +
                ", ".join([e.operation_name for e in pii_unclassified[:3]]) +
                ("..." if len(pii_unclassified) > 3 else "")
            )

        if recommendations:
            lines.append("ACTION ITEMS:")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        else:
            lines.append("[OK] ALL GOVERNANCE REQUIREMENTS MET")
            lines.append("")
            lines.append("This pipeline has comprehensive governance documentation.")
            lines.append("")

        return lines

    def _generate_footer(self) -> List[str]:
        """Generate catalog footer."""
        lines = []
        lines.append("═" * 100)
        lines.append("END OF GOVERNANCE CATALOG")
        lines.append("═" * 100)
        lines.append("")
        lines.append("This catalog was automatically generated by PySpark StoryDoc Governance Framework.")
        lines.append("For questions or to report issues, consult your governance team.")
        lines.append("")
        return lines

    # Helper methods

    def _get_attr(self, obj: Any, attr: str, default: Any = None) -> Any:
        """Safely get attribute from object or dict."""
        if hasattr(obj, attr):
            return getattr(obj, attr)
        elif isinstance(obj, dict):
            return obj.get(attr, default)
        return default

    def _find_mitigation(self, mitigations: List[Any], risk_id: str) -> Optional[Any]:
        """Find mitigation for given risk ID."""
        for mitigation in mitigations:
            if self._get_attr(mitigation, 'risk_id', '') == risk_id:
                return mitigation
        return None

    def _pct(self, num: int, denom: int) -> float:
        """Calculate percentage."""
        if denom == 0:
            return 0.0
        return (num / denom) * 100

    def _wrap_text(self, text: str, width: int, indent: str = "") -> str:
        """Wrap text to specified width with optional indent."""
        if not text:
            return ""

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > width:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length

        if current_line:
            lines.append(' '.join(current_line))

        return ('\n' + indent).join(lines)


# Convenience function
def generate_comprehensive_governance_catalog(
    lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
    output_path: str,
    title: Optional[str] = None
) -> str:
    """
    Generate comprehensive governance catalog.

    Args:
        lineage_graph: The lineage graph to document
        output_path: Path to save the catalog
        title: Optional custom title

    Returns:
        Path to generated catalog
    """
    catalog = ComprehensiveGovernanceCatalog()
    return catalog.generate_catalog(lineage_graph, output_path, title)
