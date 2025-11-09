"""
Environment separation support.
Allows separating logs by environment (dev, staging, prod).
"""

import os
from typing import Optional


def get_environment() -> str:
    """
    Get current environment from environment variable.
    Defaults to 'development' if not set.
    
    Usage:
        # Set environment variable
        export GLASSBOX_ENV=production
        
        # Or in code
        os.environ['GLASSBOX_ENV'] = 'staging'
    """
    return os.getenv('GLASSBOX_ENV', 'development')


def get_app_id_with_env(app_id: str, environment: Optional[str] = None) -> str:
    """
    Get app_id with environment suffix.
    
    Args:
        app_id: Base app ID
        environment: Optional environment override (defaults to GLASSBOX_ENV)
    
    Returns:
        app_id with environment suffix (e.g., "my-app-production")
    """
    env = environment or get_environment()
    
    # Don't add suffix for development
    if env == 'development' or env == 'dev':
        return app_id
    
    return f"{app_id}-{env}"


def get_database_path_with_env(base_path: str = ".glassbox.db", environment: Optional[str] = None) -> str:
    """
    Get database path with environment suffix.
    
    Args:
        base_path: Base database path
        environment: Optional environment override
    
    Returns:
        Database path with environment suffix (e.g., ".glassbox-production.db")
    """
    env = environment or get_environment()
    
    # Don't add suffix for development
    if env == 'development' or env == 'dev':
        return base_path
    
    # Add environment to filename
    if base_path.endswith('.db'):
        return base_path.replace('.db', f'-{env}.db')
    else:
        return f"{base_path}-{env}"

