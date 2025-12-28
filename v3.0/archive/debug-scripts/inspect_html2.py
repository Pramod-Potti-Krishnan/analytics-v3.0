#!/usr/bin/env python3
"""Quick script to find Chart.js config in HTML."""

import requests
import re

response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/market_share",
    json={
        "presentation_id": "test",
        "slide_id": "test-1",
        "slide_number": 1,
        "narrative": "Test",
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
    print("FIRST SCRIPT TAG (first 2000 chars):")
    print("=" * 80)
    print(script_matches[0][:2000])
    print("\n" + "=" * 80)

    # Look for type field
    type_match = re.search(r'type\s*:\s*["\'](\w+)["\']', script_matches[0])
    if type_match:
        print(f"\nFOUND Chart.js type: '{type_match.group(1)}'")
    else:
        print("\nCould NOT find 'type:' field in script")

        # Try alternate patterns
        print("\nSearching for alternative patterns...")
        alt_patterns = [
            r'"type"\s*:\s*"(\w+)"',
            r"'type'\s*:\s*'(\w+)'",
            r'type=\s*"(\w+)"',
            r'chart_type',
            r'chartType'
        ]
        for pattern in alt_patterns:
            matches = re.findall(pattern, script_matches[0], re.IGNORECASE)
            if matches:
                print(f"  - Found with pattern {pattern}: {matches}")
