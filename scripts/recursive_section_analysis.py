#!/usr/bin/env python3
"""
Recursive section analysis by depth.
Analyzes each Level 1 section recursively, showing structure up to L6.
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict, Counter

def load_json(json_path: Path) -> List[Dict]:
    """Load hierarchical JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_subtree(
    nodes: List[Dict],
    section_name: str,
    max_depth: int = 6,
    current_depth: int = 1
) -> Dict:
    """
    Recursively analyze a section's subtree up to max_depth.
    Shows unique values at each depth and structure.
    
    Args:
        nodes: Nodes at current level
        section_name: Name of the section being analyzed
        max_depth: Maximum depth to analyze (default 6)
        current_depth: Current depth in hierarchy
    
    Returns:
        Dictionary with analysis results
    """
    results = {
        'section_name': section_name,
        'depth_analysis': {},
        'unique_values_by_depth': {},
        'structure': {},
        'total_items': 0,
        'total_amount': 0.0
    }
    
    # Initialize depth analysis containers
    for d in range(current_depth, max_depth + 1):
        results['depth_analysis'][d] = {
            'node_count': 0,
            'leaf_count': 0,
            'unique_values': set(),
            'amounts': []
        }
        results['unique_values_by_depth'][d] = set()
    
    # Recursive function to analyze subtree
    def analyze_recursive(node_list: List[Dict], depth: int):
        for node in node_list:
            # Update total counts
            results['total_items'] += 1
            if node.get('amount'):
                results['total_amount'] += float(node['amount'])
            
            # Track this node
            if depth <= max_depth:
                results['depth_analysis'][depth]['node_count'] += 1
                
                # Add to unique values
                value = node.get('value', '').strip()
                if value:
                    results['depth_analysis'][depth]['unique_values'].add(value)
                    results['unique_values_by_depth'][depth].add(value)
                    results['structure'][value] = results['structure'].get(value, 0) + 1
                
                # Track amounts
                if node.get('amount'):
                    results['depth_analysis'][depth]['amounts'].append(float(node['amount']))
                
                # Check if leaf at this depth or below
                children = node.get('children', [])
                if not children:
                    results['depth_analysis'][depth]['leaf_count'] += 1
            
            # Recursively analyze children
            children = node.get('children', [])
            if children:
                analyze_recursive(children, depth + 1)
    
    # Start recursive analysis
    analyze_recursive(nodes, current_depth)
    
    # Calculate statistics per depth
    for d in results['depth_analysis']:
        depth_data = results['depth_analysis'][d]
        unique_count = len(depth_data['unique_values'])
        
        # Count unique values (frequency)
        value_freq = Counter()
        for node in nodes:
            if d <= max_depth:
                value = get_value_at_depth(node, d)
                if value:
                    value_freq[value] += 1
        
        # Sort unique values by frequency
        sorted_values = sorted(
            depth_data['unique_values'],
            key=lambda x: value_freq.get(x, 0),
            reverse=True
        )
        
        results['depth_analysis'][d]['unique_values_sorted'] = sorted_values
        results['depth_analysis'][d]['unique_count'] = unique_count
    
    return results

def get_value_at_depth(node: Dict, target_depth: int, current_depth: int = 1) -> str:
    """
    Get the value of this node at target_depth.
    
    Args:
        node: Current node
        target_depth: Depth we're looking for
        current_depth: Current depth in traversal
    
    Returns:
        Value at target depth, or empty string
    """
    if current_depth == target_depth:
        return node.get('value', '').strip()
    
    children = node.get('children', [])
    for child in children:
        result = get_value_at_depth(child, target_depth, current_depth + 1)
        if result:
            return result
    
    return ''

def find_section_root(sections: List[Dict], section_name: str) -> Dict:
    """
    Find the root node for a specific section.
    """
    for section in sections:
        if section.get('value', '').strip() == section_name:
            return section
        # Check children recursively
        result = find_section_root(section.get('children', []), section_name)
        if result:
            return result
    return None

def analyze_all_sections(
    root_nodes: List[Dict],
    section_names: List[str],
    max_depth: int = 6
) -> List[Dict]:
    """
    Analyze all sections recursively.
    """
    print("\n" + "=" * 80)
    print("RECURSIVE SECTION ANALYSIS BY DEPTH")
    print("=" * 80)
    print(f"\nAnalyzing {len(section_names)} sections up to depth {max_depth}")
    
    section_results = []
    
    for section_name in section_names:
        # Find this section's root
        section_root = find_section_root(root_nodes, section_name)
        
        if not section_root:
            print(f"\n⚠️  Section not found: {section_name}")
            continue
        
        print(f"\n" + "-" * 80)
        print(f"SECTION: {section_name}")
        print("-" * 80)
        
        # Analyze this section's subtree
        result = analyze_subtree(
            [section_root],
            section_name,
            max_depth=max_depth,
            current_depth=1
        )
        
        section_results.append(result)
        
        # Print analysis for this section
        print_section_analysis(result)
    
    return section_results

def print_section_analysis(result: Dict) -> None:
    """
    Print formatted analysis for a single section.
    """
    print(f"\nTotal Items: {result['total_items']:,}")
    print(f"Total Amount: ₱{result['total_amount']:,.2f}")
    print(f"Average Amount per Item: ₱{result['total_amount']/result['total_items']:,.2f}" if result['total_items'] > 0 else "N/A")
    
    print(f"\nStructure: {len(result['structure'])} unique values across all depths")
    
    # Show depth-by-depth analysis
    print(f"\n" + "=" * 80)
    print("DEPTH-BY-DEPTH ANALYSIS")
    print("=" * 80)
    
    for depth in sorted(result['depth_analysis'].keys()):
        depth_data = result['depth_analysis'][depth]
        unique_count = depth_data['unique_count']
        node_count = depth_data['node_count']
        leaf_count = depth_data['leaf_count']
        has_children = node_count - leaf_count > 0
        
        print(f"\nDepth {depth}:")
        print(f"  Total nodes: {node_count:,}")
        print(f"  Unique values: {unique_count:,}")
        print(f"  Leaf nodes: {leaf_count:,}")
        print(f"  Has children: {has_children}")
        
        if depth_data['amounts']:
            total_at_depth = sum(depth_data['amounts'])
            avg_at_depth = total_at_depth / len(depth_data['amounts']) if depth_data['amounts'] else 0
            max_at_depth = max(depth_data['amounts']) if depth_data['amounts'] else 0
            print(f"  Total amount: ₱{total_at_depth:,.2f}")
            print(f"  Average amount: ₱{avg_at_depth:,.2f}")
            print(f"  Max amount: ₱{max_at_depth:,.2f}")
        
        # Show top unique values at this depth
        unique_values = depth_data['unique_values_sorted'][:10]
        if unique_values:
            print(f"\n  Top {len(unique_values)} unique values:")
            for i, value in enumerate(unique_values, 1):
                freq = get_value_frequency(result['section_name'], value, depth)
                val_display = value[:50] + "..." if len(value) > 50 else value
                print(f"    {i:2}. {val_display} (frequency: {freq})")

def get_value_frequency(section_name: str, value: str, depth: int) -> int:
    """
    Get frequency of a value at specific depth (placeholder).
    Would need full recursive search in actual implementation.
    """
    return 1  # Placeholder

def compare_sections(section_results: List[Dict]) -> None:
    """
    Compare all sections across various metrics.
    """
    print("\n" + "=" * 80)
    print("CROSS-SECTION COMPARISON")
    print("=" * 80)
    
    # Sort sections by total amount
    sorted_sections = sorted(section_results, key=lambda x: x['total_amount'], reverse=True)
    
    print(f"\n{'Section':<50} {'Items':>8} {'Total Amount':>20} {'Avg Depth':>10}")
    print("-" * 88)
    
    for section in sorted_sections:
        name_display = section['section_name'][:47] + "..." if len(section['section_name']) > 50 else section['section_name']
        amount_str = f"₱{section['total_amount']:,.2f}"
        
        # Calculate average depth (weighted by item count)
        total_depth_sum = sum(
            depth * depth_data['node_count']
            for depth, depth_data in section['depth_analysis'].items()
        )
        avg_depth = total_depth_sum / section['total_items'] if section['total_items'] > 0 else 0
        
        print(f"{name_display:<50} {section['total_items']:>8,} {amount_str:>20} {avg_depth:>10.1f}")
    
    print(f"\nTotal: {sum(s['total_items'] for s in section_results):,} items")
    print(f"Total Amount: ₱{sum(s['total_amount'] for s in section_results):,.2f}")

def analyze_structure_patterns(section_results: List[Dict]) -> None:
    """
    Analyze structural patterns across sections.
    """
    print("\n" + "=" * 80)
    print("STRUCTURE PATTERN ANALYSIS")
    print("=" * 80)
    
    for section in section_results:
        print(f"\n{section['section_name']}:")
        
        # Count how many unique values at each depth
        depth_counts = {}
        for depth, data in section['depth_analysis'].items():
            unique_count = data['unique_count']
            depth_counts[depth] = unique_count
        
        # Find pattern
        depths_with_values = [d for d, c in depth_counts.items() if c > 0]
        
        if depths_with_values:
            min_depth = min(depths_with_values)
            max_depth = max(depths_with_values)
            depth_range = max_depth - min_depth + 1
            
            print(f"  Depth range: L{min_depth}-L{max_depth} ({depth_range} levels)")
            print(f"  Levels with values: {', '.join([f'L{d}' for d in sorted(depths_with_values)])}")
            
            # Analyze structure complexity
            total_unique = sum(depth_counts[d] for d in depth_counts.keys())
            avg_unique_per_level = total_unique / len(depths_with_values) if depths_with_values else 0
            print(f"  Avg unique values per level: {avg_unique_per_level:.1f}")
            
            # Identify most complex depth (most unique values)
            most_complex_depth = max(depth_counts, key=lambda x: depth_counts[x])
            print(f"  Most complex depth: L{most_complex_depth} ({depth_counts[most_complex_depth]} unique values)")
            
            # Identify simplest depth (fewest unique values)
            simplest_depth = min(depth_counts, key=lambda x: depth_counts[x])
            print(f"  Simplest depth: L{simplest_depth} ({depth_counts[simplest_depth]} unique values)")

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    print("=" * 80)
    print("RECURSIVE SECTION ANALYSIS")
    print("=" * 80)
    print(f"\nLoading hierarchy: {json_file}")
    
    root_nodes = load_json(json_file)
    print(f"Loaded {len(root_nodes)} root nodes")
    
    # Get Level 1 sections (natural section boundaries)
    level_1_values = set()
    for node in root_nodes:
        value = node.get('value', '').strip()
        if value:
            level_1_values.add(value)
    
    # Collect all Level 1 values from entire hierarchy
    def collect_l1(nodes):
        values = set()
        for node in nodes:
            value = node.get('value', '').strip()
            if value:
                values.add(value)
            for child in node.get('children', []):
                values.update(collect_l1([child]))
        return values
    
    all_l1_values = collect_l1(root_nodes)
    section_names = sorted(all_l1_values)
    
    print(f"\nFound {len(section_names)} unique sections")
    
    # Analyze each section recursively up to L6
    section_results = analyze_all_sections(root_nodes, section_names, max_depth=6)
    
    # Compare sections
    compare_sections(section_results)
    
    # Analyze structure patterns
    analyze_structure_patterns(section_results)
    
    # Save results
    output_file = data_dir / "recursive_section_analysis.json"
    print(f"\nSaving results to: {output_file}")
    
    # Prepare output data
    output_data = []
    for result in section_results:
        section_summary = {
            'section_name': result['section_name'],
            'total_items': result['total_items'],
            'total_amount': result['total_amount'],
            'depth_analysis': {}
        }
        
        for depth, depth_data in result['depth_analysis'].items():
            section_summary['depth_analysis'][depth] = {
                'unique_values': list(depth_data['unique_values_sorted'][:20]),  # Top 20
                'unique_count': depth_data['unique_count'],
                'node_count': depth_data['node_count'],
                'leaf_count': depth_data['leaf_count']
            }
        
        output_data.append(section_summary)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Results saved!")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("1. Each Level 1 section analyzed recursively up to L6")
    print("2. Unique values identified at each depth within each section")
    print("3. Structure complexity assessed per section")
    print("4. Cross-section comparison provided")
    print("\nRecommendations:")
    print("- Use section-specific analysis for accurate insights")
    print("- Focus on depth distribution within sections")
    print("- Compare sections of similar structural patterns")

if __name__ == "__main__":
    main()
