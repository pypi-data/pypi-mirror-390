"""Utilities for accessing OpenTelemetry meter instances."""

import logging
from typing import Any, Optional

from opentelemetry import metrics

logger = logging.getLogger(__name__)

# Global storage for the current service name
_current_service_name: Optional[str] = None


def set_current_service_name(service_name: str) -> None:
    """
    Set the current service name for meter retrieval.

    Args:
        service_name: The service name to use for meter retrieval
    """
    global _current_service_name
    _current_service_name = service_name
    logger.debug("Set current service name: %s", _current_service_name)


def get_current_meter() -> Optional[Any]:
    """
    Get the current OpenTelemetry meter instance.

    Returns:
        The current meter instance if available, None otherwise
    """
    try:
        meter_provider = metrics.get_meter_provider()
        if meter_provider:
            # Use the globally stored service name if available
            global _current_service_name
            if _current_service_name:
                service_name = _current_service_name
                logger.debug("Using stored service name: %s", service_name)
            else:
                # Fallback to default if no service name is stored
                service_name = "sup"
                logger.debug("Using fallback service name: %s", service_name)

            meter = meter_provider.get_meter(service_name)
            logger.debug("Retrieved meter for service: %s", service_name)
            return meter
    except Exception as e:
        logger.debug("Failed to get current meter: %s", str(e))
    return None
