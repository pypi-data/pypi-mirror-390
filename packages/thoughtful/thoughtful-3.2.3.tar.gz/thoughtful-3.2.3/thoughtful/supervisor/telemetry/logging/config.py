"""Configuration and initialization for OpenTelemetry logging."""

import logging
import os
from typing import Dict, Tuple

# OpenTelemetry Logs API is available in opentelemetry-sdk >= 1.27.0
from opentelemetry._logs import LoggerProvider
from opentelemetry._logs import get_logger as get_otel_logger
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider as SDKLoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.resources import Resource
from thoughtful.supervisor.telemetry.common import TelemetryType, build_otlp_exporter

logger = logging.getLogger(__name__)


def initialize_logging(
    endpoint: str,
    headers: Dict[str, str],
    resource: Resource,
    is_bitwarden_endpoint: bool = False,
    *,
    replace_root_handlers: bool = False,
    max_queue_size: int = 2048,
    schedule_delay_millis: int = 5000,
    export_timeout_millis: int = 30000,
    max_export_batch_size: int = 512,
) -> Tuple[object, object]:
    """
    Initialize OpenTelemetry Logs and install a bridge handler on stdlib logging.

    Uses BatchLogRecordProcessor for non-blocking async export. Falls back to
    console export if OTLP endpoint is unavailable.

    Args:
        endpoint: OTLP endpoint for log export
        headers: Authentication headers for OTLP requests
        resource: OpenTelemetry Resource to use (required)
        is_bitwarden_endpoint: Whether the endpoint came from Bitwarden vault
        replace_root_handlers: If True, replace existing root handlers to avoid duplicates
        max_queue_size: Maximum queue size for BatchLogRecordProcessor (default: 2048)
        schedule_delay_millis: Delay in milliseconds between exports (default: 5000)
        export_timeout_millis: Maximum timeout in milliseconds for exports (default: 30000)
        max_export_batch_size: Maximum batch size for exports (default: 512)

    Returns:
        Tuple of (logger_provider, logging_handler)
    """
    provider = SDKLoggerProvider(resource=resource)

    # Attempt OTLP export with fallback to console
    otlp_configured = False
    exporter = None

    try:
        exporter = build_otlp_exporter(
            TelemetryType.LOGGING, endpoint, headers, is_bitwarden_endpoint
        )
        # Use BatchLogRecordProcessor for async, non-blocking export
        processor = BatchLogRecordProcessor(
            exporter,
            max_queue_size=max_queue_size,
            schedule_delay_millis=schedule_delay_millis,
            export_timeout_millis=export_timeout_millis,
            max_export_batch_size=max_export_batch_size,
        )
        provider.add_log_record_processor(processor)
        otlp_configured = True
        logger.info(
            "OpenTelemetry logging initialized with OTLP endpoint "
            "(queue_size=%d, delay=%dms, timeout=%dms, batch_size=%d)",
            max_queue_size,
            schedule_delay_millis,
            export_timeout_millis,
            max_export_batch_size,
        )
    except Exception as exc:
        logger.warning(
            "Failed to initialize OTLP log exporter (%s), falling back to console export",
            str(exc),
        )

    # Fallback to console export if OTLP failed
    if not otlp_configured:
        console_exporter = ConsoleLogExporter()
        console_processor = BatchLogRecordProcessor(
            console_exporter,
            max_queue_size=max_queue_size,
            schedule_delay_millis=schedule_delay_millis,
            export_timeout_millis=export_timeout_millis,
            max_export_batch_size=max_export_batch_size,
        )
        provider.add_log_record_processor(console_processor)
        logger.info(
            "OpenTelemetry logging initialized with console export (fallback) "
            "(queue_size=%d, delay=%dms, timeout=%dms, batch_size=%d)",
            max_queue_size,
            schedule_delay_millis,
            export_timeout_millis,
            max_export_batch_size,
        )

    set_logger_provider(provider)

    handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    root_logger = logging.getLogger()
    if replace_root_handlers:
        root_logger.handlers = []
    root_logger.addHandler(handler)

    # Maintain existing root level unless env overrides
    level_name = os.environ.get("THOUGHTFUL_OTEL_LOG_LEVEL")
    if level_name:
        log_level = getattr(logging, level_name.upper(), None)
        if log_level is not None:
            root_logger.setLevel(log_level)
        else:
            logger.warning("Invalid THOUGHTFUL_OTEL_LOG_LEVEL: %s", level_name)

    return (provider, handler)
