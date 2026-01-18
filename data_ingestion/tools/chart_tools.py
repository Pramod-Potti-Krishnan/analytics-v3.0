"""
Chart generation tools for Data Ingestion Agent.

Wraps the existing AtomicChartGenerator without modification.
"""

import logging
import time
from typing import Optional, List, Dict, Any

from ..models.tools import (
    ChartResult,
    ChartTypeId,
    TransformResult,
    VisualizationIntent
)

logger = logging.getLogger(__name__)


async def generate_chart(
    transform_result: TransformResult,
    intent: VisualizationIntent,
    presentation_id: Optional[str] = None,
    slide_id: Optional[str] = None,
    chart_index: int = 0,
    width: int = 850,
    height: int = 500,
    include_insights: bool = False,
    chart_title: Optional[str] = None
) -> ChartResult:
    """
    Generate chart using existing AtomicChartGenerator.

    This tool wraps the AtomicChartGenerator without modifying it.
    It adapts the transformed data to the format expected by the generator.

    Args:
        transform_result: Transformed data from transform_data tool
        intent: Parsed visualization intent
        presentation_id: Presentation ID for persistence
        slide_id: Slide ID for persistence
        chart_index: Index for multiple charts
        width: Chart width in pixels
        height: Chart height in pixels
        include_insights: Include Key Insights panel
        chart_title: Optional chart title override

    Returns:
        ChartResult with generated chart HTML
    """
    logger.info(
        f"Tool: generate_chart with {len(transform_result.labels)} data points, "
        f"suggested type: {intent.suggested_chart_type}"
    )

    start_time = time.time()

    # Import AtomicChartGenerator (lazy import to avoid circular deps)
    from core.atomic_chart_generator import AtomicChartGenerator
    from models.atomic_models import AtomicChartRequest

    # Determine chart type
    chart_type = _determine_chart_type(
        intent.suggested_chart_type,
        transform_result,
        intent
    )

    # Prepare data for AtomicChartGenerator
    data = _prepare_chart_data(transform_result, chart_type)

    # Determine title
    title = chart_title or intent.chart_title_suggestion or _generate_default_title(
        intent, transform_result
    )

    # Create request for AtomicChartGenerator
    request = AtomicChartRequest(
        presentation_id=presentation_id or "data-ingestion",
        slide_id=slide_id or "generated",
        chart_index=chart_index,
        narrative=intent.original_narrative,
        include_insights=include_insights,
        width=width,
        height=height,
        chart_title=title,
        show_title=True,
        data=data
    )

    try:
        # Generate chart using existing generator
        generator = AtomicChartGenerator()
        response = await generator.generate(chart_type, request)

        generation_time = (time.time() - start_time) * 1000

        return ChartResult(
            success=True,
            chart_html=response.chart_html,
            chart_title=response.title or title,
            chart_type=ChartTypeId(chart_type),
            insights_html=response.insights_html if include_insights else None,
            data_points_used=len(transform_result.labels),
            generation_time_ms=generation_time,
            chart_id=response.chart_id,
            presentation_id=presentation_id,
            slide_id=slide_id
        )

    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        generation_time = (time.time() - start_time) * 1000

        # Return error result
        return ChartResult(
            success=False,
            chart_html=_generate_error_html(str(e)),
            chart_title=title,
            chart_type=ChartTypeId(chart_type),
            insights_html=None,
            data_points_used=0,
            generation_time_ms=generation_time,
            chart_id=None,
            presentation_id=presentation_id,
            slide_id=slide_id
        )


def _determine_chart_type(
    suggested: Optional[str],
    transform_result: TransformResult,
    intent: VisualizationIntent
) -> str:
    """Determine the best chart type to use."""
    # Use suggested if valid
    valid_types = [ct.value for ct in ChartTypeId]

    if suggested and suggested in valid_types:
        return suggested

    # Infer from intent type
    intent_to_chart = {
        "show_trend": "line",
        "compare_values": "bar_vertical",
        "show_composition": "pie",
        "show_ranking": "bar_horizontal",
        "show_correlation": "scatter",
        "show_distribution": "bar_vertical",
        "aggregate_data": "bar_vertical",
    }

    chart_type = intent_to_chart.get(intent.intent_type.value, "bar_vertical")

    # Validate data compatibility
    num_points = len(transform_result.labels)

    # Pie/doughnut work best with 2-8 points
    if chart_type in ("pie", "doughnut") and num_points > 8:
        chart_type = "bar_horizontal"

    # Scatter needs x/y data
    if chart_type == "scatter" and not transform_result.series_data:
        chart_type = "bar_vertical"

    return chart_type


def _prepare_chart_data(
    transform_result: TransformResult,
    chart_type: str
) -> List[Dict[str, Any]]:
    """Prepare data in format expected by AtomicChartGenerator."""
    data = []

    if chart_type in ("scatter", "bubble"):
        # Scatter/bubble need x, y format
        for i, (label, value) in enumerate(
            zip(transform_result.labels, transform_result.values)
        ):
            point = {
                "x": i,
                "y": value,
                "label": label
            }
            if chart_type == "bubble":
                point["r"] = abs(value) / max(transform_result.values) * 20 + 5
            data.append(point)

    elif chart_type == "waterfall":
        # Waterfall needs special format
        running_total = 0
        for label, value in zip(transform_result.labels, transform_result.values):
            data.append({
                "label": label,
                "start": running_total,
                "end": running_total + value
            })
            running_total += value

    elif transform_result.series_data:
        # Multi-series data
        data = {
            "labels": transform_result.labels,
            "datasets": [
                {"label": name, "data": values}
                for name, values in transform_result.series_data.items()
            ]
        }

    else:
        # Standard label/value format
        for label, value in zip(transform_result.labels, transform_result.values):
            data.append({
                "label": str(label),
                "value": float(value) if value is not None else 0
            })

    return data


def _generate_default_title(
    intent: VisualizationIntent,
    transform_result: TransformResult
) -> str:
    """Generate a default title from intent and data."""
    if intent.target_columns and intent.group_by_columns:
        return f"{intent.target_columns[0].replace('_', ' ').title()} by {intent.group_by_columns[0].replace('_', ' ').title()}"

    if intent.target_columns:
        return f"{intent.target_columns[0].replace('_', ' ').title()} Analysis"

    if transform_result.aggregation_applied:
        return f"{transform_result.aggregation_applied.title()} Analysis"

    return "Data Visualization"


def _generate_error_html(error_message: str) -> str:
    """Generate error placeholder HTML."""
    return f"""
    <div style="
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 20px;
        font-family: system-ui, sans-serif;
    ">
        <div style="color: #dc2626; font-size: 18px; margin-bottom: 10px;">
            Chart Generation Failed
        </div>
        <div style="color: #7f1d1d; font-size: 14px; text-align: center;">
            {error_message}
        </div>
    </div>
    """
