"""
Unit tests for core module components.

This package contains unit tests for core schemas, exceptions, 
configuration, and interfaces.
"""

# Core test utilities
from typing import Dict, Any

def create_mock_provider_config() -> Dict[str, Any]:
    """Create a mock provider configuration for core testing."""
    return {
        "provider_type": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "test-key",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30,
        "retry_attempts": 3
    }

def create_mock_workflow_config() -> Dict[str, Any]:
    """Create a mock workflow configuration for core testing."""
    return {
        "name": "test_workflow",
        "description": "Test workflow for unit testing",
        "providers": ["openai", "anthropic"],
        "fallback_enabled": True,
        "caching_enabled": True,
        "monitoring_enabled": True
    }

__all__ = [
    "create_mock_provider_config",
    "create_mock_workflow_config"
]
