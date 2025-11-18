"""
Analytics Microservice v3 - Direct Implementation (No Pydantic AI Agent)
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from providers import get_openai_client
from dependencies import AnalyticsDependencies
from settings import settings
from tools import chart_generator_direct, data_synthesizer_direct, theme_applier
from storage import SupabaseStorage
from analytics_types import get_chart_type, get_layout_dimensions
from chartjs_generator import ChartJSGenerator
from insight_generator import InsightGenerator
from layout_assembler import L02LayoutAssembler

logger = logging.getLogger(__name__)

logger.info("Analytics Microservice v3 initialized")


async def process_analytics_direct(
    request_data: Dict[str, Any],
    deps: AnalyticsDependencies
) -> Dict[str, Any]:
    """
    Process analytics request directly without Pydantic AI agent.
    
    Args:
        request_data: Request parameters
        deps: Analytics dependencies
        
    Returns:
        Chart result dictionary
    """
    try:
        
        # Extract parameters
        content = request_data.get("content", "Generate a chart")
        title = request_data.get("title", "Analytics Chart")
        user_data = request_data.get("data")
        chart_type = request_data.get("chart_type", "bar_vertical")
        theme = request_data.get("theme", "default")
        
        # Step 1: Process data
        await deps.send_progress_update("data_processing", 10, "Processing request")
        
        if user_data:
            # Use provided data
            chart_data = {
                "labels": [d.get("label", f"Item {i}") for i, d in enumerate(user_data)],
                "values": [d.get("value", 0) for d in user_data],
                "title": title
            }
            await deps.send_progress_update("data_processing", 25, "Using provided data")
        else:
            # Synthesize data
            await deps.send_progress_update("data_processing", 15, "Generating synthetic data")
            synthesis_result = await data_synthesizer_direct(deps, content, sample_size=10)
            
            if synthesis_result["success"]:
                chart_data = synthesis_result["data"]
                await deps.send_progress_update("data_processing", 25, "Data synthesized")
            else:
                # Fallback to simple data
                chart_data = {
                    "labels": ["Q1", "Q2", "Q3", "Q4"],
                    "values": [25, 35, 30, 40],
                    "title": title
                }
        
        # Step 2: Apply theme
        await deps.send_progress_update("theme_applying", 40, "Applying theme")
        theme_result = theme_applier({"chart_data": chart_data}, theme)
        
        # Step 3: Generate chart
        await deps.send_progress_update("chart_rendering", 60, f"Generating {chart_type} chart")

        # Add title to data
        chart_data["title"] = title

        chart_result = await chart_generator_direct(
            deps,
            chart_type=chart_type,
            data=chart_data,
            theme=theme
        )

        if not chart_result.get("success"):
            return chart_result

        # Step 4: Upload chart to Supabase Storage
        await deps.send_progress_update("uploading", 80, "Uploading chart to storage")

        chart_bytes = chart_result.get("chart_bytes")
        storage = deps.storage

        # Check if storage is configured
        if storage is None:
            return {
                "success": False,
                "error": "Supabase Storage not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env file."
            }

        chart_url = storage.upload_chart(
            image_bytes=chart_bytes,
            chart_type=chart_type,
            file_extension="png"
        )

        if not chart_url:
            return {
                "success": False,
                "error": "Failed to upload chart to storage. Check Supabase credentials."
            }

        await deps.send_progress_update("completion", 100, "Chart generation complete")

        # Return URL + simplified JSON data
        return {
            "success": True,
            "chart_url": chart_url,
            "chart_data": chart_result.get("chart_data", {}),
            "chart_type": chart_type,
            "theme": theme,
            "metadata": chart_result.get("metadata", {})
        }
        
    except Exception as e:
        logger.error(f"Direct processing failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def process_analytics_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process analytics request and return structured response.
    
    Args:
        request_data: Dictionary with request parameters
            - content: Description of analytics needed
            - title: Optional chart title
            - data: Optional user data
            - chart_type: Optional preferred chart type
            - theme: Optional theme name
            - websocket_id: Optional WebSocket connection ID
            - progress_callback: Optional progress callback
    
    Returns:
        Dictionary with chart and metadata
    """
    try:
        websocket_id = request_data.get("websocket_id")
        progress_callback = request_data.get("progress_callback")
        
        # Create dependencies
        deps = AnalyticsDependencies.from_settings(
            settings,
            websocket_id=websocket_id,
            progress_callback=progress_callback,
            chart_request_id=request_data.get("request_id")
        )
        
        # Process directly without Pydantic AI agent
        result = await process_analytics_direct(request_data, deps)

        if result.get("success"):
            return {
                "success": True,
                "chart_url": result.get("chart_url"),
                "chart_data": result.get("chart_data", {}),
                "metadata": {
                    "chart_type": result.get("chart_type", request_data.get("chart_type")),
                    "theme": result.get("theme", request_data.get("theme")),
                    "title": request_data.get("title", "Analytics Chart"),
                    **result.get("metadata", {})
                }
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Chart generation failed"),
                "metadata": {}
            }
        
    except Exception as e:
        logger.error(f"Analytics request processing failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "metadata": {}
        }
    finally:
        if 'deps' in locals():
            await deps.cleanup()


async def process_analytics_slide(
    analytics_type: str,
    layout: str,
    request_data: Dict[str, Any],
    storage: Optional[SupabaseStorage] = None
) -> Dict[str, Any]:
    """
    Process analytics slide generation (Text Service compatible pattern).

    Generates complete slide content with Chart.js HTML and LLM-generated insights,
    formatted for Layout Builder layouts (L01, L02, L03).

    Args:
        analytics_type: Type of analytics (revenue_over_time, market_share, etc.)
        layout: Layout type (L01, L02, L03)
        request_data: Request parameters matching Text Service pattern
        storage: Optional Supabase storage instance

    Returns:
        Dictionary with content and metadata in Text Service format
    """
    try:
        start_time = datetime.utcnow()

        # Extract request fields
        presentation_id = request_data.get("presentation_id")
        slide_id = request_data.get("slide_id")
        slide_number = request_data.get("slide_number")
        narrative = request_data.get("narrative", "")
        data = request_data.get("data", [])
        context = request_data.get("context", {})
        constraints = request_data.get("constraints", {})

        # Get configuration
        theme = context.get("theme", "professional")
        audience = context.get("audience", "executives")
        slide_title = context.get("slide_title", "Analytics")
        subtitle = context.get("subtitle", "")

        # Get layout dimensions
        dimensions = get_layout_dimensions(layout)
        chart_height = dimensions.get("chart_height", 600)
        chart_width = dimensions.get("chart_width", 1800)

        # Get chart type for this analytics type
        chart_type = get_chart_type(analytics_type)

        # Convert data format
        chart_data = {
            "labels": [d.get("label") for d in data],
            "values": [d.get("value") for d in data],
            "series_name": slide_title,
            "format": _detect_data_format(data)
        }

        logger.info(f"Generating {analytics_type} as {chart_type} chart in {layout} layout")

        # Generate unique chart ID
        chart_id = f"chart-{slide_id}" if slide_id else f"chart-{analytics_type}-{int(datetime.utcnow().timestamp())}"

        # Initialize generators
        chart_gen = ChartJSGenerator(theme=theme)
        insight_gen = InsightGenerator()

        # Helper function to generate chart with correct ChartJS method
        def generate_chartjs_html(
            chart_type: str,
            data: Dict,
            height: int,
            chart_id: Optional[str] = None,
            enable_editor: bool = True,  # Director Approach 3: enabled by default
            presentation_id: Optional[str] = None,
            api_base_url: str = "/api/charts"
        ) -> str:
            """Generate Chart.js HTML using appropriate method for chart type."""
            # Map chart types to ChartJSGenerator methods
            if chart_type == "line":
                return chart_gen.generate_line_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "bar" or chart_type == "bar_vertical":
                return chart_gen.generate_bar_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "bar_horizontal":
                return chart_gen.generate_horizontal_bar_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "pie":
                return chart_gen.generate_pie_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type in ["donut", "doughnut"]:
                return chart_gen.generate_doughnut_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "scatter":
                return chart_gen.generate_scatter_plot(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "bubble":
                return chart_gen.generate_bubble_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "radar":
                return chart_gen.generate_radar_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            elif chart_type == "polar_area" or chart_type == "polarArea":
                return chart_gen.generate_polar_area_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )
            else:
                # Default to bar chart for truly unknown types
                logger.warning(f"Unknown chart type '{chart_type}', defaulting to bar chart")
                return chart_gen.generate_bar_chart(
                    data=data,
                    height=height,
                    chart_id=chart_id,
                    enable_editor=enable_editor,
                    presentation_id=presentation_id,
                    api_base_url=api_base_url,
                    output_mode="inline_script"
                )

        # Read enable_editor from request, default to True (Director Approach 3)
        enable_editor = request_data.get("enable_editor", True)

        # Generate chart HTML with inline script mode for Layout Builder compliance
        chart_html = generate_chartjs_html(
            chart_type=chart_type,
            data=chart_data,
            height=chart_height,
            chart_id=chart_id,
            enable_editor=enable_editor,                   # Enabled by default, controllable per-request
            presentation_id=presentation_id,               # Pass presentation ID for persistence
            api_base_url="/api/charts"                     # API endpoint for chart data saves
        )

        # Generate content based on layout
        if layout == "L01":
            # L01: Centered chart with body text below
            insight = await insight_gen.generate_l01_insight(
                chart_type=chart_type,
                data=chart_data,
                narrative=narrative,
                audience=audience,
                context=context
            )

            content = {
                "slide_title": slide_title,
                "element_1": subtitle,
                "element_4": chart_html,
                "element_3": insight,
                "presentation_name": context.get("presentation_name", ""),
                "company_logo": context.get("company_logo", "📊")
            }

        elif layout == "L02":
            # L02: Chart left with detailed explanation right
            explanation = await insight_gen.generate_l02_explanation(
                chart_type=chart_type,
                data=chart_data,
                narrative=narrative,
                audience=audience,
                context=context
            )

            # Use layout assembler to format observations panel with Layout Builder-compliant styling
            layout_assembler = L02LayoutAssembler(theme=theme)
            formatted_observations = layout_assembler.assemble_observations_html(
                insights_text=explanation,
                title="Key Insights"
            )

            content = {
                "slide_title": slide_title,
                "element_1": subtitle,
                "element_3": chart_html,  # Chart.js inline script (already Layout Builder compliant)
                "element_2": formatted_observations,  # Styled observations panel
                "presentation_name": context.get("presentation_name", ""),
                "company_logo": context.get("company_logo", "📊")
            }

        elif layout == "L03":
            # L03: Side-by-side comparison
            # Split data into left and right
            mid_point = len(data) // 2
            left_data = {
                "labels": [d.get("label") for d in data[:mid_point]],
                "values": [d.get("value") for d in data[:mid_point]],
                "series_name": "Before",
                "format": chart_data["format"]
            }
            right_data = {
                "labels": [d.get("label") for d in data[mid_point:]],
                "values": [d.get("value") for d in data[mid_point:]],
                "series_name": "After",
                "format": chart_data["format"]
            }

            # Generate two charts
            left_chart = generate_chartjs_html(
                chart_type=chart_type,
                data=left_data,
                height=chart_height,
                chart_id=f"chart-left-{slide_id}"
            )

            right_chart = generate_chartjs_html(
                chart_type=chart_type,
                data=right_data,
                height=chart_height,
                chart_id=f"chart-right-{slide_id}"
            )

            # Generate paired descriptions
            left_desc, right_desc = await insight_gen.generate_l03_descriptions(
                left_data=left_data,
                right_data=right_data,
                narrative=narrative
            )

            content = {
                "slide_title": slide_title,
                "element_1": subtitle,
                "element_4": left_chart,
                "element_2": right_chart,
                "element_3": left_desc,
                "element_5": right_desc,
                "presentation_name": context.get("presentation_name", ""),
                "company_logo": context.get("company_logo", "📊")
            }

        else:
            raise ValueError(f"Unsupported layout: {layout}")

        # Calculate generation time
        generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Prepare metadata
        metadata = {
            "analytics_type": analytics_type,
            "layout": layout,
            "chart_library": "chartjs",
            "chart_type": chart_type,
            "model_used": "gpt-4o-mini",
            "data_points": len(data),
            "generation_time_ms": int(generation_time),
            "theme": theme,
            "generated_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Successfully generated {layout} analytics slide in {generation_time:.0f}ms")

        return {
            "success": True,
            "content": content,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"Analytics slide generation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "content": {},
            "metadata": {
                "analytics_type": analytics_type,
                "layout": layout,
                "error": str(e)
            }
        }


def _detect_data_format(data: list) -> str:
    """
    Detect data format from values (currency, percentage, or number).

    Args:
        data: List of data points with label and value

    Returns:
        Format type: "currency", "percentage", or "number"
    """
    if not data:
        return "number"

    # Check first few values
    sample_values = [d.get("value", 0) for d in data[:3]]

    # If all values are between 0 and 100, likely percentage
    if all(0 <= v <= 100 for v in sample_values):
        # But only if they're not all whole numbers above 10
        if not all(v > 10 and v == int(v) for v in sample_values):
            return "percentage"

    # If values are large (> 1000), likely currency
    if any(v > 1000 for v in sample_values):
        return "currency"

    return "number"


async def generate_l02_analytics(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate L02 analytics slide with Chart.js + observations.

    Returns 2 separate HTML fields for Director Agent integration:
    - element_3: Chart HTML (1260×720px)
    - element_2: Observations HTML (540×720px)

    Follows Director Agent integration specification v1.0.

    Args:
        request_data: Request from Director Agent
            - presentation_id: Presentation identifier
            - slide_id: Slide identifier
            - slide_number: Slide position
            - narrative: User narrative/description
            - topics: List of topic keywords
            - data: Array of {label, value} data points
            - context: {theme, audience, slide_title, subtitle, ...}
            - options: {enable_editor: bool, chart_height: int}

    Returns:
        Dictionary with content (element_3, element_2) and metadata:
        {
            "content": {
                "element_3": "<div>chart html</div>",
                "element_2": "<div>observations html</div>"
            },
            "metadata": {
                "analytics_type": "...",
                "chart_type": "...",
                "layout": "L02",
                ...
            }
        }
    """
    try:
        from chartjs_generator import ChartJSGenerator
        from layout_assembler import assemble_l02_layout
        from session_manager import get_session_manager

        start_time = datetime.utcnow()

        # Extract request fields
        presentation_id = request_data.get("presentation_id", "unknown")
        slide_id = request_data.get("slide_id", "slide-unknown")
        slide_number = request_data.get("slide_number", 1)
        narrative = request_data.get("narrative", "")
        topics = request_data.get("topics", [])
        data = request_data.get("data", [])
        context = request_data.get("context", {})
        options = request_data.get("options", {})

        # Configuration
        theme = context.get("theme", "professional")
        audience = context.get("audience", "executives")
        slide_title = context.get("slide_title", "Analytics")
        subtitle = context.get("subtitle", "")
        enable_editor = options.get("enable_editor", True)  # Director Approach 3: enabled by default

        # Determine analytics type: use explicit parameter if provided, otherwise infer (v3.1.4 hotfix)
        analytics_type = request_data.get('analytics_type') or _infer_analytics_type(narrative, topics, data)

        # Determine chart type
        chart_type = get_chart_type(analytics_type)

        # Convert data format for Chart.js
        chart_data = {
            "labels": [d.get("label", f"Item {i}") for i, d in enumerate(data)],
            "values": [d.get("value", 0) for d in data],
            "series_name": slide_title,
            "format": _detect_data_format(data)
        }

        logger.info(
            f"Generating L02 analytics: {analytics_type} ({chart_type}) "
            f"for presentation {presentation_id}, slide {slide_number}"
        )

        # Initialize generators
        chart_gen = ChartJSGenerator(theme=theme)
        insight_gen = InsightGenerator()
        session_mgr = get_session_manager()

        # Get prior slides for context
        prior_slides = session_mgr.get_prior_slides(presentation_id, limit=3)

        # Generate chart HTML (Chart.js canvas) - v3.1.5 fix for Chart.js type mapping
        chart_html = None
        if chart_type == "line":
            chart_html = chart_gen.generate_line_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "bar" or chart_type == "bar_vertical":
            chart_html = chart_gen.generate_bar_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "bar_horizontal":
            chart_html = chart_gen.generate_horizontal_bar_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "pie":
            chart_html = chart_gen.generate_pie_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type in ["donut", "doughnut"]:
            chart_html = chart_gen.generate_doughnut_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "scatter":
            # Convert label-value format to scatter datasets format (x-y coordinates)
            # Preserve labels as custom property for tooltips
            # NOTE: Editor team needs to enhance editor to support object data points
            scatter_data = {
                "datasets": [{
                    "label": slide_title,
                    "data": [
                        {
                            "x": i,
                            "y": v,
                            "label": chart_data["labels"][i]  # Preserve original label
                        }
                        for i, v in enumerate(chart_data["values"])
                    ]
                }]
            }
            # v3.1.9: FIX datalabels bug - pass in options parameter (not data dict!)
            scatter_options = {
                "plugins": {
                    "datalabels": {
                        "display": False  # Prevent [object Object] labels
                    }
                }
            }
            chart_html = chart_gen.generate_scatter_plot(
                data=scatter_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                options=scatter_options,  # ✅ CORRECT LOCATION
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "bubble":
            # Convert label-value format to bubble datasets format (x-y-r coordinates)
            # Preserve labels and vary bubble radius based on value
            # NOTE: Editor team needs to enhance editor to support object data points

            # v3.1.9: Improved proportional radius scaling (8-40px range)
            values = chart_data["values"]
            max_val = max(values) if values else 1
            min_val = min(values) if values else 0
            val_range = max_val - min_val if max_val != min_val else 1

            bubble_data = {
                "datasets": [{
                    "label": slide_title,
                    "data": [
                        {
                            "x": i,
                            "y": v,
                            # Proportional scaling: maps min→8px, max→40px
                            "r": max(8, min(40, 8 + (v - min_val) / val_range * 32)),
                            "label": chart_data["labels"][i]  # Preserve original label
                        }
                        for i, v in enumerate(values)
                    ]
                }]
            }
            # v3.1.9: FIX datalabels bug - pass in options parameter (not data dict!)
            bubble_options = {
                "plugins": {
                    "datalabels": {
                        "display": False  # Prevent [object Object] labels
                    }
                }
            }
            chart_html = chart_gen.generate_bubble_chart(
                data=bubble_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                options=bubble_options,  # ✅ CORRECT LOCATION
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "radar":
            # Convert label-value format to radar datasets format
            # Radar charts need datasets array with data values
            radar_data = {
                "labels": chart_data["labels"],
                "datasets": [{
                    "label": slide_title,
                    "data": chart_data["values"]
                }],
                "format": chart_data.get("format", "number")
            }
            chart_html = chart_gen.generate_radar_chart(
                data=radar_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        elif chart_type == "polar_area" or chart_type == "polarArea":
            chart_html = chart_gen.generate_polar_area_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )
        else:
            # Default to bar chart for unknown types
            logger.warning(f"Unknown chart type '{chart_type}', defaulting to bar chart")
            chart_html = chart_gen.generate_bar_chart(
                data=chart_data,
                height=720,
                chart_id=f"chart-{slide_id}",
                enable_editor=enable_editor,
                presentation_id=presentation_id,
                api_base_url="https://analytics-v30-production.up.railway.app/api/charts"
            )

        if not chart_html:
            raise ValueError(f"Failed to generate {chart_type} chart")

        # Generate observations/insights (v3.3.3: increased to 1000 chars for complete bullets)
        insights_text = await insight_gen.generate_l02_explanation(
            chart_type=chart_type,
            data=chart_data,
            narrative=narrative,
            audience=audience,
            context={
                **context,
                "prior_slides": prior_slides,
                "max_chars": 800  # v3.3.5: Reduced to 800 for 5-6 bullets to fit on one page
            }
        )

        # Assemble L02 layout (returns element_3 and element_2)
        l02_content = assemble_l02_layout(
            canvas_html=chart_html,
            chart_id=f"chart-{slide_id}",
            insights_text=insights_text,
            theme=theme,
            enable_editor=enable_editor
        )

        # Update session context
        session_mgr.update_context(
            presentation_id=presentation_id,
            slide_data={
                "slide_number": slide_number,
                "slide_id": slide_id,
                "analytics_type": analytics_type,
                "narrative": narrative,
                "data": data,
                "theme": theme
            }
        )

        # Calculate generation time
        generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Prepare metadata
        metadata = {
            "analytics_type": analytics_type,
            "chart_type": chart_type,
            "layout": "L02",
            "chart_library": "chartjs",
            "model_used": "gpt-4o-mini",
            "data_points": len(data),
            "generation_time_ms": int(generation_time),
            "theme": theme,
            "generated_at": datetime.utcnow().isoformat(),
            "interactive_editor": enable_editor
        }

        logger.info(
            f"Successfully generated L02 analytics slide in {generation_time:.0f}ms "
            f"({analytics_type}, {len(data)} data points)"
        )

        return {
            "content": l02_content,  # Contains element_3 and element_2
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"L02 analytics generation failed: {e}", exc_info=True)

        # Return error with empty content
        return {
            "content": {
                "element_3": f"<div style='padding: 40px; color: red;'>Error: {str(e)}</div>",
                "element_2": "<div style='padding: 40px;'>Unable to generate observations.</div>"
            },
            "metadata": {
                "layout": "L02",
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
        }


def _infer_analytics_type(narrative: str, topics: list, data: list) -> str:
    """
    Infer analytics type from narrative, topics, and data.

    Args:
        narrative: User narrative/description
        topics: List of topic keywords
        data: Data points

    Returns:
        Analytics type (revenue_over_time, market_share, etc.)
    """
    narrative_lower = narrative.lower()
    topics_lower = [t.lower() for t in topics]

    # Revenue/growth keywords → revenue_over_time
    if any(word in narrative_lower for word in ["revenue", "growth", "sales", "income"]):
        return "revenue_over_time"

    # Market/share keywords → market_share
    if any(word in narrative_lower for word in ["market", "share", "distribution", "breakdown"]):
        return "market_share"

    # Quarterly/comparison keywords → quarterly_comparison
    if any(word in narrative_lower for word in ["quarterly", "quarter", "q1", "q2", "q3", "q4", "comparison"]):
        return "quarterly_comparison"

    # Year-over-year keywords → yoy_growth
    if any(word in narrative_lower for word in ["year-over-year", "yoy", "annual", "yearly"]):
        return "yoy_growth"

    # KPI/metrics keywords → kpi_metrics
    if any(word in narrative_lower for word in ["kpi", "metrics", "performance", "indicators"]):
        return "kpi_metrics"

    # Default based on data structure
    if len(data) <= 5:
        return "market_share"  # Few categories → donut chart
    else:
        return "revenue_over_time"  # Time series → line chart