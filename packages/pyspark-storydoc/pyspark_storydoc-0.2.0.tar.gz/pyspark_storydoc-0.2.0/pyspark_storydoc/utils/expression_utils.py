"""Utilities for working with expression lineage and expansion."""

import logging
import re
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def expand_expression(
    column_name: str,
    lineage_graph,
    max_depth: int = 10,
    current_node_id: Optional[str] = None
) -> str:
    """
    Recursively expand an expression to show it in terms of original source columns.

    This function traces back through the lineage graph to replace intermediate
    column references with their actual transformation expressions.

    Args:
        column_name: Name of the column to expand
        lineage_graph: EnhancedLineageGraph containing transformation history
        max_depth: Maximum recursion depth to prevent infinite loops
        current_node_id: ID of the current node (to find transformations before this point)

    Returns:
        Fully expanded expression string

    Example:
        Given:
            price = value * 1.1
            price = price * 1.2  (reassignment)

        expand_expression("price") returns: "((value * 1.1) * 1.2)"
    """
    # Build chronological list of all transform nodes
    transform_nodes = []
    for node_id, node in lineage_graph.nodes.items():
        if hasattr(node, 'metadata') and node.metadata:
            if node.metadata.get('operation_type') == 'transform':
                transform_nodes.append({
                    'node_id': node_id,
                    'timestamp': node.timestamp if hasattr(node, 'timestamp') else 0,
                    'metadata': node.metadata
                })

    # Sort by timestamp
    transform_nodes.sort(key=lambda x: x['timestamp'])

    # If current_node_id is provided, only consider nodes before it
    if current_node_id:
        current_idx = next((i for i, n in enumerate(transform_nodes) if n['node_id'] == current_node_id), None)
        if current_idx is not None:
            transform_nodes = transform_nodes[:current_idx]

    def _expand(col_name: str, depth: int = 0, visited_nodes: Optional[Set[str]] = None) -> Optional[str]:
        """Recursive helper to expand expression."""
        if visited_nodes is None:
            visited_nodes = set()

        if depth >= max_depth:
            logger.warning(f"Max recursion depth reached for column: {col_name}")
            return col_name

        # Find the most recent transformation that created/modified this column
        # Skip any nodes we've already visited to avoid infinite loops
        transformation = None
        found_node_id = None
        for node in reversed(transform_nodes):
            # Skip visited nodes
            if node['node_id'] in visited_nodes:
                continue

            cols_added = node['metadata'].get('columns_added', [])
            cols_modified = node['metadata'].get('columns_modified', [])

            if col_name in cols_added or col_name in cols_modified:
                transformation = node['metadata'].get('transformation', '')
                found_node_id = node['node_id']
                break

        if not transformation or not found_node_id:
            # This is a source column, can't expand further
            return col_name

        # Mark this node as visited
        visited_nodes.add(found_node_id)

        # Extract the expression (right side of assignment)
        expr = _extract_expression(transformation, col_name)
        if not expr:
            return col_name

        # Find all column references in the expression
        referenced_cols = _extract_column_references(expr)

        # Recursively expand each referenced column
        expanded_expr = expr
        for ref_col in referenced_cols:
            # Pass the same visited_nodes to track the path and prevent cycles
            expanded_ref = _expand(ref_col, depth + 1, visited_nodes)
            if expanded_ref and expanded_ref != ref_col:
                # Replace the column reference with its expansion
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(ref_col) + r'\b'
                expanded_expr = re.sub(pattern, f'({expanded_ref})', expanded_expr)

        return expanded_expr

    result = _expand(column_name, 0, None)
    return result if result else column_name


def _find_column_transformation(col_name: str, lineage_graph) -> Optional[str]:
    """Find the most recent transformation that created or modified a column."""
    # Search through nodes in reverse order (most recent first)
    for node_id, node in reversed(list(lineage_graph.nodes.items())):
        if hasattr(node, 'metadata') and node.metadata:
            cols_added = node.metadata.get('columns_added', [])
            cols_modified = node.metadata.get('columns_modified', [])
            transformation = node.metadata.get('transformation', '')

            if col_name in cols_added or col_name in cols_modified:
                if transformation:
                    return transformation

    return None


def _extract_expression(transformation: str, col_name: str) -> Optional[str]:
    """
    Extract the expression from a transformation string.

    Transformations are in the format: "column_name = expression"
    This extracts the "expression" part.
    """
    parts = transformation.split('=', 1)
    if len(parts) == 2:
        return parts[1].strip()
    return None


def _extract_column_references(expression: str) -> List[str]:
    """
    Extract column names referenced in an expression.

    This uses simple heuristics to identify column names:
    - Alphanumeric identifiers (including underscores)
    - Not function names (no parentheses immediately after)
    - Not string literals
    """
    # Remove string literals first to avoid false positives
    expr_without_strings = re.sub(r"'[^']*'", '', expression)
    expr_without_strings = re.sub(r'"[^"]*"', '', expr_without_strings)

    # Find potential column names (identifiers)
    # Match word characters but exclude common SQL/function keywords
    keywords = {
        'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'AND', 'OR', 'NOT',
        'IN', 'IS', 'NULL', 'TRUE', 'FALSE', 'AS', 'OVER', 'PARTITION',
        'ORDER', 'BY', 'ASC', 'DESC', 'LIMIT', 'OFFSET'
    }

    # Match identifiers that aren't followed by '(' (to exclude functions)
    pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()'
    matches = re.findall(pattern, expr_without_strings)

    # Filter out keywords and numbers
    column_refs = []
    for match in matches:
        if match.upper() not in keywords and not match.isdigit():
            column_refs.append(match)

    # Remove duplicates while preserving order
    seen = set()
    result = []
    for col in column_refs:
        if col not in seen:
            seen.add(col)
            result.append(col)

    return result


def get_expression_lineage_chain(
    column_name: str,
    lineage_graph,
    include_source: bool = True
) -> List[Dict[str, str]]:
    """
    Get the complete chain of transformations for a column.

    Returns a list of transformation steps from source to final value.

    Args:
        column_name: Name of the column
        lineage_graph: EnhancedLineageGraph
        include_source: Whether to include source columns in the chain

    Returns:
        List of dicts with 'step', 'column', 'expression' keys

    Example:
        [
            {'step': 1, 'column': 'price', 'expression': 'value * 1.1'},
            {'step': 2, 'column': 'price', 'expression': 'price * 1.2'},
            {'step': 3, 'column': 'price', 'expression': 'price * 0.9'}
        ]
    """
    chain = []
    visited = set()

    def _trace_back(col_name: str):
        """Recursively trace back through transformations."""
        if col_name in visited:
            return
        visited.add(col_name)

        # Find transformation for this column
        for node_id, node in lineage_graph.nodes.items():
            if hasattr(node, 'metadata') and node.metadata:
                cols_added = node.metadata.get('columns_added', [])
                cols_modified = node.metadata.get('columns_modified', [])

                if col_name in cols_added or col_name in cols_modified:
                    transformation = node.metadata.get('transformation', '')
                    if transformation:
                        expr = _extract_expression(transformation, col_name)

                        # Trace back dependencies first
                        if expr:
                            refs = _extract_column_references(expr)
                            for ref in refs:
                                _trace_back(ref)

                        # Add this transformation
                        chain.append({
                            'column': col_name,
                            'expression': expr if expr else transformation,
                            'node_id': node_id,
                            'timestamp': node.timestamp if hasattr(node, 'timestamp') else None
                        })

    _trace_back(column_name)

    # Sort by timestamp to get chronological order
    chain.sort(key=lambda x: x.get('timestamp', 0) if x.get('timestamp') else 0)

    # Add step numbers
    for i, item in enumerate(chain, 1):
        item['step'] = i

    return chain
