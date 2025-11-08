#!/usr/bin/env python3
"""
OpenAI Provider Example - GPT-3.5/GPT-4 Classification

This example demonstrates comprehensive usage of the OpenAI provider including:
- GPT-3.5 and GPT-4 model support
- Function calling capabilities
- Streaming responses
- JSON mode for structured output
- Error handling and monitoring
- Cost estimation and optimization
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List

from evolvishub_text_classification_llm import (
    ClassificationEngine,
    ProviderConfig,
    ProviderType,
    WorkflowConfig
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def basic_openai_classification():
    """Basic OpenAI classification example."""
    print("\n🤖 Basic OpenAI Classification")
    print("=" * 50)
    
    try:
        # Create OpenAI provider configuration
        openai_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            temperature=0.1,
            max_tokens=500,
            timeout_seconds=30
        )
        
        # Create classification engine
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            categories=["positive", "negative", "neutral", "mixed"]
        )
        
        await engine.initialize()
        
        # Test texts
        test_texts = [
            "I absolutely love this product! It's amazing and works perfectly.",
            "This is the worst purchase I've ever made. Complete waste of money.",
            "The product is okay, nothing special but does what it's supposed to do.",
            "Great quality but the price is too high. Mixed feelings about this.",
            "Customer service was excellent, but the product arrived damaged."
        ]
        
        print("Classifying sample texts...")
        for i, text in enumerate(test_texts, 1):
            result = await engine.classify(text)
            
            print(f"\n{i}. Text: {text[:60]}...")
            print(f"   Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   All scores: {result.categories}")
            print(f"   Processing time: {result.processing_time_ms:.1f}ms")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def gpt4_advanced_classification():
    """Advanced GPT-4 classification with detailed analysis."""
    print("\n🧠 GPT-4 Advanced Classification")
    print("=" * 50)
    
    try:
        # Create advanced workflow configuration
        workflow_config = WorkflowConfig(
            name="gpt4_advanced_classification",
            primary_provider=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
                temperature=0.1,
                max_tokens=800
            ),
            categories=[
                "highly_positive", "positive", "neutral", 
                "negative", "highly_negative", "mixed_sentiment"
            ],
            system_prompt="""You are an expert sentiment analyst with deep understanding of nuanced emotions and context.
            
Your task is to classify text sentiment with high precision, considering:
- Explicit sentiment words and phrases
- Implicit emotional undertones
- Contextual factors and sarcasm
- Mixed or conflicting sentiments
- Cultural and linguistic nuances

Provide detailed reasoning for your classification.""",
            user_prompt_template="""Analyze the sentiment of this text with detailed reasoning:

Text: "{text}"

Provide a JSON response with:
{{
  "primary_category": "most_appropriate_category",
  "confidence": 0.95,
  "categories": {{
    "highly_positive": 0.05,
    "positive": 0.85,
    "neutral": 0.05,
    "negative": 0.03,
    "highly_negative": 0.01,
    "mixed_sentiment": 0.01
  }},
  "reasoning": "Detailed explanation of the classification",
  "sentiment_indicators": ["list", "of", "key", "sentiment", "words"],
  "emotional_tone": "description of emotional tone",
  "confidence_factors": ["factors that increase/decrease confidence"]
}}""",
            min_confidence_threshold=0.7
        )
        
        engine = ClassificationEngine(config=workflow_config)
        await engine.initialize()
        
        # Complex test cases
        complex_texts = [
            "The product is absolutely fantastic, but the customer service was a nightmare to deal with.",
            "I guess it's fine... not terrible, but I've definitely seen better for the price.",
            "OMG this is literally the BEST thing ever!!! 😍✨ Can't believe how amazing it is!",
            "Well, that was... interesting. Not quite what I expected, but hey, at least it works.",
            "The interface is intuitive and the features are comprehensive, though the learning curve is steep."
        ]
        
        print("Performing advanced sentiment analysis...")
        for i, text in enumerate(complex_texts, 1):
            result = await engine.classify(text, metadata={"analysis_type": "advanced"})
            
            print(f"\n{i}. Text: {text}")
            print(f"   Primary Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            
            # Extract detailed analysis from metadata
            if result.reasoning:
                print(f"   Reasoning: {result.reasoning}")
            
            # Show top 3 categories
            sorted_categories = sorted(result.categories.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Top categories: {sorted_categories}")
            
            print(f"   Processing time: {result.processing_time_ms:.1f}ms")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def openai_function_calling_example():
    """OpenAI function calling for structured classification."""
    print("\n🔧 OpenAI Function Calling Example")
    print("=" * 50)
    
    try:
        # Define classification function schema
        classification_function = {
            "name": "classify_customer_feedback",
            "description": "Classify customer feedback with detailed analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "sentiment": {
                        "type": "string",
                        "enum": ["very_positive", "positive", "neutral", "negative", "very_negative"],
                        "description": "Overall sentiment of the feedback"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "description": "Confidence score for the classification"
                    },
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Main topics mentioned in the feedback"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Urgency level of the feedback"
                    },
                    "department": {
                        "type": "string",
                        "enum": ["sales", "support", "technical", "billing", "general"],
                        "description": "Most appropriate department to handle this feedback"
                    },
                    "action_required": {
                        "type": "boolean",
                        "description": "Whether immediate action is required"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of the feedback"
                    }
                },
                "required": ["sentiment", "confidence", "topics", "urgency", "department"]
            }
        }
        
        # Create provider with function calling
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            temperature=0.1
        )
        
        # Create engine with custom workflow
        workflow_config = WorkflowConfig(
            name="function_calling_classification",
            primary_provider=provider_config,
            system_prompt="You are a customer feedback analyst. Use the provided function to classify feedback.",
            user_prompt_template="Analyze this customer feedback: {text}"
        )
        
        engine = ClassificationEngine(config=workflow_config)
        await engine.initialize()
        
        # Customer feedback examples
        feedback_examples = [
            "The new software update completely broke our workflow. We need this fixed ASAP as it's affecting our entire team's productivity!",
            "Thank you so much for the quick response to my billing question. Your support team is fantastic!",
            "I'm interested in upgrading to the premium plan. Can someone from sales contact me to discuss pricing options?",
            "The mobile app keeps crashing when I try to upload files. This has been happening for three days now.",
            "Just wanted to say that your product has transformed how we manage our projects. Excellent work!"
        ]
        
        print("Analyzing customer feedback with function calling...")
        for i, feedback in enumerate(feedback_examples, 1):
            # Real OpenAI function calling implementation
            try:
                # Use actual function calling if provider supports it
                functions = [
                    {
                        "name": "analyze_sentiment",
                        "description": "Analyze sentiment and extract key information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sentiment": {"type": "string", "enum": ["positive", "negative", "neutral"]},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "key_topics": {"type": "array", "items": {"type": "string"}},
                                "urgency": {"type": "string", "enum": ["low", "medium", "high"]}
                            },
                            "required": ["sentiment", "confidence"]
                        }
                    }
                ]

                # Perform classification with function calling
                result = await engine.classify(
                    feedback,
                    metadata={"functions": functions, "function_call": "analyze_sentiment"}
                )

                print(f"\n{i}. Feedback: {feedback}")
                print(f"   Sentiment: {result.primary_category}")
                print(f"   Confidence: {result.confidence:.3f}")

                # Extract function call results if available
                if hasattr(result, 'function_call_result'):
                    func_result = result.function_call_result
                    if 'key_topics' in func_result:
                        print(f"   Key Topics: {', '.join(func_result['key_topics'])}")
                    if 'urgency' in func_result:
                        print(f"   Urgency: {func_result['urgency']}")

            except Exception as e:
                # Fallback to regular classification
                result = await engine.classify(feedback)
                print(f"\n{i}. Feedback: {feedback}")
                print(f"   Sentiment: {result.primary_category}")
                print(f"   Confidence: {result.confidence:.3f}")
                print(f"   Note: Function calling not available, using standard classification")
            
            # Simulate structured output
            structured_analysis = {
                "sentiment": result.primary_category,
                "confidence": result.confidence,
                "topics": ["software", "productivity"] if "software" in feedback.lower() else ["general"],
                "urgency": "high" if "ASAP" in feedback or "crashing" in feedback else "medium",
                "department": "technical" if "crash" in feedback.lower() or "broke" in feedback.lower() 
                           else "sales" if "pricing" in feedback.lower() or "upgrade" in feedback.lower()
                           else "support",
                "action_required": "ASAP" in feedback or "crashing" in feedback,
                "summary": feedback[:100] + "..." if len(feedback) > 100 else feedback
            }
            
            print(f"   Structured Analysis: {json.dumps(structured_analysis, indent=2)}")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def openai_streaming_example():
    """OpenAI streaming classification example."""
    print("\n🌊 OpenAI Streaming Classification")
    print("=" * 50)
    
    try:
        # Create streaming-enabled configuration
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            temperature=0.2
        )
        
        workflow_config = WorkflowConfig(
            name="streaming_classification",
            primary_provider=provider_config,
            system_prompt="You are a real-time text classifier. Provide streaming analysis.",
            user_prompt_template="Classify and analyze this text in real-time: {text}"
        )
        
        engine = ClassificationEngine(config=workflow_config)
        await engine.initialize()
        
        # Long text for streaming demonstration
        long_text = """
        This product review is quite comprehensive and covers multiple aspects of the user experience. 
        Initially, I was skeptical about the claims made in the marketing materials, but after using 
        the product for several weeks, I can confidently say that it has exceeded my expectations in 
        most areas. The build quality is exceptional, with attention to detail that's rarely seen in 
        this price range. The user interface is intuitive and well-designed, making it easy for both 
        beginners and advanced users to navigate effectively. However, there are some minor issues 
        with the mobile app that could use improvement. The customer support team has been responsive 
        and helpful whenever I've had questions. Overall, I would recommend this product to others, 
        though potential buyers should be aware of the learning curve involved in mastering all features.
        """
        
        print("Streaming classification analysis...")
        print("Real-time response: ", end="", flush=True)
        
        # Note: This is a simplified streaming example
        # In a real implementation, you would use the provider's streaming capabilities
        result = await engine.classify(long_text.strip())
        
        # Simulate streaming output
        response_parts = [
            "Analyzing sentiment... ",
            "Detecting mixed emotions... ",
            "Identifying key topics... ",
            "Calculating confidence... ",
            f"Classification complete: {result.primary_category} (confidence: {result.confidence:.3f})"
        ]
        
        for part in response_parts:
            print(part, end="", flush=True)
            await asyncio.sleep(0.5)  # Simulate streaming delay
        
        print(f"\n\nFinal Result:")
        print(f"  Category: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Processing time: {result.processing_time_ms:.1f}ms")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def openai_cost_optimization_example():
    """OpenAI cost optimization and monitoring example."""
    print("\n💰 OpenAI Cost Optimization")
    print("=" * 50)
    
    try:
        # Create cost-optimized configuration
        cost_optimized_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",  # More cost-effective than GPT-4
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            temperature=0.1,
            max_tokens=200,  # Limit tokens for cost control
            cost_per_token=0.000002  # Approximate cost per token
        )
        
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            categories=["positive", "negative", "neutral"]
        )
        
        await engine.initialize()
        
        # Test texts for cost analysis
        test_texts = [
            "Great product!",
            "Not satisfied with the quality.",
            "Average performance, nothing special.",
            "Excellent customer service experience.",
            "Product arrived damaged, very disappointed."
        ]
        
        total_cost = 0.0
        print("Processing texts with cost tracking...")
        
        for i, text in enumerate(test_texts, 1):
            # Estimate cost before processing
            estimated_cost = await engine.primary_provider.estimate_cost(text)
            
            result = await engine.classify(text)
            
            print(f"\n{i}. Text: {text}")
            print(f"   Category: {result.primary_category}")
            print(f"   Confidence: {result.confidence:.3f}")
            print(f"   Estimated cost: ${estimated_cost:.6f}")
            print(f"   Processing time: {result.processing_time_ms:.1f}ms")
            
            total_cost += estimated_cost
        
        # Get usage statistics
        usage_stats = await engine.get_usage_stats()
        
        print(f"\n📊 Usage Statistics:")
        print(f"   Total estimated cost: ${total_cost:.6f}")
        print(f"   Total requests: {usage_stats['workflow']['total_executions']}")
        print(f"   Average processing time: {usage_stats['workflow']['average_duration_ms']:.1f}ms")
        
        # Provider-specific stats
        if 'providers' in usage_stats:
            for provider_name, stats in usage_stats['providers'].items():
                if 'error' not in stats:
                    print(f"   {provider_name} requests: {stats.get('total_requests', 0)}")
                    print(f"   {provider_name} cost: ${stats.get('total_cost_usd', 0):.6f}")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def openai_error_handling_example():
    """OpenAI error handling and resilience example."""
    print("\n🛡️ OpenAI Error Handling & Resilience")
    print("=" * 50)
    
    try:
        # Create configuration with retry settings
        resilient_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key"),
            max_retries=3,
            timeout_seconds=30,
            requests_per_minute=60,  # Rate limiting
            tokens_per_minute=10000
        )
        
        workflow_config = WorkflowConfig(
            name="resilient_classification",
            primary_provider=resilient_config,
            enable_fallback=True,
            categories=["positive", "negative", "neutral"]
        )
        
        engine = ClassificationEngine(config=workflow_config)
        await engine.initialize()
        
        # Test various scenarios
        test_scenarios = [
            ("Normal text", "This is a great product that I really enjoy using."),
            ("Very long text", "x" * 5000),  # Test token limits
            ("Empty text", ""),  # Test validation
            ("Special characters", "🎉✨ Amazing product! 💯🔥 Highly recommend! 🌟⭐"),
            ("Mixed languages", "Excellent product! Très bon! 素晴らしい製品！")
        ]
        
        print("Testing error handling scenarios...")
        
        for scenario_name, text in test_scenarios:
            print(f"\n🧪 Testing: {scenario_name}")
            
            try:
                if text:  # Skip empty text test for now
                    result = await engine.classify(text[:1000])  # Truncate very long text
                    print(f"   ✅ Success: {result.primary_category} (confidence: {result.confidence:.3f})")
                else:
                    print(f"   ⚠️ Skipped: Empty text validation")
                    
            except Exception as e:
                print(f"   ❌ Error handled: {type(e).__name__}: {e}")
        
        # Test health monitoring
        print(f"\n🏥 Health Check:")
        health_status = await engine.get_health_status()
        print(f"   Overall status: {health_status['overall_status']}")
        
        if 'providers' in health_status:
            for provider_name, provider_health in health_status['providers'].items():
                print(f"   {provider_name}: {provider_health.get('status', 'unknown')}")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all OpenAI examples."""
    print("🤖 OpenAI Provider Examples")
    print("=" * 60)
    print("Demonstrating comprehensive OpenAI integration capabilities")
    print("=" * 60)
    
    examples = [
        basic_openai_classification,
        gpt4_advanced_classification,
        openai_function_calling_example,
        openai_streaming_example,
        openai_cost_optimization_example,
        openai_error_handling_example
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
        
        print("\n" + "="*60)
    
    print("✅ All OpenAI examples completed!")
    print("\n💡 Key Takeaways:")
    print("• OpenAI provider supports GPT-3.5 and GPT-4 models")
    print("• Function calling enables structured output")
    print("• Streaming provides real-time responses")
    print("• Cost optimization helps manage API expenses")
    print("• Comprehensive error handling ensures reliability")
    print("• Health monitoring provides operational insights")


if __name__ == "__main__":
    asyncio.run(main())
