#!/usr/bin/env python3
import requests
import re

# Test scatter
print("=" * 80)
print("SCATTER CHART")
print("=" * 80)
response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/correlation_analysis",
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

html = response.json()["content"]["element_3"]
# Find first few data points
match = re.search(r'"data":\s*\[(.*?)\]', html, re.DOTALL)
if match:
    data_str = match.group(1)[:300]
    print("Data points found:")
    print(data_str)
    print()
    # Check for label property
    if '"label"' in data_str or "'label'" in data_str:
        print("✅ Labels preserved in data points")
    else:
        print("❌ Labels NOT found in data points")
else:
    print("❌ Could not find data array")

print("\n" + "=" * 80)
print("BUBBLE CHART")
print("=" * 80)
response = requests.post(
    "http://localhost:8080/api/v1/analytics/L02/multidimensional_analysis",
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

html = response.json()["content"]["element_3"]
match = re.search(r'"data":\s*\[(.*?)\]', html, re.DOTALL)
if match:
    data_str = match.group(1)[:400]
    print("Data points found:")
    print(data_str)
    print()
    # Check for label property and varying radius
    if '"label"' in data_str or "'label'" in data_str:
        print("✅ Labels preserved in data points")
    else:
        print("❌ Labels NOT found in data points")

    # Extract r values
    r_values = re.findall(r'"r":\s*([\d.]+)', data_str)
    if len(set(r_values)) > 1:
        print(f"✅ Varying radius values: {r_values}")
    else:
        print(f"❌ All same radius: {r_values}")
else:
    print("❌ Could not find data array")
