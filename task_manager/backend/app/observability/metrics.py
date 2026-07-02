"""
Prometheus Metrics instrumentation.

Defines API latency, request counters, error tracking, and active connection gauges
to expose a Prometheus-compatible metrics endpoint.
"""

from fastapi import FastAPI, Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

from app.core.config import get_settings

# ── Counters & Metrics Definitions ──────────────────────────────────────────

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests processed",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0),
)

ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of active HTTP requests currently being processed",
)

ERROR_COUNT = Counter(
    "app_errors_total",
    "Total number of application errors and exceptions",
    ["error_code"],
)


class PrometheusMetrics:
    """Helper metrics interface."""

    @staticmethod
    def record_error(error_code: str) -> None:
        """Increment error counts for monitoring alerts."""
        ERROR_COUNT.labels(error_code=error_code).inc()


def setup_metrics(app: FastAPI) -> None:
    """
    Mount Prometheus metrics endpoints and middleware on the FastAPI app.
    """
    settings = get_settings()
    if not settings.ENABLE_METRICS:
        return

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Intercept requests to record duration and status code metrics."""
        # Skip profiling metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.scope.get("route")
        endpoint_path = endpoint.path if endpoint else request.url.path

        ACTIVE_REQUESTS.inc()
        import time

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            status_code = 500
            raise
        finally:
            duration = time.perf_counter() - start_time
            ACTIVE_REQUESTS.dec()
            REQUEST_COUNT.labels(method=method, endpoint=endpoint_path, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint_path).observe(duration)

    @app.get("/metrics", tags=["System Health"], include_in_schema=False)
    def metrics_endpoint() -> Response:
        """
        Expose collected Prometheus metrics in raw text format.
        Scraped by Prometheus server.
        """
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
