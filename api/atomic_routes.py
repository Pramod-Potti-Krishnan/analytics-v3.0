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
    GOLD_STANDARD_CHARTS,
    # v3.7.0: Create element models
    CreateElementRequest,
    CreateElementResponse,
    CreateElementError,
    GridPosition as GridPositionModel,
    GridSize as GridSizeModel
)
from core.atomic_chart_generator import AtomicChartGenerator
from core.element_positioner import ElementPositioner, GridPosition, GridSize
import httpx
import time

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
# v3.7.0: CREATE ELEMENT ENDPOINT
# (MUST be before /{chart_id} to prevent route conflict)
# ========================================

# Initialize position calculator (singleton)
_positioner: Optional[ElementPositioner] = None


def get_positioner() -> ElementPositioner:
    """Get or create element positioner instance."""
    global _positioner
    if _positioner is None:
        _positioner = ElementPositioner()
    return _positioner


@router.post(
    "/create-element",
    response_model=CreateElementResponse,
    responses={
        400: {"model": CreateElementError, "description": "Invalid request"},
        500: {"model": CreateElementError, "description": "Element creation failed"},
        502: {"model": CreateElementError, "description": "Layout Service error"}
    },
    summary="Create chart as Layout Service element",
    description="""
    Generate a chart and create it as an independent Layout Service element.

    **v3.7.0 Feature**: Instead of injecting HTML into existing elements,
    this endpoint creates the chart as a proper Layout Service element with:
    - Its own grid position
    - Its own drag handles
    - Proper border alignment
    - Independent z-index layer

    **Auto-Positioning**: If no position is specified, uses top-down, left-right
    stacking algorithm to find optimal placement within content area (rows 4-17,
    columns 2-30).

    **Auto-Sizing**: If no size is specified, calculates optimal grid size based
    on chart type (e.g., pie charts get square dimensions, line charts wider).
    """
)
async def create_chart_element(request: CreateElementRequest):
    """
    Create a chart as an independent Layout Service element.

    Flow:
    1. Generate chart HTML using AtomicChartGenerator
    2. Calculate grid position (if not provided)
    3. Call Layout Service POST /charts to create element
    4. Return element ID and final position

    Args:
        request: CreateElementRequest with presentation, chart type, and options

    Returns:
        CreateElementResponse with element details and position
    """
    start_time = time.time()

    try:
        # 1. Get positioner and generator
        positioner = get_positioner()
        generator = get_generator(request.theme)

        # 2. Calculate chart size
        if request.size:
            element_size = GridSize(cols=request.size.cols, rows=request.size.rows)
        else:
            element_size = positioner.get_chart_size(request.chart_type)

        logger.info(
            f"Creating {request.chart_type} element: size={element_size.cols}x{element_size.rows}"
        )

        # 3. Calculate position if not provided
        if request.position:
            position = GridPosition(
                grid_row=request.position.grid_row,
                grid_column=request.position.grid_column
            )
        else:
            # Query existing elements from Layout Service
            existing_elements = await _get_existing_elements(
                request.layout_service_url,
                request.presentation_id,
                request.slide_index
            )
            position = positioner.calculate_position(element_size, existing_elements)

        logger.info(f"Calculated position: row={position.grid_row}, col={position.grid_column}")

        # 4. Calculate pixel dimensions for chart HTML
        # Grid unit = 60px, so convert grid size to pixels
        chart_width = element_size.cols * 60 - 20  # Subtract padding
        chart_height = element_size.rows * 60 - 20

        # 5. Generate chart HTML
        chart_request = AtomicChartRequest(
            narrative=request.narrative,
            width=chart_width,
            height=chart_height,
            chart_title=request.chart_title,
            theme=request.theme,
            enable_editor=request.enable_editor,
            presentation_id=request.presentation_id
        )

        chart_response = await generator.generate(request.chart_type, chart_request)

        # 6. Create element in Layout Service
        element_result = await _create_layout_element(
            layout_service_url=request.layout_service_url,
            presentation_id=request.presentation_id,
            slide_index=request.slide_index,
            chart_html=chart_response.chart_html,
            position=position,
            z_index=request.z_index
        )

        # 7. Calculate response
        generation_time_ms = int((time.time() - start_time) * 1000)

        return CreateElementResponse(
            success=True,
            element_id=element_result["element_id"],
            chart_type=request.chart_type,
            position=GridPositionModel(
                grid_row=position.grid_row,
                grid_column=position.grid_column
            ),
            size=GridSizeModel(
                cols=element_size.cols,
                rows=element_size.rows
            ),
            presentation_id=request.presentation_id,
            slide_index=request.slide_index,
            z_index=element_result.get("z_index", 150),
            generation_time_ms=generation_time_ms,
            chart_title=chart_response.chart_title,
            data_points=len(chart_response.data_used)
        )

    except ValueError as e:
        logger.error(f"Position calculation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "POSITION_ERROR",
                "message": str(e),
                "details": {"chart_type": request.chart_type}
            }
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Layout Service HTTP error: {e}")
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "error_code": "LAYOUT_SERVICE_ERROR",
                "message": f"Layout Service returned error: {e.response.status_code}",
                "details": {
                    "status_code": e.response.status_code,
                    "url": str(e.request.url)
                }
            }
        )
    except httpx.RequestError as e:
        logger.error(f"Layout Service connection error: {e}")
        raise HTTPException(
            status_code=502,
            detail={
                "success": False,
                "error_code": "LAYOUT_SERVICE_CONNECTION",
                "message": f"Failed to connect to Layout Service: {str(e)}",
                "details": {"layout_service_url": request.layout_service_url}
            }
        )
    except Exception as e:
        logger.error(f"Element creation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "CREATION_FAILED",
                "message": f"Element creation failed: {str(e)}",
                "details": {"exception_type": type(e).__name__}
            }
        )


async def _get_existing_elements(
    layout_service_url: str,
    presentation_id: str,
    slide_index: int
) -> list:
    """
    Query existing elements from Layout Service for position calculation.

    v3.7.1 FIX: Uses GET /presentations/{id} instead of non-existent
    GET /slides/{index} endpoint.

    Returns list of element positions in format:
    [{"grid_row": "4/15", "grid_column": "2/16"}, ...]
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # v3.7.1 FIX: Query full presentation data, then extract slide
            url = f"{layout_service_url}/api/presentations/{presentation_id}"
            response = await client.get(url)

            # Handle cases where presentation doesn't exist
            if response.status_code == 404:
                logger.debug(f"Presentation {presentation_id} not found, assuming empty")
                return []

            response.raise_for_status()
            presentation_data = response.json()

            # Extract the specific slide from presentation
            # Try both "slides" array and "presentation.slides"
            slides = (
                presentation_data.get("slides") or
                presentation_data.get("presentation", {}).get("slides") or
                []
            )

            if slide_index >= len(slides):
                logger.debug(f"Slide {slide_index} not in presentation (has {len(slides)} slides)")
                return []

            slide_data = slides[slide_index]

            # Extract element positions
            elements = []

            # Check various element types
            for element_type in ["charts", "text_boxes", "images", "diagrams", "infographics"]:
                element_list = slide_data.get(element_type, [])
                for elem in element_list:
                    if "position" in elem:
                        elements.append(elem["position"])
                    elif "grid_row" in elem and "grid_column" in elem:
                        elements.append({
                            "grid_row": elem["grid_row"],
                            "grid_column": elem["grid_column"]
                        })

            logger.debug(f"Found {len(elements)} existing elements on slide {slide_index}")
            return elements

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return []
        logger.warning(f"Layout Service HTTP error: {e.response.status_code}")
        return []  # Gracefully assume empty rather than failing
    except Exception as e:
        logger.warning(f"Failed to query existing elements: {e}")
        return []  # Assume empty if we can't query


async def _create_layout_element(
    layout_service_url: str,
    presentation_id: str,
    slide_index: int,
    chart_html: str,
    position: GridPosition,
    z_index: Optional[int] = None
) -> dict:
    """
    Create chart element in Layout Service with correct position.

    v3.7.1 FIX: Layout Service ignores position on POST, so we use CREATE+UPDATE pattern:
    1. POST to create element (gets default full-page position)
    2. PUT to update with correct position

    Uses:
    - POST /api/presentations/{id}/slides/{index}/charts (create)
    - PUT /api/presentations/{id}/slides/{index}/charts/{chart_id} (update position)

    Returns dict with element_id and z_index.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create element via POST
        create_url = f"{layout_service_url}/api/presentations/{presentation_id}/slides/{slide_index}/charts"

        create_payload = {
            "position": {
                "grid_row": position.grid_row,
                "grid_column": position.grid_column
            },
            "chart_html": chart_html
        }

        if z_index is not None:
            create_payload["z_index"] = z_index

        logger.info(f"Creating element at {create_url}")
        logger.debug(f"Payload position: {create_payload['position']}")

        response = await client.post(create_url, json=create_payload)
        response.raise_for_status()

        result = response.json()

        # Extract element ID from response
        # Layout Service may return it in different formats
        element_id = (
            result.get("chart", {}).get("id") or
            result.get("element_id") or
            result.get("id") or
            f"chart_{presentation_id}_{slide_index}"
        )

        final_z_index = result.get("chart", {}).get("z_index") or result.get("z_index") or 150

        # Step 2: Update position via PUT (v3.7.1 FIX)
        # Layout Service ignores position on POST, so we update immediately
        update_url = f"{layout_service_url}/api/presentations/{presentation_id}/slides/{slide_index}/charts/{element_id}"

        update_payload = {
            "position": {
                "grid_row": position.grid_row,
                "grid_column": position.grid_column
            }
        }

        logger.info(f"Updating element position at {update_url}")
        logger.debug(f"Update position: {update_payload['position']}")

        try:
            update_response = await client.put(update_url, json=update_payload)
            update_response.raise_for_status()
            logger.info(f"Position updated successfully for {element_id}")
        except httpx.HTTPStatusError as e:
            # Log but don't fail if update fails - element was still created
            logger.warning(f"Failed to update position for {element_id}: {e}")

        return {
            "element_id": element_id,
            "z_index": final_z_index
        }


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
