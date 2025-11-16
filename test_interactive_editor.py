"""
Test Interactive Chart Editor

Demonstrates the chart generator with built-in interactive editor.
Generates HTML with edit button, modal popup, and save functionality.
"""

from chartjs_generator import ChartJSGenerator


def test_interactive_line_chart():
    """Test line chart with interactive editor enabled."""
    generator = ChartJSGenerator(theme="professional")

    # Sample data
    data = {
        "series_name": "Quarterly Revenue",
        "labels": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
        "values": [125000, 145000, 178000, 195000],
        "format": "currency"
    }

    # Generate chart WITH interactive editor
    html = generator.generate_line_chart(
        data=data,
        height=600,
        chart_id="interactive-line-chart",
        enable_editor=True,
        presentation_id="test-presentation-123"
    )

    # Create complete HTML page for testing
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Chart Editor Test</title>

    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0"></script>

    <!-- Register datalabels plugin -->
    <script>
        Chart.register(ChartDataLabels);
    </script>

    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f5f5;
            padding: 40px 20px;
            margin: 0;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 10px;
        }}

        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 16px;
        }}

        .instructions {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }}

        .instructions h3 {{
            color: #856404;
            margin-top: 0;
            margin-bottom: 12px;
        }}

        .instructions ol {{
            margin-left: 20px;
            color: #856404;
        }}

        .instructions li {{
            margin: 8px 0;
        }}

        .chart-wrapper {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: relative;
            height: 700px;
        }}

        canvas {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Interactive Chart Editor Test</h1>
        <p class="subtitle">Chart.js with Built-in Data Editor</p>

        <div class="instructions">
            <h3>🎯 How to Test:</h3>
            <ol>
                <li>Click the <strong>"📊 Edit Data"</strong> button in the top-right corner of the chart</li>
                <li>A modal popup will open showing the current data in an editable table</li>
                <li>Edit any X-axis labels (quarters) or Y-axis values (revenue)</li>
                <li>Click <strong>"+ Add Row"</strong> to add Q5 2025 data</li>
                <li>Delete a row by clicking the 🗑️ button</li>
                <li>Click <strong>"💾 Save & Update"</strong></li>
                <li>Chart will update instantly!</li>
                <li><strong>Note:</strong> Backend API not implemented yet, so data won't persist (browser only)</li>
            </ol>
        </div>

        <div class="chart-wrapper">
            {html}
        </div>
    </div>

    <script>
        // Initialize Chart.js after a short delay
        setTimeout(() => {{
            const canvas = document.getElementById('interactive-line-chart');
            if (!canvas) {{
                console.error('Canvas not found!');
                return;
            }}

            // Parse config from HTML comment
            const comment = canvas.childNodes[0];
            if (!comment || comment.nodeType !== 8) {{
                console.error('Chart config not found in comment');
                return;
            }}

            const config = JSON.parse(comment.nodeValue.trim());

            // Create Chart.js instance
            new Chart(canvas, config);
            console.log('✅ Chart initialized successfully');
        }}, 100);
    </script>
</body>
</html>
"""

    # Save to file
    output_file = "test_interactive_editor_output.html"
    with open(output_file, "w") as f:
        f.write(full_html)

    print(f"✅ Interactive chart editor test generated!")
    print(f"📄 Output file: {output_file}")
    print(f"\n🚀 Open the file in your browser to test the interactive editor")
    print(f"   file://{os.path.abspath(output_file)}")

    return output_file


if __name__ == "__main__":
    import os
    test_interactive_line_chart()
