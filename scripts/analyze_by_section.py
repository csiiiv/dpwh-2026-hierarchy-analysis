#!/usr/bin/env python3
"""
Analyze hierarchy by major sections (Level 1 values).
Per-section analysis to handle hierarchical flexibility and overlaps.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

def load_csv(csv_path: Path) -> List[Dict]:
    """Load CSV table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze_section(rows: List[Dict], section_name: str) -> Dict:
    """
    Analyze a specific section (Level 1 value).
    
    Args:
        rows: All rows in section
        section_name: Name of the section
    
    Returns:
        Dictionary with section statistics
    """
    # Basic counts
    total_amount = sum(float(r['amount']) for r in rows if r.get('amount'))
    avg_amount = total_amount / len(rows) if rows else 0
    
    # Depth distribution
    depth_counts = Counter(int(r['depth']) for r in rows)
    
    # Level distribution (showing where values appear)
    level_2_counts = Counter()
    level_3_counts = Counter()
    level_4_counts = Counter()
    level_5_counts = Counter()
    level_6_counts = Counter()
    
    for row in rows:
        for level in [2, 3, 4, 5, 6]:
            level_key = f'level_{level}'
            value = row.get(level_key, '').strip()
            if value:
                if level == 2:
                    level_2_counts[value] += 1
                elif level == 3:
                    level_3_counts[value] += 1
                elif level == 4:
                    level_4_counts[value] += 1
                elif level == 5:
                    level_5_counts[value] += 1
                elif level == 6:
                    level_6_counts[value] += 1
    
    # Top paths by amount
    top_paths = []
    for row in rows:
        if row.get('amount'):
            top_paths.append((row['full_path'], float(row['amount']), int(row['depth'])))
    
    top_paths.sort(key=lambda x: x[1], reverse=True)
    top_paths = top_paths[:20]
    
    return {
        'name': section_name,
        'count': len(rows),
        'total_amount': total_amount,
        'avg_amount': avg_amount,
        'depth_distribution': dict(depth_counts),
        'level_2_categories': dict(level_2_counts.most_common(10)),
        'level_3_categories': dict(level_3_counts.most_common(10)),
        'level_4_categories': dict(level_4_counts.most_common(10)),
        'level_5_categories': dict(level_5_counts.most_common(10)),
        'level_6_categories': dict(level_6_counts.most_common(10)),
        'top_paths': top_paths
    }

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    print("=" * 80)
    print("PER-SECTION HIERARCHY ANALYSIS")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading table from: {csv_file}")
    rows = load_csv(csv_file)
    print(f"Loaded {len(rows):,} rows")
    
    # Get all unique Level 1 values (sections)
    level_1_values = set()
    for row in rows:
        value = row.get('level_1', '').strip()
        if value:
            level_1_values.add(value)
    
    sections = sorted(level_1_values)
    print(f"\nFound {len(sections)} major sections (Level 1)")
    
    # Analyze each section
    sections_data = []
    for section in sections:
        section_rows = [r for r in rows if r.get('level_1', '').strip() == section]
        section_stats = analyze_section(section_rows, section)
        sections_data.append(section_stats)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SECTIONS SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Section':<50} {'Items':>8} {'Total Amount':>25}")
    print("-" * 83)
    for stats in sections_data:
        name_display = stats['name'][:47] + "..." if len(stats['name']) > 50 else stats['name']
        amount_str = f"₱{stats['total_amount']:,.2f}"
        print(f"{name_display:<50} {stats['count']:>8} {amount_str:>25}")
    
    # Detailed analysis for each section
    for i, stats in enumerate(sections_data, 1):
        print("\n" + "=" * 80)
        print(f"SECTION {i}: {stats['name']}")
        print("=" * 80)
        
        print(f"\nItems: {stats['count']:,}")
        print(f"Total Amount: ₱{stats['total_amount']:,.2f}")
        print(f"Average Amount: ₱{stats['avg_amount']:,.2f}")
        
        print("\nDepth Distribution:")
        for depth in sorted(stats['depth_distribution'].keys()):
            count = stats['depth_distribution'][depth]
            pct = count / stats['count'] * 100
            print(f"  Depth {depth}: {count:>6,} ({pct:>5.1f}%)")
        
        if stats['level_2_categories']:
            print("\nTop Level 2 Categories:")
            for value, count in list(stats['level_2_categories'].items())[:5]:
                pct = count / stats['count'] * 100
                val_display = value[:40] + "..." if len(value) > 40 else value
                print(f"  {val_display:<43} {count:>4} ({pct:>5.1f}%)")
        
        if stats['level_3_categories']:
            print("\nTop Level 3 Categories:")
            for value, count in list(stats['level_3_categories'].items())[:5]:
                pct = count / stats['count'] * 100
                val_display = value[:40] + "..." if len(value) > 40 else value
                print(f"  {val_display:<43} {count:>4} ({pct:>5.1f}%)")
        
        if stats['top_paths']:
            print("\nTop 10 Paths by Amount:")
            for j, (path, amount, depth) in enumerate(stats['top_paths'][:10], 1):
                path_display = path[:70] + "..." if len(path) > 70 else path
                print(f"  {j:2}. {path_display}")
                print(f"      Amount: ₱{amount:,.2f} | Depth: {depth}")
    
    # Cross-section comparison
    print("\n" + "=" * 80)
    print("CROSS-SECTION COMPARISON")
    print("=" * 80)
    
    print(f"\n{'Section':<50} {'% of Total':>12} {'Avg Depth':>10}")
    print("-" * 72)
    
    total_all = sum(s['count'] for s in sections_data)
    total_amount_all = sum(s['total_amount'] for s in sections_data)
    
    for stats in sections_data:
        name_display = stats['name'][:47] + "..." if len(stats['name']) > 50 else stats['name']
        pct = stats['count'] / total_all * 100
        avg_depth = sum(d * c for d, c in stats['depth_distribution'].items()) / stats['count']
        print(f"{name_display:<50} {pct:>11.1f}% {avg_depth:>10.1f}")
    
    print(f"\nTotal: {total_all:,} items")
    print(f"Total Amount: ₱{total_amount_all:,.2f}")
    
    # Save detailed results to JSON
    output_file = data_dir / "section_analysis_results.json"
    print(f"\n" + "=" * 80)
    print(f"Saving detailed results to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Results saved!")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
