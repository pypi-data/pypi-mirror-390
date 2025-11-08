"""
Google AI (Gemini) provider for text classification.

This module provides integration with Google's Gemini models
for text classification tasks.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
import json

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

from .base import BaseLLMProvider
from ..core.schemas import (
    ClassificationInput, ClassificationResult, ProviderConfig, ProviderType
)
from ..core.exceptions import ProviderError, ConfigurationError


logger = logging.getLogger(__name__)


class GoogleAIProvider(BaseLLMProvider):
    """
    Google AI (Gemini) provider for text classification.
    
    Supports Gemini Pro and other Google AI models.
    """
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize Google AI provider.
        
        Args:
            config: Provider configuration
        """
        if not GOOGLE_AI_AVAILABLE:
            raise ConfigurationError(
                "Google AI library not installed. Install with: pip install google-generativeai"
            )
        
        super().__init__(config)
        self.provider_type = ProviderType.GOOGLE_AI
        self.model: Optional[Any] = None
        
        # Default models
        self.default_models = [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    
    async def _perform_initialization(self) -> bool:
        """
        Initialize the Google AI client.
        
        Returns:
            True if initialization successful
        """
        try:
            api_key = self.config.api_key
            if not api_key:
                raise ConfigurationError("Google AI API key is required")
            
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Initialize model
            model_name = self.config.model or "gemini-pro"
            self.model = genai.GenerativeModel(model_name)
            
            logger.info(f"Google AI provider initialized with model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Google AI provider: {e}")
            raise ProviderError(f"Google AI initialization failed: {e}")
    
    async def _perform_generation(
        self, 
        input_data: ClassificationInput,
        categories: List[str],
        **kwargs
    ) -> ClassificationResult:
        """
        Perform text classification using Google AI.
        
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
            
            # Prepare generation config
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.1),
                max_output_tokens=kwargs.get("max_tokens", 1000),
                top_p=kwargs.get("top_p", 0.8),
                top_k=kwargs.get("top_k", 40)
            )
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            # Parse response
            result = self._parse_classification_response(
                response.text,
                categories,
                input_data
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Google AI classification failed: {e}")
            raise ProviderError(f"Classification failed: {e}")
    
    def _build_classification_prompt(self, text: str, categories: List[str]) -> str:
        """
        Build classification prompt for Google AI.
        
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
        Parse Google AI response into ClassificationResult.
        
        Args:
            response_text: Raw response from Google AI
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
                        "provider": "google_ai",
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
                            "provider": "google_ai",
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
                    "provider": "google_ai",
                    "model": self.config.model,
                    "raw_response": response_text,
                    "parsing_method": "default_fallback"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Google AI response: {e}")
            return ClassificationResult(
                input_id=input_data.id,
                category=categories[0],
                confidence=0.1,
                metadata={
                    "provider": "google_ai",
                    "model": self.config.model,
                    "error": str(e),
                    "raw_response": response_text
                }
            )
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """
        Perform health check for Google AI provider.
        
        Returns:
            Health check results
        """
        try:
            # Simple test generation
            test_response = await asyncio.to_thread(
                self.model.generate_content,
                "Hello, how are you?",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0.1
                )
            )
            
            return {
                "status": "healthy",
                "provider": "google_ai",
                "model": self.config.model,
                "response_time": "< 1s",
                "test_response": test_response.text[:50]
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "google_ai", 
                "model": self.config.model,
                "error": str(e)
            }
    
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported Google AI models.
        
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
        
        # Gemini pricing (approximate)
        if "1.5-pro" in (self.config.model or "").lower():
            # Gemini 1.5 Pro pricing
            input_cost = input_tokens * 0.0000035  # $3.50/1M tokens
            output_cost = output_tokens * 0.0000105  # $10.50/1M tokens
        elif "1.5-flash" in (self.config.model or "").lower():
            # Gemini 1.5 Flash pricing
            input_cost = input_tokens * 0.00000035  # $0.35/1M tokens
            output_cost = output_tokens * 0.00000105  # $1.05/1M tokens
        else:
            # Gemini Pro pricing
            input_cost = input_tokens * 0.0000005  # $0.50/1M tokens
            output_cost = output_tokens * 0.0000015  # $1.50/1M tokens
        
        return input_cost + output_cost
