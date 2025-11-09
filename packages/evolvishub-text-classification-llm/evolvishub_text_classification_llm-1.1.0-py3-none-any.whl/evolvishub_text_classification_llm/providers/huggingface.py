"""
HuggingFace provider implementation.

This module implements the HuggingFace Transformers provider with support for
local model inference, quantization, device management, and streaming.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, AsyncGenerator
from pathlib import Path

# Optional torch import
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    TORCH_AVAILABLE = False

# Optional transformers import
try:
    from transformers import (
        AutoTokenizer, AutoModelForCausalLM, AutoModelForSequenceClassification,
        BitsAndBytesConfig, pipeline
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .base import BaseLLMProvider
from .factory import register_provider
from ..core.schemas import ProviderConfig
from ..core.exceptions import (
    ProviderError, ModelLoadError, ResourceError, TimeoutError
)


logger = logging.getLogger(__name__)


@register_provider("huggingface")
class HuggingFaceProvider(BaseLLMProvider):
    """
    HuggingFace Transformers provider implementation.
    
    Supports local model inference with features like quantization,
    device management, and memory optimization.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize HuggingFace provider."""
        super().__init__(config)
        
        # Model components
        self._model = None
        self._tokenizer = None
        self._device = None

        # Classification components
        self._sentiment_pipeline = None
        self._classification_pipeline = None
        self._model_type = None  # 'causal', 'classification', 'zero-shot'

        # HuggingFace-specific settings
        self.supports_streaming = True
        self.supports_local_inference = True
        self.supports_quantization = config.quantization
        self.supports_classification = True
        
        # Memory management
        self._max_memory_usage = 0
        self._model_memory_usage = 0
    
    async def _perform_initialization(self):
        """Initialize HuggingFace model and tokenizer."""
        try:
            # Check if torch is available
            if not TORCH_AVAILABLE:
                raise ModelLoadError(
                    "PyTorch not installed. Install with: pip install torch",
                    provider=self.provider_type
                )

            # Import required libraries
            try:
                from transformers import (
                    AutoTokenizer, AutoModelForCausalLM,
                    BitsAndBytesConfig, pipeline
                )
            except ImportError as e:
                raise ModelLoadError(
                    f"Transformers library not installed: {e}. "
                    "Install with: pip install transformers accelerate",
                    provider=self.provider_type,
                    cause=e
                )
            
            # Determine device
            self._device = self._get_device()
            logger.info(f"Using device: {self._device}")
            
            # Configure quantization if enabled
            quantization_config = None
            if self.config.quantization and self._device != "cpu":
                quantization_config = self._create_quantization_config()
            
            # Load tokenizer
            logger.info(f"Loading tokenizer: {self.config.model}")
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.config.model,
                cache_dir=self.config.cache_dir,
                token=self.config.extra_params.get("huggingface_token"),
                trust_remote_code=True
            )
            
            # Set pad token if not present
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Determine model type and load appropriate model
            self._model_type = self._determine_model_type()
            logger.info(f"Loading {self._model_type} model: {self.config.model}")

            model_kwargs = {
                "cache_dir": self.config.cache_dir,
                "token": self.config.extra_params.get("huggingface_token"),
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.config.quantization else torch.float32,
                "low_cpu_mem_usage": True,
            }

            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
                model_kwargs["device_map"] = "auto"

            # Load model based on type
            if self._model_type == "classification":
                self._model = AutoModelForSequenceClassification.from_pretrained(
                    self.config.model,
                    **model_kwargs
                )
            else:
                # Default to causal LM for backward compatibility
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.config.model,
                    **model_kwargs
                )

            # Move to device if not using quantization
            if not self.config.quantization:
                self._model = self._model.to(self._device)

            # Set to evaluation mode
            self._model.eval()

            # Initialize classification pipelines if supported
            await self._initialize_classification_pipelines()
            
            # Track memory usage
            self._track_memory_usage()
            
            logger.info(f"HuggingFace model loaded successfully on {self._device}")
            
        except Exception as e:
            if isinstance(e, ModelLoadError):
                raise
            raise ModelLoadError(
                f"Failed to initialize HuggingFace model: {e}",
                provider=self.provider_type,
                model=self.config.model,
                cause=e
            )
    
    def _get_device(self) -> str:
        """Determine the best device for inference."""
        if self.config.device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return self.config.device
    
    def _create_quantization_config(self):
        """Create quantization configuration."""
        try:
            from transformers import BitsAndBytesConfig
            
            # Default to 4-bit quantization
            quantization_bits = self.config.extra_params.get("quantization_bits", 4)
            
            if quantization_bits == 4:
                return BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quantization_bits == 8:
                return BitsAndBytesConfig(
                    load_in_8bit=True,
                    llm_int8_enable_fp32_cpu_offload=True
                )
            else:
                logger.warning(f"Unsupported quantization bits: {quantization_bits}")
                return None
                
        except ImportError:
            logger.warning("BitsAndBytesConfig not available, skipping quantization")
            return None
    
    async def _perform_generation(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Perform HuggingFace text generation."""
        try:
            # Format messages for the model
            prompt = self._format_messages(messages)
            
            # Tokenize input
            inputs = self._tokenizer.encode(
                prompt, 
                return_tensors="pt",
                truncation=True,
                max_length=self._get_max_input_length()
            )
            
            if self._device != "cpu":
                inputs = inputs.to(self._device)
            
            # Generation parameters
            generation_kwargs = {
                "max_new_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "do_sample": True,
                "pad_token_id": self._tokenizer.eos_token_id,
                "eos_token_id": self._tokenizer.eos_token_id,
                "repetition_penalty": kwargs.get("repetition_penalty", 1.1),
            }
            
            # Generate response
            with torch.no_grad():
                outputs = self._model.generate(
                    inputs,
                    **generation_kwargs
                )
            
            # Decode response (only new tokens)
            response = self._tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            )
            
            # Clean up response
            response = response.strip()
            
            # Handle empty responses
            if not response:
                logger.warning("Empty response from HuggingFace model")
                return "I apologize, but I couldn't generate a response."
            
            return response
            
        except torch.cuda.OutOfMemoryError as e:
            raise ResourceError(
                f"GPU out of memory: {e}",
                resource_type="gpu_memory",
                provider=self.provider_type,
                cause=e
            )
        except Exception as e:
            if isinstance(e, ResourceError):
                raise
            raise ProviderError(
                f"HuggingFace generation failed: {e}",
                provider=self.provider_type,
                model=self.config.model,
                cause=e
            )
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming response from HuggingFace model."""
        try:
            # Format messages
            prompt = self._format_messages(messages)
            
            # Tokenize input
            inputs = self._tokenizer.encode(prompt, return_tensors="pt")
            if self._device != "cpu":
                inputs = inputs.to(self._device)
            
            # Generation parameters
            max_new_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            temperature = kwargs.get("temperature", self.config.temperature)
            
            # Generate tokens one by one
            generated_tokens = []
            
            for _ in range(max_new_tokens):
                with torch.no_grad():
                    outputs = self._model(inputs)
                    logits = outputs.logits[0, -1, :]
                    
                    # Apply temperature
                    if temperature > 0:
                        logits = logits / temperature
                    
                    # Sample next token
                    probs = torch.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, 1)
                    
                    # Check for EOS token
                    if next_token.item() == self._tokenizer.eos_token_id:
                        break
                    
                    # Decode and yield token
                    token_text = self._tokenizer.decode(next_token, skip_special_tokens=True)
                    if token_text:
                        yield token_text
                    
                    # Update inputs for next iteration
                    inputs = torch.cat([inputs, next_token.unsqueeze(0)], dim=1)
                    generated_tokens.append(next_token.item())
                    
                    # Yield control to event loop
                    await asyncio.sleep(0)
                    
        except Exception as e:
            logger.error(f"HuggingFace streaming failed: {e}")
            
            # Fallback to non-streaming
            response = await self._perform_generation(messages, **kwargs)
            yield response
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for the model."""
        formatted_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_parts.append(f"System: {content}")
            elif role == "user":
                formatted_parts.append(f"Human: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
        
        # Add assistant prompt
        formatted_parts.append("Assistant:")
        
        return "\n".join(formatted_parts)
    
    def _get_max_input_length(self) -> int:
        """Get maximum input length for the model."""
        # Try to get from model config
        if hasattr(self._model, 'config') and hasattr(self._model.config, 'max_position_embeddings'):
            max_length = self._model.config.max_position_embeddings
        else:
            # Default fallback
            max_length = 2048
        
        # Reserve space for generation
        return max_length - self.config.max_tokens - 100
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform HuggingFace-specific health check."""
        try:
            # Test with minimal input
            test_messages = [{"role": "user", "content": "Hi"}]
            
            import time
            start_time = time.time()
            
            response = await self._perform_generation(test_messages, max_tokens=5)
            response_time = (time.time() - start_time) * 1000
            
            return {
                "response_time_ms": response_time,
                "model_loaded": True,
                "device": self._device,
                "memory_usage_mb": self._get_memory_usage(),
                "test_response_length": len(response)
            }
            
        except Exception as e:
            raise ProviderError(f"HuggingFace health check failed: {e}", cause=e)
    
    def _track_memory_usage(self):
        """Track current memory usage."""
        if torch.cuda.is_available() and self._device == "cuda":
            self._model_memory_usage = torch.cuda.memory_allocated() / 1024 / 1024  # MB
            self._max_memory_usage = max(self._max_memory_usage, self._model_memory_usage)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if torch.cuda.is_available() and self._device == "cuda":
            return torch.cuda.memory_allocated() / 1024 / 1024
        return 0.0
    
    async def estimate_cost(self, text: str) -> float:
        """
        Estimate cost for HuggingFace inference.
        
        For local models, cost is primarily computational (electricity, hardware).
        """
        # Rough estimation based on token count and computational cost
        estimated_tokens = len(text.split()) * 1.3
        
        # Estimate computational cost (very rough approximation)
        if self._device == "cuda":
            # GPU inference cost (electricity + hardware depreciation)
            cost_per_token = 0.00001  # $0.00001 per token (very rough estimate)
        else:
            # CPU inference cost (lower)
            cost_per_token = 0.000005
        
        return estimated_tokens * cost_per_token

    def _determine_model_type(self) -> str:
        """Determine the model type based on model name and configuration."""
        model_name = self.config.model.lower()

        # Check for known classification models
        classification_indicators = [
            'sentiment', 'classification', 'classifier', 'roberta-base-sentiment',
            'distilbert-base-uncased-finetuned-sst', 'cardiffnlp/twitter-roberta'
        ]

        # Check for zero-shot classification models
        zero_shot_indicators = ['bart-large-mnli', 'deberta-v3-large-mnli']

        if any(indicator in model_name for indicator in classification_indicators):
            return "classification"
        elif any(indicator in model_name for indicator in zero_shot_indicators):
            return "zero-shot"
        else:
            return "causal"

    async def _initialize_classification_pipelines(self):
        """Initialize classification pipelines for enhanced functionality."""
        try:
            device_id = 0 if self._device == "cuda" else -1

            # Initialize sentiment analysis pipeline if model supports it
            if self._model_type in ["classification", "zero-shot"]:
                # Use a dedicated sentiment model for better results
                sentiment_model = self.config.extra_params.get(
                    "sentiment_model",
                    "cardiffnlp/twitter-roberta-base-sentiment-latest"
                )

                try:
                    self._sentiment_pipeline = pipeline(
                        "sentiment-analysis",
                        model=sentiment_model,
                        device=device_id,
                        return_all_scores=True
                    )
                    logger.info(f"Sentiment pipeline initialized with {sentiment_model}")
                except Exception as e:
                    logger.warning(f"Failed to initialize sentiment pipeline: {e}")

            # Initialize zero-shot classification pipeline
            if self._model_type == "zero-shot" or "bart-large-mnli" in self.config.model.lower():
                try:
                    self._classification_pipeline = pipeline(
                        "zero-shot-classification",
                        model=self.config.model,
                        tokenizer=self._tokenizer,
                        device=device_id,
                        return_all_scores=True
                    )
                    logger.info("Zero-shot classification pipeline initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize classification pipeline: {e}")

        except Exception as e:
            logger.warning(f"Failed to initialize classification pipelines: {e}")

    async def classify_text(
        self,
        text: str,
        categories: List[str] = None,
        include_sentiment: bool = True
    ) -> Dict[str, Any]:
        """
        Perform enhanced text classification with structured output.

        Args:
            text: Text to classify
            categories: List of categories for classification
            include_sentiment: Whether to include sentiment analysis

        Returns:
            Structured classification result
        """
        result = {
            "primary_category": None,
            "categories": {},
            "confidence": 0.0,
            "sentiment": None,
            "processing_time_ms": 0.0
        }

        start_time = time.time()

        try:
            # Default email categories if none provided
            if categories is None:
                categories = [
                    "customer support", "technical support", "sales inquiry",
                    "billing inquiry", "complaint", "refund request",
                    "urgent communication", "emergency", "spam",
                    "promotional", "internal communication",
                    "positive feedback", "general inquiry"
                ]

            # Perform zero-shot classification if pipeline available
            if self._classification_pipeline and categories:
                classification_result = self._classification_pipeline(text, categories)

                # Extract structured results
                if classification_result:
                    result["primary_category"] = classification_result["labels"][0]
                    result["confidence"] = classification_result["scores"][0]

                    # Build categories dictionary
                    for label, score in zip(classification_result["labels"], classification_result["scores"]):
                        result["categories"][label] = float(score)

            # Perform sentiment analysis if pipeline available
            if include_sentiment and self._sentiment_pipeline:
                sentiment_result = self._sentiment_pipeline(text)

                if sentiment_result and len(sentiment_result) > 0:
                    # Handle both single result and list of results
                    if isinstance(sentiment_result[0], list):
                        sentiment_data = sentiment_result[0]
                    else:
                        sentiment_data = sentiment_result

                    # Find the highest confidence sentiment
                    best_sentiment = max(sentiment_data, key=lambda x: x['score'])
                    result["sentiment"] = {
                        "label": best_sentiment["label"].lower(),
                        "confidence": float(best_sentiment["score"])
                    }

            # Calculate processing time
            result["processing_time_ms"] = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            result["processing_time_ms"] = (time.time() - start_time) * 1000
            return result

    async def cleanup(self):
        """Cleanup HuggingFace provider resources."""
        if self._model is not None:
            del self._model
            self._model = None

        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None

        if self._sentiment_pipeline is not None:
            del self._sentiment_pipeline
            self._sentiment_pipeline = None

        if self._classification_pipeline is not None:
            del self._classification_pipeline
            self._classification_pipeline = None

        # Clear GPU cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        await super().cleanup()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        info = {
            "model_name": self.config.model,
            "device": self._device,
            "quantization": self.config.quantization,
            "memory_usage_mb": self._get_memory_usage(),
            "max_memory_usage_mb": self._max_memory_usage,
        }
        
        if self._model and hasattr(self._model, 'config'):
            config = self._model.config
            info.update({
                "vocab_size": getattr(config, 'vocab_size', None),
                "hidden_size": getattr(config, 'hidden_size', None),
                "num_layers": getattr(config, 'num_hidden_layers', None),
                "num_attention_heads": getattr(config, 'num_attention_heads', None),
                "max_position_embeddings": getattr(config, 'max_position_embeddings', None),
            })
        
        return info
