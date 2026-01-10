"""
Element Positioner for Atomic Charts
=====================================
v1.0.0: Initial implementation for Analytics v3.7.0

Calculates optimal grid positions for chart elements using
the 32x18 grid system. Implements top-down, left-right stacking.

Grid System:
- 32 columns × 18 rows
- Content area: rows 4-17, columns 2-30
- Reserved: row 1 (margin), rows 2-3 (title), row 18 (footer)
- Reserved: column 1 (left margin), columns 31-32 (right margin)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class GridSize:
    """Grid dimensions in grid units."""
    cols: int  # Number of columns
    rows: int  # Number of rows


@dataclass
class GridPosition:
    """Grid position in CSS grid notation."""
    grid_row: str      # e.g., "4/14" means rows 4-13
    grid_column: str   # e.g., "2/16" means columns 2-15

    def to_dict(self) -> Dict[str, str]:
        return {
            "grid_row": self.grid_row,
            "grid_column": self.grid_column
        }


# Chart type to recommended grid size (cols × rows)
# Sizes are optimized for each chart type's visual characteristics
CHART_TYPE_SIZES: Dict[str, GridSize] = {
    # Line/Area charts - wide for trend visibility
    "line": GridSize(cols=14, rows=10),
    "area": GridSize(cols=14, rows=10),
    "area_stacked": GridSize(cols=14, rows=10),

    # Bar charts
    "bar_vertical": GridSize(cols=12, rows=11),
    "bar_horizontal": GridSize(cols=14, rows=10),
    "bar_stacked": GridSize(cols=12, rows=11),
    "bar_grouped": GridSize(cols=14, rows=10),

    # Circular charts - square aspect ratio
    "pie": GridSize(cols=10, rows=10),
    "doughnut": GridSize(cols=10, rows=10),
    "polar_area": GridSize(cols=10, rows=10),
    "radar": GridSize(cols=10, rows=10),

    # Scatter/Bubble - balanced
    "scatter": GridSize(cols=12, rows=10),
    "bubble": GridSize(cols=12, rows=10),

    # Special charts
    "funnel": GridSize(cols=10, rows=12),
    "waterfall": GridSize(cols=14, rows=11),
    "treemap": GridSize(cols=14, rows=10),
    "gauge": GridSize(cols=8, rows=8),
    "histogram": GridSize(cols=12, rows=10),

    # Default fallback
    "default": GridSize(cols=12, rows=10),
}

# Padding to add around chart content (in grid units)
ELEMENT_PADDING = 1


class ElementPositioner:
    """
    Calculate optimal grid positions for new chart elements.

    Uses top-down, left-right stacking algorithm within the
    content area of a 32×18 grid slide.
    """

    # Content area boundaries (1-indexed grid lines)
    CONTENT_AREA = {
        "row_start": 4,    # First available row (after title/subtitle)
        "row_end": 17,     # Last available row (before footer)
        "col_start": 2,    # First available column (after left margin)
        "col_end": 30,     # Last available column (before right margin)
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ElementPositioner")

    def get_chart_size(self, chart_type: str, include_padding: bool = True) -> GridSize:
        """
        Get the recommended grid size for a chart type.

        Args:
            chart_type: The type of chart (e.g., "line", "pie", "bar_vertical")
            include_padding: Whether to add padding around the chart

        Returns:
            GridSize with columns and rows for the element
        """
        # Normalize chart type
        chart_type_lower = chart_type.lower().replace("-", "_")

        # Get base size or default
        base_size = CHART_TYPE_SIZES.get(chart_type_lower, CHART_TYPE_SIZES["default"])

        if include_padding:
            return GridSize(
                cols=base_size.cols + ELEMENT_PADDING,
                rows=base_size.rows + ELEMENT_PADDING
            )
        return base_size

    def calculate_position(
        self,
        element_size: GridSize,
        existing_elements: Optional[List[Dict]] = None
    ) -> GridPosition:
        """
        Calculate the next available position for a new element.

        Uses top-down, left-right stacking:
        1. Start at top-left of content area (row 4, col 2)
        2. Try positions going down first
        3. If column is full, move to next column band

        Args:
            element_size: Size of the new element (with padding)
            existing_elements: List of existing elements with position info.
                              Each dict should have 'grid_row' and 'grid_column'.

        Returns:
            GridPosition for the new element

        Raises:
            ValueError: If no space is available in the content area
        """
        existing = existing_elements or []

        # Parse existing element positions
        occupied_regions = self._parse_existing_elements(existing)

        self.logger.debug(
            f"Finding position for element size {element_size.cols}x{element_size.rows}, "
            f"existing regions: {len(occupied_regions)}"
        )

        # Scan top-to-bottom, then left-to-right
        col = self.CONTENT_AREA["col_start"]

        while col + element_size.cols <= self.CONTENT_AREA["col_end"] + 1:
            row = self.CONTENT_AREA["row_start"]

            while row + element_size.rows <= self.CONTENT_AREA["row_end"] + 1:
                # Check if this position is free
                if not self._overlaps_any(row, col, element_size, occupied_regions):
                    position = GridPosition(
                        grid_row=f"{row}/{row + element_size.rows}",
                        grid_column=f"{col}/{col + element_size.cols}"
                    )
                    self.logger.info(
                        f"Found position: row={position.grid_row}, col={position.grid_column}"
                    )
                    return position

                # Try next row down
                row += 1

            # Column band is full, move to next band
            # Jump by element width to avoid partial overlaps
            col += element_size.cols

        raise ValueError(
            f"No space available for element of size {element_size.cols}x{element_size.rows}. "
            f"Content area is full."
        )

    def _parse_existing_elements(self, elements: List[Dict]) -> List[Tuple[int, int, int, int]]:
        """
        Parse existing element positions into (row_start, row_end, col_start, col_end) tuples.

        Args:
            elements: List of element dicts with 'grid_row' and 'grid_column'
                     OR 'position' dict containing those fields

        Returns:
            List of (row_start, row_end, col_start, col_end) tuples
        """
        regions = []

        for elem in elements:
            try:
                # Handle both flat and nested position formats
                if 'position' in elem:
                    grid_row = elem['position'].get('grid_row', '')
                    grid_col = elem['position'].get('grid_column', '')
                else:
                    grid_row = elem.get('grid_row', '')
                    grid_col = elem.get('grid_column', '')

                if not grid_row or not grid_col:
                    continue

                # Parse "start/end" format
                row_parts = grid_row.split('/')
                col_parts = grid_col.split('/')

                if len(row_parts) == 2 and len(col_parts) == 2:
                    row_start, row_end = int(row_parts[0]), int(row_parts[1])
                    col_start, col_end = int(col_parts[0]), int(col_parts[1])
                    regions.append((row_start, row_end, col_start, col_end))

            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Failed to parse element position: {elem}, error: {e}")
                continue

        return regions

    def _overlaps_any(
        self,
        row: int,
        col: int,
        size: GridSize,
        occupied_regions: List[Tuple[int, int, int, int]]
    ) -> bool:
        """
        Check if a proposed position overlaps with any existing element.

        Args:
            row: Starting row for new element
            col: Starting column for new element
            size: Size of new element
            occupied_regions: List of (row_start, row_end, col_start, col_end) tuples

        Returns:
            True if there's an overlap, False otherwise
        """
        new_row_start = row
        new_row_end = row + size.rows
        new_col_start = col
        new_col_end = col + size.cols

        for (row_start, row_end, col_start, col_end) in occupied_regions:
            # Check for overlap (rectangles overlap if they don't NOT overlap)
            rows_overlap = not (new_row_end <= row_start or new_row_start >= row_end)
            cols_overlap = not (new_col_end <= col_start or new_col_start >= col_end)

            if rows_overlap and cols_overlap:
                return True

        return False

    def get_content_area_info(self) -> Dict:
        """Get information about the content area boundaries."""
        return {
            "row_start": self.CONTENT_AREA["row_start"],
            "row_end": self.CONTENT_AREA["row_end"],
            "col_start": self.CONTENT_AREA["col_start"],
            "col_end": self.CONTENT_AREA["col_end"],
            "available_rows": self.CONTENT_AREA["row_end"] - self.CONTENT_AREA["row_start"],
            "available_cols": self.CONTENT_AREA["col_end"] - self.CONTENT_AREA["col_start"],
            "pixels_height": (self.CONTENT_AREA["row_end"] - self.CONTENT_AREA["row_start"]) * 60,
            "pixels_width": (self.CONTENT_AREA["col_end"] - self.CONTENT_AREA["col_start"]) * 60,
        }


# Convenience function for direct usage
def get_chart_position(
    chart_type: str,
    existing_elements: Optional[List[Dict]] = None
) -> Dict[str, str]:
    """
    Get the position for a new chart element.

    Args:
        chart_type: Type of chart (e.g., "line", "pie")
        existing_elements: List of existing element positions

    Returns:
        Dict with 'grid_row' and 'grid_column' keys
    """
    positioner = ElementPositioner()
    size = positioner.get_chart_size(chart_type)
    position = positioner.calculate_position(size, existing_elements)
    return position.to_dict()


def get_chart_size_for_type(chart_type: str, include_padding: bool = True) -> Dict[str, int]:
    """
    Get the grid size for a chart type.

    Args:
        chart_type: Type of chart
        include_padding: Whether to include padding

    Returns:
        Dict with 'cols' and 'rows' keys
    """
    positioner = ElementPositioner()
    size = positioner.get_chart_size(chart_type, include_padding)
    return {"cols": size.cols, "rows": size.rows}
