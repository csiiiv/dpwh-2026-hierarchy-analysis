#!/usr/bin/env python3
"""
Flatten hierarchical JSON data to a tabular format.
Creates a table where each row represents a leaf node with all ancestor values.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional

def get_full_path(node: Dict[str, Any], path: List[str] = None) -> List[str]:
    """
    Get the full path from root to this node.
    
    Args:
        node: Current node
        path: Current path (used recursively)
    
    Returns:
        List of values from root to node
    """
    if path is None:
        path = []
    
    current_path = path + [node.get('value', '')]
    
    # This is a leaf node (no children) - return the path
    if not node.get('children'):
        return [current_path]
    
    # Recursively get paths from all children
    all_paths = []
    for child in node['children']:
        child_paths = get_full_path(child, current_path)
        all_paths.extend(child_paths)
    
    return all_paths

def get_leaf_nodes_with_details(nodes: List[Dict[str, Any]], parent_info: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Extract all leaf nodes with their details.
    
    Args:
        nodes: List of nodes to process
        parent_info: Dictionary containing parent metadata (path, ancestors, etc.)
    
    Returns:
        List of leaf node dictionaries with full information
    """
    if parent_info is None:
        parent_info = {
            'path': [],
            'ancestors': [],
            'levels': {}
        }
    
    leaf_nodes = []
    
    for node in nodes:
        # Build current node info
        current_path = parent_info['path'] + [node['value']]
        current_ancestors = parent_info['ancestors'] + [node]
        current_levels = parent_info['levels'].copy()
        
        # Add this node to levels dict
        level_num = len(current_path) - 1
        current_levels[level_num] = {
            'value': node['value'],
            'amount': node.get('amount'),
            'description': node.get('description')
        }
        
        # Check if this is a leaf node
        if not node.get('children'):
            # This is a leaf - create a row
            leaf_info = {
                'path': current_path,
                'ancestors': current_ancestors,
                'levels': current_levels,
                'value': node['value'],
                'description': node.get('description', ''),
                'amount': node.get('amount'),
                'depth': level_num
            }
            leaf_nodes.append(leaf_info)
        else:
            # Recursively process children
            child_leaves = get_leaf_nodes_with_details(
                node['children'],
                {
                    'path': current_path,
                    'ancestors': current_ancestors,
                    'levels': current_levels
                }
            )
            leaf_nodes.extend(child_leaves)
    
    return leaf_nodes

def leaf_to_table_row(leaf: Dict[str, Any], max_levels: int = 9) -> Dict[str, Any]:
    """
    Convert a leaf node to a table row.
    
    Args:
        leaf: Leaf node dictionary
        max_levels: Maximum number of hierarchy levels
    
    Returns:
        Dictionary with table columns
    """
    row = {}
    
    # Add level columns
    for i in range(max_levels):
        level_key = f'level_{i}'
        if i in leaf['levels']:
            row[level_key] = leaf['levels'][i]['value']
        else:
            row[level_key] = ''
    
    # Add other columns
    row['value'] = leaf['value']
    row['description'] = leaf['description']
    row['amount'] = leaf['amount']
    row['depth'] = leaf['depth']
    
    # Add full path as a single string
    row['full_path'] = ' > '.join(leaf['path'])
    
    return row

def flatten_hierarchy_to_csv(
    json_path: Path,
    output_path: Path,
    max_levels: int = 9
) -> int:
    """
    Flatten hierarchical JSON to CSV format.
    
    Args:
        json_path: Path to input JSON file
        output_path: Path to output CSV file
        max_levels: Maximum number of hierarchy levels
    
    Returns:
        Number of rows written
    """
    print(f"Reading JSON file: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extracting leaf nodes...")
    leaf_nodes = get_leaf_nodes_with_details(data)
    
    print(f"Found {len(leaf_nodes)} leaf nodes")
    
    # Determine actual max depth
    max_depth = max(leaf['depth'] for leaf in leaf_nodes)
    print(f"Maximum depth: {max_depth}")
    
    # Use the larger of specified max_levels or actual max depth
    actual_max_levels = max(max_levels, max_depth + 1)
    
    print(f"Converting to table rows...")
    rows = [leaf_to_table_row(leaf, actual_max_levels) for leaf in leaf_nodes]
    
    # Define CSV columns
    fieldnames = [f'level_{i}' for i in range(actual_max_levels)]
    fieldnames.extend(['value', 'description', 'amount', 'depth', 'full_path'])
    
    print(f"Writing CSV file: {output_path}")
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✓ Written {len(rows)} rows to {output_path}")
    
    # Calculate total amount
    total_amount = sum(row['amount'] for row in rows if row['amount'] is not None)
    print(f"✓ Total amount: ₱{total_amount:,.2f}")
    
    return len(rows)

def flatten_hierarchy_to_json(
    json_path: Path,
    output_path: Path,
    max_levels: int = 9
) -> int:
    """
    Flatten hierarchical JSON to JSON table format.
    
    Args:
        json_path: Path to input JSON file
        output_path: Path to output JSON file
        max_levels: Maximum number of hierarchy levels
    
    Returns:
        Number of rows written
    """
    print(f"Reading JSON file: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Extracting leaf nodes...")
    leaf_nodes = get_leaf_nodes_with_details(data)
    
    print(f"Found {len(leaf_nodes)} leaf nodes")
    
    # Determine actual max depth
    max_depth = max(leaf['depth'] for leaf in leaf_nodes)
    actual_max_levels = max(max_levels, max_depth + 1)
    
    print(f"Converting to table rows...")
    rows = [leaf_to_table_row(leaf, actual_max_levels) for leaf in leaf_nodes]
    
    print(f"Writing JSON file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Written {len(rows)} rows to {output_path}")
    
    return len(rows)

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
        return 1
    
    # Output files
    output_csv = data_dir / f"{json_file.stem}_table.csv"
    output_json = data_dir / f"{json_file.stem}_table.json"
    
    try:
        print("=" * 80)
        print("FLATTENING HIERARCHY TO TABLE")
        print("=" * 80)
        
        # Generate CSV
        print("\nGenerating CSV...")
        csv_rows = flatten_hierarchy_to_csv(json_file, output_csv)
        
        # Generate JSON
        print("\nGenerating JSON table...")
        json_rows = flatten_hierarchy_to_json(json_file, output_json)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"CSV output:  {output_csv} ({csv_rows:,} rows)")
        print(f"JSON output: {output_json} ({json_rows:,} rows)")
        print("\n✓ Conversion complete!")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
