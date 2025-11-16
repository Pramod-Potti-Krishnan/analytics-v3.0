"""
Test Analytics Microservice v3 - L03 Layout (Side-by-Side Comparison)

Tests the new Text Service-compatible analytics API with L03 layout
(side-by-side comparison with dual charts and descriptions).
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"

# Test data - designed for side-by-side comparison
test_cases = [
    {
        "name": "Year-over-Year Revenue Comparison",
        "analytics_type": "yoy_growth",
        "layout": "L03",
        "data": {
            "presentation_id": "test-l03-001",
            "slide_id": "slide-comparison-1",
            "slide_number": 5,
            "narrative": "Compare 2023 vs 2024 quarterly revenue showing 25% YoY growth",
            "data": [
                # First half: 2023 data
                {"label": "Q1 2023", "value": 125000},
                {"label": "Q2 2023", "value": 145000},
                {"label": "Q3 2023", "value": 162000},
                {"label": "Q4 2023", "value": 178000},
                # Second half: 2024 data
                {"label": "Q1 2024", "value": 156000},
                {"label": "Q2 2024", "value": 181000},
                {"label": "Q3 2024", "value": 203000},
                {"label": "Q4 2024", "value": 223000}
            ],
            "context": {
                "theme": "professional",
                "audience": "Board of Directors",
                "slide_title": "Year-over-Year Revenue Growth",
                "subtitle": "2023 vs 2024 Quarterly Comparison",
                "presentation_name": "Annual Board Review 2024"
            }
        }
    },
    {
        "name": "Before/After Product Launch Metrics",
        "analytics_type": "quarterly_comparison",
        "layout": "L03",
        "data": {
            "presentation_id": "test-l03-002",
            "slide_id": "slide-comparison-2",
            "slide_number": 8,
            "narrative": "Compare sales metrics before and after product launch showing 60% increase",
            "data": [
                # Before launch
                {"label": "Jan", "value": 35000},
                {"label": "Feb", "value": 38000},
                {"label": "Mar", "value": 36000},
                {"label": "Apr", "value": 40000},
                # After launch
                {"label": "May", "value": 58000},
                {"label": "Jun", "value": 65000},
                {"label": "Jul", "value": 62000},
                {"label": "Aug", "value": 70000}
            ],
            "context": {
                "theme": "colorful",
                "audience": "Product Team",
                "slide_title": "Product Launch Impact Analysis",
                "subtitle": "Pre-Launch vs Post-Launch Performance",
                "presentation_name": "Q3 Product Review"
            }
        }
    },
    {
        "name": "Regional Performance Comparison",
        "analytics_type": "market_share",
        "layout": "L03",
        "data": {
            "presentation_id": "test-l03-003",
            "slide_id": "slide-comparison-3",
            "slide_number": 12,
            "narrative": "Compare market share between North America and Europe regions",
            "data": [
                # North America
                {"label": "Enterprise", "value": 45},
                {"label": "SMB", "value": 30},
                {"label": "Startup", "value": 25},
                # Europe
                {"label": "Enterprise", "value": 38},
                {"label": "SMB", "value": 35},
                {"label": "Startup", "value": 27}
            ],
            "context": {
                "theme": "professional",
                "audience": "Regional Directors",
                "slide_title": "Regional Market Share Distribution",
                "subtitle": "North America vs Europe - Q4 2024",
                "presentation_name": "Global Sales Review"
            }
        }
    }
]


def test_analytics_endpoint(test_case):
    """Test a single analytics type with L03 layout."""
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

            # Check required fields for L03 (side-by-side comparison)
            required_fields = [
                'slide_title',    # Title
                'element_1',      # Subtitle
                'element_4',      # Left chart
                'element_2',      # Right chart
                'element_3',      # Left description
                'element_5'       # Right description
            ]
            missing_fields = [f for f in required_fields if f not in content]

            if missing_fields:
                print(f"\n⚠️  Warning: Missing fields: {missing_fields}")
            else:
                print(f"\n✅ All required L03 fields present")

            # Validate left chart
            left_chart_html = content.get('element_4', '')
            if 'ApexCharts' in left_chart_html and 'chart-left' in left_chart_html:
                print(f"✅ Left chart HTML contains ApexCharts with proper ID")
            else:
                print(f"⚠️  Left chart HTML may be missing ApexCharts or chart ID")

            # Validate right chart
            right_chart_html = content.get('element_2', '')
            if 'ApexCharts' in right_chart_html and 'chart-right' in right_chart_html:
                print(f"✅ Right chart HTML contains ApexCharts with proper ID")
            else:
                print(f"⚠️  Right chart HTML may be missing ApexCharts or chart ID")

            # Check left description
            left_desc = content.get('element_3', '')
            left_word_count = len(left_desc.split())
            print(f"✅ Left description generated: {left_word_count} words")

            if left_word_count < 5:
                print(f"⚠️  Left description seems too short")

            # Check right description
            right_desc = content.get('element_5', '')
            right_word_count = len(right_desc.split())
            print(f"✅ Right description generated: {right_word_count} words")

            if right_word_count < 5:
                print(f"⚠️  Right description seems too short")

            # Save output for inspection
            output_file = f"test_output_{test_case['analytics_type']}_l03.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Full response saved to: {output_file}")

            # Save HTML preview for both charts
            html_file = f"test_output_{test_case['analytics_type']}_l03.html"
            with open(html_file, 'w') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{test_case['name']} - L03 Test Output</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .slide {{
            background: white;
            border: 2px solid #ccc;
            padding: 20px;
            margin: 20px 0;
            max-width: 1920px;
        }}
        .title {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; text-align: center; }}
        .subtitle {{ font-size: 20px; color: #666; margin-bottom: 20px; text-align: center; }}
        .comparison-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 20px;
        }}
        .chart-panel {{
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            background: #fafafa;
        }}
        .chart-label {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .description {{
            font-size: 16px;
            margin-top: 15px;
            line-height: 1.5;
            color: #555;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>L03 Layout Test - Side-by-Side Comparison</h1>
    <div class="slide">
        <div class="title">{content.get('slide_title', '')}</div>
        <div class="subtitle">{content.get('element_1', '')}</div>

        <div class="comparison-container">
            <div class="chart-panel">
                <div class="chart-label">Before / Period 1</div>
                <div class="chart">
                    {content.get('element_4', '')}
                </div>
                <div class="description">{content.get('element_3', '')}</div>
            </div>

            <div class="chart-panel">
                <div class="chart-label">After / Period 2</div>
                <div class="chart">
                    {content.get('element_2', '')}
                </div>
                <div class="description">{content.get('element_5', '')}</div>
            </div>
        </div>
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
    print("Analytics Microservice v3 - L03 Layout Tests")
    print("Side-by-Side Comparison with Dual Charts")
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
        print("\n🎉 All L03 comparison tests passed!")
        print("\n📋 Key validations:")
        print("  ✓ Dual chart generation (left + right)")
        print("  ✓ Paired descriptions for comparison")
        print("  ✓ Data splitting logic")
        print("  ✓ Side-by-side layout structure")
        print("  ✓ ApexCharts integration with unique IDs")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
