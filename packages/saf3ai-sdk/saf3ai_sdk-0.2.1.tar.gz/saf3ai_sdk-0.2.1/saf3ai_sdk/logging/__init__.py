"""Logging configuration for Saf3AI SDK."""

import logging
import sys
from typing import Union

# Create logger
logger = logging.getLogger("saf3ai_sdk")

def setup_logging(level: Union[str, int] = "INFO") -> None:
    """Setup logging for Saf3AI SDK."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    logger.setLevel(level)
    
    # Create console handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.debug("Saf3AI SDK logging initialized")

__all__ = ["logger", "setup_logging"]
