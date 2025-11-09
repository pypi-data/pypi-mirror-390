"""
Serverless/Vercel-specific optimizations for zero-friction onboarding.
Handles edge functions, environment detection, and auto-configuration.
"""

import os
import json
from typing import Dict, Optional, List
from pathlib import Path


def detect_vercel_environment() -> bool:
    """Detect if running in Vercel environment."""
    return bool(os.getenv('VERCEL') or os.getenv('VERCEL_ENV'))


def detect_serverless_platform() -> Optional[str]:
    """Detect which serverless platform we're on."""
    if os.getenv('VERCEL'):
        return 'vercel'
    elif os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        return 'aws_lambda'
    elif os.getenv('FUNCTION_NAME'):  # Google Cloud Functions
        return 'gcp_functions'
    elif os.getenv('WEBSITE_SITE_NAME'):  # Azure Functions
        return 'azure_functions'
    elif os.getenv('FLY_APP_NAME'):
        return 'flyio'
    elif os.getenv('RENDER'):
        return 'render'
    else:
        return None


def get_serverless_config() -> Dict:
    """Get serverless-specific configuration."""
    platform = detect_serverless_platform()
    
    config = {
        'platform': platform,
        'is_serverless': platform is not None,
        'use_local_db': False,  # Serverless can't use local SQLite
        'backend_url': os.getenv('GLASSBOX_BACKEND_URL', 'https://api.glassbox.ai'),
        'sync_enabled': True,  # Always sync in serverless
        'edge_compatible': platform == 'vercel'  # Vercel has edge functions
    }
    
    # Vercel-specific optimizations
    if platform == 'vercel':
        config['edge_runtime'] = os.getenv('VERCEL_REGION') is not None
        config['env_file'] = '.env.local'  # Vercel uses .env.local
        config['config_file'] = 'vercel.json'
    
    return config


def generate_vercel_env_template() -> str:
    """Generate Vercel environment variables template."""
    return """# Glassbox Configuration
GLASSBOX_BACKEND_URL=https://api.glassbox.ai
GLASSBOX_APP_ID=your-app-id
GLASSBOX_API_KEY=your-api-key  # Optional
"""


def generate_vercel_json_config() -> Dict:
    """Generate vercel.json configuration for Glassbox."""
    return {
        "env": {
            "GLASSBOX_BACKEND_URL": "@glassbox_backend_url",
            "GLASSBOX_APP_ID": "@glassbox_app_id"
        },
        "functions": {
            "api/**/*.py": {
                "runtime": "python3.9"
            }
        }
    }


def detect_vercel_project_structure() -> Dict:
    """Detect Vercel project structure and suggest integration points."""
    structure = {
        'has_api': False,
        'has_pages': False,
        'has_app': False,
        'has_middleware': False,
        'framework': None,
        'integration_points': []
    }
    
    # Check for Next.js
    if Path('next.config.js').exists() or Path('next.config.ts').exists():
        structure['framework'] = 'nextjs'
        structure['has_pages'] = Path('pages').exists()
        structure['has_app'] = Path('app').exists()
        structure['has_api'] = Path('pages/api').exists() or Path('app/api').exists()
        structure['has_middleware'] = Path('middleware.js').exists() or Path('middleware.ts').exists()
        
        if structure['has_app']:
            structure['integration_points'].append('app/layout.tsx (or app/layout.js)')
        elif structure['has_pages']:
            structure['integration_points'].append('pages/_app.js (or pages/_app.tsx)')
        
        if structure['has_api']:
            structure['integration_points'].append('API routes (pages/api or app/api)')
    
    # Check for other frameworks
    elif Path('package.json').exists():
        with open('package.json', 'r') as f:
            pkg = json.load(f)
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            if 'next' in deps:
                structure['framework'] = 'nextjs'
            elif 'sveltekit' in deps:
                structure['framework'] = 'sveltekit'
            elif 'remix' in deps:
                structure['framework'] = 'remix'
            elif 'nuxt' in deps:
                structure['framework'] = 'nuxt'
    
    # Check for Python serverless (Vercel Python)
    if Path('api').exists() or Path('functions').exists():
        structure['has_api'] = True
        if Path('api').exists():
            structure['integration_points'].append('api/ directory (Python functions)')
        if Path('functions').exists():
            structure['integration_points'].append('functions/ directory')
    
    return structure


def generate_serverless_integration_code(framework: str, app_id: str, backend_url: str) -> Dict:
    """Generate integration code for serverless framework."""
    code_snippets = {}
    
    if framework == 'nextjs':
        # Next.js App Router
        code_snippets['app_router'] = f"""// app/layout.tsx (or app/layout.js)
import {{ useEffect }} from 'react';

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  useEffect(() => {{
    // Initialize Glassbox
    if (typeof window !== 'undefined') {{
      import('glassbox-sdk').then(({{ init }}) => {{
        init({{
          appId: process.env.NEXT_PUBLIC_GLASSBOX_APP_ID || '{app_id}',
          backendUrl: process.env.NEXT_PUBLIC_GLASSBOX_BACKEND_URL || '{backend_url}',
        }});
      }});
    }}
  }}, []);

  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}"""
        
        # Next.js Pages Router
        code_snippets['pages_router'] = f"""// pages/_app.js
import {{ useEffect }} from 'react';

export default function App({{ Component, pageProps }}) {{
  useEffect(() => {{
    // Initialize Glassbox
    if (typeof window !== 'undefined') {{
      import('glassbox-sdk').then(({{ init }}) => {{
        init({{
          appId: process.env.NEXT_PUBLIC_GLASSBOX_APP_ID || '{app_id}',
          backendUrl: process.env.NEXT_PUBLIC_GLASSBOX_BACKEND_URL || '{backend_url}',
        }});
      }});
    }}
  }}, []);

  return <Component {{...pageProps}} />;
}}"""
        
        # Next.js API Route
        code_snippets['api_route'] = f"""// pages/api/example.js (or app/api/example/route.js)
import glassbox from 'glassbox-sdk';

// Initialize once (serverless functions reuse)
if (!global.glassboxInitialized) {{
  glassbox.init({{
    appId: process.env.GLASSBOX_APP_ID || '{app_id}',
    backendUrl: process.env.GLASSBOX_BACKEND_URL || '{backend_url}',
  }});
  global.glassboxInitialized = true;
}}

export default async function handler(req, res) {{
  // Your AI code here
  // Glassbox automatically tracks AI calls
  res.json({{ message: 'Hello' }});
}}"""
    
    elif framework == 'python':
        # Python serverless function
        code_snippets['python_function'] = f"""# api/example.py
import glassbox

# Initialize once (module-level, reused across invocations)
glassbox.init(
    app_id=os.getenv('GLASSBOX_APP_ID', '{app_id}'),
    backend_url=os.getenv('GLASSBOX_BACKEND_URL', '{backend_url}'),
    sync_enabled=True,  # Always sync in serverless
    use_local_db=False  # No local DB in serverless
)

def handler(request):
    # Your AI code here
    # Glassbox automatically tracks AI calls
    return {{'message': 'Hello'}}"""
    
    return code_snippets


def create_vercel_env_file(app_id: str, backend_url: str) -> bool:
    """Create .env.local file for Vercel with Glassbox config."""
    env_file = Path('.env.local')
    env_content = f"""# Glassbox Configuration
# Add these to your Vercel project settings: https://vercel.com/[your-project]/settings/environment-variables

GLASSBOX_BACKEND_URL={backend_url}
GLASSBOX_APP_ID={app_id}
# GLASSBOX_API_KEY=your-api-key  # Optional
"""
    
    try:
        # Check if file exists
        if env_file.exists():
            # Append if not already present
            existing = env_file.read_text()
            if 'GLASSBOX' not in existing:
                env_file.write_text(existing + '\n' + env_content)
        else:
            env_file.write_text(env_content)
        
        return True
    except Exception:
        return False


def get_serverless_integration_instructions(platform: str, framework: str, app_id: str, backend_url: str) -> List[str]:
    """Get step-by-step instructions for serverless integration."""
    instructions = []
    
    if platform == 'vercel':
        instructions.append("1. Add environment variables to Vercel:")
        instructions.append("   - Go to: https://vercel.com/[your-project]/settings/environment-variables")
        instructions.append(f"   - Add: GLASSBOX_APP_ID = {app_id}")
        instructions.append(f"   - Add: GLASSBOX_BACKEND_URL = {backend_url}")
        instructions.append("")
        
        if framework == 'nextjs':
            instructions.append("2. Add Glassbox to your Next.js app:")
            instructions.append("   - Copy the code snippet shown above")
            instructions.append("   - Add to app/layout.tsx (App Router) or pages/_app.js (Pages Router)")
            instructions.append("")
        elif framework == 'python':
            instructions.append("2. Add Glassbox to your Python function:")
            instructions.append("   - Copy the code snippet shown above")
            instructions.append("   - Add to your api/ function file")
            instructions.append("")
        
        instructions.append("3. Deploy to Vercel:")
        instructions.append("   - git push (auto-deploys)")
        instructions.append("   - Or: vercel --prod")
        instructions.append("")
        instructions.append("4. View metrics:")
        instructions.append("   - glassbox live (from your local machine)")
        instructions.append("   - Or: https://api.glassbox.ai/dashboard")
    
    return instructions

