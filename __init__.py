"""
Analytics Microservice v3 - WebSocket-based Analytics Agent

A Pydantic AI-powered analytics microservice that generates comprehensive 
charts and visualizations through a WebSocket API with real-time progress streaming.
"""

__version__ = "3.3.5"

from agent import process_analytics_request
from dependencies import AnalyticsDependencies
from settings import settings

__all__ = [
    "process_analytics_request",
    "AnalyticsDependencies",
    "settings",
]