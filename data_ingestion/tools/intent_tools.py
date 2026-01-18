"""
Intent parsing tools for Data Ingestion Agent.

Uses OpenAI API to extract visualization intent from natural language.
"""

import logging
import json
import re
from typing import Optional, Dict, Any, List

from ..models.tools import (
    VisualizationIntent,
    IntentType,
    SessionInfo
)
from ..settings import get_data_ingestion_settings

logger = logging.getLogger(__name__)


async def parse_user_intent(
    narrative: str,
    session_info: SessionInfo,
    use_llm: bool = True
) -> VisualizationIntent:
    """
    Parse user intent from natural language narrative.

    Uses OpenAI API for sophisticated intent extraction,
    with fallback to rule-based parsing if API unavailable.

    Args:
        narrative: User's description of desired visualization
        session_info: Session information with column metadata
        use_llm: Whether to use LLM (True) or rule-based (False)

    Returns:
        VisualizationIntent with extracted intent
    """
    logger.info(f"Tool: parse_user_intent for narrative: {narrative[:100]}...")

    settings = get_data_ingestion_settings()

    # Try LLM-based parsing if enabled and API key available
    if use_llm and settings.OPENAI_API_KEY:
        try:
            return await _parse_with_openai(narrative, session_info, settings)
        except Exception as e:
            logger.warning(f"LLM intent parsing failed, falling back to rules: {e}")

    # Fallback to rule-based parsing
    return _parse_with_rules(narrative, session_info)


async def _parse_with_openai(
    narrative: str,
    session_info: SessionInfo,
    settings
) -> VisualizationIntent:
    """Parse intent using OpenAI API."""
    import openai

    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # Build column context
    columns_context = []
    for col in session_info.columns:
        col_info = f"- {col.name} ({col.dtype})"
        if col.sample_values:
            samples = ", ".join(str(v) for v in col.sample_values[:3])
            col_info += f" - samples: {samples}"
        columns_context.append(col_info)

    system_prompt = """You are a data visualization intent parser. Extract the user's visualization intent from their natural language description.

Given the user's narrative and available data columns, determine:
1. What type of visualization they want (show_distribution, compare_values, show_trend, show_composition, show_correlation, show_ranking, aggregate_data, filter_data)
2. Which columns are relevant
3. Any aggregation or grouping needed
4. Suggested chart type

Respond with a JSON object containing:
- intent_type: one of [show_distribution, compare_values, show_trend, show_composition, show_correlation, show_ranking, aggregate_data, filter_data, unknown]
- confidence: float 0-1
- target_columns: list of column names to visualize
- group_by_columns: list of columns to group by
- filter_columns: list of columns mentioned in filters
- aggregation_function: one of [sum, avg, count, min, max, null]
- filter_expression: SQL-like filter expression or null
- suggested_chart_type: one of [line, bar_vertical, bar_horizontal, pie, doughnut, scatter, area, waterfall, null]
- chart_title_suggestion: suggested title string"""

    user_prompt = f"""Available columns:
{chr(10).join(columns_context)}

User's request: "{narrative}"

Parse the intent and return JSON only."""

    try:
        response = await client.chat.completions.create(
            model=settings.INTENT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # Map intent type
        intent_type_map = {
            "show_distribution": IntentType.SHOW_DISTRIBUTION,
            "compare_values": IntentType.COMPARE_VALUES,
            "show_trend": IntentType.SHOW_TREND,
            "show_composition": IntentType.SHOW_COMPOSITION,
            "show_correlation": IntentType.SHOW_CORRELATION,
            "show_ranking": IntentType.SHOW_RANKING,
            "aggregate_data": IntentType.AGGREGATE_DATA,
            "filter_data": IntentType.FILTER_DATA,
        }

        intent_type = intent_type_map.get(
            result.get("intent_type", "unknown"),
            IntentType.UNKNOWN
        )

        return VisualizationIntent(
            intent_type=intent_type,
            confidence=float(result.get("confidence", 0.8)),
            target_columns=_validate_columns(
                result.get("target_columns", []),
                session_info
            ),
            group_by_columns=_validate_columns(
                result.get("group_by_columns", []),
                session_info
            ),
            filter_columns=_validate_columns(
                result.get("filter_columns", []),
                session_info
            ),
            aggregation_function=result.get("aggregation_function"),
            filter_expression=result.get("filter_expression"),
            suggested_chart_type=result.get("suggested_chart_type"),
            chart_title_suggestion=result.get("chart_title_suggestion"),
            time_references=_extract_time_references(narrative),
            numeric_references=_extract_numeric_references(narrative),
            original_narrative=narrative
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response: {e}")
        raise
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise


def _parse_with_rules(
    narrative: str,
    session_info: SessionInfo
) -> VisualizationIntent:
    """Parse intent using rule-based approach."""
    narrative_lower = narrative.lower()

    # Detect intent type from keywords
    intent_type = IntentType.UNKNOWN
    confidence = 0.5

    # Trend/time series keywords
    if any(kw in narrative_lower for kw in [
        "trend", "over time", "growth", "decline", "timeline",
        "monthly", "quarterly", "yearly", "by month", "by quarter", "by year"
    ]):
        intent_type = IntentType.SHOW_TREND
        confidence = 0.85

    # Comparison keywords
    elif any(kw in narrative_lower for kw in [
        "compare", "vs", "versus", "difference", "against",
        "between", "across"
    ]):
        intent_type = IntentType.COMPARE_VALUES
        confidence = 0.8

    # Composition keywords
    elif any(kw in narrative_lower for kw in [
        "breakdown", "distribution", "share", "percentage",
        "proportion", "parts", "composition"
    ]):
        intent_type = IntentType.SHOW_COMPOSITION
        confidence = 0.8

    # Ranking keywords
    elif any(kw in narrative_lower for kw in [
        "top", "bottom", "highest", "lowest", "best", "worst",
        "ranking", "rank"
    ]):
        intent_type = IntentType.SHOW_RANKING
        confidence = 0.8

    # Correlation keywords
    elif any(kw in narrative_lower for kw in [
        "correlation", "relationship", "scatter", "vs"
    ]) and len(session_info.numeric_columns) >= 2:
        intent_type = IntentType.SHOW_CORRELATION
        confidence = 0.75

    # Distribution keywords
    elif any(kw in narrative_lower for kw in [
        "distribution", "spread", "histogram"
    ]):
        intent_type = IntentType.SHOW_DISTRIBUTION
        confidence = 0.75

    # Aggregation keywords
    elif any(kw in narrative_lower for kw in [
        "total", "sum", "average", "avg", "count", "aggregate"
    ]):
        intent_type = IntentType.AGGREGATE_DATA
        confidence = 0.8

    # Filter keywords
    elif any(kw in narrative_lower for kw in [
        "filter", "where", "only", "exclude", "include"
    ]):
        intent_type = IntentType.FILTER_DATA
        confidence = 0.7

    # Find mentioned columns
    target_columns = []
    group_by_columns = []
    available_columns = [col.name.lower() for col in session_info.columns]

    for col in session_info.columns:
        col_lower = col.name.lower()
        if col_lower in narrative_lower or col.name in narrative:
            if col.dtype == "numeric":
                target_columns.append(col.name)
            elif col.dtype in ("categorical", "datetime"):
                group_by_columns.append(col.name)

    # If no columns found, use defaults
    if not target_columns and session_info.numeric_columns:
        target_columns = session_info.numeric_columns[:1]

    if not group_by_columns:
        if session_info.datetime_columns and intent_type == IntentType.SHOW_TREND:
            group_by_columns = session_info.datetime_columns[:1]
        elif session_info.categorical_columns:
            group_by_columns = session_info.categorical_columns[:1]

    # Detect aggregation function
    aggregation_function = None
    if "sum" in narrative_lower or "total" in narrative_lower:
        aggregation_function = "sum"
    elif "average" in narrative_lower or "avg" in narrative_lower or "mean" in narrative_lower:
        aggregation_function = "avg"
    elif "count" in narrative_lower:
        aggregation_function = "count"
    elif "max" in narrative_lower or "highest" in narrative_lower:
        aggregation_function = "max"
    elif "min" in narrative_lower or "lowest" in narrative_lower:
        aggregation_function = "min"

    # Suggest chart type
    suggested_chart = _suggest_chart_type(intent_type, session_info)

    # Generate title suggestion
    title_suggestion = _generate_title_suggestion(
        narrative, target_columns, group_by_columns
    )

    return VisualizationIntent(
        intent_type=intent_type,
        confidence=confidence,
        target_columns=target_columns,
        group_by_columns=group_by_columns,
        filter_columns=[],
        aggregation_function=aggregation_function,
        filter_expression=None,
        suggested_chart_type=suggested_chart,
        chart_title_suggestion=title_suggestion,
        time_references=_extract_time_references(narrative),
        numeric_references=_extract_numeric_references(narrative),
        original_narrative=narrative
    )


def _validate_columns(columns: List[str], session_info: SessionInfo) -> List[str]:
    """Validate that columns exist in session."""
    available = {col.name for col in session_info.columns}
    available_lower = {col.name.lower(): col.name for col in session_info.columns}

    valid = []
    for col in columns:
        if col in available:
            valid.append(col)
        elif col.lower() in available_lower:
            valid.append(available_lower[col.lower()])

    return valid


def _suggest_chart_type(
    intent_type: IntentType,
    session_info: SessionInfo
) -> Optional[str]:
    """Suggest chart type based on intent and data."""
    suggestions = {
        IntentType.SHOW_TREND: "line",
        IntentType.COMPARE_VALUES: "bar_vertical",
        IntentType.SHOW_COMPOSITION: "pie",
        IntentType.SHOW_RANKING: "bar_horizontal",
        IntentType.SHOW_CORRELATION: "scatter",
        IntentType.SHOW_DISTRIBUTION: "bar_vertical",
        IntentType.AGGREGATE_DATA: "bar_vertical",
    }

    return suggestions.get(intent_type)


def _generate_title_suggestion(
    narrative: str,
    target_columns: List[str],
    group_by_columns: List[str]
) -> str:
    """Generate a title suggestion from narrative."""
    # Extract first meaningful phrase
    words = narrative.split()[:8]
    title = " ".join(words)

    # Capitalize appropriately
    title = title.title()

    # Add column context if short
    if len(title) < 20 and target_columns:
        if group_by_columns:
            title = f"{target_columns[0].replace('_', ' ').title()} by {group_by_columns[0].replace('_', ' ').title()}"

    return title[:100]


def _extract_time_references(narrative: str) -> List[str]:
    """Extract time references from narrative."""
    patterns = [
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
        r'\b(q[1-4])\b',
        r'\b(20\d{2})\b',
        r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
        r'\b(weekly|monthly|quarterly|yearly|daily)\b',
    ]

    references = []
    narrative_lower = narrative.lower()

    for pattern in patterns:
        matches = re.findall(pattern, narrative_lower)
        references.extend(matches)

    return list(set(references))


def _extract_numeric_references(narrative: str) -> List[str]:
    """Extract numeric references from narrative."""
    # Find numbers with context
    patterns = [
        r'\$[\d,]+(?:\.\d+)?',  # Currency
        r'\d+(?:\.\d+)?%',       # Percentages
        r'\d{4,}',               # Large numbers
    ]

    references = []
    for pattern in patterns:
        matches = re.findall(pattern, narrative)
        references.extend(matches)

    return references
