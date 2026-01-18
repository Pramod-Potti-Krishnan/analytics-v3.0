"""
Transform tools for Data Ingestion Agent.

Provides tools for data transformation and preview.
"""

import logging
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session_store import SessionStore
from ..database.query_executor import QueryExecutor
from ..models.tools import (
    TransformResult,
    VisualizationIntent,
    SessionInfo
)

logger = logging.getLogger(__name__)


async def transform_data(
    db_session: AsyncSession,
    session_info: SessionInfo,
    intent: VisualizationIntent
) -> TransformResult:
    """
    Transform data based on visualization intent.

    Applies aggregations, groupings, and filters to prepare
    data for chart generation.

    Args:
        db_session: Database session
        session_info: Session information
        intent: Parsed visualization intent

    Returns:
        TransformResult with transformed data
    """
    logger.info(
        f"Tool: transform_data for session {session_info.session_id}, "
        f"intent: {intent.intent_type.value}"
    )

    store = SessionStore(db_session)
    session = await store.get_session_by_str_id(session_info.session_id)

    if not session:
        raise ValueError(f"Session not found: {session_info.session_id}")

    executor = QueryExecutor(db_session)
    warnings = []

    # Determine columns to use
    target_columns = intent.target_columns or session_info.numeric_columns[:1]
    group_by_columns = intent.group_by_columns

    if not target_columns:
        # No target columns, try to find any numeric column
        if session_info.numeric_columns:
            target_columns = session_info.numeric_columns[:1]
            warnings.append(f"Using default numeric column: {target_columns[0]}")
        else:
            raise ValueError("No numeric columns available for visualization")

    # Prepare aggregation
    aggregation = intent.aggregation_function or "sum"

    try:
        if group_by_columns:
            # Perform grouped aggregation
            aggregations = []
            for col in target_columns:
                aggregations.append({
                    "func": aggregation.upper(),
                    "column": col,
                    "alias": f"{aggregation}_{col}"
                })

            rows = await executor.execute_aggregation(
                table_name=session.data_table_name,
                aggregations=aggregations,
                group_by=group_by_columns,
                where_clause=intent.filter_expression
            )

            # Extract labels and values
            labels = []
            values = []
            series_data = {}

            # Initialize series data for multi-column targets
            if len(target_columns) > 1:
                for col in target_columns:
                    series_data[col] = []

            for row in rows:
                # Build label from group by columns
                if len(group_by_columns) == 1:
                    label = str(row.get(group_by_columns[0], ""))
                else:
                    label = " - ".join(
                        str(row.get(col, "")) for col in group_by_columns
                    )
                labels.append(label)

                # Get value(s)
                if len(target_columns) == 1:
                    val = row.get(f"{aggregation}_{target_columns[0]}", 0)
                    values.append(float(val) if val is not None else 0)
                else:
                    for col in target_columns:
                        val = row.get(f"{aggregation}_{col}", 0)
                        series_data[col].append(float(val) if val is not None else 0)
                    # Use first column for primary values
                    val = row.get(f"{aggregation}_{target_columns[0]}", 0)
                    values.append(float(val) if val is not None else 0)

        else:
            # No grouping - get raw data or single aggregation
            if intent.intent_type.value in ("aggregate_data", "show_distribution"):
                # Single aggregation over all data
                aggregations = []
                for col in target_columns:
                    aggregations.append({
                        "func": aggregation.upper(),
                        "column": col,
                        "alias": f"{aggregation}_{col}"
                    })

                rows = await executor.execute_aggregation(
                    table_name=session.data_table_name,
                    aggregations=aggregations,
                    where_clause=intent.filter_expression
                )

                labels = target_columns
                values = []
                for col in target_columns:
                    val = rows[0].get(f"{aggregation}_{col}", 0) if rows else 0
                    values.append(float(val) if val is not None else 0)
                series_data = None

            else:
                # Get raw data limited to reasonable size
                columns_to_fetch = list(set(target_columns + (group_by_columns or [])))

                raw_rows, total = await executor.execute_select(
                    table_name=session.data_table_name,
                    columns=columns_to_fetch,
                    where_clause=intent.filter_expression,
                    limit=100
                )

                if total > 100:
                    warnings.append(
                        f"Data truncated from {total} to 100 rows for visualization"
                    )

                # Build labels and values from raw data
                labels = []
                values = []

                for i, row in enumerate(raw_rows):
                    # Use row index or first column as label
                    if group_by_columns:
                        label = str(row.get(group_by_columns[0], i))
                    else:
                        label = str(i + 1)
                    labels.append(label)

                    val = row.get(target_columns[0], 0)
                    values.append(float(val) if val is not None else 0)

                series_data = None

        # Validate results
        if not labels or not values:
            warnings.append("Transform resulted in empty data, using sample data")
            labels = ["No Data"]
            values = [0]

        return TransformResult(
            success=True,
            rows_before=session_info.row_count,
            rows_after=len(labels),
            labels=labels,
            values=values,
            series_data=series_data if series_data else None,
            aggregation_applied=aggregation,
            group_by_applied=group_by_columns or [],
            filter_applied=intent.filter_expression,
            warnings=warnings
        )

    except Exception as e:
        logger.error(f"Transform failed: {e}")
        return TransformResult(
            success=False,
            rows_before=session_info.row_count,
            rows_after=0,
            labels=[],
            values=[],
            series_data=None,
            warnings=[f"Transform failed: {str(e)}"]
        )


async def preview_transform(
    db_session: AsyncSession,
    session_info: SessionInfo,
    columns: Optional[List[str]] = None,
    aggregation: Optional[str] = None,
    group_by: Optional[List[str]] = None,
    filter_condition: Optional[str] = None,
    filter_params: Optional[Dict[str, Any]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Preview a transformation without modifying data.

    Returns a sample of what the transformed data would look like.

    Args:
        db_session: Database session
        session_info: Session information
        columns: Columns to include
        aggregation: Aggregation function
        group_by: Group by columns
        filter_condition: SQL WHERE condition
        filter_params: Parameters for filter
        limit: Maximum rows

    Returns:
        Dict with preview data
    """
    logger.info(f"Tool: preview_transform for session {session_info.session_id}")

    store = SessionStore(db_session)
    session = await store.get_session_by_str_id(session_info.session_id)

    if not session:
        raise ValueError(f"Session not found: {session_info.session_id}")

    executor = QueryExecutor(db_session)

    try:
        if aggregation and group_by:
            # Aggregated preview
            target_columns = columns or session_info.numeric_columns[:3]
            aggregations = [
                {"func": aggregation.upper(), "column": col, "alias": f"{aggregation}_{col}"}
                for col in target_columns
            ]

            rows = await executor.execute_aggregation(
                table_name=session.data_table_name,
                aggregations=aggregations,
                group_by=group_by,
                where_clause=filter_condition,
                params=filter_params
            )

            return {
                "success": True,
                "type": "aggregated",
                "rows": rows[:limit],
                "row_count": len(rows),
                "columns": group_by + [f"{aggregation}_{col}" for col in target_columns],
                "aggregation": aggregation,
                "group_by": group_by
            }

        else:
            # Raw data preview
            rows, total = await executor.execute_select(
                table_name=session.data_table_name,
                columns=columns,
                where_clause=filter_condition,
                params=filter_params,
                limit=limit
            )

            return {
                "success": True,
                "type": "raw",
                "rows": rows,
                "row_count": len(rows),
                "total_rows": total,
                "columns": columns or [col.name for col in session_info.columns],
                "truncated": total > limit
            }

    except Exception as e:
        logger.error(f"Preview failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "rows": [],
            "row_count": 0
        }
