# Changelog

All notable changes to the Saf3AI SDK will be documented in this file.

## [0.3.1] - 2025-11-04

### Fixed
- **Conversation Continuity**: Restored ADK session tracking logic to maintain conversation continuity
  - Messages within the same ADK web session now correctly share the same conversation ID
  - Fixed issue where each message was generating a new conversation ID
  - Added `_check_and_reset_on_new_adk_session()` function for automatic session management
  - Session resets only occur when a new ADK session is detected (e.g., page refresh)

This fix resolves the issue where conversation IDs were being split incorrectly (e.g., `dcc39295-b461-45e9-bf3c-376e74b867f8` and `acc68029-4141-45cd-905c-c13a1d409a24` being treated as separate conversations when they should be the same).

## [0.3.0] - 2025-11-04

### Added - Enterprise Features Merge

This release merges critical enterprise features from the on-prem version into the main distribution.

#### Error Categorization System
- **Error Severity Mapping**: Configure custom severity levels for different error categories
  ```python
  from saf3ai_sdk import init
  
  init(
      service_name="my-agent",
      error_severity_map={
          'security': 'critical',
          'operational': 'warning',
          'user_error': 'info',
          'unknown': 'error'
      }
  )
  ```

- **`categorize_error()` Helper Function**: Automatically categorize exceptions as security, operational, or user errors
  ```python
  from saf3ai_sdk.instrumentation.adk_instrumentation import categorize_error
  from opentelemetry import trace
  
  try:
      risky_operation()
  except Exception as e:
      span = trace.get_current_span()
      category = categorize_error(e, span)
      # category is 'security', 'operational', 'user_error', or 'unknown'
  ```

#### Dynamic Version Detection
- SDK version is now automatically detected from installed package metadata
- Uses `importlib.metadata.version()` with fallback for development mode
- Version is included in all telemetry spans for better tracking

#### Improved ADK Instrumentation
- Removed hardcoded dependency on `financial_advisor` module
- Generic session handling works with any ADK agent
- Better async support with `asyncio` integration
- Config object now passed to instrumentation layer for advanced features

### Changed
- Version bumped from 0.2.0 to 0.3.0
- `init()` function now accepts `error_severity_map` parameter
- `instrument_adk()` function signature changed to accept optional `config` parameter
- ADK session handling is now generic and works with all agents

### Fixed
- Removed agent-specific hardcoded imports that limited portability
- Improved error handling in instrumentation layer

### Technical Details

#### Modified Files
1. `pyproject.toml` - Version bump to 0.3.0
2. `saf3ai_sdk/__init__.py` - Added error_severity_map parameter
3. `saf3ai_sdk/config/config.py` - Added error_severity_map configuration field
4. `saf3ai_sdk/core/tracer.py` - Dynamic version detection
5. `saf3ai_sdk/instrumentation/adk_instrumentation.py` - Error categorization and generic session handling

#### New API Parameters

**init() function:**
```python
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
    framework: Optional[str] = None,
    error_severity_map: Optional[Dict[str, str]] = None,  # NEW
    **kwargs
) -> TracingCore:
```

#### Error Categories
The `categorize_error()` function automatically detects:
- **Security errors**: Authentication, authorization, credential, token, injection, malicious activity
- **User errors**: Invalid input, validation failures, parse errors, format issues
- **Operational errors**: Timeout, connection issues, rate limits, service unavailable
- **Unknown**: Errors that don't match known patterns

### Migration Guide

No breaking changes. All new features are optional and backward compatible.

To use new error categorization:

```python
from saf3ai_sdk import init

# Initialize with custom error severity mapping
init(
    service_name="my-agent",
    otlp_endpoint="http://localhost:4318/v1/traces",
    auto_instrument_adk=True,
    error_severity_map={
        'security': 'critical',
        'operational': 'warning',
        'user_error': 'info',
        'unknown': 'error'
    }
)
```

To use error categorization helper:

```python
from saf3ai_sdk.instrumentation.adk_instrumentation import categorize_error
from opentelemetry import trace

try:
    # Your code here
    pass
except Exception as e:
    current_span = trace.get_current_span()
    category = categorize_error(e, current_span)
    
    if category == 'security':
        # Alert security team
        send_alert_to_security(e)
    elif category == 'operational':
        # Retry or degrade gracefully
        retry_operation()
```

---

## [0.2.0] - Previous Release

Previous release focused on PyPI distribution and public documentation.

---

## [0.1.0] - Initial Release

Initial release with core telemetry and tracing capabilities.

