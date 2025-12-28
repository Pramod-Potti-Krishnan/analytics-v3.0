#!/usr/bin/env python3
import requests
import re

response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/multi_metric_comparison",
    json={
        "presentation_id": "test-v316",
        "slide_id": "test-radar",
        "slide_number": 3,
        "narrative": "Test radar",
        "data": [
            {"label": "Revenue Growth", "value": 90},
            {"label": "Market Share", "value": 82},
            {"label": "Customer Satisfaction", "value": 85}
        ]
    }
)

data = response.json()
html = data.get("content", {}).get("element_3", "")

# Find datasets in HTML
script_matches = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
if script_matches:
    script = script_matches[0]

    # Look for datasets array
    datasets_match = re.search(r'"datasets":\s*(\[.*?\])', script, re.DOTALL)
    if datasets_match:
        print("Found datasets array:")
        print(datasets_match.group(1)[:500])
    else:
        print("No datasets found, showing script excerpt:")
        print(script[:1000])
else:
    print("No script tags found")
