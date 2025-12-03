"""
Chart.js Test Script

Creates a test presentation with 3 Chart.js charts to verify:
1. All 3 charts render (not just the last one) ← KEY TEST
2. Charts fit containers properly
3. Formatters work correctly
4. No JavaScript errors

If this test succeeds, we proceed with full Chart.js migration.
If it fails, we try iframe isolation or other alternatives.
"""

import requests
import json
from chartjs_test_generator import ChartJSTestGenerator

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"


def create_chartjs_test_presentation():
    """Create test presentation with Chart.js charts."""

    generator = ChartJSTestGenerator(theme="professional")

    # Generate line chart
    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue Growth",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=600,
        chart_id="chartjs-line-test"
    )

    # Generate bar chart
    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Product Categories",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450000, 380000, 290000, 220000],
            "format": "currency"
        },
        height=600,
        chart_id="chartjs-bar-test"
    )

    # Generate doughnut chart (Chart.js calls it "doughnut" not "donut")
    doughnut_html = generator.generate_doughnut_chart(
        data={
            "labels": ["Enterprise", "SMB", "Startup"],
            "values": [45, 30, 25]
        },
        height=600,
        chart_id="chartjs-doughnut-test"
    )

    # Create presentation data
    presentation_data = {
        "title": "Chart.js Test - RevealChart Plugin",
        "slides": [
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Chart.js Integration Test",
                    "element_1": "Testing RevealChart Plugin",
                    "element_2": "If all 3 charts render correctly, we migrate from ApexCharts to Chart.js. The RevealChart plugin handles all Reveal.js lifecycle automatically - no race conditions!",
                    "presentation_name": "Chart.js Test",
                    "company_logo": "🧪"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Revenue Growth Trend",
                    "element_1": "Q1-Q4 Performance",
                    "element_3": line_html,
                    "element_2": "Chart.js line chart with currency formatting. Uses Canvas rendering instead of SVG. Plugin auto-manages lifecycle.",
                    "presentation_name": "Chart.js Test",
                    "company_logo": "🧪"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Product Category Performance",
                    "element_1": "Revenue by Category",
                    "element_3": bar_html,
                    "element_2": "Chart.js bar chart with currency formatting. No event handlers needed - RevealChart plugin handles everything!",
                    "presentation_name": "Chart.js Test",
                    "company_logo": "🧪"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Market Share Distribution",
                    "element_1": "Customer Segments",
                    "element_3": doughnut_html,
                    "element_2": "Chart.js doughnut chart with percentage display. Canvas-based rendering for better performance.",
                    "presentation_name": "Chart.js Test",
                    "company_logo": "🧪"
                }
            }
        ]
    }

    # Save test data
    with open('chartjs_test_data.json', 'w') as f:
        json.dump(presentation_data, f, indent=2)
        print("✅ Saved test data to chartjs_test_data.json")

    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT: Layout Builder Team Setup Required")
    print("=" * 70)
    print("\nBefore testing, ask Layout Builder team to add to <head> section:")
    print("\n<!-- Chart.js + RevealChart Plugin -->")
    print('<script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>')
    print('<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>')
    print("\nAnd in Reveal.initialize():")
    print("\nReveal.initialize({")
    print("  plugins: [ RevealChart ],")
    print("  chart: {")
    print("    defaults: {")
    print("      font: { family: 'Inter, system-ui, sans-serif', size: 14 }")
    print("    }")
    print("  },")
    print("  // ... other config")
    print("});")
    print("\n" + "=" * 70)
    print("\nOnce Layout Builder is updated, run this script again to create")
    print("the test presentation.")
    print("=" * 70)

    # Ask user if Layout Builder is ready
    response = input("\n✋ Has Layout Builder team added Chart.js CDN? (y/n): ")

    if response.lower() != 'y':
        print("\n⏸️  Paused. Please coordinate with Layout Builder team first.")
        print("   Then run this script again.")
        return None, None

    # Send to Layout Builder
    print("\n📤 Sending test presentation to Layout Builder...")
    response = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=presentation_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code in [200, 201]:
        result = response.json()
        presentation_id = result.get('id')
        presentation_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}"

        print("\n" + "=" * 70)
        print("✅ CHART.JS TEST PRESENTATION CREATED!")
        print("=" * 70)
        print(f"\n🌐 URL: {presentation_url}")
        print(f"🆔 ID: {presentation_id}")
        print("\n📋 Test Checklist:")
        print("   □ Navigate through all 4 slides")
        print("   □ Verify all 3 charts are visible (not just last one) ← KEY")
        print("   □ Check charts fit their containers properly")
        print("   □ Confirm currency formatting shows $XXXk")
        print("   □ Confirm percentage formatting shows XX%")
        print("   □ Open browser console, verify NO errors")
        print("   □ Check for smooth rendering (no delays)")
        print("\n🎯 SUCCESS CRITERIA:")
        print("   ✅ ALL 3 charts render simultaneously")
        print("   ✅ No race condition (no blank charts)")
        print("   ✅ No JavaScript errors")
        print("   ✅ Charts look professional and fit properly")
        print("\n🚀 IF TEST SUCCEEDS:")
        print("   → Proceed with full Chart.js migration")
        print("   → Estimated effort: 2-3 weeks")
        print("   → Expected outcome: Permanent fix, zero ongoing issues")
        print("\n⚠️  IF TEST FAILS:")
        print("   → Try iframe isolation approach (8-16 hours)")
        print("   → Or consider server-side rendering (1-2 weeks)")
        print("=" * 70)

        return presentation_id, presentation_url
    else:
        print(f"\n❌ Failed to create presentation: {response.status_code}")
        print(f"   Response: {response.text}")
        return None, None


if __name__ == "__main__":
    create_chartjs_test_presentation()
