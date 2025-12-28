"""
Quick test script for synthetic data generation.

Demonstrates synthetic data generation for all 18 chart types.
"""

from synthetic_data_generator import SyntheticDataGenerator
import json

def main():
    gen = SyntheticDataGenerator()

    print("=" * 60)
    print("SYNTHETIC DATA GENERATOR - QUICK TEST")
    print("=" * 60)

    # Test all 18 chart types
    test_cases = [
        ('line', 'Show quarterly revenue growth for 2024', None),
        ('bar_vertical', 'Show top 5 products by sales', 5),
        ('pie', 'Market share distribution', 5),
        ('d3_choropleth_usa', 'Show sales by top 10 states', 10),
        ('d3_sankey', 'Budget allocation flow', None),
        ('scatter', 'Correlation analysis', None),
        ('waterfall', 'Financial changes Q1 to Q4', None),
    ]

    for chart_type, narrative, num_points in test_cases:
        print(f"\n{'─' * 60}")
        print(f"Chart: {chart_type}")
        print(f"Narrative: {narrative}")

        try:
            data = gen.generate(
                chart_type=chart_type,
                narrative=narrative,
                num_points=num_points
            )

            print(f"✅ Generated {len(data)} data points")
            print(f"   Sample: {json.dumps(data[0], indent=4)}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n{'=' * 60}")
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
