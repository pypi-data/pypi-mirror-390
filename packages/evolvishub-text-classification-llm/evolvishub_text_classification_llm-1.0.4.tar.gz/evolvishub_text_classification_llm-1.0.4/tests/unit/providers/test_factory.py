"""
Unit tests for provider factory.

Tests provider registration, creation, and capability discovery.
"""

import pytest
from unittest.mock import Mock, patch

from evolvishub_text_classification_llm.providers.factory import (
    ProviderFactory, register_provider
)
from evolvishub_text_classification_llm.providers.base import BaseLLMProvider
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType
from evolvishub_text_classification_llm.core.exceptions import ProviderError, ConfigurationError


class MockProvider(BaseLLMProvider):
    """Mock provider for testing."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.provider_type = "mock"
    
    async def _perform_initialization(self):
        """Mock initialization."""
        pass
    
    async def _perform_generation(self, messages, **kwargs):
        """Mock generation."""
        return "Mock response"
    
    async def _perform_health_check(self):
        """Mock health check."""
        return {"status": "healthy"}


class TestProviderRegistration:
    """Test provider registration functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Clear any existing providers
        ProviderFactory._providers.clear()
        ProviderFactory._provider_metadata.clear()
    
    def test_register_provider_decorator(self):
        """Test provider registration using decorator."""
        @register_provider("test_provider")
        class TestProvider(BaseLLMProvider):
            async def _perform_initialization(self):
                pass
            
            async def _perform_generation(self, messages, **kwargs):
                return "test response"
        
        assert "test_provider" in ProviderFactory._providers
        assert ProviderFactory._providers["test_provider"] == TestProvider
    
    def test_register_provider_method(self):
        """Test provider registration using method."""
        ProviderFactory.register_provider("mock_provider", MockProvider)
        
        assert "mock_provider" in ProviderFactory._providers
        assert ProviderFactory._providers["mock_provider"] == MockProvider
    
    def test_register_provider_with_metadata(self):
        """Test provider registration with metadata."""
        metadata = {
            "description": "Mock provider for testing",
            "capabilities": ["streaming", "function_calling"],
            "supported_models": ["mock-model-1", "mock-model-2"]
        }
        
        ProviderFactory.register_provider("mock_provider", MockProvider, metadata)
        
        assert "mock_provider" in ProviderFactory._provider_metadata
        assert ProviderFactory._provider_metadata["mock_provider"] == metadata
    
    def test_register_invalid_provider(self):
        """Test registering invalid provider class."""
        class InvalidProvider:
            """Not a BaseLLMProvider subclass."""
            pass
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory.register_provider("invalid", InvalidProvider)
        
        assert "must inherit from BaseLLMProvider" in str(exc_info.value)


class TestProviderCreation:
    """Test provider creation functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Clear and register mock provider
        ProviderFactory._providers.clear()
        ProviderFactory._provider_metadata.clear()
        ProviderFactory.register_provider("mock", MockProvider)
    
    def test_create_provider_success(self):
        """Test successful provider creation."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,  # Will be overridden
            model="mock-model",
            api_key="test-key"
        )
        
        # Mock the provider type to use our registered mock
        with patch.object(config, 'provider_type') as mock_type:
            mock_type.value = "mock"
            
            provider = ProviderFactory.create_provider(config)
            
            assert isinstance(provider, MockProvider)
            assert provider.config == config
    
    def test_create_unsupported_provider(self):
        """Test creating unsupported provider."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,  # Will be overridden
            model="test-model"
        )
        
        # Mock unsupported provider type
        with patch.object(config, 'provider_type') as mock_type:
            mock_type.value = "unsupported"
            
            with pytest.raises(ProviderError) as exc_info:
                ProviderFactory.create_provider(config)
            
            assert "Unsupported provider type: unsupported" in str(exc_info.value)
    
    def test_create_provider_with_validation_error(self):
        """Test provider creation with validation error."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="",  # Invalid empty model
            api_key="test-key"
        )
        
        with patch.object(config, 'provider_type') as mock_type:
            mock_type.value = "mock"
            
            with patch.object(ProviderFactory, '_validate_provider_config') as mock_validate:
                mock_validate.side_effect = ConfigurationError("Invalid model")
                
                with pytest.raises(ConfigurationError):
                    ProviderFactory.create_provider(config)
    
    def test_create_multiple_providers(self):
        """Test creating multiple providers."""
        configs = [
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="mock-model-1",
                api_key="key-1"
            ),
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="mock-model-2",
                api_key="key-2"
            )
        ]
        
        with patch.object(configs[0], 'provider_type') as mock_type1, \
             patch.object(configs[1], 'provider_type') as mock_type2:
            mock_type1.value = "mock"
            mock_type2.value = "mock"
            
            providers = ProviderFactory.create_multiple_providers(configs)
            
            assert len(providers) == 2
            assert all(isinstance(p, MockProvider) for p in providers)
    
    def test_create_multiple_providers_with_failures(self):
        """Test creating multiple providers with some failures."""
        configs = [
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="mock-model-1",
                api_key="key-1"
            ),
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="invalid-model",
                api_key="key-2"
            )
        ]
        
        with patch.object(configs[0], 'provider_type') as mock_type1, \
             patch.object(configs[1], 'provider_type') as mock_type2:
            mock_type1.value = "mock"
            mock_type2.value = "unsupported"  # This will fail
            
            providers = ProviderFactory.create_multiple_providers(configs)
            
            # Should return only successful providers
            assert len(providers) == 1
            assert isinstance(providers[0], MockProvider)


class TestProviderDiscovery:
    """Test provider discovery and capability functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        ProviderFactory._providers.clear()
        ProviderFactory._provider_metadata.clear()
        ProviderFactory.register_provider("mock", MockProvider)
    
    def test_get_supported_providers(self):
        """Test getting supported providers."""
        supported = ProviderFactory.get_supported_providers()
        
        assert "mock" in supported
        assert isinstance(supported, list)
    
    def test_get_provider_metadata(self):
        """Test getting provider metadata."""
        metadata = {
            "description": "Mock provider",
            "capabilities": ["streaming"]
        }
        
        ProviderFactory.register_provider("mock_with_meta", MockProvider, metadata)
        
        retrieved_metadata = ProviderFactory.get_provider_metadata("mock_with_meta")
        assert retrieved_metadata == metadata
        
        # Test nonexistent provider
        empty_metadata = ProviderFactory.get_provider_metadata("nonexistent")
        assert empty_metadata == {}
    
    def test_get_provider_capabilities(self):
        """Test getting provider capabilities."""
        capabilities = ProviderFactory.get_provider_capabilities("mock")
        
        assert isinstance(capabilities, dict)
        assert "streaming" in capabilities
        assert "function_calling" in capabilities
        assert "multimodal" in capabilities
        assert "cost_estimation" in capabilities
        assert "health_checks" in capabilities
    
    def test_get_provider_capabilities_nonexistent(self):
        """Test getting capabilities for nonexistent provider."""
        capabilities = ProviderFactory.get_provider_capabilities("nonexistent")
        assert capabilities == {}
    
    def test_is_provider_available(self):
        """Test checking provider availability."""
        assert ProviderFactory.is_provider_available("mock") is True
        assert ProviderFactory.is_provider_available("nonexistent") is False
    
    def test_get_recommended_provider_no_requirements(self):
        """Test getting recommended provider without requirements."""
        # Mock auto-import to return some providers
        with patch.object(ProviderFactory, '_try_auto_import'):
            with patch.object(ProviderFactory, 'is_provider_available') as mock_available:
                mock_available.side_effect = lambda p: p in ["openai", "mock"]
                
                recommended = ProviderFactory.get_recommended_provider()
                
                # Should return first available from default list
                assert recommended in ["openai", "mock"]
    
    def test_get_recommended_provider_with_requirements(self):
        """Test getting recommended provider with requirements."""
        requirements = {"streaming": True, "function_calling": False}
        
        with patch.object(ProviderFactory, 'get_supported_providers') as mock_supported:
            mock_supported.return_value = ["mock", "other"]
            
            with patch.object(ProviderFactory, 'get_provider_capabilities') as mock_capabilities:
                def mock_caps(provider):
                    if provider == "mock":
                        return {"streaming": True, "function_calling": False}
                    else:
                        return {"streaming": False, "function_calling": True}
                
                mock_capabilities.side_effect = mock_caps
                
                recommended = ProviderFactory.get_recommended_provider(requirements)
                
                # Should return "mock" as it matches requirements better
                assert recommended == "mock"
    
    def test_get_recommended_provider_no_matches(self):
        """Test getting recommended provider with no matches."""
        requirements = {"impossible_feature": True}
        
        with patch.object(ProviderFactory, 'get_supported_providers') as mock_supported:
            mock_supported.return_value = ["mock"]
            
            with patch.object(ProviderFactory, 'get_provider_capabilities') as mock_capabilities:
                mock_capabilities.return_value = {"streaming": True}
                
                recommended = ProviderFactory.get_recommended_provider(requirements)
                
                # Should return None when no provider matches
                assert recommended is None


class TestProviderValidation:
    """Test provider configuration validation."""
    
    def test_validate_openai_config(self):
        """Test OpenAI configuration validation."""
        # Valid config
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        # Should not raise
        ProviderFactory._validate_provider_config("openai", config)
    
    def test_validate_openai_missing_api_key(self):
        """Test OpenAI validation with missing API key."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4"
            # Missing api_key
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory._validate_provider_config("openai", config)
        
        assert "API key is required" in str(exc_info.value)
    
    def test_validate_azure_openai_config(self):
        """Test Azure OpenAI configuration validation."""
        config = ProviderConfig(
            provider_type=ProviderType.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key",
            api_base="https://test.openai.azure.com"
        )
        
        # Should not raise
        ProviderFactory._validate_provider_config("azure_openai", config)
    
    def test_validate_azure_openai_missing_base(self):
        """Test Azure OpenAI validation with missing base URL."""
        config = ProviderConfig(
            provider_type=ProviderType.AZURE_OPENAI,
            model="gpt-4",
            api_key="test-key"
            # Missing api_base
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory._validate_provider_config("azure_openai", config)
        
        assert "API base URL" in str(exc_info.value)
    
    def test_validate_huggingface_config(self):
        """Test HuggingFace configuration validation."""
        config = ProviderConfig(
            provider_type=ProviderType.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            device="cuda"
        )
        
        # Should not raise
        ProviderFactory._validate_provider_config("huggingface", config)
    
    def test_validate_huggingface_invalid_device(self):
        """Test HuggingFace validation with invalid device."""
        config = ProviderConfig(
            provider_type=ProviderType.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            device="invalid_device"
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory._validate_provider_config("huggingface", config)
        
        assert "Invalid device" in str(exc_info.value)
    
    def test_validate_missing_model(self):
        """Test validation with missing model."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="test-key"
            # Missing model
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory._validate_provider_config("openai", config)
        
        assert "Model name is required" in str(exc_info.value)
    
    def test_validate_invalid_rate_limits(self):
        """Test validation with invalid rate limits."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key",
            requests_per_minute=-1  # Invalid
        )
        
        with pytest.raises(ConfigurationError) as exc_info:
            ProviderFactory._validate_provider_config("openai", config)
        
        assert "must be positive" in str(exc_info.value)


class TestAutoImport:
    """Test automatic provider import functionality."""
    
    def test_try_auto_import_known_provider(self):
        """Test auto-import for known provider."""
        with patch('importlib.import_module') as mock_import:
            ProviderFactory._try_auto_import("openai")
            
            # Should attempt to import the openai module
            mock_import.assert_called_once()
    
    def test_try_auto_import_unknown_provider(self):
        """Test auto-import for unknown provider."""
        with patch('importlib.import_module') as mock_import:
            ProviderFactory._try_auto_import("unknown_provider")
            
            # Should not attempt import for unknown provider
            mock_import.assert_not_called()
    
    def test_try_auto_import_import_error(self):
        """Test auto-import with import error."""
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("Module not found")
            
            # Should not raise, just log the error
            ProviderFactory._try_auto_import("openai")
