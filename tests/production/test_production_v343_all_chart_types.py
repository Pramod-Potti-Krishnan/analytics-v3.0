#!/usr/bin/env python3
"""
Production Test Suite for Analytics Microservice v3.4.3
Tests all 20+ chart types against production API.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List
import sys

# Production API endpoint
PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

# Test data
TEST_DATA = [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 195000},
    {"label": "Q4 2024", "value": 220000}
]

# All chart types (including aliases)
ALL_CHART_TYPES = [
    # Original 9 Chart.js types
    "line", "bar_vertical", "bar_horizontal", "pie", "doughnut",
    "scatter", "bubble", "radar", "polar_area",
    # New native Chart.js types (v3.4.0)
    "area", "area_stacked", "bar_grouped", "bar_stacked", "waterfall",
    # New Chart.js plugin types (v3.4.1-3)
    "treemap", "heatmap", "matrix", "boxplot",
    "candlestick", "financial", "sankey", "mixed"
]

# Unique chart types (excluding aliases)
UNIQUE_CHART_TYPES = [
    "line", "bar_vertical", "bar_horizontal", "pie", "doughnut",
    "scatter", "bubble", "radar", "polar_area", "area", "area_stacked",
    "bar_grouped", "bar_stacked", "waterfall", "treemap",
    "heatmap", "boxplot", "candlestick", "sankey", "mixed"
]


def test_health_endpoint():
    """Test /health endpoint."""
    try:
        response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                return {"status": "✅ PASS", "error": None}
            else:
                return {"status": "❌ FAIL", "error": "Status not healthy"}
        else:
            return {"status": "❌ FAIL", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "❌ ERROR", "error": str(e)}


def test_chart_types_endpoint():
    """Test /api/v1/chart-types endpoint."""
    try:
        response = requests.get(f"{PRODUCTION_URL}/api/v1/chart-types", timeout=10)
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", {})
            total = summary.get("total_chart_types", 0)

            # Should now have 23 chart types (20 unique + 3 aliases: matrix, financial, and one more)
            expected_min = 20  # At least 20 unique types
            if total >= expected_min:
                return {
                    "status": "✅ PASS",
                    "error": None,
                    "total_types": total,
                    "chartjs_types": summary.get("chartjs_types", 0)
                }
            else:
                return {
                    "status": "❌ FAIL",
                    "error": f"Expected >={expected_min} types, got {total}",
                    "total_types": total
                }
        else:
            return {"status": "❌ FAIL", "error": f"HTTP {response.status_code}", "total_types": 0}
    except Exception as e:
        return {"status": "❌ ERROR", "error": str(e), "total_types": 0}


def test_chart_generation(chart_type: str) -> Dict:
    """Test generating a specific chart type."""
    url = f"{PRODUCTION_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": f"prod-test-v343",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Production test for {chart_type} chart",
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

                # Verify it's actual Chart.js HTML (not a fallback)
                if "<canvas" in chart_html:
                    # Check metadata
                    metadata = data.get("metadata", {})
                    actual_type = metadata.get("chart_type", "")

                    return {
                        "status": "✅ PASS",
                        "chart_type": chart_type,
                        "actual_type": actual_type,
                        "error": None,
                        "html_size": len(chart_html)
                    }
                else:
                    return {
                        "status": "❌ FAIL",
                        "chart_type": chart_type,
                        "error": "No canvas element found - may be fallback chart",
                        "html_size": len(chart_html)
                    }
            else:
                return {
                    "status": "❌ FAIL",
                    "chart_type": chart_type,
                    "error": "Missing content or element_3",
                    "html_size": 0
                }
        else:
            error_text = response.text[:200] if response.text else f"HTTP {response.status_code}"
            return {
                "status": "❌ FAIL",
                "chart_type": chart_type,
                "error": error_text,
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
    """Run comprehensive production tests."""
    print("=" * 80)
    print("Analytics Microservice v3.4.3 - Production Test Suite")
    print("=" * 80)
    print(f"Production URL: {PRODUCTION_URL}")
    print(f"Test Time: {datetime.utcnow().isoformat()}Z")
    print("=" * 80)
    print()

    all_results = {}

    # Test 1: Health check
    print("Test 1: Health Endpoint")
    print("-" * 80)
    health_result = test_health_endpoint()
    all_results["health"] = health_result
    print(f"Result: {health_result['status']}")
    if health_result['error']:
        print(f"Error: {health_result['error']}")
    print()

    # Test 2: Chart types catalog
    print("Test 2: Chart Types Catalog")
    print("-" * 80)
    catalog_result = test_chart_types_endpoint()
    all_results["catalog"] = catalog_result
    print(f"Result: {catalog_result['status']}")
    print(f"Total chart types: {catalog_result.get('total_types', 0)}")
    print(f"Chart.js types: {catalog_result.get('chartjs_types', 0)}")
    if catalog_result['error']:
        print(f"Error: {catalog_result['error']}")
    print()

    # Test 3: Chart generation for all types
    print("Test 3: Chart Generation (All Types)")
    print("-" * 80)
    chart_results = []
    passed = 0
    failed = 0

    for i, chart_type in enumerate(ALL_CHART_TYPES, 1):
        print(f"[{i}/{len(ALL_CHART_TYPES)}] {chart_type:20s} ... ", end="", flush=True)
        result = test_chart_generation(chart_type)
        chart_results.append(result)

        print(f"{result['status']}")

        if result['status'] == "✅ PASS":
            passed += 1
        else:
            failed += 1
            if result['error']:
                print(f"     Error: {result['error']}")

    all_results["chart_generation"] = {
        "total": len(ALL_CHART_TYPES),
        "passed": passed,
        "failed": failed,
        "results": chart_results
    }

    print()
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Health Check: {health_result['status']}")
    print(f"Catalog Check: {catalog_result['status']}")
    print(f"Chart Generation: {passed}/{len(ALL_CHART_TYPES)} passed")
    print()

    # Show failures
    failures = [r for r in chart_results if r['status'] != "✅ PASS"]
    if failures:
        print("Failed Chart Types:")
        print("-" * 80)
        for r in failures:
            print(f"  {r['chart_type']:20s} - {r.get('error', 'Unknown error')}")
        print()

    # Save results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = f"production_test_v343_results_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_time": datetime.utcnow().isoformat() + "Z",
            "production_url": PRODUCTION_URL,
            "version": "v3.4.3",
            "results": all_results
        }, f, indent=2)

    print(f"Detailed results saved to: {output_file}")
    print("=" * 80)

    # Determine overall success
    overall_success = (
        health_result['status'] == "✅ PASS" and
        catalog_result['status'] == "✅ PASS" and
        failed == 0
    )

    if overall_success:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
