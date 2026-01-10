"""
Atomic Chart Generator for Analytics Microservice v3.5.1

Generates atomic chart elements with synthetic data for frontend positioning.
Each chart is a self-contained HTML element ready for placement.

Key Features:
- 14 gold standard chart types
- Synthetic data generation
- Optional Key Insights panel
- Self-contained HTML with embedded scripts
- Frontend-ready element IDs
- Optional chart editor with edit button (v3.5.1)

v3.5.1 Changes:
- Removed chart-title-bar from atomic container (slide template provides title)
- Pass chart_title=None to prevent duplicate titles in chart HTML
- Added enable_editor and presentation_id parameters for edit button support
"""

import logging
import time
import uuid
import json
from typing import Dict, Any, List, Optional

from models.atomic_models import (
    AtomicChartRequest,
    AtomicChartResponse,
    ChartDimensions,
    GOLD_STANDARD_CHARTS
)
from synthetic_data_generator import SyntheticDataGenerator
from chartjs_generator import ChartJSGenerator
from insight_generator import InsightGenerator

logger = logging.getLogger(__name__)


class AtomicChartGenerator:
    """
    Generate atomic chart elements for frontend positioning.

    Each call produces a standalone chart element that can be
    positioned anywhere on the slide by the frontend.
    """

    # Chart type configurations
    CHART_CONFIGS = {
        "line": {
            "display_name": "Line Chart",
            "category": "trend",
            "method": "generate_line_chart",
            "data_format": "labels + values",
            "supports_multi_series": True,
            "use_cases": ["Time series", "Trends", "Performance over time"]
        },
        "bar_vertical": {
            "display_name": "Vertical Bar Chart",
            "category": "comparison",
            "method": "generate_bar_chart",
            "orientation": "vertical",
            "data_format": "labels + values",
            "supports_multi_series": True,
            "use_cases": ["Category comparison", "Rankings", "Metrics by group"]
        },
        "bar_horizontal": {
            "display_name": "Horizontal Bar Chart",
            "category": "comparison",
            "method": "generate_bar_chart",
            "orientation": "horizontal",
            "data_format": "labels + values",
            "supports_multi_series": True,
            "use_cases": ["Long labels", "Rankings", "Survey results"]
        },
        "pie": {
            "display_name": "Pie Chart",
            "category": "composition",
            "method": "generate_pie_chart",
            "data_format": "labels + values (percentages)",
            "supports_multi_series": False,
            "use_cases": ["Market share", "Budget allocation", "Distribution"]
        },
        "doughnut": {
            "display_name": "Doughnut Chart",
            "category": "composition",
            "method": "generate_doughnut_chart",
            "data_format": "labels + values (percentages)",
            "supports_multi_series": False,
            "use_cases": ["Progress indicators", "KPI breakdown", "Portfolio mix"]
        },
        "scatter": {
            "display_name": "Scatter Plot",
            "category": "correlation",
            "method": "generate_scatter_chart",
            "data_format": "x + y coordinates",
            "supports_multi_series": True,
            "use_cases": ["Correlations", "Clustering", "Outlier detection"]
        },
        "bubble": {
            "display_name": "Bubble Chart",
            "category": "correlation",
            "method": "generate_bubble_chart",
            "data_format": "x + y + r (radius)",
            "supports_multi_series": True,
            "use_cases": ["3D data visualization", "Market analysis", "Product positioning"]
        },
        "polar_area": {
            "display_name": "Polar Area Chart",
            "category": "composition",
            "method": "generate_polar_area_chart",
            "data_format": "labels + values",
            "supports_multi_series": False,
            "use_cases": ["Cyclical data", "Directional metrics", "Wind rose"]
        },
        "radar": {
            "display_name": "Radar Chart",
            "category": "comparison",
            "method": "generate_radar_chart",
            "data_format": "labels + values (normalized)",
            "supports_multi_series": True,
            "use_cases": ["Multi-attribute comparison", "Skill assessment", "Performance profiles"]
        },
        "area": {
            "display_name": "Area Chart",
            "category": "trend",
            "method": "generate_area_chart",
            "data_format": "labels + values",
            "supports_multi_series": True,
            "use_cases": ["Cumulative totals", "Volume over time", "Trend with magnitude"]
        },
        "area_stacked": {
            "display_name": "Stacked Area Chart",
            "category": "composition",
            "method": "generate_stacked_area_chart",
            "data_format": "labels + multiple datasets",
            "supports_multi_series": True,
            "use_cases": ["Part-to-whole over time", "Revenue by region", "Contribution analysis"]
        },
        "bar_grouped": {
            "display_name": "Grouped Bar Chart",
            "category": "comparison",
            "method": "generate_grouped_bar_chart",
            "data_format": "labels + multiple datasets",
            "supports_multi_series": True,
            "use_cases": ["Multi-series comparison", "Before/after", "Category breakdown"]
        },
        "bar_stacked": {
            "display_name": "Stacked Bar Chart",
            "category": "composition",
            "method": "generate_stacked_bar_chart",
            "data_format": "labels + multiple datasets",
            "supports_multi_series": True,
            "use_cases": ["Part-to-whole by category", "Budget breakdown", "Sales composition"]
        },
        "waterfall": {
            "display_name": "Waterfall Chart",
            "category": "flow",
            "method": "generate_waterfall_chart",
            "data_format": "labels + values (positive/negative)",
            "supports_multi_series": False,
            "use_cases": ["Bridge analysis", "P&L breakdown", "Variance analysis"]
        }
    }

    def __init__(self, theme: str = "professional"):
        """
        Initialize atomic chart generator.

        Args:
            theme: Color theme for charts
        """
        self.theme = theme
        self.synthetic_generator = SyntheticDataGenerator()
        self.chartjs_generator = ChartJSGenerator(theme=theme)
        self.insight_generator = InsightGenerator()

    async def generate(
        self,
        chart_id: str,
        request: AtomicChartRequest,
        enable_editor: bool = False,  # v3.5.1: Add editor support
        presentation_id: str = None   # v3.5.1: Required for editor
    ) -> AtomicChartResponse:
        """
        Generate atomic chart element(s).

        Args:
            chart_id: One of the 14 gold standard chart types
            request: Generation parameters
            enable_editor: If True, adds interactive data editor (v3.5.1)
            presentation_id: Required if enable_editor=True for persistence (v3.5.1)

        Returns:
            AtomicChartResponse with chart HTML and optional insights
        """
        start_time = time.time()

        if chart_id not in GOLD_STANDARD_CHARTS:
            raise ValueError(
                f"Invalid chart_id: {chart_id}. Must be one of: {GOLD_STANDARD_CHARTS}"
            )

        config = self.CHART_CONFIGS[chart_id]
        element_id = f"atomic-chart-{uuid.uuid4().hex[:8]}"

        logger.info(f"Generating atomic {chart_id} chart: {element_id}")

        # 1. Generate synthetic data
        data = self.synthetic_generator.generate(
            chart_type=chart_id,
            narrative=request.narrative,
            num_points=request.num_points
        )

        # 2. Generate chart title
        chart_title = request.chart_title or self._generate_title(chart_id, request.narrative)

        # 3. Generate chart HTML
        # v3.5.1: Pass enable_editor and presentation_id for edit button support
        chart_html = self._generate_chart_html(
            chart_id=chart_id,
            data=data,
            element_id=element_id,
            width=request.width,
            height=request.height,
            chart_title=chart_title,
            enable_editor=enable_editor,
            presentation_id=presentation_id
        )

        # 4. Optionally generate Key Insights
        insights_html = None
        insights_dimensions = None
        if request.include_insights:
            insights_html = await self._generate_insights_html(
                chart_id=chart_id,
                data=data,
                narrative=request.narrative or f"{config['display_name']} analysis",
                height=request.height
            )
            insights_dimensions = ChartDimensions(width=400, height=request.height)

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Generated atomic chart {element_id} in {generation_time_ms}ms")

        return AtomicChartResponse(
            success=True,
            chart_id=chart_id,
            chart_html=chart_html,
            insights_html=insights_html,
            data_used=data,
            chart_title=chart_title,
            generation_time_ms=generation_time_ms,
            synthetic_data=True,
            chart_dimensions=ChartDimensions(width=request.width, height=request.height),
            insights_dimensions=insights_dimensions,
            element_id=element_id
        )

    def _generate_title(self, chart_id: str, narrative: Optional[str]) -> str:
        """Generate appropriate chart title."""
        if narrative:
            # Extract meaningful title from narrative
            words = narrative.split()[:6]
            return " ".join(words).title()

        config = self.CHART_CONFIGS[chart_id]
        return config["display_name"]

    def _generate_chart_html(
        self,
        chart_id: str,
        data: List[Dict[str, Any]],
        element_id: str,
        width: int,
        height: int,
        chart_title: str,
        enable_editor: bool = False,  # v3.5.1: Add editor support
        presentation_id: str = None   # v3.5.1: Required for editor
    ) -> str:
        """
        Generate self-contained chart HTML.

        Returns HTML with embedded Chart.js initialization.

        v3.5.1: Added enable_editor and presentation_id parameters for edit button support.
        """
        config = self.CHART_CONFIGS[chart_id]

        # Transform data to Chart.js format
        chartjs_data = self._transform_to_chartjs_format(chart_id, data)

        # Generate using ChartJSGenerator methods
        method_name = config["method"]
        generator_method = getattr(self.chartjs_generator, method_name, None)

        if generator_method:
            # Call the specific chart method
            chart_html = self._call_generator_method(
                method_name=method_name,
                chart_id_type=chart_id,
                data=chartjs_data,
                element_id=element_id,
                height=height,
                chart_title=chart_title,
                config=config,
                enable_editor=enable_editor,  # v3.5.1: Pass editor params
                presentation_id=presentation_id
            )
        else:
            # Fallback to direct config generation (no editor support)
            chart_html = self._generate_generic_chart(
                chart_id_type=chart_id,
                data=chartjs_data,
                element_id=element_id,
                height=height,
                chart_title=None  # v3.5.1: Slide template provides title
            )

        # Wrap in atomic container
        return self._wrap_in_atomic_container(
            chart_html=chart_html,
            element_id=element_id,
            width=width,
            height=height,
            chart_id=chart_id,
            chart_title=chart_title  # Keep for backward compat but not rendered
        )

    def _call_generator_method(
        self,
        method_name: str,
        chart_id_type: str,
        data: Dict[str, Any],
        element_id: str,
        height: int,
        chart_title: str,
        config: Dict[str, Any],
        enable_editor: bool = False,  # v3.5.1: Add editor support
        presentation_id: str = None   # v3.5.1: Required for editor
    ) -> str:
        """
        Call the appropriate ChartJSGenerator method.

        v3.5.1: Added enable_editor and presentation_id parameters for edit button.
        v3.5.1: Pass chart_title=None to avoid duplicate titles in chart HTML.
        """
        generator = self.chartjs_generator

        # v3.5.1: Don't pass chart_title to avoid duplicate titles
        # The slide template already provides the title slot
        # Map chart types to generator methods
        if method_name == "generate_line_chart":
            return generator.generate_line_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_bar_chart":
            orientation = config.get("orientation", "vertical")
            if orientation == "horizontal":
                return generator.generate_horizontal_bar_chart(
                    data=data,
                    height=height,
                    chart_id=element_id,
                    output_mode="inline_script",
                    chart_title=None,  # v3.5.1: Slide template provides title
                    enable_editor=enable_editor,
                    presentation_id=presentation_id
                )
            else:
                return generator.generate_bar_chart(
                    data=data,
                    height=height,
                    chart_id=element_id,
                    output_mode="inline_script",
                    chart_title=None,  # v3.5.1: Slide template provides title
                    enable_editor=enable_editor,
                    presentation_id=presentation_id
                )
        elif method_name == "generate_pie_chart":
            return generator.generate_pie_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_doughnut_chart":
            return generator.generate_doughnut_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_scatter_chart":
            return generator.generate_scatter_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_bubble_chart":
            return generator.generate_bubble_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_polar_area_chart":
            return generator.generate_polar_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_radar_chart":
            return generator.generate_radar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_area_chart":
            return generator.generate_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_stacked_area_chart":
            return generator.generate_stacked_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_grouped_bar_chart":
            return generator.generate_grouped_bar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_stacked_bar_chart":
            return generator.generate_stacked_bar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        elif method_name == "generate_waterfall_chart":
            return generator.generate_waterfall_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=None,  # v3.5.1: Slide template provides title
                enable_editor=enable_editor,
                presentation_id=presentation_id
            )
        else:
            # Fallback - no editor support for generic charts
            return self._generate_generic_chart(
                chart_id_type=chart_id_type,
                data=data,
                element_id=element_id,
                height=height,
                chart_title=None  # v3.5.1: Slide template provides title
            )

    def _generate_generic_chart(
        self,
        chart_id_type: str,
        data: Dict[str, Any],
        element_id: str,
        height: int,
        chart_title: str
    ) -> str:
        """Fallback: Generate chart using direct Chart.js config."""
        # Map to Chart.js type
        type_map = {
            "line": "line",
            "bar_vertical": "bar",
            "bar_horizontal": "bar",
            "pie": "pie",
            "doughnut": "doughnut",
            "scatter": "scatter",
            "bubble": "bubble",
            "polar_area": "polarArea",
            "radar": "radar",
            "area": "line",
            "area_stacked": "line",
            "bar_grouped": "bar",
            "bar_stacked": "bar",
            "waterfall": "bar"
        }

        chartjs_type = type_map.get(chart_id_type, "bar")

        config = {
            "type": chartjs_type,
            "data": data,
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": True, "position": "top"},
                    "title": {"display": True, "text": chart_title}
                }
            }
        }

        config_json = json.dumps(config)
        js_safe_id = element_id.replace('-', '_')

        return f'''<canvas id="{element_id}"></canvas>
<script>
(function() {{
    const ctx = document.getElementById('{element_id}').getContext('2d');
    new Chart(ctx, {config_json});
}})();
</script>'''

    def _transform_to_chartjs_format(
        self,
        chart_id: str,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Transform synthetic data to Chart.js format."""
        if chart_id in ["scatter", "bubble"]:
            # Scatter/bubble uses {x, y, r} format
            return {
                "labels": [d.get("label", f"Point {i}") for i, d in enumerate(data)],
                "datasets": [{
                    "label": "Data",
                    "data": [
                        {"x": d.get("x", 0), "y": d.get("y", 0), "r": d.get("r", 10)}
                        if "r" in d else {"x": d.get("x", 0), "y": d.get("y", 0)}
                        for d in data
                    ]
                }]
            }
        else:
            # Standard label-value format
            return {
                "labels": [d.get("label", f"Item {i}") for i, d in enumerate(data)],
                "values": [d.get("value", 0) for d in data]
            }

    def _wrap_in_atomic_container(
        self,
        chart_html: str,
        element_id: str,
        width: int,
        height: int,
        chart_id: str,
        chart_title: str = None  # v3.5.1: Made optional, no longer used
    ) -> str:
        """
        Wrap chart HTML in atomic container for frontend positioning.

        v3.5.1: Removed chart-title-bar div - slide template provides title slot.
        The chart_title parameter is kept for backward compatibility but not rendered.
        """
        return f'''<div class="atomic-chart-container"
     data-chart-id="{chart_id}"
     data-element-id="{element_id}"
     style="width: {width}px; height: {height}px; position: relative;">
  <div class="chart-content" style="flex: 1; padding: 12px; height: 100%; box-sizing: border-box;">
    {chart_html}
  </div>
</div>'''

    async def _generate_insights_html(
        self,
        chart_id: str,
        data: List[Dict[str, Any]],
        narrative: str,
        height: int
    ) -> str:
        """Generate Key Insights panel HTML."""
        # Prepare data for insight generator
        insight_data = {
            "labels": [d.get("label", "") for d in data],
            "values": [d.get("value", d.get("y", 0)) for d in data]
        }

        config = self.CHART_CONFIGS[chart_id]

        try:
            # Generate insights using LLM
            explanation = await self.insight_generator.generate_l02_explanation(
                chart_type=config["display_name"],
                data=insight_data,
                narrative=narrative,
                audience="executives"
            )

            # Parse bullet points
            insights = self._parse_insights(explanation)

        except Exception as e:
            logger.warning(f"LLM insight generation failed: {e}, using fallback")
            insights = self._generate_fallback_insights(data, chart_id)

        # Build insights HTML
        insights_list = "\n".join([f'<li class="insight-item">{insight}</li>' for insight in insights])

        return f'''<div class="atomic-insights-container"
     data-chart-id="{chart_id}"
     style="width: 400px; height: {height}px; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
            border-radius: 12px; padding: 24px; box-sizing: border-box;">
  <h4 class="insights-header" style="margin: 0 0 16px 0; font-size: 18px; font-weight: 600; color: #1E40AF;">
    Key Insights
  </h4>
  <ul class="insights-list" style="margin: 0; padding: 0 0 0 20px; color: #1E3A5F; font-size: 14px; line-height: 1.6;">
    {insights_list}
  </ul>
</div>'''

    def _parse_insights(self, explanation: str) -> List[str]:
        """Parse bullet points from LLM explanation."""
        lines = explanation.strip().split('\n')
        insights = []

        for line in lines:
            line = line.strip()
            # Remove bullet markers
            if line.startswith('- ') or line.startswith('• '):
                line = line[2:]
            elif line.startswith('* '):
                line = line[2:]

            if line and len(line) > 10:
                insights.append(line)

        # Ensure we have 3-6 insights
        if len(insights) < 3:
            insights.extend(["Analysis provides valuable insights for decision-making."] * (3 - len(insights)))
        elif len(insights) > 6:
            insights = insights[:6]

        return insights

    def _generate_fallback_insights(
        self,
        data: List[Dict[str, Any]],
        chart_id: str
    ) -> List[str]:
        """Generate fallback insights when LLM fails."""
        config = self.CHART_CONFIGS[chart_id]
        values = [d.get("value", d.get("y", 0)) for d in data]

        if not values:
            return [
                f"The {config['display_name']} displays key metrics for analysis.",
                "Data visualization enables data-driven decision making.",
                "Trends and patterns are clearly visible in this representation."
            ]

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        # Calculate trend
        first_half = sum(values[:len(values)//2]) / max(len(values)//2, 1)
        second_half = sum(values[len(values)//2:]) / max(len(values) - len(values)//2, 1)
        trend = "upward" if second_half > first_half * 1.05 else "downward" if second_half < first_half * 0.95 else "stable"

        return [
            f"The {config['display_name']} shows data ranging from {min_val:.1f} to {max_val:.1f}.",
            f"Average value is {avg_val:.1f} across {len(values)} data points.",
            f"The overall trend appears {trend} based on period comparison.",
            f"This {config['category']} visualization helps identify key patterns.",
            "Consider the data distribution when making strategic decisions."
        ]

    def get_chart_catalog(self) -> List[Dict[str, Any]]:
        """Get catalog of all available atomic chart types."""
        catalog = []

        for chart_id, config in self.CHART_CONFIGS.items():
            catalog.append({
                "id": chart_id,
                "name": config["display_name"],
                "description": f"{config['display_name']} for {', '.join(config['use_cases'][:2])}",
                "category": config["category"],
                "data_format": config["data_format"],
                "min_points": 2,
                "max_points": 50,
                "supports_multi_series": config["supports_multi_series"],
                "example_use_cases": config["use_cases"]
            })

        return catalog
