"""
Sandbox mode for Glassbox.
Generates demo data so users see the magic moment immediately,
even without real AI calls.
"""

import time
import random
from typing import Optional
from .logger import get_logger
from .utils import generate_prompt_id, get_timestamp


def generate_demo_logs(count: int = 10):
    """
    Generate demo logs so dashboard shows data immediately.
    This creates the "magic moment" for first-time users.
    """
    logger = get_logger()
    if not logger:
        return
    
    models = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku"
    ]
    
    for i in range(count):
        model = random.choice(models)
        input_tokens = random.randint(50, 200)
        output_tokens = random.randint(25, 150)
        latency_ms = random.uniform(100, 800)
        
        # Calculate realistic cost
        if 'gpt-4' in model:
            cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000
        elif 'gpt-3.5' in model:
            cost = (input_tokens * 0.0015 + output_tokens * 0.002) / 1000
        elif 'claude-3-opus' in model:
            cost = (input_tokens * 0.015 + output_tokens * 0.075) / 1000
        elif 'claude-3-sonnet' in model:
            cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000
        else:
            cost = (input_tokens + output_tokens) * 0.002 / 1000
        
        valid = random.random() > 0.1  # 90% valid rate
        
        try:
            logger.log(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                valid=valid,
                prompt_id=generate_prompt_id(),
                timestamp=get_timestamp()
            )
        except Exception:
            # Silently fail - don't break if logging fails
            pass
        
        # Small delay to make timestamps realistic
        time.sleep(0.01)


def enable_sandbox_mode():
    """
    Enable sandbox mode - generates demo data automatically.
    Call this after init() to show immediate results.
    """
    # Generate demo logs in background
    try:
        generate_demo_logs(count=15)
    except Exception:
        # Silently fail
        pass

