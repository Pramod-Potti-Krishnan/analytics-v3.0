#!/usr/bin/env python3
"""Simulate director calling scatter/bubble charts to diagnose blank chart issue."""

import requests
import json
import re

PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

print("\n" + "="*80)
print("DIRECTOR SIMULATION - Diagnosing Blank Scatter Chart")
print("="*80 + "\n")

# Test 1: Simple scatter data (like our tests - this should work)
print("Test 1: Simple Scatter Data (3 points)")
print("-" * 80)
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "director-sim",
        "slide_id": "scatter-simple",
        "slide_number": 1,
        "narrative": "Simple test",
        "data": [
            {"label": "Point 1", "value": 100},
            {"label": "Point 2", "value": 150},
            {"label": "Point 3", "value": 200}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Extract chart data from HTML
    data_match = re.search(r'"data":\s*(\{[^}]+\}|\[[^\]]+\])', html)
    if data_match:
        print(f"✓ Chart data found in HTML")
        # Look for x, y coordinates
        x_coords = re.findall(r'"x":\s*(\d+)', html)
        y_coords = re.findall(r'"y":\s*(\d+\.?\d*)', html)
        print(f"  X coordinates: {x_coords}")
        print(f"  Y coordinates: {y_coords}")

    # Check axes configuration
    x_axis_match = re.search(r'"x":\s*\{[^}]*"min":\s*(\d+)[^}]*"max":\s*(\d+)', html)
    y_axis_match = re.search(r'"y":\s*\{[^}]*"min":\s*(\d+\.?\d*)[^}]*"max":\s*(\d+\.?\d*)', html)

    if x_axis_match:
        print(f"  X-axis range: {x_axis_match.group(1)} to {x_axis_match.group(2)}")
    if y_axis_match:
        print(f"  Y-axis range: {y_axis_match.group(1)} to {y_axis_match.group(2)}")

    print(f"✓ Response OK, HTML length: {len(html)} chars")
else:
    print(f"✗ FAILED: HTTP {response.status_code}")

print()

# Test 2: Large scatter data (like director - 12 points)
print("Test 2: Director-like Scatter Data (12 points)")
print("-" * 80)
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "director-sim",
        "slide_id": "scatter-12points",
        "slide_number": 2,
        "narrative": "Simulating director's 12-point scatter",
        "data": [
            {"label": f"Month {i+1}", "value": 50 + (i * 30)}
            for i in range(12)
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Extract all data points
    x_coords = [int(x) for x in re.findall(r'"x":\s*(\d+)', html)]
    y_coords = [float(y) for y in re.findall(r'"y":\s*(\d+\.?\d*)', html)]

    print(f"✓ Found {len(x_coords)} data points")
    print(f"  X range: {min(x_coords) if x_coords else 'N/A'} to {max(x_coords) if x_coords else 'N/A'}")
    print(f"  Y range: {min(y_coords) if y_coords else 'N/A'} to {max(y_coords) if y_coords else 'N/A'}")

    # Check for axes configuration
    x_axis_match = re.search(r'"x":\s*\{[^}]*"display":\s*(true|false)', html)
    y_axis_match = re.search(r'"y":\s*\{[^}]*"display":\s*(true|false)', html)

    print(f"  X-axis display: {x_axis_match.group(1) if x_axis_match else 'unknown'}")
    print(f"  Y-axis display: {y_axis_match.group(1) if y_axis_match else 'unknown'}")

    # Check point styling
    point_style_match = re.search(r'"pointStyle":\s*"(\w+)"', html)
    point_radius_match = re.search(r'"pointRadius":\s*(\d+)', html)

    print(f"  Point style: {point_style_match.group(1) if point_style_match else 'unknown'}")
    print(f"  Point radius: {point_radius_match.group(1) if point_radius_match else 'unknown'}px")

    print(f"✓ Response OK, HTML length: {len(html)} chars")
else:
    print(f"✗ FAILED: HTTP {response.status_code}")

print()

# Test 3: Extract actual chart config for inspection
print("Test 3: Extract Full Chart Config")
print("-" * 80)
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "director-sim",
        "slide_id": "scatter-config-check",
        "slide_number": 3,
        "narrative": "Config inspection",
        "data": [
            {"label": "Test 1", "value": 100},
            {"label": "Test 2", "value": 200}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]

    # Try to extract the entire datasets array
    datasets_match = re.search(r'"datasets":\s*\[(\{[^\]]+\})\]', html, re.DOTALL)
    if datasets_match:
        print("Dataset configuration:")
        dataset_str = datasets_match.group(1)
        # Pretty print key fields
        for field in ["label", "data", "pointStyle", "pointRadius", "backgroundColor"]:
            field_match = re.search(f'"{field}":\s*([^,}}]+)', dataset_str)
            if field_match:
                value = field_match.group(1).strip()
                print(f"  {field}: {value[:100]}...")

    # Save full HTML for inspection
    with open("scatter_chart_debug.html", "w") as f:
        f.write(html)
    print(f"\n✓ Full HTML saved to: scatter_chart_debug.html")
    print(f"  Open this file in a browser to see if the chart renders")
else:
    print(f"✗ FAILED: HTTP {response.status_code}")

print("\n" + "="*80)
print("DIAGNOSIS COMPLETE")
print("="*80 + "\n")
