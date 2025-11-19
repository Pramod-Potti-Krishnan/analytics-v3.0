# Analytics Microservice v3 - Comprehensive Codebase Summary

**Date**: November 18, 2025
**Current Version**: 3.4.3
**Status**: Production Ready - Chart Type Expansion Complete
**Production URL**: https://analytics-v30-production.up.railway.app
**Repository**: agents/analytics_microservice_v3

---

## Executive Summary

The Analytics Microservice v3 is a mature, production-ready REST API that generates comprehensive charts and visualizations with Chart.js 4.4.0 and official plugins. It supports **20+ chart types** including advanced visualizations (treemaps, heatmaps, boxplots, candlestick, sankey) with AI-generated insights for presentation slides. The service is fully integrated with the Director Agent using a Text Service-compatible API pattern and provides interactive, self-contained HTML charts with Reveal.js animation support.

**Key Achievement**: Successfully progressed from v3.1.x (9 analytics types) through v3.4.x (native + plugin-based chart expansion), with recent major releases focusing on chart type expansion and Editor improvements.

---

## Version History: v3.2.x → v3.4.x

### Recent Version Timeline

| Version | Date | Key Changes | Status |
|---------|------|------------|--------|
| **v3.4.3** | Nov 18 | Phase 4: Candlestick + Sankey charts, full Chart.js plugin ecosystem | ✅ Production |
| **v3.4.2** | Nov 17 | Phase 3: Heatmap/Matrix + Boxplot statistical charts | ✅ Production |
| **v3.4.1** | Nov 16 | Phase 2: Treemap chart for hierarchical data | ✅ Production |
| **v3.4.0** | Nov 16 | Phase 1: Native Chart.js types (Area, Stacked Area, Waterfall) | ✅ Production |
| **v3.3.5** | Nov 15 | Reduce Key Insights to 5-6 bullets (reduced from 7) | ✅ Production |
| **v3.3.4** | Nov 14 | Enable chart animation replay on every page load | ✅ Production |
| **v3.3.3** | Nov 13 | Fix Key Insights truncation and chart padding | ✅ Production |
| **v3.3.1** | Nov 12 | Fix grid lines visibility and Key Insights formatting | ✅ Production |
| **v3.3.0** | Nov 11 | Comprehensive chart improvements (legends, insights, scatter, bubble) | ✅ Production |
| **v3.2.2** | Nov 10 | Fix save button regression in scatter/bubble editor | ✅ Production |
| **v3.2.1** | Nov 09 | Fix scatter/bubble chart editor - X,Y columns with populated data | ✅ Production |
| **v3.2.0** | Nov 08 | Fix enforcement bug & add X marks for scatter charts | ✅ Production |

### Major Releases Summary

**v3.2.0 - v3.2.2: Editor Stabilization**
- Fixed scatter/bubble chart editor showing empty tables
- Corrected column headers (X, Y for scatter; X, Y, Radius for bubble)
- Fixed save button functionality
- X marks (pointStyle: "cross") implementation for scatter charts

**v3.3.0 - v3.3.5: Presentation Quality**
- Comprehensive improvements to legends and chart visibility
- AI-generated Key Insights with 5-6 bullet formatting (responsive to content width)
- Grid line visibility fixes
- Chart animation replay mechanism for Reveal.js integration
- Character limit enforcement (800 chars for L02 layout)

**v3.4.0 - v3.4.3: Chart Type Expansion (Phase-Based Rollout)**
- **Phase 1 (v3.4.0)**: Native Chart.js types
  - Area chart (line with filled region)
  - Stacked Area chart (cumulative visualization)
  - Waterfall chart (incremental changes)

- **Phase 2 (v3.4.1)**: Hierarchical Data
  - Treemap (chartjs-chart-treemap@3.1.0)
  - Use case: Budget breakdown, disk usage, organizational hierarchy

- **Phase 3 (v3.4.2)**: Statistical Analysis
  - Heatmap/Matrix (chartjs-chart-matrix@3.0.0)
  - Boxplot (@sgratzl/chartjs-chart-boxplot@4.4.5)
  - Use cases: Correlation analysis, statistical distributions

- **Phase 4 (v3.4.3)**: Financial & Flow
  - Candlestick (chartjs-chart-financial@0.2.1)
  - Sankey (chartjs-chart-sankey@0.12.0)
  - Use cases: Stock prices, resource flows, user journeys

---

## New Chart Types Added (v3.4.0 - v3.4.3)

### Overview: 20+ Total Supported Chart Types

**Native Chart.js (9 types)**
```
1. bar_vertical          - Standard vertical bar chart
2. bar_horizontal        - Horizontal bar chart for rankings
3. bar_grouped           - Multi-series grouped comparison
4. bar_stacked           - Part-to-whole relationships
5. line                  - Time series trends
6. line_multi            - Multiple time series comparison
7. pie                   - Proportional data (simple)
8. donut                 - Proportional data (with cutout)
9. radar                 - Multivariate comparison
10. polar_area           - Cyclical/directional data
```

**Advanced Chart.js (5 NEW types in v3.4.x)**
```
11. area                 - Line chart with filled area [NEW v3.4.0]
12. area_stacked         - Cumulative area visualization [NEW v3.4.0]
13. waterfall           - Incremental changes (up/down flow) [NEW v3.4.0]
14. scatter             - Correlation analysis (X,Y points)
15. bubble              - 3-variable relationships (X,Y,Radius)
```

**Chart.js Plugin-Based (6 NEW types in v3.4.x)**
```
16. treemap             - Hierarchical data breakdown [NEW v3.4.1]
                          Plugin: chartjs-chart-treemap@3.1.0
                          Use: Budget allocation, disk usage, org hierarchy

17. heatmap/matrix      - 2D correlation data [NEW v3.4.2]
                          Plugin: chartjs-chart-matrix@3.0.0
                          Use: Correlation matrices, calendar heatmaps, time patterns

18. boxplot             - Statistical distribution [NEW v3.4.2]
                          Plugin: @sgratzl/chartjs-chart-boxplot@4.4.5
                          Use: Outlier detection, quartile visualization, variance analysis

19. candlestick         - OHLC financial data [NEW v3.4.3]
                          Plugin: chartjs-chart-financial@0.2.1
                          Dependencies: luxon@3.3.0, chartjs-adapter-luxon@1.3.1
                          Use: Stock prices, forex data, market analysis

20. sankey              - Flow/alluvial visualization [NEW v3.4.3]
                          Plugin: chartjs-chart-sankey@0.12.0
                          Use: Resource flows, user journeys, budget allocation, energy flow
```

**Specialized Types (2 types)**
```
21. mixed               - Combo chart (multiple types)
22. histogram           - Distribution analysis
```

### Implementation Details

**Treemap (v3.4.1)**
- Lines 929-1070 in chartjs_generator.py
- Transforms flat data into hierarchical structure
- Built with chartjs-chart-treemap@3.1.0 CDN plugin
- Self-contained HTML with embedded plugin script

**Heatmap/Matrix (v3.4.2)**
- Lines 1072-1252 in chartjs_generator.py
- Converts label-value pairs into 2D grid data
- Supports color gradients for correlation visualization
- Uses chartjs-chart-matrix@3.0.0 plugin

**Boxplot (v3.4.2)**
- Lines 1254-1401 in chartjs_generator.py
- Generates statistical distribution with quartiles
- Calculates min, Q1, median, Q3, max from data
- Uses @sgratzl/chartjs-chart-boxplot@4.4.5 plugin

**Candlestick (v3.4.3)**
- Lines 1403-1614 in chartjs_generator.py
- Requires OHLC data format (Open, High, Low, Close)
- Dual dependencies: luxon for date handling, financial plugin
- Time-indexed data with proper date formatting

**Sankey (v3.4.3)**
- Lines 1616-1770+ in chartjs_generator.py
- Flow visualization for resource/user journey tracking
- Supports weighted flows between source→target nodes
- chartjs-chart-sankey@0.12.0 plugin

---

## Current Architecture

### Core Components

```
analytics_microservice_v3/
├── agent.py                 [35KB] Main orchestration (direct implementation, no Pydantic)
├── chartjs_generator.py     [133KB] Chart generation with all 20+ types (3076 lines)
├── insight_generator.py     [13KB] LLM-powered business insights
├── layout_assembler.py      [7.5KB] L02 layout HTML assembly
├── rest_server.py           [30KB] FastAPI REST API endpoints
├── job_manager.py           [5.7KB] Async job tracking and cleanup
├── storage.py               [4.2KB] Supabase Storage integration
├── analytics_types.py       [4.8KB] Chart type metadata and dimensions
├── dependencies.py          [6.2KB] Dependency injection
├── providers.py             [533B] OpenAI client configuration
├── settings.py              [4.2KB] Environment configuration
├── tools.py                 [24KB] Chart generation tools
├── prompts.py               [1.5KB] System prompts
└── main.py                  [370B] Entry point
```

### Architecture Decisions

**Direct Implementation (No Pydantic AI)**
- Agent.py implements orchestration without Pydantic AI framework
- Direct async function calls: data synthesis → chart generation → insight → layout assembly
- Simpler control flow, easier debugging
- Explicit progress tracking

**Chart.js 4.4.0 Foundation**
- Moved away from ApexCharts for core functionality
- Native Chart.js + official plugins for extensibility
- Self-contained HTML with embedded CDN scripts
- No global dependencies needed per chart

**Synchronous Analytics API (v3.1.8+)**
- `/api/v1/analytics/{layout}/{analytics_type}` endpoints
- Immediate JSON response with chart HTML (no job polling)
- Text Service-compatible format for Director integration
- Supports L01, L02, L03 layouts

**Three Layout Types**
```
L01: Centered chart + insight below (1800×600 chart + body text)
L02: Chart + observations (1260×720 chart + 540×720 text panel)
L03: Side-by-side comparison (2×840×540 charts + descriptions)
```

---

## Integration: Director Agent

### Quick Start Example

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
            "audience": "executives",
            "slide_title": "Quarterly Revenue Growth",
            "subtitle": "FY 2024 Performance",
            "presentation_name": "Board Review Q4 2024"
        }
    }
)

result = response.json()
chart_html = result["content"]["element_4"]           # Chart (1260×720px)
observations = result["content"]["element_2"]         # Observations panel
```

### 9 Supported Analytics Types

```
1. revenue_over_time        - Line chart trend
2. quarterly_comparison     - Bar chart comparison
3. market_share            - Pie/donut distribution
4. yoy_growth              - Year-over-year bars
5. kpi_metrics             - Doughnut multi-metric
6. category_ranking        - Horizontal bar ranking
7. correlation_analysis    - Scatter plot
8. multidimensional_analysis - Bubble chart
9. multi_metric_comparison - Radar multivariate
```

### Key Features

- ✅ **Synchronous Response** - No job polling needed
- ✅ **AI-Generated Insights** - GPT-4o-mini powered analysis
- ✅ **Reveal.js Integration** - Charts animate on slide change
- ✅ **Self-Contained HTML** - Complete CDN scripts embedded
- ✅ **Interactive Charts** - Hover tooltips, zoom, pan
- ✅ **Theme Support** - Colors match presentation theme
- ✅ **Batch Endpoint** - `/api/v1/analytics/batch` for multiple slides

---

## Key Recent Improvements

### v3.4.x: Chart Type Expansion Strategy

**Phased Rollout Approach**
1. **Phase 1 (v3.4.0)**: Core native types (Area, Waterfall)
2. **Phase 2 (v3.4.1)**: Hierarchical visualization (Treemap)
3. **Phase 3 (v3.4.2)**: Statistical analysis (Heatmap, Boxplot)
4. **Phase 4 (v3.4.3)**: Financial & Flow (Candlestick, Sankey)

**Rationale**: Incremental rollout reduced risk, allowed testing of plugin infrastructure, maintained production stability.

### v3.3.x: Presentation Quality Refinements

**Key Insights Optimization (v3.3.5)**
- Reduced from 7 to 6 maximum bullets
- Each bullet: 95-133 characters (optimized for one-page layout)
- Total response: 800 character max (down from 1000)
- Reason: Improved readability on slide layouts

**Chart Animation Replay (v3.3.4)**
- Charts re-animate every time slide becomes active
- Reveal.js event integration: `Reveal.on('slidechanged', ...)`
- Fallback for non-Reveal.js contexts
- Enhanced visual engagement

**Grid Line Visibility (v3.3.1)**
- Fixed buried Y-axis labels and grid
- Removed double-wrapping containers
- Proper chart padding configuration
- Increased grid opacity

### v3.2.x: Scatter/Bubble Chart Editor Fixes

**Editor Chart-Type Awareness (v3.2.1)**
- Dynamic table headers based on chart type:
  - Scatter: X, Y columns
  - Bubble: X, Y, Radius columns
  - Others: Label, Value columns
- Fixed empty table issue for scatter/bubble
- Populated data rows from chart configuration

**Scatter Chart Visual Fix (v3.2.0)**
- Implemented `pointStyle: "cross"` for scatter point markers
- X-marks (plus-shaped) point visualization
- Proper contrast against backgrounds
- Different from bubble chart circles

---

## Current Issues & Action Items

### From ANALYTICS_TEAM_ACTION_REQUIRED.md

**Priority: MEDIUM - Scatter Chart Testing Required**

**Status**: Layout Service fix deployed to branch `fix/scatter-chart-chartjs-upgrade`

**What Happened**:
- Scatter charts appeared blank when rendered in Layout Service
- Root cause: Layout Service using Chart.js 3.9.1 with bug in `pointStyle: "cross"` rendering
- Analytics Service correctly generates cross-marked points (for Chart.js 4.x compatibility)

**Required Actions**:
1. ✅ Wait for Layout Service to deploy Chart.js 4.4.0 upgrade
2. ✅ Test scatter charts via `POST /api/v1/analytics/L02/correlation_analysis`
3. ✅ Verify X-marks are visible and correctly positioned
4. ✅ Run regression tests on all 9 chart types
5. ✅ Check browser console for Chart.js 4.4.0 version

**Testing Checklist**:
- [ ] Basic scatter chart rendering (5 points)
- [ ] Medium dataset (15 points)
- [ ] Large dataset (30+ points)
- [ ] Multiple scatter charts in presentation
- [ ] Scatter vs Bubble chart comparison (regression)
- [ ] Browser console: Chart.js version 4.4.0
- [ ] Browser console: No errors
- [ ] Datalabels plugin registered successfully

**What Analytics Team Does NOT Need to Do**:
- ❌ No code changes in Analytics Service
- ❌ No configuration changes
- ❌ No deployment required
- ❌ Analytics Service scatter generation was already correct!

---

## Component Deep Dive

### chartjs_generator.py (3076 lines, 133KB)

**Structure**:
- Lines 1-100: Imports, class definition
- Lines 100-900: Basic chart generators (bar, line, pie, radar, polar_area)
- Lines 203-280: Area and stacked area charts
- Lines 425-530: Waterfall chart
- Lines 600+: Core chart configuration and HTML output
- Lines 929-1070: Treemap chart with plugin
- Lines 1072-1252: Heatmap/matrix chart with plugin
- Lines 1254-1401: Boxplot chart with plugin
- Lines 1403-1614: Candlestick chart with plugin
- Lines 1616+: Sankey chart with plugin
- Lines 2000+: Canvas HTML generation, datalabels plugin integration
- Lines 2300+: Interactive editor implementation
- Lines 2700+: Data transformation utilities

**Key Functions**:
- `generate_chart_html()` - Main entry point
- `generate_[type]_chart()` - Per-chart-type generators
- `build_chart_html()` - HTML canvas construction
- `add_datalabels_config()` - Data labels plugin setup
- `generate_editor_html()` - Interactive editor creation

**Plugin Management**:
- CDN script injection for each plugin
- Per-chart plugin loading
- Fallback patterns if plugin unavailable
- Version pinning (treemap@3.1.0, matrix@3.0.0, etc.)

### insight_generator.py (349 lines)

**Core Methods**:
- `generate_l01_insight()` - Concise 2-3 sentence insight (max 150 words)
- `generate_l02_explanation()` - Detailed 5-6 bullet points (max 800 chars)
- `generate_l03_descriptions()` - Paired short descriptions (20-30 words each)
- `_summarize_data()` - Create LLM context from data
- `_generate_fallback_insight()` - Fallback when LLM fails

**LLM Configuration**:
- Model: GPT-4o-mini
- Temperature: 0.7 (balanced creativity)
- Max tokens: 200 (L01), variable (L02), 60 (L03)

**Prompt Engineering**:
- Audience-aware phrasing (executives, managers, analysts)
- Format requirements (bullet count, character limits)
- Specific number usage from data
- Active voice, professional tone

### layout_assembler.py (218 lines)

**Purpose**: Assemble L02 layout HTML with two sections

**Dimensions**:
- Chart (element_3): 1260×720px (70% of content area)
- Observations (element_2): 540×720px (30% of content area)

**Key Methods**:
- `assemble_l02_layout()` - Main entry point
- `assemble_chart_html()` - Chart container assembly
- `assemble_observations_html()` - Observations panel assembly

**Theme Colors**:
- professional: #f8f9fa bg, #1f2937 heading, #374151 text
- corporate: #f3f4f6 bg, #111827 heading, #4b5563 text
- vibrant: #fef3c7 bg, #78350f heading, #92400e text

---

## Testing & Quality

### Test Files in Directory

```
test_all_9_types.py                      - All analytics types
test_analytics_type_mapping.py           - Type routing
test_chartjs_type_validation.py          - Chart.js types
test_director_simulation.py              - Director integration
test_editor_v321.py                      - Editor functionality
test_production_*.py (multiple)          - Version-specific tests
test_scatter_chart_fix.py                - Scatter chart validation
test_v3*.py                              - Version regression tests
```

### Test Coverage

- ✅ All 9 analytics types
- ✅ All 20+ chart types
- ✅ Editor functionality (scatter, bubble, others)
- ✅ Director integration patterns
- ✅ Theme rendering
- ✅ Data transformation
- ✅ Layout assembly
- ✅ Plugin loading

---

## Deployment & Operations

### Production URL

```
Base: https://analytics-v30-production.up.railway.app
Health: GET /health
Stats: GET /stats
Docs: GET /docs (OpenAPI)
```

### Endpoints Summary

**Analytics API (Text Service Pattern)**
- `POST /api/v1/analytics/{layout}/{analytics_type}`
- `POST /api/v1/analytics/batch`

**Legacy API (PNG Generation)**
- `POST /generate`
- `GET /status/{job_id}`
- `GET /health`
- `GET /stats`

**Chart Type Discovery**
- `GET /api/v1/chart-types`
- `GET /api/v1/chart-types/{engine}`
- `GET /api/v1/chart-types/{chart_type}`

### Environment Variables

```
OPENAI_API_KEY              - OpenAI API key (required)
SUPABASE_URL                - Supabase project URL (required)
SUPABASE_KEY                - Service role key (required)
SUPABASE_BUCKET             - Storage bucket (default: analytics-charts)
API_PORT                    - Server port (default: 8080)
JOB_CLEANUP_HOURS           - Auto-cleanup timeout (default: 1)
CHART_GENERATION_TIMEOUT    - Generation timeout (default: 30s)
MAX_CHART_SIZE_MB           - Size limit (default: 10MB)
RAILWAY_ENVIRONMENT         - deployment env (development/production)
LOG_LEVEL                   - Logging level (default: INFO)
```

### Railway Deployment

- Uses Dockerfile
- Docker image: python:3.11-slim
- Restart policy: ON_FAILURE with max 10 retries
- Health checks: `/health` endpoint

---

## Known Limitations & Future Considerations

### Current Limitations

1. **Plugin Dependencies**: Advanced charts require CDN-loaded plugins
   - Increases initial load time
   - Requires internet connectivity for CDN
   - Fallback patterns not yet implemented for offline use

2. **Scatter/Bubble Data Format**: Object-based data structure
   - Differs from standard label-value pattern
   - Editor complexity for chart-type-aware UI
   - Not all director requests may understand X,Y format

3. **Candlestick Data Requirements**: OHLC format specific
   - Requires pre-formatted financial data
   - Dual dependencies (luxon for date handling)
   - Not auto-synthesizable from generic narratives

4. **Sankey Complexity**: Flow definition requires source→target structure
   - Data synthesis for flow diagrams is challenging
   - Narrative-to-flow conversion not yet automated

### Potential Improvements

1. **Cached Plugin Loading**: Pre-load common plugins at startup
2. **Offline Fallback**: Static plugin bundles as backup
3. **Chart Type Auto-Selection**: AI-driven chart recommendation from data
4. **Advanced Filtering**: Data range limits, outlier detection
5. **Real-time Updates**: WebSocket support for live chart updates
6. **Animation Control**: Granular animation timing options
7. **Accessibility**: ARIA labels, keyboard navigation for all charts

---

## Key Metrics & Status

### Service Health

```
Version Status:          ✅ v3.4.3 Production Ready
Chart Types:             ✅ 20+ types with plugins
Analytics Types:         ✅ 9 types with Director integration
Layout Support:          ✅ L01, L02, L03
LLM Integration:         ✅ GPT-4o-mini insights
Animation Support:       ✅ Reveal.js compatible
Editor Support:          ✅ Scatter, Bubble, Bar, Line, Pie
Test Coverage:           ✅ Comprehensive across versions
```

### Performance Targets

- Chart generation: <3 seconds
- Insight generation: <2 seconds
- Total response: <5 seconds
- Concurrent requests: 100+
- Job cleanup: 1 hour (configurable)

---

## Summary Statistics

- **Total Lines of Code**: ~11,000 (including tests)
- **Production Versions**: 20+ (from v3.1.4 to v3.4.3)
- **Chart Types Supported**: 20+ (native + plugins)
- **Analytics Types**: 9
- **Layout Templates**: 3 (L01, L02, L03)
- **Plugin Dependencies**: 5 (treemap, matrix, boxplot, financial, sankey)
- **Test Files**: 15+
- **Deployment**: Railway.app
- **Framework**: FastAPI (REST) + Chart.js 4.4.0

---

## Conclusion

Analytics Microservice v3 has evolved from a basic chart generation service (v3.1.x) into a sophisticated, production-ready analytics platform with:

1. **Comprehensive Chart Support**: 20+ types covering data visualization needs from simple bars to complex flow diagrams
2. **Enterprise Integration**: Director Agent compatible with synchronous API and Text Service pattern
3. **AI-Enhanced Content**: LLM-powered business insights tailored to audience and layout
4. **Quality Polish**: Multiple refinement cycles addressing presentation quality, editor functionality, and visual fidelity
5. **Robust Architecture**: Direct implementation avoiding unnecessary complexity, clear separation of concerns

The phased rollout strategy for new chart types (Phases 1-4 in v3.4.x) demonstrates a mature engineering approach, balancing feature expansion with production stability. The recent focus on Editor improvements and scatter chart fixes shows responsiveness to user feedback and commitment to production reliability.

**Ready for**: Advanced analytics scenarios, financial data visualization, complex hierarchical data, statistical analysis, and resource flow tracking.

