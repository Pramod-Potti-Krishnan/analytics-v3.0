#!/usr/bin/env python3
"""Save each chart as individual standalone HTML file for debugging."""

import requests
import os

BASE_URL = "http://localhost:8080"

def save_standalone_chart(chart_type, data, title):
    """Save chart as standalone HTML file."""
    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "standalone",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Standalone {title}",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            chart_html = result.get("content", {}).get("element_3", "")

            # Wrap in complete HTML page
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body style="margin: 0; padding: 20px; background: #f5f5f5;">
    <h1 style="font-family: Arial; color: #333;">{title} ({chart_type})</h1>
    {chart_html}
</body>
</html>
"""

            # Save to file
            filename = f"standalone_{chart_type}.html"
            with open(filename, "w") as f:
                f.write(full_html)

            print(f"✅ {chart_type:15} → {filename} ({len(full_html):,} bytes)")
            return True
    except Exception as e:
        print(f"❌ {chart_type:15} → Error: {str(e)}")
        return False

    return False


print("=" * 70)
print("SAVING STANDALONE CHART HTML FILES")
print("=" * 70)

# Create output directory
os.makedirs("standalone_charts", exist_ok=True)
os.chdir("standalone_charts")

# Plugin charts (the ones that aren't showing)
plugin_charts = [
    ("treemap", [
        {"label": "Enterprise - North America", "value": 450},
        {"label": "Enterprise - Europe", "value": 350},
        {"label": "SMB - North America", "value": 200}
    ], "Treemap"),

    ("heatmap", [{
        "x_labels": ["Q1", "Q2", "Q3"],
        "y_labels": ["North", "South", "East"],
        "values": [[100, 150, 200], [120, 160, 210], [110, 155, 205]]
    }], "Heatmap"),

    ("matrix", [{
        "x_labels": ["Q1", "Q2"],
        "y_labels": ["North", "South"],
        "values": [[100, 150], [120, 160]]
    }], "Matrix Chart"),

    ("boxplot", [{
        "labels": ["Q1", "Q2"],
        "datasets": [{
            "label": "Sales",
            "data": [[100, 250, 350, 450, 600], [120, 270, 380, 480, 650]]
        }]
    }], "Boxplot"),

    ("candlestick", [{
        "labels": ["Day 1", "Day 2"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112}
            ]
        }]
    }], "Candlestick Chart"),

    ("financial", [{
        "labels": ["Day 1", "Day 2"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112}
            ]
        }]
    }], "Financial Chart"),

    ("sankey", [{
        "labels": ["Source A", "Source B", "Target X", "Target Y"],
        "data": [
            {"from": "Source A", "to": "Target X", "flow": 10},
            {"from": "Source B", "to": "Target Y", "flow": 8}
        ]
    }], "Sankey Diagram"),

    ("mixed", [{
        "labels": ["Q1", "Q2", "Q3"],
        "datasets": [
            {"type": "line", "label": "Revenue", "data": [100, 150, 200]},
            {"type": "bar", "label": "Costs", "data": [60, 80, 110]}
        ]
    }], "Mixed Chart"),
]

print("\nSaving plugin charts:")
for chart_type, data, title in plugin_charts:
    save_standalone_chart(chart_type, data, title)

print("\n" + "=" * 70)
print(f"Standalone charts saved to: standalone_charts/")
print("Open any of these files in browser to test individually")
print("=" * 70)
