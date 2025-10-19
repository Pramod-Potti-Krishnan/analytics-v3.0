"""
Test configuration for Analytics Microservice v3.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelTextResponse

from analytics_microservice_v3.dependencies import AnalyticsDependencies
from analytics_microservice_v3.agent import agent
from analytics_microservice_v3.settings import Settings


@pytest.fixture
def test_model():
    """Create TestModel for basic agent testing."""
    return TestModel()


@pytest.fixture
def test_agent(test_model):
    """Create agent with TestModel for testing."""
    return agent.override(model=test_model)


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for testing."""
    deps = AnalyticsDependencies(
        websocket_id="test_connection",
        user_session_id="test_session",
        max_connections=10,
        generation_timeout=30,
        debug=True
    )
    
    # Mock the progress callback
    deps.progress_callback = AsyncMock()
    return deps


@pytest.fixture
def sample_chart_data():
    """Sample chart data for testing."""
    return {
        "labels": ["A", "B", "C", "D"],
        "values": [10, 20, 15, 25],
        "title": "Test Chart",
        "x": [1, 2, 3, 4],
        "y": [10, 20, 15, 25]
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for data synthesis tests."""
    mock_client = Mock()
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    
    mock_message.content = '{"labels": ["Item 1", "Item 2", "Item 3"], "values": [10, 20, 30], "title": "Generated Data"}'
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    
    return mock_client


@pytest.fixture
def chart_function_model():
    """Create FunctionModel for chart generation testing."""
    
    async def chart_generation_function(messages, tools):
        """Simulate chart generation behavior."""
        # First response - analyze request
        if len(messages) == 1:
            return ModelTextResponse(
                content="I'll generate a chart for your data analysis request"
            )
        
        # Second response - call data synthesizer if needed
        elif len(messages) == 2:
            return {
                "data_synthesizer": {
                    "data_description": "sales data for testing",
                    "sample_size": 10
                }
            }
        
        # Third response - call chart generator
        elif len(messages) >= 3:
            return {
                "chart_generator": {
                    "chart_type": "bar_vertical",
                    "data": {
                        "labels": ["Q1", "Q2", "Q3", "Q4"],
                        "values": [100, 150, 120, 180]
                    },
                    "theme": "default"
                }
            }
    
    return FunctionModel(chart_generation_function)


@pytest.fixture
def progress_function_model():
    """Create FunctionModel for progress streaming testing."""
    
    async def progress_function(messages, tools):
        """Simulate progress streaming behavior."""
        return {
            "progress_streamer": {
                "connection_id": "test_connection",
                "progress_data": {
                    "stage": "processing",
                    "percentage": 50,
                    "message": "Generating chart..."
                }
            }
        }
    
    return FunctionModel(progress_function)


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        openai_api_key="test_key",
        railway_environment="test",
        websocket_port=8888,
        max_concurrent_connections=5,
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def websocket_mock():
    """Mock WebSocket connection for testing."""
    websocket = Mock()
    websocket.accept = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def sample_websocket_messages():
    """Sample WebSocket messages for testing."""
    return {
        "analytics_request": {
            "type": "analytics_request",
            "request_id": "test_request_123",
            "content": "Create a sales chart",
            "title": "Q4 Sales Data",
            "chart_type": "bar_vertical",
            "theme": "professional",
            "data": [100, 150, 120, 180]
        },
        "ping": {
            "type": "ping"
        },
        "invalid": {
            "type": "unknown_type",
            "data": "test"
        }
    }