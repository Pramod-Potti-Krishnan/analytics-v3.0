"""Quick test of L02 endpoint on Railway."""
import requests
import json

url = "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time"
payload = {
    "presentation_id": "test-123",
    "slide_id": "slide-1",
    "slide_number": 1,
    "narrative": "Show revenue growth",
    "data": [
        {"label": "Q1", "value": 100},
        {"label": "Q2", "value": 150}
    ],
    "context": {
        "theme": "professional",
        "slide_title": "Revenue"
    }
}

print(f"Testing: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

response = requests.post(url, json=payload, timeout=30)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"\nResponse Keys: {list(result.keys())}")

    if "content" in result:
        print(f"\nContent Keys: {list(result['content'].keys())}")

        element_3 = result["content"].get("element_3", "")
        element_2 = result["content"].get("element_2", "")

        print(f"\nelement_3 length: {len(element_3)} chars")
        print(f"element_3 preview: {element_3[:200]}...")

        print(f"\nelement_2 length: {len(element_2)} chars")
        print(f"element_2 preview: {element_2[:200]}...")

        # Check for Chart.js markers
        has_canvas = "<canvas" in element_3
        has_chartjs = "Chart.js" in element_3 or "chart-" in element_3

        print(f"\nChart.js Indicators:")
        print(f"  - Has <canvas>: {has_canvas}")
        print(f"  - Has Chart.js markers: {has_chartjs}")

    if "metadata" in result:
        print(f"\nMetadata: {json.dumps(result['metadata'], indent=2)}")
else:
    print(f"Error: {response.text}")
