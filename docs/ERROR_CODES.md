# Error Codes Reference - Analytics Service v3

**Version**: 3.1.2
**Date**: November 16, 2025
**Error Format**: Structured JSON responses

---

## 📋 Overview

Analytics Service v3.1.2 uses structured error responses with consistent formatting, error codes, categories, and actionable suggestions for quick resolution.

### Error Response Structure

All errors return this standard format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE_NAME",
    "message": "Human-readable error description",
    "category": "error_category",
    "field": "field_name",
    "details": {
      "additional": "context"
    },
    "retryable": true,
    "suggestion": "How to fix this error"
  }
}
```

---

## 🏷️ Error Categories

| Category | HTTP Status | Retryable | Description |
|----------|-------------|-----------|-------------|
| `validation` | 400 | ✅ Yes | User input errors - fix data and retry |
| `processing` | 500 | ⚠️ Maybe | Internal processing errors - may succeed on retry |
| `resource` | 404 | ❌ No | Resource not found - check IDs or URLs |
| `rate_limit` | 429 | ✅ Yes (delay) | Rate limited - wait and retry after delay |
| `system` | 500 | ❌ No | System errors - contact support |

---

## ⚠️ Validation Errors (400)

### INVALID_DATA_POINTS

**Code**: `INVALID_DATA_POINTS`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: The data array is invalid or incorrectly formatted.

**Common Causes**:
- Empty data array
- Data points with missing `label` or `value` fields
- Invalid data structure

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_DATA_POINTS",
    "message": "Data point at index 2 missing required field 'value'",
    "category": "validation",
    "field": "data",
    "details": {
      "index": 2,
      "provided_fields": ["label"]
    },
    "retryable": true,
    "suggestion": "Ensure each data point has both 'label' and 'value' fields"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
data = [
    {"label": "Q1"},  # Missing value
    {"value": 100}     # Missing label
]

# ✅ Correct
data = [
    {"label": "Q1", "value": 125000},
    {"label": "Q2", "value": 145000}
]
```

---

### INVALID_LABELS

**Code**: `INVALID_LABELS`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: One or more labels are empty, whitespace-only, or exceed maximum length.

**Common Causes**:
- Empty string labels
- Whitespace-only labels
- Labels exceeding 100 characters

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_LABELS",
    "message": "Label at index 1 cannot be empty or whitespace",
    "category": "validation",
    "field": "data",
    "details": {
      "index": 1,
      "label": "   "
    },
    "retryable": true,
    "suggestion": "Provide non-empty labels with meaningful text"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
data = [
    {"label": "", "value": 100},      # Empty
    {"label": "   ", "value": 200}    # Whitespace
]

# ✅ Correct
data = [
    {"label": "Q1 2024", "value": 100},
    {"label": "Q2 2024", "value": 200}
]
```

---

### INVALID_VALUES

**Code**: `INVALID_VALUES`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: One or more values are not valid numbers (NaN, Infinity, or non-numeric).

**Common Causes**:
- NaN values
- Infinity values
- String values instead of numbers
- null values

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_VALUES",
    "message": "Value at index 3 is NaN",
    "category": "validation",
    "field": "data",
    "details": {
      "index": 3,
      "value": "NaN"
    },
    "retryable": true,
    "suggestion": "Ensure all values are finite numbers (not NaN or Infinity)"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
data = [
    {"label": "Q1", "value": float('nan')},     # NaN
    {"label": "Q2", "value": float('inf')},     # Infinity
    {"label": "Q3", "value": "100"},            # String (will be coerced)
    {"label": "Q4", "value": None}              # null
]

# ✅ Correct
data = [
    {"label": "Q1", "value": 125000},
    {"label": "Q2", "value": 145000},
    {"label": "Q3", "value": 162000},
    {"label": "Q4", "value": 178000}
]
```

---

### MISMATCHED_LENGTHS

**Code**: `MISMATCHED_LENGTHS`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Labels and values arrays have different lengths (for interactive editor).

**Common Causes**:
- Editing chart data with mismatched arrays
- Adding/removing labels without updating values

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "MISMATCHED_LENGTHS",
    "message": "Number of values (5) must match number of labels (4)",
    "category": "validation",
    "field": "values",
    "details": {
      "labels_count": 4,
      "values_count": 5
    },
    "retryable": true,
    "suggestion": "Ensure labels and values arrays have the same length"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
labels = ["Q1", "Q2", "Q3", "Q4"]
values = [100, 200, 300, 400, 500]  # 5 values, 4 labels

# ✅ Correct
labels = ["Q1", "Q2", "Q3", "Q4"]
values = [100, 200, 300, 400]  # Matching lengths
```

---

### DUPLICATE_LABELS

**Code**: `DUPLICATE_LABELS`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Duplicate labels found in data array. Each label must be unique.

**Common Causes**:
- Copy-paste errors
- Using same time period twice
- Typos creating duplicates

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_LABELS",
    "message": "Duplicate labels found. Each data point must have a unique label",
    "category": "validation",
    "field": "data",
    "details": {
      "duplicate_label": "Q1",
      "occurrences": 2
    },
    "retryable": true,
    "suggestion": "Make all labels unique (e.g., 'Q1 2024', 'Q1 2025')"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
data = [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 200},
    {"label": "Q1", "value": 300}  # Duplicate!
]

# ✅ Correct
data = [
    {"label": "Q1 2024", "value": 100},
    {"label": "Q2 2024", "value": 200},
    {"label": "Q1 2025", "value": 300}
]
```

---

### DATA_RANGE_ERROR

**Code**: `DATA_RANGE_ERROR`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Data points out of acceptable range (2-50 points).

**Common Causes**:
- Too few data points (<2)
- Too many data points (>50)

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "DATA_RANGE_ERROR",
    "message": "At least 2 data points required for meaningful charts",
    "category": "validation",
    "field": "data",
    "details": {
      "provided": 1,
      "minimum": 2,
      "maximum": 50
    },
    "retryable": true,
    "suggestion": "Provide between 2 and 50 data points"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong - Too few
data = [
    {"label": "Q1", "value": 100}
]

# ❌ Wrong - Too many
data = [{"label": f"Point{i}", "value": i*100} for i in range(100)]

# ✅ Correct
data = [
    {"label": "Q1", "value": 125000},
    {"label": "Q2", "value": 145000},
    {"label": "Q3", "value": 162000},
    {"label": "Q4", "value": 178000}
]
```

---

### EMPTY_FIELD

**Code**: `EMPTY_FIELD`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Required field is empty or whitespace-only.

**Common Causes**:
- Empty presentation_id or slide_id
- Empty narrative
- Whitespace-only strings

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "EMPTY_FIELD",
    "message": "Narrative cannot be empty or whitespace",
    "category": "validation",
    "field": "narrative",
    "details": {
      "provided": "   "
    },
    "retryable": true,
    "suggestion": "Provide a meaningful description of the analytics needed"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
request = {
    "presentation_id": "",
    "narrative": "   ",
    "data": [...]
}

# ✅ Correct
request = {
    "presentation_id": "pres-123",
    "narrative": "Show quarterly revenue growth",
    "data": [...]
}
```

---

### INVALID_ANALYTICS_TYPE

**Code**: `INVALID_ANALYTICS_TYPE`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Unknown or unsupported analytics type specified.

**Common Causes**:
- Typo in analytics type
- Using unsupported analytics type
- Old analytics type no longer available

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_ANALYTICS_TYPE",
    "message": "Invalid analytics type: revenue_trend",
    "category": "validation",
    "field": "analytics_type",
    "details": {
      "provided": "revenue_trend",
      "supported": [
        "revenue_over_time",
        "quarterly_comparison",
        "market_share",
        "yoy_growth",
        "kpi_metrics"
      ]
    },
    "retryable": true,
    "suggestion": "Use one of: revenue_over_time, quarterly_comparison, market_share, yoy_growth, kpi_metrics"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
url = "/api/v1/analytics/L02/revenue_trend"  # Invalid type

# ✅ Correct
url = "/api/v1/analytics/L02/revenue_over_time"
```

---

### INVALID_LAYOUT

**Code**: `INVALID_LAYOUT`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Unknown or unsupported layout type specified.

**Common Causes**:
- Typo in layout
- Using unsupported layout
- Lowercase instead of uppercase

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_LAYOUT",
    "message": "Invalid layout: l02",
    "category": "validation",
    "field": "layout",
    "details": {
      "provided": "l02",
      "supported": ["L01", "L02", "L03"]
    },
    "retryable": true,
    "suggestion": "Use one of: L01, L02, L03 (uppercase)"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
url = "/api/v1/analytics/l02/revenue_over_time"  # Lowercase

# ✅ Correct
url = "/api/v1/analytics/L02/revenue_over_time"  # Uppercase
```

---

### INVALID_CHART_TYPE

**Code**: `INVALID_CHART_TYPE`
**HTTP Status**: 400
**Category**: validation
**Retryable**: ✅ Yes

**Description**: Unknown chart type requested via chart discovery API.

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CHART_TYPE",
    "message": "Chart type 'barchart' not found",
    "category": "validation",
    "field": "chart_id",
    "details": {
      "provided": "barchart"
    },
    "retryable": true,
    "suggestion": "Use /api/v1/chart-types to discover available chart types"
  }
}
```

**How to Fix**:
```python
# ❌ Wrong
url = "/api/v1/chart-types/barchart"

# ✅ Correct
url = "/api/v1/chart-types/bar_vertical"
```

---

## 🔴 Processing Errors (500)

### CHART_GENERATION_FAILED

**Code**: `CHART_GENERATION_FAILED`
**HTTP Status**: 500
**Category**: processing
**Retryable**: ⚠️ Maybe

**Description**: Chart generation encountered an internal error.

**Common Causes**:
- Chart.js configuration error
- ApexCharts rendering error
- Template processing error

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "CHART_GENERATION_FAILED",
    "message": "Failed to generate chart: Unexpected chart configuration error",
    "category": "processing",
    "details": {
      "analytics_type": "revenue_over_time",
      "layout": "L02",
      "exception_type": "ValueError"
    },
    "retryable": true,
    "suggestion": "Retry the request. If error persists, contact support"
  }
}
```

**How to Fix**:
1. Retry the request (may be transient)
2. Check if data format is correct
3. Contact support if error persists

---

### INSIGHT_GENERATION_FAILED

**Code**: `INSIGHT_GENERATION_FAILED`
**HTTP Status**: 500
**Category**: processing
**Retryable**: ⚠️ Maybe

**Description**: LLM-based insight generation failed.

**Common Causes**:
- LLM API timeout
- LLM API rate limit
- Invalid narrative input

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "INSIGHT_GENERATION_FAILED",
    "message": "Failed to generate insights: LLM API timeout",
    "category": "processing",
    "details": {
      "llm_provider": "OpenAI",
      "timeout": "30s"
    },
    "retryable": true,
    "suggestion": "Retry the request. Insights will be generated using fallback if LLM continues to fail"
  }
}
```

**How to Fix**:
1. Retry the request
2. Service has fallback insight generation if LLM fails
3. Check LLM API status if error persists

---

### LAYOUT_ASSEMBLY_FAILED

**Code**: `LAYOUT_ASSEMBLY_FAILED`
**HTTP Status**: 500
**Category**: processing
**Retryable**: ⚠️ Maybe

**Description**: Failed to assemble layout content.

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "LAYOUT_ASSEMBLY_FAILED",
    "message": "Failed to assemble L02 layout",
    "category": "processing",
    "details": {
      "layout": "L02"
    },
    "retryable": true,
    "suggestion": "Retry the request. Contact support if error persists"
  }
}
```

---

### STORAGE_ERROR

**Code**: `STORAGE_ERROR`
**HTTP Status**: 500
**Category**: processing
**Retryable**: ⚠️ Maybe

**Description**: Supabase Storage error (L01/L03 layouts).

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "STORAGE_ERROR",
    "message": "Failed to upload chart to Supabase Storage",
    "category": "processing",
    "details": {
      "bucket": "analytics-charts",
      "error": "Connection timeout"
    },
    "retryable": true,
    "suggestion": "Retry the request. Check Supabase status if error persists"
  }
}
```

---

### LLM_ERROR

**Code**: `LLM_ERROR`
**HTTP Status**: 500
**Category**: processing
**Retryable**: ⚠️ Maybe

**Description**: LLM API error (OpenAI, Google Gemini, etc.).

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "LLM_ERROR",
    "message": "LLM API error: Rate limit exceeded",
    "category": "processing",
    "details": {
      "provider": "OpenAI",
      "model": "gpt-4o-mini"
    },
    "retryable": true,
    "suggestion": "Wait a moment and retry. Service will use fallback insights if needed"
  }
}
```

---

## 🔍 Resource Errors (404)

### JOB_NOT_FOUND

**Code**: `JOB_NOT_FOUND`
**HTTP Status**: 404
**Category**: resource
**Retryable**: ❌ No

**Description**: Job ID not found (for legacy `/generate` endpoint).

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "Job job-12345 not found",
    "category": "resource",
    "details": {
      "job_id": "job-12345"
    },
    "retryable": false,
    "suggestion": "Check job ID or use /api/v1/analytics/{layout}/{type} for synchronous responses"
  }
}
```

**How to Fix**:
- Verify job ID is correct
- Jobs may expire after cleanup period
- Use modern synchronous endpoint instead

---

### CHART_NOT_FOUND

**Code**: `CHART_NOT_FOUND`
**HTTP Status**: 404
**Category**: resource
**Retryable**: ❌ No

**Description**: Chart not found in database (for interactive editor).

---

### PRESENTATION_NOT_FOUND

**Code**: `PRESENTATION_NOT_FOUND`
**HTTP Status**: 404
**Category**: resource
**Retryable**: ❌ No

**Description**: Presentation not found (for interactive editor).

---

## ⏱️ Rate Limiting Errors (429)

### RATE_LIMIT_EXCEEDED

**Code**: `RATE_LIMIT_EXCEEDED`
**HTTP Status**: 429
**Category**: rate_limit
**Retryable**: ✅ Yes (with delay)

**Description**: Rate limit exceeded. Wait before retrying.

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded: 100 requests per minute",
    "category": "rate_limit",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after": 45
    },
    "retryable": true,
    "suggestion": "Wait 45 seconds before retrying"
  }
}
```

**How to Fix**:
- Implement exponential backoff
- Respect `retry_after` value
- Reduce request frequency

---

## ❓ Generic Errors

### UNKNOWN_ERROR

**Code**: `UNKNOWN_ERROR`
**HTTP Status**: 500
**Category**: system
**Retryable**: ❌ No

**Description**: Unexpected error occurred.

**Example Error**:
```json
{
  "success": false,
  "error": {
    "code": "UNKNOWN_ERROR",
    "message": "An unexpected error occurred",
    "category": "system",
    "details": {},
    "retryable": false,
    "suggestion": "Contact support with request details"
  }
}
```

---

## 🛠️ Error Handling Best Practices

### 1. Check Error Category

```python
error = response.json().get("error", {})
category = error.get("category")

if category == "validation":
    # User input error - fix data and retry
    print(f"Fix required: {error.get('suggestion')}")

elif category == "processing":
    # Internal error - may retry
    if error.get("retryable"):
        # Implement retry logic
        pass

elif category == "resource":
    # Not found - don't retry
    print(f"Resource not found: {error.get('message')}")
```

### 2. Use Error Suggestions

```python
error = response.json().get("error", {})
if error.get("suggestion"):
    print(f"💡 Suggestion: {error['suggestion']}")
```

### 3. Implement Retry Logic

```python
import time

def call_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(url, json=data)

        if response.status_code == 200:
            return response.json()

        error = response.json().get("error", {})

        # Don't retry if not retryable
        if not error.get("retryable"):
            raise Exception(error.get("message"))

        # Exponential backoff
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)

    raise Exception("Max retries exceeded")
```

### 4. Log Error Details

```python
import logging

error = response.json().get("error", {})
logging.error(
    f"Analytics Service Error: {error.get('code')} - {error.get('message')}",
    extra={
        "error_code": error.get("code"),
        "error_category": error.get("category"),
        "error_field": error.get("field"),
        "error_details": error.get("details"),
        "retryable": error.get("retryable")
    }
)
```

---

## 📞 Support

If you encounter errors not covered in this guide:

1. **Check** error code and category
2. **Review** error details and suggestion
3. **Retry** if error is retryable
4. **Contact** support with:
   - Error code
   - Full error response
   - Request payload (sanitized)
   - Timestamp

---

**Last Updated**: November 16, 2025
**Version**: 3.1.2
**Related Documentation**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md), [CHART_TYPE_CATALOG.md](./CHART_TYPE_CATALOG.md)
