"""
Analysis tools for Data Ingestion Agent.

Provides tools for deep data structure analysis and pattern detection.
"""

import logging
from typing import Dict, List, Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session_store import SessionStore
from ..database.query_executor import QueryExecutor
from ..models.tools import (
    DataAnalysis,
    PatternType,
    SessionInfo
)

logger = logging.getLogger(__name__)


async def analyze_data_structure(
    db_session: AsyncSession,
    session_info: SessionInfo
) -> DataAnalysis:
    """
    Perform deep analysis of data structure.

    Analyzes the data to understand:
    - Numeric distributions
    - Categorical value frequencies
    - Date ranges
    - Data quality issues
    - Recommended visualizations

    Args:
        db_session: Database session
        session_info: Session information from get_session_info

    Returns:
        DataAnalysis with comprehensive data analysis
    """
    logger.info(f"Tool: analyze_data_structure for session {session_info.session_id}")

    store = SessionStore(db_session)
    session = await store.get_session_by_str_id(session_info.session_id)

    if not session:
        raise ValueError(f"Session not found: {session_info.session_id}")

    executor = QueryExecutor(db_session)

    # Analyze numeric columns
    numeric_summary = {}
    for col_name in session_info.numeric_columns:
        try:
            agg_results = await executor.execute_aggregation(
                table_name=session.data_table_name,
                aggregations=[
                    {"func": "MIN", "column": col_name, "alias": "min_val"},
                    {"func": "MAX", "column": col_name, "alias": "max_val"},
                    {"func": "AVG", "column": col_name, "alias": "avg_val"},
                    {"func": "SUM", "column": col_name, "alias": "sum_val"},
                    {"func": "COUNT", "column": col_name, "alias": "count_val"},
                ]
            )
            if agg_results:
                result = agg_results[0]
                numeric_summary[col_name] = {
                    "min": float(result.get("min_val") or 0),
                    "max": float(result.get("max_val") or 0),
                    "mean": float(result.get("avg_val") or 0),
                    "sum": float(result.get("sum_val") or 0),
                    "count": int(result.get("count_val") or 0)
                }
        except Exception as e:
            logger.warning(f"Failed to analyze numeric column {col_name}: {e}")
            numeric_summary[col_name] = {"error": str(e)}

    # Analyze categorical columns
    categorical_summary = {}
    for col_name in session_info.categorical_columns:
        try:
            rows, _ = await executor.execute_select(
                table_name=session.data_table_name,
                columns=[col_name],
                limit=1000
            )
            # Count values
            value_counts = {}
            for row in rows:
                val = str(row.get(col_name, ""))
                value_counts[val] = value_counts.get(val, 0) + 1
            # Keep top 20
            sorted_counts = dict(
                sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            )
            categorical_summary[col_name] = sorted_counts
        except Exception as e:
            logger.warning(f"Failed to analyze categorical column {col_name}: {e}")
            categorical_summary[col_name] = {"error": str(e)}

    # Analyze datetime columns
    datetime_summary = {}
    for col_name in session_info.datetime_columns:
        try:
            agg_results = await executor.execute_aggregation(
                table_name=session.data_table_name,
                aggregations=[
                    {"func": "MIN", "column": col_name, "alias": "min_date"},
                    {"func": "MAX", "column": col_name, "alias": "max_date"},
                ]
            )
            if agg_results:
                result = agg_results[0]
                datetime_summary[col_name] = {
                    "min_date": str(result.get("min_date") or ""),
                    "max_date": str(result.get("max_date") or "")
                }
        except Exception as e:
            logger.warning(f"Failed to analyze datetime column {col_name}: {e}")
            datetime_summary[col_name] = {"error": str(e)}

    # Detect patterns
    detected_patterns, pattern_confidence = _detect_patterns_from_schema(
        session_info, numeric_summary, categorical_summary, datetime_summary
    )

    # Check for duplicates
    try:
        all_rows, total = await executor.execute_select(
            table_name=session.data_table_name,
            limit=session_info.row_count
        )
        # Simple duplicate check based on string representation
        unique_rows = len(set(str(row) for row in all_rows))
        duplicate_rows = total - unique_rows
    except Exception:
        duplicate_rows = 0

    # Generate recommendations
    recommendations = _generate_recommendations(
        session_info, detected_patterns, numeric_summary, categorical_summary
    )

    # Calculate null percentage
    total_cells = session_info.row_count * session_info.column_count
    total_nulls = sum(col.null_count for col in session_info.columns)
    null_percentage = (total_nulls / total_cells * 100) if total_cells > 0 else 0

    # Identify potential issues
    potential_issues = _identify_issues(
        session_info, null_percentage, duplicate_rows
    )

    return DataAnalysis(
        session_id=session_info.session_id,
        row_count=session_info.row_count,
        column_count=session_info.column_count,
        numeric_summary=numeric_summary,
        categorical_summary=categorical_summary,
        datetime_summary=datetime_summary,
        detected_patterns=detected_patterns,
        pattern_confidence=pattern_confidence,
        null_percentage=round(null_percentage, 2),
        duplicate_rows=duplicate_rows,
        recommended_visualizations=recommendations["visualizations"],
        recommended_groupings=recommendations["groupings"],
        potential_issues=potential_issues
    )


async def detect_patterns(
    session_info: SessionInfo,
    data_analysis: Optional[DataAnalysis] = None
) -> Dict[str, Any]:
    """
    Detect data patterns for visualization recommendations.

    Identifies patterns like:
    - Time series data
    - Comparison data
    - Composition data
    - Correlation data

    Args:
        session_info: Session information
        data_analysis: Optional existing analysis

    Returns:
        Dict with detected patterns and confidence scores
    """
    logger.info(f"Tool: detect_patterns for session {session_info.session_id}")

    patterns = []
    confidence = {}

    # Check for time series
    if session_info.datetime_columns:
        patterns.append(PatternType.TIME_SERIES)
        confidence[PatternType.TIME_SERIES.value] = 0.9

    # Check for comparison (categorical + numeric)
    if session_info.categorical_columns and session_info.numeric_columns:
        patterns.append(PatternType.COMPARISON)
        confidence[PatternType.COMPARISON.value] = 0.85

    # Check for composition (single numeric, multiple categories)
    if len(session_info.categorical_columns) >= 1 and len(session_info.numeric_columns) == 1:
        patterns.append(PatternType.COMPOSITION)
        confidence[PatternType.COMPOSITION.value] = 0.8

    # Check for correlation (multiple numeric)
    if len(session_info.numeric_columns) >= 2:
        patterns.append(PatternType.CORRELATION)
        confidence[PatternType.CORRELATION.value] = 0.7

    # Check for distribution
    if session_info.numeric_columns:
        patterns.append(PatternType.DISTRIBUTION)
        confidence[PatternType.DISTRIBUTION.value] = 0.75

    # Check for ranking
    if session_info.categorical_columns and session_info.numeric_columns:
        patterns.append(PatternType.RANKING)
        confidence[PatternType.RANKING.value] = 0.7

    # Use analysis if provided
    if data_analysis:
        # Refine based on actual data
        if data_analysis.datetime_summary:
            confidence[PatternType.TIME_SERIES.value] = 0.95

    return {
        "patterns": [p.value for p in patterns],
        "confidence": confidence,
        "primary_pattern": patterns[0].value if patterns else PatternType.UNKNOWN.value
    }


def _detect_patterns_from_schema(
    session_info: SessionInfo,
    numeric_summary: Dict,
    categorical_summary: Dict,
    datetime_summary: Dict
) -> tuple:
    """Detect patterns from schema and summaries."""
    patterns = []
    confidence = {}

    # Time series detection
    if datetime_summary:
        patterns.append(PatternType.TIME_SERIES)
        confidence[PatternType.TIME_SERIES.value] = 0.9

    # Comparison detection
    if categorical_summary and numeric_summary:
        patterns.append(PatternType.COMPARISON)
        confidence[PatternType.COMPARISON.value] = 0.85

    # Composition detection
    if len(categorical_summary) >= 1 and len(numeric_summary) == 1:
        patterns.append(PatternType.COMPOSITION)
        confidence[PatternType.COMPOSITION.value] = 0.8

    # Correlation detection
    if len(numeric_summary) >= 2:
        patterns.append(PatternType.CORRELATION)
        confidence[PatternType.CORRELATION.value] = 0.7

    # Distribution detection
    if numeric_summary:
        patterns.append(PatternType.DISTRIBUTION)
        confidence[PatternType.DISTRIBUTION.value] = 0.75

    if not patterns:
        patterns.append(PatternType.UNKNOWN)
        confidence[PatternType.UNKNOWN.value] = 0.5

    return patterns, confidence


def _generate_recommendations(
    session_info: SessionInfo,
    patterns: List[PatternType],
    numeric_summary: Dict,
    categorical_summary: Dict
) -> Dict[str, List[str]]:
    """Generate visualization and grouping recommendations."""
    visualizations = []
    groupings = []

    for pattern in patterns:
        if pattern == PatternType.TIME_SERIES:
            visualizations.extend(["line", "area"])
            groupings.extend(session_info.datetime_columns)
        elif pattern == PatternType.COMPARISON:
            visualizations.extend(["bar_vertical", "bar_horizontal"])
            groupings.extend(session_info.categorical_columns)
        elif pattern == PatternType.COMPOSITION:
            visualizations.extend(["pie", "doughnut"])
            groupings.extend(session_info.categorical_columns)
        elif pattern == PatternType.CORRELATION:
            visualizations.extend(["scatter", "bubble"])
        elif pattern == PatternType.DISTRIBUTION:
            visualizations.extend(["bar_vertical"])
        elif pattern == PatternType.RANKING:
            visualizations.extend(["bar_horizontal"])
            groupings.extend(session_info.categorical_columns)

    # Deduplicate while preserving order
    visualizations = list(dict.fromkeys(visualizations))
    groupings = list(dict.fromkeys(groupings))

    return {
        "visualizations": visualizations[:5],
        "groupings": groupings[:3]
    }


def _identify_issues(
    session_info: SessionInfo,
    null_percentage: float,
    duplicate_rows: int
) -> List[str]:
    """Identify potential data quality issues."""
    issues = []

    if null_percentage > 20:
        issues.append(f"High null percentage: {null_percentage:.1f}%")

    if duplicate_rows > session_info.row_count * 0.1:
        issues.append(f"Many duplicate rows: {duplicate_rows}")

    # Check for columns with very low uniqueness (might be useless)
    for col in session_info.columns:
        if col.unique_count == 1 and not col.nullable:
            issues.append(f"Column '{col.name}' has only one unique value")

    # Check for columns with very high uniqueness (might be IDs)
    for col in session_info.columns:
        if col.dtype == "text" and col.unique_count == session_info.row_count:
            issues.append(f"Column '{col.name}' may be an identifier (all unique)")

    return issues
