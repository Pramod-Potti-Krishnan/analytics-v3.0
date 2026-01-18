"""
Session tools for Data Ingestion Agent.

Provides tools for retrieving session information.
"""

import logging
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.session_store import SessionStore
from ..models.tools import SessionInfo, ColumnInfo

logger = logging.getLogger(__name__)


async def get_session_info(
    db_session: AsyncSession,
    session_id: str
) -> Optional[SessionInfo]:
    """
    Retrieve session information and metadata.

    This is the first tool in the reasoning workflow.
    It retrieves all metadata about the uploaded data session.

    Args:
        db_session: Database session
        session_id: Session ID to retrieve

    Returns:
        SessionInfo with full session metadata, or None if not found
    """
    logger.info(f"Tool: get_session_info for session {session_id}")

    store = SessionStore(db_session)
    session = await store.get_session_by_str_id(session_id)

    if not session:
        logger.warning(f"Session not found: {session_id}")
        return None

    # Convert column schema to ColumnInfo objects
    columns = []
    for col_data in session.column_schema:
        columns.append(ColumnInfo(
            name=col_data.get("name", ""),
            dtype=col_data.get("dtype", "text"),
            nullable=col_data.get("nullable", True),
            unique_count=col_data.get("unique_count", 0),
            null_count=col_data.get("null_count", 0),
            sample_values=col_data.get("sample_values", []),
            statistics=col_data.get("statistics")
        ))

    # Extract column categories from statistics
    data_stats = session.data_statistics or {}

    return SessionInfo(
        session_id=str(session.id),
        status=session.status.value,
        filename=session.original_filename,
        row_count=session.row_count,
        column_count=len(columns),
        columns=columns,
        data_statistics=data_stats,
        numeric_columns=data_stats.get("numeric_columns", []),
        categorical_columns=data_stats.get("categorical_columns", []),
        datetime_columns=data_stats.get("datetime_columns", []),
        text_columns=data_stats.get("text_columns", []),
        created_at=session.created_at.isoformat() if session.created_at else "",
        expires_at=session.expires_at.isoformat() if session.expires_at else ""
    )
