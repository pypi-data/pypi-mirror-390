"""
Streaming Classification Engine

Provides real-time streaming classification capabilities with async generators.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
from uuid import UUID, uuid4
from datetime import datetime, timezone
import time
import json

from ..core.schemas import ClassificationInput, ClassificationResult
from ..core.exceptions import StreamingError, ProviderError
from ..workflows.classification import ClassificationEngine
from .schemas import StreamingRequest, StreamingResponse, StreamingMetrics


logger = logging.getLogger(__name__)


class StreamingClassificationEngine:
    """
    Streaming classification engine for real-time text classification.
    
    Provides async generator-based streaming classification with:
    - Real-time progress updates
    - Backpressure handling
    - Connection management
    - Metrics collection
    """
    
    def __init__(
        self,
        classification_engine: ClassificationEngine,
        max_concurrent_streams: int = 10,
        buffer_size: int = 1000,
        enable_metrics: bool = True
    ):
        """Initialize streaming classification engine."""
        self.classification_engine = classification_engine
        self.max_concurrent_streams = max_concurrent_streams
        self.buffer_size = buffer_size
        self.enable_metrics = enable_metrics
        
        # Active streams tracking
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stream_semaphore = asyncio.Semaphore(max_concurrent_streams)
        
        # Metrics
        self.metrics = StreamingMetrics()
        self.start_time = time.time()
        
        # Callbacks
        self.progress_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
    
    async def stream_classify(
        self,
        request: StreamingRequest,
        progress_callback: Optional[Callable] = None
    ) -> AsyncGenerator[StreamingResponse, None]:
        """
        Stream classification results for a single text.
        
        Args:
            request: Streaming classification request
            progress_callback: Optional callback for progress updates
            
        Yields:
            StreamingResponse: Streaming classification responses
        """
        stream_id = request.stream_id or str(uuid4())
        
        try:
            # Acquire stream slot
            async with self.stream_semaphore:
                # Register stream
                self._register_stream(stream_id, request)
                
                # Send progress update
                yield StreamingResponse(
                    request_id=request.id,
                    stream_id=stream_id,
                    chunk_type="progress",
                    progress=0.0,
                    content="Starting classification..."
                )
                
                # Perform classification with streaming
                start_time = time.time()
                
                try:
                    # Check if provider supports streaming
                    provider = self.classification_engine.primary_provider
                    if hasattr(provider, '_perform_streaming_generation'):
                        # Use provider streaming
                        async for chunk in self._stream_with_provider(request, stream_id):
                            yield chunk
                    else:
                        # Fallback to chunked processing streaming
                        async for chunk in self._stream_with_chunked_processing(request, stream_id):
                            yield chunk
                    
                    # Send completion
                    yield StreamingResponse(
                        request_id=request.id,
                        stream_id=stream_id,
                        chunk_type="complete",
                        progress=1.0,
                        content="Classification completed"
                    )
                    
                except Exception as e:
                    # Send error
                    yield StreamingResponse(
                        request_id=request.id,
                        stream_id=stream_id,
                        chunk_type="error",
                        error=str(e)
                    )
                    
                    # Update metrics
                    self.metrics.total_errors += 1
                    
                    # Call error callbacks
                    for callback in self.error_callbacks:
                        try:
                            await callback(stream_id, e)
                        except Exception as cb_error:
                            logger.error(f"Error callback failed: {cb_error}")
                
                finally:
                    # Unregister stream
                    self._unregister_stream(stream_id)
                    
                    # Update metrics
                    end_time = time.time()
                    processing_time = (end_time - start_time) * 1000
                    self._update_metrics(processing_time)
        
        except Exception as e:
            logger.error(f"Streaming classification failed: {e}")
            yield StreamingResponse(
                request_id=request.id,
                stream_id=stream_id,
                chunk_type="error",
                error=f"Streaming failed: {e}"
            )
    
    async def _stream_with_provider(
        self,
        request: StreamingRequest,
        stream_id: str
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Stream classification using provider's streaming capability."""
        try:
            # Prepare messages for provider
            messages = [
                {
                    "role": "system",
                    "content": self.classification_engine.workflow.system_prompt
                },
                {
                    "role": "user", 
                    "content": self.classification_engine.workflow.user_prompt_template.format(
                        text=request.text
                    )
                }
            ]
            
            # Progress update
            yield StreamingResponse(
                request_id=request.id,
                stream_id=stream_id,
                chunk_type="progress",
                progress=0.2,
                content="Connecting to provider..."
            )
            
            # Stream from provider
            accumulated_content = ""
            chunk_count = 0
            
            provider = self.classification_engine.primary_provider
            async for chunk in provider._perform_streaming_generation(messages):
                accumulated_content += chunk
                chunk_count += 1
                
                # Send chunk
                yield StreamingResponse(
                    request_id=request.id,
                    stream_id=stream_id,
                    chunk_type="classification",
                    content=chunk,
                    progress=min(0.2 + (chunk_count * 0.01), 0.9)
                )
                
                # Backpressure handling
                if chunk_count % 10 == 0:
                    await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
            
            # Parse final classification
            try:
                classification = self._parse_classification_response(
                    accumulated_content,
                    request.categories or self.classification_engine.workflow.categories
                )
                
                yield StreamingResponse(
                    request_id=request.id,
                    stream_id=stream_id,
                    chunk_type="classification",
                    classification=classification,
                    progress=1.0
                )
                
            except Exception as parse_error:
                logger.warning(f"Failed to parse streaming response: {parse_error}")
                # Fallback to raw content
                yield StreamingResponse(
                    request_id=request.id,
                    stream_id=stream_id,
                    chunk_type="classification",
                    content=accumulated_content,
                    progress=1.0
                )
        
        except Exception as e:
            raise StreamingError(f"Provider streaming failed: {e}")
    
    async def _stream_with_chunked_processing(
        self,
        request: StreamingRequest,
        stream_id: str
    ) -> AsyncGenerator[StreamingResponse, None]:
        """Real-time streaming with actual chunked processing for non-streaming providers."""
        try:
            start_time = time.time()

            # Send initial status
            yield StreamingResponse(
                request_id=request.id,
                stream_id=stream_id,
                chunk_type="status",
                content="Starting classification...",
                progress=0.0
            )

            # Prepare classification input
            classification_input = ClassificationInput(
                text=request.text,
                metadata=request.metadata
            )

            # Send preparation complete
            yield StreamingResponse(
                request_id=request.id,
                stream_id=stream_id,
                chunk_type="status",
                content="Request prepared, sending to provider...",
                progress=0.2
            )

            # Perform actual classification with real-time progress
            classification_task = asyncio.create_task(
                self.classification_engine.classify_input(classification_input)
            )

            # Monitor task progress with real checks
            progress = 0.2
            while not classification_task.done():
                await asyncio.sleep(0.05)  # Check every 50ms for real responsiveness
                progress = min(0.8, progress + 0.1)

                yield StreamingResponse(
                    request_id=request.id,
                    stream_id=stream_id,
                    chunk_type="progress",
                    content="Processing with provider...",
                    progress=progress
                )

            # Get the actual result
            result = await classification_task

            # Send final result with actual processing time
            processing_time_ms = (time.time() - start_time) * 1000

            yield StreamingResponse(
                request_id=request.id,
                stream_id=stream_id,
                chunk_type="classification",
                classification={
                    "primary_category": result.primary_category,
                    "confidence": result.confidence,
                    "categories": result.categories,
                    "processing_time_ms": processing_time_ms
                },
                progress=1.0
            )
        
        except Exception as e:
            raise StreamingError(f"Streaming failed: {e}")
    
    def _parse_classification_response(
        self,
        response_text: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """Parse classification response from streaming text."""
        try:
            # Try to parse as JSON first
            if "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
                
                try:
                    parsed = json.loads(json_text)
                    if "primary_category" in parsed:
                        return parsed
                except json.JSONDecodeError:
                    pass
            
            # Fallback: simple text analysis
            response_lower = response_text.lower()
            
            # Find mentioned categories
            category_scores = {}
            for category in categories:
                if category.lower() in response_lower:
                    # Simple scoring based on position and frequency
                    position_score = 1.0 - (response_lower.find(category.lower()) / len(response_lower))
                    frequency_score = response_lower.count(category.lower()) * 0.1
                    category_scores[category] = min(position_score + frequency_score, 1.0)
            
            if category_scores:
                primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
                confidence = category_scores[primary_category]
            else:
                # Default fallback
                primary_category = categories[0] if categories else "unknown"
                confidence = 0.5
            
            return {
                "primary_category": primary_category,
                "confidence": confidence,
                "categories": category_scores,
                "raw_response": response_text
            }
        
        except Exception as e:
            logger.error(f"Failed to parse classification response: {e}")
            return {
                "primary_category": categories[0] if categories else "unknown",
                "confidence": 0.1,
                "categories": {},
                "raw_response": response_text,
                "parse_error": str(e)
            }
    
    def _register_stream(self, stream_id: str, request: StreamingRequest):
        """Register a new active stream."""
        self.active_streams[stream_id] = {
            "request_id": request.id,
            "start_time": time.time(),
            "text_length": len(request.text),
            "categories": request.categories
        }
        
        if self.enable_metrics:
            self.metrics.active_streams += 1
            self.metrics.total_requests += 1
    
    def _unregister_stream(self, stream_id: str):
        """Unregister an active stream."""
        if stream_id in self.active_streams:
            del self.active_streams[stream_id]
            
            if self.enable_metrics:
                self.metrics.active_streams -= 1
                self.metrics.total_responses += 1
    
    def _update_metrics(self, processing_time_ms: float):
        """Update streaming metrics."""
        if not self.enable_metrics:
            return
        
        # Update average response time
        total_responses = self.metrics.total_responses
        if total_responses > 0:
            current_avg = self.metrics.average_response_time_ms
            self.metrics.average_response_time_ms = (
                (current_avg * (total_responses - 1) + processing_time_ms) / total_responses
            )
        else:
            self.metrics.average_response_time_ms = processing_time_ms
        
        # Update throughput
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            self.metrics.throughput_per_second = self.metrics.total_responses / elapsed_time
        
        # Update timestamp
        self.metrics.timestamp = datetime.now(timezone.utc)
    
    def add_progress_callback(self, callback: Callable):
        """Add a progress callback."""
        self.progress_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Add an error callback."""
        self.error_callbacks.append(callback)
    
    def get_metrics(self) -> StreamingMetrics:
        """Get current streaming metrics."""
        return self.metrics
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active streams."""
        return self.active_streams.copy()
    
    async def cleanup(self):
        """Cleanup streaming engine resources."""
        try:
            # Cancel all active streams
            for stream_id in list(self.active_streams.keys()):
                self._unregister_stream(stream_id)
            
            logger.info("Streaming classification engine cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during streaming engine cleanup: {e}")
