#!/usr/bin/env python3
"""Quick verification that v3.1.3 deployment is successful."""

import requests

# Test one of the new analytics types
response = requests.post(
    "https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/category_ranking",
    json={
        "presentation_id": "test",
        "slide_id": "test-1",
        "slide_number": 1,
        "narrative": "Test category ranking",
        "data": [
            {"label": "A", "value": 100},
            {"label": "B", "value": 200},
            {"label": "C", "value": 150}
        ]
    },
    timeout=15
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print("✅ SUCCESS - New analytics type working!")
    print(f"  Has element_3: {'element_3' in result.get('content', {})}")
    print(f"  Has element_2: {'element_2' in result.get('content', {})}")
    print(f"  Chart type: {result.get('metadata', {}).get('chart_type')}")
else:
    error = response.json().get("error", {})
    print(f"❌ ERROR: {error.get('code')}")
    print(f"  Message: {error.get('message')}")
