"""Tests for framework auto-detection."""

import pytest

from rl_autoscale import enable_metrics


def test_unsupported_framework():
    """Test that unsupported frameworks raise an error."""

    class UnsupportedApp:
        """Fake app that doesn't match Flask or FastAPI."""

        pass

    app = UnsupportedApp()

    with pytest.raises(ValueError, match="Unsupported framework"):
        enable_metrics(app, port=8007)


def test_flask_detection():
    """Test Flask app detection."""
    pytest.importorskip("flask")
    from flask import Flask

    app = Flask(__name__)
    metrics = enable_metrics(app, port=8008)
    assert metrics is not None


def test_fastapi_detection():
    """Test FastAPI app detection."""
    pytest.importorskip("fastapi")
    from fastapi import FastAPI

    app = FastAPI()
    metrics = enable_metrics(app, port=8009)
    assert metrics is not None
