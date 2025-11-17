# Data Labels Not Showing - Issue Diagnosis

**Date**: 2025-01-15
**Issue**: Data labels configured but not appearing on charts
**Status**: 🔴 INVESTIGATING

---

## Problem

User reports that data labels (exact values on bars/points) are NOT showing, even though:
- ✅ Axis titles showing ("Percentage (%)")
- ✅ Axis tick labels showing (0%, 10%, 20%)
- ✅ Grid lines showing
- ❌ Data labels on bars NOT showing (should show 35.5%, 28.3%, etc.)

---

## Diagnosis Steps

### Step 1: Verify Plugin is Loaded

**Required CDN**:
```html
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
```

**Check**:
1. Open browser console on presentation
2. Run: `typeof ChartDataLabels`
3. Should return `"object"` if loaded, `"undefined"` if not loaded

### Step 2: Verify Plugin Registration

The chartjs-plugin-datalabels plugin needs to be **registered** with Chart.js before use.

**Two Registration Methods**:

**Method A - Global Registration** (Preferred for RevealChart):
```javascript
// In presentation-viewer.html AFTER datalabels CDN loads
Chart.register(ChartDataLabels);
```

**Method B - Per-Chart Registration** (Our current approach):
```javascript
// In chart config
{
  type: "bar",
  plugins: [ChartDataLabels],  // Register per-chart
  options: { ... }
}
```

### Step 3: Check RevealChart Plugin Compatibility

RevealChart plugin may need the datalabels plugin to be globally registered.

---

## Root Cause Analysis

### Likely Issue #1: Plugin Not Globally Registered

**Current State**:
- chartjs-plugin-datalabels CDN added ✅
- BUT plugin not registered with Chart.js ❌

**What's Needed**:
Layout Builder needs to add ONE line after the datalabels CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
<script>
  // REQUIRED: Register datalabels plugin globally
  Chart.register(ChartDataLabels);
</script>
```

### Likely Issue #2: RevealChart Plugin Ignoring Inline Plugins

RevealChart plugin parses JSON config from HTML comments. It may not support inline plugin registration.

**Solution**: Global registration (see above)

---

## Solution: Update Layout Builder Request

### Required Changes in presentation-viewer.html

**Current (Not Working)**:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

**Required (Will Work)**:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- CRITICAL: Register datalabels plugin BEFORE RevealChart -->
<script>
  if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
    console.log('✅ ChartDataLabels plugin registered');
  } else {
    console.error('❌ Chart.js or ChartDataLabels not loaded');
  }
</script>

<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

---

## Verification Steps

After Layout Builder makes the change:

1. **Open browser console**
2. **Run**: `typeof ChartDataLabels`
   - Should return: `"object"` ✅
3. **Run**: `Chart.registry.plugins.get('datalabels')`
   - Should return: Plugin object ✅
4. **Check console logs**
   - Should see: `"✅ ChartDataLabels plugin registered"` ✅
5. **Reload presentation**
   - Data labels should now appear on all charts ✅

---

## Alternative Solution (If Global Registration Doesn't Work)

If global registration still doesn't work with RevealChart, we may need to:

1. **Switch to a different datalabels approach**:
   - Use Chart.js built-in label options (limited)
   - Or implement custom canvas drawing

2. **Modify chart generation**:
   - Remove datalabels config from options
   - Add labels using Chart.js annotations plugin instead

3. **Contact RevealChart plugin maintainer**:
   - Ask about datalabels plugin compatibility

---

## Temporary Workaround

While waiting for Layout Builder fix, we can verify the issue by:

1. **Creating a simple HTML test file** with global registration
2. **Testing locally** to confirm it works
3. **Then requesting Layout Builder to implement the same**

---

## Status

**Current**: ❌ Data labels not showing (plugin not registered)

**Waiting For**: Layout Builder to add `Chart.register(ChartDataLabels);` after plugin CDN

**Expected**: ✅ All data labels will appear once plugin is registered

---

## Files to Update

1. **Layout Builder**: `presentation-viewer.html` (add registration script)
2. **This repo**: Create updated request document for Layout Builder

---

**Next Action**: Create updated request for Layout Builder team with registration code.
