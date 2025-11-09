"""
Unit tests for evolvishub-text-classification-llm.

This package contains unit tests for individual components and modules
of the text classification library.
"""

# Import test utilities
import pytest
from typing import Any, Dict, List, Optional

# Common test fixtures and utilities
def create_mock_config() -> Dict[str, Any]:
    """Create a mock configuration for testing."""
    return {
        "provider_type": "openai",
        "model": "gpt-3.5-turbo",
        "max_tokens": 100,
        "temperature": 0.1,
        "timeout": 30
    }

def create_mock_classification_input() -> Dict[str, Any]:
    """Create a mock classification input for testing."""
    return {
        "text": "This is a test message for classification",
        "categories": ["positive", "negative", "neutral"],
        "metadata": {"source": "test", "timestamp": "2024-01-01T00:00:00Z"}
    }

def create_mock_classification_result() -> Dict[str, Any]:
    """Create a mock classification result for testing."""
    return {
        "success": True,
        "categories": {"positive": 0.8, "negative": 0.1, "neutral": 0.1},
        "confidence": 0.8,
        "processing_time_ms": 150.5,
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "metadata": {"tokens_used": 25}
    }

__all__ = [
    "create_mock_config",
    "create_mock_classification_input", 
    "create_mock_classification_result"
]
