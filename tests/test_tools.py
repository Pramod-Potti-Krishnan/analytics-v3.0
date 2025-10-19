"""
Test tool implementations for Analytics Microservice v3.
"""

import pytest
import json
import io
import base64
from unittest.mock import Mock, AsyncMock, patch
import matplotlib.pyplot as plt

from analytics_microservice_v3.tools import (
    chart_generator,
    data_synthesizer,
    theme_applier,
    progress_streamer,
    CHART_TYPES,
    THEMES
)
from analytics_microservice_v3.dependencies import AnalyticsDependencies


class TestChartGenerator:
    """Test chart generation tool."""

    @pytest.mark.asyncio
    async def test_chart_generator_bar_vertical(self, mock_dependencies, sample_chart_data):
        """Test vertical bar chart generation."""
        # Create context mock
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        result = await chart_generator(
            ctx,
            chart_type="bar_vertical",
            data=sample_chart_data,
            theme="default"
        )
        
        assert result["success"] is True
        assert "chart" in result
        assert result["chart_type"] == "bar_vertical"
        assert result["theme"] == "default"
        assert result["metadata"]["data_points"] == len(sample_chart_data["values"])

    @pytest.mark.asyncio
    async def test_chart_generator_line_chart(self, mock_dependencies):
        """Test line chart generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        line_data = {
            "x": [1, 2, 3, 4, 5],
            "y": [10, 25, 15, 30, 20],
            "title": "Line Chart Test"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="line",
            data=line_data,
            theme="dark"
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "line"
        assert result["theme"] == "dark"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_pie_chart(self, mock_dependencies):
        """Test pie chart generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        pie_data = {
            "labels": ["Category A", "Category B", "Category C"],
            "values": [30, 45, 25],
            "title": "Distribution Chart"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="pie",
            data=pie_data,
            theme="colorful"
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "pie"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_scatter_plot(self, mock_dependencies):
        """Test scatter plot generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        scatter_data = {
            "x": [1, 2, 3, 4, 5],
            "y": [2, 5, 3, 8, 7],
            "title": "Correlation Analysis"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="scatter",
            data=scatter_data,
            theme="professional"
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "scatter"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_heatmap(self, mock_dependencies):
        """Test heatmap generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        heatmap_data = {
            "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            "title": "Correlation Heatmap"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="heatmap",
            data=heatmap_data,
            theme="minimal"
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "heatmap"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_histogram(self, mock_dependencies):
        """Test histogram generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        hist_data = {
            "values": [1, 2, 2, 3, 3, 3, 4, 4, 5],
            "title": "Distribution Histogram"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="histogram",
            data=hist_data
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "histogram"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_box_plot(self, mock_dependencies):
        """Test box plot generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        box_data = {
            "datasets": [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]],
            "title": "Distribution Comparison"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="box",
            data=box_data
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "box"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_violin_plot(self, mock_dependencies):
        """Test violin plot generation."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        violin_data = {
            "datasets": [[1, 2, 3, 4, 5, 3, 4, 2, 3]],
            "title": "Distribution Shape"
        }
        
        result = await chart_generator(
            ctx,
            chart_type="violin",
            data=violin_data
        )
        
        assert result["success"] is True
        assert result["chart_type"] == "violin"
        assert "chart" in result

    @pytest.mark.asyncio
    async def test_chart_generator_invalid_type(self, mock_dependencies):
        """Test chart generation with invalid type."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        result = await chart_generator(
            ctx,
            chart_type="invalid_type",
            data={"values": [1, 2, 3]}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "Invalid chart type" in result["error"]

    @pytest.mark.asyncio
    async def test_chart_generator_progress_updates(self, mock_dependencies):
        """Test chart generation sends progress updates."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.send_progress_update = AsyncMock()
        
        await chart_generator(
            ctx,
            chart_type="bar_vertical",
            data={"labels": ["A"], "values": [1]}
        )
        
        # Verify progress updates were sent
        assert ctx.deps.send_progress_update.call_count >= 2

    @pytest.mark.asyncio
    async def test_chart_generator_error_handling(self, mock_dependencies):
        """Test chart generation error handling."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        # Mock matplotlib to raise exception
        with patch('matplotlib.pyplot.subplots', side_effect=Exception("Matplotlib error")):
            result = await chart_generator(
                ctx,
                chart_type="bar_vertical", 
                data={"values": [1, 2, 3]}
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "Matplotlib error" in result["error"]


class TestDataSynthesizer:
    """Test data synthesis tool."""

    @pytest.mark.asyncio
    async def test_data_synthesizer_success(self, mock_dependencies, mock_openai_client):
        """Test successful data synthesis."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_openai_client):
            result = await data_synthesizer(
                ctx,
                data_description="Monthly sales data",
                sample_size=10
            )
            
            assert result["success"] is True
            assert "data" in result
            assert result["sample_size"] == 10
            assert result["description"] == "Monthly sales data"

    @pytest.mark.asyncio
    async def test_data_synthesizer_json_error(self, mock_dependencies):
        """Test data synthesizer with JSON parsing error."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        # Mock OpenAI client to return invalid JSON
        mock_client = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        
        mock_message.content = "Invalid JSON response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_client):
            result = await data_synthesizer(
                ctx,
                data_description="Test data",
                sample_size=5
            )
            
            # Should fallback to default data generation
            assert result["success"] is True
            assert "warning" in result
            assert result["sample_size"] == 5

    @pytest.mark.asyncio
    async def test_data_synthesizer_sample_size_limits(self, mock_dependencies, mock_openai_client):
        """Test data synthesizer respects sample size limits."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_openai_client):
            # Test minimum limit
            result = await data_synthesizer(ctx, "test data", sample_size=5)
            assert result["sample_size"] == 10  # Should be clamped to minimum
            
            # Test maximum limit
            result = await data_synthesizer(ctx, "test data", sample_size=2000)
            assert result["sample_size"] == 1000  # Should be clamped to maximum

    @pytest.mark.asyncio
    async def test_data_synthesizer_progress_updates(self, mock_dependencies, mock_openai_client):
        """Test data synthesizer sends progress updates."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.send_progress_update = AsyncMock()
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_openai_client):
            await data_synthesizer(
                ctx,
                data_description="Test data",
                sample_size=20
            )
            
            # Verify progress updates were sent
            assert ctx.deps.send_progress_update.call_count >= 2

    @pytest.mark.asyncio
    async def test_data_synthesizer_error_handling(self, mock_dependencies):
        """Test data synthesizer error handling."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        
        # Mock OpenAI client to raise exception
        mock_client = Mock()
        mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))
        
        with patch('analytics_microservice_v3.tools.get_openai_client', return_value=mock_client):
            result = await data_synthesizer(
                ctx,
                data_description="Test data",
                sample_size=10
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "API error" in result["error"]


class TestThemeApplier:
    """Test theme application tool."""

    def test_theme_applier_default_theme(self):
        """Test applying default theme."""
        chart_config = {"title": "Test Chart"}
        
        result = theme_applier(chart_config, "default")
        
        assert result["success"] is True
        assert result["theme_applied"] == "default"
        assert "theme" in result["config"]
        assert result["config"]["theme"]["colors"] == THEMES["default"]["colors"]

    def test_theme_applier_dark_theme(self):
        """Test applying dark theme."""
        chart_config = {"title": "Test Chart"}
        
        result = theme_applier(chart_config, "dark")
        
        assert result["success"] is True
        assert result["theme_applied"] == "dark"
        assert result["config"]["background_color"] == "#1a1a1a"
        assert result["config"]["text_color"] == "#ffffff"

    def test_theme_applier_minimal_theme(self):
        """Test applying minimal theme."""
        chart_config = {"title": "Test Chart"}
        
        result = theme_applier(chart_config, "minimal")
        
        assert result["success"] is True
        assert result["theme_applied"] == "minimal"
        assert result["config"]["background_color"] == "#ffffff"
        assert result["config"]["show_legend"] is False

    def test_theme_applier_custom_colors(self):
        """Test theme with custom colors."""
        chart_config = {"title": "Test Chart"}
        custom_colors = ["#ff0000", "#00ff00", "#0000ff"]
        
        result = theme_applier(chart_config, "default", custom_colors)
        
        assert result["success"] is True
        assert result["config"]["theme"]["colors"] == custom_colors

    def test_theme_applier_invalid_colors(self):
        """Test theme with invalid custom colors."""
        chart_config = {"title": "Test Chart"}
        invalid_colors = ["not_a_color", "also_invalid"]
        
        result = theme_applier(chart_config, "default", invalid_colors)
        
        assert result["success"] is True
        # Should fall back to default theme colors
        assert result["config"]["theme"]["colors"] == THEMES["default"]["colors"]

    def test_theme_applier_unknown_theme(self):
        """Test applying unknown theme falls back to default."""
        chart_config = {"title": "Test Chart"}
        
        result = theme_applier(chart_config, "unknown_theme")
        
        assert result["success"] is True
        assert result["theme_applied"] == "unknown_theme"
        # Should use default theme configuration
        assert result["config"]["theme"]["colors"] == THEMES["default"]["colors"]

    def test_theme_applier_error_handling(self):
        """Test theme applier error handling."""
        # Pass invalid config that might cause error
        with patch('analytics_microservice_v3.tools.THEMES', side_effect=Exception("Theme error")):
            result = theme_applier({}, "default")
            
            assert result["success"] is False
            assert "error" in result


class TestProgressStreamer:
    """Test progress streaming tool."""

    @pytest.mark.asyncio
    async def test_progress_streamer_success(self, mock_dependencies):
        """Test successful progress streaming."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.active_connections = {"test_conn"}
        ctx.deps.chart_request_id = "req_123"
        ctx.deps.progress_callback = AsyncMock()
        
        progress_data = {
            "stage": "processing",
            "percentage": 50,
            "message": "Generating chart..."
        }
        
        result = await progress_streamer(ctx, "test_conn", progress_data)
        
        assert result["success"] is True
        assert result["delivered"] is True
        ctx.deps.progress_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_progress_streamer_no_callback(self, mock_dependencies):
        """Test progress streaming without callback."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.active_connections = {"test_conn"}
        ctx.deps.progress_callback = None
        
        result = await progress_streamer(
            ctx,
            "test_conn", 
            {"stage": "test", "percentage": 25}
        )
        
        assert result["success"] is True
        assert result["delivered"] is False

    @pytest.mark.asyncio
    async def test_progress_streamer_invalid_connection(self, mock_dependencies):
        """Test progress streaming with invalid connection."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.active_connections = set()  # No active connections
        
        result = await progress_streamer(
            ctx,
            "invalid_conn",
            {"stage": "test", "percentage": 50}
        )
        
        assert result["success"] is False
        assert result["delivered"] is False

    @pytest.mark.asyncio
    async def test_progress_streamer_callback_error(self, mock_dependencies):
        """Test progress streaming with callback error."""
        ctx = Mock()
        ctx.deps = mock_dependencies
        ctx.deps.active_connections = {"test_conn"}
        ctx.deps.progress_callback = AsyncMock(side_effect=Exception("Callback error"))
        
        result = await progress_streamer(
            ctx,
            "test_conn",
            {"stage": "error_test", "percentage": 75}
        )
        
        # Should handle error gracefully
        assert result["success"] is False
        assert result["delivered"] is False


class TestToolConfiguration:
    """Test tool configuration and constants."""

    def test_chart_types_complete(self):
        """Test all expected chart types are defined."""
        expected_types = [
            "bar_vertical", "bar_horizontal", "bar_grouped", "bar_stacked",
            "line", "line_multi", "area", "area_stacked", 
            "pie", "donut", "scatter", "bubble", "heatmap",
            "radar", "box", "violin", "histogram", "funnel", "treemap", "sankey"
        ]
        
        for chart_type in expected_types:
            assert chart_type in CHART_TYPES

    def test_themes_complete(self):
        """Test all expected themes are defined."""
        expected_themes = ["default", "dark", "professional", "colorful", "minimal"]
        
        for theme in expected_themes:
            assert theme in THEMES
            assert "colors" in THEMES[theme]
            assert "grid" in THEMES[theme] 
            assert "style" in THEMES[theme]

    def test_theme_color_validity(self):
        """Test theme colors are valid hex codes."""
        for theme_name, theme_config in THEMES.items():
            colors = theme_config["colors"]
            assert len(colors) >= 3  # At least 3 colors per theme
            
            for color in colors:
                assert isinstance(color, str)
                assert color.startswith("#")
                assert len(color) == 7  # Valid hex color format