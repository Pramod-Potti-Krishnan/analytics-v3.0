"""Debug market share endpoint."""
import requests
import json

url = "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/market_share"
payload = {
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
        "enable_editor": False
    }
}

print(f"Testing: {url}")
response = requests.post(url, json=payload, timeout=30)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    result = response.json()

    element_3 = result.get("content", {}).get("element_3", "")
    element_2 = result.get("content", {}).get("element_2", "")
    metadata = result.get("metadata", {})

    print(f"element_3 ({len(element_3)} chars):")
    print(element_3)
    print(f"\nelement_2 ({len(element_2)} chars):")
    print(element_2)
    print(f"\nMetadata:")
    print(json.dumps(metadata, indent=2))
else:
    print(f"Error: {response.text}")
