"""
Analytics Microservice v3.1 - Theme-Enabled Analytics Agent

A Pydantic AI-powered analytics microservice that generates comprehensive
charts and visualizations through a WebSocket API with real-time progress streaming.

v3.1 adds theme service integration with:
- 7 themes: professional, corporate, vibrant, executive, educational, children_young, children_older
- Theme-based color palettes for all chart types
- Theme-based layout styling
"""

__version__ = "3.1.0"

from agent import process_analytics_request
from dependencies import AnalyticsDependencies
from settings import settings

__all__ = [
    "process_analytics_request",
    "AnalyticsDependencies",
    "settings",
]