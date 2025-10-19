"""
Test WebSocket communication for Analytics Microservice v3.
"""

import pytest
import json
import uuid
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from analytics_microservice_v3.websocket_server import (
    websocket_endpoint,
    handle_progress_update,
    send_websocket_message,
    connections,
    dependencies_map
)


class TestWebSocketCommunication:
    """Test WebSocket message handling."""

    @pytest.mark.asyncio
    async def test_websocket_connection_establishment(self, websocket_mock):
        """Test WebSocket connection establishment."""
        # Mock the WebSocket accept process
        websocket_mock.receive_text.side_effect = [
            json.dumps({"type": "ping"}),
            Exception("Disconnect")  # Simulate disconnect
        ]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            # This should not raise an exception
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass  # Expected due to disconnect simulation
            
            # Verify connection was accepted
            websocket_mock.accept.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_max_connections_reached(self, websocket_mock):
        """Test WebSocket connection rejection when max connections reached."""
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = False  # Max connections reached
            mock_deps_class.from_settings.return_value = mock_deps
            
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass
            
            # Should send error and close connection
            websocket_mock.send_json.assert_called()
            websocket_mock.close.assert_called_with(code=1013, reason="Max connections reached")

    @pytest.mark.asyncio
    async def test_analytics_request_processing(self, websocket_mock, sample_websocket_messages):
        """Test analytics request processing via WebSocket."""
        request_message = json.dumps(sample_websocket_messages["analytics_request"])
        websocket_mock.receive_text.side_effect = [request_message, Exception("Disconnect")]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            with patch('analytics_microservice_v3.websocket_server.process_analytics_request') as mock_process:
                mock_process.return_value = {
                    "success": True,
                    "chart": "base64_chart_data",
                    "metadata": {"chart_type": "bar_vertical"}
                }
                
                try:
                    await websocket_endpoint(websocket_mock)
                except Exception:
                    pass
                
                # Verify analytics request was processed
                mock_process.assert_called_once()
                
                # Verify response was sent
                assert websocket_mock.send_json.call_count >= 2  # Welcome + response

    @pytest.mark.asyncio
    async def test_ping_pong_handling(self, websocket_mock, sample_websocket_messages):
        """Test ping/pong message handling."""
        ping_message = json.dumps(sample_websocket_messages["ping"])
        websocket_mock.receive_text.side_effect = [ping_message, Exception("Disconnect")]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass
            
            # Verify pong response was sent
            calls = websocket_mock.send_json.call_args_list
            pong_sent = any(call[0][0].get("type") == "pong" for call in calls)
            assert pong_sent

    @pytest.mark.asyncio
    async def test_unknown_message_type(self, websocket_mock, sample_websocket_messages):
        """Test handling of unknown message types."""
        invalid_message = json.dumps(sample_websocket_messages["invalid"])
        websocket_mock.receive_text.side_effect = [invalid_message, Exception("Disconnect")]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass
            
            # Verify error response was sent
            calls = websocket_mock.send_json.call_args_list
            error_sent = any("error" in call[0][0] for call in calls)
            assert error_sent

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, websocket_mock):
        """Test handling of invalid JSON messages."""
        websocket_mock.receive_text.side_effect = ["invalid json", Exception("Disconnect")]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass
            
            # Verify JSON error was handled
            calls = websocket_mock.send_json.call_args_list
            json_error_sent = any("Invalid JSON" in str(call[0][0]) for call in calls)
            assert json_error_sent

    @pytest.mark.asyncio
    async def test_progress_update_handling(self):
        """Test progress update message handling."""
        update_data = {
            "websocket_id": "test_connection",
            "stage": "processing",
            "progress": 50,
            "message": "Processing chart data"
        }
        
        # Add mock connection
        mock_websocket = AsyncMock()
        connections["test_connection"] = mock_websocket
        
        try:
            await handle_progress_update(update_data)
            
            # Verify progress message was sent
            mock_websocket.send_json.assert_called_once()
            sent_message = mock_websocket.send_json.call_args[0][0]
            assert sent_message["type"] == "progress"
            assert sent_message["stage"] == "processing"
            assert sent_message["progress"] == 50
            
        finally:
            # Cleanup
            if "test_connection" in connections:
                del connections["test_connection"]

    @pytest.mark.asyncio
    async def test_websocket_message_send_error(self):
        """Test WebSocket message send error handling."""
        mock_websocket = Mock()
        mock_websocket.send_json = AsyncMock(side_effect=Exception("Send failed"))
        
        # Should not raise exception
        await send_websocket_message(mock_websocket, {"test": "message"})
        
        # Verify attempt was made
        mock_websocket.send_json.assert_called_once_with({"test": "message"})

    @pytest.mark.asyncio
    async def test_connection_cleanup_on_disconnect(self, websocket_mock):
        """Test proper cleanup when WebSocket disconnects."""
        websocket_mock.receive_text.side_effect = Exception("WebSocketDisconnect")
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            try:
                await websocket_endpoint(websocket_mock)
            except Exception:
                pass
            
            # Verify cleanup was called
            mock_deps.cleanup.assert_called_once()
            mock_deps.remove_connection.assert_called_once()


class TestWebSocketIntegration:
    """Test WebSocket integration with agent."""

    @pytest.mark.asyncio
    async def test_full_analytics_flow(self, websocket_mock):
        """Test complete analytics flow via WebSocket."""
        analytics_request = {
            "type": "analytics_request",
            "request_id": "flow_test_123",
            "content": "Sales performance chart",
            "title": "Q4 Sales",
            "chart_type": "bar_vertical",
            "theme": "professional",
            "data": [100, 150, 120, 180]
        }
        
        websocket_mock.receive_text.side_effect = [
            json.dumps(analytics_request),
            Exception("Disconnect")
        ]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps.chart_request_id = None
            mock_deps.generation_start_time = None
            mock_deps_class.from_settings.return_value = mock_deps
            
            with patch('analytics_microservice_v3.websocket_server.process_analytics_request') as mock_process:
                mock_process.return_value = {
                    "success": True,
                    "chart": "generated_chart_base64",
                    "metadata": {
                        "chart_type": "bar_vertical",
                        "theme": "professional",
                        "generation_method": "direct"
                    }
                }
                
                try:
                    await websocket_endpoint(websocket_mock)
                except Exception:
                    pass
                
                # Verify request was processed with correct parameters
                mock_process.assert_called_once()
                call_args = mock_process.call_args[0][0]
                
                assert call_args["content"] == "Sales performance chart"
                assert call_args["title"] == "Q4 Sales"
                assert call_args["chart_type"] == "bar_vertical"
                assert call_args["theme"] == "professional"
                assert call_args["data"] == [100, 150, 120, 180]
                
                # Verify response structure
                response_calls = [call for call in websocket_mock.send_json.call_args_list 
                                if call[0][0].get("type") == "analytics_response"]
                assert len(response_calls) > 0
                
                response = response_calls[0][0][0]
                assert response["success"] is True
                assert response["request_id"] == "flow_test_123"
                assert response["chart"] == "generated_chart_base64"
                assert response["metadata"]["generation_time_ms"] is not None

    @pytest.mark.asyncio
    async def test_concurrent_connections(self):
        """Test handling multiple concurrent WebSocket connections."""
        connection_ids = ["conn_1", "conn_2", "conn_3"]
        
        # Simulate multiple connections
        for conn_id in connection_ids:
            mock_websocket = AsyncMock()
            connections[conn_id] = mock_websocket
            
            mock_deps = Mock()
            mock_deps.cleanup = AsyncMock()
            dependencies_map[conn_id] = mock_deps
        
        try:
            # Verify all connections are tracked
            assert len(connections) == 3
            assert len(dependencies_map) == 3
            
            # Test progress update to specific connection
            await handle_progress_update({
                "websocket_id": "conn_2",
                "stage": "test",
                "progress": 75
            })
            
            # Only conn_2 should receive the update
            connections["conn_2"].send_json.assert_called_once()
            connections["conn_1"].send_json.assert_not_called()
            connections["conn_3"].send_json.assert_not_called()
            
        finally:
            # Cleanup
            for conn_id in connection_ids:
                if conn_id in connections:
                    del connections[conn_id]
                if conn_id in dependencies_map:
                    del dependencies_map[conn_id]

    @pytest.mark.asyncio
    async def test_analytics_request_with_options(self, websocket_mock):
        """Test analytics request with additional options."""
        analytics_request = {
            "type": "analytics_request",
            "request_id": "options_test",
            "content": "Enhanced chart with options",
            "options": {
                "use_synthetic_data": True,
                "enhance_labels": True,
                "output_format": "svg"
            }
        }
        
        websocket_mock.receive_text.side_effect = [
            json.dumps(analytics_request),
            Exception("Disconnect")
        ]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            with patch('analytics_microservice_v3.websocket_server.process_analytics_request') as mock_process:
                mock_process.return_value = {"success": True, "chart": "test", "metadata": {}}
                
                try:
                    await websocket_endpoint(websocket_mock)
                except Exception:
                    pass
                
                # Verify options were passed through
                call_args = mock_process.call_args[0][0]
                assert call_args["use_synthetic_data"] is True
                assert call_args["enhance_labels"] is True
                assert call_args["output_format"] == "svg"

    @pytest.mark.asyncio
    async def test_error_in_analytics_processing(self, websocket_mock):
        """Test error handling during analytics processing."""
        analytics_request = {
            "type": "analytics_request",
            "request_id": "error_test",
            "content": "Chart that will fail"
        }
        
        websocket_mock.receive_text.side_effect = [
            json.dumps(analytics_request),
            Exception("Disconnect")
        ]
        
        with patch('analytics_microservice_v3.websocket_server.AnalyticsDependencies') as mock_deps_class:
            mock_deps = Mock()
            mock_deps.add_connection.return_value = True
            mock_deps.cleanup = AsyncMock()
            mock_deps.remove_connection = Mock()
            mock_deps_class.from_settings.return_value = mock_deps
            
            with patch('analytics_microservice_v3.websocket_server.process_analytics_request') as mock_process:
                mock_process.return_value = {
                    "success": False,
                    "error": "Chart generation failed",
                    "metadata": {}
                }
                
                try:
                    await websocket_endpoint(websocket_mock)
                except Exception:
                    pass
                
                # Verify error response was sent
                response_calls = [call for call in websocket_mock.send_json.call_args_list 
                                if call[0][0].get("type") == "analytics_response"]
                assert len(response_calls) > 0
                
                response = response_calls[0][0][0]
                assert response["success"] is False
                assert response["error"] == "Chart generation failed"


class TestWebSocketServer:
    """Test WebSocket server functionality."""

    def test_connections_tracking(self):
        """Test connection tracking dictionaries."""
        # Start with clean state
        initial_connections = len(connections)
        initial_deps = len(dependencies_map)
        
        # Add test connection
        test_conn_id = "test_tracking"
        connections[test_conn_id] = Mock()
        dependencies_map[test_conn_id] = Mock()
        
        try:
            assert len(connections) == initial_connections + 1
            assert len(dependencies_map) == initial_deps + 1
            assert test_conn_id in connections
            assert test_conn_id in dependencies_map
            
        finally:
            # Cleanup
            if test_conn_id in connections:
                del connections[test_conn_id]
            if test_conn_id in dependencies_map:
                del dependencies_map[test_conn_id]

    @pytest.mark.asyncio
    async def test_lifespan_cleanup(self):
        """Test application lifespan cleanup."""
        from analytics_microservice_v3.websocket_server import lifespan
        from fastapi import FastAPI
        
        # Add test dependencies that need cleanup
        mock_dep1 = Mock()
        mock_dep1.cleanup = AsyncMock()
        mock_dep2 = Mock()
        mock_dep2.cleanup = AsyncMock()
        
        dependencies_map["test1"] = mock_dep1
        dependencies_map["test2"] = mock_dep2
        connections["test1"] = Mock()
        connections["test2"] = Mock()
        
        try:
            app = FastAPI()
            async with lifespan(app):
                # Verify dependencies are present during operation
                assert len(dependencies_map) >= 2
                assert len(connections) >= 2
            
            # After lifespan, cleanup should have been called
            mock_dep1.cleanup.assert_called_once()
            mock_dep2.cleanup.assert_called_once()
            assert len(connections) == 0
            assert len(dependencies_map) == 0
            
        finally:
            # Ensure cleanup
            connections.clear()
            dependencies_map.clear()