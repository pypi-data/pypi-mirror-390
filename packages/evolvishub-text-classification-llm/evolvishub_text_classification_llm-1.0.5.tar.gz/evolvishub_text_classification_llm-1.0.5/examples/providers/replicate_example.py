#!/usr/bin/env python3
"""
Replicate Provider Example

This example demonstrates how to use the Replicate provider for text classification.
Replicate provides access to popular open-source models without infrastructure management.

Features demonstrated:
- Text classification with Llama-2 models
- CodeLlama for code-related classification
- Model comparison and selection
- Cost-effective inference
- Custom model support
- Streaming capabilities
"""

import asyncio
import os
import time
import logging
from typing import List, Dict, Any

from evolvishub_text_classification_llm import (
    ClassificationEngine,
    ProviderConfig,
    ProviderType,
    WorkflowConfig
)
from evolvishub_text_classification_llm.streaming import StreamingClassificationEngine


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_replicate_classification():
    """Demonstrate basic text classification with Replicate."""
    print("\n🦙 Basic Replicate Classification (Llama-2)")
    print("=" * 50)
    
    # Get API token
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        print("   Get your API token from: https://replicate.com/account")
        return
    
    # Sample texts for classification
    texts = [
        "I absolutely love this new framework! It's so easy to use and well-documented.",
        "This library is terrible. Full of bugs and poor documentation.",
        "The API is decent but could use some improvements in error handling.",
        "Excellent performance and great community support. Highly recommended!",
        "It works fine for basic use cases but lacks advanced features."
    ]
    
    categories = ["positive", "negative", "neutral", "mixed"]
    
    # Create Replicate provider configuration
    provider_config = ProviderConfig(
        provider_type=ProviderType.REPLICATE,
        model="meta/llama-2-7b-chat",  # Fast and cost-effective
        api_key=api_token,
        temperature=0.1,
        max_tokens=200
    )
    
    # Create workflow configuration
    workflow_config = WorkflowConfig(
        name="replicate_sentiment_analysis",
        primary_provider=provider_config,
        categories=categories,
        system_prompt="You are an expert at analyzing sentiment in text.",
        user_prompt_template="""Analyze the sentiment of this text and classify it into one of these categories: {categories}

Text: {text}

Respond with only the category name that best fits the sentiment."""
    )
    
    # Create classification engine
    engine = ClassificationEngine(config=workflow_config)
    
    try:
        await engine.initialize()
        
        print(f"✅ Replicate provider initialized with model: {provider_config.model}")
        
        # Classify each text
        for i, text in enumerate(texts, 1):
            print(f"\n📝 Text {i}: {text[:60]}...")
            
            start_time = time.time()
            result = await engine.classify(text)
            end_time = time.time()
            
            print(f"   Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Processing time: {(end_time - start_time) * 1000:.1f}ms")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await engine.cleanup()


async def replicate_model_comparison():
    """Compare different Replicate models for various tasks."""
    print("\n📊 Replicate Model Comparison")
    print("=" * 50)
    
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    # Models to compare
    models = [
        ("meta/llama-2-7b-chat", "General purpose, fast"),
        ("meta/llama-2-13b-chat", "Better quality, slower"),
        ("meta/codellama-7b-instruct", "Code-focused"),
        # ("meta/llama-2-70b-chat", "Highest quality, expensive")  # Uncomment if needed
    ]
    
    # Different types of texts
    test_cases = [
        {
            "text": "The customer service team was incredibly helpful and resolved my issue quickly.",
            "categories": ["positive", "negative", "neutral"],
            "task": "Customer feedback"
        },
        {
            "text": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
            "categories": ["good_code", "bad_code", "needs_improvement"],
            "task": "Code quality"
        },
        {
            "text": "The quarterly earnings report shows a 15% increase in revenue but declining profit margins.",
            "categories": ["positive", "negative", "neutral", "mixed"],
            "task": "Financial analysis"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Task: {test_case['task']}")
        print(f"📝 Text: {test_case['text'][:80]}...")
        print("-" * 60)
        
        for model_name, description in models:
            # Skip CodeLlama for non-code tasks and vice versa
            if "code" in test_case['task'].lower() and "code" not in model_name:
                continue
            if "code" not in test_case['task'].lower() and "code" in model_name:
                continue
            
            try:
                print(f"\n🤖 {model_name}: {description}")
                
                # Create engine
                engine = ClassificationEngine.create_simple(
                    provider_type="replicate",
                    model=model_name,
                    api_key=api_token,
                    categories=test_case['categories']
                )
                
                await engine.initialize()
                
                # Estimate cost
                estimated_cost = await engine.primary_provider.estimate_cost(test_case['text'])
                
                # Perform classification
                start_time = time.time()
                result = await engine.classify(test_case['text'])
                end_time = time.time()
                
                processing_time = (end_time - start_time) * 1000
                
                print(f"   ✅ Category: {result.primary_category} (confidence: {result.confidence:.3f})")
                print(f"   ⏱️ Time: {processing_time:.1f}ms")
                print(f"   💰 Estimated cost: ${estimated_cost:.6f}")
                
                await engine.cleanup()
                
            except Exception as e:
                print(f"   ❌ Error with {model_name}: {e}")


async def replicate_code_classification():
    """Demonstrate code classification using CodeLlama."""
    print("\n💻 Code Classification with CodeLlama")
    print("=" * 50)
    
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    # Code samples for classification
    code_samples = [
        {
            "code": """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
            """,
            "description": "Quicksort implementation"
        },
        {
            "code": """
import pandas as pd
df = pd.read_csv('data.csv')
result = df.groupby('category').sum()
            """,
            "description": "Data analysis code"
        },
        {
            "code": """
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
            """,
            "description": "Async HTTP request"
        }
    ]
    
    categories = [
        "algorithm_implementation",
        "data_processing", 
        "web_api",
        "database_operation",
        "utility_function"
    ]
    
    # Create CodeLlama engine
    engine = ClassificationEngine.create_simple(
        provider_type="replicate",
        model="meta/codellama-7b-instruct",
        api_key=api_token,
        categories=categories
    )
    
    try:
        await engine.initialize()
        
        print(f"✅ CodeLlama initialized for code classification")
        
        for i, sample in enumerate(code_samples, 1):
            print(f"\n📝 Code Sample {i}: {sample['description']}")
            print(f"```python\n{sample['code'].strip()}\n```")
            
            start_time = time.time()
            result = await engine.classify(sample['code'])
            end_time = time.time()
            
            print(f"   Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Processing time: {(end_time - start_time) * 1000:.1f}ms")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await engine.cleanup()


async def replicate_streaming_example():
    """Demonstrate streaming classification with Replicate."""
    print("\n🌊 Replicate Streaming Classification")
    print("=" * 50)
    
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    # Create classification engine
    engine = ClassificationEngine.create_simple(
        provider_type="replicate",
        model="meta/llama-2-7b-chat",
        api_key=api_token,
        categories=["positive", "negative", "neutral", "mixed"]
    )
    
    try:
        await engine.initialize()
        
        # Create streaming engine
        streaming_engine = StreamingClassificationEngine(
            classification_engine=engine,
            max_concurrent_streams=3
        )
        
        # Test text
        test_text = """
        After using this open-source library for several weeks, I have mixed feelings. 
        The documentation is comprehensive and the community is very active and helpful. 
        The performance is excellent for most use cases and the API design is intuitive. 
        However, there are some stability issues with the latest version and the 
        installation process can be tricky on certain systems. Overall, it's a 
        powerful tool but needs some polish.
        """
        
        from evolvishub_text_classification_llm.streaming.schemas import StreamingRequest
        
        # Create streaming request
        request = StreamingRequest(
            text=test_text.strip(),
            categories=["positive", "negative", "neutral", "mixed"],
            stream_id="replicate_demo_stream"
        )
        
        print(f"📝 Analyzing text: {test_text[:100]}...")
        print("\n🔄 Streaming results:")
        
        # Stream classification
        async for response in streaming_engine.stream_classify(request):
            if response.chunk_type == "progress":
                print(f"   📊 Progress: {response.progress:.1%} - {response.content}")
            elif response.chunk_type == "classification":
                if response.classification:
                    print(f"   ✅ Classification: {response.classification}")
                elif response.content:
                    print(f"   📄 Content chunk: {response.content[:100]}...")
            elif response.chunk_type == "complete":
                print(f"   🎉 {response.content}")
            elif response.chunk_type == "error":
                print(f"   ❌ Error: {response.error}")
        
        # Show metrics
        metrics = streaming_engine.get_metrics()
        print(f"\n📊 Streaming Metrics:")
        print(f"   Total requests: {metrics.total_requests}")
        print(f"   Active streams: {metrics.active_streams}")
        print(f"   Average response time: {metrics.average_response_time_ms:.1f}ms")
        
    except Exception as e:
        print(f"❌ Streaming error: {e}")
    
    finally:
        await engine.cleanup()


async def replicate_cost_analysis():
    """Analyze costs for different Replicate models."""
    print("\n💰 Replicate Cost Analysis")
    print("=" * 50)
    
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    # Different text lengths
    texts = [
        "Good product",  # Short
        "This product has good build quality and reasonable performance for the price point.",  # Medium
        """This is a detailed review after extensive testing. The product shows excellent 
        build quality with premium materials. Performance is consistently good across 
        various scenarios. The user interface is well-designed and intuitive. Battery 
        life meets expectations. Some minor issues with software updates but overall 
        a solid choice for the target market."""  # Long
    ]
    
    models = [
        "meta/llama-2-7b-chat",
        "meta/llama-2-13b-chat",
        "meta/codellama-7b-instruct"
    ]
    
    print("📊 Cost Comparison:")
    print("-" * 80)
    print(f"{'Model':<25} {'Text Length':<15} {'Est. Cost ($)':<15} {'Time (ms)':<15}")
    print("-" * 80)
    
    for model in models:
        for text in texts:
            try:
                engine = ClassificationEngine.create_simple(
                    provider_type="replicate",
                    model=model,
                    api_key=api_token,
                    categories=["positive", "negative", "neutral"]
                )
                
                await engine.initialize()
                
                # Estimate cost
                estimated_cost = await engine.primary_provider.estimate_cost(text)
                
                # Measure performance (optional - comment out to save costs)
                # start_time = time.time()
                # result = await engine.classify(text)
                # end_time = time.time()
                # processing_time = (end_time - start_time) * 1000
                
                processing_time = 0  # Placeholder when not measuring
                
                print(f"{model:<25} {len(text):<15} ${estimated_cost:<14.6f} {processing_time:<15.1f}")
                
                await engine.cleanup()
                
            except Exception as e:
                print(f"{model:<25} {len(text):<15} {'ERROR':<15} {'-':<15}")
    
    print("\n💡 Cost Optimization Tips for Replicate:")
    print("• Use smaller models (7B) for simple tasks")
    print("• Batch requests when possible")
    print("• Choose the right model for your specific task")
    print("• Monitor usage to avoid unexpected costs")
    print("• Consider caching results for repeated queries")


async def replicate_custom_model_example():
    """Demonstrate using custom models on Replicate."""
    print("\n🎯 Custom Model Support")
    print("=" * 50)
    
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN environment variable not set")
        return
    
    print("📝 Custom Model Configuration:")
    print("• Replicate supports custom fine-tuned models")
    print("• Models can be deployed from HuggingFace or custom training")
    print("• Use format: 'username/model-name' or 'username/model-name:version'")
    print("• Example: 'your-username/custom-sentiment-model'")
    
    # Example configuration for a hypothetical custom model
    custom_model_config = {
        "provider_type": "replicate",
        "model": "your-username/custom-sentiment-model",  # Replace with actual model
        "api_key": api_token,
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    print(f"\n🔧 Example configuration:")
    print(f"```python")
    print(f"engine = ClassificationEngine.create_simple(")
    print(f"    provider_type='replicate',")
    print(f"    model='{custom_model_config['model']}',")
    print(f"    api_key=api_token,")
    print(f"    categories=['positive', 'negative', 'neutral']")
    print(f")")
    print(f"```")
    
    print(f"\n💡 Benefits of Custom Models:")
    print("• Domain-specific performance")
    print("• Consistent output format")
    print("• Potentially lower costs")
    print("• Full control over model behavior")
    print("• No vendor lock-in")


async def main():
    """Run all Replicate examples."""
    print("🦙 Replicate Provider Examples")
    print("=" * 60)
    print("Demonstrating Replicate integration for text classification")
    print("=" * 60)
    
    examples = [
        basic_replicate_classification,
        replicate_model_comparison,
        replicate_code_classification,
        replicate_streaming_example,
        replicate_cost_analysis,
        replicate_custom_model_example
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
        
        print("\n" + "="*60)
    
    print("✅ All Replicate examples completed!")
    print("\n💡 Key Benefits of Replicate:")
    print("• Access to popular open-source models")
    print("• No infrastructure management required")
    print("• Cost-effective inference")
    print("• Support for custom fine-tuned models")
    print("• Easy model switching and comparison")
    print("• Strong community and model ecosystem")


if __name__ == "__main__":
    asyncio.run(main())
