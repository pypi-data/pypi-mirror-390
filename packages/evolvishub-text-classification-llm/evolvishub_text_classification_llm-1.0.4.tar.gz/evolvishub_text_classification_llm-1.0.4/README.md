<div align="center">
  <img src="https://evolvis.ai/wp-content/uploads/2025/08/evie-solutions-03.png" alt="Evolvis AI - Evie Solutions Logo" width="400">
</div>

# Evolvishub Text Classification LLM

[![PyPI version](https://badge.fury.io/py/evolvishub-text-classification-llm.svg)](https://badge.fury.io/py/evolvishub-text-classification-llm)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Enterprise-grade text classification library with 11+ LLM providers, streaming, monitoring, and advanced workflows**

## Download Statistics

[![Weekly Downloads](https://pepy.tech/badge/evolvishub-text-classification-llm/week)](https://pepy.tech/project/evolvishub-text-classification-llm)
[![Monthly Downloads](https://pepy.tech/badge/evolvishub-text-classification-llm/month)](https://pepy.tech/project/evolvishub-text-classification-llm)
[![Total Downloads](https://pepy.tech/badge/evolvishub-text-classification-llm)](https://pepy.tech/project/evolvishub-text-classification-llm)

[![PyPI - Downloads](https://img.shields.io/pypi/dm/evolvishub-text-classification-llm)](https://pypi.org/project/evolvishub-text-classification-llm/)
[![PyPI - Status](https://img.shields.io/pypi/status/evolvishub-text-classification-llm)](https://pypi.org/project/evolvishub-text-classification-llm/)
[![PyPI - Format](https://img.shields.io/pypi/format/evolvishub-text-classification-llm)](https://pypi.org/project/evolvishub-text-classification-llm/)

## Overview

Evolvishub Text Classification LLM is a comprehensive, enterprise-ready Python library designed for production-scale text classification tasks. Built by Evolvis AI, this proprietary solution provides seamless integration with 11+ leading LLM providers, advanced monitoring capabilities, and professional-grade architecture suitable for mission-critical applications.

## Key Features

### Core Capabilities
- **11+ LLM Providers**: OpenAI, Anthropic, Google, Cohere, Mistral, Replicate, HuggingFace, Azure OpenAI, AWS Bedrock, Ollama, and Custom providers
- **Streaming Support**: Real-time text generation with WebSocket support
- **Async/Await**: Full asynchronous support for high-performance applications
- **Batch Processing**: Efficient processing of large datasets with configurable concurrency
- **Smart Caching**: Semantic caching with Redis and in-memory options
- **Comprehensive Monitoring**: Built-in health checks, metrics collection, and observability
- **Enterprise Security**: Authentication, rate limiting, and audit logging
- **Workflow Templates**: Pre-built workflows for common classification scenarios

### Advanced Features
- **Provider Fallback**: Automatic failover between providers for reliability
- **Cost Optimization**: Intelligent routing based on cost and performance metrics
- **Fine-tuning Support**: Custom model training and deployment capabilities
- **Multimodal Support**: Text, image, and document processing
- **LangGraph Integration**: Complex workflow orchestration
- **Real-time Streaming**: WebSocket-based real-time classification

## Installation

### Basic Installation

```bash
pip install evolvishub-text-classification-llm
```

### Provider-Specific Installation

```bash
# Install with specific providers
pip install evolvishub-text-classification-llm[openai,anthropic]

# Install with cloud providers
pip install evolvishub-text-classification-llm[azure_openai,aws_bedrock]

# Install with local inference
pip install evolvishub-text-classification-llm[huggingface,ollama]

# Full installation (all providers)
pip install evolvishub-text-classification-llm[all]
```

### Development Installation

```bash
pip install evolvishub-text-classification-llm[dev]
```

## Quick Start

### Basic Classification

```python
import asyncio
from evolvishub_text_classification_llm import create_engine
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType, WorkflowConfig

# Configure your workflow
config = WorkflowConfig(
    name="sentiment_analysis",
    description="Analyze sentiment of customer reviews",
    providers=[
        ProviderConfig(
            provider_type=ProviderType.OPENAI,
            api_key="your-openai-api-key",
            model="gpt-4",
            max_tokens=150,
            temperature=0.1
        )
    ]
)

async def main():
    engine = create_engine(config)
    
    result = await engine.classify(
        text="This product is absolutely amazing! I love it.",
        categories=["positive", "negative", "neutral"]
    )
    
    print(f"Classification: {result.category}")
    print(f"Confidence: {result.confidence}")

asyncio.run(main())
```

## Provider Configuration

### OpenAI GPT Models

```python
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType

openai_config = ProviderConfig(
    provider_type=ProviderType.OPENAI,
    api_key="your-openai-api-key",
    model="gpt-4",
    max_tokens=150,
    temperature=0.1,
    timeout_seconds=30
)
```

### Anthropic Claude

```python
anthropic_config = ProviderConfig(
    provider_type=ProviderType.ANTHROPIC,
    api_key="your-anthropic-api-key",
    model="claude-3-sonnet-20240229",
    max_tokens=150,
    temperature=0.1
)
```

### Google Gemini

```python
google_config = ProviderConfig(
    provider_type=ProviderType.GOOGLE,
    api_key="your-google-api-key",
    model="gemini-pro",
    max_tokens=150,
    temperature=0.1
)
```

### Cohere

```python
cohere_config = ProviderConfig(
    provider_type=ProviderType.COHERE,
    api_key="your-cohere-api-key",
    model="command",
    max_tokens=150,
    temperature=0.1
)
```

### Azure OpenAI

```python
azure_config = ProviderConfig(
    provider_type=ProviderType.AZURE_OPENAI,
    api_key="your-azure-api-key",
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_version="2024-02-15-preview",
    deployment_name="gpt-4",
    max_tokens=150
)
```

### AWS Bedrock

```python
bedrock_config = ProviderConfig(
    provider_type=ProviderType.AWS_BEDROCK,
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    aws_region="us-east-1",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=150
)
```

### HuggingFace Transformers

```python
huggingface_config = ProviderConfig(
    provider_type=ProviderType.HUGGINGFACE,
    model="microsoft/DialoGPT-medium",
    device="cuda",  # or "cpu"
    max_tokens=150,
    temperature=0.1,
    load_in_8bit=True  # For memory optimization
)
```

### Ollama (Local Inference)

```python
ollama_config = ProviderConfig(
    provider_type=ProviderType.OLLAMA,
    base_url="http://localhost:11434",
    model="llama2",
    max_tokens=150,
    temperature=0.1
)
```

### Mistral AI

```python
mistral_config = ProviderConfig(
    provider_type=ProviderType.MISTRAL,
    api_key="your-mistral-api-key",
    model="mistral-large-latest",
    max_tokens=150,
    temperature=0.1
)
```

### Replicate

```python
replicate_config = ProviderConfig(
    provider_type=ProviderType.REPLICATE,
    api_key="your-replicate-api-key",
    model="meta/llama-2-70b-chat",
    max_tokens=150,
    temperature=0.1
)
```

### Custom Provider

```python
custom_config = ProviderConfig(
    provider_type=ProviderType.CUSTOM,
    api_key="your-api-key",
    base_url="https://your-api-endpoint.com",
    model="your-model",
    request_format="openai",  # or "anthropic", "custom"
    response_format="openai",
    max_tokens=150
)
```

## Batch Processing

```python
from evolvishub_text_classification_llm import create_batch_processor

async def batch_example():
    processor = create_batch_processor(config)

    texts = [
        "This is great!",
        "I hate this product.",
        "It's okay, nothing special."
    ]

    results = await processor.process_batch(
        texts=texts,
        categories=["positive", "negative", "neutral"],
        batch_size=10,
        max_workers=4
    )

    for text, result in zip(texts, results):
        print(f"'{text}' -> {result.category} ({result.confidence:.2f})")
```

## Monitoring and Health Checks

```python
from evolvishub_text_classification_llm import HealthChecker, MetricsCollector

async def monitoring_example():
    # Health monitoring
    health_checker = HealthChecker()
    health_checker.register_provider("openai", openai_provider)

    health_status = await health_checker.perform_health_check()
    print(f"System health: {health_status.overall_status}")

    # Metrics collection
    metrics = MetricsCollector()
    metrics.record_counter("requests_total", 1)
    metrics.record_histogram("response_time_ms", 150.5)

    # Export metrics
    prometheus_metrics = metrics.export_metrics("prometheus")
    print(prometheus_metrics)
```

## Streaming

```python
async def streaming_example():
    engine = create_engine(config)

    async for chunk in engine.classify_stream(
        text="Analyze this long document...",
        categories=["technical", "business", "personal"]
    ):
        print(f"Partial result: {chunk}")
```

## Configuration

### Environment Variables

```bash
# Provider API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export COHERE_API_KEY="your-cohere-key"

# Optional: Redis for caching
export REDIS_URL="redis://localhost:6379"

# Optional: Monitoring
export PROMETHEUS_PORT="8000"
```

### Advanced Configuration

```python
from evolvishub_text_classification_llm.core.config import LibraryConfig

config = LibraryConfig(
    # Caching
    enable_caching=True,
    cache_backend="redis",
    cache_ttl_seconds=3600,

    # Monitoring
    enable_monitoring=True,
    metrics_port=8000,
    health_check_interval=60,

    # Performance
    max_concurrent_requests=100,
    request_timeout_seconds=30,

    # Security
    enable_audit_logging=True,
    rate_limit_requests_per_minute=1000
)
```

## Advanced Features

### Provider Fallback

```python
# Configure multiple providers with fallback
config = WorkflowConfig(
    name="robust_classification",
    providers=[
        ProviderConfig(provider_type=ProviderType.OPENAI, priority=1),
        ProviderConfig(provider_type=ProviderType.ANTHROPIC, priority=2),
        ProviderConfig(provider_type=ProviderType.COHERE, priority=3)
    ],
    fallback_enabled=True
)
```

### Cost Optimization

```python
# Optimize for cost vs performance
config = WorkflowConfig(
    name="cost_optimized",
    optimization_strategy="cost",  # or "performance", "balanced"
    max_cost_per_request=0.01
)
```

### Custom Workflows

```python
from evolvishub_text_classification_llm import WorkflowBuilder

builder = WorkflowBuilder()
workflow = (builder
    .add_preprocessing("clean_text")
    .add_classification("sentiment")
    .add_postprocessing("confidence_threshold", min_confidence=0.8)
    .build())

result = await workflow.execute("Your text here")
```

## Troubleshooting

### Common Issues

**1. Provider Authentication Errors**
```python
# Verify API keys are set correctly
from evolvishub_text_classification_llm import ProviderFactory

if not ProviderFactory.is_provider_available("openai"):
    print("OpenAI provider not available - check API key")
```

**2. Rate Limiting**
```python
# Configure rate limiting and retries
config = ProviderConfig(
    provider_type=ProviderType.OPENAI,
    rate_limit_requests_per_minute=60,
    max_retries=3,
    retry_delay_seconds=1
)
```

**3. Memory Issues with Large Batches**
```python
# Process in smaller chunks
processor = create_batch_processor(config)
results = await processor.process_batch(
    texts=large_text_list,
    batch_size=10,  # Reduce batch size
    max_workers=2   # Reduce concurrency
)
```

### Performance Optimization

**1. Enable Caching**
```python
# Redis caching for better performance
config.enable_caching = True
config.cache_backend = "redis"
config.cache_ttl_seconds = 3600
```

**2. Use Appropriate Models**
```python
# For simple tasks, use faster models
fast_config = ProviderConfig(
    provider_type=ProviderType.OPENAI,
    model="gpt-3.5-turbo",  # Faster than gpt-4
    max_tokens=50           # Reduce for simple classifications
)
```

**3. Batch Processing**
```python
# Process multiple texts together
results = await processor.process_batch(
    texts=texts,
    batch_size=20,    # Optimal batch size
    max_workers=4     # Parallel processing
)
```

## API Reference

### Core Classes

- `ClassificationEngine`: Main engine for text classification
- `BatchProcessor`: Batch processing capabilities
- `WorkflowBuilder`: Build custom classification workflows
- `ProviderFactory`: Manage and create LLM providers
- `HealthChecker`: Monitor system health
- `MetricsCollector`: Collect and export metrics

### Provider Types

- `ProviderType.OPENAI`: OpenAI GPT models
- `ProviderType.ANTHROPIC`: Anthropic Claude models
- `ProviderType.GOOGLE`: Google Gemini/PaLM models
- `ProviderType.COHERE`: Cohere Command models
- `ProviderType.MISTRAL`: Mistral AI models
- `ProviderType.REPLICATE`: Replicate hosted models
- `ProviderType.HUGGINGFACE`: HuggingFace Transformers
- `ProviderType.AZURE_OPENAI`: Azure OpenAI Service
- `ProviderType.AWS_BEDROCK`: AWS Bedrock models
- `ProviderType.OLLAMA`: Local Ollama models
- `ProviderType.CUSTOM`: Custom HTTP-based providers

### Convenience Functions

- `create_engine(config)`: Create a classification engine
- `create_batch_processor(config)`: Create a batch processor
- `get_supported_providers()`: List available providers
- `get_features()`: List enabled features

## Enterprise Support

For enterprise customers, we offer:

- **Priority Support**: 24/7 technical support
- **Custom Integrations**: Tailored solutions for your infrastructure
- **On-Premise Deployment**: Deploy in your own environment
- **Advanced Security**: SOC2, HIPAA, and GDPR compliance
- **Custom Models**: Fine-tuning and custom model development
- **Professional Services**: Implementation and consulting

Contact us at enterprise@evolvis.ai for more information.

## License

This software is proprietary and owned by Evolvis AI. See the [LICENSE](LICENSE) file for details.

**IMPORTANT**: This is NOT open source software. Usage is subject to the terms and conditions specified in the license agreement.

## Company Information

**Evolvis AI**
Website: https://evolvis.ai
Email: info@evolvis.ai

**Author**
Alban Maxhuni, PhD
Email: a.maxhuni@evolvis.ai

## Support

For technical support, licensing inquiries, or enterprise solutions:

- **Documentation**: https://docs.evolvis.ai/text-classification-llm
- **Enterprise Sales**: m.miralles@evolvis.ai
- **Technical Support**: support@evolvis.ai
- **General Inquiries**: info@evolvis.ai

---

Copyright (c) 2025 Evolvis AI. All rights reserved.
```
