"""
FastAPI middleware for RL autoscaling metrics.

Provides automatic instrumentation for FastAPI applications.
"""

import logging
import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .metrics import RLMetrics, get_metrics_registry, start_metrics_server

logger = logging.getLogger(__name__)


class RLMetricsMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for RL autoscaling metrics.

    Automatically records request latency and count for all endpoints.
    """

    def __init__(
        self,
        app: FastAPI,
        metrics: RLMetrics,
        path_normalizer: Optional[Callable[[str], str]] = None,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.metrics = metrics
        self.path_normalizer = path_normalizer
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request and record metrics."""
        # Skip excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Process request
        response: Response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Get path (apply normalizer if provided)
        path = request.url.path
        if self.path_normalizer:
            try:
                path = self.path_normalizer(path)
            except Exception as e:
                logger.warning(f"Path normalizer failed for {path}: {e}")

        # Record metrics
        try:
            self.metrics.observe_request(
                method=request.method,
                path=path,
                duration=duration,
                status_code=response.status_code,
            )
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")

        return response


def enable_metrics(
    app: FastAPI,
    port: int = 8000,
    namespace: str = "",
    histogram_buckets: Optional[list[float]] = None,
    path_normalizer: Optional[Callable[[str], str]] = None,
    exclude_paths: Optional[list[str]] = None,
) -> RLMetrics:
    """
    Enable RL autoscaling metrics for a FastAPI application.

    Usage:
        from fastapi import FastAPI
        from rl_autoscaling_observability import enable_metrics

        app = FastAPI()
        enable_metrics(app, port=8000)

        @app.get("/api/hello")
        async def hello():
            return {"message": "Hello World"}

    Args:
        app: FastAPI application instance
        port: Port for Prometheus metrics server
        namespace: Metric name prefix
        histogram_buckets: Custom latency buckets
        path_normalizer: Function to normalize paths
        exclude_paths: Paths to exclude from metrics

    Returns:
        RLMetrics instance
    """
    # Get or create metrics instance
    metrics = get_metrics_registry(
        namespace=namespace,
        histogram_buckets=histogram_buckets,
    )

    # Start metrics server
    try:
        start_metrics_server(port)
    except OSError:
        logger.warning(f"Metrics server on port {port} may already be running")

    # Add middleware
    app.add_middleware(
        RLMetricsMiddleware,
        metrics=metrics,
        path_normalizer=path_normalizer,
        exclude_paths=exclude_paths,
    )

    logger.info(f"✅ RL metrics enabled for FastAPI app (port={port}, namespace='{namespace}')")

    return metrics
