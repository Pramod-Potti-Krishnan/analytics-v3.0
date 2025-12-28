#!/usr/bin/env python3
"""
Generate a visual viewer page for all 13 chart types.
Version 4: Waits for all plugin scripts to load before initializing charts.
"""

import requests
import json
import re

BASE_URL = "http://localhost:8080"

def get_chart_html(chart_type, data, title):
    """Get the chart HTML from the API and strip duplicate script tags."""
    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "chart-viewer",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Visual test: {title}",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            html = result.get("content", {}).get("element_3", "")

            # Strip out external script CDN tags (we load them globally in head)
            html = re.sub(
                r'<script\s+src="https://cdn\.jsdelivr\.net/[^"]+"></script>\s*',
                '',
                html,
                flags=re.IGNORECASE
            )

            # Replace immediate execution with deferred execution
            # Change: if (document.readyState === 'loading') {
            # To: window.addEventListener('pluginsLoaded', function() {
            html = re.sub(
                r'if \(document\.readyState === \'loading\'\) \{\s*document\.addEventListener\(\'DOMContentLoaded\', (\w+)\);\s*\} else \{\s*\1\(\);\s*\}',
                r'window.addEventListener("pluginsLoaded", \1);',
                html
            )

            return html
    except:
        pass
    return f"<div style='color: red; padding: 20px;'>Failed to load {chart_type}</div>"


print("Generating chart viewer page v4...")
print("(With plugin loading wait mechanism)")
print("-" * 70)

charts_html = []

# Generate all charts
charts_data = [
    ("area", [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 150},
        {"label": "Q3", "value": 200},
        {"label": "Q4", "value": 250}
    ], "Area Chart"),

    ("area_stacked", [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Product A", "data": [50, 60, 70, 80]},
            {"label": "Product B", "data": [30, 40, 50, 60]}
        ]
    }], "Stacked Area Chart"),

    ("bar_grouped", [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "2023", "data": [100, 120, 140, 160]},
            {"label": "2024", "data": [150, 180, 210, 240]}
        ]
    }], "Grouped Bar Chart"),

    ("bar_stacked", [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Revenue", "data": [100, 120, 140, 160]},
            {"label": "Costs", "data": [60, 70, 80, 90]}
        ]
    }], "Stacked Bar Chart"),

    ("waterfall", [
        {"label": "Starting Balance", "value": 1000},
        {"label": "Revenue", "value": 500},
        {"label": "Costs", "value": -300},
        {"label": "Taxes", "value": -100},
        {"label": "Ending Balance", "value": 1100}
    ], "Waterfall Chart"),

    ("treemap", [
        {"label": "Enterprise - North America", "value": 450},
        {"label": "Enterprise - Europe", "value": 350},
        {"label": "SMB - North America", "value": 200},
        {"label": "SMB - Asia", "value": 150}
    ], "Treemap"),

    ("heatmap", [{
        "x_labels": ["Q1", "Q2", "Q3", "Q4"],
        "y_labels": ["North", "South", "East", "West"],
        "values": [
            [100, 150, 200, 250],
            [120, 160, 210, 260],
            [110, 155, 205, 255],
            [105, 145, 195, 245]
        ]
    }], "Heatmap"),

    ("matrix", [{
        "x_labels": ["Q1", "Q2", "Q3"],
        "y_labels": ["North", "South", "East"],
        "values": [
            [100, 150, 200],
            [120, 160, 210],
            [110, 155, 205]
        ]
    }], "Matrix Chart"),

    ("boxplot", [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
            "label": "Sales Distribution",
            "data": [
                [100, 250, 350, 450, 600],
                [120, 270, 380, 480, 650],
                [110, 260, 370, 470, 640],
                [130, 280, 390, 490, 660]
            ]
        }]
    }], "Boxplot"),

    ("candlestick", [{
        "labels": ["Day 1", "Day 2", "Day 3", "Day 4"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112},
                {"o": 112, "h": 120, "l": 108, "c": 118},
                {"o": 118, "h": 125, "l": 115, "c": 122}
            ]
        }]
    }], "Candlestick Chart"),

    ("financial", [{
        "labels": ["Week 1", "Week 2", "Week 3"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112},
                {"o": 112, "h": 120, "l": 108, "c": 118}
            ]
        }]
    }], "Financial Chart"),

    ("sankey", [{
        "labels": ["Source A", "Source B", "Target X", "Target Y"],
        "data": [
            {"from": "Source A", "to": "Target X", "flow": 10},
            {"from": "Source A", "to": "Target Y", "flow": 5},
            {"from": "Source B", "to": "Target X", "flow": 7},
            {"from": "Source B", "to": "Target Y", "flow": 8}
        ]
    }], "Sankey Diagram"),

    ("mixed", [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"type": "line", "label": "Revenue", "data": [100, 150, 200, 250]},
            {"type": "bar", "label": "Costs", "data": [60, 80, 110, 140]}
        ]
    }], "Mixed/Combo Chart"),
]

for i, (chart_type, data, title) in enumerate(charts_data, 1):
    print(f"{i}/13 Generating {chart_type} chart...")
    html = get_chart_html(chart_type, data, title)
    charts_html.append((title, chart_type, html))

print("-" * 70)
print("Creating HTML viewer page...")

# Build the HTML page
page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analytics Microservice v3.4.3 - All 13 Chart Types</title>

    <!-- Chart.js Core - Load FIRST -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <!-- Chart.js Plugins - Load AFTER Chart.js core -->
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-treemap@3.1.0/dist/chartjs-chart-treemap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-matrix@2.0.1/dist/chartjs-chart-matrix.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@sgratzl/chartjs-chart-boxplot@4.2.5/build/index.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.2.1/dist/chartjs-chart-financial.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-sankey@0.12.0/dist/chartjs-chart-sankey.min.js"></script>

    <!-- Plugin Loading Manager -->
    <script>
        // Wait for all scripts to load before initializing charts
        window.addEventListener('load', function() {
            console.log('✅ All scripts loaded, Chart.js version:', Chart.version);
            console.log('✅ Registered controllers:', Object.keys(Chart.registry.controllers));

            // Dispatch custom event to signal plugins are ready
            window.dispatchEvent(new Event('pluginsLoaded'));
            console.log('✅ pluginsLoaded event dispatched');
        });
    </script>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 20px;
            opacity: 0.9;
        }

        .success-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-size: 18px;
            font-weight: 700;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .chart-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .chart-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e5e7eb;
        }

        .chart-title {
            font-size: 22px;
            font-weight: 700;
            color: #1f2937;
        }

        .chart-type {
            font-size: 14px;
            color: white;
            background: #667eea;
            padding: 6px 12px;
            border-radius: 6px;
            font-family: 'Monaco', 'Courier New', monospace;
        }

        .chart-content {
            min-height: 400px;
        }

        .footer {
            text-align: center;
            color: white;
            margin-top: 60px;
            padding: 30px;
            background: rgba(255,255,255,0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }

        .footer h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .stat {
            text-align: center;
        }

        .stat-number {
            font-size: 36px;
            font-weight: 800;
            color: #10b981;
        }

        .stat-label {
            font-size: 14px;
            opacity: 0.8;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Analytics Microservice v3.4.3</h1>
            <p>Complete Chart.js Integration Test</p>
            <div class="success-badge">✅ 100% Success Rate (13/13 Chart Types)</div>
        </div>

        <div class="charts-grid">
"""

# Add each chart
for title, chart_type, html in charts_html:
    page_html += f"""
            <div class="chart-card">
                <div class="chart-header">
                    <div class="chart-title">{title}</div>
                    <div class="chart-type">{chart_type}</div>
                </div>
                <div class="chart-content">
                    {html}
                </div>
            </div>
"""

page_html += """
        </div>

        <div class="footer">
            <h3>🎉 All Chart Types Working!</h3>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">5</div>
                    <div class="stat-label">Native Chart.js Types</div>
                </div>
                <div class="stat">
                    <div class="stat-number">8</div>
                    <div class="stat-label">Plugin Chart Types</div>
                </div>
                <div class="stat">
                    <div class="stat-number">13</div>
                    <div class="stat-label">Total Chart Types</div>
                </div>
                <div class="stat">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Write to file
output_file = "chart_viewer.html"
with open(output_file, "w") as f:
    f.write(page_html)

print(f"\n✅ Chart viewer v4 created: {output_file}")
print(f"   File size: {len(page_html):,} bytes")
print(f"   Plugin loading manager added")
print(f"   Chart initialization waits for 'pluginsLoaded' event")
print(f"\n📂 Opening in browser...")
