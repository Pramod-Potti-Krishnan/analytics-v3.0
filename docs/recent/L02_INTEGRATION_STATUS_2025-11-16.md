# L02 Layout Integration Status Report

**Date**: November 16, 2025
**Purpose**: Status of Analytics Service ↔ Director Agent ↔ Layout Builder integration for L02 layout template
**Created After**: IDE crash during integration work

---

## Executive Summary

The **Analytics Microservice v3** integration with **Director Agent** and **Layout Builder** for the **L02 layout template** was in active development when the IDE crashed. This integration follows the proven **Text Service pattern** to enable analytics slides in presentations.

### Integration Status: 🟡 **PARTIALLY COMPLETE**

- ✅ **Analytics Service Side**: COMPLETE and deployed to Railway
- 🟡 **Director Agent Side**: Implementation needed (design complete)
- ✅ **Layout Builder Side**: Ready (already handles Text Service pattern)
- ✅ **Testing**: Comprehensive test suite exists and passes

---

## What is L02 Integration?

### The Goal

Enable Director Agent to generate analytics slides using the L02 layout template, following the same pattern that Text Service uses for content generation.

### L02 Layout Structure

The L02 layout is a **split layout** with two distinct elements:

| Element | Purpose | Dimensions | Content Type |
|---------|---------|------------|--------------|
| **element_3** | Chart visualization | 1260×720px | Chart.js canvas HTML |
| **element_2** | Observations/Insights | 540×720px | Formatted text HTML |

### Integration Flow

```
Director Agent (Identifies analytics slide needed)
    ↓
    Calls Analytics Service: POST /api/v1/analytics/L02/{analytics_type}
    ↓
Analytics Service (Generates Chart.js + AI insights)
    ↓
    Returns: {content: {element_3: chart_html, element_2: observations_html}, metadata: {...}}
    ↓
Director Agent (Receives complete slide content)
    ↓
    Forwards to Layout Builder
    ↓
Layout Builder (Inserts HTML into L02 template)
    ↓
Final Reveal.js presentation with interactive chart
```

---

## What Has Been Completed ✅

### 1. Analytics Service Implementation (COMPLETE)

**Status**: ✅ Fully implemented, tested, and deployed to Railway

**Deployment URL**: `https://analytics-v30-production.up.railway.app`

**Endpoint**: `POST /api/v1/analytics/L02/{analytics_type}`

**Supported Analytics Types**:
- `revenue_over_time` → Line chart
- `market_share` → Donut chart
- `quarterly_comparison` → Bar chart
- `yoy_growth` → Bar chart (dual)
- `kpi_metrics` → Mixed chart

**Key Implementation Details**:

From `rest_server.py:247-324`:
```python
@app.post("/api/v1/analytics/{layout}/{analytics_type}")
async def generate_analytics_slide(layout: str, analytics_type: str, request: AnalyticsRequest):
    # L02 uses Chart.js-based generator
    if layout == "L02":
        from agent import generate_l02_analytics
        result = await generate_l02_analytics(request.dict())

        return {
            "content": result.get("content", {}),  # element_3, element_2
            "metadata": result.get("metadata", {})
        }
```

From `agent.py:432-638`:
```python
async def generate_l02_analytics(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate L02 analytics slide with Chart.js + observations.

    Returns 2 separate HTML fields:
    - element_3: Chart HTML (1260×720px Chart.js canvas)
    - element_2: Observations HTML (540×720px formatted text)
    """
    # 1. Extract request fields
    # 2. Infer analytics type from narrative/topics
    # 3. Generate Chart.js HTML
    # 4. Generate AI insights (max 500 chars for L02)
    # 5. Assemble L02 layout
    # 6. Update session context
    # 7. Return content + metadata
```

**Features**:
- ✅ Chart.js integration (not ApexCharts like L01/L03)
- ✅ Interactive chart editor support (optional)
- ✅ AI-generated insights using GPT-4o-mini
- ✅ Session context management (remembers prior slides)
- ✅ Theme support (professional, corporate, vibrant)
- ✅ Automatic analytics type inference from narrative
- ✅ Proper character limits (500 chars for observations)
- ✅ Text Service-compatible API response format

### 2. Comprehensive Testing (COMPLETE)

**Test Suite**: `tests/test_l02_director_integration.py` (288 lines)

**Tests Implemented**:
1. ✅ Revenue Over Time (line chart) - L02 layout
2. ✅ Market Share (donut chart) - L02 layout
3. ✅ Quarterly Comparison (bar chart) - L02 layout

**Test Coverage**:
- ✅ Request/response schema validation
- ✅ Content structure verification (element_3, element_2)
- ✅ Chart HTML validation (Canvas element, Chart ID)
- ✅ Observations character limit checking (≤1500 chars)
- ✅ Metadata completeness
- ✅ Production URL testing (Railway deployment)

**Sample Test Execution**:
```bash
$ python tests/test_l02_director_integration.py

================================================================================
TEST 1: L02 Revenue Over Time
================================================================================
📤 Sending request to: https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time
📥 Response status: 200
✅ SUCCESS - Response received
📊 Content Structure:
   - element_3 (chart): 8742 characters
   - element_2 (observations): 487 characters
```

### 3. Documentation (COMPLETE)

**Critical Integration Guides**:
1. ✅ `docs/L02_INTEGRATION.md` (512 lines) - Complete L02 integration specification
2. ✅ `docs/ANALYTICS_INTEGRATION_GUIDE.md` (812 lines) - General integration patterns
3. ✅ `docs/LAYOUT_SERVICE_INTEGRATION_GUIDE.md` (498 lines) - Layout Builder integration
4. ✅ `docs/INTERACTIVE_CHART_EDITOR_SPECIFICATION.md` - Interactive editor feature spec

**Documentation Includes**:
- ✅ Complete request/response schemas
- ✅ Director Agent integration code examples
- ✅ Error handling patterns
- ✅ Integration testing examples
- ✅ Deployment checklists

### 4. Supporting Infrastructure (COMPLETE)

**Components Implemented**:
- ✅ `chartjs_generator.py` - Chart.js HTML generation
- ✅ `layout_assembler.py` - L02 layout assembly
- ✅ `session_manager.py` - Session context management
- ✅ `insight_generator.py` - AI-powered insights
- ✅ `analytics_types.py` - Analytics type mappings
- ✅ Interactive chart editor API endpoints (rest_server.py:393-459)

---

## What Needs to Be Done 🟡

### 1. Director Agent Implementation (PRIMARY GAP)

**Status**: 🔴 Not started (design documented, code not written)

**Location**: `agents/director_agent/v3.4/` or `agents/director_agent/v3.3/`

**What Needs to Be Implemented**:

From the integration guide (`docs/ANALYTICS_INTEGRATION_GUIDE.md:96-251`), the Director Agent needs:

#### A. Analytics Service Client

```python
# agents/director_agent/v3.3/src/agents/director.py

from typing import Dict, Any
import requests

class AnalyticsServiceClient:
    """Client for Analytics Microservice v3"""

    def __init__(self, base_url: str = "https://analytics-v30-production.up.railway.app"):
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
        """Generate analytics slide content."""
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

#### B. Analytics Slide Detection Logic

```python
def _is_analytics_slide(self, slide_request: dict) -> bool:
    """Determine if slide needs analytics."""

    analytics_keywords = [
        "chart", "graph", "revenue", "sales", "metrics", "kpi",
        "quarterly", "monthly", "trend", "growth", "market share",
        "comparison", "year-over-year", "yoy", "performance"
    ]

    narrative = slide_request.get("narrative", "").lower()
    has_data = bool(slide_request.get("data"))
    has_analytics_keywords = any(keyword in narrative for keyword in analytics_keywords)

    return has_data or has_analytics_keywords
```

#### C. Analytics Type Inference

```python
def _infer_analytics_type(self, slide_request: dict) -> str:
    """Infer analytics type from slide request."""

    narrative = slide_request.get("narrative", "").lower()

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
        return "revenue_over_time"  # Default fallback
```

#### D. Content Routing (Analytics vs Text Service)

```python
def process_slide(self, slide_request: dict) -> dict:
    """Process a single slide request."""

    # Detect if this is an analytics slide
    if self._is_analytics_slide(slide_request):
        return self._generate_analytics_slide(slide_request)
    else:
        # Use Text Service for regular content
        return self._generate_text_slide(slide_request)

def _generate_analytics_slide(self, slide_request: dict) -> dict:
    """Generate analytics slide using Analytics Service."""

    analytics_type = self._infer_analytics_type(slide_request)
    layout = slide_request.get("layout", "L01")

    analytics_client = AnalyticsServiceClient(
        base_url="https://analytics-v30-production.up.railway.app"
    )

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
```

#### E. Integration with Stage 6 Workflow

The Director Agent has a 6-stage workflow. Analytics integration happens at **Stage 6: CONTENT_GENERATION**.

```python
# In Stage 6: CONTENT_GENERATION
async def generate_presentation_content(self, slides: list) -> dict:
    """Generate content for all slides."""

    layout_builder_slides = []

    for slide_request in slides:
        # Route to appropriate service
        content_result = self.process_slide(slide_request)  # Analytics OR Text Service

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

**Implementation Checklist for Director Agent**:
- [ ] Create `AnalyticsServiceClient` class
- [ ] Implement `_is_analytics_slide()` detection logic
- [ ] Implement `_infer_analytics_type()` mapping function
- [ ] Implement `_generate_analytics_slide()` generation method
- [ ] Integrate analytics routing into `process_slide()` method
- [ ] Add analytics service URL to Director Agent settings
- [ ] Implement error handling for Analytics Service failures
- [ ] Add fallback to Text Service if Analytics fails
- [ ] Test with L02 layout variant

### 2. Configuration Updates

**Director Agent Settings** (`agents/director_agent/v3.3/config/settings.py` or v3.4):

```python
# Add to settings
ANALYTICS_SERVICE_URL = os.getenv(
    "ANALYTICS_SERVICE_URL",
    "https://analytics-v30-production.up.railway.app"
)
ANALYTICS_TIMEOUT = int(os.getenv("ANALYTICS_TIMEOUT", "30"))  # seconds
```

**Environment Variables** (`.env.example`):

```bash
# Analytics Service Integration
ANALYTICS_SERVICE_URL=https://analytics-v30-production.up.railway.app
ANALYTICS_TIMEOUT=30
```

### 3. Integration Testing

**Test Scenario to Execute**:

```python
# Test Director → Analytics → Layout Builder flow
def test_director_l02_integration():
    """Test complete Director Agent integration with L02 layout."""

    # 1. Send request to Director Agent
    director_request = {
        "presentation_id": "test-dir-001",
        "presentation_name": "Q4 Board Review",
        "theme": "professional",
        "audience": "Board of Directors",
        "slides": [
            {
                "slide_id": "slide-1",
                "slide_number": 1,
                "layout": "L02",
                "narrative": "Show quarterly revenue growth highlighting strong Q3-Q4 performance",
                "title": "Revenue Growth",
                "subtitle": "FY 2024",
                "data": [
                    {"label": "Q1 2024", "value": 125000},
                    {"label": "Q2 2024", "value": 145000},
                    {"label": "Q3 2024", "value": 162000},
                    {"label": "Q4 2024", "value": 195000}
                ]
            }
        ]
    }

    # 2. Director should:
    #    - Detect analytics slide (has "revenue", "growth", "quarterly" + data)
    #    - Infer analytics_type = "revenue_over_time"
    #    - Call Analytics Service with L02 layout
    #    - Receive element_3 (chart) + element_2 (observations)
    #    - Forward to Layout Builder

    # 3. Verify final presentation has:
    #    - Chart.js canvas in element_3 position
    #    - Observations text in element_2 position
    #    - Interactive chart that animates on slide appearance

    # 4. Check metadata includes:
    #    - analytics_type: "revenue_over_time"
    #    - chart_type: "line"
    #    - layout: "L02"
    #    - chart_library: "chartjs"
```

---

## Potential Challenges Encountered 🚨

Based on the comprehensive documentation and implementation, these are the likely challenges that may have been encountered before the IDE crash:

### 1. **Data Requirement Challenge**

**Issue**: The Analytics Service requires Director Agent to provide actual data, not just a narrative.

**Evidence**: Multiple warnings in documentation:
- L02_INTEGRATION.md: "CRITICAL: Director must provide data array"
- ANALYTICS_INTEGRATION_GUIDE.md: "has_data = bool(slide_request.get('data'))"

**Impact**: If Director doesn't have data, it must either:
- Generate synthetic data (not ideal for real presentations)
- Use a data synthesis agent (complexity)
- Fail gracefully and fall back to Text Service

**Potential Solution Being Explored**:
```python
# In Director Agent
if self._is_analytics_slide(slide_request) and not slide_request.get("data"):
    # Option 1: Request data from user
    # Option 2: Generate synthetic data
    # Option 3: Fall back to Text Service for text-only slide
    logger.warning(f"Analytics slide requested but no data provided for {slide_id}")
```

### 2. **Analytics Type Inference Accuracy**

**Issue**: Correctly mapping narrative text to the appropriate analytics type is complex.

**Current Implementation**: Simple keyword matching (`agent.py:641-680`)

**Limitations**:
- May misclassify ambiguous narratives
- Doesn't handle edge cases well
- No machine learning or LLM-based classification

**Potential Enhancement Being Considered**:
```python
# Use LLM to infer analytics type
async def _infer_analytics_type_with_llm(self, narrative: str, data: list) -> str:
    """Use GPT to classify analytics type."""
    prompt = f"""
    Given this slide narrative and data structure, what analytics type is most appropriate?

    Narrative: {narrative}
    Data points: {len(data)}
    Data labels: {[d['label'] for d in data[:3]]}

    Choose from: revenue_over_time, market_share, quarterly_comparison, yoy_growth, kpi_metrics
    """
    # Call GPT-4o-mini for classification
```

### 3. **Layout Builder Template Compatibility**

**Issue**: Ensuring Layout Builder's L02 template correctly handles the Chart.js HTML.

**Requirements**:
- Must use `| safe` filter in Jinja2 template to render script tags
- Must preserve Chart.js canvas element structure
- Must include Chart.js CDN and datalabels plugin
- Must handle Reveal.js integration for chart animation

**Layout Builder Template Requirements** (from docs):
```html
<!-- L02 template must have: -->
<section class="slide-l02">
    <div class="chart-section">
        {{ content.element_3 | safe }}  <!-- CRITICAL: | safe filter -->
    </div>
    <div class="observations-section">
        {{ content.element_2 | safe }}
    </div>
</section>
```

**Challenge**: If Layout Builder's template doesn't use `| safe`, the Chart.js HTML will be escaped and won't render.

### 4. **Character Limit Enforcement**

**Issue**: L02 observations should be concise (500 chars recommended), but ensuring AI respects this limit is challenging.

**Current Implementation** (`agent.py:570-573`):
```python
"max_chars": 500  # L02 requirement
```

**Potential Issue**: GPT-4o-mini may exceed limit, requiring truncation or regeneration.

**Test Evidence**: `test_l02_director_integration.py:94` checks `len(element_2) <= 1500` (loose limit)

### 5. **Interactive Editor Integration**

**Issue**: Passing `enable_editor` parameter through the entire chain.

**Flow**:
```
User → Director (enable_editor?) → Analytics (enable_editor param) → Chart HTML (with/without editor)
```

**Challenge**: Decision point - when should the editor be enabled?
- Always?
- Only for specific users?
- Only in "edit mode"?
- Only for certain layouts?

**From docs** (LAYOUT_SERVICE_INTEGRATION_GUIDE.md:389-414):
```python
# Option 1: Enable for all
enable_editor = True

# Option 2: Enable only for authorized users
enable_editor = user_permissions.get('can_edit_charts', False)

# Option 3: Enable only in edit mode
enable_editor = (presentation_mode == 'edit')
```

### 6. **Error Handling and Fallback**

**Issue**: What happens when Analytics Service fails?

**Scenarios**:
- Analytics Service down
- Request timeout (>30s)
- Invalid analytics type
- Missing required data
- Chart generation fails

**Potential Solution** (from docs):
```python
def safe_generate_analytics(analytics_type, layout, **kwargs):
    """Generate analytics with fallback."""
    try:
        result = analytics_service.generate(...)
        return result
    except requests.exceptions.Timeout:
        # Fallback to Text Service
        return text_service.generate_text_slide(...)
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        # Fallback to simple text slide
        return create_error_slide(...)
```

### 7. **Session Context Management**

**Issue**: Analytics Service now maintains session context (prior slides) for coherent narratives.

**Feature** (`agent.py:514-517`):
```python
session_mgr = get_session_manager()
prior_slides = session_mgr.get_prior_slides(presentation_id, limit=3)
```

**Challenge**:
- How does Director populate session context?
- When should context be cleared?
- How to handle multi-user scenarios?

---

## Next Steps 🎯

### Immediate Actions (High Priority)

1. **Implement Director Agent Integration** (Est: 4-6 hours)
   - [ ] Create `AnalyticsServiceClient` class
   - [ ] Add analytics slide detection logic
   - [ ] Implement analytics type inference
   - [ ] Integrate into Stage 6 workflow
   - [ ] Add error handling and fallback logic

2. **Test Director Integration Locally** (Est: 2 hours)
   - [ ] Start Director Agent locally
   - [ ] Start Analytics Service locally (or use Railway)
   - [ ] Send test presentation request with analytics slide
   - [ ] Verify Director correctly calls Analytics Service
   - [ ] Verify Director correctly forwards to Layout Builder
   - [ ] Check final presentation renders correctly

3. **Verify Layout Builder Compatibility** (Est: 1 hour)
   - [ ] Check if L02 template exists in Layout Builder
   - [ ] Verify `| safe` filter is applied to element_3 and element_2
   - [ ] Test Chart.js rendering in Layout Builder
   - [ ] Verify Reveal.js integration works

### Secondary Actions (Medium Priority)

4. **Enhanced Analytics Type Inference** (Est: 2 hours)
   - [ ] Implement LLM-based analytics type classification
   - [ ] Add support for hybrid analytics types
   - [ ] Improve edge case handling

5. **Interactive Editor Decision Logic** (Est: 1 hour)
   - [ ] Decide on editor enablement strategy
   - [ ] Implement user permission checks (if needed)
   - [ ] Add mode-based editor toggling (if needed)

6. **Comprehensive Integration Testing** (Est: 3 hours)
   - [ ] Test all 5 analytics types with L02 layout
   - [ ] Test error scenarios (service down, timeout, invalid data)
   - [ ] Test fallback to Text Service
   - [ ] Test session context management
   - [ ] Performance testing (generation time <5s per slide)

### Documentation Updates (Low Priority)

7. **Update Director Agent Documentation** (Est: 1 hour)
   - [ ] Document Analytics Service integration
   - [ ] Add configuration examples
   - [ ] Update API reference

---

## Technical Specifications Reference

### L02 Request Schema

```json
{
  "presentation_id": "uuid",
  "slide_id": "slide-X",
  "slide_number": 7,
  "narrative": "Show quarterly revenue growth",
  "topics": ["revenue", "growth", "quarterly"],
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000}
  ],
  "context": {
    "theme": "professional",
    "audience": "Board of Directors",
    "slide_title": "Revenue Growth",
    "subtitle": "FY 2024"
  },
  "options": {
    "enable_editor": true
  }
}
```

### L02 Response Schema

```json
{
  "content": {
    "element_3": "<div><canvas id='chart-slide-X'></canvas><script>...</script></div>",
    "element_2": "<div style='padding:20px'>Q4 showed exceptional growth of 24% YoY...</div>"
  },
  "metadata": {
    "analytics_type": "revenue_over_time",
    "chart_type": "line",
    "layout": "L02",
    "chart_library": "chartjs",
    "data_points": 4,
    "generation_time_ms": 1234,
    "theme": "professional",
    "interactive_editor": true
  }
}
```

### Analytics Type → Chart Type Mappings

| Analytics Type | Chart Type | Best For |
|----------------|------------|----------|
| `revenue_over_time` | Line | Time series trends |
| `market_share` | Donut | Category distribution |
| `quarterly_comparison` | Bar (vertical) | Period-over-period comparison |
| `yoy_growth` | Bar (horizontal) | Year-over-year metrics |
| `kpi_metrics` | Mixed | Dashboard-style KPIs |

### Layout Dimensions

| Layout | Chart Width | Chart Height | Observations Width | Observations Height |
|--------|-------------|--------------|-------------------|-------------------|
| L01 | 1800px | 600px | N/A | N/A |
| L02 | 1260px | 720px | 540px | 720px |
| L03 | 840px | 540px | 840px | 540px |

---

## Key Files for Implementation

### Analytics Service (Already Complete)
- ✅ `rest_server.py:247-324` - L02 endpoint implementation
- ✅ `agent.py:432-638` - L02 analytics generation logic
- ✅ `chartjs_generator.py` - Chart.js HTML generation
- ✅ `layout_assembler.py` - L02 layout assembly
- ✅ `session_manager.py` - Session context management
- ✅ `insight_generator.py` - AI insight generation

### Director Agent (Needs Implementation)
- 🔴 `agents/director_agent/v3.3/src/agents/director.py` or `v3.4/`
  - Add: `AnalyticsServiceClient` class
  - Add: `_is_analytics_slide()` method
  - Add: `_infer_analytics_type()` method
  - Add: `_generate_analytics_slide()` method
  - Modify: `process_slide()` method (add analytics routing)

- 🔴 `agents/director_agent/v3.3/config/settings.py` or `v3.4/`
  - Add: `ANALYTICS_SERVICE_URL` setting
  - Add: `ANALYTICS_TIMEOUT` setting

### Testing
- ✅ `tests/test_l02_director_integration.py` - L02 specific tests (288 lines)
- ✅ `tests/test_analytics_layout_integration.py` - Full integration tests
- 🟡 Need: Director-side integration tests (to be created)

### Documentation
- ✅ `docs/L02_INTEGRATION.md` - Complete L02 specification
- ✅ `docs/ANALYTICS_INTEGRATION_GUIDE.md` - Integration patterns
- ✅ `docs/LAYOUT_SERVICE_INTEGRATION_GUIDE.md` - Layout Builder guide
- 🟡 Update: Director Agent documentation (after implementation)

---

## Success Criteria

Integration is complete when:

- [x] Analytics Service generates L02 content correctly
- [x] Test suite passes for L02 layouts
- [x] Service deployed to Railway and accessible
- [ ] Director Agent can detect analytics slides
- [ ] Director Agent can infer analytics types correctly
- [ ] Director Agent calls Analytics Service with proper payload
- [ ] Director Agent forwards Analytics content to Layout Builder
- [ ] Layout Builder renders Chart.js charts correctly in L02 layout
- [ ] Charts animate properly in Reveal.js presentations
- [ ] Interactive editor works (if enabled)
- [ ] Error handling and fallback logic works
- [ ] End-to-end integration test passes
- [ ] Performance acceptable (<5s per analytics slide)

---

## Resources

### Production URLs
- **Analytics Service**: https://analytics-v30-production.up.railway.app
- **Layout Builder**: https://web-production-f0d13.up.railway.app
- **Director Agent**: (URL to be confirmed - likely on Railway)

### API Endpoints
- **Analytics L02**: `POST /api/v1/analytics/L02/{analytics_type}`
- **Analytics Batch**: `POST /api/v1/analytics/batch`
- **Chart Data Update**: `POST /api/charts/update-data`
- **Health Check**: `GET /health`

### Documentation Links
- Text Service Integration: `../../SERVICE_INTEGRATION_OVERVIEW.md`
- L02 Specification: `../L02_INTEGRATION.md`
- Analytics Guide: `../ANALYTICS_INTEGRATION_GUIDE.md`
- Test Organization: `../../tests/TEST_ORGANIZATION.md`

---

**Status**: Ready for Director Agent implementation
**Blocker**: None (Analytics Service ready and tested)
**Next Owner**: Director Agent development team
**Estimated Completion**: 1-2 days for Director implementation + testing

---

**Last Updated**: November 16, 2025
**Report Generated By**: Analytics Microservice Team
**Context**: Post-IDE crash investigation and status assessment
