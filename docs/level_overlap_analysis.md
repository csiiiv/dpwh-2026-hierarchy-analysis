# Level Overlap Analysis

## Summary

Analysis of levels 0-6 reveals significant hierarchy flexibility: **247 values appear at multiple levels**.

This explains why hierarchy content shifts around depending on section - the same organizational unit can appear at different depths depending on context.

---

## Overlap Patterns

### Major Overlapping Categories

#### 1. **Geographic Regions** (18 items)
**Appear at**: L2, L3, L4, L5, L6

- National Capital Region
- Region I through Region XIII (13 regions)
- Cordillera Administrative Region
- Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)
- Negros Island Region
- MIMAROPA Region

**Interpretation**: Regional designations can be:
- L2: Top-level regional grouping
- L3: Organizational unit under programs
- L4: Geographic context for projects
- L5: Regional allocation category
- L6: Specific district-level context

#### 2. **District Engineering Offices** (200+ items)
**Appear at**: L5, L6

All district offices like:
- Abra District Engineering Office
- Pangasinan 1st/2nd/3rd District Engineering Office
- Metro Manila 1st/2nd/3rd District Engineering Office
- [Province] [District] District Engineering Office

**Interpretation**: District offices can be:
- L5: Organizational district (parent to projects)
- L6: Context for specific projects (as leaf node)

#### 3. **Program Categories** (10+ items)
**Appear at**: L3, L4

- Asset Preservation Program
- Network Development Program
- Bridge Program
- Construction of Flyovers/Interchanges/Underpasses/Long Span Bridges

**Interpretation**: Programs can be:
- L3: Major programmatic division
- L4: Specific project type or category

#### 4. **Administrative Units** (5+ items)
**Appear at**: L3, L4, L5, L6

- Central Office
- GOP (General Obligations Program)
- Loan Proceeds

**Interpretation**: Administrative units appear at multiple organizational levels depending on budgeting context.

---

## Unique Values Per Level

| Level | Unique Values | Type |
|--------|---------------|------|
| 0 | 1 | Root |
| 1 | 9 | Major budget categories |
| 2 | 9 | Major divisions |
| 3 | 32 | Programs/Organizations |
| 4 | 113 | Program types/Groupings |
| 5 | 309 | Regions/Districts |
| 6 | 1,217 | Specific projects/Locations |

---

## Implications for Section-Based Analysis

### Problem with Level-Based Analysis

Current leaf-node approach treats all items uniformly across all sections. However:

1. **Depth varies by section**: Some sections go to L8, others stop at L6
2. **Same value at different levels**: "National Capital Region" appears 5 different times
3. **Context-dependent structure**: The hierarchy meaning changes based on section

### Recommended: Per-Section Analysis

#### Section Cut Points

Based on overlap analysis, recommended section cuts:

**Option 1: Cut by Level 1 (Major Categories)**
- 9 sections (one for each L1 value)
- Clear, high-level separation
- Each section has consistent structure
- Best for: Strategic/programmatic analysis

**Option 2: Cut by Level 2 (Major Divisions)**
- 9 sections (one for each L2 value)
- Slightly more granular than L1
- Still maintains consistency within sections
- Best for: Organizational analysis

**Option 3: Cut by Level 3 (Program Units)**
- 32 sections
- More detailed breakdown
- Programs like "Asset Preservation Program" as sections
- Best for: Program-focused analysis

**Option 4: Cut by Level 4 (Program Types)**
- 113 sections
- Most detailed high-level cut
- Each section focused on specific program type
- Best for: Detailed program analysis

### Recommended Approach: **Level 1 + Context**

For flexible yet structured analysis:

1. **Primary Cut**: Level 1 values (9 major sections)
2. **Within Each Section**: Use full hierarchy depth
3. **Normalize by Path**: Compare items within same section only
4. **Preserve Context**: Maintain ancestor path information

### Example Section: "OPERATIONS"

```
Section: OPERATIONS (Level 1)
├── CONVERGENCE AND SPECIAL SUPPORT PROGRAM (L2)
│   ├── Various programs (L3)
│   └── Project details (L6-L8)
├── FOREIGN-ASSISTED PROJECTS (L2)
│   └── Project details
├── Infrastructure Planning, Design... (L2)
│   ├── Programs (L3)
│   └── Geographic breakdowns (L4-L6)
└── Other programs...
```

Within this section:
- Some paths go to L8 (deep project details)
- Some stop at L6 (district-level allocations)
- Compare apples-to-apples: only within OPERATIONS section

---

## Implementation Strategy

### Step 1: Section Definition

```python
sections = [
    'CAPITAL OUTLAYS',
    'MAINTENANCE AND OTHER OPERATING EXPENSES',
    'OPERATIONS',
    'SUPPORT TO OPERATIONS',
    'GENERAL ADMINISTRATIVE AND SUPPORT',
    'PROGRAMS / ACTIVITIES / PROJECTS',
    # ... other L1 values
]
```

### Step 2: Filter by Section

```python
for section in sections:
    section_rows = [row for row in table if row['level_1'] == section]
    analyze_section(section_rows, section)
```

### Step 3: Section-Specific Analysis

For each section:
- Depth distribution (may vary from L4 to L8)
- Top paths within section
- Regional/district breakdown
- Budget allocation patterns

### Step 4: Cross-Section Comparison

Compare sections using normalized metrics:
- Budget share
- Number of items
- Average depth
- Top geographic allocations
- Top program types

---

## Data Quality Notes

### Normal Behavior

1. **Hierarchical flexibility**: Same value can appear at different depths
2. **Context-dependent meaning**: Level number alone doesn't define value type
3. **Section-specific depth**: Different sections have different maximum depths

### Not Data Issues

These overlaps are **not errors** but **design features**:
- Enables flexible hierarchy representation
- Allows same organization to appear in different contexts
- Supports varied reporting requirements

---

## Next Steps

1. ✅ **Identified overlaps**: 247 values at multiple levels
2. ⏳ **Implement per-section analysis**: Script to analyze each Level 1 section
3. ⏳ **Generate section reports**: 9 comprehensive section reports
4. ⏳ **Cross-section comparison**: Compare sections with normalized metrics
5. ⏳ **Visualization**: Create section-specific visualizations

---

## Summary

The hierarchy is **intentionally flexible**, with overlapping values allowing the same organizational unit to serve different roles depending on context:

- **Flexible depth**: Sections can go to different depths (L4-L8)
- **Multi-level values**: 247 values appear at 2+ levels
- **Context-dependent**: "Region" can be L2, L3, L4, L5, or L6

**Solution**: Use per-section analysis with Level 1 as primary cut point, preserving full hierarchical context within each section.
