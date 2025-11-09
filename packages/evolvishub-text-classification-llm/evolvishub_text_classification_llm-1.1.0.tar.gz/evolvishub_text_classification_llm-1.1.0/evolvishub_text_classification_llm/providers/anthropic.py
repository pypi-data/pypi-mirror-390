"""
Anthropic Claude provider for text classification.

This module provides integration with Anthropic's Claude models
for text classification tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import json

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import BaseLLMProvider
from ..core.schemas import (
    ClassificationInput, ClassificationResult, ProviderConfig, ProviderType
)
from ..core.exceptions import ProviderError, ConfigurationError


logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider for text classification.
    
    Supports Claude-3 models including Haiku, Sonnet, and Opus.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Anthropic provider.
        
        Args:
            config: Provider configuration
        """
        if not ANTHROPIC_AVAILABLE:
            raise ConfigurationError(
                "Anthropic library not installed. Install with: pip install anthropic"
            )
        
        super().__init__(config)
        self.provider_type = "anthropic"  # ProviderType.ANTHROPIC
        self.client: Optional[anthropic.Anthropic] = None
        self.async_client: Optional[anthropic.AsyncAnthropic] = None
        
        # Default models
        self.default_models = [
            "claude-3-haiku-20240307",
            "claude-3-sonnet-20240229", 
            "claude-3-opus-20240229"
        ]
    
    async def _perform_initialization(self) -> bool:
        """
        Initialize the Anthropic client.
        
        Returns:
            True if initialization successful
        """
        try:
            api_key = self.config.api_key
            if not api_key:
                raise ConfigurationError("Anthropic API key is required")
            
            # Initialize clients
            self.client = anthropic.Anthropic(api_key=api_key)
            self.async_client = anthropic.AsyncAnthropic(api_key=api_key)
            
            logger.info(f"Anthropic provider initialized with model: {self.config.model}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise ProviderError(f"Anthropic initialization failed: {e}")
    
    async def _perform_generation(
        self, 
        input_data: ClassificationInput,
        categories: List[str],
        **kwargs
    ) -> ClassificationResult:
        """
        Perform text classification using Anthropic Claude.
        
        Args:
            input_data: Input text and metadata
            categories: Available classification categories
            **kwargs: Additional generation parameters
            
        Returns:
            Classification result
        """
        try:
            # Prepare the prompt
            prompt = self._build_classification_prompt(input_data.text, categories)
            
            # Prepare request parameters
            request_params = {
                "model": self.config.model or "claude-3-haiku-20240307",
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.1),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Make API call
            response = await self.async_client.messages.create(**request_params)
            
            # Parse response
            result = self._parse_classification_response(
                response.content[0].text,
                categories,
                input_data
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Anthropic classification failed: {e}")
            raise ProviderError(f"Classification failed: {e}")
    
    def _build_classification_prompt(self, text: str, categories: List[str]) -> str:
        """
        Build classification prompt for Anthropic Claude.
        
        Args:
            text: Text to classify
            categories: Available categories
            
        Returns:
            Formatted prompt
        """
        categories_str = ", ".join(categories)
        
        prompt = f"""Please classify the following text into one of these categories: {categories_str}

Text to classify:
"{text}"

Please respond with a JSON object containing:
- "category": the most appropriate category from the list
- "confidence": a confidence score between 0 and 1
- "reasoning": a brief explanation of your classification

Example response:
{{"category": "positive", "confidence": 0.85, "reasoning": "The text expresses satisfaction and positive sentiment."}}

Response:"""
        
        return prompt
    
    def _parse_classification_response(
        self, 
        response_text: str, 
        categories: List[str],
        input_data: ClassificationInput
    ) -> ClassificationResult:
        """
        Parse Anthropic response into ClassificationResult.
        
        Args:
            response_text: Raw response from Anthropic
            categories: Available categories
            input_data: Original input data
            
        Returns:
            Parsed classification result
        """
        try:
            # Try to parse JSON response
            if "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
                
                parsed = json.loads(json_str)
                
                category = parsed.get("category", categories[0])
                confidence = float(parsed.get("confidence", 0.5))
                reasoning = parsed.get("reasoning", "No reasoning provided")
                
                # Validate category
                if category not in categories:
                    category = categories[0]
                    confidence = 0.1
                
                return ClassificationResult(
                    input_id=input_data.id,
                    category=category,
                    confidence=confidence,
                    metadata={
                        "provider": "anthropic",
                        "model": self.config.model,
                        "reasoning": reasoning,
                        "raw_response": response_text
                    }
                )
            
            # Fallback: simple text matching
            response_lower = response_text.lower()
            for category in categories:
                if category.lower() in response_lower:
                    return ClassificationResult(
                        input_id=input_data.id,
                        category=category,
                        confidence=0.6,
                        metadata={
                            "provider": "anthropic",
                            "model": self.config.model,
                            "raw_response": response_text,
                            "parsing_method": "fallback"
                        }
                    )
            
            # Default fallback
            return ClassificationResult(
                input_id=input_data.id,
                category=categories[0],
                confidence=0.1,
                metadata={
                    "provider": "anthropic",
                    "model": self.config.model,
                    "raw_response": response_text,
                    "parsing_method": "default_fallback"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Anthropic response: {e}")
            return ClassificationResult(
                input_id=input_data.id,
                category=categories[0],
                confidence=0.1,
                metadata={
                    "provider": "anthropic",
                    "model": self.config.model,
                    "error": str(e),
                    "raw_response": response_text
                }
            )
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform health check for Anthropic provider.
        
        Returns:
            Health check results
        """
        try:
            # Simple test message
            test_response = await self.async_client.messages.create(
                model=self.config.model or "claude-3-haiku-20240307",
                max_tokens=10,
                messages=[
                    {
                        "role": "user", 
                        "content": "Hello"
                    }
                ]
            )
            
            return {
                "status": "healthy",
                "provider": "anthropic",
                "model": self.config.model,
                "response_time": "< 1s",
                "test_response": test_response.content[0].text[:50]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "anthropic", 
                "model": self.config.model,
                "error": str(e)
            }
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Anthropic models.
        
        Returns:
            List of model names
        """
        return self.default_models.copy()
    
    def estimate_cost(self, input_data: ClassificationInput, **kwargs) -> float:
        """
        Estimate cost for classification request.
        
        Args:
            input_data: Input data
            **kwargs: Additional parameters
            
        Returns:
            Estimated cost in USD
        """
        # Rough token estimation (4 chars = 1 token)
        input_tokens = len(input_data.text) // 4
        output_tokens = 100  # Estimated output
        
        # Claude-3 pricing (approximate)
        if "opus" in (self.config.model or "").lower():
            input_cost = input_tokens * 0.000015  # $15/1M tokens
            output_cost = output_tokens * 0.000075  # $75/1M tokens
        elif "sonnet" in (self.config.model or "").lower():
            input_cost = input_tokens * 0.000003  # $3/1M tokens
            output_cost = output_tokens * 0.000015  # $15/1M tokens
        else:  # Haiku
            input_cost = input_tokens * 0.00000025  # $0.25/1M tokens
            output_cost = output_tokens * 0.00000125  # $1.25/1M tokens
        
        return input_cost + output_cost
