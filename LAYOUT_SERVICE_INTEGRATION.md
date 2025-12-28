# Layout Service Chart Integration

**Document Path:** `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/LAYOUT_SERVICE_INTEGRATION.md`

This document describes the new Chart AI Service endpoint for Layout Service integration, including API specifications, usage examples, and integration guidelines.

---

## Overview

The Analytics Microservice v3.0 now includes a dedicated endpoint for the Layout Service to generate Chart.js configurations with grid-based sizing constraints. This endpoint returns pure Chart.js configuration objects optimized for client-side rendering.

**Key Features:**
- Grid-based sizing with automatic data point limits
- Minimum grid size enforcement per chart type
- 8 color palettes mapped to internal themes
- Optional synthetic data generation
- AI-generated insights (trend analysis, outliers)

---

## New Endpoints

### 1. Generate Chart

**Endpoint:** `POST /api/ai/chart/generate`

**Purpose:** Generate Chart.js configuration for Layout Service with grid-based constraints.

#### Request Schema

```typescript
interface ChartGenerateRequest {
  // Required
  prompt: string;                    // Description of chart data (1-2000 chars)
  chartType: ChartType;              // One of: bar, line, pie, doughnut, area, scatter, radar, polarArea
  presentationId: string;
  slideId: string;
  elementId: string;

  // Context
  context: {
    presentationTitle: string;
    slideTitle?: string;
    slideIndex: number;
    industry?: string;               // For realistic synthetic data
    timeFrame?: string;              // e.g., "Q1 2024", "2020-2024"
  };

  // Grid constraints (REQUIRED)
  constraints: {
    gridWidth: number;               // 1-12 grid units
    gridHeight: number;              // 1-8 grid units
  };

  // Optional configuration
  config?: {
    dataPoints?: number;             // Suggested number of data points
    datasets?: number;               // Number of series
    animated?: boolean;              // Enable animations (default: true)
    aspectRatio?: number;            // Width/height ratio
  };

  // Style options
  style?: {
    palette: ChartPalette;           // Color scheme (default: "default")
    customColors?: string[];         // Override with hex colors
    showLegend?: boolean;            // Show legend (default: true)
    legendPosition?: 'top' | 'bottom' | 'left' | 'right';
    showGrid?: boolean;              // Show grid lines (default: true)
    showDataLabels?: boolean;        // Show values on points (default: false)
  };

  // Axis configuration
  axes?: {
    xLabel?: string;
    yLabel?: string;
    yMin?: number;
    yMax?: number;
    stacked?: boolean;
  };

  // Data (provide one of these)
  data?: Array<{label: string, value: number}>;  // User-provided data
  generateData?: boolean;                         // Generate synthetic data if no data provided
}
```

#### Response Schema

```typescript
interface ChartGenerateResponse {
  success: boolean;
  data?: {
    generationId: string;

    // Chart.js configuration - ready to use with new Chart(ctx, config)
    chartConfig: {
      type: string;                  // Chart.js type
      data: {
        labels: string[];
        datasets: Array<{
          label: string;
          data: number[];
          backgroundColor: string | string[];
          borderColor: string | string[];
          borderWidth?: number;
          // ...type-specific options
        }>;
      };
      options: {
        responsive: boolean;
        maintainAspectRatio: boolean;
        plugins: {...};
        scales?: {...};
        animation?: {...};
      };
    };

    // Raw data in Chart.js format
    rawData: {
      labels: string[];
      datasets: Array<{label: string, data: number[]}>;
    };

    // Metadata
    metadata: {
      chartType: string;
      dataPointCount: number;
      datasetCount: number;
      suggestedTitle: string;
      dataRange: {
        min: number;
        max: number;
        average: number;
      };
    };

    // AI-generated insights
    insights?: {
      trend?: 'increasing' | 'decreasing' | 'stable' | 'volatile';
      outliers?: number[];           // Indices of outlier points
      highlights?: string[];         // Notable observations
    };
  };

  error?: {
    code: string;
    message: string;
    details?: object;
    retryable: boolean;
    suggestion?: string;
  };
}
```

---

### 2. Get Chart Constraints

**Endpoint:** `GET /api/ai/chart/constraints`

**Purpose:** Get minimum grid sizes and data limits for all chart types.

**Response Example:**
```json
{
  "success": true,
  "minimumGridSizes": {
    "bar": {"width": 3, "height": 3},
    "line": {"width": 3, "height": 2},
    "pie": {"width": 3, "height": 3},
    "doughnut": {"width": 3, "height": 3},
    "area": {"width": 3, "height": 2},
    "scatter": {"width": 4, "height": 3},
    "radar": {"width": 4, "height": 4},
    "polarArea": {"width": 3, "height": 3}
  },
  "dataLimits": {
    "bar": {
      "small": {"maxPoints": 4, "maxDatasets": 2},
      "medium": {"maxPoints": 8, "maxDatasets": 3},
      "large": {"maxPoints": 15, "maxDatasets": 5}
    }
    // ... other chart types
  },
  "gridRanges": {
    "width": {"min": 1, "max": 12},
    "height": {"min": 1, "max": 8}
  },
  "sizeThresholds": {
    "small": "area <= 16",
    "medium": "16 < area <= 48",
    "large": "area > 48"
  }
}
```

---

### 3. Get Available Palettes

**Endpoint:** `GET /api/ai/chart/palettes`

**Purpose:** Get all available color palettes.

**Response Example:**
```json
{
  "success": true,
  "palettes": [
    {
      "name": "default",
      "colors": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", ...],
      "internalTheme": "professional",
      "colorCount": 8
    },
    // ... 7 more palettes
  ],
  "defaultPalette": "default"
}
```

---

## Usage Examples

### Example 1: Bar Chart with User Data

```bash
curl -X POST http://localhost:8080/api/ai/chart/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show quarterly revenue growth",
    "chartType": "bar",
    "presentationId": "pres-123",
    "slideId": "slide-7",
    "elementId": "chart-1",
    "context": {
      "presentationTitle": "Q4 Business Review",
      "slideTitle": "Revenue Performance",
      "slideIndex": 6
    },
    "constraints": {
      "gridWidth": 8,
      "gridHeight": 4
    },
    "style": {
      "palette": "professional",
      "showLegend": true,
      "showDataLabels": true
    },
    "data": [
      {"label": "Q1", "value": 125000},
      {"label": "Q2", "value": 145000},
      {"label": "Q3", "value": 162000},
      {"label": "Q4", "value": 178000}
    ]
  }'
```

### Example 2: Line Chart with Synthetic Data

```bash
curl -X POST http://localhost:8080/api/ai/chart/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show monthly sales trend for technology sector",
    "chartType": "line",
    "presentationId": "pres-456",
    "slideId": "slide-2",
    "elementId": "chart-2",
    "context": {
      "presentationTitle": "Sales Report",
      "slideIndex": 1,
      "industry": "technology",
      "timeFrame": "2024"
    },
    "constraints": {
      "gridWidth": 10,
      "gridHeight": 6
    },
    "style": {
      "palette": "vibrant"
    },
    "generateData": true
  }'
```

### Example 3: Pie Chart

```bash
curl -X POST http://localhost:8080/api/ai/chart/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Market share distribution",
    "chartType": "pie",
    "presentationId": "pres-789",
    "slideId": "slide-3",
    "elementId": "chart-3",
    "context": {
      "presentationTitle": "Market Analysis",
      "slideIndex": 2
    },
    "constraints": {
      "gridWidth": 4,
      "gridHeight": 4
    },
    "style": {
      "palette": "categorical",
      "legendPosition": "right"
    },
    "data": [
      {"label": "Company A", "value": 35},
      {"label": "Company B", "value": 28},
      {"label": "Company C", "value": 22},
      {"label": "Others", "value": 15}
    ]
  }'
```

---

## Grid Constraints Reference

### Minimum Grid Sizes

| Chart Type | Min Width | Min Height | Notes |
|------------|-----------|------------|-------|
| bar        | 3         | 3          | Vertical bars |
| line       | 3         | 2          | Can be wider for more points |
| pie        | 3         | 3          | Requires square-ish aspect |
| doughnut   | 3         | 3          | Similar to pie |
| area       | 3         | 2          | Similar to line |
| scatter    | 4         | 3          | Needs space for axis labels |
| radar      | 4         | 4          | Requires square aspect |
| polarArea  | 3         | 3          | Similar to pie |

### Data Limits by Grid Size

Grid area is calculated as `gridWidth × gridHeight`.

| Size   | Area Range | Example Grids |
|--------|------------|---------------|
| Small  | ≤ 16       | 4×4, 3×5, 2×8 |
| Medium | 17-48      | 6×6, 8×5, 10×4 |
| Large  | > 48       | 8×8, 10×6, 12×5 |

**Data limits by chart type and size:**

| Chart Type | Small | Medium | Large |
|------------|-------|--------|-------|
| bar        | 4 pts | 8 pts  | 15 pts |
| line       | 6 pts | 12 pts | 24 pts |
| pie        | 4 slices | 6 slices | 8 slices |
| scatter    | 20 pts | 50 pts | 100 pts |
| radar      | 5 axes | 8 axes | 10 axes |

---

## Color Palettes

| Palette | Description | Best For |
|---------|-------------|----------|
| default | Standard blue-green-yellow-red | General use |
| professional | Dark corporate blues and greens | Business presentations |
| vibrant | Bold, saturated colors | Creative/modern designs |
| pastel | Soft, muted colors | Gentle visualizations |
| monochrome | Grayscale variations | Print-friendly |
| sequential | Light to dark blue gradient | Heat maps, progression |
| diverging | Red to green gradient | Positive/negative data |
| categorical | Distinct colors | Category comparisons |

---

## Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| INVALID_GRID_SIZE | Grid dimensions outside valid range | Yes |
| GRID_TOO_SMALL | Grid smaller than minimum for chart type | Yes |
| MISSING_DATA | No data provided and generateData=false | Yes |
| INVALID_DATA_POINTS | Invalid or insufficient data | Yes |
| CHART_GENERATION_FAILED | Internal generation error | No |

---

## Layout Service Integration Blurb

### For Layout Service Orchestrator

```typescript
/**
 * Chart AI Service Client
 *
 * Generates Chart.js configurations for grid-based canvas elements.
 *
 * Base URL: https://analytics-v30-production.up.railway.app
 * (or your deployed instance)
 *
 * Integration Steps:
 *
 * 1. VALIDATE GRID SIZE before calling generate:
 *    - Fetch /api/ai/chart/constraints on startup
 *    - Check minimumGridSizes[chartType] before allowing resize
 *    - Use this to lock minimum sizes in the UI
 *
 * 2. CALL GENERATE when user creates/updates chart element:
 *    - POST /api/ai/chart/generate with grid constraints
 *    - Response contains ready-to-use Chart.js config
 *
 * 3. RENDER CLIENT-SIDE using Chart.js 4.x:
 *    - const chart = new Chart(canvasCtx, response.data.chartConfig)
 *    - Store generationId for future updates
 *
 * 4. HANDLE ERRORS gracefully:
 *    - Check response.success
 *    - Show error.suggestion to user if retryable
 *    - Fall back to placeholder if not retryable
 */

interface ChartServiceConfig {
  baseUrl: string;
  timeout: number;  // Recommend 30000ms
}

async function generateChart(
  request: ChartGenerateRequest,
  config: ChartServiceConfig
): Promise<ChartGenerateResponse> {
  const response = await fetch(`${config.baseUrl}/api/ai/chart/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(config.timeout)
  });

  return response.json();
}

// Example integration in Layout Service orchestrator
async function handleChartElementCreate(element: CanvasElement) {
  const response = await generateChart({
    prompt: element.userPrompt,
    chartType: element.selectedChartType,
    presentationId: element.presentationId,
    slideId: element.slideId,
    elementId: element.id,
    context: {
      presentationTitle: element.presentation.title,
      slideIndex: element.slideIndex
    },
    constraints: {
      gridWidth: element.gridWidth,
      gridHeight: element.gridHeight
    },
    style: {
      palette: element.selectedPalette || 'default'
    },
    data: element.userData,
    generateData: !element.userData || element.userData.length === 0
  }, chartServiceConfig);

  if (response.success) {
    // Render chart client-side
    const canvas = document.getElementById(element.canvasId);
    const chart = new Chart(canvas, response.data.chartConfig);

    // Store for later reference
    element.chartInstance = chart;
    element.generationId = response.data.generationId;
    element.chartMetadata = response.data.metadata;
    element.chartInsights = response.data.insights;
  } else {
    // Handle error
    console.error('Chart generation failed:', response.error);
    showErrorToUser(response.error.suggestion || response.error.message);
  }
}
```

---

## Files Created/Modified

**Base Directory:** `/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/`

### New Files Created

1. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/layout_service_models.py`**

   Pydantic models for request/response:
   - `ChartGenerateRequest` - Main request model
   - `ChartGenerateResponse` - Main response model
   - `ChartType`, `ChartPalette` enums
   - Supporting models for context, constraints, style, axes

2. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/layout_service_constraints.py`**

   Grid constraint logic:
   - `MINIMUM_GRID_SIZES` - Min size per chart type
   - `DATA_LIMITS` - Data point limits by size
   - `get_layout_size()` - Calculate small/medium/large
   - `validate_grid_size()` - Validate grid meets minimum
   - `truncate_data_to_limits()` - Enforce data limits

3. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/layout_service_palette.py`**

   Color palette mapping:
   - `FRONTEND_PALETTES` - 8 color palettes from spec
   - `PALETTE_TO_THEME` - Map to internal themes
   - `get_palette_colors()` - Get colors for chart
   - `get_chart_colors_for_type()` - Type-specific colors

4. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/LAYOUT_SERVICE_INTEGRATION.md`**

   This documentation file with:
   - Complete API specifications
   - Request/response schemas
   - Usage examples with curl commands
   - Grid constraints reference tables
   - Color palettes documentation
   - Layout Service integration guide and code samples

### Modified Files

1. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/rest_server.py`**

   Added new endpoints (lines 1311-1827):
   - `POST /api/ai/chart/generate` - Main chart generation endpoint
   - `GET /api/ai/chart/constraints` - Get grid constraints
   - `GET /api/ai/chart/palettes` - Get available palettes
   - Helper functions: `_build_layout_service_chartjs_config()`, `_generate_suggested_title()`, `_analyze_data_for_insights()`

2. **`/Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice/v3.0/error_codes.py`**

   Added new error codes (lines 28-33):
   - `INVALID_GRID_SIZE`
   - `GRID_TOO_SMALL`
   - `MISSING_DATA`
   - `INVALID_PALETTE`
   - `DATA_LIMIT_EXCEEDED`

---

## Testing

All endpoints have been tested with the following scenarios:

1. **Bar chart with user data** - ✅ Pass
2. **Pie chart with categorical palette** - ✅ Pass
3. **Line chart with synthetic data** - ✅ Pass
4. **Grid size validation (too small)** - ✅ Pass (returns proper error)
5. **Constraints endpoint** - ✅ Pass
6. **Palettes endpoint** - ✅ Pass

---

## Deployment Notes

The new endpoints are part of the existing Analytics Microservice v3.0 and will be available at:

- **Production:** `https://analytics-v30-production.up.railway.app/api/ai/chart/*`
- **Local:** `http://localhost:8080/api/ai/chart/*`

No additional deployment steps required beyond the standard deployment process.
