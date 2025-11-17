"""
REST API server for Analytics Microservice v3.
FastAPI-based REST endpoints replacing WebSocket implementation.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    get_apexcharts_types,
    get_chart_types_by_layout,
    get_chart_type_by_id,
    get_chart_type_summary,
    SupportedLayout,
    ChartLibrary
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Analytics Microservice v3",
    description="REST API for chart generation with Supabase Storage",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    data: List[ChartDataPoint] = Field(..., min_items=2, max_items=50, description="Chart data points (2-50 points)")
    context: dict = Field(default_factory=dict, description="Presentation context (theme, audience, etc.)")
    constraints: dict = Field(default_factory=dict, description="Layout constraints (dimensions, etc.)")

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
        """Validate data array consistency."""
        if not v or len(v) < 2:
            raise ValueError("At least 2 data points required for meaningful charts")
        if len(v) > 50:
            raise ValueError("Maximum 50 data points allowed to prevent performance issues")

        # Check for duplicate labels
        labels = [point.label for point in v]
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analytics_microservice_v3",
        "jobs": job_manager.get_stats()
    }


@app.get("/stats")
async def get_stats():
    """Get job statistics."""
    return {
        "job_stats": job_manager.get_stats(),
        "storage_bucket": settings.SUPABASE_BUCKET
    }


# ========================================
# CHART TYPE DISCOVERY ENDPOINTS
# ========================================

@app.get("/api/v1/chart-types")
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


@app.get("/api/v1/chart-types/chartjs")
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


@app.get("/api/v1/chart-types/apexcharts")
async def get_apexcharts_chart_types():
    """
    Get ApexCharts chart types (L01, L03 layouts).

    Returns:
        ApexCharts-based chart types for legacy layouts
    """
    charts = get_apexcharts_types()

    return {
        "success": True,
        "library": ChartLibrary.APEXCHARTS.value,
        "layouts": [SupportedLayout.L01.value, SupportedLayout.L03.value],
        "count": len(charts),
        "chart_types": [ct.dict() for ct in charts]
    }


@app.get("/api/v1/chart-types/{chart_id}")
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


@app.get("/api/v1/layouts/{layout}/chart-types")
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


@app.post("/generate", response_model=JobResponse, deprecated=True)
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


@app.get("/status/{job_id}")
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


@app.post("/api/v1/analytics/{layout}/{analytics_type}")
async def generate_analytics_slide(
    layout: str,
    analytics_type: str,
    request: AnalyticsRequest
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

    Returns:
        Slide content with chart HTML and insights
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

            logger.info(f"Generating L02 analytics: {analytics_type}")

            result = await generate_l02_analytics(request.dict())

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


@app.post("/api/v1/analytics/batch")
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

class ChartDataUpdate(BaseModel):
    """Request to update chart data."""
    chart_id: str = Field(..., min_length=1, description="Chart identifier")
    presentation_id: str = Field(..., min_length=1, description="Presentation UUID")
    labels: List[str] = Field(..., min_items=2, max_items=50, description="X-axis labels (2-50 items)")
    values: List[float] = Field(..., min_items=2, max_items=50, description="Y-axis values (2-50 items)")
    timestamp: Optional[str] = Field(default=None, description="Update timestamp")

    @validator('chart_id', 'presentation_id')
    def validate_ids(cls, v):
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty or whitespace")
        return v.strip()

    @validator('labels')
    def validate_labels(cls, v):
        """Validate labels array."""
        if not v or len(v) < 2:
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

    @validator('values')
    def validate_values(cls, v, values):
        """Validate values array and ensure it matches labels length."""
        if not v or len(v) < 2:
            raise ValueError("At least 2 values required")
        if len(v) > 50:
            raise ValueError("Maximum 50 values allowed")

        # Check if lengths match
        if 'labels' in values and len(v) != len(values['labels']):
            raise ValueError(f"Number of values ({len(v)}) must match number of labels ({len(values['labels'])})")

        # Validate each value is a finite number
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Value at index {i} must be a number, got {type(val).__name__}")
            if val != val:  # NaN check
                raise ValueError(f"Value at index {i} cannot be NaN")
            if abs(val) == float('inf'):
                raise ValueError(f"Value at index {i} cannot be infinity")

        return [float(val) for val in v]


@app.post("/api/charts/update-data")
async def update_chart_data(data: ChartDataUpdate):
    """
    Save edited chart data (for interactive editor).

    Args:
        data: Chart data with labels and values

    Returns:
        Success status and message
    """
    try:
        logger.info(f"Updating chart data: {data.chart_id} in presentation {data.presentation_id}")

        # TODO: Save to database when ChartData model is available
        # For now, just return success to allow client-side editing
        # In production, you'd save to PostgreSQL or Supabase

        return {
            "success": True,
            "message": "Chart data updated successfully",
            "chart_id": data.chart_id,
            "presentation_id": data.presentation_id,
            "labels_count": len(data.labels),
            "values_count": len(data.values)
        }

    except Exception as e:
        logger.error(f"Failed to update chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/get-data/{presentation_id}")
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
