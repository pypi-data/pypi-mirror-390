"""
End-to-end integration tests for the text classification library.

These tests validate the complete workflow from configuration to classification
using real provider APIs (with test credentials).
"""

import pytest
import asyncio
import os
from typing import List, Dict, Any

from evolvishub_text_classification_llm import (
    ClassificationEngine,
    BatchProcessor,
    WorkflowConfig,
    ProviderConfig,
    ProviderType,
    ClassificationInput,
    LibraryConfig
)
from evolvishub_text_classification_llm.core.exceptions import (
    ProviderError, ConfigurationError, WorkflowError
)


# Test configuration
TEST_TEXTS = [
    "I absolutely love this product! It's amazing and works perfectly.",
    "This is the worst purchase I've ever made. Complete waste of money.",
    "The product is okay, nothing special but does what it's supposed to do.",
    "Great quality but the price is too high. Mixed feelings about this.",
    "Customer service was excellent, but the product arrived damaged."
]

EXPECTED_CATEGORIES = ["positive", "negative", "neutral", "mixed"]


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_simple_classification_workflow(self):
        """Test simple classification workflow with OpenAI."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Create simple engine
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
            categories=EXPECTED_CATEGORIES
        )
        
        try:
            await engine.initialize()
            
            # Test single classification
            result = await engine.classify(TEST_TEXTS[0])
            
            assert result is not None
            assert result.primary_category in EXPECTED_CATEGORIES
            assert 0.0 <= result.confidence <= 1.0
            assert result.processing_time_ms > 0
            assert result.provider == "openai"
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_configuration_driven_workflow(self):
        """Test configuration-driven workflow setup."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Create configuration
        config_dict = {
            "library_name": "test-classifier",
            "environment": "test",
            "default_provider": "openai",
            "providers": {
                "openai": {
                    "provider_type": "openai",
                    "model": "gpt-3.5-turbo",
                    "api_key": api_key,
                    "temperature": 0.1,
                    "max_tokens": 500
                }
            },
            "workflows": {
                "test_classification": {
                    "name": "test_classification",
                    "primary_provider": {
                        "provider_type": "openai",
                        "model": "gpt-3.5-turbo",
                        "api_key": api_key,
                        "temperature": 0.1
                    },
                    "categories": EXPECTED_CATEGORIES,
                    "system_prompt": "You are a sentiment analysis expert.",
                    "min_confidence_threshold": 0.5
                }
            }
        }
        
        # Create engine from configuration
        engine = ClassificationEngine.from_dict(config_dict)
        
        try:
            await engine.initialize()
            
            # Test classification
            result = await engine.classify(TEST_TEXTS[1])
            
            assert result is not None
            assert result.primary_category in EXPECTED_CATEGORIES
            assert result.confidence >= 0.5  # Should meet threshold
            
            # Test health status
            health = await engine.get_health_status()
            assert health["overall_status"] in ["healthy", "degraded"]
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self):
        """Test batch processing workflow."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Create engine
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
            categories=EXPECTED_CATEGORIES
        )
        
        try:
            await engine.initialize()
            
            # Create batch processor
            processor = BatchProcessor(
                engine=engine,
                max_concurrent=3,
                batch_size=10
            )
            
            # Process batch
            results = await processor.process_batch(TEST_TEXTS)
            
            assert len(results) == len(TEST_TEXTS)
            
            for result in results:
                assert result is not None
                assert result.primary_category in EXPECTED_CATEGORIES
                assert 0.0 <= result.confidence <= 1.0
                assert result.processing_time_ms > 0
            
            # Check processing stats
            stats = processor.get_processing_stats()
            assert stats["total_items"] == len(TEST_TEXTS)
            assert stats["successful_items"] > 0
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_provider_fallback_workflow(self):
        """Test provider fallback functionality."""
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not openai_key:
            pytest.skip("OpenAI API key not available")
        
        # Create primary provider (OpenAI)
        primary_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key=openai_key,
            timeout_seconds=5  # Short timeout to test fallback
        )
        
        # Create fallback providers
        fallback_configs = []
        if anthropic_key:
            fallback_configs.append(ProviderConfig(
                provider_type=ProviderType.ANTHROPIC,
                model="claude-3-haiku",
                api_key=anthropic_key
            ))
        
        # Create workflow with fallback
        workflow_config = WorkflowConfig(
            name="fallback_test",
            primary_provider=primary_config,
            fallback_providers=fallback_configs,
            enable_fallback=True,
            categories=EXPECTED_CATEGORIES
        )
        
        engine = ClassificationEngine(config=workflow_config)
        
        try:
            await engine.initialize()
            
            # Test classification (should use primary provider)
            result = await engine.classify(TEST_TEXTS[0])
            
            assert result is not None
            assert result.primary_category in EXPECTED_CATEGORIES
            # Provider could be primary or fallback depending on availability
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        # Test with invalid API key
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key="invalid-key",
            categories=EXPECTED_CATEGORIES
        )
        
        # Should fail during initialization
        with pytest.raises((ProviderError, ConfigurationError)):
            await engine.initialize()
        
        # Test with invalid model
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            engine2 = ClassificationEngine.create_simple(
                provider_type="openai",
                model="invalid-model",
                api_key=api_key,
                categories=EXPECTED_CATEGORIES
            )
            
            try:
                await engine2.initialize()
                
                # Should handle invalid model gracefully
                with pytest.raises(ProviderError):
                    await engine2.classify("Test text")
                    
            except Exception:
                # Expected to fail during initialization or classification
                pass
            finally:
                await engine2.cleanup()
    
    @pytest.mark.asyncio
    async def test_monitoring_and_metrics(self):
        """Test monitoring and metrics collection."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Create engine with monitoring enabled
        config_dict = {
            "library_name": "monitoring-test",
            "providers": {
                "openai": {
                    "provider_type": "openai",
                    "model": "gpt-3.5-turbo",
                    "api_key": api_key
                }
            },
            "monitoring": {
                "enabled": True,
                "enable_metrics": True,
                "enable_performance_tracking": True
            }
        }
        
        engine = ClassificationEngine.from_dict(config_dict)
        
        try:
            await engine.initialize()
            
            # Perform several classifications
            for text in TEST_TEXTS[:3]:
                await engine.classify(text)
            
            # Check usage statistics
            stats = await engine.get_usage_stats()
            
            assert "workflow" in stats
            assert "providers" in stats
            
            workflow_stats = stats["workflow"]
            assert workflow_stats["total_executions"] >= 3
            assert workflow_stats["successful_executions"] >= 0
            assert "average_duration_ms" in workflow_stats
            
            # Check health status
            health = await engine.get_health_status()
            assert "overall_status" in health
            assert "providers" in health
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_custom_workflow_nodes(self):
        """Test custom workflow with preprocessing and validation."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Create workflow with custom configuration
        workflow_config = WorkflowConfig(
            name="custom_workflow",
            primary_provider=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="gpt-3.5-turbo",
                api_key=api_key,
                temperature=0.1
            ),
            categories=EXPECTED_CATEGORIES,
            system_prompt="You are an expert text classifier with high accuracy.",
            user_prompt_template="""Classify this text with confidence:

Text: {text}

Provide classification with reasoning.""",
            min_confidence_threshold=0.6,
            enable_preprocessing=True,
            enable_validation=True
        )
        
        engine = ClassificationEngine(config=workflow_config)
        
        try:
            await engine.initialize()
            
            # Test with text that needs preprocessing
            messy_text = "   I LOVE this product!!!   It's AMAZING!!!   "
            result = await engine.classify(messy_text)
            
            assert result is not None
            assert result.primary_category in EXPECTED_CATEGORIES
            assert result.confidence >= 0.6  # Should meet threshold
            
            # Test workflow info
            workflow_info = await engine.workflow.get_workflow_info()
            assert workflow_info["name"] == "custom_workflow"
            assert "nodes" in workflow_info
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent processing capabilities."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
            categories=EXPECTED_CATEGORIES
        )
        
        try:
            await engine.initialize()
            
            # Create multiple concurrent classification tasks
            tasks = []
            for text in TEST_TEXTS:
                task = engine.classify(text)
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= len(TEST_TEXTS) // 2  # At least half should succeed
            
            for result in successful_results:
                assert result.primary_category in EXPECTED_CATEGORIES
                assert 0.0 <= result.confidence <= 1.0
            
        finally:
            await engine.cleanup()


@pytest.mark.integration
class TestProviderIntegration:
    """Test integration with different providers."""
    
    @pytest.mark.asyncio
    async def test_openai_integration(self):
        """Test OpenAI provider integration."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-3.5-turbo",
            api_key=api_key,
            temperature=0.1,
            max_tokens=200
        )
        
        from evolvishub_text_classification_llm.providers.factory import ProviderFactory
        provider = ProviderFactory.create_provider(config)
        
        try:
            await provider.initialize()
            
            # Test health check
            health = await provider.health_check()
            assert health["status"] == "healthy"
            
            # Test generation
            messages = [{"role": "user", "content": "Classify sentiment: I love this!"}]
            response = await provider.generate(messages)
            
            assert isinstance(response, str)
            assert len(response) > 0
            
            # Test usage stats
            stats = await provider.get_usage_stats()
            assert "total_requests" in stats
            
        finally:
            await provider.cleanup()
    
    @pytest.mark.asyncio
    async def test_anthropic_integration(self):
        """Test Anthropic provider integration."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("Anthropic API key not available")
        
        config = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            model="claude-3-haiku",
            api_key=api_key,
            temperature=0.1,
            max_tokens=200
        )
        
        from evolvishub_text_classification_llm.providers.factory import ProviderFactory
        provider = ProviderFactory.create_provider(config)
        
        try:
            await provider.initialize()
            
            # Test health check
            health = await provider.health_check()
            assert health["status"] == "healthy"
            
            # Test generation
            messages = [{"role": "user", "content": "Classify sentiment: This is terrible!"}]
            response = await provider.generate(messages)
            
            assert isinstance(response, str)
            assert len(response) > 0
            
        finally:
            await provider.cleanup()


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    @pytest.mark.asyncio
    async def test_customer_service_scenario(self):
        """Test customer service email classification scenario."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Customer service categories
        categories = [
            "complaint_billing", "complaint_service", "complaint_technical",
            "inquiry_general", "inquiry_billing", "compliment_service",
            "urgent_issue", "routine_communication"
        ]
        
        # Sample customer emails
        customer_emails = [
            "URGENT: My account has been charged twice for the same service!",
            "Thank you for the excellent customer support yesterday.",
            "I have a question about my billing statement.",
            "The app keeps crashing when I try to upload files.",
            "Can someone please help me reset my password?"
        ]
        
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-4",
            api_key=api_key,
            categories=categories
        )
        
        try:
            await engine.initialize()
            
            results = []
            for email in customer_emails:
                result = await engine.classify(email)
                results.append(result)
            
            # Validate results
            assert len(results) == len(customer_emails)
            
            for result in results:
                assert result.primary_category in categories
                assert 0.0 <= result.confidence <= 1.0
            
            # Check that urgent email is classified appropriately
            urgent_result = results[0]  # First email is urgent
            assert "urgent" in urgent_result.primary_category or result.confidence > 0.8
            
        finally:
            await engine.cleanup()
    
    @pytest.mark.asyncio
    async def test_content_moderation_scenario(self):
        """Test content moderation scenario."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OpenAI API key not available")
        
        # Content moderation categories
        categories = [
            "safe_content", "inappropriate_language", "spam",
            "harassment", "adult_content", "violence"
        ]
        
        # Sample content
        content_samples = [
            "This is a great product review. Highly recommended!",
            "Check out this amazing deal! Click here now!!!",
            "What a beautiful sunset photo.",
            "This tutorial is very helpful for beginners.",
            "Thanks for sharing this interesting article."
        ]
        
        engine = ClassificationEngine.create_simple(
            provider_type="openai",
            model="gpt-3.5-turbo",
            api_key=api_key,
            categories=categories
        )
        
        try:
            await engine.initialize()
            
            # Process content batch
            processor = BatchProcessor(engine=engine, max_concurrent=3)
            results = await processor.process_batch(content_samples)
            
            # Validate results
            assert len(results) == len(content_samples)
            
            # Most content should be classified as safe
            safe_count = sum(1 for r in results if r.primary_category == "safe_content")
            assert safe_count >= len(content_samples) // 2
            
        finally:
            await engine.cleanup()
