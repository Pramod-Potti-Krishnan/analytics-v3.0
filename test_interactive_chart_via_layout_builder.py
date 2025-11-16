"""
Test Interactive Chart Editor via Layout Builder

Generates a real presentation through Layout Builder with interactive chart.
"""

import requests
import json
from datetime import datetime
from chartjs_generator import ChartJSGenerator


def generate_interactive_chart_presentation():
    """
    Generate a presentation with interactive chart through Layout Builder.
    """

    print("=" * 60)
    print("🚀 Generating Interactive Chart Presentation")
    print("=" * 60)

    # Initialize generator
    generator = ChartJSGenerator(theme="professional")

    # Generate chart HTML with interactive editor enabled
    presentation_id = "test-interactive-" + datetime.now().strftime("%Y%m%d-%H%M%S")

    print(f"\n📊 Generating chart with interactive editor...")
    print(f"   Presentation ID: {presentation_id}")

    # Configure API URL (change this to your deployed analytics service URL)
    # Options:
    # 1. Relative URL (default) - requires layout builder to proxy: "/api/charts"
    # 2. Absolute URL - direct to analytics service: "http://localhost:8080/api/charts"
    # 3. Production URL: "https://your-analytics.railway.app/api/charts"
    api_url = "http://localhost:8080/api/charts"  # ✅ LOCAL ANALYTICS SERVICE

    chart_html = generator.generate_line_chart(
        data={
            "series_name": "Quarterly Revenue Growth",
            "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=600,
        chart_id="interactive-revenue-chart",
        enable_editor=True,  # ✨ ENABLE INTERACTIVE EDITOR
        presentation_id=presentation_id,
        api_base_url=api_url  # ✨ CONFIGURABLE API URL
    )

    print("   ✅ Chart HTML generated with interactive editor")
    print(f"   📏 HTML length: {len(chart_html)} characters")

    # Create presentation structure for Layout Builder
    presentation_data = {
        "title": "Interactive Chart Editor Demo",
        "slides": [
            # Title Slide
            {
                "layout": "L29",
                "content": {
                    "slide_title": "Interactive Chart Editor",
                    "element_1": "Live Demo",
                    "element_2": "This presentation demonstrates the interactive chart editor.\n\nClick the '📊 Edit Data' button on the chart to modify values in real-time!",
                    "presentation_name": "Interactive Chart Demo",
                    "company_logo": "✨"
                }
            },

            # Interactive Chart Slide
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Quarterly Revenue - Editable Chart",
                    "element_1": "Click 'Edit Data' to modify values",
                    "element_3": chart_html,  # Chart with interactive editor
                    "element_2": "💡 TRY IT:\n1. Click '📊 Edit Data' button\n2. Modify any values in the table\n3. Add or delete rows\n4. Click 'Save & Update'\n5. Watch the chart update!\n\n✅ Changes persist to database",
                    "presentation_name": "Interactive Chart Demo",
                    "company_logo": "✨"
                }
            },

            # Instructions Slide
            {
                "layout": "L29",
                "content": {
                    "slide_title": "How to Use Interactive Editor",
                    "element_1": "Step-by-Step Guide",
                    "element_2": "1. Click the '📊 Edit Data' button (top-right of chart)\n\n2. Modal popup shows data in editable table\n\n3. Edit X-axis labels (quarters) or Y-axis values (revenue)\n\n4. Click '+ Add Row' to add Q5 2025 data\n\n5. Delete rows with the 🗑️ button\n\n6. Click '💾 Save & Update Chart'\n\n7. Chart updates instantly and data saves to database!",
                    "presentation_name": "Interactive Chart Demo",
                    "company_logo": "✨"
                }
            }
        ]
    }

    # Send to Layout Builder
    layout_builder_url = "https://web-production-f0d13.up.railway.app/api/presentations"

    print(f"\n📤 Sending to Layout Builder...")
    print(f"   URL: {layout_builder_url}")
    print(f"   Slides: {len(presentation_data['slides'])}")

    try:
        response = requests.post(
            layout_builder_url,
            json=presentation_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in [200, 201]:
            result = response.json()
            presentation_id = result.get("id")
            presentation_url = f"https://web-production-f0d13.up.railway.app/p/{presentation_id}"

            print(f"\n✅ SUCCESS! Presentation generated")
            print("=" * 60)
            print(f"🔗 Presentation URL:")
            print(f"   {presentation_url}")
            print("=" * 60)
            print(f"\n🎯 What to do next:")
            print(f"   1. Open the URL above (opening in browser...)")
            print(f"   2. Navigate to slide 2 (the INTERACTIVE chart slide)")
            print(f"   3. Look for the '📊 Edit Data' button in top-right of chart")
            print(f"   4. Click it to open the interactive editor modal")
            print(f"   5. Edit values in the table and click 'Save & Update'")
            print(f"   6. Watch the chart update in real-time!")
            print(f"\n💡 TIP: The chart on slide 2 is INTERACTIVE - try editing it!")
            print("=" * 60)

            # Open in browser
            import webbrowser
            webbrowser.open(presentation_url)
            print(f"\n✨ Opening presentation in browser...")

            return presentation_url

        else:
            print(f"\n❌ Error from Layout Builder")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except Exception as e:
        print(f"\n❌ Error sending to Layout Builder: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    generate_interactive_chart_presentation()
