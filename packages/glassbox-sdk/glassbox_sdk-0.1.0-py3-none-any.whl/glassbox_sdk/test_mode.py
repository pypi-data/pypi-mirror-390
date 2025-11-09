"""
Testing support for Glassbox.
Allows disabling tracking in tests, using mock loggers, etc.
"""

import os
from typing import Optional


class MockLogger:
    """Mock logger for testing. Doesn't actually log anything."""
    
    def __init__(self):
        self.logs = []
    
    def log(self, **kwargs):
        """Mock log method - just stores logs in memory."""
        self.logs.append(kwargs)
    
    def clear(self):
        """Clear stored logs."""
        self.logs = []
    
    def get_logs(self):
        """Get all stored logs."""
        return self.logs


def is_test_mode() -> bool:
    """
    Check if we're in test mode.
    
    Test mode is enabled if:
    - GLASSBOX_TEST_MODE environment variable is set
    - pytest is running
    - unittest is running
    """
    # Check environment variable
    if os.getenv('GLASSBOX_TEST_MODE') == 'true':
        return True
    
    # Check if pytest is running
    try:
        import pytest
        # If pytest is imported, we might be in a test
        # Check if we're actually running pytest
        if 'pytest' in os.environ.get('_', ''):
            return True
    except ImportError:
        pass
    
    # Check if unittest is running
    import sys
    if 'unittest' in sys.modules:
        # Check if we're in a test
        for frame in sys._getframe().f_back.f_back.f_back.f_locals.values():
            if hasattr(frame, '__class__') and 'Test' in frame.__class__.__name__:
                return True
    
    return False


def get_test_logger() -> MockLogger:
    """Get a mock logger for testing."""
    return MockLogger()


def should_disable_tracking() -> bool:
    """
    Check if tracking should be disabled.
    
    Tracking is disabled if:
    - Test mode is enabled
    - GLASSBOX_DISABLE environment variable is set
    """
    if is_test_mode():
        return True
    
    if os.getenv('GLASSBOX_DISABLE') == 'true':
        return True
    
    return False

