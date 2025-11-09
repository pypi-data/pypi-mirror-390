"""
Custom provider implementation template.

This module provides a template for implementing custom LLM providers
that can integrate with any API or local model not covered by built-in providers.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator, Callable
import aiohttp

from .base import BaseLLMProvider
from .factory import register_provider
from ..core.schemas import ProviderConfig
from ..core.exceptions import (
    ProviderError, AuthenticationError, RateLimitError, 
    TimeoutError, ModelLoadError
)


logger = logging.getLogger(__name__)


@register_provider("custom")
class CustomProvider(BaseLLMProvider):
    """
    Custom provider implementation template.
    
    This provider can be configured to work with any HTTP-based LLM API
    or custom inference endpoint. It provides a flexible foundation for
    integrating with proprietary or specialized models.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize custom provider."""
        super().__init__(config)
        self._session = None
        
        # Custom provider settings (configurable)
        self.supports_function_calling = getattr(config, 'supports_function_calling', False)
        self.supports_streaming = getattr(config, 'supports_streaming', True)
        self.supports_multimodal = getattr(config, 'supports_multimodal', False)
        
        # Custom configuration
        self.base_url = getattr(config, 'base_url', None)
        self.api_endpoint = getattr(config, 'api_endpoint', None)
        self.headers = getattr(config, 'headers', {})
        self.request_format = getattr(config, 'request_format', 'openai')  # 'openai', 'anthropic', 'custom'
        self.response_format = getattr(config, 'response_format', 'openai')
        
        # Custom request/response transformers
        self.request_transformer: Optional[Callable] = getattr(config, 'request_transformer', None)
        self.response_transformer: Optional[Callable] = getattr(config, 'response_transformer', None)
        
        # Model configuration
        self.context_length = getattr(config, 'context_length', 4096)
        self.cost_per_token = getattr(config, 'cost_per_token', 0.001)
        
        if not self.base_url:
            raise ProviderError(
                "base_url is required for custom provider",
                provider="custom"
            )
        
        if not self.api_endpoint:
            self.api_endpoint = f"{self.base_url}/v1/chat/completions"
    
    async def _perform_initialization(self):
        """Initialize custom provider client."""
        try:
            # Create HTTP session with custom headers
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                **self.headers
            }
            
            # Add authentication if API key is provided
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
            
            # Test connection
            await self._test_connection()
            
        except Exception as e:
            if self._session:
                await self._session.close()
                self._session = None
            
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise ProviderError(
                    f"Cannot connect to custom provider at {self.base_url}",
                    provider="custom",
                    cause=e
                )
            raise ProviderError(
                f"Failed to initialize custom provider: {e}",
                provider="custom",
                cause=e
            )
    
    async def _test_connection(self):
        """Test the connection to custom provider."""
        try:
            # Try a simple health check or minimal request
            test_data = self._prepare_test_request()
            
            async with self._session.post(self.api_endpoint, json=test_data) as response:
                if response.status in [200, 201]:
                    logger.debug("Custom provider connection test successful")
                elif response.status == 401:
                    raise AuthenticationError(
                        "Custom provider authentication failed",
                        provider="custom"
                    )
                else:
                    logger.warning(f"Custom provider returned status {response.status}")
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            logger.warning(f"Custom provider connection test failed: {e}")
    
    def _prepare_test_request(self) -> Dict[str, Any]:
        """Prepare a minimal test request."""
        if self.request_format == "openai":
            return {
                "model": self.config.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1,
                "temperature": 0
            }
        elif self.request_format == "anthropic":
            return {
                "model": self.config.model,
                "prompt": "Human: test\n\nAssistant:",
                "max_tokens_to_sample": 1,
                "temperature": 0
            }
        else:
            # Custom format - use transformer if available
            if self.request_transformer:
                return self.request_transformer([{"role": "user", "content": "test"}], max_tokens=1)
            else:
                return {
                    "model": self.config.model,
                    "input": "test",
                    "max_tokens": 1
                }
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text response using custom provider."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Prepare request data
            request_data = self._prepare_request(messages, **kwargs)
            
            # Make API call
            start_time = asyncio.get_event_loop().time()
            
            async with self._session.post(self.api_endpoint, json=request_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    end_time = asyncio.get_event_loop().time()
                    
                    # Track metrics
                    self._track_request(end_time - start_time)
                    
                    # Extract response
                    return self._extract_response(data)
                else:
                    error_text = await response.text()
                    raise ProviderError(
                        f"Custom provider request failed: {response.status} - {error_text}",
                        provider="custom"
                    )
                    
        except Exception as e:
            self._track_error()
            if "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Custom provider request timed out: {e}",
                    provider="custom",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            elif "rate limit" in str(e).lower() or "429" in str(e):
                raise RateLimitError(
                    f"Custom provider rate limit exceeded: {e}",
                    provider="custom",
                    retry_after=60,
                    cause=e
                )
            elif "401" in str(e) or "unauthorized" in str(e).lower():
                raise AuthenticationError(
                    "Custom provider authentication failed",
                    provider="custom",
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Custom provider generation failed: {e}",
                    provider="custom",
                    cause=e
                )
    
    def _prepare_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Prepare request data based on configured format."""
        if self.request_transformer:
            return self.request_transformer(messages, **kwargs)
        
        if self.request_format == "openai":
            return {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 1.0)),
                "stop": kwargs.get("stop", None),
            }
        elif self.request_format == "anthropic":
            prompt = self._messages_to_anthropic_prompt(messages)
            return {
                "model": self.config.model,
                "prompt": prompt,
                "max_tokens_to_sample": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                "stop_sequences": kwargs.get("stop", [])
            }
        else:
            # Generic custom format
            return {
                "model": self.config.model,
                "input": self._messages_to_simple_prompt(messages),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                **kwargs
            }
    
    def _extract_response(self, data: Dict[str, Any]) -> str:
        """Extract response text from API response."""
        if self.response_transformer:
            return self.response_transformer(data)
        
        if self.response_format == "openai":
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                if "message" in choice:
                    return choice["message"].get("content", "")
                elif "text" in choice:
                    return choice["text"]
        elif self.response_format == "anthropic":
            return data.get("completion", "").strip()
        else:
            # Try common response fields
            for field in ["response", "output", "text", "content", "result"]:
                if field in data:
                    return str(data[field]).strip()
        
        # Fallback
        return str(data).strip()
    
    def _messages_to_anthropic_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to Anthropic prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def _messages_to_simple_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to simple prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            prompt_parts.append(f"{role.title()}: {content}")
        
        return "\n".join(prompt_parts)
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming text response using custom provider."""
        if not self.supports_streaming:
            # Fallback to non-streaming
            response = await self.generate(messages, **kwargs)
            yield response
            return
        
        # For streaming, implement based on provider's streaming format
        # This is a basic implementation that can be customized
        response = await self.generate(messages, **kwargs)
        
        # Simulate streaming by yielding chunks
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]
            await asyncio.sleep(0.01)
    
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
            test_data = self._prepare_test_request()
            
            async with self._session.post(self.api_endpoint, json=test_data) as response:
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                if response.status in [200, 201]:
                    return {
                        "status": "healthy",
                        "message": "Provider is operational",
                        "response_time_ms": response_time,
                        "model": self.config.model,
                        "base_url": self.base_url,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": f"Provider returned status {response.status}",
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
            "provider": "custom",
            "model": self.config.model,
            "base_url": self.base_url,
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
        estimated_tokens = len(text) / 4
        return estimated_tokens * self.cost_per_token
    
    async def cleanup(self):
        """Cleanup provider resources."""
        if self._session:
            await self._session.close()
            self._session = None
        
        self._initialized = False
        logger.info("Custom provider cleaned up")
    
    def _track_request(self, response_time: float):
        """Track request metrics."""
        self._request_count += 1
        self._last_request_time = asyncio.get_event_loop().time()
        
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
