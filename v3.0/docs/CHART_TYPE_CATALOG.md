# Chart Type Catalog - Analytics Service v3

**Version**: 3.6.0
**Date**: November 25, 2025
**Total Chart Types**: 17
**Chart Libraries**: Chart.js (9 types), D3.js (3 types), ApexCharts (4 types), Chart.js Plugins (1 type)

---

## 📊 Overview

Analytics Service v3 supports 17 chart types across three rendering libraries:

- **Chart.js** (9 types) - Used for L02 layout (Director integration)
- **D3.js** (3 types) - SVG-based advanced visualizations for L02 layout (treemap, sunburst, choropleth)
- **Chart.js Plugins** (1 type) - Plugin-based charts (waterfall) for L02 layout
- **ApexCharts** (4 types) - Used for L01 and L03 layouts (legacy)

---

## 🎨 Chart.js Types (L02 Layout)

### 1. Line Chart

**ID**: `line`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Displays trends and changes over time with connected data points. Ideal for showing continuous data progression.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 50
- **Optimal range**: 3-20 points

#### Use Cases
- Revenue trends over time
- Performance metrics tracking
- Growth trajectories
- Time series analysis
- KPI monitoring

#### Examples
- Quarterly revenue growth
- Monthly active users
- Year-over-year sales comparison
- Website traffic trends

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Time periods (Q1 2024, Jan, Week 1, etc.)",
  "value_format": "Numeric (revenue, count, percentage, etc.)"
}
```

#### Visual Properties
- **Animations**: Smooth line drawing from left to right
- **Colors**: Professional gradient color scheme
- **Interactivity**: Hover for exact values
- **Line style**: Smooth curves with tension

#### Interactive Features
- ✅ Edit chart data (modal editor)
- ✅ Hover tooltips
- ✅ Zoom/pan

#### When to Use
- ✅ Time-based data
- ✅ Continuous trends
- ✅ Multiple data series comparison
- ✅ Pattern identification

#### When NOT to Use
- ❌ Categorical comparisons (use bar chart)
- ❌ Part-to-whole relationships (use pie chart)
- ❌ Too many data points (>50 becomes cluttered)

---

### 2. Vertical Bar Chart

**ID**: `bar_vertical`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Compares values across categories with vertical bars. Best for comparing discrete categories.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 30
- **Optimal range**: 3-12 bars

#### Use Cases
- Category comparisons
- Quarterly performance
- Product sales comparison
- Regional analysis
- Department metrics

#### Examples
- Sales by product category
- Revenue by region
- Performance by department
- Market share by competitor

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Numeric values"
}
```

#### Visual Properties
- **Animations**: Bars grow from bottom to top
- **Colors**: Gradient fills with professional palette
- **Interactivity**: Hover for exact values
- **Bar width**: Auto-calculated for optimal spacing

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover tooltips
- ✅ Stacking support (via configuration)

#### When to Use
- ✅ Comparing categories
- ✅ Discrete data points
- ✅ Ranking visualization
- ✅ Before/after comparisons

#### When NOT to Use
- ❌ Too many categories (>12 bars)
- ❌ Long category names (use horizontal bar)
- ❌ Continuous time series (use line chart)

---

### 3. Horizontal Bar Chart

**ID**: `bar_horizontal`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Compares values with horizontal bars. Better for long category names or ranking visualization.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 25
- **Optimal range**: 3-10 bars

#### Use Cases
- Ranking comparisons
- Long category names
- Top performers
- Survey responses
- Priority lists

#### Examples
- Top 10 customers by revenue
- Employee satisfaction scores
- Feature prioritization
- Product comparison ratings

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names (can be long)",
  "value_format": "Numeric values"
}
```

#### Visual Properties
- **Animations**: Bars grow from left to right
- **Colors**: Gradient fills
- **Orientation**: Horizontal for better label readability
- **Label position**: Left side with full text visible

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover tooltips

#### When to Use
- ✅ Long category names
- ✅ Ranking visualization
- ✅ Top N analysis
- ✅ Survey results

#### When NOT to Use
- ❌ Short category names (use vertical bar)
- ❌ Too many categories (>10)

---

### 4. Pie Chart

**ID**: `pie`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Shows part-to-whole relationships as circular slices. Each slice represents a proportion of the total.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 8
- **Optimal range**: 3-6 slices

#### Use Cases
- Market share distribution
- Budget allocation
- Revenue breakdown
- Category proportions
- Resource allocation

#### Examples
- Market share by competitor
- Budget by department
- Revenue by product line
- Customer segments

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Positive numeric values",
  "constraint": "Values should sum to meaningful total (100%, revenue, etc.)"
}
```

#### Visual Properties
- **Animations**: Slices expand from center
- **Colors**: Distinct colors per slice
- **Labels**: Percentage and value labels
- **Legend**: Auto-positioned for readability

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover for percentages
- ✅ Slice highlighting

#### When to Use
- ✅ Part-to-whole relationships
- ✅ Percentage distributions
- ✅ Simple proportions
- ✅ Few categories (3-6)

#### When NOT to Use
- ❌ Too many slices (>8)
- ❌ Comparing exact values (use bar chart)
- ❌ Time-based trends (use line chart)

---

### 5. Doughnut Chart

**ID**: `doughnut`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Like pie chart but with hollow center. Provides modern aesthetic and optional center label area.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 8
- **Optimal range**: 3-6 slices

#### Use Cases
- Market composition
- Portfolio allocation
- Expense categories
- User demographics
- Product mix

#### Examples
- Investment portfolio breakdown
- Expense categories
- User demographics by age group
- Traffic sources

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Positive numeric values"
}
```

#### Visual Properties
- **Animations**: Slices expand from center
- **Colors**: Professional gradient palette
- **Center**: Hollow for modern aesthetic
- **Cutout**: 50% (configurable)

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover for percentages
- ✅ Center label (optional)

#### When to Use
- ✅ Modern design preference
- ✅ Part-to-whole relationships
- ✅ Need center label area
- ✅ Professional presentations

#### When NOT to Use
- ❌ Same as pie chart limitations

---

### 6. Scatter Plot

**ID**: `scatter`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Shows relationship between two variables as points on X-Y axes. Reveals patterns, correlations, and outliers.

#### Data Constraints
- **Minimum data points**: 5
- **Maximum data points**: 100
- **Optimal range**: 10-50 points

#### Use Cases
- Correlation analysis
- Pattern detection
- Outlier identification
- Distribution visualization
- Regression analysis

#### Examples
- Price vs. demand correlation
- Age vs. income relationship
- Marketing spend vs. revenue
- Temperature vs. sales

#### Data Requirements
```json
{
  "fields": ["x", "y"],
  "label_format": "Point identifiers (optional)",
  "value_format": "Two numeric values per point"
}
```

#### Visual Properties
- **Animations**: Points appear with fade-in
- **Colors**: Single color with transparency
- **Size**: Uniform or variable point sizes
- **Grid**: Background grid for reference

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover for coordinates
- ✅ Quadrant highlighting

#### When to Use
- ✅ Relationship analysis
- ✅ Correlation studies
- ✅ Outlier detection
- ✅ Pattern identification

#### When NOT to Use
- ❌ Categorical data (use bar chart)
- ❌ Time series (use line chart)
- ❌ Too few points (<5)

---

### 7. Bubble Chart

**ID**: `bubble`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Scatter plot with third dimension shown as bubble size. Visualizes three variables simultaneously.

#### Data Constraints
- **Minimum data points**: 3
- **Maximum data points**: 50
- **Optimal range**: 5-20 bubbles

#### Use Cases
- Three-dimensional comparisons
- Portfolio analysis
- Risk vs. return visualization
- Multi-variable analysis
- Market positioning

#### Examples
- Revenue (x) vs. Profit (y) vs. Market share (size)
- Risk (x) vs. Return (y) vs. Investment size (size)
- Age (x) vs. Salary (y) vs. Experience (size)

#### Data Requirements
```json
{
  "fields": ["x", "y", "r"],
  "label_format": "Data point names",
  "value_format": "Three numeric values (x, y, radius)"
}
```

#### Visual Properties
- **Animations**: Bubbles expand from center
- **Colors**: Color-coded by category or gradient
- **Size**: Variable bubble sizes for third dimension
- **Scaling**: Auto-scaled for optimal visibility

#### Interactive Features
- ✅ Edit chart data (all three dimensions)
- ✅ Hover for all three values
- ✅ Size normalization

#### When to Use
- ✅ Three-variable analysis
- ✅ Portfolio comparisons
- ✅ Multi-dimensional data
- ✅ Complex relationships

#### When NOT to Use
- ❌ Two variables only (use scatter)
- ❌ Too many bubbles (>20)
- ❌ Simple comparisons (use bar chart)

---

### 8. Radar Chart

**ID**: `radar`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Multi-axis chart showing multiple variables from center point. Creates polygon shape representing profile.

#### Data Constraints
- **Minimum data points**: 3
- **Maximum data points**: 12
- **Optimal range**: 4-8 axes

#### Use Cases
- Skill assessments
- Product comparisons
- Performance reviews
- Multi-criteria evaluation
- Competitive analysis

#### Examples
- Employee skills (leadership, technical, communication, etc.)
- Product features comparison
- Company performance metrics
- Team capability assessment

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Metric/dimension names",
  "value_format": "Normalized values (0-100 or 0-10)"
}
```

#### Visual Properties
- **Animations**: Web expands from center
- **Colors**: Filled area with semi-transparency
- **Shape**: Multi-sided polygon
- **Grid**: Circular grid lines

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover for values
- ✅ Multiple datasets overlay

#### When to Use
- ✅ Multi-dimensional profiles
- ✅ Balanced scorecard
- ✅ Skills assessment
- ✅ Competitive comparison

#### When NOT to Use
- ❌ Too few dimensions (<3)
- ❌ Too many dimensions (>12)
- ❌ Categorical data (use bar chart)

---

### 9. Polar Area Chart

**ID**: `polar_area`
**Library**: Chart.js
**Supported Layouts**: L02

#### Description
Like pie chart but shows values as radius from center. Combines angular and radial dimensions.

#### Data Constraints
- **Minimum data points**: 3
- **Maximum data points**: 12
- **Optimal range**: 4-8 segments

#### Use Cases
- Cyclical data visualization
- Multi-category comparison with magnitude
- Performance across dimensions
- Resource allocation with priority

#### Examples
- Seasonal sales patterns
- Weekly activity levels
- Department performance scores
- Time-of-day analysis

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Positive numeric values"
}
```

#### Visual Properties
- **Animations**: Segments expand from center
- **Colors**: Distinct colors per segment
- **Size**: Radius represents value magnitude
- **Grid**: Circular grid for scale reference

#### Interactive Features
- ✅ Edit chart data
- ✅ Hover for values
- ✅ Segment highlighting

#### When to Use
- ✅ Cyclical patterns
- ✅ Magnitude comparison
- ✅ Angular + radial data
- ✅ Time-of-day/week analysis

#### When NOT to Use
- ❌ Simple proportions (use pie)
- ❌ Time series (use line)
- ❌ Too many segments (>12)

---

## 🔷 D3.js Types (L02 Layout)

### 10. D3 Treemap

**ID**: `d3_treemap`
**Library**: D3.js v7
**Supported Layouts**: L02

#### Description
SVG-based hierarchical treemap visualization using D3.js. Displays proportional data as nested rectangles with hover effects and smooth rendering. Ideal for budget allocation, market share, and hierarchical breakdowns.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 50
- **Optimal range**: 4-15 rectangles

#### Use Cases
- Budget allocation by department
- Market share distribution
- Resource allocation visualization
- Portfolio composition
- Hierarchical data breakdowns

#### Examples
- Department budget allocation
- Revenue by product category
- Storage usage by folder
- Investment portfolio breakdown

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Positive numeric values",
  "note": "Automatically converted to D3 hierarchical format"
}
```

#### Visual Properties
- **Rendering**: SVG-based (not Canvas)
- **Animations**: None (immediate render)
- **Colors**: Vibrant 8-color palette with 0.85 opacity
- **Hover**: Opacity changes to 1.0 on hover
- **Labels**: White text with category name and value
- **Size**: Area proportional to value

#### Interactive Features
- ✅ Hover effects (opacity highlight)
- ✅ Reveal.js slide integration
- ⏳ Edit chart data (deferred for POC)

#### When to Use
- ✅ Part-to-whole relationships with many categories
- ✅ Budget or resource allocation
- ✅ Hierarchical data visualization
- ✅ When SVG output is preferred over Canvas

#### When NOT to Use
- ❌ Time series data (use line chart)
- ❌ Comparing exact values (use bar chart)
- ❌ Need advanced interactivity (use Chart.js types)

#### API Example
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test",
    "slide_id": "s1",
    "slide_number": 1,
    "narrative": "Show budget allocation",
    "chart_type": "d3_treemap",
    "data": [
      {"label": "Engineering", "value": 450000},
      {"label": "Sales", "value": 320000},
      {"label": "Marketing", "value": 180000}
    ]
  }'
```

---

### 11. D3 Sunburst

**ID**: `d3_sunburst`
**Library**: D3.js v7
**Supported Layouts**: L02

#### Description
SVG-based radial hierarchical visualization using D3.js partition layout. Displays hierarchical data as concentric circles with inner-to-outer levels, ideal for multi-level budget breakdowns, organizational structures, and nested data relationships.

#### Data Constraints
- **Minimum data points**: 2
- **Maximum data points**: 50
- **Optimal range**: 4-12 segments
- **Note**: Currently supports single-level hierarchy (root → children)

#### Use Cases
- Multi-level budget allocation (department → teams → projects)
- Organizational structure visualization (company → divisions → teams)
- File system usage with nested folders
- Market segmentation breakdown (region → product → category)
- Resource distribution across hierarchies

#### Examples
- FY2025 budget by department and subdepartment
- Company organizational chart
- Storage usage: folders → subfolders → files
- Sales breakdown: region → territory → account

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "Category names",
  "value_format": "Positive numeric values",
  "note": "Automatically converted to D3 hierarchical partition format"
}
```

#### Visual Properties
- **Rendering**: SVG-based radial partition layout (not Canvas)
- **Animations**: None (immediate render)
- **Colors**: Vibrant 8-color palette with 0.85 opacity
- **Hover**: Opacity changes to 1.0 on hover
- **Labels**: White text rotated to follow arc angle (only for arcs > 0.1 radians)
- **Size**: Arc angle proportional to value, concentric rings for hierarchy levels
- **Layout**: Centered circular/radial with equal radius increments per level

#### Interactive Features
- ✅ Hover effects (opacity highlight)
- ✅ Reveal.js slide integration
- ✅ Chart instance management
- ⏳ Edit chart data (deferred for POC)
- ⏳ Drill-down interactivity (future enhancement)

#### When to Use
- ✅ Hierarchical data with parent-child relationships
- ✅ Multi-level budget or resource allocation
- ✅ Organizational structure visualization
- ✅ Nested categorical data
- ✅ When radial/circular layout enhances understanding

#### When NOT to Use
- ❌ Time series data (use line chart)
- ❌ Simple part-to-whole comparison (use pie or treemap)
- ❌ Data with more than 3 hierarchy levels (needs drill-down)
- ❌ Need precise value comparison (use bar chart)

#### API Example
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test",
    "slide_id": "s1",
    "slide_number": 1,
    "narrative": "Show budget hierarchy",
    "chart_type": "d3_sunburst",
    "data": [
      {"label": "Engineering", "value": 800000},
      {"label": "Sales", "value": 600000},
      {"label": "Marketing", "value": 400000},
      {"label": "Operations", "value": 350000}
    ]
  }'
```

---

### 12. D3 Choropleth USA Map

**ID**: `d3_choropleth_usa`
**Library**: D3.js v7
**Supported Layouts**: L02

#### Description
SVG-based geographic choropleth (color-coded) map visualization using D3.js and TopoJSON. Displays data distribution across US states with interactive tooltips and gradient legend. Ideal for regional sales analysis, market penetration, state-by-state performance metrics, and geographic data visualization.

#### Data Constraints
- **Minimum data points**: 1
- **Maximum data points**: 50 (all US states)
- **Optimal range**: 5-20 states
- **Note**: Supports both state abbreviations ("CA", "TX") and full names ("California", "Texas")

#### Use Cases
- Regional sales performance by state
- Market penetration analysis across USA
- State-by-state metrics comparison
- Geographic revenue distribution
- Customer density mapping
- Store/office location performance

#### Examples
- Q4 sales performance across top 10 states
- Market share by state
- Revenue per state in FY2025
- Customer acquisition by region

#### Data Requirements
```json
{
  "fields": ["label", "value"],
  "label_format": "State names (abbreviations or full names: 'CA' or 'California')",
  "value_format": "Numeric values (sales, revenue, counts, percentages, etc.)",
  "note": "State names automatically normalized to match TopoJSON boundaries"
}
```

#### Visual Properties
- **Rendering**: SVG-based geographic projection (not Canvas)
- **Projection**: d3.geoAlbersUsa() for accurate USA map representation
- **Animations**: None (immediate render for clarity)
- **Colors**: Quantize color scale with 5-color gradient (light to dark)
- **Hover**: Interactive tooltips showing state name and exact value
- **Legend**: Vertical gradient legend with min/max values and color scale
- **Data Source**: TopoJSON from us-atlas@3 CDN (US state boundaries)
- **Tooltip**: Positioned dynamically near cursor with state data

#### Interactive Features
- ✅ Hover effects (state highlighting + tooltip)
- ✅ Color-coded value ranges (quantize scale)
- ✅ Gradient legend with value ranges
- ✅ Reveal.js slide integration
- ✅ Chart instance management
- ✅ State name normalization (handles abbreviations and full names)
- ⏳ Edit chart data (editor not yet implemented for D3 charts)
- ⏳ Drill-down to state details (future enhancement)

#### When to Use
- ✅ Geographic data visualization for USA
- ✅ State-by-state performance comparison
- ✅ Regional trends and patterns
- ✅ Market penetration analysis
- ✅ Location-based metrics (stores, customers, sales)
- ✅ When geographic context enhances understanding

#### When NOT to Use
- ❌ Non-geographic data (use bar or treemap chart)
- ❌ Time series data (use line chart)
- ❌ International data outside USA (needs different map)
- ❌ Need precise value comparison (use bar chart)
- ❌ Data with fewer than 3 states (insufficient for geographic visualization)

#### API Example
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test-choropleth-001",
    "slide_id": "slide-choropleth-1",
    "slide_number": 1,
    "narrative": "Show regional sales performance across USA",
    "chart_type": "d3_choropleth_usa",
    "data": [
      {"label": "CA", "value": 850000},
      {"label": "TX", "value": 720000},
      {"label": "NY", "value": 690000},
      {"label": "FL", "value": 580000},
      {"label": "IL", "value": 450000},
      {"label": "PA", "value": 420000},
      {"label": "OH", "value": 380000},
      {"label": "GA", "value": 360000},
      {"label": "NC", "value": 340000},
      {"label": "MI", "value": 320000}
    ],
    "context": {
      "theme": "professional",
      "slide_title": "Regional Sales Performance",
      "subtitle": "Top 10 States - FY 2024"
    }
  }'
```

---

## 📈 ApexCharts Types (L01, L03 Layouts)

### 11. Area Chart

**ID**: `area`
**Library**: ApexCharts
**Supported Layouts**: L01, L03

#### Description
Line chart with filled area below the line. Emphasizes volume and cumulative trends.

#### Data Constraints
- **Minimum data points**: 3
- **Maximum data points**: 50
- **Optimal range**: 5-30 points

#### Use Cases
- Cumulative trends
- Volume over time
- Stacked comparisons
- Total accumulation

#### Examples
- Total revenue accumulation
- Traffic volume over time
- Cumulative sales

#### Visual Properties
- **Animations**: Area fills from left to right
- **Colors**: Gradient fills
- **Interactivity**: ApexCharts native interactions

#### Interactive Features
- ✅ Zoom
- ✅ Pan
- ✅ Export to PNG/SVG

---

### 12. Heatmap

**ID**: `heatmap`
**Library**: ApexCharts
**Supported Layouts**: L01

#### Description
Matrix visualization with color-coded cells. Shows patterns in two-dimensional data.

#### Data Constraints
- **Minimum data points**: 9 (3×3 grid)
- **Maximum data points**: 500
- **Optimal range**: 20-100 cells

#### Use Cases
- Correlation matrices
- Activity patterns
- Density visualization
- Time-based patterns

#### Examples
- Website traffic by hour and day
- Sales by product and region
- User activity heatmap

#### Visual Properties
- **Animations**: Cell colors fade in
- **Colors**: Color gradient from low to high
- **Density**: Color intensity shows value magnitude

#### Interactive Features
- ✅ Hover for exact values
- ✅ Color scale legend

---

### 13. Treemap (ApexCharts)

**ID**: `treemap`
**Library**: ApexCharts
**Supported Layouts**: L01

#### Description
Hierarchical data as nested rectangles. Size represents value magnitude.

#### Data Constraints
- **Minimum data points**: 4
- **Maximum data points**: 50
- **Optimal range**: 8-25 rectangles

#### Use Cases
- Hierarchical breakdowns
- Portfolio composition
- File system visualization
- Budget allocation

#### Examples
- Revenue by division and department
- Storage usage by folder
- Product category breakdown

#### Visual Properties
- **Animations**: Rectangles expand
- **Colors**: Color-coded by category
- **Size**: Area proportional to value

#### Interactive Features
- ✅ Drill-down
- ✅ Hover for details
- ✅ Color gradients

---

### 14. Waterfall Chart

**ID**: `waterfall`
**Library**: ApexCharts
**Supported Layouts**: L01

#### Description
Shows cumulative effect of sequential positive/negative values. Visualizes step-by-step changes.

#### Data Constraints
- **Minimum data points**: 3
- **Maximum data points**: 20
- **Optimal range**: 4-12 steps

#### Use Cases
- Financial reconciliation
- Profit/loss breakdown
- Bridge analysis
- Variance explanation

#### Examples
- Income statement waterfall
- Budget to actual variance
- Starting to ending cash flow

#### Visual Properties
- **Animations**: Bars cascade from left to right
- **Colors**: Green for positive, red for negative
- **Connectors**: Lines show cumulative flow

#### Interactive Features
- ✅ Hover for running totals
- ✅ Intermediate total indicators

---

## 🎯 Chart Selection Guide

### By Data Type

| Data Type | Recommended Charts |
|-----------|-------------------|
| Time series | Line, Area |
| Categories | Bar (Vertical/Horizontal) |
| Proportions | Pie, Doughnut |
| Correlation | Scatter, Bubble |
| Multi-dimensional | Radar, Polar Area |
| Hierarchical | D3 Treemap, D3 Sunburst, Treemap |
| Sequential changes | Waterfall |
| Density/patterns | Heatmap |
| Geographic | D3 Choropleth USA |

### By Number of Data Points

| Data Points | Recommended Charts |
|-------------|-------------------|
| 2-5 | Pie, Doughnut, Bar |
| 5-15 | Line, Bar, Radar |
| 15-30 | Line, Area, Scatter |
| 30-50 | Scatter, Bubble, Heatmap |

### By Layout

| Layout | Library | Chart Types | Count |
|--------|---------|-------------|-------|
| L02 | Chart.js | line, bar_vertical, bar_horizontal, pie, doughnut, scatter, bubble, radar, polar_area | 9 |
| L02 | D3.js | d3_treemap, d3_sunburst, d3_choropleth_usa | 3 |
| L01 | ApexCharts | area, heatmap, treemap, waterfall | 4 |
| L03 | ApexCharts | area, heatmap, treemap, waterfall | 4 |

---

## 🔍 Discovering Chart Types via API

### Get All Chart Types

```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types
```

### Get Chart.js Types (L02)

```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types/chartjs
```

### Get Specific Chart Type

```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types/line
```

### Get Charts for Layout

```bash
curl https://analytics-v30-production.up.railway.app/api/v1/layouts/L02/chart-types
```

---

## 📊 Quick Reference Matrix

| Chart Type | Min Points | Max Points | Optimal | Layouts | Library |
|-----------|-----------|-----------|---------|---------|---------|
| line | 2 | 50 | 3-20 | L02 | Chart.js |
| bar_vertical | 2 | 30 | 3-12 | L02 | Chart.js |
| bar_horizontal | 2 | 25 | 3-10 | L02 | Chart.js |
| pie | 2 | 8 | 3-6 | L02 | Chart.js |
| doughnut | 2 | 8 | 3-6 | L02 | Chart.js |
| scatter | 5 | 100 | 10-50 | L02 | Chart.js |
| bubble | 3 | 50 | 5-20 | L02 | Chart.js |
| radar | 3 | 12 | 4-8 | L02 | Chart.js |
| polar_area | 3 | 12 | 4-8 | L02 | Chart.js |
| **d3_treemap** | 2 | 50 | 4-15 | L02 | **D3.js** |
| **d3_sunburst** | 2 | 50 | 4-12 | L02 | **D3.js** |
| **d3_choropleth_usa** | 1 | 50 | 5-20 | L02 | **D3.js** |
| area | 3 | 50 | 5-30 | L01, L03 | ApexCharts |
| heatmap | 9 | 500 | 20-100 | L01 | ApexCharts |
| treemap | 4 | 50 | 8-25 | L01 | ApexCharts |
| waterfall | 3 | 20 | 4-12 | L01 | ApexCharts |

---

## 📝 Notes

- **Chart.js charts** (L02) include interactive editing features
- **D3.js charts** (L02) use SVG rendering for advanced visualizations
- **ApexCharts charts** (L01, L03) are for legacy layouts
- All charts enforce data point constraints via validation
- Optimal ranges provide best visual clarity and performance

---

**Last Updated**: November 25, 2025
**Version**: 3.6.0
**Related Documentation**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md), [ERROR_CODES.md](./ERROR_CODES.md), [DATA_FORMATS_REFERENCE.md](../DATA_FORMATS_REFERENCE.md)
