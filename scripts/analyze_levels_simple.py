#!/usr/bin/env python3
"""
Simple analysis of unique values at each hierarchy level.
"""

import csv
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

def load_csv(csv_path: Path) -> List[Dict]:
    """Load CSV table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    print("=" * 80)
    print("UNIQUE VALUES AT LEVELS 0-6")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading: {csv_file}")
    rows = load_csv(csv_file)
    print(f"Loaded {len(rows):,} rows")
    
    # Get unique values for each level
    print("\n" + "=" * 80)
    print("UNIQUE VALUES PER LEVEL")
    print("=" * 80)
    
    for level in range(7):  # Levels 0-6
        level_key = f'level_{level}'
        values = set()
        
        for row in rows:
            value = row.get(level_key, '').strip()
            if value:
                values.add(value)
        
        print(f"\nLevel {level}: {len(values):>4} unique values")
        
        if len(values) <= 20:
            # Show all if small
            for value in sorted(values):
                print(f"  - {value}")
        else:
            # Show sample if large
            sorted_values = sorted(values)
            print(f"  Sample (first 15 of {len(values)}):")
            for value in sorted_values[:15]:
                print(f"    - {value}")
            print(f"  ... and {len(values) - 15} more")
    
    # Check for overlaps
    print("\n" + "=" * 80)
    print("CHECKING FOR OVERLAPPING VALUES")
    print("=" * 80)
    
    # Build value to levels mapping
    value_to_levels = defaultdict(list)
    for level in range(7):
        level_key = f'level_{level}'
        values_at_level = set()
        
        for row in rows:
            value = row.get(level_key, '').strip()
            if value:
                values_at_level.add(value)
        
        for value in values_at_level:
            value_to_levels[value].append(level)
    
    # Find overlaps
    overlaps = {k: v for k, v in value_to_levels.items() if len(v) > 1}
    
    if overlaps:
        print(f"\nFound {len(overlaps)} values appearing at multiple levels:\n")
        for value, levels in sorted(overlaps.items(), key=lambda x: len(x[1]), reverse=True):
            level_str = ', '.join([f'L{l}' for l in levels])
            print(f"  '{value}' appears at: {level_str}")
    else:
        print("\n✅ No overlaps - all values are unique to their levels")
    
    # Analyze depth distribution per level
    print("\n" + "=" * 80)
    print("VALUE DEPTH DISTRIBUTION")
    print("=" * 80)
    
    for level in range(7):
        level_key = f'level_{level}'
        value_depths = defaultdict(set)
        
        for row in rows:
            value = row.get(level_key, '').strip()
            if value:
                value_depths[value].add(int(row['depth']))
        
        print(f"\nLevel {level}: Values appear at these depths:")
        sample_count = 0
        for value, depths in sorted(value_depths.items(), key=lambda x: len(x[1]), reverse=True):
            if sample_count < 10:
                depth_str = ', '.join([f'D{d}' for d in sorted(depths)])
                print(f"  '{value[:50]}...' (depths: {depth_str})")
                sample_count += 1
        
        if len(value_depths) > 10:
            print(f"  ... and {len(value_depths) - 10} more values")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
