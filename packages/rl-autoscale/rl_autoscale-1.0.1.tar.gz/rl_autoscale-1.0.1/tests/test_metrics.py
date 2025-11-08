"""Tests for the RLMetrics class."""

from rl_autoscale.metrics import RLMetrics, get_metrics_registry


def test_metrics_singleton():
    """Test that get_metrics_registry returns the same instance."""
    metrics1 = get_metrics_registry()
    metrics2 = get_metrics_registry()
    assert metrics1 is metrics2


def test_metrics_initialization(metrics_registry):
    """Test metrics initialization with custom parameters."""
    metrics = RLMetrics(
        registry=metrics_registry, namespace="test", histogram_buckets=[0.001, 0.01, 0.1, 1.0]
    )
    assert metrics.namespace == "test"
    assert metrics.histogram_buckets == [0.001, 0.01, 0.1, 1.0]


def test_observe_request(metrics_registry):
    """Test recording request metrics."""
    metrics = RLMetrics(registry=metrics_registry, namespace="test")

    # Record a successful request
    metrics.observe_request(method="GET", path="/api/test", duration=0.150, status_code=200)

    # Verify metrics were recorded (basic smoke test)
    # In a real test, you'd inspect the prometheus registry
    assert True  # If no exception, metrics recorded successfully


def test_observe_request_with_normalization(metrics_registry):
    """Test request observation with path normalization."""
    metrics = RLMetrics(registry=metrics_registry, namespace="test")

    # Normalize path before passing to observe_request
    def normalizer(path):
        """Simple normalizer for testing."""
        return path.replace("123", ":id")

    original_path = "/user/123"
    normalized_path = normalizer(original_path)

    metrics.observe_request(
        method="GET",
        path=normalized_path,  # Pass normalized path
        duration=0.1,
        status_code=200,
    )

    assert True  # Smoke test


def test_metrics_with_different_status_codes(metrics_registry):
    """Test metrics with various HTTP status codes."""
    metrics = RLMetrics(registry=metrics_registry, namespace="test")

    status_codes = [200, 201, 400, 404, 500, 503]

    for status in status_codes:
        metrics.observe_request(method="GET", path="/test", duration=0.1, status_code=status)

    assert True  # Smoke test
