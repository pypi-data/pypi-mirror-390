"""LLM Callback hooks for security and compliance scanning."""

import logging
import time
import requests
from typing import Optional, Dict, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from saf3ai_sdk.core.auth import auth_manager, AuthenticationError

logger = logging.getLogger(__name__)


class LLMSecurityCallback:
    """
    Callback handler for LLM prompt scanning.
    
    This class intercepts LLM calls BEFORE they reach the model, scans for threats,
    and invokes a user-provided callback with the scan results.
    """
    
    def __init__(
        self,
        api_endpoint: str,
        api_key: Optional[str] = None,
        timeout: int = 10,
        enabled: bool = True,
        on_scan_complete: Optional[callable] = None
    ):
        """
        Initialize the security callback.
        
        Args:
            api_endpoint: URL of the on-prem scanning API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            enabled: Whether scanning is enabled
            on_scan_complete: Optional callback function(prompt, scan_results) -> bool
                             Should return True to allow the request, False to block it
        """
        self.api_endpoint = api_endpoint.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.enabled = enabled
        self.on_scan_complete = on_scan_complete
        
        logger.info(
            f"LLMSecurityCallback initialized: endpoint={api_endpoint}, "
            f"enabled={enabled}, has_callback={on_scan_complete is not None}"
        )
    
    def scan_prompt(
        self,
        prompt: str,
        model_name: str = "unknown",
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[Dict[str, Any], bool]:
        """
        Scan LLM prompt BEFORE sending to the model.
        
        Calls the on-prem API and invokes the user's callback with results.
        
        Args:
            prompt: The input prompt to scan
            model_name: Name of the LLM model
            conversation_id: Optional conversation ID for tracking
            metadata: Additional metadata to include in the scan
            
        Returns:
            Tuple of (scan_results, should_allow):
                - scan_results: Dict containing threat and category information
                - should_allow: bool indicating if the request should proceed
        """
        if not self.enabled:
            logger.debug("Scanning disabled, skipping")
            return ({"skipped": True, "reason": "scanning_disabled"}, True)
        
        # Get the current span (don't create a new one)
        span = trace.get_current_span()
        
        try:
            start_time = time.time()
            
            # Add security scan attributes to current span
            if span and span.is_recording():
                span.set_attribute("security.scan.enabled", True)
                span.set_attribute("security.scan.prompt_length", len(prompt))
                span.set_attribute("security.scan.model", model_name)
                if conversation_id:
                    span.set_attribute("gen_ai.conversation.id", conversation_id)
            
            # Prepare the request payload
            payload = {
                "prompt": prompt,
                "response": "",  # Empty for prompt-only scan
                "model": model_name,
                "conversation_id": conversation_id,
                "metadata": metadata or {}
            }
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}

            try:
                auth_headers = auth_manager.build_headers(self.api_key)
                headers.update(auth_headers)
            except AuthenticationError as auth_error:
                error_msg = f"Scanning blocked due to authentication failure: {auth_error}"
                logger.error(error_msg)

                if span and span.is_recording():
                    span.set_attribute("security.scan.status", "auth_error")
                    span.set_attribute("security.scan.error", str(auth_error))
                    span.set_status(Status(StatusCode.ERROR, error_msg))

                return (
                    {
                        "status": "auth_error",
                        "error": error_msg,
                        "scan_metadata": {
                            "api_endpoint": self.api_endpoint,
                            "scan_status": "auth_error",
                        },
                    },
                    False,
                )
            
            # Call the on-prem scanning API
            logger.debug(f"Scanning prompt: {len(prompt)} chars")
            if span and span.is_recording():
                span.add_event("security_scan_started", {"prompt_length": len(prompt)})
            
            api_response = requests.post(
                f"{self.api_endpoint}/scan",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            scan_duration = (time.time() - start_time) * 1000  # milliseconds
            
            if span and span.is_recording():
                span.set_attribute("security.scan.duration_ms", scan_duration)
                span.set_attribute("security.scan.api_status", api_response.status_code)
            
            if api_response.status_code == 200:
                scan_results = api_response.json()
                
                # Extract threat information
                threats = scan_results.get("threats", {})
                threat_items = threats.get("items", [])
                max_severity = threats.get("max_severity", "none")
                
                # Extract category information
                categories = scan_results.get("categories", {})
                category_items = categories.get("items", [])
                
                # Add attributes to current span
                if span and span.is_recording():
                    span.set_attribute("security.threats_found", len(threat_items) > 0)
                    span.set_attribute("security.threat_count", len(threat_items))
                    span.set_attribute("security.threat_severity", max_severity)
                    
                    if threat_items:
                        threat_types = [t.get("type") for t in threat_items]
                        span.set_attribute("security.threat_types", ",".join(threat_types))
                    
                    if category_items:
                        top_categories = [c.get("name") for c in category_items[:5]]
                        span.set_attribute("security.categories", ",".join(top_categories))
                        span.set_attribute("security.category_count", len(category_items))
                    
                    span.add_event("security_scan_completed", {
                        "threats": len(threat_items),
                        "categories": len(category_items),
                        "severity": max_severity
                    })
                
                logger.info(
                    f"Scan completed: {len(threat_items)} threats ({max_severity}), "
                    f"{len(category_items)} categories"
                )
                
                # Call user's callback if provided
                should_allow = True
                if self.on_scan_complete:
                    try:
                        # Let the developer decide what to do with the results
                        should_allow = self.on_scan_complete(prompt, scan_results)
                        logger.info(f"User callback returned: allow={should_allow}")
                        
                        if span and span.is_recording():
                            span.set_attribute("security.user_decision", "allow" if should_allow else "block")
                            if not should_allow:
                                span.set_attribute("security.blocked_by", "user_callback")
                    
                    except Exception as callback_error:
                        logger.error(f"Error in user callback: {callback_error}", exc_info=True)
                        # Default to allowing on callback error (fail open)
                        should_allow = True
                        if span and span.is_recording():
                            span.set_attribute("security.callback_error", str(callback_error))
                
                if span and span.is_recording():
                    span.set_attribute("security.scan.status", "completed")
                    span.set_status(Status(StatusCode.OK))
                
                return (scan_results, should_allow)
                
            else:
                # API returned an error
                error_msg = f"Scanning API returned status {api_response.status_code}"
                logger.error(error_msg)
                
                if span and span.is_recording():
                    span.set_attribute("security.scan.status", "error")
                    span.set_attribute("security.scan.error", error_msg)
                    span.set_status(Status(StatusCode.ERROR, error_msg))
                
                # Don't block on API errors (fail open)
                return ({"error": error_msg, "status_code": api_response.status_code}, True)
                
        except requests.exceptions.Timeout:
            error_msg = f"Scanning API timeout after {self.timeout}s"
            logger.error(error_msg)
            
            if span and span.is_recording():
                span.set_attribute("security.scan.status", "timeout")
                span.set_attribute("security.scan.error", error_msg)
            
            # Don't block on timeouts (fail open)
            return ({"error": error_msg, "timeout": True}, True)
        except Exception as e:
            error_msg = f"Scanning error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if span and span.is_recording():
                span.set_attribute("security.scan.status", "exception")
                span.set_attribute("security.scan.error", error_msg)
            
            # Don't block on unexpected errors (fail open)
            return ({"error": error_msg, "exception": str(type(e).__name__)}, True)


class LLMCallbackManager:
    """
    Manager for LLM callbacks.
    
    This class manages security callbacks and provides hooks
    that can be integrated into the ADK agent lifecycle.
    """
    
    def __init__(self):
        """Initialize the callback manager."""
        self.security_callback: Optional[LLMSecurityCallback] = None
        logger.info("LLMCallbackManager initialized")
    
    def register_security_callback(
        self,
        api_endpoint: str,
        api_key: Optional[str] = None,
        timeout: int = 10,
        enabled: bool = True,
        on_scan_complete: Optional[callable] = None
    ) -> LLMSecurityCallback:
        """
        Register a security scanning callback.
        
        Args:
            api_endpoint: URL of the on-prem scanning API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            enabled: Whether scanning is enabled
            on_scan_complete: Optional callback function(prompt, scan_results) -> bool
                             Should return True to allow, False to block
            
        Returns:
            The registered security callback instance
        """
        self.security_callback = LLMSecurityCallback(
            api_endpoint=api_endpoint,
            api_key=api_key,
            timeout=timeout,
            enabled=enabled,
            on_scan_complete=on_scan_complete
        )
        logger.info(f"Security callback registered: {api_endpoint}")
        return self.security_callback
    
    def scan_before_llm(
        self,
        prompt: str,
        model_name: str = "unknown",
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[Dict[str, Any], bool]:
        """
        Hook called BEFORE an LLM call.
        
        Args:
            prompt: The input prompt to scan
            model_name: Name of the LLM model
            conversation_id: Optional conversation ID
            metadata: Additional metadata
            
        Returns:
            Tuple of (scan_results, should_allow)
        """
        if self.security_callback and self.security_callback.enabled:
            try:
                return self.security_callback.scan_prompt(
                    prompt=prompt,
                    model_name=model_name,
                    conversation_id=conversation_id,
                    metadata=metadata
                )
            except Exception as e:
                logger.error(f"Error in security callback: {e}", exc_info=True)
                # Fail open - don't block on errors
                return ({"error": str(e)}, True)
        
        return ({"skipped": True, "reason": "no_callback"}, True)


# Global callback manager instance
_callback_manager: Optional[LLMCallbackManager] = None


def get_callback_manager() -> LLMCallbackManager:
    """Get the global callback manager instance."""
    global _callback_manager
    if _callback_manager is None:
        _callback_manager = LLMCallbackManager()
    return _callback_manager


def register_security_callback(
    api_endpoint: str,
    api_key: Optional[str] = None,
    timeout: int = 10,
    enabled: bool = True,
    on_scan_complete: Optional[callable] = None
) -> LLMSecurityCallback:
    """
    Convenience function to register a security callback.
    
    Args:
        api_endpoint: URL of the on-prem scanning API
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        enabled: Whether scanning is enabled
        on_scan_complete: Optional callback function(prompt, scan_results) -> bool
                         Should return True to allow the request, False to block it
        
    Returns:
        The registered security callback instance
        
    Example:
        ```python
        def my_security_policy(prompt: str, scan_results: dict) -> bool:
            threats = scan_results.get("threats", {})
            max_severity = threats.get("max_severity", "none")
            
            # Block high and critical threats
            if max_severity in ["high", "critical"]:
                print(f"🚫 Blocking prompt due to {max_severity} threat")
                return False
            
            # Allow everything else
            return True
        
        register_security_callback(
            api_endpoint="http://localhost:8080",
            on_scan_complete=my_security_policy
        )
        ```
    """
    manager = get_callback_manager()
    return manager.register_security_callback(
        api_endpoint=api_endpoint,
        api_key=api_key,
        timeout=timeout,
        enabled=enabled,
        on_scan_complete=on_scan_complete
    )
