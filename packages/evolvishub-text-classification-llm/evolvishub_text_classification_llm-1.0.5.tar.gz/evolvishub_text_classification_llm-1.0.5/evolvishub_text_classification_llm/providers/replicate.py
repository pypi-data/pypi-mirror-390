"""
Replicate Provider Implementation

This module provides integration with Replicate's cloud-hosted model inference platform.
Supports popular models including Llama-2, CodeLlama, and other open-source models.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import time
import json

try:
    import replicate
    REPLICATE_AVAILABLE = True
except ImportError:
    REPLICATE_AVAILABLE = False

from ..core.schemas import ProviderConfig, ProviderType
from ..core.exceptions import ProviderError, ConfigurationError
from .base import BaseLLMProvider
from .factory import register_provider


logger = logging.getLogger(__name__)


@register_provider("replicate")
class ReplicateProvider(BaseLLMProvider):
    """
    Replicate provider for text classification using cloud-hosted models.
    
    Supports popular open-source models including:
    - Llama-2 variants (7B, 13B, 70B)
    - CodeLlama for code-related tasks
    - Mistral models
    - Custom fine-tuned models
    
    Features:
    - Async prediction API
    - Streaming responses
    - Custom model support
    - Cost-effective inference
    - No infrastructure management
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Replicate provider."""
        if not REPLICATE_AVAILABLE:
            raise ConfigurationError(
                "Replicate package not installed. Install with: pip install replicate"
            )
        
        super().__init__(config)
        self.provider_type = "replicate"
        
        # Replicate-specific configuration
        self.api_token = config.api_key
        self.model = config.model or "meta/llama-2-7b-chat"
        self.temperature = config.temperature or 0.1
        self.max_tokens = config.max_tokens or 500
        self.top_p = getattr(config, 'top_p', 0.9)
        self.top_k = getattr(config, 'top_k', 50)
        
        # Validate model format
        self._validate_model()
        
        # Cost estimation (varies by model)
        self.cost_per_1k_tokens = self._get_model_cost()
    
    def _validate_model(self):
        """Validate the specified Replicate model format."""
        if "/" not in self.model:
            raise ConfigurationError(
                f"Replicate model must be in format 'owner/model-name', got: {self.model}"
            )
        
        # Common supported models
        popular_models = [
            "meta/llama-2-7b-chat",
            "meta/llama-2-13b-chat", 
            "meta/llama-2-70b-chat",
            "meta/codellama-7b-instruct",
            "meta/codellama-13b-instruct",
            "meta/codellama-34b-instruct",
            "mistralai/mistral-7b-instruct-v0.1",
            "mistralai/mixtral-8x7b-instruct-v0.1"
        ]
        
        if self.model not in popular_models:
            logger.warning(f"Model {self.model} not in popular models list. Ensure it exists on Replicate.")
    
    def _get_model_cost(self) -> float:
        """Get approximate cost per 1K tokens for the model."""
        # Replicate pricing varies by model and compute time
        # These are rough estimates based on typical usage
        cost_mapping = {
            "meta/llama-2-7b-chat": 0.0005,
            "meta/llama-2-13b-chat": 0.001,
            "meta/llama-2-70b-chat": 0.0065,
            "meta/codellama-7b-instruct": 0.0005,
            "meta/codellama-13b-instruct": 0.001,
            "meta/codellama-34b-instruct": 0.0025,
            "mistralai/mistral-7b-instruct-v0.1": 0.0005,
            "mistralai/mixtral-8x7b-instruct-v0.1": 0.0027
        }
        return cost_mapping.get(self.model, 0.001)  # Default estimate
    
    async def _perform_initialization(self):
        """Initialize Replicate client."""
        try:
            if not self.api_token:
                raise ConfigurationError("Replicate API token is required")
            
            # Set API token
            replicate.api_token = self.api_token
            
            logger.info(f"Replicate provider initialized with model: {self.model}")
            
        except Exception as e:
            raise ProviderError(f"Failed to initialize Replicate provider: {e}")
    
    async def _perform_generation(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Replicate API."""
        try:
            # Convert messages to prompt format
            prompt = self._messages_to_prompt(messages)
            
            # Prepare parameters
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_new_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "top_k": kwargs.get("top_k", self.top_k)
            }
            
            # Add model-specific parameters
            if "llama" in self.model.lower():
                input_params.update({
                    "system_prompt": "You are a helpful assistant for text classification.",
                    "repetition_penalty": 1.1
                })
            
            # Make API call
            start_time = time.time()
            
            # Run prediction
            output = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: replicate.run(self.model, input=input_params)
            )
            
            end_time = time.time()
            
            # Process output
            if isinstance(output, list):
                response = "".join(output)
            elif isinstance(output, str):
                response = output
            else:
                response = str(output)
            
            # Update usage statistics
            estimated_tokens = len(prompt) / 4 + len(response) / 4
            self._update_usage_stats(
                tokens_used=int(estimated_tokens),
                processing_time_ms=(end_time - start_time) * 1000,
                success=True
            )
            
            return response.strip()
                
        except Exception as e:
            self._update_usage_stats(success=False)
            if "rate limit" in str(e).lower():
                raise ProviderError(f"Replicate rate limit exceeded: {e}")
            elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                raise ProviderError(f"Replicate authentication failed: {e}")
            elif "not found" in str(e).lower():
                raise ProviderError(f"Replicate model not found: {self.model}")
            else:
                raise ProviderError(f"Replicate generation failed: {e}")
    
    async def _perform_streaming_generation(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Replicate API."""
        try:
            # Convert messages to prompt format
            prompt = self._messages_to_prompt(messages)
            
            # Prepare parameters
            input_params = {
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_new_tokens": kwargs.get("max_tokens", self.max_tokens),
                "top_p": kwargs.get("top_p", self.top_p),
                "top_k": kwargs.get("top_k", self.top_k)
            }
            
            # Add model-specific parameters
            if "llama" in self.model.lower():
                input_params.update({
                    "system_prompt": "You are a helpful assistant for text classification.",
                    "repetition_penalty": 1.1
                })
            
            start_time = time.time()
            total_tokens = 0
            
            # Create prediction with streaming
            prediction = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: replicate.predictions.create(
                    version=self.model,
                    input=input_params,
                    stream=True
                )
            )
            
            # Stream the output
            for event in prediction.output_iterator():
                if event:
                    total_tokens += len(str(event)) / 4  # Approximate token count
                    yield str(event)
            
            end_time = time.time()
            
            # Update usage statistics
            self._update_usage_stats(
                tokens_used=int(total_tokens),
                processing_time_ms=(end_time - start_time) * 1000,
                success=True
            )
            
        except Exception as e:
            self._update_usage_stats(success=False)
            raise ProviderError(f"Replicate streaming failed: {e}")
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform health check for Replicate provider."""
        try:
            # Simple test message
            test_messages = [
                {"role": "user", "content": "Hello, this is a health check. Please respond with 'OK'."}
            ]
            
            start_time = time.time()
            response = await self._perform_generation(test_messages)
            end_time = time.time()
            
            return {
                "status": "healthy",
                "response_time_ms": (end_time - start_time) * 1000,
                "model": self.model,
                "provider": "replicate",
                "test_response_length": len(response) if response else 0
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model,
                "provider": "replicate"
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
            "provider": "replicate",
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "supports_streaming": True,
            "supports_function_calling": False,
            "context_window": self._get_context_window(),
            "capabilities": [
                "text_generation",
                "text_classification",
                "conversation",
                "instruction_following",
                "code_generation" if "code" in self.model.lower() else "general_purpose"
            ]
        }
    
    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        context_windows = {
            "meta/llama-2-7b-chat": 4096,
            "meta/llama-2-13b-chat": 4096,
            "meta/llama-2-70b-chat": 4096,
            "meta/codellama-7b-instruct": 16384,
            "meta/codellama-13b-instruct": 16384,
            "meta/codellama-34b-instruct": 16384,
            "mistralai/mistral-7b-instruct-v0.1": 32768,
            "mistralai/mixtral-8x7b-instruct-v0.1": 32768
        }
        return context_windows.get(self.model, 4096)
    
    async def cleanup(self):
        """Cleanup Replicate provider resources."""
        try:
            # Replicate client doesn't require explicit cleanup
            logger.info("Replicate provider cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during Replicate provider cleanup: {e}")
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"ReplicateProvider(model={self.model}, temperature={self.temperature})"


# Register the provider
def register_replicate_provider():
    """Register Replicate provider with the factory."""
    from .factory import ProviderFactory
    
    ProviderFactory.register_provider(
        "replicate",
        ReplicateProvider,
        {
            "description": "Replicate cloud-hosted model inference platform",
            "capabilities": [
                "text_generation",
                "text_classification",
                "streaming",
                "code_generation",
                "custom_models",
                "open_source_models"
            ],
            "supported_models": [
                "meta/llama-2-7b-chat",
                "meta/llama-2-13b-chat",
                "meta/llama-2-70b-chat",
                "meta/codellama-7b-instruct",
                "meta/codellama-13b-instruct",
                "meta/codellama-34b-instruct",
                "mistralai/mistral-7b-instruct-v0.1",
                "mistralai/mixtral-8x7b-instruct-v0.1"
            ],
            "cost_effective": True,
            "no_infrastructure": True,
            "open_source": True
        }
    )


# Auto-register when module is imported
if REPLICATE_AVAILABLE:
    register_replicate_provider()
