"""
Universal HTTP Request Interceptor
Intercepts HTTP requests to detect and log AI API calls automatically.
Works with ANY AI provider that uses HTTP.
"""

import functools
import time
import json
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

# Try to import common HTTP libraries
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from .logger import get_logger
from .utils import (
    calculate_cost,
    generate_prompt_id,
    get_timestamp,
    validate_output
)


# AI API patterns to detect
AI_API_PATTERNS = [
    # OpenAI
    (r'api\.openai\.com', 'openai'),
    (r'openai\.azure\.com', 'openai'),
    
    # Anthropic
    (r'api\.anthropic\.com', 'anthropic'),
    
    # Cohere
    (r'api\.cohere\.ai', 'cohere'),
    
    # HuggingFace
    (r'inference-api\.huggingface\.co', 'huggingface'),
    (r'api-inference\.huggingface\.co', 'huggingface'),
    
    # Google AI
    (r'generativelanguage\.googleapis\.com', 'google-ai'),
    (r'aiplatform\.googleapis\.com', 'google-vertex'),
    
    # Azure OpenAI
    (r'\.openai\.azure\.com', 'azure-openai'),
    
    # Custom patterns (users can add)
]

# Known AI endpoints
AI_ENDPOINTS = [
    '/v1/chat/completions',  # OpenAI
    '/v1/completions',  # OpenAI
    '/v1/messages',  # Anthropic
    '/v1/generate',  # Cohere
    '/api/generate',  # HuggingFace
    '/v1/models',  # Various
]


def is_ai_api_call(url: str, method: str = 'POST') -> tuple:
    """
    Detect if an HTTP request is an AI API call.
    Returns (is_ai_call, provider_name)
    """
    if method.upper() != 'POST':
        return False, None
    
    parsed = urlparse(url)
    hostname = parsed.hostname or ''
    path = parsed.path
    
    # Check hostname patterns
    for pattern, provider in AI_API_PATTERNS:
        if re.search(pattern, hostname, re.IGNORECASE):
            return True, provider
    
    # Check endpoint patterns
    for endpoint in AI_ENDPOINTS:
        if endpoint in path:
            # Try to infer provider from hostname
            if 'openai' in hostname.lower():
                return True, 'openai'
            elif 'anthropic' in hostname.lower():
                return True, 'anthropic'
            elif 'cohere' in hostname.lower():
                return True, 'cohere'
            elif 'huggingface' in hostname.lower():
                return True, 'huggingface'
            else:
                return True, 'unknown'
    
    return False, None


def extract_tokens_from_response(response_data: Any, provider: str) -> tuple:
    """
    Extract token counts from response based on provider.
    """
    if isinstance(response_data, dict):
        # OpenAI format
        if 'usage' in response_data:
            usage = response_data['usage']
            input_tokens = usage.get('prompt_tokens') or usage.get('input_tokens', 0)
            output_tokens = usage.get('completion_tokens') or usage.get('output_tokens', 0)
            return input_tokens, output_tokens
        
        # Anthropic format
        if 'usage' in response_data:
            usage = response_data['usage']
            input_tokens = usage.get('input_tokens', 0)
            output_tokens = usage.get('output_tokens', 0)
            return input_tokens, output_tokens
        
        # Cohere format
        if 'meta' in response_data and 'tokens' in response_data['meta']:
            tokens = response_data['meta']['tokens']
            input_tokens = tokens.get('input_tokens', 0)
            output_tokens = tokens.get('output_tokens', 0)
            return input_tokens, output_tokens
    
    # Fallback: estimate from response size
    if isinstance(response_data, (str, bytes)):
        size = len(response_data) if isinstance(response_data, str) else len(response_data)
        return 0, size // 4  # Rough estimate
    
    return 0, 0


def extract_model_from_request(request_data: Any, provider: str) -> str:
    """
    Extract model name from request.
    """
    if isinstance(request_data, dict):
        # OpenAI format
        if 'model' in request_data:
            return request_data['model']
        
        # Anthropic format
        if 'model' in request_data:
            return request_data['model']
        
        # Cohere format
        if 'model' in request_data:
            return request_data['model']
    
    return f'{provider}-unknown'


def wrap_requests():
    """Wrap requests library to intercept HTTP calls."""
    if not REQUESTS_AVAILABLE:
        return
    
    original_post = requests.post
    original_get = requests.get
    
    @functools.wraps(original_post)
    def wrapped_post(*args, **kwargs):
        url = args[0] if args else kwargs.get('url', '')
        is_ai, provider = is_ai_api_call(url, 'POST')
        
        if is_ai:
            logger = get_logger()
            if logger:
                start_time = time.time()
                prompt_id = generate_prompt_id()
                
                # Get request data
                request_data = kwargs.get('json') or kwargs.get('data')
                if isinstance(request_data, str):
                    try:
                        request_data = json.loads(request_data)
                    except (TypeError, json.JSONDecodeError, ValueError):
                        # Request data is not valid JSON, use empty dict
                        request_data = {}
                
                model = extract_model_from_request(request_data, provider or 'unknown')
                
                try:
                    response = original_post(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Parse response
                    try:
                        response_data = response.json()
                    except (ValueError, json.JSONDecodeError):
                        # Response is not JSON, use text
                        response_data = response.text
                    
                    input_tokens, output_tokens = extract_tokens_from_response(response_data, provider or 'unknown')
                    cost_usd = calculate_cost(model, input_tokens, output_tokens)
                    valid = validate_output(response_data)
                    
                    # CRITICAL: Never let logging errors break user code
                    try:
                        logger.log(
                            model=model,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            latency_ms=latency_ms,
                            cost_usd=cost_usd,
                            valid=valid,
                            prompt_id=prompt_id
                        )
                    except Exception:
                        # Silently fail - logging should never break user code
                        pass
                    
                    return response
                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    try:
                        logger.log(
                            model=model,
                            input_tokens=0,
                            output_tokens=0,
                            latency_ms=latency_ms,
                            cost_usd=0.0,
                            valid=False,
                            prompt_id=prompt_id
                        )
                    except Exception:
                        # Silently fail - don't interfere with original exception
                        pass
                    raise  # Re-raise original exception
        
        return original_post(*args, **kwargs)
    
    requests.post = wrapped_post


def wrap_httpx():
    """Wrap httpx library to intercept HTTP calls."""
    if not HTTPX_AVAILABLE:
        return
    
    # Similar implementation for httpx
    # (httpx uses async, so needs async wrapper)
    pass


def intercept_http() -> None:
    """
    Intercept HTTP requests from common libraries.
    This is the universal fallback that works with ANY HTTP-based AI API.
    """
    wrap_requests()
    wrap_httpx()
    # Add more HTTP libraries as needed

