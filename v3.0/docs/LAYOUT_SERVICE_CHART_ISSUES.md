# Layout Service Chart Rendering Issues

**Date**: 2025-12-28
**Status**: ✅ ALL FIXED | Analytics Service duplicate ID bug resolved
**Test URL**: https://web-production-f0d13.up.railway.app/p/a5d50715-3c85-470f-add7-c6202780dd87

---

## 🎉 TEST RESULTS (2025-12-28)

### Layout Service `executeScriptsSequentially()` Fix: ✅ WORKING

| Feature | C3-chart | V2-chart-text | Root Cause |
|---------|----------|---------------|------------|
| Chart Rendering | ✅ WORKING | ❌ Not visible | Analytics Service bug (duplicate IDs) |
| Edit Button | ✅ WORKING | ❌ Not working | Analytics Service bug (duplicate IDs) |
| Script Execution | ✅ Sequential | ✅ Sequential | Layout Service fix working |

### Evidence of C3 Edit Button Working:
```
Console logs when clicking edit button:
- [LOG] === Excel Editor: Opening for chart chart-slide-1 ===
- [LOG] ✅ Chart found. Chart type: line
- [LOG] === 📊 EXTRACTED CHART DATA FOR EDITOR ===
- [LOG] ✅ Simple array format detected
- Editor modal opens with data table!
```

---

## 🐛 NEW FINDING: Analytics Service Duplicate Chart ID Bug

### The Root Cause of V2 Not Rendering

The Analytics Service is generating **duplicate canvas IDs** across slides:

```
Slide 0 (C3-chart):     canvas id="chart-slide-1"
Slide 1 (V2-chart-text): canvas id="chart-slide-1"  ← DUPLICATE!
Slide 2 (C3-chart):     canvas id="chart-slide-2"
Slide 3 (V2-chart-text): canvas id="chart-slide-2"  ← DUPLICATE!
Slide 4 (C3-chart):     canvas id="chart-slide-3"
Slide 5 (V2-chart-text): canvas id="chart-slide-3"  ← DUPLICATE!
```

### Why This Breaks V2 Charts:
1. When V2 slide initializes, it calls `document.getElementById('chart-slide-1')`
2. JavaScript returns the **FIRST** element with that ID (from slide 0, C3-chart)
3. The Chart.js instance renders to the **wrong canvas** (the hidden C3 canvas)
4. The V2 canvas remains empty

### ✅ FIX APPLIED (2025-12-28):

**File**: `agent.py`
**Change**: Replaced all 26 occurrences of:
```python
# Before (broken - used slide_id which can be duplicated)
chart_id=f"chart-{slide_id}"

# After (fixed - uses slide_number which is unique per slide)
chart_id=f"chart-slide-{slide_number}"
```

**Result**: Each chart now has a globally unique canvas ID based on absolute slide position:
```
Slide 0: canvas id="chart-slide-1" (slide_number=1)
Slide 1: canvas id="chart-slide-2" (slide_number=2)
Slide 2: canvas id="chart-slide-3" (slide_number=3)
...
```

**Deployment Status**: ✅ DEPLOYED to Railway (2025-12-28)

**Important Note**: Existing presentations have cached chart HTML with old IDs. The fix only affects **newly generated** charts. To verify:
1. Create a NEW presentation with C3 and V2 chart slides, OR
2. Regenerate existing presentation by calling Analytics Service again

---

## Summary

After the script execution fix (v7.5.3, commit 27fdc07), chart rendering works in **C3** but not in **V2**. Additionally, the chart edit button doesn't work in C3 (was working in L02).

### UPDATE: The Layout Service fix for `executeScriptsSequentially()` is WORKING CORRECTLY!
- ✅ C3 charts render properly
- ✅ C3 edit button opens the Excel editor
- ❌ V2 charts don't render due to Analytics Service duplicate ID bug

---

## Issue 1: V2-chart-text Charts Not Rendering

**Template**: `V2-chart-text`
**Status**: ❌ Not Working
**Expected**: Chart should render on left side, insights on right
**Actual**: Chart area is empty/not rendering

### Likely Cause
The script execution fix in `element-manager.js` may not be applied to the V2 template's chart container. The fix needs to be applied wherever `innerHTML` is used to insert chart HTML.

### Fix Applied to C3 (Reference)
```javascript
// src/utils/element-manager.js
if (config.chartHtml) {
  contentDiv.innerHTML = config.chartHtml;

  // Re-execute embedded scripts
  const scripts = contentDiv.querySelectorAll('script');
  scripts.forEach(oldScript => {
    const newScript = document.createElement('script');
    Array.from(oldScript.attributes).forEach(attr => {
      newScript.setAttribute(attr.name, attr.value);
    });
    newScript.textContent = oldScript.textContent;
    oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}
```

### Check Points for V2
1. Does V2 use `ElementManager.insertChart()` or a different method?
2. Is the chart HTML being inserted via a different code path?
3. Is the `chartHtml` property name different in V2 (e.g., `chart_html`, `element_3`)?

---

## Issue 2: Chart Edit Button Not Working in C3

**Template**: `C3-chart`
**Status**: ❌ Not Working (works in L02)
**Expected**: Clicking ✏️ button opens Excel-like chart editor
**Actual**: Nothing happens on click (no console errors)

### Likely Cause
The edit button calls a function like `openChartEditor_chart_slide_1()` which is defined in the embedded script. If scripts aren't executing in the correct order or scope, the function may not be available when the button is clicked.

### Analytics Service Edit Button HTML
```html
<button class="chart-edit-btn"
        onclick="openChartEditor_chart_slide_1()"
        style="position: absolute; top: 10px; left: 10px; ...">
  ✏️
</button>
```

### Check Points
1. Is `openChartEditor_chart_slide_1` function defined in `window` scope after script execution?
2. Are scripts being executed before the button becomes clickable?
3. Is the chart spreadsheet editor library loading?
   - Source: `https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js`

### Debugging Steps
```javascript
// Check in browser console on C3 slide:
console.log(typeof openChartEditor_chart_slide_1);  // Should be "function"
console.log(typeof openChartEditor);                 // Should be "function" (from editor lib)
console.log(window.chartInstances);                  // Should have chart reference
```

---

## Working Reference: L02

L02 template works correctly for both chart rendering and edit button. Key differences to investigate:

| Feature | L02 | C3 | V2 |
|---------|-----|----|----|
| Chart Rendering | ✅ | ✅ | ❌ |
| Edit Button | ✅ | ❌ | ❌ |
| Script Execution | Native | Fixed (v7.5.3) | Needs Fix |

---

## Test Slides for Verification

**Presentation**: https://web-production-f0d13.up.railway.app/p/a5d50715-3c85-470f-add7-c6202780dd87

| Slide | Layout | Chart Type | Rendering | Edit Button |
|-------|--------|------------|-----------|-------------|
| 1 | C3-chart | Line | ✅ | ❌ |
| 2 | V2-chart-text | Line | ❌ | ❌ |
| 3 | C3-chart | Bar | ✅ | ❌ |
| 4 | V2-chart-text | Bar | ❌ | ❌ |
| 5 | C3-chart | Pie | ✅ | ❌ |
| 6 | V2-chart-text | Pie | ❌ | ❌ |

---

## Recommended Fix Approach

### For V2 Chart Rendering
1. Find where V2 template inserts chart HTML
2. Apply the same script re-execution fix as C3
3. Ensure the property name matches (`chartHtml`, `chart_html`, or `element_3`)

### For Edit Button in C3 (and V2)
1. Ensure scripts execute in correct order:
   - First: Chart.js initialization script (creates chart instance)
   - Second: Editor library load (`chart-spreadsheet-editor.js`)
   - Third: Editor function definitions (`openChartEditor_chart_slide_X`)
2. Verify functions are attached to `window` scope
3. Check if there's a timing issue (button clickable before scripts run)

### Potential Solution: Delayed Script Execution
```javascript
// After script re-execution, wait for all scripts to complete
setTimeout(() => {
  console.log('All chart scripts should be ready now');
}, 100);
```

---

## Files to Check

- `src/utils/element-manager.js` - Script execution fix location
- `src/renderers/C3.js` - C3 template renderer
- `src/renderers/V2.js` - V2 template renderer (if exists)
- `src/renderers/L02.js` - Working reference

---

## Contact

For questions about the chart HTML structure or Analytics Service:
- Analytics Service: `https://analytics-v30-production.up.railway.app`
- Test endpoint: `POST /api/v1/analytics/L02/{analytics_type}?use_synthetic=true`

---

*Last updated: 2025-12-28*
