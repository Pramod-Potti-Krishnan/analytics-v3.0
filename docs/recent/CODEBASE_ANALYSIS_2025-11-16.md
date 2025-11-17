# Analytics Microservice v3 - Complete Codebase Analysis

**Analysis Date:** November 16, 2025
**Version:** 3.0.0
**Analysis Type:** Comprehensive Technical Review
**Analyst:** Claude Code

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Data Flow](#data-flow)
6. [Key Features](#key-features)
7. [Technology Stack](#technology-stack)
8. [Integration Patterns](#integration-patterns)
9. [Deployment Architecture](#deployment-architecture)
10. [Code Quality & Design Patterns](#code-quality--design-patterns)

---

## Executive Summary

The **Analytics Microservice v3** is a production-ready REST API service that generates interactive data visualizations and charts with AI-powered insights. It represents a significant evolution from earlier versions, transitioning from WebSocket-based communication to a more scalable REST API pattern with async job processing.

### Key Capabilities

- **20+ Chart Types**: Bar, line, pie, scatter, heatmap, violin plots, and more
- **Interactive Charts**: ApexCharts-based HTML with Reveal.js integration
- **AI-Powered Insights**: GPT-4o-mini generated business analysis
- **Cloud Storage**: Supabase Storage integration for public chart URLs
- **Job Management**: Async processing with polling-based status tracking
- **Theme Support**: 5 customizable visual themes
- **Multiple APIs**: Legacy PNG generation + new Text Service-compatible pattern

### Production Deployment

- **Live URL**: https://analytics-v30-production.up.railway.app
- **Platform**: Railway (Docker-based deployment)
- **Status**: Production-ready with comprehensive error handling

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Analytics Microservice v3                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  REST API    │      │   Job        │      │  ApexCharts  │  │
│  │  (FastAPI)   │─────▶│   Manager    │─────▶│  Generator   │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │          │
│         │                      │                      ▼          │
│         │                      │              ┌──────────────┐  │
│         │                      │              │  Insight     │  │
│         │                      │              │  Generator   │  │
│         │                      │              │  (GPT-4o)    │  │
│         │                      │              └──────────────┘  │
│         │                      │                      │          │
│         ▼                      ▼                      ▼          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Analytics Agent (Direct Mode)                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │  │
│  │  │   Data   │  │  Chart   │  │  Theme   │  │ Storage  │ │  │
│  │  │Synthesis │  │Generator │  │ Applier  │  │ Upload   │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  Supabase        │                         │
│                    │  Storage         │                         │
│                    │  (Public URLs)   │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   External       │
                    │   Clients        │
                    │  (Director,      │
                    │   Layout Builder)│
                    └──────────────────┘
```

### Component Interaction Flow

1. **Request Entry**: Client sends POST request to REST API
2. **Job Creation**: JobManager creates async job with unique ID
3. **Processing**: Analytics agent processes request directly (no Pydantic AI agent wrapper)
4. **Chart Generation**: ApexChartsGenerator creates interactive HTML
5. **Insight Generation**: InsightGenerator uses GPT-4o-mini for analysis
6. **Storage Upload**: Chart and data uploaded to Supabase Storage
7. **Job Completion**: Results stored in job manager with public URLs
8. **Client Polling**: Client polls `/status/{job_id}` for completion

---

## Core Components

### 1. REST Server (`rest_server.py`)

**Purpose**: FastAPI-based REST API server with async job processing

**Key Responsibilities**:
- Expose REST endpoints for chart generation
- Manage CORS and middleware
- Handle request validation with Pydantic models
- Route requests to job manager and analytics agent

**Main Endpoints**:
- `POST /generate` - Legacy PNG chart generation
- `POST /api/v1/analytics/{layout}/{analytics_type}` - Text Service pattern
- `POST /api/v1/analytics/batch` - Batch processing
- `GET /status/{job_id}` - Job status polling
- `GET /health` - Health check
- `GET /stats` - Service statistics

**Code Structure**:
```python
# Initialize FastAPI with metadata
app = FastAPI(
    title="Analytics Microservice v3",
    description="REST API for chart generation",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global managers
job_manager = JobManager(cleanup_hours=1)
storage = SupabaseStorage(url=..., key=..., bucket="analytics-charts")
```

---

### 2. Job Manager (`job_manager.py`)

**Purpose**: In-memory async job tracking and state management

**Key Features**:
- UUID-based job identification
- Job lifecycle management (QUEUED → PROCESSING → COMPLETED/FAILED)
- Progress tracking with percentage updates
- Automatic cleanup of old jobs (configurable hours)
- Thread-safe in-memory storage

**Job States**:
```python
class JobStatus(str, Enum):
    QUEUED = "queued"        # Initial state
    PROCESSING = "processing" # Active generation
    COMPLETED = "completed"   # Success with results
    FAILED = "failed"         # Error state
```

**Job Data Structure**:
```python
{
    "job_id": "uuid-string",
    "status": "completed",
    "progress": 100,
    "stage": "completed",
    "created_at": "ISO-8601 timestamp",
    "updated_at": "ISO-8601 timestamp",
    "chart_url": "https://supabase.co/...",
    "chart_data": {"labels": [...], "values": [...]},
    "metadata": {"generation_time_ms": 3007, ...}
}
```

**Key Methods**:
- `create_job(request_data)` - Initialize new job
- `update_progress(job_id, stage, progress)` - Update job state
- `complete_job(job_id, result)` - Mark as successful
- `fail_job(job_id, error)` - Mark as failed
- `get_stats()` - Return job statistics

---

### 3. Analytics Agent (`agent.py`)

**Purpose**: Direct chart processing without Pydantic AI agent wrapper

**Processing Pipeline**:

```
Input Request
    │
    ├─▶ Data Processing (10-25%)
    │   ├─ Use provided data OR
    │   └─ Synthesize with LLM
    │
    ├─▶ Theme Application (40%)
    │   └─ Apply color palette
    │
    ├─▶ Chart Generation (60%)
    │   ├─ ApexCharts HTML generation
    │   └─ Reveal.js integration
    │
    ├─▶ Insight Generation (70%)
    │   └─ GPT-4o-mini business analysis
    │
    ├─▶ Storage Upload (80%)
    │   └─ Supabase Storage
    │
    └─▶ Job Completion (100%)
        └─ Return URLs + data
```

**Key Functions**:
```python
async def process_analytics_direct(
    request_data: Dict[str, Any],
    deps: AnalyticsDependencies
) -> Dict[str, Any]:
    """Main processing function for analytics generation"""

async def process_analytics_l01(
    request_data: Dict[str, Any],
    deps: AnalyticsDependencies
) -> Dict[str, Any]:
    """L01 layout: Centered chart with insights"""

async def process_analytics_l03(
    request_data: Dict[str, Any],
    deps: AnalyticsDependencies
) -> Dict[str, Any]:
    """L03 layout: Side-by-side comparison"""
```

---

### 4. ApexCharts Generator (`apexcharts_generator.py`)

**Purpose**: Generate self-contained, interactive HTML charts

**Features**:
- **CDN Integration**: ApexCharts v3.45.0 from jsDelivr
- **Reveal.js Compatible**: Charts animate on slide appearance
- **Theme Support**: 5 color palettes (professional, dark, colorful, minimal, default)
- **Chart Types**: Line, Bar, Donut with full customization
- **Responsive Design**: Auto-adapts to container dimensions

**Generated HTML Structure**:
```html
<div id="chart-{uuid}" style="width: 100%; height: 600px;"></div>
<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>
<script>
(function() {
  const options = {
    chart: {
      type: "line",
      height: 600,
      animations: {
        enabled: true,
        easing: "easeinout",
        speed: 800
      }
    },
    series: [{
      name: "Revenue",
      data: [125000, 145000, 162000, 178000]
    }],
    xaxis: {
      categories: ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
    },
    colors: ["#003f5c", "#2f4b7c", "#665191"],
    // ... full configuration
  };

  const chart = new ApexCharts(
    document.querySelector('#chart-{uuid}'),
    options
  );

  // Reveal.js integration - animate on slide appearance
  if (typeof Reveal !== 'undefined') {
    Reveal.on('slidechanged', function(event) {
      const currentSlide = event.currentSlide;
      if (currentSlide && currentSlide.querySelector('#chart-{uuid}')) {
        if (!chart.rendered) {
          chart.render();
          chart.rendered = true;
        }
      }
    });
  } else {
    chart.render();
  }
})();
</script>
```

**Theme Color Palettes**:
```python
THEME_COLORS = {
    "professional": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087"],
    "dark": ["#00ff00", "#ff00ff", "#00ffff", "#ffff00", "#ff6600"],
    "colorful": ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"],
    "minimal": ["#333333", "#666666", "#999999", "#cccccc", "#e0e0e0"],
    "default": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
}
```

---

### 5. Insight Generator (`insight_generator.py`)

**Purpose**: AI-powered business insights using OpenAI GPT-4o-mini

**Insight Types**:

**L01 Insights** (Body Text):
- 2-3 sentences, max 150 words
- Key findings summary
- Notable trends
- Business implications

**L02 Explanations** (Detailed Analysis):
- 4-6 paragraphs, 250-400 words
- Statistical summary
- Detailed interpretation
- Strategic recommendations

**L03 Descriptions** (Comparison Captions):
- 1-2 sentences per chart
- Concise comparison points
- Paired left/right descriptions

**GPT-4o-mini Prompt Pattern** (L01 Example):
```python
prompt = f"""You are a business analyst generating insights for a presentation.

Chart Type: {chart_type}
Data Summary: {data_summary}
User Request: {narrative}
Audience: {audience}

Generate 2-3 concise sentences (max 150 words) that:
1. Summarize the key finding from the data
2. Identify the most notable trend or pattern
3. Provide business context or implication

Write in active voice, professional tone. No bullet points.
Use specific numbers from the data when relevant.

Example: "Revenue grew steadily throughout FY 2024, achieving
42% growth from Q1 to Q4..."
"""
```

**Error Handling**:
- Graceful fallback to template-based insights
- Timeout protection (max 200 tokens)
- Comprehensive logging

---

### 6. Storage Manager (`storage.py`)

**Purpose**: Supabase Storage integration for public chart hosting

**Features**:
- Automatic bucket creation with public access
- Unique filename generation (timestamp + UUID)
- Public URL retrieval
- Chart deletion and listing capabilities

**Upload Flow**:
```python
def upload_chart(
    self,
    image_bytes: bytes,
    chart_type: str = "chart",
    file_extension: str = "png"
) -> Optional[str]:
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_id = str(uuid.uuid4())[:8]
    filename = f"{chart_type}_{timestamp}_{chart_id}.{file_extension}"

    # Upload to Supabase Storage
    response = self.client.storage.from_(self.bucket_name).upload(
        path=filename,
        file=image_bytes,
        file_options={"content-type": f"image/{file_extension}"}
    )

    # Get public URL
    public_url = self.client.storage.from_(self.bucket_name).get_public_url(filename)

    return public_url
```

---

### 7. Analytics Types (`analytics_types.py`)

**Purpose**: Define supported analytics types and layout mappings

**Supported Types**:
```python
class AnalyticsType(str, Enum):
    REVENUE_OVER_TIME = "revenue_over_time"       # Line chart
    QUARTERLY_COMPARISON = "quarterly_comparison" # Bar chart
    MARKET_SHARE = "market_share"                 # Donut chart
    YOY_GROWTH = "yoy_growth"                     # Bar chart (dual)
    KPI_METRICS = "kpi_metrics"                   # Mixed charts
```

**Layout Mappings**:

| Analytics Type | Default Layout | Chart Type | Dimensions | Use Case |
|---------------|----------------|------------|------------|----------|
| revenue_over_time | L01 | Line | 1800×600 | Time series tracking |
| quarterly_comparison | L01 | Bar | 1800×600 | Periodic comparisons |
| market_share | L01 | Donut | 1800×600 | Distribution analysis |
| yoy_growth | L03 | Bar (dual) | 840×540 each | Year-over-year |
| kpi_metrics | L01 | Bar | 1800×600 | Key metrics |

**Layout Dimension Specifications**:
```python
LAYOUT_DIMENSIONS = {
    LayoutType.L01: {
        "chart_width": 1800,
        "chart_height": 600,
        "description": "Centered chart with body text below"
    },
    LayoutType.L02: {
        "chart_width": 1260,
        "chart_height": 720,
        "description": "Chart left (2/3) with explanation right (1/3)"
    },
    LayoutType.L03: {
        "chart_width": 840,
        "chart_height": 540,
        "description": "Two charts side-by-side for comparison"
    }
}
```

---

### 8. Dependencies (`dependencies.py`)

**Purpose**: Centralized dependency injection for analytics processing

**Dataclass Structure**:
```python
@dataclass
class AnalyticsDependencies:
    # Job Management
    job_manager: Optional[JobManager] = None
    job_id: Optional[str] = None

    # Storage
    storage: Optional[SupabaseStorage] = None

    # Tracking
    chart_request_id: Optional[str] = None
    generation_start_time: Optional[datetime] = None
    progress_callback: Optional[callable] = None

    # Configuration
    max_connections: int = 100
    generation_timeout: int = 30
    max_chart_size_mb: int = 10
    debug: bool = False
```

**Progress Update Method**:
```python
async def send_progress_update(
    self,
    stage: str,
    progress: int,
    message: str = ""
):
    """Send progress update via job manager"""
    if self.job_manager and self.job_id:
        self.job_manager.update_progress(self.job_id, stage, progress)
        logger.debug(f"Job {self.job_id}: {stage} - {progress}% - {message}")
```

---

## API Endpoints

### 1. Legacy PNG Generation

#### POST `/generate`

**Purpose**: Generate static PNG charts (backward compatibility)

**Request**:
```json
{
  "content": "Show quarterly revenue growth for 2024",
  "title": "Q1-Q4 2024 Revenue",
  "data": [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 150},
    {"label": "Q3", "value": 180},
    {"label": "Q4", "value": 210}
  ],
  "chart_type": "bar_vertical",
  "theme": "professional"
}
```

**Response**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

**Supported Chart Types**: 20+ types including bar, line, pie, scatter, heatmap, etc.

---

### 2. Text Service-Compatible API

#### POST `/api/v1/analytics/{layout}/{analytics_type}`

**Purpose**: Generate complete slide content with interactive charts + insights

**URL Parameters**:
- `layout`: L01 (centered), L02 (detailed), L03 (comparison)
- `analytics_type`: revenue_over_time, quarterly_comparison, market_share, yoy_growth, kpi_metrics

**Request Example (L01)**:
```json
{
  "presentation_id": "pres-123",
  "slide_id": "slide-7",
  "slide_number": 7,
  "narrative": "Show quarterly revenue growth highlighting Q3-Q4 performance",
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 162000},
    {"label": "Q4 2024", "value": 178000}
  ],
  "context": {
    "theme": "professional",
    "audience": "Board of Directors",
    "slide_title": "Quarterly Revenue Growth",
    "subtitle": "FY 2024 Performance",
    "presentation_name": "Board Review Q4 2024"
  },
  "constraints": {
    "max_data_points": 12,
    "chart_height": 600
  }
}
```

**Response (L01 Layout)**:
```json
{
  "content": {
    "slide_title": "Quarterly Revenue Growth",
    "element_1": "FY 2024 Performance",
    "element_4": "<div id=\"chart-058150c2\">...</div><script>...</script>",
    "element_3": "Revenue for FY 2024 demonstrated robust upward trajectory...",
    "presentation_name": "Board Review Q4 2024",
    "company_logo": "📊"
  },
  "metadata": {
    "analytics_type": "revenue_over_time",
    "layout": "L01",
    "chart_library": "apexcharts",
    "chart_type": "line",
    "model_used": "gpt-4o-mini",
    "data_points": 4,
    "generation_time_ms": 3007,
    "theme": "professional",
    "generated_at": "2025-11-14T06:30:24.598338"
  }
}
```

---

#### POST `/api/v1/analytics/batch`

**Purpose**: Generate multiple analytics slides in parallel

**Request**:
```json
{
  "presentation_id": "pres-123",
  "slides": [
    {
      "analytics_type": "revenue_over_time",
      "layout": "L01",
      "slide_id": "slide-5",
      "slide_number": 5,
      "narrative": "Show revenue growth",
      "data": [...],
      "context": {...}
    },
    {
      "analytics_type": "market_share",
      "layout": "L01",
      "slide_id": "slide-6",
      "slide_number": 6,
      "narrative": "Show market share distribution",
      "data": [...],
      "context": {...}
    }
  ]
}
```

**Response**:
```json
{
  "presentation_id": "pres-123",
  "slides": [
    {
      "success": true,
      "slide_id": "slide-5",
      "content": {...},
      "metadata": {...}
    },
    {
      "success": true,
      "slide_id": "slide-6",
      "content": {...},
      "metadata": {...}
    }
  ],
  "total": 2,
  "successful": 2
}
```

---

#### GET `/status/{job_id}`

**Purpose**: Poll job status and retrieve results

**Response (Processing)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 60,
  "stage": "chart_rendering",
  "created_at": "2025-11-16T10:30:00",
  "updated_at": "2025-11-16T10:30:15"
}
```

**Response (Completed)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "stage": "completed",
  "chart_url": "https://supabase.co/storage/v1/object/public/analytics-charts/chart_...",
  "chart_data": {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "values": [25, 35, 30, 40],
    "title": "Q1-Q4 2024 Revenue"
  },
  "chart_type": "bar_vertical",
  "theme": "professional",
  "metadata": {
    "generated_at": "2025-11-16T10:30:20",
    "data_points": 4
  }
}
```

---

#### GET `/health`

**Purpose**: Service health check with job statistics

**Response**:
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

---

## Data Flow

### End-to-End Processing Flow (Text Service API)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CLIENT REQUEST                                            │
│    POST /api/v1/analytics/L01/revenue_over_time             │
│    {                                                         │
│      "presentation_id": "pres-123",                         │
│      "narrative": "Show revenue growth",                    │
│      "data": [{"label": "Q1", "value": 100}, ...]          │
│    }                                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. REQUEST VALIDATION (FastAPI + Pydantic)                  │
│    - Validate analytics_type exists                         │
│    - Validate layout (L01/L02/L03)                          │
│    - Validate data format                                   │
│    - Validate context fields                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ANALYTICS AGENT PROCESSING                                │
│                                                              │
│    A. Data Preparation (0-20%)                              │
│       - Extract labels/values from request                  │
│       - Apply constraints (max_data_points)                 │
│       - Format for chart generation                         │
│                                                              │
│    B. Chart Generation (20-60%)                             │
│       - Determine chart type (revenue_over_time → line)     │
│       - Get layout dimensions (L01 → 1800x600)              │
│       - Call ApexChartsGenerator.generate_line_chart()      │
│       - Embed ApexCharts CDN + config                       │
│       - Add Reveal.js integration                           │
│                                                              │
│    C. Insight Generation (60-80%)                           │
│       - Call InsightGenerator.generate_l01_insight()        │
│       - Send data + narrative to GPT-4o-mini                │
│       - Receive 2-3 sentence business insight               │
│       - Format for presentation body text                   │
│                                                              │
│    D. Content Assembly (80-100%)                            │
│       - Assemble slide content dictionary                   │
│       - Map to layout elements                              │
│       - Add metadata (timing, chart type, etc.)             │
│       - Return complete slide content                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. RESPONSE FORMATTING                                       │
│    {                                                         │
│      "content": {                                            │
│        "slide_title": "Quarterly Revenue Growth",           │
│        "element_1": "FY 2024 Performance",                  │
│        "element_4": "<div id='chart-xxx'>...</div>",        │
│        "element_3": "Revenue for FY 2024..."                │
│      },                                                      │
│      "metadata": {                                           │
│        "analytics_type": "revenue_over_time",               │
│        "layout": "L01",                                      │
│        "generation_time_ms": 3007                           │
│      }                                                       │
│    }                                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CLIENT RECEIVES RESPONSE                                 │
│    - Extract chart HTML (element_4)                         │
│    - Extract insight text (element_3)                       │
│    - Pass to Layout Builder for slide assembly             │
│    - Render in Reveal.js presentation                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Dual API Pattern

**Legacy PNG API** (`/generate`):
- Static PNG chart generation
- Async job processing with polling
- Supabase Storage for hosting
- 20+ chart types via Matplotlib

**Text Service API** (`/api/v1/analytics`):
- Interactive ApexCharts HTML
- Synchronous response (no polling)
- AI-generated insights included
- Layout-aware content generation

### 2. Interactive Chart Features

**ApexCharts Integration**:
- Animations on slide appearance
- Interactive hover tooltips
- Zoom and pan capabilities
- Responsive design
- Reveal.js ready

### 3. AI-Powered Insights

**GPT-4o-mini Integration**:
- Context-aware analysis
- Audience-targeted tone
- Multi-format outputs (L01/L02/L03)
- Fallback handling

### 4. Layout Builder Integration

**Three Layout Types**:

**L01 - Centered Chart with Insights** (1800×600):
```
┌──────────────────────────────────┐
│  Title + Subtitle                │
│                                   │
│  ┌─────────────────────────────┐ │
│  │     Chart (1800×600)        │ │
│  └─────────────────────────────┘ │
│                                   │
│  Body text (2-3 sentence insight)│
└──────────────────────────────────┘
```

**L02 - Chart with Explanation** (1260×720 chart):
```
┌──────────────────────────────────┐
│  Title + Subtitle                │
│  ┌───────────┐  ┌──────────────┐ │
│  │   Chart   │  │  Detailed    │ │
│  │ (1260×720)│  │  Explanation │ │
│  └───────────┘  └──────────────┘ │
└──────────────────────────────────┘
```

**L03 - Side-by-Side Comparison** (840×540 each):
```
┌──────────────────────────────────┐
│  Title + Subtitle                │
│  ┌─────────┐  ┌─────────┐        │
│  │ Chart 1 │  │ Chart 2 │        │
│  │(840×540)│  │(840×540)│        │
│  └─────────┘  └─────────┘        │
│  Caption 1     Caption 2         │
└──────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **FastAPI** - Async REST API framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python 3.11** - Modern Python

### Chart Generation
- **ApexCharts 3.45.0** - Interactive charts
- **Matplotlib** - Legacy PNG generation
- **NumPy/Pandas** - Data processing

### AI/LLM
- **OpenAI GPT-4o-mini** - Business insights
- **Pydantic AI** - Agent framework

### Storage
- **Supabase Storage** - Chart hosting
- **In-Memory Store** - Job tracking

### Deployment
- **Railway** - PaaS hosting
- **Docker** - Containerization

---

## Integration Patterns

### Director Agent Integration

```python
# Director Agent calls Analytics Service
analytics_client = AnalyticsServiceClient(
    base_url="https://analytics-v30-production.up.railway.app"
)

result = analytics_client.generate_analytics_slide(
    analytics_type="revenue_over_time",
    layout="L01",
    presentation_id="pres-001",
    slide_id="slide-7",
    slide_number=7,
    narrative="Show quarterly revenue growth",
    data=[...],
    context={...}
)

# Extract content for Layout Builder
chart_html = result["content"]["element_4"]
insight = result["content"]["element_3"]
```

---

## Deployment Architecture

### Railway Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
```

**Environment Variables**:
```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
SUPABASE_BUCKET=analytics-charts
API_PORT=$PORT
RAILWAY_ENVIRONMENT=production
```

**Production URL**: https://analytics-v30-production.up.railway.app

---

## Code Quality & Design Patterns

### 1. Dependency Injection
- Clean separation of concerns
- Easy testing with mocked dependencies
- Flexible service swapping

### 2. Async/Await Pattern
- Non-blocking I/O operations
- Background job processing
- Efficient resource utilization

### 3. Pydantic Validation
- Automatic request validation
- Type safety throughout
- Clear error messages

### 4. Error Handling
- Layered exception handling
- Graceful degradation
- Comprehensive logging

### 5. Configuration Management
- Environment-based settings
- Type-safe configuration
- Validation on startup

---

## Summary

### Strengths

1. **Dual API Design** - Supports both legacy PNG and modern interactive charts
2. **Production-Ready** - Deployed on Railway with error handling
3. **AI Integration** - GPT-4o-mini generates contextual insights
4. **Interactive Charts** - ApexCharts with Reveal.js integration
5. **Clean Architecture** - Dependency injection, async processing
6. **Type Safety** - Pydantic validation throughout

### Areas for Improvement

1. **Job Persistence** - In-memory storage (jobs lost on restart)
   - **Solution**: Implement Redis or PostgreSQL

2. **Horizontal Scaling** - Single-instance limitation
   - **Solution**: Load balancer + multiple instances

3. **Monitoring** - Limited observability
   - **Solution**: Add Prometheus metrics, APM

4. **Caching** - No request caching
   - **Solution**: Redis caching layer

5. **Rate Limiting** - No abuse protection
   - **Solution**: Rate limiting middleware

6. **Testing** - Limited test coverage
   - **Solution**: Comprehensive test suite

### Recommended Next Steps

1. Add Redis for job storage (high priority)
2. Implement comprehensive test suite (high priority)
3. Add Prometheus metrics (medium priority)
4. Implement rate limiting (medium priority)
5. Add caching layer (low priority)
6. Horizontal scaling setup (future)

---

**End of Analysis**

*Generated: November 16, 2025*
*Maintainer: Analytics Microservice Team*
*Version: 3.0.0*
*Analyzed By: Claude Code*
