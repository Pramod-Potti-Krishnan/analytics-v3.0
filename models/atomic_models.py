"""
Atomic Chart Models for Analytics Microservice v3.5.0

Request/response Pydantic models for atomic chart endpoints.
Each endpoint generates a single chart element with synthetic data.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class ChartTypeId(str, Enum):
    """The 14 gold standard chart types."""
    LINE = "line"
    BAR_VERTICAL = "bar_vertical"
    BAR_HORIZONTAL = "bar_horizontal"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    POLAR_AREA = "polar_area"
    RADAR = "radar"
    AREA = "area"
    AREA_STACKED = "area_stacked"
    BAR_GROUPED = "bar_grouped"
    BAR_STACKED = "bar_stacked"
    WATERFALL = "waterfall"


# List of all valid chart IDs for validation
GOLD_STANDARD_CHARTS = [ct.value for ct in ChartTypeId]


class AtomicChartRequest(BaseModel):
    """Request for atomic chart generation."""

    narrative: Optional[str] = Field(
        None,
        max_length=2000,
        description="Context for data generation (e.g., 'Show quarterly revenue growth for 2024')"
    )
    include_insights: bool = Field(
        False,
        description="If True, also return Key Insights panel as separate HTML element"
    )
    num_points: Optional[int] = Field(
        None,
        ge=2,
        le=50,
        description="Number of data points to generate (auto-determined if None)"
    )
    width: int = Field(
        850,
        ge=200,
        le=2000,
        description="Chart container width in pixels"
    )
    height: int = Field(
        500,
        ge=150,
        le=1500,
        description="Chart container height in pixels"
    )
    presentation_id: Optional[str] = Field(
        None,
        description="Presentation UUID for editor integration"
    )
    chart_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Override auto-generated chart title"
    )
    theme: str = Field(
        "professional",
        description="Color theme for the chart"
    )
    enable_editor: bool = Field(
        True,
        description="v3.6.0: If True, include edit button for interactive data editing"
    )

    @validator('narrative')
    def validate_narrative(cls, v):
        """Ensure narrative is meaningful if provided."""
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v

    class Config:
        json_schema_extra = {
            "example": {
                "narrative": "Show quarterly revenue growth for 2024",
                "include_insights": True,
                "num_points": 4,
                "width": 850,
                "height": 500,
                "chart_title": "Revenue Growth Q1-Q4 2024",
                "theme": "professional"
            }
        }


class ChartDimensions(BaseModel):
    """Dimensions for chart or insights panel."""
    width: int
    height: int


class DataPointSimple(BaseModel):
    """Simple label-value data point."""
    label: str
    value: float


class DataPointScatter(BaseModel):
    """Scatter/bubble data point with coordinates."""
    label: str
    x: float
    y: float
    r: Optional[float] = None  # For bubble charts


class AtomicChartResponse(BaseModel):
    """Response with atomic chart element(s)."""

    success: bool = Field(True, description="Whether generation was successful")
    chart_id: str = Field(..., description="The chart type ID requested")
    chart_html: str = Field(..., description="Self-contained chart HTML with embedded scripts")
    insights_html: Optional[str] = Field(
        None,
        description="Key Insights panel HTML (only if include_insights=True)"
    )

    # Metadata
    # v3.7.4: Accept both list (single-series) and dict (multi-series) formats
    data_used: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(
        ...,
        description="The synthetic data used for the chart (list for single-series, dict for multi-series)"
    )
    chart_title: str = Field(..., description="Generated or provided chart title")
    generation_time_ms: int = Field(..., description="Processing time in milliseconds")
    synthetic_data: bool = Field(True, description="Always true for atomic endpoints")

    # Positioning info for frontend
    chart_dimensions: ChartDimensions = Field(
        ...,
        description="Dimensions of chart container"
    )
    insights_dimensions: Optional[ChartDimensions] = Field(
        None,
        description="Dimensions of insights panel (if generated)"
    )

    # Editor integration
    element_id: str = Field(..., description="Unique element ID for frontend positioning")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "chart_id": "line",
                "chart_html": "<div class=\"atomic-chart-container\">...</div>",
                "insights_html": "<div class=\"atomic-insights-container\">...</div>",
                "data_used": [
                    {"label": "Q1 2024", "value": 125000},
                    {"label": "Q2 2024", "value": 145000},
                    {"label": "Q3 2024", "value": 162000},
                    {"label": "Q4 2024", "value": 178000}
                ],
                "chart_title": "Revenue Growth Q1-Q4 2024",
                "generation_time_ms": 45,
                "synthetic_data": True,
                "chart_dimensions": {"width": 850, "height": 500},
                "insights_dimensions": {"width": 400, "height": 500},
                "element_id": "atomic-chart-abc12345"
            }
        }


class AtomicChartError(BaseModel):
    """Error response for atomic chart generation."""

    success: bool = Field(False)
    error_code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    suggestion: Optional[str] = Field(None, description="Suggested fix")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "INVALID_CHART_TYPE",
                "message": "Chart type 'unknown_chart' is not supported",
                "details": {"provided": "unknown_chart"},
                "suggestion": "Use one of: line, bar_vertical, bar_horizontal, pie, ..."
            }
        }


class ChartTypeCatalogItem(BaseModel):
    """Information about a single chart type for catalog endpoint."""

    id: str
    name: str
    description: str
    category: str
    data_format: str
    min_points: int
    max_points: int
    supports_multi_series: bool
    example_use_cases: List[str]


class AtomicChartCatalogResponse(BaseModel):
    """Response listing all available atomic chart types."""

    success: bool = True
    count: int
    chart_types: List[ChartTypeCatalogItem]
    endpoint_pattern: str = "/api/v1/charts/atomic/{chart_id}"


# ========================================
# v3.7.0: CREATE ELEMENT MODELS
# ========================================

class GridPosition(BaseModel):
    """Grid position in CSS grid notation (32x18 system)."""
    grid_row: str = Field(
        ...,
        description="Row position in 'start/end' format (e.g., '4/15' for rows 4-14)",
        pattern=r"^\d+/\d+$"
    )
    grid_column: str = Field(
        ...,
        description="Column position in 'start/end' format (e.g., '2/16' for columns 2-15)",
        pattern=r"^\d+/\d+$"
    )

    class Config:
        json_json_schema_extra = {
            "example": {
                "grid_row": "4/15",
                "grid_column": "2/16"
            }
        }


class GridSize(BaseModel):
    """Grid size in grid units."""
    cols: int = Field(..., ge=2, le=30, description="Number of columns")
    rows: int = Field(..., ge=2, le=14, description="Number of rows")


class CreateElementRequest(BaseModel):
    """
    Request to create a chart as a Layout Service element.

    v3.7.0: Creates chart as independent element with proper grid positioning,
    rather than injecting HTML into existing elements.
    """

    # Required fields
    presentation_id: str = Field(
        ...,
        description="UUID of the presentation to add the chart to"
    )
    slide_index: int = Field(
        ...,
        ge=0,
        description="Zero-based index of the slide to add the chart to"
    )
    chart_type: str = Field(
        ...,
        description="Chart type ID (e.g., 'line', 'bar_vertical', 'pie')"
    )
    layout_service_url: str = Field(
        ...,
        description="Base URL of the Layout Service (e.g., 'https://web-production-f0d13.up.railway.app')"
    )

    # Optional chart generation fields
    narrative: Optional[str] = Field(
        None,
        max_length=2000,
        description="Context for synthetic data generation"
    )
    data: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Explicit data points. If None, synthetic data is generated."
    )
    chart_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Override auto-generated chart title"
    )

    # Optional positioning fields
    position: Optional[GridPosition] = Field(
        None,
        description="Explicit grid position. If None, auto-calculated using stacking algorithm."
    )
    size: Optional[GridSize] = Field(
        None,
        description="Explicit grid size. If None, calculated based on chart type."
    )

    # Options
    theme: str = Field(
        "professional",
        description="Color theme for the chart"
    )
    enable_editor: bool = Field(
        True,
        description="Include edit button for interactive data editing"
    )
    z_index: Optional[int] = Field(
        None,
        ge=1,
        le=10000,
        description="Z-index for layering. If None, auto-assigned by Layout Service."
    )

    @validator('chart_type')
    def validate_chart_type(cls, v):
        """Validate chart type is supported."""
        if v not in GOLD_STANDARD_CHARTS:
            raise ValueError(f"Chart type '{v}' not supported. Valid types: {GOLD_STANDARD_CHARTS}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres-12345678-abcd-1234-efgh-567890abcdef",
                "slide_index": 0,
                "chart_type": "line",
                "layout_service_url": "https://web-production-f0d13.up.railway.app",
                "narrative": "Show quarterly revenue growth for 2024",
                "theme": "professional",
                "enable_editor": True
            }
        }


class CreateElementResponse(BaseModel):
    """
    Response from creating a chart element.

    v3.7.0: Returns element details including position and Layout Service element ID.
    """

    success: bool = Field(True, description="Whether element creation was successful")
    element_id: str = Field(..., description="UUID of the created Layout Service element")
    chart_type: str = Field(..., description="The chart type that was created")

    # Position information
    position: GridPosition = Field(..., description="Final grid position of the element")
    size: GridSize = Field(..., description="Grid size of the element")

    # Metadata
    presentation_id: str = Field(..., description="Presentation the element was added to")
    slide_index: int = Field(..., description="Slide index the element was added to")
    z_index: int = Field(..., description="Z-index of the element")
    generation_time_ms: int = Field(..., description="Processing time in milliseconds")

    # Chart data
    chart_title: str = Field(..., description="Title of the generated chart")
    data_points: int = Field(..., description="Number of data points in the chart")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "element_id": "chart_a1b2c3d4",
                "chart_type": "line",
                "position": {"grid_row": "4/15", "grid_column": "2/16"},
                "size": {"cols": 14, "rows": 11},
                "presentation_id": "pres-12345678-abcd-1234-efgh-567890abcdef",
                "slide_index": 0,
                "z_index": 150,
                "generation_time_ms": 156,
                "chart_title": "Quarterly Revenue Growth 2024",
                "data_points": 4
            }
        }


class CreateElementError(BaseModel):
    """Error response for element creation failures."""

    success: bool = Field(False)
    error_code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "LAYOUT_SERVICE_ERROR",
                "message": "Failed to create element in Layout Service",
                "details": {"status_code": 500, "response": "Internal server error"}
            }
        }
