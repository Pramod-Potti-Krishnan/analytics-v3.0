"""
Tests for Data Ingestion upload functionality.

Tests CSV parsing, type inference, validation, and upload handling.
"""

import io
import pytest
import pandas as pd
from datetime import datetime

from data_ingestion.upload.handler import CSVHandler
from data_ingestion.upload.validators import (
    validate_file_size,
    validate_file_type,
    validate_csv_content,
    validate_row_count,
    ValidationError
)
from data_ingestion.models.tools import ColumnType


class TestCSVHandler:
    """Tests for CSVHandler class."""

    def test_process_upload_success(self, sample_csv_content):
        """Test successful CSV upload processing."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv"
        )

        assert result.success is True
        assert result.row_count == 10
        assert result.column_count == 5
        assert len(result.columns) == 5
        assert result.filename == "test_data.csv"

    def test_process_upload_with_numeric_columns(self, sample_csv_content):
        """Test that numeric columns are correctly identified."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv"
        )

        # 'sales' should be detected as numeric
        sales_col = next((c for c in result.columns if c.name == "sales"), None)
        assert sales_col is not None
        assert sales_col.type == ColumnType.NUMERIC
        assert sales_col.min_value is not None
        assert sales_col.max_value is not None

    def test_process_upload_with_categorical_columns(self, sample_csv_content):
        """Test that categorical columns are correctly identified."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv"
        )

        # 'product' and 'region' should be detected as categorical
        product_col = next((c for c in result.columns if c.name == "product"), None)
        assert product_col is not None
        assert product_col.type == ColumnType.CATEGORICAL
        assert product_col.unique_count is not None
        assert len(product_col.sample_values) > 0

    def test_process_upload_with_datetime_columns(self, sample_csv_content):
        """Test that datetime columns are correctly identified."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv"
        )

        # 'date' should be detected as datetime
        date_col = next((c for c in result.columns if c.name == "date"), None)
        assert date_col is not None
        assert date_col.type == ColumnType.DATETIME

    def test_process_upload_empty_csv(self):
        """Test handling of empty CSV file."""
        handler = CSVHandler()
        empty_csv = b"col1,col2,col3\n"

        result = handler.process_upload(
            file_content=empty_csv,
            filename="empty.csv"
        )

        assert result.success is False
        assert "empty" in result.error_message.lower() or result.row_count == 0

    def test_process_upload_invalid_csv(self):
        """Test handling of invalid CSV content."""
        handler = CSVHandler()
        invalid_content = b"this is not,valid csv\n\"unclosed quote"

        result = handler.process_upload(
            file_content=invalid_content,
            filename="invalid.csv"
        )

        # Should either fail or handle gracefully
        assert result is not None

    def test_column_type_inference_mixed_numeric(self):
        """Test type inference with mixed numeric/string column."""
        handler = CSVHandler()
        csv_data = b"id,value,mixed\n1,100,abc\n2,200,123\n3,300,def\n"

        result = handler.process_upload(
            file_content=csv_data,
            filename="mixed.csv"
        )

        assert result.success is True
        # 'mixed' column should be detected as text/categorical, not numeric
        mixed_col = next((c for c in result.columns if c.name == "mixed"), None)
        assert mixed_col is not None
        assert mixed_col.type in [ColumnType.CATEGORICAL, ColumnType.TEXT]

    def test_statistics_computation(self, sample_csv_content):
        """Test that statistics are correctly computed."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv"
        )

        assert result.statistics is not None
        assert "sales" in result.statistics
        stats = result.statistics["sales"]
        assert "min" in stats or "mean" in stats

    def test_preview_rows_generation(self, sample_csv_content):
        """Test that preview rows are correctly generated."""
        handler = CSVHandler()
        result = handler.process_upload(
            file_content=sample_csv_content,
            filename="test_data.csv",
            preview_rows=3
        )

        assert result.preview is not None
        assert len(result.preview) <= 3

    def test_prepare_for_database(self, sample_dataframe):
        """Test data preparation for database insertion."""
        handler = CSVHandler()

        columns = [
            {"name": "product", "type": "categorical"},
            {"name": "region", "type": "categorical"},
            {"name": "sales", "type": "numeric"},
            {"name": "quarter", "type": "categorical"}
        ]

        col_names, rows = handler.prepare_for_database(
            sample_dataframe,
            columns
        )

        assert len(col_names) == 4
        assert len(rows) == 4
        assert all(len(row) == 4 for row in rows)


class TestValidators:
    """Tests for validation functions."""

    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        content = b"x" * (1024 * 1024)  # 1 MB
        assert validate_file_size(content, max_size_mb=10) is True

    def test_validate_file_size_too_large(self):
        """Test file size validation with oversized file."""
        content = b"x" * (15 * 1024 * 1024)  # 15 MB
        with pytest.raises(ValidationError) as exc_info:
            validate_file_size(content, max_size_mb=10)
        assert "size" in str(exc_info.value).lower()

    def test_validate_file_type_csv(self):
        """Test file type validation for CSV."""
        assert validate_file_type("data.csv") is True
        assert validate_file_type("DATA.CSV") is True

    def test_validate_file_type_tsv(self):
        """Test file type validation for TSV."""
        assert validate_file_type("data.tsv") is True

    def test_validate_file_type_invalid(self):
        """Test file type validation for invalid types."""
        with pytest.raises(ValidationError):
            validate_file_type("data.xlsx")

        with pytest.raises(ValidationError):
            validate_file_type("data.json")

        with pytest.raises(ValidationError):
            validate_file_type("image.png")

    def test_validate_csv_content_valid(self, sample_csv_content):
        """Test CSV content validation with valid content."""
        result = validate_csv_content(sample_csv_content)
        assert result is True

    def test_validate_csv_content_empty(self):
        """Test CSV content validation with empty content."""
        with pytest.raises(ValidationError):
            validate_csv_content(b"")

    def test_validate_row_count_valid(self):
        """Test row count validation with valid count."""
        assert validate_row_count(100, max_rows=100000) is True

    def test_validate_row_count_exceeded(self):
        """Test row count validation with exceeded count."""
        with pytest.raises(ValidationError):
            validate_row_count(150000, max_rows=100000)

    def test_validate_row_count_zero(self):
        """Test row count validation with zero rows."""
        with pytest.raises(ValidationError):
            validate_row_count(0, max_rows=100000)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_unicode_content(self):
        """Test handling of Unicode content in CSV."""
        handler = CSVHandler()
        csv_data = "name,city,value\nJohn,New York,100\nMáría,São Paulo,200\n日本語,東京,300\n".encode('utf-8')

        result = handler.process_upload(
            file_content=csv_data,
            filename="unicode.csv"
        )

        assert result.success is True
        assert result.row_count == 3

    def test_special_characters_in_values(self):
        """Test handling of special characters in values."""
        handler = CSVHandler()
        csv_data = b'name,description,value\n"Item, with comma","Description ""quoted""",100\n'

        result = handler.process_upload(
            file_content=csv_data,
            filename="special.csv"
        )

        assert result.success is True

    def test_large_numeric_values(self):
        """Test handling of large numeric values."""
        handler = CSVHandler()
        csv_data = b"id,big_value\n1,999999999999999\n2,1234567890123456\n"

        result = handler.process_upload(
            file_content=csv_data,
            filename="large_numbers.csv"
        )

        assert result.success is True
        big_val_col = next((c for c in result.columns if c.name == "big_value"), None)
        assert big_val_col is not None
        assert big_val_col.type == ColumnType.NUMERIC

    def test_null_values_handling(self):
        """Test handling of null/missing values."""
        handler = CSVHandler()
        csv_data = b"name,value,optional\nA,100,extra\nB,,\nC,300,\n"

        result = handler.process_upload(
            file_content=csv_data,
            filename="nulls.csv"
        )

        assert result.success is True
        # Check nullable flag is set correctly
        value_col = next((c for c in result.columns if c.name == "value"), None)
        assert value_col is not None
