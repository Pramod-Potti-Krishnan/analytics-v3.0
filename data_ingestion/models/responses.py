"""
Response models for Data Ingestion Agent API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ColumnSchemaResponse(BaseModel):
    """Column schema information."""
    name: str
    dtype: str
    nullable: bool
    unique_count: int
    null_count: int
    sample_values: List[Any]
    statistics: Optional[Dict[str, Any]] = None


class UploadResponse(BaseModel):
    """Response after successful file upload."""

    success: bool = True
    session_id: str = Field(..., description="Session ID for subsequent requests")
    filename: str = Field(..., description="Original filename")
    row_count: int = Field(..., description="Number of data rows")
    column_count: int = Field(..., description="Number of columns")
    columns: List[ColumnSchemaResponse] = Field(..., description="Column schemas")
    data_statistics: Dict[str, Any] = Field(..., description="Overall statistics")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    expires_at: Optional[str] = Field(None, description="Session expiration time")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "filename": "sales_data.csv",
                "row_count": 1000,
                "column_count": 5,
                "columns": [
                    {
                        "name": "quarter",
                        "dtype": "categorical",
                        "nullable": False,
                        "unique_count": 4,
                        "null_count": 0,
                        "sample_values": ["Q1", "Q2", "Q3"]
                    }
                ],
                "data_statistics": {
                    "numeric_columns": ["revenue", "quantity"],
                    "categorical_columns": ["quarter", "region"]
                },
                "warnings": [],
                "expires_at": "2025-01-01T12:00:00Z"
            }
        }


class ChartOutput(BaseModel):
    """Generated chart output."""
    chart_html: str = Field(..., description="Self-contained chart HTML")
    chart_title: str = Field(..., description="Chart title")
    chart_type: str = Field(..., description="Chart type used")
    insights_html: Optional[str] = Field(None, description="Key Insights HTML panel")


class ReasoningStep(BaseModel):
    """Single reasoning step in the agent workflow."""
    step_number: int
    step_type: str
    tool_name: str
    reasoning: Optional[str] = None
    duration_ms: float
    success: bool
    error_message: Optional[str] = None


class IngestResponse(BaseModel):
    """Response after data ingestion and chart generation."""

    success: bool = True
    request_id: str = Field(..., description="Request ID for audit trail")
    session_id: str = Field(..., description="Session ID used")
    chart: ChartOutput = Field(..., description="Generated chart")
    data_summary: Dict[str, Any] = Field(..., description="Data used for chart")
    reasoning_steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="Chain-of-thought reasoning steps"
    )
    total_duration_ms: float = Field(..., description="Total processing time")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "request_id": "req-xyz-123",
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "chart": {
                    "chart_html": "<div class='chart-container'>...</div>",
                    "chart_title": "Revenue by Quarter",
                    "chart_type": "bar_vertical",
                    "insights_html": None
                },
                "data_summary": {
                    "rows_used": 4,
                    "columns_used": ["quarter", "revenue"]
                },
                "reasoning_steps": [
                    {
                        "step_number": 1,
                        "step_type": "parse_intent",
                        "tool_name": "parse_user_intent",
                        "reasoning": "User wants to see revenue grouped by quarter",
                        "duration_ms": 150.5,
                        "success": True
                    }
                ],
                "total_duration_ms": 850.0
            }
        }


class SessionResponse(BaseModel):
    """Session metadata response."""

    session_id: str
    status: str
    filename: str
    row_count: int
    column_count: int
    columns: List[ColumnSchemaResponse]
    data_statistics: Optional[Dict[str, Any]] = None
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    created_at: str
    expires_at: str
    error_message: Optional[str] = None


class SessionListResponse(BaseModel):
    """List of sessions response."""

    success: bool = True
    sessions: List[SessionResponse]
    total_count: int
    limit: int
    offset: int


class ReasoningLogEntry(BaseModel):
    """Single reasoning log entry for audit."""
    id: str
    step_number: int
    step_type: str
    tool_name: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    reasoning: Optional[str] = None
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    created_at: str


class ReasoningResponse(BaseModel):
    """Full reasoning audit trail response."""

    success: bool = True
    session_id: str
    request_id: Optional[str] = None
    logs: List[ReasoningLogEntry]
    total_steps: int
    total_duration_ms: float
    final_status: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="healthy or unhealthy")
    database: Dict[str, Any] = Field(..., description="Database connection status")
    settings: Dict[str, Any] = Field(..., description="Configuration status")
    timestamp: str


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    suggestion: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response."""

    success: bool = False
    error: ErrorDetail

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "SESSION_NOT_FOUND",
                    "message": "Session with ID xyz not found",
                    "details": {"session_id": "xyz"},
                    "suggestion": "Verify the session ID or upload a new file"
                }
            }
        }
