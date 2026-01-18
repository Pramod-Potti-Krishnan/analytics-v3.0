"""
MCP-style tools for Data Ingestion Agent.

Provides 9 tools for the chain-of-thought reasoning workflow:
1. get_session_info - Retrieve session metadata
2. analyze_data_structure - Deep data analysis
3. parse_user_intent - NLP intent extraction (OpenAI)
4. detect_data_patterns - Pattern detection
5. transform_data - Data transformation
6. preview_transform - Preview without commit
7. generate_chart - Chart generation (wraps AtomicChartGenerator)
8. validate_result - Quality validation
9. suggest_alternatives - Alternative suggestions
"""

from .session_tools import get_session_info
from .analysis_tools import analyze_data_structure, detect_patterns
from .intent_tools import parse_user_intent
from .transform_tools import transform_data, preview_transform
from .chart_tools import generate_chart
from .validation_tools import validate_result, suggest_alternatives

__all__ = [
    "get_session_info",
    "analyze_data_structure",
    "detect_patterns",
    "parse_user_intent",
    "transform_data",
    "preview_transform",
    "generate_chart",
    "validate_result",
    "suggest_alternatives",
]
