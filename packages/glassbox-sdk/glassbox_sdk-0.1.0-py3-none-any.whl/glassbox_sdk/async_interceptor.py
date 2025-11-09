"""
Async HTTP Interceptor
Intercepts async HTTP requests (httpx.AsyncClient, aiohttp, etc.)
"""

import functools
import time
import json
from typing import Optional, Any
from urllib.parse import urlparse
import re

from .logger import get_logger
from .utils import (
    calculate_cost,
    generate_prompt_id,
    validate_output
)
from .http_interceptor import is_ai_api_call, extract_tokens_from_response, extract_model_from_request


async def wrap_httpx_async():
    """Wrap httpx.AsyncClient to intercept async HTTP calls."""
    try:
        import httpx
        HTTPX_AVAILABLE = True
    except ImportError:
        HTTPX_AVAILABLE = False
        return
    
    if not HTTPX_AVAILABLE:
        return
    
    # Store original AsyncClient
    original_async_client = httpx.AsyncClient
    
    class WrappedAsyncClient(original_async_client):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Wrap post method
            original_post = self.post
            
            @functools.wraps(original_post)
            async def wrapped_post(*args, **kwargs):
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
                            except:
                                request_data = {}
                        
                        model = extract_model_from_request(request_data, provider or 'unknown')
                        
                        try:
                            response = await original_post(*args, **kwargs)
                            latency_ms = (time.time() - start_time) * 1000
                            
                            # Parse response
                            try:
                                response_data = response.json()
                            except:
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
                                pass
                            raise
                
                return await original_post(*args, **kwargs)
            
            self.post = wrapped_post
    
    # Replace the class
    httpx.AsyncClient = WrappedAsyncClient


async def wrap_aiohttp():
    """Wrap aiohttp.ClientSession to intercept async HTTP calls."""
    try:
        import aiohttp
        AIOHTTP_AVAILABLE = True
    except ImportError:
        AIOHTTP_AVAILABLE = False
        return
    
    if not AIOHTTP_AVAILABLE:
        return
    
    # Store original ClientSession
    original_session = aiohttp.ClientSession
    
    class WrappedClientSession(original_session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            original_post = self.post
            
            @functools.wraps(original_post)
            async def wrapped_post(*args, **kwargs):
                url = args[0] if args else kwargs.get('url', '')
                is_ai, provider = is_ai_api_call(str(url), 'POST')
                
                if is_ai:
                    logger = get_logger()
                    if logger:
                        start_time = time.time()
                        prompt_id = generate_prompt_id()
                        
                        # Get request data
                        json_data = kwargs.get('json')
                        model = extract_model_from_request(json_data, provider or 'unknown')
                        
                        try:
                            async with original_post(*args, **kwargs) as response:
                                latency_ms = (time.time() - start_time) * 1000
                                
                                # Parse response
                                try:
                                    response_data = await response.json()
                                except:
                                    response_data = await response.text()
                                
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
                                pass
                            raise
                
                return original_post(*args, **kwargs)
            
            self.post = wrapped_post
    
    # Replace the class
    aiohttp.ClientSession = WrappedClientSession


def intercept_async_http():
    """
    Intercept async HTTP requests from common libraries.
    This enables tracking of async AI API calls.
    """
    try:
        import asyncio
        # Run async setup
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, schedule for later
            asyncio.create_task(wrap_httpx_async())
            asyncio.create_task(wrap_aiohttp())
        else:
            # If loop not running, run setup
            asyncio.run(wrap_httpx_async())
            asyncio.run(wrap_aiohttp())
    except Exception:
        # Silently fail if async setup fails
        pass

