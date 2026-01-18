"""
Session store for Data Ingestion Agent.

Provides CRUD operations for data sessions with proper
error handling and PostgreSQL integration.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, delete, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import DataSession, SessionStatus, AgentReasoningLog, ReasoningStepType

logger = logging.getLogger(__name__)


class SessionStore:
    """
    Manages data session lifecycle in PostgreSQL.

    Provides methods for creating, retrieving, updating, and
    deleting data sessions and their associated data tables.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize session store.

        Args:
            db_session: SQLAlchemy async session
        """
        self._session = db_session

    async def create_session(
        self,
        original_filename: str,
        file_size_bytes: int,
        row_count: int,
        column_schema: List[Dict[str, Any]],
        data_statistics: Optional[Dict[str, Any]] = None,
        presentation_id: Optional[str] = None,
        slide_id: Optional[str] = None,
        ttl_hours: int = 1
    ) -> DataSession:
        """
        Create a new data session.

        Args:
            original_filename: Name of uploaded CSV file
            file_size_bytes: File size in bytes
            row_count: Number of rows in data
            column_schema: Column definitions
            data_statistics: Optional statistics
            presentation_id: Optional presentation context
            slide_id: Optional slide context
            ttl_hours: Session TTL in hours

        Returns:
            Created DataSession object
        """
        session_id = uuid.uuid4()
        data_table_name = f"data_{session_id.hex}"
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        data_session = DataSession(
            id=session_id,
            presentation_id=presentation_id,
            slide_id=slide_id,
            original_filename=original_filename,
            file_size_bytes=file_size_bytes,
            row_count=row_count,
            column_schema=column_schema,
            data_statistics=data_statistics,
            data_table_name=data_table_name,
            status=SessionStatus.CREATED,
            expires_at=expires_at
        )

        self._session.add(data_session)
        await self._session.flush()

        logger.info(f"Created data session: {session_id}")
        return data_session

    async def get_session(self, session_id: uuid.UUID) -> Optional[DataSession]:
        """
        Get a data session by ID.

        Args:
            session_id: Session UUID

        Returns:
            DataSession or None if not found
        """
        stmt = select(DataSession).where(DataSession.id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_by_str_id(self, session_id: str) -> Optional[DataSession]:
        """
        Get a data session by string ID.

        Args:
            session_id: Session ID as string

        Returns:
            DataSession or None if not found/invalid
        """
        try:
            uid = uuid.UUID(session_id)
            return await self.get_session(uid)
        except ValueError:
            logger.warning(f"Invalid session ID format: {session_id}")
            return None

    async def update_session_status(
        self,
        session_id: uuid.UUID,
        status: SessionStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update session status.

        Args:
            session_id: Session UUID
            status: New status
            error_message: Optional error message

        Returns:
            True if updated, False if not found
        """
        stmt = (
            update(DataSession)
            .where(DataSession.id == session_id)
            .values(
                status=status,
                error_message=error_message,
                updated_at=datetime.utcnow()
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def update_session_statistics(
        self,
        session_id: uuid.UUID,
        data_statistics: Dict[str, Any]
    ) -> bool:
        """
        Update session data statistics.

        Args:
            session_id: Session UUID
            data_statistics: Statistics dictionary

        Returns:
            True if updated, False if not found
        """
        stmt = (
            update(DataSession)
            .where(DataSession.id == session_id)
            .values(
                data_statistics=data_statistics,
                updated_at=datetime.utcnow()
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def delete_session(self, session_id: uuid.UUID) -> bool:
        """
        Delete a session and its data table.

        Args:
            session_id: Session UUID

        Returns:
            True if deleted, False if not found
        """
        # Get session to find table name
        session = await self.get_session(session_id)
        if not session:
            return False

        # Drop the data table
        table_name = session.data_table_name
        try:
            await self._session.execute(
                text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
            )
            logger.info(f"Dropped data table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to drop table {table_name}: {e}")
            # Continue with session deletion

        # Delete session (cascades to logs)
        stmt = delete(DataSession).where(DataSession.id == session_id)
        result = await self._session.execute(stmt)

        logger.info(f"Deleted session: {session_id}")
        return result.rowcount > 0

    async def list_sessions(
        self,
        presentation_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DataSession]:
        """
        List data sessions with optional filters.

        Args:
            presentation_id: Filter by presentation
            status: Filter by status
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of DataSession objects
        """
        stmt = select(DataSession)

        if presentation_id:
            stmt = stmt.where(DataSession.presentation_id == presentation_id)
        if status:
            stmt = stmt.where(DataSession.status == status)

        stmt = stmt.order_by(DataSession.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions.

        Returns:
            Number of sessions deleted
        """
        now = datetime.utcnow()

        # Get expired sessions to drop their tables
        stmt = select(DataSession).where(DataSession.expires_at < now)
        result = await self._session.execute(stmt)
        expired_sessions = list(result.scalars().all())

        deleted_count = 0
        for session in expired_sessions:
            try:
                await self._session.execute(
                    text(f'DROP TABLE IF EXISTS "{session.data_table_name}" CASCADE')
                )
                logger.info(f"Dropped expired data table: {session.data_table_name}")
            except Exception as e:
                logger.error(f"Failed to drop expired table: {e}")

        # Delete sessions
        stmt = delete(DataSession).where(DataSession.expires_at < now)
        result = await self._session.execute(stmt)
        deleted_count = result.rowcount

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired sessions")

        return deleted_count

    async def add_reasoning_log(
        self,
        session_id: uuid.UUID,
        request_id: str,
        step_number: int,
        step_type: ReasoningStepType,
        tool_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        reasoning: Optional[str] = None,
        duration_ms: float = 0,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AgentReasoningLog:
        """
        Add a reasoning step log entry.

        Args:
            session_id: Session UUID
            request_id: Request identifier
            step_number: Step sequence number
            step_type: Type of reasoning step
            tool_name: Name of tool invoked
            input_data: Tool input
            output_data: Tool output
            reasoning: Explanation of reasoning
            duration_ms: Execution time
            success: Whether step succeeded
            error_message: Error if failed

        Returns:
            Created log entry
        """
        log_entry = AgentReasoningLog(
            session_id=session_id,
            request_id=request_id,
            step_number=step_number,
            step_type=step_type,
            tool_name=tool_name,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )

        self._session.add(log_entry)
        await self._session.flush()

        return log_entry

    async def get_reasoning_logs(
        self,
        session_id: uuid.UUID,
        request_id: Optional[str] = None
    ) -> List[AgentReasoningLog]:
        """
        Get reasoning logs for a session.

        Args:
            session_id: Session UUID
            request_id: Optional filter by request

        Returns:
            List of reasoning log entries
        """
        stmt = (
            select(AgentReasoningLog)
            .where(AgentReasoningLog.session_id == session_id)
        )

        if request_id:
            stmt = stmt.where(AgentReasoningLog.request_id == request_id)

        stmt = stmt.order_by(AgentReasoningLog.step_number)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())
