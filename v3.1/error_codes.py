"""
Error codes and standardized error responses for Analytics Microservice v3.

Provides consistent error handling and structured error responses
for Director integration and client applications.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Standardized error codes for analytics service."""

    # Validation Errors (400 series)
    INVALID_DATA_POINTS = "INVALID_DATA_POINTS"
    INVALID_LABELS = "INVALID_LABELS"
    INVALID_VALUES = "INVALID_VALUES"
    MISMATCHED_LENGTHS = "MISMATCHED_LENGTHS"
    DUPLICATE_LABELS = "DUPLICATE_LABELS"
    EMPTY_FIELD = "EMPTY_FIELD"
    INVALID_ANALYTICS_TYPE = "INVALID_ANALYTICS_TYPE"
    INVALID_LAYOUT = "INVALID_LAYOUT"
    INVALID_CHART_TYPE = "INVALID_CHART_TYPE"
    DATA_RANGE_ERROR = "DATA_RANGE_ERROR"  # Too few or too many data points

    # Processing Errors (500 series)
    CHART_GENERATION_FAILED = "CHART_GENERATION_FAILED"
    INSIGHT_GENERATION_FAILED = "INSIGHT_GENERATION_FAILED"
    LAYOUT_ASSEMBLY_FAILED = "LAYOUT_ASSEMBLY_FAILED"
    STORAGE_ERROR = "STORAGE_ERROR"
    LLM_ERROR = "LLM_ERROR"

    # Resource Errors (404 series)
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    CHART_NOT_FOUND = "CHART_NOT_FOUND"
    PRESENTATION_NOT_FOUND = "PRESENTATION_NOT_FOUND"

    # Rate Limiting (429 series)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Unknown/Generic
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VALIDATION = "validation"      # User input errors (retryable with fixes)
    PROCESSING = "processing"      # Internal processing errors (retryable)
    RESOURCE = "resource"          # Resource not found (not retryable)
    RATE_LIMIT = "rate_limit"      # Rate limiting (retryable after delay)
    SYSTEM = "system"              # System errors (contact support)


class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: ErrorCode
    message: str
    category: ErrorCategory
    field: Optional[str] = None  # Which field caused the error (if applicable)
    details: Optional[Dict[str, Any]] = None  # Additional context
    retryable: bool = False  # Whether the request can be retried
    suggestion: Optional[str] = None  # How to fix the error

    class Config:
        schema_extra = {
            "example": {
                "code": "INVALID_DATA_POINTS",
                "message": "At least 2 data points required for meaningful charts",
                "category": "validation",
                "field": "data",
                "details": {"provided": 1, "minimum": 2},
                "retryable": True,
                "suggestion": "Provide at least 2 data points with label and value"
            }
        }


class AnalyticsError(Exception):
    """
    Custom exception for analytics service errors.

    Provides structured error information for consistent API responses.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False,
        suggestion: Optional[str] = None,
        http_status: int = 500
    ):
        self.code = code
        self.message = message
        self.category = category
        self.field = field
        self.details = details or {}
        self.retryable = retryable
        self.suggestion = suggestion
        self.http_status = http_status
        super().__init__(message)

    def to_detail(self) -> ErrorDetail:
        """Convert to ErrorDetail model."""
        return ErrorDetail(
            code=self.code,
            message=self.message,
            category=self.category,
            field=self.field,
            details=self.details,
            retryable=self.retryable,
            suggestion=self.suggestion
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for HTTP response."""
        return {
            "success": False,
            "error": self.to_detail().dict(exclude_none=True)
        }


# Predefined error factories for common cases
def validation_error(
    code: ErrorCode,
    message: str,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    suggestion: Optional[str] = None
) -> AnalyticsError:
    """Create a validation error (400 status)."""
    return AnalyticsError(
        code=code,
        message=message,
        category=ErrorCategory.VALIDATION,
        field=field,
        details=details,
        retryable=True,
        suggestion=suggestion,
        http_status=400
    )


def processing_error(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    retryable: bool = True
) -> AnalyticsError:
    """Create a processing error (500 status)."""
    return AnalyticsError(
        code=code,
        message=message,
        category=ErrorCategory.PROCESSING,
        details=details,
        retryable=retryable,
        http_status=500
    )


def resource_error(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> AnalyticsError:
    """Create a resource not found error (404 status)."""
    return AnalyticsError(
        code=code,
        message=message,
        category=ErrorCategory.RESOURCE,
        details=details,
        retryable=False,
        http_status=404
    )


# Common error messages
ERROR_MESSAGES = {
    ErrorCode.INVALID_DATA_POINTS: "Invalid data points provided",
    ErrorCode.INVALID_LABELS: "Invalid labels array",
    ErrorCode.INVALID_VALUES: "Invalid values array",
    ErrorCode.MISMATCHED_LENGTHS: "Labels and values arrays have different lengths",
    ErrorCode.DUPLICATE_LABELS: "Duplicate labels found",
    ErrorCode.DATA_RANGE_ERROR: "Data points out of acceptable range (2-50)",
    ErrorCode.INVALID_ANALYTICS_TYPE: "Invalid analytics type specified",
    ErrorCode.INVALID_LAYOUT: "Invalid layout type specified",
    ErrorCode.CHART_GENERATION_FAILED: "Chart generation failed",
    ErrorCode.INSIGHT_GENERATION_FAILED: "Insight generation failed",
    ErrorCode.JOB_NOT_FOUND: "Job not found",
}


def get_error_message(code: ErrorCode, default: str = "An error occurred") -> str:
    """Get standard error message for error code."""
    return ERROR_MESSAGES.get(code, default)
