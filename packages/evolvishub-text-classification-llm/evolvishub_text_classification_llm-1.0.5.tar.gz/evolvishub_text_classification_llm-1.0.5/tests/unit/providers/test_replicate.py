"""
Unit tests for Replicate provider.

Tests the ReplicateProvider class functionality including:
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

from evolvishub_text_classification_llm.providers.replicate import ReplicateProvider
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType
from evolvishub_text_classification_llm.core.exceptions import ProviderError, ConfigurationError


class TestReplicateProvider:
    """Test suite for ReplicateProvider."""
    
    @pytest.fixture
    def provider_config(self) -> ProviderConfig:
        """Create a test provider configuration."""
        return ProviderConfig(
            provider_type=ProviderType.REPLICATE,
            model="meta/llama-2-7b-chat",
            api_key="test-api-token",
            temperature=0.1,
            max_tokens=200
        )
    
    @pytest.fixture
    def mock_replicate(self):
        """Create a mock Replicate module."""
        with patch('evolvishub_text_classification_llm.providers.replicate.replicate') as mock_replicate:
            yield mock_replicate
    
    def test_provider_initialization(self, provider_config):
        """Test provider initialization with valid configuration."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            assert provider.provider_type == "replicate"
            assert provider.model == "meta/llama-2-7b-chat"
            assert provider.api_token == "test-api-token"
            assert provider.temperature == 0.1
            assert provider.max_tokens == 200
    
    def test_provider_initialization_without_replicate(self, provider_config):
        """Test provider initialization when Replicate package is not available."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', False):
            with pytest.raises(ConfigurationError, match="Replicate package not installed"):
                ReplicateProvider(provider_config)
    
    def test_model_validation_valid(self, provider_config):
        """Test model validation for valid model format."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            assert provider.model == "meta/llama-2-7b-chat"
    
    def test_model_validation_invalid_format(self):
        """Test model validation for invalid model format."""
        config = ProviderConfig(
            provider_type=ProviderType.REPLICATE,
            model="invalid-model-format",  # Missing owner/model format
            api_key="test-token"
        )
        
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            with pytest.raises(ConfigurationError, match="Replicate model must be in format"):
                ReplicateProvider(config)
    
    def test_cost_estimation(self, provider_config):
        """Test cost estimation for different models."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Test known model cost
            assert provider.cost_per_1k_tokens == 0.0005  # meta/llama-2-7b-chat
            
            # Test unknown model cost
            provider_config.model = "unknown/model"
            provider = ReplicateProvider(provider_config)
            assert provider.cost_per_1k_tokens == 0.001  # default
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, provider_config, mock_replicate):
        """Test successful provider initialization."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            await provider._perform_initialization()
            
            # Check that API token was set
            assert mock_replicate.api_token == "test-api-token"
    
    @pytest.mark.asyncio
    async def test_initialization_failure_no_api_token(self, mock_replicate):
        """Test initialization failure with missing API token."""
        config = ProviderConfig(
            provider_type=ProviderType.REPLICATE,
            model="meta/llama-2-7b-chat",
            api_key="",  # Empty API token
            temperature=0.1
        )
        
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(config)
            
            with pytest.raises(ConfigurationError, match="Replicate API token is required"):
                await provider._perform_initialization()
    
    @pytest.mark.asyncio
    async def test_text_generation_success(self, provider_config, mock_replicate):
        """Test successful text generation."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock response
            mock_replicate.run.return_value = ["positive"]
            
            messages = [{"role": "user", "content": "Test message"}]
            result = await provider._perform_generation(messages)
            
            assert result == "positive"
            mock_replicate.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_text_generation_string_response(self, provider_config, mock_replicate):
        """Test text generation with string response."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock string response
            mock_replicate.run.return_value = "positive"
            
            messages = [{"role": "user", "content": "Test message"}]
            result = await provider._perform_generation(messages)
            
            assert result == "positive"
    
    @pytest.mark.asyncio
    async def test_text_generation_rate_limit_error(self, provider_config, mock_replicate):
        """Test text generation with rate limit error."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock rate limit error
            mock_replicate.run.side_effect = Exception("rate limit exceeded")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Replicate rate limit exceeded"):
                await provider._perform_generation(messages)
    
    @pytest.mark.asyncio
    async def test_text_generation_authentication_error(self, provider_config, mock_replicate):
        """Test text generation with authentication error."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock authentication error
            mock_replicate.run.side_effect = Exception("unauthorized access")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Replicate authentication failed"):
                await provider._perform_generation(messages)
    
    @pytest.mark.asyncio
    async def test_text_generation_model_not_found(self, provider_config, mock_replicate):
        """Test text generation with model not found error."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock model not found error
            mock_replicate.run.side_effect = Exception("model not found")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Replicate model not found"):
                await provider._perform_generation(messages)
    
    def test_messages_to_prompt_conversion(self, provider_config):
        """Test conversion of messages to prompt format."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
            
            prompt = provider._messages_to_prompt(messages)
            
            assert "System: You are a helpful assistant." in prompt
            assert "Human: Hello" in prompt
            assert "Assistant: Hi there!" in prompt
            assert "Human: How are you?" in prompt
            assert prompt.endswith("Assistant:")
    
    @pytest.mark.asyncio
    async def test_streaming_generation_success(self, provider_config, mock_replicate):
        """Test successful streaming generation."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock prediction and streaming
            mock_prediction = Mock()
            mock_prediction.output_iterator.return_value = iter(["pos", "itive"])
            mock_replicate.predictions.create.return_value = mock_prediction
            
            messages = [{"role": "user", "content": "Test message"}]
            
            result_chunks = []
            async for chunk in provider._perform_streaming_generation(messages):
                result_chunks.append(chunk)
            
            assert result_chunks == ["pos", "itive"]
    
    @pytest.mark.asyncio
    async def test_streaming_generation_error(self, provider_config, mock_replicate):
        """Test streaming generation with error."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock streaming error
            mock_replicate.predictions.create.side_effect = Exception("Streaming failed")
            
            messages = [{"role": "user", "content": "Test message"}]
            
            with pytest.raises(ProviderError, match="Replicate streaming failed"):
                async for chunk in provider._perform_streaming_generation(messages):
                    pass
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, provider_config):
        """Test successful health check."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock successful generation
            with patch.object(provider, '_perform_generation', return_value="OK"):
                health = await provider._perform_health_check()
                
                assert health["status"] == "healthy"
                assert health["model"] == "meta/llama-2-7b-chat"
                assert health["provider"] == "replicate"
                assert "response_time_ms" in health
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, provider_config):
        """Test health check failure."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Mock failed generation
            with patch.object(provider, '_perform_generation', side_effect=Exception("Health check failed")):
                health = await provider._perform_health_check()
                
                assert health["status"] == "unhealthy"
                assert health["error"] == "Health check failed"
                assert health["model"] == "meta/llama-2-7b-chat"
                assert health["provider"] == "replicate"
    
    @pytest.mark.asyncio
    async def test_cost_estimation_method(self, provider_config):
        """Test cost estimation method."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            test_text = "This is a test message for cost estimation."
            cost = await provider.estimate_cost(test_text)
            
            # Should return a positive cost
            assert cost > 0
            assert isinstance(cost, float)
    
    def test_model_info(self, provider_config):
        """Test model information retrieval."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            info = provider.get_model_info()
            
            assert info["provider"] == "replicate"
            assert info["model"] == "meta/llama-2-7b-chat"
            assert info["supports_streaming"] is True
            assert info["supports_function_calling"] is False
            assert "capabilities" in info
            assert "context_window" in info
    
    def test_context_window_sizes(self, provider_config):
        """Test context window sizes for different models."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            # Test known model
            provider = ReplicateProvider(provider_config)
            assert provider._get_context_window() == 4096
            
            # Test CodeLlama model
            provider_config.model = "meta/codellama-7b-instruct"
            provider = ReplicateProvider(provider_config)
            assert provider._get_context_window() == 16384
            
            # Test unknown model
            provider_config.model = "unknown/model"
            provider = ReplicateProvider(provider_config)
            assert provider._get_context_window() == 4096  # default
    
    @pytest.mark.asyncio
    async def test_cleanup(self, provider_config):
        """Test provider cleanup."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            # Cleanup should not raise any errors
            await provider.cleanup()
    
    def test_string_representation(self, provider_config):
        """Test string representation of provider."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            provider = ReplicateProvider(provider_config)
            
            repr_str = repr(provider)
            assert "ReplicateProvider" in repr_str
            assert "meta/llama-2-7b-chat" in repr_str
            assert "0.1" in repr_str


class TestReplicateProviderRegistration:
    """Test Replicate provider registration."""
    
    def test_provider_registration(self):
        """Test that Replicate provider is registered correctly."""
        with patch('evolvishub_text_classification_llm.providers.replicate.REPLICATE_AVAILABLE', True):
            from evolvishub_text_classification_llm.providers.replicate import register_replicate_provider
            from evolvishub_text_classification_llm.providers.factory import ProviderFactory
            
            # Mock the factory registration
            with patch.object(ProviderFactory, 'register_provider') as mock_register:
                register_replicate_provider()
                
                mock_register.assert_called_once()
                args, kwargs = mock_register.call_args
                
                assert args[0] == "replicate"
                assert args[1] == ReplicateProvider
                assert isinstance(args[2], dict)
                assert "description" in args[2]
                assert "capabilities" in args[2]
                assert "supported_models" in args[2]


@pytest.mark.integration
class TestReplicateProviderIntegration:
    """Integration tests for Replicate provider (require actual API token)."""
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require --run-integration flag"
    )
    @pytest.mark.asyncio
    async def test_real_replicate_classification(self):
        """Test real Replicate API classification (requires API token)."""
        import os
        
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            pytest.skip("REPLICATE_API_TOKEN environment variable not set")
        
        config = ProviderConfig(
            provider_type=ProviderType.REPLICATE,
            model="meta/llama-2-7b-chat",
            api_key=api_token,
            temperature=0.1,
            max_tokens=50
        )
        
        provider = ReplicateProvider(config)
        
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
