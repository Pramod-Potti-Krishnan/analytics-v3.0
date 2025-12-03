"""
Layout Service Palette Mapping
==============================

Color palette mapping from AI_SERVICE_CHART.md specification to
internal Analytics Service themes.

Author: Analytics Microservice v3 Team
Date: 2025-12
"""

from typing import Dict, List, Optional


# ============================================
# FRONTEND PALETTES (from AI_SERVICE_CHART.md)
# ============================================

FRONTEND_PALETTES: Dict[str, List[str]] = {
    "default": [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Yellow
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#F97316"   # Orange
    ],

    "professional": [
        "#1E40AF",  # Dark Blue
        "#166534",  # Dark Green
        "#B45309",  # Dark Yellow
        "#991B1B",  # Dark Red
        "#5B21B6",  # Dark Purple
        "#9D174D",  # Dark Pink
        "#0E7490",  # Dark Cyan
        "#C2410C"   # Dark Orange
    ],

    "vibrant": [
        "#2563EB",  # Bright Blue
        "#059669",  # Bright Green
        "#D97706",  # Bright Yellow
        "#DC2626",  # Bright Red
        "#7C3AED",  # Bright Purple
        "#DB2777",  # Bright Pink
        "#0891B2",  # Bright Cyan
        "#EA580C"   # Bright Orange
    ],

    "pastel": [
        "#93C5FD",  # Light Blue
        "#86EFAC",  # Light Green
        "#FCD34D",  # Light Yellow
        "#FCA5A5",  # Light Red
        "#C4B5FD",  # Light Purple
        "#F9A8D4",  # Light Pink
        "#67E8F9",  # Light Cyan
        "#FDBA74"   # Light Orange
    ],

    "monochrome": [
        "#1F2937",  # Gray 800
        "#374151",  # Gray 700
        "#4B5563",  # Gray 600
        "#6B7280",  # Gray 500
        "#9CA3AF",  # Gray 400
        "#D1D5DB",  # Gray 300
        "#E5E7EB",  # Gray 200
        "#F3F4F6"   # Gray 100
    ],

    "sequential": [
        "#EFF6FF",  # Blue 50
        "#DBEAFE",  # Blue 100
        "#BFDBFE",  # Blue 200
        "#93C5FD",  # Blue 300
        "#60A5FA",  # Blue 400
        "#3B82F6",  # Blue 500
        "#2563EB",  # Blue 600
        "#1D4ED8"   # Blue 700
    ],

    "diverging": [
        "#DC2626",  # Red
        "#F87171",  # Red Light
        "#FCA5A5",  # Red Lighter
        "#FEE2E2",  # Red Lightest
        "#DCFCE7",  # Green Lightest
        "#86EFAC",  # Green Lighter
        "#4ADE80",  # Green Light
        "#22C55E"   # Green
    ],

    "categorical": [
        "#0088FE",  # Blue
        "#00C49F",  # Teal
        "#FFBB28",  # Yellow
        "#FF8042",  # Orange
        "#8884D8",  # Purple
        "#82CA9D",  # Green
        "#FFC0CB",  # Pink
        "#A4DE6C"   # Lime
    ]
}


# ============================================
# PALETTE TO INTERNAL THEME MAPPING
# ============================================

# Maps frontend palette names to internal ChartJSGenerator theme names
PALETTE_TO_THEME: Dict[str, str] = {
    "default": "professional",
    "professional": "professional",
    "vibrant": "vibrant",
    "pastel": "professional",      # Use professional theme structure with pastel colors
    "monochrome": "corporate",     # Corporate theme has formal feel
    "sequential": "professional",  # Use professional for sequential
    "diverging": "professional",   # Use professional for diverging
    "categorical": "vibrant"       # Vibrant works well for categorical
}


# ============================================
# FUNCTIONS
# ============================================

def get_palette_colors(
    palette: str,
    count: int = 8,
    custom_colors: Optional[List[str]] = None
) -> List[str]:
    """
    Get color array for specified palette.

    Args:
        palette: Palette name (default, professional, vibrant, pastel, etc.)
        count: Number of colors needed
        custom_colors: Override with custom colors if provided

    Returns:
        List of hex color strings
    """
    # Use custom colors if provided and sufficient
    if custom_colors and len(custom_colors) >= count:
        return custom_colors[:count]

    # Get palette colors
    colors = FRONTEND_PALETTES.get(palette, FRONTEND_PALETTES["default"])

    # If need more colors than palette has, cycle through
    if count > len(colors):
        result = []
        for i in range(count):
            result.append(colors[i % len(colors)])
        return result

    return colors[:count]


def get_internal_theme(palette: str) -> str:
    """
    Get internal ChartJSGenerator theme name for a palette.

    Args:
        palette: Frontend palette name

    Returns:
        Internal theme name (professional, corporate, or vibrant)
    """
    return PALETTE_TO_THEME.get(palette, "professional")


def get_background_colors(
    palette: str,
    count: int,
    opacity: float = 1.0,
    custom_colors: Optional[List[str]] = None
) -> List[str]:
    """
    Get background colors with optional opacity.

    Args:
        palette: Palette name
        count: Number of colors needed
        opacity: Opacity value (0.0 to 1.0)
        custom_colors: Override with custom colors

    Returns:
        List of color strings (hex or rgba if opacity < 1)
    """
    colors = get_palette_colors(palette, count, custom_colors)

    if opacity >= 1.0:
        return colors

    # Convert to rgba with opacity
    result = []
    for color in colors:
        rgba = hex_to_rgba(color, opacity)
        result.append(rgba)
    return result


def get_border_colors(
    palette: str,
    count: int,
    custom_colors: Optional[List[str]] = None
) -> List[str]:
    """
    Get border colors (same as palette colors, full opacity).

    Args:
        palette: Palette name
        count: Number of colors needed
        custom_colors: Override with custom colors

    Returns:
        List of hex color strings
    """
    return get_palette_colors(palette, count, custom_colors)


def hex_to_rgba(hex_color: str, opacity: float = 1.0) -> str:
    """
    Convert hex color to rgba string.

    Args:
        hex_color: Hex color string (e.g., "#3B82F6")
        opacity: Opacity value (0.0 to 1.0)

    Returns:
        RGBA color string (e.g., "rgba(59, 130, 246, 0.5)")
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')

    # Handle short hex (e.g., #FFF)
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])

    # Convert to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r}, {g}, {b}, {opacity})"


def interpolate_colors(colors: List[str], count: int) -> List[str]:
    """
    Interpolate between colors to generate more colors.

    For now, this just cycles through colors.
    Future enhancement: actual color interpolation.

    Args:
        colors: Base color list
        count: Number of colors needed

    Returns:
        List of colors with specified count
    """
    if count <= len(colors):
        return colors[:count]

    result = []
    for i in range(count):
        result.append(colors[i % len(colors)])
    return result


def get_chart_colors_for_type(
    chart_type: str,
    palette: str,
    data_count: int,
    custom_colors: Optional[List[str]] = None
) -> Dict[str, List[str]]:
    """
    Get appropriate colors for a specific chart type.

    Different chart types need different color configurations:
    - Pie/Doughnut/PolarArea: Array of colors (one per slice)
    - Bar/Line: Single color or array
    - Scatter/Bubble: Single color per dataset

    Args:
        chart_type: Type of chart (bar, line, pie, etc.)
        palette: Palette name
        data_count: Number of data points or slices
        custom_colors: Override colors

    Returns:
        Dict with 'backgroundColor' and 'borderColor' lists
    """
    colors = get_palette_colors(palette, data_count, custom_colors)

    if chart_type in ["pie", "doughnut", "polarArea"]:
        # Each slice gets its own color
        return {
            "backgroundColor": get_background_colors(palette, data_count, 0.8, custom_colors),
            "borderColor": colors,
            "borderWidth": 2
        }
    elif chart_type in ["line", "area"]:
        # Single color with fill opacity
        return {
            "backgroundColor": get_background_colors(palette, 1, 0.2, custom_colors),
            "borderColor": colors[:1],
            "borderWidth": 2
        }
    elif chart_type in ["scatter", "bubble"]:
        # Points with opacity
        return {
            "backgroundColor": get_background_colors(palette, data_count, 0.6, custom_colors),
            "borderColor": colors,
            "borderWidth": 1
        }
    elif chart_type == "radar":
        # Filled area with low opacity
        return {
            "backgroundColor": get_background_colors(palette, 1, 0.2, custom_colors),
            "borderColor": colors[:1],
            "borderWidth": 2,
            "pointBackgroundColor": colors[:1]
        }
    else:
        # Default (bar, etc.): solid colors
        return {
            "backgroundColor": colors,
            "borderColor": colors,
            "borderWidth": 1
        }


def get_available_palettes() -> List[str]:
    """
    Get list of all available palette names.

    Returns:
        List of palette names
    """
    return list(FRONTEND_PALETTES.keys())


def get_palette_preview(palette: str) -> Dict[str, any]:
    """
    Get palette information for preview/documentation.

    Args:
        palette: Palette name

    Returns:
        Dict with palette name, colors, and mapped theme
    """
    return {
        "name": palette,
        "colors": FRONTEND_PALETTES.get(palette, FRONTEND_PALETTES["default"]),
        "internalTheme": get_internal_theme(palette),
        "colorCount": len(FRONTEND_PALETTES.get(palette, []))
    }
