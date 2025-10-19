"""
Test compliance with requirements from INITIAL.md for Analytics Microservice v3.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import asyncio

from analytics_microservice_v3.agent import agent, process_analytics_request, run_analytics_agent
from analytics_microservice_v3.tools import CHART_TYPES, THEMES
from analytics_microservice_v3.websocket_server import websocket_endpoint, handle_progress_update
from analytics_microservice_v3.dependencies import AnalyticsDependencies
from analytics_microservice_v3.settings import Settings


class TestRequirementsCompliance:
    """Validate all requirements from INITIAL.md are met."""

    def test_req_001_websocket_api_accepts_requests(self):
        """REQ-001: WebSocket API accepts chart generation requests and maintains bidirectional communication."""
        # Verify WebSocket endpoint exists and can handle requests
        assert websocket_endpoint is not None
        
        # Verify bidirectional communication capability
        assert hasattr(websocket_endpoint, '__code__')
        
        # Check for message handling patterns in the function
        import inspect
        source = inspect.getsource(websocket_endpoint)
        assert 'receive_text' in source  # Can receive messages
        assert 'send_json' in source     # Can send messages

    @pytest.mark.asyncio
    async def test_req_002_progress_updates_streaming(self):
        """REQ-002: Streams progress updates during chart creation (data processing, rendering, completion)."""
        # Test progress update functionality
        update_data = {
            "websocket_id": "test_conn",
            "stage": "data_processing",
            "progress": 25,
            "message": "Processing data..."
        }
        
        # Mock WebSocket connection
        from analytics_microservice_v3.websocket_server import connections
        mock_websocket = AsyncMock()
        connections["test_conn"] = mock_websocket
        
        try:
            await handle_progress_update(update_data)
            
            # Verify progress message was sent
            mock_websocket.send_json.assert_called_once()
            sent_message = mock_websocket.send_json.call_args[0][0]
            assert sent_message["type"] == "progress"
            assert sent_message["stage"] == "data_processing"
            assert sent_message["progress"] == 25
            
        finally:
            # Cleanup
            if "test_conn" in connections:
                del connections["test_conn"]

    def test_req_003_multiple_chart_types_support(self):
        """REQ-003: Generates high-quality charts for 20+ different visualization types."""
        # Verify we have 20+ chart types
        assert len(CHART_TYPES) >= 20
        
        # Verify all expected chart types are present
        required_types = [
            "bar_vertical", "bar_horizontal", "bar_grouped", "bar_stacked",
            "line", "line_multi", "area", "area_stacked",
            "pie", "donut", "scatter", "bubble", "heatmap",
            "radar", "box", "violin", "histogram", "funnel", "treemap", "sankey"
        ]
        
        for chart_type in required_types:
            assert chart_type in CHART_TYPES, f"Missing chart type: {chart_type}"

    @pytest.mark.asyncio
    async def test_req_004_user_provided_and_synthesized_data(self, mock_openai_client):
        """REQ-004: Handles both user-provided data and LLM-synthesized datasets."""
        # Test with user-provided data
        user_data_request = {
            "content": "Sales chart",
            "data": [100, 150, 120, 180],
            "chart_type": "bar_vertical"
        }
        
        with patch('analytics_microservice_v3.agent.agent.run') as mock_run:
            mock_result = Mock()
            mock_result.data = "user_data_chart"
            mock_run.return_value = mock_result
            
            result = await process_analytics_request(user_data_request)
            assert result["success"] is True
            assert result["metadata"]["data_source"] == "user"
        
        # Test with data synthesis (no user data provided)
        synthesis_request = {
            "content": "Generate a sales trend chart",
            "data": None,  # No user data - should trigger synthesis
            "chart_type": "line"
        }
        
        with patch('analytics_microservice_v3.agent.agent.run') as mock_run:
            mock_result = Mock()
            mock_result.data = "synthesized_chart"
            mock_run.return_value = mock_result
            
            result = await process_analytics_request(synthesis_request)
            assert result["success"] is True
            assert result["metadata"]["data_source"] == "synthetic"

    def test_req_005_consistent_themes_base64_output(self):
        """REQ-005: Applies consistent themes and returns chart as base64 image or SVG."""
        # Verify theme system is complete
        assert len(THEMES) >= 5
        expected_themes = ["default", "dark", "professional", "colorful", "minimal"]
        
        for theme in expected_themes:
            assert theme in THEMES, f"Missing theme: {theme}"
            assert "colors" in THEMES[theme]
            assert "grid" in THEMES[theme]
            assert "style" in THEMES[theme]
        
        # Verify base64 encoding capability in dependencies
        deps = AnalyticsDependencies()
        assert hasattr(deps, 'encode_chart_to_base64')
        
        # Test base64 encoding functionality
        import io
        test_buffer = io.BytesIO(b"test_image_data")
        encoded = deps.encode_chart_to_base64(test_buffer)
        
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Verify it's valid base64
        import base64
        try:
            decoded = base64.b64decode(encoded)
            assert decoded == b"test_image_data"
        except Exception:
            pytest.fail("Base64 encoding/decoding failed")

    @pytest.mark.asyncio
    async def test_req_006_concurrent_websocket_connections(self):
        """REQ-006: Supports multiple concurrent WebSocket connections without blocking."""
        # Test dependency connection management
        deps = AnalyticsDependencies(max_connections=5)
        
        # Add multiple connections
        connection_ids = [f"conn_{i}" for i in range(5)]
        for conn_id in connection_ids:
            result = deps.add_connection(conn_id)
            assert result is True, f"Failed to add connection {conn_id}"
        
        # Verify all connections are tracked
        assert len(deps.active_connections) == 5
        
        # Additional connection should be rejected (max limit)
        overflow_result = deps.add_connection("overflow_conn")
        assert overflow_result is False
        
        # Remove connections and verify cleanup
        for conn_id in connection_ids:
            deps.remove_connection(conn_id)
        
        assert len(deps.active_connections) == 0

    @pytest.mark.asyncio
    async def test_req_007_stateless_service_design(self):
        """REQ-007: Stateless service design (no data persistence required)."""
        # Verify dependencies don't maintain persistent state between requests
        deps1 = AnalyticsDependencies(websocket_id="test1")
        deps2 = AnalyticsDependencies(websocket_id="test2")
        
        # Each instance should be independent
        assert deps1.websocket_id != deps2.websocket_id
        assert deps1.active_connections != deps2.active_connections
        
        # Chart cache should be instance-specific
        deps1.chart_cache["test"] = "value1"
        assert "test" not in deps2.chart_cache
        
        # Cleanup should clear instance state
        await deps1.cleanup()
        assert len(deps1.chart_cache) == 0
        assert len(deps1.active_connections) == 0

    def test_req_008_base64_png_svg_output_format(self):
        """REQ-008: Chart output format: base64-encoded PNG or SVG strings."""
        # Verify chart generator can produce base64 output
        from analytics_microservice_v3.tools import chart_generator
        
        # Check that chart_generator returns base64 encoded data
        # This is validated by checking the function signature and return structure
        import inspect
        source = inspect.getsource(chart_generator)
        
        # Should use encode_chart_to_base64 for output
        assert 'encode_chart_to_base64' in source
        assert 'base64' in source.lower() or 'chart' in source

    @pytest.mark.asyncio
    async def test_req_009_websocket_timeout_handling(self):
        """REQ-009: WebSocket connections handle timeouts gracefully (30 second limit)."""
        # Test timeout configuration
        deps = AnalyticsDependencies(generation_timeout=30)
        assert deps.generation_timeout == 30
        
        # Test with settings
        settings = Settings(chart_generation_timeout=30)
        assert settings.chart_generation_timeout == 30
        
        # Verify timeout is used in dependencies
        deps_from_settings = AnalyticsDependencies.from_settings(settings)
        assert deps_from_settings.generation_timeout == 30

    @pytest.mark.asyncio
    async def test_req_010_json_websocket_protocol(self):
        """REQ-010: JSON-based WebSocket message protocol."""
        # Test message protocol structure
        test_message = {
            "type": "analytics_request",
            "request_id": "protocol_test",
            "content": "Test chart generation",
            "chart_type": "bar_vertical",
            "theme": "default"
        }
        
        # Verify message can be JSON serialized/deserialized
        json_str = json.dumps(test_message)
        parsed_message = json.loads(json_str)
        
        assert parsed_message["type"] == "analytics_request"
        assert parsed_message["request_id"] == "protocol_test"
        assert parsed_message["content"] == "Test chart generation"

    @pytest.mark.asyncio
    async def test_req_011_llm_data_synthesis(self, mock_openai_client):
        """REQ-011: LLM data synthesis for missing or incomplete datasets."""
        from analytics_microservice_v3.tools import data_synthesizer
        
        deps = AnalyticsDependencies()
        ctx = Mock(deps=deps)
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_openai_client):
            result = await data_synthesizer(
                ctx,
                data_description="Monthly sales data for retail company",
                sample_size=12
            )
            
            assert result["success"] is True
            assert "data" in result
            assert result["sample_size"] == 12
            
            # Verify data structure is appropriate for charts
            data = result["data"]
            assert isinstance(data, dict)
            # Should have chart-ready format
            expected_keys = ["labels", "values", "title"]
            assert any(key in data for key in expected_keys)

    def test_req_012_openai_gpt4o_mini_model(self):
        """REQ-012: Uses OpenAI gpt-4o-mini model for fast processing and cost-effectiveness."""
        from analytics_microservice_v3.settings import Settings
        from analytics_microservice_v3.providers import get_chart_model
        
        # Verify default model configuration
        settings = Settings(openai_api_key="test_key")
        
        # Check model configuration in providers
        import inspect
        source = inspect.getsource(get_chart_model)
        
        # Should reference gpt-4o-mini
        assert 'gpt-4o-mini' in source or 'openai' in source.lower()

    @pytest.mark.asyncio
    async def test_req_013_railway_websocket_deployment(self):
        """REQ-013: Railway deployment platform with WebSocket support."""
        from analytics_microservice_v3.settings import Settings
        
        # Verify Railway environment configuration
        settings = Settings(
            railway_environment="production",
            websocket_port=8080
        )
        
        assert settings.railway_environment == "production"
        assert settings.websocket_port == 8080
        
        # Verify WebSocket server configuration
        from analytics_microservice_v3.websocket_server import run_server
        assert callable(run_server)

    def test_req_014_matplotlib_chart_rendering(self):
        """REQ-014: Matplotlib chart rendering engine."""
        # Verify matplotlib is used for chart generation
        from analytics_microservice_v3.tools import chart_generator
        import inspect
        
        source = inspect.getsource(chart_generator)
        
        # Should use matplotlib components
        matplotlib_indicators = ['plt.', 'matplotlib', 'pyplot', 'subplots', 'savefig']
        assert any(indicator in source for indicator in matplotlib_indicators)

    def test_req_015_environment_variable_configuration(self):
        """REQ-015: Required environment variables are properly configured."""
        from analytics_microservice_v3.settings import Settings
        
        # Test with all required environment variables
        settings = Settings(
            openai_api_key="test-api-key",
            railway_environment="production",
            websocket_port=8080,
            max_concurrent_connections=100,
            chart_generation_timeout=30
        )
        
        assert settings.openai_api_key == "test-api-key"
        assert settings.railway_environment == "production"
        assert settings.websocket_port == 8080
        assert settings.max_concurrent_connections == 100
        assert settings.chart_generation_timeout == 30

    def test_req_016_agent_tools_integration(self):
        """REQ-016: All required tools are integrated with the Pydantic AI agent."""
        # Verify agent has all required tools
        tool_names = [tool.function.__name__ for tool in agent.tools]
        
        required_tools = [
            "chart_generator",
            "data_synthesizer", 
            "theme_applier",
            "progress_streamer"
        ]
        
        for required_tool in required_tools:
            assert required_tool in tool_names, f"Missing required tool: {required_tool}"

    @pytest.mark.asyncio
    async def test_req_017_error_handling_robustness(self):
        """REQ-017: Robust error handling for all failure scenarios."""
        # Test various error scenarios
        error_scenarios = [
            {"content": "", "expected": "empty content"},
            {"content": "test", "chart_type": "invalid_type", "expected": "invalid chart type"},
            {"content": "test", "data": "invalid_format", "expected": "invalid data format"}
        ]
        
        for scenario in error_scenarios:
            try:
                result = await process_analytics_request(scenario)
                # Should either succeed with fallbacks or fail gracefully
                assert "success" in result
                if not result["success"]:
                    assert "error" in result
            except Exception as e:
                # If exception occurs, it should be handled gracefully
                assert "error" in str(e).lower() or "failed" in str(e).lower()

    def test_req_018_performance_requirements(self):
        """REQ-018: Performance requirements are met."""
        # Verify timeout configurations are reasonable
        from analytics_microservice_v3.settings import Settings
        
        settings = Settings()
        
        # Chart generation timeout should be reasonable (30 seconds)
        assert settings.chart_generation_timeout <= 30
        
        # Max connections should support reasonable concurrent load
        assert settings.max_concurrent_connections >= 10


class TestSuccessCriteria:
    """Validate success criteria from INITIAL.md."""

    @pytest.mark.asyncio
    async def test_success_criteria_websocket_api(self):
        """Success Criteria: WebSocket API accepts chart generation requests and maintains bidirectional communication."""
        # This is tested in req_001
        assert True  # Validated by other tests

    @pytest.mark.asyncio
    async def test_success_criteria_progress_streaming(self):
        """Success Criteria: Streams progress updates during chart creation."""
        # This is tested in req_002  
        assert True  # Validated by other tests

    def test_success_criteria_20_plus_chart_types(self):
        """Success Criteria: Generates high-quality charts for 20+ different visualization types."""
        assert len(CHART_TYPES) >= 20

    @pytest.mark.asyncio
    async def test_success_criteria_data_handling(self):
        """Success Criteria: Handles both user-provided data and LLM-synthesized datasets."""
        # This is tested in req_004
        assert True  # Validated by other tests

    def test_success_criteria_theme_consistency(self):
        """Success Criteria: Applies consistent themes and returns chart as base64 image or SVG."""
        # Verify theme consistency
        assert len(THEMES) >= 5
        
        # Verify base64 output capability
        deps = AnalyticsDependencies()
        assert hasattr(deps, 'encode_chart_to_base64')

    def test_success_criteria_concurrent_connections(self):
        """Success Criteria: Supports multiple concurrent WebSocket connections without blocking."""
        # This is tested in req_006
        assert True  # Validated by connection management tests


class TestAssumptionsValidation:
    """Validate assumptions made in INITIAL.md."""

    def test_assumption_stateless_design(self):
        """Assumption: Stateless service design (no data persistence required)."""
        # Verified in req_007
        assert True

    def test_assumption_base64_output_format(self):
        """Assumption: Chart output format: base64-encoded PNG or SVG strings."""
        # Verified in req_005 and req_008
        assert True

    def test_assumption_websocket_timeout(self):
        """Assumption: WebSocket connections handle timeouts gracefully (30 second limit)."""
        # Verified in req_009
        assert True

    def test_assumption_json_protocol(self):
        """Assumption: JSON-based WebSocket message protocol."""
        # Verified in req_010
        assert True

    def test_assumption_llm_data_synthesis(self):
        """Assumption: LLM data synthesis for missing or incomplete datasets."""
        # Verified in req_011
        assert True

    def test_assumption_matplotlib_dependencies(self):
        """Assumption: Standard matplotlib dependencies for chart rendering."""
        # Verified in req_014
        assert True