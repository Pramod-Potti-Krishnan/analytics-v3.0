# Analytics Microservice v3 - Complete Styling & Configuration Guide

**Version**: 3.8.0
**Last Updated**: 2025-11-30
**Status**: Production Ready

## Table of Contents

1. [Chart.js Configuration Overview](#chartjs-configuration-overview)
2. [Complete Color Palettes](#complete-color-palettes)
3. [Font Configurations](#font-configurations)
4. [All 9 Chart Types & Styling](#all-9-chart-types--styling)
5. [Chart.js Plugins & Options](#chartjs-plugins--options)
6. [Observations Panel Styling](#observations-panel-styling)
7. [Layout Templates (L01, L02, L03)](#layout-templates-l01-l02-l03)
8. [Text Formatting & Character Limits](#text-formatting--character-limits)
9. [Integration Points for Theme Injection](#integration-points-for-theme-injection)
10. [Default Styling Parameters](#default-styling-parameters)

---

## Chart.js Configuration Overview

**Library**: Chart.js 4.4.0 (via CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0`)
**Data Labels Plugin**: chartjs-plugin-datalabels (for labels on charts)
**Container Class**: `l02-chart-container`
**Initialization**: Inline script with IIFE wrapper and Reveal.js integration

---

## Complete Color Palettes

### Three Theme Options in ChartJSGenerator

#### Theme 1: Professional (Default)
```python
"professional": {
    "primary": "#FF6B6B",      # Coral Red
    "secondary": "#4ECDC4",    # Turquoise
    "tertiary": "#FFE66D",     # Yellow
    "quaternary": "#95E1D3",   # Mint Green
    "quinary": "#F38181",      # Light Red
    "senary": "#AA96DA",       # Purple
    "septenary": "#FCBAD3",    # Pink
    "octonary": "#A8D8EA",     # Light Blue
    "palette": [
        "#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3",
        "#F38181", "#AA96DA", "#FCBAD3", "#A8D8EA"
    ],
    "gradients": {
        "red": ["rgba(255, 107, 107, 0.8)", "rgba(255, 107, 107, 0.2)"],
        "turquoise": ["rgba(78, 205, 196, 0.8)", "rgba(78, 205, 196, 0.2)"],
        "yellow": ["rgba(255, 230, 109, 0.8)", "rgba(255, 230, 109, 0.2)"],
        "mint": ["rgba(149, 225, 211, 0.8)", "rgba(149, 225, 211, 0.2)"],
        "purple": ["rgba(170, 150, 218, 0.8)", "rgba(170, 150, 218, 0.2)"]
    }
}
```

#### Theme 2: Corporate
```python
"corporate": {
    "primary": "#003f5c",       # Dark Blue
    "secondary": "#2f4b7c",     # Blue
    "tertiary": "#665191",      # Purple
    "quaternary": "#a05195",    # Magenta
    "quinary": "#d45087",       # Pink
    "senary": "#f95d6a",        # Light Red
    "septenary": "#ff7c43",     # Orange
    "octonary": "#ffa600",      # Gold
    "palette": [
        "#003f5c", "#2f4b7c", "#665191", "#a05195",
        "#d45087", "#f95d6a", "#ff7c43", "#ffa600"
    ],
    "gradients": {
        "blue": ["rgba(0, 63, 92, 0.8)", "rgba(0, 63, 92, 0.2)"],
        "purple": ["rgba(102, 81, 145, 0.8)", "rgba(102, 81, 145, 0.2)"],
        "pink": ["rgba(212, 80, 135, 0.8)", "rgba(212, 80, 135, 0.2)"],
        "orange": ["rgba(255, 166, 0, 0.8)", "rgba(255, 166, 0, 0.2)"]
    }
}
```

#### Theme 3: Vibrant
```python
"vibrant": {
    "primary": "#FF5733",       # Red-Orange
    "secondary": "#33FF57",     # Lime Green
    "tertiary": "#3357FF",      # Blue
    "quaternary": "#F033FF",    # Magenta
    "quinary": "#FF33F0",       # Magenta-Pink
    "senary": "#33FFF0",        # Cyan
    "septenary": "#F0FF33",     # Yellow-Lime
    "octonary": "#5733FF",      # Blue-Purple
    "palette": [
        "#FF5733", "#33FF57", "#3357FF", "#F033FF",
        "#FF33F0", "#33FFF0", "#F0FF33", "#5733FF"
    ],
    "gradients": {
        "red": ["rgba(255, 87, 51, 0.8)", "rgba(255, 87, 51, 0.2)"],
        "green": ["rgba(51, 255, 87, 0.8)", "rgba(51, 255, 87, 0.2)"],
        "blue": ["rgba(51, 87, 255, 0.8)", "rgba(51, 87, 255, 0.2)"],
        "purple": ["rgba(240, 51, 255, 0.8)", "rgba(240, 51, 255, 0.2)"]
    }
}
```

### L02 Layout Theme Colors (Layout Assembler)
```python
"professional": {
    "bg": "#f8f9fa",            # Background: Light Gray
    "heading": "#1f2937",       # Heading: Dark Gray
    "text": "#374151",          # Text: Gray
    "border": "#e2e8f0"         # Border: Light Gray
},
"corporate": {
    "bg": "#f3f4f6",
    "heading": "#111827",
    "text": "#4b5563",
    "border": "#d1d5db"
},
"vibrant": {
    "bg": "#fef3c7",            # Golden Yellow
    "heading": "#78350f",       # Dark Brown
    "text": "#92400e",          # Brown
    "border": "#fde68a"         # Light Yellow
}
```

---

## Font Configurations

### Chart Legend Fonts
```json
{
    "display": true,
    "position": "top",
    "labels": {
        "font": {"size": 14, "weight": "bold"},
        "padding": 15,
        "usePointStyle": true
    }
}
```

### Chart Data Labels (On Chart)
```json
{
    "display": true,
    "color": "#fff",
    "font": {"size": 14, "weight": "bold"},
    "backgroundColor": "rgba(0, 0, 0, 0.7)",
    "borderRadius": 4,
    "padding": 6
}
```

### Axis Ticks & Labels
```json
{
    "display": true,
    "font": {"size": 12, "weight": "500"},
    "color": "#333",
    "padding": 8,
    "autoSkip": false,
    "maxRotation": 45,
    "minRotation": 0
}
```

### Axis Titles
```json
{
    "display": true,
    "font": {"size": 13, "weight": "bold"},
    "color": "#333"
}
```

### Observations Panel Heading (L02)
- **Font Family**: 'Inter', -apple-system, sans-serif
- **Font Size**: 22px
- **Font Weight**: 600 (semi-bold)
- **Line Height**: 1.3
- **Color**: Theme heading color (#1f2937 for professional)

### Observations Panel Bullets (L02)
- **Font Family**: 'Inter', -apple-system, sans-serif
- **Font Size**: 19px
- **Font Weight**: Regular (400)
- **Line Height**: 1.65
- **Color**: Theme text color (#374151 for professional)
- **Margin**: 0 0 10px 0 (10px spacing between bullets)

---

## All 9 Chart Types & Styling

### 1. Line Chart
**Method**: `generate_line_chart()`
**Use Case**: Time series, trends over time
**Styling**:
- Border Color: `self.colors["primary"]` (Coral Red for professional)
- Border Width: 4px
- Point Radius: 6px
- Point Border Width: 3px
- Point Border Color: #fff
- Tension: 0.4 (smooth curve)
- Fill: True (with gradient background)

**Data Format**:
```json
{
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [100, 150, 200, 250],
    "series_name": "Revenue",
    "format": "currency|percentage|number"
}
```

**Data Label Formatting**:
- Currency: "$125K" (thousands) or "$1.5M" (millions)
- Percentage: "45.5%"
- Number: "1,234" (locale formatted)

---

### 2. Area Chart
**Method**: `generate_area_chart()`
**Use Case**: Filled time series, stacked trends
**Styling**:
- Same as line chart but with `fill: True` for all datasets
- Background: Gradient with theme color at 0.2 opacity
- Border Width: 4px

**Data Format**: Same as line chart

---

### 3. Stacked Area Chart
**Method**: `generate_stacked_area_chart()`
**Use Case**: Multi-series composition over time
**Styling**:
- Stacking enabled on both X and Y axes
- Each series gets a unique color from palette
- Fill: True for all datasets
- Border Width: 3px

**Data Format**:
```json
{
    "label": "Q1",
    "Series_1": 100,
    "Series_2": 50,
    "Series_3": 75
}
```

---

### 4. Bar Chart (Vertical)
**Method**: `generate_bar_chart(horizontal=False)`
**Use Case**: Category comparison, rankings
**Styling**:
- Background Color: Palette colors (rotating through all 8 colors)
- Border Color: Same as background
- Border Width: 2px
- Border Radius: 10px
- Hover Border Width: 3px
- Hover Border Color: #fff

**Data Format**:
```json
{
    "labels": ["Category A", "Category B", "Category C"],
    "values": [100, 150, 200],
    "format": "currency|percentage|number"
}
```

---

### 5. Horizontal Bar Chart
**Method**: `generate_horizontal_bar_chart()`
**Use Case**: Category ranking, long labels
**Styling**:
- Same as vertical bar chart
- Index Axis: "y" (swaps X and Y)
- X-axis shows values, Y-axis shows categories

**Data Format**: Same as vertical bar chart

---

### 6. Grouped Bar Chart
**Method**: `generate_grouped_bar_chart()`
**Use Case**: Multi-series comparison (side-by-side)
**Styling**:
- Multiple datasets displayed side-by-side
- Each dataset gets a unique palette color
- Border Radius: 10px
- No stacking (grouped layout)

**Data Format**:
```json
{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "2023", "data": [100, 120, 140]},
        {"label": "2024", "data": [150, 180, 200]}
    ]
}
```

---

### 7. Pie Chart
**Method**: `generate_pie_chart()`
**Use Case**: Composition, market share, parts of whole
**Styling**:
- Segment Colors: Palette colors
- Border Color: #fff
- Border Width: 4px
- Hover Background Color: Darkened version of segment color
- Hover Border Color: #fff
- Hover Border Width: 5px
- Legend Position: right
- Data Labels: Percentage display on segments

**Data Format**:
```json
{
    "labels": ["Segment A", "Segment B", "Segment C"],
    "values": [30, 45, 25]
}
```

**Data Label**: Shows percentage (e.g., "30%") centered on segment

---

### 8. Doughnut Chart
**Method**: `generate_doughnut_chart()`
**Use Case**: Alternative to pie chart with center space
**Styling**:
- Same as pie chart
- Rendered as doughnut with hollow center
- Legend Position: right
- All color styling identical to pie

**Data Format**: Same as pie chart

---

### 9. Scatter Plot
**Method**: `generate_scatter_plot()`
**Use Case**: Correlation analysis, relationship visualization
**Styling**:
- Point Style: circle
- Point Radius: 8px (reduced from 10px in v3.3.0)
- Point Background Color: Palette color (opaque)
- Point Border Color: #fff
- Point Border Width: 2px
- No fill (transparent background)
- No line connecting points

**Data Format**:
```json
{
    "datasets": [
        {
            "label": "Series 1",
            "data": [
                {"x": 10, "y": 20},
                {"x": 15, "y": 25}
            ]
        }
    ]
}
```

---

### Additional Chart Types Supported (10+ more)

#### 10. Bubble Chart
- Point Radius: 8px (scatter), bubble size based on r value
- Transparency: 70% opacity (rgba with 0.7 alpha)
- Format: `{x: X, y: Y, r: RADIUS}`

#### 11. Radar Chart
- Point Radius: 4px
- Fill: True with 20% opacity
- Tension: 0.4

#### 12. Polar Area Chart
- Segments colored with palette
- Border: #fff, 4px

#### 13. Waterfall Chart
- Neutral color for totals
- Green for positive changes
- Red for negative changes

#### 14. Stacked Bar Chart
- Y-axis stacked: true
- X-axis stacked: true
- Each dataset gets palette color

#### 15-18. D3.js Chart Types
- Treemap, Sunburst, Choropleth USA, Sankey (SVG-based, external D3.js rendering)

---

## Chart.js Plugins & Options

### Global Chart Configuration

```javascript
{
    "responsive": true,
    "maintainAspectRatio": false,
    "animation": {
        "duration": 1500,           // 1.5 seconds
        "easing": "easeInOutQuart",
        "delay": 0,
        "loop": false,
        "animateRotate": true,      // Pie/Doughnut
        "animateScale": true        // Radar
    }
}
```

### Legend Plugin
```javascript
{
    "legend": {
        "display": true,            // Show only for multiple datasets
        "position": "top",          // Pie/Doughnut: "right"
        "labels": {
            "font": {"size": 14, "weight": "bold"},
            "padding": 15,
            "usePointStyle": true
        }
    }
}
```

### Data Labels Plugin
```javascript
{
    "datalabels": {
        "display": true,
        "color": "#fff",
        "font": {"size": 14, "weight": "bold"},
        "formatter": "function(value) { ... }",
        "anchor": "end|center",     // Depends on chart type
        "align": "top|end|center",
        "offset": 4,                // For line charts
        "backgroundColor": "rgba(0, 0, 0, 0.7)",
        "borderRadius": 4,
        "padding": 6
    }
}
```

### Tooltip Plugin
```javascript
{
    "tooltip": {
        "enabled": true,
        "mode": "nearest",
        "intersect": true
    }
}
```

### Grid & Axis Configuration
```javascript
{
    "scales": {
        "x": {
            "display": true,
            "grid": {
                "display": true,
                "color": "rgba(0, 0, 0, 0.08)",
                "lineWidth": 1
            },
            "ticks": {
                "display": true,
                "font": {"size": 12, "weight": "500"},
                "color": "#333",
                "padding": 8,
                "autoSkip": false,
                "maxRotation": 45,
                "minRotation": 0
            },
            "title": {
                "display": true,
                "font": {"size": 13, "weight": "bold"},
                "color": "#333"
            }
        },
        "y": {
            "display": true,
            "beginAtZero": true,    // Always start at 0
            "grid": {
                "display": true,
                "color": "rgba(0, 0, 0, 0.08)",
                "lineWidth": 1
            },
            "ticks": {
                "display": true,
                "font": {"size": 12, "weight": "500"},
                "color": "#333",
                "padding": 8,
                "callback": "function(value) { ... }"  // Format based on type
            },
            "title": {
                "display": true,
                "text": "Amount (USD)|Percentage (%)|Value",
                "font": {"size": 13, "weight": "bold"},
                "color": "#333"
            }
        }
    }
}
```

---

## Observations Panel Styling

### L02 Layout Observations Panel

**Container**: `<div class="l02-observations-panel">`
- **Width**: 540px (30% of L02 content area)
- **Height**: 720px
- **Padding**: 40px 32px (vertical, horizontal)
- **Background**: Theme `bg` color (#f8f9fa for professional)
- **Border Radius**: 8px
- **Overflow**: Y-axis auto (scrollable)
- **Box Sizing**: border-box

**Heading** (h3):
- **Font Family**: 'Inter', -apple-system, sans-serif
- **Font Size**: 22px
- **Font Weight**: 600
- **Color**: Theme `heading` color (#1f2937 for professional)
- **Margin**: 0 0 18px 0
- **Line Height**: 1.3
- **Text Align**: left

**Bullet List** (ul):
- **Margin**: 0
- **Padding Left**: 20px
- **List Style**: disc
- **Text Align**: left

**Bullet Items** (li):
- **Font Family**: 'Inter', -apple-system, sans-serif
- **Font Size**: 19px
- **Line Height**: 1.65
- **Color**: Theme `text` color (#374151 for professional)
- **Margin**: 0 0 10px 0
- **Text Align**: left

### Bullet Content Specifications

- **Maximum Bullets**: 6 (v3.3.5 reduced from 7)
- **Character Length Per Bullet**: 95-133 characters
- **Total Character Limit**: 800 characters (v3.3.5 reduced from 1000)
- **Format**: Pre-formatted by LLM with bullet markers (-, •, *, +)
- **Content**: Complete sentences, one key insight per bullet
- **Truncation**: Truncated with "..." if exceeds max_chars

---

## Layout Templates (L01, L02, L03)

### L01 Layout: Centered Chart with Insight
**Dimensions**: 1800×600px chart + text below
**Elements**:
- `element_4`: Chart HTML (1800×600px centered)
- `element_3`: AI-generated insight (2-3 sentences, max 150 words)
- `element_1`: Subtitle text

**Use Cases**:
- Main slide with focused message
- Single prominent metric or trend

**Text Styling** (Insight):
- Paragraph below chart
- Professional body text
- 2-3 concise sentences
- Max 150 words

### L02 Layout: Chart + Detailed Observations
**Dimensions**: 1260×720px chart (left) + 540×720px panel (right)
**Elements**:
- `element_3`: Chart HTML (1260×720px, left panel)
- `element_2`: Observations panel (540×720px, right panel)
- `element_1`: Subtitle

**Observations Panel Structure**:
```
┌─ Key Insights (heading) ─────────────────┐
│                                          │
│ • Bullet point 1 (95-133 chars)         │
│ • Bullet point 2 (95-133 chars)         │
│ • Bullet point 3 (95-133 chars)         │
│ • Bullet point 4 (95-133 chars)         │
│ • Bullet point 5 (95-133 chars)         │
│ • Bullet point 6 (95-133 chars)         │
│                                          │
└──────────────────────────────────────────┘
```

**Specifications**:
- Max 6 bullet points (v3.3.5)
- Total max 800 characters
- Each bullet 19px, 1.65 line-height
- Padding: 40px 32px
- Background: Light (theme dependent)

### L03 Layout: Side-by-Side Comparison
**Dimensions**: 840×540px each chart + descriptions
**Elements**:
- `element_4`: Left chart (840×540px)
- `element_2`: Right chart (840×540px)
- `element_3`: Left description (20-30 words)
- `element_5`: Right description (20-30 words)

**Description Specifications**:
- Length: 20-30 words per description
- Format: Single paragraph
- Content: Brief context about chart (before/after, option A/B, etc.)
- Font: Standard theme text styling

---

## Text Formatting & Character Limits

### L01 Insight Text
- **Purpose**: Below-chart insight for centered layout
- **Length**: 2-3 sentences
- **Max Words**: 150 words
- **Max Characters**: ~800-900 characters (no strict limit, but concise)
- **Max Tokens**: 200 (LLM generation)
- **Format**: Plain paragraph, no bullet points
- **Active Voice**: Professional, executive-focused

**Example**:
```
"Revenue grew steadily throughout FY 2024, achieving 42% growth from Q1 to Q4. 
The strongest acceleration occurred in Q2-Q3, driven by new product launches 
and market expansion. This consistent performance positions us for sustained 
growth in the coming fiscal year."
```

### L02 Observations Bullets
- **Purpose**: Key insights panel in L02 layout
- **Number of Bullets**: 5-6 (max 6)
- **Characters Per Bullet**: 95-133 characters (5% reduction in v3.3.5)
- **Max Total Characters**: 800 characters (reduced from 1000)
- **Max Tokens**: 500 (LLM generation)
- **Format**: Complete sentences, one insight per bullet
- **Bullet Markers**: LLM generates (-, •, *, +), stripped during assembly
- **Truncation**: Auto-truncated with "..." if exceeds 800 chars

**Example**:
```
- The doughnut chart shows balanced performance across key indicators with diverse growth areas
- Revenue Growth leads at 28%, indicating strong financial performance compared to other metrics
- Customer Growth follows at 25%, suggesting effective client acquisition strategies
- Market Expansion stands at 25%, reflecting stable penetration amidst competition
- Profit Margin at 22% highlights a need for improved operational efficiency
```

### L03 Descriptions
- **Purpose**: Context for each side-by-side comparison chart
- **Length**: 20-30 words per description
- **Max Tokens**: 60 (LLM generation)
- **Format**: Single paragraph, complete statement
- **Content**: Include key metric if relevant
- **Truncation**: Strict 20-30 word limit

**Example**:
```
Left: "Pre-automation baseline showing manual processing times across departments. 
Average task completion: 4.2 hours."

Right: "Post-automation showing streamlined workflow with improved efficiency metrics. 
Average task completion: 1.8 hours."
```

---

## Integration Points for Theme Injection

### 1. Initialize ChartJSGenerator with Theme
```python
from chartjs_generator import ChartJSGenerator

# Create generator with specific theme
generator = ChartJSGenerator(theme="professional")  # or "corporate", "vibrant"

# All subsequent charts use this theme's colors
chart_html = generator.generate_line_chart(data)
```

### 2. Layout Assembler Theme Injection
```python
from layout_assembler import L02LayoutAssembler

# Create assembler with theme
assembler = L02LayoutAssembler(theme="professional")

# Theme colors applied to observations panel
observations_html = assembler.assemble_observations_html(
    insights_text=insights,
    title="Key Insights",
    max_chars=800
)
```

### 3. REST API Theme Parameter
```json
{
    "context": {
        "theme": "professional|corporate|vibrant"
    }
}
```

### 4. Theme Color Access
```python
# Inside ChartJSGenerator
self.colors = self.THEMES[theme]  # Access theme colors
self.palette = self.colors["palette"]  # 8-color palette
self.gradients = self.colors.get("gradients", {})  # Gradient definitions
```

---

## Default Styling Parameters

### Chart Container Defaults
- **Class**: `l02-chart-container`
- **Width**: 1260px (L02) or 1800px (L01) or 840px (L03)
- **Height**: 720px (L02) or 600px (L01) or 540px (L03)
- **Position**: relative
- **Background**: white
- **Padding**: 20px
- **Box Sizing**: border-box
- **Overflow**: visible

### Global Color Defaults
- **Grid Lines**: rgba(0, 0, 0, 0.08) - Very light gray
- **Axis Text**: #333 - Dark gray
- **Data Label Background**: rgba(0, 0, 0, 0.7) - Dark semi-transparent
- **Data Label Border Radius**: 4px
- **Data Label Padding**: 6px
- **Data Label Color**: #fff - White text on dark background

### Global Font Defaults
- **Legend Font Size**: 14px, weight 600
- **Data Labels Font Size**: 14px, weight 600
- **Axis Ticks Font Size**: 12px, weight 500
- **Axis Titles Font Size**: 13px, weight 600
- **Observations Heading**: 22px, weight 600
- **Observations Bullets**: 19px, weight 400

### Animation Defaults
- **Duration**: 1500ms (1.5 seconds)
- **Easing**: easeInOutQuart
- **Delay**: 0ms
- **Loop**: false
- **Rotate Animation**: true (pie/doughnut)
- **Scale Animation**: true (radar)

### Border Defaults
- **Line Chart**: 4px border width
- **Bar Chart**: 2px border width, 10px border-radius
- **Pie/Doughnut**: 4px white border
- **Scatter/Bubble**: 2px point border
- **Grid Lines**: 1px width

### Point/Marker Defaults
- **Line Chart Points**: 6px radius
- **Scatter Points**: 8px radius
- **Point Border**: 2-3px white border
- **Hover Radius**: 8px (line) or auto (scatter)

---

## File Locations & Integration

### Main Configuration Files

1. **chartjs_generator.py** (169KB)
   - Location: `/agents/analytics_microservice_v3/chartjs_generator.py`
   - Contains: All chart generation methods, themes, colors, options
   - Key Classes: `ChartJSGenerator`
   - Key Methods: `_build_chart_options()`, `_prepare_datasets()`, `_wrap_in_canvas_inline_script()`

2. **layout_assembler.py** (8.5KB)
   - Location: `/agents/analytics_microservice_v3/layout_assembler.py`
   - Contains: L02 template assembly, observations panel styling
   - Key Classes: `L02LayoutAssembler`
   - Key Methods: `assemble_l02_content()`, `assemble_observations_html()`

3. **insight_generator.py** (13KB)
   - Location: `/agents/analytics_microservice_v3/insight_generator.py`
   - Contains: AI text generation for all layouts
   - Key Classes: `InsightGenerator`
   - Text Limits: L01 150 words, L02 800 chars, L03 20-30 words

4. **analytics_types.py** (5KB)
   - Location: `/agents/analytics_microservice_v3/analytics_types.py`
   - Contains: Layout dimensions (L01, L02, L03), analytics type mappings
   - Dimensions:
     - L01: 1800×600px
     - L02: 1260×720px (chart) + 540×720px (text)
     - L03: 840×540px each

### Integration Flow

```
REST Request
    ↓
agent.py (orchestration)
    ↓
chartjs_generator.py (generates chart HTML)
    ↓
insight_generator.py (generates observations text)
    ↓
layout_assembler.py (assembles final L02 layout)
    ↓
REST Response with element_3 (chart) + element_2 (observations)
```

---

## Summary: Key Takeaways

### Color Configuration
- 3 complete themes (professional, corporate, vibrant)
- 8 colors per palette + gradients
- Separate theme colors for L02 observations panel
- Grid/axis colors: rgba(0, 0, 0, 0.08)

### Font Configuration
- Legend: 14px bold
- Data Labels: 14px bold (white on dark background)
- Axis Labels: 12px 500-weight
- Observations Heading: 22px bold
- Observations Bullets: 19px regular, 1.65 line-height

### Text Limits
- L01: 150 words (2-3 sentences)
- L02: 800 characters total, 5-6 bullets, 95-133 chars per bullet
- L03: 20-30 words per description

### Layout Dimensions
- L01: 1800×600px centered chart
- L02: 1260×720px chart + 540×720px panel (70/30 split)
- L03: 840×540px each (side-by-side)

### Chart Types Supported (18 Total)
**Original 9**: Line, Area, Stacked Area, Bar, Horizontal Bar, Grouped Bar, Stacked Bar, Pie, Doughnut
**Specialized 5**: Scatter, Bubble, Radar, Polar Area, Waterfall
**D3.js 4**: Treemap, Sunburst, Choropleth USA, Sankey

### Styling Injection Points
1. `ChartJSGenerator(theme="...")` - Chart colors
2. `L02LayoutAssembler(theme="...")` - Panel colors
3. REST API `context.theme` - End-to-end theme
4. Individual color overrides via custom_options

