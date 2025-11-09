"""
Integration tests for provider functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from evolvishub_text_classification_llm import (
    ProviderFactory, ClassificationEngine, HealthChecker, MetricsCollector
)
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType, WorkflowConfig
from evolvishub_text_classification_llm.core.exceptions import ProviderError


class TestProviderIntegration:
    """Integration tests for provider functionality."""
    
    def test_provider_factory_registration(self):
        """Test that all providers are properly registered."""
        supported_providers = ProviderFactory.get_supported_providers()
        
        # Should have at least these providers
        expected_providers = [
            "openai", "cohere", "azure_openai", "aws_bedrock", 
            "huggingface", "ollama", "custom"
        ]
        
        for provider in expected_providers:
            assert provider in supported_providers, f"Provider {provider} not registered"
        
        # Should have 10+ providers as documented
        assert len(supported_providers) >= 10, f"Expected 10+ providers, got {len(supported_providers)}"
    
    def test_provider_availability_check(self):
        """Test provider availability checking."""
        # These providers should always be available (no external dependencies)
        always_available = ["custom"]
        
        for provider in always_available:
            assert ProviderFactory.is_provider_available(provider), f"Provider {provider} should be available"
        
        # Test non-existent provider
        assert not ProviderFactory.is_provider_available("non_existent_provider")
    
    def test_provider_capabilities(self):
        """Test provider capability reporting."""
        capabilities = ProviderFactory.get_provider_capabilities("openai")
        
        assert isinstance(capabilities, dict)
        assert "streaming" in capabilities
        assert "function_calling" in capabilities
        assert "cost_estimation" in capabilities
        assert "health_checks" in capabilities
    
    @pytest.mark.asyncio
    async def test_provider_creation_and_initialization(self):
        """Test creating and initializing providers."""
        # Test with mock configuration
        config = ProviderConfig(
            provider_type=ProviderType.CUSTOM,
            api_key="test-key",
            model="test-model",
            base_url="http://localhost:8000",
            max_tokens=100,
            temperature=0.7
        )
        
        provider = ProviderFactory.create_provider(config)
        assert provider is not None
        assert provider.config == config
        
        # Test initialization (should fail gracefully with mock config)
        try:
            await provider.initialize()
        except ProviderError:
            # Expected for mock configuration
            pass
    
    @pytest.mark.asyncio
    async def test_health_checker_with_providers(self):
        """Test health checker integration with providers."""
        health_checker = HealthChecker(check_interval_seconds=1, timeout_seconds=5)
        
        # Create a mock provider
        mock_provider = Mock()
        mock_provider.health_check = AsyncMock(return_value={
            "status": "healthy",
            "message": "Provider operational"
        })
        
        # Register provider
        health_checker.register_provider("test_provider", mock_provider)
        
        # Perform health check
        system_health = await health_checker.perform_health_check()
        
        assert system_health.overall_status.value in ["healthy", "warning"]  # Might be warning due to system resources
        assert len(system_health.components) >= 2  # At least provider + system resources
        
        # Check that provider was checked
        provider_results = [c for c in system_health.components if c.component == "provider_test_provider"]
        assert len(provider_results) == 1
        assert provider_results[0].status.value == "healthy"
    
    @pytest.mark.asyncio
    async def test_metrics_collector_with_providers(self):
        """Test metrics collector integration."""
        metrics = MetricsCollector(aggregation_interval_seconds=1)
        
        # Simulate provider metrics
        metrics.record_counter("provider.requests", 10)
        metrics.record_gauge("provider.active_connections", 5)
        metrics.record_histogram("provider.response_time_ms", 150)
        metrics.record_timer("provider.generation_time_ms", 500)
        
        # Test metrics collection
        all_metrics = metrics.get_all_metrics()
        
        assert all_metrics["counters"]["provider.requests"] == 10
        assert all_metrics["gauges"]["provider.active_connections"] == 5
        assert all_metrics["histograms"]["provider.response_time_ms"] == 1
        assert all_metrics["timers"]["provider.generation_time_ms"] == 1
        
        # Test aggregation
        await metrics._aggregate_metrics()
        
        summary = metrics.get_metric_summary("provider.response_time_ms")
        assert summary is not None
        assert summary.count == 1
        assert summary.last_value == 150
    
    @pytest.mark.asyncio
    async def test_classification_engine_with_monitoring(self):
        """Test classification engine with monitoring integration."""
        # Create a mock workflow config
        workflow_config = WorkflowConfig(
            name="test_workflow",
            description="Test workflow",
            providers=[
                ProviderConfig(
                    provider_type=ProviderType.CUSTOM,
                    api_key="test-key",
                    model="test-model",
                    base_url="http://localhost:8000"
                )
            ]
        )
        
        # Create classification engine
        engine = ClassificationEngine(config=workflow_config)
        
        # Test that engine can be created without errors
        assert engine is not None
        assert engine.config == workflow_config
    
    def test_provider_factory_error_handling(self):
        """Test provider factory error handling."""
        # Test with invalid provider type
        with pytest.raises(ProviderError) as exc_info:
            invalid_config = ProviderConfig(
                provider_type="invalid_provider",  # This should cause an error
                api_key="test-key",
                model="test-model"
            )
            ProviderFactory.create_provider(invalid_config)
        
        assert "Unsupported provider type" in str(exc_info.value)
    
    def test_provider_metadata(self):
        """Test provider metadata functionality."""
        # Test that we can get provider metadata
        providers = ProviderFactory.get_supported_providers()
        
        for provider_type in providers:
            capabilities = ProviderFactory.get_provider_capabilities(provider_type)
            assert isinstance(capabilities, dict)
            
            # All providers should support basic capabilities
            assert capabilities.get("cost_estimation", False)
            assert capabilities.get("health_checks", False)
    
    @pytest.mark.asyncio
    async def test_multiple_provider_creation(self):
        """Test creating multiple providers."""
        configs = [
            ProviderConfig(
                provider_type=ProviderType.CUSTOM,
                api_key="test-key-1",
                model="model-1",
                base_url="http://localhost:8001"
            ),
            ProviderConfig(
                provider_type=ProviderType.CUSTOM,
                api_key="test-key-2", 
                model="model-2",
                base_url="http://localhost:8002"
            )
        ]
        
        providers = ProviderFactory.create_multiple_providers(configs)
        
        assert len(providers) == 2
        assert providers[0].config.model == "model-1"
        assert providers[1].config.model == "model-2"
    
    def test_provider_recommendation(self):
        """Test provider recommendation functionality."""
        # Test with no requirements (should return default)
        recommended = ProviderFactory.recommend_provider()
        assert recommended is None or recommended in ProviderFactory.get_supported_providers()
        
        # Test with specific requirements
        requirements = {
            "streaming": True,
            "function_calling": False,
            "local_inference": True
        }
        
        recommended = ProviderFactory.recommend_provider(requirements)
        if recommended:
            assert recommended in ProviderFactory.get_supported_providers()
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow with monitoring."""
        # Create health checker and metrics collector
        health_checker = HealthChecker(check_interval_seconds=1)
        metrics_collector = MetricsCollector(aggregation_interval_seconds=1)
        
        # Create a mock provider for testing
        mock_provider = Mock()
        mock_provider.health_check = AsyncMock(return_value={
            "status": "healthy",
            "message": "Mock provider operational",
            "response_time_ms": 50
        })
        mock_provider.get_usage_stats = AsyncMock(return_value={
            "requests": 100,
            "tokens": 10000,
            "errors": 2,
            "total_cost_usd": 0.50
        })
        
        # Register provider with health checker
        health_checker.register_provider("mock_provider", mock_provider)
        
        # Simulate some metrics
        metrics_collector.record_counter("requests_total", 100)
        metrics_collector.record_gauge("active_providers", 1)
        metrics_collector.record_histogram("response_time_ms", 150)
        
        # Perform health check
        system_health = await health_checker.perform_health_check()
        assert len(system_health.components) >= 2
        
        # Aggregate metrics
        await metrics_collector._aggregate_metrics()
        
        # Get comprehensive status
        health_summary = health_checker.get_health_summary()
        all_metrics = metrics_collector.get_all_metrics()
        
        assert health_summary["total_components"] >= 2
        assert all_metrics["counters"]["requests_total"] == 100
        assert all_metrics["gauges"]["active_providers"] == 1
        
        # Test metrics export
        json_export = metrics_collector.export_metrics("json")
        assert "requests_total" in json_export
        
        prometheus_export = metrics_collector.export_metrics("prometheus")
        assert "requests_total 100.0" in prometheus_export
    
    def test_library_feature_flags(self):
        """Test that library feature flags are properly set."""
        from evolvishub_text_classification_llm import get_features
        
        features = get_features()
        
        # Check that all documented features are present
        expected_features = [
            "batch_processing", "caching", "semantic_caching", "monitoring",
            "streaming", "real_time_streaming", "websocket_support", "async_support",
            "provider_fallback", "cost_optimization", "security_features",
            "workflow_templates", "fine_tuning", "multimodal", "langgraph_integration"
        ]
        
        for feature in expected_features:
            assert feature in features, f"Feature {feature} not found in feature flags"
            assert features[feature] is True, f"Feature {feature} is not enabled"
    
    def test_library_provider_count(self):
        """Test that library has the documented number of providers."""
        from evolvishub_text_classification_llm import get_supported_providers
        
        providers = get_supported_providers()
        
        # Should have 10+ providers as documented
        assert len(providers) >= 10, f"Expected 10+ providers, got {len(providers)}: {providers}"
        
        # Check for specific providers mentioned in documentation
        documented_providers = [
            "openai", "anthropic", "google", "cohere", "mistral", "replicate",
            "azure_openai", "aws_bedrock", "huggingface", "ollama", "custom"
        ]
        
        for provider in documented_providers:
            assert provider in providers, f"Documented provider {provider} not found in supported providers"
