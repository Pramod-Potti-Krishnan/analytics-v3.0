#!/usr/bin/env python3
"""
Test data formats for different chart types to verify DATA_FORMATS_REFERENCE.md accuracy
"""

import requests

BASE_URL = "http://localhost:8080"

def test_format(chart_type, data, description):
    """Test a data format for a specific chart type."""
    print(f"\nTesting {chart_type}: {description}")
    print("-" * 70)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-formats",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} data format",
        "chart_type": chart_type,
        "data": data
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            html_size = len(result.get("content", {}).get("element_3", ""))
            print(f"✅ SUCCESS - Data format valid")
            print(f"   HTML size: {html_size:,} bytes")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


print("=" * 70)
print("DATA FORMAT VALIDATION TESTS")
print("=" * 70)

results = {}

# Test 1: Simple format (line chart)
results["line"] = test_format("line",
    [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 150},
        {"label": "Q3", "value": 200}
    ],
    "Simple format - {label, value}"
)

# Test 2: Multi-series format (bar_grouped)
results["bar_grouped"] = test_format("bar_grouped",
    [{
        "labels": ["Q1", "Q2", "Q3"],
        "datasets": [
            {"label": "2023", "data": [100, 120, 140]},
            {"label": "2024", "data": [150, 180, 210]}
        ]
    }],
    "Multi-series - {labels, datasets}"
)

# Test 3: Heatmap format
results["heatmap"] = test_format("heatmap",
    [{
        "x_labels": ["Q1", "Q2"],
        "y_labels": ["North", "South"],
        "values": [[100, 150], [120, 160]]
    }],
    "Matrix format - {x_labels, y_labels, values}"
)

# Test 4: Boxplot format
results["boxplot"] = test_format("boxplot",
    [{
        "labels": ["Q1", "Q2"],
        "datasets": [{
            "label": "Sales",
            "data": [[100, 250, 350, 450, 600], [120, 270, 380, 480, 650]]
        }]
    }],
    "Statistical - [min, q1, median, q3, max]"
)

# Test 5: Candlestick format
results["candlestick"] = test_format("candlestick",
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
    "OHLC format - {o, h, l, c}"
)

# Test 6: Mixed chart format
results["mixed"] = test_format("mixed",
    [{
        "labels": ["Q1", "Q2"],
        "datasets": [
            {"type": "line", "label": "Revenue", "data": [125, 145]},
            {"type": "bar", "label": "Costs", "data": [80, 90]}
        ]
    }],
    "Combo format - datasets with type"
)

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
    print("\n🎉 ALL DATA FORMATS VALID!")
    print("DATA_FORMATS_REFERENCE.md is accurate and ready for use.")
else:
    print(f"\n⚠️ {failed} format(s) need correction:")
    for chart_type, success in results.items():
        if not success:
            print(f"   - {chart_type}")
