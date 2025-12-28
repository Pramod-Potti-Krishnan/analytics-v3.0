# Layout Service: V2 Template Chart Rendering Fix Request

**Date**: 2025-12-28
**From**: Analytics Service Team
**Priority**: High
**Status**: C3 Fixed, V2 Needs Same Fix

---

## Summary

The `executeScriptsSequentially()` fix implemented for **C3 templates is working perfectly**. However, **V2 templates are not rendering charts** because the same fix has not been applied to the V2 renderer.

| Template | Chart Rendering | Edit Button | Status |
|----------|----------------|-------------|--------|
| C3-chart | ✅ Working | ✅ Working | Fixed |
| V2-chart-text | ❌ Not Working | ❌ Not Working | **Needs Fix** |

---

## The Problem

When chart HTML is inserted via `innerHTML`, embedded `<script>` tags are **not executed** by the browser. This is a security feature of the DOM.

The C3 renderer now has a fix that manually re-executes scripts after insertion. The V2 renderer needs the same fix.

---

## The Fix (Already Working in C3)

Apply this pattern wherever V2 inserts chart HTML:

```javascript
// After inserting chart HTML via innerHTML
if (chartHtml) {
  container.innerHTML = chartHtml;

  // Re-execute embedded scripts sequentially
  const scripts = container.querySelectorAll('script');
  const executeNextScript = (index) => {
    if (index >= scripts.length) return;

    const oldScript = scripts[index];
    const newScript = document.createElement('script');

    // Copy all attributes
    Array.from(oldScript.attributes).forEach(attr => {
      newScript.setAttribute(attr.name, attr.value);
    });

    if (oldScript.src) {
      // External script - wait for load before next
      newScript.onload = () => executeNextScript(index + 1);
      newScript.onerror = () => executeNextScript(index + 1);
    } else {
      // Inline script - execute immediately
      newScript.textContent = oldScript.textContent;
    }

    oldScript.parentNode.replaceChild(newScript, oldScript);

    if (!oldScript.src) {
      executeNextScript(index + 1);
    }
  };

  executeNextScript(0);
}
```

---

## Files to Check

Please check these locations in the Layout Service codebase:

1. **V2 Template Renderer**: `src/renderers/V2.js` (or similar)
2. **Element Manager**: Check if V2 uses `ElementManager.insertChart()` or a different method
3. **Template Loader**: Where V2 template content is injected

---

## Key Questions

1. **Does V2 use a different code path than C3?**
   - C3 might use `ElementManager.insertChart()`
   - V2 might use a different method or direct `innerHTML`

2. **Is the property name different?**
   - C3 might use `chartHtml` or `config.chartHtml`
   - V2 might use `element_3`, `chart_html`, or another property name

3. **Is V2 using a different container selector?**
   - The chart container in V2 might have a different class/ID

---

## Analytics Service Chart HTML Structure

Here's the complete structure of what the Analytics Service sends. All three `<script>` blocks must execute in order:

```html
<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">

  <!-- 1. Canvas Element -->
  <canvas id="chart-slide-X"></canvas>

  <!-- 2. Edit Button -->
  <button class="chart-edit-btn"
          onclick="openChartEditor_chart_slide_X()"
          style="position: absolute; top: 10px; left: 10px; ...">
    ✏️
  </button>

  <!-- 3. SCRIPT 1: Chart Initialization (MUST EXECUTE) -->
  <script>
    (function() {
      function initChart() {
        const ctx = document.getElementById('chart-slide-X').getContext('2d');
        const chartConfig = { /* Chart.js config */ };
        const chart = new Chart(ctx, chartConfig);

        // Store for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide-X'] = chart;
      }

      // Reveal.js integration
      if (typeof Reveal !== 'undefined') {
        Reveal.on('ready', function() { /* ... */ });
        Reveal.on('slidechanged', function() { /* ... */ });
      } else {
        initChart();
      }
    })();
  </script>

  <!-- 4. SCRIPT 2: External Editor Library (MUST LOAD) -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- 5. SCRIPT 3: Editor Function Definitions (MUST EXECUTE) -->
  <script>
    (function() {
      window.openChartEditor_chart_slide_X = function() {
        // Opens Excel-like editor modal
      };

      function extractChartData_chart_slide_X(chart) {
        // Extracts data from chart instance
      }

      function updateChartData_chart_slide_X(chart, newData, chartType) {
        // Updates chart with edited data
      }
    })();
  </script>
</div>
```

**Execution Order is Critical:**
1. Script 1 creates the chart and stores in `window.chartInstances`
2. Script 2 loads the external editor library (`openChartEditor` function)
3. Script 3 defines the slide-specific editor function that uses both

If scripts don't execute in order, the edit button won't work.

---

## How to Verify the Fix

After applying the fix to V2:

1. Create a new presentation with V2-chart-text slides
2. Check browser console for:
   - `✅ Chart chart-slide-X initialized successfully`
3. Click the edit button (✏️) - should open Excel-like editor
4. Verify chart renders on the left side of V2 layout

---

## Test Presentation

After fix is deployed, test with a new presentation containing both C3 and V2 slides to confirm both work.

---

## Contact

For questions about the chart HTML structure or Analytics Service:
- **Analytics Service**: `https://analytics-v30-production.up.railway.app`
- **Health Check**: `GET /health`

---

*Document prepared: 2025-12-28*
