"""
LLM providers for the text classification library.

This module contains implementations for various LLM providers including
OpenAI, Anthropic, Google, Cohere, Azure OpenAI, AWS Bedrock, HuggingFace,
Ollama, Mistral, Replicate, and custom providers.
"""

# Import providers with error handling
_available_providers = {}

# Core imports (always required)
try:
    from .factory import ProviderFactory, register_provider
    from .base import BaseLLMProvider
    _available_providers.update({
        "ProviderFactory": ProviderFactory,
        "register_provider": register_provider,
        "BaseLLMProvider": BaseLLMProvider
    })
except ImportError as e:
    print(f"Warning: Failed to import core provider components: {e}")

# Provider imports (optional)
try:
    from .openai import OpenAIProvider
    _available_providers["OpenAIProvider"] = OpenAIProvider
except ImportError:
    pass

try:
    from .anthropic import AnthropicProvider
    _available_providers["AnthropicProvider"] = AnthropicProvider
except ImportError:
    pass

try:
    from .google import GoogleProvider
    _available_providers["GoogleProvider"] = GoogleProvider
except ImportError:
    pass

try:
    from .cohere import CohereProvider
    _available_providers["CohereProvider"] = CohereProvider
except ImportError:
    pass

try:
    from .azure_openai import AzureOpenAIProvider
    _available_providers["AzureOpenAIProvider"] = AzureOpenAIProvider
except ImportError:
    pass

try:
    from .aws_bedrock import AWSBedrockProvider
    _available_providers["AWSBedrockProvider"] = AWSBedrockProvider
except ImportError:
    pass

try:
    from .huggingface import HuggingFaceProvider
    _available_providers["HuggingFaceProvider"] = HuggingFaceProvider
except ImportError:
    pass

try:
    from .ollama import OllamaProvider
    _available_providers["OllamaProvider"] = OllamaProvider
except ImportError:
    pass

try:
    from .mistral import MistralProvider
    _available_providers["MistralProvider"] = MistralProvider
except ImportError:
    pass

try:
    from .replicate import ReplicateProvider
    _available_providers["ReplicateProvider"] = ReplicateProvider
except ImportError:
    pass

try:
    from .custom import CustomProvider
    _available_providers["CustomProvider"] = CustomProvider
except ImportError:
    pass

# Build dynamic __all__ list based on available providers
__all__ = list(_available_providers.keys())

# Expose available providers in module namespace
for name, provider_class in _available_providers.items():
    globals()[name] = provider_class