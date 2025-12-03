# L02 Analytics Integration Guide

**Version**: 1.0
**Date**: 2025-11-16
**Status**: ✅ PRODUCTION READY

Integration guide for Director Agent team to call Analytics Microservice v3 for L02 analytics slides.

---

## Quick Start

**Endpoint**: `POST /api/v1/analytics/L02/{analytics_type}`
**Deployed URL**: `https://analytics-v30-production.up.railway.app`
**Response**: 2 HTML fields (`element_3` chart, `element_2` observations)

```python
# Director Agent calls Analytics Service
response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "pres-123",
        "slide_id": "slide-7",
        "narrative": "Show quarterly revenue growth",
        "data": [{"label": "Q1", "value": 125000}, ...],
        "context": {"theme": "professional", "audience": "Board"}
    }
)

# Map to L02 template
layout_builder_payload = {
    "layout": "L25",
    "layout_variant": "L02",
    "content": {
        "slide_title": "Revenue Growth",        # Director provides
        "element_1": "FY 2024",                  # Director provides
        "element_3": response["content"]["element_3"],  # Analytics provides (chart)
        "element_2": response["content"]["element_2"],  # Analytics provides (observations)
        "presentation_name": "Q4 Review"        # Director provides
    }
}
```

---

## Request Schema

### Endpoint Pattern
```
POST /api/v1/analytics/L02/{analytics_type}
```

### Analytics Types Supported
- `revenue_over_time` → Line chart
- `quarterly_comparison` → Bar chart
- `market_share` → Donut chart
- `yoy_growth` → Bar chart
- `kpi_metrics` → Bar chart

### Request Body
```json
{
  "presentation_id": "pres-uuid-123",
  "slide_id": "slide-7",
  "slide_number": 7,
  "narrative": "Show quarterly revenue growth with strong Q4 performance",
  "topics": ["revenue", "growth", "Q4"],
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 162000},
    {"label": "Q4 2024", "value": 195000}
  ],
  "context": {
    "theme": "professional",
    "audience": "Board of Directors",
    "slide_title": "Quarterly Revenue Growth",
    "subtitle": "FY 2024 Performance"
  },
  "options": {
    "enable_editor": true
  }
}
```

**Field Descriptions**:
- `presentation_id` (required): Unique presentation identifier for session tracking
- `slide_id` (required): Unique slide identifier for chart ID generation
- `slide_number` (optional): Slide position in deck
- `narrative` (required): User's description/intent for the analytics
- `topics` (optional): Keywords to help infer analytics type
- `data` (required): Array of `{label, value}` data points **provided by Director**
- `context.theme` (optional): `professional`, `corporate`, or `vibrant` (default: professional)
- `context.audience` (optional): Target audience for insights text (default: executives)
- `context.slide_title` (required): Title for the slide
- `context.subtitle` (optional): Subtitle for the slide
- `options.enable_editor` (optional): Include interactive edit button (default: false)

---

## Response Schema

### Success Response (200 OK)
```json
{
  "content": {
    "element_3": "<div class='l02-chart-container' style='width: 1260px; height: 720px;'>...<canvas>...</canvas>...</div>",
    "element_2": "<div class='l02-observations-panel' style='width: 540px; height: 720px;'>...<h3>Key Insights</h3><p>...</p>...</div>"
  },
  "metadata": {
    "analytics_type": "revenue_over_time",
    "chart_type": "line",
    "layout": "L02",
    "chart_library": "chartjs",
    "model_used": "gpt-4o-mini",
    "data_points": 4,
    "generation_time_ms": 3007,
    "theme": "professional",
    "generated_at": "2025-11-16T10:49:20.123Z",
    "interactive_editor": true
  }
}
```

**Response Fields**:
- `content.element_3`: Chart HTML (1260×720px container with Chart.js canvas)
- `content.element_2`: Observations HTML (540×720px panel with insights text, max ~500 chars)
- `metadata.analytics_type`: Type of analytics requested
- `metadata.chart_type`: Chart visualization type (line, bar_vertical, donut)
- `metadata.layout`: Always "L02" for this endpoint
- `metadata.generation_time_ms`: Processing time in milliseconds
- `metadata.interactive_editor`: Whether edit button is included

### Error Response (500)
```json
{
  "content": {
    "element_3": "<div style='padding: 40px; color: red;'>Error: [error message]</div>",
    "element_2": "<div style='padding: 40px;'>Unable to generate observations.</div>"
  },
  "metadata": {
    "layout": "L02",
    "error": "[error details]",
    "generated_at": "2025-11-16T10:49:20.123Z"
  }
}
```

---

## Director Agent Integration

### Step 1: Classify Slide as Analytics

```python
def should_use_analytics(slide: Slide) -> bool:
    """Determine if slide needs analytics visualization."""
    narrative_lower = slide.narrative.lower()

    analytics_keywords = [
        "chart", "graph", "revenue", "sales", "growth",
        "market", "share", "quarterly", "kpi", "metrics",
        "data", "statistics", "analytics", "visualization"
    ]

    return any(keyword in narrative_lower for keyword in analytics_keywords)
```

### Step 2: Prepare Analytics Request

```python
def prepare_analytics_request(slide: Slide, context: Dict) -> Dict:
    """Prepare request for Analytics Microservice."""

    # Infer analytics type from narrative
    analytics_type = infer_analytics_type(slide.narrative, slide.topics)

    # Extract or generate data
    data = extract_data_from_slide(slide) or generate_sample_data(slide.narrative)

    return {
        "presentation_id": context["presentation_id"],
        "slide_id": slide.slide_id,
        "slide_number": slide.slide_number,
        "narrative": slide.narrative,
        "topics": slide.topics,
        "data": data,  # Director provides data
        "context": {
            "theme": context.get("theme", "professional"),
            "audience": context.get("audience", "executives"),
            "slide_title": slide.title,
            "subtitle": slide.subtitle
        },
        "options": {
            "enable_editor": False  # Disable for production presentations
        }
    }
```

### Step 3: Call Analytics Service

```python
async def call_analytics_service(
    analytics_type: str,
    request_data: Dict
) -> Dict:
    """Call Analytics Microservice L02 endpoint."""

    analytics_url = "https://analytics-v30-production.up.railway.app"
    endpoint = f"{analytics_url}/api/v1/analytics/L02/{analytics_type}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, json=request_data)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Analytics service error: {response.status_code}")
                return create_fallback_content(request_data)

    except Exception as e:
        logger.error(f"Analytics service call failed: {e}")
        return create_fallback_content(request_data)
```

### Step 4: Map to L02 Template

```python
def map_to_l02_layout(
    slide: Slide,
    analytics_response: Dict,
    context: Dict
) -> Dict:
    """Map Analytics response to L02 template for Layout Builder."""

    return {
        "layout": "L25",
        "layout_variant": "L02",
        "content": {
            # Director provides
            "slide_title": slide.title,
            "element_1": slide.subtitle or "",

            # Analytics provides
            "element_3": analytics_response["content"]["element_3"],  # Chart HTML
            "element_2": analytics_response["content"]["element_2"],  # Observations HTML

            # Director provides
            "presentation_name": context.get("presentation_name", ""),
            "company_logo": context.get("company_logo", "")
        },
        "metadata": analytics_response.get("metadata", {})
    }
```

### Step 5: Send to Layout Builder

```python
async def send_to_layout_builder(slides: List[Dict]) -> str:
    """Send slides to Layout Builder."""

    layout_builder_url = "https://web-production-f0d13.up.railway.app"

    response = await httpx.post(
        f"{layout_builder_url}/api/presentations",
        json={"slides": slides}
    )

    return response.json()["id"]  # Presentation ID
```

---

## Complete Integration Example

```python
# Director Agent - Complete L02 Analytics Flow

async def generate_analytics_slide(
    slide: Slide,
    context: Dict
) -> Dict:
    """
    Generate L02 analytics slide via Analytics Microservice.

    Args:
        slide: Slide with narrative and data
        context: Presentation context (theme, audience, etc.)

    Returns:
        L02 slide content for Layout Builder
    """

    # 1. Determine analytics type
    analytics_type = infer_analytics_type(slide.narrative, slide.topics)
    # → "revenue_over_time", "market_share", etc.

    # 2. Prepare request
    analytics_request = {
        "presentation_id": context["presentation_id"],
        "slide_id": slide.slide_id,
        "slide_number": slide.slide_number,
        "narrative": slide.narrative,
        "topics": slide.topics,
        "data": slide.data,  # Director must provide data!
        "context": {
            "theme": context.get("theme", "professional"),
            "audience": context.get("audience"),
            "slide_title": slide.title,
            "subtitle": slide.subtitle
        },
        "options": {
            "enable_editor": False  # Production default
        }
    }

    # 3. Call Analytics Service
    analytics_response = await call_analytics_service(
        analytics_type=analytics_type,
        request_data=analytics_request
    )

    # 4. Map to L02 template
    l02_slide = {
        "layout": "L25",
        "layout_variant": "L02",
        "content": {
            "slide_title": slide.title,
            "element_1": slide.subtitle or "",
            "element_3": analytics_response["content"]["element_3"],  # Chart
            "element_2": analytics_response["content"]["element_2"],  # Observations
            "presentation_name": context.get("presentation_name", ""),
            "company_logo": context.get("company_logo", "")
        }
    }

    return l02_slide
```

---

## Data Requirements

### Director MUST Provide Data

Analytics Service does not generate synthetic data for production.
Director must provide data in request:

```python
"data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 162000},
    {"label": "Q4 2024", "value": 195000}
]
```

**Data Format**:
- Array of objects with `label` (string) and `value` (number)
- Minimum: 2 data points
- Maximum: 20 data points (for readability)
- Values auto-detected as currency, percentage, or number

---

## Chart Dimensions

**L02 Layout Content Area**: 1800×720px

**Split**:
- **element_3 (Chart)**: 1260×720px (70% width)
- **element_2 (Observations)**: 540×720px (30% width)

Charts are responsive and fill the container.

---

## Observations Text Limit

Observations text is limited to **~500 characters** (4-6 sentences).

If LLM generates more, it will be truncated with "..." appended.

---

## Interactive Editor

When `enable_editor: true`:
- Chart includes "📊 Edit Data" button
- Users can modify data in modal popup
- Changes persist to backend (PostgreSQL/Supabase)
- Chart updates in real-time

**Production Recommendation**: Set `enable_editor: false` for final presentations.

---

## Error Handling

### Analytics Service Unavailable

**Director should**:
1. Catch timeout/connection errors
2. Log error for monitoring
3. Return placeholder content in element_3 and element_2
4. Continue presentation generation

```python
def create_fallback_content(request_data: Dict) -> Dict:
    """Fallback content when Analytics Service unavailable."""

    return {
        "content": {
            "element_3": "<div style='padding: 40px; text-align: center;'>Chart unavailable. Analytics service is temporarily offline.</div>",
            "element_2": "<div style='padding: 40px;'>Unable to generate insights at this time.</div>"
        },
        "metadata": {
            "layout": "L02",
            "error": "Analytics service unavailable"
        }
    }
```

### Analytics Service Returns Error

If Analytics Service returns 500 error, it will still provide error content in `element_3` and `element_2` fields.

Director can:
- Use the error content as-is (displays error message to user)
- Replace with fallback content
- Skip the slide

---

## Testing

### Health Check
```bash
curl https://analytics-v30-production.up.railway.app/health
```

### Test L02 Endpoint
```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test-123",
    "slide_id": "slide-1",
    "narrative": "Show revenue growth",
    "data": [{"label": "Q1", "value": 100}, {"label": "Q2", "value": 150}],
    "context": {"theme": "professional", "slide_title": "Revenue"}
  }'
```

### Integration Test Suite
```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice_v3
python3 test_l02_director_integration.py
```

---

## Performance

**Expected Generation Time**: 2-5 seconds per slide

**Breakdown**:
- Chart generation: ~500ms (Chart.js)
- Observations generation: ~2000ms (GPT-4o-mini)
- HTML assembly: ~50ms
- Network latency: ~200-500ms

**Optimization**: Use batch endpoint (future) for parallel multi-slide generation.

---

## Production Checklist

- [ ] Analytics Service deployed on Railway (HTTPS)
- [ ] Director has Railway URL configured
- [ ] Health check returns 200 OK
- [ ] Test request/response successful
- [ ] Error handling implemented in Director
- [ ] Fallback content ready for service failures
- [ ] Interactive editor disabled for production (or enabled for demos)
- [ ] Monitoring/logging configured

---

## Support

**Analytics Service Status**: https://analytics-v30-production.up.railway.app/health
**Test Suite**: `test_l02_director_integration.py`
**Questions**: Contact Analytics team

---

## Changelog

**v1.0 (2025-11-16)**:
- ✅ Initial L02 integration
- ✅ Chart.js with interactive editor
- ✅ 500-char observations limit
- ✅ Session management for context
- ✅ Error handling with fallback content
- ✅ Production deployment on Railway

---

**Status**: ✅ PRODUCTION READY - Director team can begin integration
