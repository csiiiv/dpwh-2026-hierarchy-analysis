#!/usr/bin/env python3
"""
Analyze flattened table to identify hierarchy structures and patterns.
Groups data by different hierarchy levels to reveal organizational patterns.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

def load_table(csv_path: Path) -> List[Dict]:
    """Load flattened table from CSV."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze_by_level(
    rows: List[Dict],
    levels: List[int],
    min_group_size: int = 5
) -> List[Tuple[str, int, float]]:
    """
    Group and aggregate by specified hierarchy levels.
    
    Args:
        rows: Table rows
        levels: List of level numbers to group by (e.g., [5, 6] for levels 5-6)
        min_group_size: Minimum number of items to include in results
    
    Returns:
        List of (key, count, total_amount) tuples sorted by amount
    """
    groups = defaultdict(lambda: {'count': 0, 'amount': 0.0})
    
    for row in rows:
        # Build group key from specified levels
        key_parts = []
        for level in levels:
            level_key = f'level_{level}'
            if row.get(level_key) and row[level_key].strip():
                key_parts.append(row[level_key].strip())
        
        if not key_parts:
            continue
        
        key = ' > '.join(key_parts)
        
        groups[key]['count'] += 1
        if row.get('amount'):
            try:
                groups[key]['amount'] += float(row['amount'])
            except (ValueError, TypeError):
                pass
    
    # Convert to list and filter by min_group_size
    results = [
        (key, data['count'], data['amount'])
        for key, data in groups.items()
        if data['count'] >= min_group_size
    ]
    
    # Sort by amount (descending)
    results.sort(key=lambda x: x[2], reverse=True)
    
    return results

def analyze_depth_distribution(rows: List[Dict]) -> Dict[int, Dict]:
    """
    Analyze distribution of items at each depth.
    
    Returns:
        Dictionary with statistics per depth level
    """
    depth_stats = {}
    
    for row in rows:
        depth = int(row['depth'])
        
        if depth not in depth_stats:
            depth_stats[depth] = {
                'count': 0,
                'total_amount': 0.0,
                'values': []
            }
        
        depth_stats[depth]['count'] += 1
        if row.get('amount'):
            try:
                amt = float(row['amount'])
                depth_stats[depth]['total_amount'] += amt
                depth_stats[depth]['values'].append(amt)
            except (ValueError, TypeError):
                pass
    
    # Calculate statistics for each depth
    for depth, stats in depth_stats.items():
        values = stats['values']
        if values:
            values.sort()
            stats['min'] = min(values)
            stats['max'] = max(values)
            stats['median'] = values[len(values) // 2]
            stats['avg'] = sum(values) / len(values)
        else:
            stats['min'] = 0
            stats['max'] = 0
            stats['median'] = 0
            stats['avg'] = 0
    
    return depth_stats

def find_top_paths(rows: List[Dict], n: int = 20) -> List[Tuple]:
    """
    Find top paths by amount.
    
    Returns:
        List of (path, amount, depth) tuples
    """
    paths = []
    for row in rows:
        if row.get('amount'):
            try:
                amt = float(row['amount'])
                paths.append((row['full_path'], amt, int(row['depth'])))
            except (ValueError, TypeError):
                pass
    
    paths.sort(key=lambda x: x[1], reverse=True)
    return paths[:n]

def analyze_level_values(rows: List[Dict], level: int, min_group_size: int = 1) -> List[Tuple[str, int, float]]:
    """
    Analyze unique values at a specific level.
    
    Args:
        rows: Table rows
        level: Hierarchy level to analyze
        min_group_size: Minimum count to include in results
    
    Returns:
        List of (value, count, total_amount) tuples
    """
    level_key = f'level_{level}'
    values = defaultdict(lambda: {'count': 0, 'amount': 0.0})
    
    for row in rows:
        value = row.get(level_key, '').strip()
        if not value:
            continue
        
        values[value]['count'] += 1
        if row.get('amount'):
            try:
                values[value]['amount'] += float(row['amount'])
            except (ValueError, TypeError):
                pass
    
    # Convert to list and filter by min_group_size
    results = [
        (value, data['count'], data['amount'])
        for value, data in values.items()
        if data['count'] >= min_group_size
    ]
    results.sort(key=lambda x: x[2], reverse=True)
    
    return results

def print_section(title: str, content: str):
    """Print a formatted section."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(content)

def format_amount(amt: float) -> str:
    """Format amount as Philippine Peso."""
    return f"₱{amt:,.2f}"

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    print("=" * 80)
    print("HIERARCHY TABLE PATTERN ANALYSIS")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading table from: {csv_file}")
    rows = load_table(csv_file)
    print(f"Loaded {len(rows):,} rows")
    
    # Calculate total
    total_amount = sum(float(r['amount']) for r in rows if r.get('amount'))
    print(f"Total amount: {format_amount(total_amount)}")
    
    # 1. Depth distribution analysis
    depth_stats = analyze_depth_distribution(rows)
    
    depth_content = []
    for depth in sorted(depth_stats.keys()):
        stats = depth_stats[depth]
        depth_content.append(
            f"\nDepth {depth}:\n"
            f"  Items:      {stats['count']:>8,} ({stats['count']/len(rows)*100:>5.1f}%)\n"
            f"  Total:      {format_amount(stats['total_amount'])}\n"
            f"  Average:     {format_amount(stats['avg'])}\n"
            f"  Median:      {format_amount(stats['median'])}\n"
            f"  Min:         {format_amount(stats['min'])}\n"
            f"  Max:         {format_amount(stats['max'])}"
        )
    
    print_section("DEPTH DISTRIBUTION ANALYSIS", "\n".join(depth_content))
    
    # 2. Analyze by Level 5 (likely regions/organizations)
    print_section("ANALYSIS BY LEVEL 5 (Regions/Districts)", "")
    level_5_analysis = analyze_level_values(rows, 5, min_group_size=3)
    
    print(f"\n{'Value':<60} {'Count':>8} {'Total Amount':>20}")
    print("-" * 88)
    for value, count, amount in level_5_analysis[:15]:
        print(f"{value[:60]:<60} {count:>8} {format_amount(amount):>20}")
    
    if len(level_5_analysis) > 15:
        print(f"\n... and {len(level_5_analysis) - 15} more items")
    
    # 3. Analyze by Level 6 (more specific)
    print_section("ANALYSIS BY LEVEL 6 (Detailed Breakdown)", "")
    level_6_analysis = analyze_level_values(rows, 6, min_group_size=5)
    
    print(f"\n{'Value':<60} {'Count':>8} {'Total Amount':>20}")
    print("-" * 88)
    for value, count, amount in level_6_analysis[:15]:
        print(f"{value[:60]:<60} {count:>8} {format_amount(amount):>20}")
    
    if len(level_6_analysis) > 15:
        print(f"\n... and {len(level_6_analysis) - 15} more items")
    
    # 4. Combined levels analysis (Level 5-6)
    print_section("ANALYSIS BY COMBINED LEVELS 5-6", "")
    combined_analysis = analyze_by_level(rows, [5, 6], min_group_size=3)
    
    print(f"\n{'Combined Level 5-6':<60} {'Count':>8} {'Total Amount':>20}")
    print("-" * 88)
    for key, count, amount in combined_analysis[:15]:
        print(f"{key[:60]:<60} {count:>8} {format_amount(amount):>20}")
    
    if len(combined_analysis) > 15:
        print(f"\n... and {len(combined_analysis) - 15} more items")
    
    # 5. Top paths
    print_section("TOP 20 PATHS BY AMOUNT", "")
    top_paths = find_top_paths(rows, 20)
    
    for i, (path, amount, depth) in enumerate(top_paths, 1):
        print(f"{i:2}. {path[:100]}")
        print(f"    Amount: {format_amount(amount)} | Depth: {depth}")
        if i < 20:
            print()
    
    # 6. Level 4 analysis (program categories)
    print_section("ANALYSIS BY LEVEL 4 (Program Categories)", "")
    level_4_analysis = analyze_level_values(rows, 4, min_group_size=10)
    
    print(f"\n{'Value':<60} {'Count':>8} {'Total Amount':>20}")
    print("-" * 88)
    for value, count, amount in level_4_analysis:
        print(f"{value[:60]:<60} {count:>8} {format_amount(amount):>20}")
    
    # 7. Summary statistics
    print_section("SUMMARY", "")
    print(f"Total items analyzed:       {len(rows):,}")
    print(f"Total amount:              {format_amount(total_amount)}")
    print(f"Average amount per item:    {format_amount(total_amount / len(rows))}")
    print(f"\nLevel 5 categories:        {len(level_5_analysis)}")
    print(f"Level 6 categories:        {len(level_6_analysis)}")
    print(f"Level 4 categories:        {len(level_4_analysis)}")
    print(f"Combined L5-L6 paths:      {len(combined_analysis)}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
