"""Histogram metrics utilities for OpenTelemetry."""

import logging
from typing import Any

from opentelemetry import metrics

logger = logging.getLogger(__name__)


def record_step_duration(meter: Any, step_id: str, duration_ms: float) -> None:
    """
    Record step duration in a service-specific histogram.

    Args:
        meter: OpenTelemetry meter instance
        step_id: ID of the step
        duration_ms: Duration in milliseconds
    """
    if not meter:
        logger.warning("No meter provided for recording step duration")
        return

    try:
        # Create a step-specific histogram
        histogram = meter.create_histogram(
            name=f"sup.{step_id}",
            description=f"Duration of step {step_id} execution in milliseconds",
            unit="ms",
        )

        if histogram:
            histogram.record(duration_ms)
            logger.debug(
                "Recorded step duration: %s = %.2f ms",
                step_id,
                duration_ms,
            )
    except Exception as e:
        logger.error("Failed to record step duration: %s", str(e))
