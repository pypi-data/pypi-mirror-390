"""
AWS Bedrock provider implementation.

This module implements the AWS Bedrock LLM provider with support for Claude,
Llama, and other foundation models available through AWS Bedrock.
"""

import asyncio
import json
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


@register_provider("aws_bedrock")
class AWSBedrockProvider(BaseLLMProvider):
    """
    AWS Bedrock provider implementation.
    
    Supports foundation models available through AWS Bedrock including
    Claude, Llama, Titan, and other models with enterprise features.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize AWS Bedrock provider."""
        super().__init__(config)
        self._client = None
        self._runtime_client = None
        
        # AWS-specific settings
        self.supports_function_calling = False  # Depends on model
        self.supports_streaming = True
        self.supports_multimodal = "claude-3" in config.model
        
        # AWS configuration
        self.region = getattr(config, 'aws_region', 'us-east-1')
        self.aws_access_key_id = getattr(config, 'aws_access_key_id', None)
        self.aws_secret_access_key = getattr(config, 'aws_secret_access_key', None)
        
        # Model-specific configurations
        self._model_configs = {
            "anthropic.claude-3-sonnet-20240229-v1:0": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_multimodal": True
            },
            "anthropic.claude-3-haiku-20240307-v1:0": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_multimodal": True
            },
            "anthropic.claude-v2:1": {
                "max_tokens": 4096,
                "supports_streaming": True,
                "supports_multimodal": False
            },
            "meta.llama2-70b-chat-v1": {
                "max_tokens": 2048,
                "supports_streaming": True,
                "supports_multimodal": False
            },
            "amazon.titan-text-express-v1": {
                "max_tokens": 8192,
                "supports_streaming": False,
                "supports_multimodal": False
            }
        }
        
        # Approximate pricing per 1K tokens
        self._pricing = {
            "anthropic.claude-3-sonnet-20240229-v1:0": {"input": 0.003, "output": 0.015},
            "anthropic.claude-3-haiku-20240307-v1:0": {"input": 0.00025, "output": 0.00125},
            "anthropic.claude-v2:1": {"input": 0.008, "output": 0.024},
            "meta.llama2-70b-chat-v1": {"input": 0.00195, "output": 0.00256},
            "amazon.titan-text-express-v1": {"input": 0.0008, "output": 0.0016},
        }
    
    async def _perform_initialization(self):
        """Initialize AWS Bedrock client."""
        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Configure session
            session_kwargs = {"region_name": self.region}
            if self.aws_access_key_id and self.aws_secret_access_key:
                session_kwargs.update({
                    "aws_access_key_id": self.aws_access_key_id,
                    "aws_secret_access_key": self.aws_secret_access_key
                })
            
            session = boto3.Session(**session_kwargs)
            
            # Initialize clients
            self._client = session.client('bedrock')
            self._runtime_client = session.client('bedrock-runtime')
            
            # Test connection
            await self._test_connection()
            
        except ImportError:
            raise ModelLoadError(
                "boto3 library not installed. Install with: pip install boto3",
                provider="aws_bedrock"
            )
        except NoCredentialsError:
            raise AuthenticationError(
                "AWS credentials not found. Configure AWS credentials.",
                provider="aws_bedrock"
            )
        except Exception as e:
            raise ProviderError(
                f"Failed to initialize AWS Bedrock client: {e}",
                provider="aws_bedrock",
                cause=e
            )
    
    async def _test_connection(self):
        """Test the connection to AWS Bedrock."""
        try:
            # List foundation models to test access
            response = self._client.list_foundation_models()
            logger.debug("AWS Bedrock connection test successful")
        except Exception as e:
            raise ProviderError(
                f"AWS Bedrock connection test failed: {e}",
                provider="aws_bedrock",
                cause=e
            )
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text response using AWS Bedrock."""
        if not self._initialized:
            await self.initialize()
        
        try:
            # Prepare model-specific request
            if "anthropic.claude" in self.config.model:
                response = await self._generate_claude(messages, **kwargs)
            elif "meta.llama" in self.config.model:
                response = await self._generate_llama(messages, **kwargs)
            elif "amazon.titan" in self.config.model:
                response = await self._generate_titan(messages, **kwargs)
            else:
                raise ProviderError(
                    f"Unsupported model: {self.config.model}",
                    provider="aws_bedrock"
                )
            
            return response
            
        except Exception as e:
            self._track_error()
            if "throttling" in str(e).lower() or "rate" in str(e).lower():
                raise RateLimitError(
                    f"AWS Bedrock rate limit exceeded: {e}",
                    provider="aws_bedrock",
                    retry_after=60,
                    cause=e
                )
            elif "timeout" in str(e).lower():
                raise TimeoutError(
                    f"AWS Bedrock request timed out: {e}",
                    provider="aws_bedrock",
                    timeout_seconds=self.config.timeout_seconds,
                    cause=e
                )
            elif "access denied" in str(e).lower() or "unauthorized" in str(e).lower():
                raise AuthenticationError(
                    "AWS Bedrock access denied",
                    provider="aws_bedrock",
                    cause=e
                )
            else:
                raise ProviderError(
                    f"AWS Bedrock generation failed: {e}",
                    provider="aws_bedrock",
                    cause=e
                )
    
    async def _generate_claude(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Claude models."""
        # Convert messages to Claude format
        prompt = self._messages_to_claude_prompt(messages)
        
        body = {
            "prompt": prompt,
            "max_tokens_to_sample": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
            "stop_sequences": kwargs.get("stop", [])
        }
        
        start_time = asyncio.get_event_loop().time()
        
        response = self._runtime_client.invoke_model(
            modelId=self.config.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        end_time = asyncio.get_event_loop().time()
        self._track_request(end_time - start_time)
        
        response_body = json.loads(response['body'].read())
        return response_body.get('completion', '').strip()
    
    async def _generate_llama(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Llama models."""
        # Convert messages to Llama format
        prompt = self._messages_to_llama_prompt(messages)
        
        body = {
            "prompt": prompt,
            "max_gen_len": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", getattr(self.config, "top_p", 0.9))
        }
        
        start_time = asyncio.get_event_loop().time()
        
        response = self._runtime_client.invoke_model(
            modelId=self.config.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        end_time = asyncio.get_event_loop().time()
        self._track_request(end_time - start_time)
        
        response_body = json.loads(response['body'].read())
        return response_body.get('generation', '').strip()
    
    async def _generate_titan(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response using Titan models."""
        # Convert messages to simple prompt
        prompt = self._messages_to_simple_prompt(messages)
        
        body = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "topP": kwargs.get("top_p", getattr(self.config, "top_p", 0.9)),
                "stopSequences": kwargs.get("stop", [])
            }
        }
        
        start_time = asyncio.get_event_loop().time()
        
        response = self._runtime_client.invoke_model(
            modelId=self.config.model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        end_time = asyncio.get_event_loop().time()
        self._track_request(end_time - start_time)
        
        response_body = json.loads(response['body'].read())
        results = response_body.get('results', [])
        if results:
            return results[0].get('outputText', '').strip()
        return ""
    
    def _messages_to_claude_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to Claude prompt format."""
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
    
    def _messages_to_llama_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to Llama prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"<s>[INST] <<SYS>>\n{content}\n<</SYS>>")
            elif role == "user":
                if prompt_parts and not prompt_parts[-1].endswith("[/INST]"):
                    prompt_parts.append(f"{content} [/INST]")
                else:
                    prompt_parts.append(f"<s>[INST] {content} [/INST]")
            elif role == "assistant":
                prompt_parts.append(f"{content}</s>")
        
        return " ".join(prompt_parts)
    
    def _messages_to_simple_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages to simple prompt format."""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"Instructions: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n".join(prompt_parts)
    
    async def generate_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """Generate streaming text response using AWS Bedrock."""
        # Note: Streaming support varies by model
        model_config = self._model_configs.get(self.config.model, {})
        if not model_config.get("supports_streaming", False):
            # Fallback to non-streaming
            response = await self.generate(messages, **kwargs)
            yield response
            return
        
        # Real AWS Bedrock streaming implementation
        try:
            # Use AWS Bedrock's actual streaming API
            request_body = {
                "inputText": messages[0]["content"] if messages else "",
                "textGenerationConfig": {
                    "maxTokenCount": kwargs.get("max_tokens", 512),
                    "temperature": kwargs.get("temperature", 0.7),
                    "topP": kwargs.get("top_p", 0.9),
                    "stopSequences": kwargs.get("stop", [])
                }
            }

            # Use Bedrock's invoke_model_with_response_stream
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )

            # Process real streaming response
            for event in response["body"]:
                chunk = json.loads(event["chunk"]["bytes"])
                if "outputText" in chunk:
                    yield chunk["outputText"]

        except Exception as e:
            # Fallback to non-streaming if streaming fails
            logger.warning(f"Streaming failed, falling back to non-streaming: {e}")
            response = await self.generate(messages, **kwargs)
            yield response
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health."""
        try:
            if not self._initialized:
                return {
                    "status": "unhealthy",
                    "message": "Provider not initialized",
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            # Test with list models call
            start_time = asyncio.get_event_loop().time()
            self._client.list_foundation_models()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "message": "Provider is operational",
                "response_time_ms": response_time,
                "model": self.config.model,
                "region": self.region,
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
            "provider": "aws_bedrock",
            "model": self.config.model,
            "region": self.region,
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
        output_cost = (estimated_tokens * 0.5 / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    async def cleanup(self):
        """Cleanup provider resources."""
        # AWS clients don't require explicit cleanup
        self._client = None
        self._runtime_client = None
        self._initialized = False
        logger.info("AWS Bedrock provider cleaned up")
    
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
