"""
REST API server for Analytics Microservice v3.
FastAPI-based REST endpoints replacing WebSocket implementation.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
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

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Microservice v3",
    description="""
## Analytics Service v3.4.3 - Complete Chart.js Suite (20+ Chart Types)

Generate interactive Chart.js visualizations with comprehensive charting capabilities.

### Key Features
- ✅ **20+ Chart Types** (Chart.js with native types and plugins)
- ✅ **Comprehensive Data Validation** (2-50 data points, NaN/Infinity rejection)
- ✅ **Structured Error Responses** (retryable flags, fix suggestions)
- ✅ **Chart Type Discovery** (complete catalog with use cases)
- ✅ **Interactive Editor** (L02 charts)
- ✅ **Text Service Compatible** (Director Agent integration)

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
    version="3.1.4",
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
        "version": "3.1.2",
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
        # Determine format
        is_multi_series = data.datasets is not None
        format_type = "multi-series" if is_multi_series else "single-series"

        if is_multi_series:
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.datasets)} series, {len(data.labels)} labels)"
            )
        else:
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
            "labels_count": len(data.labels)
        }

        if is_multi_series:
            response_data["series_count"] = len(data.datasets)
            response_data["series_names"] = [ds.label for ds in data.datasets]
        else:
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
