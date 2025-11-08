"""Tests for FastAPI middleware."""

import pytest

pytest.importorskip("fastapi")

from fastapi import FastAPI

from rl_autoscale import enable_metrics


def test_fastapi_middleware_integration(fastapi_app):
    """Test FastAPI middleware integration."""
    metrics = enable_metrics(fastapi_app, port=8004)
    assert metrics is not None


def test_fastapi_auto_detection():
    """Test that FastAPI apps are automatically detected."""
    from rl_autoscale import enable_metrics

    app = FastAPI()

    @app.get("/")
    async def index():
        return {"status": "OK"}

    # Should not raise an error
    metrics = enable_metrics(app, port=8005)
    assert metrics is not None


def test_fastapi_with_custom_config():
    """Test FastAPI integration with custom configuration."""
    app = FastAPI()

    metrics = enable_metrics(
        app, port=8006, namespace="custom", exclude_paths=["/health", "/metrics"]
    )

    assert metrics is not None
