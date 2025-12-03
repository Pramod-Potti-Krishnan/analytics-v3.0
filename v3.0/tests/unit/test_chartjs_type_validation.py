#!/usr/bin/env python3
"""
Test that Chart.js type field is correctly set in generated HTML.
Validates the actual JavaScript config, not just metadata.

This test extracts the Chart.js type from the generated HTML to ensure
the bug where all charts defaulted to type: "bar" is fixed.
"""

import requests
import re
import json
from datetime import datetime

BASE_URL = "http://localhost:8080"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Test cases: (analytics_type, our_chart_type, expected_chartjs_type)
test_cases = [
    ("revenue_over_time", "line", "line"),
    ("quarterly_comparison", "bar_vertical", "bar"),
    ("market_share", "pie", "pie"),  # Was broken: rendered as "bar"
    ("yoy_growth", "bar_vertical", "bar"),
    ("kpi_metrics", "doughnut", "doughnut"),  # Was broken: rendered as "bar"
    ("category_ranking", "bar_horizontal", "bar"),  # Was broken: rendered as vertical "bar"
    ("correlation_analysis", "scatter", "scatter"),  # Was broken: rendered as "bar"
    ("multidimensional_analysis", "bubble", "bubble"),  # Was broken: rendered as "bar"
    ("multi_metric_comparison", "radar", "radar"),  # Was broken: rendered as "bar"
]

print("\n" + BOLD + "=" * 70 + RESET)
print(BOLD + "Chart.js Type Validation Test" + RESET)
print(BOLD + "Testing: " + BASE_URL + RESET)
print(BOLD + "=" * 70 + RESET + "\n")

print(f"{BLUE}This test extracts the actual Chart.js type from generated HTML{RESET}")
print(f"{BLUE}to verify the bug fix (no more default to type: 'bar'){RESET}\n")

passed = 0
failed = 0
results = []

for analytics_type, our_type, expected_chartjs_type in test_cases:
    result = {
        "analytics_type": analytics_type,
        "our_chart_type": our_type,
        "expected_chartjs_type": expected_chartjs_type,
        "passed": False
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/{analytics_type}",
            json={
                "presentation_id": "test-chartjs-type",
                "slide_id": f"test-{analytics_type}",
                "slide_number": 1,
                "narrative": f"Test {analytics_type}",
                "data": [
                    {"label": "A", "value": 100},
                    {"label": "B", "value": 150},
                    {"label": "C", "value": 200}
                ]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            html = data.get("content", {}).get("element_3", "")

            # Extract Chart.js type from the config object
            # Look for: "type": "bar" or type: "bar" or type: 'bar'
            match = re.search(r'["\']?type["\']?\s*:\s*["\'](\w+)["\']', html)

            if match:
                actual_chartjs_type = match.group(1)
                result["actual_chartjs_type"] = actual_chartjs_type

                if actual_chartjs_type == expected_chartjs_type:
                    print(f"{GREEN}✅ {analytics_type}{RESET}")
                    print(f"   Expected: type=\"{expected_chartjs_type}\"")
                    print(f"   Actual:   type=\"{actual_chartjs_type}\" {GREEN}(CORRECT){RESET}")
                    result["passed"] = True
                    passed += 1
                else:
                    print(f"{RED}❌ {analytics_type}{RESET}")
                    print(f"   Expected: type=\"{expected_chartjs_type}\"")
                    print(f"   Actual:   type=\"{actual_chartjs_type}\" {RED}(WRONG){RESET}")
                    failed += 1
            else:
                print(f"{RED}❌ {analytics_type}{RESET}")
                print(f"   {RED}Could not find type field in Chart.js config{RESET}")
                result["error"] = "Type field not found in HTML"
                failed += 1
        else:
            print(f"{RED}❌ {analytics_type}{RESET}")
            print(f"   {RED}HTTP {response.status_code}{RESET}")
            result["error"] = f"HTTP {response.status_code}"
            failed += 1

    except Exception as e:
        print(f"{RED}❌ {analytics_type}{RESET}")
        print(f"   {RED}Exception: {str(e)}{RESET}")
        result["error"] = str(e)
        failed += 1

    results.append(result)
    print()

# Summary
print(BOLD + "=" * 70 + RESET)
print(BOLD + "Test Summary" + RESET)
print(BOLD + "=" * 70 + RESET + "\n")

total = len(test_cases)
pass_rate = (passed / total * 100) if total > 0 else 0

print(f"Total tests: {total}")
print(f"{GREEN}Passed: {passed}{RESET}")
print(f"{RED}Failed: {failed}{RESET}")
print(f"Pass rate: {pass_rate:.1f}%")

# Save detailed results to JSON
results_file = f"test_results_chartjs_types_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(results_file, 'w') as f:
    json.dump({
        "test_name": "Chart.js Type Validation",
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": results
    }, f, indent=2)

print(f"\nDetailed results saved to: {results_file}")

# Overall verdict
print()
if failed == 0:
    print(f"{GREEN}{BOLD}🎉 ALL CHART.JS TYPES CORRECT!{RESET}")
    print(f"{GREEN}✅ v3.1.5 fix verified - all charts use correct Chart.js type{RESET}")
    print(f"{GREEN}✅ No more default to type: 'bar'{RESET}")
    print(f"{GREEN}✅ Ready for deployment to Railway{RESET}\n")
    exit(0)
elif passed > 0:
    print(f"{YELLOW}{BOLD}⚠ PARTIAL SUCCESS{RESET}")
    print(f"{YELLOW}Some chart types correct, but not all{RESET}\n")
    exit(1)
else:
    print(f"{RED}{BOLD}❌ ALL TESTS FAILED{RESET}")
    print(f"{RED}Chart.js type bug still present{RESET}\n")
    exit(1)
