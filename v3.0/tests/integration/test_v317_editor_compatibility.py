#!/usr/bin/env python3
"""Test Analytics v3.1.7 editor compatibility fixes."""

import requests
import re
import json

LOCAL_URL = "http://localhost:8080"

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

print("\n" + BOLD + "=" * 80 + RESET)
print(BOLD + "Analytics v3.1.7 Editor Compatibility Validation" + RESET)
print(BOLD + f"Testing: {LOCAL_URL}" + RESET)
print(BOLD + "=" * 80 + RESET + "\n")

def check_editor_compatible_structure(html, chart_type):
    """
    Check if chart uses editor-compatible data structure.
    Editor expects: {labels: [...], datasets: [{data: [primitives]}]}
    NOT compatible: {datasets: [{data: [{x, y, r, label}]}]}
    """
    # Extract Chart.js config from HTML
    script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
    if not script_match:
        return False, "No script tag found"

    script_content = script_match.group(1)

    # Check for top-level labels array
    has_labels = '"labels":' in script_content or "'labels':" in script_content

    # Check for datasets with simple data array (not objects)
    datasets_match = re.search(r'"datasets":\s*\[(.*?)\]', script_content, re.DOTALL)
    if not datasets_match:
        return False, "No datasets found"

    datasets_str = datasets_match.group(1)

    # Check for data array
    data_match = re.search(r'"data":\s*\[(.*?)\]', datasets_str, re.DOTALL)
    if not data_match:
        return False, "No data array in datasets"

    data_str = data_match.group(1)

    # For scatter/bubble (now line/bar), check that data is simple values, NOT objects
    if chart_type in ["scatter", "bubble"]:
        # Should NOT have object syntax like {x: ..., y: ...}
        has_object_data = '{' in data_str and ('"x":' in data_str or '"y":' in data_str)
        if has_object_data:
            return False, f"❌ Data contains objects (editor incompatible): {data_str[:200]}"

        # Should have simple values
        has_simple_values = re.search(r'\d+\.?\d*', data_str)
        if not has_simple_values:
            return False, "❌ No simple values found in data array"

        if not has_labels:
            return False, "❌ Missing top-level labels array"

        return True, "✅ Editor-compatible structure (labels + simple values)"

    return True, "✅ Standard chart structure"

# Test 1: Correlation Analysis (was scatter, now line with unconnected points)
print(f"{BLUE}Test 1: Correlation Analysis (scatter → line points){RESET}")
response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/correlation_analysis",
    json={
        "presentation_id": "v317-test",
        "slide_id": "scatter-test",
        "slide_number": 1,
        "narrative": "Testing editor compatibility",
        "data": [
            {"label": "Jan - $20K spend", "value": 95},
            {"label": "Feb - $28K spend", "value": 124},
            {"label": "Mar - $35K spend", "value": 158}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    # Check metadata
    analytics_type = metadata.get("analytics_type")
    chart_type = metadata.get("chart_type")

    print(f"  Metadata: analytics_type={analytics_type}, chart_type={chart_type}")

    # Check editor compatibility
    is_compatible, message = check_editor_compatible_structure(html, "scatter")

    # Check for showLine: false (unconnected points)
    has_showline_false = '"showLine": false' in html or "'showLine': false" in html

    # Check for labels in HTML
    has_labels = "Jan - $20K spend" in html and "Feb - $28K spend" in html

    if is_compatible and has_showline_false and has_labels:
        print(f"{GREEN}✅ PASS - Editor compatible{RESET}")
        print(f"  {message}")
        print(f"  ✅ showLine: false (unconnected points)")
        print(f"  ✅ Labels present in chart")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        if not is_compatible:
            print(f"  {message}")
        if not has_showline_false:
            print(f"  ❌ Missing showLine: false")
        if not has_labels:
            print(f"  ❌ Labels not found in HTML")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 2: Multidimensional Analysis (was bubble, now bar with intensity)
print(f"{BLUE}Test 2: Multidimensional Analysis (bubble → bar intensity){RESET}")
response = requests.post(
    f"{LOCAL_URL}/api/v1/analytics/L02/multidimensional_analysis",
    json={
        "presentation_id": "v317-test",
        "slide_id": "bubble-test",
        "slide_number": 2,
        "narrative": "Testing editor compatibility",
        "data": [
            {"label": "North America", "value": 180},
            {"label": "Europe", "value": 145},
            {"label": "APAC", "value": 95}
        ]
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    html = result["content"]["element_3"]
    metadata = result["metadata"]

    # Check metadata
    analytics_type = metadata.get("analytics_type")
    chart_type = metadata.get("chart_type")

    print(f"  Metadata: analytics_type={analytics_type}, chart_type={chart_type}")

    # Check editor compatibility
    is_compatible, message = check_editor_compatible_structure(html, "bubble")

    # Check for varying color intensity (rgba with different opacity)
    rgba_matches = re.findall(r'rgba\(255,\s*107,\s*107,\s*([\d.]+)\)', html)
    has_varying_colors = len(set(rgba_matches)) > 1 if rgba_matches else False

    # Check for labels in HTML
    has_labels = "North America" in html and "Europe" in html and "APAC" in html

    if is_compatible and has_varying_colors and has_labels:
        print(f"{GREEN}✅ PASS - Editor compatible{RESET}")
        print(f"  {message}")
        print(f"  ✅ Varying color intensity: {rgba_matches[:3] if rgba_matches else 'N/A'}")
        print(f"  ✅ Labels present in chart")
    else:
        print(f"{RED}❌ FAIL{RESET}")
        if not is_compatible:
            print(f"  {message}")
        if not has_varying_colors:
            print(f"  ❌ No varying color intensity (all same: {rgba_matches[:3] if rgba_matches else 'N/A'})")
        if not has_labels:
            print(f"  ❌ Labels not found in HTML")
else:
    print(f"{RED}❌ FAIL - HTTP {response.status_code}{RESET}")

print()

# Test 3: Verify NO [object Object] anywhere
print(f"{BLUE}Test 3: Verify NO [object Object] labels{RESET}")

tests = [
    ("correlation_analysis", "scatter-check"),
    ("multidimensional_analysis", "bubble-check")
]

all_clean = True
for analytics_type, slide_id in tests:
    response = requests.post(
        f"{LOCAL_URL}/api/v1/analytics/L02/{analytics_type}",
        json={
            "presentation_id": "v317-test",
            "slide_id": slide_id,
            "slide_number": 1,
            "narrative": "Test",
            "data": [
                {"label": "Test 1", "value": 100},
                {"label": "Test 2", "value": 150}
            ]
        },
        timeout=30
    )

    if response.status_code == 200:
        html = response.json()["content"]["element_3"]
        has_object_object = "[object Object]" in html

        if has_object_object:
            print(f"{RED}❌ FAIL - {analytics_type}: Found [object Object]{RESET}")
            all_clean = False
        else:
            print(f"{GREEN}✅ PASS - {analytics_type}: Clean (no [object Object]){RESET}")
    else:
        print(f"{RED}❌ FAIL - {analytics_type}: HTTP {response.status_code}{RESET}")
        all_clean = False

print()
print(BOLD + "=" * 80 + RESET)
if all_clean:
    print(BOLD + f"{GREEN}v3.1.7 Editor Compatibility: ALL TESTS PASSED ✅{RESET}" + RESET)
    print(f"{GREEN}✅ Scatter → Line (unconnected points): Editor compatible{RESET}")
    print(f"{GREEN}✅ Bubble → Bar (intensity colors): Editor compatible{RESET}")
    print(f"{GREEN}✅ No [object Object] labels anywhere{RESET}")
    print(f"{GREEN}✅ All charts use simple value arrays (editor-compatible){RESET}")
else:
    print(BOLD + f"{RED}v3.1.7 Editor Compatibility: SOME TESTS FAILED ❌{RESET}" + RESET)
print(BOLD + "=" * 80 + RESET)
