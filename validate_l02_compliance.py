"""
L02 Layout Builder Compliance Validation Script

Tests Chart.js implementation against Layout Builder requirements.
"""

import asyncio
from agent import process_analytics_slide
from chartjs_generator import ChartJSGenerator
from layout_assembler import L02LayoutAssembler


def validate_chartjs_inline_script():
    """Validate Chart.js generates proper inline script HTML."""
    print("\n=== Test 1: Chart.js Inline Script Generation ===")

    generator = ChartJSGenerator(theme="professional")

    # Test data
    test_data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [125000, 145000, 162000, 195000],
        "series_name": "Revenue",
        "format": "currency"
    }

    # Generate line chart with inline script mode
    html = generator.generate_line_chart(
        data=test_data,
        height=720,
        chart_id="test-chart-001",
        output_mode="inline_script"
    )

    # Validation checks
    checks = {
        "Has l02-chart-container class": 'class="l02-chart-container"' in html,
        "Has correct dimensions": 'width: 1260px; height: 720px' in html,
        "Has position: relative": 'position: relative' in html,
        "Has background: white (Fix 1)": 'background: white' in html,
        "Has padding: 20px (Fix 1)": 'padding: 20px' in html,
        "Has box-sizing: border-box (Fix 1)": 'box-sizing: border-box' in html,
        "Has canvas element": '<canvas id="test-chart-001">' in html,
        "Has inline script tag": '<script>' in html and '</script>' in html,
        "Has IIFE wrapper": '(function() {' in html and '})();' in html,
        "Has maintainAspectRatio: false": 'maintainAspectRatio' in html and 'false' in html,
        "Has Chart instance creation": 'new Chart(ctx,' in html,
        "Stores chart instance": 'window.chartInstances' in html
    }

    all_passed = True
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n✓ Chart.js inline script generation: COMPLIANT (12/12 checks)")
    else:
        print("\n✗ Chart.js inline script generation: FAILED")
        print("\nGenerated HTML (first 500 chars):")
        print(html[:500])

    return all_passed


def validate_layout_assembler_typography():
    """Validate layout assembler uses correct Layout Builder typography."""
    print("\n=== Test 2: Layout Assembler Typography ===")

    assembler = L02LayoutAssembler(theme="professional")

    test_text = "Revenue increased 56% year-over-year, driven by strong Q4 performance."

    html = assembler.assemble_observations_html(
        insights_text=test_text,
        title="Key Insights"
    )

    # Validation checks
    checks = {
        "Has correct heading font-size (20px)": 'font-size: 20px' in html,
        "Has correct heading font-weight (600)": 'font-weight: 600' in html,
        "Has correct heading margin (0 0 16px 0)": 'margin: 0 0 16px 0' in html,
        "Has correct heading color (#1f2937)": 'color: #1f2937' in html,
        "Has correct heading line-height (1.3) (Fix 4)": 'line-height: 1.3' in html,
        "Has correct body font-size (16px)": 'font-size: 16px' in html,
        "Has correct body line-height (1.6)": 'line-height: 1.6' in html,
        "Has correct body color (#374151)": 'color: #374151' in html,
        "Has correct background (#f8f9fa)": 'background: #f8f9fa' in html,
        "Has border-radius (8px)": 'border-radius: 8px' in html,
        "Has fixed height (720px) (Fix 2)": 'height: 720px' in html,
        "Has asymmetric padding (40px 32px) (Fix 3)": 'padding: 40px 32px' in html,
        "Uses <p> tags for paragraphs (Fix 5)": '<p style="font-family' in html and '</p>' in html
    }

    all_passed = True
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n✓ Layout assembler typography: COMPLIANT (13/13 checks)")
    else:
        print("\n✗ Layout assembler typography: FAILED")
        print("\nGenerated HTML (first 500 chars):")
        print(html[:500])

    return all_passed


async def validate_l02_integration():
    """Validate full L02 flow with Chart.js and layout assembler."""
    print("\n=== Test 3: L02 Integration (process_analytics_slide) ===")

    # Test request data
    request_data = {
        "presentation_id": "test_pres_001",
        "slide_id": "slide_002",
        "slide_number": 2,
        "narrative": "Show quarterly revenue growth trends",
        "data": [
            {"label": "Q1 2024", "value": 125000},
            {"label": "Q2 2024", "value": 145000},
            {"label": "Q3 2024", "value": 162000},
            {"label": "Q4 2024", "value": 195000}
        ],
        "context": {
            "theme": "professional",
            "audience": "executives",
            "slide_title": "Quarterly Revenue Growth",
            "subtitle": "FY 2024 Performance",
            "presentation_name": "Q4 Business Review",
            "company_logo": "📊"
        },
        "constraints": {}
    }

    # Process L02 slide
    result = await process_analytics_slide(
        analytics_type="revenue_over_time",
        layout="L02",
        request_data=request_data,
        storage=None
    )

    # Extract content
    content = result.get("content", {})
    metadata = result.get("metadata", {})
    element_3 = content.get("element_3", "")  # Chart
    element_2 = content.get("element_2", "")  # Observations

    # Validation checks
    checks = {
        "Result has content": bool(content),
        "Result has metadata": bool(metadata),
        "Metadata shows chartjs library": metadata.get("chart_library") == "chartjs",
        "Metadata shows L02 layout": metadata.get("layout") == "L02",
        "element_3 has Chart.js HTML": "new Chart(ctx," in element_3,
        "element_3 has inline script": "<script>" in element_3,
        "element_3 has IIFE wrapper": "(function() {" in element_3,
        "element_2 has styled observations": 'class="l02-observations-panel"' in element_2,
        "element_2 has correct heading size": 'font-size: 20px' in element_2,
        "element_2 has correct body size": 'font-size: 16px' in element_2,
        "Content has required fields": all(k in content for k in ["slide_title", "element_1", "element_3", "element_2"])
    }

    all_passed = True
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check}")
        if not result:
            all_passed = False

    if all_passed:
        print("\n✓ L02 integration: COMPLIANT (11/11 checks)")
    else:
        print("\n✗ L02 integration: FAILED")
        print(f"\nMetadata: {metadata}")
        print(f"\nelement_3 (first 300 chars): {element_3[:300]}")
        print(f"\nelement_2 (first 300 chars): {element_2[:300]}")

    return all_passed


async def main():
    """Run all validation tests."""
    print("=" * 70)
    print("L02 LAYOUT BUILDER COMPLIANCE VALIDATION")
    print("=" * 70)

    results = []

    # Test 1: Chart.js inline script generation
    results.append(validate_chartjs_inline_script())

    # Test 2: Layout assembler typography
    results.append(validate_layout_assembler_typography())

    # Test 3: Full L02 integration
    results.append(await validate_l02_integration())

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL VALIDATION CHECKS PASSED - 100% LAYOUT BUILDER COMPLIANT")
        print(f"   Total Checks: {12 + 13 + 11}/36 (12 Chart.js + 13 Typography + 11 Integration)")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
