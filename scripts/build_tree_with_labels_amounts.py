"""
Build hierarchical tree with labels and amounts from CSV using row hierarchy reference.
Uses Polars for speed and multiprocessing for parallel processing.
"""
import json
import polars as pl
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from typing import Dict, List, Any
import re
from pathlib import Path


def parse_amount(amount_str: str) -> float:
    """Parse amount string to float, handling commas and whitespace."""
    if amount_str is None or not str(amount_str).strip():
        return 0.0
    # Remove commas, quotes, and whitespace, then convert to float
    cleaned = re.sub(r'[\s,\'"]', '', str(amount_str))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def get_deepest_label(row: Dict[str, Any]) -> str:
    """
    Get the deepest label from a row (nearest to amount column).
    Scans columns 0-9 from right to left (9 to 0) and returns first non-empty value.
    """
    for col_idx in range(9, -1, -1):  # Column 9 down to 0
        col_name = f"column_{col_idx}"
        if col_name in row:
            val = row[col_name]
            if val is not None and str(val).strip():
                return str(val).strip()
    return ""


def process_batch(rows_data: List[Dict], chunk_info: Dict) -> Dict[int, Dict]:
    """
    Process a batch of rows to extract labels and amounts.
    Returns a dictionary mapping row number (1-indexed) to {label, amount}.
    """
    result = {}
    for row_data in rows_data:
        row_num = row_data.get('__row_num', 0)
        if row_num == 0:
            continue

        amount = parse_amount(row_data.get('column_10'))
        label = get_deepest_label(row_data)

        result[row_num] = {
            'label': label,
            'amount': amount
        }

    return result


def load_csv_with_polars(csv_path: str, batch_size: int = 50000) -> Dict[int, Dict]:
    """
    Load CSV using Polars and extract labels/amounts in batches with multiprocessing.
    Returns dictionary mapping row number (1-indexed) to {label, amount}.
    """
    print(f"Loading CSV from {csv_path}...")

    # First, get the total number of rows
    df_count = pl.scan_csv(csv_path, has_header=False, quote_char='"', ignore_errors=True)
    total_rows = df_count.select(pl.len()).collect().item()

    print(f"Total rows in CSV: {total_rows}")

    # Read all data with Polars (optimized)
    # Read all columns, rename them for clarity
    df = pl.read_csv(
        csv_path,
        has_header=False,
        quote_char='"',
        ignore_errors=True,
        new_columns=[f"column_{i}" for i in range(24)],
        schema_overrides={f"column_{i}": pl.Utf8 for i in range(24)}
    )

    # Add row number (1-indexed to match Excel row numbers)
    df = df.with_row_index(name="__row_num", offset=1)

    # Filter rows that have data in columns 0-10 (skip empty rows)
    df = df.filter(
        pl.any_horizontal([pl.col(f"column_{i}").is_not_null() for i in range(11)])
    )

    print(f"Rows with data: {len(df)}")

    # Convert to dict for processing
    rows_data = df.to_dicts()

    # Process in batches with multiprocessing
    row_data = {}
    num_batches = (len(rows_data) + batch_size - 1) // batch_size

    print(f"Processing in {num_batches} batches of size ~{batch_size}...")

    with ProcessPoolExecutor(max_workers=None) as executor:
        futures = []

        for batch_idx in range(num_batches):
            start = batch_idx * batch_size
            end = min((batch_idx + 1) * batch_size, len(rows_data))
            batch = rows_data[start:end]

            chunk_info = {
                'batch_idx': batch_idx,
                'start': start,
                'end': end,
                'total_rows': len(rows_data)
            }

            future = executor.submit(process_batch, batch, chunk_info)
            futures.append(future)

        # Collect results
        for future in as_completed(futures):
            batch_result = future.result()
            row_data.update(batch_result)
            if len(row_data) % 10000 == 0:
                print(f"Processed {len(row_data)} rows...")

    print(f"Finished processing {len(row_data)} rows with labels/amounts")
    return row_data


def build_tree_from_hierarchy(
    hierarchy: Dict[str, Any],
    row_data: Dict[int, Dict]
) -> Dict[str, Any]:
    """
    Build tree structure by traversing hierarchy and adding labels/amounts from row_data.
    Filters out nodes with empty labels.
    """
    def build_node(node: Dict[str, Any]) -> Dict[str, Any] | None:
        row_num = node['row']
        data = row_data.get(row_num, {})
        label = data.get('label', '')

        # Filter out nodes with empty labels
        if not label or not str(label).strip():
            return None

        result = {
            'row': row_num,
            'label': label,
            'amount': data.get('amount', 0.0),
            'children': []
        }

        # Recursively build children
        for child in node['children']:
            child_result = build_node(child)
            if child_result is not None:  # Only add non-None children
                result['children'].append(child_result)

        return result

    # Build the tree, filtering out None results
    tree = []
    for root in hierarchy['hierarchy_tree']:
        root_result = build_node(root)
        if root_result is not None:
            tree.append(root_result)

    return {
        'hierarchy_tree': tree
    }


def save_tree(tree: Dict[str, Any], output_path: str):
    """Save tree structure to JSON file."""
    print(f"Saving tree to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(tree, f, indent=2)
    print(f"Tree saved successfully!")


def calculate_tree_stats(tree: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate statistics about the tree."""
    stats = {
        'total_nodes': 0,
        'total_amount': 0.0,
        'nodes_with_labels': 0,
        'nodes_with_amounts': 0,
        'leaf_nodes': 0
    }

    def count_nodes(node: Dict[str, Any], is_leaf: bool = False):
        stats['total_nodes'] += 1
        stats['total_amount'] += node.get('amount', 0.0)

        # All nodes should have labels now (filtered out empties)
        stats['nodes_with_labels'] += 1

        if node.get('amount', 0.0) != 0.0:
            stats['nodes_with_amounts'] += 1

        if is_leaf:
            stats['leaf_nodes'] += 1

        for child in node.get('children', []):
            is_child_leaf = len(child.get('children', [])) == 0
            count_nodes(child, is_child_leaf)

    for root in tree.get('hierarchy_tree', []):
        is_root_leaf = len(root.get('children', [])) == 0
        count_nodes(root, is_root_leaf)

    return stats


def main():
    """Main execution function."""
    base_path = Path('/home/temp/_CODE/DPWH_2026_GAA')

    # File paths
    csv_path = base_path / 'data' / 'FY 2026_DPWH DETAILS ENROLLED COPY (Final).csv'
    hierarchy_path = base_path / 'data' / 'row_hierarchy.json'
    output_path = base_path / 'data' / 'hierarchical_tree_with_labels_and_amounts.json'

    print("=" * 70)
    print("Building Hierarchical Tree with Labels and Amounts")
    print("=" * 70)

    # Step 1: Load row hierarchy
    print("\nStep 1: Loading row hierarchy...")
    with open(hierarchy_path, 'r') as f:
        hierarchy = json.load(f)
    print(f"Loaded hierarchy with {len(hierarchy['hierarchy_tree'])} root nodes")

    # Step 2: Load CSV and extract labels/amounts
    print("\nStep 2: Loading CSV and extracting labels/amounts...")
    row_data = load_csv_with_polars(str(csv_path), batch_size=50000)

    # Step 3: Build tree
    print("\nStep 3: Building tree from hierarchy...")
    tree = build_tree_from_hierarchy(hierarchy, row_data)
    print(f"Tree built with {len(tree['hierarchy_tree'])} root nodes")

    # Step 4: Calculate statistics
    print("\nStep 4: Calculating tree statistics...")
    stats = calculate_tree_stats(tree)
    print(f"\nTree Statistics:")
    print(f"  Total nodes: {stats['total_nodes']:,}")
    print(f"  Total amount: {stats['total_amount']:,.2f}")
    print(f"  Nodes with labels: {stats['nodes_with_labels']:,}")
    print(f"  Nodes with amounts: {stats['nodes_with_amounts']:,}")
    print(f"  Leaf nodes: {stats['leaf_nodes']:,}")

    # Step 5: Save tree
    print("\nStep 5: Saving tree...")
    save_tree(tree, str(output_path))

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)


if __name__ == '__main__':
    main()
