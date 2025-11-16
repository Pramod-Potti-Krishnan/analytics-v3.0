# Layout Builder ApexCharts CDN Addition Request

**Date**: 2025-01-15
**Priority**: HIGH
**Issue**: ApexCharts library not loaded when chart initialization scripts execute

---

## Problem

Console errors show:
```
ReferenceError: Can't find variable: ApexCharts
```

**Root Cause**: Chart initialization scripts execute before the ApexCharts CDN finishes loading, causing `ApexCharts` to be undefined.

---

## Solution

Add ApexCharts library to the viewer `<head>` section so it loads once for all charts.

---

## Changes Required

**File**: `viewer/presentation-viewer.html`

**Location**: In the `<head>` section, after Reveal.js scripts

**Add**:
```html
<!-- Reveal.js Core -->
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

<!-- ApexCharts Library (for Analytics charts) -->
<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>
```

---

## Why This Works

### Current Flow (BROKEN):
1. Slide HTML inserted with `<script src="apexcharts.min.js">`
2. Script execution extracts and executes scripts
3. ApexCharts CDN starts loading (async)
4. Chart initialization code runs immediately
5. ❌ `ApexCharts` is undefined → Error

### After Fix:
1. ApexCharts loads in `<head>` when page loads
2. Slide HTML inserted (no CDN script tag)
3. Chart initialization code runs
4. ✅ `ApexCharts` is already available → Charts render

---

## Benefits

- ✅ Loads ApexCharts once (not per slide)
- ✅ Guaranteed to load before any chart code executes
- ✅ Better performance (no duplicate CDN loads)
- ✅ Cleaner slide HTML (no redundant script tags)
- ✅ Works with script execution fix

---

## Analytics Changes

Analytics Microservice has **already been updated** to remove the CDN script tag from chart HTML:

**Before**:
```html
<div id="chart-xxx"></div>
<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>
<script>
  // Chart initialization
</script>
```

**After**:
```html
<div id="chart-xxx"></div>
<script>
  // Chart initialization (assumes ApexCharts is already loaded)
</script>
```

---

## Testing

### After Adding to Head:

1. **Verify Library Loaded**:
   - Open browser console
   - Type: `typeof ApexCharts`
   - Should return: `"function"` (not `"undefined"`)

2. **Test Presentation**:
   - Generate new chart presentation
   - Open in browser
   - Verify no `ReferenceError: Can't find variable: ApexCharts` errors
   - Confirm charts render correctly

3. **Check Network Tab**:
   - ApexCharts CDN should load once (in head)
   - No duplicate ApexCharts requests per slide

---

## Exact Code to Add

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Viewer - v7.5-main</title>

  <!-- Reveal.js Core -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">

  <!-- v7.5 Styles -->
  <link rel="stylesheet" href="/src/styles/core/reset.css">
  <link rel="stylesheet" href="/src/styles/core/grid-system.css">
  <link rel="stylesheet" href="/src/styles/core/borders.css">
  <link rel="stylesheet" href="/src/styles/content-area.css">

  <style>
    /* ... existing styles ... */
  </style>
</head>
<body>
  <!-- ... existing body content ... -->

  <!-- Reveal.js Core -->
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

  <!-- ⭐ ADD THIS LINE ⭐ -->
  <!-- ApexCharts Library (for Analytics charts) -->
  <script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>

  <!-- v7.5 Utilities -->
  <script src="/src/utils/format_ownership.js"></script>
  <script src="/src/core/reveal-config.js"></script>

  <!-- ... rest of existing scripts ... -->
</body>
</html>
```

---

## Summary

| Component | Action | Status |
|-----------|--------|--------|
| **Analytics Microservice** | Remove CDN script from chart HTML | ✅ Complete |
| **Layout Builder Viewer** | Add ApexCharts to `<head>` | ⏳ Required |

**One line to add** to fix all chart rendering issues!

---

## Contact

**Ready for immediate testing** once deployed.

Test presentation will be generated after deployment.
