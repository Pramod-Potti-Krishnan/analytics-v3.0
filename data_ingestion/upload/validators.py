"""
File validators for Data Ingestion Agent.

Validates uploaded files for:
- File size limits
- File format (CSV)
- Row/column count limits
- Data quality checks
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, BinaryIO
import io

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of file validation."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: dict

    @classmethod
    def success(cls, metadata: dict = None, warnings: List[str] = None) -> "ValidationResult":
        """Create successful validation result."""
        return cls(
            valid=True,
            errors=[],
            warnings=warnings or [],
            metadata=metadata or {}
        )

    @classmethod
    def failure(cls, errors: List[str], metadata: dict = None) -> "ValidationResult":
        """Create failed validation result."""
        return cls(
            valid=False,
            errors=errors,
            warnings=[],
            metadata=metadata or {}
        )


class FileValidator:
    """
    Validates uploaded files before processing.

    Checks:
    - File size within limits
    - Valid CSV format
    - Row count within limits
    - Column count within limits
    - No completely empty file
    """

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {".csv", ".txt", ".tsv"}

    # Supported MIME types
    SUPPORTED_MIME_TYPES = {
        "text/csv",
        "text/plain",
        "text/tab-separated-values",
        "application/csv",
        "application/vnd.ms-excel"
    }

    def __init__(
        self,
        max_file_size_bytes: int = 10 * 1024 * 1024,  # 10MB
        max_rows: int = 100000,
        max_columns: int = 100,
        min_rows: int = 1,
        min_columns: int = 1
    ):
        """
        Initialize file validator.

        Args:
            max_file_size_bytes: Maximum file size in bytes
            max_rows: Maximum number of rows
            max_columns: Maximum number of columns
            min_rows: Minimum number of rows (excluding header)
            min_columns: Minimum number of columns
        """
        self.max_file_size_bytes = max_file_size_bytes
        self.max_rows = max_rows
        self.max_columns = max_columns
        self.min_rows = min_rows
        self.min_columns = min_columns

    def validate_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate uploaded file.

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type (optional)

        Returns:
            ValidationResult with validation status
        """
        errors = []
        warnings = []
        metadata = {
            "filename": filename,
            "file_size_bytes": len(file_content),
            "content_type": content_type
        }

        # 1. Check file size
        if len(file_content) > self.max_file_size_bytes:
            errors.append(
                f"File too large: {len(file_content):,} bytes "
                f"(max: {self.max_file_size_bytes:,} bytes)"
            )
            return ValidationResult.failure(errors, metadata)

        if len(file_content) == 0:
            errors.append("File is empty")
            return ValidationResult.failure(errors, metadata)

        # 2. Check file extension
        ext = self._get_extension(filename)
        if ext not in self.SUPPORTED_EXTENSIONS:
            errors.append(
                f"Unsupported file type: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
            return ValidationResult.failure(errors, metadata)

        metadata["extension"] = ext

        # 3. Check MIME type if provided
        if content_type and content_type not in self.SUPPORTED_MIME_TYPES:
            warnings.append(
                f"Unexpected content type: {content_type}. "
                f"Proceeding with extension-based detection."
            )

        # 4. Quick CSV validation (check structure)
        csv_validation = self._validate_csv_structure(file_content, ext)
        if not csv_validation["valid"]:
            errors.extend(csv_validation["errors"])
            return ValidationResult.failure(errors, metadata)

        metadata.update(csv_validation["metadata"])
        warnings.extend(csv_validation.get("warnings", []))

        # 5. Check row count
        row_count = csv_validation["metadata"].get("row_count", 0)
        if row_count < self.min_rows:
            errors.append(
                f"Too few data rows: {row_count} "
                f"(minimum: {self.min_rows})"
            )
            return ValidationResult.failure(errors, metadata)

        if row_count > self.max_rows:
            errors.append(
                f"Too many rows: {row_count:,} "
                f"(maximum: {self.max_rows:,})"
            )
            return ValidationResult.failure(errors, metadata)

        # 6. Check column count
        col_count = csv_validation["metadata"].get("column_count", 0)
        if col_count < self.min_columns:
            errors.append(
                f"Too few columns: {col_count} "
                f"(minimum: {self.min_columns})"
            )
            return ValidationResult.failure(errors, metadata)

        if col_count > self.max_columns:
            errors.append(
                f"Too many columns: {col_count} "
                f"(maximum: {self.max_columns})"
            )
            return ValidationResult.failure(errors, metadata)

        logger.info(
            f"File validated: {filename} "
            f"({row_count:,} rows, {col_count} columns, "
            f"{len(file_content):,} bytes)"
        )

        return ValidationResult.success(metadata, warnings)

    def _get_extension(self, filename: str) -> str:
        """Get lowercase file extension."""
        import os
        _, ext = os.path.splitext(filename)
        return ext.lower()

    def _validate_csv_structure(self, content: bytes, extension: str) -> dict:
        """
        Validate CSV structure by sampling.

        Returns:
            Dict with valid, errors, warnings, metadata
        """
        import csv

        errors = []
        warnings = []
        metadata = {}

        try:
            # Decode content
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text = content.decode("latin-1")
                    warnings.append("File encoded as latin-1, converted to UTF-8")
                except UnicodeDecodeError:
                    errors.append("Unable to decode file - invalid encoding")
                    return {"valid": False, "errors": errors, "metadata": metadata}

            # Detect delimiter
            delimiter = self._detect_delimiter(text, extension)
            metadata["delimiter"] = delimiter

            # Parse CSV
            reader = csv.reader(io.StringIO(text), delimiter=delimiter)

            # Read header
            try:
                header = next(reader)
            except StopIteration:
                errors.append("File has no header row")
                return {"valid": False, "errors": errors, "metadata": metadata}

            if not header or all(h.strip() == "" for h in header):
                errors.append("Header row is empty")
                return {"valid": False, "errors": errors, "metadata": metadata}

            # Clean header names
            header = [h.strip() for h in header]
            metadata["column_count"] = len(header)
            metadata["columns"] = header

            # Check for duplicate columns
            seen_columns = set()
            duplicate_columns = []
            for col in header:
                if col in seen_columns:
                    duplicate_columns.append(col)
                seen_columns.add(col)

            if duplicate_columns:
                warnings.append(
                    f"Duplicate column names found: {duplicate_columns}. "
                    f"They will be renamed automatically."
                )

            # Count rows and check consistency
            row_count = 0
            inconsistent_rows = 0
            expected_cols = len(header)

            for row in reader:
                row_count += 1
                if len(row) != expected_cols:
                    inconsistent_rows += 1

                # Limit scanning for large files
                if row_count >= 10000 and row_count % 10000 == 0:
                    # Sample check every 10k rows
                    pass

            metadata["row_count"] = row_count

            if inconsistent_rows > 0:
                pct = (inconsistent_rows / row_count) * 100
                if pct > 10:
                    errors.append(
                        f"Too many rows with inconsistent column count: "
                        f"{inconsistent_rows:,} ({pct:.1f}%)"
                    )
                    return {"valid": False, "errors": errors, "metadata": metadata}
                else:
                    warnings.append(
                        f"{inconsistent_rows:,} rows have inconsistent column count "
                        f"({pct:.1f}%) - they will be handled gracefully"
                    )

            return {
                "valid": True,
                "errors": [],
                "warnings": warnings,
                "metadata": metadata
            }

        except csv.Error as e:
            errors.append(f"Invalid CSV format: {str(e)}")
            return {"valid": False, "errors": errors, "metadata": metadata}
        except Exception as e:
            errors.append(f"Error parsing file: {str(e)}")
            return {"valid": False, "errors": errors, "metadata": metadata}

    def _detect_delimiter(self, text: str, extension: str) -> str:
        """
        Detect CSV delimiter from content.

        Args:
            text: File content as text
            extension: File extension

        Returns:
            Detected delimiter character
        """
        if extension == ".tsv":
            return "\t"

        # Sample first few lines
        sample = text[:5000]
        lines = sample.split("\n")[:5]

        # Count potential delimiters
        delimiters = {",": 0, "\t": 0, ";": 0, "|": 0}

        for line in lines:
            for delim in delimiters:
                delimiters[delim] += line.count(delim)

        # Return most common delimiter
        best_delim = max(delimiters, key=delimiters.get)

        # Default to comma if no clear winner
        if delimiters[best_delim] == 0:
            return ","

        return best_delim
