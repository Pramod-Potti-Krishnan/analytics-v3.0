"""
Chart.js Generator - Production Version
=======================================

Complete Chart.js chart generator for Reveal.js presentations.
Supports 23+ chart types with theming, formatting, and data labels.

This replaces ApexCharts to eliminate race conditions in multi-chart presentations.
Uses RevealChart plugin for automatic lifecycle management.

Author: Analytics Microservice v3 Team
Date: 2025-01-15
Version: 1.0.0
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional, Union

# Initialize logger
logger = logging.getLogger(__name__)


class ChartJSGenerator:
    """
    Production Chart.js generator for all chart types.

    Supports:
    - 23+ chart types (line, bar, pie, scatter, etc.)
    - 3 theme options (professional, corporate, vibrant)
    - 3 formatter types (currency, percentage, number)
    - Data labels on all charts
    - Responsive sizing
    - Grid lines and scales

    Usage:
        generator = ChartJSGenerator(theme="professional")
        html = generator.generate_line_chart(data, options)
    """

    # ========================================
    # THEMES
    # ========================================

    # v3.4.7: Updated to pastel color palette for softer visual appearance
    THEMES = {
        "professional": {
            "primary": "#93C5FD",      # Pastel Blue (Tailwind blue-300)
            "secondary": "#A7F3D0",    # Pastel Mint (Tailwind emerald-200)
            "tertiary": "#FDE68A",     # Pastel Yellow (Tailwind amber-200)
            "quaternary": "#C4B5FD",   # Pastel Lavender (Tailwind violet-300)
            "quinary": "#FBCFE8",      # Pastel Pink (Tailwind pink-200)
            "senary": "#FED7AA",       # Pastel Orange (Tailwind orange-200)
            "septenary": "#A5F3FC",    # Pastel Cyan (Tailwind cyan-200)
            "octonary": "#FCA5A5",     # Pastel Coral (Tailwind red-300)
            "palette": [
                "#93C5FD", "#A7F3D0", "#FDE68A", "#C4B5FD",
                "#FBCFE8", "#FED7AA", "#A5F3FC", "#FCA5A5"
            ],
            "gradients": {
                "blue": ["rgba(147, 197, 253, 0.8)", "rgba(147, 197, 253, 0.2)"],
                "mint": ["rgba(167, 243, 208, 0.8)", "rgba(167, 243, 208, 0.2)"],
                "yellow": ["rgba(253, 230, 138, 0.8)", "rgba(253, 230, 138, 0.2)"],
                "lavender": ["rgba(196, 181, 253, 0.8)", "rgba(196, 181, 253, 0.2)"],
                "pink": ["rgba(251, 207, 232, 0.8)", "rgba(251, 207, 232, 0.2)"],
                # Backward compatible aliases (old names map to pastel equivalents)
                "red": ["rgba(252, 165, 165, 0.8)", "rgba(252, 165, 165, 0.2)"],  # Pastel coral
                "turquoise": ["rgba(167, 243, 208, 0.8)", "rgba(167, 243, 208, 0.2)"],  # Same as mint
                "purple": ["rgba(196, 181, 253, 0.8)", "rgba(196, 181, 253, 0.2)"]  # Same as lavender
            }
        },
        "corporate": {
            "primary": "#003f5c",
            "secondary": "#2f4b7c",
            "tertiary": "#665191",
            "quaternary": "#a05195",
            "quinary": "#d45087",
            "senary": "#f95d6a",
            "septenary": "#ff7c43",
            "octonary": "#ffa600",
            "palette": [
                "#003f5c", "#2f4b7c", "#665191", "#a05195",
                "#d45087", "#f95d6a", "#ff7c43", "#ffa600"
            ],
            "gradients": {
                "blue": ["rgba(0, 63, 92, 0.8)", "rgba(0, 63, 92, 0.2)"],
                "purple": ["rgba(102, 81, 145, 0.8)", "rgba(102, 81, 145, 0.2)"],
                "pink": ["rgba(212, 80, 135, 0.8)", "rgba(212, 80, 135, 0.2)"],
                "orange": ["rgba(255, 166, 0, 0.8)", "rgba(255, 166, 0, 0.2)"]
            }
        },
        "vibrant": {
            "primary": "#FF5733",
            "secondary": "#33FF57",
            "tertiary": "#3357FF",
            "quaternary": "#F033FF",
            "quinary": "#FF33F0",
            "senary": "#33FFF0",
            "septenary": "#F0FF33",
            "octonary": "#5733FF",
            "palette": [
                "#FF5733", "#33FF57", "#3357FF", "#F033FF",
                "#FF33F0", "#33FFF0", "#F0FF33", "#5733FF"
            ],
            "gradients": {
                "red": ["rgba(255, 87, 51, 0.8)", "rgba(255, 87, 51, 0.2)"],
                "green": ["rgba(51, 255, 87, 0.8)", "rgba(51, 255, 87, 0.2)"],
                "blue": ["rgba(51, 87, 255, 0.8)", "rgba(51, 87, 255, 0.2)"],
                "purple": ["rgba(240, 51, 255, 0.8)", "rgba(240, 51, 255, 0.2)"]
            }
        }
    }

    def __init__(self, theme: str = "professional"):
        """
        Initialize Chart.js generator.

        Args:
            theme: Theme name ("professional", "corporate", "vibrant")
        """
        self.theme = theme
        if theme not in self.THEMES:
            raise ValueError(f"Unknown theme: {theme}. Use 'professional', 'corporate', or 'vibrant'")

        self.colors = self.THEMES[theme]
        self.palette = self.colors["palette"]
        self.gradients = self.colors.get("gradients", {})

    # ========================================
    # DATA TRANSFORMATION
    # ========================================

    def _transform_director_to_chartjs(self, data: Union[List, Dict]) -> Dict[str, Any]:
        """
        Transform Director Agent data format to Chart.js format.

        Director sends multi-series data as:
            [
                {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
                {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88},
                ...
            ]

        Chart.js needs:
            {
                "labels": ["Q1", "Q2", ...],
                "datasets": [
                    {"label": "North America", "data": [124, 145, ...]},
                    {"label": "EMEA", "data": [98, 112, ...]},
                    {"label": "APAC", "data": [75, 88, ...]}
                ]
            }

        Also supports backward compatibility with existing formats:
        - Array with single object: [{labels: [...], datasets: [...]}]
        - Direct object: {labels: [...], datasets: [...]}

        Args:
            data: Input data in Director or standard format

        Returns:
            Chart data in Chart.js format {labels, datasets}
        """
        # Case 1: Director format - array of label-value objects
        if isinstance(data, list) and len(data) > 0 and 'label' in data[0]:
            logger.info(f"Transforming Director format to Chart.js (detected 'label' key)")

            # Extract labels from 'label' field
            labels = [item.get('label', '') for item in data]

            # Get all series names (all keys except 'label')
            series_names = [k for k in data[0].keys() if k != 'label']

            # Build datasets for each series
            datasets = []
            for series_name in series_names:
                dataset = {
                    'label': series_name,
                    'data': [item.get(series_name, 0) for item in data]
                }
                datasets.append(dataset)

            transformed = {
                'labels': labels,
                'datasets': datasets
            }
            logger.info(f"Transformed: {len(labels)} labels, {len(datasets)} datasets")
            return transformed

        # Case 2: Array with single Chart.js object (backward compatibility)
        if isinstance(data, list) and len(data) > 0 and 'datasets' in data[0]:
            logger.info(f"Extracting Chart.js format from array (already has 'datasets')")
            return data[0]

        # Case 3: Already in Chart.js format
        if isinstance(data, dict):
            return data

        # Case 4: Array format without recognizable structure - try first element
        if isinstance(data, list) and len(data) > 0:
            logger.warning(f"Unknown array format, extracting first element")
            return data[0]

        # Default: return as-is
        return data

    # ========================================
    # LINE CHARTS
    # ========================================

    def generate_line_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",  # "inline_script" (Layout Builder) or "revealchart" (legacy)
        semantic_chart_type: Optional[str] = None,  # Semantic type for editor (e.g., "area_stacked")
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js line chart.

        Args:
            data: Chart data with keys:
                - labels: List of x-axis labels
                - values: List of y-values OR
                - datasets: List of {label, data} for multiple series
                - series_name: Name of series (optional)
                - format: "currency", "percentage", or "number"
            height: Chart height in pixels
            chart_id: Unique chart ID (auto-generated if None)
            options: Custom Chart.js options to merge
            enable_editor: If True, adds interactive data editor (default: False)
            presentation_id: Required if enable_editor=True
            api_base_url: Base URL for chart API (default: "/api/charts" for proxy)
                         Set to full URL like "https://your-analytics.com/api/charts" for direct calls
            output_mode: Output format - "revealchart" for legacy RevealChart plugin (default)
                        or "inline_script" for Layout Builder inline Chart.js initialization

        Returns:
            HTML canvas element with Chart.js config (and optional editor)
        """
        labels = data.get("labels", [])
        format_type = data.get("format", "number")

        # Handle single or multiple datasets
        if "datasets" in data:
            datasets = self._prepare_datasets(data["datasets"], "line", format_type)
        else:
            values = data.get("values", [])
            series_name = data.get("series_name", "Data")
            datasets = [{
                "label": series_name,
                "data": values,
                "borderColor": self.colors["primary"],
                "backgroundColor": self.gradients.get("red", ["rgba(255, 107, 107, 0.2)"])[1],
                "borderWidth": 4,
                "pointRadius": 6,
                "pointBackgroundColor": self.colors["primary"],
                "pointBorderColor": "#fff",
                "pointBorderWidth": 3,
                "pointHoverRadius": 8,
                "pointHoverBackgroundColor": self.colors["primary"],
                "pointHoverBorderColor": "#fff",
                "tension": 0.4,
                "fill": True
            }]

        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": self._build_chart_options(format_type, "line", options, dataset_count=len(datasets))
        }

        # v3.4.19: Stacked area - show data labels only every 3rd point to reduce clutter
        if semantic_chart_type == "area_stacked":
            if "plugins" not in config["options"]:
                config["options"]["plugins"] = {}
            if "datalabels" not in config["options"]["plugins"]:
                config["options"]["plugins"]["datalabels"] = {}
            # Function shows label only for dataIndex % 3 === 0 (every 3rd point)
            config["options"]["plugins"]["datalabels"]["display"] = "function(context) { return context.dataIndex % 3 === 0; }"

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"line-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,  # Pass through output mode
            semantic_chart_type,  # Pass semantic type for editor
            chart_title=chart_title  # v3.4.11
        )

    def generate_area_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js area chart (line chart with fill).

        Args:
            data: Chart data (same structure as line chart)
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML canvas element with Chart.js area chart configuration
        """
        # Force fill=True for all datasets
        if "datasets" in data:
            for dataset in data["datasets"]:
                dataset["fill"] = True

        return self.generate_line_chart(
            data, height, chart_id, options,
            enable_editor, presentation_id, api_base_url, output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_stacked_area_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js stacked area chart.

        Args:
            data: Chart data with multiple datasets
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML canvas element with stacked area chart configuration
        """
        # Transform Director format to Chart.js format (v3.4.4 fix)
        chart_data = self._transform_director_to_chartjs(data)

        # Add stacking options
        stack_options = {
            "scales": {
                "y": {
                    "stacked": True
                },
                "x": {
                    "stacked": True
                }
            }
        }

        merged_options = self._merge_options(options or {}, stack_options)

        # Force fill=True for all datasets
        if "datasets" in chart_data:
            for dataset in chart_data["datasets"]:
                dataset["fill"] = True

        return self.generate_line_chart(
            chart_data, height, chart_id, merged_options,
            enable_editor, presentation_id, api_base_url, output_mode,
            semantic_chart_type="area_stacked",  # Tell editor this is stacked area
            chart_title=chart_title  # v3.4.11
        )

    # ========================================
    # BAR CHARTS
    # ========================================

    def generate_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        horizontal: bool = False,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js bar chart (vertical or horizontal).

        Args:
            data: Chart data (same structure as line chart)
            height: Chart height in pixels
            horizontal: True for horizontal bars
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
            chart_title: Optional title for visual alignment

        Returns:
            HTML canvas element with Chart.js config
        """
        labels = data.get("labels", [])
        format_type = data.get("format", "number")

        # Handle single or multiple datasets
        if "datasets" in data:
            datasets = self._prepare_datasets(data["datasets"], "bar", format_type, horizontal)
        else:
            values = data.get("values", [])
            series_name = data.get("series_name", "Data")

            # Use different color for each bar
            bar_colors = self.palette[:len(values)]

            datasets = [{
                "label": series_name,
                "data": values,
                "backgroundColor": bar_colors,
                "borderColor": bar_colors,
                "borderWidth": 2,
                "borderRadius": 10,
                "hoverBorderWidth": 3,
                "hoverBorderColor": "#fff"
            }]

        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": self._build_chart_options(format_type, "bar", options, horizontal, dataset_count=len(datasets))
        }

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"bar-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_horizontal_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """Generate horizontal bar chart."""
        return self.generate_bar_chart(
            data, height, horizontal=True, chart_id=chart_id, options=options,
            enable_editor=enable_editor, presentation_id=presentation_id,
            api_base_url=api_base_url, output_mode=output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_grouped_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate grouped bar chart (multiple series side-by-side).

        Requires data["datasets"] with multiple series.
        """
        # Transform Director format to Chart.js format (v3.4.4 fix)
        chart_data = self._transform_director_to_chartjs(data)

        if "datasets" not in chart_data:
            raise ValueError("Grouped bar chart requires 'datasets' in data")

        return self.generate_bar_chart(
            chart_data, height, horizontal=False, chart_id=chart_id, options=options,
            enable_editor=enable_editor, presentation_id=presentation_id,
            api_base_url=api_base_url, output_mode=output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_stacked_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        horizontal: bool = False,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate stacked bar chart.

        Bars stacked on top of each other.
        """
        # Transform Director format to Chart.js format (v3.4.4 fix)
        chart_data = self._transform_director_to_chartjs(data)

        stack_options = {
            "scales": {
                "x": {"stacked": True},
                "y": {"stacked": True}
            }
        }

        merged_options = self._merge_options(options or {}, stack_options)
        return self.generate_bar_chart(
            chart_data, height, horizontal, chart_id, merged_options,
            enable_editor=enable_editor, presentation_id=presentation_id,
            api_base_url=api_base_url, output_mode=output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_waterfall_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js waterfall chart using native floating bars.

        Waterfall charts show cumulative effect of sequential positive/negative values.
        Common use cases: P&L statements, budget analysis, cash flow.

        Args:
            data: Chart data with:
                - labels: Category labels (e.g., ["Revenue", "COGS", "Operating Expenses", "Net Profit"])
                - values: Change values (positive or negative)
                - start_value: Optional starting value (default: 0)
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML canvas element with waterfall chart configuration

        Example data format:
            {
                "labels": ["Starting Balance", "Revenue", "Expenses", "Ending Balance"],
                "values": [1000, 500, -300, None],  # None for totals
                "start_value": 0
            }
        """
        labels = data.get("labels", [])
        values = data.get("values", [])
        start_value = data.get("start_value", 0)
        format_type = data.get("format", "number")

        # Calculate cumulative values and create floating bars [start, end]
        cumulative = start_value
        floating_data = []
        bar_colors = []

        for i, value in enumerate(values):
            if value is None:
                # Total bar - show from 0 to current cumulative
                floating_data.append([0, cumulative])
                bar_colors.append(self.palette[3])  # Neutral color for totals
            elif value >= 0:
                # Positive change - bar goes up
                floating_data.append([cumulative, cumulative + value])
                bar_colors.append(self.palette[1])  # Green for positive
                cumulative += value
            else:
                # Negative change - bar goes down
                floating_data.append([cumulative + value, cumulative])
                bar_colors.append(self.palette[4])  # Red for negative
                cumulative += value

        # Build Chart.js config with floating bars
        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Waterfall",
                    "data": floating_data,
                    "backgroundColor": bar_colors,
                    "borderColor": bar_colors,
                    "borderWidth": 2,
                    "borderRadius": 6
                }]
            },
            "options": self._build_chart_options(
                format_type, "bar", options, horizontal=False, dataset_count=1
            )
        }

        # Add waterfall-specific tooltip to show changes
        if "plugins" not in config["options"]:
            config["options"]["plugins"] = {}

        config["options"]["plugins"]["tooltip"] = {
            "callbacks": {
                "label": """function(context) {
                    const raw = context.raw;
                    const value = raw[1] - raw[0];
                    const label = context.dataset.label || '';
                    return label + ': ' + value.toFixed(2);
                }"""
            }
        }

        # Waterfall-specific datalabels formatter (data is [start, end] array, not single value)
        config["options"]["plugins"]["datalabels"] = {
            "display": True,
            "color": "#fff",
            "font": {"size": 12, "weight": "bold"},
            "formatter": """function(value) {
                if (Array.isArray(value)) {
                    const diff = value[1] - value[0];
                    if (Math.abs(diff) >= 1000000) {
                        return (diff >= 0 ? '+' : '') + (diff/1000000).toFixed(1) + 'M';
                    } else if (Math.abs(diff) >= 1000) {
                        return (diff >= 0 ? '+' : '') + (diff/1000).toFixed(0) + 'K';
                    } else {
                        return (diff >= 0 ? '+' : '') + diff.toFixed(0);
                    }
                }
                return value;
            }""",
            "anchor": "end",
            "align": "end",
            "backgroundColor": "rgba(0, 0, 0, 0.7)",
            "borderRadius": 4,
            "padding": 4
        }

        # v3.4.32: Pass semantic_chart_type='waterfall' so editor can reconstruct floating bars
        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"waterfall-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            semantic_chart_type='waterfall',  # v3.4.32: Tell editor this is a waterfall chart
            chart_title=chart_title  # v3.4.11
        )

    # ========================================
    # CIRCULAR CHARTS (PIE & DOUGHNUT)
    # ========================================

    def generate_pie_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js pie chart.

        Args:
            data: Chart data with:
                - labels: Slice labels
                - values: Slice values
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        return self._generate_circular_chart(
            "pie", data, height, chart_id, options,
            enable_editor, presentation_id, api_base_url, output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_doughnut_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js doughnut chart.

        Args:
            data: Chart data with:
                - labels: Slice labels
                - values: Slice values
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        return self._generate_circular_chart(
            "doughnut", data, height, chart_id, options,
            enable_editor, presentation_id, api_base_url, output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def _generate_circular_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        height: int,
        chart_id: Optional[str],
        options: Optional[Dict[str, Any]],
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """Internal method for pie/doughnut charts."""
        labels = data.get("labels", [])
        values = data.get("values", [])

        # Use palette colors for segments
        colors = self.palette[:len(values)]

        # Create hover colors (slightly darker)
        hover_colors = [self._darken_color(c) for c in colors]

        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": colors,
                    "borderColor": "#fff",
                    "borderWidth": 4,
                    "hoverBackgroundColor": hover_colors,
                    "hoverBorderColor": "#fff",
                    "hoverBorderWidth": 5
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "right",
                        "labels": {
                            "font": {"size": 14, "weight": "bold"},
                            "padding": 15,
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#374151",  # v3.4.8: Dark gray (was #fff - unreadable on pastel)
                        "font": {"size": 16, "weight": "bold"},
                        "formatter": "function(value, context) { return value + '%'; }",
                        "anchor": "center",
                        "align": "center"
                    }
                }
            }
        }

        if options:
            config["options"] = self._merge_options(config["options"], options)

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"{chart_type}-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    # ========================================
    # SCATTER & BUBBLE CHARTS
    # ========================================

    def generate_scatter_plot(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js scatter plot.

        Args:
            data: Chart data with:
                - datasets: List of {label, data: [{x, y}, ...]}
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        if "datasets" not in data:
            raise ValueError("Scatter plot requires 'datasets' in data")

        format_type = data.get("format", "number")
        datasets = self._prepare_datasets(data["datasets"], "scatter", format_type)

        config = {
            "type": "scatter",
            "data": {"datasets": datasets},
            "options": self._build_chart_options(format_type, "scatter", options, dataset_count=len(datasets))
        }

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"scatter-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_bubble_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js bubble chart.

        Args:
            data: Chart data with:
                - datasets: List of {label, data: [{x, y, r}, ...]}
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        if "datasets" not in data:
            raise ValueError("Bubble chart requires 'datasets' in data")

        format_type = data.get("format", "number")
        datasets = self._prepare_datasets(data["datasets"], "bubble", format_type)

        # v3.3.0: Add custom tooltip to show bubble labels instead of "Analytics"
        bubble_tooltip_options = {
            "plugins": {
                "tooltip": {
                    "callbacks": {
                        "title": "function(context) { return context[0].raw.label || 'Bubble ' + (context[0].dataIndex + 1); }",
                        "label": "function(context) { const raw = context.raw; return [`X: ${raw.x}`, `Y: ${raw.y}`, `Size: ${raw.r}`]; }"
                    }
                }
            }
        }

        # Merge bubble tooltip options with any user-provided options
        merged_options = self._merge_options(bubble_tooltip_options, options or {})

        config = {
            "type": "bubble",
            "data": {"datasets": datasets},
            "options": self._build_chart_options(format_type, "bubble", merged_options, dataset_count=len(datasets))
        }

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"bubble-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    # ========================================
    # RADAR & POLAR CHARTS
    # ========================================

    def generate_radar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js radar chart.

        Args:
            data: Chart data with:
                - labels: Axis labels
                - datasets: List of {label, data}
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        labels = data.get("labels", [])
        format_type = data.get("format", "number")

        datasets = self._prepare_datasets(data.get("datasets", []), "radar", format_type)

        config = {
            "type": "radar",
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top",
                        "labels": {
                            "font": {"size": 14, "weight": "bold"},
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#fff",
                        "font": {"size": 12, "weight": "bold"},
                        "formatter": self._get_datalabel_formatter(format_type)
                    }
                },
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "ticks": {
                            "font": {"size": 11},
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    }
                }
            }
        }

        if options:
            config["options"] = self._merge_options(config["options"], options)

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"radar-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_polar_area_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js polar area chart.

        Similar to pie chart but uses radial scale.

        Args:
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        labels = data.get("labels", [])
        values = data.get("values", [])

        colors = self.palette[:len(values)]

        config = {
            "type": "polarArea",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": colors,
                    "borderColor": "#fff",
                    "borderWidth": 2
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "right",
                        "labels": {
                            "font": {"size": 14, "weight": "bold"},
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#fff",
                        "font": {"size": 14, "weight": "bold"}
                    }
                },
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "ticks": {"font": {"size": 11}}
                    }
                }
            }
        }

        if options:
            config["options"] = self._merge_options(config["options"], options)

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"polar-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    def generate_treemap_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js treemap chart using chartjs-chart-treemap plugin.

        Treemaps visualize hierarchical data as nested rectangles sized by value.
        Common use cases: Portfolio composition, disk space, market cap by sector.

        Args:
            data: Chart data with:
                - labels: Labels for each node
                - values: Values for each node (for sizing)
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML with treemap chart and embedded plugin

        Example data format:
            {
                "labels": ["Tech", "Finance", "Healthcare", "Energy"],
                "values": [450, 300, 200, 50]
            }
        """
        labels = data.get("labels", [])
        values = data.get("values", [])
        format_type = data.get("format", "number")

        # Transform flat data into treemap format
        tree_data = []
        for i, (label, value) in enumerate(zip(labels, values)):
            tree_data.append({
                "label": label,
                "value": value,
                "color": self.palette[i % len(self.palette)]
            })

        # Build Chart.js treemap config
        config = {
            "type": "treemap",
            "data": {
                "datasets": [{
                    "tree": tree_data,
                    "key": "value",
                    "groups": ["label"],
                    "spacing": 1,
                    "borderWidth": 2,
                    "borderColor": "#fff",
                    "backgroundColor": "placeholder_for_background_color",
                    "labels": {
                        "display": True,
                        "formatter": "placeholder_for_label_formatter",
                        "color": "#fff",
                        "font": {"size": 14, "weight": "bold"}
                    }
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "title": "placeholder_title_function",
                            "label": "placeholder_label_function"
                        }
                    }
                }
            }
        }

        # Merge custom options if provided
        if options:
            config["options"] = self._merge_options(config["options"], options)

        # Convert config to JSON then replace placeholders with actual functions
        config_json = json.dumps(config)
        config_json = config_json.replace(
            '"placeholder_for_background_color"',
            'function(ctx) { return ctx.raw.color || "' + self.palette[0] + '"; }'
        )
        config_json = config_json.replace(
            '"placeholder_for_label_formatter"',
            'function(ctx) { return ctx.raw.label; }'
        )
        config_json = config_json.replace(
            '"placeholder_title_function"',
            'function(context) { return context[0].raw.label; }'
        )
        config_json = config_json.replace(
            '"placeholder_label_function"',
            f'function(context) {{ return "{format_type}: " + context.raw.value; }}'
        )

        # Build HTML with treemap plugin loaded
        chart_id_safe = chart_id or f"treemap-{id(data)}"

        # v3.4.11: Build title HTML if chart_title is provided
        title_html = ""
        canvas_style = ""
        if chart_title:
            title_html = f'''<div class="chart-title" style="height: 80px; padding-top: 40px; padding-left: 20px; padding-right: 20px; flex-shrink: 0;">
      <h3 style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 24px; font-weight: 600; color: #1E3A5F; line-height: 40px;">{chart_title}</h3>
    </div>'''
            canvas_style = 'style="flex: 1; min-height: 0;"'

        treemap_html = f"""<!-- Treemap Chart with Chart.js Treemap Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@3.1.0/dist/chartjs-chart-treemap.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
    {title_html}
    <div {canvas_style}>
      <canvas id="{chart_id_safe}"></canvas>
    </div>
    <script>
        (function() {{
            function initTreemap() {{
                const ctx = document.getElementById('{chart_id_safe}').getContext('2d');
                const config = {config_json};

                const chart = new Chart(ctx, config);

                // Store for editor access
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = chart;

                console.log('✅ Treemap {chart_id_safe} initialized');
            }}

            // Initialize after treemap plugin loads
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initTreemap);
            }} else {{
                initTreemap();
            }}
        }})();
    </script>
  </div>
</div>"""

        return treemap_html

    def generate_heatmap_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js heatmap/matrix chart using chartjs-chart-matrix plugin.

        Heatmaps visualize data values in a 2D grid with color-coded cells.
        Common use cases: Correlation matrices, time-based patterns, activity heatmaps.

        Args:
            data: Chart data with:
                - x_labels: X-axis labels (columns)
                - y_labels: Y-axis labels (rows)
                - values: 2D array of values or flat array with x, y, v
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML with heatmap chart and embedded plugin

        Example data format:
            {
                "x_labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                "y_labels": ["9am", "12pm", "3pm", "6pm"],
                "values": [[10, 20, 30, 25, 15], [15, 25, 35, 30, 20], ...]
            }
        """
        x_labels = data.get("x_labels", [])
        y_labels = data.get("y_labels", [])
        values = data.get("values", [])
        format_type = data.get("format", "number")

        # Transform 2D array into matrix format [{x, y, v}, ...]
        matrix_data = []
        if isinstance(values[0], list):
            # 2D array format
            for y_idx, row in enumerate(values):
                for x_idx, value in enumerate(row):
                    matrix_data.append({
                        "x": x_labels[x_idx] if x_idx < len(x_labels) else f"Col{x_idx}",
                        "y": y_labels[y_idx] if y_idx < len(y_labels) else f"Row{y_idx}",
                        "v": value
                    })
        else:
            # Flat array with x, y, v already
            matrix_data = values

        # Calculate min/max for color scale
        all_values = [item["v"] if isinstance(item, dict) else item for item in matrix_data]
        min_val = min(all_values) if all_values else 0
        max_val = max(all_values) if all_values else 100

        # Build Chart.js matrix config
        config = {
            "type": "matrix",
            "data": {
                "datasets": [{
                    "label": "Heatmap",
                    "data": matrix_data,
                    "backgroundColor": "placeholder_bg_function",
                    "borderWidth": 1,
                    "borderColor": "#fff",
                    "width": "placeholder_width_function",
                    "height": "placeholder_height_function"
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "title": "placeholder_title",
                            "label": "placeholder_label"
                        }
                    }
                },
                "scales": {
                    "x": {
                        "type": "category",
                        "labels": x_labels,
                        "ticks": {"font": {"size": 12}},
                        "grid": {"display": False}
                    },
                    "y": {
                        "type": "category",
                        "labels": y_labels,
                        "offset": True,
                        "ticks": {"font": {"size": 12}},
                        "grid": {"display": False}
                    }
                }
            }
        }

        # Merge custom options
        if options:
            config["options"] = self._merge_options(config["options"], options)

        # Convert to JSON and inject functions
        config_json = json.dumps(config)

        # Color scale function (gradient from blue to red)
        config_json = config_json.replace(
            '"placeholder_bg_function"',
            f"""function(ctx) {{
                const value = ctx.dataset.data[ctx.dataIndex].v;
                const normalized = (value - {min_val}) / ({max_val} - {min_val});
                const r = Math.round(normalized * 255);
                const b = Math.round((1 - normalized) * 255);
                return `rgba(${{r}}, 100, ${{b}}, 0.8)`;
            }}"""
        )

        # Width and height functions
        config_json = config_json.replace(
            '"placeholder_width_function"',
            'function(ctx) { return (ctx.chart.chartArea || {}).width / ' + str(len(x_labels) if x_labels else 5) + ' - 1; }'
        )
        config_json = config_json.replace(
            '"placeholder_height_function"',
            'function(ctx) { return (ctx.chart.chartArea || {}).height / ' + str(len(y_labels) if y_labels else 4) + ' - 1; }'
        )

        # Tooltip functions
        config_json = config_json.replace(
            '"placeholder_title"',
            'function(ctx) { return ctx[0].raw.y + " - " + ctx[0].raw.x; }'
        )
        config_json = config_json.replace(
            '"placeholder_label"',
            f'function(ctx) {{ return "{format_type}: " + ctx.raw.v; }}'
        )

        # Build HTML with matrix plugin
        chart_id_safe = chart_id or f"heatmap-{id(data)}"

        # v3.4.11: Build title HTML if chart_title is provided
        title_html = ""
        canvas_style = ""
        if chart_title:
            title_html = f'''<div class="chart-title" style="height: 80px; padding-top: 40px; padding-left: 20px; padding-right: 20px; flex-shrink: 0;">
      <h3 style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 24px; font-weight: 600; color: #1E3A5F; line-height: 40px;">{chart_title}</h3>
    </div>'''
            canvas_style = 'style="flex: 1; min-height: 0;"'

        heatmap_html = f"""<!-- Heatmap/Matrix Chart with Chart.js Matrix Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@3.0.0/dist/chartjs-chart-matrix.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
    {title_html}
    <div {canvas_style}>
      <canvas id="{chart_id_safe}"></canvas>
    </div>
    <script>
        (function() {{
            function initHeatmap() {{
                const ctx = document.getElementById('{chart_id_safe}').getContext('2d');
                const config = {config_json};

                const chart = new Chart(ctx, config);

                // Store for editor access
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = chart;

                console.log('✅ Heatmap {chart_id_safe} initialized');
            }}

            // Initialize after matrix plugin loads
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initHeatmap);
            }} else {{
                initHeatmap();
            }}
        }})();
    </script>
  </div>
</div>"""

        return heatmap_html

    def generate_boxplot_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js boxplot chart using chartjs-chart-boxplot plugin.

        Boxplots show statistical distribution with min, Q1, median, Q3, max, and outliers.
        Common use cases: Salary distributions, performance metrics, A/B test results.

        Args:
            data: Chart data with:
                - labels: Category labels
                - datasets: List of {label, data: [[min, q1, median, q3, max], ...]}
                  OR raw data arrays that will be auto-calculated
            height: Chart height in pixels
            chart_id: Unique chart ID
            options: Custom Chart.js options
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)

        Returns:
            HTML with boxplot chart and embedded plugin

        Example data format:
            {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [{
                    "label": "Sales Distribution",
                    "data": [[100, 250, 350, 450, 600], [120, 270, 380, 480, 650], ...]
                }]
            }
        """
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        format_type = data.get("format", "number")

        # Prepare datasets with colors
        prepared_datasets = []
        for i, dataset in enumerate(datasets):
            color = self.palette[i % len(self.palette)]
            prepared_datasets.append({
                "label": dataset.get("label", f"Series {i+1}"),
                "data": dataset.get("data", []),
                "backgroundColor": color.replace(')', ', 0.5)').replace('rgb', 'rgba'),
                "borderColor": color,
                "borderWidth": 2,
                "outlierBackgroundColor": self.palette[(i+1) % len(self.palette)],
                "outlierRadius": 3
            })

        # Build Chart.js boxplot config
        config = {
            "type": "boxplot",
            "data": {
                "labels": labels,
                "datasets": prepared_datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": len(datasets) > 1,
                        "position": "top",
                        "labels": {
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    },
                    "tooltip": {
                        "callbacks": {
                            "label": "placeholder_label"
                        }
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": False,
                        "ticks": {"font": {"size": 12}},
                        "grid": {"color": "rgba(107, 114, 128, 0.15)"}  # v3.4.18: gray-500 at 15%
                    },
                    "x": {
                        "ticks": {"font": {"size": 12}},
                        "grid": {"display": False}
                    }
                }
            }
        }

        # Merge custom options
        if options:
            config["options"] = self._merge_options(config["options"], options)

        # Convert to JSON and inject tooltip function
        config_json = json.dumps(config)
        config_json = config_json.replace(
            '"placeholder_label"',
            f"""function(ctx) {{
                const data = ctx.parsed;
                return [
                    '{format_type} - Max: ' + data.max,
                    'Q3: ' + data.q3,
                    'Median: ' + data.median,
                    'Q1: ' + data.q1,
                    'Min: ' + data.min
                ];
            }}"""
        )

        # Build HTML with boxplot plugin
        chart_id_safe = chart_id or f"boxplot-{id(data)}"

        # v3.4.11: Build title HTML if chart_title is provided
        title_html = ""
        canvas_style = ""
        if chart_title:
            title_html = f'''<div class="chart-title" style="height: 80px; padding-top: 40px; padding-left: 20px; padding-right: 20px; flex-shrink: 0;">
      <h3 style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 24px; font-weight: 600; color: #1E3A5F; line-height: 40px;">{chart_title}</h3>
    </div>'''
            canvas_style = 'style="flex: 1; min-height: 0;"'

        boxplot_html = f"""<!-- Boxplot Chart with Chart.js Boxplot Plugin -->
<script src="https://cdn.jsdelivr.net/npm/@sgratzl/chartjs-chart-boxplot@4.4.5/build/index.umd.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
    {title_html}
    <div {canvas_style}>
      <canvas id="{chart_id_safe}"></canvas>
    </div>
    <script>
        (function() {{
            function initBoxplot() {{
                const ctx = document.getElementById('{chart_id_safe}').getContext('2d');
                const config = {config_json};

                const chart = new Chart(ctx, config);

                // Store for editor access
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = chart;

                console.log('✅ Boxplot {chart_id_safe} initialized');
            }}

            // Initialize after boxplot plugin loads
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initBoxplot);
            }} else {{
                initBoxplot();
            }}
        }})();
    </script>
  </div>
</div>"""

        return boxplot_html

    def generate_candlestick_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js candlestick/financial chart using chartjs-chart-financial plugin.

        Args:
            data: Chart data with:
                - labels: Time labels (dates/timestamps)
                - datasets: List of {label, data: [{x, o, h, l, c}, ...]}
                  where o=open, h=high, l=low, c=close
            height: Canvas height in pixels
            chart_id: Unique identifier for the chart
            options: Additional Chart.js options to override defaults
            enable_editor: Include interactive edit button
            presentation_id: Presentation ID for editor
            api_base_url: Base URL for chart API
            output_mode: Output format ("inline_script" for Layout Builder)

        Returns:
            HTML string with candlestick chart and chartjs-chart-financial plugin loaded
        """
        labels = data.get("labels", [])
        datasets = data.get("datasets", [])
        format_type = data.get("format", "currency")

        # Prepare candlestick datasets
        prepared_datasets = []
        for i, dataset in enumerate(datasets):
            # Transform data to candlestick format if needed
            candlestick_data = []
            raw_data = dataset.get("data", [])

            for j, item in enumerate(raw_data):
                if isinstance(item, dict):
                    # Already in {x, o, h, l, c} format
                    candlestick_data.append(item)
                elif isinstance(item, (list, tuple)) and len(item) >= 4:
                    # [open, high, low, close] format
                    candlestick_data.append({
                        "x": labels[j] if j < len(labels) else j,
                        "o": item[0],  # open
                        "h": item[1],  # high
                        "l": item[2],  # low
                        "c": item[3]   # close
                    })

            prepared_datasets.append({
                "label": dataset.get("label", f"Series {i+1}"),
                "data": candlestick_data,
                "color": {
                    "up": self.palette[1],    # Green for price up
                    "down": self.palette[4],  # Red for price down
                    "unchanged": self.palette[3]  # Neutral for unchanged
                },
                "borderColor": {
                    "up": self.palette[1],
                    "down": self.palette[4],
                    "unchanged": self.palette[3]
                }
            })

        # Build Chart.js candlestick config
        config = {
            "type": "candlestick",
            "data": {
                "datasets": prepared_datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": len(datasets) > 1,
                        "position": "top",
                        "labels": {
                            "font": {"size": 14},
                            "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                        }
                    },
                    "tooltip": {
                        "mode": "index",
                        "intersect": False,
                        "callbacks": {
                            "label": "placeholder_label_function"
                        }
                    },
                    "title": {
                        "display": False
                    }
                },
                "scales": {
                    "x": {
                        "type": "time",
                        "time": {
                            "unit": "day",
                            "displayFormats": {
                                "day": "MMM d"
                            }
                        },
                        "ticks": {"font": {"size": 12}},
                        "grid": {"display": False}
                    },
                    "y": {
                        "beginAtZero": False,
                        "ticks": {
                            "font": {"size": 12},
                            "callback": "placeholder_y_callback"
                        },
                        "grid": {"color": "rgba(107, 114, 128, 0.15)"}  # v3.4.18: gray-500 at 15%
                    }
                }
            }
        }

        # Merge with user options if provided
        if options:
            self._deep_merge(config["options"], options)

        # Convert to JSON and inject functions
        config_json = json.dumps(config)

        # Tooltip function showing OHLC values
        if format_type == "currency":
            label_format = """function(ctx) {
                const data = ctx.parsed;
                return [
                    'Open: $' + data.o.toFixed(2),
                    'High: $' + data.h.toFixed(2),
                    'Low: $' + data.l.toFixed(2),
                    'Close: $' + data.c.toFixed(2)
                ];
            }"""
            y_callback = "function(value) { return '$' + value.toFixed(2); }"
        else:
            label_format = """function(ctx) {
                const data = ctx.parsed;
                return [
                    'Open: ' + data.o.toFixed(2),
                    'High: ' + data.h.toFixed(2),
                    'Low: ' + data.l.toFixed(2),
                    'Close: ' + data.c.toFixed(2)
                ];
            }"""
            y_callback = "function(value) { return value.toFixed(2); }"

        config_json = config_json.replace('"placeholder_label_function"', label_format)
        config_json = config_json.replace('"placeholder_y_callback"', y_callback)

        # Generate unique chart ID
        chart_id_safe = chart_id or f"candlestick-{id(data)}"

        # v3.4.11: Build title HTML if chart_title is provided
        title_html = ""
        canvas_style = ""
        if chart_title:
            title_html = f'''<div class="chart-title" style="height: 80px; padding-top: 40px; padding-left: 20px; padding-right: 20px; flex-shrink: 0;">
      <h3 style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 24px; font-weight: 600; color: #1E3A5F; line-height: 40px;">{chart_title}</h3>
    </div>'''
            canvas_style = 'style="flex: 1; min-height: 0;"'

        # Build HTML with financial plugin and Chart.js date adapter
        candlestick_html = f"""<!-- Candlestick/Financial Chart with Chart.js Financial Plugin -->
<script src="https://cdn.jsdelivr.net/npm/luxon@3.3.0/build/global/luxon.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.1/dist/chartjs-adapter-luxon.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.2.1/dist/chartjs-chart-financial.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
    {title_html}
    <div {canvas_style}>
      <canvas id="{chart_id_safe}"></canvas>
    </div>
    <script>
        (function() {{
            function initCandlestick() {{
                // v3.3.4: Destroy existing chart to replay animation
                if (window.chartInstances && window.chartInstances['{chart_id_safe}']) {{
                    console.log('Chart {chart_id_safe} exists, destroying to replay animation...');
                    window.chartInstances['{chart_id_safe}'].destroy();
                    delete window.chartInstances['{chart_id_safe}'];
                }}

                const ctx = document.getElementById('{chart_id_safe}').getContext('2d');
                const config = {config_json};

                const chart = new Chart(ctx, config);

                // Store for editor access
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = chart;

                console.log('✅ Candlestick {chart_id_safe} initialized');
            }}

            // Initialize after financial plugin loads
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initCandlestick);
            }} else {{
                initCandlestick();
            }}

            // v3.3.4: Reinitialize on slide change for animation replay
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('slidechanged', function(event) {{
                    try {{
                        if (event.currentSlide && event.currentSlide.querySelector('#{chart_id_safe}')) {{
                            initCandlestick();
                        }}
                    }} catch (e) {{
                        console.warn('Candlestick init on slide change failed:', e);
                    }}
                }});
            }}
        }})();
    </script>
  </div>
</div>"""

        logger.info(f"Generated candlestick chart {chart_id_safe}")
        return candlestick_html

    def generate_sankey_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate Chart.js sankey diagram using chartjs-chart-sankey plugin.

        Args:
            data: Chart data with:
                - nodes: List of node labels (or {id, label} objects)
                - flows: List of {from, to, value} flow connections
            height: Canvas height in pixels
            chart_id: Unique identifier for the chart
            options: Additional Chart.js options to override defaults
            enable_editor: Include interactive edit button
            presentation_id: Presentation ID for editor
            api_base_url: Base URL for chart API
            output_mode: Output format ("inline_script" for Layout Builder)

        Returns:
            HTML string with sankey diagram and chartjs-chart-sankey plugin loaded
        """
        nodes = data.get("nodes", [])
        flows = data.get("flows", [])
        format_type = data.get("format", "number")

        # Transform nodes to sankey format
        sankey_nodes = []
        if nodes and isinstance(nodes[0], str):
            # Simple string array - convert to {id, label} format
            sankey_nodes = [{"id": node, "label": node} for node in nodes]
        else:
            # Already in object format
            sankey_nodes = nodes

        # Assign colors to nodes using palette
        for i, node in enumerate(sankey_nodes):
            if "color" not in node:
                node["color"] = self.palette[i % len(self.palette)]

        # Transform flows to sankey format
        sankey_flows = []
        for flow in flows:
            sankey_flows.append({
                "from": flow.get("from"),
                "to": flow.get("to"),
                "flow": flow.get("value", flow.get("flow", 0))
            })

        # Build Chart.js sankey config
        config = {
            "type": "sankey",
            "data": {
                "datasets": [{
                    "data": sankey_flows,
                    "colorFrom": "placeholder_color_from",
                    "colorTo": "placeholder_color_to",
                    "colorMode": "gradient",
                    "labels": {
                        "display": True,
                        "font": {"size": 12, "weight": "bold"},
                        "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                    },
                    "size": "max",
                    "borderWidth": 0
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": False},
                    "tooltip": {
                        "callbacks": {
                            "label": "placeholder_label_function"
                        }
                    },
                    "title": {
                        "display": False
                    }
                }
            }
        }

        # Merge with user options if provided
        if options:
            self._deep_merge(config["options"], options)

        # Convert to JSON and inject functions
        config_json = json.dumps(config)

        # Create node color mapping for flows
        node_colors_json = json.dumps({node["id"]: node["color"] for node in sankey_nodes})

        # Color functions using node colors
        color_from_func = f"""function(ctx) {{
            const nodeColors = {node_colors_json};
            return nodeColors[ctx.dataset.data[ctx.dataIndex].from] || '{self.palette[0]}';
        }}"""

        color_to_func = f"""function(ctx) {{
            const nodeColors = {node_colors_json};
            return nodeColors[ctx.dataset.data[ctx.dataIndex].to] || '{self.palette[1]}';
        }}"""

        # Tooltip function
        if format_type == "currency":
            label_func = """function(ctx) {
                const flow = ctx.dataset.data[ctx.dataIndex];
                return flow.from + ' → ' + flow.to + ': $' + flow.flow.toLocaleString();
            }"""
        elif format_type == "percentage":
            label_func = """function(ctx) {
                const flow = ctx.dataset.data[ctx.dataIndex];
                return flow.from + ' → ' + flow.to + ': ' + flow.flow.toFixed(1) + '%';
            }"""
        else:
            label_func = """function(ctx) {
                const flow = ctx.dataset.data[ctx.dataIndex];
                return flow.from + ' → ' + flow.to + ': ' + flow.flow.toLocaleString();
            }"""

        config_json = config_json.replace('"placeholder_color_from"', color_from_func)
        config_json = config_json.replace('"placeholder_color_to"', color_to_func)
        config_json = config_json.replace('"placeholder_label_function"', label_func)

        # Generate unique chart ID
        chart_id_safe = chart_id or f"sankey-{id(data)}"

        # v3.4.11: Build title HTML if chart_title is provided
        title_html = ""
        canvas_style = ""
        if chart_title:
            title_html = f'''<div class="chart-title" style="height: 80px; padding-top: 40px; padding-left: 20px; padding-right: 20px; flex-shrink: 0;">
      <h3 style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 24px; font-weight: 600; color: #1E3A5F; line-height: 40px;">{chart_title}</h3>
    </div>'''
            canvas_style = 'style="flex: 1; min-height: 0;"'

        # Build HTML with sankey plugin
        sankey_html = f"""<!-- Sankey Diagram with Chart.js Sankey Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.12.0/dist/chartjs-chart-sankey.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
    {title_html}
    <div {canvas_style}>
      <canvas id="{chart_id_safe}"></canvas>
    </div>
    <script>
        (function() {{
            function initSankey() {{
                // v3.3.4: Destroy existing chart to replay animation
                if (window.chartInstances && window.chartInstances['{chart_id_safe}']) {{
                    console.log('Chart {chart_id_safe} exists, destroying to replay animation...');
                    window.chartInstances['{chart_id_safe}'].destroy();
                    delete window.chartInstances['{chart_id_safe}'];
                }}

                const ctx = document.getElementById('{chart_id_safe}').getContext('2d');
                const config = {config_json};

                const chart = new Chart(ctx, config);

                // Store for editor access
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = chart;

                console.log('✅ Sankey {chart_id_safe} initialized');
            }}

            // Initialize after sankey plugin loads
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initSankey);
            }} else {{
                initSankey();
            }}

            // v3.3.4: Reinitialize on slide change for animation replay
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('slidechanged', function(event) {{
                    try {{
                        if (event.currentSlide && event.currentSlide.querySelector('#{chart_id_safe}')) {{
                            initSankey();
                        }}
                    }} catch (e) {{
                        console.warn('Sankey init on slide change failed:', e);
                    }}
                }});
            }}
        }})();
    </script>
  </div>
</div>"""

        logger.info(f"Generated sankey diagram {chart_id_safe}")
        return sankey_html

    # ========================================
    # SPECIALIZED CHARTS
    # ========================================

    def generate_mixed_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate mixed chart (e.g., line + bar).

        Args:
            data: Chart data with:
                - labels: X-axis labels
                - datasets: List of {type, label, data}
                  Each dataset has its own type (line, bar, etc.)
            enable_editor: Whether to add interactive chart editor
            presentation_id: Presentation ID for editor persistence
            api_base_url: Base URL for chart API endpoints
            output_mode: "revealchart" (legacy) or "inline_script" (Layout Builder)
        """
        # Transform Director format to Chart.js format (v3.4.4 fix)
        chart_data = self._transform_director_to_chartjs(data)

        labels = chart_data.get("labels", [])
        format_type = chart_data.get("format", "number")

        datasets = []
        for idx, ds in enumerate(chart_data.get("datasets", [])):
            dataset_type = ds.get("type", "line")
            prepared_ds = {
                "type": dataset_type,
                "label": ds.get("label", f"Series {idx+1}"),
                "data": ds.get("data", []),
                "backgroundColor": self.palette[idx % len(self.palette)],
                "borderColor": self.palette[idx % len(self.palette)],
                "borderWidth": 3 if dataset_type == "line" else 2
            }

            if dataset_type == "line":
                prepared_ds.update({
                    "fill": False,
                    "tension": 0.4,
                    "pointRadius": 4,
                    "pointBackgroundColor": self.palette[idx % len(self.palette)]
                })

            datasets.append(prepared_ds)

        config = {
            "type": "line",  # Base type
            "data": {
                "labels": labels,
                "datasets": datasets
            },
            "options": self._build_chart_options(format_type, "mixed", options, dataset_count=len(datasets))
        }

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"mixed-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode,
            chart_title=chart_title  # v3.4.11
        )

    # ========================================
    # HELPER METHODS
    # ========================================

    def _wrap_in_canvas(
        self,
        config: dict,
        height: int,
        chart_id: str,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",  # "revealchart" or "inline_script"
        semantic_chart_type: Optional[str] = None,  # Semantic type for editor
        chart_title: Optional[str] = None  # v3.4.11: Chart title for visual alignment
    ) -> str:
        """
        Wrap Chart.js config in canvas element.

        Supports two output modes:
        - "revealchart": Canvas with JSON comment (for RevealChart plugin) - LEGACY
        - "inline_script": Canvas with inline Chart.js initialization (for Layout Builder) - NEW

        Args:
            config: Complete Chart.js configuration
            height: Canvas height in pixels
            chart_id: Unique chart identifier
            enable_editor: If True, adds interactive data editor
            presentation_id: Required if enable_editor=True
            api_base_url: Base URL for chart API endpoints
            output_mode: Output format ("revealchart" or "inline_script")
            chart_title: Optional chart title for visual alignment with Key Insights

        Returns:
            HTML with chart, optionally with interactive editor
        """
        if output_mode == "inline_script":
            # Layout Builder mode: Generate inline script with IIFE wrapper
            return self._wrap_in_canvas_inline_script(
                config,
                height,
                chart_id,
                enable_editor,
                presentation_id,
                api_base_url,
                semantic_chart_type,  # Pass semantic type for editor
                chart_title  # v3.4.11: Pass chart title
            )

        # Legacy RevealChart mode
        config_json = json.dumps(config, indent=2)

        # IMPORTANT: When editor is enabled, don't set fixed height on canvas
        # Let the wrapper div control sizing for proper responsive behavior
        if enable_editor:
            canvas_html = f"""<canvas id="{chart_id}" data-chart="{config['type']}" style="width: 100%; height: 100%;">
<!--
{config_json}
-->
</canvas>"""
        else:
            canvas_html = f"""<canvas id="{chart_id}" data-chart="{config['type']}" height="{height}">
<!--
{config_json}
-->
</canvas>"""

        # Add interactive editor if requested
        if enable_editor:
            return self._wrap_with_interactive_editor(
                canvas_html,
                chart_id,
                presentation_id or "unknown",
                height,
                api_base_url
            )

        return canvas_html

    def _wrap_in_canvas_inline_script(
        self,
        config: dict,
        height: int,
        chart_id: str,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        semantic_chart_type: Optional[str] = None,  # Semantic type for editor
        chart_title: Optional[str] = None  # v3.4.11: Chart title for visual alignment
    ) -> str:
        """
        Generate Layout Builder-compliant HTML with inline Chart.js script.

        Follows exact specification from Layout Builder L02_DIRECTOR_INTEGRATION_GUIDE.md:
        - Container div with class="l02-chart-container"
        - Explicit dimensions: 1260px × 720px
        - position: relative for proper rendering
        - Canvas element (no JSON comment)
        - Inline <script> tag with IIFE wrapper
        - maintainAspectRatio: false

        v3.4.11: Added chart_title for visual alignment with Key Insights box.
        - Title displays with 40px top margin to align with Key Insights panel
        - Uses flexbox layout for proper canvas sizing

        Args:
            config: Complete Chart.js configuration
            height: Canvas height (1260px for L02, but can be overridden)
            chart_id: Unique chart identifier
            enable_editor: If True, adds interactive data editor
            presentation_id: Required if enable_editor=True
            api_base_url: Base URL for chart API endpoints
            chart_title: Optional title to display above chart

        Returns:
            Complete HTML with chart and optional editor, Layout Builder compliant
        """
        # Convert config to JSON string for inline script
        config_json = json.dumps(config)

        # v3.4.7: Convert callback/formatter strings to actual JavaScript functions
        # JSON serializes functions as strings, but Chart.js needs actual functions
        # This uses a helper function to properly handle multiline functions
        def convert_function_strings(match):
            """Convert quoted function strings to unquoted JavaScript functions."""
            key = match.group(1)  # "callback" or "formatter"
            func_str = match.group(2)  # The function definition with quotes
            # Remove the surrounding quotes and unescape any escaped characters
            func_body = func_str[1:-1]  # Remove first and last quote
            func_body = func_body.replace('\\n', '\n').replace('\\"', '"')
            return f'"{key}": {func_body}'

        # Match "callback": "function...", "formatter": "function...", "display": "function...",
        # "label": "function...", or "title": "function..."
        # The pattern captures the entire quoted function string
        # v3.4.19: Added "display" for datalabels.display function support (stacked area)
        # v3.4.x: Added "label|title" for tooltip callbacks (waterfall chart fix)
        config_json = re.sub(
            r'"(callback|formatter|display|label|title)":\s*("function\([^)]*\)\s*\{[^"]*\}")',
            convert_function_strings,
            config_json
        )

        # Sanitize chart_id for JavaScript
        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

        # Build inline script with IIFE wrapper and Reveal.js-aware initialization
        # v3.3.4: Destroy and recreate chart on every slide visit to replay animations
        # This follows Layout Builder specification with Reveal.js timing fix
        # v3.4.25: Check localStorage for saved chart data to persist edits across slide navigation
        inline_script = f"""(function() {{
      function initChart() {{
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['{chart_id}']) {{
          console.log('Chart {chart_id} exists, destroying to replay animation...');
          window.chartInstances['{chart_id}'].destroy();
          delete window.chartInstances['{chart_id}'];
        }}

        const ctx = document.getElementById('{chart_id}').getContext('2d');
        const chartConfig = {config_json};

        // v3.4.25: Check localStorage for saved chart data (persists edits across navigation)
        // v3.4.29: Fixed to handle BOTH formats: multi-series {{labels, datasets}} AND simple array [{{label, value}}]
        // v3.4.30: Fixed key collision - now unique per presentation (presentationId + chartId)
        const pathParts = window.location.pathname.split('/');
        const pIndex = pathParts.indexOf('p');
        const presentationId = pIndex !== -1 ? pathParts[pIndex + 1] : 'default';
        const storageKey = 'chartData_' + presentationId + '_' + '{chart_id}';
        const savedData = localStorage.getItem(storageKey);
        if (savedData) {{
          try {{
            const parsed = JSON.parse(savedData);
            console.log('📂 Loading saved chart data from localStorage for {chart_id}');

            // Check format: multi-series {{labels, datasets}} vs simple array [{{label, value}}]
            if (Array.isArray(parsed) && parsed.length > 0 && parsed[0].label !== undefined) {{
              // Simple array format: [{{label: "...", value: ...}}, ...]
              // Used by single-series charts (line, bar, pie, waterfall, etc.)
              console.log('📂 Applying simple array format from localStorage');
              chartConfig.data.labels = parsed.map(d => d.label);
              if (chartConfig.data.datasets[0]) {{
                chartConfig.data.datasets[0].data = parsed.map(d => d.value);
              }}
            }} else if (parsed.labels && parsed.datasets) {{
              // Multi-series format: {{labels: [...], datasets: [...]}}
              console.log('📂 Applying multi-series format from localStorage');
              chartConfig.data.labels = parsed.labels;
              parsed.datasets.forEach((savedDs, i) => {{
                if (chartConfig.data.datasets[i]) {{
                  // Preserve styling, update label and data
                  chartConfig.data.datasets[i].label = savedDs.label;
                  chartConfig.data.datasets[i].data = savedDs.data;
                }}
              }});
            }}
          }} catch (e) {{
            console.warn('Failed to load saved chart data:', e);
          }}
        }}

        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {{}};
        window.chartInstances['{chart_id}'] = chart;

        console.log('✅ Chart {chart_id} initialized successfully');
      }}

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {{
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {{
          try {{
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#{chart_id}')) {{
              setTimeout(initChart, 100);  // Small delay for slide transition
            }}
          }} catch (e) {{
            console.warn('Chart init on ready failed:', e);
          }}
        }});

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {{
          try {{
            if (event.currentSlide && event.currentSlide.querySelector('#{chart_id}')) {{
              initChart();  // This now destroys old chart and creates new one
            }}
          }} catch (e) {{
            console.warn('Chart init on slide change failed:', e);
          }}
        }});
      }} else {{
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {{
          document.addEventListener('DOMContentLoaded', initChart);
        }} else {{
          initChart();
        }}
      }}
    }})();"""

        # v3.4.11: Build title HTML if chart_title is provided
        # v3.4.14: Phrase subtitle + takeaway format, 20px font, 2-line display
        title_html = ""
        if chart_title:
            title_html = f'''<div class="chart-subtitle" style="height: 70px; padding: 15px 20px; flex-shrink: 0; background: transparent; border: none;">
    <p style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 20px; font-weight: 400; color: var(--text-secondary, #4B5563); text-align: left; line-height: 1.5;">{chart_title}</p>
  </div>'''

        # Basic chart HTML (no editor) - Director L02 spec compliant
        # v3.4.11: Use flexbox for proper title + canvas layout
        chart_html = f"""<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
  {title_html}
  <div style="flex: 1; min-height: 0; position: relative;">
    <canvas id="{chart_id}"></canvas>
  </div>
  <script>
    {inline_script}
  </script>
</div>"""

        # Add interactive editor if requested
        if enable_editor and presentation_id:
            # Use semantic type if provided, otherwise fall back to Chart.js type
            chart_type_for_editor = semantic_chart_type or config.get('type', 'bar')

            chart_html = self._wrap_inline_script_with_editor(
                chart_html,
                chart_id,
                presentation_id,
                api_base_url,
                inline_script,
                chart_type=chart_type_for_editor,  # v3.2.1: Pass chart type for dynamic editor
                chart_title=chart_title  # v3.4.11: Pass chart title for layout alignment
            )

        return chart_html

    def _wrap_with_interactive_editor(
        self,
        canvas_html: str,
        chart_id: str,
        presentation_id: str,
        height: int = 600,
        api_base_url: str = "/api/charts"
    ) -> str:
        """
        Wrap chart canvas with interactive data editor.

        Adds:
        - Edit Data button
        - Modal popup with editable table
        - JavaScript for chart updates
        - API calls to save/load data

        Args:
            canvas_html: Chart canvas HTML
            chart_id: Unique chart identifier
            presentation_id: Presentation UUID
            height: Chart height in pixels (default: 600)
            api_base_url: Base URL for chart API (default: "/api/charts")

        Returns:
            Complete HTML with chart + interactive editor
        """
        # Sanitize chart_id for JavaScript identifiers
        # Replace hyphens, dots, and other invalid chars with underscores
        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

        # Generate unique modal ID for this chart
        modal_id = f"modal-{chart_id}"

        html = f"""
<div class="chart-with-editor" style="position: relative; width: 100%; height: 100%; min-height: {height}px;">
    <!-- Chart Wrapper for proper sizing -->
    <div class="chart-wrapper" style="position: relative; height: calc(100% - 40px); width: 100%; padding-bottom: 40px;">
        {canvas_html}
    </div>

    <!-- Edit Button -->
    <button class="chart-edit-btn"
            onclick="openChartEditor_{js_safe_id}()"
            style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; z-index: 100; transition: all 0.2s;"
            onmouseover="this.style.background='rgba(0,0,0,0.9)'; this.style.transform='scale(1.05)'"
            onmouseout="this.style.background='rgba(0,0,0,0.7)'; this.style.transform='scale(1)'">
        📊 Edit Data
    </button>
</div>

<!-- Modal Popup -->
<div id="{modal_id}" class="chart-editor-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 10000; align-items: center; justify-content: center; backdrop-filter: blur(4px);">
    <div style="background: white; border-radius: 12px; width: 90%; max-width: 800px; max-height: 90vh; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column;">

        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e0e0e0;">
            <h2 style="margin: 0; font-size: 20px; color: #333;">📊 Edit Chart Data</h2>
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: none; border: none; font-size: 32px; color: #666; cursor: pointer; line-height: 1; padding: 0; width: 32px; height: 32px;">&times;</button>
        </div>

        <!-- Body -->
        <div style="padding: 24px; overflow-y: auto; flex: 1;">
            <div style="background: #f5f5f5; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <p style="margin: 4px 0; font-size: 14px;"><strong>Chart ID:</strong> {chart_id}</p>
            </div>

            <div style="overflow-x: auto; margin-bottom: 16px;">
                <table id="table-{chart_id}" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px; width: 50px;">#</th>
                            <th style="background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px;">Label (X-axis)</th>
                            <th style="background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px;">Value (Y-axis)</th>
                            <th style="background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px; width: 80px;">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-{chart_id}"></tbody>
                </table>
            </div>

            <button onclick="addRow_{js_safe_id}()" style="background: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer;">+ Add Row</button>
        </div>

        <!-- Footer -->
        <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid #e0e0e0;">
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer;">Cancel</button>
            <button onclick="saveChartData_{js_safe_id}()" style="background: #4CAF50; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;">💾 Save & Update</button>
        </div>
    </div>
</div>

<!-- JavaScript for Chart Editor -->
<script>
(function() {{
    let currentChart_{js_safe_id} = null;

    function initChart_{js_safe_id}() {{
        const canvas = document.getElementById('{chart_id}');
        if (!canvas) return;

        // DEBUG: Log all container dimensions
        const wrapper = canvas.closest('.chart-wrapper');
        const editor = canvas.closest('.chart-with-editor');
        const parent = editor?.parentElement;

        console.log('🔍 Chart Debug Info for {chart_id}:');
        console.log('  Canvas:', {{
            width: canvas.width,
            height: canvas.height,
            clientWidth: canvas.clientWidth,
            clientHeight: canvas.clientHeight,
            style: canvas.style.cssText
        }});
        console.log('  Wrapper (.chart-wrapper):', {{
            clientWidth: wrapper?.clientWidth,
            clientHeight: wrapper?.clientHeight,
            style: wrapper?.style.cssText
        }});
        console.log('  Editor (.chart-with-editor):', {{
            clientWidth: editor?.clientWidth,
            clientHeight: editor?.clientHeight,
            style: editor?.style.cssText
        }});
        console.log('  Parent Container:', {{
            clientWidth: parent?.clientWidth,
            clientHeight: parent?.clientHeight,
            tagName: parent?.tagName,
            className: parent?.className
        }});

        // Wait for Chart.js to initialize
        setTimeout(() => {{
            currentChart_{js_safe_id} = Chart.getChart(canvas);
            if (!currentChart_{js_safe_id}) {{
                console.warn('Chart not initialized yet for {chart_id}');
            }} else {{
                console.log('✅ Chart initialized:', {{
                    chartWidth: currentChart_{js_safe_id}.width,
                    chartHeight: currentChart_{js_safe_id}.height
                }});
            }}
        }}, 500);
    }}

    window.openChartEditor_{js_safe_id} = function() {{
        if (!currentChart_{js_safe_id}) {{
            currentChart_{js_safe_id} = Chart.getChart(document.getElementById('{chart_id}'));
        }}

        if (!currentChart_{js_safe_id}) {{
            alert('Chart not ready yet. Please wait a moment and try again.');
            return;
        }}

        // Populate table
        const tbody = document.getElementById('tbody-{chart_id}');
        tbody.innerHTML = '';

        const labels = currentChart_{js_safe_id}.data.labels || [];
        const values = currentChart_{js_safe_id}.data.datasets[0]?.data || [];

        labels.forEach((label, index) => {{
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">${{index + 1}}</td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                    <input type="text" class="label-input" value="${{label}}" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
                </td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                    <input type="number" class="value-input" value="${{values[index]}}" step="any" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
                </td>
                <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                    <button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>
                </td>
            `;
            tbody.appendChild(row);
        }});

        // Show modal
        document.getElementById('{modal_id}').style.display = 'flex';
    }};

    window.closeChartEditor_{js_safe_id} = function() {{
        document.getElementById('{modal_id}').style.display = 'none';
    }};

    window.addRow_{js_safe_id} = function() {{
        const tbody = document.getElementById('tbody-{chart_id}');
        const rowCount = tbody.querySelectorAll('tr').length;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">${{rowCount + 1}}</td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                <input type="text" class="label-input" value="" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
            </td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                <input type="number" class="value-input" value="0" step="any" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
            </td>
            <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
                <button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>
            </td>
        `;
        tbody.appendChild(row);
        renumberRows_{js_safe_id}();
    }};

    window.deleteRow_{js_safe_id} = function(btn) {{
        btn.closest('tr').remove();
        renumberRows_{js_safe_id}();
    }};

    function renumberRows_{js_safe_id}() {{
        const rows = document.querySelectorAll('#tbody-{chart_id} tr');
        rows.forEach((row, index) => {{
            row.querySelector('td:first-child').textContent = index + 1;
        }});
    }}

    window.saveChartData_{js_safe_id} = async function() {{
        // Collect data from table
        const rows = document.querySelectorAll('#tbody-{chart_id} tr');
        const newLabels = [];
        const newValues = [];

        rows.forEach(row => {{
            const label = row.querySelector('.label-input').value;
            const value = parseFloat(row.querySelector('.value-input').value);
            newLabels.push(label);
            newValues.push(value);
        }});

        // Update chart in browser
        currentChart_{js_safe_id}.data.labels = newLabels;
        currentChart_{js_safe_id}.data.datasets[0].data = newValues;
        currentChart_{js_safe_id}.update();

        // Save to backend
        try {{
            const response = await fetch('{api_base_url}/update-data', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    chart_id: '{chart_id}',
                    presentation_id: '{presentation_id}',
                    labels: newLabels,
                    values: newValues,
                    timestamp: new Date().toISOString()
                }})
            }});

            const result = await response.json();

            if (result.success) {{
                // Show success message
                const toast = document.createElement('div');
                toast.innerHTML = '✅ Chart updated successfully!';
                toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 14px; font-weight: 500;';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);

                // Close modal
                closeChartEditor_{js_safe_id}();
            }} else {{
                alert('Failed to save: ' + (result.error || 'Unknown error'));
            }}
        }} catch (error) {{
            console.error('Error saving chart data:', error);
            alert('Failed to save chart data. Check console for details.');
        }}
    }};

    // Initialize when DOM ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initChart_{js_safe_id});
    }} else {{
        initChart_{js_safe_id}();
    }}

    // Also try on Reveal.js ready event
    if (typeof Reveal !== 'undefined') {{
        Reveal.on('ready', initChart_{js_safe_id});
    }}
}})();
</script>
"""
        return html

    def _wrap_inline_script_with_editor(
        self,
        chart_html: str,
        chart_id: str,
        presentation_id: str,
        api_base_url: str,
        inline_script: str,
        chart_type: str = "bar",
        chart_title: Optional[str] = None  # v3.4.11: Chart title for layout alignment
    ) -> str:
        """
        Add Excel-like interactive editor to inline-script chart (Layout Builder mode).

        v4.0: Replaced custom HTML editor with professional Excel-like spreadsheet editor.
        Uses chart-spreadsheet-editor.js library for consistent, feature-rich editing.

        Args:
            chart_html: Chart HTML with inline script
            chart_id: Unique chart identifier
            presentation_id: Presentation UUID
            api_base_url: Base URL for chart API
            inline_script: The Chart.js initialization script
            chart_type: Type of chart (bar, scatter, bubble, d3_*, etc.)
            chart_title: Optional title for chart (v3.4.11)

        Returns:
            Chart HTML with Excel-like editor controls
        """
        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

        # Extract service base URL (remove /api/charts suffix for static file serving)
        # api_base_url may be:
        #   - "https://analytics-v30-production.up.railway.app/api/charts" (production)
        #   - "/api/charts" (local dev)
        # We need just the domain part for static files:
        #   - "https://analytics-v30-production.up.railway.app" (production)
        #   - "" (local dev, becomes relative URL)
        service_base_url = api_base_url.replace('/api/charts', '') if '/api/charts' in api_base_url else api_base_url

        # v3.4.11: Build title HTML if chart_title is provided
        # v3.4.14: Phrase subtitle + takeaway format, 20px font, 2-line display
        title_html = ""
        if chart_title:
            title_html = f'''<div class="chart-subtitle" style="height: 70px; padding: 15px 20px; flex-shrink: 0; background: transparent; border: none;">
    <p style="margin: 0; font-family: 'Inter', -apple-system, sans-serif; font-size: 20px; font-weight: 400; color: var(--text-secondary, #4B5563); text-align: left; line-height: 1.5;">{chart_title}</p>
  </div>'''

        # v4.0: Streamlined HTML with Excel editor library
        # v3.4.11: Use flexbox for proper title + canvas layout
        editor_html = f"""<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; box-sizing: border-box; border: none; border-radius: 0; display: flex; flex-direction: column;">
  {title_html}
  <div style="flex: 1; min-height: 0; position: relative;">
    <canvas id="{chart_id}"></canvas>

    <!-- Edit Button (Pencil Icon) - v3.4.11: Moved inside canvas wrapper for proper positioning -->
    <button class="chart-edit-btn"
            onclick="openChartEditor_{js_safe_id}()"
            style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;"
            onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'"
            onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
      ✏️
    </button>
  </div>

  <script>
    {inline_script}
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="{service_base_url}/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {{
      window.openChartEditor_{js_safe_id} = function() {{
        console.log('=== Excel Editor: Opening for chart {chart_id} ===');

        // Get chart instance
        const chart = window.chartInstances?.['{chart_id}'];
        if (!chart) {{
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }}

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', '{chart_type}');

        // Extract current chart data
        const chartData = extractChartData_{js_safe_id}(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {{
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {{
                chartData.datasets.forEach((ds, i) => {{
                    console.log(`  Dataset ${{i}}:`, ds.label, '- data points:', ds.data.length);
                }});
            }}
        }} else if (Array.isArray(chartData)) {{
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {{
                console.log('  First row sample:', chartData[0]);
            }}
        }}
        console.log('Chart type parameter:', '{chart_type}');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            '{chart_id}',
            '{chart_type}',
            chartData,
            {{
                apiEndpoint: '{api_base_url}/update-data',
                onSave: async (newData, chartId) => {{
                    console.log('💾 Saving chart data:', newData);

                    // Transform editor export format to API format
                    function transformToApiFormat(data, chartType) {{
                        console.log('🔄 Transforming data for chart type:', chartType);

                        // Scatter format: [{{x, y, label}}] → {{chart_type: 'scatter', data: [...]}}
                        if (chartType === 'scatter' && Array.isArray(data) && data.length > 0 &&
                            data[0].x !== undefined && data[0].y !== undefined && data[0].r === undefined) {{
                            console.log('✅ Scatter chart format detected - passing through');
                            return {{
                                chart_type: 'scatter',
                                data: data.map(d => ({{
                                    x: parseFloat(d.x),
                                    y: parseFloat(d.y),
                                    label: d.label
                                }}))
                            }};
                        }}

                        // Bubble format: [{{label, x, y, r}}] → {{chart_type: 'bubble', data: [...]}}
                        if (chartType === 'bubble' && Array.isArray(data) && data.length > 0 && data[0].r !== undefined) {{
                            console.log('✅ Bubble chart format detected - passing through');
                            return {{
                                chart_type: 'bubble',
                                data: data.map(d => ({{
                                    x: parseFloat(d.x),
                                    y: parseFloat(d.y),
                                    r: parseFloat(d.r),
                                    label: d.label
                                }}))
                            }};
                        }}

                        // v3.4.33: Waterfall format: [{{label, value: [start, end]}}]
                        // Value is an array representing floating bar positions
                        if (chartType === 'waterfall' && Array.isArray(data) && data.length > 0 &&
                            data[0].value !== undefined && Array.isArray(data[0].value)) {{
                            console.log('✅ Waterfall Start/End format detected');
                            return {{
                                chart_type: chartType,
                                labels: data.map(d => String(d.label).trim()),
                                values: data.map(d => d.value)  // Keep as [start, end] arrays
                            }};
                        }}

                        // Multi-series format: {{labels: [...], datasets: [...]}}
                        if (data && data.labels && data.datasets) {{
                            console.log('✅ Multi-series format detected - adding chart_type');
                            return {{
                                chart_type: chartType,
                                labels: data.labels,
                                datasets: data.datasets
                            }};
                        }}

                        // Simple charts: [{{label, value}}] → {{labels: [...], values: [...]}}
                        // v3.4.31: Fix 422 error - ensure values are numbers, labels are strings
                        if (Array.isArray(data) && data.length > 0 && data[0].label !== undefined && data[0].value !== undefined) {{
                            console.log('✅ Simple chart format detected - converting to labels/values');
                            const labels = data.map(d => String(d.label).trim());
                            const values = data.map(d => {{
                                const num = parseFloat(d.value);
                                return isNaN(num) ? 0 : num;
                            }});
                            console.log('📊 Transformed - labels:', labels.length, 'values:', values.length);
                            return {{
                                chart_type: chartType,
                                labels: labels,
                                values: values
                            }};
                        }}

                        // Fallback: return as-is with chart_type and let API validation handle it
                        console.warn('⚠️ Unknown data format - passing through with chart_type');
                        return {{ chart_type: chartType, data: data }};
                    }}

                    // Save to API FIRST (before updating chart)
                    try {{
                        // Transform data to API-compatible format
                        const apiPayload = transformToApiFormat(newData, '{chart_type}');
                        console.log('📤 Sending to API:', apiPayload);

                        const response = await fetch('{api_base_url}/update-data', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                chart_id: chartId,
                                presentation_id: '{presentation_id}',
                                ...apiPayload,  // Spread transformed data (now in correct format)
                                timestamp: new Date().toISOString()
                            }})
                        }});

                        if (!response.ok) {{
                            const errorData = await response.json().catch(() => ({{}}));
                            // v3.4.31: Better error logging for debugging 422 errors
                            console.error('❌ API Error Response:', errorData);
                            let errorMsg = `API request failed: ${{response.status}}`;
                            if (errorData.detail) {{
                                if (Array.isArray(errorData.detail)) {{
                                    // Pydantic validation errors are arrays
                                    errorMsg = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join('; ');
                                }} else {{
                                    errorMsg = String(errorData.detail);
                                }}
                            }}
                            console.error('❌ Error message:', errorMsg);
                            throw new Error(errorMsg);
                        }}

                        const result = await response.json();
                        console.log('✅ API save successful:', result);

                        // Update chart instance ONLY AFTER successful save
                        // v3.4.23: Fix - get chart from window.chartInstances (chart was undefined)
                        const chartInstance = window.chartInstances[chartId];
                        if (chartInstance) {{
                            updateChartData_{js_safe_id}(chartInstance, newData, '{chart_type}');
                            console.log('✅ Chart visual updated');

                            // v3.4.25: Save to localStorage for persistence across slide navigation
                            // v3.4.30: Fixed key collision - now unique per presentation (presentationId + chartId)
                            // Extract presentation_id from URL: /p/{{presentation_id}}
                            const pathParts = window.location.pathname.split('/');
                            const pIndex = pathParts.indexOf('p');
                            const presentationId = pIndex !== -1 ? pathParts[pIndex + 1] : 'default';
                            const storageKey = 'chartData_' + presentationId + '_' + chartId;
                            localStorage.setItem(storageKey, JSON.stringify(newData));
                            console.log('💾 Chart data saved to localStorage:', storageKey);

                            // v3.4.28: Persist to Layout Service for cross-user persistence
                            // Fixed: Use PUT /slides/{{index}} to update slide.content.chart_html directly
                            // V2-chart-text stores chart in content.chart_html, not in charts[] array
                            (async () => {{
                                try {{
                                    // presentationId already extracted above for localStorage key

                                    // Get slide index from Reveal.js
                                    const slideIndex = typeof Reveal !== 'undefined' ? Reveal.getIndices().h : 0;

                                    // Get updated chart HTML from DOM
                                    const canvasElement = document.getElementById(chartId);
                                    const chartContainer = canvasElement ? canvasElement.closest('.l02-chart-container') : null;

                                    if (presentationId && chartContainer) {{
                                        const updatedHtml = chartContainer.outerHTML;
                                        console.log('📤 Persisting chart to Layout Service (slide ' + slideIndex + ')');

                                        // v3.4.28: PUT to slide content directly (not /charts endpoint)
                                        // V2-chart-text layout stores chart_html in slide.content.chart_html
                                        const layoutResponse = await fetch(
                                            `https://web-production-f0d13.up.railway.app/api/presentations/${{presentationId}}/slides/${{slideIndex}}`,
                                            {{
                                                method: 'PUT',
                                                headers: {{ 'Content-Type': 'application/json' }},
                                                body: JSON.stringify({{ chart_html: updatedHtml }})
                                            }}
                                        );

                                        if (layoutResponse.ok) {{
                                            console.log('✅ Chart persisted to Layout Service');
                                        }} else {{
                                            const errText = await layoutResponse.text();
                                            console.warn('⚠️ Layout Service persistence failed:', layoutResponse.status, errText);
                                        }}
                                    }} else {{
                                        console.log('ℹ️ Skipping Layout Service (preview mode or no container)');
                                    }}
                                }} catch (layoutError) {{
                                    console.warn('⚠️ Layout Service persistence error:', layoutError.message);
                                    // Don't throw - localStorage save already succeeded
                                }}
                            }})();
                        }} else {{
                            console.warn('⚠️ Chart instance not found:', chartId);
                        }}

                    }} catch (error) {{
                        console.error('❌ Error saving chart data:', error);
                        throw error;  // Chart remains unchanged if save fails
                    }}
                }}
            }}
        );
    }};

    // Extract data from chart instance based on chart type
    function extractChartData_{js_safe_id}(chart) {{
        const chartType = chart.config.type;

        if (chartType === 'scatter') {{
            // Scatter: array of {{x, y}}
            return chart.data.datasets[0]?.data || [];
        }} else if (chartType === 'bubble') {{
            // Bubble: array of {{label, x, y, r}}
            return chart.data.datasets[0]?.data || [];
        }} else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {{
            // UNIVERSAL RULE: Use dataset count to determine format
            // - Multiple datasets → Multi-series format (multi-line, grouped bars, stacked areas)
            // - Single dataset → Simple format (single line, pie, radar, etc.)

            if (chart.data.datasets.length > 1) {{
                // Multi-series format
                return {{
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({{
                        label: ds.label,
                        data: ds.data
                    }}))
                }};
            }} else {{
                // Single-series format (works for all: line, bar, radar, pie, doughnut, polar)
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({{ label, value: values[i] }}));
            }}
        }} else {{
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({{ label, value: values[i] }}));
        }}
    }}

    // Update chart instance with new data
    function updateChartData_{js_safe_id}(chart, newData, chartType) {{
        console.log('📝 Updating chart with new data:', newData);

        if (chartType === 'scatter' || chartType === 'bubble') {{
            // Object-based data
            chart.data.datasets[0].data = newData;
        }} else if (newData.labels && newData.datasets) {{
            // Multi-series format - preserve styling while updating data
            chart.data.labels = newData.labels;

            // Preserve existing dataset styling (colors, borders, etc.)
            const oldDatasets = chart.data.datasets.slice();  // Copy existing datasets

            newData.datasets.forEach((newDs, i) => {{
                if (oldDatasets[i]) {{
                    // Update existing dataset, preserve styling
                    chart.data.datasets[i] = {{
                        ...oldDatasets[i],          // Keep all styling properties
                        label: newDs.label,         // Update label
                        data: newDs.data            // Update data
                    }};
                }} else {{
                    // New dataset - add with data from editor
                    // Chart.js will apply default styling on next render
                    chart.data.datasets[i] = {{
                        label: newDs.label,
                        data: newDs.data
                    }};
                }}
            }});

            // Remove extra datasets if user deleted series
            if (chart.data.datasets.length > newData.datasets.length) {{
                chart.data.datasets.length = newData.datasets.length;
            }}

            console.log(`✅ Updated chart with ${{newData.datasets.length}} series`);
        }} else if (Array.isArray(newData)) {{
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);

            // v3.4.33: Waterfall charts use Start/End format with dynamic colors
            if (chartType === 'waterfall') {{
                console.log('🌊 Waterfall chart - using Start/End format');
                const floatingBars = [];
                const newColors = [];

                newData.forEach((d, i) => {{
                    let start, end;
                    if (Array.isArray(d.value)) {{
                        // New format: value is [start, end] array
                        start = d.value[0];
                        end = d.value[1];
                    }} else {{
                        // Legacy fallback: single value treated as end with start=0
                        start = 0;
                        end = parseFloat(d.value) || 0;
                    }}

                    // Floating bar format: [min, max] for Chart.js
                    floatingBars.push([Math.min(start, end), Math.max(start, end)]);

                    // Dynamic colors based on direction
                    const isIncrease = end > start;
                    const isTotal = (i === 0 || i === newData.length - 1) && start === 0;

                    if (isTotal) {{
                        newColors.push('#93C5FD'); // Blue for totals (opening/closing)
                    }} else if (isIncrease) {{
                        newColors.push('#A7F3D0'); // Green for increases
                    }} else {{
                        newColors.push('#FBCFE8'); // Pink for decreases
                    }}
                }});

                console.log('📊 Floating bars:', floatingBars);
                console.log('🎨 Colors:', newColors);
                chart.data.datasets[0].data = floatingBars;
                chart.data.datasets[0].backgroundColor = newColors;
                chart.data.datasets[0].borderColor = newColors;
            }} else {{
                chart.data.datasets[0].data = newData.map(d => d.value);
            }}
        }}

        chart.update();
    }}
  }})();
  </script>
</div>
"""

        return editor_html

    def _wrap_d3_chart_with_editor(
        self,
        d3_html: str,
        chart_id: str,
        chart_type: str,  # 'd3_treemap', 'd3_sunburst', etc.
        data: Union[List[Dict[str, Any]], Dict[str, Any]],  # Current chart data
        presentation_id: str,
        api_base_url: str
    ) -> str:
        """
        Add self-contained editor overlay to D3 charts.
        v3.4.36: Made editor fully self-contained (no external JS dependencies)
        """

        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')
        modal_id = f"d3-editor-modal-{js_safe_id}"

        # Convert data to simple format for editor
        if isinstance(data, list):
            editor_data = data  # Already in correct format
        else:
            # Extract from dict format
            labels = data.get('labels', [])
            values = data.get('values', [])
            editor_data = [{"label": l, "value": v} for l, v in zip(labels, values)]

        wrapped_html = f"""<div style="position: relative;">
  {d3_html}

  <!-- Edit Button -->
  <button class="chart-edit-btn"
          onclick="openD3Editor_{js_safe_id}()"
          style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;"
          onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=\\'margin-left: 6px; font-size: 13px;\\'>edit</span>'; this.style.background='rgba(0,0,0,0.8)'"
          onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <!-- Self-contained D3 Editor Modal (v3.4.37: added pointer-events for interactivity) -->
  <div id="{modal_id}" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.5); z-index: 10000; justify-content: center; align-items: center; pointer-events: auto;">
    <div style="background: white; border-radius: 12px; width: 90%; max-width: 600px; max-height: 80vh; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); pointer-events: auto; position: relative;">
      <!-- Header -->
      <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3 style="margin: 0; font-size: 18px; font-weight: 600;">📊 Edit D3 {chart_type.replace('d3_', '').title()} Data</h3>
          <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">Modify values and save to update the chart</p>
        </div>
        <button onclick="closeD3Editor_{js_safe_id}()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 20px; display: flex; align-items: center; justify-content: center;">&times;</button>
      </div>

      <!-- Table Container -->
      <div style="padding: 20px; max-height: 400px; overflow-y: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <thead>
            <tr style="background: #f8f9fa;">
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6; width: 40px;">#</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6;">Label</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6; width: 120px;">Value</th>
              <th style="padding: 12px; text-align: center; border-bottom: 2px solid #dee2e6; width: 50px;">Del</th>
            </tr>
          </thead>
          <tbody id="d3-tbody-{js_safe_id}"></tbody>
        </table>
      </div>

      <!-- Footer -->
      <div style="padding: 15px 20px; background: #f8f9fa; border-top: 1px solid #dee2e6; display: flex; justify-content: space-between; align-items: center;">
        <button onclick="addD3Row_{js_safe_id}()" style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500;">+ Add Row</button>
        <div>
          <button onclick="closeD3Editor_{js_safe_id}()" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-right: 10px;">Cancel</button>
          <button onclick="saveD3Data_{js_safe_id}()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600;">💾 Save Changes</button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // v3.4.36: Self-contained D3 editor functions
    var d3EditorData_{js_safe_id} = {json.dumps(editor_data)};

    window.openD3Editor_{js_safe_id} = function() {{
      console.log('📊 Opening D3 editor for {chart_id}');

      // Populate table
      const tbody = document.getElementById('d3-tbody-{js_safe_id}');
      tbody.innerHTML = '';

      d3EditorData_{js_safe_id}.forEach((item, index) => {{
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">${{index + 1}}</td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
            <input type="text" class="d3-label-input-{js_safe_id}" value="${{item.label || ''}}" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
          </td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
            <input type="number" class="d3-value-input-{js_safe_id}" value="${{item.value || 0}}" step="any" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
          </td>
          <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
            <button onclick="deleteD3Row_{js_safe_id}(this)" style="background: #dc3545; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>
          </td>
        `;
        tbody.appendChild(row);
      }});

      // Show modal
      document.getElementById('{modal_id}').style.display = 'flex';
    }};

    window.closeD3Editor_{js_safe_id} = function() {{
      document.getElementById('{modal_id}').style.display = 'none';
    }};

    window.addD3Row_{js_safe_id} = function() {{
      const tbody = document.getElementById('d3-tbody-{js_safe_id}');
      const rowCount = tbody.querySelectorAll('tr').length;
      const row = document.createElement('tr');
      row.innerHTML = `
        <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">${{rowCount + 1}}</td>
        <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
          <input type="text" class="d3-label-input-{js_safe_id}" value="" placeholder="New Label" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
        </td>
        <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0;">
          <input type="number" class="d3-value-input-{js_safe_id}" value="0" step="any" style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">
        </td>
        <td style="padding: 8px 12px; border-bottom: 1px solid #e0e0e0; text-align: center;">
          <button onclick="deleteD3Row_{js_safe_id}(this)" style="background: #dc3545; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>
        </td>
      `;
      tbody.appendChild(row);
      renumberD3Rows_{js_safe_id}();
    }};

    window.deleteD3Row_{js_safe_id} = function(btn) {{
      btn.closest('tr').remove();
      renumberD3Rows_{js_safe_id}();
    }};

    function renumberD3Rows_{js_safe_id}() {{
      const rows = document.querySelectorAll('#d3-tbody-{js_safe_id} tr');
      rows.forEach((row, index) => {{
        row.querySelector('td:first-child').textContent = index + 1;
      }});
    }}

    window.saveD3Data_{js_safe_id} = async function() {{
      // Collect data from table
      const labels = document.querySelectorAll('.d3-label-input-{js_safe_id}');
      const values = document.querySelectorAll('.d3-value-input-{js_safe_id}');

      const newData = [];
      labels.forEach((labelInput, i) => {{
        newData.push({{
          label: labelInput.value,
          value: parseFloat(values[i].value) || 0
        }});
      }});

      console.log('💾 Saving D3 chart data:', newData);

      // Save to backend API
      try {{
        const response = await fetch('{api_base_url}/update-data', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            chart_id: '{chart_id}',
            presentation_id: '{presentation_id}',
            labels: newData.map(d => d.label),
            values: newData.map(d => d.value),
            chart_type: '{chart_type}',
            timestamp: Date.now()
          }})
        }});

        if (!response.ok) {{
          const errorData = await response.json().catch(() => ({{}}));
          throw new Error(errorData.detail || 'Save failed');
        }}

        const result = await response.json();
        console.log('✅ Save result:', result);

        // Update local data
        d3EditorData_{js_safe_id} = newData;

        // Close modal and show success
        closeD3Editor_{js_safe_id}();

        // Show toast notification
        const toast = document.createElement('div');
        toast.innerHTML = '✅ Chart data saved! Refresh page to see D3 chart updates.';
        toast.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 24px; border-radius: 8px; z-index: 10001; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);

      }} catch (error) {{
        console.error('❌ Error saving D3 chart data:', error);
        alert('❌ Failed to save: ' + error.message);
      }}
    }};
  </script>
</div>"""

        return wrapped_html

    def _build_chart_options(
        self,
        format_type: str,
        chart_type: str,
        custom_options: Optional[Dict[str, Any]] = None,
        horizontal: bool = False,
        dataset_count: int = 1
    ) -> dict:
        """
        Build Chart.js options with GUARANTEED visible axes, labels, and formatters.

        ENFORCED SETTINGS (cannot be disabled):
        - Axes always visible with labels and units
        - Data labels always shown on all points/bars
        - Grid lines always displayed
        - Formatters always applied (currency/percentage/number)
        - Scales always begin at zero where appropriate

        Args:
            format_type: "currency", "percentage", or "number"
            chart_type: Type of chart ("line", "bar", etc.)
            custom_options: Custom options to merge
            horizontal: For horizontal bar charts
            dataset_count: Number of datasets (for legend display logic)

        Returns:
            Complete options dictionary with guaranteed visibility
        """
        # v3.3.0: Hide legend for single-dataset charts, show for multiple datasets
        show_legend = dataset_count > 1 or chart_type in ["pie", "doughnut", "polarArea"]

        options = {
            "responsive": True,
            "maintainAspectRatio": False,
            # v3.4.5: Add layout padding to prevent axis label cutoff
            "layout": {
                "padding": {
                    "left": 15,
                    "right": 25,
                    "top": 15,
                    "bottom": 40  # Extra space for rotated X-axis labels
                }
            },
            "animation": {
                "duration": 1500,  # 1.5 seconds for smooth animation
                "easing": "easeInOutQuart",  # Smooth acceleration/deceleration
                "delay": 0,
                "loop": False,
                "animateRotate": True,  # For pie/doughnut charts
                "animateScale": True    # For radar charts
            },
            "plugins": {
                "legend": {
                    "display": show_legend,  # v3.3.0: Only show for multiple datasets
                    "position": "top",
                    "labels": {
                        "font": {"size": 14, "weight": "bold"},
                        "padding": 15,
                        "usePointStyle": True,
                        "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                    }
                },
                "datalabels": {
                    # GUARANTEED: Always display data labels
                    "display": True,
                    "color": "#fff",
                    "font": {"size": 14, "weight": "bold"},
                    "formatter": self._get_datalabel_formatter(format_type),
                    "anchor": "end" if chart_type in ["line", "bar"] else "center",
                    "align": "top" if chart_type == "line" else ("end" if chart_type == "bar" else "center"),
                    "offset": 4 if chart_type == "line" else 0,
                    # Add background for better readability
                    "backgroundColor": "rgba(0, 0, 0, 0.7)",
                    "borderRadius": 4,
                    "padding": 6
                },
                "tooltip": {
                    "enabled": True,
                    "mode": "nearest",
                    "intersect": True
                    # v3.3.0: Bubble charts will get custom callbacks added via custom_options
                }
            }
        }

        # Add scales for charts that support them
        if chart_type in ["line", "bar", "scatter", "bubble", "mixed"]:
            x_axis = "y" if horizontal else "x"
            y_axis = "x" if horizontal else "y"

            options["scales"] = {
                x_axis: {
                    # GUARANTEED: Always display X-axis
                    "display": True,
                    "grid": {
                        "display": True,  # Always show grid
                        "color": "rgba(107, 114, 128, 0.15)",  # v3.4.18: gray-500 at 15% opacity
                        "lineWidth": 1
                    },
                    "ticks": {
                        "display": True,  # Always show labels
                        "font": {"size": 12, "weight": "500"},
                        "color": "#6b7280",  # v3.4.7: Subtle gray (Tailwind gray-500)
                        "padding": 8,
                        "autoSkip": False,  # Show all labels
                        "maxRotation": 45,
                        "minRotation": 0
                    },
                    "title": {
                        "display": True,
                        "text": "",  # Will be set per chart if needed
                        "font": {"size": 13, "weight": "bold"},
                        "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                    }
                },
                y_axis: {
                    # GUARANTEED: Always display Y-axis
                    "display": True,
                    "beginAtZero": True,  # Always start at zero
                    "grace": "15%",  # v3.4.5: Add 15% headroom above max value for data labels
                    "grid": {
                        "display": True,  # Always show grid
                        "color": "rgba(107, 114, 128, 0.15)",  # v3.4.18: gray-500 at 15% opacity
                        "lineWidth": 1
                    },
                    "ticks": {
                        "display": True,  # Always show labels
                        "font": {"size": 12, "weight": "500"},
                        "color": "#6b7280",  # v3.4.7: Subtle gray (Tailwind gray-500)
                        "padding": 8,
                        **self._get_tick_config(format_type)
                    },
                    "title": {
                        "display": True,
                        "text": self._get_axis_title(format_type),  # Auto-set based on format
                        "font": {"size": 13, "weight": "bold"},
                        "color": "#6b7280"  # v3.4.15: Standardized gray-500 for all text
                    }
                }
            }

            # Horizontal bar charts - swap axis formatting
            if horizontal and chart_type == "bar":
                options["indexAxis"] = "y"
                # Move tick formatting to x-axis for horizontal bars (value axis)
                options["scales"]["x"]["ticks"].update(self._get_tick_config(format_type))
                options["scales"]["x"]["title"]["text"] = self._get_axis_title(format_type)
                options["scales"]["x"]["grace"] = "15%"  # v3.4.5: Headroom for data labels
                # Remove tick config and grace from y-axis (category axis)
                options["scales"]["y"]["ticks"] = {
                    "display": True,
                    "font": {"size": 12, "weight": "500"},
                    "color": "#6b7280",  # v3.4.15: Standardized gray-500 for all text
                    "padding": 8,
                    "autoSkip": False
                }
                options["scales"]["y"]["title"]["text"] = ""
                options["scales"]["y"].pop("grace", None)  # Remove grace from category axis

        # Merge custom options (but enforce critical settings)
        if custom_options:
            options = self._merge_options(options, custom_options)

            # ENFORCE: Re-apply critical settings that must not be disabled
            # v3.2.0: EXCEPTION - Allow scatter/bubble to disable datalabels (prevents [object Object])
            if "plugins" in options and "datalabels" in options["plugins"]:
                if chart_type not in ["scatter", "bubble"]:
                    options["plugins"]["datalabels"]["display"] = True
            if "scales" in options:
                for axis in options["scales"]:
                    options["scales"][axis]["display"] = True
                    options["scales"][axis]["ticks"]["display"] = True

        return options

    def _get_axis_title(self, format_type: str) -> str:
        """
        Get axis title based on format type.

        Returns appropriate unit labels for Y-axis.
        """
        if format_type == "currency":
            return "Amount (USD)"
        elif format_type == "percentage":
            return "Percentage (%)"
        else:
            return "Value"

    def _get_tick_config(self, format_type: str) -> dict:
        """
        Get tick configuration for axis formatting.

        GUARANTEED: Always returns formatter callback.
        """
        if format_type == "currency":
            return {
                "callback": "function(value) { return '$' + (value/1000).toFixed(0) + 'K'; }"
            }
        elif format_type == "percentage":
            return {
                "callback": "function(value) { return value.toFixed(1) + '%'; }"
            }
        else:
            return {
                "callback": "function(value) { return value.toLocaleString(); }"
            }

    def _get_datalabel_formatter(self, format_type: str) -> str:
        """
        Get data label formatter function as string.

        GUARANTEED: Always returns a formatter that displays values.
        These labels will appear directly on chart points/bars/segments.
        """
        if format_type == "currency":
            # Display as $XXXk (e.g., $125K, $1.5M)
            return """function(value) {
                if (value >= 1000000) {
                    return '$' + (value/1000000).toFixed(1) + 'M';
                } else if (value >= 1000) {
                    return '$' + (value/1000).toFixed(0) + 'K';
                } else {
                    return '$' + value.toFixed(0);
                }
            }"""
        elif format_type == "percentage":
            # Display as XX.X% (e.g., 45.5%)
            return "function(value) { return value.toFixed(1) + '%'; }"
        else:
            # Display as formatted number (e.g., 1,234)
            return "function(value) { return value.toLocaleString(); }"

    def _prepare_datasets(
        self,
        datasets: List[Dict[str, Any]],
        chart_type: str,
        format_type: str,
        horizontal: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Prepare datasets with colors and styling.

        Args:
            datasets: Raw dataset definitions
            chart_type: Type of chart
            format_type: Formatter type
            horizontal: For horizontal charts

        Returns:
            Prepared datasets with styling
        """
        prepared = []

        for idx, ds in enumerate(datasets):
            color = self.palette[idx % len(self.palette)]

            # v3.1.9: Fix transparency for scatter/bubble visibility
            if chart_type == "scatter":
                bg_color = color  # Opaque for scatter points
            elif chart_type == "bubble":
                bg_color = self._hex_to_rgba(color, 0.7)  # 70% opacity for bubbles
            elif chart_type == "bar":
                bg_color = color
            else:
                bg_color = self._hex_to_rgba(color, 0.2)

            prepared_ds = {
                "label": ds.get("label", f"Series {idx+1}"),
                "data": ds.get("data", []),
                "backgroundColor": bg_color,
                "borderColor": color,
                "borderWidth": 3 if chart_type == "line" else 2
            }

            # Chart-specific styling
            if chart_type == "line":
                prepared_ds.update({
                    "fill": ds.get("fill", True),
                    "tension": 0.4,
                    "pointRadius": 6,
                    "pointBackgroundColor": color,
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 3
                })
            elif chart_type == "bar":
                prepared_ds.update({
                    "borderRadius": 10
                })
            elif chart_type in ["scatter", "bubble"]:
                prepared_ds.update({
                    "pointStyle": "circle",  # v3.3.0: Circle for both scatter and bubble (better visibility)
                    "pointRadius": 8 if chart_type == "scatter" else None,  # v3.3.0: Reduced from 10 to 8 for circles
                    "pointBackgroundColor": color,
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 2
                })
            elif chart_type == "radar":
                prepared_ds.update({
                    "fill": True,
                    "backgroundColor": self._hex_to_rgba(color, 0.2),
                    "pointRadius": 4,
                    "pointBackgroundColor": color
                })

            prepared.append(prepared_ds)

        return prepared

    def generate_d3_treemap_chart(
        self,
        data: Dict[str, Any],
        height: int = 720,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate D3.js treemap chart using D3.js v7.

        This provides SVG-based hierarchical visualization as an advanced alternative
        visualizations. Uses D3.js v7 for full control over treemap rendering.

        Args:
            data: Chart data with labels and values:
                  {"labels": ["Cat1", "Cat2"], "values": [100, 200]}
            height: Chart height in pixels (default: 720)
            chart_id: Unique chart ID
            options: Custom D3 options (reserved for future use)
            enable_editor: Editor support (not yet implemented for D3 charts)
            presentation_id: For future editor integration
            api_base_url: API endpoint base
            output_mode: Always "inline_script" for D3 charts

        Returns:
            HTML with D3 treemap SVG and embedded D3.js library
        """
        # Extract chart data from array format if needed (v3.4.3 fix)
        # Support both formats:
        # 1. Array of objects: [{"label": "A", "value": 100}, ...]
        # 2. Structured object: {"labels": [...], "values": [...]}
        if isinstance(data, list):
            # Format 1: Array of label-value objects
            labels = [item.get("label", "") for item in data]
            values = [item.get("value", 0) for item in data]
        else:
            # Format 2: Structured object
            labels = data.get("labels", [])
            values = data.get("values", [])

        if not labels or not values:
            return "<div style='color: red; padding: 20px;'>Error: D3 treemap requires labels and values</div>"

        # Transform to D3 hierarchical format
        hierarchical_data = {
            "name": "root",
            "children": [
                {"name": str(label), "value": float(value)}
                for label, value in zip(labels, values)
            ]
        }

        # Get theme colors
        colors = self.palette

        # Safe chart ID
        chart_id_safe = chart_id or f"d3-treemap-{id(data)}"

        # Dimensions - v3.4.35: Reduced width to fit V2-chart-text layout with Key Insights panel
        container_width = 850  # Fits alongside ~400px Key Insights panel
        container_height = height
        svg_width = container_width - 40  # Account for padding
        svg_height = container_height - 60  # Leave room for potential title

        # Build D3 treemap HTML
        d3_html = f"""<!-- D3.js Treemap Chart -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

<div class="l02-chart-container" style="width: {container_width}px; height: {container_height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; overflow: hidden;">
    <div id="{chart_id_safe}" style="padding: 10px;"></div>
    <script>
        (function() {{
            function initD3Treemap() {{
                // Data
                const data = {json.dumps(hierarchical_data)};
                const colors = {json.dumps(colors)};

                // Dimensions
                const width = {svg_width};
                const height = {svg_height};

                // Create treemap layout
                const treemap = d3.treemap()
                    .size([width, height])
                    .padding(2)
                    .round(true);

                // Create hierarchy and sum values
                const root = d3.hierarchy(data)
                    .sum(d => d.value)
                    .sort((a, b) => b.value - a.value);

                // Generate treemap layout
                treemap(root);

                // Clear existing SVG (for Reveal.js re-rendering)
                d3.select('#{chart_id_safe}').selectAll('*').remove();

                // Create SVG
                const svg = d3.select('#{chart_id_safe}')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height)
                    .style('font', '14px Arial, sans-serif');

                // Create cells
                const cell = svg.selectAll('g')
                    .data(root.leaves())
                    .enter().append('g')
                    .attr('transform', d => `translate(${{d.x0}},${{d.y0}})`);

                // Add rectangles
                cell.append('rect')
                    .attr('width', d => d.x1 - d.x0)
                    .attr('height', d => d.y1 - d.y0)
                    .attr('fill', (d, i) => colors[i % colors.length])
                    .attr('fill-opacity', 0.85)
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 2)
                    .attr('rx', 3)
                    .attr('ry', 3)
                    .on('mouseover', function(event, d) {{
                        d3.select(this).attr('fill-opacity', 1);
                    }})
                    .on('mouseout', function(event, d) {{
                        d3.select(this).attr('fill-opacity', 0.85);
                    }});

                // Add labels (only if cell is large enough)
                cell.filter(d => (d.x1 - d.x0) > 60 && (d.y1 - d.y0) > 40)
                    .append('text')
                    .attr('x', 5)
                    .attr('y', 20)
                    .text(d => d.data.name)
                    .attr('fill', '#fff')
                    .attr('font-size', '14px')
                    .attr('font-weight', 'bold')
                    .style('pointer-events', 'none');

                // Add value labels (only if cell is large enough)
                cell.filter(d => (d.x1 - d.x0) > 60 && (d.y1 - d.y0) > 60)
                    .append('text')
                    .attr('x', 5)
                    .attr('y', 40)
                    .text(d => d.value.toLocaleString())
                    .attr('fill', '#fff')
                    .attr('font-size', '12px')
                    .style('pointer-events', 'none');

                // Store chart instance
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = {{
                    type: 'd3_treemap',
                    data: data,
                    destroy: function() {{
                        d3.select('#{chart_id_safe}').selectAll('*').remove();
                    }}
                }};

                console.log('✅ D3 Treemap {chart_id_safe} initialized');
            }}

            // v3.4.37: Improved initialization for first-load rendering
            // Reveal.js-aware initialization with fallback for cases where 'ready' has already fired
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('ready', function() {{
                    try {{
                        const currentSlide = Reveal.getCurrentSlide();
                        if (currentSlide && currentSlide.querySelector('#{chart_id_safe}')) {{
                            setTimeout(initD3Treemap, 300);  // Increased from 100ms
                        }}
                    }} catch (e) {{
                        console.warn('D3 treemap init on ready failed:', e);
                    }}
                }});

                Reveal.on('slidechanged', function(event) {{
                    try {{
                        if (event.currentSlide && event.currentSlide.querySelector('#{chart_id_safe}')) {{
                            initD3Treemap();
                        }}
                    }} catch (e) {{
                        console.warn('D3 treemap init on slide change failed:', e);
                    }}
                }});

                // v3.4.37: Fallback for cases where Reveal 'ready' already fired before script loaded
                // This handles first-load rendering when the script executes after Reveal is ready
                setTimeout(function() {{
                    const container = document.getElementById('{chart_id_safe}');
                    if (container && !container.querySelector('svg')) {{
                        console.log('D3 Treemap fallback init - Reveal ready may have already fired');
                        initD3Treemap();
                    }}
                }}, 500);
            }} else {{
                // Standalone mode (no Reveal.js)
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initD3Treemap);
                }} else {{
                    initD3Treemap();
                }}
            }}
        }})();
    </script>
</div>"""

        # Add editor overlay if enabled
        if enable_editor and presentation_id:
            d3_html = self._wrap_d3_chart_with_editor(
                d3_html=d3_html,
                chart_id=chart_id_safe,
                chart_type='d3_treemap',
                data={'labels': labels, 'values': values},
                presentation_id=presentation_id,
                api_base_url=api_base_url
            )

        return d3_html

    def generate_d3_sunburst_chart(
        self,
        data: Dict[str, Any],
        height: int = 720,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate D3.js sunburst chart for multi-level hierarchical data.

        Sunburst diagram displays hierarchical data as concentric circles,
        with each ring representing a level in the hierarchy. Perfect for
        budget breakdowns, organizational structures, file system usage.

        Args:
            data: Chart data with labels and values:
                  {"labels": ["Cat1", "Cat2"], "values": [100, 200]}
                  Or hierarchical: {"name": "root", "children": [...]}
            height: Chart height in pixels (default: 720)
            chart_id: Unique chart ID
            options: Custom D3 options (reserved for future use)
            enable_editor: Editor support (not yet implemented for D3 charts)
            presentation_id: For future editor integration
            api_base_url: API endpoint base
            output_mode: Always "inline_script" for D3 charts

        Returns:
            HTML with D3 sunburst SVG and embedded D3.js library
        """
        # Extract chart data from array format if needed (v3.4.3 fix)
        # Support both formats:
        # 1. Array of objects: [{"label": "A", "value": 100}, ...]
        # 2. Structured object: {"labels": [...], "values": [...]}
        if isinstance(data, list):
            # Format 1: Array of label-value objects
            labels = [item.get("label", "") for item in data]
            values = [item.get("value", 0) for item in data]
        else:
            # Format 2: Structured object
            labels = data.get("labels", [])
            values = data.get("values", [])

        if not labels or not values:
            return "<div style='color: red; padding: 20px;'>Error: D3 sunburst requires labels and values</div>"

        # Transform to D3 hierarchical format
        hierarchical_data = {
            "name": "root",
            "children": [
                {"name": str(label), "value": float(value)}
                for label, value in zip(labels, values)
            ]
        }

        # Get theme colors
        colors = self.palette

        # Safe chart ID
        chart_id_safe = chart_id or f"d3-sunburst-{id(data)}"

        # Dimensions (square for radial layout) - v3.4.35: Reduced width for V2 layout
        container_width = 850  # Fits alongside ~400px Key Insights panel
        container_height = height
        size = min(container_width - 40, container_height - 40)
        radius = size / 2

        # Build D3 sunburst HTML
        d3_html = f"""<!-- D3.js Sunburst Chart -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

<div class="l02-chart-container" style="width: {container_width}px; height: {container_height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; overflow: hidden;">
    <div id="{chart_id_safe}" style="display: flex; justify-content: center; padding: 10px;"></div>
    <script>
        (function() {{
            function initD3Sunburst() {{
                // Data
                const data = {json.dumps(hierarchical_data)};
                const colors = {json.dumps(colors)};

                // Dimensions
                const width = {size};
                const height = {size};
                const radius = {radius};

                // Create partition layout
                const partition = d3.partition()
                    .size([2 * Math.PI, radius]);

                // Create hierarchy and sum values
                const root = d3.hierarchy(data)
                    .sum(d => d.value)
                    .sort((a, b) => b.value - a.value);

                // Generate partition layout
                partition(root);

                // Arc generator
                const arc = d3.arc()
                    .startAngle(d => d.x0)
                    .endAngle(d => d.x1)
                    .innerRadius(d => d.y0)
                    .outerRadius(d => d.y1);

                // Clear existing SVG (for Reveal.js re-rendering)
                d3.select('#{chart_id_safe}').selectAll('*').remove();

                // Create SVG
                const svg = d3.select('#{chart_id_safe}')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height)
                    .style('font', '12px Arial, sans-serif');

                // Create group and center it
                const g = svg.append('g')
                    .attr('transform', `translate(${{width / 2}},${{height / 2}})`);

                // Create arcs
                const path = g.selectAll('path')
                    .data(root.descendants().filter(d => d.depth))
                    .enter().append('path')
                    .attr('d', arc)
                    .attr('fill', (d, i) => colors[i % colors.length])
                    .attr('fill-opacity', 0.85)
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 2)
                    .on('mouseover', function(event, d) {{
                        d3.select(this).attr('fill-opacity', 1);
                    }})
                    .on('mouseout', function(event, d) {{
                        d3.select(this).attr('fill-opacity', 0.85);
                    }});

                // Add labels (only for larger arcs)
                g.selectAll('text')
                    .data(root.descendants().filter(d => d.depth && (d.x1 - d.x0) > 0.1))
                    .enter().append('text')
                    .attr('transform', function(d) {{
                        const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
                        const y = (d.y0 + d.y1) / 2;
                        return `rotate(${{x - 90}}) translate(${{y}},0) rotate(${{x < 180 ? 0 : 180}})`;
                    }})
                    .attr('dy', '0.35em')
                    .attr('text-anchor', 'middle')
                    .text(d => d.data.name)
                    .attr('fill', '#fff')
                    .attr('font-size', '11px')
                    .attr('font-weight', 'bold')
                    .style('pointer-events', 'none');

                // Store chart instance
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = {{
                    type: 'd3_sunburst',
                    data: data,
                    destroy: function() {{
                        d3.select('#{chart_id_safe}').selectAll('*').remove();
                    }}
                }};

                console.log('✅ D3 Sunburst {chart_id_safe} initialized');
            }}

            // Reveal.js-aware initialization (matches Chart.js pattern)
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('ready', function() {{
                    try {{
                        const currentSlide = Reveal.getCurrentSlide();
                        if (currentSlide && currentSlide.querySelector('#{chart_id_safe}')) {{
                            setTimeout(initD3Sunburst, 100);
                        }}
                    }} catch (e) {{
                        console.warn('D3 sunburst init on ready failed:', e);
                    }}
                }});

                Reveal.on('slidechanged', function(event) {{
                    try {{
                        if (event.currentSlide && event.currentSlide.querySelector('#{chart_id_safe}')) {{
                            initD3Sunburst();
                        }}
                    }} catch (e) {{
                        console.warn('D3 sunburst init on slide change failed:', e);
                    }}
                }});
            }} else {{
                // Standalone mode (no Reveal.js)
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initD3Sunburst);
                }} else {{
                    initD3Sunburst();
                }}
            }}
        }})();
    </script>
</div>"""

        # Add editor overlay if enabled
        if enable_editor and presentation_id:
            d3_html = self._wrap_d3_chart_with_editor(
                d3_html=d3_html,
                chart_id=chart_id_safe,
                chart_type='d3_sunburst',
                data={'labels': labels, 'values': values},
                presentation_id=presentation_id,
                api_base_url=api_base_url
            )

        return d3_html

    def generate_d3_choropleth_usa_chart(
        self,
        data: Dict[str, Any],
        height: int = 720,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate D3.js choropleth map of USA states using D3.js v7.

        Choropleth (color-coded) map visualization showing geographic data
        distribution across US states. Each state is colored based on its
        data value, creating an intuitive geographic heat map. Perfect for
        regional sales, market penetration, and state-by-state metrics.

        Args:
            data: Chart data with labels (state names) and values:
                  {"labels": ["California", "Texas", ...], "values": [450000, 380000, ...]}
                  Supports full names, abbreviations, or mixed formats
            height: Chart height in pixels (default: 720)
            chart_id: Unique chart ID
            options: Custom D3 options (reserved for future use)
            enable_editor: Editor support (not yet implemented for D3 charts)
            presentation_id: For future editor integration
            api_base_url: API endpoint base
            output_mode: Always "inline_script" for D3 charts

        Returns:
            HTML with D3 choropleth map SVG and embedded D3.js library
        """
        # Extract labels and values
        labels = data.get("labels", [])
        values = data.get("values", [])

        if not labels or not values:
            return "<div style='color: red; padding: 20px;'>Error: D3 choropleth requires labels (state names) and values</div>"

        # State name aliases (support both full names and abbreviations)
        STATE_ALIASES = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming'
        }

        # Create reverse mapping (full name -> abbreviation)
        STATE_NAMES_TO_ABBR = {v: k for k, v in STATE_ALIASES.items()}

        # Normalize state names and create data map
        state_data_map = {}
        for label, value in zip(labels, values):
            label_str = str(label).strip()
            # Check if it's an abbreviation
            if label_str.upper() in STATE_ALIASES:
                full_name = STATE_ALIASES[label_str.upper()]
                state_data_map[full_name] = float(value)
            # Check if it's a full name
            elif label_str in STATE_NAMES_TO_ABBR:
                state_data_map[label_str] = float(value)
            # Try case-insensitive match
            else:
                for abbr, name in STATE_ALIASES.items():
                    if name.lower() == label_str.lower():
                        state_data_map[name] = float(value)
                        break

        # Get theme colors
        colors = self.palette

        # Safe chart ID
        chart_id_safe = chart_id or f"d3-choropleth-{id(data)}"

        # Dimensions - v3.4.35: Reduced width to fit V2-chart-text layout with Key Insights panel
        container_width = 850  # Fits alongside ~400px Key Insights panel
        container_height = height
        map_width = container_width - 80  # Leave room for legend
        map_height = container_height - 40

        # Calculate value domain for color scale
        if values:
            min_val = min(values)
            max_val = max(values)
        else:
            min_val = 0
            max_val = 100

        # Build D3 choropleth HTML
        d3_html = f"""<!-- D3.js Choropleth USA Map -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>

<div class="l02-chart-container" style="width: {container_width}px; height: {container_height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; overflow: hidden;">
    <div id="{chart_id_safe}" style="padding: 10px;"></div>
    <script>
        (function() {{
            function initD3Choropleth() {{
                // Data map
                const stateData = {json.dumps(state_data_map)};
                const colors = {json.dumps(colors)};

                // Dimensions
                const width = {map_width};
                const height = {map_height};

                // Value domain
                const minValue = {min_val};
                const maxValue = {max_val};

                // Color scale - use quantize for discrete color bins
                const colorScale = d3.scaleQuantize()
                    .domain([minValue, maxValue])
                    .range(colors);

                // Clear existing SVG (for Reveal.js re-rendering)
                d3.select('#{chart_id_safe}').selectAll('*').remove();

                // Create SVG
                const svg = d3.select('#{chart_id_safe}')
                    .append('svg')
                    .attr('width', width + 100)  // Extra space for legend
                    .attr('height', height)
                    .style('font', '12px Arial, sans-serif');

                // Create map group
                const mapGroup = svg.append('g')
                    .attr('transform', 'translate(0, 0)');

                // Projection for USA
                const projection = d3.geoAlbersUsa()
                    .scale(width * 1.3)
                    .translate([width / 2, height / 2]);

                const path = d3.geoPath().projection(projection);

                // Tooltip
                const tooltip = d3.select('#{chart_id_safe}')
                    .append('div')
                    .style('position', 'absolute')
                    .style('background', 'rgba(0, 0, 0, 0.8)')
                    .style('color', 'white')
                    .style('padding', '8px 12px')
                    .style('border-radius', '4px')
                    .style('font-size', '13px')
                    .style('pointer-events', 'none')
                    .style('opacity', 0)
                    .style('z-index', 1000);

                // Load TopoJSON for US states
                d3.json('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json')
                    .then(function(us) {{
                        // Convert TopoJSON to GeoJSON
                        const states = topojson.feature(us, us.objects.states);

                        // Draw states
                        mapGroup.selectAll('path')
                            .data(states.features)
                            .enter().append('path')
                            .attr('d', path)
                            .attr('fill', function(d) {{
                                const stateName = d.properties.name;
                                const value = stateData[stateName];
                                return value !== undefined ? colorScale(value) : '#e0e0e0';
                            }})
                            .attr('stroke', '#fff')
                            .attr('stroke-width', 1)
                            .style('cursor', 'pointer')
                            .on('mouseover', function(event, d) {{
                                const stateName = d.properties.name;
                                const value = stateData[stateName];

                                // Highlight state
                                d3.select(this)
                                    .attr('stroke', '#333')
                                    .attr('stroke-width', 2);

                                // Show tooltip
                                if (value !== undefined) {{
                                    tooltip
                                        .style('opacity', 1)
                                        .html(`<strong>${{stateName}}</strong><br/>Value: ${{value.toLocaleString()}}`);
                                }}
                            }})
                            .on('mousemove', function(event) {{
                                tooltip
                                    .style('left', (event.pageX + 10) + 'px')
                                    .style('top', (event.pageY - 30) + 'px');
                            }})
                            .on('mouseout', function() {{
                                d3.select(this)
                                    .attr('stroke', '#fff')
                                    .attr('stroke-width', 1);
                                tooltip.style('opacity', 0);
                            }});

                        // Add legend
                        const legendWidth = 20;
                        const legendHeight = 200;
                        const legendX = width + 20;
                        const legendY = 50;

                        const legendScale = d3.scaleLinear()
                            .domain([minValue, maxValue])
                            .range([legendHeight, 0]);

                        const legendAxis = d3.axisRight(legendScale)
                            .ticks(5)
                            .tickFormat(d => d >= 1000 ? (d / 1000).toFixed(0) + 'K' : d);

                        // Create gradient for legend
                        const defs = svg.append('defs');
                        const linearGradient = defs.append('linearGradient')
                            .attr('id', 'legend-gradient-{chart_id_safe}')
                            .attr('x1', '0%')
                            .attr('y1', '100%')
                            .attr('x2', '0%')
                            .attr('y2', '0%');

                        // Add color stops
                        colors.forEach((color, i) => {{
                            linearGradient.append('stop')
                                .attr('offset', `${{(i / (colors.length - 1)) * 100}}%`)
                                .attr('stop-color', color);
                        }});

                        // Legend rectangle
                        svg.append('rect')
                            .attr('x', legendX)
                            .attr('y', legendY)
                            .attr('width', legendWidth)
                            .attr('height', legendHeight)
                            .style('fill', 'url(#legend-gradient-{chart_id_safe})');

                        // Legend axis
                        svg.append('g')
                            .attr('transform', `translate(${{legendX + legendWidth}}, ${{legendY}})`)
                            .call(legendAxis)
                            .style('font-size', '11px');

                        console.log('✅ D3 Choropleth {chart_id_safe} initialized');
                    }})
                    .catch(function(error) {{
                        console.error('Error loading TopoJSON:', error);
                        d3.select('#{chart_id_safe}')
                            .append('div')
                            .style('color', 'red')
                            .style('padding', '20px')
                            .text('Error loading USA map data');
                    }});

                // Store chart instance
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = {{
                    type: 'd3_choropleth_usa',
                    data: stateData,
                    destroy: function() {{
                        d3.select('#{chart_id_safe}').selectAll('*').remove();
                    }}
                }};
            }}

            // Reveal.js-aware initialization (matches Chart.js pattern)
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('ready', function() {{
                    try {{
                        const currentSlide = Reveal.getCurrentSlide();
                        if (currentSlide && currentSlide.querySelector('#{chart_id_safe}')) {{
                            setTimeout(initD3Choropleth, 100);
                        }}
                    }} catch (e) {{
                        console.warn('D3 choropleth init on ready failed:', e);
                    }}
                }});

                Reveal.on('slidechanged', function(event) {{
                    try {{
                        if (event.currentSlide && event.currentSlide.querySelector('#{chart_id_safe}')) {{
                            initD3Choropleth();
                        }}
                    }} catch (e) {{
                        console.warn('D3 choropleth init on slide change failed:', e);
                    }}
                }});
            }} else {{
                // Standalone mode (no Reveal.js)
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initD3Choropleth);
                }} else {{
                    initD3Choropleth();
                }}
            }}
        }})();
    </script>
</div>"""

        # Add editor overlay if enabled
        if enable_editor and presentation_id:
            d3_html = self._wrap_d3_chart_with_editor(
                d3_html=d3_html,
                chart_id=chart_id_safe,
                chart_type='d3_choropleth_usa',
                data={'labels': labels, 'values': values},
                presentation_id=presentation_id,
                api_base_url=api_base_url
            )

        return d3_html

    def generate_d3_sankey_chart(
        self,
        data: Dict[str, Any],
        height: int = 720,
        chart_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        enable_editor: bool = False,
        presentation_id: Optional[str] = None,
        api_base_url: str = "/api/charts",
        output_mode: str = "inline_script",
        chart_title: Optional[str] = None  # v3.4.11
    ) -> str:
        """
        Generate D3.js Sankey diagram using D3.js v7.

        Sankey diagram for visualizing flows between nodes (e.g., budget allocation,
        process workflows, energy transfers, customer journey).

        Data format: Simple label-value pairs converted to source→target flows
        Input: [{"label": "Source → Target", "value": 100}, ...]
        OR: [{"source": "A", "target": "B", "value": 100}, ...]
        """
        chart_id_safe = chart_id or f"sankey-{int(datetime.now().timestamp())}"
        # Dimensions - v3.4.35: Reduced width to fit V2-chart-text layout with Key Insights panel
        container_width = 850  # Fits alongside ~400px Key Insights panel
        container_height = height

        # Parse data into nodes and links
        nodes_set = set()
        links = []

        # Handle two data formats:
        # Format 1: {"label": "Source → Target", "value": X}
        # Format 2: {"source": "A", "target": "B", "value": X}

        for item in data.get('values', data.get('data', [])) if isinstance(data, dict) else data:
            if 'source' in item and 'target' in item:
                # Format 2: Explicit source/target
                source = str(item['source'])
                target = str(item['target'])
                value = float(item.get('value', 0))
            else:
                # Format 1: Parse "Source → Target" from label
                label = str(item.get('label', ''))
                value = float(item.get('value', 0))

                # Split on arrow symbols
                if '→' in label or '->' in label or '→' in label:
                    parts = label.replace('->', '→').split('→')
                    if len(parts) == 2:
                        source = parts[0].strip()
                        target = parts[1].strip()
                    else:
                        # Fallback: treat as source→"Other"
                        source = label.strip()
                        target = "Other"
                else:
                    # No arrow: treat as source→"Output"
                    source = label.strip()
                    target = "Output"

            nodes_set.add(source)
            nodes_set.add(target)
            links.append({"source": source, "target": target, "value": value})

        # Create nodes array with indices
        nodes_list = sorted(list(nodes_set))
        nodes = [{"name": node} for node in nodes_list]
        node_index = {node: i for i, node in enumerate(nodes_list)}

        # Convert link source/target to indices
        links_with_indices = [
            {
                "source": node_index[link["source"]],
                "target": node_index[link["target"]],
                "value": link["value"]
            }
            for link in links
        ]

        # Prepare data for D3
        sankey_data = {
            "nodes": nodes,
            "links": links_with_indices
        }

        # Color palette for nodes
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52BE80"
        ]

        # Build D3 Sankey HTML
        d3_html = f"""<!-- D3.js Sankey Diagram -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/d3-sankey@0.12"></script>

<div class="l02-chart-container" style="width: {container_width}px; height: {container_height}px; position: relative; box-sizing: border-box; border: none; border-radius: 0; overflow: hidden;">
    <div id="{chart_id_safe}" style="width: 100%; height: 100%;"></div>
    <script>
        (function() {{
            const data = {json.dumps(sankey_data)};
            const colors = {json.dumps(colors)};

            function initD3Sankey() {{
                const container = document.getElementById('{chart_id_safe}');
                const width = container.clientWidth;
                const height = container.clientHeight;

                // Clear any existing content
                container.innerHTML = '';

                // Create SVG
                const svg = d3.select('#{chart_id_safe}')
                    .append('svg')
                    .attr('width', width)
                    .attr('height', height)
                    .attr('viewBox', [0, 0, width, height])
                    .attr('style', 'max-width: 100%; height: auto;');

                // Create Sankey generator
                const sankey = d3.sankey()
                    .nodeId(d => d.name)
                    .nodeWidth(15)
                    .nodePadding(10)
                    .extent([[20, 20], [width - 20, height - 20]]);

                // Generate the Sankey diagram
                const graph = sankey({{
                    nodes: data.nodes.map(d => Object.assign({{}}, d)),
                    links: data.links.map(d => Object.assign({{}}, d))
                }});

                // Create color scale
                const colorScale = d3.scaleOrdinal()
                    .domain(data.nodes.map(d => d.name))
                    .range(colors);

                // Add links (flows)
                svg.append('g')
                    .attr('fill', 'none')
                    .selectAll('path')
                    .data(graph.links)
                    .join('path')
                    .attr('d', d3.sankeyLinkHorizontal())
                    .attr('stroke', d => colorScale(d.source.name))
                    .attr('stroke-width', d => Math.max(1, d.width))
                    .attr('opacity', 0.4)
                    .on('mouseover', function(event, d) {{
                        d3.select(this).attr('opacity', 0.7);
                        showTooltip(event, `${{d.source.name}} → ${{d.target.name}}<br/>Value: ${{d.value.toLocaleString()}}`);
                    }})
                    .on('mouseout', function() {{
                        d3.select(this).attr('opacity', 0.4);
                        hideTooltip();
                    }});

                // Add nodes (rectangles)
                const nodes = svg.append('g')
                    .selectAll('rect')
                    .data(graph.nodes)
                    .join('rect')
                    .attr('x', d => d.x0)
                    .attr('y', d => d.y0)
                    .attr('height', d => d.y1 - d.y0)
                    .attr('width', d => d.x1 - d.x0)
                    .attr('fill', d => colorScale(d.name))
                    .attr('opacity', 0.9)
                    .on('mouseover', function(event, d) {{
                        d3.select(this).attr('opacity', 1.0);
                        const incoming = d.sourceLinks.reduce((sum, l) => sum + l.value, 0);
                        const outgoing = d.targetLinks.reduce((sum, l) => sum + l.value, 0);
                        showTooltip(event, `${{d.name}}<br/>In: ${{incoming.toLocaleString()}}<br/>Out: ${{outgoing.toLocaleString()}}`);
                    }})
                    .on('mouseout', function() {{
                        d3.select(this).attr('opacity', 0.9);
                        hideTooltip();
                    }});

                // Add node labels
                svg.append('g')
                    .style('font-size', '12px')
                    .style('font-weight', '600')
                    .selectAll('text')
                    .data(graph.nodes)
                    .join('text')
                    .attr('x', d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
                    .attr('y', d => (d.y1 + d.y0) / 2)
                    .attr('dy', '0.35em')
                    .attr('text-anchor', d => d.x0 < width / 2 ? 'start' : 'end')
                    .attr('fill', '#333')
                    .text(d => d.name);

                // Tooltip
                const tooltip = d3.select('#{chart_id_safe}')
                    .append('div')
                    .style('position', 'absolute')
                    .style('background', 'rgba(0, 0, 0, 0.8)')
                    .style('color', 'white')
                    .style('padding', '8px 12px')
                    .style('border-radius', '4px')
                    .style('font-size', '13px')
                    .style('pointer-events', 'none')
                    .style('opacity', 0)
                    .style('z-index', '1000');

                function showTooltip(event, html) {{
                    tooltip
                        .style('opacity', 1)
                        .html(html)
                        .style('left', (event.pageX - container.getBoundingClientRect().left + 10) + 'px')
                        .style('top', (event.pageY - container.getBoundingClientRect().top - 20) + 'px');
                }}

                function hideTooltip() {{
                    tooltip.style('opacity', 0);
                }}

                // Store chart instance for cleanup
                window.chartInstances = window.chartInstances || {{}};
                window.chartInstances['{chart_id_safe}'] = {{
                    destroy: function() {{
                        container.innerHTML = '';
                    }}
                }};

                console.log('✅ D3 Sankey diagram initialized:', '{chart_id_safe}');
            }}

            // Reveal.js integration
            if (typeof Reveal !== 'undefined') {{
                Reveal.on('ready', function() {{
                    const currentSlide = Reveal.getCurrentSlide();
                    if (currentSlide && currentSlide.querySelector('#{chart_id_safe}')) {{
                        initD3Sankey();
                    }}
                }});

                Reveal.on('slidechanged', function(event) {{
                    if (event.currentSlide.querySelector('#{chart_id_safe}')) {{
                        initD3Sankey();
                    }}
                }});
            }} else {{
                // Not in Reveal.js, init immediately
                if (document.readyState === 'loading') {{
                    document.addEventListener('DOMContentLoaded', initD3Sankey);
                }} else {{
                    initD3Sankey();
                }}
            }}
        }})();
    </script>
</div>"""

        # Add editor overlay if enabled
        if enable_editor and presentation_id:
            # Reconstruct simple format from links data for editor
            editor_data = [{"label": f"{link['source']} → {link['target']}", "value": link['value']} for link in links]
            d3_html = self._wrap_d3_chart_with_editor(
                d3_html=d3_html,
                chart_id=chart_id_safe,
                chart_type='d3_sankey',
                data=editor_data,  # Pass as list format for editor
                presentation_id=presentation_id,
                api_base_url=api_base_url
            )

        return d3_html

    def _merge_options(self, base: dict, override: dict) -> dict:
        """Deep merge two option dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_options(result[key], value)
            else:
                result[key] = value

        return result

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba with alpha."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"

    def _darken_color(self, hex_color: str, amount: float = 0.2) -> str:
        """Darken a hex color by a percentage."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = int(r * (1 - amount))
        g = int(g * (1 - amount))
        b = int(b * (1 - amount))

        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    print("Chart.js Generator - Production Version")
    print("=" * 60)
    print("This is the production Chart.js generator.")
    print("Import and use in your application:")
    print("")
    print("  from chartjs_generator import ChartJSGenerator")
    print("  generator = ChartJSGenerator(theme='professional')")
    print("  html = generator.generate_line_chart(data)")
    print("")
    print("Supported chart types: 20+ types")
    print("Themes: professional, corporate, vibrant")
    print("Formatters: currency, percentage, number")
