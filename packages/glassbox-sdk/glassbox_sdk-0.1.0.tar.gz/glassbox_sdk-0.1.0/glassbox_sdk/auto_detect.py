"""
Automatic environment detection.
Detects installed AI libraries, API keys, and project structure.
Makes Glassbox "just work" with zero configuration.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple


def detect_installed_libraries() -> List[str]:
    """
    Detect which AI libraries are installed.
    Returns list of detected library names.
    """
    detected = []
    
    # Check for OpenAI
    try:
        import openai
        detected.append('openai')
    except ImportError:
        pass
    
    # Check for Anthropic
    try:
        import anthropic
        detected.append('anthropic')
    except ImportError:
        pass
    
    # Check for LangChain
    try:
        import langchain
        detected.append('langchain')
    except ImportError:
        pass
    
    # Check for Cohere
    try:
        import cohere
        detected.append('cohere')
    except ImportError:
        pass
    
    # Check for HuggingFace
    try:
        import transformers
        detected.append('huggingface')
    except ImportError:
        pass
    
    return detected


def detect_api_keys() -> Dict[str, bool]:
    """
    Detect available API keys from environment variables.
    Returns dict of provider -> has_key.
    """
    keys = {}
    
    # OpenAI
    keys['openai'] = bool(os.getenv('OPENAI_API_KEY'))
    
    # Anthropic
    keys['anthropic'] = bool(os.getenv('ANTHROPIC_API_KEY'))
    
    # Cohere
    keys['cohere'] = bool(os.getenv('COHERE_API_KEY'))
    
    # HuggingFace
    keys['huggingface'] = bool(os.getenv('HUGGINGFACE_API_KEY'))
    
    # Google AI
    keys['google'] = bool(os.getenv('GOOGLE_AI_API_KEY'))
    
    return keys


def detect_project_type() -> Optional[str]:
    """
    Detect project type (Python package, Jupyter, script, etc.).
    """
    # Check if running in Jupyter
    try:
        if 'ipykernel' in sys.modules:
            return 'jupyter'
    except:
        pass
    
    # Check if running in Colab
    try:
        import google.colab
        return 'colab'
    except ImportError:
        pass
    
    # Check for setup.py or pyproject.toml (Python package)
    if os.path.exists('setup.py') or os.path.exists('pyproject.toml'):
        return 'package'
    
    # Check for requirements.txt (Python project)
    if os.path.exists('requirements.txt'):
        return 'project'
    
    # Default: script
    return 'script'


def get_smart_defaults() -> Dict[str, any]:
    """
    Get smart defaults based on detected environment.
    """
    detected_libs = detect_installed_libraries()
    api_keys = detect_api_keys()
    project_type = detect_project_type()
    
    defaults = {
        'app_id': _get_default_app_id(),
        'sync_enabled': True,
        'auto_wrap': True,
        'environment': os.getenv('GLASSBOX_ENV', 'development'),
    }
    
    # If no API keys detected, enable sandbox mode
    if not any(api_keys.values()):
        defaults['sandbox_mode'] = True
    else:
        defaults['sandbox_mode'] = False
    
    # Auto-detect backend URL if not set
    if not os.getenv('GLASSBOX_BACKEND_URL'):
        defaults['backend_url'] = 'http://localhost:8000'
    
    return defaults


def _get_default_app_id() -> str:
    """
    Get default app_id from project structure.
    """
    # Try to get from directory name
    cwd = os.getcwd()
    dir_name = os.path.basename(cwd)
    
    # Clean up directory name
    app_id = dir_name.lower().replace(' ', '-').replace('_', '-')
    
    # If it's a common name, use a better default
    if app_id in ['', '.', 'home', 'users']:
        app_id = 'my-ai-app'
    
    return app_id


def print_detection_summary():
    """
    Print a friendly summary of what was detected.
    """
    detected_libs = detect_installed_libraries()
    api_keys = detect_api_keys()
    project_type = detect_project_type()
    
    print("🔍 Glassbox Auto-Detection:")
    print(f"   📦 Project type: {project_type}")
    
    if detected_libs:
        print(f"   ✅ Detected libraries: {', '.join(detected_libs)}")
    else:
        print("   ⚠️  No AI libraries detected (will use HTTP interception)")
    
    if any(api_keys.values()):
        found_keys = [k for k, v in api_keys.items() if v]
        print(f"   🔑 API keys found: {', '.join(found_keys)}")
    else:
        print("   💡 No API keys found (sandbox mode enabled)")
    
    print("   ✨ Auto-tracking enabled - you're ready to go!")

