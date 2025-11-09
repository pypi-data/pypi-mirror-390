"""
Unit tests for Cohere provider.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from evolvishub_text_classification_llm.providers.cohere import CohereProvider
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType
from evolvishub_text_classification_llm.core.exceptions import (
    ProviderError, AuthenticationError, RateLimitError, TimeoutError
)


@pytest.fixture
def cohere_config():
    """Create a test Cohere configuration."""
    return ProviderConfig(
        provider_type=ProviderType.COHERE,
        api_key="test-api-key",
        model="command",
        max_tokens=100,
        temperature=0.7,
        timeout_seconds=30
    )


@pytest.fixture
def cohere_provider(cohere_config):
    """Create a Cohere provider instance."""
    return CohereProvider(cohere_config)


class TestCohereProvider:
    """Test cases for Cohere provider."""
    
    def test_initialization(self, cohere_provider):
        """Test provider initialization."""
        assert cohere_provider.provider_type == ProviderType.COHERE
        assert cohere_provider.config.model == "command"
        assert not cohere_provider.supports_function_calling
        assert cohere_provider.supports_streaming
        assert cohere_provider.supports_embeddings
        assert cohere_provider.supports_classification
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, cohere_provider):
        """Test successful provider initialization."""
        with patch('cohere.Client') as mock_client, \
             patch('cohere.AsyncClient') as mock_async_client:
            
            # Mock the test connection
            mock_async_instance = AsyncMock()
            mock_async_client.return_value = mock_async_instance
            mock_async_instance.generate.return_value = Mock(
                generations=[Mock(text="test response")]
            )
            
            await cohere_provider.initialize()
            
            assert cohere_provider.is_initialized
            mock_client.assert_called_once()
            mock_async_client.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialization_missing_library(self, cohere_provider):
        """Test initialization with missing Cohere library."""
        with patch('cohere.Client', side_effect=ImportError("No module named 'cohere'")):
            with pytest.raises(ProviderError) as exc_info:
                await cohere_provider.initialize()
            
            assert "Cohere library not installed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_initialization_invalid_api_key(self, cohere_provider):
        """Test initialization with invalid API key."""
        with patch('cohere.Client') as mock_client, \
             patch('cohere.AsyncClient') as mock_async_client:
            
            mock_async_instance = AsyncMock()
            mock_async_client.return_value = mock_async_instance
            mock_async_instance.generate.side_effect = Exception("invalid api key")
            
            with pytest.raises(AuthenticationError):
                await cohere_provider.initialize()
    
    @pytest.mark.asyncio
    async def test_generate_success(self, cohere_provider):
        """Test successful text generation."""
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.return_value = Mock(
                generations=[Mock(text="I'm doing well, thank you!")]
            )
            cohere_provider._initialized = True
            
            result = await cohere_provider.generate(messages)
            
            assert result == "I'm doing well, thank you!"
            mock_client.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_rate_limit(self, cohere_provider):
        """Test generation with rate limit error."""
        messages = [{"role": "user", "content": "Test"}]
        
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.side_effect = Exception("rate limit exceeded")
            cohere_provider._initialized = True
            
            with pytest.raises(RateLimitError):
                await cohere_provider.generate(messages)
    
    @pytest.mark.asyncio
    async def test_generate_timeout(self, cohere_provider):
        """Test generation with timeout error."""
        messages = [{"role": "user", "content": "Test"}]
        
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.side_effect = Exception("timeout")
            cohere_provider._initialized = True
            
            with pytest.raises(TimeoutError):
                await cohere_provider.generate(messages)
    
    @pytest.mark.asyncio
    async def test_generate_stream(self, cohere_provider):
        """Test streaming text generation."""
        messages = [{"role": "user", "content": "Tell me a story"}]
        
        async def mock_stream():
            for token in ["Once", " upon", " a", " time"]:
                yield Mock(text=token)
        
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.return_value = mock_stream()
            cohere_provider._initialized = True
            
            result = []
            async for chunk in cohere_provider.generate_stream(messages):
                result.append(chunk)
            
            assert result == ["Once", " upon", " a", " time"]
    
    def test_messages_to_prompt(self, cohere_provider):
        """Test message to prompt conversion."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        prompt = cohere_provider._messages_to_prompt(messages)
        
        expected = (
            "System: You are a helpful assistant.\n\n"
            "Human: Hello!\n\n"
            "Assistant: Hi there!\n\n"
            "Human: How are you?\n\n"
            "Assistant:"
        )
        
        assert prompt == expected
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, cohere_provider):
        """Test health check when provider is healthy."""
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.return_value = Mock(
                generations=[Mock(text="healthy")]
            )
            cohere_provider._initialized = True
            
            health = await cohere_provider.health_check()
            
            assert health["status"] == "healthy"
            assert "response_time_ms" in health
            assert health["model"] == "command"
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, cohere_provider):
        """Test health check when provider is unhealthy."""
        with patch.object(cohere_provider, '_async_client') as mock_client:
            mock_client.generate.side_effect = Exception("Connection failed")
            cohere_provider._initialized = True
            
            health = await cohere_provider.health_check()
            
            assert health["status"] == "unhealthy"
            assert "Connection failed" in health["message"]
    
    @pytest.mark.asyncio
    async def test_health_check_not_initialized(self, cohere_provider):
        """Test health check when provider is not initialized."""
        health = await cohere_provider.health_check()
        
        assert health["status"] == "unhealthy"
        assert "not initialized" in health["message"]
    
    @pytest.mark.asyncio
    async def test_get_usage_stats(self, cohere_provider):
        """Test getting usage statistics."""
        cohere_provider._request_count = 10
        cohere_provider._token_count = 1000
        cohere_provider._error_count = 2
        cohere_provider._total_cost = 0.05
        
        stats = await cohere_provider.get_usage_stats()
        
        assert stats["provider"] == "cohere"
        assert stats["model"] == "command"
        assert stats["requests"] == 10
        assert stats["tokens"] == 1000
        assert stats["errors"] == 2
        assert stats["total_cost_usd"] == 0.05
        assert "uptime_hours" in stats
        assert "avg_response_time_ms" in stats
    
    @pytest.mark.asyncio
    async def test_estimate_cost(self, cohere_provider):
        """Test cost estimation."""
        text = "This is a test text for cost estimation."
        
        cost = await cohere_provider.estimate_cost(text)
        
        assert isinstance(cost, float)
        assert cost > 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, cohere_provider):
        """Test provider cleanup."""
        cohere_provider._async_client = Mock()
        cohere_provider._client = Mock()
        cohere_provider._initialized = True
        
        await cohere_provider.cleanup()
        
        assert cohere_provider._async_client is None
        assert cohere_provider._client is None
        assert not cohere_provider._initialized
    
    def test_track_request(self, cohere_provider):
        """Test request tracking."""
        initial_count = cohere_provider._request_count
        
        cohere_provider._track_request(0.5)  # 500ms response time
        
        assert cohere_provider._request_count == initial_count + 1
        assert len(cohere_provider._response_times) == 1
        assert cohere_provider._response_times[0] == 500.0
    
    def test_track_error(self, cohere_provider):
        """Test error tracking."""
        initial_error_count = cohere_provider._error_count
        
        cohere_provider._track_error()
        
        assert cohere_provider._error_count == initial_error_count + 1
        assert cohere_provider._consecutive_errors == 1
    
    def test_track_multiple_errors(self, cohere_provider):
        """Test tracking multiple consecutive errors."""
        # Track multiple errors
        for _ in range(6):
            cohere_provider._track_error()
        
        assert cohere_provider._consecutive_errors == 6
        assert cohere_provider._health_status == "unhealthy"
    
    def test_model_limits(self, cohere_provider):
        """Test model token limits."""
        assert "command" in cohere_provider._model_limits
        assert "command-r" in cohere_provider._model_limits
        assert cohere_provider._model_limits["command"] == 4096
        assert cohere_provider._model_limits["command-r"] == 128000
    
    def test_pricing_info(self, cohere_provider):
        """Test pricing information."""
        assert "command" in cohere_provider._pricing
        assert "input" in cohere_provider._pricing["command"]
        assert "output" in cohere_provider._pricing["command"]
        assert isinstance(cohere_provider._pricing["command"]["input"], float)
        assert isinstance(cohere_provider._pricing["command"]["output"], float)
