"""AG2 (AutoGen) framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class AG2FrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "ag2"
    def create_prompt_callback(self):
        logger.warning("AG2 adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

