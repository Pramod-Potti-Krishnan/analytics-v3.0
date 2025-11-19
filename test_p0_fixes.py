#!/usr/bin/env python3
"""
Test P0 Fixes for 5 Chart Types
Tests bar_grouped, bar_stacked, candlestick, financial, sankey
"""

import requests
import time

BASE_URL = "http://localhost:8080"

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

def test_chart_type(chart_type, description):
    """Test a single chart type."""
    print(f"\nTesting {chart_type}: {description}")
    print("-" * 70)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-p0",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} chart",
        "chart_type": chart_type,
        "data": [
            {"label": "Q1", "value": 100},
            {"label": "Q2", "value": 150},
            {"label": "Q3", "value": 200},
            {"label": "Q4", "value": 250}
        ],
        "context": {
            "theme": "professional",
            "slide_title": f"{chart_type.upper()} Test"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            chart_type_returned = result.get("metadata", {}).get("chart_type", "unknown")
            has_content = "element_3" in result.get("content", {})
            html_size = len(result.get("content", {}).get("element_3", ""))

            print(f"✅ SUCCESS")
            print(f"   Status: {response.status_code}")
            print(f"   Chart type returned: {chart_type_returned}")
            print(f"   Has content: {has_content}")
            print(f"   HTML size: {html_size:,} bytes")

            return True
        else:
            print(f"❌ FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# Test all 5 P0 fixes
print("=" * 70)
print("P0 FIXES VALIDATION TEST")
print("=" * 70)

results = {}

# Test 1: bar_grouped (was broken - missing enable_editor)
results["bar_grouped"] = test_chart_type("bar_grouped", "Grouped bar chart (P0 fix: enable_editor)")

# Test 2: bar_stacked (was broken - missing enable_editor)
results["bar_stacked"] = test_chart_type("bar_stacked", "Stacked bar chart (P0 fix: enable_editor)")

# Test 3: candlestick (was broken - missing logger)
results["candlestick"] = test_chart_type("candlestick", "Candlestick chart (P0 fix: logger)")

# Test 4: financial (was broken - missing logger, alias for candlestick)
results["financial"] = test_chart_type("financial", "Financial chart (P0 fix: logger)")

# Test 5: sankey (was broken - missing logger)
results["sankey"] = test_chart_type("sankey", "Sankey diagram (P0 fix: logger)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
passed = sum(1 for v in results.values() if v)
failed = len(results) - passed

print(f"Total tests: {len(results)}")
print(f"✅ Passed: {passed}/{len(results)} ({passed/len(results)*100:.0f}%)")
print(f"❌ Failed: {failed}/{len(results)}")

if failed == 0:
    print("\n🎉 ALL P0 FIXES WORKING! Ready to deploy.")
else:
    print(f"\n⚠️ {failed} chart types still have issues:")
    for chart_type, success in results.items():
        if not success:
            print(f"   - {chart_type}")
