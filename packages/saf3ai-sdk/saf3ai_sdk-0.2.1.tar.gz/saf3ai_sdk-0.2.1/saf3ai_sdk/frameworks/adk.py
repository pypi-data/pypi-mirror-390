"""
Google ADK (Agent Development Kit) framework adapter.

This module provides security callback integration for Google ADK agents.
"""

import logging
from typing import Optional, Callable

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class ADKFrameworkAdapter(BaseFrameworkAdapter):
    """Framework adapter for Google ADK."""
    
    def get_framework_name(self) -> str:
        return "adk"
    
    def create_prompt_callback(self):
        """
        Create ADK before_model_callback for prompt scanning.
        
        Returns:
            ADK-compatible before_model_callback function
        """
        # Import ADK-specific callback creator
        from saf3ai_sdk.adk_callbacks import create_security_callback
        
        callbacks = create_security_callback(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            timeout=self.timeout,
            on_scan_complete=self.on_scan_complete,
            scan_responses=False,
            agent_identifier=self.agent_identifier
        )
        
        return callbacks  # Returns just the before_callback
    
    def create_response_callback(self):
        """
        Create ADK after_model_callback for response scanning.
        
        Returns:
            ADK-compatible after_model_callback function
        """
        # Import ADK-specific callback creator
        from saf3ai_sdk.adk_callbacks import create_security_callback
        
        callbacks = create_security_callback(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            timeout=self.timeout,
            on_scan_complete=self.on_scan_complete,
            scan_responses=True,
            agent_identifier=self.agent_identifier
        )
        
        # Returns tuple of (before, after), we want the after callback
        if isinstance(callbacks, tuple):
            return callbacks[1]
        return None
    
    def create_callbacks(self, scan_responses: bool = False):
        """
        Convenience method to create both callbacks at once.
        
        Args:
            scan_responses: Whether to also create response scanning callback
            
        Returns:
            If scan_responses=False: before_model_callback
            If scan_responses=True: (before_model_callback, after_model_callback)
        """
        from saf3ai_sdk.adk_callbacks import create_security_callback
        
        return create_security_callback(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key,
            timeout=self.timeout,
            on_scan_complete=self.on_scan_complete,
            scan_responses=scan_responses,
            agent_identifier=self.agent_identifier
        )


# Register this adapter
from . import register_framework_adapter
register_framework_adapter('adk', ADKFrameworkAdapter)
register_framework_adapter('google-adk', ADKFrameworkAdapter)

