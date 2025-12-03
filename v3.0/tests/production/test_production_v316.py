#!/usr/bin/env python3
"""Test Analytics v3.1.6 data transformation fixes in production."""

import requests
import re

PRODUCTION_URL = "https://analytics-v30-production.up.railway.app"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "=" * 80 + RESET)
print(BOLD + "Analytics v3.1.6 Production Data Transformation Validation" + RESET)
print(BOLD + f"Testing: {PRODUCTION_URL}" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

def check_labels_in_data(html, expected_labels):
    """Check if labels are preserved in data points"""
    for label in expected_labels:
        if label in html:
            return True
    return False

# Test 1: Scatter Chart
print(f"{BLUE}Test 1: Scatter Chart (correlation_analysis){RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "prod-v316-test",
        "slide_id": "scatter",
        "slide_number": 1,
        "narrative": "Test",
        "data": [
            {"label": "Jan - $20K spend", "value": 95},
            {"label": "Feb - $28K spend", "value": 124}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    html = response.json()["content"]["element_3"]
    has_labels = check_labels_in_data(html, ["Jan - $20K spend", "Feb - $28K spend"])

    if has_labels:
        print(f"{GREEN}✅ PASS - Labels preserved in data points{RESET}")
    else:
        print(f"{RED}❌ FAIL - Labels NOT found{RESET}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 2: Bubble Chart
print(f"{BLUE}Test 2: Bubble Chart (multidimensional_analysis){RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "prod-v316-test",
        "slide_id": "bubble",
        "slide_number": 2,
        "narrative": "Test",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    html = response.json()["content"]["element_3"]
    has_labels = check_labels_in_data(html, ["North America", "Europe", "APAC"])

    # Check for varying radius
    r_values = re.findall(r'"r":\s*([\d.]+)', html)
    varying_radius = len(set(r_values)) > 1

    if has_labels and varying_radius:
        print(f"{GREEN}✅ PASS - Labels preserved + varying radii: {r_values[:3]}{RESET}")
    elif has_labels:
        print(f"{RED}⚠️  PARTIAL - Labels OK but all same radius{RESET}")
    else:
        print(f"{RED}❌ FAIL - Labels NOT found{RESET}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 3: Radar Chart
print(f"{BLUE}Test 3: Radar Chart (multi_metric_comparison){RESET}")
response = requests.post(
    f"{PRODUCTION_URL}/api/v1/analytics/L02/multi_metric_comparison",
    json={
        "presentation_id": "prod-v316-test",
        "slide_id": "radar",
        "slide_number": 3,
        "narrative": "Test",
        "data": [
            {"label": "Revenue Growth", "value": 90},
            {"label": "Market Share", "value": 82},
            {"label": "Customer Satisfaction", "value": 85}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    html = response.json()["content"]["element_3"]

    # Check for populated datasets
    datasets_match = re.search(r'"datasets":\s*\[(.*?)\]', html, re.DOTALL)

    if datasets_match:
        datasets_str = datasets_match.group(1)
        # Check if datasets array has content (not just whitespace/empty)
        has_data = '"data":' in datasets_str and len(datasets_str.strip()) > 10

        if has_data:
            print(f"{GREEN}✅ PASS - Datasets array populated with data{RESET}")
        else:
            print(f"{RED}❌ FAIL - Datasets array empty{RESET}")
    else:
        print(f"{RED}❌ FAIL - Could not find datasets in response{RESET}")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()
print(BOLD + "=" * 80 + RESET)
print(BOLD + "v3.1.6 Production Validation Complete" + RESET)
print(BOLD + "=" * 80 + RESET)
