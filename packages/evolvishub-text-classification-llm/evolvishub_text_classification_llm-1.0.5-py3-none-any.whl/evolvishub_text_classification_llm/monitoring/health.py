"""
Health checking system for the text classification library.

This module provides comprehensive health monitoring for providers, workflows,
and system resources with detailed diagnostics and alerting capabilities.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from ..core.interfaces import ILLMProvider
from ..core.exceptions import ProviderError, ResourceError
from ..providers.factory import ProviderFactory


logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Overall system health status."""
    overall_status: HealthStatus
    components: List[HealthCheckResult]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    healthy_components: int = 0
    warning_components: int = 0
    critical_components: int = 0
    
    def __post_init__(self):
        """Calculate component counts."""
        self.healthy_components = sum(1 for c in self.components if c.status == HealthStatus.HEALTHY)
        self.warning_components = sum(1 for c in self.components if c.status == HealthStatus.WARNING)
        self.critical_components = sum(1 for c in self.components if c.status == HealthStatus.CRITICAL)


class HealthChecker:
    """
    Comprehensive health checking system.
    
    Monitors provider health, system resources, and workflow components
    with configurable check intervals and alerting thresholds.
    """
    
    def __init__(
        self,
        check_interval_seconds: int = 60,
        timeout_seconds: int = 30,
        max_retries: int = 3,
        alert_callback: Optional[Callable] = None
    ):
        """
        Initialize health checker.
        
        Args:
            check_interval_seconds: Interval between health checks
            timeout_seconds: Timeout for individual health checks
            max_retries: Maximum retry attempts for failed checks
            alert_callback: Optional callback for health alerts
        """
        self.check_interval = check_interval_seconds
        self.timeout = timeout_seconds
        self.max_retries = max_retries
        self.alert_callback = alert_callback
        
        self._running = False
        self._last_check: Optional[SystemHealth] = None
        self._check_history: List[SystemHealth] = []
        self._max_history = 100
        
        # Component registry
        self._providers: Dict[str, ILLMProvider] = {}
        self._custom_checks: Dict[str, Callable] = {}
    
    def register_provider(self, name: str, provider: ILLMProvider):
        """Register a provider for health monitoring."""
        self._providers[name] = provider
        logger.info(f"Registered provider for health monitoring: {name}")
    
    def register_custom_check(self, name: str, check_func: Callable):
        """Register a custom health check function."""
        self._custom_checks[name] = check_func
        logger.info(f"Registered custom health check: {name}")
    
    async def check_provider_health(self, name: str, provider: ILLMProvider) -> HealthCheckResult:
        """Check health of a specific provider."""
        start_time = time.time()
        
        try:
            # Use provider's built-in health check if available
            health_data = await asyncio.wait_for(
                provider.health_check(),
                timeout=self.timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status based on response
            if health_data.get("status") == "healthy":
                status = HealthStatus.HEALTHY
                message = f"Provider {name} is healthy"
            elif health_data.get("status") == "degraded":
                status = HealthStatus.WARNING
                message = f"Provider {name} is degraded"
            else:
                status = HealthStatus.CRITICAL
                message = f"Provider {name} reported issues"
            
            return HealthCheckResult(
                component=f"provider_{name}",
                status=status,
                message=message,
                response_time_ms=response_time,
                details=health_data
            )
            
        except asyncio.TimeoutError:
            return HealthCheckResult(
                component=f"provider_{name}",
                status=HealthStatus.CRITICAL,
                message=f"Provider {name} health check timed out",
                response_time_ms=(time.time() - start_time) * 1000,
                error="timeout"
            )
        except Exception as e:
            return HealthCheckResult(
                component=f"provider_{name}",
                status=HealthStatus.CRITICAL,
                message=f"Provider {name} health check failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def check_system_resources(self) -> HealthCheckResult:
        """Check system resource health."""
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            details = {
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "cpu_percent": cpu_percent,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            }
            
            # Determine status based on thresholds
            if memory.percent > 90 or cpu_percent > 90 or disk.percent > 90:
                status = HealthStatus.CRITICAL
                message = "System resources critically low"
            elif memory.percent > 80 or cpu_percent > 80 or disk.percent > 80:
                status = HealthStatus.WARNING
                message = "System resources running high"
            else:
                status = HealthStatus.HEALTHY
                message = "System resources healthy"
            
            return HealthCheckResult(
                component="system_resources",
                status=status,
                message=message,
                details=details
            )
            
        except ImportError:
            return HealthCheckResult(
                component="system_resources",
                status=HealthStatus.UNKNOWN,
                message="psutil not available for system monitoring",
                error="missing_dependency"
            )
        except Exception as e:
            return HealthCheckResult(
                component="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"System resource check failed: {str(e)}",
                error=str(e)
            )
    
    async def run_custom_check(self, name: str, check_func: Callable) -> HealthCheckResult:
        """Run a custom health check function."""
        start_time = time.time()
        
        try:
            result = await asyncio.wait_for(
                check_func() if asyncio.iscoroutinefunction(check_func) else check_func(),
                timeout=self.timeout
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, HealthCheckResult):
                result.response_time_ms = response_time
                return result
            elif isinstance(result, dict):
                return HealthCheckResult(
                    component=f"custom_{name}",
                    status=HealthStatus(result.get("status", "unknown")),
                    message=result.get("message", f"Custom check {name} completed"),
                    response_time_ms=response_time,
                    details=result.get("details", {})
                )
            else:
                return HealthCheckResult(
                    component=f"custom_{name}",
                    status=HealthStatus.HEALTHY,
                    message=f"Custom check {name} passed",
                    response_time_ms=response_time
                )
                
        except Exception as e:
            return HealthCheckResult(
                component=f"custom_{name}",
                status=HealthStatus.CRITICAL,
                message=f"Custom check {name} failed: {str(e)}",
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def perform_health_check(self) -> SystemHealth:
        """Perform comprehensive health check of all components."""
        logger.info("Starting comprehensive health check")
        start_time = time.time()
        
        results = []
        
        # Check all registered providers
        for name, provider in self._providers.items():
            result = await self.check_provider_health(name, provider)
            results.append(result)
        
        # Check system resources
        system_result = await self.check_system_resources()
        results.append(system_result)
        
        # Run custom checks
        for name, check_func in self._custom_checks.items():
            result = await self.run_custom_check(name, check_func)
            results.append(result)
        
        # Determine overall status
        critical_count = sum(1 for r in results if r.status == HealthStatus.CRITICAL)
        warning_count = sum(1 for r in results if r.status == HealthStatus.WARNING)
        
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
        else:
            overall_status = HealthStatus.HEALTHY
        
        health = SystemHealth(
            overall_status=overall_status,
            components=results
        )
        
        # Store in history
        self._last_check = health
        self._check_history.append(health)
        if len(self._check_history) > self._max_history:
            self._check_history.pop(0)
        
        # Trigger alerts if needed
        if self.alert_callback and overall_status in [HealthStatus.CRITICAL, HealthStatus.WARNING]:
            try:
                await self.alert_callback(health)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
        
        duration = time.time() - start_time
        logger.info(f"Health check completed in {duration:.2f}s - Status: {overall_status.value}")
        
        return health
    
    async def start_monitoring(self):
        """Start continuous health monitoring."""
        if self._running:
            logger.warning("Health monitoring already running")
            return
        
        self._running = True
        logger.info(f"Starting health monitoring (interval: {self.check_interval}s)")
        
        while self._running:
            try:
                await self.perform_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(min(self.check_interval, 60))  # Fallback interval
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        self._running = False
        logger.info("Stopped health monitoring")
    
    def get_last_health_check(self) -> Optional[SystemHealth]:
        """Get the most recent health check result."""
        return self._last_check
    
    def get_health_history(self, limit: Optional[int] = None) -> List[SystemHealth]:
        """Get health check history."""
        if limit:
            return self._check_history[-limit:]
        return self._check_history.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of system health."""
        if not self._last_check:
            return {"status": "no_data", "message": "No health checks performed yet"}
        
        return {
            "overall_status": self._last_check.overall_status.value,
            "last_check": self._last_check.timestamp.isoformat(),
            "healthy_components": self._last_check.healthy_components,
            "warning_components": self._last_check.warning_components,
            "critical_components": self._last_check.critical_components,
            "total_components": len(self._last_check.components),
            "monitoring_active": self._running
        }
