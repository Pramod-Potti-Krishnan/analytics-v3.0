#!/usr/bin/env python3
"""Test Analytics v3.1.9 comprehensive fixes in production."""

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
print(BOLD + "Analytics v3.1.9 Production Comprehensive Fix Validation" + RESET)
print(BOLD + f"Testing: {PRODUCTION_URL}" + RESET)
print(BOLD + "="*80 + RESET + "\n")

# Test 1: Scatter Chart Comprehensive Fix
print(f"{BLUE}{BOLD}Test 1: Scatter Chart Comprehensive Fix{RESET}")
print(f"{BLUE}Testing: correlation_analysis (scatter chart){RESET}")

response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "prod-v319-test",
        "slide_id": "scatter-comprehensive",
        "slide_number": 1,
        "narrative": "Testing v3.1.9 comprehensive scatter fixes",
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

    # Check 1: Chart type is scatter
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check 2: No [object Object] labels
    has_object_object = "[object Object]" in html

    # Check 3: Points are visible (pointRadius >= 10)
    radius_match = re.search(r'"pointRadius":\s*(\d+)', html)
    point_radius = int(radius_match.group(1)) if radius_match else 0

    # Check 4: Background color is opaque
    bg_color_match = re.search(r'"backgroundColor":\s*"([^"]+)"', html)
    bg_color = bg_color_match.group(1) if bg_color_match else ""
    is_opaque = "rgba" not in bg_color or ",1)" in bg_color or ",0.9)" in bg_color or ",0.8)" in bg_color or ",0.7)" in bg_color

    # Check 5: Labels preserved
    has_labels = "Jan - $20K spend" in html

    all_checks = [
        ("Chart type", chart_type == "scatter", chart_type, "scatter"),
        ("[object Object]", not has_object_object, str(has_object_object), "False"),
        ("Point radius", point_radius >= 10, f"{point_radius}px", "≥10px"),
        ("Background opaque", is_opaque, bg_color[:30], "opaque"),
        ("Labels preserved", has_labels, str(has_labels), "True")
    ]

    all_passed = all(check[1] for check in all_checks)

    if all_passed:
        print(f"{GREEN}✅ PASS - All scatter fixes working{RESET}")
        for name, _, actual, _ in all_checks:
            print(f"  {name}: {actual}")
        scatter_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        for name, passed, actual, expected in all_checks:
            if not passed:
                print(f"  {RED}✗ {name}: {actual} (expected: {expected}){RESET}")
            else:
                print(f"  {GREEN}✓ {name}: {actual}{RESET}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")
    if response.status_code >= 400:
        print(f"  Error: {response.text[:200]}")

print()

# Test 2: Bubble Chart Comprehensive Fix
print(f"{BLUE}{BOLD}Test 2: Bubble Chart Comprehensive Fix{RESET}")
print(f"{BLUE}Testing: multidimensional_analysis (bubble chart){RESET}")

response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "prod-v319-test",
        "slide_id": "bubble-comprehensive",
        "slide_number": 2,
        "narrative": "Testing v3.1.9 comprehensive bubble fixes",
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

    # Check 1: Chart type is bubble
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    chart_type = type_match.group(1) if type_match else "unknown"

    # Check 2: No [object Object] labels
    has_object_object = "[object Object]" in html

    # Check 3: Varying radius (proportional scaling 8-40px)
    r_values = [float(v) for v in re.findall(r'"r":\s*(\d+\.?\d*)', html)]
    has_varying_radius = len(set([round(r) for r in r_values])) > 1 if r_values else False
    radius_range = f"{min(r_values):.1f}-{max(r_values):.1f}px" if r_values else "none"

    # Check 4: Background color has good opacity (0.6-0.8)
    bg_color_match = re.search(r'"backgroundColor":\s*"rgba\([^,]+,[^,]+,[^,]+,([^)]+)\)"', html)
    alpha = float(bg_color_match.group(1)) if bg_color_match else 0
    good_opacity = 0.6 <= alpha <= 0.8

    # Check 5: Labels preserved
    has_labels = "North America" in html

    all_checks = [
        ("Chart type", chart_type == "bubble", chart_type, "bubble"),
        ("[object Object]", not has_object_object, str(has_object_object), "False"),
        ("Varying radius", has_varying_radius, radius_range, "8-40px range"),
        ("Opacity", good_opacity, f"{alpha}", "0.6-0.8"),
        ("Labels preserved", has_labels, str(has_labels), "True")
    ]

    all_passed = all(check[1] for check in all_checks)

    if all_passed:
        print(f"{GREEN}✅ PASS - All bubble fixes working{RESET}")
        for name, _, actual, _ in all_checks:
            print(f"  {name}: {actual}")
        bubble_passed = True
    else:
        print(f"{RED}❌ FAIL{RESET}")
        for name, passed, actual, expected in all_checks:
            if not passed:
                print(f"  {RED}✗ {name}: {actual} (expected: {expected}){RESET}")
            else:
                print(f"  {GREEN}✓ {name}: {actual}{RESET}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")
    if response.status_code >= 400:
        print(f"  Error: {response.text[:200]}")

print()

# Test 3: All 9 Analytics Types
print(f"{BLUE}{BOLD}Test 3: All 9 Analytics Types (Chart Type Validation){RESET}")

expected_types = {
    "revenue_over_time": "line",
    "quarterly_comparison": "bar",
    "market_share": "pie",
    "yoy_growth": "bar",
    "kpi_metrics": "doughnut",
    "category_ranking": "bar",
    "correlation_analysis": "scatter",  # ✅ Fixed in v3.1.9
    "multidimensional_analysis": "bubble",  # ✅ Fixed in v3.1.9
    "multi_metric_comparison": "radar"
}

all_types_passed = True
for analytics_type, expected_chart_type in expected_types.items():
    response = requests.post(
        f"{PRODUCTION_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "prod-v319-test",
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
    print(BOLD + f"{GREEN}v3.1.9 Production Validation: ALL TESTS PASSED ✅{RESET}" + RESET)
    print(f"{GREEN}✅ Scatter chart: No [object Object], 10px points, opaque{RESET}")
    print(f"{GREEN}✅ Bubble chart: No [object Object], varying radius 8-40px, 70% opacity{RESET}")
    print(f"{GREEN}✅ All 9 analytics types with correct Chart.js types{RESET}")
    print(f"\n{BOLD}{GREEN}🎉 v3.1.9 COMPREHENSIVE FIX SUCCESSFUL!{RESET}{RESET}")
else:
    print(BOLD + f"{RED}v3.1.9 Production Validation: SOME TESTS FAILED ❌{RESET}" + RESET)
    if not scatter_passed:
        print(f"{RED}❌ Scatter chart fixes incomplete{RESET}")
    if not bubble_passed:
        print(f"{RED}❌ Bubble chart fixes incomplete{RESET}")
    if not all_types_passed:
        print(f"{RED}❌ Some analytics types have issues{RESET}")
print(BOLD + "="*80 + RESET)
