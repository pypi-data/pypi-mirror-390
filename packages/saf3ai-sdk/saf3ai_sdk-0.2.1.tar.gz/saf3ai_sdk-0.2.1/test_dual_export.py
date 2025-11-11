#!/usr/bin/env python3
"""
Test dual export: Full data to on-prem, stripped data to SaaS
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
import time

def test_dual_export():
    """Send test trace with sensitive data to on-prem collector"""
    
    print("=" * 70)
    print("Testing Dual Export: On-Prem (Full) + SaaS (Stripped)")
    print("=" * 70)
    print()
    
    # Set up resource
    resource = Resource.create({
        "service.name": "customer-financial-app",
        "service.version": "1.0.0",
        "deployment.environment": "production",
    })
    
    # Set up tracer
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer(__name__)
    
    # Configure OTLP exporter to ON-PREM collector
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4318/v1/traces",  # On-prem collector
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    print("📤 Sending trace with SENSITIVE data to on-prem collector...")
    print()
    
    # Create test span with sensitive customer data
    with tracer.start_as_current_span("customer-query") as span:
        # Set sensitive attributes (will be stripped for SaaS)
        span.set_attribute("prompt", "SENSITIVE: What is my account balance for account #12345?")
        span.set_attribute("response", "SENSITIVE: Your account balance is $50,000.00 USD")
        
        # Set metadata attributes (will be sent to SaaS)
        span.set_attribute("organization_id", "customer-acme-corp")
        span.set_attribute("agent_id", "financial-advisor-bot")
        span.set_attribute("model", "gpt-4")
        span.set_attribute("conversation_id", "conv-test-001")
        
        print("   Prompt: SENSITIVE: What is my account balance for account #12345?")
        print("   Response: SENSITIVE: Your account balance is $50,000.00 USD")
        print("   Organization: customer-acme-corp")
        print("   Agent: financial-advisor-bot")
        print()
        
        time.sleep(0.5)
    
    # Allow time for export
    print("⏳ Waiting for dual export to complete...")
    time.sleep(5)
    
    print()
    print("=" * 70)
    print("✅ Test trace sent!")
    print("=" * 70)
    print()
    
    print("🔍 Verify FULL data in on-prem OpenSearch (port 9202):")
    print('   curl "http://localhost:9202/traces-generic-default/_search?size=1&sort=@timestamp:desc" | jq .')
    print('   Should show: "prompt": "SENSITIVE: What is my account balance..."')
    print()
    
    print("🔍 Verify STRIPPED data in SaaS OpenSearch (port 9200):")
    print('   curl "http://localhost:9200/saf3ai-analytics-raw-logs/_search?size=1&sort=@timestamp:desc" | jq .')
    print('   Should show: "data_stripped": "true"')
    print('   Should NOT show prompt or response fields!')
    print()
    
    print("🎯 Key Verification:")
    print("   1. On-prem has FULL customer data (prompts/responses)")
    print("   2. SaaS has ONLY metadata (no prompts/responses)")
    print("   3. Data privacy is maintained!")

if __name__ == "__main__":
    test_dual_export()

