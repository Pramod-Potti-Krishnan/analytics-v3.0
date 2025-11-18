#!/usr/bin/env python3
"""
Test Chart.js type field in PRODUCTION (Railway deployment).
Validates v3.1.5 fix for all 9 analytics types.
"""

import requests
import re
import json
from datetime import datetime

PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Test cases: (analytics_type, expected_chartjs_type)
test_cases = [
    ("revenue_over_time", "line"),
    ("quarterly_comparison", "bar"),
    ("market_share", "pie"),
    ("yoy_growth", "bar"),
    ("kpi_metrics", "doughnut"),
    ("category_ranking", "bar"),
    ("correlation_analysis", "scatter"),
    ("multidimensional_analysis", "bubble"),
    ("multi_metric_comparison", "radar"),
]

print("\n" + BOLD + "=" * 80 + RESET)
print(BOLD + "Analytics v3.1.5 Production Chart.js Type Validation" + RESET)
print(BOLD + f"Testing: {PRODUCTION_URL}" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

print(f"{BLUE}Validating Chart.js type field in generated HTML{RESET}")
print(f"{BLUE}Target: All 9 analytics types with correct Chart.js type{RESET}\n")

passed = 0
failed = 0
results = []

for analytics_type, expected_type in test_cases:
    result = {
        "analytics_type": analytics_type,
        "expected_chartjs_type": expected_type,
        "passed": False
    }

    try:
        response = requests.post(
            f"{PRODUCTION_URL}/api/v1/analytics/L02/{analytics_type}",
            json={
                "presentation_id": "prod-test-v315",
                "slide_id": f"test-{analytics_type}",
                "slide_number": 1,
                "narrative": f"Production test {analytics_type}",
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

            # Extract Chart.js type from config
            match = re.search(r'["\']?type["\']?\s*:\s*["\'](\w+)["\']', html)

            if match:
                actual_type = match.group(1)
                result["actual_chartjs_type"] = actual_type

                if actual_type == expected_type:
                    print(f"{GREEN}✅ {analytics_type}{RESET}")
                    print(f"   Expected: type=\"{expected_type}\"")
                    print(f"   Actual:   type=\"{actual_type}\" {GREEN}(CORRECT){RESET}")
                    result["passed"] = True
                    passed += 1
                else:
                    print(f"{RED}❌ {analytics_type}{RESET}")
                    print(f"   Expected: type=\"{expected_type}\"")
                    print(f"   Actual:   type=\"{actual_type}\" {RED}(WRONG){RESET}")
                    failed += 1
            else:
                print(f"{RED}❌ {analytics_type}{RESET}")
                print(f"   {RED}Could not find type field in Chart.js config{RESET}")
                result["error"] = "Type field not found"
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
print(BOLD + "=" * 80 + RESET)
print(BOLD + "Production Test Summary (v3.1.5)" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

total = len(test_cases)
pass_rate = (passed / total * 100) if total > 0 else 0

print(f"Total tests: {total}")
print(f"{GREEN}Passed: {passed}{RESET}")
print(f"{RED}Failed: {failed}{RESET}")
print(f"Pass rate: {pass_rate:.1f}%")

# Save results
results_file = f"production_test_v315_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(results_file, 'w') as f:
    json.dump({
        "test_name": "Production Chart.js Type Validation v3.1.5",
        "production_url": PRODUCTION_URL,
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": results
    }, f, indent=2)

print(f"\nResults saved to: {results_file}")

# Verdict
print()
if failed == 0:
    print(f"{GREEN}{BOLD}🎉 ALL PRODUCTION TESTS PASSED!{RESET}")
    print(f"{GREEN}✅ v3.1.5 successfully deployed to Railway{RESET}")
    print(f"{GREEN}✅ All 9 analytics types rendering with correct Chart.js type{RESET}")
    print(f"{GREEN}✅ Director team can now integrate Analytics v3.1.5{RESET}\n")
    exit(0)
elif passed > 0:
    print(f"{YELLOW}{BOLD}⚠ PARTIAL SUCCESS{RESET}")
    print(f"{YELLOW}Some chart types correct, deployment may still be in progress{RESET}\n")
    exit(1)
else:
    print(f"{RED}{BOLD}❌ ALL TESTS FAILED{RESET}")
    print(f"{RED}Deployment may have failed or not completed yet{RESET}\n")
    exit(1)
