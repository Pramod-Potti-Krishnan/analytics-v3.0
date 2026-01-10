"""
Core modules for Analytics Microservice v3.6.0

Contains atomic chart generation logic.

v3.6.0 Changes:
- LLM-generated insight-style titles
- Edit button for interactive data editing
- Removed duplicate internal chart titles
"""

from .atomic_chart_generator import AtomicChartGenerator

__all__ = ['AtomicChartGenerator']
