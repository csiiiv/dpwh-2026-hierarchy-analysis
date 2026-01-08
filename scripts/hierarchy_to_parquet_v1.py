#!/usr/bin/env python3
"""
Flatten hierarchy to Parquet format - Option 1: Leaf Nodes Only
Creates one row per leaf node with all ancestor values in separate columns.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

def load_json(json_path: Path) -> List[Dict]:
    """Load hierarchical JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def looks_like_amount(value: str) -> bool:
    """Check if a string looks like an amount."""
    if not value:
        return False
    value = value.strip().replace(',', '').replace('₱', '').replace('PHP', '')
    try:
        float(value)
        return True
    except ValueError:
        return False

def find_leaves_and_paths(nodes: List[Dict]) -> List[Dict]:
    """
    Recursively find all leaf nodes and build their full paths.
    
    Returns list of dictionaries with path and amount information.
    """
    results = []
    
    def traverse(node: Dict, current_path: List[str]):
        """Recursively traverse nodes to find leaves."""
        children = node.get('children', [])
        value = node.get('value', '').strip()
        amount = node.get('amount')
        description = node.get('description', '')
        
        if not children:
            # This is a leaf node
            path = current_path + [value]
            results.append({
                'path': ' > '.join(path),
                'level_0': '.',
                'level_1': path[0] if len(path) > 0 else '',
                'level_2': path[1] if len(path) > 1 else '',
                'level_3': path[2] if len(path) > 2 else '',
                'level_4': path[3] if len(path) > 3 else '',
                'level_5': path[4] if len(path) > 4 else '',
                'level_6': path[5] if len(path) > 5 else '',
                'level_7': path[6] if len(path) > 6 else '',
                'level_8': path[7] if len(path) > 7 else '',
                'level_9': path[8] if len(path) > 8 else '',
                'level_10': path[9] if len(path) > 9 else '',
                'level_11': path[10] if len(path) > 10 else '',
                'value': value,
                'description': description,
                'amount': amount,
                'depth': len(path)
            })
        else:
            # Recurse into children
            for child in children:
                traverse(child, current_path + [value])
    
    # Start traversal from root nodes
    for node in nodes:
        traverse(node, [])
    
    return results

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    
    hierarchy_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    print("=" * 80)
    print("FLATTENING HIERARCHY TO PARQUET - OPTION 1: LEAF NODES ONLY")
    print("=" * 80)
    
    print(f"\nLoading hierarchy from: {hierarchy_file}")
    root_nodes = load_json(hierarchy_file)
    print(f"Loaded {len(root_nodes):,} root nodes")
    
    # Find all leaves
    print("\nFinding leaf nodes...")
    leaf_rows = find_leaves_and_paths(root_nodes)
    print(f"Found {len(leaf_rows):,} leaf nodes")
    
    # Calculate statistics
    total_amount = sum(row['amount'] for row in leaf_rows if row['amount'] is not None)
    rows_with_amount = sum(1 for row in leaf_rows if row['amount'] is not None)
    
    # Depth distribution
    depth_dist = {}
    for row in leaf_rows:
        depth = row['depth']
        depth_dist[depth] = depth_dist.get(depth, 0) + 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\nTotal leaf rows: {len(leaf_rows):,}")
    print(f"Rows with amounts: {rows_with_amount}")
    print(f"Total amount: ₱{total_amount:,.2f}" if total_amount else "N/A")
    
    print("\nDepth distribution:")
    for depth in sorted(depth_dist.keys()):
        count = depth_dist[depth]
        pct = count / len(leaf_rows) * 100
        print(f"  Depth {depth}: {count:>6,} ({pct:>5.1f}%)")
    
    # Sample rows
    print("\n" + "=" * 80)
    print("SAMPLE ROWS (first 5)")
    print("=" * 80)
    for i, row in enumerate(leaf_rows[:5], 1):
        print(f"\nRow {i}:")
        print(f"  Path: {row['path'][:100]}")
        print(f"  Value: {row['value'][:60]}")
        print(f"  Description: {row['description'][:60] if row['description'] else 'N/A'}")
        print(f"  Amount: ₱{row['amount']:,.2f}" if row['amount'] else "N/A")
        print(f"  Depth: {row['depth']}")
    
    # Save to Parquet
    parquet_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_leaf_nodes.parquet"
    
    print("\n" + "=" * 80)
    print(f"Saving to Parquet: {parquet_file}")
    
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
        
        # Convert to PyArrow table
        table = pa.table({
            'level_0': [row['level_0'] for row in leaf_rows],
            'level_1': [row['level_1'] for row in leaf_rows],
            'level_2': [row['level_2'] for row in leaf_rows],
            'level_3': [row['level_3'] for row in leaf_rows],
            'level_4': [row['level_4'] for row in leaf_rows],
            'level_5': [row['level_5'] for row in leaf_rows],
            'level_6': [row['level_6'] for row in leaf_rows],
            'level_7': [row['level_7'] for row in leaf_rows],
            'level_8': [row['level_8'] for row in leaf_rows],
            'level_9': [row['level_9'] for row in leaf_rows],
            'level_10': [row['level_10'] for row in leaf_rows],
            'level_11': [row['level_11'] for row in leaf_rows],
            'value': [row['value'] for row in leaf_rows],
            'description': [row['description'] for row in leaf_rows],
            'amount': [float(row['amount']) if row['amount'] is not None else None for row in leaf_rows],
            'depth': [row['depth'] for row in leaf_rows],
            'path': [row['path'] for row in leaf_rows]
        })
        
        # Write to Parquet
        pq.write_table(table, parquet_file)
        
        print(f"✓ Saved {len(leaf_rows):,} rows to Parquet file")
        print(f"  File size: {parquet_file.stat().st_size / (1024 * 1024):.2f} MB")
        
    except ImportError as e:
        print(f"\n⚠️  PyArrow not installed. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'pyarrow', 'pyarrow-parquet'], check=True)
        print("✓ PyArrow installed. Please run script again.")
        return
    
    except Exception as e:
        print(f"\n❌ Error saving to Parquet: {e}")
        return
    
    # Also save to CSV for compatibility
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_leaf_nodes.csv"
    print(f"\nAlso saving to CSV: {csv_file}")
    
    import csv as csv_module
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'level_0', 'level_1', 'level_2', 'level_3', 'level_4',
            'level_5', 'level_6', 'level_7', 'level_8', 'level_9', 'level_10', 'level_11',
            'value', 'description', 'amount', 'depth', 'path'
        ]
        writer = csv_module.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in leaf_rows:
            # Clean up None values for CSV
            csv_row = {k: (v if v is not None else '') for k, v in row.items()}
            writer.writerow(csv_row)
    
    print(f"✓ Saved {len(leaf_rows):,} rows to CSV file")
    
    print("\n" + "=" * 80)
    print("OPTION 1 COMPLETE")
    print("=" * 80)
    print("\nKey Features:")
    print("1. One row per leaf node (no duplicates)")
    print("2. All ancestor values in separate columns (level_0 to level_11)")
    print("3. Preserves full organizational hierarchy in row format")
    print("4. Includes value, description, amount, and depth")
    print("5. Saved as both Parquet and CSV formats")

if __name__ == "__main__":
    main()
