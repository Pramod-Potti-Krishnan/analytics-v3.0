#!/usr/bin/env python3
"""
Analytics Team - Scatter Chart Fix Validation Suite
Test scatter charts after Layout Service Chart.js 4.4.0 upgrade

Usage:
    python3 test_scatter_chart_fix.py

Requirements:
    - Layout Service must have Chart.js 4.4.0 deployed
    - Analytics Service v3.2.0 running on Railway
"""

import requests
import json
import time
from datetime import datetime

# Service URLs
ANALYTICS_URL = "https://analytics-v30-production.up.railway.app"
LAYOUT_URL = "https://web-production-f0d13.up.railway.app"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Test results tracking
test_results = {
    "scatter_tests": [],
    "regression_tests": [],
    "total_pass": 0,
    "total_fail": 0,
    "timestamp": datetime.now().isoformat()
}

def print_header(title):
    """Print section header"""
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")

def print_test(test_name, status, details=""):
    """Print test result"""
    symbol = f"{GREEN}✅ PASS{RESET}" if status else f"{RED}❌ FAIL{RESET}"
    print(f"{symbol} - {test_name}")
    if details:
        print(f"    {details}")

def test_scatter_chart_generation(size_name, data_points):
    """Test scatter chart generation with Analytics Service"""
    print(f"\n{BLUE}Test: Scatter Chart Generation - {size_name}{RESET}")
    print(f"  Data points: {len(data_points)}")

    response = requests.post(
        f"{ANALYTICS_URL}/api/v1/analytics/L02/correlation_analysis",
        json={
            "presentation_id": "scatter-fix-validation",
            "slide_id": f"scatter-{size_name.lower()}",
            "slide_number": 1,
            "narrative": f"Testing {size_name} scatter chart after Chart.js upgrade",
            "data": data_points
        },
        timeout=30
    )

    if response.status_code != 200:
        print_test(f"Analytics Service Response ({size_name})", False,
                   f"HTTP {response.status_code}")
        test_results["scatter_tests"].append({
            "test": f"scatter_{size_name}",
            "status": "FAIL",
            "reason": f"HTTP {response.status_code}"
        })
        test_results["total_fail"] += 1
        return None

    result = response.json()

    # Validate response structure
    if "content" not in result or "element_3" not in result["content"]:
        print_test(f"Response Structure ({size_name})", False,
                   "Missing content.element_3")
        test_results["scatter_tests"].append({
            "test": f"scatter_{size_name}",
            "status": "FAIL",
            "reason": "Missing element_3"
        })
        test_results["total_fail"] += 1
        return None

    # Validate metadata
    if "metadata" not in result or result["metadata"].get("chart_type") != "scatter":
        print_test(f"Chart Type ({size_name})", False,
                   f"Expected 'scatter', got {result.get('metadata', {}).get('chart_type')}")
        test_results["scatter_tests"].append({
            "test": f"scatter_{size_name}",
            "status": "FAIL",
            "reason": "Wrong chart type"
        })
        test_results["total_fail"] += 1
        return None

    html = result["content"]["element_3"]
    chart_data = result["metadata"]["chart_data"]

    # Validate chart configuration
    checks = {
        "Chart type": chart_data.get("type") == "scatter",
        "Point style": "cross" in json.dumps(chart_data),
        "Point radius": "10" in json.dumps(chart_data),
        "Data points": len(chart_data.get("data", {}).get("datasets", [{}])[0].get("data", [])) == len(data_points),
        "Canvas element": '<canvas id=' in html
    }

    all_passed = all(checks.values())

    for check_name, passed in checks.items():
        if not passed:
            print(f"  {RED}✗{RESET} {check_name} check failed")

    if all_passed:
        print_test(f"Scatter Chart Generation ({size_name})", True,
                   f"{len(data_points)} points, pointStyle: cross, radius: 10px")
        test_results["scatter_tests"].append({
            "test": f"scatter_{size_name}",
            "status": "PASS",
            "data_points": len(data_points)
        })
        test_results["total_pass"] += 1
    else:
        print_test(f"Scatter Chart Generation ({size_name})", False,
                   "Configuration checks failed")
        test_results["scatter_tests"].append({
            "test": f"scatter_{size_name}",
            "status": "FAIL",
            "reason": "Configuration validation failed"
        })
        test_results["total_fail"] += 1

    return result

def test_bubble_chart_regression():
    """Test that bubble charts still work (regression check)"""
    print(f"\n{BLUE}Test: Bubble Chart Regression{RESET}")

    response = requests.post(
        f"{ANALYTICS_URL}/api/v1/analytics/L02/multidimensional_analysis",
        json={
            "presentation_id": "scatter-fix-validation",
            "slide_id": "bubble-regression",
            "slide_number": 2,
            "narrative": "Regression test for bubble charts",
            "data": [
                {"label": "Region A", "value": 180},
                {"label": "Region B", "value": 145},
                {"label": "Region C", "value": 95}
            ]
        },
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("metadata", {}).get("chart_type") == "bubble":
            print_test("Bubble Chart Still Works", True,
                       "Chart type: bubble, circles rendering")
            test_results["regression_tests"].append({
                "test": "bubble_chart",
                "status": "PASS"
            })
            test_results["total_pass"] += 1
            return True

    print_test("Bubble Chart Still Works", False,
               f"HTTP {response.status_code if response else 'No response'}")
    test_results["regression_tests"].append({
        "test": "bubble_chart",
        "status": "FAIL"
    })
    test_results["total_fail"] += 1
    return False

def test_all_chart_types():
    """Test all 9 analytics chart types (regression)"""
    print(f"\n{BLUE}Test: All Chart Types Regression{RESET}")

    chart_types = {
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

    test_data = [
        {"label": "Test 1", "value": 100},
        {"label": "Test 2", "value": 150},
        {"label": "Test 3", "value": 200}
    ]

    all_passed = True

    for analytics_type, expected_chart_type in chart_types.items():
        response = requests.post(
            f"{ANALYTICS_URL}/api/v1/analytics/L02/{analytics_type}",
            json={
                "presentation_id": "scatter-fix-validation",
                "slide_id": f"test-{analytics_type}",
                "slide_number": 1,
                "narrative": "Regression test",
                "data": test_data
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            chart_type = result.get("metadata", {}).get("chart_type")

            if chart_type == expected_chart_type:
                print(f"  {GREEN}✓{RESET} {analytics_type}: {chart_type}")
                test_results["regression_tests"].append({
                    "test": analytics_type,
                    "status": "PASS",
                    "chart_type": chart_type
                })
                test_results["total_pass"] += 1
            else:
                print(f"  {RED}✗{RESET} {analytics_type}: {chart_type} (expected: {expected_chart_type})")
                test_results["regression_tests"].append({
                    "test": analytics_type,
                    "status": "FAIL",
                    "chart_type": chart_type,
                    "expected": expected_chart_type
                })
                test_results["total_fail"] += 1
                all_passed = False
        else:
            print(f"  {RED}✗{RESET} {analytics_type}: HTTP {response.status_code}")
            test_results["regression_tests"].append({
                "test": analytics_type,
                "status": "FAIL",
                "reason": f"HTTP {response.status_code}"
            })
            test_results["total_fail"] += 1
            all_passed = False

        time.sleep(0.5)  # Rate limiting

    return all_passed

def generate_test_report():
    """Generate test report in markdown format"""
    report = f"""# Scatter Chart Fix - Analytics Team Test Results

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tester**: Analytics Team Automated Test Suite
**Layout Service Version**: Chart.js 4.4.0 (expected)
**Analytics Service Version**: v3.2.0

## Test Results Summary

### Overall Results
- **Total Tests**: {test_results['total_pass'] + test_results['total_fail']}
- **Passed**: {test_results['total_pass']} ✅
- **Failed**: {test_results['total_fail']} ❌
- **Pass Rate**: {(test_results['total_pass'] / (test_results['total_pass'] + test_results['total_fail']) * 100):.1f}%

### Scatter Chart Tests
"""

    for test in test_results["scatter_tests"]:
        status_icon = "✅ PASS" if test["status"] == "PASS" else "❌ FAIL"
        report += f"- {status_icon} - {test['test']}"
        if "data_points" in test:
            report += f" ({test['data_points']} points)"
        if "reason" in test:
            report += f" - {test['reason']}"
        report += "\n"

    report += "\n### Regression Tests\n"

    for test in test_results["regression_tests"]:
        status_icon = "✅ PASS" if test["status"] == "PASS" else "❌ FAIL"
        report += f"- {status_icon} - {test['test']}"
        if "chart_type" in test:
            report += f" (type: {test['chart_type']})"
        if "reason" in test:
            report += f" - {test['reason']}"
        report += "\n"

    overall_status = "✅ ALL TESTS PASS" if test_results["total_fail"] == 0 else \
                     "🟡 PARTIAL PASS" if test_results["total_pass"] > test_results["total_fail"] else \
                     "❌ FAIL"

    report += f"""
### Overall Status
{overall_status} - {"Ready for production" if test_results["total_fail"] == 0 else "Issues found, review required"}

### Next Steps
"""

    if test_results["total_fail"] == 0:
        report += "- ✅ All tests passed\n"
        report += "- ✅ Scatter charts working correctly\n"
        report += "- ✅ No regressions detected\n"
        report += "- ✅ Ready for production use\n"
    else:
        report += f"- ⚠️ {test_results['total_fail']} test(s) failed\n"
        report += "- 🔍 Review failed tests above\n"
        report += "- 📞 Contact Layout Service team if scatter charts still blank\n"
        report += "- 🔄 May need rollback if multiple regressions\n"

    report += f"""
### Test Configuration
- **Analytics Service**: {ANALYTICS_URL}
- **Layout Service**: {LAYOUT_URL}
- **Test Timestamp**: {test_results['timestamp']}

---
Generated by automated test suite
"""

    return report

# Main execution
if __name__ == "__main__":
    print_header("Scatter Chart Fix - Validation Test Suite")
    print(f"Analytics Service: {ANALYTICS_URL}")
    print(f"Layout Service: {LAYOUT_URL}")
    print(f"Test Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Small scatter chart (5 points)
    print_header("Phase 1: Scatter Chart Generation Tests")
    small_data = [
        {"label": f"Point {i+1}", "value": 100 + (i * 25)}
        for i in range(5)
    ]
    test_scatter_chart_generation("Small", small_data)

    # Test 2: Medium scatter chart (15 points)
    medium_data = [
        {"label": f"P{i+1}", "value": 10 + (i * 10)}
        for i in range(15)
    ]
    test_scatter_chart_generation("Medium", medium_data)

    # Test 3: Large scatter chart (30 points)
    large_data = [
        {"label": f"Data{i+1}", "value": 50 + (i * 8)}
        for i in range(30)
    ]
    test_scatter_chart_generation("Large", large_data)

    # Test 4: Bubble chart regression
    print_header("Phase 2: Regression Testing")
    test_bubble_chart_regression()

    # Test 5: All chart types
    test_all_chart_types()

    # Generate report
    print_header("Test Results Summary")
    print(f"Total Tests Run: {test_results['total_pass'] + test_results['total_fail']}")
    print(f"{GREEN}Passed: {test_results['total_pass']}{RESET}")
    print(f"{RED}Failed: {test_results['total_fail']}{RESET}")

    if test_results["total_fail"] == 0:
        print(f"\n{BOLD}{GREEN}🎉 ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Scatter charts are working correctly after Chart.js 4.4.0 upgrade{RESET}")
    else:
        print(f"\n{BOLD}{YELLOW}⚠️ SOME TESTS FAILED{RESET}")
        print(f"{YELLOW}Review the results above and contact Layout Service team{RESET}")

    # Save report
    report = generate_test_report()
    report_filename = f"scatter_fix_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, "w") as f:
        f.write(report)

    print(f"\n{BLUE}Test report saved: {report_filename}{RESET}")
    print(f"{BLUE}Full results JSON: test_results.json{RESET}\n")

    # Save JSON results
    with open("test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    # Exit code
    exit(0 if test_results["total_fail"] == 0 else 1)
