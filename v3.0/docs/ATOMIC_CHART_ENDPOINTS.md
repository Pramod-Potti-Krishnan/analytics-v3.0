# Atomic Chart Endpoints (v3.5.0)

> Generate atomic chart elements with synthetic data for frontend positioning

## Overview

Atomic chart endpoints provide 14 gold standard chart types as self-contained HTML elements. Each endpoint:

- Generates a single chart element using synthetic data
- Optionally includes a Key Insights panel as a separate element
- Returns self-contained HTML ready for frontend positioning
- Requires no external data - synthetic data is generated based on narrative context

## The 14 Gold Standard Chart Types

| # | Chart ID | Display Name | Category | Use Cases |
|---|----------|--------------|----------|-----------|
| 1 | `line` | Line Chart | Trend | Time series, Performance over time |
| 2 | `bar_vertical` | Vertical Bar Chart | Comparison | Category comparison, Rankings |
| 3 | `bar_horizontal` | Horizontal Bar Chart | Comparison | Long labels, Survey results |
| 4 | `pie` | Pie Chart | Composition | Market share, Distribution |
| 5 | `doughnut` | Doughnut Chart | Composition | KPI breakdown, Portfolio mix |
| 6 | `scatter` | Scatter Plot | Correlation | Correlations, Outlier detection |
| 7 | `bubble` | Bubble Chart | Correlation | 3D visualization, Product positioning |
| 8 | `polar_area` | Polar Area Chart | Composition | Cyclical data, Seasonal patterns |
| 9 | `radar` | Radar Chart | Comparison | Multi-attribute comparison, Skills |
| 10 | `area` | Area Chart | Trend | Cumulative totals, Volume over time |
| 11 | `area_stacked` | Stacked Area Chart | Composition | Part-to-whole over time |
| 12 | `bar_grouped` | Grouped Bar Chart | Comparison | Multi-series comparison, Before/after |
| 13 | `bar_stacked` | Stacked Bar Chart | Composition | Budget breakdown, Sales composition |
| 14 | `waterfall` | Waterfall Chart | Flow | Bridge analysis, P&L breakdown |

---

## API Endpoints

### Base URL

```
https://analytics-v30-production.up.railway.app/api/v1/charts/atomic
```

### Catalog Endpoint

```http
GET /api/v1/charts/atomic/catalog
```

Returns metadata for all 14 chart types.

**Response:**
```json
{
  "success": true,
  "count": 14,
  "chart_types": [
    {
      "id": "line",
      "name": "Line Chart",
      "description": "Line Chart for Time series, Trends",
      "category": "trend",
      "data_format": "labels + values",
      "min_points": 2,
      "max_points": 50,
      "supports_multi_series": true,
      "example_use_cases": ["Time series", "Trends", "Performance over time"]
    }
  ],
  "endpoint_pattern": "/api/v1/charts/atomic/{chart_id}"
}
```

### Generate Chart Endpoint

```http
POST /api/v1/charts/atomic/{chart_id}
```

Generates an atomic chart element.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `chart_id` | string | One of 14 gold standard chart IDs |

**Request Body:**
```json
{
  "narrative": "Show quarterly revenue growth for 2024",
  "include_insights": true,
  "num_points": 4,
  "width": 850,
  "height": 500,
  "chart_title": "Revenue Growth Q1-Q4 2024",
  "theme": "professional"
}
```

**Request Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `narrative` | string | null | Context for data generation |
| `include_insights` | boolean | false | Include Key Insights panel |
| `num_points` | integer | auto | Number of data points (2-50) |
| `width` | integer | 850 | Chart container width (px) |
| `height` | integer | 500 | Chart container height (px) |
| `chart_title` | string | auto | Override auto-generated title |
| `theme` | string | "professional" | Color theme |
| `presentation_id` | string | null | For editor integration |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `theme` | string | "professional" | Color theme (professional, corporate, vibrant) |

---

## Response Structure

### Success Response

```json
{
  "success": true,
  "chart_id": "line",
  "chart_html": "<div class=\"atomic-chart-container\">...</div>",
  "insights_html": "<div class=\"atomic-insights-container\">...</div>",
  "data_used": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 162000},
    {"label": "Q4 2024", "value": 178000}
  ],
  "chart_title": "Revenue Growth Q1-Q4 2024",
  "generation_time_ms": 45,
  "synthetic_data": true,
  "chart_dimensions": {"width": 850, "height": 500},
  "insights_dimensions": {"width": 400, "height": 500},
  "element_id": "atomic-chart-abc12345"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether generation succeeded |
| `chart_id` | string | The chart type requested |
| `chart_html` | string | Self-contained chart HTML with scripts |
| `insights_html` | string | Key Insights panel HTML (if requested) |
| `data_used` | array | Synthetic data used for the chart |
| `chart_title` | string | Generated or provided title |
| `generation_time_ms` | integer | Processing time in milliseconds |
| `synthetic_data` | boolean | Always true for atomic endpoints |
| `chart_dimensions` | object | Width and height of chart container |
| `insights_dimensions` | object | Width and height of insights panel |
| `element_id` | string | Unique ID for frontend positioning |

### Error Response

```json
{
  "success": false,
  "error_code": "INVALID_CHART_TYPE",
  "message": "Chart type 'unknown' is not supported",
  "details": {"provided": "unknown", "valid_types": [...]},
  "suggestion": "Use one of: line, bar_vertical, ..."
}
```

---

## Usage Examples

### Basic Line Chart

```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/charts/atomic/line" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Show quarterly revenue growth for 2024"
  }'
```

### Bar Chart with Insights

```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/charts/atomic/bar_vertical" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Compare department performance rankings",
    "include_insights": true,
    "width": 900,
    "height": 600
  }'
```

### Pie Chart with Custom Title

```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/charts/atomic/pie" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Market share distribution",
    "chart_title": "Q4 2024 Market Share",
    "num_points": 5
  }'
```

### Scatter Plot for Correlation Analysis

```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/charts/atomic/scatter" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Customer satisfaction vs revenue correlation",
    "include_insights": true
  }'
```

### Waterfall Chart for Financial Analysis

```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/charts/atomic/waterfall" \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Net income bridge from revenue to profit",
    "width": 1000,
    "height": 550
  }'
```

---

## HTML Output Structure

### Chart Container

```html
<div class="atomic-chart-container"
     data-chart-id="line"
     data-element-id="atomic-chart-abc12345"
     style="width: 850px; height: 500px; position: relative;">
  <div class="chart-title-bar" style="padding: 8px 16px; font-weight: 600;">
    Revenue Growth Q1-Q4 2024
  </div>
  <div class="chart-content" style="flex: 1; padding: 12px;">
    <canvas id="atomic-chart-abc12345"></canvas>
    <script>
      // Chart.js initialization with IIFE wrapper
    </script>
  </div>
</div>
```

### Insights Panel

```html
<div class="atomic-insights-container"
     data-chart-id="line"
     style="width: 400px; height: 500px; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border-radius: 12px; padding: 24px;">
  <h4 class="insights-header" style="color: #1E40AF;">
    Key Insights
  </h4>
  <ul class="insights-list" style="color: #1E3A5F;">
    <li>Revenue grew 25% year over year</li>
    <li>Q3 showed strongest acceleration</li>
    <li>Trend indicates continued growth</li>
  </ul>
</div>
```

---

## Frontend Integration

### Positioning Charts

The atomic elements are self-contained and can be positioned anywhere:

```javascript
// Fetch atomic chart
const response = await fetch('/api/v1/charts/atomic/line', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    narrative: 'Show revenue trend',
    include_insights: true
  })
});

const { chart_html, insights_html, element_id } = await response.json();

// Position chart on slide
const chartContainer = document.createElement('div');
chartContainer.style.cssText = 'position: absolute; left: 50px; top: 100px;';
chartContainer.innerHTML = chart_html;
slide.appendChild(chartContainer);

// Position insights panel separately
if (insights_html) {
  const insightsContainer = document.createElement('div');
  insightsContainer.style.cssText = 'position: absolute; right: 50px; top: 100px;';
  insightsContainer.innerHTML = insights_html;
  slide.appendChild(insightsContainer);
}
```

### Re-rendering Charts

Charts use inline scripts with IIFE wrappers. To re-render after DOM insertion:

```javascript
// Charts auto-initialize when added to DOM
// For Reveal.js, charts reinitialize on slide change
```

---

## Data Formats by Chart Type

### Simple Charts (labels + values)
`line`, `bar_vertical`, `bar_horizontal`, `pie`, `doughnut`, `polar_area`, `area`

```json
[
  {"label": "Q1", "value": 125000},
  {"label": "Q2", "value": 145000}
]
```

### Scatter/Bubble Charts (x, y, r)
`scatter`, `bubble`

```json
[
  {"label": "Acme Corp", "x": 85, "y": 92},
  {"label": "TechFlow", "x": 72, "y": 88, "r": 25}
]
```

### Radar Charts (normalized 0-100)
`radar`

```json
[
  {"label": "Customer Sat.", "value": 85},
  {"label": "Quality Score", "value": 92}
]
```

### Waterfall Charts (positive/negative)
`waterfall`

```json
[
  {"label": "Opening Balance", "value": 100000},
  {"label": "Product Sales", "value": 45000},
  {"label": "COGS", "value": -25000},
  {"label": "Net Result", "value": 120000}
]
```

### Multi-Series Charts
`area_stacked`, `bar_grouped`, `bar_stacked`

Generated with multiple datasets internally.

---

## Themes

### Professional (Default)
- Pastel blue, mint, yellow, lavender palette
- Soft gradients
- Modern, clean appearance

### Corporate
- Deep blues, purples, oranges
- Business-focused palette
- Traditional presentation style

### Vibrant
- Bright, saturated colors
- High contrast
- Eye-catching visuals

---

## Error Handling

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_CHART_TYPE` | 400 | Unknown chart_id provided |
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `GENERATION_FAILED` | 500 | Chart generation failed |

---

## Testing

### Run Test Script

```bash
cd v3.0/tests
./test_atomic_charts.sh
```

### Run Unit Tests

```bash
cd v3.0
pytest tests/test_atomic_charts.py -v
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.5.0 | 2025-01-01 | Initial atomic endpoints for 14 chart types |

---

## Related Documentation

- [Chart Type Catalog](./CHART_TYPE_CATALOG.md)
- [Integration Guide](./INTEGRATION_GUIDE.md)
- [Error Codes](./ERROR_CODES.md)
