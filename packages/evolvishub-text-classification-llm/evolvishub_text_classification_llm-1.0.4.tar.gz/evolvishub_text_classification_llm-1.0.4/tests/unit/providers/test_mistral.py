"""
Unit tests for Mistral AI provider.

Tests the MistralProvider class functionality including:
- Provider initialization and configuration
- Text generation and classification
- Streaming capabilities
- Error handling and recovery
- Cost estimation
- Health checks
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from evolvishub_text_classification_llm.providers.mistral import MistralProvider
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType
from evolvishub_text_classification_llm.core.exceptions import ProviderError, ConfigurationError


class TestMistralProvider:
    """Test suite for MistralProvider."""
    
    @pytest.fixture
    def provider_config(self) -> ProviderConfig:
        """Create a test provider configuration."""
        return ProviderConfig(
            provider_type=ProviderType.MISTRAL,
            model="mistral-small",
            api_key="test-api-key",
            temperature=0.1,
            max_tokens=200
        )
    
    @pytest.fixture
    def mock_mistral_client(self):
        """Create a mock Mistral client."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MistralAsyncClient') as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def mock_mistral_sync_client(self):
        """Create a mock Mistral sync client."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MistralClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            yield mock_instance
    
    def test_provider_initialization(self, provider_config):
        """Test provider initialization with valid configuration."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            assert provider.provider_type == "mistral"
            assert provider.model == "mistral-small"
            assert provider.api_key == "test-api-key"
            assert provider.temperature == 0.1
            assert provider.max_tokens == 200
    
    def test_provider_initialization_without_mistral(self, provider_config):
        """Test provider initialization when Mistral package is not available."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', False):
            with pytest.raises(ConfigurationError, match="Mistral AI package not installed"):
                MistralProvider(provider_config)
    
    def test_model_validation(self, provider_config):
        """Test model validation for supported models."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            # Test valid model
            provider = MistralProvider(provider_config)
            assert provider.model == "mistral-small"
            
            # Test invalid model (should log warning but not fail)
            provider_config.model = "invalid-model"
            provider = MistralProvider(provider_config)
            assert provider.model == "invalid-model"
    
    def test_cost_estimation(self, provider_config):
        """Test cost estimation for different models."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            # Test known model cost
            assert provider.cost_per_1k_tokens == 0.0006  # mistral-small
            
            # Test unknown model cost
            provider_config.model = "unknown-model"
            provider = MistralProvider(provider_config)
            assert provider.cost_per_1k_tokens == 0.001  # default
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, provider_config, mock_mistral_client, mock_mistral_sync_client):
        """Test successful provider initialization."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            await provider._perform_initialization()
            
            assert provider.client is not None
            assert provider.sync_client is not None
    
    @pytest.mark.asyncio
    async def test_initialization_failure_no_api_key(self, mock_mistral_client, mock_mistral_sync_client):
        """Test initialization failure with missing API key."""
        config = ProviderConfig(
            provider_type=ProviderType.MISTRAL,
            model="mistral-small",
            api_key="",  # Empty API key
            temperature=0.1
        )
        
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(config)
            
            with pytest.raises(ConfigurationError, match="Mistral API key is required"):
                await provider._perform_initialization()
    
    @pytest.mark.asyncio
    async def test_text_generation_success(self, provider_config, mock_mistral_client):
        """Test successful text generation."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            
            # Mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "positive"
            mock_response.usage.total_tokens = 50
            mock_mistral_client.chat.return_value = mock_response
            
            messages = [{"role": "user", "content": "Test message"}]
            result = await provider._perform_generation(messages)
            
            assert result == "positive"
            mock_mistral_client.chat.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_text_generation_no_response(self, provider_config, mock_mistral_client):
        """Test text generation with no response."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            
            # Mock empty response
            mock_response = Mock()
            mock_response.choices = []
            mock_mistral_client.chat.return_value = mock_response
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="No response generated from Mistral"):
                await provider._perform_generation(messages)
    
    @pytest.mark.asyncio
    async def test_text_generation_rate_limit_error(self, provider_config, mock_mistral_client):
        """Test text generation with rate limit error."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            
            # Mock rate limit error
            mock_mistral_client.chat.side_effect = Exception("rate limit exceeded")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Mistral rate limit exceeded"):
                await provider._perform_generation(messages)
    
    @pytest.mark.asyncio
    async def test_streaming_generation_success(self, provider_config, mock_mistral_client):
        """Test successful streaming generation."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            
            # Mock streaming response
            async def mock_stream():
                chunks = ["pos", "itive"]
                for chunk in chunks:
                    mock_chunk = Mock()
                    mock_chunk.choices = [Mock()]
                    mock_chunk.choices[0].delta.content = chunk
                    yield mock_chunk
            
            mock_mistral_client.chat_stream.return_value = mock_stream()
            
            messages = [{"role": "user", "content": "Test message"}]
            
            result_chunks = []
            async for chunk in provider._perform_streaming_generation(messages):
                result_chunks.append(chunk)
            
            assert result_chunks == ["pos", "itive"]
    
    @pytest.mark.asyncio
    async def test_streaming_generation_error(self, provider_config, mock_mistral_client):
        """Test streaming generation with error."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            
            # Mock streaming error
            mock_mistral_client.chat_stream.side_effect = Exception("Streaming failed")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Mistral streaming failed"):
                async for chunk in provider._perform_streaming_generation(messages):
                    pass
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, provider_config):
        """Test successful health check."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            # Mock successful generation
            with patch.object(provider, '_perform_generation', return_value="OK"):
                health = await provider._perform_health_check()
                
                assert health["status"] == "healthy"
                assert health["model"] == "mistral-small"
                assert health["provider"] == "mistral"
                assert "response_time_ms" in health
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, provider_config):
        """Test health check failure."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            # Mock failed generation
            with patch.object(provider, '_perform_generation', side_effect=Exception("Health check failed")):
                health = await provider._perform_health_check()
                
                assert health["status"] == "unhealthy"
                assert health["error"] == "Health check failed"
                assert health["model"] == "mistral-small"
                assert health["provider"] == "mistral"
    
    @pytest.mark.asyncio
    async def test_cost_estimation_method(self, provider_config):
        """Test cost estimation method."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            test_text = "This is a test message for cost estimation."
            cost = await provider.estimate_cost(test_text)
            
            # Should return a positive cost
            assert cost > 0
            assert isinstance(cost, float)
    
    def test_model_info(self, provider_config):
        """Test model information retrieval."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            info = provider.get_model_info()
            
            assert info["provider"] == "mistral"
            assert info["model"] == "mistral-small"
            assert info["supports_streaming"] is True
            assert info["supports_function_calling"] is False
            assert "capabilities" in info
            assert "context_window" in info
    
    def test_context_window_sizes(self, provider_config):
        """Test context window sizes for different models."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            # Test known model
            provider = MistralProvider(provider_config)
            assert provider._get_context_window() == 32000
            
            # Test unknown model
            provider_config.model = "unknown-model"
            provider = MistralProvider(provider_config)
            assert provider._get_context_window() == 32000  # default
    
    @pytest.mark.asyncio
    async def test_cleanup(self, provider_config, mock_mistral_client, mock_mistral_sync_client):
        """Test provider cleanup."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            provider.client = mock_mistral_client
            provider.sync_client = mock_mistral_sync_client
            
            await provider.cleanup()
            
            assert provider.client is None
            assert provider.sync_client is None
    
    def test_string_representation(self, provider_config):
        """Test string representation of provider."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            provider = MistralProvider(provider_config)
            
            repr_str = repr(provider)
            assert "MistralProvider" in repr_str
            assert "mistral-small" in repr_str
            assert "0.1" in repr_str


class TestMistralProviderRegistration:
    """Test Mistral provider registration."""
    
    def test_provider_registration(self):
        """Test that Mistral provider is registered correctly."""
        with patch('evolvishub_text_classification_llm.providers.mistral.MISTRAL_AVAILABLE', True):
            from evolvishub_text_classification_llm.providers.mistral import register_mistral_provider
            from evolvishub_text_classification_llm.providers.factory import ProviderFactory
            
            # Mock the factory registration
            with patch.object(ProviderFactory, 'register_provider') as mock_register:
                register_mistral_provider()
                
                mock_register.assert_called_once()
                args, kwargs = mock_register.call_args
                
                assert args[0] == "mistral"
                assert args[1] == MistralProvider
                assert isinstance(args[2], dict)
                assert "description" in args[2]
                assert "capabilities" in args[2]
                assert "supported_models" in args[2]


@pytest.mark.integration
class TestMistralProviderIntegration:
    """Integration tests for Mistral provider (require actual API key)."""
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require --run-integration flag"
    )
    @pytest.mark.asyncio
    async def test_real_mistral_classification(self):
        """Test real Mistral API classification (requires API key)."""
        import os
        
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            pytest.skip("MISTRAL_API_KEY environment variable not set")
        
        config = ProviderConfig(
            provider_type=ProviderType.MISTRAL,
            model="mistral-tiny",  # Use cheapest model for testing
            api_key=api_key,
            temperature=0.1,
            max_tokens=50
        )
        
        provider = MistralProvider(config)
        
        try:
            await provider.initialize()
            
            # Test health check
            health = await provider.health_check()
            assert health["status"] == "healthy"
            
            # Test classification
            messages = [
                {"role": "user", "content": "This is a positive message about the product."}
            ]
            
            result = await provider.generate(messages)
            assert isinstance(result, str)
            assert len(result) > 0
            
        finally:
            await provider.cleanup()
