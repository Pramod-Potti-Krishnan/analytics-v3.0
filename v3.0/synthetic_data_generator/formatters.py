"""
Data format converters for different chart types.

Converts simple {label, value} format to chart-specific formats
(scatter objects, multi-series, hierarchical, etc.)
"""

from typing import List, Dict, Any
import random


class DataFormatter:
    """
    Converts generated data to chart-specific formats.

    Handles:
    - Simple format: [{label, value}, ...]
    - Object format: [{x, y, label}, ...] (scatter/bubble)
    - Multi-series format: {datasets: [{label, data}, ...]}
    - Hierarchical format: (treemap/sunburst)
    - Flow format: Source→Target notation (sankey)
    """

    def format(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Format data for specific chart type.

        Args:
            data: Base data in simple {label, value} format
            chart_type: Target chart type ID

        Returns:
            Formatted data ready for chart rendering
        """
        formatter_map = {
            'scatter': self._format_scatter,
            'bubble': self._format_bubble,
            'bar_grouped': self._format_multi_series,
            'bar_stacked': self._format_multi_series,
            'area_stacked': self._format_multi_series,
            'radar': self._format_radar,
            'd3_sankey': self._format_sankey,
            # All others use simple format
        }

        formatter = formatter_map.get(chart_type, self._format_simple)
        return formatter(data, chart_type)

    def _format_simple(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """Simple format: unchanged {label, value} pairs."""
        return data

    def _format_scatter(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Convert to scatter format: {x, y, label}.

        If data already has x,y keys (from generator), preserve them.
        Otherwise convert from simple {label, value} format.

        Input: [{"label": "A", "value": 100}, ...]  OR  [{"label": "A", "x": 10, "y": 20}, ...]
        Output: [{"x": 0, "y": 100, "label": "A"}, ...]  OR  [{"x": 10, "y": 20, "label": "A"}, ...]
        """
        return [
            {
                "x": item.get('x', i),                        # Preserve generator's x or use index
                "y": item.get('y', item.get('value', 0)),     # Preserve generator's y or use value or 0
                "label": item.get('label', f"Point {i+1}")
            }
            for i, item in enumerate(data)
        ]

    def _format_bubble(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Convert to bubble format: {x, y, r, label}.

        If data already has x,y,r keys (from generator), preserve them.
        Otherwise convert from simple {label, value} format.

        Input: [{"label": "A", "value": 100}, ...]  OR  [{"label": "A", "x": 10, "y": 20, "r": 15}, ...]
        Output: [{"x": 0, "y": 100, "r": 15, "label": "A"}, ...]  OR  [{"x": 10, "y": 20, "r": 15, "label": "A"}, ...]
        """
        return [
            {
                "x": item.get('x', i),                        # Preserve generator's x or use index
                "y": item.get('y', item.get('value', 0)),     # Preserve generator's y or use value or 0
                "r": item.get('r', random.randint(10, 30)),   # Preserve generator's r or generate
                "label": item.get('label', f"Point {i+1}")
            }
            for i, item in enumerate(data)
        ]

    def _format_multi_series(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> Dict[str, Any]:
        """
        Convert to multi-series format.

        Input: [{"label": "Q1", "value": 100}, ...]
        Output: {
            "labels": ["Q1", "Q2", ...],
            "datasets": [
                {"label": "Series A", "data": [100, 120, ...]},
                {"label": "Series B", "data": [80, 90, ...]}
            ]
        }
        """
        labels = [item['label'] for item in data]

        # Create 2-3 series with variance
        num_series = random.randint(2, 3)
        datasets = []

        for i in range(num_series):
            series_data = [
                round(item['value'] * random.uniform(0.7, 1.3), 2)
                for item in data
            ]
            datasets.append({
                "label": f"Series {chr(65+i)}",  # A, B, C
                "data": series_data
            })

        return {
            "labels": labels,
            "datasets": datasets
        }

    def _format_radar(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> Dict[str, Any]:
        """
        Convert to radar format (normalized 0-100).

        Input: [{"label": "Speed", "value": 80}, ...]
        Output: {
            "labels": ["Speed", "Power", ...],
            "datasets": [{"label": "Performance", "data": [80, 90, ...]}]
        }
        """
        labels = [item['label'] for item in data]

        # Normalize values to 0-100 range
        values = [item['value'] for item in data]
        if values:
            max_val = max(values)
            normalized = [
                round((val / max_val) * 100, 1) if max_val > 0 else 50
                for val in values
            ]
        else:
            normalized = []

        return {
            "labels": labels,
            "datasets": [{
                "label": "Performance",
                "data": normalized
            }]
        }

    def _format_sankey(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Ensure Sankey flow notation.

        Input: [{"label": "A → B", "value": 100}, ...]
        Output: Unchanged (already in correct format)

        If labels don't have arrows, add them.
        """
        formatted = []

        for i, item in enumerate(data):
            label = item['label']

            # Check if label has arrow notation
            if '→' in label or '->' in label:
                formatted.append(item)
            else:
                # Add arrow notation (split at midpoint)
                if i < len(data) // 2:
                    new_label = f"Source → {label}"
                else:
                    new_label = f"{data[i - len(data)//2]['label']} → Target"

                formatted.append({
                    "label": new_label,
                    "value": item['value']
                })

        return formatted
