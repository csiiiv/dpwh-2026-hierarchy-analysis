#!/usr/bin/env python3
"""
Analyze all unique values at each hierarchy level to identify sections and overlaps.
Shows complete distribution of values across levels 0-6.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter

def load_csv(csv_path: Path) -> List[Dict]:
    """Load CSV table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def get_unique_values_by_level(rows: List[Dict], max_level: int = 6) -> Dict[int, Set[str]]:
    """
    Get all unique values for each level up to max_level.
    
    Returns:
        Dictionary mapping level to set of unique values
    """
    level_values = {}
    
    for level in range(max_level + 1):
        level_key = f'level_{level}'
        values = set()
        
        for row in rows:
            value = row.get(level_key, '').strip()
            if value:
                values.add(value)
        
        level_values[level] = values
    
    return level_values

def analyze_level_distribution(rows: List[Dict], level: int) -> List[Tuple[str, int, float]]:
    """
    Analyze distribution of values at a specific level.
    Shows where each value appears in the hierarchy path.
    
    Returns:
        List of (value, count, total_amount) tuples
    """
    level_key = f'level_{level}'
    value_stats = defaultdict(lambda: {'count': 0, 'amount': 0.0, 'contexts': defaultdict(int)})
    
    for row in rows:
        value = row.get(level_key, '').strip()
        if not value:
            continue
        
        value_stats[value]['count'] += 1
        
        # Track amount
        if row.get('amount'):
            try:
                value_stats[value]['amount'] += float(row['amount'])
            except (ValueError, TypeError):
                pass
        
        # Track context - what values appear at the next level
        next_level_key = f'level_{level + 1}'
        next_level_value = row.get(next_level_key, '').strip()
        if next_level_value:
            value_stats[value]['contexts'][next_level_value] += 1
    
    # Convert to list
    results = []
    for value, stats in value_stats.items():
        results.append({
            'value': value,
            'count': stats['count'],
            'amount': stats['amount'],
            'contexts': dict(stats['contexts']),
            'context_count': len(stats['contexts']),
            'top_context': max(stats['contexts'].items(), key=lambda x: x[1])[0] if stats['contexts'] else None
        })
    
    # Sort by count
    results.sort(key=lambda x: x['count'], reverse=True)
    
    return results

def detect_sections(rows: List[Dict], level: int) -> List[Dict]:
    """
    Detect potential sections based on value distribution patterns.
    Sections are identified by:
    - High-frequency values that appear as parent to many children
    - Values that appear at specific depth positions
    """
    level_key = f'level_{level}'
    
    # Get all values at this level
    value_counts = Counter()
    value_depths = defaultdict(set)
    value_children = defaultdict(set)
    
    for row in rows:
        value = row.get(level_key, '').strip()
        if value:
            value_counts[value] += 1
            value_depths[int(row['depth'])].add(value)
            
            # Track children at next level
            next_level_key = f'level_{level + 1}'
            child = row.get(next_level_key, '').strip()
            if child:
                value_children[value].add(child)
    
    # Identify potential section headers
    # Section headers typically:
    # - Appear at shallower depths
    # - Have many unique children
    # - Are high-frequency
    
    sections = []
    for value in sorted(value_counts.keys(), key=lambda x: value_counts[x], reverse=True):
        stats = {
            'value': value,
            'count': value_counts[value],
            'depths': sorted(list(value_depths[value])),
            'child_count': len(value_children[value]),
            'unique_children': len(value_children[value])
        }
        
        # Score this as a potential section header
        # Higher score = more likely to be a section header
        score = (
            stats['count'] * 0.3 +  # High frequency
            stats['unique_children'] * 0.5 +  # Many unique children
            (8 - min(stats['depths'])) * 0.2  # Appears early in hierarchy
        )
        
        stats['score'] = score
        sections.append(stats)
    
    sections.sort(key=lambda x: x['score'], reverse=True)
    
    return sections

def analyze_level_overlap(level_values: Dict[int, Set[str]]) -> None:
    """
    Check if values appear at multiple levels (indicates inconsistency).
    """
    print("\n" + "=" * 80)
    print("LEVEL OVERLAP ANALYSIS")
    print("=" * 80)
    
    all_values = {}
    for level, values in level_values.items():
        for value in values:
            if value not in all_values:
                all_values[value] = []
            all_values[value].append(level)
    
    # Find values that appear at multiple levels
    overlapping = {k: v for k, v in all_values.items() if len(v) > 1}
    
    if overlapping:
        print(f"\n⚠️  Found {len(overlapping)} values appearing at MULTIPLE LEVELS:")
        print("\nValue (appears at levels):")
        for value in sorted(overlapping.keys(), key=lambda x: len(overlapping[x]), reverse=True):
            levels_str = ', '.join(f"L{l}" for l in overlapping[value])
            print(f"  '{value}' → {levels_str}")
    else:
        print("\n✅ No overlapping values found - hierarchy levels are distinct")
    
    return len(overlapping)

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
    print("COMPREHENSIVE LEVELS 0-6 ANALYSIS")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading table from: {csv_file}")
    rows = load_csv(csv_file)
    print(f"Loaded {len(rows):,} rows")
    
    # Get unique values for levels 0-6
    print("\nExtracting unique values for levels 0-6...")
    level_values = get_unique_values_by_level(rows, max_level=6)
    
    # Show summary for each level
    print("\n" + "=" * 80)
    print("UNIQUE VALUES SUMMARY")
    print("=" * 80)
    
    for level in sorted(level_values.keys()):
        values = level_values[level]
        print(f"\nLevel {level}: {len(values):>5} unique values")
    
    # Check for overlaps
    overlap_count = analyze_level_overlap(level_values)
    
    # Detailed analysis for each level
    for level in sorted(level_values.keys()):
        print("\n" + "=" * 80)
        print(f"LEVEL {level} - DETAILED ANALYSIS")
        print("=" * 80)
        
        values = sorted(level_values[level])
        print(f"\nTotal unique values: {len(values)}")
        print("\nAll unique values:")
        for i, value in enumerate(values, 1):
            print(f"  {i:3}. {value}")
    
    # Detect sections at different levels
    print("\n" + "=" * 80)
    print("SECTION DETECTION ANALYSIS")
    print("=" * 80)
    
    for level in range(1, 6):  # Check levels 1-5
        print(f"\nLevel {level} - Potential Section Headers:")
        sections = detect_sections(rows, level)
        
        if sections:
            print(f"\n{'Value':<60} {'Count':>6} {'Children':>8} {'Score':>6}")
            print("-" * 80)
            for section in sections[:20]:  # Show top 20
                print(f"{section['value']:<60} {section['count']:>6} {section['unique_children']:>8} {section['score']:>6.1f}")
            if len(sections) > 20:
                print(f"\n... and {len(sections) - 20} more potential sections")
        else:
            print("  No clear section headers detected")
    
    # Analyze value distribution and contexts
    print("\n" + "=" * 80)
    print("VALUE CONTEXT ANALYSIS")
    print("=" * 80)
    
    for level in range(1, 6):
        print(f"\nLevel {level} - Top 10 values with their contexts:")
        analysis = analyze_level_distribution(rows, level)
        
        if analysis:
            print(f"\n{'Value':<50} {'Count':>6} {'Amount':>18} {'Contexts':>8}")
            print("-" * 82)
            for item in analysis[:10]:
                val_display = item['value'][:47] + "..." if len(item['value']) > 50 else item['value']
                print(f"{val_display:<50} {item['count']:>6} {format_amount(item['amount']):>18} {item['context_count']:>8}")
                
                # Show top context if relevant
                if item['top_context'] and item['context_count'] > 1:
                    print(f"  → Top context: {item['top_context']} ({item['contexts'][item['top_context']]} children)")
    
    # Summary recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR SECTION CUTS")
    print("=" * 80)
    
    print("\nBased on analysis, here are recommended section cut points:")
    print("\n1. Analyze by Level 1 values (major budget categories)")
    print("   These represent the highest-level divisions:")
    level_1_values = sorted(level_values[1])
    for i, val in enumerate(level_1_values, 1):
        print(f"      {i}. {val}")
    
    print("\n2. Analyze by Level 2-3 (organizational units)")
    print("   These represent major functional divisions")
    
    print("\n3. Consider grouping by Level 4 (program categories)")
    print(f"   {len(level_values[4])} program categories identified")
    
    print("\n4. For geographic analysis, use Level 5-6")
    print(f"   {len(level_values[5])} regional units at Level 5")
    print(f"   {len(level_values[6])} district units at Level 6")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nOverlapping values found: {overlap_count}")
    print("If overlaps exist, consider section-based analysis rather than level-based")

if __name__ == "__main__":
    main()
