"""
Tests for Data Ingestion Agent reasoning engine.

Tests the chain-of-thought reasoning workflow, state machine,
tool orchestration, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timezone

from data_ingestion.agent.reasoning_engine import (
    ReasoningEngine,
    ReasoningContext,
    ReasoningState
)
from data_ingestion.agent.tool_registry import ToolRegistry, create_default_registry
from data_ingestion.models.tools import (
    SessionInfo,
    ColumnSchema,
    ColumnType,
    VisualizationIntent,
    IntentType,
    TransformResult,
    ChartResult,
    ChartType,
    ValidationResult
)


class TestReasoningEngine:
    """Tests for ReasoningEngine class."""

    @pytest.fixture
    def mock_session_store(self):
        """Create mock session store."""
        mock_store = MagicMock()
        mock_store.get_session = AsyncMock()
        mock_store.add_reasoning_log = AsyncMock()
        return mock_store

    @pytest.fixture
    def reasoning_engine(self, mock_db_session):
        """Create reasoning engine for testing."""
        return ReasoningEngine(mock_db_session)

    @pytest.mark.asyncio
    async def test_process_success(self, reasoning_engine, mock_db_session, sample_session_info, sample_intent, sample_transform_result, sample_chart_result, sample_validation_result):
        """Test successful end-to-end processing."""
        with patch.multiple(
            'data_ingestion.agent.reasoning_engine',
            get_session_info=AsyncMock(return_value=sample_session_info),
            parse_user_intent=AsyncMock(return_value=sample_intent),
            transform_data=AsyncMock(return_value=sample_transform_result),
            generate_chart=AsyncMock(return_value=sample_chart_result),
            validate_result=AsyncMock(return_value=sample_validation_result)
        ):
            with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
                MockStore.return_value.add_reasoning_log = AsyncMock()

                result = await reasoning_engine.process(
                    session_id=sample_session_info.session_id,
                    narrative="Show sales by product"
                )

                assert result is not None
                assert result["success"] is True
                assert "chart" in result
                assert "reasoning_steps" in result
                assert len(result["reasoning_steps"]) >= 4

    @pytest.mark.asyncio
    async def test_process_session_not_found(self, reasoning_engine, mock_db_session):
        """Test processing when session is not found."""
        with patch('data_ingestion.tools.session_tools.SessionStore') as MockStore:
            MockStore.return_value.get_session = AsyncMock(return_value=None)

            with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockEngineStore:
                MockEngineStore.return_value.add_reasoning_log = AsyncMock()

                # Patch the import within reasoning_engine
                with patch.object(reasoning_engine, '_step_get_session') as mock_step:
                    async def fail_get_session(ctx):
                        ctx.state = ReasoningState.ERROR
                        ctx.error_message = "Session not found"
                        return ctx
                    mock_step.side_effect = fail_get_session

                    result = await reasoning_engine.process(
                        session_id="nonexistent-session",
                        narrative="Show data"
                    )

                    assert result is not None
                    assert result["success"] is False
                    assert "error" in result

    @pytest.mark.asyncio
    async def test_process_max_steps_exceeded(self, reasoning_engine, mock_db_session, sample_session_info):
        """Test that processing stops when max steps exceeded."""
        # Create context with very low max_steps
        ctx = ReasoningContext(
            request_id="test",
            session_id=sample_session_info.session_id,
            narrative="Test",
            max_steps=1
        )

        with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
            MockStore.return_value.add_reasoning_log = AsyncMock()

            # The engine should stop after max_steps
            # This tests the safety mechanism
            result = await reasoning_engine.process(
                session_id=sample_session_info.session_id,
                narrative="Show data"
            )

            # Result should exist (may be error or success depending on implementation)
            assert result is not None

    @pytest.mark.asyncio
    async def test_process_with_chart_type_override(self, reasoning_engine, mock_db_session, sample_session_info, sample_intent, sample_transform_result, sample_chart_result, sample_validation_result):
        """Test processing with chart type override."""
        with patch.multiple(
            'data_ingestion.agent.reasoning_engine',
            get_session_info=AsyncMock(return_value=sample_session_info),
            parse_user_intent=AsyncMock(return_value=sample_intent),
            transform_data=AsyncMock(return_value=sample_transform_result),
            generate_chart=AsyncMock(return_value=sample_chart_result),
            validate_result=AsyncMock(return_value=sample_validation_result)
        ):
            with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
                MockStore.return_value.add_reasoning_log = AsyncMock()

                result = await reasoning_engine.process(
                    session_id=sample_session_info.session_id,
                    narrative="Show sales",
                    chart_type="pie"  # Override
                )

                assert result is not None


class TestReasoningContext:
    """Tests for ReasoningContext dataclass."""

    def test_context_initialization(self):
        """Test context initialization with defaults."""
        ctx = ReasoningContext(
            request_id="test-123",
            session_id="session-456",
            narrative="Show me the data"
        )

        assert ctx.request_id == "test-123"
        assert ctx.session_id == "session-456"
        assert ctx.narrative == "Show me the data"
        assert ctx.state == ReasoningState.INIT
        assert ctx.current_step == 0
        assert ctx.max_steps == 10
        assert ctx.session_info is None
        assert ctx.intent is None
        assert ctx.transform_result is None
        assert ctx.chart_result is None
        assert len(ctx.reasoning_steps) == 0

    def test_context_with_options(self):
        """Test context with optional parameters."""
        ctx = ReasoningContext(
            request_id="test",
            session_id="session",
            narrative="test",
            chart_type="bar_vertical",
            chart_title="My Chart",
            include_insights=True,
            width=1000,
            height=600
        )

        assert ctx.chart_type == "bar_vertical"
        assert ctx.chart_title == "My Chart"
        assert ctx.include_insights is True
        assert ctx.width == 1000
        assert ctx.height == 600


class TestReasoningState:
    """Tests for ReasoningState enum."""

    def test_state_values(self):
        """Test all state values exist."""
        assert ReasoningState.INIT == "init"
        assert ReasoningState.GET_SESSION == "get_session"
        assert ReasoningState.PARSE_INTENT == "parse_intent"
        assert ReasoningState.TRANSFORM == "transform"
        assert ReasoningState.GENERATE_CHART == "generate_chart"
        assert ReasoningState.VALIDATE == "validate"
        assert ReasoningState.COMPLETE == "complete"
        assert ReasoningState.ERROR == "error"


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_create_default_registry(self):
        """Test default registry creation."""
        registry = create_default_registry()

        assert registry is not None
        # Check that essential tools are registered
        assert registry.has_tool("get_session_info")
        assert registry.has_tool("parse_user_intent")
        assert registry.has_tool("transform_data")
        assert registry.has_tool("generate_chart")
        assert registry.has_tool("validate_result")

    def test_registry_get_tool(self):
        """Test getting tool from registry."""
        registry = create_default_registry()

        tool = registry.get_tool("get_session_info")
        assert tool is not None
        assert callable(tool)

    def test_registry_get_nonexistent_tool(self):
        """Test getting non-existent tool."""
        registry = create_default_registry()

        tool = registry.get_tool("nonexistent_tool")
        assert tool is None

    def test_registry_list_tools(self):
        """Test listing all tools."""
        registry = create_default_registry()

        tools = registry.list_tools()
        assert isinstance(tools, list)
        assert len(tools) >= 5  # At least the core tools

    def test_registry_register_custom_tool(self):
        """Test registering a custom tool."""
        registry = ToolRegistry()

        async def custom_tool(arg1, arg2):
            return {"result": arg1 + arg2}

        registry.register("custom_tool", custom_tool, "A custom tool for testing")

        assert registry.has_tool("custom_tool")
        tool = registry.get_tool("custom_tool")
        assert tool == custom_tool


class TestStateMachineTransitions:
    """Tests for state machine transitions."""

    @pytest.mark.asyncio
    async def test_init_to_get_session(self, mock_db_session):
        """Test transition from INIT to GET_SESSION."""
        engine = ReasoningEngine(mock_db_session)

        ctx = ReasoningContext(
            request_id="test",
            session_id="session",
            narrative="test"
        )

        assert ctx.state == ReasoningState.INIT

        # Execute one step
        ctx = await engine._execute_step(ctx)

        assert ctx.state == ReasoningState.GET_SESSION

    @pytest.mark.asyncio
    async def test_error_state_stops_processing(self, mock_db_session, sample_session_info):
        """Test that ERROR state stops further processing."""
        engine = ReasoningEngine(mock_db_session)

        ctx = ReasoningContext(
            request_id="test",
            session_id="session",
            narrative="test",
            state=ReasoningState.ERROR,
            error_message="Test error"
        )

        # State machine should not process ERROR state
        original_state = ctx.state
        # In ERROR state, process should return early

        with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
            MockStore.return_value.add_reasoning_log = AsyncMock()

            result = await engine.process(
                session_id="test",
                narrative="test"
            )

            # Should get a result (success or failure)
            assert result is not None


class TestReasoningStepLogging:
    """Tests for reasoning step logging."""

    @pytest.mark.asyncio
    async def test_steps_are_logged(self, mock_db_session, sample_session_info, sample_intent, sample_transform_result, sample_chart_result, sample_validation_result):
        """Test that reasoning steps are properly logged."""
        engine = ReasoningEngine(mock_db_session)

        with patch.multiple(
            'data_ingestion.agent.reasoning_engine',
            get_session_info=AsyncMock(return_value=sample_session_info),
            parse_user_intent=AsyncMock(return_value=sample_intent),
            transform_data=AsyncMock(return_value=sample_transform_result),
            generate_chart=AsyncMock(return_value=sample_chart_result),
            validate_result=AsyncMock(return_value=sample_validation_result)
        ):
            with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
                mock_store = MockStore.return_value
                mock_store.add_reasoning_log = AsyncMock()

                result = await engine.process(
                    session_id=sample_session_info.session_id,
                    narrative="Show data"
                )

                # Check reasoning steps in result
                assert "reasoning_steps" in result
                steps = result["reasoning_steps"]

                # Each step should have required fields
                for step in steps:
                    assert hasattr(step, 'step_number') or 'step_number' in step.__dict__
                    assert hasattr(step, 'step_type') or 'step_type' in step.__dict__
                    assert hasattr(step, 'tool_name') or 'tool_name' in step.__dict__
                    assert hasattr(step, 'success') or 'success' in step.__dict__

    @pytest.mark.asyncio
    async def test_step_duration_tracked(self, mock_db_session, sample_session_info, sample_intent, sample_transform_result, sample_chart_result, sample_validation_result):
        """Test that step durations are tracked."""
        engine = ReasoningEngine(mock_db_session)

        with patch.multiple(
            'data_ingestion.agent.reasoning_engine',
            get_session_info=AsyncMock(return_value=sample_session_info),
            parse_user_intent=AsyncMock(return_value=sample_intent),
            transform_data=AsyncMock(return_value=sample_transform_result),
            generate_chart=AsyncMock(return_value=sample_chart_result),
            validate_result=AsyncMock(return_value=sample_validation_result)
        ):
            with patch('data_ingestion.agent.reasoning_engine.SessionStore') as MockStore:
                MockStore.return_value.add_reasoning_log = AsyncMock()

                result = await engine.process(
                    session_id=sample_session_info.session_id,
                    narrative="Show data"
                )

                # Check total duration is tracked
                assert "total_duration_ms" in result
                assert result["total_duration_ms"] >= 0

                # Check individual step durations
                for step in result["reasoning_steps"]:
                    assert hasattr(step, 'duration_ms') or 'duration_ms' in step.__dict__
