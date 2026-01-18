"""
SQLAlchemy ORM models for Data Ingestion Agent.

Defines the PostgreSQL schema for:
- data_sessions: Session metadata and column schema
- agent_reasoning_log: Chain-of-thought steps
- transform_audit: SQL transformation history
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class SessionStatus(str, enum.Enum):
    """Status of a data ingestion session."""
    CREATED = "created"
    PROCESSING = "processing"
    READY = "ready"
    EXPIRED = "expired"
    ERROR = "error"


class ReasoningStepType(str, enum.Enum):
    """Types of reasoning steps in the agent workflow."""
    GET_SESSION = "get_session"
    ANALYZE_DATA = "analyze_data"
    PARSE_INTENT = "parse_intent"
    DETECT_PATTERNS = "detect_patterns"
    TRANSFORM_DATA = "transform_data"
    GENERATE_CHART = "generate_chart"
    VALIDATE_RESULT = "validate_result"
    SUGGEST_ALTERNATIVES = "suggest_alternatives"
    ERROR = "error"


class DataSession(Base):
    """
    Data ingestion session with uploaded CSV metadata.

    Stores session information, column schema (JSONB), and
    references the dynamically created data table.
    """
    __tablename__ = "data_sessions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Presentation context (for slide integration)
    presentation_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    slide_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # File metadata
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Column schema stored as JSONB
    # Format: [{"name": "col1", "dtype": "float64", "nullable": true, "sample_values": [...]}]
    column_schema: Mapped[Dict] = mapped_column(JSONB, nullable=False, default=list)

    # Data statistics (JSONB)
    # Format: {"numeric_columns": [...], "categorical_columns": [...], "date_columns": [...]}
    data_statistics: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # Dynamic table name: data_{session_id}
    data_table_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Session status
    status: Mapped[SessionStatus] = mapped_column(
        SQLEnum(SessionStatus),
        default=SessionStatus.CREATED,
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    # Relationships
    reasoning_logs: Mapped[List["AgentReasoningLog"]] = relationship(
        "AgentReasoningLog",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    transform_audits: Mapped[List["TransformAudit"]] = relationship(
        "TransformAudit",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_data_sessions_presentation_id", "presentation_id"),
        Index("ix_data_sessions_status", "status"),
        Index("ix_data_sessions_expires_at", "expires_at"),
        Index("ix_data_sessions_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "session_id": str(self.id),
            "presentation_id": self.presentation_id,
            "slide_id": self.slide_id,
            "original_filename": self.original_filename,
            "file_size_bytes": self.file_size_bytes,
            "row_count": self.row_count,
            "column_count": len(self.column_schema) if self.column_schema else 0,
            "columns": self.column_schema,
            "data_statistics": self.data_statistics,
            "status": self.status.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class AgentReasoningLog(Base):
    """
    Chain-of-thought reasoning log for agent workflow.

    Records each step of the reasoning process with inputs,
    outputs, duration, and tool-specific details.
    """
    __tablename__ = "agent_reasoning_log"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sessions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Request identifier (groups steps from same /ingest call)
    request_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Step information
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[ReasoningStepType] = mapped_column(
        SQLEnum(ReasoningStepType),
        nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Input/output data (JSONB for flexibility)
    input_data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # Reasoning explanation
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Execution metadata
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship
    session: Mapped["DataSession"] = relationship(
        "DataSession",
        back_populates="reasoning_logs"
    )

    # Indexes
    __table_args__ = (
        Index("ix_reasoning_log_session_id", "session_id"),
        Index("ix_reasoning_log_request_id", "request_id"),
        Index("ix_reasoning_log_step_number", "session_id", "request_id", "step_number"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "step_number": self.step_number,
            "step_type": self.step_type.value,
            "tool_name": self.tool_name,
            "input_summary": self._summarize_data(self.input_data),
            "output_summary": self._summarize_data(self.output_data),
            "reasoning": self.reasoning,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def _summarize_data(data: Optional[Dict], max_length: int = 200) -> Optional[str]:
        """Summarize JSONB data for display."""
        if not data:
            return None
        import json
        summary = json.dumps(data)
        if len(summary) > max_length:
            return summary[:max_length] + "..."
        return summary


class TransformAudit(Base):
    """
    SQL transformation audit log.

    Records all SQL transformations applied to session data
    for debugging and rollback capabilities.
    """
    __tablename__ = "transform_audit"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Foreign key to session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sessions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Request identifier
    request_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # SQL details
    sql_query: Mapped[str] = mapped_column(Text, nullable=False)
    query_params: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # Result metadata
    rows_affected: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result_preview: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True)

    # Execution status
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship
    session: Mapped["DataSession"] = relationship(
        "DataSession",
        back_populates="transform_audits"
    )

    # Indexes
    __table_args__ = (
        Index("ix_transform_audit_session_id", "session_id"),
        Index("ix_transform_audit_request_id", "request_id"),
        Index("ix_transform_audit_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "sql_query": self.sql_query[:500] + "..." if len(self.sql_query) > 500 else self.sql_query,
            "rows_affected": self.rows_affected,
            "success": self.success,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
