#!/usr/bin/env python3
"""
Recursive section analysis by depth for Level 1 sections ONLY.
Analyzes each of the 11 major sections recursively up to L6.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

def load_json(json_path: Path) -> List[Dict]:
    """Load hierarchical JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_subtree(
    section_root: Dict,
    section_name: str,
    max_depth: int = 6
) -> Dict:
    """
    Recursively analyze a section's subtree up to max_depth.
    
    Args:
        section_root: Root node of this section
        section_name: Name of section
        max_depth: Maximum depth to analyze (default 6)
    
    Returns:
        Dictionary with analysis results
    """
    results = {
        'section_name': section_name,
        'depth_analysis': {},
        'structure': {},
        'total_items': 0,
        'total_amount': 0.0,
        'paths': []
    }
    
    # Initialize depth analysis containers
    for d in range(1, max_depth + 1):  # Depths 1-6 (relative to section start)
        results['depth_analysis'][d] = {
            'node_count': 0,
            'unique_values': set(),
            'amounts': [],
            'top_values': []
        }
    
    # Recursive function to analyze subtree
    def analyze_recursive(nodes: List[Dict], relative_depth: int):
        for node in nodes:
            # Update total counts
            results['total_items'] += 1
            if node.get('amount'):
                results['total_amount'] += float(node['amount'])
            
            # Determine absolute depth (L1 + relative_depth)
            abs_depth = 1 + relative_depth
            
            # Track at relevant depth
            if 1 <= abs_depth <= max_depth:
                depth_key = abs_depth
                depth_data = results['depth_analysis'][depth_key]
                
                depth_data['node_count'] += 1
                
                # Add to unique values
                value = node.get('value', '').strip()
                if value:
                    depth_data['unique_values'].add(value)
                    results['structure'][value] = results['structure'].get(value, 0) + 1
                
                # Track amounts
                if node.get('amount'):
                    depth_data['amounts'].append(float(node['amount']))
            
            # Build path to leaf
            children = node.get('children', [])
            if not children:
                # This is a leaf - build path
                path_parts = []
                def build_path(n: Dict, current_depth: int):
                    path_parts.append(n.get('value', '').strip())
                    if not n.get('children', []):
                        return ' > '.join(reversed(path_parts))
                    for child in n['children'][:1]:  # Only first child for path
                        return build_path(child, current_depth + 1)
                
                full_path = build_path(section_root, 0)
                if node.get('amount'):
                    results['paths'].append((full_path, float(node['amount']), abs_depth))
            else:
                # Recursively analyze children
                analyze_recursive(children, relative_depth + 1)
    
    # Start recursive analysis from section root
    analyze_recursive([section_root], 1)
    
    # Calculate statistics per depth
    for d in range(1, max_depth + 1):
        depth_data = results['depth_analysis'][d]
        amounts = depth_data['amounts']
        depth_data['total_amount'] = sum(amounts) if amounts else 0.0
        depth_data['avg_amount'] = sum(amounts) / len(amounts) if amounts else 0.0
        depth_data['max_amount'] = max(amounts) if amounts else 0.0
        depth_data['min_amount'] = min(amounts) if amounts else 0.0
        
        # Sort unique values by frequency in flattened table
        # Count occurrences in all paths
        value_freq = Counter()
        for path, amount, depth in results['paths']:
            parts = path.split(' > ')
            if len(parts) >= d:
                value = parts[d-1]  # Depth d corresponds to parts[d-1] (0-indexed)
                value_freq[value] += 1
        
        depth_data['unique_values_sorted'] = sorted(
            depth_data['unique_values'],
            key=lambda x: value_freq.get(x, 0),
            reverse=True
        )
    
    # Get top paths by amount
    results['paths'].sort(key=lambda x: x[1], reverse=True)
    results['top_paths'] = results['paths'][:20]
    
    return results

def print_section_analysis(result: Dict) -> None:
    """Print formatted analysis for a single section."""
    print(f"\nSECTION: {result['section_name']}")
    print(f"{'='*70}")
    
    print(f"\nTotal Items: {result['total_items']:,}")
    print(f"Total Amount: ₱{result['total_amount']:,.2f}")
    print(f"Average Amount per Item: ₱{result['total_amount']/result['total_items']:,.2f}" if result['total_items'] > 0 else "N/A")
    
    print(f"\nStructure: {len(result['structure'])} unique values")
    
    # Show depth-by-depth analysis
    print(f"\n{'DEPTH':<6} {'Items':>10} {'Unique':>10} {'Total Amount':>20} {'Avg':>18} {'Max':>18}")
    print("-" * 86)
    
    for d in sorted(result['depth_analysis'].keys()):
        depth_data = result['depth_analysis'][d]
        amount_str = f"₱{depth_data['total_amount']:,.2f}" if depth_data['total_amount'] else "N/A"
        avg_str = f"₱{depth_data['avg_amount']:,.2f}" if depth_data['amounts'] else "N/A"
        max_str = f"₱{depth_data['max_amount']:,.2f}" if depth_data['amounts'] else "N/A"
        
        print(f"  L{d:>2} {depth_data['node_count']:>10,} {depth_data['unique_values']:>10,} {amount_str:>20} {avg_str:>18} {max_str:>18}")
    
    # Show top 10 unique values per depth
    print(f"\nTOP UNIQUE VALUES BY DEPTH")
    
    for d in sorted(result['depth_analysis'].keys()):
        depth_data = result['depth_analysis'][d]
        unique_values = depth_data['unique_values_sorted'][:10]
        
        if unique_values:
            print(f"\n  Depth L{d} - Top {len(unique_values)} unique values:")
            for i, value in enumerate(unique_values, 1):
                val_display = value[:50] + "..." if len(value) > 50 else value
                print(f"    {i:2}. {val_display}")
    
    # Show top paths by amount
    print(f"\nTOP 20 PATHS BY AMOUNT")
    for i, (path, amount, depth) in enumerate(result['top_paths'], 1):
        path_display = path[:100] + "..." if len(path) > 100 else path
        print(f"{i:2}. {path_display}")
        print(f"    Amount: ₱{amount:,.2f} | Depth: L{depth}")

def compare_sections(section_results: List[Dict]) -> None:
    """Compare all sections across various metrics."""
    print("\n" + "=" * 80)
    print("CROSS-SECTION COMPARISON")
    print("=" * 80)
    
    # Sort sections by total amount
    sorted_sections = sorted(section_results, key=lambda x: x['total_amount'], reverse=True)
    
    print(f"\n{'Section':<50} {'Items':>10} {'Total Amount':>20} {'Avg Amount':>18} {'Max Depth':>10}")
    print("-" * 100)
    
    for section in sorted_sections:
        name_display = section['section_name'][:47] + "..." if len(section['section_name']) > 50 else section['section_name']
        amount_str = f"₱{section['total_amount']:,.2f}"
        avg_str = f"₱{section['total_amount']/section['total_items']:,.2f}" if section['total_items'] > 0 else "N/A"
        
        # Find max depth with data
        max_data_depth = 0
        for d in section['depth_analysis'].keys():
            if section['depth_analysis'][d]['node_count'] > 0:
                max_data_depth = d
        
        print(f"{name_display:<50} {section['total_items']:>10,} {amount_str:>20} {avg_str:>18}   L{max_data_depth}")
    
    print(f"\nTotal: {sum(s['total_items'] for s in section_results):,} items")
    print(f"Total Amount: ₱{sum(s['total_amount'] for s in section_results):,.2f}")

def main():
    """Main function."""
    # Get paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    json_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json"
    
    print("=" * 80)
    print("RECURSIVE SECTION ANALYSIS (LEVEL 1 SECTIONS)")
    print("=" * 80)
    print(f"\nLoading hierarchy: {json_file}")
    
    root_nodes = load_json(json_file)
    print(f"Loaded {len(root_nodes)} root nodes")
    
    # Get Level 1 values (major sections)
    level_1_values = set()
    for node in root_nodes:
        level_1_values.add(node.get('value', '').strip())
        for child in node.get('children', []):
            level_1_values.add(child.get('value', '').strip())
    
    section_names = sorted([v for v in level_1_values if v and v != '.'])
    print(f"\nFound {len(section_names)} major sections (Level 1)")
    for i, name in enumerate(section_names, 1):
        print(f"{i:2}. {name}")
    
    # Analyze each section recursively up to L6
    section_results = []
    
    for section_name in section_names:
        # Find this section's root node
        section_root = None
        
        def find_section_root(nodes, name):
            for node in nodes:
                if node.get('value', '').strip() == name:
                    return node
                result = find_section_root(node.get('children', []), name)
                if result:
                    return result
            return None
        
        section_root = find_section_root(root_nodes, section_name)
        
        if section_root:
            result = analyze_subtree(section_root, section_name, max_depth=6)
            section_results.append(result)
            print_section_analysis(result)
        else:
            print(f"\n⚠️  Could not find root for section: {section_name}")
    
    # Compare sections
    compare_sections(section_results)
    
    # Save results
    output_file = data_dir / "recursive_section_analysis.json"
    print(f"\nSaving results to: {output_file}")
    
    output_data = []
    for result in section_results:
        section_summary = {
            'section_name': result['section_name'],
            'total_items': result['total_items'],
            'total_amount': result['total_amount'],
            'depth_analysis': {}
        }
        
        for d, depth_data in result['depth_analysis'].items():
            section_summary['depth_analysis'][d] = {
                'node_count': depth_data['node_count'],
                'unique_values': list(depth_data['unique_values_sorted'][:50]),  # Top 50
                'unique_count': len(depth_data['unique_values']),
                'total_amount': depth_data['total_amount'],
                'avg_amount': depth_data['avg_amount'],
                'max_amount': depth_data['max_amount']
            }
        
        output_data.append(section_summary)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Results saved!")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("1. Each Level 1 section analyzed independently")
    print("2. Depth distribution shown for L1-L6 (within section)")
    print("3. Unique values identified at each depth")
    print("4. Top 20 paths by amount per section")
    print("5. Cross-section comparison of budget allocation")
    print("\nRecommendations:")
    print("- Use section-specific analysis for accurate insights")
    print("- Compare sections of similar structure patterns")
    print("- Focus depth analysis within section boundaries")

if __name__ == "__main__":
    main()
