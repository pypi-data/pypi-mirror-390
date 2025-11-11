"""
Template for creating new framework adapters.

Copy this file and rename it to <framework>_adapter.py
Then implement the abstract methods for your framework.

IMPLEMENTATION CHECKLIST:
[ ] Update class name
[ ] Update framework name in get_framework_name()
[ ] Implement create_prompt_callback() for pre-LLM scanning
[ ] Implement create_response_callback() for post-LLM scanning
[ ] Test with actual framework
[ ] Update documentation with usage example
"""

import logging
from typing import Optional, Callable

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class YourFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for [FRAMEWORK_NAME].
    
    Implementation Status: 🚧 Placeholder
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='your-framework',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-agent-abc123'
        )
        
        # Add to your framework's agent/chain
        # (framework-specific integration code here)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "your-framework"  # e.g., 'langchain', 'crewai', etc.
    
    def create_prompt_callback(self):
        """
        Create a callback for prompt scanning (before LLM).
        
        Steps to implement:
        1. Import your framework's callback/hook interface
        2. Create a class/function that implements that interface
        3. In the callback, call scan_prompt() from saf3ai_sdk.scanner
        4. Pass agent_identifier in metadata for custom guardrails
        5. Call self.on_scan_complete() if provided
        6. Return the callback instance
        
        Returns:
            Framework-specific callback object/function
        """
        logger.warning(f"{self.get_framework_name()} adapter not yet implemented")
        
        # TODO: Implement framework-specific callback
        # Example pattern:
        # from saf3ai_sdk.scanner import scan_prompt
        # 
        # def your_framework_callback(prompt, **kwargs):
        #     metadata = {"agent_identifier": self.agent_identifier}
        #     scan_results = scan_prompt(
        #         prompt=prompt,
        #         api_endpoint=self.api_endpoint,
        #         api_key=self.api_key,
        #         timeout=self.timeout,
        #         metadata=metadata
        #     )
        #     
        #     if self.on_scan_complete:
        #         should_allow = self.on_scan_complete(prompt, scan_results, "prompt")
        #         if not should_allow:
        #             # Block the request (framework-specific)
        #             raise ValueError("Security policy blocked request")
        #     
        #     return None  # Allow
        # 
        # return your_framework_callback
        
        return None
    
    def create_response_callback(self):
        """
        Create a callback for response scanning (after LLM).
        
        Similar to create_prompt_callback() but for LLM responses.
        
        Returns:
            Framework-specific callback object/function
        """
        logger.warning(f"{self.get_framework_name()} response scanning not yet implemented")
        
        # TODO: Implement response scanning callback
        # Use scan_response() from saf3ai_sdk.scanner
        
        return None

