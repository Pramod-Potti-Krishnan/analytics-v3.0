#!/usr/bin/env python3
"""
Test chart_type override parameter fix.
Verifies that the chart_type parameter is now respected.
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_chart_type_override():
    """Test that chart_type parameter overrides default."""

    print("=" * 80)
    print("Testing chart_type Override Fix")
    print("=" * 80)
    print()

    # Test 1: Request area chart (should override default line chart for revenue_over_time)
    print("Test 1: Override revenue_over_time (default: line) with area chart")
    print("-" * 80)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-override",
        "slide_id": "slide-1",
        "slide_number": 1,
        "narrative": "Show cumulative revenue growth",
        "chart_type": "area",  # OVERRIDE: Should use area instead of line
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000},
            {"label": "Q3 2024", "value": 195000},
            {"label": "Q4 2024", "value": 220000}
        ],
        "context": {
            "theme": "professional",
            "slide_title": "Revenue Growth"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        actual_chart_type = result.get("metadata", {}).get("chart_type", "unknown")

        print(f"Requested chart_type: area")
        print(f"Actual chart_type: {actual_chart_type}")

        if actual_chart_type == "area":
            print("✅ TEST PASSED: chart_type override working!")
        else:
            print(f"❌ TEST FAILED: Expected 'area', got '{actual_chart_type}'")

        print()

    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        print()
        return

    # Test 2: Request treemap chart
    print("Test 2: Override market_share (default: pie) with treemap chart")
    print("-" * 80)

    url = f"{BASE_URL}/api/v1/analytics/L02/market_share"
    payload = {
        "presentation_id": "test-override",
        "slide_id": "slide-2",
        "slide_number": 2,
        "narrative": "Show budget allocation",
        "chart_type": "treemap",  # OVERRIDE: Should use treemap instead of pie
        "data": [
            {"label": "Engineering", "value": 450000},
            {"label": "Sales", "value": 320000},
            {"label": "Marketing", "value": 180000},
            {"label": "Operations", "value": 120000}
        ],
        "context": {
            "theme": "colorful",
            "slide_title": "Budget Allocation"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        actual_chart_type = result.get("metadata", {}).get("chart_type", "unknown")

        print(f"Requested chart_type: treemap")
        print(f"Actual chart_type: {actual_chart_type}")

        if actual_chart_type == "treemap":
            print("✅ TEST PASSED: chart_type override working!")
        else:
            print(f"❌ TEST FAILED: Expected 'treemap', got '{actual_chart_type}'")

        print()

    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        print()
        return

    # Test 3: Request waterfall chart
    print("Test 3: Override with waterfall chart")
    print("-" * 80)

    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-override",
        "slide_id": "slide-3",
        "slide_number": 3,
        "narrative": "Show revenue changes",
        "chart_type": "waterfall",  # OVERRIDE: Should use waterfall
        "data": [
            {"label": "Q1 Starting", "value": 100000},
            {"label": "Q1 Change", "value": 25000},
            {"label": "Q2 Change", "value": 20000},
            {"label": "Q3 Change", "value": 50000}
        ],
        "context": {
            "theme": "professional",
            "slide_title": "Revenue Changes"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        actual_chart_type = result.get("metadata", {}).get("chart_type", "unknown")

        print(f"Requested chart_type: waterfall")
        print(f"Actual chart_type: {actual_chart_type}")

        if actual_chart_type == "waterfall":
            print("✅ TEST PASSED: chart_type override working!")
        else:
            print(f"❌ TEST FAILED: Expected 'waterfall', got '{actual_chart_type}'")

        print()

    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        print()
        return

    print("=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_chart_type_override()
