"""
Analytics Microservice v3 - Direct Implementation (No Pydantic AI Agent)
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

from .providers import get_openai_client
from .dependencies import AnalyticsDependencies
from .settings import settings
from .tools import chart_generator_direct, data_synthesizer_direct, theme_applier
from .storage import SupabaseStorage

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