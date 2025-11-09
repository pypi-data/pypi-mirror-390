"""
Azure OpenAI provider implementation.

This module implements the Azure OpenAI LLM provider with support for GPT models
deployed on Azure, including enterprise features and comprehensive error handling.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

from .base import BaseLLMProvider
from .factory import register_provider
from ..core.schemas import ProviderConfig
from ..core.exceptions import (
    ProviderError, AuthenticationError, RateLimitError, 
    TimeoutError, ModelLoadError
)


logger = logging.getLogger(__name__)


@register_provider("azure_openai")
class AzureOpenAIProvider(BaseLLMProvider):
    """
    Azure OpenAI provider implementation.
    
    Supports GPT models deployed on Azure with enterprise features like
    private endpoints, managed identity, and comprehensive error handling.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Azure OpenAI provider."""
        super().__init__(config)
        self._client = None
        self._async_client = None
        
        # Azure-specific settings
        self.supports_function_calling = True
        self.supports_streaming = True
        self.supports_multimodal = "gpt-4" in config.model and "vision" in config.model
        
        # Required Azure-specific configuration
        self.azure_endpoint = getattr(config, 'azure_endpoint', None)
        self.api_version = getattr(config, 'api_version', '2024-02-15-preview')
        self.deployment_name = getattr(config, 'deployment_name', config.model)
        
        # Model-specific token limits (same as OpenAI)
        self._model_limits = {
            "gpt-35-turbo": 4096,
            "gpt-35-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
        }
        
        # Azure pricing (varies by region, these are approximate)
        self._pricing = {
            "gpt-35-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-35-turbo-16k": {"input": 0.003, "output": 0.004},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32k": {"input": 0.06, "output": 0.12},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
        }
    
    async def _perform_initialization(self):
        """Initialize Azure OpenAI client."""
        try:
            from openai import AsyncAzureOpenAI, AzureOpenAI
            
            if not self.azure_endpoint:
                raise ProviderError(
                    "Azure endpoint is required for Azure OpenAI provider",
                    provider="azure_openai"
                )
            
            # Initialize clients
            client_kwargs = {
                "api_key": self.config.api_key,
                "azure_endpoint": self.azure_endpoint,
                "api_version": self.api_version,
                "timeout": self.config.timeout_seconds
            }
            
            self._client = AzureOpenAI(**client_kwargs)
            self._async_client = AsyncAzureOpenAI(**client_kwargs)
            
            # Test connection
            await self._test_connection()
            
        except ImportError:
            raise ModelLoadError(
                "OpenAI library not installed. Install with: pip install openai",
                provider="azure_openai"
            )
        except Exception as e:
            if "invalid api key" in str(e).lower() or "unauthorized" in str(e).lower():
                raise AuthenticationError(
                    "Invalid Azure OpenAI API key or unauthorized access",
                    provider="azure_openai",
                    cause=e
                )
            raise ProviderError(
                f"Failed to initialize Azure OpenAI client: {e}",
                provider="azure_openai",
                cause=e
            )
    
    async def _test_connection(self):
        """Test the connection to Azure OpenAI API."""
        try:
            # Make a simple API call to test authentication
            response = await self._async_client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
                temperature=0
            )
            logger.debug("Azure OpenAI connection test successful")
        except Exception as e:
            raise ProviderError(
                f"Azure OpenAI connection test failed: {e}",
                provider="azure_openai",
                cause=e
            )
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text response using Azure OpenAI."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Prepare chat completion parameters
            completion_params = {
                "model": self.deployment_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 1.0)),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0),
                "stop": kwargs.get("stop", None),
            }
            
            # Add function calling if provided
            if "functions" in kwargs:
                completion_params["functions"] = kwargs["functions"]
                completion_params["function_call"] = kwargs.get("function_call", "auto")
            
            # Make API call
            start_time = asyncio.get_event_loop().time()
            response = await self._async_client.chat.completions.create(**completion_params)
            end_time = asyncio.get_event_loop().time()
            
            # Track metrics
            self._track_request(end_time - start_time, response.usage)
            
            # Extract response
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if choice.message.function_call:
                    # Return function call information
                    return f"Function call: {choice.message.function_call.name}({choice.message.function_call.arguments})"
                else:
                    return choice.message.content or ""
            else:
                raise ProviderError(
                    "No response generated from Azure OpenAI",
                    provider="azure_openai"
                )
                
        except Exception as e:
            self._track_error()
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise RateLimitError(
                    f"Azure OpenAI rate limit exceeded: {e}",
                    provider="azure_openai",
                    retry_after=60,
                    cause=e
                )
            elif "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Azure OpenAI request timed out: {e}",
                    provider="azure_openai",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            elif "unauthorized" in str(e).lower() or "invalid api key" in str(e).lower():
                raise AuthenticationError(
                    "Azure OpenAI authentication failed",
                    provider="azure_openai",
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Azure OpenAI generation failed: {e}",
                    provider="azure_openai",
                    cause=e
                )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming text response using Azure OpenAI."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Prepare streaming parameters
            completion_params = {
                "model": self.deployment_name,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 1.0)),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0),
                "stop": kwargs.get("stop", None),
                "stream": True
            }
            
            # Make streaming API call
            start_time = asyncio.get_event_loop().time()
            
            async for chunk in await self._async_client.chat.completions.create(**completion_params):
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            
            end_time = asyncio.get_event_loop().time()
            self._track_request(end_time - start_time)
            
        except Exception as e:
            self._track_error()
            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                raise RateLimitError(
                    f"Azure OpenAI streaming rate limit exceeded: {e}",
                    provider="azure_openai",
                    retry_after=60,
                    cause=e
                )
            elif "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Azure OpenAI streaming request timed out: {e}",
                    provider="azure_openai",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Azure OpenAI streaming failed: {e}",
                    provider="azure_openai",
                    cause=e
                )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health."""
        try:
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "message": "Provider not initialized",
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # Test with a minimal request
            start_time = asyncio.get_event_loop().time()
            await self._async_client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Health check"}],
                max_tokens=1,
                temperature=0
            )
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "message": "Provider is operational",
                "response_time_ms": response_time,
                "model": self.deployment_name,
                "azure_endpoint": self.azure_endpoint,
                "api_version": self.api_version,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {e}",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        uptime = (asyncio.get_event_loop().time() - self._start_time.timestamp()) / 3600
        
        return {
            "provider": "azure_openai",
            "model": self.deployment_name,
            "azure_endpoint": self.azure_endpoint,
            "api_version": self.api_version,
            "requests": self._request_count,
            "tokens": self._token_count,
            "errors": self._error_count,
            "total_cost_usd": self._total_cost,
            "uptime_hours": uptime,
            "avg_response_time_ms": sum(self._response_times) / len(self._response_times) if self._response_times else 0,
            "health_status": self._health_status,
            "last_request": self._last_request_time.isoformat() if self._last_request_time else None
        }
    
    async def estimate_cost(self, text: str) -> float:
        """Estimate cost for processing given text."""
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = len(text) / 4
        
        model_pricing = self._pricing.get(self.config.model, {"input": 0.001, "output": 0.002})
        
        # Estimate input and output tokens
        input_cost = (estimated_tokens / 1000) * model_pricing["input"]
        output_cost = (estimated_tokens * 0.5 / 1000) * model_pricing["output"]  # Assume output is 50% of input
        
        return input_cost + output_cost
    
    async def cleanup(self):
        """Cleanup provider resources."""
        if self._async_client:
            await self._async_client.close()
            self._async_client = None
        
        if self._client:
            self._client.close()
            self._client = None
        
        self._initialized = False
        logger.info("Azure OpenAI provider cleaned up")
    
    def _track_request(self, response_time: float, usage=None):
        """Track request metrics."""
        self._request_count += 1
        self._last_request_time = asyncio.get_event_loop().time()
        
        # Track tokens if usage info is available
        if usage:
            self._token_count += getattr(usage, 'total_tokens', 0)
            
            # Calculate cost if possible
            if hasattr(usage, 'prompt_tokens') and hasattr(usage, 'completion_tokens'):
                model_pricing = self._pricing.get(self.config.model, {"input": 0.001, "output": 0.002})
                input_cost = (usage.prompt_tokens / 1000) * model_pricing["input"]
                output_cost = (usage.completion_tokens / 1000) * model_pricing["output"]
                self._total_cost += input_cost + output_cost
        
        # Track response time
        response_time_ms = response_time * 1000
        self._response_times.append(response_time_ms)
        if len(self._response_times) > self._max_response_times:
            self._response_times.pop(0)
        
        # Reset consecutive errors on successful request
        self._consecutive_errors = 0
        self._health_status = "healthy"
    
    def _track_error(self):
        """Track error metrics."""
        self._error_count += 1
        self._consecutive_errors += 1
        
        # Update health status based on error rate
        if self._consecutive_errors > 5:
            self._health_status = "unhealthy"
        elif self._consecutive_errors > 2:
            self._health_status = "degraded"
