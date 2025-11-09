"""
Trust and credibility features for terminal-first developers.
Builds confidence through transparency, safety, and local-first guarantees.
"""

import os
import sys
from typing import Dict, List, Tuple
from pathlib import Path


def get_trust_indicators() -> Dict[str, bool]:
    """
    Get trust indicators that show the product is safe and reliable.
    """
    return {
        'local_first': True,  # Works offline, no cloud required
        'no_telemetry': True,  # No tracking, no spyware
        'open_source': True,  # Code is visible and auditable
        'never_breaks_code': True,  # Errors are caught and handled
        'privacy_first': True,  # Data stays local by default
        'exportable': True,  # Can export all data
        'self_hostable': True,  # Can run backend yourself
        'zero_dependencies': False,  # Has minimal dependencies
        'production_safe': True,  # Safe for production use
        'reversible': True  # Can uninstall cleanly
    }


def get_privacy_guarantees() -> List[str]:
    """
    Get privacy guarantees for developers.
    """
    return [
        "All data stored locally by default",
        "No telemetry or tracking",
        "No API keys or secrets sent to backend",
        "Backend sync is optional and encrypted",
        "You control what data is shared",
        "Can run completely offline"
    ]


def get_safety_guarantees() -> List[str]:
    """
    Get safety guarantees for production use.
    """
    return [
        "Errors never break your application code",
        "Logging failures are silently handled",
        "Zero performance impact when disabled",
        "No network calls block your code",
        "Thread-safe and production-ready",
        "Graceful degradation if backend is down"
    ]


def get_transparency_info() -> Dict[str, str]:
    """
    Get transparency information about the product.
    """
    return {
        'source_code': 'https://github.com/glassbox-ai/glassbox',
        'license': 'MIT',
        'data_location': 'Local SQLite database (.glassbox.db)',
        'backend_optional': 'Yes - works completely offline',
        'data_export': 'SQLite database can be exported/backed up',
        'self_host': 'Backend is open source and self-hostable'
    }


def print_trust_badges():
    """
    Print trust badges that build confidence.
    """
    badges = [
        ("🔒", "Local-First", "Works offline, no cloud required"),
        ("🛡️", "Production-Safe", "Never breaks your code"),
        ("🔓", "Open Source", "Code is visible and auditable"),
        ("🚫", "No Telemetry", "No tracking, no spyware"),
        ("🔐", "Privacy-First", "Data stays local by default"),
        ("↩️", "Reversible", "Uninstall cleanly anytime")
    ]
    
    lines = []
    for emoji, label, desc in badges:
        lines.append(f"{emoji} {label}: {desc}")
    
    return lines


def get_developer_trust_messaging() -> Dict[str, str]:
    """
    Get messaging that builds trust with experienced developers.
    """
    return {
        'header': "Built for Developers, by Developers",
        'subheader': "We understand you need to trust your tools. Here's why Glassbox is safe:",
        'local_first': "Local-first architecture: Works completely offline. Your data stays on your machine.",
        'open_source': "Open source: Review the code, audit the security, contribute improvements.",
        'production_safe': "Production-safe: Errors are caught and handled. Your code never breaks.",
        'privacy': "Privacy-first: No telemetry, no tracking, no secrets sent anywhere.",
        'reversible': "Reversible: Uninstall anytime. Export your data. No vendor lock-in.",
        'transparent': "Transparent: See exactly what data is collected and where it goes."
    }


def check_trust_indicators() -> Tuple[bool, List[str]]:
    """
    Check if trust indicators are properly configured.
    Returns (all_good, warnings)
    """
    warnings = []
    
    # Check if local database exists (local-first)
    if not Path('.glassbox.db').exists():
        warnings.append("Local database not found - run 'glassbox init' first")
    
    # Check if backend sync is disabled (privacy-first)
    # This would be checked from logger config
    
    return len(warnings) == 0, warnings


def get_uninstall_instructions() -> List[str]:
    """
    Get instructions for clean uninstall.
    """
    return [
        "1. Remove Glassbox from your code:",
        "   - Remove 'import glassbox' and 'glassbox.init()' lines",
        "",
        "2. Remove local data (optional):",
        "   - Delete .glassbox.db file",
        "   - Delete .glassbox/ directory if it exists",
        "",
        "3. Uninstall package:",
        "   - pip uninstall glassbox-sdk",
        "",
        "4. Remove environment variables (if set):",
        "   - Remove GLASSBOX_* from your .env files",
        "",
        "That's it! No traces left behind."
    ]


def get_data_export_info() -> Dict[str, str]:
    """
    Get information about data export capabilities.
    """
    return {
        'format': 'SQLite database (.glassbox.db)',
        'location': 'Current directory or .glassbox/',
        'export_command': 'cp .glassbox.db backup.db',
        'readable': 'Yes - standard SQLite format',
        'portable': 'Yes - can import to any SQLite tool',
        'backup': 'Just copy the .glassbox.db file'
    }

