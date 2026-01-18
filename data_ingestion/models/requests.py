"""
Request models for Data Ingestion Agent API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class UploadRequest(BaseModel):
    """Request metadata for file upload (file content sent separately)."""

    presentation_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Presentation UUID for slide integration"
    )
    slide_id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Slide identifier for context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres-123-456",
                "slide_id": "slide-7"
            }
        }


class IngestRequest(BaseModel):
    """
    Request to process data and generate visualization.

    The agent will use chain-of-thought reasoning to:
    1. Analyze the session data
    2. Parse user intent from narrative
    3. Transform data as needed
    4. Generate appropriate chart
    """

    session_id: str = Field(
        ...,
        min_length=1,
        description="Session ID from upload"
    )
    narrative: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User description of desired visualization"
    )
    chart_type: Optional[str] = Field(
        None,
        description="Optional chart type override (auto-detected if not specified)"
    )
    chart_title: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional chart title (generated if not specified)"
    )
    presentation_id: Optional[str] = Field(
        None,
        description="Presentation ID for chart persistence"
    )
    slide_id: Optional[str] = Field(
        None,
        description="Slide ID for chart persistence"
    )
    include_insights: bool = Field(
        False,
        description="Include Key Insights panel with chart"
    )
    width: int = Field(
        850,
        ge=200,
        le=2000,
        description="Chart width in pixels"
    )
    height: int = Field(
        500,
        ge=150,
        le=1500,
        description="Chart height in pixels"
    )

    @field_validator("narrative")
    @classmethod
    def validate_narrative(cls, v: str) -> str:
        """Ensure narrative is meaningful."""
        if not v or not v.strip():
            raise ValueError("Narrative cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "narrative": "Show revenue by quarter as a bar chart",
                "chart_type": None,
                "include_insights": True,
                "width": 850,
                "height": 500
            }
        }


class PreviewRequest(BaseModel):
    """
    Request to preview a transformation without committing.

    Returns a preview of the data after applying the transformation,
    without modifying the underlying session data.
    """

    session_id: str = Field(
        ...,
        min_length=1,
        description="Session ID to preview"
    )
    columns: Optional[List[str]] = Field(
        None,
        description="Columns to include (None = all)"
    )
    aggregation: Optional[str] = Field(
        None,
        description="Aggregation to apply (sum, avg, count, etc.)"
    )
    group_by: Optional[List[str]] = Field(
        None,
        description="Columns to group by"
    )
    filter_condition: Optional[str] = Field(
        None,
        max_length=500,
        description="SQL WHERE condition (parameterized)"
    )
    filter_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Parameters for filter condition"
    )
    limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum rows to return"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "columns": ["quarter", "revenue"],
                "aggregation": "sum",
                "group_by": ["quarter"],
                "limit": 20
            }
        }


class SessionListRequest(BaseModel):
    """Request to list data sessions."""

    presentation_id: Optional[str] = Field(
        None,
        description="Filter by presentation ID"
    )
    status: Optional[str] = Field(
        None,
        description="Filter by status (created, ready, expired, error)"
    )
    limit: int = Field(
        50,
        ge=1,
        le=200,
        description="Maximum sessions to return"
    )
    offset: int = Field(
        0,
        ge=0,
        description="Pagination offset"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres-123",
                "status": "ready",
                "limit": 50,
                "offset": 0
            }
        }
