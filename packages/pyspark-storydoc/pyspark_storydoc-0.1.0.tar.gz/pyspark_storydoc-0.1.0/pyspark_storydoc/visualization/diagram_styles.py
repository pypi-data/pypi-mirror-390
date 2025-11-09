"""
Centralized diagram styling configuration for consistent visualization across all diagrams.

This module defines standardized node types, shapes, colors, and edge styles following:
- Standard flowchart conventions
- Colorblind-friendly palette (Blue/Orange/Green)
- WCAG 2.1 AA contrast requirements (4.5:1 minimum)
- Semantic shape meanings
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class NodeStyle:
    """Style definition for a node type."""
    fill_color: str
    stroke_color: str
    stroke_width: str
    text_color: str
    description: str


@dataclass
class ShapeDefinition:
    """Shape definition with Mermaid syntax."""
    mermaid_template: str  # e.g., "{{{{'{content}'}}}}" for diamond
    description: str


# Node shape definitions (following standard flowchart conventions)
NODE_SHAPES: Dict[str, ShapeDefinition] = {
    'diamond': ShapeDefinition(
        mermaid_template='{{"{content}"}}',
        description='Input/Decision point - Used for data sources'
    ),
    'hexagon': ShapeDefinition(
        mermaid_template='{{"{content}"}}',
        description='Preparation/Condition - Used for filters'
    ),
    'rectangle': ShapeDefinition(
        mermaid_template='["{content}"]',
        description='Process/Action - Used for transformations'
    ),
    'subroutine': ShapeDefinition(
        mermaid_template='[["{content}"]]',
        description='Complex subprocess - Used for joins'
    ),
    'stadium': ShapeDefinition(
        mermaid_template='(["{content}"])',
        description='Grouping/Collection - Used for aggregations'
    ),
    'trapezoid': ShapeDefinition(
        mermaid_template='[/"{content}"\\]',
        description='Manual operation/Merge - Used for unions'
    ),
    'rounded_rectangle': ShapeDefinition(
        mermaid_template='("{content}")',
        description='Terminal/Context - Used for business concepts'
    ),
}


# Node type to style mapping (colorblind-friendly palette)
NODE_STYLES: Dict[str, NodeStyle] = {
    # Data Movement Operations
    'source': NodeStyle(
        fill_color='#00BCD4',  # Cyan
        stroke_color='#0097A7',  # Dark Cyan
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Data origin - diamond indicates start/input'
    ),
    'union': NodeStyle(
        fill_color='#00ACC1',  # Teal
        stroke_color='#00838F',  # Dark Teal
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Merging multiple sources'
    ),

    # Data Transformation Operations
    'filter': NodeStyle(
        fill_color='#2196F3',  # Blue
        stroke_color='#1565C0',  # Dark Blue
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Selection/filtering - hexagon shows decision point'
    ),
    'select': NodeStyle(
        fill_color='#1976D2',  # Medium Blue
        stroke_color='#0D47A1',  # Navy
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Column selection'
    ),
    'withColumn': NodeStyle(
        fill_color='#42A5F5',  # Light Blue
        stroke_color='#1976D2',  # Medium Blue
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Column transformation'
    ),
    'transform': NodeStyle(
        fill_color='#9C27B0',  # Purple
        stroke_color='#6A1B9A',  # Dark Purple
        stroke_width='2px',
        text_color='#FFFFFF',
        description='General transformations'
    ),

    # Data Aggregation & Combination
    'join': NodeStyle(
        fill_color='#4CAF50',  # Green
        stroke_color='#2E7D32',  # Dark Green
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Combining datasets - subroutine shows complexity'
    ),
    'group': NodeStyle(
        fill_color='#FF9800',  # Orange
        stroke_color='#E65100',  # Dark Orange
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Aggregation - rounded shows grouping'
    ),
    'groupby': NodeStyle(
        fill_color='#FF9800',  # Orange
        stroke_color='#E65100',  # Dark Orange
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Aggregation - rounded shows grouping'
    ),

    # Business & Context
    'business_concept': NodeStyle(
        fill_color='#E1F5FE',  # Light Blue
        stroke_color='#0277BD',  # Deep Blue
        stroke_width='2px',
        text_color='#000000',
        description='High-level business logic container'
    ),

    # Analysis & Profiling
    'describe_profile': NodeStyle(
        fill_color='#FFF9C4',  # Light Yellow
        stroke_color='#F57F17',  # Dark Yellow
        stroke_width='2px',
        text_color='#000000',
        description='Data profiling/analysis checkpoint'
    ),

    # Compressed Operations
    'compressed': NodeStyle(
        fill_color='#E0E0E0',  # Light Grey
        stroke_color='#9E9E9E',  # Medium Grey
        stroke_width='1px',
        text_color='#424242',
        description='Compressed sequence of non-impacting operations'
    ),

    # Governance Markers
    'governance_direct_impact': NodeStyle(
        fill_color='#FFCDD2',  # Light Red
        stroke_color='#C62828',  # Dark Red
        stroke_width='4px',
        text_color='#000000',
        description='Direct customer impact - requires highest governance'
    ),
    'governance_indirect_impact': NodeStyle(
        fill_color='#FFF9C4',  # Light Yellow
        stroke_color='#F57F17',  # Dark Yellow
        stroke_width='2px',
        text_color='#000000',
        description='Indirect customer impact - requires governance oversight'
    ),
    'governance_risk_critical': NodeStyle(
        fill_color='#FFCDD2',  # Light Red
        stroke_color='#B71C1C',  # Very Dark Red
        stroke_width='4px',
        text_color='#000000',
        description='Critical risk level - immediate attention required'
    ),
    'governance_risk_high': NodeStyle(
        fill_color='#FFE0B2',  # Light Orange
        stroke_color='#E65100',  # Dark Orange
        stroke_width='2px',
        text_color='#000000',
        description='High risk level - regular monitoring required'
    ),
    'governance_risk_medium': NodeStyle(
        fill_color='#FFF9C4',  # Light Yellow
        stroke_color='#F9A825',  # Dark Yellow
        stroke_width='2px',
        text_color='#000000',
        description='Medium risk level - periodic review needed'
    ),
    'governance_approved': NodeStyle(
        fill_color='#C8E6C9',  # Light Green
        stroke_color='#2E7D32',  # Dark Green
        stroke_width='2px',
        text_color='#000000',
        description='Governance approved with mitigation plan'
    ),

    # Default/Fallback
    'default': NodeStyle(
        fill_color='#78909C',  # Blue Grey
        stroke_color='#455A64',  # Dark Blue Grey
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Fallback for undefined types'
    ),
    'operation': NodeStyle(
        fill_color='#78909C',  # Blue Grey
        stroke_color='#455A64',  # Dark Blue Grey
        stroke_width='2px',
        text_color='#FFFFFF',
        description='Generic operation'
    ),
}


# Node type to shape mapping
NODE_TYPE_TO_SHAPE: Dict[str, str] = {
    'source': 'diamond',
    'union': 'trapezoid',
    'filter': 'hexagon',
    'select': 'rectangle',
    'withColumn': 'rectangle',
    'transform': 'rectangle',
    'join': 'subroutine',
    'group': 'stadium',
    'groupby': 'stadium',
    'business_concept': 'rounded_rectangle',
    'describe_profile': 'hexagon',
    'compressed': 'rectangle',
    'default': 'rectangle',
    'operation': 'rectangle',
}


# Edge styles
EDGE_STYLES = {
    'normal': {
        'symbol': '-->',
        'color': '#666666',
        'description': 'Standard data flow'
    },
    'fork': {
        'symbol': '==>',
        'color': '#E65100',
        'description': 'Data reuse/branching'
    },
    'distribution': {
        'symbol': '-.->',
        'color': '#1976D2',
        'description': 'Analysis connection'
    },
}


def get_node_style(operation_type: str) -> NodeStyle:
    """
    Get the style for a given operation type.

    Args:
        operation_type: The type of operation (source, filter, join, etc.)

    Returns:
        NodeStyle object with colors and styling
    """
    return NODE_STYLES.get(operation_type, NODE_STYLES['default'])


def get_node_shape(operation_type: str) -> str:
    """
    Get the Mermaid shape template for a given operation type.

    Args:
        operation_type: The type of operation

    Returns:
        Shape name (diamond, hexagon, rectangle, etc.)
    """
    return NODE_TYPE_TO_SHAPE.get(operation_type, 'rectangle')


def get_mermaid_shape_template(operation_type: str) -> str:
    """
    Get the Mermaid shape template string for a given operation type.

    Args:
        operation_type: The type of operation

    Returns:
        Mermaid template string with {content} placeholder
    """
    shape_name = get_node_shape(operation_type)
    return NODE_SHAPES[shape_name].mermaid_template


def format_node_with_style(node_id: str, content: str, operation_type: str) -> str:
    """
    Format a complete Mermaid node definition with proper shape and style.

    Args:
        node_id: The Mermaid node ID
        content: The content/label for the node
        operation_type: The type of operation

    Returns:
        Complete Mermaid node definition string
    """
    template = get_mermaid_shape_template(operation_type)
    shaped_content = template.replace('{content}', content)
    return f"{node_id}{shaped_content}"


def generate_mermaid_style_classes() -> str:
    """
    Generate Mermaid classDef statements for all node styles.

    Returns:
        Multi-line string with all classDef statements
    """
    lines = []

    for node_type, style in NODE_STYLES.items():
        class_name = f"{node_type}Op" if node_type != 'default' else 'defaultOp'

        # Add dashed stroke for compressed nodes
        if node_type == 'compressed':
            lines.append(
                f" classDef {class_name} "
                f"fill:{style.fill_color},"
                f"stroke:{style.stroke_color},"
                f"stroke-width:{style.stroke_width},"
                f"stroke-dasharray:5 5,"
                f"color:{style.text_color}"
            )
        else:
            lines.append(
                f" classDef {class_name} "
                f"fill:{style.fill_color},"
                f"stroke:{style.stroke_color},"
                f"stroke-width:{style.stroke_width},"
                f"color:{style.text_color}"
            )

    return '\n'.join(lines)


def get_node_class_name(operation_type: str) -> str:
    """
    Get the CSS class name for a given operation type.

    Args:
        operation_type: The type of operation

    Returns:
        CSS class name (e.g., 'sourceOp', 'filterOp')
    """
    if operation_type == 'default':
        return 'defaultOp'
    return f"{operation_type}Op"


def get_legend_items() -> list:
    """
    Get legend items for documentation.

    Returns:
        List of tuples (emoji, name, description)
    """
    legend = [
        ('🔷', 'Source', 'Data loading operations'),
        ('⬡', 'Filter', 'Row filtering operations'),
        ('[GREEN]', 'Join', 'Data joining operations'),
        ('[ORANGE]', 'Group', 'Aggregation operations'),
        ('[PURPLE]', 'Transform', 'General transformations'),
        ('🔶', 'Union', 'Data union operations'),
        ('[BLUE]', 'Select', 'Column selection operations'),
        ('💠', 'WithColumn', 'Column transformation operations'),
    ]
    return legend
