"""
Mistral AI Provider Implementation

This module provides integration with Mistral AI's language models for text classification.
Supports all Mistral models including mistral-tiny, mistral-small, mistral-medium, and mistral-large.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import time

try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    from mistralai.async_client import MistralAsyncClient
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

from ..core.schemas import ProviderConfig, ProviderType
from ..core.exceptions import ProviderError, ConfigurationError
from .base import BaseLLMProvider
from .factory import register_provider


logger = logging.getLogger(__name__)


@register_provider("mistral")
class MistralProvider(BaseLLMProvider):
    """
    Mistral AI provider for text classification.
    
    Supports all Mistral models with enterprise features including:
    - mistral-tiny: Fast and cost-effective for simple tasks
    - mistral-small: Balanced performance and cost
    - mistral-medium: High-quality results for complex tasks
    - mistral-large: Best performance for demanding applications
    
    Features:
    - Async/await support
    - Streaming responses
    - Rate limiting and retry logic
    - Cost estimation
    - Health monitoring
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Mistral provider."""
        if not MISTRAL_AVAILABLE:
            raise ConfigurationError(
                "Mistral AI package not installed. Install with: pip install mistralai"
            )
        
        super().__init__(config)
        self.provider_type = "mistral"
        self.client: Optional[MistralAsyncClient] = None
        self.sync_client: Optional[MistralClient] = None
        
        # Mistral-specific configuration
        self.api_key = config.api_key
        self.model = config.model or "mistral-small"
        self.temperature = config.temperature or 0.1
        self.max_tokens = config.max_tokens or 500
        self.top_p = getattr(config, 'top_p', 1.0)
        
        # Validate model
        self._validate_model()
        
        # Cost estimation (approximate USD per 1K tokens)
        self.cost_per_1k_tokens = self._get_model_cost()
    
    def _validate_model(self):
        """Validate the specified Mistral model."""
        supported_models = [
            "mistral-tiny",
            "mistral-small", 
            "mistral-medium",
            "mistral-large",
            "mistral-7b-instruct",
            "mistral-8x7b-instruct",
            "mistral-8x22b-instruct"
        ]
        
        if self.model not in supported_models:
            logger.warning(f"Model {self.model} not in known supported models: {supported_models}")
    
    def _get_model_cost(self) -> float:
        """Get approximate cost per 1K tokens for the model."""
        cost_mapping = {
            "mistral-tiny": 0.00025,
            "mistral-small": 0.0006,
            "mistral-medium": 0.0027,
            "mistral-large": 0.008,
            "mistral-7b-instruct": 0.00025,
            "mistral-8x7b-instruct": 0.0007,
            "mistral-8x22b-instruct": 0.002
        }
        return cost_mapping.get(self.model, 0.001)  # Default estimate
    
    async def _perform_initialization(self):
        """Initialize Mistral client."""
        try:
            if not self.api_key:
                raise ConfigurationError("Mistral API key is required")
            
            # Initialize async client
            self.client = MistralAsyncClient(api_key=self.api_key)
            
            # Initialize sync client for non-async operations
            self.sync_client = MistralClient(api_key=self.api_key)
            
            logger.info(f"Mistral provider initialized with model: {self.model}")
            
        except Exception as e:
            raise ProviderError(f"Failed to initialize Mistral provider: {e}")
    
    async def _perform_generation(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Mistral API."""
        try:
            # Convert messages to Mistral format
            mistral_messages = []
            for msg in messages:
                mistral_messages.append(
                    ChatMessage(role=msg["role"], content=msg["content"])
                )
            
            # Prepare parameters
            params = {
                "model": self.model,
                "messages": mistral_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p)
            }
            
            # Make API call
            start_time = time.time()
            response = await self.client.chat(**params)
            end_time = time.time()
            
            # Extract response
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                
                # Update usage statistics
                self._update_usage_stats(
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    processing_time_ms=(end_time - start_time) * 1000,
                    success=True
                )
                
                return content
            else:
                raise ProviderError("No response generated from Mistral")
                
        except Exception as e:
            self._update_usage_stats(success=False)
            if "rate limit" in str(e).lower():
                raise ProviderError(f"Mistral rate limit exceeded: {e}")
            elif "authentication" in str(e).lower():
                raise ProviderError(f"Mistral authentication failed: {e}")
            else:
                raise ProviderError(f"Mistral generation failed: {e}")
    
    async def _perform_streaming_generation(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Mistral API."""
        try:
            # Convert messages to Mistral format
            mistral_messages = []
            for msg in messages:
                mistral_messages.append(
                    ChatMessage(role=msg["role"], content=msg["content"])
                )
            
            # Prepare parameters for streaming
            params = {
                "model": self.model,
                "messages": mistral_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "stream": True
            }
            
            # Make streaming API call
            start_time = time.time()
            total_tokens = 0
            
            async for chunk in await self.client.chat_stream(**params):
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        total_tokens += 1  # Approximate token count
                        yield delta.content
            
            end_time = time.time()
            
            # Update usage statistics
            self._update_usage_stats(
                tokens_used=total_tokens,
                processing_time_ms=(end_time - start_time) * 1000,
                success=True
            )
            
        except Exception as e:
            self._update_usage_stats(success=False)
            raise ProviderError(f"Mistral streaming failed: {e}")
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check for Mistral provider."""
        try:
            # Simple test message
            test_messages = [
                {"role": "user", "content": "Hello, this is a health check."}
            ]
            
            start_time = time.time()
            response = await self._perform_generation(test_messages)
            end_time = time.time()
            
            return {
                "status": "healthy",
                "response_time_ms": (end_time - start_time) * 1000,
                "model": self.model,
                "provider": "mistral",
                "test_response_length": len(response) if response else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model,
                "provider": "mistral"
            }
    
    async def estimate_cost(self, text: str, **kwargs) -> float:
        """Estimate cost for processing the given text."""
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(text) / 4
        
        # Add tokens for response (estimated)
        response_tokens = kwargs.get("max_tokens", self.max_tokens)
        total_tokens = estimated_tokens + response_tokens
        
        # Calculate cost
        cost = (total_tokens / 1000) * self.cost_per_1k_tokens
        return cost
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "provider": "mistral",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "supports_streaming": True,
            "supports_function_calling": False,  # Mistral doesn't support function calling yet
            "context_window": self._get_context_window(),
            "capabilities": [
                "text_generation",
                "text_classification", 
                "conversation",
                "instruction_following",
                "multilingual"
            ]
        }
    
    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        context_windows = {
            "mistral-tiny": 32000,
            "mistral-small": 32000,
            "mistral-medium": 32000,
            "mistral-large": 32000,
            "mistral-7b-instruct": 32000,
            "mistral-8x7b-instruct": 32000,
            "mistral-8x22b-instruct": 65536
        }
        return context_windows.get(self.model, 32000)
    
    async def cleanup(self):
        """Cleanup Mistral provider resources."""
        try:
            if self.client:
                # Mistral client doesn't require explicit cleanup
                self.client = None
            
            if self.sync_client:
                self.sync_client = None
                
            logger.info("Mistral provider cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during Mistral provider cleanup: {e}")
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"MistralProvider(model={self.model}, temperature={self.temperature})"


# Register the provider
def register_mistral_provider():
    """Register Mistral provider with the factory."""
    from .factory import ProviderFactory
    
    ProviderFactory.register_provider(
        "mistral",
        MistralProvider,
        {
            "description": "Mistral AI language models for text classification",
            "capabilities": [
                "text_generation",
                "text_classification",
                "streaming",
                "multilingual",
                "instruction_following"
            ],
            "supported_models": [
                "mistral-tiny",
                "mistral-small",
                "mistral-medium", 
                "mistral-large",
                "mistral-7b-instruct",
                "mistral-8x7b-instruct",
                "mistral-8x22b-instruct"
            ],
            "cost_effective": True,
            "enterprise_ready": True
        }
    )


# Auto-register when module is imported
if MISTRAL_AVAILABLE:
    register_mistral_provider()
