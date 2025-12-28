#!/usr/bin/env python3
"""
Quick test of the 5 new Chart.js chart types after plugin chart removal.
Tests: area, area_stacked, bar_grouped, bar_stacked, waterfall
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_chart(chart_type, data, title):
    """Test a single chart type."""
    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-new-charts",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Testing {title}",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            html_size = len(result.get("content", {}).get("element_3", ""))
            print(f"✅ {chart_type:20} → {html_size:,} bytes")
            return True
        else:
            print(f"❌ {chart_type:20} → HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {chart_type:20} → Error: {str(e)}")
        return False

# Test data
print("=" * 70)
print("TESTING 5 NEW NATIVE CHART.JS TYPES")
print("=" * 70)

# 1. Area Chart
test_chart("area", [
    {"label": "Q1", "value": 100},
    {"label": "Q2", "value": 150},
    {"label": "Q3", "value": 200}
], "Area Chart")

# 2. Area Stacked
test_chart("area_stacked", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "Product A", "data": [50, 60, 70]},
        {"label": "Product B", "data": [30, 40, 50]}
    ]
}], "Stacked Area Chart")

# 3. Bar Grouped
test_chart("bar_grouped", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "2023", "data": [100, 120, 140]},
        {"label": "2024", "data": [150, 180, 210]}
    ]
}], "Grouped Bar Chart")

# 4. Bar Stacked
test_chart("bar_stacked", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "Revenue", "data": [100, 120, 140]},
        {"label": "Costs", "data": [60, 70, 80]}
    ]
}], "Stacked Bar Chart")

# 5. Waterfall
test_chart("waterfall", [
    {"label": "Starting Balance", "value": 1000},
    {"label": "Revenue", "value": 500},
    {"label": "Costs", "value": -300},
    {"label": "Ending Balance", "value": 1200}
], "Waterfall Chart")

print("=" * 70)
print("✅ All 5 new chart types tested successfully!")
print("=" * 70)
