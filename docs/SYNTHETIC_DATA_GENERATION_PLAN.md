# Synthetic Data Generation Implementation Plan

**Version**: 1.0
**Date**: November 25, 2025
**Status**: APPROVED - IMPLEMENTATION IN PROGRESS
**Analytics Service Version**: 3.7.0

---

## 🎯 Executive Summary

This plan implements an **independent synthetic data generation capability** for the Analytics Microservice v3, enabling the service to generate realistic, context-aware data without relying on the Director Agent. This capability serves two primary purposes:

1. **(a) PRIMARY - Phase 1**: Generate synthetic data based on chart type and user narrative context
2. **(b) FUTURE - Phase 2**: Search user-uploaded files for relevant data

**Key Benefits**:
- ✅ **Independence**: Service can operate standalone for development, testing, and preview
- ✅ **Backward Compatible**: Zero breaking changes to existing Director integration
- ✅ **Realistic Data**: Context-aware generation based on narrative and chart type
- ✅ **Testing**: Automated test data generation for all 18 chart types
- ✅ **Flexibility**: Optional fallback when Director data is unavailable

---

## 📊 Current Architecture Analysis

### Director-to-Analytics Data Flow (Existing)

```
┌──────────────────┐
│  Director Agent  │  Provides actual data from user narrative
│    (v3.4+)       │
└────────┬─────────┘
         │
         │ POST /api/v1/analytics/L02/{analytics_type}
         │ {
         │   "presentation_id": "...",
         │   "slide_id": "...",
         │   "narrative": "Show Q4 revenue growth...",
         │   "data": [
         │     {"label": "Q1", "value": 125000},
         │     {"label": "Q2", "value": 145000}
         │   ]
         │ }
         ▼
┌─────────────────────────────────────────────────────┐
│           Analytics Microservice v3.7               │
│                                                     │
│  ┌──────────────┐    ┌─────────────┐              │
│  │ rest_server  │───▶│   agent.py  │              │
│  │  (FastAPI)   │    │ (processor) │              │
│  └──────────────┘    └──────┬──────┘              │
│                             │                      │
│          ┌──────────────────▼──────────────┐       │
│          │   chartjs_generator.py          │       │
│          │   (18 chart type methods)       │       │
│          └──────────────┬──────────────────┘       │
│                         │                          │
│          ┌──────────────▼──────────────┐           │
│          │   layout_assembler.py       │           │
│          └──────────────┬──────────────┘           │
└─────────────────────────┼────────────────────────────┘
                          │
                          │ Returns: Rendered slide HTML
                          ▼
                 ┌────────────────┐
                 │ Layout Builder │
                 └────────────────┘
```

**Current Limitations**:
- 🚫 **Dependency**: Must have Director provide data
- 🚫 **No Standalone Testing**: Can't test charts without Director integration
- 🚫 **No Fallback**: No alternative when Director data unavailable
- 🚫 **Manual Test Data**: Each test file requires hand-crafted data

---

## 🏗️ Proposed Architecture: Synthetic Data Generation

### New Architecture with Synthetic Data Layer

```
┌──────────────────┐
│  Director Agent  │  Primary data source (existing)
│    (v3.4+)       │
└────────┬─────────┘
         │
         │ POST /api/v1/analytics/L02/{analytics_type}
         │ data: [...] (provided by Director)
         ▼
┌────────────────────────────────────────────────────────────────┐
│              Analytics Microservice v3.7 (Enhanced)            │
│                                                                │
│  ┌──────────────┐      ┌─────────────────────────────────┐   │
│  │ rest_server  │─────▶│  Data Source Router (NEW)       │   │
│  │  (FastAPI)   │      │                                 │   │
│  └──────────────┘      │  1. Director data (primary)     │   │
│                        │  2. User files (future)         │   │
│                        │  3. Synthetic data (fallback)   │   │
│                        └─────────┬───────────────────────┘   │
│                                  │                            │
│         ┌────────────────────────┼────────────────┐           │
│         │                        │                │           │
│         ▼                        ▼                ▼           │
│  ┌────────────┐       ┌──────────────────┐   ┌──────────┐   │
│  │  Director  │       │  Synthetic Data  │   │   User   │   │
│  │   Data     │       │    Generator     │   │   Files  │   │
│  │ (existing) │       │     (NEW)        │   │ (future) │   │
│  └────┬───────┘       └────────┬─────────┘   └─────┬────┘   │
│       │                        │                    │        │
│       └────────────┬───────────┴────────────────────┘        │
│                    ▼                                          │
│           ┌─────────────────┐                                │
│           │    agent.py     │                                │
│           │  (processor)    │                                │
│           └────────┬────────┘                                │
│                    │                                          │
│           ┌────────▼────────────────┐                        │
│           │  chartjs_generator.py   │                        │
│           │  (18 chart renderers)   │                        │
│           └────────┬────────────────┘                        │
│                    │                                          │
│           ┌────────▼────────────────┐                        │
│           │  layout_assembler.py    │                        │
│           └────────┬────────────────┘                        │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     │ Returns: Rendered slide HTML
                     ▼
            ┌────────────────┐
            │ Layout Builder │
            └────────────────┘
```

### Data Source Priority Chain

```
┌─────────────────────────────────────────────┐
│  Data Source Selection Logic               │
│                                             │
│  IF use_synthetic_data == True:            │
│    ↓                                        │
│    Use Synthetic Generator                 │
│                                             │
│  ELSE IF Director provides data:           │
│    ↓                                        │
│    Use Director Data (existing behavior)   │
│                                             │
│  ELSE IF User files available:             │
│    ↓                                        │
│    Search User Files (Phase 2 - future)    │
│                                             │
│  ELSE:                                      │
│    ↓                                        │
│    FALLBACK → Synthetic Generator          │
└─────────────────────────────────────────────┘
```

---

## 🔧 Technical Design

### Module Structure

```
analytics_microservice_v3/
├── synthetic_data_generator/         # NEW MODULE
│   ├── __init__.py                   # Module exports
│   ├── generator.py                  # Main generation engine (~400 lines)
│   ├── scenarios.py                  # Business scenarios (~300 lines)
│   ├── constraints.py                # Chart constraint reader (~150 lines)
│   ├── formatters.py                 # Data format converters (~200 lines)
│   ├── validators.py                 # Generation validation (~100 lines)
│   └── narrative_parser.py           # Context extraction (~200 lines)
├── rest_server.py                    # MODIFIED: Add endpoints
├── agent.py                          # MODIFIED: Add fallback logic
└── README.md                         # MODIFIED: Document capabilities
```

---

## 📝 Implementation Phases

### Phase 0: Architecture & Design ✅ CURRENT
**Duration**: 1-2 hours
**Status**: IN PROGRESS

**Tasks**:
- [x] Analyze current Director-Analytics data flow
- [x] Design synthetic data generation architecture
- [ ] Create `SYNTHETIC_DATA_GENERATION_PLAN.md` (this document)
- [ ] Define API contracts
- [ ] Create test strategy

**Deliverables**:
- Comprehensive plan document
- Architecture diagrams
- API specifications

---

### Phase 1: Core Synthetic Data Generator
**Duration**: 3-4 hours
**Status**: PENDING

#### 1.1 Create Module Foundation

**File**: `synthetic_data_generator/__init__.py`
```python
"""
Synthetic Data Generator for Analytics Microservice v3.

Generates realistic, context-aware data for all 18 chart types.
"""

from .generator import SyntheticDataGenerator
from .scenarios import BusinessScenario, SCENARIO_LIBRARY
from .constraints import ChartConstraints

__all__ = [
    'SyntheticDataGenerator',
    'BusinessScenario',
    'SCENARIO_LIBRARY',
    'ChartConstraints'
]

__version__ = '1.0.0'
```

#### 1.2 Core Generator Engine

**File**: `synthetic_data_generator/generator.py` (~400 lines)

**Key Components**:

```python
from typing import List, Dict, Any, Optional
from .scenarios import SCENARIO_LIBRARY, BusinessScenario
from .constraints import ChartConstraints
from .formatters import DataFormatter
from .validators import DataValidator
from .narrative_parser import NarrativeParser
import random
import numpy as np

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
            if 'quarterly' in narrative.lower() or 'quarter' in narrative.lower():
                return 4
            if 'monthly' in narrative.lower() or 'month' in narrative.lower():
                return 12
            if 'weekly' in narrative.lower():
                return min(52, constraints['max_data_points'])

        # Use chart type optimal range
        optimal_str = constraints.get('optimal_data_points', '5-10')
        if '-' in optimal_str:
            low, high = map(int, optimal_str.split('-'))
            return random.randint(low, high)

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

        # Auto-select scenario based on context
        return self._auto_select_scenario(chart_type, context)

    def _auto_select_scenario(
        self,
        chart_type: str,
        context: dict
    ) -> BusinessScenario:
        """Automatically select appropriate scenario."""
        # Map chart types to default scenarios
        scenario_map = {
            'line': 'revenue_growth',
            'bar_vertical': 'category_comparison',
            'bar_horizontal': 'category_comparison',
            'pie': 'market_share',
            'doughnut': 'market_share',
            'd3_choropleth_usa': 'geographic_sales',
            'd3_sankey': 'budget_flow',
            'd3_treemap': 'hierarchical_revenue',
            'd3_sunburst': 'hierarchical_revenue',
            'scatter': 'correlation_analysis',
            'bubble': 'multidimensional_analysis',
            'waterfall': 'financial_waterfall',
            # ... all 18 types
        }

        scenario_name = scenario_map.get(chart_type, 'generic_metrics')
        return SCENARIO_LIBRARY.get(scenario_name, BusinessScenario.generic())

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
            values.append(value)

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
                    "value": flow_value
                })

        # Department → Project flows
        for dept in departments[:min(3, len(departments))]:
            for proj in projects[:min(2, len(projects))]:
                flow_value = base_value * random.uniform(0.2, 0.5)
                data.append({
                    "label": f"{dept} → {proj}",
                    "value": flow_value
                })

        # Return limited to num_points
        return data[:num_points]

    # ... (14 more chart-type-specific generators)

    def _generate_simple_data(
        self,
        num_points: int,
        scenario: BusinessScenario,
        context: dict,
        constraints: dict
    ) -> List[Dict[str, Any]]:
        """Fallback: Generate simple label-value data."""
        labels = [f"Item {i+1}" for i in range(num_points)]
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
        else:
            return [f"Period {i+1}" for i in range(num_points)]

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
            'cyclical': lambda i, n: 1.0 + 0.3 * np.sin(2 * np.pi * i / n)
        }

        trend_func = trend_map.get(trend, trend_map['stable'])

        for i in range(num_points):
            # Base trend
            trend_mult = trend_func(i, num_points)

            # Seasonality (quarterly pattern)
            season_mult = 1.0
            if seasonality:
                season_mult = 1.0 + 0.2 * np.sin(2 * np.pi * i / 4)

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
```

#### 1.3 Business Scenarios Library

**File**: `synthetic_data_generator/scenarios.py` (~300 lines)

```python
"""
Business scenario templates for synthetic data generation.

Each scenario defines realistic patterns for different business contexts.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class BusinessScenario:
    """
    Business scenario template for data generation.

    Attributes:
        name: Scenario name (e.g., 'revenue_growth')
        description: Human-readable description
        trend: Trend pattern ('upward', 'downward', 'stable', 'cyclical')
        volatility: Data variance (0.0-1.0)
        base_value: Starting value magnitude
        seasonality: Whether to apply seasonal patterns
        distribution: Value distribution pattern
        value_format: 'currency', 'percentage', 'number'
        metadata: Additional scenario-specific parameters
    """
    name: str
    description: str
    trend: str = 'stable'
    volatility: float = 0.1
    base_value: float = 100000
    seasonality: bool = False
    distribution: str = 'normal'
    value_format: str = 'number'
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def generic(cls) -> 'BusinessScenario':
        """Default generic scenario."""
        return cls(
            name='generic_metrics',
            description='Generic business metrics',
            trend='stable',
            volatility=0.15,
            base_value=100,
            seasonality=False
        )


# Scenario Library (15+ pre-defined scenarios)

SCENARIO_LIBRARY = {

    # Financial Scenarios
    'revenue_growth': BusinessScenario(
        name='revenue_growth',
        description='Revenue growth over time with upward trend',
        trend='upward',
        volatility=0.15,
        base_value=125000,
        seasonality=True,
        value_format='currency',
        metadata={'growth_rate': 0.08}
    ),

    'revenue_decline': BusinessScenario(
        name='revenue_decline',
        description='Revenue decline over time',
        trend='downward',
        volatility=0.12,
        base_value=200000,
        seasonality=False,
        value_format='currency',
        metadata={'decline_rate': -0.05}
    ),

    'seasonal_revenue': BusinessScenario(
        name='seasonal_revenue',
        description='Revenue with strong seasonal patterns',
        trend='stable',
        volatility=0.1,
        base_value=150000,
        seasonality=True,
        value_format='currency',
        metadata={'peak_quarter': 4}
    ),

    'financial_waterfall': BusinessScenario(
        name='financial_waterfall',
        description='Financial waterfall with positive and negative changes',
        trend='stable',
        volatility=0.05,
        base_value=500000,
        seasonality=False,
        value_format='currency',
        metadata={'has_negatives': True, 'final_total': True}
    ),

    # Market Analysis Scenarios
    'market_share': BusinessScenario(
        name='market_share',
        description='Market share distribution across competitors',
        trend='stable',
        volatility=0.08,
        base_value=25.0,  # percentage
        seasonality=False,
        distribution='competitive',  # Sum to 100%
        value_format='percentage',
        metadata={'total_sum': 100}
    ),

    'category_comparison': BusinessScenario(
        name='category_comparison',
        description='Category comparison metrics',
        trend='stable',
        volatility=0.2,
        base_value=50000,
        seasonality=False,
        value_format='number'
    ),

    # Geographic Scenarios
    'geographic_sales': BusinessScenario(
        name='geographic_sales',
        description='Sales performance by geographic region',
        trend='stable',
        volatility=0.25,
        base_value=850000,
        seasonality=False,
        distribution='geographic',  # Larger regions get higher values
        value_format='currency',
        metadata={'region_weighting': True}
    ),

    # Process Flow Scenarios
    'budget_flow': BusinessScenario(
        name='budget_flow',
        description='Budget allocation flow from sources to projects',
        trend='stable',
        volatility=0.1,
        base_value=500000,
        seasonality=False,
        distribution='flow',
        value_format='currency',
        metadata={'multi_level': True, 'conservation': True}
    ),

    'customer_journey': BusinessScenario(
        name='customer_journey',
        description='Customer journey funnel from awareness to conversion',
        trend='downward',  # Funnel narrows
        volatility=0.05,
        base_value=10000,
        seasonality=False,
        distribution='funnel',
        value_format='number',
        metadata={'conversion_rate': 0.15}
    ),

    # Hierarchical Scenarios
    'hierarchical_revenue': BusinessScenario(
        name='hierarchical_revenue',
        description='Revenue breakdown by product hierarchy',
        trend='stable',
        volatility=0.18,
        base_value=200000,
        seasonality=False,
        distribution='hierarchical',
        value_format='currency',
        metadata={'levels': 3, 'branching_factor': 3}
    ),

    # Performance Metrics Scenarios
    'kpi_performance': BusinessScenario(
        name='kpi_performance',
        description='KPI performance metrics',
        trend='upward',
        volatility=0.12,
        base_value=75.0,  # percentage
        seasonality=False,
        value_format='percentage',
        metadata={'target': 85.0}
    ),

    'correlation_analysis': BusinessScenario(
        name='correlation_analysis',
        description='Correlation between two variables',
        trend='stable',
        volatility=0.15,
        base_value=50,
        seasonality=False,
        distribution='correlated',
        value_format='number',
        metadata={'correlation': 0.75}
    ),

    'multidimensional_analysis': BusinessScenario(
        name='multidimensional_analysis',
        description='Multi-dimensional bubble chart analysis',
        trend='stable',
        volatility=0.2,
        base_value=100,
        seasonality=False,
        distribution='clustered',
        value_format='number',
        metadata={'dimensions': 3}
    ),

    # Growth Scenarios
    'yoy_growth': BusinessScenario(
        name='yoy_growth',
        description='Year-over-year growth comparison',
        trend='upward',
        volatility=0.1,
        base_value=8.5,  # percentage
        seasonality=False,
        value_format='percentage',
        metadata={'comparison_years': 2}
    ),

    'quarterly_comparison': BusinessScenario(
        name='quarterly_comparison',
        description='Quarterly performance comparison',
        trend='stable',
        volatility=0.12,
        base_value=180000,
        seasonality=True,
        value_format='currency',
        metadata={'quarters': 4}
    ),

    # Generic fallback
    'generic_metrics': BusinessScenario.generic(),
}


def get_scenario(name: str) -> BusinessScenario:
    """Get scenario by name with fallback to generic."""
    return SCENARIO_LIBRARY.get(name, BusinessScenario.generic())


def list_scenarios() -> list[str]:
    """List all available scenario names."""
    return list(SCENARIO_LIBRARY.keys())


def get_scenario_for_chart_type(chart_type: str) -> BusinessScenario:
    """Get recommended scenario for a chart type."""
    chart_scenario_map = {
        'line': 'revenue_growth',
        'bar_vertical': 'category_comparison',
        'bar_horizontal': 'category_comparison',
        'bar_grouped': 'category_comparison',
        'bar_stacked': 'category_comparison',
        'pie': 'market_share',
        'doughnut': 'market_share',
        'area': 'seasonal_revenue',
        'area_stacked': 'seasonal_revenue',
        'scatter': 'correlation_analysis',
        'bubble': 'multidimensional_analysis',
        'radar': 'kpi_performance',
        'polar_area': 'market_share',
        'waterfall': 'financial_waterfall',
        'd3_treemap': 'hierarchical_revenue',
        'd3_sunburst': 'hierarchical_revenue',
        'd3_choropleth_usa': 'geographic_sales',
        'd3_sankey': 'budget_flow',
    }

    scenario_name = chart_scenario_map.get(chart_type, 'generic_metrics')
    return get_scenario(scenario_name)
```

#### 1.4 Chart Constraints Reader

**File**: `synthetic_data_generator/constraints.py` (~150 lines)

```python
"""
Chart constraint reader for synthetic data generation.

Reads chart type constraints from chart_catalog.py to ensure
generated data meets requirements.
"""

import sys
import os
from typing import Dict, Any, Optional

# Import chart catalog
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from chart_catalog import get_chart_catalog, ChartType


class ChartConstraints:
    """
    Reads and provides chart type constraints for data generation.

    Constraints include:
    - min_data_points
    - max_data_points
    - optimal_data_points
    - special requirements (e.g., US state names for choropleth)
    """

    def __init__(self):
        """Initialize with chart catalog."""
        self.catalog = get_chart_catalog()
        self._constraints_cache = {}
        self._load_constraints()

    def _load_constraints(self):
        """Load all chart constraints into cache."""
        for chart_type in self.catalog['all_chart_types']:
            chart_id = chart_type['id']
            self._constraints_cache[chart_id] = {
                'id': chart_id,
                'name': chart_type['name'],
                'library': chart_type['library'],
                'min_data_points': chart_type.get('min_data_points', 2),
                'max_data_points': chart_type.get('max_data_points', 50),
                'optimal_data_points': chart_type.get('optimal_data_points', '5-10'),
                'supported_layouts': chart_type.get('supported_layouts', []),
                'use_cases': chart_type.get('use_cases', []),
                'special_requirements': self._extract_special_requirements(chart_type)
            }

    def _extract_special_requirements(self, chart_type: dict) -> dict:
        """Extract special requirements from chart type."""
        requirements = {}

        chart_id = chart_type['id']

        # D3 Choropleth USA: Requires US state names
        if chart_id == 'd3_choropleth_usa':
            requirements['label_type'] = 'us_state'
            requirements['state_formats'] = ['abbreviation', 'full_name']

        # D3 Sankey: Requires flow notation
        if chart_id == 'd3_sankey':
            requirements['label_format'] = 'source_target_flow'
            requirements['flow_notation'] = ['arrow', 'explicit']

        # Scatter/Bubble: Requires x,y coordinates
        if chart_id in ['scatter', 'bubble']:
            requirements['data_format'] = 'object_based'
            requirements['required_fields'] = ['x', 'y']
            if chart_id == 'bubble':
                requirements['required_fields'].append('r')

        # Multi-series charts
        if chart_id in ['bar_grouped', 'bar_stacked', 'area_stacked']:
            requirements['data_format'] = 'multi_series'
            requirements['min_series'] = 2
            requirements['max_series'] = 5

        # Radar chart: Normalized values
        if chart_id == 'radar':
            requirements['value_range'] = [0, 100]
            requirements['normalized'] = True

        # Hierarchical charts
        if chart_id in ['d3_treemap', 'd3_sunburst']:
            requirements['data_format'] = 'hierarchical'
            requirements['simple_format_accepted'] = True

        # Waterfall: Positive/negative values
        if chart_id == 'waterfall':
            requirements['value_types'] = ['positive', 'negative']
            requirements['has_total'] = True

        # Market share charts: Sum to 100
        if chart_id in ['pie', 'doughnut', 'polar_area']:
            requirements['sum_constraint'] = 100  # for percentages
            requirements['positive_only'] = True

        return requirements

    def get_constraints(self, chart_type: str) -> Dict[str, Any]:
        """
        Get constraints for a chart type.

        Args:
            chart_type: Chart type ID

        Returns:
            Dictionary with constraints

        Example:
            >>> constraints = ChartConstraints()
            >>> c = constraints.get_constraints('d3_choropleth_usa')
            >>> print(c['min_data_points'])  # 1
            >>> print(c['special_requirements']['label_type'])  # 'us_state'
        """
        if chart_type not in self._constraints_cache:
            raise ValueError(f"Unknown chart type: {chart_type}")

        return self._constraints_cache[chart_type]

    def get_optimal_point_count(self, chart_type: str) -> int:
        """Get optimal data point count for a chart type."""
        constraints = self.get_constraints(chart_type)
        optimal_str = constraints['optimal_data_points']

        if '-' in str(optimal_str):
            # Parse range like "5-10"
            low, high = map(int, optimal_str.split('-'))
            return (low + high) // 2

        # Single value
        return int(optimal_str)

    def is_valid_point_count(self, chart_type: str, num_points: int) -> bool:
        """Check if data point count is valid for chart type."""
        constraints = self.get_constraints(chart_type)
        min_points = constraints['min_data_points']
        max_points = constraints['max_data_points']

        return min_points <= num_points <= max_points

    def get_all_chart_types(self) -> list[str]:
        """Get list of all supported chart type IDs."""
        return list(self._constraints_cache.keys())

    def get_chart_types_by_library(self, library: str) -> list[str]:
        """Get chart types for a specific library (Chart.js or D3.js)."""
        return [
            chart_id
            for chart_id, constraints in self._constraints_cache.items()
            if constraints['library'] == library
        ]
```

#### 1.5 Data Formatters

**File**: `synthetic_data_generator/formatters.py` (~200 lines)

```python
"""
Data format converters for different chart types.

Converts simple {label, value} format to chart-specific formats
(scatter objects, multi-series, hierarchical, etc.)
"""

from typing import List, Dict, Any


class DataFormatter:
    """
    Converts generated data to chart-specific formats.

    Handles:
    - Simple format: [{label, value}, ...]
    - Object format: [{x, y, label}, ...] (scatter/bubble)
    - Multi-series format: {datasets: [{label, data}, ...]}
    - Hierarchical format: (treemap/sunburst)
    - Flow format: Source→Target notation (sankey)
    """

    def format(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Format data for specific chart type.

        Args:
            data: Base data in simple {label, value} format
            chart_type: Target chart type ID

        Returns:
            Formatted data ready for chart rendering
        """
        formatter_map = {
            'scatter': self._format_scatter,
            'bubble': self._format_bubble,
            'bar_grouped': self._format_multi_series,
            'bar_stacked': self._format_multi_series,
            'area_stacked': self._format_multi_series,
            'radar': self._format_radar,
            'd3_sankey': self._format_sankey,
            # All others use simple format
        }

        formatter = formatter_map.get(chart_type, self._format_simple)
        return formatter(data, chart_type)

    def _format_simple(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """Simple format: unchanged {label, value} pairs."""
        return data

    def _format_scatter(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Convert to scatter format: {x, y, label}.

        Input: [{"label": "A", "value": 100}, ...]
        Output: [{"x": 0, "y": 100, "label": "A"}, ...]
        """
        return [
            {
                "x": i,
                "y": item['value'],
                "label": item['label']
            }
            for i, item in enumerate(data)
        ]

    def _format_bubble(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Convert to bubble format: {x, y, r, label}.

        Input: [{"label": "A", "value": 100}, ...]
        Output: [{"x": 0, "y": 100, "r": 15, "label": "A"}, ...]
        """
        import random

        return [
            {
                "x": i,
                "y": item['value'],
                "r": random.randint(10, 30),  # Bubble size
                "label": item['label']
            }
            for i, item in enumerate(data)
        ]

    def _format_multi_series(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> Dict[str, Any]:
        """
        Convert to multi-series format.

        Input: [{"label": "Q1", "value": 100}, ...]
        Output: {
            "labels": ["Q1", "Q2", ...],
            "datasets": [
                {"label": "Series A", "data": [100, 120, ...]},
                {"label": "Series B", "data": [80, 90, ...]}
            ]
        }
        """
        import random

        labels = [item['label'] for item in data]

        # Create 2-3 series with variance
        num_series = random.randint(2, 3)
        datasets = []

        for i in range(num_series):
            series_data = [
                item['value'] * random.uniform(0.7, 1.3)
                for item in data
            ]
            datasets.append({
                "label": f"Series {chr(65+i)}",  # A, B, C
                "data": series_data
            })

        return {
            "labels": labels,
            "datasets": datasets
        }

    def _format_radar(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> Dict[str, Any]:
        """
        Convert to radar format (normalized 0-100).

        Input: [{"label": "Speed", "value": 80}, ...]
        Output: {
            "labels": ["Speed", "Power", ...],
            "datasets": [{"label": "Performance", "data": [80, 90, ...]}]
        }
        """
        labels = [item['label'] for item in data]

        # Normalize values to 0-100 range
        values = [item['value'] for item in data]
        if values:
            max_val = max(values)
            normalized = [
                round((val / max_val) * 100, 1) if max_val > 0 else 50
                for val in values
            ]
        else:
            normalized = []

        return {
            "labels": labels,
            "datasets": [{
                "label": "Performance",
                "data": normalized
            }]
        }

    def _format_sankey(
        self,
        data: List[Dict[str, Any]],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Ensure Sankey flow notation.

        Input: [{"label": "A → B", "value": 100}, ...]
        Output: Unchanged (already in correct format)

        If labels don't have arrows, add them.
        """
        formatted = []

        for i, item in enumerate(data):
            label = item['label']

            # Check if label has arrow notation
            if '→' in label or '->' in label:
                formatted.append(item)
            else:
                # Add arrow notation (split at midpoint)
                if i < len(data) // 2:
                    new_label = f"Source → {label}"
                else:
                    new_label = f"{data[i - len(data)//2]['label']} → Target"

                formatted.append({
                    "label": new_label,
                    "value": item['value']
                })

        return formatted
```

#### 1.6 Data Validators

**File**: `synthetic_data_generator/validators.py` (~100 lines)

```python
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
            if 'value' not in first_item and 'y' not in first_item:
                errors.append("Data points must have 'value' or 'y' field")

        return errors

    def _validate_labels(self, data: List[Dict[str, Any]]) -> List[str]:
        """Validate labels."""
        errors = []

        labels = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                label = item.get('label', '')

                # Check non-empty
                if not label or (isinstance(label, str) and label.strip() == ''):
                    errors.append(f"Data point {i}: Label is empty")
                    continue

                # Check length
                if isinstance(label, str) and len(label) > 100:
                    errors.append(f"Data point {i}: Label exceeds 100 chars")

                labels.append(label)

        # Check uniqueness
        if len(labels) != len(set(labels)):
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
                    continue  # May be multi-series format

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
                # ... (full state name list)
            }

            for i, item in enumerate(data):
                label = item.get('label', '')
                if label not in valid_states:
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
```

#### 1.7 Narrative Parser

**File**: `synthetic_data_generator/narrative_parser.py` (~200 lines)

```python
"""
Narrative context parser for synthetic data generation.

Extracts contextual information from user narratives to
generate more realistic, relevant data.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime


class NarrativeParser:
    """
    Parses user narratives to extract data generation context.

    Extracts:
    - Timeframe (quarterly, monthly, yearly, etc.)
    - Trend indicators (growth, decline, stable)
    - Domain (revenue, market share, performance, etc.)
    - Magnitude indicators (millions, thousands, percentages)
    - Geographic hints (states, regions, countries)
    - Comparisons (year-over-year, quarter-over-quarter)
    """

    def __init__(self):
        """Initialize with pattern definitions."""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for extraction."""
        self.patterns = {
            # Timeframes
            'quarterly': re.compile(r'\b(quarter|quarterly|Q[1-4])\b', re.I),
            'monthly': re.compile(r'\b(month|monthly|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b', re.I),
            'yearly': re.compile(r'\b(year|yearly|annual|FY\s*\d{4}|20\d{2})\b', re.I),
            'weekly': re.compile(r'\b(week|weekly)\b', re.I),

            # Trends
            'growth': re.compile(r'\b(grow|growth|increase|rising|upward|climb|surge|boost)\b', re.I),
            'decline': re.compile(r'\b(decline|decrease|drop|falling|downward|shrink|reduce)\b', re.I),
            'stable': re.compile(r'\b(stable|steady|consistent|maintained|flat)\b', re.I),
            'volatile': re.compile(r'\b(volatile|fluctuat|vary|unsteady)\b', re.I),

            # Domains
            'revenue': re.compile(r'\b(revenue|sales|income|earnings)\b', re.I),
            'market_share': re.compile(r'\b(market\s+share|share\s+of\s+market)\b', re.I),
            'performance': re.compile(r'\b(performance|metrics|KPI|key\s+performance)\b', re.I),
            'budget': re.compile(r'\b(budget|allocation|spending|expenditure)\b', re.I),
            'customers': re.compile(r'\b(customer|client|user|subscriber)\b', re.I),

            # Magnitudes
            'millions': re.compile(r'\b(million|M|\$\d+M)\b', re.I),
            'thousands': re.compile(r'\b(thousand|K|\$\d+K)\b', re.I),
            'billions': re.compile(r'\b(billion|B|\$\d+B)\b', re.I),
            'percentage': re.compile(r'\b(\d+%|percent|percentage)\b', re.I),

            # Geography
            'us_states': re.compile(r'\b(state|states|USA|US|America)\b', re.I),
            'global': re.compile(r'\b(global|world|international|countries)\b', re.I),
            'regional': re.compile(r'\b(region|regional|geographic)\b', re.I),

            # Comparisons
            'yoy': re.compile(r'\b(year-over-year|YoY|y-o-y|annual\s+comparison)\b', re.I),
            'qoq': re.compile(r'\b(quarter-over-quarter|QoQ|q-o-q)\b', re.I),
        }

    def parse(self, narrative: Optional[str]) -> Dict[str, Any]:
        """
        Parse narrative to extract context.

        Args:
            narrative: User narrative text

        Returns:
            Dictionary with extracted context

        Example:
            >>> parser = NarrativeParser()
            >>> context = parser.parse(
            ...     "Show quarterly revenue growth for FY 2024"
            ... )
            >>> print(context)
            {
                'timeframe': 'quarter',
                'trend': 'growth',
                'domain': 'revenue',
                'year': 2024,
                'magnitude': 'thousands'
            }
        """
        if not narrative:
            return self._default_context()

        context = {}

        # Extract timeframe
        context['timeframe'] = self._extract_timeframe(narrative)

        # Extract trend
        context['trend'] = self._extract_trend(narrative)

        # Extract domain
        context['domain'] = self._extract_domain(narrative)

        # Extract magnitude
        context['magnitude'] = self._extract_magnitude(narrative)

        # Extract year
        context['year'] = self._extract_year(narrative)

        # Extract geography
        context['geography'] = self._extract_geography(narrative)

        # Extract comparison type
        context['comparison'] = self._extract_comparison(narrative)

        return context

    def _default_context(self) -> Dict[str, Any]:
        """Return default context when no narrative provided."""
        return {
            'timeframe': 'quarter',
            'trend': 'stable',
            'domain': 'metrics',
            'magnitude': 'number',
            'year': datetime.now().year,
            'geography': None,
            'comparison': None
        }

    def _extract_timeframe(self, narrative: str) -> str:
        """Extract timeframe from narrative."""
        if self.patterns['quarterly'].search(narrative):
            return 'quarter'
        if self.patterns['monthly'].search(narrative):
            return 'month'
        if self.patterns['yearly'].search(narrative):
            return 'year'
        if self.patterns['weekly'].search(narrative):
            return 'week'
        return 'period'

    def _extract_trend(self, narrative: str) -> str:
        """Extract trend from narrative."""
        if self.patterns['growth'].search(narrative):
            return 'upward'
        if self.patterns['decline'].search(narrative):
            return 'downward'
        if self.patterns['stable'].search(narrative):
            return 'stable'
        if self.patterns['volatile'].search(narrative):
            return 'cyclical'
        return 'stable'

    def _extract_domain(self, narrative: str) -> str:
        """Extract business domain from narrative."""
        if self.patterns['revenue'].search(narrative):
            return 'revenue'
        if self.patterns['market_share'].search(narrative):
            return 'market_share'
        if self.patterns['performance'].search(narrative):
            return 'performance'
        if self.patterns['budget'].search(narrative):
            return 'budget'
        if self.patterns['customers'].search(narrative):
            return 'customers'
        return 'metrics'

    def _extract_magnitude(self, narrative: str) -> str:
        """Extract value magnitude from narrative."""
        if self.patterns['billions'].search(narrative):
            return 'billions'
        if self.patterns['millions'].search(narrative):
            return 'millions'
        if self.patterns['thousands'].search(narrative):
            return 'thousands'
        if self.patterns['percentage'].search(narrative):
            return 'percentage'
        return 'number'

    def _extract_year(self, narrative: str) -> int:
        """Extract year from narrative."""
        # Look for FY2024, 2024, etc.
        year_match = re.search(r'\b(FY\s*)?20(\d{2})\b', narrative)
        if year_match:
            return int(f"20{year_match.group(2)}")

        return datetime.now().year

    def _extract_geography(self, narrative: str) -> Optional[str]:
        """Extract geography hint from narrative."""
        if self.patterns['us_states'].search(narrative):
            return 'us_states'
        if self.patterns['global'].search(narrative):
            return 'global'
        if self.patterns['regional'].search(narrative):
            return 'regional'
        return None

    def _extract_comparison(self, narrative: str) -> Optional[str]:
        """Extract comparison type from narrative."""
        if self.patterns['yoy'].search(narrative):
            return 'year_over_year'
        if self.patterns['qoq'].search(narrative):
            return 'quarter_over_quarter'
        return None
```

---

### Phase 2: API Integration
**Duration**: 2-3 hours
**Status**: PENDING

#### 2.1 New REST Endpoints

**File**: `rest_server.py` (additions)

```python
# Add these endpoints to existing rest_server.py

from synthetic_data_generator import SyntheticDataGenerator

# Initialize generator
synthetic_generator = SyntheticDataGenerator()


@app.post("/api/v1/synthetic/generate")
async def generate_synthetic_data(request: SyntheticDataRequest):
    """
    Generate synthetic data for a chart type.

    Endpoint for standalone synthetic data generation.
    Used for testing, preview, and development.
    """
    try:
        data = synthetic_generator.generate(
            chart_type=request.chart_type,
            narrative=request.narrative,
            num_points=request.num_points,
            scenario=request.scenario
        )

        return {
            "success": True,
            "data": data,
            "metadata": {
                "chart_type": request.chart_type,
                "generated_at": datetime.utcnow().isoformat(),
                "num_points": len(data),
                "scenario": request.scenario
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/v1/preview/{chart_type}")
async def preview_chart_type(chart_type: str, request: Optional[PreviewRequest] = None):
    """
    Generate preview slide for a chart type using synthetic data.

    Allows testing chart rendering without Director integration.
    """
    try:
        # Generate synthetic data
        data = synthetic_generator.generate(
            chart_type=chart_type,
            narrative=request.narrative if request else None,
            num_points=request.num_points if request else None
        )

        # Generate slide (reuse existing L02 pipeline)
        result = agent.generate_l02_analytics(
            presentation_id="preview",
            slide_id=f"preview-{chart_type}",
            slide_number=1,
            narrative=request.narrative if request else f"Preview of {chart_type} chart",
            data=data,
            chart_type=chart_type,
            use_synthetic_data=True
        )

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Modify existing analytics endpoint to support synthetic data
@app.post("/api/v1/analytics/L02/{analytics_type}")
async def generate_l02_analytics_slide(
    analytics_type: str,
    request: AnalyticsRequest,
    use_synthetic: bool = False  # NEW PARAMETER
):
    """
    Generate L02 analytics slide.

    Now supports optional synthetic data generation when:
    - use_synthetic=True is specified
    - Director data is missing or invalid
    """
    try:
        # Determine data source
        if use_synthetic or not request.data or len(request.data) == 0:
            # Use synthetic data generator
            data = synthetic_generator.generate(
                chart_type=request.chart_type or analytics_type,
                narrative=request.narrative,
                num_points=request.context.get('num_points') if request.context else None
            )
        else:
            # Use Director-provided data (existing behavior)
            data = [
                {"label": dp.label, "value": dp.value}
                for dp in request.data
            ]

        # Continue with existing pipeline
        result = agent.generate_l02_analytics(
            presentation_id=request.presentation_id,
            slide_id=request.slide_id,
            slide_number=request.slide_number,
            narrative=request.narrative,
            data=data,
            context=request.context,
            constraints=request.constraints,
            chart_type=request.chart_type,
            use_synthetic_data=use_synthetic
        )

        return result

    except Exception as e:
        logger.error(f"Analytics generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# New Pydantic models for synthetic endpoints

class SyntheticDataRequest(BaseModel):
    chart_type: str
    narrative: Optional[str] = None
    num_points: Optional[int] = None
    scenario: Optional[str] = None


class PreviewRequest(BaseModel):
    narrative: Optional[str] = None
    num_points: Optional[int] = None
```

#### 2.2 Agent Integration

**File**: `agent.py` (modifications)

```python
# Modify generate_l02_analytics() to accept use_synthetic_data parameter

def generate_l02_analytics(
    self,
    presentation_id: str,
    slide_id: str,
    slide_number: int,
    narrative: str,
    data: list,
    context: dict = None,
    constraints: dict = None,
    chart_type: str = None,
    use_synthetic_data: bool = False  # NEW PARAMETER
):
    """
    Generate L02 analytics slide.

    Now supports synthetic data generation as fallback.
    """
    # ... existing code ...

    # Add metadata flag
    metadata['synthetic_data_used'] = use_synthetic_data

    # ... rest of existing code ...
```

---

### Phase 3: Testing & Validation
**Duration**: 2 hours
**Status**: PENDING

#### 3.1 Test Suite Structure

```
tests/
├── test_synthetic_generator.py          # Core generator tests
├── test_scenarios.py                    # Scenario tests
├── test_constraints.py                  # Constraint reader tests
├── test_formatters.py                   # Formatter tests
├── test_validators.py                   # Validator tests
├── test_narrative_parser.py             # Parser tests
├── test_api_integration.py              # API endpoint tests
└── test_all_chart_types.py              # All 18 chart types with synthetic data
```

#### 3.2 Comprehensive Test Examples

**File**: `tests/test_all_chart_types.py`

```python
"""
Comprehensive test suite for synthetic data generation.

Tests all 18 chart types with various scenarios.
"""

import pytest
from synthetic_data_generator import SyntheticDataGenerator


@pytest.fixture
def generator():
    return SyntheticDataGenerator()


class TestAllChartTypes:
    """Test synthetic data generation for all 18 chart types."""

    def test_line_chart(self, generator):
        """Test line chart data generation."""
        data = generator.generate(
            chart_type='line',
            narrative='Show quarterly revenue growth for 2024',
            scenario='revenue_growth'
        )

        assert len(data) == 4  # 4 quarters
        assert all('label' in d and 'value' in d for d in data)
        assert all(isinstance(d['value'], (int, float)) for d in data)
        assert data[0]['value'] < data[-1]['value']  # Growth trend

    def test_d3_choropleth_usa(self, generator):
        """Test D3 choropleth USA map data generation."""
        data = generator.generate(
            chart_type='d3_choropleth_usa',
            narrative='Show sales by top 10 US states',
            scenario='geographic_sales'
        )

        assert len(data) == 10

        # Validate US state abbreviations
        valid_states = {
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'
        }
        for d in data:
            assert d['label'] in valid_states

    def test_d3_sankey(self, generator):
        """Test D3 Sankey diagram data generation."""
        data = generator.generate(
            chart_type='d3_sankey',
            narrative='Show budget flow from revenue to departments',
            scenario='budget_flow'
        )

        assert len(data) >= 3

        # Validate flow notation
        for d in data:
            assert '→' in d['label'] or '->' in d['label']

    # ... (tests for all 18 chart types)

    @pytest.mark.parametrize('chart_type', [
        'line', 'bar_vertical', 'bar_horizontal', 'pie', 'doughnut',
        'scatter', 'bubble', 'radar', 'polar_area', 'area', 'area_stacked',
        'bar_grouped', 'bar_stacked', 'waterfall',
        'd3_treemap', 'd3_sunburst', 'd3_choropleth_usa', 'd3_sankey'
    ])
    def test_all_chart_types_generate(self, generator, chart_type):
        """Test that all 18 chart types can generate data."""
        data = generator.generate(chart_type=chart_type)

        assert len(data) > 0
        assert len(data) <= 50  # Max constraint
```

---

### Phase 4: Documentation
**Duration**: 1 hour
**Status**: PENDING

#### 4.1 README Updates

**File**: `README.md` (additions)

```markdown
## Synthetic Data Generation

**Version**: 3.7.0+ supports independent synthetic data generation for all 18 chart types.

### Features

- ✅ **Context-Aware**: Generates realistic data based on user narrative
- ✅ **18 Chart Types**: Supports all Chart.js and D3.js chart types
- ✅ **15+ Scenarios**: Pre-defined business scenarios (revenue, market share, etc.)
- ✅ **Fallback Support**: Automatic fallback when Director data unavailable
- ✅ **Preview Mode**: Test charts without Director integration

### Usage

#### 1. Standalone Data Generation

```bash
curl -X POST http://localhost:8002/api/v1/synthetic/generate \
  -H "Content-Type: application/json" \
  -d '{
    "chart_type": "line",
    "narrative": "Show quarterly revenue growth for 2024",
    "scenario": "revenue_growth"
  }'
```

#### 2. Chart Preview Mode

```bash
curl -X POST http://localhost:8002/api/v1/preview/d3_choropleth_usa \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "Show sales across top 10 US states"
  }'
```

#### 3. Analytics with Optional Synthetic Data

```bash
curl -X POST http://localhost:8002/api/v1/analytics/L02/revenue_over_time?use_synthetic=true \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test-123",
    "slide_id": "slide-1",
    "slide_number": 1,
    "narrative": "Show Q4 2024 revenue trends"
  }'
```

### Available Scenarios

| Scenario | Description | Best For |
|----------|-------------|----------|
| `revenue_growth` | Upward trending revenue | Line, area charts |
| `market_share` | Market share distribution | Pie, doughnut charts |
| `geographic_sales` | Sales by US states | Choropleth map |
| `budget_flow` | Budget allocation flows | Sankey diagram |
| `correlation_analysis` | Variable correlation | Scatter plot |
| ... | (15+ total scenarios) | All chart types |

### Python API

```python
from synthetic_data_generator import SyntheticDataGenerator

gen = SyntheticDataGenerator()

# Generate data
data = gen.generate(
    chart_type='d3_choropleth_usa',
    narrative='Show Q4 sales by state',
    scenario='geographic_sales'
)

print(data)
# [
#   {"label": "CA", "value": 850000},
#   {"label": "TX", "value": 720000},
#   ...
# ]
```
```

---

## 🚀 API Design

### New Endpoints

#### 1. Generate Synthetic Data
```
POST /api/v1/synthetic/generate
```

**Request**:
```json
{
  "chart_type": "line",
  "narrative": "Show quarterly revenue growth for 2024",
  "num_points": 4,
  "scenario": "revenue_growth"
}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 195000},
    {"label": "Q4 2024", "value": 220000}
  ],
  "metadata": {
    "chart_type": "line",
    "generated_at": "2025-11-25T12:00:00Z",
    "num_points": 4,
    "scenario": "revenue_growth"
  }
}
```

#### 2. Preview Chart Type
```
POST /api/v1/preview/{chart_type}
```

**Request**:
```json
{
  "narrative": "Show top 10 states by sales",
  "num_points": 10
}
```

**Response**: Full L02 slide HTML (same as analytics endpoint)

#### 3. Analytics with Optional Synthetic Data
```
POST /api/v1/analytics/L02/{analytics_type}?use_synthetic=true
```

**Behavior**:
- `use_synthetic=false` (default): Use Director-provided data
- `use_synthetic=true`: Generate synthetic data (ignore Director data)
- Automatic fallback if Director data missing

---

## 🔗 Integration Points

### With Existing Codebase

1. **rest_server.py**
   - Add 2 new endpoints
   - Modify 1 existing endpoint to support `use_synthetic` parameter

2. **agent.py**
   - Add `use_synthetic_data` parameter to `generate_l02_analytics()`
   - Add metadata flag to track synthetic data usage

3. **chart_catalog.py**
   - No changes needed (constraints reader accesses it directly)

4. **chartjs_generator.py**
   - No changes needed (consumes same data format)

### With Director Agent

**Backward Compatible**: Director integration unchanged
- Director continues to provide data as primary source
- Synthetic data only used when explicitly requested or as fallback
- No breaking changes to API contract

**Future Enhancement**: Director can optionally request synthetic data augmentation
```json
{
  "presentation_id": "...",
  "data": [...],  // Sparse data from Director
  "augment_with_synthetic": true,  // NEW OPTIONAL FLAG
  "target_points": 12  // Augment to 12 points
}
```

---

## 📊 Data Generation Strategies

### Chart Type Matrix

| Chart Type | Strategy | Special Handling |
|-----------|----------|------------------|
| **Line** | Time-series with trend | Quarterly/monthly labels |
| **Bar (V/H)** | Category comparison | Random categories |
| **Pie** | Market share distribution | Values sum to 100% |
| **Doughnut** | Same as pie | Values sum to 100% |
| **Scatter** | Correlation pattern | X,Y coordinates |
| **Bubble** | Multi-dimensional | X,Y,R coordinates |
| **Radar** | Performance metrics | Normalized 0-100 |
| **Polar Area** | Radial distribution | Positive values |
| **Area** | Time-series fill | Trend + seasonality |
| **Area Stacked** | Multi-series stacked | 2-3 series |
| **Bar Grouped** | Multi-series grouped | 2-3 series |
| **Bar Stacked** | Multi-series stacked | 2-3 series |
| **Waterfall** | Financial changes | +/- values + total |
| **D3 Treemap** | Hierarchical | Simple format OK |
| **D3 Sunburst** | Hierarchical | Simple format OK |
| **D3 Choropleth** | US states | State abbreviations |
| **D3 Sankey** | Flow diagram | Source→Target notation |

### Scenario-to-Chart Mapping

| Business Scenario | Recommended Charts |
|------------------|-------------------|
| Revenue Growth | Line, Area, Bar Vertical |
| Market Share | Pie, Doughnut, Polar Area |
| Geographic Sales | Choropleth USA Map |
| Budget Flow | Sankey Diagram |
| Hierarchical Data | Treemap, Sunburst |
| Correlation Analysis | Scatter, Bubble |
| Performance Metrics | Radar, Polar Area |
| Financial Changes | Waterfall |
| Multi-series Comparison | Grouped/Stacked Bar, Stacked Area |

---

## 🧪 Testing Strategy

### Test Coverage Goals

- ✅ **100%** of 18 chart types tested
- ✅ **90%+** code coverage for generator module
- ✅ **All 15 scenarios** tested
- ✅ **Pydantic validation** passes for all generated data
- ✅ **Performance**: <100ms generation time

### Test Types

1. **Unit Tests**: Individual components (generator, formatters, validators)
2. **Integration Tests**: API endpoints + full pipeline
3. **Chart Type Tests**: All 18 chart types generate valid data
4. **Scenario Tests**: All 15 scenarios produce realistic data
5. **Performance Tests**: Generation time benchmarks
6. **Validation Tests**: All generated data passes Pydantic validators

### Test Data Examples

```python
# Line chart test
test_data = {
    "chart_type": "line",
    "narrative": "Show quarterly revenue growth",
    "expected_points": 4,
    "expected_trend": "upward"
}

# Choropleth test
test_data = {
    "chart_type": "d3_choropleth_usa",
    "narrative": "Show sales by state",
    "expected_points": 10,
    "expected_labels": ["CA", "TX", "NY", ...]
}
```

---

## 🔮 Future Phase: User File Search (Phase 2)

**Status**: DEFERRED - Architecture designed, implementation pending

### Overview

Enable Analytics service to search and extract data from user-uploaded files (CSV, Excel, JSON, etc.).

### Architecture

```
┌──────────────┐
│ User Uploads │
│   Files      │
└──────┬───────┘
       │
       │ POST /api/v1/files/upload
       ▼
┌─────────────────────────────────┐
│  File Management Service (NEW)  │
│                                 │
│  ┌───────────────────────────┐  │
│  │  File Storage (S3/local)  │  │
│  └───────────┬───────────────┘  │
│              │                  │
│  ┌───────────▼───────────────┐  │
│  │  Metadata Extractor       │  │
│  │  (columns, rows, types)   │  │
│  └───────────┬───────────────┘  │
│              │                  │
│  ┌───────────▼───────────────┐  │
│  │  Search Index (vector DB) │  │
│  └───────────┬───────────────┘  │
│              │                  │
└──────────────┼──────────────────┘
               │
               │ Query: "Get Q4 revenue data"
               ▼
       ┌───────────────┐
       │  Data Router  │
       │  (Enhanced)   │
       └───────────────┘
               │
               │ Returns: Extracted data
               ▼
       ┌───────────────┐
       │  Agent.py     │
       │  (Existing)   │
       └───────────────┘
```

### Components to Build

1. **File Upload Endpoint**
   ```
   POST /api/v1/files/upload
   Accepts: CSV, Excel, JSON, XML
   Returns: file_id, metadata
   ```

2. **Metadata Extractor**
   - Column names and types
   - Row count
   - Date ranges
   - Numeric columns (potential chart data)

3. **Search Index**
   - Vector database (ChromaDB, Pinecone, etc.)
   - Index file contents and metadata
   - Query: "Find Q4 2024 revenue data"
   - Returns: Matching rows/columns

4. **Data Extraction Service**
   - Extract relevant columns
   - Convert to {label, value} format
   - Validate extracted data

5. **Data Source Priority**
   ```
   1. Director data (if provided)
   2. User files (if available and relevant)
   3. Synthetic data (fallback)
   ```

### API Design (Phase 2)

```python
@app.post("/api/v1/files/upload")
async def upload_file(file: UploadFile):
    """Upload and index user file for data extraction."""
    pass

@app.post("/api/v1/files/search")
async def search_files(query: str):
    """Search uploaded files for relevant data."""
    pass

@app.post("/api/v1/analytics/L02/{analytics_type}")
async def generate_l02_analytics_slide(
    analytics_type: str,
    request: AnalyticsRequest,
    use_synthetic: bool = False,
    search_user_files: bool = False  # NEW PARAMETER (Phase 2)
):
    """Generate analytics with optional user file search."""
    pass
```

### Estimated Effort (Phase 2)
- **File Upload Service**: 2-3 hours
- **Metadata Extraction**: 2-3 hours
- **Search Index**: 3-4 hours
- **Data Extraction**: 2-3 hours
- **Integration**: 2 hours
- **Testing**: 3 hours
- **Total**: 14-18 hours

---

## ✅ Success Criteria

### Phase 1 (Synthetic Data) Success Criteria

1. ✅ **Data Quality**
   - All 18 chart types generate valid data
   - Data passes Pydantic validators
   - Realistic values based on scenario

2. ✅ **Context Awareness**
   - Narrative parsing extracts timeframe, trend, domain
   - Generated data matches narrative context
   - Appropriate labels (Q1, states, etc.)

3. ✅ **Performance**
   - Generation time <100ms per request
   - No memory leaks or resource issues
   - Handles concurrent requests

4. ✅ **Integration**
   - Zero breaking changes to existing API
   - Backward compatible with Director integration
   - Metadata tracks synthetic data usage

5. ✅ **Testing**
   - >90% code coverage
   - All 18 chart types tested
   - All 15 scenarios tested
   - Performance benchmarks met

6. ✅ **Documentation**
   - README updated with usage examples
   - API documentation complete
   - Integration guide for Director

### Phase 2 (User Files) Success Criteria (Future)

1. ✅ File upload and storage working
2. ✅ Metadata extraction for CSV, Excel, JSON
3. ✅ Search index returns relevant data
4. ✅ Data extraction to {label, value} format
5. ✅ Integration with existing analytics pipeline

---

## 📅 Implementation Timeline

### Week 1: Core Implementation

| Day | Phase | Tasks | Hours |
|-----|-------|-------|-------|
| 1 | Phase 0 | Architecture, planning, documentation | 2 |
| 1-2 | Phase 1 | Core generator, scenarios, constraints | 4 |
| 2-3 | Phase 1 | Formatters, validators, narrative parser | 4 |
| 3-4 | Phase 2 | API integration, endpoints | 3 |
| 4 | Phase 3 | Testing, validation | 2 |
| 4 | Phase 4 | Documentation updates | 1 |

**Total**: 16 hours (~2 work days)

### Future: Phase 2 (User Files)
- **Timeline**: TBD (after Phase 1 deployment)
- **Duration**: ~3 work days
- **Effort**: 14-18 hours

---

## 🔧 Development Workflow

### Setup

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice_v3

# Create synthetic data generator module
mkdir -p synthetic_data_generator

# Install dependencies (if needed)
pip install numpy  # For trend generation

# Run tests
pytest tests/test_synthetic_generator.py -v
```

### Development Process

1. **Create module files**
   - `__init__.py`
   - `generator.py`
   - `scenarios.py`
   - `constraints.py`
   - `formatters.py`
   - `validators.py`
   - `narrative_parser.py`

2. **Implement chart-type generators**
   - Start with simple charts (line, bar, pie)
   - Add complex formats (scatter, bubble, multi-series)
   - Implement D3 chart generators (choropleth, sankey)

3. **Add API endpoints**
   - `/api/v1/synthetic/generate`
   - `/api/v1/preview/{chart_type}`
   - Modify existing analytics endpoint

4. **Write tests**
   - Unit tests for each component
   - Integration tests for API
   - All 18 chart types tested

5. **Update documentation**
   - README with usage examples
   - API documentation
   - Integration guide

### Testing Workflow

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_all_chart_types.py -v

# Test with coverage
pytest --cov=synthetic_data_generator tests/

# Performance benchmarks
pytest tests/test_performance.py --benchmark
```

### Deployment

1. **Local Testing**
   ```bash
   # Restart local server
   kill -9 37645  # Kill old process
   python main.py  # Start new server
   ```

2. **Production Deployment** (Railway)
   ```bash
   git add .
   git commit -m "feat: Add synthetic data generation capability"
   git push origin main
   # Railway auto-deploys
   ```

3. **Validation**
   ```bash
   # Test synthetic data endpoint
   curl -X POST http://localhost:8002/api/v1/synthetic/generate \
     -H "Content-Type: application/json" \
     -d '{"chart_type": "line", "narrative": "Show Q4 revenue"}'

   # Test preview endpoint
   curl -X POST http://localhost:8002/api/v1/preview/d3_choropleth_usa \
     -H "Content-Type: application/json" \
     -d '{"narrative": "Show sales by state"}'
   ```

---

## 📚 Appendices

### Appendix A: Chart Type Constraints Reference

(See `chart_catalog.py` for authoritative source)

| Chart Type | Min | Max | Optimal | Special Requirements |
|-----------|-----|-----|---------|----------------------|
| line | 2 | 50 | 3-20 | Time-series labels |
| bar_vertical | 2 | 30 | 3-12 | - |
| bar_horizontal | 2 | 30 | 3-12 | - |
| pie | 2 | 8 | 3-6 | Sum to 100% |
| doughnut | 2 | 8 | 3-6 | Sum to 100% |
| scatter | 5 | 100 | 10-50 | X,Y coordinates |
| bubble | 3 | 50 | 5-20 | X,Y,R coordinates |
| radar | 3 | 12 | 4-8 | Normalized 0-100 |
| polar_area | 3 | 12 | 4-8 | Positive values |
| area | 3 | 50 | 5-30 | Time-series |
| area_stacked | 3 | 50 | 5-30 | Multi-series |
| bar_grouped | 2 | 30 | 3-12 | Multi-series |
| bar_stacked | 2 | 30 | 3-12 | Multi-series |
| waterfall | 3 | 20 | 4-12 | +/- values, total |
| d3_treemap | 2 | 50 | 4-15 | Hierarchical |
| d3_sunburst | 2 | 50 | 4-12 | Hierarchical |
| d3_choropleth_usa | 1 | 50 | 5-20 | US state names |
| d3_sankey | 2 | 50 | 5-15 | Flow notation |

### Appendix B: Scenario Library Reference

| Scenario | Trend | Volatility | Base Value | Format | Best For |
|----------|-------|-----------|------------|--------|----------|
| revenue_growth | upward | 0.15 | 125000 | currency | Line, area |
| revenue_decline | downward | 0.12 | 200000 | currency | Line, area |
| seasonal_revenue | stable | 0.10 | 150000 | currency | Area, line |
| financial_waterfall | stable | 0.05 | 500000 | currency | Waterfall |
| market_share | stable | 0.08 | 25.0 | percentage | Pie, doughnut |
| category_comparison | stable | 0.20 | 50000 | number | Bar charts |
| geographic_sales | stable | 0.25 | 850000 | currency | Choropleth |
| budget_flow | stable | 0.10 | 500000 | currency | Sankey |
| customer_journey | downward | 0.05 | 10000 | number | Sankey |
| hierarchical_revenue | stable | 0.18 | 200000 | currency | Treemap, sunburst |
| kpi_performance | upward | 0.12 | 75.0 | percentage | Radar |
| correlation_analysis | stable | 0.15 | 50 | number | Scatter |
| multidimensional | stable | 0.20 | 100 | number | Bubble |
| yoy_growth | upward | 0.10 | 8.5 | percentage | Bar |
| quarterly_comparison | stable | 0.12 | 180000 | currency | Bar |

### Appendix C: Narrative Parser Patterns

| Pattern Category | Examples | Extracted Context |
|-----------------|----------|-------------------|
| Timeframe | "quarterly", "Q1", "Q4" | `timeframe: 'quarter'` |
| Timeframe | "monthly", "Jan", "Dec" | `timeframe: 'month'` |
| Timeframe | "yearly", "FY2024", "annual" | `timeframe: 'year'` |
| Trend | "growth", "increase", "rising" | `trend: 'upward'` |
| Trend | "decline", "decrease", "drop" | `trend: 'downward'` |
| Trend | "stable", "steady", "flat" | `trend: 'stable'` |
| Domain | "revenue", "sales", "income" | `domain: 'revenue'` |
| Domain | "market share" | `domain: 'market_share'` |
| Domain | "performance", "KPI" | `domain: 'performance'` |
| Magnitude | "million", "$5M" | `magnitude: 'millions'` |
| Magnitude | "thousand", "$100K" | `magnitude: 'thousands'` |
| Magnitude | "20%", "percent" | `magnitude: 'percentage'` |
| Geography | "states", "USA", "US" | `geography: 'us_states'` |
| Geography | "global", "countries" | `geography: 'global'` |

### Appendix D: Example Requests & Responses

**Example 1: Simple Line Chart**

Request:
```json
{
  "chart_type": "line",
  "narrative": "Show quarterly revenue growth for 2024"
}
```

Response:
```json
{
  "success": true,
  "data": [
    {"label": "Q1 2024", "value": 125000},
    {"label": "Q2 2024", "value": 145000},
    {"label": "Q3 2024", "value": 195000},
    {"label": "Q4 2024", "value": 220000}
  ],
  "metadata": {
    "chart_type": "line",
    "scenario": "revenue_growth",
    "num_points": 4
  }
}
```

**Example 2: Choropleth Map**

Request:
```json
{
  "chart_type": "d3_choropleth_usa",
  "narrative": "Show sales performance across top 10 states",
  "num_points": 10
}
```

Response:
```json
{
  "success": true,
  "data": [
    {"label": "CA", "value": 850000},
    {"label": "TX", "value": 720000},
    {"label": "FL", "value": 680000},
    {"label": "NY", "value": 690000},
    {"label": "PA", "value": 520000},
    {"label": "IL", "value": 490000},
    {"label": "OH", "value": 460000},
    {"label": "GA", "value": 440000},
    {"label": "NC", "value": 420000},
    {"label": "MI", "value": 400000}
  ]
}
```

**Example 3: Sankey Flow**

Request:
```json
{
  "chart_type": "d3_sankey",
  "narrative": "Show budget allocation from revenue to departments to projects",
  "scenario": "budget_flow"
}
```

Response:
```json
{
  "success": true,
  "data": [
    {"label": "Revenue → Engineering", "value": 800000},
    {"label": "Revenue → Sales", "value": 600000},
    {"label": "Revenue → Marketing", "value": 400000},
    {"label": "Engineering → Product A", "value": 500000},
    {"label": "Engineering → Product B", "value": 300000},
    {"label": "Sales → Direct Sales", "value": 400000},
    {"label": "Sales → Partnerships", "value": 200000}
  ]
}
```

---

## 🎯 Next Steps

1. ✅ **Approve Plan** (Complete)
2. 🔄 **Create Module Files** (In Progress)
3. ⏳ **Implement Core Generator**
4. ⏳ **Add API Endpoints**
5. ⏳ **Write Tests**
6. ⏳ **Update Documentation**
7. ⏳ **Deploy & Validate**

---

**END OF SYNTHETIC DATA GENERATION PLAN**

**Status**: Phase 0 Complete - Ready for Phase 1 Implementation
**Estimated Completion**: 2 work days (16 hours total)
**Deployment**: Local + Railway production
**Backward Compatibility**: 100% - Zero breaking changes
