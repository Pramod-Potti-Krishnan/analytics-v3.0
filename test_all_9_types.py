#!/usr/bin/env python3
"""
Comprehensive test for all 9 analytics types in v3.1.4.
Tests that analytics_type parameter is correctly routed and processed.
"""

import requests
import json
from typing import List, Tuple

BASE_URL = "http://localhost:8080"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# All 9 analytics types with expected chart types
TEST_CASES = [
    # Tier 1: Core Business Analytics (Existing)
    ("revenue_over_time", "line"),
    ("quarterly_comparison", "bar_vertical"),
    ("market_share", "pie"),
    ("yoy_growth", "bar_vertical"),
    ("kpi_metrics", "doughnut"),

    # Tier 2: Advanced Visualizations (NEW in v3.1.3)
    ("category_ranking", "bar_horizontal"),
    ("correlation_analysis", "scatter"),
    ("multidimensional_analysis", "bubble"),
    ("multi_metric_comparison", "radar"),
]

def test_analytics_type(analytics_type: str, expected_chart_type: str) -> dict:
    """Test a single analytics type and return results."""

    response = requests.post(
        f"{BASE_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "test",
            "slide_id": f"test-{analytics_type}",
            "slide_number": 1,
            "narrative": f"Test {analytics_type}",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 150},
                {"label": "Q3", "value": 200}
            ]
        },
        timeout=30
    )

    result = {
        "analytics_type": analytics_type,
        "expected_chart_type": expected_chart_type,
        "status_code": response.status_code,
        "passed": False,
        "errors": []
    }

    if response.status_code != 200:
        result["errors"].append(f"HTTP {response.status_code}")
        return result

    try:
        data = response.json()

        # Check content structure
        if "content" not in data:
            result["errors"].append("Missing 'content' field")
            return result

        if "metadata" not in data:
            result["errors"].append("Missing 'metadata' field")
            return result

        content = data["content"]
        metadata = data["metadata"]

        # Check element_3 and element_2
        if not content.get("element_3"):
            result["errors"].append("element_3 is empty or missing")

        if not content.get("element_2"):
            result["errors"].append("element_2 is empty or missing")

        # CRITICAL: Check analytics_type matches URL parameter
        actual_analytics_type = metadata.get("analytics_type", "NONE")
        if actual_analytics_type != analytics_type:
            result["errors"].append(
                f"analytics_type mismatch: expected '{analytics_type}', got '{actual_analytics_type}'"
            )
            result["actual_analytics_type"] = actual_analytics_type
        else:
            result["actual_analytics_type"] = actual_analytics_type

        # Check chart_type
        actual_chart_type = metadata.get("chart_type", "NONE")
        if actual_chart_type != expected_chart_type:
            result["errors"].append(
                f"chart_type mismatch: expected '{expected_chart_type}', got '{actual_chart_type}'"
            )
        result["actual_chart_type"] = actual_chart_type

        # Test passes if no errors
        result["passed"] = len(result["errors"]) == 0

    except Exception as e:
        result["errors"].append(f"Exception: {str(e)}")

    return result


if __name__ == "__main__":
    print(f"\n{BOLD}{'=' * 80}{RESET}")
    print(f"{BOLD}Analytics Service v3.1.4 - Comprehensive Analytics Type Test{RESET}")
    print(f"{BOLD}Testing: {BASE_URL}{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    results = []
    passed_count = 0
    failed_count = 0

    for i, (analytics_type, expected_chart_type) in enumerate(TEST_CASES, 1):
        print(f"{BOLD}Test {i}/9: {analytics_type}{RESET}")
        print(f"  Expected chart type: {expected_chart_type}")

        result = test_analytics_type(analytics_type, expected_chart_type)
        results.append(result)

        if result["passed"]:
            print(f"  {GREEN}✓ PASSED{RESET}")
            print(f"    analytics_type: {result['actual_analytics_type']}")
            print(f"    chart_type: {result['actual_chart_type']}")
            passed_count += 1
        else:
            print(f"  {RED}✗ FAILED{RESET}")
            for error in result["errors"]:
                print(f"    - {error}")
            if "actual_analytics_type" in result:
                print(f"    actual analytics_type: {result['actual_analytics_type']}")
            if "actual_chart_type" in result:
                print(f"    actual chart_type: {result['actual_chart_type']}")
            failed_count += 1

        print()

    # Summary
    print(f"{BOLD}{'=' * 80}{RESET}")
    print(f"{BOLD}Test Summary{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    total = len(TEST_CASES)
    pass_rate = (passed_count / total * 100) if total > 0 else 0

    print(f"Total tests: {total}")
    print(f"{GREEN}Passed: {passed_count}{RESET}")
    print(f"{RED}Failed: {failed_count}{RESET}")
    print(f"Pass rate: {pass_rate:.1f}%")

    # Overall verdict
    if failed_count == 0:
        print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}✅ v3.1.4 hotfix verified - all 9 analytics types working correctly{RESET}")
        print(f"{GREEN}✅ Analytics type routing bug FIXED{RESET}")
        print(f"{GREEN}✅ Ready for deployment to Railway{RESET}\n")
        exit(0)
    elif passed_count > 0:
        print(f"\n{YELLOW}{BOLD}⚠ PARTIAL SUCCESS{RESET}")
        print(f"{YELLOW}Some analytics types are working, but not all{RESET}\n")
        exit(1)
    else:
        print(f"\n{RED}{BOLD}❌ ALL TESTS FAILED{RESET}")
        print(f"{RED}Critical regression still present{RESET}\n")
        exit(1)
