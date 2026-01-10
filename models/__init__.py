"""
Models for Analytics Microservice v3.6.0

This module exposes Pydantic models for request/response handling.

v3.6.0: Added enable_editor parameter to AtomicChartRequest
"""

from .atomic_models import (
    AtomicChartRequest,
    AtomicChartResponse,
    AtomicChartError,
    AtomicChartCatalogResponse,
    ChartTypeCatalogItem,
    ChartDimensions,
    ChartTypeId,
    GOLD_STANDARD_CHARTS
)

# Note: ChartData (SQLAlchemy model) not imported - requires SQLAlchemy dependency
# which is not currently needed for atomic chart endpoints

__all__ = [
    'AtomicChartRequest',
    'AtomicChartResponse',
    'AtomicChartError',
    'AtomicChartCatalogResponse',
    'ChartTypeCatalogItem',
    'ChartDimensions',
    'ChartTypeId',
    'GOLD_STANDARD_CHARTS'
]
