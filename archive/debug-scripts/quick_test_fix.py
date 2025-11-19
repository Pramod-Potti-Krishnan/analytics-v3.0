#!/usr/bin/env python3
"""
Quick test to verify v3.1.4 hotfix resolves analytics type routing bug.
Tests 3 representative analytics types to confirm fix.
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8080"

def test_analytics_type(analytics_type: str, expected_type: str) -> bool:
    """Test a single analytics type."""
    print(f"\nTesting: {analytics_type}")
    print(f"Expected: {expected_type}")

    response = requests.post(
        f"{BASE_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "test",
            "slide_id": "test-1",
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

    if response.status_code == 200:
        result = response.json()
        actual_type = result.get("metadata", {}).get("analytics_type", "NONE")
        chart_type = result.get("metadata", {}).get("chart_type", "NONE")

        success = actual_type == expected_type
        status = "✅ PASS" if success else "❌ FAIL"

        print(f"  Actual: {actual_type}")
        print(f"  Chart type: {chart_type}")
        print(f"  Status: {status}")

        return success
    else:
        print(f"  ❌ HTTP Error: {response.status_code}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Analytics v3.1.4 Hotfix Verification")
    print("=" * 70)

    # Test 3 representative types
    tests = [
        ("revenue_over_time", "revenue_over_time"),     # Was broken (returned market_share)
        ("market_share", "market_share"),               # Was working
        ("category_ranking", "category_ranking"),       # New type, was broken
    ]

    results = []
    for analytics_type, expected in tests:
        results.append(test_analytics_type(analytics_type, expected))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - Hotfix verified!")
    else:
        print(f"\n❌ SOME TESTS FAILED - Fix not complete")

    exit(0 if passed == total else 1)
