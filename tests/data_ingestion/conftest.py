"""
Test fixtures for Data Ingestion Agent tests.

Provides mock database sessions, sample CSV data, and test configurations.
"""

import io
import uuid
import pytest
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

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
from data_ingestion.models.responses import (
    UploadResponse,
    SessionMetadata,
    ReasoningStep
)
from data_ingestion.settings import get_data_ingestion_settings


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV file content for upload testing."""
    csv_data = """product,region,sales,quarter,date
Laptop,North,15000,Q1,2024-01-15
Laptop,South,12000,Q1,2024-01-20
Desktop,North,8000,Q1,2024-02-10
Desktop,South,9500,Q1,2024-02-15
Tablet,North,5000,Q2,2024-04-01
Tablet,South,6200,Q2,2024-04-10
Phone,North,20000,Q2,2024-05-05
Phone,South,18500,Q2,2024-05-12
Laptop,North,16500,Q3,2024-07-01
Desktop,East,7500,Q3,2024-07-15"""
    return csv_data.encode('utf-8')


@pytest.fixture
def sample_csv_file(sample_csv_content) -> io.BytesIO:
    """Sample CSV file as BytesIO for testing."""
    return io.BytesIO(sample_csv_content)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Sample pandas DataFrame for testing."""
    return pd.DataFrame({
        'product': ['Laptop', 'Desktop', 'Tablet', 'Phone'],
        'region': ['North', 'South', 'East', 'West'],
        'sales': [15000, 8000, 5000, 20000],
        'quarter': ['Q1', 'Q2', 'Q3', 'Q4']
    })


@pytest.fixture
def sample_column_schemas() -> list:
    """Sample column schemas for testing."""
    return [
        ColumnSchema(
            name="product",
            type=ColumnType.CATEGORICAL,
            nullable=False,
            unique_count=4,
            sample_values=["Laptop", "Desktop", "Tablet", "Phone"]
        ),
        ColumnSchema(
            name="region",
            type=ColumnType.CATEGORICAL,
            nullable=False,
            unique_count=4,
            sample_values=["North", "South", "East", "West"]
        ),
        ColumnSchema(
            name="sales",
            type=ColumnType.NUMERIC,
            nullable=False,
            min_value=5000.0,
            max_value=20000.0,
            mean_value=12000.0
        ),
        ColumnSchema(
            name="quarter",
            type=ColumnType.CATEGORICAL,
            nullable=False,
            unique_count=4,
            sample_values=["Q1", "Q2", "Q3", "Q4"]
        )
    ]


@pytest.fixture
def sample_session_info(sample_column_schemas) -> SessionInfo:
    """Sample session info for testing."""
    return SessionInfo(
        session_id=str(uuid.uuid4()),
        filename="test_data.csv",
        row_count=10,
        column_count=4,
        columns=sample_column_schemas,
        numeric_columns=["sales"],
        categorical_columns=["product", "region", "quarter"],
        datetime_columns=[],
        created_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc),
        table_name=f"data_{uuid.uuid4().hex}"
    )


@pytest.fixture
def sample_data_analysis() -> DataAnalysis:
    """Sample data analysis result for testing."""
    return DataAnalysis(
        total_rows=10,
        total_columns=4,
        numeric_summary={
            "sales": {
                "min": 5000,
                "max": 20000,
                "mean": 12000,
                "std": 5500
            }
        },
        categorical_summary={
            "product": {"unique": 4, "top": "Laptop", "freq": 3},
            "region": {"unique": 4, "top": "North", "freq": 4}
        },
        null_counts={"product": 0, "region": 0, "sales": 0, "quarter": 0},
        recommendations=[
            "Use 'sales' as the primary metric column",
            "Group by 'product' or 'region' for comparisons"
        ],
        detected_patterns=["categorical_comparison", "regional_data"]
    )


@pytest.fixture
def sample_intent() -> VisualizationIntent:
    """Sample visualization intent for testing."""
    return VisualizationIntent(
        intent_type=IntentType.COMPARE_VALUES,
        confidence=0.85,
        target_columns=["sales"],
        group_by_columns=["product"],
        filter_columns=[],
        aggregation_function="sum",
        filter_expression=None,
        suggested_chart_type="bar_vertical",
        chart_title_suggestion="Sales by Product"
    )


@pytest.fixture
def sample_transform_result(sample_dataframe) -> TransformResult:
    """Sample transform result for testing."""
    return TransformResult(
        success=True,
        data=[
            {"label": "Laptop", "value": 15000},
            {"label": "Desktop", "value": 8000},
            {"label": "Tablet", "value": 5000},
            {"label": "Phone", "value": 20000}
        ],
        rows_before=10,
        rows_after=4,
        aggregation_applied="sum",
        group_by_applied=["product"],
        sql_executed="SELECT product, SUM(sales) FROM data_xxx GROUP BY product",
        warnings=[]
    )


@pytest.fixture
def sample_chart_result() -> ChartResult:
    """Sample chart result for testing."""
    return ChartResult(
        success=True,
        chart_html="<div id='chart-123'>...</div><script>...</script>",
        chart_title="Sales by Product",
        chart_type=ChartType.BAR_VERTICAL,
        data_points_used=4,
        generation_time_ms=150.5,
        chart_id="chart-123",
        insights_html=None
    )


@pytest.fixture
def sample_validation_result() -> ValidationResult:
    """Sample validation result for testing."""
    return ValidationResult(
        valid=True,
        score=0.92,
        issues=[],
        suggestions=["Consider adding data labels for better readability"]
    )


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock async database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()

    # Mock scalar_one_or_none for queries
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
    session.execute.return_value = mock_result

    return session


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for intent parsing."""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_message.content = """{
        "intent_type": "compare_values",
        "confidence": 0.85,
        "target_columns": ["sales"],
        "group_by_columns": ["product"],
        "filter_columns": [],
        "aggregation_function": "sum",
        "filter_expression": null,
        "suggested_chart_type": "bar_vertical",
        "chart_title_suggestion": "Sales by Product"
    }"""
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.fixture
def data_ingestion_settings():
    """Get data ingestion settings for testing."""
    return get_data_ingestion_settings()


@pytest.fixture
def sample_reasoning_steps() -> list:
    """Sample reasoning steps for testing."""
    return [
        ReasoningStep(
            step_number=1,
            step_type="get_session",
            tool_name="get_session_info",
            reasoning="Loaded session with 10 rows, 4 columns",
            duration_ms=25.5,
            success=True,
            error_message=None
        ),
        ReasoningStep(
            step_number=2,
            step_type="parse_intent",
            tool_name="parse_user_intent",
            reasoning="Intent: compare_values (confidence: 0.85). Chart type: bar_vertical",
            duration_ms=350.2,
            success=True,
            error_message=None
        ),
        ReasoningStep(
            step_number=3,
            step_type="transform",
            tool_name="transform_data",
            reasoning="Transformed 10 rows -> 4 data points. Aggregation: sum",
            duration_ms=45.8,
            success=True,
            error_message=None
        ),
        ReasoningStep(
            step_number=4,
            step_type="generate_chart",
            tool_name="generate_chart",
            reasoning="Generated bar_vertical chart with 4 data points",
            duration_ms=150.5,
            success=True,
            error_message=None
        ),
        ReasoningStep(
            step_number=5,
            step_type="validate",
            tool_name="validate_result",
            reasoning="Validation score: 0.92. Valid: True",
            duration_ms=10.2,
            success=True,
            error_message=None
        )
    ]


@pytest.fixture
def sample_upload_response() -> UploadResponse:
    """Sample upload response for testing."""
    session_id = str(uuid.uuid4())
    return UploadResponse(
        success=True,
        session_id=session_id,
        filename="test_data.csv",
        row_count=10,
        column_count=4,
        columns=[
            {"name": "product", "type": "categorical"},
            {"name": "region", "type": "categorical"},
            {"name": "sales", "type": "numeric"},
            {"name": "quarter", "type": "categorical"}
        ],
        preview_rows=[
            {"product": "Laptop", "region": "North", "sales": 15000, "quarter": "Q1"}
        ],
        expires_at=datetime.now(timezone.utc).isoformat(),
        message="File uploaded successfully. 10 rows, 4 columns detected."
    )
