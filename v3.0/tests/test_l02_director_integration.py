"""
L02 Director Integration Test

Tests the complete L02 analytics flow as it would be called by Director Agent.
Validates request/response schema and content structure.
"""

import asyncio
import sys
import requests
from datetime import datetime

# Base URL for analytics service
BASE_URL = "https://analytics-v30-production.up.railway.app"  # Railway production URL


def test_l02_revenue_over_time():
    """
    Test L02 analytics generation with revenue_over_time analytics type.
    Simulates Director Agent request.
    """
    print("\n" + "=" * 80)
    print("TEST 1: L02 Revenue Over Time")
    print("=" * 80)

    # Simulate Director Agent request
    request_data = {
        "presentation_id": "pres-test-123",
        "slide_id": "slide-7",
        "slide_number": 7,
        "narrative": "Show quarterly revenue growth with strong Q4 performance",
        "topics": ["revenue", "growth", "Q4", "2024"],
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000},
            {"label": "Q3 2024", "value": 162000},
            {"label": "Q4 2024", "value": 195000}
        ],
        "context": {
            "theme": "professional",
            "audience": "Board of Directors",
            "slide_title": "Quarterly Revenue Growth",
            "subtitle": "FY 2024 Performance"
        },
        "options": {
            "enable_editor": True
        }
    }

    print(f"\n📤 Sending request to: {BASE_URL}/api/v1/analytics/L02/revenue_over_time")
    print(f"   Presentation ID: {request_data['presentation_id']}")
    print(f"   Data points: {len(request_data['data'])}")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        print(f"\n📥 Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print("\n✅ SUCCESS - Response received")
            print("\n📊 Content Structure:")
            print(f"   - element_3 (chart): {len(result['content'].get('element_3', ''))} characters")
            print(f"   - element_2 (observations): {len(result['content'].get('element_2', ''))} characters")

            print("\n📈 Metadata:")
            metadata = result.get('metadata', {})
            print(f"   - analytics_type: {metadata.get('analytics_type')}")
            print(f"   - chart_type: {metadata.get('chart_type')}")
            print(f"   - layout: {metadata.get('layout')}")
            print(f"   - data_points: {metadata.get('data_points')}")
            print(f"   - generation_time_ms: {metadata.get('generation_time_ms')}ms")
            print(f"   - theme: {metadata.get('theme')}")
            print(f"   - interactive_editor: {metadata.get('interactive_editor')}")

            # Validate response structure
            assert "content" in result, "Missing 'content' field"
            assert "element_3" in result["content"], "Missing 'element_3' (chart)"
            assert "element_2" in result["content"], "Missing 'element_2' (observations)"
            assert "metadata" in result, "Missing 'metadata' field"

            # Validate content
            element_3 = result["content"]["element_3"]
            element_2 = result["content"]["element_2"]

            assert len(element_3) > 100, "element_3 (chart) seems too short"
            assert len(element_2) > 50, "element_2 (observations) seems too short"
            assert len(element_2) <= 1500, f"element_2 ({len(element_2)} chars) exceeds expected size"

            # Check for Chart.js canvas in chart HTML
            assert "<canvas" in element_3, "Chart HTML missing <canvas> element"
            assert "chart-slide-7" in element_3 or "chart-" in element_3, "Chart missing chart ID"

            # Check observations panel styling
            assert "padding" in element_2.lower(), "Observations missing styling"

            print("\n✅ All validations passed!")

            # Preview content
            print("\n🔍 Content Preview:")
            print(f"   element_3 (chart): {element_3[:150]}...")
            print(f"   element_2 (observations): {element_2[:200]}...")

            return True

        else:
            print(f"\n❌ ERROR - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_l02_market_share():
    """
    Test L02 analytics with market_share analytics type (donut chart).
    """
    print("\n" + "=" * 80)
    print("TEST 2: L02 Market Share")
    print("=" * 80)

    request_data = {
        "presentation_id": "pres-test-456",
        "slide_id": "slide-5",
        "slide_number": 5,
        "narrative": "Market share distribution across product categories",
        "topics": ["market", "share", "products"],
        "data": [
            {"label": "Product A", "value": 35},
            {"label": "Product B", "value": 28},
            {"label": "Product C", "value": 22},
            {"label": "Product D", "value": 15}
        ],
        "context": {
            "theme": "corporate",
            "audience": "Sales Team",
            "slide_title": "Market Share by Product",
            "subtitle": "Q4 2024"
        },
        "options": {
            "enable_editor": False  # Test without editor
        }
    }

    print(f"\n📤 Sending request to: {BASE_URL}/api/v1/analytics/L02/market_share")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/market_share",
            json=request_data,
            timeout=30
        )

        print(f"📥 Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Market share analytics generated")
            print(f"   Chart: {len(result['content']['element_3'])} chars")
            print(f"   Observations: {len(result['content']['element_2'])} chars")
            print(f"   Chart type: {result['metadata']['chart_type']}")
            return True
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False


def test_l02_quarterly_comparison():
    """
    Test L02 analytics with quarterly_comparison (bar chart).
    """
    print("\n" + "=" * 80)
    print("TEST 3: L02 Quarterly Comparison")
    print("=" * 80)

    request_data = {
        "presentation_id": "pres-test-789",
        "slide_id": "slide-3",
        "slide_number": 3,
        "narrative": "Compare quarterly sales across regions",
        "topics": ["quarterly", "sales", "comparison"],
        "data": [
            {"label": "North", "value": 450000},
            {"label": "South", "value": 380000},
            {"label": "East", "value": 520000},
            {"label": "West", "value": 410000}
        ],
        "context": {
            "theme": "vibrant",
            "audience": "Regional Managers",
            "slide_title": "Regional Sales Comparison",
            "subtitle": "Q4 2024"
        }
    }

    print(f"\n📤 Sending request to: {BASE_URL}/api/v1/analytics/L02/quarterly_comparison")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/quarterly_comparison",
            json=request_data,
            timeout=30
        )

        print(f"📥 Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS - Quarterly comparison generated")

            # Check observations character limit
            obs_length = len(result['content']['element_2'])
            print(f"   Observations length: {obs_length} chars")

            if obs_length > 1500:
                print(f"   ⚠️ WARNING: Observations might be too long ({obs_length} chars)")
            else:
                print(f"   ✅ Observations within reasonable length")

            return True
        else:
            print(f"❌ ERROR - Status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False


def run_all_tests():
    """Run all L02 integration tests."""
    print("\n" + "█" * 80)
    print("L02 DIRECTOR INTEGRATION TEST SUITE")
    print("█" * 80)
    print(f"\nTesting against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = []

    # Test 1: Revenue over time (line chart)
    results.append(("Revenue Over Time", test_l02_revenue_over_time()))

    # Test 2: Market share (donut chart)
    results.append(("Market Share", test_l02_market_share()))

    # Test 3: Quarterly comparison (bar chart)
    results.append(("Quarterly Comparison", test_l02_quarterly_comparison()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
