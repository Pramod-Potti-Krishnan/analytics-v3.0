"""
Chart Data API Routes (FastAPI)

Handles saving and loading chart data edits for interactive editor.
Supports simple, multi-series, scatter/bubble, and waterfall chart formats.

v3.7.14 Changes:
- FEATURE: Added WaterfallDataPoint model for waterfall chart persistence
- FEATURE: Added waterfall_data field to ChartDataUpdate model
- Waterfall charts now use dedicated start/end data format
- Save/retrieve logic handles waterfall's floating bar format
- Fixes: Waterfall chart edits not persisting (TypeError on [[start,end]] format)

v3.7.3 Changes:
- Implemented Supabase persistence for chart data edits
- Added GET /get-data/{presentation_id}/{chart_id} endpoint
- Upsert logic for save/update operations
"""

import logging
import os
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from supabase import create_client, Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/charts", tags=["Interactive Editor"])

# Initialize Supabase client for database operations
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """Get or create Supabase client for database operations."""
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if url and key:
            try:
                _supabase_client = create_client(url, key)
                logger.info("Supabase client initialized for chart data persistence")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
    return _supabase_client


# ========================================
# MODELS
# ========================================

class DatasetSchema(BaseModel):
    """Single dataset in multi-series format."""
    label: str = Field(..., min_length=1, description="Series name/label")
    data: List[float] = Field(..., min_length=2, max_length=50, description="Data points for this series")

    @validator('data')
    def validate_data(cls, v):
        """Validate data array contains valid numbers."""
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Data point at index {i} must be a number, got {type(val).__name__}")
            if val != val:  # NaN check
                raise ValueError(f"Data point at index {i} cannot be NaN")
            if abs(val) == float('inf'):
                raise ValueError(f"Data point at index {i} cannot be infinity")
        return [float(val) for val in v]


class ScatterBubbleDataPoint(BaseModel):
    """Single data point for scatter/bubble charts."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    r: Optional[float] = Field(default=None, description="Bubble radius (bubble charts only)")
    label: str = Field(..., min_length=1, description="Point label")

    @validator('x', 'y', 'r')
    def validate_numeric(cls, v, values, **kwargs):
        """Validate numeric values."""
        if v is None:
            return v  # r is optional

        if v != v:  # NaN check
            raise ValueError("Value cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError("Value cannot be infinity")

        return v


class WaterfallDataPoint(BaseModel):
    """Single data point for waterfall charts (floating bars)."""
    label: str = Field(..., min_length=1, description="Step label")
    start: float = Field(..., description="Bar start position")
    end: float = Field(..., description="Bar end position")

    @validator('start', 'end')
    def validate_numeric(cls, v):
        """Validate numeric values for waterfall data points."""
        if v != v:  # NaN check
            raise ValueError("Value cannot be NaN")
        if abs(v) == float('inf'):
            raise ValueError("Value cannot be infinity")
        return v


class ChartDataUpdate(BaseModel):
    """Request to update chart data - supports simple, multi-series, and scatter/bubble formats."""
    chart_id: str = Field(..., min_length=1, description="Chart identifier")
    presentation_id: str = Field(..., min_length=1, description="Presentation UUID")
    chart_type: str = Field(..., description="Chart type (e.g., 'scatter', 'bubble', 'bar', etc.)")

    # Simple charts: labels + values
    labels: Optional[List[str]] = Field(default=None, min_length=2, max_length=50, description="X-axis labels (simple charts)")
    values: Optional[List[float]] = Field(default=None, min_length=2, max_length=50, description="Y-axis values (simple charts)")

    # Multi-series charts: labels + datasets
    datasets: Optional[List[DatasetSchema]] = Field(default=None, min_length=1, max_length=20, description="Multiple data series (multi-series charts)")

    # Scatter/bubble charts: data points with x/y/r coordinates
    data: Optional[List[ScatterBubbleDataPoint]] = Field(default=None, min_length=2, max_length=50, description="Data points for scatter/bubble charts")

    # Waterfall charts: data points with start/end values (floating bars)
    waterfall_data: Optional[List[WaterfallDataPoint]] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Data points for waterfall charts"
    )

    timestamp: Optional[str] = Field(default=None, description="Update timestamp")

    @validator('chart_id', 'presentation_id')
    def validate_ids(cls, v):
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty or whitespace")
        return v.strip()

    @validator('labels')
    def validate_labels(cls, v):
        """Validate labels array (optional for scatter/bubble)."""
        if v is None:
            return v  # Optional for scatter/bubble charts

        if len(v) < 2:
            raise ValueError("At least 2 labels required")
        if len(v) > 50:
            raise ValueError("Maximum 50 labels allowed")

        # Check for empty labels
        for i, label in enumerate(v):
            if not label or not str(label).strip():
                raise ValueError(f"Label at index {i} cannot be empty")

        # Check for duplicate labels
        if len(v) != len(set(v)):
            raise ValueError("Duplicate labels found. Each label must be unique")

        return [str(label).strip() for label in v]

    @validator('data', always=True)
    def validate_format(cls, v, values):
        """Validate that appropriate data format is provided based on chart type."""
        chart_type = values.get('chart_type', '')
        has_labels = values.get('labels') is not None
        has_values = values.get('values') is not None
        has_datasets = values.get('datasets') is not None
        has_data = v is not None  # scatter/bubble data
        has_waterfall = values.get('waterfall_data') is not None

        # v3.7.14: Waterfall charts: require 'waterfall_data' field
        if chart_type == 'waterfall':
            if not has_waterfall:
                raise ValueError("Waterfall charts require 'waterfall_data' field with start/end values")
            if has_labels or has_values or has_datasets or has_data:
                raise ValueError("Waterfall charts should only use 'waterfall_data' field")
            return v

        # Scatter/bubble charts: require 'data' field
        if chart_type in ['scatter', 'bubble']:
            if not has_data:
                raise ValueError(f"{chart_type} charts require 'data' field with x/y coordinates")
            if has_labels or has_values or has_datasets:
                raise ValueError(f"{chart_type} charts should only use 'data' field, not labels/values/datasets")

            # Validate bubble charts have radius
            if chart_type == 'bubble':
                for i, point in enumerate(v):
                    if point.r is None:
                        raise ValueError(f"Bubble chart data point {i} missing radius 'r'")

            return v

        # Multi-series charts: require labels + datasets
        if has_datasets:
            if not has_labels:
                raise ValueError("Multi-series charts require 'labels' field")
            if has_values or has_data:
                raise ValueError("Cannot mix datasets with values or data")

            labels = values.get('labels', [])
            datasets = values.get('datasets', [])
            for i, ds in enumerate(datasets):
                if len(ds.data) != len(labels):
                    raise ValueError(
                        f"Dataset {i} ('{ds.label}'): data length ({len(ds.data)}) "
                        f"must match labels length ({len(labels)})"
                    )
            return v

        # Simple charts: require labels + values
        if has_values:
            if not has_labels:
                raise ValueError("Simple charts require 'labels' field")
            if has_datasets or has_data:
                raise ValueError("Cannot mix values with datasets or data")

            labels = values.get('labels', [])
            vals = values.get('values', [])
            if len(vals) != len(labels):
                raise ValueError(f"Number of values ({len(vals)}) must match number of labels ({len(labels)})")

            for i, val in enumerate(vals):
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Value at index {i} must be a number, got {type(val).__name__}")
                if val != val:  # NaN check
                    raise ValueError(f"Value at index {i} cannot be NaN")
                if abs(val) == float('inf'):
                    raise ValueError(f"Value at index {i} cannot be infinity")
            return v

        # No valid format provided
        raise ValueError("Must provide either: (1) labels+values for simple charts, (2) labels+datasets for multi-series, (3) data for scatter/bubble, or (4) waterfall_data for waterfall charts")


class ChartDataDelete(BaseModel):
    """Request to delete chart data."""
    chart_id: str = Field(..., min_length=1, description="Chart identifier")
    presentation_id: str = Field(..., min_length=1, description="Presentation UUID")

    @validator('chart_id', 'presentation_id')
    def validate_ids(cls, v):
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty or whitespace")
        return v.strip()


# ========================================
# ENDPOINTS
# ========================================

@router.post("/update-data")
async def update_chart_data(data: ChartDataUpdate):
    """
    Save edited chart data (for interactive editor).

    Supports both single-series (labels + values) and multi-series (labels + datasets) formats.

    Args:
        data: Chart data with labels and either values (single-series) or datasets (multi-series)

    Returns:
        Success status and message with format information
    """
    try:
        # Determine format based on chart_type and available fields
        is_waterfall = data.chart_type == 'waterfall' and data.waterfall_data is not None
        is_scatter_bubble = data.chart_type in ['scatter', 'bubble'] and data.data is not None
        is_multi_series = data.datasets is not None and not is_scatter_bubble and not is_waterfall

        if is_waterfall:
            format_type = "waterfall"
            logger.info(
                f"Updating waterfall chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.waterfall_data)} steps)"
            )
        elif is_scatter_bubble:
            format_type = data.chart_type
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.data)} data points)"
            )
        elif is_multi_series:
            format_type = "multi-series"
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.datasets)} series, {len(data.labels)} labels)"
            )
        else:
            format_type = "single-series"
            logger.info(
                f"Updating {format_type} chart data: {data.chart_id} in presentation {data.presentation_id} "
                f"({len(data.labels)} labels, {len(data.values)} values)"
            )

        # v3.7.3: Save to Supabase database
        supabase = get_supabase_client()
        persisted = False

        if supabase:
            try:
                # Prepare data for storage
                chart_data_record = {
                    "chart_id": data.chart_id,
                    "presentation_id": data.presentation_id,
                    "chart_type": data.chart_type,
                    "updated_at": datetime.utcnow().isoformat()
                }

                # Format-specific data storage
                if is_waterfall:
                    # v3.7.14: Waterfall stores labels + values with start/end
                    chart_data_record["labels"] = [p.label for p in data.waterfall_data]
                    chart_data_record["values"] = [
                        {"start": p.start, "end": p.end, "label": p.label}
                        for p in data.waterfall_data
                    ]
                elif is_scatter_bubble:
                    chart_data_record["labels"] = []  # Scatter/bubble don't use labels
                    chart_data_record["values"] = [
                        {"x": p.x, "y": p.y, "r": p.r, "label": p.label}
                        for p in data.data
                    ]
                elif is_multi_series:
                    chart_data_record["labels"] = data.labels
                    chart_data_record["values"] = [
                        {"label": ds.label, "data": ds.data}
                        for ds in data.datasets
                    ]
                else:
                    chart_data_record["labels"] = data.labels
                    chart_data_record["values"] = data.values

                # Upsert: Check if record exists, then update or insert
                existing = supabase.table("chart_data_edits").select("id").eq(
                    "chart_id", data.chart_id
                ).eq(
                    "presentation_id", data.presentation_id
                ).execute()

                if existing.data:
                    # Update existing record
                    result = supabase.table("chart_data_edits").update(
                        chart_data_record
                    ).eq(
                        "chart_id", data.chart_id
                    ).eq(
                        "presentation_id", data.presentation_id
                    ).execute()
                    logger.info(f"Updated chart data: {data.chart_id}")
                else:
                    # Insert new record
                    chart_data_record["created_at"] = datetime.utcnow().isoformat()
                    result = supabase.table("chart_data_edits").insert(
                        chart_data_record
                    ).execute()
                    logger.info(f"Inserted chart data: {data.chart_id}")

                persisted = True

            except Exception as db_error:
                logger.error(f"Database error: {db_error}", exc_info=True)
                # Continue without persistence - client-side still works

        response_data = {
            "success": True,
            "message": f"Chart data updated successfully ({format_type})",
            "chart_id": data.chart_id,
            "presentation_id": data.presentation_id,
            "format": format_type,
            "chart_type": data.chart_type,
            "updated_at": datetime.utcnow().isoformat(),
            "persisted": persisted  # v3.7.3: Indicate if saved to database
        }

        if is_waterfall:
            response_data["steps_count"] = len(data.waterfall_data)
        elif is_scatter_bubble:
            response_data["data_points_count"] = len(data.data)
        elif is_multi_series:
            response_data["labels_count"] = len(data.labels)
            response_data["series_count"] = len(data.datasets)
            response_data["series_names"] = [ds.label for ds in data.datasets]
        else:
            response_data["labels_count"] = len(data.labels)
            response_data["values_count"] = len(data.values)

        return response_data

    except Exception as e:
        logger.error(f"Failed to update chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-data/{presentation_id}")
async def get_all_chart_data(presentation_id: str):
    """
    Get all saved chart data for a presentation.

    v3.7.3: Implemented Supabase persistence retrieval.

    Args:
        presentation_id: Presentation UUID

    Returns:
        List of chart data edits for the presentation
    """
    try:
        logger.info(f"Fetching chart data for presentation: {presentation_id}")

        supabase = get_supabase_client()
        charts = []

        if supabase:
            try:
                result = supabase.table("chart_data_edits").select("*").eq(
                    "presentation_id", presentation_id
                ).execute()

                if result.data:
                    charts = [
                        {
                            "chart_id": record["chart_id"],
                            "labels": record.get("labels", []),
                            "values": record.get("values", []),
                            "chart_type": record.get("chart_type"),
                            "updated_at": record.get("updated_at")
                        }
                        for record in result.data
                    ]
                    logger.info(f"Retrieved {len(charts)} chart edits for {presentation_id}")

            except Exception as db_error:
                logger.error(f"Database error fetching charts: {db_error}")

        return {
            "success": True,
            "presentation_id": presentation_id,
            "charts": charts,
            "count": len(charts)
        }

    except Exception as e:
        logger.error(f"Failed to fetch chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-data/{presentation_id}/{chart_id}")
async def get_specific_chart_data(presentation_id: str, chart_id: str):
    """
    Get saved data for a specific chart.

    v3.7.3: New endpoint for retrieving individual chart edits.

    Args:
        presentation_id: Presentation UUID
        chart_id: Chart element ID

    Returns:
        Chart data if found, or success=False if no saved data
    """
    try:
        logger.info(f"Fetching chart data: {chart_id} in {presentation_id}")

        supabase = get_supabase_client()

        if supabase:
            try:
                result = supabase.table("chart_data_edits").select("*").eq(
                    "chart_id", chart_id
                ).eq(
                    "presentation_id", presentation_id
                ).execute()

                if result.data and len(result.data) > 0:
                    record = result.data[0]
                    values = record.get("values", [])
                    chart_type = record.get("chart_type", "")

                    # v3.7.14: Detect waterfall format (has start/end in values)
                    is_waterfall = (
                        chart_type == 'waterfall' and
                        len(values) > 0 and
                        isinstance(values[0], dict) and
                        'start' in values[0] and
                        'end' in values[0]
                    )

                    # v3.7.10: Detect and return multi-series format as 'datasets'
                    multi_series_charts = ['area_stacked', 'bar_grouped', 'bar_stacked']
                    is_multi_series = (
                        chart_type in multi_series_charts and
                        len(values) > 0 and
                        isinstance(values[0], dict) and
                        'label' in values[0] and
                        'data' in values[0]
                    )

                    response_data = {
                        "chart_id": record["chart_id"],
                        "presentation_id": record["presentation_id"],
                        "labels": record.get("labels", []),
                        "chart_type": chart_type,
                        "updated_at": record.get("updated_at")
                    }

                    if is_waterfall:
                        # v3.7.14: Return as 'waterfall_data' for waterfall charts
                        response_data["waterfall_data"] = values
                    elif is_multi_series:
                        # Return as 'datasets' for multi-series charts
                        response_data["datasets"] = values
                    else:
                        # Return as 'values' for other chart types
                        response_data["values"] = values

                    return {
                        "success": True,
                        "data": response_data
                    }

            except Exception as db_error:
                logger.error(f"Database error: {db_error}")

        # No saved data found
        return {
            "success": False,
            "message": "No saved data found for this chart",
            "chart_id": chart_id,
            "presentation_id": presentation_id
        }

    except Exception as e:
        logger.error(f"Failed to fetch chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-data")
async def delete_chart_data(request: ChartDataDelete):
    """
    Delete chart data for a specific chart.

    v3.7.3: Implemented Supabase persistence deletion.

    Args:
        request: Chart ID and presentation ID to delete

    Returns:
        Success status and message
    """
    try:
        logger.info(f"Deleting chart data: {request.chart_id} in presentation {request.presentation_id}")

        supabase = get_supabase_client()
        deleted = False

        if supabase:
            try:
                result = supabase.table("chart_data_edits").delete().eq(
                    "chart_id", request.chart_id
                ).eq(
                    "presentation_id", request.presentation_id
                ).execute()

                deleted = True
                logger.info(f"Deleted chart data: {request.chart_id}")

            except Exception as db_error:
                logger.error(f"Database error deleting chart: {db_error}")

        return {
            "success": True,
            "message": "Chart data deleted successfully",
            "chart_id": request.chart_id,
            "presentation_id": request.presentation_id,
            "deleted_from_db": deleted
        }

    except Exception as e:
        logger.error(f"Failed to delete chart data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
