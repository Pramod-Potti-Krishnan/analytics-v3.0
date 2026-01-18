"""
Internal models for Data Ingestion Agent tools.

These models are used by the MCP-style tools for
passing data between reasoning steps.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ColumnInfo(BaseModel):
    """Information about a single column."""
    name: str
    dtype: str  # numeric, categorical, datetime, text
    nullable: bool
    unique_count: int
    null_count: int
    sample_values: List[Any]
    statistics: Optional[Dict[str, Any]] = None


class SessionInfo(BaseModel):
    """
    Session information returned by get_session_info tool.

    Contains metadata about the session and its data.
    """
    session_id: str
    status: str
    filename: str
    row_count: int
    column_count: int
    columns: List[ColumnInfo]
    data_statistics: Dict[str, Any]
    numeric_columns: List[str]
    categorical_columns: List[str]
    datetime_columns: List[str]
    text_columns: List[str]
    created_at: str
    expires_at: str


class PatternType(str, Enum):
    """Types of data patterns that can be detected."""
    TIME_SERIES = "time_series"
    COMPARISON = "comparison"
    COMPOSITION = "composition"
    CORRELATION = "correlation"
    DISTRIBUTION = "distribution"
    RANKING = "ranking"
    TREND = "trend"
    UNKNOWN = "unknown"


class DataAnalysis(BaseModel):
    """
    Result of data structure analysis.

    Contains deep analysis of the data including
    patterns, recommendations, and statistics.
    """
    session_id: str
    row_count: int
    column_count: int

    # Column analysis
    numeric_summary: Dict[str, Dict[str, float]]  # col -> {min, max, mean, etc.}
    categorical_summary: Dict[str, Dict[str, int]]  # col -> value counts
    datetime_summary: Dict[str, Dict[str, str]]  # col -> {min, max, range}

    # Pattern detection
    detected_patterns: List[PatternType]
    pattern_confidence: Dict[str, float]  # pattern -> confidence

    # Data quality
    null_percentage: float
    duplicate_rows: int

    # Recommendations
    recommended_visualizations: List[str]
    recommended_groupings: List[str]
    potential_issues: List[str]


class IntentType(str, Enum):
    """Types of user visualization intent."""
    SHOW_DISTRIBUTION = "show_distribution"
    COMPARE_VALUES = "compare_values"
    SHOW_TREND = "show_trend"
    SHOW_COMPOSITION = "show_composition"
    SHOW_CORRELATION = "show_correlation"
    SHOW_RANKING = "show_ranking"
    AGGREGATE_DATA = "aggregate_data"
    FILTER_DATA = "filter_data"
    UNKNOWN = "unknown"


class VisualizationIntent(BaseModel):
    """
    Parsed user intent from narrative.

    The intent parsing tool extracts:
    - What the user wants to see
    - Which columns are relevant
    - What transformations might be needed
    """
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0)

    # Column references
    target_columns: List[str]  # Columns to visualize
    group_by_columns: List[str]  # Columns to group by
    filter_columns: List[str]  # Columns mentioned in filters

    # Aggregation
    aggregation_function: Optional[str] = None  # sum, avg, count, etc.

    # Filter
    filter_expression: Optional[str] = None

    # Chart preferences
    suggested_chart_type: Optional[str] = None
    chart_title_suggestion: Optional[str] = None

    # Extracted entities
    time_references: List[str] = Field(default_factory=list)
    numeric_references: List[str] = Field(default_factory=list)

    # Original narrative for reference
    original_narrative: str


class ChartTypeId(str, Enum):
    """Available chart types."""
    LINE = "line"
    BAR_VERTICAL = "bar_vertical"
    BAR_HORIZONTAL = "bar_horizontal"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    AREA = "area"
    AREA_STACKED = "area_stacked"
    BAR_GROUPED = "bar_grouped"
    BAR_STACKED = "bar_stacked"
    WATERFALL = "waterfall"
    RADAR = "radar"
    POLAR_AREA = "polar_area"


class ChartRecommendation(BaseModel):
    """
    Chart type recommendation from analysis.

    Includes confidence score and reasoning.
    """
    chart_type: ChartTypeId
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    data_requirements: Dict[str, str]  # What columns needed
    limitations: List[str] = Field(default_factory=list)


class TransformResult(BaseModel):
    """
    Result of data transformation.

    Contains the transformed data ready for charting.
    """
    success: bool
    rows_before: int
    rows_after: int

    # Transformed data
    labels: List[str]
    values: List[float]
    series_data: Optional[Dict[str, List[float]]] = None  # For multi-series

    # Metadata
    aggregation_applied: Optional[str] = None
    group_by_applied: List[str] = Field(default_factory=list)
    filter_applied: Optional[str] = None

    # Warnings
    warnings: List[str] = Field(default_factory=list)


class ChartResult(BaseModel):
    """
    Result of chart generation.

    Contains the generated chart HTML and metadata.
    """
    success: bool
    chart_html: str
    chart_title: str
    chart_type: ChartTypeId

    # Optional insights
    insights_html: Optional[str] = None

    # Metadata
    data_points_used: int
    generation_time_ms: float

    # For persistence
    chart_id: Optional[str] = None
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None


class ValidationResult(BaseModel):
    """
    Result of chart validation.

    Checks that the generated chart meets quality standards.
    """
    valid: bool
    score: float = Field(ge=0.0, le=1.0)

    # Quality checks
    data_accuracy: bool
    visual_quality: bool
    label_clarity: bool
    appropriate_chart_type: bool

    # Issues found
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class AlternativeSuggestion(BaseModel):
    """
    Alternative visualization suggestion.

    When the primary chart might not be optimal.
    """
    chart_type: ChartTypeId
    reason: str
    confidence: float
    would_require: Optional[str] = None  # Data transformation needed
