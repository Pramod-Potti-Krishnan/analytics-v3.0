"""
Comprehensive Chart.js Test Suite
==================================

Tests all chart types from the production Chart.js generator.
Generates a multi-slide presentation with one chart type per slide.

Author: Analytics Microservice v3 Team
Date: 2025-01-15
"""

import requests
import json
from chartjs_generator import ChartJSGenerator


LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"


def create_comprehensive_chartjs_test():
    """Create comprehensive test presentation with all chart types."""

    generator = ChartJSGenerator(theme="professional")

    print("Generating comprehensive Chart.js test presentation...")
    print("=" * 70)

    # ========================================
    # PREPARE TEST DATA
    # ========================================

    # Line chart data
    line_data = {
        "series_name": "Revenue Growth",
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [125000, 145000, 178000, 195000],
        "format": "currency"
    }

    # Multi-series line data
    multi_line_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "datasets": [
            {"label": "Product A", "data": [65, 78, 90, 95, 105, 120]},
            {"label": "Product B", "data": [45, 52, 60, 75, 85, 95]},
            {"label": "Product C", "data": [28, 35, 42, 50, 62, 75]}
        ],
        "format": "currency"
    }

    # Bar chart data
    bar_data = {
        "series_name": "Product Categories",
        "labels": ["Software", "Cloud", "Consulting", "Support"],
        "values": [450000, 380000, 290000, 220000],
        "format": "currency"
    }

    # Grouped bar data
    grouped_bar_data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Sales", "data": [450, 520, 610, 720]},
            {"label": "Expenses", "data": [320, 340, 380, 420]},
            {"label": "Profit", "data": [130, 180, 230, 300]}
        ],
        "format": "currency"
    }

    # Pie/Doughnut data
    circular_data = {
        "labels": ["Enterprise", "SMB", "Startup"],
        "values": [45, 30, 25]
    }

    # Scatter data
    scatter_data = {
        "datasets": [
            {
                "label": "Dataset 1",
                "data": [
                    {"x": 10, "y": 20}, {"x": 15, "y": 35},
                    {"x": 20, "y": 30}, {"x": 25, "y": 45},
                    {"x": 30, "y": 55}, {"x": 35, "y": 50}
                ]
            },
            {
                "label": "Dataset 2",
                "data": [
                    {"x": 12, "y": 25}, {"x": 18, "y": 40},
                    {"x": 22, "y": 35}, {"x": 28, "y": 50},
                    {"x": 32, "y": 60}, {"x": 38, "y": 55}
                ]
            }
        ],
        "format": "number"
    }

    # Bubble data
    bubble_data = {
        "datasets": [
            {
                "label": "Company A",
                "data": [
                    {"x": 20, "y": 30, "r": 15},
                    {"x": 40, "y": 50, "r": 10}
                ]
            },
            {
                "label": "Company B",
                "data": [
                    {"x": 25, "y": 35, "r": 20},
                    {"x": 45, "y": 55, "r": 12}
                ]
            }
        ],
        "format": "number"
    }

    # Radar data
    radar_data = {
        "labels": ["Speed", "Reliability", "Comfort", "Safety", "Efficiency"],
        "datasets": [
            {"label": "Model A", "data": [85, 90, 75, 95, 80]},
            {"label": "Model B", "data": [70, 85, 90, 80, 85]}
        ],
        "format": "number"
    }

    # Polar area data
    polar_data = {
        "labels": ["Red", "Green", "Blue", "Yellow", "Purple"],
        "values": [11, 16, 7, 14, 9]
    }

    # Mixed chart data
    mixed_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
        "datasets": [
            {"type": "line", "label": "Revenue", "data": [450, 520, 480, 610, 690]},
            {"type": "bar", "label": "Target", "data": [400, 500, 500, 600, 700]}
        ],
        "format": "currency"
    }

    # ========================================
    # GENERATE CHARTS
    # ========================================

    print("\n1. Generating Line Chart...")
    line_html = generator.generate_line_chart(line_data, height=600, chart_id="line-chart-test")

    print("2. Generating Multi-Series Line Chart...")
    multi_line_html = generator.generate_line_chart(multi_line_data, height=600, chart_id="multi-line-test")

    print("3. Generating Area Chart...")
    area_html = generator.generate_area_chart(line_data, height=600, chart_id="area-chart-test")

    print("4. Generating Stacked Area Chart...")
    stacked_area_html = generator.generate_stacked_area_chart(multi_line_data, height=600, chart_id="stacked-area-test")

    print("5. Generating Vertical Bar Chart...")
    bar_html = generator.generate_bar_chart(bar_data, height=600, chart_id="bar-chart-test")

    print("6. Generating Horizontal Bar Chart...")
    hbar_html = generator.generate_horizontal_bar_chart(bar_data, height=600, chart_id="hbar-chart-test")

    print("7. Generating Grouped Bar Chart...")
    grouped_bar_html = generator.generate_grouped_bar_chart(grouped_bar_data, height=600, chart_id="grouped-bar-test")

    print("8. Generating Stacked Bar Chart...")
    stacked_bar_html = generator.generate_stacked_bar_chart(grouped_bar_data, height=600, chart_id="stacked-bar-test")

    print("9. Generating Pie Chart...")
    pie_html = generator.generate_pie_chart(circular_data, height=600, chart_id="pie-chart-test")

    print("10. Generating Doughnut Chart...")
    doughnut_html = generator.generate_doughnut_chart(circular_data, height=600, chart_id="doughnut-chart-test")

    print("11. Generating Scatter Plot...")
    scatter_html = generator.generate_scatter_plot(scatter_data, height=600, chart_id="scatter-plot-test")

    print("12. Generating Bubble Chart...")
    bubble_html = generator.generate_bubble_chart(bubble_data, height=600, chart_id="bubble-chart-test")

    print("13. Generating Radar Chart...")
    radar_html = generator.generate_radar_chart(radar_data, height=600, chart_id="radar-chart-test")

    print("14. Generating Polar Area Chart...")
    polar_html = generator.generate_polar_area_chart(polar_data, height=600, chart_id="polar-chart-test")

    print("15. Generating Mixed Chart...")
    mixed_html = generator.generate_mixed_chart(mixed_data, height=600, chart_id="mixed-chart-test")

    print("\n✅ All charts generated successfully!")

    # ========================================
    # CREATE PRESENTATION
    # ========================================

    presentation_data = {
        "title": "Chart.js Comprehensive Test - All Chart Types",
        "slides": [
            # Title slide (L29)
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Chart.js Comprehensive Test",
                    "element_1": "Testing All Chart Types",
                    "element_2": "15 different chart types with RevealChart plugin. If all charts render correctly, Chart.js migration is APPROVED for production. No race conditions expected!",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 1. Line Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "1. Line Chart",
                    "element_1": "Revenue Growth Trend",
                    "element_3": line_html,
                    "element_2": "Basic line chart with currency formatting, data labels on points, and gradient fill.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 2. Multi-Series Line Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "2. Multi-Series Line Chart",
                    "element_1": "Product Performance",
                    "element_3": multi_line_html,
                    "element_2": "Multiple series line chart comparing 3 products over 6 months.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 3. Area Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "3. Area Chart",
                    "element_1": "Revenue with Filled Area",
                    "element_3": area_html,
                    "element_2": "Area chart shows the same data as line chart but with filled area under the line.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 4. Stacked Area Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "4. Stacked Area Chart",
                    "element_1": "Product Performance Stacked",
                    "element_3": stacked_area_html,
                    "element_2": "Stacked area chart shows cumulative values of multiple series.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 5. Vertical Bar Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "5. Vertical Bar Chart",
                    "element_1": "Category Performance",
                    "element_3": bar_html,
                    "element_2": "Vertical bar chart with different colors for each category.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 6. Horizontal Bar Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "6. Horizontal Bar Chart",
                    "element_1": "Category Performance (Horizontal)",
                    "element_3": hbar_html,
                    "element_2": "Same data as vertical bars but displayed horizontally for easier label reading.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 7. Grouped Bar Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "7. Grouped Bar Chart",
                    "element_1": "Quarterly Comparison",
                    "element_3": grouped_bar_html,
                    "element_2": "Grouped bars comparing Sales, Expenses, and Profit side-by-side.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 8. Stacked Bar Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "8. Stacked Bar Chart",
                    "element_1": "Quarterly Totals",
                    "element_3": stacked_bar_html,
                    "element_2": "Stacked bars showing cumulative totals of Sales, Expenses, and Profit.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 9. Pie Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "9. Pie Chart",
                    "element_1": "Market Share Distribution",
                    "element_3": pie_html,
                    "element_2": "Pie chart showing percentage distribution across customer segments.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 10. Doughnut Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "10. Doughnut Chart",
                    "element_1": "Market Share (Doughnut)",
                    "element_3": doughnut_html,
                    "element_2": "Doughnut chart with center hole, same data as pie chart.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 11. Scatter Plot (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "11. Scatter Plot",
                    "element_1": "Correlation Analysis",
                    "element_3": scatter_html,
                    "element_2": "Scatter plot showing relationship between two variables for two datasets.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 12. Bubble Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "12. Bubble Chart",
                    "element_1": "Three-Dimensional Data",
                    "element_3": bubble_html,
                    "element_2": "Bubble chart with size representing third dimension of data.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 13. Radar Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "13. Radar Chart",
                    "element_1": "Multi-Attribute Comparison",
                    "element_3": radar_html,
                    "element_2": "Radar chart comparing two models across 5 attributes.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 14. Polar Area Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "14. Polar Area Chart",
                    "element_1": "Radial Distribution",
                    "element_3": polar_html,
                    "element_2": "Polar area chart showing values on a radial scale.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # 15. Mixed Chart (L02)
            {
                "layout": "L02",
                "content": {
                    "slide_title": "15. Mixed Chart (Line + Bar)",
                    "element_1": "Revenue vs Target",
                    "element_3": mixed_html,
                    "element_2": "Mixed chart combining line (Revenue) and bar (Target) on same axes.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            },

            # Final Summary Slide (L29)
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Test Complete! ✅",
                    "element_1": "15 Chart Types Tested",
                    "element_2": "If all charts rendered correctly, Chart.js migration is APPROVED. Benefits: Zero race conditions, automatic lifecycle management, smaller bundle size, better performance.",
                    "presentation_name": "Chart.js All Types Test",
                    "company_logo": "📊"
                }
            }
        ]
    }

    # ========================================
    # SEND TO LAYOUT BUILDER
    # ========================================

    print("\n" + "=" * 70)
    print("Sending comprehensive test to Layout Builder...")
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
            presentation_id = result.get("id")  # API returns "id" not "presentation_id"
            presentation_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}"

            print("\n" + "=" * 70)
            print("✅ SUCCESS! Comprehensive test presentation created!")
            print("=" * 70)
            print(f"\n🔗 Presentation URL:")
            print(f"   {presentation_url}")
            print("\n" + "=" * 70)
            print("📋 COMPREHENSIVE TEST CHECKLIST:")
            print("=" * 70)
            print("Navigate to the URL above and verify:\n")
            print(" [ ] 1.  Line Chart renders with data labels")
            print(" [ ] 2.  Multi-Series Line Chart shows 3 lines")
            print(" [ ] 3.  Area Chart has filled gradient")
            print(" [ ] 4.  Stacked Area Chart shows cumulative values")
            print(" [ ] 5.  Vertical Bar Chart has colored bars")
            print(" [ ] 6.  Horizontal Bar Chart displays correctly")
            print(" [ ] 7.  Grouped Bar Chart shows side-by-side bars")
            print(" [ ] 8.  Stacked Bar Chart shows cumulative bars")
            print(" [ ] 9.  Pie Chart displays percentages")
            print(" [ ] 10. Doughnut Chart has center hole")
            print(" [ ] 11. Scatter Plot shows two datasets")
            print(" [ ] 12. Bubble Chart has variable-sized bubbles")
            print(" [ ] 13. Radar Chart displays pentagon shape")
            print(" [ ] 14. Polar Area Chart shows radial segments")
            print(" [ ] 15. Mixed Chart combines line and bar")
            print("\n" + "=" * 70)
            print("🎯 SUCCESS CRITERIA:")
            print("=" * 70)
            print("✓ ALL 15 charts render (not just last one)")
            print("✓ No JavaScript errors in console")
            print("✓ Data labels visible on all charts")
            print("✓ Scales and grid lines displayed")
            print("✓ Colors applied correctly")
            print("✓ Charts fit their containers")
            print("✓ Currency formatting shows $XXXk")
            print("✓ No race conditions observed")
            print("\n" + "=" * 70)
            print("🎉 If all checks pass → Chart.js MIGRATION APPROVED!")
            print("=" * 70)

            # Save test data
            test_log = {
                "test_name": "comprehensive_chartjs_test",
                "timestamp": "2025-01-15",
                "presentation_url": presentation_url,
                "presentation_id": presentation_id,
                "chart_types_tested": 15,
                "status": "pending_verification"
            }

            with open("chartjs_comprehensive_test_log.json", "w") as f:
                json.dump(test_log, f, indent=2)

            print(f"\nTest log saved to: chartjs_comprehensive_test_log.json")

        else:
            print(f"\n❌ ERROR: Failed to create presentation")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Failed to send request to Layout Builder")
        print(f"Error: {e}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    create_comprehensive_chartjs_test()
