#!/usr/bin/env python3
"""Inspect scatter chart output to debug type field issue."""

import requests
import re

response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "test",
        "slide_id": "test-scatter",
        "slide_number": 1,
        "narrative": "Test scatter",
        "data": [{"label": "A", "value": 100}, {"label": "B", "value": 150}]
    }
)

data = response.json()
html = data.get("content", {}).get("element_3", "")

# Find script tags
script_matches = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
print(f"Found {len(script_matches)} script tags\n")

if script_matches:
    print("=" * 80)
    print("SCATTER CHART SCRIPT (first 1500 chars):")
    print("=" * 80)
    print(script_matches[0][:1500])
    print("\n" + "=" * 80)

    # Look for type field
    type_match = re.search(r'["\']?type["\']?\s*:\s*["\'](\w+)["\']', script_matches[0])
    if type_match:
        print(f"\nFOUND Chart.js type: '{type_match.group(1)}'")
    else:
        print("\n❌ Could NOT find 'type:' field in script")

        # Check if it's using a different chart library
        if "new Chart(" in script_matches[0]:
            print("✓ Uses Chart.js")
        if "Plotly" in script_matches[0]:
            print("⚠️  Uses Plotly (not Chart.js!)")
        if "ApexCharts" in script_matches[0]:
            print("⚠️  Uses ApexCharts (not Chart.js!)")
