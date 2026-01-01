"""
Atomic Chart Routes for Analytics Microservice v3.5.0

14 atomic endpoints for gold standard chart types.
Each endpoint generates a single chart element with synthetic data.

Endpoint Pattern: POST /api/v1/charts/atomic/{chart_id}

Usage Example:
    POST /api/v1/charts/atomic/line
    {
        "narrative": "Show quarterly revenue growth for 2024",
        "include_insights": true,
        "width": 850,
        "height": 500
    }
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from models.atomic_models import (
    AtomicChartRequest,
    AtomicChartResponse,
    AtomicChartError,
    AtomicChartCatalogResponse,
    ChartTypeCatalogItem,
    GOLD_STANDARD_CHARTS
)
from core.atomic_chart_generator import AtomicChartGenerator

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/charts/atomic",
    tags=["Atomic Charts"],
    responses={
        400: {"model": AtomicChartError, "description": "Invalid request"},
        500: {"model": AtomicChartError, "description": "Generation failed"}
    }
)

# Initialize generator (singleton)
_generator: Optional[AtomicChartGenerator] = None


def get_generator(theme: str = "professional") -> AtomicChartGenerator:
    """Get or create atomic chart generator instance."""
    global _generator
    if _generator is None or _generator.theme != theme:
        _generator = AtomicChartGenerator(theme=theme)
    return _generator


# ========================================
# CATALOG ENDPOINT
# ========================================

@router.get(
    "/catalog",
    response_model=AtomicChartCatalogResponse,
    summary="Get atomic chart catalog",
    description="List all 14 gold standard chart types with metadata"
)
async def get_atomic_chart_catalog():
    """
    Get catalog of all available atomic chart types.

    Returns detailed information about each chart type including:
    - Display name and description
    - Category (trend, comparison, composition, correlation, flow)
    - Data format requirements
    - Example use cases

    This endpoint helps clients discover available chart types
    before generating charts.
    """
    generator = get_generator()
    catalog = generator.get_chart_catalog()

    return AtomicChartCatalogResponse(
        success=True,
        count=len(catalog),
        chart_types=[
            ChartTypeCatalogItem(**item) for item in catalog
        ],
        endpoint_pattern="/api/v1/charts/atomic/{chart_id}"
    )


# ========================================
# GENERIC CHART ENDPOINT
# ========================================

@router.post(
    "/{chart_id}",
    response_model=AtomicChartResponse,
    summary="Generate atomic chart",
    description="Generate a single chart element with synthetic data"
)
async def generate_atomic_chart(
    chart_id: str,
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """
    Generate atomic chart element for frontend positioning.

    This endpoint generates a self-contained chart HTML element
    that can be positioned anywhere on the slide by the frontend.

    **Chart Types:**
    - line, bar_vertical, bar_horizontal
    - pie, doughnut, polar_area
    - scatter, bubble
    - radar
    - area, area_stacked
    - bar_grouped, bar_stacked
    - waterfall

    **Features:**
    - Synthetic data generation based on narrative
    - Optional Key Insights panel
    - Self-contained HTML with embedded Chart.js

    Args:
        chart_id: One of 14 gold standard chart types
        request: Generation parameters
        theme: Color theme (professional, corporate, vibrant)

    Returns:
        AtomicChartResponse with chart_html and optional insights_html
    """
    # Validate chart_id
    if chart_id not in GOLD_STANDARD_CHARTS:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "INVALID_CHART_TYPE",
                "message": f"Chart type '{chart_id}' is not supported",
                "details": {"provided": chart_id, "valid_types": GOLD_STANDARD_CHARTS},
                "suggestion": f"Use one of: {', '.join(GOLD_STANDARD_CHARTS)}"
            }
        )

    try:
        generator = get_generator(theme)
        response = await generator.generate(chart_id, request)
        return response

    except ValueError as e:
        logger.error(f"Validation error for {chart_id}: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": str(e),
                "details": {"chart_id": chart_id},
                "suggestion": "Check request parameters"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate atomic chart {chart_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "GENERATION_FAILED",
                "message": f"Chart generation failed: {str(e)}",
                "details": {"chart_id": chart_id, "exception_type": type(e).__name__},
                "suggestion": "Check server logs for details"
            }
        )


# ========================================
# CONVENIENCE ENDPOINTS (Type-Specific)
# ========================================
# These provide better OpenAPI documentation

@router.post(
    "/line",
    response_model=AtomicChartResponse,
    summary="Generate line chart",
    description="Generate atomic line chart for time series data"
)
async def generate_line_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic line chart with synthetic time series data."""
    return await generate_atomic_chart("line", request, theme)


@router.post(
    "/bar_vertical",
    response_model=AtomicChartResponse,
    summary="Generate vertical bar chart",
    description="Generate atomic vertical bar chart for comparisons"
)
async def generate_bar_vertical_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic vertical bar chart with synthetic data."""
    return await generate_atomic_chart("bar_vertical", request, theme)


@router.post(
    "/bar_horizontal",
    response_model=AtomicChartResponse,
    summary="Generate horizontal bar chart",
    description="Generate atomic horizontal bar chart for rankings"
)
async def generate_bar_horizontal_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic horizontal bar chart with synthetic data."""
    return await generate_atomic_chart("bar_horizontal", request, theme)


@router.post(
    "/pie",
    response_model=AtomicChartResponse,
    summary="Generate pie chart",
    description="Generate atomic pie chart for market share/composition"
)
async def generate_pie_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic pie chart with synthetic percentage data."""
    return await generate_atomic_chart("pie", request, theme)


@router.post(
    "/doughnut",
    response_model=AtomicChartResponse,
    summary="Generate doughnut chart",
    description="Generate atomic doughnut chart for KPI breakdown"
)
async def generate_doughnut_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic doughnut chart with synthetic data."""
    return await generate_atomic_chart("doughnut", request, theme)


@router.post(
    "/scatter",
    response_model=AtomicChartResponse,
    summary="Generate scatter plot",
    description="Generate atomic scatter plot for correlation analysis"
)
async def generate_scatter_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic scatter chart with synthetic x/y data."""
    return await generate_atomic_chart("scatter", request, theme)


@router.post(
    "/bubble",
    response_model=AtomicChartResponse,
    summary="Generate bubble chart",
    description="Generate atomic bubble chart for 3D data visualization"
)
async def generate_bubble_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic bubble chart with synthetic x/y/r data."""
    return await generate_atomic_chart("bubble", request, theme)


@router.post(
    "/polar_area",
    response_model=AtomicChartResponse,
    summary="Generate polar area chart",
    description="Generate atomic polar area chart for cyclical data"
)
async def generate_polar_area_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic polar area chart with synthetic data."""
    return await generate_atomic_chart("polar_area", request, theme)


@router.post(
    "/radar",
    response_model=AtomicChartResponse,
    summary="Generate radar chart",
    description="Generate atomic radar chart for multi-attribute comparison"
)
async def generate_radar_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic radar chart with synthetic normalized data."""
    return await generate_atomic_chart("radar", request, theme)


@router.post(
    "/area",
    response_model=AtomicChartResponse,
    summary="Generate area chart",
    description="Generate atomic area chart for cumulative trends"
)
async def generate_area_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic area chart with synthetic time series data."""
    return await generate_atomic_chart("area", request, theme)


@router.post(
    "/area_stacked",
    response_model=AtomicChartResponse,
    summary="Generate stacked area chart",
    description="Generate atomic stacked area chart for part-to-whole over time"
)
async def generate_area_stacked_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic stacked area chart with synthetic multi-series data."""
    return await generate_atomic_chart("area_stacked", request, theme)


@router.post(
    "/bar_grouped",
    response_model=AtomicChartResponse,
    summary="Generate grouped bar chart",
    description="Generate atomic grouped bar chart for multi-series comparison"
)
async def generate_bar_grouped_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic grouped bar chart with synthetic multi-series data."""
    return await generate_atomic_chart("bar_grouped", request, theme)


@router.post(
    "/bar_stacked",
    response_model=AtomicChartResponse,
    summary="Generate stacked bar chart",
    description="Generate atomic stacked bar chart for composition by category"
)
async def generate_bar_stacked_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic stacked bar chart with synthetic multi-series data."""
    return await generate_atomic_chart("bar_stacked", request, theme)


@router.post(
    "/waterfall",
    response_model=AtomicChartResponse,
    summary="Generate waterfall chart",
    description="Generate atomic waterfall chart for bridge analysis"
)
async def generate_waterfall_chart(
    request: AtomicChartRequest,
    theme: str = Query("professional", description="Color theme")
):
    """Generate atomic waterfall chart with synthetic positive/negative data."""
    return await generate_atomic_chart("waterfall", request, theme)
