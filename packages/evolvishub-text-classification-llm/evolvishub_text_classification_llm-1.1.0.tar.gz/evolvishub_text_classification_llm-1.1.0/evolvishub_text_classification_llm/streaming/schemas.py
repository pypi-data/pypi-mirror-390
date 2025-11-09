"""
Streaming Classification Schemas

Data models for streaming classification operations.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class StreamingRequest(BaseModel):
    """Request model for streaming classification."""
    
    id: UUID = Field(default_factory=uuid4)
    text: str = Field(..., min_length=1, max_length=100000)
    metadata: Optional[Dict[str, Any]] = None
    categories: Optional[List[str]] = None
    stream_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class StreamingResponse(BaseModel):
    """Response model for streaming classification."""
    
    request_id: UUID
    stream_id: Optional[str] = None
    chunk_type: str = Field(default="classification")  # classification, progress, error, complete
    content: Optional[str] = None
    classification: Optional[Dict[str, Any]] = None
    progress: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class StreamingBatchRequest(BaseModel):
    """Request model for streaming batch classification."""
    
    id: UUID = Field(default_factory=uuid4)
    texts: List[str] = Field(..., min_items=1, max_items=1000)
    metadata: Optional[List[Dict[str, Any]]] = None
    categories: Optional[List[str]] = None
    batch_size: int = Field(default=10, ge=1, le=100)
    stream_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class StreamingBatchResponse(BaseModel):
    """Response model for streaming batch classification."""
    
    request_id: UUID
    stream_id: Optional[str] = None
    batch_index: int
    total_batches: int
    chunk_type: str = Field(default="batch_result")  # batch_result, batch_progress, batch_error, batch_complete
    results: Optional[List[Dict[str, Any]]] = None
    progress_percentage: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class ConnectionInfo(BaseModel):
    """Information about a WebSocket connection."""
    
    connection_id: UUID = Field(default_factory=uuid4)
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    active_streams: List[str] = Field(default_factory=list)
    total_requests: int = Field(default=0)
    total_responses: int = Field(default=0)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class StreamingMetrics(BaseModel):
    """Metrics for streaming operations."""
    
    total_connections: int = Field(default=0)
    active_connections: int = Field(default=0)
    total_requests: int = Field(default=0)
    total_responses: int = Field(default=0)
    total_errors: int = Field(default=0)
    average_response_time_ms: float = Field(default=0.0)
    throughput_per_second: float = Field(default=0.0)
    active_streams: int = Field(default=0)
    memory_usage_mb: float = Field(default=0.0)
    cpu_usage_percent: float = Field(default=0.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StreamingConfig(BaseModel):
    """Configuration for streaming operations."""
    
    max_connections: int = Field(default=100, ge=1, le=10000)
    max_concurrent_streams: int = Field(default=10, ge=1, le=100)
    connection_timeout_seconds: int = Field(default=300, ge=30, le=3600)
    heartbeat_interval_seconds: int = Field(default=30, ge=10, le=300)
    max_message_size_bytes: int = Field(default=1048576, ge=1024, le=10485760)  # 1MB default
    buffer_size: int = Field(default=1000, ge=100, le=10000)
    enable_compression: bool = Field(default=True)
    enable_metrics: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    class Config:
        validate_assignment = True


class StreamingError(BaseModel):
    """Error model for streaming operations."""
    
    error_id: UUID = Field(default_factory=uuid4)
    error_type: str
    error_message: str
    request_id: Optional[UUID] = None
    stream_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    stack_trace: Optional[str] = None
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
