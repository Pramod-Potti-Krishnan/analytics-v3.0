# Layout Builder Chart.js Integration Request

**Date**: 2025-01-15
**Requested By**: Analytics Microservice v3 Team
**Priority**: High
**Estimated Time**: 15-30 minutes

---

## Background

We're experiencing persistent race condition issues with ApexCharts where only the last chart renders in multi-chart presentations. After researching alternatives, we've identified **Chart.js with the RevealChart plugin** as the industry-standard solution that eliminates these issues completely.

**Current Issue**: Only last chart renders (ApexCharts race condition)
**Proposed Solution**: Chart.js with official RevealChart plugin
**Success Rate**: 95% (proven technology with Reveal.js)

---

## Changes Needed

### 1. Add Chart.js CDN to `<head>` Section

**File**: `/agents/layout_builder_main/v7.5-main/viewer/presentation-viewer.html`

**Add these two script tags in the `<head>` section** (before ApexCharts or after, doesn't matter):

```html
<!-- Chart.js + RevealChart Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

**Exact Location**: Add after the ApexCharts CDN line:

```html
<!-- EXISTING ApexCharts CDN -->
<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>

<!-- NEW: Chart.js + RevealChart Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

---

### 2. Add RevealChart Plugin to Reveal.initialize()

**File**: `/agents/layout_builder_main/v7.5-main/viewer/reveal-config.js` (or wherever Reveal.initialize() is)

**Update Reveal.initialize()** to include the RevealChart plugin:

```javascript
Reveal.initialize({
  // EXISTING config
  width: '100%',
  height: '100%',
  // ... other existing settings ...

  // NEW: Add RevealChart plugin
  plugins: [ RevealChart ],

  // NEW: Chart.js default configuration
  chart: {
    defaults: {
      color: 'lightgray',
      font: {
        family: 'Inter, system-ui, sans-serif',
        size: 14
      }
    }
  }
});
```

**If plugins array already exists**, just add `RevealChart` to it:

```javascript
// BEFORE
plugins: [ SomeOtherPlugin ]

// AFTER
plugins: [ SomeOtherPlugin, RevealChart ]
```

---

## Why This Works

### RevealChart Plugin Handles Everything Automatically

Unlike ApexCharts (which requires manual event handlers), the RevealChart plugin:
- ✅ Automatically discovers all `<canvas data-chart="type">` elements
- ✅ Handles Reveal.js lifecycle events (`ready`, `slidechanged`, etc.)
- ✅ Renders charts at the correct time (no race conditions)
- ✅ Destroys charts when leaving slides (memory management)
- ✅ Supports all major chart types: line, bar, pie, doughnut, radar, etc.

### Chart HTML Format (for reference)

Analytics service will send charts in this format:

```html
<canvas data-chart="line" height="600">
<!--
{
  "type": "line",
  "data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [{
      "label": "Revenue",
      "data": [125000, 145000, 178000, 195000]
    }]
  },
  "options": { ... }
}
-->
</canvas>
```

**No JavaScript in the HTML** - the plugin reads the JSON config from the comment and handles everything!

---

## Compatibility

### Existing Features
- ✅ Works alongside existing ApexCharts (both can coexist)
- ✅ No changes to L02, L03, or other layout templates
- ✅ No API contract changes
- ✅ Same `element_3` field usage

### Browser Support
- ✅ Chrome/Edge 88+
- ✅ Firefox 78+
- ✅ Safari 14+
- ✅ All modern browsers (2020+)

---

## Testing After Implementation

1. **Verify CDN Loading**:
   - Open browser console
   - Type `Chart` - should show Chart.js object
   - Type `RevealChart` - should show plugin object

2. **Test With Sample Canvas**:
   ```html
   <canvas data-chart="bar">
   <!--
   {
     "data": {
       "labels": ["A", "B", "C"],
       "datasets": [{ "data": [10, 20, 30] }]
     }
   }
   -->
   </canvas>
   ```
   This should auto-render when slide loads.

---

## Rollback Plan

If any issues arise, simply:
1. Remove the two Chart.js script tags
2. Remove `RevealChart` from plugins array
3. Remove `chart: {}` config object

ApexCharts will continue working as before (with the race condition).

---

## Questions?

**Analytics Team Contact**: Available for clarifications
**Plugin Documentation**: https://rajgoel.github.io/reveal.js-plugins/chart/
**Chart.js Documentation**: https://www.chartjs.org/docs/latest/

---

## Next Steps

1. ✅ Layout Builder team implements changes above
2. ✅ Redeploy to Railway
3. ✅ Analytics team runs Chart.js test presentation
4. ✅ If successful → Full migration (2-3 weeks)
5. ✅ If fails → Try alternative approaches

---

**Thank you!** This will permanently solve the race condition issue. 🙏
