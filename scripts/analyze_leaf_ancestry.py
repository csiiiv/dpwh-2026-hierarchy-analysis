#!/usr/bin/env python3
"""
Analyze leaf nodes by their full ancestry path.
Properly separates and organizes region and district office data.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter

def load_csv(csv_path: Path) -> List[Dict]:
    """Load CSV table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def looks_like_amount(value: str) -> bool:
    """Check if a string looks like an amount."""
    if not value:
        return False
    value = value.strip().replace(',', '').replace('₱', '').replace('PHP', '')
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_region(value: str) -> bool:
    """Check if a value looks like a region name."""
    if not value:
        return False
    value = value.strip()
    
    # Check for common region patterns
    region_keywords = [
        'Region I', 'Region II', 'Region III', 'Region IV', 'Region V',
        'Region VI', 'Region VII', 'Region VIII', 'Region IX',
        'Region X', 'Region XI', 'Region XII', 'Region XIII',
        'Region XIV', 'Region XV', 'Region XVI',
        'National Capital Region', 'NCR',
        'Cordillera Administrative Region', 'CAR',
        'MIMAROPA Region', 'Mindoro',
        'Negros Island Region', 'NIR',
        'Bangsamoro', 'BARMM'
    ]
    
    value_lower = value.lower()
    for keyword in region_keywords:
        if keyword.lower() in value_lower:
            return True
    
    return False

def is_district_office(value: str) -> bool:
    """Check if a value looks like a district engineering office."""
    if not value:
        return False
    value = value.strip()
    
    # Check for district engineering office patterns
    patterns = [
        r'\d+st District Engineering Office',
        r'\d+nd District Engineering Office',
        r'\d+rd District Engineering Office',
        r'\d+th District Engineering Office',
        r'\d+ District Engineering Office',
        r'District Engineering Office',
        r'City District Engineering Office',
    ]
    
    for pattern in patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    
    return False

def parse_ancestry(path: List[str]) -> Dict[str, str]:
    """
    Parse a path to extract structured components.
    
    Returns dict with keys:
    - section: Level 1 (major section)
    - level_2: Second level
    - level_3: Third level
    - level_4: Fourth level
    - level_5: Fifth level
    - level_6: Sixth level
    - level_7: Seventh level
    - level_8: Eighth level
    - level_9: Ninth level
    - region: Extracted region if found
    - district_office: Extracted district office if found
    - other_components: Other non-amount, non-region, non-office components
    """
    result = {
        'section': '',
        'level_2': '',
        'level_3': '',
        'level_4': '',
        'level_5': '',
        'level_6': '',
        'level_7': '',
        'level_8': '',
        'level_9': '',
        'region': '',
        'district_office': '',
        'other_components': []
    }
    
    # Assign levels
    for i, component in enumerate(path):
        level_key = f'level_{i + 2}' if i > 0 else 'section'
        if level_key in result:
            result[level_key] = component
    
    # Extract region (scan all levels for region-like values)
    for i, component in enumerate(path):
        if is_region(component) and not looks_like_amount(component):
            result['region'] = component
            break
    
    # Extract district office (scan all levels for office-like values)
    for i, component in enumerate(path):
        if is_district_office(component) and not looks_like_amount(component):
            result['district_office'] = component
            break
    
    # Collect other components (exclude section, region, district_office, amounts)
    for i, component in enumerate(path):
        if i == 0:  # Skip section
            continue
        if component == result['region'] or component == result['district_office']:
            continue
        if looks_like_amount(component):
            continue
        result['other_components'].append(component)
    
    return result

def analyze_by_section(rows: List[Dict]) -> Dict:
    """
    Analyze all rows grouped by section with structured ancestry breakdown.
    """
    sections = defaultdict(lambda: {
        'total_rows': 0,
        'total_amount': 0.0,
        'regions': Counter(),
        'district_offices': Counter(),
        'leaves': []
    })
    
    for row in rows:
        section = row.get('level_1', '').strip()
        if not section:
            continue
        
        # Parse path
        path = [row.get(f'level_{i}', '').strip() for i in range(1, 10)]
        path = [p for p in path if p and not looks_like_amount(p)]
        
        # Parse ancestry
        ancestry = parse_ancestry(path)
        
        # Update section stats
        sections[section]['total_rows'] += 1
        if row.get('amount') and str(row['amount']).strip():
            try:
                amount = float(row['amount'])
                sections[section]['total_amount'] += amount
            except ValueError:
                pass
        
        # Track region
        if ancestry['region']:
            sections[section]['regions'][ancestry['region']] += 1
        
        # Track district office
        if ancestry['district_office']:
            sections[section]['district_offices'][ancestry['district_office']] += 1
        
        # Store leaf details
        leaf_data = {
            'path': ' > '.join(path),
            'full_ancestry': path,
            'ancestry': ancestry,
            'amount': row.get('amount'),
            'depth': int(row.get('depth', 0))
        }
        sections[section]['leaves'].append(leaf_data)
    
    return dict(sections)

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    print("=" * 80)
    print("LEAF ANCESTRY ANALYSIS WITH REGION/OFFICE SEPARATION")
    print("=" * 80)
    
    # Load data
    print(f"\nLoading table from: {csv_file}")
    rows = load_csv(csv_file)
    print(f"Loaded {len(rows):,} rows")
    
    # Analyze by section
    sections_data = analyze_by_section(rows)
    
    # Print summary by section
    print("\n" + "=" * 80)
    print("SECTIONS SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Section':<50} {'Rows':>8} {'Amount':>20}")
    print("-" * 78)
    
    for section_name, data in sections_data.items():
        section_display = section_name[:47] + "..." if len(section_name) > 50 else section_name
        amount_str = f"₱{data['total_amount']:,.0f}" if data['total_amount'] else "N/A"
        print(f"{section_display:<50} {data['total_rows']:>8} {amount_str:>20}")
    
    # Detailed breakdown for each section
    for section_name, data in sections_data.items():
        print("\n" + "=" * 80)
        print(f"SECTION: {section_name}")
        print("=" * 80)
        
        print(f"\nRows: {data['total_rows']:,}")
        print(f"Total Amount: ₱{data['total_amount']:,.2f}")
        
        # Show regions
        if data['regions']:
            print(f"\n📍 REGIONS ({len(data['regions'])} unique)")
            print("-" * 60)
            for i, (region, count) in enumerate(data['regions'].most_common(20), 1):
                pct = count / data['total_rows'] * 100
                region_display = region[:50] + "..." if len(region) > 50 else region
                print(f"  {i:2}. {region_display:<50} {count:>5} ({pct:>5.1f}%)")
            
            if len(data['regions']) > 20:
                print(f"  ... and {len(data['regions']) - 20} more")
        
        # Show district offices
        if data['district_offices']:
            print(f"\n🏢 DISTRICT ENGINEERING OFFICES ({len(data['district_offices'])} unique)")
            print("-" * 60)
            for i, (office, count) in enumerate(data['district_offices'].most_common(20), 1):
                pct = count / data['total_rows'] * 100
                office_display = office[:50] + "..." if len(office) > 50 else office
                print(f"  {i:2}. {office_display:<50} {count:>5} ({pct:>5.1f}%)")
            
            if len(data['district_offices']) > 20:
                print(f"  ... and {len(data['district_offices']) - 20} more")
        
        # Show top leaf paths by amount
        leaves_with_amount = [l for l in data['leaves'] if l.get('amount') and str(l['amount']).strip()]
        leaves_with_amount.sort(key=lambda x: float(x['amount']), reverse=True)
        
        if leaves_with_amount:
            print(f"\n💰 TOP 15 LEAF PATHS BY AMOUNT")
            print("-" * 60)
            for i, leaf in enumerate(leaves_with_amount[:15], 1):
                path_display = leaf['path'][:70] + "..." if len(leaf['path']) > 70 else leaf['path']
                print(f"  {i:2}. {path_display}")
                print(f"      Amount: ₱{float(leaf['amount']):,.2f} | Depth: {leaf['depth']}")
    
    # Save results
    output_file = data_dir / "leaf_ancestry_analysis.json"
    print(f"\n" + "=" * 80)
    print(f"Saving detailed results to: {output_file}")
    
    # Prepare output data
    output_data = []
    for section_name, data in sections_data.items():
        section_output = {
            'name': section_name,
            'total_rows': data['total_rows'],
            'total_amount': data['total_amount'],
            'regions': dict(data['regions'].most_common(100)),  # Top 100
            'region_counts_exceeded': len(data['regions']) > 100,
            'total_regions': len(data['regions']),
            'district_offices': dict(data['district_offices'].most_common(100)),  # Top 100
            'district_counts_exceeded': len(data['district_offices']) > 100,
            'total_district_offices': len(data['district_offices']),
            'top_leaves_by_amount': sorted(
                data['leaves'],
                key=lambda x: float(x['amount']) if x.get('amount') else 0,
                reverse=True
            )[:20]
        }
        output_data.append(section_output)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Results saved!")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nKey Insights:")
    print("1. All leaf nodes analyzed with full ancestry path")
    print("2. Region names automatically detected and extracted")
    print("3. District engineering offices automatically detected and extracted")
    print("4. Amount-like values filtered out from ancestry components")
    print("5. Top 100 unique entries saved for regions and offices")

if __name__ == "__main__":
    main()
