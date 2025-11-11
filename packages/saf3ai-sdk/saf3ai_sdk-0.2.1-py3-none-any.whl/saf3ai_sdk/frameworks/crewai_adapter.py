"""CrewAI framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class CrewAIFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "crewai"
    def create_prompt_callback(self):
        logger.warning("CrewAI adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

