#!/usr/bin/env python3
"""Inspect v3.1.7 chart implementations."""

import requests
import re

LOCAL_URL = "http://localhost:8080"

print("=" * 80)
print("CORRELATION_ANALYSIS (scatter → line points)")
print("=" * 80)

response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "test",
        "slide_id": "test-scatter",
        "slide_number": 1,
        "narrative": "Test",
        "data": [
            {"label": "Jan - $20K", "value": 95},
            {"label": "Feb - $28K", "value": 124}
        ]
    }
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    print(f"Metadata chart_type: {metadata.get('chart_type')}")

    # Find Chart.js type in HTML
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    if type_match:
        print(f"Chart.js type: {type_match.group(1)}")

    # Check for showLine
    if "showLine" in html:
        showline_match = re.search(r'"showLine":\s*(true|false)', html)
        if showline_match:
            print(f"showLine: {showline_match.group(1)}")

    # Check for labels
    if "Jan - $20K" in html:
        print("✅ Labels present")
    else:
        print("❌ Labels NOT present")

    # Check for [object Object]
    if "[object Object]" in html:
        print("❌ [object Object] found!")
    else:
        print("✅ No [object Object]")

print("\n" + "=" * 80)
print("MULTIDIMENSIONAL_ANALYSIS (bubble → bar intensity)")
print("=" * 80)

response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "test",
        "slide_id": "test-bubble",
        "slide_number": 1,
        "narrative": "Test",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    }
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    print(f"Metadata chart_type: {metadata.get('chart_type')}")

    # Find Chart.js type in HTML
    type_match = re.search(r'"type":\s*"(\w+)"', html)
    if type_match:
        print(f"Chart.js type: {type_match.group(1)}")

    # Check for color intensity
    rgba_matches = re.findall(r'rgba\(255,\s*107,\s*107,\s*([\d.]+)\)', html)
    if rgba_matches:
        unique_opacities = list(set(rgba_matches))
        print(f"Color opacities found: {unique_opacities}")
        if len(unique_opacities) > 1:
            print("✅ Varying color intensity")
        else:
            print("⚠️  All same color intensity")

    # Check for labels
    if "North America" in html and "Europe" in html:
        print("✅ Labels present")
    else:
        print("❌ Labels NOT present")

    # Check for [object Object]
    if "[object Object]" in html:
        print("❌ [object Object] found!")
    else:
        print("✅ No [object Object]")
