"""
Generate standalone HTML files for visual validation.

Creates self-contained HTML files that can be opened directly in a browser
to verify charts render correctly WITHOUT requiring Layout Service integration.

This helps isolate whether issues are in Analytics Service or Layout Service.
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chartjs_generator import ChartJSGenerator


def save_standalone_html(chart_name, chart_html, data_description):
    """Save chart HTML as standalone file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"standalone_{chart_name}_{timestamp}.html"

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chart_name.replace('_', ' ').title()} - Standalone Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        .info {{
            background: #e9ecef;
            padding: 20px;
            border-left: 4px solid #007bff;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .info h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .info pre {{
            background: #fff;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 13px;
        }}
        .chart-wrapper {{
            margin: 30px 0;
            padding: 20px;
            background: #fafafa;
            border-radius: 8px;
        }}
        .success-badge {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            {chart_name.replace('_', ' ').title()}
            <span class="success-badge">✓ STANDALONE TEST</span>
        </h1>

        <div class="info">
            <h3>Test Information</h3>
            <p><strong>Chart Type:</strong> {chart_name}</p>
            <p><strong>Test Time:</strong> {timestamp}</p>
            <p><strong>Data Format:</strong> Director Agent v3.4 format (transformed to Chart.js)</p>
            <p><strong>Environment:</strong> Standalone HTML (no Layout Service)</p>
        </div>

        <div class="info">
            <h3>Test Data</h3>
            <pre>{data_description}</pre>
        </div>

        <div class="chart-wrapper">
            <h2>Chart Output</h2>
            {chart_html}
        </div>

        <div class="info">
            <h3>Validation Checklist</h3>
            <ul>
                <li>✓ Chart renders visually (not blank)</li>
                <li>✓ All data series appear</li>
                <li>✓ Labels are visible</li>
                <li>✓ No console errors</li>
                <li>✓ Chart is interactive (hover works)</li>
            </ul>
            <p><strong>Open browser console (F12) to check for any JavaScript errors.</strong></p>
        </div>
    </div>
</body>
</html>"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Generated: {filename}")
    return filename


def main():
    """Generate all standalone HTML files."""
    print("\n" + "="*70)
    print("STANDALONE HTML GENERATOR")
    print("="*70)
    print("\nGenerating self-contained HTML files for visual validation...")
    print("These files can be opened directly in a browser.\n")

    generator = ChartJSGenerator(theme="professional")
    files_created = []

    # 1. Bar Grouped
    print("\n" + "-"*70)
    print("1. Generating bar_grouped...")
    data_bar_grouped = [
        {"label": "Q1", "North America": 124, "EMEA": 98, "APAC": 75},
        {"label": "Q2", "North America": 145, "EMEA": 112, "APAC": 88},
        {"label": "Q3", "North America": 165, "EMEA": 128, "APAC": 105},
        {"label": "Q4", "North America": 180, "EMEA": 145, "APAC": 125}
    ]
    html = generator.generate_grouped_bar_chart(data=data_bar_grouped, height=600)
    filename = save_standalone_html(
        "bar_grouped",
        html,
        str(data_bar_grouped[:2]) + "\n  ..."
    )
    files_created.append(filename)

    # 2. Bar Stacked
    print("\n" + "-"*70)
    print("2. Generating bar_stacked...")
    data_bar_stacked = [
        {"label": "Q1", "Operations": 45, "Sales": 35, "R&D": 20, "Marketing": 15},
        {"label": "Q2", "Operations": 48, "Sales": 40, "R&D": 25, "Marketing": 18},
        {"label": "Q3", "Operations": 52, "Sales": 45, "R&D": 30, "Marketing": 22},
        {"label": "Q4", "Operations": 55, "Sales": 50, "R&D": 35, "Marketing": 25}
    ]
    html = generator.generate_stacked_bar_chart(data=data_bar_stacked, height=600)
    filename = save_standalone_html(
        "bar_stacked",
        html,
        str(data_bar_stacked[:2]) + "\n  ..."
    )
    files_created.append(filename)

    # 3. Area Stacked
    print("\n" + "-"*70)
    print("3. Generating area_stacked...")
    data_area_stacked = [
        {"label": "Q1", "Product A": 120, "Product B": 95, "Product C": 70},
        {"label": "Q2", "Product A": 145, "Product B": 110, "Product C": 85},
        {"label": "Q3", "Product A": 170, "Product B": 130, "Product C": 100},
        {"label": "Q4", "Product A": 200, "Product B": 155, "Product C": 120}
    ]
    html = generator.generate_stacked_area_chart(data=data_area_stacked, height=600)
    filename = save_standalone_html(
        "area_stacked",
        html,
        str(data_area_stacked[:2]) + "\n  ..."
    )
    files_created.append(filename)

    # 4. Mixed
    print("\n" + "-"*70)
    print("4. Generating mixed...")
    data_mixed = [
        {"label": "Q1", "Revenue": 120, "Costs": 80},
        {"label": "Q2", "Revenue": 150, "Costs": 90},
        {"label": "Q3", "Revenue": 180, "Costs": 100},
        {"label": "Q4", "Revenue": 200, "Costs": 110}
    ]
    html = generator.generate_mixed_chart(data=data_mixed, height=600)
    filename = save_standalone_html(
        "mixed",
        html,
        str(data_mixed)
    )
    files_created.append(filename)

    # 5. D3 Sunburst
    print("\n" + "-"*70)
    print("5. Generating d3_sunburst...")
    data_d3_sunburst = [
        {"label": "Engineering", "value": 800000},
        {"label": "Sales", "value": 600000},
        {"label": "Marketing", "value": 400000},
        {"label": "Operations", "value": 350000},
        {"label": "Finance", "value": 200000},
        {"label": "HR", "value": 150000}
    ]
    html = generator.generate_d3_sunburst_chart(data=data_d3_sunburst, height=720)
    filename = save_standalone_html(
        "d3_sunburst",
        html,
        str(data_d3_sunburst[:3]) + "\n  ..."
    )
    files_created.append(filename)

    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\n✅ Created {len(files_created)} standalone HTML files:\n")
    for i, filename in enumerate(files_created, 1):
        print(f"{i}. {filename}")

    print("\n" + "="*70)
    print("HOW TO TEST")
    print("="*70)
    print("""
1. Open each HTML file in your web browser (double-click or right-click → Open With)
2. Check that the chart renders correctly (not blank)
3. Verify all data series appear
4. Open browser console (F12) to check for errors
5. Test interactivity (hover over chart elements)

If charts render correctly in standalone HTML but fail in Layout Service,
the issue is in Layout Service integration, NOT Analytics Service.

Share these files with the Director team for verification!
""")

    return 0


if __name__ == "__main__":
    exit(main())
