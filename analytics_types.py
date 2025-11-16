"""
Analytics Types and Layout Mappings for Analytics Microservice v3.

Defines supported analytics visualization types and their optimal layout mappings
for integration with Layout Builder (L01, L02, L03).
"""

from enum import Enum
from typing import Dict


class AnalyticsType(str, Enum):
    """Supported analytics visualization types."""

    # Tier 1: Core Business Analytics (Most Common)
    REVENUE_OVER_TIME = "revenue_over_time"
    QUARTERLY_COMPARISON = "quarterly_comparison"
    MARKET_SHARE = "market_share"
    YOY_GROWTH = "yoy_growth"
    KPI_METRICS = "kpi_metrics"


class LayoutType(str, Enum):
    """Layout Builder layout types for analytics slides."""

    L01 = "L01"  # Centered chart with insights (1800x600px chart + body text)
    L02 = "L02"  # Chart left + detailed explanation right (1260x720px chart + text panel)
    L03 = "L03"  # Side-by-side comparison (840x540px each + descriptions)


# Map analytics types to optimal Layout Builder layouts
ANALYTICS_LAYOUT_MAP: Dict[AnalyticsType, LayoutType] = {
    AnalyticsType.REVENUE_OVER_TIME: LayoutType.L01,
    AnalyticsType.QUARTERLY_COMPARISON: LayoutType.L01,
    AnalyticsType.MARKET_SHARE: LayoutType.L01,
    AnalyticsType.YOY_GROWTH: LayoutType.L03,  # Side-by-side comparison
    AnalyticsType.KPI_METRICS: LayoutType.L01,
}


# Map analytics types to ApexCharts chart types
ANALYTICS_CHART_MAP: Dict[AnalyticsType, str] = {
    AnalyticsType.REVENUE_OVER_TIME: "line",
    AnalyticsType.QUARTERLY_COMPARISON: "bar",
    AnalyticsType.MARKET_SHARE: "donut",
    AnalyticsType.YOY_GROWTH: "bar",
    AnalyticsType.KPI_METRICS: "bar",
}


# Layout dimension specifications (for chart sizing)
LAYOUT_DIMENSIONS = {
    LayoutType.L01: {
        "chart_width": 1800,
        "chart_height": 600,
        "description": "Centered chart with body text below"
    },
    LayoutType.L02: {
        "chart_width": 1260,
        "chart_height": 720,
        "description": "Chart left (2/3) with explanation right (1/3)"
    },
    LayoutType.L03: {
        "chart_width": 840,
        "chart_height": 540,
        "description": "Two charts side-by-side for comparison"
    }
}


def get_analytics_layout(analytics_type: str) -> str:
    """
    Get the optimal layout for an analytics type.

    Args:
        analytics_type: Analytics type identifier

    Returns:
        Layout type (L01, L02, or L03)
    """
    try:
        atype = AnalyticsType(analytics_type)
        return ANALYTICS_LAYOUT_MAP[atype].value
    except (ValueError, KeyError):
        # Default to L01 for unknown types
        return LayoutType.L01.value


def get_chart_type(analytics_type: str) -> str:
    """
    Get the ApexCharts chart type for an analytics type.

    Args:
        analytics_type: Analytics type identifier

    Returns:
        ApexCharts chart type (line, bar, donut, etc.)
    """
    try:
        atype = AnalyticsType(analytics_type)
        return ANALYTICS_CHART_MAP[atype]
    except (ValueError, KeyError):
        # Default to bar chart for unknown types
        return "bar"


def get_layout_dimensions(layout: str) -> Dict[str, int]:
    """
    Get chart dimensions for a layout type.

    Args:
        layout: Layout type (L01, L02, L03)

    Returns:
        Dictionary with chart_width and chart_height
    """
    try:
        ltype = LayoutType(layout)
        dims = LAYOUT_DIMENSIONS[ltype]
        return {
            "chart_width": dims["chart_width"],
            "chart_height": dims["chart_height"]
        }
    except (ValueError, KeyError):
        # Default to L01 dimensions
        return {
            "chart_width": 1800,
            "chart_height": 600
        }
