"""Haystack framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class HaystackFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "haystack"
    def create_prompt_callback(self):
        logger.warning("Haystack adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

