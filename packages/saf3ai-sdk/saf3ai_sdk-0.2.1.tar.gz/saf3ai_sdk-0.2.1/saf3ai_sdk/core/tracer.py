"""Core tracing functionality for Saf3AI SDK."""

import atexit
import threading
from typing import Optional, Any, Dict, Union, Callable
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.status import StatusCode
from opentelemetry import context as context_api

from saf3ai_sdk.config import Config
from saf3ai_sdk.logging import logger

# Get SDK version from package metadata
try:
    from importlib.metadata import version, PackageNotFoundError
    try:
        SDK_VERSION = version("saf3ai-sdk")
    except PackageNotFoundError:
        # Fallback if package not installed (e.g., during development)
        SDK_VERSION = "0.1.0"
except ImportError:
    # Python < 3.8 fallback
    try:
        import importlib_metadata
        SDK_VERSION = importlib_metadata.version("saf3ai-sdk")
    except Exception:
        SDK_VERSION = "0.1.0"


class TraceContext:
    """Context manager for trace spans."""
    
    def __init__(self, span: Span, token: Optional[context_api.Token] = None):
        self.span = span
        self.token = token
        self._end_state = StatusCode.UNSET
    
    def __enter__(self) -> "TraceContext":
        """Enter the trace context."""
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> bool:
        """Exit the trace context and end the trace."""
        if exc_type is not None:
            self._end_state = StatusCode.ERROR
            if exc_val:
                logger.debug(f"Trace exiting with exception: {exc_val}")
        else:
            self._end_state = StatusCode.OK
        
        try:
            tracer.end_trace(self, self._end_state)
        except Exception as e:
            logger.error(f"Error ending trace in context manager: {e}")
        
        return False


class TracingCore:
    """Central component for tracing in Saf3AI SDK."""
    
    def __init__(self) -> None:
        """Initialize the tracing core."""
        self.provider: Optional[TracerProvider] = None
        self._initialized = False
        self._config: Optional[Config] = None
        self._active_traces: Dict[str, TraceContext] = {}
        self._traces_lock = threading.Lock()
        self._agent_id: Optional[str] = None  # Store agent ID
        self._custom_attributes: Dict[str, Any] = {}  # Store custom attributes like user_id, employee_id
        
        # Register shutdown handler
        atexit.register(self.shutdown)
    
    def initialize(self, config: Config) -> None:
        """Initialize the tracing core with configuration."""
        if self._initialized:
            logger.debug("Tracing core already initialized")
            return
        
        self._config = config
        config.validate()
        
        # Create resource attributes
        resource_attrs = {
            "service.name": config.service_name,
            "service.environment": config.environment,
            "service.version": SDK_VERSION,
            "saf3ai.sdk.version": SDK_VERSION,
            "saf3ai.sdk.type": "agent_telemetry",
        }
        
        # Add custom tags
        resource_attrs.update(config.tags)
        
        # Extract agent_id from tags if present
        if 'agent_id' in config.tags:
            self._agent_id = config.tags['agent_id']
        
        resource = Resource(resource_attrs)

        # --- CREATE OUR OWN TRACERPROVIDER ---
        # Always create our own TracerProvider instance
        self.provider = TracerProvider(resource=resource)
        logger.info("Created new TracerProvider instance")
        
        # Force our TracerProvider to be the global one
        # This ensures all spans (including ADK spans) go through our processors
        current_provider = trace.get_tracer_provider()
        if isinstance(current_provider, trace.NoOpTracerProvider):
            trace.set_tracer_provider(self.provider)
            logger.info("Set our TracerProvider as the global provider")
        else:
            logger.warning("An existing TracerProvider is already set globally")
            logger.warning("Forcing our TracerProvider to be the global one")
            # Force our provider to be used globally
            trace.set_tracer_provider(self.provider)
            logger.info("Successfully overrode the global TracerProvider")
        # --- END OF TRACERPROVIDER LOGIC ---
        
        # Create and add span processor
        logger.info(f"Console output enabled: {config.console_output}")
        logger.info(f"Debug mode enabled: {config.debug_mode}")
        
        # Create exporters and processors
        exporters = []
        processors = []
        
        if config.exporter:
            # Use custom exporter if provided
            exporters.append(config.exporter)
            logger.info("Using custom exporter")
        else:
            # Always add OTLP exporter for telemetry collection
            from saf3ai_sdk.core.exporters import Saf3AIOTLPExporter
            otlp_exporter = Saf3AIOTLPExporter(
                endpoint=config.otlp_endpoint,
                headers=config.otlp_headers,
                service_name=config.service_name,
                environment=config.environment
            )
            exporters.append(otlp_exporter)
            logger.info("Using OTLP exporter for telemetry collection")
        
        if config.console_output:
            # Add console exporter for debugging
            from saf3ai_sdk.core.exporters.console_exporter import ConsoleTelemetryExporter
            console_exporter = ConsoleTelemetryExporter(debug_mode=config.debug_mode)
            exporters.append(console_exporter)
            logger.info("Console telemetry output enabled - all spans will be printed to terminal")
        
        # Create processors for each exporter
        for i, exporter in enumerate(exporters):
            # Use SimpleSpanProcessor for console exporter (immediate export)
            # Use BatchSpanProcessor for OTLP exporter (batched export)
            if config.console_output and i == len(exporters) - 1:  # Last exporter is console
                processor = SimpleSpanProcessor(exporter)
                logger.info(f"Using SimpleSpanProcessor for console exporter (immediate export)")
            else:
                processor = SimpleSpanProcessor(exporter)  # Changed to SimpleSpanProcessor for immediate export
                logger.info(f"Using SimpleSpanProcessor for OTLP exporter (immediate export)")
            processors.append(processor)
        
        logger.info(f"Created {len(processors)} span processors for {len(exporters)} exporters")
        
        if config.processor:
            # Use custom processor if provided
            if hasattr(self.provider, 'add_span_processor'):
                self.provider.add_span_processor(config.processor)
                logger.info("Added custom span processor")
            else:
                logger.error(f"Cannot add span processor to provider of type {type(self.provider)}")
        else:
            # Add all processors we created
            if hasattr(self.provider, 'add_span_processor'):
                for i, processor in enumerate(processors):
                    self.provider.add_span_processor(processor)
                    logger.info(f"Added span processor {i+1}/{len(processors)} to provider: {type(processor).__name__}")
                logger.info(f"Added {len(processors)} span processors to provider")
            else:
                logger.error(f"Cannot add span processor to provider of type {type(self.provider)}. Telemetry will not work.")
        
        self._initialized = True
        logger.info(f"Saf3AI tracing core initialized for service: {config.service_name}")
    
    @property
    def initialized(self) -> bool:
        """Check if the tracing core is initialized."""
        return self._initialized
    
    def get_tracer(self, name: str = "saf3ai") -> trace.Tracer:
        """Get a tracer with the given name."""
        if not self._initialized:
            raise RuntimeError("Tracing core not initialized")
        
        # Use our own TracerProvider instance instead of the global one
        # This ensures spans are processed by our span processors
        if self.provider:
            logger.debug(f"Getting tracer '{name}' from our TracerProvider instance")
            return self.provider.get_tracer(name)
        else:
            logger.warning(f"TracerProvider not available, falling back to global provider")
            return trace.get_tracer(name)
    
    def get_current_span(self):
        """Get the current active span."""
        return trace.get_current_span()
    
    def get_active_trace(self):
        """Get the currently active trace if any."""
        with self._traces_lock:
            if self._active_traces:
                # Return the most recent active trace
                return list(self._active_traces.values())[-1]
        return None
    
    def start_as_current_span(self, name: str, **kwargs):
        """Start a span and set it as the current span with proper context propagation."""
        tracer = self.get_tracer()
        
        # If context is provided, use it; otherwise use current context
        context = kwargs.get('context', context_api.get_current())
        
        # Remove context from kwargs to avoid passing it to start_span
        span_kwargs = {k: v for k, v in kwargs.items() if k != 'context'}
        
        # Start span with the specified context
        span = tracer.start_span(name, context=context, **span_kwargs)
        
        # Return a context manager that sets the span as current
        return trace.use_span(span, end_on_exit=True)
    
    def start_as_current_span_with_parent(self, name: str, parent_span: Span, **kwargs):
        """Start a span with an explicit parent span and set it as current."""
        tracer = self.get_tracer()
        parent_context = trace.set_span_in_context(parent_span)
        return tracer.start_as_current_span(name, context=parent_context, **kwargs)
    
    def start_trace(
        self, 
        trace_name: str = "session", 
        tags: Optional[Dict[str, Any]] = None
    ) -> Optional[TraceContext]:
        """Start a new trace (root span) and return its context."""
        if not self._initialized:
            logger.warning("Tracing core not initialized. Cannot start trace.")
            return None
        
        # Build trace attributes
        attributes = {
            "trace.name": trace_name,
            "trace.type": "session",
            "service.name": self._config.service_name,
            "service.environment": self._config.environment,
            "saf3ai.sdk.version": "0.1.0",
            "saf3ai.sdk.type": "agent_telemetry",
        }
        
        if tags:
            attributes.update(tags)
        
        # Create span
        span, context_token = self._create_span(
            operation_name=trace_name,
            span_kind="session",
            attributes=attributes
        )
        
        logger.debug(f"Trace '{trace_name}' started with span ID: {span.get_span_context().span_id}")
        
        trace_context = TraceContext(span, token=context_token)
        
        # Track the active trace
        with self._traces_lock:
            try:
                trace_id = f"{span.get_span_context().trace_id:x}"
            except (TypeError, ValueError):
                trace_id = str(span.get_span_context().trace_id)
            
            self._active_traces[trace_id] = trace_context
            logger.debug(f"Added trace {trace_id} to active traces. Total active: {len(self._active_traces)}")
        
        return trace_context
    
    def end_trace(
        self, 
        trace_context: Optional[TraceContext] = None, 
        end_state: Union[StatusCode, str] = StatusCode.OK
    ) -> None:
        """End a trace (its root span) and finalizes it."""
        if not self._initialized:
            logger.warning("Tracing core not initialized. Cannot end trace.")
            return
        
        # If no specific trace_context provided, end all active traces
        if trace_context is None:
            with self._traces_lock:
                active_traces = list(self._active_traces.values())
                logger.debug(f"Ending all {len(active_traces)} active traces")
            
            for active_trace in active_traces:
                self._end_single_trace(active_trace, end_state)
            return
        
        # End specific trace
        self._end_single_trace(trace_context, end_state)
    
    def _end_single_trace(self, trace_context: TraceContext, end_state: Union[StatusCode, str]) -> None:
        """Internal method to end a single trace."""
        if not trace_context or not trace_context.span:
            logger.warning("Invalid TraceContext or span provided to end trace.")
            return
        
        span = trace_context.span
        token = trace_context.token
        
        try:
            trace_id = f"{span.get_span_context().trace_id:x}"
        except (TypeError, ValueError):
            trace_id = str(span.get_span_context().trace_id)
        
        logger.debug(f"Ending trace with span ID: {span.get_span_context().span_id}")
        
        try:
            # Set span status
            if isinstance(end_state, StatusCode):
                span.set_status(end_state)
            else:
                # Convert string to StatusCode
                if end_state.lower() in ["success", "ok"]:
                    span.set_status(StatusCode.OK)
                elif end_state.lower() in ["error", "failed"]:
                    span.set_status(StatusCode.ERROR)
                else:
                    span.set_status(StatusCode.UNSET)
            
            # End the span
            span.end()
            
            # Detach context token
            if token:
                context_api.detach(token)
            
            # Remove from active traces
            with self._traces_lock:
                if trace_id in self._active_traces:
                    del self._active_traces[trace_id]
                    logger.debug(f"Removed trace {trace_id} from active traces. Remaining: {len(self._active_traces)}")
            
        except Exception as e:
            logger.error(f"Error ending trace: {e}")
    
    def _create_span(
        self,
        operation_name: str,
        span_kind: str = "internal",
        attributes: Optional[Dict[str, Any]] = None,
        parent_span: Optional[Span] = None
    ) -> tuple[Span, context_api.Token]:
        """Create a span and return it with context token."""
        tracer = self.get_tracer()
        
        # Create span name
        span_name = f"{operation_name}.{span_kind}"
        
        # Build default attributes
        default_attributes = {
            "service.name": self._config.service_name,
            "service.environment": self._config.environment,
            "saf3ai.sdk.version": "0.1.0",
            "saf3ai.sdk.type": "agent_telemetry",
        }
        
        # Merge with provided attributes
        if attributes:
            default_attributes.update(attributes)
        
        # Determine the context to use
        if parent_span:
            # Use the provided parent span's context
            parent_context = trace.set_span_in_context(parent_span)
            span = tracer.start_span(span_name, context=parent_context, attributes=default_attributes)
        else:
            # Get current context
            current_context = context_api.get_current()
            span = tracer.start_span(span_name, context=current_context, attributes=default_attributes)
        
        # Set span as current context
        ctx = trace.set_span_in_context(span)
        token = context_api.attach(ctx)
        
        return span, token
    
    def get_active_traces(self) -> Dict[str, TraceContext]:
        """Get a copy of currently active traces."""
        with self._traces_lock:
            return self._active_traces.copy()
    
    def get_active_trace_count(self) -> int:
        """Get the number of currently active traces."""
        with self._traces_lock:
            return len(self._active_traces)
    
    def shutdown(self) -> None:
        """Shutdown the tracing core and clean up resources."""
        if not self._initialized:
            return
        
        try:
            # End all active traces
            with self._traces_lock:
                active_traces = list(self._active_traces.values())
                logger.debug(f"Shutting down tracer with {len(active_traces)} active traces")
            
            for trace_context in active_traces:
                try:
                    self._end_single_trace(trace_context, StatusCode.OK)
                except Exception as e:
                    logger.error(f"Error ending trace during shutdown: {e}")
            
            # Force flush all processors
            if self.provider:
                self.provider.force_flush()
                self.provider.shutdown()
            
            logger.debug("Tracing core shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during tracing core shutdown: {e}")
        
        finally:
            self._initialized = False
    
    def set_custom_attributes(self, attributes: Dict[str, Any]) -> None:
        """Set custom attributes to be added to all future spans."""
        self._custom_attributes.update(attributes)
        logger.debug(f"Custom attributes updated: {list(attributes.keys())}")
    
    def get_custom_attributes(self) -> Dict[str, Any]:
        """Get current custom attributes."""
        return self._custom_attributes.copy()
    
    def clear_custom_attributes(self) -> None:
        """Clear all custom attributes."""
        self._custom_attributes.clear()
        logger.debug("Custom attributes cleared")
    
    def get_custom_attribute(self, key: str) -> Any:
        """Get a specific custom attribute."""
        return self._custom_attributes.get(key)


# Global tracer instance
tracer = TracingCore()
