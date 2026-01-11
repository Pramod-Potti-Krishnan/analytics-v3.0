"""
Atomic Chart Generator for Analytics Microservice v3.7.4

Generates atomic chart elements with synthetic data for frontend positioning.
Each chart is a self-contained HTML element ready for placement.

Key Features:
- 14 gold standard chart types
- Synthetic data generation
- Optional Key Insights panel
- Self-contained HTML with embedded scripts
- Frontend-ready element IDs

v3.7.4 Changes:
- Fixed persistence API URL: now uses absolute URL for cross-origin calls
- Charts embedded in frontend now correctly call analytics service for persistence
- Added visual toast notification when data is persisted to server
- Fixed validators.py for multi-series dict format detection

v3.7.3 Changes:
- Fixed multi-series chart generation (radar, area_stacked, bar_grouped, bar_stacked)
- _transform_to_chartjs_format() now detects dict format with {labels, datasets}
- Multi-series data from formatters passed through directly to ChartJSGenerator
- Fixes "'str' object has no attribute 'get'" error on multi-series charts

v3.6.2 Changes:
- Removed backdrop-filter: blur(4px) which caused grey artifacts in Reveal.js
- Adjusted backdrop opacity from 0.8 to 0.6 for cleaner appearance

v3.6.1 Changes:
- Fixed editor modal z-index (10000 -> 999999) for Reveal.js presentations
- Added pointer-events: auto to modal overlay and dialog
- Changed modal dimensions from 100% to 100vw/100vh

v3.6.0 Changes:
- Removed internal chart titles (external display only)
- LLM-generated insight-style titles: "{takeaway}: {explanation}"
- Title returned in response for slide template to display
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
from settings import settings

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
        request: AtomicChartRequest
    ) -> AtomicChartResponse:
        """
        Generate atomic chart element(s).

        Args:
            chart_id: One of the 14 gold standard chart types
            request: Generation parameters

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

        # 2. Generate chart title (v3.6.0: LLM-generated insight-style title)
        if request.chart_title:
            # User provided explicit title - use it
            chart_title = request.chart_title
        else:
            # Generate LLM-powered insight-style title
            chart_title = await self._generate_insight_title(chart_id, data, request.narrative)

        # 3. Generate chart HTML (v3.6.0: with optional edit button)
        chart_html = self._generate_chart_html(
            chart_id=chart_id,
            data=data,
            element_id=element_id,
            width=request.width,
            height=request.height,
            chart_title=chart_title,
            enable_editor=request.enable_editor,
            presentation_id=request.presentation_id
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
        """
        Generate basic chart title (used only as fallback).

        v3.6.0: This is now only used when LLM insight title generation fails.
        Primary title generation uses _generate_insight_title().
        """
        if narrative:
            # Extract meaningful title from narrative
            words = narrative.split()[:6]
            return " ".join(words).title()

        config = self.CHART_CONFIGS[chart_id]
        return config["display_name"]

    async def _generate_insight_title(
        self,
        chart_id: str,
        data: List[Dict[str, Any]],
        narrative: Optional[str]
    ) -> str:
        """
        Generate LLM-powered insight-style title.

        v3.6.0: Returns format "{3-word takeaway}: {explanation 35-40 chars}"
        Example: "Strong Growth: Revenue increased 22% quarter-over-quarter"

        Args:
            chart_id: Chart type ID
            data: Generated synthetic data
            narrative: User's narrative description

        Returns:
            Insight-style title string
        """
        config = self.CHART_CONFIGS[chart_id]

        # Prepare data in format expected by insight generator
        insight_data = {
            "labels": [d.get("label", f"Item {i}") for i, d in enumerate(data)],
            "values": [d.get("value", d.get("y", 0)) for d in data]
        }

        try:
            title = await self.insight_generator.generate_insight_title(
                chart_type=config["display_name"],
                data=insight_data,
                narrative=narrative
            )
            return title
        except Exception as e:
            logger.warning(f"LLM insight title generation failed: {e}, using fallback")
            return self._generate_title(chart_id, narrative)

    def _generate_chart_html(
        self,
        chart_id: str,
        data: List[Dict[str, Any]],
        element_id: str,
        width: int,
        height: int,
        chart_title: str,
        enable_editor: bool = True,
        presentation_id: Optional[str] = None
    ) -> str:
        """
        Generate self-contained chart HTML.

        v3.6.0: Added enable_editor and presentation_id for edit button support.

        Returns HTML with embedded Chart.js initialization and optional editor.
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
                config=config
            )
        else:
            # Fallback to direct config generation
            chart_html = self._generate_generic_chart(
                chart_id_type=chart_id,
                data=chartjs_data,
                element_id=element_id,
                height=height,
                chart_title=chart_title
            )

        # Wrap in atomic container with optional editor
        return self._wrap_in_atomic_container(
            chart_html=chart_html,
            element_id=element_id,
            width=width,
            height=height,
            chart_id=chart_id,
            chart_title=chart_title,
            enable_editor=enable_editor,
            presentation_id=presentation_id
        )

    def _call_generator_method(
        self,
        method_name: str,
        chart_id_type: str,
        data: Dict[str, Any],
        element_id: str,
        height: int,
        chart_title: str,
        config: Dict[str, Any]
    ) -> str:
        """
        Call the appropriate ChartJSGenerator method.

        v3.6.0: Pass chart_title=None to generator to skip internal title rendering.
        Title is returned in response for external display (insight-style format).
        """
        generator = self.chartjs_generator

        # v3.6.0: No internal titles - title returned in response for external display
        internal_title = None

        # Map chart types to generator methods
        if method_name == "generate_line_chart":
            return generator.generate_line_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_bar_chart":
            orientation = config.get("orientation", "vertical")
            if orientation == "horizontal":
                return generator.generate_horizontal_bar_chart(
                    data=data,
                    height=height,
                    chart_id=element_id,
                    output_mode="inline_script",
                    chart_title=internal_title,
                    responsive_sizing=True  # v3.7.1
                )
            else:
                return generator.generate_bar_chart(
                    data=data,
                    height=height,
                    chart_id=element_id,
                    output_mode="inline_script",
                    chart_title=internal_title,
                    responsive_sizing=True  # v3.7.1
                )
        elif method_name == "generate_pie_chart":
            return generator.generate_pie_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_doughnut_chart":
            return generator.generate_doughnut_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_scatter_chart":
            return generator.generate_scatter_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_bubble_chart":
            return generator.generate_bubble_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_polar_area_chart":
            return generator.generate_polar_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_radar_chart":
            return generator.generate_radar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_area_chart":
            return generator.generate_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_stacked_area_chart":
            return generator.generate_stacked_area_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_grouped_bar_chart":
            return generator.generate_grouped_bar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_stacked_bar_chart":
            return generator.generate_stacked_bar_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        elif method_name == "generate_waterfall_chart":
            return generator.generate_waterfall_chart(
                data=data,
                height=height,
                chart_id=element_id,
                output_mode="inline_script",
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
            )
        else:
            # Fallback
            return self._generate_generic_chart(
                chart_id_type=chart_id_type,
                data=data,
                element_id=element_id,
                height=height,
                chart_title=internal_title,
                responsive_sizing=True  # v3.7.1: Use 100% sizing for atomic elements
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
        data
    ) -> Dict[str, Any]:
        """
        Transform synthetic data to Chart.js format.

        v3.7.3: Now handles both single-series list AND multi-series dict formats.
        Multi-series formatters return: {"labels": [...], "datasets": [{...}, {...}]}
        Single-series formatters return: [{"label": "Q1", "value": 100}, ...]

        ChartJSGenerator expects:
        - Multi-series: {"labels": [...], "datasets": [...]} - passed through as-is
        - Single-series: {"labels": [...], "values": [...]}
        """
        # v3.7.3: If already in Chart.js multi-series format (dict with labels+datasets), pass through
        if isinstance(data, dict):
            if 'labels' in data and 'datasets' in data:
                # Multi-series format - pass through directly for ChartJSGenerator
                # generate_grouped_bar_chart, generate_stacked_bar_chart, etc. expect this format
                logger.debug(f"v3.7.3: Multi-series data detected for {chart_id}, passing through")
                return data  # Return as-is: {labels, datasets}
            elif 'labels' in data and 'values' in data:
                # Already in our expected output format
                return data

        # Handle scatter and bubble charts (point format)
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

        # Standard single-series label-value format (list input)
        if isinstance(data, list):
            return {
                "labels": [d.get("label", f"Item {i}") for i, d in enumerate(data)],
                "values": [d.get("value", 0) for d in data]
            }

        # Fallback for unexpected formats
        logger.warning(f"v3.7.3: Unexpected data format for {chart_id}: {type(data)}")
        return {"labels": [], "values": []}

    def _wrap_in_atomic_container(
        self,
        chart_html: str,
        element_id: str,
        width: int,
        height: int,
        chart_id: str,
        chart_title: str,
        enable_editor: bool = True,
        presentation_id: Optional[str] = None
    ) -> str:
        """
        Wrap chart HTML in atomic container for frontend positioning.

        v3.6.0:
        - Removed internal title bar - title is now returned in response
        - Added edit button and modal for interactive data editing
        """
        js_safe_id = element_id.replace('-', '_')
        modal_id = f"modal-{element_id}"

        # Generate edit button and modal if enabled
        if enable_editor:
            edit_button = self._generate_edit_button(js_safe_id)
            editor_modal = self._generate_editor_modal(
                element_id=element_id,
                js_safe_id=js_safe_id,
                modal_id=modal_id,
                chart_id=chart_id,
                presentation_id=presentation_id
            )
        else:
            edit_button = ""
            editor_modal = ""

        return f'''<div class="atomic-chart-container"
     data-chart-id="{chart_id}"
     data-element-id="{element_id}"
     style="width: {width}px; height: {height}px; position: relative;">
  <div class="chart-content" style="width: 100%; height: 100%;">
    {chart_html}
  </div>
  {edit_button}
</div>
{editor_modal}'''

    def _generate_edit_button(self, js_safe_id: str) -> str:
        """Generate edit button HTML for atomic chart."""
        return f'''<button class="chart-edit-btn"
        onclick="openChartEditor_{js_safe_id}()"
        style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 14px; z-index: 100; transition: all 0.2s; display: flex; align-items: center; gap: 6px;"
        onmouseover="this.style.background='rgba(0,0,0,0.9)'; this.style.transform='scale(1.05)'"
        onmouseout="this.style.background='rgba(0,0,0,0.7)'; this.style.transform='scale(1)'">
    <span style="font-size: 16px;">📊</span> Edit Data
</button>'''

    def _generate_editor_modal(
        self,
        element_id: str,
        js_safe_id: str,
        modal_id: str,
        chart_id: str,
        presentation_id: Optional[str]
    ) -> str:
        """
        Generate complete editor modal with JavaScript for atomic charts.

        v3.6.3: Move modal to document.body to escape Reveal.js stacking context.
        v3.7.2: Chart-type-aware columns for scatter (Label/X/Y) and bubble (Label/X/Y/Radius)
        """
        pres_id = presentation_id or "atomic-standalone"

        # v3.7.2: Chart-type-specific table headers
        th_style = 'background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px;'
        if chart_id == "scatter":
            table_headers = f'''
                            <th style="{th_style} width: 50px;">#</th>
                            <th style="{th_style}">Label</th>
                            <th style="{th_style}">X</th>
                            <th style="{th_style}">Y</th>
                            <th style="{th_style} width: 80px;">Actions</th>
            '''
        elif chart_id == "bubble":
            table_headers = f'''
                            <th style="{th_style} width: 50px;">#</th>
                            <th style="{th_style}">Label</th>
                            <th style="{th_style}">X</th>
                            <th style="{th_style}">Y</th>
                            <th style="{th_style}">Radius</th>
                            <th style="{th_style} width: 80px;">Actions</th>
            '''
        else:
            table_headers = f'''
                            <th style="{th_style} width: 50px;">#</th>
                            <th style="{th_style}">Label</th>
                            <th style="{th_style}">Value</th>
                            <th style="{th_style} width: 80px;">Actions</th>
            '''

        return f'''<!-- Atomic Chart Editor Modal (v3.6.3: moved to document.body to escape Reveal.js stacking context) -->
<div id="{modal_id}" class="chart-editor-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 999999; align-items: center; justify-content: center; pointer-events: auto;">
    <div style="background: white; border-radius: 12px; width: 90%; max-width: 800px; max-height: 90vh; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.3); display: flex; flex-direction: column; pointer-events: auto; position: relative;">

        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e0e0e0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h2 style="margin: 0; font-size: 20px; color: white; display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">📊</span> Edit Chart Data
            </h2>
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: rgba(255,255,255,0.2); border: none; font-size: 24px; color: white; cursor: pointer; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">&times;</button>
        </div>

        <!-- Body -->
        <div style="padding: 24px; overflow-y: auto; flex: 1;">
            <div style="background: #f5f5f5; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px;">
                <p style="margin: 4px 0; font-size: 14px;"><strong>Chart Type:</strong> {chart_id}</p>
                <p style="margin: 4px 0; font-size: 14px;"><strong>Element ID:</strong> {element_id}</p>
            </div>

            <div style="overflow-x: auto; margin-bottom: 16px;">
                <table id="table-{element_id}" style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
{table_headers}
                        </tr>
                    </thead>
                    <tbody id="tbody-{element_id}"></tbody>
                </table>
            </div>

            <button onclick="addRow_{js_safe_id}()" style="background: #f0f0f0; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 18px;">+</span> Add Row
            </button>
        </div>

        <!-- Footer -->
        <div style="display: flex; justify-content: flex-end; gap: 12px; padding: 16px 24px; border-top: 1px solid #e0e0e0; background: #f8f9fa;">
            <button onclick="closeChartEditor_{js_safe_id}()" style="background: white; color: #333; border: 1px solid #ccc; padding: 10px 20px; border-radius: 6px; font-size: 14px; cursor: pointer;">Cancel</button>
            <button onclick="saveChartData_{js_safe_id}()" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 16px;">💾</span> Save & Update
            </button>
        </div>
    </div>
</div>

<!-- JavaScript for Atomic Chart Editor (v3.7.2: Chart-type-aware for scatter/bubble) -->
<script>
(function() {{
    let atomicChart_{js_safe_id} = null;
    const chartType_{js_safe_id} = '{chart_id}';

    function findChartInstance_{js_safe_id}() {{
        // Find the canvas element inside this atomic container
        const container = document.querySelector('[data-element-id="{element_id}"]');
        if (!container) return null;

        const canvas = container.querySelector('canvas');
        if (!canvas) return null;

        // Try to get the Chart.js instance
        return Chart.getChart(canvas);
    }}

    function initEditor_{js_safe_id}() {{
        atomicChart_{js_safe_id} = findChartInstance_{js_safe_id}();
        if (atomicChart_{js_safe_id}) {{
            console.log('✅ Atomic chart editor initialized for {element_id}');
        }}
    }}

    window.openChartEditor_{js_safe_id} = function() {{
        if (!atomicChart_{js_safe_id}) {{
            atomicChart_{js_safe_id} = findChartInstance_{js_safe_id}();
        }}

        if (!atomicChart_{js_safe_id}) {{
            alert('Chart not ready yet. Please wait a moment and try again.');
            return;
        }}

        // Populate table with current data
        const tbody = document.getElementById('tbody-{element_id}');
        tbody.innerHTML = '';

        const inputStyle = 'width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;';
        const tdStyle = 'padding: 8px 12px; border-bottom: 1px solid #e0e0e0;';
        const deleteBtn = '<button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>';

        // v3.7.2: Chart-type-specific data extraction
        if (chartType_{js_safe_id} === 'scatter') {{
            const data = atomicChart_{js_safe_id}.data.datasets[0]?.data || [];
            data.forEach((point, index) => {{
                const label = point.label || `Point ${{index + 1}}`;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="${{tdStyle}}">${{index + 1}}</td>
                    <td style="${{tdStyle}}"><input type="text" class="label-input" value="${{label}}" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="x-input" value="${{point.x || 0}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="y-input" value="${{point.y || 0}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}">${{deleteBtn}}</td>
                `;
                tbody.appendChild(row);
            }});
        }} else if (chartType_{js_safe_id} === 'bubble') {{
            const data = atomicChart_{js_safe_id}.data.datasets[0]?.data || [];
            data.forEach((point, index) => {{
                const label = point.label || `Point ${{index + 1}}`;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="${{tdStyle}}">${{index + 1}}</td>
                    <td style="${{tdStyle}}"><input type="text" class="label-input" value="${{label}}" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="x-input" value="${{point.x || 0}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="y-input" value="${{point.y || 0}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="r-input" value="${{point.r || 15}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}">${{deleteBtn}}</td>
                `;
                tbody.appendChild(row);
            }});
        }} else {{
            // Standard label/value charts
            const labels = atomicChart_{js_safe_id}.data.labels || [];
            const values = atomicChart_{js_safe_id}.data.datasets[0]?.data || [];

            labels.forEach((label, index) => {{
                const value = typeof values[index] === 'object' ? values[index].y || 0 : values[index];
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="${{tdStyle}}">${{index + 1}}</td>
                    <td style="${{tdStyle}}"><input type="text" class="label-input" value="${{label}}" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="value-input" value="${{value}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}">${{deleteBtn}}</td>
                `;
                tbody.appendChild(row);
            }});
        }}

        // v3.6.3: Move modal to document.body to escape Reveal.js transform stacking context
        // This ensures the modal covers the entire viewport, not just the slide container
        const modal = document.getElementById('{modal_id}');
        if (modal.parentElement !== document.body) {{
            document.body.appendChild(modal);
        }}
        modal.style.display = 'flex';
    }};

    window.closeChartEditor_{js_safe_id} = function() {{
        document.getElementById('{modal_id}').style.display = 'none';
    }};

    window.addRow_{js_safe_id} = function() {{
        const tbody = document.getElementById('tbody-{element_id}');
        const rowCount = tbody.querySelectorAll('tr').length;
        const row = document.createElement('tr');
        const inputStyle = 'width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;';
        const tdStyle = 'padding: 8px 12px; border-bottom: 1px solid #e0e0e0;';
        const deleteBtn = '<button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">🗑️</button>';

        // v3.7.2: Chart-type-specific new row templates
        if (chartType_{js_safe_id} === 'scatter') {{
            row.innerHTML = `
                <td style="${{tdStyle}}">${{rowCount + 1}}</td>
                <td style="${{tdStyle}}"><input type="text" class="label-input" value="New Point" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="x-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="y-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}">${{deleteBtn}}</td>
            `;
        }} else if (chartType_{js_safe_id} === 'bubble') {{
            row.innerHTML = `
                <td style="${{tdStyle}}">${{rowCount + 1}}</td>
                <td style="${{tdStyle}}"><input type="text" class="label-input" value="New Point" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="x-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="y-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="r-input" value="15" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}">${{deleteBtn}}</td>
            `;
        }} else {{
            row.innerHTML = `
                <td style="${{tdStyle}}">${{rowCount + 1}}</td>
                <td style="${{tdStyle}}"><input type="text" class="label-input" value="New Item" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="value-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}">${{deleteBtn}}</td>
            `;
        }}
        tbody.appendChild(row);
        renumberRows_{js_safe_id}();
    }};

    window.deleteRow_{js_safe_id} = function(btn) {{
        btn.closest('tr').remove();
        renumberRows_{js_safe_id}();
    }};

    function renumberRows_{js_safe_id}() {{
        const rows = document.querySelectorAll('#tbody-{element_id} tr');
        rows.forEach((row, index) => {{
            row.querySelector('td:first-child').textContent = index + 1;
        }});
    }}

    window.saveChartData_{js_safe_id} = function() {{
        // Collect data from table
        const rows = document.querySelectorAll('#tbody-{element_id} tr');

        // v3.7.2: Chart-type-specific save logic
        if (chartType_{js_safe_id} === 'scatter') {{
            const newData = [];
            rows.forEach(row => {{
                const label = row.querySelector('.label-input').value;
                const x = parseFloat(row.querySelector('.x-input').value) || 0;
                const y = parseFloat(row.querySelector('.y-input').value) || 0;
                newData.push({{ label, x, y }});
            }});
            atomicChart_{js_safe_id}.data.datasets[0].data = newData;
        }} else if (chartType_{js_safe_id} === 'bubble') {{
            const newData = [];
            rows.forEach(row => {{
                const label = row.querySelector('.label-input').value;
                const x = parseFloat(row.querySelector('.x-input').value) || 0;
                const y = parseFloat(row.querySelector('.y-input').value) || 0;
                const r = parseFloat(row.querySelector('.r-input').value) || 15;
                newData.push({{ label, x, y, r }});
            }});
            atomicChart_{js_safe_id}.data.datasets[0].data = newData;
        }} else {{
            // Standard label/value save
            const newLabels = [];
            const newValues = [];
            rows.forEach(row => {{
                const label = row.querySelector('.label-input').value;
                const value = parseFloat(row.querySelector('.value-input').value) || 0;
                newLabels.push(label);
                newValues.push(value);
            }});
            atomicChart_{js_safe_id}.data.labels = newLabels;
            atomicChart_{js_safe_id}.data.datasets[0].data = newValues;
        }}

        atomicChart_{js_safe_id}.update();

        // v3.7.3: Persist to server if presentation context available
        const presentationId = window.currentPresentationId ||
            (window.location.pathname.match(/\/p\/([^\/]+)/) || [])[1] ||
            '';

        if (presentationId) {{
            // Build persistence payload based on chart type
            let payload = {{
                chart_id: '{element_id}',
                presentation_id: presentationId,
                chart_type: chartType_{js_safe_id}
            }};

            if (chartType_{js_safe_id} === 'scatter') {{
                payload.data = atomicChart_{js_safe_id}.data.datasets[0].data.map(p => ({{
                    x: p.x, y: p.y, label: p.label || ''
                }}));
            }} else if (chartType_{js_safe_id} === 'bubble') {{
                payload.data = atomicChart_{js_safe_id}.data.datasets[0].data.map(p => ({{
                    x: p.x, y: p.y, r: p.r, label: p.label || ''
                }}));
            }} else {{
                payload.labels = atomicChart_{js_safe_id}.data.labels;
                payload.values = atomicChart_{js_safe_id}.data.datasets[0].data;
            }}

            // v3.7.4: Call persistence API with absolute URL (cross-origin from frontend)
            const analyticsServiceUrl = '{settings.analytics_service_url}';
            fetch(analyticsServiceUrl + '/api/charts/update-data', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(payload)
            }})
            .then(r => r.json())
            .then(result => {{
                console.log('Chart data persisted:', result.persisted ? 'success' : 'client-only');
                if (result.persisted) {{
                    // Update toast to show persistence success
                    const persistToast = document.createElement('div');
                    persistToast.innerHTML = '💾 Changes saved to server';
                    persistToast.style.cssText = 'position: fixed; top: 70px; right: 20px; background: #10B981; color: white; padding: 12px 20px; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 13px;';
                    document.body.appendChild(persistToast);
                    setTimeout(() => persistToast.remove(), 2500);
                }}
            }})
            .catch(err => console.warn('Persistence failed (client-only):', err));
        }}

        // Show success message
        const toast = document.createElement('div');
        toast.innerHTML = '✅ Chart updated successfully!';
        toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 14px; font-weight: 500;';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);

        // Close modal
        closeChartEditor_{js_safe_id}();
    }};

    // Initialize when DOM ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(initEditor_{js_safe_id}, 500);
        }});
    }} else {{
        setTimeout(initEditor_{js_safe_id}, 500);
    }}
}})();
</script>'''

    async def _generate_insights_html(
        self,
        chart_id: str,
        data,
        narrative: str,
        height: int
    ) -> str:
        """Generate Key Insights panel HTML."""
        # v3.7.4: Handle multi-series dict format {labels, datasets}
        if isinstance(data, dict) and "labels" in data and "datasets" in data:
            # Multi-series format: extract labels and flatten values from first dataset
            insight_data = {
                "labels": data["labels"],
                "values": data["datasets"][0].get("data", []) if data["datasets"] else []
            }
        else:
            # Standard list of dicts format
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
        data,
        chart_id: str
    ) -> List[str]:
        """Generate fallback insights when LLM fails."""
        config = self.CHART_CONFIGS[chart_id]

        # v3.7.4: Handle multi-series dict format {labels, datasets}
        if isinstance(data, dict) and "labels" in data and "datasets" in data:
            # Multi-series format: use values from first dataset
            values = data["datasets"][0].get("data", []) if data["datasets"] else []
        else:
            # Standard list of dicts format
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
