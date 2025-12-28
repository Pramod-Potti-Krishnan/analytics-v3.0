
Step 4: 

Here is a copy of the complete code I got when I clicked on inspect element and opened the ‘Elements’ section in console:
<!DOCTYPE html>
<html lang="en" class="reveal-full-page"><head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fix Verification - bar_grouped - Regional Performance</title>

  <!-- Reveal.js Core -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">

  <!-- v7.5 Styles -->
  <link rel="stylesheet" href="/src/styles/core/reset.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/grid-system.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/borders.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/content-area.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/edit-mode.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/review-mode.css?v=20250124">
  <link rel="stylesheet" href="/src/styles/regeneration-panel.css?v=20250124">

  <style>
    /* Minimal additional styling */
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }

    .reveal {
      background: #ffffff;
    }

    /* Help text */
    #help-text {
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.8);
      color: white;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      z-index: 10000;
      opacity: 0;
      transition: opacity 0.3s;
    }

    #help-text.show {
      opacity: 1;
    }
  </style>
<style>
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
</style></head>
<body class="reveal-viewport" style="--slide-width: 1920px; --slide-height: 1080px; --slide-scale: 0.765625;">
  <!-- Help Text -->
  <div id="help-text" class="">
    Press 'R' for review mode | 'E' for edit mode | 'G' for grid | 'B' for borders | '?' for help
  </div>

  <!-- Edit Mode UI -->
  <button id="toggle-edit-mode" onclick="toggleEditMode()">✏️ Edit Mode</button>

  <div id="edit-controls">
    <button id="save-btn" onclick="saveAllChanges()" title="Save Changes">💾</button>
    <button id="cancel-btn" onclick="cancelEdits()" title="Cancel">❌</button>
    <button id="view-history-btn" onclick="showVersionHistory()" title="Version History">📋</button>
  </div>

  <div id="edit-notification"></div>

  <div class="edit-shortcuts">
    <div><kbd>E</kbd> Toggle Edit Mode</div>
    <div><kbd>Ctrl+S</kbd> Save Changes</div>
    <div><kbd>ESC</kbd> Cancel</div>
  </div>

  <!-- Selection Indicator -->
  <div id="selection-indicator" class="selection-indicator"></div>

  <!-- AI Regeneration Panel -->
  <div id="regeneration-panel">
    <h3>🤖 AI Regeneration</h3>
    <div class="input-group">
      <input type="text" id="ai-instruction-input" placeholder="Enter instruction (e.g., Make it more engaging with examples)">
      <button id="regenerate-btn" onclick="regenerateSelectedSections()">
        Regenerate with AI
      </button>
      <button id="cancel-selection-btn" onclick="clearSelection()">
        Cancel
      </button>
    </div>
  </div>

  <!-- Reveal.js Container -->
  <div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>

  <!-- Reveal.js Core -->
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

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
      console.log('✅ Chart.js extended plugins loaded:', {
        treemap: typeof TreemapController !== 'undefined',
        matrix: typeof MatrixController !== 'undefined',
        boxplot: typeof BoxPlotController !== 'undefined',
        financial: typeof CandlestickController !== 'undefined',
        sankey: typeof SankeyController !== 'undefined'
      });
    } else {
      console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    }
  </script>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

  <!-- v7.5 Utilities -->
  <script src="/src/utils/format_ownership.js"></script>
  <script src="/src/utils/edit-mode.js"></script>
  <script src="/src/utils/review-mode.js"></script>
  <script src="/src/core/reveal-config.js"></script>

  <!-- Review Mode & AI Regeneration Components -->
  <script src="/src/components/regeneration-panel.js"></script>

  <!-- v7.5 Renderers (6 layouts) -->
  <script src="/src/renderers/L01.js"></script>
  <script src="/src/renderers/L02.js"></script>
  <script src="/src/renderers/L03.js"></script>
  <script src="/src/renderers/L25.js"></script>
  <script src="/src/renderers/L27.js"></script>
  <script src="/src/renderers/L29.js"></script>

  <!-- Presentation Rendering Script -->
  <script>
    // Presentation data (injected by server)
    const PRESENTATION_DATA = {"title": "Fix Verification - bar_grouped - Regional Performance", "slides": [{"layout": "L02", "content": {"slide_title": "Regional Performance Comparison", "element_1": "Q1-Q4 2024 by Region", "element_3": "<div class=\"l02-chart-container\" style=\"width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;\">\n  <canvas id=\"chart-slide_001\"><\/canvas>\n\n  <!-- Edit Button (Pencil Icon) -->\n  <button class=\"chart-edit-btn\"\n          onclick=\"openChartEditor_chart_slide_001()\"\n          style=\"position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;\"\n          onmouseover=\"this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit<\/span>'; this.style.background='rgba(0,0,0,0.8)'\"\n          onmouseout=\"this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'\">\n    ✏️\n  <\/button>\n\n  <script>\n    (function() {\n      function initChart() {\n        // v3.3.4: Destroy existing chart instance to force animation replay\n        if (window.chartInstances && window.chartInstances['chart-slide_001']) {\n          console.log('Chart chart-slide_001 exists, destroying to replay animation...');\n          window.chartInstances['chart-slide_001'].destroy();\n          delete window.chartInstances['chart-slide_001'];\n        }\n\n        const ctx = document.getElementById('chart-slide_001').getContext('2d');\n        const chartConfig = {\"type\": \"bar\", \"data\": {\"labels\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"], \"datasets\": [{\"label\": \"North America\", \"data\": [124, 145, 165, 180], \"backgroundColor\": \"#FF6B6B\", \"borderColor\": \"#FF6B6B\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"EMEA\", \"data\": [98, 112, 128, 145], \"backgroundColor\": \"#4ECDC4\", \"borderColor\": \"#4ECDC4\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"APAC\", \"data\": [75, 88, 105, 125], \"backgroundColor\": \"#FFE66D\", \"borderColor\": \"#FFE66D\", \"borderWidth\": 2, \"borderRadius\": 10}]}, \"options\": {\"responsive\": true, \"maintainAspectRatio\": false, \"animation\": {\"duration\": 1500, \"easing\": \"easeInOutQuart\", \"delay\": 0, \"loop\": false, \"animateRotate\": true, \"animateScale\": true}, \"plugins\": {\"legend\": {\"display\": true, \"position\": \"top\", \"labels\": {\"font\": {\"size\": 14, \"weight\": \"bold\"}, \"padding\": 15, \"usePointStyle\": true}}, \"datalabels\": {\"display\": true, \"color\": \"#fff\", \"font\": {\"size\": 14, \"weight\": \"bold\"}, \"formatter\": \"function(value) { return value.toLocaleString(); }\", \"anchor\": \"end\", \"align\": \"end\", \"offset\": 0, \"backgroundColor\": \"rgba(0, 0, 0, 0.7)\", \"borderRadius\": 4, \"padding\": 6}, \"tooltip\": {\"enabled\": true, \"mode\": \"nearest\", \"intersect\": true}}, \"scales\": {\"x\": {\"display\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"autoSkip\": false, \"maxRotation\": 45, \"minRotation\": 0}, \"title\": {\"display\": true, \"text\": \"\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}, \"y\": {\"display\": true, \"beginAtZero\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"callback\": \"function(value) { return value.toLocaleString(); }\"}, \"title\": {\"display\": true, \"text\": \"Value\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}}}};\n        const chart = new Chart(ctx, chartConfig);\n\n        // Store reference for editor access\n        window.chartInstances = window.chartInstances || {};\n        window.chartInstances['chart-slide_001'] = chart;\n\n        console.log('✅ Chart chart-slide_001 initialized successfully');\n      }\n\n      // Reveal.js-aware initialization to ensure animations play\n      if (typeof Reveal !== 'undefined') {\n        // Wait for Reveal.js to be fully initialized before accessing methods\n        Reveal.on('ready', function() {\n          try {\n            const currentSlide = Reveal.getCurrentSlide();\n            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {\n              setTimeout(initChart, 100);  // Small delay for slide transition\n            }\n          } catch (e) {\n            console.warn('Chart init on ready failed:', e);\n          }\n        });\n\n        // v3.3.4: Always reinitialize on slide change to replay animation\n        Reveal.on('slidechanged', function(event) {\n          try {\n            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {\n              initChart();  // This now destroys old chart and creates new one\n            }\n          } catch (e) {\n            console.warn('Chart init on slide change failed:', e);\n          }\n        });\n      } else {\n        // No Reveal.js detected, init immediately (standalone mode)\n        if (document.readyState === 'loading') {\n          document.addEventListener('DOMContentLoaded', initChart);\n        } else {\n          initChart();\n        }\n      }\n    })();\n  <\/script>\n\n  <!-- Load Excel-like Spreadsheet Editor Library -->\n  <script src=\"https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js\"><\/script>\n\n  <!-- Excel Editor Function Definitions -->\n  <script>\n  (function() {\n      window.openChartEditor_chart_slide_001 = function() {\n        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');\n\n        // Get chart instance\n        const chart = window.chartInstances?.['chart-slide_001'];\n        if (!chart) {\n            console.error('Chart not found in window.chartInstances');\n            alert('Chart not ready. Please wait and try again.');\n            return;\n        }\n\n        console.log('✅ Chart found. Chart type:', chart.config.type);\n        console.log('Chart type parameter:', 'bar');\n\n        // Extract current chart data\n        const chartData = extractChartData_chart_slide_001(chart);\n\n        // === DIAGNOSTIC LOGGING ===\n        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');\n        console.log('Data type:', typeof chartData);\n        console.log('Is Array?:', Array.isArray(chartData));\n        console.log('Full data:', JSON.stringify(chartData, null, 2));\n\n        if (chartData && chartData.labels) {\n            console.log('✅ Multi-series format detected');\n            console.log('  Labels:', chartData.labels);\n            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);\n            if (chartData.datasets) {\n                chartData.datasets.forEach((ds, i) => {\n                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);\n                });\n            }\n        } else if (Array.isArray(chartData)) {\n            console.log('✅ Simple array format detected');\n            console.log('  Rows:', chartData.length);\n            if (chartData.length > 0) {\n                console.log('  First row sample:', chartData[0]);\n            }\n        }\n        console.log('Chart type parameter:', 'bar');\n        console.log('=== END DIAGNOSTIC DATA ===');\n\n        // Open Excel-like editor\n        openChartEditor(\n            'chart-slide_001',\n            'bar',\n            chartData,\n            {\n                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',\n                onSave: async (newData, chartId) => {\n                    console.log('Saving chart data:', newData);\n\n                    // Update chart instance\n                    updateChartData_chart_slide_001(chart, newData, 'bar');\n\n                    // Save to API\n                    try {\n                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({\n                                chart_id: chartId,\n                                presentation_id: 'fix_verify_001',\n                                data: newData,\n                                timestamp: Date.now()\n                            })\n                        });\n\n                        if (!response.ok) {\n                            throw new Error('API request failed');\n                        }\n\n                        console.log('✅ Chart data saved successfully');\n                    } catch (error) {\n                        console.error('❌ Error saving chart data:', error);\n                        throw error;\n                    }\n                }\n            }\n        );\n    };\n\n    // Extract data from chart instance based on chart type\n    function extractChartData_chart_slide_001(chart) {\n        const chartType = chart.config.type;\n\n        if (chartType === 'scatter') {\n            // Scatter: array of {x, y}\n            return chart.data.datasets[0]?.data || [];\n        } else if (chartType === 'bubble') {\n            // Bubble: array of {label, x, y, r}\n            return chart.data.datasets[0]?.data || [];\n        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {\n            // Check if multi-series\n            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {\n                // Multi-series format\n                return {\n                    labels: chart.data.labels || [],\n                    datasets: chart.data.datasets.map(ds => ({\n                        label: ds.label,\n                        data: ds.data\n                    }))\n                };\n            } else {\n                // Simple label-value format\n                const labels = chart.data.labels || [];\n                const values = chart.data.datasets[0]?.data || [];\n                return labels.map((label, i) => ({ label, value: values[i] }));\n            }\n        } else {\n            // Default: label-value format\n            const labels = chart.data.labels || [];\n            const values = chart.data.datasets[0]?.data || [];\n            return labels.map((label, i) => ({ label, value: values[i] }));\n        }\n    }\n\n    // Update chart instance with new data\n    function updateChartData_chart_slide_001(chart, newData, chartType) {\n        if (chartType === 'scatter' || chartType === 'bubble') {\n            // Object-based data\n            chart.data.datasets[0].data = newData;\n        } else if (newData.labels && newData.datasets) {\n            // Multi-series format\n            chart.data.labels = newData.labels;\n            chart.data.datasets = newData.datasets;\n        } else if (Array.isArray(newData)) {\n            // Simple label-value format\n            chart.data.labels = newData.map(d => d.label);\n            chart.data.datasets[0].data = newData.map(d => d.value);\n        }\n\n        chart.update();\n    }\n  })();\n  <\/script>\n<\/div>\n", "element_2": "<div class=\"l02-observations-panel\" style=\"width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;\">\n    <h3 style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;\">\n        Key Insights\n    <\/h3>\n    <ul style=\"margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;\">\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Executives should prioritize identifying challenges in each region to drive future performance improvements.\n        <\/li>\n    <\/ul>\n<\/div>", "presentation_name": "P0 Fixes Verification", "company_logo": "✅"}, "background_color": null, "background_image": null}], "id": "8270434d-8cfc-4cda-8bae-e52a60fa7ff0", "created_at": "2025-11-29T15:53:37.607337"};

    // Renderer registry (6 layouts)
    const RENDERERS = {
      'L01': window.renderL01,
      'L02': window.renderL02,
      'L03': window.renderL03,
      'L25': window.renderL25,
      'L27': window.renderL27,
      'L29': window.renderL29
    };

    /**
     * Render presentation from data
     */
    function renderPresentation(data) {
      if (!data || !data.slides) {
        console.error('Invalid presentation data');
        return;
      }

      const slidesContainer = document.getElementById('slides-container');
      slidesContainer.innerHTML = '';

      // Update document title
      document.title = data.title || 'Presentation';

      // Render each slide
      data.slides.forEach((slide, index) => {
        const layout = slide.layout;
        const content = slide.content;

        // Get renderer
        const renderer = RENDERERS[layout];
        if (!renderer) {
          console.error(`No renderer found for layout: ${layout}`);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Error: Unknown Layout</h2>
                <p>Layout '${layout}' is not supported in v7.5-main</p>
                <p>Valid layouts: L01, L02, L03, L25, L27, L29</p>
              </div>
            </section>
          `;
          return;
        }

        // Render slide
        try {
          const slideHTML = renderer(content, slide, index);

          // Create temporary container to parse HTML
          const tempContainer = document.createElement('div');
          tempContainer.innerHTML = slideHTML;

          // Extract all script tags before inserting HTML
          const scripts = tempContainer.querySelectorAll('script');

          // Insert the HTML while preserving previous DOM elements
          // Using appendChild instead of innerHTML += to avoid destroying previous slides
          const sections = tempContainer.querySelectorAll('section');
          sections.forEach(section => {
            slidesContainer.appendChild(section);
          });

          // Manually execute each script by creating new script elements
          scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy all attributes (src, type, async, defer, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });

            // Copy script content (for inline scripts)
            newScript.textContent = oldScript.textContent;

            // Append to document body - this triggers execution
            document.body.appendChild(newScript);
          });

        } catch (error) {
          console.error(`Error rendering slide ${index + 1}:`, error);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Rendering Error</h2>
                <p>Failed to render slide ${index + 1} (${layout})</p>
                <p>${error.message}</p>
              </div>
            </section>
          `;
        }
      });

      // Initialize Reveal.js AFTER scripts have time to execute
      setTimeout(() => {
        if (typeof initReveal === 'function') {
          initReveal();
        } else {
          // Fallback if reveal-config.js not loaded
          Reveal.initialize({
            width: 1920,
            height: 1080,
            margin: 0,
            minScale: 0.1,
            maxScale: 3.0,
            center: true,
            controls: true,
            progress: true,
            slideNumber: 'c/t',
            hash: true,
            history: true
          });
        }

        console.log(`✅ Presentation rendered: ${data.slides.length} slides`);
      }, 300);  // Give scripts 300ms to execute
    }

    /**
     * Show help text briefly
     */
    function showHelpText() {
      const helpText = document.getElementById('help-text');
      helpText.classList.add('show');
      setTimeout(() => {
        helpText.classList.remove('show');
      }, 3000);
    }

    // Add keyboard shortcuts (Note: 'B' and 'C' are handled by RevealJS config)
    document.addEventListener('keydown', (e) => {
      if (e.key === '?') {
        showHelpText();
      }
    });

    /**
     * postMessage Bridge for Cross-Origin Communication
     * Allows parent window from different origin to control the presentation
     *
     * Security: Validates message origin before executing commands
     */
    window.addEventListener('message', (event) => {
      // Security: Validate origin
      // Allow localhost (development), cloud platforms, and production frontend (deckster.xyz)
      const allowedOriginPattern = /^https?:\/\/(localhost:\d+|127\.0\.0\.1:\d+|.*\.up\.railway\.app|.*\.vercel\.app|.*\.netlify\.app|(www\.)?deckster\.xyz)$/;

      if (!allowedOriginPattern.test(event.origin)) {
        console.warn('⚠️ Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      const { action, params } = event.data || {};

      if (!action) {
        console.warn('⚠️ postMessage received without action:', event.data);
        return;
      }

      console.log(`📨 postMessage received: ${action}`, params);

      let result = { success: false, action };

      try {
        switch (action) {
          // Navigation functions
          case 'nextSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.next();
              result.success = true;
            }
            break;

          case 'prevSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.prev();
              result.success = true;
            }
            break;

          case 'goToSlide':
            if (typeof goToSlide === 'function' && params?.index !== undefined) {
              goToSlide(params.index);  // Now expects 0-based index
              result.success = true;
              result.slideIndex = params.index;
            } else if (typeof Reveal !== 'undefined' && params?.index !== undefined) {
              Reveal.slide(params.index);  // Fallback: direct call with 0-based index
              result.success = true;
              result.slideIndex = params.index;
            }
            break;

          case 'getCurrentSlideInfo':
            if (typeof getCurrentSlideInfo === 'function') {
              result.success = true;
              result.data = getCurrentSlideInfo();
            }
            break;

          // Edit mode functions
          case 'toggleEditMode':
            if (typeof toggleEditMode === 'function') {
              toggleEditMode();
              result.success = true;
              result.isEditing = document.body.getAttribute('data-mode') === 'edit';
            }
            break;

          case 'saveAllChanges':
            if (typeof saveAllChanges === 'function') {
              saveAllChanges();
              result.success = true;
            }
            break;

          case 'cancelEdits':
            if (typeof cancelEdits === 'function') {
              cancelEdits();
              result.success = true;
            }
            break;

          case 'showVersionHistory':
            if (typeof showVersionHistory === 'function') {
              showVersionHistory();
              result.success = true;
            }
            break;

          // Overview mode functions
          case 'toggleOverview':
            if (typeof toggleOverview === 'function') {
              toggleOverview();
              result.success = true;
              result.isOverview = isOverviewActive();
            } else if (typeof Reveal !== 'undefined') {
              Reveal.toggleOverview();
              result.success = true;
            }
            break;

          case 'isOverviewActive':
            if (typeof isOverviewActive === 'function') {
              result.success = true;
              result.data = isOverviewActive();
            }
            break;

          // Debug functions
          case 'toggleGridOverlay':
            if (typeof toggleGridOverlay === 'function') {
              toggleGridOverlay();
              result.success = true;
            }
            break;

          case 'toggleBorderHighlight':
            if (typeof toggleBorderHighlight === 'function') {
              toggleBorderHighlight();
              result.success = true;
            }
            break;

          // Review mode functions
          case 'toggleReviewMode':
            if (typeof toggleReviewMode === 'function') {
              toggleReviewMode();
              result.success = true;
              result.isReviewing = document.body.getAttribute('data-mode') === 'review';
            }
            break;

          case 'enterReviewMode':
            if (typeof enterReviewMode === 'function') {
              enterReviewMode();
              result.success = true;
              result.isReviewing = true;
            }
            break;

          case 'exitReviewMode':
            if (typeof exitReviewMode === 'function') {
              exitReviewMode();
              result.success = true;
              result.isReviewing = false;
            }
            break;

          case 'getSelectedSections':
            if (typeof getSelectedSections === 'function') {
              result.success = true;
              result.data = getSelectedSections();
            }
            break;

          case 'clearSelection':
            if (typeof clearSelection === 'function') {
              clearSelection();
              result.success = true;
            }
            break;

          default:
            console.warn(`⚠️ Unknown action: ${action}`);
            result.error = `Unknown action: ${action}`;
        }
      } catch (error) {
        console.error(`❌ Error executing action ${action}:`, error);
        result.success = false;
        result.error = error.message;
      }

      // Send response back to parent
      event.source.postMessage(result, event.origin);
      console.log(`📤 postMessage response sent:`, result);
    });

    console.log('✅ postMessage bridge initialized - ready for cross-origin commands');

    // Render presentation on load
    window.addEventListener('DOMContentLoaded', () => {
      if (PRESENTATION_DATA) {
        renderPresentation(PRESENTATION_DATA);
      } else {
        document.getElementById('slides-container').innerHTML = `
          <section>
            <div style="text-align: center; padding: 60px; color: #6b7280;">
              <h1 style="font-size: 48px; color: #1f2937;">No Presentation Data</h1>
              <p style="font-size: 24px; margin-top: 24px;">No presentation data was provided</p>
              <p style="font-size: 18px; margin-top: 16px; color: #9ca3af;">Use the API to create a presentation</p>
            </div>
          </section>
        `;
        if (typeof initReveal === 'function') {
          initReveal();
        }
      }

      // Show help text on first load
      setTimeout(showHelpText, 1000);
    });
  </script>


<svg id="SvgjsSvg1001" width="2" height="0" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev" style="overflow: hidden; top: -100%; left: -100%; position: absolute; opacity: 0;"><defs id="SvgjsDefs1002"></defs><polyline id="SvgjsPolyline1003" points="0,0"></polyline><path id="SvgjsPath1004" d="M0 0 "></path></svg><script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script><script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script><script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script></body></html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fix Verification - bar_grouped - Regional Performance</title>

  <!-- Reveal.js Core -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">

  <!-- v7.5 Styles -->
  <link rel="stylesheet" href="/src/styles/core/reset.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/grid-system.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/borders.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/content-area.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/edit-mode.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/review-mode.css?v=20250124">
  <link rel="stylesheet" href="/src/styles/regeneration-panel.css?v=20250124">

  <style>
    /* Minimal additional styling */
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }

    .reveal {
      background: #ffffff;
    }

    /* Help text */
    #help-text {
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.8);
      color: white;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      z-index: 10000;
      opacity: 0;
      transition: opacity 0.3s;
    }

    #help-text.show {
      opacity: 1;
    }
  </style>
<style>
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
</style></head>
<body class="reveal-viewport" style="--slide-width: 1920px; --slide-height: 1080px; --slide-scale: 0.765625;">
  <!-- Help Text -->
  <div id="help-text" class="">
    Press 'R' for review mode | 'E' for edit mode | 'G' for grid | 'B' for borders | '?' for help
  </div>

  <!-- Edit Mode UI -->
  <button id="toggle-edit-mode" onclick="toggleEditMode()">✏️ Edit Mode</button>

  <div id="edit-controls">
    <button id="save-btn" onclick="saveAllChanges()" title="Save Changes">💾</button>
    <button id="cancel-btn" onclick="cancelEdits()" title="Cancel">❌</button>
    <button id="view-history-btn" onclick="showVersionHistory()" title="Version History">📋</button>
  </div>

  <div id="edit-notification"></div>

  <div class="edit-shortcuts">
    <div><kbd>E</kbd> Toggle Edit Mode</div>
    <div><kbd>Ctrl+S</kbd> Save Changes</div>
    <div><kbd>ESC</kbd> Cancel</div>
  </div>

  <!-- Selection Indicator -->
  <div id="selection-indicator" class="selection-indicator"></div>

  <!-- AI Regeneration Panel -->
  <div id="regeneration-panel">
    <h3>🤖 AI Regeneration</h3>
    <div class="input-group">
      <input type="text" id="ai-instruction-input" placeholder="Enter instruction (e.g., Make it more engaging with examples)">
      <button id="regenerate-btn" onclick="regenerateSelectedSections()">
        Regenerate with AI
      </button>
      <button id="cancel-selection-btn" onclick="clearSelection()">
        Cancel
      </button>
    </div>
  </div>

  <!-- Reveal.js Container -->
  <div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>

  <!-- Reveal.js Core -->
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

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
      console.log('✅ Chart.js extended plugins loaded:', {
        treemap: typeof TreemapController !== 'undefined',
        matrix: typeof MatrixController !== 'undefined',
        boxplot: typeof BoxPlotController !== 'undefined',
        financial: typeof CandlestickController !== 'undefined',
        sankey: typeof SankeyController !== 'undefined'
      });
    } else {
      console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    }
  </script>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

  <!-- v7.5 Utilities -->
  <script src="/src/utils/format_ownership.js"></script>
  <script src="/src/utils/edit-mode.js"></script>
  <script src="/src/utils/review-mode.js"></script>
  <script src="/src/core/reveal-config.js"></script>

  <!-- Review Mode & AI Regeneration Components -->
  <script src="/src/components/regeneration-panel.js"></script>

  <!-- v7.5 Renderers (6 layouts) -->
  <script src="/src/renderers/L01.js"></script>
  <script src="/src/renderers/L02.js"></script>
  <script src="/src/renderers/L03.js"></script>
  <script src="/src/renderers/L25.js"></script>
  <script src="/src/renderers/L27.js"></script>
  <script src="/src/renderers/L29.js"></script>

  <!-- Presentation Rendering Script -->
  <script>
    // Presentation data (injected by server)
    const PRESENTATION_DATA = {"title": "Fix Verification - bar_grouped - Regional Performance", "slides": [{"layout": "L02", "content": {"slide_title": "Regional Performance Comparison", "element_1": "Q1-Q4 2024 by Region", "element_3": "<div class=\"l02-chart-container\" style=\"width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;\">\n  <canvas id=\"chart-slide_001\"><\/canvas>\n\n  <!-- Edit Button (Pencil Icon) -->\n  <button class=\"chart-edit-btn\"\n          onclick=\"openChartEditor_chart_slide_001()\"\n          style=\"position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;\"\n          onmouseover=\"this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit<\/span>'; this.style.background='rgba(0,0,0,0.8)'\"\n          onmouseout=\"this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'\">\n    ✏️\n  <\/button>\n\n  <script>\n    (function() {\n      function initChart() {\n        // v3.3.4: Destroy existing chart instance to force animation replay\n        if (window.chartInstances && window.chartInstances['chart-slide_001']) {\n          console.log('Chart chart-slide_001 exists, destroying to replay animation...');\n          window.chartInstances['chart-slide_001'].destroy();\n          delete window.chartInstances['chart-slide_001'];\n        }\n\n        const ctx = document.getElementById('chart-slide_001').getContext('2d');\n        const chartConfig = {\"type\": \"bar\", \"data\": {\"labels\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"], \"datasets\": [{\"label\": \"North America\", \"data\": [124, 145, 165, 180], \"backgroundColor\": \"#FF6B6B\", \"borderColor\": \"#FF6B6B\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"EMEA\", \"data\": [98, 112, 128, 145], \"backgroundColor\": \"#4ECDC4\", \"borderColor\": \"#4ECDC4\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"APAC\", \"data\": [75, 88, 105, 125], \"backgroundColor\": \"#FFE66D\", \"borderColor\": \"#FFE66D\", \"borderWidth\": 2, \"borderRadius\": 10}]}, \"options\": {\"responsive\": true, \"maintainAspectRatio\": false, \"animation\": {\"duration\": 1500, \"easing\": \"easeInOutQuart\", \"delay\": 0, \"loop\": false, \"animateRotate\": true, \"animateScale\": true}, \"plugins\": {\"legend\": {\"display\": true, \"position\": \"top\", \"labels\": {\"font\": {\"size\": 14, \"weight\": \"bold\"}, \"padding\": 15, \"usePointStyle\": true}}, \"datalabels\": {\"display\": true, \"color\": \"#fff\", \"font\": {\"size\": 14, \"weight\": \"bold\"}, \"formatter\": \"function(value) { return value.toLocaleString(); }\", \"anchor\": \"end\", \"align\": \"end\", \"offset\": 0, \"backgroundColor\": \"rgba(0, 0, 0, 0.7)\", \"borderRadius\": 4, \"padding\": 6}, \"tooltip\": {\"enabled\": true, \"mode\": \"nearest\", \"intersect\": true}}, \"scales\": {\"x\": {\"display\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"autoSkip\": false, \"maxRotation\": 45, \"minRotation\": 0}, \"title\": {\"display\": true, \"text\": \"\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}, \"y\": {\"display\": true, \"beginAtZero\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"callback\": \"function(value) { return value.toLocaleString(); }\"}, \"title\": {\"display\": true, \"text\": \"Value\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}}}};\n        const chart = new Chart(ctx, chartConfig);\n\n        // Store reference for editor access\n        window.chartInstances = window.chartInstances || {};\n        window.chartInstances['chart-slide_001'] = chart;\n\n        console.log('✅ Chart chart-slide_001 initialized successfully');\n      }\n\n      // Reveal.js-aware initialization to ensure animations play\n      if (typeof Reveal !== 'undefined') {\n        // Wait for Reveal.js to be fully initialized before accessing methods\n        Reveal.on('ready', function() {\n          try {\n            const currentSlide = Reveal.getCurrentSlide();\n            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {\n              setTimeout(initChart, 100);  // Small delay for slide transition\n            }\n          } catch (e) {\n            console.warn('Chart init on ready failed:', e);\n          }\n        });\n\n        // v3.3.4: Always reinitialize on slide change to replay animation\n        Reveal.on('slidechanged', function(event) {\n          try {\n            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {\n              initChart();  // This now destroys old chart and creates new one\n            }\n          } catch (e) {\n            console.warn('Chart init on slide change failed:', e);\n          }\n        });\n      } else {\n        // No Reveal.js detected, init immediately (standalone mode)\n        if (document.readyState === 'loading') {\n          document.addEventListener('DOMContentLoaded', initChart);\n        } else {\n          initChart();\n        }\n      }\n    })();\n  <\/script>\n\n  <!-- Load Excel-like Spreadsheet Editor Library -->\n  <script src=\"https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js\"><\/script>\n\n  <!-- Excel Editor Function Definitions -->\n  <script>\n  (function() {\n      window.openChartEditor_chart_slide_001 = function() {\n        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');\n\n        // Get chart instance\n        const chart = window.chartInstances?.['chart-slide_001'];\n        if (!chart) {\n            console.error('Chart not found in window.chartInstances');\n            alert('Chart not ready. Please wait and try again.');\n            return;\n        }\n\n        console.log('✅ Chart found. Chart type:', chart.config.type);\n        console.log('Chart type parameter:', 'bar');\n\n        // Extract current chart data\n        const chartData = extractChartData_chart_slide_001(chart);\n\n        // === DIAGNOSTIC LOGGING ===\n        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');\n        console.log('Data type:', typeof chartData);\n        console.log('Is Array?:', Array.isArray(chartData));\n        console.log('Full data:', JSON.stringify(chartData, null, 2));\n\n        if (chartData && chartData.labels) {\n            console.log('✅ Multi-series format detected');\n            console.log('  Labels:', chartData.labels);\n            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);\n            if (chartData.datasets) {\n                chartData.datasets.forEach((ds, i) => {\n                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);\n                });\n            }\n        } else if (Array.isArray(chartData)) {\n            console.log('✅ Simple array format detected');\n            console.log('  Rows:', chartData.length);\n            if (chartData.length > 0) {\n                console.log('  First row sample:', chartData[0]);\n            }\n        }\n        console.log('Chart type parameter:', 'bar');\n        console.log('=== END DIAGNOSTIC DATA ===');\n\n        // Open Excel-like editor\n        openChartEditor(\n            'chart-slide_001',\n            'bar',\n            chartData,\n            {\n                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',\n                onSave: async (newData, chartId) => {\n                    console.log('Saving chart data:', newData);\n\n                    // Update chart instance\n                    updateChartData_chart_slide_001(chart, newData, 'bar');\n\n                    // Save to API\n                    try {\n                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({\n                                chart_id: chartId,\n                                presentation_id: 'fix_verify_001',\n                                data: newData,\n                                timestamp: Date.now()\n                            })\n                        });\n\n                        if (!response.ok) {\n                            throw new Error('API request failed');\n                        }\n\n                        console.log('✅ Chart data saved successfully');\n                    } catch (error) {\n                        console.error('❌ Error saving chart data:', error);\n                        throw error;\n                    }\n                }\n            }\n        );\n    };\n\n    // Extract data from chart instance based on chart type\n    function extractChartData_chart_slide_001(chart) {\n        const chartType = chart.config.type;\n\n        if (chartType === 'scatter') {\n            // Scatter: array of {x, y}\n            return chart.data.datasets[0]?.data || [];\n        } else if (chartType === 'bubble') {\n            // Bubble: array of {label, x, y, r}\n            return chart.data.datasets[0]?.data || [];\n        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {\n            // Check if multi-series\n            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {\n                // Multi-series format\n                return {\n                    labels: chart.data.labels || [],\n                    datasets: chart.data.datasets.map(ds => ({\n                        label: ds.label,\n                        data: ds.data\n                    }))\n                };\n            } else {\n                // Simple label-value format\n                const labels = chart.data.labels || [];\n                const values = chart.data.datasets[0]?.data || [];\n                return labels.map((label, i) => ({ label, value: values[i] }));\n            }\n        } else {\n            // Default: label-value format\n            const labels = chart.data.labels || [];\n            const values = chart.data.datasets[0]?.data || [];\n            return labels.map((label, i) => ({ label, value: values[i] }));\n        }\n    }\n\n    // Update chart instance with new data\n    function updateChartData_chart_slide_001(chart, newData, chartType) {\n        if (chartType === 'scatter' || chartType === 'bubble') {\n            // Object-based data\n            chart.data.datasets[0].data = newData;\n        } else if (newData.labels && newData.datasets) {\n            // Multi-series format\n            chart.data.labels = newData.labels;\n            chart.data.datasets = newData.datasets;\n        } else if (Array.isArray(newData)) {\n            // Simple label-value format\n            chart.data.labels = newData.map(d => d.label);\n            chart.data.datasets[0].data = newData.map(d => d.value);\n        }\n\n        chart.update();\n    }\n  })();\n  <\/script>\n<\/div>\n", "element_2": "<div class=\"l02-observations-panel\" style=\"width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;\">\n    <h3 style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;\">\n        Key Insights\n    <\/h3>\n    <ul style=\"margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;\">\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Executives should prioritize identifying challenges in each region to drive future performance improvements.\n        <\/li>\n    <\/ul>\n<\/div>", "presentation_name": "P0 Fixes Verification", "company_logo": "✅"}, "background_color": null, "background_image": null}], "id": "8270434d-8cfc-4cda-8bae-e52a60fa7ff0", "created_at": "2025-11-29T15:53:37.607337"};

    // Renderer registry (6 layouts)
    const RENDERERS = {
      'L01': window.renderL01,
      'L02': window.renderL02,
      'L03': window.renderL03,
      'L25': window.renderL25,
      'L27': window.renderL27,
      'L29': window.renderL29
    };

    /**
     * Render presentation from data
     */
    function renderPresentation(data) {
      if (!data || !data.slides) {
        console.error('Invalid presentation data');
        return;
      }

      const slidesContainer = document.getElementById('slides-container');
      slidesContainer.innerHTML = '';

      // Update document title
      document.title = data.title || 'Presentation';

      // Render each slide
      data.slides.forEach((slide, index) => {
        const layout = slide.layout;
        const content = slide.content;

        // Get renderer
        const renderer = RENDERERS[layout];
        if (!renderer) {
          console.error(`No renderer found for layout: ${layout}`);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Error: Unknown Layout</h2>
                <p>Layout '${layout}' is not supported in v7.5-main</p>
                <p>Valid layouts: L01, L02, L03, L25, L27, L29</p>
              </div>
            </section>
          `;
          return;
        }

        // Render slide
        try {
          const slideHTML = renderer(content, slide, index);

          // Create temporary container to parse HTML
          const tempContainer = document.createElement('div');
          tempContainer.innerHTML = slideHTML;

          // Extract all script tags before inserting HTML
          const scripts = tempContainer.querySelectorAll('script');

          // Insert the HTML while preserving previous DOM elements
          // Using appendChild instead of innerHTML += to avoid destroying previous slides
          const sections = tempContainer.querySelectorAll('section');
          sections.forEach(section => {
            slidesContainer.appendChild(section);
          });

          // Manually execute each script by creating new script elements
          scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy all attributes (src, type, async, defer, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });

            // Copy script content (for inline scripts)
            newScript.textContent = oldScript.textContent;

            // Append to document body - this triggers execution
            document.body.appendChild(newScript);
          });

        } catch (error) {
          console.error(`Error rendering slide ${index + 1}:`, error);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Rendering Error</h2>
                <p>Failed to render slide ${index + 1} (${layout})</p>
                <p>${error.message}</p>
              </div>
            </section>
          `;
        }
      });

      // Initialize Reveal.js AFTER scripts have time to execute
      setTimeout(() => {
        if (typeof initReveal === 'function') {
          initReveal();
        } else {
          // Fallback if reveal-config.js not loaded
          Reveal.initialize({
            width: 1920,
            height: 1080,
            margin: 0,
            minScale: 0.1,
            maxScale: 3.0,
            center: true,
            controls: true,
            progress: true,
            slideNumber: 'c/t',
            hash: true,
            history: true
          });
        }

        console.log(`✅ Presentation rendered: ${data.slides.length} slides`);
      }, 300);  // Give scripts 300ms to execute
    }

    /**
     * Show help text briefly
     */
    function showHelpText() {
      const helpText = document.getElementById('help-text');
      helpText.classList.add('show');
      setTimeout(() => {
        helpText.classList.remove('show');
      }, 3000);
    }

    // Add keyboard shortcuts (Note: 'B' and 'C' are handled by RevealJS config)
    document.addEventListener('keydown', (e) => {
      if (e.key === '?') {
        showHelpText();
      }
    });

    /**
     * postMessage Bridge for Cross-Origin Communication
     * Allows parent window from different origin to control the presentation
     *
     * Security: Validates message origin before executing commands
     */
    window.addEventListener('message', (event) => {
      // Security: Validate origin
      // Allow localhost (development), cloud platforms, and production frontend (deckster.xyz)
      const allowedOriginPattern = /^https?:\/\/(localhost:\d+|127\.0\.0\.1:\d+|.*\.up\.railway\.app|.*\.vercel\.app|.*\.netlify\.app|(www\.)?deckster\.xyz)$/;

      if (!allowedOriginPattern.test(event.origin)) {
        console.warn('⚠️ Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      const { action, params } = event.data || {};

      if (!action) {
        console.warn('⚠️ postMessage received without action:', event.data);
        return;
      }

      console.log(`📨 postMessage received: ${action}`, params);

      let result = { success: false, action };

      try {
        switch (action) {
          // Navigation functions
          case 'nextSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.next();
              result.success = true;
            }
            break;

          case 'prevSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.prev();
              result.success = true;
            }
            break;

          case 'goToSlide':
            if (typeof goToSlide === 'function' && params?.index !== undefined) {
              goToSlide(params.index);  // Now expects 0-based index
              result.success = true;
              result.slideIndex = params.index;
            } else if (typeof Reveal !== 'undefined' && params?.index !== undefined) {
              Reveal.slide(params.index);  // Fallback: direct call with 0-based index
              result.success = true;
              result.slideIndex = params.index;
            }
            break;

          case 'getCurrentSlideInfo':
            if (typeof getCurrentSlideInfo === 'function') {
              result.success = true;
              result.data = getCurrentSlideInfo();
            }
            break;

          // Edit mode functions
          case 'toggleEditMode':
            if (typeof toggleEditMode === 'function') {
              toggleEditMode();
              result.success = true;
              result.isEditing = document.body.getAttribute('data-mode') === 'edit';
            }
            break;

          case 'saveAllChanges':
            if (typeof saveAllChanges === 'function') {
              saveAllChanges();
              result.success = true;
            }
            break;

          case 'cancelEdits':
            if (typeof cancelEdits === 'function') {
              cancelEdits();
              result.success = true;
            }
            break;

          case 'showVersionHistory':
            if (typeof showVersionHistory === 'function') {
              showVersionHistory();
              result.success = true;
            }
            break;

          // Overview mode functions
          case 'toggleOverview':
            if (typeof toggleOverview === 'function') {
              toggleOverview();
              result.success = true;
              result.isOverview = isOverviewActive();
            } else if (typeof Reveal !== 'undefined') {
              Reveal.toggleOverview();
              result.success = true;
            }
            break;

          case 'isOverviewActive':
            if (typeof isOverviewActive === 'function') {
              result.success = true;
              result.data = isOverviewActive();
            }
            break;

          // Debug functions
          case 'toggleGridOverlay':
            if (typeof toggleGridOverlay === 'function') {
              toggleGridOverlay();
              result.success = true;
            }
            break;

          case 'toggleBorderHighlight':
            if (typeof toggleBorderHighlight === 'function') {
              toggleBorderHighlight();
              result.success = true;
            }
            break;

          // Review mode functions
          case 'toggleReviewMode':
            if (typeof toggleReviewMode === 'function') {
              toggleReviewMode();
              result.success = true;
              result.isReviewing = document.body.getAttribute('data-mode') === 'review';
            }
            break;

          case 'enterReviewMode':
            if (typeof enterReviewMode === 'function') {
              enterReviewMode();
              result.success = true;
              result.isReviewing = true;
            }
            break;

          case 'exitReviewMode':
            if (typeof exitReviewMode === 'function') {
              exitReviewMode();
              result.success = true;
              result.isReviewing = false;
            }
            break;

          case 'getSelectedSections':
            if (typeof getSelectedSections === 'function') {
              result.success = true;
              result.data = getSelectedSections();
            }
            break;

          case 'clearSelection':
            if (typeof clearSelection === 'function') {
              clearSelection();
              result.success = true;
            }
            break;

          default:
            console.warn(`⚠️ Unknown action: ${action}`);
            result.error = `Unknown action: ${action}`;
        }
      } catch (error) {
        console.error(`❌ Error executing action ${action}:`, error);
        result.success = false;
        result.error = error.message;
      }

      // Send response back to parent
      event.source.postMessage(result, event.origin);
      console.log(`📤 postMessage response sent:`, result);
    });

    console.log('✅ postMessage bridge initialized - ready for cross-origin commands');

    // Render presentation on load
    window.addEventListener('DOMContentLoaded', () => {
      if (PRESENTATION_DATA) {
        renderPresentation(PRESENTATION_DATA);
      } else {
        document.getElementById('slides-container').innerHTML = `
          <section>
            <div style="text-align: center; padding: 60px; color: #6b7280;">
              <h1 style="font-size: 48px; color: #1f2937;">No Presentation Data</h1>
              <p style="font-size: 24px; margin-top: 24px;">No presentation data was provided</p>
              <p style="font-size: 18px; margin-top: 16px; color: #9ca3af;">Use the API to create a presentation</p>
            </div>
          </section>
        `;
        if (typeof initReveal === 'function') {
          initReveal();
        }
      }

      // Show help text on first load
      setTimeout(showHelpText, 1000);
    });
  </script>


<svg id="SvgjsSvg1001" width="2" height="0" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev" style="overflow: hidden; top: -100%; left: -100%; position: absolute; opacity: 0;"><defs id="SvgjsDefs1002"></defs><polyline id="SvgjsPolyline1003" points="0,0"></polyline><path id="SvgjsPath1004" d="M0 0 "></path></svg><script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script><script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script><script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script></body>
<!-- Help Text -->
<div id="help-text" class="">
    Press 'R' for review mode | 'E' for edit mode | 'G' for grid | 'B' for borders | '?' for help
  </div>
<!-- Edit Mode UI -->
<button id="toggle-edit-mode" onclick="toggleEditMode()">✏️ Edit Mode</button>
<div id="edit-controls">
    <button id="save-btn" onclick="saveAllChanges()" title="Save Changes">💾</button>
    <button id="cancel-btn" onclick="cancelEdits()" title="Cancel">❌</button>
    <button id="view-history-btn" onclick="showVersionHistory()" title="Version History">📋</button>
  </div>
<div id="edit-notification"></div>
<div class="edit-shortcuts">
    <div><kbd>E</kbd> Toggle Edit Mode</div>
    <div><kbd>Ctrl+S</kbd> Save Changes</div>
    <div><kbd>ESC</kbd> Cancel</div>
  </div>
<!-- Selection Indicator -->
<div id="selection-indicator" class="selection-indicator"></div>
<!-- AI Regeneration Panel -->
<div id="regeneration-panel">
    <h3>🤖 AI Regeneration</h3>
    <div class="input-group">
      <input type="text" id="ai-instruction-input" placeholder="Enter instruction (e.g., Make it more engaging with examples)">
      <button id="regenerate-btn" onclick="regenerateSelectedSections()">
        Regenerate with AI
      </button>
      <button id="cancel-selection-btn" onclick="clearSelection()">
        Cancel
      </button>
    </div>
  </div>
<!-- Reveal.js Container -->
<div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>
<div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
<section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section>
<!-- Title (42px bold, matching L25) -->
<div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>
<!-- Subtitle (24px, matching L25) -->
<div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>
<!-- Left: Diagram/Chart Container (1260px × 720px) -->
<div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>
<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>
<canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>
<!-- Edit Button (Pencil Icon) -->
<button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>
<script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>
<!-- Load Excel-like Spreadsheet Editor Library -->
<script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>
<!-- Excel Editor Function Definitions -->
<script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
<div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>
<div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>
<!-- Right: Observations/Text Container (540px × 720px) -->
<div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>
<!-- Footer: Presentation Name (18px, matching L25) -->
<div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
<!-- Footer: Company Logo (bottom-right, matching L27) -->
<div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
<section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section>
<div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
<div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div>
<div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div>
<aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside>
<div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div>
<div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div>
<div class="pause-overlay"><button class="resume-button">Resume presentation</button></div>
<div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div>
<<pseudo>></<pseudo>>
<div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>
<!-- Reveal.js Core -->
<script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>
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
      console.log('✅ Chart.js extended plugins loaded:', {
        treemap: typeof TreemapController !== 'undefined',
        matrix: typeof MatrixController !== 'undefined',
        boxplot: typeof BoxPlotController !== 'undefined',
        financial: typeof CandlestickController !== 'undefined',
        sankey: typeof SankeyController !== 'undefined'
      });
    } else {
      console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    }
  </script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
<!-- v7.5 Utilities -->
<script src="/src/utils/format_ownership.js"></script>
<script src="/src/utils/edit-mode.js"></script>
<script src="/src/utils/review-mode.js"></script>
<script src="/src/core/reveal-config.js"></script>
<!-- Review Mode & AI Regeneration Components -->
<script src="/src/components/regeneration-panel.js"></script>
<!-- v7.5 Renderers (6 layouts) -->
<script src="/src/renderers/L01.js"></script>
<script src="/src/renderers/L02.js"></script>
<script src="/src/renderers/L03.js"></script>
<script src="/src/renderers/L25.js"></script>
<script src="/src/renderers/L27.js"></script>
<script src="/src/renderers/L29.js"></script>
<!-- Presentation Rendering Script -->
<script>
    // Presentation data (injected by server)
    const PRESENTATION_DATA = {"title": "Fix Verification - bar_grouped - Regional Performance", "slides": [{"layout": "L02", "content": {"slide_title": "Regional Performance Comparison", "element_1": "Q1-Q4 2024 by Region", "element_3": "<div class=\"l02-chart-container\" style=\"width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;\">\n  <canvas id=\"chart-slide_001\"><\/canvas>\n\n  <!-- Edit Button (Pencil Icon) -->\n  <button class=\"chart-edit-btn\"\n          onclick=\"openChartEditor_chart_slide_001()\"\n          style=\"position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;\"\n          onmouseover=\"this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit<\/span>'; this.style.background='rgba(0,0,0,0.8)'\"\n          onmouseout=\"this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'\">\n    ✏️\n  <\/button>\n\n  <script>\n    (function() {\n      function initChart() {\n        // v3.3.4: Destroy existing chart instance to force animation replay\n        if (window.chartInstances && window.chartInstances['chart-slide_001']) {\n          console.log('Chart chart-slide_001 exists, destroying to replay animation...');\n          window.chartInstances['chart-slide_001'].destroy();\n          delete window.chartInstances['chart-slide_001'];\n        }\n\n        const ctx = document.getElementById('chart-slide_001').getContext('2d');\n        const chartConfig = {\"type\": \"bar\", \"data\": {\"labels\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"], \"datasets\": [{\"label\": \"North America\", \"data\": [124, 145, 165, 180], \"backgroundColor\": \"#FF6B6B\", \"borderColor\": \"#FF6B6B\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"EMEA\", \"data\": [98, 112, 128, 145], \"backgroundColor\": \"#4ECDC4\", \"borderColor\": \"#4ECDC4\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"APAC\", \"data\": [75, 88, 105, 125], \"backgroundColor\": \"#FFE66D\", \"borderColor\": \"#FFE66D\", \"borderWidth\": 2, \"borderRadius\": 10}]}, \"options\": {\"responsive\": true, \"maintainAspectRatio\": false, \"animation\": {\"duration\": 1500, \"easing\": \"easeInOutQuart\", \"delay\": 0, \"loop\": false, \"animateRotate\": true, \"animateScale\": true}, \"plugins\": {\"legend\": {\"display\": true, \"position\": \"top\", \"labels\": {\"font\": {\"size\": 14, \"weight\": \"bold\"}, \"padding\": 15, \"usePointStyle\": true}}, \"datalabels\": {\"display\": true, \"color\": \"#fff\", \"font\": {\"size\": 14, \"weight\": \"bold\"}, \"formatter\": \"function(value) { return value.toLocaleString(); }\", \"anchor\": \"end\", \"align\": \"end\", \"offset\": 0, \"backgroundColor\": \"rgba(0, 0, 0, 0.7)\", \"borderRadius\": 4, \"padding\": 6}, \"tooltip\": {\"enabled\": true, \"mode\": \"nearest\", \"intersect\": true}}, \"scales\": {\"x\": {\"display\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"autoSkip\": false, \"maxRotation\": 45, \"minRotation\": 0}, \"title\": {\"display\": true, \"text\": \"\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}, \"y\": {\"display\": true, \"beginAtZero\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"callback\": \"function(value) { return value.toLocaleString(); }\"}, \"title\": {\"display\": true, \"text\": \"Value\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}}}};\n        const chart = new Chart(ctx, chartConfig);\n\n        // Store reference for editor access\n        window.chartInstances = window.chartInstances || {};\n        window.chartInstances['chart-slide_001'] = chart;\n\n        console.log('✅ Chart chart-slide_001 initialized successfully');\n      }\n\n      // Reveal.js-aware initialization to ensure animations play\n      if (typeof Reveal !== 'undefined') {\n        // Wait for Reveal.js to be fully initialized before accessing methods\n        Reveal.on('ready', function() {\n          try {\n            const currentSlide = Reveal.getCurrentSlide();\n            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {\n              setTimeout(initChart, 100);  // Small delay for slide transition\n            }\n          } catch (e) {\n            console.warn('Chart init on ready failed:', e);\n          }\n        });\n\n        // v3.3.4: Always reinitialize on slide change to replay animation\n        Reveal.on('slidechanged', function(event) {\n          try {\n            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {\n              initChart();  // This now destroys old chart and creates new one\n            }\n          } catch (e) {\n            console.warn('Chart init on slide change failed:', e);\n          }\n        });\n      } else {\n        // No Reveal.js detected, init immediately (standalone mode)\n        if (document.readyState === 'loading') {\n          document.addEventListener('DOMContentLoaded', initChart);\n        } else {\n          initChart();\n        }\n      }\n    })();\n  <\/script>\n\n  <!-- Load Excel-like Spreadsheet Editor Library -->\n  <script src=\"https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js\"><\/script>\n\n  <!-- Excel Editor Function Definitions -->\n  <script>\n  (function() {\n      window.openChartEditor_chart_slide_001 = function() {\n        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');\n\n        // Get chart instance\n        const chart = window.chartInstances?.['chart-slide_001'];\n        if (!chart) {\n            console.error('Chart not found in window.chartInstances');\n            alert('Chart not ready. Please wait and try again.');\n            return;\n        }\n\n        console.log('✅ Chart found. Chart type:', chart.config.type);\n        console.log('Chart type parameter:', 'bar');\n\n        // Extract current chart data\n        const chartData = extractChartData_chart_slide_001(chart);\n\n        // === DIAGNOSTIC LOGGING ===\n        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');\n        console.log('Data type:', typeof chartData);\n        console.log('Is Array?:', Array.isArray(chartData));\n        console.log('Full data:', JSON.stringify(chartData, null, 2));\n\n        if (chartData && chartData.labels) {\n            console.log('✅ Multi-series format detected');\n            console.log('  Labels:', chartData.labels);\n            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);\n            if (chartData.datasets) {\n                chartData.datasets.forEach((ds, i) => {\n                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);\n                });\n            }\n        } else if (Array.isArray(chartData)) {\n            console.log('✅ Simple array format detected');\n            console.log('  Rows:', chartData.length);\n            if (chartData.length > 0) {\n                console.log('  First row sample:', chartData[0]);\n            }\n        }\n        console.log('Chart type parameter:', 'bar');\n        console.log('=== END DIAGNOSTIC DATA ===');\n\n        // Open Excel-like editor\n        openChartEditor(\n            'chart-slide_001',\n            'bar',\n            chartData,\n            {\n                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',\n                onSave: async (newData, chartId) => {\n                    console.log('Saving chart data:', newData);\n\n                    // Update chart instance\n                    updateChartData_chart_slide_001(chart, newData, 'bar');\n\n                    // Save to API\n                    try {\n                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({\n                                chart_id: chartId,\n                                presentation_id: 'fix_verify_001',\n                                data: newData,\n                                timestamp: Date.now()\n                            })\n                        });\n\n                        if (!response.ok) {\n                            throw new Error('API request failed');\n                        }\n\n                        console.log('✅ Chart data saved successfully');\n                    } catch (error) {\n                        console.error('❌ Error saving chart data:', error);\n                        throw error;\n                    }\n                }\n            }\n        );\n    };\n\n    // Extract data from chart instance based on chart type\n    function extractChartData_chart_slide_001(chart) {\n        const chartType = chart.config.type;\n\n        if (chartType === 'scatter') {\n            // Scatter: array of {x, y}\n            return chart.data.datasets[0]?.data || [];\n        } else if (chartType === 'bubble') {\n            // Bubble: array of {label, x, y, r}\n            return chart.data.datasets[0]?.data || [];\n        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {\n            // Check if multi-series\n            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {\n                // Multi-series format\n                return {\n                    labels: chart.data.labels || [],\n                    datasets: chart.data.datasets.map(ds => ({\n                        label: ds.label,\n                        data: ds.data\n                    }))\n                };\n            } else {\n                // Simple label-value format\n                const labels = chart.data.labels || [];\n                const values = chart.data.datasets[0]?.data || [];\n                return labels.map((label, i) => ({ label, value: values[i] }));\n            }\n        } else {\n            // Default: label-value format\n            const labels = chart.data.labels || [];\n            const values = chart.data.datasets[0]?.data || [];\n            return labels.map((label, i) => ({ label, value: values[i] }));\n        }\n    }\n\n    // Update chart instance with new data\n    function updateChartData_chart_slide_001(chart, newData, chartType) {\n        if (chartType === 'scatter' || chartType === 'bubble') {\n            // Object-based data\n            chart.data.datasets[0].data = newData;\n        } else if (newData.labels && newData.datasets) {\n            // Multi-series format\n            chart.data.labels = newData.labels;\n            chart.data.datasets = newData.datasets;\n        } else if (Array.isArray(newData)) {\n            // Simple label-value format\n            chart.data.labels = newData.map(d => d.label);\n            chart.data.datasets[0].data = newData.map(d => d.value);\n        }\n\n        chart.update();\n    }\n  })();\n  <\/script>\n<\/div>\n", "element_2": "<div class=\"l02-observations-panel\" style=\"width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;\">\n    <h3 style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;\">\n        Key Insights\n    <\/h3>\n    <ul style=\"margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;\">\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Executives should prioritize identifying challenges in each region to drive future performance improvements.\n        <\/li>\n    <\/ul>\n<\/div>", "presentation_name": "P0 Fixes Verification", "company_logo": "✅"}, "background_color": null, "background_image": null}], "id": "8270434d-8cfc-4cda-8bae-e52a60fa7ff0", "created_at": "2025-11-29T15:53:37.607337"};

    // Renderer registry (6 layouts)
    const RENDERERS = {
      'L01': window.renderL01,
      'L02': window.renderL02,
      'L03': window.renderL03,
      'L25': window.renderL25,
      'L27': window.renderL27,
      'L29': window.renderL29
    };

    /**
     * Render presentation from data
     */
    function renderPresentation(data) {
      if (!data || !data.slides) {
        console.error('Invalid presentation data');
        return;
      }

      const slidesContainer = document.getElementById('slides-container');
      slidesContainer.innerHTML = '';

      // Update document title
      document.title = data.title || 'Presentation';

      // Render each slide
      data.slides.forEach((slide, index) => {
        const layout = slide.layout;
        const content = slide.content;

        // Get renderer
        const renderer = RENDERERS[layout];
        if (!renderer) {
          console.error(`No renderer found for layout: ${layout}`);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Error: Unknown Layout</h2>
                <p>Layout '${layout}' is not supported in v7.5-main</p>
                <p>Valid layouts: L01, L02, L03, L25, L27, L29</p>
              </div>
            </section>
          `;
          return;
        }

        // Render slide
        try {
          const slideHTML = renderer(content, slide, index);

          // Create temporary container to parse HTML
          const tempContainer = document.createElement('div');
          tempContainer.innerHTML = slideHTML;

          // Extract all script tags before inserting HTML
          const scripts = tempContainer.querySelectorAll('script');

          // Insert the HTML while preserving previous DOM elements
          // Using appendChild instead of innerHTML += to avoid destroying previous slides
          const sections = tempContainer.querySelectorAll('section');
          sections.forEach(section => {
            slidesContainer.appendChild(section);
          });

          // Manually execute each script by creating new script elements
          scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy all attributes (src, type, async, defer, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });

            // Copy script content (for inline scripts)
            newScript.textContent = oldScript.textContent;

            // Append to document body - this triggers execution
            document.body.appendChild(newScript);
          });

        } catch (error) {
          console.error(`Error rendering slide ${index + 1}:`, error);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Rendering Error</h2>
                <p>Failed to render slide ${index + 1} (${layout})</p>
                <p>${error.message}</p>
              </div>
            </section>
          `;
        }
      });

      // Initialize Reveal.js AFTER scripts have time to execute
      setTimeout(() => {
        if (typeof initReveal === 'function') {
          initReveal();
        } else {
          // Fallback if reveal-config.js not loaded
          Reveal.initialize({
            width: 1920,
            height: 1080,
            margin: 0,
            minScale: 0.1,
            maxScale: 3.0,
            center: true,
            controls: true,
            progress: true,
            slideNumber: 'c/t',
            hash: true,
            history: true
          });
        }

        console.log(`✅ Presentation rendered: ${data.slides.length} slides`);
      }, 300);  // Give scripts 300ms to execute
    }

    /**
     * Show help text briefly
     */
    function showHelpText() {
      const helpText = document.getElementById('help-text');
      helpText.classList.add('show');
      setTimeout(() => {
        helpText.classList.remove('show');
      }, 3000);
    }

    // Add keyboard shortcuts (Note: 'B' and 'C' are handled by RevealJS config)
    document.addEventListener('keydown', (e) => {
      if (e.key === '?') {
        showHelpText();
      }
    });

    /**
     * postMessage Bridge for Cross-Origin Communication
     * Allows parent window from different origin to control the presentation
     *
     * Security: Validates message origin before executing commands
     */
    window.addEventListener('message', (event) => {
      // Security: Validate origin
      // Allow localhost (development), cloud platforms, and production frontend (deckster.xyz)
      const allowedOriginPattern = /^https?:\/\/(localhost:\d+|127\.0\.0\.1:\d+|.*\.up\.railway\.app|.*\.vercel\.app|.*\.netlify\.app|(www\.)?deckster\.xyz)$/;

      if (!allowedOriginPattern.test(event.origin)) {
        console.warn('⚠️ Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      const { action, params } = event.data || {};

      if (!action) {
        console.warn('⚠️ postMessage received without action:', event.data);
        return;
      }

      console.log(`📨 postMessage received: ${action}`, params);

      let result = { success: false, action };

      try {
        switch (action) {
          // Navigation functions
          case 'nextSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.next();
              result.success = true;
            }
            break;

          case 'prevSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.prev();
              result.success = true;
            }
            break;

          case 'goToSlide':
            if (typeof goToSlide === 'function' && params?.index !== undefined) {
              goToSlide(params.index);  // Now expects 0-based index
              result.success = true;
              result.slideIndex = params.index;
            } else if (typeof Reveal !== 'undefined' && params?.index !== undefined) {
              Reveal.slide(params.index);  // Fallback: direct call with 0-based index
              result.success = true;
              result.slideIndex = params.index;
            }
            break;

          case 'getCurrentSlideInfo':
            if (typeof getCurrentSlideInfo === 'function') {
              result.success = true;
              result.data = getCurrentSlideInfo();
            }
            break;

          // Edit mode functions
          case 'toggleEditMode':
            if (typeof toggleEditMode === 'function') {
              toggleEditMode();
              result.success = true;
              result.isEditing = document.body.getAttribute('data-mode') === 'edit';
            }
            break;

          case 'saveAllChanges':
            if (typeof saveAllChanges === 'function') {
              saveAllChanges();
              result.success = true;
            }
            break;

          case 'cancelEdits':
            if (typeof cancelEdits === 'function') {
              cancelEdits();
              result.success = true;
            }
            break;

          case 'showVersionHistory':
            if (typeof showVersionHistory === 'function') {
              showVersionHistory();
              result.success = true;
            }
            break;

          // Overview mode functions
          case 'toggleOverview':
            if (typeof toggleOverview === 'function') {
              toggleOverview();
              result.success = true;
              result.isOverview = isOverviewActive();
            } else if (typeof Reveal !== 'undefined') {
              Reveal.toggleOverview();
              result.success = true;
            }
            break;

          case 'isOverviewActive':
            if (typeof isOverviewActive === 'function') {
              result.success = true;
              result.data = isOverviewActive();
            }
            break;

          // Debug functions
          case 'toggleGridOverlay':
            if (typeof toggleGridOverlay === 'function') {
              toggleGridOverlay();
              result.success = true;
            }
            break;

          case 'toggleBorderHighlight':
            if (typeof toggleBorderHighlight === 'function') {
              toggleBorderHighlight();
              result.success = true;
            }
            break;

          // Review mode functions
          case 'toggleReviewMode':
            if (typeof toggleReviewMode === 'function') {
              toggleReviewMode();
              result.success = true;
              result.isReviewing = document.body.getAttribute('data-mode') === 'review';
            }
            break;

          case 'enterReviewMode':
            if (typeof enterReviewMode === 'function') {
              enterReviewMode();
              result.success = true;
              result.isReviewing = true;
            }
            break;

          case 'exitReviewMode':
            if (typeof exitReviewMode === 'function') {
              exitReviewMode();
              result.success = true;
              result.isReviewing = false;
            }
            break;

          case 'getSelectedSections':
            if (typeof getSelectedSections === 'function') {
              result.success = true;
              result.data = getSelectedSections();
            }
            break;

          case 'clearSelection':
            if (typeof clearSelection === 'function') {
              clearSelection();
              result.success = true;
            }
            break;

          default:
            console.warn(`⚠️ Unknown action: ${action}`);
            result.error = `Unknown action: ${action}`;
        }
      } catch (error) {
        console.error(`❌ Error executing action ${action}:`, error);
        result.success = false;
        result.error = error.message;
      }

      // Send response back to parent
      event.source.postMessage(result, event.origin);
      console.log(`📤 postMessage response sent:`, result);
    });

    console.log('✅ postMessage bridge initialized - ready for cross-origin commands');

    // Render presentation on load
    window.addEventListener('DOMContentLoaded', () => {
      if (PRESENTATION_DATA) {
        renderPresentation(PRESENTATION_DATA);
      } else {
        document.getElementById('slides-container').innerHTML = `
          <section>
            <div style="text-align: center; padding: 60px; color: #6b7280;">
              <h1 style="font-size: 48px; color: #1f2937;">No Presentation Data</h1>
              <p style="font-size: 24px; margin-top: 24px;">No presentation data was provided</p>
              <p style="font-size: 18px; margin-top: 16px; color: #9ca3af;">Use the API to create a presentation</p>
            </div>
          </section>
        `;
        if (typeof initReveal === 'function') {
          initReveal();
        }
      }

      // Show help text on first load
      setTimeout(showHelpText, 1000);
    });
  </script>
<svg id="SvgjsSvg1001" width="2" height="0" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev" style="overflow: hidden; top: -100%; left: -100%; position: absolute; opacity: 0;"><defs id="SvgjsDefs1002"></defs><polyline id="SvgjsPolyline1003" points="0,0"></polyline><path id="SvgjsPath1004" d="M0 0 "></path></svg>
<script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>
<script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>
<script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
<body class="reveal-viewport" style="--slide-width: 1920px; --slide-height: 1080px; --slide-scale: 0.765625;">
  <!-- Help Text -->
  <div id="help-text" class="">
    Press 'R' for review mode | 'E' for edit mode | 'G' for grid | 'B' for borders | '?' for help
  </div>

  <!-- Edit Mode UI -->
  <button id="toggle-edit-mode" onclick="toggleEditMode()">✏️ Edit Mode</button>

  <div id="edit-controls">
    <button id="save-btn" onclick="saveAllChanges()" title="Save Changes">💾</button>
    <button id="cancel-btn" onclick="cancelEdits()" title="Cancel">❌</button>
    <button id="view-history-btn" onclick="showVersionHistory()" title="Version History">📋</button>
  </div>

  <div id="edit-notification"></div>

  <div class="edit-shortcuts">
    <div><kbd>E</kbd> Toggle Edit Mode</div>
    <div><kbd>Ctrl+S</kbd> Save Changes</div>
    <div><kbd>ESC</kbd> Cancel</div>
  </div>

  <!-- Selection Indicator -->
  <div id="selection-indicator" class="selection-indicator"></div>

  <!-- AI Regeneration Panel -->
  <div id="regeneration-panel">
    <h3>🤖 AI Regeneration</h3>
    <div class="input-group">
      <input type="text" id="ai-instruction-input" placeholder="Enter instruction (e.g., Make it more engaging with examples)">
      <button id="regenerate-btn" onclick="regenerateSelectedSections()">
        Regenerate with AI
      </button>
      <button id="cancel-selection-btn" onclick="clearSelection()">
        Cancel
      </button>
    </div>
  </div>

  <!-- Reveal.js Container -->
  <div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>

  <!-- Reveal.js Core -->
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

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
      console.log('✅ Chart.js extended plugins loaded:', {
        treemap: typeof TreemapController !== 'undefined',
        matrix: typeof MatrixController !== 'undefined',
        boxplot: typeof BoxPlotController !== 'undefined',
        financial: typeof CandlestickController !== 'undefined',
        sankey: typeof SankeyController !== 'undefined'
      });
    } else {
      console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    }
  </script>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

  <!-- v7.5 Utilities -->
  <script src="/src/utils/format_ownership.js"></script>
  <script src="/src/utils/edit-mode.js"></script>
  <script src="/src/utils/review-mode.js"></script>
  <script src="/src/core/reveal-config.js"></script>

  <!-- Review Mode & AI Regeneration Components -->
  <script src="/src/components/regeneration-panel.js"></script>

  <!-- v7.5 Renderers (6 layouts) -->
  <script src="/src/renderers/L01.js"></script>
  <script src="/src/renderers/L02.js"></script>
  <script src="/src/renderers/L03.js"></script>
  <script src="/src/renderers/L25.js"></script>
  <script src="/src/renderers/L27.js"></script>
  <script src="/src/renderers/L29.js"></script>

  <!-- Presentation Rendering Script -->
  <script>
    // Presentation data (injected by server)
    const PRESENTATION_DATA = {"title": "Fix Verification - bar_grouped - Regional Performance", "slides": [{"layout": "L02", "content": {"slide_title": "Regional Performance Comparison", "element_1": "Q1-Q4 2024 by Region", "element_3": "<div class=\"l02-chart-container\" style=\"width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;\">\n  <canvas id=\"chart-slide_001\"><\/canvas>\n\n  <!-- Edit Button (Pencil Icon) -->\n  <button class=\"chart-edit-btn\"\n          onclick=\"openChartEditor_chart_slide_001()\"\n          style=\"position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;\"\n          onmouseover=\"this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit<\/span>'; this.style.background='rgba(0,0,0,0.8)'\"\n          onmouseout=\"this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'\">\n    ✏️\n  <\/button>\n\n  <script>\n    (function() {\n      function initChart() {\n        // v3.3.4: Destroy existing chart instance to force animation replay\n        if (window.chartInstances && window.chartInstances['chart-slide_001']) {\n          console.log('Chart chart-slide_001 exists, destroying to replay animation...');\n          window.chartInstances['chart-slide_001'].destroy();\n          delete window.chartInstances['chart-slide_001'];\n        }\n\n        const ctx = document.getElementById('chart-slide_001').getContext('2d');\n        const chartConfig = {\"type\": \"bar\", \"data\": {\"labels\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"], \"datasets\": [{\"label\": \"North America\", \"data\": [124, 145, 165, 180], \"backgroundColor\": \"#FF6B6B\", \"borderColor\": \"#FF6B6B\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"EMEA\", \"data\": [98, 112, 128, 145], \"backgroundColor\": \"#4ECDC4\", \"borderColor\": \"#4ECDC4\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"APAC\", \"data\": [75, 88, 105, 125], \"backgroundColor\": \"#FFE66D\", \"borderColor\": \"#FFE66D\", \"borderWidth\": 2, \"borderRadius\": 10}]}, \"options\": {\"responsive\": true, \"maintainAspectRatio\": false, \"animation\": {\"duration\": 1500, \"easing\": \"easeInOutQuart\", \"delay\": 0, \"loop\": false, \"animateRotate\": true, \"animateScale\": true}, \"plugins\": {\"legend\": {\"display\": true, \"position\": \"top\", \"labels\": {\"font\": {\"size\": 14, \"weight\": \"bold\"}, \"padding\": 15, \"usePointStyle\": true}}, \"datalabels\": {\"display\": true, \"color\": \"#fff\", \"font\": {\"size\": 14, \"weight\": \"bold\"}, \"formatter\": \"function(value) { return value.toLocaleString(); }\", \"anchor\": \"end\", \"align\": \"end\", \"offset\": 0, \"backgroundColor\": \"rgba(0, 0, 0, 0.7)\", \"borderRadius\": 4, \"padding\": 6}, \"tooltip\": {\"enabled\": true, \"mode\": \"nearest\", \"intersect\": true}}, \"scales\": {\"x\": {\"display\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"autoSkip\": false, \"maxRotation\": 45, \"minRotation\": 0}, \"title\": {\"display\": true, \"text\": \"\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}, \"y\": {\"display\": true, \"beginAtZero\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"callback\": \"function(value) { return value.toLocaleString(); }\"}, \"title\": {\"display\": true, \"text\": \"Value\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}}}};\n        const chart = new Chart(ctx, chartConfig);\n\n        // Store reference for editor access\n        window.chartInstances = window.chartInstances || {};\n        window.chartInstances['chart-slide_001'] = chart;\n\n        console.log('✅ Chart chart-slide_001 initialized successfully');\n      }\n\n      // Reveal.js-aware initialization to ensure animations play\n      if (typeof Reveal !== 'undefined') {\n        // Wait for Reveal.js to be fully initialized before accessing methods\n        Reveal.on('ready', function() {\n          try {\n            const currentSlide = Reveal.getCurrentSlide();\n            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {\n              setTimeout(initChart, 100);  // Small delay for slide transition\n            }\n          } catch (e) {\n            console.warn('Chart init on ready failed:', e);\n          }\n        });\n\n        // v3.3.4: Always reinitialize on slide change to replay animation\n        Reveal.on('slidechanged', function(event) {\n          try {\n            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {\n              initChart();  // This now destroys old chart and creates new one\n            }\n          } catch (e) {\n            console.warn('Chart init on slide change failed:', e);\n          }\n        });\n      } else {\n        // No Reveal.js detected, init immediately (standalone mode)\n        if (document.readyState === 'loading') {\n          document.addEventListener('DOMContentLoaded', initChart);\n        } else {\n          initChart();\n        }\n      }\n    })();\n  <\/script>\n\n  <!-- Load Excel-like Spreadsheet Editor Library -->\n  <script src=\"https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js\"><\/script>\n\n  <!-- Excel Editor Function Definitions -->\n  <script>\n  (function() {\n      window.openChartEditor_chart_slide_001 = function() {\n        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');\n\n        // Get chart instance\n        const chart = window.chartInstances?.['chart-slide_001'];\n        if (!chart) {\n            console.error('Chart not found in window.chartInstances');\n            alert('Chart not ready. Please wait and try again.');\n            return;\n        }\n\n        console.log('✅ Chart found. Chart type:', chart.config.type);\n        console.log('Chart type parameter:', 'bar');\n\n        // Extract current chart data\n        const chartData = extractChartData_chart_slide_001(chart);\n\n        // === DIAGNOSTIC LOGGING ===\n        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');\n        console.log('Data type:', typeof chartData);\n        console.log('Is Array?:', Array.isArray(chartData));\n        console.log('Full data:', JSON.stringify(chartData, null, 2));\n\n        if (chartData && chartData.labels) {\n            console.log('✅ Multi-series format detected');\n            console.log('  Labels:', chartData.labels);\n            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);\n            if (chartData.datasets) {\n                chartData.datasets.forEach((ds, i) => {\n                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);\n                });\n            }\n        } else if (Array.isArray(chartData)) {\n            console.log('✅ Simple array format detected');\n            console.log('  Rows:', chartData.length);\n            if (chartData.length > 0) {\n                console.log('  First row sample:', chartData[0]);\n            }\n        }\n        console.log('Chart type parameter:', 'bar');\n        console.log('=== END DIAGNOSTIC DATA ===');\n\n        // Open Excel-like editor\n        openChartEditor(\n            'chart-slide_001',\n            'bar',\n            chartData,\n            {\n                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',\n                onSave: async (newData, chartId) => {\n                    console.log('Saving chart data:', newData);\n\n                    // Update chart instance\n                    updateChartData_chart_slide_001(chart, newData, 'bar');\n\n                    // Save to API\n                    try {\n                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({\n                                chart_id: chartId,\n                                presentation_id: 'fix_verify_001',\n                                data: newData,\n                                timestamp: Date.now()\n                            })\n                        });\n\n                        if (!response.ok) {\n                            throw new Error('API request failed');\n                        }\n\n                        console.log('✅ Chart data saved successfully');\n                    } catch (error) {\n                        console.error('❌ Error saving chart data:', error);\n                        throw error;\n                    }\n                }\n            }\n        );\n    };\n\n    // Extract data from chart instance based on chart type\n    function extractChartData_chart_slide_001(chart) {\n        const chartType = chart.config.type;\n\n        if (chartType === 'scatter') {\n            // Scatter: array of {x, y}\n            return chart.data.datasets[0]?.data || [];\n        } else if (chartType === 'bubble') {\n            // Bubble: array of {label, x, y, r}\n            return chart.data.datasets[0]?.data || [];\n        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {\n            // Check if multi-series\n            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {\n                // Multi-series format\n                return {\n                    labels: chart.data.labels || [],\n                    datasets: chart.data.datasets.map(ds => ({\n                        label: ds.label,\n                        data: ds.data\n                    }))\n                };\n            } else {\n                // Simple label-value format\n                const labels = chart.data.labels || [];\n                const values = chart.data.datasets[0]?.data || [];\n                return labels.map((label, i) => ({ label, value: values[i] }));\n            }\n        } else {\n            // Default: label-value format\n            const labels = chart.data.labels || [];\n            const values = chart.data.datasets[0]?.data || [];\n            return labels.map((label, i) => ({ label, value: values[i] }));\n        }\n    }\n\n    // Update chart instance with new data\n    function updateChartData_chart_slide_001(chart, newData, chartType) {\n        if (chartType === 'scatter' || chartType === 'bubble') {\n            // Object-based data\n            chart.data.datasets[0].data = newData;\n        } else if (newData.labels && newData.datasets) {\n            // Multi-series format\n            chart.data.labels = newData.labels;\n            chart.data.datasets = newData.datasets;\n        } else if (Array.isArray(newData)) {\n            // Simple label-value format\n            chart.data.labels = newData.map(d => d.label);\n            chart.data.datasets[0].data = newData.map(d => d.value);\n        }\n\n        chart.update();\n    }\n  })();\n  <\/script>\n<\/div>\n", "element_2": "<div class=\"l02-observations-panel\" style=\"width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;\">\n    <h3 style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;\">\n        Key Insights\n    <\/h3>\n    <ul style=\"margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;\">\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Executives should prioritize identifying challenges in each region to drive future performance improvements.\n        <\/li>\n    <\/ul>\n<\/div>", "presentation_name": "P0 Fixes Verification", "company_logo": "✅"}, "background_color": null, "background_image": null}], "id": "8270434d-8cfc-4cda-8bae-e52a60fa7ff0", "created_at": "2025-11-29T15:53:37.607337"};

    // Renderer registry (6 layouts)
    const RENDERERS = {
      'L01': window.renderL01,
      'L02': window.renderL02,
      'L03': window.renderL03,
      'L25': window.renderL25,
      'L27': window.renderL27,
      'L29': window.renderL29
    };

    /**
     * Render presentation from data
     */
    function renderPresentation(data) {
      if (!data || !data.slides) {
        console.error('Invalid presentation data');
        return;
      }

      const slidesContainer = document.getElementById('slides-container');
      slidesContainer.innerHTML = '';

      // Update document title
      document.title = data.title || 'Presentation';

      // Render each slide
      data.slides.forEach((slide, index) => {
        const layout = slide.layout;
        const content = slide.content;

        // Get renderer
        const renderer = RENDERERS[layout];
        if (!renderer) {
          console.error(`No renderer found for layout: ${layout}`);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Error: Unknown Layout</h2>
                <p>Layout '${layout}' is not supported in v7.5-main</p>
                <p>Valid layouts: L01, L02, L03, L25, L27, L29</p>
              </div>
            </section>
          `;
          return;
        }

        // Render slide
        try {
          const slideHTML = renderer(content, slide, index);

          // Create temporary container to parse HTML
          const tempContainer = document.createElement('div');
          tempContainer.innerHTML = slideHTML;

          // Extract all script tags before inserting HTML
          const scripts = tempContainer.querySelectorAll('script');

          // Insert the HTML while preserving previous DOM elements
          // Using appendChild instead of innerHTML += to avoid destroying previous slides
          const sections = tempContainer.querySelectorAll('section');
          sections.forEach(section => {
            slidesContainer.appendChild(section);
          });

          // Manually execute each script by creating new script elements
          scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy all attributes (src, type, async, defer, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });

            // Copy script content (for inline scripts)
            newScript.textContent = oldScript.textContent;

            // Append to document body - this triggers execution
            document.body.appendChild(newScript);
          });

        } catch (error) {
          console.error(`Error rendering slide ${index + 1}:`, error);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Rendering Error</h2>
                <p>Failed to render slide ${index + 1} (${layout})</p>
                <p>${error.message}</p>
              </div>
            </section>
          `;
        }
      });

      // Initialize Reveal.js AFTER scripts have time to execute
      setTimeout(() => {
        if (typeof initReveal === 'function') {
          initReveal();
        } else {
          // Fallback if reveal-config.js not loaded
          Reveal.initialize({
            width: 1920,
            height: 1080,
            margin: 0,
            minScale: 0.1,
            maxScale: 3.0,
            center: true,
            controls: true,
            progress: true,
            slideNumber: 'c/t',
            hash: true,
            history: true
          });
        }

        console.log(`✅ Presentation rendered: ${data.slides.length} slides`);
      }, 300);  // Give scripts 300ms to execute
    }

    /**
     * Show help text briefly
     */
    function showHelpText() {
      const helpText = document.getElementById('help-text');
      helpText.classList.add('show');
      setTimeout(() => {
        helpText.classList.remove('show');
      }, 3000);
    }

    // Add keyboard shortcuts (Note: 'B' and 'C' are handled by RevealJS config)
    document.addEventListener('keydown', (e) => {
      if (e.key === '?') {
        showHelpText();
      }
    });

    /**
     * postMessage Bridge for Cross-Origin Communication
     * Allows parent window from different origin to control the presentation
     *
     * Security: Validates message origin before executing commands
     */
    window.addEventListener('message', (event) => {
      // Security: Validate origin
      // Allow localhost (development), cloud platforms, and production frontend (deckster.xyz)
      const allowedOriginPattern = /^https?:\/\/(localhost:\d+|127\.0\.0\.1:\d+|.*\.up\.railway\.app|.*\.vercel\.app|.*\.netlify\.app|(www\.)?deckster\.xyz)$/;

      if (!allowedOriginPattern.test(event.origin)) {
        console.warn('⚠️ Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      const { action, params } = event.data || {};

      if (!action) {
        console.warn('⚠️ postMessage received without action:', event.data);
        return;
      }

      console.log(`📨 postMessage received: ${action}`, params);

      let result = { success: false, action };

      try {
        switch (action) {
          // Navigation functions
          case 'nextSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.next();
              result.success = true;
            }
            break;

          case 'prevSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.prev();
              result.success = true;
            }
            break;

          case 'goToSlide':
            if (typeof goToSlide === 'function' && params?.index !== undefined) {
              goToSlide(params.index);  // Now expects 0-based index
              result.success = true;
              result.slideIndex = params.index;
            } else if (typeof Reveal !== 'undefined' && params?.index !== undefined) {
              Reveal.slide(params.index);  // Fallback: direct call with 0-based index
              result.success = true;
              result.slideIndex = params.index;
            }
            break;

          case 'getCurrentSlideInfo':
            if (typeof getCurrentSlideInfo === 'function') {
              result.success = true;
              result.data = getCurrentSlideInfo();
            }
            break;

          // Edit mode functions
          case 'toggleEditMode':
            if (typeof toggleEditMode === 'function') {
              toggleEditMode();
              result.success = true;
              result.isEditing = document.body.getAttribute('data-mode') === 'edit';
            }
            break;

          case 'saveAllChanges':
            if (typeof saveAllChanges === 'function') {
              saveAllChanges();
              result.success = true;
            }
            break;

          case 'cancelEdits':
            if (typeof cancelEdits === 'function') {
              cancelEdits();
              result.success = true;
            }
            break;

          case 'showVersionHistory':
            if (typeof showVersionHistory === 'function') {
              showVersionHistory();
              result.success = true;
            }
            break;

          // Overview mode functions
          case 'toggleOverview':
            if (typeof toggleOverview === 'function') {
              toggleOverview();
              result.success = true;
              result.isOverview = isOverviewActive();
            } else if (typeof Reveal !== 'undefined') {
              Reveal.toggleOverview();
              result.success = true;
            }
            break;

          case 'isOverviewActive':
            if (typeof isOverviewActive === 'function') {
              result.success = true;
              result.data = isOverviewActive();
            }
            break;

          // Debug functions
          case 'toggleGridOverlay':
            if (typeof toggleGridOverlay === 'function') {
              toggleGridOverlay();
              result.success = true;
            }
            break;

          case 'toggleBorderHighlight':
            if (typeof toggleBorderHighlight === 'function') {
              toggleBorderHighlight();
              result.success = true;
            }
            break;

          // Review mode functions
          case 'toggleReviewMode':
            if (typeof toggleReviewMode === 'function') {
              toggleReviewMode();
              result.success = true;
              result.isReviewing = document.body.getAttribute('data-mode') === 'review';
            }
            break;

          case 'enterReviewMode':
            if (typeof enterReviewMode === 'function') {
              enterReviewMode();
              result.success = true;
              result.isReviewing = true;
            }
            break;

          case 'exitReviewMode':
            if (typeof exitReviewMode === 'function') {
              exitReviewMode();
              result.success = true;
              result.isReviewing = false;
            }
            break;

          case 'getSelectedSections':
            if (typeof getSelectedSections === 'function') {
              result.success = true;
              result.data = getSelectedSections();
            }
            break;

          case 'clearSelection':
            if (typeof clearSelection === 'function') {
              clearSelection();
              result.success = true;
            }
            break;

          default:
            console.warn(`⚠️ Unknown action: ${action}`);
            result.error = `Unknown action: ${action}`;
        }
      } catch (error) {
        console.error(`❌ Error executing action ${action}:`, error);
        result.success = false;
        result.error = error.message;
      }

      // Send response back to parent
      event.source.postMessage(result, event.origin);
      console.log(`📤 postMessage response sent:`, result);
    });

    console.log('✅ postMessage bridge initialized - ready for cross-origin commands');

    // Render presentation on load
    window.addEventListener('DOMContentLoaded', () => {
      if (PRESENTATION_DATA) {
        renderPresentation(PRESENTATION_DATA);
      } else {
        document.getElementById('slides-container').innerHTML = `
          <section>
            <div style="text-align: center; padding: 60px; color: #6b7280;">
              <h1 style="font-size: 48px; color: #1f2937;">No Presentation Data</h1>
              <p style="font-size: 24px; margin-top: 24px;">No presentation data was provided</p>
              <p style="font-size: 18px; margin-top: 16px; color: #9ca3af;">Use the API to create a presentation</p>
            </div>
          </section>
        `;
        if (typeof initReveal === 'function') {
          initReveal();
        }
      }

      // Show help text on first load
      setTimeout(showHelpText, 1000);
    });
  </script>


<svg id="SvgjsSvg1001" width="2" height="0" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev" style="overflow: hidden; top: -100%; left: -100%; position: absolute; opacity: 0;"><defs id="SvgjsDefs1002"></defs><polyline id="SvgjsPolyline1003" points="0,0"></polyline><path id="SvgjsPath1004" d="M0 0 "></path></svg><script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script><script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script><script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script></body>
<html lang="en" class="reveal-full-page"><head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fix Verification - bar_grouped - Regional Performance</title>

  <!-- Reveal.js Core -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/theme/white.css">

  <!-- v7.5 Styles -->
  <link rel="stylesheet" href="/src/styles/core/reset.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/grid-system.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/core/borders.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/content-area.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/edit-mode.css?v=20251116">
  <link rel="stylesheet" href="/src/styles/review-mode.css?v=20250124">
  <link rel="stylesheet" href="/src/styles/regeneration-panel.css?v=20250124">

  <style>
    /* Minimal additional styling */
    body {
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    }

    .reveal {
      background: #ffffff;
    }

    /* Help text */
    #help-text {
      position: fixed;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(0,0,0,0.8);
      color: white;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 12px;
      z-index: 10000;
      opacity: 0;
      transition: opacity 0.3s;
    }

    #help-text.show {
      opacity: 1;
    }
  </style>
<style>
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
</style></head>
<body class="reveal-viewport" style="--slide-width: 1920px; --slide-height: 1080px; --slide-scale: 0.765625;">
  <!-- Help Text -->
  <div id="help-text" class="">
    Press 'R' for review mode | 'E' for edit mode | 'G' for grid | 'B' for borders | '?' for help
  </div>

  <!-- Edit Mode UI -->
  <button id="toggle-edit-mode" onclick="toggleEditMode()">✏️ Edit Mode</button>

  <div id="edit-controls">
    <button id="save-btn" onclick="saveAllChanges()" title="Save Changes">💾</button>
    <button id="cancel-btn" onclick="cancelEdits()" title="Cancel">❌</button>
    <button id="view-history-btn" onclick="showVersionHistory()" title="Version History">📋</button>
  </div>

  <div id="edit-notification"></div>

  <div class="edit-shortcuts">
    <div><kbd>E</kbd> Toggle Edit Mode</div>
    <div><kbd>Ctrl+S</kbd> Save Changes</div>
    <div><kbd>ESC</kbd> Cancel</div>
  </div>

  <!-- Selection Indicator -->
  <div id="selection-indicator" class="selection-indicator"></div>

  <!-- AI Regeneration Panel -->
  <div id="regeneration-panel">
    <h3>🤖 AI Regeneration</h3>
    <div class="input-group">
      <input type="text" id="ai-instruction-input" placeholder="Enter instruction (e.g., Make it more engaging with examples)">
      <button id="regenerate-btn" onclick="regenerateSelectedSections()">
        Regenerate with AI
      </button>
      <button id="cancel-selection-btn" onclick="clearSelection()">
        Cancel
      </button>
    </div>
  </div>

  <!-- Reveal.js Container -->
  <div class="reveal slide center focused ready" role="application" data-transition-speed="default" data-background-transition="fade" style="cursor: none;">
    <div class="slides" id="slides-container" style="width: 1920px; height: 1080px; inset: 50% auto auto 50%; transform: translate(-50%, -50%) scale(0.765625);"><section data-layout="L02" class="content-slide grid-container present" style="top: 0px; display: block;">
      <!-- Title (42px bold, matching L25) -->
      <div class="slide-title" data-section-id="slide-0-section-title" data-section-type="title" data-slide-index="0" style="grid-row: 2/3; grid-column: 2/32; font-size: 42px; font-weight: bold; color: #1f2937; line-height: 1.2;">
        Regional Performance Comparison
      </div>

      <!-- Subtitle (24px, matching L25) -->
      <div class="subtitle" data-section-id="slide-0-section-subtitle" data-section-type="subtitle" data-slide-index="0" style="grid-row: 3/4; grid-column: 2/32; font-size: 24px; color: #6b7280; line-height: 1.4; margin-top: 8px;">
        Q1-Q4 2024 by Region
      </div>

      <!-- Left: Diagram/Chart Container (1260px × 720px) -->
      <div class="diagram-container" data-section-id="slide-0-section-diagram" data-section-type="diagram" data-slide-index="0" style="grid-row: 5/17; grid-column: 2/23; width: 100%; height: 100%; overflow: visible; display: block;">
        <div class="l02-chart-container" style="width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;">
  <canvas id="chart-slide_001" width="2440" height="1360" style="display: block; box-sizing: border-box; height: 680px; width: 1220px;"></canvas>

  <!-- Edit Button (Pencil Icon) -->
  <button class="chart-edit-btn" onclick="openChartEditor_chart_slide_001()" style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;" onmouseover="this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit</span>'; this.style.background='rgba(0,0,0,0.8)'" onmouseout="this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'">
    ✏️
  </button>

  <script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script>

  <!-- Load Excel-like Spreadsheet Editor Library -->
  <script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script>

  <!-- Excel Editor Function Definitions -->
  <script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script>
</div>

      </div>

      <!-- Right: Observations/Text Container (540px × 720px) -->
      <div class="body-primary" data-section-id="slide-0-section-text" data-section-type="text" data-slide-index="0" style="grid-row: 5/17; grid-column: 23/32; width: 100%; height: 100%; overflow: auto;">
        <div class="l02-observations-panel" style="width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        Key Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.
        </li>
        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;">
            Executives should prioritize identifying challenges in each region to drive future performance improvements.
        </li>
    </ul>
</div>
      </div>

      <!-- Footer: Presentation Name (18px, matching L25) -->
      
      <div class="footer-presentation-name" style="grid-row: 18/19; grid-column: 2/7; padding: 8px 14px; font-size: 18px; color: #1f2937; font-weight: 500; display: flex; align-items: center; height: 100%;">
        P0 Fixes Verification
      </div>
      

      <!-- Footer: Company Logo (bottom-right, matching L27) -->
      
      <div class="footer-company-logo" style="grid-row: 17/19; grid-column: 30/32; display: flex; align-items: center; justify-content: center; padding: 10px;">
        <div style="max-width: 50%; max-height: 50%; display: flex; align-items: center; justify-content: center; font-size: 36px;">
          ✅
        </div>
      </div>
      
    </section></div>
  <div class="backgrounds"><div class="slide-background content-slide grid-container present" data-loaded="true" style="display: block;"><div class="slide-background-content"></div></div></div><div class="slide-number" style="display: block;"><a href="#/">
					<span class="slide-number-a">1</span>
					<span class="slide-number-delimiter">/</span>
					<span class="slide-number-b">1</span>
					</a></div><aside class="controls" data-controls-layout="bottom-right" data-controls-back-arrows="faded" style="display: block;"><button class="navigate-left" aria-label="previous slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-right" aria-label="next slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-up" aria-label="above slide" disabled="disabled"><div class="controls-arrow"></div></button>
			<button class="navigate-down" aria-label="below slide" disabled="disabled"><div class="controls-arrow"></div></button></aside><div class="progress" style="display: block;"><span style="transform: scaleX(0);"></span></div><div class="speaker-notes" data-prevent-swipe="" tabindex="0"></div><div class="pause-overlay"><button class="resume-button">Resume presentation</button></div><div class="aria-status" aria-live="polite" aria-atomic="true" style="position: absolute; height: 1px; width: 1px; overflow: hidden; clip: rect(1px, 1px, 1px, 1px);">Regional Performance Comparison Q1-Q4 2024 by Region ✏️ Key Insights The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero. Each region reported zero performance for all four quarters, indicating a lack of growth or activity. The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement. With averages and totals remaining at zero, there is a clear need to investigate underlying issues. Executives should prioritize identifying challenges in each region to drive future performance improvements. P0 Fixes Verification ✅ </div></div>

  <!-- Reveal.js Core -->
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@4.5.0/dist/reveal.js"></script>

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
      console.log('✅ Chart.js extended plugins loaded:', {
        treemap: typeof TreemapController !== 'undefined',
        matrix: typeof MatrixController !== 'undefined',
        boxplot: typeof BoxPlotController !== 'undefined',
        financial: typeof CandlestickController !== 'undefined',
        sankey: typeof SankeyController !== 'undefined'
      });
    } else {
      console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
    }
  </script>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

  <!-- v7.5 Utilities -->
  <script src="/src/utils/format_ownership.js"></script>
  <script src="/src/utils/edit-mode.js"></script>
  <script src="/src/utils/review-mode.js"></script>
  <script src="/src/core/reveal-config.js"></script>

  <!-- Review Mode & AI Regeneration Components -->
  <script src="/src/components/regeneration-panel.js"></script>

  <!-- v7.5 Renderers (6 layouts) -->
  <script src="/src/renderers/L01.js"></script>
  <script src="/src/renderers/L02.js"></script>
  <script src="/src/renderers/L03.js"></script>
  <script src="/src/renderers/L25.js"></script>
  <script src="/src/renderers/L27.js"></script>
  <script src="/src/renderers/L29.js"></script>

  <!-- Presentation Rendering Script -->
  <script>
    // Presentation data (injected by server)
    const PRESENTATION_DATA = {"title": "Fix Verification - bar_grouped - Regional Performance", "slides": [{"layout": "L02", "content": {"slide_title": "Regional Performance Comparison", "element_1": "Q1-Q4 2024 by Region", "element_3": "<div class=\"l02-chart-container\" style=\"width: 1260px; height: 720px; position: relative; background: white; padding: 20px; box-sizing: border-box;\">\n  <canvas id=\"chart-slide_001\"><\/canvas>\n\n  <!-- Edit Button (Pencil Icon) -->\n  <button class=\"chart-edit-btn\"\n          onclick=\"openChartEditor_chart_slide_001()\"\n          style=\"position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.6); color: white; border: none; padding: 8px; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 16px; z-index: 100; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; overflow: hidden; white-space: nowrap;\"\n          onmouseover=\"this.style.width='80px'; this.style.borderRadius='20px'; this.innerHTML='✏️ <span style=&quot;margin-left: 6px; font-size: 13px;&quot;>edit<\/span>'; this.style.background='rgba(0,0,0,0.8)'\"\n          onmouseout=\"this.style.width='36px'; this.style.borderRadius='50%'; this.innerHTML='✏️'; this.style.background='rgba(0,0,0,0.6)'\">\n    ✏️\n  <\/button>\n\n  <script>\n    (function() {\n      function initChart() {\n        // v3.3.4: Destroy existing chart instance to force animation replay\n        if (window.chartInstances && window.chartInstances['chart-slide_001']) {\n          console.log('Chart chart-slide_001 exists, destroying to replay animation...');\n          window.chartInstances['chart-slide_001'].destroy();\n          delete window.chartInstances['chart-slide_001'];\n        }\n\n        const ctx = document.getElementById('chart-slide_001').getContext('2d');\n        const chartConfig = {\"type\": \"bar\", \"data\": {\"labels\": [\"Q1\", \"Q2\", \"Q3\", \"Q4\"], \"datasets\": [{\"label\": \"North America\", \"data\": [124, 145, 165, 180], \"backgroundColor\": \"#FF6B6B\", \"borderColor\": \"#FF6B6B\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"EMEA\", \"data\": [98, 112, 128, 145], \"backgroundColor\": \"#4ECDC4\", \"borderColor\": \"#4ECDC4\", \"borderWidth\": 2, \"borderRadius\": 10}, {\"label\": \"APAC\", \"data\": [75, 88, 105, 125], \"backgroundColor\": \"#FFE66D\", \"borderColor\": \"#FFE66D\", \"borderWidth\": 2, \"borderRadius\": 10}]}, \"options\": {\"responsive\": true, \"maintainAspectRatio\": false, \"animation\": {\"duration\": 1500, \"easing\": \"easeInOutQuart\", \"delay\": 0, \"loop\": false, \"animateRotate\": true, \"animateScale\": true}, \"plugins\": {\"legend\": {\"display\": true, \"position\": \"top\", \"labels\": {\"font\": {\"size\": 14, \"weight\": \"bold\"}, \"padding\": 15, \"usePointStyle\": true}}, \"datalabels\": {\"display\": true, \"color\": \"#fff\", \"font\": {\"size\": 14, \"weight\": \"bold\"}, \"formatter\": \"function(value) { return value.toLocaleString(); }\", \"anchor\": \"end\", \"align\": \"end\", \"offset\": 0, \"backgroundColor\": \"rgba(0, 0, 0, 0.7)\", \"borderRadius\": 4, \"padding\": 6}, \"tooltip\": {\"enabled\": true, \"mode\": \"nearest\", \"intersect\": true}}, \"scales\": {\"x\": {\"display\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"autoSkip\": false, \"maxRotation\": 45, \"minRotation\": 0}, \"title\": {\"display\": true, \"text\": \"\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}, \"y\": {\"display\": true, \"beginAtZero\": true, \"grid\": {\"display\": true, \"color\": \"rgba(0, 0, 0, 0.08)\", \"lineWidth\": 1}, \"ticks\": {\"display\": true, \"font\": {\"size\": 12, \"weight\": \"500\"}, \"color\": \"#333\", \"padding\": 8, \"callback\": \"function(value) { return value.toLocaleString(); }\"}, \"title\": {\"display\": true, \"text\": \"Value\", \"font\": {\"size\": 13, \"weight\": \"bold\"}, \"color\": \"#333\"}}}}};\n        const chart = new Chart(ctx, chartConfig);\n\n        // Store reference for editor access\n        window.chartInstances = window.chartInstances || {};\n        window.chartInstances['chart-slide_001'] = chart;\n\n        console.log('✅ Chart chart-slide_001 initialized successfully');\n      }\n\n      // Reveal.js-aware initialization to ensure animations play\n      if (typeof Reveal !== 'undefined') {\n        // Wait for Reveal.js to be fully initialized before accessing methods\n        Reveal.on('ready', function() {\n          try {\n            const currentSlide = Reveal.getCurrentSlide();\n            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {\n              setTimeout(initChart, 100);  // Small delay for slide transition\n            }\n          } catch (e) {\n            console.warn('Chart init on ready failed:', e);\n          }\n        });\n\n        // v3.3.4: Always reinitialize on slide change to replay animation\n        Reveal.on('slidechanged', function(event) {\n          try {\n            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {\n              initChart();  // This now destroys old chart and creates new one\n            }\n          } catch (e) {\n            console.warn('Chart init on slide change failed:', e);\n          }\n        });\n      } else {\n        // No Reveal.js detected, init immediately (standalone mode)\n        if (document.readyState === 'loading') {\n          document.addEventListener('DOMContentLoaded', initChart);\n        } else {\n          initChart();\n        }\n      }\n    })();\n  <\/script>\n\n  <!-- Load Excel-like Spreadsheet Editor Library -->\n  <script src=\"https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js\"><\/script>\n\n  <!-- Excel Editor Function Definitions -->\n  <script>\n  (function() {\n      window.openChartEditor_chart_slide_001 = function() {\n        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');\n\n        // Get chart instance\n        const chart = window.chartInstances?.['chart-slide_001'];\n        if (!chart) {\n            console.error('Chart not found in window.chartInstances');\n            alert('Chart not ready. Please wait and try again.');\n            return;\n        }\n\n        console.log('✅ Chart found. Chart type:', chart.config.type);\n        console.log('Chart type parameter:', 'bar');\n\n        // Extract current chart data\n        const chartData = extractChartData_chart_slide_001(chart);\n\n        // === DIAGNOSTIC LOGGING ===\n        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');\n        console.log('Data type:', typeof chartData);\n        console.log('Is Array?:', Array.isArray(chartData));\n        console.log('Full data:', JSON.stringify(chartData, null, 2));\n\n        if (chartData && chartData.labels) {\n            console.log('✅ Multi-series format detected');\n            console.log('  Labels:', chartData.labels);\n            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);\n            if (chartData.datasets) {\n                chartData.datasets.forEach((ds, i) => {\n                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);\n                });\n            }\n        } else if (Array.isArray(chartData)) {\n            console.log('✅ Simple array format detected');\n            console.log('  Rows:', chartData.length);\n            if (chartData.length > 0) {\n                console.log('  First row sample:', chartData[0]);\n            }\n        }\n        console.log('Chart type parameter:', 'bar');\n        console.log('=== END DIAGNOSTIC DATA ===');\n\n        // Open Excel-like editor\n        openChartEditor(\n            'chart-slide_001',\n            'bar',\n            chartData,\n            {\n                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',\n                onSave: async (newData, chartId) => {\n                    console.log('Saving chart data:', newData);\n\n                    // Update chart instance\n                    updateChartData_chart_slide_001(chart, newData, 'bar');\n\n                    // Save to API\n                    try {\n                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {\n                            method: 'POST',\n                            headers: { 'Content-Type': 'application/json' },\n                            body: JSON.stringify({\n                                chart_id: chartId,\n                                presentation_id: 'fix_verify_001',\n                                data: newData,\n                                timestamp: Date.now()\n                            })\n                        });\n\n                        if (!response.ok) {\n                            throw new Error('API request failed');\n                        }\n\n                        console.log('✅ Chart data saved successfully');\n                    } catch (error) {\n                        console.error('❌ Error saving chart data:', error);\n                        throw error;\n                    }\n                }\n            }\n        );\n    };\n\n    // Extract data from chart instance based on chart type\n    function extractChartData_chart_slide_001(chart) {\n        const chartType = chart.config.type;\n\n        if (chartType === 'scatter') {\n            // Scatter: array of {x, y}\n            return chart.data.datasets[0]?.data || [];\n        } else if (chartType === 'bubble') {\n            // Bubble: array of {label, x, y, r}\n            return chart.data.datasets[0]?.data || [];\n        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {\n            // Check if multi-series\n            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {\n                // Multi-series format\n                return {\n                    labels: chart.data.labels || [],\n                    datasets: chart.data.datasets.map(ds => ({\n                        label: ds.label,\n                        data: ds.data\n                    }))\n                };\n            } else {\n                // Simple label-value format\n                const labels = chart.data.labels || [];\n                const values = chart.data.datasets[0]?.data || [];\n                return labels.map((label, i) => ({ label, value: values[i] }));\n            }\n        } else {\n            // Default: label-value format\n            const labels = chart.data.labels || [];\n            const values = chart.data.datasets[0]?.data || [];\n            return labels.map((label, i) => ({ label, value: values[i] }));\n        }\n    }\n\n    // Update chart instance with new data\n    function updateChartData_chart_slide_001(chart, newData, chartType) {\n        if (chartType === 'scatter' || chartType === 'bubble') {\n            // Object-based data\n            chart.data.datasets[0].data = newData;\n        } else if (newData.labels && newData.datasets) {\n            // Multi-series format\n            chart.data.labels = newData.labels;\n            chart.data.datasets = newData.datasets;\n        } else if (Array.isArray(newData)) {\n            // Simple label-value format\n            chart.data.labels = newData.map(d => d.label);\n            chart.data.datasets[0].data = newData.map(d => d.value);\n        }\n\n        chart.update();\n    }\n  })();\n  <\/script>\n<\/div>\n", "element_2": "<div class=\"l02-observations-panel\" style=\"width: 540px; height: 720px; padding: 40px 32px; background: #f8f9fa; border-radius: 8px; overflow-y: auto; box-sizing: border-box;\">\n    <h3 style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: #1f2937; margin: 0 0 18px 0; line-height: 1.3; text-align: left;\">\n        Key Insights\n    <\/h3>\n    <ul style=\"margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;\">\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The bar_grouped chart illustrates quarterly performance across three regions, revealing consistent metrics at zero.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Each region reported zero performance for all four quarters, indicating a lack of growth or activity.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            The data shows no fluctuations, suggesting stability, but also a missed opportunity for advancement.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            With averages and totals remaining at zero, there is a clear need to investigate underlying issues.\n        <\/li>\n        <li style=\"font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: #374151; margin: 0 0 10px 0; text-align: left;\">\n            Executives should prioritize identifying challenges in each region to drive future performance improvements.\n        <\/li>\n    <\/ul>\n<\/div>", "presentation_name": "P0 Fixes Verification", "company_logo": "✅"}, "background_color": null, "background_image": null}], "id": "8270434d-8cfc-4cda-8bae-e52a60fa7ff0", "created_at": "2025-11-29T15:53:37.607337"};

    // Renderer registry (6 layouts)
    const RENDERERS = {
      'L01': window.renderL01,
      'L02': window.renderL02,
      'L03': window.renderL03,
      'L25': window.renderL25,
      'L27': window.renderL27,
      'L29': window.renderL29
    };

    /**
     * Render presentation from data
     */
    function renderPresentation(data) {
      if (!data || !data.slides) {
        console.error('Invalid presentation data');
        return;
      }

      const slidesContainer = document.getElementById('slides-container');
      slidesContainer.innerHTML = '';

      // Update document title
      document.title = data.title || 'Presentation';

      // Render each slide
      data.slides.forEach((slide, index) => {
        const layout = slide.layout;
        const content = slide.content;

        // Get renderer
        const renderer = RENDERERS[layout];
        if (!renderer) {
          console.error(`No renderer found for layout: ${layout}`);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Error: Unknown Layout</h2>
                <p>Layout '${layout}' is not supported in v7.5-main</p>
                <p>Valid layouts: L01, L02, L03, L25, L27, L29</p>
              </div>
            </section>
          `;
          return;
        }

        // Render slide
        try {
          const slideHTML = renderer(content, slide, index);

          // Create temporary container to parse HTML
          const tempContainer = document.createElement('div');
          tempContainer.innerHTML = slideHTML;

          // Extract all script tags before inserting HTML
          const scripts = tempContainer.querySelectorAll('script');

          // Insert the HTML while preserving previous DOM elements
          // Using appendChild instead of innerHTML += to avoid destroying previous slides
          const sections = tempContainer.querySelectorAll('section');
          sections.forEach(section => {
            slidesContainer.appendChild(section);
          });

          // Manually execute each script by creating new script elements
          scripts.forEach(oldScript => {
            const newScript = document.createElement('script');

            // Copy all attributes (src, type, async, defer, etc.)
            Array.from(oldScript.attributes).forEach(attr => {
              newScript.setAttribute(attr.name, attr.value);
            });

            // Copy script content (for inline scripts)
            newScript.textContent = oldScript.textContent;

            // Append to document body - this triggers execution
            document.body.appendChild(newScript);
          });

        } catch (error) {
          console.error(`Error rendering slide ${index + 1}:`, error);
          slidesContainer.innerHTML += `
            <section class="error-slide">
              <div style="color: red; text-align: center; padding: 40px;">
                <h2>Rendering Error</h2>
                <p>Failed to render slide ${index + 1} (${layout})</p>
                <p>${error.message}</p>
              </div>
            </section>
          `;
        }
      });

      // Initialize Reveal.js AFTER scripts have time to execute
      setTimeout(() => {
        if (typeof initReveal === 'function') {
          initReveal();
        } else {
          // Fallback if reveal-config.js not loaded
          Reveal.initialize({
            width: 1920,
            height: 1080,
            margin: 0,
            minScale: 0.1,
            maxScale: 3.0,
            center: true,
            controls: true,
            progress: true,
            slideNumber: 'c/t',
            hash: true,
            history: true
          });
        }

        console.log(`✅ Presentation rendered: ${data.slides.length} slides`);
      }, 300);  // Give scripts 300ms to execute
    }

    /**
     * Show help text briefly
     */
    function showHelpText() {
      const helpText = document.getElementById('help-text');
      helpText.classList.add('show');
      setTimeout(() => {
        helpText.classList.remove('show');
      }, 3000);
    }

    // Add keyboard shortcuts (Note: 'B' and 'C' are handled by RevealJS config)
    document.addEventListener('keydown', (e) => {
      if (e.key === '?') {
        showHelpText();
      }
    });

    /**
     * postMessage Bridge for Cross-Origin Communication
     * Allows parent window from different origin to control the presentation
     *
     * Security: Validates message origin before executing commands
     */
    window.addEventListener('message', (event) => {
      // Security: Validate origin
      // Allow localhost (development), cloud platforms, and production frontend (deckster.xyz)
      const allowedOriginPattern = /^https?:\/\/(localhost:\d+|127\.0\.0\.1:\d+|.*\.up\.railway\.app|.*\.vercel\.app|.*\.netlify\.app|(www\.)?deckster\.xyz)$/;

      if (!allowedOriginPattern.test(event.origin)) {
        console.warn('⚠️ Rejected postMessage from unauthorized origin:', event.origin);
        return;
      }

      const { action, params } = event.data || {};

      if (!action) {
        console.warn('⚠️ postMessage received without action:', event.data);
        return;
      }

      console.log(`📨 postMessage received: ${action}`, params);

      let result = { success: false, action };

      try {
        switch (action) {
          // Navigation functions
          case 'nextSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.next();
              result.success = true;
            }
            break;

          case 'prevSlide':
            if (typeof Reveal !== 'undefined') {
              Reveal.prev();
              result.success = true;
            }
            break;

          case 'goToSlide':
            if (typeof goToSlide === 'function' && params?.index !== undefined) {
              goToSlide(params.index);  // Now expects 0-based index
              result.success = true;
              result.slideIndex = params.index;
            } else if (typeof Reveal !== 'undefined' && params?.index !== undefined) {
              Reveal.slide(params.index);  // Fallback: direct call with 0-based index
              result.success = true;
              result.slideIndex = params.index;
            }
            break;

          case 'getCurrentSlideInfo':
            if (typeof getCurrentSlideInfo === 'function') {
              result.success = true;
              result.data = getCurrentSlideInfo();
            }
            break;

          // Edit mode functions
          case 'toggleEditMode':
            if (typeof toggleEditMode === 'function') {
              toggleEditMode();
              result.success = true;
              result.isEditing = document.body.getAttribute('data-mode') === 'edit';
            }
            break;

          case 'saveAllChanges':
            if (typeof saveAllChanges === 'function') {
              saveAllChanges();
              result.success = true;
            }
            break;

          case 'cancelEdits':
            if (typeof cancelEdits === 'function') {
              cancelEdits();
              result.success = true;
            }
            break;

          case 'showVersionHistory':
            if (typeof showVersionHistory === 'function') {
              showVersionHistory();
              result.success = true;
            }
            break;

          // Overview mode functions
          case 'toggleOverview':
            if (typeof toggleOverview === 'function') {
              toggleOverview();
              result.success = true;
              result.isOverview = isOverviewActive();
            } else if (typeof Reveal !== 'undefined') {
              Reveal.toggleOverview();
              result.success = true;
            }
            break;

          case 'isOverviewActive':
            if (typeof isOverviewActive === 'function') {
              result.success = true;
              result.data = isOverviewActive();
            }
            break;

          // Debug functions
          case 'toggleGridOverlay':
            if (typeof toggleGridOverlay === 'function') {
              toggleGridOverlay();
              result.success = true;
            }
            break;

          case 'toggleBorderHighlight':
            if (typeof toggleBorderHighlight === 'function') {
              toggleBorderHighlight();
              result.success = true;
            }
            break;

          // Review mode functions
          case 'toggleReviewMode':
            if (typeof toggleReviewMode === 'function') {
              toggleReviewMode();
              result.success = true;
              result.isReviewing = document.body.getAttribute('data-mode') === 'review';
            }
            break;

          case 'enterReviewMode':
            if (typeof enterReviewMode === 'function') {
              enterReviewMode();
              result.success = true;
              result.isReviewing = true;
            }
            break;

          case 'exitReviewMode':
            if (typeof exitReviewMode === 'function') {
              exitReviewMode();
              result.success = true;
              result.isReviewing = false;
            }
            break;

          case 'getSelectedSections':
            if (typeof getSelectedSections === 'function') {
              result.success = true;
              result.data = getSelectedSections();
            }
            break;

          case 'clearSelection':
            if (typeof clearSelection === 'function') {
              clearSelection();
              result.success = true;
            }
            break;

          default:
            console.warn(`⚠️ Unknown action: ${action}`);
            result.error = `Unknown action: ${action}`;
        }
      } catch (error) {
        console.error(`❌ Error executing action ${action}:`, error);
        result.success = false;
        result.error = error.message;
      }

      // Send response back to parent
      event.source.postMessage(result, event.origin);
      console.log(`📤 postMessage response sent:`, result);
    });

    console.log('✅ postMessage bridge initialized - ready for cross-origin commands');

    // Render presentation on load
    window.addEventListener('DOMContentLoaded', () => {
      if (PRESENTATION_DATA) {
        renderPresentation(PRESENTATION_DATA);
      } else {
        document.getElementById('slides-container').innerHTML = `
          <section>
            <div style="text-align: center; padding: 60px; color: #6b7280;">
              <h1 style="font-size: 48px; color: #1f2937;">No Presentation Data</h1>
              <p style="font-size: 24px; margin-top: 24px;">No presentation data was provided</p>
              <p style="font-size: 18px; margin-top: 16px; color: #9ca3af;">Use the API to create a presentation</p>
            </div>
          </section>
        `;
        if (typeof initReveal === 'function') {
          initReveal();
        }
      }

      // Show help text on first load
      setTimeout(showHelpText, 1000);
    });
  </script>


<svg id="SvgjsSvg1001" width="2" height="0" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svgjs="http://svgjs.dev" style="overflow: hidden; top: -100%; left: -100%; position: absolute; opacity: 0;"><defs id="SvgjsDefs1002"></defs><polyline id="SvgjsPolyline1003" points="0,0"></polyline><path id="SvgjsPath1004" d="M0 0 "></path></svg><script>
    (function() {
      function initChart() {
        // v3.3.4: Destroy existing chart instance to force animation replay
        if (window.chartInstances && window.chartInstances['chart-slide_001']) {
          console.log('Chart chart-slide_001 exists, destroying to replay animation...');
          window.chartInstances['chart-slide_001'].destroy();
          delete window.chartInstances['chart-slide_001'];
        }

        const ctx = document.getElementById('chart-slide_001').getContext('2d');
        const chartConfig = {"type": "bar", "data": {"labels": ["Q1", "Q2", "Q3", "Q4"], "datasets": [{"label": "North America", "data": [124, 145, 165, 180], "backgroundColor": "#FF6B6B", "borderColor": "#FF6B6B", "borderWidth": 2, "borderRadius": 10}, {"label": "EMEA", "data": [98, 112, 128, 145], "backgroundColor": "#4ECDC4", "borderColor": "#4ECDC4", "borderWidth": 2, "borderRadius": 10}, {"label": "APAC", "data": [75, 88, 105, 125], "backgroundColor": "#FFE66D", "borderColor": "#FFE66D", "borderWidth": 2, "borderRadius": 10}]}, "options": {"responsive": true, "maintainAspectRatio": false, "animation": {"duration": 1500, "easing": "easeInOutQuart", "delay": 0, "loop": false, "animateRotate": true, "animateScale": true}, "plugins": {"legend": {"display": true, "position": "top", "labels": {"font": {"size": 14, "weight": "bold"}, "padding": 15, "usePointStyle": true}}, "datalabels": {"display": true, "color": "#fff", "font": {"size": 14, "weight": "bold"}, "formatter": "function(value) { return value.toLocaleString(); }", "anchor": "end", "align": "end", "offset": 0, "backgroundColor": "rgba(0, 0, 0, 0.7)", "borderRadius": 4, "padding": 6}, "tooltip": {"enabled": true, "mode": "nearest", "intersect": true}}, "scales": {"x": {"display": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "autoSkip": false, "maxRotation": 45, "minRotation": 0}, "title": {"display": true, "text": "", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}, "y": {"display": true, "beginAtZero": true, "grid": {"display": true, "color": "rgba(0, 0, 0, 0.08)", "lineWidth": 1}, "ticks": {"display": true, "font": {"size": 12, "weight": "500"}, "color": "#333", "padding": 8, "callback": "function(value) { return value.toLocaleString(); }"}, "title": {"display": true, "text": "Value", "font": {"size": 13, "weight": "bold"}, "color": "#333"}}}}};
        const chart = new Chart(ctx, chartConfig);

        // Store reference for editor access
        window.chartInstances = window.chartInstances || {};
        window.chartInstances['chart-slide_001'] = chart;

        console.log('✅ Chart chart-slide_001 initialized successfully');
      }

      // Reveal.js-aware initialization to ensure animations play
      if (typeof Reveal !== 'undefined') {
        // Wait for Reveal.js to be fully initialized before accessing methods
        Reveal.on('ready', function() {
          try {
            const currentSlide = Reveal.getCurrentSlide();
            if (currentSlide && currentSlide.querySelector('#chart-slide_001')) {
              setTimeout(initChart, 100);  // Small delay for slide transition
            }
          } catch (e) {
            console.warn('Chart init on ready failed:', e);
          }
        });

        // v3.3.4: Always reinitialize on slide change to replay animation
        Reveal.on('slidechanged', function(event) {
          try {
            if (event.currentSlide && event.currentSlide.querySelector('#chart-slide_001')) {
              initChart();  // This now destroys old chart and creates new one
            }
          } catch (e) {
            console.warn('Chart init on slide change failed:', e);
          }
        });
      } else {
        // No Reveal.js detected, init immediately (standalone mode)
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', initChart);
        } else {
          initChart();
        }
      }
    })();
  </script><script src="https://analytics-v30-production.up.railway.app/static/js/chart-spreadsheet-editor.js"></script><script>
  (function() {
      window.openChartEditor_chart_slide_001 = function() {
        console.log('=== Excel Editor: Opening for chart chart-slide_001 ===');

        // Get chart instance
        const chart = window.chartInstances?.['chart-slide_001'];
        if (!chart) {
            console.error('Chart not found in window.chartInstances');
            alert('Chart not ready. Please wait and try again.');
            return;
        }

        console.log('✅ Chart found. Chart type:', chart.config.type);
        console.log('Chart type parameter:', 'bar');

        // Extract current chart data
        const chartData = extractChartData_chart_slide_001(chart);

        // === DIAGNOSTIC LOGGING ===
        console.log('=== 📊 EXTRACTED CHART DATA FOR EDITOR ===');
        console.log('Data type:', typeof chartData);
        console.log('Is Array?:', Array.isArray(chartData));
        console.log('Full data:', JSON.stringify(chartData, null, 2));

        if (chartData && chartData.labels) {
            console.log('✅ Multi-series format detected');
            console.log('  Labels:', chartData.labels);
            console.log('  Datasets count:', chartData.datasets ? chartData.datasets.length : 0);
            if (chartData.datasets) {
                chartData.datasets.forEach((ds, i) => {
                    console.log(`  Dataset ${i}:`, ds.label, '- data points:', ds.data.length);
                });
            }
        } else if (Array.isArray(chartData)) {
            console.log('✅ Simple array format detected');
            console.log('  Rows:', chartData.length);
            if (chartData.length > 0) {
                console.log('  First row sample:', chartData[0]);
            }
        }
        console.log('Chart type parameter:', 'bar');
        console.log('=== END DIAGNOSTIC DATA ===');

        // Open Excel-like editor
        openChartEditor(
            'chart-slide_001',
            'bar',
            chartData,
            {
                apiEndpoint: 'https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data',
                onSave: async (newData, chartId) => {
                    console.log('Saving chart data:', newData);

                    // Update chart instance
                    updateChartData_chart_slide_001(chart, newData, 'bar');

                    // Save to API
                    try {
                        const response = await fetch('https://analytics-v30-production.up.railway.app/api/charts/api/charts/update-data', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                chart_id: chartId,
                                presentation_id: 'fix_verify_001',
                                data: newData,
                                timestamp: Date.now()
                            })
                        });

                        if (!response.ok) {
                            throw new Error('API request failed');
                        }

                        console.log('✅ Chart data saved successfully');
                    } catch (error) {
                        console.error('❌ Error saving chart data:', error);
                        throw error;
                    }
                }
            }
        );
    };

    // Extract data from chart instance based on chart type
    function extractChartData_chart_slide_001(chart) {
        const chartType = chart.config.type;

        if (chartType === 'scatter') {
            // Scatter: array of {x, y}
            return chart.data.datasets[0]?.data || [];
        } else if (chartType === 'bubble') {
            // Bubble: array of {label, x, y, r}
            return chart.data.datasets[0]?.data || [];
        } else if (['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea'].includes(chartType)) {
            // Check if multi-series
            if (chart.data.datasets.length > 1 || chart.data.datasets[0]?.label) {
                // Multi-series format
                return {
                    labels: chart.data.labels || [],
                    datasets: chart.data.datasets.map(ds => ({
                        label: ds.label,
                        data: ds.data
                    }))
                };
            } else {
                // Simple label-value format
                const labels = chart.data.labels || [];
                const values = chart.data.datasets[0]?.data || [];
                return labels.map((label, i) => ({ label, value: values[i] }));
            }
        } else {
            // Default: label-value format
            const labels = chart.data.labels || [];
            const values = chart.data.datasets[0]?.data || [];
            return labels.map((label, i) => ({ label, value: values[i] }));
        }
    }

    // Update chart instance with new data
    function updateChartData_chart_slide_001(chart, newData, chartType) {
        if (chartType === 'scatter' || chartType === 'bubble') {
            // Object-based data
            chart.data.datasets[0].data = newData;
        } else if (newData.labels && newData.datasets) {
            // Multi-series format
            chart.data.labels = newData.labels;
            chart.data.datasets = newData.datasets;
        } else if (Array.isArray(newData)) {
            // Simple label-value format
            chart.data.labels = newData.map(d => d.label);
            chart.data.datasets[0].data = newData.map(d => d.value);
        }

        chart.update();
    }
  })();
  </script></body></html>


Step 5: 
> document.querySelector('.chart-edit-btn').getAttribute('onclick')
< "openChartEditor_chart_slide_001()"



 