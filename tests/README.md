# Analytics Microservice v3 - Test Suite

This directory contains all test files organized by test type and purpose.

## 📁 Test Organization

### 🔬 Unit Tests (`unit/`)
Core functionality and component-level tests.

- `test_all_9_types.py` - All 9 native Chart.js types validation
- `test_analytics_type_mapping.py` - Analytics type to chart type mapping
- `test_chartjs_type_validation.py` - Chart.js type validation
- `test_v319_local.py` - Local v3.1.9 tests
- `test_v320_local.py` - Local v3.2.0 tests

**Run unit tests:**
\`\`\`bash
cd /path/to/analytics_microservice_v3
python -m pytest tests/unit/ -v
\`\`\`

### 🔗 Integration Tests (`integration/`)
API endpoint and service integration tests.

- `test_director_simulation.py` - Director Agent integration simulation
- `test_editor_v321.py` - Chart editor v3.2.1 tests
- `test_scatter_chart_fix.py` - Scatter chart bug fix validation
- `test_v316_data_transformation_fixes.py` - v3.1.6 data transformation
- `test_v317_editor_compatibility.py` - v3.1.7 editor compatibility

**Run integration tests:**
\`\`\`bash
python -m pytest tests/integration/ -v
\`\`\`

### 🚀 Production Tests (`production/`)
Production environment validation and version-specific tests.

- `test_production_v316.py` - Production validation v3.1.6
- `test_production_v317.py` - Production validation v3.1.7
- `test_production_v318.py` - Production validation v3.1.8
- `test_production_v319.py` - Production validation v3.1.9
- `test_production_v320.py` - Production validation v3.2.0
- `test_production_chartjs_types.py` - Chart.js types production test

**Run production tests:**
\`\`\`bash
python -m pytest tests/production/ -v
\`\`\`

## 🎯 Quick Test Commands

### Run All Tests
\`\`\`bash
python -m pytest tests/ -v
\`\`\`

### Run Specific Test File
\`\`\`bash
python tests/unit/test_all_9_types.py
\`\`\`

### Run with Coverage
\`\`\`bash
python -m pytest tests/ --cov=. --cov-report=html
\`\`\`

### Run Tests Matching Pattern
\`\`\`bash
python -m pytest tests/ -k "scatter" -v
\`\`\`

## 📊 Test Coverage

The test suite covers:
- ✅ All 9 native Chart.js chart types
- ✅ Advanced chart types (treemap, heatmap, boxplot, candlestick, sankey)
- ✅ Analytics type to chart type mapping
- ✅ Director Agent integration API
- ✅ Chart editor functionality
- ✅ Data transformation and validation
- ✅ Error handling and edge cases
- ✅ Production environment compatibility

## 🐛 Debugging Failed Tests

If tests fail:
1. Check [\`../docs/ANALYTICS_TEAM_ACTION_REQUIRED.md\`](../docs/ANALYTICS_TEAM_ACTION_REQUIRED.md) for known issues
2. Review relevant version documentation in [\`../docs/\`](../docs/)
3. Check production deployment status
4. Verify environment variables in \`.env\`

## 📝 Adding New Tests

When adding new tests:
1. Place in appropriate directory (\`unit/\`, \`integration/\`, or \`production/\`)
2. Follow naming convention: \`test_<feature>_<version>.py\`
3. Include docstrings explaining test purpose
4. Update this README with test description

## 🔍 Test Data

Test data files are archived in:
- [\`../archive/test-results/\`](../archive/test-results/) - Historical test outputs
- Individual test files may include inline test data

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Integration Guide](../docs/INTEGRATION_GUIDE.md) - API integration
- [Chart Type Catalog](../docs/CHART_TYPE_CATALOG.md) - Chart types reference
- [Error Codes](../docs/ERROR_CODES.md) - Error handling
