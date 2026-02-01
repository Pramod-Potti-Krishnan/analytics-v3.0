"""
Data Architecture Atomic Models for Analytics Microservice v1.0.0

Request/response Pydantic models for DATA_ARCHITECTURE atomic endpoint.
Generates Entity-Relationship (ER) diagrams with tables, fields, and relationships.

v1.0.0 Initial Release:
- DataEntity model for database tables/views
- DataField model for columns with types and constraints
- DataRelationship model for foreign key connections
- Crow's foot notation cardinality types
- Position presets for common layouts
- Request/response models with explicit and LLM paths
"""

from typing import List, Dict, Any, Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator
import uuid


# ========================================
# POSITION PRESETS
# ========================================

DATA_ARCH_POSITION_PRESETS = {
    "full_content": {
        "start_col": 2,
        "start_row": 4,
        "gridWidth": 30,
        "gridHeight": 14
    },
    "left_four_fifths": {
        "start_col": 2,
        "start_row": 4,
        "gridWidth": 24,
        "gridHeight": 14
    },
    "center_medium": {
        "start_col": 5,
        "start_row": 5,
        "gridWidth": 22,
        "gridHeight": 12
    },
    "right_half": {
        "start_col": 17,
        "start_row": 4,
        "gridWidth": 15,
        "gridHeight": 14
    }
}


# ========================================
# ENTITY TYPES
# ========================================

EntityType = Literal["table", "view", "enum", "junction"]


# ========================================
# CARDINALITY TYPES (Crow's Foot Notation)
# ========================================

CardinalityType = Literal[
    "one_to_one",      # |——|   (1:1)
    "one_to_many",     # |——<   (1:N)
    "many_to_one",     # >——|   (N:1)
    "many_to_many",    # >——<   (M:N)
    "zero_or_one",     # o——|   (0..1)
    "zero_or_many"     # o——<   (0..N)
]


# ========================================
# FIELD MODEL (Column)
# ========================================

class DataField(BaseModel):
    """
    Database column/field definition.

    Represents a single column in a database table with type information
    and constraint indicators.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Column name (snake_case recommended)"
    )
    data_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Data type: INT, VARCHAR(255), TIMESTAMP, UUID, etc."
    )
    is_primary_key: bool = Field(
        default=False,
        description="True if this field is (part of) the primary key"
    )
    is_foreign_key: bool = Field(
        default=False,
        description="True if this field references another table"
    )
    is_nullable: bool = Field(
        default=True,
        description="True if the column allows NULL values"
    )
    default_value: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Default value expression (e.g., 'NOW()', '0', 'uuid_generate_v4()')"
    )
    references: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Foreign key reference in format 'table_name.field_name'"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is valid identifier format."""
        if not v or not v.strip():
            raise ValueError("Field name cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "user_id",
                "data_type": "INT",
                "is_primary_key": False,
                "is_foreign_key": True,
                "is_nullable": False,
                "references": "users.id"
            }
        }


# ========================================
# ENTITY MODEL (Table)
# ========================================

class DataEntity(BaseModel):
    """
    Database entity (table/view) definition.

    Represents a database table or view with its fields and position
    on the ER diagram canvas.
    """
    id: Optional[str] = Field(
        default=None,
        description="Entity ID (auto-generated as ent-{uuid8} if not provided)"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Table/view name (snake_case recommended)"
    )
    type: EntityType = Field(
        default="table",
        description="Entity type: table, view, enum, or junction"
    )
    fields: List[DataField] = Field(
        default_factory=list,
        description="List of columns/fields in this entity"
    )
    x_position: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Horizontal position as percentage (0-100)"
    )
    y_position: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Vertical position as percentage (0-100)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional description of the entity's purpose"
    )
    color: Optional[str] = Field(
        default=None,
        description="Optional hex color for the entity card header"
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = f"ent-{uuid.uuid4().hex[:8]}"

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure table name is valid."""
        if not v or not v.strip():
            raise ValueError("Entity name cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ent-a1b2c3d4",
                "name": "users",
                "type": "table",
                "fields": [
                    {"name": "id", "data_type": "INT", "is_primary_key": True, "is_nullable": False},
                    {"name": "email", "data_type": "VARCHAR(255)", "is_nullable": False},
                    {"name": "created_at", "data_type": "TIMESTAMP", "default_value": "NOW()"}
                ],
                "x_position": 20.0,
                "y_position": 30.0,
                "description": "System users table"
            }
        }


# ========================================
# RELATIONSHIP MODEL (Foreign Key Connection)
# ========================================

class DataRelationship(BaseModel):
    """
    Database relationship (foreign key) definition.

    Represents a connection between two entities using crow's foot notation
    for cardinality visualization.
    """
    id: Optional[str] = Field(
        default=None,
        description="Relationship ID (auto-generated as rel-{uuid8} if not provided)"
    )
    from_entity: str = Field(
        ...,
        description="Source entity ID"
    )
    from_field: str = Field(
        ...,
        description="Source field name"
    )
    to_entity: str = Field(
        ...,
        description="Target entity ID"
    )
    to_field: str = Field(
        ...,
        description="Target field name (usually primary key)"
    )
    cardinality: CardinalityType = Field(
        default="one_to_many",
        description="Relationship cardinality using crow's foot notation"
    )
    is_optional: bool = Field(
        default=False,
        description="True for optional relationships (renders as dashed line)"
    )
    label: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Optional relationship label/name"
    )

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.id = f"rel-{uuid.uuid4().hex[:8]}"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rel-e5f6g7h8",
                "from_entity": "ent-orders",
                "from_field": "user_id",
                "to_entity": "ent-users",
                "to_field": "id",
                "cardinality": "many_to_one",
                "is_optional": False,
                "label": "placed by"
            }
        }


# ========================================
# REQUEST MODEL
# ========================================

class DataArchitectureAtomicRequest(BaseModel):
    """
    Request for DATA_ARCHITECTURE atomic endpoint.

    Supports two input paths:
    1. Explicit: Provide entities and relationships directly
    2. LLM: Provide a prompt to generate the ER diagram

    If both are provided, explicit data takes precedence.
    """

    # Required identifiers
    presentation_id: str = Field(
        ...,
        min_length=1,
        description="Presentation UUID (required for persistence)"
    )
    slide_id: str = Field(
        ...,
        min_length=1,
        description="Slide identifier (required for deterministic IDs)"
    )
    diagram_index: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Index for multiple diagrams on same slide"
    )

    # Explicit definition path
    entities: List[DataEntity] = Field(
        default_factory=list,
        description="Explicit entity definitions (explicit path)"
    )
    relationships: List[DataRelationship] = Field(
        default_factory=list,
        description="Explicit relationship definitions (explicit path)"
    )

    # LLM generation path
    prompt: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Natural language description for LLM generation (LLM path)"
    )
    placeholder_mode: bool = Field(
        default=False,
        description="If True, use fallback schemas without LLM call"
    )

    # Optional element ID for persistence
    element_id: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Existing element_id to preserve (for diagram updates)"
    )

    # Display options
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Diagram title (auto-generated if not provided)"
    )
    theme_mode: Literal["light", "dark"] = Field(
        default="light",
        description="Color theme mode"
    )
    show_data_types: bool = Field(
        default=True,
        description="Show data type annotations on fields"
    )
    show_nullable: bool = Field(
        default=True,
        description="Show nullable indicators on fields"
    )
    show_title: bool = Field(
        default=True,
        description="Display diagram title above the visualization"
    )
    enable_editor: bool = Field(
        default=True,
        description="Enable interactive edit mode"
    )

    # Sizing and positioning
    gridWidth: int = Field(
        default=30,
        ge=10,
        le=32,
        description="Width in grid units (32-column system)"
    )
    gridHeight: int = Field(
        default=14,
        ge=6,
        le=18,
        description="Height in grid units (18-row system)"
    )
    position_preset: Optional[str] = Field(
        default=None,
        description="Position preset name (overrides manual positioning)"
    )
    start_col: Optional[int] = Field(
        default=None,
        ge=1,
        le=32,
        description="Starting column position (1-32)"
    )
    start_row: Optional[int] = Field(
        default=None,
        ge=1,
        le=18,
        description="Starting row position (1-18)"
    )
    external_margin: int = Field(
        default=10,
        ge=0,
        le=50,
        description="External margin in pixels"
    )

    @field_validator('presentation_id', 'slide_id')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Ensure IDs are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("cannot be empty or whitespace")
        return v.strip()

    @field_validator('position_preset')
    @classmethod
    def validate_preset(cls, v: Optional[str]) -> Optional[str]:
        """Validate position preset if provided."""
        if v is not None and v not in DATA_ARCH_POSITION_PRESETS:
            valid = list(DATA_ARCH_POSITION_PRESETS.keys())
            raise ValueError(f"Invalid preset '{v}'. Valid presets: {valid}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "presentation_id": "pres-12345678-abcd",
                "slide_id": "slide-1",
                "diagram_index": 0,
                "prompt": "Design a database schema for an e-commerce platform with users, products, orders, and reviews",
                "theme_mode": "light",
                "gridWidth": 30,
                "gridHeight": 14
            }
        }


# ========================================
# RESPONSE MODEL
# ========================================

class DataArchitectureAtomicResponse(BaseModel):
    """Response with generated DATA_ARCHITECTURE HTML element."""

    success: bool = Field(True, description="Whether generation was successful")
    diagram_type: str = Field(
        default="data_architecture",
        description="Type identifier for this diagram"
    )
    html_content: str = Field(
        ...,
        description="Self-contained HTML with embedded CSS and JavaScript"
    )

    # Data used
    entities: List[Dict[str, Any]] = Field(
        ...,
        description="Entity definitions used in generation"
    )
    relationships: List[Dict[str, Any]] = Field(
        ...,
        description="Relationship definitions used in generation"
    )

    # Metadata
    title: str = Field(..., description="Generated or provided diagram title")
    generation_time_ms: int = Field(..., description="Processing time in milliseconds")
    element_id: str = Field(..., description="Unique element ID for frontend positioning")
    source: Literal["explicit", "llm", "placeholder"] = Field(
        ...,
        description="Data source: explicit (provided), llm (generated), or placeholder (fallback)"
    )

    # Grid position (returned when position specified in request)
    grid_position: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Grid position: {start_col, start_row, width, height, grid_row, grid_column}"
    )

    # Planning metadata (when LLM was used)
    reasoning: Optional[str] = Field(
        default=None,
        description="LLM's reasoning for schema design (only for LLM path)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "diagram_type": "data_architecture",
                "html_content": "<div class=\"data-architecture-container\">...</div>",
                "entities": [
                    {"id": "ent-001", "name": "users", "type": "table", "fields": []},
                    {"id": "ent-002", "name": "orders", "type": "table", "fields": []}
                ],
                "relationships": [
                    {"id": "rel-001", "from_entity": "ent-002", "to_entity": "ent-001", "cardinality": "many_to_one"}
                ],
                "title": "E-Commerce Database Schema",
                "generation_time_ms": 125,
                "element_id": "data-arch-pres-12345678-abcd-slide-1-0-a1b2c3d4",
                "source": "llm",
                "grid_position": {
                    "start_col": 2,
                    "start_row": 4,
                    "width": 30,
                    "height": 14,
                    "grid_row": "4/18",
                    "grid_column": "2/32"
                },
                "reasoning": "Designed normalized schema with user-order relationship..."
            }
        }


# ========================================
# ERROR MODEL
# ========================================

class DataArchitectureAtomicError(BaseModel):
    """Error response for DATA_ARCHITECTURE generation."""

    success: bool = Field(False)
    error_code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    suggestion: Optional[str] = Field(None, description="Suggested fix")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "LLM_GENERATION_FAILED",
                "message": "Failed to generate ER diagram from prompt",
                "details": {"prompt": "Design a database..."},
                "suggestion": "Try providing explicit entities or use placeholder_mode=true"
            }
        }
