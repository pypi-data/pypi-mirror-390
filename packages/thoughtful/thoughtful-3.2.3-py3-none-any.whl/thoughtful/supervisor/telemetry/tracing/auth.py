"""Authentication handling for OTLP endpoints."""

import base64
import logging
from typing import Dict, Optional

from t_vault import bw_get_item

logger = logging.getLogger(__name__)


def get_otlp_endpoint() -> Optional[str]:
    """
    Get OTLP endpoint from vault using the "username" key.

    Returns:
        The endpoint URL if found, None otherwise
    """
    try:
        endpoint = bw_get_item("otl-info")["username"]
        return endpoint
    except Exception:
        logger.warning("Failed to get OTLP endpoint from vault")
        return None


def get_auth_headers(
    existing_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Get authentication headers for OTLP endpoint.

    Args:
        existing_headers: Optional existing headers to use

    Returns:
        Dictionary of headers including authentication
    """
    if existing_headers:
        return existing_headers

    headers = {}
    try:
        password = bw_get_item("otl-info")["password"]
        auth_string = f"otel-client:{password}"
        auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"
        headers = {"Authorization": auth_header}
    except Exception:
        logger.warning("Failed to get authentication credentials from vault")

    return headers
