"""
OpenTelemetry Tracing setup.

Hooks up tracer provider and exporter (OTLP gRPC/HTTP) to collect distributed
traces for all incoming requests, repository calls, and database operations.
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import get_settings
from app.db.database import get_engine


def setup_tracing(app: FastAPI) -> None:
    """
    Initialize OpenTelemetry trace providers and auto-instrumentations.
    """
    settings = get_settings()
    if not settings.ENABLE_TRACING:
        return

    # Define Service Identity Resource
    resource = Resource.create(
        attributes={
            SERVICE_NAME: settings.APP_NAME,
            "service.version": settings.APP_VERSION,
            "deployment.environment": settings.ENVIRONMENT.value,
        }
    )

    # Configure global tracer provider
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.OTLP_ENDPOINT))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument FastAPI request lifecycles
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=provider,
        excluded_urls="health,health/live,health/ready,metrics",
    )

    # Instrument SQLAlchemy transactions
    engine = get_engine()
    SQLAlchemyInstrumentor().instrument(
        engine=engine.sync_engine,
        tracer_provider=provider,
    )
