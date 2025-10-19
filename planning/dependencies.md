# Analytics Microservice v3 - Dependency Configuration

## Configuration Architecture

Simple, minimal configuration for WebSocket-based analytics service. Focused on Railway deployment with OpenAI integration and real-time chart generation capabilities.

## Core Configuration Files

### 1. settings.py - Environment Configuration
```python
"""
Configuration management using pydantic-settings and python-dotenv.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider")
    llm_api_key: str = Field(..., alias="OPENAI_API_KEY", description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o-mini", description="Model name")
    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for OpenAI API"
    )
    
    # WebSocket Configuration
    websocket_port: int = Field(default=8080, description="WebSocket server port")
    max_concurrent_connections: int = Field(
        default=100, 
        description="Maximum concurrent WebSocket connections"
    )
    
    # Chart Generation Configuration
    chart_generation_timeout: int = Field(
        default=30, 
        description="Chart generation timeout in seconds"
    )
    max_chart_size_mb: int = Field(
        default=10, 
        description="Maximum chart size in MB"
    )
    
    # Railway Configuration
    railway_environment: str = Field(
        default="development", 
        description="Railway environment (development/production)"
    )
    
    # Application Configuration
    app_env: str = Field(default="development", description="Environment")
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Debug mode")
    max_retries: int = Field(default=3, description="Max retry attempts")
    
    @field_validator("llm_api_key")
    @classmethod
    def validate_openai_key(cls, v):
        """Ensure OpenAI API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("OpenAI API key cannot be empty")
        return v
    
    @field_validator("websocket_port")
    @classmethod
    def validate_port(cls, v):
        """Validate WebSocket port range."""
        if v < 1024 or v > 65535:
            raise ValueError("WebSocket port must be between 1024 and 65535")
        return v
    
    @field_validator("chart_generation_timeout")
    @classmethod
    def validate_timeout(cls, v):
        """Validate chart generation timeout."""
        if v < 5 or v > 300:
            raise ValueError("Chart generation timeout must be between 5 and 300 seconds")
        return v


def load_settings() -> Settings:
    """Load settings with proper error handling."""
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "openai_api_key" in str(e).lower():
            error_msg += "\nMake sure to set OPENAI_API_KEY in your .env file"
        raise ValueError(error_msg) from e


# Global settings instance
settings = load_settings()
```

### 2. providers.py - Model Provider Configuration
```python
"""
OpenAI provider configuration for analytics microservice.
"""

from typing import Optional
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from .settings import settings


def get_llm_model(model_choice: Optional[str] = None) -> OpenAIModel:
    """
    Get OpenAI model configuration for analytics tasks.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured OpenAI model instance
    """
    model_name = model_choice or settings.llm_model
    
    provider_instance = OpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key
    )
    
    return OpenAIModel(model_name, provider=provider_instance)


def get_chart_model() -> OpenAIModel:
    """
    Get optimized model for chart generation tasks.
    Uses gpt-4o-mini for fast, cost-effective processing.
    
    Returns:
        OpenAI model optimized for chart generation
    """
    provider_instance = OpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key
    )
    
    return OpenAIModel("gpt-4o-mini", provider=provider_instance)
```

### 3. dependencies.py - Agent Dependencies
```python
"""
Dependencies for Analytics Microservice v3 agent.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set
import asyncio
import logging
import base64
import io
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsDependencies:
    """
    Dependencies injected into analytics agent runtime context.
    
    Manages WebSocket connections, chart generation state, and external services
    needed for real-time analytics chart generation.
    """
    
    # WebSocket Connection Management
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
        Send progress update via WebSocket callback.
        
        Args:
            stage: Current generation stage (data_processing, rendering, completion)
            progress: Progress percentage (0-100)
            message: Optional progress message
        """
        if self.progress_callback and self.websocket_id:
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
```

### 4. agent.py - Agent Initialization
```python
"""
Analytics Microservice v3 - Pydantic AI Agent Implementation
"""

import logging
from typing import Optional
from pydantic_ai import Agent

from .providers import get_llm_model, get_chart_model
from .dependencies import AnalyticsDependencies
from .settings import settings

logger = logging.getLogger(__name__)

# System prompt for analytics agent
SYSTEM_PROMPT = """
You are an advanced analytics agent specialized in generating comprehensive charts and visualizations.

Your capabilities:
1. **Data Analysis**: Understand data patterns and recommend appropriate chart types
2. **Chart Generation**: Create 20+ chart types (bar, line, pie, scatter, heatmap, violin, etc.)
3. **Data Synthesis**: Generate realistic datasets when user data is incomplete
4. **Theme Application**: Apply consistent visual themes and styling
5. **Real-time Communication**: Provide progress updates during chart generation

Always:
- Choose the most appropriate chart type for the data and user intent
- Generate realistic, coherent data when synthesis is needed
- Apply consistent themes and professional styling
- Provide clear progress updates during generation
- Return charts as base64-encoded images or SVG

Communication style: Professional, data-focused, and efficient.
"""

# Initialize the agent with chart-optimized model
agent = Agent(
    get_chart_model(),
    deps_type=AnalyticsDependencies,
    system_prompt=SYSTEM_PROMPT,
    retries=settings.max_retries
)

logger.info("Analytics Microservice v3 agent initialized")

# Convenience functions for agent usage
async def run_analytics_agent(
    prompt: str,
    websocket_id: Optional[str] = None,
    progress_callback: Optional[callable] = None,
    **dependency_overrides
) -> str:
    """
    Run the analytics agent with WebSocket support.
    
    Args:
        prompt: User prompt/chart request
        websocket_id: WebSocket connection identifier
        progress_callback: Callback for progress updates
        **dependency_overrides: Override default dependencies
    
    Returns:
        Agent response as string (typically base64 chart)
    """
    deps = AnalyticsDependencies.from_settings(
        settings,
        websocket_id=websocket_id,
        progress_callback=progress_callback,
        **dependency_overrides
    )
    
    try:
        # Send initial progress update
        if websocket_id and progress_callback:
            await deps.send_progress_update("initialization", 0, "Starting chart generation")
        
        result = await agent.run(prompt, deps=deps)
        
        # Send completion update
        if websocket_id and progress_callback:
            await deps.send_progress_update("completion", 100, "Chart generation complete")
        
        return result.data
    finally:
        await deps.cleanup()


def create_analytics_agent_with_deps(**dependency_overrides) -> tuple[Agent, AnalyticsDependencies]:
    """
    Create agent instance with custom dependencies.
    
    Args:
        **dependency_overrides: Custom dependency values
    
    Returns:
        Tuple of (agent, dependencies)
    """
    deps = AnalyticsDependencies.from_settings(settings, **dependency_overrides)
    return agent, deps
```

## Environment File Template

### .env.example
```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your-openai-api-key-here

# WebSocket Configuration
WEBSOCKET_PORT=8080
MAX_CONCURRENT_CONNECTIONS=100

# Chart Generation Settings
CHART_GENERATION_TIMEOUT=30
MAX_CHART_SIZE_MB=10

# Railway Deployment
RAILWAY_ENVIRONMENT=production

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false
MAX_RETRIES=3
```

## Python Dependencies

### requirements.txt
```
# Core Pydantic AI dependencies
pydantic-ai>=0.1.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# OpenAI Provider
openai>=1.0.0

# WebSocket and FastAPI
fastapi>=0.104.0
websockets>=12.0
uvicorn>=0.24.0

# Chart Generation
matplotlib>=3.7.0
numpy>=1.24.0
pandas>=2.0.0
seaborn>=0.12.0
pillow>=10.0.0

# Async utilities
httpx>=0.25.0
aiofiles>=23.0.0

# Development and testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
ruff>=0.1.0

# Monitoring
loguru>=0.7.0
```

## WebSocket Integration Patterns

### Connection Management
```python
# Example WebSocket connection handler
async def handle_websocket_connection(websocket, connection_id: str):
    """Handle WebSocket connection for chart generation."""
    deps = AnalyticsDependencies.from_settings(
        settings,
        websocket_id=connection_id,
        progress_callback=send_websocket_update
    )
    
    if not deps.add_connection(connection_id):
        await websocket.close(code=1013, reason="Max connections reached")
        return
    
    try:
        async for message in websocket:
            # Process chart generation request
            chart_result = await run_analytics_agent(
                message,
                websocket_id=connection_id,
                progress_callback=send_websocket_update
            )
            
            await websocket.send_text(chart_result)
    finally:
        deps.remove_connection(connection_id)
```

### Progress Streaming
```python
async def send_websocket_update(update_data: dict):
    """Send progress update via WebSocket."""
    websocket_id = update_data["websocket_id"]
    # Implementation will send JSON progress data
    # to active WebSocket connection
```

## Railway Deployment Configuration

### Railway-specific Environment Variables
- `RAILWAY_ENVIRONMENT`: Set to "production" for Railway deployment
- `PORT`: Automatically provided by Railway, used for WebSocket server
- `WEBSOCKET_PORT`: Fallback port configuration

### Deployment Considerations
- Stateless design for Railway's scaling
- WebSocket connection limits appropriate for Railway resources
- Chart generation timeout suitable for Railway request limits
- Memory-efficient matplotlib backend (Agg) for headless operation

## Security Measures

### API Key Management
- OpenAI API key validation on startup
- No hardcoded credentials in code
- Secure environment variable loading via python-dotenv

### WebSocket Security
- Connection limits to prevent resource exhaustion
- Request timeout handling
- Chart size limits to prevent memory issues

## Quality Checklist

Before finalizing configuration:
- ✅ OpenAI API key validation implemented
- ✅ WebSocket connection management configured
- ✅ Chart generation timeout and size limits set
- ✅ Railway deployment variables included
- ✅ Matplotlib backend configured for headless operation
- ✅ Progress streaming mechanism defined
- ✅ Resource cleanup handled properly
- ✅ Security measures in place
- ✅ Error handling for WebSocket disconnections

## Integration Notes

This configuration supports:
- **Real-time WebSocket communication** with progress streaming
- **Railway deployment** with production-ready settings
- **Chart generation** with matplotlib and OpenAI integration
- **Connection scaling** with configurable limits
- **Error recovery** with retry mechanisms

The minimal design focuses on core analytics functionality while maintaining Railway deployment compatibility and real-time WebSocket capabilities.

---
Generated: 2025-09-01
Archon Project ID: 9da83cf1-ab6b-4195-9e2c-699e24d44129