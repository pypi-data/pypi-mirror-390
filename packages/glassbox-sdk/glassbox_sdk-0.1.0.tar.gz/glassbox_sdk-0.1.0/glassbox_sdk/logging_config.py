"""
Logging configuration for Glassbox SDK.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[int] = None, enable_debug: bool = False) -> None:
    """
    Set up logging for Glassbox SDK.
    
    Args:
        level: Logging level (default: WARNING for production, INFO for debug)
        enable_debug: Enable debug logging (default: False)
    """
    if level is None:
        level = logging.DEBUG if enable_debug else logging.WARNING
    
    # Create logger
    logger = logging.getLogger('glassbox')
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return
    
    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)


# Initialize logging on import
setup_logging()

