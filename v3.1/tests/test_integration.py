"""
Integration and error handling tests for Analytics Microservice v3.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import io
import base64

from analytics_microservice_v3.agent import run_analytics_agent, process_analytics_request
from analytics_microservice_v3.dependencies import AnalyticsDependencies
from analytics_microservice_v3.websocket_server import websocket_endpoint
from analytics_microservice_v3.tools import chart_generator, data_synthesizer


class TestFullIntegration:
    """Test complete end-to-end integration."""

    @pytest.mark.asyncio
    async def test_complete_chart_generation_flow(self, mock_openai_client):
        """Test complete flow from WebSocket request to chart generation."""
        # Mock all external dependencies
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_openai_client):
            with patch('analytics_microservice_v3.providers.get_chart_model') as mock_model:
                # Mock the agent model to simulate tool calls
                mock_model.return_value = Mock()
                
                # Create real dependencies
                deps = AnalyticsDependencies(
                    websocket_id="integration_test",
                    progress_callback=AsyncMock(),
                    debug=True
                )
                
                # Test data synthesis
                data_result = await data_synthesizer(
                    Mock(deps=deps),
                    data_description="Monthly sales figures",
                    sample_size=12
                )
                
                assert data_result["success"] is True
                assert "data" in data_result
                
                # Test chart generation with synthesized data
                chart_result = await chart_generator(
                    Mock(deps=deps),
                    chart_type="line",
                    data=data_result["data"],
                    theme="professional"
                )
                
                assert chart_result["success"] is True
                assert "chart" in chart_result
                assert chart_result["chart_type"] == "line"

    @pytest.mark.asyncio
    async def test_websocket_to_agent_integration(self):
        """Test WebSocket request processing through to agent."""
        websocket_request = {
            "type": "analytics_request",
            "request_id": "integration_123",
            "content": "Create a quarterly revenue chart",
            "title": "Q4 Revenue Analysis",
            "chart_type": "bar_vertical",
            "theme": "professional",
            "data": None  # Will trigger data synthesis
        }
        
        # Mock the entire agent run
        with patch('analytics_microservice_v3.agent.agent.run') as mock_agent_run:
            mock_result = Mock()
            mock_result.data = "base64_encoded_chart_data"
            mock_agent_run.return_value = mock_result
            
            result = await process_analytics_request(websocket_request)
            
            assert result["success"] is True
            assert result["chart"] == "base64_encoded_chart_data"
            assert result["metadata"]["chart_type"] == "bar_vertical"
            assert result["metadata"]["theme"] == "professional"
            assert result["metadata"]["data_source"] == "synthetic"  # No user data provided

    @pytest.mark.asyncio
    async def test_concurrent_requests_handling(self):
        """Test handling multiple concurrent analytics requests."""
        requests = [
            {"content": f"Chart {i}", "chart_type": "bar_vertical", "websocket_id": f"conn_{i}"}
            for i in range(5)
        ]
        
        with patch('analytics_microservice_v3.agent.agent.run') as mock_agent_run:
            mock_result = Mock()
            mock_result.data = "chart_data"
            mock_agent_run.return_value = mock_result
            
            # Process requests concurrently
            tasks = [process_analytics_request(req) for req in requests]
            results = await asyncio.gather(*tasks)
            
            # All requests should complete successfully
            for result in results:
                assert result["success"] is True
                assert result["chart"] == "chart_data"
            
            # Verify agent was called for each request
            assert mock_agent_run.call_count == 5

    @pytest.mark.asyncio
    async def test_progress_streaming_integration(self):
        """Test progress updates throughout the analytics pipeline."""
        deps = AnalyticsDependencies(
            websocket_id="progress_test",
            progress_callback=AsyncMock(),
            chart_request_id="req_123"
        )
        
        with patch('analytics_microservice_v3.tools.get_openai_client') as mock_client:
            # Mock OpenAI response
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            mock_message.content = '{"labels": ["A", "B"], "values": [1, 2]}'
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
            
            # Test data synthesizer progress
            ctx = Mock(deps=deps)
            await data_synthesizer(ctx, "test data", 10)
            
            # Test chart generator progress
            await chart_generator(ctx, "bar_vertical", {"labels": ["A"], "values": [1]})
            
            # Verify progress updates were sent
            assert deps.progress_callback.call_count >= 4  # Multiple progress updates

    @pytest.mark.asyncio
    async def test_memory_management_large_requests(self):
        """Test memory management with large chart requests."""
        # Simulate large dataset
        large_data = {
            "labels": [f"Item_{i}" for i in range(1000)],
            "values": list(range(1000)),
            "title": "Large Dataset Chart"
        }
        
        deps = AnalyticsDependencies(
            max_chart_size_mb=5,  # Set reasonable limit
            websocket_id="memory_test"
        )
        
        ctx = Mock(deps=deps)
        result = await chart_generator(
            ctx,
            chart_type="bar_vertical",
            data=large_data,
            theme="minimal"
        )
        
        # Should handle large datasets without crashing
        assert result["success"] is True
        assert "chart" in result
        
        # Verify chart size is within bounds (base64 encoded)
        chart_data = base64.b64decode(result["chart"])
        size_mb = len(chart_data) / (1024 * 1024)
        assert size_mb <= deps.max_chart_size_mb


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""

    @pytest.mark.asyncio
    async def test_openai_api_failure(self):
        """Test handling of OpenAI API failures."""
        deps = AnalyticsDependencies(websocket_id="error_test")
        ctx = Mock(deps=deps)
        
        # Mock OpenAI client to raise exception
        with patch('analytics_microservice_v3.tools.get_openai_client') as mock_client:
            mock_client.return_value.chat.completions.create = AsyncMock(
                side_effect=Exception("OpenAI API unavailable")
            )
            
            result = await data_synthesizer(ctx, "test data", 10)
            
            assert result["success"] is False
            assert "error" in result
            assert "OpenAI API unavailable" in result["error"]

    @pytest.mark.asyncio
    async def test_matplotlib_rendering_failure(self):
        """Test handling of matplotlib rendering failures."""
        deps = AnalyticsDependencies(websocket_id="render_error")
        ctx = Mock(deps=deps)
        
        # Mock matplotlib to raise exception during rendering
        with patch('matplotlib.pyplot.subplots', side_effect=Exception("Rendering failed")):
            result = await chart_generator(
                ctx,
                chart_type="bar_vertical",
                data={"labels": ["A"], "values": [1]}
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "Rendering failed" in result["error"]

    @pytest.mark.asyncio
    async def test_websocket_connection_loss_during_processing(self):
        """Test handling connection loss during chart generation."""
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_json = AsyncMock(side_effect=Exception("Connection lost"))
        mock_websocket.receive_text = AsyncMock(return_value=json.dumps({
            "type": "analytics_request",
            "request_id": "connection_test",
            "content": "Test chart"
        }))
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            with patch('analytics_microservice_v3.websocket_server.process_analytics_request') as mock_process:
                mock_process.return_value = {"success": True, "chart": "test", "metadata": {}}
                
                try:
                    await websocket_endpoint(mock_websocket)
                except Exception:
                    pass  # Expected due to connection loss
                
                # Cleanup should still be called
                mock_deps.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_chart_data_handling(self):
        """Test handling of invalid or corrupted chart data."""
        deps = AnalyticsDependencies(websocket_id="invalid_data")
        ctx = Mock(deps=deps)
        
        # Test with various invalid data scenarios
        invalid_datasets = [
            {"labels": None, "values": [1, 2, 3]},  # None labels
            {"labels": ["A", "B"], "values": None},  # None values
            {"labels": [], "values": []},  # Empty data
            {"labels": ["A"], "values": [1, 2, 3]},  # Mismatched lengths
            {"matrix": None},  # Invalid matrix for heatmap
        ]
        
        for invalid_data in invalid_datasets:
            result = await chart_generator(
                ctx,
                chart_type="bar_vertical",
                data=invalid_data
            )
            
            # Should either succeed with fallback or fail gracefully
            assert "success" in result
            if not result["success"]:
                assert "error" in result

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for long-running operations."""
        deps = AnalyticsDependencies(
            websocket_id="timeout_test",
            generation_timeout=1  # Very short timeout
        )
        
        # Mock slow operation
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(2)  # Longer than timeout
            return {"success": True, "chart": "data"}
        
        with patch('analytics_microservice_v3.agent.agent.run', side_effect=slow_operation):
            start_time = datetime.utcnow()
            
            # This should handle timeout gracefully
            try:
                await asyncio.wait_for(
                    run_analytics_agent("Test chart", websocket_id="timeout_test"),
                    timeout=1.5
                )
            except asyncio.TimeoutError:
                pass  # Expected
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            assert elapsed < 3  # Shouldn't wait for full slow operation

    @pytest.mark.asyncio
    async def test_resource_exhaustion_handling(self):
        """Test handling of resource exhaustion scenarios."""
        deps = AnalyticsDependencies(
            websocket_id="resource_test",
            max_connections=2
        )
        
        # Fill up connection slots
        assert deps.add_connection("conn_1") is True
        assert deps.add_connection("conn_2") is True
        
        # Next connection should be rejected
        assert deps.add_connection("conn_3") is False
        
        # Cleanup and verify resources are freed
        deps.remove_connection("conn_1")
        assert deps.add_connection("conn_3") is True

    @pytest.mark.asyncio
    async def test_malformed_request_handling(self):
        """Test handling of malformed analytics requests."""
        malformed_requests = [
            {},  # Empty request
            {"type": "analytics_request"},  # Missing content
            {"type": "analytics_request", "content": ""},  # Empty content
            {"type": "analytics_request", "content": "test", "chart_type": "invalid"},  # Invalid chart type
            {"type": "analytics_request", "content": "test", "data": "not_a_list"},  # Invalid data format
        ]
        
        for request in malformed_requests:
            result = await process_analytics_request(request)
            
            # Should handle gracefully - either success with defaults or controlled failure
            assert "success" in result
            if not result["success"]:
                assert "error" in result

    @pytest.mark.asyncio
    async def test_dependency_injection_failure(self):
        """Test handling of dependency injection failures."""
        # Test with invalid settings
        with patch('analytics_microservice_v3.dependencies.AnalyticsDependencies.from_settings') as mock_from_settings:
            mock_from_settings.side_effect = Exception("Dependency creation failed")
            
            try:
                result = await process_analytics_request({
                    "content": "Test chart",
                    "websocket_id": "dep_fail_test"
                })
                
                # Should either handle gracefully or fail controlled
                assert "success" in result
                if not result["success"]:
                    assert "error" in result
                    
            except Exception as e:
                # If exception propagates, it should be descriptive
                assert "Dependency creation failed" in str(e)


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""

    @pytest.mark.asyncio
    async def test_rapid_request_succession(self):
        """Test handling rapid succession of requests."""
        requests = [
            {"content": f"Chart {i}", "websocket_id": f"rapid_{i}"}
            for i in range(10)
        ]
        
        with patch('analytics_microservice_v3.agent.agent.run') as mock_agent_run:
            mock_result = Mock()
            mock_result.data = "quick_chart"
            mock_agent_run.return_value = mock_result
            
            start_time = datetime.utcnow()
            
            # Fire all requests rapidly
            tasks = [process_analytics_request(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Should complete in reasonable time (adjust based on performance expectations)
            assert elapsed < 10  # 10 seconds for 10 requests should be reasonable
            
            # Most requests should succeed (some might fail due to resource limits)
            successful = [r for r in results if isinstance(r, dict) and r.get("success")]
            assert len(successful) >= 5  # At least half should succeed

    @pytest.mark.asyncio
    async def test_memory_cleanup_verification(self):
        """Test that memory is properly cleaned up after operations."""
        import gc
        
        initial_objects = len(gc.get_objects())
        
        # Process several requests to potentially create memory leaks
        for i in range(5):
            deps = AnalyticsDependencies(websocket_id=f"cleanup_{i}")
            deps.add_connection(f"conn_{i}")
            
            with patch('analytics_microservice_v3.agent.agent.run') as mock_run:
                mock_result = Mock()
                mock_result.data = f"chart_{i}"
                mock_run.return_value = mock_result
                
                await run_analytics_agent(f"Chart {i}", websocket_id=f"cleanup_{i}")
                await deps.cleanup()
        
        # Force garbage collection
        gc.collect()
        
        # Object count should not have grown significantly
        final_objects = len(gc.get_objects())
        growth = final_objects - initial_objects
        
        # Allow some growth but not excessive (adjust threshold as needed)
        assert growth < 1000  # Threshold for reasonable memory growth

    @pytest.mark.asyncio
    async def test_connection_limit_enforcement(self):
        """Test that connection limits are properly enforced."""
        deps = AnalyticsDependencies(max_connections=3)
        
        # Fill connection pool
        connections = []
        for i in range(3):
            conn_id = f"limit_test_{i}"
            assert deps.add_connection(conn_id) is True
            connections.append(conn_id)
        
        # Additional connections should be rejected
        assert deps.add_connection("overflow_1") is False
        assert deps.add_connection("overflow_2") is False
        
        # Remove one connection
        deps.remove_connection(connections[0])
        
        # Now should be able to add one more
        assert deps.add_connection("new_connection") is True
        assert deps.add_connection("still_overflow") is False