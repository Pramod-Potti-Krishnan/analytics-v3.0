# Integration Test Verification Plan - Post Layout Service CDN Fix

**Date**: November 27, 2025
**Version**: Analytics v3.4.4 + Layout Service CDN Update
**Status**: 📋 READY FOR VERIFICATION
**Teams**: Analytics ✅ (fixes deployed) + Layout Service ✅ (CDN updated)

---

## Executive Summary

Both teams have completed their fixes:
- **Analytics Service**: v3.4.4 deployed with data transformation (commit 43960ff)
- **Layout Service**: CDN scripts updated in presentation-viewer.html

**This document provides the verification checklist** to confirm all 5 previously broken charts now work correctly.

---

## Quick Verification Checklist

### For Director Team (Quick Test)

Visit these production URLs and verify:

#### 1. Mixed Chart
**URL**: https://web-production-f0d13.up.railway.app/p/34796d89-c613-47d4-85f2-a3dea38db976

**Expected**:
- [ ] Chart renders (not blank)
- [ ] Shows BOTH line and bar elements
- [ ] Revenue displayed as line
- [ ] Costs displayed as bars
- [ ] No console errors about CDN plugins

**If fails**: Take screenshot of console errors (F12 → Console tab)

---

#### 2. D3 Sunburst Chart
**URL**: https://web-production-f0d13.up.railway.app/p/c3211cd0-db92-4f6e-84dd-34cbe7c9a4a4

**Expected**:
- [ ] Chart renders as circular sunburst diagram (NOT bar chart)
- [ ] Shows hierarchical segments in radial layout
- [ ] Interactive hover works
- [ ] No console errors about D3.js or CDN plugins

**If fails**: Take screenshot showing what chart type actually renders

---

#### 3. Bar Grouped Chart
**URL**: (Request from Director team - needs test URL)

**Expected**:
- [ ] Chart renders (not blank)
- [ ] Multiple series displayed side-by-side
- [ ] All data series visible (North America, EMEA, APAC)
- [ ] Labels show correctly (Q1, Q2, Q3, Q4)
- [ ] No console errors

---

#### 4. Bar Stacked Chart
**URL**: (Request from Director team - needs test URL)

**Expected**:
- [ ] Chart renders (not blank)
- [ ] Bars are stacked (not side-by-side)
- [ ] All departments visible in stack
- [ ] Colors differentiate segments
- [ ] No console errors

---

#### 5. Area Stacked Chart
**URL**: (Request from Director team - needs test URL)

**Expected**:
- [ ] Chart renders (not blank)
- [ ] Areas are stacked on top of each other
- [ ] Fill colors visible
- [ ] Multiple product series shown
- [ ] No console errors

---

## Detailed Verification Steps

### Step 1: Browser Console Check (5 minutes)

**For EACH chart URL**:

1. Open URL in browser
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Refresh page
5. Check for errors:

**✅ PASS if you see**:
```
✅ Chart.js 4.4.0 loaded
✅ D3.js v7 loaded (for sunburst)
✅ ChartDataLabels plugin registered
✅ All required plugins loaded
```

**❌ FAIL if you see**:
```
❌ Failed to load resource: chartjs-chart-box-and-violin-plot.min.js (404)
❌ Refused to execute ... Content-Type is not a script MIME type
❌ D3 is not defined
❌ Chart is not defined
```

**Action if FAIL**: Screenshot the errors and share with both teams

---

### Step 2: Visual Chart Validation (10 minutes)

**For EACH chart**:

1. **Verify Chart Type**:
   - mixed → Should show line + bars together
   - d3_sunburst → Should show circular radial diagram
   - bar_grouped → Should show bars side-by-side
   - bar_stacked → Should show stacked bars
   - area_stacked → Should show filled areas

2. **Verify Data Rendering**:
   - All data series visible
   - Labels display correctly
   - Legend shows all series names
   - Chart is NOT blank
   - Chart is NOT showing wrong type

3. **Verify Interactivity**:
   - Hover over chart elements
   - Tooltip appears with data values
   - No JavaScript errors on interaction

**Action if FAIL**: Take screenshot of what renders vs. what was expected

---

### Step 3: Editor Functionality (5 minutes per chart)

**For EACH chart**:

1. Click "Edit Chart" button (if available)
2. Verify:
   - [ ] Editor opens without errors
   - [ ] Data grid shows correctly
   - [ ] Can add/edit data points
   - [ ] Changes reflect in chart preview
   - [ ] Can save changes

**Action if FAIL**: Document which step failed

---

### Step 4: Network Tab Validation (5 minutes)

**Purpose**: Verify correct CDN scripts are loading

1. Open any chart URL
2. F12 → Network tab
3. Refresh page
4. Filter by "JS"
5. Look for these successful loads (status 200):

**✅ Required for ALL charts**:
- chart.umd.min.js (Chart.js 4.4.0)
- chartjs-plugin-datalabels (v2.2.0)

**✅ Required for d3_sunburst ONLY**:
- d3@7 (main D3.js library)

**❌ Should NOT see**:
- chartjs-chart-box-and-violin-plot.min.js (should not load for mixed/sunburst)

**Action if FAIL**: Screenshot Network tab showing failed/wrong scripts

---

## Test Data Formats

### Mixed Chart Test Data
```json
[
  {"label": "Q1", "Revenue": 120, "Costs": 80},
  {"label": "Q2", "Revenue": 150, "Costs": 90},
  {"label": "Q3", "Revenue": 180, "Costs": 100},
  {"label": "Q4", "Revenue": 200, "Costs": 110}
]
```

**Expected Transform**:
```json
{
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [
    {"label": "Revenue", "data": [120, 150, 180, 200], "type": "line"},
    {"label": "Costs", "data": [80, 90, 100, 110], "type": "bar"}
  ]
}
```

---

### D3 Sunburst Test Data
```json
[
  {"label": "Engineering", "value": 800000},
  {"label": "Sales", "value": 600000},
  {"label": "Marketing", "value": 400000},
  {"label": "Operations", "value": 350000},
  {"label": "Finance", "value": 200000},
  {"label": "HR", "value": 150000}
]
```

**Expected Transform**:
```json
{
  "labels": ["Engineering", "Sales", "Marketing", "Operations", "Finance", "HR"],
  "values": [800000, 600000, 400000, 350000, 200000, 150000]
}
```

---

### Bar Grouped Test Data
```json
[
  {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
  {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88},
  {"label": "Q3", "North America": 165, "EMEA": 128, "APAC": 105},
  {"label": "Q4", "North America": 180, "EMEA": 145, "APAC": 125}
]
```

**Expected Transform**:
```json
{
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [
    {"label": "North America", "data": [124, 145, 165, 180]},
    {"label": "EMEA", "data": [98, 112, 128, 145]},
    {"label": "APAC", "data": [75, 88, 105, 125]}
  ]
}
```

---

## Success Criteria

### ✅ All Charts PASS if:

1. **Visual Rendering**: All 5 charts display correctly (not blank, correct type)
2. **Console Errors**: Zero CDN-related errors in browser console
3. **Data Series**: All data series visible in each chart
4. **Interactivity**: Hover/tooltip functionality works
5. **Editor**: Chart editor loads and functions correctly
6. **Performance**: Charts load within 3 seconds

### Overall Success Target:
- **16 of 18 chart types working (89%)**
- Only d3_choropleth_usa and d3_sankey remain unimplemented

---

## Failure Scenarios & Diagnosis

### Scenario 1: Chart Still Renders Blank

**Possible Causes**:
1. Analytics transformation not applied correctly
2. Layout Service not rendering Analytics HTML
3. Chart.js initialization error

**Diagnosis Steps**:
1. Check browser console for JavaScript errors
2. Inspect HTML source - look for `<canvas>` element
3. Check if Chart.js script loaded successfully
4. Verify data is present in HTML (view source)

**Owner**: If no `<canvas>` → Layout Service; if `<canvas>` but no chart → Analytics Service

---

### Scenario 2: Console Shows CDN Errors

**Possible Causes**:
1. Layout Service didn't apply CDN fix correctly
2. CDN URL is incorrect or unreachable
3. Wrong plugin version specified

**Diagnosis Steps**:
1. Check Network tab for failed script loads
2. Verify presentation-viewer.html has correct CDN URLs
3. Test CDN URL directly in browser

**Owner**: Layout Service (CDN script configuration)

---

### Scenario 3: Wrong Chart Type Renders

**Possible Causes**:
1. Analytics sending wrong chart type metadata
2. Director sending wrong chart_type parameter
3. Layout Service using wrong renderer

**Diagnosis Steps**:
1. Check HTML source for `chart_type` metadata
2. Verify Director request includes correct chart_type
3. Check Analytics logs for chart generation requests

**Owner**: Depends on where wrong type originates (Director → Analytics → Layout)

---

### Scenario 4: d3_sunburst Still Shows Bar Chart

**Possible Causes**:
1. D3.js not loaded (Layout Service CDN issue)
2. Analytics fallback to bar chart due to D3 unavailable
3. Data format still incorrect

**Diagnosis Steps**:
1. Check console: `typeof d3` should be "object", not "undefined"
2. Check Network tab: d3@7 script should load (status 200)
3. View HTML source: should contain D3 sunburst rendering code

**Owner**: Layout Service if D3.js not loaded; Analytics if D3 loaded but chart wrong

---

## Rollback Plan (If Tests Fail)

### If Analytics v3.4.4 Needs Rollback:
```bash
cd /agents/analytics_microservice_v3
git revert 43960ff
git push origin main
```
**Impact**: Charts revert to v3.4.3 state (partially broken)

### If Layout Service CDN Changes Need Rollback:
**File**: `/agents/layout_builder_main/v7.5-main/viewer/presentation-viewer.html`
**Action**: Remove D3.js CDN line, restore previous version
**Impact**: d3_sunburst and d3_treemap will break again

---

## Post-Verification Actions

### If ALL Tests PASS ✅:

1. **Update Director Configuration**:
   - Remove 4 disabled chart entries from `config/analytics_variants.json`
   - Remove 4 disabled entries from `src/utils/service_router_v1_2.py`
   - Re-enable: bar_grouped, bar_stacked, area_stacked, mixed

2. **Update Documentation**:
   - Mark charts as "working" in Director docs
   - Update success rate: 16 of 18 (89%)
   - Document remaining 2 charts as "not implemented"

3. **Create Success Report**:
   - Document final test results
   - Share with both teams
   - Close all P0 tickets

### If ANY Tests FAIL ❌:

1. **Isolate Root Cause**:
   - Use standalone HTML files to test Analytics Service alone
   - Use Layout Service test environment to verify CDN scripts
   - Identify which team needs to fix

2. **Create Bug Report**:
   - Document exact failure scenario
   - Include screenshots and console logs
   - Assign to responsible team

3. **Coordinate Fix**:
   - Schedule follow-up between teams
   - Implement additional fixes
   - Re-run verification

---

## Testing Timeline

**Recommended Schedule**:

| Time | Activity | Owner | Duration |
|------|----------|-------|----------|
| T+0 | Console check for all 5 charts | Director Team | 5 min |
| T+5 | Visual validation of all charts | Director Team | 10 min |
| T+15 | Editor functionality testing | Director Team | 25 min |
| T+40 | Network tab CDN verification | Director Team | 5 min |
| T+45 | Document results | Director Team | 10 min |
| T+55 | Share results with Analytics/Layout | Director Team | 5 min |
| **T+60** | **TOTAL VERIFICATION TIME** | | **1 hour** |

---

## Test Result Template

**Copy this template and fill in results**:

```markdown
# Integration Test Results - Post CDN Fix

**Date**: [DATE]
**Tester**: [NAME]
**Environment**: Production (Railway)

## Console Check Results

### Mixed Chart
URL: https://web-production-f0d13.up.railway.app/p/34796d89-c613-47d4-85f2-a3dea38db976
- [ ] No CDN errors
- [ ] Chart.js loaded
- [ ] Chart renders correctly
**Status**: ✅ PASS / ❌ FAIL
**Notes**:

### D3 Sunburst Chart
URL: https://web-production-f0d13.up.railway.app/p/c3211cd0-db92-4f6e-84dd-34cbe7c9a4a4
- [ ] No CDN errors
- [ ] D3.js loaded
- [ ] Sunburst diagram renders (NOT bar chart)
**Status**: ✅ PASS / ❌ FAIL
**Notes**:

### Bar Grouped Chart
URL: [INSERT URL]
- [ ] No CDN errors
- [ ] Chart.js loaded
- [ ] Grouped bars render correctly
**Status**: ✅ PASS / ❌ FAIL
**Notes**:

### Bar Stacked Chart
URL: [INSERT URL]
- [ ] No CDN errors
- [ ] Chart.js loaded
- [ ] Stacked bars render correctly
**Status**: ✅ PASS / ❌ FAIL
**Notes**:

### Area Stacked Chart
URL: [INSERT URL]
- [ ] No CDN errors
- [ ] Chart.js loaded
- [ ] Stacked area chart renders correctly
**Status**: ✅ PASS / ❌ FAIL
**Notes**:

## Overall Results

**Total Passed**: ___ / 5
**Total Failed**: ___ / 5
**Success Rate**: ____%

## Recommended Actions

[✅ If all passed]: Re-enable charts in Director configuration
[❌ If any failed]: [Document specific failures and assign to teams]
```

---

## Contact Information

### For Questions During Testing:

**Analytics Service Team**:
- Repository: https://github.com/Pramod-Potti-Krishnan/analytics-v3.0.git
- Version: v3.4.4 (commit 43960ff)
- Documentation: P0_FIXES_V3.4.4_COMPLETE.md

**Layout Service Team**:
- Location: `/agents/layout_builder_main/v7.5-main`
- File Modified: `viewer/presentation-viewer.html` (lines 111-121)
- Documentation: LAYOUT_SERVICE_CDN_FIX_REQUIRED.md

**Director Service Team**:
- Version: v3.4
- Status: Awaiting integration test results

---

## Appendix: Known Working Charts (For Reference)

These 11 charts are confirmed working and should NOT be tested:

1. ✅ bar (simple bar chart)
2. ✅ line (simple line chart)
3. ✅ pie
4. ✅ doughnut
5. ✅ scatter
6. ✅ bubble
7. ✅ radar
8. ✅ polar_area
9. ✅ funnel
10. ✅ waterfall
11. ✅ d3_treemap

---

## Appendix: Known Not Implemented (For Reference)

These 2 charts are NOT IMPLEMENTED and should NOT be tested:

1. ❌ d3_choropleth_usa (P1 - not implemented)
2. ❌ d3_sankey (P1 - plugin missing)

---

**Document Version**: 1.0
**Last Updated**: November 27, 2025
**Status**: 📋 Ready for Director Team Testing
**Expected Outcome**: 16 of 18 charts working (89% success rate)
