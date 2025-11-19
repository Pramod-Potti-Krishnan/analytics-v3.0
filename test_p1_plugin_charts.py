#!/usr/bin/env python3
"""
Test P1 Plugin Chart Types with Correct Data Formats
Tests treemap, heatmap, matrix, boxplot, mixed with proper data structures
"""

import requests
import time

BASE_URL = "http://localhost:8080"

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

def test_chart_type(chart_type, description, data_payload):
    """Test a single chart type with custom data format."""
    print(f"\nTesting {chart_type}: {description}")
    print("-" * 70)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-p1",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} chart",
        "chart_type": chart_type,
        "data": data_payload,
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
            html_content = result.get("content", {}).get("element_3", "")
            html_size = len(html_content)

            # Check for CDN script tags
            has_treemap_cdn = "chartjs-chart-treemap" in html_content
            has_matrix_cdn = "chartjs-chart-matrix" in html_content
            has_boxplot_cdn = "chartjs-chart-boxplot" in html_content

            print(f"✅ SUCCESS")
            print(f"   Status: {response.status_code}")
            print(f"   Chart type returned: {chart_type_returned}")
            print(f"   Has content: {has_content}")
            print(f"   HTML size: {html_size:,} bytes")

            if chart_type == "treemap" and has_treemap_cdn:
                print(f"   ✅ Treemap CDN script tag present")
            elif chart_type in ["heatmap", "matrix"] and has_matrix_cdn:
                print(f"   ✅ Matrix CDN script tag present")
            elif chart_type == "boxplot" and has_boxplot_cdn:
                print(f"   ✅ Boxplot CDN script tag present")

            return True
        else:
            print(f"❌ FAILED")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


# Test all 5 P1 chart types with appropriate data formats
print("=" * 70)
print("P1 PLUGIN CHART TYPES VALIDATION TEST")
print("=" * 70)

results = {}

# Test 1: Treemap (hierarchical data)
# Note: Treemap needs flat data with values for sizing
treemap_data = [
    {"label": "Tech", "value": 450},
    {"label": "Finance", "value": 300},
    {"label": "Healthcare", "value": 200},
    {"label": "Energy", "value": 50}
]
results["treemap"] = test_chart_type("treemap", "Treemap chart (hierarchical)", treemap_data)

# Test 2: Heatmap (matrix data)
# Note: Heatmap needs x_labels, y_labels, and 2D values array
heatmap_data = {
    "x_labels": ["Q1", "Q2", "Q3", "Q4"],
    "y_labels": ["North", "South", "East", "West"],
    "values": [
        [100, 150, 200, 250],  # North
        [120, 160, 210, 260],  # South
        [110, 155, 205, 255],  # East
        [105, 145, 195, 245]   # West
    ]
}
results["heatmap"] = test_chart_type("heatmap", "Heatmap chart (correlation matrix)", [heatmap_data])

# Test 3: Matrix (alias for heatmap)
results["matrix"] = test_chart_type("matrix", "Matrix chart (alias for heatmap)", [heatmap_data])

# Test 4: Boxplot (statistical distribution)
# Note: Boxplot needs datasets with statistical data [min, q1, median, q3, max]
boxplot_data = {
    "labels": ["Q1", "Q2", "Q3", "Q4"],
    "datasets": [{
        "label": "Sales Distribution",
        "data": [
            [100, 250, 350, 450, 600],  # Q1: min, q1, median, q3, max
            [120, 270, 380, 480, 650],  # Q2
            [110, 260, 370, 470, 640],  # Q3
            [130, 280, 390, 490, 660]   # Q4
        ]
    }]
}
results["boxplot"] = test_chart_type("boxplot", "Boxplot chart (distribution)", [boxplot_data])

# Test 5: Mixed (combo chart)
# Note: Mixed chart needs datasets with type specified for each series
mixed_data = {
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
}
results["mixed"] = test_chart_type("mixed", "Mixed chart (line + bar)", [mixed_data])

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
    print("\n🎉 ALL P1 PLUGIN CHARTS WORKING! Ready to deploy.")
else:
    print(f"\n⚠️ {failed} chart types still have issues:")
    for chart_type, success in results.items():
        if not success:
            print(f"   - {chart_type}")
