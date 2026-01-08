#!/usr/bin/env python3
"""
Analyze hierarchy by major sections (Level 1 values) up to Level 11.
Per-section analysis with top 100 unique entries and counts_exceeded_flag.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List
from collections import Counter

def load_csv(csv_path: Path) -> List[Dict]:
    """Load CSV table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def looks_like_amount(value: str) -> bool:
    """
    Check if a string looks like an amount/number.
    Amounts typically have digits with commas and possibly decimal points.
    """
    if not value:
        return False
    
    value = value.strip().replace(',', '').replace('₱', '').replace('PHP', '')
    
    # Check if it's a number
    try:
        float(value)
        return True
    except ValueError:
        return False

def analyze_section(rows: List[Dict], section_name: str) -> Dict:
    """
    Analyze a specific section (Level 1 value) up to Level 11.
    
    Args:
        rows: All rows in section
        section_name: Name of the section
    
    Returns:
        Dictionary with section statistics
    """
    # Basic counts
    total_amount = sum(float(r['amount']) for r in rows if r.get('amount') and r['amount'].strip())
    avg_amount = total_amount / len(rows) if rows else 0
    
    # Depth distribution
    depth_counts = Counter(int(r['depth']) for r in rows)
    
    # Level distribution for levels 2-11
    level_counts = {}
    for level in range(2, 12):  # Levels 2-11
        level_counts[level] = Counter()
    
    for row in rows:
        for level in range(2, 12):
            level_key = f'level_{level}'
            value = row.get(level_key, '').strip()
            # Skip if it looks like an amount
            if value and not looks_like_amount(value):
                level_counts[level][value] += 1
    
    # Get top 100 entries per level and add counts_exceeded_flag
    level_categories = {}
    for level in range(2, 12):
        counter = level_counts[level]
        total_unique = len(counter)
        top_entries = counter.most_common(100)
        
        # Add flag if exceeded 100
        level_categories[f'level_{level}_categories'] = {
            'entries': dict(top_entries),
            'counts_exceeded': total_unique > 100,
            'total_unique_count': total_unique,
            'shown_count': len(top_entries)
        }
    
    return {
        'name': section_name,
        'count': len(rows),
        'total_amount': total_amount,
        'avg_amount': avg_amount,
        'depth_distribution': dict(depth_counts),
        **level_categories
    }

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    print("=" * 80)
    print("PER-SECTION HIERARCHY ANALYSIS (LEVELS 1-11)")
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
        
        # Show level categories with exceeded flags
        for level in range(2, 12):
            level_key = f'level_{level}_categories'
            if level_key in stats and stats[level_key]['entries']:
                cat_data = stats[level_key]
                print(f"\nLevel {level} Categories:")
                print(f"  Total unique: {cat_data['total_unique_count']:,} | Shown: {cat_data['shown_count']:,}", end="")
                if cat_data['counts_exceeded']:
                    print(f" | ⚠️  COUNTS EXCEEDED (>{cat_data['total_unique_count'] - 100} hidden)")
                else:
                    print()
                
                # Show top 10 entries
                for j, (value, count) in enumerate(list(cat_data['entries'].items())[:10], 1):
                    pct = count / stats['count'] * 100
                    val_display = value[:40] + "..." if len(value) > 40 else value
                    print(f"  {j:2}. {val_display:<43} {count:>4} ({pct:>5.1f}%)")
    
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
    
    # Summary of counts_exceeded flags
    print("\n" + "=" * 80)
    print("COUNTS EXCEEDED SUMMARY")
    print("=" * 80)
    
    for stats in sections_data:
        exceeded_levels = []
        for level in range(2, 12):
            level_key = f'level_{level}_categories'
            if level_key in stats and stats[level_key]['counts_exceeded']:
                exceeded_levels.append(f"L{level}")
        
        if exceeded_levels:
            name_display = stats['name'][:45] + "..." if len(stats['name']) > 48 else stats['name']
            print(f"{name_display:<50} {', '.join(exceeded_levels)}")
        else:
            name_display = stats['name'][:45] + "..." if len(stats['name']) > 48 else stats['name']
            print(f"{name_display:<50} ✓ All levels ≤ 100 entries")
    
    # Save detailed results to JSON (without top_paths)
    output_file = data_dir / "section_analysis_results.json"
    print(f"\n" + "=" * 80)
    print(f"Saving detailed results to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Results saved!")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Changes:")
    print("1. Analysis extended to Level 11")
    print("2. Amount-like values filtered from categories")
    print("3. Top 100 unique entries per level")
    print("4. counts_exceeded flag added when >100 entries")
    print("5. top_paths field removed from output")

if __name__ == "__main__":
    main()
