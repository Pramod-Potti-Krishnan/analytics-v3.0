# Bug Investigation Report: Column Headers Stacking Vertically

## Issue Summary
Column names in the chart editor table are stacking vertically in column A instead of spreading horizontally across the header row.

## Visual Evidence
**Expected Behavior:**
```
Row 1 (letters):  [blank] | A | B | C | D | Actions
Row 2 (names):    #       | Label ✓ | North America ✓ | EMEA ✓ | APAC ✓ | Actions
Row 3 (data):     1       | Q1 | 124 | 98 | 75 | 🗑️
```

**Actual Behavior:**
```
Row 1 (letters):  [blank] | A | B | C | D |
Row 2 (names):    #       | Label ✓       | | | Actions
                            North America ✓ | | |
                            EMEA ✓         | | |
                            APAC ✓         | | |
Row 3 (data):     1       | Q1 | 124 | 98 | 75 | 🗑️
```

## Root Cause Analysis

### Location
**File:** `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice_v3/static/js/chart-spreadsheet-editor.js`
**Lines:** 889-896

### The Bug
```css
.spreadsheet-col-header {
    position: relative;
    display: flex;              /* ← BUG: This breaks table cell layout */
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 12px 8px;
}
```

### Technical Explanation
1. **HTML Structure is Correct:** The JavaScript generates separate `<th>` elements for each column (verified via DOM inspection)
2. **CSS Breaks Table Layout:** Setting `display: flex` on `<th>` elements overrides their natural `display: table-cell` behavior
3. **Result:** The `<th>` elements lose table column positioning and stack vertically at the same left coordinate (153px)

### Evidence from Browser DevTools
```javascript
// DOM positions of header cells:
Header 0 ("#"):            left = 85.5px,  display: table-cell ✅
Header 1 ("Label"):        left = 153px,   display: flex ❌
Header 2 ("North America"): left = 153px,   display: flex ❌ (STACKED!)
Header 3 ("EMEA"):         left = 153px,   display: flex ❌ (STACKED!)
Header 4 ("APAC"):         left = 153px,   display: flex ❌ (STACKED!)
Header 5 ("Actions"):      left = 408.5px, display: table-cell ✅
```

All column name headers (1-4) have the **same left position** and stack vertically instead of spreading horizontally.

## Proposed Fix

### Solution
Change the CSS to keep `<th>` elements as `display: table-cell` and create flex layout **inside** the cell using the existing `.col-header-content` wrapper.

### Code Changes Required

**File:** `analytics_microservice_v3/static/js/chart-spreadsheet-editor.js`

**Before (Lines 889-903):**
```css
.spreadsheet-col-header {
    position: relative;
    display: flex;              /* ← REMOVE THIS */
    align-items: center;        /* ← MOVE TO INNER WRAPPER */
    justify-content: space-between;  /* ← MOVE TO INNER WRAPPER */
    gap: 8px;                   /* ← MOVE TO INNER WRAPPER */
    padding: 12px 8px;
}

.col-header-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 4px;
}
```

**After:**
```css
.spreadsheet-col-header {
    position: relative;
    /* display: flex; ← REMOVED - let it be table-cell */
    padding: 12px 8px;
    vertical-align: middle;  /* ← ADD for proper alignment */
}

/* Add wrapper div styling to achieve flex layout inside the cell */
.spreadsheet-col-header > div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}

.col-header-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 4px;
}
```

**Alternative (requires HTML change):**
Add a wrapper `<div>` in the HTML generation (lines 516-521):
```javascript
html += `<th class="spreadsheet-col-header ${activeClass}" data-column="${col}">
    <div class="col-header-wrapper">
        <span class="col-header-content">
            ${col} ${activeIcon}
        </span>
        ${deleteBtn}
    </div>
</th>`;
```

## Impact Assessment
- **Severity:** P0 - Critical (entire table editor is unusable)
- **Affected Users:** All users using chart data editor
- **Workaround:** None (feature is completely broken)
- **Fix Complexity:** Low (single CSS change or minimal HTML restructure)

## Testing Requirements
After fix:
1. Verify column headers spread horizontally across A, B, C, D columns
2. Verify delete buttons still appear on hover for series columns
3. Verify column header styling (centering, icons) is preserved
4. Test with 2-column, 3-column, 4-column, and 5-column charts
5. Verify no regression in data row rendering

## Files to Modify
1. `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice_v3/static/js/chart-spreadsheet-editor.js`
   - CSS section: Lines 889-903
   - HTML generation (if wrapper approach): Lines 516-521

## Verification Steps
1. Open chart editor modal
2. Confirm second header row shows: `# | Label ✓ | North America ✓ | EMEA ✓ | APAC ✓ | Actions`
3. Confirm each column name is in its own column (A, B, C, D)
4. Confirm delete buttons (🗑️) appear on hover for series columns
5. Confirm visual styling matches design intent
