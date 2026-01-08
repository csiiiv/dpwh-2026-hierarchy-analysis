#!/usr/bin/env python3
"""
Analyze the hierarchy structure to plan for flattening to a table.
"""

import json
from pathlib import Path
from collections import Counter

def analyze_structure(nodes, level=0, stats=None):
    """Analyze hierarchy structure by level."""
    if stats is None:
        stats = {}
    
    for node in nodes:
        value = node['value']
        has_amount = node.get('amount') is not None
        has_children = len(node.get('children', [])) > 0
        has_description = 'description' in node and node['description']
        
        key = f'level_{level}'
        if key not in stats:
            stats[key] = Counter()
        
        stats[key]['total'] += 1
        if has_amount:
            stats[key]['with_amount'] += 1
        if has_children:
            stats[key]['with_children'] += 1
        if has_description:
            stats[key]['with_description'] += 1
        
        # Track value lengths
        stats[key]['total_value_len'] += len(value)
        
        # Track amounts
        if has_amount:
            stats[key]['total_amount'] += node['amount']
        
        # Recursively process children
        analyze_structure(node['children'], level + 1, stats)
    
    return stats

def max_depth(nodes, level=0):
    """Calculate maximum depth of hierarchy."""
    if not nodes:
        return level
    depths = [max_depth(node.get('children', []), level + 1) for node in nodes]
    return max(depths) if depths else level

def get_sample_paths(nodes, level=0, max_samples=5, results=None):
    """Get sample paths through hierarchy."""
    if results is None:
        results = []
    
    if level > 8:  # Don't go too deep
        return results
    
    for i, node in enumerate(nodes):
        if len(results) >= max_samples:
            break
        
        value = node['value'][:60]
        amount = node.get('amount')
        amount_str = f' (₱{amount:,.0f})' if amount else ''
        
        path = f'L{level}: {value}{amount_str}'
        
        if node.get('children'):
            child_path = get_sample_paths([node['children'][0]], level + 1, 1, [])
            if child_path:
                path += ' > ' + child_path[0]
        
        results.append(path)
    
    return results

def main():
    data_dir = Path(__file__).parent.parent / "data"
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("HIERARCHY STRUCTURE ANALYSIS")
    print("=" * 80)
    
    stats = analyze_structure(data)
    
    for level in sorted(stats.keys()):
        s = stats[level]
        print(f"\n{level.upper()}:")
        print(f"  Total nodes:           {s['total']:>8,}")
        print(f"  With amounts:          {s['with_amount']:>8,} ({s['with_amount']/s['total']*100:.1f}%)")
        print(f"  With children:         {s['with_children']:>8,} ({s['with_children']/s['total']*100:.1f}%)")
        print(f"  With descriptions:     {s['with_description']:>8,} ({s['with_description']/s['total']*100:.1f}%)")
        print(f"  Avg value length:      {s['total_value_len']/s['total']:>8.1f} chars")
        if 'total_amount' in s:
            print(f"  Total amount:          ₱{s['total_amount']:>,.2f}")
    
    depth = max_depth(data)
    print(f"\n{'='*80}")
    print(f"Maximum hierarchy depth: {depth} levels")
    print(f"{'='*80}")
    
    print("\nSAMPLE PATHS:")
    print("-" * 80)
    for i, path in enumerate(get_sample_paths(data), 1):
        print(f"{i}. {path}")

if __name__ == "__main__":
    main()
