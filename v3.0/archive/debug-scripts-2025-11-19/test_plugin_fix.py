#!/usr/bin/env python3
"""
Test script to verify plugin chart fix.

Tests:
1. Multi-series charts still work (bar_grouped, area_stacked, bar_stacked)
2. Plugin charts are now fixed (heatmap, matrix, boxplot, candlestick, financial, sankey, mixed)
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_chart(chart_type, data, description, expected_min_size=1000):
    """Test a chart type with specific data."""
    print(f"\nTesting {chart_type}: {description}")
    print("-" * 70)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-plugin-fix",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} after plugin fix",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            html = result.get("content", {}).get("element_3", "")
            html_size = len(html)

            # Success indicators
            has_canvas = "<canvas" in html
            has_chart_init = "new Chart" in html or "Chart.register" in html
            has_error = "Error:" in html or "'list' object" in html
            size_ok = html_size >= expected_min_size

            success = has_canvas and not has_error and size_ok
            status = "✅ SUCCESS" if success else "❌ FAILED"

            print(f"{status}")
            print(f"  Status Code: {response.status_code}")
            print(f"  HTML Size: {html_size:,} bytes (min: {expected_min_size:,})")
            print(f"  Has Canvas: {has_canvas}")
            print(f"  Has Chart Init: {has_chart_init}")
            print(f"  Has Error: {has_error}")

            if has_error:
                # Extract error message
                error_start = html.find("Error:")
                if error_start != -1:
                    error_msg = html[error_start:error_start+100]
                    print(f"  Error Message: {error_msg}")

            return success
        else:
            error = response.json() if response.headers.get("content-type") == "application/json" else response.text
            print(f"❌ FAILED")
            print(f"  Status Code: {response.status_code}")
            print(f"  Error: {error}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


print("=" * 70)
print("PLUGIN CHART FIX VALIDATION TEST SUITE")
print("=" * 70)

results = {}

# PART 1: Verify multi-series charts still work
print("\n" + "=" * 70)
print("PART 1: MULTI-SERIES CHARTS (should still work)")
print("=" * 70)

# Test 1: bar_grouped
results["bar_grouped"] = test_chart(
    "bar_grouped",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "2023", "data": [100, 120, 140, 160]},
            {"label": "2024", "data": [150, 180, 210, 240]}
        ]
    }],
    "Multi-series grouped bars",
    expected_min_size=30000
)

# Test 2: area_stacked
results["area_stacked"] = test_chart(
    "area_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Product A", "data": [50, 60, 70, 80]},
            {"label": "Product B", "data": [30, 40, 50, 60]}
        ]
    }],
    "Multi-series stacked areas",
    expected_min_size=30000
)

# Test 3: bar_stacked
results["bar_stacked"] = test_chart(
    "bar_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Revenue", "data": [100, 120, 140, 160]},
            {"label": "Costs", "data": [60, 70, 80, 90]}
        ]
    }],
    "Multi-series stacked bars",
    expected_min_size=30000
)

# PART 2: Verify plugin charts are now fixed
print("\n" + "=" * 70)
print("PART 2: PLUGIN CHARTS (should now be fixed)")
print("=" * 70)

# Test 4: heatmap
results["heatmap"] = test_chart(
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
    "Heatmap with matrix data",
    expected_min_size=1800
)

# Test 5: matrix (alias for heatmap)
results["matrix"] = test_chart(
    "matrix",
    [{
        "x_labels": ["Q1", "Q2", "Q3"],
        "y_labels": ["North", "South"],
        "values": [
            [100, 150, 200],
            [120, 160, 210]
        ]
    }],
    "Matrix chart (heatmap alias)",
    expected_min_size=1800
)

# Test 6: boxplot
results["boxplot"] = test_chart(
    "boxplot",
    [{
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
    }],
    "Boxplot with statistical data",
    expected_min_size=1800
)

# Test 7: candlestick
results["candlestick"] = test_chart(
    "candlestick",
    [{
        "labels": ["Day 1", "Day 2", "Day 3"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112},
                {"o": 112, "h": 120, "l": 108, "c": 118}
            ]
        }]
    }],
    "Candlestick with OHLC data",
    expected_min_size=1800
)

# Test 8: financial (alias for candlestick)
results["financial"] = test_chart(
    "financial",
    [{
        "labels": ["Day 1", "Day 2"],
        "datasets": [{
            "label": "Stock Price",
            "data": [
                {"o": 100, "h": 110, "l": 95, "c": 105},
                {"o": 105, "h": 115, "l": 100, "c": 112}
            ]
        }]
    }],
    "Financial chart (candlestick alias)",
    expected_min_size=1800
)

# Test 9: sankey
results["sankey"] = test_chart(
    "sankey",
    [{
        "labels": ["Source A", "Source B", "Target X", "Target Y"],
        "data": [
            {"from": "Source A", "to": "Target X", "flow": 10},
            {"from": "Source A", "to": "Target Y", "flow": 5},
            {"from": "Source B", "to": "Target X", "flow": 7},
            {"from": "Source B", "to": "Target Y", "flow": 8}
        ]
    }],
    "Sankey with flow data",
    expected_min_size=1800
)

# Test 10: mixed
results["mixed"] = test_chart(
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
            }
        ]
    }],
    "Mixed chart (line + bar)",
    expected_min_size=28000
)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

multi_series_charts = ["bar_grouped", "area_stacked", "bar_stacked"]
plugin_charts = ["heatmap", "matrix", "boxplot", "candlestick", "financial", "sankey", "mixed"]

multi_series_passed = sum(1 for ct in multi_series_charts if results.get(ct, False))
plugin_charts_passed = sum(1 for ct in plugin_charts if results.get(ct, False))

total_passed = sum(1 for v in results.values() if v)
total_failed = len(results) - total_passed

print(f"\nMulti-Series Charts (3 total):")
print(f"  ✅ Passed: {multi_series_passed}/3 ({multi_series_passed/3*100:.0f}%)")
if multi_series_passed < 3:
    print(f"  ❌ Failed: {', '.join([ct for ct in multi_series_charts if not results.get(ct, False)])}")

print(f"\nPlugin Charts (7 total):")
print(f"  ✅ Passed: {plugin_charts_passed}/7 ({plugin_charts_passed/7*100:.0f}%)")
if plugin_charts_passed < 7:
    print(f"  ❌ Failed: {', '.join([ct for ct in plugin_charts if not results.get(ct, False)])}")

print(f"\nOverall:")
print(f"  Total Tests: {len(results)}")
print(f"  ✅ Passed: {total_passed}/{len(results)} ({total_passed/len(results)*100:.0f}%)")
print(f"  ❌ Failed: {total_failed}/{len(results)}")

if total_failed == 0:
    print("\n🎉 ALL CHARTS WORKING!")
    print("✅ Multi-series charts: Still working correctly")
    print("✅ Plugin charts: Fixed by removing from multi_series_chart_types list")
    print("\nReady for production deployment!")
else:
    print(f"\n⚠️ {total_failed} test(s) failed:")
    for chart_type, success in results.items():
        if not success:
            print(f"   - {chart_type}")
