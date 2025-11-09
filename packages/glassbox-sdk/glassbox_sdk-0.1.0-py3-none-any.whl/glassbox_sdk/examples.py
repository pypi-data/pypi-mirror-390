"""
Examples showing how to use Glassbox with ANY AI tech stack.
"""

# Example 1: Using decorator with custom AI function
"""
from glassbox_sdk import init, track

@track(model="custom-ai")
def my_custom_ai_call(prompt):
    # Your custom AI API call
    response = custom_api.generate(prompt)
    return response

init()
result = my_custom_ai_call("Hello!")
"""

# Example 2: Using decorator with custom token extraction
"""
from glassbox_sdk import init, track

def extract_my_tokens(response):
    return (response.input_token_count, response.output_token_count)

@track(
    model="my-api",
    extract_tokens=extract_my_tokens,
    extract_model=lambda r: r.model_name
)
def my_ai_function(prompt):
    return my_api.generate(prompt)

init()
result = my_ai_function("Hello!")
"""

# Example 3: Manual logging for full control
"""
from glassbox_sdk import init, log_call

init()

# Your AI call
response = my_custom_api.generate(
    prompt="Hello",
    model="my-model"
)

# Manual logging
log_call(
    model="my-model",
    response=response,
    latency_ms=500  # You measure this
)
"""

# Example 4: HTTP interception (automatic for any HTTP API)
"""
from glassbox_sdk import init, intercept_http
import requests

init()
intercept_http()  # Intercepts all HTTP requests

# Any HTTP-based AI API will be automatically tracked
response = requests.post(
    "https://api.my-ai-provider.com/v1/generate",
    json={"prompt": "Hello"}
)
# Automatically logged!
"""

# Example 5: Context manager for manual tracking
"""
from glassbox_sdk import init, get_logger

init()
logger = get_logger()

with logger.track_call("my-model") as call:
    response = my_ai_api.generate("Hello")
    call.log(response)
"""

# Example 6: Custom AI provider integration
"""
from glassbox_sdk import init, track
import my_custom_ai_library

@track(
    model="custom-provider",
    extract_tokens=lambda r: (r.metadata.input_tokens, r.metadata.output_tokens),
    extract_model=lambda r: r.metadata.model
)
def call_custom_ai(prompt):
    return my_custom_ai_library.generate(prompt)

init()
result = call_custom_ai("Hello!")
"""

