"""MultiOn framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class MultiOnFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "multion"
    def create_prompt_callback(self):
        logger.warning("MultiOn adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

