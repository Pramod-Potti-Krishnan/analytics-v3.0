# D3.js Chart Editor Support - Status & Implementation Plan

**Version**: 1.0
**Date**: 2025-11-28
**Status**: ⚠️ PARTIAL IMPLEMENTATION (Chart.js charts fully supported)

---

## Current Status

### ✅ Fully Supported (14 Chart Types)
**Chart.js Charts** - Excel-like editor with full features:
- `line`, `bar_vertical`, `bar_horizontal`, `pie`, `doughnut`
- `scatter`, `bubble`, `radar`, `polar_area`, `area`
- `bar_grouped`, `bar_stacked`, `area_stacked`, `waterfall`

**Features**:
- ✅ Edit button with modal popup
- ✅ Excel-like grid with chart-type-aware columns
- ✅ Real-time chart updates (chart.update())
- ✅ Keyboard navigation, copy/paste
- ✅ Add/delete rows, data validation
- ✅ Saves to backend API

### ⚠️ Partially Supported (4 Chart Types)
**D3.js Charts** - Editor library ready, integration pending:
- `d3_treemap`, `d3_sunburst`, `d3_choropleth_usa`, `d3_sankey`

**What Works**:
- ✅ Excel editor library has column configurations for D3 charts
- ✅ Data parsing (e.g., Sankey arrow notation `A → B`)
- ✅ Validation and data model specs

**What's Missing**:
- ❌ Edit button overlay on D3 charts
- ❌ D3 chart instance storage (no equivalent to window.chartInstances)
- ❌ Dynamic re-rendering after data changes
- ❌ Integration with D3 chart generation methods

---

## Technical Challenge

### Chart.js vs D3.js Architecture

| Aspect | Chart.js | D3.js |
|--------|----------|-------|
| **Rendering** | Canvas (imperative) | SVG (declarative) |
| **Instance** | Stored in `window.chartInstances[id]` | No global storage |
| **Update** | `chart.update()` method | Full re-render required |
| **Data Access** | `chart.data.labels`, `chart.data.datasets` | Data embedded in SVG/DOM |
| **Editor Integration** | Simple: update + chart.update() | Complex: extract data, re-render SVG |

### Why D3 Charts Are Different

1. **No chart instance**: D3 charts directly manipulate SVG DOM, no "chart object" to update
2. **Full re-render needed**: Can't just update data points, must rebuild entire SVG
3. **Data extraction**: Must parse SVG elements to get current data
4. **Initialization logic**: D3 init code is inline script, not easily callable

---

## Implementation Options

### Option 1: Read-Only Editor (Quick, 2-3 hours)
**What it does**:
- Add edit button to D3 charts
- Open Excel editor with current data
- Allow editing, but on save, show message: "Changes saved. Refresh page to see updated chart."
- Data persists to backend, chart updates on next render

**Pros**:
- ✅ Quick to implement
- ✅ Provides full Excel editor UX
- ✅ Data editing works perfectly
- ✅ Saves to backend

**Cons**:
- ❌ No real-time chart update
- ❌ Requires page refresh

**Implementation**:
```python
# In generate_d3_treemap_chart, before return:
if enable_editor:
    d3_html = f"""<div style="position: relative;">
      {d3_html}

      <button onclick="openD3Editor_{chart_id}()"
              style="position: absolute; top: 10px; left: 10px; ...">
        ✏️
      </button>

      <script src="/static/js/chart-spreadsheet-editor.js"></script>
      <script>
        function openD3Editor_{chart_id}() {{
          const data = {json.dumps(list(zip(labels, values)))};
          openChartEditor('{chart_id}', 'd3_treemap', data, {{
            onSave: async (newData) => {{
              // Save to backend
              await fetch(...);
              alert('Chart data saved. Refresh page to see changes.');
            }}
          }});
        }}
      </script>
    </div>"""
```

**Estimated Time**: 2-3 hours (add to all 4 D3 methods)

---

### Option 2: Full Dynamic Update (Complex, 8-12 hours)
**What it does**:
- Refactor D3 chart generation to create reusable render functions
- Store D3 data and render function globally
- Editor updates data and calls re-render
- Real-time chart updates

**Implementation Steps**:
1. Extract D3 rendering logic into callable functions
2. Store render function: `window.d3RenderFunctions[chartId] = renderFunc`
3. Store data: `window.d3ChartData[chartId] = data`
4. Editor updates data and calls `window.d3RenderFunctions[chartId](newData)`

**Pros**:
- ✅ Real-time updates (matches Chart.js UX)
- ✅ Professional, polished experience
- ✅ No page refresh needed

**Cons**:
- ❌ Significant refactoring required
- ❌ 8-12 hours implementation time
- ❌ Risk of breaking existing D3 charts

**Not Recommended** for this iteration - too risky and time-consuming.

---

### Option 3: Deferred Implementation (Fastest)
**What it does**:
- Document that D3 chart editing is "coming soon"
- Focus on perfecting Chart.js editor (14 chart types = 78% coverage)
- Add D3 support in future release (v4.1)

**Pros**:
- ✅ No additional work
- ✅ Focus on quality for Chart.js charts
- ✅ 14/18 types (78%) fully functional

**Cons**:
- ❌ Incomplete feature
- ❌ User expectation not fully met

---

## Recommended Approach: Option 1 (Read-Only D3 Editor)

**Why**:
1. **78% of charts already work** (14/18 Chart.js types)
2. **Quick to implement** (2-3 hours)
3. **Provides value** - users can edit D3 data, just need to refresh
4. **Low risk** - minimal changes to existing code
5. **Foundation for future** - enables Option 2 later

**Implementation Plan**:
1. Create `_wrap_d3_chart_with_editor()` method
2. Add to all 4 D3 chart generation methods
3. Editor saves data, shows refresh message
4. Document limitation in README

---

## Implementation Code (Option 1)

### New Method in ChartJSGenerator:

```python
def _wrap_d3_chart_with_editor(
    self,
    d3_html: str,
    chart_id: str,
    chart_type: str,  # 'd3_treemap', 'd3_sunburst', etc.
    data: List[Dict[str, Any]],  # Current chart data
    presentation_id: str,
    api_base_url: str
) -> str:
    """Add editor overlay to D3 charts (read-only with refresh)"""

    js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

    # Convert data to simple format for editor
    if isinstance(data, list):
        editor_data = data  # Already in correct format
    else:
        # Extract from dict format
        labels = data.get('labels', [])
        values = data.get('values', [])
        editor_data = [{"label": l, "value": v} for l, v in zip(labels, values)]

    wrapped_html = f"""<div style="position: relative;">
  {d3_html}

  <!-- Edit Button -->
  <button class="chart-edit-btn"
          onclick="openD3Editor_{js_safe_id}()"
          style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;"
          onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=\\'margin-left: 6px; font-size: 13px;\\'>edit</span>'; this.style.background='rgba(0,0,0,0.8)'"
          onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script src="/static/js/chart-spreadsheet-editor.js"></script>
  <script>
    function openD3Editor_{js_safe_id}() {{
      const data = {json.dumps(editor_data)};

      openChartEditor(
        '{chart_id}',
        '{chart_type}',
        data,
        {{
          onSave: async (newData, chartId) => {{
            console.log('Saving D3 chart data:', newData);

            // Save to backend API
            try {{
              const response = await fetch('{api_base_url}/api/charts/update-data', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                  chart_id: chartId,
                  presentation_id: '{presentation_id}',
                  data: newData,
                  chart_type: '{chart_type}',
                  timestamp: Date.now()
                }})
              }});

              if (!response.ok) {{
                throw new Error('Save failed');
              }}

              // Show refresh message (D3 charts need full re-render)
              alert('✅ Chart data saved successfully!\\n\\n⚠️ D3 charts require a page refresh to display updates.\\n\\nPlease refresh the page to see your changes.');

            }} catch (error) {{
              console.error('Error saving D3 chart data:', error);
              alert('❌ Failed to save chart data. Please try again.');
              throw error;
            }}
          }}
        }}
      );
    }}
  </script>
</div>"""

    return wrapped_html
```

### Update D3 Chart Methods:

```python
def generate_d3_treemap_chart(self, ...):
    # ... existing code ...

    # Before return
    if enable_editor and presentation_id:
        d3_html = self._wrap_d3_chart_with_editor(
            d3_html=d3_html,
            chart_id=chart_id,
            chart_type='d3_treemap',
            data={'labels': labels, 'values': values},
            presentation_id=presentation_id,
            api_base_url=api_base_url
        )

    return d3_html
```

---

## Testing D3 Editor

### Test Cases:
1. **Open Editor**: Click edit button → Excel editor opens
2. **View Data**: Verify correct labels and values displayed
3. **Edit Data**: Change values, add rows, delete rows
4. **Save**: Click save → success message shown
5. **Refresh**: Refresh page → see updated chart
6. **Column Config**: Verify correct columns for each D3 chart type:
   - Treemap: Label, Value
   - Sunburst: Label, Value
   - Choropleth: State, Value
   - Sankey: Source, Target, Value

---

## Future Enhancement (v4.1): Real-Time D3 Updates

When time permits, implement Option 2 for seamless UX:

1. **Refactor D3 Rendering**:
   ```javascript
   window.d3Renderers = {};

   function createD3TreemapRenderer(containerId, data) {
     return function(newData) {
       d3.select(`#${containerId}`).selectAll("*").remove();
       // Re-render treemap with newData
     };
   }

   window.d3Renderers['chart-123'] = createD3TreemapRenderer('chart-123', initialData);
   ```

2. **Editor Calls Renderer**:
   ```javascript
   onSave: (newData) => {
     window.d3Renderers[chartId](newData);
     // Also save to backend
   }
   ```

3. **Benefits**:
   - Real-time updates
   - No page refresh
   - Matches Chart.js UX

**Estimated Effort**: 8-12 hours (v4.1 release)

---

## Documentation Updates

### README.md:
```markdown
## Excel-Like Chart Editor

Edit chart data interactively with a professional Excel-like interface.

### Supported Chart Types:

**✅ Full Support** (Real-time updates):
- All Chart.js charts (14 types): Line, Bar, Pie, Scatter, Bubble, etc.
- Keyboard navigation, copy/paste, add/delete rows
- Changes update immediately

**⚠️ Basic Support** (Requires refresh):
- D3.js charts (4 types): Treemap, Sunburst, Choropleth, Sankey
- Full Excel editor with data editing
- Changes saved to backend
- **Page refresh required** to see chart updates
- Real-time updates coming in v4.1
```

---

## Decision: Implementation Recommendation

**Implement Option 1** (Read-Only D3 Editor with refresh):

**Rationale**:
1. 78% of charts (14/18) have full real-time editing
2. Remaining 22% (4/18) have functional editing with minor inconvenience
3. Quick implementation (2-3 hours)
4. Low risk, high value
5. Sets foundation for v4.1 real-time updates

**Estimated Timeline**:
- Option 1 Implementation: 2-3 hours
- Testing: 1 hour
- Documentation: 30 minutes
- **Total**: 3.5-4.5 hours

---

## Status Summary

| Chart Type | Editor Status | Update Method | ETA |
|-----------|---------------|---------------|-----|
| Chart.js (14) | ✅ Complete | Real-time | Done |
| D3.js (4) | ⚠️ Basic | Refresh | 3-4 hours |
| **Total** | **78% Complete** | - | **3-4 hours** |

---

**Next Steps**:
1. Implement `_wrap_d3_chart_with_editor()` method
2. Add to all 4 D3 chart generation methods
3. Test editing workflow for each D3 chart type
4. Update documentation (README.md)
5. Commit to feature branch

**After this**: Move to Stage 3.5 (comprehensive tests)
