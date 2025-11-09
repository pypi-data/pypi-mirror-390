"""
Streaming module for evolvishub-text-classification-llm.

This module contains streaming classification capabilities.
"""

# Import streaming components when available
try:
    from .engine import StreamingClassificationEngine
    STREAMING_ENGINE_AVAILABLE = True
except ImportError:
    STREAMING_ENGINE_AVAILABLE = False

try:
    from .schemas import (
        StreamingRequest,
        StreamingResponse,
        StreamingBatchRequest,
        StreamingBatchResponse,
        ConnectionInfo,
        StreamingMetrics
    )
    STREAMING_SCHEMAS_AVAILABLE = True
except ImportError:
    STREAMING_SCHEMAS_AVAILABLE = False

__all__ = []

# Add available components to exports
if STREAMING_ENGINE_AVAILABLE:
    __all__.append("StreamingClassificationEngine")

if STREAMING_SCHEMAS_AVAILABLE:
    __all__.extend([
        "StreamingRequest",
        "StreamingResponse", 
        "StreamingBatchRequest",
        "StreamingBatchResponse",
        "ConnectionInfo",
        "StreamingMetrics"
    ])
