#!/usr/bin/env python3
"""
Test all 20+ chart types on local server.
Verifies that each chart type generates valid HTML without errors.
"""

import requests
import json
from typing import Dict, List
import sys

BASE_URL = "http://localhost:8080"

# Test data
TEST_DATA = [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 195000},
    {"label": "Q4 2024", "value": 220000}
]

# All chart types to test (23 entries including aliases)
CHART_TYPES = [
    # Original 9 types
    "line",
    "bar_vertical",
    "bar_horizontal",
    "pie",
    "doughnut",
    "scatter",
    "bubble",
    "radar",
    "polar_area",
    # New native types (v3.4.0)
    "area",
    "area_stacked",
    "bar_grouped",
    "bar_stacked",
    "waterfall",
    # New plugin types (v3.4.1-3)
    "treemap",
    "heatmap",
    "matrix",  # alias for heatmap
    "boxplot",
    "candlestick",
    "financial",  # alias for candlestick
    "sankey",
    "mixed"
]


def test_chart_type(chart_type: str) -> Dict:
    """Test a single chart type."""
    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-local",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type} chart",
        "chart_type": chart_type,
        "data": TEST_DATA,
        "context": {
            "theme": "professional",
            "audience": "executives"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Verify response structure
            if "content" in data and "element_3" in data["content"]:
                chart_html = data["content"]["element_3"]

                # Basic validation - check for Chart.js canvas
                if "<canvas" in chart_html or "chart" in chart_html.lower():
                    return {
                        "status": "✅ PASS",
                        "chart_type": chart_type,
                        "error": None,
                        "html_size": len(chart_html)
                    }
                else:
                    return {
                        "status": "⚠️ WARN",
                        "chart_type": chart_type,
                        "error": "HTML doesn't contain expected chart elements",
                        "html_size": len(chart_html)
                    }
            else:
                return {
                    "status": "❌ FAIL",
                    "chart_type": chart_type,
                    "error": "Missing content or element_3 in response",
                    "html_size": 0
                }
        else:
            return {
                "status": "❌ FAIL",
                "chart_type": chart_type,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
                "html_size": 0
            }

    except Exception as e:
        return {
            "status": "❌ ERROR",
            "chart_type": chart_type,
            "error": str(e),
            "html_size": 0
        }


def main():
    """Run tests for all chart types."""
    print("=" * 70)
    print("Testing All Chart Types on Local Server")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Total chart types to test: {len(CHART_TYPES)}")
    print("=" * 70)
    print()

    results = []
    passed = 0
    failed = 0
    warned = 0

    for i, chart_type in enumerate(CHART_TYPES, 1):
        print(f"[{i}/{len(CHART_TYPES)}] Testing {chart_type:20s} ... ", end="", flush=True)
        result = test_chart_type(chart_type)
        results.append(result)

        print(f"{result['status']} ", end="")
        if result['error']:
            print(f"({result['error'][:50]})")
        else:
            print(f"({result['html_size']:,} bytes)")

        if result['status'] == "✅ PASS":
            passed += 1
        elif result['status'] == "⚠️ WARN":
            warned += 1
        else:
            failed += 1

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total: {len(CHART_TYPES)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Warned: {warned}")
    print(f"❌ Failed: {failed}")
    print()

    # Show failures
    failures = [r for r in results if r['status'] in ['❌ FAIL', '❌ ERROR']]
    if failures:
        print("Failed Chart Types:")
        print("-" * 70)
        for r in failures:
            print(f"  {r['chart_type']:20s} - {r['error']}")
        print()

    # Save detailed results
    output_file = "test_results_all_types_local.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(CHART_TYPES),
                "passed": passed,
                "warned": warned,
                "failed": failed
            },
            "results": results
        }, f, indent=2)

    print(f"Detailed results saved to: {output_file}")
    print("=" * 70)

    # Exit with error code if any failures
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
