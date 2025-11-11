"""Console exporter for Saf3AI SDK debug mode."""

import json
from typing import Sequence
from datetime import datetime
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace.status import StatusCode

from saf3ai_sdk.logging import logger


class ConsoleTelemetryExporter(SpanExporter):
    """Console exporter that prints telemetry data to stdout for debugging."""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.span_count = 0
        self.llm_interactions = 0
        self.agent_interactions = 0
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to console with detailed information."""
        print(f"🔍 DEBUG: Console exporter called with {len(spans) if spans else 0} spans")
        if not spans:
            return SpanExportResult.SUCCESS
        
        for span in spans:
            self.span_count += 1
            print(f"🔍 DEBUG: Processing span: {span.name}")
            self._print_span(span)
        
        return SpanExportResult.SUCCESS
    
    def _print_span(self, span: ReadableSpan):
        """Print span information to console."""
        span_name = span.name.lower()
        
        if self._is_llm_span(span_name, span.attributes):
            self._print_llm_span(span)
        elif self._is_agent_span(span_name, span.attributes):
            self._print_agent_span(span)
        else:
            self._print_general_span(span)
    
    def _is_llm_span(self, span_name: str, attributes: dict) -> bool:
        """Check if this is an LLM-related span."""
        # *** MODIFIED: Added 'call_llm' from ADK logs ***
        llm_keywords = [
            'llm', 'openai', 'anthropic', 'gemini', 'model', 
            'completion', 'chat', 'gpt', 'call_llm'
        ]
        
        if any(keyword in span_name for keyword in llm_keywords):
            return True
        
        # *** MODIFIED: Added specific ADK attribute keys ***
        adk_keys = ['gen_ai.request.model', 'gcp.vertex.agent.llm_request']
        for key in adk_keys:
            if key in attributes:
                return True
                
        return False
    
    def _is_agent_span(self, span_name: str, attributes: dict) -> bool:
        """Check if this is an agent-related span."""
        # *** MODIFIED: Added 'invoke_agent' and 'run_async' from logs ***
        agent_keywords = [
            'agent', 'financial', 'coordinator', 'analyst', 
            'task', 'workflow', 'invoke_agent', 'run_async'
        ]
        return any(keyword in span_name for keyword in agent_keywords) or \
               any(keyword in str(attributes).lower() for keyword in agent_keywords)
    
    def _print_llm_span(self, span: ReadableSpan):
        """Print LLM-specific span with special formatting."""
        self.llm_interactions += 1
        
        print("\n" + "🤖" + "="*78)
        print(f"🤖 LLM INTERACTION #{self.llm_interactions} - {span.name}")
        print("🤖" + "="*78)
        
        print(f"🤖 Duration: {self._format_duration(span.end_time - span.start_time)}")
        print(f"🤖 Status: {span.status.status_code}")
        print(f"🤖 Trace ID: {span.context.trace_id:032x}")
        
        print("\n🤖 LLM Data:")
        
        # --- SAF3AI SDK ATTRIBUTES (our custom spans) ---
        
        # Model
        if "llm.model" in span.attributes:
            print(f"🤖 📊 Model: {span.attributes['llm.model']}")
        elif "gen_ai.request.model" in span.attributes:
            print(f"🤖 📊 Model: {span.attributes['gen_ai.request.model']}")
        
        # Provider
        if "llm.provider" in span.attributes:
            print(f"🤖 🔧 Provider: {span.attributes['llm.provider']}")
        
        # Prompt (Saf3AI SDK format)
        if "llm.prompt" in span.attributes:
            prompt_text = span.attributes["llm.prompt"]
            print(f"🤖 📝 Prompt:")
            print(f"🤖    {self._format_text(prompt_text)}")
        # Prompt (ADK format)
        elif "gcp.vertex.agent.llm_request" in span.attributes:
            try:
                request_data = json.loads(span.attributes["gcp.vertex.agent.llm_request"])
                # Extract the prompt from the complex structure
                prompt_text = "System: " + request_data.get('config', {}).get('system_instruction', '')
                prompt_text += "\nUser: " + request_data.get('contents', [{}])[0].get('parts', [{}])[0].get('text', '[prompt not parsed]')
                print(f"🤖 📝 Prompt:")
                print(f"🤖    {self._format_text(prompt_text)}")
            except:
                print(f"🤖 📝 Prompt (raw): {self._format_text(str(span.attributes['gcp.vertex.agent.llm_request']))}")
        
        # Response (Saf3AI SDK format)
        if "llm.response" in span.attributes:
            response_text = span.attributes["llm.response"]
            print(f"🤖 💬 Response:")
            print(f"🤖    {self._format_text(response_text)}")
        # Response (ADK format)
        elif "gcp.vertex.agent.llm_response" in span.attributes:
            try:
                response_data = json.loads(span.attributes["gcp.vertex.agent.llm_response"])
                # Extract text or thought
                parts = response_data.get('content', {}).get('parts', [{}])
                if 'text' in parts[0]:
                    response_text = parts[0]['text']
                elif 'thought_signature' in parts[0]:
                     response_text = f"[Agent Thought: {parts[0]['thought_signature'][:100]}...]"
                else:
                    response_text = '[response not parsed]'
                print(f"🤖 💬 Response:")
                print(f"🤖    {self._format_text(response_text)}")
            except:
                print(f"🤖 💬 Response (raw): {self._format_text(str(span.attributes['gcp.vertex.agent.llm_response']))}")

        # Response length (Saf3AI SDK format)
        if "llm.response_length" in span.attributes:
            print(f"🤖 📊 Response Length: {span.attributes['llm.response_length']} characters")

        # Tokens (ADK format)
        if "gen_ai.usage.input_tokens" in span.attributes:
            print(f"🤖 📊 Input Tokens: {span.attributes['gen_ai.usage.input_tokens']}")
        if "gen_ai.usage.output_tokens" in span.attributes:
            print(f"🤖 📊 Output Tokens: {span.attributes['gen_ai.usage.output_tokens']}")
        
        # --- END OF SAF3AI SDK ATTRIBUTES ---

        print("🤖" + "="*78)
    
    def _print_agent_span(self, span: ReadableSpan):
        """Print agent-specific span."""
        self.agent_interactions += 1
        
        print("\n" + "👤" + "="*78)
        print(f"👤 AGENT INTERACTION #{self.agent_interactions} - {span.name}")
        print("👤" + "="*78)
        
        print(f"👤 Duration: {self._format_duration(span.end_time - span.start_time)}")
        print(f"👤 Status: {span.status.status_code}")
        print(f"👤 Trace ID: {span.context.trace_id:032x}")
        
        key_attrs = ['service.name', 'span.kind', 'function.name', 'agent.name']
        for attr in key_attrs:
            if attr in span.attributes:
                print(f"👤 {attr}: {span.attributes[attr]}")
        
        if span.status.status_code == StatusCode.ERROR:
            error_attrs = {k: v for k, v in span.attributes.items() if 'error' in k.lower()}
            if error_attrs:
                print(f"\n👤 ❌ Error Details:")
                for key, value in error_attrs.items():
                    print(f"👤    {key}: {value}")
        
        print("👤" + "="*78)
    
    def _print_general_span(self, span: ReadableSpan):
        """Print general span information."""
        if self.debug_mode:
            print(f"\n📊 [{self.span_count}] {span.name} ({self._format_duration(span.end_time - span.start_time)})")
        else:
            if span.status.status_code == StatusCode.ERROR or span.end_time - span.start_time > 100_000_000:  # > 100ms
                print(f"\n⚠️  [{self.span_count}] {span.name} ({self._format_duration(span.end_time - span.start_time)}) - {span.status.status_code.name}")
    
    def _extract_llm_attributes(self, attributes: dict) -> dict:
        """(No longer primary method for LLM spans, but kept for fallback)"""
        llm_attrs = {}
        llm_keywords = ['llm', 'prompt', 'response', 'model', 'token', 'input', 'output', 'completion', 'chat']
        
        for key, value in attributes.items():
            if any(keyword in key.lower() for keyword in llm_keywords):
                llm_attrs[key] = value
        
        adk_keys = [
            'gen_ai.request.model', 'gcp.vertex.agent.llm_request',
            'gcp.vertex.agent.llm_response', 'gen_ai.usage.input_tokens',
            'gen_ai.usage.output_tokens'
        ]
        for key in adk_keys:
            if key in attributes:
                llm_attrs[key] = attributes[key]
        
        return llm_attrs
    
    def _format_text(self, text: str) -> str:
        """Format long text for better readability."""
        if len(text) > 1000: # Increased limit
            return text[:1000] + "..."
        return text.replace('\n', '\n🤖    ') # Indent newlines
    
    def _format_duration(self, nanoseconds: int) -> str:
        """Format duration in human-readable format."""
        if nanoseconds < 1000:
            return f"{nanoseconds}ns"
        elif nanoseconds < 1_000_000:
            return f"{nanoseconds/1000:.1f}μs"
        elif nanoseconds < 1_000_000_000:
            return f"{nanoseconds/1_000_000:.1f}ms"
        else:
            return f"{nanoseconds/1_000_000_000:.2f}s"
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        print(f"\n🔧 Console Telemetry Summary:")
        print(f"📊 Total spans exported: {self.span_count}")
        print(f"🤖 LLM interactions: {self.llm_interactions}")
        print(f"👤 Agent interactions: {self.agent_interactions}")
        print("🔧 Console exporter shutdown complete")