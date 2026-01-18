"""
Validation tools for Data Ingestion Agent.

Provides tools for validating generated charts and suggesting alternatives.
"""

import logging
from typing import List, Optional

from ..models.tools import (
    ChartResult,
    ChartTypeId,
    TransformResult,
    VisualizationIntent,
    ValidationResult,
    AlternativeSuggestion,
    SessionInfo
)

logger = logging.getLogger(__name__)


async def validate_result(
    chart_result: ChartResult,
    transform_result: TransformResult,
    intent: VisualizationIntent
) -> ValidationResult:
    """
    Validate the generated chart result.

    Checks:
    - Data accuracy (all data points used)
    - Visual quality (reasonable size, no empty)
    - Label clarity (readable labels)
    - Chart type appropriateness

    Args:
        chart_result: Generated chart
        transform_result: Data used for chart
        intent: Original intent

    Returns:
        ValidationResult with quality assessment
    """
    logger.info(f"Tool: validate_result for chart type {chart_result.chart_type.value}")

    issues = []
    suggestions = []
    score = 1.0

    # Check 1: Data accuracy
    data_accuracy = True
    if chart_result.data_points_used != len(transform_result.labels):
        data_accuracy = False
        issues.append(
            f"Data point mismatch: {chart_result.data_points_used} used vs "
            f"{len(transform_result.labels)} expected"
        )
        score -= 0.2

    # Check 2: Visual quality
    visual_quality = True
    if not chart_result.chart_html or len(chart_result.chart_html) < 100:
        visual_quality = False
        issues.append("Chart HTML appears to be empty or too small")
        score -= 0.3

    if chart_result.data_points_used == 0:
        visual_quality = False
        issues.append("No data points in chart")
        score -= 0.4

    # Check 3: Label clarity
    label_clarity = True
    max_label_length = max(len(str(l)) for l in transform_result.labels) if transform_result.labels else 0

    if max_label_length > 50:
        label_clarity = False
        issues.append("Some labels are very long and may be truncated")
        suggestions.append("Consider using shorter labels or a horizontal bar chart")
        score -= 0.1

    if len(transform_result.labels) > 20:
        label_clarity = False
        issues.append("Many data points may make labels crowded")
        suggestions.append("Consider filtering to top/bottom N items")
        score -= 0.1

    # Check 4: Chart type appropriateness
    appropriate_chart = _check_chart_appropriateness(
        chart_result.chart_type,
        transform_result,
        intent
    )

    if not appropriate_chart["appropriate"]:
        issues.append(appropriate_chart["reason"])
        if appropriate_chart["suggestion"]:
            suggestions.append(appropriate_chart["suggestion"])
        score -= 0.15

    # Check for transform warnings
    if transform_result.warnings:
        for warning in transform_result.warnings:
            issues.append(f"Transform warning: {warning}")
            score -= 0.05

    # Normalize score
    score = max(0.0, min(1.0, score))

    return ValidationResult(
        valid=score >= 0.5,
        score=round(score, 2),
        data_accuracy=data_accuracy,
        visual_quality=visual_quality,
        label_clarity=label_clarity,
        appropriate_chart_type=appropriate_chart["appropriate"],
        issues=issues,
        suggestions=suggestions
    )


async def suggest_alternatives(
    chart_result: ChartResult,
    transform_result: TransformResult,
    intent: VisualizationIntent,
    session_info: SessionInfo
) -> List[AlternativeSuggestion]:
    """
    Suggest alternative visualizations.

    Analyzes the current chart and suggests alternatives that
    might better represent the data.

    Args:
        chart_result: Current chart result
        transform_result: Data used
        intent: Original intent
        session_info: Session information

    Returns:
        List of alternative suggestions
    """
    logger.info(f"Tool: suggest_alternatives for {chart_result.chart_type.value}")

    alternatives = []
    current_type = chart_result.chart_type

    num_points = len(transform_result.labels)
    has_negative = any(v < 0 for v in transform_result.values)
    has_series = transform_result.series_data is not None

    # Suggest based on data characteristics
    if current_type == ChartTypeId.BAR_VERTICAL:
        # Vertical bar alternatives
        if num_points > 8:
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.BAR_HORIZONTAL,
                reason="Horizontal bars work better with many categories",
                confidence=0.8
            ))

        if not has_negative and num_points <= 8:
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.PIE,
                reason="Pie chart can show composition if parts sum to a whole",
                confidence=0.6,
                would_require="Ensure values represent parts of a whole"
            ))

        alternatives.append(AlternativeSuggestion(
            chart_type=ChartTypeId.LINE,
            reason="Line chart if data has a natural order or time sequence",
            confidence=0.5
        ))

    elif current_type == ChartTypeId.LINE:
        alternatives.append(AlternativeSuggestion(
            chart_type=ChartTypeId.AREA,
            reason="Area chart emphasizes cumulative effect",
            confidence=0.7
        ))

        if not has_negative:
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.BAR_VERTICAL,
                reason="Bar chart for discrete category comparison",
                confidence=0.6
            ))

    elif current_type == ChartTypeId.PIE:
        alternatives.append(AlternativeSuggestion(
            chart_type=ChartTypeId.DOUGHNUT,
            reason="Doughnut provides similar view with center space for text",
            confidence=0.85
        ))

        alternatives.append(AlternativeSuggestion(
            chart_type=ChartTypeId.BAR_HORIZONTAL,
            reason="Bars allow precise value comparison",
            confidence=0.7
        ))

    elif current_type == ChartTypeId.SCATTER:
        if session_info.numeric_columns and len(session_info.numeric_columns) >= 3:
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.BUBBLE,
                reason="Bubble chart can show a third dimension",
                confidence=0.75,
                would_require="Select a third numeric column for bubble size"
            ))

    # Add multi-series suggestions if applicable
    if has_series:
        if current_type not in (ChartTypeId.AREA_STACKED, ChartTypeId.BAR_STACKED):
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.AREA_STACKED,
                reason="Stacked area shows cumulative trend across series",
                confidence=0.65
            ))

            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.BAR_STACKED,
                reason="Stacked bar shows total with series breakdown",
                confidence=0.65
            ))

    # Always suggest radar for multi-dimensional comparison
    if len(transform_result.labels) >= 3 and len(transform_result.labels) <= 10:
        if current_type != ChartTypeId.RADAR:
            alternatives.append(AlternativeSuggestion(
                chart_type=ChartTypeId.RADAR,
                reason="Radar chart for multi-dimensional profile comparison",
                confidence=0.5
            ))

    # Sort by confidence and limit
    alternatives.sort(key=lambda x: x.confidence, reverse=True)

    return alternatives[:5]


def _check_chart_appropriateness(
    chart_type: ChartTypeId,
    transform_result: TransformResult,
    intent: VisualizationIntent
) -> dict:
    """Check if chart type is appropriate for the data."""
    num_points = len(transform_result.labels)
    has_negative = any(v < 0 for v in transform_result.values)

    # Pie/doughnut checks
    if chart_type in (ChartTypeId.PIE, ChartTypeId.DOUGHNUT):
        if has_negative:
            return {
                "appropriate": False,
                "reason": "Pie/doughnut charts cannot show negative values",
                "suggestion": "Use bar chart instead"
            }
        if num_points > 10:
            return {
                "appropriate": False,
                "reason": "Too many slices (>10) makes pie charts hard to read",
                "suggestion": "Use bar chart or filter to top categories"
            }

    # Scatter/bubble checks
    if chart_type in (ChartTypeId.SCATTER, ChartTypeId.BUBBLE):
        if num_points < 5:
            return {
                "appropriate": False,
                "reason": "Scatter plots need more data points to show patterns",
                "suggestion": "Use bar chart for small datasets"
            }

    # Radar checks
    if chart_type == ChartTypeId.RADAR:
        if num_points < 3:
            return {
                "appropriate": False,
                "reason": "Radar charts need at least 3 dimensions",
                "suggestion": "Use bar chart instead"
            }
        if num_points > 10:
            return {
                "appropriate": False,
                "reason": "Too many axes makes radar charts confusing",
                "suggestion": "Limit to 5-8 dimensions"
            }

    # Waterfall checks
    if chart_type == ChartTypeId.WATERFALL:
        if num_points < 2:
            return {
                "appropriate": False,
                "reason": "Waterfall needs at least 2 steps",
                "suggestion": "Use simple bar chart"
            }

    return {"appropriate": True, "reason": None, "suggestion": None}
