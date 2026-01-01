"""
REST API server for Analytics Microservice v3.
FastAPI-based REST endpoints replacing WebSocket implementation.

v3.4.5 (2025-12-28):
- Monthly labels ("Jan '24") instead of "Period X"
- Blue gradient Key Insights panel with blue heading/bullets
- Chart layout padding and 15% Y-axis grace for data labels
- Realistic category labels (departments, companies, metrics)
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator, root_validator, ValidationError
import uvicorn

from settings import settings
from job_manager import JobManager
from storage import SupabaseStorage
from dependencies import AnalyticsDependencies
from agent import process_analytics_direct
from analytics_types import AnalyticsType, get_analytics_layout
from error_codes import (
    ErrorCode,
    ErrorCategory,
    AnalyticsError,
    validation_error,
    processing_error,
    resource_error,
    get_error_message
)
from chart_catalog import (
    get_chart_catalog,
    get_chartjs_types,
    get_chart_types_by_layout,
    get_chart_type_by_id,
    get_chart_type_summary,
    SupportedLayout,
    ChartLibrary
)
from synthetic_data_generator import SyntheticDataGenerator

# Layout Service Integration imports
from layout_service_models import (
    ChartGenerateRequest,
    ChartGenerateResponse,
    ChartGenerateResponseData,
    ChartConfiguration,
    ChartMetadata,
    ChartInsights,
    DataRange,
    RawChartData,
    DatasetData,
    ChartErrorResponse,
    ChartErrorCode as LayoutErrorCode,
    TrendType
)
from layout_service_constraints import (
    get_layout_size,
    get_data_limits,
    validate_grid_size,
    map_chart_type_to_internal,
    truncate_data_to_limits,
    get_minimum_grid_size,
    get_all_minimum_grid_sizes
)
from layout_service_palette import (
    get_palette_colors,
    get_internal_theme,
    get_chart_colors_for_type,
    get_available_palettes
)

# v3.5.0: Atomic Chart Routes
from api.atomic_routes import router as atomic_router

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Microservice v3",
    description="""
## Analytics Service v3.1.0 - Complete Chart.js Suite (20+ Chart Types)

Generate interactive Chart.js visualizations with comprehensive charting capabilities.

### Key Features
- ✅ **20+ Chart Types** (Chart.js with native types and plugins)
- ✅ **Comprehensive Data Validation** (2-50 data points, NaN/Infinity rejection)
- ✅ **Structured Error Responses** (retryable flags, fix suggestions)
- ✅ **Chart Type Discovery** (complete catalog with use cases)
- ✅ **Interactive Editor** (L02 charts)
- ✅ **Director Agent Integration** (Service Coordination endpoints)
- ✅ **Field Aliases** (chart_html, element_4, body - reduces Director mapping)

### Quick Start
```python
import requests

response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "pres-123",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth",
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000}
        ]
    }
)
```

### Documentation
- **Integration Guide**: [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md)
- **Chart Catalog**: [docs/CHART_TYPE_CATALOG.md](docs/CHART_TYPE_CATALOG.md)
- **Error Codes**: [docs/ERROR_CODES.md](docs/ERROR_CODES.md)
    """,
    version="3.5.0",
    contact={
        "name": "Analytics Service Team",
        "url": "https://github.com/Pramod-Potti-Krishnan/analytics-v3.0"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "https://analytics-v30-production.up.railway.app",
            "description": "Production server on Railway"
        },
        {
            "url": "http://localhost:8080",
            "description": "Local development server"
        }
    ],
    openapi_tags=[
        {
            "name": "Chart Discovery",
            "description": "Discover available chart types, constraints, and compatibility"
        },
        {
            "name": "Analytics Generation",
            "description": "Generate analytics slides with charts and insights (Director integration)"
        },
        {
            "name": "Interactive Editor",
            "description": "Edit chart data interactively (L02 charts)"
        },
        {
            "name": "Legacy",
            "description": "Deprecated endpoints (use Analytics Generation instead)"
        },
        {
            "name": "Health & Monitoring",
            "description": "Service health checks and statistics"
        },
        {
            "name": "Layout Service Integration",
            "description": "Chart generation for Layout Service with grid-based sizing constraints"
        },
        {
            "name": "Service Coordination",
            "description": "Director Agent coordination endpoints for Strawman Service integration (Phase 1-3)"
        },
        {
            "name": "Atomic Charts",
            "description": "Generate atomic chart elements with synthetic data for frontend positioning (v3.5.0)"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for Excel-like chart editor
app.mount("/static", StaticFiles(directory="static"), name="static")

# v3.5.0: Include atomic chart routes
app.include_router(atomic_router)


# Exception handlers
@app.exception_handler(AnalyticsError)
async def analytics_error_handler(request: Request, exc: AnalyticsError):
    """Handle structured analytics errors."""
    return JSONResponse(
        status_code=exc.http_status,
        content=exc.to_dict()
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with structured format."""
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Extract field and message
    field = ".".join(str(loc) for loc in first_error.get("loc", [])) if first_error.get("loc") else None
    message = first_error.get("msg", "Validation failed")

    # Create structured error response
    error = validation_error(
        code=ErrorCode.INVALID_DATA_POINTS,
        message=message,
        field=field,
        details={"validation_errors": errors},
        suggestion="Check the request data format and try again"
    )

    return JSONResponse(
        status_code=400,
        content=error.to_dict()
    )

# Initialize global managers
job_manager = JobManager(cleanup_hours=settings.JOB_CLEANUP_HOURS)
storage = SupabaseStorage(
    url=settings.SUPABASE_URL,
    key=settings.SUPABASE_KEY,
    bucket_name=settings.SUPABASE_BUCKET
)

# Initialize synthetic data generator
synthetic_generator = SyntheticDataGenerator()


# Request/Response Models

class ChartDataPoint(BaseModel):
    """Single chart data point with validation."""
    label: str = Field(..., min_length=1, max_length=100, description="Data point label (e.g., 'Q1 2024')")
    value: float = Field(..., description="Numeric value for the data point")

    @validator('label')
    def validate_label(cls, v):
        """Ensure label is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Label cannot be empty or whitespace")
        return v.strip()

    @validator('value')
    def validate_value(cls, v):
        """Ensure value is a valid finite number."""
        if not isinstance(v, (int, float)):
            raise ValueError(f"Value must be a number, got {type(v).__name__}")
        if v != v:  # NaN check
            raise ValueError("Value cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError("Value cannot be infinity")
        return float(v)


class ChartRequest(BaseModel):
    """Chart generation request."""
    content: str = Field(..., description="Description of analytics needed")
    title: str = Field(default="Analytics Chart", description="Chart title")
    data: list = Field(default=None, description="Optional user-provided data")
    chart_type: str = Field(default="bar_vertical", description="Chart type")
    theme: str = Field(default="professional", description="Color theme")

    class Config:
        schema_extra = {
            "example": {
                "content": "Show quarterly revenue growth for 2024",
                "title": "Q1-Q4 2024 Revenue",
                "chart_type": "bar_vertical",
                "theme": "professional"
            }
        }


class JobResponse(BaseModel):
    """Job creation response."""
    job_id: str
    status: str


class AnalyticsRequest(BaseModel):
    """Analytics generation request (Text Service compatible pattern)."""
    presentation_id: str = Field(..., min_length=1, description="Presentation UUID")
    slide_id: str = Field(..., min_length=1, description="Slide identifier")
    slide_number: int = Field(..., ge=1, description="Slide position in deck (1-indexed)")
    narrative: str = Field(..., min_length=1, max_length=2000, description="User's description of analytics needed")
    data: Optional[List[Union[ChartDataPoint, dict]]] = Field(None, min_items=1, max_items=50, description="Chart data: simple points [{label, value}] or complex structures (heatmap, boxplot, mixed). Optional if use_synthetic=true")
    context: dict = Field(default_factory=dict, description="Presentation context (theme, audience, etc.)")
    constraints: dict = Field(default_factory=dict, description="Layout constraints (dimensions, etc.)")
    chart_type: Optional[str] = Field(None, description="Optional chart type override (e.g., 'area', 'treemap', 'waterfall')")

    @validator('presentation_id', 'slide_id')
    def validate_ids(cls, v):
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty or whitespace")
        return v.strip()

    @validator('narrative')
    def validate_narrative(cls, v):
        """Ensure narrative is meaningful."""
        if not v or not v.strip():
            raise ValueError("Narrative cannot be empty or whitespace")
        return v.strip()

    @validator('data')
    def validate_data_consistency(cls, v):
        """Validate data array consistency - supports both simple and complex formats."""
        # Allow None for synthetic data generation (v3.8.0)
        if v is None:
            return v

        if len(v) < 1:
            raise ValueError("At least 1 data point required (or use use_synthetic=true for synthetic data)")
        if len(v) > 50:
            raise ValueError("Maximum 50 data points allowed to prevent performance issues")

        # For simple ChartDataPoint format, check for duplicate labels
        # For complex formats (dicts), skip validation as structure varies by chart type
        chartdata_points = [point for point in v if isinstance(point, ChartDataPoint)]
        if chartdata_points:
            labels = [point.label for point in chartdata_points]
            if len(labels) != len(set(labels)):
                raise ValueError("Duplicate labels found. Each data point must have a unique label")

        return v

    class Config:
        schema_extra = {
            "example": {
                "presentation_id": "pres-123",
                "slide_id": "slide-7",
                "slide_number": 7,
                "narrative": "Show quarterly revenue growth highlighting strong Q3-Q4 performance",
                "data": [
                    {"label": "Q1 2024", "value": 125000},
                    {"label": "Q2 2024", "value": 145000},
                    {"label": "Q3 2024", "value": 162000},
                    {"label": "Q4 2024", "value": 178000}
                ],
                "context": {
                    "theme": "professional",
                    "audience": "Board of Directors",
                    "slide_title": "Quarterly Revenue Growth",
                    "subtitle": "FY 2024 Performance"
                }
            }
        }


class SyntheticDataRequest(BaseModel):
    """Request for standalone synthetic data generation."""
    chart_type: str = Field(..., description="Chart type ID (e.g., 'line', 'd3_choropleth_usa')")
    narrative: Optional[str] = Field(None, max_length=2000, description="Narrative for context extraction")
    num_points: Optional[int] = Field(None, ge=1, le=50, description="Number of data points to generate")
    scenario: Optional[str] = Field(None, description="Business scenario name (e.g., 'revenue_growth')")

    @validator('chart_type')
    def validate_chart_type(cls, v):
        """Ensure chart type exists in catalog."""
        catalog = get_chart_catalog()
        valid_types = [ct.id for ct in catalog]
        if v not in valid_types:
            raise ValueError(f"Invalid chart type: {v}. Valid types: {', '.join(valid_types[:5])}...")
        return v


class PreviewRequest(BaseModel):
    """Request for preview mode (chart with synthetic data)."""
    narrative: Optional[str] = Field(None, max_length=2000, description="Narrative for context extraction")
    num_points: Optional[int] = Field(None, ge=1, le=50, description="Number of data points to generate")


class BatchAnalyticsRequest(BaseModel):
    """Batch analytics generation request."""
    presentation_id: str
    slides: list = Field(..., description="List of analytics requests")


# ========================================
# SERVICE COORDINATION MODELS (Phase 1-3)
# Director Agent Strawman Service Integration
# ========================================

class SlideContent(BaseModel):
    """Slide content for service coordination."""
    title: str = Field(..., description="Slide title")
    topics: List[str] = Field(default_factory=list, description="Slide topics/bullet points")
    topic_count: int = Field(default=0, description="Number of topics")


class ContentHints(BaseModel):
    """Content hints for service routing."""
    has_numbers: bool = Field(default=False, description="Content contains numerical data")
    is_comparison: bool = Field(default=False, description="Content is comparing items")
    is_time_based: bool = Field(default=False, description="Content is time-series based")
    detected_keywords: List[str] = Field(default_factory=list, description="Keywords detected in content")


class AvailableSpace(BaseModel):
    """Available space constraints from layout."""
    width: int = Field(..., description="Available width in pixels")
    height: int = Field(..., description="Available height in pixels")
    sub_zones: Optional[List[Dict[str, Any]]] = Field(None, description="Sub-zone dimensions if multi-column")


class CanHandleRequest(BaseModel):
    """Phase 2: Request for content negotiation."""
    slide_content: SlideContent = Field(..., description="Slide content to evaluate")
    content_hints: ContentHints = Field(default_factory=ContentHints, description="Content analysis hints")
    available_space: Optional[AvailableSpace] = Field(None, description="Layout space constraints")

    class Config:
        schema_extra = {
            "example": {
                "slide_content": {
                    "title": "Q4 Revenue Analysis",
                    "topics": ["Revenue grew 15%", "New markets contributed 30%", "Cost reduction achieved"],
                    "topic_count": 3
                },
                "content_hints": {
                    "has_numbers": True,
                    "is_comparison": False,
                    "is_time_based": False,
                    "detected_keywords": ["revenue", "growth", "percentage"]
                },
                "available_space": {
                    "width": 1800,
                    "height": 750
                }
            }
        }


class SpaceUtilization(BaseModel):
    """Space utilization estimate."""
    fits_well: bool = Field(..., description="Content fits well in available space")
    estimated_fill_percent: int = Field(..., ge=0, le=100, description="Estimated space fill percentage")


class CanHandleResponse(BaseModel):
    """Phase 2: Response for content negotiation."""
    can_handle: bool = Field(..., description="Whether this service can handle the content")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    reason: str = Field(..., description="Explanation for the decision")
    suggested_approach: str = Field(..., description="Suggested approach (chart/text)")
    space_utilization: Optional[SpaceUtilization] = Field(None, description="Space utilization estimate")


class RecommendChartRequest(BaseModel):
    """Phase 3: Request for chart type recommendation."""
    slide_content: SlideContent = Field(..., description="Slide content to evaluate")
    detected_patterns: Optional[List[str]] = Field(None, description="Detected data patterns (time_series, comparison, composition, etc.)")

    class Config:
        schema_extra = {
            "example": {
                "slide_content": {
                    "title": "Revenue Trend",
                    "topics": ["Show revenue growth over 4 quarters"],
                    "topic_count": 1
                },
                "detected_patterns": ["time_series"]
            }
        }


class ChartRecommendation(BaseModel):
    """Single chart type recommendation."""
    chart_type: str = Field(..., description="Recommended chart type ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reason: str = Field(..., description="Reason for this recommendation")


class RecommendChartResponse(BaseModel):
    """Phase 3: Response with chart type recommendations."""
    recommended_charts: List[ChartRecommendation] = Field(..., description="Ranked chart recommendations")


async def process_chart_job(job_id: str, request_data: Dict[str, Any]):
    """
    Process chart generation job asynchronously.

    Args:
        job_id: Unique job identifier
        request_data: Chart generation parameters
    """
    try:
        # Create dependencies with job manager and storage
        deps = AnalyticsDependencies(
            job_manager=job_manager,
            job_id=job_id,
            storage=storage
        )

        # Process analytics request
        result = await process_analytics_direct(request_data, deps)

        if result.get("success"):
            # Complete job with results
            job_manager.complete_job(job_id, result)
        else:
            # Fail job
            error = result.get("error", "Unknown error")
            job_manager.fail_job(job_id, error)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        job_manager.fail_job(job_id, str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    logger.info("Analytics Microservice v3 starting...")

    # Create Supabase bucket if needed
    if storage.create_bucket_if_not_exists():
        logger.info("Supabase Storage ready")
    else:
        logger.warning("Failed to initialize Supabase Storage")

    logger.info(f"REST API ready on port {settings.API_PORT}")


@app.get("/")
async def root():
    """Service information endpoint."""
    return {
        "service": "Analytics Microservice v3",
        "version": "3.1.6",
        "status": "running",
        "api_type": "REST",
        "endpoints": {
            "generate": "POST /generate (⚠️ Deprecated - Use /api/v1/analytics/{layout}/{type})",
            "status": "GET /status/{job_id}",
            "health": "GET /health",
            "stats": "GET /stats",
            "chart_catalog": "GET /api/v1/chart-types (Discovery)",
            "chartjs_types": "GET /api/v1/chart-types/chartjs",
            "apexcharts_types": "GET /api/v1/chart-types/apexcharts",
            "chart_type_detail": "GET /api/v1/chart-types/{chart_id}",
            "layout_compatibility": "GET /api/v1/layouts/{layout}/chart-types",
            "analytics": "POST /api/v1/analytics/{layout}/{type} (Director integration)",
            "batch": "POST /api/v1/analytics/batch",
            "chart_editor": "POST /api/charts/update-data (Interactive editing)"
        },
        "supported_analytics": [t.value for t in AnalyticsType],
        "supported_layouts": ["L01", "L02", "L03"],
        "chart_libraries": ["Chart.js (L02)", "ApexCharts (L01, L03)"],
        "features": {
            "data_validation": "✅ Comprehensive input validation",
            "structured_errors": "✅ Standardized error responses",
            "chart_discovery": "✅ Complete chart type catalog",
            "interactive_editing": "✅ Chart data editor (L02)",
            "director_integration": "✅ Text Service compatible API"
        }
    }


@app.get("/health", tags=["Health & Monitoring"])
async def health_check():
    """
    Health check endpoint.

    Returns service health status and job statistics.
    """
    return {
        "status": "healthy",
        "service": "analytics_microservice_v3",
        "jobs": job_manager.get_stats()
    }


@app.get("/stats", tags=["Health & Monitoring"])
async def get_stats():
    """
    Get job statistics.

    Returns detailed job statistics and storage configuration.
    """
    return {
        "job_stats": job_manager.get_stats(),
        "storage_bucket": settings.SUPABASE_BUCKET
    }


# ========================================
# SERVICE COORDINATION ENDPOINTS (Phase 1-3)
# Director Agent Strawman Service Integration
# ========================================

@app.get("/capabilities", tags=["Service Coordination"])
async def get_capabilities():
    """
    **Phase 1: Service Capabilities Endpoint**

    Returns complete service description for Director Agent's Strawman Service.
    This endpoint enables intelligent service routing by exposing what this
    service can handle, what it handles well, and what patterns it recognizes.

    Returns:
        ServiceCapabilities: Complete service metadata including:
        - Supported chart types and libraries
        - Content signals (what we handle well/poorly)
        - Pattern detection capabilities
        - Chart recommendations by pattern type
        - Available endpoints
    """
    catalog = get_chart_catalog()

    return {
        "service": "analytics-service",
        "version": "3.1.6",
        "status": "healthy",

        "capabilities": {
            "slide_types": ["chart", "visualization", "data_display"],
            "chart_types": [ct.id for ct in catalog],
            "supported_layouts": ["L01", "L02", "L03"],
            "supports_themes": True,
            "can_generate_data": True,
            "chart_libraries": ["Chart.js", "D3.js"]
        },

        # v3.1.0: Field aliases for Director convenience (reduces mapping burden)
        "response_format": {
            "content_fields": {
                "element_3": "Chart HTML (original field)",
                "element_2": "Observations/insights HTML (original field)",
                "chart_html": "Alias for element_3 (for C3-chart, V2-chart-text)",
                "element_4": "Alias for element_3 (for L02 SPEC compliance)",
                "body": "Alias for element_2 (for V2-chart-text)"
            },
            "field_mapping_guide": {
                "C3-chart": {"chart_html": "element_3"},
                "V2-chart-text": {"chart_html": "element_3", "body": "element_2"},
                "L02": {"element_4": "element_3", "element_2": "element_2"}
            },
            "note": "Director can use aliases directly without mapping. Original fields kept for backward compatibility."
        },

        "content_signals": {
            "handles_well": [
                "numerical_data", "time_series", "comparisons_with_numbers",
                "distributions", "trends", "percentages"
            ],
            "handles_poorly": [
                "pure_text_content", "bullet_points", "processes_without_data"
            ],
            "keywords": [
                "chart", "graph", "trend", "over time", "percentage",
                "growth", "decline", "revenue", "sales", "distribution",
                "metrics", "KPI", "data", "numbers", "statistics"
            ],
            "pattern_detection": {
                "time_series": ["over time", "by quarter", "by month", "trend", "growth", "quarterly", "monthly", "yearly"],
                "comparison": ["vs", "compared to", "difference between", "versus", "compare"],
                "composition": ["breakdown", "distribution", "share of", "percentage", "proportion", "parts of"]
            }
        },

        "chart_recommendations": {
            "time_series": ["line", "area"],
            "comparison": ["bar_vertical", "bar_horizontal", "bar_grouped"],
            "composition": ["pie", "doughnut", "d3_treemap"],
            "correlation": ["scatter", "bubble"],
            "hierarchy": ["d3_treemap", "d3_sunburst"],
            "flow": ["d3_sankey"],
            "geographic": ["d3_choropleth_usa"]
        },

        "endpoints": {
            "capabilities": "GET /capabilities",
            "generate": "POST /api/v1/analytics/{layout}/{analytics_type}",
            "can_handle": "POST /api/v1/analytics/can-handle",
            "recommend_chart": "POST /api/v1/analytics/recommend-chart",
            "chart_types": "GET /api/v1/chart-types",
            "synthetic_data": "POST /api/v1/synthetic/generate"
        }
    }


@app.post("/api/v1/analytics/can-handle",
          response_model=CanHandleResponse,
          tags=["Service Coordination"])
async def can_handle(request: CanHandleRequest):
    """
    **Phase 2: Content Negotiation Endpoint**

    Answers: "Can Analytics Service handle this content?"
    Returns a confidence score and reasoning to enable intelligent service routing.

    The Strawman Service queries all content services with the same request,
    and routes to the service with highest confidence that fits the space.

    Args:
        request: CanHandleRequest with slide content, hints, and space constraints

    Returns:
        CanHandleResponse with:
        - can_handle: Whether we can process this content
        - confidence: Score from 0.0 to 1.0
        - reason: Explanation of the decision
        - suggested_approach: "chart" or "text"
        - space_utilization: How well content fits available space
    """
    content = request.slide_content
    hints = request.content_hints

    # Calculate confidence based on content signals
    confidence = 0.0
    reasons = []

    # Check for numerical data signals
    if hints.has_numbers:
        confidence += 0.3
        reasons.append("contains numerical data")

    # Check for time-based data
    if hints.is_time_based:
        confidence += 0.25
        reasons.append("time series detected")

    # Check for comparison signals
    if hints.is_comparison:
        confidence += 0.2
        reasons.append("comparison data")

    # Keyword matching against our capabilities
    chart_keywords = ["chart", "graph", "trend", "growth", "revenue", "percentage",
                      "distribution", "over time", "metrics", "KPI", "data",
                      "numbers", "statistics", "sales", "performance"]
    matched_keywords = []
    for kw in hints.detected_keywords:
        if any(ck in kw.lower() for ck in chart_keywords):
            matched_keywords.append(kw)
    if matched_keywords:
        confidence += min(0.25, len(matched_keywords) * 0.08)
        reasons.append(f"keywords matched: {matched_keywords[:3]}")

    # Check topic content for numbers/percentages
    numeric_topics = sum(1 for t in content.topics
                         if any(c.isdigit() for c in t) or '%' in t or '$' in t)
    if numeric_topics > 0:
        confidence += min(0.2, numeric_topics * 0.07)
        reasons.append(f"{numeric_topics} topics with numbers/percentages")

    # Check title for chart-related keywords
    title_lower = content.title.lower()
    title_signals = ["chart", "graph", "trend", "growth", "revenue", "sales",
                     "performance", "metrics", "analysis", "data", "statistics"]
    if any(sig in title_lower for sig in title_signals):
        confidence += 0.1
        reasons.append("title suggests data visualization")

    # Normalize confidence to 0-1 range
    confidence = min(1.0, max(0.0, confidence))

    # Determine if we can handle it (threshold: 0.4)
    can_handle_result = confidence >= 0.4

    # Suggest approach
    suggested_approach = "chart" if can_handle_result else "text"

    # Space utilization (if space provided)
    space_util = None
    if request.available_space:
        space_util = SpaceUtilization(
            fits_well=True,  # Charts scale to fit available space
            estimated_fill_percent=85 if can_handle_result else 0
        )

    return CanHandleResponse(
        can_handle=can_handle_result,
        confidence=round(confidence, 2),
        reason=" | ".join(reasons) if reasons else "No chart signals detected",
        suggested_approach=suggested_approach,
        space_utilization=space_util
    )


@app.post("/api/v1/analytics/recommend-chart",
          response_model=RecommendChartResponse,
          tags=["Service Coordination"])
async def recommend_chart(request: RecommendChartRequest):
    """
    **Phase 3: Chart Type Recommendation Endpoint**

    Recommends the best chart types based on content and detected patterns.
    Used after /can-handle confirms this service should handle the content.

    The Strawman Service uses this to get specific chart type recommendations
    that fit the layout constraints and match the data characteristics.

    Args:
        request: RecommendChartRequest with slide content and detected patterns

    Returns:
        RecommendChartResponse with ranked chart recommendations (top 5)
    """
    content = request.slide_content
    patterns = request.detected_patterns or []

    recommendations = []

    # Pattern-based recommendations mapping
    pattern_map = {
        "time_series": [
            ("line", 0.95, "Time series data best shown as line chart"),
            ("area", 0.80, "Area chart also effective for trends over time")
        ],
        "comparison": [
            ("bar_vertical", 0.90, "Vertical bars ideal for category comparison"),
            ("bar_horizontal", 0.85, "Horizontal bars work well for long category labels"),
            ("bar_grouped", 0.75, "Grouped bars for multi-series comparison")
        ],
        "composition": [
            ("pie", 0.90, "Pie chart shows parts of a whole clearly"),
            ("doughnut", 0.85, "Doughnut provides clean composition view"),
            ("d3_treemap", 0.70, "Treemap for hierarchical composition data")
        ],
        "correlation": [
            ("scatter", 0.90, "Scatter plot reveals correlations between variables"),
            ("bubble", 0.80, "Bubble chart adds third dimension to correlation")
        ],
        "hierarchy": [
            ("d3_treemap", 0.90, "Treemap visualizes hierarchical data effectively"),
            ("d3_sunburst", 0.85, "Sunburst for nested hierarchies with drill-down")
        ],
        "flow": [
            ("d3_sankey", 0.90, "Sankey diagram shows flow between nodes")
        ],
        "geographic": [
            ("d3_choropleth_usa", 0.95, "Choropleth map for US state-level data")
        ],
        "distribution": [
            ("bar_vertical", 0.85, "Bar chart shows distribution clearly"),
            ("pie", 0.75, "Pie chart for percentage distribution")
        ]
    }

    # Add recommendations based on detected patterns
    for pattern in patterns:
        if pattern in pattern_map:
            for chart_type, confidence, reason in pattern_map[pattern]:
                # Avoid duplicates
                if not any(r.chart_type == chart_type for r in recommendations):
                    recommendations.append(ChartRecommendation(
                        chart_type=chart_type,
                        confidence=confidence,
                        reason=reason
                    ))

    # Keyword-based fallback if no patterns provided or matched
    if not recommendations:
        title_lower = content.title.lower()
        topics_text = " ".join(content.topics).lower()
        combined = f"{title_lower} {topics_text}"

        # Detect patterns from text content
        if any(kw in combined for kw in ["trend", "over time", "growth", "monthly", "quarterly", "yearly", "timeline"]):
            recommendations.append(ChartRecommendation(
                chart_type="line",
                confidence=0.85,
                reason="Time-related keywords detected in content"
            ))
            recommendations.append(ChartRecommendation(
                chart_type="area",
                confidence=0.70,
                reason="Area chart as alternative for time trends"
            ))
        elif any(kw in combined for kw in ["compare", "vs", "versus", "difference", "against"]):
            recommendations.append(ChartRecommendation(
                chart_type="bar_vertical",
                confidence=0.85,
                reason="Comparison keywords detected in content"
            ))
            recommendations.append(ChartRecommendation(
                chart_type="bar_grouped",
                confidence=0.70,
                reason="Grouped bar for multi-item comparison"
            ))
        elif any(kw in combined for kw in ["share", "percentage", "breakdown", "distribution", "proportion"]):
            recommendations.append(ChartRecommendation(
                chart_type="pie",
                confidence=0.85,
                reason="Composition keywords detected in content"
            ))
            recommendations.append(ChartRecommendation(
                chart_type="doughnut",
                confidence=0.75,
                reason="Doughnut as alternative for composition"
            ))
        elif any(kw in combined for kw in ["map", "state", "region", "geographic", "location"]):
            recommendations.append(ChartRecommendation(
                chart_type="d3_choropleth_usa",
                confidence=0.85,
                reason="Geographic keywords detected in content"
            ))
        else:
            # Default recommendation for general data
            recommendations.append(ChartRecommendation(
                chart_type="bar_vertical",
                confidence=0.60,
                reason="Default recommendation for general numerical data"
            ))
            recommendations.append(ChartRecommendation(
                chart_type="line",
                confidence=0.50,
                reason="Line chart as versatile alternative"
            ))

    # Sort by confidence (highest first)
    recommendations.sort(key=lambda x: x.confidence, reverse=True)

    return RecommendChartResponse(
        recommended_charts=recommendations[:5]  # Return top 5
    )


# ========================================
# CHART TYPE DISCOVERY ENDPOINTS
# ========================================

@app.get("/api/v1/chart-types", tags=["Chart Discovery"])
async def get_all_chart_types():
    """
    Get complete chart type catalog.

    Returns comprehensive information about all supported chart types,
    including constraints, use cases, and integration details.

    Returns:
        Complete chart type catalog with 13+ chart types
    """
    catalog = get_chart_catalog()
    summary = get_chart_type_summary()

    return {
        "success": True,
        "summary": summary,
        "chart_types": [ct.dict() for ct in catalog]
    }


@app.get("/api/v1/chart-types/chartjs", tags=["Chart Discovery"])
async def get_chartjs_chart_types():
    """
    Get Chart.js chart types (L02 layout compatible).

    Returns:
        Chart.js-based chart types for Director integration
    """
    charts = get_chartjs_types()

    return {
        "success": True,
        "library": ChartLibrary.CHARTJS.value,
        "layouts": [SupportedLayout.L02.value],
        "count": len(charts),
        "chart_types": [ct.dict() for ct in charts]
    }


@app.get("/api/v1/chart-types/{chart_id}", tags=["Chart Discovery"])
async def get_specific_chart_type(chart_id: str):
    """
    Get detailed information about a specific chart type.

    Args:
        chart_id: Chart type identifier (e.g., 'line', 'bar_vertical', 'pie')

    Returns:
        Detailed chart type specification
    """
    chart_type = get_chart_type_by_id(chart_id)

    if not chart_type:
        raise resource_error(
            code=ErrorCode.INVALID_CHART_TYPE,
            message=f"Chart type '{chart_id}' not found",
            details={"provided": chart_id}
        )

    return {
        "success": True,
        "chart_type": chart_type.dict()
    }


@app.get("/api/v1/layouts/{layout}/chart-types", tags=["Chart Discovery"])
async def get_chart_types_for_layout(layout: str):
    """
    Get chart types compatible with a specific layout.

    Args:
        layout: Layout type (L01, L02, L03)

    Returns:
        Chart types compatible with the specified layout
    """
    # Validate layout
    try:
        layout_enum = SupportedLayout(layout)
    except ValueError:
        raise validation_error(
            code=ErrorCode.INVALID_LAYOUT,
            message=f"Invalid layout: {layout}",
            field="layout",
            details={
                "provided": layout,
                "supported": [l.value for l in SupportedLayout]
            },
            suggestion=f"Use one of: {', '.join(l.value for l in SupportedLayout)}"
        )

    # Get compatible chart types
    charts = get_chart_types_by_layout(layout_enum)

    # Determine library used for this layout
    library = ChartLibrary.CHARTJS if layout == "L02" else ChartLibrary.APEXCHARTS

    return {
        "success": True,
        "layout": layout,
        "library": library.value,
        "count": len(charts),
        "chart_types": [ct.dict() for ct in charts]
    }


@app.post("/generate", tags=["Legacy"], response_model=JobResponse, deprecated=True)
async def generate_chart(request: ChartRequest):
    """
    ⚠️ **DEPRECATED** - Submit a chart generation request.

    **This endpoint is deprecated and will be removed in v4.0.0.**

    **Migration Guide:**
    - Use `POST /api/v1/analytics/{layout}/{analytics_type}` instead
    - New endpoint provides:
      - Text Service compatibility for Director integration
      - Synchronous responses (no job polling needed)
      - Structured error responses
      - Better data validation
      - Chart type discovery via `/api/v1/chart-types`

    **Example Migration:**
    ```
    # Old (Deprecated):
    POST /generate
    {
      "content": "Show quarterly revenue",
      "title": "Revenue Chart",
      "chart_type": "bar_vertical"
    }

    # New (Recommended):
    POST /api/v1/analytics/L02/revenue_over_time
    {
      "presentation_id": "pres-123",
      "slide_id": "slide-1",
      "slide_number": 1,
      "narrative": "Show quarterly revenue",
      "data": [
        {"label": "Q1", "value": 125000},
        {"label": "Q2", "value": 145000}
      ]
    }
    ```

    Returns job_id for polling status.
    """
    # Log deprecation warning
    logger.warning(
        f"⚠️ DEPRECATED ENDPOINT USED: /generate - "
        f"Client should migrate to /api/v1/analytics/{{layout}}/{{analytics_type}}. "
        f"Request: {request.title}"
    )

    try:
        # Convert request to dict
        request_data = request.dict()

        # Create job
        job_id = job_manager.create_job(request_data)

        # Start async processing
        asyncio.create_task(process_chart_job(job_id, request_data))

        logger.info(f"Created job {job_id} for chart: {request.title}")

        return JobResponse(
            job_id=job_id,
            status="processing"
        )

    except Exception as e:
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}", tags=["Legacy"])
async def get_job_status(job_id: str):
    """
    Get status and results of a chart generation job.

    Args:
        job_id: Job identifier returned from /generate

    Returns:
        Job status, progress, and results (if completed)
    """
    status = job_manager.get_job_status(job_id)

    if not status:
        raise resource_error(
            code=ErrorCode.JOB_NOT_FOUND,
            message=f"Job {job_id} not found",
            details={"job_id": job_id}
        )

    return status


@app.post("/api/v1/synthetic/generate", tags=["Synthetic Data Generation"])
async def generate_synthetic_data(request: SyntheticDataRequest):
    """
    Generate synthetic data for any chart type.

    This endpoint generates realistic, context-aware synthetic data without requiring
    Director integration. Useful for testing, development, and preview mode.

    Args:
        request: Synthetic data generation request

    Returns:
        Generated data array ready for chart rendering

    Example:
        ```json
        {
            "chart_type": "line",
            "narrative": "Show quarterly revenue growth for 2024",
            "scenario": "revenue_growth"
        }
        ```

    Response:
        ```json
        {
            "success": true,
            "data": [
                {"label": "Q1 2024", "value": 125000},
                {"label": "Q2 2024", "value": 145000},
                {"label": "Q3 2024", "value": 195000},
                {"label": "Q4 2024", "value": 220000}
            ],
            "metadata": {
                "chart_type": "line",
                "num_points": 4,
                "scenario": "revenue_growth",
                "generated_at": "2025-11-25T..."
            }
        }
        ```
    """
    try:
        from datetime import datetime

        # Generate synthetic data
        data = synthetic_generator.generate(
            chart_type=request.chart_type,
            narrative=request.narrative,
            num_points=request.num_points,
            scenario=request.scenario
        )

        return {
            "success": True,
            "data": data,
            "metadata": {
                "chart_type": request.chart_type,
                "num_points": len(data),
                "scenario": request.scenario,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }
        }

    except ValueError as e:
        # Validation errors from generator
        raise validation_error(
            code=ErrorCode.INVALID_DATA_POINTS,
            message=str(e),
            field="data_generation",
            details={"error": str(e)},
            suggestion="Check chart type and parameters"
        )
    except Exception as e:
        logger.error(f"Synthetic data generation failed: {e}", exc_info=True)
        raise processing_error(
            code=ErrorCode.CHART_GENERATION_FAILED,
            message=f"Failed to generate synthetic data: {str(e)}",
            details={"exception_type": type(e).__name__},
            retryable=True
        )


@app.post("/api/v1/preview/{chart_type}", tags=["Synthetic Data Generation"])
async def preview_chart_type(
    chart_type: str,
    request: Optional[PreviewRequest] = None
):
    """
    Generate preview slide for a chart type using synthetic data.

    This endpoint creates a complete analytics slide with synthetic data,
    allowing you to preview chart types without Director integration.

    Args:
        chart_type: Chart type ID (e.g., 'line', 'd3_choropleth_usa')
        request: Optional preview parameters

    Returns:
        Complete slide content with chart and observations

    Example:
        ```
        POST /api/v1/preview/d3_choropleth_usa
        {
            "narrative": "Show sales by top 10 states"
        }
        ```
    """
    try:
        from datetime import datetime
        from agent import generate_l02_analytics

        # Use request if provided, otherwise create default
        narrative = request.narrative if request else f"Preview of {chart_type} chart"
        num_points = request.num_points if request else None

        # Generate synthetic data
        data = synthetic_generator.generate(
            chart_type=chart_type,
            narrative=narrative,
            num_points=num_points
        )

        # Create analytics request dict
        request_dict = {
            "presentation_id": "preview",
            "slide_id": f"preview-{chart_type}",
            "slide_number": 1,
            "narrative": narrative,
            "data": data,
            "chart_type": chart_type,
            "context": {
                "theme": "professional",
                "mode": "preview"
            },
            "analytics_type": "preview"
        }

        # Generate slide using existing pipeline
        result = await generate_l02_analytics(request_dict)

        # Add synthetic data metadata
        result["metadata"]["synthetic_data_used"] = True
        result["metadata"]["preview_mode"] = True

        return {
            "content": result.get("content", {}),
            "metadata": result.get("metadata", {})
        }

    except ValueError as e:
        raise validation_error(
            code=ErrorCode.INVALID_CHART_TYPE,
            message=f"Invalid chart type: {chart_type}",
            field="chart_type",
            details={"error": str(e)},
            suggestion="Check /api/v1/charts/catalog for valid chart types"
        )
    except Exception as e:
        logger.error(f"Preview generation failed: {e}", exc_info=True)
        raise processing_error(
            code=ErrorCode.CHART_GENERATION_FAILED,
            message=f"Failed to generate preview: {str(e)}",
            details={"chart_type": chart_type},
            retryable=True
        )


@app.post("/api/v1/analytics/{layout}/{analytics_type}", tags=["Analytics Generation"])
async def generate_analytics_slide(
    layout: str,
    analytics_type: str,
    request: AnalyticsRequest,
    use_synthetic: bool = False
):
    """
    Generate analytics slide content (Text Service compatible).

    This endpoint matches the Text Service API pattern for seamless Director integration.
    Returns complete slide content ready for Layout Builder.

    For L02 layout: Returns 2 HTML fields (element_3 chart, element_2 observations).
    For L01/L03 layouts: Returns standard content fields.

    Args:
        layout: Layout type (L01, L02, L03)
        analytics_type: Analytics visualization type (revenue_over_time, market_share, etc.)
        request: Analytics generation request
        use_synthetic: Optional flag to generate synthetic data instead of using request.data

    Returns:
        Slide content with chart HTML and insights

    New Features (v3.8.0):
        - Optional synthetic data generation via `use_synthetic=true` query parameter
        - Automatic fallback to synthetic data if request.data is empty
        - Metadata tracks whether synthetic data was used

    Example with synthetic data:
        ```
        POST /api/v1/analytics/L02/revenue_over_time?use_synthetic=true
        {
            "presentation_id": "test-123",
            "slide_id": "slide-1",
            "slide_number": 1,
            "narrative": "Show quarterly revenue growth for 2024"
            // No data field needed - will be generated synthetically
        }
        ```
    """
    try:
        # Validate analytics type
        try:
            atype = AnalyticsType(analytics_type)
        except ValueError:
            raise validation_error(
                code=ErrorCode.INVALID_ANALYTICS_TYPE,
                message=f"Invalid analytics type: {analytics_type}",
                field="analytics_type",
                details={
                    "provided": analytics_type,
                    "supported": [t.value for t in AnalyticsType]
                },
                suggestion=f"Use one of: {', '.join(t.value for t in AnalyticsType)}"
            )

        # L02 uses new Chart.js-based generator (Director integration)
        if layout == "L02":
            from agent import generate_l02_analytics

            # Check if we should use synthetic data
            synthetic_data_used = False

            # Pass analytics_type explicitly in request dict (v3.1.4 hotfix)
            request_dict = request.dict()
            request_dict['analytics_type'] = analytics_type

            # Generate synthetic data if requested or if data is empty
            if use_synthetic or not request_dict.get('data') or len(request_dict.get('data', [])) == 0:
                logger.info(f"Generating synthetic data for L02 analytics: {analytics_type}")

                # Generate synthetic data
                synthetic_data = synthetic_generator.generate(
                    chart_type=request.chart_type or analytics_type,
                    narrative=request.narrative,
                    num_points=None  # Auto-determine from narrative/chart type
                )

                # Replace data in request
                request_dict['data'] = synthetic_data
                synthetic_data_used = True

                logger.info(f"Generated {len(synthetic_data)} synthetic data points")
            else:
                logger.info(f"Using Director-provided data ({len(request_dict.get('data', []))} points)")

            # Generate slide
            result = await generate_l02_analytics(request_dict)

            # Add synthetic data metadata
            result["metadata"]["synthetic_data_used"] = synthetic_data_used
            result["metadata"]["data_source"] = "synthetic" if synthetic_data_used else "director"

            # Return Text Service compatible response
            # For L02: content contains element_3 (chart) and element_2 (observations)
            return {
                "content": result.get("content", {}),
                "metadata": result.get("metadata", {})
            }

        # L01/L03 use existing ApexCharts-based generator
        else:
            from agent import process_analytics_slide

            logger.info(f"Generating {layout} analytics: {analytics_type}")

            result = await process_analytics_slide(
                analytics_type=analytics_type,
                layout=layout,
                request_data=request.dict(),
                storage=storage
            )

            if not result.get("success"):
                error_msg = result.get("error", "Analytics generation failed")
                raise processing_error(
                    code=ErrorCode.CHART_GENERATION_FAILED,
                    message=error_msg,
                    details={"analytics_type": analytics_type, "layout": layout},
                    retryable=True
                )

            # Return Text Service compatible response
            return {
                "content": result.get("content", {}),
                "metadata": result.get("metadata", {})
            }

    except AnalyticsError:
        raise
    except Exception as e:
        logger.error(f"Analytics generation failed: {e}", exc_info=True)
        raise processing_error(
            code=ErrorCode.CHART_GENERATION_FAILED,
            message=str(e),
            details={"exception_type": type(e).__name__},
            retryable=False
        )


@app.post("/api/v1/analytics/batch", tags=["Analytics Generation"])
async def generate_analytics_batch(request: BatchAnalyticsRequest):
    """
    Generate multiple analytics slides in batch (parallel processing).

    Args:
        request: Batch request with multiple slide specifications

    Returns:
        List of slide contents with charts and insights
    """
    try:
        from agent import process_analytics_slide

        results = []

        # Process slides in parallel
        tasks = []
        for slide_req in request.slides:
            analytics_type = slide_req.get("analytics_type")
            layout = slide_req.get("layout") or get_analytics_layout(analytics_type)

            task = process_analytics_slide(
                analytics_type=analytics_type,
                layout=layout,
                request_data=slide_req,
                storage=storage
            )
            tasks.append(task)

        # Wait for all to complete
        import asyncio
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Format results
        for i, result in enumerate(completed_results):
            if isinstance(result, Exception):
                results.append({
                    "success": False,
                    "slide_id": request.slides[i].get("slide_id"),
                    "error": str(result)
                })
            else:
                results.append({
                    "success": result.get("success", False),
                    "slide_id": request.slides[i].get("slide_id"),
                    "content": result.get("content", {}),
                    "metadata": result.get("metadata", {})
                })

        return {
            "presentation_id": request.presentation_id,
            "slides": results,
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success"))
        }

    except Exception as e:
        logger.error(f"Batch analytics generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# INTERACTIVE CHART EDITOR API
# ========================================

class DatasetSchema(BaseModel):
    """Single dataset in multi-series format."""
    label: str = Field(..., min_length=1, description="Series name/label")
    data: List[float] = Field(..., min_items=2, max_items=50, description="Data points for this series")

    @validator('data')
    def validate_data(cls, v):
        """Validate data array contains valid numbers."""
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Data point at index {i} must be a number, got {type(val).__name__}")
            if val != val:  # NaN check
                raise ValueError(f"Data point at index {i} cannot be NaN")
            if abs(val) == float('inf'):
                raise ValueError(f"Data point at index {i} cannot be infinity")
        return [float(val) for val in v]


class ScatterBubbleDataPoint(BaseModel):
    """Single data point for scatter/bubble charts."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    r: Optional[float] = Field(default=None, description="Bubble radius (bubble charts only)")
    label: str = Field(..., min_length=1, description="Point label")

    @validator('x', 'y', 'r')
    def validate_numeric(cls, v, values, **kwargs):
        """Validate numeric values."""
        # Get field name from kwargs (Pydantic V2 compatibility)
        field_name = kwargs.get('field', {}).get('name', 'value')

        if v is None:
            # r is optional, x and y are required (handled by Field)
            return v

        if v != v:  # NaN check
            raise ValueError(f"{field_name} cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError(f"{field_name} cannot be infinity")

        return v


class ChartDataUpdate(BaseModel):
    """Request to update chart data - supports simple, multi-series, and scatter/bubble formats."""
    chart_id: str = Field(..., min_length=1, description="Chart identifier")
    presentation_id: str = Field(..., min_length=1, description="Presentation UUID")
    chart_type: str = Field(..., description="Chart type (e.g., 'scatter', 'bubble', 'bar', etc.)")

    # Simple charts: labels + values
    labels: Optional[List[str]] = Field(default=None, min_items=2, max_items=50, description="X-axis labels (simple charts)")
    values: Optional[List[float]] = Field(default=None, min_items=2, max_items=50, description="Y-axis values (simple charts)")

    # Multi-series charts: labels + datasets
    datasets: Optional[List[DatasetSchema]] = Field(default=None, min_items=1, max_items=20, description="Multiple data series (multi-series charts)")

    # Scatter/bubble charts: data points with x/y/r coordinates
    data: Optional[List[ScatterBubbleDataPoint]] = Field(default=None, min_items=2, max_items=50, description="Data points for scatter/bubble charts")

    timestamp: Optional[str] = Field(default=None, description="Update timestamp")

    @validator('chart_id', 'presentation_id')
    def validate_ids(cls, v):
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty or whitespace")
        return v.strip()

    @validator('labels')
    def validate_labels(cls, v):
        """Validate labels array (optional for scatter/bubble)."""
        if v is None:
            return v  # Optional for scatter/bubble charts

        if len(v) < 2:
            raise ValueError("At least 2 labels required")
        if len(v) > 50:
            raise ValueError("Maximum 50 labels allowed")

        # Check for empty labels
        for i, label in enumerate(v):
            if not label or not str(label).strip():
                raise ValueError(f"Label at index {i} cannot be empty")

        # Check for duplicate labels
        if len(v) != len(set(v)):
            raise ValueError("Duplicate labels found. Each label must be unique")

        return [str(label).strip() for label in v]

    @validator('data', always=True)
    def validate_format(cls, v, values):
        """Validate that appropriate data format is provided based on chart type."""
        chart_type = values.get('chart_type', '')
        has_labels = values.get('labels') is not None
        has_values = values.get('values') is not None
        has_datasets = values.get('datasets') is not None
        has_data = v is not None  # scatter/bubble data

        # Scatter/bubble charts: require 'data' field
        if chart_type in ['scatter', 'bubble']:
            if not has_data:
                raise ValueError(f"{chart_type} charts require 'data' field with x/y coordinates")
            if has_labels or has_values or has_datasets:
                raise ValueError(f"{chart_type} charts should only use 'data' field, not labels/values/datasets")

            # Validate bubble charts have radius
            if chart_type == 'bubble':
                for i, point in enumerate(v):
                    if point.r is None:
                        raise ValueError(f"Bubble chart data point {i} missing radius 'r'")

            return v

        # Multi-series charts: require labels + datasets
        if has_datasets:
            if not has_labels:
                raise ValueError("Multi-series charts require 'labels' field")
            if has_values or has_data:
                raise ValueError("Cannot mix datasets with values or data")

            labels = values.get('labels', [])
            for i, ds in enumerate(v if has_datasets else []):
                if len(ds.data) != len(labels):
                    raise ValueError(
                        f"Dataset {i} ('{ds.label}'): data length ({len(ds.data)}) "
                        f"must match labels length ({len(labels)})"
                    )
            return values.get('datasets')

        # Simple charts: require labels + values
        if has_values:
            if not has_labels:
                raise ValueError("Simple charts require 'labels' field")
            if has_datasets or has_data:
                raise ValueError("Cannot mix values with datasets or data")

            labels = values.get('labels', [])
            vals = values.get('values', [])
            if len(vals) != len(labels):
                raise ValueError(f"Number of values ({len(vals)}) must match number of labels ({len(labels)})")

            for i, val in enumerate(vals):
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Value at index {i} must be a number, got {type(val).__name__}")
                if val != val:  # NaN check
                    raise ValueError(f"Value at index {i} cannot be NaN")
                if abs(val) == float('inf'):
                    raise ValueError(f"Value at index {i} cannot be infinity")
            return v

        # No valid format provided
        raise ValueError("Must provide either: (1) labels+values for simple charts, (2) labels+datasets for multi-series, or (3) data for scatter/bubble")


@app.post("/api/charts/update-data", tags=["Interactive Editor"])
async def update_chart_data(data: ChartDataUpdate):
    """
    Save edited chart data (for interactive editor).

    Supports both single-series (labels + values) and multi-series (labels + datasets) formats.

    Args:
        data: Chart data with labels and either values (single-series) or datasets (multi-series)

    Returns:
        Success status and message with format information
    """
    try:
        # Determine format based on chart_type and available fields
        is_scatter_bubble = data.chart_type in ['scatter', 'bubble'] and data.data is not None
        is_multi_series = data.datasets is not None and not is_scatter_bubble

        if is_scatter_bubble:
            format_type = data.chart_type
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.data)} data points)"
            )
        elif is_multi_series:
            format_type = "multi-series"
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.datasets)} series, {len(data.labels)} labels)"
            )
        else:
            format_type = "single-series"
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.labels)} labels, {len(data.values)} values)"
            )

        # TODO: Save to database when ChartData model is available
        # For now, just return success to allow client-side editing
        # In production, you'd save to PostgreSQL or Supabase

        response_data = {
            "success": True,
            "message": f"Chart data updated successfully ({format_type})",
            "chart_id": data.chart_id,
            "presentation_id": data.presentation_id,
            "format": format_type,
            "chart_type": data.chart_type
        }

        if is_scatter_bubble:
            response_data["data_points_count"] = len(data.data)
        elif is_multi_series:
            response_data["labels_count"] = len(data.labels)
            response_data["series_count"] = len(data.datasets)
            response_data["series_names"] = [ds.label for ds in data.datasets]
        else:
            response_data["labels_count"] = len(data.labels)
            response_data["values_count"] = len(data.values)

        return response_data

    except Exception as e:
        logger.error(f"Failed to update chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/get-data/{presentation_id}", tags=["Interactive Editor"])
async def get_chart_data(presentation_id: str):
    """
    Get all saved chart data for a presentation.

    Args:
        presentation_id: Presentation UUID

    Returns:
        List of chart data edits
    """
    try:
        logger.info(f"Fetching chart data for presentation: {presentation_id}")

        # TODO: Load from database when ChartData model is available
        # For now, return empty list

        return {
            "success": True,
            "presentation_id": presentation_id,
            "charts": []
        }

    except Exception as e:
        logger.error(f"Failed to fetch chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# LAYOUT SERVICE INTEGRATION API
# ========================================

@app.post("/api/ai/chart/generate", tags=["Layout Service Integration"], response_model=ChartGenerateResponse)
async def generate_chart_for_layout_service(request: ChartGenerateRequest):
    """
    Generate chart for Layout Service with grid-based constraints.

    This endpoint generates Chart.js configurations optimized for the Layout Service's
    grid-based canvas system. It enforces minimum grid sizes per chart type and
    limits data points based on available space.

    Args:
        request: Chart generation request with grid constraints

    Returns:
        Chart.js configuration with metadata and optional insights

    Grid Constraints:
        - gridWidth: 1-12 units
        - gridHeight: 1-8 units
        - Minimum sizes enforced per chart type (e.g., pie requires 3x3)
        - Data points limited based on grid area (small/medium/large)

    Example:
        ```
        POST /api/ai/chart/generate
        {
            "prompt": "Show quarterly revenue growth",
            "chartType": "bar",
            "presentationId": "pres-123",
            "slideId": "slide-7",
            "elementId": "chart-1",
            "context": {
                "presentationTitle": "Q4 Review",
                "slideIndex": 6
            },
            "constraints": {
                "gridWidth": 8,
                "gridHeight": 4
            },
            "style": {
                "palette": "professional"
            },
            "data": [
                {"label": "Q1", "value": 125000},
                {"label": "Q2", "value": 145000}
            ]
        }
        ```
    """
    import uuid
    from datetime import datetime
    from chartjs_generator import ChartJSGenerator

    try:
        chart_type = request.chartType.value
        grid_width = request.constraints.gridWidth
        grid_height = request.constraints.gridHeight

        logger.info(f"Layout Service chart generation: {chart_type} at {grid_width}x{grid_height}")

        # 1. Validate grid size meets minimum for chart type
        is_valid, error_msg = validate_grid_size(chart_type, grid_width, grid_height)
        if not is_valid:
            min_size = get_minimum_grid_size(chart_type)
            raise validation_error(
                code=ErrorCode.INVALID_GRID_SIZE,
                message=error_msg,
                field="constraints",
                details={
                    "provided": {"width": grid_width, "height": grid_height},
                    "minimum": min_size,
                    "chart_type": chart_type
                },
                suggestion=f"Use at least {min_size['width']}x{min_size['height']} grid for {chart_type} charts"
            )

        # 2. Get data limits based on grid area
        limits = get_data_limits(chart_type, grid_width, grid_height)
        layout_size = get_layout_size(grid_width, grid_height)
        logger.info(f"Grid area {grid_width * grid_height} = {layout_size.value}, limits: {limits}")

        # 3. Get or generate data
        data = None
        synthetic_data_used = False

        if request.data and len(request.data) > 0:
            # User provided data - truncate if needed
            raw_data = [
                {"label": d.label, "value": d.value} if hasattr(d, 'label') else d
                for d in request.data
            ]
            data = truncate_data_to_limits(raw_data, limits, chart_type)
            if len(data) < len(raw_data):
                logger.info(f"Truncated data from {len(raw_data)} to {len(data)} points for grid size")
        elif request.generateData:
            # Generate synthetic data
            logger.info(f"Generating synthetic data for {chart_type}")
            synthetic_data = synthetic_generator.generate(
                chart_type=map_chart_type_to_internal(chart_type),
                narrative=request.prompt,
                num_points=limits.get("maxPoints", 8)
            )
            data = truncate_data_to_limits(synthetic_data, limits, chart_type)
            synthetic_data_used = True
        else:
            # No data and not generating - error
            raise validation_error(
                code=ErrorCode.MISSING_DATA,
                message="No data provided and generateData is false",
                field="data",
                details={"generateData": request.generateData},
                suggestion="Provide data array or set generateData=true"
            )

        if not data or len(data) == 0:
            raise validation_error(
                code=ErrorCode.INVALID_DATA_POINTS,
                message="No valid data points after processing",
                field="data",
                details={"original_count": len(request.data) if request.data else 0},
                suggestion="Provide at least 2 valid data points"
            )

        # 4. Map chart type to internal type
        internal_type = map_chart_type_to_internal(chart_type)

        # 5. Get palette colors
        palette_name = request.style.palette.value if request.style and request.style.palette else "default"
        custom_colors = request.style.customColors if request.style else None
        data_count = len(data)

        colors = get_palette_colors(palette_name, data_count, custom_colors)
        theme = get_internal_theme(palette_name)
        color_config = get_chart_colors_for_type(chart_type, palette_name, data_count, custom_colors)

        # 6. Build Chart.js config
        generator = ChartJSGenerator(theme=theme)

        # Extract labels and values from data
        labels = [d.get("label", f"Item {i}") for i, d in enumerate(data)]
        values = [d.get("value", 0) for d in data]

        # Build chart configuration based on type
        chart_config = _build_layout_service_chartjs_config(
            chart_type=chart_type,
            internal_type=internal_type,
            labels=labels,
            values=values,
            colors=colors,
            color_config=color_config,
            request=request,
            generator=generator
        )

        # 7. Calculate metadata
        data_range = DataRange(
            min=min(values) if values else 0,
            max=max(values) if values else 0,
            average=sum(values) / len(values) if values else 0
        )

        suggested_title = _generate_suggested_title(request.prompt, chart_type)

        metadata = ChartMetadata(
            chartType=request.chartType,
            dataPointCount=len(data),
            datasetCount=1,  # Simple charts have 1 dataset
            suggestedTitle=suggested_title,
            dataRange=data_range
        )

        # 8. Generate insights (simple trend analysis)
        insights = _analyze_data_for_insights(values) if values and len(values) >= 2 else None

        # 9. Build raw data in Chart.js format
        raw_data = RawChartData(
            labels=labels,
            datasets=[
                DatasetData(
                    label=suggested_title,
                    data=values,
                    backgroundColor=color_config.get("backgroundColor"),
                    borderColor=color_config.get("borderColor")
                )
            ]
        )

        # 10. Return response
        generation_id = str(uuid.uuid4())

        logger.info(f"Layout Service chart generated: {generation_id} ({chart_type}, {len(data)} points)")

        return ChartGenerateResponse(
            success=True,
            data=ChartGenerateResponseData(
                generationId=generation_id,
                chartConfig=chart_config,
                rawData=raw_data,
                metadata=metadata,
                insights=insights
            )
        )

    except AnalyticsError:
        raise
    except Exception as e:
        logger.error(f"Layout Service chart generation failed: {e}", exc_info=True)
        raise processing_error(
            code=ErrorCode.CHART_GENERATION_FAILED,
            message=f"Chart generation failed: {str(e)}",
            details={"exception_type": type(e).__name__, "chart_type": request.chartType.value},
            retryable=False
        )


def _build_layout_service_chartjs_config(
    chart_type: str,
    internal_type: str,
    labels: list,
    values: list,
    colors: list,
    color_config: dict,
    request: ChartGenerateRequest,
    generator
) -> ChartConfiguration:
    """Build Chart.js configuration for Layout Service."""

    # Map Layout Service types to Chart.js types
    chartjs_type_map = {
        "bar": "bar",
        "line": "line",
        "pie": "pie",
        "doughnut": "doughnut",
        "area": "line",  # Line with fill
        "scatter": "scatter",
        "radar": "radar",
        "polarArea": "polarArea"
    }

    chartjs_type = chartjs_type_map.get(chart_type, "bar")

    # Build dataset
    dataset = {
        "label": request.context.slideTitle or "Data",
        "data": values,
        "backgroundColor": color_config.get("backgroundColor", colors),
        "borderColor": color_config.get("borderColor", colors),
        "borderWidth": color_config.get("borderWidth", 2)
    }

    # Type-specific dataset options
    if chart_type == "line":
        dataset["tension"] = 0.4
        dataset["fill"] = False
        dataset["pointRadius"] = 4
        dataset["pointHoverRadius"] = 6
    elif chart_type == "area":
        dataset["tension"] = 0.4
        dataset["fill"] = True
        dataset["pointRadius"] = 3
    elif chart_type in ["pie", "doughnut", "polarArea"]:
        # These use array of colors
        pass
    elif chart_type == "radar":
        dataset["fill"] = True
        dataset["pointRadius"] = 3

    # Build options
    style = request.style
    axes = request.axes
    config = request.config

    show_legend = style.showLegend if style and style.showLegend is not None else True
    legend_position = style.legendPosition.value if style and style.legendPosition else "top"
    show_grid = style.showGrid if style and style.showGrid is not None else True
    show_data_labels = style.showDataLabels if style and style.showDataLabels is not None else False
    animated = config.animated if config and config.animated is not None else True

    options = {
        "responsive": True,
        "maintainAspectRatio": False,
        "plugins": {
            "legend": {
                "display": show_legend,
                "position": legend_position
            },
            "tooltip": {
                "enabled": True
            }
        }
    }

    # Add animation options
    if not animated:
        options["animation"] = False
    else:
        options["animation"] = {
            "duration": 750,
            "easing": "easeOutQuart"
        }

    # Add data labels plugin config if requested
    if show_data_labels:
        options["plugins"]["datalabels"] = {
            "display": True,
            "anchor": "end",
            "align": "top"
        }

    # Add scales for applicable chart types
    if chart_type in ["bar", "line", "area", "scatter"]:
        options["scales"] = {
            "x": {
                "display": True,
                "grid": {
                    "display": show_grid
                }
            },
            "y": {
                "display": True,
                "beginAtZero": True,
                "grid": {
                    "display": show_grid
                }
            }
        }

        # Add axis labels if provided
        if axes:
            if axes.xLabel:
                options["scales"]["x"]["title"] = {
                    "display": True,
                    "text": axes.xLabel
                }
            if axes.yLabel:
                options["scales"]["y"]["title"] = {
                    "display": True,
                    "text": axes.yLabel
                }
            if axes.yMin is not None:
                options["scales"]["y"]["min"] = axes.yMin
            if axes.yMax is not None:
                options["scales"]["y"]["max"] = axes.yMax
            if axes.stacked:
                options["scales"]["x"]["stacked"] = True
                options["scales"]["y"]["stacked"] = True

    # Add radar-specific options
    if chart_type == "radar":
        options["scales"] = {
            "r": {
                "angleLines": {"display": True},
                "suggestedMin": 0
            }
        }

    # Add aspect ratio if provided
    if config and config.aspectRatio:
        options["aspectRatio"] = config.aspectRatio

    # Pie/doughnut specific
    if chart_type == "doughnut":
        options["cutout"] = "50%"

    return ChartConfiguration(
        type=chartjs_type,
        data={
            "labels": labels,
            "datasets": [dataset]
        },
        options=options
    )


def _generate_suggested_title(prompt: str, chart_type: str) -> str:
    """Generate a suggested title from the prompt."""
    # Simple extraction - take first meaningful phrase
    prompt_lower = prompt.lower()

    # Common patterns
    if "show" in prompt_lower:
        # "Show quarterly revenue" -> "Quarterly Revenue"
        parts = prompt.split("show", 1)
        if len(parts) > 1:
            title = parts[1].strip().title()
            # Limit length
            words = title.split()[:5]
            return " ".join(words)

    if "display" in prompt_lower:
        parts = prompt.split("display", 1)
        if len(parts) > 1:
            title = parts[1].strip().title()
            words = title.split()[:5]
            return " ".join(words)

    # Fallback: Use first part of prompt
    words = prompt.split()[:5]
    return " ".join(words).title()


def _analyze_data_for_insights(values: list) -> ChartInsights:
    """Analyze data to generate basic insights."""
    if not values or len(values) < 2:
        return None

    # Calculate trend
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]

    first_avg = sum(first_half) / len(first_half) if first_half else 0
    second_avg = sum(second_half) / len(second_half) if second_half else 0

    if abs(second_avg - first_avg) < (first_avg * 0.05):  # Less than 5% change
        trend = TrendType.STABLE
    elif second_avg > first_avg:
        trend = TrendType.INCREASING
    else:
        trend = TrendType.DECREASING

    # Check for volatility (standard deviation)
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5

    if std_dev > mean * 0.3:  # High coefficient of variation
        trend = TrendType.VOLATILE

    # Find outliers (values > 2 std devs from mean)
    outliers = []
    for i, v in enumerate(values):
        if abs(v - mean) > 2 * std_dev:
            outliers.append(i)

    # Generate highlights
    highlights = []
    if len(values) >= 2:
        total_change = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        if abs(total_change) >= 5:
            direction = "growth" if total_change > 0 else "decline"
            highlights.append(f"{abs(total_change):.1f}% {direction} over the period")

    max_val = max(values)
    min_val = min(values)
    max_idx = values.index(max_val)
    min_idx = values.index(min_val)

    if max_idx != min_idx:
        highlights.append(f"Peak at position {max_idx + 1}, lowest at position {min_idx + 1}")

    return ChartInsights(
        trend=trend,
        outliers=outliers if outliers else None,
        highlights=highlights if highlights else None
    )


@app.get("/api/ai/chart/constraints", tags=["Layout Service Integration"])
async def get_chart_constraints():
    """
    Get grid constraints for all chart types.

    Returns minimum grid sizes and data limits for each chart type,
    allowing the Layout Service to validate and enforce constraints
    before calling the generate endpoint.

    Returns:
        Dictionary with minimumGridSizes and dataLimits per chart type
    """
    from layout_service_constraints import get_all_minimum_grid_sizes, get_all_data_limits

    return {
        "success": True,
        "minimumGridSizes": get_all_minimum_grid_sizes(),
        "dataLimits": get_all_data_limits(),
        "gridRanges": {
            "width": {"min": 1, "max": 12},
            "height": {"min": 1, "max": 8}
        },
        "sizeThresholds": {
            "small": "area <= 16",
            "medium": "16 < area <= 48",
            "large": "area > 48"
        }
    }


@app.get("/api/ai/chart/palettes", tags=["Layout Service Integration"])
async def get_available_chart_palettes():
    """
    Get available color palettes for chart generation.

    Returns all available palette names and their color arrays,
    allowing the Layout Service to display palette options to users.

    Returns:
        List of available palettes with their colors
    """
    from layout_service_palette import FRONTEND_PALETTES, PALETTE_TO_THEME

    palettes = []
    for name, colors in FRONTEND_PALETTES.items():
        palettes.append({
            "name": name,
            "colors": colors,
            "internalTheme": PALETTE_TO_THEME.get(name, "professional"),
            "colorCount": len(colors)
        })

    return {
        "success": True,
        "palettes": palettes,
        "defaultPalette": "default"
    }


def run_server():
    """Start the REST API server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()
