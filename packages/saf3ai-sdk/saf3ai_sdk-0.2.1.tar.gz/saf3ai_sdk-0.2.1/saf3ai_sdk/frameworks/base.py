"""
Base framework adapter interface.

All framework-specific adapters should inherit from this base class.
"""

from typing import Optional, Dict, Any, Callable
from abc import ABC, abstractmethod


class BaseFrameworkAdapter(ABC):
    """
    Base class for framework-specific adapters.
    
    Each framework (ADK, LangChain, LlamaIndex) implements this interface
    to provide framework-specific security callback integration.
    """
    
    def __init__(
        self,
        api_endpoint: str,
        agent_identifier: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 10,
        on_scan_complete: Optional[Callable] = None
    ):
        """
        Initialize the framework adapter.
        
        Args:
            api_endpoint: URL of the on-prem scanning API
            agent_identifier: Agent identifier for custom guardrails
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            on_scan_complete: Optional callback function(text, scan_results, text_type) -> bool
        """
        self.api_endpoint = api_endpoint
        self.agent_identifier = agent_identifier
        self.api_key = api_key
        self.timeout = timeout
        self.on_scan_complete = on_scan_complete
    
    @abstractmethod
    def create_prompt_callback(self):
        """
        Create a before-LLM callback for the framework.
        
        Returns:
            Framework-specific callback object/function
        """
        pass
    
    @abstractmethod
    def create_response_callback(self):
        """
        Create an after-LLM callback for the framework.
        
        Returns:
            Framework-specific callback object/function
        """
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the framework name (e.g., 'adk', 'langchain')."""
        pass

