# Analytics Microservice v3

A REST API analytics microservice that generates comprehensive charts and visualizations, storing them in Supabase Storage and returning public URLs with underlying data.

## 🌐 Production URL

**Live API**: `https://analytics-v30-production.up.railway.app`

Test it now:
```bash
curl https://analytics-v30-production.up.railway.app/health
```

## Features

- 🚀 **REST API** with async job processing and polling
- 📊 **20+ Chart Types** including bar, line, pie, scatter, heatmap, violin plots and more
- 🤖 **LLM-Enhanced Data Synthesis** using OpenAI GPT-4o-mini
- 🎨 **Theme Customization** with 5 pre-defined themes
- ☁️ **Supabase Storage** for chart hosting with public URLs
- 📈 **Job Progress Tracking** with optional polling endpoint
- 🔄 **Concurrent Job Processing** with automatic cleanup
- 🚂 **Railway Deployed** and production-ready

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

#### Using Production API

```python
import requests
import time

# Submit chart generation request to production
response = requests.post("https://analytics-v30-production.up.railway.app/generate", json={
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
    status_response = requests.get(f"https://analytics-v30-production.up.railway.app/status/{job_id}")
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

#### Using Local Development

```python
import requests
import time

# For local development, use localhost
BASE_URL = "http://localhost:8080"

response = requests.post(f"{BASE_URL}/generate", json={
    "content": "Show quarterly revenue growth for 2024",
    "title": "Q1-Q4 2024 Revenue",
    "chart_type": "bar_vertical",
    "theme": "professional"
})

job_data = response.json()
job_id = job_data["job_id"]

# Poll for completion
while True:
    status_response = requests.get(f"{BASE_URL}/status/{job_id}")
    status = status_response.json()

    if status["status"] == "completed":
        print(f"Chart URL: {status['chart_url']}")
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

## 🔌 Integration Guide for Other Services

This section shows how to integrate the Analytics Microservice v3 into your application.

### Base URLs

- **Production**: `https://analytics-v30-production.up.railway.app`
- **Local Development**: `http://localhost:8080`

### Integration Pattern

The microservice uses an async job pattern:
1. **Submit** chart generation request → Get `job_id`
2. **Poll** status endpoint until completion
3. **Retrieve** chart URL and data from completed job

### Python Integration

```python
import requests
import time
from typing import Dict, Any, Optional

class AnalyticsClient:
    """Client for Analytics Microservice v3"""

    def __init__(self, base_url: str = "https://analytics-v30-production.up.railway.app"):
        self.base_url = base_url.rstrip('/')

    def generate_chart(
        self,
        content: str,
        title: str = "Analytics Chart",
        chart_type: str = "bar_vertical",
        theme: str = "professional",
        data: Optional[list] = None,
        poll_interval: float = 1.0,
        max_wait: int = 60
    ) -> Dict[str, Any]:
        """
        Generate a chart and wait for completion.

        Args:
            content: Description of analytics needed
            title: Chart title
            chart_type: Type of chart (see docs for options)
            theme: Color theme (default, dark, professional, colorful, minimal)
            data: Optional user-provided data
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait for completion

        Returns:
            Dict with chart_url, chart_data, and metadata

        Raises:
            TimeoutError: If chart generation exceeds max_wait
            RuntimeError: If chart generation fails
        """
        # Submit request
        response = requests.post(f"{self.base_url}/generate", json={
            "content": content,
            "title": title,
            "chart_type": chart_type,
            "theme": theme,
            "data": data
        })
        response.raise_for_status()

        job_data = response.json()
        job_id = job_data["job_id"]

        # Poll for completion
        elapsed = 0
        while elapsed < max_wait:
            status_response = requests.get(f"{self.base_url}/status/{job_id}")
            status_response.raise_for_status()
            status = status_response.json()

            if status["status"] == "completed":
                return {
                    "chart_url": status["chart_url"],
                    "chart_data": status["chart_data"],
                    "chart_type": status["chart_type"],
                    "theme": status["theme"],
                    "metadata": status.get("metadata", {})
                }
            elif status["status"] == "failed":
                raise RuntimeError(f"Chart generation failed: {status.get('error')}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Chart generation timed out after {max_wait} seconds")

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """Get current status of a job."""
        response = requests.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    client = AnalyticsClient()

    # Generate a chart
    result = client.generate_chart(
        content="Show monthly sales data for 2024",
        title="2024 Sales Performance",
        chart_type="line",
        theme="professional"
    )

    print(f"Chart URL: {result['chart_url']}")
    print(f"Chart has {len(result['chart_data']['labels'])} data points")
```

### JavaScript/TypeScript Integration

```javascript
class AnalyticsClient {
    constructor(baseUrl = 'https://analytics-v30-production.up.railway.app') {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    async generateChart({
        content,
        title = 'Analytics Chart',
        chartType = 'bar_vertical',
        theme = 'professional',
        data = null,
        pollInterval = 1000,
        maxWait = 60000
    }) {
        // Submit request
        const response = await fetch(`${this.baseUrl}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content,
                title,
                chart_type: chartType,
                theme,
                data
            })
        });

        if (!response.ok) {
            throw new Error(`Failed to submit chart request: ${response.statusText}`);
        }

        const { job_id } = await response.json();

        // Poll for completion
        const startTime = Date.now();
        while (Date.now() - startTime < maxWait) {
            const statusResponse = await fetch(`${this.baseUrl}/status/${job_id}`);

            if (!statusResponse.ok) {
                throw new Error(`Failed to get job status: ${statusResponse.statusText}`);
            }

            const status = await statusResponse.json();

            if (status.status === 'completed') {
                return {
                    chartUrl: status.chart_url,
                    chartData: status.chart_data,
                    chartType: status.chart_type,
                    theme: status.theme,
                    metadata: status.metadata || {}
                };
            } else if (status.status === 'failed') {
                throw new Error(`Chart generation failed: ${status.error}`);
            }

            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }

        throw new Error(`Chart generation timed out after ${maxWait}ms`);
    }

    async getStatus(jobId) {
        const response = await fetch(`${this.baseUrl}/status/${jobId}`);
        if (!response.ok) {
            throw new Error(`Failed to get status: ${response.statusText}`);
        }
        return response.json();
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) {
            throw new Error(`Health check failed: ${response.statusText}`);
        }
        return response.json();
    }
}

// Example usage
const client = new AnalyticsClient();

client.generateChart({
    content: 'Show monthly sales data for 2024',
    title: '2024 Sales Performance',
    chartType: 'line',
    theme: 'professional'
})
.then(result => {
    console.log('Chart URL:', result.chartUrl);
    console.log('Data points:', result.chartData.labels.length);
})
.catch(error => {
    console.error('Chart generation failed:', error);
});
```

### cURL Examples

```bash
# Submit chart generation request
curl -X POST https://analytics-v30-production.up.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Show quarterly revenue for 2024",
    "title": "Q1-Q4 2024 Revenue",
    "chart_type": "bar_vertical",
    "theme": "professional"
  }'

# Response: {"job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "processing"}

# Check job status
curl https://analytics-v30-production.up.railway.app/status/550e8400-e29b-41d4-a716-446655440000

# Health check
curl https://analytics-v30-production.up.railway.app/health
```

### FastAPI/Flask Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

ANALYTICS_URL = "https://analytics-v30-production.up.railway.app"

class ChartRequest(BaseModel):
    content: str
    title: str = "Chart"
    chart_type: str = "bar_vertical"
    theme: str = "professional"

@app.post("/api/generate-chart")
async def generate_chart(request: ChartRequest):
    """Generate a chart using the analytics microservice."""
    try:
        # Submit to analytics service
        response = requests.post(
            f"{ANALYTICS_URL}/generate",
            json=request.dict()
        )
        response.raise_for_status()

        job_data = response.json()
        job_id = job_data["job_id"]

        # Return job_id for client-side polling
        # Or wait for completion server-side
        return {
            "job_id": job_id,
            "status_url": f"{ANALYTICS_URL}/status/{job_id}"
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chart-status/{job_id}")
async def get_chart_status(job_id: str):
    """Check status of a chart generation job."""
    try:
        response = requests.get(f"{ANALYTICS_URL}/status/{job_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### React Integration

```typescript
import { useState, useCallback } from 'react';

interface ChartResult {
    chartUrl: string;
    chartData: {
        labels: string[];
        values: number[];
        title: string;
    };
    chartType: string;
    theme: string;
}

const ANALYTICS_URL = 'https://analytics-v30-production.up.railway.app';

export function useAnalyticsChart() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ChartResult | null>(null);

    const generateChart = useCallback(async (
        content: string,
        title: string = 'Chart',
        chartType: string = 'bar_vertical',
        theme: string = 'professional'
    ) => {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Submit request
            const submitResponse = await fetch(`${ANALYTICS_URL}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content, title, chart_type: chartType, theme })
            });

            if (!submitResponse.ok) {
                throw new Error('Failed to submit chart request');
            }

            const { job_id } = await submitResponse.json();

            // Poll for completion
            while (true) {
                const statusResponse = await fetch(`${ANALYTICS_URL}/status/${job_id}`);

                if (!statusResponse.ok) {
                    throw new Error('Failed to get job status');
                }

                const status = await statusResponse.json();

                if (status.status === 'completed') {
                    setResult({
                        chartUrl: status.chart_url,
                        chartData: status.chart_data,
                        chartType: status.chart_type,
                        theme: status.theme
                    });
                    break;
                } else if (status.status === 'failed') {
                    throw new Error(status.error || 'Chart generation failed');
                }

                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    }, []);

    return { generateChart, loading, error, result };
}

// Example component usage
function ChartGenerator() {
    const { generateChart, loading, error, result } = useAnalyticsChart();

    const handleGenerate = () => {
        generateChart(
            'Show monthly sales for 2024',
            '2024 Sales Performance',
            'line',
            'professional'
        );
    };

    return (
        <div>
            <button onClick={handleGenerate} disabled={loading}>
                {loading ? 'Generating...' : 'Generate Chart'}
            </button>
            {error && <p>Error: {error}</p>}
            {result && <img src={result.chartUrl} alt={result.chartData.title} />}
        </div>
    );
}
```

### Error Handling Best Practices

```python
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def safe_generate_chart(content: str, **kwargs) -> dict:
    """
    Generate chart with comprehensive error handling.
    """
    base_url = "https://analytics-v30-production.up.railway.app"

    try:
        # Submit request with timeout
        response = requests.post(
            f"{base_url}/generate",
            json={"content": content, **kwargs},
            timeout=10
        )
        response.raise_for_status()
        job_id = response.json()["job_id"]

        # Poll with retries
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                status_response = requests.get(
                    f"{base_url}/status/{job_id}",
                    timeout=10
                )
                status_response.raise_for_status()
                status = status_response.json()

                if status["status"] == "completed":
                    return status
                elif status["status"] == "failed":
                    return {
                        "success": False,
                        "error": status.get("error", "Unknown error")
                    }

            except Timeout:
                print(f"Status check timeout (attempt {attempt + 1})")
                continue
            except HTTPError as e:
                if e.response.status_code == 404:
                    return {"success": False, "error": "Job not found"}
                raise

            time.sleep(1)

        return {"success": False, "error": "Timeout waiting for completion"}

    except Timeout:
        return {"success": False, "error": "Request timeout"}
    except HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

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