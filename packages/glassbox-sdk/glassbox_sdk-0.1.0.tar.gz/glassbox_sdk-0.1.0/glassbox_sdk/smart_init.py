"""
Smart initialization with zero-friction, Codex-style onboarding.
Auto-detects context, auto-configures, auto-verifies.
"""

import os
import sys
import subprocess
from typing import Dict, Optional, Tuple
from .auto_detect import (
    detect_installed_libraries,
    detect_api_keys,
    detect_project_type,
    get_smart_defaults
)
from .serverless import (
    detect_serverless_platform,
    get_serverless_config,
    detect_vercel_project_structure,
    generate_serverless_integration_code,
    create_vercel_env_file,
    get_serverless_integration_instructions
)


def detect_web_app() -> bool:
    """Detect if this is a web application."""
    # Check for common web framework files
    web_indicators = [
        'app.py', 'main.py', 'server.py', 'wsgi.py', 'asgi.py',
        'package.json', 'requirements.txt', 'Pipfile',
        'flask', 'django', 'fastapi', 'express', 'next'
    ]
    
    files = os.listdir('.')
    for indicator in web_indicators:
        if any(indicator in f.lower() for f in files):
            return True
    
    # Check for web framework imports
    try:
        import flask
        return True
    except:
        pass
    
    try:
        import django
        return True
    except:
        pass
    
    try:
        import fastapi
        return True
    except:
        pass
    
    return False


def detect_frontend_ai_calls() -> bool:
    """Detect if AI calls might happen in frontend."""
    # Check for frontend files
    frontend_indicators = [
        'index.html', 'app.html', 'index.js', 'app.js',
        'src/', 'public/', 'static/', 'templates/'
    ]
    
    files = os.listdir('.')
    for indicator in frontend_indicators:
        if any(indicator in f.lower() for f in files):
            return True
    
    return False


def suggest_best_integration(context: Dict) -> str:
    """
    Suggest best integration method based on detected context.
    Returns: 'backend_sdk', 'frontend_js', 'hybrid', 'proxy', 'sdk', or 'serverless'
    """
    # Serverless gets special handling
    if context.get('is_serverless'):
        if context.get('has_frontend'):
            return 'serverless_hybrid'  # Both serverless backend and frontend
        else:
            return 'serverless'  # Serverless backend only
    
    is_web_app = context.get('is_web_app', False)
    has_frontend = context.get('has_frontend', False)
    project_type = context.get('project_type', 'script')
    
    if is_web_app and has_frontend:
        return 'hybrid'  # Both backend SDK and frontend JS
    elif is_web_app:
        return 'backend_sdk'  # Web app with backend only
    elif project_type in ['jupyter', 'colab', 'notebook']:
        return 'sdk'  # SDK for notebooks
    elif project_type == 'script':
        return 'sdk'  # SDK for scripts
    else:
        return 'proxy'  # Fallback to proxy


def auto_configure_integration(method: str, app_id: str, backend_url: str, context: Optional[Dict] = None) -> Dict:
    """
    Auto-configure integration based on method.
    Returns configuration and code snippets.
    """
    config = {
        'method': method,
        'app_id': app_id,
        'backend_url': backend_url,
        'code_snippet': None,
        'instructions': [],
        'env_vars': [],
        'files_to_create': []
    }
    
    # Serverless-specific configuration
    if method == 'serverless' or method == 'serverless_hybrid':
        platform = context.get('serverless_platform') if context else None
        framework = context.get('framework', 'unknown') if context else 'unknown'
        
        if platform == 'vercel':
            # Generate Vercel-specific code
            vercel_structure = context.get('vercel_structure', {}) if context else {}
            snippets = generate_serverless_integration_code(framework, app_id, backend_url)
            
            if framework == 'nextjs':
                if vercel_structure.get('has_app'):
                    config['code_snippet'] = snippets.get('app_router', '')
                    config['instructions'] = [
                        "Add to app/layout.tsx (or app/layout.js)",
                        "This initializes Glassbox for all pages"
                    ]
                elif vercel_structure.get('has_pages'):
                    config['code_snippet'] = snippets.get('pages_router', '')
                    config['instructions'] = [
                        "Add to pages/_app.js (or pages/_app.tsx)",
                        "This initializes Glassbox for all pages"
                    ]
                
                # Also show API route example
                config['api_snippet'] = snippets.get('api_route', '')
            elif framework == 'python':
                config['code_snippet'] = snippets.get('python_function', '')
                config['instructions'] = [
                    "Add to your api/ function file",
                    "Initialize at module level (reused across invocations)"
                ]
            
            # Environment variables
            config['env_vars'] = [
                f"GLASSBOX_APP_ID={app_id}",
                f"GLASSBOX_BACKEND_URL={backend_url}"
            ]
            
            # Create .env.local file
            if create_vercel_env_file(app_id, backend_url):
                config['files_to_create'] = ['.env.local']
                config['instructions'].extend([
                    "",
                    "✅ Created .env.local with Glassbox config",
                    "Add these to Vercel: https://vercel.com/[project]/settings/environment-variables"
                ])
            
            # Get detailed instructions
            detailed_instructions = get_serverless_integration_instructions(platform, framework, app_id, backend_url)
            config['detailed_instructions'] = detailed_instructions
            
        else:
            # Generic serverless
            config['code_snippet'] = f"""import glassbox
import os

# Initialize (module-level, reused across invocations)
glassbox.init(
    app_id=os.getenv('GLASSBOX_APP_ID', '{app_id}'),
    backend_url=os.getenv('GLASSBOX_BACKEND_URL', '{backend_url}'),
    sync_enabled=True,  # Always sync in serverless
    use_local_db=False  # No local DB in serverless
)"""
            config['instructions'] = [
                "Add to your serverless function",
                "Initialize at module level (reused across invocations)"
            ]
            config['env_vars'] = [
                f"GLASSBOX_APP_ID={app_id}",
                f"GLASSBOX_BACKEND_URL={backend_url}"
            ]
    
    elif method == 'backend_sdk' or method == 'sdk':
        config['code_snippet'] = f"""import glassbox
glassbox.init(app_id="{app_id}", backend_url="{backend_url}")"""
        config['instructions'] = [
            "Add this to your main application file:",
            "  - Flask: Add to app.py or __init__.py",
            "  - Django: Add to settings.py or wsgi.py",
            "  - FastAPI: Add to main.py",
            "  - Script: Add at the top of your script"
        ]
    elif method == 'frontend_js':
        config['code_snippet'] = f"""<script src="https://cdn.glassbox.ai/sdk.js"></script>
<script>
  Glassbox.init({{
    appId: '{app_id}',
    proxyUrl: '{backend_url}/proxy'
  }});
</script>"""
        config['instructions'] = [
            "Add this to your HTML:",
            "  - Before closing </head> tag, or",
            "  - Before closing </body> tag"
        ]
    elif method == 'hybrid':
        config['code_snippet'] = f"""# Backend (Python)
import glassbox
glassbox.init(app_id="{app_id}", backend_url="{backend_url}")

# Frontend (HTML)
<script src="https://cdn.glassbox.ai/sdk.js"></script>
<script>
  Glassbox.init({{appId: '{app_id}', proxyUrl: '{backend_url}/proxy'}});
</script>"""
        config['instructions'] = [
            "Add backend code to your Python app",
            "Add frontend code to your HTML"
        ]
    elif method == 'proxy':
        config['code_snippet'] = f"""# Start proxy
glassbox proxy --auto-configure

# Or set environment variables
export HTTP_PROXY={backend_url}/proxy
export HTTPS_PROXY={backend_url}/proxy"""
        config['instructions'] = [
            "Start the proxy server",
            "Set environment variables in your app"
        ]
    
    return config


def auto_verify_setup(app_id: str, backend_url: str) -> Tuple[bool, str]:
    """
    Auto-verify that setup is working.
    Returns (success, message)
    """
    try:
        # Check if database exists
        if not os.path.exists('.glassbox.db'):
            return False, "Database not created"
        
        # Check if logger is initialized
        try:
            from .logger import get_logger
            logger = get_logger()
            if logger:
                # Database exists and logger is initialized
                return True, "Setup verified successfully"
            else:
                return False, "Logger not initialized"
        except Exception as e:
            return False, f"Verification failed: {str(e)}"
        
    except Exception as e:
        return False, f"Verification error: {str(e)}"


def get_smart_init_context() -> Dict:
    """
    Get complete context for smart initialization.
    """
    defaults = get_smart_defaults()
    detected_libs = detect_installed_libraries()
    api_keys = detect_api_keys()
    project_type = detect_project_type()
    is_web_app = detect_web_app()
    has_frontend = detect_frontend_ai_calls()
    
    # Detect serverless platform
    serverless_platform = detect_serverless_platform()
    serverless_config = get_serverless_config() if serverless_platform else None
    
    context = {
        'app_id': defaults.get('app_id', 'my-app'),
        'backend_url': defaults.get('backend_url', 'http://localhost:8000'),
        'detected_libs': detected_libs,
        'api_keys': api_keys,
        'project_type': project_type,
        'is_web_app': is_web_app,
        'has_frontend': has_frontend,
        'has_api_keys': any(api_keys.values()),
        'sandbox_mode': not any(api_keys.values()),
        'is_serverless': serverless_platform is not None,
        'serverless_platform': serverless_platform,
        'serverless_config': serverless_config
    }
    
    # Override defaults for serverless
    if serverless_platform:
        context['backend_url'] = serverless_config.get('backend_url', 'https://api.glassbox.ai')
        context['use_local_db'] = False  # Serverless can't use local SQLite
        context['sync_enabled'] = True  # Always sync in serverless
    
    # Detect Vercel project structure if on Vercel
    if serverless_platform == 'vercel':
        vercel_structure = detect_vercel_project_structure()
        context['vercel_structure'] = vercel_structure
        context['framework'] = vercel_structure.get('framework', 'unknown')
    
    # Suggest best integration method
    context['best_method'] = suggest_best_integration(context)
    
    return context

