"""
Models for Analytics Microservice v3.9.0

This module exposes Pydantic models for request/response handling.

v3.9.0: Added DATA_ARCHITECTURE models for ER diagram generation
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

# v3.9.0: DATA_ARCHITECTURE models
from .data_architecture_atomic_models import (
    DataArchitectureAtomicRequest,
    DataArchitectureAtomicResponse,
    DataArchitectureAtomicError,
    DataEntity,
    DataField,
    DataRelationship,
    DATA_ARCH_POSITION_PRESETS,
    EntityType,
    CardinalityType
)

# Note: ChartData (SQLAlchemy model) not imported - requires SQLAlchemy dependency
# which is not currently needed for atomic chart endpoints

__all__ = [
    # Chart models
    'AtomicChartRequest',
    'AtomicChartResponse',
    'AtomicChartError',
    'AtomicChartCatalogResponse',
    'ChartTypeCatalogItem',
    'ChartDimensions',
    'ChartTypeId',
    'GOLD_STANDARD_CHARTS',
    # DATA_ARCHITECTURE models
    'DataArchitectureAtomicRequest',
    'DataArchitectureAtomicResponse',
    'DataArchitectureAtomicError',
    'DataEntity',
    'DataField',
    'DataRelationship',
    'DATA_ARCH_POSITION_PRESETS',
    'EntityType',
    'CardinalityType'
]
