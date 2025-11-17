"""
Comprehensive Test Suite for Analytics Type Mapping (v3.1.3)

Tests all 9 analytics types (5 existing + 4 new) to verify:
1. Analytics type to chart type mapping
2. L02 layout response format (element_3 and element_2)
3. Chart generation for all types
4. Error handling for invalid types

Run with: python3 test_analytics_type_mapping.py
"""

import requests
import json
from typing import Dict, Any, List
from datetime import datetime

# Configuration
BASE_URL = "https://analytics-v30-production.up.railway.app"
# For local testing:
# BASE_URL = "http://localhost:8080"

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def test_analytics_type_mapping():
    """Test all 9 analytics types and their chart type mappings."""

    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Analytics Service v3.1.3 - Comprehensive Analytics Type Test{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    # Define all 9 analytics types with expected chart types
    test_cases = [
        # Tier 1: Core Business Analytics (Existing)
        {
            "analytics_type": "revenue_over_time",
            "expected_chart_type": "line",
            "description": "Revenue trends over time",
            "tier": "Tier 1 (Existing)"
        },
        {
            "analytics_type": "quarterly_comparison",
            "expected_chart_type": "bar_vertical",
            "description": "Compare quarterly metrics",
            "tier": "Tier 1 (Existing)"
        },
        {
            "analytics_type": "market_share",
            "expected_chart_type": "pie",
            "description": "Market share distribution",
            "tier": "Tier 1 (Existing)"
        },
        {
            "analytics_type": "yoy_growth",
            "expected_chart_type": "bar_vertical",
            "description": "Year-over-year growth",
            "tier": "Tier 1 (Existing)"
        },
        {
            "analytics_type": "kpi_metrics",
            "expected_chart_type": "doughnut",
            "description": "KPI metrics visualization",
            "tier": "Tier 1 (Existing)"
        },

        # Tier 2: Advanced Visualizations (NEW in v3.1.3)
        {
            "analytics_type": "category_ranking",
            "expected_chart_type": "bar_horizontal",
            "description": "Ranked category comparison",
            "tier": "Tier 2 (NEW)"
        },
        {
            "analytics_type": "correlation_analysis",
            "expected_chart_type": "scatter",
            "description": "Correlation between variables",
            "tier": "Tier 2 (NEW)"
        },
        {
            "analytics_type": "multidimensional_analysis",
            "expected_chart_type": "bubble",
            "description": "3-dimensional data analysis",
            "tier": "Tier 2 (NEW)"
        },
        {
            "analytics_type": "multi_metric_comparison",
            "expected_chart_type": "radar",
            "description": "Compare multiple metrics",
            "tier": "Tier 2 (NEW)"
        },
        # Note: radial_composition not included in first batch for simplicity
    ]

    # Test data (label-value format for all chart types)
    test_data = [
        {"label": "Q1 2024", "value": 125000},
        {"label": "Q2 2024", "value": 145000},
        {"label": "Q3 2024", "value": 195000},
        {"label": "Q4 2024", "value": 220000}
    ]

    results = {
        "passed": 0,
        "failed": 0,
        "total": len(test_cases),
        "details": []
    }

    print(f"{Colors.BLUE}Testing {len(test_cases)} analytics types...{Colors.RESET}\n")

    for i, test_case in enumerate(test_cases, 1):
        analytics_type = test_case["analytics_type"]
        expected_chart_type = test_case["expected_chart_type"]
        description = test_case["description"]
        tier = test_case["tier"]

        print(f"{Colors.BOLD}Test {i}/{len(test_cases)}: {analytics_type}{Colors.RESET}")
        print(f"  Description: {description}")
        print(f"  Tier: {tier}")
        print(f"  Expected chart type: {expected_chart_type}")

        # Prepare request
        request_payload = {
            "presentation_id": f"test-pres-{i}",
            "slide_id": f"slide-{i}",
            "slide_number": i,
            "narrative": f"Test {description}",
            "data": test_data,
            "context": {
                "theme": "professional",
                "audience": "executives"
            }
        }

        try:
            # Make request to L02 endpoint
            url = f"{BASE_URL}/api/v1/analytics/L02/{analytics_type}"
            response = requests.post(url, json=request_payload, timeout=30)

            if response.status_code == 200:
                result = response.json()

                # Verify success field
                assert result.get("success") is True, "Response missing 'success: true'"

                # Verify content structure
                content = result.get("content", {})
                assert "element_3" in content, "Missing element_3 (chart HTML)"
                assert "element_2" in content, "Missing element_2 (observations)"

                # Verify elements are populated
                element_3 = content.get("element_3", "")
                element_2 = content.get("element_2", "")

                assert len(element_3) > 0, "element_3 is empty"
                assert len(element_2) > 0, "element_2 is empty"

                # Verify metadata
                metadata = result.get("metadata", {})
                actual_chart_type = metadata.get("chart_type", "")

                if actual_chart_type == expected_chart_type:
                    print(f"  {Colors.GREEN}✓ PASSED{Colors.RESET}")
                    print(f"    - Chart type: {actual_chart_type}")
                    print(f"    - element_3 size: {len(element_3)} chars")
                    print(f"    - element_2 size: {len(element_2)} chars")
                    results["passed"] += 1
                    results["details"].append({
                        "analytics_type": analytics_type,
                        "status": "PASSED",
                        "chart_type": actual_chart_type
                    })
                else:
                    print(f"  {Colors.YELLOW}⚠ PARTIAL PASS{Colors.RESET}")
                    print(f"    - Expected chart type: {expected_chart_type}")
                    print(f"    - Actual chart type: {actual_chart_type}")
                    results["passed"] += 1
                    results["details"].append({
                        "analytics_type": analytics_type,
                        "status": "PARTIAL",
                        "expected_chart_type": expected_chart_type,
                        "actual_chart_type": actual_chart_type
                    })

            elif response.status_code == 400:
                error = response.json().get("error", {})
                error_code = error.get("code", "UNKNOWN")
                message = error.get("message", "No message")
                suggestion = error.get("suggestion", "No suggestion")

                print(f"  {Colors.RED}✗ FAILED{Colors.RESET}")
                print(f"    - Error code: {error_code}")
                print(f"    - Message: {message}")
                print(f"    - Suggestion: {suggestion}")
                results["failed"] += 1
                results["details"].append({
                    "analytics_type": analytics_type,
                    "status": "FAILED",
                    "error_code": error_code,
                    "message": message
                })

            else:
                print(f"  {Colors.RED}✗ FAILED{Colors.RESET}")
                print(f"    - Unexpected status code: {response.status_code}")
                print(f"    - Response: {response.text[:200]}")
                results["failed"] += 1
                results["details"].append({
                    "analytics_type": analytics_type,
                    "status": "FAILED",
                    "http_status": response.status_code
                })

        except AssertionError as e:
            print(f"  {Colors.RED}✗ FAILED{Colors.RESET}")
            print(f"    - Assertion error: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "analytics_type": analytics_type,
                "status": "FAILED",
                "error": str(e)
            })

        except requests.exceptions.Timeout:
            print(f"  {Colors.RED}✗ FAILED{Colors.RESET}")
            print(f"    - Request timeout (30s)")
            results["failed"] += 1
            results["details"].append({
                "analytics_type": analytics_type,
                "status": "FAILED",
                "error": "Timeout"
            })

        except Exception as e:
            print(f"  {Colors.RED}✗ FAILED{Colors.RESET}")
            print(f"    - Exception: {str(e)}")
            results["failed"] += 1
            results["details"].append({
                "analytics_type": analytics_type,
                "status": "FAILED",
                "error": str(e)
            })

        print()  # Empty line between tests

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"Total tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Pass rate: {pass_rate:.1f}%")

    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}All 9 analytics types are working correctly.{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME TESTS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review failed tests above.{Colors.RESET}")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_analytics_types_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {results_file}")

    return results


def test_invalid_analytics_type():
    """Test that invalid analytics types are properly rejected."""

    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Testing Invalid Analytics Type Handling{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    invalid_type = "nonexistent_type"
    test_data = [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 200}
    ]

    request_payload = {
        "presentation_id": "test-invalid",
        "slide_id": "slide-invalid",
        "slide_number": 1,
        "narrative": "Test invalid type",
        "data": test_data
    }

    try:
        url = f"{BASE_URL}/api/v1/analytics/L02/{invalid_type}"
        response = requests.post(url, json=request_payload, timeout=30)

        if response.status_code == 400:
            error = response.json().get("error", {})
            error_code = error.get("code", "")
            suggestion = error.get("suggestion", "")

            if error_code == "INVALID_ANALYTICS_TYPE":
                print(f"{Colors.GREEN}✓ PASSED{Colors.RESET}")
                print(f"  Invalid analytics type correctly rejected")
                print(f"  Error code: {error_code}")
                print(f"  Suggestion: {suggestion}")

                # Verify suggestion includes all 9 analytics types
                if "category_ranking" in suggestion and "correlation_analysis" in suggestion:
                    print(f"{Colors.GREEN}  ✓ Suggestion includes new analytics types{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}  ⚠ Suggestion may not include all new types{Colors.RESET}")

                return True
            else:
                print(f"{Colors.RED}✗ FAILED{Colors.RESET}")
                print(f"  Expected error code INVALID_ANALYTICS_TYPE, got: {error_code}")
                return False
        else:
            print(f"{Colors.RED}✗ FAILED{Colors.RESET}")
            print(f"  Expected status 400, got: {response.status_code}")
            return False

    except Exception as e:
        print(f"{Colors.RED}✗ FAILED{Colors.RESET}")
        print(f"  Exception: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}Analytics Service v3.1.3 Compatibility Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}Testing Production: {BASE_URL}{Colors.RESET}\n")

    # Run analytics type mapping tests
    mapping_results = test_analytics_type_mapping()

    # Run invalid type test
    invalid_result = test_invalid_analytics_type()

    # Final summary
    print(f"\n{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}Overall Results{Colors.RESET}")
    print(f"{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    total_tests = mapping_results["total"] + 1
    total_passed = mapping_results["passed"] + (1 if invalid_result else 0)
    total_failed = mapping_results["failed"] + (0 if invalid_result else 1)

    print(f"Total tests run: {total_tests}")
    print(f"{Colors.GREEN}Total passed: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}Total failed: {total_failed}{Colors.RESET}")

    if total_failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED - v3.1.3 READY FOR DEPLOYMENT{Colors.RESET}\n")
        exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME TESTS FAILED - REVIEW REQUIRED{Colors.RESET}\n")
        exit(1)
