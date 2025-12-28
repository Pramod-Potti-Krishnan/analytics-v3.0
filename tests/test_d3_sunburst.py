"""Test D3.js sunburst chart - multi-level hierarchical visualization."""
import requests
import json
import os
from datetime import datetime

# Test both local and production
BASE_URLS = {
    "local": "http://localhost:8080",
    "production": "https://analytics-v30-production.up.railway.app"
}

def test_d3_sunburst(base_url: str, env_name: str):
    """Test d3_sunburst chart type."""
    print(f"\n{'='*60}")
    print(f"Testing D3 Sunburst on {env_name.upper()}")
    print(f"{'='*60}\n")

    url = f"{base_url}/api/v1/analytics/L02/market_share"

    payload = {
        "presentation_id": "test-sunburst-001",
        "slide_id": "slide-sunburst-1",
        "slide_number": 1,
        "narrative": "Show FY2025 budget allocation hierarchy",
        "chart_type": "d3_sunburst",  # Explicitly request D3 sunburst
        "data": [
            {"label": "Engineering", "value": 800000},
            {"label": "Sales", "value": 600000},
            {"label": "Marketing", "value": 400000},
            {"label": "Operations", "value": 350000},
            {"label": "Finance", "value": 200000},
            {"label": "HR", "value": 150000}
        ],
        "context": {
            "theme": "professional",
            "slide_title": "Budget Hierarchy",
            "subtitle": "FY 2025 - Multi-Level Breakdown"
        }
    }

    print(f"URL: {url}")
    print(f"Chart Type: d3_sunburst")
    print(f"Data Points: {len(payload['data'])}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    print(f"\n{'-'*60}\n")

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS - Response received\n")

            # Check response structure
            print(f"Response Keys: {list(result.keys())}")

            if "content" in result:
                content = result["content"]
                print(f"Content Keys: {list(content.keys())}\n")

                # Check for D3.js chart in element_3 (L02 chart container)
                element_3 = content.get("element_3", "")
                element_2 = content.get("element_2", "")

                print(f"Chart HTML (element_3):")
                print(f"  - Length: {len(element_3)} chars")
                print(f"  - Preview: {element_3[:200]}...\n")

                print(f"Observations (element_2):")
                print(f"  - Length: {len(element_2)} chars")
                print(f"  - Preview: {element_2[:200]}...\n")

                # D3.js sunburst specific checks
                has_d3_cdn = "cdn.jsdelivr.net/npm/d3@7" in element_3
                has_svg = "svg" in element_3.lower()
                has_sunburst = "sunburst" in element_3.lower()
                has_d3_partition = "d3.partition" in element_3
                has_d3_arc = "d3.arc" in element_3
                has_chart_id = "d3-sunburst" in element_3

                print(f"D3.js Sunburst Indicators:")
                print(f"  ✓ Has D3.js v7 CDN: {has_d3_cdn}")
                print(f"  ✓ Has SVG rendering: {has_svg}")
                print(f"  ✓ Has sunburst reference: {has_sunburst}")
                print(f"  ✓ Has d3.partition(): {has_d3_partition}")
                print(f"  ✓ Has d3.arc(): {has_d3_arc}")
                print(f"  ✓ Has d3-sunburst ID: {has_chart_id}\n")

                # Metadata checks
                if "metadata" in result:
                    metadata = result["metadata"]
                    print(f"Metadata:")
                    print(f"  - Chart Type: {metadata.get('chart_type')}")
                    print(f"  - Chart Library: {metadata.get('chart_library', 'N/A')}")
                    print(f"  - Data Points: {metadata.get('data_points')}")
                    print(f"  - Generation Time: {metadata.get('generation_time_ms')}ms")
                    print(f"  - Theme: {metadata.get('theme')}\n")

                # Save HTML to file for inspection
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_d3_sunburst_{env_name}_{timestamp}.html"

                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D3 Sunburst Test - {env_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .metadata {{
            margin: 20px 0;
            padding: 15px;
            background: #e9ecef;
            border-left: 4px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>D3 Sunburst Chart Test ({env_name.upper()})</h1>

        <div class="metadata">
            <h3>Test Information</h3>
            <p><strong>Environment:</strong> {env_name}</p>
            <p><strong>Chart Type:</strong> d3_sunburst</p>
            <p><strong>Data Points:</strong> {len(payload['data'])}</p>
            <p><strong>Test Time:</strong> {timestamp}</p>
        </div>

        <div class="chart-section">
            <h2>Chart Title</h2>
            <h3>Subtitle</h3>
            {element_3}
        </div>

        <div class="metadata">
            <h3>Observations</h3>
            {element_2}
        </div>

        <div class="metadata">
            <h3>Response Metadata</h3>
            <pre>{json.dumps(result.get('metadata', {}), indent=2)}</pre>
        </div>
    </div>
</body>
</html>"""

                with open(filename, "w") as f:
                    f.write(html_content)

                print(f"📄 HTML saved to: {filename}")
                print(f"   Open this file in a browser to see the D3 sunburst chart\n")

                # Validation summary
                all_indicators = [has_d3_cdn, has_svg, has_sunburst, has_d3_partition, has_d3_arc]
                if all(all_indicators):
                    print(f"✅ ALL CHECKS PASSED - D3 sunburst rendering correctly")
                else:
                    print(f"⚠️  SOME CHECKS FAILED - Review the HTML output")

        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    print("="*60)
    print("D3.JS SUNBURST CHART TEST")
    print("Testing D3.js integration for hierarchical visualization")
    print("="*60)

    # Try local first
    print("\nAttempting local test first...")
    try:
        test_d3_sunburst(BASE_URLS["local"], "local")
    except requests.exceptions.ConnectionError:
        print("❌ Local server not running (port 8080)")
    except Exception as e:
        print(f"❌ Local test failed: {str(e)}")

    # Test production
    print("\nTesting production deployment...")
    try:
        test_d3_sunburst(BASE_URLS["production"], "production")
    except Exception as e:
        print(f"❌ Production test failed: {str(e)}")

    print("="*60)
    print("Test complete! Check the generated HTML file(s) in this directory.")
    print("="*60)
