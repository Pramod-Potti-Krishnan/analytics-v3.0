# Analytics Microservice v3

A REST API analytics microservice that generates comprehensive charts and visualizations, storing them in Supabase Storage and returning public URLs with underlying data.

## Features

- 🚀 **REST API** with async job processing and polling
- 📊 **20+ Chart Types** including bar, line, pie, scatter, heatmap, violin plots and more
- 🤖 **LLM-Enhanced Data Synthesis** using OpenAI GPT-4o-mini
- 🎨 **Theme Customization** with 5 pre-defined themes
- ☁️ **Supabase Storage** for chart hosting with public URLs
- 📈 **Job Progress Tracking** with optional polling endpoint
- 🔄 **Concurrent Job Processing** with automatic cleanup
- 🚂 **Railway Ready** for immediate deployment

## Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to the microservice
cd agents/analytics_microservice_v3

# Create virtual environment
cd agents/analytics_microservice_v3
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env and add your OpenAI API key and Supabase credentials
```

### 2. Run the Service

```bash
# Start the REST API server
python main.py
```

The service will start on `http://localhost:8080`

### 3. Test with REST Client

```python
import requests
import time

# Submit chart generation request
response = requests.post("http://localhost:8080/generate", json={
    "content": "Show quarterly revenue growth for 2024",
    "title": "Q1-Q4 2024 Revenue",
    "chart_type": "bar_vertical",
    "theme": "professional"
})

job_data = response.json()
job_id = job_data["job_id"]
print(f"Job created: {job_id}")

# Poll for results
while True:
    status_response = requests.get(f"http://localhost:8080/status/{job_id}")
    status = status_response.json()

    print(f"Status: {status['status']} - Progress: {status.get('progress', 0)}%")

    if status["status"] == "completed":
        print(f"Chart URL: {status['chart_url']}")
        print(f"Chart Data: {status['chart_data']}")
        break
    elif status["status"] == "failed":
        print(f"Error: {status.get('error')}")
        break

    time.sleep(1)
```

## REST API Endpoints

### POST /generate

Submit a chart generation request. Returns a job_id for polling.

**Request Body:**
```json
{
    "content": "Description of analytics needed",
    "title": "Chart Title (optional)",
    "data": [{"label": "Q1", "value": 100}],  // Optional user data
    "chart_type": "bar_vertical",  // Optional, defaults to bar_vertical
    "theme": "professional"  // Optional: default, dark, professional, colorful, minimal
}
```

**Response:**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing"
}
```

### GET /status/{job_id}

Poll for job status and results.

**Response (Processing):**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 60,
    "stage": "chart_rendering",
    "created_at": "2025-01-19T10:30:00",
    "updated_at": "2025-01-19T10:30:15"
}
```

**Response (Completed):**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "stage": "completed",
    "chart_url": "https://your-supabase-url.supabase.co/storage/v1/object/public/analytics-charts/chart_20250119_103020_abc123.png",
    "chart_data": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [25, 35, 30, 40],
        "title": "Q1-Q4 2024 Revenue"
    },
    "chart_type": "bar_vertical",
    "theme": "professional",
    "metadata": {
        "generated_at": "2025-01-19T10:30:20",
        "data_points": 4
    }
}
```

**Response (Failed):**
```json
{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "error": "Chart generation failed: Invalid chart type"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
    "status": "healthy",
    "service": "analytics_microservice_v3",
    "jobs": {
        "total_jobs": 10,
        "queued": 2,
        "processing": 3,
        "completed": 4,
        "failed": 1
    }
}
```

### GET /stats

Job statistics.

**Response:**
```json
{
    "job_stats": {
        "total_jobs": 10,
        "queued": 2,
        "processing": 3,
        "completed": 4,
        "failed": 1
    },
    "storage_bucket": "analytics-charts"
}
```

### GET /

Service information.

**Response:**
```json
{
    "service": "Analytics Microservice v3",
    "version": "3.0.0",
    "status": "running",
    "api_type": "REST",
    "endpoints": {
        "generate": "POST /generate",
        "status": "GET /status/{job_id}",
        "health": "GET /health",
        "stats": "GET /stats"
    }
}
```

## Available Chart Types

- `bar_vertical` - Vertical bar chart
- `bar_horizontal` - Horizontal bar chart
- `bar_grouped` - Grouped bar chart
- `bar_stacked` - Stacked bar chart
- `line` - Line chart
- `line_multi` - Multi-line chart
- `area` - Area chart
- `area_stacked` - Stacked area chart
- `pie` - Pie chart
- `donut` - Donut chart
- `scatter` - Scatter plot
- `bubble` - Bubble chart
- `heatmap` - Heatmap
- `radar` - Radar chart
- `box` - Box plot
- `violin` - Violin plot
- `histogram` - Histogram
- `funnel` - Funnel chart
- `treemap` - Treemap
- `sankey` - Sankey diagram

## Available Themes

- `default` - Clean blue theme
- `dark` - Dark mode with neon colors
- `professional` - Muted professional colors
- `colorful` - Bright, vibrant colors
- `minimal` - Grayscale minimalist

## Deployment

### Railway Deployment

1. Create a new Railway project
2. Add environment variables:
   ```
   OPENAI_API_KEY=your-key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-service-role-key
   SUPABASE_BUCKET=analytics-charts
   RAILWAY_ENVIRONMENT=production
   API_PORT=$PORT
   ```
3. Deploy using the Dockerfile (see below)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
```

### Railway Configuration (railway.json)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `SUPABASE_URL` | Supabase project URL (required) | - |
| `SUPABASE_KEY` | Supabase service role key (required) | - |
| `SUPABASE_BUCKET` | Supabase storage bucket name | analytics-charts |
| `API_PORT` | REST API server port | 8080 |
| `JOB_CLEANUP_HOURS` | Hours after which completed jobs are auto-cleaned | 1 |
| `CHART_GENERATION_TIMEOUT` | Timeout for chart generation (seconds) | 30 |
| `MAX_CHART_SIZE_MB` | Maximum chart size in MB | 10 |
| `RAILWAY_ENVIRONMENT` | Deployment environment | development |
| `LOG_LEVEL` | Logging level | INFO |

## Architecture

```
analytics_microservice_v3/
├── agent.py           # Chart generation logic with Supabase upload
├── dependencies.py    # Agent dependencies and job tracking
├── providers.py       # OpenAI provider configuration
├── settings.py        # Environment configuration
├── prompts.py        # System prompts
├── tools.py          # Agent tools (chart_generator, data_synthesizer, etc.)
├── rest_server.py    # FastAPI REST API server
├── job_manager.py    # Async job tracking and management
├── storage.py        # Supabase Storage integration
├── main.py           # Entry point
├── requirements.txt  # Python dependencies
├── .env.example      # Environment template
└── README.md         # This file
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .
```

## Troubleshooting

### Connection Issues
- Ensure the service is running on the correct port
- Check firewall settings
- Verify OPENAI_API_KEY is set correctly
- Verify Supabase credentials are correct

### Supabase Storage Issues
- Ensure SUPABASE_URL and SUPABASE_KEY are valid
- Check that the storage bucket exists or can be created
- Verify the service role key has storage permissions

### Chart Generation Errors
- Check the chart_type is supported
- Ensure data format matches expected structure
- Verify theme name is valid

### Performance
- Monitor active connections (max 100 by default)
- Check chart generation timeout settings
- Review logs for bottlenecks

## License

MIT

## Support

For issues or questions, please check the logs or create an issue in the repository.