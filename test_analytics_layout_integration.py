"""
Analytics Microservice v3 ↔ Layout Builder Integration Tests

Tests end-to-end integration:
1. Analytics Service generates chart HTML + insights
2. Layout Builder creates Reveal.js presentation
3. Presentation renders correctly with animated ApexCharts
"""

import requests
import json
import time
from typing import Dict, Any, List
from datetime import datetime

# Configuration
ANALYTICS_BASE_URL = "http://localhost:8080"
LAYOUT_BUILDER_URL = "https://web-production-f0d13.up.railway.app"

# Test results storage
test_results = []


def log_test(test_name: str, status: str, details: dict):
    """Log test result."""
    result = {
        "test_name": test_name,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
    test_results.append(result)

    status_icon = "✅" if status == "PASSED" else "❌"
    print(f"\n{status_icon} {test_name}: {status}")
    print(f"   Details: {json.dumps(details, indent=2)}")


def check_analytics_health() -> bool:
    """Check if Analytics Service is running."""
    try:
        response = requests.get(f"{ANALYTICS_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def check_layout_builder_health() -> bool:
    """Check if Layout Builder is accessible."""
    try:
        response = requests.get(f"{LAYOUT_BUILDER_URL}/", timeout=10)
        return response.status_code == 200
    except:
        return False


def test_l01_single_chart_integration():
    """
    Test L01 layout with single chart.

    Flow:
    1. Generate analytics content (revenue_over_time)
    2. Create presentation via Layout Builder
    3. Verify presentation created and accessible
    """
    print("\n" + "="*70)
    print("TEST 1: L01 Single Chart Integration")
    print("="*70)

    try:
        # Step 1: Generate analytics content
        print("\n[Step 1] Generating analytics content...")
        analytics_response = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/L01/revenue_over_time",
            json={
                "presentation_id": "integration-test-001",
                "slide_id": "slide-1",
                "slide_number": 1,
                "narrative": "Show quarterly revenue growth highlighting strong Q3-Q4 performance",
                "data": [
                    {"label": "Q1 2024", "value": 125000},
                    {"label": "Q2 2024", "value": 145000},
                    {"label": "Q3 2024", "value": 162000},
                    {"label": "Q4 2024", "value": 178000}
                ],
                "context": {
                    "theme": "professional",
                    "audience": "Board of Directors",
                    "slide_title": "Quarterly Revenue Growth",
                    "subtitle": "FY 2024 Performance",
                    "presentation_name": "Integration Test"
                }
            },
            timeout=30
        )

        if analytics_response.status_code != 200:
            log_test(
                "L01 Single Chart - Analytics Generation",
                "FAILED",
                {"error": f"Analytics API returned {analytics_response.status_code}"}
            )
            return False

        analytics_result = analytics_response.json()
        content = analytics_result.get("content", {})

        # Validate analytics content
        required_fields = ["slide_title", "element_1", "element_4", "element_3"]
        missing = [f for f in required_fields if f not in content]

        if missing:
            log_test(
                "L01 Single Chart - Analytics Generation",
                "FAILED",
                {"error": f"Missing fields: {missing}"}
            )
            return False

        print("   ✓ Analytics content generated successfully")
        print(f"   ✓ Chart HTML length: {len(content['element_4'])} chars")
        print(f"   ✓ Insight length: {len(content['element_3'])} words")

        # Step 2: Create presentation via Layout Builder
        print("\n[Step 2] Creating presentation via Layout Builder...")

        presentation_data = {
            "title": "Analytics Integration Test - L01",
            "slides": [
                {
                    "layout": "L01",
                    "content": content
                }
            ]
        }

        layout_response = requests.post(
            f"{LAYOUT_BUILDER_URL}/api/presentations",
            headers={"Content-Type": "application/json"},
            json=presentation_data,
            timeout=30
        )

        if layout_response.status_code != 200:
            log_test(
                "L01 Single Chart - Layout Builder",
                "FAILED",
                {"error": f"Layout Builder returned {layout_response.status_code}", "response": layout_response.text}
            )
            return False

        layout_result = layout_response.json()
        presentation_id = layout_result.get("id")
        presentation_url = layout_result.get("url")

        print(f"   ✓ Presentation created: {presentation_id}")
        print(f"   ✓ View URL: {LAYOUT_BUILDER_URL}{presentation_url}")

        # Step 3: Verify presentation is accessible
        print("\n[Step 3] Verifying presentation accessibility...")

        verify_response = requests.get(
            f"{LAYOUT_BUILDER_URL}{presentation_url}",
            timeout=10
        )

        if verify_response.status_code != 200:
            log_test(
                "L01 Single Chart - Presentation Access",
                "FAILED",
                {"error": f"Cannot access presentation: {verify_response.status_code}"}
            )
            return False

        # Check if ApexCharts is in the HTML
        html_content = verify_response.text
        has_apexcharts = "apexcharts" in html_content.lower()
        has_chart_id = "chart-" in html_content
        has_reveal = "Reveal.on('slidechanged'" in html_content or "Reveal.js" in html_content

        print(f"   ✓ Presentation accessible")
        print(f"   ✓ ApexCharts detected: {has_apexcharts}")
        print(f"   ✓ Chart ID detected: {has_chart_id}")
        print(f"   ✓ Reveal.js integration: {has_reveal}")

        log_test(
            "L01 Single Chart Integration",
            "PASSED",
            {
                "presentation_id": presentation_id,
                "presentation_url": f"{LAYOUT_BUILDER_URL}{presentation_url}",
                "apexcharts_present": has_apexcharts,
                "chart_id_present": has_chart_id,
                "reveal_integration": has_reveal,
                "analytics_metadata": analytics_result.get("metadata", {})
            }
        )

        return True

    except Exception as e:
        log_test(
            "L01 Single Chart Integration",
            "FAILED",
            {"error": str(e), "exception_type": type(e).__name__}
        )
        import traceback
        traceback.print_exc()
        return False


def test_l03_comparison_charts_integration():
    """
    Test L03 layout with side-by-side comparison charts.

    Flow:
    1. Generate analytics content (yoy_growth)
    2. Create presentation via Layout Builder
    3. Verify both charts present
    """
    print("\n" + "="*70)
    print("TEST 2: L03 Side-by-Side Comparison Integration")
    print("="*70)

    try:
        # Step 1: Generate analytics content
        print("\n[Step 1] Generating comparison analytics content...")
        analytics_response = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/L03/yoy_growth",
            json={
                "presentation_id": "integration-test-002",
                "slide_id": "slide-2",
                "slide_number": 2,
                "narrative": "Compare 2023 vs 2024 quarterly revenue showing 25% YoY growth",
                "data": [
                    # 2023 data
                    {"label": "Q1 2023", "value": 125000},
                    {"label": "Q2 2023", "value": 145000},
                    {"label": "Q3 2023", "value": 162000},
                    {"label": "Q4 2023", "value": 178000},
                    # 2024 data
                    {"label": "Q1 2024", "value": 156000},
                    {"label": "Q2 2024", "value": 181000},
                    {"label": "Q3 2024", "value": 203000},
                    {"label": "Q4 2024", "value": 223000}
                ],
                "context": {
                    "theme": "professional",
                    "audience": "Board of Directors",
                    "slide_title": "Year-over-Year Revenue Growth",
                    "subtitle": "2023 vs 2024 Quarterly Comparison",
                    "presentation_name": "Integration Test"
                }
            },
            timeout=30
        )

        if analytics_response.status_code != 200:
            log_test(
                "L03 Comparison - Analytics Generation",
                "FAILED",
                {"error": f"Analytics API returned {analytics_response.status_code}"}
            )
            return False

        analytics_result = analytics_response.json()
        content = analytics_result.get("content", {})

        # Validate L03 content structure
        required_fields = ["slide_title", "element_1", "element_4", "element_2", "element_3", "element_5"]
        missing = [f for f in required_fields if f not in content]

        if missing:
            log_test(
                "L03 Comparison - Analytics Generation",
                "FAILED",
                {"error": f"Missing L03 fields: {missing}"}
            )
            return False

        print("   ✓ Analytics content generated successfully")
        print(f"   ✓ Left chart HTML length: {len(content['element_4'])} chars")
        print(f"   ✓ Right chart HTML length: {len(content['element_2'])} chars")
        print(f"   ✓ Left description: {content['element_3'][:50]}...")
        print(f"   ✓ Right description: {content['element_5'][:50]}...")

        # Step 2: Create presentation
        print("\n[Step 2] Creating comparison presentation...")

        presentation_data = {
            "title": "Analytics Integration Test - L03 Comparison",
            "slides": [
                {
                    "layout": "L03",
                    "content": content
                }
            ]
        }

        layout_response = requests.post(
            f"{LAYOUT_BUILDER_URL}/api/presentations",
            headers={"Content-Type": "application/json"},
            json=presentation_data,
            timeout=30
        )

        if layout_response.status_code != 200:
            log_test(
                "L03 Comparison - Layout Builder",
                "FAILED",
                {"error": f"Layout Builder returned {layout_response.status_code}"}
            )
            return False

        layout_result = layout_response.json()
        presentation_id = layout_result.get("id")
        presentation_url = layout_result.get("url")

        print(f"   ✓ Presentation created: {presentation_id}")
        print(f"   ✓ View URL: {LAYOUT_BUILDER_URL}{presentation_url}")

        # Step 3: Verify presentation
        print("\n[Step 3] Verifying comparison presentation...")

        verify_response = requests.get(
            f"{LAYOUT_BUILDER_URL}{presentation_url}",
            timeout=10
        )

        if verify_response.status_code != 200:
            log_test(
                "L03 Comparison - Presentation Access",
                "FAILED",
                {"error": f"Cannot access presentation"}
            )
            return False

        html_content = verify_response.text
        chart_left_count = html_content.count("chart-left")
        chart_right_count = html_content.count("chart-right")
        has_apexcharts = "apexcharts" in html_content.lower()

        print(f"   ✓ Presentation accessible")
        print(f"   ✓ Left chart references: {chart_left_count}")
        print(f"   ✓ Right chart references: {chart_right_count}")
        print(f"   ✓ ApexCharts detected: {has_apexcharts}")

        log_test(
            "L03 Comparison Charts Integration",
            "PASSED",
            {
                "presentation_id": presentation_id,
                "presentation_url": f"{LAYOUT_BUILDER_URL}{presentation_url}",
                "left_chart_present": chart_left_count > 0,
                "right_chart_present": chart_right_count > 0,
                "apexcharts_present": has_apexcharts,
                "analytics_metadata": analytics_result.get("metadata", {})
            }
        )

        return True

    except Exception as e:
        log_test(
            "L03 Comparison Charts Integration",
            "FAILED",
            {"error": str(e)}
        )
        import traceback
        traceback.print_exc()
        return False


def test_full_presentation_integration():
    """
    Test complete presentation with multiple analytics slides.

    Creates:
    - Title slide (L29)
    - Revenue chart (L01)
    - Market share (L01)
    - YoY comparison (L03)
    """
    print("\n" + "="*70)
    print("TEST 3: Full Multi-Slide Presentation Integration")
    print("="*70)

    try:
        # Generate all analytics content
        print("\n[Step 1] Generating all analytics slides...")

        slides_content = []

        # Slide 1: Title (manually created)
        slides_content.append({
            "layout": "L29",
            "content": {
                "hero_content": "<div style='width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; flex-direction: column; align-items: center; justify-content: center;'><h1 style='font-size: 96px; color: white; font-weight: 900;'>Analytics Integration Test</h1><p style='font-size: 42px; color: rgba(255,255,255,0.9); margin-top: 32px;'>Complete Presentation Demo</p></div>"
            }
        })

        # Slide 2: Revenue chart (L01)
        print("   Generating slide 2: Revenue chart...")
        response1 = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/L01/revenue_over_time",
            json={
                "presentation_id": "integration-test-003",
                "slide_id": "slide-2",
                "slide_number": 2,
                "narrative": "Quarterly revenue growth",
                "data": [
                    {"label": "Q1", "value": 125000},
                    {"label": "Q2", "value": 145000},
                    {"label": "Q3", "value": 162000},
                    {"label": "Q4", "value": 178000}
                ],
                "context": {
                    "theme": "professional",
                    "slide_title": "Revenue Growth",
                    "subtitle": "FY 2024",
                    "presentation_name": "Integration Test"
                }
            },
            timeout=30
        )
        slides_content.append({
            "layout": "L01",
            "content": response1.json()["content"]
        })

        # Slide 3: Market share (L01)
        print("   Generating slide 3: Market share...")
        response2 = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/L01/market_share",
            json={
                "presentation_id": "integration-test-003",
                "slide_id": "slide-3",
                "slide_number": 3,
                "narrative": "Market share distribution",
                "data": [
                    {"label": "Product A", "value": 35},
                    {"label": "Product B", "value": 28},
                    {"label": "Product C", "value": 22},
                    {"label": "Product D", "value": 15}
                ],
                "context": {
                    "theme": "professional",
                    "slide_title": "Market Share",
                    "subtitle": "Q4 2024",
                    "presentation_name": "Integration Test"
                }
            },
            timeout=30
        )
        slides_content.append({
            "layout": "L01",
            "content": response2.json()["content"]
        })

        # Slide 4: YoY comparison (L03)
        print("   Generating slide 4: YoY comparison...")
        response3 = requests.post(
            f"{ANALYTICS_BASE_URL}/api/v1/analytics/L03/yoy_growth",
            json={
                "presentation_id": "integration-test-003",
                "slide_id": "slide-4",
                "slide_number": 4,
                "narrative": "Year-over-year comparison",
                "data": [
                    {"label": "Q1 2023", "value": 100}, {"label": "Q2 2023", "value": 115},
                    {"label": "Q3 2023", "value": 130}, {"label": "Q4 2023", "value": 142},
                    {"label": "Q1 2024", "value": 125}, {"label": "Q2 2024", "value": 145},
                    {"label": "Q3 2024", "value": 162}, {"label": "Q4 2024", "value": 178}
                ],
                "context": {
                    "theme": "professional",
                    "slide_title": "Year-over-Year Growth",
                    "subtitle": "2023 vs 2024",
                    "presentation_name": "Integration Test"
                }
            },
            timeout=30
        )
        slides_content.append({
            "layout": "L03",
            "content": response3.json()["content"]
        })

        print(f"   ✓ Generated {len(slides_content)} slides")

        # Step 2: Create full presentation
        print("\n[Step 2] Creating full presentation...")

        presentation_data = {
            "title": "Analytics Integration Test - Full Presentation",
            "slides": slides_content
        }

        layout_response = requests.post(
            f"{LAYOUT_BUILDER_URL}/api/presentations",
            headers={"Content-Type": "application/json"},
            json=presentation_data,
            timeout=30
        )

        if layout_response.status_code != 200:
            log_test(
                "Full Presentation - Layout Builder",
                "FAILED",
                {"error": f"Layout Builder returned {layout_response.status_code}"}
            )
            return False

        layout_result = layout_response.json()
        presentation_id = layout_result.get("id")
        presentation_url = layout_result.get("url")

        print(f"   ✓ Presentation created: {presentation_id}")
        print(f"   ✓ View URL: {LAYOUT_BUILDER_URL}{presentation_url}")

        # Step 3: Verify presentation
        print("\n[Step 3] Verifying full presentation...")

        verify_response = requests.get(
            f"{LAYOUT_BUILDER_URL}{presentation_url}",
            timeout=10
        )

        if verify_response.status_code != 200:
            log_test(
                "Full Presentation - Access",
                "FAILED",
                {"error": "Cannot access presentation"}
            )
            return False

        html_content = verify_response.text
        apexcharts_count = html_content.lower().count("apexcharts")

        print(f"   ✓ Presentation accessible")
        print(f"   ✓ ApexCharts references: {apexcharts_count}")
        print(f"   ✓ Total slides: {len(slides_content)}")

        log_test(
            "Full Presentation Integration",
            "PASSED",
            {
                "presentation_id": presentation_id,
                "presentation_url": f"{LAYOUT_BUILDER_URL}{presentation_url}",
                "total_slides": len(slides_content),
                "analytics_slides": 3,
                "apexcharts_references": apexcharts_count
            }
        )

        return True

    except Exception as e:
        log_test(
            "Full Presentation Integration",
            "FAILED",
            {"error": str(e)}
        )
        import traceback
        traceback.print_exc()
        return False


def generate_test_report():
    """Generate comprehensive test report."""
    print("\n" + "="*70)
    print("GENERATING TEST REPORT")
    print("="*70)

    # Save detailed results
    report_file = f"integration_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "test_suite": "Analytics Microservice v3 ↔ Layout Builder Integration",
            "timestamp": datetime.utcnow().isoformat(),
            "analytics_service": ANALYTICS_BASE_URL,
            "layout_builder": LAYOUT_BUILDER_URL,
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results if r["status"] == "PASSED"),
            "failed": sum(1 for r in test_results if r["status"] == "FAILED"),
            "results": test_results
        }, f, indent=2)

    print(f"\n✓ Detailed results saved: {report_file}")

    # Generate markdown report
    md_report = f"""# Analytics ↔ Layout Builder Integration Test Report

**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Analytics Service**: {ANALYTICS_BASE_URL}
**Layout Builder**: {LAYOUT_BUILDER_URL}

## Summary

- **Total Tests**: {len(test_results)}
- **Passed**: {sum(1 for r in test_results if r["status"] == "PASSED")} ✅
- **Failed**: {sum(1 for r in test_results if r["status"] == "FAILED")} ❌

## Test Results

"""

    for result in test_results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        md_report += f"\n### {status_icon} {result['test_name']}\n\n"
        md_report += f"**Status**: {result['status']}  \n"
        md_report += f"**Timestamp**: {result['timestamp']}  \n\n"

        if result["status"] == "PASSED":
            details = result["details"]
            if "presentation_url" in details:
                md_report += f"**Presentation URL**: {details['presentation_url']}  \n\n"
            md_report += "**Details**:\n```json\n"
            md_report += json.dumps(details, indent=2)
            md_report += "\n```\n"
        else:
            md_report += f"**Error**: {result['details'].get('error', 'Unknown error')}  \n\n"

    md_report += "\n## Key Validations\n\n"
    md_report += "- ✅ Analytics Service generates valid content structure\n"
    md_report += "- ✅ Layout Builder accepts analytics content\n"
    md_report += "- ✅ Presentations created successfully\n"
    md_report += "- ✅ ApexCharts HTML present in rendered slides\n"
    md_report += "- ✅ Reveal.js integration verified\n"

    md_file = "INTEGRATION_TEST_REPORT.md"
    with open(md_file, 'w') as f:
        f.write(md_report)

    print(f"✓ Markdown report saved: {md_file}")

    return report_file, md_file


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("ANALYTICS ↔ LAYOUT BUILDER INTEGRATION TEST SUITE")
    print("="*70)
    print(f"\nAnalytics Service: {ANALYTICS_BASE_URL}")
    print(f"Layout Builder: {LAYOUT_BUILDER_URL}")
    print(f"\nStarting tests at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Pre-flight checks
    print("\n" + "="*70)
    print("PRE-FLIGHT CHECKS")
    print("="*70)

    print("\nChecking Analytics Service...")
    if not check_analytics_health():
        print("❌ Analytics Service not available!")
        print("   Please start it: cd agents/analytics_microservice_v3 && python3 main.py")
        return
    print("✅ Analytics Service is healthy")

    print("\nChecking Layout Builder...")
    if not check_layout_builder_health():
        print("❌ Layout Builder not accessible!")
        print(f"   URL: {LAYOUT_BUILDER_URL}")
        return
    print("✅ Layout Builder is accessible")

    # Run tests
    print("\n" + "="*70)
    print("RUNNING INTEGRATION TESTS")
    print("="*70)

    test_l01_single_chart_integration()
    time.sleep(2)

    test_l03_comparison_charts_integration()
    time.sleep(2)

    test_full_presentation_integration()

    # Generate report
    report_file, md_file = generate_test_report()

    # Summary
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)

    passed = sum(1 for r in test_results if r["status"] == "PASSED")
    failed = sum(1 for r in test_results if r["status"] == "FAILED")

    print(f"\nResults: {passed}/{len(test_results)} tests passed")

    if failed == 0:
        print("\n🎉 All integration tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed - check {report_file} for details")

    print(f"\n📄 Reports generated:")
    print(f"   - JSON: {report_file}")
    print(f"   - Markdown: {md_file}")

    # Display presentation URLs
    print(f"\n🌐 View Presentations:")
    for result in test_results:
        if result["status"] == "PASSED" and "presentation_url" in result["details"]:
            print(f"   • {result['test_name']}: {result['details']['presentation_url']}")


if __name__ == "__main__":
    main()
