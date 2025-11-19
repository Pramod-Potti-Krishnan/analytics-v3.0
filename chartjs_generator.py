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

    THEMES = {
        "professional": {
            "primary": "#FF6B6B",      # Coral Red
            "secondary": "#4ECDC4",    # Turquoise
            "tertiary": "#FFE66D",     # Yellow
            "quaternary": "#95E1D3",   # Mint Green
            "quinary": "#F38181",      # Light Red
            "senary": "#AA96DA",       # Purple
            "septenary": "#FCBAD3",    # Pink
            "octonary": "#A8D8EA",     # Light Blue
            "palette": [
                "#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3",
                "#F38181", "#AA96DA", "#FCBAD3", "#A8D8EA"
            ],
            "gradients": {
                "red": ["rgba(255, 107, 107, 0.8)", "rgba(255, 107, 107, 0.2)"],
                "turquoise": ["rgba(78, 205, 196, 0.8)", "rgba(78, 205, 196, 0.2)"],
                "yellow": ["rgba(255, 230, 109, 0.8)", "rgba(255, 230, 109, 0.2)"],
                "mint": ["rgba(149, 225, 211, 0.8)", "rgba(149, 225, 211, 0.2)"],
                "purple": ["rgba(170, 150, 218, 0.8)", "rgba(170, 150, 218, 0.2)"]
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
        output_mode: str = "inline_script"  # "inline_script" (Layout Builder) or "revealchart" (legacy)
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

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"line-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode  # Pass through output mode
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
        output_mode: str = "inline_script"
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
            enable_editor, presentation_id, api_base_url, output_mode
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
        output_mode: str = "inline_script"
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
        # Extract chart data from array format if needed (v3.4.3 fix)
        if isinstance(data, list) and len(data) > 0:
            chart_data = data[0]
        else:
            chart_data = data

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
            enable_editor, presentation_id, api_base_url, output_mode
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
        output_mode: str = "inline_script"
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
            output_mode
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
        output_mode: str = "inline_script"
    ) -> str:
        """Generate horizontal bar chart."""
        return self.generate_bar_chart(
            data, height, horizontal=True, chart_id=chart_id, options=options,
            enable_editor=enable_editor, presentation_id=presentation_id,
            api_base_url=api_base_url, output_mode=output_mode
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
        output_mode: str = "inline_script"
    ) -> str:
        """
        Generate grouped bar chart (multiple series side-by-side).

        Requires data["datasets"] with multiple series.
        """
        # Extract chart data from array format if needed (v3.4.3 fix)
        if isinstance(data, list) and len(data) > 0:
            chart_data = data[0]
        else:
            chart_data = data

        if "datasets" not in chart_data:
            raise ValueError("Grouped bar chart requires 'datasets' in data")

        return self.generate_bar_chart(
            chart_data, height, horizontal=False, chart_id=chart_id, options=options,
            enable_editor=enable_editor, presentation_id=presentation_id,
            api_base_url=api_base_url, output_mode=output_mode
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
        output_mode: str = "inline_script"
    ) -> str:
        """
        Generate stacked bar chart.

        Bars stacked on top of each other.
        """
        # Extract chart data from array format if needed (v3.4.3 fix)
        if isinstance(data, list) and len(data) > 0:
            chart_data = data[0]
        else:
            chart_data = data

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
            api_base_url=api_base_url, output_mode=output_mode
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
        output_mode: str = "inline_script"
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
                    const dataIndex = context.dataIndex;
                    const value = context.parsed.y - context.parsed._custom;
                    const label = context.dataset.label || '';
                    return label + ': ' + value.toFixed(2);
                }"""
            }
        }

        return self._wrap_in_canvas(
            config,
            height,
            chart_id or f"waterfall-chart-{id(data)}",
            enable_editor,
            presentation_id,
            api_base_url,
            output_mode
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
        output_mode: str = "inline_script"
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
            enable_editor, presentation_id, api_base_url, output_mode
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
        output_mode: str = "inline_script"
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
            enable_editor, presentation_id, api_base_url, output_mode
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
        output_mode: str = "inline_script"
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
                            "padding": 15
                        }
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#fff",
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
            output_mode
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
        output_mode: str = "inline_script"
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
            output_mode
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
        output_mode: str = "inline_script"
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
            output_mode
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
        output_mode: str = "inline_script"
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
                        "labels": {"font": {"size": 14, "weight": "bold"}}
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
                            "color": "#666"
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
            output_mode
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
        output_mode: str = "inline_script"
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
                        "labels": {"font": {"size": 14, "weight": "bold"}}
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
            output_mode
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
        output_mode: str = "inline_script"
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
        treemap_html = f"""<!-- Treemap Chart with Chart.js Treemap Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@3.1.0/dist/chartjs-chart-treemap.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
    <canvas id="{chart_id_safe}"></canvas>
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
        output_mode: str = "inline_script"
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
        heatmap_html = f"""<!-- Heatmap/Matrix Chart with Chart.js Matrix Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@3.0.0/dist/chartjs-chart-matrix.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
    <canvas id="{chart_id_safe}"></canvas>
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
        output_mode: str = "inline_script"
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
                        "position": "top"
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
                        "grid": {"color": "rgba(0, 0, 0, 0.1)"}
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
        boxplot_html = f"""<!-- Boxplot Chart with Chart.js Boxplot Plugin -->
<script src="https://cdn.jsdelivr.net/npm/@sgratzl/chartjs-chart-boxplot@4.4.5/build/index.umd.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
    <canvas id="{chart_id_safe}"></canvas>
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
        output_mode: str = "inline_script"
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
                        "labels": {"font": {"size": 14}}
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
                        "grid": {"color": "rgba(0, 0, 0, 0.1)"}
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

        # Build HTML with financial plugin and Chart.js date adapter
        candlestick_html = f"""<!-- Candlestick/Financial Chart with Chart.js Financial Plugin -->
<script src="https://cdn.jsdelivr.net/npm/luxon@3.3.0/build/global/luxon.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.1/dist/chartjs-adapter-luxon.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.2.1/dist/chartjs-chart-financial.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
    <canvas id="{chart_id_safe}"></canvas>
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
        output_mode: str = "inline_script"
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
                        "color": "#333"
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

        # Build HTML with sankey plugin
        sankey_html = f"""<!-- Sankey Diagram with Chart.js Sankey Plugin -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.12.0/dist/chartjs-chart-sankey.min.js"></script>

<div class="l02-chart-container" style="width: 1260px; height: {height}px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
    <canvas id="{chart_id_safe}"></canvas>
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
        output_mode: str = "inline_script"
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
        labels = data.get("labels", [])
        format_type = data.get("format", "number")

        datasets = []
        for idx, ds in enumerate(data.get("datasets", [])):
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
            output_mode
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
        output_mode: str = "inline_script"  # "revealchart" or "inline_script"
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
                api_base_url
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
        api_base_url: str = "/api/charts"
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

        Args:
            config: Complete Chart.js configuration
            height: Canvas height (1260px for L02, but can be overridden)
            chart_id: Unique chart identifier
            enable_editor: If True, adds interactive data editor
            presentation_id: Required if enable_editor=True
            api_base_url: Base URL for chart API endpoints

        Returns:
            Complete HTML with chart and optional editor, Layout Builder compliant
        """
        # Convert config to JSON string for inline script
        config_json = json.dumps(config)

        # Sanitize chart_id for JavaScript
        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')

        # Build inline script with IIFE wrapper and Reveal.js-aware initialization
        # v3.3.4: Destroy and recreate chart on every slide visit to replay animations
        # This follows Layout Builder specification with Reveal.js timing fix
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

        # Basic chart HTML (no editor) - Director L02 spec compliant
        chart_html = f"""<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="{chart_id}"></canvas>
  <script>
    {inline_script}
  </script>
</div>"""

        # Add interactive editor if requested
        if enable_editor and presentation_id:
            chart_html = self._wrap_inline_script_with_editor(
                chart_html,
                chart_id,
                presentation_id,
                api_base_url,
                inline_script,
                chart_type=config.get('type', 'bar')  # v3.2.1: Pass chart type for dynamic editor
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
        chart_type: str = "bar"
    ) -> str:
        """
        Add interactive editor to inline-script chart (Layout Builder mode).

        Simpler than legacy editor because chart is already initialized inline.
        Just adds editor UI and references existing chart instance.

        Args:
            chart_html: Chart HTML with inline script
            chart_id: Unique chart identifier
            presentation_id: Presentation UUID
            api_base_url: Base URL for chart API
            inline_script: The Chart.js initialization script
            chart_type: Type of chart (bar, scatter, bubble, etc.) for dynamic editor

        Returns:
            Chart HTML with editor controls added
        """
        js_safe_id = chart_id.replace('-', '_').replace('.', '_').replace(' ', '_')
        modal_id = f"modal-{chart_id}"

        # v3.2.1: Dynamic table headers based on chart type
        if chart_type == "scatter":
            header_cols = """
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">X</th>
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Y</th>"""
        elif chart_type == "bubble":
            header_cols = """
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Label</th>
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">X</th>
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Y</th>
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Radius</th>"""
        else:
            header_cols = """
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Label</th>
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6;">Value</th>"""

        # Extract just the canvas and script from chart_html
        # chart_html structure: <div class="l02-chart-container">...canvas...script...</div>
        # We need to add editor button inside the container

        editor_html = f"""<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="{chart_id}"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn"
          onclick="openChartEditor_{js_safe_id}()"
          style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;"
          onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=\\'margin-left: 6px; font-size: 13px;\\'>edit</span>'; this.style.background='rgba(0,0,0,0.8)'"
          onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    {inline_script}
  </script>
</div>

<!-- Modal Popup for Editor -->
<div id="{modal_id}" class="chart-editor-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 10000;">
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; border-radius: 16px; width: 90%; max-width: 900px; max-height: 85vh; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.4); display: flex; flex-direction: column; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">

        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: white; border-bottom: 1px solid #e9ecef;">
            <h2 style="margin: 0; font-size: 24px; font-weight: 600; color: #667eea;">📊 Edit Chart Data</h2>
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: #f3f4f6; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 24px; color: #6b7280; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center;" onmouseover="this.style.background='#e5e7eb'" onmouseout="this.style.background='#f3f4f6'">&times;</button>
        </div>

        <!-- Body -->
        <div style="padding: 32px; overflow-y: auto; flex: 1; background: #f8f9fa;">
            <table id="table-{chart_id}" style="width: 100%; border-collapse: separate; border-spacing: 0; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <thead>
                    <tr style="background: linear-gradient(to right, #f8f9fa, #e9ecef);">
                        <th style="padding: 16px 20px; text-align: left; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6; width: 60px;">#</th>
                        {header_cols}
                        <th style="padding: 16px 20px; text-align: center; font-weight: 600; color: #495057; font-size: 16.8px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #dee2e6; width: 100px;">Actions</th>
                    </tr>
                </thead>
                <tbody id="tbody-{chart_id}"></tbody>
            </table>
            <button onclick="addRow_{js_safe_id}()" style="margin-top: 20px; background: white; color: #667eea; border: 2px dashed #667eea; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s; width: 100%;" onmouseover="this.style.background='#f8f9ff'; this.style.borderColor='#764ba2'" onmouseout="this.style.background='white'; this.style.borderColor='#667eea'">+ Add Row</button>
        </div>

        <!-- Footer -->
        <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 24px 32px; background: white; border-top: 1px solid #e9ecef;">
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: #f8f9fa; color: #495057; border: 1px solid #dee2e6; padding: 12px 28px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s;" onmouseover="this.style.background='#e9ecef'" onmouseout="this.style.background='#f8f9fa'">Cancel</button>
            <button onclick="saveChartData_{js_safe_id}()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 32px; border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(102, 126, 234, 0.5)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(102, 126, 234, 0.4)'">💾 Save & Update</button>
        </div>
    </div>
</div>

<script>
(function() {{
    window.openChartEditor_{js_safe_id} = function() {{
        // Lazy lookup: Get chart at button click time (not script load time)
        console.log('=== Edit Button Clicked ===');
        console.log('Looking for chart ID: {chart_id}');
        const chart = window.chartInstances?.['{chart_id}'];
        console.log('window.chartInstances:', window.chartInstances);
        console.log('Chart found:', !!chart);

        if (!chart) {{
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }}

        console.log('✅ Chart found, opening editor');

        // Populate table
        const tbody = document.getElementById('tbody-{chart_id}');
        tbody.innerHTML = '';

        const chartType = chart.config.type;
        console.log('Chart type:', chartType);

        // v3.2.1: Handle scatter/bubble charts (object data) vs other charts (array data)
        if (chartType === 'scatter' || chartType === 'bubble') {{
            // Scatter/bubble: data is array of {{x, y, label}} or {{x, y, r, label}}
            const dataPoints = chart.data.datasets[0]?.data || [];
            console.log('Object-based data points:', dataPoints.length);

            dataPoints.forEach((point, index) => {{
                const row = document.createElement('tr');
                row.style.transition = 'background 0.2s';

                if (chartType === 'scatter') {{
                    row.innerHTML = `
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{index + 1}}</td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="number" class="x-input" value="${{point.x}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="number" class="y-input" value="${{point.y}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                            <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                        </td>
                    `;
                }} else {{ // bubble
                    row.innerHTML = `
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{index + 1}}</td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="text" class="label-input" value="${{point.label || 'Bubble ' + (index + 1)}}" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="number" class="x-input" value="${{point.x}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="number" class="y-input" value="${{point.y}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                            <input type="number" class="r-input" value="${{point.r}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                        </td>
                        <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                            <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                        </td>
                    `;
                }}

                row.onmouseover = () => row.style.background = '#f8f9ff';
                row.onmouseout = () => row.style.background = 'transparent';
                tbody.appendChild(row);
            }});
        }} else {{
            // Other charts: data is labels array + values array
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            console.log('Array-based data:', labels.length, 'labels');

            labels.forEach((label, index) => {{
                const row = document.createElement('tr');
                row.style.transition = 'background 0.2s';
                row.innerHTML = `
                    <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{index + 1}}</td>
                    <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                        <input type="text" class="label-input" value="${{label}}" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                    </td>
                    <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                        <input type="number" class="value-input" value="${{values[index]}}" step="any" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                    </td>
                    <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                        <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                    </td>
                `;
                row.onmouseover = () => row.style.background = '#f8f9ff';
                row.onmouseout = () => row.style.background = 'transparent';
                tbody.appendChild(row);
            }});
        }}

        document.getElementById('{modal_id}').style.display = 'flex';
    }};

    window.closeChartEditor_{js_safe_id} = function() {{
        document.getElementById('{modal_id}').style.display = 'none';
    }};

    window.addRow_{js_safe_id} = function() {{
        const chart = window.chartInstances?.['{chart_id}'];
        const chartType = chart?.config?.type || 'bar';
        const tbody = document.getElementById('tbody-{chart_id}');
        const rowCount = tbody.querySelectorAll('tr').length;
        const row = document.createElement('tr');
        row.style.transition = 'background 0.2s';

        // v3.2.1: Chart-type-aware row templates
        if (chartType === 'scatter') {{
            row.innerHTML = `
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{rowCount + 1}}</td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="x-input" value="0" step="any" placeholder="Enter X" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="y-input" value="0" step="any" placeholder="Enter Y" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                    <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                </td>
            `;
        }} else if (chartType === 'bubble') {{
            row.innerHTML = `
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{rowCount + 1}}</td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="text" class="label-input" value="" placeholder="Bubble ${{rowCount + 1}}" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="x-input" value="0" step="any" placeholder="Enter X" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="y-input" value="0" step="any" placeholder="Enter Y" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="r-input" value="10" step="any" placeholder="Enter Radius" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                    <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                </td>
            `;
        }} else {{
            row.innerHTML = `
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; color: #868e96; font-weight: 600; font-size: 16.8px;">${{rowCount + 1}}</td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="text" class="label-input" value="" placeholder="Enter label" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5;">
                    <input type="number" class="value-input" value="0" step="any" placeholder="Enter value" style="width: 100%; padding: 10px 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; transition: all 0.2s; font-family: inherit;" onfocus="this.style.borderColor='#667eea'; this.style.boxShadow='0 0 0 3px rgba(102, 126, 234, 0.1)'" onblur="this.style.borderColor='#e9ecef'; this.style.boxShadow='none'">
                </td>
                <td style="padding: 16px 20px; border-bottom: 1px solid #f1f3f5; text-align: center;">
                    <button onclick="deleteRow_{js_safe_id}(this)" style="background: transparent; color: #ff4444; border: none; padding: 4px; cursor: pointer; font-size: 18px; transition: all 0.2s;" onmouseover="this.style.color='#cc0000'; this.style.transform='scale(1.1)'" onmouseout="this.style.color='#ff4444'; this.style.transform='scale(1)'">🗑️</button>
                </td>
            `;
        }}

        row.onmouseover = () => row.style.background = '#f8f9ff';
        row.onmouseout = () => row.style.background = 'transparent';
        tbody.appendChild(row);
    }};

    window.deleteRow_{js_safe_id} = function(btn) {{
        btn.closest('tr').remove();
    }};

    window.saveChartData_{js_safe_id} = async function() {{
        // Lazy lookup: Get chart at save time (not script load time)
        const chart = window.chartInstances?.['{chart_id}'];
        if (!chart) {{
            console.error('Chart not found when saving');
            alert('Chart not available. Please refresh and try again.');
            return;
        }}

        const chartType = chart.config.type;
        const rows = document.querySelectorAll('#tbody-{chart_id} tr');

        // v3.2.1 FIX: Declare variables outside blocks so they're available for backend save
        let newLabels = [];
        let newValues = [];

        // v3.2.1: Rebuild data structures based on chart type
        if (chartType === 'scatter' || chartType === 'bubble') {{
            // Scatter/bubble: rebuild object array
            const newDataPoints = [];

            rows.forEach((row, index) => {{
                const xInput = row.querySelector('.x-input');
                const yInput = row.querySelector('.y-input');
                const labelInput = row.querySelector('.label-input');
                const x = parseFloat(xInput.value);
                const y = parseFloat(yInput.value);
                const label = labelInput ? labelInput.value || `Point ${{index + 1}}` : `Point ${{index + 1}}`;

                if (chartType === 'scatter') {{
                    newDataPoints.push({{
                        x: x,
                        y: y,
                        label: label
                    }});
                }} else {{ // bubble
                    const rInput = row.querySelector('.r-input');
                    const r = parseFloat(rInput.value);
                    newDataPoints.push({{
                        x: x,
                        y: y,
                        r: r,
                        label: label || `Bubble ${{index + 1}}`
                    }});
                }}
            }});

            // Update chart data (NO labels array for scatter/bubble)
            chart.data.datasets[0].data = newDataPoints;
            console.log('Updated scatter/bubble data:', newDataPoints);

            // v3.2.1 FIX: For backend compatibility, convert to labels/values format
            // Backend expects labels + values even for scatter/bubble
            newLabels = newDataPoints.map(p => p.label || '');
            newValues = newDataPoints.map(p => chartType === 'scatter' ? p.y : p.r);
        }} else {{
            // Other charts: rebuild labels + values arrays
            rows.forEach(row => {{
                const label = row.querySelector('.label-input').value;
                const value = parseFloat(row.querySelector('.value-input').value);
                newLabels.push(label);
                newValues.push(value);
            }});

            // Update chart
            chart.data.labels = newLabels;
            chart.data.datasets[0].data = newValues;
            console.log('Updated chart data:', newLabels, newValues);
        }}

        chart.update();

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
                const toast = document.createElement('div');
                toast.innerHTML = '✅ Chart updated successfully!';
                toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 16px 24px; border-radius: 8px; z-index: 100001;';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);
                closeChartEditor_{js_safe_id}();
            }} else {{
                alert('Failed to save: ' + (result.error || 'Unknown error'));
            }}
        }} catch (error) {{
            console.error('Error saving chart data:', error);
            alert('Failed to save chart data.');
        }}
    }};
}})();
</script>
"""

        return editor_html

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
                        "usePointStyle": True
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
                        "color": "rgba(0, 0, 0, 0.08)",
                        "lineWidth": 1
                    },
                    "ticks": {
                        "display": True,  # Always show labels
                        "font": {"size": 12, "weight": "500"},
                        "color": "#333",
                        "padding": 8,
                        "autoSkip": False,  # Show all labels
                        "maxRotation": 45,
                        "minRotation": 0
                    },
                    "title": {
                        "display": True,
                        "text": "",  # Will be set per chart if needed
                        "font": {"size": 13, "weight": "bold"},
                        "color": "#333"
                    }
                },
                y_axis: {
                    # GUARANTEED: Always display Y-axis
                    "display": True,
                    "beginAtZero": True,  # Always start at zero
                    "grid": {
                        "display": True,  # Always show grid
                        "color": "rgba(0, 0, 0, 0.08)",
                        "lineWidth": 1
                    },
                    "ticks": {
                        "display": True,  # Always show labels
                        "font": {"size": 12, "weight": "500"},
                        "color": "#333",
                        "padding": 8,
                        **self._get_tick_config(format_type)
                    },
                    "title": {
                        "display": True,
                        "text": self._get_axis_title(format_type),  # Auto-set based on format
                        "font": {"size": 13, "weight": "bold"},
                        "color": "#333"
                    }
                }
            }

            # Horizontal bar charts - swap axis formatting
            if horizontal and chart_type == "bar":
                options["indexAxis"] = "y"
                # Move tick formatting to x-axis for horizontal bars
                options["scales"]["x"]["ticks"].update(self._get_tick_config(format_type))
                options["scales"]["x"]["title"]["text"] = self._get_axis_title(format_type)
                # Remove tick config from y-axis
                options["scales"]["y"]["ticks"] = {
                    "display": True,
                    "font": {"size": 12, "weight": "500"},
                    "color": "#333",
                    "padding": 8,
                    "autoSkip": False
                }
                options["scales"]["y"]["title"]["text"] = ""

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
