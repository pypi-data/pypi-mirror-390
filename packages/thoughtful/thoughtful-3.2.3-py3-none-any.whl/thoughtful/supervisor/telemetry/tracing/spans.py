"""Span creation and lifecycle management for OpenTelemetry tracing."""

import logging
from types import TracebackType
from typing import Any, Optional, Type

from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)


def create_root_span(manifest_uid: str) -> tuple[Any, Any]:
    """
    Create and return a root span context manager and span.

    Args:
        manifest_uid (str): The uid of the manifest/workflow for the span

    Returns:
        tuple[Any, Any]: A tuple containing (span_context_manager, span)

    Raises:
        ValueError: If tracing is not initialized or span creation fails
    """
    try:
        tracer = trace.get_tracer(__name__)
        span_cm = tracer.start_as_current_span(
            name=manifest_uid,
            kind=trace.SpanKind.SERVER,
            attributes={},
            end_on_exit=False,
        )
        span = span_cm.__enter__()
        return span_cm, span
    except Exception as e:
        logger.error("Failed to create root span: %s", str(e))
        raise ValueError(f"Failed to create root span for {manifest_uid}: {str(e)}")


def close_root_span(
    span_cm: Any,
    span: Any,
    exc_type: Optional[Type[Exception]] = None,
    exc_val: Optional[Exception] = None,
    exc_tb: Optional[TracebackType] = None,
) -> None:
    """
    Close a root span with proper status and exception handling.

    Args:
        span_cm: The span context manager
        span: The span to close
        exc_type: Exception type if an exception occurred
        exc_val: Exception value if an exception occurred
        exc_tb: Exception traceback if an exception occurred
    """
    try:
        # Set final status based on whether there was an exception
        if exc_type:
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            if exc_val:
                span.set_attributes(
                    {
                        SpanAttributes.EXCEPTION_TYPE: type(exc_val).__name__,
                        SpanAttributes.EXCEPTION_MESSAGE: str(exc_val),
                    }
                )
                span.record_exception(exc_val)
        else:
            span.set_status(trace.Status(trace.StatusCode.OK))

        # End the span and exit the context manager
        span.end()
        span_cm.__exit__(exc_type, exc_val, exc_tb)
    except Exception as e:
        logger.error(f"Error closing root span: {e}")
