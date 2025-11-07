"""Common utilities for telemetry components."""

import logging
from enum import Enum
from typing import Any, Dict, Optional

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter as GRPCOTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter as GRPCOTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GRPCOTLPSpanExporter,
)
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter as HTTPOTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as HTTPOTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPOTLPSpanExporter,
)
from t_vault import bw_get_item

logger = logging.getLogger(__name__)


def shorten_hostname(hostname: str) -> str:
    """
    Smart shorten hostnames for external service metrics while preserving meaning.

    Applies multiple shortening strategies to reduce hostname length while keeping
    the most important identifying information.

    Args:
        hostname: The original hostname to shorten

    Returns:
        Shortened hostname that's more suitable for metric names
    """
    if not hostname:
        return hostname

    # Strategy 1: Remove common API prefixes
    if hostname.startswith("api."):
        hostname = hostname[4:]  # Remove "api."

    # Strategy 2: Abbreviate common service names
    abbreviations = {
        # General services
        "placeholder": "ph",
        "typicode": "tc",
        "github": "gh",
        "httpbin": "hb",
        "googleapis": "gapi",
        "amazonaws": "aws",
        "microsoft": "ms",
        "cloudflare": "cf",
        # LLM/AI services
        "openai": "oai",
        "anthropic": "ant",
        "claude": "cl",
        "gpt": "gpt",
        "gemini": "gem",
    }

    for full_name, abbrev in abbreviations.items():
        if full_name in hostname:
            hostname = hostname.replace(full_name, abbrev)

    # Strategy 3: Remove redundant TLDs for well-known services
    # Keep the main identifying part
    if "." in hostname:
        parts = hostname.split(".")
        if len(parts) >= 3:
            # For subdomain.domain.tld, keep domain.tld if it's well-known
            main_domain = ".".join(parts[-2:])
            if main_domain in [
                "github.com",
                "google.com",
                "amazon.com",
                "openai.com",
                "anthropic.com",
            ]:
                hostname = main_domain
        elif len(parts) == 2:
            # For domain.tld, keep as-is if it's short enough
            if len(hostname) <= 15:  # Reasonable length for metric names
                pass  # Keep as-is
            else:
                # If too long, keep just the domain part
                hostname = parts[0]

    return hostname


class TelemetryType(Enum):
    """Telemetry component types."""

    TRACING = "traces"
    LOGGING = "logs"
    METRICS = "metrics"


def get_vault_otlp_config() -> Dict[str, Any]:
    """
    Get OTLP configuration from vault.

    Returns:
        Dictionary containing vault endpoints and headers, or empty dict if unavailable
    """
    try:
        vault_data = bw_get_item("otl-info")
        if vault_data:
            logger.debug("Retrieved OTLP configuration from vault")

            config = {}

            # Get endpoint from username (expects gRPC endpoint in format hostname:port)
            if hasattr(vault_data, "username") and vault_data.username:
                base_endpoint = vault_data.username
                # Use endpoint directly from Bitwarden (already includes port 4317)

                # Use the same gRPC endpoint for all telemetry types
                for telemetry_type in TelemetryType:
                    config[f"{telemetry_type.value}_endpoint"] = base_endpoint

            # Get auth headers from password (for gRPC, use simple key-value format)
            if hasattr(vault_data, "password") and vault_data.password:
                password = vault_data.password
                # For gRPC, use simple metadata format instead of Basic auth
                config["headers"] = {"authorization": password}

            return config
        else:
            logger.debug("No OTLP configuration found in vault")
    except Exception:
        logger.warning("Failed to get OTLP configuration from vault")

    # Return empty config if vault is unavailable
    return {}


def resolve_shared_endpoint(
    otlp_config: Optional[Dict[str, Any]] = None,
) -> tuple[str, bool]:
    """
    Resolve a shared endpoint for all telemetry components using a 3-tier priority system.

    Priority 1: Explicitly provided endpoint in config
    Priority 2: Any telemetry type endpoint from config (tracing, metrics, or logging)
    Priority 3: Endpoint from Bitwarden vault configuration

    Args:
        otlp_config: Optional configuration override

    Returns:
        Tuple of (endpoint, is_bitwarden_endpoint)

    Raises:
        ValueError: If endpoint resolution fails or no configuration is found
    """
    # Priority 1: Use explicitly provided endpoint
    if otlp_config and "endpoint" in otlp_config:
        endpoint = otlp_config["endpoint"]
        logger.debug("Using explicitly provided endpoint")
        is_bitwarden = False
    # Priority 2: Use any telemetry type endpoint from config
    elif otlp_config:
        # Check for any telemetry type endpoint
        for telemetry_type in TelemetryType:
            if f"{telemetry_type.value}_endpoint" in otlp_config:
                endpoint = otlp_config[f"{telemetry_type.value}_endpoint"]
                logger.debug("Using config endpoint for %s", telemetry_type.value)
                is_bitwarden = False
                break
        else:
            # No endpoint found in config, try vault
            endpoint, is_bitwarden = _resolve_vault_endpoint()
    else:
        # No config provided, try vault
        endpoint, is_bitwarden = _resolve_vault_endpoint()

    # Basic validation - just ensure it's a non-empty string
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("OTLP endpoint must be a non-empty string")

    return endpoint, is_bitwarden


def _resolve_vault_endpoint() -> tuple[str, bool]:
    """
    Resolve endpoint from Bitwarden vault configuration.

    Returns:
        Tuple of (endpoint, is_bitwarden_endpoint)

    Raises:
        ValueError: If no endpoint is found in vault
    """
    vault_config = get_vault_otlp_config()
    if vault_config:
        # Check for any telemetry type endpoint in vault
        for telemetry_type in TelemetryType:
            if f"{telemetry_type.value}_endpoint" in vault_config:
                endpoint = vault_config[f"{telemetry_type.value}_endpoint"]
                logger.debug("Using vault endpoint for %s", telemetry_type.value)
                return endpoint, True

    # No endpoint found - raise error
    raise ValueError("No endpoint configuration found in vault or config")


def resolve_endpoint(
    telemetry_type: TelemetryType,
    otlp_config: Optional[Dict[str, Any]] = None,
) -> tuple[str, bool]:
    """
    Resolve endpoint for a telemetry component using a 3-tier priority system.

    Priority 1: Explicitly provided endpoint in config
    Priority 2: Specific telemetry type endpoint from config
    Priority 3: Endpoint from Bitwarden vault configuration

    Args:
        telemetry_type: The type of telemetry component
        otlp_config: Optional configuration override

    Returns:
        Tuple of (endpoint, is_bitwarden_endpoint)

    Raises:
        ValueError: If endpoint resolution fails or no configuration is found
    """
    # Priority 1: Use explicitly provided endpoint
    if otlp_config and "endpoint" in otlp_config:
        endpoint = otlp_config["endpoint"]
        logger.debug("Using explicitly provided endpoint")
        is_bitwarden = False
    # Priority 2: Use specific telemetry type endpoint from config
    elif otlp_config and f"{telemetry_type.value}_endpoint" in otlp_config:
        endpoint = otlp_config[f"{telemetry_type.value}_endpoint"]
        logger.debug("Using config endpoint for %s", telemetry_type.value)
        is_bitwarden = False
    # Priority 3: Look in vault for endpoint
    else:
        vault_config = get_vault_otlp_config()
        if vault_config and f"{telemetry_type.value}_endpoint" in vault_config:
            endpoint = vault_config[f"{telemetry_type.value}_endpoint"]
            logger.debug("Using vault endpoint for %s", telemetry_type.value)
            is_bitwarden = True
        else:
            # No endpoint found - raise error
            raise ValueError(
                f"No endpoint configuration found for {telemetry_type.value}"
            )

    # Basic validation - just ensure it's a non-empty string
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("OTLP endpoint must be a non-empty string")

    return endpoint, is_bitwarden


def resolve_auth_headers(
    otlp_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Resolve authentication headers for telemetry components using a 3-tier priority system.

    Priority 1: Headers from explicit config
    Priority 2: Headers from Bitwarden vault configuration
    Priority 3: Empty headers (no authentication)

    Args:
        otlp_config: Optional configuration override

    Returns:
        Dictionary of authentication headers
    """
    # Priority 1: Use headers from config if provided
    if otlp_config and "headers" in otlp_config:
        logger.debug("Using explicitly provided auth headers")
        return otlp_config["headers"]

    # Priority 2: Look in vault for headers
    vault_config = get_vault_otlp_config()
    if vault_config and "headers" in vault_config:
        logger.debug("Using vault auth headers")
        return vault_config["headers"]

    # Priority 3: Fall back to empty headers
    logger.debug("Using empty auth headers (no authentication)")
    return {}


def build_otlp_exporter(
    telemetry_type: TelemetryType,
    endpoint: str,
    headers: Dict[str, str],
    is_bitwarden_endpoint: bool = False,
) -> Any:
    """
    Build appropriate OTLP exporter based on telemetry type and endpoint protocol.

    Args:
        telemetry_type: The type of telemetry component
        endpoint: OTLP endpoint URL
        headers: Authentication headers
        is_bitwarden_endpoint: Whether the endpoint came from Bitwarden vault

    Returns:
        Appropriate OTLP exporter instance
    """
    # Smart protocol detection logic
    if is_bitwarden_endpoint:
        # Bitwarden endpoints always use gRPC
        use_grpc = True
    else:
        # Custom endpoints: check port to determine protocol
        if ":4317" in endpoint:
            use_grpc = True
        elif ":4318" in endpoint or ":" not in endpoint:
            use_grpc = False
        else:
            # Fallback: check if endpoint starts with protocol
            use_grpc = not endpoint.startswith(("http://", "https://"))

    if telemetry_type == TelemetryType.TRACING:
        return (
            HTTPOTLPSpanExporter(endpoint=endpoint, headers=headers)
            if not use_grpc
            else GRPCOTLPSpanExporter(endpoint=endpoint, headers=headers)
        )

    elif telemetry_type == TelemetryType.METRICS:
        return (
            HTTPOTLPMetricExporter(endpoint=endpoint, headers=headers)
            if not use_grpc
            else GRPCOTLPMetricExporter(endpoint=endpoint, headers=headers)
        )

    elif telemetry_type == TelemetryType.LOGGING:
        return (
            HTTPOTLPLogExporter(endpoint=endpoint, headers=headers)
            if not use_grpc
            else GRPCOTLPLogExporter(endpoint=endpoint, headers=headers)
        )

    else:
        raise ValueError(f"Unknown telemetry type: {telemetry_type}")
