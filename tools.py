"""
Tools for Analytics Microservice v3 agent.
"""

import io
import json
import base64
import logging
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
from pydantic_ai import RunContext

from dependencies import AnalyticsDependencies
from providers import get_openai_client

logger = logging.getLogger(__name__)

# Set matplotlib backend for headless operation
matplotlib.use('Agg')

# Define available chart types
CHART_TYPES = {
    "bar_vertical": "Bar Chart (Vertical)",
    "bar_horizontal": "Bar Chart (Horizontal)",
    "bar_grouped": "Grouped Bar Chart",
    "bar_stacked": "Stacked Bar Chart",
    "line": "Line Chart",
    "line_multi": "Multi-Line Chart",
    "area": "Area Chart",
    "area_stacked": "Stacked Area Chart",
    "pie": "Pie Chart",
    "donut": "Donut Chart",
    "scatter": "Scatter Plot",
    "bubble": "Bubble Chart",
    "heatmap": "Heatmap",
    "radar": "Radar Chart",
    "box": "Box Plot",
    "violin": "Violin Plot",
    "histogram": "Histogram",
    "funnel": "Funnel Chart",
    "treemap": "Treemap",
    "sankey": "Sankey Diagram"
}

# Define theme configurations
THEMES = {
    "default": {
        "colors": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
        "grid": True,
        "style": "seaborn-v0_8"
    },
    "dark": {
        "colors": ["#00ff00", "#ff00ff", "#00ffff", "#ffff00", "#ff00ff"],
        "grid": True,
        "style": "dark_background"
    },
    "professional": {
        "colors": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"],
        "grid": False,
        "style": "seaborn-v0_8-whitegrid"
    },
    "colorful": {
        "colors": ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"],
        "grid": True,
        "style": "seaborn-v0_8-bright"
    },
    "minimal": {
        "colors": ["#333333", "#666666", "#999999", "#cccccc", "#e0e0e0"],
        "grid": False,
        "style": "classic"
    }
}


async def chart_generator(
    ctx: RunContext[AnalyticsDependencies],
    chart_type: str,
    data: Dict[str, Any],
    theme: str = "default"
) -> Dict[str, Any]:
    """
    Generate matplotlib chart from provided data and parameters.
    
    Args:
        chart_type: Type of chart (bar, line, pie, scatter, heatmap, etc.)
        data: Dictionary containing chart data (x, y, labels, values)
        theme: Visual theme to apply (default, dark, professional, colorful)
    
    Returns:
        Dictionary with chart image (base64), metadata, and generation status
    """
    try:
        # Send progress update
        await ctx.deps.send_progress_update("chart_rendering", 50, f"Generating {chart_type} chart")
        
        # Validate chart type
        if chart_type not in CHART_TYPES:
            return {
                "success": False,
                "error": f"Invalid chart type. Supported types: {', '.join(CHART_TYPES.keys())}"
            }
        
        # Apply theme
        theme_config = THEMES.get(theme, THEMES["default"])
        plt.style.use(theme_config["style"])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate chart based on type
        if chart_type == "bar_vertical":
            labels = data.get("labels", data.get("x", []))
            values = data.get("values", data.get("y", []))
            bars = ax.bar(labels, values, color=theme_config["colors"][0])
            ax.set_xlabel("Categories")
            ax.set_ylabel("Values")
            
        elif chart_type == "bar_horizontal":
            labels = data.get("labels", data.get("y", []))
            values = data.get("values", data.get("x", []))
            ax.barh(labels, values, color=theme_config["colors"][1])
            ax.set_xlabel("Values")
            ax.set_ylabel("Categories")
            
        elif chart_type == "line":
            x = data.get("x", list(range(len(data.get("y", [])))))
            y = data.get("y", [])
            ax.plot(x, y, color=theme_config["colors"][0], linewidth=2, marker='o')
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            
        elif chart_type == "pie":
            labels = data.get("labels", [])
            values = data.get("values", [])
            ax.pie(values, labels=labels, colors=theme_config["colors"], autopct='%1.1f%%')
            
        elif chart_type == "scatter":
            x = data.get("x", [])
            y = data.get("y", [])
            ax.scatter(x, y, color=theme_config["colors"][2], alpha=0.6, s=100)
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            
        elif chart_type == "heatmap":
            matrix_data = data.get("matrix", [[]])
            im = ax.imshow(matrix_data, cmap='coolwarm', aspect='auto')
            plt.colorbar(im, ax=ax)
            
        elif chart_type == "histogram":
            values = data.get("values", data.get("x", []))
            ax.hist(values, bins=20, color=theme_config["colors"][3], alpha=0.7, edgecolor='black')
            ax.set_xlabel("Values")
            ax.set_ylabel("Frequency")
            
        elif chart_type == "box":
            datasets = data.get("datasets", [data.get("values", [])])
            ax.boxplot(datasets, patch_artist=True, boxprops=dict(facecolor=theme_config["colors"][0]))
            ax.set_ylabel("Values")
            
        elif chart_type == "violin":
            datasets = data.get("datasets", [data.get("values", [])])
            parts = ax.violinplot(datasets, showmeans=True, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor(theme_config["colors"][1])
                pc.set_alpha(0.7)
                
        else:
            # Default to bar chart for unsupported types
            labels = data.get("labels", ["A", "B", "C"])
            values = data.get("values", [1, 2, 3])
            ax.bar(labels, values, color=theme_config["colors"][0])
        
        # Add title if provided
        title = data.get("title", f"{CHART_TYPES.get(chart_type, 'Chart')}")
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Apply grid setting
        ax.grid(theme_config["grid"], alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        chart_base64 = ctx.deps.encode_chart_to_base64(buffer)
        
        await ctx.deps.send_progress_update("chart_rendering", 75, "Chart generated successfully")
        
        return {
            "success": True,
            "chart": chart_base64,
            "chart_type": chart_type,
            "theme": theme,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "data_points": len(data.get("values", data.get("y", [])))
            }
        }
        
    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        return {
            "success": False,
            "error": f"Chart generation failed: {str(e)}"
        }


async def data_synthesizer(
    ctx: RunContext[AnalyticsDependencies],
    data_description: str,
    sample_size: int = 50
) -> Dict[str, Any]:
    """
    Synthesize realistic dataset using LLM based on description.
    
    Args:
        data_description: Natural language description of desired data
        sample_size: Number of data points to generate (10-1000)
    
    Returns:
        Dictionary with synthesized data in chart-ready format
    """
    try:
        # Send progress update
        await ctx.deps.send_progress_update("data_processing", 25, "Synthesizing data")
        
        # Clamp sample size
        sample_size = max(10, min(1000, sample_size))
        
        # Use OpenAI to generate data
        client = get_openai_client()
        
        prompt = f"""Generate realistic data for: {data_description}
        
        Create exactly {sample_size} data points in JSON format:
        {{
            "labels": ["label1", "label2", ...],
            "values": [value1, value2, ...],
            "x": [x1, x2, ...],
            "y": [y1, y2, ...],
            "title": "Descriptive title"
        }}
        
        Ensure the data is realistic and matches the description context.
        Return ONLY valid JSON, no explanations."""
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data generation specialist. Generate realistic datasets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        data_json = response.choices[0].message.content.strip()
        # Clean up JSON if needed
        if data_json.startswith("```json"):
            data_json = data_json[7:]
        if data_json.endswith("```"):
            data_json = data_json[:-3]
            
        data = json.loads(data_json)
        
        # Ensure we have the right sample size
        for key in ["values", "x", "y"]:
            if key in data and len(data[key]) != sample_size:
                # Adjust to match sample size
                if len(data[key]) > sample_size:
                    data[key] = data[key][:sample_size]
                else:
                    # Pad with interpolated values
                    while len(data[key]) < sample_size:
                        data[key].append(data[key][-1] if data[key] else 0)
        
        # Adjust labels if needed
        if "labels" in data and len(data["labels"]) != sample_size:
            if len(data["labels"]) > sample_size:
                data["labels"] = data["labels"][:sample_size]
            else:
                while len(data["labels"]) < sample_size:
                    data["labels"].append(f"Item {len(data['labels']) + 1}")
        
        await ctx.deps.send_progress_update("data_processing", 40, "Data synthesized successfully")
        
        return {
            "success": True,
            "data": data,
            "sample_size": sample_size,
            "description": data_description
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse synthesized data: {e}")
        # Return simple default dataset
        return {
            "success": True,
            "data": {
                "labels": [f"Item {i+1}" for i in range(sample_size)],
                "values": [np.random.randint(10, 100) for _ in range(sample_size)],
                "title": data_description
            },
            "sample_size": sample_size,
            "warning": "Used fallback data generation"
        }
    except Exception as e:
        logger.error(f"Data synthesis failed: {e}")
        return {
            "success": False,
            "error": f"Data synthesis failed: {str(e)}"
        }


async def chart_generator_direct(
    deps: 'AnalyticsDependencies',
    chart_type: str,
    data: Dict[str, Any],
    theme: str = "default"
) -> Dict[str, Any]:
    """
    Direct chart generator without RunContext.
    """
    try:
        # Send progress update
        await deps.send_progress_update("chart_rendering", 50, f"Generating {chart_type} chart")
        
        # Validate chart type
        if chart_type not in CHART_TYPES:
            return {
                "success": False,
                "error": f"Invalid chart type. Supported types: {', '.join(CHART_TYPES.keys())}"
            }
        
        # Apply theme
        theme_config = THEMES.get(theme, THEMES["default"])
        plt.style.use(theme_config["style"])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate chart based on type
        if chart_type == "bar_vertical":
            labels = data.get("labels", data.get("x", []))
            values = data.get("values", data.get("y", []))
            bars = ax.bar(labels, values, color=theme_config["colors"][0])
            ax.set_xlabel("Categories")
            ax.set_ylabel("Values")
            
        elif chart_type == "bar_horizontal":
            labels = data.get("labels", data.get("y", []))
            values = data.get("values", data.get("x", []))
            ax.barh(labels, values, color=theme_config["colors"][1])
            ax.set_xlabel("Values")
            ax.set_ylabel("Categories")
            
        elif chart_type == "line":
            x = data.get("x", list(range(len(data.get("y", data.get("values", []))))))
            y = data.get("y", data.get("values", []))
            ax.plot(x, y, color=theme_config["colors"][0], linewidth=2, marker='o')
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            
        elif chart_type == "pie":
            labels = data.get("labels", [])
            values = data.get("values", [])
            ax.pie(values, labels=labels, colors=theme_config["colors"], autopct='%1.1f%%')
            
        elif chart_type == "scatter":
            x = data.get("x", data.get("labels", list(range(len(data.get("values", []))))))
            y = data.get("y", data.get("values", []))
            ax.scatter(x, y, color=theme_config["colors"][2], alpha=0.6, s=100)
            ax.set_xlabel("X Axis")
            ax.set_ylabel("Y Axis")
            
        elif chart_type == "heatmap":
            matrix_data = data.get("matrix", [[]])
            if not matrix_data:
                # Create sample matrix from values
                values = data.get("values", [1, 2, 3, 4])
                size = int(len(values) ** 0.5) + 1
                matrix_data = np.array(values[:size*size]).reshape(size, size)
            im = ax.imshow(matrix_data, cmap='coolwarm', aspect='auto')
            plt.colorbar(im, ax=ax)
            
        elif chart_type == "histogram":
            values = data.get("values", data.get("x", []))
            ax.hist(values, bins=min(20, max(5, len(values)//3)), color=theme_config["colors"][3], alpha=0.7, edgecolor='black')
            ax.set_xlabel("Values")
            ax.set_ylabel("Frequency")
            
        elif chart_type == "box":
            datasets = data.get("datasets", [data.get("values", [])])
            ax.boxplot(datasets, patch_artist=True, boxprops=dict(facecolor=theme_config["colors"][0]))
            ax.set_ylabel("Values")
            
        elif chart_type == "violin":
            datasets = data.get("datasets", [data.get("values", [])])
            parts = ax.violinplot(datasets, showmeans=True, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor(theme_config["colors"][1])
                pc.set_alpha(0.7)
                
        else:
            # Default to bar chart for unsupported types
            labels = data.get("labels", ["A", "B", "C"])
            values = data.get("values", [1, 2, 3])
            ax.bar(labels, values, color=theme_config["colors"][0])
        
        # Add title if provided
        title = data.get("title", f"{CHART_TYPES.get(chart_type, 'Chart')}")
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Apply grid setting
        if theme_config["grid"]:
            ax.grid(True, alpha=0.3)
        
        # Tight layout
        plt.tight_layout()

        # Save chart to buffer as PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)

        # Get PNG bytes
        buffer.seek(0)
        chart_bytes = buffer.getvalue()

        await deps.send_progress_update("chart_rendering", 75, "Chart generated successfully")

        return {
            "success": True,
            "chart_bytes": chart_bytes,
            "chart_data": {
                "labels": data.get("labels", data.get("x", [])),
                "values": data.get("values", data.get("y", [])),
                "title": data.get("title", "Chart")
            },
            "chart_type": chart_type,
            "theme": theme,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "data_points": len(data.get("values", data.get("y", [])))
            }
        }
        
    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        return {
            "success": False,
            "error": f"Chart generation failed: {str(e)}"
        }


async def data_synthesizer_direct(
    deps: 'AnalyticsDependencies',
    data_description: str,
    sample_size: int = 50
) -> Dict[str, Any]:
    """
    Direct data synthesizer without RunContext.
    """
    try:
        # Send progress update
        await deps.send_progress_update("data_processing", 25, "Synthesizing data")
        
        # Clamp sample size
        sample_size = max(10, min(1000, sample_size))
        
        # Use OpenAI to generate data
        client = get_openai_client()
        
        prompt = f"""Generate realistic data for: {data_description}
        
        Create exactly {sample_size} data points in JSON format:
        {{
            "labels": ["label1", "label2", ...],
            "values": [value1, value2, ...],
            "x": [x1, x2, ...],
            "y": [y1, y2, ...],
            "title": "Descriptive title"
        }}
        
        Ensure the data is realistic and matches the description context.
        Return ONLY valid JSON, no explanations."""
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data generation specialist. Generate realistic datasets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        data_json = response.choices[0].message.content.strip()
        # Clean up JSON if needed
        if data_json.startswith("```json"):
            data_json = data_json[7:]
        if data_json.endswith("```"):
            data_json = data_json[:-3]
            
        data = json.loads(data_json)
        
        # Ensure we have the right sample size
        for key in ["values", "x", "y"]:
            if key in data and len(data[key]) != sample_size:
                # Adjust to match sample size
                if len(data[key]) > sample_size:
                    data[key] = data[key][:sample_size]
                else:
                    # Pad with interpolated values
                    while len(data[key]) < sample_size:
                        data[key].append(data[key][-1] if data[key] else 0)
        
        # Adjust labels if needed
        if "labels" in data and len(data["labels"]) != sample_size:
            if len(data["labels"]) > sample_size:
                data["labels"] = data["labels"][:sample_size]
            else:
                while len(data["labels"]) < sample_size:
                    data["labels"].append(f"Item {len(data['labels']) + 1}")
        
        await deps.send_progress_update("data_processing", 40, "Data synthesized successfully")
        
        return {
            "success": True,
            "data": data,
            "sample_size": sample_size,
            "description": data_description
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse synthesized data: {e}")
        # Return simple default dataset
        return {
            "success": True,
            "data": {
                "labels": [f"Item {i+1}" for i in range(sample_size)],
                "values": [np.random.randint(10, 100) for _ in range(sample_size)],
                "title": data_description
            },
            "sample_size": sample_size,
            "warning": "Used fallback data generation"
        }
    except Exception as e:
        logger.error(f"Data synthesis failed: {e}")
        return {
            "success": False,
            "error": f"Data synthesis failed: {str(e)}"
        }


def theme_applier(
    chart_config: Dict[str, Any],
    theme_name: str,
    custom_colors: List[str] = None
) -> Dict[str, Any]:
    """
    Apply visual theme configuration to chart parameters.
    
    Args:
        chart_config: Base chart configuration dictionary
        theme_name: Theme to apply (default, dark, professional, colorful, minimal)
        custom_colors: Optional list of hex colors to override theme palette
    
    Returns:
        Updated chart configuration with theme styling applied
    """
    try:
        # Get theme or fallback to default
        theme = THEMES.get(theme_name, THEMES["default"])
        
        # Apply custom colors if provided
        if custom_colors:
            # Validate hex colors
            valid_colors = []
            for color in custom_colors:
                if color.startswith("#") and len(color) in [4, 7]:
                    valid_colors.append(color)
            if valid_colors:
                theme["colors"] = valid_colors
        
        # Merge theme with chart config
        chart_config["theme"] = {
            "name": theme_name,
            "colors": theme["colors"],
            "grid": theme["grid"],
            "style": theme["style"],
            "font_size": 12,
            "title_size": 14,
            "label_size": 10
        }
        
        # Add theme-specific configurations
        if theme_name == "dark":
            chart_config["background_color"] = "#1a1a1a"
            chart_config["text_color"] = "#ffffff"
        elif theme_name == "minimal":
            chart_config["background_color"] = "#ffffff"
            chart_config["text_color"] = "#333333"
            chart_config["show_legend"] = False
        
        return {
            "success": True,
            "config": chart_config,
            "theme_applied": theme_name
        }
        
    except Exception as e:
        logger.error(f"Theme application failed: {e}")
        return {
            "success": False,
            "config": chart_config,
            "error": f"Theme application failed: {str(e)}"
        }


async def progress_streamer(
    ctx: RunContext[AnalyticsDependencies],
    connection_id: str,
    progress_data: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Stream progress updates to WebSocket connection.
    
    Args:
        connection_id: WebSocket connection identifier
        progress_data: Progress information (stage, percentage, message)
    
    Returns:
        Dictionary indicating successful message delivery
    """
    try:
        # Validate connection
        if connection_id not in ctx.deps.active_connections:
            logger.warning(f"Connection {connection_id} not found in active connections")
            return {"success": False, "delivered": False}
        
        # Format progress message
        progress_message = {
            "type": "progress_update",
            "connection_id": connection_id,
            "request_id": ctx.deps.chart_request_id,
            "stage": progress_data.get("stage", "processing"),
            "progress": progress_data.get("percentage", 0),
            "message": progress_data.get("message", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send via callback if available
        if ctx.deps.progress_callback:
            await ctx.deps.progress_callback(progress_message)
            return {"success": True, "delivered": True}
        else:
            logger.info(f"Progress update queued: {progress_message}")
            return {"success": True, "delivered": False}
            
    except Exception as e:
        logger.error(f"Progress streaming failed: {e}")
        # Continue silently - don't break chart generation
        return {"success": False, "delivered": False}