"""Centralized telemetry configuration and setup."""

import logging
import os
import platform
import socket
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Dict, Optional, Type

from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import (
    ResourceAttributes as SemConvResourceAttributes,
)
from thoughtful.supervisor.telemetry.common import TelemetryType, get_vault_otlp_config
from thoughtful.supervisor.telemetry.common import resolve_auth_headers
from thoughtful.supervisor.telemetry.common import resolve_shared_endpoint
from thoughtful.supervisor.telemetry.logging.config import initialize_logging
from thoughtful.supervisor.telemetry.meter_utils import set_current_service_name
from thoughtful.supervisor.telemetry.metrics.config import initialize_metrics
from thoughtful.supervisor.telemetry.tracing import close_root_span
from thoughtful.supervisor.telemetry.tracing.config import initialize_tracing
from thoughtful.supervisor.telemetry.tracing.spans import create_root_span
from thoughtful.supervisor.telemetry.tracing.workflow import analyze_workflow_structure

logger = logging.getLogger(__name__)


# Global telemetry state management
_global_telemetry_context: Optional["TelemetryContext"] = None


def get_global_telemetry_context() -> Optional["TelemetryContext"]:
    """
    Get the global telemetry context if it exists.

    Returns:
        The global TelemetryContext or None if not initialized
    """
    return _global_telemetry_context


def set_global_telemetry_context(context: "TelemetryContext") -> None:
    """
    Set the global telemetry context.

    Args:
        context: The TelemetryContext to set as global
    """
    global _global_telemetry_context
    _global_telemetry_context = context


def clear_global_telemetry_context() -> None:
    """Clear the global telemetry context."""
    global _global_telemetry_context
    _global_telemetry_context = None


@dataclass
class TelemetryConfig:
    """Centralized configuration for all telemetry components."""

    # Service identification
    service_name: str
    manifest: Optional[Any] = None

    # Shared OTLP endpoint for all telemetry types
    endpoint: Optional[str] = None
    is_bitwarden_endpoint: bool = False

    # Authentication headers for OTLP requests
    auth_headers: Optional[Dict[str, str]] = None

    # Feature toggles to enable/disable telemetry components
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True

    # Custom resource attributes to add to all telemetry data
    resource_attributes: Optional[Dict[str, Any]] = None


@dataclass
class TelemetryContext:
    """Context object holding initialized telemetry components."""

    # Core components
    root_span_cm: Optional[Any] = None
    root_span: Optional[Any] = None
    meter_provider: Optional[Any] = None
    meter: Optional[Any] = None

    # Configuration used
    config: Optional[TelemetryConfig] = None

    # Resource built for all components
    resource: Optional[Resource] = None


class TelemetryConfigBuilder:
    """Builder for creating TelemetryConfig with proper defaults and validation."""

    def __init__(self):
        self._config = TelemetryConfig(service_name="")

    def with_service_name(self, name: str) -> "TelemetryConfigBuilder":
        """Set the service name."""
        self._config.service_name = name
        return self

    def with_manifest(self, manifest: Any) -> "TelemetryConfigBuilder":
        """Set the manifest object."""
        self._config.manifest = manifest
        return self

    def with_otlp_config(
        self, otlp_config: Optional[Dict[str, Any]]
    ) -> "TelemetryConfigBuilder":
        """Resolve all endpoints and auth from OTLP config, with automatic Bitwarden fallback."""
        # If no explicit config provided, try to use Bitwarden configuration
        if not otlp_config:
            try:
                vault_config = get_vault_otlp_config()
                if vault_config:
                    otlp_config = vault_config
                    logger.debug("Using Bitwarden configuration for telemetry")
                else:
                    logger.debug("No Bitwarden configuration found, using defaults")
            except Exception as e:
                logger.debug("Failed to get Bitwarden configuration: %s", str(e))

        if not otlp_config:
            return self

        # Resolve shared endpoint for all telemetry types (only once)
        (
            self._config.endpoint,
            self._config.is_bitwarden_endpoint,
        ) = resolve_shared_endpoint(otlp_config)

        # Resolve authentication headers
        try:
            self._config.auth_headers = resolve_auth_headers(otlp_config)
        except Exception as e:
            logger.error("Failed to resolve telemetry authentication: %s", str(e))
            self._config.auth_headers = {}

        return self

    def with_feature_toggles(self, **toggles) -> "TelemetryConfigBuilder":
        """Set feature toggles."""
        for key, value in toggles.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        return self

    def build(self) -> TelemetryConfig:
        """Build and validate the configuration."""
        self._validate()
        return self._config

    def _validate(self) -> None:
        """Validate the configuration."""
        if not self._config.service_name:
            raise ValueError("Service name is required")

        # Extract service name from manifest if available
        if (
            self._config.manifest
            and hasattr(self._config.manifest, "uid")
            and self._config.manifest.uid
        ):
            manifest_uid = self._config.manifest.uid
            if len(manifest_uid) > 5:
                logger.warning(
                    "manifest.uid '%s' exceeds 5 character limit (%d chars). "
                    "Using first 5 characters '%s' for telemetry service name.",
                    manifest_uid,
                    len(manifest_uid),
                    manifest_uid[:5],
                )
            self._config.service_name = manifest_uid[:5]

        if not self._config.service_name:
            raise ValueError("Service name is required")


def extract_machine_attributes() -> Dict[str, Any]:
    """
    Extract machine attributes that are certainly available.
    Focuses on OS-level information and container details.

    Returns:
        Dictionary of machine attributes following OpenTelemetry semantic conventions
    """
    attributes = {}

    attributes[SemConvResourceAttributes.HOST_NAME] = socket.gethostname()
    attributes[SemConvResourceAttributes.HOST_ARCH] = platform.machine()
    attributes[SemConvResourceAttributes.OS_TYPE] = platform.system()
    attributes[SemConvResourceAttributes.OS_VERSION] = platform.version()

    attributes[SemConvResourceAttributes.PROCESS_RUNTIME_NAME] = "python"
    attributes[
        SemConvResourceAttributes.PROCESS_RUNTIME_VERSION
    ] = platform.python_version()

    attributes[SemConvResourceAttributes.DEPLOYMENT_ENVIRONMENT] = (
        "supervisor.prod"
        if os.environ.get("THOUGHTFUL_PRODUCTION")
        else "supervisor.dev"
    )

    if os.environ.get("CONTAINER_ID"):
        attributes[SemConvResourceAttributes.CONTAINER_ID] = os.environ.get(
            "CONTAINER_ID"
        )

    if os.environ.get("IMAGE_NAME"):
        attributes[SemConvResourceAttributes.CONTAINER_IMAGE_NAME] = os.environ.get(
            "IMAGE_NAME"
        )
        attributes[SemConvResourceAttributes.CONTAINER_IMAGE_TAG] = os.environ.get(
            "IMAGE_TAG", "latest"
        )
    return attributes


def extract_workflow_metrics(manifest) -> Dict[str, Any]:
    """
    Extract workflow metrics from manifest data that are certainly available.

    Args:
        manifest: The manifest object containing workflow information

    Returns:
        Dictionary of metrics that can be used as span attributes
    """
    if not manifest:
        return {}

    metrics = {}

    # Basic manifest information
    metrics["sup.manifest.uid"] = manifest.uid
    metrics["sup.manifest.description"] = manifest.description or "unknown"
    metrics["sup.manifest.author"] = manifest.author or "unknown"
    metrics["sup.manifest.source"] = manifest.source

    # Agent type information (optional)
    if hasattr(manifest, "agent_type") and manifest.agent_type:
        metrics["sup.manifest.agent_type"] = manifest.agent_type

    # Workflow structure metrics
    workflow_stats = analyze_workflow_structure(manifest.workflow)
    metrics.update(workflow_stats)

    return metrics


def _build_resource_from_config(config: TelemetryConfig) -> Resource:
    """
    Build a shared resource with machine and workflow attributes.

    This resource will be used across all telemetry components to ensure
    consistent attribute collection and avoid duplication.

    Args:
        config: TelemetryConfig containing service name and manifest

    Returns:
        OpenTelemetry Resource with all attributes
    """
    machine_attributes = extract_machine_attributes()
    workflow_metrics = extract_workflow_metrics(config.manifest)

    attributes: Dict[str, Any] = {
        "service.name": config.service_name,
        **machine_attributes,
        **workflow_metrics,
    }

    # Add agent_type as resource attribute if available
    if (
        config.manifest
        and hasattr(config.manifest, "agent_type")
        and config.manifest.agent_type
    ):
        attributes["agent.type"] = config.manifest.agent_type

    # Add any custom resource attributes from config
    if config.resource_attributes:
        attributes.update(config.resource_attributes)

    return Resource.create(attributes)


def setup_telemetry_from_config(config: TelemetryConfig) -> TelemetryContext:
    """
    Consolidated setup function using TelemetryConfig.

    This is the internal implementation used by the public setup_telemetry function.
    It provides a more maintainable and testable approach to telemetry initialization.

    Args:
        config: TelemetryConfig containing all telemetry configuration

    Returns:
        TelemetryContext with initialized components
    """
    # Metrics are disabled - using traces for dashboards instead
    # This call is a no-op when metrics are disabled, but kept for compatibility
    set_current_service_name(config.service_name)

    # Build shared resource for all telemetry components
    resource = _build_resource_from_config(config)

    # Initialize context
    context = TelemetryContext(config=config, resource=resource)

    # Initialize components with fail-open approach
    if config.enable_tracing and config.endpoint:
        try:
            # Extract span processor configuration from manifest if available
            span_processor_kwargs = {}
            if (
                config.manifest
                and hasattr(config.manifest, "telemetry")
                and config.manifest.telemetry
                and config.manifest.telemetry.span_processor
            ):
                span_config = config.manifest.telemetry.span_processor
                if span_config.max_queue_size is not None:
                    span_processor_kwargs["max_queue_size"] = span_config.max_queue_size
                if span_config.schedule_delay_millis is not None:
                    span_processor_kwargs[
                        "schedule_delay_millis"
                    ] = span_config.schedule_delay_millis
                if span_config.export_timeout_millis is not None:
                    span_processor_kwargs[
                        "export_timeout_millis"
                    ] = span_config.export_timeout_millis
                if span_config.max_export_batch_size is not None:
                    span_processor_kwargs[
                        "max_export_batch_size"
                    ] = span_config.max_export_batch_size

                logger.debug(
                    "Using custom span processor configuration from manifest: %s",
                    span_processor_kwargs,
                )

            initialize_tracing(
                endpoint=config.endpoint,
                headers=config.auth_headers or {},
                resource=resource,
                is_bitwarden_endpoint=config.is_bitwarden_endpoint,
                **span_processor_kwargs,
            )

            # Create root span using the actual service name
            context.root_span_cm, context.root_span = create_root_span(
                config.service_name
            )

            logger.debug("OpenTelemetry tracing initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry tracing: %s", str(e))
            # Continue without tracing

    if config.enable_logging and config.endpoint:
        try:
            # Extract log processor configuration from manifest if available
            log_processor_kwargs = {}
            if (
                config.manifest
                and hasattr(config.manifest, "telemetry")
                and config.manifest.telemetry
                and config.manifest.telemetry.log_processor
            ):
                log_config = config.manifest.telemetry.log_processor
                if log_config.max_queue_size is not None:
                    log_processor_kwargs["max_queue_size"] = log_config.max_queue_size
                if log_config.schedule_delay_millis is not None:
                    log_processor_kwargs[
                        "schedule_delay_millis"
                    ] = log_config.schedule_delay_millis
                if log_config.export_timeout_millis is not None:
                    log_processor_kwargs[
                        "export_timeout_millis"
                    ] = log_config.export_timeout_millis
                if log_config.max_export_batch_size is not None:
                    log_processor_kwargs[
                        "max_export_batch_size"
                    ] = log_config.max_export_batch_size

                logger.debug(
                    "Using custom log processor configuration from manifest: %s",
                    log_processor_kwargs,
                )

            initialize_logging(
                endpoint=config.endpoint,
                headers=config.auth_headers or {},
                resource=resource,
                is_bitwarden_endpoint=config.is_bitwarden_endpoint,
                **log_processor_kwargs,
            )

            logger.debug("OpenTelemetry logging initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry logging: %s", str(e))
            # Continue without logging

    # Metrics are disabled - using traces for dashboards instead
    # if config.enable_metrics and config.endpoint:
    #     try:
    #         # Extract metric reader configuration from manifest if available
    #         metric_reader_kwargs = {}
    #         if (
    #             config.manifest
    #             and hasattr(config.manifest, "telemetry")
    #             and config.manifest.telemetry
    #             and config.manifest.telemetry.metric_reader
    #         ):
    #             metric_config = config.manifest.telemetry.metric_reader
    #             if metric_config.export_interval_millis is not None:
    #                 metric_reader_kwargs["export_interval_millis"] = (
    #                     metric_config.export_interval_millis
    #                 )
    #             if metric_config.export_timeout_millis is not None:
    #                 metric_reader_kwargs["export_timeout_millis"] = (
    #                     metric_config.export_timeout_millis
    #                 )
    #
    #             logger.debug(
    #                 "Using custom metric reader configuration from manifest: %s",
    #                 metric_reader_kwargs,
    #             )
    #
    #         context.meter_provider, context.meter = initialize_metrics(
    #             endpoint=config.endpoint,
    #             headers=config.auth_headers or {},
    #             resource=resource,
    #             is_bitwarden_endpoint=config.is_bitwarden_endpoint,
    #             **metric_reader_kwargs,
    #         )
    #
    #         logger.debug("OpenTelemetry metrics initialized successfully")
    #
    #     except Exception as e:
    #         logger.error("Failed to initialize OpenTelemetry metrics: %s", str(e))
    #         # Continue without metrics

    # Set as global context for easy access
    set_global_telemetry_context(context)

    logger.info("Telemetry initialization completed")
    return context


def shutdown_telemetry_from_context(
    context: TelemetryContext,
    exc_type: Optional[Type[Exception]] = None,
    exc_val: Optional[Exception] = None,
    exc_tb: Optional[TracebackType] = None,
) -> None:
    """
    Shutdown telemetry components and record workflow completion.

    Args:
        context: TelemetryContext containing all telemetry components
        exc_type: Exception type if any
        exc_val: Exception value if any
        exc_tb: Exception traceback if any
    """
    if not context.config:
        return

    # Clean up the root tracing span if it was started
    if context.root_span_cm is not None and context.root_span is not None:
        close_root_span(
            context.root_span_cm, context.root_span, exc_type, exc_val, exc_tb
        )

    # Metrics are disabled - using traces for dashboards instead
    # This is a no-op now as meter_provider will never be set, but kept for safety
    if context.meter_provider is not None:
        try:
            context.meter_provider.shutdown()
        except Exception:
            logger.exception("Failed to shutdown meter provider")

    # Clear global context
    clear_global_telemetry_context()


# Main API functions
def setup_telemetry(
    otlp_config: Optional[Dict[str, Any]] = None,
    manifest: Any = None,
    service_name: str = "sup",
) -> TelemetryContext:
    """
    Initialize all OpenTelemetry telemetry components using TelemetryConfig.

    Args:
        otlp_config: Optional dictionary containing OTLP configuration
        manifest: Optional manifest object for resource attributes and service name
        service_name: Name of the service for resource attributes

    Returns:
        TelemetryContext with initialized components
    """
    config = (
        TelemetryConfigBuilder()
        .with_service_name(service_name)
        .with_manifest(manifest)
        .with_otlp_config(otlp_config)
        .build()
    )

    return setup_telemetry_from_config(config)


def shutdown_telemetry(
    context: TelemetryContext,
    exc_type: Optional[Type[Exception]] = None,
    exc_val: Optional[Exception] = None,
    exc_tb: Optional[TracebackType] = None,
) -> None:
    """
    Shutdown telemetry components and record workflow completion.

    Args:
        context: TelemetryContext containing all telemetry components
        exc_type: Exception type if any
        exc_val: Exception value if any
        exc_tb: Exception traceback if any
    """
    shutdown_telemetry_from_context(context, exc_type, exc_val, exc_tb)


# Convenience functions for accessing telemetry components
def get_current_meter():
    """
    Get the current meter from the global telemetry context.

    Note: Metrics are disabled - using traces for dashboards instead.
    This function will always return None as metrics are not initialized.

    Returns:
        The current meter instance or None if not available (always None when metrics disabled)
    """
    context = get_global_telemetry_context()
    return context.meter if context else None


def get_current_root_span():
    """
    Get the current root span from the global telemetry context.

    Returns:
        The current root span instance or None if not available
    """
    context = get_global_telemetry_context()
    return context.root_span if context else None


def is_telemetry_initialized() -> bool:
    """
    Check if telemetry is currently initialized.

    Returns:
        True if telemetry is initialized, False otherwise
    """
    return get_global_telemetry_context() is not None


def get_telemetry_config() -> Optional[TelemetryConfig]:
    """
    Get the current telemetry configuration.

    Returns:
        The current TelemetryConfig or None if not initialized
    """
    context = get_global_telemetry_context()
    return context.config if context else None
