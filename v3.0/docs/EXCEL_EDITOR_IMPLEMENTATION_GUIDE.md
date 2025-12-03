# Excel-Like Editor Implementation Guide

**Version**: 1.0
**Date**: 2025-11-28
**Status**: ⚠️ READY FOR IMPLEMENTATION
**Feature Branch**: `feature/excel-like-chart-editor`

---

## Implementation Summary

This guide describes how to complete the Excel-like editor integration into the Analytics Microservice.

### ✅ Completed Work (Stages 1-3.2)

1. **Stage 1**: Created `docs/CHART_DATA_MODELS.md`
   - Comprehensive data model documentation for all 18 chart types
   - Table structure specifications for Excel-like editor
   - Column highlighting rules and validation requirements

2. **Stage 2**: Created `docs/SYNTHETIC_DATA_VALIDATION_REPORT.md`
   - Validated synthetic data generator alignment (100% aligned!)
   - No generator changes needed
   - Minor Sankey parsing needed in editor only

3. **Stage 3.1-3.2**: Created `static/js/chart-spreadsheet-editor.js`
   - Comprehensive Excel-like editor library (1,200+ lines)
   - Features implemented:
     - ✅ Dynamic column configuration per chart type
     - ✅ Cell editing with keyboard navigation (arrows, tab, enter)
     - ✅ Add/delete rows and columns
     - ✅ Copy/paste support from Excel
     - ✅ Active data column highlighting (yellow/green)
     - ✅ Data validation (min/max rows, type checking)
     - ✅ Real-time chart updates
     - ✅ Sankey arrow notation parsing
     - ✅ Multi-series dynamic columns
     - ✅ Toast notifications
     - ✅ Chart-type-aware schemas

---

## ⚠️ Remaining Work (Stages 3.3-3.5)

### Stage 3.3: Replace Current Editor UI in chartjs_generator.py

**File**: `chartjs_generator.py`
**Method**: `_wrap_inline_script_with_editor()` (lines 2465-2843)

**Current Implementation**:
- 378 lines of inline HTML + JavaScript
- Custom table rendering for each chart type
- Separate handling for scatter/bubble vs other charts

**Required Replacement**:
Replace the entire method with a streamlined version that uses the Excel editor library:

```python
def _wrap_inline_script_with_editor(
    self,
    chart_html: str,
    chart_id: str,
    presentation_id: str,
    api_base_url: str,
    inline_script: str,
    chart_type: str = "bar"
) -> str:
    """
    Add Excel-like interactive editor to inline-script chart (Layout Builder mode).

    v4.0: Replaced custom HTML editor with professional Excel-like spreadsheet editor.
    Uses chart-spreadsheet-editor.js library for consistent, feature-rich editing.

    Args:
        chart_html: Chart HTML with inline script
        chart_id: Unique chart identifier
        presentation_id: Presentation UUID
        api_base_url: Base URL for chart API
        inline_script: The Chart.js initialization script
        chart_type: Type of chart (bar, scatter, bubble, d3_*, etc.)

    Returns:
        Chart HTML with Excel-like editor controls
    """
    js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

    # v4.0: Streamlined HTML with Excel editor library
    editor_html = f"""<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="{chart_id}"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn"
          onclick="openChartEditor_{js_safe_id}()"
          style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;"
          onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=\\'margin-left: 6px; font-size: 13px;\\'>edit</span>'; this.style.background='rgba(0,0,0,0.8)'"
          onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    {inline_script}
  </script>
</div>

<!-- Load Excel-like Spreadsheet Editor Library -->
<script src="/static/js/chart-spreadsheet-editor.js"></script>

<script>
(function() {{
    window.openChartEditor_{js_safe_id} = function() {{
        console.log('=== Excel Editor: Opening for chart {chart_id} ===');

        // Get chart instance
        const chart = window.chartInstances?.['{chart_id}'];
        if (!chart) {{
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }}

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', '{chart_type}');

        // Extract current chart data
        const chartData = extractChartData_{js_safe_id}(chart);

        // Open Excel-like editor
        openChartEditor(
            '{chart_id}',
            '{chart_type}',
            chartData,
            {{
                apiEndpoint: '{api_base_url}/api/charts/update-data',
                onSave: async (newData, chartId) => {{
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_{js_safe_id}(chart, newData, '{chart_type}');

                    // Save to API
                    try {{
                        const response = await fetch('{api_base_url}/api/charts/update-data', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                chart_id: chartId,
                                presentation_id: '{presentation_id}',
                                data: newData,
                                timestamp: Date.now()
                            }})
                        }});

                        if (!response.ok) {{
                            throw new Error('API request failed');
                        }}

                        console.log('✅ Chart data saved successfully');
                    }} catch (error) {{
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }}
                }}
            }}
        );
    }};

    // Extract data from chart instance based on chart type
    function extractChartData_{js_safe_id}(chart) {{
        const chartType = chart.config.type;

        if (chartType === 'scatter') {{
            // Scatter: array of {{x, y}}
            return chart.data.datasets[0]?.data || [];
        }} else if (chartType === 'bubble') {{
            // Bubble: array of {{label, x, y, r}}
            return chart.data.datasets[0]?.data || [];
        }} else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {{
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {{
                // Multi-series format
                return {{
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({{
                        label: ds.label,
                        data: ds.data
                    }}))
                }};
            }} else {{
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({{ label, value: values[i] }}));
            }}
        }} else {{
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({{ label, value: values[i] }}));
        }}
    }}

    // Update chart instance with new data
    function updateChartData_{js_safe_id}(chart, newData, chartType) {{
        if (chartType === 'scatter' || chartType === 'bubble') {{
            // Object-based data
            chart.data.datasets[0].data = newData;
        }} else if (newData.labels && newData.datasets) {{
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        }} else if (Array.isArray(newData)) {{
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }}

        chart.update();
    }}
}})();
</script>
"""

    return editor_html
```

**Benefits of New Implementation**:
- ✅ Reduces method from 378 lines → ~95 lines (75% reduction!)
- ✅ Removes all inline HTML table generation
- ✅ Delegates to professional Excel-like library
- ✅ Consistent UX across all chart types
- ✅ Much easier to maintain and extend

**Manual Implementation Steps**:

1. **Backup the file**:
   ```bash
   cp chartjs_generator.py chartjs_generator.py.backup
   ```

2. **Open `chartjs_generator.py` in editor**

3. **Find line 2465**: `def _wrap_inline_script_with_editor(`

4. **Delete lines 2465-2843** (entire method body)

5. **Paste the new implementation** from above

6. **Save the file**

7. **Test**: Run tests to verify Chart.js charts still work

---

### Stage 3.4: Add D3.js Chart Editor Support

**Current Status**: D3 charts (d3_treemap, d3_sunburst, d3_choropleth_usa, d3_sankey) have NO editor support.

**What's Needed**:

1. **Find where D3 charts are rendered** (search for `d3_treemap`, `d3_sunburst`, etc.)

2. **Add editor wrapper** to D3 chart HTML output (similar to Chart.js)

3. **D3 charts already supported** in Excel editor library:
   - `d3_treemap`: Label, Value columns (hierarchical parent.child notation)
   - `d3_sunburst`: Label, Value columns (hierarchical parent.child notation)
   - `d3_choropleth_usa`: State, Value columns
   - `d3_sankey`: Source, Target, Value columns (parses arrow notation)

4. **Implementation Pattern**:
   ```python
   # In d3_generator.py or wherever D3 charts are built
   if enable_editor:
       d3_html = self._wrap_inline_script_with_editor(
           chart_html=d3_svg_html,
           chart_id=chart_id,
           presentation_id=presentation_id,
           api_base_url=settings.api_base_url,
           inline_script=d3_init_script,
           chart_type='d3_treemap'  # or d3_sunburst, d3_sankey, etc.
       )
   ```

---

### Stage 3.5: Create Comprehensive Tests

**Test File**: `tests/test_excel_editor.py`

**Required Test Coverage**:

```python
import pytest
from static.js.chart_spreadsheet_editor import ChartSpreadsheetEditor  # Will need Python-JS bridge

class TestExcelEditor:
    """Test Excel-like editor for all chart types"""

    # Simple format tests (13 chart types)
    @pytest.mark.parametrize("chart_type", [
        'line', 'bar_vertical', 'bar_horizontal', 'pie', 'doughnut',
        'radar', 'polar_area', 'area', 'waterfall',
        'd3_treemap', 'd3_sunburst', 'd3_choropleth_usa'
    ])
    def test_simple_format_charts(self, chart_type):
        """Test editor with simple label-value charts"""
        data = [
            {"label": "Q1", "value": 100},
            {"label": "Q2", "value": 120}
        ]
        # Test: editor opens, displays correct columns, saves data
        pass

    def test_scatter_chart(self):
        """Test scatter chart with X, Y columns"""
        data = [{"x": 10, "y": 20}, {"x": 30, "y": 40}]
        # Test: editor displays X, Y columns (no Label)
        pass

    def test_bubble_chart(self):
        """Test bubble chart with Label, X, Y, Radius columns"""
        data = [
            {"label": "A", "x": 10, "y": 20, "r": 15},
            {"label": "B", "x": 30, "y": 40, "r": 20}
        ]
        # Test: editor displays all 4 columns
        pass

    @pytest.mark.parametrize("chart_type", ['bar_grouped', 'bar_stacked', 'area_stacked'])
    def test_multi_series_charts(self, chart_type):
        """Test multi-series charts with dynamic columns"""
        data = {
            "labels": ["Q1", "Q2"],
            "datasets": [
                {"label": "2023", "data": [100, 120]},
                {"label": "2024", "data": [110, 130]}
            ]
        }
        # Test: editor displays Label + dynamic series columns
        # Test: can add new series column
        pass

    def test_sankey_chart(self):
        """Test Sankey with Source, Target, Value columns"""
        data = [
            {"label": "A → B", "value": 100},
            {"label": "B → C", "value": 50}
        ]
        # Test: editor parses arrow notation into Source, Target columns
        # Test: on save, reconstitutes arrow notation
        pass

    def test_cell_highlighting(self):
        """Test active data column highlighting"""
        # Test: active columns have yellow/green background
        # Test: inactive columns have white/gray background
        pass

    def test_keyboard_navigation(self):
        """Test arrow keys, tab, enter navigation"""
        # Test: Arrow keys navigate cells
        # Test: Tab moves to next cell
        # Test: Enter moves to next row
        pass

    def test_copy_paste(self):
        """Test copy/paste from Excel"""
        # Simulate Excel paste (tab/newline separated)
        # Test: data correctly parsed and inserted
        pass

    def test_add_delete_rows(self):
        """Test row operations"""
        # Test: can add row with + button
        # Test: can delete row with trash icon
        # Test: minimum 2 rows enforced
        pass

    def test_data_validation(self):
        """Test data validation rules"""
        # Test: empty cells rejected
        # Test: NaN/Infinity rejected
        # Test: incorrect types rejected
        pass

    def test_save_and_update_chart(self):
        """Test save updates chart instance"""
        # Test: save button triggers API call
        # Test: chart.update() called
        # Test: visual chart reflects new data
        pass
```

**Running Tests**:
```bash
pytest tests/test_excel_editor.py -v
```

---

## 📋 Completion Checklist

Before merging to main:

- [ ] **Stage 3.3**: `chartjs_generator.py` updated with Excel editor
- [ ] **Stage 3.4**: D3 charts have editor support
- [ ] **Stage 3.5**: All tests passing (>90% coverage)
- [ ] **Manual Testing**: Test all 18 chart types manually
  - [ ] Line, Bar, Pie, Doughnut charts
  - [ ] Scatter, Bubble charts
  - [ ] Radar, Polar Area charts
  - [ ] Bar Grouped, Bar Stacked, Area Stacked charts
  - [ ] Waterfall chart
  - [ ] D3 Treemap, D3 Sunburst charts
  - [ ] D3 Choropleth USA chart
  - [ ] D3 Sankey chart
- [ ] **Excel Features Tested**:
  - [ ] Copy/paste from Excel works
  - [ ] Keyboard navigation (arrows, tab, enter) works
  - [ ] Add/delete rows works
  - [ ] Add series columns works (multi-series charts)
  - [ ] Cell highlighting (active columns) displays correctly
  - [ ] Data validation prevents invalid data
  - [ ] Save updates chart and persists to backend
- [ ] **Documentation Updated**:
  - [ ] README.md mentions Excel-like editor
  - [ ] CHANGELOG added for v4.0 release
- [ ] **Git Commits**:
  - [ ] Commit 1: Stage 1 - Data models
  - [ ] Commit 2: Stage 2 - Validation report
  - [ ] Commit 3: Stage 3.1-3.2 - Excel editor library
  - [ ] Commit 4: Stage 3.3 - Chart.js integration
  - [ ] Commit 5: Stage 3.4 - D3 integration
  - [ ] Commit 6: Stage 3.5 - Tests
- [ ] **Ready for Review**: Push feature branch to GitHub

---

## 🚀 Estimated Remaining Time

- **Stage 3.3** (Chart.js integration): 1-2 hours
- **Stage 3.4** (D3 integration): 2-3 hours
- **Stage 3.5** (Testing): 2-3 hours
- **Manual testing**: 1-2 hours
- **Total**: 6-10 hours remaining

---

## 📝 Notes for Implementation

### Static File Serving

Ensure `/static/js/chart-spreadsheet-editor.js` is served by FastAPI:

```python
# In rest_server.py
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### Browser Compatibility

The Excel editor uses modern JavaScript (ES6+). Ensure browsers support:
- Arrow functions
- Template literals
- Fetch API
- Async/await

### Performance Considerations

For charts with >50 rows, the Excel editor will:
- Show scrollable table
- Maintain performance with virtual scrolling (future enhancement)
- Limit to 50 rows max (enforced by validator)

---

## 🎯 Success Criteria

✅ **Feature is complete when**:
1. All 18 chart types have Excel-like editor
2. All Excel features work (keyboard nav, copy/paste, highlighting)
3. Tests pass with >90% coverage
4. Manual testing confirms UX matches PowerPoint Excel editor behavior
5. Feature branch pushed to GitHub for review
6. Documentation updated

---

## Version History

- **v1.0** (2025-11-28): Initial implementation guide
  - Stages 1-3.2 completed
  - Stages 3.3-3.5 pending
  - Ready for final implementation

---

**END OF IMPLEMENTATION GUIDE**
