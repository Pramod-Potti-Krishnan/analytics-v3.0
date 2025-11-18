"""
L02 Layout Assembler for Analytics Microservice v3

Assembles HTML for L02 template (L25 variant) with two sections:
- element_3: Chart (1260px × 720px) - Left 70%
- element_2: Observations (540px × 720px) - Right 30%

Follows Director Agent integration specification v1.0
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class L02LayoutAssembler:
    """Assembles L02-specific HTML for charts and observations."""

    # L02 Template Dimensions (within L25 content area: 1800×720)
    CHART_WIDTH = 1260  # 70% of content area
    CHART_HEIGHT = 720
    OBSERVATIONS_WIDTH = 540  # 30% of content area
    OBSERVATIONS_HEIGHT = 720

    # Theme color palettes - Layout Builder standard colors
    THEMES = {
        "professional": {
            "bg": "#f8f9fa",      # Layout Builder background
            "heading": "#1f2937",  # Layout Builder heading color
            "text": "#374151",     # Layout Builder body text color
            "border": "#e2e8f0"
        },
        "corporate": {
            "bg": "#f3f4f6",
            "heading": "#111827",
            "text": "#4b5563",
            "border": "#d1d5db"
        },
        "vibrant": {
            "bg": "#fef3c7",
            "heading": "#78350f",
            "text": "#92400e",
            "border": "#fde68a"
        }
    }

    def __init__(self, theme: str = "professional"):
        """
        Initialize layout assembler.

        Args:
            theme: Visual theme (professional, corporate, vibrant)
        """
        self.theme = theme if theme in self.THEMES else "professional"
        self.colors = self.THEMES[self.theme]

    def assemble_chart_html(
        self,
        canvas_html: str,
        chart_id: str,
        enable_editor: bool = False
    ) -> str:
        """
        Assemble chart HTML for element_3 (L02 left panel).

        Args:
            canvas_html: Complete Canvas HTML with Chart.js config
            chart_id: Unique chart identifier
            enable_editor: Include interactive edit button

        Returns:
            HTML string for element_3 field (1260×720px container)
        """
        logger.info(f"Assembling L02 chart HTML for {chart_id}")

        # v3.3.1: Return canvas_html directly - chart generator already provides the container
        # Removed double-wrapping that was hiding grid lines and Y-axis values
        logger.debug(f"Chart HTML length: {len(canvas_html)} characters")
        return canvas_html

    def assemble_observations_html(
        self,
        insights_text: str,
        title: str = "Key Insights",
        max_chars: int = 1000
    ) -> str:
        """
        Assemble observations HTML for element_2 (L02 right panel).

        Args:
            insights_text: Business insights/observations text (expected to be pre-formatted bullets from LLM)
            title: Panel heading (default: "Key Insights")
            max_chars: Maximum character limit (v3.3.3: increased to 1000 for complete bullets)

        Returns:
            HTML string for element_2 field (540×720px panel)
        """
        logger.info(f"Assembling L02 observations HTML ({len(insights_text)} chars)")

        # v3.3.3: LLM now generates pre-formatted bullets, just split by newlines
        # Remove any leading bullet markers (-, •, *, etc.) and clean whitespace
        bullets = []
        for line in insights_text.split('\n'):
            line = line.strip()
            if line:
                # Remove common bullet markers
                if line.startswith(('-', '•', '*', '+')):
                    line = line[1:].strip()
                bullets.append(line)

        # Limit to 7 bullets max (LLM should already do this, but enforce as backup)
        bullets = bullets[:7]

        # v3.3.3: NO TRUNCATION - LLM generates complete bullets (100-140 chars each)
        # Build bullet list HTML
        bullets_html = ""
        for bullet in bullets:
            bullets_html += f"""        <li style="font-family: 'Inter', -apple-system, sans-serif; font-size: 19px; line-height: 1.65; color: {self.colors['text']}; margin: 0 0 10px 0; text-align: left;">
            {bullet}
        </li>
"""

        # Styled observations panel with bullet list (v3.3.1: left-aligned bullets)
        html = f"""<div class="l02-observations-panel" style="width: {self.OBSERVATIONS_WIDTH}px; height: 720px; padding: 40px 32px; background: {self.colors['bg']}; border-radius: 8px; overflow-y: auto; box-sizing: border-box;">
    <h3 style="font-family: 'Inter', -apple-system, sans-serif; font-size: 22px; font-weight: 600; color: {self.colors['heading']}; margin: 0 0 18px 0; line-height: 1.3; text-align: left;">
        {title}
    </h3>
    <ul style="margin: 0; padding-left: 20px; list-style-type: disc; text-align: left;">
{bullets_html}    </ul>
</div>"""

        logger.debug(f"Observations HTML length: {len(html)} characters")
        return html

    def assemble_l02_content(
        self,
        canvas_html: str,
        chart_id: str,
        insights_text: str,
        enable_editor: bool = False,
        observations_title: str = "Key Insights"
    ) -> Dict[str, str]:
        """
        Assemble complete L02 content with chart and observations.

        This is the main method that returns the 2 HTML fields
        for Director to map to L02 template.

        Args:
            canvas_html: Chart.js canvas HTML
            chart_id: Unique chart identifier
            insights_text: Business insights/observations
            enable_editor: Include interactive edit button
            observations_title: Heading for observations panel

        Returns:
            Dictionary with element_3 (chart) and element_2 (observations):
            {
                "element_3": "<div>chart html</div>",
                "element_2": "<div>observations html</div>"
            }
        """
        logger.info(f"Assembling complete L02 content for {chart_id}")

        # Assemble chart HTML (element_3)
        element_3 = self.assemble_chart_html(
            canvas_html=canvas_html,
            chart_id=chart_id,
            enable_editor=enable_editor
        )

        # Assemble observations HTML (element_2)
        element_2 = self.assemble_observations_html(
            insights_text=insights_text,
            title=observations_title,
            max_chars=1000  # v3.3.3: Increased to 1000 for complete bullet points
        )

        result = {
            "element_3": element_3,
            "element_2": element_2
        }

        logger.info(f"L02 assembly complete - element_3: {len(element_3)} chars, element_2: {len(element_2)} chars")

        return result


# Convenience function for quick assembly
def assemble_l02_layout(
    canvas_html: str,
    chart_id: str,
    insights_text: str,
    theme: str = "professional",
    enable_editor: bool = False
) -> Dict[str, str]:
    """
    Quick convenience function to assemble L02 layout.

    Args:
        canvas_html: Chart.js canvas HTML
        chart_id: Unique chart identifier
        insights_text: Business insights text
        theme: Visual theme (professional, corporate, vibrant)
        enable_editor: Include interactive edit button

    Returns:
        Dictionary with element_3 and element_2 HTML fields
    """
    assembler = L02LayoutAssembler(theme=theme)
    return assembler.assemble_l02_content(
        canvas_html=canvas_html,
        chart_id=chart_id,
        insights_text=insights_text,
        enable_editor=enable_editor
    )
