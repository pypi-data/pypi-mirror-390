"""
Auto-wrapping functionality for OpenAI, Anthropic, and LangChain
Enables zero-configuration instrumentation
"""

import functools
import time
from typing import Any, Optional
from .logger import get_logger
from .utils import extract_tokens, extract_model, calculate_cost, validate_output, generate_prompt_id


def wrap_openai() -> None:
    """Auto-wrap OpenAI client methods."""
    try:
        import openai
        
        # Wrap ChatCompletion.create
        if hasattr(openai, 'ChatCompletion'):
            original_create = openai.ChatCompletion.create
            
            @functools.wraps(original_create)
            def wrapped_create(*args, **kwargs):
                logger = get_logger()
                if not logger:
                    return original_create(*args, **kwargs)
                
                model = kwargs.get('model', args[1] if len(args) > 1 else 'unknown')
                start_time = time.time()
                prompt_id = generate_prompt_id()
                
                try:
                    response = original_create(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    input_tokens, output_tokens = extract_tokens(response)
                    model_name = extract_model(response, model)
                    cost_usd = calculate_cost(model_name, input_tokens, output_tokens)
                    valid = validate_output(response)
                    
                    # CRITICAL: Never let logging errors break user code
                    try:
                        logger.log(
                            model=model_name,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            latency_ms=latency_ms,
                            cost_usd=cost_usd,
                            valid=valid,
                            prompt_id=prompt_id
                        )
                    except (AttributeError, ValueError, TypeError) as e:
                        # Logging errors should never break user code
                        # These are non-fatal - continue execution
                        pass
                    
                    return response
                except (AttributeError, ValueError, TypeError, RuntimeError) as e:
                    # Log error case (but don't let logging break error handling)
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
                    except (AttributeError, ValueError, TypeError) as e:
                        # Don't interfere with original exception - logging failed
                        pass
                    raise  # Re-raise original exception
            
            openai.ChatCompletion.create = wrapped_create
        
        # Wrap OpenAI v1+ client (monkey patch after instantiation)
        if hasattr(openai, 'OpenAI'):
            # Store original class
            original_openai_class = openai.OpenAI
            
            class WrappedOpenAI(original_openai_class):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Wrap chat.completions.create after initialization
                    if hasattr(self, 'chat') and hasattr(self.chat, 'completions'):
                        original_create = self.chat.completions.create
                        
                        @functools.wraps(original_create)
                        def wrapped_create(*args, **kwargs):
                            logger = get_logger()
                            if not logger:
                                return original_create(*args, **kwargs)
                            
                            model = kwargs.get('model', args[0] if args else 'unknown')
                            start_time = time.time()
                            prompt_id = generate_prompt_id()
                            
                            try:
                                response = original_create(*args, **kwargs)
                                latency_ms = (time.time() - start_time) * 1000
                                
                                input_tokens, output_tokens = extract_tokens(response)
                                model_name = extract_model(response, model)
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
                                    model=model,
                                    input_tokens=0,
                                    output_tokens=0,
                                    latency_ms=latency_ms,
                                    cost_usd=0.0,
                                    valid=False,
                                    prompt_id=prompt_id
                                )
                                raise
                        
                        self.chat.completions.create = wrapped_create
            
            # Replace the class
            openai.OpenAI = WrappedOpenAI
            
    except ImportError:
        pass  # OpenAI not installed - this is expected if library not available


def wrap_anthropic():
    """Auto-wrap Anthropic client methods."""
    try:
        import anthropic
        
        if hasattr(anthropic, 'Anthropic'):
            original_init = anthropic.Anthropic.__init__
            
            def patched_init(self, *args, **kwargs):
                original_init(self, *args, **kwargs)
                
                # Wrap messages.create
                if hasattr(self, 'messages'):
                    original_create = self.messages.create
                    
                    @functools.wraps(original_create)
                    def wrapped_create(*args, **kwargs):
                        logger = get_logger()
                        if not logger:
                            return original_create(*args, **kwargs)
                        
                        model = kwargs.get('model', 'claude-3-sonnet')
                        start_time = time.time()
                        prompt_id = generate_prompt_id()
                        
                        try:
                            response = original_create(*args, **kwargs)
                            latency_ms = (time.time() - start_time) * 1000
                            
                            input_tokens, output_tokens = extract_tokens(response)
                            model_name = extract_model(response, model)
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
                                model=model,
                                input_tokens=0,
                                output_tokens=0,
                                latency_ms=latency_ms,
                                cost_usd=0.0,
                                valid=False,
                                prompt_id=prompt_id
                            )
                            raise
                    
                    self.messages.create = wrapped_create
            
            anthropic.Anthropic.__init__ = patched_init
            
    except ImportError:
        pass  # Anthropic not installed


def wrap_langchain():
    """Auto-wrap LangChain LLM calls."""
    try:
        from langchain.callbacks.base import BaseCallbackHandler
        from langchain.schema import LLMResult
        
        class GlassboxCallbackHandler(BaseCallbackHandler):
            """LangChain callback handler for Glassbox."""
            
            def __init__(self):
                super().__init__()
                self.start_times = {}
                self.prompt_ids = {}
            
            def on_llm_start(self, serialized, prompts, **kwargs):
                """Called when LLM starts running."""
                logger = get_logger()
                if logger:
                    run_id = kwargs.get('run_id', str(id(prompts)))
                    self.start_times[run_id] = time.time()
                    self.prompt_ids[run_id] = generate_prompt_id()
            
            def on_llm_end(self, response: LLMResult, **kwargs):
                """Called when LLM ends running."""
                logger = get_logger()
                if not logger:
                    return
                
                run_id = kwargs.get('run_id', '')
                if run_id not in self.start_times:
                    return
                
                start_time = self.start_times.pop(run_id)
                prompt_id = self.prompt_ids.pop(run_id, generate_prompt_id())
                latency_ms = (time.time() - start_time) * 1000
                
                # Extract data from LLMResult
                generations = response.generations
                if generations and len(generations) > 0:
                    # Estimate tokens (LangChain doesn't always provide usage)
                    total_tokens = sum(len(str(gen)) for gen_list in generations for gen in gen_list)
                    input_tokens = total_tokens // 2  # Rough estimate
                    output_tokens = total_tokens - input_tokens
                    
                    model = getattr(response, 'llm_output', {}).get('model_name', 'langchain-llm')
                    cost_usd = calculate_cost(model, input_tokens, output_tokens)
                    valid = len(generations) > 0 and any(len(gen_list) > 0 for gen_list in generations)
                    
                    logger.log(
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=latency_ms,
                        cost_usd=cost_usd,
                        valid=valid,
                        prompt_id=prompt_id
                    )
        
        # Store handler for later use
        _langchain_handler = GlassboxCallbackHandler()
        
    except ImportError:
        pass  # LangChain not installed - this is expected if library not available


def auto_wrap_all():
    """Auto-wrap all supported AI libraries."""
    wrap_openai()
    wrap_anthropic()
    wrap_langchain()

