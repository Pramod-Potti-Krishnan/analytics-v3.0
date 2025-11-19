#!/usr/bin/env python3
"""
Test script for v3.2.1 scatter/bubble chart editor fix.
Tests that editors show correct columns and populate data rows.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from chartjs_generator import ChartJSGenerator

def test_scatter_editor():
    """Test scatter chart editor with X, Y columns"""
    print("\n=== Test 1: Scatter Chart Editor ===")

    gen = ChartJSGenerator()

    # Generate scatter chart with editor enabled
    chart_html = gen.generate_scatter_plot(
        data={
            "labels": ["Point A", "Point B", "Point C", "Point D", "Point E"],
            "values": [100, 150, 200, 175, 225]
        },
        options={
            "plugins": {
                "datalabels": {
                    "display": False  # No [object Object] labels
                }
            }
        },
        presentation_id="test-scatter-editor",
        enable_editor=True,  # CRITICAL: Enable editor
        chart_id="scatter-test-v321"
    )

    # Save to file
    output_file = "test_scatter_editor_v321.html"
    with open(output_file, "w") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scatter Chart Editor Test v3.2.1</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 40px;
            background: #f5f5f5;
        }}
        .test-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-info h2 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .test-info ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .test-info li {{
            margin: 5px 0;
        }}
        .pass {{
            color: #4CAF50;
            font-weight: 600;
        }}
        .fail {{
            color: #f44336;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="test-info">
        <h2>📊 Scatter Chart Editor Test - v3.2.1</h2>
        <p><strong>Test Objectives:</strong></p>
        <ul>
            <li class="pass">✅ Editor should show <strong>X</strong> and <strong>Y</strong> column headers (NOT Label/Value)</li>
            <li class="pass">✅ Editor should populate table with <strong>5 data rows</strong> (NOT empty)</li>
            <li class="pass">✅ Each row should have X and Y input fields with numeric values</li>
            <li class="pass">✅ Add Row button should create X, Y inputs (NOT Label/Value)</li>
            <li class="pass">✅ Save should update chart with new X, Y coordinates</li>
            <li class="pass">✅ Chart should show <strong>X marks (crosses)</strong>, not circles</li>
            <li class="pass">✅ NO [object Object] labels should appear on chart</li>
        </ul>
        <p><strong>Instructions:</strong> Click the pencil icon (✏️) in top-left of chart to test editor</p>
    </div>

    {chart_html}

    <script>
        // Register ChartDataLabels plugin globally
        if (typeof Chart !== 'undefined' && Chart.register) {{
            Chart.register(ChartDataLabels);
            console.log('✅ ChartDataLabels plugin registered globally');
        }} else {{
            console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
        }}
    </script>
</body>
</html>
        """)

    print(f"✅ Scatter editor test saved to: {output_file}")
    print("   Open in browser and check:")
    print("   1. Click ✏️ edit button")
    print("   2. Table headers should be: #, X, Y, Actions")
    print("   3. Table should show 5 rows with data")
    print("   4. Try editing values and saving")
    return output_file

def test_bubble_editor():
    """Test bubble chart editor with X, Y, Radius columns"""
    print("\n=== Test 2: Bubble Chart Editor ===")

    gen = ChartJSGenerator()

    # Generate bubble chart with editor enabled
    chart_html = gen.generate_bubble_chart(
        data={
            "labels": ["Bubble A", "Bubble B", "Bubble C"],
            "values": [180, 145, 95]
        },
        options={
            "plugins": {
                "datalabels": {
                    "display": False  # No [object Object] labels
                }
            }
        },
        presentation_id="test-bubble-editor",
        enable_editor=True,  # CRITICAL: Enable editor
        chart_id="bubble-test-v321"
    )

    # Save to file
    output_file = "test_bubble_editor_v321.html"
    with open(output_file, "w") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bubble Chart Editor Test v3.2.1</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 40px;
            background: #f5f5f5;
        }}
        .test-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-info h2 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .test-info ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .test-info li {{
            margin: 5px 0;
        }}
        .pass {{
            color: #4CAF50;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="test-info">
        <h2>🫧 Bubble Chart Editor Test - v3.2.1</h2>
        <p><strong>Test Objectives:</strong></p>
        <ul>
            <li class="pass">✅ Editor should show <strong>X</strong>, <strong>Y</strong>, and <strong>Radius</strong> column headers</li>
            <li class="pass">✅ Editor should populate table with <strong>3 data rows</strong> (NOT empty)</li>
            <li class="pass">✅ Each row should have X, Y, Radius input fields with numeric values</li>
            <li class="pass">✅ Add Row button should create X, Y, Radius inputs</li>
            <li class="pass">✅ Save should update chart with new coordinates and sizes</li>
            <li class="pass">✅ Chart should show <strong>circles</strong> with varying sizes</li>
            <li class="pass">✅ NO [object Object] labels should appear on chart</li>
        </ul>
        <p><strong>Instructions:</strong> Click the pencil icon (✏️) in top-left of chart to test editor</p>
    </div>

    {chart_html}

    <script>
        // Register ChartDataLabels plugin globally
        if (typeof Chart !== 'undefined' && Chart.register) {{
            Chart.register(ChartDataLabels);
            console.log('✅ ChartDataLabels plugin registered globally');
        }} else {{
            console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
        }}
    </script>
</body>
</html>
        """)

    print(f"✅ Bubble editor test saved to: {output_file}")
    print("   Open in browser and check:")
    print("   1. Click ✏️ edit button")
    print("   2. Table headers should be: #, X, Y, Radius, Actions")
    print("   3. Table should show 3 rows with data")
    print("   4. Try editing values and saving")
    return output_file

def test_bar_editor_regression():
    """Test that bar chart editor still works (regression check)"""
    print("\n=== Test 3: Bar Chart Editor (Regression) ===")

    gen = ChartJSGenerator()

    # Generate bar chart with editor enabled
    chart_html = gen.generate_bar_chart(
        data={
            "labels": ["Category A", "Category B", "Category C"],
            "values": [120, 180, 150]
        },
        presentation_id="test-bar-editor",
        enable_editor=True,
        chart_id="bar-test-v321"
    )

    # Save to file
    output_file = "test_bar_editor_regression_v321.html"
    with open(output_file, "w") as f:
        f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Bar Chart Editor Regression Test v3.2.1</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 40px;
            background: #f5f5f5;
        }}
        .test-info {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-info h2 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .test-info ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .test-info li {{
            margin: 5px 0;
        }}
        .pass {{
            color: #4CAF50;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="test-info">
        <h2>📊 Bar Chart Editor Regression Test - v3.2.1</h2>
        <p><strong>Test Objectives:</strong></p>
        <ul>
            <li class="pass">✅ Editor should show <strong>Label</strong> and <strong>Value</strong> column headers (NOT X/Y)</li>
            <li class="pass">✅ Editor should populate table with <strong>3 data rows</strong></li>
            <li class="pass">✅ Each row should have Label (text) and Value (number) inputs</li>
            <li class="pass">✅ Add Row button should create Label, Value inputs</li>
            <li class="pass">✅ Save should update chart with new labels and values</li>
            <li class="pass">✅ Chart should show vertical bars</li>
        </ul>
        <p><strong>Instructions:</strong> Click the pencil icon (✏️) in top-left of chart to test editor</p>
    </div>

    {chart_html}

    <script>
        // Register ChartDataLabels plugin globally
        if (typeof Chart !== 'undefined' && Chart.register) {{
            Chart.register(ChartDataLabels);
            console.log('✅ ChartDataLabels plugin registered globally');
        }} else {{
            console.error('❌ ERROR: Chart.js or ChartDataLabels not loaded');
        }}
    </script>
</body>
</html>
        """)

    print(f"✅ Bar editor regression test saved to: {output_file}")
    print("   Open in browser and check:")
    print("   1. Click ✏️ edit button")
    print("   2. Table headers should be: #, Label, Value, Actions")
    print("   3. Table should show 3 rows with data")
    return output_file

if __name__ == "__main__":
    print("=" * 60)
    print("Analytics Microservice v3.2.1 - Editor Fix Tests")
    print("=" * 60)

    # Run all tests
    scatter_file = test_scatter_editor()
    bubble_file = test_bubble_editor()
    bar_file = test_bar_editor_regression()

    print("\n" + "=" * 60)
    print("✅ ALL TEST FILES CREATED")
    print("=" * 60)
    print(f"\n📂 Test Files:")
    print(f"   1. {scatter_file}")
    print(f"   2. {bubble_file}")
    print(f"   3. {bar_file}")
    print(f"\n🌐 Open each file in your browser to verify the fixes")
    print(f"\n✅ Expected Results:")
    print(f"   - Scatter: X, Y columns with 5 data rows")
    print(f"   - Bubble: X, Y, Radius columns with 3 data rows")
    print(f"   - Bar: Label, Value columns with 3 data rows (regression)")
    print("=" * 60)
