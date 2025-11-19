# Archive Directory

This directory contains historical files that are not actively used but kept for reference.

## 📁 Contents

### 🐛 Debug Scripts (`debug-scripts/`)
Historical debugging and inspection scripts used during development.

- `check_response_format.py` - Response format validation
- `inspect_*.py` - Chart inspection scripts (HTML, scatter, radar, bubble)
- `quick_test_fix.py` - Quick bug fix validation
- `verify_deployment.py` - Deployment verification script

**Note**: These scripts were used for debugging specific issues in earlier versions. For current debugging, see the main test suite in [`../tests/`](../tests/).

### 📊 Test Results (`test-results/`)
Historical test output files from various versions.

- `test_results_analytics_types_*.json` - Analytics type mapping results
- `test_results_chartjs_types_*.json` - Chart.js type validation results
- `production_test_v315_*.json` - Production test outputs

**Note**: These are archived outputs. Current test results should be generated fresh from the test suite.

### 🌐 HTML Demos (`html-demos/`)
Interactive HTML demos and debug pages.

- `chart_editor_demo.html` - Full-featured chart editor demo
- `interactive_editor_demo_simple.html` - Simplified editor demo
- `scatter_chart_debug.html` - Scatter chart debugging page
- `test_scatter_editor_simple.html` - Simple scatter editor test

**Note**: These demos were useful for visual debugging. For current chart testing, use the production deployment or local server.

### 📝 Server Logs
- `server.log` - Historical server logs (if present)

## ⚠️ Important Notes

1. **Do Not Delete**: These files provide historical context for bug fixes and development decisions
2. **Not Maintained**: Files here are frozen in time and not updated
3. **Reference Only**: Use for understanding past issues, not for current development
4. **Check Git History**: For detailed context, check git commits related to these files

## 🔄 Moving Files to Archive

When archiving files:
1. Ensure they're no longer actively used
2. Place in appropriate subdirectory
3. Update this README with description
4. Consider adding git commit reference for context

## 📚 Related Directories

- [`../tests/`](../tests/) - Active test suite
- [`../docs/`](../docs/) - Current documentation
- Root directory - Active application code

## 📖 Historical Context

This archive represents development from v3.1.4 through v3.2.1, covering:
- Chart type mapping fixes
- Editor compatibility improvements
- Scatter/bubble chart debugging
- Data transformation fixes
- Production validation iterations
