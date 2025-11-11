"""TaskWeaver framework adapter. Implementation Status: 📋 Placeholder"""
import logging
from .base import BaseFrameworkAdapter
logger = logging.getLogger(__name__)

class TaskWeaverFrameworkAdapter(BaseFrameworkAdapter):
    def get_framework_name(self) -> str:
        return "taskweaver"
    def create_prompt_callback(self):
        logger.warning("TaskWeaver adapter not yet implemented")
        return None
    def create_response_callback(self):
        return None

