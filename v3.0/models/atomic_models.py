"""
Atomic Chart Models for Analytics Microservice v3.5.1

Request/response Pydantic models for atomic chart endpoints.
Each endpoint generates a single chart element with synthetic data.

v3.5.1 Changes:
- Added enable_editor field to AtomicChartRequest for edit button support
"""

from typing import List, Dict, Any, Optional
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
    enable_editor: bool = Field(
        False,
        description="If True, adds interactive data editor button (requires presentation_id)"
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

    @validator('narrative')
    def validate_narrative(cls, v):
        """Ensure narrative is meaningful if provided."""
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else v

    class Config:
        schema_extra = {
            "example": {
                "narrative": "Show quarterly revenue growth for 2024",
                "include_insights": True,
                "num_points": 4,
                "width": 850,
                "height": 500,
                "presentation_id": "abc123-def456",
                "enable_editor": True,
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
    data_used: List[Dict[str, Any]] = Field(
        ...,
        description="The synthetic data used for the chart"
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
        schema_extra = {
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
        schema_extra = {
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
