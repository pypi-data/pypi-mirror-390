"""AI21 framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class AI21FrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "ai21"
    def create_prompt_callback(self):
        logger.warning("AI21 adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

