"""
CSV upload handler for Data Ingestion Agent.

Handles CSV parsing, type inference, and data table creation.
"""

import logging
import io
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

from .validators import FileValidator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class ColumnSchema:
    """Schema information for a single column."""
    name: str
    original_name: str
    dtype: str
    pandas_dtype: str
    nullable: bool
    unique_count: int
    null_count: int
    sample_values: List[Any]
    statistics: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "original_name": self.original_name,
            "dtype": self.dtype,
            "pandas_dtype": self.pandas_dtype,
            "nullable": self.nullable,
            "unique_count": self.unique_count,
            "null_count": self.null_count,
            "sample_values": self.sample_values,
            "statistics": self.statistics
        }


@dataclass
class UploadResult:
    """Result of CSV upload processing."""
    success: bool
    session_id: Optional[str]
    filename: str
    row_count: int
    column_count: int
    columns: List[ColumnSchema]
    data_statistics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    file_size_bytes: int
    dataframe: Optional[pd.DataFrame] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "success": self.success,
            "session_id": self.session_id,
            "filename": self.filename,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": [c.to_dict() for c in self.columns],
            "data_statistics": self.data_statistics,
            "errors": self.errors,
            "warnings": self.warnings,
            "file_size_bytes": self.file_size_bytes
        }


class CSVHandler:
    """
    Handles CSV file parsing and schema inference.

    Responsibilities:
    - Parse CSV files with auto-delimiter detection
    - Infer column types (numeric, categorical, datetime, text)
    - Generate column statistics
    - Prepare data for PostgreSQL insertion
    """

    # Type classification thresholds
    CATEGORICAL_THRESHOLD = 0.5  # If unique ratio < 0.5, consider categorical
    MAX_CATEGORICAL_UNIQUE = 100  # Max unique values for categorical

    def __init__(
        self,
        max_file_size_bytes: int = 10 * 1024 * 1024,
        max_rows: int = 100000,
        max_columns: int = 100,
        sample_size: int = 5
    ):
        """
        Initialize CSV handler.

        Args:
            max_file_size_bytes: Maximum file size
            max_rows: Maximum rows
            max_columns: Maximum columns
            sample_size: Sample values per column
        """
        self.validator = FileValidator(
            max_file_size_bytes=max_file_size_bytes,
            max_rows=max_rows,
            max_columns=max_columns
        )
        self.sample_size = sample_size

    def process_upload(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None,
        presentation_id: Optional[str] = None,
        slide_id: Optional[str] = None
    ) -> UploadResult:
        """
        Process an uploaded CSV file.

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type
            presentation_id: Optional presentation context
            slide_id: Optional slide context

        Returns:
            UploadResult with parsed data and schema
        """
        errors = []
        warnings = []

        # Step 1: Validate file
        validation = self.validator.validate_file(
            file_content, filename, content_type
        )

        if not validation.valid:
            return UploadResult(
                success=False,
                session_id=None,
                filename=filename,
                row_count=0,
                column_count=0,
                columns=[],
                data_statistics={},
                errors=validation.errors,
                warnings=validation.warnings,
                file_size_bytes=len(file_content)
            )

        warnings.extend(validation.warnings)

        # Step 2: Parse CSV into DataFrame
        try:
            df, parse_warnings = self._parse_csv(
                file_content,
                validation.metadata.get("delimiter", ",")
            )
            warnings.extend(parse_warnings)
        except Exception as e:
            logger.error(f"Failed to parse CSV: {e}")
            return UploadResult(
                success=False,
                session_id=None,
                filename=filename,
                row_count=0,
                column_count=0,
                columns=[],
                data_statistics={},
                errors=[f"Failed to parse CSV: {str(e)}"],
                warnings=warnings,
                file_size_bytes=len(file_content)
            )

        # Step 3: Infer column schemas
        columns = self._infer_column_schemas(df)

        # Step 4: Compute data statistics
        data_statistics = self._compute_statistics(df, columns)

        # Step 5: Generate session ID
        session_id = str(uuid.uuid4())

        logger.info(
            f"Processed CSV: {filename} -> {len(df)} rows, "
            f"{len(columns)} columns, session {session_id}"
        )

        return UploadResult(
            success=True,
            session_id=session_id,
            filename=filename,
            row_count=len(df),
            column_count=len(columns),
            columns=columns,
            data_statistics=data_statistics,
            errors=[],
            warnings=warnings,
            file_size_bytes=len(file_content),
            dataframe=df
        )

    def _parse_csv(
        self,
        content: bytes,
        delimiter: str
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Parse CSV content into DataFrame.

        Args:
            content: File content as bytes
            delimiter: Column delimiter

        Returns:
            Tuple of (DataFrame, warnings)
        """
        warnings = []

        # Try UTF-8 first, fallback to latin-1
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
            warnings.append("File encoded as latin-1, converted to UTF-8")

        # Parse with pandas
        df = pd.read_csv(
            io.StringIO(text),
            delimiter=delimiter,
            low_memory=False,
            na_values=["", "NA", "N/A", "null", "NULL", "None", "nan", "NaN"],
            keep_default_na=True
        )

        # Clean column names
        df.columns = self._clean_column_names(df.columns.tolist())

        # Drop completely empty rows
        original_rows = len(df)
        df = df.dropna(how="all")
        if len(df) < original_rows:
            warnings.append(
                f"Removed {original_rows - len(df)} completely empty rows"
            )

        return df, warnings

    def _clean_column_names(self, columns: List[str]) -> List[str]:
        """
        Clean and deduplicate column names.

        Args:
            columns: Original column names

        Returns:
            Cleaned column names
        """
        import re

        cleaned = []
        seen = {}

        for col in columns:
            # Clean the name
            name = str(col).strip()

            # Replace invalid characters
            name = re.sub(r'[^\w\s]', '_', name)
            name = re.sub(r'\s+', '_', name)
            name = re.sub(r'_+', '_', name)
            name = name.strip('_')

            # Ensure not empty
            if not name:
                name = "column"

            # Ensure starts with letter
            if name[0].isdigit():
                name = f"col_{name}"

            # Handle duplicates
            original_name = name
            counter = 1
            while name in seen:
                name = f"{original_name}_{counter}"
                counter += 1

            seen[name] = True
            cleaned.append(name)

        return cleaned

    def _infer_column_schemas(self, df: pd.DataFrame) -> List[ColumnSchema]:
        """
        Infer schema for each column.

        Args:
            df: Input DataFrame

        Returns:
            List of ColumnSchema objects
        """
        schemas = []

        for col in df.columns:
            series = df[col]

            # Get pandas dtype
            pandas_dtype = str(series.dtype)

            # Infer semantic type
            dtype = self._infer_semantic_type(series)

            # Compute statistics
            null_count = int(series.isna().sum())
            unique_count = int(series.nunique())
            nullable = null_count > 0

            # Get sample values (non-null)
            non_null = series.dropna()
            if len(non_null) > 0:
                sample_values = non_null.head(self.sample_size).tolist()
                # Convert numpy types to Python types
                sample_values = [self._to_python_type(v) for v in sample_values]
            else:
                sample_values = []

            # Compute type-specific statistics
            statistics = self._compute_column_statistics(series, dtype)

            schema = ColumnSchema(
                name=col,
                original_name=col,
                dtype=dtype,
                pandas_dtype=pandas_dtype,
                nullable=nullable,
                unique_count=unique_count,
                null_count=null_count,
                sample_values=sample_values,
                statistics=statistics
            )

            schemas.append(schema)

        return schemas

    def _infer_semantic_type(self, series: pd.Series) -> str:
        """
        Infer semantic type for a column.

        Types:
        - numeric: Integer or float values
        - categorical: Limited set of repeated values
        - datetime: Date/time values
        - text: Free-form text

        Args:
            series: Pandas Series

        Returns:
            Semantic type string
        """
        # Check if already numeric
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"

        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        # Try to parse as numeric
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                pd.to_numeric(non_null)
                return "numeric"
            except (ValueError, TypeError):
                pass

            # Try to parse as datetime
            try:
                pd.to_datetime(non_null, infer_datetime_format=True)
                return "datetime"
            except (ValueError, TypeError):
                pass

        # Check if categorical
        if len(non_null) > 0:
            unique_ratio = series.nunique() / len(non_null)
            unique_count = series.nunique()

            if (unique_ratio < self.CATEGORICAL_THRESHOLD and
                    unique_count <= self.MAX_CATEGORICAL_UNIQUE):
                return "categorical"

        return "text"

    def _compute_column_statistics(
        self,
        series: pd.Series,
        dtype: str
    ) -> Dict[str, Any]:
        """
        Compute statistics for a column based on its type.

        Args:
            series: Pandas Series
            dtype: Inferred semantic type

        Returns:
            Statistics dictionary
        """
        stats = {}

        non_null = series.dropna()
        if len(non_null) == 0:
            return stats

        if dtype == "numeric":
            try:
                numeric = pd.to_numeric(non_null, errors="coerce").dropna()
                if len(numeric) > 0:
                    stats = {
                        "min": float(numeric.min()),
                        "max": float(numeric.max()),
                        "mean": float(numeric.mean()),
                        "median": float(numeric.median()),
                        "std": float(numeric.std()) if len(numeric) > 1 else 0,
                        "sum": float(numeric.sum())
                    }
            except Exception:
                pass

        elif dtype == "categorical":
            value_counts = non_null.value_counts()
            stats = {
                "top_values": value_counts.head(10).to_dict(),
                "category_count": int(non_null.nunique())
            }

        elif dtype == "datetime":
            try:
                dates = pd.to_datetime(non_null, errors="coerce").dropna()
                if len(dates) > 0:
                    stats = {
                        "min_date": str(dates.min()),
                        "max_date": str(dates.max()),
                        "date_range_days": (dates.max() - dates.min()).days
                    }
            except Exception:
                pass

        elif dtype == "text":
            lengths = non_null.astype(str).str.len()
            stats = {
                "min_length": int(lengths.min()),
                "max_length": int(lengths.max()),
                "avg_length": float(lengths.mean())
            }

        return stats

    def _compute_statistics(
        self,
        df: pd.DataFrame,
        columns: List[ColumnSchema]
    ) -> Dict[str, Any]:
        """
        Compute overall data statistics.

        Args:
            df: Input DataFrame
            columns: Column schemas

        Returns:
            Statistics dictionary
        """
        numeric_cols = [c.name for c in columns if c.dtype == "numeric"]
        categorical_cols = [c.name for c in columns if c.dtype == "categorical"]
        datetime_cols = [c.name for c in columns if c.dtype == "datetime"]
        text_cols = [c.name for c in columns if c.dtype == "text"]

        # Compute correlation matrix for numeric columns
        correlation_matrix = None
        if len(numeric_cols) >= 2:
            try:
                numeric_df = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
                corr = numeric_df.corr()
                # Find highly correlated pairs
                high_corr = []
                for i, col1 in enumerate(numeric_cols):
                    for j, col2 in enumerate(numeric_cols):
                        if i < j:
                            corr_val = corr.loc[col1, col2]
                            if abs(corr_val) > 0.7 and not pd.isna(corr_val):
                                high_corr.append({
                                    "columns": [col1, col2],
                                    "correlation": round(corr_val, 3)
                                })
                correlation_matrix = {
                    "high_correlations": high_corr
                }
            except Exception:
                pass

        return {
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols,
            "text_columns": text_cols,
            "total_nulls": int(df.isna().sum().sum()),
            "null_percentage": round(
                (df.isna().sum().sum() / (len(df) * len(df.columns))) * 100, 2
            ) if len(df) > 0 else 0,
            "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
            "correlation_analysis": correlation_matrix
        }

    @staticmethod
    def _to_python_type(value: Any) -> Any:
        """Convert numpy types to Python native types."""
        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        if pd.isna(value):
            return None
        return value

    def prepare_for_database(
        self,
        df: pd.DataFrame,
        columns: List[ColumnSchema]
    ) -> Tuple[List[str], List[List[Any]]]:
        """
        Prepare DataFrame for database insertion.

        Args:
            df: Input DataFrame
            columns: Column schemas

        Returns:
            Tuple of (column_names, rows)
        """
        column_names = [c.name for c in columns]
        rows = []

        for _, row in df.iterrows():
            row_data = []
            for col in columns:
                value = row[col.name]

                # Convert to appropriate type
                if pd.isna(value):
                    row_data.append(None)
                elif col.dtype == "numeric":
                    try:
                        row_data.append(float(value))
                    except (ValueError, TypeError):
                        row_data.append(None)
                elif col.dtype == "datetime":
                    try:
                        dt = pd.to_datetime(value)
                        row_data.append(dt.isoformat() if not pd.isna(dt) else None)
                    except (ValueError, TypeError):
                        row_data.append(str(value))
                else:
                    row_data.append(str(value) if value is not None else None)

            rows.append(row_data)

        return column_names, rows
