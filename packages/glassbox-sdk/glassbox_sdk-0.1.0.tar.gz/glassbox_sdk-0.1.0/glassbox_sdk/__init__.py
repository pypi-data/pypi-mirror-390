"""
Glassbox — See your AI costs in real-time

Codex-style minimal SDK. One line, zero config.

Usage:
    import glassbox
    glassbox.init()  # That's it!

    # Your existing AI code works as-is
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(...)
    # ✅ Automatically tracked!
"""

# Core API (Codex-style: minimal, essential only)
from .logger import init, get_logger, log_call

# Advanced features (available but not in main namespace)
from .logger import GlassboxLogger
from .auto_wrap import auto_wrap_all
from .decorators import track, track_call
from .http_interceptor import intercept_http
from .async_decorators import track_async
from .async_interceptor import intercept_async_http

__version__ = "0.1.0"

# Codex-style: minimal public API
__all__ = [
    "init",        # Main entry point - just works
    "get_logger",  # Get logger instance
    "log_call",    # Manual logging when needed
]

