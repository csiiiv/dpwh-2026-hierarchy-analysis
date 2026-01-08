#!/usr/bin/env python3
"""
Convert flattened table (CSV/JSON) to markdown format.
Creates a markdown table with sample data and summary statistics.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict

def format_amount(amount):
    """Format amount as Philippine Peso."""
    if amount is None or amount == '':
        return ''
    try:
        amt = float(amount)
        return f" ₱{amt:,.2f}"
    except (ValueError, TypeError):
        return ''

def csv_to_markdown(csv_path: Path, output_path: Path, max_rows: int = 20):
    """
    Convert CSV table to markdown format.
    
    Args:
        csv_path: Path to input CSV file
        output_path: Path to output markdown file
        max_rows: Maximum number of rows to display in markdown table
    """
    print(f"Reading CSV file: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows):,} rows")
    
    # Calculate statistics
    total_amount = sum(float(r['amount']) if r['amount'] else 0 for r in rows)
    rows_with_amount = sum(1 for r in rows if r['amount'])
    rows_with_desc = sum(1 for r in rows if r['description'] and r['description'].strip())
    
    # Determine which level columns to show
    max_depth = max(int(r['depth']) for r in rows) if rows else 0
    level_columns = [f'level_{i}' for i in range(max_depth + 1)]
    
    # Build markdown content
    md_lines = []
    
    # Header
    md_lines.append("# Flattened DPWH 2026 GAA Data")
    md_lines.append("")
    md_lines.append("This document contains the flattened hierarchy data from the DPWH 2026 General Appropriations Act.")
    md_lines.append("")
    
    # Statistics
    md_lines.append("## Summary Statistics")
    md_lines.append("")
    md_lines.append(f"- **Total rows:** {len(rows):,}")
    md_lines.append(f"- **Total amount:** ₱{total_amount:,.2f}")
    md_lines.append(f"- **Rows with amounts:** {rows_with_amount:,} ({rows_with_amount/len(rows)*100:.1f}%)")
    md_lines.append(f"- **Rows with descriptions:** {rows_with_desc:,} ({rows_with_desc/len(rows)*100:.1f}%)")
    md_lines.append(f"- **Maximum depth:** {max_depth} levels")
    md_lines.append("")
    
    # Distribution by depth
    depth_counts = {}
    for row in rows:
        depth = row['depth']
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
    
    md_lines.append("### Distribution by Depth")
    md_lines.append("")
    md_lines.append("| Depth | Rows | Percentage |")
    md_lines.append("|-------|-------|------------|")
    for depth in sorted(depth_counts.keys()):
        count = depth_counts[depth]
        percentage = count / len(rows) * 100
        md_lines.append(f"| {depth} | {count:,} | {percentage:.1f}% |")
    md_lines.append("")
    
    # Sample table (limited rows)
    md_lines.append(f"## Sample Data (First {min(max_rows, len(rows))} Rows)")
    md_lines.append("")
    
    # Create table header
    headers = level_columns[:6]  # Limit to 6 level columns for readability
    headers.extend(['Value', 'Amount', 'Depth'])
    
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("|" + "|".join(["--------" for _ in headers]) + "|")
    
    # Add rows
    for row in rows[:max_rows]:
        row_data = []
        for col in headers:
            if col == 'Amount':
                row_data.append(format_amount(row.get(col, '')))
            elif col == 'Depth':
                row_data.append(row.get('depth', ''))
            else:
                val = row.get(col, '')
                # Truncate long values
                if len(str(val)) > 40:
                    val = str(val)[:37] + "..."
                row_data.append(val)
        md_lines.append("| " + " | ".join(str(v) for v in row_data) + " |")
    
    if len(rows) > max_rows:
        md_lines.append(f"\n*... and {len(rows) - max_rows:,} more rows*")
    
    md_lines.append("")
    
    # Column descriptions
    md_lines.append("## Column Descriptions")
    md_lines.append("")
    md_lines.append("- **level_0 to level_N**: Hierarchy level values (ancestors)")
    md_lines.append("- **value**: The leaf node value (most specific item)")
    md_lines.append("- **description**: Additional description (rare)")
    md_lines.append("- **amount**: Budget allocation amount")
    md_lines.append("- **depth**: Depth in hierarchy (0-8)")
    md_lines.append("- **full_path**: Complete path from root to leaf")
    md_lines.append("")
    
    # Full path samples
    md_lines.append("## Sample Full Paths")
    md_lines.append("")
    for i, row in enumerate(rows[:10], 1):
        path = row.get('full_path', '')
        amount = format_amount(row.get('amount', ''))
        md_lines.append(f"{i}. {path}{amount}")
    md_lines.append("")
    
    # Write to file
    md_content = "\n".join(md_lines)
    
    print(f"Writing markdown file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✓ Markdown file created: {output_path}")

def main():
    """Main function."""
    # Get script directory and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    
    # Find CSV file
    csv_file = data_dir / "FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy_table.csv"
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        return 1
    
    # Output markdown file
    output_file = data_dir / f"{csv_file.stem}_sample.md"
    
    try:
        csv_to_markdown(csv_file, output_file)
        print(f"\n✓ Conversion complete!")
        print(f"  Input:  {csv_file}")
        print(f"  Output: {output_file}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
