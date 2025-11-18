#!/usr/bin/env python3
"""Quick script to inspect actual HTML format from API response."""

import requests
import json

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

# Print first 1000 characters to see the structure
print("=" * 80)
print("FIRST 1000 CHARACTERS OF HTML:")
print("=" * 80)
print(html[:1000])
print("\n" + "=" * 80)

# Look for "type" in the HTML
import re
type_matches = re.findall(r'.{50}type.{50}', html, re.IGNORECASE)
print(f"\nFOUND {len(type_matches)} instances of 'type' in HTML:")
print("=" * 80)
for i, match in enumerate(type_matches[:5], 1):
    print(f"{i}. ...{match}...")
