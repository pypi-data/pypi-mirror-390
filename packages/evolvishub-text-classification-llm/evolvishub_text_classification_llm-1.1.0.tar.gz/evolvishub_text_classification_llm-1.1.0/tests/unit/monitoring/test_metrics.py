"""
Unit tests for MetricsCollector.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from evolvishub_text_classification_llm.monitoring.metrics import (
    MetricsCollector, MetricType, MetricPoint, MetricSummary, TimerContext
)


@pytest.fixture
def metrics_collector():
    """Create a MetricsCollector instance."""
    return MetricsCollector(
        max_points_per_metric=100,
        retention_hours=1,
        aggregation_interval_seconds=5
    )


class TestMetricPoint:
    """Test cases for MetricPoint."""
    
    def test_metric_point_creation(self):
        """Test creating a metric point."""
        point = MetricPoint(
            name="test_metric",
            value=42.5,
            tags={"environment": "test"},
            metric_type=MetricType.GAUGE
        )
        
        assert point.name == "test_metric"
        assert point.value == 42.5
        assert point.tags["environment"] == "test"
        assert point.metric_type == MetricType.GAUGE


class TestMetricSummary:
    """Test cases for MetricSummary."""
    
    def test_metric_summary_creation(self):
        """Test creating a metric summary."""
        summary = MetricSummary(
            name="test_metric",
            count=100,
            sum=1000.0,
            min=5.0,
            max=50.0,
            avg=10.0,
            p50=10.0,
            p95=45.0,
            p99=48.0,
            last_value=15.0,
            last_updated=MetricPoint("test", 0).timestamp
        )
        
        assert summary.name == "test_metric"
        assert summary.count == 100
        assert summary.avg == 10.0
        assert summary.p95 == 45.0


class TestMetricsCollector:
    """Test cases for MetricsCollector."""
    
    def test_initialization(self, metrics_collector):
        """Test metrics collector initialization."""
        assert metrics_collector.max_points == 100
        assert metrics_collector.retention_hours == 1
        assert metrics_collector.aggregation_interval == 5
        assert not metrics_collector._running
    
    def test_record_counter(self, metrics_collector):
        """Test recording counter metrics."""
        metrics_collector.record_counter("requests", 1.0)
        metrics_collector.record_counter("requests", 2.0)
        
        assert metrics_collector.get_counter("requests") == 3.0
        
        points = metrics_collector.get_metric_points("requests")
        assert len(points) == 2
        assert points[0].metric_type == MetricType.COUNTER
    
    def test_record_gauge(self, metrics_collector):
        """Test recording gauge metrics."""
        metrics_collector.record_gauge("cpu_usage", 75.5)
        metrics_collector.record_gauge("cpu_usage", 80.0)
        
        assert metrics_collector.get_gauge("cpu_usage") == 80.0
        
        points = metrics_collector.get_metric_points("cpu_usage")
        assert len(points) == 2
        assert points[-1].value == 80.0
        assert points[-1].metric_type == MetricType.GAUGE
    
    def test_record_histogram(self, metrics_collector):
        """Test recording histogram metrics."""
        values = [10, 20, 30, 40, 50]
        for value in values:
            metrics_collector.record_histogram("response_time", value)
        
        points = metrics_collector.get_metric_points("response_time")
        assert len(points) == 5
        assert all(p.metric_type == MetricType.HISTOGRAM for p in points)
    
    def test_record_timer(self, metrics_collector):
        """Test recording timer metrics."""
        metrics_collector.record_timer("api_call_duration", 150.5)
        metrics_collector.record_timer("api_call_duration", 200.0)
        
        points = metrics_collector.get_metric_points("api_call_duration")
        assert len(points) == 2
        assert points[0].value == 150.5
        assert points[1].value == 200.0
        assert all(p.metric_type == MetricType.TIMER for p in points)
    
    def test_increment_decrement(self, metrics_collector):
        """Test increment and decrement convenience methods."""
        metrics_collector.increment("page_views")
        metrics_collector.increment("page_views")
        metrics_collector.decrement("page_views")
        
        assert metrics_collector.get_counter("page_views") == 1.0
    
    def test_set_gauge_observe(self, metrics_collector):
        """Test set_gauge and observe convenience methods."""
        metrics_collector.set_gauge("memory_usage", 85.5)
        assert metrics_collector.get_gauge("memory_usage") == 85.5
        
        metrics_collector.observe("latency", 100.0)
        metrics_collector.observe("latency", 150.0)
        
        points = metrics_collector.get_metric_points("latency")
        assert len(points) == 2
    
    def test_timer_context_manager(self, metrics_collector):
        """Test timer context manager."""
        with patch('time.time', side_effect=[0.0, 0.15]):  # 150ms duration
            with metrics_collector.timer("operation_time"):
                pass  # Simulate some operation
        
        points = metrics_collector.get_metric_points("operation_time")
        assert len(points) == 1
        assert points[0].value == 150.0  # 150ms
        assert points[0].metric_type == MetricType.TIMER
    
    def test_timer_context_with_tags(self, metrics_collector):
        """Test timer context manager with tags."""
        tags = {"operation": "database_query", "table": "users"}
        
        with patch('time.time', side_effect=[0.0, 0.1]):
            with metrics_collector.timer("db_query_time", tags):
                pass
        
        points = metrics_collector.get_metric_points("db_query_time")
        assert len(points) == 1
        assert points[0].tags == tags
    
    def test_get_metric_points_with_limit(self, metrics_collector):
        """Test getting metric points with limit."""
        for i in range(10):
            metrics_collector.record_counter("test_metric", 1.0)
        
        all_points = metrics_collector.get_metric_points("test_metric")
        limited_points = metrics_collector.get_metric_points("test_metric", limit=5)
        
        assert len(all_points) == 10
        assert len(limited_points) == 5
        assert limited_points == all_points[-5:]  # Should get last 5 points
    
    def test_calculate_percentiles(self, metrics_collector):
        """Test percentile calculation."""
        values = list(range(1, 101))  # 1 to 100
        percentiles = metrics_collector._calculate_percentiles(values)
        
        assert percentiles["p50"] == 50.5  # Median
        assert percentiles["p95"] == 95.05  # 95th percentile
        assert percentiles["p99"] == 99.01  # 99th percentile
    
    def test_calculate_percentiles_empty(self, metrics_collector):
        """Test percentile calculation with empty values."""
        percentiles = metrics_collector._calculate_percentiles([])
        
        assert percentiles["p50"] == 0.0
        assert percentiles["p95"] == 0.0
        assert percentiles["p99"] == 0.0
    
    @pytest.mark.asyncio
    async def test_aggregate_metrics(self, metrics_collector):
        """Test metric aggregation."""
        # Add some test data
        values = [10, 20, 30, 40, 50]
        for value in values:
            metrics_collector.record_histogram("test_metric", value)
        
        await metrics_collector._aggregate_metrics()
        
        summary = metrics_collector.get_metric_summary("test_metric")
        assert summary is not None
        assert summary.count == 5
        assert summary.sum == 150.0
        assert summary.min == 10.0
        assert summary.max == 50.0
        assert summary.avg == 30.0
        assert summary.p50 == 30.0
    
    def test_get_all_metrics(self, metrics_collector):
        """Test getting all metrics."""
        metrics_collector.record_counter("requests", 10.0)
        metrics_collector.record_gauge("cpu_usage", 75.0)
        metrics_collector.record_histogram("response_time", 100.0)
        metrics_collector.record_timer("api_duration", 200.0)
        
        all_metrics = metrics_collector.get_all_metrics()
        
        assert "counters" in all_metrics
        assert "gauges" in all_metrics
        assert "histograms" in all_metrics
        assert "timers" in all_metrics
        assert "summaries" in all_metrics
        
        assert all_metrics["counters"]["requests"] == 10.0
        assert all_metrics["gauges"]["cpu_usage"] == 75.0
        assert all_metrics["histograms"]["response_time"] == 1
        assert all_metrics["timers"]["api_duration"] == 1
    
    def test_summary_to_dict(self, metrics_collector):
        """Test converting summary to dictionary."""
        summary = MetricSummary(
            name="test",
            count=10,
            sum=100.0,
            min=5.0,
            max=25.0,
            avg=10.0,
            p50=10.0,
            p95=20.0,
            p99=24.0,
            last_value=15.0,
            last_updated=MetricPoint("test", 0).timestamp
        )
        
        summary_dict = metrics_collector._summary_to_dict(summary)
        
        assert summary_dict["count"] == 10
        assert summary_dict["sum"] == 100.0
        assert summary_dict["avg"] == 10.0
        assert summary_dict["p95"] == 20.0
        assert "last_updated" in summary_dict
    
    @pytest.mark.asyncio
    async def test_cleanup_old_metrics(self, metrics_collector):
        """Test cleaning up old metrics."""
        # Add some metrics
        for i in range(5):
            metrics_collector.record_counter("old_metric", 1.0)
        
        # Mock old timestamps
        for point in metrics_collector._metrics["old_metric"]:
            point.timestamp = point.timestamp.replace(year=2020)  # Very old
        
        await metrics_collector._cleanup_old_metrics()
        
        # Should have removed old points
        points = metrics_collector.get_metric_points("old_metric")
        assert len(points) == 0
    
    def test_reset_metrics(self, metrics_collector):
        """Test resetting all metrics."""
        metrics_collector.record_counter("test1", 10.0)
        metrics_collector.record_gauge("test2", 20.0)
        metrics_collector.record_histogram("test3", 30.0)
        
        assert len(metrics_collector._metrics) > 0
        assert len(metrics_collector._counters) > 0
        assert len(metrics_collector._gauges) > 0
        
        metrics_collector.reset_metrics()
        
        assert len(metrics_collector._metrics) == 0
        assert len(metrics_collector._counters) == 0
        assert len(metrics_collector._gauges) == 0
        assert len(metrics_collector._histograms) == 0
        assert len(metrics_collector._timers) == 0
        assert len(metrics_collector._summaries) == 0
    
    def test_export_metrics_json(self, metrics_collector):
        """Test exporting metrics in JSON format."""
        metrics_collector.record_counter("requests", 100.0)
        metrics_collector.record_gauge("cpu_usage", 75.0)
        
        json_export = metrics_collector.export_metrics("json")
        
        data = json.loads(json_export)
        assert "counters" in data
        assert "gauges" in data
        assert data["counters"]["requests"] == 100.0
        assert data["gauges"]["cpu_usage"] == 75.0
    
    def test_export_metrics_prometheus(self, metrics_collector):
        """Test exporting metrics in Prometheus format."""
        metrics_collector.record_counter("http_requests_total", 100.0)
        metrics_collector.record_gauge("cpu_usage_percent", 75.0)
        
        # Add a summary for testing
        metrics_collector._summaries["response_time"] = MetricSummary(
            name="response_time",
            count=10,
            sum=1000.0,
            min=50.0,
            max=200.0,
            avg=100.0,
            p50=95.0,
            p95=180.0,
            p99=195.0,
            last_value=120.0,
            last_updated=MetricPoint("test", 0).timestamp
        )
        
        prometheus_export = metrics_collector.export_metrics("prometheus")
        
        assert "# TYPE http_requests_total counter" in prometheus_export
        assert "http_requests_total 100.0" in prometheus_export
        assert "# TYPE cpu_usage_percent gauge" in prometheus_export
        assert "cpu_usage_percent 75.0" in prometheus_export
        assert "# TYPE response_time summary" in prometheus_export
        assert "response_time_count 10" in prometheus_export
        assert "response_time{quantile=\"0.95\"} 180.0" in prometheus_export
    
    def test_export_metrics_unsupported_format(self, metrics_collector):
        """Test exporting metrics with unsupported format."""
        with pytest.raises(ValueError) as exc_info:
            metrics_collector.export_metrics("xml")
        
        assert "Unsupported export format: xml" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_export_callback(self, metrics_collector):
        """Test metrics export callback."""
        export_callback = AsyncMock()
        metrics_collector.export_callback = export_callback
        
        metrics_collector.record_counter("test", 1.0)
        await metrics_collector._aggregate_metrics()
        
        export_callback.assert_called_once()
        call_args = export_callback.call_args[0][0]
        assert isinstance(call_args, dict)
        assert "counters" in call_args
    
    @pytest.mark.asyncio
    async def test_start_stop_collection(self, metrics_collector):
        """Test starting and stopping metric collection."""
        assert not metrics_collector._running
        
        # Start collection
        await metrics_collector.start_collection()
        assert metrics_collector._running
        assert metrics_collector._aggregation_task is not None
        assert metrics_collector._cleanup_task is not None
        
        # Stop collection
        await metrics_collector.stop_collection()
        assert not metrics_collector._running
        assert metrics_collector._aggregation_task.cancelled()
        assert metrics_collector._cleanup_task.cancelled()


class TestTimerContext:
    """Test cases for TimerContext."""
    
    def test_timer_context_initialization(self):
        """Test timer context initialization."""
        collector = Mock()
        context = TimerContext(collector, "test_timer", {"tag": "value"})
        
        assert context.collector == collector
        assert context.name == "test_timer"
        assert context.tags == {"tag": "value"}
        assert context.start_time is None
    
    def test_timer_context_usage(self):
        """Test timer context manager usage."""
        collector = Mock()
        
        with patch('time.time', side_effect=[1.0, 1.5]):  # 500ms duration
            with TimerContext(collector, "test_timer") as context:
                assert context.start_time == 1.0
        
        collector.record_timer.assert_called_once_with("test_timer", 500.0, None)
