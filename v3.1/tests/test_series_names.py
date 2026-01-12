"""
Test for custom series names in multi-series charts.

Verifies that the synthetic data generator correctly uses custom series names
when generating data for multi-series chart types (bar_grouped, bar_stacked, area_stacked).
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synthetic_data_generator import SyntheticDataGenerator


def test_custom_series_names():
    """Test that custom series names are used in multi-series charts."""
    print("\n" + "="*60)
    print("TEST: Custom Series Names in Multi-Series Charts")
    print("="*60)

    generator = SyntheticDataGenerator()

    # Test case 1: area_stacked with custom series names
    print("\n1. Testing area_stacked with custom series names...")
    custom_names = ["North America", "EMEA", "APAC"]

    data = generator.generate(
        chart_type="area_stacked",
        narrative="Show quarterly revenue by region",
        num_points=4,
        series_names=custom_names
    )

    assert 'datasets' in data, "Expected multi-series format with 'datasets' key"
    assert len(data['datasets']) == len(custom_names), f"Expected {len(custom_names)} datasets, got {len(data['datasets'])}"

    for i, dataset in enumerate(data['datasets']):
        assert dataset['label'] == custom_names[i], f"Expected series name '{custom_names[i]}', got '{dataset['label']}'"

    print(f"   ✅ PASS - Generated {len(data['datasets'])} series with custom names:")
    for ds in data['datasets']:
        print(f"      - {ds['label']}: {len(ds['data'])} data points")

    # Test case 2: bar_grouped with custom series names
    print("\n2. Testing bar_grouped with custom series names...")
    custom_names_2 = ["Desktop", "Mobile", "Tablet", "Smart TV"]

    data2 = generator.generate(
        chart_type="bar_grouped",
        narrative="Show market share by device type",
        num_points=5,
        series_names=custom_names_2
    )

    assert 'datasets' in data2, "Expected multi-series format with 'datasets' key"
    assert len(data2['datasets']) == len(custom_names_2), f"Expected {len(custom_names_2)} datasets"

    for i, dataset in enumerate(data2['datasets']):
        assert dataset['label'] == custom_names_2[i], f"Expected series name '{custom_names_2[i]}', got '{dataset['label']}'"

    print(f"   ✅ PASS - Generated {len(data2['datasets'])} series with custom names:")
    for ds in data2['datasets']:
        print(f"      - {ds['label']}: {len(ds['data'])} data points")

    # Test case 3: bar_stacked WITHOUT custom names (should default to Series A, B, C)
    print("\n3. Testing bar_stacked WITHOUT custom series names (defaults)...")

    data3 = generator.generate(
        chart_type="bar_stacked",
        narrative="Show quarterly sales breakdown",
        num_points=4
    )

    assert 'datasets' in data3, "Expected multi-series format with 'datasets' key"
    assert len(data3['datasets']) >= 2, "Expected at least 2 datasets"

    # Check that default names are used (Series A, Series B, etc.)
    for i, dataset in enumerate(data3['datasets']):
        expected_default = f"Series {chr(65+i)}"
        assert dataset['label'] == expected_default, f"Expected default '{expected_default}', got '{dataset['label']}'"

    print(f"   ✅ PASS - Generated {len(data3['datasets'])} series with default names:")
    for ds in data3['datasets']:
        print(f"      - {ds['label']}: {len(ds['data'])} data points")

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    return True


def test_single_series_name():
    """Test with a single custom series name."""
    print("\n" + "="*60)
    print("TEST: Single Series Name")
    print("="*60)

    generator = SyntheticDataGenerator()

    data = generator.generate(
        chart_type="area_stacked",
        narrative="Show revenue trend",
        num_points=4,
        series_names=["Revenue"]
    )

    assert 'datasets' in data, "Expected multi-series format"
    assert len(data['datasets']) == 1, f"Expected 1 dataset, got {len(data['datasets'])}"
    assert data['datasets'][0]['label'] == "Revenue", f"Expected 'Revenue', got '{data['datasets'][0]['label']}'"

    print(f"   ✅ PASS - Generated single series: {data['datasets'][0]['label']}")
    return True


if __name__ == "__main__":
    try:
        test_custom_series_names()
        test_single_series_name()
        print("\n🎉 All series name tests completed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
