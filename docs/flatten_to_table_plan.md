# Plan: Flatten Hierarchy to Table Format

## Overview

The current JSON hierarchy structure contains nested data across **9 levels** with **23,614 total nodes**. This document outlines the strategy for converting this nested structure into a flat table format suitable for analysis, reporting, and data export.

## Current Structure Analysis

### Hierarchy Statistics

| Level | Total Nodes | With Amounts | With Children | With Descriptions | Avg Value Length |
|--------|-------------|---------------|---------------|-------------------|------------------|
| L0     | 1           | 0 (0.0%)      | 1 (100.0%)    | 0 (0.0%)          | 1.0 chars        |
| L1     | 11          | 10 (90.9%)     | 7 (63.6%)     | 0 (0.0%)          | 33.9 chars       |
| L2     | 14          | 14 (100.0%)    | 11 (78.6%)    | 0 (0.0%)          | 43.4 chars       |
| L3     | 37          | 37 (100.0%)    | 30 (81.1%)    | 3 (8.1%)          | 61.6 chars       |
| L4     | 245         | 245 (100.0%)   | 155 (63.3%)   | 16 (6.5%)         | 27.2 chars       |
| L5     | 1,268       | 1,267 (99.9%)  | 984 (77.6%)   | 0 (0.0%)          | 27.1 chars       |
| L6     | 4,249       | 4,249 (100.0%) | 2,295 (54.0%) | 0 (0.0%)          | 60.8 chars       |
| L7     | 14,115      | 14,096 (99.9%) | 520 (3.7%)    | 0 (0.0%)          | 100.7 chars      |
| L8     | 3,674       | 3,674 (100.0%) | 0 (0.0%)      | 0 (0.0%)          | 103.3 chars      |

**Total**: 23,614 nodes across 9 levels

### Key Observations

1. **Maximum Depth**: 9 levels (L0 to L8)
2. **Most nodes have amounts**: 23,592 out of 23,614 (99.9%)
3. **Leaf nodes**: L8 has no children (3,674 nodes)
4. **Intermediate nodes with amounts**: Many nodes at L3-L7 have both amounts AND children
5. **Descriptions**: Very rare (only 19 nodes total, all at L3-L4)

### Sample Hierarchy Path

```
L0: .
└── L1: SUPPORT TO OPERATIONS [₱16,328,233,000]
    └── L2: Infrastructure Planning, Design, Construction and Maintenance [₱16,311,753,000]
        └── L3: Maintenance, Repair and Rehabilitation of Infrastructure Facilities [₱15,980,717,000]
            └── L4: Routine Maintenance of National Roads [₱8,502,016,000]
                └── L5: National Capital Region [₱375,127,000]
                    └── L6: North Manila District Engineering Office [₱50,000,000]
                        └── L7-L8: Specific projects/locations with amounts
```

## Flattening Approaches

### Option 1: Leaf Nodes Only (Recommended)

**Description**: Create one row per leaf node (nodes without children), with all ancestor values in separate columns.

**Pros**:
- Clean, normalized structure
- No duplication of intermediate node amounts
- Easier to aggregate and analyze
- Standard database design pattern

**Cons**:
- Loses intermediate node information (though amounts can be derived from children)
- May miss important context from intermediate levels that have their own significance

**Estimated Row Count**: ~3,674 rows (L8 nodes) + ~520 rows (L7 nodes without children) ≈ **4,194 rows**

**Column Structure**:
```
| Level_0 | Level_1 | Level_2 | Level_3 | Level_4 | Level_5 | Level_6 | Level_7 | Level_8 | Description | Amount |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|-------------|---------|
| .       | SUPPORT TO OPERATIONS | ... | ... | ... | ... | ... | ... | Project Name | ₱50,000,000 |
```

### Option 2: All Nodes (Denormalized)

**Description**: Create one row for every node in the hierarchy.

**Pros**:
- Preserves all node information
- No data loss
- Simple to implement

**Cons**:
- High duplication (amounts appear multiple times in hierarchy)
- Difficult to aggregate (need to avoid double-counting)
- Larger file size

**Estimated Row Count**: **23,614 rows**

**Column Structure**: Same as Option 1, but with many rows having NULL values for deeper levels.

### Option 3: Denormalized Paths (Full Enumeration)

**Description**: Create one row for every complete path through the hierarchy.

**Pros**:
- Complete representation of all relationships
- Easy to see full context for any node

**Cons**:
- Maximum duplication
- Very large output
- Complex to maintain

**Estimated Row Count**: Could be tens of thousands depending on branching factor.

### Option 4: Hybrid Approach (Most Flexible)

**Description**: Create multiple tables/views:
1. **Nodes Table**: All nodes with basic info (id, level, value, amount, description)
2. **Hierarchy Table**: Parent-child relationships (parent_id, child_id)
3. **Leaf Table**: Flattened view of leaf nodes with all ancestors

**Pros**:
- Most flexible
- Can generate different views as needed
- Relational database friendly
- Preserves all information while enabling efficient queries

**Cons**:
- More complex to maintain
- Requires SQL or similar for joining

## Recommendation: Option 1 (Leaf Nodes Only) with Enhancements

### Why This Approach?

1. **Focus on Leaf Nodes**: L7 and L8 nodes represent the most granular data points (projects, specific allocations)
2. **Preserve Context**: Ancestor values provide full organizational context
3. **Minimal Duplication**: Each actual budget item appears once
4. **Easy to Aggregate**: Summing amounts gives correct totals without complex deduplication

### Enhanced Column Structure

```csv
level_0,level_1,level_2,level_3,level_4,level_5,level_6,level_7,level_8,value,description,amount
.,SUPPORT TO OPERATIONS,Infrastructure Planning...,...,...,...,...,...,Project Name,Description text,₱50,000,000
```

### Implementation Plan

#### Phase 1: Core Flattening Script

**File**: `scripts/hierarchy_to_table.py`

**Functionality**:
1. Load JSON hierarchy
2. Traverse to find leaf nodes (nodes without children)
3. Build full path for each leaf
4. Extract ancestor values for each level
5. Write to CSV/JSON table format

**Features**:
- Support for variable depth (not all paths go to L8)
- Handle missing levels gracefully
- Include description column
- Format amounts properly
- Add metadata (depth, node count per path)

#### Phase 2: Enhanced Output Formats

1. **CSV Format**: Standard comma-separated values
2. **Markdown Table**: Human-readable documentation
3. **Excel Format**: With formatting and multiple sheets
4. **JSON Table**: Array of row objects

#### Phase 3: Analysis Views

Create additional flattened views:

1. **By Region**: Group by geographic regions (L5-L6)
2. **By Category**: Group by program/activity type (L2-L3)
3. **By District**: Group by district engineering offices
4. **Summary View**: Aggregated by level

### Sample Output (CSV)

```csv
level_0,level_1,level_2,level_3,level_4,level_5,level_6,level_7,level_8,value,description,amount
.,SUPPORT TO OPERATIONS,Infrastructure Planning, Design, Construction and Maintenance,Maintenance, Repair and Rehabilitation of Infrastructure Facilities,Routine Maintenance of National Roads,National Capital Region,North Manila District Engineering Office,,,₱50,000,000
.,MAINTENANCE AND OTHER OPERATING EXPENSES,,,,,,,,,,₱18,371,150,000
```

### Additional Considerations

1. **Level 0**: Current value is "." - should we use a meaningful label like "Root"?
2. **Empty Levels**: Some paths may not go to L8 - handle with empty strings
3. **Amount Placement**: Should amounts from intermediate levels be included as separate rows?
4. **Descriptions**: Very rare but should be preserved
5. **Value Lengths**: Some values are very long (>100 chars) - may need truncation for CSV

## Next Steps

1. ✅ Analyze hierarchy structure (completed)
2. ⏳ Implement `hierarchy_to_table.py` script
3. ⏳ Generate CSV output
4. ⏳ Create markdown documentation
5. ⏳ Add Excel export option
6. ⏳ Generate summary statistics
7. ⏳ Test and validate against original data

## Validation Checklist

- [ ] Total amount in flattened table equals sum of all leaf node amounts
- [ ] All leaf nodes are represented
- [ ] No data loss during transformation
- [ ] Ancestor paths are correct and complete
- [ ] Amounts are properly formatted
- [ ] Special characters (newlines, pipes) are handled correctly
- [ ] Description values are preserved
