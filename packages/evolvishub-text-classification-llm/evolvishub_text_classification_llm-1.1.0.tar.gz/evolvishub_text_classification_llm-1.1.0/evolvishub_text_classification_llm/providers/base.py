"""
Base LLM provider implementation.

This module provides the abstract base class and common functionality
for all LLM providers in the text classification library.
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime, timedelta

from ..core.interfaces import ILLMProvider
from ..core.schemas import ProviderConfig
from ..core.exceptions import ProviderError, RateLimitError, TimeoutError


logger = logging.getLogger(__name__)


class BaseLLMProvider(ILLMProvider):
    """
    Base implementation for LLM providers.
    
    This class provides common functionality that all providers can inherit,
    including rate limiting, retry logic, usage tracking, and health monitoring.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the base provider."""
        super().__init__(config)
        
        # Usage tracking
        self._request_count = 0
        self._token_count = 0
        self._error_count = 0
        self._total_cost = 0.0
        self._last_request_time = None
        self._start_time = datetime.utcnow()
        
        # Rate limiting
        self._request_times = []
        self._token_times = []
        
        # Health monitoring
        self._last_health_check = None
        self._health_status = "unknown"
        self._consecutive_errors = 0
        
        # Performance tracking
        self._response_times = []
        self._max_response_times = 100  # Keep last 100 response times
    
    async def initialize(self) -> bool:
        """
        Initialize the provider.
        
        Subclasses should override this method to perform provider-specific
        initialization (authentication, model loading, etc.).
        """
        try:
            await self._perform_initialization()
            self._initialized = True
            self._health_status = "healthy"
            logger.info(f"Provider {self.provider_type} initialized successfully")
            return True
        except Exception as e:
            self._health_status = "unhealthy"
            logger.error(f"Failed to initialize provider {self.provider_type}: {e}")
            raise ProviderError(
                f"Provider initialization failed: {e}",
                provider=self.provider_type,
                cause=e
            )
    
    @abstractmethod
    async def _perform_initialization(self):
        """Perform provider-specific initialization."""
        pass
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate text response with rate limiting and error handling.
        
        This method wraps the provider-specific generation with common
        functionality like rate limiting, retry logic, and usage tracking.
        """
        if not self._initialized:
            raise ProviderError(
                "Provider not initialized",
                provider=self.provider_type
            )
        
        # Check rate limits
        await self._check_rate_limits()
        
        # Track request start time
        start_time = time.time()
        
        try:
            # Perform the actual generation
            response = await self._perform_generation(messages, **kwargs)
            
            # Track successful request
            response_time = (time.time() - start_time) * 1000
            await self._track_successful_request(response, response_time)
            
            return response
            
        except Exception as e:
            # Track failed request
            await self._track_failed_request(e)
            
            # Re-raise the exception
            if isinstance(e, ProviderError):
                raise
            else:
                raise ProviderError(
                    f"Generation failed: {e}",
                    provider=self.provider_type,
                    model=self.model_name,
                    cause=e
                )
    
    @abstractmethod
    async def _perform_generation(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Perform provider-specific text generation."""
        pass
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate streaming text response.
        
        Default implementation falls back to non-streaming generation.
        Providers that support streaming should override this method.
        """
        if not self._initialized:
            raise ProviderError(
                "Provider not initialized",
                provider=self.provider_type
            )
        
        # Fallback to non-streaming
        response = await self.generate(messages, **kwargs)
        yield response
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check with caching.
        
        This method caches health check results to avoid excessive API calls.
        """
        now = datetime.utcnow()
        
        # Use cached result if recent
        if (self._last_health_check and 
            (now - self._last_health_check).seconds < 30):
            return {
                "status": self._health_status,
                "provider": self.provider_type,
                "model": self.model_name,
                "last_check": self._last_health_check.isoformat(),
                "cached": True
            }
        
        try:
            # Perform actual health check
            health_data = await self._perform_health_check()
            
            self._health_status = "healthy"
            self._consecutive_errors = 0
            self._last_health_check = now
            
            return {
                "status": "healthy",
                "provider": self.provider_type,
                "model": self.model_name,
                "last_check": now.isoformat(),
                "cached": False,
                **health_data
            }
            
        except Exception as e:
            self._health_status = "unhealthy"
            self._consecutive_errors += 1
            self._last_health_check = now
            
            logger.warning(f"Health check failed for {self.provider_type}: {e}")
            
            return {
                "status": "unhealthy",
                "provider": self.provider_type,
                "model": self.model_name,
                "last_check": now.isoformat(),
                "error": str(e),
                "consecutive_errors": self._consecutive_errors,
                "cached": False
            }
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform provider-specific health check.
        
        Default implementation performs a simple generation test.
        Providers can override this for more specific health checks.
        """
        test_messages = [{"role": "user", "content": "Hello"}]
        response = await self._perform_generation(test_messages, max_tokens=10)
        
        return {
            "test_response_length": len(response),
            "response_time_ms": self._get_average_response_time()
        }
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics."""
        uptime = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            "provider": self.provider_type,
            "model": self.model_name,
            "uptime_seconds": uptime,
            "total_requests": self._request_count,
            "total_tokens": self._token_count,
            "total_errors": self._error_count,
            "total_cost_usd": self._total_cost,
            "error_rate": self._error_count / max(self._request_count, 1),
            "requests_per_minute": self._get_requests_per_minute(),
            "tokens_per_minute": self._get_tokens_per_minute(),
            "average_response_time_ms": self._get_average_response_time(),
            "health_status": self._health_status,
            "consecutive_errors": self._consecutive_errors
        }
    
    async def estimate_cost(self, text: str) -> float:
        """
        Estimate cost for processing text.
        
        Default implementation uses token count and cost per token.
        Providers can override for more accurate cost estimation.
        """
        if not self.config.cost_per_token:
            return 0.0
        
        # Simple token estimation (rough approximation)
        estimated_tokens = len(text.split()) * 1.3  # Account for tokenization
        return estimated_tokens * self.config.cost_per_token

    async def classify_text(
        self,
        text: str,
        categories: List[str] = None,
        include_sentiment: bool = True
    ) -> Dict[str, Any]:
        """
        Perform structured text classification.

        Default implementation uses LLM generation with structured prompts.
        Providers can override for more specialized classification.

        Args:
            text: Text to classify
            categories: List of categories for classification
            include_sentiment: Whether to include sentiment analysis

        Returns:
            Structured classification result
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

        # Build classification prompt
        categories_str = ", ".join(categories)

        prompt = f"""Analyze the following text and provide a structured classification result.

Text to classify: "{text}"

Available categories: {categories_str}

Please respond with a JSON object containing:
1. "primary_category": The most appropriate category from the list
2. "confidence": A confidence score between 0.0 and 1.0
3. "categories": An object with all categories and their confidence scores
4. "sentiment": An object with "label" (positive/negative/neutral) and "confidence" score

Respond only with valid JSON, no additional text."""

        try:
            # Generate response using the provider's generation method
            messages = [{"role": "user", "content": prompt}]
            response = await self._perform_generation(messages, temperature=0.1, max_tokens=500)

            # Try to parse JSON response
            try:
                result = json.loads(response.strip())

                # Validate and normalize the result
                normalized_result = {
                    "primary_category": result.get("primary_category", "general inquiry"),
                    "categories": result.get("categories", {}),
                    "confidence": float(result.get("confidence", 0.0)),
                    "sentiment": result.get("sentiment"),
                    "processing_time_ms": (time.time() - start_time) * 1000
                }

                # Ensure confidence is in valid range
                normalized_result["confidence"] = max(0.0, min(1.0, normalized_result["confidence"]))

                return normalized_result

            except json.JSONDecodeError:
                # Fallback: parse response manually
                return self._parse_classification_response(response, categories, start_time)

        except Exception as e:
            logger.error(f"Classification failed for provider {self.provider_type}: {e}")
            return {
                "primary_category": "general inquiry",
                "categories": {"general inquiry": 0.5},
                "confidence": 0.5,
                "sentiment": {"label": "neutral", "confidence": 0.5},
                "processing_time_ms": (time.time() - start_time) * 1000
            }

    def _parse_classification_response(
        self,
        response: str,
        categories: List[str],
        start_time: float
    ) -> Dict[str, Any]:
        """
        Fallback method to parse classification response manually.
        """
        import time
        import re

        # Simple pattern matching for category extraction
        response_lower = response.lower()

        # Find the most likely category
        primary_category = "general inquiry"
        confidence = 0.5

        for category in categories:
            if category.lower() in response_lower:
                primary_category = category
                confidence = 0.7  # Higher confidence if category found in text
                break

        # Simple sentiment detection
        sentiment_label = "neutral"
        sentiment_confidence = 0.5

        positive_words = ["positive", "good", "excellent", "satisfied", "happy"]
        negative_words = ["negative", "bad", "terrible", "disappointed", "angry"]

        if any(word in response_lower for word in positive_words):
            sentiment_label = "positive"
            sentiment_confidence = 0.7
        elif any(word in response_lower for word in negative_words):
            sentiment_label = "negative"
            sentiment_confidence = 0.7

        return {
            "primary_category": primary_category,
            "categories": {primary_category: confidence},
            "confidence": confidence,
            "sentiment": {
                "label": sentiment_label,
                "confidence": sentiment_confidence
            },
            "processing_time_ms": (time.time() - start_time) * 1000
        }

    async def cleanup(self):
        """Cleanup provider resources."""
        self._initialized = False
        logger.info(f"Provider {self.provider_type} cleaned up")
    
    # Rate limiting methods
    
    async def _check_rate_limits(self):
        """Check and enforce rate limits."""
        now = time.time()
        
        # Check requests per minute limit
        if self.config.requests_per_minute:
            self._request_times = [t for t in self._request_times if now - t < 60]
            
            if len(self._request_times) >= self.config.requests_per_minute:
                wait_time = 60 - (now - self._request_times[0])
                raise RateLimitError(
                    f"Request rate limit exceeded: {self.config.requests_per_minute}/minute",
                    provider=self.provider_type,
                    retry_after=int(wait_time) + 1
                )
        
        # Check tokens per minute limit
        if self.config.tokens_per_minute:
            minute_ago = now - 60
            recent_tokens = sum(
                tokens for timestamp, tokens in self._token_times 
                if timestamp > minute_ago
            )
            
            if recent_tokens >= self.config.tokens_per_minute:
                oldest_time = min(t[0] for t in self._token_times if t[0] > minute_ago)
                wait_time = 60 - (now - oldest_time)
                raise RateLimitError(
                    f"Token rate limit exceeded: {self.config.tokens_per_minute}/minute",
                    provider=self.provider_type,
                    retry_after=int(wait_time) + 1
                )
    
    async def _track_successful_request(self, response: str, response_time_ms: float):
        """Track successful request metrics."""
        now = time.time()
        
        self._request_count += 1
        self._last_request_time = now
        
        # Track request time for rate limiting
        if self.config.requests_per_minute:
            self._request_times.append(now)
        
        # Estimate tokens and track
        estimated_tokens = len(response.split()) * 1.3
        self._token_count += estimated_tokens
        
        if self.config.tokens_per_minute:
            self._token_times.append((now, estimated_tokens))
            # Clean old entries
            self._token_times = [
                (t, tokens) for t, tokens in self._token_times 
                if now - t < 60
            ]
        
        # Track response time
        self._response_times.append(response_time_ms)
        if len(self._response_times) > self._max_response_times:
            self._response_times.pop(0)
        
        # Track cost
        if self.config.cost_per_token:
            self._total_cost += estimated_tokens * self.config.cost_per_token
    
    async def _track_failed_request(self, error: Exception):
        """Track failed request metrics."""
        self._error_count += 1
        self._consecutive_errors += 1
        
        if self._consecutive_errors > 5:
            self._health_status = "degraded"
        
        logger.warning(
            f"Request failed for {self.provider_type}: {error}",
            extra={"provider": self.provider_type, "error_count": self._error_count}
        )
    
    # Utility methods
    
    def _get_requests_per_minute(self) -> float:
        """Calculate current requests per minute."""
        now = time.time()
        recent_requests = [t for t in self._request_times if now - t < 60]
        return len(recent_requests)
    
    def _get_tokens_per_minute(self) -> float:
        """Calculate current tokens per minute."""
        now = time.time()
        recent_tokens = sum(
            tokens for timestamp, tokens in self._token_times 
            if now - timestamp < 60
        )
        return recent_tokens
    
    def _get_average_response_time(self) -> float:
        """Calculate average response time."""
        if not self._response_times:
            return 0.0
        return sum(self._response_times) / len(self._response_times)
