"""
Dependencies for Analytics Microservice v3 agent.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set, TYPE_CHECKING
import asyncio
import logging
import base64
import io
from datetime import datetime

if TYPE_CHECKING:
    from storage import SupabaseStorage
    from job_manager import JobManager

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsDependencies:
    """
    Dependencies injected into analytics agent runtime context.

    Manages job tracking, storage, and chart generation state for REST API.
    """

    # Job Management (replaces WebSocket)
    job_manager: Optional['JobManager'] = None
    job_id: Optional[str] = None

    # Storage
    storage: Optional['SupabaseStorage'] = None

    # Legacy fields (for backward compatibility)
    websocket_id: Optional[str] = None
    user_session_id: Optional[str] = None
    active_connections: Set[str] = field(default_factory=set, init=False)

    # Chart Generation Context
    chart_request_id: Optional[str] = None
    generation_start_time: Optional[datetime] = None
    progress_callback: Optional[callable] = None

    # Configuration from Settings
    max_connections: int = 100
    generation_timeout: int = 30
    max_chart_size_mb: int = 10
    debug: bool = False

    # External Service Clients (initialized lazily)
    _matplotlib_backend: Optional[str] = field(default="Agg", init=False, repr=False)
    _chart_cache: Optional[Dict[str, Any]] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Initialize matplotlib backend for headless operation."""
        import matplotlib
        matplotlib.use(self._matplotlib_backend)
        logger.info(f"Matplotlib backend set to: {self._matplotlib_backend}")
    
    @property
    def chart_cache(self) -> Dict[str, Any]:
        """Lazy initialization of chart cache."""
        if self._chart_cache is None:
            self._chart_cache = {}
            logger.info("Chart cache initialized")
        return self._chart_cache
    
    async def send_progress_update(self, stage: str, progress: int, message: str = ""):
        """
        Send progress update via job manager or WebSocket callback (legacy).

        Args:
            stage: Current generation stage (data_processing, rendering, completion)
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        # Use job manager if available (REST API mode)
        if self.job_manager and self.job_id:
            try:
                self.job_manager.update_progress(self.job_id, stage, progress)
                logger.debug(f"Job {self.job_id}: {stage} - {progress}% - {message}")
            except Exception as e:
                logger.error(f"Failed to update job progress: {e}")

        # Fallback to WebSocket callback (legacy mode)
        elif self.progress_callback and self.websocket_id:
            try:
                update_data = {
                    "websocket_id": self.websocket_id,
                    "request_id": self.chart_request_id,
                    "stage": stage,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await self.progress_callback(update_data)
            except Exception as e:
                logger.error(f"Failed to send progress update: {e}")
    
    def add_connection(self, connection_id: str) -> bool:
        """
        Add new WebSocket connection.
        
        Args:
            connection_id: Unique connection identifier
        
        Returns:
            True if connection added, False if max connections reached
        """
        if len(self.active_connections) >= self.max_connections:
            logger.warning(f"Max connections ({self.max_connections}) reached")
            return False
        
        self.active_connections.add(connection_id)
        logger.info(f"Connection added: {connection_id}. Active: {len(self.active_connections)}")
        return True
    
    def remove_connection(self, connection_id: str):
        """Remove WebSocket connection."""
        self.active_connections.discard(connection_id)
        logger.info(f"Connection removed: {connection_id}. Active: {len(self.active_connections)}")
    
    def encode_chart_to_base64(self, chart_buffer: io.BytesIO) -> str:
        """
        Encode matplotlib chart buffer to base64 string.
        
        Args:
            chart_buffer: BytesIO buffer containing chart image
        
        Returns:
            Base64-encoded chart string
        """
        chart_buffer.seek(0)
        chart_bytes = chart_buffer.getvalue()
        
        # Check size limit
        size_mb = len(chart_bytes) / (1024 * 1024)
        if size_mb > self.max_chart_size_mb:
            logger.warning(f"Chart size ({size_mb:.2f}MB) exceeds limit ({self.max_chart_size_mb}MB)")
        
        return base64.b64encode(chart_bytes).decode('utf-8')
    
    async def cleanup(self):
        """Cleanup resources when done."""
        if self._chart_cache:
            self._chart_cache.clear()
        
        # Clear active connections
        self.active_connections.clear()
        logger.info("Analytics dependencies cleaned up")
    
    @classmethod
    def from_settings(cls, settings, **kwargs):
        """
        Create dependencies from settings with overrides.
        
        Args:
            settings: Settings instance
            **kwargs: Override values
        
        Returns:
            Configured AnalyticsDependencies instance
        """
        return cls(
            max_connections=kwargs.get('max_connections', settings.max_concurrent_connections),
            generation_timeout=kwargs.get('generation_timeout', settings.chart_generation_timeout),
            max_chart_size_mb=kwargs.get('max_chart_size_mb', settings.max_chart_size_mb),
            debug=kwargs.get('debug', settings.debug),
            **{k: v for k, v in kwargs.items() 
               if k not in ['max_connections', 'generation_timeout', 'max_chart_size_mb', 'debug']}
        )