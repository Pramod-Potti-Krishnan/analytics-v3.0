"""
Chart constraint reader for synthetic data generation.

Reads chart type constraints from chart_catalog.py to ensure
generated data meets requirements.
"""

import sys
import os
from typing import Dict, Any, Optional

# Import chart catalog
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from chart_catalog import get_chart_catalog


class ChartConstraints:
    """
    Reads and provides chart type constraints for data generation.

    Constraints include:
    - min_data_points
    - max_data_points
    - optimal_data_points
    - special requirements (e.g., US state names for choropleth)
    """

    def __init__(self):
        """Initialize with chart catalog."""
        self.catalog = get_chart_catalog()
        self._constraints_cache = {}
        self._load_constraints()

    def _load_constraints(self):
        """Load all chart constraints into cache."""
        for chart_type in self.catalog:
            chart_id = chart_type.id
            self._constraints_cache[chart_id] = {
                'id': chart_id,
                'name': chart_type.name,
                'library': chart_type.library,
                'min_data_points': chart_type.min_data_points,
                'max_data_points': chart_type.max_data_points,
                'optimal_data_points': chart_type.optimal_data_points,
                'supported_layouts': chart_type.supported_layouts,
                'use_cases': chart_type.use_cases,
                'special_requirements': self._extract_special_requirements(chart_type)
            }

    def _extract_special_requirements(self, chart_type) -> dict:
        """Extract special requirements from chart type."""
        requirements = {}

        chart_id = chart_type.id

        # D3 Choropleth USA: Requires US state names
        if chart_id == 'd3_choropleth_usa':
            requirements['label_type'] = 'us_state'
            requirements['state_formats'] = ['abbreviation', 'full_name']

        # D3 Sankey: Requires flow notation
        if chart_id == 'd3_sankey':
            requirements['label_format'] = 'source_target_flow'
            requirements['flow_notation'] = ['arrow', 'explicit']

        # Scatter/Bubble: Requires x,y coordinates
        if chart_id in ['scatter', 'bubble']:
            requirements['data_format'] = 'object_based'
            requirements['required_fields'] = ['x', 'y']
            if chart_id == 'bubble':
                requirements['required_fields'].append('r')

        # Multi-series charts
        if chart_id in ['bar_grouped', 'bar_stacked', 'area_stacked']:
            requirements['data_format'] = 'multi_series'
            requirements['min_series'] = 2
            requirements['max_series'] = 5

        # Radar chart: Normalized values
        if chart_id == 'radar':
            requirements['value_range'] = [0, 100]
            requirements['normalized'] = True

        # Hierarchical charts
        if chart_id in ['d3_treemap', 'd3_sunburst']:
            requirements['data_format'] = 'hierarchical'
            requirements['simple_format_accepted'] = True

        # Waterfall: Positive/negative values
        if chart_id == 'waterfall':
            requirements['value_types'] = ['positive', 'negative']
            requirements['has_total'] = True

        # Market share charts: Sum to 100
        if chart_id in ['pie', 'doughnut', 'polar_area']:
            requirements['sum_constraint'] = 100  # for percentages
            requirements['positive_only'] = True

        return requirements

    def get_constraints(self, chart_type: str) -> Dict[str, Any]:
        """
        Get constraints for a chart type.

        Args:
            chart_type: Chart type ID

        Returns:
            Dictionary with constraints

        Example:
            >>> constraints = ChartConstraints()
            >>> c = constraints.get_constraints('d3_choropleth_usa')
            >>> print(c['min_data_points'])  # 1
            >>> print(c['special_requirements']['label_type'])  # 'us_state'
        """
        if chart_type not in self._constraints_cache:
            raise ValueError(f"Unknown chart type: {chart_type}")

        return self._constraints_cache[chart_type]

    def get_optimal_point_count(self, chart_type: str) -> int:
        """Get optimal data point count for a chart type."""
        constraints = self.get_constraints(chart_type)
        optimal_str = str(constraints['optimal_data_points'])

        if '-' in optimal_str:
            # Parse range like "5-10"
            low, high = map(int, optimal_str.split('-'))
            return (low + high) // 2

        # Single value
        return int(optimal_str)

    def is_valid_point_count(self, chart_type: str, num_points: int) -> bool:
        """Check if data point count is valid for chart type."""
        constraints = self.get_constraints(chart_type)
        min_points = constraints['min_data_points']
        max_points = constraints['max_data_points']

        return min_points <= num_points <= max_points

    def get_all_chart_types(self) -> list:
        """Get list of all supported chart type IDs."""
        return list(self._constraints_cache.keys())

    def get_chart_types_by_library(self, library: str) -> list:
        """Get chart types for a specific library (Chart.js or D3.js)."""
        return [
            chart_id
            for chart_id, constraints in self._constraints_cache.items()
            if constraints['library'] == library
        ]
