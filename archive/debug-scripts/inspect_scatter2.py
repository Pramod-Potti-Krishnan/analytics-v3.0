#!/usr/bin/env python3
"""Inspect full scatter chart response."""

import requests
import json

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

print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()
    html = data.get("content", {}).get("element_3", "")

    print("=" * 80)
    print(f"HTML length: {len(html)} characters")
    print("=" * 80)
    print("\nFirst 1000 characters:")
    print(html[:1000])
    print("\n" + "=" * 80)

    if "PlotlyElement" in html or "Plotly" in html:
        print("\n⚠️  SCATTER uses Plotly.js (not Chart.js)")
    elif "new Chart(" in html:
        print("\n✓ Uses Chart.js")
    else:
        print("\n❓ Unknown chart library or no chart")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)
