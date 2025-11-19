# Data Format Reference - Analytics Microservice v3.4.3

**Complete reference for data formats expected by all 22 chart types**

---

## Overview

The Analytics Microservice supports two main data format patterns:

1. **Simple Format**: `[{label: string, value: number}, ...]` - For basic single-series charts
2. **Complex Format**: Nested structures with specific schemas - For multi-series and plugin charts

---

## 1. Simple Format Charts (9 types)

These charts accept straightforward `{label, value}` arrays:

### 1.1 Line Chart (`line`)

**Use Case**: Trends over time, time series data

**Data Format**:
```json
{
  "data": [
    {"label": "Jan 2024", "value": 125000},
    {"label": "Feb 2024", "value": 145000},
    {"label": "Mar 2024", "value": 162000},
    {"label": "Apr 2024", "value": 178000}
  ]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-001",
    "slide_id": "slide-1",
    "slide_number": 1,
    "narrative": "Show monthly revenue trend",
    "data": [
      {"label": "Jan", "value": 125000},
      {"label": "Feb", "value": 145000},
      {"label": "Mar", "value": 162000}
    ]
  }'
```

---

### 1.2 Vertical Bar Chart (`bar_vertical`)

**Use Case**: Categorical comparisons, rankings

**Data Format**:
```json
{
  "data": [
    {"label": "Product A", "value": 450},
    {"label": "Product B", "value": 320},
    {"label": "Product C", "value": 280},
    {"label": "Product D", "value": 150}
  ]
}
```

---

### 1.3 Horizontal Bar Chart (`bar_horizontal`)

**Use Case**: Rankings with long labels, comparison

**Data Format**: Same as `bar_vertical`
```json
{
  "data": [
    {"label": "Sales Department", "value": 850000},
    {"label": "Marketing Department", "value": 620000},
    {"label": "Engineering Department", "value": 450000}
  ]
}
```

---

### 1.4 Pie Chart (`pie`)

**Use Case**: Part-to-whole relationships, proportions

**Data Format**:
```json
{
  "data": [
    {"label": "North America", "value": 45},
    {"label": "Europe", "value": 30},
    {"label": "Asia", "value": 20},
    {"label": "Other", "value": 5}
  ]
}
```

---

### 1.5 Doughnut Chart (`doughnut`)

**Use Case**: Same as pie chart but with center cutout

**Data Format**: Same as `pie`
```json
{
  "data": [
    {"label": "Direct Sales", "value": 65},
    {"label": "Channel Partners", "value": 25},
    {"label": "Online", "value": 10}
  ]
}
```

---

### 1.6 Scatter Plot (`scatter`)

**Use Case**: Correlation analysis, data distribution

**Data Format**:
```json
{
  "data": [
    {"label": "Point 1", "value": 25},
    {"label": "Point 2", "value": 45},
    {"label": "Point 3", "value": 35},
    {"label": "Point 4", "value": 55}
  ]
}
```

**Note**: For true X-Y scatter plots, use `bubble` chart type with x, y, z coordinates.

---

### 1.7 Radar Chart (`radar`)

**Use Case**: Multivariate data, skill assessments, competitive analysis

**Data Format**:
```json
{
  "data": [
    {"label": "Performance", "value": 85},
    {"label": "Reliability", "value": 90},
    {"label": "Features", "value": 75},
    {"label": "Support", "value": 80},
    {"label": "Price", "value": 70}
  ]
}
```

---

### 1.8 Polar Area Chart (`polar_area`)

**Use Case**: Cyclical data, directional data

**Data Format**: Same as `radar`
```json
{
  "data": [
    {"label": "Q1", "value": 45},
    {"label": "Q2", "value": 55},
    {"label": "Q3", "value": 60},
    {"label": "Q4", "value": 50}
  ]
}
```

---

### 1.9 Area Chart (`area`)

**Use Case**: Cumulative trends, volume over time

**Data Format**: Same as `line`
```json
{
  "data": [
    {"label": "Week 1", "value": 1200},
    {"label": "Week 2", "value": 1450},
    {"label": "Week 3", "value": 1680},
    {"label": "Week 4", "value": 1920}
  ]
}
```

---

## 2. Multi-Series Charts (5 types)

These charts require `datasets` array for multiple series:

### 2.1 Grouped Bar Chart (`bar_grouped`)

**Use Case**: Side-by-side comparison of multiple series

**Data Format**:
```json
{
  "data": [{
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [
      {
        "label": "2023 Revenue",
        "data": [100, 120, 140, 160]
      },
      {
        "label": "2024 Revenue",
        "data": [125, 145, 170, 195]
      }
    ]
  }]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/quarterly_comparison \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-002",
    "slide_id": "slide-2",
    "slide_number": 2,
    "narrative": "Compare 2023 vs 2024 quarterly revenue",
    "chart_type": "bar_grouped",
    "data": [{
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "datasets": [
        {"label": "2023", "data": [100, 120, 140, 160]},
        {"label": "2024", "data": [125, 145, 170, 195]}
      ]
    }]
  }'
```

---

### 2.2 Stacked Bar Chart (`bar_stacked`)

**Use Case**: Part-to-whole over categories, contribution breakdown

**Data Format**: Same structure as `bar_grouped`
```json
{
  "data": [{
    "labels": ["Product A", "Product B", "Product C"],
    "datasets": [
      {
        "label": "North America",
        "data": [45, 35, 50]
      },
      {
        "label": "Europe",
        "data": [30, 45, 35]
      },
      {
        "label": "Asia",
        "data": [25, 20, 15]
      }
    ]
  }]
}
```

---

### 2.3 Stacked Area Chart (`area_stacked`)

**Use Case**: Cumulative trends over time, composition changes

**Data Format**: Same as `bar_grouped`
```json
{
  "data": [{
    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
    "datasets": [
      {
        "label": "Direct Sales",
        "data": [120, 135, 150, 165, 180]
      },
      {
        "label": "Channel Sales",
        "data": [80, 90, 100, 110, 120]
      },
      {
        "label": "Online Sales",
        "data": [40, 50, 60, 70, 80]
      }
    ]
  }]
}
```

---

### 2.4 Mixed/Combo Chart (`mixed`)

**Use Case**: Combining different chart types (e.g., line + bar)

**Data Format**:
```json
{
  "data": [{
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [
      {
        "type": "line",
        "label": "Revenue",
        "data": [125, 145, 170, 195]
      },
      {
        "type": "bar",
        "label": "Costs",
        "data": [80, 90, 110, 120]
      }
    ]
  }]
}
```

**Important**: Each dataset must specify its `type` (line, bar, etc.)

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/kpi_metrics \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-003",
    "slide_id": "slide-3",
    "slide_number": 3,
    "narrative": "Show revenue vs costs trend",
    "chart_type": "mixed",
    "data": [{
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "datasets": [
        {"type": "line", "label": "Revenue", "data": [125, 145, 170, 195]},
        {"type": "bar", "label": "Costs", "data": [80, 90, 110, 120]}
      ]
    }]
  }'
```

---

### 2.5 Bubble Chart (`bubble`)

**Use Case**: Three-variable relationships (x, y, size)

**Data Format**:
```json
{
  "data": [{
    "labels": ["Product A", "Product B", "Product C"],
    "datasets": [{
      "label": "Product Performance",
      "data": [
        {"x": 45, "y": 85, "r": 15},
        {"x": 60, "y": 75, "r": 20},
        {"x": 70, "y": 90, "r": 25}
      ]
    }]
  }]
}
```

**Note**: `r` represents bubble radius (size)

---

## 3. Waterfall Chart (1 type)

### 3.1 Waterfall Chart (`waterfall`)

**Use Case**: Incremental changes, profit bridges, variance analysis

**Data Format**:
```json
{
  "data": [
    {"label": "Starting Revenue", "value": 100000},
    {"label": "Q1 Growth", "value": 25000},
    {"label": "Q2 Growth", "value": 20000},
    {"label": "Q3 Growth", "value": 50000},
    {"label": "Q4 Growth", "value": 25000},
    {"label": "Ending Revenue", "value": 220000}
  ]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-004",
    "slide_id": "slide-4",
    "slide_number": 4,
    "narrative": "Show revenue bridge from Q1 to Q4",
    "chart_type": "waterfall",
    "data": [
      {"label": "Q1 Starting", "value": 100000},
      {"label": "Q1 Change", "value": 25000},
      {"label": "Q2 Change", "value": 20000},
      {"label": "Q3 Change", "value": 50000},
      {"label": "Q4 Change", "value": 25000},
      {"label": "Q4 Ending", "value": 220000}
    ]
  }'
```

---

## 4. Plugin Charts - Complex Formats (7 types)

These charts require specialized data structures:

### 4.1 Treemap Chart (`treemap`)

**Use Case**: Hierarchical data, budget breakdown, disk usage, market share

**Data Format**: Simple label-value format (plugin handles hierarchy visualization)
```json
{
  "data": [
    {"label": "Engineering", "value": 450000},
    {"label": "Sales", "value": 320000},
    {"label": "Marketing", "value": 180000},
    {"label": "Operations", "value": 120000}
  ]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-005",
    "slide_id": "slide-5",
    "slide_number": 5,
    "narrative": "Show budget allocation by department",
    "chart_type": "treemap",
    "data": [
      {"label": "Engineering", "value": 450000},
      {"label": "Sales", "value": 320000},
      {"label": "Marketing", "value": 180000},
      {"label": "Operations", "value": 120000}
    ]
  }'
```

---

### 4.2 Heatmap Chart (`heatmap` or `matrix`)

**Use Case**: Correlation matrices, calendar patterns, 2D data relationships

**Data Format**:
```json
{
  "data": [{
    "x_labels": ["Q1", "Q2", "Q3", "Q4"],
    "y_labels": ["North", "South", "East", "West"],
    "values": [
      [100, 150, 200, 250],
      [120, 160, 210, 260],
      [110, 155, 205, 255],
      [105, 145, 195, 245]
    ]
  }]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/quarterly_comparison \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-006",
    "slide_id": "slide-6",
    "slide_number": 6,
    "narrative": "Show regional performance by quarter",
    "chart_type": "heatmap",
    "data": [{
      "x_labels": ["Q1", "Q2", "Q3", "Q4"],
      "y_labels": ["North", "South", "East", "West"],
      "values": [
        [100, 150, 200, 250],
        [120, 160, 210, 260],
        [110, 155, 205, 255],
        [105, 145, 195, 245]
      ]
    }]
  }'
```

**Note**: `matrix` is an alias for `heatmap` - same data format

---

### 4.3 Boxplot Chart (`boxplot`)

**Use Case**: Statistical distribution, outlier detection, quartile analysis

**Data Format**:
```json
{
  "data": [{
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [{
      "label": "Sales Distribution",
      "data": [
        [100, 250, 350, 450, 600],
        [120, 270, 380, 480, 650],
        [110, 260, 370, 470, 640],
        [130, 280, 390, 490, 660]
      ]
    }]
  }]
}
```

**Format**: Each data point is `[min, q1, median, q3, max]`

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/quarterly_comparison \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-007",
    "slide_id": "slide-7",
    "slide_number": 7,
    "narrative": "Show quarterly sales distribution",
    "chart_type": "boxplot",
    "data": [{
      "labels": ["Q1", "Q2", "Q3", "Q4"],
      "datasets": [{
        "label": "Sales Distribution",
        "data": [
          [100, 250, 350, 450, 600],
          [120, 270, 380, 480, 650],
          [110, 260, 370, 470, 640],
          [130, 280, 390, 490, 660]
        ]
      }]
    }]
  }'
```

---

### 4.4 Candlestick Chart (`candlestick` or `financial`)

**Use Case**: Financial OHLC data, stock prices, forex analysis

**Data Format**:
```json
{
  "data": [{
    "labels": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    "datasets": [{
      "label": "Stock Price",
      "data": [
        {"o": 100, "h": 110, "l": 95, "c": 105},
        {"o": 105, "h": 115, "l": 100, "c": 112},
        {"o": 112, "h": 120, "l": 108, "c": 118},
        {"o": 118, "h": 125, "l": 115, "c": 122}
      ]
    }]
  }]
}
```

**Format**: Each data point is `{o: open, h: high, l: low, c: close}`

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-008",
    "slide_id": "slide-8",
    "slide_number": 8,
    "narrative": "Show stock price movement",
    "chart_type": "candlestick",
    "data": [{
      "labels": ["Day 1", "Day 2", "Day 3", "Day 4"],
      "datasets": [{
        "label": "Stock Price",
        "data": [
          {"o": 100, "h": 110, "l": 95, "c": 105},
          {"o": 105, "h": 115, "l": 100, "c": 112},
          {"o": 112, "h": 120, "l": 108, "c": 118},
          {"o": 118, "h": 125, "l": 115, "c": 122}
        ]
      }]
    }]
  }'
```

**Note**: `financial` is an alias for `candlestick` - same data format

---

### 4.5 Sankey Diagram (`sankey`)

**Use Case**: Flow visualization, resource allocation, user journeys, budget flows

**Data Format**:
```json
{
  "data": [{
    "nodes": [
      {"id": "Traffic"},
      {"id": "Organic"},
      {"id": "Paid"},
      {"id": "Conversions"}
    ],
    "links": [
      {"source": "Traffic", "target": "Organic", "value": 450},
      {"source": "Traffic", "target": "Paid", "value": 320},
      {"source": "Organic", "target": "Conversions", "value": 180},
      {"source": "Paid", "target": "Conversions", "value": 120}
    ]
  }]
}
```

**Example Request**:
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "pres-009",
    "slide_id": "slide-9",
    "slide_number": 9,
    "narrative": "Show traffic flow from sources to conversions",
    "chart_type": "sankey",
    "data": [{
      "nodes": [
        {"id": "Total Traffic"},
        {"id": "Organic"},
        {"id": "Paid"},
        {"id": "Conversions"}
      ],
      "links": [
        {"source": "Total Traffic", "target": "Organic", "value": 450},
        {"source": "Total Traffic", "target": "Paid", "value": 320},
        {"source": "Organic", "target": "Conversions", "value": 180},
        {"source": "Paid", "target": "Conversions", "value": 120}
      ]
    }]
  }'
```

---

## 5. Summary Table

| Chart Type | Category | Data Format | Example |
|------------|----------|-------------|---------|
| `line` | Simple | `[{label, value}]` | Time series, trends |
| `bar_vertical` | Simple | `[{label, value}]` | Categorical comparison |
| `bar_horizontal` | Simple | `[{label, value}]` | Rankings |
| `pie` | Simple | `[{label, value}]` | Proportions |
| `doughnut` | Simple | `[{label, value}]` | Proportions with center cutout |
| `scatter` | Simple | `[{label, value}]` | Distribution |
| `radar` | Simple | `[{label, value}]` | Multivariate data |
| `polar_area` | Simple | `[{label, value}]` | Cyclical data |
| `area` | Simple | `[{label, value}]` | Cumulative trends |
| `bar_grouped` | Multi-Series | `[{labels, datasets}]` | Side-by-side comparison |
| `bar_stacked` | Multi-Series | `[{labels, datasets}]` | Part-to-whole breakdown |
| `area_stacked` | Multi-Series | `[{labels, datasets}]` | Cumulative composition |
| `mixed` | Multi-Series | `[{labels, datasets}]` | Combined chart types |
| `bubble` | Multi-Series | `[{labels, datasets}]` | 3-variable relationships |
| `waterfall` | Special | `[{label, value}]` | Incremental changes |
| `treemap` | Plugin | `[{label, value}]` | Hierarchical data |
| `heatmap` | Plugin | `[{x_labels, y_labels, values}]` | 2D correlation |
| `matrix` | Plugin | `[{x_labels, y_labels, values}]` | Same as heatmap |
| `boxplot` | Plugin | `[{labels, datasets}]` | Statistical distribution |
| `candlestick` | Plugin | `[{labels, datasets}]` | Financial OHLC |
| `financial` | Plugin | `[{labels, datasets}]` | Same as candlestick |
| `sankey` | Plugin | `[{nodes, links}]` | Flow visualization |

---

## 6. Common Patterns

### Pattern 1: Simple Single-Series
**Charts**: line, bar_vertical, bar_horizontal, pie, doughnut, scatter, radar, polar_area, area, waterfall, treemap

```json
{
  "data": [
    {"label": "Category 1", "value": 100},
    {"label": "Category 2", "value": 150},
    {"label": "Category 3", "value": 200}
  ]
}
```

### Pattern 2: Multi-Series with Datasets
**Charts**: bar_grouped, bar_stacked, area_stacked, mixed, bubble, boxplot, candlestick

```json
{
  "data": [{
    "labels": ["Cat 1", "Cat 2", "Cat 3"],
    "datasets": [
      {"label": "Series 1", "data": [100, 150, 200]},
      {"label": "Series 2", "data": [120, 160, 210]}
    ]
  }]
}
```

### Pattern 3: Matrix/Grid Data
**Charts**: heatmap, matrix

```json
{
  "data": [{
    "x_labels": ["Col 1", "Col 2", "Col 3"],
    "y_labels": ["Row 1", "Row 2", "Row 3"],
    "values": [
      [10, 20, 30],
      [15, 25, 35],
      [12, 22, 32]
    ]
  }]
}
```

### Pattern 4: Flow Data
**Charts**: sankey

```json
{
  "data": [{
    "nodes": [{"id": "A"}, {"id": "B"}],
    "links": [{"source": "A", "target": "B", "value": 100}]
  }]
}
```

---

## 7. Validation Rules

### All Chart Types
- ✅ Minimum: 1 data point (some charts require more - see specifics)
- ✅ Maximum: 50 data points
- ✅ Labels: Non-empty strings (max 100 characters)
- ✅ Values: Finite numbers (no NaN, no Infinity)

### Simple Format
- ✅ Each point must have `label` and `value`
- ✅ Labels should be unique (recommended)

### Multi-Series Format
- ✅ Must have `labels` array
- ✅ Must have `datasets` array with at least one dataset
- ✅ Each dataset must have `label` and `data` array
- ✅ All datasets must have same number of data points as labels array

### Heatmap/Matrix Format
- ✅ Must have `x_labels`, `y_labels`, and `values`
- ✅ `values` must be 2D array matching dimensions
- ✅ `values[i].length` must equal `x_labels.length` for all rows

### Boxplot Format
- ✅ Each data point must be array of 5 numbers: `[min, q1, median, q3, max]`
- ✅ Must satisfy: `min ≤ q1 ≤ median ≤ q3 ≤ max`

### Candlestick Format
- ✅ Each data point must have `o`, `h`, `l`, `c` properties
- ✅ Must satisfy: `l ≤ o, c ≤ h`

### Sankey Format
- ✅ Must have `nodes` and `links` arrays
- ✅ Each node must have unique `id`
- ✅ Each link must reference existing node IDs in `source` and `target`
- ✅ Link `value` must be positive number

---

## 8. Testing Your Data Format

Use the test script to validate your data format:

```python
import requests

def test_chart_data(chart_type, data):
    """Test if data format is correct for chart type."""
    response = requests.post(
        f"https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
        json={
            "presentation_id": "test-format",
            "slide_id": "test-slide",
            "slide_number": 1,
            "narrative": f"Test {chart_type} data format",
            "chart_type": chart_type,
            "data": data
        },
        timeout=30
    )

    if response.status_code == 200:
        print(f"✅ {chart_type}: Data format valid")
        return True
    else:
        print(f"❌ {chart_type}: {response.json()}")
        return False

# Test simple format
test_chart_data("line", [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 150}
])

# Test multi-series format
test_chart_data("bar_grouped", [{
    "labels": ["Q1", "Q2"],
    "datasets": [
        {"label": "2023", "data": [100, 120]},
        {"label": "2024", "data": [150, 180]}
    ]
}])

# Test heatmap format
test_chart_data("heatmap", [{
    "x_labels": ["Q1", "Q2"],
    "y_labels": ["North", "South"],
    "values": [[100, 150], [120, 160]]
}])
```

---

## 9. Common Errors and Solutions

### Error: "Field required: label"
**Cause**: Using complex format for simple chart type
**Solution**: Use `[{label, value}]` format for simple charts

### Error: "Field required: datasets"
**Cause**: Using simple format for multi-series chart
**Solution**: Wrap data in `[{labels, datasets}]` structure

### Error: "Field required: x_labels"
**Cause**: Missing heatmap structure
**Solution**: Provide `{x_labels, y_labels, values}` for heatmap/matrix

### Error: "Boxplot data must be array of 5 numbers"
**Cause**: Incorrect boxplot data format
**Solution**: Use `[min, q1, median, q3, max]` for each data point

### Error: "Candlestick data must have o, h, l, c properties"
**Cause**: Missing OHLC properties
**Solution**: Provide `{o, h, l, c}` for each candlestick

---

**Last Updated**: November 19, 2025
**Version**: 3.4.3
**Status**: Complete - All 22 chart types documented
