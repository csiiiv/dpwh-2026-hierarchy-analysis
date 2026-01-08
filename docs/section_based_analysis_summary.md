# Section-Based Hierarchy Analysis

## Overview

Analysis confirms your suspicion: **hierarchy content shifts around depending on section** due to flexible structure where same values can appear at different levels.

---

## Key Finding: 247 Overlapping Values

**247 values appear at multiple levels**, confirming hierarchy flexibility:

### Overlap Categories

1. **Geographic Regions** (18 items)
   - Appear at: L2, L3, L4, L5, L6
   - Example: "National Capital Region" appears 5 times across levels
   
2. **District Engineering Offices** (200+ items)
   - Appear at: L5, L6
   - Example: "Abra District Engineering Office" at both levels
   
3. **Program Categories** (10+ items)
   - Appear at: L3, L4
   - Example: "Asset Preservation Program", "Network Development Program"
   
4. **Administrative Units** (5+ items)
   - Appear at: L3, L4, L5, L6
   - Example: "Central Office", "GOP", "Loan Proceeds"

---

## Section Structure Analysis

### 9 Major Sections (Level 1)

| Section | Items | % of Total | Total Amount | Avg Amount | Avg Depth |
|----------|--------|-------------|---------------|-------------|------------|
| **CAPITAL OUTLAYS** | 1 | 0.0% | ₱496.9B | ₱496.9B | 1.0 |
| **OPERATIONS** | 17,951 | 91.5% | ₱656.0B | ₱36.5M | 7.2 |
| **SUPPORT TO OPERATIONS** | 891 | 4.5% | ₱44.8B | ₱50.3M | 6.0 |
| **Pre-Feasibility Study** | 688 | 3.5% | ₱12.3B | ₱17.9M | 5.7 |
| **GENERAL ADMINISTRATIVE AND SUPPORT** | 38 | 0.2% | ₱4.8B | ₱127.5M | 6.2 |
| **Payments of ROW** | 39 | 0.2% | ₱5.0B | ₱128.2M | 4.9 |
| **MAINTENANCE AND OTHER OPERATING EXPENSES** | 1 | 0.0% | ₱18.4B | ₱18.4B | 1.0 |
| **Payments of Contractual Obligations** | 1 | 0.0% | ₱1.0B | ₱1.0B | 4.0 |
| **PROGRAMS / ACTIVITIES / PROJECTS** | 1 | 0.0% | ₱0.0 | ₱0.0 | 1.0 |

---

## Section Characteristics

### 1. OPERATIONS Section (91.5% of budget)

**Structure**:
- Top Level 2: CONVERGENCE AND SPECIAL SUPPORT PROGRAM (70.7%)
- Top Level 3: Basic Infrastructure Program (45.6%)
- Depth: Ranges from L4 to L8
- Top 4 programs: Basic Infrastructure, Sustainable Infrastructure, Asset Preservation, Network Development

**Key insight**: Deeper hierarchy with most items at L7 (74.5%) and L8 (20.4%)

### 2. SUPPORT TO OPERATIONS Section (3.6% of budget)

**Structure**:
- Top Level 2: Infrastructure Planning, Design... (99.6%)
- Top Level 3: Maintenance, Repair and Rehabilitation (99.1%)
- Depth: Mostly L6 (91.7%) and L7 (6.6%)
- Focus: District engineering offices

**Key insight**: Shallow depth, focused on district-level operations

### 3. Pre-Feasibility Study Section (3.5% of budget)

**Structure**:
- Top Level 3: Regionwide/Nationwide (58.3%)
- Depth: Mostly L5 (34.6%), L6 (32.0%), L7 (22.8%)
- Focus: Feasibility and preliminary engineering studies

**Key insight**: Distributed across regions, moderate depth

### 4. CAPITAL OUTLAYS Section (40.1% of budget)

**Structure**:
- Single item at L1
- No deeper structure

**Key insight**: Simple, high-value allocation

---

## Recommended Analysis Approach

### Problem with Universal Level-Based Analysis

Traditional level-based analysis doesn't work because:

1. **Depth varies by section**: OPERATIONS goes to L8, SUPPORT TO OPERATIONS stops at L7
2. **Same value, different roles**: "National Capital Region" means different things at different depths
3. **Context-dependent**: Can't compare items across sections without normalization

### Solution: Per-Section Analysis

**Primary Cut**: Level 1 (9 major sections)

**Within Each Section**:
1. Analyze depth distribution independently
2. Identify top categories within section
3. Compare items within same context only
4. Preserve full hierarchical path for tracking

**Cross-Section Comparison**:
1. Budget share comparison (normalized)
2. Complexity comparison (average depth)
3. Geographic distribution comparison
4. Top program types comparison

---

## Implementation Scripts

### Created Scripts

1. **analyze_levels_simple.py**
   - Basic unique values per level (0-6)
   - Checks for overlapping values
   - Shows depth distribution per level
   
2. **analyze_by_section.py**
   - Per-section analysis (9 sections)
   - Depth distribution within sections
   - Top categories per level (L2-L6)
   - Top 10 paths by amount per section
   - Cross-section comparison
   - Saves detailed JSON results

### Generated Outputs

1. **all_levels_analysis.txt**: Full level analysis
2. **section_analysis_results.json**: Detailed section results
3. **level_overlap_analysis.md**: Comprehensive overlap documentation

---

## Key Insights

### 1. Budget Concentration

- **Top 3 sections**: 96.1% of total budget
  - CAPITAL OUTLAYS: 40.1%
  - OPERATIONS: 52.9%
  - SUPPORT TO OPERATIONS: 3.6%
  
- **Operations dominance**: OPERATIONS section contains 91.5% of all items

### 2. Section Complexity

- **Deep sections**: OPERATIONS (avg depth 7.2)
- **Shallow sections**: CAPITAL OUTLAYS (depth 1), MAINTENANCE (depth 1)
- **Medium sections**: SUPPORT TO OPERATIONS (avg depth 6.0), Pre-Feasibility (avg depth 5.7)

### 3. Geographic Distribution

Most geographic analysis meaningful within sections:
- **OPERATIONS**: Regional breakdowns through hierarchy
- **SUPPORT TO OPERATIONS**: District engineering offices
- **Pre-Feasibility**: Regionwide studies

---

## Recommendations

### For Strategic Analysis

1. **Use per-section analysis** for accurate comparisons
2. **Focus on OPERATIONS section** (52.9% of budget)
3. **Analyze within-section patterns** rather than cross-section
4. **Preserve hierarchical context** for item tracking

### For Budget Management

1. **Monitor OPERATIONS section** closely (52.9% of budget, 91.5% of items)
2. **Track program types**: Basic Infrastructure, Sustainable Infrastructure, etc.
3. **Regional equity analysis**: Within each section
4. **Section-specific KPIs**: Different metrics for different section types

### For Data Management

1. **Section-based data views**: Create separate views per Level 1 value
2. **Normalized comparisons**: Compare apples-to-apples
3. **Context-aware reporting**: Always report section context

---

## Next Steps

✅ **Completed**:
- Identified overlapping values (247 items)
- Analyzed all levels (0-6)
- Created per-section analysis framework
- Generated comprehensive documentation

⏳ **Recommended Next Steps**:
1. Create section-specific reports for each major section
2. Visualize section structures
3. Develop section-specific KPIs
4. Create cross-section comparison dashboards
5. Implement section-based data views in web interface

---

## Conclusion

The hierarchy is **intentionally flexible** with overlapping values enabling the same organizational unit to serve different roles depending on context.

**Per-section analysis** is the correct approach:
- Handles varying depth across sections
- Respects context-dependent structure
- Enables accurate comparisons within sections
- Maintains full hierarchical context

**Primary sections** for analysis:
1. **OPERATIONS** (52.9% budget, 91.5% items)
2. **SUPPORT TO OPERATIONS** (3.6% budget, 4.5% items)
3. **Pre-Feasibility Studies** (1.0% budget, 3.5% items)
4. **Other sections** (collectively small percentages)

All analysis scripts and documentation have been committed to git and pushed to repository.
