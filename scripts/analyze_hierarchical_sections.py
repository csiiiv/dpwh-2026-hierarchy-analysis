#!/usr/bin/env python3
"""
Analyze hierarchical sections by examining natural parent-child transitions.
Identifies section boundaries based on depth changes in the original JSON hierarchy.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

def load_json(json_path: Path) -> List[Dict]:
    """Load hierarchical JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_section_depths(nodes: List[Dict], current_depth: int = 0) -> List[Dict]:
    """
    Recursively analyze depth changes in hierarchy.
    Identifies where sections transition based on depth patterns.
    
    Args:
        nodes: List of nodes at current level
        current_depth: Current depth in hierarchy
    
    Returns:
        List of nodes with depth information
    """
    results = []
    
    for node in nodes:
        # Get the actual depth of this node
        node_depth = current_depth
        node_data = {
            'value': node.get('value', ''),
            'amount': node.get('amount'),
            'has_children': len(node.get('children', [])) > 0,
            'depth': node_depth,
            'child_depths': [],
            'path': []
        }
        
        # Analyze children
        if node.get('children'):
            child_depths = set()
            for child in node['children']:
                child_analysis = analyze_section_depths([child], current_depth + 1)
                results.extend(child_analysis)
                
                # Track depth of this child's leaves
                if child_analysis:
                    max_child_depth = max(c['depth'] for c in child_analysis)
                    child_depths.add(max_child_depth)
            
            node_data['child_depths'] = sorted(list(child_depths))
            
            # Build path to deepest leaf
            if child_depths:
                deepest_depth = max(child_depths)
                node_data['max_leaf_depth'] = deepest_depth
                node_data['depth_span'] = deepest_depth - node_depth
            else:
                node_data['max_leaf_depth'] = node_depth
                node_data['depth_span'] = 0
        
        results.append(node_data)
    
    return results

def identify_section_transitions(nodes: List[Dict]) -> List[Dict]:
    """
    Identify natural section transitions in the hierarchy.
    A section transition occurs when:
    - A node has no siblings (single path through that level)
    - A node's children show significant depth variation
    - A node represents a major budget category
    """
    transitions = []
    
    # Analyze the entire tree
    all_nodes = analyze_section_depths(nodes)
    
    # Group by depth
    nodes_by_depth = defaultdict(list)
    for node in all_nodes:
        nodes_by_depth[node['depth']].append(node)
    
    print("\n" + "=" * 80)
    print("HIERARCHY DEPTH ANALYSIS")
    print("=" * 80)
    
    for depth in sorted(nodes_by_depth.keys()):
        nodes_at_depth = nodes_by_depth[depth]
        print(f"\nDepth {depth}: {len(nodes_at_depth)} nodes")
        
        # Count nodes with children vs without
        with_children = sum(1 for n in nodes_at_depth if n['has_children'])
        without_children = sum(1 for n in nodes_at_depth if not n['has_children'])
        
        print(f"  With children: {with_children}")
        print(f"  Without children (leaves): {without_children}")
        
        # Analyze depth spans
        depth_spans = [n['depth_span'] for n in nodes_at_depth if 'depth_span' in n]
        if depth_spans:
            avg_span = sum(depth_spans) / len(depth_spans)
            max_span = max(depth_spans)
            print(f"  Avg depth span to leaves: {avg_span:.1f}")
            print(f"  Max depth span to leaves: {max_span}")
        
        # Show sample nodes at this depth
        print(f"  Sample nodes:")
        for i, node in enumerate(nodes_at_depth[:5], 1):
            has_leaves = ', '.join([str(d) for d in node.get('child_depths', [])])
            val_display = node['value'][:40] + "..." if len(node['value']) > 40 else node['value']
            print(f"    {i}. {val_display}")
            if node['amount']:
                print(f"       Amount: ₱{node['amount']:,.0f}")
            if node.get('max_leaf_depth') is not None:
                print(f"       Leaves at depths: {has_leaves}")
                print(f"       Span to leaves: {node['depth_span']}")
    
    return all_nodes

def find_major_sections(nodes: List[Dict]) -> List[Dict]:
    """
    Identify major sections by analyzing depth transitions.
    Major sections are identified by:
    - Nodes with depth > 2 (strategic categories)
    - Nodes with significant child depth variation
    - Nodes representing large budget allocations
    """
    all_nodes = analyze_section_depths(nodes)
    
    print("\n" + "=" * 80)
    print("IDENTIFYING MAJOR SECTIONS")
    print("=" * 80)
    
    # Section candidates based on depth 1-3 (strategic levels)
    section_candidates = [n for n in all_nodes if n['depth'] <= 3]
    
    # Also include nodes that are "branching points" - nodes with many children
    # or nodes where child depth varies significantly
    branching_nodes = []
    for node in all_nodes:
        if node['has_children']:
            child_depths = node.get('child_depths', [])
            if child_depths:
                # Check if children go to multiple different depths
                unique_depths = set(child_depths)
                if len(unique_depths) > 1:
                    # This node has children at different depths
                    node['branching_factor'] = len(unique_depths)
                    branching_nodes.append(node)
    
    print(f"\nFound {len(section_candidates)} strategic nodes (depth 0-3)")
    print(f"Found {len(branching_nodes)} branching nodes (children at multiple depths)")
    
    sections = []
    
    # Combine strategic nodes and branching nodes
    # Use tuple of (depth, value) as unique identifier to avoid dict hashability issue
    all_candidates = section_candidates + branching_nodes
    
    # Deduplicate by (depth, value) pair
    unique_pairs = {}
    for node in all_candidates:
        key = (node['depth'], node['value'])
        if key not in unique_pairs:
            unique_pairs[key] = node
    
    unique_candidates = list(unique_pairs.values())
    unique_candidates.sort(key=lambda x: x['depth'])
    
    print(f"\nTotal unique section candidates: {len(unique_candidates)}")
    
    for i, node in enumerate(unique_candidates, 1):
        section_info = {
            'id': i,
            'value': node['value'],
            'depth': node['depth'],
            'amount': node['amount'],
            'has_children': node['has_children'],
            'branching_factor': node.get('branching_factor', 1),
            'max_leaf_depth': node.get('max_leaf_depth', node['depth']),
            'depth_span': node.get('depth_span', 0)
        }
        
        sections.append(section_info)
        
        print(f"\n{i}. {node['value']}")
        print(f"   Depth: {node['depth']}")
        if node['amount']:
            print(f"   Amount: ₱{node['amount']:,.0f}")
        print(f"   Has children: {node['has_children']}")
        if node.get('branching_factor', 1) > 1:
            print(f"   Branching factor: {node['branching_factor']} (children at {len(set(node.get('child_depths', [])))} different depths)")
        if node.get('max_leaf_depth') is not None:
            print(f"   Max leaf depth: {node['max_leaf_depth']}")
            print(f"   Depth span: {node['depth_span']}")
    
    return sections

def analyze_section_characteristics(sections: List[Dict], all_nodes: List[Dict]) -> None:
    """
    Analyze characteristics of identified sections.
    """
    print("\n" + "=" * 80)
    print("SECTION CHARACTERISTICS ANALYSIS")
    print("=" * 80)
    
    # Group sections by depth
    sections_by_depth = defaultdict(list)
    for section in sections:
        sections_by_depth[section['depth']].append(section)
    
    for depth in sorted(sections_by_depth.keys()):
        secs = sections_by_depth[depth]
        print(f"\nSections at Depth {depth}:")
        
        for section in secs:
            val_display = section['value'][:50] + "..." if len(section['value']) > 50 else section['value']
            
            if section['branching_factor'] > 1:
                print(f"  Branching: {val_display}")
                print(f"    → Children at {len(set(section.get('child_depths', [])))} different depths")
                print(f"    → Branching factor: {section['branching_factor']}")
            else:
                print(f"  Simple: {val_display}")
                
                if section.get('max_leaf_depth') is not None:
                    print(f"    → Max depth: {section['max_leaf_depth']}")
                    if section['depth_span'] > 0:
                        print(f"    → Span: {section['depth_span']} levels")

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    print("=" * 80)
    print("HIERARCHICAL SECTION ANALYSIS")
    print("=" * 80)
    print(f"\nLoading JSON hierarchy: {json_file}")
    
    nodes = load_json(json_file)
    print(f"Loaded {len(nodes)} root nodes")
    
    # Analyze depth distribution
    all_nodes = identify_section_transitions(nodes)
    
    # Find major sections
    sections = find_major_sections(nodes)
    
    # Analyze section characteristics
    analyze_section_characteristics(sections, all_nodes)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Count by depth
    depth_counts = Counter(n['depth'] for n in all_nodes)
    
    print(f"\nTotal nodes analyzed: {len(all_nodes)}")
    print(f"\nNodes by depth:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]:>6,}")
    
    # Section summary
    print(f"\nMajor sections identified: {len(sections)}")
    
    # Branching analysis
    branching_sections = [s for s in sections if s.get('branching_factor', 1) > 1]
    simple_sections = [s for s in sections if s.get('branching_factor', 1) <= 1]
    
    print(f"  Branching sections: {len(branching_sections)}")
    print(f"  Simple sections: {len(simple_sections)}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nRecommendations:")
    print("1. Use branching sections as primary section boundaries")
    print("2. Simple sections may be leaf nodes or single-path categories")
    print("3. Analyze within each branching section independently")
    print("4. The natural hierarchy already encodes the sections")

if __name__ == "__main__":
    main()
