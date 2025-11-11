"""Configuration management for Saf3AI SDK."""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter


@dataclass
class Config:
    """Configuration class for Saf3AI SDK."""
    
    # OTLP Configuration
    otlp_endpoint: str = field(
        default_factory=lambda: os.getenv("SAF3AI_OTLP_ENDPOINT", "https://analyzer.sandbox.saf3ai.com/v1/traces"),
        metadata={"description": "OTLP collector endpoint"}
    )
    
    otlp_headers: Optional[Dict[str, str]] = field(
        default_factory=lambda: None,
        metadata={"description": "Additional headers for OTLP requests"}
    )
    
    # Service Configuration
    service_name: str = field(
        default_factory=lambda: os.getenv("SAF3AI_SERVICE_NAME", "saf3ai-agent"),
        metadata={"description": "Name of the service being instrumented"}
    )
    
    environment: str = field(
        default_factory=lambda: os.getenv("SAF3AI_ENVIRONMENT", "development"),
        metadata={"description": "Environment name (development, staging, production)"}
    )
    
    # OpenSearch Configuration
    opensearch_endpoint: str = field(
        default_factory=lambda: os.getenv("SAF3AI_OPENSEARCH_ENDPOINT", "http://localhost:9200"),
        metadata={"description": "OpenSearch endpoint (for reference)"}
    )
    
    opensearch_index_prefix: str = field(
        default_factory=lambda: os.getenv("SAF3AI_INDEX_PREFIX", "saf3ai"),
        metadata={"description": "Prefix for OpenSearch indices"}
    )
    
    # SDK Configuration
    auto_instrument: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_AUTO_INSTRUMENT", "true").lower() == "true",
        metadata={"description": "Whether to automatically instrument frameworks"}
    )
    
    auth_enabled: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_AUTH_ENABLED", "true").lower() == "true",
        metadata={"description": "Whether to enforce SDK-level authentication"}
    )

    api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("SAF3AI_API_KEY"),
        metadata={"description": "Organization API key presented with outbound requests"}
    )

    api_key_header_name: str = field(
        default_factory=lambda: os.getenv("SAF3AI_API_KEY_HEADER", "X-API-Key"),
        metadata={"description": "HTTP header name used for the API key"}
    )

    # ADK Auto-instrumentation
    auto_instrument_adk: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_AUTO_INSTRUMENT_ADK", "true").lower() == "true",
        metadata={"description": "Whether to automatically instrument Google ADK agents and LLMs"}
    )
    
    instrument_llm_calls: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_INSTRUMENT_LLM_CALLS", "true").lower() == "true",
        metadata={"description": "Whether to instrument LLM API calls"}
    )
    
    max_queue_size: int = field(
        default_factory=lambda: int(os.getenv("SAF3AI_MAX_QUEUE_SIZE", "512")),
        metadata={"description": "Maximum number of spans to queue"}
    )
    
    max_wait_time: int = field(
        default_factory=lambda: int(os.getenv("SAF3AI_MAX_WAIT_TIME", "5000")),
        metadata={"description": "Maximum time to wait before flushing queue (ms)"}
    )
    
    # Logging Configuration
    log_level: Union[str, int] = field(
        default_factory=lambda: os.getenv("SAF3AI_LOG_LEVEL", "INFO"),
        metadata={"description": "Logging level for Saf3AI SDK"}
    )
    
    # Debug Configuration
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_DEBUG_MODE", "false").lower() == "true",
        metadata={"description": "Enable debug logging"}
    )
    
    console_output: bool = field(
        default_factory=lambda: os.getenv("SAF3AI_CONSOLE_OUTPUT", "false").lower() == "true",
        metadata={"description": "Print telemetry to console"}
    )
    
    # Custom Exporters and Processors
    exporter: Optional[SpanExporter] = field(
        default_factory=lambda: None,
        metadata={"description": "Custom span exporter"}
    )
    
    processor: Optional[SpanProcessor] = field(
        default_factory=lambda: None,
        metadata={"description": "Custom span processor"}
    )
    
    # Additional Configuration
    tags: Dict[str, str] = field(
        default_factory=lambda: {},
        metadata={"description": "Additional tags to include in all spans"}
    )
    
    # Error Categorization Configuration
    error_severity_map: Dict[str, str] = field(
        default_factory=lambda: {
            'security': 'critical',
            'operational': 'warning',
            'user_error': 'info',
            'unknown': 'error'
        },
        metadata={"description": "Mapping of error categories to severity levels"}
    )
    
    def configure(
        self,
        otlp_endpoint: Optional[str] = None,
        otlp_headers: Optional[Dict[str, str]] = None,
        service_name: Optional[str] = None,
        environment: Optional[str] = None,
        opensearch_endpoint: Optional[str] = None,
        opensearch_index_prefix: Optional[str] = None,
        auto_instrument: Optional[bool] = None,
        auth_enabled: Optional[bool] = None,
        api_key: Optional[str] = None,
        api_key_header_name: Optional[str] = None,
        auto_instrument_adk: Optional[bool] = None,
        instrument_llm_calls: Optional[bool] = None,
        max_queue_size: Optional[int] = None,
        max_wait_time: Optional[int] = None,
        log_level: Optional[Union[str, int]] = None,
        debug_mode: Optional[bool] = None,
        console_output: Optional[bool] = None,
        exporter: Optional[SpanExporter] = None,
        processor: Optional[SpanProcessor] = None,
        tags: Optional[Dict[str, str]] = None,
        error_severity_map: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        """Update configuration with new values."""
        
        if otlp_endpoint is not None:
            self.otlp_endpoint = otlp_endpoint
            
        if otlp_headers is not None:
            self.otlp_headers = otlp_headers
            
        if service_name is not None:
            self.service_name = service_name
            
        if environment is not None:
            self.environment = environment
            
        if opensearch_endpoint is not None:
            self.opensearch_endpoint = opensearch_endpoint
            
        if opensearch_index_prefix is not None:
            self.opensearch_index_prefix = opensearch_index_prefix
            
        if auto_instrument is not None:
            self.auto_instrument = auto_instrument
        
        if auth_enabled is not None:
            self.auth_enabled = auth_enabled

        if api_key is not None:
            self.api_key = api_key

        if api_key_header_name is not None:
            self.api_key_header_name = api_key_header_name
        
        if auto_instrument_adk is not None:
            self.auto_instrument_adk = auto_instrument_adk
            
        if instrument_llm_calls is not None:
            self.instrument_llm_calls = instrument_llm_calls
            
        if max_queue_size is not None:
            self.max_queue_size = max_queue_size
            
        if max_wait_time is not None:
            self.max_wait_time = max_wait_time
            
        if log_level is not None:
            if isinstance(log_level, str):
                log_level_str = log_level.upper()
                if hasattr(logging, log_level_str):
                    self.log_level = getattr(logging, log_level_str)
                else:
                    self.log_level = logging.INFO
            else:
                self.log_level = log_level
                
        if debug_mode is not None:
            self.debug_mode = debug_mode
            # Set log level to DEBUG when debug_mode is True
            if debug_mode:
                self.log_level = logging.DEBUG
            
        if console_output is not None:
            self.console_output = console_output
                
        if exporter is not None:
            self.exporter = exporter
            
        if processor is not None:
            self.processor = processor
            
        if tags is not None:
            self.tags.update(tags)
            
        if error_severity_map is not None:
            self.error_severity_map = error_severity_map
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "otlp_endpoint": self.otlp_endpoint,
            "otlp_headers": self.otlp_headers,
            "service_name": self.service_name,
            "environment": self.environment,
            "opensearch_endpoint": self.opensearch_endpoint,
            "opensearch_index_prefix": self.opensearch_index_prefix,
            "auto_instrument": self.auto_instrument,
            "auth_enabled": self.auth_enabled,
            "api_key_header_name": self.api_key_header_name,
            "auto_instrument_adk": self.auto_instrument_adk,
            "instrument_llm_calls": self.instrument_llm_calls,
            "max_queue_size": self.max_queue_size,
            "max_wait_time": self.max_wait_time,
            "log_level": self.log_level,
            "tags": self.tags,
        }
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if not self.otlp_endpoint:
            raise ValueError("OTLP endpoint cannot be empty")
            
        if not self.service_name:
            raise ValueError("Service name cannot be empty")
            
        if self.max_queue_size <= 0:
            raise ValueError("Max queue size must be positive")
            
        if self.max_wait_time <= 0:
            raise ValueError("Max wait time must be positive")