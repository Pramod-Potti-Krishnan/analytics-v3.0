"""
Chart.js Test Generator - Simple test to verify RevealChart plugin works

This is a minimal implementation to test if Chart.js with RevealChart plugin
can solve the race condition issues we've been experiencing with ApexCharts.

If this test succeeds (all 3 charts render), we'll proceed with full migration.
"""

import json
from typing import Dict, Any, List


class ChartJSTestGenerator:
    """
    Minimal Chart.js generator for testing RevealChart plugin integration.

    Chart.js uses Canvas rendering instead of SVG (like ApexCharts).
    The RevealChart plugin handles all Reveal.js lifecycle automatically.
    """

    def __init__(self, theme: str = "professional"):
        self.theme = theme

        # Vibrant, colorful palette
        self.colors = {
            "primary": "#FF6B6B",      # Coral Red
            "secondary": "#4ECDC4",    # Turquoise
            "tertiary": "#FFE66D",     # Yellow
            "quaternary": "#95E1D3",   # Mint Green
            "quinary": "#F38181",      # Light Red
            "senary": "#AA96DA",       # Purple
            "septenary": "#FCBAD3",    # Pink
            "octonary": "#A8D8EA"      # Light Blue
        }

        # Gradient colors for backgrounds
        self.gradients = {
            "red": ["rgba(255, 107, 107, 0.8)", "rgba(255, 107, 107, 0.2)"],
            "turquoise": ["rgba(78, 205, 196, 0.8)", "rgba(78, 205, 196, 0.2)"],
            "yellow": ["rgba(255, 230, 109, 0.8)", "rgba(255, 230, 109, 0.2)"],
            "mint": ["rgba(149, 225, 211, 0.8)", "rgba(149, 225, 211, 0.2)"],
            "purple": ["rgba(170, 150, 218, 0.8)", "rgba(170, 150, 218, 0.2)"]
        }

    def generate_line_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: str = "line-chart"
    ) -> str:
        """
        Generate Chart.js line chart HTML.

        Chart.js uses a different config structure than ApexCharts:
        - "data.labels" instead of "xaxis.categories"
        - "data.datasets" instead of "series"
        - "options.scales.y.ticks.callback" instead of "yaxis.labels.formatter"
        """
        labels = data.get("labels", [])
        values = data.get("values", [])
        series_name = data.get("series_name", "Data")
        format_type = data.get("format", "number")

        # Build Chart.js config with gradient
        config = {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": series_name,
                    "data": values,
                    "borderColor": self.colors["primary"],
                    "backgroundColor": "rgba(255, 107, 107, 0.2)",  # Coral gradient
                    "borderWidth": 4,
                    "pointRadius": 6,
                    "pointBackgroundColor": self.colors["primary"],
                    "pointBorderColor": "#fff",
                    "pointBorderWidth": 3,
                    "pointHoverRadius": 8,
                    "pointHoverBackgroundColor": self.colors["primary"],
                    "pointHoverBorderColor": "#fff",
                    "tension": 0.4,  # Smooth curves
                    "fill": True
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top",
                        "labels": {
                            "font": {"size": 14, "weight": "bold"}
                        }
                    },
                    "tooltip": {
                        "enabled": True,
                        "callbacks": self._get_tooltip_callback(format_type)
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#fff",
                        "font": {"size": 14, "weight": "bold"},
                        "formatter": self._get_datalabel_formatter(format_type),
                        "anchor": "end",
                        "align": "top",
                        "offset": 4
                    }
                },
                "scales": {
                    "x": {
                        "display": True,
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "font": {"size": 12},
                            "color": "#666"
                        }
                    },
                    "y": {
                        "display": True,
                        "beginAtZero": True,
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "font": {"size": 12},
                            "color": "#666",
                            **self._get_tick_config(format_type)
                        }
                    }
                }
            }
        }

        return self._wrap_in_canvas(config, height, chart_id)

    def generate_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        horizontal: bool = False,
        chart_id: str = "bar-chart"
    ) -> str:
        """Generate Chart.js bar chart HTML."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        series_name = data.get("series_name", "Data")
        format_type = data.get("format", "number")

        chart_type = "bar" if not horizontal else "horizontalBar"

        # Use different color for each bar
        bar_colors = [
            self.colors["secondary"],   # Turquoise
            self.colors["tertiary"],    # Yellow
            self.colors["quaternary"],  # Mint Green
            self.colors["senary"]       # Purple
        ]

        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": series_name,
                    "data": values,
                    "backgroundColor": bar_colors[:len(values)],
                    "borderColor": bar_colors[:len(values)],
                    "borderWidth": 2,
                    "borderRadius": 10,
                    "hoverBorderWidth": 3,
                    "hoverBorderColor": "#fff"
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "indexAxis": "y" if horizontal else "x",
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top",
                        "labels": {
                            "font": {"size": 14, "weight": "bold"}
                        }
                    },
                    "tooltip": {
                        "enabled": True,
                        "callbacks": self._get_tooltip_callback(format_type)
                    },
                    "datalabels": {
                        "display": True,
                        "color": "#fff",
                        "font": {"size": 14, "weight": "bold"},
                        "formatter": self._get_datalabel_formatter(format_type),
                        "anchor": "end",
                        "align": "end"
                    }
                },
                "scales": {
                    "x": {
                        "display": True,
                        "beginAtZero": True if horizontal else False,
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "font": {"size": 12},
                            "color": "#666",
                            **(self._get_tick_config(format_type) if horizontal else {})
                        }
                    },
                    "y": {
                        "display": True,
                        "beginAtZero": True if not horizontal else False,
                        "grid": {
                            "display": True,
                            "color": "rgba(0, 0, 0, 0.05)"
                        },
                        "ticks": {
                            "font": {"size": 12},
                            "color": "#666",
                            **(self._get_tick_config(format_type) if not horizontal else {})
                        }
                    }
                }
            }
        }

        return self._wrap_in_canvas(config, height, chart_id)

    def generate_doughnut_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        chart_id: str = "doughnut-chart"
    ) -> str:
        """
        Generate Chart.js doughnut chart HTML.

        Note: Chart.js calls it "doughnut" not "donut"
        """
        labels = data.get("labels", [])
        values = data.get("values", [])

        # Use vibrant colors for segments
        colors = [
            self.colors["quinary"],     # Light Red
            self.colors["secondary"],   # Turquoise
            self.colors["senary"],      # Purple
            self.colors["tertiary"],    # Yellow
            self.colors["quaternary"]   # Mint Green
        ]

        # Hover colors (slightly darker)
        hover_colors = [
            "#F06060",  # Darker red
            "#3DB8AF",  # Darker turquoise
            "#9A7FC9",  # Darker purple
            "#FFE045",  # Darker yellow
            "#7FD4C1"   # Darker mint
        ]

        config = {
            "type": "doughnut",
            "data": {
                "labels": labels,
                "datasets": [{
                    "data": values,
                    "backgroundColor": colors[:len(values)],
                    "borderColor": "#fff",
                    "borderWidth": 4,
                    "hoverBackgroundColor": hover_colors[:len(values)],
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
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.parsed + '%'; }"
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

        return self._wrap_in_canvas(config, height, chart_id)

    def _wrap_in_canvas(self, config: dict, height: int, chart_id: str) -> str:
        """
        Wrap Chart.js config in canvas element for RevealChart plugin.

        RevealChart plugin looks for <canvas data-chart="type"> elements
        and reads the config from a JSON comment.

        This is MUCH simpler than ApexCharts - no event handlers needed!
        The plugin handles everything automatically.
        """
        config_json = json.dumps(config, indent=2)

        html = f"""<canvas id="{chart_id}" data-chart="{config['type']}" height="{height}">
<!--
{config_json}
-->
</canvas>"""

        return html

    def _get_tick_config(self, format_type: str) -> dict:
        """Get tick configuration for axis formatting."""
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

    def _get_tooltip_callback(self, format_type: str) -> dict:
        """Get tooltip callback for formatting."""
        if format_type == "currency":
            return {
                "label": "function(context) { return context.dataset.label + ': $' + context.parsed.y.toLocaleString(); }"
            }
        elif format_type == "percentage":
            return {
                "label": "function(context) { return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%'; }"
            }
        else:
            return {
                "label": "function(context) { return context.dataset.label + ': ' + context.parsed.y.toLocaleString(); }"
            }

    def _get_datalabel_formatter(self, format_type: str) -> str:
        """Get data label formatter function as string."""
        if format_type == "currency":
            return "function(value) { return '$' + (value/1000).toFixed(0) + 'K'; }"
        elif format_type == "percentage":
            return "function(value) { return value.toFixed(1) + '%'; }"
        else:
            return "function(value) { return value.toLocaleString(); }"

    def _hex_to_rgba(self, hex_color: str, alpha: float) -> str:
        """Convert hex color to rgba with alpha."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"


if __name__ == "__main__":
    print("Chart.js Test Generator")
    print("=" * 60)
    print("This script generates Chart.js charts for testing.")
    print("Use test_chartjs.py to create a test presentation.")
