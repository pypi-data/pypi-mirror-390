"""REST API generic adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class RESTAPIFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "rest"
    def create_prompt_callback(self):
        logger.warning("REST API adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

