"""Simple governance catalog generator for text-based documentation."""

from datetime import datetime
from typing import Any, Dict, List, Union

from ..core.enhanced_lineage_graph import EnhancedLineageGraph
from ..core.graph_builder import LineageGraph
from .metadata import ApprovalStatus, GovernanceMetadata


class GovernanceCatalog:
    """
    Generate simple text-based governance catalog from lineage graph.

    Highlights:
    - Business justifications
    - Risks and mitigations
    - Customer impact
    - Approval status
    - Data classification
    """

    def __init__(self):
        """Initialize catalog generator."""
        pass

    def _extract_governed_concepts(self, lineage_graph: Union[LineageGraph, EnhancedLineageGraph]) -> List[Any]:
        """
        Extract concepts with governance metadata from the graph.

        Args:
            lineage_graph: Either LineageGraph or EnhancedLineageGraph

        Returns:
            List of concepts with governance metadata
        """
        concepts = []

        if isinstance(lineage_graph, EnhancedLineageGraph):
            # Extract from EnhancedLineageGraph
            for node in lineage_graph.nodes.values():
                if 'business_context' in node.metadata:
                    governance = node.metadata.get('governance_metadata')
                    if governance:
                        concept = {
                            'name': node.metadata.get('operation_name', node.name),
                            'node_id': node.node_id,
                            'governance': governance,
                            'metadata': node.metadata
                        }
                        concepts.append(concept)
        elif isinstance(lineage_graph, LineageGraph):
            # Extract from LineageGraph
            for node in lineage_graph.get_business_concepts():
                if hasattr(node, 'governance_metadata') and node.governance_metadata:
                    concept = {
                        'name': node.name,
                        'node_id': node.node_id,
                        'governance': node.governance_metadata,
                        'metadata': node.metadata if hasattr(node, 'metadata') else {}
                    }
                    concepts.append(concept)

        return concepts

    def generate_catalog(
        self,
        lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
        output_path: str,
        include_summary: bool = True
    ) -> str:
        """
        Generate governance catalog in text format.

        Args:
            lineage_graph: The lineage graph to document
            output_path: Path to save the catalog
            include_summary: Include executive summary

        Returns:
            Path to generated catalog
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("GOVERNANCE CATALOG")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Pipeline: {lineage_graph.name}")
        lines.append("")

        # Get governed concepts
        concepts = self._extract_governed_concepts(lineage_graph)

        if not concepts:
            lines.append("[!] No governance metadata found in pipeline.")
            lines.append("")
        else:
            # Summary
            if include_summary:
                lines.extend(self._generate_summary(concepts))
                lines.append("")

            # Detailed catalog
            lines.append("=" * 80)
            lines.append("OPERATIONS CATALOG")
            lines.append("=" * 80)
            lines.append("")

            for i, concept in enumerate(concepts, 1):
                lines.extend(self._format_concept(i, concept))
                lines.append("")

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path

    def _generate_summary(self, concepts: List[Dict[str, Any]]) -> List[str]:
        """Generate executive summary section."""
        lines = ["=" * 80]
        lines.append("EXECUTIVE SUMMARY")
        lines.append("=" * 80)
        lines.append("")

        total = len(concepts)
        lines.append(f"Total Governed Operations: {total}")
        lines.append("")

        # Count by category
        with_justification = sum(1 for c in concepts
                                if hasattr(c['governance'], 'business_justification')
                                and c['governance'].business_justification)

        with_risks = sum(1 for c in concepts
                        if hasattr(c['governance'], 'known_risks')
                        and c['governance'].known_risks)

        with_mitigations = sum(1 for c in concepts
                              if hasattr(c['governance'], 'risk_mitigations')
                              and c['governance'].risk_mitigations)

        customer_impact = sum(1 for c in concepts
                             if hasattr(c['governance'], 'customer_impact_level')
                             and c['governance'].customer_impact_level
                             and c['governance'].customer_impact_level != 'none')

        approved = sum(1 for c in concepts
                      if hasattr(c['governance'], 'approval_status')
                      and c['governance'].approval_status == ApprovalStatus.APPROVED)

        pii_processing = sum(1 for c in concepts
                            if hasattr(c['governance'], 'processes_pii')
                            and c['governance'].processes_pii)

        lines.append("Coverage:")
        lines.append(f"  - Business Justification:  {with_justification}/{total}  ({with_justification/total*100:.0f}%)")
        lines.append(f"  - Risk Assessment:         {with_risks}/{total}  ({with_risks/total*100:.0f}%)")
        lines.append(f"  - Risk Mitigations:        {with_mitigations}/{total}  ({with_mitigations/total*100:.0f}%)")
        lines.append(f"  - Customer Impact:         {customer_impact}/{total}  ({customer_impact/total*100:.0f}%)")
        lines.append(f"  - Approved Operations:     {approved}/{total}  ({approved/total*100:.0f}%)")
        lines.append(f"  - PII Processing:          {pii_processing}/{total}  ({pii_processing/total*100:.0f}%)")

        return lines

    def _format_concept(self, index: int, concept: Dict[str, Any]) -> List[str]:
        """Format a single concept with all its governance metadata."""
        lines = []
        gov = concept['governance']
        name = concept['name']

        lines.append("-" * 80)
        lines.append(f"[{index}] {name}")
        lines.append("-" * 80)
        lines.append("")

        # Business Justification
        if hasattr(gov, 'business_justification') and gov.business_justification:
            lines.append("WHY (Business Justification):")
            lines.append(f"  {gov.business_justification}")
            lines.append("")

        # Regulatory Requirement
        if hasattr(gov, 'regulatory_requirement') and gov.regulatory_requirement:
            lines.append("Regulatory Requirement:")
            lines.append(f"  {gov.regulatory_requirement}")
            lines.append("")

        # Risks
        if hasattr(gov, 'known_risks') and gov.known_risks:
            lines.append("RISKS:")
            for risk in gov.known_risks:
                if hasattr(risk, 'risk_id'):
                    # Structured risk object
                    severity = getattr(risk, 'severity', 'unknown').upper()
                    category = getattr(risk, 'category', 'unknown')
                    description = getattr(risk, 'description', 'No description')
                    lines.append(f"  [{severity}] {category}: {description}")

                    likelihood = getattr(risk, 'likelihood', None)
                    impact = getattr(risk, 'impact', None)
                    if likelihood or impact:
                        lines.append(f"    Likelihood: {likelihood or 'N/A'}  |  Impact: {impact or 'N/A'}")
                else:
                    # Simple string risk
                    lines.append(f"  - {risk}")
            lines.append("")

        # Mitigations
        if hasattr(gov, 'risk_mitigations') and gov.risk_mitigations:
            lines.append("MITIGATIONS:")
            for mitigation in gov.risk_mitigations:
                if hasattr(mitigation, 'risk_id'):
                    # Structured mitigation object
                    risk_id = getattr(mitigation, 'risk_id', 'N/A')
                    strategy = getattr(mitigation, 'mitigation', 'No strategy')
                    status = getattr(mitigation, 'status', 'unknown').upper()
                    effectiveness = getattr(mitigation, 'effectiveness', 'unknown').upper()

                    lines.append(f"  Risk {risk_id}:")
                    lines.append(f"    Strategy: {strategy}")
                    lines.append(f"    Status: {status}  |  Effectiveness: {effectiveness}")

                    review_date = getattr(mitigation, 'review_date', None)
                    if review_date:
                        lines.append(f"    Next Review: {review_date}")
                else:
                    # Simple string mitigation
                    lines.append(f"  - {mitigation}")
            lines.append("")

        # Customer Impact
        if hasattr(gov, 'customer_impact_level') and gov.customer_impact_level:
            impact_level = str(gov.customer_impact_level).upper()
            if impact_level != 'NONE':
                lines.append(f"CUSTOMER IMPACT: {impact_level}")

                if hasattr(gov, 'impacting_columns') and gov.impacting_columns:
                    lines.append(f"  Impacting Columns: {', '.join(gov.impacting_columns)}")

                if hasattr(gov, 'impact_description') and gov.impact_description:
                    lines.append(f"  Description: {gov.impact_description}")

                lines.append("")

        # Data Classification & PII
        if hasattr(gov, 'processes_pii') and gov.processes_pii:
            lines.append("DATA HANDLING:")
            lines.append("  Processes PII: YES")

            if hasattr(gov, 'pii_columns') and gov.pii_columns:
                lines.append(f"  PII Columns: {', '.join(gov.pii_columns)}")

            if hasattr(gov, 'data_classification') and gov.data_classification:
                classification = str(gov.data_classification).upper()
                lines.append(f"  Classification: {classification}")

            if hasattr(gov, 'data_retention_days') and gov.data_retention_days:
                days = gov.data_retention_days
                years = days / 365
                lines.append(f"  Retention: {days} days ({years:.1f} years)")

            lines.append("")

        # Approval Status
        if hasattr(gov, 'requires_approval') and gov.requires_approval:
            lines.append("APPROVAL:")

            if hasattr(gov, 'approval_status') and gov.approval_status:
                status = str(gov.approval_status).upper()
                lines.append(f"  Status: {status}")

                if status == 'APPROVED':
                    if hasattr(gov, 'approved_by') and gov.approved_by:
                        lines.append(f"  Approved By: {gov.approved_by}")

                    if hasattr(gov, 'approval_date') and gov.approval_date:
                        date_str = gov.approval_date if isinstance(gov.approval_date, str) else gov.approval_date.strftime('%Y-%m-%d')
                        lines.append(f"  Date: {date_str}")

                    if hasattr(gov, 'approval_reference') and gov.approval_reference:
                        lines.append(f"  Reference: {gov.approval_reference}")
                elif status == 'PENDING':
                    lines.append("  [!] NOT APPROVED FOR PRODUCTION USE")

            lines.append("")

        # Risk Owner
        if hasattr(gov, 'risk_owner') and gov.risk_owner:
            lines.append(f"Risk Owner: {gov.risk_owner}")
            lines.append("")

        # Review Schedule
        if hasattr(gov, 'next_review_date') and gov.next_review_date:
            review_date = gov.next_review_date if isinstance(gov.next_review_date, str) else gov.next_review_date.strftime('%Y-%m-%d')
            lines.append(f"Next Review: {review_date}")
            lines.append("")

        return lines


# Export convenience function
def generate_governance_catalog(
    lineage_graph: Union[LineageGraph, EnhancedLineageGraph],
    output_path: str
) -> str:
    """
    Generate governance catalog from lineage graph.

    Args:
        lineage_graph: The lineage graph to document
        output_path: Path to save the catalog

    Returns:
        Path to generated catalog
    """
    catalog = GovernanceCatalog()
    return catalog.generate_catalog(lineage_graph, output_path)
