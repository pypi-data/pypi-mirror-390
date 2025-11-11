"""OpenSearch OTLP exporter for Saf3AI SDK."""

import threading
from typing import Dict, Optional, Sequence
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

from saf3ai_sdk.logging import logger


class Saf3AIOTLPExporter(OTLPSpanExporter):
    """Custom OTLP exporter that sends data to OpenSearch via OTLP Collector using HTTP."""
    
    def __init__(
        self,
        endpoint: str = "https://analyzer.sandbox.saf3ai.com/v1/traces",
        headers: Optional[Dict[str, str]] = None,
        service_name: str = "saf3ai-agent",
        environment: str = "development",
        **kwargs
    ):
        """
        Initialize the Saf3AI OTLP exporter.
        
        Args:
            endpoint: OTLP collector HTTP endpoint (e.g., http://localhost:4318/v1/traces or https://analyzer.sandbox.saf3ai.com/v1/traces)
            headers: Additional headers for OTLP requests
            service_name: Name of the service being instrumented
            environment: Environment name
            **kwargs: Additional arguments passed to parent OTLP exporter
        """
        super().__init__(endpoint=endpoint, headers=headers, **kwargs)
        self.service_name = service_name
        self.environment = environment
        self._lock = threading.Lock()
        
        logger.info(f"Saf3AI OTLP HTTP exporter initialized for {service_name} ({environment}) → {endpoint}")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to OpenSearch via OTLP Collector.
        
        Args:
            spans: Sequence of spans to export
            
        Returns:
            SpanExportResult indicating success or failure
        """
        print(f"🔍 DEBUG: OTLP exporter called with {len(spans) if spans else 0} spans")
        if not spans:
            print("🔍 DEBUG: No spans to export, returning SUCCESS")
            return SpanExportResult.SUCCESS
        
        try:
            print(f"🔍 DEBUG: Attempting to export {len(spans)} spans to OTLP collector at {self._endpoint}")
            # Note: Custom attributes are added during span creation in the tracer
            # No need to modify spans here as they're already properly configured
            
            # Use parent OTLP exporter
            result = super().export(spans)
            
            if result == SpanExportResult.SUCCESS:
                print(f"🔍 DEBUG: Successfully exported {len(spans)} spans to OpenSearch via OTLP")
                logger.debug(f"Successfully exported {len(spans)} spans to OpenSearch via OTLP")
            else:
                print(f"🔍 DEBUG: Failed to export {len(spans)} spans to OpenSearch via OTLP")
                logger.warning(f"Failed to export {len(spans)} spans to OpenSearch via OTLP")
            
            return result
            
        except Exception as e:
            print(f"🔍 DEBUG: Error exporting spans to OpenSearch via OTLP: {e}")
            logger.error(f"Error exporting spans to OpenSearch via OTLP: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        try:
            # super().shutdown()
            logger.debug("Saf3AI OTLP exporter shutdown complete")
        except Exception as e:
            logger.error(f"Error during Saf3AI OTLP exporter shutdown: {e}")
