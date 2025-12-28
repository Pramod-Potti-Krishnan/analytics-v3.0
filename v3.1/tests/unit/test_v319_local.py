#!/usr/bin/env python3
"""Test Analytics v3.1.9 comprehensive fixes locally."""

import requests
import re
import time

# Test against local server
LOCAL_URL = "http://localhost:8080"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

def check_server_running():
    """Check if local server is running."""
    try:
        response = requests.get(f"{LOCAL_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_scatter_fix():
    """Test scatter chart comprehensive fix."""
    print(f"\n{BLUE}{BOLD}Test 1: Scatter Chart Comprehensive Fix{RESET}")
    print(f"{BLUE}Testing: correlation_analysis (scatter chart){RESET}")

    response = requests.post(
        f"{LOCAL_URL}/api/v1/analytics/L02/correlation_analysis",
        json={
            "presentation_id": "test-v319",
            "slide_id": "scatter-fix",
            "slide_number": 1,
            "narrative": "Testing v3.1.9 scatter fixes",
            "data": [
                {"label": "Jan - $20K", "value": 95},
                {"label": "Feb - $28K", "value": 124},
                {"label": "Mar - $35K", "value": 158},
                {"label": "Apr - $42K", "value": 189}
            ]
        },
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        html = result["content"]["element_3"]

        # Check 1: Chart type is scatter
        type_match = re.search(r'"type":\s*"(\w+)"', html)
        chart_type = type_match.group(1) if type_match else "unknown"

        # Check 2: No [object Object] labels
        has_object_object = "[object Object]" in html

        # Check 3: Points are visible (pointRadius = 10)
        radius_match = re.search(r'"pointRadius":\s*(\d+)', html)
        point_radius = int(radius_match.group(1)) if radius_match else 0

        # Check 4: Background color is opaque (not 0.2 alpha)
        bg_color_match = re.search(r'"backgroundColor":\s*"([^"]+)"', html)
        bg_color = bg_color_match.group(1) if bg_color_match else ""
        is_opaque = "rgba" not in bg_color or ",1)" in bg_color or ",0.9)" in bg_color or ",0.8)" in bg_color or ",0.7)" in bg_color

        # Check 5: Labels preserved
        has_labels = "Jan - $20K" in html

        all_passed = (
            chart_type == "scatter" and
            not has_object_object and
            point_radius >= 10 and
            is_opaque and
            has_labels
        )

        if all_passed:
            print(f"{GREEN}✅ PASS - All scatter fixes working{RESET}")
            print(f"  Chart type: {chart_type}")
            print(f"  [object Object]: {has_object_object} (should be False)")
            print(f"  Point radius: {point_radius}px (should be ≥10)")
            print(f"  Background: {bg_color[:50]}... (opaque)")
            print(f"  Labels preserved: {has_labels}")
        else:
            print(f"{RED}❌ FAIL{RESET}")
            print(f"  Chart type: {chart_type} (expected: scatter)")
            print(f"  [object Object]: {has_object_object}")
            print(f"  Point radius: {point_radius}px (expected: ≥10)")
            print(f"  Background: {bg_color[:50]}...")
            print(f"  Labels: {has_labels}")

        return all_passed
    else:
        print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")
        return False

def test_bubble_fix():
    """Test bubble chart comprehensive fix."""
    print(f"\n{BLUE}{BOLD}Test 2: Bubble Chart Comprehensive Fix{RESET}")
    print(f"{BLUE}Testing: multidimensional_analysis (bubble chart){RESET}")

    response = requests.post(
        f"{LOCAL_URL}/api/v1/analytics/L02/multidimensional_analysis",
        json={
            "presentation_id": "test-v319",
            "slide_id": "bubble-fix",
            "slide_number": 2,
            "narrative": "Testing v3.1.9 bubble fixes",
            "data": [
                {"label": "North America", "value": 180},
                {"label": "Europe", "value": 145},
                {"label": "APAC", "value": 95},
                {"label": "LATAM", "value": 62}
            ]
        },
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        html = result["content"]["element_3"]

        # Check 1: Chart type is bubble
        type_match = re.search(r'"type":\s*"(\w+)"', html)
        chart_type = type_match.group(1) if type_match else "unknown"

        # Check 2: No [object Object] labels
        has_object_object = "[object Object]" in html

        # Check 3: Varying radius (proportional scaling)
        r_values = re.findall(r'"r":\s*(\d+\.?\d*)', html)
        has_varying_radius = len(set(r_values)) > 1 if r_values else False
        radius_range = f"{min(r_values)}-{max(r_values)}" if r_values else "none"

        # Check 4: Background color has good opacity (0.7 alpha)
        bg_color_match = re.search(r'"backgroundColor":\s*"rgba\([^,]+,[^,]+,[^,]+,([^)]+)\)"', html)
        alpha = float(bg_color_match.group(1)) if bg_color_match else 0
        good_opacity = 0.6 <= alpha <= 0.8

        # Check 5: Labels preserved
        has_labels = "North America" in html

        all_passed = (
            chart_type == "bubble" and
            not has_object_object and
            has_varying_radius and
            good_opacity and
            has_labels
        )

        if all_passed:
            print(f"{GREEN}✅ PASS - All bubble fixes working{RESET}")
            print(f"  Chart type: {chart_type}")
            print(f"  [object Object]: {has_object_object} (should be False)")
            print(f"  Varying radius: {has_varying_radius} (range: {radius_range}px)")
            print(f"  Opacity: {alpha} (should be 0.6-0.8)")
            print(f"  Labels preserved: {has_labels}")
        else:
            print(f"{RED}❌ FAIL{RESET}")
            print(f"  Chart type: {chart_type} (expected: bubble)")
            print(f"  [object Object]: {has_object_object}")
            print(f"  Varying radius: {has_varying_radius} (range: {radius_range}px)")
            print(f"  Opacity: {alpha} (expected: 0.6-0.8)")
            print(f"  Labels: {has_labels}")

        return all_passed
    else:
        print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")
        return False

def test_all_9_types():
    """Test all 9 analytics types."""
    print(f"\n{BLUE}{BOLD}Test 3: All 9 Analytics Types (Chart Type Validation){RESET}")

    expected_types = {
        "revenue_over_time": "line",
        "quarterly_comparison": "bar",
        "market_share": "pie",
        "yoy_growth": "bar",
        "kpi_metrics": "doughnut",
        "category_ranking": "bar",
        "correlation_analysis": "scatter",  # ✅ Fixed
        "multidimensional_analysis": "bubble",  # ✅ Fixed
        "multi_metric_comparison": "radar"
    }

    all_correct = True
    for analytics_type, expected_chart_type in expected_types.items():
        response = requests.post(
            f"{LOCAL_URL}/api/v1/analytics/L02/{analytics_type}",
            json={
                "presentation_id": "test-v319",
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

    return all_correct

def main():
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Analytics v3.1.9 Local Comprehensive Fix Validation{RESET}")
    print(f"{BOLD}Testing: {LOCAL_URL}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}")

    # Check if server is running
    if not check_server_running():
        print(f"\n{RED}{BOLD}❌ Local server not running!{RESET}")
        print(f"{YELLOW}Please start the server first:{RESET}")
        print(f"  cd agents/analytics_microservice_v3")
        print(f"  python3 main.py")
        print(f"\nWaiting 5 seconds for server to start...")
        time.sleep(5)

        if not check_server_running():
            print(f"{RED}Server still not responding. Exiting.{RESET}")
            return

    # Run tests
    scatter_passed = test_scatter_fix()
    bubble_passed = test_bubble_fix()
    all_types_passed = test_all_9_types()

    # Summary
    print(f"\n{BOLD}{'='*80}{RESET}")
    if scatter_passed and bubble_passed and all_types_passed:
        print(f"{BOLD}{GREEN}v3.1.9 Local Validation: ALL TESTS PASSED ✅{RESET}{RESET}")
        print(f"{GREEN}✅ Scatter chart: No [object Object], points visible (10px), opaque{RESET}")
        print(f"{GREEN}✅ Bubble chart: No [object Object], varying radius, 70% opacity{RESET}")
        print(f"{GREEN}✅ All 9 analytics types with correct Chart.js types{RESET}")
        print(f"\n{YELLOW}Ready to deploy v3.1.9 to Railway!{RESET}")
    else:
        print(f"{BOLD}{RED}v3.1.9 Local Validation: SOME TESTS FAILED ❌{RESET}{RESET}")
        if not scatter_passed:
            print(f"{RED}❌ Scatter chart fixes incomplete{RESET}")
        if not bubble_passed:
            print(f"{RED}❌ Bubble chart fixes incomplete{RESET}")
        if not all_types_passed:
            print(f"{RED}❌ Some analytics types have issues{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

if __name__ == "__main__":
    main()
