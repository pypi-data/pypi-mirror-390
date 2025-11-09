"""
Provider examples for evolvishub-text-classification-llm.

This package contains examples demonstrating how to use different
LLM providers including OpenAI, Anthropic, Google, Cohere, HuggingFace,
and others for text classification tasks.
"""

# Provider-specific example configurations
from typing import Dict, Any, List

def get_openai_example_config() -> Dict[str, Any]:
    """Get OpenAI provider example configuration."""
    return {
        "provider_type": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "your-openai-api-key",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def get_anthropic_example_config() -> Dict[str, Any]:
    """Get Anthropic provider example configuration."""
    return {
        "provider_type": "anthropic",
        "model": "claude-3-haiku-20240307",
        "api_key": "your-anthropic-api-key",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def get_google_example_config() -> Dict[str, Any]:
    """Get Google provider example configuration."""
    return {
        "provider_type": "google",
        "model": "gemini-pro",
        "api_key": "your-google-api-key",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def get_huggingface_example_config() -> Dict[str, Any]:
    """Get HuggingFace provider example configuration."""
    return {
        "provider_type": "huggingface",
        "model": "microsoft/DialoGPT-medium",
        "device": "auto",  # auto, cpu, cuda
        "cache_dir": "/tmp/huggingface_cache",
        "use_quantization": True,
        "timeout": 60
    }

def get_azure_openai_example_config() -> Dict[str, Any]:
    """Get Azure OpenAI provider example configuration."""
    return {
        "provider_type": "azure_openai",
        "model": "gpt-35-turbo",
        "api_key": "your-azure-openai-api-key",
        "azure_endpoint": "https://your-resource.openai.azure.com/",
        "api_version": "2024-02-01",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def get_ollama_example_config() -> Dict[str, Any]:
    """Get Ollama provider example configuration."""
    return {
        "provider_type": "ollama",
        "model": "llama2:7b",
        "base_url": "http://localhost:11434",
        "timeout": 60
    }

def get_all_provider_configs() -> Dict[str, Dict[str, Any]]:
    """Get all provider example configurations."""
    return {
        "openai": get_openai_example_config(),
        "anthropic": get_anthropic_example_config(),
        "google": get_google_example_config(),
        "huggingface": get_huggingface_example_config(),
        "azure_openai": get_azure_openai_example_config(),
        "ollama": get_ollama_example_config()
    }

def get_provider_comparison_example() -> Dict[str, Any]:
    """Get configuration for comparing multiple providers."""
    return {
        "test_text": "I'm very disappointed with the delayed delivery and poor customer service.",
        "categories": ["customer_satisfaction", "customer_complaint", "neutral"],
        "providers_to_test": ["openai", "anthropic", "huggingface"],
        "comparison_metrics": [
            "accuracy",
            "response_time",
            "confidence_score",
            "cost_per_request"
        ]
    }

__all__ = [
    "get_openai_example_config",
    "get_anthropic_example_config",
    "get_google_example_config",
    "get_huggingface_example_config",
    "get_azure_openai_example_config",
    "get_ollama_example_config",
    "get_all_provider_configs",
    "get_provider_comparison_example"
]
