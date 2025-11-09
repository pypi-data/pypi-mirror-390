"""
Unit tests for provider implementations.

This package contains unit tests for all LLM provider implementations
including OpenAI, Anthropic, Google, Cohere, HuggingFace, and others.
"""

# Provider test utilities
from typing import Dict, Any, List
import pytest

def create_mock_provider_response() -> Dict[str, Any]:
    """Create a mock provider response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "content": "positive: 0.8, negative: 0.1, neutral: 0.1"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 20,
            "completion_tokens": 15,
            "total_tokens": 35
        },
        "model": "gpt-3.5-turbo"
    }

def create_mock_api_error() -> Dict[str, Any]:
    """Create a mock API error for testing error handling."""
    return {
        "error": {
            "message": "Rate limit exceeded",
            "type": "rate_limit_error",
            "code": "rate_limit_exceeded"
        }
    }

def get_test_providers() -> List[str]:
    """Get list of providers to test."""
    return [
        "openai",
        "anthropic", 
        "google",
        "cohere",
        "azure_openai",
        "aws_bedrock",
        "huggingface",
        "ollama",
        "mistral",
        "replicate"
    ]

__all__ = [
    "create_mock_provider_response",
    "create_mock_api_error",
    "get_test_providers"
]
