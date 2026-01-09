#!/usr/bin/env python3
"""
Section depth analysis - Analyzes each Level 1 section recursively up to L6.
Shows unique values and structure within each section.
"""

import json
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter

def load_json(json_path: Path) -> List[Dict]:
    """Load hierarchical JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_section_recursive(nodes: List[Dict], section_name: str, max_depth: int = 6) -> Dict:
    """
    Recursively analyze a section's subtree up to max_depth.
    """
    results = {
        'section_name': section_name,
        'total_items': 0,
        'total_amount': 0.0,
        'depth_analysis': {},
        'paths': []
    }
    
    # Initialize depth analysis containers
    for d in range(1, max_depth + 1):  # Depths 1-6 (relative to section start)
        results['depth_analysis'][f'L{d}'] = {
            'node_count': 0,
            'unique_values': set(),
            'amounts': []
        }
    
    # Recursive function
    def analyze_recursive(node_list: List[Dict], section_depth: int):
        for node in node_list:
            # Determine absolute depth (section_depth is depth within section)
            abs_depth = 1 + section_depth - 1  # Section starts at depth 1 relative to root
            
            # Only track if within our range
            if section_depth <= max_depth:
                results['total_items'] += 1
                
                amount = node.get('amount')
                if amount:
                    results['total_amount'] += float(amount)
                
                # Track at specific depth
                depth_key = f'L{section_depth}'
                if depth_key in results['depth_analysis']:
                    depth_data = results['depth_analysis'][depth_key]
                    depth_data['node_count'] += 1
                    value = node.get('value', '').strip()
                    if value:
                        depth_data['unique_values'].add(value)
                    if amount:
                        depth_data['amounts'].append(float(amount))
                
                # Build path if this is a leaf within section
                children = node.get('children', [])
                if not children or section_depth == max_depth:
                    # This is a leaf in section - build path
                    path_parts = []
                    def build_path(n: Dict, current_depth: int):
                        path_parts.append(n.get('value', '').strip())
                        if not n.get('children', []) or current_depth == max_depth:
                            return ' > '.join(reversed(path_parts))
                        for child in n.get('children', [])[:1]:  # Just first child for main path
                            result = build_path(child, current_depth + 1)
                            if result:
                                return result
                        return None
                    
                    full_path = build_path(node, section_depth)
                    if full_path:
                        results['paths'].append((full_path, amount, section_depth))
                
                # Recursively analyze children
                if children:
                    analyze_recursive(children, section_depth + 1)
    
    # Start analysis
    analyze_recursive(nodes, 1)
    
    # Calculate statistics per depth
    for d in range(1, max_depth + 1):
        depth_key = f'L{d}'
        if depth_key in results['depth_analysis']:
            depth_data = results['depth_analysis'][depth_key]
            amounts = depth_data['amounts']
            
            if amounts:
                depth_data['total_amount'] = sum(amounts)
                depth_data['avg_amount'] = sum(amounts) / len(amounts)
                depth_data['max_amount'] = max(amounts)
                depth_data['min_amount'] = min(amounts)
    
    # Sort paths by amount
    results['paths'].sort(key=lambda x: x[1], reverse=True)
    results['top_paths'] = results['paths'][:20]
    
    return results

def print_section_analysis(result: Dict) -> None:
    """Print formatted analysis for a single section."""
    print(f"\n{'='*80}")
    print(f"SECTION: {result['section_name']}")
    print("="*80)
    
    print(f"\nTotal Items: {result['total_items']:,}")
    print(f"Total Amount: ₱{result['total_amount']:,.2f}")
    print(f"Average Amount per Item: ₱{result['total_amount']/result['total_items']:,.2f}" if result['total_items'] > 0 else "N/A")
    
    print(f"\nStructure: {result['total_items']} items across {len(result['depth_analysis'])} depths")
    
    # Show depth-by-depth analysis
    print(f"\n{'='*80}")
    print("DEPTH-BY-DEPTH ANALYSIS (L1-L6 relative to section)")
    print("="*80)
    
    for depth_key in sorted(result['depth_analysis'].keys()):
        d = depth_key.replace('L', '')
        depth_data = result['depth_analysis'][depth_key]
        
        amount_str = f"₱{depth_data['total_amount']:,.2f}" if 'total_amount' in depth_data else "N/A"
        avg_str = f"₱{depth_data['avg_amount']:,.2f}" if 'avg_amount' in depth_data else "N/A"
        max_str = f"₱{depth_data['max_amount']:,.2f}" if 'max_amount' in depth_data else "N/A"
        
        print(f"\nDepth L{d}: {depth_data['node_count']:,} nodes, {depth_data['node_count'] - depth_data['unique_count']:,} unique values")
        print(f"  Total Amount: {amount_str}")
        print(f"  Average Amount: {avg_str}")
        print(f"  Max Amount: {max_str}")
        
        # Show top 10 unique values
        unique_values = sorted(list(depth_data['unique_values']))[:10]
        if unique_values:
            print(f"  Top {len(unique_values)} unique values:")
            for value in unique_values:
                val_display = value[:60] + "..." if len(value) > 60 else value
                print(f"    - {val_display}")
    
    # Show top paths
    print(f"\n{'='*80}")
    print(f"TOP 20 PATHS BY AMOUNT")
    print("="*80)
    
    for i, (path, amount, depth) in enumerate(result['top_paths'], 1):
        path_display = path[:120] + "..." if len(path) > 120 else path
        print(f"\n{i:2}. {path_display}")
        print(f"    Amount: ₱{amount:,.2f} | Depth: L{depth}")

def compare_sections(section_results: List[Dict]) -> None:
    """Compare all sections across various metrics."""
    print(f"\n{'='*80}")
    print("CROSS-SECTION COMPARISON")
    print("="*80)
    
    # Sort sections by total amount
    sorted_sections = sorted(section_results, key=lambda x: x['total_amount'], reverse=True)
    
    print(f"\n{'Section':<60} {'Items':>10} {'Total Amount':>22} {'Max Depth':>10} {'Avg Amount':>18}")
    print("-"*108)
    
    for section in sorted_sections:
        name_display = section['section_name'][:57] + "..." if len(section['section_name']) > 60 else section['section_name']
        amount_str = f"₱{section['total_amount']:,.2f}"
        avg_str = f"₱{section['total_amount']/section['total_items']:,.2f}" if section['total_items'] > 0 else "N/A"
        
        # Find max depth with data
        max_depth_with_data = 0
        for d_key in section['depth_analysis'].keys():
            if section['depth_analysis'][d_key]['node_count'] > 0:
                max_depth_with_data = d
                break
        
        print(f"{name_display:<60} {section['total_items']:>10,} {amount_str:>22}   L{max_depth_with_data}   {avg_str:>18}")
    
    total_items = sum(s['total_items'] for s in section_results)
    total_amount = sum(s['total_amount'] for s in section_results)
    
    print(f"\nTotal: {total_items:,} items")
    print(f"Total Amount: ₱{total_amount:,.2f}")

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    print("="*80)
    print("RECURSIVE SECTION DEPTH ANALYSIS")
    print("="*80)
    print(f"\nLoading hierarchy: {json_file}")
    
    root_nodes = load_json(json_file)
    print(f"Loaded {len(root_nodes)} root nodes")
    
    # Get Level 1 values (major sections)
    level_1_values = set()
    for node in root_nodes:
        value = node.get('value', '').strip()
        if value and value != '.':
            level_1_values.add(value)
    
    section_names = sorted([v for v in level_1_values])
    print(f"\nFound {len(section_names)} major sections (Level 1)")
    for i, name in enumerate(section_names, 1):
        print(f"{i}. {name}")
    
    # Analyze each section
    section_results = []
    
    for section_name in section_names:
        # Find this section's root
        section_root = None
        for node in root_nodes:
            if node.get('value', '').strip() == section_name:
                section_root = node
                break
        
        if section_root:
            result = analyze_section_recursive([section_root], section_name, max_depth=6)
            section_results.append(result)
        else:
            print(f"\nWarning: Could not find root for section: {section_name}")
    
    # Compare sections
    if section_results:
        compare_sections(section_results)
    
    # Save results
    output_file = data_dir / "section_depth_analysis.json"
    print(f"\nSaving results to: {output_file}")
    
    output_data = []
    for result in section_results:
        section_summary = {
            'section_name': result['section_name'],
            'total_items': result['total_items'],
            'total_amount': result['total_amount'],
            'depth_analysis': {}
        }
        
        for d_key, d_data in result['depth_analysis'].items():
            section_summary['depth_analysis'][d_key] = {
                'node_count': d_data['node_count'],
                'unique_count': len(d_data['unique_values']),
                'top_unique_values': sorted(list(d_data['unique_values']))[:20],
                'total_amount': d_data.get('total_amount', 0.0),
                'avg_amount': d_data.get('avg_amount', 0.0),
                'max_amount': d_data.get('max_amount', 0.0)
            }
        
        output_data.append(section_summary)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("Results saved!")
    
    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nKey Insights:")
    print("1. Each Level 1 section analyzed recursively up to L6")
    print("2. Depth distribution shown within each section (L1-L6 relative to section)")
    print("3. Unique values identified at each depth level")
    print("4. Top 20 paths by amount per section")
    print("5. Cross-section comparison of budget allocation")
    print("\nRecommendations:")
    print("- Use section-specific analysis for accurate insights")
    print("- Compare sections of similar depth patterns")
    print("- Focus on depth distribution within section boundaries")

if __name__ == "__main__":
    main()
