from __future__ import annotations

from .config import get_settings


def configure_telemetry() -> None:
    settings = get_settings()
    if not settings.otel_exporter_otlp_endpoint:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": "flowrebase-api"}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)))
        trace.set_tracer_provider(provider)
    except Exception:
        # Telemetry must never prevent the control plane from starting.
        return
