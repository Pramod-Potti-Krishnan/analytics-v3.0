"""
Job Manager for async chart generation tracking.
Manages in-memory job states and progress updates.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status states."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    """Represents a chart generation job."""

    def __init__(self, request_data: Dict[str, Any]):
        self.job_id = str(uuid.uuid4())
        self.request_data = request_data
        self.status = JobStatus.QUEUED
        self.progress = 0
        self.stage = "initialization"
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary format."""
        response = {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "stage": self.stage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        # Add result if completed
        if self.status == JobStatus.COMPLETED and self.result:
            response.update(self.result)

        # Add error if failed
        if self.status == JobStatus.FAILED and self.error:
            response["error"] = self.error

        return response


class JobManager:
    """Manages chart generation jobs in memory."""

    def __init__(self, cleanup_hours: int = 1):
        """
        Initialize job manager.

        Args:
            cleanup_hours: Hours after which completed jobs are auto-cleaned
        """
        self.jobs: Dict[str, Job] = {}
        self.cleanup_hours = cleanup_hours
        logger.info(f"JobManager initialized (cleanup after {cleanup_hours}h)")

    def create_job(self, request_data: Dict[str, Any]) -> str:
        """
        Create a new job.

        Args:
            request_data: Chart generation request parameters

        Returns:
            job_id: Unique job identifier
        """
        job = Job(request_data)
        self.jobs[job.job_id] = job

        # Cleanup old jobs
        self._cleanup_old_jobs()

        logger.info(f"Created job {job.job_id}")
        return job.job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job object or None if not found
        """
        return self.jobs.get(job_id)

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status and results.

        Args:
            job_id: Job identifier

        Returns:
            Job status dictionary or None if not found
        """
        job = self.get_job(job_id)
        if not job:
            return None

        return job.to_dict()

    def update_progress(self, job_id: str, stage: str, progress: int):
        """
        Update job progress.

        Args:
            job_id: Job identifier
            stage: Current processing stage
            progress: Progress percentage (0-100)
        """
        job = self.get_job(job_id)
        if job:
            job.stage = stage
            job.progress = min(100, max(0, progress))
            job.status = JobStatus.PROCESSING
            job.updated_at = datetime.now()
            logger.debug(f"Job {job_id} progress: {progress}% - {stage}")

    def complete_job(self, job_id: str, result: Dict[str, Any]):
        """
        Mark job as completed with results.

        Args:
            job_id: Job identifier
            result: Chart generation result {chart_url, chart_data, metadata}
        """
        job = self.get_job(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.stage = "completed"
            job.result = result
            job.updated_at = datetime.now()
            logger.info(f"Job {job_id} completed successfully")

    def fail_job(self, job_id: str, error: str):
        """
        Mark job as failed.

        Args:
            job_id: Job identifier
            error: Error message
        """
        job = self.get_job(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.error = error
            job.updated_at = datetime.now()
            logger.error(f"Job {job_id} failed: {error}")

    def _cleanup_old_jobs(self):
        """Remove jobs older than cleanup_hours."""
        cutoff = datetime.now() - timedelta(hours=self.cleanup_hours)
        old_jobs = [
            job_id for job_id, job in self.jobs.items()
            if job.updated_at < cutoff and job.status in [JobStatus.COMPLETED, JobStatus.FAILED]
        ]

        for job_id in old_jobs:
            del self.jobs[job_id]
            logger.debug(f"Cleaned up old job {job_id}")

        if old_jobs:
            logger.info(f"Cleaned up {len(old_jobs)} old jobs")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get job manager statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "total_jobs": len(self.jobs),
            "queued": sum(1 for j in self.jobs.values() if j.status == JobStatus.QUEUED),
            "processing": sum(1 for j in self.jobs.values() if j.status == JobStatus.PROCESSING),
            "completed": sum(1 for j in self.jobs.values() if j.status == JobStatus.COMPLETED),
            "failed": sum(1 for j in self.jobs.values() if j.status == JobStatus.FAILED),
        }
        return stats
