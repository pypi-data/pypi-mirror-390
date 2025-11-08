# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-01-08

### Fixed
- **BREAKING FIX**: Implemented lazy imports for Flask and FastAPI middleware to prevent `ModuleNotFoundError` when optional dependencies are not installed
  - Package can now be imported without installing `flask` or `fastapi` extras
  - Framework-specific imports only occur when calling the respective `enable_*_metrics()` functions
  - Fixes issue where base package installation failed with `ModuleNotFoundError: No module named 'fastapi'`
- Fixed CI workflow externally managed Python environment issues by using `uv sync --extra dev`
- Upgraded deprecated GitHub Actions: `actions/upload-artifact@v3` → `v4`, `codecov-action@v3` → `v4`

### Changed
- `enable_flask_metrics()` and `enable_fastapi_metrics()` now use lazy imports (deferred until function call)
- All CI/CD commands now use `uv run` prefix for consistent environment management

## [1.0.0] - 2025-01-07

### Added
- Initial release of rl-autoscale
- Flask middleware for automatic metrics instrumentation
- FastAPI middleware for automatic metrics instrumentation
- Auto-detection of web framework (Flask vs FastAPI)
- Standardized Prometheus metrics:
  - `http_request_duration_seconds` (Histogram)
  - `http_requests_total` (Counter)
- Path normalization to prevent cardinality explosion
- Configurable histogram buckets optimized for web APIs
- Configurable path exclusions (e.g., /health, /metrics)
- Production-ready error handling
- Comprehensive documentation and examples
- Example applications for Flask and FastAPI

### Features
- One-line integration: `enable_metrics(app, port=8000)`
- Zero-dependency core (only prometheus-client required)
- Optional dependencies for Flask and FastAPI
- Thread-safe metrics collection
- Minimal performance overhead (<1ms per request)
- Support for custom namespaces and labels

[1.0.0]: https://github.com/ghazafm/rl-autoscale/releases/tag/v1.0.0
