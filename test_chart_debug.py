"""
Debug test to identify ApexCharts rendering issue.

Creates three test scenarios:
1. Charts WITH formatters (current failing behavior)
2. Charts WITHOUT formatters (to isolate if formatters are the problem)
3. Charts with console.log of complete config (for detailed debugging)
"""

import requests
import json
from apexcharts_generator import ApexChartsGenerator

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

def create_debug_presentation():
    """Create presentation with debug logging and formatter-free charts."""

    generator = ApexChartsGenerator(theme="professional")

    # Test 1: Line chart WITHOUT any formatters
    line_html_no_formatter = generator.generate_line_chart_debug(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125, 145, 178, 195],
            "format": "none"  # NO FORMATTER
        },
        height=720,
        chart_id="chart-line-no-formatter"
    )

    # Test 2: Bar chart WITHOUT any formatters
    bar_html_no_formatter = generator.generate_bar_chart_debug(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450, 380, 290, 220],
            "format": "none"  # NO FORMATTER
        },
        height=720,
        chart_id="chart-bar-no-formatter"
    )

    # Test 3: Donut chart (working - for comparison)
    donut_html = generator.generate_donut_chart(
        data={
            "labels": ["Enterprise", "SMB", "Startup"],
            "values": [45, 30, 25],
            "format": "percentage",
            "total_label": "Total"
        },
        height=720,
        chart_id="chart-donut-working"
    )

    # Test 4: Line chart WITH formatter (to confirm it fails)
    line_html_with_formatter = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=720,
        chart_id="chart-line-with-formatter"
    )

    # Test 5: Bar chart WITH formatter (to confirm it fails)
    bar_html_with_formatter = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450000, 380000, 290000, 220000],
            "format": "currency"
        },
        height=720,
        chart_id="chart-bar-with-formatter"
    )

    # Create presentation data
    presentation_data = {
        "title": "ApexCharts Debug Test - Formatter Investigation",
        "slides": [
            {
                "layout": "L29",
                "content": {
                    "slide_title": "ApexCharts Debug Test",
                    "element_1": "Testing formatters vs no formatters",
                    "element_2": "This presentation tests whether formatters are causing the rendering issue",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Test 1: Line Chart WITHOUT Formatter",
                    "element_1": "No formatter functions - raw values displayed",
                    "element_3": line_html_no_formatter,
                    "element_2": "This chart has NO formatter. If it renders, the problem is formatters. If it doesn't render, the problem is elsewhere.",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Test 2: Bar Chart WITHOUT Formatter",
                    "element_1": "No formatter functions - raw values displayed",
                    "element_3": bar_html_no_formatter,
                    "element_2": "This chart has NO formatter. If it renders, the problem is formatters. If it doesn't render, the problem is elsewhere.",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Test 3: Donut Chart (Working Baseline)",
                    "element_1": "With percentage formatter - KNOWN TO WORK",
                    "element_3": donut_html,
                    "element_2": "This chart has the percentage formatter and is known to work. Use this as a baseline for comparison.",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Test 4: Line Chart WITH Formatter",
                    "element_1": "Currency formatter - EXPECTED TO FAIL",
                    "element_3": line_html_with_formatter,
                    "element_2": "This chart has the currency formatter. Expected to fail based on previous tests. Compare console logs with Test 1.",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Test 5: Bar Chart WITH Formatter",
                    "element_1": "Currency formatter - EXPECTED TO FAIL",
                    "element_3": bar_html_with_formatter,
                    "element_2": "This chart has the currency formatter. Expected to fail based on previous tests. Compare console logs with Test 2.",
                    "presentation_name": "Debug Test",
                    "company_logo": "🔍"
                }
            }
        ]
    }

    # Save debug data
    with open('debug_slides_data.json', 'w') as f:
        json.dump(presentation_data, f, indent=2)

    # Send to Layout Builder
    response = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=presentation_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        result = response.json()
        presentation_id = result.get('id')
        presentation_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}"

        print("✅ Debug presentation created successfully!")
        print(f"   URL: {presentation_url}")
        print(f"   ID: {presentation_id}")
        print("\n📋 Test Scenarios:")
        print("   Slide 2: Line chart WITHOUT formatter")
        print("   Slide 3: Bar chart WITHOUT formatter")
        print("   Slide 4: Donut chart WITH formatter (working baseline)")
        print("   Slide 5: Line chart WITH formatter (expected to fail)")
        print("   Slide 6: Bar chart WITH formatter (expected to fail)")
        print("\n🔍 What to check:")
        print("   1. Do slides 2 & 3 render? → Problem is formatters")
        print("   2. Do slides 2 & 3 fail too? → Problem is chart type config")
        print("   3. Compare console logs between working and failing charts")
        print("   4. Look for ApexCharts config output in console")

        return presentation_id, presentation_url
    else:
        print(f"❌ Failed to create presentation: {response.status_code}")
        print(f"   Response: {response.text}")
        return None, None


if __name__ == "__main__":
    create_debug_presentation()
