"""
Systematic ApexCharts Formatter Testing Suite

Tests different formatter syntax variations to identify what works and what breaks.
Each test generates a presentation with line and bar charts using specific formatter patterns.

Run phases sequentially and validate each with UAT before proceeding.
"""

import requests
import json
from datetime import datetime
from apexcharts_generator import ApexChartsGenerator

LAYOUT_SERVICE_URL = "https://web-production-f0d13.up.railway.app"

# Track test results
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": []
}


def log_test_result(test_id, test_name, url, expected, notes=""):
    """Log test result for UAT tracking."""
    result = {
        "test_id": test_id,
        "test_name": test_name,
        "url": url,
        "expected": expected,
        "notes": notes,
        "uat_status": "pending"  # User will update this
    }
    test_results["tests"].append(result)

    # Save results after each test
    with open('formatter_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)


def create_test_presentation(test_id, test_name, line_chart_html, bar_chart_html):
    """Create presentation with specific chart HTML for testing."""

    presentation_data = {
        "title": f"Formatter Test {test_id}: {test_name}",
        "slides": [
            {
                "layout": "L29",
                "content": {
                    "slide_title": f"Test {test_id}",
                    "element_1": test_name,
                    "element_2": "UAT: Check if charts render correctly",
                    "presentation_name": f"Test {test_id}",
                    "company_logo": "🧪"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Line Chart Test",
                    "element_1": test_name,
                    "element_3": line_chart_html,
                    "element_2": "Expected: Line chart should render with formatter applied to y-axis and tooltips",
                    "presentation_name": f"Test {test_id}",
                    "company_logo": "🧪"
                }
            },
            {
                "layout": "L02",
                "content": {
                    "slide_title": "Bar Chart Test",
                    "element_1": test_name,
                    "element_3": bar_chart_html,
                    "element_2": "Expected: Bar chart should render with formatter applied to data labels, y-axis, and tooltips",
                    "presentation_name": f"Test {test_id}",
                    "company_logo": "🧪"
                }
            }
        ]
    }

    # Send to Layout Builder
    response = requests.post(
        f"{LAYOUT_SERVICE_URL}/api/presentations",
        json=presentation_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code in [200, 201]:
        result = response.json()
        presentation_id = result.get('id')
        presentation_url = f"{LAYOUT_SERVICE_URL}/p/{presentation_id}"
        return presentation_id, presentation_url
    else:
        print(f"❌ Failed to create test {test_id}: {response.status_code}")
        return None, None


# =============================================================================
# PHASE 1: BASELINE SIMPLIFICATION TESTS
# =============================================================================

def test_1a_string_concatenation():
    """Test 1A: Remove template literal, use string concatenation."""
    print("\n" + "="*70)
    print("TEST 1A: String Concatenation (No Template Literal)")
    print("="*70)
    print("Hypothesis: Template literals with $${} are breaking ApexCharts parser")
    print("Change: (val) => `$${...}` → (val) => '$' + ...")
    print()

    generator = ApexChartsGenerator(theme="professional")

    # Override formatters with string concatenation
    original_get_value_formatter = generator._get_value_formatter
    original_get_data_label_formatter = generator._get_data_label_formatter
    original_get_tooltip_formatter = generator._get_tooltip_formatter

    def custom_value_formatter(data):
        if data.get("format") == "currency":
            return "(val) => '$' + (Number(val)/1000).toFixed(0) + 'K'"
        return original_get_value_formatter(data)

    def custom_data_label_formatter(data):
        if data.get("format") == "currency":
            return "(val) => '$' + (Number(val)/1000).toFixed(0) + 'K'"
        return original_get_data_label_formatter(data)

    def custom_tooltip_formatter(data):
        if data.get("format") == "currency":
            return "(val) => '$' + Number(val).toLocaleString()"
        return original_get_tooltip_formatter(data)

    generator._get_value_formatter = custom_value_formatter
    generator._get_data_label_formatter = custom_data_label_formatter
    generator._get_tooltip_formatter = custom_tooltip_formatter

    # Generate charts
    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=720,
        chart_id="test-1a-line"
    )

    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450000, 380000, 290000, 220000],
            "format": "currency"
        },
        height=720,
        chart_id="test-1a-bar"
    )

    presentation_id, url = create_test_presentation(
        "1A",
        "String Concatenation (No Template Literal)",
        line_html,
        bar_html
    )

    if url:
        print(f"✅ Test 1A Created: {url}")
        print(f"   Formatter: (val) => '$' + (Number(val)/1000).toFixed(0) + 'K'")
        print(f"\n📋 UAT Checklist:")
        print(f"   [ ] Do both charts render?")
        print(f"   [ ] Are values formatted as currency with K suffix?")
        print(f"   [ ] Any console errors?")

        log_test_result(
            "1A",
            "String Concatenation",
            url,
            "Both charts render with currency formatting"
        )

        return url

    return None


def test_1b_predivided_values():
    """Test 1B: Pre-divide data values, use simpler formatter."""
    print("\n" + "="*70)
    print("TEST 1B: Pre-Divided Values (Simpler Formatter)")
    print("="*70)
    print("Hypothesis: Division operation in formatter is breaking parser")
    print("Change: values=[125000,...] → values=[125,...], formatter without /1000")
    print()

    generator = ApexChartsGenerator(theme="professional")

    # Override formatters to avoid division
    original_get_value_formatter = generator._get_value_formatter
    original_get_data_label_formatter = generator._get_data_label_formatter
    original_get_tooltip_formatter = generator._get_tooltip_formatter

    def custom_value_formatter(data):
        if data.get("format") == "currency":
            return "(val) => `$${Number(val).toFixed(0)}K`"
        return original_get_value_formatter(data)

    def custom_data_label_formatter(data):
        if data.get("format") == "currency":
            return "(val) => `$${Number(val).toFixed(0)}K`"
        return original_get_data_label_formatter(data)

    def custom_tooltip_formatter(data):
        if data.get("format") == "currency":
            return "(val) => `$${Number(val).toFixed(0)}K`"
        return original_get_tooltip_formatter(data)

    generator._get_value_formatter = custom_value_formatter
    generator._get_data_label_formatter = custom_data_label_formatter
    generator._get_tooltip_formatter = custom_tooltip_formatter

    # Generate charts with PRE-DIVIDED values
    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125, 145, 178, 195],  # Already in thousands
            "format": "currency"
        },
        height=720,
        chart_id="test-1b-line"
    )

    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450, 380, 290, 220],  # Already in thousands
            "format": "currency"
        },
        height=720,
        chart_id="test-1b-bar"
    )

    presentation_id, url = create_test_presentation(
        "1B",
        "Pre-Divided Values (No Division in Formatter)",
        line_html,
        bar_html
    )

    if url:
        print(f"✅ Test 1B Created: {url}")
        print(f"   Formatter: (val) => `$${Number(val).toFixed(0)}K`")
        print(f"   Values: [125, 145, 178, 195] (pre-divided by 1000)")
        print(f"\n📋 UAT Checklist:")
        print(f"   [ ] Do both charts render?")
        print(f"   [ ] Are values shown as $125K, $145K, etc.?")
        print(f"   [ ] Any console errors?")

        log_test_result(
            "1B",
            "Pre-Divided Values",
            url,
            "Both charts render without division operation in formatter"
        )

        return url

    return None


def test_1c_match_donut_exactly():
    """Test 1C: Use exact donut chart formatter pattern."""
    print("\n" + "="*70)
    print("TEST 1C: Match Donut Pattern Exactly")
    print("="*70)
    print("Hypothesis: Simple ${Number(val).toFixed(X)} pattern works")
    print("Change: Use exact donut formatter syntax for line/bar charts")
    print()

    generator = ApexChartsGenerator(theme="professional")

    # Override formatters to match donut pattern
    original_get_value_formatter = generator._get_value_formatter
    original_get_data_label_formatter = generator._get_data_label_formatter
    original_get_tooltip_formatter = generator._get_tooltip_formatter

    def custom_formatter(data):
        # Match donut chart pattern exactly: (val) => `${Number(val).toFixed(1)}%`
        # But without % symbol
        return "(val) => `${Number(val).toFixed(0)}`"

    generator._get_value_formatter = custom_formatter
    generator._get_data_label_formatter = custom_formatter
    generator._get_tooltip_formatter = custom_formatter

    # Generate charts with normal values
    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125, 145, 178, 195],
            "format": "number"  # Use simple formatter
        },
        height=720,
        chart_id="test-1c-line"
    )

    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450, 380, 290, 220],
            "format": "number"  # Use simple formatter
        },
        height=720,
        chart_id="test-1c-bar"
    )

    presentation_id, url = create_test_presentation(
        "1C",
        "Match Donut Pattern Exactly",
        line_html,
        bar_html
    )

    if url:
        print(f"✅ Test 1C Created: {url}")
        print(f"   Formatter: (val) => `${Number(val).toFixed(0)}`")
        print(f"   Pattern: Exact match to working donut chart")
        print(f"\n📋 UAT Checklist:")
        print(f"   [ ] Do both charts render?")
        print(f"   [ ] Are values shown as plain numbers (125, 145, etc.)?")
        print(f"   [ ] Any console errors?")

        log_test_result(
            "1C",
            "Match Donut Pattern",
            url,
            "Both charts render with donut-style formatter"
        )

        return url

    return None


# =============================================================================
# PHASE 2: DOLLAR SIGN ESCAPING TESTS
# =============================================================================

def test_2a_escaped_dollar():
    """Test 2A: Escape the literal dollar sign."""
    print("\n" + "="*70)
    print("TEST 2A: Escaped Dollar Sign")
    print("="*70)
    print("Hypothesis: Literal $ needs escaping in template literal")
    print("Change: `$${...}` → `\\$${...}`")
    print()

    generator = ApexChartsGenerator(theme="professional")

    # Override formatters with escaped dollar
    def custom_formatter(data):
        if data.get("format") == "currency":
            return "(val) => `\\$${(Number(val)/1000).toFixed(0)}K`"
        return "(val) => Number(val).toLocaleString()"

    generator._get_value_formatter = custom_formatter
    generator._get_data_label_formatter = custom_formatter
    generator._get_tooltip_formatter = custom_formatter

    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=720,
        chart_id="test-2a-line"
    )

    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450000, 380000, 290000, 220000],
            "format": "currency"
        },
        height=720,
        chart_id="test-2a-bar"
    )

    presentation_id, url = create_test_presentation(
        "2A",
        "Escaped Dollar Sign",
        line_html,
        bar_html
    )

    if url:
        print(f"✅ Test 2A Created: {url}")
        print(f"   Formatter: (val) => `\\$${(Number(val)/1000).toFixed(0)}K`")
        print(f"\n📋 UAT Checklist:")
        print(f"   [ ] Do both charts render?")
        print(f"   [ ] Is $ symbol displayed correctly?")
        print(f"   [ ] Any console errors?")

        log_test_result(
            "2A",
            "Escaped Dollar",
            url,
            "Both charts render with escaped $ in template literal"
        )

        return url

    return None


def test_2b_no_dollar_symbol():
    """Test 2B: Remove dollar symbol entirely."""
    print("\n" + "="*70)
    print("TEST 2B: No Dollar Symbol")
    print("="*70)
    print("Hypothesis: $ symbol itself is problematic")
    print("Change: `$${...}K` → `${...}K`")
    print()

    generator = ApexChartsGenerator(theme="professional")

    # Override formatters without dollar symbol
    def custom_formatter(data):
        if data.get("format") == "currency":
            return "(val) => `${(Number(val)/1000).toFixed(0)}K`"
        return "(val) => Number(val).toLocaleString()"

    generator._get_value_formatter = custom_formatter
    generator._get_data_label_formatter = custom_formatter
    generator._get_tooltip_formatter = custom_formatter

    line_html = generator.generate_line_chart(
        data={
            "series_name": "Revenue",
            "labels": ["Q1", "Q2", "Q3", "Q4"],
            "values": [125000, 145000, 178000, 195000],
            "format": "currency"
        },
        height=720,
        chart_id="test-2b-line"
    )

    bar_html = generator.generate_bar_chart(
        data={
            "series_name": "Sales",
            "labels": ["Software", "Cloud", "Consulting", "Support"],
            "values": [450000, 380000, 290000, 220000],
            "format": "currency"
        },
        height=720,
        chart_id="test-2b-bar"
    )

    presentation_id, url = create_test_presentation(
        "2B",
        "No Dollar Symbol",
        line_html,
        bar_html
    )

    if url:
        print(f"✅ Test 2B Created: {url}")
        print(f"   Formatter: (val) => `${(Number(val)/1000).toFixed(0)}K`")
        print(f"\n📋 UAT Checklist:")
        print(f"   [ ] Do both charts render?")
        print(f"   [ ] Values shown as 125K, 145K (no $ symbol)?")
        print(f"   [ ] Any console errors?")

        log_test_result(
            "2B",
            "No Dollar Symbol",
            url,
            "Both charts render without $ symbol in formatter"
        )

        return url

    return None


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_phase_1():
    """Run Phase 1: Baseline Simplification Tests."""
    print("\n" + "#"*70)
    print("# PHASE 1: BASELINE SIMPLIFICATION TESTS")
    print("#"*70)

    results = {}

    results['1A'] = test_1a_string_concatenation()
    input("\n⏸️  Press Enter after UAT validation to continue...")

    results['1B'] = test_1b_predivided_values()
    input("\n⏸️  Press Enter after UAT validation to continue...")

    results['1C'] = test_1c_match_donut_exactly()
    input("\n⏸️  Press Enter after UAT validation to continue...")

    return results


def run_phase_2():
    """Run Phase 2: Dollar Sign Escaping Tests."""
    print("\n" + "#"*70)
    print("# PHASE 2: DOLLAR SIGN ESCAPING TESTS")
    print("#"*70)

    results = {}

    results['2A'] = test_2a_escaped_dollar()
    input("\n⏸️  Press Enter after UAT validation to continue...")

    results['2B'] = test_2b_no_dollar_symbol()
    input("\n⏸️  Press Enter after UAT validation to continue...")

    return results


def print_summary():
    """Print summary of all test results."""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    with open('formatter_test_results.json', 'r') as f:
        results = json.load(f)

    for test in results['tests']:
        status = test.get('uat_status', 'pending')
        symbol = "✅" if status == "pass" else "❌" if status == "fail" else "⏳"
        print(f"{symbol} Test {test['test_id']}: {test['test_name']}")
        print(f"   URL: {test['url']}")
        print(f"   Status: {status}")
        print()

    print(f"\nResults saved to: formatter_test_results.json")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║       APEXCHARTS FORMATTER SYSTEMATIC TESTING SUITE                  ║
║       Testing currency formatter variations to find working pattern  ║
╚══════════════════════════════════════════════════════════════════════╝

This script will generate test presentations sequentially.
After each test, validate in browser before proceeding.

Tests are organized in phases:
  Phase 1: Baseline Simplification (3 tests)
  Phase 2: Dollar Sign Escaping (2 tests)

Run phases individually or all together.
""")

    choice = input("Run [1] Phase 1 only, [2] Phase 2 only, [3] All phases: ").strip()

    if choice == "1":
        run_phase_1()
        print_summary()
    elif choice == "2":
        run_phase_2()
        print_summary()
    elif choice == "3":
        run_phase_1()
        run_phase_2()
        print_summary()
    else:
        print("Invalid choice. Run with argument 1, 2, or 3.")
