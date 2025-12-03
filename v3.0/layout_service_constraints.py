"""
Layout Service Grid Constraints
===============================

Grid-based sizing logic and data limits for Layout Service integration.
Follows AI_SERVICE_CHART.md specification for minimum sizes and data point limits.

Author: Analytics Microservice v3 Team
Date: 2025-12
"""

from typing import Dict, Tuple, Literal
from enum import Enum


class LayoutSize(str, Enum):
    """Layout size categories based on grid area."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


# ============================================
# MINIMUM GRID SIZES PER CHART TYPE
# ============================================

MINIMUM_GRID_SIZES: Dict[str, Dict[str, int]] = {
    "bar": {"width": 3, "height": 3},
    "line": {"width": 3, "height": 2},
    "pie": {"width": 3, "height": 3},
    "doughnut": {"width": 3, "height": 3},
    "area": {"width": 3, "height": 2},
    "scatter": {"width": 4, "height": 3},
    "radar": {"width": 4, "height": 4},
    "polarArea": {"width": 3, "height": 3},
}


# ============================================
# DATA LIMITS BY CHART TYPE AND SIZE
# ============================================

DATA_LIMITS: Dict[str, Dict[str, Dict[str, int]]] = {
    "bar": {
        "small": {"maxPoints": 4, "maxDatasets": 2},
        "medium": {"maxPoints": 8, "maxDatasets": 3},
        "large": {"maxPoints": 15, "maxDatasets": 5}
    },
    "line": {
        "small": {"maxPoints": 6, "maxDatasets": 2},
        "medium": {"maxPoints": 12, "maxDatasets": 3},
        "large": {"maxPoints": 24, "maxDatasets": 4}
    },
    "pie": {
        "small": {"maxPoints": 4, "maxDatasets": 1},
        "medium": {"maxPoints": 6, "maxDatasets": 1},
        "large": {"maxPoints": 8, "maxDatasets": 1}
    },
    "doughnut": {
        "small": {"maxPoints": 4, "maxDatasets": 1},
        "medium": {"maxPoints": 6, "maxDatasets": 1},
        "large": {"maxPoints": 8, "maxDatasets": 1}
    },
    "area": {
        "small": {"maxPoints": 6, "maxDatasets": 2},
        "medium": {"maxPoints": 12, "maxDatasets": 3},
        "large": {"maxPoints": 24, "maxDatasets": 4}
    },
    "scatter": {
        "small": {"maxPoints": 20, "maxDatasets": 2},
        "medium": {"maxPoints": 50, "maxDatasets": 3},
        "large": {"maxPoints": 100, "maxDatasets": 4}
    },
    "radar": {
        "small": {"maxPoints": 5, "maxDatasets": 2},
        "medium": {"maxPoints": 8, "maxDatasets": 3},
        "large": {"maxPoints": 10, "maxDatasets": 4}
    },
    "polarArea": {
        "small": {"maxPoints": 4, "maxDatasets": 1},
        "medium": {"maxPoints": 6, "maxDatasets": 1},
        "large": {"maxPoints": 8, "maxDatasets": 1}
    }
}

# Default limits for unknown chart types
DEFAULT_LIMITS: Dict[str, Dict[str, int]] = {
    "small": {"maxPoints": 4, "maxDatasets": 2},
    "medium": {"maxPoints": 8, "maxDatasets": 3},
    "large": {"maxPoints": 15, "maxDatasets": 4}
}


# ============================================
# CHART TYPE MAPPING
# ============================================

# Map Layout Service chart types to internal Analytics Service types
CHART_TYPE_MAPPING: Dict[str, str] = {
    "bar": "bar_vertical",
    "line": "line",
    "pie": "pie",
    "doughnut": "doughnut",
    "area": "area",
    "scatter": "scatter",
    "radar": "radar",
    "polarArea": "polar_area"
}

# Reverse mapping for response
INTERNAL_TO_LAYOUT_TYPE: Dict[str, str] = {v: k for k, v in CHART_TYPE_MAPPING.items()}


# ============================================
# FUNCTIONS
# ============================================

def get_layout_size(grid_width: int, grid_height: int) -> LayoutSize:
    """
    Calculate layout size category from grid dimensions.

    Size thresholds (from AI_SERVICE_CHART.md spec):
    - small: area <= 16 (e.g., 4x4 or 3x5)
    - medium: 16 < area <= 48 (e.g., 6x6 or 8x6)
    - large: area > 48 (e.g., 8x8 or 12x6)

    Args:
        grid_width: Width in grid units (1-12)
        grid_height: Height in grid units (1-8)

    Returns:
        LayoutSize enum value
    """
    area = grid_width * grid_height

    if area <= 16:
        return LayoutSize.SMALL
    elif area <= 48:
        return LayoutSize.MEDIUM
    else:
        return LayoutSize.LARGE


def get_data_limits(chart_type: str, grid_width: int, grid_height: int) -> Dict[str, int]:
    """
    Get data point and dataset limits for a chart type at given grid size.

    Args:
        chart_type: Layout Service chart type (bar, line, pie, etc.)
        grid_width: Width in grid units (1-12)
        grid_height: Height in grid units (1-8)

    Returns:
        Dict with 'maxPoints' and 'maxDatasets' keys
    """
    size = get_layout_size(grid_width, grid_height)

    # Get limits for chart type, fall back to defaults
    type_limits = DATA_LIMITS.get(chart_type, DEFAULT_LIMITS)
    size_limits = type_limits.get(size.value, DEFAULT_LIMITS[size.value])

    return {
        "maxPoints": size_limits.get("maxPoints", 10),
        "maxDatasets": size_limits.get("maxDatasets", 2)
    }


def validate_grid_size(chart_type: str, grid_width: int, grid_height: int) -> Tuple[bool, str]:
    """
    Validate that grid dimensions meet minimum requirements for chart type.

    Args:
        chart_type: Layout Service chart type (bar, line, pie, etc.)
        grid_width: Width in grid units (1-12)
        grid_height: Height in grid units (1-8)

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string
    """
    # Validate grid is within allowed range
    if grid_width < 1 or grid_width > 12:
        return False, f"gridWidth must be between 1 and 12, got {grid_width}"

    if grid_height < 1 or grid_height > 8:
        return False, f"gridHeight must be between 1 and 8, got {grid_height}"

    # Get minimum size for chart type
    min_size = MINIMUM_GRID_SIZES.get(chart_type)
    if min_size is None:
        # Unknown chart type - allow but warn
        return True, ""

    min_width = min_size["width"]
    min_height = min_size["height"]

    if grid_width < min_width:
        return False, f"Chart type '{chart_type}' requires minimum width of {min_width} grid units, got {grid_width}"

    if grid_height < min_height:
        return False, f"Chart type '{chart_type}' requires minimum height of {min_height} grid units, got {grid_height}"

    return True, ""


def get_minimum_grid_size(chart_type: str) -> Dict[str, int]:
    """
    Get minimum grid dimensions for a chart type.

    Args:
        chart_type: Layout Service chart type

    Returns:
        Dict with 'width' and 'height' keys
    """
    return MINIMUM_GRID_SIZES.get(chart_type, {"width": 3, "height": 3})


def map_chart_type_to_internal(chart_type: str) -> str:
    """
    Map Layout Service chart type to internal Analytics Service type.

    Args:
        chart_type: Layout Service chart type (bar, line, pie, etc.)

    Returns:
        Internal chart type (bar_vertical, line, pie, etc.)
    """
    return CHART_TYPE_MAPPING.get(chart_type, chart_type)


def map_internal_to_layout_type(internal_type: str) -> str:
    """
    Map internal Analytics Service type back to Layout Service type.

    Args:
        internal_type: Internal chart type (bar_vertical, polar_area, etc.)

    Returns:
        Layout Service chart type (bar, polarArea, etc.)
    """
    return INTERNAL_TO_LAYOUT_TYPE.get(internal_type, internal_type)


def truncate_data_to_limits(
    data: list,
    limits: Dict[str, int],
    chart_type: str = None
) -> list:
    """
    Truncate data to fit within size limits.

    Args:
        data: List of data points
        limits: Dict with 'maxPoints' key
        chart_type: Optional chart type for specific handling

    Returns:
        Truncated data list
    """
    max_points = limits.get("maxPoints", 50)

    if len(data) <= max_points:
        return data

    # For pie/doughnut, take top values to preserve meaningful data
    if chart_type in ["pie", "doughnut", "polarArea"]:
        # Sort by value (descending) and take top N
        try:
            sorted_data = sorted(data, key=lambda x: x.get("value", 0) if isinstance(x, dict) else 0, reverse=True)
            return sorted_data[:max_points]
        except (TypeError, KeyError):
            pass

    # For other types, take evenly spaced samples
    if len(data) > max_points:
        step = len(data) / max_points
        indices = [int(i * step) for i in range(max_points)]
        return [data[i] for i in indices]

    return data[:max_points]


def get_all_minimum_grid_sizes() -> Dict[str, Dict[str, int]]:
    """
    Get minimum grid sizes for all chart types.

    Returns:
        Dict mapping chart type to minimum width/height
    """
    return MINIMUM_GRID_SIZES.copy()


def get_all_data_limits() -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Get data limits for all chart types and sizes.

    Returns:
        Complete DATA_LIMITS dictionary
    """
    return DATA_LIMITS.copy()
