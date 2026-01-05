# DPWH 2026 GAA Hierarchy Explorer

This project contains scripts to convert Excel data to hierarchical JSON and a web interface to explore it.

## Files

- `scripts/xlsx_to_csv.py` - Converts XLSX to CSV format
- `scripts/extract_unique_values.py` - Extracts unique values from columns 0-9
- `scripts/build_hierarchy.py` - Builds hierarchy from CSV (legacy)
- `scripts/build_hierarchy_from_xlsx.py` - Builds hierarchy from XLSX with formatting awareness
- `index.html` - Interactive web interface to explore the hierarchy
- `data/` - Contains the source XLSX file and generated JSON files

## Usage

### Generate Hierarchy JSON

```bash
# Install dependencies
pip install -r requirements.txt

# Generate hierarchy from XLSX (recommended - includes formatting)
python scripts/build_hierarchy_from_xlsx.py
```

This will create `data/FY 2026_DPWH DETAILS ENROLLED COPY (Final)_hierarchy.json`

### View in Web Browser

1. Start a simple HTTP server:
```bash
python3 -m http.server 8000
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. The interactive hierarchy explorer will load automatically.

## Features

- **Hierarchical Tree View**: Expand/collapse nodes to navigate the structure
- **Search**: Search by name, amount, or description
- **Amount Display**: Shows monetary values in Philippine Peso format
- **Descriptions**: Displays italicized description text when available
- **Responsive Design**: Works on desktop and mobile devices

## Hierarchy Structure

Each node in the JSON contains:
- `value`: The node's name/title
- `amount`: Monetary value (if present)
- `description`: Description text (if present, from italic rows)
- `children`: Array of child nodes
