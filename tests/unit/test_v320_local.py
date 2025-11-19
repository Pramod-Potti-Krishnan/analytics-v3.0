#!/usr/bin/env python3
"""Test Analytics v3.2.0 comprehensive fixes locally."""

import requests
import re

LOCAL_URL = "http://localhost:8080"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "="*80 + RESET)
print(BOLD + "Analytics v3.2.0 Local Comprehensive Fix Validation" + RESET)
print(BOLD + f"Testing: {LOCAL_URL}" + RESET)
print(BOLD + "="*80 + RESET + "\n")

# Test 1: Scatter Chart - No [object Object] + X marks
print(f"{BLUE}{BOLD}Test 1: Scatter Chart - Enforcement Bug Fix + X Marks{RESET}")
response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "test-v320",
        "slide_id": "scatter-v320",
        "slide_number": 1,
        "narrative": "Testing v3.2.0 enforcement fix and X marks",
        "data": [
            {"label": "Jan - $20K", "value": 95},
            {"label": "Feb - $28K", "value": 124},
            {"label": "Mar - $35K", "value": 158}
        ]
    },
    timeout=30
)

scatter_passed = False
if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Check 1: No [object Object]
    has_object_object = "[object Object]" in html

    # Check 2: pointStyle is 'cross'
    point_style_match = re.search(r'"pointStyle":\s*"(\w+)"', html)
    point_style = point_style_match.group(1) if point_style_match else "none"

    # Check 3: Chart type is scatter
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check 4: pointRadius is 10
    radius_match = re.search(r'"pointRadius":\s*(\d+)', html)
    point_radius = int(radius_match.group(1)) if radius_match else 0

    # Check 5: Background is opaque
    bg_color_match = re.search(r'"backgroundColor":\s*"([^"]+)"', html)
    bg_color = bg_color_match.group(1) if bg_color_match else ""
    is_opaque = "rgba" not in bg_color or ",1)" in bg_color

    all_passed = (
        not has_object_object and
        point_style == "cross" and
        chart_type == "scatter" and
        point_radius >= 10 and
        is_opaque
    )

    if all_passed:
        print(f"{GREEN}✅ PASS - Scatter chart v3.2.0 fixes working{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Point style: {point_style} (should be 'cross')")
        print(f"  Chart type: {chart_type}")
        print(f"  Point radius: {point_radius}px")
        print(f"  Background: {bg_color[:30]}...")
        scatter_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Point style: {point_style} (should be 'cross')")
        print(f"  Chart type: {chart_type}")
        print(f"  Point radius: {point_radius}px")
        print(f"  Background: {bg_color[:30]}...")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 2: Bubble Chart - No [object Object]
print(f"{BLUE}{BOLD}Test 2: Bubble Chart - Enforcement Bug Fix{RESET}")
response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "test-v320",
        "slide_id": "bubble-v320",
        "slide_number": 2,
        "narrative": "Testing v3.2.0 enforcement fix for bubbles",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    },
    timeout=30
)

bubble_passed = False
if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Check 1: No [object Object]
    has_object_object = "[object Object]" in html

    # Check 2: Chart type is bubble
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check 3: Varying radius
    r_values = [float(v) for v in re.findall(r'"r":\s*(\d+\.?\d*)', html)]
    has_varying_radius = len(set([round(r) for r in r_values])) > 1 if r_values else False

    # Check 4: Background opacity
    bg_color_match = re.search(r'"backgroundColor":\s*"rgba\([^,]+,[^,]+,[^,]+,([^)]+)\)"', html)
    alpha = float(bg_color_match.group(1)) if bg_color_match else 0

    all_passed = (
        not has_object_object and
        chart_type == "bubble" and
        has_varying_radius and
        0.6 <= alpha <= 0.8
    )

    if all_passed:
        print(f"{GREEN}✅ PASS - Bubble chart v3.2.0 fixes working{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Chart type: {chart_type}")
        print(f"  Varying radius: {has_varying_radius}")
        print(f"  Opacity: {alpha}")
        bubble_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  [object Object]: {has_object_object} (should be False)")
        print(f"  Chart type: {chart_type}")
        print(f"  Varying radius: {has_varying_radius}")
        print(f"  Opacity: {alpha}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 3: All 9 Analytics Types
print(f"{BLUE}{BOLD}Test 3: All 9 Analytics Types (Quick Check){RESET}")

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
        f"{LOCAL_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "test-v320",
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
    print(BOLD + f"{GREEN}v3.2.0 Local Validation: ALL TESTS PASSED ✅{RESET}" + RESET)
    print(f"{GREEN}✅ Scatter: No [object Object], X (cross) marks, 10px, opaque{RESET}")
    print(f"{GREEN}✅ Bubble: No [object Object], varying radius, 70% opacity{RESET}")
    print(f"{GREEN}✅ All 9 analytics types with correct Chart.js types{RESET}")
    print(f"\n{YELLOW}Ready to deploy v3.2.0 to Railway!{RESET}")
else:
    print(BOLD + f"{RED}v3.2.0 Local Validation: SOME TESTS FAILED ❌{RESET}" + RESET)
    if not scatter_passed:
        print(f"{RED}❌ Scatter chart fixes incomplete{RESET}")
    if not bubble_passed:
        print(f"{RED}❌ Bubble chart fixes incomplete{RESET}")
    if not all_types_passed:
        print(f"{RED}❌ Some analytics types have issues{RESET}")
print(BOLD + "="*80 + RESET + "\n")
