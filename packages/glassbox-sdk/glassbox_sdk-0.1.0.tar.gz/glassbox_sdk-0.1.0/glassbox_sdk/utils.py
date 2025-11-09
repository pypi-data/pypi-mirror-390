"""
Utility functions for Glassbox SDK
"""

import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost in USD based on model and token usage.
    Pricing as of 2024 (approximate).
    """
    pricing = {
        "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
        "gpt-4-turbo": {"input": 0.01 / 1000, "output": 0.03 / 1000},
        "gpt-3.5-turbo": {"input": 0.0015 / 1000, "output": 0.002 / 1000},
        "claude-3-opus": {"input": 0.015 / 1000, "output": 0.075 / 1000},
        "claude-3-sonnet": {"input": 0.003 / 1000, "output": 0.015 / 1000},
        "claude-3-haiku": {"input": 0.00025 / 1000, "output": 0.00125 / 1000},
    }
    
    # Try exact match first
    if model in pricing:
        cost = (input_tokens * pricing[model]["input"]) + (output_tokens * pricing[model]["output"])
        return round(cost, 6)
    
    # Try partial match (e.g., "gpt-4-0125" -> "gpt-4")
    for key, prices in pricing.items():
        if model.startswith(key):
            cost = (input_tokens * prices["input"]) + (output_tokens * prices["output"])
            return round(cost, 6)
    
    # Default fallback
    return round((input_tokens + output_tokens) * 0.002 / 1000, 6)


def extract_tokens(response: Any) -> tuple[int, int]:
    """
    Extract input and output tokens from various response formats.
    Supports OpenAI, Anthropic, and LangChain formats.
    """
    input_tokens = 0
    output_tokens = 0
    
    # OpenAI format
    if hasattr(response, "usage"):
        usage = response.usage
        input_tokens = getattr(usage, "prompt_tokens", 0) or getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "completion_tokens", 0) or getattr(usage, "output_tokens", 0)
    
    # Anthropic format
    elif hasattr(response, "usage"):
        usage = response.usage
        input_tokens = getattr(usage, "input_tokens", 0)
        output_tokens = getattr(usage, "output_tokens", 0)
    
    # Dictionary format
    elif isinstance(response, dict):
        if "usage" in response:
            usage = response["usage"]
            input_tokens = usage.get("prompt_tokens", usage.get("input_tokens", 0))
            output_tokens = usage.get("completion_tokens", usage.get("output_tokens", 0))
    
    return input_tokens, output_tokens


def extract_model(response: Any, default: str = "unknown") -> str:
    """
    Extract model name from response.
    """
    if hasattr(response, "model"):
        return response.model
    elif isinstance(response, dict):
        return response.get("model", default)
    return default


def generate_prompt_id() -> str:
    """
    Generate a unique prompt ID.
    """
    import uuid
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    """
    return datetime.now(timezone.utc).isoformat()


def validate_output(response: Any) -> bool:
    """
    Basic validation: check if response is not empty and has expected structure.
    Can be extended with custom validation logic.
    """
    if response is None:
        return False
    
    # OpenAI format
    if hasattr(response, "choices") and len(response.choices) > 0:
        return True
    
    # Anthropic format
    if hasattr(response, "content") and len(response.content) > 0:
        return True
    
    # Dictionary format
    if isinstance(response, dict):
        if "choices" in response and len(response.get("choices", [])) > 0:
            return True
        if "content" in response and len(response.get("content", [])) > 0:
            return True
    
    # String format
    if isinstance(response, str) and len(response.strip()) > 0:
        return True
    
    return False

