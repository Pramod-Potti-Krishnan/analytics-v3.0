# Layout Service CDN Fix Required - Mixed & D3 Sunburst Charts

**Date**: November 27, 2025
**From**: Analytics Service Team
**To**: Layout Service Team
**Priority**: P0 - CRITICAL
**Affects**: 2 chart types (mixed, d3_sunburst)

---

## Executive Summary

Two chart types are broken due to Layout Service CDN configuration issues:

1. **mixed chart** - Renders as line chart instead of line + bar combination
2. **d3_sunburst chart** - Renders as bar chart instead of circular sunburst diagram

Both charts show console errors for wrong CDN plugin loading:
```
[Error] Failed to load resource: chartjs-chart-box-and-violin-plot.min.js (404)
[Error] Refused to execute ... Content-Type is not a script MIME type
```

**Root Cause**: Layout Service loads box-and-violin-plot plugin globally for ALL presentations, and is missing D3.js library needed for sunburst charts.

---

## Investigation Results

### File Affected
**Path**: `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/layout_builder_main/v7.5-main/viewer/presentation-viewer.html`

**Lines 111-121**: Static CDN script loading

### Current Code (PROBLEMATIC)

```html
<!-- Chart.js + Plugins (for Analytics charts) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- Chart.js Extended Chart Type Plugins -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2.0.1/dist/chartjs-chart-matrix.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js"></script> <!-- ⚠️ CAUSES ERROR -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.0/dist/chartjs-chart-financial.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.11.0/dist/chartjs-chart-sankey.min.js"></script>
```

### Issues Identified

#### Issue 1: Box-and-Violin Plugin Loaded Globally
- **Problem**: Line 118 loads `chartjs-chart-box-and-violin-plot@3.0.0` on EVERY presentation
- **Impact**: Causes 404 error when CDN fails to load or has MIME type issues
- **Affects**: All presentations, even those without boxplot/violin charts
- **For mixed chart**: Not needed - Chart.js 4.4.0 supports mixed charts natively
- **For d3_sunburst**: Not needed - uses D3.js, not Chart.js

#### Issue 2: Missing D3.js Library
- **Problem**: No D3.js CDN script in template
- **Impact**: d3_sunburst charts cannot render (fallback to bar chart)
- **Required**: `https://cdn.jsdelivr.net/npm/d3@7`
- **Note**: Analytics Service includes D3.js in its HTML, but may be overridden or not executing

---

## Why This Happens

### Layout Service Architecture
Layout Service uses a **"load everything" static approach**:
1. All Chart.js plugins loaded in HTML template header
2. No logic to detect chart types in presentations
3. No dynamic/conditional CDN loading
4. Template designed for original 13 chart types (Nov 19, 2025 update)
5. Never updated when mixed/d3_sunburst were added

### Evidence
From `ANALYTICS_DATA_UNPACKING_BUG.md` (Lines 504-520):
- Box-and-violin plugin was added Nov 19, 2025
- Added to support boxplot charts
- Works for boxplot but breaks mixed/d3_sunburst

---

## Recommended Fixes

### Option 1: Quick Fix (Recommended)

**Add D3.js, Keep Existing Plugins**

Modify `presentation-viewer.html` lines 111-121:

```html
<!-- Chart.js + Plugins (for Analytics charts) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- D3.js Library (for d3_sunburst, d3_treemap, d3_choropleth charts) -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

<!-- Chart.js Extended Chart Type Plugins -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2.0.1/dist/chartjs-chart-matrix.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.0/dist/chartjs-chart-financial.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.11.0/dist/chartjs-chart-sankey.min.js"></script>
```

**Pros**:
- Simple one-line addition
- Fixes d3_sunburst charts
- Mixed charts will work (Chart.js 4.4.0 native support)
- Minimal code changes
- No risk of breaking existing charts

**Cons**:
- Still loads box-and-violin plugin even if not needed
- Adds ~50KB D3.js library to all presentations
- No performance optimization

**Estimated Time**: 5 minutes

---

### Option 2: Conditional Loading (Better Long-Term)

**Implement Dynamic Plugin Detection**

Add JavaScript to detect chart types and load only required plugins:

```html
<script>
  // Parse presentation data to detect chart types
  const chartTypes = new Set();
  if (window.presentationData && window.presentationData.slides) {
    window.presentationData.slides.forEach(slide => {
      if (slide.content && slide.content.metadata) {
        chartTypes.add(slide.content.metadata.chart_type);
      }
    });
  }

  // CDN mapping
  const pluginCDNs = {
    'boxplot': 'https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js',
    'violin': 'https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js',
    'd3_sunburst': 'https://cdn.jsdelivr.net/npm/d3@7',
    'd3_treemap': 'https://cdn.jsdelivr.net/npm/d3@7',
    'd3_choropleth_usa': 'https://cdn.jsdelivr.net/npm/d3@7',
    'sankey': 'https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.11.0/dist/chartjs-chart-sankey.min.js'
  };

  // Load required plugins
  const scriptsToLoad = new Set();
  chartTypes.forEach(type => {
    if (pluginCDNs[type]) {
      scriptsToLoad.add(pluginCDNs[type]);
    }
  });

  // Inject scripts dynamically
  scriptsToLoad.forEach(url => {
    const script = document.createElement('script');
    script.src = url;
    document.head.appendChild(script);
  });
</script>
```

**Pros**:
- Loads only required plugins
- Better performance (fewer HTTP requests)
- Scalable for future chart types
- No unused plugin errors

**Cons**:
- More complex implementation
- Requires testing across all chart types
- Async loading may cause race conditions

**Estimated Time**: 2-3 hours

---

### Option 3: Remove Template CDNs (Analytics-Owned)

**Let Analytics Service Handle All CDNs**

Remove all Chart.js plugin CDNs from template, rely on Analytics to include them inline:

```html
<!-- Base Chart.js only -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- All other plugins loaded by Analytics Service inline -->
```

**Pros**:
- Layout Service is CDN-agnostic
- Analytics owns full rendering stack
- No duplicate script loading
- Simpler Layout Service maintenance

**Cons**:
- Requires Analytics Service changes
- Larger HTML payloads from Analytics
- Duplicate CDN loads if multiple charts use same plugin
- Coordination between teams needed

**Estimated Time**: 4-6 hours (both teams)

---

## Recommended Action Plan

### Immediate Fix (Today)
1. Add D3.js CDN to `presentation-viewer.html` (Option 1)
2. Deploy to production
3. Test mixed and d3_sunburst charts
4. Verify no console errors

### Short-Term (Next Sprint)
1. Implement conditional plugin loading (Option 2)
2. Test across all 18 chart types
3. Measure performance improvement
4. Deploy with feature flag

### Long-Term (Next Quarter)
1. Consider Analytics-owned CDN approach (Option 3)
2. Coordinate with Analytics team
3. Design unified CDN strategy
4. Implement and test thoroughly

---

## Testing Checklist

After applying fix, verify:

### Mixed Chart
- [ ] Renders with line and bar elements (not just line)
- [ ] Revenue shows as line
- [ ] Costs show as bars
- [ ] No console errors
- [ ] Editor works correctly
- [ ] Can add/edit/delete data points

### D3 Sunburst Chart
- [ ] Renders as circular sunburst diagram (not bar chart)
- [ ] Shows hierarchical data correctly
- [ ] Interactive hover works
- [ ] No console errors
- [ ] Displays all segments
- [ ] Colors applied correctly

### Other Charts (Regression Testing)
- [ ] Boxplot still works (if box-and-violin kept)
- [ ] All 16 working chart types still render
- [ ] No new console errors introduced
- [ ] Performance impact minimal

---

## Error Messages to Fix

### Before Fix
```
[Error] Failed to load resource: the server responded with a status of 404 ()
  (chartjs-chart-box-and-violin-plot.min.js, line 0)

[Error] Refused to execute
  https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js
  as script because "X-Content-Type-Options: nosniff" was given
  and its Content-Type is not a script MIME type.
```

### After Fix (Expected)
```
✅ Chart.js 4.4.0 loaded
✅ D3.js v7 loaded
✅ ChartDataLabels plugin registered
✅ All required plugins loaded
```

---

## Impact Analysis

### Current State
- **Working Charts**: 12 of 18 (67%)
- **Broken Charts**: 6 of 18 (33%)
  - 4 from Analytics Service (fixed in v3.4.4)
  - 2 from Layout Service (mixed, d3_sunburst)

### After Fix
- **Working Charts**: 16 of 18 (89%)
- **Broken Charts**: 2 of 18 (11%)
  - d3_choropleth_usa (not implemented)
  - d3_sankey (plugin issue)

### User Impact
- **Users Affected**: Anyone using mixed or d3_sunburst charts
- **Severity**: High - charts completely non-functional
- **Workaround**: None (charts don't render correctly)
- **Fix Urgency**: P0 - Deploy ASAP

---

## Files Provided

1. **This Document**: `LAYOUT_SERVICE_CDN_FIX_REQUIRED.md`
2. **Analytics Fix**: Already deployed in v3.4.4
3. **Test URLs**: Provided by Director team
   - mixed: https://web-production-f0d13.up.railway.app/p/34796d89-c613-47d4-85f2-a3dea38db976
   - d3_sunburst: https://web-production-f0d13.up.railway.app/p/c3211cd0-db92-4f6e-84dd-34cbe7c9a4a4

---

## Questions for Layout Service Team

1. **Preferred Solution**: Option 1 (quick), Option 2 (conditional), or Option 3 (Analytics-owned)?
2. **Timeline**: Can Option 1 be deployed today? This week?
3. **Testing Resources**: Who will test across all chart types after fix?
4. **Deployment Process**: Railway auto-deploy or manual trigger?
5. **Rollback Plan**: Can we revert quickly if issues arise?

---

## Contact Information

**Analytics Service Team**
- Repository: https://github.com/Pramod-Potti-Krishnan/analytics-v3.0.git
- Version: v3.4.4
- Status: Data transformation fixes deployed

**Layout Service Team**
- Location: `/agents/layout_builder_main/v7.5-main`
- File to Modify: `viewer/presentation-viewer.html`
- Lines: 111-121 (CDN scripts)

**Director Service Team**
- Version: v3.4
- Status: Awaiting Layout Service fix for 2 remaining charts

---

## Appendix: Why Analytics Service Cannot Fix This

The Analytics Service generates chart HTML with inline `<script>` tags that include:
- Chart.js initialization
- Data configuration
- Chart options

However, the Layout Service template loads CDN scripts BEFORE Analytics HTML is injected. This creates a race condition where:
1. Box-and-violin plugin tries to load (fails with 404)
2. Browser console shows error
3. Chart.js may not initialize correctly
4. D3.js is not loaded at all (for sunburst)

Analytics Service cannot control:
- What scripts Layout Service loads globally
- When those scripts execute
- Error handling for failed CDN loads

Therefore, the fix MUST be in Layout Service template.

---

**Report Generated**: November 27, 2025
**Status**: ⏳ Awaiting Layout Service Team Action
**Expected Resolution**: Add D3.js CDN (1 line change, 5 minutes)
**Expected Outcome**: 16 of 18 charts working (89% success rate)
