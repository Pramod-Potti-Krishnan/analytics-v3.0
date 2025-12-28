#!/usr/bin/env python3
"""
Comprehensive test of all 13 new Chart.js chart types.

Tests all chart types added in v3.4.3 to verify 100% success rate.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

def test_chart(chart_type, data, description, expected_min_size=1000):
    """Test a chart type with specific data."""
    print(f"\n{chart_type:15} | {description:50}", end=" | ")

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-all-13",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type}",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            html = result.get("content", {}).get("element_3", "")
            html_size = len(html)

            has_canvas = "<canvas" in html
            has_error = "Error:" in html or "'list' object" in html
            size_ok = html_size >= expected_min_size

            success = has_canvas and not has_error and size_ok

            if success:
                print(f"✅ {html_size:6,} bytes")
                return True, html_size
            else:
                error_msg = ""
                if not has_canvas:
                    error_msg = "No canvas"
                elif has_error:
                    error_start = html.find("Error:")
                    error_msg = html[error_start:error_start+50] if error_start != -1 else "Unknown error"
                elif not size_ok:
                    error_msg = f"Too small ({html_size} < {expected_min_size})"

                print(f"❌ {html_size:6,} bytes - {error_msg}")
                return False, html_size
        else:
            print(f"❌ HTTP {response.status_code}")
            return False, 0

    except Exception as e:
        print(f"❌ Exception: {str(e)[:30]}")
        return False, 0


print("=" * 100)
print("COMPREHENSIVE 13-CHART VALIDATION TEST")
print("=" * 100)
print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 100)

results = {}
sizes = {}

# ========================================
# NATIVE CHART.JS TYPES (5)
# ========================================
print("\n" + "=" * 100)
print("NATIVE CHART.JS TYPES (5)")
print("=" * 100)

# 1. Area Chart
success, size = test_chart(
    "area",
    [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 150},
        {"label": "Q3", "value": 200},
        {"label": "Q4", "value": 250}
    ],
    "Area chart (filled line)",
    expected_min_size=30000
)
results["area"] = success
sizes["area"] = size

# 2. Area Stacked
success, size = test_chart(
    "area_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Product A", "data": [50, 60, 70, 80]},
            {"label": "Product B", "data": [30, 40, 50, 60]},
            {"label": "Product C", "data": [20, 30, 40, 50]}
        ]
    }],
    "Stacked area chart (multi-series)",
    expected_min_size=30000
)
results["area_stacked"] = success
sizes["area_stacked"] = size

# 3. Bar Grouped
success, size = test_chart(
    "bar_grouped",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "2023", "data": [100, 120, 140, 160]},
            {"label": "2024", "data": [150, 180, 210, 240]}
        ]
    }],
    "Grouped bar chart (multi-series side-by-side)",
    expected_min_size=30000
)
results["bar_grouped"] = success
sizes["bar_grouped"] = size

# 4. Bar Stacked
success, size = test_chart(
    "bar_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Revenue", "data": [100, 120, 140, 160]},
            {"label": "Costs", "data": [60, 70, 80, 90]},
            {"label": "Profit", "data": [40, 50, 60, 70]}
        ]
    }],
    "Stacked bar chart (multi-series stacked)",
    expected_min_size=30000
)
results["bar_stacked"] = success
sizes["bar_stacked"] = size

# 5. Waterfall
success, size = test_chart(
    "waterfall",
    [
        {"label": "Starting Balance", "value": 1000},
        {"label": "Revenue", "value": 500},
        {"label": "Costs", "value": -300},
        {"label": "Taxes", "value": -100},
        {"label": "Ending Balance", "value": 1100}
    ],
    "Waterfall chart (cumulative changes)",
    expected_min_size=30000
)
results["waterfall"] = success
sizes["waterfall"] = size

# ========================================
# CHART.JS PLUGIN TYPES (8)
# ========================================
print("\n" + "=" * 100)
print("CHART.JS PLUGIN TYPES (8)")
print("=" * 100)

# 6. Treemap
success, size = test_chart(
    "treemap",
    [
        {"label": "Enterprise - North America", "value": 450},
        {"label": "Enterprise - Europe", "value": 350},
        {"label": "SMB - North America", "value": 200},
        {"label": "SMB - Asia", "value": 150},
        {"label": "Consumer - North America", "value": 100},
        {"label": "Consumer - Europe", "value": 75}
    ],
    "Treemap (hierarchical data)",
    expected_min_size=1800
)
results["treemap"] = success
sizes["treemap"] = size

# 7. Heatmap
success, size = test_chart(
    "heatmap",
    [{
        "x_labels": ["Q1", "Q2", "Q3", "Q4"],
        "y_labels": ["North", "South", "East", "West"],
        "values": [
            [100, 150, 200, 250],
            [120, 160, 210, 260],
            [110, 155, 205, 255],
            [105, 145, 195, 245]
        ]
    }],
    "Heatmap (2D correlation matrix)",
    expected_min_size=1800
)
results["heatmap"] = success
sizes["heatmap"] = size

# 8. Matrix
success, size = test_chart(
    "matrix",
    [{
        "x_labels": ["Q1", "Q2", "Q3"],
        "y_labels": ["Product A", "Product B", "Product C"],
        "values": [
            [100, 150, 200],
            [120, 160, 210],
            [110, 155, 205]
        ]
    }],
    "Matrix chart (alias for heatmap)",
    expected_min_size=1800
)
results["matrix"] = success
sizes["matrix"] = size

# 9. Boxplot
success, size = test_chart(
    "boxplot",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
            "label": "Sales Distribution",
            "data": [
                [100, 250, 350, 450, 600],  # min, q1, median, q3, max
                [120, 270, 380, 480, 650],
                [110, 260, 370, 470, 640],
                [130, 280, 390, 490, 660]
            ]
        }]
    }],
    "Boxplot (statistical distribution)",
    expected_min_size=1800
)
results["boxplot"] = success
sizes["boxplot"] = size

# 10. Candlestick
success, size = test_chart(
    "candlestick",
    [{
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
    }],
    "Candlestick (OHLC financial data)",
    expected_min_size=1800
)
results["candlestick"] = success
sizes["candlestick"] = size

# 11. Financial
success, size = test_chart(
    "financial",
    [{
        "labels": ["Week 1", "Week 2", "Week 3"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112},
                {"o": 112, "h": 120, "l": 108, "c": 118}
            ]
        }]
    }],
    "Financial chart (alias for candlestick)",
    expected_min_size=1800
)
results["financial"] = success
sizes["financial"] = size

# 12. Sankey
success, size = test_chart(
    "sankey",
    [{
        "labels": ["Source A", "Source B", "Target X", "Target Y", "Target Z"],
        "data": [
            {"from": "Source A", "to": "Target X", "flow": 10},
            {"from": "Source A", "to": "Target Y", "flow": 5},
            {"from": "Source B", "to": "Target X", "flow": 7},
            {"from": "Source B", "to": "Target Y", "flow": 8},
            {"from": "Source B", "to": "Target Z", "flow": 3}
        ]
    }],
    "Sankey diagram (flow visualization)",
    expected_min_size=1800
)
results["sankey"] = success
sizes["sankey"] = size

# 13. Mixed
success, size = test_chart(
    "mixed",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {
                "type": "line",
                "label": "Revenue",
                "data": [100, 150, 200, 250]
            },
            {
                "type": "bar",
                "label": "Costs",
                "data": [60, 80, 110, 140]
            },
            {
                "type": "bar",
                "label": "Profit",
                "data": [40, 70, 90, 110]
            }
        ]
    }],
    "Mixed/combo chart (line + bar)",
    expected_min_size=28000
)
results["mixed"] = success
sizes["mixed"] = size

# ========================================
# SUMMARY
# ========================================
print("\n" + "=" * 100)
print("TEST SUMMARY")
print("=" * 100)

native_charts = ["area", "area_stacked", "bar_grouped", "bar_stacked", "waterfall"]
plugin_charts = ["treemap", "heatmap", "matrix", "boxplot", "candlestick", "financial", "sankey", "mixed"]

native_passed = sum(1 for ct in native_charts if results.get(ct, False))
plugin_passed = sum(1 for ct in plugin_charts if results.get(ct, False))
total_passed = sum(1 for v in results.values() if v)
total_failed = len(results) - total_passed

print(f"\nNative Chart.js Types (5 total):")
print(f"  ✅ Passed: {native_passed}/5 ({native_passed/5*100:.0f}%)")
if native_passed < 5:
    failed = [ct for ct in native_charts if not results.get(ct, False)]
    print(f"  ❌ Failed: {', '.join(failed)}")

print(f"\nChart.js Plugin Types (8 total):")
print(f"  ✅ Passed: {plugin_passed}/8 ({plugin_passed/8*100:.0f}%)")
if plugin_passed < 8:
    failed = [ct for ct in plugin_charts if not results.get(ct, False)]
    print(f"  ❌ Failed: {', '.join(failed)}")

print(f"\nOVERALL RESULTS:")
print(f"  Total Chart Types: 13")
print(f"  ✅ Passed: {total_passed}/13 ({total_passed/13*100:.0f}%)")
print(f"  ❌ Failed: {total_failed}/13")

if total_failed == 0:
    print("\n" + "=" * 100)
    print("🎉 ALL 13 CHART TYPES WORKING!")
    print("=" * 100)
    print("\n✅ SUCCESS RATE: 100% (13/13)")
    print("✅ Native Chart.js: 5/5 working")
    print("✅ Plugin Charts: 8/8 working")
    print("\nAnalytics Microservice v3.4.3 is fully operational!")
else:
    print("\n" + "=" * 100)
    print(f"⚠️ {total_failed} CHART TYPE(S) FAILED")
    print("=" * 100)
    for chart_type, success in results.items():
        if not success:
            print(f"  ❌ {chart_type}: {sizes.get(chart_type, 0)} bytes")

# Size breakdown
print("\n" + "=" * 100)
print("SIZE BREAKDOWN")
print("=" * 100)
print("\nNative Charts (inline scripts - larger):")
for ct in native_charts:
    if ct in sizes:
        print(f"  {ct:15} {sizes[ct]:6,} bytes")

print("\nPlugin Charts (CDN-based - smaller):")
for ct in plugin_charts:
    if ct in sizes:
        print(f"  {ct:15} {sizes[ct]:6,} bytes")

print("\n" + "=" * 100)
