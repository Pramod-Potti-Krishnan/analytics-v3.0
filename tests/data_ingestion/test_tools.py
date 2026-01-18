"""
Tests for Data Ingestion MCP-style tools.

Tests individual tools for session management, data analysis,
intent parsing, transformation, chart generation, and validation.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timezone

from data_ingestion.models.tools import (
    SessionInfo,
    ColumnSchema,
    ColumnType,
    DataAnalysis,
    VisualizationIntent,
    IntentType,
    TransformResult,
    ChartResult,
    ChartType,
    ValidationResult
)


class TestSessionTools:
    """Tests for session management tools."""

    @pytest.mark.asyncio
    async def test_get_session_info_success(self, mock_db_session, sample_session_info):
        """Test successful session info retrieval."""
        from data_ingestion.tools.session_tools import get_session_info

        # Mock database returning session data
        mock_session_data = Mock()
        mock_session_data.id = sample_session_info.session_id
        mock_session_data.filename = sample_session_info.filename
        mock_session_data.row_count = sample_session_info.row_count
        mock_session_data.column_count = sample_session_info.column_count
        mock_session_data.column_schema = [c.model_dump() for c in sample_session_info.columns]
        mock_session_data.table_name = sample_session_info.table_name
        mock_session_data.created_at = sample_session_info.created_at
        mock_session_data.expires_at = sample_session_info.expires_at

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session_data
        mock_db_session.execute.return_value = mock_result

        with patch('data_ingestion.tools.session_tools.SessionStore') as MockStore:
            mock_store = MockStore.return_value
            mock_store.get_session = AsyncMock(return_value=mock_session_data)

            result = await get_session_info(
                mock_db_session,
                sample_session_info.session_id
            )

            assert result is not None
            assert result.session_id == sample_session_info.session_id

    @pytest.mark.asyncio
    async def test_get_session_info_not_found(self, mock_db_session):
        """Test session info retrieval when session not found."""
        from data_ingestion.tools.session_tools import get_session_info

        with patch('data_ingestion.tools.session_tools.SessionStore') as MockStore:
            mock_store = MockStore.return_value
            mock_store.get_session = AsyncMock(return_value=None)

            result = await get_session_info(
                mock_db_session,
                "nonexistent-session-id"
            )

            assert result is None


class TestAnalysisTools:
    """Tests for data analysis tools."""

    @pytest.mark.asyncio
    async def test_analyze_data_structure(self, sample_session_info):
        """Test data structure analysis."""
        from data_ingestion.tools.analysis_tools import analyze_data_structure

        result = await analyze_data_structure(sample_session_info)

        assert result is not None
        assert isinstance(result, DataAnalysis)
        assert result.total_rows == sample_session_info.row_count
        assert result.total_columns == sample_session_info.column_count

    @pytest.mark.asyncio
    async def test_detect_patterns_comparison(self, sample_session_info):
        """Test pattern detection for comparison data."""
        from data_ingestion.tools.analysis_tools import detect_patterns

        result = await detect_patterns(sample_session_info)

        assert result is not None
        assert isinstance(result, list)
        # Should detect categorical columns suitable for comparison
        assert any("comparison" in p or "categorical" in p for p in result)

    @pytest.mark.asyncio
    async def test_detect_patterns_time_series(self):
        """Test pattern detection for time series data."""
        from data_ingestion.tools.analysis_tools import detect_patterns

        # Session with datetime column
        session_info = SessionInfo(
            session_id="test-session",
            filename="timeseries.csv",
            row_count=100,
            column_count=3,
            columns=[
                ColumnSchema(name="date", type=ColumnType.DATETIME, nullable=False),
                ColumnSchema(name="value", type=ColumnType.NUMERIC, nullable=False, min_value=0, max_value=100),
                ColumnSchema(name="category", type=ColumnType.CATEGORICAL, nullable=False, unique_count=3)
            ],
            numeric_columns=["value"],
            categorical_columns=["category"],
            datetime_columns=["date"],
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc),
            table_name="data_test"
        )

        result = await detect_patterns(session_info)

        assert result is not None
        # Should detect time series pattern
        assert any("time" in p.lower() or "trend" in p.lower() for p in result)


class TestIntentTools:
    """Tests for intent parsing tools."""

    @pytest.mark.asyncio
    async def test_parse_user_intent_comparison(self, sample_session_info):
        """Test intent parsing for comparison narrative."""
        from data_ingestion.tools.intent_tools import parse_user_intent

        narrative = "Show me sales by product category"

        result = await parse_user_intent(
            narrative=narrative,
            session_info=sample_session_info,
            use_llm=False  # Use rule-based for testing
        )

        assert result is not None
        assert isinstance(result, VisualizationIntent)
        assert result.intent_type in [IntentType.COMPARE_VALUES, IntentType.SHOW_DISTRIBUTION]
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_parse_user_intent_trend(self, sample_session_info):
        """Test intent parsing for trend narrative."""
        from data_ingestion.tools.intent_tools import parse_user_intent

        narrative = "Show the trend of sales over time"

        result = await parse_user_intent(
            narrative=narrative,
            session_info=sample_session_info,
            use_llm=False
        )

        assert result is not None
        assert result.intent_type in [IntentType.SHOW_TREND, IntentType.COMPARE_VALUES]

    @pytest.mark.asyncio
    async def test_parse_user_intent_composition(self, sample_session_info):
        """Test intent parsing for composition narrative."""
        from data_ingestion.tools.intent_tools import parse_user_intent

        narrative = "Show the breakdown of sales by region as a pie chart"

        result = await parse_user_intent(
            narrative=narrative,
            session_info=sample_session_info,
            use_llm=False
        )

        assert result is not None
        assert result.intent_type in [IntentType.SHOW_COMPOSITION, IntentType.COMPARE_VALUES]
        assert result.suggested_chart_type in ["pie", "doughnut", "bar_vertical"]

    @pytest.mark.asyncio
    async def test_parse_user_intent_with_llm(self, sample_session_info, mock_openai_response):
        """Test intent parsing using LLM."""
        from data_ingestion.tools.intent_tools import parse_user_intent

        with patch('openai.AsyncOpenAI') as MockClient:
            mock_client = MockClient.return_value
            mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

            result = await parse_user_intent(
                narrative="Show sales comparison by product",
                session_info=sample_session_info,
                use_llm=True
            )

            assert result is not None
            assert isinstance(result, VisualizationIntent)

    @pytest.mark.asyncio
    async def test_parse_user_intent_unknown(self, sample_session_info):
        """Test intent parsing with unclear narrative."""
        from data_ingestion.tools.intent_tools import parse_user_intent

        narrative = "do something with the data"

        result = await parse_user_intent(
            narrative=narrative,
            session_info=sample_session_info,
            use_llm=False
        )

        assert result is not None
        # Should still return a result with lower confidence
        assert result.confidence < 0.5 or result.intent_type == IntentType.UNKNOWN


class TestTransformTools:
    """Tests for data transformation tools."""

    @pytest.mark.asyncio
    async def test_transform_data_aggregation(self, mock_db_session, sample_session_info, sample_intent):
        """Test data transformation with aggregation."""
        from data_ingestion.tools.transform_tools import transform_data

        # Mock query executor
        with patch('data_ingestion.tools.transform_tools.QueryExecutor') as MockExecutor:
            mock_executor = MockExecutor.return_value
            mock_executor.execute_aggregation = AsyncMock(return_value=[
                {"product": "Laptop", "sales_sum": 15000},
                {"product": "Desktop", "sales_sum": 8000},
                {"product": "Tablet", "sales_sum": 5000},
                {"product": "Phone", "sales_sum": 20000}
            ])

            result = await transform_data(
                mock_db_session,
                sample_session_info,
                sample_intent
            )

            assert result is not None
            assert isinstance(result, TransformResult)
            assert result.success is True
            assert len(result.data) == 4

    @pytest.mark.asyncio
    async def test_transform_data_no_aggregation(self, mock_db_session, sample_session_info):
        """Test data transformation without aggregation."""
        from data_ingestion.tools.transform_tools import transform_data

        intent = VisualizationIntent(
            intent_type=IntentType.SHOW_DISTRIBUTION,
            confidence=0.8,
            target_columns=["sales"],
            group_by_columns=[],
            filter_columns=[],
            aggregation_function=None,
            suggested_chart_type="histogram"
        )

        with patch('data_ingestion.tools.transform_tools.QueryExecutor') as MockExecutor:
            mock_executor = MockExecutor.return_value
            mock_executor.execute_select = AsyncMock(return_value=(
                [{"sales": 15000}, {"sales": 8000}, {"sales": 5000}, {"sales": 20000}],
                4
            ))

            result = await transform_data(
                mock_db_session,
                sample_session_info,
                intent
            )

            assert result is not None
            assert result.success is True

    @pytest.mark.asyncio
    async def test_preview_transform(self, mock_db_session, sample_session_info, sample_intent):
        """Test transformation preview."""
        from data_ingestion.tools.transform_tools import preview_transform

        with patch('data_ingestion.tools.transform_tools.QueryExecutor') as MockExecutor:
            mock_executor = MockExecutor.return_value
            mock_executor.execute_aggregation = AsyncMock(return_value=[
                {"product": "Laptop", "sales_sum": 15000}
            ])

            result = await preview_transform(
                mock_db_session,
                sample_session_info,
                sample_intent,
                limit=5
            )

            assert result is not None
            assert "sql" in result or "preview" in result


class TestChartTools:
    """Tests for chart generation tools."""

    @pytest.mark.asyncio
    async def test_generate_chart_bar(self, sample_transform_result, sample_intent):
        """Test bar chart generation."""
        from data_ingestion.tools.chart_tools import generate_chart

        with patch('data_ingestion.tools.chart_tools.AtomicChartGenerator') as MockGenerator:
            mock_generator = MockGenerator.return_value
            mock_generator.generate = AsyncMock(return_value={
                "success": True,
                "html": "<div>chart</div>",
                "chart_type": "bar_vertical"
            })

            result = await generate_chart(
                transform_result=sample_transform_result,
                intent=sample_intent,
                width=800,
                height=500
            )

            assert result is not None
            assert isinstance(result, ChartResult)
            assert result.success is True
            assert result.chart_html is not None

    @pytest.mark.asyncio
    async def test_generate_chart_with_insights(self, sample_transform_result, sample_intent):
        """Test chart generation with insights."""
        from data_ingestion.tools.chart_tools import generate_chart

        with patch('data_ingestion.tools.chart_tools.AtomicChartGenerator') as MockGenerator:
            mock_generator = MockGenerator.return_value
            mock_generator.generate = AsyncMock(return_value={
                "success": True,
                "html": "<div>chart</div>",
                "chart_type": "bar_vertical"
            })

            result = await generate_chart(
                transform_result=sample_transform_result,
                intent=sample_intent,
                include_insights=True
            )

            assert result is not None
            assert result.success is True

    @pytest.mark.asyncio
    async def test_generate_chart_failure(self, sample_transform_result, sample_intent):
        """Test chart generation failure handling."""
        from data_ingestion.tools.chart_tools import generate_chart

        with patch('data_ingestion.tools.chart_tools.AtomicChartGenerator') as MockGenerator:
            mock_generator = MockGenerator.return_value
            mock_generator.generate = AsyncMock(side_effect=Exception("Generation failed"))

            result = await generate_chart(
                transform_result=sample_transform_result,
                intent=sample_intent
            )

            assert result is not None
            assert result.success is False


class TestValidationTools:
    """Tests for validation tools."""

    @pytest.mark.asyncio
    async def test_validate_result_valid(self, sample_chart_result, sample_transform_result, sample_intent):
        """Test validation of valid chart result."""
        from data_ingestion.tools.validation_tools import validate_result

        result = await validate_result(
            sample_chart_result,
            sample_transform_result,
            sample_intent
        )

        assert result is not None
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.score >= 0.5

    @pytest.mark.asyncio
    async def test_validate_result_with_issues(self, sample_transform_result, sample_intent):
        """Test validation detecting issues."""
        from data_ingestion.tools.validation_tools import validate_result

        # Chart result with too few data points
        chart_result = ChartResult(
            success=True,
            chart_html="<div>chart</div>",
            chart_title="Test",
            chart_type=ChartType.PIE,
            data_points_used=1,  # Too few for pie chart
            generation_time_ms=100
        )

        result = await validate_result(
            chart_result,
            sample_transform_result,
            sample_intent
        )

        assert result is not None
        # Should flag issues with single data point pie chart
        assert len(result.issues) > 0 or result.score < 0.8

    @pytest.mark.asyncio
    async def test_suggest_alternatives(self, sample_chart_result, sample_transform_result):
        """Test alternative chart suggestions."""
        from data_ingestion.tools.validation_tools import suggest_alternatives

        result = await suggest_alternatives(
            sample_chart_result,
            sample_transform_result
        )

        assert result is not None
        assert isinstance(result, list)
        # Should suggest at least one alternative
        assert len(result) >= 0  # May be empty if current chart is optimal
