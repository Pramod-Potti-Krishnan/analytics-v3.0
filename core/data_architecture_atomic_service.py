"""
Data Architecture Atomic Service for Analytics Microservice v1.0.0

Generates HTML visualization for Entity-Relationship (ER) diagrams.
Produces self-contained HTML with entity cards, SVG relationship paths,
and crow's foot notation markers.

v1.0.0 Initial Release:
- Entity card rendering with field lists
- SVG crow's foot markers for cardinality
- Bezier curve relationship paths
- Light/dark theme support via CSS variables
- Drag/drop entity repositioning
- Edit panel for entity/relationship modifications
- postMessage protocol for persistence
"""

import logging
import time
import uuid
import json
import html
from typing import Dict, Any, List, Optional, Tuple

from models.data_architecture_atomic_models import (
    DataArchitectureAtomicRequest,
    DataArchitectureAtomicResponse,
    DataEntity,
    DataField,
    DataRelationship,
    DATA_ARCH_POSITION_PRESETS
)

logger = logging.getLogger(__name__)

# Grid system constants
GRID_UNIT_PX = 60  # 1 grid unit = 60 pixels


class DataArchitectureAtomicService:
    """
    Generate atomic DATA_ARCHITECTURE HTML elements.

    Creates self-contained ER diagram visualizations with:
    - Entity cards showing table structure
    - SVG paths with crow's foot notation
    - Interactive drag/drop and editing
    - Theme-aware styling
    """

    # Entity type colors (default palette)
    ENTITY_COLORS = {
        "table": "#3B82F6",     # Blue
        "view": "#8B5CF6",      # Purple
        "enum": "#10B981",      # Green
        "junction": "#F59E0B"   # Amber
    }

    # Cardinality marker definitions
    CARDINALITY_MARKERS = {
        "one_to_one": ("one", "one"),
        "one_to_many": ("one", "many"),
        "many_to_one": ("many", "one"),
        "many_to_many": ("many", "many"),
        "zero_or_one": ("zero", "one"),
        "zero_or_many": ("zero", "many")
    }

    def __init__(self):
        """Initialize the Data Architecture service."""
        pass

    def generate(
        self,
        request: DataArchitectureAtomicRequest,
        entities: List[DataEntity],
        relationships: List[DataRelationship],
        title: str,
        source: str
    ) -> DataArchitectureAtomicResponse:
        """
        Generate DATA_ARCHITECTURE HTML visualization.

        Args:
            request: Original request with display options
            entities: List of entity definitions
            relationships: List of relationship definitions
            title: Diagram title
            source: Data source ("explicit", "llm", or "placeholder")

        Returns:
            DataArchitectureAtomicResponse with HTML content
        """
        start_time = time.time()

        # Generate or use provided element_id
        if request.element_id:
            element_id = request.element_id
            logger.info(f"Using provided element_id: {element_id}")
        else:
            short_uuid = uuid.uuid4().hex[:8]
            element_id = f"data-arch-{request.presentation_id}-{request.slide_id}-{request.diagram_index}-{short_uuid}"
            logger.info(f"Generated new element_id: {element_id}")

        # Calculate grid position
        grid_position = self._calculate_grid_position(request)

        # Calculate pixel dimensions
        if grid_position:
            width_px = grid_position['width'] * GRID_UNIT_PX - 20
            height_px = grid_position['height'] * GRID_UNIT_PX - 20
        else:
            width_px = request.gridWidth * GRID_UNIT_PX - 20
            height_px = request.gridHeight * GRID_UNIT_PX - 20

        # Generate HTML
        html_content = self._generate_html(
            element_id=element_id,
            entities=entities,
            relationships=relationships,
            title=title,
            theme_mode=request.theme_mode,
            show_data_types=request.show_data_types,
            show_nullable=request.show_nullable,
            show_title=request.show_title,
            enable_editor=request.enable_editor,
            width_px=width_px,
            height_px=height_px,
            presentation_id=request.presentation_id
        )

        generation_time_ms = int((time.time() - start_time) * 1000)

        return DataArchitectureAtomicResponse(
            success=True,
            diagram_type="data_architecture",
            html_content=html_content,
            entities=[e.model_dump() for e in entities],
            relationships=[r.model_dump() for r in relationships],
            title=title,
            generation_time_ms=generation_time_ms,
            element_id=element_id,
            source=source,
            grid_position=grid_position
        )

    def _calculate_grid_position(self, request: DataArchitectureAtomicRequest) -> Optional[Dict[str, Any]]:
        """Calculate grid position from request parameters."""
        # Apply preset if specified
        if request.position_preset:
            preset = DATA_ARCH_POSITION_PRESETS[request.position_preset]
            start_col = preset["start_col"]
            start_row = preset["start_row"]
            width = preset["gridWidth"]
            height = preset["gridHeight"]
        elif request.start_col is not None or request.start_row is not None:
            start_col = request.start_col if request.start_col is not None else 2
            start_row = request.start_row if request.start_row is not None else 4
            width = request.gridWidth
            height = request.gridHeight
        else:
            return None

        end_row = min(start_row + height, 19)
        end_col = min(start_col + width, 33)

        return {
            "start_col": start_col,
            "start_row": start_row,
            "width": width,
            "height": height,
            "grid_row": f"{start_row}/{end_row}",
            "grid_column": f"{start_col}/{end_col}"
        }

    def _generate_html(
        self,
        element_id: str,
        entities: List[DataEntity],
        relationships: List[DataRelationship],
        title: str,
        theme_mode: str,
        show_data_types: bool,
        show_nullable: bool,
        show_title: bool,
        enable_editor: bool,
        width_px: int,
        height_px: int,
        presentation_id: str
    ) -> str:
        """Generate complete HTML with CSS and JavaScript."""
        js_safe_id = element_id.replace('-', '_')

        # Generate CSS
        css = self._generate_css(theme_mode)

        # Generate SVG markers
        svg_markers = self._generate_svg_markers(theme_mode)

        # Generate entity cards
        entity_html = self._generate_entities_html(
            entities, show_data_types, show_nullable
        )

        # Build entity lookup for relationship rendering
        entity_lookup = {e.id: e for e in entities}

        # Generate relationship paths
        relationship_svg = self._generate_relationships_svg(
            relationships, entity_lookup
        )

        # Generate title HTML
        title_html = ""
        if show_title and title:
            escaped_title = html.escape(title)
            title_html = f'''<h3 class="diagram-title">{escaped_title}</h3>'''

        # Generate edit button
        edit_button = ""
        if enable_editor:
            edit_button = self._generate_edit_button(js_safe_id)

        # Generate JavaScript
        js_code = self._generate_javascript(
            element_id, js_safe_id, entities, relationships, presentation_id, enable_editor
        )

        # Assemble final HTML
        theme_class = "theme-dark" if theme_mode == "dark" else "theme-light"

        return f'''<div class="data-architecture-container {theme_class}"
     id="{element_id}"
     data-element-id="{element_id}"
     data-diagram-type="data_architecture"
     style="width: 100%; height: 100%; position: relative; overflow: hidden; box-sizing: border-box;">
  <style>{css}</style>
  {title_html}
  <div class="diagram-canvas" style="width: 100%; height: calc(100% - {40 if show_title else 0}px); position: relative; overflow: hidden;">
    <svg class="relationship-layer" width="100%" height="100%" style="position: absolute; top: 0; left: 0; pointer-events: none;">
      {svg_markers}
      <g class="relationships">
        {relationship_svg}
      </g>
    </svg>
    <div class="entities-layer" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
      {entity_html}
    </div>
  </div>
  {edit_button}
  <script>{js_code}</script>
</div>'''

    def _generate_css(self, theme_mode: str) -> str:
        """Generate CSS with theme variables."""
        return '''
/* DATA_ARCHITECTURE Theme Variables */
.theme-light {
    --da-bg-color: #FFFFFF;
    --da-text-primary: #111827;
    --da-text-secondary: #6B7280;
    --da-entity-bg: #FFFFFF;
    --da-entity-border: #E5E7EB;
    --da-entity-header-bg: #F3F4F6;
    --da-field-pk-color: #F59E0B;
    --da-field-fk-color: #3B82F6;
    --da-field-hover-bg: #F9FAFB;
    --da-rel-color: #6B7280;
    --da-rel-optional-color: #9CA3AF;
    --da-shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
    --da-shadow-hover: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06);
}

.theme-dark {
    --da-bg-color: #111827;
    --da-text-primary: #F9FAFB;
    --da-text-secondary: #9CA3AF;
    --da-entity-bg: #1F2937;
    --da-entity-border: #374151;
    --da-entity-header-bg: #374151;
    --da-field-pk-color: #FBBF24;
    --da-field-fk-color: #60A5FA;
    --da-field-hover-bg: #374151;
    --da-rel-color: #9CA3AF;
    --da-rel-optional-color: #6B7280;
    --da-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
    --da-shadow-hover: 0 4px 6px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3);
}

.data-architecture-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--da-bg-color);
    color: var(--da-text-primary);
}

.diagram-title {
    margin: 10px 0 10px 20px;
    padding: 0;
    font-size: 18px;
    font-weight: 600;
    color: var(--da-text-primary);
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Entity Card Styles */
.data-entity {
    position: absolute;
    min-width: 160px;
    max-width: 280px;
    background: var(--da-entity-bg);
    border: 1px solid var(--da-entity-border);
    border-radius: 8px;
    box-shadow: var(--da-shadow);
    cursor: move;
    transition: box-shadow 0.2s ease, transform 0.1s ease;
    z-index: 10;
}

.data-entity:hover {
    box-shadow: var(--da-shadow-hover);
}

.data-entity.dragging {
    z-index: 100;
    transform: scale(1.02);
    box-shadow: var(--da-shadow-hover);
}

.entity-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    background: var(--da-entity-header-bg);
    border-bottom: 1px solid var(--da-entity-border);
    border-radius: 7px 7px 0 0;
}

.entity-name {
    font-weight: 600;
    font-size: 13px;
    color: var(--da-text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.entity-type-badge {
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    background: var(--entity-accent, #3B82F6);
    color: white;
    margin-left: 8px;
    flex-shrink: 0;
}

.entity-fields {
    padding: 4px 0;
    max-height: 200px;
    overflow-y: auto;
}

.entity-field {
    display: flex;
    align-items: center;
    padding: 4px 12px;
    font-size: 12px;
    gap: 6px;
    transition: background 0.15s ease;
}

.entity-field:hover {
    background: var(--da-field-hover-bg);
}

.field-icon {
    width: 14px;
    flex-shrink: 0;
    font-size: 10px;
}

.field-name {
    font-weight: 500;
    color: var(--da-text-primary);
    flex-shrink: 0;
}

.field-type {
    color: var(--da-text-secondary);
    font-size: 11px;
    margin-left: auto;
    font-family: 'Monaco', 'Menlo', monospace;
}

.field-nullable {
    color: var(--da-text-secondary);
    font-size: 10px;
    opacity: 0.7;
}

.entity-field.pk .field-icon { color: var(--da-field-pk-color); }
.entity-field.fk .field-icon { color: var(--da-field-fk-color); }

/* Relationship Path Styles */
.relationship-path {
    fill: none;
    stroke: var(--da-rel-color);
    stroke-width: 1.5;
    transition: stroke-width 0.2s ease;
}

.relationship-path:hover {
    stroke-width: 2.5;
}

.relationship-path.optional {
    stroke-dasharray: 5, 5;
    stroke: var(--da-rel-optional-color);
}

.relationship-label {
    font-size: 10px;
    fill: var(--da-text-secondary);
    text-anchor: middle;
}

/* Edit Button */
.da-edit-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(0,0,0,0.7);
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    z-index: 100;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 6px;
}

.da-edit-btn:hover {
    background: rgba(0,0,0,0.9);
    transform: scale(1.05);
}
'''

    def _generate_svg_markers(self, theme_mode: str) -> str:
        """Generate SVG marker definitions for crow's foot notation."""
        rel_color = "#9CA3AF" if theme_mode == "dark" else "#6B7280"

        return f'''<defs>
  <!-- One (|) marker -->
  <marker id="marker-one" viewBox="0 0 10 10" refX="10" refY="5"
          markerWidth="10" markerHeight="10" orient="auto-start-reverse">
    <line x1="10" y1="0" x2="10" y2="10" stroke="{rel_color}" stroke-width="2"/>
  </marker>

  <!-- Many (<) marker - Crow's Foot -->
  <marker id="marker-many" viewBox="0 0 14 10" refX="14" refY="5"
          markerWidth="14" markerHeight="10" orient="auto-start-reverse">
    <path d="M 0 5 L 14 0 M 0 5 L 14 10 M 0 5 L 14 5"
          stroke="{rel_color}" stroke-width="1.5" fill="none"/>
  </marker>

  <!-- Zero (o) marker -->
  <marker id="marker-zero" viewBox="0 0 12 10" refX="0" refY="5"
          markerWidth="12" markerHeight="10" orient="auto-start-reverse">
    <circle cx="6" cy="5" r="4" stroke="{rel_color}" fill="none" stroke-width="1.5"/>
  </marker>

  <!-- Combined markers -->
  <marker id="marker-zero-one" viewBox="0 0 22 10" refX="22" refY="5"
          markerWidth="22" markerHeight="10" orient="auto-start-reverse">
    <circle cx="6" cy="5" r="4" stroke="{rel_color}" fill="none" stroke-width="1.5"/>
    <line x1="14" y1="0" x2="14" y2="10" stroke="{rel_color}" stroke-width="2"/>
  </marker>

  <marker id="marker-zero-many" viewBox="0 0 26 10" refX="26" refY="5"
          markerWidth="26" markerHeight="10" orient="auto-start-reverse">
    <circle cx="6" cy="5" r="4" stroke="{rel_color}" fill="none" stroke-width="1.5"/>
    <path d="M 12 5 L 26 0 M 12 5 L 26 10 M 12 5 L 26 5"
          stroke="{rel_color}" stroke-width="1.5" fill="none"/>
  </marker>
</defs>'''

    def _generate_entities_html(
        self,
        entities: List[DataEntity],
        show_data_types: bool,
        show_nullable: bool
    ) -> str:
        """Generate HTML for all entity cards."""
        html_parts = []

        for entity in entities:
            entity_html = self._generate_entity_card(
                entity, show_data_types, show_nullable
            )
            html_parts.append(entity_html)

        return '\n'.join(html_parts)

    def _generate_entity_card(
        self,
        entity: DataEntity,
        show_data_types: bool,
        show_nullable: bool
    ) -> str:
        """Generate HTML for a single entity card."""
        entity_color = entity.color or self.ENTITY_COLORS.get(entity.type, "#3B82F6")
        escaped_name = html.escape(entity.name)
        entity_type = entity.type.upper()

        # Generate fields HTML
        fields_html = []
        for field in entity.fields:
            field_html = self._generate_field_html(
                field, show_data_types, show_nullable
            )
            fields_html.append(field_html)

        fields_content = '\n'.join(fields_html) if fields_html else '<div class="entity-field" style="color: var(--da-text-secondary); font-style: italic;">No fields defined</div>'

        return f'''<div class="data-entity"
     data-entity-id="{entity.id}"
     style="left: {entity.x_position}%; top: {entity.y_position}%; --entity-accent: {entity_color};">
  <div class="entity-header">
    <span class="entity-name">{escaped_name}</span>
    <span class="entity-type-badge" style="background: {entity_color};">{entity_type}</span>
  </div>
  <div class="entity-fields">
    {fields_content}
  </div>
</div>'''

    def _generate_field_html(
        self,
        field: DataField,
        show_data_types: bool,
        show_nullable: bool
    ) -> str:
        """Generate HTML for a single field row."""
        classes = ["entity-field"]
        icon = ""

        if field.is_primary_key:
            classes.append("pk")
            icon = "🔑"
        elif field.is_foreign_key:
            classes.append("fk")
            icon = "🔗"

        escaped_name = html.escape(field.name)

        type_html = ""
        if show_data_types:
            escaped_type = html.escape(field.data_type)
            type_html = f'<span class="field-type">{escaped_type}</span>'

        nullable_html = ""
        if show_nullable and field.is_nullable and not field.is_primary_key:
            nullable_html = '<span class="field-nullable">NULL</span>'

        return f'''<div class="{' '.join(classes)}">
  <span class="field-icon">{icon}</span>
  <span class="field-name">{escaped_name}</span>
  {type_html}
  {nullable_html}
</div>'''

    def _generate_relationships_svg(
        self,
        relationships: List[DataRelationship],
        entity_lookup: Dict[str, DataEntity]
    ) -> str:
        """Generate SVG paths for all relationships."""
        paths = []

        for rel in relationships:
            from_entity = entity_lookup.get(rel.from_entity)
            to_entity = entity_lookup.get(rel.to_entity)

            if not from_entity or not to_entity:
                logger.warning(f"Relationship {rel.id} references missing entity")
                continue

            path_html = self._generate_relationship_path(rel, from_entity, to_entity)
            paths.append(path_html)

        return '\n'.join(paths)

    def _generate_relationship_path(
        self,
        rel: DataRelationship,
        from_entity: DataEntity,
        to_entity: DataEntity
    ) -> str:
        """Generate SVG path for a single relationship with crow's foot markers."""
        # Calculate connection points (percentage-based)
        from_x = from_entity.x_position
        from_y = from_entity.y_position
        to_x = to_entity.x_position
        to_y = to_entity.y_position

        # Determine markers based on cardinality
        start_marker, end_marker = self.CARDINALITY_MARKERS.get(
            rel.cardinality, ("one", "many")
        )

        # Build marker references
        if rel.cardinality == "zero_or_one":
            end_marker_url = "url(#marker-zero-one)"
            start_marker_url = "url(#marker-one)"
        elif rel.cardinality == "zero_or_many":
            end_marker_url = "url(#marker-zero-many)"
            start_marker_url = "url(#marker-one)"
        else:
            start_marker_url = f"url(#marker-{start_marker})"
            end_marker_url = f"url(#marker-{end_marker})"

        # Optional styling
        optional_class = " optional" if rel.is_optional else ""

        # Label
        label_html = ""
        if rel.label:
            mid_x = (from_x + to_x) / 2
            mid_y = (from_y + to_y) / 2
            escaped_label = html.escape(rel.label)
            label_html = f'<text class="relationship-label" x="{mid_x}%" y="{mid_y}%">{escaped_label}</text>'

        # Path data uses JavaScript to calculate actual pixel positions
        return f'''<g class="relationship-group" data-rel-id="{rel.id}"
   data-from-entity="{rel.from_entity}" data-to-entity="{rel.to_entity}">
  <path class="relationship-path{optional_class}"
        data-from-x="{from_x}" data-from-y="{from_y}"
        data-to-x="{to_x}" data-to-y="{to_y}"
        marker-start="{start_marker_url}"
        marker-end="{end_marker_url}" />
  {label_html}
</g>'''

    def _generate_edit_button(self, js_safe_id: str) -> str:
        """Generate edit button HTML."""
        return f'''<button class="da-edit-btn"
        onclick="openDataArchEditor_{js_safe_id}()"
        title="Edit diagram">
    <span style="font-size: 16px;">✏️</span> Edit
</button>'''

    def _generate_javascript(
        self,
        element_id: str,
        js_safe_id: str,
        entities: List[DataEntity],
        relationships: List[DataRelationship],
        presentation_id: str,
        enable_editor: bool
    ) -> str:
        """Generate JavaScript for interactivity and persistence."""
        entities_json = json.dumps([e.model_dump() for e in entities])
        relationships_json = json.dumps([r.model_dump() for r in relationships])

        return f'''
(function() {{
    const containerId = "{element_id}";
    const presentationId = "{presentation_id}";
    const container = document.getElementById(containerId);
    if (!container) return;

    // State
    let entities = {entities_json};
    let relationships = {relationships_json};
    let isDragging = false;
    let dragEntity = null;
    let dragOffset = {{ x: 0, y: 0 }};

    // Initialize
    function init() {{
        setupDragDrop();
        updateRelationshipPaths();
        window.addEventListener('resize', updateRelationshipPaths);
    }}

    // Drag and Drop
    function setupDragDrop() {{
        const entityElements = container.querySelectorAll('.data-entity');
        entityElements.forEach(el => {{
            el.addEventListener('mousedown', startDrag);
        }});
        document.addEventListener('mousemove', onDrag);
        document.addEventListener('mouseup', endDrag);
    }}

    function startDrag(e) {{
        if (e.target.closest('.da-edit-btn')) return;
        const entityEl = e.target.closest('.data-entity');
        if (!entityEl) return;

        isDragging = true;
        dragEntity = entityEl;
        dragEntity.classList.add('dragging');

        const rect = dragEntity.getBoundingClientRect();
        dragOffset.x = e.clientX - rect.left;
        dragOffset.y = e.clientY - rect.top;
        e.preventDefault();
    }}

    function onDrag(e) {{
        if (!isDragging || !dragEntity) return;

        const canvas = container.querySelector('.diagram-canvas');
        const canvasRect = canvas.getBoundingClientRect();

        // Calculate new position as percentage
        const newX = ((e.clientX - dragOffset.x - canvasRect.left) / canvasRect.width) * 100;
        const newY = ((e.clientY - dragOffset.y - canvasRect.top) / canvasRect.height) * 100;

        // Clamp to bounds
        const clampedX = Math.max(0, Math.min(85, newX));
        const clampedY = Math.max(0, Math.min(85, newY));

        dragEntity.style.left = clampedX + '%';
        dragEntity.style.top = clampedY + '%';

        // Update entity data
        const entityId = dragEntity.dataset.entityId;
        const entity = entities.find(e => e.id === entityId);
        if (entity) {{
            entity.x_position = clampedX;
            entity.y_position = clampedY;
        }}

        updateRelationshipPaths();
    }}

    function endDrag() {{
        if (isDragging && dragEntity) {{
            dragEntity.classList.remove('dragging');
            notifyParent('update');
        }}
        isDragging = false;
        dragEntity = null;
    }}

    // Update SVG relationship paths
    function updateRelationshipPaths() {{
        const canvas = container.querySelector('.diagram-canvas');
        const canvasRect = canvas.getBoundingClientRect();

        container.querySelectorAll('.relationship-group').forEach(group => {{
            const path = group.querySelector('.relationship-path');
            if (!path) return;

            const fromEntityId = group.dataset.fromEntity;
            const toEntityId = group.dataset.toEntity;

            const fromEl = container.querySelector(`[data-entity-id="${{fromEntityId}}"]`);
            const toEl = container.querySelector(`[data-entity-id="${{toEntityId}}"]`);

            if (!fromEl || !toEl) return;

            const fromRect = fromEl.getBoundingClientRect();
            const toRect = toEl.getBoundingClientRect();

            // Calculate connection points (center of entity cards, relative to canvas)
            const fromX = fromRect.left + fromRect.width / 2 - canvasRect.left;
            const fromY = fromRect.top + fromRect.height / 2 - canvasRect.top;
            const toX = toRect.left + toRect.width / 2 - canvasRect.left;
            const toY = toRect.top + toRect.height / 2 - canvasRect.top;

            // Calculate edge connection points
            const fromEdge = getEdgePoint(fromRect, toRect, canvasRect);
            const toEdge = getEdgePoint(toRect, fromRect, canvasRect);

            // Create bezier curve
            const dx = Math.abs(toEdge.x - fromEdge.x);
            const dy = Math.abs(toEdge.y - fromEdge.y);
            const curveOffset = Math.min(50, Math.max(20, (dx + dy) / 4));

            let cp1x, cp1y, cp2x, cp2y;
            if (dx > dy) {{
                cp1x = fromEdge.x + (fromEdge.x < toEdge.x ? curveOffset : -curveOffset);
                cp1y = fromEdge.y;
                cp2x = toEdge.x + (toEdge.x < fromEdge.x ? curveOffset : -curveOffset);
                cp2y = toEdge.y;
            }} else {{
                cp1x = fromEdge.x;
                cp1y = fromEdge.y + (fromEdge.y < toEdge.y ? curveOffset : -curveOffset);
                cp2x = toEdge.x;
                cp2y = toEdge.y + (toEdge.y < fromEdge.y ? curveOffset : -curveOffset);
            }}

            const d = `M ${{fromEdge.x}} ${{fromEdge.y}} C ${{cp1x}} ${{cp1y}}, ${{cp2x}} ${{cp2y}}, ${{toEdge.x}} ${{toEdge.y}}`;
            path.setAttribute('d', d);

            // Update label position
            const label = group.querySelector('.relationship-label');
            if (label) {{
                label.setAttribute('x', (fromEdge.x + toEdge.x) / 2);
                label.setAttribute('y', (fromEdge.y + toEdge.y) / 2 - 8);
            }}
        }});
    }}

    function getEdgePoint(fromRect, toRect, canvasRect) {{
        const fromCX = fromRect.left + fromRect.width / 2 - canvasRect.left;
        const fromCY = fromRect.top + fromRect.height / 2 - canvasRect.top;
        const toCX = toRect.left + toRect.width / 2 - canvasRect.left;
        const toCY = toRect.top + toRect.height / 2 - canvasRect.top;

        const angle = Math.atan2(toCY - fromCY, toCX - fromCX);
        const w = fromRect.width / 2 + 5;
        const h = fromRect.height / 2 + 5;

        // Find intersection with rectangle edge
        const tan = Math.tan(angle);
        let x, y;

        if (Math.abs(Math.cos(angle)) * h > Math.abs(Math.sin(angle)) * w) {{
            // Intersects left or right edge
            x = Math.cos(angle) > 0 ? w : -w;
            y = x * tan;
        }} else {{
            // Intersects top or bottom edge
            y = Math.sin(angle) > 0 ? h : -h;
            x = y / tan;
        }}

        return {{
            x: fromCX + x,
            y: fromCY + y
        }};
    }}

    // Notify parent window of state changes
    function notifyParent(action) {{
        try {{
            const message = {{
                type: 'updateDataArchitectureState',
                elementId: containerId,
                action: action,
                dataArchitectureData: {{
                    entities: entities,
                    relationships: relationships
                }},
                timestamp: Date.now()
            }};
            window.parent.postMessage(message, '*');
        }} catch (e) {{
            console.warn('Failed to notify parent:', e);
        }}
    }}

    // Expose functions globally
    window['openDataArchEditor_{js_safe_id}'] = function() {{
        console.log('Edit mode - to be implemented');
        // TODO: Implement edit panel/modal
        alert('Edit mode coming soon!');
    }};

    window['getDataArchState_{js_safe_id}'] = function() {{
        return {{ entities, relationships }};
    }};

    // Initialize on DOM ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', init);
    }} else {{
        init();
    }}
}})();
'''
