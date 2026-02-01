"""
Core modules for Analytics Microservice v3.9.0

Contains atomic chart generation and DATA_ARCHITECTURE diagram logic.

v3.9.0 Changes:
- Added DATA_ARCHITECTURE ER diagram generation
- DataArchitectureAtomicService for HTML visualization
- DataArchitecturePlanner for LLM generation and fallback schemas

v3.6.0 Changes:
- LLM-generated insight-style titles
- Edit button for interactive data editing
- Removed duplicate internal chart titles
"""

from .atomic_chart_generator import AtomicChartGenerator
from .data_architecture_atomic_service import DataArchitectureAtomicService
from .data_architecture_planner import DataArchitecturePlanner, DataArchitecturePlanRequest, DataArchitecturePlanResult

__all__ = [
    'AtomicChartGenerator',
    'DataArchitectureAtomicService',
    'DataArchitecturePlanner',
    'DataArchitecturePlanRequest',
    'DataArchitecturePlanResult'
]
