"""OpenAI framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class OpenAIFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "openai"
    def create_prompt_callback(self):
        logger.warning("OpenAI adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

