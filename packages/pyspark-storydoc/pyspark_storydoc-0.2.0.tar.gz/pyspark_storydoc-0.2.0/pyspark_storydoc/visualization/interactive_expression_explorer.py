#!/usr/bin/env python3
"""
Interactive Expression Explorer for PySpark StoryDoc.

This module generates interactive HTML visualizations of expression lineage,
allowing users to explore column dependencies, complexity metrics, and impact
analysis through a web interface.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InteractiveExpressionExplorer:
    """
    Generate interactive HTML visualization of expression lineage.

    Features:
    - Click columns to see full expression
    - Highlight upstream dependencies
    - Highlight downstream impacts
    - Filter by expression type
    - Search columns
    - Complexity heat map
    """

    def __init__(self):
        """Initialize the interactive expression explorer."""
        self.template_path = Path(__file__).parent / "templates" / "expression_explorer.html"

    def generate_html(
        self,
        expressions: List[Dict[str, Any]],
        impact_analyzer,
        output_path: str,
        title: str = "Expression Lineage Explorer"
    ) -> str:
        """
        Generate interactive HTML file.

        Args:
            expressions: List of expression dictionaries
            impact_analyzer: ImpactAnalyzer instance with built dependency graph
            output_path: Path to write HTML file
            title: Page title

        Returns:
            Path to generated HTML file
        """
        logger.info(f"Generating interactive expression explorer at {output_path}")

        # Generate graph data
        graph_data = self.generate_graph_data(expressions, impact_analyzer)

        # Generate expression details
        expression_details = self.generate_expression_details(expressions, impact_analyzer)

        # Generate summary statistics
        summary_stats = impact_analyzer.get_impact_summary()

        # Load or create HTML template
        html_content = self._create_html_content(
            title,
            graph_data,
            expression_details,
            summary_stats
        )

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')

        logger.info(f"Interactive explorer generated: {output_path}")
        return str(output_path)

    def generate_graph_data(
        self,
        expressions: List[Dict[str, Any]],
        impact_analyzer
    ) -> Dict[str, Any]:
        """
        Convert lineage graph to D3-compatible JSON.

        Args:
            expressions: List of expression metadata
            impact_analyzer: ImpactAnalyzer instance

        Returns:
            Dictionary with:
                - nodes: List of node objects
                - edges: List of edge objects
        """
        nodes = []
        edges = []
        node_ids = set()

        # Build nodes from expressions
        for expr in expressions:
            col_name = expr.get('column_name')
            node_ids.add(col_name)

            # Analyze impact for this column
            impact = impact_analyzer.analyze_column_impact(col_name)

            # Determine complexity and impact metrics
            complexity = expr.get('complexity_level', 1)
            total_impact = impact.get('total_impact', 0)
            operation_type = expr.get('operation_type', 'unknown')

            nodes.append({
                'id': col_name,
                'label': col_name,
                'type': operation_type,
                'complexity': complexity,
                'impact': total_impact,
                'risk': impact.get('risk_assessment', 'LOW')
            })

            # Build edges from dependencies
            source_columns = expr.get('source_columns', [])
            for source in source_columns:
                # Add source node if not already present
                if source not in node_ids:
                    node_ids.add(source)
                    nodes.append({
                        'id': source,
                        'label': source,
                        'type': 'source',
                        'complexity': 0,
                        'impact': 0,
                        'risk': 'LOW'
                    })

                # Add edge
                edges.append({
                    'source': source,
                    'target': col_name,
                    'type': operation_type
                })

        return {
            'nodes': nodes,
            'edges': edges
        }

    def generate_expression_details(
        self,
        expressions: List[Dict[str, Any]],
        impact_analyzer
    ) -> Dict[str, Any]:
        """
        Generate detailed expression data for each column.

        Args:
            expressions: List of expression metadata
            impact_analyzer: ImpactAnalyzer instance

        Returns:
            Dictionary mapping column names to detail objects
        """
        details = {}

        for expr in expressions:
            col_name = expr.get('column_name')

            # Get impact analysis
            impact = impact_analyzer.analyze_column_impact(col_name)

            # Build formatted impact tree
            impact_tree_text = impact_analyzer.format_impact_tree_text(
                impact.get('impact_tree', {})
            )

            details[col_name] = {
                'column_name': col_name,
                'expression': expr.get('expression', ''),
                'formatted_expression': expr.get('formatted_expression', expr.get('expression', '')),
                'operation_type': expr.get('operation_type', 'unknown'),
                'complexity_level': expr.get('complexity_level', 1),
                'source_columns': expr.get('source_columns', []),
                'direct_dependencies': impact.get('direct_dependencies', []),
                'total_impact': impact.get('total_impact', 0),
                'risk_assessment': impact.get('risk_assessment', 'LOW'),
                'critical_path': impact.get('critical_path', []),
                'impact_tree': impact_tree_text,
                'created_in': expr.get('created_in', 'unknown'),
                'business_concept': expr.get('business_concept', '')
            }

        return details

    def _create_html_content(
        self,
        title: str,
        graph_data: Dict[str, Any],
        expression_details: Dict[str, Any],
        summary_stats: Dict[str, Any]
    ) -> str:
        """
        Create complete HTML content.

        Args:
            title: Page title
            graph_data: Graph data for D3
            expression_details: Expression detail data
            summary_stats: Summary statistics

        Returns:
            Complete HTML string
        """
        # Convert data to JSON for embedding
        graph_data_json = json.dumps(graph_data, indent=2)
        expression_details_json = json.dumps(expression_details, indent=2)
        summary_stats_json = json.dumps(summary_stats, indent=2)

        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Light theme with dark text for maximum readability */
        body {{
            background-color: #ffffff;
            color: #1f2937;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}

        .container-fluid {{
            background-color: #ffffff;
            color: #1f2937;
        }}

        .card {{
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            color: #1f2937;
        }}

        .card-header {{
            background-color: #f3f4f6;
            border-bottom: 1px solid #e5e7eb;
            color: #111827;
            font-weight: 600;
        }}

        .card-body {{
            background-color: #ffffff;
            color: #1f2937;
        }}

        #graph {{
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }}

        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .node circle {{
            stroke: #374151;
            stroke-width: 2px;
        }}

        .node.selected circle {{
            stroke: #ef4444;
            stroke-width: 4px;
        }}

        .node.dependency circle {{
            stroke: #f59e0b;
            stroke-width: 3px;
        }}

        .node.impact circle {{
            stroke: #3b82f6;
            stroke-width: 3px;
        }}

        .node text {{
            fill: #1f2937;
            font-size: 12px;
            font-weight: 500;
            pointer-events: none;
        }}

        .link {{
            stroke: #9ca3af;
            stroke-opacity: 0.6;
            fill: none;
        }}

        .link.highlighted {{
            stroke: #3b82f6;
            stroke-opacity: 1;
            stroke-width: 2px;
        }}

        /* Complexity colors - optimized for light background */
        .complexity-low circle {{ fill: #10b981; }}
        .complexity-medium circle {{ fill: #f59e0b; }}
        .complexity-high circle {{ fill: #ef4444; }}
        .complexity-source circle {{ fill: #3b82f6; }}

        .form-control, .form-select {{
            background-color: #ffffff;
            border: 1px solid #d1d5db;
            color: #1f2937;
        }}

        .form-control:focus, .form-select:focus {{
            background-color: #ffffff;
            border-color: #3b82f6;
            color: #1f2937;
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }}

        .form-check-label {{
            color: #1f2937;
        }}

        .form-check-input {{
            border-color: #d1d5db;
        }}

        .form-check-input:checked {{
            background-color: #3b82f6;
            border-color: #3b82f6;
        }}

        .btn-outline-primary {{
            color: #3b82f6;
            border-color: #3b82f6;
        }}

        .btn-outline-primary:hover {{
            background-color: #3b82f6;
            color: #ffffff;
            border-color: #3b82f6;
        }}

        .table {{
            color: #1f2937;
            background-color: #ffffff;
        }}

        .table thead {{
            background-color: #f3f4f6;
            color: #111827;
            font-weight: 600;
        }}

        .table-striped tbody tr:nth-of-type(odd) {{
            background-color: #f9fafb;
        }}

        .table-hover tbody tr:hover {{
            background-color: #f3f4f6;
            cursor: pointer;
        }}

        #details-panel {{
            max-height: 600px;
            overflow-y: auto;
            background-color: #ffffff;
            color: #1f2937;
            padding: 15px;
        }}

        .stats-item {{
            padding: 10px;
            margin: 6px 0;
            background-color: #f9fafb;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            color: #1f2937;
        }}

        .text-muted {{
            color: #6b7280 !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #111827;
        }}

        pre {{
            background-color: #f3f4f6;
            color: #1f2937;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
        }}

        code {{
            background-color: #f3f4f6;
            color: #1f2937;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}

        strong {{
            color: #111827;
            font-weight: 600;
        }}

        .badge {{
            font-weight: 500;
        }}

        /* Arrow marker for light background */
        #arrowhead {{
            fill: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="container-fluid p-3">
        <h1 class="mb-4">{title}</h1>

        <div class="row">
            <!-- Left sidebar: Controls -->
            <div class="col-md-3">
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="mb-0">Search & Filter</h5>
                    </div>
                    <div class="card-body">
                        <input type="text" class="form-control mb-3" id="search" placeholder="Search columns...">

                        <h6>Column Types</h6>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="show-source" checked>
                            <label class="form-check-label" for="show-source">Source Columns</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="show-derived" checked>
                            <label class="form-check-label" for="show-derived">Derived Columns</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="show-aggregations" checked>
                            <label class="form-check-label" for="show-aggregations">Aggregations</label>
                        </div>

                        <h6 class="mt-3">Complexity Filter</h6>
                        <select class="form-select" id="complexity-filter">
                            <option value="all">All</option>
                            <option value="low">Low (1-3)</option>
                            <option value="medium">Medium (4-6)</option>
                            <option value="high">High (7-10)</option>
                        </select>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Statistics</h5>
                    </div>
                    <div class="card-body">
                        <div id="stats"></div>
                    </div>
                </div>
            </div>

            <!-- Center: Graph visualization -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Dependency Graph</h5>
                    </div>
                    <div class="card-body">
                        <svg id="graph" width="100%" height="600"></svg>
                        <div class="btn-group mt-2" role="group">
                            <button class="btn btn-sm btn-outline-primary" id="zoom-in">Zoom In</button>
                            <button class="btn btn-sm btn-outline-primary" id="zoom-out">Zoom Out</button>
                            <button class="btn btn-sm btn-outline-primary" id="reset">Reset View</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right sidebar: Details panel -->
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Column Details</h5>
                    </div>
                    <div class="card-body" id="details-panel">
                        <p class="text-muted">Click a column node to see details</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-3">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">Expression Table</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover" id="expression-table">
                                <thead>
                                    <tr>
                                        <th>Column</th>
                                        <th>Type</th>
                                        <th>Complexity</th>
                                        <th>Dependencies</th>
                                        <th>Impact</th>
                                        <th>Risk</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Embed data
        const graphData = {graph_data_json};
        const expressionDetails = {expression_details_json};
        const summaryStats = {summary_stats_json};

        // Initialize visualization
        let selectedNode = null;
        let simulation = null;

        // Render statistics
        function renderStatistics() {{
            const statsHtml = `
                <div class="stats-item"><strong>Total Columns:</strong> ${{summaryStats.total_columns}}</div>
                <div class="stats-item"><strong>Source Columns:</strong> ${{summaryStats.source_columns}}</div>
                <div class="stats-item"><strong>Derived Columns:</strong> ${{summaryStats.derived_columns}}</div>
                <div class="stats-item"><strong>Leaf Columns:</strong> ${{summaryStats.leaf_columns}}</div>
                <div class="stats-item"><strong>Max Chain Length:</strong> ${{summaryStats.max_chain_length}}</div>
                <div class="stats-item"><strong>Avg Dependencies:</strong> ${{summaryStats.avg_dependencies}}</div>
            `;
            document.getElementById('stats').innerHTML = statsHtml;
        }}

        // Render graph
        function renderGraph() {{
            const svg = d3.select("#graph");
            const width = svg.node().getBoundingClientRect().width;
            const height = 600;

            svg.selectAll("*").remove();

            const g = svg.append("g");

            // Create zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on("zoom", (event) => {{
                    g.attr("transform", event.transform);
                }});

            svg.call(zoom);

            // Create simulation
            simulation = d3.forceSimulation(graphData.nodes)
                .force("link", d3.forceLink(graphData.edges).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(30));

            // Create links
            const link = g.append("g")
                .selectAll("path")
                .data(graphData.edges)
                .join("path")
                .attr("class", "link")
                .attr("marker-end", "url(#arrowhead)");

            // Add arrow marker
            svg.append("defs").append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#9ca3af");

            // Create nodes
            const node = g.append("g")
                .selectAll("g")
                .data(graphData.nodes)
                .join("g")
                .attr("class", d => {{
                    let classes = ["node"];
                    if (d.complexity === 0) classes.push("complexity-source");
                    else if (d.complexity <= 3) classes.push("complexity-low");
                    else if (d.complexity <= 6) classes.push("complexity-medium");
                    else classes.push("complexity-high");
                    return classes.join(" ");
                }})
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended))
                .on("click", (event, d) => {{
                    showDetails(d.id);
                    highlightConnections(d.id);
                    event.stopPropagation();
                }});

            node.append("circle")
                .attr("r", d => 5 + d.impact * 2);

            node.append("text")
                .attr("dx", 12)
                .attr("dy", 4)
                .text(d => d.label);

            // Update positions on simulation tick
            simulation.on("tick", () => {{
                link.attr("d", d => {{
                    const dx = d.target.x - d.source.x;
                    const dy = d.target.y - d.source.y;
                    const dr = Math.sqrt(dx * dx + dy * dy);
                    return `M${{d.source.x}},${{d.source.y}}L${{d.target.x}},${{d.target.y}}`;
                }});

                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});

            // Zoom controls
            document.getElementById('zoom-in').onclick = () => {{
                svg.transition().call(zoom.scaleBy, 1.3);
            }};

            document.getElementById('zoom-out').onclick = () => {{
                svg.transition().call(zoom.scaleBy, 0.7);
            }};

            document.getElementById('reset').onclick = () => {{
                svg.transition().call(zoom.transform, d3.zoomIdentity);
            }};
        }}

        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}

        // Show column details
        function showDetails(columnName) {{
            const details = expressionDetails[columnName];
            if (!details) return;

            const html = `
                <h6>${{details.column_name}}</h6>
                <p><strong>Type:</strong> ${{details.operation_type}}</p>
                <p><strong>Complexity:</strong> ${{details.complexity_level}}/10</p>
                <p><strong>Risk:</strong> <span class="badge bg-${{details.risk_assessment === 'HIGH' ? 'danger' : details.risk_assessment === 'MEDIUM' ? 'warning' : 'success'}}">${{details.risk_assessment}}</span></p>

                <h6 class="mt-3">Expression</h6>
                <pre>${{details.formatted_expression}}</pre>

                <h6 class="mt-3">Dependencies</h6>
                <p>${{details.source_columns.length > 0 ? details.source_columns.join(', ') : 'None'}}</p>

                <h6 class="mt-3">Downstream Impact</h6>
                <p><strong>Direct:</strong> ${{details.direct_dependencies.length}}</p>
                <p><strong>Total:</strong> ${{details.total_impact}}</p>

                <h6 class="mt-3">Impact Tree</h6>
                <pre>${{details.impact_tree}}</pre>
            `;

            document.getElementById('details-panel').innerHTML = html;
        }}

        // Highlight connections
        function highlightConnections(columnName) {{
            const details = expressionDetails[columnName];
            if (!details) return;

            const dependencies = new Set(details.source_columns);
            const impacts = new Set(details.direct_dependencies);

            d3.selectAll(".node")
                .classed("selected", d => d.id === columnName)
                .classed("dependency", d => dependencies.has(d.id))
                .classed("impact", d => impacts.has(d.id));

            d3.selectAll(".link")
                .classed("highlighted", d =>
                    (d.source.id === columnName || d.target.id === columnName) ||
                    (dependencies.has(d.source.id) && d.target.id === columnName) ||
                    (d.source.id === columnName && impacts.has(d.target.id))
                );
        }}

        // Populate expression table
        function populateTable() {{
            const tbody = document.querySelector('#expression-table tbody');
            tbody.innerHTML = '';

            Object.values(expressionDetails).forEach(details => {{
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td><strong>${{details.column_name}}</strong></td>
                    <td>${{details.operation_type}}</td>
                    <td>${{details.complexity_level}}/10</td>
                    <td>${{details.source_columns.length}}</td>
                    <td>${{details.total_impact}}</td>
                    <td><span class="badge bg-${{details.risk_assessment === 'HIGH' ? 'danger' : details.risk_assessment === 'MEDIUM' ? 'warning' : 'success'}}">${{details.risk_assessment}}</span></td>
                `;
                row.style.cursor = 'pointer';
                row.onclick = () => {{
                    showDetails(details.column_name);
                    highlightConnections(details.column_name);
                }};
            }});
        }}

        // Initialize
        renderStatistics();
        renderGraph();
        populateTable();

        // Search functionality
        document.getElementById('search').addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            d3.selectAll(".node")
                .style("opacity", d => d.label.toLowerCase().includes(query) ? 1 : 0.2);
        }});
    </script>
</body>
</html>
"""
        return html
