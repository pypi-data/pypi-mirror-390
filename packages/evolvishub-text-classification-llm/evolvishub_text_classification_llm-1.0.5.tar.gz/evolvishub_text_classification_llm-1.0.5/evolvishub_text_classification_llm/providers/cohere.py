"""
Cohere provider implementation.

This module implements the Cohere LLM provider with support for Command models,
embeddings, classification, and comprehensive error handling.
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


@register_provider("cohere")
class CohereProvider(BaseLLMProvider):
    """
    Cohere provider implementation.
    
    Supports Command models, embeddings, and classification with features like
    streaming, comprehensive error handling, and usage tracking.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Cohere provider."""
        super().__init__(config)
        self._client = None
        self._async_client = None
        
        # Cohere-specific settings
        self.supports_function_calling = False  # Cohere doesn't support function calling yet
        self.supports_streaming = True
        self.supports_embeddings = True
        self.supports_classification = True
        
        # Model-specific token limits
        self._model_limits = {
            "command": 4096,
            "command-light": 4096,
            "command-nightly": 4096,
            "command-r": 128000,
            "command-r-plus": 128000,
        }
        
        # Pricing per 1K tokens (approximate)
        self._pricing = {
            "command": {"input": 0.0015, "output": 0.002},
            "command-light": {"input": 0.0003, "output": 0.0006},
            "command-nightly": {"input": 0.0015, "output": 0.002},
            "command-r": {"input": 0.0005, "output": 0.0015},
            "command-r-plus": {"input": 0.003, "output": 0.015},
        }
    
    async def _perform_initialization(self):
        """Initialize Cohere client."""
        try:
            import cohere
            
            # Initialize client
            self._client = cohere.Client(
                api_key=self.config.api_key,
                timeout=self.config.timeout_seconds
            )
            
            # Initialize async client
            self._async_client = cohere.AsyncClient(
                api_key=self.config.api_key,
                timeout=self.config.timeout_seconds
            )
            
            # Test connection with a simple API call
            await self._test_connection()
            
        except ImportError:
            raise ModelLoadError(
                "Cohere library not installed. Install with: pip install cohere",
                provider="cohere"
            )
        except Exception as e:
            if "invalid api key" in str(e).lower():
                raise AuthenticationError(
                    "Invalid Cohere API key",
                    provider="cohere",
                    cause=e
                )
            raise ProviderError(
                f"Failed to initialize Cohere client: {e}",
                provider="cohere",
                cause=e
            )
    
    async def _test_connection(self):
        """Test the connection to Cohere API."""
        try:
            # Make a simple API call to test authentication
            response = await self._async_client.generate(
                model=self.config.model,
                prompt="Test",
                max_tokens=1,
                temperature=0
            )
            logger.debug("Cohere connection test successful")
        except Exception as e:
            raise ProviderError(
                f"Cohere connection test failed: {e}",
                provider="cohere",
                cause=e
            )
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text response using Cohere."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert messages to Cohere format
            prompt = self._messages_to_prompt(messages)
            
            # Prepare generation parameters
            generation_params = {
                "model": self.config.model,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                "k": kwargs.get("top_k", getattr(self.config, "top_k", 0)),
                "stop_sequences": kwargs.get("stop", []),
                "return_likelihoods": "NONE"
            }
            
            # Make API call
            start_time = asyncio.get_event_loop().time()
            response = await self._async_client.generate(**generation_params)
            end_time = asyncio.get_event_loop().time()
            
            # Track metrics
            self._track_request(end_time - start_time)
            
            # Extract response text
            if response.generations and len(response.generations) > 0:
                return response.generations[0].text.strip()
            else:
                raise ProviderError(
                    "No response generated from Cohere",
                    provider="cohere"
                )
                
        except Exception as e:
            self._track_error()
            if "rate limit" in str(e).lower():
                raise RateLimitError(
                    f"Cohere rate limit exceeded: {e}",
                    provider="cohere",
                    retry_after=60,
                    cause=e
                )
            elif "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Cohere request timed out: {e}",
                    provider="cohere",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            elif "invalid api key" in str(e).lower():
                raise AuthenticationError(
                    "Invalid Cohere API key",
                    provider="cohere",
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Cohere generation failed: {e}",
                    provider="cohere",
                    cause=e
                )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming text response using Cohere."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert messages to Cohere format
            prompt = self._messages_to_prompt(messages)
            
            # Prepare generation parameters
            generation_params = {
                "model": self.config.model,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                "k": kwargs.get("top_k", getattr(self.config, "top_k", 0)),
                "stop_sequences": kwargs.get("stop", []),
                "stream": True
            }
            
            # Make streaming API call
            start_time = asyncio.get_event_loop().time()
            
            async for token in self._async_client.generate(**generation_params):
                if hasattr(token, 'text') and token.text:
                    yield token.text
            
            end_time = asyncio.get_event_loop().time()
            self._track_request(end_time - start_time)
            
        except Exception as e:
            self._track_error()
            if "rate limit" in str(e).lower():
                raise RateLimitError(
                    f"Cohere streaming rate limit exceeded: {e}",
                    provider="cohere",
                    retry_after=60,
                    cause=e
                )
            elif "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Cohere streaming request timed out: {e}",
                    provider="cohere",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Cohere streaming failed: {e}",
                    provider="cohere",
                    cause=e
                )
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Cohere prompt format."""
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
        
        # Add final prompt for assistant response
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
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
            await self._async_client.generate(
                model=self.config.model,
                prompt="Health check",
                max_tokens=1,
                temperature=0
            )
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "message": "Provider is operational",
                "response_time_ms": response_time,
                "model": self.config.model,
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
            "provider": "cohere",
            "model": self.config.model,
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
            # Cohere client doesn't require explicit cleanup
            self._async_client = None
        
        if self._client:
            self._client = None
        
        self._initialized = False
        logger.info("Cohere provider cleaned up")
    
    def _track_request(self, response_time: float):
        """Track request metrics."""
        self._request_count += 1
        self._last_request_time = asyncio.get_event_loop().time()
        
        # Track response time
        response_time_ms = response_time * 1000
        self._response_times.append(response_time_ms)
        if len(self._response_times) > self._max_response_times:
            self._response_times.pop(0)
    
    def _track_error(self):
        """Track error metrics."""
        self._error_count += 1
        self._consecutive_errors += 1
        
        # Update health status based on error rate
        if self._consecutive_errors > 5:
            self._health_status = "unhealthy"
        elif self._consecutive_errors > 2:
            self._health_status = "degraded"
