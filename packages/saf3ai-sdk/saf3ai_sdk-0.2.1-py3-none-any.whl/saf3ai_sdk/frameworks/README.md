# Saf3AI SDK Framework Adapters

This directory contains framework-specific adapters for integrating Saf3AI security scanning with various AI frameworks.

## Architecture

```
saf3ai_sdk/
└── frameworks/
    ├── __init__.py           # Auto-registration of all adapters
    ├── base.py               # Base adapter interface
    ├── adk.py                # ✅ Google ADK (Implemented)
    ├── langchain_adapter.py  # 🚧 LangChain (In Progress)
    ├── llamaindex_adapter.py # 📋 LlamaIndex (Placeholder)
    ├── openai_adapter.py     # 📋 OpenAI (Placeholder)
    ├── ...                   # Other frameworks
    └── FRAMEWORK_ADAPTER_TEMPLATE.py  # Template for new adapters
```

## Implementation Status

| Framework | Status | Priority | Notes |
|-----------|--------|----------|-------|
| **Google ADK** | ✅ Implemented | HIGH | Production ready |
| **LangChain** | 🚧 In Progress | HIGH | BaseCallbackHandler implemented |
| **LlamaIndex** | 📋 Placeholder | HIGH | Needs CallbackManager integration |
| **OpenAI** | 📋 Placeholder | MEDIUM | Direct API wrapper |
| **Anthropic** | 📋 Placeholder | MEDIUM | Claude API wrapper |
| **Cohere** | 📋 Placeholder | MEDIUM | Cohere API wrapper |
| **Groq** | 📋 Placeholder | MEDIUM | Fast inference API |
| **Ollama** | 📋 Placeholder | MEDIUM | Local model wrapper |
| **CrewAI** | 📋 Placeholder | MEDIUM | Multi-agent framework |
| **AG2 (AutoGen)** | 📋 Placeholder | MEDIUM | Microsoft AutoGen |
| **AI21** | 📋 Placeholder | LOW | Jurassic models |
| **Mistral** | 📋 Placeholder | LOW | Mistral API |
| **xAI** | 📋 Placeholder | LOW | Grok API |
| **Camel AI** | 📋 Placeholder | LOW | Research framework |
| **Haystack** | 📋 Placeholder | LOW | NLP pipelines |
| **Llama Stack** | 📋 Placeholder | LOW | Meta's Llama ecosystem |
| **LiteLLM** | 📋 Placeholder | LOW | Unified LLM API |
| **MultiOn** | 📋 Placeholder | LOW | Browser automation |
| **smolagents** | 📋 Placeholder | LOW | Hugging Face agents |
| **SwarmZero** | 📋 Placeholder | LOW | Swarm intelligence |
| **TaskWeaver** | 📋 Placeholder | LOW | Microsoft TaskWeaver |
| **REST API** | 📋 Placeholder | LOW | Generic REST wrapper |

## How to Add a New Framework

### 1. Copy the Template
```bash
cp FRAMEWORK_ADAPTER_TEMPLATE.py myframework_adapter.py
```

### 2. Implement the Adapter

**Required Methods:**
- `get_framework_name()` - Return framework name
- `create_prompt_callback()` - Create pre-LLM callback
- `create_response_callback()` - Create post-LLM callback

**Key Integration Points:**
- Use `saf3ai_sdk.scanner.scan_prompt()` for prompt scanning
- Use `saf3ai_sdk.scanner.scan_response()` for response scanning
- Pass `agent_identifier` in metadata: `{"agent_identifier": self.agent_identifier}`
- Call `self.on_scan_complete(text, scan_results, text_type)` for custom policies
- Handle framework-specific blocking/allowing mechanisms

### 3. Register the Adapter

Add to `__init__.py`:
```python
try:
    from .myframework_adapter import MyFrameworkAdapter
    register_framework_adapter('myframework', MyFrameworkAdapter)
except ImportError:
    pass
```

### 4. Test the Integration

```python
from saf3ai_sdk import init, create_framework_security_callbacks

# Initialize SDK
init(
    service_name="my-agent",
    agent_id="my-agent-abc123",
    framework="myframework",
    otlp_endpoint="http://localhost:4318/v1/traces"
)

# Create security callbacks
callback = create_framework_security_callbacks(
    framework='myframework',
    api_endpoint='http://localhost:8082',
    agent_identifier='my-agent-abc123'
)

# Use with your framework
# (framework-specific code)
```

## Common Patterns

### Pattern 1: Callback-Based Frameworks (LangChain, LlamaIndex)
These frameworks use callback handlers that get notified at various lifecycle events.

**Implementation:**
- Create a class that inherits from framework's base callback class
- Override `on_llm_start` (or equivalent) to scan prompts
- Override `on_llm_end` (or equivalent) to scan responses
- Return instance of your callback class

### Pattern 2: Wrapper-Based Frameworks (OpenAI, Anthropic, Cohere)
These are direct API clients that can be wrapped.

**Implementation:**
- Create a wrapper class around the framework's client
- Intercept calls to `chat()`, `complete()`, etc.
- Scan before calling the underlying client
- Scan response after receiving it
- Return wrapped client instance

### Pattern 3: Agent-Based Frameworks (CrewAI, AG2)
These are multi-agent orchestration frameworks.

**Implementation:**
- Hook into agent execution lifecycle
- Scan at agent transition points
- Track agent-to-agent communication
- Handle multi-step workflows

## Security Scanning Flow

For all frameworks, the scanning flow is:

```
1. User Input
   ↓
2. Framework Callback Triggered
   ↓
3. scan_prompt() called
   ↓
4. On-prem API (Model Armor + NLP + Custom Guardrails)
   ↓
5. Scan Results Returned
   ↓
6. on_scan_complete() callback (user policy)
   ↓
7. Allow or Block based on policy
   ↓
8. LLM Call (if allowed)
   ↓
9. scan_response() called
   ↓
10. Response policy check
   ↓
11. Return to user (if allowed)
```

## Custom Guardrails

All adapters automatically support custom guardrails when `agent_identifier` is provided:

```python
callback = create_framework_security_callbacks(
    framework='your-framework',
    agent_identifier='my-agent-abc123',  # ← This enables custom guardrails!
    ...
)
```

The on-prem API will:
1. Match rules configured for this specific agent
2. Apply keyword/regex patterns
3. Return matches in `custom_rule_matches`
4. Include in `framework_info_combined` for telemetry

## Contributing

To contribute a new framework adapter:

1. Create the adapter using the template
2. Test with actual framework
3. Add example usage to docstring
4. Submit PR with test coverage

## Support

For framework-specific questions, see:
- **ADK**: `adk.py` (reference implementation)
- **LangChain**: `langchain_adapter.py` (callback example)
- **Template**: `FRAMEWORK_ADAPTER_TEMPLATE.py` (starter code)

