"""Tests for Flask middleware."""

import pytest

pytest.importorskip("flask")

from flask import Flask

from rl_autoscale import enable_metrics


def test_flask_middleware_integration(flask_app):
    """Test Flask middleware integration."""
    metrics = enable_metrics(flask_app, port=8001)
    assert metrics is not None


def test_flask_auto_detection():
    """Test that Flask apps are automatically detected."""
    from rl_autoscale import enable_metrics

    app = Flask(__name__)

    @app.route("/")
    def index():
        return "OK"

    # Should not raise an error
    metrics = enable_metrics(app, port=8002)
    assert metrics is not None


def test_flask_with_custom_config():
    """Test Flask integration with custom configuration."""
    app = Flask(__name__)

    metrics = enable_metrics(app, port=8003, namespace="custom", exclude_paths=["/health"])

    assert metrics is not None
