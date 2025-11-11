"""
LangChain framework adapter.

This module provides security callback integration for LangChain agents/chains.

Implementation Status: 🚧 In Progress
"""

import logging
from typing import Optional, Callable, Any, Dict, List

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class LangChainFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for LangChain.
    
    Integrates security scanning with LangChain using BaseCallbackHandler.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='langchain',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-langchain-agent-abc123'
        )
        
        # Add to LangChain chain/agent
        chain = LLMChain(
            llm=llm,
            prompt=prompt,
            callbacks=[callback]  # Add security callback
        )
        ```
    """
    
    def get_framework_name(self) -> str:
        return "langchain"
    
    def create_prompt_callback(self):
        """
        Create LangChain BaseCallbackHandler for prompt and response scanning.
        
        Returns:
            LangChain-compatible BaseCallbackHandler instance
        """
        try:
            from langchain.callbacks.base import BaseCallbackHandler
            from langchain.schema import LLMResult
            
            # Import scanner
            from saf3ai_sdk.scanner import scan_prompt, scan_response
            
            adapter_self = self
            
            class Saf3AILangChainCallback(BaseCallbackHandler):
                """LangChain callback handler for Saf3AI security scanning."""
                
                def on_llm_start(
                    self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
                ) -> None:
                    """Scan prompts before sending to LLM."""
                    for prompt in prompts:
                        try:
                            metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                            scan_results = scan_prompt(
                                prompt=prompt,
                                api_endpoint=adapter_self.api_endpoint,
                                api_key=adapter_self.api_key,
                                timeout=adapter_self.timeout,
                                metadata=metadata
                            )
                            
                            # Call user callback if provided
                            if adapter_self.on_scan_complete:
                                should_allow = adapter_self.on_scan_complete(prompt, scan_results, "prompt")
                                if not should_allow:
                                    raise ValueError("Security policy blocked this request")
                        
                        except Exception as e:
                            logger.error(f"LangChain security scan error: {e}")
                            # Fail open by default
                
                def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
                    """Scan LLM responses."""
                    for generation in response.generations:
                        for gen in generation:
                            try:
                                response_text = gen.text
                                metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                                scan_results = scan_response(
                                    response=response_text,
                                    api_endpoint=adapter_self.api_endpoint,
                                    api_key=adapter_self.api_key,
                                    timeout=adapter_self.timeout,
                                    metadata=metadata
                                )
                                
                                # Call user callback if provided
                                if adapter_self.on_scan_complete:
                                    should_allow = adapter_self.on_scan_complete(response_text, scan_results, "response")
                                    if not should_allow:
                                        # Can't block at this point, but log it
                                        logger.warning("LangChain response blocked by security policy")
                            
                            except Exception as e:
                                logger.error(f"LangChain response scan error: {e}")
            
            return Saf3AILangChainCallback()
        
        except ImportError:
            logger.warning("LangChain not installed - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        For LangChain, both prompt and response scanning happen in the same callback handler.
        
        Returns:
            Same as create_prompt_callback()
        """
        return self.create_prompt_callback()

