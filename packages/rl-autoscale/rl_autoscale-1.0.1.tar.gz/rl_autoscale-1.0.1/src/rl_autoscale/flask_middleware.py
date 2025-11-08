"""
Flask middleware for RL autoscaling metrics.

Provides automatic instrumentation for Flask applications with minimal configuration.
"""

import logging
import time
from typing import Optional

from flask import Flask, request

from .metrics import RLMetrics, get_metrics_registry, start_metrics_server

logger = logging.getLogger(__name__)


def enable_metrics(
    app: Flask,
    port: int = 8000,
    namespace: str = "",
    histogram_buckets: Optional[list[float]] = None,
    path_normalizer: Optional[callable] = None,
    exclude_paths: Optional[list[str]] = None,
) -> RLMetrics:
    r"""
    Enable RL autoscaling metrics for a Flask application.

    This function instruments your Flask app with:
    - Automatic request timing
    - Response time histogram (for percentile calculation)
    - Request counter (for throughput analysis)
    - Prometheus metrics endpoint

    Usage:
        from flask import Flask
        from rl_autoscaling_observability import enable_metrics

        app = Flask(__name__)
        enable_metrics(app, port=8000)

        @app.route("/api/hello")
        def hello():
            return "Hello World"

    Args:
        app: Flask application instance
        port: Port for Prometheus metrics server (default: 8000)
        namespace: Metric name prefix (e.g., "myapp")
        histogram_buckets: Custom latency buckets (default: 5ms to 10s)
        path_normalizer: Function to normalize paths (e.g., /user/123 -> /user/:id)
        exclude_paths: Paths to exclude from metrics (e.g., ["/health", "/metrics"])

    Returns:
        RLMetrics instance for manual instrumentation if needed

    Example with path normalization:
        def normalize_path(path):
            # Convert /user/123 to /user/:id
            import re
            return re.sub(r'/\d+', '/:id', path)

        enable_metrics(app, path_normalizer=normalize_path)
    """
    # Get or create metrics instance
    metrics = get_metrics_registry(
        namespace=namespace,
        histogram_buckets=histogram_buckets,
    )

    # Default excluded paths
    if exclude_paths is None:
        exclude_paths = ["/health", "/healthz", "/metrics", "/readiness", "/liveness"]

    # Start metrics server
    try:
        start_metrics_server(port)
    except OSError:
        logger.warning(f"Metrics server on port {port} may already be running")

    @app.before_request
    def before_request_handler():
        """Record request start time."""
        request._rl_metrics_start_time = time.time()

    @app.after_request
    def after_request_handler(response):
        """Record request completion and emit metrics."""
        # Skip if no start time recorded
        if not hasattr(request, "_rl_metrics_start_time"):
            return response

        # Calculate duration
        duration = time.time() - request._rl_metrics_start_time

        # Get request details
        method = request.method
        path = request.path
        status_code = response.status_code

        # Apply path normalization if provided
        if path_normalizer:
            try:
                path = path_normalizer(path)
            except Exception as e:
                logger.warning(f"Path normalizer failed for {path}: {e}")

        # Skip excluded paths
        if path in exclude_paths:
            return response

        # Record metrics
        try:
            metrics.observe_request(
                method=method,
                path=path,
                duration=duration,
                status_code=status_code,
            )
        except Exception as e:
            logger.error(f"Failed to record metrics for {method} {path}: {e}")

        return response

    logger.info(
        f"✅ RL metrics enabled for Flask app "
        f"(port={port}, namespace='{namespace}', excluded={len(exclude_paths)} paths)"
    )

    return metrics


def normalize_api_paths(path: str) -> str:
    """
    Default path normalizer for API endpoints.

    Converts:
    - /api/users/123 -> /api/users/:id
    - /api/posts/456/comments -> /api/posts/:id/comments
    - /files/abc-def-123.pdf -> /files/:filename

    Args:
        path: Original request path

    Returns:
        Normalized path
    """
    import re

    # Replace numeric IDs
    path = re.sub(r"/\d+", "/:id", path)

    # Replace UUIDs
    path = re.sub(
        r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "/:uuid",
        path,
        flags=re.IGNORECASE,
    )

    # Replace filenames with extensions
    path = re.sub(r"/[^/]+\.[a-zA-Z0-9]+$", "/:filename", path)

    return path
