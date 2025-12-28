"""
Test script for verifying all P0 chart fixes.

This tests the 5 broken charts identified in the Director's test report:
1. bar_grouped - Multi-series data structure bug
2. bar_stacked - Multi-series data structure bug
3. area_stacked - Multi-series data structure bug
4. mixed - Multi-series data structure bug
5. d3_sunburst - Data format mismatch

All charts should now properly handle the array format data structure.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chartjs_generator import ChartJSGenerator

def test_bar_grouped():
    """Test bar_grouped chart with multi-series data."""
    print("\n" + "="*60)
    print("Testing bar_grouped chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    # This is the format the Director sends (array with datasets inside)
    data = [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "North America", "data": [124, 145, 165, 180]},
            {"label": "EMEA", "data": [98, 112, 128, 145]},
            {"label": "APAC", "data": [75, 88, 105, 125]}
        ]
    }]

    try:
        html = generator.generate_grouped_bar_chart(
            data=data,
            height=600,
            chart_id="test-bar-grouped"
        )

        # Check that HTML was generated
        assert len(html) > 1000, "HTML too short"
        assert "canvas" in html.lower(), "No canvas element found"
        assert "chart" in html.lower(), "No chart reference found"

        print("✅ PASS - bar_grouped chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - bar_grouped chart failed: {str(e)}")
        return False


def test_bar_stacked():
    """Test bar_stacked chart with multi-series data."""
    print("\n" + "="*60)
    print("Testing bar_stacked chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    data = [{
        "labels": ["Product A", "Product B", "Product C"],
        "datasets": [
            {"label": "Revenue", "data": [120, 150, 180]},
            {"label": "Costs", "data": [80, 90, 100]},
            {"label": "Profit", "data": [40, 60, 80]}
        ]
    }]

    try:
        html = generator.generate_stacked_bar_chart(
            data=data,
            height=600,
            chart_id="test-bar-stacked"
        )

        assert len(html) > 1000, "HTML too short"
        assert "canvas" in html.lower(), "No canvas element found"
        assert "stacked" in html.lower() or "chart" in html.lower(), "No stacked chart reference"

        print("✅ PASS - bar_stacked chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - bar_stacked chart failed: {str(e)}")
        return False


def test_area_stacked():
    """Test area_stacked chart with multi-series data."""
    print("\n" + "="*60)
    print("Testing area_stacked chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    data = [{
        "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
        "datasets": [
            {"label": "Desktop", "data": [100, 120, 140, 160, 180]},
            {"label": "Mobile", "data": [80, 90, 110, 130, 150]},
            {"label": "Tablet", "data": [40, 50, 60, 70, 80]}
        ]
    }]

    try:
        html = generator.generate_stacked_area_chart(
            data=data,
            height=600,
            chart_id="test-area-stacked"
        )

        assert len(html) > 1000, "HTML too short"
        assert "canvas" in html.lower(), "No canvas element found"

        print("✅ PASS - area_stacked chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - area_stacked chart failed: {str(e)}")
        return False


def test_mixed():
    """Test mixed chart (line + bar) with multi-series data."""
    print("\n" + "="*60)
    print("Testing mixed chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    data = [{
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"type": "line", "label": "Revenue", "data": [120, 150, 180, 200]},
            {"type": "bar", "label": "Costs", "data": [80, 90, 100, 110]}
        ]
    }]

    try:
        html = generator.generate_mixed_chart(
            data=data,
            height=600,
            chart_id="test-mixed"
        )

        assert len(html) > 1000, "HTML too short"
        assert "canvas" in html.lower(), "No canvas element found"

        print("✅ PASS - mixed chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - mixed chart failed: {str(e)}")
        return False


def test_d3_sunburst():
    """Test d3_sunburst chart with array format data."""
    print("\n" + "="*60)
    print("Testing d3_sunburst chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    # This is the format the Director sends (array of label-value objects)
    data = [
        {"label": "Engineering", "value": 800000},
        {"label": "Sales", "value": 600000},
        {"label": "Marketing", "value": 400000},
        {"label": "Operations", "value": 350000},
        {"label": "Finance", "value": 200000},
        {"label": "HR", "value": 150000}
    ]

    try:
        html = generator.generate_d3_sunburst_chart(
            data=data,
            height=720,
            chart_id="test-d3-sunburst"
        )

        assert len(html) > 1000, "HTML too short"
        assert "d3" in html.lower(), "No D3.js reference found"
        assert "sunburst" in html.lower() or "partition" in html, "No sunburst reference"

        print("✅ PASS - d3_sunburst chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - d3_sunburst chart failed: {str(e)}")
        return False


def test_d3_treemap():
    """Test d3_treemap chart with array format data (preventive fix)."""
    print("\n" + "="*60)
    print("Testing d3_treemap chart...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    # This is the format the Director sends
    data = [
        {"label": "Product A", "value": 450000},
        {"label": "Product B", "value": 380000},
        {"label": "Product C", "value": 320000},
        {"label": "Product D", "value": 250000}
    ]

    try:
        html = generator.generate_d3_treemap_chart(
            data=data,
            height=720,
            chart_id="test-d3-treemap"
        )

        assert len(html) > 1000, "HTML too short"
        assert "d3" in html.lower(), "No D3.js reference found"
        assert "treemap" in html.lower(), "No treemap reference"

        print("✅ PASS - d3_treemap chart generated successfully")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - d3_treemap chart failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ANALYTICS MICROSERVICE v3 - P0 CHART FIXES VERIFICATION")
    print("="*70)
    print("\nTesting all 5 broken charts identified in Director's test report:")
    print("1. bar_grouped - Multi-series data structure bug")
    print("2. bar_stacked - Multi-series data structure bug")
    print("3. area_stacked - Multi-series data structure bug")
    print("4. mixed - Multi-series data structure bug")
    print("5. d3_sunburst - Data format mismatch")
    print("\nAlso testing:")
    print("6. d3_treemap - Preventive fix for same data format issue")

    results = {
        "bar_grouped": test_bar_grouped(),
        "bar_stacked": test_bar_stacked(),
        "area_stacked": test_area_stacked(),
        "mixed": test_mixed(),
        "d3_sunburst": test_d3_sunburst(),
        "d3_treemap": test_d3_treemap()
    }

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for chart, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {chart}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! All P0 chart fixes are working correctly.")
        print("\nNext steps:")
        print("1. Start the analytics service: python main.py")
        print("2. Run integration tests with Director Agent v3.4")
        print("3. Verify charts render correctly in Layout Service")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit(main())
