"""
Provider factory for creating LLM provider instances.

This module implements the factory pattern for creating and managing
LLM provider instances with automatic registration and configuration-driven
provider selection.
"""

import logging
from typing import Dict, Type, List, Optional
from functools import wraps

from ..core.interfaces import ILLMProvider, IProviderFactory
from ..core.schemas import ProviderConfig, ProviderType
from ..core.exceptions import ProviderError, ConfigurationError
from .base import BaseLLMProvider


logger = logging.getLogger(__name__)


def register_provider(provider_type: str):
    """
    Decorator for registering provider classes.
    
    Args:
        provider_type: Provider type identifier
        
    Example:
        @register_provider("openai")
        class OpenAIProvider(BaseLLMProvider):
            pass
    """
    def decorator(provider_class: Type[BaseLLMProvider]):
        ProviderFactory.register_provider(provider_type, provider_class)
        return provider_class
    return decorator


class ProviderFactory(IProviderFactory):
    """
    Factory for creating LLM provider instances.
    
    This factory supports automatic provider registration, configuration-driven
    provider creation, and provider capability discovery.
    """
    
    # Registry of provider classes
    _providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    # Provider metadata
    _provider_metadata: Dict[str, Dict[str, any]] = {}
    
    @classmethod
    def register_provider(
        cls, 
        provider_type: str, 
        provider_class: Type[BaseLLMProvider],
        metadata: Optional[Dict[str, any]] = None
    ):
        """
        Register a provider class.
        
        Args:
            provider_type: Provider type identifier
            provider_class: Provider implementation class
            metadata: Optional provider metadata
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise ConfigurationError(
                f"Provider class must inherit from BaseLLMProvider: {provider_class}"
            )
        
        cls._providers[provider_type] = provider_class
        cls._provider_metadata[provider_type] = metadata or {}
        
        logger.info(f"Registered provider: {provider_type} -> {provider_class.__name__}")
    
    @classmethod
    def create_provider(cls, config: ProviderConfig) -> ILLMProvider:
        """
        Create a provider instance from configuration.
        
        Args:
            config: Provider configuration
            
        Returns:
            Configured provider instance
            
        Raises:
            ProviderError: If provider type is not supported
            ConfigurationError: If configuration is invalid
        """
        provider_type = config.provider_type.value
        
        if provider_type not in cls._providers:
            # Try to auto-import provider
            cls._try_auto_import(provider_type)
        
        if provider_type not in cls._providers:
            raise ProviderError(
                f"Unsupported provider type: {provider_type}. "
                f"Supported providers: {list(cls._providers.keys())}",
                provider=provider_type
            )
        
        provider_class = cls._providers[provider_type]
        
        try:
            # Validate configuration for this provider
            cls._validate_provider_config(provider_type, config)
            
            # Create provider instance
            provider = provider_class(config)
            
            logger.info(f"Created provider instance: {provider_type} ({config.model})")
            return provider
            
        except Exception as e:
            if isinstance(e, (ProviderError, ConfigurationError)):
                raise
            raise ProviderError(
                f"Failed to create provider {provider_type}: {e}",
                provider=provider_type,
                cause=e
            )
    
    @classmethod
    def create_multiple_providers(
        cls, 
        configs: List[ProviderConfig]
    ) -> List[ILLMProvider]:
        """
        Create multiple provider instances.
        
        Args:
            configs: List of provider configurations
            
        Returns:
            List of configured provider instances
        """
        providers = []
        
        for config in configs:
            try:
                provider = cls.create_provider(config)
                providers.append(provider)
            except Exception as e:
                logger.error(f"Failed to create provider {config.provider_type}: {e}")
                # Continue with other providers
        
        return providers
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        Get list of supported provider types.
        
        Returns:
            List of provider type identifiers
        """
        # Try to auto-import all known providers
        for provider_type in ProviderType:
            cls._try_auto_import(provider_type.value)
        
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_metadata(cls, provider_type: str) -> Dict[str, any]:
        """
        Get metadata for a provider type.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Provider metadata dictionary
        """
        return cls._provider_metadata.get(provider_type, {})
    
    @classmethod
    def get_provider_capabilities(cls, provider_type: str) -> Dict[str, bool]:
        """
        Get capabilities for a provider type.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Dictionary of capabilities
        """
        if provider_type not in cls._providers:
            return {}
        
        provider_class = cls._providers[provider_type]
        
        # Check for streaming support
        has_streaming = (
            hasattr(provider_class, 'generate_stream') and
            provider_class.generate_stream != BaseLLMProvider.generate_stream
        )
        
        # Check for function calling support
        has_function_calling = hasattr(provider_class, 'supports_function_calling')
        
        # Check for multimodal support
        has_multimodal = hasattr(provider_class, 'supports_multimodal')
        
        return {
            "streaming": has_streaming,
            "function_calling": has_function_calling,
            "multimodal": has_multimodal,
            "cost_estimation": True,  # All providers support basic cost estimation
            "health_checks": True,    # All providers support health checks
        }
    
    @classmethod
    def is_provider_available(cls, provider_type: str) -> bool:
        """
        Check if a provider type is available.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            True if provider is available
        """
        if provider_type in cls._providers:
            return True
        
        # Try to auto-import
        cls._try_auto_import(provider_type)
        return provider_type in cls._providers
    
    @classmethod
    def get_recommended_provider(
        cls, 
        requirements: Optional[Dict[str, any]] = None
    ) -> Optional[str]:
        """
        Get recommended provider based on requirements.
        
        Args:
            requirements: Dictionary of requirements (e.g., {"streaming": True})
            
        Returns:
            Recommended provider type or None
        """
        if not requirements:
            # Return default provider if available
            for provider_type in ["openai", "anthropic", "google"]:
                if cls.is_provider_available(provider_type):
                    return provider_type
            return None
        
        # Score providers based on requirements
        provider_scores = {}
        
        for provider_type in cls.get_supported_providers():
            capabilities = cls.get_provider_capabilities(provider_type)
            score = 0
            
            for requirement, required_value in requirements.items():
                if requirement in capabilities:
                    if capabilities[requirement] == required_value:
                        score += 1
                    elif required_value and not capabilities[requirement]:
                        score -= 2  # Penalty for missing required capability
            
            provider_scores[provider_type] = score
        
        # Return provider with highest score
        if provider_scores:
            return max(provider_scores, key=provider_scores.get)
        
        return None
    
    @classmethod
    def _try_auto_import(cls, provider_type: str):
        """
        Try to automatically import a provider module.
        
        Args:
            provider_type: Provider type to import
        """
        try:
            # Map provider types to module names
            module_map = {
                "openai": "openai",
                "anthropic": "anthropic", 
                "google": "google",
                "cohere": "cohere",
                "azure_openai": "azure_openai",
                "aws_bedrock": "bedrock",
                "huggingface": "huggingface",
                "ollama": "ollama",
                "custom": "custom"
            }
            
            if provider_type in module_map:
                module_name = module_map[provider_type]
                
                # Try to import the provider module
                import importlib
                try:
                    importlib.import_module(f"..{module_name}", __name__)
                    logger.debug(f"Auto-imported provider module: {module_name}")
                except ImportError as e:
                    logger.debug(f"Could not auto-import {module_name}: {e}")
                
        except Exception as e:
            logger.debug(f"Auto-import failed for {provider_type}: {e}")
    
    @classmethod
    def _validate_provider_config(cls, provider_type: str, config: ProviderConfig):
        """
        Validate provider-specific configuration.
        
        Args:
            provider_type: Provider type
            config: Provider configuration
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Basic validation
        if not config.model:
            raise ConfigurationError(
                f"Model name is required for provider {provider_type}",
                config_key="model"
            )
        
        # Provider-specific validation
        if provider_type in ["openai", "anthropic", "cohere", "google"]:
            if not config.api_key:
                raise ConfigurationError(
                    f"API key is required for provider {provider_type}",
                    config_key="api_key"
                )
        
        elif provider_type == "azure_openai":
            if not config.api_key or not config.api_base:
                raise ConfigurationError(
                    f"API key and API base URL are required for Azure OpenAI",
                    config_key="api_key,api_base"
                )
        
        elif provider_type == "huggingface":
            # Validate HuggingFace-specific settings
            if config.device not in ["auto", "cpu", "cuda", "mps"]:
                raise ConfigurationError(
                    f"Invalid device for HuggingFace: {config.device}",
                    config_key="device"
                )
        
        # Validate rate limiting settings
        if config.requests_per_minute and config.requests_per_minute <= 0:
            raise ConfigurationError(
                "Requests per minute must be positive",
                config_key="requests_per_minute"
            )
        
        if config.tokens_per_minute and config.tokens_per_minute <= 0:
            raise ConfigurationError(
                "Tokens per minute must be positive",
                config_key="tokens_per_minute"
            )


# Global factory instance
provider_factory = ProviderFactory()
