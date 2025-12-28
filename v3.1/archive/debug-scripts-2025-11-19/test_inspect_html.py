#!/usr/bin/env python3
"""Quick test to inspect HTML output from chart generation."""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_and_save(chart_type, data):
    """Test chart and save HTML for inspection."""
    url = f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time"
    payload = {
        "presentation_id": "test-inspect",
        "slide_id": f"slide-{chart_type}",
        "slide_number": 1,
        "narrative": f"Test {chart_type}",
        "chart_type": chart_type,
        "data": data
    }

    response = requests.post(url, json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        html = result.get("content", {}).get("element_3", "")

        # Save to file
        with open(f"{chart_type}_output.html", "w") as f:
            f.write(html)

        print(f"\n{chart_type}:")
        print(f"  Size: {len(html):,} bytes")
        print(f"  Saved to: {chart_type}_output.html")

        # Check for specific indicators
        if chart_type == "treemap":
            has_label_in_raw = "raw.label" in html
            has_color_in_raw = "raw.color" in html
            print(f"  Has 'raw.label': {has_label_in_raw}")
            print(f"  Has 'raw.color': {has_color_in_raw}")
        elif chart_type in ["area_stacked", "bar_stacked"]:
            has_item_0 = "Item 0" in html
            print(f"  Has 'Item 0' (bad): {has_item_0}")
        elif chart_type == "bar_grouped":
            has_datasets_error = "requires 'datasets'" in html
            print(f"  Has datasets error: {has_datasets_error}")

# Test treemap
print("Testing treemap...")
test_and_save("treemap", [
    {"label": "Enterprise - North America", "value": 450},
    {"label": "SMB - Europe", "value": 200}
])

# Test area_stacked
print("\nTesting area_stacked...")
test_and_save("area_stacked", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "Product A", "data": [50, 60, 70]},
        {"label": "Product B", "data": [30, 40, 50]}
    ]
}])

# Test bar_stacked
print("\nTesting bar_stacked...")
test_and_save("bar_stacked", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "Revenue", "data": [100, 120, 140]},
        {"label": "Costs", "data": [60, 70, 80]}
    ]
}])

# Test bar_grouped
print("\nTesting bar_grouped...")
test_and_save("bar_grouped", [{
    "labels": ["Q1", "Q2", "Q3"],
    "datasets": [
        {"label": "2023", "data": [100, 120, 140]},
        {"label": "2024", "data": [150, 180, 210]}
    ]
}])

print("\n✅ HTML files saved. Inspect them to verify fixes.")
