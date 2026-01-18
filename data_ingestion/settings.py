"""
Settings for Data Ingestion module.

Separate from main analytics settings to maintain isolation.
Uses DATA_INGESTION_ prefix for all environment variables.
"""

import os
from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class DataIngestionSettings(BaseSettings):
    """
    Data Ingestion module settings.

    All environment variables use DATA_INGESTION_ prefix.
    """

    model_config = ConfigDict(
        env_prefix="DATA_INGESTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # PostgreSQL Configuration (Railway auto-injects DATABASE_URL)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection URL (Railway injects this)"
    )

    # Connection Pool Settings
    DB_POOL_MIN_SIZE: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Minimum connections in pool"
    )
    DB_POOL_MAX_SIZE: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Maximum connections in pool"
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )

    # Session Settings
    SESSION_TTL_HOURS: int = Field(
        default=1,
        ge=1,
        le=24,
        description="Session time-to-live in hours"
    )
    SESSION_CLEANUP_INTERVAL_MINUTES: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Interval for expired session cleanup"
    )

    # File Upload Limits
    MAX_FILE_SIZE_MB: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum upload file size in MB"
    )
    MAX_ROWS_PER_SESSION: int = Field(
        default=100000,
        ge=1000,
        le=1000000,
        description="Maximum rows per session"
    )
    MAX_COLUMNS_PER_SESSION: int = Field(
        default=100,
        ge=10,
        le=500,
        description="Maximum columns per session"
    )

    # Query Limits
    QUERY_TIMEOUT_SECONDS: int = Field(
        default=30,
        ge=5,
        le=300,
        description="SQL query timeout in seconds"
    )
    MAX_RESULT_ROWS: int = Field(
        default=10000,
        ge=100,
        le=100000,
        description="Maximum rows returned by queries"
    )

    # Agent Settings
    MAX_AGENT_STEPS: int = Field(
        default=10,
        ge=3,
        le=50,
        description="Maximum reasoning steps per request"
    )
    AGENT_STEP_TIMEOUT_SECONDS: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout per agent reasoning step"
    )

    # OpenAI Settings (for intent parsing)
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for intent parsing (falls back to main settings)"
    )
    INTENT_MODEL: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for intent parsing"
    )

    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_data_ingestion_settings() -> DataIngestionSettings:
    """
    Get cached data ingestion settings instance.

    Returns:
        DataIngestionSettings instance
    """
    settings = DataIngestionSettings()

    # Fallback: Check for Railway's DATABASE_URL if not prefixed
    if not settings.DATABASE_URL:
        railway_url = os.environ.get("DATABASE_URL")
        if railway_url:
            settings.DATABASE_URL = railway_url

    # Fallback: Get OpenAI key from main settings
    if not settings.OPENAI_API_KEY:
        main_key = os.environ.get("OPENAI_API_KEY")
        if main_key:
            settings.OPENAI_API_KEY = main_key

    return settings


def validate_settings() -> dict:
    """
    Validate data ingestion settings.

    Returns:
        Dict with validation results
    """
    try:
        settings = get_data_ingestion_settings()

        issues = []

        if not settings.DATABASE_URL:
            issues.append("DATABASE_URL not configured - PostgreSQL required")

        if not settings.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not configured - intent parsing disabled")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "settings": {
                "database_configured": bool(settings.DATABASE_URL),
                "openai_configured": bool(settings.OPENAI_API_KEY),
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
                "max_rows": settings.MAX_ROWS_PER_SESSION,
                "session_ttl_hours": settings.SESSION_TTL_HOURS,
            }
        }

    except Exception as e:
        return {
            "valid": False,
            "issues": [str(e)],
            "settings": {}
        }
