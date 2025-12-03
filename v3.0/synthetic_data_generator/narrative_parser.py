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
