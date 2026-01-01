"""
API Routes for Analytics Microservice v3.0

This module exposes FastAPI routers for the analytics service.
"""

from .atomic_routes import router as atomic_router
from .chart_data_routes import router as chart_data_router

__all__ = ['atomic_router', 'chart_data_router']
