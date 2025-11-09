#!/usr/bin/env python3
"""
Mistral AI Provider Example

This example demonstrates how to use the Mistral AI provider for text classification.
Mistral AI offers high-quality, cost-effective language models with excellent performance.

Features demonstrated:
- Basic text classification with Mistral models
- Model comparison (tiny, small, medium, large)
- Streaming classification
- Cost estimation and optimization
- Error handling and fallback strategies
- Performance benchmarking
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


async def basic_mistral_classification():
    """Demonstrate basic text classification with Mistral AI."""
    print("\n🤖 Basic Mistral AI Classification")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY environment variable not set")
        print("   Get your API key from: https://console.mistral.ai/")
        return
    
    # Sample texts for classification
    texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is the worst purchase I've ever made. Complete waste of money.",
        "The product is okay, nothing special but does what it's supposed to do.",
        "Great quality but the price is too high. Mixed feelings about this.",
        "Customer service was excellent, but the product arrived damaged."
    ]
    
    categories = ["positive", "negative", "neutral", "mixed"]
    
    # Create Mistral provider configuration
    provider_config = ProviderConfig(
        provider_type=ProviderType.MISTRAL,
        model="mistral-small",  # Cost-effective model
        api_key=api_key,
        temperature=0.1,
        max_tokens=200
    )
    
    # Create workflow configuration
    workflow_config = WorkflowConfig(
        name="mistral_sentiment_analysis",
        primary_provider=provider_config,
        categories=categories,
        system_prompt="You are an expert sentiment analysis assistant.",
        user_prompt_template="""Analyze the sentiment of this text and classify it into one of these categories: {categories}

Text: {text}

Respond with a JSON object containing:
- primary_category: the most appropriate category
- confidence: confidence score (0.0 to 1.0)
- reasoning: brief explanation of your classification

JSON Response:"""
    )
    
    # Create classification engine
    engine = ClassificationEngine(config=workflow_config)
    
    try:
        await engine.initialize()
        
        print(f"✅ Mistral provider initialized with model: {provider_config.model}")
        
        # Classify each text
        for i, text in enumerate(texts, 1):
            print(f"\n📝 Text {i}: {text[:50]}...")
            
            start_time = time.time()
            result = await engine.classify(text)
            end_time = time.time()
            
            print(f"   Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Processing time: {(end_time - start_time) * 1000:.1f}ms")
            
            if hasattr(result, 'categories') and result.categories:
                print(f"   All scores: {result.categories}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        await engine.cleanup()


async def mistral_model_comparison():
    """Compare different Mistral models for performance and cost."""
    print("\n📊 Mistral Model Comparison")
    print("=" * 50)
    
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY environment variable not set")
        return
    
    # Models to compare
    models = [
        ("mistral-tiny", "Fastest and most cost-effective"),
        ("mistral-small", "Balanced performance and cost"),
        ("mistral-medium", "High quality for complex tasks"),
        # ("mistral-large", "Best performance (most expensive)")  # Uncomment if needed
    ]
    
    test_text = "The new smartphone has excellent camera quality and battery life, but the price is quite high and the design feels outdated compared to competitors."
    categories = ["positive", "negative", "neutral", "mixed"]
    
    results = []
    
    for model_name, description in models:
        print(f"\n🧪 Testing {model_name}: {description}")
        
        try:
            # Create provider config
            provider_config = ProviderConfig(
                provider_type=ProviderType.MISTRAL,
                model=model_name,
                api_key=api_key,
                temperature=0.1,
                max_tokens=150
            )
            
            # Create engine
            engine = ClassificationEngine.create_simple(
                provider_type="mistral",
                model=model_name,
                api_key=api_key,
                categories=categories
            )
            
            await engine.initialize()
            
            # Estimate cost
            estimated_cost = await engine.primary_provider.estimate_cost(test_text)
            
            # Perform classification
            start_time = time.time()
            result = await engine.classify(test_text)
            end_time = time.time()
            
            processing_time = (end_time - start_time) * 1000
            
            results.append({
                "model": model_name,
                "category": result.primary_category,
                "confidence": result.confidence,
                "processing_time_ms": processing_time,
                "estimated_cost_usd": estimated_cost,
                "description": description
            })
            
            print(f"   ✅ Category: {result.primary_category} (confidence: {result.confidence:.3f})")
            print(f"   ⏱️ Time: {processing_time:.1f}ms")
            print(f"   💰 Estimated cost: ${estimated_cost:.6f}")
            
            await engine.cleanup()
            
        except Exception as e:
            print(f"   ❌ Error with {model_name}: {e}")
            results.append({
                "model": model_name,
                "error": str(e),
                "description": description
            })
    
    # Summary comparison
    print(f"\n📈 Model Comparison Summary:")
    print("-" * 80)
    print(f"{'Model':<15} {'Category':<12} {'Confidence':<12} {'Time (ms)':<12} {'Cost ($)':<12}")
    print("-" * 80)
    
    for result in results:
        if "error" not in result:
            print(f"{result['model']:<15} {result['category']:<12} {result['confidence']:<12.3f} "
                  f"{result['processing_time_ms']:<12.1f} {result['estimated_cost_usd']:<12.6f}")
        else:
            print(f"{result['model']:<15} {'ERROR':<12} {'-':<12} {'-':<12} {'-':<12}")


async def mistral_streaming_example():
    """Demonstrate streaming classification with Mistral AI."""
    print("\n🌊 Mistral Streaming Classification")
    print("=" * 50)
    
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY environment variable not set")
        return
    
    # Create classification engine
    engine = ClassificationEngine.create_simple(
        provider_type="mistral",
        model="mistral-small",
        api_key=api_key,
        categories=["positive", "negative", "neutral", "mixed"]
    )
    
    try:
        await engine.initialize()
        
        # Create streaming engine
        streaming_engine = StreamingClassificationEngine(
            classification_engine=engine,
            max_concurrent_streams=5
        )
        
        # Test text
        test_text = """
        I recently purchased this laptop for work and gaming. The performance is outstanding - 
        it handles all my development tools smoothly and runs games at high settings. 
        The build quality feels premium with a solid aluminum body. However, the battery 
        life is disappointing, lasting only about 4 hours with normal use. The keyboard 
        is comfortable for typing, but the trackpad could be more responsive. Overall, 
        it's a powerful machine with some trade-offs.
        """
        
        from evolvishub_text_classification_llm.streaming.schemas import StreamingRequest
        
        # Create streaming request
        request = StreamingRequest(
            text=test_text.strip(),
            categories=["positive", "negative", "neutral", "mixed"],
            stream_id="mistral_demo_stream"
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


async def mistral_cost_optimization():
    """Demonstrate cost optimization strategies with Mistral AI."""
    print("\n💰 Mistral Cost Optimization")
    print("=" * 50)
    
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("❌ MISTRAL_API_KEY environment variable not set")
        return
    
    # Sample texts of different lengths
    texts = [
        "Great product!",  # Short
        "This product has excellent build quality and performs well in most scenarios.",  # Medium
        """This is a comprehensive review of the product after using it for several months. 
        The build quality is exceptional with premium materials throughout. Performance 
        has been consistently reliable across various use cases. The user interface is 
        intuitive and well-designed. However, there are some minor issues with battery 
        life and the price point is quite high compared to competitors."""  # Long
    ]
    
    categories = ["positive", "negative", "neutral"]
    
    print("📊 Cost Analysis by Text Length and Model:")
    print("-" * 70)
    print(f"{'Text Length':<15} {'Model':<15} {'Est. Cost ($)':<15} {'Time (ms)':<15}")
    print("-" * 70)
    
    for text in texts:
        text_length = len(text)
        
        for model in ["mistral-tiny", "mistral-small"]:
            try:
                # Create engine
                engine = ClassificationEngine.create_simple(
                    provider_type="mistral",
                    model=model,
                    api_key=api_key,
                    categories=categories
                )
                
                await engine.initialize()
                
                # Estimate cost
                estimated_cost = await engine.primary_provider.estimate_cost(text)
                
                # Measure actual performance
                start_time = time.time()
                result = await engine.classify(text)
                end_time = time.time()
                
                processing_time = (end_time - start_time) * 1000
                
                print(f"{text_length:<15} {model:<15} ${estimated_cost:<14.6f} {processing_time:<15.1f}")
                
                await engine.cleanup()
                
            except Exception as e:
                print(f"{text_length:<15} {model:<15} {'ERROR':<15} {'-':<15}")
    
    print("\n💡 Cost Optimization Tips:")
    print("• Use mistral-tiny for simple sentiment analysis")
    print("• Use mistral-small for balanced performance/cost")
    print("• Batch similar requests to reduce overhead")
    print("• Set appropriate max_tokens to control costs")
    print("• Use caching for repeated classifications")


async def mistral_error_handling():
    """Demonstrate error handling and fallback strategies."""
    print("\n🛡️ Mistral Error Handling & Fallback")
    print("=" * 50)
    
    # Test with invalid API key
    print("🧪 Testing with invalid API key...")
    try:
        engine = ClassificationEngine.create_simple(
            provider_type="mistral",
            model="mistral-small",
            api_key="invalid-key",
            categories=["positive", "negative"]
        )
        
        await engine.initialize()
        result = await engine.classify("Test text")
        
    except Exception as e:
        print(f"   ✅ Correctly caught authentication error: {type(e).__name__}")
    
    # Test with invalid model
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key:
        print("\n🧪 Testing with invalid model...")
        try:
            engine = ClassificationEngine.create_simple(
                provider_type="mistral",
                model="invalid-model",
                api_key=api_key,
                categories=["positive", "negative"]
            )
            
            await engine.initialize()
            result = await engine.classify("Test text")
            
        except Exception as e:
            print(f"   ✅ Correctly caught model error: {type(e).__name__}")
        
        # Test fallback to different model
        print("\n🧪 Testing fallback strategy...")
        try:
            from evolvishub_text_classification_llm.core.schemas import ProviderConfig
            
            # Primary provider (might fail)
            primary_config = ProviderConfig(
                provider_type=ProviderType.MISTRAL,
                model="mistral-small",
                api_key=api_key,
                timeout_seconds=1  # Very short timeout
            )
            
            # Fallback provider
            fallback_config = ProviderConfig(
                provider_type=ProviderType.MISTRAL,
                model="mistral-tiny",  # Faster model as fallback
                api_key=api_key
            )
            
            workflow_config = WorkflowConfig(
                name="fallback_test",
                primary_provider=primary_config,
                fallback_providers=[fallback_config],
                enable_fallback=True,
                categories=["positive", "negative", "neutral"]
            )
            
            engine = ClassificationEngine(config=workflow_config)
            await engine.initialize()
            
            result = await engine.classify("This is a test message for fallback.")
            print(f"   ✅ Fallback successful: {result.primary_category}")
            
            await engine.cleanup()
            
        except Exception as e:
            print(f"   ❌ Fallback test failed: {e}")


async def main():
    """Run all Mistral AI examples."""
    print("🤖 Mistral AI Provider Examples")
    print("=" * 60)
    print("Demonstrating Mistral AI integration for text classification")
    print("=" * 60)
    
    examples = [
        basic_mistral_classification,
        mistral_model_comparison,
        mistral_streaming_example,
        mistral_cost_optimization,
        mistral_error_handling
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
        
        print("\n" + "="*60)
    
    print("✅ All Mistral AI examples completed!")
    print("\n💡 Key Benefits of Mistral AI:")
    print("• Cost-effective pricing with excellent performance")
    print("• Multiple model sizes for different use cases")
    print("• Fast inference with low latency")
    print("• Strong multilingual capabilities")
    print("• Excellent instruction following")
    print("• European-based provider with strong privacy focus")


if __name__ == "__main__":
    asyncio.run(main())
