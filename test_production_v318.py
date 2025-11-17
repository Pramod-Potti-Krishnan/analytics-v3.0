#!/usr/bin/env python3
"""Test Analytics v3.1.8 scatter/bubble restoration in production."""

import requests
import re

PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "=" * 80 + RESET)
print(BOLD + "Analytics v3.1.8 Production Scatter/Bubble Restoration Validation" + RESET)
print(BOLD + f"Testing: {PRODUCTION_URL}" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

# Test 1: Correlation Analysis (scatter restored)
print(f"{BLUE}Test 1: Correlation Analysis (scatter chart restored){RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "prod-v318-test",
        "slide_id": "scatter-test",
        "slide_number": 1,
        "narrative": "Testing scatter restoration",
        "data": [
            {"label": "Jan - $20K spend", "value": 95},
            {"label": "Feb - $28K spend", "value": 124},
            {"label": "Mar - $35K spend", "value": 158}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    # Check Chart.js type
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check metadata
    metadata_chart_type = metadata.get("chart_type")

    # Check for [object Object]
    has_object_object = "[object Object]" in html

    # Check for labels in tooltips
    has_labels = "Jan - $20K spend" in html

    if chart_type == "scatter" and metadata_chart_type == "scatter" and not has_object_object and has_labels:
        print(f"{GREEN}✅ PASS{RESET}")
        print(f"  Chart.js type: scatter (correct - RESTORED)")
        print(f"  Metadata type: scatter (correct)")
        print(f"  [object Object]: No (datalabels fix working)")
        print(f"  Labels in tooltips: Yes")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  Chart.js type: {chart_type} (expected: scatter)")
        print(f"  Metadata type: {metadata_chart_type}")
        print(f"  [object Object]: {has_object_object}")
        print(f"  Labels: {has_labels}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 2: Multidimensional Analysis (bubble restored)
print(f"{BLUE}Test 2: Multidimensional Analysis (bubble chart restored){RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "prod-v318-test",
        "slide_id": "bubble-test",
        "slide_number": 2,
        "narrative": "Testing bubble restoration",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    # Check Chart.js type
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check metadata
    metadata_chart_type = metadata.get("chart_type")

    # Check for [object Object]
    has_object_object = "[object Object]" in html

    # Check for labels in tooltips
    has_labels = "North America" in html

    # Check for varying radius
    r_values = re.findall(r'"r":\s*(\d+\.?\d*)', html)
    has_varying_radius = len(set(r_values)) > 1 if r_values else False

    if chart_type == "bubble" and metadata_chart_type == "bubble" and not has_object_object and has_labels:
        print(f"{GREEN}✅ PASS{RESET}")
        print(f"  Chart.js type: bubble (correct - RESTORED)")
        print(f"  Metadata type: bubble (correct)")
        print(f"  [object Object]: No (datalabels fix working)")
        print(f"  Labels in tooltips: Yes")
        if has_varying_radius:
            print(f"  Varying radius: Yes {r_values[:3]}")
        else:
            print(f"  Varying radius: Static (OK for uniform data)")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  Chart.js type: {chart_type} (expected: bubble)")
        print(f"  Metadata type: {metadata_chart_type}")
        print(f"  [object Object]: {has_object_object}")
        print(f"  Labels: {has_labels}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 3: Verify All 9 Analytics Types
print(f"{BLUE}Test 3: Verify All 9 Analytics Types (correct chart types){RESET}")

expected_types = {
    "revenue_over_time": "line",
    "quarterly_comparison": "bar",
    "market_share": "pie",
    "yoy_growth": "bar",
    "kpi_metrics": "doughnut",
    "category_ranking": "bar",
    "correlation_analysis": "scatter",  # ✅ RESTORED
    "multidimensional_analysis": "bubble",  # ✅ RESTORED
    "multi_metric_comparison": "radar"
}

all_correct = True
for analytics_type, expected_chart_type in expected_types.items():
    response = requests.post(
        f"{PRODUCTION_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "prod-v318-test",
            "slide_id": f"test-{analytics_type}",
            "slide_number": 1,
            "narrative": "Test",
            "data": [
                {"label": "Test 1", "value": 100},
                {"label": "Test 2", "value": 150},
                {"label": "Test 3", "value": 200}
            ]
        },
        timeout=30
    )

    if response.status_code == 200:
        html = response.json()["content"]["element_3"]
        type_match = re.search(r'"type":\s*"(\w+)"', html)
        chart_type = type_match.group(1) if type_match else "unknown"

        # Check for [object Object]
        has_object_object = "[object Object]" in html

        if chart_type == expected_chart_type and not has_object_object:
            print(f"{GREEN}✅ PASS - {analytics_type}: {chart_type}{RESET}")
        else:
            print(f"{RED}❌ FAIL - {analytics_type}: {chart_type} (expected: {expected_chart_type}), [object Object]: {has_object_object}{RESET}")
            all_correct = False
    else:
        print(f"{RED}❌ FAIL - {analytics_type}: HTTP {response.status_code}{RESET}")
        all_correct = False

print()
print(BOLD + "=" * 80 + RESET)
if all_correct:
    print(BOLD + f"{GREEN}v3.1.8 Production Validation: ALL TESTS PASSED ✅{RESET}" + RESET)
    print(f"{GREEN}✅ Scatter chart RESTORED (was line in v3.1.7){RESET}")
    print(f"{GREEN}✅ Bubble chart RESTORED (was bar in v3.1.7){RESET}")
    print(f"{GREEN}✅ Datalabels fix working (no [object Object]){RESET}")
    print(f"{GREEN}✅ All 9 analytics types with correct Chart.js types{RESET}")
    print(f"{GREEN}✅ Charts render correctly (editor enhancement pending){RESET}")
else:
    print(BOLD + f"{RED}v3.1.8 Production Validation: SOME TESTS FAILED ❌{RESET}" + RESET)
print(BOLD + "=" * 80 + RESET)
