# Chart Rendering CDN Requirements for Layout Service

**Issue**: Charts render in L02 but not in C3, V2, L25 and other templates.

**Root Cause**: The following CDN libraries and plugin registration must be included in the HTML `<head>` or before `</body>` for Chart.js charts to render.

---

## Required Script Includes (Copy-Paste Ready)

```html
<!-- ApexCharts Library (for Analytics charts) -->
<script src="https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js"></script>

<!-- Chart.js + Plugins (for Analytics charts) -->
<!-- Chart.js 4.4.0 UMD bundle - fixes scatter chart pointStyle:"cross" rendering bug present in 3.x -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

<!-- D3.js Library (for d3_sunburst, d3_treemap, d3_choropleth charts) -->
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

<!-- Chart.js Extended Chart Type Plugins -->
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2.0.1/dist/chartjs-chart-matrix.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.0/dist/chartjs-chart-financial.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.11.0/dist/chartjs-chart-sankey.min.js"></script>

<!-- Register Datalabels Plugin with Chart.js -->
<script>
  if (typeof Chart !== 'undefined' && typeof ChartDataLabels !== 'undefined') {
    Chart.register(ChartDataLabels);
    console.log('✅ ChartDataLabels plugin registered globally');
  } else {
    console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
  }
</script>

<!-- Reveal.js Chart Plugin (for slide lifecycle management) -->
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
```

---

## Templates Status

| Template | Status | Notes |
|----------|--------|-------|
| L02 | ✅ Working | Has all CDN includes |
| C3-chart | ❌ Not working | Needs CDN includes added |
| V2-chart-text | ❌ Not working | Needs CDN includes added |
| L25 | ❌ Not working | Needs CDN includes added |
| Any chart-capable template | ❌ Check | Should have CDN includes |

---

## Chart Types Supported

| Library | Chart Types |
|---------|------------|
| **Chart.js** | line, bar, pie, doughnut, scatter, bubble, radar, polar_area |
| **Chart.js Plugins** | treemap, matrix, boxplot, financial, sankey |
| **D3.js** | d3_treemap, d3_sunburst, d3_choropleth_usa |
| **ApexCharts** | Additional chart types |

---

## CDN Library Summary

| Library | Version | CDN URL | Purpose |
|---------|---------|---------|---------|
| ApexCharts | 3.45.0 | `https://cdn.jsdelivr.net/npm/apexcharts@3.45.0/dist/apexcharts.min.js` | ApexCharts-based analytics |
| Chart.js | 4.4.0 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` | Core charting (UMD bundle) |
| ChartDataLabels | 2.2.0 | `https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0` | Data labels on charts |
| D3.js | 7 | `https://cdn.jsdelivr.net/npm/d3@7` | D3 charts (sunburst, choropleth) |
| Treemap Plugin | 2.3.0 | `https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@2.3.0/dist/chartjs-chart-treemap.min.js` | Treemap charts |
| Matrix Plugin | 2.0.1 | `https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2.0.1/dist/chartjs-chart-matrix.min.js` | Matrix/heatmap charts |
| Box Plot Plugin | 3.0.0 | `https://cdn.jsdelivr.net/npm/chartjs-chart-box-and-violin-plot@3.0.0/dist/chartjs-chart-box-and-violin-plot.min.js` | Box plots |
| Financial Plugin | 0.1.0 | `https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.0/dist/chartjs-chart-financial.min.js` | Candlestick/OHLC charts |
| Sankey Plugin | 0.11.0 | `https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.11.0/dist/chartjs-chart-sankey.min.js` | Sankey diagrams |
| Reveal.js Chart | latest | `https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js` | Slide lifecycle management |

---

## Implementation Notes

1. **Script Order Matters**: Chart.js must load before plugins, and plugins must load before the registration script.

2. **Plugin Registration**: The `Chart.register(ChartDataLabels)` call is essential - without it, data labels won't appear on charts.

3. **UMD Bundle**: Use `chart.umd.min.js` (not `chart.min.js`) to fix the scatter chart `pointStyle:"cross"` rendering bug in Chart.js 3.x.

4. **Reveal.js Integration**: The chart plugin handles chart lifecycle (init/destroy) during slide transitions to replay animations.

---

## Reference

- Working example: `analytics_microservice/v3.0/docs/L_25reference_html.html`
- Analytics Service: `https://analytics-v30-production.up.railway.app`
- Layout Service: `https://web-production-f0d13.up.railway.app`

---

*Last updated: 2025-12-27*
