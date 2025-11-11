"""
Framework-specific integrations for Saf3AI SDK.

This module contains adapters for different AI frameworks.
Each framework has its own module with framework-specific callback implementations.

Supported Frameworks:
- ADK (Google Agent Development Kit) ✅ Implemented
- LangChain
- LlamaIndex
- OpenAI
- Anthropic
- Cohere
- AI21
- Mistral
- Groq
- Ollama
- xAI
- CrewAI
- AG2 (formerly AutoGen)
- Camel AI
- Haystack
- Llama Stack
- LiteLLM
- MultiOn
- smolagents
- SwarmZero
- TaskWeaver
- REST API (generic)
"""

from .base import BaseFrameworkAdapter

__all__ = ["BaseFrameworkAdapter", "get_framework_adapter", "list_supported_frameworks"]

# Framework adapter registry
FRAMEWORK_ADAPTERS = {}


def register_framework_adapter(framework_name: str, adapter_class):
    """Register a framework adapter."""
    FRAMEWORK_ADAPTERS[framework_name.lower()] = adapter_class


def get_framework_adapter(framework_name: str):
    """
    Get a framework adapter by name.
    
    Args:
        framework_name: Name of the framework (case-insensitive)
        
    Returns:
        Framework adapter class or None if not found
    """
    return FRAMEWORK_ADAPTERS.get(framework_name.lower())


def list_supported_frameworks():
    """List all registered framework adapters."""
    return list(FRAMEWORK_ADAPTERS.keys())


# Auto-import and register all framework adapters
try:
    from .adk import ADKFrameworkAdapter
    register_framework_adapter('adk', ADKFrameworkAdapter)
    register_framework_adapter('google-adk', ADKFrameworkAdapter)
except ImportError as e:
    pass

try:
    from .langchain import LangChainFrameworkAdapter
    register_framework_adapter('langchain', LangChainFrameworkAdapter)
except ImportError:
    pass

try:
    from .llamaindex_adapter import LlamaIndexFrameworkAdapter
    register_framework_adapter('llamaindex', LlamaIndexFrameworkAdapter)
    register_framework_adapter('llama-index', LlamaIndexFrameworkAdapter)
except ImportError:
    pass

try:
    from .openai_adapter import OpenAIFrameworkAdapter
    register_framework_adapter('openai', OpenAIFrameworkAdapter)
except ImportError:
    pass

try:
    from .anthropic_adapter import AnthropicFrameworkAdapter
    register_framework_adapter('anthropic', AnthropicFrameworkAdapter)
except ImportError:
    pass

try:
    from .cohere_adapter import CohereFrameworkAdapter
    register_framework_adapter('cohere', CohereFrameworkAdapter)
except ImportError:
    pass

try:
    from .mistral_adapter import MistralFrameworkAdapter
    register_framework_adapter('mistral', MistralFrameworkAdapter)
except ImportError:
    pass

try:
    from .groq_adapter import GroqFrameworkAdapter
    register_framework_adapter('groq', GroqFrameworkAdapter)
except ImportError:
    pass

try:
    from .ollama_adapter import OllamaFrameworkAdapter
    register_framework_adapter('ollama', OllamaFrameworkAdapter)
except ImportError:
    pass

try:
    from .xai_adapter import XAIFrameworkAdapter
    register_framework_adapter('xai', XAIFrameworkAdapter)
    register_framework_adapter('x-ai', XAIFrameworkAdapter)
except ImportError:
    pass

try:
    from .crewai_adapter import CrewAIFrameworkAdapter
    register_framework_adapter('crewai', CrewAIFrameworkAdapter)
    register_framework_adapter('crew-ai', CrewAIFrameworkAdapter)
except ImportError:
    pass

try:
    from .ag2_adapter import AG2FrameworkAdapter
    register_framework_adapter('ag2', AG2FrameworkAdapter)
    register_framework_adapter('autogen', AG2FrameworkAdapter)
except ImportError:
    pass

try:
    from .camelai_adapter import CamelAIFrameworkAdapter
    register_framework_adapter('camelai', CamelAIFrameworkAdapter)
    register_framework_adapter('camel-ai', CamelAIFrameworkAdapter)
except ImportError:
    pass

try:
    from .ai21_adapter import AI21FrameworkAdapter
    register_framework_adapter('ai21', AI21FrameworkAdapter)
except ImportError:
    pass

try:
    from .haystack_adapter import HaystackFrameworkAdapter
    register_framework_adapter('haystack', HaystackFrameworkAdapter)
except ImportError:
    pass

try:
    from .llamastack_adapter import LlamaStackFrameworkAdapter
    register_framework_adapter('llamastack', LlamaStackFrameworkAdapter)
    register_framework_adapter('llama-stack', LlamaStackFrameworkAdapter)
except ImportError:
    pass

try:
    from .litellm_adapter import LiteLLMFrameworkAdapter
    register_framework_adapter('litellm', LiteLLMFrameworkAdapter)
except ImportError:
    pass

try:
    from .multion_adapter import MultiOnFrameworkAdapter
    register_framework_adapter('multion', MultiOnFrameworkAdapter)
except ImportError:
    pass

try:
    from .smolagents_adapter import SmolagentsFrameworkAdapter
    register_framework_adapter('smolagents', SmolagentsFrameworkAdapter)
except ImportError:
    pass

try:
    from .swarmzero_adapter import SwarmZeroFrameworkAdapter
    register_framework_adapter('swarmzero', SwarmZeroFrameworkAdapter)
    register_framework_adapter('swarm-zero', SwarmZeroFrameworkAdapter)
except ImportError:
    pass

try:
    from .taskweaver_adapter import TaskWeaverFrameworkAdapter
    register_framework_adapter('taskweaver', TaskWeaverFrameworkAdapter)
    register_framework_adapter('task-weaver', TaskWeaverFrameworkAdapter)
except ImportError:
    pass

try:
    from .rest_adapter import RESTAPIFrameworkAdapter
    register_framework_adapter('rest', RESTAPIFrameworkAdapter)
    register_framework_adapter('rest-api', RESTAPIFrameworkAdapter)
    register_framework_adapter('generic', RESTAPIFrameworkAdapter)
except ImportError:
    pass
