"""Telemetry endpoint exclusions to prevent child traces from telemetry export requests."""

import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def get_excluded_endpoints() -> List[str]:
    """Get the list of currently excluded telemetry endpoints."""
    # Default telemetry endpoints to exclude
    telemetry_endpoints = [
        "otel-collector.obs.thoughtful.ai",  # Current OTLP collector
        "otel-collector-private.obs.thoughtful.ai",  # Private OTLP collector
        "otel.thoughthub.thoughtful-dev.ai",  # Dev OTLP collector
        "localhost:8080",
        "localhost",  # Local development
        "127.0.0.1",  # Local development
    ]

    # Check for custom exclusions from environment
    custom_exclusions = os.environ.get("THOUGHTFUL_TELEMETRY_EXCLUDED_ENDPOINTS")
    if custom_exclusions:
        custom_list = [endpoint.strip() for endpoint in custom_exclusions.split(",")]
        telemetry_endpoints.extend(custom_list)
        # Remove duplicates while preserving order
        seen = set()
        telemetry_endpoints = [
            x for x in telemetry_endpoints if not (x in seen or seen.add(x))
        ]

    return telemetry_endpoints
