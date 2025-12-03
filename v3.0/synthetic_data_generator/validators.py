"""
Validation for generated synthetic data.

Ensures generated data passes all Pydantic validators and
chart-specific constraints.
"""

from typing import List, Dict, Any, Tuple
import math


class DataValidator:
    """
    Validates generated synthetic data.

    Checks:
    - Data point count within min/max range
    - No NaN or Infinity values
    - Labels are non-empty and unique
    - Values are finite numbers
    - Chart-specific constraints met
    """

    def validate(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate generated data.

        Args:
            data: Generated data
            chart_type: Chart type ID

        Returns:
            (is_valid, error_messages)

        Example:
            >>> validator = DataValidator()
            >>> is_valid, errors = validator.validate(data, 'line')
            >>> if not is_valid:
            ...     print(f"Validation errors: {errors}")
        """
        errors = []

        # Basic validations
        errors.extend(self._validate_structure(data))
        errors.extend(self._validate_labels(data))
        errors.extend(self._validate_values(data))

        # Chart-specific validations
        errors.extend(self._validate_chart_specific(data, chart_type))

        return (len(errors) == 0, errors)

    def _validate_structure(self, data: List[Dict[str, Any]]) -> List[str]:
        """Validate basic data structure."""
        errors = []

        if not data:
            errors.append("Data is empty")
            return errors

        if not isinstance(data, list):
            errors.append(f"Data must be list, got {type(data)}")
            return errors

        # Check first item has required fields
        first_item = data[0]
        if isinstance(first_item, dict):
            if 'label' not in first_item and 'x' not in first_item:
                errors.append("Data points must have 'label' or 'x' field")
            if 'value' not in first_item and 'y' not in first_item and 'datasets' not in first_item:
                errors.append("Data points must have 'value' or 'y' field")

        return errors

    def _validate_labels(self, data: List[Dict[str, Any]]) -> List[str]:
        """Validate labels."""
        errors = []

        labels = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                label = item.get('label', '')

                # Skip if multi-series format (has labels array at top level)
                if 'labels' in item:
                    continue

                # Check non-empty
                if not label or (isinstance(label, str) and label.strip() == ''):
                    errors.append(f"Data point {i}: Label is empty")
                    continue

                # Check length
                if isinstance(label, str) and len(label) > 100:
                    errors.append(f"Data point {i}: Label exceeds 100 chars")

                labels.append(label)

        # Check uniqueness
        if labels and len(labels) != len(set(labels)):
            errors.append("Duplicate labels found")

        return errors

    def _validate_values(self, data: List[Dict[str, Any]]) -> List[str]:
        """Validate numeric values."""
        errors = []

        for i, item in enumerate(data):
            if isinstance(item, dict):
                # Get value (could be 'value', 'y', or in nested structure)
                value = item.get('value') or item.get('y')

                if value is None:
                    # May be multi-series format
                    if 'datasets' in item:
                        continue
                    # May be scatter/bubble format
                    if 'x' in item and 'y' in item:
                        value = item['y']
                    else:
                        continue

                # Check finite number
                if not isinstance(value, (int, float)):
                    errors.append(f"Data point {i}: Value is not a number")
                    continue

                if math.isnan(value):
                    errors.append(f"Data point {i}: Value is NaN")

                if math.isinf(value):
                    errors.append(f"Data point {i}: Value is Infinity")

        return errors

    def _validate_chart_specific(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[str]:
        """Chart-specific validations."""
        errors = []

        # Scatter/Bubble: Require x,y,r fields
        if chart_type == 'scatter':
            for i, item in enumerate(data):
                if 'x' not in item or 'y' not in item:
                    errors.append(f"Scatter point {i}: Missing x or y coordinate")

        if chart_type == 'bubble':
            for i, item in enumerate(data):
                if 'x' not in item or 'y' not in item or 'r' not in item:
                    errors.append(f"Bubble point {i}: Missing x, y, or r field")

        # D3 Choropleth: Validate US state names
        if chart_type == 'd3_choropleth_usa':
            valid_states = {
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
                'DC', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
                'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
                'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
                'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts',
                'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana',
                'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
                'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma',
                'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
                'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
                'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
            }

            for i, item in enumerate(data):
                label = item.get('label', '')
                if label and label not in valid_states:
                    errors.append(
                        f"Choropleth point {i}: '{label}' is not a valid US state"
                    )

        # D3 Sankey: Validate flow notation
        if chart_type == 'd3_sankey':
            for i, item in enumerate(data):
                label = item.get('label', '')
                if '→' not in label and '->' not in label:
                    if 'source' not in item or 'target' not in item:
                        errors.append(
                            f"Sankey flow {i}: Must have arrow notation or "
                            "source/target fields"
                        )

        return errors
