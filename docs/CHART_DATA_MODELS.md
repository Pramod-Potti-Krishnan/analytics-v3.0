# Chart Data Models - Table Structures for All 18 Chart Types

**Version**: 1.0
**Date**: 2025-11-28
**Purpose**: Define the exact table/spreadsheet structure needed for each chart type in the Analytics Microservice

---

## Overview

This document defines the **data table structure** (columns and rows) required for each of the 18 supported chart types. This serves as the specification for:
- Excel-like editor interface
- Synthetic data generation
- Data validation
- API request/response formats

---

## Table Structure Categories

### Category 1: Simple Label-Value Format (13 Chart Types)

**Chart Types**:
- `line` - Line Chart
- `bar_vertical` - Vertical Bar Chart
- `bar_horizontal` - Horizontal Bar Chart
- `pie` - Pie Chart
- `doughnut` - Doughnut Chart
- `radar` - Radar Chart
- `polar_area` - Polar Area Chart
- `area` - Area Chart
- `waterfall` - Waterfall Chart
- `d3_treemap` - D3 Treemap
- `d3_sunburst` - D3 Sunburst
- `d3_choropleth_usa` - D3 USA Choropleth Map

**Table Structure**:

| # | Label | Value | Actions |
|---|-------|-------|---------|
| 1 | Q1 2024 | 125000 | 🗑️ |
| 2 | Q2 2024 | 145000 | 🗑️ |
| 3 | Q3 2024 | 162000 | 🗑️ |
| 4 | Q4 2024 | 180000 | 🗑️ |

**Column Definitions**:
- **#**: Row number (auto-generated, read-only)
- **Label**: String - Category name, time period, or identifier (required, editable)
- **Value**: Number - Numeric value for the data point (required, editable)
- **Actions**: Delete button (functional, not data)

**Special Cases**:

#### D3 Choropleth USA (`d3_choropleth_usa`)
| # | State | Value | Actions |
|---|-------|-------|---------|
| 1 | California | 500000 | 🗑️ |
| 2 | Texas | 420000 | 🗑️ |
| 3 | New York | 380000 | 🗑️ |

- **State** column instead of **Label**
- Must use valid US state names (full or abbreviated)

#### D3 Treemap/Sunburst - Hierarchical Format
For hierarchical charts, labels can use parent.child notation:

| # | Label | Value | Actions |
|---|-------|-------|---------|
| 1 | Revenue | 1000000 | 🗑️ |
| 2 | Revenue.Sales | 600000 | 🗑️ |
| 3 | Revenue.Services | 400000 | 🗑️ |
| 4 | Costs | 700000 | 🗑️ |
| 5 | Costs.Operations | 450000 | 🗑️ |

- Period (`.`) in label denotes parent-child relationship
- Parent nodes automatically calculated as sum of children

**Highlighted Columns**: Label, Value (both highlighted as active data)

---

### Category 2: Scatter Format (1 Chart Type)

**Chart Types**:
- `scatter` - Scatter Plot

**Table Structure**:

| # | X | Y | Actions |
|---|---|---|---------|
| 1 | 45 | 85 | 🗑️ |
| 2 | 60 | 75 | 🗑️ |
| 3 | 72 | 92 | 🗑️ |
| 4 | 55 | 68 | 🗑️ |

**Column Definitions**:
- **#**: Row number (auto-generated, read-only)
- **X**: Number - X-axis value (required, editable)
- **Y**: Number - Y-axis value (required, editable)
- **Actions**: Delete button (functional, not data)

**Notes**:
- No label column (scatter plots use point index as identifier)
- Points are numbered automatically (Point 1, Point 2, etc.)
- Both X and Y must be numeric values

**Highlighted Columns**: X, Y (both highlighted as active data)

---

### Category 3: Bubble Format (1 Chart Type)

**Chart Types**:
- `bubble` - Bubble Chart

**Table Structure**:

| # | Label | X | Y | Radius | Actions |
|---|-------|---|---|--------|---------|
| 1 | Product A | 45 | 85 | 15 | 🗑️ |
| 2 | Product B | 60 | 75 | 20 | 🗑️ |
| 3 | Product C | 72 | 92 | 12 | 🗑️ |
| 4 | Product D | 55 | 68 | 25 | 🗑️ |

**Column Definitions**:
- **#**: Row number (auto-generated, read-only)
- **Label**: String - Bubble identifier/name (required, editable)
- **X**: Number - X-axis position (required, editable)
- **Y**: Number - Y-axis position (required, editable)
- **Radius**: Number - Bubble size (required, editable, positive values)
- **Actions**: Delete button (functional, not data)

**Notes**:
- Label column added in v3.3.2 for bubble identification
- Radius determines bubble size (typically 5-30 for good visibility)
- All numeric columns (X, Y, Radius) must be numbers

**Highlighted Columns**: Label, X, Y, Radius (all highlighted as active data)

---

### Category 4: Multi-Series Format (3 Chart Types)

**Chart Types**:
- `bar_grouped` - Grouped Bar Chart
- `bar_stacked` - Stacked Bar Chart
- `area_stacked` - Stacked Area Chart

**Table Structure** (Dynamic columns based on number of series):

| # | Label | 2023 Revenue | 2024 Revenue | Actions |
|---|-------|-------------|-------------|---------|
| 1 | Q1 | 100000 | 125000 | 🗑️ |
| 2 | Q2 | 120000 | 145000 | 🗑️ |
| 3 | Q3 | 140000 | 170000 | 🗑️ |
| 4 | Q4 | 160000 | 195000 | 🗑️ |

**Column Definitions**:
- **#**: Row number (auto-generated, read-only)
- **Label**: String - Category name (required, editable)
- **Series 1, 2, ... N**: Number - Values for each data series (dynamic, editable)
- **Actions**: Delete button and **Add Column** button

**Dynamic Series Columns**:
- Number of series columns is variable (minimum 1, typically 2-5)
- Column headers are series names (e.g., "2023 Revenue", "2024 Revenue")
- Users can add new series columns via "+ Add Series" button
- Each series column accepts numeric values

**Editor Features**:
- **Add Series Button**: Allows adding new series column (appears in table header)
- **Delete Series**: Right-click column header to delete (minimum 1 series must remain)
- **Rename Series**: Double-click column header to rename

**Notes**:
- For grouped bars: series shown side-by-side
- For stacked bars/areas: series stacked on top of each other
- All series should have same number of data points (rows)

**Highlighted Columns**: Label + all series columns highlighted as active data

---

### Category 5: Sankey Flow Format (1 Chart Type)

**Chart Types**:
- `d3_sankey` - D3 Sankey Diagram (Flow Diagram)

**Table Structure**:

| # | Source | Target | Value | Actions |
|---|--------|--------|-------|---------|
| 1 | Revenue | Engineering | 450000 | 🗑️ |
| 2 | Revenue | Sales | 320000 | 🗑️ |
| 3 | Revenue | Marketing | 230000 | 🗑️ |
| 4 | Engineering | Projects | 200000 | 🗑️ |
| 5 | Engineering | Infrastructure | 150000 | 🗑️ |
| 6 | Sales | Direct Sales | 180000 | 🗑️ |

**Column Definitions**:
- **#**: Row number (auto-generated, read-only)
- **Source**: String - Starting node name (required, editable)
- **Target**: String - Ending node name (required, editable)
- **Value**: Number - Flow amount/thickness (required, editable, positive)
- **Actions**: Delete button (functional, not data)

**Notes**:
- Each row represents a flow connection between two nodes
- Source and Target can appear in multiple rows
- Node names are case-sensitive
- Flows are directional (Source → Target)
- Value determines the width/thickness of the flow link

**Data Validation**:
- Source ≠ Target (cannot flow to itself)
- Value must be positive number
- Circular flows are allowed (A→B, B→C, C→A) but may need special handling

**Highlighted Columns**: Source, Target, Value (all highlighted as active data)

---

## Excel-Like Editor Column Highlighting Rules

### Active Data Columns (Highlighted)
Columns that directly contribute to the chart visualization should be highlighted with:
- **Background**: Light yellow (#fffacd) or light green (#e8f5e9)
- **Border**: Slightly darker border to indicate active area
- **Header**: Bold text with subtle icon (✓ or ★)

### Inactive/Extra Columns (Not Highlighted)
Any additional columns beyond the chart's requirements:
- **Background**: White or light gray (#f5f5f5)
- **Border**: Standard border
- **Behavior**: Still editable but visually de-emphasized

### Examples:

#### Line Chart
| # | **Label** ✓ | **Value** ✓ | Extra Column | Actions |
|---|------------|-------------|--------------|---------|
|   | Highlighted | Highlighted | Not highlighted | N/A |

#### Bubble Chart
| # | **Label** ✓ | **X** ✓ | **Y** ✓ | **Radius** ✓ | Extra | Actions |
|---|------------|---------|---------|-------------|-------|---------|
|   | Highlighted | Highlighted | Highlighted | Highlighted | Not highlighted | N/A |

---

## Data Validation Rules

### All Chart Types
1. **Minimum Rows**: 2 data points (enforced by `chart_catalog.py` constraints)
2. **Maximum Rows**: 50 data points (system limit)
3. **Empty Cells**: Not allowed in required columns
4. **Numeric Validation**: Number columns reject non-numeric input
5. **NaN/Infinity**: Rejected (return validation error)

### Chart-Specific Rules

#### Line/Area Charts
- Labels should be sequential (time series) for best visualization
- Values can be negative for trend lines

#### Pie/Doughnut Charts
- Values must be positive
- Values automatically converted to percentages
- Minimum 2 slices, maximum 12 slices recommended

#### Scatter/Bubble Charts
- X and Y can be any numeric range
- Bubble radius must be positive (> 0)

#### Bar Charts
- Values can be negative (for waterfall/comparison)
- Grouped/Stacked: All series must have same row count

#### D3 Choropleth
- State names must match valid US states
- Invalid states will be grayed out on map

#### D3 Sankey
- Source and Target must be non-empty strings
- Value must be positive
- No self-loops (Source ≠ Target)

---

## JSON Data Format Mapping

### Simple Format → JSON
**Table**:
| Label | Value |
|-------|-------|
| Q1 | 100 |
| Q2 | 120 |

**JSON**:
```json
{
  "data": [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 120}
  ]
}
```

### Multi-Series Format → JSON
**Table**:
| Label | 2023 | 2024 |
|-------|------|------|
| Q1 | 100 | 125 |
| Q2 | 120 | 145 |

**JSON**:
```json
{
  "data": [{
    "labels": ["Q1", "Q2"],
    "datasets": [
      {"label": "2023", "data": [100, 120]},
      {"label": "2024", "data": [125, 145]}
    ]
  }]
}
```

### Bubble Format → JSON
**Table**:
| Label | X | Y | Radius |
|-------|---|---|--------|
| A | 45 | 85 | 15 |
| B | 60 | 75 | 20 |

**JSON**:
```json
{
  "data": [{
    "labels": ["A", "B"],
    "datasets": [{
      "label": "Performance",
      "data": [
        {"x": 45, "y": 85, "r": 15},
        {"x": 60, "y": 75, "r": 20}
      ]
    }]
  }]
}
```

### Scatter Format → JSON
**Table**:
| X | Y |
|---|---|
| 45 | 85 |
| 60 | 75 |

**JSON**:
```json
{
  "data": [{
    "labels": ["Point 1", "Point 2"],
    "datasets": [{
      "label": "Data Points",
      "data": [
        {"x": 45, "y": 85},
        {"x": 60, "y": 75}
      ]
    }]
  }]
}
```

### Sankey Format → JSON
**Table**:
| Source | Target | Value |
|--------|--------|-------|
| A | B | 100 |
| B | C | 50 |

**JSON**:
```json
{
  "data": [
    {"label": "A → B", "value": 100},
    {"label": "B → C", "value": 50}
  ]
}
```

---

## Implementation Guidelines for Excel Editor

### Table Rendering
1. **Dynamic Headers**: Generate column headers based on chart type
2. **Row Numbering**: Auto-increment row numbers, update on delete
3. **Editable Cells**: All data cells should be `<input>` elements or contenteditable
4. **Action Column**: Always last column, contains delete row button

### User Interactions
1. **Double-click cell**: Enter edit mode
2. **Enter key**: Save cell, move to next row
3. **Tab key**: Save cell, move to next column
4. **Arrow keys**: Navigate cells (when not editing)
5. **Ctrl+C/V**: Copy/paste support from Excel
6. **Delete key**: Clear cell content (not delete row)

### Add/Delete Operations
1. **Add Row**: "+ Add Row" button below table
2. **Delete Row**: Trash icon in Actions column
3. **Add Column**: For multi-series charts only, "+ Add Series" in header
4. **Delete Column**: Right-click column header (multi-series only)

### Data Sync
1. **Auto-save**: Save on blur (cell loses focus)
2. **Batch save**: "Save & Update Chart" button applies all changes
3. **Cancel**: "Cancel" button reverts to original data
4. **Validation**: Validate on save, show inline errors

### Highlighting Implementation
1. **Column classes**: Add `active-column` class to highlighted columns
2. **CSS styling**: Apply yellow/green background to active columns
3. **Header icons**: Add ✓ or ★ to active column headers
4. **Row highlighting**: Highlight entire row on hover

---

## Summary Table: Chart Type → Columns Mapping

| Chart Type | Columns | Notes |
|-----------|---------|-------|
| **line** | Label, Value | Time series recommended |
| **bar_vertical** | Label, Value | Standard categorical |
| **bar_horizontal** | Label, Value | Standard categorical |
| **pie** | Label, Value | Values → percentages |
| **doughnut** | Label, Value | Values → percentages |
| **scatter** | X, Y | No labels |
| **bubble** | Label, X, Y, Radius | 4 dimensions |
| **radar** | Label, Value | Normalized 0-100 |
| **polar_area** | Label, Value | Cyclical data |
| **area** | Label, Value | Fill under line |
| **area_stacked** | Label, Series1, Series2, ... | Multi-series |
| **bar_grouped** | Label, Series1, Series2, ... | Multi-series |
| **bar_stacked** | Label, Series1, Series2, ... | Multi-series |
| **waterfall** | Label, Value | Incremental changes |
| **d3_treemap** | Label, Value | Hierarchical (parent.child) |
| **d3_sunburst** | Label, Value | Hierarchical (parent.child) |
| **d3_choropleth_usa** | State, Value | US state names |
| **d3_sankey** | Source, Target, Value | Flow diagram |

---

## Version History

- **v1.0** (2025-11-28): Initial documentation for Excel-like editor implementation
  - Defined table structures for all 18 chart types
  - Documented column highlighting rules
  - Specified data validation requirements
  - Created JSON mapping examples

---

## References

- `chart_catalog.py` - Chart type definitions and constraints
- `chartjs_generator.py` - Chart rendering and current editor implementation
- `synthetic_data_generator/` - Synthetic data generation patterns
- `docs/DATA_FORMATS_REFERENCE.md` - Comprehensive data format examples
