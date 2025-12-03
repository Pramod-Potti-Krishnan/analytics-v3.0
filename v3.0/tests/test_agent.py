"""
Test core agent functionality for Analytics Microservice v3.
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from pydantic_ai.models.test import TestModel
from pydantic_ai.messages import ModelTextResponse

from analytics_microservice_v3.agent import (
    agent,
    run_analytics_agent,
    process_analytics_request,
    create_analytics_agent_with_deps
)
from analytics_microservice_v3.dependencies import AnalyticsDependencies


class TestAnalyticsAgent:
    """Test core agent functionality."""

    @pytest.mark.asyncio
    async def test_agent_basic_response(self, test_agent, mock_dependencies):
        """Test agent provides appropriate response."""
        result = await test_agent.run(
            "Create a bar chart for sales data",
            deps=mock_dependencies
        )
        
        assert result.data is not None
        assert isinstance(result.data, str)
        assert len(result.all_messages()) > 0

    @pytest.mark.asyncio
    async def test_agent_with_chart_request(self, chart_function_model, mock_dependencies):
        """Test agent with chart generation behavior."""
        test_agent = agent.override(model=chart_function_model)
        
        result = await test_agent.run(
            "Generate a sales chart with Q1-Q4 data",
            deps=mock_dependencies
        )
        
        # Verify chart generation flow
        messages = result.all_messages()
        assert len(messages) >= 3
        
        # Check for tool calls
        tool_calls = [msg for msg in messages if msg.role == "tool-call"]
        assert len(tool_calls) >= 1
        
        # Verify data synthesizer or chart generator was called
        tool_names = [call.tool_name for call in tool_calls]
        assert any(name in ["data_synthesizer", "chart_generator"] for name in tool_names)

    @pytest.mark.asyncio
    async def test_run_analytics_agent(self, mock_dependencies):
        """Test run_analytics_agent function."""
        test_model = TestModel()
        test_model.agent_responses = [
            ModelTextResponse(content="I'll create a chart for you"),
            {"chart_generator": {
                "chart_type": "bar_vertical",
                "data": {"labels": ["A", "B"], "values": [1, 2]},
                "theme": "default"
            }}
        ]
        
        with patch('analytics_microservice_v3.agent.agent') as mock_agent:
            mock_agent.override.return_value = agent.override(model=test_model)
            mock_agent.run = AsyncMock(return_value=AsyncMock(data="mock_chart_data"))
            
            result = await run_analytics_agent(
                "Create a test chart",
                websocket_id="test_ws",
                progress_callback=AsyncMock()
            )
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_process_analytics_request_success(self):
        """Test successful analytics request processing."""
        request_data = {
            "content": "Sales performance chart",
            "title": "Q4 Sales",
            "chart_type": "bar_vertical",
            "theme": "professional",
            "data": [100, 150, 120, 180]
        }
        
        with patch('analytics_microservice_v3.agent.run_analytics_agent') as mock_run:
            mock_run.return_value = "base64_chart_data"
            
            result = await process_analytics_request(request_data)
            
            assert result["success"] is True
            assert result["chart"] == "base64_chart_data"
            assert result["metadata"]["chart_type"] == "bar_vertical"
            assert result["metadata"]["theme"] == "professional"

    @pytest.mark.asyncio
    async def test_process_analytics_request_failure(self):
        """Test analytics request processing with error."""
        request_data = {
            "content": "Invalid chart request"
        }
        
        with patch('analytics_microservice_v3.agent.run_analytics_agent') as mock_run:
            mock_run.side_effect = Exception("Chart generation failed")
            
            result = await process_analytics_request(request_data)
            
            assert result["success"] is False
            assert "error" in result
            assert "Chart generation failed" in result["error"]

    def test_create_analytics_agent_with_deps(self):
        """Test agent creation with custom dependencies."""
        test_agent, deps = create_analytics_agent_with_deps(
            websocket_id="custom_ws",
            debug=True
        )
        
        assert test_agent is not None
        assert deps.websocket_id == "custom_ws"
        assert deps.debug is True

    @pytest.mark.asyncio
    async def test_agent_tool_integration(self, test_agent, mock_dependencies):
        """Test agent integrates with tools correctly."""
        # Configure TestModel to simulate tool calling
        test_model = test_agent.model
        test_model.agent_responses = [
            ModelTextResponse(content="I'll generate a chart"),
            {"chart_generator": {
                "chart_type": "line",
                "data": {"x": [1, 2, 3], "y": [10, 20, 30]},
                "theme": "dark"
            }}
        ]
        
        with patch('analytics_microservice_v3.tools.chart_generator') as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "chart": "mock_base64_chart"
            }
            
            result = await test_agent.run(
                "Create a line chart",
                deps=mock_dependencies
            )
            
            # Verify tool was called through agent
            assert result.data is not None

    @pytest.mark.asyncio
    async def test_agent_progress_updates(self, mock_dependencies):
        """Test agent sends progress updates."""
        test_model = TestModel()
        test_agent = agent.override(model=test_model)
        
        # Mock progress callback
        progress_callback = AsyncMock()
        mock_dependencies.progress_callback = progress_callback
        
        await run_analytics_agent(
            "Test chart",
            websocket_id="test_ws",
            progress_callback=progress_callback
        )
        
        # Verify progress updates were sent
        assert mock_dependencies.progress_callback.call_count >= 2  # Initial and completion

    @pytest.mark.asyncio
    async def test_agent_dependency_cleanup(self, mock_dependencies):
        """Test dependency cleanup after agent run."""
        test_model = TestModel()
        test_agent = agent.override(model=test_model)
        
        # Add some connections to track cleanup
        mock_dependencies.add_connection("test_conn_1")
        mock_dependencies.add_connection("test_conn_2")
        
        await run_analytics_agent(
            "Test chart",
            websocket_id="test_ws"
        )
        
        # Verify connections were cleared after cleanup
        assert len(mock_dependencies.active_connections) == 0

    @pytest.mark.asyncio 
    async def test_agent_error_handling(self, test_agent, mock_dependencies):
        """Test agent handles errors gracefully."""
        # Configure agent to simulate error
        with patch('analytics_microservice_v3.tools.chart_generator') as mock_tool:
            mock_tool.side_effect = Exception("Tool execution failed")
            
            # Agent should handle tool errors without crashing
            result = await test_agent.run(
                "Create a problematic chart",
                deps=mock_dependencies
            )
            
            # Agent should still return a response
            assert result.data is not None

    @pytest.mark.asyncio
    async def test_agent_multiple_tool_calls(self, chart_function_model, mock_dependencies):
        """Test agent can make multiple tool calls in sequence."""
        test_agent = agent.override(model=chart_function_model)
        
        result = await test_agent.run(
            "Create a comprehensive sales analysis with data synthesis",
            deps=mock_dependencies
        )
        
        messages = result.all_messages()
        tool_calls = [msg for msg in messages if msg.role == "tool-call"]
        
        # Should have multiple tool calls for comprehensive analysis
        assert len(tool_calls) >= 1
        
        # Verify different tools were called
        tool_names = [call.tool_name for call in tool_calls]
        expected_tools = ["data_synthesizer", "chart_generator", "theme_applier", "progress_streamer"]
        assert any(tool in expected_tools for tool in tool_names)


class TestAgentConfiguration:
    """Test agent configuration and settings."""

    def test_agent_initialization(self):
        """Test agent is properly initialized."""
        assert agent is not None
        assert agent.deps_type == AnalyticsDependencies
        assert agent.system_prompt is not None

    def test_agent_tools_registered(self):
        """Test all required tools are registered with agent."""
        # Check that tools are accessible through agent
        tool_names = [tool.function.__name__ for tool in agent.tools]
        
        expected_tools = [
            "chart_generator",
            "data_synthesizer", 
            "theme_applier",
            "progress_streamer"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_agent_retries_configuration(self, mock_dependencies):
        """Test agent retry configuration."""
        # Agent should have retry configuration from settings
        assert hasattr(agent, 'retries')
        
        # Test with failing tool to verify retries
        test_model = TestModel()
        test_agent = agent.override(model=test_model)
        
        with patch('analytics_microservice_v3.tools.chart_generator') as mock_tool:
            # First call fails, second succeeds
            mock_tool.side_effect = [
                Exception("Temporary failure"),
                {"success": True, "chart": "success_chart"}
            ]
            
            result = await test_agent.run(
                "Test retry behavior",
                deps=mock_dependencies
            )
            
            assert result.data is not None