"""
OpenAI provider implementation.

This module implements the OpenAI LLM provider with support for GPT models,
function calling, streaming, and comprehensive error handling.
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


@register_provider("openai")
class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider implementation.
    
    Supports GPT-3.5, GPT-4, and other OpenAI models with features like
    function calling, streaming, and comprehensive error handling.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        self._client = None
        self._async_client = None
        
        # OpenAI-specific settings
        self.supports_function_calling = True
        self.supports_streaming = True
        self.supports_multimodal = config.model.startswith("gpt-4") and "vision" in config.model
        self.supports_classification = True
        
        # Model-specific token limits
        self._model_limits = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-preview": 128000,
        }
    
    async def _perform_initialization(self):
        """Initialize OpenAI client."""
        try:
            # Import OpenAI library
            try:
                import openai
                from openai import AsyncOpenAI
            except ImportError:
                raise ModelLoadError(
                    "OpenAI library not installed. Install with: pip install openai",
                    provider=self.provider_type
                )
            
            # Validate configuration
            if not self.config.api_key:
                raise AuthenticationError(
                    "OpenAI API key is required",
                    provider=self.provider_type
                )
            
            # Create async client
            client_kwargs = {
                "api_key": self.config.api_key,
                "timeout": self.config.timeout_seconds,
                "max_retries": self.config.max_retries,
            }
            
            if self.config.api_base:
                client_kwargs["base_url"] = self.config.api_base
            
            if self.config.organization:
                client_kwargs["organization"] = self.config.organization
            
            self._async_client = AsyncOpenAI(**client_kwargs)
            
            # Test authentication with a simple request
            await self._test_authentication()
            
            logger.info(f"OpenAI provider initialized with model: {self.config.model}")
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, ModelLoadError)):
                raise
            raise ModelLoadError(
                f"Failed to initialize OpenAI provider: {e}",
                provider=self.provider_type,
                model=self.config.model,
                cause=e
            )
    
    async def _test_authentication(self):
        """Test OpenAI API authentication."""
        try:
            # Make a simple API call to test authentication
            response = await self._async_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                temperature=0
            )
            
            if not response.choices:
                raise AuthenticationError(
                    "Invalid response from OpenAI API",
                    provider=self.provider_type
                )
                
        except Exception as e:
            if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                raise AuthenticationError(
                    f"OpenAI authentication failed: {e}",
                    provider=self.provider_type,
                    cause=e
                )
            elif "rate_limit" in str(e).lower():
                raise RateLimitError(
                    f"Rate limit exceeded during initialization: {e}",
                    provider=self.provider_type,
                    cause=e
                )
            else:
                raise ModelLoadError(
                    f"OpenAI API test failed: {e}",
                    provider=self.provider_type,
                    cause=e
                )
    
    async def _perform_generation(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Perform OpenAI text generation."""
        try:
            # Prepare request parameters
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0),
            }
            
            # Add function calling if provided
            if "functions" in kwargs:
                request_params["functions"] = kwargs["functions"]
                if "function_call" in kwargs:
                    request_params["function_call"] = kwargs["function_call"]
            
            # Add response format if provided
            if "response_format" in kwargs:
                request_params["response_format"] = kwargs["response_format"]
            
            # Make API request
            response = await self._async_client.chat.completions.create(**request_params)
            
            # Extract response content
            if not response.choices:
                raise ProviderError(
                    "No response choices returned from OpenAI",
                    provider=self.provider_type,
                    model=self.config.model
                )
            
            choice = response.choices[0]
            
            # Handle function calling response
            if choice.message.function_call:
                return f"Function call: {choice.message.function_call.name}({choice.message.function_call.arguments})"
            
            # Handle regular text response
            content = choice.message.content
            if not content:
                raise ProviderError(
                    "Empty response content from OpenAI",
                    provider=self.provider_type,
                    model=self.config.model
                )
            
            return content.strip()
            
        except Exception as e:
            # Handle OpenAI-specific errors
            if hasattr(e, 'status_code'):
                if e.status_code == 401:
                    raise AuthenticationError(
                        f"OpenAI authentication failed: {e}",
                        provider=self.provider_type,
                        status_code=e.status_code,
                        cause=e
                    )
                elif e.status_code == 429:
                    # Extract retry-after header if available
                    retry_after = getattr(e, 'retry_after', None)
                    raise RateLimitError(
                        f"OpenAI rate limit exceeded: {e}",
                        provider=self.provider_type,
                        status_code=e.status_code,
                        retry_after=retry_after,
                        cause=e
                    )
                elif e.status_code >= 500:
                    raise ProviderError(
                        f"OpenAI server error: {e}",
                        provider=self.provider_type,
                        status_code=e.status_code,
                        cause=e
                    )
            
            # Handle timeout errors
            if "timeout" in str(e).lower():
                raise TimeoutError(
                    f"OpenAI request timeout: {e}",
                    timeout_seconds=self.config.timeout_seconds,
                    operation="text_generation",
                    cause=e
                )
            
            # Re-raise if already a provider error
            if isinstance(e, ProviderError):
                raise
            
            # Generic error handling
            raise ProviderError(
                f"OpenAI generation failed: {e}",
                provider=self.provider_type,
                model=self.config.model,
                cause=e
            )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response from OpenAI."""
        try:
            # Prepare request parameters
            request_params = {
                "model": self.config.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "stream": True,
            }
            
            # Make streaming API request
            stream = await self._async_client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            # Handle streaming errors
            logger.error(f"OpenAI streaming failed: {e}")
            
            # Fallback to non-streaming
            response = await self._perform_generation(messages, **kwargs)
            yield response
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform OpenAI-specific health check."""
        try:
            # Test with minimal request
            test_messages = [{"role": "user", "content": "Hi"}]
            
            import time
            start_time = time.time()
            
            response = await self._async_client.chat.completions.create(
                model=self.config.model,
                messages=test_messages,
                max_tokens=5,
                temperature=0
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "response_time_ms": response_time,
                "model_available": True,
                "api_accessible": True,
                "test_response_length": len(response.choices[0].message.content) if response.choices else 0
            }
            
        except Exception as e:
            raise ProviderError(f"OpenAI health check failed: {e}", cause=e)
    
    async def estimate_cost(self, text: str) -> float:
        """
        Estimate cost for OpenAI API usage.
        
        Uses OpenAI's pricing model based on token count.
        """
        # Rough token estimation (OpenAI uses ~4 chars per token)
        estimated_tokens = len(text) / 4
        
        # OpenAI pricing (as of 2024, subject to change)
        pricing = {
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},  # per 1K tokens
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32k": {"input": 0.06, "output": 0.12},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        }
        
        model_pricing = pricing.get(self.config.model, pricing["gpt-3.5-turbo"])
        
        # Estimate input + output tokens
        input_cost = (estimated_tokens / 1000) * model_pricing["input"]
        output_cost = (self.config.max_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost

    async def classify_text(
        self,
        text: str,
        categories: List[str] = None,
        include_sentiment: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced classification using OpenAI function calling or JSON mode.
        """
        import time
        import json

        start_time = time.time()

        # Default email categories if none provided
        if categories is None:
            categories = [
                "customer support", "technical support", "sales inquiry",
                "billing inquiry", "complaint", "refund request",
                "urgent communication", "emergency", "spam",
                "promotional", "internal communication",
                "positive feedback", "general inquiry"
            ]

        try:
            # Use function calling if supported
            if self.supports_function_calling():
                return await self._classify_with_function_calling(text, categories, include_sentiment, start_time)
            # Use JSON mode if supported
            elif self.supports_json_mode():
                return await self._classify_with_json_mode(text, categories, include_sentiment, start_time)
            else:
                # Fallback to base implementation
                return await super().classify_text(text, categories, include_sentiment)

        except Exception as e:
            logger.error(f"OpenAI classification failed: {e}")
            return {
                "primary_category": "general inquiry",
                "categories": {"general inquiry": 0.5},
                "confidence": 0.5,
                "sentiment": {"label": "neutral", "confidence": 0.5},
                "processing_time_ms": (time.time() - start_time) * 1000
            }

    async def _classify_with_function_calling(
        self,
        text: str,
        categories: List[str],
        include_sentiment: bool,
        start_time: float
    ) -> Dict[str, Any]:
        """Use OpenAI function calling for structured classification."""
        import time

        # Define the classification function
        classification_function = {
            "name": "classify_text",
            "description": "Classify text into categories and analyze sentiment",
            "parameters": {
                "type": "object",
                "properties": {
                    "primary_category": {
                        "type": "string",
                        "description": "The most appropriate category",
                        "enum": categories
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score between 0.0 and 1.0",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "categories": {
                        "type": "object",
                        "description": "All categories with confidence scores",
                        "additionalProperties": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0
                        }
                    },
                    "sentiment": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "enum": ["positive", "negative", "neutral"]
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0
                            }
                        },
                        "required": ["label", "confidence"]
                    }
                },
                "required": ["primary_category", "confidence", "categories"]
            }
        }

        messages = [
            {
                "role": "system",
                "content": "You are an expert text classifier. Analyze the given text and classify it into the most appropriate category."
            },
            {
                "role": "user",
                "content": f"Classify this text: {text}"
            }
        ]

        response = await self._async_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            functions=[classification_function],
            function_call={"name": "classify_text"},
            temperature=0.1
        )

        # Extract function call result
        function_call = response.choices[0].message.function_call
        if function_call and function_call.name == "classify_text":
            result = json.loads(function_call.arguments)
            result["processing_time_ms"] = (time.time() - start_time) * 1000
            return result

        # Fallback if function calling failed
        return await super().classify_text(text, categories, include_sentiment)

    async def _classify_with_json_mode(
        self,
        text: str,
        categories: List[str],
        include_sentiment: bool,
        start_time: float
    ) -> Dict[str, Any]:
        """Use OpenAI JSON mode for structured classification."""
        import time
        import json

        categories_str = ", ".join(categories)

        prompt = f"""Analyze the following text and provide a structured classification result in JSON format.

Text: "{text}"

Categories: {categories_str}

Respond with a JSON object containing:
- "primary_category": The most appropriate category
- "confidence": Confidence score (0.0-1.0)
- "categories": Object with all categories and their scores
- "sentiment": Object with "label" (positive/negative/neutral) and "confidence"

JSON response:"""

        messages = [{"role": "user", "content": prompt}]

        response = await self._async_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )

        try:
            result = json.loads(response.choices[0].message.content)
            result["processing_time_ms"] = (time.time() - start_time) * 1000
            return result
        except json.JSONDecodeError:
            return await super().classify_text(text, categories, include_sentiment)

    async def cleanup(self):
        """Cleanup OpenAI provider resources."""
        if self._async_client:
            await self._async_client.close()
            self._async_client = None
        
        await super().cleanup()
    
    def get_model_context_limit(self) -> int:
        """Get context limit for the current model."""
        return self._model_limits.get(self.config.model, 4096)
    
    def supports_function_calling(self) -> bool:
        """Check if model supports function calling."""
        return self.config.model.startswith(("gpt-3.5", "gpt-4"))
    
    def supports_json_mode(self) -> bool:
        """Check if model supports JSON mode."""
        return self.config.model in [
            "gpt-3.5-turbo-1106", "gpt-4-1106-preview", 
            "gpt-4-turbo", "gpt-4-turbo-preview"
        ]
