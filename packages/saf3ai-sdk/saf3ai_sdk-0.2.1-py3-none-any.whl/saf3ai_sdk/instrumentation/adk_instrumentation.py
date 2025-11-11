"""
Auto-instrumentation for Google ADK agents and LLMs.
This version programmatically patches all key ADK classes to ensure a single,
unified trace, replicating the AgentOps strategy for saf3ai_sdk.

*** FINAL VERSION WITH ROBUST CONTEXT REPAIR ***
"""

import functools
import json
import asyncio
from opentelemetry import trace, context
from opentelemetry.trace import SpanContext, TraceFlags, NonRecordingSpan, Status, StatusCode
from opentelemetry import context as context_api
import uuid
import random
import threading

from saf3ai_sdk.logging import logger
from saf3ai_sdk.core.tracer import tracer as saf3ai_tracer_core
from saf3ai_sdk.core.tracer import TraceContext

# --- ADD Global Storage for Last Span Context per Session ---
_last_span_context_per_session = {}
_session_context_lock = threading.Lock()

# --- ADD Global Storage for Session Trace Links ---
_session_trace_links = {}  # session_id -> list of trace contexts
_session_links_lock = threading.Lock()

# --- ADD Global Storage for Current Persistent Session ID ---
_current_persistent_session_id = None
_persistent_session_lock = threading.Lock()

# --- ADD Global Storage for Current Agent Span (for callbacks to access) ---
_current_agent_span = threading.local()
# --- END Global Storage ---

# --- ADD Global Storage for SDK Config (for accessing error_severity_map) ---
_sdk_config = None

# --- ADD Global Storage for ADK Session Tracking (for conversation continuity) ---
_last_adk_session_id = None
_adk_session_lock = threading.Lock()

def _check_and_reset_on_new_adk_session(adk_session_id: str) -> bool:
    """
    Check if this is a new ADK session and reset persistent session if needed.
    This ensures conversation continuity within the same ADK web session.
    
    Returns:
        bool: True if session was reset, False otherwise
    """
    global _last_adk_session_id
    
    if not adk_session_id:
        return False
    
    with _adk_session_lock:
        if adk_session_id != _last_adk_session_id:
            if _last_adk_session_id is not None:
                # This is a new ADK session, reset the persistent session
                logger.info(f"🔄 Detected new ADK session: {adk_session_id} (was: {_last_adk_session_id})")
                new_session = reset_persistent_session()
                logger.info(f"✅ Reset persistent session for conversation continuity: {new_session}")
            else:
                logger.info(f"🆕 First ADK session detected: {adk_session_id}")
            
            _last_adk_session_id = adk_session_id
            return True
        
        return False

def categorize_error(error: Exception, span=None) -> str:
    """
    ⚠️ CUSTOM HELPER: Categorize errors as security vs. operational.
    
    This is an OPTIONAL helper function you can call to better categorize errors.
    
    Args:
        error: The exception to categorize
        span: Optional OTel span to add attributes to
    
    Returns:
        str: Error category ('security', 'operational', 'user_error', 'unknown')
    
    Example:
        # In your callback:
        from saf3ai_sdk.instrumentation.adk_instrumentation import categorize_error
        
        try:
            result = risky_operation()
        except Exception as e:
            current_span = trace.get_current_span()
            category = categorize_error(e, current_span)
            
            if category == 'security':
                # Alert security team
                pass
    """
    error_name = type(error).__name__
    error_msg = str(error).lower()
    
    # Security-related errors
    security_indicators = [
        'permission', 'denied', 'unauthorized', 'forbidden', 'authentication',
        'credential', 'token', 'invalid signature', 'csrf', 'xss', 'injection',
        'blocked', 'threat', 'malicious', 'suspicious'
    ]
    
    # User input errors
    user_error_indicators = [
        'invalid input', 'validation', 'required field', 'parse error',
        'bad request', 'invalid format'
    ]
    
    # Operational errors
    operational_indicators = [
        'timeout', 'connection', 'network', 'unavailable', 'rate limit',
        'quota', 'overload', 'busy', 'retry'
    ]
    
    category = 'unknown'
    
    if any(indicator in error_msg for indicator in security_indicators):
        category = 'security'
    elif any(indicator in error_msg for indicator in user_error_indicators):
        category = 'user_error'
    elif any(indicator in error_msg for indicator in operational_indicators):
        category = 'operational'
    
    # Add to span if provided
    if span and span.is_recording():
        span.set_attribute("error.category", category)
        span.set_attribute("error.type", error_name)
        span.set_attribute("error.message", str(error))
        
        # Add severity based on category (from config or default)
        # Use the SDK config's error_severity_map if available
        if _sdk_config and hasattr(_sdk_config, 'error_severity_map'):
            severity_map = _sdk_config.error_severity_map
        else:
            # Fallback to default severity mapping
            severity_map = {
                'security': 'critical',
                'operational': 'warning',
                'user_error': 'info',
                'unknown': 'error'
            }
        span.set_attribute("error.severity", severity_map.get(category, 'error'))
    
    return category


def _add_trace_to_session_links(session_id: str, trace_context: TraceContext):
    """
    Add a trace context to the session's trace links for later linking.
    """
    with _session_links_lock:
        if session_id not in _session_trace_links:
            _session_trace_links[session_id] = []
        _session_trace_links[session_id].append(trace_context)
        logger.debug(f"Added trace {trace_context.span.get_span_context().trace_id:x} to session {session_id} links")

def _create_trace_links_for_session(session_id: str, current_trace_context: TraceContext):
    """
    Create trace links between the current trace and all previous traces in the session.
    """
    with _session_links_lock:
        if session_id not in _session_trace_links:
            return []
        
        links = []
        current_span_context = current_trace_context.span.get_span_context()
        
        for prev_trace_context in _session_trace_links[session_id]:
            if prev_trace_context.span.get_span_context().trace_id != current_span_context.trace_id:
                # Create a link to the previous trace
                from opentelemetry.trace import Link
                prev_span_context = prev_trace_context.span.get_span_context()
                link = Link(prev_span_context, attributes={
                    "link.type": "session_continuation",
                    "session.id": session_id,
                    "link.description": "Previous trace in same session"
                })
                links.append(link)
                logger.debug(f"Created link from trace {current_span_context.trace_id:x} to trace {prev_span_context.trace_id:x}")
        
        return links

def _cleanup_old_session_data():
    """
    Clean up old session data to prevent memory leaks.
    Keep only the last 10 traces per session.
    """
    with _session_links_lock:
        for session_id in list(_session_trace_links.keys()):
            if len(_session_trace_links[session_id]) > 10:
                # Keep only the last 10 traces
                _session_trace_links[session_id] = _session_trace_links[session_id][-10:]
                logger.debug(f"Cleaned up old traces for session {session_id}, keeping last 10")

def _get_or_create_persistent_session_id():
    """
    Get the current persistent session ID, or create a new one if none exists.
    This ID persists across agent handoffs within the same ADK web session.
    """
    global _current_persistent_session_id
    
    with _persistent_session_lock:
        if _current_persistent_session_id is None:
            _current_persistent_session_id = f"adk_session_{uuid.uuid4().hex[:8]}"
            logger.info(f"🔗 Created new persistent session ID: {_current_persistent_session_id}")
        
        return _current_persistent_session_id

def reset_persistent_session():
    """
    Reset the persistent session ID to create a new session.
    This should be called when starting a new ADK web session.
    """
    global _current_persistent_session_id
    
    with _persistent_session_lock:
        old_session_id = _current_persistent_session_id
        _current_persistent_session_id = f"adk_session_{uuid.uuid4().hex[:8]}"
        logger.info(f"🔄 Reset persistent session ID from {old_session_id} to {_current_persistent_session_id}")
        
        # Clean up old session data
        if old_session_id and old_session_id in _session_trace_links:
            with _session_links_lock:
                del _session_trace_links[old_session_id]
                logger.debug(f"Cleaned up old session data for {old_session_id}")
        
        return _current_persistent_session_id

def _get_repaired_context(adk_session_id: str = None):
    """
    Checks for a valid trace context. If it's lost (NonRecordingSpan),
    this function attempts to find the active root trace (matching adk_session_id
    if provided, otherwise the most recent) from the Saf3AI TracingCore
    and returns a new context parented to that trace. Returns None if repair fails.
    """
    current_span = trace.get_current_span()

    if current_span and current_span.is_recording():
        # Context is valid, proceed as normal.
        # logger.debug("OTel context is valid.")
        return context.get_current()

    # Context is LOST. Attempt to find the parent trace from our SDK's active list.
    logger.debug("OTel context lost. Attempting repair.")
    active_traces = saf3ai_tracer_core.get_active_traces()
    parent_span = None

    if not active_traces:
        logger.warning("Could not repair OTel context: No active traces found in SDK.")
        return None # Cannot repair if no traces are active

    # 1. Try to find the trace using the specific session ID
    if adk_session_id:
        try:
            # Ensure the key format matches how it's stored in _patch_llm_agent
            trace_id_str = f"{int(adk_session_id.replace('-', '')[:32], 16):x}"
            if trace_id_str in active_traces:
                parent_span = active_traces[trace_id_str].span
                logger.debug(f"Context repair: Found active trace matching session ID {adk_session_id}.")
            else:
                logger.debug(f"Context repair: No active trace found for session ID {adk_session_id}.")
        except (ValueError, TypeError):
             logger.warning(f"Context repair: Could not derive trace ID from session ID: {adk_session_id}")

    # 2. If session ID didn't match, fall back to the most recently added trace
    if not parent_span:
        try:
            parent_trace_context = list(active_traces.values())[-1]
            parent_span = parent_trace_context.span
            logger.debug("Context repair: Using most recent active trace as parent.")
        except Exception as e:
             logger.error(f"Context repair: Failed to get most recent active trace: {e}")
             return None # Failed to get parent

    # 3. Create the repaired context object
    if parent_span:
        try:
            repaired_context = trace.set_span_in_context(parent_span)
            logger.debug(f"Repaired broken trace context. Re-parenting to trace {parent_span.get_span_context().trace_id:x}")
            return repaired_context
        except Exception as e:
            logger.error(f"Failed to create repaired context object: {e}")

    # If all attempts failed
    logger.error("Failed to repair OTel context after all attempts.")
    return None


def _patch_llm_agent(tracer):
    """
    Patches LlmAgent.run_async. Creates a new root trace ONLY if necessary,
    attempting to LINK it to the previous trace segment for the same session.
    Otherwise creates a child span using repaired context.
    """
    try:
        from google.adk.agents import LlmAgent
        
        print(f"🚨 PRINT: _patch_llm_agent called!")
        
        if hasattr(LlmAgent, '_saf3ai_instrumented_agent'):
            print(f"🚨 PRINT: LlmAgent already instrumented.")
            logger.debug("LlmAgent already instrumented.")
            return True

        original_run_async = LlmAgent.run_async

        @functools.wraps(original_run_async)
        async def instrumented_run_async(self, *args, **kwargs):
            print(f"🚨 PRINT: LlmAgent {self.name} - instrumented_run_async called!")
            
            # Try to extract session ID from multiple sources
            adk_session_id = kwargs.get('session_id')
            if not adk_session_id and args:
                # Try to extract from args (ADK context)
                for arg in args:
                    if hasattr(arg, 'session') and hasattr(arg.session, 'id'):
                        adk_session_id = arg.session.id
                        print(f"🚨 PRINT: Found session ID in args: {adk_session_id}")
                        break
            
            # Check if this is a new ADK session and auto-reset telemetry if needed
            # This ensures conversation continuity within the same ADK web session
            if adk_session_id:
                    _check_and_reset_on_new_adk_session(adk_session_id)
            
            # For trace linking, use a persistent session ID that doesn't change between agent handoffs
            # This ensures all traces in the same ADK web session are linked together
            persistent_session_id = _get_or_create_persistent_session_id()
            print(f"🚨 PRINT: Using persistent session ID for linking: {persistent_session_id}")
            
            print(f"🚨 PRINT: LlmAgent {self.name} - session_id from kwargs: {adk_session_id}")
            print(f"🚨 PRINT: LlmAgent {self.name} - all kwargs keys: {list(kwargs.keys())}")
            print(f"🚨 PRINT: LlmAgent {self.name} - args count: {len(args) if args else 0}")
            if args:
                print(f"🚨 PRINT: LlmAgent {self.name} - first arg type: {type(args[0])}")
                if hasattr(args[0], 'session'):
                    print(f"🚨 PRINT: LlmAgent {self.name} - session in first arg: {args[0].session}")
            
            logger.info(f"🔍 INFO: LlmAgent {self.name} - session_id from kwargs: {adk_session_id}")
            logger.info(f"🔍 INFO: LlmAgent {self.name} - all kwargs keys: {list(kwargs.keys())}")
            logger.info(f"🔍 INFO: LlmAgent {self.name} - args: {args}")
            repaired_context = _get_repaired_context(adk_session_id) # Attempt repair first

            is_new_trace = (not trace.get_current_span().is_recording()) and (repaired_context is None)

            current_span_context = None # Variable to store context for linking

            if is_new_trace:
                # PATH 1: ROOT AGENT / NEW TRACE SEGMENT
                # Use persistent session ID for linking, but individual session ID for trace ID generation
                linking_session_id = persistent_session_id
                trace_session_id = adk_session_id or str(uuid.uuid4())
                
                try:
                    trace_id_int = int(trace_session_id.replace('-', '')[:32], 16)
                except (ValueError, TypeError):
                    logger.error(f"Failed to create trace ID from session ID: {trace_session_id}. Generating random trace ID.")
                    trace_id_int = random.getrandbits(128)

                span_id_int = random.getrandbits(64)
                span_context = SpanContext(
                    trace_id=trace_id_int, span_id=span_id_int, is_remote=False,
                    trace_flags=TraceFlags(0x01) # SAMPLED
                )
                span_name = f"{self.name}.run_async"
                otel_tracer = saf3ai_tracer_core.get_tracer("saf3ai.adk_instrumentation")

                # --- ENHANCED LINKING LOGIC ---
                links = []
                print(f"🚨 PRINT: Trace linking - linking_session_id: {linking_session_id}")
                print(f"🚨 PRINT: Trace linking - _session_trace_links keys: {list(_session_trace_links.keys())}")
                logger.info(f"🔍 INFO: Trace linking - linking_session_id: {linking_session_id}")
                logger.info(f"🔍 INFO: Trace linking - _session_trace_links keys: {list(_session_trace_links.keys())}")
                if linking_session_id: # Only link if we have a session ID
                    # Create links to all previous traces in this session
                    with _session_links_lock:
                        if linking_session_id in _session_trace_links:
                            logger.debug(f"🔍 DEBUG: Found {len(_session_trace_links[linking_session_id])} previous traces for session {linking_session_id}")
                            for prev_trace_context in _session_trace_links[linking_session_id]:
                                from opentelemetry.trace import Link
                                prev_span_context = prev_trace_context.span.get_span_context()
                                link = Link(prev_span_context, attributes={
                                    "link.type": "session_continuation",
                                    "session.id": linking_session_id,
                                    "link.description": "Previous trace in same session"
                                })
                                links.append(link)
                                logger.debug(f"Created link to previous trace {prev_span_context.trace_id:x} for session {linking_session_id}")
                        else:
                            logger.debug(f"🔍 DEBUG: No previous traces found for session {linking_session_id}")
                    logger.debug(f"Created {len(links)} trace links for session {linking_session_id}")
                else:
                    logger.debug(f"🔍 DEBUG: No linking_session_id provided, skipping trace linking")
                # --- END ENHANCED LINKING LOGIC ---

                # Create the root span properly using the tracer
                # Get agent ID from tags/config
                agent_id = getattr(saf3ai_tracer_core, '_agent_id', None)
                
                # Get custom attributes from tracer (includes enduser.id if set)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                logger.info(f"🔍 ROOT AGENT - Retrieved custom_attrs: {custom_attrs}")
                
                # Build span attributes
                span_attributes = {
                    "agent.name": self.name,
                    "agent.id": str(agent_id) if agent_id else "unknown",
                    "span.kind": "agent_session",
                    "adk.session_id": trace_session_id,
                    "session.id": linking_session_id,
                    "trace.type": "root_agent"
                }
                
                # Add custom attributes (including enduser.id if developer set it)
                span_attributes.update(custom_attrs)
                
                span = otel_tracer.start_span(
                    span_name,
                    attributes=span_attributes,
                    links=links # <-- Pass the link here
                )
                current_span_context = span.get_span_context() # Store context for next link

                # Store the agent span globally so callbacks can access it
                _current_agent_span.span = span

                # Set the span as current in the context
                ctx = trace.set_span_in_context(span)
                token = context_api.attach(ctx)
                trace_context_obj = TraceContext(span, token)
                trace_id_str_key = f"{trace_id_int:x}"
                with saf3ai_tracer_core._traces_lock:
                    saf3ai_tracer_core._active_traces[trace_id_str_key] = trace_context_obj
                
                # Add this trace to the session links for future linking
                if linking_session_id:
                    logger.debug(f"🔍 DEBUG: Adding trace {trace_id_str_key} to session {linking_session_id} links")
                    _add_trace_to_session_links(linking_session_id, trace_context_obj)
                else:
                    logger.debug(f"🔍 DEBUG: No linking_session_id to add trace to session links")
                
                logger.debug(f"Root agent {self.name} called. Creating new trace: {trace_id_str_key}")

                try:
                    # Store the agent span globally so callbacks can access it
                    _current_agent_span.span = trace_context_obj.span
                    
                    # Set the span as current context immediately
                    ctx = trace.set_span_in_context(trace_context_obj.span)
                    token = context_api.attach(ctx)
                    
                    # Now call the original method - LLM calls should be children of this span
                    async for event in original_run_async(self, *args, **kwargs):
                        yield event
                    
                    if trace_context_obj.span and trace_context_obj.span.is_recording():
                        trace_context_obj.span.set_status(Status(StatusCode.OK))
                        
                except Exception as e:
                    if trace_context_obj.span and trace_context_obj.span.is_recording():
                        trace_context_obj.span.set_status(Status(StatusCode.ERROR, str(e)))
                        trace_context_obj.span.set_attribute("error.message", str(e))
                    raise
                finally:
                    # Detach the context
                    context_api.detach(token)
                # Trace remains ACTIVE in _active_traces

            else:
                # PATH 2: SUB-AGENT or SESSION CONTINUATION
                logger.debug(f"Sub-agent or continuation for {self.name}. Creating child span.")
                final_context = repaired_context or context.get_current()
                span_name = f"{self.name}.run_async"
                
                with tracer.start_as_current_span(span_name, context=final_context) as span:
                    current_span_context = span.get_span_context() # Store context for next link
                    
                    # Store the agent span globally so callbacks can access it
                    _current_agent_span.span = span
                    
                    span.set_attribute("agent.name", self.name)
                    span.set_attribute("span.kind", "agent_task")
                    if adk_session_id:
                         span.set_attribute("adk.session_id", adk_session_id)
                         span.set_attribute("session.id", persistent_session_id)
                         span.set_attribute("trace.type", "sub_agent")
                    
                    # Add custom attributes (includes enduser.id if developer set it)
                    custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                    logger.info(f"🔍 SUB AGENT - Retrieved custom_attrs: {custom_attrs}")
                    logger.info(f"🔍 SUB AGENT - Setting {len(custom_attrs)} custom attributes on span")
                    for key, value in custom_attrs.items():
                        logger.info(f"🔍 SUB AGENT - Setting attribute: {key} = {value}")
                        span.set_attribute(key, value)
                    try:
                        async for event in original_run_async(self, *args, **kwargs):
                            yield event
                        span.set_status(Status(StatusCode.OK))
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.set_attribute("error.message", str(e))
                        raise

            # --- Store context for next interaction ---
            if current_span_context and persistent_session_id:
                 with _session_context_lock:
                     _last_span_context_per_session[persistent_session_id] = current_span_context
                     logger.debug(f"Updated last span context for session {persistent_session_id} to span {current_span_context.span_id:x}")
            # --- End store context ---


        setattr(LlmAgent, 'run_async', instrumented_run_async)
        setattr(LlmAgent, '_saf3ai_instrumented_agent', True)
        print(f"🚨 PRINT: Successfully instrumented LlmAgent.run_async!")
        logger.info("✅ Successfully instrumented LlmAgent.run_async (Root & Sub-Agents with Linking)")
        return True

    except ImportError:
        logger.warning("google.adk.agents.LlmAgent not found. Skipping root agent instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument LlmAgent: {e}")
        return False


def _patch_agent_tool(tracer):
    """Instrument AgentTool.run_async to capture sub-agent handoff."""
    try:
        from google.adk.tools.agent_tool import AgentTool

        if hasattr(AgentTool, '_saf3ai_instrumented_tool'):
            logger.debug("AgentTool already instrumented.")
            return True

        original_run_async = AgentTool.run_async

        @functools.wraps(original_run_async)
        async def instrumented_run_async(self, *, args, tool_context):
            adk_session_id = tool_context.get('session_id') if isinstance(tool_context, dict) else None
            persistent_session_id = _get_or_create_persistent_session_id()
            logger.debug(f"🔍 DEBUG: AgentTool - session_id from tool_context: {adk_session_id}")
            logger.debug(f"🔍 DEBUG: AgentTool - tool_context type: {type(tool_context)}")
            logger.debug(f"🔍 DEBUG: AgentTool - tool_context keys: {list(tool_context.keys()) if isinstance(tool_context, dict) else 'Not a dict'}")
            # Use the current OpenTelemetry context for proper parent-child relationships
            current_context = context.get_current()
            agent_name = getattr(self.agent, 'name', 'unknown_agent')
            span_name = f"agent_tool.handoff.{agent_name}"

            with tracer.start_as_current_span(span_name, context=current_context) as span:
                span.set_attribute("tool.type", "agent_tool")
                span.set_attribute("tool.agent_name", agent_name)
                if adk_session_id:
                    span.set_attribute("adk.session_id", adk_session_id)
                    span.set_attribute("session.id", persistent_session_id)
                    span.set_attribute("trace.type", "agent_handoff")
                if args:
                    span.set_attribute("tool.args", str(args))

                try:
                    result = await original_run_async(self, args=args, tool_context=tool_context)
                    if result:
                        span.set_attribute("tool.result", str(result)[:2000])
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise

        setattr(AgentTool, 'run_async', instrumented_run_async)
        setattr(AgentTool, '_saf3ai_instrumented_tool', True)
        logger.info("✅ Successfully instrumented AgentTool.run_async (Sub-Agent Handoff)")
        return True

    except ImportError:
        logger.warning("google.adk.tools.agent_tool.AgentTool not found. Skipping agent tool instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument AgentTool: {e}")
        return False


def _patch_gemini_llm(tracer):
    """Instrument Google ADK LLM calls (Gemini.generate_content_async)."""
    try:
        from google.adk.models.google_llm import Gemini

        if hasattr(Gemini, '_saf3ai_instrumented_llm'):
            logger.debug("Gemini LLM already instrumented.")
            return True

        original_generate_content_async = Gemini.generate_content_async

        @functools.wraps(original_generate_content_async)
        def instrumented_generate_content_async(self, *args, **kwargs):

            async def _instrumented_generator():
                print(f"🚨 PRINT: LLM instrumentation called!")
                adk_session_id = None
                config = kwargs.get('config')
                if config and hasattr(config, 'labels') and isinstance(config.labels, dict):
                     adk_session_id = config.labels.get('adk_session_id') or config.labels.get('session_id')
                
                persistent_session_id = _get_or_create_persistent_session_id()
                
                # Try to get the current active span to enhance it
                current_span = trace.get_current_span()
                print(f"🚨 PRINT: LLM - current active span: {current_span}")
                print(f"🚨 PRINT: LLM - is recording: {current_span.is_recording() if current_span else 'N/A'}")
                
                # Create a NEW child span for LLM call instead of enhancing
                # This gives us proper span hierarchy and visibility
                print(f"🚨 PRINT: Creating child LLM span under: {current_span.name if current_span else 'no parent'}")
                
                span_name = "call_llm"
                with tracer.start_as_current_span(span_name) as llm_span:
                    llm_span.set_attribute("llm.provider", "google")
                    llm_span.set_attribute("llm.model", getattr(self, 'model', 'unknown'))
                    if adk_session_id:
                        llm_span.set_attribute("adk.session_id", adk_session_id)
                        llm_span.set_attribute("session.id", persistent_session_id)
                        llm_span.set_attribute("trace.type", "llm_call")
                    
                    # Process the LLM call and add response data
                    try:
                        prompt_data = kwargs.get('contents', args[0] if args else None)
                        if prompt_data:
                            try:
                                llm_span.set_attribute("llm.prompt", json.dumps(prompt_data))
                            except TypeError:
                                llm_span.set_attribute("llm.prompt", str(prompt_data))
                            
                        async_generator = original_generate_content_async(self, *args, **kwargs)
                        
                        full_response_text = []
                        async for response in async_generator:
                            if hasattr(response, 'text') and response.text is not None:
                                full_response_text.append(response.text)
                            yield response
                        
                        llm_span.set_attribute("llm.response", "".join(full_response_text))
                        llm_span.set_status(Status(StatusCode.OK))
                        
                    except Exception as e:
                        llm_span.set_status(Status(StatusCode.ERROR, str(e)))
                        llm_span.set_attribute("error.message", str(e))
                        raise

            return _instrumented_generator()

        setattr(Gemini, 'generate_content_async', instrumented_generate_content_async)
        setattr(Gemini, '_saf3ai_instrumented_llm', True)
        logger.info("✅ Successfully instrumented Google ADK LLM calls")
        return True

    except ImportError:
        logger.warning("google.adk.models.google_llm.Gemini not found. Skipping LLM instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument ADK LLM calls: {e}")
        return False

def instrument_adk(tracer, config=None):
    """
    Auto-instrument Google ADK agents and LLMs. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance (for error_severity_map access)
    """
    global _sdk_config
    
    # Store config globally for error categorization
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for error categorization")
    
    results = {
        "root_agent_instrumentation": False,
        "sub_agent_instrumentation": False,
        "llm_instrumentation": False,
    }
    
    logger.info("🔧 Starting ADK auto-instrumentation...")
    
    results["root_agent_instrumentation"] = _patch_llm_agent(tracer)
    results["sub_agent_instrumentation"] = _patch_agent_tool(tracer)
    results["llm_instrumentation"] = _patch_gemini_llm(tracer)
    
    # Clean up old session data to prevent memory leaks
    _cleanup_old_session_data()
    
    logger.info(f"🎯 ADK auto-instrumentation complete: {results}")
    return results