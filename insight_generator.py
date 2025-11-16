"""
LLM-Powered Insight Generator for Analytics Microservice v3.

Generates business insights from chart data using OpenAI GPT-4o-mini.
Supports different insight types for L01 (body text), L02 (detailed explanation),
and L03 (paired short descriptions).
"""

import logging
from typing import Dict, Any, Tuple, Optional
from providers import get_openai_client

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Generate AI-powered business insights from analytics data."""

    def __init__(self):
        """Initialize insight generator with OpenAI client."""
        self.client = get_openai_client()

    async def generate_l01_insight(
        self,
        chart_type: str,
        data: Dict[str, Any],
        narrative: str,
        audience: str = "executives",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate concise insight for L01 layout (body text below chart).

        Args:
            chart_type: Type of chart (line, bar, donut, etc.)
            data: Chart data with labels and values
            narrative: User's description of what the chart should show
            audience: Target audience (executives, managers, analysts, etc.)
            context: Optional context from previous slides

        Returns:
            2-3 sentence insight (max 150 words)
        """
        data_summary = self._summarize_data(data)

        prompt = f"""You are a business analyst generating insights for a presentation slide.

Chart Type: {chart_type}
Data Summary: {data_summary}
User Request: {narrative}
Audience: {audience}

Generate 2-3 concise sentences (max 150 words) that:
1. Summarize the key finding from the data
2. Identify the most notable trend or pattern
3. Provide business context or implication

Write in active voice, professional tone suitable for presentations. No bullet points.
Use specific numbers from the data when relevant.

Example: "Revenue grew steadily throughout FY 2024, achieving 42% growth from Q1 to Q4. The strongest acceleration occurred in Q2-Q3, driven by new product launches and market expansion."
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business analyst expert at interpreting data and generating executive-level insights for presentations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )

            insight = response.choices[0].message.content.strip()
            logger.info(f"Generated L01 insight: {len(insight)} characters")
            return insight

        except Exception as e:
            logger.error(f"Failed to generate L01 insight: {e}")
            # Fallback to basic summary
            return self._generate_fallback_insight(data, narrative)

    async def generate_l02_explanation(
        self,
        chart_type: str,
        data: Dict[str, Any],
        narrative: str,
        statistical_summary: Optional[str] = None,
        audience: str = "executives",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate detailed explanation for L02 layout (right text panel).

        Args:
            chart_type: Type of chart
            data: Chart data with labels and values
            narrative: User's description
            statistical_summary: Optional statistical analysis (R², correlations, etc.)
            audience: Target audience
            context: Optional context

        Returns:
            4-6 sentence detailed explanation (max 250 words)
        """
        data_summary = self._summarize_data(data)

        prompt = f"""You are a business analyst generating detailed explanations for complex charts in presentations.

Chart Type: {chart_type}
Data Summary: {data_summary}
Statistical Info: {statistical_summary or 'Not provided'}
User Request: {narrative}
Audience: {audience}

Generate 4-6 sentences (max 250 words) that:
1. Explain what the visualization shows
2. Highlight key statistical findings (correlations, outliers, trends)
3. Provide interpretation and business implications
4. Suggest actionable insights or next steps

Write professionally for {audience}. Include specific numbers when relevant.
This will appear in a text panel next to the chart, so be detailed but clear.

Example: "This scatter plot reveals a strong positive correlation (R² = 0.87) between marketing spend and sales revenue. Each $1 invested in marketing generates approximately $4.20 in sales. Notable outliers in Q2 suggest seasonal variations that should be factored into budget planning. The trend line indicates diminishing returns above $50K monthly spend, suggesting an optimal investment threshold."
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business analyst expert at interpreting complex data visualizations and explaining them clearly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            explanation = response.choices[0].message.content.strip()
            logger.info(f"Generated L02 explanation: {len(explanation)} characters")
            return explanation

        except Exception as e:
            logger.error(f"Failed to generate L02 explanation: {e}")
            # Fallback
            return self._generate_fallback_explanation(data, narrative)

    async def generate_l03_descriptions(
        self,
        left_data: Dict[str, Any],
        right_data: Dict[str, Any],
        narrative: str,
        comparison_context: str = "before/after"
    ) -> Tuple[str, str]:
        """
        Generate paired short descriptions for L03 side-by-side comparison.

        Args:
            left_data: Data for left chart
            right_data: Data for right chart
            narrative: Overall comparison description
            comparison_context: Type of comparison (before/after, option A/B, period 1/2)

        Returns:
            Tuple of (left_description, right_description), each 20-30 words
        """
        left_summary = self._summarize_data(left_data)
        right_summary = self._summarize_data(right_data)

        # Generate left description
        left_desc = await self._generate_short_description(
            left_data,
            left_summary,
            "baseline/before/option A",
            narrative
        )

        # Generate right description
        right_desc = await self._generate_short_description(
            right_data,
            right_summary,
            "improved/after/option B",
            narrative
        )

        return left_desc, right_desc

    async def _generate_short_description(
        self,
        data: Dict[str, Any],
        data_summary: str,
        state: str,
        context: str
    ) -> str:
        """Generate a single short description (20-30 words)."""

        prompt = f"""Generate a brief description (20-30 words) for a chart in a side-by-side comparison slide.

Data: {data_summary}
This represents: {state}
Context: {context}

Be concise and specific. Include a key metric if relevant.

Example: "Pre-automation baseline showing manual processing times across departments. Average task completion: 4.2 hours."

Generate description:"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=60
            )

            description = response.choices[0].message.content.strip()
            logger.info(f"Generated short description: {len(description.split())} words")
            return description

        except Exception as e:
            logger.error(f"Failed to generate short description: {e}")
            # Simple fallback
            values = data.get("values", [])
            if values:
                avg = sum(values) / len(values)
                return f"{state.title()} state with average value of {avg:.1f} across {len(values)} data points."
            return f"{state.title()} state visualization."

    def _summarize_data(self, data: Dict[str, Any]) -> str:
        """
        Create text summary of data for LLM context.

        Args:
            data: Chart data dictionary

        Returns:
            Human-readable data summary
        """
        labels = data.get("labels", [])
        values = data.get("values", [])

        if not values:
            return "No data provided"

        summary_parts = []

        # Basic stats
        summary_parts.append(f"Data points: {len(values)}")

        # Range
        if labels and len(labels) == len(values):
            first_label, first_val = labels[0], values[0]
            last_label, last_val = labels[-1], values[-1]
            summary_parts.append(f"Range: {first_label}={first_val} to {last_label}={last_val}")

        # Statistical summary
        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        summary_parts.append(f"Min: {min_val}, Max: {max_val}, Average: {avg_val:.1f}")

        # Trend if applicable
        if len(values) >= 2:
            first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
            second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
            if second_half_avg > first_half_avg * 1.1:
                summary_parts.append("Trend: Increasing")
            elif second_half_avg < first_half_avg * 0.9:
                summary_parts.append("Trend: Decreasing")
            else:
                summary_parts.append("Trend: Stable")

        return "; ".join(summary_parts)

    def _generate_fallback_insight(self, data: Dict[str, Any], narrative: str) -> str:
        """Generate basic insight when LLM fails."""
        values = data.get("values", [])
        labels = data.get("labels", [])

        if not values:
            return "Data visualization showing key metrics for analysis."

        min_val = min(values)
        max_val = max(values)
        avg_val = sum(values) / len(values)

        if labels and len(labels) == len(values):
            min_idx = values.index(min_val)
            max_idx = values.index(max_val)

            return f"Analysis shows values ranging from {min_val} ({labels[min_idx]}) to {max_val} ({labels[max_idx]}), with an average of {avg_val:.1f}. {narrative}"
        else:
            return f"Data analysis reveals values ranging from {min_val} to {max_val}, with an average of {avg_val:.1f}."

    def _generate_fallback_explanation(self, data: Dict[str, Any], narrative: str) -> str:
        """Generate basic explanation when LLM fails."""
        data_summary = self._summarize_data(data)
        return f"This visualization presents {narrative}. {data_summary}. The data provides insights into key trends and patterns for informed decision-making."
