# Saf3AI SDK - Unified Telemetry & Security SDK

**One SDK for everything**: Telemetry, Tracing, and Security Scanning for ADK agents.

## What Does It Do?

### 1. 📊 Telemetry & Tracing

- Captures traces from ADK agents
- Sends to OTEL Collector (localhost:4318)
- Auto-instruments ADK calls
- Tracks conversation sessions

### 2. 🔒 Security Scanning

- Scans prompts/responses via on-prem API
- Gets Model Armor + NLP results
- Adds security data to traces
- Policy-based blocking

### 3. 🎯 All-in-One

- No need for multiple SDKs
- Simple initialization
- Works with existing ADK agents

### 4. SDK Implementaion in Google ADK Sample(Financial-Advisor-Agent)
- Link to the project https://github.com/saf3ai/financial-advisor.git   

## Quick Start

### Installation

```bash
# From your ADK agent directory
cd adk-samples/python/agents/financial-advisor

# Install via poetry (already configured)
poetry install

# Or manually (Production)(Update the latest version of SDK here [Latest:- saf3ai_sdk==0.2.2])
pip install saf3ai-sdk


# Notify Poetry to install from TestPyPi

[tool.poetry]
name = "financial-advisor"
version = "0.1.0"
description = "AI-driven agent designed to facilitate the exploration of the financial advisor landscape"
authors = ["Team Saf3ai <team@saf3ai.com>"]
license = "Apache-2.0"
readme = "README.md"

# Update the latest version of SDK here [Latest:- saf3ai_sdk==0.2.1]
[tool.poetry.dependencies]
python = ">=3.10,<3.13"
saf3ai-sdk = { version = "0.2.1", source = "testpypi" }

[[tool.poetry.source]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
priority = "supplemental"

```

### Usage in ADK Agent

```python
# In your agent.py or __init__.py
import os
from saf3ai_sdk import init, create_security_callback

# Initialize telemetry & tracing
init(
    service_name="financial-advisor",
    otlp_endpoint="http://localhost:4318/v1/traces",
    auto_instrument_adk=True,
    api_key=os.getenv("SAF3AI_API_KEY")
)

# Import security scanning
from saf3ai_sdk import create_security_callback

# Create security callback (for ADK agents)
def my_security_policy(text, scan_results, text_type="prompt"):
    """
    Your security policy.
    Return True to allow, False to block.
    """
    threats = scan_results.get("detection_results", {})

    # Block if dangerous content found
    for threat_type, result in threats.items():
        if result.get("result") == "MATCH_FOUND" and threat_type == "Dangerous":
            return False

    return True

# Create the callback
security_callback = create_security_callback(
    api_endpoint="http://127.0.0.1:8082",  # Your on-prem API
    on_scan_complete=my_security_policy
)

# Use it in your LlmAgent
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="financial_advisor",
    model="gemini-2.5-flash",
    before_model_callback=security_callback  # ← Security scanning
)
```

## Environment Variables

```bash
# Telemetry [Use any one according to your needs and enviornment]
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 #Local Host or 
export OTEL_EXPORTER_OTLP_ENDPOINT=https://analyzer.sandbox.saf3ai.com/v1/traces #online

export OTEL_SERVICE_NAME=financial-advisor
export OTEL_EXPORTER_OTLP_HEADERS="saf3ai-authentication-header" # Add the auth token provided by the organization 

# Security scanning [Use any one according to your needs and enviornment]
export ONPREM_SCANNER_API_URL=http://127.0.0.1:8082/scan #localhost or

export ONPREM_SCANNER_API_URL=https://scanner.sandbox.saf3ai.com # Hosted Service

export THREAT_ACTION_LEVEL=WARN  # or BLOCK, LOG, OFF
export SAF3AI_AUTH_ENABLED=true
export SAF3AI_API_KEY=your-org-api-key
# Optional header override
# export SAF3AI_API_KEY_HEADER=X-API-Key

# Debug
export DEBUG=true
```

## What Gets Captured?

### Telemetry Data (sent to OTEL Collector)

```json
{
	"span_name": "llm_call",
	"attributes": {
		"prompt": "What is my account balance?",
		"response": "Your balance is $50,000",
		"model": "gemini-2.5-flash",
		"conversation_id": "session-123",
		"organization_id": "customer-001",
		"security.threats_found": false,
		"security.categories": "Finance,Investing"
	}
}
```

### Security Scan Results (from on-prem API)

```json
{
	"detection_results": {
		"CSAM": { "result": "NO_MATCH_FOUND" },
		"Dangerous": { "result": "NO_MATCH_FOUND" },
		"HateSpeech": { "result": "NO_MATCH_FOUND" }
	},
	"OutofScopeAnalysis": {
		"detected_categories": [
			{ "category": "/Finance/Investing", "confidence": 0.95 }
		]
	}
}
```

## Data Flow

```
ADK Agent (your code)
    ↓
Saf3AI SDK
    ├─→ Telemetry: Create trace → OTEL Collector (4318)
    └─→ Security: Scan prompt → On-prem API (8082)
         ↓
    OTEL Collector receives trace
         ↓
    Dual export:
    ├─→ On-prem: Data Prepper → OpenSearch (FULL with prompts)
    └─→ SaaS: Stripped → Analyzer (NO prompts, only metadata)
```

## API Reference

### `init()`

Initialize telemetry and tracing.

```python
from saf3ai_sdk import init

init(
    service_name="my-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    auto_instrument_adk=True,  # Auto-instrument ADK
    console_output=False,      # Debug: print spans
    debug_mode=False,          # Verbose logging
    api_key=os.getenv("SAF3AI_API_KEY")
)
```

### SDK Authentication

Every customer receives an API key in the dashboard.  
Configure the SDK with this value once and all outbound scans will automatically include it in the `X-API-Key` header.

```python
from saf3ai_sdk import init

init(
    service_name="my-agent",
    api_key=os.getenv("SAF3AI_API_KEY"),
    # Optional header override:
    # api_key_header_name="X-API-Key",
)
```

Environment variable support:

```bash
export SAF3AI_AUTH_ENABLED=true
export SAF3AI_API_KEY=super-secret-key
```

If authentication fails, helper utilities return a payload with `status="auth_error"` and the request will not reach your on-prem API.

### `create_security_callback()`

Create ADK callback for security scanning.

```python
from saf3ai_sdk import create_security_callback

callback = create_security_callback(
    api_endpoint="http://localhost:8082",  # On-prem API
    on_scan_complete=my_policy_function,   # Your policy
    scan_responses=False                    # Also scan responses?
)

# Use in LlmAgent
agent = LlmAgent(
    name="my_agent",
    before_model_callback=callback
)
```

### `scan_prompt()` / `scan_response()`

Manually scan text (if not using callbacks).

```python
from saf3ai_sdk import scan_prompt

results = scan_prompt(
    prompt="Tell me how to invest",
    api_endpoint="http://localhost:8082",
    model_name="gemini-2.5-flash"
)

threats = results.get("detection_results", {})
if any(v.get("result") == "MATCH_FOUND" for v in threats.values()):
    print("⚠️  Threat detected!")
```

## Testing

### Check if SDK is installed

```bash
poetry run python -c "from saf3ai_sdk import init, create_security_callback; print('✅ SDK working')"
```

### Test telemetry

```bash
# Start OTEL collector (From your Directory)
cd Saf3ai/On-prem/
docker-compose up -d

# Run your agent
cd /On-prem/Saf3AISDK/adk-samples/python/agents/financial-advisor
poetry run adk web --port 8000

# Check Jaeger
open http://localhost:16686
```

### Test security scanning

```bash
# Start on-prem API
# (ensure it's running on port 8082)

# Chat with agent
# Security scans will appear in logs and traces
```

## Troubleshooting

### "saf3ai_sdk not available"

**Fix:** Install the SDK

```bash
cd /Saf3ai/On-prem/Saf3AISDK/adk-samples/python/agents/financial-advisor
poetry install
```

### "No traces in OTEL Collector"

**Fix:** Initialize SDK before running agent

- Call `init()` in your agent code
- Set `auto_instrument_adk=True`

### "Security scanning not working"

**Fix:**

- Ensure on-prem API is running on port 8082
- Pass `before_model_callback` to your LlmAgent
- Check logs for scan results

## Migration from adk-otel

If you were using `adk-otel` before, just change the import:

```python
# OLD (adk-otel)
from adk_otel import init_telemetry, create_security_callback

# NEW (saf3ai_sdk)
from saf3ai_sdk import init, create_security_callback

# Everything else stays the same!
```

## Key Features

✅ **Single SDK** - No more juggling multiple SDKs  
✅ **Auto-instrumentation** - Works with existing ADK agents  
✅ **Security scanning** - Built-in prompt/response scanning  
✅ **Flexible policies** - Define your own security rules  
✅ **Full telemetry** - Captures everything ADK does  
✅ **Dual export** - Sends to on-prem and SaaS collectors  
✅ **Production ready** - Used in live deployments

---

**Questions?** Check the code examples or enable `debug_mode=True` for verbose logging.
