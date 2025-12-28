"""
Comprehensive API test script for synthetic data generation endpoints.

Tests all three integration points:
1. Standalone synthetic data generation
2. Preview mode
3. Analytics with synthetic data fallback
"""

import requests
import json
from datetime import datetime


BASE_URL = "http://localhost:8080"


def test_standalone_generation():
    """Test /api/v1/synthetic/generate endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Standalone Synthetic Data Generation")
    print("="*60)

    test_cases = [
        {
            "name": "Line chart with narrative",
            "payload": {
                "chart_type": "line",
                "narrative": "Show quarterly revenue growth for 2024"
            }
        },
        {
            "name": "D3 Choropleth USA",
            "payload": {
                "chart_type": "d3_choropleth_usa",
                "narrative": "Show sales by top 10 states",
                "num_points": 10
            }
        },
        {
            "name": "D3 Sankey with scenario",
            "payload": {
                "chart_type": "d3_sankey",
                "scenario": "budget_flow"
            }
        },
        {
            "name": "Pie chart - Market share",
            "payload": {
                "chart_type": "pie",
                "num_points": 5,
                "scenario": "market_share"
            }
        }
    ]

    for test in test_cases:
        print(f"\n📊 {test['name']}")
        print(f"   Request: {json.dumps(test['payload'], indent=6)}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/synthetic/generate",
                json=test['payload'],
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS - Generated {len(data['data'])} points")
                print(f"   Sample: {json.dumps(data['data'][0], indent=6)}")
            else:
                print(f"   ❌ FAILED - Status {response.status_code}")
                print(f"   Error: {response.text}")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")


def test_preview_mode():
    """Test /api/v1/preview/{chart_type} endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Preview Mode (Chart with Synthetic Data)")
    print("="*60)

    test_cases = [
        {
            "chart_type": "line",
            "payload": {"narrative": "Show Q4 revenue trends"}
        },
        {
            "chart_type": "d3_choropleth_usa",
            "payload": {"narrative": "Show sales by state"}
        },
        {
            "chart_type": "scatter",
            "payload": None
        }
    ]

    for test in test_cases:
        print(f"\n📊 Preview: {test['chart_type']}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/preview/{test['chart_type']}",
                json=test['payload'] if test['payload'] else {},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                metadata = data.get('metadata', {})
                print(f"   ✅ SUCCESS")
                print(f"   Synthetic data used: {metadata.get('synthetic_data_used')}")
                print(f"   Chart type: {metadata.get('chart_type')}")
                print(f"   Element 3 length: {len(data.get('content', {}).get('element_3', ''))} chars")
            else:
                print(f"   ❌ FAILED - Status {response.status_code}")
                print(f"   Error: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")


def test_analytics_with_synthetic():
    """Test /api/v1/analytics/L02/{analytics_type}?use_synthetic=true endpoint."""
    print("\n" + "="*60)
    print("TEST 3: Analytics with Synthetic Data Fallback")
    print("="*60)

    test_cases = [
        {
            "name": "Revenue over time (use_synthetic=true)",
            "analytics_type": "revenue_over_time",
            "use_synthetic": True,
            "payload": {
                "presentation_id": "test-123",
                "slide_id": "slide-1",
                "slide_number": 1,
                "narrative": "Show quarterly revenue growth for 2024",
                "chart_type": "line"  # Required for synthetic data generation
                # No data field - will be generated
            }
        },
        {
            "name": "Market share (with Director data)",
            "analytics_type": "market_share",
            "use_synthetic": False,
            "payload": {
                "presentation_id": "test-456",
                "slide_id": "slide-2",
                "slide_number": 2,
                "narrative": "Show market share distribution",
                "data": [
                    {"label": "Company A", "value": 35.5},
                    {"label": "Company B", "value": 28.3},
                    {"label": "Company C", "value": 20.2},
                    {"label": "Others", "value": 16.0}
                ]
            }
        },
        {
            "name": "YoY Growth (auto fallback - no data)",
            "analytics_type": "yoy_growth",
            "use_synthetic": False,  # Not requested, but will fallback
            "payload": {
                "presentation_id": "test-789",
                "slide_id": "slide-3",
                "slide_number": 3,
                "narrative": "Show year-over-year growth",
                "chart_type": "bar_vertical"  # Required for automatic fallback
                # No data field - will automatically use synthetic
            }
        }
    ]

    for test in test_cases:
        print(f"\n📊 {test['name']}")

        try:
            url = f"{BASE_URL}/api/v1/analytics/L02/{test['analytics_type']}"
            if test['use_synthetic']:
                url += "?use_synthetic=true"

            response = requests.post(
                url,
                json=test['payload'],
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                metadata = data.get('metadata', {})
                print(f"   ✅ SUCCESS")
                print(f"   Data source: {metadata.get('data_source', 'unknown')}")
                print(f"   Synthetic used: {metadata.get('synthetic_data_used', False)}")
                print(f"   Chart type: {metadata.get('chart_type')}")
            else:
                print(f"   ❌ FAILED - Status {response.status_code}")
                print(f"   Error: {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ ERROR: {e}")


def test_error_cases():
    """Test error handling."""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)

    error_tests = [
        {
            "name": "Invalid chart type",
            "endpoint": "/api/v1/synthetic/generate",
            "payload": {"chart_type": "invalid_chart"}
        },
        {
            "name": "Missing required field",
            "endpoint": "/api/v1/synthetic/generate",
            "payload": {}
        }
    ]

    for test in error_tests:
        print(f"\n❌ {test['name']}")

        try:
            response = requests.post(
                f"{BASE_URL}{test['endpoint']}",
                json=test['payload'],
                timeout=5
            )

            if response.status_code >= 400:
                print(f"   ✅ Correctly returned error {response.status_code}")
                error_data = response.json()
                print(f"   Error code: {error_data.get('error', {}).get('code')}")
            else:
                print(f"   ⚠️  Expected error but got {response.status_code}")

        except Exception as e:
            print(f"   ⚠️  Exception: {e}")


def main():
    """Run all tests."""
    print("\n" + "🔧" * 30)
    print("SYNTHETIC DATA API TEST SUITE")
    print("🔧" * 30)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("\nPlease start the server first:")
        print("  python main.py")
        return

    # Run all test suites
    test_standalone_generation()
    test_preview_mode()
    test_analytics_with_synthetic()
    test_error_cases()

    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
