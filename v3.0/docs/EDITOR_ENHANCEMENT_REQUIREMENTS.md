# Editor Enhancement Requirements for Scatter/Bubble Chart Support

**Date**: November 17, 2025 (Updated for v3.2.0)
**Target**: Layout Service Data Editor
**Priority**: 🟡 MEDIUM (Charts work, editor shows blank - not blocking rendering)
**Status**: ⏳ PENDING EDITOR TEAM IMPLEMENTATION

---

## v3.2.0 User Requirements - Column Specifications

**CRITICAL: User has specified exact column headers for scatter/bubble editors:**

### Scatter Chart Editor Requirements
**Columns to Display**:
1. **X** - X coordinate value (numeric, editable)
2. **Y** - Y coordinate value (numeric, editable)

**Do NOT show**:
- ❌ Label column (labels should not appear in scatter editor)
- ❌ [object Object] text anywhere

**Visual Appearance**:
- Points should display as **X (cross) marks**, not circles

### Bubble Chart Editor Requirements
**Columns to Display**:
1. **X** - X coordinate value (numeric, editable)
2. **Y** - Y coordinate value (numeric, editable)
3. **Value (size)** - Bubble radius/size (numeric, editable)

**Do NOT show**:
- ❌ Label column (labels should not appear in bubble editor)
- ❌ [object Object] text anywhere

**Visual Appearance**:
- Bubbles should vary in size based on value
- Bubbles should be clearly visible (70% opacity)

---

## Executive Summary

The Analytics Service uses **scatter** and **bubble** charts with object-based data points (`{x, y, label}` and `{x, y, r, label}`). These chart types render perfectly and display correctly, but the data editor shows blank fields because it only supports primitive value arrays.

**Current Fix** (v3.2.0): Fixed enforcement bug, scatter shows X marks, datalabels disabled
**Long-term Solution**: Enhance editor to parse and display object data points with correct column headers

---

## Problem Description

### Current Editor Limitation

The data editor expects this simple format:
```javascript
{
  "labels": ["Q1", "Q2", "Q3"],  // Top-level labels array
  "datasets": [{
    "data": [100, 150, 200]      // Simple primitive values
  }]
}
```

### Scatter/Bubble Chart Format

Scatter and bubble charts use object data points:
```javascript
// Scatter Chart
{
  "datasets": [{
    "data": [
      {"x": 0, "y": 95, "label": "Jan - $20K spend"},
      {"x": 1, "y": 124, "label": "Feb - $28K spend"}
    ]
  }]
  // NO top-level "labels" array
}

// Bubble Chart
{
  "datasets": [{
    "data": [
      {"x": 0, "y": 180, "r": 30, "label": "North America"},
      {"x": 1, "y": 145, "r": 29, "label": "Europe"}
    ]
  }]
}
```

### Why the Editor Fails

1. **No top-level labels array**: Editor looks for `data.labels` → not found → shows nothing
2. **Object data points**: Editor expects `datasets[0].data = [primitives]` → gets objects → can't parse
3. **No object property extraction**: Editor doesn't know how to extract `x`, `y`, `r`, `label` from objects
4. **Blank fields displayed**: User sees empty input fields instead of actual data

---

## Required Enhancements

### Option 1: Intelligent Data Parser (RECOMMENDED)

Enhance the editor to detect and parse different data formats:

**Detection Logic**:
```javascript
function detectDataFormat(chartData) {
  // Check if data points are objects
  if (chartData.datasets[0]?.data[0] && typeof chartData.datasets[0].data[0] === 'object') {
    const firstPoint = chartData.datasets[0].data[0];

    // Scatter chart: {x, y, label}
    if ('x' in firstPoint && 'y' in firstPoint) {
      return 'scatter';
    }

    // Bubble chart: {x, y, r, label}
    if ('x' in firstPoint && 'y' in firstPoint && 'r' in firstPoint) {
      return 'bubble';
    }
  }

  // Standard format: {labels, datasets: [{data: [primitives]}]}
  return 'standard';
}
```

**Scatter Chart Editor** (v3.2.0 Updated):
```javascript
function renderScatterEditor(data) {
  // Extract data from objects
  const points = data.datasets[0].data;

  // v3.2.0: Display ONLY X and Y columns (NO LABEL COLUMN)
  return (
    <table>
      <thead>
        <tr>
          <th>X</th>
          <th>Y</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {points.map((point, i) => (
          <tr key={i}>
            <td><input value={point.x} onChange={(e) => updateXValue(i, e.target.value)} /></td>
            <td><input value={point.y} onChange={(e) => updateYValue(i, e.target.value)} /></td>
            <td><button onClick={() => deletePoint(i)}>Delete</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Bubble Chart Editor** (v3.2.0 Updated):
```javascript
function renderBubbleEditor(data) {
  // Extract data from objects
  const points = data.datasets[0].data;

  // v3.2.0: Display X, Y, and Value (size) columns (NO LABEL COLUMN)
  return (
    <table>
      <thead>
        <tr>
          <th>X</th>
          <th>Y</th>
          <th>Value (size)</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {points.map((point, i) => (
          <tr key={i}>
            <td><input value={point.x} onChange={(e) => updateXValue(i, e.target.value)} /></td>
            <td><input value={point.y} onChange={(e) => updateYValue(i, e.target.value)} /></td>
            <td><input value={point.r} onChange={(e) => updateRadius(i, e.target.value)} /></td>
            <td><button onClick={() => deletePoint(i)}>Delete</button></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**Save Logic**:
```javascript
function saveScatterData(editedPoints) {
  return {
    "datasets": [{
      "label": "Correlation Data",
      "data": editedPoints.map((point, i) => ({
        "x": i,  // Auto-generate X as index
        "y": parseFloat(point.y),
        "label": point.label
      }))
    }]
  };
}

function saveBubbleData(editedPoints) {
  return {
    "datasets": [{
      "label": "Regional Performance",
      "data": editedPoints.map((point, i) => ({
        "x": i,  // Auto-generate X as index
        "y": parseFloat(point.y),
        "r": parseFloat(point.r),
        "label": point.label
      }))
    }]
  };
}
```

---

### Option 2: Fallback to Simple Format (NOT RECOMMENDED)

Convert scatter/bubble data to simple format when opening editor:

**Conversion Logic**:
```javascript
function convertToEditableFormat(chartData, chartType) {
  if (chartType === 'scatter' || chartType === 'bubble') {
    const points = chartData.datasets[0].data;

    return {
      "labels": points.map(p => p.label),
      "datasets": [{
        "data": points.map(p => p.y)
      }]
    };
  }

  return chartData;  // Already in simple format
}

function convertBackToScatter(editedData) {
  return {
    "datasets": [{
      "data": editedData.labels.map((label, i) => ({
        "x": i,
        "y": editedData.datasets[0].data[i],
        "label": label
      }))
    }]
  };
}
```

**Drawback**: Loses radius information for bubble charts

---

### Option 3: Display-Only Mode (TEMPORARY)

Show scatter/bubble data in read-only format with message:

```javascript
function renderReadOnlyEditor(data, chartType) {
  const points = data.datasets[0].data;

  return (
    <div className="read-only-editor">
      <div className="info-banner">
        ℹ️ {chartType} charts use a complex data structure.
        Enhanced editing coming soon.
      </div>

      <table>
        <thead>
          <tr>
            <th>Label</th>
            <th>Value</th>
            {chartType === 'bubble' && <th>Radius</th>}
          </tr>
        </thead>
        <tbody>
          {points.map((point, i) => (
            <tr key={i}>
              <td>{point.label}</td>
              <td>{point.y}</td>
              {chartType === 'bubble' && <td>{point.r}</td>}
            </tr>
          ))}
        </tbody>
      </table>

      <p>To edit, please use the Analytics Service API directly.</p>
    </div>
  );
}
```

---

## Implementation Roadmap

### Phase 1: Detection & Read-Only Display (Quick Win - 2-3 days)

1. Add format detection logic to editor
2. Detect scatter/bubble charts by checking for object data points
3. Show read-only table view with message
4. Provide "Edit via API" link or documentation

**Files to Modify**:
- `layout_service/editor/ChartEditor.tsx` (add format detection)
- `layout_service/editor/DataGrid.tsx` (add read-only scatter/bubble view)

**Testing**:
- Verify scatter charts show read-only view
- Verify bubble charts show read-only view with radius
- Verify other charts still editable

---

### Phase 2: Full Editable Support (Complete - 1-2 weeks)

1. Implement scatter chart editor with columns: Label, X-Value, Y-Value
2. Implement bubble chart editor with columns: Label, X-Value, Y-Value, Radius
3. Add save logic to convert back to object format
4. Add validation (numeric values, positive radius, etc.)
5. Add add/delete point functionality

**Files to Modify**:
- `layout_service/editor/ScatterEditor.tsx` (new file)
- `layout_service/editor/BubbleEditor.tsx` (new file)
- `layout_service/editor/ChartEditor.tsx` (routing logic)
- `layout_service/api/chartDataConverter.ts` (conversion utilities)

**Testing**:
- Verify scatter chart editing works end-to-end
- Verify bubble chart editing works end-to-end
- Verify data persistence after save
- Verify chart re-renders correctly after edit

---

## Current Workaround (v3.1.8)

**What We Fixed in Analytics Service**:
- Set `datalabels: {display: false}` for scatter/bubble charts
- Prevents `[object Object]` from appearing on the chart
- Charts render correctly with proper scatter/bubble visualization

**What Still Needs Fixing**:
- Editor shows blank fields when user clicks "Edit Data"
- Users cannot edit scatter/bubble chart data through the UI
- Users must use Analytics API directly to update data

**Impact**:
- 🟢 Charts display correctly (rendering not blocked)
- 🟡 Editor UX degraded (shows blank, but not critical)
- 🔵 Workaround: Users can edit via Analytics API

---

## Data Flow Examples

### Scatter Chart Data Flow

**Analytics Service Output** (v3.1.8):
```javascript
{
  "content": {
    "element_3": "<canvas>...</canvas>",  // Scatter chart HTML
    "element_2": "Observations..."
  },
  "metadata": {
    "analytics_type": "correlation_analysis",
    "chart_type": "scatter",
    "chart_data": {
      "datasets": [{
        "data": [
          {"x": 0, "y": 95, "label": "Jan - $20K"},
          {"x": 1, "y": 124, "label": "Feb - $28K"}
        ]
      }],
      "datalabels": {"display": false}  // ✅ No [object Object]
    }
  }
}
```

**Layout Service Editor** (CURRENT - shows blank):
```
┌──────────────────────────────────────┐
│ Edit Chart Data                      │
├──────────────────────────────────────┤
│ Labels:  [                        ]  │  ← BLANK (no labels array)
│ Data:    [                        ]  │  ← BLANK (can't parse objects)
│                                      │
│ [Cancel]              [Save Changes] │
└──────────────────────────────────────┘
```

**Layout Service Editor** (AFTER Option 1 - works):
```
┌──────────────────────────────────────┐
│ Edit Scatter Chart Data              │
├──────────────────────────────────────┤
│ Label            X-Value    Y-Value  │
│ Jan - $20K       0          95       │  ← Editable
│ Feb - $28K       1          124      │  ← Editable
│                                      │
│ [+ Add Point]    [Cancel]   [Save]  │
└──────────────────────────────────────┘
```

---

## Recommended Priority

**Priority**: 🟡 MEDIUM

**Rationale**:
- Charts render correctly (not blocking presentations)
- Users can view all data in the chart
- Users can edit via Analytics API (workaround exists)
- Editor UX degraded but not broken

**Timeline**:
- Phase 1 (Read-Only): 2-3 days
- Phase 2 (Full Edit): 1-2 weeks

**Dependencies**:
- None (Analytics Service v3.1.8 provides correct data)

---

## Contact

**For Questions**:
- Analytics Team: Fixed datalabels bug in v3.1.8
- Editor Team: Needs to implement Option 1 (recommended)

**Related Documentation**:
- `ANALYTICS_V3.1.8_COMPLETE.md` - Analytics Service fix
- Chart.js Scatter Documentation: https://www.chartjs.org/docs/latest/charts/scatter.html
- Chart.js Bubble Documentation: https://www.chartjs.org/docs/latest/charts/bubble.html

---

**Status**: ✅ Analytics Service fixed (v3.1.8)
**Status**: ⏳ Editor Enhancement pending (Editor Team)
**Blocking**: No (charts work, editor UX degraded)
