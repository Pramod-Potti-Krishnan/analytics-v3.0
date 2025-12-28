"""
OpenAI provider configuration for analytics microservice.
"""

from typing import Optional
import openai
from settings import settings


def get_llm_model(model_choice: Optional[str] = None):
    """
    Get OpenAI model configuration for analytics tasks.
    
    Args:
        model_choice: Optional override for model choice
    
    Returns:
        Configured OpenAI model name
    """
    return model_choice or settings.llm_model


def get_openai_client():
    """
    Get configured OpenAI client.
    
    Returns:
        OpenAI client instance
    """
    return openai.AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url
    )


def get_chart_model():
    """
    Get optimized model for chart generation tasks.
    Uses gpt-4o-mini for fast, cost-effective processing.
    
    Returns:
        OpenAI model name optimized for chart generation
    """
    return "gpt-4o-mini"