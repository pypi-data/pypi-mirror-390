# Saf3AI SDK - Multi-Framework Support

## Overview

The Saf3AI SDK now supports **23+ AI frameworks** through a pluggable adapter system. Each framework has its own adapter that handles framework-specific callback/hook integration while sharing the same core security scanning infrastructure.

## Supported Frameworks

### ✅ Production Ready
- **Google ADK** (Agent Development Kit)

### 🚧 In Progress
- **LangChain** (BaseCallbackHandler implemented)

### 📋 Ready for Implementation
- AI21
- Anthropic (Claude)
- AG2 (AutoGen)
- Camel AI
- Cohere
- CrewAI
- Groq
- Haystack
- LlamaIndex
- Llama Stack
- LiteLLM
- Mistral
- MultiOn
- Ollama
- OpenAI
- smolagents
- SwarmZero
- TaskWeaver
- xAI (Grok)
- REST API (generic)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           Saf3AI SDK - Core Layer                   │
│  - OpenTelemetry Instrumentation                    │
│  - Security Scanner (scan_prompt, scan_response)    │
│  - Telemetry Export (OTLP)                          │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │  Framework Layer   │
         │  (Adapters)        │
         └─────────┬──────────┘
                   │
   ┌───────────────┼───────────────┬──────────────┐
   │               │               │              │
┌──▼───┐      ┌───▼────┐     ┌───▼────┐    ┌───▼────┐
│ ADK  │      │LangChain│     │LlamaIdx│    │ OpenAI │
│  ✅   │      │   🚧    │     │   📋    │    │   📋    │
└──────┘      └────────┘     └────────┘    └────────┘
                               ... +19 more
```

## Quick Start (Any Framework)

### Step 1: Initialize SDK

```python
import saf3ai_sdk

saf3ai_sdk.init(
    service_name="my-agent",
    agent_id="my-agent-abc123",  # Your agent identifier
    framework="adk",  # ← Specify your framework!
    otlp_endpoint="http://localhost:4318/v1/traces"
)
```

### Step 2: Create Security Callbacks

```python
callbacks = saf3ai_sdk.create_framework_security_callbacks(
    framework="adk",  # or 'langchain', 'llamaindex', etc.
    api_endpoint="http://localhost:8082",
    agent_identifier="my-agent-abc123",  # For custom guardrails
    scan_responses=True
)
```

### Step 3: Attach to Your Framework

**For ADK:**
```python
from google.adk.agents import LlmAgent

before_cb, after_cb = callbacks

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    before_model_callback=before_cb,  # Scan prompts
    after_model_callback=after_cb     # Scan responses
)
```

**For LangChain:**
```python
from langchain.chains import LLMChain

callback = callbacks  # Single callback for LangChain

chain = LLMChain(
    llm=llm,
    prompt=prompt,
    callbacks=[callback]  # Add security scanning
)
```

**For LlamaIndex:**
```python
# Coming soon - will use CallbackManager
```

## Framework Parameter Benefits

The `framework` parameter enables:

1. **Automatic Instrumentation**: Right hooks for each framework
2. **Custom Guardrails**: Rules apply based on agent_identifier
3. **Framework-Specific Telemetry**: Captures framework-native attributes
4. **Clean Separation**: No code mixing between frameworks

## Adding Custom Policy

All frameworks support custom security policies:

```python
def my_security_policy(text: str, scan_results: dict, text_type: str) -> bool:
    """
    Custom security policy.
    
    Args:
        text: The text being scanned
        scan_results: Scan results from on-prem API
        text_type: "prompt" or "response"
    
    Returns:
        True to allow, False to block
    """
    # Check threats
    detection_results = scan_results.get("detection_results", {})
    threats = [k for k, v in detection_results.items() if v.get("result") == "MATCH_FOUND"]
    
    if threats:
        print(f"⚠️  Threats detected: {threats}")
        return False  # Block
    
    # Check custom guardrails
    custom_rules = scan_results.get("custom_rule_matches", [])
    if custom_rules:
        print(f"🚨 Custom guardrails triggered: {custom_rules}")
        return False  # Block
    
    return True  # Allow

# Use with any framework
callbacks = saf3ai_sdk.create_framework_security_callbacks(
    framework="your-framework",
    agent_identifier="my-agent",
    on_scan_complete=my_security_policy  # ← Your custom policy
)
```

## What Gets Scanned

For all frameworks, the SDK scans:

1. **Model Armor Threats** (via on-prem API):
   - CSAM
   - Dangerous Content
   - Hate Speech
   - Harassment
   - Sexual Content
   - Prompt Injection
   - Malicious URLs
   - Sensitive Data

2. **NLP Categories** (via Google NLP):
   - Business categories
   - Entity extraction
   - Sentiment analysis

3. **Custom Guardrails** (from your SaaS platform):
   - Organization-specific rules
   - Agent-specific rules
   - Keyword/regex patterns
   - Configurable severity

## Telemetry Captured

All framework integrations automatically capture:

- `framework`: Framework name (adk, langchain, etc.)
- `agent_id`: Agent identifier
- `security.threats_found`: Boolean
- `security.threat_types`: Comma-separated list
- `security.custom_guardrails`: Triggered guardrails
- Framework-specific attributes

## Extending to New Frameworks

See `saf3ai_sdk/frameworks/README.md` and `FRAMEWORK_ADAPTER_TEMPLATE.py` for detailed implementation guide.

**3-Step Process:**
1. Copy template
2. Implement 2 methods (create_prompt_callback, create_response_callback)
3. Register in `__init__.py`

**No changes needed to:**
- Core SDK code
- Scanner module
- Other framework adapters
- Telemetry infrastructure

Clean separation of concerns! 🎯

## List Supported Frameworks

```python
from saf3ai_sdk.frameworks import list_supported_frameworks

print(list_supported_frameworks())
# ['adk', 'google-adk', 'langchain', 'llamaindex', 'openai', ...]
```

## Production Deployment

For production, ensure:
1. On-prem API is running and accessible
2. Custom guardrails synced from SaaS
3. Agent identifier is unique and registered
4. Framework parameter matches your stack
5. OTLP endpoint is configured

Happy scanning! 🚀

