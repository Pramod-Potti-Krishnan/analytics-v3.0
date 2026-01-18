"""
Tool registry for Data Ingestion Agent.

Provides MCP-style tool registration and dispatch.
"""

import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Categories of tools."""
    SESSION = "session"
    ANALYSIS = "analysis"
    INTENT = "intent"
    TRANSFORM = "transform"
    CHART = "chart"
    VALIDATION = "validation"


@dataclass
class Tool:
    """
    MCP-style tool definition.

    Represents a single tool that can be invoked by the reasoning engine.
    """
    name: str
    description: str
    category: ToolCategory
    handler: Callable
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    requires_session: bool = True
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "requires_session": self.requires_session,
            "timeout_seconds": self.timeout_seconds
        }


class ToolRegistry:
    """
    Registry for MCP-style tools.

    Manages tool registration, lookup, and invocation.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[ToolCategory, List[str]] = {
            cat: [] for cat in ToolCategory
        }

    def register(self, tool: Tool) -> None:
        """
        Register a tool.

        Args:
            tool: Tool to register
        """
        if tool.name in self._tools:
            logger.warning(f"Overwriting existing tool: {tool.name}")

        self._tools[tool.name] = tool
        self._categories[tool.category].append(tool.name)

        logger.debug(f"Registered tool: {tool.name} ({tool.category.value})")

    def get(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool or None if not found
        """
        return self._tools.get(name)

    def get_by_category(self, category: ToolCategory) -> List[Tool]:
        """
        Get all tools in a category.

        Args:
            category: Tool category

        Returns:
            List of tools
        """
        return [
            self._tools[name]
            for name in self._categories.get(category, [])
        ]

    def list_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def list_tool_names(self) -> List[str]:
        """Get all registered tool names."""
        return list(self._tools.keys())

    async def invoke(
        self,
        tool_name: str,
        **kwargs
    ) -> Any:
        """
        Invoke a tool by name.

        Args:
            tool_name: Name of tool to invoke
            **kwargs: Tool arguments

        Returns:
            Tool result

        Raises:
            ValueError: If tool not found
        """
        tool = self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        logger.info(f"Invoking tool: {tool_name}")

        try:
            # Check if handler is async
            import asyncio
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**kwargs)
            else:
                result = tool.handler(**kwargs)

            return result

        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}")
            raise


def create_default_registry() -> ToolRegistry:
    """
    Create a registry with all default tools registered.

    Returns:
        ToolRegistry with all data ingestion tools
    """
    from ..tools import (
        get_session_info,
        analyze_data_structure,
        detect_patterns,
        parse_user_intent,
        transform_data,
        preview_transform,
        generate_chart,
        validate_result,
        suggest_alternatives
    )

    registry = ToolRegistry()

    # Session tools
    registry.register(Tool(
        name="get_session_info",
        description="Retrieve session metadata and column schema",
        category=ToolCategory.SESSION,
        handler=get_session_info,
        input_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Session ID"}
            },
            "required": ["session_id"]
        },
        output_schema={
            "type": "object",
            "description": "SessionInfo with columns, statistics, etc."
        },
        requires_session=True
    ))

    # Analysis tools
    registry.register(Tool(
        name="analyze_data_structure",
        description="Deep analysis of data structure, patterns, and statistics",
        category=ToolCategory.ANALYSIS,
        handler=analyze_data_structure,
        input_schema={
            "type": "object",
            "properties": {
                "session_info": {"type": "object", "description": "SessionInfo from get_session_info"}
            },
            "required": ["session_info"]
        },
        requires_session=True,
        timeout_seconds=60
    ))

    registry.register(Tool(
        name="detect_patterns",
        description="Detect data patterns for visualization recommendations",
        category=ToolCategory.ANALYSIS,
        handler=detect_patterns,
        input_schema={
            "type": "object",
            "properties": {
                "session_info": {"type": "object"},
                "data_analysis": {"type": "object", "description": "Optional existing analysis"}
            },
            "required": ["session_info"]
        },
        requires_session=False
    ))

    # Intent tools
    registry.register(Tool(
        name="parse_user_intent",
        description="Parse visualization intent from natural language",
        category=ToolCategory.INTENT,
        handler=parse_user_intent,
        input_schema={
            "type": "object",
            "properties": {
                "narrative": {"type": "string"},
                "session_info": {"type": "object"},
                "use_llm": {"type": "boolean", "default": True}
            },
            "required": ["narrative", "session_info"]
        },
        requires_session=False,
        timeout_seconds=30
    ))

    # Transform tools
    registry.register(Tool(
        name="transform_data",
        description="Transform data based on visualization intent",
        category=ToolCategory.TRANSFORM,
        handler=transform_data,
        input_schema={
            "type": "object",
            "properties": {
                "session_info": {"type": "object"},
                "intent": {"type": "object"}
            },
            "required": ["session_info", "intent"]
        },
        requires_session=True,
        timeout_seconds=30
    ))

    registry.register(Tool(
        name="preview_transform",
        description="Preview transformation without committing",
        category=ToolCategory.TRANSFORM,
        handler=preview_transform,
        input_schema={
            "type": "object",
            "properties": {
                "session_info": {"type": "object"},
                "columns": {"type": "array"},
                "aggregation": {"type": "string"},
                "group_by": {"type": "array"},
                "limit": {"type": "integer", "default": 100}
            },
            "required": ["session_info"]
        },
        requires_session=True
    ))

    # Chart tools
    registry.register(Tool(
        name="generate_chart",
        description="Generate chart from transformed data",
        category=ToolCategory.CHART,
        handler=generate_chart,
        input_schema={
            "type": "object",
            "properties": {
                "transform_result": {"type": "object"},
                "intent": {"type": "object"},
                "width": {"type": "integer", "default": 850},
                "height": {"type": "integer", "default": 500},
                "include_insights": {"type": "boolean", "default": False}
            },
            "required": ["transform_result", "intent"]
        },
        requires_session=False,
        timeout_seconds=30
    ))

    # Validation tools
    registry.register(Tool(
        name="validate_result",
        description="Validate generated chart quality",
        category=ToolCategory.VALIDATION,
        handler=validate_result,
        input_schema={
            "type": "object",
            "properties": {
                "chart_result": {"type": "object"},
                "transform_result": {"type": "object"},
                "intent": {"type": "object"}
            },
            "required": ["chart_result", "transform_result", "intent"]
        },
        requires_session=False
    ))

    registry.register(Tool(
        name="suggest_alternatives",
        description="Suggest alternative visualizations",
        category=ToolCategory.VALIDATION,
        handler=suggest_alternatives,
        input_schema={
            "type": "object",
            "properties": {
                "chart_result": {"type": "object"},
                "transform_result": {"type": "object"},
                "intent": {"type": "object"},
                "session_info": {"type": "object"}
            },
            "required": ["chart_result", "transform_result", "intent", "session_info"]
        },
        requires_session=False
    ))

    logger.info(f"Created default tool registry with {len(registry.list_tools())} tools")

    return registry
