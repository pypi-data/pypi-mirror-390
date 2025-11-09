"""
Integration tests for evolvishub-text-classification-llm.

This package contains integration tests that verify the interaction
between different components and external services.
"""

# Integration test utilities
import os
from typing import Dict, Any, List, Optional

def get_test_api_keys() -> Dict[str, Optional[str]]:
    """Get API keys for integration testing from environment variables."""
    return {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
        "cohere": os.getenv("COHERE_API_KEY"),
        "azure_openai": os.getenv("AZURE_OPENAI_API_KEY"),
        "huggingface": os.getenv("HUGGINGFACE_TOKEN"),
        "mistral": os.getenv("MISTRAL_API_KEY"),
        "replicate": os.getenv("REPLICATE_API_TOKEN")
    }

def get_available_providers() -> List[str]:
    """Get list of providers available for integration testing."""
    api_keys = get_test_api_keys()
    return [provider for provider, key in api_keys.items() if key is not None]

def create_integration_test_config() -> Dict[str, Any]:
    """Create configuration for integration testing."""
    return {
        "timeout": 60,  # Longer timeout for real API calls
        "retry_attempts": 2,
        "test_categories": ["positive", "negative", "neutral"],
        "test_texts": [
            "This is an excellent product with amazing features!",
            "I'm very disappointed with this poor quality service.",
            "The weather today is partly cloudy with mild temperatures."
        ],
        "expected_confidence_threshold": 0.5,
        "max_response_time_ms": 5000
    }

def should_skip_provider_test(provider: str) -> bool:
    """Check if a provider test should be skipped due to missing API key."""
    api_keys = get_test_api_keys()
    return api_keys.get(provider) is None

def create_end_to_end_test_scenario() -> Dict[str, Any]:
    """Create a comprehensive end-to-end test scenario."""
    return {
        "workflow_config": {
            "name": "integration_test_workflow",
            "providers": ["openai", "anthropic"],
            "fallback_enabled": True,
            "caching_enabled": False,  # Disable for testing
            "monitoring_enabled": True
        },
        "test_inputs": [
            {
                "text": "Customer service was outstanding today!",
                "categories": ["customer_satisfaction", "customer_complaint"],
                "expected_top_category": "customer_satisfaction"
            },
            {
                "text": "URGENT: System is down and needs immediate attention",
                "categories": ["urgent", "normal", "low"],
                "expected_top_category": "urgent"
            },
            {
                "text": "How do I reset my password?",
                "categories": ["technical_support", "billing", "general"],
                "expected_top_category": "technical_support"
            }
        ],
        "performance_requirements": {
            "max_response_time_ms": 3000,
            "min_accuracy": 0.7,
            "max_error_rate": 0.05
        }
    }

__all__ = [
    "get_test_api_keys",
    "get_available_providers",
    "create_integration_test_config",
    "should_skip_provider_test",
    "create_end_to_end_test_scenario"
]
