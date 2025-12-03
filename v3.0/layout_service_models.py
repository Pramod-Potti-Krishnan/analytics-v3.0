"""
Layout Service Integration Models
=================================

Pydantic models for Layout Service chart generation endpoint.
Follows AI_SERVICE_CHART.md specification for request/response schemas.

Author: Analytics Microservice v3 Team
Date: 2025-12
"""

from typing import List, Optional, Literal, Union, Any, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================
# ENUMS
# ============================================

class ChartType(str, Enum):
    """Supported chart types for Layout Service."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    RADAR = "radar"
    POLAR_AREA = "polarArea"


class ChartPalette(str, Enum):
    """Color palette options from AI_SERVICE_CHART.md spec."""
    DEFAULT = "default"
    PROFESSIONAL = "professional"
    VIBRANT = "vibrant"
    PASTEL = "pastel"
    MONOCHROME = "monochrome"
    SEQUENTIAL = "sequential"
    DIVERGING = "diverging"
    CATEGORICAL = "categorical"


class LegendPosition(str, Enum):
    """Legend position options."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class AxisType(str, Enum):
    """Axis type options."""
    CATEGORY = "category"
    TIME = "time"
    LINEAR = "linear"


class TrendType(str, Enum):
    """Trend analysis types."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


class ChartErrorCode(str, Enum):
    """Error codes for chart generation."""
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_PROMPT = "INVALID_PROMPT"
    INVALID_GRID_SIZE = "INVALID_GRID_SIZE"
    GRID_TOO_SMALL = "GRID_TOO_SMALL"
    MISSING_DATA = "MISSING_DATA"
    GENERATION_FAILED = "GENERATION_FAILED"
    DATA_INCONSISTENT = "DATA_INCONSISTENT"
    RATE_LIMITED = "RATE_LIMITED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# ============================================
# REQUEST MODELS
# ============================================

class ChartContext(BaseModel):
    """Context information for chart generation."""
    presentationTitle: str = Field(..., min_length=1, max_length=200)
    slideTitle: Optional[str] = Field(None, max_length=200)
    slideIndex: int = Field(..., ge=0)
    industry: Optional[str] = Field(None, max_length=100, description="Industry context for realistic data")
    timeFrame: Optional[str] = Field(None, max_length=50, description="Time range like 'Q1 2024' or '2020-2024'")


class ChartConstraints(BaseModel):
    """Grid-based size constraints for chart rendering."""
    gridWidth: int = Field(..., ge=1, le=12, description="Element width in grid units (1-12)")
    gridHeight: int = Field(..., ge=1, le=8, description="Element height in grid units (1-8)")

    def get_area(self) -> int:
        """Calculate grid area."""
        return self.gridWidth * self.gridHeight


class ChartConfig(BaseModel):
    """Optional chart configuration parameters."""
    dataPoints: Optional[int] = Field(None, ge=1, le=100, description="Suggested number of data points")
    datasets: Optional[int] = Field(None, ge=1, le=10, description="Number of data series")
    animated: Optional[bool] = Field(True, description="Enable chart animations")
    aspectRatio: Optional[float] = Field(None, gt=0, description="Width/height ratio override")


class ChartStyle(BaseModel):
    """Style options for chart rendering."""
    palette: ChartPalette = Field(ChartPalette.DEFAULT, description="Color scheme")
    customColors: Optional[List[str]] = Field(None, description="Override palette with custom colors")
    showLegend: Optional[bool] = Field(True, description="Display legend")
    legendPosition: Optional[LegendPosition] = Field(LegendPosition.TOP, description="Legend placement")
    showGrid: Optional[bool] = Field(True, description="Display grid lines")
    showDataLabels: Optional[bool] = Field(False, description="Show values on data points")

    @validator('customColors')
    def validate_colors(cls, v):
        if v is not None:
            for color in v:
                if not color.startswith('#') or len(color) not in [4, 7, 9]:
                    raise ValueError(f"Invalid color format: {color}. Use hex format like #RGB or #RRGGBB")
        return v


class ChartAxes(BaseModel):
    """Axis configuration options."""
    xLabel: Optional[str] = Field(None, max_length=100, description="X-axis label")
    yLabel: Optional[str] = Field(None, max_length=100, description="Y-axis label")
    xType: Optional[AxisType] = Field(AxisType.CATEGORY, description="X-axis type")
    yMin: Optional[float] = Field(None, description="Y-axis minimum value")
    yMax: Optional[float] = Field(None, description="Y-axis maximum value")
    stacked: Optional[bool] = Field(False, description="Enable stacked chart mode")


class ChartDataPoint(BaseModel):
    """Single data point for chart."""
    label: str = Field(..., min_length=1, max_length=100)
    value: float

    @validator('value')
    def validate_value(cls, v):
        if v != v:  # NaN check
            raise ValueError("Value cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError("Value cannot be infinity")
        return float(v)


class ScatterDataPoint(BaseModel):
    """Data point for scatter/bubble charts."""
    x: float
    y: float
    r: Optional[float] = Field(None, ge=0, description="Bubble radius (for bubble charts)")
    label: Optional[str] = Field(None, max_length=100)

    @validator('x', 'y')
    def validate_coords(cls, v):
        if v != v:  # NaN check
            raise ValueError("Coordinate cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError("Coordinate cannot be infinity")
        return float(v)


class ChartGenerateRequest(BaseModel):
    """
    Main request model for Layout Service chart generation.

    Follows AI_SERVICE_CHART.md specification.
    """
    # Required fields
    prompt: str = Field(..., min_length=1, max_length=2000, description="Description of chart data")
    chartType: ChartType = Field(..., description="Type of chart to generate")
    presentationId: str = Field(..., min_length=1, max_length=100)
    slideId: str = Field(..., min_length=1, max_length=100)
    elementId: str = Field(..., min_length=1, max_length=100)

    # Context
    context: ChartContext = Field(..., description="Presentation context")

    # Constraints
    constraints: ChartConstraints = Field(..., description="Grid size constraints")

    # Optional configuration
    config: Optional[ChartConfig] = Field(None, description="Chart configuration")
    style: Optional[ChartStyle] = Field(None, description="Style options")
    axes: Optional[ChartAxes] = Field(None, description="Axis configuration")

    # Data
    data: Optional[List[Union[ChartDataPoint, ScatterDataPoint, Dict[str, Any]]]] = Field(
        None,
        description="Chart data points. If not provided and generateData=True, synthetic data will be generated."
    )
    generateData: bool = Field(False, description="Generate synthetic data if no data provided")

    @validator('data')
    def validate_data_length(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError("Maximum 100 data points allowed")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Show quarterly revenue growth for 2024",
                "chartType": "bar",
                "presentationId": "pres-123",
                "slideId": "slide-7",
                "elementId": "chart-1",
                "context": {
                    "presentationTitle": "Q4 Business Review",
                    "slideTitle": "Revenue Performance",
                    "slideIndex": 6,
                    "industry": "technology",
                    "timeFrame": "2024"
                },
                "constraints": {
                    "gridWidth": 8,
                    "gridHeight": 4
                },
                "style": {
                    "palette": "professional",
                    "showLegend": True,
                    "showDataLabels": True
                },
                "data": [
                    {"label": "Q1", "value": 125000},
                    {"label": "Q2", "value": 145000},
                    {"label": "Q3", "value": 162000},
                    {"label": "Q4", "value": 178000}
                ]
            }
        }


# ============================================
# RESPONSE MODELS
# ============================================

class DataRange(BaseModel):
    """Statistics about the data range."""
    min: float
    max: float
    average: float


class ChartMetadata(BaseModel):
    """Metadata about the generated chart."""
    chartType: ChartType
    dataPointCount: int
    datasetCount: int
    suggestedTitle: str
    dataRange: DataRange


class ChartInsights(BaseModel):
    """AI-generated insights about the chart data."""
    trend: Optional[TrendType] = Field(None, description="Overall trend direction")
    outliers: Optional[List[int]] = Field(None, description="Indices of outlier data points")
    highlights: Optional[List[str]] = Field(None, description="Notable observations")


class DatasetData(BaseModel):
    """Single dataset in chart data."""
    label: str
    data: List[float]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None


class RawChartData(BaseModel):
    """Raw chart data in Chart.js format."""
    labels: List[str]
    datasets: List[DatasetData]


class ChartConfiguration(BaseModel):
    """Complete Chart.js configuration object."""
    type: str
    data: Dict[str, Any]
    options: Dict[str, Any]
    plugins: Optional[List[Any]] = None


class ChartGenerateResponseData(BaseModel):
    """Successful response data."""
    generationId: str
    chartConfig: ChartConfiguration
    rawData: RawChartData
    metadata: ChartMetadata
    insights: Optional[ChartInsights] = None
    preview: Optional[Dict[str, str]] = Field(None, description="Base64 PNG preview if requested")


class ChartErrorResponse(BaseModel):
    """Error response details."""
    code: ChartErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    retryable: bool = False
    suggestion: Optional[str] = None


class ChartGenerateResponse(BaseModel):
    """
    Main response model for Layout Service chart generation.

    Follows AI_SERVICE_CHART.md specification.
    """
    success: bool
    data: Optional[ChartGenerateResponseData] = None
    error: Optional[ChartErrorResponse] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "generationId": "gen-abc123",
                    "chartConfig": {
                        "type": "bar",
                        "data": {
                            "labels": ["Q1", "Q2", "Q3", "Q4"],
                            "datasets": [{
                                "label": "Revenue",
                                "data": [125000, 145000, 162000, 178000],
                                "backgroundColor": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444"]
                            }]
                        },
                        "options": {
                            "responsive": True,
                            "maintainAspectRatio": False
                        }
                    },
                    "rawData": {
                        "labels": ["Q1", "Q2", "Q3", "Q4"],
                        "datasets": [{"label": "Revenue", "data": [125000, 145000, 162000, 178000]}]
                    },
                    "metadata": {
                        "chartType": "bar",
                        "dataPointCount": 4,
                        "datasetCount": 1,
                        "suggestedTitle": "Quarterly Revenue Growth",
                        "dataRange": {"min": 125000, "max": 178000, "average": 152500}
                    },
                    "insights": {
                        "trend": "increasing",
                        "outliers": [],
                        "highlights": ["42% growth from Q1 to Q4"]
                    }
                }
            }
        }
