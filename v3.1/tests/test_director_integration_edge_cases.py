"""
Edge Case Test Suite for Director Integration
Analytics Service v3.1.2

Tests all validation rules, error codes, and edge cases for Director team integration.
"""

import pytest
import requests
from typing import Dict, Any, List
import time

# Configuration
BASE_URL = "https://analytics-v30-production.up.railway.app"
# For local testing, uncomment:
# BASE_URL = "http://localhost:8080"

class TestDataValidation:
    """Test comprehensive data validation rules."""

    def test_minimum_data_points_violation(self):
        """Test INVALID_DATA_POINTS error with less than 2 points."""
        payload = {
            "presentation_id": "test-pres-001",
            "slide_id": "slide-001",
            "slide_number": 1,
            "narrative": "Test with only 1 data point",
            "data": [
                {"label": "Q1", "value": 100}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_DATA_POINTS"
        assert error["category"] == "validation"
        assert error["retryable"] is True
        assert "2 data points" in error["message"].lower()
        assert error["suggestion"] is not None

    def test_maximum_data_points_violation(self):
        """Test INVALID_DATA_POINTS error with more than 50 points."""
        payload = {
            "presentation_id": "test-pres-002",
            "slide_id": "slide-002",
            "slide_number": 2,
            "narrative": "Test with 51 data points",
            "data": [
                {"label": f"Point {i}", "value": i * 100}
                for i in range(51)
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_DATA_POINTS"
        assert error["category"] == "validation"
        assert error["retryable"] is True
        assert "50" in error["message"]

    def test_nan_value_rejection(self):
        """Test INVALID_VALUES error with NaN values."""
        payload = {
            "presentation_id": "test-pres-003",
            "slide_id": "slide-003",
            "slide_number": 3,
            "narrative": "Test with NaN value",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": float('nan')},
                {"label": "Q3", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_VALUES"
        assert error["category"] == "validation"
        assert error["retryable"] is True
        assert "nan" in error["message"].lower()

    def test_infinity_value_rejection(self):
        """Test INVALID_VALUES error with Infinity values."""
        payload = {
            "presentation_id": "test-pres-004",
            "slide_id": "slide-004",
            "slide_number": 4,
            "narrative": "Test with Infinity value",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": float('inf')},
                {"label": "Q3", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_VALUES"
        assert error["category"] == "validation"
        assert error["retryable"] is True
        assert "infinity" in error["message"].lower()

    def test_duplicate_labels_rejection(self):
        """Test DUPLICATE_LABELS error."""
        payload = {
            "presentation_id": "test-pres-005",
            "slide_id": "slide-005",
            "slide_number": 5,
            "narrative": "Test with duplicate labels",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 200},
                {"label": "Q1", "value": 300}  # Duplicate!
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "DUPLICATE_LABELS"
        assert error["category"] == "validation"
        assert error["retryable"] is True
        assert "duplicate" in error["message"].lower()
        assert error["suggestion"] is not None

    def test_empty_label_rejection(self):
        """Test INVALID_LABELS error with empty labels."""
        payload = {
            "presentation_id": "test-pres-006",
            "slide_id": "slide-006",
            "slide_number": 6,
            "narrative": "Test with empty label",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "", "value": 200},
                {"label": "Q3", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] in ["INVALID_LABELS", "EMPTY_FIELD"]
        assert error["category"] == "validation"
        assert error["retryable"] is True

    def test_whitespace_only_label_rejection(self):
        """Test INVALID_LABELS error with whitespace-only labels."""
        payload = {
            "presentation_id": "test-pres-007",
            "slide_id": "slide-007",
            "slide_number": 7,
            "narrative": "Test with whitespace label",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "   ", "value": 200},
                {"label": "Q3", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] in ["INVALID_LABELS", "EMPTY_FIELD"]
        assert error["category"] == "validation"
        assert error["retryable"] is True

    def test_label_trimming(self):
        """Test that labels with leading/trailing whitespace are trimmed."""
        payload = {
            "presentation_id": "test-pres-008",
            "slide_id": "slide-008",
            "slide_number": 8,
            "narrative": "Test label trimming",
            "data": [
                {"label": "  Q1  ", "value": 100},
                {"label": "Q2", "value": 200},
                {"label": "  Q3", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        # Should succeed with trimmed labels
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True


class TestChartDiscovery:
    """Test chart type discovery endpoints."""

    def test_get_all_chart_types(self):
        """Test GET /api/v1/chart-types returns all chart types."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "summary" in data
        assert "chart_types" in data
        assert data["summary"]["total_chart_types"] == 13
        assert data["summary"]["chartjs_types"] == 9
        assert data["summary"]["apexcharts_types"] == 4

    def test_get_chartjs_types(self):
        """Test GET /api/v1/chart-types/chartjs returns only Chart.js types."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types/chartjs")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["chart_types"]) == 9
        for chart in data["chart_types"]:
            assert chart["library"] == "Chart.js"

    def test_get_apexcharts_types(self):
        """Test GET /api/v1/chart-types/apexcharts returns only ApexCharts types."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types/apexcharts")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["chart_types"]) == 4
        for chart in data["chart_types"]:
            assert chart["library"] == "ApexCharts"

    def test_get_specific_chart_type(self):
        """Test GET /api/v1/chart-types/{chart_id} returns specific chart details."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types/line")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["chart_type"]["id"] == "line"
        assert data["chart_type"]["name"] == "Line Chart"
        assert data["chart_type"]["library"] == "Chart.js"
        assert "min_data_points" in data["chart_type"]
        assert "max_data_points" in data["chart_type"]
        assert "use_cases" in data["chart_type"]

    def test_get_invalid_chart_type(self):
        """Test GET /api/v1/chart-types/{chart_id} with invalid ID returns error."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types/invalid_chart")

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "INVALID_CHART_TYPE"
        assert error["category"] == "resource"
        assert error["retryable"] is False

    def test_get_layout_compatible_charts(self):
        """Test GET /api/v1/layouts/{layout}/chart-types returns layout-compatible charts."""
        response = requests.get(f"{BASE_URL}/api/v1/layouts/L02/chart-types")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["layout"] == "L02"
        # All Chart.js types support L02, plus ApexCharts area/heatmap/treemap/waterfall
        assert len(data["chart_types"]) >= 9

        # Verify all returned charts support L02
        for chart in data["chart_types"]:
            assert "L02" in chart["supported_layouts"]

    def test_chart_type_schema_completeness(self):
        """Test that chart type schema includes all required fields."""
        response = requests.get(f"{BASE_URL}/api/v1/chart-types/line")

        assert response.status_code == 200
        chart = response.json()["chart_type"]

        # Required fields
        assert "id" in chart
        assert "name" in chart
        assert "description" in chart
        assert "library" in chart
        assert "supported_layouts" in chart
        assert "min_data_points" in chart
        assert "max_data_points" in chart
        assert "optimal_data_points" in chart
        assert "use_cases" in chart
        assert "examples" in chart
        assert "data_requirements" in chart
        assert "visual_properties" in chart
        assert "interactive_features" in chart


class TestErrorHandling:
    """Test comprehensive error handling."""

    def test_error_response_structure(self):
        """Test that error responses have correct structure."""
        payload = {
            "presentation_id": "test-pres-009",
            "slide_id": "slide-009",
            "slide_number": 9,
            "narrative": "Test error structure",
            "data": [{"label": "Q1", "value": 100}]  # Too few points
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        data = response.json()

        # Verify error structure
        assert "success" in data
        assert data["success"] is False
        assert "error" in data

        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "category" in error
        assert "retryable" in error
        # Optional fields
        assert "field" in error or "details" in error or "suggestion" in error

    def test_retryable_flags_accuracy(self):
        """Test that retryable flags are set correctly."""
        # Validation error (retryable)
        payload = {
            "presentation_id": "test-pres-010",
            "slide_id": "slide-010",
            "slide_number": 10,
            "narrative": "Test retryable flag",
            "data": [{"label": "Q1", "value": 100}]  # Too few points
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["category"] == "validation"
        assert error["retryable"] is True

    def test_invalid_analytics_type(self):
        """Test INVALID_ANALYTICS_TYPE error."""
        payload = {
            "presentation_id": "test-pres-011",
            "slide_id": "slide-011",
            "slide_number": 11,
            "narrative": "Test invalid analytics type",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 200}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/invalid_type",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_ANALYTICS_TYPE"
        assert error["category"] == "validation"
        assert error["retryable"] is False

    def test_invalid_layout(self):
        """Test INVALID_LAYOUT error."""
        payload = {
            "presentation_id": "test-pres-012",
            "slide_id": "slide-012",
            "slide_number": 12,
            "narrative": "Test invalid layout",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 200}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L99/revenue_over_time",
            json=payload
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == "INVALID_LAYOUT"
        assert error["category"] == "validation"
        assert error["retryable"] is False


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_exactly_2_data_points(self):
        """Test minimum valid data points (2)."""
        payload = {
            "presentation_id": "test-pres-013",
            "slide_id": "slide-013",
            "slide_number": 13,
            "narrative": "Test with exactly 2 data points",
            "data": [
                {"label": "Q1", "value": 100},
                {"label": "Q2", "value": 200}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_exactly_50_data_points(self):
        """Test maximum valid data points (50)."""
        payload = {
            "presentation_id": "test-pres-014",
            "slide_id": "slide-014",
            "slide_number": 14,
            "narrative": "Test with exactly 50 data points",
            "data": [
                {"label": f"Point {i}", "value": i * 100}
                for i in range(50)
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_zero_values(self):
        """Test that zero values are accepted."""
        payload = {
            "presentation_id": "test-pres-015",
            "slide_id": "slide-015",
            "slide_number": 15,
            "narrative": "Test with zero values",
            "data": [
                {"label": "Q1", "value": 0},
                {"label": "Q2", "value": 100},
                {"label": "Q3", "value": 0}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_negative_values(self):
        """Test that negative values are accepted."""
        payload = {
            "presentation_id": "test-pres-016",
            "slide_id": "slide-016",
            "slide_number": 16,
            "narrative": "Test with negative values",
            "data": [
                {"label": "Q1", "value": -100},
                {"label": "Q2", "value": 200},
                {"label": "Q3", "value": -50}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_very_large_values(self):
        """Test that very large values are accepted."""
        payload = {
            "presentation_id": "test-pres-017",
            "slide_id": "slide-017",
            "slide_number": 17,
            "narrative": "Test with very large values",
            "data": [
                {"label": "Q1", "value": 1e12},
                {"label": "Q2", "value": 2e12},
                {"label": "Q3", "value": 3e12}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_very_small_values(self):
        """Test that very small values are accepted."""
        payload = {
            "presentation_id": "test-pres-018",
            "slide_id": "slide-018",
            "slide_number": 18,
            "narrative": "Test with very small values",
            "data": [
                {"label": "Q1", "value": 1e-6},
                {"label": "Q2", "value": 2e-6},
                {"label": "Q3", "value": 3e-6}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_unicode_labels(self):
        """Test that Unicode labels are accepted."""
        payload = {
            "presentation_id": "test-pres-019",
            "slide_id": "slide-019",
            "slide_number": 19,
            "narrative": "Test with Unicode labels",
            "data": [
                {"label": "日本", "value": 100},
                {"label": "中国", "value": 200},
                {"label": "한국", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True

    def test_special_characters_in_labels(self):
        """Test that special characters in labels are accepted."""
        payload = {
            "presentation_id": "test-pres-020",
            "slide_id": "slide-020",
            "slide_number": 20,
            "narrative": "Test with special characters",
            "data": [
                {"label": "Q1 (2024)", "value": 100},
                {"label": "Q2 - 2024", "value": 200},
                {"label": "Q3 & Q4", "value": 300}
            ]
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/analytics/L02/revenue_over_time",
            json=payload
        )

        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True


class TestHealthAndMonitoring:
    """Test health check and monitoring endpoints."""

    def test_health_check(self):
        """Test GET /health endpoint."""
        response = requests.get(f"{BASE_URL}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics_microservice_v3"

    def test_stats_endpoint(self):
        """Test GET /stats endpoint."""
        response = requests.get(f"{BASE_URL}/stats")

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data


def run_all_tests():
    """Run all tests and generate report."""
    print("=" * 80)
    print("Analytics Service v3.1.2 - Director Integration Edge Case Tests")
    print("=" * 80)
    print()

    # Run pytest with detailed output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra"
    ])


if __name__ == "__main__":
    run_all_tests()
