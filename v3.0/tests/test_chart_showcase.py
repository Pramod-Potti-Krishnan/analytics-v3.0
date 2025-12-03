"""
Test script to generate chart showcase presentation on Layout Builder.
Creates line, bar, and donut charts using L02 layout for user review.
"""

import asyncio
import json
import requests
from agent import process_analytics_slide

# Railway Layout Builder URL
LAYOUT_BUILDER_URL = "https://web-production-f0d13.up.railway.app"


async def generate_chart_slides():
    """Generate three analytics slides with different chart types."""

    slides_data = []

    # 1. LINE CHART - Revenue Over Time
    print("Generating Line Chart (Revenue Over Time)...")
    line_request = {
        "presentation_id": "showcase-001",
        "slide_id": "slide-1",
        "slide_number": 1,
        "narrative": "Revenue has grown consistently over the past 4 quarters, with particularly strong performance in Q3 and Q4 driven by new product launches.",
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000},
            {"label": "Q3 2024", "value": 178000},
            {"label": "Q4 2024", "value": 195000}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Revenue Growth Trajectory",
            "subtitle": "Quarterly Performance FY 2024",
            "presentation_name": "Chart Showcase",
            "company_logo": "📊"
        }
    }

    line_result = await process_analytics_slide(
        analytics_type="revenue_over_time",
        layout="L02",
        request_data=line_request
    )

    if line_result["success"]:
        slides_data.append({
            "layout": "L02",
            "content": line_result["content"]
        })
        print("✓ Line chart generated successfully")
    else:
        print(f"✗ Line chart failed: {line_result.get('error')}")
        return None

    # 2. BAR CHART - Quarterly Comparison
    print("\nGenerating Bar Chart (Quarterly Comparison)...")
    bar_request = {
        "presentation_id": "showcase-001",
        "slide_id": "slide-2",
        "slide_number": 2,
        "narrative": "Sales performance varied significantly across product categories, with Software Solutions leading at $450K, followed by Cloud Services at $380K.",
        "data": [
            {"label": "Software Solutions", "value": 450000},
            {"label": "Cloud Services", "value": 380000},
            {"label": "Consulting", "value": 290000},
            {"label": "Support & Maintenance", "value": 220000}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Product Category Performance",
            "subtitle": "Q4 2024 Revenue by Category",
            "presentation_name": "Chart Showcase",
            "company_logo": "📊"
        }
    }

    bar_result = await process_analytics_slide(
        analytics_type="quarterly_comparison",
        layout="L02",
        request_data=bar_request
    )

    if bar_result["success"]:
        slides_data.append({
            "layout": "L02",
            "content": bar_result["content"]
        })
        print("✓ Bar chart generated successfully")
    else:
        print(f"✗ Bar chart failed: {bar_result.get('error')}")
        return None

    # 3. DONUT CHART - Market Share
    print("\nGenerating Donut Chart (Market Share)...")
    donut_request = {
        "presentation_id": "showcase-001",
        "slide_id": "slide-3",
        "slide_number": 3,
        "narrative": "Market share distribution shows strong performance in Enterprise segment (45%), followed by SMB (30%) and Startup (25%).",
        "data": [
            {"label": "Enterprise", "value": 45},
            {"label": "SMB", "value": 30},
            {"label": "Startup", "value": 25}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Customer Segment Distribution",
            "subtitle": "Market Share by Company Size",
            "presentation_name": "Chart Showcase",
            "company_logo": "📊"
        }
    }

    donut_result = await process_analytics_slide(
        analytics_type="market_share",
        layout="L02",
        request_data=donut_request
    )

    if donut_result["success"]:
        slides_data.append({
            "layout": "L02",
            "content": donut_result["content"]
        })
        print("✓ Donut chart generated successfully")
    else:
        print(f"✗ Donut chart failed: {donut_result.get('error')}")
        return None

    return slides_data


def create_presentation_on_layout_builder(slides_data):
    """Send presentation to Layout Builder service."""

    # Add title slide
    presentation_data = {
        "title": "ApexCharts Showcase - Line, Bar, Donut",
        "slides": [
            {
                "layout": "L29",
                "content": {
                    "hero_content": """<div style='width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                        <h1 style='font-size: 96px; color: white; font-weight: 900; margin-bottom: 32px;'>Chart Showcase</h1>
                        <p style='font-size: 48px; color: rgba(255,255,255,0.9);'>ApexCharts Integration Review</p>
                        <p style='font-size: 32px; color: rgba(255,255,255,0.8); margin-top: 48px;'>Line • Bar • Donut</p>
                    </div>"""
                }
            }
        ] + slides_data
    }

    # POST to Layout Builder
    print(f"\nSending presentation to {LAYOUT_BUILDER_URL}...")
    try:
        response = requests.post(
            f"{LAYOUT_BUILDER_URL}/api/presentations",
            headers={"Content-Type": "application/json"},
            json=presentation_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            presentation_url = f"{LAYOUT_BUILDER_URL}{result['url']}"
            print(f"\n{'='*70}")
            print(f"✓ Presentation created successfully!")
            print(f"{'='*70}")
            print(f"\nPresentation ID: {result['id']}")
            print(f"View URL: {presentation_url}")
            print(f"\nSlides included:")
            print(f"  1. Title Slide (L29)")
            print(f"  2. Line Chart - Revenue Growth (L02)")
            print(f"  3. Bar Chart - Product Categories (L02)")
            print(f"  4. Donut Chart - Market Share (L02)")
            print(f"\n{'='*70}\n")
            return presentation_url
        else:
            print(f"✗ Failed to create presentation: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"✗ Error posting to Layout Builder: {e}")
        return None


async def main():
    """Main execution function."""
    print("="*70)
    print("ApexCharts Showcase Generator")
    print("="*70)
    print("\nGenerating analytics slides with L02 layout...\n")

    # Generate slides
    slides_data = await generate_chart_slides()

    if not slides_data:
        print("\n✗ Failed to generate slides")
        return

    # Save slide data for debugging
    with open("showcase_slides_data.json", "w") as f:
        json.dump(slides_data, f, indent=2)
    print(f"\n✓ Slide data saved to showcase_slides_data.json")

    # Create presentation on Layout Builder
    presentation_url = create_presentation_on_layout_builder(slides_data)

    if presentation_url:
        print(f"\n🎉 SUCCESS! Open this URL in your browser:")
        print(f"\n    {presentation_url}\n")
        print("Navigate with arrow keys, press 'G' for grid overlay, 'H' for help\n")
    else:
        print("\n✗ Failed to create presentation on Layout Builder")


if __name__ == "__main__":
    asyncio.run(main())
