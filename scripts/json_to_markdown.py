#!/usr/bin/env python3
"""
Convert hierarchical JSON to markdown format.
Creates a markdown file with a hierarchical list structure.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

def format_amount(amount):
    """Format amount as Philippine Peso."""
    if amount is None:
        return ""
    return f" ₱{amount:,.2f}"

def escape_markdown(text):
    """Escape special markdown characters."""
    if not text:
        return ""
    # Escape special characters that might break markdown
    text = str(text)
    # Escape pipe characters (used in tables)
    text = text.replace('|', '\\|')
    return text

def node_to_markdown(node: Dict[str, Any], level: int = 0, prefix: str = "") -> List[str]:
    """
    Convert a node to markdown list items.
    
    Args:
        node: Node dictionary with value, amount, description, children
        level: Current indentation level (0-based)
        prefix: Prefix for list markers (for nested lists)
    
    Returns:
        List of markdown lines
    """
    lines = []
    
    # Build the line content
    value = escape_markdown(node.get('value', ''))
    amount = format_amount(node.get('amount'))
    description = node.get('description')
    
    # Create the list item
    indent = "  " * level
    list_marker = "-" if level == 0 else "-"
    
    # Main line with value and amount
    line = f"{indent}{list_marker} **{value}**{amount}"
    lines.append(line)
    
    # Add description if present (as a sub-item or in italics)
    if description:
        desc_text = escape_markdown(description)
        # Add description as a nested item or in parentheses
        desc_indent = "  " * (level + 1)
        lines.append(f"{desc_indent}  *{desc_text}*")
    
    # Process children
    children = node.get('children', [])
    if children:
        for child in children:
            child_lines = node_to_markdown(child, level + 1)
            lines.extend(child_lines)
    
    return lines

def json_to_markdown(json_path: Path, output_path: Path = None) -> str:
    """
    Convert JSON hierarchy to markdown format.
    
    Args:
        json_path: Path to input JSON file
        output_path: Path to output markdown file (optional)
    
    Returns:
        Markdown string
    """
    print(f"Reading JSON file: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Build markdown content
    markdown_lines = []
    
    # Add header
    markdown_lines.append("# DPWH 2026 GAA Hierarchy")
    markdown_lines.append("")
    markdown_lines.append("This document contains the hierarchical structure of the DPWH 2026 General Appropriations Act.")
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # Process each root node
    for root in data:
        root_lines = node_to_markdown(root, level=0)
        markdown_lines.extend(root_lines)
        markdown_lines.append("")  # Add spacing between root nodes
    
    markdown_content = "\n".join(markdown_lines)
    
    # Write to file if output path specified
    if output_path:
        print(f"Writing markdown to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ Markdown file created: {output_path}")
    else:
        # Return the content
        return markdown_content
    
    return markdown_content

def main():
    """Main function."""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    
    # Find JSON file
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    if not json_file.exists():
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)
    
    # Output markdown file
    output_file = data_dir / f"{json_file.stem}.md"
    
    try:
        json_to_markdown(json_file, output_file)
        print(f"\n✓ Conversion complete!")
        print(f"  Input:  {json_file}")
        print(f"  Output: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
