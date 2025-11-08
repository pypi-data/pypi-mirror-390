"""
Unit tests for streaming module components.

This package contains unit tests for streaming classification engine,
WebSocket support, and real-time processing capabilities.
"""

# Streaming test utilities
from typing import Dict, Any, List, AsyncGenerator
import asyncio

def create_mock_streaming_request() -> Dict[str, Any]:
    """Create a mock streaming request for testing."""
    return {
        "id": "test-stream-123",
        "text": "This is a streaming test message",
        "categories": ["urgent", "normal", "low"],
        "stream_id": "test-stream",
        "metadata": {"source": "websocket", "client_id": "test-client"}
    }

def create_mock_streaming_response() -> Dict[str, Any]:
    """Create a mock streaming response for testing."""
    return {
        "id": "test-stream-123",
        "success": True,
        "categories": {"urgent": 0.7, "normal": 0.2, "low": 0.1},
        "confidence": 0.7,
        "processing_time_ms": 89.5,
        "stream_id": "test-stream",
        "timestamp": "2024-01-01T00:00:00Z"
    }

async def create_mock_stream() -> AsyncGenerator[Dict[str, Any], None]:
    """Create a mock async stream for testing."""
    for i in range(3):
        yield {
            "id": f"stream-{i}",
            "text": f"Stream message {i}",
            "categories": ["test", "mock"],
            "sequence": i
        }
        await asyncio.sleep(0.1)

def create_mock_websocket_message() -> Dict[str, Any]:
    """Create a mock WebSocket message for testing."""
    return {
        "type": "classification_request",
        "data": {
            "text": "WebSocket test message",
            "categories": ["websocket", "test"],
            "client_id": "ws-client-123"
        }
    }

__all__ = [
    "create_mock_streaming_request",
    "create_mock_streaming_response",
    "create_mock_stream",
    "create_mock_websocket_message"
]
