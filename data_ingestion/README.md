# Data Ingestion Agent (v3.8.0)

An intelligent data ingestion module for the Analytics Microservice that accepts user CSV data, uses chain-of-thought reasoning to analyze and visualize it, and generates charts using the existing atomic endpoints.

## Overview

The Data Ingestion Agent provides:
- **CSV Upload**: Accept and validate CSV files with automatic type inference
- **Chain-of-Thought Reasoning**: Intelligent analysis using a state machine workflow
- **Natural Language Processing**: Parse user narratives to understand visualization intent
- **Automatic Chart Generation**: Generate appropriate charts using existing `AtomicChartGenerator`
- **Full Audit Trail**: Track all reasoning steps for transparency and debugging

## Architecture

```
data_ingestion/
├── __init__.py                    # Module entry point
├── settings.py                    # Configuration settings
├── README.md                      # This file
│
├── agent/                         # Chain-of-thought reasoning
│   ├── __init__.py
│   ├── reasoning_engine.py        # State machine orchestrator
│   ├── tool_registry.py           # MCP-style tool registration
│   └── prompts.py                 # LLM prompt templates
│
├── tools/                         # 9 MCP-style tools
│   ├── __init__.py
│   ├── session_tools.py           # get_session_info
│   ├── analysis_tools.py          # analyze_data_structure, detect_patterns
│   ├── intent_tools.py            # parse_user_intent (OpenAI + rule-based)
│   ├── transform_tools.py         # transform_data, preview_transform
│   ├── chart_tools.py             # generate_chart (wraps AtomicChartGenerator)
│   └── validation_tools.py        # validate_result, suggest_alternatives
│
├── database/                      # PostgreSQL integration
│   ├── __init__.py
│   ├── connection.py              # Async connection pooling (SQLAlchemy)
│   ├── models.py                  # ORM models: data_sessions, reasoning_log
│   ├── session_store.py           # Session CRUD operations
│   └── query_executor.py          # Safe SQL execution with validation
│
├── models/                        # Pydantic models
│   ├── __init__.py
│   ├── requests.py                # UploadRequest, IngestRequest, PreviewRequest
│   ├── responses.py               # UploadResponse, IngestResponse, etc.
│   └── tools.py                   # SessionInfo, VisualizationIntent, etc.
│
└── upload/                        # CSV file handling
    ├── __init__.py
    ├── handler.py                 # CSV parsing, type inference
    └── validators.py              # Size, format, row count validation
```

## API Endpoints

All endpoints use the prefix `/api/v1/data/`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload CSV file, create session, store in PostgreSQL |
| `/ingest` | POST | Process data + narrative, return chart |
| `/sessions/{session_id}` | GET | Get session metadata and columns |
| `/sessions/{session_id}/preview` | POST | Preview transformation without committing |
| `/sessions/{session_id}/reasoning` | GET | Get full chain-of-thought audit trail |
| `/sessions/{session_id}` | DELETE | Delete session and data |
| `/sessions` | GET | List sessions for presentation |
| `/health` | GET | PostgreSQL connection health check |

## Configuration

### Environment Variables

```bash
# PostgreSQL Database (Railway)
DATA_INGESTION_DATABASE_URL=postgresql://user:pass@host:port/db

# Connection Pool Settings
DATA_INGESTION_DB_POOL_MIN_SIZE=5
DATA_INGESTION_DB_POOL_MAX_SIZE=20
DATA_INGESTION_DB_POOL_TIMEOUT=30

# Session Limits
DATA_INGESTION_SESSION_TTL_HOURS=1
DATA_INGESTION_MAX_FILE_SIZE_MB=10
DATA_INGESTION_MAX_ROWS_PER_SESSION=100000

# LLM Integration (optional, falls back to rule-based)
DATA_INGESTION_OPENAI_API_KEY=sk-...
DATA_INGESTION_LLM_MODEL=gpt-4o-mini
DATA_INGESTION_LLM_TIMEOUT=30

# Agent Settings
DATA_INGESTION_MAX_AGENT_STEPS=10
DATA_INGESTION_QUERY_TIMEOUT=30
DATA_INGESTION_MAX_QUERY_ROWS=10000
```

### Settings Class

```python
from data_ingestion.settings import get_data_ingestion_settings

settings = get_data_ingestion_settings()
print(settings.DATABASE_URL)
print(settings.MAX_FILE_SIZE_MB)
```

## Usage

### 1. Upload CSV Data

```bash
curl -X POST http://localhost:8080/api/v1/data/upload \
  -F "file=@sales_data.csv" \
  -F "presentation_id=pres-123"
```

Response:
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sales_data.csv",
  "row_count": 100,
  "column_count": 5,
  "columns": [
    {"name": "product", "type": "categorical", "unique_count": 4},
    {"name": "region", "type": "categorical", "unique_count": 3},
    {"name": "sales", "type": "numeric", "min": 1000, "max": 50000},
    {"name": "quarter", "type": "categorical", "unique_count": 4},
    {"name": "date", "type": "datetime"}
  ],
  "preview_rows": [...],
  "expires_at": "2024-01-15T15:00:00Z"
}
```

### 2. Generate Visualization

```bash
curl -X POST http://localhost:8080/api/v1/data/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "narrative": "Show me total sales by product as a bar chart",
    "include_insights": true
  }'
```

Response:
```json
{
  "success": true,
  "request_id": "req-abc123",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "chart": {
    "chart_html": "<div id='chart-xyz'>...</div><script>...</script>",
    "chart_title": "Total Sales by Product",
    "chart_type": "bar_vertical",
    "insights_html": "<div class='insights'>...</div>"
  },
  "data_summary": {
    "rows_used": 100,
    "columns_used": ["product", "sales"],
    "aggregation": "sum",
    "group_by": ["product"]
  },
  "reasoning_steps": [
    {
      "step_number": 1,
      "step_type": "get_session",
      "tool_name": "get_session_info",
      "reasoning": "Loaded session with 100 rows, 5 columns",
      "duration_ms": 25.5,
      "success": true
    },
    ...
  ],
  "total_duration_ms": 850.3
}
```

### 3. Preview Transformation

```bash
curl -X POST http://localhost:8080/api/v1/data/sessions/550e8400-e29b-41d4-a716-446655440000/preview \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Show average sales by region"
  }'
```

### 4. Get Reasoning Audit Trail

```bash
curl http://localhost:8080/api/v1/data/sessions/550e8400-e29b-41d4-a716-446655440000/reasoning
```

## Chain-of-Thought Reasoning

The agent uses a state machine with the following workflow:

```
INIT → GET_SESSION → PARSE_INTENT → TRANSFORM → GENERATE_CHART → VALIDATE → COMPLETE
                                                                              ↓
                                                                            ERROR
```

### Reasoning Steps

1. **GET_SESSION**: Load session metadata and column schema
2. **PARSE_INTENT**: Extract visualization intent from user narrative
3. **TRANSFORM**: Transform data based on intent (aggregation, grouping, filtering)
4. **GENERATE_CHART**: Generate chart using AtomicChartGenerator
5. **VALIDATE**: Quality checks on generated chart

### Intent Types

| Intent | Description | Example Narrative |
|--------|-------------|-------------------|
| `compare_values` | Category comparison | "Compare sales by product" |
| `show_trend` | Time series trend | "Show revenue over time" |
| `show_composition` | Parts of whole | "Breakdown of sales by region" |
| `show_distribution` | Value distribution | "Distribution of order values" |
| `show_correlation` | Relationship | "Correlation between price and sales" |
| `show_ranking` | Ranked items | "Top 10 products by revenue" |
| `aggregate_data` | Summary statistics | "Total sales per quarter" |

## MCP-Style Tools

The module implements 9 MCP-style tools:

| Tool | Purpose |
|------|---------|
| `get_session_info` | Retrieve session metadata and column schema |
| `analyze_data_structure` | Deep analysis: statistics, patterns, recommendations |
| `parse_user_intent` | NLP intent extraction (OpenAI + rule-based fallback) |
| `detect_patterns` | Trend, seasonality, correlation detection |
| `transform_data` | Execute SQL against session data |
| `preview_transform` | Preview transformation without full execution |
| `generate_chart` | Wrapper around AtomicChartGenerator |
| `validate_result` | Quality checks on generated chart |
| `suggest_alternatives` | Alternative visualization suggestions |

## Database Schema

### Tables

1. **data_sessions**: Session metadata
   - `id`: UUID primary key
   - `presentation_id`: Optional presentation association
   - `filename`: Original CSV filename
   - `row_count`, `column_count`: Data dimensions
   - `column_schema`: JSONB with column types and statistics
   - `table_name`: Dynamic data table name
   - `created_at`, `expires_at`: TTL management

2. **agent_reasoning_log**: Chain-of-thought audit trail
   - `id`: UUID primary key
   - `session_id`: Foreign key to data_sessions
   - `request_id`: Unique request identifier
   - `step_number`: Step sequence
   - `step_type`: Enum (get_session, parse_intent, transform, etc.)
   - `tool_name`: Tool invoked
   - `reasoning`: Human-readable reasoning
   - `duration_ms`: Step duration
   - `success`, `error_message`: Result

3. **transform_audit**: SQL transformation history
   - `id`: UUID primary key
   - `session_id`: Foreign key to data_sessions
   - `sql_executed`: SQL query
   - `rows_before`, `rows_after`: Row counts
   - `aggregation_applied`, `group_by_applied`: Transform details

## Error Handling

The module uses structured error codes:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `FILE_TOO_LARGE` | 400 | File exceeds size limit |
| `UNSUPPORTED_FILE_TYPE` | 400 | Non-CSV file uploaded |
| `INVALID_CSV_FORMAT` | 400 | Malformed CSV |
| `SESSION_NOT_FOUND` | 404 | Session doesn't exist |
| `SESSION_EXPIRED` | 410 | Session TTL exceeded |
| `AMBIGUOUS_INTENT` | 400 | Unable to parse narrative |
| `TRANSFORM_FAILED` | 500 | Data transformation error |
| `AGENT_MAX_STEPS_EXCEEDED` | 500 | Safety limit reached |
| `DATABASE_NOT_CONFIGURED` | 503 | PostgreSQL unavailable |

## Testing

```bash
# Run all data ingestion tests
pytest tests/data_ingestion/ -v

# Run specific test file
pytest tests/data_ingestion/test_upload.py -v

# Run with coverage
pytest tests/data_ingestion/ --cov=data_ingestion --cov-report=html
```

## Security Considerations

1. **SQL Injection Prevention**: All queries use parameterized statements
2. **Table Name Validation**: Dynamic tables must match pattern `data_[a-f0-9]{32}`
3. **File Size Limits**: Configurable max file size (default 10MB)
4. **Row Count Limits**: Configurable max rows (default 100,000)
5. **Session TTL**: Automatic cleanup of expired sessions
6. **Query Timeout**: Configurable timeout for database queries

## Dependencies

- `sqlalchemy[asyncio]>=2.0.0`: Async ORM
- `asyncpg>=0.29.0`: PostgreSQL async driver
- `pandas>=2.0.0`: CSV parsing and data manipulation
- `openai>=1.0.0`: Optional LLM integration for intent parsing
- `pydantic>=2.0.0`: Data validation

## Integration with Existing Atomic Endpoints

This module **does not modify** the existing atomic endpoints. It wraps `AtomicChartGenerator.generate()` internally:

```python
# In chart_tools.py
from core.atomic_chart_generator import AtomicChartGenerator

async def generate_chart(transform_result, intent, ...):
    generator = AtomicChartGenerator(theme="professional")
    # Adapt data format and call generator
    result = await generator.generate(...)
    return ChartResult(...)
```

## Version History

- **v3.8.0**: Initial release of Data Ingestion Agent
  - CSV upload with type inference
  - Chain-of-thought reasoning engine
  - 9 MCP-style tools
  - PostgreSQL session storage
  - Full audit trail support
