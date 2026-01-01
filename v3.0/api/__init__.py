"""
API Routes for Analytics Microservice v3.0

This module exposes FastAPI routers for the analytics service.
"""

from .atomic_routes import router as atomic_router

__all__ = ['atomic_router']
