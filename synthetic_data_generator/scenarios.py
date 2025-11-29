"""
Business scenario templates for synthetic data generation.

Each scenario defines realistic patterns for different business contexts.
"""

from dataclasses import dataclass, field
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
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

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


def list_scenarios() -> list:
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
