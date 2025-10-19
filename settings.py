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

    # Supabase Configuration
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_KEY: str = Field(..., description="Supabase service role key")
    SUPABASE_BUCKET: str = Field(
        default="analytics-charts",
        description="Supabase storage bucket name"
    )

    # REST API Configuration
    API_PORT: int = Field(default=8080, description="REST API server port")
    JOB_CLEANUP_HOURS: int = Field(
        default=1,
        description="Hours after which completed jobs are auto-cleaned"
    )

    # WebSocket Configuration (Legacy - kept for backward compatibility)
    websocket_port: int = Field(default=8080, description="WebSocket server port", alias="WEBSOCKET_PORT")
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

    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v):
        """Ensure Supabase URL is not empty and valid."""
        if not v or v.strip() == "":
            raise ValueError("Supabase URL cannot be empty")
        if not v.startswith("https://"):
            raise ValueError("Supabase URL must start with https://")
        return v

    @field_validator("SUPABASE_KEY")
    @classmethod
    def validate_supabase_key(cls, v):
        """Ensure Supabase key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Supabase key cannot be empty")
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
        if "supabase" in str(e).lower():
            error_msg += "\nMake sure to set SUPABASE_URL and SUPABASE_KEY in your .env file"
        raise ValueError(error_msg) from e


# Global settings instance
settings = load_settings()