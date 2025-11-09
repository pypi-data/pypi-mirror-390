"""
Decorator-based tracking for user-controlled instrumentation.
Works with ANY function, not just AI libraries.
"""

import functools
import time
from typing import Callable, Any, Optional
from .logger import get_logger
from .utils import (
    calculate_cost,
    generate_prompt_id,
    get_timestamp,
    validate_output
)


def track(
    model: Optional[str] = None,
    extract_tokens: Optional[Callable] = None,
    extract_model: Optional[Callable] = None,
    calculate_cost_func: Optional[Callable] = None
):
    """
    Decorator to track any function call.
    
    Usage:
        @glassbox.track(model="my-model")
        def my_ai_call(prompt):
            # Your AI code here
            return response
        
        # Or with custom extractors:
        @glassbox.track(
            model="custom-api",
            extract_tokens=lambda r: (r.input_count, r.output_count),
            extract_model=lambda r: r.model_name
        )
        def custom_ai_call(prompt):
            return custom_api.generate(prompt)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger()
            if not logger:
                return func(*args, **kwargs)
            
            start_time = time.time()
            prompt_id = generate_prompt_id()
            model_name = model or f"{func.__name__}-unknown"
            
            try:
                response = func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract tokens
                if extract_tokens:
                    input_tokens, output_tokens = extract_tokens(response)
                else:
                    # Default: try to extract from response
                    input_tokens, output_tokens = _default_extract_tokens(response)
                
                # Extract model
                if extract_model:
                    model_name = extract_model(response) or model_name
                
                # Calculate cost
                if calculate_cost_func:
                    cost_usd = calculate_cost_func(response)
                else:
                    cost_usd = calculate_cost(model_name, input_tokens, output_tokens)
                
                valid = validate_output(response)
                
                logger.log(
                    model=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd,
                    valid=valid,
                    prompt_id=prompt_id
                )
                
                return response
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                logger.log(
                    model=model_name,
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=latency_ms,
                    cost_usd=0.0,
                    valid=False,
                    prompt_id=prompt_id
                )
                raise
        
        return wrapper
    return decorator


def _default_extract_tokens(response: Any) -> tuple[int, int]:
    """Default token extraction - tries common patterns."""
    if hasattr(response, 'usage'):
        usage = response.usage
        input_tokens = getattr(usage, 'prompt_tokens', 0) or getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'completion_tokens', 0) or getattr(usage, 'output_tokens', 0)
        return input_tokens, output_tokens
    
    if isinstance(response, dict):
        if 'usage' in response:
            usage = response['usage']
            input_tokens = usage.get('prompt_tokens') or usage.get('input_tokens', 0)
            output_tokens = usage.get('completion_tokens') or usage.get('output_tokens', 0)
            return input_tokens, output_tokens
    
    # Fallback: estimate
    if isinstance(response, str):
        return 0, len(response.split()) // 2
    
    return 0, 0


def track_call(func: Callable = None, *, model: Optional[str] = None):
    """
    Simpler decorator syntax.
    
    Usage:
        @glassbox.track_call(model="gpt-4")
        def my_function():
            return ai_call()
    """
    if func is None:
        return track(model=model)
    return track(model=model)(func)

