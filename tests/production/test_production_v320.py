#!/usr/bin/env python3
"""Test Analytics v3.2.0 comprehensive fixes in production."""

import requests
import re

PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "="*80 + RESET)
print(BOLD + "Analytics v3.2.0 Production Validation" + RESET)
print(BOLD + f"Testing: {PRODUCTION_URL}" + RESET)
print(BOLD + "="*80 + RESET + "\n")

# Test 1: Scatter Chart - Enforcement Bug Fix + X Marks
print(f"{BLUE}{BOLD}Test 1: Scatter Chart - Enforcement Bug Fix + X Marks{RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "prod-v320-test",
        "slide_id": "scatter-enforcement-fix",
        "slide_number": 1,
        "narrative": "Testing v3.2.0 enforcement bug fix and X marks in production",
        "data": [
            {"label": "Jan - $20K spend", "value": 95},
            {"label": "Feb - $28K spend", "value": 124},
            {"label": "Mar - $35K spend", "value": 158},
            {"label": "Apr - $42K spend", "value": 189}
        ]
    },
    timeout=30
)

scatter_passed = False
if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Check 1: No [object Object] (CRITICAL - this was the bug)
    has_object_object = "[object Object]" in html

    # Check 2: pointStyle is 'cross'
    point_style_match = re.search(r'"pointStyle":\s*"(\w+)"', html)
    point_style = point_style_match.group(1) if point_style_match else "none"

    # Check 3: Chart type is scatter
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    all_passed = (
        not has_object_object and
        point_style == "cross" and
        chart_type == "scatter"
    )

    if all_passed:
        print(f"{GREEN}✅ PASS - Enforcement bug FIXED, X marks working{RESET}")
        print(f"  [object Object]: {has_object_object} (✅ Bug fixed!)")
        print(f"  Point style: {point_style} (✅ X marks!)")
        print(f"  Chart type: {chart_type}")
        scatter_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Point style: {point_style} (should be 'cross')")
        print(f"  Chart type: {chart_type}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 2: Bubble Chart - Enforcement Bug Fix
print(f"{BLUE}{BOLD}Test 2: Bubble Chart - Enforcement Bug Fix{RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "prod-v320-test",
        "slide_id": "bubble-enforcement-fix",
        "slide_number": 2,
        "narrative": "Testing v3.2.0 enforcement bug fix for bubbles in production",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95},
            {"label": "LATAM", "value": 62}
        ]
    },
    timeout=30
)

bubble_passed = False
if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Check 1: No [object Object] (CRITICAL - this was the bug)
    has_object_object = "[object Object]" in html

    # Check 2: Chart type is bubble
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    all_passed = (
        not has_object_object and
        chart_type == "bubble"
    )

    if all_passed:
        print(f"{GREEN}✅ PASS - Enforcement bug FIXED{RESET}")
        print(f"  [object Object]: {has_object_object} (✅ Bug fixed!)")
        print(f"  Chart type: {chart_type}")
        bubble_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Chart type: {chart_type}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 3: All 9 Analytics Types
print(f"{BLUE}{BOLD}Test 3: All 9 Analytics Types{RESET}")

expected_types = {
    "revenue_over_time": "line",
    "quarterly_comparison": "bar",
    "market_share": "pie",
    "yoy_growth": "bar",
    "kpi_metrics": "doughnut",
    "category_ranking": "bar",
    "correlation_analysis": "scatter",
    "multidimensional_analysis": "bubble",
    "multi_metric_comparison": "radar"
}

all_types_passed = True
for analytics_type, expected_chart_type in expected_types.items():
    response = requests.post(
        f"{PRODUCTION_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "prod-v320-test",
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
            all_types_passed = False
    else:
        print(f"{RED}❌ FAIL - {analytics_type}: HTTP {response.status_code}{RESET}")
        all_types_passed = False

print()
print(BOLD + "="*80 + RESET)
if scatter_passed and bubble_passed and all_types_passed:
    print(BOLD + f"{GREEN}v3.2.0 Production Validation: ALL TESTS PASSED ✅{RESET}" + RESET)
    print(f"{GREEN}✅ Enforcement bug FIXED (no more [object Object]){RESET}")
    print(f"{GREEN}✅ Scatter: X (cross) marks visible{RESET}")
    print(f"{GREEN}✅ All 9 analytics types with correct Chart.js types{RESET}")
    print(f"\n{BOLD}{GREEN}🎉 v3.2.0 DEPLOYMENT SUCCESSFUL!{RESET}{RESET}")
else:
    print(BOLD + f"{RED}v3.2.0 Production Validation: SOME TESTS FAILED ❌{RESET}" + RESET)
    if not scatter_passed:
        print(f"{RED}❌ Scatter chart enforcement fix incomplete{RESET}")
    if not bubble_passed:
        print(f"{RED}❌ Bubble chart enforcement fix incomplete{RESET}")
    if not all_types_passed:
        print(f"{RED}❌ Some analytics types have issues{RESET}")
print(BOLD + "="*80 + RESET + "\n")
