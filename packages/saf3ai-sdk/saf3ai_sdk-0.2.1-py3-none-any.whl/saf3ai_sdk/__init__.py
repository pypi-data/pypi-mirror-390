"""Saf3AI SDK main entry point."""

from typing import Optional, Dict, Union, Any
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter

from saf3ai_sdk.config import Config
from saf3ai_sdk.core.tracer import tracer, TracingCore
from saf3ai_sdk.core.auth import auth_manager
from saf3ai_sdk.logging import logger

# Import decorators for easy access
from saf3ai_sdk.core.decorators import trace, agent, task, tool, workflow

# Import security scanning functionality (consolidated from adk-otel)
from saf3ai_sdk.callbacks import (
    register_security_callback,
    get_callback_manager,
    LLMSecurityCallback,
    LLMCallbackManager
)
from saf3ai_sdk.adk_callbacks import create_security_callback
from saf3ai_sdk.scanner import scan_prompt, scan_response, scan_prompt_and_response

# Import framework adapters
from saf3ai_sdk.frameworks import BaseFrameworkAdapter, get_framework_adapter

__all__ = [
    "init",
    "tracer",
    "get_tracer",
    "trace",
    "agent",
    "task",
    "tool",
    "workflow",
    "reset_session",
    "set_custom_attributes",  # NEW
    "get_custom_attributes",   # NEW
    "clear_custom_attributes", # NEW
    # Security scanning (from adk-otel, now consolidated)
    "register_security_callback",
    "get_callback_manager",
    "LLMSecurityCallback",
    "LLMCallbackManager",
    "create_security_callback",
    "scan_prompt",
    "scan_response",
    "scan_prompt_and_response",
    # Framework adapters
    "BaseFrameworkAdapter",
    "get_framework_adapter",
    "create_framework_security_callbacks",  # NEW helper
]

def get_tracer(name: str = "saf3ai"):
    """
    Get a tracer from the Saf3AI SDK's TracerProvider.
    
    This ensures spans are processed by our span processors.
    
    Args:
        name: Name of the tracer
        
    Returns:
        Tracer instance from our TracerProvider
    """
    return tracer.get_tracer(name)


def set_custom_attributes(attributes: Dict[str, Any]) -> None:
    """Set custom attributes to be added to all future spans."""
    tracer.set_custom_attributes(attributes)


def get_custom_attributes() -> Dict[str, Any]:
    """Get current custom attributes."""
    return tracer.get_custom_attributes()


def clear_custom_attributes() -> None:
    """Clear all custom attributes."""
    tracer.clear_custom_attributes()


def init(
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    otlp_headers: Optional[Dict[str, str]] = None,
    log_level: Optional[Union[str, int]] = None,
    debug_mode: Optional[bool] = None,
    console_output: Optional[bool] = None,
    auto_instrument_adk: Optional[bool] = None,
    exporter: Optional[SpanExporter] = None,
    processor: Optional[SpanProcessor] = None,
    tags: Optional[Dict[str, str]] = None,
    agent_id: Optional[str] = None,
    framework: Optional[str] = None,  # NEW: 'adk', 'langchain', 'llamaindex', etc.
    error_severity_map: Optional[Dict[str, str]] = None,  # Custom severity mapping
    auth_enabled: Optional[bool] = None,
    api_key: Optional[str] = None,
    api_key_header_name: Optional[str] = None,
    **kwargs
) -> TracingCore:
    """
    Initialize the Saf3AI SDK.
    
    Configures the global tracer, sets up exporters, and applies
    automatic instrumentation for the specified framework.
    
    Args:
        framework: AI framework being used ('adk', 'langchain', 'llamaindex', or None for manual)
        agent_id: Unique identifier for this agent (alphanumeric, e.g., 'financial-coordinator-b14fd')
        error_severity_map: Optional custom mapping of error categories to severity levels
                            Default: {'security': 'critical', 'operational': 'warning', 
                                     'user_error': 'info', 'unknown': 'error'}
        ... (other params)
    """
    
    config = Config()
    
    # Add agent_id and framework to tags
    if not tags:
        tags = {}
    
    if agent_id:
        tags['agent_id'] = agent_id
    
    if framework:
        tags['framework'] = framework
        tags['saf3ai.framework'] = framework
    
    config.configure(
        service_name=service_name,
        environment=environment,
        otlp_endpoint=otlp_endpoint,
        otlp_headers=otlp_headers,
        log_level=log_level,
        debug_mode=debug_mode,
        console_output=console_output,
        auto_instrument_adk=auto_instrument_adk,
        exporter=exporter,
        processor=processor,
        tags=tags,
        error_severity_map=error_severity_map,
        auth_enabled=auth_enabled,
        api_key=api_key,
        api_key_header_name=api_key_header_name,
        **kwargs
    )
    
    auth_manager.configure(
        enabled=config.auth_enabled,
        api_key=config.api_key,
        header_name=config.api_key_header_name,
    )

    # Initialize the core tracer
    tracer.initialize(config)
    
    # Apply auto-instrumentation if requested
    if auto_instrument_adk:
        from saf3ai_sdk.instrumentation import instrument_adk
        instrument_adk(tracer.get_tracer("saf3ai-adk"), config)
            
    return tracer

def create_framework_security_callbacks(
    framework: str,
    api_endpoint: str,
    agent_identifier: str,
    api_key: Optional[str] = None,
    timeout: int = 10,
    on_scan_complete: Optional[Any] = None,
    scan_responses: bool = False
):
    """
    Create framework-specific security callbacks.
    
    This is a convenience function that automatically creates the right callbacks
    based on the framework being used.
    
    Args:
        framework: Framework name ('adk', 'langchain', 'llamaindex')
        api_endpoint: URL of the on-prem scanning API
        agent_identifier: Agent identifier for custom guardrails
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        on_scan_complete: Optional callback function(text, scan_results, text_type) -> bool
        scan_responses: Whether to also scan responses (framework-dependent)
    
    Returns:
        Framework-specific callback(s) - format depends on framework
    """
    adapter_class = get_framework_adapter(framework)
    
    if not adapter_class:
        logger.error(f"Unknown framework: {framework}. Supported: adk, langchain, llamaindex")
        return None
    
    # Create the adapter instance
    adapter = adapter_class(
        api_endpoint=api_endpoint,
        agent_identifier=agent_identifier,
        api_key=api_key,
        timeout=timeout,
        on_scan_complete=on_scan_complete
    )
    
    # For ADK, use the create_callbacks convenience method
    if framework in ['adk', 'google-adk']:
        return adapter.create_callbacks(scan_responses=scan_responses)
    
    # For other frameworks, return both callbacks
    if scan_responses:
        return (adapter.create_prompt_callback(), adapter.create_response_callback())
    else:
        return adapter.create_prompt_callback()


def reset_session():
    """
    Reset the current persistent session to create a new session.
    Call this when you want to start a new ADK web session.
    This will create a new persistent session ID and clean up old session data.
    """
    try:
        from saf3ai_sdk.instrumentation.adk_instrumentation import reset_persistent_session
        return reset_persistent_session()
    except ImportError:
        print("🔍 DEBUG: ADK instrumentation not available")
        return None

# Alias init_telemetry for compatibility (was init_telemetry in adk-otel)
init_telemetry = init