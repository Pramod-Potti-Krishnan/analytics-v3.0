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

from .settings import settings
from .job_manager import JobManager
from .storage import SupabaseStorage
from .dependencies import AnalyticsDependencies
from .agent import process_analytics_direct

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
            "generate": "POST /generate",
            "status": "GET /status/{job_id}",
            "health": "GET /health",
            "stats": "GET /stats"
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
