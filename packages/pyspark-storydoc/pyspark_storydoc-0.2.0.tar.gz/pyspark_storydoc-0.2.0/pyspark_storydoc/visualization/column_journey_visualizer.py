"""Column Journey Visualization - tracks metrics horizontally across operations."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.graph_builder import (
    BusinessConceptNode,
    LineageGraph,
    MetricsData,
    OperationNode,
)

logger = logging.getLogger(__name__)


@dataclass
class ColumnJourney:
    """Represents a column's journey through operations."""
    column_name: str
    journey_points: List[Tuple[str, Optional[int]]]  # (operation_name, distinct_count)
    starts_at_operation: int  # Index where this column first appears
    ends_at_operation: int    # Index where this column last appears


@dataclass
class OperationStep:
    """Represents an operation step in the journey."""
    operation_name: str
    operation_type: str
    business_context: str
    order_index: int


class ColumnJourneyVisualizer:
    """
    Visualizer that shows how tracked columns flow horizontally through operations.

    Each tracked column gets its own row, and operations are shown as columns.
    When multiple data sources join, their metrics converge.
    """

    def __init__(self, lineage_graph: LineageGraph):
        """
        Initialize the Column Journey Visualizer.

        Args:
            lineage_graph: The lineage graph to visualize
        """
        self.lineage_graph = lineage_graph
        self.operations: List[OperationStep] = []
        self.column_journeys: Dict[str, ColumnJourney] = {}
        self.all_tracked_columns: Set[str] = set()

    def _extract_operations_sequence(self) -> List[OperationStep]:
        """Extract operations in chronological order from all business concepts."""
        operations = []
        order_index = 0

        # Get all business concepts
        business_concepts = self.lineage_graph.get_business_concepts()

        # Sort business concepts by creation time for consistent ordering
        business_concepts.sort(key=lambda x: getattr(x, 'created_at', 0))

        for concept in business_concepts:
            # Add operations from each business concept
            for op in concept.technical_operations:
                operations.append(OperationStep(
                    operation_name=op.name,
                    operation_type=op.operation_type.value,
                    business_context=concept.name,
                    order_index=order_index
                ))
                order_index += 1

        return operations

    def _extract_tracked_columns(self) -> Set[str]:
        """Extract all tracked columns from operations that have metrics."""
        columns = set()

        for concept in self.lineage_graph.get_business_concepts():
            # Get columns from business concept track_columns
            if hasattr(concept, 'track_columns') and concept.track_columns:
                columns.update(concept.track_columns)

            # Get columns from operation metrics
            for op in concept.technical_operations:
                if op.before_metrics and op.before_metrics.distinct_counts:
                    columns.update(op.before_metrics.distinct_counts.keys())
                if op.after_metrics and op.after_metrics.distinct_counts:
                    columns.update(op.after_metrics.distinct_counts.keys())

        return columns

    def _build_column_journeys(self) -> Dict[str, ColumnJourney]:
        """Build the journey for each tracked column."""
        journeys = {}

        for column in self.all_tracked_columns:
            journey_points = []
            starts_at = len(self.operations)  # Start with max index
            ends_at = -1

            for i, op_step in enumerate(self.operations):
                # Find the corresponding operation node
                op_node = self._find_operation_node(op_step.operation_name)
                distinct_count = None

                if op_node:
                    # Check after_metrics first (result of operation)
                    if (op_node.after_metrics and
                        op_node.after_metrics.distinct_counts and
                        column in op_node.after_metrics.distinct_counts):
                        distinct_count = op_node.after_metrics.distinct_counts[column]
                        starts_at = min(starts_at, i)
                        ends_at = max(ends_at, i)
                    # Fall back to before_metrics if after_metrics not available
                    elif (op_node.before_metrics and
                          op_node.before_metrics.distinct_counts and
                          column in op_node.before_metrics.distinct_counts):
                        distinct_count = op_node.before_metrics.distinct_counts[column]
                        starts_at = min(starts_at, i)
                        ends_at = max(ends_at, i)

                journey_points.append((op_step.operation_name, distinct_count))

            # Handle case where column never appears
            if starts_at == len(self.operations):
                starts_at = 0
                ends_at = 0

            journeys[column] = ColumnJourney(
                column_name=column,
                journey_points=journey_points,
                starts_at_operation=starts_at,
                ends_at_operation=ends_at
            )

        return journeys

    def _find_operation_node(self, operation_name: str) -> Optional[OperationNode]:
        """Find an operation node by name."""
        for concept in self.lineage_graph.get_business_concepts():
            for op in concept.technical_operations:
                if op.name == operation_name:
                    return op
        return None

    def generate_text_visualization(self) -> str:
        """Generate a text-based column journey visualization."""
        # Extract data
        self.operations = self._extract_operations_sequence()
        self.all_tracked_columns = self._extract_tracked_columns()
        self.column_journeys = self._build_column_journeys()

        if not self.operations:
            return "No operations found in lineage graph."

        if not self.all_tracked_columns:
            return "No tracked columns found in lineage graph."

        # Build the visualization
        lines = []
        lines.append("Column Journey Visualization")
        lines.append("=" * 50)
        lines.append("")

        # Create header with operation names
        header_line = "Column".ljust(15)
        for op in self.operations:
            op_name = op.operation_name[:12] + ("..." if len(op.operation_name) > 12 else "")
            header_line += f"| {op_name:^15} "
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # Create rows for each column
        for column in sorted(self.all_tracked_columns):
            journey = self.column_journeys[column]
            row_line = column[:14].ljust(15)

            for i, (op_name, count) in enumerate(journey.journey_points):
                if count is not None:
                    count_str = f"[{count}]"
                    if i > journey.starts_at_operation and i <= journey.ends_at_operation:
                        # Show connection line
                        row_line += f"|--{count_str:^11}--"
                    else:
                        row_line += f"| {count_str:^15} "
                else:
                    if i >= journey.starts_at_operation and i <= journey.ends_at_operation:
                        row_line += "|" + "-" * 15 + "--"
                    else:
                        row_line += "| {:<15} ".format("[N/A]")

            lines.append(row_line)

        # Add operation details
        lines.append("")
        lines.append("Operation Details:")
        lines.append("-" * 20)
        for i, op in enumerate(self.operations):
            lines.append(f"{i+1:2}. {op.operation_name} ({op.operation_type}) - {op.business_context}")

        # Add summary
        lines.append("")
        lines.append("Summary:")
        lines.append(f"- Total Operations: {len(self.operations)}")
        lines.append(f"- Tracked Columns: {len(self.all_tracked_columns)}")
        lines.append("- Legend: [N/A] = Column not present, [123] = Distinct count, -- = Flow connection")

        return "\n".join(lines)

    def generate_html_visualization(self) -> str:
        """Generate an HTML-based column journey visualization."""
        # Extract data
        self.operations = self._extract_operations_sequence()
        self.all_tracked_columns = self._extract_tracked_columns()
        self.column_journeys = self._build_column_journeys()

        if not self.operations:
            return "<p>No operations found in lineage graph.</p>"

        if not self.all_tracked_columns:
            return "<p>No tracked columns found in lineage graph.</p>"

        html_parts = []
        html_parts.append("""
        <div class="column-journey-visualization">
            <h2>Column Journey Visualization</h2>
            <style>
                .column-journey-visualization {
                    font-family: 'Courier New', monospace;
                    margin: 20px;
                }
                .journey-table {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }
                .journey-table th, .journey-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                .journey-table th {
                    background-color: #f2f2f2;
                    font-weight: bold;
                }
                .column-name {
                    background-color: #e6f3ff;
                    font-weight: bold;
                    text-align: left;
                }
                .metric-present {
                    background-color: #d4edda;
                }
                .metric-absent {
                    background-color: #f8d7da;
                    color: #721c24;
                }
                .operation-details {
                    margin-top: 20px;
                    font-size: 0.9em;
                }
            </style>
            <table class="journey-table">
                <thead>
                    <tr>
                        <th class="column-name">Column</th>
        """)

        # Add operation headers
        for op in self.operations:
            html_parts.append(f'<th title="{op.business_context} - {op.operation_type}">{op.operation_name}</th>')

        html_parts.append("""
                    </tr>
                </thead>
                <tbody>
        """)

        # Add rows for each column
        for column in sorted(self.all_tracked_columns):
            journey = self.column_journeys[column]
            html_parts.append(f'<tr><td class="column-name">{column}</td>')

            for i, (op_name, count) in enumerate(journey.journey_points):
                if count is not None:
                    html_parts.append(f'<td class="metric-present">[{count}]</td>')
                else:
                    html_parts.append('<td class="metric-absent">[N/A]</td>')

            html_parts.append('</tr>')

        html_parts.append("""
                </tbody>
            </table>
            <div class="operation-details">
                <h3>Operation Details:</h3>
                <ul>
        """)

        # Add operation details
        for i, op in enumerate(self.operations):
            html_parts.append(f'<li><strong>{op.operation_name}</strong> ({op.operation_type}) - {op.business_context}</li>')

        html_parts.append(f"""
                </ul>
                <p><strong>Summary:</strong> {len(self.operations)} operations, {len(self.all_tracked_columns)} tracked columns</p>
            </div>
        </div>
        """)

        return "".join(html_parts)

    def generate_mermaid_diagram(self) -> str:
        """Generate a Mermaid flowchart with grid layout showing column journeys."""
        # Extract data
        self.operations = self._extract_operations_sequence()
        self.all_tracked_columns = self._extract_tracked_columns()
        self.column_journeys = self._build_column_journeys()

        if not self.operations:
            return "flowchart TD\n    A[No operations found]"

        if not self.all_tracked_columns:
            return "flowchart TD\n    A[No tracked columns found]"

        lines = []
        lines.append("flowchart TD")
        lines.append("")

        # Create header row nodes for operations
        lines.append("    %% Header Row - Operations")
        for i, op in enumerate(self.operations):
            op_name_clean = op.operation_name.replace('&gt;', '>').replace('&lt;', '<').replace('&', 'and')
            header_id = f"H{i}"
            lines.append(f"    {header_id}[\"{op_name_clean}<br/>{op.operation_type}\"]")

        # Connect header nodes horizontally
        for i in range(len(self.operations) - 1):
            lines.append(f"    H{i} --- H{i+1}")

        lines.append("")

        # Create row label nodes for columns
        lines.append("    %% Row Labels - Columns")
        for i, column in enumerate(sorted(self.all_tracked_columns)):
            col_id = f"R{i}"
            lines.append(f"    {col_id}[\"{column}\"]")

        # Connect row labels vertically
        sorted_columns = sorted(self.all_tracked_columns)
        for i in range(len(sorted_columns) - 1):
            lines.append(f"    R{i} --- R{i+1}")

        lines.append("")

        # Create data cells
        lines.append("    %% Data Cells")
        for row_idx, column in enumerate(sorted_columns):
            journey = self.column_journeys[column]

            for col_idx, (op_name, count) in enumerate(journey.journey_points):
                cell_id = f"C{row_idx}_{col_idx}"

                if count is not None:
                    lines.append(f"    {cell_id}[\"{count:,}\"]")
                else:
                    lines.append(f"    {cell_id}[\"N/A\"]")

        lines.append("")

        # Create grid connections
        lines.append("    %% Grid Connections")

        # Connect headers to data cells vertically
        for col_idx in range(len(self.operations)):
            lines.append(f"    H{col_idx} --- C0_{col_idx}")

        # Connect row labels to data cells horizontally
        for row_idx in range(len(sorted_columns)):
            lines.append(f"    R{row_idx} --- C{row_idx}_0")

        # Connect data cells in grid pattern
        for row_idx in range(len(sorted_columns)):
            for col_idx in range(len(self.operations) - 1):
                lines.append(f"    C{row_idx}_{col_idx} --- C{row_idx}_{col_idx+1}")

        for col_idx in range(len(self.operations)):
            for row_idx in range(len(sorted_columns) - 1):
                lines.append(f"    C{row_idx}_{col_idx} --- C{row_idx+1}_{col_idx}")

        lines.append("")

        # Add styling with business context coloring
        lines.append("    %% Styling")

        # Group operations by business context for header coloring
        business_contexts = {}
        for op in self.operations:
            if op.business_context not in business_contexts:
                business_contexts[op.business_context] = []
            business_contexts[op.business_context].append(op)

        # Style headers by business context
        context_colors = ["#e1f5fe", "#f3e5f5", "#e8f5e8", "#fff3e0", "#fce4ec"]
        for ctx_idx, (context, ops) in enumerate(business_contexts.items()):
            color = context_colors[ctx_idx % len(context_colors)]
            lines.append(f"    classDef context{ctx_idx} fill:{color},stroke:#333,stroke-width:2px")

            for op in ops:
                op_idx = self.operations.index(op)
                lines.append(f"    class H{op_idx} context{ctx_idx}")

        # Style other elements
        lines.append("    classDef rowLabel fill:#f0f0f0,stroke:#666,stroke-width:2px,font-weight:bold")
        lines.append("    classDef dataCell fill:#ffffff,stroke:#ccc,stroke-width:1px")
        lines.append("    classDef naCell fill:#ffebee,stroke:#ccc,stroke-width:1px")

        # Apply styles
        for i in range(len(sorted_columns)):
            lines.append(f"    class R{i} rowLabel")

        for row_idx in range(len(sorted_columns)):
            journey = self.column_journeys[sorted_columns[row_idx]]
            for col_idx, (op_name, count) in enumerate(journey.journey_points):
                cell_id = f"C{row_idx}_{col_idx}"
                if count is not None:
                    lines.append(f"    class {cell_id} dataCell")
                else:
                    lines.append(f"    class {cell_id} naCell")

        return "\n".join(lines)

    def generate_markdown_table(self) -> str:
        """Generate a Markdown table showing column journeys."""
        # Extract data
        self.operations = self._extract_operations_sequence()
        self.all_tracked_columns = self._extract_tracked_columns()
        self.column_journeys = self._build_column_journeys()

        if not self.operations:
            return "# Column Journey Visualization\n\nNo operations found."

        if not self.all_tracked_columns:
            return "# Column Journey Visualization\n\nNo tracked columns found."

        lines = []
        lines.append("# Column Journey Visualization")
        lines.append("")

        # Group operations by business context for section headers
        business_contexts = {}
        for op in self.operations:
            if op.business_context not in business_contexts:
                business_contexts[op.business_context] = []
            business_contexts[op.business_context].append(op)

        # Add business context legend
        lines.append("## Business Context Legend")
        for i, context in enumerate(business_contexts.keys()):
            clean_context = context.replace('&gt;', '>').replace('&lt;', '<')
            lines.append(f"- **Context {i+1}**: {clean_context}")
        lines.append("")

        # Create table header
        header_line = "| Column |"
        separator_line = "|--------|"

        for i, op in enumerate(self.operations):
            # Find business context for this operation
            context_num = 1
            for j, (context, ops) in enumerate(business_contexts.items()):
                if op in ops:
                    context_num = j + 1
                    break

            op_name_clean = op.operation_name.replace('&gt;', '>').replace('&lt;', '<')
            header_cell = f" **{op_name_clean}** (C{context_num}) |"
            header_line += header_cell
            separator_line += "--------|"

        lines.append(header_line)
        lines.append(separator_line)

        # Create complete data rows for the main table
        for column in sorted(self.all_tracked_columns):
            journey = self.column_journeys[column]
            row_line = f"| **{column}** |"

            for op_idx, (op_name, count) in enumerate(journey.journey_points):
                if count is not None:
                    cell_value = f" {count:,} |"
                else:
                    cell_value = " N/A |"

                row_line += cell_value

            lines.append(row_line)

        lines.append("")

        # Group table by business context sections
        for ctx_idx, (context, ops) in enumerate(business_contexts.items()):
            clean_context = context.replace('&gt;', '>').replace('&lt;', '<')
            lines.append(f"## Business Context {ctx_idx + 1}: {clean_context}")
            lines.append("")

            # Create sub-table for this business context
            # Find operations in this context
            context_op_indices = [self.operations.index(op) for op in ops]

            if context_op_indices:
                # Create header for this context
                ctx_header_line = "| Column |"
                ctx_separator_line = "|--------|"

                for op_idx in context_op_indices:
                    op = self.operations[op_idx]
                    op_name_clean = op.operation_name.replace('&gt;', '>').replace('&lt;', '<')
                    ctx_header_line += f" **{op_name_clean}** |"
                    ctx_separator_line += "--------|"

                lines.append(ctx_header_line)
                lines.append(ctx_separator_line)

                # Create data rows for this context
                for column in sorted(self.all_tracked_columns):
                    journey = self.column_journeys[column]

                    # Check if this column has data in this context
                    has_data_in_context = False
                    for op_idx in context_op_indices:
                        if op_idx < len(journey.journey_points):
                            _, count = journey.journey_points[op_idx]
                            if count is not None:
                                has_data_in_context = True
                                break

                    if has_data_in_context:
                        row_line = f"| **{column}** |"

                        for op_idx in context_op_indices:
                            if op_idx < len(journey.journey_points):
                                _, count = journey.journey_points[op_idx]
                                if count is not None:
                                    cell_value = f" {count:,} |"
                                else:
                                    cell_value = " N/A |"
                            else:
                                cell_value = " N/A |"

                            row_line += cell_value

                        lines.append(row_line)

                lines.append("")

        # Add summary
        lines.append("## Summary")
        lines.append(f"- **Total Operations**: {len(self.operations)}")
        lines.append(f"- **Tracked Columns**: {len(self.all_tracked_columns)}")
        lines.append(f"- **Business Contexts**: {len(business_contexts)}")
        lines.append("")
        lines.append("**Note**: Values represent distinct counts for each tracked column at each operation.")

        return "\n".join(lines)

    def generate_ascii_table(self) -> str:
        """Generate an ASCII table showing column journeys."""
        # Extract data
        self.operations = self._extract_operations_sequence()
        self.all_tracked_columns = self._extract_tracked_columns()
        self.column_journeys = self._build_column_journeys()

        if not self.operations:
            return "Column Journey Visualization\n\nNo operations found."

        if not self.all_tracked_columns:
            return "Column Journey Visualization\n\nNo tracked columns found."

        lines = []
        lines.append("COLUMN JOURNEY VISUALIZATION")
        lines.append("=" * 80)
        lines.append("")

        # Group operations by business context
        business_contexts = {}
        for op in self.operations:
            if op.business_context not in business_contexts:
                business_contexts[op.business_context] = []
            business_contexts[op.business_context].append(op)

        # Add business context legend
        lines.append("BUSINESS CONTEXT LEGEND:")
        lines.append("-" * 25)
        for i, context in enumerate(business_contexts.keys()):
            clean_context = context.replace('&gt;', '>').replace('&lt;', '<')
            lines.append(f"[C{i+1}] {clean_context}")
        lines.append("")

        # Calculate column widths
        col_width = 12
        row_label_width = max(len(col) for col in self.all_tracked_columns) + 2

        # Create header
        header_parts = ["Column".ljust(row_label_width)]
        separator_parts = ["-" * row_label_width]

        for i, op in enumerate(self.operations):
            # Find business context
            context_num = 1
            for j, (context, ops) in enumerate(business_contexts.items()):
                if op in ops:
                    context_num = j + 1
                    break

            op_name_clean = op.operation_name.replace('&gt;', '>').replace('&lt;', '<')
            op_header = f"{op_name_clean[:10]}(C{context_num})"
            header_parts.append(op_header.ljust(col_width))
            separator_parts.append("-" * col_width)

        lines.append("| " + " | ".join(header_parts) + " |")
        lines.append("|-" + "-|-".join(separator_parts) + "-|")

        # Group table by business context sections
        for ctx_idx, (context, ops) in enumerate(business_contexts.items()):
            clean_context = context.replace('&gt;', '>').replace('&lt;', '<')
            lines.append(f"BUSINESS CONTEXT {ctx_idx + 1}: {clean_context.upper()}")
            lines.append("=" * min(len(f"BUSINESS CONTEXT {ctx_idx + 1}: {clean_context.upper()}"), 80))
            lines.append("")

            # Find operations in this context
            context_op_indices = [self.operations.index(op) for op in ops]

            if context_op_indices:
                # Create header for this context
                ctx_header_parts = ["Column".ljust(row_label_width)]
                ctx_separator_parts = ["-" * row_label_width]

                for op_idx in context_op_indices:
                    op = self.operations[op_idx]
                    op_name_clean = op.operation_name.replace('&gt;', '>').replace('&lt;', '<')
                    op_header = f"{op_name_clean[:col_width-1]}"
                    ctx_header_parts.append(op_header.ljust(col_width))
                    ctx_separator_parts.append("-" * col_width)

                lines.append("| " + " | ".join(ctx_header_parts) + " |")
                lines.append("|-" + "-|-".join(ctx_separator_parts) + "-|")

                # Create data rows for this context
                for column in sorted(self.all_tracked_columns):
                    journey = self.column_journeys[column]

                    # Check if this column has data in this context
                    has_data_in_context = False
                    for op_idx in context_op_indices:
                        if op_idx < len(journey.journey_points):
                            _, count = journey.journey_points[op_idx]
                            if count is not None:
                                has_data_in_context = True
                                break

                    if has_data_in_context:
                        row_parts = [column.ljust(row_label_width)]

                        for op_idx in context_op_indices:
                            if op_idx < len(journey.journey_points):
                                _, count = journey.journey_points[op_idx]
                                if count is not None:
                                    cell_value = f"{count:,}"
                                else:
                                    cell_value = "N/A"
                            else:
                                cell_value = "N/A"

                            row_parts.append(cell_value[:col_width].ljust(col_width))

                        lines.append("| " + " | ".join(row_parts) + " |")

                lines.append("")

        # Add summary
        lines.append("SUMMARY:")
        lines.append(f"  Operations: {len(self.operations)}")
        lines.append(f"  Columns:    {len(self.all_tracked_columns)}")
        lines.append(f"  Contexts:   {len(business_contexts)}")
        lines.append("")
        lines.append("NOTE: Values represent distinct counts for each tracked column at each operation.")

        return "\n".join(lines)

    def export_to_file(self, filename: str, format_type: str = "html") -> None:
        """
        Export the column journey visualization to a file.

        Args:
            filename: Output filename
            format_type: Export format ("html", "text", "mermaid", "markdown", or "ascii")
        """
        if format_type.lower() == "html":
            content = self.generate_html_visualization()
        elif format_type.lower() == "mermaid":
            content = self.generate_mermaid_diagram()
        elif format_type.lower() == "markdown" or format_type.lower() == "md":
            content = self.generate_markdown_table()
        elif format_type.lower() == "ascii":
            content = self.generate_ascii_table()
        else:
            content = self.generate_text_visualization()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Column journey visualization exported to {filename}")