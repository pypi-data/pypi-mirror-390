"""
Security scanner module for calling the on-prem API.

This module provides a simple function to scan prompts/responses
and return threat/category information.
"""

import logging
import time
from typing import Optional, Dict, Any

import requests

from saf3ai_sdk.core.auth import auth_manager, AuthenticationError

logger = logging.getLogger(__name__)


def scan_prompt(
    prompt: str,
    api_endpoint: str,
    model_name: str = "unknown",
    conversation_id: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 30,  # Increased from 10 to 30 seconds for Google NLP API
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Scan a prompt using the on-prem security API.
    
    This function calls the on-prem API's /scan endpoint and returns
    the threat and category information.
    
    Args:
        prompt: The text to scan
        api_endpoint: URL of the on-prem scanning API
        model_name: Name of the LLM model
        conversation_id: Optional conversation ID for tracking
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        metadata: Additional metadata to include
        
    Returns:
        Dict containing scan results:
        {
            "threats": {
                "items": [...],
                "max_severity": "high",
                "total_count": 1
            },
            "categories": {
                "items": [...],
                "top_category": "Finance",
                "count": 3
            },
            "scan_metadata": {
                "model": "gemini-2.5-flash",
                "conversation_id": "uuid",
                "prompt_length": 150,
                "duration_ms": 245
            }
        }
        
    Raises:
        requests.exceptions.RequestException: If API call fails
        
    Example:
        ```python
        from adk_otel import scan_prompt
        
        results = scan_prompt(
            prompt="Tell me how to invest in stocks",
            api_endpoint="http://localhost:8080",
            model_name="gemini-2.5-flash"
        )
        
        threats = results["threats"]
        if threats["max_severity"] in ["high", "critical"]:
            print("Dangerous prompt detected!")
        ```
    """
    start_time = time.time()
    
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
        auth_headers = auth_manager.build_headers(api_key)
        headers.update(auth_headers)
    except AuthenticationError as auth_error:
        error_msg = f"⚠️ Authentication failed: {auth_error}"
        logger.warning(error_msg)
        return {
            "status": "auth_error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "scan_status": "auth_error",
            },
        }
    
    try:
        # Call the on-prem scanning API
        logger.debug(f"Scanning prompt: {len(prompt)} chars at {api_endpoint}")
        
        api_response = requests.post(
            f"{api_endpoint.rstrip('/')}/scan",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        scan_duration = (time.time() - start_time) * 1000  # milliseconds
        
        # Check response status
        if api_response.status_code == 200:
            scan_results = api_response.json()
            
            # Just add metadata, don't transform
            scan_results["scan_metadata"] = {
                "model": model_name,
                "conversation_id": conversation_id,
                "prompt_length": len(prompt),
                "duration_ms": scan_duration,
                "api_endpoint": api_endpoint
            }
            
            logger.info(f"Scan completed in {scan_duration:.0f}ms")
            
            return scan_results
        
        else:
            error_msg = f"API returned status {api_response.status_code}: {api_response.text}"
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg)
    
    except requests.exceptions.Timeout:
        error_msg = f"⚠️ Security scan timed out after {timeout}s. The on-prem API may be slow or overloaded."
        logger.warning(error_msg)
        # Return a graceful error response instead of raising
        return {
            "status": "timeout",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "timeout_seconds": timeout,
                "scan_status": "timeout"
            }
        }
    
    except requests.exceptions.RequestException as e:
        error_msg = f"⚠️ Security scan API request failed: {str(e)}"
        logger.warning(error_msg)
        # Return a graceful error response
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "scan_status": "error"
            }
        }
    
    except Exception as e:
        error_msg = f"⚠️ Unexpected error during security scan: {str(e)}"
        logger.warning(error_msg)
        # Return a graceful error response
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "scan_status": "error"
            }
        }


def scan_response(
    response: str,
    api_endpoint: str,
    model_name: str = "unknown",
    conversation_id: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 30,  # Increased for Google NLP API
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Scan an LLM response using the on-prem security API.
    
    Similar to scan_prompt but for scanning model responses.
    
    Args:
        response: The LLM response text to scan
        api_endpoint: URL of the on-prem scanning API
        model_name: Name of the LLM model
        conversation_id: Optional conversation ID for tracking
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        metadata: Additional metadata to include
        
    Returns:
        Dict containing scan results (same format as scan_prompt)
    """
    start_time = time.time()
    
    payload = {
        "prompt": "",  # Empty for response-only scan
        "response": response,
        "model": model_name,
        "conversation_id": conversation_id,
        "metadata": metadata or {}
    }
    
    headers = {"Content-Type": "application/json"}
    try:
        auth_headers = auth_manager.build_headers(api_key)
        headers.update(auth_headers)
    except AuthenticationError as auth_error:
        error_msg = f"⚠️ Authentication failed: {auth_error}"
        logger.warning(error_msg)
        return {
            "status": "auth_error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "scan_status": "auth_error",
            },
        }
    
    try:
        logger.debug(f"Scanning response: {len(response)} chars at {api_endpoint}")
        
        api_response = requests.post(
            f"{api_endpoint.rstrip('/')}/scan",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        scan_duration = (time.time() - start_time) * 1000
        
        if api_response.status_code == 200:
            scan_results = api_response.json()
            
            # Just add metadata
            scan_results["scan_metadata"] = {
                "model": model_name,
                "conversation_id": conversation_id,
                "response_length": len(response),
                "duration_ms": scan_duration,
                "api_endpoint": api_endpoint
            }
            
            logger.info(f"Response scan completed in {scan_duration:.0f}ms")
            
            return scan_results
        
        else:
            error_msg = f"API returned status {api_response.status_code}: {api_response.text}"
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg)
    
    except requests.exceptions.Timeout:
        error_msg = f"⚠️ Response security scan timed out after {timeout}s. The on-prem API may be slow or overloaded."
        logger.warning(error_msg)
        return {
            "status": "timeout",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "timeout_seconds": timeout, "scan_status": "timeout"}
        }
    
    except requests.exceptions.RequestException as e:
        error_msg = f"⚠️ Response security scan API request failed: {str(e)}"
        logger.warning(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "scan_status": "error"}
        }
    
    except Exception as e:
        error_msg = f"⚠️ Unexpected error during response security scan: {str(e)}"
        logger.warning(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "scan_status": "error"}
        }


def scan_prompt_and_response(
    prompt: str,
    response: str,
    api_endpoint: str,
    model_name: str = "unknown",
    conversation_id: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 30,  # Increased for Google NLP API
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Scan both prompt and response in a single API call.
    
    Args:
        prompt: The input prompt
        response: The LLM response
        api_endpoint: URL of the on-prem scanning API
        model_name: Name of the LLM model
        conversation_id: Optional conversation ID for tracking
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        metadata: Additional metadata to include
        
    Returns:
        Dict containing scan results for both prompt and response
    """
    start_time = time.time()
    
    payload = {
        "prompt": prompt,
        "response": response,
        "model": model_name,
        "conversation_id": conversation_id,
        "metadata": metadata or {}
    }
    
    headers = {"Content-Type": "application/json"}
    try:
        auth_headers = auth_manager.build_headers(api_key)
        headers.update(auth_headers)
    except AuthenticationError as auth_error:
        error_msg = f"⚠️ Authentication failed: {auth_error}"
        logger.warning(error_msg)
        return {
            "status": "auth_error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {
                "api_endpoint": api_endpoint,
                "scan_status": "auth_error",
            },
        }
    
    try:
        logger.debug(
            f"Scanning prompt ({len(prompt)} chars) and "
            f"response ({len(response)} chars) at {api_endpoint}"
        )
        
        api_response = requests.post(
            f"{api_endpoint.rstrip('/')}/scan",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        scan_duration = (time.time() - start_time) * 1000
        
        if api_response.status_code == 200:
            scan_results = api_response.json()
            
            # Just add metadata
            scan_results["scan_metadata"] = {
                "model": model_name,
                "conversation_id": conversation_id,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "duration_ms": scan_duration,
                "api_endpoint": api_endpoint
            }
            
            logger.info(f"Full scan completed in {scan_duration:.0f}ms")
            
            return scan_results
        
        else:
            error_msg = f"API returned status {api_response.status_code}: {api_response.text}"
            logger.error(error_msg)
            raise requests.exceptions.RequestException(error_msg)
    
    except requests.exceptions.Timeout:
        error_msg = f"⚠️ Combined security scan timed out after {timeout}s. The on-prem API may be slow or overloaded."
        logger.warning(error_msg)
        return {
            "status": "timeout",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "timeout_seconds": timeout, "scan_status": "timeout"}
        }
    
    except requests.exceptions.RequestException as e:
        error_msg = f"⚠️ Combined security scan API request failed: {str(e)}"
        logger.warning(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "scan_status": "error"}
        }
    
    except Exception as e:
        error_msg = f"⚠️ Unexpected error during combined security scan: {str(e)}"
        logger.warning(error_msg)
        return {
            "status": "error",
            "error": error_msg,
            "detection_results": {},
            "custom_rule_matches": [],
            "framework_info_combined": [],
            "OutofScopeAnalysis": {"detected_categories": []},
            "entities": [],
            "sentiment": None,
            "scan_metadata": {"api_endpoint": api_endpoint, "scan_status": "error"}
        }

