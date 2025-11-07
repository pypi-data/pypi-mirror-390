"""OpenTelemetry tracing utilities for Thoughtful supervisor."""

from thoughtful.supervisor.telemetry.tracing.config import initialize_tracing
from thoughtful.supervisor.telemetry.tracing.spans import close_root_span
from thoughtful.supervisor.telemetry.tracing.spans import create_root_span

__all__ = [
    "initialize_tracing",
    "create_root_span",
    "close_root_span",
]
