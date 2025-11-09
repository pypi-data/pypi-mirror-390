"""
Unit tests for HealthChecker.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from evolvishub_text_classification_llm.monitoring.health import (
    HealthChecker, HealthStatus, HealthCheckResult, SystemHealth
)
from evolvishub_text_classification_llm.core.interfaces import ILLMProvider


@pytest.fixture
def health_checker():
    """Create a HealthChecker instance."""
    return HealthChecker(
        check_interval_seconds=10,
        timeout_seconds=5,
        max_retries=2
    )


@pytest.fixture
def mock_provider():
    """Create a mock LLM provider."""
    provider = Mock(spec=ILLMProvider)
    provider.health_check = AsyncMock(return_value={
        "status": "healthy",
        "message": "Provider is operational"
    })
    return provider


class TestHealthCheckResult:
    """Test cases for HealthCheckResult."""
    
    def test_health_check_result_creation(self):
        """Test creating a health check result."""
        result = HealthCheckResult(
            component="test_component",
            status=HealthStatus.HEALTHY,
            message="Component is healthy",
            response_time_ms=150.0
        )
        
        assert result.component == "test_component"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Component is healthy"
        assert result.response_time_ms == 150.0
        assert result.error is None


class TestSystemHealth:
    """Test cases for SystemHealth."""
    
    def test_system_health_calculation(self):
        """Test system health component counting."""
        components = [
            HealthCheckResult("comp1", HealthStatus.HEALTHY, "OK"),
            HealthCheckResult("comp2", HealthStatus.WARNING, "Warning"),
            HealthCheckResult("comp3", HealthStatus.CRITICAL, "Critical"),
            HealthCheckResult("comp4", HealthStatus.HEALTHY, "OK"),
        ]
        
        health = SystemHealth(
            overall_status=HealthStatus.CRITICAL,
            components=components
        )
        
        assert health.healthy_components == 2
        assert health.warning_components == 1
        assert health.critical_components == 1


class TestHealthChecker:
    """Test cases for HealthChecker."""
    
    def test_initialization(self, health_checker):
        """Test health checker initialization."""
        assert health_checker.check_interval == 10
        assert health_checker.timeout == 5
        assert health_checker.max_retries == 2
        assert not health_checker._running
        assert health_checker._last_check is None
    
    def test_register_provider(self, health_checker, mock_provider):
        """Test registering a provider for monitoring."""
        health_checker.register_provider("test_provider", mock_provider)
        
        assert "test_provider" in health_checker._providers
        assert health_checker._providers["test_provider"] == mock_provider
    
    def test_register_custom_check(self, health_checker):
        """Test registering a custom health check."""
        def custom_check():
            return {"status": "healthy", "message": "Custom check passed"}
        
        health_checker.register_custom_check("custom_test", custom_check)
        
        assert "custom_test" in health_checker._custom_checks
        assert health_checker._custom_checks["custom_test"] == custom_check
    
    @pytest.mark.asyncio
    async def test_check_provider_health_success(self, health_checker, mock_provider):
        """Test successful provider health check."""
        result = await health_checker.check_provider_health("test_provider", mock_provider)
        
        assert result.component == "provider_test_provider"
        assert result.status == HealthStatus.HEALTHY
        assert "test_provider is healthy" in result.message
        assert result.response_time_ms > 0
        mock_provider.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_provider_health_degraded(self, health_checker, mock_provider):
        """Test provider health check with degraded status."""
        mock_provider.health_check.return_value = {
            "status": "degraded",
            "message": "Provider is degraded"
        }
        
        result = await health_checker.check_provider_health("test_provider", mock_provider)
        
        assert result.status == HealthStatus.WARNING
        assert "degraded" in result.message
    
    @pytest.mark.asyncio
    async def test_check_provider_health_timeout(self, health_checker, mock_provider):
        """Test provider health check timeout."""
        mock_provider.health_check.side_effect = asyncio.TimeoutError()
        
        result = await health_checker.check_provider_health("test_provider", mock_provider)
        
        assert result.status == HealthStatus.CRITICAL
        assert "timed out" in result.message
        assert result.error == "timeout"
    
    @pytest.mark.asyncio
    async def test_check_provider_health_exception(self, health_checker, mock_provider):
        """Test provider health check with exception."""
        mock_provider.health_check.side_effect = Exception("Connection failed")
        
        result = await health_checker.check_provider_health("test_provider", mock_provider)
        
        assert result.status == HealthStatus.CRITICAL
        assert "Connection failed" in result.message
        assert result.error == "Connection failed"
    
    @pytest.mark.asyncio
    async def test_check_system_resources_with_psutil(self, health_checker):
        """Test system resource check with psutil available."""
        mock_memory = Mock()
        mock_memory.percent = 50.0
        mock_memory.available = 8 * (1024**3)  # 8GB
        
        with patch('psutil.virtual_memory', return_value=mock_memory), \
             patch('psutil.cpu_percent', return_value=30.0), \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_disk_usage = Mock()
            mock_disk_usage.percent = 60.0
            mock_disk_usage.free = 100 * (1024**3)  # 100GB
            mock_disk.return_value = mock_disk_usage
            
            result = await health_checker.check_system_resources()
            
            assert result.component == "system_resources"
            assert result.status == HealthStatus.HEALTHY
            assert result.details["memory_percent"] == 50.0
            assert result.details["cpu_percent"] == 30.0
            assert result.details["disk_percent"] == 60.0
    
    @pytest.mark.asyncio
    async def test_check_system_resources_critical(self, health_checker):
        """Test system resource check with critical usage."""
        mock_memory = Mock()
        mock_memory.percent = 95.0  # Critical memory usage
        mock_memory.available = 1 * (1024**3)  # 1GB
        
        with patch('psutil.virtual_memory', return_value=mock_memory), \
             patch('psutil.cpu_percent', return_value=95.0), \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_disk_usage = Mock()
            mock_disk_usage.percent = 95.0  # Critical disk usage
            mock_disk_usage.free = 1 * (1024**3)  # 1GB
            mock_disk.return_value = mock_disk_usage
            
            result = await health_checker.check_system_resources()
            
            assert result.status == HealthStatus.CRITICAL
            assert "critically low" in result.message
    
    @pytest.mark.asyncio
    async def test_check_system_resources_no_psutil(self, health_checker):
        """Test system resource check without psutil."""
        with patch('psutil.virtual_memory', side_effect=ImportError()):
            result = await health_checker.check_system_resources()
            
            assert result.status == HealthStatus.UNKNOWN
            assert "psutil not available" in result.message
            assert result.error == "missing_dependency"
    
    @pytest.mark.asyncio
    async def test_run_custom_check_success(self, health_checker):
        """Test running a successful custom check."""
        def custom_check():
            return {
                "status": "healthy",
                "message": "Custom check passed",
                "details": {"value": 42}
            }
        
        result = await health_checker.run_custom_check("test_check", custom_check)
        
        assert result.component == "custom_test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Custom check passed"
        assert result.details["value"] == 42
    
    @pytest.mark.asyncio
    async def test_run_custom_check_async(self, health_checker):
        """Test running an async custom check."""
        async def async_custom_check():
            return {"status": "healthy", "message": "Async check passed"}
        
        result = await health_checker.run_custom_check("async_test", async_custom_check)
        
        assert result.status == HealthStatus.HEALTHY
        assert "Async check passed" in result.message
    
    @pytest.mark.asyncio
    async def test_run_custom_check_exception(self, health_checker):
        """Test custom check with exception."""
        def failing_check():
            raise Exception("Check failed")
        
        result = await health_checker.run_custom_check("failing_check", failing_check)
        
        assert result.status == HealthStatus.CRITICAL
        assert "Check failed" in result.message
        assert result.error == "Check failed"
    
    @pytest.mark.asyncio
    async def test_perform_health_check_comprehensive(self, health_checker, mock_provider):
        """Test comprehensive health check."""
        # Register provider and custom check
        health_checker.register_provider("test_provider", mock_provider)
        health_checker.register_custom_check("custom", lambda: {"status": "healthy"})
        
        with patch.object(health_checker, 'check_system_resources') as mock_system:
            mock_system.return_value = HealthCheckResult(
                "system_resources", HealthStatus.HEALTHY, "System OK"
            )
            
            health = await health_checker.perform_health_check()
            
            assert isinstance(health, SystemHealth)
            assert health.overall_status == HealthStatus.HEALTHY
            assert len(health.components) == 3  # provider + system + custom
            assert health.healthy_components == 3
    
    @pytest.mark.asyncio
    async def test_perform_health_check_with_critical(self, health_checker, mock_provider):
        """Test health check with critical component."""
        mock_provider.health_check.side_effect = Exception("Provider failed")
        health_checker.register_provider("failing_provider", mock_provider)
        
        health = await health_checker.perform_health_check()
        
        assert health.overall_status == HealthStatus.CRITICAL
        assert health.critical_components > 0
    
    @pytest.mark.asyncio
    async def test_perform_health_check_with_warning(self, health_checker, mock_provider):
        """Test health check with warning component."""
        mock_provider.health_check.return_value = {"status": "degraded"}
        health_checker.register_provider("degraded_provider", mock_provider)
        
        health = await health_checker.perform_health_check()
        
        assert health.overall_status == HealthStatus.WARNING
        assert health.warning_components > 0
    
    @pytest.mark.asyncio
    async def test_alert_callback(self, health_checker, mock_provider):
        """Test alert callback functionality."""
        alert_callback = AsyncMock()
        health_checker.alert_callback = alert_callback
        
        # Set up a failing provider to trigger alert
        mock_provider.health_check.side_effect = Exception("Provider failed")
        health_checker.register_provider("failing_provider", mock_provider)
        
        await health_checker.perform_health_check()
        
        alert_callback.assert_called_once()
        call_args = alert_callback.call_args[0][0]
        assert isinstance(call_args, SystemHealth)
        assert call_args.overall_status == HealthStatus.CRITICAL
    
    def test_get_last_health_check(self, health_checker):
        """Test getting last health check result."""
        assert health_checker.get_last_health_check() is None
        
        # After setting a result
        mock_health = SystemHealth(HealthStatus.HEALTHY, [])
        health_checker._last_check = mock_health
        
        assert health_checker.get_last_health_check() == mock_health
    
    def test_get_health_history(self, health_checker):
        """Test getting health check history."""
        # Initially empty
        assert health_checker.get_health_history() == []
        
        # Add some history
        health1 = SystemHealth(HealthStatus.HEALTHY, [])
        health2 = SystemHealth(HealthStatus.WARNING, [])
        health_checker._check_history = [health1, health2]
        
        history = health_checker.get_health_history()
        assert len(history) == 2
        assert history[0] == health1
        assert history[1] == health2
        
        # Test with limit
        limited_history = health_checker.get_health_history(limit=1)
        assert len(limited_history) == 1
        assert limited_history[0] == health2
    
    def test_get_health_summary_no_data(self, health_checker):
        """Test health summary with no data."""
        summary = health_checker.get_health_summary()
        
        assert summary["status"] == "no_data"
        assert "No health checks performed" in summary["message"]
    
    def test_get_health_summary_with_data(self, health_checker):
        """Test health summary with data."""
        mock_health = SystemHealth(
            overall_status=HealthStatus.HEALTHY,
            components=[
                HealthCheckResult("comp1", HealthStatus.HEALTHY, "OK"),
                HealthCheckResult("comp2", HealthStatus.WARNING, "Warning")
            ]
        )
        health_checker._last_check = mock_health
        
        summary = health_checker.get_health_summary()
        
        assert summary["overall_status"] == "healthy"
        assert summary["healthy_components"] == 1
        assert summary["warning_components"] == 1
        assert summary["critical_components"] == 0
        assert summary["total_components"] == 2
        assert not summary["monitoring_active"]
    
    def test_start_stop_monitoring(self, health_checker):
        """Test starting and stopping monitoring."""
        assert not health_checker._running
        
        health_checker.stop_monitoring()
        assert not health_checker._running
        
        # Test that multiple stops don't cause issues
        health_checker.stop_monitoring()
        assert not health_checker._running
