"""
LlamaIndex framework adapter.

Implementation Status: 📋 Placeholder
"""

import logging
from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)

class LlamaIndexFrameworkAdapter(BaseFrameworkAdapter):
    """Framework adapter for LlamaIndex."""
    
    def get_framework_name(self) -> str:
        return "llamaindex"
    
    def create_prompt_callback(self):
        logger.warning("LlamaIndex adapter not yet implemented")
        return None
    
    def create_response_callback(self):
        logger.warning("LlamaIndex response scanning not yet implemented")
        return None

