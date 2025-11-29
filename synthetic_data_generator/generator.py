"""
Core synthetic data generator for Analytics Microservice v3.

Generates realistic, context-aware data for all 18 chart types based on:
- Chart type constraints (from chart_catalog.py)
- User narrative context (extracted patterns)
- Business scenarios (pre-defined templates)
"""

from typing import List, Dict, Any, Optional
import random
import math

from .scenarios import SCENARIO_LIBRARY, BusinessScenario, get_scenario_for_chart_type
from .constraints import ChartConstraints
from .formatters import DataFormatter
from .validators import DataValidator
from .narrative_parser import NarrativeParser


class SyntheticDataGenerator:
    """
    Main synthetic data generation engine.

    Generates realistic data based on:
    - Chart type constraints (from chart_catalog.py)
    - User narrative context (extracted patterns)
    - Business scenarios (pre-defined templates)
    """

    def __init__(self):
        self.constraints = ChartConstraints()
        self.formatter = DataFormatter()
        self.validator = DataValidator()
        self.parser = NarrativeParser()

    def generate(
        self,
        chart_type: str,
        narrative: Optional[str] = None,
        num_points: Optional[int] = None,
        scenario: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate synthetic data for a given chart type.

        Args:
            chart_type: Chart type ID (e.g., 'line', 'd3_choropleth_usa')
            narrative: User narrative for context extraction
            num_points: Number of data points (auto-determined if None)
            scenario: Business scenario name (e.g., 'revenue_growth')
            **kwargs: Additional generation parameters

        Returns:
            List of {label, value} dictionaries ready for chart rendering

        Example:
            >>> gen = SyntheticDataGenerator()
            >>> data = gen.generate(
            ...     chart_type='line',
            ...     narrative='Show quarterly revenue growth for 2024',
            ...     scenario='revenue_growth'
            ... )
            >>> # Returns: [
            >>> #   {"label": "Q1 2024", "value": 125000},
            >>> #   {"label": "Q2 2024", "value": 145000},
            >>> #   {"label": "Q3 2024", "value": 195000},
            >>> #   {"label": "Q4 2024", "value": 220000}
            >>> # ]
        """
        # 1. Get chart constraints
        constraints = self.constraints.get_constraints(chart_type)

        # 2. Determine number of points
        if num_points is None:
            num_points = self._determine_optimal_points(
                chart_type, constraints, narrative
            )

        # 3. Parse narrative context (if provided)
        context = self.parser.parse(narrative) if narrative else {}

        # 4. Select or create scenario
        scenario_obj = self._get_scenario(scenario, chart_type, context)

        # 5. Generate base data
        data = self._generate_data(
            chart_type=chart_type,
            num_points=num_points,
            scenario=scenario_obj,
            context=context,
            constraints=constraints
        )

        # 6. Format for chart type
        formatted_data = self.formatter.format(data, chart_type)

        # 7. Validate
        is_valid, errors = self.validator.validate(formatted_data, chart_type)
        if not is_valid:
            raise ValueError(f"Generated data failed validation: {errors}")

        return formatted_data

    def _determine_optimal_points(
        self,
        chart_type: str,
        constraints: dict,
        narrative: Optional[str]
    ) -> int:
        """Determine optimal number of data points based on context."""
        # Parse narrative for timeframe hints
        if narrative:
            narrative_lower = narrative.lower()
            if 'quarterly' in narrative_lower or 'quarter' in narrative_lower:
                return 4
            if 'monthly' in narrative_lower or 'month' in narrative_lower:
                return 12
            if 'weekly' in narrative_lower:
                return min(52, constraints['max_data_points'])
            if 'top 10' in narrative_lower or 'top ten' in narrative_lower:
                return 10
            if 'top 5' in narrative_lower or 'top five' in narrative_lower:
                return 5

        # Use chart type optimal range
        optimal_str = str(constraints.get('optimal_data_points', '5-10'))

        # Extract numeric range from strings like "5-15 flows" or "5-10"
        import re
        match = re.search(r'(\d+)-(\d+)', optimal_str)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            return random.randint(low, high)

        # Try single number
        match = re.search(r'(\d+)', optimal_str)
        if match:
            return int(match.group(1))

        # Fallback to middle of min-max range
        return (constraints['min_data_points'] + constraints['max_data_points']) // 2

    def _get_scenario(
        self,
        scenario_name: Optional[str],
        chart_type: str,
        context: dict
    ) -> BusinessScenario:
        """Get or create business scenario."""
        if scenario_name and scenario_name in SCENARIO_LIBRARY:
            return SCENARIO_LIBRARY[scenario_name]

        # Auto-select scenario based on chart type
        return get_scenario_for_chart_type(chart_type)

    def _generate_data(
        self,
        chart_type: str,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate base data using scenario template."""
        # Delegate to chart-type-specific generators
        generator_method = f'_generate_{chart_type}_data'
        if hasattr(self, generator_method):
            return getattr(self, generator_method)(
                num_points, scenario, context, constraints
            )

        # Fallback to simple generation
        return self._generate_simple_data(
            num_points, scenario, context, constraints
        )

    # Chart-type-specific generators (18 methods)

    def _generate_line_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for line charts (time series)."""
        labels = self._generate_time_labels(num_points, context)
        values = self._generate_trend_values(
            num_points,
            trend=scenario.trend,
            volatility=scenario.volatility,
            base_value=scenario.base_value,
            seasonality=scenario.seasonality
        )

        return [
            {"label": label, "value": value}
            for label, value in zip(labels, values)
        ]

    def _generate_bar_vertical_data(self, num_points, scenario, context, constraints):
        """Generate data for vertical bar charts."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_bar_horizontal_data(self, num_points, scenario, context, constraints):
        """Generate data for horizontal bar charts."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_pie_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for pie charts (must sum to 100 for percentages)."""
        labels = self._generate_category_labels(num_points, context)

        # Generate values that sum to 100 (for market share)
        if scenario.value_format == 'percentage':
            values = self._generate_percentage_distribution(num_points)
        else:
            values = self._generate_random_values(
                num_points,
                base_value=scenario.base_value,
                variance=scenario.volatility
            )

        return [
            {"label": label, "value": value}
            for label, value in zip(labels, values)
        ]

    def _generate_doughnut_data(self, num_points, scenario, context, constraints):
        """Generate data for doughnut charts (same as pie)."""
        return self._generate_pie_data(num_points, scenario, context, constraints)

    def _generate_scatter_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for scatter plots with correlation."""
        labels = [f"Point {i+1}" for i in range(num_points)]

        # Generate correlated x,y pairs
        correlation = scenario.metadata.get('correlation', 0.7)
        x_values = [random.uniform(0, 100) for _ in range(num_points)]
        y_values = []

        for x in x_values:
            # Add correlation
            y_base = x * correlation
            # Add variance
            variance = random.uniform(-20, 20) * (1 - abs(correlation))
            y = max(0, y_base + variance)
            y_values.append(round(y, 2))

        return [
            {"label": label, "value": y, "x": round(x, 2), "y": y}
            for label, x, y in zip(labels, x_values, y_values)
        ]

    def _generate_bubble_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for bubble charts (x, y, r)."""
        scatter_data = self._generate_scatter_data(num_points, scenario, context, constraints)

        # Add bubble size (r)
        for item in scatter_data:
            item['r'] = random.randint(10, 30)

        return scatter_data

    def _generate_radar_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for radar charts (normalized 0-100)."""
        # Performance metrics labels
        metrics = ['Speed', 'Power', 'Agility', 'Endurance', 'Accuracy', 'Efficiency']
        labels = metrics[:min(num_points, len(metrics))]

        # Generate normalized values (0-100)
        values = [
            round(random.uniform(50, 100), 1)
            for _ in range(len(labels))
        ]

        return [
            {"label": label, "value": value}
            for label, value in zip(labels, values)
        ]

    def _generate_polar_area_data(self, num_points, scenario, context, constraints):
        """Generate data for polar area charts."""
        return self._generate_pie_data(num_points, scenario, context, constraints)

    def _generate_area_data(self, num_points, scenario, context, constraints):
        """Generate data for area charts."""
        return self._generate_line_data(num_points, scenario, context, constraints)

    def _generate_area_stacked_data(self, num_points, scenario, context, constraints):
        """Generate data for stacked area charts (multi-series)."""
        return self._generate_line_data(num_points, scenario, context, constraints)

    def _generate_bar_grouped_data(self, num_points, scenario, context, constraints):
        """Generate data for grouped bar charts (multi-series)."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_bar_stacked_data(self, num_points, scenario, context, constraints):
        """Generate data for stacked bar charts (multi-series)."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_waterfall_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for waterfall charts (positive/negative changes)."""
        labels = []
        values = []

        # Starting value
        labels.append("Starting Balance")
        values.append(scenario.base_value)

        # Changes (positive and negative)
        for i in range(num_points - 2):  # Reserve space for total
            labels.append(f"Change {i+1}")
            # Mix of positive and negative
            change = scenario.base_value * random.uniform(-0.2, 0.3)
            values.append(round(change, 2))

        # Final total
        labels.append("Final Total")
        total = sum(values)
        values.append(round(total, 2))

        return [
            {"label": label, "value": value}
            for label, value in zip(labels, values)
        ]

    def _generate_d3_treemap_data(self, num_points, scenario, context, constraints):
        """Generate data for D3 treemap (hierarchical)."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_d3_sunburst_data(self, num_points, scenario, context, constraints):
        """Generate data for D3 sunburst (hierarchical)."""
        return self._generate_simple_data(num_points, scenario, context, constraints)

    def _generate_d3_choropleth_usa_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for US choropleth map."""
        # Top 50 US states by population
        us_states = [
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
            'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MD', 'MO', 'WI',
            'CO', 'MN', 'SC', 'AL', 'LA', 'KY', 'OR', 'OK', 'CT', 'UT',
            'IA', 'NV', 'AR', 'MS', 'KS', 'NM', 'NE', 'ID', 'WV', 'HI',
            'NH', 'ME', 'RI', 'MT', 'DE', 'SD', 'ND', 'AK', 'VT', 'WY'
        ]

        # Select top N states
        selected_states = us_states[:min(num_points, len(us_states))]

        # Generate values with geographic variation
        base_value = scenario.base_value
        values = []
        for i, state in enumerate(selected_states):
            # Larger states get higher values (with variance)
            state_multiplier = 1.0 - (i * 0.05)  # Decaying multiplier
            variance = random.uniform(0.8, 1.2)
            value = base_value * state_multiplier * variance
            values.append(round(value, 2))

        return [
            {"label": state, "value": value}
            for state, value in zip(selected_states, values)
        ]

    def _generate_d3_sankey_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Generate data for Sankey flow diagram."""
        # Generate multi-level flows
        # Level 1: Sources
        sources = ['Revenue', 'Investment', 'Grants']
        # Level 2: Departments
        departments = ['Engineering', 'Sales', 'Marketing', 'Operations']
        # Level 3: Projects
        projects = ['Product A', 'Product B', 'Product C', 'Product D']

        data = []
        base_value = scenario.base_value

        # Source → Department flows
        for source in sources[:min(2, len(sources))]:
            for dept in departments[:min(3, len(departments))]:
                flow_value = base_value * random.uniform(0.3, 0.7)
                data.append({
                    "label": f"{source} → {dept}",
                    "value": round(flow_value, 2)
                })

        # Department → Project flows
        for dept in departments[:min(3, len(departments))]:
            for proj in projects[:min(2, len(projects))]:
                flow_value = base_value * random.uniform(0.2, 0.5)
                data.append({
                    "label": f"{dept} → {proj}",
                    "value": round(flow_value, 2)
                })

        # Return limited to num_points
        return data[:num_points]

    def _generate_simple_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Fallback: Generate simple label-value data."""
        labels = self._generate_category_labels(num_points, context)
        values = self._generate_random_values(
            num_points,
            base_value=scenario.base_value,
            variance=scenario.volatility
        )

        return [
            {"label": label, "value": value}
            for label, value in zip(labels, values)
        ]

    # Helper methods

    def _generate_time_labels(
        self,
        num_points: int,
        context: dict
    ) -> List[str]:
        """Generate time-based labels (Q1, Jan, Week 1, etc.)."""
        timeframe = context.get('timeframe', 'quarter')
        year = context.get('year', 2024)

        if timeframe == 'quarter':
            return [f"Q{i+1} {year}" for i in range(min(num_points, 4))]
        elif timeframe == 'month':
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return [f"{months[i]} {year}" for i in range(min(num_points, 12))]
        elif timeframe == 'week':
            return [f"Week {i+1}" for i in range(min(num_points, 52))]
        else:
            return [f"Period {i+1}" for i in range(num_points)]

    def _generate_category_labels(
        self,
        num_points: int,
        context: dict
    ) -> List[str]:
        """Generate category labels based on domain."""
        domain = context.get('domain', 'metrics')

        if domain == 'revenue':
            categories = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E',
                         'Service 1', 'Service 2', 'Service 3', 'Other', 'Misc']
        elif domain == 'market_share':
            categories = ['Company A', 'Company B', 'Company C', 'Company D', 'Company E',
                         'Competitor 1', 'Competitor 2', 'Others']
        elif domain == 'performance':
            categories = ['Metric 1', 'Metric 2', 'Metric 3', 'Metric 4', 'Metric 5',
                         'KPI A', 'KPI B', 'KPI C']
        elif domain == 'customers':
            categories = ['Segment A', 'Segment B', 'Segment C', 'Segment D',
                         'Enterprise', 'SMB', 'Consumer', 'Other']
        else:
            categories = [f"Category {chr(65+i)}" for i in range(20)]

        return categories[:num_points]

    def _generate_trend_values(
        self,
        num_points: int,
        trend: str = 'upward',
        volatility: float = 0.1,
        base_value: float = 100000,
        seasonality: bool = False
    ) -> List[float]:
        """Generate values with trend and optional seasonality."""
        values = []

        # Trend multipliers
        trend_map = {
            'upward': lambda i, n: 1.0 + (i / n) * 0.5,
            'downward': lambda i, n: 1.0 - (i / n) * 0.3,
            'stable': lambda i, n: 1.0,
            'cyclical': lambda i, n: 1.0 + 0.3 * math.sin(2 * math.pi * i / n)
        }

        trend_func = trend_map.get(trend, trend_map['stable'])

        for i in range(num_points):
            # Base trend
            trend_mult = trend_func(i, num_points)

            # Seasonality (quarterly pattern)
            season_mult = 1.0
            if seasonality:
                season_mult = 1.0 + 0.2 * math.sin(2 * math.pi * i / 4)

            # Random variance
            variance_mult = random.uniform(1 - volatility, 1 + volatility)

            value = base_value * trend_mult * season_mult * variance_mult
            values.append(round(value, 2))

        return values

    def _generate_random_values(
        self,
        num_points: int,
        base_value: float = 100,
        variance: float = 0.2
    ) -> List[float]:
        """Generate random values around base_value."""
        return [
            round(base_value * random.uniform(1 - variance, 1 + variance), 2)
            for _ in range(num_points)
        ]

    def _generate_percentage_distribution(
        self,
        num_points: int
    ) -> List[float]:
        """Generate percentage values that sum to 100."""
        # Generate random values
        raw_values = [random.uniform(1, 10) for _ in range(num_points)]

        # Normalize to sum to 100
        total = sum(raw_values)
        percentages = [(val / total) * 100 for val in raw_values]

        # Round and ensure sum is exactly 100
        rounded = [round(p, 1) for p in percentages]
        diff = 100.0 - sum(rounded)

        # Add diff to largest value
        if diff != 0:
            max_idx = rounded.index(max(rounded))
            rounded[max_idx] = round(rounded[max_idx] + diff, 1)

        return rounded
