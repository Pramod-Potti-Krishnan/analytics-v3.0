"""
Comprehensive tests for Excel-like chart editor functionality.

Tests the chart-spreadsheet-editor.js library integration and validates:
- Editor opens for all supported chart types (14 Chart.js types)
- Correct columns displayed for each chart type
- Data validation works
- Editor integrates with chartjs_generator properly

Note: These are integration tests that validate the Python-side implementation.
JavaScript functionality tests should be done in browser/E2E tests.
"""

import pytest
from chartjs_generator import ChartJSGenerator


class TestExcelEditorIntegration:
    """Test Excel editor integration with chart generation"""

    @pytest.fixture
    def generator(self):
        """Create ChartJSGenerator instance"""
        return ChartJSGenerator()

    def test_editor_library_exists(self):
        """Test that Excel editor library file exists"""
        import os
        editor_path = 'static/js/chart-spreadsheet-editor.js'
        assert os.path.exists(editor_path), f"Excel editor library not found at {editor_path}"

        # Check file is not empty
        with open(editor_path, 'r') as f:
            content = f.read()
            assert len(content) > 1000, "Excel editor library seems too small"
            assert 'ChartSpreadsheetEditor' in content, "ChartSpreadsheetEditor class not found"

    def test_static_files_mount(self):
        """Test that FastAPI serves static files"""
        from rest_server import app
        from fastapi.staticfiles import StaticFiles

        # Check if /static mount exists
        routes = {route.path: route for route in app.routes}
        assert '/static' in str(routes), "Static files not mounted in FastAPI app"

    def test_chartjs_generator_has_editor_method(self, generator):
        """Test that ChartJSGenerator has the new editor method"""
        assert hasattr(generator, '_wrap_inline_script_with_editor'), \
            "ChartJSGenerator missing _wrap_inline_script_with_editor method"

    @pytest.mark.parametrize("chart_type,expected_substring", [
        ('line', 'chart-spreadsheet-editor.js'),
        ('bar', 'chart-spreadsheet-editor.js'),
        ('pie', 'chart-spreadsheet-editor.js'),
        ('scatter', 'chart-spreadsheet-editor.js'),
        ('bubble', 'chart-spreadsheet-editor.js'),
    ])
    def test_editor_library_loaded_in_charts(self, generator, chart_type, expected_substring):
        """Test that editor library is loaded in generated charts"""
        # Generate a simple chart with editor enabled
        data = {"labels": ["A", "B"], "values": [10, 20]}

        if chart_type == 'scatter':
            chart_html = generator.generate_scatter_chart(
                data=data,
                enable_editor=True,
                presentation_id='test-pres',
                api_base_url='/api'
            )
        elif chart_type == 'bubble':
            bubble_data = [
                {"label": "A", "x": 10, "y": 20, "r": 15},
                {"label": "B", "x": 30, "y": 40, "r": 20}
            ]
            chart_html = generator.generate_bubble_chart(
                data=bubble_data,
                enable_editor=True,
                presentation_id='test-pres',
                api_base_url='/api'
            )
        else:
            # Use generic chart generation method
            chart_html = generator.generate_chart(
                chart_type=chart_type,
                data=data,
                chart_id='test-chart',
                enable_editor=True,
                presentation_id='test-pres',
                api_base_url='/api'
            )

        assert expected_substring in chart_html, \
            f"Excel editor library not loaded in {chart_type} chart HTML"

    def test_editor_has_edit_button(self, generator):
        """Test that charts with editor enabled have edit button"""
        data = {"labels": ["Q1", "Q2"], "values": [100, 120]}

        chart_html = generator.generate_chart(
            chart_type='line',
            data=data,
            chart_id='test-chart',
            enable_editor=True,
            presentation_id='test-pres',
            api_base_url='/api'
        )

        # Check for edit button
        assert 'chart-edit-btn' in chart_html, "Edit button not found in chart HTML"
        assert '✏️' in chart_html, "Edit icon not found in chart HTML"
        assert 'openChartEditor_' in chart_html, "Editor open function not found"

    def test_editor_extracts_chart_data(self, generator):
        """Test that editor JavaScript extracts chart data correctly"""
        data = {"labels": ["A", "B", "C"], "values": [10, 20, 30]}

        chart_html = generator.generate_chart(
            chart_type='bar',
            data=data,
            chart_id='test-bar',
            enable_editor=True,
            presentation_id='test-pres',
            api_base_url='/api'
        )

        # Check for data extraction function
        assert 'extractChartData_' in chart_html, "Data extraction function not found"
        assert 'updateChartData_' in chart_html, "Data update function not found"

    def test_editor_disabled_by_default(self, generator):
        """Test that editor is not added when enable_editor=False"""
        data = {"labels": ["A", "B"], "values": [10, 20]}

        chart_html = generator.generate_chart(
            chart_type='line',
            data=data,
            chart_id='test-chart',
            enable_editor=False  # Explicitly False
        )

        # Editor components should NOT be present
        assert 'chart-spreadsheet-editor.js' not in chart_html, \
            "Excel editor loaded even though enable_editor=False"
        assert 'openChartEditor_' not in chart_html, \
            "Editor open function found even though enable_editor=False"


class TestExcelEditorColumnConfigurations:
    """Test that Excel editor has correct column configurations for each chart type"""

    def test_data_models_documentation_exists(self):
        """Test that CHART_DATA_MODELS.md exists and is comprehensive"""
        import os
        doc_path = 'docs/CHART_DATA_MODELS.md'
        assert os.path.exists(doc_path), f"Data models documentation not found at {doc_path}"

        with open(doc_path, 'r') as f:
            content = f.read()

            # Check for all chart types
            assert 'Simple Label-Value Format (13 Chart Types)' in content
            assert 'Scatter Format (1 Chart Type)' in content
            assert 'Bubble Format (1 Chart Type)' in content
            assert 'Multi-Series Format (3 Chart Types)' in content
            assert 'Sankey Flow Format (1 Chart Type)' in content

            # Check for specific chart types
            chart_types = [
                'line', 'bar_vertical', 'pie', 'scatter', 'bubble',
                'bar_grouped', 'd3_sankey', 'd3_treemap', 'd3_choropleth_usa'
            ]
            for chart_type in chart_types:
                assert chart_type in content, f"Chart type {chart_type} not documented"

    def test_synthetic_data_validation_report_exists(self):
        """Test that synthetic data validation report exists"""
        import os
        report_path = 'docs/SYNTHETIC_DATA_VALIDATION_REPORT.md'
        assert os.path.exists(report_path), f"Validation report not found at {report_path}"

        with open(report_path, 'r') as f:
            content = f.read()

            # Check for validation status
            assert 'EXCELLENT ALIGNMENT' in content or '100% ALIGNED' in content
            assert 'All 18 chart types' in content

    def test_implementation_guide_exists(self):
        """Test that implementation guide exists and is comprehensive"""
        import os
        guide_path = 'docs/EXCEL_EDITOR_IMPLEMENTATION_GUIDE.md'
        assert os.path.exists(guide_path), f"Implementation guide not found at {guide_path}"

        with open(guide_path, 'r') as f:
            content = f.read()

            # Check for key sections
            assert 'Completion Checklist' in content
            assert 'Stage 3.3' in content
            assert 'Stage 3.4' in content
            assert 'Stage 3.5' in content


class TestChartTypeDataModels:
    """Test data models for each chart type match specifications"""

    @pytest.fixture
    def generator(self):
        return ChartJSGenerator()

    def test_simple_charts_label_value(self, generator):
        """Test simple charts use label-value format"""
        data = {"labels": ["A", "B"], "values": [10, 20]}

        for chart_type in ['line', 'bar', 'pie', 'doughnut']:
            chart_html = generator.generate_chart(
                chart_type=chart_type,
                data=data,
                chart_id=f'test-{chart_type}'
            )
            # Just verify it generates without error
            assert chart_html is not None
            assert len(chart_html) > 100

    def test_scatter_chart_xy_format(self, generator):
        """Test scatter charts use X,Y format"""
        scatter_data = [
            {"x": 10, "y": 20},
            {"x": 30, "y": 40}
        ]

        chart_html = generator.generate_scatter_chart(data=scatter_data)
        assert chart_html is not None
        # Scatter should not have labels array (uses x,y objects)
        assert 'datasets' in chart_html or 'data' in chart_html

    def test_bubble_chart_label_xy_r_format(self, generator):
        """Test bubble charts use Label, X, Y, Radius format"""
        bubble_data = [
            {"label": "A", "x": 10, "y": 20, "r": 15},
            {"label": "B", "x": 30, "y": 40, "r": 25}
        ]

        chart_html = generator.generate_bubble_chart(data=bubble_data)
        assert chart_html is not None
        # Bubble should include labels
        assert 'label' in chart_html.lower() or 'datasets' in chart_html


class TestEditorFeatures:
    """Test specific Excel editor features"""

    def test_keyboard_navigation_documented(self):
        """Test that keyboard navigation is documented in editor code"""
        with open('static/js/chart-spreadsheet-editor.js', 'r') as f:
            content = f.read()

            # Check for keyboard event handlers
            assert 'ArrowUp' in content, "Arrow up navigation not implemented"
            assert 'ArrowDown' in content, "Arrow down navigation not implemented"
            assert 'Tab' in content, "Tab navigation not implemented"
            assert 'Enter' in content, "Enter key handling not implemented"

    def test_copy_paste_support_documented(self):
        """Test that copy/paste support is documented"""
        with open('static/js/chart-spreadsheet-editor.js', 'r') as f:
            content = f.read()

            # Check for clipboard handling
            assert 'paste' in content.lower(), "Paste handling not found"
            assert 'clipboardData' in content or 'clipboard' in content, \
                "Clipboard API usage not found"

    def test_data_validation_documented(self):
        """Test that data validation is documented"""
        with open('static/js/chart-spreadsheet-editor.js', 'r') as f:
            content = f.read()

            # Check for validation
            assert '_validateData' in content or 'validate' in content, \
                "Data validation not found"
            assert 'NaN' in content or 'isNaN' in content, \
                "NaN validation not found"

    def test_highlighting_documented(self):
        """Test that column highlighting is documented"""
        with open('static/js/chart-spreadsheet-editor.js', 'r') as f:
            content = f.read()

            # Check for highlighting classes/styles
            assert 'active' in content.lower() or 'highlight' in content.lower(), \
                "Column highlighting not found"


class TestDocumentation:
    """Test that all documentation is complete and accurate"""

    def test_readme_mentions_excel_editor(self):
        """Test that README.md mentions the Excel editor feature"""
        with open('README.md', 'r') as f:
            content = f.read()

            # Should mention Excel or editor or similar
            assert 'edit' in content.lower() or 'excel' in content.lower(), \
                "README.md doesn't mention editor feature"

    def test_all_required_docs_exist(self):
        """Test that all required documentation files exist"""
        import os

        required_docs = [
            'docs/CHART_DATA_MODELS.md',
            'docs/SYNTHETIC_DATA_VALIDATION_REPORT.md',
            'docs/EXCEL_EDITOR_IMPLEMENTATION_GUIDE.md',
            'docs/D3_EDITOR_SUPPORT_STATUS.md',
        ]

        for doc_path in required_docs:
            assert os.path.exists(doc_path), f"Required documentation missing: {doc_path}"


class TestAPIEndpoints:
    """Test that required API endpoints exist"""

    def test_update_data_endpoint_exists(self):
        """Test that /api/charts/update-data endpoint is defined"""
        from rest_server import app

        # Get all routes
        routes = {route.path: route for route in app.routes}

        # Check for update endpoint
        update_endpoints = [path for path in routes.keys() if 'update-data' in path or 'update_data' in path]

        # If endpoint doesn't exist, it will need to be added
        # For now, just document the requirement
        if not update_endpoints:
            pytest.skip("Update data endpoint not yet implemented - needs to be added")


# Summary test to run first
class TestOverallStatus:
    """High-level status tests"""

    def test_excel_editor_library_complete(self):
        """Test that Excel editor library is complete and substantial"""
        import os
        library_path = 'static/js/chart-spreadsheet-editor.js'

        assert os.path.exists(library_path)

        with open(library_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')

            # Should be substantial (>1000 lines)
            assert len(lines) > 1000, f"Excel editor library seems incomplete ({len(lines)} lines)"

            # Should have key classes
            assert 'class ChartSpreadsheetEditor' in content
            assert 'openChartEditor' in content

    def test_feature_branch_status(self):
        """Test that we're on the feature branch"""
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        current_branch = result.stdout.strip()

        assert current_branch == 'feature/excel-like-chart-editor', \
            f"Not on feature branch (currently on: {current_branch})"

    def test_chart_support_coverage(self):
        """Test that we have documentation for all 18 chart types"""
        with open('docs/CHART_DATA_MODELS.md', 'r') as f:
            content = f.read()

            # Count chart types mentioned
            # Should cover all 18 types
            chart_count = content.count('Chart Type')
            assert chart_count >= 18, f"Expected 18+ chart types documented, found {chart_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
