"""Configuration and initialization for OpenTelemetry metrics."""

import logging
from typing import Any, Dict

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter

logger = logging.getLogger(__name__)


def initialize_metrics(
    endpoint: str,
    headers: Dict[str, str],
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
    export_interval_millis: int = 10000,
    export_timeout_millis: int = 5000,
) -> tuple[Any, Any]:
    """
    Initialize OpenTelemetry metrics with OTLP exporter using centralized configuration.

    Uses PeriodicExportingMetricReader for non-blocking async export. Falls back to
    console export if OTLP endpoint is unavailable.

    Args:
        endpoint: OTLP endpoint for metrics export
        headers: Authentication headers for OTLP requests
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint: Whether the endpoint came from Bitwarden vault
        export_interval_millis: Interval in milliseconds between exports (default: 10000)
        export_timeout_millis: Maximum timeout in milliseconds for exports (default: 5000)

    Returns:
        Tuple of (meter_provider, meter)
    """
    if resource is None:
        raise ValueError("Resource is required for metrics initialization")

    metric_readers = []
    otlp_configured = False

    # Attempt OTLP export with fallback to console
    try:
        # Create metric exporter using centralized function with smart protocol detection
        exporter = build_otlp_exporter(
            TelemetryType.METRICS, endpoint, headers, is_bitwarden_endpoint
        )

        # Create metric reader with periodic export (async, non-blocking)
        otlp_reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=export_interval_millis,
            export_timeout_millis=export_timeout_millis,
        )
        metric_readers.append(otlp_reader)
        otlp_configured = True
        logger.info(
            "OpenTelemetry metrics initialized with OTLP endpoint "
            "(interval=%dms, timeout=%dms)",
            export_interval_millis,
            export_timeout_millis,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize OTLP metric exporter (%s), falling back to console export",
            str(exc),
        )

    # Fallback to console export if OTLP failed
    if not otlp_configured:
        console_exporter = ConsoleMetricExporter()
        console_reader = PeriodicExportingMetricReader(
            console_exporter,
            export_interval_millis=60000,  # Export every 60 seconds for console
            export_timeout_millis=export_timeout_millis,
        )
        metric_readers.append(console_reader)
        logger.info(
            "OpenTelemetry metrics initialized with console export (fallback) "
            "(interval=60000ms, timeout=%dms)",
            export_timeout_millis,
        )

    # Create meter provider with configured readers
    meter_provider = MeterProvider(
        metric_readers=metric_readers,
        resource=resource,
    )

    # Set global meter provider
    metrics.set_meter_provider(meter_provider)

    # Get meter for the service from the resource
    service_name = resource.attributes.get("service.name", "sup")
    meter = meter_provider.get_meter(service_name)

    return meter_provider, meter
