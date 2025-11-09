#!/usr/bin/env python3
"""
Comprehensive example of the Evolvishub Text Classification LLM Library.

This example demonstrates various usage patterns including:
- Simple classification setup
- Configuration-driven setup
- Batch processing
- Custom workflows
- Multiple provider usage
- Error handling and monitoring
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Import the library
from evolvishub_text_classification_llm import (
    ClassificationEngine,
    BatchProcessor,
    WorkflowBuilder,
    ProviderFactory,
    LibraryConfig,
    WorkflowConfig,
    ProviderConfig,
    ProviderType,
    create_engine,
    create_batch_processor
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_simple_classification():
    """Example 1: Simple classification with minimal setup."""
    print("\n🔍 Example 1: Simple Classification")
    print("=" * 50)
    
    try:
        # Create a simple classification engine
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key="your-openai-api-key",  # Replace with actual key
            categories=["positive", "negative", "neutral"]
        )
        
        # Initialize the engine
        await engine.initialize()
        
        # Classify some texts
        sample_texts = [
            "I love this product! It's amazing!",
            "This is terrible, I hate it.",
            "It's okay, nothing special.",
            "Best purchase I've ever made!",
            "Worst experience ever, very disappointed."
        ]
        
        for text in sample_texts:
            result = await engine.classify(text)
            print(f"Text: {text[:50]}...")
            print(f"Category: {result.primary_category}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"All categories: {result.categories}")
            print("-" * 30)
        
        # Cleanup
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_configuration_driven():
    """Example 2: Configuration-driven setup with YAML config."""
    print("\n🔍 Example 2: Configuration-Driven Setup")
    print("=" * 50)
    
    # Create configuration dictionary (normally loaded from YAML file)
    config_dict = {
        "library_name": "text-classification-demo",
        "environment": "development",
        "default_provider": "openai",
        
        "providers": {
            "openai": {
                "provider_type": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "${OPENAI_API_KEY}",
                "temperature": 0.1,
                "max_tokens": 500,
                "timeout_seconds": 30
            },
            "huggingface": {
                "provider_type": "huggingface",
                "model": "microsoft/DialoGPT-medium",
                "device": "auto",
                "quantization": True,
                "cache_dir": "./models"
            }
        },
        
        "workflows": {
            "sentiment_analysis": {
                "name": "sentiment_analysis",
                "workflow_type": "classification",
                "primary_provider": {
                    "provider_type": "openai",
                    "model": "gpt-3.5-turbo",
                    "api_key": "${OPENAI_API_KEY}",
                    "temperature": 0.1
                },
                "categories": ["positive", "negative", "neutral"],
                "system_prompt": "You are a sentiment analysis expert.",
                "user_prompt_template": "Analyze the sentiment of this text: {text}",
                "min_confidence_threshold": 0.7
            }
        },
        
        "cache": {
            "enabled": True,
            "cache_type": "memory",
            "max_memory_items": 1000
        },
        
        "monitoring": {
            "enabled": True,
            "log_level": "INFO"
        }
    }
    
    try:
        # Create engine from configuration
        engine = ClassificationEngine.from_dict(config_dict)
        await engine.initialize()
        
        # Test classification
        result = await engine.classify(
            "This product exceeded my expectations! Highly recommended.",
            metadata={"source": "product_review", "rating": 5}
        )
        
        print(f"Classification Result:")
        print(f"  Category: {result.primary_category}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Provider: {result.provider}")
        print(f"  Processing time: {result.processing_time_ms:.1f}ms")
        
        # Get health status
        health = await engine.get_health_status()
        print(f"\nEngine Health: {health['overall_status']}")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_batch_processing():
    """Example 3: Batch processing with progress tracking."""
    print("\n🔍 Example 3: Batch Processing")
    print("=" * 50)
    
    try:
        # Create engine
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key="your-openai-api-key",
            categories=["complaint", "compliment", "inquiry", "urgent"]
        )
        
        # Create batch processor with progress callback
        def progress_callback(progress):
            print(f"Progress: {progress.progress_percentage:.1f}% "
                  f"({progress.processed_items}/{progress.total_items}) "
                  f"- Success rate: {progress.success_rate:.1f}%")
        
        batch_processor = BatchProcessor(
            engine=engine,
            max_concurrent=5,
            progress_callback=progress_callback
        )
        
        # Sample customer service texts
        customer_texts = [
            "I'm very unhappy with the service I received yesterday.",
            "Thank you for the excellent customer support!",
            "Can you please help me with my account settings?",
            "URGENT: My system is down and I need immediate assistance!",
            "The product quality is outstanding, keep up the good work.",
            "I have a question about my billing statement.",
            "This is the worst experience I've ever had with your company.",
            "Your team was very helpful and professional.",
            "How do I reset my password?",
            "EMERGENCY: Data breach detected, please contact me ASAP!"
        ]
        
        # Process batch
        print("Starting batch processing...")
        batch_result = await batch_processor.process_batch(customer_texts)
        
        # Display results
        print(f"\nBatch Processing Results:")
        print(f"  Total items: {batch_result.total_items}")
        print(f"  Successful: {batch_result.successful_items}")
        print(f"  Failed: {batch_result.failed_items}")
        print(f"  Success rate: {batch_result.success_rate:.1f}%")
        print(f"  Average processing time: {batch_result.average_processing_time_ms:.1f}ms")
        print(f"  Throughput: {batch_result.throughput_items_per_second:.1f} items/sec")
        
        # Show category distribution
        print(f"\nCategory Distribution:")
        for category, count in batch_result.get_statistics()["provider_usage"].items():
            print(f"  {category}: {count}")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_custom_workflow():
    """Example 4: Custom workflow with multiple processing steps."""
    print("\n🔍 Example 4: Custom Workflow")
    print("=" * 50)
    
    try:
        # Create provider
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key="your-openai-api-key",
            temperature=0.1
        )
        
        provider = ProviderFactory.create_provider(provider_config)
        await provider.initialize()
        
        # Create workflow configuration
        workflow_config = WorkflowConfig(
            name="custom_email_classifier",
            primary_provider=provider_config,
            categories=[
                "customer_complaint", "feature_request", "bug_report",
                "sales_inquiry", "support_request", "compliment"
            ],
            system_prompt="""You are an expert email classifier for a software company.
            Classify emails into appropriate categories based on their content and intent.""",
            user_prompt_template="""Classify this email:

Subject: {subject}
Content: {text}

Provide a JSON response with:
- primary_category: the most relevant category
- confidence: confidence score (0.0-1.0)
- reasoning: brief explanation of the classification""",
            min_confidence_threshold=0.6
        )
        
        # Build custom workflow
        workflow = (WorkflowBuilder()
            .create(workflow_config)
            .add_preprocessing(["clean_whitespace", "remove_urls"])
            .add_classification(
                provider=provider,
                system_prompt=workflow_config.system_prompt,
                user_prompt_template=workflow_config.user_prompt_template,
                temperature=0.1
            )
            .add_validation(min_confidence=0.6)
            .add_postprocessing()
            .build())
        
        # Test the workflow
        sample_emails = [
            {
                "subject": "Bug in login system",
                "text": "I can't log into my account. The system keeps saying invalid credentials even though I'm using the correct password."
            },
            {
                "subject": "Feature request: Dark mode",
                "text": "Would it be possible to add a dark mode option to the application? Many users have been requesting this feature."
            },
            {
                "subject": "Excellent customer service!",
                "text": "I wanted to thank your support team for their quick response and helpful solution to my problem."
            }
        ]
        
        for email in sample_emails:
            # Format the text with subject
            formatted_text = f"Subject: {email['subject']}\nContent: {email['text']}"
            
            from evolvishub_text_classification_llm.core.schemas import ClassificationInput
            input_data = ClassificationInput(
                text=formatted_text,
                metadata={"subject": email["subject"]}
            )
            
            result = await workflow.execute(input_data)
            
            print(f"Email: {email['subject']}")
            print(f"Category: {result.primary_category}")
            print(f"Confidence: {result.confidence:.2f}")
            if result.reasoning:
                print(f"Reasoning: {result.reasoning}")
            print("-" * 30)
        
        await provider.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_multiple_providers():
    """Example 5: Using multiple providers with fallback."""
    print("\n🔍 Example 5: Multiple Providers with Fallback")
    print("=" * 50)
    
    try:
        # Create multiple provider configurations
        openai_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key="your-openai-api-key",
            priority=1  # Highest priority
        )
        
        huggingface_config = ProviderConfig(
            provider_type=ProviderType.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            device="auto",
            quantization=True,
            priority=2  # Fallback
        )
        
        # Create workflow with fallback providers
        workflow_config = WorkflowConfig(
            name="multi_provider_classification",
            primary_provider=openai_config,
            fallback_providers=[huggingface_config],
            enable_fallback=True,
            categories=["positive", "negative", "neutral"]
        )
        
        # Create engine
        engine = ClassificationEngine(config=workflow_config)
        await engine.initialize()
        
        # Test classification
        result = await engine.classify("This is a great product!")
        
        print(f"Classification Result:")
        print(f"  Category: {result.primary_category}")
        print(f"  Provider used: {result.provider}")
        print(f"  Model: {result.model_version}")
        print(f"  Confidence: {result.confidence:.2f}")
        
        # Get usage stats for all providers
        usage_stats = await engine.get_usage_stats()
        print(f"\nProvider Usage Stats:")
        for provider_name, stats in usage_stats["providers"].items():
            if "error" not in stats:
                print(f"  {provider_name}: {stats['total_requests']} requests")
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_monitoring_and_health():
    """Example 6: Monitoring and health checks."""
    print("\n🔍 Example 6: Monitoring and Health Checks")
    print("=" * 50)
    
    try:
        # Create engine with monitoring enabled
        config_dict = {
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "provider_type": "openai",
                    "model": "gpt-3.5-turbo",
                    "api_key": "your-openai-api-key"
                }
            },
            "monitoring": {
                "enabled": True,
                "enable_metrics": True,
                "log_level": "INFO",
                "enable_performance_tracking": True
            }
        }
        
        engine = ClassificationEngine.from_dict(config_dict)
        await engine.initialize()
        
        # Perform some classifications to generate metrics
        test_texts = [
            "Great product!",
            "Not satisfied with the service.",
            "Average quality, nothing special."
        ]
        
        for text in test_texts:
            await engine.classify(text)
        
        # Check health status
        health = await engine.get_health_status()
        print("Health Status:")
        print(json.dumps(health, indent=2, default=str))
        
        # Get usage statistics
        stats = await engine.get_usage_stats()
        print("\nUsage Statistics:")
        print(json.dumps(stats, indent=2, default=str))
        
        await engine.cleanup()
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all examples."""
    print("🧠 Evolvishub Text Classification LLM Library - Examples")
    print("=" * 60)
    
    # Note: These examples require actual API keys to work
    # Replace "your-openai-api-key" with real API keys for testing
    
    examples = [
        example_simple_classification,
        example_configuration_driven,
        example_batch_processing,
        example_custom_workflow,
        example_multiple_providers,
        example_monitoring_and_health
    ]
    
    for example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"❌ Example {example_func.__name__} failed: {e}")
        
        print("\n" + "="*60)
    
    print("✅ All examples completed!")
    print("\n💡 Next steps:")
    print("1. Replace API keys with your actual keys")
    print("2. Customize prompts and categories for your use case")
    print("3. Integrate with your data sources")
    print("4. Set up monitoring and logging")
    print("5. Deploy to production with proper configuration")


if __name__ == "__main__":
    asyncio.run(main())
