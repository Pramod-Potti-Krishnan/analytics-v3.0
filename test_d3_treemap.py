"""Test D3.js treemap chart - POC for D3 integration."""
import requests
import json
import os
from datetime import datetime

# Test both local and production
BASE_URLS = {
    "local": "http://localhost:8080",
    "production": "https://analytics-v30-production.up.railway.app"
}

def test_d3_treemap(base_url: str, env_name: str):
    """Test d3_treemap chart type."""
    print(f"\n{'='*60}")
    print(f"Testing D3 Treemap on {env_name.upper()}")
    print(f"{'='*60}\n")

    url = f"{base_url}/api/v1/analytics/L02/market_share"

    payload = {
        "presentation_id": "test-d3-001",
        "slide_id": "slide-d3-1",
        "slide_number": 1,
        "narrative": "Show budget allocation across departments",
        "chart_type": "d3_treemap",  # Explicitly request D3 treemap
        "data": [
            {"label": "Engineering", "value": 450000},
            {"label": "Sales", "value": 320000},
            {"label": "Marketing", "value": 180000},
            {"label": "Operations", "value": 120000},
            {"label": "HR", "value": 80000},
            {"label": "Finance", "value": 60000}
        ],
        "context": {
            "theme": "professional",
            "slide_title": "Budget Allocation",
            "subtitle": "FY 2024 - By Department"
        }
    }

    print(f"URL: {url}")
    print(f"Chart Type: d3_treemap")
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

                # D3.js specific checks
                has_d3_cdn = "cdn.jsdelivr.net/npm/d3@7" in element_3
                has_svg = "svg" in element_3.lower()
                has_treemap = "treemap" in element_3.lower()
                has_d3_hierarchy = "d3.hierarchy" in element_3
                has_chart_id = "d3-treemap" in element_3

                print(f"D3.js Indicators:")
                print(f"  ✓ Has D3.js v7 CDN: {has_d3_cdn}")
                print(f"  ✓ Has SVG rendering: {has_svg}")
                print(f"  ✓ Has treemap reference: {has_treemap}")
                print(f"  ✓ Has d3.hierarchy(): {has_d3_hierarchy}")
                print(f"  ✓ Has d3-treemap ID: {has_chart_id}\n")

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
                filename = f"test_d3_treemap_{env_name}_{timestamp}.html"

                # Create complete HTML page
                full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D3 Treemap Test - {env_name}</title>
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
        .chart-section {{
            margin: 20px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .metadata {{
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-left: 4px solid #007bff;
        }}
        pre {{
            background: #263238;
            color: #aed581;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>D3 Treemap Chart Test ({env_name.upper()})</h1>

        <div class="metadata">
            <h3>Test Information</h3>
            <p><strong>Environment:</strong> {env_name}</p>
            <p><strong>Chart Type:</strong> d3_treemap</p>
            <p><strong>Data Points:</strong> {len(payload['data'])}</p>
            <p><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <div class="chart-section">
            <h2>{content.get('slide_title', 'Chart Title')}</h2>
            <h3>{content.get('element_1', 'Subtitle')}</h3>
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

                with open(filename, 'w') as f:
                    f.write(full_html)

                print(f"📄 HTML saved to: {filename}")
                print(f"   Open this file in a browser to see the D3 treemap chart\n")

                # Validation summary
                all_checks = all([has_d3_cdn, has_svg, has_treemap, has_d3_hierarchy, has_chart_id])
                if all_checks:
                    print(f"✅ ALL CHECKS PASSED - D3 treemap implementation validated!")
                else:
                    print(f"⚠️  SOME CHECKS FAILED - Review the HTML output")

            else:
                print(f"❌ ERROR - No 'content' in response")

        else:
            print(f"❌ ERROR - Status {response.status_code}")
            print(f"Response: {response.text[:500]}...")

    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT - Request took longer than 30 seconds")
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Could not connect to {env_name}")
    except Exception as e:
        print(f"❌ EXCEPTION - {type(e).__name__}: {str(e)}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("D3.js TREEMAP CHART TEST")
    print("Testing D3.js integration as proof of concept")
    print("="*60)

    # Test local first (if available)
    print("\nAttempting local test first...")
    try:
        test_d3_treemap(BASE_URLS["local"], "local")
    except:
        print("⚠️  Local server not running, skipping local test\n")

    # Always test production
    print("\nTesting production deployment...")
    test_d3_treemap(BASE_URLS["production"], "production")

    print("\n" + "="*60)
    print("Test complete! Check the generated HTML file(s) in this directory.")
    print("="*60 + "\n")
