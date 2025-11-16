"""
Chart Data Model

Database model for storing chart data edits from interactive editor.
"""

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime


try:
    from extensions import db
except ImportError:
    # Fallback if extensions not available
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()


class ChartData(db.Model):
    """
    Chart data edits table.

    Stores user edits to chart data for persistence across sessions.
    """
    __tablename__ = 'chart_data_edits'

    id = Column(Integer, primary_key=True)
    chart_id = Column(String(255), nullable=False, index=True)
    presentation_id = Column(String(255), nullable=False, index=True)
    labels = Column(JSONB, nullable=False)  # Array of X-axis labels
    values = Column(JSONB, nullable=False)  # Array of Y-axis values
    chart_type = Column(String(50))  # 'line', 'bar', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))  # User ID who made the edit

    __table_args__ = (
        db.UniqueConstraint(
            'chart_id',
            'presentation_id',
            name='unique_chart_per_presentation'
        ),
        db.Index('idx_chart_edits_presentation', 'presentation_id'),
        db.Index('idx_chart_edits_chart', 'chart_id'),
    )

    def __repr__(self):
        return f"<ChartData {self.chart_id} in {self.presentation_id}>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'chart_id': self.chart_id,
            'presentation_id': self.presentation_id,
            'labels': self.labels,
            'values': self.values,
            'chart_type': self.chart_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

    @classmethod
    def create(cls, chart_id, presentation_id, labels, values, chart_type=None, updated_by=None):
        """
        Create new chart data record.

        Args:
            chart_id: Unique chart identifier
            presentation_id: Presentation UUID
            labels: List of X-axis labels
            values: List of Y-axis values
            chart_type: Type of chart (optional)
            updated_by: User ID (optional)

        Returns:
            ChartData instance
        """
        return cls(
            chart_id=chart_id,
            presentation_id=presentation_id,
            labels=labels,
            values=values,
            chart_type=chart_type,
            updated_by=updated_by
        )

    @classmethod
    def update_or_create(cls, chart_id, presentation_id, labels, values, chart_type=None, updated_by=None):
        """
        Update existing record or create new one.

        Args:
            chart_id: Unique chart identifier
            presentation_id: Presentation UUID
            labels: List of X-axis labels
            values: List of Y-axis values
            chart_type: Type of chart (optional)
            updated_by: User ID (optional)

        Returns:
            Tuple of (ChartData instance, was_created boolean)
        """
        existing = cls.query.filter_by(
            chart_id=chart_id,
            presentation_id=presentation_id
        ).first()

        if existing:
            existing.labels = labels
            existing.values = values
            existing.updated_at = datetime.utcnow()
            if chart_type:
                existing.chart_type = chart_type
            if updated_by:
                existing.updated_by = updated_by
            return existing, False
        else:
            new_record = cls.create(
                chart_id=chart_id,
                presentation_id=presentation_id,
                labels=labels,
                values=values,
                chart_type=chart_type,
                updated_by=updated_by
            )
            db.session.add(new_record)
            return new_record, True
