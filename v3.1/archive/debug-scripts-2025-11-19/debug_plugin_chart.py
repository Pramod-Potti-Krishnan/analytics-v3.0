#!/usr/bin/env python3
"""Debug plugin chart HTML structure."""

import requests

BASE_URL = "http://localhost:8080"

# Test treemap
response = requests.post(
    f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
    json={
        "presentation_id": "debug",
        "slide_id": "slide-treemap",
        "slide_number": 1,
        "narrative": "Debug",
        "chart_type": "treemap",
        "data": [
            {"label": "Enterprise", "value": 450},
            {"label": "SMB", "value": 200}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result.get("content", {}).get("element_3", "")

    # Save to file for inspection
    with open("debug_treemap.html", "w") as f:
        f.write(html)

    print(f"HTML saved to debug_treemap.html ({len(html)} bytes)")
    print("\nFirst 500 characters:")
    print(html[:500])
    print("\n" + "="*70)
    print("Looking for script tags:")
    if "<script src=" in html:
        print("✅ Has external script tag")
        # Extract script tags
        import re
        scripts = re.findall(r'<script src="([^"]+)"', html)
        for script in scripts:
            print(f"  - {script}")
    else:
        print("❌ No external script tags found")

    if "<script>" in html or "new Chart" in html:
        print("✅ Has inline script")
    else:
        print("❌ No inline script found")
else:
    print(f"❌ Failed: {response.status_code}")
