"""
Unit tests for streaming classification engine.

Tests the StreamingClassificationEngine functionality including:
- Stream management and registration
- Real-time classification streaming
- Progress tracking and metrics
- Error handling and recovery
- Backpressure handling
- Connection management
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
from uuid import uuid4

from evolvishub_text_classification_llm.streaming.engine import StreamingClassificationEngine
from evolvishub_text_classification_llm.streaming.schemas import StreamingRequest, StreamingResponse
from evolvishub_text_classification_llm.workflows.classification import ClassificationEngine
from evolvishub_text_classification_llm.core.schemas import ClassificationResult
from evolvishub_text_classification_llm.core.exceptions import StreamingError


class TestStreamingClassificationEngine:
    """Test suite for StreamingClassificationEngine."""
    
    @pytest.fixture
    def mock_classification_engine(self):
        """Create a mock classification engine."""
        engine = Mock(spec=ClassificationEngine)
        engine.primary_provider = Mock()
        engine.workflow = Mock()
        engine.workflow.system_prompt = "You are a helpful assistant."
        engine.workflow.user_prompt_template = "Classify: {text}"
        engine.workflow.categories = ["positive", "negative", "neutral"]
        return engine
    
    @pytest.fixture
    def streaming_engine(self, mock_classification_engine):
        """Create a streaming classification engine."""
        return StreamingClassificationEngine(
            classification_engine=mock_classification_engine,
            max_concurrent_streams=5,
            buffer_size=100,
            enable_metrics=True
        )
    
    @pytest.fixture
    def streaming_request(self):
        """Create a test streaming request."""
        return StreamingRequest(
            text="This is a test message for classification.",
            categories=["positive", "negative", "neutral"],
            stream_id="test_stream_001"
        )
    
    def test_streaming_engine_initialization(self, mock_classification_engine):
        """Test streaming engine initialization."""
        engine = StreamingClassificationEngine(
            classification_engine=mock_classification_engine,
            max_concurrent_streams=10,
            buffer_size=500,
            enable_metrics=True
        )
        
        assert engine.classification_engine == mock_classification_engine
        assert engine.max_concurrent_streams == 10
        assert engine.buffer_size == 500
        assert engine.enable_metrics is True
        assert len(engine.active_streams) == 0
        assert engine.stream_semaphore._value == 10
    
    def test_stream_registration(self, streaming_engine, streaming_request):
        """Test stream registration and unregistration."""
        stream_id = "test_stream"
        
        # Register stream
        streaming_engine._register_stream(stream_id, streaming_request)
        
        assert stream_id in streaming_engine.active_streams
        assert streaming_engine.active_streams[stream_id]["request_id"] == streaming_request.id
        assert streaming_engine.metrics.active_streams == 1
        assert streaming_engine.metrics.total_requests == 1
        
        # Unregister stream
        streaming_engine._unregister_stream(stream_id)
        
        assert stream_id not in streaming_engine.active_streams
        assert streaming_engine.metrics.active_streams == 0
        assert streaming_engine.metrics.total_responses == 1
    
    def test_metrics_update(self, streaming_engine):
        """Test metrics update functionality."""
        initial_time = streaming_engine.metrics.average_response_time_ms
        
        # Update metrics with processing time
        streaming_engine._update_metrics(150.0)
        
        assert streaming_engine.metrics.average_response_time_ms == 150.0
        
        # Update again to test averaging
        streaming_engine._update_metrics(250.0)
        
        assert streaming_engine.metrics.average_response_time_ms == 200.0  # (150 + 250) / 2
    
    @pytest.mark.asyncio
    async def test_stream_classify_with_provider_streaming(self, streaming_engine, streaming_request, mock_classification_engine):
        """Test stream classification with provider that supports streaming."""
        # Mock provider with streaming support
        mock_provider = Mock()
        mock_provider._perform_streaming_generation = AsyncMock()
        
        async def mock_streaming():
            yield "pos"
            yield "itive"
        
        mock_provider._perform_streaming_generation.return_value = mock_streaming()
        mock_classification_engine.primary_provider = mock_provider
        
        # Collect streaming responses
        responses = []
        async for response in streaming_engine.stream_classify(streaming_request):
            responses.append(response)
        
        # Verify responses
        assert len(responses) > 0
        
        # Check for progress updates
        progress_responses = [r for r in responses if r.chunk_type == "progress"]
        assert len(progress_responses) > 0
        
        # Check for classification chunks
        classification_responses = [r for r in responses if r.chunk_type == "classification"]
        assert len(classification_responses) > 0
        
        # Check for completion
        complete_responses = [r for r in responses if r.chunk_type == "complete"]
        assert len(complete_responses) == 1
    
    @pytest.mark.asyncio
    async def test_stream_classify_without_provider_streaming(self, streaming_engine, streaming_request, mock_classification_engine):
        """Test stream classification with provider that doesn't support streaming."""
        # Mock provider without streaming support
        mock_provider = Mock()
        mock_provider._perform_streaming_generation = None  # No streaming method
        mock_classification_engine.primary_provider = mock_provider
        
        # Mock classification result
        mock_result = ClassificationResult(
            primary_category="positive",
            confidence=0.85,
            categories={"positive": 0.85, "negative": 0.15},
            processing_time_ms=100.0,
            provider="test"
        )
        mock_classification_engine.classify_input = AsyncMock(return_value=mock_result)
        
        # Collect streaming responses
        responses = []
        async for response in streaming_engine.stream_classify(streaming_request):
            responses.append(response)
        
        # Verify responses
        assert len(responses) > 0
        
        # Check for progress updates
        progress_responses = [r for r in responses if r.chunk_type == "progress"]
        assert len(progress_responses) > 0
        
        # Check for final classification
        classification_responses = [r for r in responses if r.chunk_type == "classification"]
        assert len(classification_responses) > 0
        
        final_classification = classification_responses[-1]
        assert final_classification.classification["primary_category"] == "positive"
        assert final_classification.classification["confidence"] == 0.85
    
    @pytest.mark.asyncio
    async def test_stream_classify_error_handling(self, streaming_engine, streaming_request, mock_classification_engine):
        """Test error handling during stream classification."""
        # Mock provider that raises an error
        mock_provider = Mock()
        mock_provider._perform_streaming_generation = AsyncMock(side_effect=Exception("Provider error"))
        mock_classification_engine.primary_provider = mock_provider
        
        # Collect streaming responses
        responses = []
        async for response in streaming_engine.stream_classify(streaming_request):
            responses.append(response)
        
        # Verify error response
        error_responses = [r for r in responses if r.chunk_type == "error"]
        assert len(error_responses) > 0
        
        error_response = error_responses[0]
        assert "Provider error" in error_response.error
        
        # Check that metrics were updated for error
        assert streaming_engine.metrics.total_errors > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_stream_limit(self, mock_classification_engine):
        """Test concurrent stream limit enforcement."""
        # Create engine with low concurrent limit
        engine = StreamingClassificationEngine(
            classification_engine=mock_classification_engine,
            max_concurrent_streams=2,
            enable_metrics=True
        )
        
        # Mock provider
        mock_provider = Mock()
        
        async def slow_streaming():
            await asyncio.sleep(0.1)  # Simulate slow processing
            yield "result"
        
        mock_provider._perform_streaming_generation = AsyncMock(return_value=slow_streaming())
        mock_classification_engine.primary_provider = mock_provider
        
        # Create multiple requests
        requests = [
            StreamingRequest(text=f"Test message {i}", stream_id=f"stream_{i}")
            for i in range(5)
        ]
        
        # Start all streams concurrently
        tasks = [engine.stream_classify(req) for req in requests]
        
        # Collect first response from each stream
        first_responses = []
        for task in tasks:
            async for response in task:
                first_responses.append(response)
                break  # Just get the first response
        
        # Should have responses from all streams (semaphore should handle concurrency)
        assert len(first_responses) == 5
    
    def test_parse_classification_response_json(self, streaming_engine):
        """Test parsing JSON classification response."""
        json_response = '{"primary_category": "positive", "confidence": 0.9}'
        categories = ["positive", "negative", "neutral"]
        
        result = streaming_engine._parse_classification_response(json_response, categories)
        
        assert result["primary_category"] == "positive"
        assert result["confidence"] == 0.9
    
    def test_parse_classification_response_text(self, streaming_engine):
        """Test parsing text classification response."""
        text_response = "This text is clearly positive in sentiment."
        categories = ["positive", "negative", "neutral"]
        
        result = streaming_engine._parse_classification_response(text_response, categories)
        
        assert result["primary_category"] == "positive"  # Should find "positive" in text
        assert result["confidence"] > 0
        assert "raw_response" in result
    
    def test_parse_classification_response_fallback(self, streaming_engine):
        """Test parsing classification response with fallback."""
        unclear_response = "This is an unclear response without clear sentiment."
        categories = ["positive", "negative", "neutral"]
        
        result = streaming_engine._parse_classification_response(unclear_response, categories)
        
        assert result["primary_category"] in categories
        assert result["confidence"] >= 0
        assert "raw_response" in result
    
    def test_callback_management(self, streaming_engine):
        """Test progress and error callback management."""
        progress_callback = Mock()
        error_callback = Mock()
        
        # Add callbacks
        streaming_engine.add_progress_callback(progress_callback)
        streaming_engine.add_error_callback(error_callback)
        
        assert progress_callback in streaming_engine.progress_callbacks
        assert error_callback in streaming_engine.error_callbacks
    
    def test_get_metrics(self, streaming_engine):
        """Test metrics retrieval."""
        metrics = streaming_engine.get_metrics()
        
        assert hasattr(metrics, 'total_requests')
        assert hasattr(metrics, 'active_streams')
        assert hasattr(metrics, 'total_responses')
        assert hasattr(metrics, 'total_errors')
        assert hasattr(metrics, 'average_response_time_ms')
    
    def test_get_active_streams(self, streaming_engine, streaming_request):
        """Test active streams retrieval."""
        stream_id = "test_stream"
        
        # Register a stream
        streaming_engine._register_stream(stream_id, streaming_request)
        
        active_streams = streaming_engine.get_active_streams()
        
        assert stream_id in active_streams
        assert active_streams[stream_id]["request_id"] == streaming_request.id
        
        # Should return a copy, not the original
        assert active_streams is not streaming_engine.active_streams
    
    @pytest.mark.asyncio
    async def test_cleanup(self, streaming_engine, streaming_request):
        """Test streaming engine cleanup."""
        # Register some streams
        streaming_engine._register_stream("stream_1", streaming_request)
        streaming_engine._register_stream("stream_2", streaming_request)
        
        assert len(streaming_engine.active_streams) == 2
        
        # Cleanup
        await streaming_engine.cleanup()
        
        # All streams should be unregistered
        assert len(streaming_engine.active_streams) == 0
    
    @pytest.mark.asyncio
    async def test_stream_with_custom_categories(self, streaming_engine, mock_classification_engine):
        """Test streaming with custom categories."""
        custom_request = StreamingRequest(
            text="This is a business-related message.",
            categories=["business", "personal", "technical"],
            stream_id="custom_stream"
        )
        
        # Mock provider without streaming
        mock_provider = Mock()
        mock_provider._perform_streaming_generation = None
        mock_classification_engine.primary_provider = mock_provider
        
        # Mock classification result
        mock_result = ClassificationResult(
            primary_category="business",
            confidence=0.92,
            categories={"business": 0.92, "personal": 0.05, "technical": 0.03},
            processing_time_ms=120.0,
            provider="test"
        )
        mock_classification_engine.classify_input = AsyncMock(return_value=mock_result)
        
        # Collect responses
        responses = []
        async for response in streaming_engine.stream_classify(custom_request):
            responses.append(response)
        
        # Find classification response
        classification_responses = [r for r in responses if r.chunk_type == "classification"]
        assert len(classification_responses) > 0
        
        final_classification = classification_responses[-1]
        assert final_classification.classification["primary_category"] == "business"
    
    @pytest.mark.asyncio
    async def test_stream_with_metadata(self, streaming_engine, mock_classification_engine):
        """Test streaming with metadata."""
        request_with_metadata = StreamingRequest(
            text="Test message with metadata.",
            categories=["positive", "negative", "neutral"],
            metadata={"source": "test", "priority": "high"},
            stream_id="metadata_stream"
        )
        
        # Mock provider and result
        mock_provider = Mock()
        mock_provider._perform_streaming_generation = None
        mock_classification_engine.primary_provider = mock_provider
        
        mock_result = ClassificationResult(
            primary_category="neutral",
            confidence=0.75,
            categories={"neutral": 0.75, "positive": 0.15, "negative": 0.10},
            processing_time_ms=90.0,
            provider="test"
        )
        mock_classification_engine.classify_input = AsyncMock(return_value=mock_result)
        
        # Stream classification
        responses = []
        async for response in streaming_engine.stream_classify(request_with_metadata):
            responses.append(response)
        
        # Verify that metadata was passed through (indirectly through the request)
        assert len(responses) > 0
        
        # Check that classification was performed
        classification_responses = [r for r in responses if r.chunk_type == "classification"]
        assert len(classification_responses) > 0


class TestStreamingEngineIntegration:
    """Integration tests for streaming engine."""
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_streams(self, mock_classification_engine):
        """Test multiple concurrent streams processing."""
        engine = StreamingClassificationEngine(
            classification_engine=mock_classification_engine,
            max_concurrent_streams=3,
            enable_metrics=True
        )
        
        # Mock provider
        mock_provider = Mock()
        
        async def mock_streaming():
            await asyncio.sleep(0.05)  # Small delay
            yield "positive"
        
        mock_provider._perform_streaming_generation = AsyncMock(return_value=mock_streaming())
        mock_classification_engine.primary_provider = mock_provider
        
        # Create multiple requests
        requests = [
            StreamingRequest(text=f"Message {i}", stream_id=f"concurrent_{i}")
            for i in range(5)
        ]
        
        # Process all streams concurrently
        async def process_stream(request):
            responses = []
            async for response in engine.stream_classify(request):
                responses.append(response)
            return responses
        
        # Run all streams
        results = await asyncio.gather(*[process_stream(req) for req in requests])
        
        # Verify all streams completed
        assert len(results) == 5
        for result in results:
            assert len(result) > 0  # Each stream should have responses
        
        # Check metrics
        metrics = engine.get_metrics()
        assert metrics.total_requests == 5
        assert metrics.total_responses == 5
