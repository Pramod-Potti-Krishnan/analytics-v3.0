# Analytics Microservice v3 - Integration Guide

Complete guide for integrating the Analytics Microservice v3 with the Director Agent and other services using the Text Service-compatible API pattern.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Director Agent Integration](#director-agent-integration)
- [Layout Builder Integration](#layout-builder-integration)
- [API Patterns](#api-patterns)
- [Chart Types & Layouts](#chart-types--layouts)
- [Error Handling](#error-handling)
- [Testing Integration](#testing-integration)
- [Performance Optimization](#performance-optimization)

---

## Overview

The Analytics Microservice v3 follows the **Text Service pattern** for seamless integration with the Director Agent and Layout Builder. It generates:

1. **Interactive ApexCharts** (HTML + JavaScript)
2. **AI-Generated Insights** (using GPT-4o-mini)
3. **Complete Slide Content** (title, subtitle, charts, insights)
4. **Reveal.js Integration** (automatic chart animation on slide appearance)

### Key Benefits

- ✅ **No Polling Required**: Synchronous responses (unlike legacy PNG generation)
- ✅ **Interactive Charts**: Users can hover, zoom, pan on charts
- ✅ **Animated Presentations**: Charts animate when slides appear
- ✅ **AI Insights**: Contextual business analysis included
- ✅ **Text Service Compatible**: Drop-in replacement for text content

---

## Architecture

### Service Communication Flow

```
┌─────────────────┐
│  Director Agent │ (Orchestrates presentation creation)
└────────┬────────┘
         │
         │ 1. Identifies analytics slide needed
         │
         ├────────────────────────────────────────┐
         │                                        │
         v                                        v
┌─────────────────────┐                  ┌──────────────────┐
│  Analytics Service  │                  │  Text Service    │
│  (v3 - NEW)         │                  │  (Rich Content)  │
└─────────┬───────────┘                  └──────────────────┘
          │
          │ 2. Generates:
          │    - ApexCharts HTML (element_4)
          │    - AI Insight (element_3)
          │    - Title/Subtitle (slide_title, element_1)
          │
          v
┌─────────────────────────────────────────────┐
│  Director Agent                              │
│  - Receives complete slide content          │
│  - Forwards to Layout Builder                │
└─────────────────────────────────────────────┘
          │
          v
┌─────────────────────────────────────────────┐
│  Layout Builder                              │
│  - Inserts chart HTML into layout           │
│  - Inserts insights into layout             │
│  - Generates final Reveal.js slide          │
└─────────────────────────────────────────────┘
```

### Format Ownership

Following the established pattern:

| Component | Owned By | Format |
|-----------|----------|--------|
| **Chart HTML** | Analytics Service | ApexCharts HTML + JS |
| **Insight Text** | Analytics Service | Plain text |
| **Slide Structure** | Layout Builder | Reveal.js HTML |
| **Title/Subtitle** | Analytics Service | Plain text |

---

## Director Agent Integration

### Step 1: Import Analytics Client

```python
# agents/director_agent/v3.3/src/agents/director.py

from typing import Dict, Any
import requests

class AnalyticsServiceClient:
    """Client for Analytics Microservice v3"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')

    def generate_analytics_slide(
        self,
        analytics_type: str,
        layout: str,
        presentation_id: str,
        slide_id: str,
        slide_number: int,
        narrative: str,
        data: list,
        context: dict,
        constraints: dict = None
    ) -> Dict[str, Any]:
        """
        Generate analytics slide content.

        Returns:
            {
                "content": {
                    "slide_title": str,
                    "element_1": str (subtitle),
                    "element_4": str (chart HTML),
                    "element_3": str (insight),
                    ...
                },
                "metadata": {...}
            }
        """
        url = f"{self.base_url}/api/v1/analytics/{layout}/{analytics_type}"

        payload = {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "slide_number": slide_number,
            "narrative": narrative,
            "data": data,
            "context": context,
            "constraints": constraints or {}
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        return response.json()
```

### Step 2: Detect Analytics Slides

```python
# In Director Agent's slide processing logic

def process_slide(self, slide_request: dict) -> dict:
    """Process a single slide request."""

    # Detect if this is an analytics slide
    if self._is_analytics_slide(slide_request):
        return self._generate_analytics_slide(slide_request)
    else:
        # Use Text Service for regular content
        return self._generate_text_slide(slide_request)

def _is_analytics_slide(self, slide_request: dict) -> bool:
    """Determine if slide needs analytics."""

    # Keywords that indicate analytics
    analytics_keywords = [
        "chart", "graph", "revenue", "sales", "metrics", "kpi",
        "quarterly", "monthly", "trend", "growth", "market share",
        "comparison", "year-over-year", "yoy", "performance"
    ]

    narrative = slide_request.get("narrative", "").lower()

    # Check for explicit data
    has_data = bool(slide_request.get("data"))

    # Check for analytics keywords
    has_analytics_keywords = any(
        keyword in narrative for keyword in analytics_keywords
    )

    return has_data or has_analytics_keywords
```

### Step 3: Generate Analytics Slide

```python
def _generate_analytics_slide(self, slide_request: dict) -> dict:
    """Generate analytics slide using Analytics Service."""

    # Extract or infer analytics type
    analytics_type = self._infer_analytics_type(slide_request)

    # Determine layout (default to L01 if not specified)
    layout = slide_request.get("layout", "L01")

    # Initialize analytics client
    analytics_client = AnalyticsServiceClient(
        base_url="http://localhost:8080"  # Or from settings
    )

    # Generate analytics content
    result = analytics_client.generate_analytics_slide(
        analytics_type=analytics_type,
        layout=layout,
        presentation_id=slide_request["presentation_id"],
        slide_id=slide_request["slide_id"],
        slide_number=slide_request["slide_number"],
        narrative=slide_request["narrative"],
        data=slide_request.get("data", []),
        context={
            "theme": slide_request.get("theme", "professional"),
            "audience": slide_request.get("audience", "executives"),
            "slide_title": slide_request.get("title", "Analytics"),
            "subtitle": slide_request.get("subtitle", ""),
            "presentation_name": slide_request.get("presentation_name", "")
        },
        constraints=slide_request.get("constraints", {})
    )

    return result

def _infer_analytics_type(self, slide_request: dict) -> str:
    """Infer analytics type from slide request."""

    narrative = slide_request.get("narrative", "").lower()

    # Simple keyword matching (can be enhanced with LLM)
    if "revenue" in narrative or "sales" in narrative:
        if "year" in narrative or "yoy" in narrative:
            return "yoy_growth"
        return "revenue_over_time"

    elif "market share" in narrative or "distribution" in narrative:
        return "market_share"

    elif "quarterly" in narrative or "compare" in narrative:
        return "quarterly_comparison"

    elif "kpi" in narrative or "metrics" in narrative:
        return "kpi_metrics"

    else:
        # Default fallback
        return "revenue_over_time"
```

### Step 4: Forward to Layout Builder

```python
def build_presentation(self, slides: list) -> dict:
    """Build complete presentation."""

    layout_builder_slides = []

    for slide_request in slides:
        # Get content (either from Analytics or Text Service)
        content_result = self.process_slide(slide_request)

        # Prepare for Layout Builder
        layout_builder_slide = {
            "slide_id": slide_request["slide_id"],
            "layout": slide_request.get("layout", "L01"),
            "content": content_result["content"],
            "metadata": content_result.get("metadata", {})
        }

        layout_builder_slides.append(layout_builder_slide)

    # Send to Layout Builder
    return self.layout_builder_client.build_slides(layout_builder_slides)
```

---

## Layout Builder Integration

The Layout Builder receives slide content from the Director Agent and inserts it into Reveal.js templates.

### Handling Chart HTML (element_4)

```html
<!-- In Layout Builder template (e.g., L01.html) -->

<section class="slide slide-l01">
    <!-- Title -->
    <div class="slide-title">
        {{ content.slide_title }}
    </div>

    <!-- Subtitle -->
    <div class="subtitle">
        {{ content.element_1 }}
    </div>

    <!-- Chart Area (ApexCharts HTML inserted here) -->
    <div class="chart-container">
        {{ content.element_4 | safe }}
        <!--
        This contains:
        - <div id="chart-abc123"></div>
        - <script src="apexcharts CDN"></script>
        - <script>chart initialization with Reveal.js integration</script>
        -->
    </div>

    <!-- Insight Text -->
    <div class="body-text">
        {{ content.element_3 }}
    </div>
</section>
```

### Critical: Use `| safe` Filter

**IMPORTANT**: The chart HTML from Analytics Service contains `<script>` tags that must be rendered as-is.

```python
# In Layout Builder (using Jinja2)

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
env.autoescape = True  # Enable autoescape for security

template = env.get_template('L01.html')

# Render with content
rendered = template.render(content=slide_content)

# The `| safe` filter in the template allows script tags
# {{ content.element_4 | safe }}
```

### L03 Side-by-Side Layout

```html
<!-- L03 template with two charts -->

<section class="slide slide-l03">
    <div class="slide-title">{{ content.slide_title }}</div>
    <div class="subtitle">{{ content.element_1 }}</div>

    <div class="comparison-container">
        <!-- Left Chart -->
        <div class="chart-panel left">
            <div class="chart-wrapper">
                {{ content.element_4 | safe }}
            </div>
            <div class="description">{{ content.element_3 }}</div>
        </div>

        <!-- Right Chart -->
        <div class="chart-panel right">
            <div class="chart-wrapper">
                {{ content.element_2 | safe }}
            </div>
            <div class="description">{{ content.element_5 }}</div>
        </div>
    </div>
</section>
```

---

## API Patterns

### Pattern 1: Single Analytics Slide

```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/analytics/L01/revenue_over_time",
    json={
        "presentation_id": "pres-001",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth",
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
            "subtitle": "FY 2024 Performance"
        }
    },
    timeout=30
)

result = response.json()

# Access content
chart_html = result["content"]["element_4"]
insight = result["content"]["element_3"]
```

### Pattern 2: Batch Analytics Generation

```python
response = requests.post(
    "http://localhost:8080/api/v1/analytics/batch",
    json={
        "presentation_id": "pres-001",
        "slides": [
            {
                "analytics_type": "revenue_over_time",
                "layout": "L01",
                "slide_id": "slide-5",
                "slide_number": 5,
                "narrative": "Revenue trends",
                "data": [...],
                "context": {...}
            },
            {
                "analytics_type": "market_share",
                "layout": "L01",
                "slide_id": "slide-6",
                "slide_number": 6,
                "narrative": "Market distribution",
                "data": [...],
                "context": {...}
            }
        ]
    },
    timeout=60
)

batch_result = response.json()

# Process results
for slide_result in batch_result["slides"]:
    if slide_result["success"]:
        print(f"Slide {slide_result['slide_id']}: Success")
    else:
        print(f"Slide {slide_result['slide_id']}: {slide_result['error']}")
```

### Pattern 3: Error Handling

```python
def safe_generate_analytics(
    analytics_type: str,
    layout: str,
    **kwargs
) -> dict:
    """Generate analytics with comprehensive error handling."""

    try:
        response = requests.post(
            f"http://localhost:8080/api/v1/analytics/{layout}/{analytics_type}",
            json=kwargs,
            timeout=30
        )

        if response.status_code == 400:
            # Validation error
            error_detail = response.json().get("detail", "Invalid request")
            return {
                "success": False,
                "error": f"Validation error: {error_detail}",
                "content": {},
                "metadata": {}
            }

        elif response.status_code == 500:
            # Server error
            return {
                "success": False,
                "error": "Analytics service internal error",
                "content": {},
                "metadata": {}
            }

        response.raise_for_status()
        result = response.json()

        return {
            "success": True,
            **result
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Analytics service timeout (>30s)",
            "content": {},
            "metadata": {}
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to analytics service",
            "content": {},
            "metadata": {}
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "content": {},
            "metadata": {}
        }
```

---

## Chart Types & Layouts

### Analytics Type Selection Matrix

| User Intent | Analytics Type | Default Layout | Chart Type |
|------------|---------------|----------------|------------|
| "Show revenue over time" | `revenue_over_time` | L01 | Line |
| "Compare quarters" | `quarterly_comparison` | L01 | Bar |
| "Market share breakdown" | `market_share` | L01 | Donut |
| "Year-over-year growth" | `yoy_growth` | L03 | Bar (dual) |
| "KPI dashboard" | `kpi_metrics` | L02 | Mixed |

### Layout Selection Rules

1. **L01 (Centered Chart + Insight)**
   - Single metric focus
   - Simple time series
   - Distribution analysis
   - Use when: One clear message to convey

2. **L02 (Chart + Explanation)**
   - Complex data
   - Statistical analysis
   - Multiple insights
   - Use when: Detailed explanation needed

3. **L03 (Side-by-Side Comparison)**
   - Before/after
   - A/B testing
   - Regional comparison
   - Use when: Two datasets to compare

---

## Error Handling

### Common Errors

#### 1. Invalid Analytics Type

```json
{
  "detail": "Invalid analytics type: unknown_type. Supported: ['revenue_over_time', 'quarterly_comparison', 'market_share', 'yoy_growth', 'kpi_metrics']"
}
```

**Solution**: Use one of the supported analytics types

#### 2. Missing Required Fields

```json
{
  "detail": [
    {
      "loc": ["body", "data"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution**: Ensure all required fields (presentation_id, slide_id, slide_number, narrative, data, context) are provided

#### 3. Service Timeout

Analytics generation takes 1-5 seconds typically. If timeout occurs:

```python
try:
    response = requests.post(url, json=payload, timeout=30)
except requests.exceptions.Timeout:
    # Fallback: Use text-only slide or retry
    pass
```

---

## Testing Integration

### Local Testing Setup

```bash
# Terminal 1: Start Analytics Service
cd agents/analytics_microservice_v3
source venv/bin/activate
python3 main.py

# Terminal 2: Run Integration Tests
python3 test_analytics_l01.py
python3 test_analytics_l03.py
```

### Integration Test Example

```python
# test_director_analytics_integration.py

import requests

def test_director_to_analytics_integration():
    """Test Director Agent → Analytics Service integration."""

    # Simulate Director Agent request
    director_request = {
        "presentation_id": "test-pres-001",
        "slides": [
            {
                "slide_id": "slide-7",
                "slide_number": 7,
                "layout": "L01",
                "narrative": "Show quarterly revenue growth",
                "data": [
                    {"label": "Q1", "value": 100},
                    {"label": "Q2", "value": 120},
                    {"label": "Q3", "value": 140},
                    {"label": "Q4", "value": 160}
                ],
                "context": {
                    "theme": "professional",
                    "slide_title": "Revenue Growth",
                    "subtitle": "Q1-Q4 2024"
                }
            }
        ]
    }

    # Director processes slide
    slide = director_request["slides"][0]

    # Call Analytics Service
    result = requests.post(
        "http://localhost:8080/api/v1/analytics/L01/revenue_over_time",
        json={
            "presentation_id": slide["presentation_id"],
            "slide_id": slide["slide_id"],
            "slide_number": slide["slide_number"],
            "narrative": slide["narrative"],
            "data": slide["data"],
            "context": slide["context"]
        },
        timeout=30
    ).json()

    # Validate response
    assert "content" in result
    assert "element_4" in result["content"]  # Chart HTML
    assert "element_3" in result["content"]  # Insight
    assert "ApexCharts" in result["content"]["element_4"]
    assert len(result["content"]["element_3"]) > 50  # Insight has content

    print("✅ Director → Analytics integration test passed")

if __name__ == "__main__":
    test_director_to_analytics_integration()
```

---

## Performance Optimization

### 1. Batch Processing

Generate multiple analytics slides in parallel:

```python
# Instead of sequential requests:
for slide in slides:
    result = generate_single_analytics(slide)  # Slow

# Use batch endpoint:
result = generate_batch_analytics(slides)  # Fast (parallel)
```

### 2. Caching Strategy

Cache insights for identical data:

```python
import hashlib
import json

def get_cache_key(data: list, narrative: str) -> str:
    """Generate cache key for analytics request."""
    cache_data = {
        "data": data,
        "narrative": narrative
    }
    return hashlib.md5(
        json.dumps(cache_data, sort_keys=True).encode()
    ).hexdigest()

# Check cache before calling service
cache_key = get_cache_key(data, narrative)
if cache_key in analytics_cache:
    return analytics_cache[cache_key]

# Generate and cache
result = analytics_client.generate_analytics_slide(...)
analytics_cache[cache_key] = result
```

### 3. Timeout Configuration

```python
# Different timeouts for different scenarios
timeouts = {
    "simple_chart": 10,  # Simple bar/line charts
    "complex_chart": 20,  # Heatmaps, complex visuals
    "batch": 60  # Batch processing
}

response = requests.post(
    url,
    json=payload,
    timeout=timeouts["simple_chart"]
)
```

### 4. Async Processing (Optional)

For non-blocking Director Agent:

```python
import asyncio
import aiohttp

async def generate_analytics_async(session, slide):
    """Generate analytics asynchronously."""
    async with session.post(
        f"{base_url}/api/v1/analytics/{slide['layout']}/{slide['analytics_type']}",
        json=slide
    ) as response:
        return await response.json()

async def process_all_slides(slides):
    """Process all slides concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_analytics_async(session, slide)
            for slide in slides
        ]
        return await asyncio.gather(*tasks)

# Usage in Director Agent
results = asyncio.run(process_all_slides(analytics_slides))
```

---

## Summary Checklist

Integration complete when:

- [ ] Analytics client implemented in Director Agent
- [ ] Analytics slide detection logic added
- [ ] Content routing (Analytics vs Text Service) working
- [ ] Layout Builder templates handle chart HTML correctly
- [ ] `| safe` filter applied to element_4 (chart HTML)
- [ ] Error handling implemented
- [ ] Integration tests passing
- [ ] Batch processing tested
- [ ] Performance acceptable (<5s per slide)
- [ ] Charts animate correctly in Reveal.js

---

## Support & Troubleshooting

### Common Issues

**Issue**: Charts not rendering
- **Solution**: Check that `| safe` filter is applied in Layout Builder template

**Issue**: Charts not animating
- **Solution**: Verify Reveal.js is initialized before charts load

**Issue**: Service timeout
- **Solution**: Check network connectivity, increase timeout, or use batch endpoint

**Issue**: Insights too generic
- **Solution**: Provide more detailed narrative and context in request

### Getting Help

- Check service logs: `tail -f /tmp/analytics_v3.log`
- Test with provided test files: `python3 test_analytics_l01.py`
- Verify service health: `curl http://localhost:8080/health`

---

**End of Integration Guide**
