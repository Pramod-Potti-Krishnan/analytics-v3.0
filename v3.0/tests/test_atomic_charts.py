"""
Unit Tests for Atomic Chart Endpoints (v3.5.0)

Tests all 14 gold standard chart types with various configurations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.atomic_models import (
    AtomicChartRequest,
    AtomicChartResponse,
    GOLD_STANDARD_CHARTS,
    ChartTypeId
)
from core.atomic_chart_generator import AtomicChartGenerator


class TestAtomicModels:
    """Test Pydantic models for atomic charts."""

    def test_gold_standard_charts_count(self):
        """Verify we have exactly 14 gold standard charts."""
        assert len(GOLD_STANDARD_CHARTS) == 14

    def test_chart_type_enum(self):
        """Verify ChartTypeId enum has all 14 types."""
        assert len(ChartTypeId) == 14
        assert ChartTypeId.LINE.value == "line"
        assert ChartTypeId.WATERFALL.value == "waterfall"

    def test_atomic_chart_request_defaults(self):
        """Test AtomicChartRequest default values."""
        request = AtomicChartRequest()

        assert request.narrative is None
        assert request.include_insights is False
        assert request.num_points is None
        assert request.width == 850
        assert request.height == 500
        assert request.theme == "professional"

    def test_atomic_chart_request_with_values(self):
        """Test AtomicChartRequest with provided values."""
        request = AtomicChartRequest(
            narrative="Show quarterly revenue",
            include_insights=True,
            num_points=4,
            width=900,
            height=600,
            chart_title="Revenue Q1-Q4"
        )

        assert request.narrative == "Show quarterly revenue"
        assert request.include_insights is True
        assert request.num_points == 4
        assert request.width == 900
        assert request.height == 600
        assert request.chart_title == "Revenue Q1-Q4"

    def test_atomic_chart_request_narrative_validation(self):
        """Test that empty narratives are converted to None."""
        request = AtomicChartRequest(narrative="  ")
        assert request.narrative is None

    def test_atomic_chart_request_num_points_validation(self):
        """Test num_points validation bounds."""
        # Valid range
        request = AtomicChartRequest(num_points=5)
        assert request.num_points == 5

        # Below minimum should fail
        with pytest.raises(ValueError):
            AtomicChartRequest(num_points=1)

        # Above maximum should fail
        with pytest.raises(ValueError):
            AtomicChartRequest(num_points=100)


class TestAtomicChartGenerator:
    """Test AtomicChartGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create generator instance for tests."""
        return AtomicChartGenerator(theme="professional")

    def test_generator_initialization(self, generator):
        """Test generator initializes with correct theme."""
        assert generator.theme == "professional"
        assert generator.synthetic_generator is not None
        assert generator.chartjs_generator is not None
        assert generator.insight_generator is not None

    def test_chart_configs_complete(self, generator):
        """Verify all 14 chart types have configs."""
        assert len(generator.CHART_CONFIGS) == 14

        for chart_id in GOLD_STANDARD_CHARTS:
            assert chart_id in generator.CHART_CONFIGS
            config = generator.CHART_CONFIGS[chart_id]
            assert "display_name" in config
            assert "category" in config
            assert "method" in config
            assert "use_cases" in config

    def test_get_chart_catalog(self, generator):
        """Test catalog generation."""
        catalog = generator.get_chart_catalog()

        assert len(catalog) == 14

        for item in catalog:
            assert "id" in item
            assert "name" in item
            assert "description" in item
            assert "category" in item
            assert "supports_multi_series" in item

    def test_generate_title_from_narrative(self, generator):
        """Test title generation from narrative."""
        title = generator._generate_title("line", "Show quarterly revenue growth for 2024")
        assert "Show" in title or "Quarterly" in title.title()

    def test_generate_title_fallback(self, generator):
        """Test title generation fallback."""
        title = generator._generate_title("line", None)
        assert title == "Line Chart"

    def test_transform_to_chartjs_format_simple(self, generator):
        """Test data transformation for simple charts."""
        data = [
            {"label": "Q1", "value": 100},
            {"label": "Q2", "value": 150}
        ]

        result = generator._transform_to_chartjs_format("line", data)

        assert "labels" in result
        assert "values" in result
        assert result["labels"] == ["Q1", "Q2"]
        assert result["values"] == [100, 150]

    def test_transform_to_chartjs_format_scatter(self, generator):
        """Test data transformation for scatter charts."""
        data = [
            {"label": "Point A", "x": 10, "y": 20},
            {"label": "Point B", "x": 30, "y": 40}
        ]

        result = generator._transform_to_chartjs_format("scatter", data)

        assert "labels" in result
        assert "datasets" in result
        assert len(result["datasets"]) == 1
        assert result["datasets"][0]["data"][0]["x"] == 10
        assert result["datasets"][0]["data"][0]["y"] == 20

    def test_parse_insights(self, generator):
        """Test insight parsing from LLM response."""
        explanation = """
        - Revenue grew 25% year over year
        - Customer acquisition improved significantly
        - Market share expanded to new regions
        """

        insights = generator._parse_insights(explanation)

        assert len(insights) >= 3
        assert "Revenue grew 25% year over year" in insights

    def test_generate_fallback_insights(self, generator):
        """Test fallback insight generation."""
        data = [
            {"label": "Q1", "value": 100},
            {"label": "Q2", "value": 150},
            {"label": "Q3", "value": 200}
        ]

        insights = generator._generate_fallback_insights(data, "line")

        assert len(insights) >= 3
        assert any("100" in i or "200" in i for i in insights)


class TestAtomicChartGeneration:
    """Integration tests for chart generation."""

    @pytest.fixture
    def generator(self):
        """Create generator with mocked insight generator."""
        gen = AtomicChartGenerator(theme="professional")
        # Mock the insight generator to avoid LLM calls
        gen.insight_generator.generate_l02_explanation = AsyncMock(
            return_value="- Test insight 1\n- Test insight 2\n- Test insight 3"
        )
        return gen

    @pytest.mark.asyncio
    async def test_generate_line_chart(self, generator):
        """Test line chart generation."""
        request = AtomicChartRequest(
            narrative="Show quarterly revenue",
            include_insights=False
        )

        response = await generator.generate("line", request)

        assert response.success is True
        assert response.chart_id == "line"
        assert response.chart_html is not None
        assert len(response.chart_html) > 100
        assert response.data_used is not None
        assert len(response.data_used) > 0
        assert response.element_id.startswith("atomic-chart-")
        assert response.insights_html is None

    @pytest.mark.asyncio
    async def test_generate_chart_with_insights(self, generator):
        """Test chart generation with insights panel."""
        request = AtomicChartRequest(
            narrative="Show department performance",
            include_insights=True
        )

        response = await generator.generate("bar_vertical", request)

        assert response.success is True
        assert response.insights_html is not None
        assert "Key Insights" in response.insights_html
        assert response.insights_dimensions is not None
        assert response.insights_dimensions.width == 400

    @pytest.mark.asyncio
    async def test_generate_all_chart_types(self, generator):
        """Test all 14 chart types can be generated."""
        request = AtomicChartRequest()

        for chart_id in GOLD_STANDARD_CHARTS:
            response = await generator.generate(chart_id, request)

            assert response.success is True, f"Failed for {chart_id}"
            assert response.chart_id == chart_id
            assert response.chart_html is not None
            assert response.data_used is not None

    @pytest.mark.asyncio
    async def test_invalid_chart_type(self, generator):
        """Test error handling for invalid chart type."""
        request = AtomicChartRequest()

        with pytest.raises(ValueError) as exc_info:
            await generator.generate("invalid_chart", request)

        assert "invalid_chart" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_custom_dimensions(self, generator):
        """Test custom width and height."""
        request = AtomicChartRequest(
            width=1000,
            height=700
        )

        response = await generator.generate("pie", request)

        assert response.chart_dimensions.width == 1000
        assert response.chart_dimensions.height == 700

    @pytest.mark.asyncio
    async def test_custom_title(self, generator):
        """Test custom chart title."""
        request = AtomicChartRequest(
            chart_title="My Custom Title"
        )

        response = await generator.generate("doughnut", request)

        assert response.chart_title == "My Custom Title"

    @pytest.mark.asyncio
    async def test_generation_time_tracking(self, generator):
        """Test that generation time is tracked."""
        request = AtomicChartRequest()

        response = await generator.generate("radar", request)

        assert response.generation_time_ms >= 0
        assert response.generation_time_ms < 5000  # Should be fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
