"""
Ollama provider implementation.

This module implements the Ollama LLM provider with support for local models
including Llama, Mistral, CodeLlama, and other models available through Ollama.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import aiohttp

from .base import BaseLLMProvider
from .factory import register_provider
from ..core.schemas import ProviderConfig
from ..core.exceptions import (
    ProviderError, AuthenticationError, RateLimitError, 
    TimeoutError, ModelLoadError
)


logger = logging.getLogger(__name__)


@register_provider("ollama")
class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider implementation.
    
    Supports local models through Ollama including Llama, Mistral, CodeLlama,
    and other open-source models with local inference capabilities.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize Ollama provider."""
        super().__init__(config)
        self._session = None
        
        # Ollama-specific settings
        self.supports_function_calling = False  # Most local models don't support function calling
        self.supports_streaming = True
        self.supports_multimodal = "llava" in config.model.lower()
        
        # Ollama configuration
        self.base_url = getattr(config, 'base_url', 'http://localhost:11434')
        self.api_endpoint = f"{self.base_url}/api"
        
        # Model-specific configurations
        self._model_configs = {
            "llama2": {"context_length": 4096, "supports_streaming": True},
            "llama2:13b": {"context_length": 4096, "supports_streaming": True},
            "llama2:70b": {"context_length": 4096, "supports_streaming": True},
            "mistral": {"context_length": 8192, "supports_streaming": True},
            "mistral:7b": {"context_length": 8192, "supports_streaming": True},
            "codellama": {"context_length": 16384, "supports_streaming": True},
            "codellama:13b": {"context_length": 16384, "supports_streaming": True},
            "llava": {"context_length": 4096, "supports_streaming": True, "multimodal": True},
            "neural-chat": {"context_length": 4096, "supports_streaming": True},
            "starling-lm": {"context_length": 8192, "supports_streaming": True},
        }
        
        # Local models have no direct cost, but we can estimate compute cost
        self._compute_cost_per_token = 0.0001  # Rough estimate for local compute
    
    async def _perform_initialization(self):
        """Initialize Ollama client."""
        try:
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self._session = aiohttp.ClientSession(timeout=timeout)
            
            # Test connection and check if model is available
            await self._test_connection()
            await self._ensure_model_available()
            
        except Exception as e:
            if self._session:
                await self._session.close()
                self._session = None
            
            if "connection" in str(e).lower() or "refused" in str(e).lower():
                raise ProviderError(
                    f"Cannot connect to Ollama server at {self.base_url}. "
                    "Make sure Ollama is running.",
                    provider="ollama",
                    cause=e
                )
            raise ProviderError(
                f"Failed to initialize Ollama client: {e}",
                provider="ollama",
                cause=e
            )
    
    async def _test_connection(self):
        """Test the connection to Ollama server."""
        try:
            async with self._session.get(f"{self.api_endpoint}/tags") as response:
                if response.status == 200:
                    logger.debug("Ollama connection test successful")
                else:
                    raise ProviderError(
                        f"Ollama server returned status {response.status}",
                        provider="ollama"
                    )
        except Exception as e:
            raise ProviderError(
                f"Ollama connection test failed: {e}",
                provider="ollama",
                cause=e
            )
    
    async def _ensure_model_available(self):
        """Ensure the specified model is available in Ollama."""
        try:
            # List available models
            async with self._session.get(f"{self.api_endpoint}/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    available_models = [model["name"] for model in data.get("models", [])]
                    
                    # Check if our model is available
                    model_found = any(
                        self.config.model in model or model.startswith(self.config.model)
                        for model in available_models
                    )
                    
                    if not model_found:
                        logger.warning(
                            f"Model {self.config.model} not found in Ollama. "
                            f"Available models: {available_models}. "
                            "Attempting to pull model..."
                        )
                        await self._pull_model()
                else:
                    raise ProviderError(
                        f"Failed to list Ollama models: {response.status}",
                        provider="ollama"
                    )
        except Exception as e:
            logger.warning(f"Could not verify model availability: {e}")
    
    async def _pull_model(self):
        """Pull the model if it's not available."""
        try:
            pull_data = {"name": self.config.model}
            async with self._session.post(
                f"{self.api_endpoint}/pull",
                json=pull_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully pulled model {self.config.model}")
                else:
                    logger.warning(f"Failed to pull model {self.config.model}")
        except Exception as e:
            logger.warning(f"Error pulling model: {e}")
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text response using Ollama."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)
            
            # Prepare generation parameters
            generate_data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                    "top_k": kwargs.get("top_k", getattr(self.config, "top_k", 40)),
                    "stop": kwargs.get("stop", [])
                }
            }
            
            # Make API call
            start_time = asyncio.get_event_loop().time()
            
            async with self._session.post(
                f"{self.api_endpoint}/generate",
                json=generate_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    end_time = asyncio.get_event_loop().time()
                    
                    # Track metrics
                    self._track_request(end_time - start_time)
                    
                    return data.get("response", "").strip()
                else:
                    error_text = await response.text()
                    raise ProviderError(
                        f"Ollama generation failed: {response.status} - {error_text}",
                        provider="ollama"
                    )
                    
        except Exception as e:
            self._track_error()
            if "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Ollama request timed out: {e}",
                    provider="ollama",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            elif "connection" in str(e).lower():
                raise ProviderError(
                    f"Ollama connection error: {e}",
                    provider="ollama",
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Ollama generation failed: {e}",
                    provider="ollama",
                    cause=e
                )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming text response using Ollama."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)
            
            # Prepare streaming parameters
            generate_data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                    "top_k": kwargs.get("top_k", getattr(self.config, "top_k", 40)),
                    "stop": kwargs.get("stop", [])
                }
            }
            
            # Make streaming API call
            start_time = asyncio.get_event_loop().time()
            
            async with self._session.post(
                f"{self.api_endpoint}/generate",
                json=generate_data
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    end_time = asyncio.get_event_loop().time()
                    self._track_request(end_time - start_time)
                else:
                    error_text = await response.text()
                    raise ProviderError(
                        f"Ollama streaming failed: {response.status} - {error_text}",
                        provider="ollama"
                    )
                    
        except Exception as e:
            self._track_error()
            if "timeout" in str(e).lower():
                raise TimeoutError(
                    f"Ollama streaming request timed out: {e}",
                    provider="ollama",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            else:
                raise ProviderError(
                    f"Ollama streaming failed: {e}",
                    provider="ollama",
                    cause=e
                )
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Ollama prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
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
            
            # Test with a simple request
            start_time = asyncio.get_event_loop().time()
            
            async with self._session.get(f"{self.api_endpoint}/tags") as response:
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                
                if response.status == 200:
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
                        "message": f"Ollama server returned status {response.status}",
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
            "provider": "ollama",
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
        # Local models have minimal cost (electricity/compute)
        estimated_tokens = len(text) / 4
        return estimated_tokens * self._compute_cost_per_token
    
    async def cleanup(self):
        """Cleanup provider resources."""
        if self._session:
            await self._session.close()
            self._session = None
        
        self._initialized = False
        logger.info("Ollama provider cleaned up")
    
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
