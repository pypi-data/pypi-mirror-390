"""
Streaming examples for evolvishub-text-classification-llm.

This package contains examples demonstrating real-time streaming
classification, WebSocket support, and batch streaming capabilities.
"""

# Streaming example configurations
from typing import Dict, Any, List, AsyncGenerator
import asyncio

def get_streaming_example_config() -> Dict[str, Any]:
    """Get streaming classification example configuration."""
    return {
        "provider_type": "openai",
        "model": "gpt-3.5-turbo",
        "stream_buffer_size": 10,
        "max_concurrent_streams": 5,
        "stream_timeout": 30,
        "websocket_port": 8765,
        "enable_real_time": True
    }

def get_websocket_example_config() -> Dict[str, Any]:
    """Get WebSocket streaming example configuration."""
    return {
        "host": "localhost",
        "port": 8765,
        "path": "/classify",
        "max_connections": 100,
        "heartbeat_interval": 30,
        "message_queue_size": 1000,
        "authentication_required": False
    }

async def generate_sample_stream() -> AsyncGenerator[Dict[str, Any], None]:
    """Generate sample streaming data for examples."""
    sample_messages = [
        "Customer service was excellent today!",
        "I'm having trouble with my account login.",
        "URGENT: System outage affecting all users.",
        "Thank you for the quick response to my inquiry.",
        "The new feature update is working perfectly.",
        "I need help with billing questions.",
        "Great job on the recent product improvements!",
        "There's a bug in the mobile application."
    ]
    
    categories = ["customer_satisfaction", "customer_complaint", "technical_support", "urgent", "normal"]
    
    for i, message in enumerate(sample_messages):
        yield {
            "id": f"stream-{i}",
            "text": message,
            "categories": categories,
            "timestamp": f"2024-01-01T00:{i:02d}:00Z",
            "metadata": {"source": "example_stream", "sequence": i}
        }
        await asyncio.sleep(0.5)  # Simulate real-time streaming

def get_batch_streaming_example() -> Dict[str, Any]:
    """Get batch streaming example configuration."""
    return {
        "batch_size": 5,
        "processing_interval": 2.0,  # seconds
        "max_queue_size": 100,
        "parallel_processing": True,
        "error_handling": "continue",  # continue, stop, retry
        "output_format": "json"
    }

def get_real_time_dashboard_config() -> Dict[str, Any]:
    """Get real-time dashboard example configuration."""
    return {
        "dashboard_port": 8080,
        "update_interval": 1.0,  # seconds
        "metrics_to_display": [
            "messages_per_second",
            "average_response_time",
            "classification_accuracy",
            "active_connections",
            "error_rate"
        ],
        "chart_types": {
            "messages_per_second": "line",
            "response_time": "histogram",
            "accuracy": "gauge",
            "connections": "counter"
        }
    }

def get_streaming_performance_test() -> Dict[str, Any]:
    """Get streaming performance test configuration."""
    return {
        "test_duration_seconds": 60,
        "messages_per_second": 10,
        "concurrent_streams": 3,
        "message_size_range": [50, 500],  # characters
        "categories_per_message": 3,
        "expected_metrics": {
            "max_response_time_ms": 2000,
            "min_throughput_mps": 8,  # messages per second
            "max_error_rate": 0.05
        }
    }

__all__ = [
    "get_streaming_example_config",
    "get_websocket_example_config",
    "generate_sample_stream",
    "get_batch_streaming_example",
    "get_real_time_dashboard_config",
    "get_streaming_performance_test"
]
