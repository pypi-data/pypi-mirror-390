"""
Core metrics definitions for RL autoscaling.

This module provides standardized Prometheus metrics that are expected by
RL-based autoscaling agents.
"""

import logging
from typing import Optional

from prometheus_client import Counter, Histogram, start_http_server
from prometheus_client.registry import REGISTRY, CollectorRegistry

logger = logging.getLogger(__name__)


class RLMetrics:
    """
    Standardized metrics for RL autoscaling systems.

    This class encapsulates all metrics required by RL autoscaling agents:
    - Request latency (histogram for percentile calculation)
    - Request count (for throughput analysis)

    The metrics follow Prometheus naming conventions and are designed to be
    scraped at regular intervals (typically 15-60 seconds).
    """

    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        namespace: str = "",
        histogram_buckets: Optional[list[float]] = None,
    ):
        """
        Initialize metrics collectors.

        Args:
            registry: Prometheus registry (default: global REGISTRY)
            namespace: Metric name prefix (e.g., "myapp" -> "myapp_http_...")
            histogram_buckets: Custom histogram buckets for latency
                              Default optimized for web APIs: 5ms to 10s
        """
        self.registry = registry or REGISTRY
        self.namespace = namespace

        # Default buckets cover 5ms to 10s (optimized for web APIs)
        if histogram_buckets is None:
            histogram_buckets = [
                0.005,  # 5ms
                0.01,  # 10ms
                0.025,  # 25ms
                0.05,  # 50ms
                0.1,  # 100ms
                0.25,  # 250ms
                0.5,  # 500ms
                1.0,  # 1s
                2.5,  # 2.5s
                5.0,  # 5s
                10.0,  # 10s
            ]

        self.histogram_buckets = histogram_buckets

        # Request latency histogram
        # Used by RL agent to calculate response time percentiles
        self.request_latency = Histogram(
            name=f"{namespace}_http_request_duration_seconds"
            if namespace
            else "http_request_duration_seconds",
            documentation="HTTP request latency in seconds",
            labelnames=["method", "path"],
            buckets=self.histogram_buckets,
            registry=self.registry,
        )

        # Request counter
        # Used by RL agent to understand traffic patterns
        self.request_count = Counter(
            name=f"{namespace}_http_requests_total" if namespace else "http_requests_total",
            documentation="Total HTTP requests",
            labelnames=["method", "path", "http_status"],
            registry=self.registry,
        )

        logger.info(
            f"Initialized RL metrics with namespace='{namespace}', "
            f"buckets={len(self.histogram_buckets)}"
        )

    def observe_request(
        self,
        method: str,
        path: str,
        duration: float,
        status_code: int,
    ) -> None:
        """
        Record a single HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (e.g., "/api/users")
            duration: Request duration in seconds
            status_code: HTTP status code (200, 404, etc.)
        """
        try:
            self.request_latency.labels(method=method, path=path).observe(duration)
            self.request_count.labels(method=method, path=path, http_status=str(status_code)).inc()
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}", exc_info=True)


# Global metrics registry instance
_metrics_instance: Optional[RLMetrics] = None


def get_metrics_registry(
    namespace: str = "",
    histogram_buckets: Optional[list[float]] = None,
) -> RLMetrics:
    """
    Get or create the global metrics instance.

    Args:
        namespace: Metric name prefix
        histogram_buckets: Custom histogram buckets

    Returns:
        Global RLMetrics instance
    """
    global _metrics_instance

    if _metrics_instance is None:
        _metrics_instance = RLMetrics(
            namespace=namespace,
            histogram_buckets=histogram_buckets,
        )

    return _metrics_instance


def start_metrics_server(port: int = 8000) -> None:
    """
    Start Prometheus metrics HTTP server.

    This starts a simple HTTP server that exposes metrics at /metrics endpoint.
    Prometheus scrapes this endpoint at regular intervals.

    Args:
        port: Port number for metrics server (default: 8000)

    Raises:
        OSError: If port is already in use
    """
    try:
        start_http_server(port)
        logger.info(f"✅ Metrics server started on port {port}")
        logger.info(f"📊 Metrics available at http://localhost:{port}/metrics")
    except OSError as e:
        if "Address already in use" in str(e):
            logger.warning(f"⚠️  Port {port} already in use, metrics server may already be running")
        else:
            logger.error(f"Failed to start metrics server on port {port}: {e}")
            raise
