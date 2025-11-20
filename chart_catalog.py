"""
Chart Type Catalog for Analytics Microservice v3.

Provides comprehensive catalog of all supported chart types,
their constraints, use cases, and integration information
for Director Agent integration.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ChartLibrary(str, Enum):
    """Chart rendering libraries supported."""
    CHARTJS = "Chart.js"


class SupportedLayout(str, Enum):
    """Layouts supported by Analytics Service."""
    L01 = "L01"  # Centered chart + text below
    L02 = "L02"  # Chart left + observations right (Chart.js)
    L03 = "L03"  # Side-by-side charts (2 charts)


class ChartType(BaseModel):
    """Comprehensive chart type specification."""
    id: str = Field(..., description="Chart type identifier (e.g., 'line', 'bar_vertical')")
    name: str = Field(..., description="Human-readable chart name")
    description: str = Field(..., description="What this chart type visualizes")
    library: ChartLibrary = Field(..., description="Rendering library used")
    supported_layouts: List[SupportedLayout] = Field(..., description="Layouts that support this chart")
    min_data_points: int = Field(..., description="Minimum data points required")
    max_data_points: int = Field(..., description="Maximum data points recommended")
    optimal_data_points: str = Field(..., description="Optimal data point range")
    use_cases: List[str] = Field(..., description="Best use cases for this chart type")
    examples: List[str] = Field(..., description="Example scenarios")
    data_requirements: Dict[str, Any] = Field(default_factory=dict, description="Data structure requirements")
    visual_properties: Dict[str, Any] = Field(default_factory=dict, description="Visual characteristics")
    interactive_features: List[str] = Field(default_factory=list, description="Interactive capabilities")


# ===================================================
# CHART.JS TYPES (L02 Layout - Director Integration)
# ===================================================

CHARTJS_TYPES = [
    ChartType(
        id="line",
        name="Line Chart",
        description="Displays trends and changes over time with connected data points",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=50,
        optimal_data_points="3-20 points",
        use_cases=[
            "Revenue trends over time",
            "Performance metrics tracking",
            "Growth trajectories",
            "Time series analysis",
            "KPI monitoring"
        ],
        examples=[
            "Quarterly revenue growth",
            "Monthly active users",
            "Year-over-year sales comparison"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Time periods (Q1 2024, Jan, Week 1, etc.)",
            "value_format": "Numeric (revenue, count, percentage, etc.)"
        },
        visual_properties={
            "animations": "Smooth line drawing from left to right",
            "colors": "Professional gradient color scheme",
            "interactivity": "Hover for exact values"
        },
        interactive_features=["Edit chart data", "Hover tooltips", "Zoom/pan"]
    ),

    ChartType(
        id="bar_vertical",
        name="Vertical Bar Chart",
        description="Compares values across categories with vertical bars",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=30,
        optimal_data_points="3-12 bars",
        use_cases=[
            "Category comparisons",
            "Quarterly performance",
            "Product sales comparison",
            "Regional analysis",
            "Department metrics"
        ],
        examples=[
            "Sales by product category",
            "Revenue by region",
            "Performance by department"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Numeric values"
        },
        visual_properties={
            "animations": "Bars grow from bottom to top",
            "colors": "Gradient fills with professional palette",
            "interactivity": "Hover for exact values"
        },
        interactive_features=["Edit chart data", "Hover tooltips"]
    ),

    ChartType(
        id="bar_horizontal",
        name="Horizontal Bar Chart",
        description="Compares values with horizontal bars (better for long labels)",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=25,
        optimal_data_points="3-10 bars",
        use_cases=[
            "Ranking comparisons",
            "Long category names",
            "Top performers",
            "Survey responses",
            "Priority lists"
        ],
        examples=[
            "Top 10 customers by revenue",
            "Employee satisfaction scores",
            "Feature prioritization"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names (can be long)",
            "value_format": "Numeric values"
        },
        visual_properties={
            "animations": "Bars grow from left to right",
            "colors": "Gradient fills",
            "orientation": "Horizontal for better label readability"
        },
        interactive_features=["Edit chart data", "Hover tooltips"]
    ),

    ChartType(
        id="pie",
        name="Pie Chart",
        description="Shows part-to-whole relationships as circular slices",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=8,
        optimal_data_points="3-6 slices",
        use_cases=[
            "Market share distribution",
            "Budget allocation",
            "Revenue breakdown",
            "Category proportions",
            "Resource allocation"
        ],
        examples=[
            "Market share by competitor",
            "Budget by department",
            "Revenue by product line"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Positive numeric values",
            "constraint": "Values should sum to meaningful total (100%, revenue, etc.)"
        },
        visual_properties={
            "animations": "Slices expand from center",
            "colors": "Distinct colors per slice",
            "labels": "Percentage and value labels"
        },
        interactive_features=["Edit chart data", "Hover for percentages"]
    ),

    ChartType(
        id="doughnut",
        name="Doughnut Chart",
        description="Like pie chart but with hollow center (modern look)",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=8,
        optimal_data_points="3-6 slices",
        use_cases=[
            "Market composition",
            "Portfolio allocation",
            "Expense categories",
            "User demographics",
            "Product mix"
        ],
        examples=[
            "Investment portfolio breakdown",
            "Expense categories",
            "User demographics by age group"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Positive numeric values"
        },
        visual_properties={
            "animations": "Slices expand from center",
            "colors": "Professional gradient palette",
            "center": "Hollow for modern aesthetic"
        },
        interactive_features=["Edit chart data", "Hover for percentages"]
    ),

    ChartType(
        id="scatter",
        name="Scatter Plot",
        description="Shows relationship between two variables as points",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=5,
        max_data_points=100,
        optimal_data_points="10-50 points",
        use_cases=[
            "Correlation analysis",
            "Pattern detection",
            "Outlier identification",
            "Distribution visualization",
            "Regression analysis"
        ],
        examples=[
            "Price vs. demand correlation",
            "Age vs. income relationship",
            "Marketing spend vs. revenue"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Point identifiers (required)",
            "value_format": "Single numeric value per point (service auto-converts to x-y coordinates)",
            "note": "Despite being a scatter plot, uses label-value format like all other charts"
        },
        visual_properties={
            "animations": "Points appear with fade-in",
            "colors": "Single color with transparency",
            "size": "Uniform or variable point sizes"
        },
        interactive_features=["Edit chart data", "Hover for coordinates"]
    ),

    ChartType(
        id="bubble",
        name="Bubble Chart",
        description="Scatter plot with third dimension shown as bubble size",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=50,
        optimal_data_points="5-20 bubbles",
        use_cases=[
            "Three-dimensional comparisons",
            "Portfolio analysis",
            "Risk vs. return visualization",
            "Multi-variable analysis",
            "Market positioning"
        ],
        examples=[
            "Revenue (x) vs. Profit (y) vs. Market share (size)",
            "Risk (x) vs. Return (y) vs. Investment size (size)",
            "Age (x) vs. Salary (y) vs. Experience (size)"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Data point names (required)",
            "value_format": "Single numeric value per point (service auto-converts to x-y coordinates with derived radius)",
            "note": "Despite being a 3D chart, uses label-value format like all other charts"
        },
        visual_properties={
            "animations": "Bubbles expand from center",
            "colors": "Color-coded by category or gradient",
            "size": "Variable bubble sizes for third dimension"
        },
        interactive_features=["Edit chart data", "Hover for all three values"]
    ),

    ChartType(
        id="radar",
        name="Radar Chart",
        description="Multi-axis chart showing multiple variables from center point",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=12,
        optimal_data_points="4-8 axes",
        use_cases=[
            "Skill assessments",
            "Product comparisons",
            "Performance reviews",
            "Multi-criteria evaluation",
            "Competitive analysis"
        ],
        examples=[
            "Employee skills (leadership, technical, communication, etc.)",
            "Product features comparison",
            "Company performance metrics"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Metric/dimension names",
            "value_format": "Normalized values (0-100 or 0-10)"
        },
        visual_properties={
            "animations": "Web expands from center",
            "colors": "Filled area with semi-transparency",
            "shape": "Multi-sided polygon"
        },
        interactive_features=["Edit chart data", "Hover for values"]
    ),

    ChartType(
        id="polar_area",
        name="Polar Area Chart",
        description="Like pie chart but shows values as radius from center",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=12,
        optimal_data_points="4-8 segments",
        use_cases=[
            "Cyclical data visualization",
            "Multi-category comparison with magnitude",
            "Performance across dimensions",
            "Resource allocation with priority"
        ],
        examples=[
            "Seasonal sales patterns",
            "Weekly activity levels",
            "Department performance scores"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Positive numeric values"
        },
        visual_properties={
            "animations": "Segments expand from center",
            "colors": "Distinct colors per segment",
            "size": "Radius represents value magnitude"
        },
        interactive_features=["Edit chart data", "Hover for values"]
    ),

    # ===================================================
    # NEW CHART.JS TYPES (v3.4.0+)
    # ===================================================

    ChartType(
        id="area",
        name="Area Chart",
        description="Line chart with filled area below (Chart.js native)",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=50,
        optimal_data_points="5-30 points",
        use_cases=[
            "Cumulative trends over time",
            "Volume visualization",
            "Growth patterns",
            "Resource consumption",
            "Performance metrics with magnitude"
        ],
        examples=[
            "Total revenue accumulation",
            "Traffic volume over time",
            "Resource usage trends"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Time periods or categories",
            "value_format": "Numeric values"
        },
        visual_properties={
            "animations": "Area fills from left to right",
            "colors": "Gradient fills with transparency",
            "interactivity": "Hover for exact values"
        },
        interactive_features=["Edit chart data", "Hover tooltips", "Zoom/pan"]
    ),

    ChartType(
        id="area_stacked",
        name="Stacked Area Chart",
        description="Multiple areas stacked on top of each other showing cumulative trends",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=40,
        optimal_data_points="5-20 points",
        use_cases=[
            "Multi-series cumulative trends",
            "Category composition over time",
            "Revenue breakdown by product",
            "Resource allocation tracking",
            "Market share evolution"
        ],
        examples=[
            "Revenue by product line over quarters",
            "User acquisition by channel over time",
            "Budget allocation by department"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Time periods",
            "value_format": "Numeric values (positive)"
        },
        visual_properties={
            "animations": "Areas stack and fill from bottom",
            "colors": "Multiple gradient fills",
            "stacking": "Values cumulate vertically"
        },
        interactive_features=["Edit chart data", "Hover tooltips", "Series toggle"]
    ),

    ChartType(
        id="bar_grouped",
        name="Grouped Bar Chart",
        description="Multiple bar series displayed side-by-side for comparison",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=24,
        optimal_data_points="3-10 groups",
        use_cases=[
            "Multi-series categorical comparison",
            "Year-over-year comparisons",
            "Product performance across regions",
            "Team performance comparison",
            "A/B test results"
        ],
        examples=[
            "Sales by product across Q1-Q4",
            "Performance metrics by team and quarter",
            "Regional sales comparison across years"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Numeric values"
        },
        visual_properties={
            "animations": "Bars grow from bottom",
            "colors": "Distinct colors per series",
            "grouping": "Bars grouped by category"
        },
        interactive_features=["Edit chart data", "Hover tooltips", "Series toggle"]
    ),

    ChartType(
        id="bar_stacked",
        name="Stacked Bar Chart",
        description="Bars stacked to show part-to-whole and total values",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=2,
        max_data_points=24,
        optimal_data_points="3-10 categories",
        use_cases=[
            "Part-to-whole composition",
            "Total with breakdown",
            "Budget allocation visualization",
            "Resource distribution",
            "Category composition"
        ],
        examples=[
            "Total sales with product breakdown",
            "Budget by department and category",
            "Project hours by team member and task type"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Category names",
            "value_format": "Numeric values"
        },
        visual_properties={
            "animations": "Bars grow and stack from bottom",
            "colors": "Distinct colors per series",
            "stacking": "Values cumulate vertically"
        },
        interactive_features=["Edit chart data", "Hover tooltips", "Series toggle"]
    ),

    ChartType(
        id="waterfall",
        name="Waterfall Chart",
        description="Shows cumulative effect of sequential positive/negative values (Chart.js native)",
        library=ChartLibrary.CHARTJS,
        supported_layouts=[SupportedLayout.L02],
        min_data_points=3,
        max_data_points=20,
        optimal_data_points="4-12 steps",
        use_cases=[
            "Financial reconciliation",
            "Profit/loss breakdown",
            "Bridge analysis",
            "Variance explanation",
            "Cash flow analysis"
        ],
        examples=[
            "Income statement waterfall",
            "Budget to actual variance",
            "Starting to ending cash flow",
            "Year-over-year revenue change"
        ],
        data_requirements={
            "fields": ["label", "value"],
            "label_format": "Step names",
            "value_format": "Numeric (positive or negative)"
        },
        visual_properties={
            "animations": "Bars cascade from left to right",
            "colors": "Green for positive, red for negative",
            "connectors": "Lines show cumulative flow"
        },
        interactive_features=["Edit chart data", "Hover for running totals"]
    ),

    # ===================================================
    # CHART.JS PLUGIN TYPES - REMOVED (v3.4.3)
    # ===================================================
    # The following 8 plugin-based chart types were removed due to rendering issues:
    # - treemap, heatmap, matrix, boxplot, candlestick, financial, sankey, mixed
    # Keeping 14 total chart types: 9 original Chart.js + 5 new native Chart.js types
]


# ===================================================
# COMPLETE CATALOG
# ===================================================

ALL_CHART_TYPES = CHARTJS_TYPES


def get_chart_catalog() -> List[ChartType]:
    """Get complete chart type catalog."""
    return ALL_CHART_TYPES


def get_chartjs_types() -> List[ChartType]:
    """Get Chart.js chart types (all types now Chart.js only)."""
    return CHARTJS_TYPES


def get_chart_types_by_layout(layout: SupportedLayout) -> List[ChartType]:
    """Get chart types compatible with specific layout."""
    return [ct for ct in ALL_CHART_TYPES if layout in ct.supported_layouts]


def get_chart_type_by_id(chart_id: str) -> Optional[ChartType]:
    """Get specific chart type by ID."""
    # Handle aliases (matrix and financial aliases removed with plugin charts in v3.4.3)
    alias_map = {}
    chart_id = alias_map.get(chart_id, chart_id)

    for ct in ALL_CHART_TYPES:
        if ct.id == chart_id:
            return ct
    return None


def get_chart_type_summary() -> Dict[str, Any]:
    """Get summary statistics about chart type catalog."""
    return {
        "total_chart_types": len(ALL_CHART_TYPES),
        "chartjs_types": len(CHARTJS_TYPES),
        "l02_compatible": len(get_chart_types_by_layout(SupportedLayout.L02)),
        "chart_libraries": [ChartLibrary.CHARTJS.value],
        "supported_layouts": [l.value for l in SupportedLayout]
    }
