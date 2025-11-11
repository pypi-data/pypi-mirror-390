"""
ADK-native callbacks for security scanning.

This module provides callbacks that integrate with ADK's built-in callback system
instead of monkey-patching. This is the clean, official way to intercept LLM calls.
"""

import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger(__name__)

# Import ADK types
try:
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.models.llm_request import LlmRequest
    from google.adk.models.llm_response import LlmResponse
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logger.warning("ADK not available - callbacks will not work")


def create_security_callback(api_endpoint: str, api_key: Optional[str] = None, 
                            timeout: int = 10, on_scan_complete: Optional[callable] = None,
                            scan_responses: bool = False, agent_identifier: Optional[str] = None):
    """
    Create ADK callbacks that scan prompts and optionally responses for security threats.
    
    This function returns callback(s) that can be passed to LlmAgent's callback parameters.
    
    Args:
        api_endpoint: URL of the on-prem scanning API
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        on_scan_complete: Optional callback function(text, scan_results, text_type) -> bool
                         Should return True to allow, False to block
                         text_type will be "prompt" or "response"
        scan_responses: If True, also returns after_model_callback to scan responses
        agent_identifier: Optional agent identifier for custom guardrails enforcement
    
    Returns:
        If scan_responses=False: A before_model_callback function
        If scan_responses=True: Tuple of (before_model_callback, after_model_callback)
        
    Example:
        ```python
        def my_policy(prompt, scan_results):
            return scan_results["threats"]["max_severity"] not in ["high", "critical"]
        
        callback = create_security_callback(
            api_endpoint="http://localhost:8080",
            on_scan_complete=my_policy
        )
        
        agent = LlmAgent(
            name="my_agent",
            model="gemini-2.5-flash",
            before_model_callback=callback
        )
        ```
    """
    if not ADK_AVAILABLE:
        logger.error("ADK not available - cannot create security callback")
        return None
    
    # Import the security scanner
    try:
        from .scanner import scan_prompt as _scan_prompt
    except ImportError:
        logger.error("scanner module not available")
        return None
    
    def security_callback(*, callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """
        ADK before_model_callback that scans prompts for security threats.
        
        Args:
            callback_context: CallbackContext from ADK
            llm_request: The LLM request about to be sent
        
        Returns:
            None to allow the request, or an LlmResponse to block it
        """
        # Get the current span for telemetry
        # In ADK callbacks, this will be the call_llm span
        span = trace.get_current_span()
        
        # ALSO get the agent span (the one that gets exported)
        # We store a reference to it in the instrumentation
        agent_span = None
        try:
            from saf3ai_sdk.instrumentation.adk_instrumentation import _current_agent_span
            agent_span = getattr(_current_agent_span, 'span', None)
        except:
            pass
        
        # Extract the prompt from the request
        prompt = _extract_prompt_from_request(llm_request)
        if not prompt:
            logger.debug("No prompt found in request, skipping security scan")
            return None
        
        # Get model name
        model_name = getattr(llm_request, 'model', 'unknown')
        
        # Get conversation ID from context or span
        conversation_id = _extract_conversation_id(callback_context, span)
        
        # Add security scan attributes to current span AND agent span
        # The current span might be call_llm, but we also need to add to the agent span
        spans_to_update = []
        if span and span.is_recording():
            spans_to_update.append(span)
        
        # Add the agent span (the one that gets exported to Jaeger/OpenSearch)
        if agent_span and agent_span.is_recording():
            spans_to_update.append(agent_span)
            logger.debug(f"Adding attributes to both call_llm span and agent span")
        
        for target_span in spans_to_update:
            target_span.set_attribute("security.scan.enabled", True)
            target_span.set_attribute("security.scan.prompt_length", len(prompt))
            target_span.set_attribute("security.scan.model", model_name)
            
            # Store the FULL prompt (no truncation)
            # Use BOTH prefixed and non-prefixed attributes for compatibility
            target_span.set_attribute("security.scan.prompt", prompt)  # Full prompt
            target_span.set_attribute("prompt", prompt)  # Full prompt without prefix
            
            # Also extract and store just the user's latest input for UI convenience
            user_input = prompt.split('\n')[0] if prompt else prompt
            target_span.set_attribute("security.scan.user_input", user_input)  # Full user input
            target_span.set_attribute("user_input", user_input)  # Full user input without prefix
            
            if conversation_id:
                target_span.set_attribute("gen_ai.conversation.id", conversation_id)
        
        try:
            if span and span.is_recording():
                span.add_event("security_scan_started", {"prompt_length": len(prompt)})
            
            # Call the scanner function with agent_identifier
            metadata = {"agent_identifier": agent_identifier} if agent_identifier else {}
            scan_results = _scan_prompt(
                prompt=prompt,
                api_endpoint=api_endpoint,
                model_name=model_name,
                conversation_id=conversation_id,
                api_key=api_key,
                timeout=timeout,
                metadata=metadata
            )
            
            # Get scan duration from results
            scan_duration = scan_results.get("scan_metadata", {}).get("duration_ms", 0)
            
            if span and span.is_recording():
                span.set_attribute("security.scan.duration_ms", scan_duration)
                span.set_attribute("security.scan.api_status", 200)
                
            # Extract detection results from raw API response
            detection_results = scan_results.get("detection_results", {})
            
            # Check if any threats were found
            threats_found = []
            for threat_type, result_data in detection_results.items():
                if result_data.get("result") == "MATCH_FOUND":
                    threats_found.append(threat_type)
            
            # Extract categories
            out_of_scope = scan_results.get("OutofScopeAnalysis", {})
            detected_categories = out_of_scope.get("detected_categories", [])
            
            # Add attributes to ALL spans (both call_llm and agent span)
            for target_span in spans_to_update:
                if target_span and target_span.is_recording():
                    target_span.set_attribute("security.threats_found", len(threats_found) > 0)
                    target_span.set_attribute("security.threat_count", len(threats_found))
                    
                    if threats_found:
                        target_span.set_attribute("security.threat_types", ",".join(threats_found))
                    
                    if detected_categories:
                        category_names = [c.get("category", "").split("/")[1] for c in detected_categories[:3] if c.get("category")]
                        if category_names:
                            target_span.set_attribute("security.categories", ",".join(category_names))
                        target_span.set_attribute("security.category_count", len(detected_categories))
                    
                    # Store the complete scan results (Model Armor + NLP combined)
                    import json
                    try:
                        scan_results_json = json.dumps(scan_results)
                        # Store as attribute (truncate if too large for span attributes)
                        if len(scan_results_json) <= 4000:
                            target_span.set_attribute("security.scan.full_results", scan_results_json)
                        else:
                            # If too large, store summary
                            summary = {
                                "detection_results": detection_results,
                                "category_count": len(detected_categories),
                                "top_categories": detected_categories[:3]
                            }
                            target_span.set_attribute("security.scan.full_results", json.dumps(summary))
                    except Exception as e:
                        logger.warning(f"Could not serialize scan results: {e}")
                    
                    target_span.add_event("security_scan_completed", {
                        "threats": len(threats_found),
                        "categories": len(detected_categories)
                    })
            
            logger.info(
                f"Security scan completed: {len(threats_found)} threats, "
                f"{len(detected_categories)} categories"
            )
            
            # Call user's callback if provided
            should_allow = True
            if on_scan_complete:
                try:
                    print(f"\n🔍 Calling user's security policy callback...")
                    print(f"   Prompt: {prompt[:50]}...")
                    print(f"   Scan results keys: {list(scan_results.keys())}")
                    
                    should_allow = on_scan_complete(prompt, scan_results, "prompt")
                    
                    print(f"   User callback returned: allow={should_allow}")
                    logger.info(f"User callback returned: allow={should_allow}")
                    
                    # Add decision to ALL spans (both call_llm and agent span)
                    for target_span in spans_to_update:
                        if target_span and target_span.is_recording():
                            target_span.set_attribute("security.user_decision", "allow" if should_allow else "block")
                            if not should_allow:
                                target_span.set_attribute("security.blocked_by", "user_callback")
                
                except Exception as callback_error:
                    logger.error(f"Error in user callback: {callback_error}", exc_info=True)
                    # Default to allowing on callback error (fail open)
                    should_allow = True
                    if span and span.is_recording():
                        span.set_attribute("security.callback_error", str(callback_error))
            
            if not should_allow:
                # BLOCK THE REQUEST by returning an error response
                # Create a user-friendly error message based on detected threats
                threat_messages = {
                    "CSAM": "inappropriate content involving minors",
                    "Dangerous": "dangerous or harmful content",
                    "HateSpeech": "hate speech or discriminatory content",
                    "Harassment": "harassing or bullying content",
                    "SexualExplicit": "sexually explicit content",
                    "PIandJailbreak": "an attempt to bypass security controls",
                    "MaliciousURIs": "potentially malicious links",
                    "SenstiveData": "sensitive personal information"
                }
                
                # Get friendly descriptions for detected threats
                detected_issues = [threat_messages.get(t, t.lower()) for t in threats_found]
                
                if len(detected_issues) == 1:
                    error_message = (
                        f"I'm sorry, but I cannot assist with this request. "
                        f"The system detected {detected_issues[0]}. "
                        f"This system is not allowed to answer questions of this nature."
                    )
                else:
                    issues_text = ", ".join(detected_issues[:-1]) + f" and {detected_issues[-1]}"
                    error_message = (
                        f"I'm sorry, but I cannot assist with this request. "
                        f"The system detected {issues_text}. "
                        f"This system is not allowed to answer questions of this nature."
                    )
                
                logger.warning(f"User callback blocked LLM call: {error_message}")
                
                if span and span.is_recording():
                    span.set_status(Status(StatusCode.ERROR, "Security violation detected"))
                    span.add_event("security_request_blocked", {
                        "threat_types": ",".join(threats_found)
                    })
                
                # Return an LlmResponse to block the request
                return _create_error_response(error_message)
            
            # Allow the request
            if span and span.is_recording():
                span.set_attribute("security.scan.status", "completed")
                span.set_status(Status(StatusCode.OK))
            
            return None  # None means "proceed with normal LLM call"
        
        except Exception as e:
            error_msg = f"Scanning error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if span and span.is_recording():
                span.set_attribute("security.scan.status", "error")
                span.set_attribute("security.scan.error", error_msg)
            
            # Fail open - allow on errors
            return None
    
    # Create after_model_callback if response scanning is enabled
    if scan_responses:
        def response_security_callback(*, callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
            """
            ADK after_model_callback that scans LLM responses for security threats.
            
            Args:
                callback_context: CallbackContext from ADK
                llm_response: The LLM response that was generated
            
            Returns:
                None to allow the response, or a modified LlmResponse to block it
            """
            # Get the current span
            span = trace.get_current_span()
            
            # Extract response text
            response_text = _extract_response_from_llm_response(llm_response)
            if not response_text:
                logger.debug("No response text found, skipping response scan")
                return None
            
            # Get model name and conversation ID
            model_name = "unknown"
            conversation_id = _extract_conversation_id(callback_context, span)
            
            # Add response scan attributes to current span AND agent span
            # Get the agent span (the one that gets exported)
            agent_span = None
            try:
                from saf3ai_sdk.instrumentation.adk_instrumentation import _current_agent_span
                agent_span = getattr(_current_agent_span, 'span', None)
            except:
                pass
            
            spans_to_update = []
            if span and span.is_recording():
                spans_to_update.append(span)
            
            # Add the agent span
            if agent_span and agent_span.is_recording():
                spans_to_update.append(agent_span)
            
            for target_span in spans_to_update:
                target_span.set_attribute("security.response_scan.enabled", True)
                target_span.set_attribute("security.response_scan.length", len(response_text))
                target_span.set_attribute("security.scan.response", response_text)  # FULL response - no truncation
                target_span.set_attribute("response", response_text)  # FULL response without prefix
            
            try:
                if span and span.is_recording():
                    span.add_event("security_response_scan_started", {"response_length": len(response_text)})
                
                # Scan the response using scanner module
                from .scanner import scan_response as _scan_response
                
                metadata = {"agent_identifier": agent_identifier} if agent_identifier else {}
                scan_results = _scan_response(
                    response=response_text,
                    api_endpoint=api_endpoint,
                    model_name=model_name,
                    conversation_id=conversation_id,
                    api_key=api_key,
                    timeout=timeout,
                    metadata=metadata
                )
                
                # Extract detection results
                detection_results = scan_results.get("detection_results", {})
                threats_found = [k for k, v in detection_results.items() if v.get("result") == "MATCH_FOUND"]
                
                # Add telemetry to ALL spans (both call_llm and agent span)
                for target_span in spans_to_update:
                    if target_span and target_span.is_recording():
                        target_span.set_attribute("security.response_threats_found", len(threats_found) > 0)
                        target_span.set_attribute("security.response_threat_count", len(threats_found))
                        if threats_found:
                            target_span.set_attribute("security.response_threat_types", ",".join(threats_found))
                        
                        # Store the complete response scan results (Model Armor + NLP)
                        import json
                        try:
                            scan_results_json = json.dumps(scan_results)
                            if len(scan_results_json) <= 4000:
                                target_span.set_attribute("security.response_scan.full_results", scan_results_json)
                            else:
                                # If too large, store summary
                                out_of_scope = scan_results.get("OutofScopeAnalysis", {})
                                detected_categories = out_of_scope.get("detected_categories", [])
                                summary = {
                                    "detection_results": detection_results,
                                    "category_count": len(detected_categories),
                                    "top_categories": detected_categories[:3]
                                }
                                target_span.set_attribute("security.response_scan.full_results", json.dumps(summary))
                        except Exception as e:
                            logger.warning(f"Could not serialize response scan results: {e}")
                
                # Call user's callback if provided
                should_allow = True
                if on_scan_complete:
                    try:
                        should_allow = on_scan_complete(response_text, scan_results, "response")
                        logger.info(f"User callback for response: allow={should_allow}")
                        
                        # Add decision to ALL spans
                        for target_span in spans_to_update:
                            if target_span and target_span.is_recording():
                                target_span.set_attribute("security.response_user_decision", "allow" if should_allow else "block")
                    except Exception as e:
                        logger.error(f"Error in response callback: {e}", exc_info=True)
                        should_allow = True  # Fail open
                
                if not should_allow:
                    # Block the response
                    error_message = (
                        f"🚫 Security Violation: The generated response contains security concerns and cannot be shown. "
                        f"Detected: {', '.join(threats_found)}."
                    )
                    logger.warning(f"Response blocked: {error_message}")
                    
                    if span and span.is_recording():
                        span.set_status(Status(StatusCode.ERROR, "Response security violation"))
                    
                    return _create_error_response(error_message)
                
                return None  # Allow the response
            
            except Exception as e:
                logger.error(f"Error scanning response: {e}", exc_info=True)
                return None  # Fail open
        
        return (security_callback, response_security_callback)
    
    return security_callback


def _extract_prompt_from_request(llm_request: LlmRequest) -> str:
    """
    Extract the LATEST USER MESSAGE from an LlmRequest.
    
    ADK sends the full conversation history, but we only want to scan
    the most recent user input.
    """
    try:
        # Try to get contents from the request
        if hasattr(llm_request, 'contents'):
            contents = llm_request.contents
            
            if isinstance(contents, str):
                return contents
            
            elif isinstance(contents, list):
                # ADK sends conversation as list of Content objects
                # Each has a 'role' (user/model) and 'parts' (text content)
                # We want the LAST user message
                
                user_messages = []
                for item in contents:
                    # Check if this is a user message
                    role = getattr(item, 'role', None)
                    
                    if role == 'user':
                        # Extract text from this user message
                        if hasattr(item, 'parts'):
                            for part in item.parts:
                                if hasattr(part, 'text') and part.text:
                                    user_messages.append(part.text)
                        elif hasattr(item, 'text') and item.text:
                            user_messages.append(item.text)
                
                # Return the LAST user message (most recent)
                if user_messages:
                    latest_user_message = user_messages[-1]
                    if latest_user_message:
                        logger.debug(f"Extracted latest user message: {latest_user_message[:50]}...")
                        return latest_user_message
                
                # Fallback: concatenate everything if we can't find role
                prompt_parts = []
                for item in contents:
                    if isinstance(item, str):
                        prompt_parts.append(item)
                    elif hasattr(item, 'text') and item.text:
                        prompt_parts.append(item.text)
                    elif hasattr(item, 'parts'):
                        for part in item.parts:
                            if hasattr(part, 'text') and part.text:
                                prompt_parts.append(part.text)
                
                # Filter out None values before joining
                prompt_parts = [p for p in prompt_parts if p is not None]
                return "\n".join(prompt_parts) if prompt_parts else ""
        
        # Fallback to string representation
        return str(llm_request)
    except Exception as e:
        logger.error(f"Error extracting prompt: {e}", exc_info=True)
        return ""


def _extract_response_from_llm_response(llm_response: LlmResponse) -> str:
    """Extract the response text from an LlmResponse."""
    try:
        if hasattr(llm_response, 'candidates') and llm_response.candidates:
            for candidate in llm_response.candidates:
                if hasattr(candidate, 'content'):
                    content = candidate.content
                    if hasattr(content, 'parts'):
                        text_parts = []
                        for part in content.parts:
                            if hasattr(part, 'text'):
                                text_parts.append(part.text)
                        if text_parts:
                            return "\n".join(text_parts)
        
        # Fallback
        return str(llm_response)
    except Exception as e:
        logger.error(f"Error extracting response: {e}", exc_info=True)
        return ""


def _extract_conversation_id(ctx: CallbackContext, span) -> Optional[str]:
    """Extract conversation ID from context or span."""
    try:
        # Try to get from context session
        if hasattr(ctx, 'session') and hasattr(ctx.session, 'id'):
            return str(ctx.session.id)
        
        # Try to get from span attributes
        if span and span.is_recording():
            conv_id = span.attributes.get('gen_ai.conversation.id')
            if conv_id:
                return str(conv_id)
            
            # Fallback: Use trace_id as conversation_id if session is not available
            # This ensures conversation_id is ALWAYS present for tracking
            span_context = span.get_span_context()
            if span_context and span_context.is_valid:
                trace_id = format(span_context.trace_id, '032x')  # Convert to hex string
                logger.debug(f"No session ID found, using trace_id as conversation_id: {trace_id}")
                return trace_id
    except Exception as e:
        logger.debug(f"Could not extract conversation ID: {e}")
    
    return None


def _create_error_response(error_message: str) -> LlmResponse:
    """Create an LlmResponse containing an error message."""
    try:
        from google.adk.models.llm_response import LlmResponse
        from google.genai import types
        
        # Create a response with the error message
        # LlmResponse has 'content' field, not 'candidates'
        response = LlmResponse(
            content=types.Content(
                parts=[types.Part(text=error_message)],
                role="model"
            ),
            turn_complete=True
        )
        return response
    except Exception as e:
        logger.error(f"Error creating error response: {e}", exc_info=True)
        # If we can't create a proper response, return None (allow the request)
        return None

