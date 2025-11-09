"""Customer impact detection for identifying operations that affect customers."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..core.graph_builder import BusinessConceptNode, LineageGraph, OperationNode


class ImpactType(Enum):
    """Types of customer impact."""
    FINANCIAL = "financial"  # Pricing, fees, charges
    ACCESS_DECISION = "access_decision"  # Approval, eligibility, access control
    MARKETING = "marketing"  # Offers, promotions, targeting
    RISK_ASSESSMENT = "risk_assessment"  # Risk scores, credit scores
    SERVICE_LEVEL = "service_level"  # Service tier, priority, limits
    OTHER_DIRECT_IMPACT = "other_direct_impact"


@dataclass
class ImpactingColumn:
    """A column that impacts customers."""
    column_name: str
    node_id: str
    node_name: str
    impact_type: ImpactType
    confidence: float
    detection_method: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "column_name": self.column_name,
            "node_id": self.node_id,
            "node_name": self.node_name,
            "impact_type": self.impact_type.value,
            "confidence": self.confidence,
            "detection_method": self.detection_method,
        }


@dataclass
class CustomerImpactAnalysis:
    """Complete customer impact analysis for a pipeline."""
    impact_level: str  # direct, indirect, none
    impacting_columns: List[ImpactingColumn]
    impacting_concepts: List[str]  # Node IDs of impacting concepts
    confidence: float
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "impact_level": self.impact_level,
            "impacting_columns": [col.to_dict() for col in self.impacting_columns],
            "impacting_concepts": self.impacting_concepts,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
        }


class CustomerImpactDetector:
    """
    Detect operations and columns that impact customers.

    Uses pattern matching on column names and operation descriptions to
    identify customer-impacting operations.
    """

    # Pattern categories for different impact types
    FINANCIAL_PATTERNS = [
        r"price", r"premium", r"cost", r"fee", r"charge", r"payment",
        r"amount", r"total", r"subtotal", r"discount", r"refund",
        r"interest", r"rate", r"apr", r"balance"
    ]

    DECISION_PATTERNS = [
        r"approval", r"approved", r"decline", r"declined", r"reject",
        r"decision", r"eligibility", r"eligible", r"status",
        r"qualified", r"qualification", r"acceptance", r"accepted"
    ]

    MARKETING_PATTERNS = [
        r"offer", r"promotion", r"campaign", r"discount", r"coupon",
        r"voucher", r"incentive", r"reward", r"loyalty", r"targeting"
    ]

    RISK_SCORE_PATTERNS = [
        r"risk.*score", r"credit.*score", r"risk.*rating",
        r"credit.*rating", r"propensity", r"probability"
    ]

    SERVICE_LEVEL_PATTERNS = [
        r"tier", r"level", r"priority", r"limit", r"threshold",
        r"quota", r"allowance", r"entitlement"
    ]

    # Customer identifier patterns
    CUSTOMER_ID_PATTERNS = [
        r"customer.*id", r"cust.*id", r"user.*id", r"member.*id",
        r"account.*id", r"client.*id", r"subscriber.*id"
    ]

    def __init__(self):
        """Initialize the customer impact detector."""
        pass

    def detect_impact(self, lineage_graph: LineageGraph) -> CustomerImpactAnalysis:
        """
        Analyze entire lineage for customer impact.

        Args:
            lineage_graph: The lineage graph to analyze

        Returns:
            Complete customer impact analysis
        """
        # 1. Identify leaf nodes (outputs)
        leaf_nodes = lineage_graph.get_leaf_nodes()

        # 2. Analyze output columns
        impacting_columns = []
        for leaf in leaf_nodes:
            if isinstance(leaf, (BusinessConceptNode, OperationNode)):
                # Check tracked columns
                if isinstance(leaf, BusinessConceptNode):
                    columns_to_check = leaf.track_columns
                else:
                    columns_to_check = []

                # Also check governance metadata if present
                if hasattr(leaf, 'governance_metadata') and leaf.governance_metadata:
                    if leaf.governance_metadata.impacting_columns:
                        columns_to_check.extend(leaf.governance_metadata.impacting_columns)

                for col in columns_to_check:
                    impact_type, confidence = self._classify_column_impact(col)
                    if impact_type:
                        impacting_columns.append(ImpactingColumn(
                            column_name=col,
                            node_id=leaf.node_id,
                            node_name=leaf.name,
                            impact_type=impact_type,
                            confidence=confidence,
                            detection_method="column_name_pattern"
                        ))

        # 3. Identify impacting concepts
        impacting_concepts = []
        for col_info in impacting_columns:
            if col_info.node_id not in impacting_concepts:
                impacting_concepts.append(col_info.node_id)

        # 4. Check business concepts for explicit impact declarations
        for node in lineage_graph.nodes.values():
            if isinstance(node, BusinessConceptNode):
                if hasattr(node, 'governance_metadata') and node.governance_metadata:
                    if node.governance_metadata.customer_impact_level:
                        impact_level_value = node.governance_metadata.customer_impact_level.value
                        if impact_level_value in ["direct", "indirect"]:
                            if node.node_id not in impacting_concepts:
                                impacting_concepts.append(node.node_id)

        # 5. Classify overall impact level
        impact_level = self._classify_impact_level(impacting_columns, impacting_concepts, lineage_graph)

        # 6. Calculate aggregate confidence
        confidence = self._aggregate_confidence(impacting_columns)

        # 7. Generate recommendations
        recommendations = self._generate_recommendations(impact_level, impacting_columns)

        return CustomerImpactAnalysis(
            impact_level=impact_level,
            impacting_columns=impacting_columns,
            impacting_concepts=impacting_concepts,
            confidence=confidence,
            recommendations=recommendations
        )

    def _classify_column_impact(self, column_name: str) -> tuple[Optional[ImpactType], float]:
        """
        Classify the type of customer impact for a column.

        Returns:
            Tuple of (ImpactType, confidence) or (None, 0.0) if no impact detected
        """
        column_lower = column_name.lower()

        # Check financial patterns
        for pattern in self.FINANCIAL_PATTERNS:
            if re.search(pattern, column_lower):
                return ImpactType.FINANCIAL, 0.90

        # Check decision patterns
        for pattern in self.DECISION_PATTERNS:
            if re.search(pattern, column_lower):
                return ImpactType.ACCESS_DECISION, 0.85

        # Check marketing patterns
        for pattern in self.MARKETING_PATTERNS:
            if re.search(pattern, column_lower):
                return ImpactType.MARKETING, 0.80

        # Check risk score patterns
        for pattern in self.RISK_SCORE_PATTERNS:
            if re.search(pattern, column_lower):
                return ImpactType.RISK_ASSESSMENT, 0.85

        # Check service level patterns
        for pattern in self.SERVICE_LEVEL_PATTERNS:
            if re.search(pattern, column_lower):
                return ImpactType.SERVICE_LEVEL, 0.75

        return None, 0.0

    def _is_impacting_column(self, column_name: str) -> bool:
        """Check if column name suggests customer impact."""
        impact_type, _ = self._classify_column_impact(column_name)
        return impact_type is not None

    def _classify_impact_level(
        self,
        impacting_columns: List[ImpactingColumn],
        impacting_concepts: List[str],
        lineage_graph: LineageGraph
    ) -> str:
        """
        Classify overall impact level: direct, indirect, or none.

        Args:
            impacting_columns: List of identified impacting columns
            impacting_concepts: List of impacting concept IDs
            lineage_graph: The lineage graph

        Returns:
            Impact level: "direct", "indirect", or "none"
        """
        # If no impacting columns or concepts, no impact
        if not impacting_columns and not impacting_concepts:
            return "none"

        # Check if any concept explicitly declares direct impact
        for concept_id in impacting_concepts:
            node = lineage_graph.get_node(concept_id)
            if isinstance(node, BusinessConceptNode):
                if hasattr(node, 'governance_metadata') and node.governance_metadata:
                    if node.governance_metadata.customer_impact_level:
                        level = node.governance_metadata.customer_impact_level.value
                        if level == "direct":
                            return "direct"

        # Check impact types of columns
        high_impact_types = {ImpactType.FINANCIAL, ImpactType.ACCESS_DECISION}
        for col in impacting_columns:
            if col.impact_type in high_impact_types and col.confidence > 0.75:
                return "direct"

        # If we have impacting columns but not high-confidence direct impact
        if impacting_columns:
            return "indirect"

        # If we have impacting concepts but no specific columns identified
        if impacting_concepts:
            return "indirect"

        return "none"

    def _aggregate_confidence(self, impacting_columns: List[ImpactingColumn]) -> float:
        """Calculate aggregate confidence score."""
        if not impacting_columns:
            return 0.0

        return sum(col.confidence for col in impacting_columns) / len(impacting_columns)

    def _generate_recommendations(self, impact_level: str, impacting_columns: List[ImpactingColumn]) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []

        if impact_level == "direct":
            recommendations.append(
                "[WARN] CRITICAL: Direct customer impact detected. Implement comprehensive testing, "
                "validation rules, and human review processes for outliers."
            )
            recommendations.append(
                "Document business justification and obtain necessary approvals before production deployment."
            )
            recommendations.append(
                "Implement monitoring and alerting for unexpected changes in impacting columns."
            )

            # Check for specific impact types
            financial_cols = [col for col in impacting_columns if col.impact_type == ImpactType.FINANCIAL]
            if financial_cols:
                recommendations.append(
                    f"Financial impact detected in columns: {', '.join(col.column_name for col in financial_cols)}. "
                    "Implement financial reconciliation and audit trails."
                )

            decision_cols = [col for col in impacting_columns if col.impact_type == ImpactType.ACCESS_DECISION]
            if decision_cols:
                recommendations.append(
                    f"Access decision impact detected in columns: {', '.join(col.column_name for col in decision_cols)}. "
                    "Perform fairness analysis and disparate impact testing."
                )

        elif impact_level == "indirect":
            recommendations.append(
                "Indirect customer impact detected. Document how this operation influences customer treatment."
            )
            recommendations.append(
                "Consider implementing monitoring for downstream impacts."
            )

        else:
            recommendations.append(
                "No customer impact detected. This operation appears to be for internal analytics or reporting."
            )

        return recommendations

    def trace_column_lineage(
        self,
        lineage_graph: LineageGraph,
        column_name: str,
        starting_node_id: str
    ) -> List[str]:
        """
        Trace a column back through the lineage to identify source operations.

        Args:
            lineage_graph: The lineage graph
            column_name: The column to trace
            starting_node_id: The node ID where the column appears

        Returns:
            List of node IDs that contributed to this column
        """
        # This is a simplified version - full implementation would track column transformations
        source_nodes = []
        visited = set()

        def trace_parents(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)

            node = lineage_graph.get_node(node_id)
            if node:
                source_nodes.append(node_id)
                for parent_id in node.parents:
                    trace_parents(parent_id)

        trace_parents(starting_node_id)
        return source_nodes

    def get_impacting_operations(self, lineage_graph: LineageGraph) -> List[BusinessConceptNode]:
        """
        Get all operations that have been marked or detected as customer-impacting.

        Args:
            lineage_graph: The lineage graph

        Returns:
            List of business concept nodes with customer impact
        """
        impacting_nodes = []

        for node in lineage_graph.nodes.values():
            if isinstance(node, BusinessConceptNode):
                # Check explicit governance metadata
                if hasattr(node, 'governance_metadata') and node.governance_metadata:
                    if node.governance_metadata.customer_impact_level:
                        level = node.governance_metadata.customer_impact_level.value
                        if level in ["direct", "indirect"]:
                            impacting_nodes.append(node)
                            continue

                # Check if tracked columns are impacting
                if node.track_columns:
                    for col in node.track_columns:
                        if self._is_impacting_column(col):
                            impacting_nodes.append(node)
                            break

        return impacting_nodes
