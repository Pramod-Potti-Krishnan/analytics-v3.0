##Analytics Service v3 - Director Integration Guide

**Version**: 3.5.0
**Date**: November 21, 2025
**Status**: ✅ Production Ready
**Target Audience**: Director Agent Integration Team

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Chart Type Discovery](#chart-type-discovery)
4. [Request/Response Schema](#requestresponse-schema)
5. [Error Handling](#error-handling)
6. [Layout Integration](#layout-integration)
7. [Data Validation](#data-validation)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Migration from Legacy](#migration-from-legacy)
11. [Chart Development Workflow](#chart-development-workflow)

---

## 🚀 Quick Start

### Recommended Endpoint (Director Integration)

```http
POST https://analytics-v30-production.up.railway.app/api/v1/analytics/{layout}/{analytics_type}
```

**Why use this endpoint?**
- ✅ Synchronous responses (no job polling)
- ✅ Text Service compatible (seamless Director integration)
- ✅ Structured error responses
- ✅ Comprehensive data validation
- ✅ Layout Builder HTML auto-detection compatible

### Minimal Working Example

```python
import requests

# Generate L02 analytics slide
response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "pres-123",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth with strong Q3-Q4 performance",
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000},
            {"label": "Q3 2024", "value": 195000},
            {"label": "Q4 2024", "value": 220000}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives"
        }
    }
)

result = response.json()

# Use in Layout Builder
chart_html = result["content"]["element_3"]       # Chart.js inline script
observations_html = result["content"]["element_2"]  # Styled observations panel
```

---

## 🔍 API Overview

### Core Endpoints

| Endpoint | Method | Purpose | Use Case |
|----------|--------|---------|----------|
| `/api/v1/analytics/{layout}/{type}` | POST | Generate analytics slide | **Primary** - Director integration |
| `/api/v1/chart-types` | GET | Discover chart types | Chart type selection UI |
| `/api/v1/chart-types/{chart_id}` | GET | Get chart details | Detailed chart specs |
| `/api/v1/layouts/{layout}/chart-types` | GET | Layout compatibility | Check chart-layout compatibility |
| `/api/charts/update-data` | POST | Update chart data | Interactive editor support |
| `/health` | GET | Health check | Service monitoring |

### Deprecated Endpoints

| Endpoint | Status | Migration Path |
|----------|--------|----------------|
| `/generate` | ⚠️ Deprecated (v4.0.0) | Use `/api/v1/analytics/{layout}/{type}` |

---

## 📊 Chart Type Discovery

### Get All Chart Types

```http
GET /api/v1/chart-types
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_chart_types": 13,
    "chartjs_types": 9,
    "apexcharts_types": 4,
    "l01_compatible": 4,
    "l02_compatible": 9,
    "l03_compatible": 4
  },
  "chart_types": [
    {
      "id": "line",
      "name": "Line Chart",
      "description": "Displays trends and changes over time",
      "library": "Chart.js",
      "supported_layouts": ["L02"],
      "min_data_points": 2,
      "max_data_points": 50,
      "optimal_data_points": "3-20 points",
      "use_cases": [
        "Revenue trends over time",
        "Performance metrics tracking"
      ]
    }
    // ... more chart types
  ]
}
```

### Get Chart.js Types (L02 Compatible)

```http
GET /api/v1/chart-types/chartjs
```

**Returns**: 9 Chart.js chart types compatible with L02 layout (Director integration)

**Chart Types**:
- `line` - Line Chart
- `bar_vertical` - Vertical Bar Chart
- `bar_horizontal` - Horizontal Bar Chart
- `pie` - Pie Chart
- `doughnut` - Doughnut Chart
- `scatter` - Scatter Plot
- `bubble` - Bubble Chart
- `radar` - Radar Chart
- `polar_area` - Polar Area Chart

### Get Layout Compatibility

```http
GET /api/v1/layouts/L02/chart-types
```

**Response:**
```json
{
  "success": true,
  "layout": "L02",
  "library": "Chart.js",
  "count": 9,
  "chart_types": [/* array of compatible charts */]
}
```

---

## 📝 Request/Response Schema

### Request Schema (Universal)

```typescript
interface AnalyticsRequest {
  // Required fields
  presentation_id: string;       // Presentation UUID (1+ chars)
  slide_id: string;              // Slide identifier (1+ chars)
  slide_number: number;          // Slide position (>= 1)
  narrative: string;             // Description (1-2000 chars)
  data: ChartDataPoint[];        // 2-50 data points

  // Optional fields
  context?: {
    theme?: string;              // e.g., "professional"
    audience?: string;           // e.g., "executives"
    slide_title?: string;
    subtitle?: string;
  };
  constraints?: object;          // Layout constraints
}

interface ChartDataPoint {
  label: string;                 // Unique label (1-100 chars, not whitespace)
  value: number;                 // Finite numeric value (not NaN, not Infinity)
}
```

### Data Validation Rules

| Field | Constraint | Validation |
|-------|------------|------------|
| `data` | 2-50 points | ✅ Enforced (prevents crashes) |
| `data[].label` | Unique, not empty | ✅ Enforced (duplicate check) |
| `data[].value` | Finite number | ✅ Enforced (NaN/Infinity rejected) |
| `narrative` | 1-2000 chars | ✅ Enforced (not whitespace) |
| `presentation_id` | Not empty | ✅ Enforced (trimmed) |
| `slide_id` | Not empty | ✅ Enforced (trimmed) |
| `slide_number` | >= 1 | ✅ Enforced (1-indexed) |

### Response Schema (L02 Layout)

```typescript
interface AnalyticsResponse {
  content: {
    element_3: string;  // Chart HTML (Chart.js inline script, 1260×720px)
    element_2: string;  // Observations HTML (styled panel, 540×720px)
  };
  metadata: {
    service: "analytics_v3";
    version: "3.1.2";
    library: "chartjs";
    layout: "L02";
    chart_type: string;
    data_points: number;
    // ... additional metadata
  };
}
```

### Response Schema (L01/L03 Layouts)

```typescript
interface AnalyticsResponse {
  content: {
    chart_html: string;    // ApexCharts HTML
    insights: string;      // Generated insights
    // ... layout-specific fields
  };
  metadata: {
    service: "analytics_v3";
    version: "3.1.2";
    library: "apexcharts";
    layout: "L01" | "L03";
    // ... additional metadata
  };
}
```

---

## ⚠️ Error Handling

### Structured Error Response

All errors return consistent format:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_DATA_POINTS",
    "message": "At least 2 data points required for meaningful charts",
    "category": "validation",
    "field": "data",
    "details": {
      "provided": 1,
      "minimum": 2
    },
    "retryable": true,
    "suggestion": "Provide at least 2 data points with label and value"
  }
}
```

### Error Categories

| Category | HTTP Status | Retryable | Meaning |
|----------|-------------|-----------|---------|
| `validation` | 400 | ✅ Yes | User input error - fix data and retry |
| `processing` | 500 | ⚠️ Maybe | Internal error - may succeed on retry |
| `resource` | 404 | ❌ No | Resource not found - check IDs |
| `rate_limit` | 429 | ✅ Yes (delay) | Rate limited - wait and retry |

### Common Error Codes

| Code | HTTP | Meaning | Fix |
|------|------|---------|-----|
| `INVALID_DATA_POINTS` | 400 | Invalid data array | Check data format |
| `DUPLICATE_LABELS` | 400 | Duplicate labels found | Use unique labels |
| `DATA_RANGE_ERROR` | 400 | Too few/many points | Send 2-50 points |
| `INVALID_ANALYTICS_TYPE` | 400 | Unknown analytics type | Check supported types |
| `CHART_GENERATION_FAILED` | 500 | Chart generation error | Retry or check logs |
| `JOB_NOT_FOUND` | 404 | Job ID not found | Check job ID |

### Error Handling Best Practices

```python
import requests
from typing import Dict, Any

def call_analytics_service(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Call Analytics Service with proper error handling."""
    try:
        response = requests.post(
            "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
            json=request_data,
            timeout=30
        )

        # Check if request was successful
        if response.status_code == 200:
            return response.json()

        # Handle structured errors
        error_data = response.json()
        error = error_data.get("error", {})

        # Log error details
        print(f"Analytics Service Error [{error.get('code')}]: {error.get('message')}")

        # Check if retryable
        if error.get("retryable") and error.get("category") == "processing":
            # Retry logic here
            pass

        # Show user-friendly suggestion
        if error.get("suggestion"):
            print(f"Suggestion: {error.get('suggestion')}")

        return None

    except requests.exceptions.Timeout:
        print("Analytics Service timeout - retry with exponential backoff")
        return None

    except requests.exceptions.ConnectionError:
        print("Analytics Service unreachable - check network/Railway status")
        return None
```

---

## 🎨 Layout Integration

### L02 Layout (Chart + Observations)

**Dimensions**:
- Chart (element_3): 1260×720px (left side)
- Observations (element_2): 540×720px (right side)

**HTML Structure**:

```html
<!-- element_3: Chart HTML -->
<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide-7"></canvas>
  <script>
    (function() {
      // IIFE wrapper prevents global scope pollution
      const ctx = document.getElementById('chart-slide-7').getContext('2d');
      const chartConfig = {
        type: 'line',
        data: { /* chart data */ },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 1500,
            easing: 'easeInOutQuart'
          }
          /* ... Chart.js options ... */
        }
      };
      const chart = new Chart(ctx, chartConfig);

      // Store chart instance for interactive editor
      window.chartInstances = window.chartInstances || {};
      window.chartInstances['chart-slide-7'] = chart;
    })();
  </script>

  <!-- Edit Button (if enable_editor=true) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_7()">✏️</button>

  <!-- Interactive Editor Modal (if enable_editor=true) -->
  <!-- ... modal HTML ... -->
</div>

<!-- element_2: Observations HTML -->
<div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
  <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 20px; font-weight: 600; color: #1f2937; margin: 0 0 16px 0; line-height: 1.3;">
    Key Insights
  </h3>
  <p style="font-family: 'Inter', -apple-system, sans-serif; font-size: 16px; line-height: 1.6; color: #374151; margin: 0 0 12px 0;">
    The quarterly revenue data shows strong growth trajectory...
  </p>
</div>
```

**Layout Builder Compatibility**:
- ✅ HTML auto-detection works (`<script>` tags present)
- ✅ Chart.js initializes via inline script (no external dependencies)
- ✅ Reveal.js integration (slidechanged event support)
- ✅ Interactive editor (if enabled)

### L01 Layout (Centered Chart + Text)

**Dimensions**:
- Chart: 1800×600px (centered)

**Library**: ApexCharts

### L03 Layout (Side-by-Side Charts)

**Dimensions**:
- Chart 1: 840×540px (left)
- Chart 2: 840×540px (right)

**Library**: ApexCharts

---

## ✅ Data Validation

### Input Validation (Automatic)

Analytics Service v3.1.2 includes comprehensive Pydantic validation:

**Validated Automatically**:
- ✅ Data array has 2-50 points
- ✅ Labels are unique (no duplicates)
- ✅ Labels are not empty or whitespace
- ✅ Values are finite numbers (no NaN, no Infinity)
- ✅ Presentation ID and Slide ID are not empty
- ✅ Narrative is 1-2000 characters
- ✅ Slide number is >= 1

**Validation Errors Return 400 with Details**:

```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_LABELS",
    "message": "Duplicate labels found. Each data point must have a unique label",
    "category": "validation",
    "field": "data",
    "details": {
      "validation_errors": [/* Pydantic errors */]
    },
    "retryable": true,
    "suggestion": "Check the request data format and try again"
  }
}
```

### Pre-Request Validation (Recommended)

```python
def validate_analytics_request(data: list) -> tuple[bool, str]:
    """
    Validate analytics request before sending to service.

    Returns: (is_valid, error_message)
    """
    # Check data point count
    if len(data) < 2:
        return False, "At least 2 data points required"
    if len(data) > 50:
        return False, "Maximum 50 data points allowed"

    # Check for duplicate labels
    labels = [point["label"] for point in data]
    if len(labels) != len(set(labels)):
        return False, "Duplicate labels found"

    # Check for empty labels or invalid values
    for i, point in enumerate(data):
        if not point.get("label") or not str(point["label"]).strip():
            return False, f"Label at index {i} is empty"

        try:
            value = float(point["value"])
            if value != value or abs(value) == float('inf'):
                return False, f"Value at index {i} is NaN or Infinity"
        except (TypeError, ValueError):
            return False, f"Value at index {i} is not a number"

    return True, ""

# Usage
is_valid, error = validate_analytics_request(request_data["data"])
if not is_valid:
    print(f"Validation failed: {error}")
else:
    # Safe to call Analytics Service
    response = call_analytics_service(request_data)
```

---

## 🎯 Best Practices

### 1. Use Synchronous Endpoint

✅ **DO**: Use `/api/v1/analytics/{layout}/{type}`
```python
# Synchronous - immediate response
response = requests.post(url, json=request_data)
result = response.json()
```

❌ **DON'T**: Use deprecated `/generate` (requires polling)
```python
# Async - requires polling job status
job_response = requests.post("/generate", json=request_data)
job_id = job_response.json()["job_id"]

# Must poll for completion
while True:
    status = requests.get(f"/status/{job_id}").json()
    if status["status"] == "completed":
        break
```

### 2. Validate Data Before Sending

✅ **DO**: Pre-validate to catch errors early
```python
# Validate before calling service
is_valid, error = validate_analytics_request(data)
if not is_valid:
    return {"error": error}

response = call_analytics_service(request_data)
```

❌ **DON'T**: Send invalid data and rely on service validation
```python
# Service will reject, but wastes network round-trip
response = call_analytics_service(invalid_data)
```

### 3. Handle Structured Errors

✅ **DO**: Parse error structure and show suggestions
```python
if not response.ok:
    error = response.json().get("error", {})
    print(f"Error: {error.get('message')}")
    if error.get("suggestion"):
        print(f"Fix: {error['suggestion']}")
    if error.get("retryable"):
        # Implement retry logic
        pass
```

❌ **DON'T**: Just show raw error message
```python
print(response.text)  # Hard to parse, no structured info
```

### 4. Use Chart Type Discovery

✅ **DO**: Discover chart types dynamically
```python
# Get compatible charts for L02
charts = requests.get("/api/v1/layouts/L02/chart-types").json()
for chart in charts["chart_types"]:
    print(f"{chart['name']}: {chart['description']}")
```

❌ **DON'T**: Hardcode chart type lists
```python
CHART_TYPES = ["line", "bar", "pie"]  # May become outdated
```

### 5. Optimize Data Point Count

| Chart Type | Optimal Range | Reasoning |
|-----------|---------------|-----------|
| Line | 3-20 points | Too many = cluttered, too few = not meaningful |
| Bar (Vertical) | 3-12 bars | Good visual comparison without overcrowding |
| Pie/Doughnut | 3-6 slices | More slices = hard to distinguish |
| Scatter/Bubble | 10-50 points | Pattern detection requires sufficient points |

### 6. Set Timeouts

✅ **DO**: Set reasonable timeouts
```python
response = requests.post(url, json=data, timeout=30)  # 30 seconds
```

❌ **DON'T**: Use infinite timeout
```python
response = requests.post(url, json=data)  # May hang indefinitely
```

---

## 🔧 Troubleshooting

### Issue: Chart Not Rendering

**Symptoms**: Blank slide or no chart visible

**Possible Causes**:
1. HTML not being detected by Layout Builder
2. Chart.js library not loaded
3. Invalid chart configuration

**Solutions**:
```python
# 1. Verify HTML contains <script> tags
html = result["content"]["element_3"]
assert "<script>" in html, "No inline script found"

# 2. Check Chart.js is loaded in Layout Builder
# Ensure Chart.js 3.x is included in Layout Builder dependencies

# 3. Validate chart configuration
assert "new Chart(" in html, "Chart instance creation missing"
```

### Issue: Edit Button Not Showing

**Symptoms**: No edit button on chart

**Possible Cause**: `enable_editor=False` (default)

**Solution**:
```python
# Analytics Service uses enable_editor=False by default
# Contact Analytics team to enable or request via API parameter
```

### Issue: Animations Not Working

**Symptoms**: Charts appear instantly without animation

**Possible Cause**: Reveal.js timing or animation config

**Solution**:
```python
# Verify animation config in HTML
html = result["content"]["element_3"]
assert '"duration": 1500' in html, "Animation duration missing"

# Check Reveal.js slidechanged event listener
assert "slidechanged" in html, "Reveal.js integration missing"
```

### Issue: Validation Errors

**Symptoms**: 400 error with validation message

**Solution**:
```python
# Check error details
error = response.json()["error"]
print(f"Field: {error['field']}")
print(f"Message: {error['message']}")
print(f"Suggestion: {error['suggestion']}")

# Fix data based on suggestion
if error["code"] == "DUPLICATE_LABELS":
    # Make labels unique
    data = make_labels_unique(data)
```

### Issue: Service Timeout

**Symptoms**: Request times out after 30s

**Possible Causes**:
1. Large data set (>50 points)
2. LLM insight generation slow
3. Network issues

**Solutions**:
```python
# 1. Reduce data points (optimize to recommended range)
if len(data) > 20:
    data = data[:20]  # Trim to optimal range

# 2. Retry with exponential backoff
import time
for attempt in range(3):
    try:
        response = requests.post(url, json=data, timeout=30)
        break
    except requests.exceptions.Timeout:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
        else:
            raise
```

---

## 🔄 Migration from Legacy

### From `/generate` to `/api/v1/analytics/{layout}/{type}`

**Before** (Deprecated):
```python
# Async pattern with job polling
response = requests.post(
    "https://analytics-v30-production.up.railway.app/generate",
    json={
        "content": "Show quarterly revenue growth",
        "title": "Revenue Chart",
        "data": [
            {"label": "Q1", "value": 125000},
            {"label": "Q2", "value": 145000}
        ],
        "chart_type": "bar_vertical",
        "theme": "professional"
    }
)
job_id = response.json()["job_id"]

# Poll for completion
while True:
    status_response = requests.get(f"https://analytics-v30-production.up.railway.app/status/{job_id}")
    status = status_response.json()
    if status["status"] == "completed":
        result = status["result"]
        break
    time.sleep(1)
```

**After** (Recommended):
```python
# Sync pattern with immediate response
response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "pres-123",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth highlighting strong performance",
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives"
        }
    }
)

# Immediate result
result = response.json()
chart_html = result["content"]["element_3"]
observations = result["content"]["element_2"]
```

**Benefits**:
- ✅ No job polling (simpler code)
- ✅ Text Service compatible (Director integration)
- ✅ Structured errors
- ✅ Better data validation
- ✅ Chart type discovery

---

## 🛠️ Chart Development Workflow

### Required Steps When Adding New Chart Types

**CRITICAL**: Every time a new chart type is added to the Analytics Service, the following steps MUST be completed:

#### 1. Update CHART_TYPE_CATALOG.md

**Location**: `/docs/CHART_TYPE_CATALOG.md`

**Required Updates**:
- Update version number and date in header
- Increment total chart type count
- Add new section with complete chart specification:
  - Chart ID and library
  - Description
  - Data constraints (min/max/optimal points)
  - Use cases and examples
  - Data requirements (JSON schema)
  - Visual properties
  - Interactive features
  - When to use / When NOT to use
  - API example with curl command
- Update Quick Reference Matrix table
- Update Chart Selection Guide tables
- Update "By Layout" table

#### 2. Provide Director Test Prompt

After updating the catalog, **immediately provide the user with a Director test prompt** following this template:

```
Create a presentation slide showing [BUSINESS CONTEXT]. Use a [CHART_TYPE] chart type to visualize the following data:
[SAMPLE DATA IN NATURAL LANGUAGE]

The slide should highlight [KEY INSIGHTS] and suggest [STRATEGIC RECOMMENDATIONS].
```

**Example** (for d3_treemap):
```
Create a presentation slide showing our department budget allocation for FY 2025. Use a d3_treemap chart type to visualize the following data:
- Engineering: $450,000
- Sales: $320,000
- Marketing: $180,000
- Operations: $120,000
- HR: $80,000
- Finance: $60,000

The slide should highlight which departments have the largest budget allocations and suggest strategic insights about resource distribution.
```

#### 3. Documentation Checklist

Before marking chart development as complete:

- [ ] CHART_TYPE_CATALOG.md updated with new chart entry
- [ ] Version and date updated in catalog header
- [ ] Chart type count incremented
- [ ] Quick Reference Matrix includes new chart
- [ ] Chart Selection Guide tables updated
- [ ] DATA_FORMATS_REFERENCE.md updated with data format example
- [ ] README.md updated with chart type count
- [ ] Director test prompt provided to user
- [ ] User has confirmed successful test from Director's end

### Catalog Maintenance

**File**: `docs/CHART_TYPE_CATALOG.md`
**Purpose**: Primary reference for Director service chart selection
**Update Frequency**: Every new chart type addition
**Review Schedule**: Quarterly for accuracy

This catalog is the **single source of truth** that Director uses to:
- Discover available chart types
- Understand data constraints
- Select appropriate chart for user's narrative
- Generate proper API requests

**Failure to update the catalog will result in Director not being able to use the new chart type.**

---

## 📞 Support & Resources

### Documentation
- **Chart Type Catalog**: [CHART_TYPE_CATALOG.md](./CHART_TYPE_CATALOG.md)
- **Error Codes**: [ERROR_CODES.md](./ERROR_CODES.md)
- **OpenAPI Spec**: Available at `/docs` endpoint

### Service URLs
- **Production**: `https://analytics-v30-production.up.railway.app`
- **Health Check**: `https://analytics-v30-production.up.railway.app/health`
- **API Docs**: `https://analytics-v30-production.up.railway.app/docs`

### Contact
- **Analytics Team**: (Contact info)
- **Director Team**: (Contact info)
- **Issues**: Report via internal ticketing system

---

**Last Updated**: November 21, 2025
**Version**: 3.5.0
**Next Review**: Q1 2026
