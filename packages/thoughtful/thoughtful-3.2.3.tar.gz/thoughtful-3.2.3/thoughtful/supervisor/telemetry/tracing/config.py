"""Core tracing configuration and initialization."""

import logging
from typing import Dict, Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter
from thoughtful.supervisor.telemetry.span_processors import (
    ExternalServiceCallSpanProcessor,
)
from thoughtful.supervisor.telemetry.tracing.instrumentation import (
    initialize_grpc_instrumentation,
)
from thoughtful.supervisor.telemetry.tracing.instrumentation import (
    initialize_http_instrumentation,
)

logger = logging.getLogger(__name__)


def initialize_tracing(
    *,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    enable_console_export: bool = False,
    enable_http_instrumentation: bool = True,
    enable_grpc_instrumentation: bool = True,
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
    max_queue_size: int = 2048,
    schedule_delay_millis: int = 5000,
    export_timeout_millis: int = 30000,
    max_export_batch_size: int = 512,
) -> None:
    """Configure a global :class:`TracerProvider`.

    Uses BatchSpanProcessor for non-blocking async export. Falls back to
    console export if OTLP endpoint is unavailable.

    Args:
        endpoint (str): The OTLP endpoint URL.
        headers (Dict[str, str], optional): Headers to include in OTLP requests.
        enable_console_export (bool): Whether to also export spans to console.
        enable_http_instrumentation (bool): Whether to automatically instrument HTTP libraries.
        enable_grpc_instrumentation (bool): Whether to automatically instrument gRPC.
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint (bool): Whether the endpoint came from Bitwarden vault
        max_queue_size: Maximum queue size for BatchSpanProcessor (default: 2048)
        schedule_delay_millis: Delay in milliseconds between exports (default: 5000)
        export_timeout_millis: Maximum timeout in milliseconds for exports (default: 30000)
        max_export_batch_size: Maximum batch size for exports (default: 512)
    """
    provider = TracerProvider(resource=resource)

    # Attempt OTLP export with fallback to console
    otlp_configured = False

    try:
        # Create exporter using centralized function with smart protocol detection
        exporter = build_otlp_exporter(
            TelemetryType.TRACING, endpoint, headers or {}, is_bitwarden_endpoint
        )

        # Use BatchSpanProcessor for async, non-blocking export
        processor = BatchSpanProcessor(
            exporter,
            max_queue_size=max_queue_size,
            schedule_delay_millis=schedule_delay_millis,
            export_timeout_millis=export_timeout_millis,
            max_export_batch_size=max_export_batch_size,
        )
        provider.add_span_processor(processor)
        otlp_configured = True
        logger.info(
            "OpenTelemetry tracing initialized with OTLP endpoint "
            "(queue_size=%d, delay=%dms, timeout=%dms, batch_size=%d)",
            max_queue_size,
            schedule_delay_millis,
            export_timeout_millis,
            max_export_batch_size,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize OTLP trace exporter (%s), falling back to console export",
            str(exc),
        )

    # Fallback to console export if OTLP failed or explicitly requested
    if not otlp_configured or enable_console_export:
        console_processor = BatchSpanProcessor(
            ConsoleSpanExporter(),
            max_queue_size=max_queue_size,
            schedule_delay_millis=schedule_delay_millis,
            export_timeout_millis=export_timeout_millis,
            max_export_batch_size=max_export_batch_size,
        )
        provider.add_span_processor(console_processor)
        if not otlp_configured:
            logger.info(
                "OpenTelemetry tracing initialized with console export (fallback) "
                "(queue_size=%d, delay=%dms, timeout=%dms, batch_size=%d)",
                max_queue_size,
                schedule_delay_millis,
                export_timeout_millis,
                max_export_batch_size,
            )
        else:
            logger.info("OpenTelemetry tracing: console export enabled alongside OTLP")

    # Add custom span processor for external service call metrics
    provider.add_span_processor(ExternalServiceCallSpanProcessor())

    trace.set_tracer_provider(provider)

    if enable_http_instrumentation:
        initialize_http_instrumentation()

    if enable_grpc_instrumentation:
        initialize_grpc_instrumentation()
