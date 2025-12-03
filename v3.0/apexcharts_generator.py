"""
ApexCharts HTML Generator for Analytics Microservice v3.

Generates self-contained, presentation-ready HTML with ApexCharts for Reveal.js integration.
Charts animate on slide appearance and support interactive features (hover, zoom, pan).
"""

import json
import uuid
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ApexChartsGenerator:
    """Generate interactive ApexCharts HTML for presentation slides."""

    # CDN version for ApexCharts
    APEXCHARTS_VERSION = "3.45.0"
    APEXCHARTS_CDN = f"https://cdn.jsdelivr.net/npm/apexcharts@{APEXCHARTS_VERSION}/dist/apexcharts.min.js"

    # Theme color palettes
    THEME_COLORS = {
        "professional": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"],
        "dark": ["#00ff00", "#ff00ff", "#00ffff", "#ffff00", "#ff6600"],
        "colorful": ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"],
        "minimal": ["#333333", "#666666", "#999999", "#cccccc", "#e0e0e0"],
        "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    }

    def __init__(self, theme: str = "professional"):
        """
        Initialize ApexCharts generator.

        Args:
            theme: Color theme (professional, dark, colorful, minimal, default)
        """
        self.theme = theme
        self.colors = self.THEME_COLORS.get(theme, self.THEME_COLORS["default"])

    def generate_chart_html(
        self,
        chart_type: str,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        chart_id: Optional[str] = None
    ) -> str:
        """
        Generate complete HTML for a chart (auto-routes to specific chart type).

        Args:
            chart_type: ApexCharts chart type (line, bar, donut, etc.)
            data: Chart data with labels and values
            height: Chart height in pixels
            width: Chart width in pixels
            chart_id: Optional custom chart ID

        Returns:
            Self-contained HTML with ApexCharts
        """
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        # Route to specific chart generator
        if chart_type == "line":
            return self.generate_line_chart(data, height, width, chart_id)
        elif chart_type == "bar":
            return self.generate_bar_chart(data, height, width, chart_id)
        elif chart_type == "donut":
            return self.generate_donut_chart(data, height, width, chart_id)
        else:
            # Default to bar chart
            logger.warning(f"Unknown chart type {chart_type}, defaulting to bar")
            return self.generate_bar_chart(data, height, width, chart_id)

    def generate_line_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        chart_id: Optional[str] = None
    ) -> str:
        """Generate line chart HTML."""
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        config = {
            "chart": {
                "type": "line",
                "height": height,
                "width": "100%",
                "animations": {
                    "enabled": True,
                    "easing": "easeinout",
                    "speed": 800,
                    "animateGradually": {
                        "enabled": True,
                        "delay": 150
                    }
                },
                "toolbar": {"show": False},
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "responsive": [{
                "breakpoint": 10000,
                "options": {
                    "chart": {
                        "width": "100%"
                    },
                    "legend": {
                        "position": "bottom"
                    }
                }
            }],
            "series": [{
                "name": data.get("series_name", "Data"),
                "data": data.get("values", [])
            }],
            "xaxis": {
                "categories": data.get("labels", []),
                "labels": {
                    "style": {
                        "fontSize": "14px",
                        "fontWeight": 500
                    }
                }
            },
            "yaxis": {
                "labels": {
                    "style": {
                        "fontSize": "14px"
                    },
                    "formatter": self._get_value_formatter(data)
                }
            },
            "stroke": {
                "curve": "smooth",
                "width": 3
            },
            "markers": {
                "size": 6,
                "hover": {"size": 8}
            },
            "colors": [self.colors[0]],
            "tooltip": {
                "y": {
                    "formatter": self._get_tooltip_formatter(data)
                }
            },
            "grid": {
                "borderColor": "#e0e0e0",
                "strokeDashArray": 4
            }
        }

        return self._wrap_in_html(chart_id, config, height)

    def generate_bar_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        horizontal: bool = False,
        chart_id: Optional[str] = None
    ) -> str:
        """Generate bar chart HTML (vertical or horizontal)."""
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        config = {
            "chart": {
                "type": "bar",
                "height": height,
                "width": "100%",
                "animations": {
                    "enabled": True,
                    "speed": 800,
                    "animateGradually": {
                        "enabled": True,
                        "delay": 150
                    }
                },
                "toolbar": {"show": False},
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "responsive": [{
                "breakpoint": 10000,
                "options": {
                    "chart": {
                        "width": "100%"
                    },
                    "legend": {
                        "position": "bottom"
                    }
                }
            }],
            "plotOptions": {
                "bar": {
                    "horizontal": horizontal,
                    "borderRadius": 8,
                    "dataLabels": {
                        "position": "top" if not horizontal else "center"
                    },
                    "columnWidth": "60%"
                }
            },
            "dataLabels": {
                "enabled": True,
                "formatter": self._get_data_label_formatter(data),
                "offsetY": -20 if not horizontal else 0,
                "style": {
                    "fontSize": "14px",
                    "fontWeight": "bold",
                    "colors": ["#304758"]
                }
            },
            "series": [{
                "name": data.get("series_name", "Values"),
                "data": data.get("values", [])
            }],
            "xaxis": {
                "categories": data.get("labels", []),
                "labels": {
                    "style": {
                        "fontSize": "14px",
                        "fontWeight": 500
                    }
                }
            },
            "yaxis": {
                "labels": {
                    "style": {"fontSize": "14px"},
                    "formatter": self._get_value_formatter(data)
                }
            },
            "colors": [self.colors[1]],
            "tooltip": {
                "y": {
                    "formatter": self._get_tooltip_formatter(data)
                }
            },
            "grid": {
                "borderColor": "#e0e0e0",
                "strokeDashArray": 4
            }
        }

        return self._wrap_in_html(chart_id, config, height)

    def generate_donut_chart(
        self,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        chart_id: Optional[str] = None
    ) -> str:
        """Generate donut chart HTML."""
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        config = {
            "chart": {
                "type": "donut",
                "height": height,
                "width": "100%",
                "animations": {
                    "enabled": True,
                    "speed": 800
                },
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "responsive": [{
                "breakpoint": 10000,
                "options": {
                    "chart": {
                        "width": "100%"
                    },
                    "legend": {
                        "position": "bottom"
                    }
                }
            }],
            "series": data.get("values", []),
            "labels": data.get("labels", []),
            "colors": self.colors,
            "legend": {
                "position": "bottom",
                "fontSize": "16px",
                "fontWeight": 500,
                "horizontalAlign": "center"
            },
            "dataLabels": {
                "enabled": True,
                "formatter": self._create_percentage_formatter(),
                "style": {
                    "fontSize": "16px",
                    "fontWeight": "bold"
                }
            },
            "plotOptions": {
                "pie": {
                    "donut": {
                        "size": "65%",
                        "labels": {
                            "show": True,
                            "total": {
                                "show": True,
                                "label": data.get("total_label", "Total"),
                                "fontSize": "18px",
                                "fontWeight": 600,
                                "formatter": self._create_total_formatter(data)
                            }
                        }
                    }
                }
            },
            "tooltip": {
                "y": {
                    "formatter": self._get_tooltip_formatter(data)
                }
            }
        }

        return self._wrap_in_html(chart_id, config, height)

    def _wrap_in_html(self, chart_id: str, config: dict, height: int) -> str:
        """
        Wrap ApexCharts config in HTML with Reveal.js integration.

        Args:
            chart_id: Unique chart identifier
            config: ApexCharts configuration object
            height: Chart height in pixels

        Returns:
            Complete HTML string with embedded JavaScript
        """
        # Convert config to JavaScript object string
        # We use a custom serializer to handle function strings correctly
        config_json = self._dict_to_js_object(config)

        html = f"""<div id="{chart_id}" style="width: 100%; height: {height}px;"></div>
<script>
(function() {{
  console.log('📊 Chart script executing for {chart_id}');

  // Check if ApexCharts is available
  if (typeof ApexCharts === 'undefined') {{
    console.error('❌ ApexCharts library not loaded for {chart_id}');
    return;
  }}
  console.log('✅ ApexCharts available for {chart_id}');

  // ApexCharts configuration
  const options = {config_json};

  // Initialize chart
  const chartElement = document.querySelector('#{chart_id}');
  if (!chartElement) {{
    console.error('❌ Chart element not found: #{chart_id}');
    return;
  }}
  console.log('✅ Chart element found: #{chart_id}');

  const chart = new ApexCharts(chartElement, options);
  console.log('✅ ApexCharts instance created for {chart_id}');

  // FIXED: Use unique named handlers per chart to avoid race condition
  if (typeof Reveal !== 'undefined') {{
    console.log('✅ Reveal.js detected for {chart_id}');

    // Unique ready handler per chart
    const readyHandler_{chart_id.replace('-', '_')} = function() {{
      console.log('🎯 Reveal ready handler fired for {chart_id}');
      const currentSlide = Reveal.getCurrentSlide();
      if (currentSlide && currentSlide.querySelector('#{chart_id}') && !chart.rendered) {{
        console.log('🎨 Rendering chart {chart_id} (ready)');
        try {{
          chart.render();
          chart.rendered = true;
          console.log('✅ Chart {chart_id} rendered successfully!');
        }} catch (error) {{
          console.error('❌ Error rendering {chart_id}:', error);
        }}
      }}
    }};

    // Unique slidechanged handler per chart
    const slideChangedHandler_{chart_id.replace('-', '_')} = function(event) {{
      if (event.currentSlide.querySelector('#{chart_id}') && !chart.rendered) {{
        console.log('🎨 Rendering chart {chart_id} (slide changed)');
        try {{
          chart.render();
          chart.rendered = true;
          console.log('✅ Chart {chart_id} rendered successfully!');
          // Clean up after rendering
          Reveal.off('slidechanged', slideChangedHandler_{chart_id.replace('-', '_')});
        }} catch (error) {{
          console.error('❌ Error rendering {chart_id}:', error);
        }}
      }}
    }};

    // Register BOTH handlers with unique names
    Reveal.on('ready', readyHandler_{chart_id.replace('-', '_')});
    Reveal.on('slidechanged', slideChangedHandler_{chart_id.replace('-', '_')});
  }} else {{
    console.log('⚠️ Reveal.js not detected, rendering immediately for {chart_id}');
    chart.render();
  }}
}})();
</script>"""

        return html

    def _get_value_formatter(self, data: Dict[str, Any]) -> str:
        """Get JavaScript formatter function for axis values."""
        format_type = data.get("format", "number")

        # CRITICAL: Use string concatenation NOT template literals
        # Template literals with $${} break ApexCharts parser
        if format_type == "currency":
            return "(val) => '$' + (Number(val)/1000).toFixed(0) + 'K'"
        elif format_type == "percentage":
            return "(val) => Number(val).toFixed(1) + '%'"
        else:
            return "(val) => Number(val).toLocaleString()"

    def _get_tooltip_formatter(self, data: Dict[str, Any]) -> str:
        """Get JavaScript formatter function for tooltips."""
        format_type = data.get("format", "number")

        # CRITICAL: Use string concatenation NOT template literals
        if format_type == "currency":
            return "(val) => '$' + Number(val).toLocaleString()"
        elif format_type == "percentage":
            return "(val) => Number(val).toFixed(1) + '%'"
        else:
            return "(val) => Number(val).toLocaleString()"

    def _get_data_label_formatter(self, data: Dict[str, Any]) -> str:
        """Get JavaScript formatter function for data labels."""
        format_type = data.get("format", "number")

        # CRITICAL: Use string concatenation NOT template literals
        if format_type == "currency":
            return "(val) => '$' + (Number(val)/1000).toFixed(0) + 'K'"
        elif format_type == "percentage":
            return "(val) => Number(val).toFixed(1) + '%'"
        else:
            return "(val) => Number(val).toLocaleString()"

    def _create_percentage_formatter(self) -> str:
        """Create percentage formatter for donut charts."""
        # CRITICAL: Use string concatenation NOT template literals
        return "(val) => Number(val).toFixed(1) + '%'"

    def _create_total_formatter(self, data: Dict[str, Any]) -> str:
        """Create total formatter for donut chart center."""
        format_type = data.get("format", "number")

        # CRITICAL: Use string concatenation NOT template literals
        if format_type == "currency":
            return "(w) => '$' + w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString()"
        else:
            return "(w) => w.globals.seriesTotals.reduce((a, b) => a + b, 0).toLocaleString()"

    def generate_line_chart_debug(
        self,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        chart_id: Optional[str] = None
    ) -> str:
        """Generate line chart HTML with debug logging and NO formatters."""
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        # Minimal config with NO formatters
        config = {
            "chart": {
                "type": "line",
                "height": height,
                "width": "100%",
                "animations": {"enabled": True, "speed": 800},
                "toolbar": {"show": False},
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "series": [{
                "name": data.get("series_name", "Data"),
                "data": data.get("values", [])
            }],
            "xaxis": {
                "categories": data.get("labels", [])
            },
            "stroke": {"curve": "smooth", "width": 3},
            "markers": {"size": 6},
            "colors": [self.colors[0]]
        }

        return self._wrap_in_html_debug(chart_id, config, height)

    def generate_bar_chart_debug(
        self,
        data: Dict[str, Any],
        height: int = 600,
        width: int = 1800,
        chart_id: Optional[str] = None
    ) -> str:
        """Generate bar chart HTML with debug logging and NO formatters."""
        chart_id = chart_id or f"chart-{uuid.uuid4().hex[:8]}"

        # Minimal config with NO formatters
        config = {
            "chart": {
                "type": "bar",
                "height": height,
                "width": "100%",
                "animations": {"enabled": True, "speed": 800},
                "toolbar": {"show": False},
                "fontFamily": "Inter, system-ui, sans-serif"
            },
            "plotOptions": {
                "bar": {
                    "horizontal": False,
                    "borderRadius": 8,
                    "columnWidth": "60%"
                }
            },
            "series": [{
                "name": data.get("series_name", "Values"),
                "data": data.get("values", [])
            }],
            "xaxis": {
                "categories": data.get("labels", [])
            },
            "colors": [self.colors[1]]
        }

        return self._wrap_in_html_debug(chart_id, config, height)

    def _wrap_in_html_debug(self, chart_id: str, config: dict, height: int) -> str:
        """
        Wrap ApexCharts config with EXTENSIVE debug logging.

        Outputs the complete config object to console before rendering.
        """
        config_json = self._dict_to_js_object(config)

        html = f"""<div id="{chart_id}" style="width: 100%; height: {height}px;"></div>
<script>
(function() {{
  console.log('🔍 DEBUG: Chart script executing for {chart_id}');

  if (typeof ApexCharts === 'undefined') {{
    console.error('❌ ApexCharts library not loaded for {chart_id}');
    return;
  }}
  console.log('✅ ApexCharts available');

  // ApexCharts configuration
  const options = {config_json};

  // DEBUG: Output complete config
  console.log('🔍 DEBUG: Complete ApexCharts config for {chart_id}:', JSON.stringify(options, null, 2));
  console.log('🔍 DEBUG: Series data:', options.series);
  console.log('🔍 DEBUG: X-axis categories:', options.xaxis?.categories);
  console.log('🔍 DEBUG: Chart type:', options.chart?.type);

  const chartElement = document.querySelector('#{chart_id}');
  if (!chartElement) {{
    console.error('❌ Chart element not found: #{chart_id}');
    return;
  }}
  console.log('✅ Chart element found');

  try {{
    const chart = new ApexCharts(chartElement, options);
    console.log('✅ ApexCharts instance created for {chart_id}');

    // FIXED: Use unique handler names per chart to avoid race conditions
    if (typeof Reveal !== 'undefined') {{
      console.log('✅ Reveal.js detected');

      // Unique ready handler per chart
      const readyHandler_{chart_id.replace('-', '_')} = function() {{
        console.log('🎯 Reveal ready handler fired for {chart_id}');
        const currentSlide = Reveal.getCurrentSlide();
        if (currentSlide && currentSlide.querySelector('#{chart_id}')) {{
          console.log('🎨 Rendering {chart_id} now (on current slide)');
          try {{
            chart.render();
            console.log('✅ Chart {chart_id} rendered successfully!');
            chart.rendered = true;
          }} catch (renderError) {{
            console.error('❌ Render error for {chart_id}:', renderError);
            console.error('Stack trace:', renderError.stack);
          }}
        }} else {{
          console.log('ℹ️ Chart {chart_id} not on current slide');
        }}
      }};

      // Unique slidechanged handler per chart
      const slideChangedHandler_{chart_id.replace('-', '_')} = function(event) {{
        const currentSlide = event.currentSlide;
        if (currentSlide && currentSlide.querySelector('#{chart_id}') && !chart.rendered) {{
          console.log('🎨 Rendering {chart_id} (slide changed)');
          try {{
            chart.render();
            console.log('✅ Chart {chart_id} rendered successfully!');
            chart.rendered = true;
            Reveal.off('slidechanged', slideChangedHandler_{chart_id.replace('-', '_')});
          }} catch (renderError) {{
            console.error('❌ Render error for {chart_id}:', renderError);
            console.error('Stack trace:', renderError.stack);
          }}
        }}
      }};

      // Register both handlers with unique names
      Reveal.on('ready', readyHandler_{chart_id.replace('-', '_')});
      Reveal.on('slidechanged', slideChangedHandler_{chart_id.replace('-', '_')});
    }} else {{
      console.log('⚠️ Reveal.js not detected, rendering immediately');
      try {{
        chart.render();
        console.log('✅ Chart {chart_id} rendered successfully!');
      }} catch (renderError) {{
        console.error('❌ Render error for {chart_id}:', renderError);
        console.error('Stack trace:', renderError.stack);
      }}
    }}
  }} catch (constructorError) {{
    console.error('❌ Error creating ApexCharts instance for {chart_id}:', constructorError);
    console.error('Stack trace:', constructorError.stack);
  }}
}})();
</script>"""

        return html

    def _dict_to_js_object(self, obj: Any, indent: int = 2) -> str:
        """
        Convert Python dict to JavaScript object string.

        Handles function strings correctly (doesn't quote them).
        A string is treated as a function if it starts with '(' or 'function'.

        Args:
            obj: Python object to convert
            indent: Indentation level for formatting

        Returns:
            JavaScript object string
        """
        if obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif isinstance(obj, str):
            # Check if this is a function string
            trimmed = obj.strip()
            if trimmed.startswith('(') and '=>' in trimmed:
                # Arrow function - return unquoted
                return obj
            elif trimmed.startswith('function'):
                # Traditional function - return unquoted
                return obj
            else:
                # Regular string - escape and quote
                return json.dumps(obj)
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            items = [self._dict_to_js_object(item, indent + 2) for item in obj]
            if all(len(str(item)) < 40 for item in items):
                # Short array - single line
                return "[" + ", ".join(items) + "]"
            else:
                # Long array - multi-line
                spacing = "\n" + " " * (indent + 2)
                return "[" + spacing + ("," + spacing).join(items) + "\n" + " " * indent + "]"
        elif isinstance(obj, dict):
            if not obj:
                return "{}"
            pairs = []
            for key, value in obj.items():
                key_str = f'"{key}"' if not key.replace('_', '').isalnum() else f'"{key}"'
                value_str = self._dict_to_js_object(value, indent + 2)
                pairs.append(f'{" " * (indent + 2)}{key_str}: {value_str}')
            return "{\n" + ",\n".join(pairs) + "\n" + " " * indent + "}"
        else:
            # Fallback for unknown types
            return json.dumps(obj)
