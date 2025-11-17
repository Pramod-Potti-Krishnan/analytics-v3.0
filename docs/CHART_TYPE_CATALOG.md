# Chart Type Catalog - Analytics Service v3

**Version**: 3.1.2
**Date**: November 16, 2025
**Total Chart Types**: 13
**Chart Libraries**: Chart.js (9 types), ApexCharts (4 types)

---

## 📊 Overview

Analytics Service v3 supports 13 chart types across two rendering libraries:

- **Chart.js** (9 types) - Used for L02 layout (Director integration)
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

## 📈 ApexCharts Types (L01, L03 Layouts)

### 10. Area Chart

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

### 11. Heatmap

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

### 12. Treemap

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

### 13. Waterfall Chart

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
| Hierarchical | Treemap |
| Sequential changes | Waterfall |
| Density/patterns | Heatmap |

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
| area | 3 | 50 | 5-30 | L01, L03 | ApexCharts |
| heatmap | 9 | 500 | 20-100 | L01 | ApexCharts |
| treemap | 4 | 50 | 8-25 | L01 | ApexCharts |
| waterfall | 3 | 20 | 4-12 | L01 | ApexCharts |

---

## 📝 Notes

- **Chart.js charts** (L02) include interactive editing features
- **ApexCharts charts** (L01, L03) are for legacy layouts
- All charts enforce data point constraints via validation
- Optimal ranges provide best visual clarity and performance

---

**Last Updated**: November 16, 2025
**Version**: 3.1.2
**Related Documentation**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md), [ERROR_CODES.md](./ERROR_CODES.md)
