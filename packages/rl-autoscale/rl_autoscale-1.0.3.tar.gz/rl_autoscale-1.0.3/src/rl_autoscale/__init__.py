"""
RL Autoscale - Production-Ready Metrics for RL-Based Autoscaling

A lightweight Python library for instrumenting applications with standardized
metrics for reinforcement learning-based autoscaling systems.

Usage:
    from rl_autoscale import enable_metrics

    app = Flask(__name__)
    enable_metrics(app, port=8000)
"""

from .metrics import RLMetrics, get_metrics_registry

__version__ = "1.0.3"
__all__ = [
    "RLMetrics",
    "enable_metrics",
    "enable_flask_metrics",
    "enable_fastapi_metrics",
    "get_metrics_registry",
]


def enable_flask_metrics(app, port: int = 8000, **kwargs):
    """
    Enable metrics for Flask applications.

    This function is lazily imported to avoid requiring Flask as a dependency
    when it's not needed.
    """
    from .flask_middleware import enable_metrics as _enable_flask_metrics

    return _enable_flask_metrics(app, port=port, **kwargs)


def enable_fastapi_metrics(app, port: int = 8000, **kwargs):
    """
    Enable metrics for FastAPI applications.

    This function is lazily imported to avoid requiring FastAPI as a dependency
    when it's not needed.
    """
    from .fastapi_middleware import enable_metrics as _enable_fastapi_metrics

    return _enable_fastapi_metrics(app, port=port, **kwargs)


def enable_metrics(app, port: int = 8000, **kwargs):
    """
    Auto-detect framework and enable metrics.

    Args:
        app: Flask, FastAPI, or other WSGI/ASGI application
        port: Port for Prometheus metrics endpoint (default: 8000)
        **kwargs: Additional configuration options

    Returns:
        Configured metrics instance
    """
    # Detect Flask
    if hasattr(app, "before_request") and hasattr(app, "after_request"):
        return enable_flask_metrics(app, port=port, **kwargs)

    # Detect FastAPI
    if hasattr(app, "add_middleware"):
        return enable_fastapi_metrics(app, port=port, **kwargs)

    raise ValueError(f"Unsupported framework: {type(app).__name__}. Supported: Flask, FastAPI")
