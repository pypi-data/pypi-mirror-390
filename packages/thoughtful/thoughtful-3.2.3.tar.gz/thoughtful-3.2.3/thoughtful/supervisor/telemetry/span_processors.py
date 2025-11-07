"""Custom span processors for telemetry."""

import logging
from typing import Any, Optional

from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.trace import Span

logger = logging.getLogger(__name__)


class ExternalServiceCallSpanProcessor(SpanProcessor):
    """
    A span processor for external service call tracking.

    This processor is kept for compatibility but no longer records metrics.
    Spans are still created for external calls, but metrics are no longer recorded.
    """

    def __init__(self):
        """Initialize the external service call span processor."""
        super().__init__()

    def on_start(self, span: Span, parent_context: Optional[Any] = None) -> None:
        """
        Called when a span is started.

        Args:
            span: The span that was started
            parent_context: The parent context
        """
        # We don't need to do anything on span start

    def on_end(self, span: Span) -> None:
        """
        Called when a span is ended.

        Args:
            span: The span that was ended
        """
        # External service call tracking has been removed
        # Spans are still created for external calls, but metrics are no longer recorded

    def shutdown(self) -> None:
        """Shutdown the span processor."""
        # No cleanup needed for this processor

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending spans.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            True if flush was successful, False otherwise
        """
        # No pending spans to flush for this processor
        return True
