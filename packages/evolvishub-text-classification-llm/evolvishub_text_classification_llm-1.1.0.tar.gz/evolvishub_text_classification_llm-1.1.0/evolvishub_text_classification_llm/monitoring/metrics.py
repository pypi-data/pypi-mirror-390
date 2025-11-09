"""
Metrics collection and analytics system for the text classification library.

This module provides comprehensive metrics collection, aggregation, and reporting
capabilities for monitoring performance, usage, and system behavior.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json

from ..core.exceptions import ResourceError


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricPoint:
    """A single metric data point."""
    name: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p50: float
    p95: float
    p99: float
    last_value: float
    last_updated: datetime


class MetricsCollector:
    """
    Comprehensive metrics collection and analytics system.
    
    Collects, aggregates, and reports metrics for performance monitoring,
    usage analytics, and system observability.
    """
    
    def __init__(
        self,
        max_points_per_metric: int = 10000,
        retention_hours: int = 24,
        aggregation_interval_seconds: int = 60,
        export_callback: Optional[Callable] = None
    ):
        """
        Initialize metrics collector.
        
        Args:
            max_points_per_metric: Maximum data points to retain per metric
            retention_hours: How long to retain metric data
            aggregation_interval_seconds: Interval for metric aggregation
            export_callback: Optional callback for exporting metrics
        """
        self.max_points = max_points_per_metric
        self.retention_hours = retention_hours
        self.aggregation_interval = aggregation_interval_seconds
        self.export_callback = export_callback
        
        # Metric storage
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.max_points))
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        
        # Aggregated data
        self._summaries: Dict[str, MetricSummary] = {}
        self._last_aggregation = datetime.utcnow()
        
        # Background tasks
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._aggregation_task: Optional[asyncio.Task] = None
    
    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Record a counter metric (cumulative value)."""
        self._counters[name] += value
        self._record_point(name, value, MetricType.COUNTER, tags)
    
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric (current value)."""
        self._gauges[name] = value
        self._record_point(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a histogram metric (distribution of values)."""
        self._histograms[name].append(value)
        self._record_point(name, value, MetricType.HISTOGRAM, tags)
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timer metric (duration measurement)."""
        self._timers[name].append(duration_ms)
        self._record_point(name, duration_ms, MetricType.TIMER, tags)
    
    def _record_point(self, name: str, value: float, metric_type: MetricType, tags: Optional[Dict[str, str]]):
        """Record a metric data point."""
        point = MetricPoint(
            name=name,
            value=value,
            metric_type=metric_type,
            tags=tags or {}
        )
        self._metrics[name].append(point)
    
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        return TimerContext(self, name, tags)
    
    def increment(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Increment a counter by 1."""
        self.record_counter(name, 1.0, tags)
    
    def decrement(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Decrement a counter by 1."""
        self.record_counter(name, -1.0, tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge value."""
        self.record_gauge(name, value, tags)
    
    def observe(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Observe a value (adds to histogram)."""
        self.record_histogram(name, value, tags)
    
    def get_counter(self, name: str) -> float:
        """Get current counter value."""
        return self._counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> float:
        """Get current gauge value."""
        return self._gauges.get(name, 0.0)
    
    def get_metric_points(self, name: str, limit: Optional[int] = None) -> List[MetricPoint]:
        """Get metric data points."""
        points = list(self._metrics.get(name, []))
        if limit:
            return points[-limit:]
        return points
    
    def get_metric_summary(self, name: str) -> Optional[MetricSummary]:
        """Get aggregated metric summary."""
        return self._summaries.get(name)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metric values."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: len(v) for k, v in self._histograms.items()},
            "timers": {k: len(v) for k, v in self._timers.items()},
            "summaries": {k: self._summary_to_dict(v) for k, v in self._summaries.items()}
        }
    
    def _summary_to_dict(self, summary: MetricSummary) -> Dict[str, Any]:
        """Convert metric summary to dictionary."""
        return {
            "count": summary.count,
            "sum": summary.sum,
            "min": summary.min,
            "max": summary.max,
            "avg": summary.avg,
            "p50": summary.p50,
            "p95": summary.p95,
            "p99": summary.p99,
            "last_value": summary.last_value,
            "last_updated": summary.last_updated.isoformat()
        }
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentiles for a list of values."""
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def percentile(p):
            k = (n - 1) * p / 100
            f = int(k)
            c = k - f
            if f + 1 < n:
                return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c
            else:
                return sorted_values[f]
        
        return {
            "p50": percentile(50),
            "p95": percentile(95),
            "p99": percentile(99)
        }
    
    async def _aggregate_metrics(self):
        """Aggregate metrics into summaries."""
        logger.debug("Aggregating metrics")
        
        for name, points in self._metrics.items():
            if not points:
                continue
            
            values = [p.value for p in points]
            percentiles = self._calculate_percentiles(values)
            
            summary = MetricSummary(
                name=name,
                count=len(values),
                sum=sum(values),
                min=min(values),
                max=max(values),
                avg=sum(values) / len(values),
                p50=percentiles["p50"],
                p95=percentiles["p95"],
                p99=percentiles["p99"],
                last_value=values[-1],
                last_updated=points[-1].timestamp
            )
            
            self._summaries[name] = summary
        
        self._last_aggregation = datetime.utcnow()
        
        # Export metrics if callback is configured
        if self.export_callback:
            try:
                await self.export_callback(self.get_all_metrics())
            except Exception as e:
                logger.error(f"Metrics export failed: {e}")
    
    async def _cleanup_old_metrics(self):
        """Remove old metric data points."""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
        
        for name, points in self._metrics.items():
            # Remove old points
            while points and points[0].timestamp < cutoff_time:
                points.popleft()
        
        # Clean up histogram and timer data
        for name, values in list(self._histograms.items()):
            if len(values) > self.max_points:
                self._histograms[name] = values[-self.max_points:]
        
        for name, values in list(self._timers.items()):
            if len(values) > self.max_points:
                self._timers[name] = values[-self.max_points:]
    
    async def start_collection(self):
        """Start background metric collection and aggregation."""
        if self._running:
            logger.warning("Metrics collection already running")
            return
        
        self._running = True
        logger.info("Starting metrics collection")
        
        # Start aggregation task
        self._aggregation_task = asyncio.create_task(self._aggregation_loop())
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _aggregation_loop(self):
        """Background loop for metric aggregation."""
        while self._running:
            try:
                await self._aggregate_metrics()
                await asyncio.sleep(self.aggregation_interval)
            except Exception as e:
                logger.error(f"Metrics aggregation error: {e}")
                await asyncio.sleep(60)  # Fallback interval
    
    async def _cleanup_loop(self):
        """Background loop for metric cleanup."""
        while self._running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(3600)  # Cleanup every hour
            except Exception as e:
                logger.error(f"Metrics cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def stop_collection(self):
        """Stop background metric collection."""
        self._running = False
        
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped metrics collection")
    
    def reset_metrics(self):
        """Reset all metrics data."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._timers.clear()
        self._summaries.clear()
        logger.info("Reset all metrics")
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        data = self.get_all_metrics()
        
        if format.lower() == "json":
            return json.dumps(data, indent=2, default=str)
        elif format.lower() == "prometheus":
            return self._export_prometheus_format(data)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus_format(self, data: Dict[str, Any]) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        # Export counters
        for name, value in data["counters"].items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")
        
        # Export gauges
        for name, value in data["gauges"].items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")
        
        # Export histogram summaries
        for name, summary in data["summaries"].items():
            lines.append(f"# TYPE {name} summary")
            lines.append(f"{name}_count {summary['count']}")
            lines.append(f"{name}_sum {summary['sum']}")
            lines.append(f"{name}{{quantile=\"0.5\"}} {summary['p50']}")
            lines.append(f"{name}{{quantile=\"0.95\"}} {summary['p95']}")
            lines.append(f"{name}{{quantile=\"0.99\"}} {summary['p99']}")
        
        return "\n".join(lines)


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.name, duration_ms, self.tags)
