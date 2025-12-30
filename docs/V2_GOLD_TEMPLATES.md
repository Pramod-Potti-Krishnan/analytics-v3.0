# V2 Gold Standard Templates

> Version 3.4.17 | Last Updated: December 2024

## Overview

The V2-chart-text layout provides a two-column design with a **chart visualization** (left) and **Key Insights panel** (right). This layout is the gold standard for analytics slides in Deckster presentations.

## Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                          V2-chart-text                          │
├────────────────────────────────┬────────────────────────────────┤
│                                │                                │
│          Chart HTML            │      Key Insights Panel        │
│       (1260px x 720px)         │        (600px x 680px)         │
│                                │                                │
│   • Chart subtitle (20px)      │   • "Key Insights" header      │
│   • Chart.js canvas            │   • 5 bullet points (18px)     │
│   • Edit button (pencil icon)  │   • Blue accent border         │
│                                │                                │
└────────────────────────────────┴────────────────────────────────┘
```

## Standard Specifications

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

### Layout Field Names
| Field | Description |
|-------|-------------|
| `chart_html` | Complete Chart.js canvas with initialization script |
| `body` | Key Insights HTML panel |
| `slide_title` | Slide title text |
| `subtitle` | Slide subtitle text |
| `logo` | Logo placeholder (usually empty) |

---

## Approved Gold Standard Charts

### 1. Line Chart
**Chart Type**: `line`
**Analytics Type**: `revenue_over_time`
**Use Case**: Time series trends, temporal data

```json
{
  "chart_type": "line",
  "analytics_type": "revenue_over_time",
  "data_format": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [25, 35, 30, 40]
  }
}
```

**Features**:
- Smooth line with tension
- Point markers with hover effects
- Gradient fill option
- Y-axis with grace padding

---

### 2. Vertical Bar Chart
**Chart Type**: `bar_vertical` (or `bar`)
**Analytics Type**: `category_ranking`
**Use Case**: Category comparisons, rankings

```json
{
  "chart_type": "bar_vertical",
  "analytics_type": "category_ranking",
  "data_format": {
    "labels": ["Category A", "Category B", "Category C"],
    "values": [100, 80, 60]
  }
}
```

**Features**:
- Rounded corners (borderRadius: 10)
- Individual bar colors from pastel palette
- Data labels at bar ends
- X-axis category labels

---

### 3. Pie Chart
**Chart Type**: `pie`
**Analytics Type**: `market_share`
**Use Case**: Part-to-whole relationships, distribution

```json
{
  "chart_type": "pie",
  "analytics_type": "market_share",
  "data_format": {
    "labels": ["Segment A", "Segment B", "Segment C"],
    "values": [40, 35, 25]
  }
}
```

**Features**:
- Offset on hover
- Percentage labels on slices
- Legend at top
- Subtle border between segments

---

### 4. Horizontal Bar Chart
**Chart Type**: `bar_horizontal`
**Analytics Type**: `category_ranking`
**Use Case**: Rankings with long labels, comparisons

```json
{
  "chart_type": "bar_horizontal",
  "analytics_type": "category_ranking",
  "data_format": {
    "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
    "values": [48000, 44000, 43000, 40000]
  }
}
```

**Features**:
- `indexAxis: "y"` for horizontal orientation
- Labels on Y-axis (left side)
- Values on X-axis
- Dollar formatting for financial data

---

### 5. Doughnut Chart
**Chart Type**: `doughnut`
**Analytics Type**: `market_share`
**Use Case**: Part-to-whole with center space, percentages

```json
{
  "chart_type": "doughnut",
  "analytics_type": "market_share",
  "data_format": {
    "labels": ["Product A", "Product B", "Product C"],
    "values": [45, 30, 25]
  }
}
```

**Features**:
- Center cutout (50%)
- Percentage labels
- Interactive hover effects
- Pastel color scheme

---

### 6. Scatter Chart
**Chart Type**: `scatter`
**Analytics Type**: `correlation_analysis`
**Use Case**: X-Y correlation, relationship analysis

```json
{
  "chart_type": "scatter",
  "analytics_type": "correlation_analysis",
  "data_format": {
    "datasets": [{
      "label": "Analytics",
      "data": [
        {"x": 19.5, "y": 15.65, "label": "Point A"},
        {"x": 37.21, "y": 28.45, "label": "Point B"}
      ]
    }]
  }
}
```

**Features**:
- Circular point markers (pointRadius: 8)
- White border on points
- Tooltip with x, y, and label values
- Both X and Y axes displayed

---

### 7. Bubble Chart
**Chart Type**: `bubble`
**Analytics Type**: `multidimensional_analysis`
**Use Case**: 3-variable visualization, sized comparisons

```json
{
  "chart_type": "bubble",
  "analytics_type": "multidimensional_analysis",
  "data_format": {
    "datasets": [{
      "label": "Analytics",
      "data": [
        {"x": 20, "y": 30, "r": 15, "label": "Item A"},
        {"x": 40, "y": 50, "r": 25, "label": "Item B"}
      ]
    }]
  }
}
```

**Features**:
- Bubble size (`r`) represents third dimension
- Semi-transparent fill
- Tooltip shows x, y, r, and label
- Scale respects bubble radii

---

### 8. Polar Area Chart
**Chart Type**: `polar_area`
**Analytics Type**: `radial_composition`
**Use Case**: Radial part-to-whole, categorical distribution

```json
{
  "chart_type": "polar_area",
  "analytics_type": "radial_composition",
  "data_format": {
    "labels": ["Category A", "Category B", "Category C"],
    "values": [50, 30, 20]
  }
}
```

**Features**:
- Radial segments from center
- Equal angular width, varying radius
- Pastel color scheme
- Legend at top

---

### 9. Radar Chart
**Chart Type**: `radar`
**Analytics Type**: `multi_metric_comparison`
**Use Case**: Multi-dimensional performance comparison

```json
{
  "chart_type": "radar",
  "analytics_type": "multi_metric_comparison",
  "data_format": {
    "labels": ["Customer Sat.", "Quality Score", "Delivery Speed", "Cost Efficiency"],
    "datasets": [{
      "label": "Performance",
      "data": [100.0, 79.7, 80.6, 73.8]
    }]
  }
}
```

**Features**:
- Normalized values (0-100 scale)
- Semi-transparent fill
- Point markers at vertices
- Grid lines for scale reference

---

### 10. Area Chart
**Chart Type**: `area`
**Analytics Type**: `revenue_over_time`
**Use Case**: Time series with filled area, cumulative trends
**Validated**: v3.4.25 (December 2024)

```json
{
  "chart_type": "area",
  "analytics_type": "revenue_over_time",
  "data_format": {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "values": [30000, 35000, 32000, 40000, 38000, 45000]
  }
}
```

**Features**:
- Filled area under line
- Gradient fill effect
- Smooth line with tension
- Interactive spreadsheet editor with data persistence
- Series name editing support

---

### 11. Stacked Area Chart
**Chart Type**: `area_stacked`
**Analytics Type**: `revenue_over_time`
**Use Case**: Multi-series cumulative trends, composition over time
**Validated**: v3.4.25 (December 2024)

```json
{
  "chart_type": "area_stacked",
  "analytics_type": "revenue_over_time",
  "data_format": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [
      {"label": "Product A", "data": [50000, 55000, 60000, 65000]},
      {"label": "Product B", "data": [30000, 35000, 40000, 45000]},
      {"label": "Series C", "data": [20000, 25000, 30000, 35000]}
    ]
  }
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

### 12. Grouped Bar Chart (Multi-Column)
**Chart Type**: `bar_grouped`
**Analytics Type**: `category_ranking`
**Use Case**: Side-by-side category comparison across series
**Validated**: v3.4.25 (December 2024)

```json
{
  "chart_type": "bar_grouped",
  "analytics_type": "category_ranking",
  "data_format": {
    "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
    "datasets": [
      {"label": "Series A", "data": [52000, 48000, 51000, 54000]},
      {"label": "Series B", "data": [49000, 37000, 50000, 44000]},
      {"label": "Series C", "data": [54000, 61000, 29000, 45000]}
    ]
  }
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

### 13. Stacked Bar Chart
**Chart Type**: `bar_stacked`
**Analytics Type**: `category_ranking`
**Use Case**: Cumulative category totals with component breakdown
**Validated**: v3.4.25 (December 2024)

```json
{
  "chart_type": "bar_stacked",
  "analytics_type": "category_ranking",
  "data_format": {
    "labels": ["Revenue", "Profit", "Growth Rate", "Customer Sat."],
    "datasets": [
      {"label": "Series A", "data": [66000, 67000, 37000, 64000]},
      {"label": "Series B", "data": [76000, 53000, 38000, 48000]},
      {"label": "Series C", "data": [62000, 55000, 45000, 60000]}
    ]
  }
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

## API Usage

### Endpoint
```
POST /api/v1/analytics/L02/{analytics_type}?use_synthetic=true
```

### Request Body
```json
{
  "presentation_id": "pres-123",
  "slide_id": "slide-1",
  "slide_number": 1,
  "narrative": "Analysis description for data generation",
  "chart_type": "line"
}
```

### Response
```json
{
  "content": {
    "chart_html": "<div class=\"l02-chart-container\">...</div>",
    "body": "<div class=\"l02-observations-panel\">...</div>",
    "element_3": "...",
    "element_2": "..."
  },
  "metadata": {
    "layout": "L02",
    "generated_at": "2025-12-29T...",
    "synthetic_data_used": true
  }
}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.4.17 | 2024-12-30 | Added radar to multi_series_chart_types, fixed radar data handling |
| v3.4.16 | 2024-12-29 | Fixed validator to accept dict format for radar charts |
| v3.4.15 | 2024-12-29 | Standardized #6b7280 color for all text elements |
| v3.4.14 | 2024-12-29 | Changed chart subtitle font from 18px to 20px |
| v3.4.11 | 2024-12-28 | Added chart title generation from narrative |

---

## Test References

- **Basic Charts Test**: `tests/test_analytics_basic_charts.sh` (line, bar_vertical, pie)
- **Next Charts Test**: `tests/test_v2_next_charts.sh` (bar_horizontal, doughnut, scatter, bubble, radar, polar_area)
- **Test Output**: `test_outputs/v2_next_charts_YYYYMMDD_HHMMSS/`
