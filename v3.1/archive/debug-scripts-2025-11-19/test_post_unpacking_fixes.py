#!/usr/bin/env python3
"""
Test script to verify data unpacking fixes and treemap label formatter fix.

Tests:
1. bar_grouped - Should accept multi-series data without error
2. area_stacked - Should render chart with proper labels
3. bar_stacked - Should render chart with proper labels
4. treemap - Should display label text, not color codes
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_chart(chart_type, data, description):
    """Test a chart type with specific data."""
    print(f"\n{'=' * 70}")
    print(f"Testing {chart_type}: {description}")
    print('=' * 70)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-unpacking-fixes",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} after unpacking fixes",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            html = result.get("content", {}).get("element_3", "")
            html_size = len(html)

            # Check for success indicators
            has_canvas = "<canvas" in html
            has_chart_init = "new Chart" in html

            # Chart-specific validation
            if chart_type == "bar_grouped":
                # Should not have error about datasets
                has_error = "Grouped bar chart requires 'datasets'" in html
                status = "✅ SUCCESS" if not has_error and has_canvas else "❌ FAILED"
            elif chart_type in ["area_stacked", "bar_stacked"]:
                # Should not render "Item 0" (indicates missing labels)
                has_item_0 = "Item 0" in html
                status = "✅ SUCCESS" if not has_item_0 and has_canvas else "❌ FAILED"
            elif chart_type == "treemap":
                # Should have label formatter that returns ctx.raw.label
                has_label_formatter = "ctx.raw.label" in html
                # Should NOT have color formatter for labels
                has_color_in_formatter = '"placeholder_for_function"' in html
                status = "✅ SUCCESS" if has_label_formatter and not has_color_in_formatter else "❌ FAILED"
            else:
                status = "✅ SUCCESS" if has_canvas else "❌ FAILED"

            print(f"{status}")
            print(f"  Status Code: {response.status_code}")
            print(f"  HTML Size: {html_size:,} bytes")
            print(f"  Has Canvas: {has_canvas}")
            print(f"  Has Chart Init: {has_chart_init}")

            if chart_type == "treemap":
                print(f"  Has Label Formatter: {has_label_formatter}")
                print(f"  Has Color in Formatter: {has_color_in_formatter}")

            return status == "✅ SUCCESS"
        else:
            error = response.json() if response.headers.get("content-type") == "application/json" else response.text
            print(f"❌ FAILED")
            print(f"  Status Code: {response.status_code}")
            print(f"  Error: {error}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# Test data for each chart type
print("\n" + "=" * 70)
print("POST-UNPACKING FIXES VALIDATION TEST SUITE")
print("=" * 70)

results = {}

# Test 1: bar_grouped (P0 - data unpacking fix)
results["bar_grouped"] = test_chart(
    "bar_grouped",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "2023", "data": [100, 120, 140, 160]},
            {"label": "2024", "data": [150, 180, 210, 240]}
        ]
    }],
    "Multi-series data unpacking fix"
)

# Test 2: area_stacked (P0 - data unpacking fix)
results["area_stacked"] = test_chart(
    "area_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Product A", "data": [50, 60, 70, 80]},
            {"label": "Product B", "data": [30, 40, 50, 60]},
            {"label": "Product C", "data": [20, 30, 40, 50]}
        ]
    }],
    "Multi-series data unpacking fix"
)

# Test 3: bar_stacked (P0 - data unpacking fix)
results["bar_stacked"] = test_chart(
    "bar_stacked",
    [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Revenue", "data": [100, 120, 140, 160]},
            {"label": "Costs", "data": [60, 70, 80, 90]},
            {"label": "Profit", "data": [40, 50, 60, 70]}
        ]
    }],
    "Multi-series data unpacking fix"
)

# Test 4: treemap (P1 - label formatter fix)
results["treemap"] = test_chart(
    "treemap",
    [
        {"label": "Enterprise - North America", "value": 450},
        {"label": "Enterprise - Europe", "value": 350},
        {"label": "SMB - North America", "value": 200},
        {"label": "SMB - Asia", "value": 150},
        {"label": "Consumer - North America", "value": 100},
        {"label": "Consumer - Europe", "value": 75}
    ],
    "Label formatter fix (should show labels, not colors)"
)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

passed = sum(1 for v in results.values() if v)
failed = len(results) - passed

print(f"Total Tests: {len(results)}")
print(f"✅ Passed: {passed}/{len(results)} ({passed/len(results)*100:.0f}%)")
print(f"❌ Failed: {failed}/{len(results)}")

if failed == 0:
    print("\n🎉 ALL FIXES WORKING!")
    print("✅ bar_grouped: Data unpacking successful")
    print("✅ area_stacked: Data unpacking successful")
    print("✅ bar_stacked: Data unpacking successful")
    print("✅ treemap: Label formatter fixed")
    print("\nReady for production deployment!")
else:
    print(f"\n⚠️ {failed} test(s) failed:")
    for chart_type, success in results.items():
        if not success:
            print(f"   - {chart_type}")
