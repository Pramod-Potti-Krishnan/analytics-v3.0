# Analytics Service API Reference

**Version**: 3.4.25
**Base URL**: `http://localhost:8080` (local) | Production via Railway
**Last Updated**: December 2024

---

## Production URL

**Base URL**: `https://analytics-v30-production.up.railway.app`

All endpoints below should be prefixed with this base URL in production.

---

## GOLD STANDARD: 13 Tested & Approved Chart Types (V2-chart-text Layout)

These 13 chart types have been **tested and approved** for production use. They generate analytics slides with Chart.js visualizations and AI-generated Key Insights.

### Endpoint Summary

| Chart Type | Endpoint | Analytics Type | Use Case |
|------------|----------|----------------|----------|
| **line** | `POST /api/v1/analytics/L02/revenue_over_time` | `revenue_over_time` | Time series trends |
| **bar_vertical** | `POST /api/v1/analytics/L02/category_ranking` | `category_ranking` | Category comparisons |
| **pie** | `POST /api/v1/analytics/L02/market_share` | `market_share` | Part-to-whole |
| **bar_horizontal** | `POST /api/v1/analytics/L02/category_ranking` | `category_ranking` | Rankings with long labels |
| **doughnut** | `POST /api/v1/analytics/L02/market_share` | `market_share` | Composition with center |
| **scatter** | `POST /api/v1/analytics/L02/correlation_analysis` | `correlation_analysis` | X-Y correlation |
| **bubble** | `POST /api/v1/analytics/L02/multidimensional_analysis` | `multidimensional_analysis` | 3-variable analysis |
| **polar_area** | `POST /api/v1/analytics/L02/radial_composition` | `radial_composition` | Radial distribution |
| **radar** | `POST /api/v1/analytics/L02/multi_metric_comparison` | `multi_metric_comparison` | Multi-dimensional comparison |
| **area** | `POST /api/v1/analytics/L02/revenue_over_time` | `revenue_over_time` | Filled time series |
| **area_stacked** | `POST /api/v1/analytics/L02/revenue_over_time` | `revenue_over_time` | Multi-series cumulative |
| **bar_grouped** | `POST /api/v1/analytics/L02/category_ranking` | `category_ranking` | Side-by-side comparison |
| **bar_stacked** | `POST /api/v1/analytics/L02/category_ranking` | `category_ranking` | Cumulative breakdown |

### V2-chart-text Layout Structure

```
+-------------------------------------------------------------+
|                       V2-chart-text                          |
+-----------------------------+-------------------------------+
|                             |                               |
|        Chart HTML           |      Key Insights Panel       |
|      (1260px x 720px)       |       (600px x 680px)         |
|                             |                               |
|   - Chart subtitle (20px)   |   - "Key Insights" header     |
|   - Chart.js canvas         |   - 5 bullet points (18px)    |
|   - Edit button (pencil)    |   - Blue accent border        |
|                             |                               |
+-----------------------------+-------------------------------+
```

### Response Field Mapping

| Field | Description | Alias |
|-------|-------------|-------|
| `chart_html` | Complete Chart.js canvas with initialization script | `element_3`, `element_4` |
| `body` | Key Insights HTML panel | `element_2` |
| `slide_title` | Slide title text | - |
| `subtitle` | Slide subtitle text | - |

---

## Gold Standard Charts (13 Total)

### Chart Set 1: Basic Charts (Validated in Round 1)

#### 1. Line Chart
**Chart Type**: `line`
**Analytics Type**: `revenue_over_time`
**Use Case**: Time series trends, temporal data

**Request**:
```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time?use_synthetic=true" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-123",
    "slide_id": "slide-1",
    "slide_number": 1,
    "narrative": "Show quarterly revenue growth highlighting strong Q3-Q4 performance",
    "chart_type": "line"
  }'
```

**Response**:
```json
{
  "content": {
    "chart_html": "<div class=\"l02-chart-container\">...<canvas id=\"chart-slide-1\">...</canvas>...</div>",
    "body": "<div class=\"l02-observations-panel\"><h3>Key Insights</h3><ul><li>Revenue grew 42%...</li></ul></div>",
    "element_3": "...",
    "element_2": "..."
  },
  "metadata": {
    "service": "analytics_v3",
    "chart_type": "line",
    "layout": "L02",
    "data_source": "synthetic",
    "synthetic_data_used": true,
    "data_points": 4,
    "generation_time_ms": 1250
  }
}
```

**Data Format**:
```json
{
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "values": [25, 35, 30, 40]
}
```

**Features**:
- Smooth line with tension
- Point markers with hover effects
- Gradient fill option
- Y-axis with grace padding

---

#### 2. Vertical Bar Chart
**Chart Type**: `bar_vertical` (or `bar`)
**Analytics Type**: `category_ranking`
**Use Case**: Category comparisons, rankings

**Request**:
```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/category_ranking?use_synthetic=true" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-123",
    "slide_id": "slide-2",
    "slide_number": 2,
    "narrative": "Compare department performance rankings",
    "chart_type": "bar_vertical"
  }'
```

**Data Format**:
```json
{
  "labels": ["Category A", "Category B", "Category C"],
  "values": [100, 80, 60]
}
```

**Features**:
- Rounded corners (borderRadius: 10)
- Individual bar colors from pastel palette
- Data labels at bar ends
- X-axis category labels

---

#### 3. Pie Chart
**Chart Type**: `pie`
**Analytics Type**: `market_share`
**Use Case**: Part-to-whole relationships, distribution

**Request**:
```bash
curl -X POST "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share?use_synthetic=true" \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-123",
    "slide_id": "slide-3",
    "slide_number": 3,
    "narrative": "Show market share distribution across segments",
    "chart_type": "pie"
  }'
```

**Data Format**:
```json
{
  "labels": ["Segment A", "Segment B", "Segment C"],
  "values": [40, 35, 25]
}
```

**Features**:
- Offset on hover
- Percentage labels on slices
- Legend at top
- Subtle border between segments

---

### Chart Set 2: Next Charts (Validated in Round 1)

#### 4. Horizontal Bar Chart
**Chart Type**: `bar_horizontal`
**Analytics Type**: `category_ranking`
**Use Case**: Rankings with long labels, comparisons

**Data Format**:
```json
{
  "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
  "values": [48000, 44000, 43000, 40000]
}
```

**Features**:
- `indexAxis: "y"` for horizontal orientation
- Labels on Y-axis (left side)
- Values on X-axis
- Dollar formatting for financial data

---

#### 5. Doughnut Chart
**Chart Type**: `doughnut`
**Analytics Type**: `market_share`
**Use Case**: Part-to-whole with center space, percentages

**Data Format**:
```json
{
  "labels": ["Product A", "Product B", "Product C"],
  "values": [45, 30, 25]
}
```

**Features**:
- Center cutout (50%)
- Percentage labels
- Interactive hover effects
- Pastel color scheme

---

#### 6. Scatter Chart
**Chart Type**: `scatter`
**Analytics Type**: `correlation_analysis`
**Use Case**: X-Y correlation, relationship analysis

**Data Format**:
```json
{
  "datasets": [{
    "label": "Analytics",
    "data": [
      {"x": 19.5, "y": 15.65, "label": "Point A"},
      {"x": 37.21, "y": 28.45, "label": "Point B"}
    ]
  }]
}
```

**Features**:
- Circular point markers (pointRadius: 8)
- White border on points
- Tooltip with x, y, and label values
- Both X and Y axes displayed

---

#### 7. Bubble Chart
**Chart Type**: `bubble`
**Analytics Type**: `multidimensional_analysis`
**Use Case**: 3-variable visualization, sized comparisons

**Data Format**:
```json
{
  "datasets": [{
    "label": "Analytics",
    "data": [
      {"x": 20, "y": 30, "r": 15, "label": "Item A"},
      {"x": 40, "y": 50, "r": 25, "label": "Item B"}
    ]
  }]
}
```

**Features**:
- Bubble size (`r`) represents third dimension
- Semi-transparent fill
- Tooltip shows x, y, r, and label
- Scale respects bubble radii

---

#### 8. Polar Area Chart
**Chart Type**: `polar_area`
**Analytics Type**: `radial_composition`
**Use Case**: Radial part-to-whole, categorical distribution

**Data Format**:
```json
{
  "labels": ["Category A", "Category B", "Category C"],
  "values": [50, 30, 20]
}
```

**Features**:
- Radial segments from center
- Equal angular width, varying radius
- Pastel color scheme
- Legend at top

---

#### 9. Radar Chart
**Chart Type**: `radar`
**Analytics Type**: `multi_metric_comparison`
**Use Case**: Multi-dimensional performance comparison

**Data Format**:
```json
{
  "labels": ["Customer Sat.", "Quality Score", "Delivery Speed", "Cost Efficiency"],
  "datasets": [{
    "label": "Performance",
    "data": [100.0, 79.7, 80.6, 73.8]
  }]
}
```

**Features**:
- Normalized values (0-100 scale)
- Semi-transparent fill
- Point markers at vertices
- Grid lines for scale reference

---

### Chart Set 3: Advanced Multi-Series Charts (Validated in Round 2 - v3.4.25)

#### 10. Area Chart
**Chart Type**: `area`
**Analytics Type**: `revenue_over_time`
**Use Case**: Time series with filled area, cumulative trends
**Validated**: v3.4.25 (December 2024)

**Data Format**:
```json
{
  "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  "values": [30000, 35000, 32000, 40000, 38000, 45000]
}
```

**Features**:
- Filled area under line
- Gradient fill effect
- Smooth line with tension
- Interactive spreadsheet editor with data persistence
- Series name editing support

---

#### 11. Stacked Area Chart
**Chart Type**: `area_stacked`
**Analytics Type**: `revenue_over_time`
**Use Case**: Multi-series cumulative trends, composition over time
**Validated**: v3.4.25 (December 2024)

**Data Format**:
```json
{
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [
    {"label": "Product A", "data": [50000, 55000, 60000, 65000]},
    {"label": "Product B", "data": [30000, 35000, 40000, 45000]},
    {"label": "Series C", "data": [20000, 25000, 30000, 35000]}
  ]
}
```

**Features**:
- Multiple stacked series
- Each series fills above previous
- Multi-series color palette
- Interactive spreadsheet editor
- **Editable series names** (v3.4.24+)
- Data persists across slide navigation (v3.4.25 localStorage)

---

#### 12. Grouped Bar Chart (Multi-Column)
**Chart Type**: `bar_grouped`
**Analytics Type**: `category_ranking`
**Use Case**: Side-by-side category comparison across series
**Validated**: v3.4.25 (December 2024)

**Data Format**:
```json
{
  "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
  "datasets": [
    {"label": "Series A", "data": [52000, 48000, 51000, 54000]},
    {"label": "Series B", "data": [49000, 37000, 50000, 44000]},
    {"label": "Series C", "data": [54000, 61000, 29000, 45000]}
  ]
}
```

**Features**:
- Side-by-side bars for each category
- Multiple series with distinct colors
- Rounded corners (borderRadius: 10)
- Interactive spreadsheet editor
- **Editable series names** (v3.4.24+)
- Data persists across slide navigation (v3.4.25 localStorage)

---

#### 13. Stacked Bar Chart
**Chart Type**: `bar_stacked`
**Analytics Type**: `category_ranking`
**Use Case**: Cumulative category totals with component breakdown
**Validated**: v3.4.25 (December 2024)

**Data Format**:
```json
{
  "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
  "datasets": [
    {"label": "Series A", "data": [66000, 67000, 37000, 64000]},
    {"label": "Series B", "data": [76000, 53000, 38000, 48000]},
    {"label": "Series C", "data": [62000, 55000, 45000, 60000]}
  ]
}
```

**Features**:
- Stacked bars showing cumulative totals
- Multiple series stacked vertically
- X and Y axis stacked: true
- Multi-series color palette
- Interactive spreadsheet editor
- **Editable series names** (v3.4.24+)
- Data persists across slide navigation (v3.4.25 localStorage)

---

## API Contracts

### Primary Endpoint

```
POST /api/v1/analytics/L02/{analytics_type}?use_synthetic=true
```

### Request Schema

```json
{
  "presentation_id": "pres-123",
  "slide_id": "slide-1",
  "slide_number": 1,
  "narrative": "Analysis description for data generation",
  "chart_type": "line",
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000}
  ],
  "context": {
    "theme": "professional",
    "audience": "Board of Directors"
  }
}
```

### Response Schema

```json
{
  "content": {
    "chart_html": "<div class=\"l02-chart-container\">...</div>",
    "body": "<div class=\"l02-observations-panel\">...</div>",
    "element_3": "...",
    "element_2": "..."
  },
  "metadata": {
    "service": "analytics_v3",
    "chart_type": "line",
    "layout": "L02",
    "data_source": "synthetic",
    "synthetic_data_used": true,
    "data_points": 4,
    "generation_time_ms": 1250
  }
}
```

### Layout Service Integration

```json
{
  "layout": "V2-chart-text",
  "content": {
    "slide_title": "Quarterly Revenue Growth",
    "subtitle": "FY 2024 Performance",
    "chart_html": "...from Analytics Service response content.chart_html...",
    "body": "...from Analytics Service response content.body...",
    "logo": " "
  }
}
```

---

## Director Integration

### Content Routing

Use `POST /api/v1/analytics/can-handle` to determine if content should be routed to Analytics Service:

**Request**:
```json
{
  "slide_content": {
    "title": "Q4 Revenue Analysis",
    "topics": ["Revenue grew 15%", "New markets +30%"],
    "topic_count": 2
  },
  "content_hints": {
    "has_numbers": true,
    "is_time_based": true,
    "detected_keywords": ["revenue", "growth"]
  }
}
```

**Response**:
```json
{
  "can_handle": true,
  "confidence": 0.95,
  "reason": "contains numerical data | time series detected | keywords matched",
  "suggested_approach": "chart"
}
```

### Confidence Score Guidelines

| Score | Meaning | Action |
|-------|---------|--------|
| 0.90+ | Excellent fit | Use Analytics Service |
| 0.70-0.89 | Good fit | Use Analytics Service |
| 0.40-0.69 | Acceptable | Consider alternatives |
| < 0.40 | Poor fit | Route to Text Service |

### Chart Recommendation

Use `POST /api/v1/analytics/recommend-chart` to get chart type recommendations:

**Request**:
```json
{
  "slide_content": {
    "title": "Revenue Trend",
    "topics": ["Show revenue growth over 4 quarters"],
    "topic_count": 1
  },
  "detected_patterns": ["time_series"]
}
```

**Response**:
```json
{
  "recommended_charts": [
    {"chart_type": "line", "confidence": 0.95, "reason": "Time series data best shown as line chart"},
    {"chart_type": "area", "confidence": 0.80, "reason": "Area chart also effective for trends"}
  ]
}
```

---

## Typography & Color Standards

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Chart subtitle | Inter | 20px | 400 | #4B5563 |
| Key Insights header | Inter | 24px | 700 | #3B82F6 |
| Insight bullets | Inter | 18px | 400 | #4B5563 |
| Axis labels | Inter | 12px | 500 | #6b7280 |
| Axis titles | Inter | 13px | Bold | #4b5563 |
| Legend labels | Inter | 14px | Bold | #6b7280 |

### Color Standards (v3.4.15)

- **Text/Axes/Labels**: #6b7280 (gray-500)
- **Accent Blue**: #3B82F6 / #60A5FA
- **Chart Colors**: Pastel palette (#93C5FD, #A7F3D0, #FDE68A, #C4B5FD, #FBCFE8, #FED7AA, #A5F3FC, #FCA5A5)

---

## Interactive Spreadsheet Editor

All L02 charts include an interactive Excel-like spreadsheet editor (v3.4.24+):

### Features

- **Edit Button**: Pencil icon on chart hover
- **Series Name Editing**: Click series header to rename
- **Data Editing**: Click cells to modify values
- **Add/Remove Rows**: Dynamic row management
- **Data Persistence**: Saves to localStorage (v3.4.25)

### API Endpoint for Saving

```
POST /api/charts/update-data
```

**Request (Single-Series)**:
```json
{
  "chart_id": "chart-slide-1",
  "presentation_id": "pres-123",
  "chart_type": "bar_vertical",
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "values": [100, 150, 200, 175]
}
```

**Request (Multi-Series)**:
```json
{
  "chart_id": "chart-slide-1",
  "presentation_id": "pres-123",
  "chart_type": "bar_grouped",
  "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [
    {"label": "Product A", "data": [100, 120, 140, 160]},
    {"label": "Product B", "data": [80, 95, 110, 125]}
  ]
}
```

---

## Test References

### Round 1: Basic 9 Chart Types

**Test Script**: `tests/test_v2_gold_standard_all.sh`

```bash
# Test all 9 basic gold standard charts
./tests/test_v2_gold_standard_all.sh
```

**Charts Tested**:
1. line (revenue_over_time)
2. bar_vertical (category_ranking)
3. pie (market_share)
4. bar_horizontal (category_ranking)
5. doughnut (market_share)
6. scatter (correlation_analysis)
7. bubble (multidimensional_analysis)
8. polar_area (radial_composition)
9. radar (multi_metric_comparison)

**Result**: 9/9 PASSED

### Round 2: Advanced Multi-Series Charts

**Test Script**: `tests/test_v2_chartjs_remaining.sh`

```bash
# Test remaining Chart.js chart types
./tests/test_v2_chartjs_remaining.sh
```

**Charts Tested**:
1. area (revenue_over_time) - PASSED
2. area_stacked (revenue_over_time) - PASSED
3. bar_grouped (category_ranking) - PASSED
4. bar_stacked (category_ranking) - PASSED
5. waterfall (revenue_over_time) - FAILED (not yet implemented)

**Result**: 4/5 PASSED (waterfall pending)

### Test Output Location

```
test_outputs/v2_gold_standard_YYYYMMDD_HHMMSS/
test_outputs/v2_chartjs_remaining_YYYYMMDD_HHMMSS/
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.4.25 | 2024-12-30 | Added localStorage persistence for chart edits, validated area/area_stacked/bar_grouped/bar_stacked |
| v3.4.24 | 2024-12-30 | Fixed multi-series detection in _exportData(), editable series names |
| v3.4.17 | 2024-12-30 | Added radar to multi_series_chart_types, fixed radar data handling |
| v3.4.16 | 2024-12-29 | Fixed validator to accept dict format for radar charts |
| v3.4.15 | 2024-12-29 | Standardized #6b7280 color for all text elements |
| v3.4.14 | 2024-12-29 | Changed chart subtitle font from 18px to 20px |
| v3.4.11 | 2024-12-28 | Added chart title generation from narrative |
| v3.1.0 | 2024-12 | Added Director coordination endpoints |

---

## Related Documents

- [V2_GOLD_TEMPLATES.md](../../analytics_microservice/docs/V2_GOLD_TEMPLATES.md) - Detailed chart specifications
- [TEXT_SERVICE_API_REFERENCE.md](./TEXT_SERVICE_API_REFERENCE.md) - Text Service integration
- [SERVICE_CAPABILITIES_SPEC.md](./SERVICE_CAPABILITIES_SPEC.md) - Coordination endpoint specification
