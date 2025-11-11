"""Cohere framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class CohereFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "cohere"
    def create_prompt_callback(self):
        logger.warning("Cohere adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

