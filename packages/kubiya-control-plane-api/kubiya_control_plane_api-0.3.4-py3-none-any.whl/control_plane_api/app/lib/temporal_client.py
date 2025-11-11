"""Temporal client for Agent Control Plane API"""

import os
from pathlib import Path
from typing import Optional
import structlog
from temporalio.client import Client, TLSConfig

logger = structlog.get_logger()

_temporal_client: Optional[Client] = None


async def get_temporal_client() -> Client:
    """
    Get or create Temporal client singleton.

    Supports mTLS authentication for Temporal Cloud.
    This client is used by the API to submit workflows.

    Returns:
        Temporal client instance
    """
    global _temporal_client

    if _temporal_client is not None:
        return _temporal_client

    temporal_host = os.environ.get("TEMPORAL_HOST")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    # Strip whitespace and newlines from all env vars (common issue with env vars)
    if temporal_host:
        temporal_host = temporal_host.strip()
    if temporal_namespace:
        temporal_namespace = temporal_namespace.strip()
    if temporal_api_key:
        temporal_api_key = temporal_api_key.strip()
    temporal_cert_path = os.environ.get("TEMPORAL_CLIENT_CERT_PATH")
    temporal_key_path = os.environ.get("TEMPORAL_CLIENT_KEY_PATH")

    if not temporal_host or not temporal_namespace:
        raise ValueError(
            "TEMPORAL_HOST and TEMPORAL_NAMESPACE environment variables are required"
        )

    try:
        # Check if connecting to Temporal Cloud
        is_cloud = "tmprl.cloud" in temporal_host or "api.temporal.io" in temporal_host

        if is_cloud:
            # Check authentication method: API Key or mTLS
            if temporal_api_key:
                # API Key authentication
                logger.info("temporal_auth_method", method="api_key")

                # Connect with TLS and API key
                _temporal_client = await Client.connect(
                    temporal_host,
                    namespace=temporal_namespace,
                    tls=TLSConfig(),  # TLS without client cert
                    rpc_metadata={"authorization": f"Bearer {temporal_api_key}"}
                )
            elif temporal_cert_path:
                # mTLS authentication
                logger.info("temporal_auth_method", method="mtls")

                # Load client certificate
                cert_path = Path(temporal_cert_path)
                if not cert_path.exists():
                    raise FileNotFoundError(
                        f"Temporal client certificate not found at {cert_path}"
                    )

                with open(cert_path, "rb") as f:
                    cert_content = f.read()

                # Check if private key is in same file or separate
                if b"BEGIN PRIVATE KEY" in cert_content or b"BEGIN RSA PRIVATE KEY" in cert_content:
                    # Key is in the same file
                    client_cert = cert_content
                    client_key = cert_content
                else:
                    # Key must be in separate file
                    if not temporal_key_path:
                        raise ValueError(
                            "Private key not found in certificate file and no separate key path configured. "
                            "Please provide TEMPORAL_CLIENT_KEY_PATH environment variable."
                        )
                    key_path = Path(temporal_key_path)
                    with open(key_path, "rb") as f:
                        client_key = f.read()
                    client_cert = cert_content

                # Create TLS config for mTLS
                tls_config = TLSConfig(
                    client_cert=client_cert,
                    client_private_key=client_key,
                )

                # Connect to Temporal Cloud with mTLS
                _temporal_client = await Client.connect(
                    temporal_host,
                    namespace=temporal_namespace,
                    tls=tls_config,
                )
            else:
                raise ValueError(
                    "For Temporal Cloud connection, either TEMPORAL_API_KEY or TEMPORAL_CLIENT_CERT_PATH must be provided"
                )
        else:
            # Local Temporal server (no authentication required)
            _temporal_client = await Client.connect(
                temporal_host,
                namespace=temporal_namespace,
            )

        logger.info(
            "temporal_client_connected",
            host=temporal_host,
            namespace=temporal_namespace,
        )

        return _temporal_client

    except Exception as e:
        logger.error("temporal_client_connection_failed", error=str(e))
        raise


async def close_temporal_client() -> None:
    """Close the Temporal client connection"""
    global _temporal_client

    if _temporal_client is not None:
        await _temporal_client.close()
        _temporal_client = None
        logger.info("temporal_client_closed")
