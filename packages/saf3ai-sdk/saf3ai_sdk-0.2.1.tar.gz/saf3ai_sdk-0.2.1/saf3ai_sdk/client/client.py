"""Client for Saf3AI SDK."""

import threading
from typing import Any, Dict, Optional

from saf3ai_sdk.config import Config
from saf3ai_sdk.core.tracer import tracer
from saf3ai_sdk.core.auth import auth_manager
from saf3ai_sdk.logging import logger, setup_logging


class Client:
    """Singleton client for Saf3AI SDK."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Client, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config: Optional[Config] = None
        self._initialized = True
    
    def init(
        self,
        # OTLP Configuration
        otlp_endpoint: str = "https://analyzer.sandbox.saf3ai.com/v1/traces",
        otlp_headers: Optional[Dict[str, str]] = None,
        
        # Service Configuration
        service_name: str = "saf3ai-agent",
        environment: str = "development",
        
        # OpenSearch Configuration
        opensearch_endpoint: str = "http://localhost:9200",
        opensearch_index_prefix: str = "saf3ai",
        
        # SDK Configuration
        auto_instrument: bool = True,
        instrument_llm_calls: bool = True,
        max_queue_size: int = 512,
        max_wait_time: int = 5000,
        
        # Debug Configuration
        debug_mode: bool = False,
        console_output: bool = False,

        # Authentication Configuration
        auth_enabled: Optional[bool] = None,
        api_key: Optional[str] = None,
        api_key_header_name: Optional[str] = None,
        
        **kwargs
    ) -> "Client":
        """
        Initialize the Saf3AI SDK client.
        
        Args:
            otlp_endpoint: OTLP collector endpoint
            otlp_headers: Additional headers for OTLP requests
            service_name: Name of the service being instrumented
            environment: Environment name
            opensearch_endpoint: OpenSearch endpoint (for reference)
            opensearch_index_prefix: Prefix for OpenSearch indices
            auto_instrument: Whether to automatically instrument frameworks
            instrument_llm_calls: Whether to instrument LLM API calls
            max_queue_size: Maximum number of spans to queue
            max_wait_time: Maximum time to wait before flushing queue
            debug_mode: Enable debug logging
            console_output: Print telemetry to console
            auth_enabled: Enable or disable SDK-level authentication
            api_key: Organization API key to attach to outbound requests
            api_key_header_name: Header name used for the API key (default X-API-Key)
            **kwargs: Additional configuration parameters
            
        Returns:
            The initialized client instance
        """
        # Create configuration
        self.config = Config()
        self.config.configure(
            otlp_endpoint=otlp_endpoint,
            otlp_headers=otlp_headers,
            service_name=service_name,
            environment=environment,
            opensearch_endpoint=opensearch_endpoint,
            opensearch_index_prefix=opensearch_index_prefix,
            auto_instrument=auto_instrument,
            instrument_llm_calls=instrument_llm_calls,
            max_queue_size=max_queue_size,
            max_wait_time=max_wait_time,
            debug_mode=debug_mode,
            console_output=console_output,
            auth_enabled=auth_enabled,
            api_key=api_key,
            api_key_header_name=api_key_header_name,
            **kwargs
        )
        
        # Setup logging
        setup_logging(self.config.log_level)

        # Configure authentication
        auth_manager.configure(
            enabled=self.config.auth_enabled,
            api_key=self.config.api_key,
            header_name=self.config.api_key_header_name,
        )
        
        # Initialize tracing core
        tracer.initialize(self.config)
        
        logger.info(f"Saf3AI SDK initialized for service: {service_name}")
        
        return self
    
    def configure(self, **kwargs) -> None:
        """Update client configuration."""
        if self.config is None:
            raise RuntimeError("Client not initialized. Call init() first.")
        
        self.config.configure(**kwargs)
        logger.info("Client configuration updated")
    
    def start_trace(self, trace_name: str = "session", tags: Optional[Dict[str, Any]] = None):
        """Start a new trace."""
        if not tracer.initialized:
            raise RuntimeError("Tracer not initialized. Call init() first.")
        
        return tracer.start_trace(trace_name, tags)
    
    def end_trace(self, trace_context=None, end_state="OK"):
        """End a trace."""
        if not tracer.initialized:
            raise RuntimeError("Tracer not initialized. Call init() first.")
        
        tracer.end_trace(trace_context, end_state)
    
    def get_active_traces(self):
        """Get currently active traces."""
        if not tracer.initialized:
            return {}
        
        return tracer.get_active_traces()
    
    def get_active_trace_count(self) -> int:
        """Get the number of currently active traces."""
        if not tracer.initialized:
            return 0
        
        return tracer.get_active_trace_count()
    
    def shutdown(self) -> None:
        """Shutdown the client and clean up resources."""
        if tracer.initialized:
            tracer.shutdown()
            logger.info("Saf3AI SDK client shutdown complete")
