"""
Markdown Validation Utilities.

This module provides utilities to validate markdown files, including checking
that all image references point to existing files.
"""
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import unquote

logger = logging.getLogger(__name__)


def extract_image_references(markdown_content: str) -> List[Tuple[str, str]]:
    """
    Extract all image references from markdown content.

    Finds both standard markdown images and HTML img tags:
    - ![alt text](path/to/image.png)
    - <img src="path/to/image.png" />

    Args:
        markdown_content: The markdown file content as a string

    Returns:
        List of tuples (alt_text_or_tag, image_path)
    """
    images = []

    # Match markdown image syntax: ![alt](path)
    markdown_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    for match in re.finditer(markdown_pattern, markdown_content):
        alt_text = match.group(1)
        image_path = match.group(2)
        # Remove URL fragments and query strings
        image_path = image_path.split('#')[0].split('?')[0]
        images.append((alt_text, image_path))

    # Match HTML img tags: <img src="path" ...>
    html_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    for match in re.finditer(html_pattern, markdown_content):
        image_path = match.group(1)
        # Remove URL fragments and query strings
        image_path = image_path.split('#')[0].split('?')[0]
        images.append(("HTML img tag", image_path))

    return images


def resolve_image_path(markdown_file_path: Path, image_ref: str) -> Optional[Path]:
    """
    Resolve an image reference to an absolute path.

    Handles:
    - Absolute paths
    - Relative paths (relative to the markdown file)
    - URLs (skipped, returns None)
    - URL-encoded characters (like %20 for spaces)

    Args:
        markdown_file_path: Path to the markdown file
        image_ref: The image reference from the markdown

    Returns:
        Resolved absolute path, or None if it's a URL or can't be resolved
    """
    # Skip URLs
    if image_ref.startswith(('http://', 'https://', 'ftp://', '//')):
        return None

    # URL-decode the path to handle encoded characters like %20 (space)
    decoded_ref = unquote(image_ref)

    # Handle absolute paths
    image_path = Path(decoded_ref)
    if image_path.is_absolute():
        return image_path

    # Handle relative paths - resolve relative to markdown file location
    markdown_dir = markdown_file_path.parent
    resolved_path = (markdown_dir / image_path).resolve()

    return resolved_path


def validate_image_references(markdown_file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate that all image references in a markdown file actually exist.

    This function:
    1. Parses the markdown file for image references (both markdown and HTML syntax)
    2. Resolves each image path (handling relative and absolute paths)
    3. Checks if each image file exists
    4. Returns validation results

    Args:
        markdown_file_path: Path to the markdown file to validate

    Returns:
        Tuple of (all_valid, missing_images) where:
        - all_valid: True if all images exist, False otherwise
        - missing_images: List of paths to missing image files

    Example:
        >>> valid, missing = validate_image_references("report.md")
        >>> if not valid:
        ...     print(f"Missing images: {missing}")
    """
    md_path = Path(markdown_file_path)

    # Check if markdown file exists
    if not md_path.exists():
        logger.error(f"Markdown file not found: {markdown_file_path}")
        return False, [f"Markdown file not found: {markdown_file_path}"]

    # Read markdown content
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading markdown file: {e}")
        return False, [f"Error reading file: {e}"]

    # Extract image references
    image_refs = extract_image_references(content)

    if not image_refs:
        # No images to validate
        logger.debug(f"No image references found in {markdown_file_path}")
        return True, []

    # Validate each image
    missing_images = []

    for alt_text, image_ref in image_refs:
        # Resolve the image path
        image_path = resolve_image_path(md_path, image_ref)

        # Skip URLs (they're external, we can't validate them)
        if image_path is None:
            logger.debug(f"Skipping URL reference: {image_ref}")
            continue

        # Check if image exists
        if not image_path.exists():
            missing_images.append(str(image_ref))
            logger.warning(f"Missing image: {image_ref} (resolved to: {image_path})")

    all_valid = len(missing_images) == 0

    if all_valid:
        logger.info(f"All {len(image_refs)} image references validated successfully in {markdown_file_path}")
    else:
        logger.error(f"{len(missing_images)} missing images in {markdown_file_path}")

    return all_valid, missing_images


def validate_markdown_directory(directory_path: str, recursive: bool = True) -> dict:
    """
    Validate all markdown files in a directory.

    Args:
        directory_path: Path to the directory to scan
        recursive: If True, scan subdirectories recursively

    Returns:
        Dictionary with validation results:
        {
            'total_files': int,
            'valid_files': int,
            'invalid_files': int,
            'details': {
                'file_path': {
                    'valid': bool,
                    'missing_images': list
                },
                ...
            }
        }
    """
    dir_path = Path(directory_path)

    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Directory not found: {directory_path}")

    # Find all markdown files
    if recursive:
        md_files = list(dir_path.rglob("*.md"))
    else:
        md_files = list(dir_path.glob("*.md"))

    results = {
        'total_files': len(md_files),
        'valid_files': 0,
        'invalid_files': 0,
        'details': {}
    }

    for md_file in md_files:
        valid, missing = validate_image_references(str(md_file))

        results['details'][str(md_file)] = {
            'valid': valid,
            'missing_images': missing
        }

        if valid:
            results['valid_files'] += 1
        else:
            results['invalid_files'] += 1

    return results
