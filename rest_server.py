"""
REST API server for Analytics Microservice v3.
FastAPI-based REST endpoints replacing WebSocket implementation.
"""

import logging
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from settings import settings
from job_manager import JobManager
from storage import SupabaseStorage
from dependencies import AnalyticsDependencies
from agent import process_analytics_direct
from analytics_types import AnalyticsType, get_analytics_layout

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

# Initialize global managers
job_manager = JobManager(cleanup_hours=settings.JOB_CLEANUP_HOURS)
storage = SupabaseStorage(
    url=settings.SUPABASE_URL,
    key=settings.SUPABASE_KEY,
    bucket_name=settings.SUPABASE_BUCKET
)


# Request/Response Models
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
    presentation_id: str = Field(..., description="Presentation UUID")
    slide_id: str = Field(..., description="Slide identifier")
    slide_number: int = Field(..., description="Slide position in deck")
    narrative: str = Field(..., description="User's description of analytics needed")
    data: list = Field(..., description="Chart data points [{label, value}, ...]")
    context: dict = Field(default_factory=dict, description="Presentation context (theme, audience, etc.)")
    constraints: dict = Field(default_factory=dict, description="Layout constraints (dimensions, etc.)")

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
        "version": "3.0.0",
        "status": "running",
        "api_type": "REST",
        "endpoints": {
            "generate": "POST /generate (Legacy PNG generation)",
            "status": "GET /status/{job_id}",
            "health": "GET /health",
            "stats": "GET /stats",
            "analytics": "POST /api/v1/analytics/{layout}/{type} (Text Service compatible)",
            "batch": "POST /api/v1/analytics/batch"
        },
        "supported_analytics": [t.value for t in AnalyticsType],
        "supported_layouts": ["L01", "L02", "L03"]
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


@app.post("/generate", response_model=JobResponse)
async def generate_chart(request: ChartRequest):
    """
    Submit a chart generation request.

    Returns job_id for polling status.
    """
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
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

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
            raise HTTPException(
                status_code=400,
                detail=f"Invalid analytics type: {analytics_type}. Supported: {[t.value for t in AnalyticsType]}"
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
                raise HTTPException(
                    status_code=500,
                    detail=result.get("error", "Analytics generation failed")
                )

            # Return Text Service compatible response
            return {
                "content": result.get("content", {}),
                "metadata": result.get("metadata", {})
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
    chart_id: str = Field(..., description="Chart identifier")
    presentation_id: str = Field(..., description="Presentation UUID")
    labels: list = Field(..., description="X-axis labels")
    values: list = Field(..., description="Y-axis values")
    timestamp: str = Field(default=None, description="Update timestamp")


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
