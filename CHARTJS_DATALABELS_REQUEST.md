# Chart.js Datalabels Plugin - Additional CDN Request

**Date**: 2025-01-15
**Priority**: Medium
**Estimated Time**: 5 minutes

---

## Purpose

To show data values directly on charts (numbers on each point, bar, or segment), we need to add the Chart.js Datalabels plugin.

---

## Changes Needed

### Add Datalabels Plugin CDN to `<head>`

**File**: `/agents/layout_builder_main/v7.5-main/viewer/presentation-viewer.html`

**Add this script tag** (after the Chart.js CDN):

```html
<!-- Chart.js CDN (already added) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>

<!-- NEW: Chart.js Datalabels Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- RevealChart Plugin (already added) -->
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

**Exact line to add**:
```html
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
```

---

## What This Enables

With the datalabels plugin, charts will show:

- **Line Charts**: Values on each data point ($125K, $145K, etc.)
- **Bar Charts**: Values on top of each bar ($450K, $380K, etc.)
- **Doughnut Charts**: Percentages in each segment (45%, 30%, 25%)

**Example**:
- Without plugin: Only see values on hover
- With plugin: See all values directly on the chart

---

## Testing After Implementation

Open browser console and verify:
```javascript
typeof Chart.plugins.get('datalabels')
// Should return "object" (not undefined)
```

---

## Rollback

If any issues, simply remove the datalabels script tag. Charts will still render but without data labels.

---

**Time**: ~5 minutes
**Impact**: Enhances chart readability with visible data labels
