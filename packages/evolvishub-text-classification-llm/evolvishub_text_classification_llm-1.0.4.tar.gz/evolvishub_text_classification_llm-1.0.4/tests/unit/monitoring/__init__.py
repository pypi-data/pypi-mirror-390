"""
Unit tests for monitoring module components.

This package contains unit tests for health checking, metrics collection,
and observability features.
"""

# Monitoring test utilities
from typing import Dict, Any, List
from datetime import datetime

def create_mock_health_status() -> Dict[str, Any]:
    """Create a mock health status for testing."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": 45.2,
        "checks": {
            "provider_connectivity": "healthy",
            "memory_usage": "healthy", 
            "disk_space": "healthy",
            "api_endpoints": "healthy"
        },
        "details": {
            "memory_usage_percent": 65.4,
            "disk_usage_percent": 23.1,
            "active_connections": 12
        }
    }

def create_mock_metrics() -> Dict[str, Any]:
    """Create mock metrics for testing."""
    return {
        "requests_total": 1250,
        "requests_successful": 1198,
        "requests_failed": 52,
        "average_response_time_ms": 234.5,
        "total_processing_time_ms": 293125.0,
        "cache_hits": 456,
        "cache_misses": 794,
        "provider_usage": {
            "openai": 650,
            "anthropic": 400,
            "huggingface": 200
        },
        "error_rates": {
            "rate_limit": 0.02,
            "timeout": 0.01,
            "api_error": 0.01
        }
    }

def create_mock_performance_data() -> List[Dict[str, Any]]:
    """Create mock performance data for testing."""
    return [
        {
            "timestamp": "2024-01-01T00:00:00Z",
            "response_time_ms": 150.5,
            "provider": "openai",
            "success": True,
            "tokens_used": 25
        },
        {
            "timestamp": "2024-01-01T00:01:00Z", 
            "response_time_ms": 89.2,
            "provider": "anthropic",
            "success": True,
            "tokens_used": 18
        },
        {
            "timestamp": "2024-01-01T00:02:00Z",
            "response_time_ms": 0.0,
            "provider": "openai",
            "success": False,
            "error": "rate_limit_exceeded"
        }
    ]

__all__ = [
    "create_mock_health_status",
    "create_mock_metrics",
    "create_mock_performance_data"
]
