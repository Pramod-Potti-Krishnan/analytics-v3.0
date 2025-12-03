#!/usr/bin/env python3
"""
Test script to verify scatter and bubble chart fixes.

Tests:
1. Synthetic data generation - no duplicate keys, proper y values
2. Data structure has correct fields (label, x, y, r for bubble)
3. Frontend data format matches backend expectations
"""

import sys
import json
from synthetic_data_generator import SyntheticDataGenerator


def test_scatter_data_generation():
    """Test scatter chart synthetic data generation."""
    print("\n" + "="*60)
    print("TEST 1: Scatter Chart Data Generation")
    print("="*60)

    generator = SyntheticDataGenerator()
    data = generator.generate(
        chart_type='scatter',
        narrative='Show correlation between sales and revenue',
        num_points=8
    )

    print(f"\n✅ Generated {len(data)} scatter data points")
    print(f"\n📊 Sample data (first 3 points):")
    for i, point in enumerate(data[:3]):
        print(f"  Point {i+1}: {json.dumps(point, indent=4)}")

    # Validation
    errors = []

    # Check structure
    for i, point in enumerate(data):
        # Should have: label, x, y
        if 'label' not in point:
            errors.append(f"Point {i}: Missing 'label' field")
        if 'x' not in point:
            errors.append(f"Point {i}: Missing 'x' field")
        if 'y' not in point:
            errors.append(f"Point {i}: Missing 'y' field")

        # Should NOT have: value key (that was the bug)
        if 'value' in point:
            errors.append(f"Point {i}: Has duplicate 'value' field (should only have x, y, label)")

        # Y should NOT be zero for all points (would indicate synthetic data issue)
        if 'y' in point and point['y'] == 0:
            # It's ok if ONE point is zero, but not all
            pass

    # Check if ALL y values are zero (the main bug)
    all_y_zero = all(point.get('y', 0) == 0 for point in data)
    if all_y_zero:
        errors.append("❌ BUG: All y values are 0 (synthetic data generation failed)")
    else:
        print(f"\n✅ Y values are properly distributed (not all zero)")

    # Check for duplicate 'value' key
    has_value_key = any('value' in point for point in data)
    if has_value_key:
        errors.append("❌ BUG: Data contains duplicate 'value' key")
    else:
        print(f"✅ No duplicate 'value' key found")

    # Check required fields
    has_all_fields = all('label' in point and 'x' in point and 'y' in point for point in data)
    if has_all_fields:
        print(f"✅ All points have required fields (label, x, y)")
    else:
        errors.append("❌ Some points missing required fields")

    # Print results
    if errors:
        print(f"\n❌ FAILED: {len(errors)} errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\n✅ PASSED: Scatter chart data generation is correct!")
        return True


def test_bubble_data_generation():
    """Test bubble chart synthetic data generation."""
    print("\n" + "="*60)
    print("TEST 2: Bubble Chart Data Generation")
    print("="*60)

    generator = SyntheticDataGenerator()
    data = generator.generate(
        chart_type='bubble',
        narrative='Show multidimensional product analysis',
        num_points=5
    )

    print(f"\n✅ Generated {len(data)} bubble data points")
    print(f"\n📊 Sample data (first 3 points):")
    for i, point in enumerate(data[:3]):
        print(f"  Point {i+1}: {json.dumps(point, indent=4)}")

    # Validation
    errors = []

    # Check structure
    for i, point in enumerate(data):
        # Should have: label, x, y, r
        if 'label' not in point:
            errors.append(f"Point {i}: Missing 'label' field")
        if 'x' not in point:
            errors.append(f"Point {i}: Missing 'x' field")
        if 'y' not in point:
            errors.append(f"Point {i}: Missing 'y' field")
        if 'r' not in point:
            errors.append(f"Point {i}: Missing 'r' field (bubble radius)")

        # Should NOT have: value key
        if 'value' in point:
            errors.append(f"Point {i}: Has duplicate 'value' field")

    # Check if ALL y values are zero
    all_y_zero = all(point.get('y', 0) == 0 for point in data)
    if all_y_zero:
        errors.append("❌ BUG: All y values are 0 (synthetic data generation failed)")
    else:
        print(f"\n✅ Y values are properly distributed (not all zero)")

    # Check for duplicate 'value' key
    has_value_key = any('value' in point for point in data)
    if has_value_key:
        errors.append("❌ BUG: Data contains duplicate 'value' key")
    else:
        print(f"✅ No duplicate 'value' key found")

    # Check required fields
    has_all_fields = all('label' in point and 'x' in point and 'y' in point and 'r' in point for point in data)
    if has_all_fields:
        print(f"✅ All points have required fields (label, x, y, r)")
    else:
        errors.append("❌ Some points missing required fields")

    # Print results
    if errors:
        print(f"\n❌ FAILED: {len(errors)} errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"\n✅ PASSED: Bubble chart data generation is correct!")
        return True


def test_backend_api_format():
    """Test that data format matches backend API expectations."""
    print("\n" + "="*60)
    print("TEST 3: Backend API Format Compatibility")
    print("="*60)

    generator = SyntheticDataGenerator()
    scatter_data = generator.generate(chart_type='scatter', num_points=5)
    bubble_data = generator.generate(chart_type='bubble', num_points=5)

    errors = []

    # Scatter data format
    print("\n📤 Scatter data format for API:")
    api_payload = {
        "chart_id": "chart-slide-001",
        "presentation_id": "test-001",
        "chart_type": "scatter",
        "data": scatter_data
    }
    print(f"  {json.dumps(api_payload, indent=2)[:200]}...")

    # Validate scatter format
    for point in scatter_data:
        if not isinstance(point.get('label'), str) or not point.get('label'):
            errors.append(f"Scatter: Invalid label (backend requires non-empty string)")
        if not isinstance(point.get('x'), (int, float)):
            errors.append(f"Scatter: Invalid x coordinate (must be number)")
        if not isinstance(point.get('y'), (int, float)):
            errors.append(f"Scatter: Invalid y coordinate (must be number)")

    if not errors:
        print(f"✅ Scatter data format matches backend ScatterBubbleDataPoint schema")

    # Bubble data format
    print("\n📤 Bubble data format for API:")
    api_payload = {
        "chart_id": "chart-slide-002",
        "presentation_id": "test-002",
        "chart_type": "bubble",
        "data": bubble_data
    }
    print(f"  {json.dumps(api_payload, indent=2)[:200]}...")

    # Validate bubble format
    for point in bubble_data:
        if not isinstance(point.get('label'), str) or not point.get('label'):
            errors.append(f"Bubble: Invalid label (backend requires non-empty string)")
        if not isinstance(point.get('x'), (int, float)):
            errors.append(f"Bubble: Invalid x coordinate (must be number)")
        if not isinstance(point.get('y'), (int, float)):
            errors.append(f"Bubble: Invalid y coordinate (must be number)")
        if not isinstance(point.get('r'), (int, float)):
            errors.append(f"Bubble: Invalid r (radius) value (must be number)")

    if not errors:
        print(f"✅ Bubble data format matches backend ScatterBubbleDataPoint schema")
    else:
        print(f"\n❌ FAILED: {len(errors)} format errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"\n✅ PASSED: Data formats are compatible with backend API!")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🔬 SCATTER & BUBBLE CHART FIX VERIFICATION")
    print("="*60)
    print("\nTesting fixes for:")
    print("  1. Synthetic data generation (remove duplicate 'value' key)")
    print("  2. Y values should not all be zero")
    print("  3. Data format matches backend API expectations")

    results = []

    # Run tests
    results.append(("Scatter Data Generation", test_scatter_data_generation()))
    results.append(("Bubble Data Generation", test_bubble_data_generation()))
    results.append(("Backend API Format", test_backend_api_format()))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\n{'='*60}")
    if total_passed == total_tests:
        print(f"✅ ALL TESTS PASSED ({total_passed}/{total_tests})")
        print(f"{'='*60}\n")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({total_passed}/{total_tests} passed)")
        print(f"{'='*60}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
