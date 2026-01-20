"""
Atomic Chart Generator for Analytics Microservice v3.7.32

Generates atomic chart elements with synthetic data for frontend positioning.
Each chart is a self-contained HTML element ready for placement.

Key Features:
- 14 gold standard chart types
- Synthetic data generation
- Optional Key Insights panel
- Self-contained HTML with embedded scripts
- Deterministic element IDs for persistence
- Auto-loads saved edits on chart initialization
- Reveal.js slide navigation persistence support
- Multi-series, waterfall, scatter/bubble persistence
- Editable series names in multi-series charts
- Configurable title visibility (show_title)
- Stretch-to-fit container with 10px padding

v3.7.32 Changes:
- FIX: saveChartData now finds table elements in parent document when modal is moved
- Table rows and series inputs are now correctly queried from modalDoc
- Fixes empty labels/values arrays causing 422 server error on save

v3.7.31 Changes:
- FIX: Expose chart editor functions to parent window when modal is moved
- Save, Cancel, Add Row, Delete Row buttons now work when modal is in parent document
- Functions are registered on parent window so onclick handlers can find them

v3.7.30 Changes:
- FIX: Modal now escapes iframe viewport constraint by appending to parent.document.body
- FIX: Presentation ID now correctly extracted from parent window for iframe context
- Charts rendered inside iframes (via srcdoc) now properly access parent's currentPresentationId
- Modal covers full slide instead of being constrained to small chart container
- Data persistence now works correctly in text-labs and other iframe contexts
- Enhanced debug logging to show iframe context and parent window info

v3.7.19 Changes:
- FIX: Canvas ID collision with container (v7.5.23 compatibility)
- Generic fallback now uses canvas-{element_id} instead of {element_id}
- Fixes: getElementById finding container div instead of canvas element
- Charts now render correctly when element-manager wraps them in containers

v3.7.18 Changes:
- FEATURE: Stretch-to-fit styling for chart containers (like tables)
- Container now uses 100% width/height instead of fixed pixels
- Added 10px padding on all sides for consistent margins
- Added box-sizing: border-box so padding is included in dimensions
- Added overflow: hidden to clip content that doesn't fit
- Charts now properly fill their container and resize responsively

v3.7.17 Changes:
- FIX: Waterfall chart colors now persist across navigation and refresh
- Save waterfall data to localStorage on editor save for immediate reload
- Check localStorage FIRST in reloadSavedData (sync) before server fetch (async)
- Fixes timing issue where colors reverted when navigating away and back
- Colors are recalculated from start/end comparison (green=increase, pink=decrease)

v3.7.16 Changes:
- FIX: Title now appears ABOVE chart instead of on the side
- Container uses flex layout (display: flex; flex-direction: column)
- Chart content uses flex: 1 to fill remaining space
- Title styling improved: single-line, truncates if too long
- Enhanced debug logging for waterfall persistence troubleshooting

v3.7.15 Changes:
- FEATURE: Added show_title parameter for chart title visibility control
- When show_title=True (default), title is rendered above the chart
- When show_title=False, title is omitted from HTML but still in response
- Title uses styled <h3> element with professional typography

v3.7.14 Changes:
- FEATURE: Waterfall chart persistence now uses dedicated waterfall_data format
- Save payload sends {waterfall_data: [{label, start, end}, ...]}
- Load logic checks for waterfall_data first, with fallback for old format
- Fixes: Waterfall edits not persisting (TypeError on [[start,end]] format)

v3.7.11 Changes:
- FEATURE: Editable series names in multi-series editor header
- Series column headers are now input fields (click to edit)
- Updated series names are saved to chart and persisted
- Chart legend updates when series names change

v3.7.10 Changes:
- FEATURE: Multi-series editor for area_stacked, bar_grouped, bar_stacked
- FEATURE: Waterfall editor with Start/End columns
- Dynamic column headers based on dataset series names
- Multi-series save/load with datasets format
- Waterfall save/load with [[start, end], ...] format

v3.7.9 Changes:
- CRITICAL FIX: reloadSavedData now handles scatter/bubble x/y/r format
- Scatter/bubble data persists correctly with coordinate format
- Detects chart type and applies appropriate data structure
- Fixes: Scatter/bubble edits not persisting on navigation/refresh

v3.7.8 Changes:
- CRITICAL FIX: Added Reveal.js slidechanged event listener for navigation persistence
- Refactored loadSavedData into reloadSavedData function (reusable)
- Chart data now reloads when navigating back to a slide in Reveal.js
- Fixes: Edited data showing as original when navigating fwd/backward

v3.7.7 Changes:
- CRITICAL FIX: openChartEditor now always re-finds chart instance (fixes stale instance bug)
- CRITICAL FIX: loadSavedData uses retry with exponential backoff (fixes timing issues)
- CRITICAL FIX: Array length validation for labels/values (fixes empty array bug)
- Fixes: Second save failing, data not loading on revisit

v3.7.6 Changes:
- Added loadSavedData function that runs on chart initialization
- Fetches saved edits from /api/charts/get-data/{pres_id}/{chart_id}
- If saved data exists, updates Chart.js instance with persisted values
- Fixes issue where edited data was lost on slide navigation

v3.7.5 Changes:
- BREAKING: presentation_id and slide_id are now REQUIRED
- Deterministic chart IDs: chart-{pres_id}-{slide_id}-{chart_type}-{index}
- Enables proper persistence via Layout Service (matches V2 pattern)
- Charts are no longer regenerated on slide revisit

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

        # v3.7.5: Deterministic chart ID for persistence
        # Format: chart-{presentation_id}-{slide_id}-{chart_type}-{index}
        element_id = f"chart-{request.presentation_id}-{request.slide_id}-{chart_id}-{request.chart_index}"

        logger.info(f"Generating atomic {chart_id} chart: {element_id}")

        # 1. Use provided data or generate synthetic data
        # v3.8.0: Support explicit data for data ingestion use case
        if request.data is not None and len(request.data) > 0:
            data = request.data
            logger.info(f"Using provided data with {len(data)} points")
        else:
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

        # 3. Generate chart HTML (v3.6.0: with optional edit button, v3.7.16: with show_title + flex layout)
        chart_html = self._generate_chart_html(
            chart_id=chart_id,
            data=data,
            element_id=element_id,
            width=request.width,
            height=request.height,
            chart_title=chart_title,
            enable_editor=request.enable_editor,
            presentation_id=request.presentation_id,
            show_title=request.show_title
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

        # v3.8.0: Determine if data was synthetic or provided
        used_synthetic = request.data is None or len(request.data) == 0

        return AtomicChartResponse(
            success=True,
            chart_id=chart_id,
            chart_html=chart_html,
            insights_html=insights_html,
            data_used=data,
            chart_title=chart_title,
            generation_time_ms=generation_time_ms,
            synthetic_data=used_synthetic,
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
        data,
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

        # v3.7.4: Handle multi-series dict format {labels, datasets}
        if isinstance(data, dict) and "labels" in data and "datasets" in data:
            # Multi-series format
            insight_data = {
                "labels": data["labels"],
                "values": data["datasets"][0].get("data", []) if data["datasets"] else []
            }
        else:
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
        presentation_id: Optional[str] = None,
        show_title: bool = True
    ) -> str:
        """
        Generate self-contained chart HTML.

        v3.7.16: Flex layout for title positioning, enhanced styling.
        v3.7.15: Added show_title for conditional title rendering.
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
            presentation_id=presentation_id,
            show_title=show_title
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

        # v7.5.23: Use canvas-{element_id} to avoid ID collision with container
        return f'''<canvas id="canvas-{element_id}"></canvas>
<script>
(function() {{
    const ctx = document.getElementById('canvas-{element_id}').getContext('2d');
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
        presentation_id: Optional[str] = None,
        show_title: bool = True
    ) -> str:
        """
        Wrap chart HTML in atomic container for frontend positioning.

        v3.7.16:
        - FIX: Title positioning - now uses flex layout to stack title above chart
        - Container: display: flex; flex-direction: column
        - Chart content: flex: 1; min-height: 0 (fills remaining space)
        - Title: single-line with truncation (white-space: nowrap, text-overflow: ellipsis)

        v3.7.15:
        - Added show_title parameter to conditionally render title above chart
        - When show_title=True, displays title in styled <h3> element
        - When show_title=False, title is omitted but still returned in response

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

        # v3.7.16: Conditionally render title with flex-safe styling
        title_html = ""
        if show_title and chart_title:
            title_html = f'''<h3 style="margin: 30px 0 30px 50px; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 21px; font-weight: 600; color: #1E3A5F; line-height: 1.2; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0;">{chart_title}</h3>'''  # v7.5.28: 50px left indent to align with Y-axis, 21px font, 30px bottom margin

        # v3.7.18: Stretch-to-fit with padding (like tables)
        # - Uses 100% width/height instead of fixed pixels
        # - v7.5.28: 30px left padding for symmetry with right side, 10px top/right/bottom
        # - box-sizing: border-box so padding is included in dimensions
        # - overflow: hidden to clip content that doesn't fit
        return f'''<div class="atomic-chart-container"
     data-chart-id="{chart_id}"
     data-element-id="{element_id}"
     style="width: 100%; height: 100%; padding: 10px 10px 10px 30px; box-sizing: border-box; position: relative; display: flex; flex-direction: column; overflow: hidden;">
  {title_html}
  <div class="chart-content" style="width: 100%; flex: 1; min-height: 0; overflow: hidden;">
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
    <span style="font-size: 16px;">&#128202;</span> Edit Data
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

        # v3.7.10: Chart-type-specific table headers (multi-series headers built dynamically in JS)
        th_style = 'background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px;'
        multi_series_charts = ['area_stacked', 'bar_grouped', 'bar_stacked']

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
        elif chart_id == "waterfall":
            table_headers = f'''
                            <th style="{th_style} width: 50px;">#</th>
                            <th style="{th_style}">Label</th>
                            <th style="{th_style}">Start</th>
                            <th style="{th_style}">End</th>
                            <th style="{th_style} width: 80px;">Actions</th>
            '''
        elif chart_id in multi_series_charts:
            # v3.7.10: Multi-series headers built dynamically - placeholder row updated by JS
            table_headers = f'''
                            <th style="{th_style} width: 50px;">#</th>
                            <th style="{th_style}">Label</th>
                            <!-- Series columns inserted dynamically by JavaScript -->
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
                <span style="font-size: 24px;">&#128202;</span> Edit Chart Data
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
                <span style="font-size: 16px;">&#128190;</span> Save &amp; Update
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
        // v3.7.7: Always re-find chart instance (previous may be stale after navigation)
        atomicChart_{js_safe_id} = findChartInstance_{js_safe_id}();

        if (!atomicChart_{js_safe_id}) {{
            alert('Chart not ready yet. Please wait a moment and try again.');
            return;
        }}

        // Populate table with current data
        const tbody = document.getElementById('tbody-{element_id}');
        tbody.innerHTML = '';

        const inputStyle = 'width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;';
        const tdStyle = 'padding: 8px 12px; border-bottom: 1px solid #e0e0e0;';
        const deleteBtn = '<button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">&#128465;</button>';

        // v3.7.10: Chart-type-specific data extraction with multi-series and waterfall support
        const multiSeriesCharts = ['area_stacked', 'bar_grouped', 'bar_stacked'];
        const isMultiSeries = multiSeriesCharts.includes(chartType_{js_safe_id});

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
        }} else if (chartType_{js_safe_id} === 'waterfall') {{
            // v3.7.18: Waterfall with Start/End columns using barDirections for semantic meaning
            const labels = atomicChart_{js_safe_id}.data.labels || [];
            const data = atomicChart_{js_safe_id}.data.datasets[0]?.data || [];

            // v3.7.18: Get barDirections to determine semantic Start/End
            const cfg = atomicChart_{js_safe_id}.config;
            const directions = cfg.barDirections || cfg._config?.barDirections || [];

            labels.forEach((label, index) => {{
                const value = data[index];
                const direction = directions[index] || 'positive';

                // v3.7.18: Extract Start/End based on direction for intuitive editing
                // Positive: Start < End (going up)
                // Negative: Start > End (going down)
                // Total: Start = 0
                let start, end;
                if (Array.isArray(value)) {{
                    if (direction === 'negative') {{
                        // Negative bar: swap so Start > End (intuitive for decrease)
                        start = value[1];  // Higher value
                        end = value[0];    // Lower value
                    }} else {{
                        // Positive or Total: keep as-is
                        start = value[0];
                        end = value[1];
                    }}
                }} else {{
                    start = 0;
                    end = typeof value === 'number' ? value : 0;
                }}

                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="${{tdStyle}}">${{index + 1}}</td>
                    <td style="${{tdStyle}}"><input type="text" class="label-input" value="${{label}}" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="start-input" value="${{start}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}"><input type="number" class="end-input" value="${{end}}" step="any" style="${{inputStyle}}"></td>
                    <td style="${{tdStyle}}">${{deleteBtn}}</td>
                `;
                tbody.appendChild(row);
            }});
        }} else if (isMultiSeries) {{
            // v3.7.10: Multi-series charts (area_stacked, bar_grouped, bar_stacked)
            const labels = atomicChart_{js_safe_id}.data.labels || [];
            const datasets = atomicChart_{js_safe_id}.data.datasets || [];

            // Store series names for later use
            window.seriesNames_{js_safe_id} = datasets.map((ds, i) => ds.label || `Series ${{i + 1}}`);

            // v3.7.11: Rebuild table header with EDITABLE series name inputs
            const thead = document.querySelector('#table-{element_id} thead tr');
            const thStyle = 'background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #dee2e6; font-size: 14px;';
            const seriesInputStyle = 'width: 100%; padding: 6px 8px; border: 1px solid #667eea; border-radius: 4px; font-size: 13px; font-weight: 600; background: #f0f4ff; color: #333;';
            let headerHTML = `<th style="${{thStyle}} width: 50px;">#</th><th style="${{thStyle}}">Label</th>`;
            window.seriesNames_{js_safe_id}.forEach((name, idx) => {{
                headerHTML += `<th style="${{thStyle}}"><input type="text" class="series-name-input" data-series-idx="${{idx}}" value="${{name}}" style="${{seriesInputStyle}}" title="Click to edit series name"></th>`;
            }});
            headerHTML += `<th style="${{thStyle}} width: 80px;">Actions</th>`;
            thead.innerHTML = headerHTML;

            // Populate data rows
            labels.forEach((label, rowIndex) => {{
                const row = document.createElement('tr');
                let rowHTML = `
                    <td style="${{tdStyle}}">${{rowIndex + 1}}</td>
                    <td style="${{tdStyle}}"><input type="text" class="label-input" value="${{label}}" style="${{inputStyle}}"></td>
                `;
                datasets.forEach((ds, seriesIndex) => {{
                    const value = ds.data[rowIndex] !== undefined ? ds.data[rowIndex] : 0;
                    rowHTML += `<td style="${{tdStyle}}"><input type="number" class="series-input" data-series="${{seriesIndex}}" value="${{value}}" step="any" style="${{inputStyle}}"></td>`;
                }});
                rowHTML += `<td style="${{tdStyle}}">${{deleteBtn}}</td>`;
                row.innerHTML = rowHTML;
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

        // v3.7.30: Move modal to PARENT document.body to escape iframe viewport constraint
        // Charts are rendered inside iframes, so position:fixed is relative to iframe viewport, not parent page
        const modal = document.getElementById('{modal_id}');
        const isInIframe = (window.parent && window.parent !== window);
        const targetBody = isInIframe ? window.parent.document.body : document.body;

        if (modal.parentElement !== targetBody) {{
            targetBody.appendChild(modal);
        }}

        // v3.7.31: Expose functions to parent window so onclick handlers work when modal is in parent
        if (isInIframe) {{
            window.parent.saveChartData_{js_safe_id} = window.saveChartData_{js_safe_id};
            window.parent.closeChartEditor_{js_safe_id} = window.closeChartEditor_{js_safe_id};
            window.parent.addRow_{js_safe_id} = window.addRow_{js_safe_id};
            window.parent.deleteRow_{js_safe_id} = window.deleteRow_{js_safe_id};
            console.log('[v3.7.31] Exposed chart editor functions to parent window for modal:', '{modal_id}');
        }}

        modal.style.display = 'flex';
    }};

    // v3.7.30: Look for modal in parent document where it was moved
    window.closeChartEditor_{js_safe_id} = function() {{
        const targetDoc = (window.parent && window.parent !== window)
            ? window.parent.document
            : document;
        const modal = targetDoc.getElementById('{modal_id}') || document.getElementById('{modal_id}');
        if (modal) {{
            modal.style.display = 'none';
        }}
    }};

    window.addRow_{js_safe_id} = function() {{
        const tbody = document.getElementById('tbody-{element_id}');
        const rowCount = tbody.querySelectorAll('tr').length;
        const row = document.createElement('tr');
        const inputStyle = 'width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;';
        const tdStyle = 'padding: 8px 12px; border-bottom: 1px solid #e0e0e0;';
        const deleteBtn = '<button onclick="deleteRow_{js_safe_id}(this)" style="background: #ff4444; color: white; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; font-size: 14px;">&#128465;</button>';

        // v3.7.10: Chart-type-specific new row templates with multi-series and waterfall
        const multiSeriesCharts = ['area_stacked', 'bar_grouped', 'bar_stacked'];
        const isMultiSeries = multiSeriesCharts.includes(chartType_{js_safe_id});

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
        }} else if (chartType_{js_safe_id} === 'waterfall') {{
            row.innerHTML = `
                <td style="${{tdStyle}}">${{rowCount + 1}}</td>
                <td style="${{tdStyle}}"><input type="text" class="label-input" value="New Item" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="start-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}"><input type="number" class="end-input" value="0" step="any" style="${{inputStyle}}"></td>
                <td style="${{tdStyle}}">${{deleteBtn}}</td>
            `;
        }} else if (isMultiSeries) {{
            // Multi-series: add cells for each series
            const seriesNames = window.seriesNames_{js_safe_id} || [];
            let rowHTML = `
                <td style="${{tdStyle}}">${{rowCount + 1}}</td>
                <td style="${{tdStyle}}"><input type="text" class="label-input" value="New Item" style="${{inputStyle}}"></td>
            `;
            seriesNames.forEach((name, idx) => {{
                rowHTML += `<td style="${{tdStyle}}"><input type="number" class="series-input" data-series="${{idx}}" value="0" step="any" style="${{inputStyle}}"></td>`;
            }});
            rowHTML += `<td style="${{tdStyle}}">${{deleteBtn}}</td>`;
            row.innerHTML = rowHTML;
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

    window.saveChartData_{js_safe_id} = async function() {{
        // v3.7.32: Find table in correct document (modal may be in parent document)
        const isInIframe = (window.parent && window.parent !== window);
        const modalDoc = isInIframe ? window.parent.document : document;
        const rows = modalDoc.querySelectorAll('#tbody-{element_id} tr');
        console.log('[v3.7.32] Save: Found', rows.length, 'rows in', isInIframe ? 'parent document' : 'current document');

        // v3.7.10: Chart-type-specific save logic with multi-series and waterfall
        const multiSeriesCharts = ['area_stacked', 'bar_grouped', 'bar_stacked'];
        const isMultiSeries = multiSeriesCharts.includes(chartType_{js_safe_id});

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
        }} else if (chartType_{js_safe_id} === 'waterfall') {{
            // v3.7.16: Waterfall with Start/End columns - recalculate colors and directions
            const newLabels = [];
            const floatingBars = [];
            const newColors = [];
            const newDirections = [];
            const rowCount = rows.length;

            rows.forEach((row, i) => {{
                const label = row.querySelector('.label-input').value;
                const start = parseFloat(row.querySelector('.start-input').value) || 0;
                const end = parseFloat(row.querySelector('.end-input').value) || 0;
                newLabels.push(label);

                // Floating bar format: [min, max] for Chart.js
                floatingBars.push([Math.min(start, end), Math.max(start, end)]);

                // Determine direction from start vs end comparison
                const isIncrease = end > start;
                const isTotal = (i === 0 || i === rowCount - 1) && start === 0;

                if (isTotal) {{
                    newColors.push('#93C5FD'); // Blue for totals
                    newDirections.push('total');
                }} else if (isIncrease) {{
                    newColors.push('#A7F3D0'); // Green for increases
                    newDirections.push('positive');
                }} else {{
                    newColors.push('#FBCFE8'); // Pink for decreases
                    newDirections.push('negative');
                }}
            }});

            // Update chart data, colors, and directions
            atomicChart_{js_safe_id}.data.labels = newLabels;
            atomicChart_{js_safe_id}.data.datasets[0].data = floatingBars;
            atomicChart_{js_safe_id}.data.datasets[0].backgroundColor = newColors;
            atomicChart_{js_safe_id}.data.datasets[0].borderColor = newColors;

            // Update barDirections for the formatter
            if (atomicChart_{js_safe_id}.config) {{
                atomicChart_{js_safe_id}.config.barDirections = newDirections;
                if (atomicChart_{js_safe_id}.config._config) {{
                    atomicChart_{js_safe_id}.config._config.barDirections = newDirections;
                }}
            }}

            console.log('🌊 Waterfall save - Colors:', newColors, 'Directions:', newDirections);
        }} else if (isMultiSeries) {{
            // v3.7.11: Multi-series charts with editable series names
            const newLabels = [];
            const seriesData = [];
            const newSeriesNames = [];
            const numSeries = window.seriesNames_{js_safe_id}?.length || 0;

            // v3.7.11: Collect updated series names from header inputs
            // v3.7.32: Use modalDoc (modal may be in parent document)
            const seriesNameInputs = modalDoc.querySelectorAll('#table-{element_id} thead .series-name-input');
            seriesNameInputs.forEach(input => {{
                newSeriesNames.push(input.value.trim() || `Series ${{newSeriesNames.length + 1}}`);
            }});

            // Update stored series names
            window.seriesNames_{js_safe_id} = newSeriesNames;

            // Initialize series data arrays
            for (let i = 0; i < numSeries; i++) {{
                seriesData.push([]);
            }}

            rows.forEach(row => {{
                const label = row.querySelector('.label-input').value;
                newLabels.push(label);

                const seriesInputs = row.querySelectorAll('.series-input');
                seriesInputs.forEach((input, idx) => {{
                    const value = parseFloat(input.value) || 0;
                    if (seriesData[idx]) {{
                        seriesData[idx].push(value);
                    }}
                }});
            }});

            // Update chart labels and data
            atomicChart_{js_safe_id}.data.labels = newLabels;
            seriesData.forEach((data, idx) => {{
                if (atomicChart_{js_safe_id}.data.datasets[idx]) {{
                    atomicChart_{js_safe_id}.data.datasets[idx].data = data;
                    // v3.7.11: Also update series names in chart
                    if (newSeriesNames[idx]) {{
                        atomicChart_{js_safe_id}.data.datasets[idx].label = newSeriesNames[idx];
                    }}
                }}
            }});
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

        // v3.7.30: Check parent window first (for iframe context) then fallback to current window
        const parentWindow = (window.parent && window.parent !== window) ? window.parent : window;
        const presentationId = parentWindow.currentPresentationId ||
            window.currentPresentationId ||
            (parentWindow.location.pathname.match(/\/p\/([^\/]+)/) || [])[1] ||
            (window.location.pathname.match(/\/p\/([^\/]+)/) || [])[1] ||
            '';
        console.log('[v3.7.30] Save: presentationId resolved to:', presentationId);

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
            }} else if (chartType_{js_safe_id} === 'waterfall') {{
                // v3.7.14: Waterfall persistence with dedicated waterfall_data format
                payload.waterfall_data = atomicChart_{js_safe_id}.data.labels.map((label, idx) => {{
                    const dataPoint = atomicChart_{js_safe_id}.data.datasets[0].data[idx];
                    return {{
                        label: label,
                        start: Array.isArray(dataPoint) ? dataPoint[0] : 0,
                        end: Array.isArray(dataPoint) ? dataPoint[1] : dataPoint
                    }};
                }});

                // v3.7.17: Also save to localStorage for immediate reload on navigation
                const storageKey = 'chartData_' + presentationId + '_' + '{element_id}';
                localStorage.setItem(storageKey, JSON.stringify({{
                    waterfall_data: payload.waterfall_data
                }}));
                console.log('💾 [v3.7.17] Waterfall data saved to localStorage:', storageKey);
            }} else if (isMultiSeries) {{
                // v3.7.10: Multi-series persistence
                payload.labels = atomicChart_{js_safe_id}.data.labels;
                payload.datasets = atomicChart_{js_safe_id}.data.datasets.map(ds => ({{
                    label: ds.label,
                    data: ds.data
                }}));
            }} else {{
                payload.labels = atomicChart_{js_safe_id}.data.labels;
                payload.values = atomicChart_{js_safe_id}.data.datasets[0].data;
            }}

            // v3.7.30: Enhanced persistence API call with blocking save (don't close modal until confirmed)
            const analyticsServiceUrl = '{settings.analytics_service_url}';
            console.log('[v3.7.30] Persistence payload:', JSON.stringify(payload, null, 2));
            console.log('[v3.7.30] Analytics Service URL:', analyticsServiceUrl);

            try {{
                const response = await fetch(analyticsServiceUrl + '/api/charts/update-data', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});

                console.log('[v3.7.30] Persistence response status:', response.status);

                if (!response.ok) {{
                    throw new Error('Server returned ' + response.status + ': ' + response.statusText);
                }}

                const result = await response.json();
                console.log('[v3.7.30] Persistence result:', JSON.stringify(result));

                if (!result.persisted) {{
                    throw new Error('Server did not confirm save (persisted=false)');
                }}

                // SUCCESS: Show toast and close modal
                const toast = document.createElement('div');
                toast.innerHTML = '&#9989; Chart saved successfully!';
                toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 14px; font-weight: 500;';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 3000);

                // Close modal only after save confirmed
                closeChartEditor_{js_safe_id}();

            }} catch (saveError) {{
                console.error('[v3.7.30] ❌ Chart save FAILED:', saveError);
                console.error('[v3.7.30] Failed payload was:', JSON.stringify(payload));

                // Show error alert - DO NOT close modal
                const errorToast = document.createElement('div');
                errorToast.innerHTML = '&#10060; Save failed: ' + saveError.message + '<br><small>Check console for details. Try again.</small>';
                errorToast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 14px; font-weight: 500; max-width: 350px;';
                document.body.appendChild(errorToast);
                setTimeout(() => errorToast.remove(), 6000);

                // Modal stays open so user can retry
                return;
            }}
        }} else {{
            // No presentation context - just show local update toast and close
            const toast = document.createElement('div');
            toast.innerHTML = '&#9989; Chart updated locally (no presentation context)';
            toast.style.cssText = 'position: fixed; top: 20px; right: 20px; background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 16px 24px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 100000; font-size: 14px; font-weight: 500;';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);

            closeChartEditor_{js_safe_id}();
        }}
    }};

    // Initialize when DOM ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(initEditor_{js_safe_id}, 500);
        }});
    }} else {{
        setTimeout(initEditor_{js_safe_id}, 500);
    }}

    // v3.7.30: Reusable function to load saved data (called on init AND slide change)
    // Now handles scatter/bubble, waterfall, and multi-series charts
    // Added comprehensive debug logging
    async function reloadSavedData_{js_safe_id}() {{
        const chartId = '{element_id}';
        const analyticsServiceUrl = '{settings.analytics_service_url}';

        // v3.7.30: Debug logging for troubleshooting persistence issues (with parent window info)
        const parentWindow = (window.parent && window.parent !== window) ? window.parent : window;
        console.log('[v3.7.30 Chart Reload] ======= RELOAD START =======');
        console.log('[v3.7.30 Chart Reload] chartId:', chartId);
        console.log('[v3.7.30 Chart Reload] analyticsServiceUrl:', analyticsServiceUrl);
        console.log('[v3.7.30 Chart Reload] Running inside iframe:', window.parent !== window);
        console.log('[v3.7.30 Chart Reload] parent.currentPresentationId:', parentWindow.currentPresentationId);
        console.log('[v3.7.30 Chart Reload] window.currentPresentationId:', window.currentPresentationId);
        console.log('[v3.7.30 Chart Reload] parent.location.pathname:', parentWindow.location.pathname);
        console.log('[v3.7.30 Chart Reload] window.location.pathname:', window.location.pathname);

        // v3.7.30: Extract presentation ID - check parent window first (for iframe context)
        const presentationId = parentWindow.currentPresentationId ||
            window.currentPresentationId ||
            (parentWindow.location.pathname.match(/\\/p\\/([^\\/]+)/) || [])[1] ||
            (window.location.pathname.match(/\\/p\\/([^\\/]+)/) || [])[1];

        console.log('[v3.7.30 Chart Reload] Resolved presentationId:', presentationId);

        if (!presentationId) {{
            console.error('[v3.7.30 Chart Reload] ❌ No presentation ID found! Cannot load saved data.');
            console.log('[v3.7.30 Chart Reload] ======= RELOAD ABORTED =======');
            return;
        }}

        // Find chart instance (should be ready since slide is visible)
        const chart = findChartInstance_{js_safe_id}();
        if (!chart) {{
            console.warn('[v3.7.30 Chart Reload] Chart instance not ready yet');
            return;
        }}

        // v3.7.17: Check localStorage FIRST for waterfall data (synchronous, fixes timing issue)
        const isWaterfallChart = chartType_{js_safe_id} === 'waterfall';
        if (isWaterfallChart) {{
            const storageKey = 'chartData_' + presentationId + '_' + chartId;
            const savedLocal = localStorage.getItem(storageKey);
            if (savedLocal) {{
                try {{
                    const parsed = JSON.parse(savedLocal);
                    if (parsed.waterfall_data && Array.isArray(parsed.waterfall_data)) {{
                        console.log('📂 [v3.7.17] Loading waterfall data from localStorage:', storageKey);
                        const waterfallData = parsed.waterfall_data;
                        chart.data.labels = waterfallData.map(p => p.label);

                        if (chart.data.datasets && chart.data.datasets[0]) {{
                            // Recalculate colors and directions from start/end comparison
                            const floatingBars = [];
                            const newColors = [];
                            const newDirections = [];
                            const dataLen = waterfallData.length;

                            waterfallData.forEach((p, i) => {{
                                const start = p.start;
                                const end = p.end;

                                // Floating bar format: [min, max]
                                floatingBars.push([Math.min(start, end), Math.max(start, end)]);

                                // Determine direction from start vs end
                                const isIncrease = end > start;
                                const isTotal = (i === 0 || i === dataLen - 1) && start === 0;

                                if (isTotal) {{
                                    newColors.push('#93C5FD'); // Blue for totals
                                    newDirections.push('total');
                                }} else if (isIncrease) {{
                                    newColors.push('#A7F3D0'); // Green for increases
                                    newDirections.push('positive');
                                }} else {{
                                    newColors.push('#FBCFE8'); // Pink for decreases
                                    newDirections.push('negative');
                                }}
                            }});

                            chart.data.datasets[0].data = floatingBars;
                            chart.data.datasets[0].backgroundColor = newColors;
                            chart.data.datasets[0].borderColor = newColors;

                            // Update barDirections for formatter
                            if (chart.config) {{
                                chart.config.barDirections = newDirections;
                                if (chart.config._config) {{
                                    chart.config._config.barDirections = newDirections;
                                }}
                            }}
                        }}
                        chart.update();
                        console.log('✅ [v3.7.17] Waterfall colors restored from localStorage');
                        return; // Skip server fetch - localStorage is authoritative
                    }}
                }} catch (e) {{
                    console.warn('[v3.7.17] Failed to parse localStorage waterfall data:', e);
                }}
            }}
        }}

        const multiSeriesCharts = ['area_stacked', 'bar_grouped', 'bar_stacked'];
        const isMultiSeries = multiSeriesCharts.includes(chartType_{js_safe_id});

        // v3.7.30: Debug logging for server fetch
        const fetchUrl = `${{analyticsServiceUrl}}/api/charts/get-data/${{presentationId}}/${{chartId}}`;
        console.log('[v3.7.30 Chart Reload] Fetching saved data from:', fetchUrl);

        try {{
            const response = await fetch(fetchUrl);

            console.log('[v3.7.30 Chart Reload] Fetch response status:', response.status, response.statusText);

            if (response.ok) {{
                const saved = await response.json();
                console.log('[v3.7.30 Chart Reload] Saved data received:', JSON.stringify(saved, null, 2));

                if (saved.success && saved.data) {{
                    // v3.7.10: Check for multi-series format first (has datasets array)
                    if (isMultiSeries && saved.data.datasets && Array.isArray(saved.data.datasets)) {{
                        // Multi-series format: {{ labels: [...], datasets: [{{label, data}}, ...] }}
                        if (saved.data.labels) {{
                            chart.data.labels = saved.data.labels;
                        }}
                        saved.data.datasets.forEach((ds, idx) => {{
                            if (chart.data.datasets[idx]) {{
                                chart.data.datasets[idx].data = ds.data;
                                if (ds.label) {{
                                    chart.data.datasets[idx].label = ds.label;
                                }}
                            }}
                        }});
                        chart.update();
                        console.log('✅ Loaded saved multi-series data for', chartId);
                        return;
                    }}

                    // v3.7.16: Check for waterfall_data format first (new format)
                    const isWaterfall = chartType_{js_safe_id} === 'waterfall';
                    if (isWaterfall && saved.data.waterfall_data && Array.isArray(saved.data.waterfall_data)) {{
                        const waterfallData = saved.data.waterfall_data;
                        chart.data.labels = waterfallData.map(p => p.label);

                        if (chart.data.datasets && chart.data.datasets[0]) {{
                            // v3.7.16: Recalculate colors and directions from start/end comparison
                            const floatingBars = [];
                            const newColors = [];
                            const newDirections = [];
                            const dataLen = waterfallData.length;

                            waterfallData.forEach((p, i) => {{
                                const start = p.start;
                                const end = p.end;

                                // Floating bar format: [min, max]
                                floatingBars.push([Math.min(start, end), Math.max(start, end)]);

                                // Determine direction from start vs end
                                const isIncrease = end > start;
                                const isTotal = (i === 0 || i === dataLen - 1) && start === 0;

                                if (isTotal) {{
                                    newColors.push('#93C5FD'); // Blue for totals
                                    newDirections.push('total');
                                }} else if (isIncrease) {{
                                    newColors.push('#A7F3D0'); // Green for increases
                                    newDirections.push('positive');
                                }} else {{
                                    newColors.push('#FBCFE8'); // Pink for decreases
                                    newDirections.push('negative');
                                }}
                            }});

                            chart.data.datasets[0].data = floatingBars;
                            chart.data.datasets[0].backgroundColor = newColors;
                            chart.data.datasets[0].borderColor = newColors;

                            // Update barDirections for formatter
                            if (chart.config) {{
                                chart.config.barDirections = newDirections;
                                if (chart.config._config) {{
                                    chart.config._config.barDirections = newDirections;
                                }}
                            }}
                        }}
                        chart.update();
                        console.log('✅ Loaded saved waterfall data with recalculated colors for', chartId);
                        return;
                    }}

                    // Check for values array
                    if (Array.isArray(saved.data.values) && saved.data.values.length > 0) {{
                        const values = saved.data.values;

                        // v3.7.9: Check if this is scatter/bubble format (array of objects with x/y)
                        const isScatterBubble = chartType_{js_safe_id} === 'scatter' || chartType_{js_safe_id} === 'bubble';
                        const hasXYFormat = values[0] && typeof values[0] === 'object' && 'x' in values[0] && 'y' in values[0];

                        // v3.7.10: Fallback - check if this is old waterfall format ([[start, end], ...])
                        const hasOldWaterfallFormat = isWaterfall && Array.isArray(values[0]) && values[0].length === 2;

                        if (isScatterBubble && hasXYFormat) {{
                            // Scatter/bubble: apply x/y/r data directly
                            if (chart.data.datasets && chart.data.datasets[0]) {{
                                chart.data.datasets[0].data = values.map(p => ({{
                                    x: p.x,
                                    y: p.y,
                                    r: p.r !== undefined ? p.r : 15,
                                    label: p.label || ''
                                }}));
                            }}
                            chart.update();
                            console.log('✅ Loaded saved scatter/bubble data for', chartId);
                        }} else if (hasOldWaterfallFormat) {{
                            // Waterfall (old format): apply [[start, end], ...] format
                            if (saved.data.labels) {{
                                chart.data.labels = saved.data.labels;
                            }}
                            if (chart.data.datasets && chart.data.datasets[0]) {{
                                chart.data.datasets[0].data = values;
                            }}
                            chart.update();
                            console.log('✅ Loaded saved waterfall data (legacy format) for', chartId);
                        }} else if (Array.isArray(saved.data.labels) && saved.data.labels.length > 0) {{
                            // Standard charts: apply labels and values
                            chart.data.labels = saved.data.labels;
                            if (chart.data.datasets && chart.data.datasets[0]) {{
                                chart.data.datasets[0].data = values;
                            }}
                            chart.update();
                            console.log('✅ Loaded saved chart data for', chartId);
                        }}
                    }}
                }}
            }} else {{
                console.log('[v3.7.30 Chart Reload] No saved data returned (response not ok or no data)');
            }}
        }} catch (e) {{
            // v3.7.30: Enhanced error logging for debugging
            console.error('[v3.7.30 Chart Reload] ❌ Error loading saved data:', e);
            console.error('[v3.7.30 Chart Reload] Error details:', e.message);
        }}
        console.log('[v3.7.30 Chart Reload] ======= RELOAD END =======');
    }}

    // v3.7.8: Initial load with retry logic
    (async function initialLoad_{js_safe_id}() {{
        // Retry with exponential backoff to ensure chart is ready on first load
        for (let attempt = 0; attempt < 4; attempt++) {{
            await new Promise(resolve => setTimeout(resolve, 400 * (attempt + 1)));
            const chart = findChartInstance_{js_safe_id}();
            if (chart) {{
                await reloadSavedData_{js_safe_id}();
                break;
            }}
        }}
    }})();

    // v3.7.8: Listen for Reveal.js slide changes to reload data on navigation
    if (typeof Reveal !== 'undefined') {{
        Reveal.on('slidechanged', function(event) {{
            // Check if this chart's container is on the current slide
            const chartContainer = document.getElementById('{element_id}');
            if (chartContainer) {{
                const currentSlide = event.currentSlide;
                if (currentSlide && currentSlide.contains(chartContainer)) {{
                    // Small delay to ensure chart is rendered
                    setTimeout(() => reloadSavedData_{js_safe_id}(), 200);
                }}
            }}
        }});
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
