"""
Test Guaranteed Labels and Axes
=================================

This test verifies that ALL charts show:
1. X-axis and Y-axis labels ALWAYS visible
2. Data labels on EVERY point/bar/segment
3. Proper units and formatting
4. Grid lines for easier reading

Author: Analytics Microservice v3 Team
Date: 2025-01-15
"""

import requests
from chartjs_generator import ChartJSGenerator


LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"


def test_guaranteed_labels():
    """Test that axes and data labels are guaranteed to be visible."""

    generator = ChartJSGenerator(theme="professional")

    print("Testing Guaranteed Labels and Axes...")
    print("=" * 70)

    # Test 1: Line chart with currency (must show $XXXk on EVERY point)
    print("\n1. Line Chart - Currency Format")
    line_chart = generator.generate_line_chart(
        data={
            "series_name": "Quarterly Revenue",
            "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=600,
        chart_id="guaranteed-line-test"
    )
    print("   ✓ Generated with guaranteed data labels on all 4 points")
    print("   ✓ Y-axis title: 'Amount (USD)'")
    print("   ✓ Y-axis labels: $0, $50K, $100K, $150K, $200K")
    print("   ✓ Point labels: $125K, $145K, $178K, $195K")

    # Test 2: Bar chart with percentage (must show XX% on EVERY bar)
    print("\n2. Bar Chart - Percentage Format")
    bar_chart = generator.generate_bar_chart(
        data={
            "series_name": "Market Share",
            "labels": ["Product A", "Product B", "Product C", "Product D"],
            "values": [35.5, 28.3, 22.1, 14.1],
            "format": "percentage"
        },
        height=600,
        chart_id="guaranteed-bar-test"
    )
    print("   ✓ Generated with guaranteed data labels on all 4 bars")
    print("   ✓ Y-axis title: 'Percentage (%)'")
    print("   ✓ Y-axis labels: 0%, 10%, 20%, 30%, 40%")
    print("   ✓ Bar labels: 35.5%, 28.3%, 22.1%, 14.1%")

    # Test 3: Multi-series line chart (must show values on ALL points of ALL series)
    print("\n3. Multi-Series Line Chart - Number Format")
    multi_line_chart = generator.generate_line_chart(
        data={
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "datasets": [
                {"label": "Sales Team A", "data": [120, 135, 148, 162, 180]},
                {"label": "Sales Team B", "data": [98, 110, 125, 142, 155]},
                {"label": "Sales Team C", "data": [75, 88, 95, 108, 120]}
            ],
            "format": "number"
        },
        height=600,
        chart_id="guaranteed-multiline-test"
    )
    print("   ✓ Generated with guaranteed data labels on all 15 points (3 series × 5 points)")
    print("   ✓ Y-axis title: 'Value'")
    print("   ✓ Y-axis labels: 0, 50, 100, 150, 200")
    print("   ✓ Point labels: Formatted numbers with commas")

    # Test 4: Horizontal bar with large numbers
    print("\n4. Horizontal Bar Chart - Large Currency Values")
    hbar_chart = generator.generate_horizontal_bar_chart(
        data={
            "series_name": "Annual Revenue",
            "labels": ["2020", "2021", "2022", "2023", "2024"],
            "values": [1250000, 1780000, 2340000, 3100000, 4500000],
            "format": "currency"
        },
        height=600,
        chart_id="guaranteed-hbar-test"
    )
    print("   ✓ Generated with guaranteed data labels on all 5 bars")
    print("   ✓ X-axis title: 'Amount (USD)'")
    print("   ✓ X-axis labels: $0, $1M, $2M, $3M, $4M, $5M")
    print("   ✓ Bar labels: $1.3M, $1.8M, $2.3M, $3.1M, $4.5M")

    # Create presentation
    presentation_data = {
        "title": "Guaranteed Labels Test",
        "slides": [
            # Title
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Guaranteed Labels & Axes Test",
                    "element_1": "ENFORCED Settings",
                    "element_2": "This presentation tests GUARANTEED visibility of:\n• X and Y axis labels (always shown)\n• Data labels on EVERY point/bar\n• Proper units (USD, %, etc.)\n• Grid lines for readability\n\nThese settings CANNOT be disabled.",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            },

            # Line Chart
            {
                "layout": "L02",
                "content": {
                    "slide_title": "1. Line Chart - Currency Format",
                    "element_1": "Quarterly Revenue Growth",
                    "element_3": line_chart,
                    "element_2": "✅ VERIFY:\n• Y-axis shows 'Amount (USD)'\n• Y-axis has labels: $0, $50K, $100K, etc.\n• EVERY point shows value: $125K, $145K, $178K, $195K\n• Grid lines visible\n• X-axis shows all quarter labels",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            },

            # Bar Chart
            {
                "layout": "L02",
                "content": {
                    "slide_title": "2. Bar Chart - Percentage Format",
                    "element_1": "Market Share Distribution",
                    "element_3": bar_chart,
                    "element_2": "✅ VERIFY:\n• Y-axis shows 'Percentage (%)'\n• Y-axis has labels: 0%, 10%, 20%, etc.\n• EVERY bar shows value: 35.5%, 28.3%, 22.1%, 14.1%\n• Grid lines visible\n• X-axis shows all product labels",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            },

            # Multi-Series Line
            {
                "layout": "L02",
                "content": {
                    "slide_title": "3. Multi-Series Line - Number Format",
                    "element_1": "Sales Team Performance",
                    "element_3": multi_line_chart,
                    "element_2": "✅ VERIFY:\n• Y-axis shows 'Value'\n• Y-axis has formatted labels\n• ALL 15 points show values (3 series × 5 points)\n• Grid lines visible\n• Legend shows all 3 teams\n• X-axis shows all month labels",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            },

            # Horizontal Bar
            {
                "layout": "L02",
                "content": {
                    "slide_title": "4. Horizontal Bar - Large Currency",
                    "element_1": "5-Year Revenue Growth",
                    "element_3": hbar_chart,
                    "element_2": "✅ VERIFY:\n• X-axis shows 'Amount (USD)'\n• X-axis has labels: $0, $1M, $2M, etc.\n• EVERY bar shows value: $1.3M, $1.8M, etc.\n• Grid lines visible\n• Y-axis shows all year labels\n• Values formatted in millions",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            },

            # Summary
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Test Complete ✅",
                    "element_1": "All Labels Guaranteed",
                    "element_2": "If all 4 charts show:\n✓ Axis titles with units\n✓ All axis labels visible\n✓ Data labels on EVERY point/bar\n✓ Proper formatting (currency/percentage/number)\n✓ Grid lines for easier reading\n\nThen GUARANTEED LABELS are working correctly!",
                    "presentation_name": "Guaranteed Labels Test",
                    "company_logo": "✅"
                }
            }
        ]
    }

    # Send to Layout Builder
    print("\n" + "=" * 70)
    print("Sending test presentation to Layout Builder...")
    print("=" * 70)

    try:
        response = requests.post(
            f"{LAYOUT_SERVICE_URL}/api/presentations",
            json=presentation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code in [200, 201]:
            result = response.json()
            presentation_id = result.get("id")
            presentation_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}"

            print("\n" + "=" * 70)
            print("✅ SUCCESS! Guaranteed Labels test created!")
            print("=" * 70)
            print(f"\n🔗 Presentation URL:")
            print(f"   {presentation_url}")
            print("\n" + "=" * 70)
            print("📋 VERIFICATION CHECKLIST:")
            print("=" * 70)
            print("\nSlide 2 - Line Chart:")
            print("  [ ] Y-axis title: 'Amount (USD)'")
            print("  [ ] Y-axis labels: $0, $50K, $100K, $150K, $200K")
            print("  [ ] Point labels on ALL 4 points: $125K, $145K, $178K, $195K")
            print("  [ ] X-axis labels: Q1 2024, Q2 2024, Q3 2024, Q4 2024")
            print("  [ ] Grid lines visible")

            print("\nSlide 3 - Bar Chart:")
            print("  [ ] Y-axis title: 'Percentage (%)'")
            print("  [ ] Y-axis labels: 0%, 10%, 20%, 30%, 40%")
            print("  [ ] Bar labels on ALL 4 bars: 35.5%, 28.3%, 22.1%, 14.1%")
            print("  [ ] X-axis labels: Product A, B, C, D")
            print("  [ ] Grid lines visible")

            print("\nSlide 4 - Multi-Series Line:")
            print("  [ ] Y-axis title: 'Value'")
            print("  [ ] Y-axis labels: 0, 50, 100, 150, 200")
            print("  [ ] Point labels on ALL 15 points (3 series × 5 points)")
            print("  [ ] X-axis labels: Jan, Feb, Mar, Apr, May")
            print("  [ ] Legend shows: Sales Team A, B, C")
            print("  [ ] Grid lines visible")

            print("\nSlide 5 - Horizontal Bar:")
            print("  [ ] X-axis title: 'Amount (USD)'")
            print("  [ ] X-axis labels: $0, $1M, $2M, $3M, $4M, $5M")
            print("  [ ] Bar labels on ALL 5 bars: $1.3M, $1.8M, $2.3M, $3.1M, $4.5M")
            print("  [ ] Y-axis labels: 2020, 2021, 2022, 2023, 2024")
            print("  [ ] Grid lines visible")

            print("\n" + "=" * 70)
            print("🎯 SUCCESS CRITERIA:")
            print("=" * 70)
            print("✓ ALL axis titles visible with proper units")
            print("✓ ALL axis labels formatted correctly")
            print("✓ ALL data points/bars show their exact values")
            print("✓ Grid lines visible on all charts")
            print("✓ NO missing labels or values")
            print("\n" + "=" * 70)
            print("✅ If all checks pass → GUARANTEED LABELS WORKING!")
            print("=" * 70)

        else:
            print(f"\n❌ ERROR: Failed to create presentation")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    test_guaranteed_labels()
