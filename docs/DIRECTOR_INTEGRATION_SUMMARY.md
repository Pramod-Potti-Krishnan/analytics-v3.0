# Analytics Service v3.1.3 - Director Integration Summary (CORRECTED)

**Date**: November 17, 2025
**Version**: v3.1.3 (Updated after Director Team compatibility testing)
**Production URL**: https://analytics-v30-production.up.railway.app
**Status**: 🔄 **UPDATES IN PROGRESS** - Fixing compatibility issues

---

## ⚠️ IMPORTANT CORRECTION

**This document has been rewritten to accurately reflect the actual Analytics Service implementation** after Director v3.4 team discovered critical discrepancies in our original documentation.

**Changes from v3.1.2**:
- ✅ Corrected analytics types count (5 → 9 in v3.1.3)
- ✅ Clarified analytics_type vs chart_type distinction
- ✅ Fixed data format documentation (all charts use label-value only)
- ✅ Clarified L02 layout response format

---

## 🎯 Executive Summary

Analytics Service v3.1.3 provides **5 analytics types** (expanding to **9 in this release**) that automatically select appropriate chart visualizations from a catalog of **13 chart types**.

### Critical Distinction: Analytics Types vs Chart Types

**❌ PREVIOUS DOCUMENTATION ERROR**: Claimed "9 analytics types supported"
**✅ ACTUAL IMPLEMENTATION**: **5 analytics types** in v3.1.2, expanding to **9 in v3.1.3**

**What's the difference?**

| Concept | Definition | Count | User Controls |
|---------|------------|-------|---------------|
| **Analytics Type** | Business scenario endpoint (e.g., `revenue_over_time`) | 5→9 | ✅ YES - Specified in URL |
| **Chart Type** | Visual format (e.g., `line`, `pie`, `scatter`) | 13 | ❌ NO - Auto-selected by service |

**How it works**:
```
User requests → analytics_type (revenue_over_time)
Service selects → chart_type (line)
Service generates → Chart.js or ApexCharts visualization
```

---

## 📊 Supported Analytics Types

### **v3.1.2 (Current Production) - 5 Types**

| Analytics Type | Chart Type Auto-Selected | Description | Layout |
|---------------|-------------------------|-------------|---------|
| `revenue_over_time` | line | Revenue trends over time | L02 |
| `quarterly_comparison` | bar_vertical | Compare quarterly metrics | L02 |
| `market_share` | pie | Market share distribution | L02 |
| `yoy_growth` | bar_vertical | Year-over-year growth | L02 |
| `kpi_metrics` | doughnut | KPI metrics visualization | L02 |

### **v3.1.3 (Deploying within 24 hours) - 9 Types**

**NEW analytics types being added**:

| Analytics Type | Chart Type Auto-Selected | Description | Layout |
|---------------|-------------------------|-------------|---------|
| ✅ `revenue_over_time` | line | Revenue trends over time | L02 |
| ✅ `quarterly_comparison` | bar_vertical | Compare quarterly metrics | L02 |
| ✅ `market_share` | pie | Market share distribution | L02 |
| ✅ `yoy_growth` | bar_vertical | Year-over-year growth | L02 |
| ✅ `kpi_metrics` | doughnut | KPI metrics visualization | L02 |
| **🆕 `category_ranking`** | **bar_horizontal** | **Ranked category comparison** | **L02** |
| **🆕 `correlation_analysis`** | **scatter** | **Correlation between variables** | **L02** |
| **🆕 `multidimensional_analysis`** | **bubble** | **3-dimensional data analysis** | **L02** |
| **🆕 `multi_metric_comparison`** | **radar** | **Compare multiple metrics** | **L02** |
| **🆕 `radial_composition`** | **polar_area** | **Radial data composition** | **L02** |

---

## 🔧 API Usage

### **Correct Endpoint Usage**

```python
# ✅ CORRECT - Use analytics_type in URL
POST /api/v1/analytics/L02/revenue_over_time

# ❌ WRONG - Cannot specify chart_type directly
POST /api/v1/analytics/L02/line  # This will fail!
```

### **Request Format (ALL Charts Use label-value Format)**

**⚠️ CRITICAL**: All charts require `label` and `value` fields, regardless of chart type.

```python
import requests

response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "pres-123",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth",
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
```

### **Data Format - IMPORTANT CLARIFICATION**

**❌ PREVIOUS DOCUMENTATION ERROR**:
- Claimed scatter charts accept `{"x": value, "y": value}` format
- Claimed bubble charts accept `{"x": value, "y": value, "r": value}` format

**✅ ACTUAL IMPLEMENTATION**:
- **ALL chart types** use `{"label": string, "value": number}` format
- Scatter and bubble charts convert label-value data to x-y coordinates automatically
- **No x-y-r format is supported** in current implementation

```python
# ✅ CORRECT - Works for ALL chart types (including scatter/bubble)
data = [
    {"label": "Point A", "value": 100},
    {"label": "Point B", "value": 200}
]

# ❌ WRONG - NOT SUPPORTED (despite previous documentation)
data = [
    {"x": 100, "y": 200},  # Will fail validation
    {"x": 150, "y": 300}
]
```

---

## 📤 Response Format (L02 Layout Only)

### **Successful Response Structure**

```json
{
  "success": true,
  "content": {
    "element_3": "<div id=\"chart-slide-7\">...Chart HTML with inline Chart.js...</div>",
    "element_2": "<p class=\"observations-text\">Generated observations paragraph...</p>",
    "slide_id": "slide-7",
    "layout": "L02"
  },
  "metadata": {
    "chart_type": "line",
    "analytics_type": "revenue_over_time",
    "data_points": 4,
    "theme": "professional",
    "generation_time_ms": 1234,
    "llm_model": "gemini-1.5-flash-002"
  }
}
```

### **Response Fields Explained**

| Field | Type | Description | Size |
|-------|------|-------------|------|
| `element_3` | string | Complete Chart HTML with inline Chart.js/ApexCharts script | 2,000-50,000 chars |
| `element_2` | string | Generated observations paragraph HTML | 100-1,000 chars |
| `slide_id` | string | Echo of input slide_id | - |
| `layout` | string | Always "L02" for analytics endpoint | - |

**⚠️ IMPORTANT**:
- `element_3` and `element_2` are **ONLY returned for L02 layout**
- L01 and L03 layouts use different field names
- Always use `/api/v1/analytics/L02/{analytics_type}` endpoint for Director integration

---

## 🔍 Chart Type Discovery API

### **Why Use Chart Discovery?**

Chart discovery API lets you explore the **13 chart types** supported by the service, even though you can't directly specify them when using analytics_type endpoints.

**Use cases**:
- Understand what visualizations are possible
- See data constraints for each chart type
- Plan which analytics_type to use based on desired visualization

### **Discovery Endpoints**

#### 1. **GET /api/v1/chart-types** - Complete Catalog
```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types
```
**Returns**: All 13 chart types with specifications

#### 2. **GET /api/v1/chart-types/chartjs** - Chart.js Types Only
```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types/chartjs
```
**Returns**: 9 Chart.js chart types

#### 3. **GET /api/v1/chart-types/{chart_id}** - Specific Chart Details
```bash
curl https://analytics-v30-production.up.railway.app/api/v1/chart-types/line
```
**Returns**: Complete specification for a specific chart type

### **13 Chart Types in Catalog**

**Chart.js Types (9)**:
1. `line` - Line Chart (trends over time)
2. `bar_vertical` - Vertical Bar Chart (category comparison)
3. `bar_horizontal` - Horizontal Bar Chart (ranked comparison)
4. `pie` - Pie Chart (part-to-whole)
5. `doughnut` - Doughnut Chart (part-to-whole with center)
6. `scatter` - Scatter Plot (correlation)
7. `bubble` - Bubble Chart (3-dimensional)
8. `radar` - Radar Chart (multi-dimensional comparison)
9. `polar_area` - Polar Area Chart (cyclic data)

**ApexCharts Types (4)**:
10. `area` - Area Chart (cumulative trends)
11. `heatmap` - Heatmap (matrix visualization)
12. `treemap` - Treemap (hierarchical data)
13. `waterfall` - Waterfall Chart (cumulative changes)

**Chart Type to Analytics Type Mapping (v3.1.3)**:

| Chart Type | Analytics Type(s) That Use It |
|-----------|------------------------------|
| line | revenue_over_time |
| bar_vertical | quarterly_comparison, yoy_growth |
| bar_horizontal | category_ranking 🆕 |
| pie | market_share |
| doughnut | kpi_metrics |
| scatter | correlation_analysis 🆕 |
| bubble | multidimensional_analysis 🆕 |
| radar | multi_metric_comparison 🆕 |
| polar_area | radial_composition 🆕 |

---

## ✅ Data Validation Rules

### **Constraints (Strictly Enforced)**

| Rule | Constraint | Error Code |
|------|-----------|-----------|
| Minimum data points | 2 points | INVALID_DATA_POINTS |
| Maximum data points | 50 points | INVALID_DATA_POINTS |
| Label format | Non-empty string, 1-100 chars | INVALID_LABELS |
| Value format | Finite number (no NaN/Infinity) | INVALID_VALUES |
| Duplicate labels | All labels must be unique | DUPLICATE_LABELS |
| Array matching | Labels and values same length | MISMATCHED_LENGTHS |

### **Validation Example**

```python
# ✅ VALID
data = [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000}
]

# ❌ INVALID - Too few points
data = [{"label": "Q1", "value": 100}]  # Error: INVALID_DATA_POINTS

# ❌ INVALID - NaN value
data = [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": float('nan')}  # Error: INVALID_VALUES
]

# ❌ INVALID - Duplicate labels
data = [
    {"label": "Q1", "value": 100},
    {"label": "Q1", "value": 200}  # Error: DUPLICATE_LABELS
]
```

---

## ⚠️ Error Handling

### **Structured Error Response**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_ANALYTICS_TYPE",
    "message": "Invalid analytics type: category_ranking",
    "category": "validation",
    "field": "analytics_type",
    "details": {
      "provided": "category_ranking",
      "allowed": [
        "revenue_over_time",
        "quarterly_comparison",
        "market_share",
        "yoy_growth",
        "kpi_metrics"
      ]
    },
    "retryable": false,
    "suggestion": "Use one of the supported analytics types: revenue_over_time, quarterly_comparison, market_share, yoy_growth, kpi_metrics"
  }
}
```

### **Error Categories**

| Category | HTTP Status | Retryable | Description |
|----------|-------------|-----------|-------------|
| validation | 400 | ✅ Yes (after fixing data) | User input errors |
| processing | 500 | ⚠️ Maybe | Internal processing errors |
| resource | 404 | ❌ No | Resource not found |
| rate_limit | 429 | ✅ Yes (with delay) | Rate limited |
| system | 500 | ⚠️ Maybe | System errors |

### **Common Error Codes**

| Error Code | When It Happens | Fix |
|-----------|----------------|-----|
| `INVALID_ANALYTICS_TYPE` | Using unsupported analytics_type | Use one of 5 supported types (9 in v3.1.3) |
| `INVALID_DATA_POINTS` | Less than 2 or more than 50 points | Provide 2-50 data points |
| `DUPLICATE_LABELS` | Duplicate labels in data | Ensure all labels are unique |
| `INVALID_VALUES` | NaN, Infinity, or non-numeric values | Use finite numbers only |

---

## 📋 Director Team Integration Guide

### **What Director Team Can Do Now (v3.1.2)**

#### 1. **Generate L02 Analytics Slides**
Use 5 supported analytics types:
```python
analytics_types = [
    "revenue_over_time",
    "quarterly_comparison",
    "market_share",
    "yoy_growth",
    "kpi_metrics"
]

for analytics_type in analytics_types:
    response = requests.post(
        f"https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "pres-123",
            "slide_id": f"slide-{analytics_type}",
            "slide_number": 1,
            "narrative": f"Show {analytics_type}",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 150}
            ]
        }
    )

    if response.status_code == 200:
        result = response.json()
        chart_html = result["content"]["element_3"]
        observations = result["content"]["element_2"]
        # Use in Layout Builder
```

#### 2. **Handle Errors Gracefully**
```python
response = requests.post(url, json=data)
if response.status_code != 200:
    error = response.json()["error"]

    # Check if retryable
    if error["retryable"]:
        print(f"Retryable error: {error['code']}")
        print(f"Suggestion: {error['suggestion']}")
        # Implement retry logic
    else:
        print(f"Permanent error: {error['code']}")
        print(f"Message: {error['message']}")
```

#### 3. **Validate Data Before Sending**
```python
def validate_analytics_data(data: List[Dict]) -> Tuple[bool, Optional[str]]:
    """Validate data before sending to Analytics Service."""

    # Check minimum points
    if len(data) < 2:
        return False, "Need at least 2 data points"

    # Check maximum points
    if len(data) > 50:
        return False, "Maximum 50 data points allowed"

    # Check for duplicates
    labels = [d["label"] for d in data]
    if len(labels) != len(set(labels)):
        return False, "Duplicate labels found"

    # Check for NaN/Infinity
    for point in data:
        if not isinstance(point["value"], (int, float)):
            return False, f"Invalid value type: {point['value']}"
        if point["value"] != point["value"]:  # NaN check
            return False, "NaN values not allowed"
        if abs(point["value"]) == float('inf'):
            return False, "Infinity values not allowed"

    return True, None
```

### **What Will Be Available in v3.1.3 (Within 24 hours)**

#### 1. **4 Additional Analytics Types**
```python
# NEW analytics types (deploy within 24 hours)
new_analytics_types = [
    "category_ranking",           # → bar_horizontal
    "correlation_analysis",       # → scatter
    "multidimensional_analysis",  # → bubble
    "multi_metric_comparison",    # → radar
    "radial_composition"          # → polar_area
]

# Total: 9 analytics types (up from 5)
```

#### 2. **Full Chart Type Coverage**
After v3.1.3 deployment:
- ✅ All 9 Chart.js types accessible via analytics_type
- ✅ All analytics types return element_3 and element_2 for L02
- ✅ Consistent label-value data format across all types

---

## 📊 Comparison: Documentation vs Reality

### **v3.1.2 Documentation Claims vs Reality**

| Claim in Original Docs | Reality | Status |
|------------------------|---------|--------|
| "9 analytics types supported" | Only 5 analytics types | ❌ FALSE |
| "13 chart types available" | 13 chart types in catalog | ✅ TRUE |
| "Choose any chart type" | Cannot specify chart_type directly | ❌ MISLEADING |
| "Scatter uses x-y format" | All charts use label-value format | ❌ FALSE |
| "Bubble uses x-y-r format" | All charts use label-value format | ❌ FALSE |
| "element_3 returned" | Only for L02 layout | ⚠️ INCOMPLETE |
| "Structured errors" | Yes, implemented correctly | ✅ TRUE |
| "Data validation" | Yes, implemented correctly | ✅ TRUE |

---

## 🚀 Version History

### **v3.1.2 (Current Production)**
- ✅ 5 analytics types
- ✅ 13 chart types in discovery catalog
- ✅ Comprehensive data validation
- ✅ Structured error responses
- ❌ Documentation inaccuracies

### **v3.1.3 (Deploying within 24 hours)**
- ✅ 9 analytics types (expanded from 5)
- ✅ Corrected documentation
- ✅ All Chart.js types accessible
- ✅ Analytics type to chart type mapping documented

---

## 📞 Support and Resources

### **Documentation Links**
- **Integration Guide**: [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md)
- **Chart Type Catalog**: [docs/CHART_TYPE_CATALOG.md](docs/CHART_TYPE_CATALOG.md)
- **Error Codes**: [docs/ERROR_CODES.md](docs/ERROR_CODES.md)
- **OpenAPI Docs**: https://analytics-v30-production.up.railway.app/docs

### **API Endpoints**
- **Production Base URL**: https://analytics-v30-production.up.railway.app
- **Health Check**: https://analytics-v30-production.up.railway.app/health
- **Chart Discovery**: https://analytics-v30-production.up.railway.app/api/v1/chart-types
- **Interactive Docs**: https://analytics-v30-production.up.railway.app/docs

---

## ✅ Acknowledgment of Director Team Findings

We acknowledge and thank the Director v3.4 team for their thorough compatibility testing, which uncovered these critical documentation discrepancies:

1. ✅ **Issue 1: Limited Analytics Type Support** - CONFIRMED and FIXING
2. ✅ **Issue 2: Data Schema Mismatch** - CONFIRMED and DOCUMENTED
3. ✅ **Issue 3: Missing Response Fields** - CLARIFIED (L02-specific)
4. ✅ **Issue 4: Documentation Inaccurate** - CONFIRMED and CORRECTED

**This document has been completely rewritten** to accurately reflect the Analytics Service implementation.

---

*For questions or issues, please refer to the documentation or contact the Analytics Service team.*
*Last Updated: November 17, 2025 - Post Director Team Compatibility Testing*
