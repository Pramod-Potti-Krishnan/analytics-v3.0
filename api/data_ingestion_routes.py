"""
API routes for Data Ingestion Agent.

Provides REST endpoints for CSV upload, data ingestion,
and session management under /api/v1/data/ prefix.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
    Form,
    Depends,
    BackgroundTasks
)
from fastapi.responses import JSONResponse

from data_ingestion.settings import get_data_ingestion_settings, validate_settings
from data_ingestion.database.connection import get_db_connection, close_db_connection
from data_ingestion.database.session_store import SessionStore
from data_ingestion.database.query_executor import QueryExecutor
from data_ingestion.database.models import SessionStatus, Base
from data_ingestion.upload.handler import CSVHandler
from data_ingestion.agent.reasoning_engine import ReasoningEngine
from data_ingestion.models.requests import (
    IngestRequest,
    PreviewRequest,
    SessionListRequest
)
from data_ingestion.models.responses import (
    UploadResponse,
    IngestResponse,
    SessionResponse,
    SessionListResponse,
    ReasoningResponse,
    HealthResponse,
    ErrorResponse,
    ColumnSchemaResponse,
    ChartOutput,
    ReasoningStep,
    ReasoningLogEntry
)

logger = logging.getLogger(__name__)

# Create router with /api/v1/data prefix
router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Ingestion"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


# Error codes specific to data ingestion
class DataIngestionErrorCode:
    """Error codes for data ingestion module."""
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
    INVALID_CSV_FORMAT = "INVALID_CSV_FORMAT"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    AMBIGUOUS_INTENT = "AMBIGUOUS_INTENT"
    TRANSFORM_FAILED = "TRANSFORM_FAILED"
    AGENT_MAX_STEPS_EXCEEDED = "AGENT_MAX_STEPS_EXCEEDED"
    DATABASE_NOT_CONFIGURED = "DATABASE_NOT_CONFIGURED"


def _error_response(code: str, message: str, details: dict = None, status_code: int = 400) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }
    )


# Background task for session cleanup
async def cleanup_expired_sessions_task():
    """Background task to clean up expired sessions."""
    import asyncio

    settings = get_data_ingestion_settings()
    interval_seconds = settings.SESSION_CLEANUP_INTERVAL_MINUTES * 60

    while True:
        try:
            await asyncio.sleep(interval_seconds)

            db = await get_db_connection()
            async with db.session() as session:
                store = SessionStore(session)
                deleted = await store.cleanup_expired_sessions()
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} expired sessions")

        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")


@router.get("/health", response_model=HealthResponse)
async def data_ingestion_health():
    """
    Health check for Data Ingestion module.

    Returns database connection status and configuration.
    """
    settings_validation = validate_settings()

    try:
        db = await get_db_connection()
        db_health = await db.health_check()
    except Exception as e:
        db_health = {"status": "error", "error": str(e)}

    status = "healthy" if (
        settings_validation["valid"] and
        db_health.get("status") == "healthy"
    ) else "unhealthy"

    return HealthResponse(
        status=status,
        database=db_health,
        settings=settings_validation["settings"],
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    presentation_id: Optional[str] = Form(None),
    slide_id: Optional[str] = Form(None)
):
    """
    Upload a CSV file and create a data session.

    The uploaded file is parsed, validated, and stored in PostgreSQL.
    Returns session ID for subsequent operations.

    Args:
        file: CSV file to upload
        presentation_id: Optional presentation context
        slide_id: Optional slide context

    Returns:
        UploadResponse with session_id and column schemas
    """
    settings = get_data_ingestion_settings()

    # Check database configuration
    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured. Set DATA_INGESTION_DATABASE_URL.",
            status_code=503
        )

    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        return _error_response(
            DataIngestionErrorCode.INVALID_CSV_FORMAT,
            f"Failed to read file: {str(e)}"
        )

    # Initialize handler
    handler = CSVHandler(
        max_file_size_bytes=settings.max_file_size_bytes,
        max_rows=settings.MAX_ROWS_PER_SESSION,
        max_columns=settings.MAX_COLUMNS_PER_SESSION
    )

    # Process upload
    result = handler.process_upload(
        file_content=content,
        filename=file.filename or "upload.csv",
        content_type=file.content_type,
        presentation_id=presentation_id,
        slide_id=slide_id
    )

    if not result.success:
        return _error_response(
            DataIngestionErrorCode.INVALID_CSV_FORMAT,
            result.errors[0] if result.errors else "Upload validation failed",
            {"errors": result.errors, "warnings": result.warnings}
        )

    # Store in database
    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)
            executor = QueryExecutor(db_session)

            # Create session record
            data_session = await store.create_session(
                original_filename=result.filename,
                file_size_bytes=result.file_size_bytes,
                row_count=result.row_count,
                column_schema=[c.to_dict() for c in result.columns],
                data_statistics=result.data_statistics,
                presentation_id=presentation_id,
                slide_id=slide_id,
                ttl_hours=settings.SESSION_TTL_HOURS
            )

            # Create data table
            await executor.create_data_table(
                table_name=data_session.data_table_name,
                columns=[c.to_dict() for c in result.columns]
            )

            # Insert data
            if result.dataframe is not None:
                column_names, rows = handler.prepare_for_database(
                    result.dataframe,
                    result.columns
                )
                await executor.insert_data(
                    table_name=data_session.data_table_name,
                    columns=column_names,
                    rows=rows
                )

            # Update status to ready
            await store.update_session_status(
                data_session.id,
                SessionStatus.READY
            )

            # Build response
            return UploadResponse(
                success=True,
                session_id=str(data_session.id),
                filename=result.filename,
                row_count=result.row_count,
                column_count=result.column_count,
                columns=[
                    ColumnSchemaResponse(
                        name=c.name,
                        dtype=c.dtype,
                        nullable=c.nullable,
                        unique_count=c.unique_count,
                        null_count=c.null_count,
                        sample_values=c.sample_values,
                        statistics=c.statistics
                    )
                    for c in result.columns
                ],
                data_statistics=result.data_statistics,
                warnings=result.warnings,
                expires_at=data_session.expires_at.isoformat() + "Z"
            )

    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return _error_response(
            "UPLOAD_FAILED",
            f"Failed to store data: {str(e)}",
            status_code=500
        )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_data(request: IngestRequest):
    """
    Process data and generate visualization.

    Uses chain-of-thought reasoning to:
    1. Analyze session data
    2. Parse user intent from narrative
    3. Transform data as needed
    4. Generate appropriate chart

    Args:
        request: Ingest request with session_id and narrative

    Returns:
        IngestResponse with chart HTML and reasoning steps
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            # Run reasoning engine
            engine = ReasoningEngine(db_session)
            result = await engine.process(
                session_id=request.session_id,
                narrative=request.narrative,
                chart_type=request.chart_type,
                chart_title=request.chart_title,
                presentation_id=request.presentation_id,
                slide_id=request.slide_id,
                include_insights=request.include_insights,
                width=request.width,
                height=request.height
            )

            if not result["success"]:
                return _error_response(
                    "INGEST_FAILED",
                    result.get("error", "Processing failed"),
                    {"reasoning_steps": [s.model_dump() for s in result.get("reasoning_steps", [])]}
                )

            return IngestResponse(
                success=True,
                request_id=result["request_id"],
                session_id=result["session_id"],
                chart=result["chart"],
                data_summary=result["data_summary"],
                reasoning_steps=result["reasoning_steps"],
                total_duration_ms=result["total_duration_ms"]
            )

    except Exception as e:
        logger.error(f"Ingest failed: {e}", exc_info=True)
        return _error_response(
            "INGEST_FAILED",
            f"Processing failed: {str(e)}",
            status_code=500
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get session metadata and column information.

    Args:
        session_id: Session UUID

    Returns:
        SessionResponse with full session details
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)
            session = await store.get_session_by_str_id(session_id)

            if not session:
                return _error_response(
                    DataIngestionErrorCode.SESSION_NOT_FOUND,
                    f"Session not found: {session_id}",
                    status_code=404
                )

            # Check if expired
            if session.expires_at < datetime.utcnow():
                return _error_response(
                    DataIngestionErrorCode.SESSION_EXPIRED,
                    f"Session expired at {session.expires_at.isoformat()}",
                    status_code=410
                )

            return SessionResponse(
                session_id=str(session.id),
                status=session.status.value,
                filename=session.original_filename,
                row_count=session.row_count,
                column_count=len(session.column_schema),
                columns=[
                    ColumnSchemaResponse(
                        name=c["name"],
                        dtype=c["dtype"],
                        nullable=c.get("nullable", True),
                        unique_count=c.get("unique_count", 0),
                        null_count=c.get("null_count", 0),
                        sample_values=c.get("sample_values", []),
                        statistics=c.get("statistics")
                    )
                    for c in session.column_schema
                ],
                data_statistics=session.data_statistics,
                presentation_id=session.presentation_id,
                slide_id=session.slide_id,
                created_at=session.created_at.isoformat() + "Z",
                expires_at=session.expires_at.isoformat() + "Z",
                error_message=session.error_message
            )

    except Exception as e:
        logger.error(f"Get session failed: {e}", exc_info=True)
        return _error_response(
            "SESSION_ERROR",
            f"Failed to get session: {str(e)}",
            status_code=500
        )


@router.post("/sessions/{session_id}/preview")
async def preview_transform(session_id: str, request: PreviewRequest):
    """
    Preview a data transformation without committing.

    Args:
        session_id: Session UUID
        request: Preview request parameters

    Returns:
        Preview of transformed data
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)
            session = await store.get_session_by_str_id(session_id)

            if not session:
                return _error_response(
                    DataIngestionErrorCode.SESSION_NOT_FOUND,
                    f"Session not found: {session_id}",
                    status_code=404
                )

            from data_ingestion.tools import preview_transform as preview_tool
            from data_ingestion.tools import get_session_info

            session_info = await get_session_info(db_session, session_id)

            result = await preview_tool(
                db_session=db_session,
                session_info=session_info,
                columns=request.columns,
                aggregation=request.aggregation,
                group_by=request.group_by,
                filter_condition=request.filter_condition,
                filter_params=request.filter_params,
                limit=request.limit
            )

            return result

    except Exception as e:
        logger.error(f"Preview failed: {e}", exc_info=True)
        return _error_response(
            "PREVIEW_FAILED",
            f"Preview failed: {str(e)}",
            status_code=500
        )


@router.get("/sessions/{session_id}/reasoning", response_model=ReasoningResponse)
async def get_reasoning_logs(
    session_id: str,
    request_id: Optional[str] = None
):
    """
    Get full chain-of-thought reasoning audit trail.

    Args:
        session_id: Session UUID
        request_id: Optional filter by specific request

    Returns:
        ReasoningResponse with all reasoning steps
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)
            session = await store.get_session_by_str_id(session_id)

            if not session:
                return _error_response(
                    DataIngestionErrorCode.SESSION_NOT_FOUND,
                    f"Session not found: {session_id}",
                    status_code=404
                )

            logs = await store.get_reasoning_logs(
                session_id=session.id,
                request_id=request_id
            )

            log_entries = [
                ReasoningLogEntry(
                    id=str(log.id),
                    step_number=log.step_number,
                    step_type=log.step_type.value,
                    tool_name=log.tool_name,
                    input_summary=log._summarize_data(log.input_data),
                    output_summary=log._summarize_data(log.output_data),
                    reasoning=log.reasoning,
                    duration_ms=log.duration_ms,
                    success=log.success,
                    error_message=log.error_message,
                    created_at=log.created_at.isoformat() + "Z"
                )
                for log in logs
            ]

            total_duration = sum(log.duration_ms for log in logs)
            final_status = "success" if all(log.success for log in logs) else "partial_failure"

            return ReasoningResponse(
                success=True,
                session_id=session_id,
                request_id=request_id,
                logs=log_entries,
                total_steps=len(log_entries),
                total_duration_ms=total_duration,
                final_status=final_status
            )

    except Exception as e:
        logger.error(f"Get reasoning logs failed: {e}", exc_info=True)
        return _error_response(
            "REASONING_ERROR",
            f"Failed to get reasoning logs: {str(e)}",
            status_code=500
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and its data.

    Args:
        session_id: Session UUID

    Returns:
        Success confirmation
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)
            deleted = await store.delete_session(uuid.UUID(session_id))

            if not deleted:
                return _error_response(
                    DataIngestionErrorCode.SESSION_NOT_FOUND,
                    f"Session not found: {session_id}",
                    status_code=404
                )

            return {"success": True, "message": f"Session {session_id} deleted"}

    except ValueError:
        return _error_response(
            "INVALID_SESSION_ID",
            f"Invalid session ID format: {session_id}"
        )
    except Exception as e:
        logger.error(f"Delete session failed: {e}", exc_info=True)
        return _error_response(
            "DELETE_FAILED",
            f"Failed to delete session: {str(e)}",
            status_code=500
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    presentation_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    List data sessions.

    Args:
        presentation_id: Filter by presentation
        status: Filter by status
        limit: Maximum sessions to return
        offset: Pagination offset

    Returns:
        SessionListResponse with session list
    """
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        return _error_response(
            DataIngestionErrorCode.DATABASE_NOT_CONFIGURED,
            "PostgreSQL database not configured",
            status_code=503
        )

    try:
        db = await get_db_connection()
        async with db.session() as db_session:
            store = SessionStore(db_session)

            # Parse status if provided
            session_status = None
            if status:
                try:
                    session_status = SessionStatus(status)
                except ValueError:
                    return _error_response(
                        "INVALID_STATUS",
                        f"Invalid status: {status}. Valid: {[s.value for s in SessionStatus]}"
                    )

            sessions = await store.list_sessions(
                presentation_id=presentation_id,
                status=session_status,
                limit=min(limit, 200),
                offset=offset
            )

            session_responses = [
                SessionResponse(
                    session_id=str(s.id),
                    status=s.status.value,
                    filename=s.original_filename,
                    row_count=s.row_count,
                    column_count=len(s.column_schema),
                    columns=[
                        ColumnSchemaResponse(
                            name=c["name"],
                            dtype=c["dtype"],
                            nullable=c.get("nullable", True),
                            unique_count=c.get("unique_count", 0),
                            null_count=c.get("null_count", 0),
                            sample_values=c.get("sample_values", []),
                            statistics=c.get("statistics")
                        )
                        for c in s.column_schema
                    ],
                    data_statistics=s.data_statistics,
                    presentation_id=s.presentation_id,
                    slide_id=s.slide_id,
                    created_at=s.created_at.isoformat() + "Z",
                    expires_at=s.expires_at.isoformat() + "Z",
                    error_message=s.error_message
                )
                for s in sessions
            ]

            return SessionListResponse(
                success=True,
                sessions=session_responses,
                total_count=len(sessions),
                limit=limit,
                offset=offset
            )

    except Exception as e:
        logger.error(f"List sessions failed: {e}", exc_info=True)
        return _error_response(
            "LIST_FAILED",
            f"Failed to list sessions: {str(e)}",
            status_code=500
        )


# Startup event to initialize database
async def init_data_ingestion_db():
    """Initialize database on startup."""
    settings = get_data_ingestion_settings()

    if not settings.DATABASE_URL:
        logger.warning(
            "Data Ingestion: DATABASE_URL not configured. "
            "Set DATA_INGESTION_DATABASE_URL to enable data ingestion features."
        )
        return

    try:
        from sqlalchemy import text

        db = await get_db_connection()

        # Create tables if they don't exist
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Data Ingestion: Database initialized successfully")

    except Exception as e:
        logger.error(f"Data Ingestion: Database initialization failed: {e}")


# Shutdown event
async def shutdown_data_ingestion_db():
    """Close database connections on shutdown."""
    await close_db_connection()
    logger.info("Data Ingestion: Database connections closed")
