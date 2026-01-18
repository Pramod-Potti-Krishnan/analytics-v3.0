"""
Reasoning engine for Data Ingestion Agent.

Provides chain-of-thought reasoning with state machine workflow.
"""

import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from .tool_registry import ToolRegistry, create_default_registry
from ..database.session_store import SessionStore
from ..database.models import ReasoningStepType
from ..models.tools import (
    SessionInfo,
    DataAnalysis,
    VisualizationIntent,
    TransformResult,
    ChartResult,
    ValidationResult
)
from ..models.responses import ReasoningStep, ChartOutput
from ..settings import get_data_ingestion_settings

logger = logging.getLogger(__name__)


class ReasoningState(str, Enum):
    """States in the reasoning workflow."""
    INIT = "init"
    GET_SESSION = "get_session"
    PARSE_INTENT = "parse_intent"
    ANALYZE_DATA = "analyze_data"
    TRANSFORM = "transform"
    GENERATE_CHART = "generate_chart"
    VALIDATE = "validate"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ReasoningContext:
    """
    Context passed through reasoning steps.

    Accumulates results from each step for use in subsequent steps.
    """
    # Request info
    request_id: str
    session_id: str
    narrative: str

    # Chart options
    chart_type: Optional[str] = None
    chart_title: Optional[str] = None
    presentation_id: Optional[str] = None
    slide_id: Optional[str] = None
    include_insights: bool = False
    width: int = 850
    height: int = 500

    # State
    state: ReasoningState = ReasoningState.INIT
    current_step: int = 0
    max_steps: int = 10

    # Results accumulated from tools
    session_info: Optional[SessionInfo] = None
    data_analysis: Optional[DataAnalysis] = None
    intent: Optional[VisualizationIntent] = None
    transform_result: Optional[TransformResult] = None
    chart_result: Optional[ChartResult] = None
    validation_result: Optional[ValidationResult] = None

    # Execution tracking
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    total_duration_ms: float = 0.0
    error_message: Optional[str] = None


class ReasoningEngine:
    """
    Chain-of-thought reasoning engine.

    Orchestrates the workflow:
    1. get_session_info - Load session metadata
    2. parse_user_intent - Extract intent from narrative
    3. transform_data - Prepare data for visualization
    4. generate_chart - Create the chart
    5. validate_result - Check quality
    """

    def __init__(
        self,
        db_session: AsyncSession,
        registry: Optional[ToolRegistry] = None
    ):
        """
        Initialize reasoning engine.

        Args:
            db_session: Database session
            registry: Optional tool registry (creates default if None)
        """
        self._db_session = db_session
        self._registry = registry or create_default_registry()
        self._session_store = SessionStore(db_session)
        self._settings = get_data_ingestion_settings()

    async def process(
        self,
        session_id: str,
        narrative: str,
        chart_type: Optional[str] = None,
        chart_title: Optional[str] = None,
        presentation_id: Optional[str] = None,
        slide_id: Optional[str] = None,
        include_insights: bool = False,
        width: int = 850,
        height: int = 500
    ) -> Dict[str, Any]:
        """
        Process a data ingestion request.

        Runs the chain-of-thought reasoning workflow to:
        1. Understand the data
        2. Parse user intent
        3. Transform data
        4. Generate visualization

        Args:
            session_id: Data session ID
            narrative: User's description of desired visualization
            chart_type: Optional chart type override
            chart_title: Optional title override
            presentation_id: For chart persistence
            slide_id: For chart persistence
            include_insights: Include Key Insights panel
            width: Chart width
            height: Chart height

        Returns:
            Dict with success, chart, reasoning steps, etc.
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(f"Starting reasoning process: request={request_id}, session={session_id}")

        # Initialize context
        ctx = ReasoningContext(
            request_id=request_id,
            session_id=session_id,
            narrative=narrative,
            chart_type=chart_type,
            chart_title=chart_title,
            presentation_id=presentation_id,
            slide_id=slide_id,
            include_insights=include_insights,
            width=width,
            height=height,
            max_steps=self._settings.MAX_AGENT_STEPS
        )

        try:
            # Run state machine
            while ctx.state != ReasoningState.COMPLETE and ctx.state != ReasoningState.ERROR:
                if ctx.current_step >= ctx.max_steps:
                    ctx.state = ReasoningState.ERROR
                    ctx.error_message = f"Max steps ({ctx.max_steps}) exceeded"
                    break

                ctx = await self._execute_step(ctx)
                ctx.current_step += 1

            ctx.total_duration_ms = (time.time() - start_time) * 1000

            # Log reasoning to database
            await self._log_reasoning(ctx)

            # Build response
            if ctx.state == ReasoningState.COMPLETE and ctx.chart_result:
                return {
                    "success": True,
                    "request_id": request_id,
                    "session_id": session_id,
                    "chart": ChartOutput(
                        chart_html=ctx.chart_result.chart_html,
                        chart_title=ctx.chart_result.chart_title,
                        chart_type=ctx.chart_result.chart_type.value,
                        insights_html=ctx.chart_result.insights_html
                    ),
                    "data_summary": {
                        "rows_used": ctx.transform_result.rows_after if ctx.transform_result else 0,
                        "columns_used": ctx.intent.target_columns if ctx.intent else [],
                        "aggregation": ctx.transform_result.aggregation_applied if ctx.transform_result else None,
                        "group_by": ctx.transform_result.group_by_applied if ctx.transform_result else []
                    },
                    "reasoning_steps": ctx.reasoning_steps,
                    "total_duration_ms": ctx.total_duration_ms,
                    "validation": ctx.validation_result.model_dump() if ctx.validation_result else None
                }
            else:
                return {
                    "success": False,
                    "request_id": request_id,
                    "session_id": session_id,
                    "error": ctx.error_message or "Unknown error",
                    "reasoning_steps": ctx.reasoning_steps,
                    "total_duration_ms": ctx.total_duration_ms
                }

        except Exception as e:
            logger.error(f"Reasoning process failed: {e}", exc_info=True)
            ctx.total_duration_ms = (time.time() - start_time) * 1000

            return {
                "success": False,
                "request_id": request_id,
                "session_id": session_id,
                "error": str(e),
                "reasoning_steps": ctx.reasoning_steps,
                "total_duration_ms": ctx.total_duration_ms
            }

    async def _execute_step(self, ctx: ReasoningContext) -> ReasoningContext:
        """Execute a single reasoning step based on current state."""
        step_start = time.time()

        if ctx.state == ReasoningState.INIT:
            # Transition to get session
            ctx.state = ReasoningState.GET_SESSION

        elif ctx.state == ReasoningState.GET_SESSION:
            ctx = await self._step_get_session(ctx)

        elif ctx.state == ReasoningState.PARSE_INTENT:
            ctx = await self._step_parse_intent(ctx)

        elif ctx.state == ReasoningState.TRANSFORM:
            ctx = await self._step_transform(ctx)

        elif ctx.state == ReasoningState.GENERATE_CHART:
            ctx = await self._step_generate_chart(ctx)

        elif ctx.state == ReasoningState.VALIDATE:
            ctx = await self._step_validate(ctx)

        return ctx

    async def _step_get_session(self, ctx: ReasoningContext) -> ReasoningContext:
        """Step 1: Get session information."""
        step_start = time.time()

        try:
            from ..tools import get_session_info

            ctx.session_info = await get_session_info(
                self._db_session,
                ctx.session_id
            )

            if not ctx.session_info:
                ctx.state = ReasoningState.ERROR
                ctx.error_message = f"Session not found: {ctx.session_id}"
                self._add_step(ctx, "get_session", "get_session_info", step_start, False, ctx.error_message)
                return ctx

            reasoning = (
                f"Loaded session with {ctx.session_info.row_count} rows, "
                f"{ctx.session_info.column_count} columns. "
                f"Numeric: {len(ctx.session_info.numeric_columns)}, "
                f"Categorical: {len(ctx.session_info.categorical_columns)}"
            )

            self._add_step(ctx, "get_session", "get_session_info", step_start, True, reasoning=reasoning)
            ctx.state = ReasoningState.PARSE_INTENT

        except Exception as e:
            ctx.state = ReasoningState.ERROR
            ctx.error_message = str(e)
            self._add_step(ctx, "get_session", "get_session_info", step_start, False, str(e))

        return ctx

    async def _step_parse_intent(self, ctx: ReasoningContext) -> ReasoningContext:
        """Step 2: Parse user intent."""
        step_start = time.time()

        try:
            from ..tools import parse_user_intent

            ctx.intent = await parse_user_intent(
                ctx.narrative,
                ctx.session_info,
                use_llm=True
            )

            # Override chart type if specified
            if ctx.chart_type:
                ctx.intent.suggested_chart_type = ctx.chart_type

            reasoning = (
                f"Intent: {ctx.intent.intent_type.value} "
                f"(confidence: {ctx.intent.confidence:.2f}). "
                f"Target columns: {ctx.intent.target_columns}. "
                f"Group by: {ctx.intent.group_by_columns}. "
                f"Chart type: {ctx.intent.suggested_chart_type}"
            )

            self._add_step(ctx, "parse_intent", "parse_user_intent", step_start, True, reasoning=reasoning)
            ctx.state = ReasoningState.TRANSFORM

        except Exception as e:
            ctx.state = ReasoningState.ERROR
            ctx.error_message = str(e)
            self._add_step(ctx, "parse_intent", "parse_user_intent", step_start, False, str(e))

        return ctx

    async def _step_transform(self, ctx: ReasoningContext) -> ReasoningContext:
        """Step 3: Transform data."""
        step_start = time.time()

        try:
            from ..tools import transform_data

            ctx.transform_result = await transform_data(
                self._db_session,
                ctx.session_info,
                ctx.intent
            )

            if not ctx.transform_result.success:
                ctx.state = ReasoningState.ERROR
                ctx.error_message = "Data transformation failed"
                self._add_step(ctx, "transform", "transform_data", step_start, False, ctx.error_message)
                return ctx

            reasoning = (
                f"Transformed {ctx.transform_result.rows_before} rows -> "
                f"{ctx.transform_result.rows_after} data points. "
                f"Aggregation: {ctx.transform_result.aggregation_applied}. "
                f"Group by: {ctx.transform_result.group_by_applied}"
            )

            if ctx.transform_result.warnings:
                reasoning += f". Warnings: {ctx.transform_result.warnings}"

            self._add_step(ctx, "transform", "transform_data", step_start, True, reasoning=reasoning)
            ctx.state = ReasoningState.GENERATE_CHART

        except Exception as e:
            ctx.state = ReasoningState.ERROR
            ctx.error_message = str(e)
            self._add_step(ctx, "transform", "transform_data", step_start, False, str(e))

        return ctx

    async def _step_generate_chart(self, ctx: ReasoningContext) -> ReasoningContext:
        """Step 4: Generate chart."""
        step_start = time.time()

        try:
            from ..tools import generate_chart

            ctx.chart_result = await generate_chart(
                transform_result=ctx.transform_result,
                intent=ctx.intent,
                presentation_id=ctx.presentation_id,
                slide_id=ctx.slide_id,
                width=ctx.width,
                height=ctx.height,
                include_insights=ctx.include_insights,
                chart_title=ctx.chart_title
            )

            if not ctx.chart_result.success:
                ctx.state = ReasoningState.ERROR
                ctx.error_message = "Chart generation failed"
                self._add_step(ctx, "generate_chart", "generate_chart", step_start, False, ctx.error_message)
                return ctx

            reasoning = (
                f"Generated {ctx.chart_result.chart_type.value} chart with "
                f"{ctx.chart_result.data_points_used} data points. "
                f"Title: {ctx.chart_result.chart_title}. "
                f"Time: {ctx.chart_result.generation_time_ms:.0f}ms"
            )

            self._add_step(ctx, "generate_chart", "generate_chart", step_start, True, reasoning=reasoning)
            ctx.state = ReasoningState.VALIDATE

        except Exception as e:
            ctx.state = ReasoningState.ERROR
            ctx.error_message = str(e)
            self._add_step(ctx, "generate_chart", "generate_chart", step_start, False, str(e))

        return ctx

    async def _step_validate(self, ctx: ReasoningContext) -> ReasoningContext:
        """Step 5: Validate result."""
        step_start = time.time()

        try:
            from ..tools import validate_result

            ctx.validation_result = await validate_result(
                ctx.chart_result,
                ctx.transform_result,
                ctx.intent
            )

            reasoning = (
                f"Validation score: {ctx.validation_result.score:.2f}. "
                f"Valid: {ctx.validation_result.valid}. "
            )

            if ctx.validation_result.issues:
                reasoning += f"Issues: {ctx.validation_result.issues[:2]}"

            self._add_step(ctx, "validate", "validate_result", step_start, True, reasoning=reasoning)

            # Even if validation finds issues, we consider the process complete
            ctx.state = ReasoningState.COMPLETE

        except Exception as e:
            # Validation failure is not fatal
            logger.warning(f"Validation failed: {e}")
            self._add_step(ctx, "validate", "validate_result", step_start, False, str(e))
            ctx.state = ReasoningState.COMPLETE

        return ctx

    def _add_step(
        self,
        ctx: ReasoningContext,
        step_type: str,
        tool_name: str,
        start_time: float,
        success: bool,
        error_message: Optional[str] = None,
        reasoning: Optional[str] = None
    ) -> None:
        """Add a reasoning step to context."""
        duration_ms = (time.time() - start_time) * 1000

        step = ReasoningStep(
            step_number=len(ctx.reasoning_steps) + 1,
            step_type=step_type,
            tool_name=tool_name,
            reasoning=reasoning,
            duration_ms=round(duration_ms, 2),
            success=success,
            error_message=error_message
        )

        ctx.reasoning_steps.append(step)

    async def _log_reasoning(self, ctx: ReasoningContext) -> None:
        """Log reasoning steps to database."""
        try:
            for step in ctx.reasoning_steps:
                # Map step type to enum
                step_type_map = {
                    "get_session": ReasoningStepType.GET_SESSION,
                    "parse_intent": ReasoningStepType.PARSE_INTENT,
                    "analyze_data": ReasoningStepType.ANALYZE_DATA,
                    "transform": ReasoningStepType.TRANSFORM_DATA,
                    "generate_chart": ReasoningStepType.GENERATE_CHART,
                    "validate": ReasoningStepType.VALIDATE_RESULT,
                }

                await self._session_store.add_reasoning_log(
                    session_id=uuid.UUID(ctx.session_id),
                    request_id=ctx.request_id,
                    step_number=step.step_number,
                    step_type=step_type_map.get(step.step_type, ReasoningStepType.ERROR),
                    tool_name=step.tool_name,
                    reasoning=step.reasoning,
                    duration_ms=step.duration_ms,
                    success=step.success,
                    error_message=step.error_message
                )

        except Exception as e:
            logger.error(f"Failed to log reasoning steps: {e}")
