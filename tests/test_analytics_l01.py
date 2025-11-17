"""
Test Analytics Microservice v3 - L01 Layout

Tests the new Text Service-compatible analytics API with L01 layout
(centered chart with insights).
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"

# Test data
test_cases = [
    {
        "name": "Revenue Over Time",
        "analytics_type": "revenue_over_time",
        "layout": "L01",
        "data": {
            "presentation_id": "test-001",
            "slide_id": "slide-1",
            "slide_number": 1,
            "narrative": "Show quarterly revenue growth highlighting strong Q3-Q4 performance",
            "data": [
                {"label": "Q1 2024", "value": 125000},
                {"label": "Q2 2024", "value": 145000},
                {"label": "Q3 2024", "value": 162000},
                {"label": "Q4 2024", "value": 178000}
            ],
            "context": {
                "theme": "professional",
                "audience": "Board of Directors",
                "slide_title": "Quarterly Revenue Growth",
                "subtitle": "FY 2024 Performance",
                "presentation_name": "Board Review Q4 2024"
            }
        }
    },
    {
        "name": "Market Share",
        "analytics_type": "market_share",
        "layout": "L01",
        "data": {
            "presentation_id": "test-002",
            "slide_id": "slide-2",
            "slide_number": 2,
            "narrative": "Show market share distribution across product lines",
            "data": [
                {"label": "Product A", "value": 35},
                {"label": "Product B", "value": 28},
                {"label": "Product C", "value": 22},
                {"label": "Product D", "value": 15}
            ],
            "context": {
                "theme": "professional",
                "audience": "executives",
                "slide_title": "Market Share Distribution",
                "subtitle": "Product Portfolio Q4 2024"
            }
        }
    },
    {
        "name": "Quarterly Comparison",
        "analytics_type": "quarterly_comparison",
        "layout": "L01",
        "data": {
            "presentation_id": "test-003",
            "slide_id": "slide-3",
            "slide_number": 3,
            "narrative": "Compare sales performance across quarters",
            "data": [
                {"label": "Q1", "value": 45},
                {"label": "Q2", "value": 52},
                {"label": "Q3", "value": 48},
                {"label": "Q4", "value": 61}
            ],
            "context": {
                "theme": "colorful",
                "audience": "sales team",
                "slide_title": "Sales Performance by Quarter",
                "subtitle": "Units Sold (Thousands)"
            }
        }
    }
]


def test_analytics_endpoint(test_case):
    """Test a single analytics type."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_case['name']}")
    print(f"Type: {test_case['analytics_type']}, Layout: {test_case['layout']}")
    print(f"{'='*60}")

    # Make request
    url = f"{BASE_URL}/api/v1/analytics/{test_case['layout']}/{test_case['analytics_type']}"

    print(f"\nPOST {url}")

    try:
        response = requests.post(url, json=test_case['data'], timeout=30)

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Success!")
            print(f"\nResponse structure:")
            print(f"  - content keys: {list(result.get('content', {}).keys())}")
            print(f"  - metadata: {json.dumps(result.get('metadata', {}), indent=4)}")

            # Validate content structure
            content = result.get('content', {})

            # Check required fields for L01
            required_fields = ['slide_title', 'element_1', 'element_4', 'element_3']
            missing_fields = [f for f in required_fields if f not in content]

            if missing_fields:
                print(f"\n⚠️  Warning: Missing fields: {missing_fields}")
            else:
                print(f"\n✅ All required L01 fields present")

            # Check chart HTML
            chart_html = content.get('element_4', '')
            if 'ApexCharts' in chart_html and 'Reveal' in chart_html:
                print(f"✅ Chart HTML contains ApexCharts and Reveal.js integration")
            else:
                print(f"⚠️  Chart HTML may be missing ApexCharts or Reveal.js")

            # Check insight
            insight = content.get('element_3', '')
            word_count = len(insight.split())
            print(f"✅ Insight generated: {word_count} words")

            if word_count < 10:
                print(f"⚠️  Insight seems too short")

            # Save output for inspection
            output_file = f"test_output_{test_case['analytics_type']}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full response saved to: {output_file}")

            # Save HTML for preview
            html_file = f"test_output_{test_case['analytics_type']}.html"
            with open(html_file, 'w') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{test_case['name']} - Test Output</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .slide {{ border: 2px solid #ccc; padding: 20px; margin: 20px 0; }}
        .title {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
        .subtitle {{ font-size: 20px; color: #666; margin-bottom: 20px; }}
        .insight {{ font-size: 18px; margin-top: 20px; line-height: 1.5; }}
    </style>
</head>
<body>
    <h1>{test_case['name']} - Layout Test</h1>
    <div class="slide">
        <div class="title">{content.get('slide_title', '')}</div>
        <div class="subtitle">{content.get('element_1', '')}</div>
        <div class="chart">
            {content.get('element_4', '')}
        </div>
        <div class="insight">{content.get('element_3', '')}</div>
    </div>
</body>
</html>""")
            print(f"💾 HTML preview saved to: {html_file}")

            return True

        else:
            print(f"\n❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_check():
    """Test service health."""
    print(f"\n{'='*60}")
    print("Health Check")
    print(f"{'='*60}")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to service: {e}")
        print(f"\nMake sure the service is running:")
        print(f"  cd agents/analytics_microservice_v3")
        print(f"  source venv/bin/activate")
        print(f"  python main.py")
        return False


if __name__ == "__main__":
    print(f"\n" + "="*60)
    print("Analytics Microservice v3 - L01 Layout Tests")
    print(f"="*60)

    # Check service health first
    if not test_health_check():
        print("\n⚠️  Service not available. Please start the service first.")
        exit(1)

    time.sleep(1)

    # Run tests
    results = []
    for test_case in test_cases:
        result = test_analytics_endpoint(test_case)
        results.append((test_case['name'], result))
        time.sleep(2)  # Brief pause between tests

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
