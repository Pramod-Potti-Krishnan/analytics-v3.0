"""
Test script for verifying Director format data transformation.

This tests the actual data format that Director Agent v3.4 sends:
[
    {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
    {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88},
    ...
]

Must be transformed to Chart.js format:
{
    "labels": ["Q1", "Q2", ...],
    "datasets": [
        {"label": "North America", "data": [124, 145, ...]},
        {"label": "EMEA", "data": [98, 112, ...]},
        {"label": "APAC", "data": [75, 88, ...]}
    ]
}
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chartjs_generator import ChartJSGenerator


def test_bar_grouped_director_format():
    """Test bar_grouped with Director's actual data format."""
    print("\n" + "="*60)
    print("Testing bar_grouped with DIRECTOR FORMAT...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    # This is EXACTLY what Director sends
    director_data = [
        {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
        {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88},
        {"label": "Q3", "North America": 165, "EMEA": 128, "APAC": 105},
        {"label": "Q4", "North America": 180, "EMEA": 145, "APAC": 125}
    ]

    print(f"Input data format: {director_data[0]}")

    try:
        html = generator.generate_grouped_bar_chart(
            data=director_data,
            height=600,
            chart_id="test-bar-grouped"
        )

        assert len(html) > 1000, f"HTML too short: {len(html)} chars"
        assert "canvas" in html.lower(), "No canvas element found"
        assert "chart" in html.lower(), "No chart reference found"

        # Check for data in output
        assert "North America" in html, "Series 'North America' not found in HTML"
        assert "EMEA" in html, "Series 'EMEA' not found in HTML"
        assert "APAC" in html, "Series 'APAC' not found in HTML"

        print("✅ PASS - bar_grouped with Director format")
        print(f"   HTML length: {len(html)} chars")
        print(f"   Contains all 3 series: North America, EMEA, APAC")
        return True

    except Exception as e:
        print(f"❌ FAIL - bar_grouped: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_bar_stacked_director_format():
    """Test bar_stacked with Director's actual data format."""
    print("\n" + "="*60)
    print("Testing bar_stacked with DIRECTOR FORMAT...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    director_data = [
        {"label": "Q1", "Operations": 45, "Sales": 35, "R&D": 20, "Marketing": 15},
        {"label": "Q2", "Operations": 48, "Sales": 40, "R&D": 25, "Marketing": 18},
        {"label": "Q3", "Operations": 52, "Sales": 45, "R&D": 30, "Marketing": 22},
        {"label": "Q4", "Operations": 55, "Sales": 50, "R&D": 35, "Marketing": 25}
    ]

    print(f"Input data format: {director_data[0]}")

    try:
        html = generator.generate_stacked_bar_chart(
            data=director_data,
            height=600,
            chart_id="test-bar-stacked"
        )

        assert len(html) > 1000, f"HTML too short: {len(html)} chars"
        assert "canvas" in html.lower(), "No canvas element found"
        assert "stacked" in html.lower() or "chart" in html.lower(), "No stacked reference"

        print("✅ PASS - bar_stacked with Director format")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - bar_stacked: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_area_stacked_director_format():
    """Test area_stacked with Director's actual data format."""
    print("\n" + "="*60)
    print("Testing area_stacked with DIRECTOR FORMAT...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    director_data = [
        {"label": "Q1", "Product A": 120, "Product B": 95, "Product C": 70},
        {"label": "Q2", "Product A": 145, "Product B": 110, "Product C": 85},
        {"label": "Q3", "Product A": 170, "Product B": 130, "Product C": 100},
        {"label": "Q4", "Product A": 200, "Product B": 155, "Product C": 120}
    ]

    print(f"Input data format: {director_data[0]}")

    try:
        html = generator.generate_stacked_area_chart(
            data=director_data,
            height=600,
            chart_id="test-area-stacked"
        )

        assert len(html) > 1000, f"HTML too short: {len(html)} chars"
        assert "canvas" in html.lower(), "No canvas element found"

        print("✅ PASS - area_stacked with Director format")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - area_stacked: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_mixed_director_format():
    """Test mixed chart with Director's actual data format."""
    print("\n" + "="*60)
    print("Testing mixed chart with DIRECTOR FORMAT...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    director_data = [
        {"label": "Q1", "Revenue": 120, "Costs": 80},
        {"label": "Q2", "Revenue": 150, "Costs": 90},
        {"label": "Q3", "Revenue": 180, "Costs": 100},
        {"label": "Q4", "Revenue": 200, "Costs": 110}
    ]

    print(f"Input data format: {director_data[0]}")

    try:
        html = generator.generate_mixed_chart(
            data=director_data,
            height=600,
            chart_id="test-mixed"
        )

        assert len(html) > 1000, f"HTML too short: {len(html)} chars"
        assert "canvas" in html.lower(), "No canvas element found"

        print("✅ PASS - mixed chart with Director format")
        print(f"   HTML length: {len(html)} chars")
        return True

    except Exception as e:
        print(f"❌ FAIL - mixed chart: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_transformation_logic():
    """Test the transformation function directly."""
    print("\n" + "="*60)
    print("Testing _transform_director_to_chartjs() function...")
    print("="*60)

    generator = ChartJSGenerator(theme="professional")

    # Director format
    director_data = [
        {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
        {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88}
    ]

    result = generator._transform_director_to_chartjs(director_data)

    print("Input (Director format):")
    print(f"  {director_data}")
    print("\nOutput (Chart.js format):")
    print(f"  labels: {result.get('labels', [])}")
    print(f"  datasets:")
    for ds in result.get('datasets', []):
        print(f"    - {ds.get('label')}: {ds.get('data')}")

    # Verify transformation
    assert 'labels' in result, "Missing 'labels' key"
    assert 'datasets' in result, "Missing 'datasets' key"
    assert result['labels'] == ['Q1', 'Q2'], f"Wrong labels: {result['labels']}"
    assert len(result['datasets']) == 3, f"Wrong dataset count: {len(result['datasets'])}"

    # Check series
    series_names = [ds['label'] for ds in result['datasets']]
    assert 'North America' in series_names, "Missing North America series"
    assert 'EMEA' in series_names, "Missing EMEA series"
    assert 'APAC' in series_names, "Missing APAC series"

    print("\n✅ PASS - Transformation logic correct")
    print("   ✓ labels extracted correctly")
    print("   ✓ 3 datasets created")
    print("   ✓ All series present: North America, EMEA, APAC")

    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("DIRECTOR FORMAT DATA TRANSFORMATION TESTS")
    print("="*70)
    print("\nTesting with ACTUAL Director Agent v3.4 data format:")
    print('[{"label": "Q1", "Series1": 100, "Series2": 80}, ...]')
    print("\nMust transform to Chart.js format:")
    print('{labels: ["Q1", ...], datasets: [{label: "Series1", data: [100, ...]}, ...]}')

    results = {
        "transformation_logic": test_transformation_logic(),
        "bar_grouped": test_bar_grouped_director_format(),
        "bar_stacked": test_bar_stacked_director_format(),
        "area_stacked": test_area_stacked_director_format(),
        "mixed": test_mixed_director_format()
    }

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe transformation correctly handles Director's data format.")
        print("\nNext steps:")
        print("1. Test with Layout Service integration")
        print("2. Generate standalone HTML samples")
        print("3. Verify visual rendering in browser")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
