"""Automatic instrumentation setup for HTTP and gRPC."""

import logging

from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from thoughtful.supervisor.telemetry.exclusions import get_excluded_endpoints

logger = logging.getLogger(__name__)


def initialize_http_instrumentation() -> None:
    """Initialize automatic HTTP instrumentation for requests and httpx."""
    excluded_urls = ",".join(get_excluded_endpoints())

    try:
        # Exclude telemetry endpoints to prevent creating child traces for log/metric/trace export
        RequestsInstrumentor().instrument(excluded_urls=excluded_urls)
        logger.info(
            f"HTTP instrumentation enabled for requests library (excluded: {excluded_urls})"
        )
    except Exception as e:
        logger.warning(f"Failed to initialize requests instrumentation: {e}")

    try:
        # Exclude telemetry endpoints for httpx as well
        HTTPXClientInstrumentor().instrument(excluded_urls=excluded_urls)
        logger.info(
            f"HTTP instrumentation enabled for httpx library (excluded: {excluded_urls})"
        )
    except Exception as e:
        logger.warning(f"Failed to initialize httpx instrumentation: {e}")


def initialize_grpc_instrumentation() -> None:
    """Initialize automatic gRPC instrumentation."""
    excluded_urls = ",".join(get_excluded_endpoints())

    try:
        # Exclude telemetry endpoints for gRPC as well
        GrpcInstrumentorClient().instrument(excluded_urls=excluded_urls)
        logger.info(
            f"gRPC instrumentation enabled for client (excluded: {excluded_urls})"
        )
    except Exception as e:
        logger.warning(f"Failed to initialize gRPC client instrumentation: {e}")

    try:
        GrpcInstrumentorServer().instrument()
        logger.info("gRPC instrumentation enabled for server")
    except Exception as e:
        logger.warning(f"Failed to initialize gRPC server instrumentation: {e}")
