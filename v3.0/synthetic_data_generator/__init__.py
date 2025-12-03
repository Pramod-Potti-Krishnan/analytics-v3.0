"""
Synthetic Data Generator for Analytics Microservice v3.

Generates realistic, context-aware data for all 18 chart types.
Supports independent operation without Director Agent dependency.

Version: 1.0.0
"""

from .generator import SyntheticDataGenerator
from .scenarios import BusinessScenario, SCENARIO_LIBRARY, get_scenario, list_scenarios
from .constraints import ChartConstraints

__all__ = [
    'SyntheticDataGenerator',
    'BusinessScenario',
    'SCENARIO_LIBRARY',
    'get_scenario',
    'list_scenarios',
    'ChartConstraints'
]

__version__ = '1.0.0'
