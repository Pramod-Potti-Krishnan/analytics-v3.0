# URGENT: Chart.js Datalabels Plugin Registration

**Date**: 2025-01-15
**Priority**: 🔴 HIGH - Data labels not showing on charts
**Estimated Time**: 2 minutes
**Issue**: Plugin CDN added but not registered

---

## Problem

The chartjs-plugin-datalabels CDN was added, but the plugin is **not registered** with Chart.js. This causes data labels to be invisible even though they're configured.

**Current Result**: Data labels don't show on any charts (see screenshot)
**Expected Result**: Data labels show exact values on all bars/points

---

## Required Fix

### Add Plugin Registration Script

**File**: `/agents/layout_builder_main/v7.5-main/viewer/presentation-viewer.html`

**Current Code** (in `<head>`):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

**Updated Code** (add registration between datalabels and RevealChart):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- CRITICAL: Register datalabels plugin globally -->
<script>
  if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
    console.log('✅ ChartDataLabels plugin registered globally');
  } else {
    console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    if (typeof Chart === 'undefined') console.error('   - Chart.js not found');
    if (typeof ChartDataLabels === 'undefined') console.error('   - ChartDataLabels not found');
  }
</script>

<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

**What This Does**:
1. Checks that both Chart.js and ChartDataLabels loaded successfully
2. Registers the datalabels plugin globally with Chart.js
3. Logs confirmation to console for debugging
4. MUST be placed AFTER datalabels CDN but BEFORE RevealChart plugin

---

## Why This Is Needed

Chart.js plugins (including chartjs-plugin-datalabels) must be **registered** before use. Simply loading the CDN is not enough.

**Without Registration**:
- Plugin CDN loads ✅
- Plugin object exists in memory ✅
- BUT Chart.js doesn't know to use it ❌
- Data labels don't appear ❌

**With Registration**:
- Plugin CDN loads ✅
- Plugin object exists in memory ✅
- Chart.js knows to use it ✅
- Data labels appear on all charts ✅

---

## Verification After Deployment

1. **Open any chart presentation**
2. **Open browser console** (F12)
3. **Look for log message**: `"✅ ChartDataLabels plugin registered globally"`
4. **Run in console**: `Chart.registry.plugins.get('datalabels')`
   - Should return: Plugin object (not undefined)
5. **Reload presentation**
   - Data labels should now appear on all bars/points

---

## Exact Line to Add

**Copy this entire block and paste it between the two script tags**:

```html
<!-- CRITICAL: Register datalabels plugin globally -->
<script>
  if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
    console.log('✅ ChartDataLabels plugin registered globally');
  } else {
    console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    if (typeof Chart === 'undefined') console.error('   - Chart.js not found');
    if (typeof ChartDataLabels === 'undefined') console.error('   - ChartDataLabels not found');
  }
</script>
```

**Placement**:
- AFTER: `<script src="...chartjs-plugin-datalabels..."></script>`
- BEFORE: `<script src="...reveal.js-plugins...chart/plugin.js"></script>`

---

## Expected Result

**Before Fix**:
- Axes and grid lines visible ✅
- Data labels on bars/points NOT visible ❌

**After Fix**:
- Axes and grid lines visible ✅
- Data labels on bars/points VISIBLE ✅
- Example: Bar chart shows "35.5%", "28.3%", "22.1%", "14.1%" on each bar

---

## Rollback

If any issues occur:
1. Remove the registration script block
2. Redeploy
3. Charts will work but without data labels (same as current state)

---

## Timeline

**Estimated Time**: 2 minutes to add the script
**Deployment**: Depends on Railway deployment time
**Testing**: 1 minute to verify in console

---

## Questions?

If there are any issues or questions:
1. Check browser console for error messages
2. Verify the script was added in the correct location
3. Confirm all three CDNs are loading (Chart.js, datalabels, RevealChart)

---

**Status**: ⏸️ Awaiting Layout Builder team to add registration script

**After deployment, please confirm by checking for the log message**:
`"✅ ChartDataLabels plugin registered globally"`
