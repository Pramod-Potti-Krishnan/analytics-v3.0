#!/usr/bin/env python3
"""
Test v3.1.6 Data Transformation Fixes
Tests the 3 bugs reported by Director team:
1. Scatter chart - label preservation
2. Bubble chart - label preservation + varying radius
3. Radar chart - datasets array population
"""

import requests
import json
import re

BASE_URL = "http://localhost:8080"

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "=" * 80 + RESET)
print(BOLD + "Analytics v3.1.6 - Data Transformation Fix Validation" + RESET)
print(BOLD + f"Testing: {BASE_URL}" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

def extract_chart_config(html):
    """Extract Chart.js config from HTML"""
    match = re.search(r'const chartConfig = ({.*?});', html, re.DOTALL)
    if match:
        config_str = match.group(1)
        # Use eval with limited scope (safe for our controlled JSON)
        try:
            return eval(config_str)
        except:
            return None
    return None

# Test 1: Scatter Chart - Label Preservation
print(f"{BLUE}Test 1: Scatter Chart (correlation_analysis){RESET}")
print(f"Bug: Labels lost during x-y transformation")
print(f"Fix: Preserve labels as custom property in data points\n")

response = requests.post(
    f"{BASE_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "test-v316",
        "slide_id": "test-scatter",
        "slide_number": 1,
        "narrative": "Spending vs customer acquisition correlation",
        "data": [
            {"label": "Jan - $20K spend", "value": 95},
            {"label": "Feb - $28K spend", "value": 124},
            {"label": "Mar - $35K spend", "value": 158}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    html = data.get("content", {}).get("element_3", "")
    config = extract_chart_config(html)

    if config and "datasets" in config["data"]:
        dataset = config["data"]["datasets"][0]
        data_points = dataset.get("data", [])

        # Check if labels are preserved
        has_labels = all("label" in point for point in data_points)

        if has_labels:
            print(f"{GREEN}✅ PASS{RESET}")
            print(f"   Labels preserved: {[p['label'] for p in data_points[:3]]}")
            print(f"   Data points: {data_points[:3]}")
        else:
            print(f"{RED}❌ FAIL{RESET}")
            print(f"   Labels NOT preserved in data points")
            print(f"   Data points: {data_points[:3]}")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"   Could not extract chart config")
else:
    print(f"{RED}❌ FAIL{RESET}")
    print(f"   HTTP {response.status_code}")

print()

# Test 2: Bubble Chart - Label Preservation + Varying Radius
print(f"{BLUE}Test 2: Bubble Chart (multidimensional_analysis){RESET}")
print(f"Bug: Labels lost + all bubbles same size (r: 10)")
print(f"Fix: Preserve labels + scale radius based on value\n")

response = requests.post(
    f"{BASE_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "test-v316",
        "slide_id": "test-bubble",
        "slide_number": 2,
        "narrative": "Regional performance analysis",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    html = data.get("content", {}).get("element_3", "")
    config = extract_chart_config(html)

    if config and "datasets" in config["data"]:
        dataset = config["data"]["datasets"][0]
        data_points = dataset.get("data", [])

        # Check if labels are preserved
        has_labels = all("label" in point for point in data_points)

        # Check if radius varies
        radii = [point.get("r", 0) for point in data_points]
        varying_radius = len(set(radii)) > 1  # More than one unique radius value

        if has_labels and varying_radius:
            print(f"{GREEN}✅ PASS{RESET}")
            print(f"   Labels preserved: {[p['label'] for p in data_points]}")
            print(f"   Varying radii: {radii} (unique values: {len(set(radii))})")
            print(f"   Sample data point: {data_points[0]}")
        else:
            print(f"{RED}❌ PARTIAL or FAIL{RESET}")
            if not has_labels:
                print(f"   ❌ Labels NOT preserved")
            else:
                print(f"   ✅ Labels preserved")
            if not varying_radius:
                print(f"   ❌ All bubbles same size: {radii}")
            else:
                print(f"   ✅ Varying radii: {radii}")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"   Could not extract chart config")
else:
    print(f"{RED}❌ FAIL{RESET}")
    print(f"   HTTP {response.status_code}")

print()

# Test 3: Radar Chart - Datasets Array Population
print(f"{BLUE}Test 3: Radar Chart (multi_metric_comparison){RESET}")
print(f"Bug: datasets array is empty []")
print(f"Fix: Populate datasets array with label and data values\n")

response = requests.post(
    f"{BASE_URL}/api/v1/analytics/L02/multi_metric_comparison",
    json={
        "presentation_id": "test-v316",
        "slide_id": "test-radar",
        "slide_number": 3,
        "narrative": "Multi-metric performance comparison",
        "data": [
            {"label": "Revenue Growth", "value": 90},
            {"label": "Market Share", "value": 82},
            {"label": "Customer Satisfaction", "value": 85},
            {"label": "Operational Efficiency", "value": 68}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    html = data.get("content", {}).get("element_3", "")
    config = extract_chart_config(html)

    if config and "datasets" in config["data"]:
        datasets = config["data"]["datasets"]
        labels = config["data"].get("labels", [])

        # Check if datasets array is populated
        has_datasets = len(datasets) > 0
        has_data = has_datasets and len(datasets[0].get("data", [])) > 0

        if has_datasets and has_data:
            dataset = datasets[0]
            print(f"{GREEN}✅ PASS{RESET}")
            print(f"   Datasets array populated: {len(datasets)} dataset(s)")
            print(f"   Labels: {labels}")
            print(f"   Data values: {dataset.get('data', [])}")
            print(f"   Dataset label: {dataset.get('label', 'N/A')}")
        else:
            print(f"{RED}❌ FAIL{RESET}")
            if not has_datasets:
                print(f"   ❌ Datasets array is EMPTY: {datasets}")
            elif not has_data:
                print(f"   ❌ Dataset exists but data array is EMPTY")
            print(f"   Labels: {labels}")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        print(f"   Could not extract chart config or datasets missing")
else:
    print(f"{RED}❌ FAIL{RESET}")
    print(f"   HTTP {response.status_code}")

print()
print(BOLD + "=" * 80 + RESET)
print(BOLD + "v3.1.6 Data Transformation Validation Complete" + RESET)
print(BOLD + "=" * 80 + RESET)
